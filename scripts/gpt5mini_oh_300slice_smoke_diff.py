"""Phase 0.4 smoke + diff for the gpt-5-mini OH 300-slice validation.

Runs `extract_one_filing_from_cache` once against a single hand-validated
baseline filing (default report_id 1427844), then diffs the resulting
`filing.json` against the Sonnet output for the same filing. Checks the four
invariants documented in RUNBOOK_day2.md step 0.4 and reports
top-level-shape divergence.

Behavior on completion:
    - All invariants hold  → delete the smoke output so it doesn't contaminate
      the 3-run dispatch.   Exit 0.
    - Any invariant fails  → leave the smoke output in place for inspection.
      Exit 1.
    - Structural shape diverges → leave output in place, exit 2.

Usage:
    python scripts/gpt5mini_oh_300slice_smoke_diff.py
    python scripts/gpt5mini_oh_300slice_smoke_diff.py --report-id 1427844
    python scripts/gpt5mini_oh_300slice_smoke_diff.py --no-cleanup  # keep output
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.env_local import load_env_local  # noqa: E402
from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
    extract_one_filing_from_cache,
)

# Hand-validated invariants for report_id 1427844 (per RUNBOOK_day2.md 0.4).
# These come from the Sonnet baseline + human eyeball of the cached HTML —
# they're properties of the SOURCE, not properties of either model, so they
# should hold for any correct extractor.
_INVARIANTS_1427844 = {
    "state": "OH",
    "filer_person_name": "Nathan Aichele",
    "len_positions": 4,
    "len_expenditures": 1,
    "expenditures_0_amount": 20.0,
}

# Array fields whose lengths we cross-check between providers for structural
# sanity (a wild mismatch on any of these indicates an extractor bug, not a
# model disagreement worth analyzing further).
_ARRAY_FIELDS = ("positions", "expenditures", "engagements", "gifts")


def _find_filing(report_dir: Path, run_label_prefix: str | None = None) -> Path | None:
    """Most-recent filing.json under report_dir, optionally restricting to a
    run_label prefix (e.g., 'mini_smoke_' to pick out this script's output)."""
    if not report_dir.is_dir():
        return None
    runs = sorted(
        d for d in report_dir.iterdir()
        if d.is_dir() and (
            run_label_prefix is None or d.name.startswith(run_label_prefix)
        )
    )
    for run_dir in reversed(runs):
        candidate = run_dir / "filing.json"
        if candidate.exists():
            return candidate
    return None


def _check_invariants(mini: dict, report_id: str) -> tuple[bool, list[str]]:
    """Check the hand-validated invariants for known report_ids. Returns
    (all_passed, list_of_failure_messages). For unknown report_ids returns
    (True, []) without checking — there's nothing to compare against."""
    if report_id != "1427844":
        return True, []

    inv = _INVARIANTS_1427844
    failures = []
    got_state = mini.get("state")
    if got_state != inv["state"]:
        failures.append(
            f"state: got {got_state!r}, expected {inv['state']!r}"
        )
    got_filer = (mini.get("filer_person") or {}).get("name")
    if got_filer != inv["filer_person_name"]:
        failures.append(
            f"filer_person.name: got {got_filer!r}, expected "
            f"{inv['filer_person_name']!r}"
        )
    got_positions = len(mini.get("positions") or [])
    if got_positions != inv["len_positions"]:
        failures.append(
            f"len(positions): got {got_positions}, expected {inv['len_positions']}"
        )
    got_expenditures = len(mini.get("expenditures") or [])
    if got_expenditures != inv["len_expenditures"]:
        failures.append(
            f"len(expenditures): got {got_expenditures}, expected "
            f"{inv['len_expenditures']}"
        )
    if got_expenditures >= 1:
        got_amount = (mini.get("expenditures") or [{}])[0].get("amount")
        # Compare numerically — schema may have it as int, float, or Decimal.
        try:
            if float(got_amount) != float(inv["expenditures_0_amount"]):
                failures.append(
                    f"expenditures[0].amount: got {got_amount!r}, expected "
                    f"{inv['expenditures_0_amount']}"
                )
        except (TypeError, ValueError):
            failures.append(
                f"expenditures[0].amount: got {got_amount!r} (non-numeric)"
            )
    return (not failures), failures


def _check_structure(sonnet: dict, mini: dict) -> tuple[bool, list[str]]:
    """Top-level shape comparison: same key set, same array fields present.
    Wild length divergences (e.g., 10x) flag a probable extractor bug."""
    issues = []
    s_keys = set(sonnet.keys())
    m_keys = set(mini.keys())
    only_sonnet = s_keys - m_keys
    only_mini = m_keys - s_keys
    if only_sonnet:
        issues.append(f"top-level keys only in sonnet: {sorted(only_sonnet)}")
    if only_mini:
        issues.append(f"top-level keys only in mini:   {sorted(only_mini)}")
    for f in _ARRAY_FIELDS:
        sl = len(sonnet.get(f) or [])
        ml = len(mini.get(f) or [])
        # Wild = >5x in either direction with both >0, OR one is >5 and the
        # other is 0. Tight invariant tied to the explicit invariants above.
        if sl == 0 and ml == 0:
            continue
        wild = (
            (sl > 0 and ml > 0 and max(sl / ml, ml / sl) > 5)
            or (sl == 0 and ml > 5)
            or (ml == 0 and sl > 5)
        )
        if wild:
            issues.append(f"len({f}): sonnet={sl}, mini={ml} (wild divergence)")
    return (not issues), issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-id", default="1427844",
        help="Report id to smoke-test (default 1427844, hand-validated).",
    )
    parser.add_argument(
        "--data-dir", default=str(DATA_DIR),
        help=f"OH portal data dir (default {DATA_DIR}).",
    )
    parser.add_argument(
        "--no-cleanup", action="store_true",
        help="Do not delete the smoke output dir on success (default cleans up).",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    report_id = args.report_id

    load_env_local()

    print(f"[smoke] extracting mini on report_id={report_id}", file=sys.stderr)
    filing_path, usage = extract_one_filing_from_cache(
        report_id,
        run_label="mini_smoke",
        data_dir=data_dir,
        log=lambda m: print(f"  {m}", file=sys.stderr),
    )
    print(f"[smoke] wrote {filing_path}", file=sys.stderr)
    print(f"[smoke] usage: {usage}", file=sys.stderr)

    mini = json.loads(filing_path.read_text())

    sonnet_path = _find_filing(data_dir / "extracted" / report_id)
    if sonnet_path is None:
        print(
            f"[smoke] FAIL — no Sonnet baseline for {report_id} to diff against.",
            file=sys.stderr,
        )
        return 2
    sonnet = json.loads(sonnet_path.read_text())

    # Top-level shape diff (informational + structural sanity gate).
    print("[smoke] sonnet top-level keys:", sorted(sonnet.keys()), file=sys.stderr)
    print("[smoke] mini   top-level keys:", sorted(mini.keys()), file=sys.stderr)
    for f in _ARRAY_FIELDS:
        print(
            f"[smoke]   {f}: sonnet={len(sonnet.get(f) or [])}, "
            f"mini={len(mini.get(f) or [])}",
            file=sys.stderr,
        )
    shape_ok, shape_issues = _check_structure(sonnet, mini)
    if not shape_ok:
        print("[smoke] STRUCTURAL DIVERGENCE:", file=sys.stderr)
        for s in shape_issues:
            print(f"  - {s}", file=sys.stderr)
        print(
            f"[smoke] leaving output for inspection at "
            f"{filing_path.parent}",
            file=sys.stderr,
        )
        return 2

    # Hand-validated invariants (only for known report_ids).
    inv_ok, inv_failures = _check_invariants(mini, report_id)
    if not inv_ok:
        print("[smoke] INVARIANT FAILURES:", file=sys.stderr)
        for s in inv_failures:
            print(f"  - {s}", file=sys.stderr)
        print(
            f"[smoke] leaving output for inspection at "
            f"{filing_path.parent}",
            file=sys.stderr,
        )
        return 1

    print(f"[smoke] OK — all invariants hold for {report_id}", file=sys.stderr)

    if not args.no_cleanup:
        # Remove all mini_smoke_* run dirs for this report_id so the 3-run
        # dispatch isn't contaminated. The dispatch enumerates run dirs by
        # `mini_run_<N>_` prefix, so a `mini_smoke_*` dir is harmless in
        # practice — but the runbook calls for cleanup and explicit is better.
        report_dir = data_dir / EXTRACTED_OPENAI_SUBDIR / report_id
        if report_dir.is_dir():
            for run_dir in report_dir.iterdir():
                if run_dir.is_dir() and run_dir.name.startswith("mini_smoke_"):
                    shutil.rmtree(run_dir)
                    print(f"[smoke] cleaned up {run_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

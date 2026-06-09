"""Re-test the brief-fix: targeted re-extraction on the 26 reporting_period failures.

Session: docs/active/leave-behind-prep/convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md

The reporting_period spot-check identified 26 medium-arm failures (13
disagreements + 13 one-null) caused by gpt-5-mini misreading OH's
'May-Aug25' shorthand. The brief was patched to expand the shorthand
explicitly. This script re-extracts ONLY those 26 filings under a new
run_label ("mini_medium_briefv2_run_1") so:

  1. The original mini_medium_run_1 outputs stay on disk for comparison.
  2. The new outputs are byte-identifiable by run_label.
  3. The brief change shows up in extraction_run.json.prompt_version
     automatically (8e564091e96fd395 -> 5606c835a47a174a) — no separate
     versioning needed.

Cost estimate: 26 filings × ~$0.0079/filing = ~$0.21.
Wall-clock: 26 filings × ~3.8s/filing on 10-way concurrent = ~10s.

After this runs, re-run the spot-check pointed at the new run_label to
confirm the malformed-date count drops.

Run
---
    uv run python scripts/gpt5mini_oh_300slice_briefv2_retest.py

After it finishes, evaluate:
    uv run python scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py \\
        --arm medium_briefv2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# The 26 report_ids identified by the reporting_period spot-check on
# the medium arm: 13 with malformed-date disagreements + 13 with one-null
# (mini=null where Sonnet emitted). All 26 share the same root cause —
# mini couldn't parse 'May-Aug25' shorthand. After the brief fix, all 26
# should emit clean 2025-XX-XX dates matching Sonnet.
TARGET_RIDS_MEDIUM = [
    # ── disagreements (both emitted, mini emitted malformed) ──
    "1429064", "1436864", "1437090", "1429882", "1433534", "1433628",
    "1435010", "1437386", "1396330", "1401706", "1411564", "1428260",
    "1436088",
    # ── one_null (mini emitted null where sonnet emitted) ──
    "1396552", "1399318", "1400518", "1401482", "1407808", "1417388",
    "1426400", "1428760", "1430446", "1433900", "1434836", "1436990",
    "1438288",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-concurrent", type=int, default=10,
        help="Concurrency level (default 10).",
    )
    parser.add_argument(
        "--reasoning-effort", default="medium",
        choices=["minimal", "low", "medium", "high"],
        help=(
            "Which reasoning_effort to re-test under. Default medium (the "
            "production-candidate setting that surfaced the bug)."
        ),
    )
    parser.add_argument(
        "--run-label-suffix", default="briefv2",
        help=(
            "Suffix appended to the effort tag in the run_label. Default "
            "'briefv2'. Full label becomes "
            "f'mini_{effort}_{suffix}_run_1'."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the dispatch invocation; don't actually run.",
    )
    args = parser.parse_args()

    from lobby_analysis.oh_portal.fetch import DATA_DIR
    from lobby_analysis.oh_portal.pipeline_openai import (
        EXTRACTED_OPENAI_SUBDIR,
    )

    # Import the dispatcher's parallel worker directly rather than spawning
    # a subprocess: gives us proper run_label control without adding a new
    # CLI flag to the main dispatcher script.
    #
    # NOTE: assigning to sys.modules BEFORE exec_module() is load-bearing.
    # Without it, the @dataclass decorator inside dispatch.py fails with
    # "NoneType has no attribute __dict__" because dataclasses looks up
    # cls.__module__ in sys.modules and finds None. Mirrors the test
    # harness pattern in test_gpt5mini_oh_300slice_dispatch.py.
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gpt5mini_dispatch",
        _REPO_ROOT / "scripts" / "gpt5mini_oh_300slice_dispatch.py",
    )
    assert spec and spec.loader
    dispatch_mod = importlib.util.module_from_spec(spec)
    sys.modules["gpt5mini_dispatch"] = dispatch_mod
    spec.loader.exec_module(dispatch_mod)

    run_label = f"mini_{args.reasoning_effort}_{args.run_label_suffix}_run_1"
    print(f"Target rids ({len(TARGET_RIDS_MEDIUM)}): {TARGET_RIDS_MEDIUM[:5]}...", file=sys.stderr)
    print(f"Run label: {run_label}", file=sys.stderr)
    print(f"Reasoning effort: {args.reasoning_effort}", file=sys.stderr)
    print(f"Concurrency: {args.max_concurrent}", file=sys.stderr)
    print(f"Output dir: {DATA_DIR}/{EXTRACTED_OPENAI_SUBDIR}/<rid>/{run_label}_*", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] would dispatch; exiting.", file=sys.stderr)
        return 0

    def log(m: str) -> None:
        print(m, file=sys.stderr)

    results = dispatch_mod.run_one_pass(
        TARGET_RIDS_MEDIUM,
        run_label=run_label,
        data_dir=DATA_DIR,
        wall_clock_cap_s=3600,
        resume=True,  # safe — distinct run_label means nothing to resume from
        log=log,
        reasoning_effort=args.reasoning_effort,
        max_concurrent=args.max_concurrent,
    )

    # Summarize
    n_ok = sum(1 for r in results if r.status == "extracted")
    n_failed = sum(1 for r in results if r.status == "failed")
    total_cost = sum(r.cost_usd for r in results if r.cost_usd)
    print(f"\n[briefv2-retest] {n_ok}/{len(TARGET_RIDS_MEDIUM)} extracted, {n_failed} failed, ${total_cost:.4f}", file=sys.stderr)
    print(
        "\nNext: rerun the spot-check pointed at the new arm:\n"
        f"  uv run python scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py \\\n"
        f"      --arm {args.reasoning_effort}_{args.run_label_suffix}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

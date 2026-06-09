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
    # Default: re-test the 26 known reporting_period failure rids.
    # ~10s wall-clock, ~$0.21.
    uv run python scripts/gpt5mini_oh_300slice_briefv2_retest.py

    # Full medium-arm regression: re-test all ~100 rids from the original
    # medium arm. Confirms the brief change doesn't BREAK previously-good
    # filings. ~$0.79.
    uv run python scripts/gpt5mini_oh_300slice_briefv2_retest.py \\
        --mode full-medium

After it runs, evaluate:
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
KNOWN_FAILURE_RIDS = [
    # ── disagreements (both emitted, mini emitted malformed) ──
    "1429064", "1436864", "1437090", "1429882", "1433534", "1433628",
    "1435010", "1437386", "1396330", "1401706", "1411564", "1428260",
    "1436088",
    # ── one_null (mini emitted null where sonnet emitted) ──
    "1396552", "1399318", "1400518", "1401482", "1407808", "1417388",
    "1426400", "1428760", "1430446", "1433900", "1434836", "1436990",
    "1438288",
]


def derive_full_medium_rids(data_dir, run_label_prefix: str = "mini_medium_run_1_") -> list[str]:
    """Find every report_id with an existing mini_medium_run_1_* output.

    This is the "what did the original medium arm actually run on" source
    of truth, used by --mode full-medium for the full-arm regression test.
    Distinct from --mode known-failures (the 26-rid cherry-pick).
    """
    from lobby_analysis.oh_portal.pipeline_openai import EXTRACTED_OPENAI_SUBDIR
    root = data_dir / EXTRACTED_OPENAI_SUBDIR
    if not root.is_dir():
        return []
    rids: list[str] = []
    for report_dir in sorted(root.iterdir()):
        if not report_dir.is_dir():
            continue
        # Each report dir contains one or more run_dirs; check if any
        # has the medium prefix.
        has_medium = any(
            d.is_dir() and d.name.startswith(run_label_prefix)
            for d in report_dir.iterdir()
        )
        if has_medium:
            rids.append(report_dir.name)
    return rids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", default="known-failures",
        choices=["known-failures", "full-medium"],
        help=(
            "Which rid set to re-extract under the new brief. "
            "'known-failures' (default): the 26 hardcoded report_ids that "
            "the spot-check identified as reporting_period failures on the "
            "original medium arm. Cheap (~$0.21) and fast (~10s). Good for "
            "first-pass 'does the fix work on the broken cases?' check. "
            "'full-medium': all ~100 report_ids that were in the original "
            "medium arm, derived at runtime by listing extracted_openai/ for "
            "mini_medium_run_1_* outputs. Used to verify the brief change "
            "doesn't REGRESS the previously-good cases. Costs ~$0.79."
        ),
    )
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

    from lobby_analysis.oh_portal.env_local import load_env_local
    from lobby_analysis.oh_portal.fetch import DATA_DIR
    from lobby_analysis.oh_portal.pipeline_openai import (
        EXTRACTED_OPENAI_SUBDIR,
    )

    # Load OPENAI_API_KEY etc. from .env.local. Without this, fresh shells
    # see no credentials and every extraction fails with OpenAIError. The
    # main dispatcher does this at the start of main(); briefv2_retest
    # needs to do it too since it doesn't shell out to the dispatcher CLI.
    load_env_local()

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

    # Resolve target rid set from --mode.
    if args.mode == "known-failures":
        target_rids = list(KNOWN_FAILURE_RIDS)
        mode_descr = "26 known reporting_period failure rids (hardcoded)"
    elif args.mode == "full-medium":
        target_rids = derive_full_medium_rids(DATA_DIR)
        mode_descr = f"all {len(target_rids)} rids found in mini_medium_run_1_* (derived)"
        if not target_rids:
            print(
                "[briefv2-retest] ERROR: --mode full-medium found no "
                "mini_medium_run_1_* outputs. Run the original medium arm "
                "first or check --data-dir.",
                file=sys.stderr,
            )
            return 1
    else:
        raise ValueError(f"unhandled mode: {args.mode}")

    # Cost estimate. The original medium arm averaged $0.0079/filing.
    estimated_cost = len(target_rids) * 0.0079
    run_label = f"mini_{args.reasoning_effort}_{args.run_label_suffix}_run_1"
    print(f"Mode: {args.mode} — {mode_descr}", file=sys.stderr)
    print(f"Target rids: {len(target_rids)}", file=sys.stderr)
    print(f"Run label: {run_label}", file=sys.stderr)
    print(f"Reasoning effort: {args.reasoning_effort}", file=sys.stderr)
    print(f"Concurrency: {args.max_concurrent}", file=sys.stderr)
    print(f"Estimated cost: ~${estimated_cost:.2f} (at $0.0079/filing)", file=sys.stderr)
    print(f"Output dir: {DATA_DIR}/{EXTRACTED_OPENAI_SUBDIR}/<rid>/{run_label}_*", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] would dispatch; exiting.", file=sys.stderr)
        return 0

    def log(m: str) -> None:
        print(m, file=sys.stderr)

    results = dispatch_mod.run_one_pass(
        target_rids,
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
    print(f"\n[briefv2-retest] {n_ok}/{len(target_rids)} extracted, {n_failed} failed, ${total_cost:.4f}", file=sys.stderr)
    print(
        "\nNext: rerun the spot-check pointed at the new arm:\n"
        f"  uv run python scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py \\\n"
        f"      --arm {args.reasoning_effort}_{args.run_label_suffix}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

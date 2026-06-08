"""Phase 2 cost watchdog for the gpt-5-mini OH 300-slice validation.

Reads the per-pass summary JSONs written by `gpt5mini_oh_300slice_dispatch.py`
(`_summary_run{1,2,3}.json`), sums `total_cost_usd`, and reports the running
total. Exits non-zero if the running total exceeds the budget cap (default
$5.00 per RUNBOOK_day2.md Phase 2 hard-stop), so an automating script or
operator notices.

Per-pass JSONs missing from disk are skipped (treated as "not yet run"). This
script is intended to be invoked between dispatch passes — after pass 1, after
pass 2, etc.

Usage:
    python scripts/gpt5mini_oh_300slice_cost_check.py
    python scripts/gpt5mini_oh_300slice_cost_check.py --budget-usd 5.0

Exit codes:
    0   total spend within budget
    1   total spend exceeds budget (operator should stop and surface)
    2   no summary files found at all (dispatch hasn't run yet)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_SUMMARY_DIR = _REPO_ROOT / "data" / "oh_portal" / "extracted_openai"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-dir", default=str(_DEFAULT_SUMMARY_DIR),
        help=f"Directory holding _summary_run*.json (default {_DEFAULT_SUMMARY_DIR}).",
    )
    parser.add_argument(
        "--budget-usd", type=float, default=5.0,
        help="Budget ceiling in USD (default 5.0). Exit 1 if total exceeds.",
    )
    args = parser.parse_args()
    summary_dir = Path(args.summary_dir)

    total = 0.0
    per_pass: list[tuple[int, float]] = []
    for n in (1, 2, 3):
        path = summary_dir / f"_summary_run{n}.json"
        if not path.exists():
            continue
        try:
            summary = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[cost] WARN — {path} unreadable: {exc!r}", file=sys.stderr)
            continue
        cost = summary.get("total_cost_usd")
        if cost is None:
            print(f"[cost] WARN — {path} missing total_cost_usd", file=sys.stderr)
            continue
        per_pass.append((n, float(cost)))
        total += float(cost)

    if not per_pass:
        print(
            f"[cost] no _summary_run*.json under {summary_dir} — "
            "dispatch hasn't completed any pass yet.",
            file=sys.stderr,
        )
        return 2

    for n, cost in per_pass:
        print(f"[cost] pass {n}: ${cost:.4f}", file=sys.stderr)
    print(f"[cost] running total: ${total:.4f}", file=sys.stderr)
    print(f"[cost] budget ceiling: ${args.budget_usd:.2f}", file=sys.stderr)

    if total > args.budget_usd:
        print(
            f"[cost] OVER BUDGET — total ${total:.4f} > "
            f"${args.budget_usd:.2f}. STOP and surface to user.",
            file=sys.stderr,
        )
        return 1
    print(f"[cost] OK — within budget", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

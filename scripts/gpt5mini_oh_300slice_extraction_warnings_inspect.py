"""Inspect extraction_warnings content across sonnet / mini-medium / mini-briefv2.

Session: docs/active/leave-behind-prep/convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md

The cross-arm briefv2 results showed extraction_warnings agreement dropping
from 30% (sonnet vs medium) to 13% (sonnet vs medium_briefv2). The
agreement-rate metric measures equal list-LENGTH (per the cross-arm script
design), so 13% means briefv2 emits a different number of warnings than
sonnet on 87% of filings. This script reads the WARNING TEXT itself across
the three arms on a sample of filings so we can see whether briefv2's
warnings are:

  (a) Useful & content-relevant (briefv2 catches more legitimate ambiguities)
  (b) Noise (verbose stylistic emissions about the brief itself)
  (c) Different topics (briefv2 warns about different things than original)

Reads the first N rids in sonnet-order by default; pass --rids to target
specific filings.

Run
---
    # Default: first 5 rids in sonnet order
    uv run python scripts/gpt5mini_oh_300slice_extraction_warnings_inspect.py

    # Target a specific subset
    uv run python scripts/gpt5mini_oh_300slice_extraction_warnings_inspect.py \\
        --rids 1394434,1394636,1395368

    # All 100 briefv2 filings
    uv run python scripts/gpt5mini_oh_300slice_extraction_warnings_inspect.py \\
        --all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
)


def _latest_filing_json(report_dir: Path, prefix: str | None = None) -> Path | None:
    if not report_dir.is_dir():
        return None
    candidates: list[Path] = []
    for d in report_dir.iterdir():
        if not d.is_dir():
            continue
        if prefix is not None and not d.name.startswith(prefix):
            continue
        fj = d / "filing.json"
        if fj.exists():
            candidates.append(fj)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_arm(rid: str, data_dir: Path, arm: str) -> dict | None:
    if arm == "sonnet":
        path = _latest_filing_json(data_dir / "extracted" / rid)
    else:
        prefix = f"mini_{arm}_run_1_"
        path = _latest_filing_json(
            data_dir / EXTRACTED_OPENAI_SUBDIR / rid, prefix=prefix
        )
    if path is None:
        return None
    return json.loads(path.read_text())


def find_briefv2_rids(data_dir: Path) -> list[str]:
    """Return rids that have a medium_briefv2 output on disk."""
    root = data_dir / EXTRACTED_OPENAI_SUBDIR
    if not root.is_dir():
        return []
    out: list[str] = []
    for rid_dir in sorted(root.iterdir()):
        if not rid_dir.is_dir():
            continue
        if any(
            d.is_dir() and d.name.startswith("mini_medium_briefv2_run_1_")
            for d in rid_dir.iterdir()
        ):
            out.append(rid_dir.name)
    return out


def _format_warnings(warnings: list | None) -> str:
    if warnings is None:
        return "(field absent)"
    if not warnings:
        return "(empty list)"
    return "\n".join(f"      - {w}" for w in warnings)


def inspect_rid(rid: str, data_dir: Path, arms: list[str]) -> None:
    """Print warnings across all arms for one rid."""
    print(f"━━━ {rid} ━━━")
    for arm in arms:
        filing = load_arm(rid, data_dir, arm)
        if filing is None:
            print(f"  [{arm}] (no output on disk)")
            continue
        warnings = filing.get("extraction_warnings")
        n = len(warnings) if warnings else 0
        print(f"  [{arm}] {n} warning(s)")
        formatted = _format_warnings(warnings)
        if formatted not in ("(field absent)", "(empty list)"):
            print(formatted)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument(
        "--rids", default=None,
        help="Comma-separated rids to inspect. Default: first 5 in sonnet order.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Inspect all rids that have briefv2 output (typically 100).",
    )
    parser.add_argument(
        "--arms", default="sonnet,medium,medium_briefv2",
        help=(
            "Comma-separated arm names to compare. Default: "
            "sonnet,medium,medium_briefv2. Each arm resolves to a "
            "filing.json under the standard on-disk layout."
        ),
    )
    parser.add_argument(
        "--summary", action="store_true",
        help=(
            "Skip the per-rid breakdown; just print arm-level counts "
            "(rids with N warnings, rids with empty list, rids with field "
            "absent)."
        ),
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]

    if args.rids:
        rids = [r.strip() for r in args.rids.split(",") if r.strip()]
    elif args.all:
        rids = find_briefv2_rids(data_dir)
    else:
        # Default: first 5 briefv2 rids
        rids = find_briefv2_rids(data_dir)[:5]

    print(f"Inspecting {len(rids)} rid(s) across arms: {arms}\n")

    if args.summary:
        # Arm-level histograms only — no per-rid detail
        for arm in arms:
            n_with: dict[int, int] = {}
            n_empty = 0
            n_absent = 0
            for rid in rids:
                filing = load_arm(rid, data_dir, arm)
                if filing is None:
                    n_absent += 1
                    continue
                warnings = filing.get("extraction_warnings")
                if warnings is None:
                    n_absent += 1
                elif not warnings:
                    n_empty += 1
                else:
                    n_with[len(warnings)] = n_with.get(len(warnings), 0) + 1
            print(f"[{arm}]")
            print(f"  no output / field absent: {n_absent}")
            print(f"  empty list:              {n_empty}")
            print("  non-empty (by count):")
            for n, count in sorted(n_with.items()):
                print(f"     {n:3d} warning(s): {count} filing(s)")
            print()
    else:
        for rid in rids:
            inspect_rid(rid, data_dir, arms)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

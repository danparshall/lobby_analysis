"""Spot-check is_current disagreements between Sonnet and a mini arm.

Session: docs/active/leave-behind-prep/convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md

The cross-arm briefv2 results showed is_current agreement dropping from 98%
(original medium vs sonnet) to 94% (medium_briefv2 vs sonnet) — six new
disagreements introduced by the brief change on a field that SHOULD be
deterministic (per the schema docstring, `is_current` defaults True and
flips False only when the filing is superseded by an amendment).

The slice was scraped as a point-in-time set of active AERs, so the
expected truth is is_current=True for every filing. This script
enumerates the disagreements and prints (rid, sonnet_value, mini_value)
so we can see:

  (a) Did briefv2 emit False where True is expected? (Real regression.)
  (b) Did briefv2 emit True where Sonnet emitted False? (Briefv2 got
      a previously-wrong field right.)
  (c) Some mix? (Investigate case by case.)

Run
---
    uv run python scripts/gpt5mini_oh_300slice_is_current_spotcheck.py \\
        --arm medium_briefv2

    # Compare original medium vs sonnet too:
    uv run python scripts/gpt5mini_oh_300slice_is_current_spotcheck.py \\
        --arm medium --arm medium_briefv2
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


def find_disagreements(
    rids: list[str], data_dir: Path, arm: str
) -> list[dict]:
    out: list[dict] = []
    for rid in rids:
        sonnet = load_arm(rid, data_dir, "sonnet")
        mini = load_arm(rid, data_dir, arm)
        if sonnet is None or mini is None:
            continue
        sv = sonnet.get("is_current")
        mv = mini.get("is_current")
        if sv == mv:
            continue
        out.append({
            "report_id": rid,
            "sonnet": sv,
            "mini": mv,
            # Also pull filing_action and supersedes — adjacent fields that
            # might explain the disagreement (e.g., briefv2 might flip
            # is_current based on a perceived filing_action='amended').
            "sonnet_filing_action": sonnet.get("filing_action"),
            "mini_filing_action": mini.get("filing_action"),
            "sonnet_supersedes": sonnet.get("supersedes"),
            "mini_supersedes": mini.get("supersedes"),
        })
    return out


def find_intersection_rids(data_dir: Path, arms: list[str]) -> list[str]:
    sonnet_root = data_dir / "extracted"
    intersection: list[str] = []
    for rid in sorted(p.name for p in sonnet_root.iterdir() if p.is_dir()):
        if load_arm(rid, data_dir, "sonnet") is None:
            continue
        if all(load_arm(rid, data_dir, a) is not None for a in arms):
            intersection.append(rid)
    return intersection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument(
        "--arm", action="append",
        default=None,
        help=(
            "Arm(s) to check. Default: medium_briefv2. Pass multiple --arm "
            "to compare several mini variants side by side."
        ),
    )
    args = parser.parse_args()

    arms = args.arm or ["medium_briefv2"]
    data_dir = Path(args.data_dir)
    rids = find_intersection_rids(data_dir, arms)
    print(f"Comparison set: {len(rids)} report_ids in (sonnet ∩ {' ∩ '.join(arms)})\n")

    for arm in arms:
        print(f"━━━ {arm} vs sonnet — is_current ━━━")
        disagreements = find_disagreements(rids, data_dir, arm)
        print(f"  disagreements: {len(disagreements)}")

        if disagreements:
            # Direction histogram
            cats: dict[str, int] = {}
            for d in disagreements:
                key = f"sonnet={d['sonnet']} mini={d['mini']}"
                cats[key] = cats.get(key, 0) + 1
            print("\n  by direction:")
            for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
                print(f"    {n:3d}  {cat}")

            print("\n  full list (rid, is_current sonnet/mini, filing_action sonnet/mini, supersedes sonnet/mini):")
            for d in sorted(disagreements, key=lambda x: x["report_id"]):
                print(
                    f"    {d['report_id']}  "
                    f"current={d['sonnet']}/{d['mini']}  "
                    f"action={d['sonnet_filing_action']}/{d['mini_filing_action']}  "
                    f"supersedes={d['sonnet_supersedes']}/{d['mini_supersedes']}"
                )
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Spot-check is_itemized emission regression: briefv2 emits, briefv3 abstains.

Plan: docs/active/leave-behind-prep/plans/20260609_is_itemized_investigation_and_writeup.md
Session: docs/active/leave-behind-prep/convos/20260612_gpt5mini_quality_gap_checks.md

The briefv3 cross-arm run showed is_itemized going from 5/100 emissions
(briefv2, all 5 agreeing with sonnet) to 0/100 (briefv3, full abstention).
Per the plan, before considering a brief-v4 we need to know whether sonnet's
is_itemized emissions are ground truth or guesswork:

  GROUND_TRUTH_EMITS    source clearly shows itemized-vs-not; briefv3 lost
                        real signal -> brief-v4 candidate.
  GROUND_TRUTH_ABSTAINS source is empty/silent on itemization; sonnet was
                        defaulting -> briefv3's abstention is CORRECT,
                        ship brief-v3 unchanged.
  AMBIGUOUS             reasonable extractors could go either way.

This script does the plan's Step 1 (identify the rids where briefv2 emits
non-null and briefv3 emits null) and tees up Step 2 (human read of the raw
HTML) by printing, per rid:

  - sonnet / briefv2 / briefv3 is_itemized values
  - len(expenditures) per arm — is_itemized on an EMPTY Section II is
    semantically undefined, so an empty list is evidence for ABSTAINS
  - the raw.html path to open for the hand read

Run (from repo root, on the machine with data/oh_portal/)
---
    uv run python scripts/gpt5mini_oh_300slice_is_itemized_spotcheck.py
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
        path = _latest_filing_json(data_dir / EXTRACTED_OPENAI_SUBDIR / rid, prefix=prefix)
    if path is None:
        return None
    return json.loads(path.read_text())


def _raw_html_path(rid: str, data_dir: Path) -> Path | None:
    raw_root = data_dir / "raw" / rid
    if not raw_root.is_dir():
        return None
    candidates = sorted(raw_root.glob("*/raw.html"))
    return candidates[-1] if candidates else None


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
    parser.add_argument("--arm-emits", default="medium_briefv2")
    parser.add_argument("--arm-abstains", default="medium_briefv3")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    arms = [args.arm_emits, args.arm_abstains]
    rids = find_intersection_rids(data_dir, arms)
    print(
        f"Comparison set: {len(rids)} report_ids in "
        f"(sonnet ∩ {args.arm_emits} ∩ {args.arm_abstains})\n"
    )

    # Emission census across the full intersection, for context.
    census: dict[str, int] = {"sonnet": 0, args.arm_emits: 0, args.arm_abstains: 0}
    targets: list[dict] = []
    for rid in rids:
        sonnet = load_arm(rid, data_dir, "sonnet")
        v2 = load_arm(rid, data_dir, args.arm_emits)
        v3 = load_arm(rid, data_dir, args.arm_abstains)
        assert sonnet is not None and v2 is not None and v3 is not None
        if sonnet.get("is_itemized") is not None:
            census["sonnet"] += 1
        if v2.get("is_itemized") is not None:
            census[args.arm_emits] += 1
        if v3.get("is_itemized") is not None:
            census[args.arm_abstains] += 1
        if v2.get("is_itemized") is not None and v3.get("is_itemized") is None:
            targets.append(
                {
                    "report_id": rid,
                    "sonnet": sonnet.get("is_itemized"),
                    "v2": v2.get("is_itemized"),
                    "v3": v3.get("is_itemized"),
                    "n_exp_sonnet": len(sonnet.get("expenditures") or []),
                    "n_exp_v2": len(v2.get("expenditures") or []),
                    "n_exp_v3": len(v3.get("expenditures") or []),
                    "raw_html": _raw_html_path(rid, data_dir),
                }
            )

    print("is_itemized non-null emission census:")
    for arm, n in census.items():
        print(f"  {arm:20s} {n:3d}/{len(rids)}")
    print()

    print(
        f"rids where {args.arm_emits} emits but {args.arm_abstains} abstains: "
        f"{len(targets)}  (plan expects 5)\n"
    )
    for t in targets:
        print(
            f"  {t['report_id']}  "
            f"is_itemized sonnet={t['sonnet']} v2={t['v2']} v3={t['v3']}  "
            f"len(expenditures) sonnet/v2/v3={t['n_exp_sonnet']}/"
            f"{t['n_exp_v2']}/{t['n_exp_v3']}"
        )
        print(f"      raw: {t['raw_html']}")
    print(
        "\nHand-read Step 2 per the plan: open each raw.html, look at Section II."
        "\nCategorize each rid GROUND_TRUTH_EMITS / GROUND_TRUTH_ABSTAINS / AMBIGUOUS."
        "\nEmpty Section II (len(expenditures)==0 in all arms) is prima facie"
        "\nevidence for GROUND_TRUTH_ABSTAINS — confirm against the HTML."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

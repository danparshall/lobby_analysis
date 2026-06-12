"""Spot-check positions disagreements at CONTENT level, not list length.

Session: docs/active/leave-behind-prep/convos/20260612_gpt5mini_quality_gap_checks.md

The cross-arm analyzer compares `positions` by list LENGTH (94% agreement,
sonnet vs medium_briefv3, n=100). Two gaps in that signal, both flagged as
open questions in the 3-arm dispatch convo:

  1. The 6 length disagreements are uncharacterized — extra/missing bills,
     or split/merge of the same bill set?
  2. Same-length lists can hide content differences (different bills, or
     same bills with different position/issue values).

Positions carry the bill references the OH chain composer consumes
(plans/20260611_oh_chain_composer_design.md), so content-level fidelity here
gates the mini swap more directly than any other list field.

Canonicalization: each position maps to a key
    (normalized bill text, position)
where normalized bill text is bill_reference.original_text upper-cased with
whitespace collapsed (falling back to bill_number, then general_issue_area
for bill-less positions). Comparison is by multiset of keys, so duplicate
positions on the same bill are counted, not collapsed.

Output per rid with any difference: sonnet-only keys, mini-only keys, and a
category:
    LENGTH_DIFF        list lengths differ
    CONTENT_DIFF       same length, different key multisets
    POSITION_VAL_DIFF  same bills, only the position enum differs
Plus a bill-text-only pass (ignoring the position value) so "same bills,
different stance label" separates from "different bills" — the latter is
what would corrupt the chain composer.

Run (from repo root, on the machine with data/oh_portal/)
---
    uv run python scripts/gpt5mini_oh_300slice_positions_spotcheck.py
    uv run python scripts/gpt5mini_oh_300slice_positions_spotcheck.py \\
        --arm medium_briefv2 --arm medium_briefv3
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
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


def find_intersection_rids(data_dir: Path, arms: list[str]) -> list[str]:
    sonnet_root = data_dir / "extracted"
    intersection: list[str] = []
    for rid in sorted(p.name for p in sonnet_root.iterdir() if p.is_dir()):
        if load_arm(rid, data_dir, "sonnet") is None:
            continue
        if all(load_arm(rid, data_dir, a) is not None for a in arms):
            intersection.append(rid)
    return intersection


def _norm_bill_text(pos: dict) -> str:
    ref = pos.get("bill_reference") or {}
    text = (
        ref.get("original_text")
        or ref.get("bill_number")
        or pos.get("general_issue_area")
        or "(no bill)"
    )
    return re.sub(r"\s+", " ", str(text)).strip().upper()


def position_keys(filing: dict) -> Counter:
    return Counter((_norm_bill_text(p), p.get("position")) for p in (filing.get("positions") or []))


def bill_keys(filing: dict) -> Counter:
    return Counter(_norm_bill_text(p) for p in (filing.get("positions") or []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--arm", action="append", default=None)
    args = parser.parse_args()

    arms = args.arm or ["medium_briefv3"]
    data_dir = Path(args.data_dir)
    rids = find_intersection_rids(data_dir, arms)
    print(f"Comparison set: {len(rids)} report_ids in (sonnet ∩ {' ∩ '.join(arms)})\n")

    for arm in arms:
        print(f"━━━ {arm} vs sonnet — positions content ━━━")
        census: Counter = Counter()
        diffs: list[dict] = []
        for rid in rids:
            sonnet = load_arm(rid, data_dir, "sonnet")
            mini = load_arm(rid, data_dir, arm)
            assert sonnet is not None and mini is not None
            sk, mk = position_keys(sonnet), position_keys(mini)
            sb, mb = bill_keys(sonnet), bill_keys(mini)
            s_len = sum(sk.values())
            m_len = sum(mk.values())
            if sk == mk:
                census["identical"] += 1
                continue
            if s_len != m_len:
                category = "LENGTH_DIFF"
            elif sb == mb:
                category = "POSITION_VAL_DIFF"
            else:
                category = "CONTENT_DIFF"
            census[category] += 1
            diffs.append(
                {
                    "rid": rid,
                    "category": category,
                    "len": f"{s_len}/{m_len}",
                    "bills_match": sb == mb,
                    "sonnet_only": sorted((sk - mk).elements()),
                    "mini_only": sorted((mk - sk).elements()),
                }
            )

        print("  census:")
        for k, n in census.most_common():
            print(f"    {n:3d}  {k}")
        same_bills = sum(1 for d in diffs if d["bills_match"])
        print(
            f"\n  of {len(diffs)} differing rids, {same_bills} have IDENTICAL"
            f" bill multisets (chain-safe; stance/label noise only)\n"
        )
        for d in diffs:
            print(
                f"  {d['rid']}  {d['category']}  len s/m={d['len']}  bills_match={d['bills_match']}"
            )
            for side in ("sonnet_only", "mini_only"):
                for key in d[side]:
                    print(f"      {side:11s} {key}")
        print()

    print(
        "Decision guide: CONTENT_DIFF / LENGTH_DIFF rows with bills_match=False"
        "\nare the chain-corrupting class — eyeball those against raw HTML."
        "\nPOSITION_VAL_DIFF rows are stance-label noise; the chain composer"
        "\ndoesn't read the position enum, so they don't gate the mini swap."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

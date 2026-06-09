"""Spot-check reporting_period_start/end disagreements between Sonnet and a mini arm.

Session: docs/active/leave-behind-prep/convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md

The cross-arm agreement table flagged reporting_period_start (85.1%) and
reporting_period_end (90.6%) as the lowest-agreement fields where both
Sonnet and mini-medium emit. This script enumerates the actual
disagreements so we can see whether they're:

  (a) Date-format / normalization noise ('2025-01-01' vs '2025-1-1',
      '01/01/2025' vs '2025-01-01', etc.) — fix: add a normalization layer.
  (b) One-day-off boundaries (period start 2025-01-01 vs 2024-12-31) — fix:
      probably a brief-design clarification.
  (c) Semester boundary confusion (Jan-Jun reported as full year or
      mid-period) — fix: brief-design.
  (d) Genuinely different reads of the source — investigate per filing.

For each disagreement, prints rid + sonnet value + mini value + a one-line
classification guess based on simple heuristics. The classification is a
starting point, not authoritative; eyeball before trusting.

Run
---
    uv run python scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py \\
        --arm medium

    # All arms at once:
    uv run python scripts/gpt5mini_oh_300slice_reporting_period_spotcheck.py \\
        --arm medium --arm low --arm minimal
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
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


def _parse_date(s: str | None) -> date | None:
    """Try common date formats. Returns None on failure.

    Tries the formats we've seen in the OH AERs and Sonnet output. Falls
    back to dateutil if available. The point of parsing here is to catch
    format-only disagreements ('2025-01-01' vs '01/01/2025') so they're
    classified separately from genuine date-value disagreements.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    from datetime import datetime
    for fmt in (
        "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
        "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
    ):
        try:
            return datetime.strptime(s[:len(fmt) + 8], fmt).date()
        except ValueError:
            continue
        except Exception:
            continue
    # Last resort: dateutil
    try:
        from dateutil.parser import parse as du_parse  # type: ignore
        return du_parse(s).date()
    except Exception:
        return None


def classify(sonnet_v: str | None, mini_v: str | None) -> str:
    """Heuristic classification of a disagreement pair."""
    if sonnet_v is None or mini_v is None:
        return "one_null"  # shouldn't reach here, but defensive
    if sonnet_v == mini_v:
        return "exact_match"  # shouldn't reach here either
    sd = _parse_date(sonnet_v)
    md = _parse_date(mini_v)
    if sd is None or md is None:
        return "unparseable"
    if sd == md:
        return "format_only"  # parsed equal → format difference only
    delta = (md - sd).days
    if abs(delta) == 1:
        return f"one_day_off (mini {'+1' if delta > 0 else '-1'})"
    if abs(delta) <= 7:
        return f"week_off ({delta:+d} days)"
    if abs(delta) <= 35:
        return f"month_off ({delta:+d} days)"
    if abs(delta) <= 200:
        return f"semester_or_quarter_boundary ({delta:+d} days)"
    return f"large_delta ({delta:+d} days)"


def find_disagreements(
    rids: list[str], data_dir: Path, arm: str, field: str
) -> list[dict]:
    out: list[dict] = []
    for rid in rids:
        sonnet = load_arm(rid, data_dir, "sonnet")
        mini = load_arm(rid, data_dir, arm)
        if sonnet is None or mini is None:
            continue
        sv = sonnet.get(field)
        mv = mini.get(field)
        # Disagreement = both emitted AND values differ
        if sv is None or mv is None:
            continue
        if sv == mv:
            continue
        out.append({
            "report_id": rid,
            "sonnet": sv,
            "mini": mv,
            "category": classify(sv, mv),
        })
    return out


def find_one_null(
    rids: list[str], data_dir: Path, arm: str, field: str
) -> list[dict]:
    """Find the one_null cases — exactly one arm emitted."""
    out: list[dict] = []
    for rid in rids:
        sonnet = load_arm(rid, data_dir, "sonnet")
        mini = load_arm(rid, data_dir, arm)
        if sonnet is None or mini is None:
            continue
        sv = sonnet.get(field)
        mv = mini.get(field)
        s_null = sv is None
        m_null = mv is None
        if s_null == m_null:
            continue
        out.append({
            "report_id": rid,
            "sonnet": sv,
            "mini": mv,
            "which_null": "sonnet" if s_null else "mini",
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
        "--arm", action="append", choices=["medium", "low", "minimal"],
        default=None, help="Arm(s) to check. Default: medium.",
    )
    parser.add_argument(
        "--field", action="append",
        choices=["reporting_period_start", "reporting_period_end"],
        default=None, help="Field(s) to check. Default: both.",
    )
    args = parser.parse_args()

    arms = args.arm or ["medium"]
    fields = args.field or [
        "reporting_period_start", "reporting_period_end",
    ]

    data_dir = Path(args.data_dir)
    rids = find_intersection_rids(data_dir, arms)
    print(f"Comparison set: {len(rids)} report_ids in (sonnet ∩ {' ∩ '.join(arms)})\n")

    for arm in arms:
        for field in fields:
            print(f"━━━ {arm} vs sonnet — {field} ━━━")
            disagreements = find_disagreements(rids, data_dir, arm, field)
            one_nulls = find_one_null(rids, data_dir, arm, field)
            print(f"  disagreements (both emitted, differ): {len(disagreements)}")
            print(f"  one_null (exactly one emitted):       {len(one_nulls)}")

            if disagreements:
                # Category histogram
                cats: dict[str, int] = {}
                for d in disagreements:
                    cats[d["category"]] = cats.get(d["category"], 0) + 1
                print("\n  by category:")
                for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
                    print(f"    {n:3d}  {cat}")

                print("\n  full list:")
                print(f"    {'report_id':<10}  {'sonnet':<20}  {'mini':<20}  category")
                for d in sorted(disagreements, key=lambda x: x["category"]):
                    print(
                        f"    {d['report_id']:<10}  {str(d['sonnet']):<20}  "
                        f"{str(d['mini']):<20}  {d['category']}"
                    )

            if one_nulls:
                print("\n  one_null cases:")
                print(f"    {'report_id':<10}  {'which_null':<10}  {'sonnet':<20}  {'mini':<20}")
                for o in one_nulls[:15]:  # cap at 15 for readability
                    print(
                        f"    {o['report_id']:<10}  {o['which_null']:<10}  "
                        f"{str(o['sonnet']):<20}  {str(o['mini']):<20}"
                    )
                if len(one_nulls) > 15:
                    print(f"    ... and {len(one_nulls) - 15} more")
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Per-(arm-pair) field agreement across sonnet / mini-medium / mini-low.

Session: docs/active/leave-behind-prep/convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md
Results: docs/active/leave-behind-prep/results/20260609_cross_arm_agreement.md

Walks the 100-filing intersection of the three arms' on-disk outputs and
emits a per-field agreement matrix. Run after all three mini dispatches
land.

Agreement definition (per Dan 2026-06-09)
-----------------------------------------
- Two values agree iff they are EXACTLY equal after JSON canonicalization.
- BOTH-NULL is NOT agreement. When both arms emit null on a field, that
  is a separate category ("both abstained") and should be investigated,
  not papered over. The Day-2 finding that mini-minimal hits 98% null on
  reporting_period_start while Sonnet hits 0% null is precisely the kind
  of thing both-null-as-agreement would hide.
- ONE-NULL (one arm emits, the other doesn't) counts as DISAGREEMENT.
- Lists are compared by length only (not contents) — exact content equality
  is too strict for the noisy-extraction question this script answers; a
  separate per-list-item analysis is the right tool for list contents.

Output
------
Per field:
  n_compared              total filings both arms produced output for
  both_null               count where BOTH emitted null (separate bucket)
  one_null                count where exactly one emitted null
  both_emitted_agree      count where both emitted non-null AND values agree
  both_emitted_disagree   count where both emitted non-null AND values differ
  agreement_rate          both_emitted_agree / (both_emitted_agree +
                                                both_emitted_disagree)
                          -- denominator excludes both-null and one-null
                          -- conservative; null asymmetry shows separately

Headline table: one row per (arm-pair, field) with the five counts above.

Run
---
    uv run python scripts/gpt5mini_oh_300slice_cross_arm_agreement.py \\
        --out docs/active/leave-behind-prep/results/20260609_cross_arm_agreement.md

If --out is omitted, writes markdown to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
)

# Fields to compare. Curated subset of LobbyingFiling: scalar content fields
# plus list-length checks. Skipped:
#   - id/state/filing_type: should be identical across all extractions of the
#     same source; not interesting.
#   - source_url, source_document, provenance, raw_text, supersedes: provenance
#     metadata; Sonnet vs mini differ in serialization shape (see Day-2 null
#     divergence table), not in extraction semantics.
#   - filer_person, filer_organization (objects, not scalars): handle via
#     name extraction below.
SCALAR_FIELDS = [
    "filer_role",
    "filing_id",
    "filing_action",
    "is_current",
    "reporting_period_start",
    "reporting_period_end",
    "filed_date",
    "total_compensation",
    "total_reimbursements",
    "total_other_costs",
    "total_expenditure",
    "total_hours_communicating",
    "total_hours_other",
    "total_income",
    "is_itemized",
]

# Fields whose value is itself an object — we compare the canonical name only,
# since nested-object equality is too strict and Person/Organization equality
# is its own can of worms.
NAMED_OBJECT_FIELDS = [
    "filer_person",
    "filer_organization",
    "employer",
]

# Fields whose value is a list. We compare list LENGTH only here; per-item
# content equivalence requires its own per-list-type comparison logic.
LIST_LENGTH_FIELDS = [
    "positions",
    "expenditures",
    "engagements",
    "gifts",
    "extraction_warnings",
]


def _latest_filing_json(report_dir: Path, prefix: str | None = None) -> Path | None:
    """Return the most recent filing.json under report_dir, by mtime.

    `prefix` filters subdirectory names (e.g., "mini_medium_run_1_" to scope
    to one arm).
    """
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


def _canonicalize(v: Any) -> Any:
    """Canonicalize a value for equality comparison.

    The intent is: same logical value → same canonical form, but no semantic
    normalization (no date-format conversion, no case folding, no whitespace
    collapsing). That's "exact equality after JSON canonicalization" per
    the Dan 2026-06-09 design call.
    """
    if v is None:
        return None
    if isinstance(v, dict):
        return tuple(sorted((k, _canonicalize(vv)) for k, vv in v.items()))
    if isinstance(v, list):
        return tuple(_canonicalize(x) for x in v)
    return v


def _name_of(obj: Any) -> str | None:
    """Extract a name from a Person/Organization-shaped dict, else None."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get("name")
    return None


def load_arm_filing(
    rid: str, data_dir: Path, *, arm: str
) -> dict | None:
    """Load the filing.json for a (report_id, arm) pair, or None if missing.

    Arm is one of: 'sonnet', 'medium', 'low', 'minimal'.
    """
    if arm == "sonnet":
        report_dir = data_dir / "extracted" / rid
        path = _latest_filing_json(report_dir)
    else:
        prefix = f"mini_{arm}_run_1_"
        report_dir = data_dir / EXTRACTED_OPENAI_SUBDIR / rid
        path = _latest_filing_json(report_dir, prefix=prefix)
    if path is None:
        return None
    return json.loads(path.read_text())


def field_value(filing: dict, field: str) -> Any:
    """Return the value to compare for a given field, with named-object handling."""
    if field in NAMED_OBJECT_FIELDS:
        return _name_of(filing.get(field))
    if field in LIST_LENGTH_FIELDS:
        v = filing.get(field)
        return None if v is None else len(v)
    return filing.get(field)


def compare_pair(
    rids: list[str],
    arm_a: str,
    arm_b: str,
    data_dir: Path,
) -> dict[str, dict[str, int]]:
    """For each field, count agreement / disagreement / null patterns across rids.

    Returns: field -> {
        n_compared, both_null, one_null,
        both_emitted_agree, both_emitted_disagree
    }
    """
    fields = SCALAR_FIELDS + NAMED_OBJECT_FIELDS + LIST_LENGTH_FIELDS
    stats: dict[str, dict[str, int]] = {
        f: {
            "n_compared": 0,
            "both_null": 0,
            "one_null": 0,
            "both_emitted_agree": 0,
            "both_emitted_disagree": 0,
        }
        for f in fields
    }
    n_loaded = 0
    for rid in rids:
        fa = load_arm_filing(rid, data_dir, arm=arm_a)
        fb = load_arm_filing(rid, data_dir, arm=arm_b)
        if fa is None or fb is None:
            continue
        n_loaded += 1
        for f in fields:
            va = field_value(fa, f)
            vb = field_value(fb, f)
            stats[f]["n_compared"] += 1
            a_null = va is None
            b_null = vb is None
            if a_null and b_null:
                stats[f]["both_null"] += 1
            elif a_null or b_null:
                stats[f]["one_null"] += 1
            else:
                if _canonicalize(va) == _canonicalize(vb):
                    stats[f]["both_emitted_agree"] += 1
                else:
                    stats[f]["both_emitted_disagree"] += 1
    return stats, n_loaded


def find_intersection_rids(data_dir: Path) -> list[str]:
    """Return report_ids present in sonnet + mini_medium + mini_low + mini_minimal.

    Each arm's filing must be discoverable (latest by mtime under the right
    prefix). Order is deterministic: sorted by report_id.
    """
    sonnet_root = data_dir / "extracted"
    mini_root = data_dir / EXTRACTED_OPENAI_SUBDIR
    if not sonnet_root.is_dir():
        raise FileNotFoundError(f"No sonnet baseline at {sonnet_root}")
    if not mini_root.is_dir():
        raise FileNotFoundError(f"No mini outputs at {mini_root}")

    candidates = sorted(p.name for p in sonnet_root.iterdir() if p.is_dir())
    intersection: list[str] = []
    skipped: dict[str, int] = {a: 0 for a in ("sonnet", "medium", "low", "minimal")}
    for rid in candidates:
        ok = True
        for arm in ("sonnet", "medium", "low", "minimal"):
            f = load_arm_filing(rid, data_dir, arm=arm)
            if f is None:
                skipped[arm] += 1
                ok = False
                break
        if ok:
            intersection.append(rid)
    return intersection, skipped


def render_markdown(
    pairs_stats: dict[tuple[str, str], dict[str, dict[str, int]]],
    intersection_size: int,
    skipped: dict[str, int],
) -> str:
    out: list[str] = []
    out.append("# Cross-arm field agreement — sonnet / mini-medium / mini-low\n")
    out.append(
        f"Comparison set: **{intersection_size} filings** present in all four arms "
        f"(sonnet + mini-medium + mini-low + mini-minimal).\n"
    )
    if any(skipped.values()):
        out.append("Filings missing per arm during intersection scan:\n")
        for arm, n in skipped.items():
            if n:
                out.append(f"- {arm}: {n} report_ids missing\n")
        out.append("\n")
    out.append(
        "## Definitions\n"
        "- **both_null:** both arms emitted null on this field. Investigate; "
        "this is NOT counted as agreement per the 2026-06-09 design call.\n"
        "- **one_null:** exactly one arm emitted null. Counted as disagreement.\n"
        "- **both_emitted_agree:** both arms emitted non-null AND values are "
        "exactly equal after JSON canonicalization.\n"
        "- **both_emitted_disagree:** both arms emitted non-null but values differ.\n"
        "- **agreement_rate:** both_emitted_agree / "
        "(both_emitted_agree + both_emitted_disagree). Denominator excludes "
        "null cells so null asymmetry shows up separately in the both_null "
        "and one_null columns.\n\n"
    )
    for (a, b), stats in pairs_stats.items():
        out.append(f"## {a} vs {b}\n\n")
        out.append(
            "| field | n | both_null | one_null | agree | disagree | "
            "agreement_rate |\n"
        )
        out.append(
            "|---|---:|---:|---:|---:|---:|---:|\n"
        )
        for field, s in stats.items():
            denom = s["both_emitted_agree"] + s["both_emitted_disagree"]
            rate = (
                f"{s['both_emitted_agree']/denom:.1%}" if denom else "—"
            )
            out.append(
                f"| `{field}` | {s['n_compared']} | {s['both_null']} | "
                f"{s['one_null']} | {s['both_emitted_agree']} | "
                f"{s['both_emitted_disagree']} | {rate} |\n"
            )
        out.append("\n")
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument(
        "--out", default=None,
        help="Path to write markdown report. Default: stdout.",
    )
    parser.add_argument(
        "--pairs", default="sonnet,medium;sonnet,low;medium,low",
        help=(
            "Semicolon-separated list of arm-pairs to compare. "
            "Default: sonnet-medium, sonnet-low, medium-low. "
            "Pass 'all' for every pairing across sonnet/medium/low/minimal."
        ),
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    intersection, skipped = find_intersection_rids(data_dir)
    print(
        f"[cross-arm] intersection: {len(intersection)} report_ids",
        file=sys.stderr,
    )
    for arm, n in skipped.items():
        if n:
            print(f"[cross-arm] {arm} missing on {n} report_ids", file=sys.stderr)

    if args.pairs == "all":
        arms = ["sonnet", "medium", "low", "minimal"]
        pairs = [
            (arms[i], arms[j])
            for i in range(len(arms))
            for j in range(i + 1, len(arms))
        ]
    else:
        pairs = [
            tuple(p.split(",")) for p in args.pairs.split(";") if p.strip()
        ]

    pairs_stats: dict[tuple[str, str], dict] = {}
    for a, b in pairs:
        print(f"[cross-arm] comparing {a} vs {b}", file=sys.stderr)
        stats, _ = compare_pair(intersection, a, b, data_dir)
        pairs_stats[(a, b)] = stats

    md = render_markdown(pairs_stats, len(intersection), skipped)
    if args.out:
        Path(args.out).write_text(md)
        print(f"[cross-arm] wrote {args.out}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

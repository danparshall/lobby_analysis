"""Generate per-row provenance table from v2 TSV + freeze-decisions doc.

For each of the 181 compendium rows, produces a row in a markdown table with:
- `compendium_row_id`
- 2-token prefix family (the row's structural anchor)
- `first_introduced_by` (which projection-mapping doc first added the row to the union)
- D-decision references (D1-D8, D12, D16 -- the freeze decisions that renamed, merged, or
  promoted the row by name)
- One-line excerpt from the TSV `notes` column

The D-decision refs are derived programmatically by reading the freeze-decisions
markdown and capturing which rows each decision named explicitly. This is meant
to be re-run if the v2 TSV is regenerated (by `tools/freeze_canonicalize_rows.py`)
so the provenance table stays in lock-step.

Output: 20260514_provenance_table.md alongside this script.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TSV = ROOT / "compendium" / "disclosure_side_compendium_items_v2.tsv"
FREEZE_DOC = (
    ROOT
    / "docs"
    / "historical"
    / "compendium-source-extracts"
    / "results"
    / "projections"
    / "20260513_row_freeze_decisions.md"
)
OUT = Path(__file__).with_suffix(".md")


def two_token_prefix(row_id: str) -> str:
    toks = row_id.split("_")
    return "_".join(toks[:2]) if len(toks) >= 2 else row_id


def extract_d_decisions(freeze_md: str) -> dict[str, list[str]]:
    """Return a mapping {row_id: [d_decision_ids]}.

    Walks every D-decision section header (e.g., '### D1 — ...'). Inside each
    section, finds row_id-shaped tokens (snake_case identifiers backticked or in
    markdown tables) and credits the D-decision to every row_id mentioned. We
    only credit the *target* (v2) row_id when a section's two-column merge/rename
    table is present -- the v1 source name lives in the freeze doc as historical
    context but isn't the canonical v2 name.

    Heuristic: a row_id-shaped string is `[a-z][a-z0-9_]+` of length >= 3 tokens.
    We filter to only IDs that exist in the v2 TSV to avoid false positives on
    arbitrary snake-case prose.
    """
    # Section split: lines starting with '### D'
    sections: list[tuple[str, str]] = []  # (decision_id, body)
    current: list[str] = []
    current_id: str | None = None
    for line in freeze_md.splitlines():
        m = re.match(r"^### (D\d+)\b", line)
        if m:
            if current_id is not None:
                sections.append((current_id, "\n".join(current)))
            current_id = m.group(1)
            current = [line]
        else:
            current.append(line)
    if current_id is not None:
        sections.append((current_id, "\n".join(current)))

    return dict(sections_to_pairs(sections))


def sections_to_pairs(sections: list[tuple[str, str]]):
    """Yield (decision_id, body) pairs as-is."""
    for d_id, body in sections:
        yield d_id, body


def credit_decisions_to_rows(
    sections: dict[str, str], v2_row_ids: set[str]
) -> dict[str, list[str]]:
    """For each D-decision section, extract the row_ids it names (target column when
    a merge/rename table is present)."""
    row_to_decisions: dict[str, list[str]] = defaultdict(list)
    id_pattern = re.compile(r"`([a-z][a-z0-9_]{8,})`")

    for d_id, body in sections.items():
        # Find all backticked row_id-like tokens
        candidates = set(id_pattern.findall(body))
        # Filter to v2 row_ids only -- the freeze doc cites both v1 source names
        # (which no longer exist) and v2 target names; we want only the v2.
        targets = candidates & v2_row_ids
        for row_id in targets:
            row_to_decisions[row_id].append(d_id)

    # Sort decisions per row (D1, D2, ... rather than D2, D1)
    for row_id, decisions in row_to_decisions.items():
        decisions.sort(key=lambda d: int(d[1:]))

    return dict(row_to_decisions)


def main() -> int:
    rows: list[dict[str, str]] = []
    with TSV.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            rows.append(r)

    v2_row_ids = {r["compendium_row_id"] for r in rows}

    sections: dict[str, str] = {}
    current_id: str | None = None
    current: list[str] = []
    for line in FREEZE_DOC.read_text().splitlines():
        m = re.match(r"^### (D\d+)\b", line)
        if m:
            if current_id is not None:
                sections[current_id] = "\n".join(current)
            current_id = m.group(1)
            current = [line]
        else:
            current.append(line)
    if current_id is not None:
        sections[current_id] = "\n".join(current)

    row_to_decisions = credit_decisions_to_rows(sections, v2_row_ids)

    # Build per-row prefix families
    by_prefix: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        by_prefix[two_token_prefix(r["compendium_row_id"])].append(r["compendium_row_id"])

    # Write markdown
    n = len(rows)
    lines: list[str] = []
    lines.append("# Per-row provenance table — v2 compendium")
    lines.append("")
    lines.append(f"Source TSV: `{TSV.relative_to(ROOT)}` ({n} rows)")
    lines.append(f"Freeze doc: `{FREEZE_DOC.relative_to(ROOT)}`")
    lines.append("")
    lines.append("Generated by `20260514_provenance_table.py` on 2026-05-14.")
    lines.append("")
    lines.append(
        "Each row's D-decision refs are derived programmatically by scanning the "
        "freeze-decisions doc for backticked v2 row_ids. A row will show a D-decision "
        "ref if the doc's section for that decision mentions the row by name "
        "(target name in merge/rename tables; KEEP-list rows in Section 4/5/6)."
    )
    lines.append("")
    lines.append(
        "**Coverage check.** Of 181 rows, "
        f"{sum(1 for r in rows if r['compendium_row_id'] in row_to_decisions)} have at least one "
        f"D-decision ref. The remainder are rows that survived the freeze unchanged "
        "(introduced via their projection-mapping doc, with no freeze-level rename / merge / KEEP-callout)."
    )
    lines.append("")

    lines.append("## Per-row provenance")
    lines.append("")
    lines.append("| compendium_row_id | 2-tok family | first_introduced_by | D-refs | notes excerpt |")
    lines.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["compendium_row_id"]):
        rid = r["compendium_row_id"]
        family = two_token_prefix(rid)
        first = r["first_introduced_by"].replace("_projection_mapping.md", "").replace(".md", "")
        decs = ", ".join(row_to_decisions.get(rid, []))
        notes = r["notes"].strip()
        # Truncate notes for table-readability
        if len(notes) > 120:
            notes = notes[:117] + "..."
        # Escape any pipe chars in notes
        notes = notes.replace("|", "\\|")
        lines.append(f"| `{rid}` | `{family}_*` | {first} | {decs} | {notes} |")
    lines.append("")

    # Family-grouped summary, nested 1-token -> 2-token.
    # The 1-token level is the "structural" family identity (e.g. `actor_*` is
    # really one family even though every member splits into a singleton at
    # 2-token granularity). The 2-token level is the sub-family-within-family
    # (e.g. `lobbyist_spending_*` vs `lobbyist_reg_*` vs `lobbyist_directory_*`).
    lines.append("## Provenance grouped by family")
    lines.append("")
    lines.append(
        "1-token prefix is the structural family identity; 2-token sub-families "
        "are listed underneath when the 1-token family has internal structure."
    )
    lines.append("")

    by_1tok: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_1tok[r["compendium_row_id"].split("_")[0]].append(r)

    for one_tok, family_rows in sorted(by_1tok.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(family_rows) < 2:
            continue
        lines.append(f"### `{one_tok}_*` ({len(family_rows)} rows)")
        lines.append("")
        firsts_in_family = defaultdict(int)
        for fr in family_rows:
            firsts_in_family[fr["first_introduced_by"]] += 1
        intro_summary = ", ".join(
            f"{c} from `{doc}`" for doc, c in sorted(firsts_in_family.items(), key=lambda kv: -kv[1])
        )
        lines.append(f"Introduced: {intro_summary}.")
        lines.append("")
        family_decisions: set[str] = set()
        for fr in family_rows:
            family_decisions.update(row_to_decisions.get(fr["compendium_row_id"], []))
        if family_decisions:
            lines.append(
                f"D-decisions touching this family: {', '.join(sorted(family_decisions, key=lambda d: int(d[1:])))}."
            )
            lines.append("")
        # 2-token sub-families (only show when >= 2 members each, to suppress
        # singleton-only sub-bucket spam in families like `actor_*`).
        sub_buckets: dict[str, list[str]] = defaultdict(list)
        for fr in family_rows:
            sub_buckets[two_token_prefix(fr["compendium_row_id"])].append(fr["compendium_row_id"])
        multi_sub = {k: v for k, v in sub_buckets.items() if len(v) >= 2}
        singleton_subs = [
            v[0] for k, v in sub_buckets.items() if len(v) == 1
        ]
        if multi_sub:
            lines.append("**2-token sub-families:**")
            lines.append("")
            for sub, ms in sorted(multi_sub.items(), key=lambda kv: -len(kv[1])):
                lines.append(f"- `{sub}_*` ({len(ms)} rows)")
            if singleton_subs:
                lines.append(
                    f"- ({len(singleton_subs)} row{'s' if len(singleton_subs) != 1 else ''} "
                    f"with singleton 2-token sub-prefix)"
                )
            lines.append("")
        elif singleton_subs:
            lines.append(
                f"_All {len(family_rows)} rows have singleton 2-token sub-prefixes — "
                f"the family identity lives at the 1-token level._"
            )
            lines.append("")

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT} ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

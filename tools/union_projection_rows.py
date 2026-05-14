#!/usr/bin/env python3
"""Union compendium-row references from the Phase B projection mapping docs.

Reads each of the 8 score-projection mapping docs' "## Summary of compendium
rows touched" section, parses the markdown row tables, dedupes by row_id
across docs, and emits results/projections/disclosure_side_compendium_items_v1.tsv.

LobbyView's 4 candidate NEW rows (LV-1..LV-4) are appended as
status=freeze-candidate (parsed manually from the schema-coverage doc's narrative).
LV-5 (bill_client_link) is documented as recommended-OUT in the schema-coverage
mapping doc and omitted here.

OpenSecrets-distinctive 3 candidate rows (OS-tabled 2026-05-12) are not in any
mapping doc and are not pulled in here; they're a separate row-freeze-brainstorm
input.

Output schema (TSV):
    compendium_row_id, cell_type, axis, rubrics_reading, n_rubrics,
    first_introduced_by, status, notes
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS_DIR = (
    REPO_ROOT
    / "docs"
    / "active"
    / "compendium-source-extracts"
    / "results"
    / "projections"
)
OUTPUT_TSV = PROJECTIONS_DIR / "disclosure_side_compendium_items_v1.tsv"

# Mapping doc filename -> rubric tag. Order matters: first-introduced-by is
# computed by walking this dict in order and taking the first doc that lists
# each row.
SCORE_PROJECTION_DOCS: dict[str, str] = {
    "cpi_2015_c11_projection_mapping.md": "cpi_2015",
    "pri_2010_projection_mapping.md": "pri_2010",
    "sunlight_2015_projection_mapping.md": "sunlight_2015",
    "newmark_2017_projection_mapping.md": "newmark_2017",
    "newmark_2005_projection_mapping.md": "newmark_2005",
    "opheim_1991_projection_mapping.md": "opheim_1991",
    "hiredguns_2007_projection_mapping.md": "hg_2007",
    "focal_2024_projection_mapping.md": "focal_2024",
}

# LobbyView freeze-candidates (parsed from lobbyview_schema_coverage.md narrative).
# Kept here so the union TSV carries all current freeze inputs in one place.
LOBBYVIEW_FREEZE_CANDIDATES: list[dict[str, str]] = [
    {
        "row_id": "lobbyist_report_distinguishes_in_house_vs_contract_filer",
        "cell_type": "binary",
        "axis": "legal",
        "rubrics_reading": "lobbyview:is_client_self_filer (candidate)",
        "notes": "LV-1; LDA §10; for: explicit distinction in LDA + Kim 2025 uses it; against: implicit in α form-split + scope.2",
    },
    {
        "row_id": "lobbyist_filings_flagged_as_amendment_vs_original",
        "cell_type": "binary",
        "axis": "legal",
        "rubrics_reading": "lobbyview:is_amendment (candidate)",
        "notes": "LV-2; data-quality signal vs operational metadata",
    },
    {
        "row_id": "lobbying_disclosure_uses_standardized_issue_code_taxonomy",
        "cell_type": "typed: enum {none / state_specific / lda / other}",
        "axis": "legal",
        "rubrics_reading": "lobbyview:issue_code (candidate)",
        "notes": "LV-3; LDA §15 fixed taxonomy; states usually have state-specific or free-text",
    },
    {
        "row_id": "lobbying_report_records_inferred_bill_links_to_specific_bills",
        "cell_type": "binary",
        "axis": "practical",
        "rubrics_reading": "lobbyview:bill_client_link (candidate)",
        "notes": "LV-4; derived inference, not disclosure; LobbyView mapping recommends OUT",
    },
]


# ---------------------------------------------------------------------------
# Markdown table parsing
# ---------------------------------------------------------------------------


def split_markdown_tables(section_text: str) -> list[list[str]]:
    """Return runs of consecutive '|'-prefixed lines as separate tables."""
    tables: list[list[str]] = []
    current: list[str] = []
    for line in section_text.splitlines():
        if line.lstrip().startswith("|"):
            current.append(line)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _split_cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Split into (header_cells, list_of_row_cells); drops the separator row."""
    if not lines:
        return [], []
    header = _split_cells(lines[0])
    rows: list[list[str]] = []
    for line in lines[1:]:
        cells = _split_cells(line)
        if all(re.fullmatch(r"[-:\s]+", c or "-") for c in cells):
            continue
        if not cells or not any(cells):
            continue
        rows.append(cells)
    return header, rows


def extract_summary_section(md_path: Path) -> str:
    """Return markdown between '## Summary of compendium rows touched' and next '## '."""
    text = md_path.read_text()
    m = re.search(r"^## Summary of compendium rows touched\s*$", text, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + (nxt.start() if nxt else len(text) - start)
    return text[start:end]


# ---------------------------------------------------------------------------
# Per-doc extraction
# ---------------------------------------------------------------------------


SKIP_ROW_PATTERNS = (
    # Composite/derived row markers that don't name a single canonical row_id
    re.compile(r"^\("),  # e.g., "(derived projection from PRI cadence family ...)"
)

# Composite row entries that describe a multi-cell OR-projection read of
# pre-existing rows. These DON'T create new row_ids; they grant the reading
# rubric a read on each constituent row. Keys are the composite text as it
# appears in the source doc's Summary table (after backtick + paren removal
# is messy, so we match on substring presence).
COMPOSITE_ROW_EXPANSIONS: list[tuple[str, list[str]]] = [
    # Opheim 1991: 2-cell monthly OR
    (
        "lobbyist_report_cadence_includes_monthly` + `principal_report_cadence_includes_monthly",
        [
            "lobbyist_report_cadence_includes_monthly",
            "principal_report_cadence_includes_monthly",
        ],
    ),
    # Newmark 2005: 8-cell more-frequent-than-annual OR
    (
        "lobbyist_report_cadence_includes_{monthly,quarterly,triannual,semiannual}",
        [
            "lobbyist_report_cadence_includes_monthly",
            "lobbyist_report_cadence_includes_quarterly",
            "lobbyist_report_cadence_includes_triannual",
            "lobbyist_report_cadence_includes_semiannual",
            "principal_report_cadence_includes_monthly",
            "principal_report_cadence_includes_quarterly",
            "principal_report_cadence_includes_triannual",
            "principal_report_cadence_includes_semiannual",
        ],
    ),
]


def normalize_cell_type(raw: str) -> str:
    """Strip backticks + collapse whitespace inside typed declarations."""
    s = raw.strip()
    # Drop backticks
    s = s.replace("`", "")
    # Strip leading "typed:" or "typed " prefix variation -> canonical "typed "
    s = re.sub(r"\btyped\s*:\s*", "typed ", s)
    # Collapse multiple whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def clean_row_id(raw: str) -> str:
    s = raw.strip()
    # Strip single pair of backticks if present
    if s.startswith("`") and s.endswith("`"):
        s = s[1:-1]
    # Strip outer parens-wrapped notes
    return s.strip()


def find_col(header: list[str], keyword: str) -> int | None:
    for i, h in enumerate(header):
        if keyword in h.lower():
            return i
    return None


def normalize_axis(raw: str) -> str:
    s = raw.lower().strip()
    has_legal = "legal" in s
    has_practical = "practical" in s
    if has_legal and has_practical:
        return "legal+practical"
    if has_legal:
        return "legal"
    if has_practical:
        return "practical"
    return s


def parse_doc(md_path: Path, rubric_tag: str) -> tuple[list[dict], list[str]]:
    """Return (records, warnings)."""
    section = extract_summary_section(md_path)
    if not section:
        return [], [f"{md_path.name}: no Summary section found"]

    records: list[dict] = []
    warnings: list[str] = []

    # Detect PRI-style subsections that imply axis from section header
    has_axis_subheaders = bool(
        re.search(
            r"^### .*(Accessibility-side|Disclosure-law-side).*$",
            section,
            re.MULTILINE,
        )
    )

    if has_axis_subheaders:
        # Split by ### subheaders; each subsection has its own implied axis
        subheader_re = re.compile(r"^### .*$", re.MULTILINE)
        positions = [m.start() for m in subheader_re.finditer(section)]
        headers = subheader_re.findall(section)
        positions.append(len(section))
        for i, header_text in enumerate(headers):
            part = section[positions[i] : positions[i + 1]]
            low = header_text.lower()
            if "accessibility-side" in low or "practical_availability" in low:
                implied_axis = "practical"
            elif "disclosure-law-side" in low or "legal_availability" in low:
                implied_axis = "legal"
            else:
                implied_axis = ""
            for tbl in split_markdown_tables(part):
                header, rows = parse_table(tbl)
                if not rows:
                    continue
                axis_col = find_col(header, "axis")
                status_col = find_col(header, "status")
                cell_type_col = find_col(header, "cell type") or 1
                for cells in rows:
                    recs = _row_to_record(
                        cells,
                        rubric_tag,
                        md_path.name,
                        axis_col=axis_col,
                        status_col=status_col,
                        cell_type_col=cell_type_col,
                        implied_axis=implied_axis,
                        warnings=warnings,
                    )
                    records.extend(recs)
    else:
        for tbl in split_markdown_tables(section):
            header, rows = parse_table(tbl)
            if not rows:
                continue
            axis_col = find_col(header, "axis")
            status_col = find_col(header, "status")
            cell_type_col = find_col(header, "cell type") or 1
            for cells in rows:
                recs = _row_to_record(
                    cells,
                    rubric_tag,
                    md_path.name,
                    axis_col=axis_col,
                    status_col=status_col,
                    cell_type_col=cell_type_col,
                    implied_axis="",
                    warnings=warnings,
                )
                records.extend(recs)

    return records, warnings


def _row_to_record(
    cells: list[str],
    rubric_tag: str,
    source_doc: str,
    *,
    axis_col: int | None,
    status_col: int | None,
    cell_type_col: int,
    implied_axis: str,
    warnings: list[str],
) -> list[dict]:
    """Return a list of records. Composite row entries expand to multiple records."""
    if not cells or len(cells) < 2:
        return []
    raw = cells[0].strip()
    if not raw or raw.lower() in ("row id (working name)", "row id"):
        return []
    if any(p.match(raw) for p in SKIP_ROW_PATTERNS):
        warnings.append(f"{source_doc}: skipped non-row line: {raw[:80]}")
        return []

    # Check for composite row entries (multi-cell OR-projection reads)
    expansion = None
    for marker, constituents in COMPOSITE_ROW_EXPANSIONS:
        if marker in raw:
            expansion = constituents
            break
    if expansion is not None:
        warnings.append(
            f"{source_doc}: expanded composite read into {len(expansion)} constituent rows ({rubric_tag} added as reader)"
        )

    if expansion is None:
        row_ids = [clean_row_id(raw)]
    else:
        row_ids = expansion

    cell_type_raw = cells[cell_type_col] if cell_type_col < len(cells) else ""
    cell_type = normalize_cell_type(cell_type_raw)
    if axis_col is not None and axis_col < len(cells):
        axis = normalize_axis(cells[axis_col])
    else:
        axis = implied_axis
    status_in_doc = ""
    if status_col is not None and status_col < len(cells):
        status_in_doc = cells[status_col]

    out = []
    for rid in row_ids:
        if not rid:
            continue
        # For expanded constituents, we cannot reliably infer cell_type from the
        # composite entry — leave empty so the union takes the cell_type from
        # the row's original-introducer doc.
        rec_cell_type = "" if expansion is not None else cell_type
        out.append(
            {
                "row_id": rid,
                "cell_type": rec_cell_type,
                "axis": axis,
                "rubric_tag": rubric_tag,
                "status_in_doc": status_in_doc,
                "source_mapping_doc": source_doc,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Union + write
# ---------------------------------------------------------------------------


def main() -> None:
    if not PROJECTIONS_DIR.exists():
        raise SystemExit(f"projections dir not found: {PROJECTIONS_DIR}")

    all_records: list[dict] = []
    all_warnings: list[str] = []
    per_doc_counts: dict[str, int] = {}

    for filename, rubric_tag in SCORE_PROJECTION_DOCS.items():
        path = PROJECTIONS_DIR / filename
        if not path.exists():
            all_warnings.append(f"missing mapping doc: {filename}")
            continue
        recs, warns = parse_doc(path, rubric_tag)
        per_doc_counts[filename] = len(recs)
        all_records.extend(recs)
        all_warnings.extend(warns)

    # Union by row_id
    union: dict[str, dict] = {}
    for rec in all_records:
        rid = rec["row_id"]
        if rid not in union:
            union[rid] = {
                "compendium_row_id": rid,
                "cell_type": rec["cell_type"],
                "axis": rec["axis"],
                "rubrics_reading": [rec["rubric_tag"]],
                "statuses_in_docs": [
                    f"{rec['rubric_tag']}={rec['status_in_doc']}"
                    if rec["status_in_doc"]
                    else rec["rubric_tag"]
                ],
                "source_docs": [rec["source_mapping_doc"]],
            }
        else:
            ex = union[rid]
            if rec["rubric_tag"] not in ex["rubrics_reading"]:
                ex["rubrics_reading"].append(rec["rubric_tag"])
            ex["source_docs"].append(rec["source_mapping_doc"])
            ex["statuses_in_docs"].append(
                f"{rec['rubric_tag']}={rec['status_in_doc']}"
                if rec["status_in_doc"]
                else rec["rubric_tag"]
            )
            # Merge axes (take union if different)
            if rec["axis"] and not ex["axis"]:
                ex["axis"] = rec["axis"]
            elif rec["axis"] and ex["axis"] and rec["axis"] != ex["axis"]:
                # Combine
                merged = "+".join(
                    sorted(set(ex["axis"].split("+") + rec["axis"].split("+")))
                )
                ex["axis"] = merged
            # Cell type: keep first non-empty; warn on conflict
            if rec["cell_type"] and ex["cell_type"] and rec["cell_type"] != ex["cell_type"]:
                all_warnings.append(
                    f"cell_type conflict for `{rid}`: "
                    f"{ex['cell_type']!r} ({ex['source_docs'][0]}) vs "
                    f"{rec['cell_type']!r} ({rec['source_mapping_doc']})"
                )

    # first_introduced_by = first rubric in SCORE_PROJECTION_DOCS order that reads it
    rubric_order = list(SCORE_PROJECTION_DOCS.values())
    rubric_to_doc = {v: k for k, v in SCORE_PROJECTION_DOCS.items()}
    for rid, info in union.items():
        for rb in rubric_order:
            if rb in info["rubrics_reading"]:
                info["first_introduced_by"] = rubric_to_doc[rb]
                break
        else:
            info["first_introduced_by"] = ""

    # Build output rows
    rows_out: list[dict] = []
    for rid in sorted(union):
        info = union[rid]
        n = len(info["rubrics_reading"])
        notes = ""
        if n == 1:
            notes = f"single-rubric ({info['rubrics_reading'][0]})"
        rows_out.append(
            {
                "compendium_row_id": rid,
                "cell_type": info["cell_type"],
                "axis": info["axis"],
                "rubrics_reading": ";".join(sorted(info["rubrics_reading"])),
                "n_rubrics": n,
                "first_introduced_by": info["first_introduced_by"],
                "status": "firm",
                "notes": notes,
            }
        )

    # Append LobbyView freeze-candidates (not from score-projection table parse)
    for fc in LOBBYVIEW_FREEZE_CANDIDATES:
        rows_out.append(
            {
                "compendium_row_id": fc["row_id"],
                "cell_type": fc["cell_type"],
                "axis": fc["axis"],
                "rubrics_reading": fc["rubrics_reading"],
                "n_rubrics": 0,
                "first_introduced_by": "lobbyview_schema_coverage.md",
                "status": "freeze-candidate",
                "notes": fc["notes"],
            }
        )

    fieldnames = [
        "compendium_row_id",
        "cell_type",
        "axis",
        "rubrics_reading",
        "n_rubrics",
        "first_introduced_by",
        "status",
        "notes",
    ]
    with OUTPUT_TSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows_out:
            writer.writerow(row)

    firm = sum(1 for r in rows_out if r["status"] == "firm")
    cand = sum(1 for r in rows_out if r["status"] == "freeze-candidate")
    single = sum(
        1 for r in rows_out if r["status"] == "firm" and r["n_rubrics"] == 1
    )

    print("Per-doc parsed-row counts:")
    for fn, n in per_doc_counts.items():
        print(f"  {fn}: {n}")
    print()
    print(f"Firm rows (union of 8 score-projection mappings): {firm}")
    print(f"Freeze-candidate rows (LobbyView LV-1..LV-4):     {cand}")
    print(f"Total rows in TSV:                                {len(rows_out)}")
    print(f"Single-rubric firm rows:                          {single}")
    print()
    print(f"Wrote: {OUTPUT_TSV.relative_to(REPO_ROOT)}")

    if all_warnings:
        print()
        print(f"Warnings ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()

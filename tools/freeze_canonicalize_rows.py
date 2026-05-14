#!/usr/bin/env python3
"""Apply compendium 2.0 row-freeze decisions (D1-D19) to v1.tsv → v2.tsv.

Input: docs/active/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v1.tsv
Output: docs/active/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv

Decisions encoded:
- D1: merge lobbyist_report_includes_direct_compensation (PRI) + lobbyist_spending_report_includes_compensation (CPI)
      → lobbyist_spending_report_includes_total_compensation (8-rubric).
- D2: merge principal_report_includes_direct_compensation (HG+PRI) into
      principal_spending_report_includes_compensation_paid_to_lobbyists (CPI; now 3-rubric).
- D3: rename PRI E2 prefix lobbyist_report_includes_* → lobbyist_spending_report_includes_*
      and PRI E1 prefix principal_report_includes_* → principal_spending_report_includes_*.
      Cadence rows (E1h/E2h) and uses_itemized_format also renamed. Newmark-introduced
      contributions_received row also renamed.
- D4: rename materiality_threshold_financial_value → lobbyist_filing_de_minimis_threshold_dollars
      and materiality_threshold_time_percent → lobbyist_filing_de_minimis_threshold_time_percent.
- D5: rename ..._compensation_broken_down_by_client → ..._compensation_broken_down_by_payer.
- D6: split def_target_legislative_or_executive_staff (FOCAL) → merge into existing
      def_target_legislative_staff (CPI) + add NEW def_target_executive_staff (FOCAL).
- D7: keep contributions_received_for_lobbying combined (no actor-split); rename per D3.
- D8: rename lobbyist_disclosure_includes_* → lobbyist_reg_form_includes_* (2 rows).
- D9: lobbying_data_downloadable_in_analytical_format cell_type → binary.
- D10: lobbyist_registration_required cell_type stays two-axis.
- D11: registration_deadline_days_after_first_lobbying cell_type stays two-axis.
- D12: LV-1 IN as firm row (1-rubric: lobbyview).
- D13: LV-2 OUT.
- D14: LV-3 OUT.
- D15: LV-4 OUT.
- D16: OS-1 IN as NEW firm row (path-b unvalidated; 0-rubric).
- D17: OS-2 OUT (stays in _tabled/).
- D18: OS-3 OUT (stays in _tabled/).
- D19: full-text vs structured search split — DEFER (no change to TSV).

Cell_type cosmetic normalization (Section 2 of decision log) also applied silently.
"""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJ_DIR = (
    REPO_ROOT
    / "docs"
    / "active"
    / "compendium-source-extracts"
    / "results"
    / "projections"
)
V1 = PROJ_DIR / "disclosure_side_compendium_items_v1.tsv"
V2 = PROJ_DIR / "disclosure_side_compendium_items_v2.tsv"

# D1 + D2: merge maps {source_row_id: canonical_row_id}
MERGES = {
    "lobbyist_report_includes_direct_compensation": "lobbyist_spending_report_includes_total_compensation",
    "lobbyist_spending_report_includes_compensation": "lobbyist_spending_report_includes_total_compensation",
    "principal_report_includes_direct_compensation": "principal_spending_report_includes_compensation_paid_to_lobbyists",
    # D6 collapse half: legislative_or_executive_staff merges into legislative_staff
    "def_target_legislative_or_executive_staff": "def_target_legislative_staff",
}

# D3 + D4 + D5 + D8: rename map {old_row_id: new_row_id}
# (Note: rows in MERGES are not in RENAMES; they're handled before renaming.)
RENAMES = {
    # D3 — PRI E2 (lobbyist contents)
    "lobbyist_report_includes_contacts_made": "lobbyist_spending_report_includes_contacts_made",
    "lobbyist_report_includes_general_issues": "lobbyist_spending_report_includes_general_issues",
    "lobbyist_report_includes_gifts_entertainment_transport_lodging": "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
    "lobbyist_report_includes_indirect_costs": "lobbyist_spending_report_includes_indirect_costs",
    "lobbyist_report_includes_lobbyist_contact_info": "lobbyist_spending_report_includes_lobbyist_contact_info",
    "lobbyist_report_includes_principal_business_nature": "lobbyist_spending_report_includes_principal_business_nature",
    "lobbyist_report_includes_principal_contact_info": "lobbyist_spending_report_includes_principal_contact_info",
    "lobbyist_report_includes_principal_names": "lobbyist_spending_report_includes_principal_names",
    "lobbyist_report_includes_specific_bill_number": "lobbyist_spending_report_includes_specific_bill_number",
    "lobbyist_report_uses_itemized_format": "lobbyist_spending_report_uses_itemized_format",
    # D3 — PRI E1 (principal contents)
    "principal_report_includes_business_nature": "principal_spending_report_includes_business_nature",
    "principal_report_includes_contacts_made": "principal_spending_report_includes_contacts_made",
    "principal_report_includes_general_issues": "principal_spending_report_includes_general_issues",
    "principal_report_includes_gifts_entertainment_transport_lodging": "principal_spending_report_includes_gifts_entertainment_transport_lodging",
    "principal_report_includes_indirect_costs": "principal_spending_report_includes_indirect_costs",
    "principal_report_includes_lobbyist_contact_info": "principal_spending_report_includes_lobbyist_contact_info",
    "principal_report_includes_lobbyist_names": "principal_spending_report_includes_lobbyist_names",
    "principal_report_includes_major_financial_contributors": "principal_spending_report_includes_major_financial_contributors",
    "principal_report_includes_principal_contact_info": "principal_spending_report_includes_principal_contact_info",
    "principal_report_includes_specific_bill_number": "principal_spending_report_includes_specific_bill_number",
    "principal_report_includes_total_expenditures": "principal_spending_report_includes_total_expenditures",
    "principal_report_uses_itemized_format": "principal_spending_report_uses_itemized_format",
    # D3 — cadence rows (PRI E1h + E2h)
    "lobbyist_report_cadence_includes_annual": "lobbyist_spending_report_cadence_includes_annual",
    "lobbyist_report_cadence_includes_monthly": "lobbyist_spending_report_cadence_includes_monthly",
    "lobbyist_report_cadence_includes_other": "lobbyist_spending_report_cadence_includes_other",
    "lobbyist_report_cadence_includes_quarterly": "lobbyist_spending_report_cadence_includes_quarterly",
    "lobbyist_report_cadence_includes_semiannual": "lobbyist_spending_report_cadence_includes_semiannual",
    "lobbyist_report_cadence_includes_triannual": "lobbyist_spending_report_cadence_includes_triannual",
    "lobbyist_report_cadence_other_specification": "lobbyist_spending_report_cadence_other_specification",
    "principal_report_cadence_includes_annual": "principal_spending_report_cadence_includes_annual",
    "principal_report_cadence_includes_monthly": "principal_spending_report_cadence_includes_monthly",
    "principal_report_cadence_includes_other": "principal_spending_report_cadence_includes_other",
    "principal_report_cadence_includes_quarterly": "principal_spending_report_cadence_includes_quarterly",
    "principal_report_cadence_includes_semiannual": "principal_spending_report_cadence_includes_semiannual",
    "principal_report_cadence_includes_triannual": "principal_spending_report_cadence_includes_triannual",
    "principal_report_cadence_other_specification": "principal_spending_report_cadence_other_specification",
    # D3 — Newmark-introduced contributions row
    "lobbyist_or_principal_report_includes_contributions_received_for_lobbying": "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying",
    # D4 — filing-de-minimis threshold rename (was PRI's materiality_*)
    "materiality_threshold_financial_value": "lobbyist_filing_de_minimis_threshold_dollars",
    "materiality_threshold_time_percent": "lobbyist_filing_de_minimis_threshold_time_percent",
    # D5 — compensation broken-down rename
    "lobbyist_spending_report_includes_compensation_broken_down_by_client": "lobbyist_spending_report_includes_compensation_broken_down_by_payer",
    # D8 — lobbyist_disclosure → lobbyist_reg_form prefix
    "lobbyist_disclosure_includes_business_associations_with_officials": "lobbyist_reg_form_includes_business_associations_with_officials",
    "lobbyist_disclosure_includes_employment_type": "lobbyist_reg_form_includes_employment_type",
}

# D6 NEW row from staff-cell split.
SPLIT_NEW_ROWS = [
    {
        "compendium_row_id": "def_target_executive_staff",
        "cell_type": "binary",
        "axis": "legal",
        "rubrics_reading": "focal_2024",
        "first_introduced_by": "focal_2024_projection_mapping.md",
        "status": "firm",
        "notes": "single-rubric (focal_2024); split from def_target_legislative_or_executive_staff per D6",
    },
]

# D12 + D16 — promotions / additions
PROMOTIONS = {
    # D12: LV-1 from candidate → firm
    "lobbyist_report_distinguishes_in_house_vs_contract_filer": {
        "rubrics_reading": "lobbyview",
        "status": "firm",
        "notes": "single-rubric (lobbyview); LV-1 promoted at freeze per D12",
    },
}

OS_NEW_ROWS = [
    # D16: OS-1 IN as path-b unvalidated row
    {
        "compendium_row_id": "separate_registrations_for_lobbyists_and_clients",
        "cell_type": "binary",
        "axis": "legal",
        "rubrics_reading": "(unvalidated; path-b)",
        "first_introduced_by": "_tabled/opensecrets_2022_tabled.md",
        "status": "firm",
        "notes": "OS-1 path-b unvalidated; OpenSecrets Cat 1 reads but is tabled. Real distinguishing observable in some states.",
    },
]

# D13, D14, D15 — drop these LobbyView candidates entirely from v2
DROPS = {
    "lobbyist_filings_flagged_as_amendment_vs_original",  # LV-2
    "lobbying_disclosure_uses_standardized_issue_code_taxonomy",  # LV-3
    "lobbying_report_records_inferred_bill_links_to_specific_bills",  # LV-4
}

# Cell-type normalization (Section 2 of decision log)
CELL_TYPE_NORMALIZE = {
    "typed Optional[<TimeThreshold>]": "typed Optional[TimeThreshold]",
    "typed Optional[<count + FTE>]": "typed Optional[count_with_FTE]",
    "typed Optional[<TimeSpent>]": "typed Optional[TimeSpent]",
    "typed Optional[<SectorClassification>]": "typed Optional[SectorClassification]",
    "typed <UpdateCadence>": "typed UpdateCadence",
    "binary (practical)": "binary",
    "binary derived from CPI #206's 4-feature cell": "binary",
    "binary (derived)": "binary",
}

# Hardcoded canonical rubric order (for sorting rubrics_reading lists)
RUBRIC_ORDER = [
    "cpi_2015",
    "pri_2010",
    "sunlight_2015",
    "newmark_2017",
    "newmark_2005",
    "opheim_1991",
    "hg_2007",
    "focal_2024",
    "lobbyview",
]


def normalize_cell_type(s: str) -> str:
    s = s.strip()
    return CELL_TYPE_NORMALIZE.get(s, s)


def merge_rubrics(*lists: str) -> str:
    """Merge semicolon-joined rubric lists, dedupe, sort by canonical order."""
    seen = set()
    for s in lists:
        if not s:
            continue
        for r in s.split(";"):
            r = r.strip()
            if r:
                seen.add(r)
    ordered = [r for r in RUBRIC_ORDER if r in seen]
    # Anything not in RUBRIC_ORDER (e.g., "lobbyview:..." raw forms) appended in-order
    other = [r for r in seen if r not in RUBRIC_ORDER]
    return ";".join(ordered + sorted(other))


def main() -> None:
    rows_in = list(csv.DictReader(V1.open(), delimiter="\t"))
    print(f"v1.tsv: {len(rows_in)} rows")

    # Stage 1 — drop LV candidates that are OUT (D13, D14, D15) + freeze-candidate LV-1 row body
    # (we'll re-add LV-1 with promoted firm fields after merges)
    rows = []
    for r in rows_in:
        rid = r["compendium_row_id"]
        if rid in DROPS:
            continue
        # Drop the freeze-candidate version of LV-1 (we re-add as firm via PROMOTIONS below)
        if rid in PROMOTIONS and r.get("status") == "freeze-candidate":
            continue
        rows.append(r)

    # Stage 2 — apply merges (D1, D2, D6 collapse half)
    merged_rows = {}  # canonical_row_id → merged row dict
    for r in rows:
        rid = r["compendium_row_id"]
        target_rid = MERGES.get(rid, rid)
        if target_rid in merged_rows:
            existing = merged_rows[target_rid]
            existing["rubrics_reading"] = merge_rubrics(
                existing["rubrics_reading"], r["rubrics_reading"]
            )
            # Keep the earliest first_introduced_by (CPI before PRI etc.)
            # Use cell_type from canonical target if present
        else:
            merged_rows[target_rid] = dict(r)
            merged_rows[target_rid]["compendium_row_id"] = target_rid

    # Stage 3 — apply renames (D3, D4, D5, D8). Renames don't merge; they're 1:1.
    renamed_rows = {}
    for rid, r in merged_rows.items():
        new_rid = RENAMES.get(rid, rid)
        if new_rid != rid:
            r = dict(r)
            r["compendium_row_id"] = new_rid
        renamed_rows[new_rid] = r

    # Stage 4 — apply promotions (D12: LV-1 firm)
    for rid, fields in PROMOTIONS.items():
        if rid in renamed_rows:
            renamed_rows[rid].update(fields)
        else:
            # If the freeze-candidate row was dropped already, build from scratch
            renamed_rows[rid] = {
                "compendium_row_id": rid,
                "cell_type": "binary",
                "axis": "legal",
                "first_introduced_by": "lobbyview_schema_coverage.md",
                **fields,
            }

    # Stage 5 — add D6 split NEW + D16 OS-1 NEW
    for new_row in SPLIT_NEW_ROWS + OS_NEW_ROWS:
        renamed_rows[new_row["compendium_row_id"]] = dict(new_row)

    # Stage 6 — recompute n_rubrics + normalize cell_type
    out_rows = []
    for rid, r in renamed_rows.items():
        rubrics = r.get("rubrics_reading", "")
        # Path-b unvalidated rows: n_rubrics = 0
        if rubrics.startswith("(unvalidated"):
            n_rubrics = 0
        else:
            n_rubrics = len([x for x in rubrics.split(";") if x.strip()])
        r["n_rubrics"] = str(n_rubrics)
        r["cell_type"] = normalize_cell_type(r.get("cell_type", ""))
        # Notes column: refresh for canonical row_ids whose rubric set changed
        if n_rubrics == 1 and not r.get("notes", "").startswith("single-rubric"):
            sole = [x for x in rubrics.split(";") if x.strip()][0]
            r["notes"] = f"single-rubric ({sole})"
        elif n_rubrics > 1 and r.get("notes", "").startswith("single-rubric"):
            r["notes"] = ""
        out_rows.append(r)

    # Stage 7 — sort by row_id for deterministic output
    out_rows.sort(key=lambda r: r["compendium_row_id"])

    # Write
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
    with V2.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for r in out_rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    # Summary stats
    print(f"v2.tsv: {len(out_rows)} rows")
    by_n = {}
    for r in out_rows:
        n = int(r["n_rubrics"])
        by_n[n] = by_n.get(n, 0) + 1
    print("Tier distribution (n_rubrics → count):")
    for n in sorted(by_n.keys(), reverse=True):
        print(f"  {n}: {by_n[n]}")
    print(f"Wrote: {V2}")


if __name__ == "__main__":
    main()

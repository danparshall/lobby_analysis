"""Build the compendium artifact + framework dedup map.

Stage A of `docs/active/statute-retrieval/plans/20260430_compendium_population_and_smr_fill.md`.

Curation judgments are encoded as Python data structures in this file. The
script reads the four source rubric CSVs (PRI 2010 disclosure, PRI 2010
accessibility, FOCAL 2024, Sunlight 2015), applies the judgments, and emits:

    data/compendium/disclosure_items.csv
    data/compendium/framework_dedup_map.csv

Idempotent: rerun any time. The CSVs are committed so reviewers can diff
both the script and the output.

Usage:
    uv run python scripts/build_compendium.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PRI_DISCLOSURE = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "pri-2026-rescore"
    / "results"
    / "pri_2010_disclosure_law_rubric.csv"
)
PRI_ACCESSIBILITY = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "pri-2026-rescore"
    / "results"
    / "pri_2010_accessibility_rubric.csv"
)
FOCAL = (
    REPO_ROOT
    / "docs"
    / "historical"
    / "focal-extraction"
    / "results"
    / "focal_2024_indicators.csv"
)
SUNLIGHT_DATA = REPO_ROOT / "papers" / "Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv"

OUT_DIR = REPO_ROOT / "data" / "compendium"
OUT_COMPENDIUM = OUT_DIR / "disclosure_items.csv"
OUT_DEDUP_MAP = OUT_DIR / "framework_dedup_map.csv"


# -----------------------------------------------------------------------------
# Compendium row model (in-memory, before CSV serialization)
# -----------------------------------------------------------------------------


@dataclass
class CompRow:
    id: str
    name: str
    description: str
    domain: str  # registration | reporting | financial | accessibility | etc.
    data_type: str  # boolean | numeric | categorical | free_text | compound
    framework_references: list[dict] = field(default_factory=list)
    maps_to_state_master_field: str | None = None
    maps_to_filing_field: str | None = None
    observable_from_database: bool = False
    notes: str = ""


# Index for cross-rubric ref injection. Keyed by (framework, item_id) → CompRow.
_index: dict[tuple[str, str], CompRow] = {}
_rows: list[CompRow] = []


def _add(row: CompRow) -> None:
    _rows.append(row)
    for ref in row.framework_references:
        _index[(ref["framework"], ref["item_id"])] = row


def _add_ref(framework: str, item_id: str, target_pri_id: str, item_text: str | None = None) -> None:
    """Attach a FrameworkReference to the compendium row that already references PRI:target_pri_id."""
    target = _index.get(("pri_2010_disclosure", target_pri_id)) or _index.get(
        ("pri_2010_accessibility", target_pri_id)
    )
    if target is None:
        raise KeyError(f"no compendium row references PRI:{target_pri_id}")
    target.framework_references.append(
        {"framework": framework, "item_id": item_id, **({"item_text": item_text} if item_text else {})}
    )
    _index[(framework, item_id)] = target


# -----------------------------------------------------------------------------
# PRI 2010 disclosure-law spine (61 atomic items)
# -----------------------------------------------------------------------------

# Keyed by PRI item_id. Encodes the curation judgments (compendium id, domain,
# observable_from_database). Domain bulk-assigned from PRI sub_component:
# A/B/C/D → registration; E1/E2 → reporting. data_type derived from PRI's
# data_type column (binary→boolean, numeric_*→numeric, text→free_text).
PRI_DISCLOSURE_JUDGMENTS: dict[str, dict] = {
    # A. Who is required to register
    "A1": {"id": "REG_LOBBYIST", "name": "Lobbyist must register", "domain": "registration"},
    "A2": {"id": "REG_VOLUNTEER_LOBBYIST", "name": "Volunteer lobbyist must register", "domain": "registration"},
    "A3": {"id": "REG_PRINCIPAL", "name": "Principal must register", "domain": "registration"},
    "A4": {"id": "REG_LOBBYING_FIRM", "name": "Lobbying firm must register", "domain": "registration"},
    "A5": {"id": "REG_GOVERNORS_OFFICE", "name": "Governor's office must register", "domain": "registration"},
    "A6": {"id": "REG_EXECUTIVE_AGENCY", "name": "Executive branch agency must register", "domain": "registration"},
    "A7": {"id": "REG_LEGISLATIVE_BRANCH", "name": "Legislative branch must register", "domain": "registration"},
    "A8": {"id": "REG_INDEPENDENT_AGENCY", "name": "Independent agency must register", "domain": "registration"},
    "A9": {"id": "REG_LOCAL_GOVERNMENT", "name": "Local government must register", "domain": "registration"},
    "A10": {"id": "REG_GOVT_LOBBYING_GOVT", "name": "Government lobbying government must register", "domain": "registration"},
    "A11": {"id": "REG_OTHER_PUBLIC_ENTITY", "name": "Other public entity must register", "domain": "registration"},
    # B. Government exemptions
    "B1": {"id": "EXEMPT_GOVT_OFFICIAL_CAPACITY", "name": "Government / official-capacity exemption exists", "domain": "registration"},
    "B2": {"id": "EXEMPT_GOVT_PARTIAL_RELIEF", "name": "Government partial relief from non-government rules", "domain": "registration"},
    "B3": {"id": "PARITY_GOVT_AS_LOBBYIST", "name": "Government subject to lobbyist disclosure rules", "domain": "registration"},
    "B4": {"id": "PARITY_GOVT_AS_PRINCIPAL", "name": "Government subject to principal disclosure rules", "domain": "registration"},
    # C. Definition of public entity
    "C0": {"id": "DEF_PUBLIC_ENTITY", "name": "Law defines 'public entity'", "domain": "registration"},
    "C1": {"id": "DEF_PUBLIC_ENTITY_OWNERSHIP", "name": "Public-entity definition uses ownership", "domain": "registration"},
    "C2": {"id": "DEF_PUBLIC_ENTITY_STRUCTURE", "name": "Public-entity definition uses structure / revenue composition", "domain": "registration"},
    "C3": {"id": "DEF_PUBLIC_ENTITY_CHARTER", "name": "Public-entity definition uses public charter / special protection", "domain": "registration"},
    # D. Materiality test (de-minimis)
    "D0": {"id": "THRESHOLD_MATERIALITY", "name": "Materiality (de-minimis) test exists", "domain": "registration"},
    "D1_present": {"id": "THRESHOLD_FINANCIAL_PRESENT", "name": "Financial de-minimis threshold exists", "domain": "registration"},
    "D1_value": {"id": "THRESHOLD_FINANCIAL_VALUE", "name": "Financial de-minimis dollar threshold (USD)", "domain": "registration"},
    "D2_present": {"id": "THRESHOLD_TIME_PRESENT", "name": "Time de-minimis threshold exists", "domain": "registration"},
    "D2_value": {"id": "THRESHOLD_TIME_VALUE", "name": "Time de-minimis percentage threshold", "domain": "registration"},
    # E1. Principal Reports
    "E1a": {"id": "RPT_PRINCIPAL_GATE", "name": "Principal must file disclosure report", "domain": "reporting"},
    "E1b": {"id": "RPT_PRINCIPAL_CONTACT", "name": "Principal report includes principal address & phone", "domain": "reporting"},
    "E1c": {"id": "RPT_PRINCIPAL_LOBBYIST_NAMES", "name": "Principal report lists representing lobbyists", "domain": "reporting"},
    "E1d": {"id": "RPT_PRINCIPAL_LOBBYIST_CONTACT", "name": "Principal report includes lobbyist address & phone", "domain": "reporting"},
    "E1e": {"id": "RPT_PRINCIPAL_BUSINESS_NATURE", "name": "Principal report includes nature of business (public/private)", "domain": "reporting"},
    "E1f_i": {"id": "RPT_PRINCIPAL_COMPENSATION", "name": "Principal report includes direct lobbying costs (compensation)", "domain": "reporting"},
    "E1f_ii": {"id": "RPT_PRINCIPAL_NON_COMPENSATION", "name": "Principal report includes indirect lobbying costs (non-compensation)", "domain": "reporting"},
    "E1f_iii": {"id": "RPT_PRINCIPAL_OTHER_COSTS", "name": "Principal report includes gifts / entertainment / transport / lodging", "domain": "reporting"},
    "E1f_iv": {"id": "RPT_PRINCIPAL_ITEMIZED", "name": "Principal report is itemized (vs lump-sum)", "domain": "reporting"},
    "E1g_i": {"id": "RPT_PRINCIPAL_ISSUE_GENERAL", "name": "Principal report discloses general issues lobbied", "domain": "reporting"},
    "E1g_ii": {"id": "RPT_PRINCIPAL_BILL_SPECIFIC", "name": "Principal report discloses specific bill numbers / legislation IDs", "domain": "reporting"},
    "E1h_i": {"id": "FREQ_PRINCIPAL_MONTHLY", "name": "Principal reporting frequency: monthly", "domain": "reporting"},
    "E1h_ii": {"id": "FREQ_PRINCIPAL_QUARTERLY", "name": "Principal reporting frequency: quarterly", "domain": "reporting"},
    "E1h_iii": {"id": "FREQ_PRINCIPAL_TRI_ANNUAL", "name": "Principal reporting frequency: tri-annual (legislative calendar)", "domain": "reporting"},
    "E1h_iv": {"id": "FREQ_PRINCIPAL_SEMI_ANNUAL", "name": "Principal reporting frequency: semi-annual", "domain": "reporting"},
    "E1h_v": {"id": "FREQ_PRINCIPAL_ANNUAL", "name": "Principal reporting frequency: annual", "domain": "reporting"},
    "E1h_vi": {"id": "FREQ_PRINCIPAL_OTHER", "name": "Principal reporting frequency: other (free-text)", "domain": "reporting"},
    "E1i": {"id": "RPT_PRINCIPAL_CONTACTS_LOGGED", "name": "Principal must disclose contacts (contact log)", "domain": "contact_log"},
    "E1j": {"id": "RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS", "name": "Principal must disclose major financial contributors", "domain": "reporting"},
    # E2. Lobbyist Disclosure
    "E2a": {"id": "RPT_LOBBYIST_GATE", "name": "Lobbyist must file disclosure report", "domain": "reporting"},
    "E2b": {"id": "RPT_LOBBYIST_CONTACT", "name": "Lobbyist report includes lobbyist address & phone", "domain": "reporting"},
    "E2c": {"id": "RPT_LOBBYIST_PRINCIPAL_NAMES", "name": "Lobbyist report lists represented principals", "domain": "reporting"},
    "E2d": {"id": "RPT_LOBBYIST_PRINCIPAL_CONTACT", "name": "Lobbyist report includes principal address & phone", "domain": "reporting"},
    "E2e": {"id": "RPT_LOBBYIST_PRINCIPAL_NATURE", "name": "Lobbyist report includes principal's business nature (public/private)", "domain": "reporting"},
    "E2f_i": {"id": "RPT_LOBBYIST_COMPENSATION", "name": "Lobbyist report includes direct lobbying costs (compensation)", "domain": "reporting"},
    "E2f_ii": {"id": "RPT_LOBBYIST_NON_COMPENSATION", "name": "Lobbyist report includes indirect lobbying costs (non-compensation)", "domain": "reporting"},
    "E2f_iii": {"id": "RPT_LOBBYIST_OTHER_COSTS", "name": "Lobbyist report includes gifts / entertainment / transport / lodging", "domain": "reporting"},
    "E2f_iv": {"id": "RPT_LOBBYIST_ITEMIZED", "name": "Lobbyist report is itemized (vs lump-sum)", "domain": "reporting"},
    "E2g_i": {"id": "RPT_LOBBYIST_ISSUE_GENERAL", "name": "Lobbyist report discloses general issues lobbied", "domain": "reporting"},
    "E2g_ii": {"id": "RPT_LOBBYIST_BILL_SPECIFIC", "name": "Lobbyist report discloses specific bill numbers / legislation IDs", "domain": "reporting"},
    "E2h_i": {"id": "FREQ_LOBBYIST_MONTHLY", "name": "Lobbyist reporting frequency: monthly", "domain": "reporting"},
    "E2h_ii": {"id": "FREQ_LOBBYIST_QUARTERLY", "name": "Lobbyist reporting frequency: quarterly", "domain": "reporting"},
    "E2h_iii": {"id": "FREQ_LOBBYIST_TRI_ANNUAL", "name": "Lobbyist reporting frequency: tri-annual (legislative calendar)", "domain": "reporting"},
    "E2h_iv": {"id": "FREQ_LOBBYIST_SEMI_ANNUAL", "name": "Lobbyist reporting frequency: semi-annual", "domain": "reporting"},
    "E2h_v": {"id": "FREQ_LOBBYIST_ANNUAL", "name": "Lobbyist reporting frequency: annual", "domain": "reporting"},
    "E2h_vi": {"id": "FREQ_LOBBYIST_OTHER", "name": "Lobbyist reporting frequency: other (free-text)", "domain": "reporting"},
    "E2i": {"id": "RPT_LOBBYIST_CONTACTS_LOGGED", "name": "Lobbyist must disclose contacts (contact log)", "domain": "contact_log"},
}


def _data_type_from_pri(pri_dt: str) -> str:
    if pri_dt == "binary":
        return "boolean"
    if pri_dt.startswith("numeric_"):
        return "numeric"
    if pri_dt == "text":
        return "free_text"
    if pri_dt.startswith("ordinal_"):
        return "categorical"
    raise ValueError(f"unknown PRI data_type: {pri_dt}")


def _observable_from_pri_id(pri_id: str) -> bool:
    """A/B/C/D require statute reading. E* can be inferred from filings.

    This is the bulk rule per plan A.3.7. Per-row overrides go in NOTES if any.
    """
    return pri_id.startswith("E")


# PRI 2010 accessibility (22 items, all domain=accessibility, all observable=True)
PRI_ACCESSIBILITY_JUDGMENTS: dict[str, dict] = {
    "Q1": {"id": "ACC_DATA_AVAILABLE_AT_ALL", "name": "Some lobbying data available (any format, by request or web)"},
    "Q2": {"id": "ACC_DEDICATED_WEBSITE", "name": "Dedicated state lobbying website exists"},
    "Q3": {"id": "ACC_WEBSITE_FINDABILITY", "name": "State lobbying website is easily found"},
    "Q4": {"id": "ACC_CURRENT_YEAR_DATA", "name": "Current-year lobbying data available on the website"},
    "Q5": {"id": "ACC_HISTORICAL_DATA", "name": "Historical lobbying data available, downloadable, or viewable"},
    "Q6": {"id": "ACC_DOWNLOAD_ANALYSIS_READY", "name": "Data downloadable in analysis-ready electronic format (CSV / Excel / SPSS)"},
    "Q7a": {"id": "ACC_SORT_BY_PRINCIPAL", "name": "Search/sort by principal (city, hiring authority, employer, corporation)"},
    "Q7b": {"id": "ACC_SORT_BY_PRINCIPAL_LOCATION", "name": "Search/sort by principal location (address, city)"},
    "Q7c": {"id": "ACC_SORT_BY_LOBBYIST_NAME", "name": "Search/sort by lobbyist name"},
    "Q7d": {"id": "ACC_SORT_BY_LOBBYIST_LOCATION", "name": "Search/sort by lobbyist location (address, city)"},
    "Q7e": {"id": "ACC_SORT_BY_DATE", "name": "Search/sort by specific date"},
    "Q7f": {"id": "ACC_SORT_BY_PERIOD", "name": "Search/sort by specific time period (quarter etc.)"},
    "Q7g": {"id": "ACC_SORT_BY_TOTAL_EXPENDITURES", "name": "Search/sort by total expenditures"},
    "Q7h": {"id": "ACC_SORT_BY_COMPENSATION", "name": "Search/sort by compensation spending"},
    "Q7i": {"id": "ACC_SORT_BY_MISC_EXPENSES", "name": "Search/sort by miscellaneous (non-compensation) expenses"},
    "Q7j": {"id": "ACC_SORT_BY_FUNDING_SOURCE", "name": "Search/sort by sources of funding (public/taxpayer-funded)"},
    "Q7k": {"id": "ACC_SORT_BY_SUBJECT", "name": "Search/sort by subject of lobbying (item of legislation)"},
    "Q7l": {"id": "ACC_SORT_BY_DESIGNATED_ENTITY", "name": "Search/sort by designated entities assigned to lobbyist"},
    "Q7m": {"id": "ACC_SORT_BY_LEGAL_STATUS", "name": "Search/sort by legal status of principal (govt / non-profit / for-profit)"},
    "Q7n": {"id": "ACC_SORT_BY_SECTOR", "name": "Search/sort by sector"},
    "Q7o": {"id": "ACC_SORT_BY_SUB_SECTOR", "name": "Search/sort by sub-sector"},
    "Q8": {"id": "ACC_MULTI_CRITERIA_SORT", "name": "Multi-criteria simultaneous sort (ordinal 0-15)"},
}


def build_pri_accessibility() -> None:
    with PRI_ACCESSIBILITY.open() as f:
        for row in csv.DictReader(f):
            q_id = row["item_id"]
            judgment = PRI_ACCESSIBILITY_JUDGMENTS[q_id]
            comp_row = CompRow(
                id=judgment["id"],
                name=judgment["name"],
                description=row["item_text"].rstrip(".") + ".",
                domain="accessibility",
                data_type=_data_type_from_pri(row["data_type"]),
                framework_references=[
                    {
                        "framework": "pri_2010_accessibility",
                        "item_id": q_id,
                        "item_text": row["item_text"],
                    }
                ],
                observable_from_database=True,
            )
            _add(comp_row)


def _dedup_self_pri_accessibility() -> None:
    for q_id in PRI_ACCESSIBILITY_JUDGMENTS:
        _dedup.append(
            DedupRow(
                source_framework="pri_2010_accessibility",
                source_item_id=q_id,
                target_expression=f"pri_2010_accessibility:{q_id}",
                notes="self-reference (PRI accessibility row)",
            )
        )


def build_pri_disclosure_spine() -> None:
    with PRI_DISCLOSURE.open() as f:
        for row in csv.DictReader(f):
            pri_id = row["item_id"]
            judgment = PRI_DISCLOSURE_JUDGMENTS[pri_id]
            comp_row = CompRow(
                id=judgment["id"],
                name=judgment["name"],
                description=row["item_text"].rstrip(".") + ".",
                domain=judgment["domain"],
                data_type=_data_type_from_pri(row["data_type"]),
                framework_references=[
                    {
                        "framework": "pri_2010_disclosure",
                        "item_id": pri_id,
                        "item_text": row["item_text"],
                    }
                ],
                observable_from_database=_observable_from_pri_id(pri_id),
            )
            _add(comp_row)


# -----------------------------------------------------------------------------
# Dedup map accumulator
# -----------------------------------------------------------------------------


@dataclass
class DedupRow:
    source_framework: str
    source_item_id: str
    target_expression: str
    notes: str = ""


_dedup: list[DedupRow] = []


def _dedup_self_pri_disclosure() -> None:
    for pri_id in PRI_DISCLOSURE_JUDGMENTS:
        _dedup.append(
            DedupRow(
                source_framework="pri_2010_disclosure",
                source_item_id=pri_id,
                target_expression=f"pri_2010_disclosure:{pri_id}",
                notes="self-reference (PRI is the spine)",
            )
        )


# -----------------------------------------------------------------------------
# Output writers
# -----------------------------------------------------------------------------


COMPENDIUM_FIELDS = [
    "id",
    "name",
    "description",
    "domain",
    "data_type",
    "framework_references_json",
    "maps_to_state_master_field",
    "maps_to_filing_field",
    "observable_from_database",
    "notes",
]

DEDUP_FIELDS = ["source_framework", "source_item_id", "target_expression", "notes"]


def write_outputs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUT_COMPENDIUM.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMPENDIUM_FIELDS)
        writer.writeheader()
        for r in _rows:
            writer.writerow(
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "domain": r.domain,
                    "data_type": r.data_type,
                    "framework_references_json": json.dumps(r.framework_references),
                    "maps_to_state_master_field": r.maps_to_state_master_field or "",
                    "maps_to_filing_field": r.maps_to_filing_field or "",
                    "observable_from_database": "True" if r.observable_from_database else "False",
                    "notes": r.notes,
                }
            )

    with OUT_DEDUP_MAP.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DEDUP_FIELDS)
        writer.writeheader()
        for d in _dedup:
            writer.writerow(
                {
                    "source_framework": d.source_framework,
                    "source_item_id": d.source_item_id,
                    "target_expression": d.target_expression,
                    "notes": d.notes,
                }
            )


def _summary() -> dict:
    by_framework: dict[str, int] = {}
    for r in _rows:
        for ref in r.framework_references:
            by_framework[ref["framework"]] = by_framework.get(ref["framework"], 0) + 1
    return {
        "compendium_rows": len(_rows),
        "framework_reference_counts": by_framework,
        "dedup_rows": len(_dedup),
    }


def main() -> int:
    build_pri_disclosure_spine()
    _dedup_self_pri_disclosure()
    build_pri_accessibility()
    _dedup_self_pri_accessibility()
    write_outputs()
    summary = _summary()
    print(f"Wrote {OUT_COMPENDIUM.relative_to(REPO_ROOT)}: {summary['compendium_rows']} rows")
    print(f"Wrote {OUT_DEDUP_MAP.relative_to(REPO_ROOT)}: {summary['dedup_rows']} rows")
    print(f"Framework reference counts: {summary['framework_reference_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

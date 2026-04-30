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
    # A. Who is required to register (no field_path; map to RegistrationRequirement)
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
    # B. Government exemptions (no field_path; routed to StateMasterRecord.notes per plan B.4)
    "B1": {"id": "EXEMPT_GOVT_OFFICIAL_CAPACITY", "name": "Government / official-capacity exemption exists", "domain": "registration"},
    "B2": {"id": "EXEMPT_GOVT_PARTIAL_RELIEF", "name": "Government partial relief from non-government rules", "domain": "registration"},
    "B3": {"id": "PARITY_GOVT_AS_LOBBYIST", "name": "Government subject to lobbyist disclosure rules", "domain": "registration"},
    "B4": {"id": "PARITY_GOVT_AS_PRINCIPAL", "name": "Government subject to principal disclosure rules", "domain": "registration"},
    # C. Definition of public entity (no field_path; routed to notes)
    "C0": {"id": "DEF_PUBLIC_ENTITY", "name": "Law defines 'public entity'", "domain": "registration"},
    "C1": {"id": "DEF_PUBLIC_ENTITY_OWNERSHIP", "name": "Public-entity definition uses ownership", "domain": "registration"},
    "C2": {"id": "DEF_PUBLIC_ENTITY_STRUCTURE", "name": "Public-entity definition uses structure / revenue composition", "domain": "registration"},
    "C3": {"id": "DEF_PUBLIC_ENTITY_CHARTER", "name": "Public-entity definition uses public charter / special protection", "domain": "registration"},
    # D. Materiality test (no field_path; D1/D2 thresholds map to top-level de_minimis_* fields on StateMasterRecord directly per plan B.4)
    "D0": {"id": "THRESHOLD_MATERIALITY", "name": "Materiality (de-minimis) test exists", "domain": "registration"},
    "D1_present": {"id": "THRESHOLD_FINANCIAL_PRESENT", "name": "Financial de-minimis threshold exists", "domain": "registration"},
    "D1_value": {"id": "THRESHOLD_FINANCIAL_VALUE", "name": "Financial de-minimis dollar threshold (USD)", "domain": "registration"},
    "D2_present": {"id": "THRESHOLD_TIME_PRESENT", "name": "Time de-minimis threshold exists", "domain": "registration"},
    "D2_value": {"id": "THRESHOLD_TIME_VALUE", "name": "Time de-minimis percentage threshold", "domain": "registration"},
    # E1. Principal Reports
    # E1a / E1h_* are NOT field-level — they map to ReportingPartyRequirement (gate / frequency).
    "E1a": {"id": "RPT_PRINCIPAL_GATE", "name": "Principal must file disclosure report", "domain": "reporting"},
    "E1b": {"id": "RPT_PRINCIPAL_CONTACT", "name": "Principal report includes principal address & phone", "domain": "reporting", "field_path": "filer_organization.contact_details[].value"},
    "E1c": {"id": "RPT_PRINCIPAL_LOBBYIST_NAMES", "name": "Principal report lists representing lobbyists", "domain": "reporting", "field_path": "registration::lobbyist.name", "field_note": "Stored on LobbyistRegistration; principal's lobbyist list = inverse of registrations where clients[] contains the principal."},
    "E1d": {"id": "RPT_PRINCIPAL_LOBBYIST_CONTACT", "name": "Principal report includes lobbyist address & phone", "domain": "reporting", "field_path": "registration::lobbyist.contact_details[].value", "field_note": "Lobbyist contact info is on the registration record, not the principal's filing."},
    "E1e": {"id": "RPT_PRINCIPAL_BUSINESS_NATURE", "name": "Principal report includes nature of business (public/private)", "domain": "reporting", "field_path": "filer_organization.legal_form"},
    "E1f_i": {"id": "RPT_PRINCIPAL_COMPENSATION", "name": "Principal report includes direct lobbying costs (compensation)", "domain": "reporting", "field_path": "total_compensation"},
    "E1f_ii": {"id": "RPT_PRINCIPAL_NON_COMPENSATION", "name": "Principal report includes indirect lobbying costs (non-compensation)", "domain": "reporting", "field_path": "total_reimbursements"},
    "E1f_iii": {"id": "RPT_PRINCIPAL_OTHER_COSTS", "name": "Principal report includes gifts / entertainment / transport / lodging", "domain": "reporting", "field_path": "total_other_costs"},
    "E1f_iv": {"id": "RPT_PRINCIPAL_ITEMIZED", "name": "Principal report is itemized (vs lump-sum)", "domain": "reporting", "field_path": "is_itemized"},
    "E1g_i": {"id": "RPT_PRINCIPAL_ISSUE_GENERAL", "name": "Principal report discloses general issues lobbied", "domain": "reporting", "field_path": "positions[].general_issue_area"},
    "E1g_ii": {"id": "RPT_PRINCIPAL_BILL_SPECIFIC", "name": "Principal report discloses specific bill numbers / legislation IDs", "domain": "reporting", "field_path": "positions[].bill_reference"},
    "E1h_i": {"id": "FREQ_PRINCIPAL_MONTHLY", "name": "Principal reporting frequency: monthly", "domain": "reporting"},
    "E1h_ii": {"id": "FREQ_PRINCIPAL_QUARTERLY", "name": "Principal reporting frequency: quarterly", "domain": "reporting"},
    "E1h_iii": {"id": "FREQ_PRINCIPAL_TRI_ANNUAL", "name": "Principal reporting frequency: tri-annual (legislative calendar)", "domain": "reporting"},
    "E1h_iv": {"id": "FREQ_PRINCIPAL_SEMI_ANNUAL", "name": "Principal reporting frequency: semi-annual", "domain": "reporting"},
    "E1h_v": {"id": "FREQ_PRINCIPAL_ANNUAL", "name": "Principal reporting frequency: annual", "domain": "reporting"},
    "E1h_vi": {"id": "FREQ_PRINCIPAL_OTHER", "name": "Principal reporting frequency: other (free-text)", "domain": "reporting"},
    "E1i": {"id": "RPT_PRINCIPAL_CONTACTS_LOGGED", "name": "Principal must disclose contacts (contact log)", "domain": "contact_log", "field_path": "engagements[]", "field_note": "Gate item: presence of any engagement entry = contacts disclosed."},
    "E1j": {"id": "RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS", "name": "Principal must disclose major financial contributors", "domain": "reporting", "field_note": "No clean LobbyingFiling field today; would surface as a separate financial_contributors[] disclosure if added."},
    # E2. Lobbyist Disclosure
    "E2a": {"id": "RPT_LOBBYIST_GATE", "name": "Lobbyist must file disclosure report", "domain": "reporting"},
    "E2b": {"id": "RPT_LOBBYIST_CONTACT", "name": "Lobbyist report includes lobbyist address & phone", "domain": "reporting", "field_path": "filer_person.contact_details[].value"},
    "E2c": {"id": "RPT_LOBBYIST_PRINCIPAL_NAMES", "name": "Lobbyist report lists represented principals", "domain": "reporting", "field_path": "registration::clients[].name"},
    "E2d": {"id": "RPT_LOBBYIST_PRINCIPAL_CONTACT", "name": "Lobbyist report includes principal address & phone", "domain": "reporting", "field_path": "registration::clients[].contact_details[].value"},
    "E2e": {"id": "RPT_LOBBYIST_PRINCIPAL_NATURE", "name": "Lobbyist report includes principal's business nature (public/private)", "domain": "reporting", "field_path": "registration::clients[].legal_form"},
    "E2f_i": {"id": "RPT_LOBBYIST_COMPENSATION", "name": "Lobbyist report includes direct lobbying costs (compensation)", "domain": "reporting", "field_path": "total_compensation"},
    "E2f_ii": {"id": "RPT_LOBBYIST_NON_COMPENSATION", "name": "Lobbyist report includes indirect lobbying costs (non-compensation)", "domain": "reporting", "field_path": "total_reimbursements"},
    "E2f_iii": {"id": "RPT_LOBBYIST_OTHER_COSTS", "name": "Lobbyist report includes gifts / entertainment / transport / lodging", "domain": "reporting", "field_path": "total_other_costs"},
    "E2f_iv": {"id": "RPT_LOBBYIST_ITEMIZED", "name": "Lobbyist report is itemized (vs lump-sum)", "domain": "reporting", "field_path": "is_itemized"},
    "E2g_i": {"id": "RPT_LOBBYIST_ISSUE_GENERAL", "name": "Lobbyist report discloses general issues lobbied", "domain": "reporting", "field_path": "positions[].general_issue_area"},
    "E2g_ii": {"id": "RPT_LOBBYIST_BILL_SPECIFIC", "name": "Lobbyist report discloses specific bill numbers / legislation IDs", "domain": "reporting", "field_path": "positions[].bill_reference"},
    "E2h_i": {"id": "FREQ_LOBBYIST_MONTHLY", "name": "Lobbyist reporting frequency: monthly", "domain": "reporting"},
    "E2h_ii": {"id": "FREQ_LOBBYIST_QUARTERLY", "name": "Lobbyist reporting frequency: quarterly", "domain": "reporting"},
    "E2h_iii": {"id": "FREQ_LOBBYIST_TRI_ANNUAL", "name": "Lobbyist reporting frequency: tri-annual (legislative calendar)", "domain": "reporting"},
    "E2h_iv": {"id": "FREQ_LOBBYIST_SEMI_ANNUAL", "name": "Lobbyist reporting frequency: semi-annual", "domain": "reporting"},
    "E2h_v": {"id": "FREQ_LOBBYIST_ANNUAL", "name": "Lobbyist reporting frequency: annual", "domain": "reporting"},
    "E2h_vi": {"id": "FREQ_LOBBYIST_OTHER", "name": "Lobbyist reporting frequency: other (free-text)", "domain": "reporting"},
    "E2i": {"id": "RPT_LOBBYIST_CONTACTS_LOGGED", "name": "Lobbyist must disclose contacts (contact log)", "domain": "contact_log", "field_path": "engagements[]", "field_note": "Gate item: presence of any engagement entry = contacts disclosed."},
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


# -----------------------------------------------------------------------------
# FOCAL 2024 (50 indicators)
#
# Each judgment has type ∈ {"1to1", "coarser", "new"}.
# - 1to1: attach FOCAL ref to a single compendium row already keyed by
#   (framework, pri_id).
# - coarser: attach FOCAL ref to multiple PRI rows; dedup target_expression
#   joins them with `&` (FOCAL = AND of the underlying items) or `|`
#   (FOCAL = OR; counted if any underlying item is required).
# - new: create a new compendium row with FOCAL as the only initial ref.
# -----------------------------------------------------------------------------

FOCAL_JUDGMENTS: list[dict] = [
    # Group 1: Scope
    {
        "focal_id": "1.1", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["A1", "A2", "A3", "A4", "A6", "A7", "A8", "A9", "A10", "A11"],
        "op": "&",
        "note": "FOCAL 1.1 (registry covers all listed types) = AND of PRI A-series",
    },
    {
        "focal_id": "1.2", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["D1_present", "D2_present"],
        "op": "&",
        "note": "polarity-flipped: FOCAL asks for low/no threshold, PRI asks if threshold exists",
    },
    {
        "focal_id": "1.3", "type": "new",
        "comp_id": "REG_LOBBYING_TARGETS_SCOPE",
        "name": "Scope of officials counted as lobbying targets",
        "domain": "registration", "data_type": "categorical", "observable": False,
    },
    {
        "focal_id": "1.4", "type": "new",
        "comp_id": "REG_LOBBYING_ACTIVITY_FORMS_SCOPE",
        "name": "Scope of activity forms counted as lobbying (oral, written, electronic, events)",
        "domain": "registration", "data_type": "categorical", "observable": False,
    },
    # Group 2: Timeliness
    {
        "focal_id": "2.1", "type": "new",
        "comp_id": "ACC_REGISTRY_UPDATE_FRESHNESS",
        "name": "Registry change updates frequency (target close to real-time)",
        "domain": "accessibility", "data_type": "categorical", "observable": True,
    },
    {
        "focal_id": "2.2", "type": "new",
        "comp_id": "ACC_ACTIVITY_DISCLOSURE_FRESHNESS",
        "name": "Lobbying activity disclosure freshness (target close to real-time)",
        "domain": "accessibility", "data_type": "categorical", "observable": True,
    },
    {
        "focal_id": "2.3", "type": "new",
        "comp_id": "RPT_OFFICIAL_DIARY_DISCLOSURE",
        "name": "Officials' / ministers' diaries (calendars / meeting logs) disclosed",
        "domain": "contact_log", "data_type": "boolean", "observable": False,
    },
    # Group 3: Openness
    {
        "focal_id": "3.1", "type": "1to1",
        "framework": "pri_2010_accessibility", "pri_id": "Q2",
    },
    {
        "focal_id": "3.2", "type": "new",
        "comp_id": "ACC_DIARIES_ONLINE",
        "name": "Lobbyist / minister diaries available online",
        "domain": "accessibility", "data_type": "boolean", "observable": True,
    },
    {
        "focal_id": "3.3", "type": "coarser",
        "framework": "pri_2010_accessibility",
        "pri_ids": ["Q1", "Q6"],
        "op": "&",
        "note": "FOCAL 3.3 is a 5-condition compound (no-registration, free, open license, non-proprietary, machine-readable); PRI Q1 covers availability and Q6 covers analysis-ready format. Open-license / no-registration are not in PRI",
    },
    {
        "focal_id": "3.4", "type": "1to1",
        "framework": "pri_2010_accessibility", "pri_id": "Q6",
    },
    {
        "focal_id": "3.5", "type": "1to1",
        "framework": "pri_2010_accessibility", "pri_id": "Q8",
    },
    {
        "focal_id": "3.6", "type": "new",
        "comp_id": "ACC_UNIQUE_IDENTIFIERS",
        "name": "Unique identifiers in registry (lobbyists, individuals, organisations)",
        "domain": "accessibility", "data_type": "boolean", "observable": True,
    },
    {
        "focal_id": "3.7", "type": "new",
        "comp_id": "ACC_LINKED_DATA",
        "name": "Linked / interconnected data (to other datasets, e.g. campaign finance)",
        "domain": "accessibility", "data_type": "boolean", "observable": True,
    },
    {
        "focal_id": "3.8", "type": "1to1",
        "framework": "pri_2010_accessibility", "pri_id": "Q5",
    },
    {
        "focal_id": "3.9", "type": "new",
        "comp_id": "ACC_CHANGE_FLAGGING",
        "name": "Changes / updates documented with a flagging system",
        "domain": "accessibility", "data_type": "boolean", "observable": True,
    },
    # Group 4: Descriptors
    {
        "focal_id": "4.1", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1c", "E2c"],
        "op": "|",
        "note": "FOCAL 4.1 (full names) finer than PRI but cross-references both name-listing rows",
    },
    {
        "focal_id": "4.2", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1b", "E1d", "E2b", "E2d"],
        "op": "|",
        "note": "FOCAL 4.2 (contact details) covers all four contact-detail rows on either side",
    },
    {
        "focal_id": "4.3", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1e", "E2e"],
        "op": "|",
        "note": "FOCAL 4.3 (legal form) on either principal-side or lobbyist-side report",
    },
    {
        "focal_id": "4.4", "type": "new",
        "comp_id": "RPT_ORG_REGISTRATION_NUMBER",
        "name": "Organization registration number (Sec-of-State entity ID or EIN)",
        "domain": "reporting", "data_type": "free_text", "observable": True,
    },
    {
        "focal_id": "4.5", "type": "new",
        "comp_id": "RPT_SECTOR_DISCLOSED",
        "name": "Sector / sub-sector of principal disclosed",
        "domain": "reporting", "data_type": "categorical", "observable": True,
    },
    {
        "focal_id": "4.6", "type": "new",
        "comp_id": "RPT_LOBBYIST_CONTRACT_TYPE",
        "name": "Type of lobbyist contract (salaried / contracted)",
        "domain": "reporting", "data_type": "categorical", "observable": True,
    },
    # Group 5: Revolving door
    {
        "focal_id": "5.1", "type": "new",
        "comp_id": "REVOLVING_LOBBYIST_PRIOR_OFFICES",
        "name": "List of all prior public offices held by lobbyist with dates",
        "domain": "revolving_door", "data_type": "compound", "observable": True,
    },
    {
        "focal_id": "5.2", "type": "new",
        "comp_id": "REVOLVING_COOLING_OFF_DATABASE",
        "name": "Database of officials banned from lobbying (cooling-off period)",
        "domain": "revolving_door", "data_type": "boolean", "observable": True,
    },
    # Group 6: Relationships
    {
        "focal_id": "6.1", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E2c",
        "note": "FOCAL 6.1 (consultant/firm client list) ≈ PRI E2c (lobbyist report lists represented principals)",
    },
    {
        "focal_id": "6.2", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E1j",
        "note": "FOCAL 6.2 (sponsors / members) ≈ PRI E1j (major financial contributors)",
    },
    {
        "focal_id": "6.3", "type": "new",
        "comp_id": "REL_BOARD_SEATS",
        "name": "List of board seats held (associations, companies)",
        "domain": "relationship", "data_type": "compound", "observable": True,
    },
    {
        "focal_id": "6.4", "type": "new",
        "comp_id": "REL_OFFICIAL_BUSINESS_TIES",
        "name": "Direct business associations with public officials, candidates, or household members",
        "domain": "relationship", "data_type": "compound", "observable": True,
    },
    # Group 7: Financials
    {
        "focal_id": "7.1", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E2f_i",
        "note": "FOCAL 7.1 (total lobbying income for consultants/firms) ≈ PRI E2f_i (lobbyist compensation)",
    },
    {
        "focal_id": "7.2", "type": "new",
        "comp_id": "FIN_INCOME_PER_CLIENT",
        "name": "Lobbying income per client (consultants / firms)",
        "domain": "financial", "data_type": "numeric", "observable": True,
    },
    {
        "focal_id": "7.3", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E1j",
        "note": "FOCAL 7.3 (income sources + amount) finer than PRI E1j (major financial contributors)",
    },
    {
        "focal_id": "7.4", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E1c",
        "note": "FOCAL 7.4 (number of lobbyists) implied by PRI E1c (lobbyists listed by name)",
    },
    {
        "focal_id": "7.5", "type": "new",
        "comp_id": "FIN_TIME_SPENT_LOBBYING",
        "name": "Amount of time spent on lobbying",
        "domain": "financial", "data_type": "numeric", "observable": True,
    },
    {
        "focal_id": "7.6", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1f_i", "E1f_ii", "E1f_iii"],
        "op": "&",
        "note": "FOCAL 7.6 (total expenditure) = AND of PRI E1f_i (comp) + E1f_ii (non-comp) + E1f_iii (other)",
    },
    {
        "focal_id": "7.7", "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1f_i", "E1f_ii"],
        "op": "&",
        "note": "FOCAL 7.7 (compensated vs uncompensated) = AND of PRI E1f_i + E1f_ii",
    },
    {
        "focal_id": "7.8", "type": "new",
        "comp_id": "FIN_EXPENDITURE_PER_ISSUE",
        "name": "Expenditure per issue / topic",
        "domain": "financial", "data_type": "numeric", "observable": True,
    },
    {
        "focal_id": "7.9", "type": "new",
        "comp_id": "FIN_TRADE_ASSOCIATION_DUES",
        "name": "Expenditure on membership / sponsorship of organisations that lobby",
        "domain": "financial", "data_type": "numeric", "observable": True,
    },
    {
        "focal_id": "7.10", "type": "1to1",
        "framework": "pri_2010_disclosure", "pri_id": "E1f_iii",
        "note": "FOCAL 7.10 (gifts / non-financial benefits) ≈ PRI E1f_iii (gifts/entertainment/transport/lodging)",
    },
    {
        "focal_id": "7.11", "type": "new",
        "comp_id": "FIN_CAMPAIGN_CONTRIBUTIONS",
        "name": "Campaign / political contributions disclosed (incl. in-kind)",
        "domain": "financial", "data_type": "compound", "observable": True,
    },
    # Group 8: Contact log fields (all NEW; PRI E1i / E2i are gate items only)
    {"focal_id": "8.1", "type": "new", "comp_id": "CONTACT_BENEFICIARY",
     "name": "Contact log: organisation / interest represented (beneficiary)",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.2", "type": "new", "comp_id": "CONTACT_PERSONS_CONTACTED",
     "name": "Contact log: names of persons contacted and their position",
     "domain": "contact_log", "data_type": "compound", "observable": True},
    {"focal_id": "8.3", "type": "new", "comp_id": "CONTACT_INSTITUTION",
     "name": "Contact log: institution / department contacted",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.4", "type": "new", "comp_id": "CONTACT_MEETING_ATTENDEES",
     "name": "Contact log: names of all meeting attendees",
     "domain": "contact_log", "data_type": "compound", "observable": True},
    {"focal_id": "8.5", "type": "new", "comp_id": "CONTACT_DATE",
     "name": "Contact log: date",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.6", "type": "new", "comp_id": "CONTACT_FORM",
     "name": "Contact log: form (in-person, video, phone)",
     "domain": "contact_log", "data_type": "categorical", "observable": True},
    {"focal_id": "8.7", "type": "new", "comp_id": "CONTACT_LOCATION",
     "name": "Contact log: location",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.8", "type": "new", "comp_id": "CONTACT_MATERIALS_SHARED",
     "name": "Contact log: materials shared (excluding commercially sensitive)",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.9", "type": "new", "comp_id": "CONTACT_TOPICS",
     "name": "Contact log: topics / issues discussed",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.10", "type": "new", "comp_id": "CONTACT_OUTCOMES_SOUGHT",
     "name": "Contact log: outcomes sought (legislation supported / opposed)",
     "domain": "contact_log", "data_type": "free_text", "observable": True},
    {"focal_id": "8.11", "type": "new", "comp_id": "CONTACT_LEGISLATIVE_REFERENCES",
     "name": "Contact log: targeted legislation / bill numbers / measures",
     "domain": "contact_log", "data_type": "compound", "observable": True},
]


# -----------------------------------------------------------------------------
# Sunlight 2015 (5 published categories → 7 atomic items per the decomposition
# in docs/active/statute-retrieval/results/20260429_sunlight_pri_item_level.md)
# -----------------------------------------------------------------------------

SUNLIGHT_JUDGMENTS: list[dict] = [
    {
        "sunlight_id": "activity",
        "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1g_i", "E1g_ii", "E2g_i", "E2g_ii"],
        "op": "|",
        "item_text": "Lobbyist Activity reporting (general subjects vs bills/actions vs bills+position)",
        "note": "Sunlight Activity ordinal: -1 none, 0 general subjects, 1 bills, 2 bills+position",
    },
    {
        "sunlight_id": "position_taken",
        "type": "new",
        "comp_id": "RPT_POSITION_TAKEN",
        "name": "Lobbyist position taken on legislation (support/oppose)",
        "domain": "reporting",
        "data_type": "categorical",
        "observable": True,
        "item_text": "Position taken on each bill or item lobbied (support/oppose)",
        "note": "Sunlight Activity score 2 implies position-taken disclosure; concept absent from PRI",
    },
    {
        "sunlight_id": "expenditure_transparency",
        "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1f_i", "E1f_ii", "E1f_iii", "E1f_iv", "E2f_i", "E2f_ii", "E2f_iii", "E2f_iv"],
        "op": "|",
        "item_text": "Expenditure Transparency (no report / lump / broad categories / itemized w/ dates+desc)",
        "note": "Sunlight ExpTrans ordinal: -1 no report, 0 lump, 1 broad categories, 2 itemized w/ dates+desc",
    },
    {
        "sunlight_id": "expenditure_format_granularity",
        "type": "new",
        "comp_id": "RPT_EXPENDITURE_FORMAT_GRANULARITY",
        "name": "Expenditure report format granularity (lump / broad / itemized-w/-dates+desc)",
        "domain": "reporting",
        "data_type": "categorical",
        "observable": True,
        "item_text": "Expenditure format granularity",
        "note": "Sunlight separates broad-categories from itemized-w/-dates+desc; PRI E*f_iv is binary itemized only",
    },
    {
        "sunlight_id": "expenditure_itemization_threshold",
        "type": "new",
        "comp_id": "RPT_EXPENDITURE_ITEMIZATION_THRESHOLD",
        "name": "Expenditure itemization threshold (expenses below $X exempt from itemization)",
        "domain": "reporting",
        "data_type": "numeric",
        "observable": False,
        "item_text": "Threshold below which expenditure itemization is not required",
        "note": "Sunlight Threshold concept is itemization-threshold (different from PRI D1 registration-threshold)",
    },
    {
        "sunlight_id": "document_accessibility",
        "type": "coarser",
        "framework": "pri_2010_accessibility",
        "pri_ids": ["Q1", "Q6", "Q8"],
        "op": "|",
        "item_text": "Document Accessibility (portal usability for finding & downloading data)",
        "note": "Sunlight DocAccess ordinal -2..2; overlaps PRI Q1 (data exists), Q6 (analysis-ready download), Q8 (multi-sort)",
    },
    {
        "sunlight_id": "compensation",
        "type": "coarser",
        "framework": "pri_2010_disclosure",
        "pri_ids": ["E1f_i", "E2f_i"],
        "op": "|",
        "item_text": "Lobbyist Compensation disclosed (Sunlight: -1 no, 0 yes)",
        "note": "Sunlight Compensation: -1 not disclosed, 0 disclosed; PRI splits principal vs lobbyist sides",
    },
]


def build_sunlight_2015() -> None:
    for j in SUNLIGHT_JUDGMENTS:
        sunlight_id = j["sunlight_id"]
        text = j["item_text"]
        ref = {"framework": "sunlight_2015", "item_id": sunlight_id, "item_text": text}

        if j["type"] == "coarser":
            framework = j["framework"]
            pri_ids = j["pri_ids"]
            op = j["op"]
            joined = f" {op} ".join(f"{framework}:{pid}" for pid in pri_ids)
            for pri_id in pri_ids:
                target = _index[(framework, pri_id)]
                if not any(
                    r["framework"] == "sunlight_2015" and r["item_id"] == sunlight_id
                    for r in target.framework_references
                ):
                    target.framework_references.append(ref)
            _index[("sunlight_2015", sunlight_id)] = _index[(framework, pri_ids[0])]
            _dedup.append(
                DedupRow(
                    source_framework="sunlight_2015",
                    source_item_id=sunlight_id,
                    target_expression=joined,
                    notes=j.get("note", ""),
                )
            )

        elif j["type"] == "new":
            comp_row = CompRow(
                id=j["comp_id"],
                name=j["name"],
                description=text.rstrip(".") + ".",
                domain=j["domain"],
                data_type=j["data_type"],
                framework_references=[ref],
                observable_from_database=j["observable"],
            )
            _add(comp_row)
            _dedup.append(
                DedupRow(
                    source_framework="sunlight_2015",
                    source_item_id=sunlight_id,
                    target_expression="NEW",
                    notes=j.get("note", ""),
                )
            )
        else:
            raise ValueError(f"unknown Sunlight judgment type: {j['type']}")


def _focal_indicators_indexed() -> dict[str, dict]:
    with FOCAL.open() as f:
        return {row["indicator_id"]: row for row in csv.DictReader(f)}


def build_focal_2024() -> None:
    indicators = _focal_indicators_indexed()
    for j in FOCAL_JUDGMENTS:
        focal_id = j["focal_id"]
        focal_row = indicators[focal_id]
        text = focal_row["indicator_text"]
        ref = {"framework": "focal_2024", "item_id": focal_id, "item_text": text}

        if j["type"] == "1to1":
            framework = j["framework"]
            pri_id = j["pri_id"]
            target = _index[(framework, pri_id)]
            target.framework_references.append(ref)
            _index[("focal_2024", focal_id)] = target
            _dedup.append(
                DedupRow(
                    source_framework="focal_2024",
                    source_item_id=focal_id,
                    target_expression=f"{framework}:{pri_id}",
                    notes=j.get("note", ""),
                )
            )

        elif j["type"] == "coarser":
            framework = j["framework"]
            pri_ids = j["pri_ids"]
            op = j["op"]  # "&" or "|"
            joined = f" {op} ".join(f"{framework}:{pid}" for pid in pri_ids)
            for pri_id in pri_ids:
                target = _index[(framework, pri_id)]
                if not any(
                    r["framework"] == "focal_2024" and r["item_id"] == focal_id
                    for r in target.framework_references
                ):
                    target.framework_references.append(ref)
            _index[("focal_2024", focal_id)] = _index[(framework, pri_ids[0])]
            _dedup.append(
                DedupRow(
                    source_framework="focal_2024",
                    source_item_id=focal_id,
                    target_expression=joined,
                    notes=j.get("note", ""),
                )
            )

        elif j["type"] == "new":
            comp_row = CompRow(
                id=j["comp_id"],
                name=j["name"],
                description=text.rstrip(".") + ".",
                domain=j["domain"],
                data_type=j["data_type"],
                framework_references=[ref],
                observable_from_database=j["observable"],
            )
            _add(comp_row)
            _dedup.append(
                DedupRow(
                    source_framework="focal_2024",
                    source_item_id=focal_id,
                    target_expression="NEW",
                    notes=j.get("note", ""),
                )
            )
        else:
            raise ValueError(f"unknown FOCAL judgment type: {j['type']}")


def build_pri_disclosure_spine() -> None:
    with PRI_DISCLOSURE.open() as f:
        for row in csv.DictReader(f):
            pri_id = row["item_id"]
            judgment = PRI_DISCLOSURE_JUDGMENTS[pri_id]
            field_path = judgment.get("field_path")
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
                maps_to_state_master_field=field_path,
                maps_to_filing_field=field_path,
                observable_from_database=_observable_from_pri_id(pri_id),
                notes=judgment.get("field_note", ""),
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
    build_focal_2024()
    build_sunlight_2015()
    write_outputs()
    summary = _summary()
    print(f"Wrote {OUT_COMPENDIUM.relative_to(REPO_ROOT)}: {summary['compendium_rows']} rows")
    print(f"Wrote {OUT_DEDUP_MAP.relative_to(REPO_ROOT)}: {summary['dedup_rows']} rows")
    print(f"Framework reference counts: {summary['framework_reference_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

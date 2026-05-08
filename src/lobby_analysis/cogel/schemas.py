"""Hand-curated column schemas for COGEL Blue Book 1990 Tables 28-31.

Each table has a fixed schema transcribed from a multimodal read of one
data page. The schema is the contract between the v1 token TSV and the
per-table CSV outputs in v2.

Tables and source pages:

  Table 28 (Definition / Registration / Prohibitions): scans 159, 160
    Footnote-only continuation: 161, 162.
  Table 29 (Reporting Requirements): scans 163, 164, 165, 166, 167
    Footnote-only continuation: 168.
  Table 30 (Report Filing): scans 169, 170
    Footnote-only continuation: 171.
  Table 31 (Compliance Authority): scans 172, 173, 174, 175, 176, 177
    Footnote-only continuation: 178.

Schemas were transcribed from scans 159, 165, 169, 172 respectively. The
SCAN_TABLE_MAP below records which table each scan belongs to plus a
`is_data` flag distinguishing data pages from footnote-only continuations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ValueKind = Literal["marker", "free_text", "currency", "frequency"]


@dataclass(frozen=True)
class Column:
    """One canonical column in a Blue Book table."""

    key: str
    header_text: str
    value_kind: ValueKind
    header_aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Table:
    name: str
    table_number: int
    scan_pages: tuple[int, ...]
    columns: tuple[Column, ...]
    # Hand-curated inter-cell x boundaries at the v1 extractor's 300 DPI
    # rotated coordinate frame. Length must equal `len(columns) - 1`. These
    # are the primary path; the auto-clustering fallback in grid.py kicks in
    # only if `boundaries` is empty.
    boundaries: tuple[float, ...] = ()

    @property
    def column_count(self) -> int:
        return len(self.columns)

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(c.key for c in self.columns)


# ----- Table 28: Definition, Registration, and Prohibited Activities -----

TABLE_28 = Table(
    name="LOBBYISTS: DEFINITION, REGISTRATION, AND PROHIBITED ACTIVITIES",
    table_number=28,
    scan_pages=(159, 160),
    columns=(
        # Definition of Lobbyist Includes
        Column("def_legislative_parliamentary",
               "Legislative/Parliamentary lobbying", "marker"),
        Column("def_administrative_agency",
               "Administrative agency lobbying", "marker"),
        Column("def_elective_officials_as_lobbyists",
               "Elective officials as lobbyists", "marker"),
        Column("def_public_employees_as_lobbyists",
               "Public employees as lobbyists", "marker"),
        Column("def_compensation_standard", "Compensation standard", "marker"),
        Column("def_expenditure_standard", "Expenditure standard", "marker"),
        Column("def_time_standard", "Time standard", "marker"),
        # Required to Register
        Column("reg_actual_contact_with_state_officials",
               "Those having actual contact with state officials", "marker"),
        Column("reg_employing_individuals_with_actual_contact",
               "Those employing individuals having actual contact", "marker"),
        Column("reg_public_officials_lobbying_in_official_capacity",
               "Public officials lobbying in their official capacity", "marker"),
        Column("reg_other", "Other", "marker"),
        Column("reg_firm_must_register_all_employees",
               "Lobbyist firm has to register all employees in addition to those making actual contact",
               "marker"),
        # Number of Registered During Typical Year
        Column("registered_as_lobbyists", "As Lobbyists", "free_text"),
        Column("registered_as_lobbyist_employees", "As Lobbyist Employees", "free_text"),
        Column("registered_public_agency_lobbyists", "Public agency lobbyists", "free_text"),
        # Registration Fees
        Column("fee_amount", "Amount of fee", "currency"),
        Column("fee_period_covered", "Period Covered", "frequency"),
        # Prohibited Activities Involving Lobbyists
        Column("prohibit_campaign_contribs_any_time",
               "Lobbyists making campaign contributions at any time", "marker"),
        Column("prohibit_campaign_contribs_during_session",
               "Lobbyists making campaign contributions during legislative sessions",
               "marker"),
        Column("prohibit_expenditures_over_threshold",
               "Lobbyists making expenditures in excess of $ per official per year",
               "marker"),
        Column("prohibit_solicitation_for_officials",
               "Solicitation of contributions or gifts for officials or employees by lobbyists",
               "marker"),
        Column("prohibit_other", "Other", "marker"),
        Column("prohibit_contingent_compensation",
               "Lobbying for contingent compensation", "marker"),
    ),
    # Marker centroids on scans 159-160 cluster at uniform ~100 px spacing
    # for the def/prohibit groups and ~80 px for the reg group; non-marker
    # columns 11-16 interpolated within marker-anchored gaps.
    boundaries=(
        628, 728, 828, 928, 1028, 1127,   # def cols 0..6
        1257, 1381, 1465, 1547, 1644,     # reg cols 7..10 + col 11
        1801, 1976, 2131,                 # registered cols 12..14 (numeric)
        2281, 2425,                       # fee amount + period
        2629, 2807, 2907, 3006, 3105, 3205,  # prohibit cols 17..22
    ),
)


# ----- Table 29: Reporting Requirements -----

TABLE_29 = Table(
    name="LOBBYISTS: REPORTING REQUIREMENTS",
    table_number=29,
    scan_pages=(163, 164, 165, 166, 167),
    columns=(
        # Required To File Report
        Column("file_compensated_with_actual_contact",
               "Those Having Actual Contact with State Officials and are Compensated",
               "marker"),
        Column("file_uncompensated_with_actual_contact",
               "Those Having Actual Contact with State Officials and are not Compensated",
               "marker"),
        Column("file_employing_with_actual_contact",
               "Those Employing Individuals Having Actual Contact with State Officials",
               "marker"),
        Column("file_employing_with_contact_over_threshold",
               "Those Employing Individuals Having Actual Contact with State Officials and Spend Over Threshold",
               "marker"),
        Column("file_other", "Other", "marker"),
        # Report Frequency Requirements for
        Column("freq_lobbyist", "Lobbyist", "free_text"),
        Column("freq_lobbyist_employees", "Lobbyist Employees", "free_text"),
        Column("freq_federal_state_public_lobby", "Federal/State Public Lobby", "free_text"),
        # Disclosures Required in Lobbyist Reports
        Column("disclose_legislation_admin_action",
               "Legislation/Administrative Action Seeking to Influence", "marker"),
        Column("disclose_expenditures_benefiting_officials",
               "Expenditures Benefiting Public Officials or Employees", "marker"),
        Column("disclose_compensation_by_employer",
               "Compensation Received (Broken Down by Employer(s))", "marker"),
        Column("disclose_total_compensation", "Total Compensation Received", "marker"),
        Column("disclose_categories_of_expenditures", "Categories of Expenditures", "marker"),
        Column("disclose_total_expenditures", "Total Expenditures", "marker"),
        Column("disclose_contributions_for_lobbying",
               "Contributions Received from Others for Lobbying", "marker"),
        Column("disclose_other", "Other", "marker"),
    ),
    # Boundaries derived from marker clustering on scan 165 + multimodal
    # validation on Missouri (15/16 cells correct on first pass). Cols 5-7
    # (free-text frequency columns) hand-positioned between marker anchors.
    boundaries=(
        719,    # col 0|1  midpt(643, 794)
        881,    # col 1|2  midpt(794, 968)
        1063,   # col 2|3  midpt(968, 1158)
        1240,   # col 3|4  midpt(1158, 1322)
        1420,   # col 4|5  between col-4 marker (~1322) and col-5 free-text start (~1430)
        1650,   # col 5|6  between col-5 free-text end (~1620) and col-6 marker (~1685)
        1830,   # col 6|7  between col-6 marker (~1685) and col-7 free-text start (~1979)
        2100,   # col 7|8  between col-7 free-text end (~2050) and col-8 markers (~2177)
        2261,   # col 8|9  midpt(2177, 2336)
        2410,   # col 9|10 midpt(2336, 2484)
        2559,   # col 10|11 midpt(2484, 2634)
        2708,   # col 11|12 midpt(2634, 2782)
        2857,   # col 12|13 midpt(2782, 2932)
        3007,   # col 13|14 midpt(2932, 3082)
        3156,   # col 14|15 midpt(3082, 3230)
    ),
)


# ----- Table 30: Report Filing -----

TABLE_30 = Table(
    name="LOBBYING: REPORT FILING",
    table_number=30,
    scan_pages=(169, 170),
    columns=(
        # What is the nature of review of filed reports?
        Column("review_desk_all", "Desk Review of All Reports", "marker"),
        Column("review_field_all", "Field Review of All Reports", "marker"),
        Column("review_desk_or_field_all", "Desk or Field Review of All Reports", "marker"),
        Column("review_desk_over_threshold",
               "Desk Review of Reports with Expenditures Exceeding $", "marker"),
        Column("review_field_over_threshold",
               "Field Review of Reports with Expenditures Exceeding $", "marker"),
        Column("review_desk_or_field_over_threshold",
               "Desk or Field Review of Reports with Expenditures Exceeding $", "marker"),
        Column("review_desk_random", "Desk Review of Randomly Selected Reports", "marker"),
        Column("review_field_random", "Field Review of Randomly Selected Reports", "marker"),
        Column("review_desk_or_field_random",
               "Desk or Field Review of Randomly Selected Reports", "marker"),
        Column("review_desk_complaints",
               "Desk Review of Reports about Which Complaints Are Filed", "marker"),
        Column("review_field_complaints",
               "Field Review of Reports about Which Complaints Are Filed", "marker"),
        Column("review_desk_or_field_complaints",
               "Desk or Field Review of Reports about Which Complaints Are Filed",
               "marker"),
        # Standalone numerics
        Column("approx_reports_filed_annually",
               "Approximate Number of Reports Filed Annually?", "free_text"),
        Column("approx_reported_expenditures_prior_year",
               "Approximate Amount of Reported Expenditures in the Previous Calendar Year",
               "currency"),
        # Are Reports Available to the Public?
        Column("public_access_unrestricted", "Yes, on Unrestricted Basis", "marker"),
        Column("public_access_restricted", "Yes, on Restricted Basis", "marker"),
        Column("public_access_not_available", "Not Available", "marker"),
        Column("public_access_agency_compiles_publishes",
               "Agency Compiles & Publishes Lobbyist Data", "marker"),
    ),
    # Marker clustering on scans 169-170 yields 12 evenly-spaced centroids
    # (~149 px) for cols 0-11; cols 12-13 (numeric) interpolated; cols 14-17
    # markers continue. Gap from col 13 to col 14 is wider (~149 px) due to
    # group-section break.
    boundaries=(
        761, 911, 1060, 1209, 1358, 1507, 1657, 1806, 1956, 2105, 2254,  # cols 0..11
        2403, 2552,                                                       # cols 12-13 (interp)
        2701, 2851, 3000, 3149,                                           # cols 14..17
    ),
)


# ----- Table 31: Compliance Authority -----

# Table 31 has a compound row label: jurisdiction + agency name. We carry
# the agency name as its own column so the CSV is wide-uniform with the
# others.

TABLE_31 = Table(
    name="LOBBYING: COMPLIANCE AUTHORITY OF SELECTED AGENCIES",
    table_number=31,
    scan_pages=(172, 173, 174, 175, 176, 177),
    columns=(
        Column("compliance_agency_name", "Agency", "free_text"),
        Column("auth_subpoena_witnesses", "Subpoena Witnesses", "marker"),
        Column("auth_subpoena_records", "Subpoena Records", "marker"),
        Column("auth_conduct_administrative_hearings",
               "Conduct Administrative Hearings", "marker"),
        Column("auth_impose_administrative_fines", "Impose Administrative Fines", "marker"),
        Column("auth_impose_administrative_penalties_amount",
               "Impose Administrative Penalties, Amount $", "currency"),
        Column("auth_file_independent_court_actions",
               "File Independent Court Actions", "marker"),
        Column("auth_request_other_official_mandatory",
               "Request Other Official to Prosecute on Mandatory Basis", "marker"),
        Column("auth_request_other_official_discretionary",
               "Request Other Official to Prosecute on Discretionary Basis", "marker"),
        Column("auth_who_else_can_prosecute",
               "If Agency Cannot Initiate Prosecution for Violations on Its Own Violation, Who Does Have Authority to Prosecute",
               "free_text"),
    ),
    # Marker clustering on Table 31 scans yields 8 evenly-spaced centroids
    # at ~250 px (cols 1-8 = markers + currency); col 0 (agency_name) and
    # col 9 (who_else_can_prosecute) extrapolated by one spacing each.
    boundaries=(
        807, 1056, 1305, 1553, 1800, 2048, 2299, 2548, 2797,
    ),
)


ALL_TABLES: tuple[Table, ...] = (TABLE_28, TABLE_29, TABLE_30, TABLE_31)


# Map every scan page that appears in the corpus to its parent table and
# whether it carries data rows. Footnote-only continuation pages should
# emit no jurisdictions in v1 and produce no CSV rows in v2.
SCAN_TABLE_MAP: dict[int, tuple[int, bool]] = {
    # Table 28
    159: (28, True), 160: (28, True), 161: (28, False), 162: (28, False),
    # Table 29
    163: (29, True), 164: (29, True), 165: (29, True), 166: (29, True),
    167: (29, True), 168: (29, False),
    # Table 30
    169: (30, True), 170: (30, True), 171: (30, False),
    # Table 31
    172: (31, True), 173: (31, True), 174: (31, True), 175: (31, True),
    176: (31, True), 177: (31, True), 178: (31, False),
}


def table_for_scan(scan_page: int) -> Table | None:
    """Return the Table a scan page belongs to, or None if footnote-only."""
    info = SCAN_TABLE_MAP.get(scan_page)
    if info is None:
        return None
    table_num, is_data = info
    if not is_data:
        return None
    for t in ALL_TABLES:
        if t.table_number == table_num:
            return t
    return None

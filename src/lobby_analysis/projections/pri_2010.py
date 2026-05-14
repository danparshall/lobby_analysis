"""PRI 2010 (Disclosure Law + Accessibility) projection.

PRI 2010 publishes two independent per-state scores: disclosure law (max 37)
and accessibility (max 22). Each has a paper-derived rollup rule documented in
``docs/historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md``
and implemented in ``src/scoring/calibration.py`` (line-cited to the paper,
unit-tested at rule level in ``tests/test_calibration.py``). This module wires
v2 compendium cells through PRI-atomic-item helpers to that existing rollup.

Spec doc:
``docs/historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md``

Ground-truth files (sub-aggregate-level, 50 states each):

* ``docs/historical/pri-2026-rescore/results/pri_2010_disclosure_law_scores.csv``
  (5 disclosure-law sub-aggregates per state)
* ``docs/historical/pri-2026-rescore/results/pri_2010_accessibility_scores.csv``
  (8 accessibility sub-components per state)

PRI 2010 did **not** publish per-state per-atomic-item answers — only
sub-aggregate sums. Per-atomic-item helper validation is therefore
fixture-based; per-state end-to-end validation is feasible only for
accessibility (which exposes Q1..Q6 per state + Q7_raw sum + Q8_normalized).
Disclosure-law per-state validation is blocked until the extraction harness
ships per-state cell values (Track B).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from scoring.calibration import (
    AccessibilitySubAggregates,
    DisclosureSubAggregates,
    STATE_NAME_TO_USPS,
    rollup_accessibility,
    rollup_disclosure_law,
)


# ---------------------------------------------------------------------------
# Spec table: PRI atomic item id -> (v2 compendium row id, axis)
#
# Naming-drift correction baked in: spec doc's principal_report_* /
# lobbyist_report_* working names resolve to v2's principal_spending_report_* /
# lobbyist_spending_report_*. E1f_i and E2f_i resolve to multi-rubric shared
# rows (compensation_paid_to_lobbyists / total_compensation respectively).
#
# 7 atomic items the published rollup does not read are skipped per YAGNI:
#   C1, C2, C3 (descriptive sub-criteria of C; paper scores C as 0/1 gate only)
#   D1_present, D1_value, D2_present, D2_value (typed materiality cells;
#       paper scores D as 0/1 gate only)
# ---------------------------------------------------------------------------

# Axis constants
_LEGAL = "legal_availability"
_PRACTICAL = "practical_availability"

# (item_id, v2_row_id, axis)
_DISCLOSURE_SPEC: tuple[tuple[str, str, str], ...] = (
    # A: Who is required to register (11 items)
    ("A1", "actor_paid_lobbyist_registration_required", _LEGAL),
    ("A2", "actor_volunteer_lobbyist_registration_required", _LEGAL),
    ("A3", "actor_principal_registration_required", _LEGAL),
    ("A4", "actor_lobbying_firm_registration_required", _LEGAL),
    ("A5", "actor_governors_office_registration_required", _LEGAL),
    ("A6", "actor_executive_agency_registration_required", _LEGAL),
    ("A7", "actor_legislative_branch_registration_required", _LEGAL),
    ("A8", "actor_independent_agency_registration_required", _LEGAL),
    ("A9", "actor_local_government_registration_required", _LEGAL),
    ("A10", "actor_intergov_agency_lobbying_registration_required", _LEGAL),
    ("A11", "actor_public_entity_other_registration_required", _LEGAL),
    # B: Government exemptions (4 items; B1/B2 reverse-scored in rollup)
    ("B1", "exemption_for_govt_official_capacity_exists", _LEGAL),
    ("B2", "exemption_partial_for_govt_agencies", _LEGAL),
    ("B3", "govt_agencies_subject_to_lobbyist_disclosure_requirements", _LEGAL),
    ("B4", "govt_agencies_subject_to_principal_disclosure_requirements", _LEGAL),
    # C: Public entity definition (gate only)
    ("C0", "law_defines_public_entity", _LEGAL),
    # D: Materiality test (gate only)
    ("D0", "law_includes_materiality_test", _LEGAL),
    # E1: Principal reports (19 items)
    ("E1a", "principal_spending_report_required", _LEGAL),
    ("E1b", "principal_spending_report_includes_principal_contact_info", _LEGAL),
    ("E1c", "principal_spending_report_includes_lobbyist_names", _LEGAL),
    ("E1d", "principal_spending_report_includes_lobbyist_contact_info", _LEGAL),
    ("E1e", "principal_spending_report_includes_business_nature", _LEGAL),
    ("E1f_i", "principal_spending_report_includes_compensation_paid_to_lobbyists", _LEGAL),
    ("E1f_ii", "principal_spending_report_includes_indirect_costs", _LEGAL),
    ("E1f_iii", "principal_spending_report_includes_gifts_entertainment_transport_lodging", _LEGAL),
    ("E1f_iv", "principal_spending_report_uses_itemized_format", _LEGAL),
    ("E1g_i", "principal_spending_report_includes_general_issues", _LEGAL),
    ("E1g_ii", "principal_spending_report_includes_specific_bill_number", _LEGAL),
    ("E1h_i", "principal_spending_report_cadence_includes_monthly", _LEGAL),
    ("E1h_ii", "principal_spending_report_cadence_includes_quarterly", _LEGAL),
    ("E1h_iii", "principal_spending_report_cadence_includes_triannual", _LEGAL),
    ("E1h_iv", "principal_spending_report_cadence_includes_semiannual", _LEGAL),
    ("E1h_v", "principal_spending_report_cadence_includes_annual", _LEGAL),
    ("E1h_vi", "principal_spending_report_cadence_includes_other", _LEGAL),
    ("E1i", "principal_spending_report_includes_contacts_made", _LEGAL),
    ("E1j", "principal_spending_report_includes_major_financial_contributors", _LEGAL),
    # E2: Lobbyist reports (18 items; no E2j)
    ("E2a", "lobbyist_spending_report_required", _LEGAL),
    ("E2b", "lobbyist_spending_report_includes_lobbyist_contact_info", _LEGAL),
    ("E2c", "lobbyist_spending_report_includes_principal_names", _LEGAL),
    ("E2d", "lobbyist_spending_report_includes_principal_contact_info", _LEGAL),
    ("E2e", "lobbyist_spending_report_includes_principal_business_nature", _LEGAL),
    ("E2f_i", "lobbyist_spending_report_includes_total_compensation", _LEGAL),
    ("E2f_ii", "lobbyist_spending_report_includes_indirect_costs", _LEGAL),
    ("E2f_iii", "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging", _LEGAL),
    ("E2f_iv", "lobbyist_spending_report_uses_itemized_format", _LEGAL),
    ("E2g_i", "lobbyist_spending_report_includes_general_issues", _LEGAL),
    ("E2g_ii", "lobbyist_spending_report_includes_specific_bill_number", _LEGAL),
    ("E2h_i", "lobbyist_spending_report_cadence_includes_monthly", _LEGAL),
    ("E2h_ii", "lobbyist_spending_report_cadence_includes_quarterly", _LEGAL),
    ("E2h_iii", "lobbyist_spending_report_cadence_includes_triannual", _LEGAL),
    ("E2h_iv", "lobbyist_spending_report_cadence_includes_semiannual", _LEGAL),
    ("E2h_v", "lobbyist_spending_report_cadence_includes_annual", _LEGAL),
    ("E2h_vi", "lobbyist_spending_report_cadence_includes_other", _LEGAL),
    ("E2i", "lobbyist_spending_report_includes_contacts_made", _LEGAL),
)

_ACCESSIBILITY_SPEC: tuple[tuple[str, str, str], ...] = (
    # Q1..Q6: simple binaries on practical_availability
    ("Q1", "lobbying_data_minimally_available", _PRACTICAL),
    ("Q2", "state_has_dedicated_lobbying_website", _PRACTICAL),
    ("Q3", "lobbying_website_easily_findable", _PRACTICAL),
    ("Q4", "lobbying_data_current_year_present_on_website", _PRACTICAL),
    ("Q5", "lobbying_data_historical_archive_present", _PRACTICAL),
    ("Q6", "lobbying_data_downloadable_in_analytical_format", _PRACTICAL),
    # Q7a..Q7o: 15 search-filter binaries
    ("Q7a", "lobbying_search_filter_by_principal", _PRACTICAL),
    ("Q7b", "lobbying_search_filter_by_principal_location", _PRACTICAL),
    ("Q7c", "lobbying_search_filter_by_lobbyist_name", _PRACTICAL),
    ("Q7d", "lobbying_search_filter_by_lobbyist_location", _PRACTICAL),
    ("Q7e", "lobbying_search_filter_by_specific_date", _PRACTICAL),
    ("Q7f", "lobbying_search_filter_by_time_period", _PRACTICAL),
    ("Q7g", "lobbying_search_filter_by_total_expenditures", _PRACTICAL),
    ("Q7h", "lobbying_search_filter_by_compensation", _PRACTICAL),
    ("Q7i", "lobbying_search_filter_by_misc_expenses", _PRACTICAL),
    ("Q7j", "lobbying_search_filter_by_funding_source", _PRACTICAL),
    ("Q7k", "lobbying_search_filter_by_subject", _PRACTICAL),
    ("Q7l", "lobbying_search_filter_by_assigned_entity", _PRACTICAL),
    ("Q7m", "lobbying_search_filter_by_principal_legal_status", _PRACTICAL),
    ("Q7n", "lobbying_search_filter_by_sector", _PRACTICAL),
    ("Q7o", "lobbying_search_filter_by_subsector", _PRACTICAL),
    # Q8: typed 0..15 passthrough
    ("Q8", "lobbying_search_simultaneous_multicriteria_capability", _PRACTICAL),
)


# Build name-keyed lookup table for fast helper access.
_ATOMIC_SPEC: dict[str, tuple[str, str]] = {
    item_id: (row, axis) for item_id, row, axis in _DISCLOSURE_SPEC + _ACCESSIBILITY_SPEC
}

# Items where the cell value is passed through unchanged (typed, not binary).
# Currently just Q8.
_TYPED_PASSTHROUGH_ITEMS: frozenset[str] = frozenset({"Q8"})

PRI_2010_DISCLOSURE_ATOMIC_IDS: tuple[str, ...] = tuple(t[0] for t in _DISCLOSURE_SPEC)
PRI_2010_ACCESSIBILITY_ATOMIC_IDS: tuple[str, ...] = tuple(t[0] for t in _ACCESSIBILITY_SPEC)


# ---------------------------------------------------------------------------
# Score models
# ---------------------------------------------------------------------------


class PRI2010DisclosureLawScore(BaseModel):
    """A PRI 2010 disclosure-law score for one state.

    Carries the 54 per-atomic-item answers fed to the rollup, the 5 sub-aggregates
    PRI publishes, the total (max 37), and the percent (total / 37 * 100).
    No letter grade — PRI 2010 does not publish one.
    """

    model_config = ConfigDict(frozen=True)

    state: str
    atomic_scores: dict[str, int]
    A_registration: int
    B_gov_exemptions: int
    C_public_entity_def: int
    D_materiality: int
    E_info_disclosed: int
    total: int
    percent: float


class PRI2010AccessibilityScore(BaseModel):
    """A PRI 2010 accessibility score for one state.

    Carries the 22 per-atomic-item answers fed to the rollup, the 8
    sub-components PRI publishes (Q1..Q6 + Q7_raw + Q8_normalized), the total
    (max 22), and the percent (total / 22 * 100).
    """

    model_config = ConfigDict(frozen=True)

    state: str
    atomic_scores: dict[str, int]
    Q1: int
    Q2: int
    Q3: int
    Q4: int
    Q5: int
    Q6: int
    Q7_raw: int
    Q8_normalized: float
    total: float
    percent: float


# ---------------------------------------------------------------------------
# Per-item projection
# ---------------------------------------------------------------------------


def project_pri_atomic_item(item_id: str, cells: dict[str, Any]) -> int:
    """Project one PRI 2010 atomic item from v2 compendium cells.

    For binary atomic items (75 of 76), returns 0 or 1 — 1 iff the spec'd
    cell on the spec'd axis is truthy. For Q8 (typed 0..15), returns the
    raw cell value unchanged (rollup divides by 15 to produce Q8_normalized).
    Missing cells project to 0.

    Raises KeyError if item_id is not a known PRI 2010 atomic item.
    """
    row, axis = _ATOMIC_SPEC[item_id]  # KeyError if unknown
    cell = cells.get(row) or {}
    value = cell.get(axis)
    if item_id in _TYPED_PASSTHROUGH_ITEMS:
        if value is None:
            return 0
        return int(value)
    return 1 if value else 0


def project_pri_atomic_items(cells: dict[str, Any]) -> dict[str, int]:
    """Project all 76 PRI 2010 atomic items from v2 compendium cells.

    Returns a dict keyed by PRI atomic item id (A1..A11, B1..B4, C0, D0,
    E1a..E1j, E2a..E2i, Q1..Q6, Q7a..Q7o, Q8). The disclosure-law and
    accessibility halves can be fed to scoring.calibration.rollup_*
    directly.
    """
    return {item_id: project_pri_atomic_item(item_id, cells) for item_id in _ATOMIC_SPEC}


# ---------------------------------------------------------------------------
# Top-level projections
# ---------------------------------------------------------------------------


_DISCLOSURE_LAW_MAX = 37  # 11 (A) + 4 (B) + 1 (C) + 1 (D) + 20 (E) per Table 5
_ACCESSIBILITY_MAX = 22  # 1+1+1+1+1+1 + 15 + 1 per paper §IV


def project_pri_2010_disclosure_law(cells: dict[str, Any], state: str) -> PRI2010DisclosureLawScore:
    """Top-level: v2 cells -> per-atomic-item answers -> calibration rollup -> score."""
    atomic = {
        item_id: project_pri_atomic_item(item_id, cells)
        for item_id in PRI_2010_DISCLOSURE_ATOMIC_IDS
    }
    sub: DisclosureSubAggregates = rollup_disclosure_law(atomic)
    # The rollup returns Optional[int]s for null-propagation, but our atomic
    # dict is dense (every helper produces a concrete 0/1), so sub fields are
    # never None here. We assert to keep the type narrow for the score model.
    assert sub.A_registration is not None
    assert sub.B_gov_exemptions is not None
    assert sub.C_public_entity_def is not None
    assert sub.D_materiality is not None
    assert sub.E_info_disclosed is not None
    assert sub.total is not None
    return PRI2010DisclosureLawScore(
        state=state,
        atomic_scores=atomic,
        A_registration=sub.A_registration,
        B_gov_exemptions=sub.B_gov_exemptions,
        C_public_entity_def=sub.C_public_entity_def,
        D_materiality=sub.D_materiality,
        E_info_disclosed=sub.E_info_disclosed,
        total=sub.total,
        percent=sub.total / _DISCLOSURE_LAW_MAX * 100,
    )


def project_pri_2010_accessibility(cells: dict[str, Any], state: str) -> PRI2010AccessibilityScore:
    """Top-level: v2 cells -> per-atomic-item answers -> calibration rollup -> score."""
    atomic = {
        item_id: project_pri_atomic_item(item_id, cells)
        for item_id in PRI_2010_ACCESSIBILITY_ATOMIC_IDS
    }
    sub: AccessibilitySubAggregates = rollup_accessibility(atomic)
    assert sub.Q1 is not None
    assert sub.Q2 is not None
    assert sub.Q3 is not None
    assert sub.Q4 is not None
    assert sub.Q5 is not None
    assert sub.Q6 is not None
    assert sub.Q7_raw is not None
    assert sub.Q8_normalized is not None
    assert sub.total is not None
    return PRI2010AccessibilityScore(
        state=state,
        atomic_scores=atomic,
        Q1=sub.Q1,
        Q2=sub.Q2,
        Q3=sub.Q3,
        Q4=sub.Q4,
        Q5=sub.Q5,
        Q6=sub.Q6,
        Q7_raw=sub.Q7_raw,
        Q8_normalized=sub.Q8_normalized,
        total=sub.total,
        percent=sub.total / _ACCESSIBILITY_MAX * 100,
    )


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def rank_pri_2010_states(scores: dict[str, float]) -> dict[str, int]:
    """Return a {state: rank} mapping where higher score -> lower rank.

    Uses competition (1224) ranking: tied states share the same rank, the
    next rank skips the corresponding count. PRI's published per-state
    rank column uses this convention (verified: Alabama and Colorado both
    have disclosure-law total 19 and share rank 36).
    """
    ordered = sorted(scores.items(), key=lambda kv: -kv[1])
    out: dict[str, int] = {}
    prev_score: float | None = None
    prev_rank = 0
    for i, (state, score) in enumerate(ordered, start=1):
        if prev_score is None or score != prev_score:
            prev_rank = i
            prev_score = score
        out[state] = prev_rank
    return out


# ---------------------------------------------------------------------------
# Ground-truth loaders (re-exports of scoring.calibration loaders, but
# returning the same Pydantic types under the projections namespace)
# ---------------------------------------------------------------------------


def _disclosure_scores_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "docs"
        / "historical"
        / "pri-2026-rescore"
        / "results"
        / "pri_2010_disclosure_law_scores.csv"
    )


def _accessibility_scores_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "docs"
        / "historical"
        / "pri-2026-rescore"
        / "results"
        / "pri_2010_accessibility_scores.csv"
    )


def load_pri_2010_disclosure_law_reference(
    repo_root: Path,
) -> dict[str, DisclosureSubAggregates]:
    """Load published 50-state disclosure-law sub-aggregates as a USPS-keyed dict."""
    out: dict[str, DisclosureSubAggregates] = {}
    with _disclosure_scores_path(repo_root).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            usps = STATE_NAME_TO_USPS[row["state"]]
            out[usps] = DisclosureSubAggregates(
                A_registration=int(row["A_registration"]),
                B_gov_exemptions=int(row["B_gov_exemptions"]),
                C_public_entity_def=int(row["C_public_entity_def"]),
                D_materiality=int(row["D_materiality"]),
                E_info_disclosed=int(row["E_info_disclosed"]),
                total=int(row["total_2010"]),
            )
    return out


def load_pri_2010_accessibility_reference(
    repo_root: Path,
) -> dict[str, AccessibilitySubAggregates]:
    """Load published 50-state accessibility sub-components as a USPS-keyed dict."""
    out: dict[str, AccessibilitySubAggregates] = {}
    with _accessibility_scores_path(repo_root).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            usps = STATE_NAME_TO_USPS[row["state"]]
            out[usps] = AccessibilitySubAggregates(
                Q1=int(row["Q1"]),
                Q2=int(row["Q2"]),
                Q3=int(row["Q3"]),
                Q4=int(row["Q4"]),
                Q5=int(row["Q5"]),
                Q6=int(row["Q6"]),
                Q7_raw=int(float(row["Q7_raw"])),
                Q8_normalized=float(row["Q8_normalized"]),
                total=float(row["total_2010"]),
            )
    return out

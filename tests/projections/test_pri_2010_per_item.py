"""Per-atomic-item projection tests for PRI 2010.

PRI 2010 publishes sub-aggregate ground truth only (50 states x 5 disclosure-law
sub-aggregates + 50 states x 8 accessibility sub-components). Per-atomic-item
ground truth was never released. These fixture tests pin the per-item helper
behavior directly: for each PRI atomic item (A1..A11, B1..B4, C0, D0, E1a..E1j,
E2a..E2i, Q1..Q6, Q7a..Q7o, Q8), the projection reads a single v2 compendium
cell on a specific axis and returns 0/1 (or 0..15 for Q8).

The spec-doc-to-v2-row mapping carries one naming-drift correction: the
projection spec (written pre-promote) uses ``principal_report_*`` /
``lobbyist_report_*``; the v2 TSV uses ``principal_spending_report_*`` /
``lobbyist_spending_report_*``. Two specific rows are cross-rubric shared:
E1f_i resolves to ``principal_spending_report_includes_compensation_paid_to_lobbyists``
(same row CPI #203 reads) and E2f_i resolves to
``lobbyist_spending_report_includes_total_compensation`` (a multi-rubric row).
"""

from __future__ import annotations

import pytest

from lobby_analysis.projections.pri_2010 import (
    PRI_2010_ACCESSIBILITY_ATOMIC_IDS,
    PRI_2010_DISCLOSURE_ATOMIC_IDS,
    project_pri_atomic_item,
    project_pri_atomic_items,
)


# ---------------------------------------------------------------------------
# Spec table: (PRI atomic item id, v2 compendium row id, axis)
#
# This table is the *test*'s source of truth — independent of the
# implementation's own mapping. Both must agree for tests to pass.
# Row names verified to be present in compendium/disclosure_side_compendium_items_v2.tsv
# on 2026-05-14 (76 of 76 expected rows resolved).
# ---------------------------------------------------------------------------


_DISCLOSURE_SPEC: tuple[tuple[str, str, str], ...] = (
    # A: Who is required to register (11 items, legal_availability)
    ("A1", "actor_paid_lobbyist_registration_required", "legal_availability"),
    ("A2", "actor_volunteer_lobbyist_registration_required", "legal_availability"),
    ("A3", "actor_principal_registration_required", "legal_availability"),
    ("A4", "actor_lobbying_firm_registration_required", "legal_availability"),
    ("A5", "actor_governors_office_registration_required", "legal_availability"),
    ("A6", "actor_executive_agency_registration_required", "legal_availability"),
    ("A7", "actor_legislative_branch_registration_required", "legal_availability"),
    ("A8", "actor_independent_agency_registration_required", "legal_availability"),
    ("A9", "actor_local_government_registration_required", "legal_availability"),
    ("A10", "actor_intergov_agency_lobbying_registration_required", "legal_availability"),
    ("A11", "actor_public_entity_other_registration_required", "legal_availability"),
    # B: Government exemptions (4 items, legal_availability)
    # B1/B2 are reverse-scored *in the rollup*, NOT in the per-item projection.
    # The per-item helper returns the literal 0/1 answer to the rubric question;
    # rollup_disclosure_law applies (1 - B1) + (1 - B2) per the paper.
    ("B1", "exemption_for_govt_official_capacity_exists", "legal_availability"),
    ("B2", "exemption_partial_for_govt_agencies", "legal_availability"),
    ("B3", "govt_agencies_subject_to_lobbyist_disclosure_requirements", "legal_availability"),
    ("B4", "govt_agencies_subject_to_principal_disclosure_requirements", "legal_availability"),
    # C: Definition of public entity (1 item read by rollup; C1-C3 unread, skipped)
    ("C0", "law_defines_public_entity", "legal_availability"),
    # D: Materiality test (1 item read by rollup; D1/D2 typed cells unread, skipped)
    ("D0", "law_includes_materiality_test", "legal_availability"),
    # E1: Principal reports (19 items, legal_availability)
    ("E1a", "principal_spending_report_required", "legal_availability"),
    ("E1b", "principal_spending_report_includes_principal_contact_info", "legal_availability"),
    ("E1c", "principal_spending_report_includes_lobbyist_names", "legal_availability"),
    ("E1d", "principal_spending_report_includes_lobbyist_contact_info", "legal_availability"),
    ("E1e", "principal_spending_report_includes_business_nature", "legal_availability"),
    (
        "E1f_i",
        "principal_spending_report_includes_compensation_paid_to_lobbyists",
        "legal_availability",
    ),
    ("E1f_ii", "principal_spending_report_includes_indirect_costs", "legal_availability"),
    (
        "E1f_iii",
        "principal_spending_report_includes_gifts_entertainment_transport_lodging",
        "legal_availability",
    ),
    ("E1f_iv", "principal_spending_report_uses_itemized_format", "legal_availability"),
    ("E1g_i", "principal_spending_report_includes_general_issues", "legal_availability"),
    ("E1g_ii", "principal_spending_report_includes_specific_bill_number", "legal_availability"),
    ("E1h_i", "principal_spending_report_cadence_includes_monthly", "legal_availability"),
    ("E1h_ii", "principal_spending_report_cadence_includes_quarterly", "legal_availability"),
    ("E1h_iii", "principal_spending_report_cadence_includes_triannual", "legal_availability"),
    ("E1h_iv", "principal_spending_report_cadence_includes_semiannual", "legal_availability"),
    ("E1h_v", "principal_spending_report_cadence_includes_annual", "legal_availability"),
    ("E1h_vi", "principal_spending_report_cadence_includes_other", "legal_availability"),
    ("E1i", "principal_spending_report_includes_contacts_made", "legal_availability"),
    (
        "E1j",
        "principal_spending_report_includes_major_financial_contributors",
        "legal_availability",
    ),
    # E2: Lobbyist reports (18 items, legal_availability — no E2j)
    ("E2a", "lobbyist_spending_report_required", "legal_availability"),
    ("E2b", "lobbyist_spending_report_includes_lobbyist_contact_info", "legal_availability"),
    ("E2c", "lobbyist_spending_report_includes_principal_names", "legal_availability"),
    ("E2d", "lobbyist_spending_report_includes_principal_contact_info", "legal_availability"),
    ("E2e", "lobbyist_spending_report_includes_principal_business_nature", "legal_availability"),
    ("E2f_i", "lobbyist_spending_report_includes_total_compensation", "legal_availability"),
    ("E2f_ii", "lobbyist_spending_report_includes_indirect_costs", "legal_availability"),
    (
        "E2f_iii",
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
        "legal_availability",
    ),
    ("E2f_iv", "lobbyist_spending_report_uses_itemized_format", "legal_availability"),
    ("E2g_i", "lobbyist_spending_report_includes_general_issues", "legal_availability"),
    ("E2g_ii", "lobbyist_spending_report_includes_specific_bill_number", "legal_availability"),
    ("E2h_i", "lobbyist_spending_report_cadence_includes_monthly", "legal_availability"),
    ("E2h_ii", "lobbyist_spending_report_cadence_includes_quarterly", "legal_availability"),
    ("E2h_iii", "lobbyist_spending_report_cadence_includes_triannual", "legal_availability"),
    ("E2h_iv", "lobbyist_spending_report_cadence_includes_semiannual", "legal_availability"),
    ("E2h_v", "lobbyist_spending_report_cadence_includes_annual", "legal_availability"),
    ("E2h_vi", "lobbyist_spending_report_cadence_includes_other", "legal_availability"),
    ("E2i", "lobbyist_spending_report_includes_contacts_made", "legal_availability"),
)


_ACCESSIBILITY_SPEC: tuple[tuple[str, str, str], ...] = (
    # Q1..Q6 binaries, all practical_availability
    ("Q1", "lobbying_data_minimally_available", "practical_availability"),
    ("Q2", "state_has_dedicated_lobbying_website", "practical_availability"),
    ("Q3", "lobbying_website_easily_findable", "practical_availability"),
    ("Q4", "lobbying_data_current_year_present_on_website", "practical_availability"),
    ("Q5", "lobbying_data_historical_archive_present", "practical_availability"),
    ("Q6", "lobbying_data_downloadable_in_analytical_format", "practical_availability"),
    # Q7a..Q7o: 15 search-filter binaries
    ("Q7a", "lobbying_search_filter_by_principal", "practical_availability"),
    ("Q7b", "lobbying_search_filter_by_principal_location", "practical_availability"),
    ("Q7c", "lobbying_search_filter_by_lobbyist_name", "practical_availability"),
    ("Q7d", "lobbying_search_filter_by_lobbyist_location", "practical_availability"),
    ("Q7e", "lobbying_search_filter_by_specific_date", "practical_availability"),
    ("Q7f", "lobbying_search_filter_by_time_period", "practical_availability"),
    ("Q7g", "lobbying_search_filter_by_total_expenditures", "practical_availability"),
    ("Q7h", "lobbying_search_filter_by_compensation", "practical_availability"),
    ("Q7i", "lobbying_search_filter_by_misc_expenses", "practical_availability"),
    ("Q7j", "lobbying_search_filter_by_funding_source", "practical_availability"),
    ("Q7k", "lobbying_search_filter_by_subject", "practical_availability"),
    ("Q7l", "lobbying_search_filter_by_assigned_entity", "practical_availability"),
    ("Q7m", "lobbying_search_filter_by_principal_legal_status", "practical_availability"),
    ("Q7n", "lobbying_search_filter_by_sector", "practical_availability"),
    ("Q7o", "lobbying_search_filter_by_subsector", "practical_availability"),
    # Q8: typed 0..15 passthrough, practical_availability
    ("Q8", "lobbying_search_simultaneous_multicriteria_capability", "practical_availability"),
)


_BINARY_SPEC = _DISCLOSURE_SPEC + tuple(t for t in _ACCESSIBILITY_SPEC if t[0] != "Q8")
_Q8_ROW = "lobbying_search_simultaneous_multicriteria_capability"


# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------


def test_disclosure_atomic_ids_count_is_54():
    """11 A + 4 B + 1 C0 + 1 D0 + 19 E1 + 18 E2 = 54 atomic items projected.

    7 PRI atomic items that the published rollup does not read (C1, C2, C3,
    D1_present, D1_value, D2_present, D2_value) are skipped per YAGNI.
    """
    assert len(PRI_2010_DISCLOSURE_ATOMIC_IDS) == 54


def test_accessibility_atomic_ids_count_is_22():
    """Q1..Q6 (6) + Q7a..Q7o (15) + Q8 (1) = 22 atomic items projected."""
    assert len(PRI_2010_ACCESSIBILITY_ATOMIC_IDS) == 22


# ---------------------------------------------------------------------------
# Binary atomic items: True / False / missing -> 1 / 0 / 0
# 75 binary items x 3 cases = 225 parameterized tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("item_id, v2_row, axis", _BINARY_SPEC, ids=[s[0] for s in _BINARY_SPEC])
def test_binary_atomic_item_true_projects_to_one(item_id, v2_row, axis):
    cells = {v2_row: {axis: True}}
    assert project_pri_atomic_item(item_id, cells) == 1


@pytest.mark.parametrize("item_id, v2_row, axis", _BINARY_SPEC, ids=[s[0] for s in _BINARY_SPEC])
def test_binary_atomic_item_false_projects_to_zero(item_id, v2_row, axis):
    cells = {v2_row: {axis: False}}
    assert project_pri_atomic_item(item_id, cells) == 0


@pytest.mark.parametrize("item_id, v2_row, axis", _BINARY_SPEC, ids=[s[0] for s in _BINARY_SPEC])
def test_binary_atomic_item_missing_cell_projects_to_zero(item_id, v2_row, axis):
    """A missing compendium cell is read as 0 (NO), consistent with the
    CPI module's de jure normalization (anything-not-YES/MOD/NO -> NO).
    Justification: in PRI's 0/1 universe, absence of an affirmative statutory
    provision is a negative answer."""
    assert project_pri_atomic_item(item_id, {}) == 0


# ---------------------------------------------------------------------------
# Q8: typed 0..15 passthrough
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("q8_value", list(range(16)))
def test_q8_passes_through_unchanged(q8_value):
    """Q8 is the only non-binary PRI atomic item. PRI 2010 scored it as a
    holistic 0..15 ordinal (paper §IV); the rollup divides by 15 to produce
    Q8_normalized in [0, 1]. The per-item projection returns the raw 0..15
    value untouched; the rollup does the normalization."""
    cells = {_Q8_ROW: {"practical_availability": q8_value}}
    assert project_pri_atomic_item("Q8", cells) == q8_value


def test_q8_missing_cell_projects_to_zero():
    assert project_pri_atomic_item("Q8", {}) == 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unknown_item_id_raises():
    with pytest.raises(KeyError):
        project_pri_atomic_item("not_a_real_item", {})


# ---------------------------------------------------------------------------
# Batch helper: project_pri_atomic_items returns all 76 items at once
# ---------------------------------------------------------------------------


def test_project_pri_atomic_items_returns_all_76_items():
    """project_pri_atomic_items(cells) projects every PRI 2010 atomic item
    (54 disclosure-law + 22 accessibility = 76) in one pass, returning a
    dict keyed by PRI atomic item id. Used by the top-level
    project_pri_2010_disclosure_law / accessibility functions before passing
    to the rollup."""
    result = project_pri_atomic_items({})
    assert len(result) == 76
    assert set(result) == set(PRI_2010_DISCLOSURE_ATOMIC_IDS) | set(
        PRI_2010_ACCESSIBILITY_ATOMIC_IDS
    )
    # All values should be 0 (no cells -> no positive answers)
    assert all(v == 0 for v in result.values())


def test_project_pri_atomic_items_a_series_round_trip():
    """Setting cells for all 11 A-series rows to True should yield A1..A11 = 1
    in the returned dict (and 0 for everything else)."""
    cells = {
        row: {axis: True} for item_id, row, axis in _DISCLOSURE_SPEC if item_id.startswith("A")
    }
    result = project_pri_atomic_items(cells)
    a_keys = [f"A{i}" for i in range(1, 12)]
    for k in a_keys:
        assert result[k] == 1, f"expected A-series {k}=1, got {result[k]}"
    # Spot-check that non-A items remain 0
    assert result["B1"] == 0
    assert result["E1a"] == 0
    assert result["Q1"] == 0

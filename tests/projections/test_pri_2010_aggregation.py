"""End-to-end and aggregation tests for PRI 2010 projection.

Validation strategy (per session brief): rule-based.

The PRI 2010 rollup is already exhaustively tested at rule level in
``tests/test_calibration.py`` (B1/B2 reverse-scoring, E "higher of E1/E2 +
F/G double-count + separate J", h-frequency collapse, max arithmetic per
Table 5, etc. — all line-cited to the paper). This file does NOT re-test
those rules; instead it pins the *wiring* between

  cells -> per-item helpers -> calibration rollup -> Score model

and exercises the wiring on real ground-truth shapes for accessibility
(which has per-atomic-item ground truth for Q1..Q6 + Q7_raw sum + Q8
normalized — enough for an honest 50-state round-trip).

Disclosure-law per-state validation is NOT included: PRI 2010 publishes only
sub-aggregates (A/B/C/D/E_info_disclosed), not per-atomic-item answers, so the
projection layer cannot be fully end-to-end-validated until the extraction
harness ships per-state cell values. Wiring tests below use hand-crafted
disclosure-law fixtures that exercise every code path (A sum, B reverse-score,
C0 gate, D0 gate, E max(base) + fg double-count + E1j separate).

Tolerance per session brief: +/- 1 on every published per-state aggregate.
"""

from __future__ import annotations

from pathlib import Path

from lobby_analysis.projections.pri_2010 import (
    PRI2010AccessibilityScore,
    PRI2010DisclosureLawScore,
    load_pri_2010_accessibility_reference,
    load_pri_2010_disclosure_law_reference,
    project_pri_2010_accessibility,
    project_pri_2010_disclosure_law,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cells_for_accessibility_state(
    q1: int,
    q2: int,
    q3: int,
    q4: int,
    q5: int,
    q6: int,
    q7_raw: int,
    q8_raw: int,
) -> dict[str, dict[str, object]]:
    """Build a cells dict that projects to the given accessibility atomic items.

    Q1..Q6 are direct binary cells. Q7_raw is a sum of 15 binaries; we
    distribute by setting the first ``q7_raw`` of Q7a..Q7o to True. Q8 is
    a typed 0..15 cell.
    """
    q7_keys_v2 = [
        "lobbying_search_filter_by_principal",
        "lobbying_search_filter_by_principal_location",
        "lobbying_search_filter_by_lobbyist_name",
        "lobbying_search_filter_by_lobbyist_location",
        "lobbying_search_filter_by_specific_date",
        "lobbying_search_filter_by_time_period",
        "lobbying_search_filter_by_total_expenditures",
        "lobbying_search_filter_by_compensation",
        "lobbying_search_filter_by_misc_expenses",
        "lobbying_search_filter_by_funding_source",
        "lobbying_search_filter_by_subject",
        "lobbying_search_filter_by_assigned_entity",
        "lobbying_search_filter_by_principal_legal_status",
        "lobbying_search_filter_by_sector",
        "lobbying_search_filter_by_subsector",
    ]
    cells: dict[str, dict[str, object]] = {
        "lobbying_data_minimally_available": {"practical_availability": bool(q1)},
        "state_has_dedicated_lobbying_website": {"practical_availability": bool(q2)},
        "lobbying_website_easily_findable": {"practical_availability": bool(q3)},
        "lobbying_data_current_year_present_on_website": {"practical_availability": bool(q4)},
        "lobbying_data_historical_archive_present": {"practical_availability": bool(q5)},
        "lobbying_data_downloadable_in_analytical_format": {"practical_availability": bool(q6)},
        "lobbying_search_simultaneous_multicriteria_capability": {"practical_availability": q8_raw},
    }
    for i, key in enumerate(q7_keys_v2):
        cells[key] = {"practical_availability": i < q7_raw}
    return cells


# ---------------------------------------------------------------------------
# Accessibility end-to-end: 50-state round-trip
# ---------------------------------------------------------------------------


def test_accessibility_50_state_round_trip_within_tolerance():
    """For each of 50 published states, build a cells dict from the published
    Q1..Q6 binaries + Q7_raw sum + Q8_normalized (recovered as Q8_raw =
    round(Q8_normalized * 15)). Project through and verify the resulting
    total matches the published total within tolerance.

    Tolerance:
    - Q1..Q6 should match exactly (direct passthrough).
    - Q7_raw should match exactly (sum reproducible).
    - Q8_normalized may differ by up to ~1/30 (rounding of Q8_raw to int).
      PRI publishes Q8_normalized to 1dp; recovering Q8_raw introduces at
      most 0.5/15 = 0.033 error per state.
    - total may therefore differ by up to ~0.05 (Q8 error + 1dp rounding).
    """
    references = load_pri_2010_accessibility_reference(REPO_ROOT)
    failures = []
    for state, ref in references.items():
        q8_raw = round(ref.Q8_normalized * 15)
        cells = _cells_for_accessibility_state(
            ref.Q1,
            ref.Q2,
            ref.Q3,
            ref.Q4,
            ref.Q5,
            ref.Q6,
            ref.Q7_raw,
            q8_raw,
        )
        score = project_pri_2010_accessibility(cells, state)
        # Sub-component agreement
        if (
            score.Q1 != ref.Q1
            or score.Q2 != ref.Q2
            or score.Q3 != ref.Q3
            or score.Q4 != ref.Q4
            or score.Q5 != ref.Q5
            or score.Q6 != ref.Q6
            or score.Q7_raw != ref.Q7_raw
        ):
            failures.append((state, "sub-component", score, ref))
            continue
        # Total within tolerance (1.0 per session-brief spec)
        if abs(score.total - ref.total) > 1.0:
            failures.append((state, "total", score.total, ref.total))
    assert failures == [], f"accessibility round-trip failures: {failures}"


def test_accessibility_returns_typed_score_model():
    """project_pri_2010_accessibility returns a PRI2010AccessibilityScore."""
    cells = _cells_for_accessibility_state(1, 1, 1, 1, 0, 0, 3, 1)
    score = project_pri_2010_accessibility(cells, "AL")
    assert isinstance(score, PRI2010AccessibilityScore)
    assert score.state == "AL"
    # Q7_raw should match the input
    assert score.Q7_raw == 3


# ---------------------------------------------------------------------------
# Disclosure-law wiring tests (hand-crafted to exercise each code path)
# ---------------------------------------------------------------------------


_A_ROWS = [
    "actor_paid_lobbyist_registration_required",
    "actor_volunteer_lobbyist_registration_required",
    "actor_principal_registration_required",
    "actor_lobbying_firm_registration_required",
    "actor_governors_office_registration_required",
    "actor_executive_agency_registration_required",
    "actor_legislative_branch_registration_required",
    "actor_independent_agency_registration_required",
    "actor_local_government_registration_required",
    "actor_intergov_agency_lobbying_registration_required",
    "actor_public_entity_other_registration_required",
]


def test_disclosure_law_a_full_sums_to_11():
    """A_registration is a simple sum of A1..A11 (rollup_disclosure_law)."""
    cells: dict[str, dict[str, object]] = {row: {"legal_availability": True} for row in _A_ROWS}
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.A_registration == 11


def test_disclosure_law_a_partial_sums():
    """A_registration counts only the True ones."""
    cells: dict[str, dict[str, object]] = {
        _A_ROWS[0]: {"legal_availability": True},  # A1
        _A_ROWS[4]: {"legal_availability": True},  # A5
        _A_ROWS[10]: {"legal_availability": True},  # A11
    }
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.A_registration == 3


def test_disclosure_law_b_reverse_scores_b1_b2():
    """B1/B2 'No' (False, 0) contribute 1 each via the (1 - B) reverse-score
    in the rollup; B3/B4 'Yes' (True, 1) contribute 1 each directly.
    """
    cells: dict[str, dict[str, object]] = {
        "exemption_for_govt_official_capacity_exists": {"legal_availability": False},  # B1=0 -> +1
        "exemption_partial_for_govt_agencies": {"legal_availability": False},  # B2=0 -> +1
        "govt_agencies_subject_to_lobbyist_disclosure_requirements": {
            "legal_availability": True
        },  # B3=1 -> +1
        "govt_agencies_subject_to_principal_disclosure_requirements": {
            "legal_availability": True
        },  # B4=1 -> +1
    }
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.B_gov_exemptions == 4


def test_disclosure_law_b_all_yes_yields_two():
    """All four B items 'Yes': B1/B2 contribute 0 each (reverse-scored), B3/B4
    contribute 1 each. Total = 2.
    """
    cells: dict[str, dict[str, object]] = {
        "exemption_for_govt_official_capacity_exists": {"legal_availability": True},  # B1=1 -> 0
        "exemption_partial_for_govt_agencies": {"legal_availability": True},  # B2=1 -> 0
        "govt_agencies_subject_to_lobbyist_disclosure_requirements": {
            "legal_availability": True
        },  # B3=1 -> +1
        "govt_agencies_subject_to_principal_disclosure_requirements": {
            "legal_availability": True
        },  # B4=1 -> +1
    }
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.B_gov_exemptions == 2


def test_disclosure_law_c0_d0_gates():
    cells: dict[str, dict[str, object]] = {
        "law_defines_public_entity": {"legal_availability": True},
        "law_includes_materiality_test": {"legal_availability": False},
    }
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.C_public_entity_def == 1
    assert score.D_materiality == 0


def test_disclosure_law_e_higher_of_e1_e2_and_fg_double_count_and_e1j_independent():
    """Exercise the full E rollup rule.

    E1 side: a=1, b=1, c=0, d=0, e=0, h_i=1, i=0  -> base_e1 = 3
             f_i=1, f_ii=0, f_iii=0, f_iv=0, g_i=1, g_ii=0  -> fg_e1 = 2
    E2 side: a=1, b=1, c=1, d=1, e=1, h_i=0, h_ii=1, i=1  -> base_e2 = 7
             f_i=0, f_ii=0, f_iii=1, f_iv=1, g_i=0, g_ii=1  -> fg_e2 = 3
    E1j = 1

    E_info_disclosed = max(3, 7) + 2 + 3 + 1 = 13.
    """
    cells: dict[str, dict[str, object]] = {
        # E1 side
        "principal_spending_report_required": {"legal_availability": True},  # E1a=1
        "principal_spending_report_includes_principal_contact_info": {
            "legal_availability": True
        },  # E1b=1
        "principal_spending_report_includes_lobbyist_names": {"legal_availability": False},  # E1c=0
        "principal_spending_report_includes_lobbyist_contact_info": {
            "legal_availability": False
        },  # E1d=0
        "principal_spending_report_includes_business_nature": {
            "legal_availability": False
        },  # E1e=0
        "principal_spending_report_cadence_includes_monthly": {
            "legal_availability": True
        },  # E1h_i=1
        "principal_spending_report_cadence_includes_quarterly": {
            "legal_availability": False
        },  # E1h_ii=0
        "principal_spending_report_cadence_includes_triannual": {
            "legal_availability": False
        },  # E1h_iii=0
        "principal_spending_report_includes_contacts_made": {"legal_availability": False},  # E1i=0
        "principal_spending_report_includes_compensation_paid_to_lobbyists": {
            "legal_availability": True
        },  # E1f_i=1
        "principal_spending_report_includes_indirect_costs": {
            "legal_availability": False
        },  # E1f_ii=0
        "principal_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": False
        },  # E1f_iii=0
        "principal_spending_report_uses_itemized_format": {"legal_availability": False},  # E1f_iv=0
        "principal_spending_report_includes_general_issues": {
            "legal_availability": True
        },  # E1g_i=1
        "principal_spending_report_includes_specific_bill_number": {
            "legal_availability": False
        },  # E1g_ii=0
        "principal_spending_report_includes_major_financial_contributors": {
            "legal_availability": True
        },  # E1j=1
        # E2 side
        "lobbyist_spending_report_required": {"legal_availability": True},  # E2a=1
        "lobbyist_spending_report_includes_lobbyist_contact_info": {
            "legal_availability": True
        },  # E2b=1
        "lobbyist_spending_report_includes_principal_names": {"legal_availability": True},  # E2c=1
        "lobbyist_spending_report_includes_principal_contact_info": {
            "legal_availability": True
        },  # E2d=1
        "lobbyist_spending_report_includes_principal_business_nature": {
            "legal_availability": True
        },  # E2e=1
        "lobbyist_spending_report_cadence_includes_monthly": {
            "legal_availability": False
        },  # E2h_i=0
        "lobbyist_spending_report_cadence_includes_quarterly": {
            "legal_availability": True
        },  # E2h_ii=1
        "lobbyist_spending_report_cadence_includes_triannual": {
            "legal_availability": False
        },  # E2h_iii=0
        "lobbyist_spending_report_includes_contacts_made": {"legal_availability": True},  # E2i=1
        "lobbyist_spending_report_includes_total_compensation": {
            "legal_availability": False
        },  # E2f_i=0
        "lobbyist_spending_report_includes_indirect_costs": {
            "legal_availability": False
        },  # E2f_ii=0
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": True
        },  # E2f_iii=1
        "lobbyist_spending_report_uses_itemized_format": {"legal_availability": True},  # E2f_iv=1
        "lobbyist_spending_report_includes_general_issues": {
            "legal_availability": False
        },  # E2g_i=0
        "lobbyist_spending_report_includes_specific_bill_number": {
            "legal_availability": True
        },  # E2g_ii=1
    }
    score = project_pri_2010_disclosure_law(cells, "TEST")
    # max(3, 7) + 2 + 3 + 1 = 13
    assert score.E_info_disclosed == 13


def test_disclosure_law_total_sums_sub_aggregates():
    """total = A + B + C + D + E_info_disclosed."""
    # All-zero cells -> sub-aggregates all 0 except B
    # (B has 1-B1 + 1-B2 = 2 when B1=B2=0/missing, B3=B4=0/missing).
    cells: dict[str, dict[str, object]] = {}
    score = project_pri_2010_disclosure_law(cells, "TEST")
    assert score.A_registration == 0
    assert score.B_gov_exemptions == 2  # reverse-scored: missing B1/B2 -> 0 -> 1 each
    assert score.C_public_entity_def == 0
    assert score.D_materiality == 0
    assert score.E_info_disclosed == 0
    assert score.total == 2


def test_disclosure_law_returns_typed_score_model():
    score = project_pri_2010_disclosure_law({}, "AL")
    assert isinstance(score, PRI2010DisclosureLawScore)
    assert score.state == "AL"


def test_disclosure_law_percent_normalizes_against_37():
    """percent = total / 37 * 100. Spec rollup max is 37 per Table 5."""
    cells = {row: {"legal_availability": True} for row in _A_ROWS}
    score = project_pri_2010_disclosure_law(cells, "TEST")
    # A=11, B=2 (B1=B2=missing/0 -> +1 each), C=0, D=0, E=0 -> total 13
    assert score.total == 13
    assert abs(score.percent - 13 / 37 * 100) < 1e-9


def test_accessibility_percent_normalizes_against_22():
    cells = _cells_for_accessibility_state(1, 1, 1, 1, 1, 1, 11, 5)
    score = project_pri_2010_accessibility(cells, "TEST")
    # 6 + 11 + 5/15 = 17 + 0.333... = 17.333...
    expected_total = 6 + 11 + 5 / 15
    assert abs(score.total - expected_total) < 1e-9
    assert abs(score.percent - expected_total / 22 * 100) < 1e-9


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def test_disclosure_law_rank_50_states_matches_published():
    """Ranking states by descending total reproduces PRI's published
    disclosure-law rank. CPI used competition (1224) ranking; check whether
    PRI uses the same. The ground-truth CSV's rank_2010 column is the spec.
    """
    from lobby_analysis.projections.pri_2010 import rank_pri_2010_states

    references = load_pri_2010_disclosure_law_reference(REPO_ROOT)
    # Build {state: total}
    totals = {s: ref.total for s, ref in references.items()}
    projected_ranks = rank_pri_2010_states(totals)
    # Load published ranks
    import csv

    csv_path = (
        REPO_ROOT
        / "docs"
        / "historical"
        / "pri-2026-rescore"
        / "results"
        / "pri_2010_disclosure_law_scores.csv"
    )
    state_name_to_usps = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
    }
    published_ranks: dict[str, int] = {}
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            published_ranks[state_name_to_usps[row["state"]]] = int(row["rank_2010"])
    mismatches = []
    for state in published_ranks:
        if projected_ranks[state] != published_ranks[state]:
            mismatches.append((state, projected_ranks[state], published_ranks[state]))
    assert mismatches == [], f"rank mismatches: {mismatches}"

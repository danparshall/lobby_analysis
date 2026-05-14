"""Per-item projection tests for CPI 2015 C11 (Lobbying Disclosure).

Each test exercises a single per-item helper (e.g. ``project_ind_196``)
against a hand-built ``cells`` dict keyed by ``compendium_row_id``. The
shape of each cell value is::

    cells[row_id] = {
        "legal_availability": <typed>,        # optional
        "practical_availability": <typed>,    # optional
    }

Helpers return an ``int`` in {0, 25, 50, 75, 100}:

* De jure 2-tier items use {0, 100}.
* De jure 3-tier items use {0, 50, 100}.
* De facto 5-tier items use {0, 25, 50, 75, 100}.

This is the canonical projected-score representation; it matches what
the CPI 2015 graders recorded in the per-state CSV and is what the
aggregation rule operates on.

Per-item de jure tests are fixture-based (no per-state ground truth at
the underlying cell level — spec doc Open Issue 5). De facto passthrough
items also get a 50-state data-driven test that doubles as a wiring
check.
"""

from __future__ import annotations

import pytest

from lobby_analysis.projections.cpi_2015_c11 import (
    load_per_state_ground_truth,
    project_ind_196,
    project_ind_197,
    project_ind_198,
    project_ind_199,
    project_ind_200,
    project_ind_201,
    project_ind_202,
    project_ind_203,
    project_ind_204,
    project_ind_205,
    project_ind_206,
    project_ind_207,
    project_ind_208,
    project_ind_209,
)


# ---------------------------------------------------------------------------
# IND_196 - de jure 2-tier: def_target_legislative AND def_target_governors_office
# ---------------------------------------------------------------------------


def test_ind_196_yes_when_legislative_and_governors_office_both_covered():
    cells = {
        "def_target_legislative_branch": {"legal_availability": True},
        "def_target_governors_office": {"legal_availability": True},
    }
    assert project_ind_196(cells) == 100


def test_ind_196_no_when_governors_office_not_covered():
    cells = {
        "def_target_legislative_branch": {"legal_availability": True},
        "def_target_governors_office": {"legal_availability": False},
    }
    assert project_ind_196(cells) == 0


def test_ind_196_no_when_legislative_not_covered():
    cells = {
        "def_target_legislative_branch": {"legal_availability": False},
        "def_target_governors_office": {"legal_availability": True},
    }
    assert project_ind_196(cells) == 0


def test_ind_196_no_when_neither_covered():
    cells = {
        "def_target_legislative_branch": {"legal_availability": False},
        "def_target_governors_office": {"legal_availability": False},
    }
    assert project_ind_196(cells) == 0


# ---------------------------------------------------------------------------
# IND_197 - de jure 3-tier: compensation_threshold_for_lobbyist_registration
# threshold == 0 -> YES (100); threshold > 0 -> MOD (50); no statute -> NO (0).
# ---------------------------------------------------------------------------


def test_ind_197_yes_when_compensation_threshold_is_zero():
    cells = {"compensation_threshold_for_lobbyist_registration": {"legal_availability": 0}}
    assert project_ind_197(cells) == 100


def test_ind_197_moderate_when_compensation_threshold_is_positive():
    cells = {"compensation_threshold_for_lobbyist_registration": {"legal_availability": 500}}
    assert project_ind_197(cells) == 50


def test_ind_197_no_when_no_compensation_statute():
    cells = {"compensation_threshold_for_lobbyist_registration": {"legal_availability": None}}
    assert project_ind_197(cells) == 0


# ---------------------------------------------------------------------------
# IND_198 - de facto 5-tier passthrough: lobbyist_registration_required
# (practical_availability axis)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_198_passes_through_practical_availability_value(value: int):
    cells = {"lobbyist_registration_required": {"practical_availability": value}}
    assert project_ind_198(cells) == value


# ---------------------------------------------------------------------------
# IND_199 - de jure 3-tier: lobbyist_registration_renewal_cadence
# annual or more frequent -> YES; biennial/less_frequent -> MOD; no_registration -> NO.
# Cell type is enum string.
# ---------------------------------------------------------------------------


def test_ind_199_yes_when_renewal_cadence_is_annual():
    cells = {"lobbyist_registration_renewal_cadence": {"legal_availability": "annual"}}
    assert project_ind_199(cells) == 100


def test_ind_199_moderate_when_renewal_cadence_is_biennial():
    cells = {"lobbyist_registration_renewal_cadence": {"legal_availability": "biennial"}}
    assert project_ind_199(cells) == 50


def test_ind_199_moderate_when_renewal_cadence_is_less_frequent_than_biennial():
    cells = {
        "lobbyist_registration_renewal_cadence": {
            "legal_availability": "less_frequent_than_biennial"
        }
    }
    assert project_ind_199(cells) == 50


def test_ind_199_no_when_no_registration_required():
    cells = {
        "lobbyist_registration_renewal_cadence": {
            "legal_availability": "no_registration_required"
        }
    }
    assert project_ind_199(cells) == 0


# ---------------------------------------------------------------------------
# IND_200 - de facto 5-tier passthrough:
# registration_timeliness_after_first_lobbying_activity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_200_passes_through_practical_availability_value(value: int):
    cells = {
        "registration_timeliness_after_first_lobbying_activity": {
            "practical_availability": value
        }
    }
    assert project_ind_200(cells) == value


# ---------------------------------------------------------------------------
# IND_201 - de jure 3-tier compound (3 binary rows):
# report_required AND itemized AND includes_compensation -> 100
# report_required AND (itemized XOR includes_compensation) -> 50
# else -> 0
# ---------------------------------------------------------------------------


def test_ind_201_yes_when_report_required_itemized_and_compensation_included():
    cells = {
        "lobbyist_spending_report_required": {"legal_availability": True},
        "lobbyist_spending_report_includes_itemized_expenses": {"legal_availability": True},
        "lobbyist_spending_report_includes_compensation": {"legal_availability": True},
    }
    assert project_ind_201(cells) == 100


def test_ind_201_moderate_when_itemized_but_no_compensation():
    cells = {
        "lobbyist_spending_report_required": {"legal_availability": True},
        "lobbyist_spending_report_includes_itemized_expenses": {"legal_availability": True},
        "lobbyist_spending_report_includes_compensation": {"legal_availability": False},
    }
    assert project_ind_201(cells) == 50


def test_ind_201_moderate_when_compensation_but_not_itemized():
    cells = {
        "lobbyist_spending_report_required": {"legal_availability": True},
        "lobbyist_spending_report_includes_itemized_expenses": {"legal_availability": False},
        "lobbyist_spending_report_includes_compensation": {"legal_availability": True},
    }
    assert project_ind_201(cells) == 50


def test_ind_201_no_when_no_report_required():
    cells = {
        "lobbyist_spending_report_required": {"legal_availability": False},
        "lobbyist_spending_report_includes_itemized_expenses": {"legal_availability": True},
        "lobbyist_spending_report_includes_compensation": {"legal_availability": True},
    }
    assert project_ind_201(cells) == 0


# ---------------------------------------------------------------------------
# IND_202 - de facto 5-tier passthrough: lobbyist_spending_report_filing_cadence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_202_passes_through_practical_availability_value(value: int):
    cells = {"lobbyist_spending_report_filing_cadence": {"practical_availability": value}}
    assert project_ind_202(cells) == value


# ---------------------------------------------------------------------------
# IND_203 - de jure 3-tier: principal_spending_report_required
# + principal_spending_report_includes_compensation_paid_to_lobbyists
# Both true -> 100; required only -> 50; not required -> 0.
# ---------------------------------------------------------------------------


def test_ind_203_yes_when_principal_report_required_and_includes_compensation():
    cells = {
        "principal_spending_report_required": {"legal_availability": True},
        "principal_spending_report_includes_compensation_paid_to_lobbyists": {
            "legal_availability": True
        },
    }
    assert project_ind_203(cells) == 100


def test_ind_203_moderate_when_principal_report_required_but_no_compensation():
    cells = {
        "principal_spending_report_required": {"legal_availability": True},
        "principal_spending_report_includes_compensation_paid_to_lobbyists": {
            "legal_availability": False
        },
    }
    assert project_ind_203(cells) == 50


def test_ind_203_no_when_principal_report_not_required():
    cells = {
        "principal_spending_report_required": {"legal_availability": False},
        "principal_spending_report_includes_compensation_paid_to_lobbyists": {
            "legal_availability": True
        },
    }
    assert project_ind_203(cells) == 0


# ---------------------------------------------------------------------------
# IND_204 - de facto 5-tier passthrough:
# principal_spending_report_includes_compensation_paid_to_lobbyists
# (reads the practical_availability axis of the same row #203 hits in law).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_204_passes_through_practical_availability_value(value: int):
    cells = {
        "principal_spending_report_includes_compensation_paid_to_lobbyists": {
            "practical_availability": value
        }
    }
    assert project_ind_204(cells) == value


# ---------------------------------------------------------------------------
# IND_205 - de facto compound (3 reads):
# online AND free OR offline within 7 days -> 100
# offline 2 weeks visit-required or fee -> 50
# offline > a month or prohibitive or unobtainable -> 0
# 25 / 75 intermediate are scorer judgment partial credit.
# ---------------------------------------------------------------------------


def test_ind_205_full_score_when_online_and_free():
    cells = {
        "lobbying_disclosure_documents_online": {"practical_availability": True},
        "lobbying_disclosure_documents_free_to_access": {"practical_availability": True},
        "lobbying_disclosure_offline_request_response_time_days": {
            "practical_availability": 7
        },
    }
    assert project_ind_205(cells) == 100


def test_ind_205_full_score_when_offline_within_seven_days():
    cells = {
        "lobbying_disclosure_documents_online": {"practical_availability": False},
        "lobbying_disclosure_documents_free_to_access": {"practical_availability": False},
        "lobbying_disclosure_offline_request_response_time_days": {
            "practical_availability": 5
        },
    }
    assert project_ind_205(cells) == 100


def test_ind_205_half_score_when_offline_two_weeks_with_fee():
    cells = {
        "lobbying_disclosure_documents_online": {"practical_availability": False},
        "lobbying_disclosure_documents_free_to_access": {"practical_availability": False},
        "lobbying_disclosure_offline_request_response_time_days": {
            "practical_availability": 14
        },
    }
    assert project_ind_205(cells) == 50


def test_ind_205_zero_when_offline_more_than_a_month():
    cells = {
        "lobbying_disclosure_documents_online": {"practical_availability": False},
        "lobbying_disclosure_documents_free_to_access": {"practical_availability": False},
        "lobbying_disclosure_offline_request_response_time_days": {
            "practical_availability": 35
        },
    }
    assert project_ind_205(cells) == 0


# ---------------------------------------------------------------------------
# IND_206 - de facto 5-tier passthrough: lobbying_data_open_data_quality
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_206_passes_through_practical_availability_value(value: int):
    cells = {"lobbying_data_open_data_quality": {"practical_availability": value}}
    assert project_ind_206(cells) == value


# ---------------------------------------------------------------------------
# IND_207 - de jure 3-tier: lobbying_disclosure_audit_required_in_law (enum)
# regular_third_party_audit_required -> 100
# audit_only_when_irregularities_suspected_or_compliance_review -> 50
# no_audit_requirement -> 0
# ---------------------------------------------------------------------------


def test_ind_207_yes_when_regular_third_party_audit_required():
    cells = {
        "lobbying_disclosure_audit_required_in_law": {
            "legal_availability": "regular_third_party_audit_required"
        }
    }
    assert project_ind_207(cells) == 100


def test_ind_207_moderate_when_audit_only_when_irregularities():
    cells = {
        "lobbying_disclosure_audit_required_in_law": {
            "legal_availability": "audit_only_when_irregularities_suspected_or_compliance_review"
        }
    }
    assert project_ind_207(cells) == 50


def test_ind_207_no_when_no_audit_requirement():
    cells = {
        "lobbying_disclosure_audit_required_in_law": {
            "legal_availability": "no_audit_requirement"
        }
    }
    assert project_ind_207(cells) == 0


# ---------------------------------------------------------------------------
# IND_208 - de facto 5-tier passthrough: lobbying_disclosure_audit_required_in_law
# (reads practical_availability axis of the same row #207 hits in law).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_208_passes_through_practical_availability_value(value: int):
    cells = {
        "lobbying_disclosure_audit_required_in_law": {"practical_availability": value}
    }
    assert project_ind_208(cells) == value


# ---------------------------------------------------------------------------
# IND_209 - de facto 5-tier passthrough:
# lobbying_violation_penalties_imposed_in_practice
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 25, 50, 75, 100])
def test_ind_209_passes_through_practical_availability_value(value: int):
    cells = {
        "lobbying_violation_penalties_imposed_in_practice": {"practical_availability": value}
    }
    assert project_ind_209(cells) == value


# ---------------------------------------------------------------------------
# Data-driven 50-state wiring tests for the 8 de facto passthrough items.
# These are weak validation (passthrough is tautological) but exercise
# the full plumbing from ground-truth CSV -> cells dict -> projection
# helper -> int across every state.
# ---------------------------------------------------------------------------


_DE_FACTO_PASSTHROUGH_ITEMS = {
    "IND_198": (project_ind_198, "lobbyist_registration_required"),
    "IND_200": (
        project_ind_200,
        "registration_timeliness_after_first_lobbying_activity",
    ),
    "IND_202": (project_ind_202, "lobbyist_spending_report_filing_cadence"),
    "IND_204": (
        project_ind_204,
        "principal_spending_report_includes_compensation_paid_to_lobbyists",
    ),
    "IND_206": (project_ind_206, "lobbying_data_open_data_quality"),
    "IND_208": (project_ind_208, "lobbying_disclosure_audit_required_in_law"),
    "IND_209": (project_ind_209, "lobbying_violation_penalties_imposed_in_practice"),
}


@pytest.mark.parametrize("indicator_id", sorted(_DE_FACTO_PASSTHROUGH_ITEMS))
def test_de_facto_passthrough_against_50_state_ground_truth(indicator_id: str):
    truth = load_per_state_ground_truth()
    helper, row_id = _DE_FACTO_PASSTHROUGH_ITEMS[indicator_id]
    states_seen = 0
    for (state, ind), expected in truth.items():
        if ind != indicator_id:
            continue
        cells = {row_id: {"practical_availability": expected}}
        actual = helper(cells)
        assert actual == expected, f"{indicator_id} {state}: {actual} != {expected}"
        states_seen += 1
    assert states_seen == 50

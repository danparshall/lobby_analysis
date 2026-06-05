"""Aggregation / end-to-end / regression tests for Sunlight 2015.

This file's role differs from CPI/PRI's aggregation tests. Sunlight's
published ``Total`` (arithmetic sum across all 5 items) and ``Grade``
(letter, empirically-derived cutoffs) cannot be reproduced because
item 4 (``document_accessibility``) is excluded. The module
intentionally does NOT export aggregation functions; the tests here
regression-guard their absence.

The 50-state validation is per-state per-item: for each (state, item)
pair in the published CSV, build a minimal ``cells`` dict whose
projection should yield the published tier, run
``project_sunlight_2015``, and assert
``score.per_item_scores[item_id] == reference_tier``.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import lobby_analysis.projections.sunlight_2015 as sunlight_mod
from lobby_analysis.projections.sunlight_2015 import (
    IN_SCOPE_ITEMS,
    Sunlight2015Score,
    UNABLE_TO_EVALUATE,
    load_sunlight_2015_reference,
    load_sunlight_2015_reference_marker_provenance,
    project_sunlight_2015,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Regression guard: no aggregation API
# ---------------------------------------------------------------------------


def test_module_does_not_export_total_function():
    assert not hasattr(sunlight_mod, "project_sunlight_2015_total")


def test_module_does_not_export_grade_function():
    assert not hasattr(sunlight_mod, "project_sunlight_2015_grade")


def test_module_does_not_export_rank_function():
    assert not hasattr(sunlight_mod, "rank_sunlight_2015_states")


def test_score_model_has_no_total_field():
    fields = Sunlight2015Score.model_fields
    assert "total" not in fields
    assert "grade" not in fields
    assert "rank" not in fields


# ---------------------------------------------------------------------------
# Reverse-projection cells builder (test-fixture only — not production code)
# ---------------------------------------------------------------------------


def _cells_yielding_tier(item_id: str, tier: int) -> dict:
    """Build a minimal cells dict whose projection yields ``tier`` for ``item_id``.

    The canonical truth-table rows are picked for items with multiple
    valid input combinations producing the same tier (item 1: set both
    form sides to the same nested-tier pattern; item 5: set the
    spending-report total-compensation cell to True for tier 0).
    """
    if item_id == "sunlight_2015.lobbyist_activity":
        # 4 tiers; pick the canonical monotonic row and mirror both form sides.
        patterns = {
            -1: (False, False, False),
            0: (True, False, False),
            1: (True, True, False),
            2: (True, True, True),
        }
        gen, bill, pos = patterns[tier]
        return {
            "lobbyist_reg_form_includes_general_subject_matter": {
                "legal_availability": gen
            },
            "lobbyist_reg_form_includes_bill_or_action_identifier": {
                "legal_availability": bill
            },
            "lobbyist_reg_form_includes_position_on_bill": {"legal_availability": pos},
            "lobbyist_spending_report_includes_general_subject_matter": {
                "legal_availability": gen
            },
            "lobbyist_spending_report_includes_bill_or_action_identifier": {
                "legal_availability": bill
            },
            "lobbyist_spending_report_includes_position_on_bill": {
                "legal_availability": pos
            },
        }
    if item_id == "sunlight_2015.expenditure_transparency":
        patterns = {
            -1: (False, False, False),
            0: (True, False, False),
            1: (True, True, False),
            2: (True, True, True),
        }
        req, cat, itm = patterns[tier]
        return {
            "lobbyist_spending_report_required": {"legal_availability": req},
            "lobbyist_spending_report_categorizes_expenses_by_type": {
                "legal_availability": cat
            },
            "lobbyist_spending_report_includes_itemized_expenses": {
                "legal_availability": itm
            },
        }
    if item_id == "sunlight_2015.expenditure_reporting_thresholds":
        if tier == 0:
            return {
                "lobbyist_filing_itemization_de_minimis_threshold_dollars": {
                    "legal_availability": None
                }
            }
        if tier == -1:
            return {
                "lobbyist_filing_itemization_de_minimis_threshold_dollars": {
                    "legal_availability": Decimal("100")
                }
            }
        raise AssertionError(f"unexpected tier {tier} for {item_id}")
    if item_id == "sunlight_2015.lobbyist_compensation":
        if tier == 0:
            # Canonical: total-compensation cell True; others False (still
            # OR-projects to disclosed).
            return {
                "lobbyist_spending_report_includes_total_compensation": {
                    "legal_availability": True
                },
                "lobbyist_spending_report_includes_compensation_broken_down_by_payer": {
                    "legal_availability": False
                },
                "lobbyist_reg_form_includes_compensation": {"legal_availability": False},
            }
        if tier == -1:
            return {
                "lobbyist_spending_report_includes_total_compensation": {
                    "legal_availability": False
                },
                "lobbyist_spending_report_includes_compensation_broken_down_by_payer": {
                    "legal_availability": False
                },
                "lobbyist_reg_form_includes_compensation": {"legal_availability": False},
            }
        raise AssertionError(f"unexpected tier {tier} for {item_id}")
    raise AssertionError(f"unknown item_id {item_id}")


# ---------------------------------------------------------------------------
# 50-state per-state per-item parameterized validation
# ---------------------------------------------------------------------------


def _state_item_params() -> list[tuple[str, str, int]]:
    reference = load_sunlight_2015_reference(REPO_ROOT)
    out: list[tuple[str, str, int]] = []
    for state, scores in reference.items():
        for item_id in IN_SCOPE_ITEMS:
            out.append((state, item_id, scores[item_id]))
    return out


@pytest.mark.parametrize(("state", "item_id", "expected_tier"), _state_item_params())
def test_50_state_per_item_round_trip(state: str, item_id: str, expected_tier: int):
    cells = _cells_yielding_tier(item_id, expected_tier)
    score = project_sunlight_2015(cells, state)
    assert score.per_item_scores[item_id] == expected_tier


# ---------------------------------------------------------------------------
# Top-level Sunlight2015Score wiring
# ---------------------------------------------------------------------------


def test_project_sunlight_2015_returns_score_model_with_all_4_items():
    cells: dict = {}
    for item_id in IN_SCOPE_ITEMS:
        cells.update(_cells_yielding_tier(item_id, 0))
    score = project_sunlight_2015(cells, "VA")
    assert isinstance(score, Sunlight2015Score)
    assert score.state == "VA"
    assert set(score.per_item_scores.keys()) == set(IN_SCOPE_ITEMS)


def test_project_sunlight_2015_threads_unable_to_evaluate():
    # No cells at all → every item returns the sentinel; oddity_flags are empty.
    score = project_sunlight_2015({}, "VA")
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == UNABLE_TO_EVALUATE


def test_project_sunlight_2015_threads_oddity_flags():
    cells = {
        # Item 1 oddity: bill_id=True with general_subject=False.
        "lobbyist_reg_form_includes_general_subject_matter": {"legal_availability": False},
        "lobbyist_reg_form_includes_bill_or_action_identifier": {"legal_availability": True},
        "lobbyist_reg_form_includes_position_on_bill": {"legal_availability": False},
        "lobbyist_spending_report_includes_general_subject_matter": {
            "legal_availability": False
        },
        "lobbyist_spending_report_includes_bill_or_action_identifier": {
            "legal_availability": False
        },
        "lobbyist_spending_report_includes_position_on_bill": {"legal_availability": False},
        # Items 2, 3, 5 default to clean tiers.
        "lobbyist_spending_report_required": {"legal_availability": True},
        "lobbyist_spending_report_categorizes_expenses_by_type": {"legal_availability": True},
        "lobbyist_spending_report_includes_itemized_expenses": {"legal_availability": False},
        "lobbyist_filing_itemization_de_minimis_threshold_dollars": {"legal_availability": None},
        "lobbyist_spending_report_includes_total_compensation": {"legal_availability": True},
        "lobbyist_spending_report_includes_compensation_broken_down_by_payer": {
            "legal_availability": False
        },
        "lobbyist_reg_form_includes_compensation": {"legal_availability": False},
    }
    score = project_sunlight_2015(cells, "VA")
    assert score.per_item_scores["sunlight_2015.lobbyist_activity"] == -1
    assert len(score.oddity_flags["sunlight_2015.lobbyist_activity"]) == 1
    # Other items have no oddity.
    assert score.oddity_flags["sunlight_2015.expenditure_transparency"] == []
    assert score.oddity_flags["sunlight_2015.expenditure_reporting_thresholds"] == []
    assert score.oddity_flags["sunlight_2015.lobbyist_compensation"] == []


# ---------------------------------------------------------------------------
# Marker-provenance round-trip
# ---------------------------------------------------------------------------


def test_marker_carrying_cells_still_project_to_published_tier():
    """For each (state, item) carrying a marker, build cells from the
    *stripped* tier and assert the projection matches that stripped tier.
    Markers are caveats on the published tier, not invalidations."""
    reference = load_sunlight_2015_reference(REPO_ROOT)
    provenance = load_sunlight_2015_reference_marker_provenance(REPO_ROOT)
    for state, marker_map in provenance.items():
        for item_id in marker_map:
            expected_tier = reference[state][item_id]
            cells = _cells_yielding_tier(item_id, expected_tier)
            score = project_sunlight_2015(cells, state)
            assert score.per_item_scores[item_id] == expected_tier, (
                f"{state}.{item_id} (marker {marker_map[item_id]!r}): "
                f"projected {score.per_item_scores[item_id]} != published {expected_tier}"
            )

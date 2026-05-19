"""Aggregation / end-to-end / regression tests for Newmark 2017.

This file:

* exercises ``project_newmark_2017`` end-to-end (cells -> per_item +
  sub-aggregates),
* regression-guards the absence of an ``index_total`` API (5 ``prohib.*``
  cells excluded -> 0-19 total not reproducible),
* regression-guards the absence of helpers for the 5 excluded
  ``prohib.*`` items, and
* confirms the in-scope / excluded item membership invariants.

There is intentionally no 50-state per-item ground-truth test. Newmark
2017 publishes only sub-aggregate totals per state in Table 2 of the
PDF; the per-state CSV extraction is deferred (no extracted CSV exists
in the repo yet). The aggregation test covers the projection logic via
synthetic fixtures.
"""

from __future__ import annotations

from decimal import Decimal

import lobby_analysis.projections.newmark_2017 as newmark_2017_mod
from lobby_analysis.projections.newmark_2017 import (
    EXCLUDED_ITEMS,
    IN_SCOPE_ITEMS,
    Newmark2017Score,
    UNABLE_TO_EVALUATE,
    project_newmark_2017,
)


# ---------------------------------------------------------------------------
# Regression guards: no ``index_total`` API
# ---------------------------------------------------------------------------


def test_module_does_not_export_index_total_function():
    """``index.total = def + prohib + disclosure`` requires the 5
    excluded ``prohib.*`` cells; exposing an ``index_total`` function
    would smuggle a wrong-by-design API."""
    assert not hasattr(newmark_2017_mod, "project_newmark_2017_index_total")


def test_module_does_not_export_prohib_section_total_function():
    assert not hasattr(newmark_2017_mod, "project_newmark_2017_prohib_section_total")


def test_score_model_has_no_index_total_field():
    fields = Newmark2017Score.model_fields
    assert "index_total" not in fields
    assert "prohib_section_total" not in fields


# ---------------------------------------------------------------------------
# Regression guards: excluded items have no helpers
# ---------------------------------------------------------------------------


def test_excluded_items_are_disjoint_from_in_scope():
    assert EXCLUDED_ITEMS.isdisjoint(set(IN_SCOPE_ITEMS))


def test_in_scope_items_count_is_fourteen():
    """7 def items + 7 disclosure items = 14."""
    assert len(IN_SCOPE_ITEMS) == 14


def test_excluded_items_count_is_five():
    """5 ``prohib.*`` items excluded per Phase B disclosure-only qualifier."""
    assert len(EXCLUDED_ITEMS) == 5


def test_no_helper_defined_for_prohib_items():
    """The dispatcher raises KeyError for any out-of-scope item."""
    from lobby_analysis.projections.newmark_2017 import project_newmark_2017_item

    for item_id in EXCLUDED_ITEMS:
        try:
            project_newmark_2017_item(item_id, {})
        except KeyError:
            continue
        raise AssertionError(f"expected KeyError for excluded {item_id!r}")


# ---------------------------------------------------------------------------
# End-to-end fixture builders
# ---------------------------------------------------------------------------


def _cells_all_true() -> dict[str, dict]:
    """Build a complete cells dict where every in-scope item projects to 1.

    For binary items: axis True.
    For typed items: axis is a non-empty representative value.
    For gifts OR: lobbyist-side True (principal-side absent is fine — the
    helper short-circuits TRUE without needing the other side).
    """
    return {
        # Definitions: 4 binary
        "def_target_legislative_branch": {"legal_availability": True},
        "def_target_executive_agency": {"legal_availability": True},
        "def_actor_class_elected_officials": {"legal_availability": True},
        "def_actor_class_public_employees": {"legal_availability": True},
        # Definitions: 3 typed
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": Decimal("500.00")
        },
        "lobbyist_registration_threshold_expenditure_dollars": {
            "legal_availability": Decimal("250.00")
        },
        "lobbyist_registration_threshold_time_percent": {"legal_availability": "20%"},
        # Disclosure: 6 single-row binary
        "lobbyist_spending_report_includes_general_subject_matter": {
            "legal_availability": True
        },
        "lobbyist_spending_report_includes_compensation_broken_down_by_payer": {
            "legal_availability": True
        },
        "lobbyist_spending_report_includes_total_compensation": {
            "legal_availability": True
        },
        "lobbyist_spending_report_categorizes_expenses_by_type": {
            "legal_availability": True
        },
        "lobbyist_spending_report_includes_total_expenditures": {
            "legal_availability": True
        },
        "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying": {
            "legal_availability": True
        },
        # Disclosure: gifts actor-agnostic OR
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": True
        },
        "principal_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": False
        },
    }


def _cells_all_false() -> dict[str, dict]:
    """Complete cells dict where every in-scope item projects to 0.

    Typed cells get axis None (no threshold defined -> 0); binary cells
    get axis False.
    """
    cells = _cells_all_true()
    for row_id in cells:
        if row_id.startswith("lobbyist_registration_threshold_"):
            cells[row_id] = {"legal_availability": None}
        else:
            cells[row_id] = {"legal_availability": False}
    return cells


# ---------------------------------------------------------------------------
# project_newmark_2017 top-level wiring
# ---------------------------------------------------------------------------


def test_project_returns_score_model_with_all_14_items():
    score = project_newmark_2017(_cells_all_true(), "VA")
    assert isinstance(score, Newmark2017Score)
    assert score.state == "VA"
    assert set(score.per_item_scores.keys()) == set(IN_SCOPE_ITEMS)


def test_project_all_true_yields_max_sub_aggregates():
    score = project_newmark_2017(_cells_all_true(), "VA")
    assert score.def_section_total == 7
    assert score.disclosure_section_total == 7
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == 1, f"{item_id}"


def test_project_all_false_yields_zero_sub_aggregates():
    score = project_newmark_2017(_cells_all_false(), "VA")
    assert score.def_section_total == 0
    assert score.disclosure_section_total == 0
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == 0, f"{item_id}"


def test_project_empty_cells_yields_all_unable_and_none_sub_aggregates():
    """No cells at all -> every item is the sentinel; sub-aggregates are
    None (cannot sum a battery containing the sentinel)."""
    score = project_newmark_2017({}, "VA")
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == UNABLE_TO_EVALUATE
    assert score.def_section_total is None
    assert score.disclosure_section_total is None


def test_project_partial_def_battery_yields_none_for_def_section_total():
    """One missing def cell -> def_section_total is None; disclosure is
    fully populated so disclosure_section_total is concrete."""
    cells = _cells_all_true()
    del cells["lobbyist_registration_threshold_time_percent"]
    score = project_newmark_2017(cells, "VA")
    assert score.def_section_total is None
    assert score.disclosure_section_total == 7
    assert (
        score.per_item_scores["newmark_2017.def.time_standard"] == UNABLE_TO_EVALUATE
    )


def test_project_mixed_truth_table_yields_correct_partial_sums():
    """Honest sub-aggregate counts when 3 def items + 5 disclosure
    items project to 1, others to 0."""
    cells = _cells_all_false()
    # Flip 3 def items to TRUE.
    cells["def_target_legislative_branch"] = {"legal_availability": True}
    cells["def_target_executive_agency"] = {"legal_availability": True}
    cells["lobbyist_registration_threshold_compensation_dollars"] = {
        "legal_availability": Decimal("500.00")
    }
    # Flip 5 disclosure items to TRUE.
    cells["lobbyist_spending_report_includes_general_subject_matter"] = {
        "legal_availability": True
    }
    cells["lobbyist_spending_report_includes_total_compensation"] = {
        "legal_availability": True
    }
    cells["lobbyist_spending_report_categorizes_expenses_by_type"] = {
        "legal_availability": True
    }
    cells["lobbyist_spending_report_includes_total_expenditures"] = {
        "legal_availability": True
    }
    # Gifts: only lobbyist side TRUE — the OR-helper still yields 1.
    cells["lobbyist_spending_report_includes_gifts_entertainment_transport_lodging"] = {
        "legal_availability": True
    }
    score = project_newmark_2017(cells, "VA")
    assert score.def_section_total == 3
    assert score.disclosure_section_total == 5


# ---------------------------------------------------------------------------
# No-variation cells are still read honestly
# ---------------------------------------------------------------------------


def test_no_variation_def_legislative_lobbying_projects_zero_when_false():
    """Counterfactual: a 2015 state with no legislative-lobbying
    registration requirement. The projection returns 0 honestly — does
    not coerce to 1 just because every observed 2015 state was TRUE."""
    cells = _cells_all_true()
    cells["def_target_legislative_branch"] = {"legal_availability": False}
    score = project_newmark_2017(cells, "VA")
    assert score.per_item_scores["newmark_2017.def.legislative_lobbying"] == 0
    assert score.def_section_total == 6

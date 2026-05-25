"""Aggregation / end-to-end / regression tests for Newmark 2005.

This file:

* exercises ``project_newmark_2005`` end-to-end (cells -> per_item +
  panel-labeled score),
* regression-guards the absence of an ``index_total`` API (5 excluded
  items -> 0-18 total not reproducible),
* regression-guards the absence of sub-aggregate fields on the score
  model (Newmark 2005 publishes no sub-aggregates — exposing them would
  smuggle an API claiming reproducibility against unpublished data),
* regression-guards the absence of helpers for the 4 ``prohib_*`` items
  and the 1 ``penalty_stringency_2003`` add-on,
* regression-guards the falsified-2017-speculation: Newmark 2005 has
  6 disclosure items, NOT 7 — there is no ``contributions_from_others``
  parallel item, and the corresponding cell is not read by this
  module, and
* exercises the weak-inequality contract that
  ``sum(in_scope_items) <= published_index_total`` would hold for any
  valid input (verified here as ``<= 14`` since max partial is 14/18).

There is intentionally no 50-state per-panel ground-truth test. Newmark
2005 publishes only per-state totals in Table 1 (across 6 panels); the
extracted CSV does not exist in the repo yet, and weak-inequality
validation against per-state totals is deferred until that extraction
lands.
"""

from __future__ import annotations

from decimal import Decimal

import lobby_analysis.projections.newmark_2005 as newmark_2005_mod
from lobby_analysis.projections.newmark_2005 import (
    EXCLUDED_ITEMS,
    IN_SCOPE_ITEMS,
    Newmark2005Score,
    UNABLE_TO_EVALUATE,
    project_newmark_2005,
)


# ---------------------------------------------------------------------------
# Regression guards: no ``index_total`` API, no sub-aggregate API
# ---------------------------------------------------------------------------


def test_module_does_not_export_index_total_function():
    """The 0-18 total requires 5 excluded items (4 prohib + 1 penalty);
    exposing an ``index_total`` would smuggle a wrong-by-design API."""
    assert not hasattr(newmark_2005_mod, "project_newmark_2005_index_total")


def test_module_does_not_export_section_total_functions():
    """Newmark 2005 publishes only per-state totals (Table 1), NOT per-state
    sub-aggregates. Exposing ``def_section_total`` / ``disclosure_section_total``
    would claim reproducibility against unpublished data."""
    assert not hasattr(newmark_2005_mod, "project_newmark_2005_def_section_total")
    assert not hasattr(
        newmark_2005_mod, "project_newmark_2005_disclosure_section_total"
    )
    assert not hasattr(newmark_2005_mod, "project_newmark_2005_freq_section_total")


def test_score_model_has_no_total_or_sub_aggregate_fields():
    fields = Newmark2005Score.model_fields
    assert "index_total" not in fields
    assert "def_section_total" not in fields
    assert "freq_section_total" not in fields
    assert "disclosure_section_total" not in fields


def test_score_model_carries_panel_label():
    fields = Newmark2005Score.model_fields
    assert "panel" in fields


# ---------------------------------------------------------------------------
# Regression guards: excluded items have no helpers
# ---------------------------------------------------------------------------


def test_excluded_items_count_is_five():
    """4 ``prohib_*`` items + 1 ``penalty_stringency_2003`` add-on."""
    assert len(EXCLUDED_ITEMS) == 5


def test_in_scope_items_count_is_fourteen():
    """7 def + 1 freq + 6 disclosure = 14."""
    assert len(IN_SCOPE_ITEMS) == 14


def test_excluded_items_are_disjoint_from_in_scope():
    assert EXCLUDED_ITEMS.isdisjoint(set(IN_SCOPE_ITEMS))


def test_no_helper_defined_for_prohib_or_penalty_items():
    from lobby_analysis.projections.newmark_2005 import project_newmark_2005_item

    for item_id in EXCLUDED_ITEMS:
        try:
            project_newmark_2005_item(item_id, {})
        except KeyError:
            continue
        raise AssertionError(f"expected KeyError for excluded {item_id!r}")


# ---------------------------------------------------------------------------
# Falsified-2017-speculation regression guard
#
# The Newmark 2017 mapping speculated that Newmark 2005 had a parallel
# ``contributions_from_others`` disclosure item. The Newmark 2005 mapping
# work falsified this — Newmark 2005 has only 6 disclosure items, not 7.
# Confirm here that no ``contributions_from_others`` item is exposed and
# that the corresponding cell is not in the read set.
# ---------------------------------------------------------------------------


def test_no_contributions_from_others_item_in_newmark_2005():
    for item_id in IN_SCOPE_ITEMS:
        assert "contributions_from_others" not in item_id
        assert "contributions_received" not in item_id
    for item_id in EXCLUDED_ITEMS:
        assert "contributions_from_others" not in item_id


def test_contributions_received_cell_does_not_affect_newmark_2005():
    """Even if the Newmark-2017-distinctive cell is present in the cells
    dict, the Newmark 2005 projection ignores it."""
    cells_without = _cells_all_true()
    cells_with = dict(cells_without)
    cells_with[
        "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying"
    ] = {"legal_availability": True}
    score_without = project_newmark_2005(cells_without, "VA", "2003")
    score_with = project_newmark_2005(cells_with, "VA", "2003")
    assert score_without.per_item_scores == score_with.per_item_scores


# ---------------------------------------------------------------------------
# End-to-end fixture builders
# ---------------------------------------------------------------------------


_CADENCE_ROWS = (
    "lobbyist_spending_report_cadence_includes_monthly",
    "lobbyist_spending_report_cadence_includes_quarterly",
    "lobbyist_spending_report_cadence_includes_triannual",
    "lobbyist_spending_report_cadence_includes_semiannual",
    "principal_spending_report_cadence_includes_monthly",
    "principal_spending_report_cadence_includes_quarterly",
    "principal_spending_report_cadence_includes_triannual",
    "principal_spending_report_cadence_includes_semiannual",
)


def _cells_all_true() -> dict[str, dict]:
    """Cells dict where every in-scope Newmark 2005 item projects to 1.

    Cadence: ALL 8 sub-annual cells TRUE. Gifts: lobbyist-side TRUE.
    """
    cells: dict[str, dict] = {
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
        # Disclosure: 5 single-row binary
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
        # Disclosure: gifts OR
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": True
        },
        "principal_spending_report_includes_gifts_entertainment_transport_lodging": {
            "legal_availability": False
        },
    }
    # Frequency: 8 sub-annual cadence cells all TRUE.
    for row in _CADENCE_ROWS:
        cells[row] = {"legal_availability": True}
    return cells


def _cells_all_false() -> dict[str, dict]:
    cells = _cells_all_true()
    for row_id, cell in list(cells.items()):
        if row_id.startswith("lobbyist_registration_threshold_"):
            cells[row_id] = {"legal_availability": None}
        else:
            cells[row_id] = {"legal_availability": False}
    return cells


# ---------------------------------------------------------------------------
# project_newmark_2005 top-level wiring
# ---------------------------------------------------------------------------


def test_project_returns_score_model_with_all_14_items():
    score = project_newmark_2005(_cells_all_true(), "VA", "2003")
    assert isinstance(score, Newmark2005Score)
    assert score.state == "VA"
    assert score.panel == "2003"
    assert set(score.per_item_scores.keys()) == set(IN_SCOPE_ITEMS)


def test_project_all_true_yields_all_ones():
    score = project_newmark_2005(_cells_all_true(), "VA", "2003")
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == 1, f"{item_id}"


def test_project_all_false_yields_all_zeros():
    score = project_newmark_2005(_cells_all_false(), "VA", "2003")
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == 0, f"{item_id}"


def test_project_empty_cells_yields_all_unable():
    score = project_newmark_2005({}, "VA", "2003")
    for item_id in IN_SCOPE_ITEMS:
        assert score.per_item_scores[item_id] == UNABLE_TO_EVALUATE


def test_panel_label_is_threaded_through_unchanged():
    for panel in ("1990-91", "1994-95", "1996-97", "2000-01", "2002", "2003"):
        score = project_newmark_2005(_cells_all_true(), "VA", panel)
        assert score.panel == panel


# ---------------------------------------------------------------------------
# Weak-inequality contract
# ---------------------------------------------------------------------------


def test_max_partial_total_is_fourteen_of_eighteen():
    """The in-scope partial maxes out at 14 of Newmark's published 0-18.
    A test computing the partial sum from per_item_scores must always
    find <= 14 (or None, if any item is unable_to_evaluate)."""
    score = project_newmark_2005(_cells_all_true(), "VA", "2003")
    partial = sum(int(v) for v in score.per_item_scores.values() if isinstance(v, int))
    assert partial == 14
    assert partial <= 18  # weak inequality vs hypothetical published total


def test_partial_total_is_zero_when_no_provisions():
    score = project_newmark_2005(_cells_all_false(), "VA", "2003")
    partial = sum(int(v) for v in score.per_item_scores.values() if isinstance(v, int))
    assert partial == 0

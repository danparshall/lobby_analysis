"""Per-item projection tests for Sunlight 2015.

Each test exercises a single per-item helper against a hand-built
``cells`` dict keyed by ``compendium_row_id``. Cell shape::

    cells[row_id] = {
        "legal_availability": <typed>,
        "practical_availability": <typed>,    # ignored by Sunlight
    }

Helpers return ``tuple[int | Literal["unable_to_evaluate"], str | None]``:

* The first element is the projected tier (signed int) or the
  ``unable_to_evaluate`` sentinel when required input cells are missing.
* The second element is ``None`` for clean truth-table inputs, or a
  human-readable oddity string for statutorily-implausible
  combinations (e.g., ``bill_id=True AND general_subject=False``).

Item 4 (``document_accessibility``) is excluded; no helper is defined.
``test_sunlight_2015_aggregation.py`` regression-guards this.
"""

from __future__ import annotations

from lobby_analysis.projections.sunlight_2015 import (
    UNABLE_TO_EVALUATE,
    project_sunlight_item1,
)


# ---------------------------------------------------------------------------
# Item 1: lobbyist_activity (4-tier nested, alpha form-type split)
#
# 6 input cells (legal_availability axis):
#   reg-form side:        general_subject_matter, bill_or_action_identifier, position_on_bill
#   spending-report side: general_subject_matter, bill_or_action_identifier, position_on_bill
#
# Per-concept form-agnostic OR over the two form sides, then tier table:
#   (F, F, F) -> -1
#   (T, F, F) ->  0
#   (T, T, F) ->  1
#   (T, T, T) ->  2
# Statutorily-implausible combinations (lower predicate False, higher True)
# return the cascading-downward tier (lowest failing predicate) plus a
# non-None oddity string.
# ---------------------------------------------------------------------------


_REG_ROWS = {
    "general": "lobbyist_reg_form_includes_general_subject_matter",
    "bill": "lobbyist_reg_form_includes_bill_or_action_identifier",
    "position": "lobbyist_reg_form_includes_position_on_bill",
}
_SPEND_ROWS = {
    "general": "lobbyist_spending_report_includes_general_subject_matter",
    "bill": "lobbyist_spending_report_includes_bill_or_action_identifier",
    "position": "lobbyist_spending_report_includes_position_on_bill",
}


def _cells_item1(reg: tuple[bool, bool, bool], spend: tuple[bool, bool, bool]) -> dict:
    """Build a full item-1 cells dict from two (general, bill, position) triples."""
    cells: dict = {}
    for concept, val in zip(("general", "bill", "position"), reg):
        cells[_REG_ROWS[concept]] = {"legal_availability": val}
    for concept, val in zip(("general", "bill", "position"), spend):
        cells[_SPEND_ROWS[concept]] = {"legal_availability": val}
    return cells


def test_item1_unable_to_evaluate_when_all_cells_missing():
    score, oddity = project_sunlight_item1({})
    assert score == UNABLE_TO_EVALUATE
    assert oddity is None


def test_item1_unable_to_evaluate_when_one_required_cell_missing():
    # Omit lobbyist_spending_report_includes_position_on_bill specifically.
    cells = _cells_item1(reg=(True, True, True), spend=(True, True, True))
    del cells[_SPEND_ROWS["position"]]
    score, oddity = project_sunlight_item1(cells)
    assert score == UNABLE_TO_EVALUATE
    assert oddity is None

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

from decimal import Decimal

import itertools

from lobby_analysis.projections.sunlight_2015 import (
    UNABLE_TO_EVALUATE,
    project_sunlight_item1,
    project_sunlight_item2,
    project_sunlight_item3,
    project_sunlight_item5,
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


# --- valid truth-table tiers (4 tiers x 3 form-type variants) --------------


def test_item1_tier_minus1_when_nothing_disclosed_both_forms():
    cells = _cells_item1(reg=(False, False, False), spend=(False, False, False))
    assert project_sunlight_item1(cells) == (-1, None)


def test_item1_tier0_general_subject_only_on_reg_form():
    cells = _cells_item1(reg=(True, False, False), spend=(False, False, False))
    assert project_sunlight_item1(cells) == (0, None)


def test_item1_tier0_general_subject_only_on_spending_report():
    cells = _cells_item1(reg=(False, False, False), spend=(True, False, False))
    assert project_sunlight_item1(cells) == (0, None)


def test_item1_tier0_general_subject_on_both_forms():
    cells = _cells_item1(reg=(True, False, False), spend=(True, False, False))
    assert project_sunlight_item1(cells) == (0, None)


def test_item1_tier1_general_and_bill_on_reg_form_only():
    cells = _cells_item1(reg=(True, True, False), spend=(False, False, False))
    assert project_sunlight_item1(cells) == (1, None)


def test_item1_tier1_general_and_bill_split_across_forms():
    # general_subject on reg form; bill_id on spending report. OR over the
    # form-type split should still yield tier 1.
    cells = _cells_item1(reg=(True, False, False), spend=(False, True, False))
    assert project_sunlight_item1(cells) == (1, None)


def test_item1_tier2_full_disclosure_both_forms():
    cells = _cells_item1(reg=(True, True, True), spend=(True, True, True))
    assert project_sunlight_item1(cells) == (2, None)


def test_item1_tier2_position_only_on_spending_report_others_on_reg_form():
    # Each concept satisfied by one or both forms; specifically tests the
    # form-agnostic-OR behavior at every concept-pair.
    cells = _cells_item1(reg=(True, True, False), spend=(False, False, True))
    assert project_sunlight_item1(cells) == (2, None)


# --- statutorily-implausible (oddity) combinations -------------------------
#
# Cascading-downward: lowest failing predicate sets the tier. Oddity flag
# names the specific failure mode so a downstream auditor can investigate.


def test_item1_oddity_bill_without_general_subject():
    # general=F, bill=T, position=F  ->  tier -1 (general failed)
    cells = _cells_item1(reg=(False, True, False), spend=(False, False, False))
    score, oddity = project_sunlight_item1(cells)
    assert score == -1
    assert oddity is not None
    assert "bill_or_action_identifier" in oddity
    assert "general_subject_matter" in oddity


def test_item1_oddity_position_without_general_subject():
    # general=F, bill=F, position=T  ->  tier -1 (general failed)
    cells = _cells_item1(reg=(False, False, True), spend=(False, False, False))
    score, oddity = project_sunlight_item1(cells)
    assert score == -1
    assert oddity is not None
    assert "position_on_bill" in oddity
    assert "general_subject_matter" in oddity


def test_item1_oddity_bill_and_position_without_general_subject():
    # general=F, bill=T, position=T  ->  tier -1 (general failed)
    cells = _cells_item1(reg=(False, True, True), spend=(False, False, False))
    score, oddity = project_sunlight_item1(cells)
    assert score == -1
    assert oddity is not None
    assert "general_subject_matter" in oddity


def test_item1_oddity_position_without_bill():
    # general=T, bill=F, position=T  ->  tier 0 (bill failed)
    cells = _cells_item1(reg=(True, False, True), spend=(False, False, False))
    score, oddity = project_sunlight_item1(cells)
    assert score == 0
    assert oddity is not None
    assert "position_on_bill" in oddity
    assert "bill_or_action_identifier" in oddity


# ---------------------------------------------------------------------------
# Item 2: expenditure_transparency (4-tier clean nesting)
#
# 3 input cells (legal_availability):
#   lobbyist_spending_report_required
#   lobbyist_spending_report_categorizes_expenses_by_type
#   lobbyist_spending_report_includes_itemized_expenses
#
# Truth table (with wildcards from spec doc):
#   F * * -> -1
#   T F F ->  0
#   T T F ->  1
#   T * T ->  2
# Oddity: (T, F, T) — itemization without categorization. Tier 2 (per
# spec wildcard) plus non-None oddity flag.
# ---------------------------------------------------------------------------


_ITEM2_REQUIRED_ROW = "lobbyist_spending_report_required"
_ITEM2_CATEGORIZED_ROW = "lobbyist_spending_report_categorizes_expenses_by_type"
_ITEM2_ITEMIZED_ROW = "lobbyist_spending_report_includes_itemized_expenses"


def _cells_item2(required: bool, categorized: bool, itemized: bool) -> dict:
    return {
        _ITEM2_REQUIRED_ROW: {"legal_availability": required},
        _ITEM2_CATEGORIZED_ROW: {"legal_availability": categorized},
        _ITEM2_ITEMIZED_ROW: {"legal_availability": itemized},
    }


def test_item2_unable_to_evaluate_when_required_cell_missing():
    cells = _cells_item2(True, True, True)
    del cells[_ITEM2_REQUIRED_ROW]
    score, oddity = project_sunlight_item2(cells)
    assert score == UNABLE_TO_EVALUATE
    assert oddity is None


def test_item2_tier_minus1_not_required():
    # F * * -> -1; any combination of categorized/itemized.
    for categorized in (False, True):
        for itemized in (False, True):
            assert project_sunlight_item2(_cells_item2(False, categorized, itemized)) == (
                -1,
                None,
            )


def test_item2_tier0_required_lump_total():
    assert project_sunlight_item2(_cells_item2(True, False, False)) == (0, None)


def test_item2_tier1_required_categorized_not_itemized():
    assert project_sunlight_item2(_cells_item2(True, True, False)) == (1, None)


def test_item2_tier2_fully_itemized_and_categorized():
    assert project_sunlight_item2(_cells_item2(True, True, True)) == (2, None)


def test_item2_oddity_itemized_without_categorization():
    # T F T -> tier 2 (per spec wildcard "T * T -> 2") + oddity flag.
    score, oddity = project_sunlight_item2(_cells_item2(True, False, True))
    assert score == 2
    assert oddity is not None
    assert "itemized" in oddity
    assert "categorized" in oddity


# ---------------------------------------------------------------------------
# Item 3: expenditure_reporting_thresholds (2-tier typed cell)
#
# 1 input cell: lobbyist_filing_itemization_de_minimis_threshold_dollars
# (Optional[Decimal] on legal_availability axis).
#
#   threshold absent OR threshold == 0  ->   0   (all expenditures itemized)
#   threshold > 0                       ->  -1   (below-threshold lines exempt)
#
# unable_to_evaluate: row_id not present as a key in cells. A row present
# with legal_availability=None means "no threshold defined" -> tier 0
# per the spec rule "threshold IS NULL ... -> 0".
# ---------------------------------------------------------------------------


_ITEM3_ROW = "lobbyist_filing_itemization_de_minimis_threshold_dollars"


def test_item3_unable_to_evaluate_when_row_absent_from_cells():
    score, oddity = project_sunlight_item3({})
    assert score == UNABLE_TO_EVALUATE
    assert oddity is None


def test_item3_tier0_when_threshold_is_none():
    # Row present, legal_availability=None -> "no threshold defined" -> 0.
    cells = {_ITEM3_ROW: {"legal_availability": None}}
    assert project_sunlight_item3(cells) == (0, None)


def test_item3_tier0_when_threshold_is_zero_decimal():
    cells = {_ITEM3_ROW: {"legal_availability": Decimal("0")}}
    assert project_sunlight_item3(cells) == (0, None)


def test_item3_tier_minus1_when_threshold_positive_small():
    cells = {_ITEM3_ROW: {"legal_availability": Decimal("25.00")}}
    assert project_sunlight_item3(cells) == (-1, None)


def test_item3_tier_minus1_when_threshold_positive_large():
    cells = {_ITEM3_ROW: {"legal_availability": Decimal("500.00")}}
    assert project_sunlight_item3(cells) == (-1, None)


# ---------------------------------------------------------------------------
# Item 5: lobbyist_compensation (2-tier OR over 3 binary cells)
#
# 3 input cells (legal_availability):
#   lobbyist_spending_report_includes_total_compensation
#   lobbyist_spending_report_includes_compensation_broken_down_by_payer
#   lobbyist_reg_form_includes_compensation
#
# Rule: any compensation observable disclosed -> 0; none -> -1.
# (Form-agnostic OR; no oddity flags because there is no statutory
# implausibility — any subset of 3 disclosure modes can coexist.)
# ---------------------------------------------------------------------------


_ITEM5_TOTAL_ROW = "lobbyist_spending_report_includes_total_compensation"
_ITEM5_BREAKDOWN_ROW = (
    "lobbyist_spending_report_includes_compensation_broken_down_by_payer"
)
_ITEM5_REGFORM_ROW = "lobbyist_reg_form_includes_compensation"


def _cells_item5(total: bool, breakdown: bool, regform: bool) -> dict:
    return {
        _ITEM5_TOTAL_ROW: {"legal_availability": total},
        _ITEM5_BREAKDOWN_ROW: {"legal_availability": breakdown},
        _ITEM5_REGFORM_ROW: {"legal_availability": regform},
    }


def test_item5_unable_to_evaluate_when_total_row_missing():
    cells = _cells_item5(True, True, True)
    del cells[_ITEM5_TOTAL_ROW]
    score, oddity = project_sunlight_item5(cells)
    assert score == UNABLE_TO_EVALUATE
    assert oddity is None


def test_item5_tier_minus1_when_nothing_disclosed():
    assert project_sunlight_item5(_cells_item5(False, False, False)) == (-1, None)


def test_item5_tier0_for_every_non_zero_combination():
    # 2^3 - 1 = 7 combinations where at least one cell is True.
    for combo in itertools.product([False, True], repeat=3):
        if combo == (False, False, False):
            continue
        assert project_sunlight_item5(_cells_item5(*combo)) == (0, None), (
            f"expected (0, None) for combo {combo}"
        )


# ---------------------------------------------------------------------------
# Item 4: document_accessibility EXCLUDED
#
# Per 2026-05-07 audit: 5-tier ordinal conflates 3-4 sub-features with a
# documented -1/-2 near-typo. Cell-to-tier function not well-defined.
# Module exposes the exclusion via EXCLUDED_ITEMS; no helper is defined.
# ---------------------------------------------------------------------------


def test_item4_helper_is_not_defined():
    import lobby_analysis.projections.sunlight_2015 as sunlight_mod

    assert not hasattr(sunlight_mod, "project_sunlight_item4")


def test_item4_is_in_excluded_items():
    from lobby_analysis.projections.sunlight_2015 import EXCLUDED_ITEMS

    assert "sunlight_2015.document_accessibility" in EXCLUDED_ITEMS


def test_item4_not_in_in_scope_items():
    from lobby_analysis.projections.sunlight_2015 import IN_SCOPE_ITEMS

    assert "sunlight_2015.document_accessibility" not in IN_SCOPE_ITEMS

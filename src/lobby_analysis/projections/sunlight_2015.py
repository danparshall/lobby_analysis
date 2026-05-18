"""Sunlight 2015 (Lobbying Disclosure Scorecard) projection.

Implements per-item projections for the 4 in-scope Sunlight 2015 items:

* item 1 ``sunlight_2015.lobbyist_activity`` (4-tier, -1..2)
* item 2 ``sunlight_2015.expenditure_transparency`` (4-tier, -1..2)
* item 3 ``sunlight_2015.expenditure_reporting_thresholds`` (2-tier, -1..0)
* item 5 ``sunlight_2015.lobbyist_compensation`` (2-tier, -1..0)

Item 4 (``sunlight_2015.document_accessibility``, 5-tier -2..2) is
**excluded** per the 2026-05-07 audit decision (see
``docs/historical/compendium-source-extracts/results/projections/20260507_sunlight_atomic_audit.md``).
The 5-tier ordinal conflates 3-4 sub-features and the -1/-2 tier
descriptors are a documented near-typo. The cell-to-tier function is
not well-defined. Module-level ``EXCLUDED_ITEMS`` carries the
exclusion; ``tests/projections/test_sunlight_2015_aggregation.py``
regression-guards against accidental re-introduction.

**No aggregation.** Sunlight's published ``Total`` (arithmetic sum
across all 5 items) and ``Grade`` (letter, empirically-derived
cutoffs) are NOT reproducible from the 4 in-scope items. The module
intentionally does NOT export ``project_sunlight_2015_total``,
``project_sunlight_2015_grade``, or ``rank_sunlight_2015_states``. The
aggregation-test file regression-guards this.

Spec doc:
``docs/historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md``

Ground-truth file (50 states x 4 in-scope columns = 200 cells, per-state
per-item):

* ``papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv``

CSV cells carry undocumented footnote markers (``*``, ``**``, ``***``,
``^``, ``^^``). The loader strips markers for integer coercion and
preserves marker provenance in a sibling dict.

Conventions internalized by this module:

* **alpha form-type split.** Sunlight item 1 reads the same 3 concepts
  (general_subject_matter / bill_or_action_identifier / position_on_bill)
  off two distinct compendium rows each: one ``lobbyist_reg_form_*``
  side and one ``lobbyist_spending_report_*`` side. The projection ORs
  across the form-type pair before the tier-table lookup.
* **beta AND-projection (forward-looking).** Sunlight item 1
  introduces the 3 ``lobbyist_spending_report_*`` rows that Opheim 1991
  (rubric #6) reads via AND-projection. Keep these row IDs stable;
  Opheim's plan references them by name.
* **collect-once-map-many.** Several rows feed multiple Sunlight items
  (none in this module, but the convention applies in the cross-rubric
  layer).

Spec-doc-to-v2 rename applied (1 row):

* spec doc: ``lobbyist_spending_report_includes_compensation_broken_down_by_client``
* v2:        ``lobbyist_spending_report_includes_compensation_broken_down_by_payer``

Same observable; rename was decision D1/D2/D5 from the 2026-05-13
row-freeze (Open Issue 2 in the original spec landed as ``_by_payer``).
"""

from __future__ import annotations

from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEGAL_AXIS: Final[str] = "legal_availability"

#: Items implemented by this module. Each id matches the Sunlight 2015
#: published item name, lowercased and prefixed by ``sunlight_2015.``.
IN_SCOPE_ITEMS: Final[tuple[str, ...]] = (
    "sunlight_2015.lobbyist_activity",
    "sunlight_2015.expenditure_transparency",
    "sunlight_2015.expenditure_reporting_thresholds",
    "sunlight_2015.lobbyist_compensation",
)

#: Items deliberately not implemented. ``document_accessibility``
#: excluded per 2026-05-07 audit; cell-to-tier function not
#: well-defined.
EXCLUDED_ITEMS: Final[frozenset[str]] = frozenset(
    {"sunlight_2015.document_accessibility"}
)

#: Sentinel returned by per-item helpers when required input cells are
#: missing. Threaded into ``Sunlight2015Score.per_item_scores`` unchanged
#: (the dict value type is ``int | str`` to accommodate both cases).
UNABLE_TO_EVALUATE: Final[Literal["unable_to_evaluate"]] = "unable_to_evaluate"


# ---------------------------------------------------------------------------
# Pydantic score model
# ---------------------------------------------------------------------------


class Sunlight2015Score(BaseModel):
    """A Sunlight 2015 score for one state.

    Carries the 4 in-scope per-item scores plus an oddity-flag dict.
    No total, no grade, no rank: these are not reproducible from the 4
    in-scope items (item 4 excluded). Test file
    ``test_sunlight_2015_aggregation.py`` regression-guards the absence
    of total/grade/rank functions at the module level.
    """

    model_config = ConfigDict(frozen=True)

    state: str
    per_item_scores: dict[str, int | str]
    oddity_flags: dict[str, list[str]]


# ---------------------------------------------------------------------------
# Cell-read helpers
# ---------------------------------------------------------------------------


def _legal(cells: dict[str, Any], row_id: str) -> Any:
    """Return the legal_availability value for a row, or None if missing."""
    cell = cells.get(row_id)
    if cell is None:
        return None
    return cell.get(LEGAL_AXIS)


# ---------------------------------------------------------------------------
# Item 1: lobbyist_activity (4-tier nested, alpha form-type split)
# ---------------------------------------------------------------------------

_ITEM1_REG_ROWS: Final[tuple[str, str, str]] = (
    "lobbyist_reg_form_includes_general_subject_matter",
    "lobbyist_reg_form_includes_bill_or_action_identifier",
    "lobbyist_reg_form_includes_position_on_bill",
)
_ITEM1_SPEND_ROWS: Final[tuple[str, str, str]] = (
    "lobbyist_spending_report_includes_general_subject_matter",
    "lobbyist_spending_report_includes_bill_or_action_identifier",
    "lobbyist_spending_report_includes_position_on_bill",
)


def project_sunlight_item1(
    cells: dict[str, Any],
) -> tuple[int | Literal["unable_to_evaluate"], str | None]:
    """Sunlight item 1: lobbyist_activity (4-tier, -1..2).

    Reads 6 binary cells (3 concepts x 2 form sides). Form-agnostic OR
    collapses each concept-pair, then nested-tier mapping applies. Returns
    ``(UNABLE_TO_EVALUATE, None)`` if any of the 6 required cells is missing.
    """
    for row_id in _ITEM1_REG_ROWS + _ITEM1_SPEND_ROWS:
        if _legal(cells, row_id) is None:
            return UNABLE_TO_EVALUATE, None
    reg = tuple(bool(_legal(cells, r)) for r in _ITEM1_REG_ROWS)
    spend = tuple(bool(_legal(cells, r)) for r in _ITEM1_SPEND_ROWS)
    general = reg[0] or spend[0]
    bill = reg[1] or spend[1]
    position = reg[2] or spend[2]

    # Cascading-downward tier assignment: lowest failing predicate sets
    # the tier. Statutorily expected: general_subject >= bill_id >= position
    # (each higher tier requires the lower predicates). Any violation is an
    # oddity flagged downstream, not silently coerced.
    if not general:
        tier = -1
    elif not bill:
        tier = 0
    elif not position:
        tier = 1
    else:
        tier = 2

    higher_without_lower: list[str] = []
    if (bill or position) and not general:
        higher_without_lower.append(
            "bill_or_action_identifier and/or position_on_bill True while "
            "general_subject_matter False"
        )
    if position and not bill:
        higher_without_lower.append(
            "position_on_bill True while bill_or_action_identifier False"
        )
    oddity = "; ".join(higher_without_lower) if higher_without_lower else None
    return tier, oddity


# ---------------------------------------------------------------------------
# Item 2: expenditure_transparency (4-tier nested with wildcard at top tier)
# ---------------------------------------------------------------------------

_ITEM2_REQUIRED_ROW: Final[str] = "lobbyist_spending_report_required"
_ITEM2_CATEGORIZED_ROW: Final[str] = (
    "lobbyist_spending_report_categorizes_expenses_by_type"
)
_ITEM2_ITEMIZED_ROW: Final[str] = "lobbyist_spending_report_includes_itemized_expenses"


def project_sunlight_item2(
    cells: dict[str, Any],
) -> tuple[int | Literal["unable_to_evaluate"], str | None]:
    """Sunlight item 2: expenditure_transparency (4-tier, -1..2).

    Truth table per spec doc::

        F * * -> -1   (report not required)
        T F F ->  0   (lump total only)
        T T F ->  1   (categorized but not itemized)
        T * T ->  2   (itemized, with or without separate categorization)

    The ``(T, F, T)`` combination — itemization without separate
    categorization — is statutorily implausible (itemization implies
    categorization). Returns tier 2 per the wildcard rule, with a
    non-None oddity flag.
    """
    for row_id in (_ITEM2_REQUIRED_ROW, _ITEM2_CATEGORIZED_ROW, _ITEM2_ITEMIZED_ROW):
        if _legal(cells, row_id) is None:
            return UNABLE_TO_EVALUATE, None
    required = bool(_legal(cells, _ITEM2_REQUIRED_ROW))
    categorized = bool(_legal(cells, _ITEM2_CATEGORIZED_ROW))
    itemized = bool(_legal(cells, _ITEM2_ITEMIZED_ROW))
    if not required:
        return -1, None
    if itemized:
        if not categorized:
            return 2, (
                "itemized True while categorized False (itemization implies "
                "categorization statutorily)"
            )
        return 2, None
    if categorized:
        return 1, None
    return 0, None


# ---------------------------------------------------------------------------
# Item 3: expenditure_reporting_thresholds (2-tier typed cell)
#
# This is the itemization-de-minimis threshold (Sunlight #3's "below
# this amount, individual lines need not be itemized"). It is distinct
# from two neighboring threshold concepts:
#
#   * lobbyist-status threshold:
#       lobbyist_registration_threshold_compensation_dollars
#       (CPI #197 / HG Q2 / Newmark / Opheim / FOCAL scope.2)
#   * filing-de-minimis threshold (whether a registered lobbyist's
#     activity even triggers filing): a separate PRI D1 row.
#
# v2's row id is correctly scoped; do not collapse with either neighbor.
# ---------------------------------------------------------------------------

_ITEM3_ROW: Final[str] = "lobbyist_filing_itemization_de_minimis_threshold_dollars"


def project_sunlight_item3(
    cells: dict[str, Any],
) -> tuple[int | Literal["unable_to_evaluate"], str | None]:
    """Sunlight item 3: expenditure_reporting_thresholds (2-tier, -1..0).

    threshold IS NULL OR threshold == 0  ->   0
    threshold > 0                        ->  -1

    Returns ``(UNABLE_TO_EVALUATE, None)`` only when the row id is not a
    key in ``cells``. A row present with ``legal_availability=None``
    means "no threshold defined in law" and projects to tier 0.
    """
    if _ITEM3_ROW not in cells:
        return UNABLE_TO_EVALUATE, None
    threshold = cells[_ITEM3_ROW].get(LEGAL_AXIS)
    if threshold is None or threshold == 0:
        return 0, None
    return -1, None


# ---------------------------------------------------------------------------
# Item 5: lobbyist_compensation (2-tier OR over 3 binary cells)
# ---------------------------------------------------------------------------

_ITEM5_TOTAL_ROW: Final[str] = "lobbyist_spending_report_includes_total_compensation"
_ITEM5_BREAKDOWN_ROW: Final[str] = (
    "lobbyist_spending_report_includes_compensation_broken_down_by_payer"
)
_ITEM5_REGFORM_ROW: Final[str] = "lobbyist_reg_form_includes_compensation"


def project_sunlight_item5(
    cells: dict[str, Any],
) -> tuple[int | Literal["unable_to_evaluate"], str | None]:
    """Sunlight item 5: lobbyist_compensation (2-tier, -1..0).

    Form-agnostic OR over 3 disclosure modes. Any compensation
    observable disclosed -> 0; none -> -1. No statutory implausibility
    among the three modes, so no oddity flag.
    """
    for row_id in (_ITEM5_TOTAL_ROW, _ITEM5_BREAKDOWN_ROW, _ITEM5_REGFORM_ROW):
        if _legal(cells, row_id) is None:
            return UNABLE_TO_EVALUATE, None
    disclosed = any(
        bool(_legal(cells, r))
        for r in (_ITEM5_TOTAL_ROW, _ITEM5_BREAKDOWN_ROW, _ITEM5_REGFORM_ROW)
    )
    return (0, None) if disclosed else (-1, None)

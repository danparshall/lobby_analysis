"""Newmark 2005 (state lobbying regulation measure) projection.

Implements per-item projections for the 14 disclosure-only in-scope
Newmark 2005 items:

* 7 ``def_*`` items (definitions battery; max sum 7)
* 1 ``freq_reporting_more_than_annual`` item (frequency battery; max 1)
* 6 ``disc_*`` items (disclosure battery; max sum 6)

Maximum reproducible partial = 14 of Newmark's published 0-18 ``index.total``.

**Excluded** per the disclosure-only Phase B qualifier:

* 4 ``prohib_*`` items (campaign-contribution prohibitions, excessive-
  expenditure prohibition, solicitation prohibition).
* 1 ``penalty_stringency_2003`` 2003-only ordinal add-on (enforcement-
  side, paper-coded directly from state codes — no transparent rubric).

**No ``index.total`` aggregation, no sub-aggregate APIs**. Newmark 2005
publishes only per-state totals in Table 1 (across 6 panels: 1990-91,
1994-95, 1996-97, 2000-01, 2002, 2003). It does NOT publish
sub-aggregates per state. Exposing ``def_section_total_partial`` or
``disclosure_section_total_partial`` would smuggle an API that claims
reproducibility against unpublished data. The module intentionally
exposes only ``per_item_scores``; tests can compute the partial sum
themselves for the weak-inequality check
(``sum(in_scope_items) <= published_index_total``).

Spec doc:
``docs/historical/compendium-source-extracts/results/projections/newmark_2005_projection_mapping.md``

**Reuse from ``newmark_2017``** (this module imports):

* ``project_gifts_actor_agnostic_or`` — same observable, identical
  helper. Newmark 2005's ``disc_expenditures_benefiting_officials``
  item and Newmark 2017's ``disclosure.expenditures_benefiting_officials``
  item both read the actor-agnostic OR.
* The 3 typed-cell threshold rows + ``def_actor_class_*`` rows + 1 NEW
  disclosure row (``lobbyist_spending_report_includes_total_expenditures``).
  Compendium-row reuse is 14 of 14 — zero new rows introduced.

**NEW helper introduced here**:

* ``project_cadence_more_than_annual_or`` — 8-cell OR over
  lobbyist/principal × {monthly, quarterly, triannual, semiannual}
  cadence cells. Newmark 2005's ``freq_reporting_more_than_annual``
  reads this. The ``_annual`` and ``_other`` cadence cells are NOT in
  the read set — "annual" doesn't satisfy ">annual".

**Structural delta from Newmark 2017**:

* Newmark 2005 has a ``freq_reporting_more_than_annual`` item; Newmark
  2017 dropped it. The freq item reads 8 cadence cells (1-item × 8 OR).
* Newmark 2005 has 6 disclosure items; Newmark 2017 has 7. The 2017
  ``disclosure.contributions_from_others`` item is NOT in Newmark 2005
  — the 2017 mapping's speculation of a 2005 parallel was falsified by
  the 2005 mapping work. Regression-guarded.

Spec-doc-to-v2 renames applied (15 rows):

* 7 inherited from Newmark 2017 (see that module's docstring).
* 8 cadence renames: ``*_report_cadence_*`` -> ``*_spending_report_cadence_*``
  (4 lobbyist + 4 principal cells).

Ground-truth status: Newmark publishes Table 1 per-state index totals
(50 states × 6 panels = 300 cells). No CSV extraction exists in the
repo yet; the 50-state weak-inequality validation harness is deferred
until that extraction lands. Per-item helper tests + aggregation tests
cover the projection logic.
"""

from __future__ import annotations

from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict

from lobby_analysis.projections.newmark_2017 import project_gifts_actor_agnostic_or


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEGAL_AXIS: Final[str] = "legal_availability"

#: Items implemented by this module. Each id matches the Newmark 2005
#: indicator id from ``items_Newmark2005.tsv``, prefixed by ``newmark_2005.``.
IN_SCOPE_ITEMS: Final[tuple[str, ...]] = (
    # Definitions battery (7)
    "newmark_2005.def_legislative_lobbying",
    "newmark_2005.def_administrative_agency_lobbying",
    "newmark_2005.def_elected_officials_as_lobbyists",
    "newmark_2005.def_public_employees_as_lobbyists",
    "newmark_2005.def_compensation_standard",
    "newmark_2005.def_expenditure_standard",
    "newmark_2005.def_time_standard",
    # Frequency battery (1)
    "newmark_2005.freq_reporting_more_than_annual",
    # Disclosure battery (6 — NOT 7; ``contributions_from_others`` is
    # Newmark-2017-distinctive, not in Newmark 2005.)
    "newmark_2005.disc_legislative_admin_action_to_influence",
    "newmark_2005.disc_expenditures_benefiting_officials",
    "newmark_2005.disc_compensation_by_employer",
    "newmark_2005.disc_total_compensation",
    "newmark_2005.disc_categories_of_expenditures",
    "newmark_2005.disc_total_expenditures",
)

#: Items deliberately not implemented per the disclosure-only Phase B
#: qualifier. 4 ``prohib_*`` items + 1 ``penalty_stringency_2003`` add-on.
EXCLUDED_ITEMS: Final[frozenset[str]] = frozenset(
    {
        "newmark_2005.prohib_campaign_contrib_any_time",
        "newmark_2005.prohib_campaign_contrib_during_session",
        "newmark_2005.prohib_expenditures_over_threshold",
        "newmark_2005.prohib_solicitation_by_officials",
        "newmark_2005.penalty_stringency_2003",
    }
)

#: Sentinel returned by per-item helpers when required input cells are
#: missing.
UNABLE_TO_EVALUATE: Final[Literal["unable_to_evaluate"]] = "unable_to_evaluate"


# ---------------------------------------------------------------------------
# Spec table for single-row items (11 items)
# ---------------------------------------------------------------------------

_BINARY: Final[str] = "binary"
_TYPED: Final[str] = "typed_is_not_null"

# (item_id, v2_row_id, kind) for the 11 single-row items. The gifts OR
# item dispatches to ``project_gifts_actor_agnostic_or``; the freq item
# dispatches to ``project_cadence_more_than_annual_or`` (both spec'd
# out-of-table because they read multiple rows).
_SINGLE_ROW_SPEC: Final[tuple[tuple[str, str, str], ...]] = (
    # Definitions battery
    ("newmark_2005.def_legislative_lobbying", "def_target_legislative_branch", _BINARY),
    ("newmark_2005.def_administrative_agency_lobbying", "def_target_executive_agency", _BINARY),
    ("newmark_2005.def_elected_officials_as_lobbyists", "def_actor_class_elected_officials", _BINARY),
    ("newmark_2005.def_public_employees_as_lobbyists", "def_actor_class_public_employees", _BINARY),
    ("newmark_2005.def_compensation_standard", "lobbyist_registration_threshold_compensation_dollars", _TYPED),
    ("newmark_2005.def_expenditure_standard", "lobbyist_registration_threshold_expenditure_dollars", _TYPED),
    ("newmark_2005.def_time_standard", "lobbyist_registration_threshold_time_percent", _TYPED),
    # Disclosure battery (single-row items)
    ("newmark_2005.disc_legislative_admin_action_to_influence", "lobbyist_spending_report_includes_general_subject_matter", _BINARY),
    ("newmark_2005.disc_compensation_by_employer", "lobbyist_spending_report_includes_compensation_broken_down_by_payer", _BINARY),
    ("newmark_2005.disc_total_compensation", "lobbyist_spending_report_includes_total_compensation", _BINARY),
    ("newmark_2005.disc_categories_of_expenditures", "lobbyist_spending_report_categorizes_expenses_by_type", _BINARY),
    ("newmark_2005.disc_total_expenditures", "lobbyist_spending_report_includes_total_expenditures", _BINARY),
)


_SPEC_BY_ITEM: Final[dict[str, tuple[str, str]]] = {
    item_id: (row, kind) for item_id, row, kind in _SINGLE_ROW_SPEC
}


# Special-dispatch items (multi-row helpers).
_GIFTS_ITEM: Final[str] = "newmark_2005.disc_expenditures_benefiting_officials"
_FREQ_ITEM: Final[str] = "newmark_2005.freq_reporting_more_than_annual"


# 8 cadence cells read by the freq helper. ``_annual`` and ``_other``
# cadence cells are NOT in the set — "annual" doesn't satisfy ">annual",
# and "other" is ambiguous.
_CADENCE_SUB_ANNUAL_ROWS: Final[tuple[str, ...]] = (
    "lobbyist_spending_report_cadence_includes_monthly",
    "lobbyist_spending_report_cadence_includes_quarterly",
    "lobbyist_spending_report_cadence_includes_triannual",
    "lobbyist_spending_report_cadence_includes_semiannual",
    "principal_spending_report_cadence_includes_monthly",
    "principal_spending_report_cadence_includes_quarterly",
    "principal_spending_report_cadence_includes_triannual",
    "principal_spending_report_cadence_includes_semiannual",
)


# ---------------------------------------------------------------------------
# Pydantic score model
# ---------------------------------------------------------------------------


class Newmark2005Score(BaseModel):
    """A Newmark 2005 score for one state on one panel.

    Carries the 14 in-scope per-item scores and the panel label. **No**
    sub-aggregate fields and **no** ``index_total`` field — Newmark 2005
    publishes only per-state totals in Table 1 (across 6 panels), not
    per-state sub-aggregates. Exposing sub-aggregates would smuggle an
    API that claims reproducibility against unpublished data.
    """

    model_config = ConfigDict(frozen=True)

    state: str
    panel: str
    per_item_scores: dict[str, int | str]


# ---------------------------------------------------------------------------
# Per-item helpers
# ---------------------------------------------------------------------------


def _project_binary(cells: dict[str, Any], row_id: str) -> int | Literal["unable_to_evaluate"]:
    """``cell == TRUE -> 1; FALSE -> 0; missing or None -> unable_to_evaluate``."""
    cell = cells.get(row_id)
    if cell is None:
        return UNABLE_TO_EVALUATE
    value = cell.get(LEGAL_AXIS)
    if value is None:
        return UNABLE_TO_EVALUATE
    return 1 if value else 0


def _project_typed_is_not_null(
    cells: dict[str, Any], row_id: str
) -> int | Literal["unable_to_evaluate"]:
    """``IS NOT NULL`` semantics on a typed cell. See ``newmark_2017`` for the
    full rule."""
    if row_id not in cells:
        return UNABLE_TO_EVALUATE
    value = cells[row_id].get(LEGAL_AXIS)
    if value is None or value == "":
        return 0
    return 1


def project_cadence_more_than_annual_or(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """Frequency of reporting: more frequently than once per year.

    OR over 8 cadence cells: ``{lobbyist, principal}`` ×
    ``{monthly, quarterly, triannual, semiannual}``. Newmark 2005's
    ``freq_reporting_more_than_annual`` reads this; the rubric returns 1
    if any sub-annual cadence is required somewhere in the disclosure
    regime.

    The ``_annual`` and ``_other`` cadence cells are NOT in the read set
    — "annual" is the negative case, "other" is ambiguous.

    Strict missing-cell semantics: if any of the 8 cells is missing or
    has axis None, returns ``"unable_to_evaluate"`` UNLESS at least one
    other cell is known TRUE (which short-circuits the OR to 1). This
    matches Newmark 2017's gifts-OR semantics: a known TRUE wins; a known
    all-FALSE wins; anything else is unknown.

    Introduced in this module rather than ``newmark_2017`` (which has no
    frequency item). Opheim 1991 will read the same cells at a finer cut
    (monthly-only); a separate Opheim helper applies there.
    """
    values: list[Any] = []
    for row_id in _CADENCE_SUB_ANNUAL_ROWS:
        cell = cells.get(row_id)
        values.append(cell.get(LEGAL_AXIS) if cell is not None else None)
    if any(v is True for v in values):
        return 1
    if all(v is False for v in values):
        return 0
    return UNABLE_TO_EVALUATE


# ---------------------------------------------------------------------------
# Per-item dispatcher
# ---------------------------------------------------------------------------


def project_newmark_2005_item(
    item_id: str, cells: dict[str, Any]
) -> int | Literal["unable_to_evaluate"]:
    """Project one Newmark 2005 atomic item from v2 compendium cells.

    Dispatches: single-row binary, single-row typed-IS-NOT-NULL, the
    gifts actor-agnostic OR helper (imported from ``newmark_2017``), or
    the cadence-more-than-annual OR helper. Raises ``KeyError`` if
    ``item_id`` is not an in-scope Newmark 2005 item.
    """
    if item_id == _GIFTS_ITEM:
        return project_gifts_actor_agnostic_or(cells)
    if item_id == _FREQ_ITEM:
        return project_cadence_more_than_annual_or(cells)
    row, kind = _SPEC_BY_ITEM[item_id]  # KeyError on unknown item
    if kind == _BINARY:
        return _project_binary(cells, row)
    if kind == _TYPED:
        return _project_typed_is_not_null(cells, row)
    raise AssertionError(f"unknown spec kind {kind!r} for {item_id!r}")


# ---------------------------------------------------------------------------
# Top-level projection
# ---------------------------------------------------------------------------


def project_newmark_2005(
    cells: dict[str, Any], state: str, panel: str
) -> Newmark2005Score:
    """Project Newmark 2005 per-item scores for one (state, panel) pair.

    ``panel`` is the published panel label — one of ``"1990-91"``,
    ``"1994-95"``, ``"1996-97"``, ``"2000-01"``, ``"2002"``, ``"2003"``.
    It's threaded into the returned score for cross-panel comparisons
    but does NOT change the projection logic (statute snapshots for the
    panel are encoded in the ``cells`` dict the caller passes in).

    Returns a frozen ``Newmark2005Score`` with 14 per-item scores
    (``0``, ``1``, or ``"unable_to_evaluate"``). No sub-aggregate fields,
    no ``index_total`` — Newmark 2005 publishes only per-state totals,
    not sub-aggregates, and the 0-18 total requires 5 excluded items.
    """
    per_item: dict[str, int | str] = {
        item_id: project_newmark_2005_item(item_id, cells) for item_id in IN_SCOPE_ITEMS
    }
    return Newmark2005Score(state=state, panel=panel, per_item_scores=per_item)

"""Newmark 2017 (state lobbying regulation index, 2015 vintage) projection.

Implements per-item projections for the 14 disclosure-only in-scope
Newmark 2017 items:

* 7 ``def.*`` items (definitions battery; max sum 7)
* 7 ``disclosure.*`` items (registration/reporting disclosure; max sum 7)

Plus the two sub-aggregate totals that Newmark publishes per-state in
Table 2 of the paper (``def.section_total`` and
``disclosure.section_total``, each 0-7).

**Excluded** per the disclosure-only Phase B qualifier: the 5
``prohib.*`` atomic items (campaign-contribution prohibitions,
solicitation prohibition, contingent-compensation prohibition,
revolving-door restriction). These are restrictions on conduct, not
disclosure requirements; they re-enter scope in a later round.

**No ``index.total`` aggregation**. Newmark's published 0-19 total is
``def.section_total + prohib.section_total + disclosure.section_total``
and cannot be reproduced without the 5 excluded ``prohib.*`` cells.
The module intentionally does NOT export ``project_newmark_2017_index_total``;
``tests/projections/test_newmark_2017_aggregation.py`` regression-guards
this absence.

Spec doc:
``docs/historical/compendium-source-extracts/results/projections/newmark_2017_projection_mapping.md``

Conventions:

* **Binary items**: ``cell.legal_availability == TRUE -> 1; FALSE -> 0;
  missing/None -> "unable_to_evaluate"``.
* **Typed-cell items (3 def.*_standard items)**: ``IS NOT NULL`` semantics
  on a typed cell — non-empty value (including ``Decimal("0")``) projects
  to 1; ``None`` / empty-string projects to 0; row missing from cells dict
  projects to ``"unable_to_evaluate"``.
* **Gifts actor-agnostic OR** (1 disclosure item): OR over
  ``lobbyist_spending_report_*`` and ``principal_spending_report_*``
  gifts/entertainment/transport/lodging rows. Helper
  ``project_gifts_actor_agnostic_or`` is exported (Newmark 2005 reuses it).
* **No-variation items not special-cased**: ``def.legislative_lobbying``
  and ``disclosure.expenditures_benefiting_officials`` are empirically
  uniform across 50 states in 2015 (per Newmark's Table 3 footnote), but
  the projection reads their cells honestly. A counterfactual state with
  ``def_target_legislative_branch == False`` projects to 0, not coerced
  to 1.

Spec-doc-to-v2 renames applied (7 rows):

* ``compensation_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_compensation_dollars``
* ``expenditure_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_expenditure_dollars``
* ``time_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_time_percent``
* ``lobbyist_report_includes_gifts_entertainment_transport_lodging`` →
  ``lobbyist_spending_report_includes_gifts_entertainment_transport_lodging``
* ``principal_report_includes_gifts_entertainment_transport_lodging`` →
  ``principal_spending_report_includes_gifts_entertainment_transport_lodging``
* ``lobbyist_spending_report_includes_compensation_broken_down_by_client`` →
  ``lobbyist_spending_report_includes_compensation_broken_down_by_payer``
* ``lobbyist_or_principal_report_includes_contributions_received_for_lobbying`` →
  ``lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying``

Ground-truth status: Newmark publishes Table 2 sub-aggregates per state
in the paper PDF. No CSV extraction exists in the repo yet; the 50-state
sub-aggregate validation harness is deferred until that extraction lands.
Per-item helper tests + aggregation tests cover the projection logic.
"""

from __future__ import annotations

from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEGAL_AXIS: Final[str] = "legal_availability"

#: Items implemented by this module. Each id matches the Newmark 2017
#: published item name, prefixed by ``newmark_2017.``.
IN_SCOPE_ITEMS: Final[tuple[str, ...]] = (
    # Definitions battery (7)
    "newmark_2017.def.legislative_lobbying",
    "newmark_2017.def.administrative_agency_lobbying",
    "newmark_2017.def.elective_officials_as_lobbyists",
    "newmark_2017.def.public_employees_as_lobbyists",
    "newmark_2017.def.compensation_standard",
    "newmark_2017.def.expenditure_standard",
    "newmark_2017.def.time_standard",
    # Disclosure battery (7)
    "newmark_2017.disclosure.influence_legislation_or_admin",
    "newmark_2017.disclosure.expenditures_benefiting_officials",
    "newmark_2017.disclosure.compensation_by_employer",
    "newmark_2017.disclosure.total_compensation",
    "newmark_2017.disclosure.categories_of_expenditures",
    "newmark_2017.disclosure.total_expenditures",
    "newmark_2017.disclosure.contributions_from_others",
)

#: Items deliberately not implemented per the disclosure-only Phase B
#: qualifier. All 5 ``prohib.*`` items are restrictions on conduct, not
#: disclosure requirements.
EXCLUDED_ITEMS: Final[frozenset[str]] = frozenset(
    {
        "newmark_2017.prohib.contributions_anytime",
        "newmark_2017.prohib.contributions_during_session",
        "newmark_2017.prohib.solicitation_by_officials",
        "newmark_2017.prohib.contingent_compensation",
        "newmark_2017.prohib.revolving_door",
    }
)

#: Sentinel returned by per-item helpers when a required input cell is
#: missing (row absent from cells dict, or binary-cell axis value is None).
UNABLE_TO_EVALUATE: Final[Literal["unable_to_evaluate"]] = "unable_to_evaluate"


# ---------------------------------------------------------------------------
# Spec table
#
# (item_id, v2_row_id, kind) where kind in {"binary", "typed_is_not_null"}.
# The gifts actor-agnostic OR and contributions-from-others items are
# spec'd out-of-table because they read multiple rows or carry distinct
# documentation. The 11 single-row items live here.
# ---------------------------------------------------------------------------

_BINARY: Final[str] = "binary"
_TYPED: Final[str] = "typed_is_not_null"

_SINGLE_ROW_SPEC: Final[tuple[tuple[str, str, str], ...]] = (
    # Definitions battery
    ("newmark_2017.def.legislative_lobbying", "def_target_legislative_branch", _BINARY),
    ("newmark_2017.def.administrative_agency_lobbying", "def_target_executive_agency", _BINARY),
    ("newmark_2017.def.elective_officials_as_lobbyists", "def_actor_class_elected_officials", _BINARY),
    ("newmark_2017.def.public_employees_as_lobbyists", "def_actor_class_public_employees", _BINARY),
    ("newmark_2017.def.compensation_standard", "lobbyist_registration_threshold_compensation_dollars", _TYPED),
    ("newmark_2017.def.expenditure_standard", "lobbyist_registration_threshold_expenditure_dollars", _TYPED),
    ("newmark_2017.def.time_standard", "lobbyist_registration_threshold_time_percent", _TYPED),
    # Disclosure battery (single-row items)
    ("newmark_2017.disclosure.influence_legislation_or_admin", "lobbyist_spending_report_includes_general_subject_matter", _BINARY),
    ("newmark_2017.disclosure.compensation_by_employer", "lobbyist_spending_report_includes_compensation_broken_down_by_payer", _BINARY),
    ("newmark_2017.disclosure.total_compensation", "lobbyist_spending_report_includes_total_compensation", _BINARY),
    ("newmark_2017.disclosure.categories_of_expenditures", "lobbyist_spending_report_categorizes_expenses_by_type", _BINARY),
    ("newmark_2017.disclosure.total_expenditures", "lobbyist_spending_report_includes_total_expenditures", _BINARY),
    ("newmark_2017.disclosure.contributions_from_others", "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying", _BINARY),
)


# Lookup table keyed by item id.
_SPEC_BY_ITEM: Final[dict[str, tuple[str, str]]] = {
    item_id: (row, kind) for item_id, row, kind in _SINGLE_ROW_SPEC
}


# Gifts actor-agnostic OR reads these two rows.
_GIFTS_ITEM: Final[str] = "newmark_2017.disclosure.expenditures_benefiting_officials"
_GIFTS_LOBBYIST_ROW: Final[str] = (
    "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging"
)
_GIFTS_PRINCIPAL_ROW: Final[str] = (
    "principal_spending_report_includes_gifts_entertainment_transport_lodging"
)


# ---------------------------------------------------------------------------
# Pydantic score model
# ---------------------------------------------------------------------------


class Newmark2017Score(BaseModel):
    """A Newmark 2017 score for one state.

    Carries the 14 in-scope per-item scores plus the two reproducible
    Table-2 sub-aggregates (``def_section_total`` and
    ``disclosure_section_total``, each 0-7). No ``index_total`` field —
    Newmark's 0-19 published total requires the 5 excluded ``prohib.*``
    cells and is regression-guarded absent at the module level.

    Sub-aggregates are computed only when all 7 items in the battery
    project to concrete integers. If any item in the battery is
    ``"unable_to_evaluate"``, the sub-aggregate is None.
    """

    model_config = ConfigDict(frozen=True)

    state: str
    per_item_scores: dict[str, int | str]
    def_section_total: int | None
    disclosure_section_total: int | None


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
    """``IS NOT NULL`` semantics on a typed cell.

    Row absent from cells dict -> ``"unable_to_evaluate"`` (we don't know
    whether a threshold exists). Row present with axis value None or
    empty-string -> 0 (no threshold defined). Row present with any other
    value, including ``Decimal("0")`` or ``"0"`` -> 1 (a threshold of $0
    is still a threshold that exists in law).
    """
    if row_id not in cells:
        return UNABLE_TO_EVALUATE
    value = cells[row_id].get(LEGAL_AXIS)
    if value is None or value == "":
        return 0
    return 1


def project_gifts_actor_agnostic_or(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """Disclosure: expenditures benefiting public officials or employees.

    OR over the lobbyist-side and principal-side gifts/entertainment/
    transport/lodging rows. Newmark's framing is actor-agnostic
    ("expenditures benefiting officials" — somewhere in the disclosure
    regime), so the OR is the coarsest correct reading.

    Returns ``"unable_to_evaluate"`` if BOTH actor-side rows are missing
    or have None axis values. If one side is present (with True or
    False) and the other is missing, the present side determines the
    answer — a known TRUE on either side projects to 1; a known FALSE on
    one side with the other missing projects to ``"unable_to_evaluate"``
    (we cannot rule out the other side disclosing).

    Exported by name so Newmark 2005 can import and reuse this helper
    verbatim (its ``disc_expenditures_benefiting_officials`` item reads
    the same observable).
    """
    lobbyist = cells.get(_GIFTS_LOBBYIST_ROW)
    principal = cells.get(_GIFTS_PRINCIPAL_ROW)
    lob_val = lobbyist.get(LEGAL_AXIS) if lobbyist is not None else None
    princ_val = principal.get(LEGAL_AXIS) if principal is not None else None
    # If either side is known TRUE, the OR is TRUE.
    if lob_val is True or princ_val is True:
        return 1
    # Both sides known FALSE -> OR is FALSE.
    if lob_val is False and princ_val is False:
        return 0
    # Otherwise at least one side is unknown and no known TRUE rescues us.
    return UNABLE_TO_EVALUATE


# ---------------------------------------------------------------------------
# Per-item dispatcher
# ---------------------------------------------------------------------------


def project_newmark_2017_item(
    item_id: str, cells: dict[str, Any]
) -> int | Literal["unable_to_evaluate"]:
    """Project one Newmark 2017 atomic item from v2 compendium cells.

    Dispatches: single-row binary, single-row typed-IS-NOT-NULL, or the
    gifts actor-agnostic OR helper. Raises ``KeyError`` if ``item_id`` is
    not an in-scope Newmark 2017 item.
    """
    if item_id == _GIFTS_ITEM:
        return project_gifts_actor_agnostic_or(cells)
    row, kind = _SPEC_BY_ITEM[item_id]  # KeyError on unknown item
    if kind == _BINARY:
        return _project_binary(cells, row)
    if kind == _TYPED:
        return _project_typed_is_not_null(cells, row)
    raise AssertionError(f"unknown spec kind {kind!r} for {item_id!r}")


# ---------------------------------------------------------------------------
# Top-level projection
# ---------------------------------------------------------------------------


_DEF_BATTERY: Final[tuple[str, ...]] = tuple(
    item for item in IN_SCOPE_ITEMS if item.startswith("newmark_2017.def.")
)
_DISCLOSURE_BATTERY: Final[tuple[str, ...]] = tuple(
    item for item in IN_SCOPE_ITEMS if item.startswith("newmark_2017.disclosure.")
)


def _sum_battery(
    per_item: dict[str, int | str], battery: tuple[str, ...]
) -> int | None:
    """Sum a battery's per-item scores; return None if any item is the sentinel."""
    total = 0
    for item_id in battery:
        score = per_item[item_id]
        if isinstance(score, str):
            return None
        total += score
    return total


def project_newmark_2017(cells: dict[str, Any], state: str) -> Newmark2017Score:
    """Project Newmark 2017 per-item scores + 2 sub-aggregates for one state.

    Returns a frozen ``Newmark2017Score`` with 14 per-item scores
    (``0``, ``1``, or ``"unable_to_evaluate"``) and the two reproducible
    Table-2 sub-aggregates. No ``index_total`` — the 0-19 headline
    requires 5 excluded ``prohib.*`` cells and is regression-guarded
    absent in ``tests/projections/test_newmark_2017_aggregation.py``.
    """
    per_item: dict[str, int | str] = {
        item_id: project_newmark_2017_item(item_id, cells) for item_id in IN_SCOPE_ITEMS
    }
    return Newmark2017Score(
        state=state,
        per_item_scores=per_item,
        def_section_total=_sum_battery(per_item, _DEF_BATTERY),
        disclosure_section_total=_sum_battery(per_item, _DISCLOSURE_BATTERY),
    )

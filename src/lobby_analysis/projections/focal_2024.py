"""FOCAL 2024 (Lacy-Nichols cross-national lobbying-disclosure framework).

Projection over v2 compendium cells for the 49 in-scope 2024 indicators +
1 2025-only addition. FOCAL was published as a cross-national framework
(28 jurisdictions in L-N 2025); the **Federal US LDA** row is the
load-bearing per-item validation anchor (target 81 raw / 180 max = 45%
after excluding ``revolving_door.2``).

For US states there is **no per-state FOCAL ground truth** — FOCAL has not
been applied to US states by anyone (other than this project). State-level
validation runs through cross-rubric agreement, not direct FOCAL match.

This module is built **incrementally across 4 sub-plans** all converging
on the same ``_SPEC_BY_ITEM`` dispatcher dict:

1. **Legal core (this plan)** — 26 items: scope 4 + descriptors 6 +
   relationships 4+1 + revolving_door 1 + financials 11. Module skeleton,
   score model, ground-truth loader stub.
2. **Contact log** — 11 items (companion plan).
3. **Openness + timeliness** — 12 items (companion plan).
4. **Aggregation** — weighted sum + US LDA federal validation + ranking
   (companion plan); ships ``project_focal_2024(cells, jurisdiction, vintage)``.

Plan: ``docs/active/phase-c-projection-tdd/plans/20260518_focal_2024_legal_core_plan.md``
Spec doc: ``docs/historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md``

Conventions:

* **Binary items (2-tier)**: ``cell.legal_availability == TRUE -> 2;
  FALSE -> 0; missing or None -> "unable_to_evaluate"``. Note the
  *2* (not 1) — FOCAL's published per-item granularity is 0/1/2,
  with TRUE collapsing to the full-tier max (2) under the YAGNI ruling
  (OQ3/OQ4) that documented "partly" sub-tiers are not extractable
  from v2 binary cells.
* **Typed-cell IS NOT NULL items**: any non-empty typed value (including
  ``Decimal("0")`` or a non-empty dict) projects to 2; ``None`` /
  empty-string projects to 0; row absent projects to
  ``"unable_to_evaluate"``.
* **Named compound helpers** for the 6 multi-cell items: scope.1, scope.2,
  scope.3, scope.4, financials.6, financials.10 (added in later batteries).
* **Vintage gating**: ``relationships.0`` (2025-only "Lobbyist list") is
  scored only when ``vintage >= 2025``; for earlier vintages the dispatcher
  refuses the item via ``KeyError`` (the spec table doesn't carry it for
  pre-2025 vintages — selected by the top-level projector in Plan 4).

Known systematic over/under-scoring channels (YAGNI partly-tier collapse,
documented in the plan's OQ3/OQ4):

* descriptors.1, .2, .4: FOCAL "P=some entries incomplete" tier collapses
  to binary; states with incomplete disclosure project as 2 (over-score)
  or 0 (under-score) per the binary cell.
* relationships.4: FOCAL distinguishes "Y/N only" (P=1) from "with detail"
  (Y=2); v2 has the binary cell only. Binary read projects to 2 if TRUE.

Tolerance budget for Federal US LDA target (81 raw points): ±15 raw on
the 180-max scale per the aggregation plan (Plan 4 owns the validation
harness).

Spec-doc-to-v2 renames applied (legal core; 16 of 17 — relationships.0
rename is also new this session):

* ``compensation_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_compensation_dollars``
* ``expenditure_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_expenditure_dollars``
* ``time_threshold_for_lobbyist_registration`` →
  ``lobbyist_registration_threshold_time_percent``
* ``lobbyist_definition_included_actor_types`` →
  ``def_lobbyist_actor_types``
* ``lobbying_definition_included_activity_types`` →
  ``def_lobbying_activity_types``
* ``def_target_legislative_or_executive_staff`` SPLIT →
  ``def_target_legislative_staff`` + ``def_target_executive_staff``
* ``lobbyist_disclosure_includes_employment_type`` →
  ``lobbyist_reg_form_includes_employment_type``
* ``lobbyist_report_includes_principal_names`` →
  ``lobbyist_spending_report_includes_principal_names``
* ``principal_or_lobbyist_reg_form_includes_member_or_sponsor_names`` →
  ``lobbyist_or_principal_reg_form_includes_member_or_sponsor_names``
  (arg-order normalization: lobbyist first)
* ``lobbyist_disclosure_includes_business_associations_with_officials`` →
  ``lobbyist_reg_form_includes_business_associations_with_officials``
* ``lobbyist_spending_report_includes_compensation_broken_down_by_client`` →
  ``lobbyist_spending_report_includes_compensation_broken_down_by_payer``
* ``lobbyist_report_includes_gifts_entertainment_transport_lodging`` →
  ``lobbyist_spending_report_includes_gifts_entertainment_transport_lodging``
* ``principal_report_includes_gifts_entertainment_transport_lodging`` →
  ``principal_spending_report_includes_gifts_entertainment_transport_lodging``
* ``lobbyist_report_includes_campaign_contributions`` →
  ``lobbyist_spending_report_includes_campaign_contributions``
* ``principal_report_includes_total_expenditures`` →
  ``principal_spending_report_includes_total_expenditures``
* ``lobbyist_or_principal_report_includes_{lobbyist_count_total_and_FTE,
  time_spent_on_lobbying, trade_association_dues_or_sponsorship}`` →
  ``lobbyist_or_principal_spending_report_includes_*``
* ``principal_report_lists_lobbyists_employed`` →
  ``principal_spending_report_lists_lobbyists_employed``
* ``relationships.lobbyist_list_2025`` (plan working name) →
  ``relationships.0`` (L-N 2025 published indicator id; ``focal_2024_indicator_id_map
  = "(new in 2025)"``)
"""

from __future__ import annotations

from typing import Any, Final, Literal


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEGAL_AXIS: Final[str] = "legal_availability"

#: Sentinel returned by per-item helpers when a required input cell is
#: missing (row absent from cells dict, or binary-cell axis value is None).
UNABLE_TO_EVALUATE: Final[Literal["unable_to_evaluate"]] = "unable_to_evaluate"

#: Items deliberately not implemented per the FOCAL-1 user-decision
#: 2026-05-13 (disclosure-only Phase B scope; revolving_door.2 is a state-
#: side meta-publication of an enforcement mechanism, not a disclosure
#: requirement).
EXCLUDED_ITEMS: Final[frozenset[str]] = frozenset({"focal_2024.revolving_door.2"})


# ---------------------------------------------------------------------------
# Spec table
#
# (item_id, v2_row_id, kind) where kind in {"binary", "typed_is_not_null"}.
# Compound items (scope.*, financials.6, financials.10) are dispatched
# out-of-table to named helpers (added in later batteries).
# ---------------------------------------------------------------------------

_BINARY: Final[str] = "binary"
_TYPED_NOT_NULL: Final[str] = "typed_is_not_null"


_SINGLE_ROW_SPEC: Final[tuple[tuple[str, str, str], ...]] = (
    # Descriptors battery (6 items, all 2-tier; OQ3 YAGNI partly collapse)
    ("focal_2024.descriptors.1", "lobbyist_reg_form_includes_lobbyist_full_name", _BINARY),
    ("focal_2024.descriptors.2", "lobbyist_reg_form_includes_lobbyist_contact_details", _BINARY),
    ("focal_2024.descriptors.3", "lobbyist_reg_form_includes_lobbyist_legal_form", _TYPED_NOT_NULL),
    ("focal_2024.descriptors.4", "lobbyist_reg_form_includes_lobbyist_business_id", _BINARY),
    ("focal_2024.descriptors.5", "lobbyist_reg_form_includes_lobbyist_sector", _TYPED_NOT_NULL),
    ("focal_2024.descriptors.6", "lobbyist_reg_form_includes_employment_type", _BINARY),
)


_SPEC_BY_ITEM: Final[dict[str, tuple[str, str]]] = {
    item_id: (row, kind) for item_id, row, kind in _SINGLE_ROW_SPEC
}


# ---------------------------------------------------------------------------
# Per-item helpers
# ---------------------------------------------------------------------------


def _project_binary_2tier(
    cells: dict[str, Any], row_id: str
) -> int | Literal["unable_to_evaluate"]:
    """``cell == TRUE -> 2; FALSE -> 0; missing or None -> unable_to_evaluate``.

    The *2* (not 1) is FOCAL-specific: per-item published granularity is
    0/1/2, but YAGNI collapses the "partly" sub-tier (1) to binary since
    it's not extractable from v2 binary cells (OQ3/OQ4).
    """
    cell = cells.get(row_id)
    if cell is None:
        return UNABLE_TO_EVALUATE
    value = cell.get(LEGAL_AXIS)
    if value is None:
        return UNABLE_TO_EVALUATE
    return 2 if value else 0


def _project_typed_is_not_null_2tier(
    cells: dict[str, Any], row_id: str
) -> int | Literal["unable_to_evaluate"]:
    """``IS NOT NULL`` semantics on a typed cell, 2-tier.

    Row absent -> ``"unable_to_evaluate"`` (we don't know whether the
    state's regime requires this disclosure). Row present with axis value
    ``None`` or empty-string -> 0. Row present with any other value
    (including ``Decimal("0")`` or a non-empty dict) -> 2.
    """
    if row_id not in cells:
        return UNABLE_TO_EVALUATE
    value = cells[row_id].get(LEGAL_AXIS)
    if value is None or value == "":
        return 0
    return 2


# ---------------------------------------------------------------------------
# Per-item dispatcher
# ---------------------------------------------------------------------------


def project_focal_2024_item(
    item_id: str, cells: dict[str, Any]
) -> int | Literal["unable_to_evaluate"]:
    """Project one FOCAL 2024 atomic item from v2 compendium cells.

    Raises ``KeyError`` on:

    * unknown ``item_id`` (not in ``_SPEC_BY_ITEM`` and not a known
      compound helper),
    * excluded items (``focal_2024.revolving_door.2``),
    * vintage-gated items called outside their vintage window
      (e.g. ``focal_2024.relationships.0`` for ``vintage=2024``;
      dispatcher signature gains a ``vintage`` arg when the relationships
      battery lands).

    Compound helpers (scope.*, financials.6, financials.10) are dispatched
    inline as their respective batteries land.
    """
    # Compound helpers will be inserted here as later batteries land.
    row, kind = _SPEC_BY_ITEM[item_id]  # KeyError on unknown
    if kind == _BINARY:
        return _project_binary_2tier(cells, row)
    if kind == _TYPED_NOT_NULL:
        return _project_typed_is_not_null_2tier(cells, row)
    raise AssertionError(f"unknown spec kind {kind!r} for {item_id!r}")

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

1. **Legal core** (landed 2026-05-22) — 27 items: scope 4 + descriptors 6 +
   relationships 4+1 + revolving_door 1 + financials 11. Module skeleton,
   score model, ground-truth loader stub.
2. **Contact log** (landed 2026-05-22) — 11 items: .1–.10 single-row
   (.6 typed enum, rest binary) + .11 OR-pair across reg_form +
   spending_report sides for the bill-id α form-type split.
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
* contact_log.1, .3, .9, .11: FOCAL "P=some entries incomplete" /
  "vague_or_unclear" / "general_list_not_specific" sub-tiers collapse to
  binary. On Federal US LDA the underlying v2 cells extract as TRUE for
  all four, projecting raw=2 each vs published raw=1; cumulative weighted
  over-scoring on contact_log = +10 points (projected subtotal 20 vs
  published 10). Tolerance absorbed by Plan 4's aggregation harness.

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

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final, Literal

from lobby_analysis.projections.newmark_2017 import (
    UNABLE_TO_EVALUATE as _NEWMARK_UNABLE,
    project_gifts_actor_agnostic_or as _newmark_gifts_or,
)


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
    # Revolving door battery (1 item in scope; revolving_door.2 excluded)
    ("focal_2024.revolving_door.1", "lobbyist_reg_form_includes_lobbyist_prior_public_offices_held", _BINARY),
    # Relationships battery (4 binary + 1 vintage-gated)
    ("focal_2024.relationships.2", "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names", _BINARY),
    ("focal_2024.relationships.3", "lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships", _BINARY),
    ("focal_2024.relationships.4", "lobbyist_reg_form_includes_business_associations_with_officials", _BINARY),
    # relationships.0 (2025-only "Lobbyist list") — also single-row binary, but
    # vintage-gated via _MIN_VINTAGE below.
    ("focal_2024.relationships.0", "principal_spending_report_lists_lobbyists_employed", _BINARY),
    # Financials battery (11 items; 8 single-row + 3 compound).
    # financials.6, .10 are compound helpers dispatched out-of-table below.
    ("focal_2024.financials.1", "lobbyist_spending_report_includes_total_compensation", _BINARY),
    ("focal_2024.financials.2", "lobbyist_spending_report_includes_compensation_broken_down_by_payer", _BINARY),
    ("focal_2024.financials.3", "consultant_lobbyist_report_includes_income_by_source_type", _TYPED_NOT_NULL),
    ("focal_2024.financials.4", "lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE", _TYPED_NOT_NULL),
    ("focal_2024.financials.5", "lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying", _TYPED_NOT_NULL),
    # financials.7 reuses the same v2 row as descriptors.6
    # (lobbyist_reg_form_includes_employment_type). Binary read on a binary
    # cell collapses the spec doc's "IS NOT NULL" framing to the binary
    # value (FALSE → 0; TRUE → 2). The cell-share regression test pins this.
    ("focal_2024.financials.7", "lobbyist_reg_form_includes_employment_type", _BINARY),
    ("focal_2024.financials.8", "lobbyist_spending_report_includes_expenditure_per_issue", _BINARY),
    ("focal_2024.financials.9", "lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship", _BINARY),
    ("focal_2024.financials.11", "lobbyist_spending_report_includes_campaign_contributions", _BINARY),
    # Contact log battery (Plan 2; 9 binary + 1 typed_is_not_null + 1 OR-pair).
    # contact_log.11 is compound (OR over reg_form + spending_report sides);
    # dispatched out-of-table via _COMPOUND_DISPATCH below.
    #
    # Partly-tier collapse (OQ3 YAGNI): .1, .3, .9, .11 publish raw=1 ("partly")
    # on Federal US LDA but project to 2 (full) under the binary read since v2
    # cells don't carry the partly-tier sub-criteria. Cumulative over-scoring
    # on US LDA contact_log = +10 weighted points (projected 20 vs published
    # 10); Plan 4's aggregation harness budgets this.
    ("focal_2024.contact_log.1", "lobbying_contact_log_includes_beneficiary_organization", _BINARY),
    ("focal_2024.contact_log.2", "lobbying_contact_log_includes_official_contacted_name", _BINARY),
    ("focal_2024.contact_log.3", "lobbying_contact_log_includes_institution_or_department", _BINARY),
    ("focal_2024.contact_log.4", "lobbying_contact_log_includes_meeting_attendees", _BINARY),
    ("focal_2024.contact_log.5", "lobbying_contact_log_includes_date", _BINARY),
    ("focal_2024.contact_log.6", "lobbying_contact_log_includes_communication_form", _TYPED_NOT_NULL),
    ("focal_2024.contact_log.7", "lobbying_contact_log_includes_location", _BINARY),
    ("focal_2024.contact_log.8", "lobbying_contact_log_includes_materials_shared", _BINARY),
    ("focal_2024.contact_log.9", "lobbying_contact_log_includes_topics_discussed", _BINARY),
    ("focal_2024.contact_log.10", "lobbyist_spending_report_includes_position_on_bill", _BINARY),
)


_SPEC_BY_ITEM: Final[dict[str, tuple[str, str]]] = {
    item_id: (row, kind) for item_id, row, kind in _SINGLE_ROW_SPEC
}


# ---------------------------------------------------------------------------
# Vintage gating
#
# Items in this dict are scored only when ``vintage >= _MIN_VINTAGE[item]``.
# A dispatcher call with a lower vintage raises KeyError ("not in scope for
# this vintage"). Callers filter IN_SCOPE_ITEMS by vintage before
# dispatching; the KeyError is a programming-error tripwire rather than a
# silent skip (which would mask iteration-order bugs in the aggregator).
# ---------------------------------------------------------------------------

_MIN_VINTAGE: Final[dict[str, int]] = {
    "focal_2024.relationships.0": 2025,
}


# ---------------------------------------------------------------------------
# Compound-item helpers
#
# relationships.1 reads 2 binary rows under an OR:
#   lobbyist_spending_report_includes_principal_names
#   OR lobbyist_reg_form_lists_each_employer_or_principal
#
# financials.10 will reuse the same OR-pattern on the gifts/entertainment/
# transport/lodging row pair (added with the financials battery; per the
# plan, can also import newmark_2017's ``project_gifts_actor_agnostic_or``
# and rescale 0/1 -> 0/2).
# ---------------------------------------------------------------------------

_REL_1_ROWS: Final[tuple[str, str]] = (
    "lobbyist_spending_report_includes_principal_names",
    "lobbyist_reg_form_lists_each_employer_or_principal",
)

#: financials.6 reads both actor-side total-expenditures rows under an AND
#: (lobbyist-side ∧ principal-side). 3-tier semantics: both TRUE → 2,
#: exactly one TRUE → 1, both FALSE → 0, any unknown → UNABLE_TO_EVALUATE.
_FIN_6_ROWS: Final[tuple[str, str]] = (
    "lobbyist_spending_report_includes_total_expenditures",
    "principal_spending_report_includes_total_expenditures",
)

#: contact_log.11 reads the α form-type-split pair (spending_report side
#: + reg_form side) under an OR. FOCAL framing: "Targeted areas of public
#: policy or legislation, including bill numbers" — disclosure exists if
#: present on either filing surface. Same OR semantics as relationships.1.
_CL_11_ROWS: Final[tuple[str, str]] = (
    "lobbyist_spending_report_includes_bill_or_action_identifier",
    "lobbyist_reg_form_includes_bill_or_action_identifier",
)


# ---------------------------------------------------------------------------
# Scope battery constants
#
# scope.1 / scope.4 set-membership full sets — extracted from FOCAL paper
# Table 3 / Suppl File 1. The 9 organizational actor types and 8 activity
# types are FOCAL-distinctive enumerations carried by the v2 cells.
#
# scope.2 calibration cutoffs (OQ1 defaults): $1000 / 5% time. Module-level
# constants overridable per-test via the helper's keyword args.
# ---------------------------------------------------------------------------

_SCOPE_1_FULL_SET: Final[frozenset[str]] = frozenset({
    "prof_consultant",
    "inhouse_company",
    "inhouse_org",
    "prof_consultancy",
    "law_firm",
    "think_tank",
    "research_institution",
    "public_entity",
    "govt_agency_employee",
})

_SCOPE_4_FULL_SET: Final[frozenset[str]] = frozenset({
    "oral",
    "written",
    "electronic",
    "virtual",
    "meeting_organizing",
    "events",
    "phone_calls",
    "emails",
})

#: scope.2 calibration defaults (OQ1). "Significant threshold" boundary in
#: FOCAL paper line 1206-1208 is scorer-judgment. Defaults chosen to make
#: US LDA's published scope.2 = 0 hold (US has $3000 comp + 20% time —
#: both above these cutoffs).
SCOPE_2_LOW_DOLLAR_CUTOFF: Final[Decimal] = Decimal("1000")
SCOPE_2_LOW_TIME_CUTOFF: Final[Decimal] = Decimal("5")

_SCOPE_2_COMP_ROW: Final[str] = "lobbyist_registration_threshold_compensation_dollars"
_SCOPE_2_EXP_ROW: Final[str] = "lobbyist_registration_threshold_expenditure_dollars"
_SCOPE_2_TIME_ROW: Final[str] = "lobbyist_registration_threshold_time_percent"

_SCOPE_3_MAJOR_BRANCH_ROWS: Final[tuple[str, ...]] = (
    "def_target_legislative_branch",
    "def_target_executive_agency",
    "def_target_governors_office",
)
_SCOPE_3_STAFF_ROWS: Final[tuple[str, str]] = (
    "def_target_legislative_staff",
    "def_target_executive_staff",
)

_SCOPE_1_ROW: Final[str] = "def_lobbyist_actor_types"
_SCOPE_4_ROW: Final[str] = "def_lobbying_activity_types"


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


def _project_binary_or_2tier(
    cells: dict[str, Any], row_ids: tuple[str, ...]
) -> int | Literal["unable_to_evaluate"]:
    """Multi-row binary OR, 2-tier.

    If ANY row's ``legal_availability`` is known TRUE -> 2 (the OR is
    satisfied regardless of other sides).
    If ALL rows' values are known FALSE -> 0.
    Otherwise (at least one side unknown and no known-TRUE rescue) ->
    ``"unable_to_evaluate"``.

    Used by relationships.1 (principal-names OR lists-each-employer) and
    inline-reusable for financials.10 (gifts actor-agnostic OR — though
    that one will also be cross-checked against newmark_2017's
    ``project_gifts_actor_agnostic_or`` when the financials battery lands).
    """
    values: list[bool | None] = []
    for row_id in row_ids:
        cell = cells.get(row_id)
        values.append(cell.get(LEGAL_AXIS) if cell is not None else None)
    if any(v is True for v in values):
        return 2
    if all(v is False for v in values):
        return 0
    return UNABLE_TO_EVALUATE


def _project_binary_and_3tier(
    cells: dict[str, Any], row_ids: tuple[str, ...]
) -> int | Literal["unable_to_evaluate"]:
    """Multi-row binary AND, 3-tier.

    Returns:
        2 — when ALL rows are known TRUE.
        1 — when at least one is known TRUE and at least one is known FALSE
            (full set is known, but not all TRUE — "partly").
        0 — when ALL rows are known FALSE.
        ``"unable_to_evaluate"`` — when any row is missing or has axis None
            and the answer cannot be determined from the known values alone.

    Used by financials.6 (lobbyist-side ∧ principal-side total expenditures).
    """
    values: list[bool | None] = []
    for row_id in row_ids:
        cell = cells.get(row_id)
        values.append(cell.get(LEGAL_AXIS) if cell is not None else None)
    if any(v is None for v in values):
        return UNABLE_TO_EVALUATE
    if all(v is True for v in values):
        return 2
    if any(v is True for v in values):
        return 1
    return 0


def _project_financials_10_from_newmark(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """financials.10 (gifts/expenditures benefiting officials).

    Imports ``project_gifts_actor_agnostic_or`` from ``newmark_2017`` (which
    returns 0/1 on its actor-agnostic OR over the lobbyist-side + principal-
    side gifts rows) and rescales to FOCAL's per-item 0/2 granularity.
    UNABLE_TO_EVALUATE passes through unchanged.

    The import couples this module to ``newmark_2017``'s helper stability —
    a `test_financials_10_matches_newmark_2017_helper_rescaled` regression
    test surfaces drift if newmark's semantics change.
    """
    result = _newmark_gifts_or(cells)
    if result == _NEWMARK_UNABLE:
        return UNABLE_TO_EVALUATE
    return result * 2  # 0 → 0; 1 → 2


# ---------------------------------------------------------------------------
# Scope battery helpers
# ---------------------------------------------------------------------------


def _project_set_membership_3tier(
    cells: dict[str, Any],
    row_id: str,
    full_set: frozenset[str],
    partly_predicate: Any,
) -> int | Literal["unable_to_evaluate"]:
    """Generic 3-tier set-membership over a typed Set[enum] cell.

    full_set match -> 2; partly_predicate(cell) -> 1; else -> 0.
    Row absent or axis None -> ``"unable_to_evaluate"``.

    ``partly_predicate`` receives the cell's frozen set value (after
    coercion from list/set to frozenset). Callers supply the predicate
    that captures the rubric's "partly" semantics for the specific battery
    (e.g. scope.1 requires ``"prof_consultant" in cell``).
    """
    if row_id not in cells:
        return UNABLE_TO_EVALUATE
    raw = cells[row_id].get(LEGAL_AXIS)
    if raw is None:
        return UNABLE_TO_EVALUATE
    cell_set = frozenset(raw)
    if cell_set == full_set:
        return 2
    if partly_predicate(cell_set):
        return 1
    return 0


def _project_focal_scope_1(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """scope.1 — lobbyist actor types set-membership.

    Full 9-set → 2; ``"prof_consultant"`` ∈ cell AND cell ≠ full → 1
    (FOCAL "other exclusions"); ``cell == {"prof_consultant"}`` only → 0
    (FOCAL "only consultant lobbyists"); empty or narrower → 0.
    """
    return _project_set_membership_3tier(
        cells,
        _SCOPE_1_ROW,
        _SCOPE_1_FULL_SET,
        partly_predicate=lambda s: "prof_consultant" in s and s != frozenset({"prof_consultant"}),
    )


def _project_focal_scope_4(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """scope.4 — lobbying activity types set-membership.

    Full 8-set → 2; non-empty proper subset → 1; empty → 0.

    NOTE: FOCAL spec doc labels partly = "limited to influencing legislative
    changes" and no = "{face_to_face} only". Neither atomizes onto the
    8-enum ``Set[enum{oral, written, electronic, virtual, meeting_organizing,
    events, phone_calls, emails}]`` cell content (no ``face_to_face``
    enum bit, no ``legislative_changes_only`` flag). Module projects scope.4
    parallel to scope.1's set-membership shape — full → 2, non-empty proper
    subset → 1, empty → 0 — as the cleanest atomization of the available
    cell data. Documented as a known divergence; US LDA scope.4 = 2 (full
    set) sanity-checks the convention against the published anchor.
    """
    return _project_set_membership_3tier(
        cells,
        _SCOPE_4_ROW,
        _SCOPE_4_FULL_SET,
        partly_predicate=lambda s: len(s) > 0,
    )


def _coerce_threshold_decimal(raw: Any) -> Decimal | None:
    """Coerce a typed-cell threshold value to ``Decimal``.

    Accepts ``Decimal``, ``int``, ``float``, or a numeric string. Returns
    None for None or empty string. Raises ``InvalidOperation`` on a
    non-numeric string (a contract-violation in the cell — bubble up
    rather than silently coerce to 0).
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, Decimal):
        return raw
    if isinstance(raw, (int, float)):
        return Decimal(str(raw))
    return Decimal(str(raw))


def _project_focal_scope_2(
    cells: dict[str, Any],
    low_dollar_cutoff: Decimal = SCOPE_2_LOW_DOLLAR_CUTOFF,
    low_time_cutoff: Decimal = SCOPE_2_LOW_TIME_CUTOFF,
) -> int | Literal["unable_to_evaluate"]:
    """scope.2 — no/low financial or time threshold for registration.

    3-tier calibrated read:
        any threshold > cutoff (significant)         → 0 (no)
        any threshold present but none significant   → 1 (partly)
        no thresholds (all three None)               → 2 (yes — anyone must register)

    All three threshold rows must be present in ``cells`` (with axis value
    None or a value) for projection — if any row is row-absent we cannot
    distinguish "law specifies no threshold" from "we haven't extracted the
    threshold yet". The 3-cell pattern is the canonical 5-rubric-confirmed
    threshold-cell family; row-absent on any → UNABLE_TO_EVALUATE.
    """
    required = (_SCOPE_2_COMP_ROW, _SCOPE_2_EXP_ROW, _SCOPE_2_TIME_ROW)
    for row in required:
        if row not in cells:
            return UNABLE_TO_EVALUATE
    try:
        comp = _coerce_threshold_decimal(cells[_SCOPE_2_COMP_ROW].get(LEGAL_AXIS))
        exp = _coerce_threshold_decimal(cells[_SCOPE_2_EXP_ROW].get(LEGAL_AXIS))
        time = _coerce_threshold_decimal(cells[_SCOPE_2_TIME_ROW].get(LEGAL_AXIS))
    except InvalidOperation:
        # Non-numeric threshold value is a cell-contract violation; surface
        # as UNABLE rather than silently coerce.
        return UNABLE_TO_EVALUATE
    any_threshold = any(t is not None for t in (comp, exp, time))
    if not any_threshold:
        return 2
    significant = (
        (comp is not None and comp > low_dollar_cutoff)
        or (exp is not None and exp > low_dollar_cutoff)
        or (time is not None and time > low_time_cutoff)
    )
    if significant:
        return 0
    return 1


def _project_focal_scope_3(
    cells: dict[str, Any],
) -> int | Literal["unable_to_evaluate"]:
    """scope.3 — major-branch AND with staff-AND sub-projection (OQ2 strict).

    Major branches in scope (legislative ∧ executive ∧ governor) determine
    the top-level tier: if any major branch is FALSE → 0 (regardless of
    staff). If any major-branch cell is missing → UNABLE (can't determine
    top tier).

    Once major branches are all TRUE, the staff cells discriminate between
    2 (yes — all targets including staff) and 1 (partly — staff excluded).
    OQ2 strict-AND: BOTH ``def_target_legislative_staff`` AND
    ``def_target_executive_staff`` must be TRUE for ``staff_in_scope=True``.

    Staff-cell-missing only causes UNABLE when the answer is still
    ambiguous between 2 and 1 — i.e. when all major branches are TRUE.
    If a major branch is already determined FALSE, the answer is 0 and
    staff-cell-missing doesn't affect it.
    """
    major_vals: list[bool | None] = []
    for row in _SCOPE_3_MAJOR_BRANCH_ROWS:
        cell = cells.get(row)
        major_vals.append(cell.get(LEGAL_AXIS) if cell is not None else None)
    # If any major branch is known FALSE → 0; staff cells irrelevant.
    if any(v is False for v in major_vals):
        return 0
    # All known TRUE so far — but if any is None, we can't decide between
    # 0 (some branch FALSE) and {1, 2} (all branches TRUE).
    if any(v is None for v in major_vals):
        return UNABLE_TO_EVALUATE
    # All major branches TRUE: read the staff cells.
    staff_vals: list[bool | None] = []
    for row in _SCOPE_3_STAFF_ROWS:
        cell = cells.get(row)
        staff_vals.append(cell.get(LEGAL_AXIS) if cell is not None else None)
    if any(v is None for v in staff_vals):
        return UNABLE_TO_EVALUATE
    if all(v is True for v in staff_vals):
        return 2
    return 1


# ---------------------------------------------------------------------------
# Per-item dispatcher
# ---------------------------------------------------------------------------


_COMPOUND_DISPATCH: Final[dict[str, Any]] = {
    "focal_2024.relationships.1": lambda cells: _project_binary_or_2tier(cells, _REL_1_ROWS),
    "focal_2024.financials.6": lambda cells: _project_binary_and_3tier(cells, _FIN_6_ROWS),
    "focal_2024.financials.10": _project_financials_10_from_newmark,
    "focal_2024.scope.1": _project_focal_scope_1,
    "focal_2024.scope.2": _project_focal_scope_2,
    "focal_2024.scope.3": _project_focal_scope_3,
    "focal_2024.scope.4": _project_focal_scope_4,
    "focal_2024.contact_log.11": lambda cells: _project_binary_or_2tier(cells, _CL_11_ROWS),
}


def project_focal_2024_item(
    item_id: str, cells: dict[str, Any], vintage: int = 2024
) -> int | Literal["unable_to_evaluate"]:
    """Project one FOCAL 2024 atomic item from v2 compendium cells.

    Raises ``KeyError`` on:

    * unknown ``item_id`` (not in ``_SPEC_BY_ITEM`` and not a known
      compound helper),
    * excluded items (``focal_2024.revolving_door.2``),
    * vintage-gated items called outside their vintage window
      (e.g. ``focal_2024.relationships.0`` for ``vintage=2024``).
    """
    # Vintage gate: items registered in _MIN_VINTAGE are scored only when
    # vintage >= their minimum. A pre-min-vintage call is a programming
    # error in the caller's IN_SCOPE_ITEMS iteration, not a data-missing
    # condition — raise rather than return UNABLE_TO_EVALUATE.
    min_v = _MIN_VINTAGE.get(item_id)
    if min_v is not None and vintage < min_v:
        raise KeyError(
            f"{item_id!r} is gated by min_vintage={min_v}; called with "
            f"vintage={vintage}"
        )
    if item_id in _COMPOUND_DISPATCH:
        return _COMPOUND_DISPATCH[item_id](cells)
    row, kind = _SPEC_BY_ITEM[item_id]  # KeyError on unknown
    if kind == _BINARY:
        return _project_binary_2tier(cells, row)
    if kind == _TYPED_NOT_NULL:
        return _project_typed_is_not_null_2tier(cells, row)
    raise AssertionError(f"unknown spec kind {kind!r} for {item_id!r}")


# ---------------------------------------------------------------------------
# Ground-truth loader
#
# Reads the Lacy-Nichols 2025 per-country scores CSV
# (``docs/historical/compendium-source-extracts/results/focal_2025_lacy_nichols_per_country_scores.csv``)
# and returns ``{jurisdiction: {indicator_id: raw_score}}``. The 27 FOCAL
# legal-core indicator IDs are listed in ``FOCAL_2024_LEGAL_CORE_INDICATORS``;
# companion plans (contact_log, openness/timeliness) extend the indicator
# set as their batteries land.
#
# Federal_US LDA (CSV row "United States") is the load-bearing per-item
# validation anchor; other 27 jurisdictions are reference data.
# ---------------------------------------------------------------------------


#: 27 indicator IDs in this plan's legal-core scope (4 scope + 6 descriptors
#: + 1 revolving_door + 5 relationships [includes 2025-only relationships.0]
#: + 11 financials). IDs are bare (no ``focal_2024.`` prefix) — matches
#: CSV wire format. Companion plans extend by adding their indicators.
FOCAL_2024_LEGAL_CORE_INDICATORS: Final[frozenset[str]] = frozenset({
    "scope.1", "scope.2", "scope.3", "scope.4",
    "descriptors.1", "descriptors.2", "descriptors.3",
    "descriptors.4", "descriptors.5", "descriptors.6",
    "revolving_door.1",
    "relationships.0", "relationships.1",
    "relationships.2", "relationships.3", "relationships.4",
    "financials.1", "financials.2", "financials.3",
    "financials.4", "financials.5", "financials.6",
    "financials.7", "financials.8", "financials.9",
    "financials.10", "financials.11",
})

#: 11 indicator IDs in Plan 2's contact_log scope. IDs are bare (no
#: ``focal_2024.`` prefix) — matches CSV wire format.
FOCAL_2024_CONTACT_LOG_INDICATORS: Final[frozenset[str]] = frozenset({
    "contact_log.1", "contact_log.2", "contact_log.3",
    "contact_log.4", "contact_log.5", "contact_log.6",
    "contact_log.7", "contact_log.8", "contact_log.9",
    "contact_log.10", "contact_log.11",
})

_GROUND_TRUTH_CSV_PARTS: Final[tuple[str, ...]] = (
    "docs",
    "historical",
    "compendium-source-extracts",
    "results",
    "focal_2025_lacy_nichols_per_country_scores.csv",
)


def load_focal_2024_per_country_reference(
    repo_root: Path,
) -> dict[str, dict[str, int | None]]:
    """Load per-jurisdiction per-indicator published raw scores.

    Returns ``{jurisdiction_name: {indicator_id: raw_score | None}}`` where
    ``indicator_id`` is the verbatim CSV value (e.g. ``"financials.1"``,
    no module prefix), and ``raw_score`` is the published integer in
    ``{0, 1, 2}``. A value of ``None`` represents L-N 2025's
    "not_assessable" state (CSV ``raw_score == "NA"``); callers that
    aggregate must exclude these cells from both the numerator and the
    max-sum denominator. Callers comparing against the module's
    ``focal_2024.*`` dispatcher keys must add the prefix themselves.

    Includes all 28 L-N 2025 jurisdictions and all CSV indicator IDs
    (legal-core + timeliness + openness + contact_log). Per the plan's
    Phase C scope, the legal-core subset
    (``FOCAL_2024_LEGAL_CORE_INDICATORS``) is the load-bearing slice;
    companion plans validate their own slices. The US row carries no
    ``None`` cells in legal-core. Across the full CSV the missing-value
    cells split into 40 ``"NA"`` cells (the L-N "not_assessable" state,
    concentrated on non-US scope.2/scope.3/scope.4) and 15 empty-string
    cells (parliamentary-system observable ``timeliness.2`` in non-
    parliamentary jurisdictions). Both flavors collapse to ``None`` for
    callers; the source distinction is documented but not preserved.
    """
    csv_path = repo_root.joinpath(*_GROUND_TRUTH_CSV_PARTS)
    reference: dict[str, dict[str, int | None]] = {}
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            jurisdiction = row["country"]
            indicator_id = row["indicator_id"]
            raw = row["raw_score"]
            raw_score: int | None = (
                None if raw == "NA" or raw.strip() == "" else int(raw)
            )
            reference.setdefault(jurisdiction, {})[indicator_id] = raw_score
    return reference

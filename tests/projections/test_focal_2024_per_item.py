"""Per-item projection tests for FOCAL 2024.

Each test exercises a single per-item helper against a hand-built
``cells`` dict keyed by v2 compendium row id. Cell shape::

    cells[row_id] = {
        "legal_availability": <typed>,
        "practical_availability": <typed>,    # not read by legal-core items
    }

Helpers return ``int | Literal["unable_to_evaluate"]`` where ``int ∈ {0, 1, 2}``:

* ``2`` when the state's regime fully satisfies the indicator.
* ``1`` only for the 3-tier helper items (scope.*, financials.6) where a
  documented "partly" interpretation applies.
* ``0`` when the regime lacks the indicator.
* ``"unable_to_evaluate"`` when required input cells are missing.

The 1 excluded item (``revolving_door.2`` — enforcement-adjacent, not
disclosure-side) is regression-guarded by an explicit test asserting
``KeyError`` on dispatch.

Conventions per the FOCAL legal-core plan (2026-05-18):

* "Partly" sub-tiers documented in FOCAL Suppl Tables but not extractable
  from v2 binary cells are collapsed to binary 0/2 (YAGNI, OQ3/OQ4).
  This is a known systematic over/under-scoring channel; tolerance is
  budgeted at ±15 raw points on the 81 Federal US LDA target (Plan 4).
* ``relationships.0`` (2025-only "Lobbyist list") gated by ``vintage``;
  not scored for ``vintage=2024``.
"""

from __future__ import annotations

import pytest

from lobby_analysis.projections.focal_2024 import (
    EXCLUDED_ITEMS,
    UNABLE_TO_EVALUATE,
    project_focal_2024_item,
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _binary_cell(value: bool | None) -> dict[str, bool | None]:
    return {"legal_availability": value}


def _typed_cell(value: object | None) -> dict[str, object | None]:
    return {"legal_availability": value}


# ---------------------------------------------------------------------------
# Descriptors battery — 4 binary + 2 typed-IS-NOT-NULL items
#
# All 6 items collapse to 0/2 per OQ3 YAGNI (the FOCAL "P=some entries
# incomplete" sub-tier is not extractable from v2 binary cells).
#
# descriptors.1 (full names)         -> lobbyist_reg_form_includes_lobbyist_full_name    [binary]
# descriptors.2 (contact details)    -> lobbyist_reg_form_includes_lobbyist_contact_details  [binary]
# descriptors.3 (legal form)         -> lobbyist_reg_form_includes_lobbyist_legal_form   [typed Optional[enum]]
# descriptors.4 (business id)        -> lobbyist_reg_form_includes_lobbyist_business_id  [binary]
# descriptors.5 (sector)             -> lobbyist_reg_form_includes_lobbyist_sector       [typed Optional[SectorClassification]]
# descriptors.6 (contract type)      -> lobbyist_reg_form_includes_employment_type       [binary]
# ---------------------------------------------------------------------------


# --- descriptors.1 (binary full_name) ---


def test_descriptors_1_full_name_two_when_true():
    cells = {"lobbyist_reg_form_includes_lobbyist_full_name": _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.descriptors.1", cells) == 2


def test_descriptors_1_full_name_zero_when_false():
    cells = {"lobbyist_reg_form_includes_lobbyist_full_name": _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.descriptors.1", cells) == 0


def test_descriptors_1_full_name_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.1", {}) == UNABLE_TO_EVALUATE
    )


def test_descriptors_1_full_name_unable_when_axis_none():
    cells = {"lobbyist_reg_form_includes_lobbyist_full_name": _binary_cell(None)}
    assert (
        project_focal_2024_item("focal_2024.descriptors.1", cells)
        == UNABLE_TO_EVALUATE
    )


# --- descriptors.2 (binary contact_details) ---


def test_descriptors_2_contact_details_two_when_true():
    cells = {
        "lobbyist_reg_form_includes_lobbyist_contact_details": _binary_cell(True)
    }
    assert project_focal_2024_item("focal_2024.descriptors.2", cells) == 2


def test_descriptors_2_contact_details_zero_when_false():
    cells = {
        "lobbyist_reg_form_includes_lobbyist_contact_details": _binary_cell(False)
    }
    assert project_focal_2024_item("focal_2024.descriptors.2", cells) == 0


def test_descriptors_2_contact_details_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.2", {}) == UNABLE_TO_EVALUATE
    )


# --- descriptors.3 (typed Optional[enum] legal_form) ---


def test_descriptors_3_legal_form_two_when_enum_value_present():
    """``IS NOT NULL`` semantics: any non-empty typed value -> 2."""
    cells = {
        "lobbyist_reg_form_includes_lobbyist_legal_form": _typed_cell(
            "corporation"  # representative enum value
        )
    }
    assert project_focal_2024_item("focal_2024.descriptors.3", cells) == 2


def test_descriptors_3_legal_form_zero_when_axis_none():
    cells = {"lobbyist_reg_form_includes_lobbyist_legal_form": _typed_cell(None)}
    assert project_focal_2024_item("focal_2024.descriptors.3", cells) == 0


def test_descriptors_3_legal_form_zero_when_axis_empty_string():
    cells = {"lobbyist_reg_form_includes_lobbyist_legal_form": _typed_cell("")}
    assert project_focal_2024_item("focal_2024.descriptors.3", cells) == 0


def test_descriptors_3_legal_form_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.3", {}) == UNABLE_TO_EVALUATE
    )


# --- descriptors.4 (binary business_id) ---


def test_descriptors_4_business_id_two_when_true():
    cells = {"lobbyist_reg_form_includes_lobbyist_business_id": _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.descriptors.4", cells) == 2


def test_descriptors_4_business_id_zero_when_false():
    cells = {"lobbyist_reg_form_includes_lobbyist_business_id": _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.descriptors.4", cells) == 0


def test_descriptors_4_business_id_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.4", {}) == UNABLE_TO_EVALUATE
    )


# --- descriptors.5 (typed Optional[SectorClassification] sector) ---


def test_descriptors_5_sector_two_when_typed_value_present():
    cells = {
        "lobbyist_reg_form_includes_lobbyist_sector": _typed_cell(
            {"scheme": "NAICS", "code": "5416"}
        )
    }
    assert project_focal_2024_item("focal_2024.descriptors.5", cells) == 2


def test_descriptors_5_sector_zero_when_axis_none():
    cells = {"lobbyist_reg_form_includes_lobbyist_sector": _typed_cell(None)}
    assert project_focal_2024_item("focal_2024.descriptors.5", cells) == 0


def test_descriptors_5_sector_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.5", {}) == UNABLE_TO_EVALUATE
    )


# --- descriptors.6 (binary employment_type; reused by financials.7) ---


def test_descriptors_6_contract_type_two_when_true():
    cells = {"lobbyist_reg_form_includes_employment_type": _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.descriptors.6", cells) == 2


def test_descriptors_6_contract_type_zero_when_false():
    cells = {"lobbyist_reg_form_includes_employment_type": _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.descriptors.6", cells) == 0


def test_descriptors_6_contract_type_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.descriptors.6", {}) == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Revolving door battery — 1 item in scope (binary)
#
# revolving_door.1 -> lobbyist_reg_form_includes_lobbyist_prior_public_offices_held
# revolving_door.2 is OUT (excluded by FOCAL-1 user-decision 2026-05-13).
# ---------------------------------------------------------------------------


def test_revolving_door_1_two_when_true():
    cells = {
        "lobbyist_reg_form_includes_lobbyist_prior_public_offices_held": _binary_cell(
            True
        )
    }
    assert project_focal_2024_item("focal_2024.revolving_door.1", cells) == 2


def test_revolving_door_1_zero_when_false():
    cells = {
        "lobbyist_reg_form_includes_lobbyist_prior_public_offices_held": _binary_cell(
            False
        )
    }
    assert project_focal_2024_item("focal_2024.revolving_door.1", cells) == 0


def test_revolving_door_1_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.revolving_door.1", {})
        == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Relationships battery — 4 binary items + 1 vintage-gated (relationships.0)
#
# relationships.0 (2025-only, "Lobbyist list") -> principal_spending_report_lists_lobbyists_employed
#   Gated by vintage >= 2025. For vintage=2024 the dispatcher raises KeyError
#   — the item is not in 2024-vintage scope at all (vs UNABLE_TO_EVALUATE,
#   which is reserved for "data missing"). Caller filters IN_SCOPE_ITEMS by
#   vintage before dispatching.
#
# relationships.1 (client list, binary OR over 2 rows) — first OR-helper:
#   lobbyist_spending_report_includes_principal_names
#   OR lobbyist_reg_form_lists_each_employer_or_principal
#
# relationships.2/.3/.4 single binary rows.
# ---------------------------------------------------------------------------


# --- relationships.0 (2025-only, vintage-gated) ---


def test_relationships_0_keyerror_for_2024_vintage():
    """Vintage 2024 doesn't include the 2025-only "Lobbyist list" indicator.
    Dispatch raises KeyError (semantically "not in scope for this vintage").
    """
    with pytest.raises(KeyError):
        project_focal_2024_item("focal_2024.relationships.0", {}, vintage=2024)


def test_relationships_0_two_when_true_in_2025_vintage():
    cells = {
        "principal_spending_report_lists_lobbyists_employed": _binary_cell(True)
    }
    assert (
        project_focal_2024_item(
            "focal_2024.relationships.0", cells, vintage=2025
        )
        == 2
    )


def test_relationships_0_zero_when_false_in_2025_vintage():
    cells = {
        "principal_spending_report_lists_lobbyists_employed": _binary_cell(False)
    }
    assert (
        project_focal_2024_item(
            "focal_2024.relationships.0", cells, vintage=2025
        )
        == 0
    )


def test_relationships_0_unable_when_row_missing_in_2025_vintage():
    assert (
        project_focal_2024_item("focal_2024.relationships.0", {}, vintage=2025)
        == UNABLE_TO_EVALUATE
    )


# --- relationships.1 (binary OR over 2 rows) ---


_REL1_SPEND = "lobbyist_spending_report_includes_principal_names"
_REL1_REGFORM = "lobbyist_reg_form_lists_each_employer_or_principal"


def test_relationships_1_two_when_only_spending_side_true():
    cells = {
        _REL1_SPEND: _binary_cell(True),
        _REL1_REGFORM: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.relationships.1", cells) == 2


def test_relationships_1_two_when_only_regform_side_true():
    cells = {
        _REL1_SPEND: _binary_cell(False),
        _REL1_REGFORM: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.relationships.1", cells) == 2


def test_relationships_1_two_when_both_sides_true():
    cells = {
        _REL1_SPEND: _binary_cell(True),
        _REL1_REGFORM: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.relationships.1", cells) == 2


def test_relationships_1_zero_when_both_sides_false():
    cells = {
        _REL1_SPEND: _binary_cell(False),
        _REL1_REGFORM: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.relationships.1", cells) == 0


def test_relationships_1_unable_when_both_rows_missing():
    assert (
        project_focal_2024_item("focal_2024.relationships.1", {})
        == UNABLE_TO_EVALUATE
    )


def test_relationships_1_two_when_one_side_true_other_missing():
    """A known TRUE on either side wins the OR."""
    cells = {_REL1_SPEND: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.relationships.1", cells) == 2


def test_relationships_1_unable_when_one_side_false_other_missing():
    """A False on one side with the other unknown can't rule out
    disclosure — return unable, not coerce to 0."""
    cells = {_REL1_SPEND: _binary_cell(False)}
    assert (
        project_focal_2024_item("focal_2024.relationships.1", cells)
        == UNABLE_TO_EVALUATE
    )


# --- relationships.2/.3/.4 (single binary rows) ---


def test_relationships_2_member_sponsor_names_two_when_true():
    cells = {
        "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names": _binary_cell(
            True
        )
    }
    assert project_focal_2024_item("focal_2024.relationships.2", cells) == 2


def test_relationships_2_member_sponsor_names_zero_when_false():
    cells = {
        "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names": _binary_cell(
            False
        )
    }
    assert project_focal_2024_item("focal_2024.relationships.2", cells) == 0


def test_relationships_3_board_memberships_two_when_true():
    cells = {
        "lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships": _binary_cell(
            True
        )
    }
    assert project_focal_2024_item("focal_2024.relationships.3", cells) == 2


def test_relationships_4_business_associations_two_when_true():
    """relationships.4 reads the binary cell; FOCAL "partly" sub-tier
    (Y/N-only vs with-detail) is collapsed per OQ4 YAGNI."""
    cells = {
        "lobbyist_reg_form_includes_business_associations_with_officials": _binary_cell(
            True
        )
    }
    assert project_focal_2024_item("focal_2024.relationships.4", cells) == 2


def test_relationships_4_business_associations_zero_when_false():
    cells = {
        "lobbyist_reg_form_includes_business_associations_with_officials": _binary_cell(
            False
        )
    }
    assert project_focal_2024_item("focal_2024.relationships.4", cells) == 0


# ---------------------------------------------------------------------------
# Financials battery — 11 items (8 single-row + 3 compound)
#
# financials.1  (total income)            -> lobbyist_spending_report_includes_total_compensation                       [binary]
# financials.2  (income per client)       -> lobbyist_spending_report_includes_compensation_broken_down_by_payer        [binary]
# financials.3  (income source types)     -> consultant_lobbyist_report_includes_income_by_source_type                  [typed Set[enum]+amounts → IS NOT NULL]
# financials.4  (lobbyist count + FTE)    -> lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE [typed count_with_FTE → IS NOT NULL]
# financials.5  (time on lobbying)        -> lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying      [typed TimeSpent → IS NOT NULL]
# financials.6  (expenditure both sides)  -> AND-helper over lobbyist_spending_report_includes_total_expenditures
#                                            AND principal_spending_report_includes_total_expenditures                  [3-tier AND]
# financials.7  (compensated/uncomp.)     -> lobbyist_reg_form_includes_employment_type (reuses descriptors.6's row)    [binary]
# financials.8  (expenditure per issue)   -> lobbyist_spending_report_includes_expenditure_per_issue                    [binary]
# financials.9  (trade-assoc dues/spons.) -> lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship [binary]
# financials.10 (gifts/expenditures       -> OR-helper imported from newmark_2017's project_gifts_actor_agnostic_or
#                benefiting officials)       rescaled 0/1 → 0/2 (newmark uses 0/1; FOCAL needs 0/2)                     [OR rescale]
# financials.11 (campaign contributions)  -> lobbyist_spending_report_includes_campaign_contributions                   [binary]
#
# financials.7 reads the same v2 row as descriptors.6 — a regression test
# asserts the two dispatcher results agree on every cell value (binary
# semantics; "IS NOT NULL" framing in spec doc collapses to binary on the
# binary cell type).
# ---------------------------------------------------------------------------


_FIN1_ROW = "lobbyist_spending_report_includes_total_compensation"
_FIN2_ROW = "lobbyist_spending_report_includes_compensation_broken_down_by_payer"
_FIN3_ROW = "consultant_lobbyist_report_includes_income_by_source_type"
_FIN4_ROW = "lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE"
_FIN5_ROW = "lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying"
_FIN6_LOB_ROW = "lobbyist_spending_report_includes_total_expenditures"
_FIN6_PRIN_ROW = "principal_spending_report_includes_total_expenditures"
_FIN7_ROW = "lobbyist_reg_form_includes_employment_type"  # same as descriptors.6
_FIN8_ROW = "lobbyist_spending_report_includes_expenditure_per_issue"
_FIN9_ROW = "lobbyist_or_principal_spending_report_includes_trade_association_dues_or_sponsorship"
_FIN10_LOB_ROW = "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging"
_FIN10_PRIN_ROW = "principal_spending_report_includes_gifts_entertainment_transport_lodging"
_FIN11_ROW = "lobbyist_spending_report_includes_campaign_contributions"


# --- financials.1 (binary total compensation) ---


def test_financials_1_two_when_true():
    cells = {_FIN1_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.1", cells) == 2


def test_financials_1_zero_when_false():
    cells = {_FIN1_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.1", cells) == 0


def test_financials_1_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.1", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.2 (binary compensation per payer) ---


def test_financials_2_two_when_true():
    cells = {_FIN2_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.2", cells) == 2


def test_financials_2_zero_when_false():
    cells = {_FIN2_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.2", cells) == 0


def test_financials_2_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.2", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.3 (typed Set[enum]+amounts income source types; IS NOT NULL) ---


def test_financials_3_two_when_typed_set_value_present():
    """``IS NOT NULL`` semantics on the typed Set[enum]+amounts cell."""
    cells = {
        _FIN3_ROW: _typed_cell(
            {"membership_dues": 50000, "donations": 10000}  # representative value
        )
    }
    assert project_focal_2024_item("focal_2024.financials.3", cells) == 2


def test_financials_3_zero_when_axis_none():
    cells = {_FIN3_ROW: _typed_cell(None)}
    assert project_focal_2024_item("focal_2024.financials.3", cells) == 0


def test_financials_3_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.3", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.4 (typed count_with_FTE; IS NOT NULL) ---


def test_financials_4_two_when_typed_value_present():
    cells = {_FIN4_ROW: _typed_cell({"count": 5, "fte": 2.5})}
    assert project_focal_2024_item("focal_2024.financials.4", cells) == 2


def test_financials_4_zero_when_axis_none():
    cells = {_FIN4_ROW: _typed_cell(None)}
    assert project_focal_2024_item("focal_2024.financials.4", cells) == 0


def test_financials_4_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.4", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.5 (typed TimeSpent; IS NOT NULL) ---


def test_financials_5_two_when_typed_value_present():
    cells = {_FIN5_ROW: _typed_cell({"hours": 120, "period": "quarter"})}
    assert project_focal_2024_item("focal_2024.financials.5", cells) == 2


def test_financials_5_zero_when_axis_none():
    cells = {_FIN5_ROW: _typed_cell(None)}
    assert project_focal_2024_item("focal_2024.financials.5", cells) == 0


def test_financials_5_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.5", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.6 (AND over lobbyist-side + principal-side total expenditures) ---
#
# 3-tier semantics:
#   both TRUE                 → 2 (yes — full coverage)
#   exactly one TRUE          → 1 (partly — one side covered)
#   both FALSE                → 0 (no)
#   any side unknown / missing → UNABLE (cannot rule out the other side)
#
# UNABLE on partial-knowledge mirrors relationships.1's principled OR
# semantics — silent-False coercion of None (as in the plan's pseudocode)
# would hide extraction holes; the prior session shipped UNABLE-on-unknown
# as the project convention and we extend it to AND here.


def test_financials_6_two_when_both_sides_true():
    cells = {
        _FIN6_LOB_ROW: _binary_cell(True),
        _FIN6_PRIN_ROW: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.financials.6", cells) == 2


def test_financials_6_one_when_only_lobbyist_side_true():
    cells = {
        _FIN6_LOB_ROW: _binary_cell(True),
        _FIN6_PRIN_ROW: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.financials.6", cells) == 1


def test_financials_6_one_when_only_principal_side_true():
    cells = {
        _FIN6_LOB_ROW: _binary_cell(False),
        _FIN6_PRIN_ROW: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.financials.6", cells) == 1


def test_financials_6_zero_when_both_sides_false():
    cells = {
        _FIN6_LOB_ROW: _binary_cell(False),
        _FIN6_PRIN_ROW: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.financials.6", cells) == 0


def test_financials_6_unable_when_both_rows_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.6", {}) == UNABLE_TO_EVALUATE
    )


def test_financials_6_unable_when_one_side_true_other_missing():
    """One TRUE + other unknown: cannot decide between 2 and 1 → UNABLE."""
    cells = {_FIN6_LOB_ROW: _binary_cell(True)}
    assert (
        project_focal_2024_item("focal_2024.financials.6", cells)
        == UNABLE_TO_EVALUATE
    )


def test_financials_6_unable_when_one_side_false_other_missing():
    """One FALSE + other unknown: cannot decide between 1 and 0 → UNABLE."""
    cells = {_FIN6_LOB_ROW: _binary_cell(False)}
    assert (
        project_focal_2024_item("focal_2024.financials.6", cells)
        == UNABLE_TO_EVALUATE
    )


# --- financials.7 (binary employment_type; cell-shared with descriptors.6) ---


def test_financials_7_two_when_true():
    cells = {_FIN7_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.7", cells) == 2


def test_financials_7_zero_when_false():
    cells = {_FIN7_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.7", cells) == 0


def test_financials_7_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.7", {}) == UNABLE_TO_EVALUATE
    )


def test_financials_7_and_descriptors_6_agree_on_shared_row():
    """Regression guard on the cell-share: financials.7 and descriptors.6
    must project to identical values on identical cell input — they read
    the same v2 row (``lobbyist_reg_form_includes_employment_type``)."""
    for axis_value in (True, False, None):
        cells = {_FIN7_ROW: _binary_cell(axis_value)}
        assert project_focal_2024_item(
            "focal_2024.financials.7", cells
        ) == project_focal_2024_item("focal_2024.descriptors.6", cells)


# --- financials.8 (binary expenditure per issue) ---


def test_financials_8_two_when_true():
    cells = {_FIN8_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.8", cells) == 2


def test_financials_8_zero_when_false():
    cells = {_FIN8_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.8", cells) == 0


def test_financials_8_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.8", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.9 (binary trade-association dues or sponsorship) ---


def test_financials_9_two_when_true():
    cells = {_FIN9_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.9", cells) == 2


def test_financials_9_zero_when_false():
    cells = {_FIN9_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.9", cells) == 0


def test_financials_9_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.9", {}) == UNABLE_TO_EVALUATE
    )


# --- financials.10 (OR-helper imported from newmark_2017; rescale 0/1 → 0/2) ---
#
# Imports ``project_gifts_actor_agnostic_or`` from newmark_2017 (which
# returns 0/1) and rescales to FOCAL's 0/2 per-item granularity. UNABLE
# passes through unchanged.


def test_financials_10_two_when_only_lobbyist_side_true():
    cells = {
        _FIN10_LOB_ROW: _binary_cell(True),
        _FIN10_PRIN_ROW: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.financials.10", cells) == 2


def test_financials_10_two_when_only_principal_side_true():
    cells = {
        _FIN10_LOB_ROW: _binary_cell(False),
        _FIN10_PRIN_ROW: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.financials.10", cells) == 2


def test_financials_10_two_when_both_sides_true():
    cells = {
        _FIN10_LOB_ROW: _binary_cell(True),
        _FIN10_PRIN_ROW: _binary_cell(True),
    }
    assert project_focal_2024_item("focal_2024.financials.10", cells) == 2


def test_financials_10_zero_when_both_sides_false():
    cells = {
        _FIN10_LOB_ROW: _binary_cell(False),
        _FIN10_PRIN_ROW: _binary_cell(False),
    }
    assert project_focal_2024_item("focal_2024.financials.10", cells) == 0


def test_financials_10_unable_when_both_rows_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.10", {})
        == UNABLE_TO_EVALUATE
    )


def test_financials_10_two_when_one_side_true_other_missing():
    cells = {_FIN10_LOB_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.10", cells) == 2


def test_financials_10_unable_when_one_side_false_other_missing():
    cells = {_FIN10_LOB_ROW: _binary_cell(False)}
    assert (
        project_focal_2024_item("focal_2024.financials.10", cells)
        == UNABLE_TO_EVALUATE
    )


def test_financials_10_matches_newmark_2017_helper_rescaled():
    """Coupling test: financials.10's projection must equal newmark_2017's
    ``project_gifts_actor_agnostic_or`` × 2 (UNABLE passes through).

    Sanity-checks the import-and-rescale chain — if newmark_2017's helper
    semantics change underneath us, this test surfaces the drift."""
    from lobby_analysis.projections.newmark_2017 import (
        project_gifts_actor_agnostic_or,
        UNABLE_TO_EVALUATE as NM_UNABLE,
    )
    for lob, prin in [(True, True), (True, False), (False, True), (False, False)]:
        cells = {
            _FIN10_LOB_ROW: _binary_cell(lob),
            _FIN10_PRIN_ROW: _binary_cell(prin),
        }
        nm = project_gifts_actor_agnostic_or(cells)
        focal = project_focal_2024_item("focal_2024.financials.10", cells)
        if nm == NM_UNABLE:
            assert focal == UNABLE_TO_EVALUATE
        else:
            assert focal == nm * 2


# --- financials.11 (binary campaign contributions) ---


def test_financials_11_two_when_true():
    cells = {_FIN11_ROW: _binary_cell(True)}
    assert project_focal_2024_item("focal_2024.financials.11", cells) == 2


def test_financials_11_zero_when_false():
    cells = {_FIN11_ROW: _binary_cell(False)}
    assert project_focal_2024_item("focal_2024.financials.11", cells) == 0


def test_financials_11_unable_when_row_missing():
    assert (
        project_focal_2024_item("focal_2024.financials.11", {})
        == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Scope battery — 4 items, all named helpers
#
# scope.1 (lobbyist actor types)  -> def_lobbyist_actor_types (typed Set[enum])    [set-membership 3-tier]
# scope.2 (no/low threshold)      -> 3 typed threshold cells (compensation $, expenditure $, time %) [calibrated 3-tier]
# scope.3 (target types)          -> 5 binary def_target_* cells                   [AND 3-tier with staff sub-AND]
# scope.4 (activity breadth)      -> def_lobbying_activity_types (typed Set[enum]) [set-membership 3-tier]
#
# OQ1 default cutoffs: $1000 / 5% (fixture-overridable, but tests pin defaults).
# OQ2 staff-AND-strict: both def_target_legislative_staff AND def_target_executive_staff must be TRUE for staff_in_scope=TRUE.
#
# scope.4 "partly" tier divergence from spec doc: spec doc labels P="limited
# to influencing legislative changes" and N="face_to_face only" — neither
# atomizes onto the 8-enum Set[enum] cell content. Module projects scope.4
# parallel to scope.1: full 8-set → 2; non-empty proper subset → 1; empty → 0.
# Documented in module docstring.
# ---------------------------------------------------------------------------


_SCOPE_1_FULL: frozenset[str] = frozenset({
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
_SCOPE_4_FULL: frozenset[str] = frozenset({
    "oral",
    "written",
    "electronic",
    "virtual",
    "meeting_organizing",
    "events",
    "phone_calls",
    "emails",
})

_SCOPE_1_ROW = "def_lobbyist_actor_types"
_SCOPE_2_COMP_ROW = "lobbyist_registration_threshold_compensation_dollars"
_SCOPE_2_EXP_ROW = "lobbyist_registration_threshold_expenditure_dollars"
_SCOPE_2_TIME_ROW = "lobbyist_registration_threshold_time_percent"
_SCOPE_3_LEG_ROW = "def_target_legislative_branch"
_SCOPE_3_EXEC_ROW = "def_target_executive_agency"
_SCOPE_3_GOV_ROW = "def_target_governors_office"
_SCOPE_3_LEG_STAFF_ROW = "def_target_legislative_staff"
_SCOPE_3_EXEC_STAFF_ROW = "def_target_executive_staff"
_SCOPE_4_ROW = "def_lobbying_activity_types"


# --- scope.1 (set-membership 3-tier over 9 lobbyist actor types) ---


def test_scope_1_two_when_cell_is_full_set():
    cells = {_SCOPE_1_ROW: _typed_cell(set(_SCOPE_1_FULL))}
    assert project_focal_2024_item("focal_2024.scope.1", cells) == 2


def test_scope_1_one_when_cell_has_prof_consultant_plus_others():
    """``cell ⊃ {prof_consultant} AND cell ≠ full`` → partly."""
    cells = {_SCOPE_1_ROW: _typed_cell({"prof_consultant", "inhouse_company"})}
    assert project_focal_2024_item("focal_2024.scope.1", cells) == 1


def test_scope_1_zero_when_cell_is_only_prof_consultant():
    cells = {_SCOPE_1_ROW: _typed_cell({"prof_consultant"})}
    assert project_focal_2024_item("focal_2024.scope.1", cells) == 0


def test_scope_1_zero_when_cell_is_empty_set():
    cells = {_SCOPE_1_ROW: _typed_cell(set())}
    assert project_focal_2024_item("focal_2024.scope.1", cells) == 0


def test_scope_1_zero_when_cell_lacks_prof_consultant():
    """Without prof_consultant, the 'partly' predicate fails — narrow → 0."""
    cells = {_SCOPE_1_ROW: _typed_cell({"law_firm", "think_tank"})}
    assert project_focal_2024_item("focal_2024.scope.1", cells) == 0


def test_scope_1_unable_when_row_missing():
    assert project_focal_2024_item("focal_2024.scope.1", {}) == UNABLE_TO_EVALUATE


def test_scope_1_unable_when_axis_none():
    cells = {_SCOPE_1_ROW: _typed_cell(None)}
    assert (
        project_focal_2024_item("focal_2024.scope.1", cells) == UNABLE_TO_EVALUATE
    )


# --- scope.2 (calibrated 3-tier; OQ1 defaults $1000 / 5% time) ---


def test_scope_2_two_when_no_thresholds_at_all():
    """no thresholds → ``any_threshold=False`` → yes (anyone must register)."""
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell(None),
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell(None),
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 2


def test_scope_2_one_when_low_compensation_threshold_only():
    """threshold exists but below cutoff → partly."""
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell("500"),  # below $1000 cutoff
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell(None),
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 1


def test_scope_2_zero_when_compensation_above_cutoff():
    """significant compensation threshold → no."""
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell("3000"),  # above $1000 cutoff
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell(None),
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 0


def test_scope_2_zero_when_expenditure_above_cutoff():
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell(None),
        _SCOPE_2_EXP_ROW: _typed_cell("2500"),  # above $1000 cutoff
        _SCOPE_2_TIME_ROW: _typed_cell(None),
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 0


def test_scope_2_zero_when_time_above_cutoff():
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell(None),
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell("20"),  # 20% > 5% cutoff
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 0


def test_scope_2_one_when_time_below_cutoff():
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell(None),
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell("3"),  # 3% < 5% cutoff
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 1


def test_scope_2_zero_when_us_lda_like_values():
    """US LDA validation anchor: $3000 compensation + 20% time → published 0."""
    cells = {
        _SCOPE_2_COMP_ROW: _typed_cell("3000"),
        _SCOPE_2_EXP_ROW: _typed_cell(None),
        _SCOPE_2_TIME_ROW: _typed_cell("20"),
    }
    assert project_focal_2024_item("focal_2024.scope.2", cells) == 0


def test_scope_2_unable_when_all_three_rows_missing():
    """Distinct from "all three present with None axis" — row-absent means
    we don't know whether thresholds exist in law at all."""
    assert project_focal_2024_item("focal_2024.scope.2", {}) == UNABLE_TO_EVALUATE


# --- scope.3 (AND-projection over 5 binary cells; staff-AND-strict per OQ2) ---


def _scope_3_cells(leg: bool, exec_: bool, gov: bool, leg_staff: bool, exec_staff: bool):
    return {
        _SCOPE_3_LEG_ROW: _binary_cell(leg),
        _SCOPE_3_EXEC_ROW: _binary_cell(exec_),
        _SCOPE_3_GOV_ROW: _binary_cell(gov),
        _SCOPE_3_LEG_STAFF_ROW: _binary_cell(leg_staff),
        _SCOPE_3_EXEC_STAFF_ROW: _binary_cell(exec_staff),
    }


def test_scope_3_two_when_all_five_targets_true():
    cells = _scope_3_cells(True, True, True, True, True)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 2


def test_scope_3_one_when_major_branches_but_no_staff():
    """3 major branches TRUE + both staff cells FALSE → partly."""
    cells = _scope_3_cells(True, True, True, False, False)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 1


def test_scope_3_one_when_major_branches_and_only_leg_staff():
    """OQ2 strict-AND on staff: only legislative_staff TRUE → staff_in_scope=False → partly."""
    cells = _scope_3_cells(True, True, True, True, False)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 1


def test_scope_3_one_when_major_branches_and_only_exec_staff():
    """OQ2 strict-AND on staff: only executive_staff TRUE → staff_in_scope=False → partly."""
    cells = _scope_3_cells(True, True, True, False, True)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 1


def test_scope_3_zero_when_legislative_branch_missing():
    """Any major branch FALSE → no (regardless of staff)."""
    cells = _scope_3_cells(False, True, True, True, True)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 0


def test_scope_3_zero_when_executive_agency_missing():
    cells = _scope_3_cells(True, False, True, True, True)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 0


def test_scope_3_zero_when_governors_office_missing():
    cells = _scope_3_cells(True, True, False, True, True)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 0


def test_scope_3_zero_when_all_five_targets_false():
    cells = _scope_3_cells(False, False, False, False, False)
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 0


def test_scope_3_unable_when_a_major_branch_cell_missing():
    """If we don't know whether a major branch is in scope, we can't
    decide between major_branches True (→ 1 or 2) and False (→ 0)."""
    cells = _scope_3_cells(True, True, True, True, True)
    del cells[_SCOPE_3_GOV_ROW]
    assert (
        project_focal_2024_item("focal_2024.scope.3", cells) == UNABLE_TO_EVALUATE
    )


def test_scope_3_unable_when_a_staff_cell_missing_but_major_branches_true():
    """All major branches TRUE but a staff cell missing → can't decide
    between 2 (full) and 1 (partly) → UNABLE."""
    cells = _scope_3_cells(True, True, True, True, True)
    del cells[_SCOPE_3_EXEC_STAFF_ROW]
    assert (
        project_focal_2024_item("focal_2024.scope.3", cells) == UNABLE_TO_EVALUATE
    )


def test_scope_3_zero_when_staff_cells_missing_but_major_branch_false():
    """Major branch FALSE — the answer is 0 regardless of staff cells.
    Don't UNABLE on staff-cell-missing when major-branches-failure has
    already determined the answer."""
    cells = {
        _SCOPE_3_LEG_ROW: _binary_cell(True),
        _SCOPE_3_EXEC_ROW: _binary_cell(False),
        _SCOPE_3_GOV_ROW: _binary_cell(True),
        # staff cells missing
    }
    assert project_focal_2024_item("focal_2024.scope.3", cells) == 0


# --- scope.4 (set-membership 3-tier over 8 activity types) ---
#
# Projection parallel to scope.1: full 8-set → 2; non-empty proper subset
# → 1; empty (or axis None) → 0. Spec doc's P/N labels
# ("limited to influencing legislative changes" / "{face_to_face} only")
# don't atomize onto the 8-enum cell content; module docstring documents
# this divergence.


def test_scope_4_two_when_cell_is_full_set():
    cells = {_SCOPE_4_ROW: _typed_cell(set(_SCOPE_4_FULL))}
    assert project_focal_2024_item("focal_2024.scope.4", cells) == 2


def test_scope_4_one_when_cell_is_non_empty_proper_subset():
    cells = {_SCOPE_4_ROW: _typed_cell({"oral", "written", "electronic"})}
    assert project_focal_2024_item("focal_2024.scope.4", cells) == 1


def test_scope_4_zero_when_cell_is_empty_set():
    cells = {_SCOPE_4_ROW: _typed_cell(set())}
    assert project_focal_2024_item("focal_2024.scope.4", cells) == 0


def test_scope_4_unable_when_row_missing():
    assert project_focal_2024_item("focal_2024.scope.4", {}) == UNABLE_TO_EVALUATE


def test_scope_4_unable_when_axis_none():
    cells = {_SCOPE_4_ROW: _typed_cell(None)}
    assert (
        project_focal_2024_item("focal_2024.scope.4", cells) == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Excluded items regression guard
# ---------------------------------------------------------------------------


def test_excluded_items_contains_revolving_door_2():
    """``revolving_door.2`` (database of officials in cooling-off period) is
    OUT per FOCAL-1 user-decision 2026-05-13 — enforcement-adjacent, not
    disclosure-side."""
    assert "focal_2024.revolving_door.2" in EXCLUDED_ITEMS


def test_excluded_item_raises_keyerror_on_dispatch():
    with pytest.raises(KeyError):
        project_focal_2024_item("focal_2024.revolving_door.2", {})


def test_unknown_item_raises_keyerror_on_dispatch():
    with pytest.raises(KeyError):
        project_focal_2024_item("focal_2024.not_a_real_item", {})

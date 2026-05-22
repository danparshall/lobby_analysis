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

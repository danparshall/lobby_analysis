"""Per-item projection tests for Newmark 2017.

Each test exercises a single per-item helper against a hand-built
``cells`` dict keyed by v2 compendium row id. Cell shape::

    cells[row_id] = {
        "legal_availability": <typed>,
        "practical_availability": <typed>,    # ignored by Newmark
    }

Helpers return ``int | Literal["unable_to_evaluate"]``:

* ``1`` if the state's statute includes the provision.
* ``0`` if not.
* ``"unable_to_evaluate"`` if required input cells are missing.

The 5 ``prohib.*`` items are excluded; no helpers are defined.
``test_newmark_2017_aggregation.py`` regression-guards those exclusions.
"""

from __future__ import annotations

from decimal import Decimal

from lobby_analysis.projections.newmark_2017 import (
    UNABLE_TO_EVALUATE,
    project_gifts_actor_agnostic_or,
    project_newmark_2017_item,
)


# ---------------------------------------------------------------------------
# Helpers for fixture construction
# ---------------------------------------------------------------------------


def _binary_cell(value: bool | None) -> dict[str, bool | None]:
    return {"legal_availability": value}


# ---------------------------------------------------------------------------
# Definitions battery — 4 plain binary items
#
# def.legislative_lobbying        -> def_target_legislative_branch
# def.administrative_agency_lobbying -> def_target_executive_agency
# def.elective_officials_as_lobbyists -> def_actor_class_elected_officials
# def.public_employees_as_lobbyists -> def_actor_class_public_employees
# ---------------------------------------------------------------------------


def test_def_legislative_lobbying_true_when_target_legislative_branch_true():
    cells = {"def_target_legislative_branch": _binary_cell(True)}
    assert project_newmark_2017_item("newmark_2017.def.legislative_lobbying", cells) == 1


def test_def_legislative_lobbying_false_when_target_legislative_branch_false():
    """Honest 0 for the counterfactual state — empirical 2015 uniformity
    is a property of the world, not the projection."""
    cells = {"def_target_legislative_branch": _binary_cell(False)}
    assert project_newmark_2017_item("newmark_2017.def.legislative_lobbying", cells) == 0


def test_def_legislative_lobbying_unable_when_row_missing():
    assert (
        project_newmark_2017_item("newmark_2017.def.legislative_lobbying", {})
        == UNABLE_TO_EVALUATE
    )


def test_def_administrative_agency_lobbying_true():
    cells = {"def_target_executive_agency": _binary_cell(True)}
    assert (
        project_newmark_2017_item(
            "newmark_2017.def.administrative_agency_lobbying", cells
        )
        == 1
    )


def test_def_elective_officials_as_lobbyists_true():
    cells = {"def_actor_class_elected_officials": _binary_cell(True)}
    assert (
        project_newmark_2017_item(
            "newmark_2017.def.elective_officials_as_lobbyists", cells
        )
        == 1
    )


def test_def_public_employees_as_lobbyists_true():
    cells = {"def_actor_class_public_employees": _binary_cell(True)}
    assert (
        project_newmark_2017_item(
            "newmark_2017.def.public_employees_as_lobbyists", cells
        )
        == 1
    )


# ---------------------------------------------------------------------------
# Definitions battery — 3 typed-cell IS NOT NULL items
#
# def.compensation_standard -> lobbyist_registration_threshold_compensation_dollars
# def.expenditure_standard  -> lobbyist_registration_threshold_expenditure_dollars
# def.time_standard         -> lobbyist_registration_threshold_time_percent
#
# Semantics: row absent -> unable_to_evaluate; axis None or "" -> 0;
# any other value (including Decimal(0), "0") -> 1.
# ---------------------------------------------------------------------------


def test_compensation_standard_one_when_threshold_present():
    cells = {
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": Decimal("500.00")
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.compensation_standard", cells) == 1
    )


def test_compensation_standard_zero_when_axis_none():
    cells = {
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": None
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.compensation_standard", cells) == 0
    )


def test_compensation_standard_zero_when_axis_empty_string():
    cells = {
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": ""
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.compensation_standard", cells) == 0
    )


def test_compensation_standard_one_when_threshold_is_decimal_zero():
    """Per the spec: ``Decimal("0")`` is non-null. A state defining
    lobbyists with $0 compensation threshold has a threshold *that
    exists* — score 1, not 0."""
    cells = {
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": Decimal("0")
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.compensation_standard", cells) == 1
    )


def test_compensation_standard_unable_when_row_missing():
    assert (
        project_newmark_2017_item("newmark_2017.def.compensation_standard", {})
        == UNABLE_TO_EVALUATE
    )


def test_expenditure_standard_one_when_threshold_present():
    cells = {
        "lobbyist_registration_threshold_expenditure_dollars": {
            "legal_availability": Decimal("250.00")
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.expenditure_standard", cells) == 1
    )


def test_expenditure_standard_zero_when_axis_none():
    cells = {
        "lobbyist_registration_threshold_expenditure_dollars": {
            "legal_availability": None
        }
    }
    assert (
        project_newmark_2017_item("newmark_2017.def.expenditure_standard", cells) == 0
    )


def test_time_standard_one_when_typed_value_present():
    """TimeThreshold is structured (magnitude + unit), so any non-empty
    representation projects to 1. The raw-string form here represents
    the federal LDA's '20% of work time' shape."""
    cells = {
        "lobbyist_registration_threshold_time_percent": {
            "legal_availability": "20%"
        }
    }
    assert project_newmark_2017_item("newmark_2017.def.time_standard", cells) == 1


def test_time_standard_zero_when_axis_none():
    cells = {
        "lobbyist_registration_threshold_time_percent": {
            "legal_availability": None
        }
    }
    assert project_newmark_2017_item("newmark_2017.def.time_standard", cells) == 0


def test_time_standard_unable_when_row_missing():
    assert (
        project_newmark_2017_item("newmark_2017.def.time_standard", {})
        == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Disclosure battery — gifts actor-agnostic OR helper
# ---------------------------------------------------------------------------


_GIFTS_LOB = "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging"
_GIFTS_PRIN = "principal_spending_report_includes_gifts_entertainment_transport_lodging"


def test_gifts_or_one_when_only_lobbyist_side_true():
    cells = {
        _GIFTS_LOB: _binary_cell(True),
        _GIFTS_PRIN: _binary_cell(False),
    }
    assert project_gifts_actor_agnostic_or(cells) == 1


def test_gifts_or_one_when_only_principal_side_true():
    cells = {
        _GIFTS_LOB: _binary_cell(False),
        _GIFTS_PRIN: _binary_cell(True),
    }
    assert project_gifts_actor_agnostic_or(cells) == 1


def test_gifts_or_one_when_both_sides_true():
    cells = {
        _GIFTS_LOB: _binary_cell(True),
        _GIFTS_PRIN: _binary_cell(True),
    }
    assert project_gifts_actor_agnostic_or(cells) == 1


def test_gifts_or_zero_when_both_sides_false():
    cells = {
        _GIFTS_LOB: _binary_cell(False),
        _GIFTS_PRIN: _binary_cell(False),
    }
    assert project_gifts_actor_agnostic_or(cells) == 0


def test_gifts_or_unable_when_both_rows_missing():
    assert project_gifts_actor_agnostic_or({}) == UNABLE_TO_EVALUATE


def test_gifts_or_unable_when_one_side_false_other_missing():
    """A False on one side with the other unknown can't rule out
    disclosure — return unable_to_evaluate rather than coerce to 0."""
    cells = {_GIFTS_LOB: _binary_cell(False)}
    assert project_gifts_actor_agnostic_or(cells) == UNABLE_TO_EVALUATE


def test_gifts_or_one_when_one_side_true_other_missing():
    """A True on one side wins the OR regardless of the other side."""
    cells = {_GIFTS_LOB: _binary_cell(True)}
    assert project_gifts_actor_agnostic_or(cells) == 1


def test_gifts_item_dispatches_to_gifts_or_helper():
    cells = {
        _GIFTS_LOB: _binary_cell(True),
        _GIFTS_PRIN: _binary_cell(False),
    }
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.expenditures_benefiting_officials", cells
        )
        == 1
    )


# ---------------------------------------------------------------------------
# Disclosure battery — 6 plain binary items
# ---------------------------------------------------------------------------


def test_disclosure_influence_legislation_or_admin_true():
    cells = {"lobbyist_spending_report_includes_general_subject_matter": _binary_cell(True)}
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.influence_legislation_or_admin", cells
        )
        == 1
    )


def test_disclosure_compensation_by_employer_reads_by_payer_row():
    """v2 row name is ``_by_payer`` (Sunlight-mapping rename); spec doc
    used ``_by_client``. Test enforces the rename."""
    cells = {
        "lobbyist_spending_report_includes_compensation_broken_down_by_payer": _binary_cell(
            True
        )
    }
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.compensation_by_employer", cells
        )
        == 1
    )


def test_disclosure_total_compensation_true():
    cells = {"lobbyist_spending_report_includes_total_compensation": _binary_cell(True)}
    assert (
        project_newmark_2017_item("newmark_2017.disclosure.total_compensation", cells)
        == 1
    )


def test_disclosure_categories_of_expenditures_true():
    cells = {"lobbyist_spending_report_categorizes_expenses_by_type": _binary_cell(True)}
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.categories_of_expenditures", cells
        )
        == 1
    )


def test_disclosure_total_expenditures_true():
    cells = {"lobbyist_spending_report_includes_total_expenditures": _binary_cell(True)}
    assert (
        project_newmark_2017_item("newmark_2017.disclosure.total_expenditures", cells)
        == 1
    )


def test_disclosure_contributions_from_others_reads_promoted_row():
    """Newmark-2017-distinctive observable. v2 promoted the row to the
    ``_spending_report_`` family during freeze; spec doc used a shorter
    ``_report_`` form."""
    cells = {
        "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying": _binary_cell(
            True
        )
    }
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.contributions_from_others", cells
        )
        == 1
    )


def test_disclosure_contributions_from_others_false():
    cells = {
        "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying": _binary_cell(
            False
        )
    }
    assert (
        project_newmark_2017_item(
            "newmark_2017.disclosure.contributions_from_others", cells
        )
        == 0
    )

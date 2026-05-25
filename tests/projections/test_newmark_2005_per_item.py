"""Per-item projection tests for Newmark 2005.

Each test exercises a single per-item helper. Most items reuse the
Newmark 2017 mapping (verbatim row id and read rule); per-item tests
here focus on the items that differ from 2017:

* The frequency-of-reporting item (NEW 8-cell cadence OR helper).
* The 7 reused def items + 6 reused disclosure items get spot-check
  coverage to confirm dispatcher wiring (the rules themselves are
  covered in ``test_newmark_2017_per_item.py``).
* The gifts actor-agnostic OR is imported from ``newmark_2017``; a
  dispatcher test confirms the import.

Regression-guards in ``test_newmark_2005_aggregation.py`` cover the
falsified-2017-speculation row (``contributions_from_others`` is NOT in
Newmark 2005) and the exclusion of the 4 ``prohib_*`` items + the 1
``penalty_stringency_2003`` item.
"""

from __future__ import annotations

from decimal import Decimal

from lobby_analysis.projections.newmark_2005 import (
    UNABLE_TO_EVALUATE,
    project_cadence_more_than_annual_or,
    project_newmark_2005_item,
)


def _binary_cell(value: bool | None) -> dict[str, bool | None]:
    return {"legal_availability": value}


# ---------------------------------------------------------------------------
# Definitions battery — spot-check dispatcher (rules covered in 2017)
# ---------------------------------------------------------------------------


def test_def_legislative_lobbying_dispatches_to_binary_helper():
    cells = {"def_target_legislative_branch": _binary_cell(True)}
    assert project_newmark_2005_item("newmark_2005.def_legislative_lobbying", cells) == 1


def test_def_compensation_standard_dispatches_to_typed_helper():
    cells = {
        "lobbyist_registration_threshold_compensation_dollars": {
            "legal_availability": Decimal("500.00")
        }
    }
    assert (
        project_newmark_2005_item("newmark_2005.def_compensation_standard", cells) == 1
    )


def test_def_time_standard_zero_when_axis_none():
    cells = {
        "lobbyist_registration_threshold_time_percent": {"legal_availability": None}
    }
    assert project_newmark_2005_item("newmark_2005.def_time_standard", cells) == 0


def test_def_elected_officials_unable_when_row_missing():
    assert (
        project_newmark_2005_item(
            "newmark_2005.def_elected_officials_as_lobbyists", {}
        )
        == UNABLE_TO_EVALUATE
    )


# ---------------------------------------------------------------------------
# Frequency battery — 8-cell cadence OR helper
# ---------------------------------------------------------------------------


_CADENCE_ROWS = (
    "lobbyist_spending_report_cadence_includes_monthly",
    "lobbyist_spending_report_cadence_includes_quarterly",
    "lobbyist_spending_report_cadence_includes_triannual",
    "lobbyist_spending_report_cadence_includes_semiannual",
    "principal_spending_report_cadence_includes_monthly",
    "principal_spending_report_cadence_includes_quarterly",
    "principal_spending_report_cadence_includes_triannual",
    "principal_spending_report_cadence_includes_semiannual",
)


def _all_cadence(value: bool) -> dict[str, dict]:
    return {row: _binary_cell(value) for row in _CADENCE_ROWS}


def test_cadence_or_zero_when_all_8_false():
    assert project_cadence_more_than_annual_or(_all_cadence(False)) == 0


def test_cadence_or_one_when_all_8_true():
    assert project_cadence_more_than_annual_or(_all_cadence(True)) == 1


def test_cadence_or_one_when_only_lobbyist_monthly_true():
    cells = _all_cadence(False)
    cells["lobbyist_spending_report_cadence_includes_monthly"] = _binary_cell(True)
    assert project_cadence_more_than_annual_or(cells) == 1


def test_cadence_or_one_when_only_principal_semiannual_true():
    cells = _all_cadence(False)
    cells["principal_spending_report_cadence_includes_semiannual"] = _binary_cell(True)
    assert project_cadence_more_than_annual_or(cells) == 1


def test_cadence_or_one_when_4_lobbyist_cells_true():
    cells = _all_cadence(False)
    for row in _CADENCE_ROWS[:4]:  # all 4 lobbyist-side cells
        cells[row] = _binary_cell(True)
    assert project_cadence_more_than_annual_or(cells) == 1


def test_cadence_or_unable_when_all_8_missing():
    assert project_cadence_more_than_annual_or({}) == UNABLE_TO_EVALUATE


def test_cadence_or_unable_when_7_cells_present_1_missing_and_no_true():
    """Strict missing-cell semantics: a known-FALSE majority is not
    enough to conclude FALSE if any cell is unknown — the missing cell
    could be TRUE."""
    cells = _all_cadence(False)
    del cells["lobbyist_spending_report_cadence_includes_monthly"]
    assert project_cadence_more_than_annual_or(cells) == UNABLE_TO_EVALUATE


def test_cadence_or_one_when_known_true_overrides_missing():
    """A known TRUE short-circuits the OR — the missing cell doesn't
    matter once any cell is known TRUE."""
    cells = _all_cadence(False)
    cells["lobbyist_spending_report_cadence_includes_quarterly"] = _binary_cell(True)
    del cells["principal_spending_report_cadence_includes_monthly"]
    assert project_cadence_more_than_annual_or(cells) == 1


def test_cadence_or_does_not_read_annual_cell():
    """Negative-case sanity: only the ``_annual`` cell is TRUE. Annual
    cadence is the negative case for ">annual"; helper must return 0."""
    cells = _all_cadence(False)
    # Add the annual-cadence cells with TRUE — they should NOT be read.
    cells["lobbyist_spending_report_cadence_includes_annual"] = _binary_cell(True)
    cells["principal_spending_report_cadence_includes_annual"] = _binary_cell(True)
    assert project_cadence_more_than_annual_or(cells) == 0


def test_cadence_or_does_not_read_other_cell():
    """Same as above for the ``_other`` cadence cell."""
    cells = _all_cadence(False)
    cells["lobbyist_spending_report_cadence_includes_other"] = _binary_cell(True)
    cells["principal_spending_report_cadence_includes_other"] = _binary_cell(True)
    assert project_cadence_more_than_annual_or(cells) == 0


def test_freq_item_dispatches_to_cadence_helper():
    cells = _all_cadence(False)
    cells["lobbyist_spending_report_cadence_includes_quarterly"] = _binary_cell(True)
    assert (
        project_newmark_2005_item("newmark_2005.freq_reporting_more_than_annual", cells)
        == 1
    )


# ---------------------------------------------------------------------------
# Disclosure battery — spot-check dispatcher
# ---------------------------------------------------------------------------


def test_disclosure_influence_legislation_or_admin_true():
    cells = {"lobbyist_spending_report_includes_general_subject_matter": _binary_cell(True)}
    assert (
        project_newmark_2005_item(
            "newmark_2005.disc_legislative_admin_action_to_influence", cells
        )
        == 1
    )


def test_disclosure_compensation_by_employer_reads_by_payer_row():
    cells = {
        "lobbyist_spending_report_includes_compensation_broken_down_by_payer": _binary_cell(
            True
        )
    }
    assert (
        project_newmark_2005_item("newmark_2005.disc_compensation_by_employer", cells)
        == 1
    )


def test_disclosure_total_expenditures_reads_2017_introduced_row():
    """Reuses the row Newmark 2017 mapping introduced. No new row in 2005."""
    cells = {"lobbyist_spending_report_includes_total_expenditures": _binary_cell(True)}
    assert (
        project_newmark_2005_item("newmark_2005.disc_total_expenditures", cells) == 1
    )


# ---------------------------------------------------------------------------
# Gifts OR — imported from newmark_2017
# ---------------------------------------------------------------------------


def test_gifts_item_dispatches_to_imported_helper():
    cells = {
        "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging": _binary_cell(
            True
        ),
        "principal_spending_report_includes_gifts_entertainment_transport_lodging": _binary_cell(
            False
        ),
    }
    assert (
        project_newmark_2005_item(
            "newmark_2005.disc_expenditures_benefiting_officials", cells
        )
        == 1
    )


def test_gifts_or_helper_is_the_same_object_as_in_newmark_2017():
    """Regression-guard the import: the Newmark 2005 module must reuse
    Newmark 2017's helper rather than declaring its own copy."""
    from lobby_analysis.projections import newmark_2005, newmark_2017

    # The helper is exposed under newmark_2017's name and is the same
    # function object the 2005 dispatcher calls.
    from lobby_analysis.projections.newmark_2017 import project_gifts_actor_agnostic_or as helper_2017

    assert helper_2017 is newmark_2017.project_gifts_actor_agnostic_or
    # newmark_2005 imports the helper at module level; check the name is
    # bound in the 2005 module namespace.
    assert newmark_2005.project_gifts_actor_agnostic_or is helper_2017

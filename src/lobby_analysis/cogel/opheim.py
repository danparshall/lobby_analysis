"""Opheim 1991 cross-validation: 22 binary items projected from COGEL v2 CSVs.

See ``docs/active/cogel-extraction/plans/20260507_opheim_cross_validation.md``
for the design and ``papers/text/Opheim_1991__state_lobby_regulation.txt`` §III
for the coding rules. The 2026-05-12 convo summary records the four mapping
calls made during Phase 1 implementation (freq rule, sources-of-income
provisional mapping, other-influence-activities any-of, penalties-amount
column).

Each item is one row of ``OPHEIM_ITEMS``: an ``OpheimItem`` dataclass with
the item_id, dimension, Opheim's wording, the COGEL table it lifts from,
the column key(s) the encoder reads, and the encoder callable itself.
The encoder takes a CSV row dict and returns 0 or 1.

``score_state`` rolls up the 22 encoders against a single state's per-table
row dicts.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

RowDict = dict[str, str]
Encoder = Callable[[RowDict], int]


@dataclass(frozen=True)
class OpheimItem:
    """One of Opheim 1991's 22 binary lobby-regulation index items."""

    item_id: str
    dimension: str  # "definitions" | "disclosure" | "oversight"
    description: str
    cogel_table: int  # 28, 29, 30, or 31
    cogel_column_keys: tuple[str, ...]
    encoder: Encoder


# ---------------------------------------------------------------------------
# Encoder factories
# ---------------------------------------------------------------------------


def _marker(col: str) -> Encoder:
    """1 if ``row[col]`` contains an asterisk, else 0."""

    def _f(row: RowDict) -> int:
        v = row.get(col, "") or ""
        return 1 if "*" in v else 0

    return _f


def _any_marker(*cols: str) -> Encoder:
    """1 if any of ``row[col]`` for ``col`` in ``cols`` contains an asterisk."""

    def _f(row: RowDict) -> int:
        for c in cols:
            v = row.get(c, "") or ""
            if "*" in v:
                return 1
        return 0

    return _f


def _freq_monthly(col: str) -> Encoder:
    """Opheim §III: 1 if reporting is monthly OR both in and out of session.

    Quarterly / semi-annually / annually all score 0.
    """

    def _f(row: RowDict) -> int:
        v = (row.get(col, "") or "").lower()
        if "monthly" in v:
            return 1
        if "in and out" in v or "in-and-out" in v:
            return 1
        return 0

    return _f


def _penalties(col: str) -> Encoder:
    """T31 penalties: column carries dollar amounts, not markers.

    1 if cell contains ``*`` (legacy marker) OR any digit (the dollar
    amount itself). Cells like ``N.A.``, em-dash, underscore, or empty
    score 0.
    """

    def _f(row: RowDict) -> int:
        v = row.get(col, "") or ""
        if "*" in v:
            return 1
        if any(c.isdigit() for c in v):
            return 1
        return 0

    return _f


# ---------------------------------------------------------------------------
# The 22 items — order matches Opheim §III paragraph order.
# ---------------------------------------------------------------------------


OPHEIM_ITEMS: list[OpheimItem] = [
    # ---- Definitions (7 items, T28 cols 0-6) --------------------------
    OpheimItem(
        item_id="def_legislative_lobbying",
        dimension="definitions",
        description='"legislative" lobbying as a criterion for defining a lobbyist',
        cogel_table=28,
        cogel_column_keys=("def_legislative_parliamentary",),
        encoder=_marker("def_legislative_parliamentary"),
    ),
    OpheimItem(
        item_id="def_administrative_lobbying",
        dimension="definitions",
        description='"administrative" lobbying as a criterion',
        cogel_table=28,
        cogel_column_keys=("def_administrative_agency",),
        encoder=_marker("def_administrative_agency"),
    ),
    OpheimItem(
        item_id="def_elective_officials_as_lobbyists",
        dimension="definitions",
        description='"elective officials" designated as lobbyists',
        cogel_table=28,
        cogel_column_keys=("def_elective_officials_as_lobbyists",),
        encoder=_marker("def_elective_officials_as_lobbyists"),
    ),
    OpheimItem(
        item_id="def_public_employees_as_lobbyists",
        dimension="definitions",
        description='"public employees" designated as lobbyists',
        cogel_table=28,
        cogel_column_keys=("def_public_employees_as_lobbyists",),
        encoder=_marker("def_public_employees_as_lobbyists"),
    ),
    OpheimItem(
        item_id="def_compensation_standard",
        dimension="definitions",
        description="compensation standard delineates lobbying activity",
        cogel_table=28,
        cogel_column_keys=("def_compensation_standard",),
        encoder=_marker("def_compensation_standard"),
    ),
    OpheimItem(
        item_id="def_expenditure_standard",
        dimension="definitions",
        description="expenditure standard delineates lobbying activity",
        cogel_table=28,
        cogel_column_keys=("def_expenditure_standard",),
        encoder=_marker("def_expenditure_standard"),
    ),
    OpheimItem(
        item_id="def_time_standard",
        dimension="definitions",
        description="time standard delineates lobbying activity",
        cogel_table=28,
        cogel_column_keys=("def_time_standard",),
        encoder=_marker("def_time_standard"),
    ),
    # ---- Disclosure (8 items, T29) ------------------------------------
    OpheimItem(
        item_id="freq_monthly_or_in_out_session",
        dimension="disclosure",
        description="reporting frequency: monthly during session OR both in and out of session",
        cogel_table=29,
        cogel_column_keys=("freq_lobbyist",),
        encoder=_freq_monthly("freq_lobbyist"),
    ),
    OpheimItem(
        item_id="disclose_total_spending",
        dimension="disclosure",
        description="total spending disclosed",
        cogel_table=29,
        cogel_column_keys=("disclose_total_expenditures",),
        encoder=_marker("disclose_total_expenditures"),
    ),
    OpheimItem(
        item_id="disclose_spending_by_category",
        dimension="disclosure",
        description="spending broken down by category",
        cogel_table=29,
        cogel_column_keys=("disclose_categories_of_expenditures",),
        encoder=_marker("disclose_categories_of_expenditures"),
    ),
    OpheimItem(
        item_id="disclose_expenditures_benefiting_public_employees",
        dimension="disclosure",
        description=(
            "expenditures benefiting public employees including gifts "
            "(Opheim's wording; COGEL column header says 'officials')"
        ),
        cogel_table=29,
        cogel_column_keys=("disclose_expenditures_benefiting_officials",),
        encoder=_marker("disclose_expenditures_benefiting_officials"),
    ),
    OpheimItem(
        item_id="disclose_legislation_approved_or_opposed",
        dimension="disclosure",
        description="legislation approved or opposed by the lobbyist",
        cogel_table=29,
        cogel_column_keys=("disclose_legislation_admin_action",),
        encoder=_marker("disclose_legislation_admin_action"),
    ),
    OpheimItem(
        item_id="disclose_sources_of_income",
        dimension="disclosure",
        description=(
            "sources of income — provisional best-fit to T29 "
            "compensation_by_employer; weakly supported (see 2026-05-12 convo "
            "NJ/WA spot-check)"
        ),
        cogel_table=29,
        cogel_column_keys=("disclose_compensation_by_employer",),
        encoder=_marker("disclose_compensation_by_employer"),
    ),
    OpheimItem(
        item_id="disclose_total_income",
        dimension="disclosure",
        description="total income (compensation)",
        cogel_table=29,
        cogel_column_keys=("disclose_total_compensation",),
        encoder=_marker("disclose_total_compensation"),
    ),
    OpheimItem(
        item_id="disclose_other_influence_activities",
        dimension="disclosure",
        description=(
            "other activities constituting influence peddling or conflict of "
            "interest — any-of T29 contributions_for_lobbying + other (catch-all)"
        ),
        cogel_table=29,
        cogel_column_keys=("disclose_contributions_for_lobbying", "disclose_other"),
        encoder=_any_marker(
            "disclose_contributions_for_lobbying",
            "disclose_other",
        ),
    ),
    # ---- Oversight (7 items, T30 + T31) -------------------------------
    OpheimItem(
        item_id="review_thoroughness",
        dimension="oversight",
        description=(
            "review of all reports — any-of: desk-all, field-all, "
            "desk-or-field-all"
        ),
        cogel_table=30,
        cogel_column_keys=(
            "review_desk_all",
            "review_field_all",
            "review_desk_or_field_all",
        ),
        encoder=_any_marker(
            "review_desk_all",
            "review_field_all",
            "review_desk_or_field_all",
        ),
    ),
    OpheimItem(
        item_id="subpoena_witnesses",
        dimension="oversight",
        description="agency authority to subpoena witnesses",
        cogel_table=31,
        cogel_column_keys=("auth_subpoena_witnesses",),
        encoder=_marker("auth_subpoena_witnesses"),
    ),
    OpheimItem(
        item_id="subpoena_records",
        dimension="oversight",
        description="agency authority to subpoena records",
        cogel_table=31,
        cogel_column_keys=("auth_subpoena_records",),
        encoder=_marker("auth_subpoena_records"),
    ),
    OpheimItem(
        item_id="conduct_administrative_hearings",
        dimension="oversight",
        description="agency authority to conduct administrative hearings",
        cogel_table=31,
        cogel_column_keys=("auth_conduct_administrative_hearings",),
        encoder=_marker("auth_conduct_administrative_hearings"),
    ),
    OpheimItem(
        item_id="impose_administrative_fines",
        dimension="oversight",
        description="agency authority to impose administrative fines",
        cogel_table=31,
        cogel_column_keys=("auth_impose_administrative_fines",),
        encoder=_marker("auth_impose_administrative_fines"),
    ),
    OpheimItem(
        item_id="impose_administrative_penalties",
        dimension="oversight",
        description=(
            "agency authority to impose administrative penalties "
            "(T31 column is amount-bearing; encoder accepts '*' OR digit)"
        ),
        cogel_table=31,
        cogel_column_keys=("auth_impose_administrative_penalties_amount",),
        encoder=_penalties("auth_impose_administrative_penalties_amount"),
    ),
    OpheimItem(
        item_id="file_independent_court_actions",
        dimension="oversight",
        description="agency authority to file independent court actions",
        cogel_table=31,
        cogel_column_keys=("auth_file_independent_court_actions",),
        encoder=_marker("auth_file_independent_court_actions"),
    ),
]


# ---------------------------------------------------------------------------
# State-level rollup
# ---------------------------------------------------------------------------


def score_state(
    t28: RowDict,
    t29: RowDict,
    t30: RowDict,
    t31: RowDict,
) -> int:
    """Apply all 22 Opheim encoders to one state's row across the 4 COGEL tables.

    Returns the integer index score in [0, 22] (though Opheim's published range
    on the 47 in-scope states is [0, 18]).
    """
    by_table = {28: t28, 29: t29, 30: t30, 31: t31}
    return sum(item.encoder(by_table[item.cogel_table]) for item in OPHEIM_ITEMS)

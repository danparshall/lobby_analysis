"""Tests for Opheim 1991 cross-validation encoders (cogel-extraction Phase 1).

See `docs/active/cogel-extraction/plans/20260507_opheim_cross_validation.md`
for the design rationale and `docs/active/cogel-extraction/RESEARCH_LOG.md`
2026-05-11 entry for the three coding-rule resolutions used here.

The encoders are tested with minimal synthetic dicts so the tests are
independent of the v2 grid CSV shape. The Missouri smoke test pins
end-to-end behaviour against a real row whose Opheim score (5) is
documented in `data/compendium/opheim_1991_published_scores.csv`.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from lobby_analysis.cogel.opheim import OPHEIM_ITEMS, score_state


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _get(item_id: str):
    """Look up an OpheimItem by item_id; pytest fails clearly if missing."""
    for it in OPHEIM_ITEMS:
        if it.item_id == item_id:
            return it
    raise AssertionError(f"item_id not found in OPHEIM_ITEMS: {item_id}")


REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS = REPO_ROOT / "docs/active/cogel-extraction/results"
OPHEIM_SCORES_CSV = REPO_ROOT / "data/compendium/opheim_1991_published_scores.csv"


def _load_row(table: int, state: str) -> dict | None:
    path = RESULTS / f"cogel_1990_table{table}.csv"
    with path.open() as f:
        for r in csv.DictReader(f):
            if r["jurisdiction"] == state:
                return r
    return None


# ---------------------------------------------------------------------------
# Structural invariants on OPHEIM_ITEMS
# ---------------------------------------------------------------------------


def test_opheim_items_total_count_is_22():
    assert len(OPHEIM_ITEMS) == 22


def test_opheim_items_dimensions_split_7_8_7():
    from collections import Counter

    c = Counter(it.dimension for it in OPHEIM_ITEMS)
    assert c == {"definitions": 7, "disclosure": 8, "oversight": 7}


def test_opheim_item_ids_are_unique():
    ids = [it.item_id for it in OPHEIM_ITEMS]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Simple-marker encoders (18 items: 7 definitions + 6 disclosure cats
# + 5 oversight)
#
# Each item reads exactly one CSV column and returns 1 iff the cell
# contains "*". The parametrized pair below covers every such item with
# a 1-row and a 0-row to catch encoder/column wiring bugs.
# ---------------------------------------------------------------------------

SIMPLE_MARKER_ITEMS = [
    # Definitions (T28 columns 0-6)
    ("def_legislative_lobbying", "def_legislative_parliamentary"),
    ("def_administrative_lobbying", "def_administrative_agency"),
    ("def_elective_officials_as_lobbyists", "def_elective_officials_as_lobbyists"),
    ("def_public_employees_as_lobbyists", "def_public_employees_as_lobbyists"),
    ("def_compensation_standard", "def_compensation_standard"),
    ("def_expenditure_standard", "def_expenditure_standard"),
    ("def_time_standard", "def_time_standard"),
    # Disclosure categories 2-7 (item 1 is freq, item 8 is other-influence;
    # both special-cased below)
    ("disclose_total_spending", "disclose_total_expenditures"),
    ("disclose_spending_by_category", "disclose_categories_of_expenditures"),
    (
        "disclose_expenditures_benefiting_public_employees",
        "disclose_expenditures_benefiting_officials",
    ),
    ("disclose_legislation_approved_or_opposed", "disclose_legislation_admin_action"),
    ("disclose_sources_of_income", "disclose_compensation_by_employer"),
    ("disclose_total_income", "disclose_total_compensation"),
    # Oversight: subpoena/hearings/fines/court (5 markers; review and
    # penalties are special-cased below)
    ("subpoena_witnesses", "auth_subpoena_witnesses"),
    ("subpoena_records", "auth_subpoena_records"),
    ("conduct_administrative_hearings", "auth_conduct_administrative_hearings"),
    ("impose_administrative_fines", "auth_impose_administrative_fines"),
    ("file_independent_court_actions", "auth_file_independent_court_actions"),
]


@pytest.mark.parametrize("item_id,col", SIMPLE_MARKER_ITEMS)
def test_simple_marker_asterisk_scores_1(item_id, col):
    item = _get(item_id)
    assert item.encoder({col: "*"}) == 1


@pytest.mark.parametrize("item_id,col", SIMPLE_MARKER_ITEMS)
def test_simple_marker_em_dash_scores_0(item_id, col):
    item = _get(item_id)
    assert item.encoder({col: "—"}) == 0


# ---------------------------------------------------------------------------
# Frequency item (disclosure item #1 of 8)
#
# Opheim §III: "States which require reports to be filed monthly during
# the session or both in and out of session were coded 1, while states
# which require reports quarterly, semi-annually, or annually were
# coded 0."
# ---------------------------------------------------------------------------


def test_freq_monthly_during_session_scores_1():
    item = _get("freq_monthly_or_in_out_session")
    assert (
        item.encoder({"freq_lobbyist": "Monthly during legislative session"}) == 1
    )


def test_freq_in_and_out_of_session_scores_1():
    item = _get("freq_monthly_or_in_out_session")
    assert item.encoder({"freq_lobbyist": "In and out of session"}) == 1


def test_freq_annually_scores_0():
    item = _get("freq_monthly_or_in_out_session")
    assert item.encoder({"freq_lobbyist": "Annually"}) == 0


def test_freq_quarterly_scores_0():
    item = _get("freq_monthly_or_in_out_session")
    assert item.encoder({"freq_lobbyist": "Quarterly"}) == 0


def test_freq_three_reports_per_year_scores_0():
    # Missouri's actual T29 value; Opheim's binary rule treats this as
    # "less than monthly" → 0.
    item = _get("freq_monthly_or_in_out_session")
    assert item.encoder({"freq_lobbyist": "3 reports per year"}) == 0


# ---------------------------------------------------------------------------
# Other-influence-activities item (disclosure item #8 of 8)
#
# Opheim §III: "other activities that might constitute influence
# peddling or conflict of interest." T29 has two catch-all columns that
# fit this description: `disclose_contributions_for_lobbying`
# (peddling-side) and `disclose_other` (catch-all). Encoder uses
# any-of. See 2026-05-12 convo for the spot-check rationale.
# ---------------------------------------------------------------------------


def test_other_influence_contributions_only_scores_1():
    item = _get("disclose_other_influence_activities")
    assert (
        item.encoder(
            {
                "disclose_contributions_for_lobbying": "*",
                "disclose_other": "—",
            }
        )
        == 1
    )


def test_other_influence_other_only_scores_1():
    item = _get("disclose_other_influence_activities")
    assert (
        item.encoder(
            {
                "disclose_contributions_for_lobbying": "—",
                "disclose_other": "*",
            }
        )
        == 1
    )


def test_other_influence_both_absent_scores_0():
    item = _get("disclose_other_influence_activities")
    assert (
        item.encoder(
            {
                "disclose_contributions_for_lobbying": "—",
                "disclose_other": "—",
            }
        )
        == 0
    )


# ---------------------------------------------------------------------------
# Review thoroughness item (oversight item #1 of 7)
#
# Opheim §III line 141-142: "1 for review of all reports, 0 for less
# extensive review." T30 has three review_*_all columns (desk, field,
# desk-or-field) measuring the same scope=all dimension via different
# mechanisms. Encoder uses any-of per Phase 0 settlement.
# ---------------------------------------------------------------------------


def test_review_thoroughness_desk_all_scores_1():
    item = _get("review_thoroughness")
    assert (
        item.encoder(
            {
                "review_desk_all": "*",
                "review_field_all": "",
                "review_desk_or_field_all": "",
            }
        )
        == 1
    )


def test_review_thoroughness_field_all_scores_1():
    item = _get("review_thoroughness")
    assert (
        item.encoder(
            {
                "review_desk_all": "",
                "review_field_all": "*",
                "review_desk_or_field_all": "",
            }
        )
        == 1
    )


def test_review_thoroughness_desk_or_field_all_scores_1():
    item = _get("review_thoroughness")
    assert (
        item.encoder(
            {
                "review_desk_all": "",
                "review_field_all": "",
                "review_desk_or_field_all": "*",
            }
        )
        == 1
    )


def test_review_thoroughness_none_scores_0():
    item = _get("review_thoroughness")
    assert (
        item.encoder(
            {
                "review_desk_all": "",
                "review_field_all": "",
                "review_desk_or_field_all": "",
            }
        )
        == 0
    )


# ---------------------------------------------------------------------------
# Administrative penalties item (oversight item #6 of 7)
#
# T31 `auth_impose_administrative_penalties_amount` is an AMOUNT
# column, not a marker column. Cells contain numeric amounts
# (e.g. "1,000"), asterisks, or absence indicators (N.A./em-dash/
# underscore/empty). Encoder: 1 if cell contains "*" OR any digit.
# ---------------------------------------------------------------------------


def test_penalties_asterisk_scores_1():
    item = _get("impose_administrative_penalties")
    assert item.encoder({"auth_impose_administrative_penalties_amount": "*"}) == 1


def test_penalties_numeric_amount_scores_1():
    item = _get("impose_administrative_penalties")
    assert (
        item.encoder({"auth_impose_administrative_penalties_amount": "1,000"}) == 1
    )


def test_penalties_em_dash_scores_0():
    item = _get("impose_administrative_penalties")
    assert item.encoder({"auth_impose_administrative_penalties_amount": "—"}) == 0


def test_penalties_na_scores_0():
    item = _get("impose_administrative_penalties")
    assert (
        item.encoder({"auth_impose_administrative_penalties_amount": "N.A."}) == 0
    )


def test_penalties_empty_scores_0():
    item = _get("impose_administrative_penalties")
    assert item.encoder({"auth_impose_administrative_penalties_amount": ""}) == 0


# ---------------------------------------------------------------------------
# State-level rollup
#
# score_state takes the four per-table row dicts for one jurisdiction
# and returns the sum across all 22 encoders. Test feeds a synthetic
# state with a known vector and asserts the rollup matches.
# ---------------------------------------------------------------------------


def test_score_state_known_vector_sums_to_5():
    # 2 definitions + 1 freq + 1 disclose-category + 1 review = 5
    t28 = {
        "def_legislative_parliamentary": "*",
        "def_administrative_agency": "*",
    }
    t29 = {
        "freq_lobbyist": "Monthly during legislative session",
        "disclose_total_expenditures": "*",
    }
    t30 = {"review_desk_all": "*"}
    t31 = {}
    assert score_state(t28, t29, t30, t31) == 5


def test_score_state_all_zeros_sums_to_0():
    # No markers anywhere → score 0
    empty = {}
    assert score_state(empty, empty, empty, empty) == 0


# ---------------------------------------------------------------------------
# Real-data smoke test on Missouri
#
# Missouri's published Opheim score is 5 (data/compendium/
# opheim_1991_published_scores.csv). Asserting ±2 because of the
# 1988→1990 vintage gap and because frequency was sourced differently
# by Opheim.
# ---------------------------------------------------------------------------


def test_missouri_score_within_2_of_opheim():
    r28 = _load_row(28, "Missouri")
    r29 = _load_row(29, "Missouri")
    r30 = _load_row(30, "Missouri")
    r31 = _load_row(31, "Missouri")
    assert r28 is not None, "Missouri missing from T28"
    assert r29 is not None, "Missouri missing from T29"
    assert r30 is not None, "Missouri missing from T30"
    assert r31 is not None, "Missouri missing from T31"
    our_score = score_state(r28, r29, r30, r31)
    opheim_score = 5
    assert abs(our_score - opheim_score) <= 2, (
        f"Missouri delta exceeds ±2: ours={our_score}, opheim={opheim_score}"
    )


# ---------------------------------------------------------------------------
# 47-state coverage check
#
# Any state Opheim scored that is missing from one of our four CSVs
# blocks Phase 2 — we cannot score it. The test asserts presence,
# not correctness.
#
# As of 2026-05-12 (Phase 1), 11 Opheim states are missing from T28/T29
# (AZ, CO, DE, GA, IL, KY, NM, OH, PA, RI, SC), with DE/RI/SC also missing
# from T30 and DE from T31, plus IA missing from T29. The plan's "What
# could change" §1 anticipates this: v2 extraction needs to recover these
# states before Opheim cross-val is authoritative. Tracked as xfail
# (strict=False) so the suite stays green; when v2 extraction is fixed the
# test will XPASS and we can drop the marker.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=False,
    reason=(
        "11 Opheim states missing from T28/T29 as of 2026-05-12 — "
        "tracked as a v2-extraction-pipeline gap, not a Phase-1 encoder issue. "
        "See plan 'What could change' §1 and 2026-05-12 convo."
    ),
)
def test_all_47_opheim_states_present_in_all_four_csvs():
    with OPHEIM_SCORES_CSV.open() as f:
        states = [r["state"] for r in csv.DictReader(f)]
    assert len(states) == 47, f"Expected 47 Opheim states, got {len(states)}"

    missing: dict[str, list[int]] = {}
    for table in (28, 29, 30, 31):
        path = RESULTS / f"cogel_1990_table{table}.csv"
        with path.open() as f:
            present = {r["jurisdiction"] for r in csv.DictReader(f)}
        for s in states:
            if s not in present:
                missing.setdefault(s, []).append(table)

    assert not missing, f"States missing from CSVs (state → table list): {missing}"

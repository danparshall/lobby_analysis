"""Smoke tests for the v2 compendium loader.

The v2 compendium is the contract between the two parallel successor branches
(`extraction-harness-brainstorm` produces cells; `phase-c-projection-tdd`
consumes them). These tests verify the loader parses the TSV and exposes the
contract correctly. The loader returns raw ``list[dict[str, str]]`` rather
than typed models on purpose — typed models belong to the harness branch's
surgery.
"""

from __future__ import annotations

from lobby_analysis.compendium_loader import load_v2_compendium


# Expected v2 columns per `compendium/README.md` row-shape contract.
EXPECTED_V2_COLUMNS = {
    "compendium_row_id",
    "cell_type",
    "axis",
    "rubrics_reading",
    "n_rubrics",
    "first_introduced_by",
    "status",
    "notes",
}

# Per `compendium/_deprecated/v1/README.md` and the 2026-05-13 row-freeze decisions log,
# v2 has 181 rows (180 firm + 1 path-b unvalidated). This is the load-bearing contract
# the successor branches consume.
EXPECTED_V2_ROW_COUNT = 181

# The most-validated row in Compendium 2.0 — read by all 8 score-projection rubrics
# (CPI 2015, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991,
# HG 2007, FOCAL 2024). Canonicalized in Decision D1 of the freeze log.
CANONICAL_8_RUBRIC_ROW_ID = "lobbyist_spending_report_includes_total_compensation"


def test_load_v2_compendium_returns_181_rows():
    rows = load_v2_compendium()
    assert len(rows) == EXPECTED_V2_ROW_COUNT, (
        f"v2 compendium contract is 181 rows; loader returned {len(rows)}"
    )


def test_load_v2_compendium_rows_have_expected_columns():
    rows = load_v2_compendium()
    assert rows, "loader returned no rows — cannot check column shape"
    actual_columns = set(rows[0].keys())
    assert actual_columns == EXPECTED_V2_COLUMNS, (
        f"v2 row shape mismatch.\n"
        f"  expected: {sorted(EXPECTED_V2_COLUMNS)}\n"
        f"  actual:   {sorted(actual_columns)}"
    )


def test_load_v2_compendium_includes_canonical_8_rubric_row():
    rows = load_v2_compendium()
    row_ids = {row["compendium_row_id"] for row in rows}
    assert CANONICAL_8_RUBRIC_ROW_ID in row_ids, (
        f"canonical 8-rubric anchor row {CANONICAL_8_RUBRIC_ROW_ID!r} "
        f"missing from v2 compendium — this row should be present per "
        f"Decision D1 of the 2026-05-13 row-freeze log."
    )

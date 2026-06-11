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
# `prompt_text` was added 2026-06-03 per convo
# `20260603_statute_disagreement_prior_art_review` (v2.2 ledger Entry 3),
# then DROPPED 2026-06-04 per convo `20260604_wide_pass_yaml_sidecar_design`
# and plan `20260604_wide_prompt_text_pass.md`. Prompts now live in the
# sidecar YAML at `compendium/source_quotes.yaml`; the TSV reverts to the
# original 8-column row-shape contract.
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
# v2 had 181 rows; v2.1 (2026-06-05, Pattern C row split on wi-ralph-cpi-renewal-cadence)
# has 183 rows after un-combining `_imposed_in_practice` and `_audit_required_in_law`
# into single-axis pairs (each + 1 sibling row). Cell count unchanged at 186.
# The loader default now points at `disclosure_side_compendium_items_v2.1.tsv`.
EXPECTED_V2_ROW_COUNT = 183

# The most-validated row in Compendium 2.0 — read by all 8 score-projection rubrics
# (CPI 2015, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991,
# HG 2007, FOCAL 2024). Canonicalized in Decision D1 of the freeze log.
CANONICAL_8_RUBRIC_ROW_ID = "lobbyist_spending_report_includes_total_compensation"


def test_load_v2_compendium_returns_expected_row_count():
    rows = load_v2_compendium()
    assert len(rows) == EXPECTED_V2_ROW_COUNT, (
        f"v2.1 compendium contract is {EXPECTED_V2_ROW_COUNT} rows; loader returned {len(rows)}"
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

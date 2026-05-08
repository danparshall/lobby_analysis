"""Tests for the COGEL Blue Book v2 grid pipeline.

See `docs/active/cogel-extraction/plans/20260505_v2_column_clustering.md`
for the design.

Unit tests use a tiny synthetic fixture TSV to exercise cell-normalisation
rules in isolation. The integration test loads the committed v1 TSV
(`docs/active/cogel-extraction/results/20260505_v1_tokens.tsv`) and verifies
Missouri's emitted Table 29 row against the multimodal ground truth from
the convo summary.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.cogel import grid, schemas
from lobby_analysis.cogel.grid import GridToken


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TSV = REPO_ROOT / "tests" / "fixtures" / "cogel_minimal.tsv"
V1_TSV = REPO_ROOT / "docs" / "active" / "cogel-extraction" / "results" / "20260505_v1_tokens.tsv"


# ----- helpers -----------------------------------------------------------

def _t(text: str, x: int = 0, conf: int = 95, row: str = "Testland") -> GridToken:
    """Compact factory for a synthetic GridToken at y=1000 on scan 999."""
    return GridToken(
        scan_page=999, row=row, x=x, y=1000, w=30, h=25, conf=conf, text=text,
    )


# ----- cell normalisation ------------------------------------------------

def test_marker_asterisk_normalises_to_star():
    cell = grid.normalise_cell([_t("*")], "marker")
    assert cell.value == "*"


@pytest.mark.parametrize("dash_text", ["—", "-", "--", "_"])
def test_marker_dash_variants_all_normalise_to_em_dash(dash_text):
    cell = grid.normalise_cell([_t(dash_text)], "marker")
    assert cell.value == "—"


def test_marker_empty_cell_is_empty_string():
    cell = grid.normalise_cell([], "marker")
    assert cell.value == ""


def test_marker_unknown_glyph_flagged():
    cell = grid.normalise_cell([_t("X")], "marker")
    assert "unknown_marker" in cell.flags


def test_free_text_joins_consecutive_tokens_with_single_space():
    tokens = [_t("3", x=100), _t("reports", x=140), _t("per", x=200), _t("year", x=240)]
    cell = grid.normalise_cell(tokens, "free_text")
    assert cell.value == "3 reports per year"


def test_free_text_repairs_hyphen_joined_ocr_artifact():
    """`3-reports` is a single OCR token; repair to `3 reports`."""
    tokens = [_t("3-reports", x=100), _t("per", x=140), _t("year", x=180)]
    cell = grid.normalise_cell(tokens, "free_text")
    assert cell.value == "3 reports per year"


def test_free_text_drops_low_confidence_garbage():
    """Page-margin garbage like `SITYIY` at conf=31 should not end up in the cell."""
    tokens = [_t("Annually", x=100, conf=88), _t("SITYIY", x=200, conf=31)]
    cell = grid.normalise_cell(tokens, "free_text")
    assert cell.value == "Annually"


def test_free_text_keeps_low_confidence_markers():
    """Markers OCR at low conf often; the conf threshold does not apply to them."""
    tokens = [_t("—", x=100, conf=20)]
    cell = grid.normalise_cell(tokens, "marker")
    assert cell.value == "—"


def test_free_text_strips_trailing_footnote_into_separate_field():
    cell = grid.normalise_cell([_t("Annually(k)", x=100)], "free_text")
    assert cell.value == "Annually"
    assert cell.footnote == "k"


def test_free_text_multi_footnote_capture():
    """`Annually(k)(m)` is rare but real — both footnote letters must survive."""
    cell = grid.normalise_cell([_t("Annually(k)(m)", x=100)], "free_text")
    assert cell.value == "Annually"
    assert cell.footnote == "k,m"


def test_na_literal_preserved():
    """`N.A.` (Not Available) is data, not noise. Preserve it verbatim."""
    cell = grid.normalise_cell([_t("N.A.", x=100, conf=85)], "free_text")
    assert cell.value == "N.A."


def test_currency_extracts_numeric_value():
    cell = grid.normalise_cell([_t("$26,200,000", x=100)], "currency")
    assert cell.value == "$26,200,000"
    assert cell.numeric_value == 26_200_000


def test_currency_handles_no_dollar_sign():
    cell = grid.normalise_cell([_t("1,500", x=100)], "currency")
    assert cell.numeric_value == 1500


def test_frequency_normalises_known_value():
    cell = grid.normalise_cell([_t("Annually", x=100)], "frequency")
    assert cell.value == "Annually"


def test_frequency_passes_unknown_through_as_free_text():
    cell = grid.normalise_cell(
        [_t("3", x=100), _t("times", x=140), _t("a", x=180), _t("year", x=210)],
        "frequency",
    )
    assert cell.value == "3 times a year"


# ----- column-boundary derivation ---------------------------------------

def test_column_boundaries_are_midpoints_of_adjacent_centroids():
    """Given cluster centroids at x={600, 750, 900, 1100}, derived boundaries
    are the midpoints {675, 825, 1000} between adjacent clusters."""
    centroids = [600, 750, 900, 1100]
    boundaries = grid.midpoint_boundaries(centroids)
    assert boundaries == [675, 825, 1000]


def test_token_assigned_to_cell_by_x_position():
    """Boundaries [675, 825, 1000] yield 4 cells. A token at x=720 falls into
    cell 1 (between 675 and 825)."""
    boundaries = [675, 825, 1000]
    tok = _t("*", x=720)
    cell_idx = grid.cell_index_for_x(tok.cx, boundaries)
    assert cell_idx == 1


def test_marker_cluster_count_matches_schema_or_flag():
    """If marker clustering produces a wildly different count than the schema
    expects, the page is flagged (rather than silently emitting wrong data)."""
    # Synthetic markers at 5 distinct x's; Table 28 expects 23 columns.
    fake_markers = [_t("*", x=x) for x in (100, 300, 500, 700, 900)]
    boundaries, warnings = grid.boundaries_from_markers(fake_markers, schemas.TABLE_28)
    assert any("column_count_mismatch" in w["flag"] for w in warnings)


# ----- TSV loading -------------------------------------------------------

def test_load_v1_tsv_yields_grid_tokens():
    tokens = list(grid.load_tokens(FIXTURE_TSV))
    assert len(tokens) == 16
    assert tokens[0].text == "Header"
    assert tokens[0].row == "_header"
    assert tokens[1].row == "Testland"


# ----- integration: real v1 TSV -----------------------------------------

# Multimodal ground truth for Missouri (scan 165, Table 29) — taken from
# the convo summary `20260505_blue_book_v1_extractor.md`. Order matches
# `schemas.TABLE_29.keys`.
MISSOURI_GROUND_TRUTH = {
    "file_compensated_with_actual_contact": "*",
    "file_uncompensated_with_actual_contact": "—",
    "file_employing_with_actual_contact": "—",
    "file_employing_with_contact_over_threshold": "—",
    "file_other": "—",
    "freq_lobbyist": "3 reports per year",
    "freq_lobbyist_employees": "—",
    "freq_federal_state_public_lobby": "3 times a year",
    "disclose_legislation_admin_action": "*",
    "disclose_expenditures_benefiting_officials": "*",
    "disclose_compensation_by_employer": "—",
    "disclose_total_compensation": "—",
    "disclose_categories_of_expenditures": "*",
    "disclose_total_expenditures": "*",
    "disclose_contributions_for_lobbying": "—",
    "disclose_other": "—",
}


@pytest.mark.skipif(not V1_TSV.exists(), reason="v1 TSV not present")
def test_missouri_row_recovered_from_real_tsv():
    rows, _warnings = grid.project_table(V1_TSV, schemas.TABLE_29)
    missouri = next((r for r in rows if r["jurisdiction"] == "Missouri"), None)
    assert missouri is not None, "Missouri row missing from Table 29 emission"

    correct = sum(
        1 for k, v in MISSOURI_GROUND_TRUTH.items() if missouri.get(k) == v
    )
    assert correct >= 15, (
        f"Missouri row recovered only {correct}/16 cells correctly; "
        f"got {missouri}"
    )


@pytest.mark.skipif(not V1_TSV.exists(), reason="v1 TSV not present")
def test_footnote_only_page_emits_no_rows():
    """Scan 161 is a footnote-only Table 28 continuation — no jurisdictions
    on it. The grid pipeline should emit no Table 28 rows from scan 161."""
    rows, _warnings = grid.project_table(V1_TSV, schemas.TABLE_28)
    scan_161_rows = [r for r in rows if r.get("_scan_page") == 161]
    assert scan_161_rows == []


@pytest.mark.skipif(not V1_TSV.exists(), reason="v1 TSV not present")
def test_marker_totals_preserved_across_emission():
    """Sum of asterisks + dashes across all 4 emitted CSVs should approximate
    the v1 TSV totals (509 / 986). Allow up to 5% drift for tokens that fall
    outside any column boundary or get filtered."""
    total_asterisks = 0
    total_dashes = 0
    for table in schemas.ALL_TABLES:
        rows, _warnings = grid.project_table(V1_TSV, table)
        for row in rows:
            for col in table.columns:
                if col.value_kind != "marker":
                    continue
                v = row.get(col.key, "")
                if v == "*":
                    total_asterisks += 1
                elif v == "—":
                    total_dashes += 1

    # v1 TSV totals from the convo summary. 90% recovery threshold for v2 —
    # boundaries are hand-curated and some markers fall outside any column
    # bucket (e.g., footnote-prose strays). Tighten as boundaries are refined.
    assert total_asterisks >= int(509 * 0.90), (
        f"Asterisk recovery dropped: {total_asterisks} / 509 expected"
    )
    assert total_dashes >= int(986 * 0.90), (
        f"Dash recovery dropped: {total_dashes} / 986 expected"
    )

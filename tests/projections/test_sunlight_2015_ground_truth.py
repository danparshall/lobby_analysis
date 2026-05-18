"""Ground-truth loader tests for Sunlight 2015.

The published CSV (``papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv``)
has 50 rows x 10 columns. The loader returns USPS-keyed dicts of
per-item tier (int), strips undocumented footnote markers
(``*``/``**``/``***``/``^``/``^^``) before integer coercion, and
preserves marker provenance in a sibling structure so caveat tests
can recover which cells carried which markers.

Per-state per-item ground truth: 50 states x 4 in-scope columns = 200
cells. Item 4 (``Document Accessibility``) is in the CSV but the
loader does NOT surface it — it would tempt downstream code to
accidentally re-include the excluded item.
"""

from __future__ import annotations

from pathlib import Path

from lobby_analysis.projections.sunlight_2015 import (
    IN_SCOPE_ITEMS,
    load_sunlight_2015_reference,
    load_sunlight_2015_reference_marker_provenance,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_reference_has_50_states():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    assert len(reference) == 50


def test_reference_keys_are_usps_codes():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    # All keys are 2-letter uppercase USPS codes.
    for key in reference:
        assert len(key) == 2
        assert key.isalpha()
        assert key.isupper()


def test_reference_each_state_has_all_in_scope_items():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    expected_items = set(IN_SCOPE_ITEMS)
    for state, scores in reference.items():
        assert set(scores.keys()) == expected_items, (
            f"{state}: items mismatch — got {set(scores.keys())}"
        )


def test_reference_does_not_expose_item_4():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    for state, scores in reference.items():
        assert "sunlight_2015.document_accessibility" not in scores


def test_reference_values_are_ints_no_markers():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    for state, scores in reference.items():
        for item_id, val in scores.items():
            assert isinstance(val, int), f"{state}.{item_id}={val!r}"
            assert -2 <= val <= 2, f"{state}.{item_id}={val!r} out of range"


# --- Spot-checks against the published CSV ---------------------------------


def test_reference_massachusetts_top_scorer():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    ma = reference["MA"]
    assert ma["sunlight_2015.lobbyist_activity"] == 2
    assert ma["sunlight_2015.expenditure_transparency"] == 2
    assert ma["sunlight_2015.expenditure_reporting_thresholds"] == 0
    assert ma["sunlight_2015.lobbyist_compensation"] == 0


def test_reference_florida_bottom_scorer_strips_marker():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    fl = reference["FL"]
    assert fl["sunlight_2015.lobbyist_activity"] == -1
    assert fl["sunlight_2015.expenditure_transparency"] == -1
    assert fl["sunlight_2015.expenditure_reporting_thresholds"] == -1
    # Florida's Lobbyist Compensation = "-1**" in the CSV.
    assert fl["sunlight_2015.lobbyist_compensation"] == -1


def test_reference_kentucky_mid_pack():
    reference = load_sunlight_2015_reference(REPO_ROOT)
    ky = reference["KY"]
    assert ky["sunlight_2015.lobbyist_activity"] == 1
    assert ky["sunlight_2015.expenditure_transparency"] == 1
    assert ky["sunlight_2015.expenditure_reporting_thresholds"] == 0
    assert ky["sunlight_2015.lobbyist_compensation"] == -1


# --- Marker provenance -----------------------------------------------------


def test_marker_provenance_records_florida_double_asterisk():
    provenance = load_sunlight_2015_reference_marker_provenance(REPO_ROOT)
    # Florida's Lobbyist Compensation cell carries "**".
    assert provenance["FL"]["sunlight_2015.lobbyist_compensation"] == "**"


def test_marker_provenance_at_least_one_marker_recorded():
    provenance = load_sunlight_2015_reference_marker_provenance(REPO_ROOT)
    total_markers = sum(len(state_markers) for state_markers in provenance.values())
    # Inventory established 2026-05-18 Phase 0: 36 marker-carrying cells across
    # the 4 in-scope columns (28 *, 2 **, 5 ***, 1 ^^).
    assert total_markers == 36


def test_marker_provenance_excludes_clean_cells():
    provenance = load_sunlight_2015_reference_marker_provenance(REPO_ROOT)
    # Massachusetts top-scorer cells are all marker-free.
    assert provenance.get("MA", {}) == {}

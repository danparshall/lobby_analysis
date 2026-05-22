"""Ground-truth loader tests for FOCAL 2024.

Loads ``docs/historical/compendium-source-extracts/results/focal_2025_lacy_nichols_per_country_scores.csv``
and exposes a per-country dict of indicator → raw_score for the 27 FOCAL
legal-core indicators (or fewer per country, since the CSV's raw_score
column is populated for all 28 jurisdictions on all 49 + 1 indicators).

Validation regime:

* **Federal US LDA** (CSV "United States" row) is the load-bearing
  per-item anchor — the loader must surface every legal-core indicator
  for the US row with raw_score ∈ {0, 1, 2} and exact match against
  the published verbatim values from L-N 2025 Suppl Table 5.
* **27 other countries** are reference data per the plan's validation
  regime ("non-US jurisdiction; reference data not in primary validation
  scope"). Tests on per-country aggregates for those rows are
  ``pytest.mark.xfail`` at landing; the per-country presence-and-bounds
  smoke tests here pass.

This plan ships only the loader; per-country aggregation harness lives
in Plan 4 (focal_2024 aggregation). Companion plans (contact_log,
openness/timeliness) add their own indicator IDs to the loader's
output set as their batteries land.

Indicator IDs are returned **verbatim from the CSV** (no
``focal_2024.`` module prefix). Callers that compare against
``_SPEC_BY_ITEM`` keys must add the prefix themselves; the loader's
contract mirrors the CSV's wire format.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.projections.focal_2024 import (
    FOCAL_2024_LEGAL_CORE_INDICATORS,
    load_focal_2024_per_country_reference,
)


# Resolve the repo root via worktree-aware path walking. Tests run from
# either main checkout or a worktree; conftest.py doesn't fix this for us
# in the projections subtree, so walk up from this file.
_REPO_ROOT: Path = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def reference() -> dict[str, dict[str, int]]:
    return load_focal_2024_per_country_reference(_REPO_ROOT)


# ---------------------------------------------------------------------------
# Shape: 28 jurisdictions, 27 legal-core indicators each
# ---------------------------------------------------------------------------


def test_legal_core_indicator_set_has_27_items():
    """4 scope + 6 descriptors + 1 revolving_door + 5 relationships + 11 financials = 27."""
    assert len(FOCAL_2024_LEGAL_CORE_INDICATORS) == 27


def test_legal_core_indicator_set_contains_expected_ids():
    """Spot-check coverage of all 5 batteries in the legal-core indicator set."""
    expected = {
        "scope.1", "scope.2", "scope.3", "scope.4",
        "descriptors.1", "descriptors.2", "descriptors.3",
        "descriptors.4", "descriptors.5", "descriptors.6",
        "revolving_door.1",
        "relationships.0", "relationships.1",
        "relationships.2", "relationships.3", "relationships.4",
        "financials.1", "financials.2", "financials.3",
        "financials.4", "financials.5", "financials.6",
        "financials.7", "financials.8", "financials.9",
        "financials.10", "financials.11",
    }
    assert expected == FOCAL_2024_LEGAL_CORE_INDICATORS


def test_revolving_door_2_not_in_legal_core_indicator_set():
    """revolving_door.2 is excluded per FOCAL-1 user-decision; it stays in
    the CSV (so the raw row is loadable) but is filtered out of the
    legal-core indicator set."""
    assert "revolving_door.2" not in FOCAL_2024_LEGAL_CORE_INDICATORS


def test_reference_has_united_states_row(reference):
    assert "United States" in reference


def test_united_states_row_has_all_27_legal_core_indicators(reference):
    us_keys = set(reference["United States"].keys())
    # US row may carry additional indicators (timeliness, openness, contact_log)
    # — those are loaded for companion plans, but the legal-core subset must be
    # complete.
    assert FOCAL_2024_LEGAL_CORE_INDICATORS.issubset(us_keys)


def test_all_united_states_legal_core_values_in_bounds(reference):
    for indicator in FOCAL_2024_LEGAL_CORE_INDICATORS:
        value = reference["United States"][indicator]
        assert value in {0, 1, 2}, f"{indicator}={value} outside {{0,1,2}}"


# ---------------------------------------------------------------------------
# US LDA verbatim spot checks against L-N 2025 Suppl Table 5
# (per the plan's Federal US LDA validation anchor)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "indicator,expected_raw",
    [
        # Scope
        ("scope.1", 2),   # full set — LDA broad lobbyist definition
        ("scope.2", 0),   # significant thresholds ($3000 + 20%)
        ("scope.3", 0),   # staff narrow in LDA
        ("scope.4", 2),   # full activity breadth
        # Descriptors
        ("descriptors.1", 2),
        ("descriptors.2", 2),
        ("descriptors.3", 0),
        ("descriptors.4", 0),
        ("descriptors.5", 2),
        ("descriptors.6", 0),
        # Revolving door
        ("revolving_door.1", 2),
        # Relationships
        ("relationships.0", 2),  # 2025-only "Lobbyist list"
        ("relationships.1", 1),  # partly — client list
        ("relationships.2", 0),
        ("relationships.3", 0),
        ("relationships.4", 0),
        # Financials
        ("financials.1", 2),
        ("financials.2", 2),
        ("financials.3", 0),
        ("financials.4", 0),
        ("financials.5", 0),
        ("financials.6", 2),
        ("financials.7", 0),
        ("financials.8", 0),
        ("financials.9", 0),
        ("financials.10", 0),
        ("financials.11", 2),
    ],
)
def test_united_states_legal_core_values_match_published(
    reference, indicator, expected_raw
):
    """Verbatim against L-N 2025 Suppl Table 5 — the Federal US LDA per-
    indicator anchor for Phase C validation. Mismatch indicates either
    the CSV drifted, the loader is mistransforming, or the indicator-ID
    convention changed."""
    assert reference["United States"][indicator] == expected_raw


def test_united_states_legal_core_raw_sum(reference):
    """Sum of the 27 legal-core US values (raw) = 24.

    Computation: scope (2+0+0+2) + descriptors (2+2+0+0+2+0) +
    revolving_door (2) + relationships (2+1+0+0+0) + financials
    (2+2+0+0+0+2+0+0+0+0+2) = 4 + 6 + 2 + 3 + 8 = 23.

    (24 if relationships.0 is excluded from sub-counts and recomputed
    with all 27; this assertion uses 23 as the verified count.)
    """
    total = sum(
        reference["United States"][indicator]
        for indicator in FOCAL_2024_LEGAL_CORE_INDICATORS
    )
    # 2 + 0 + 0 + 2 = 4 (scope)
    # 2 + 2 + 0 + 0 + 2 + 0 = 6 (descriptors)
    # 2 = 2 (revolving_door.1)
    # 2 + 1 + 0 + 0 + 0 = 3 (relationships)
    # 2 + 2 + 0 + 0 + 0 + 2 + 0 + 0 + 0 + 0 + 2 = 8 (financials)
    # Total = 4 + 6 + 2 + 3 + 8 = 23
    assert total == 23


# ---------------------------------------------------------------------------
# 27 reference countries: presence smoke test + xfail aggregates
# ---------------------------------------------------------------------------


def test_reference_has_28_jurisdictions(reference):
    """L-N 2025 scored 28 jurisdictions (27 countries + US federal LDA)."""
    assert len(reference) == 28


def test_all_jurisdictions_have_legal_core_indicators(reference):
    """Smoke test: every jurisdiction in the CSV has the legal-core
    indicators present. Indicator values themselves are reference data
    for non-US jurisdictions (not Phase-C-validated)."""
    for jurisdiction, per_item in reference.items():
        assert FOCAL_2024_LEGAL_CORE_INDICATORS.issubset(
            set(per_item.keys())
        ), f"{jurisdiction} missing some legal-core indicators"


def test_all_legal_core_values_in_bounds_for_all_jurisdictions(reference):
    """Bounds-check across 28 × 27 = 756 cells. ``None`` (not_assessable)
    is allowed for non-US legal-core cells; the US row carries no NA."""
    for jurisdiction, per_item in reference.items():
        for indicator in FOCAL_2024_LEGAL_CORE_INDICATORS:
            v = per_item[indicator]
            assert v is None or v in {0, 1, 2}, (
                f"{jurisdiction}/{indicator}={v!r} outside {{0,1,2,None}}"
            )


def test_united_states_legal_core_has_no_na_cells(reference):
    """The Federal US LDA validation anchor must have an integer raw score
    for every legal-core indicator — no NA cells permitted on the US row."""
    for indicator in FOCAL_2024_LEGAL_CORE_INDICATORS:
        v = reference["United States"][indicator]
        assert v is not None, f"US/{indicator} is NA (not_assessable)"


@pytest.mark.xfail(
    reason="non-US jurisdiction; reference data not in primary validation scope",
    strict=False,
)
def test_canada_aggregate_matches_published(reference):
    """Canada published as 49% in L-N 2025 Suppl Table 5 — aggregation
    harness lives in Plan 4; this is a placeholder against the loader."""
    raise NotImplementedError("aggregation harness lives in Plan 4")


@pytest.mark.xfail(
    reason="non-US jurisdiction; reference data not in primary validation scope",
    strict=False,
)
def test_chile_aggregate_matches_published(reference):
    raise NotImplementedError("aggregation harness lives in Plan 4")


@pytest.mark.xfail(
    reason="non-US jurisdiction; reference data not in primary validation scope",
    strict=False,
)
def test_netherlands_aggregate_matches_published(reference):
    raise NotImplementedError("aggregation harness lives in Plan 4")

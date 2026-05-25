"""Ground-truth loader tests for CPI 2015 C11.

The 700-cell per-state CSV at
docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv
has six known glitches per the spec doc + an extra round of fact-checking:

* Colorado was typed in title case ("Yes"/"No") on all six of its de jure
  rows (IND_196, IND_197, IND_199, IND_201, IND_203, IND_207). Case-insensitive
  YES/MODERATE/NO matching normalizes this.
* IND_199 Texas and IND_203 Massachusetts both carry the literal string
  "100" where YES/MODERATE/NO is expected. CPI's 3-tier de jure rubric maps
  100 -> YES, so they should be normalized to YES.

The loader returns scores as plain ints in {0, 25, 50, 75, 100} (after
mapping the de jure tiers YES/MODERATE/NO -> 100/50/0). That makes the
ground truth directly comparable to per-item projection output and
directly usable as input to the aggregation rule fit.
"""

from __future__ import annotations

from lobby_analysis.projections.cpi_2015_c11 import load_per_state_ground_truth


def test_load_per_state_ground_truth_returns_700_cells():
    truth = load_per_state_ground_truth()
    assert len(truth) == 50 * 14  # 50 states x 14 items


def test_load_per_state_ground_truth_keys_are_state_indicator_pairs():
    truth = load_per_state_ground_truth()
    assert ("Alabama", "IND_196") in truth
    assert ("Wyoming", "IND_209") in truth


def test_load_per_state_ground_truth_values_are_ints_in_5_tier_range():
    truth = load_per_state_ground_truth()
    for value in truth.values():
        assert isinstance(value, int)
        assert value in {0, 25, 50, 75, 100}


def test_load_normalizes_case_insensitive_yes_no_for_colorado():
    # Colorado's hand-typed "Yes" cells should round-trip to 100;
    # "No" should round-trip to 0. All 6 of Colorado's de jure cells
    # were typed in title case.
    truth = load_per_state_ground_truth()
    assert truth[("Colorado", "IND_196")] == 100  # "Yes" -> YES -> 100
    assert truth[("Colorado", "IND_197")] == 100
    assert truth[("Colorado", "IND_199")] == 100
    assert truth[("Colorado", "IND_201")] == 100
    assert truth[("Colorado", "IND_203")] == 0  # "No" -> NO -> 0
    assert truth[("Colorado", "IND_207")] == 0


def test_load_normalizes_invalid_de_jure_cell_to_zero():
    # IND_199 Texas + IND_203 Massachusetts carry the literal string
    # "100" in a YES/MODERATE/NO column -- an Excel transcription
    # artifact. CPI's published per-state aggregate is consistent with
    # treating these invalid cells as NO (0), not YES (100). See
    # docstring on `_DE_JURE_TIER_TO_SCORE` for the empirical-fit
    # derivation.
    truth = load_per_state_ground_truth()
    assert truth[("Texas", "IND_199")] == 0
    assert truth[("Massachusetts", "IND_203")] == 0

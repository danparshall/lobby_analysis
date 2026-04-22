"""Tests for scoring.calibration — PRI rollup + reference-score loader + agreement.

Spec: docs/historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scoring.calibration import (
    AgreementReport,
    DisclosureSubAggregates,
    compute_agreement,
    load_pri_reference_scores,
    rollup_accessibility,
    rollup_disclosure_law,
)
from scoring.statute_retrieval import PRI_RESPONDER_STATES

REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Disclosure-law rollup: sub-component rules
# ---------------------------------------------------------------------------


def _disclosure_all_zero() -> dict[str, float | None]:
    """Return a complete atomic-score dict for pri_disclosure_law, all zeros.

    Rubric has 61 items per tests/test_pipeline.py expectation.
    """
    ids = [
        # A1..A11
        *[f"A{i}" for i in range(1, 12)],
        # B1..B4
        *[f"B{i}" for i in range(1, 5)],
        # C0..C3
        *[f"C{i}" for i in range(0, 4)],
        # D0, D1_present, D1_value, D2_present, D2_value
        "D0", "D1_present", "D1_value", "D2_present", "D2_value",
        # E1 side
        "E1a", "E1b", "E1c", "E1d", "E1e",
        "E1f_i", "E1f_ii", "E1f_iii", "E1f_iv",
        "E1g_i", "E1g_ii",
        "E1h_i", "E1h_ii", "E1h_iii", "E1h_iv", "E1h_v", "E1h_vi",
        "E1i", "E1j",
        # E2 side
        "E2a", "E2b", "E2c", "E2d", "E2e",
        "E2f_i", "E2f_ii", "E2f_iii", "E2f_iv",
        "E2g_i", "E2g_ii",
        "E2h_i", "E2h_ii", "E2h_iii", "E2h_iv", "E2h_v", "E2h_vi",
        "E2i",
    ]
    assert len(ids) == 61, f"disclosure-law rubric should have 61 items, got {len(ids)}"
    return {i: 0 for i in ids}


def test_disclosure_A_is_simple_sum_of_A1_through_A11() -> None:
    scores = _disclosure_all_zero()
    for i in range(1, 12):
        scores[f"A{i}"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.A_registration == 11


def test_disclosure_A_partial() -> None:
    scores = _disclosure_all_zero()
    scores["A1"] = 1
    scores["A5"] = 1
    scores["A11"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.A_registration == 3


def test_disclosure_B_reverse_scores_B1_and_B2() -> None:
    """B1/B2 answered 'No' (=0) contribute 1 each; B3/B4 answered 'Yes' (=1) contribute 1."""
    scores = _disclosure_all_zero()
    # B1 = 0 (no exemption) → contributes 1
    # B2 = 0 (not relieved) → contributes 1
    # B3 = 1 (same disclosure) → contributes 1
    # B4 = 1 (same disclosure as principals) → contributes 1
    scores["B1"] = 0
    scores["B2"] = 0
    scores["B3"] = 1
    scores["B4"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.B_gov_exemptions == 4  # paper cap; no state actually scores 4 but the rule allows it


def test_disclosure_B_all_worst_case_is_zero() -> None:
    """B1/B2='Yes' (exemption exists = bad), B3/B4='No' (not subject = bad) → all zero."""
    scores = _disclosure_all_zero()
    scores["B1"] = 1
    scores["B2"] = 1
    scores["B3"] = 0
    scores["B4"] = 0
    agg = rollup_disclosure_law(scores)
    assert agg.B_gov_exemptions == 0


def test_disclosure_C_ignores_C1_C2_C3_subcriteria() -> None:
    """Per Table 5 (0-1 cap) and paper line 1434, only C0 contributes."""
    scores = _disclosure_all_zero()
    scores["C0"] = 1
    scores["C1"] = 1
    scores["C2"] = 1
    scores["C3"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.C_public_entity_def == 1


def test_disclosure_C0_zero_yields_C_zero() -> None:
    scores = _disclosure_all_zero()
    scores["C0"] = 0
    scores["C1"] = 1  # descriptive info ignored
    agg = rollup_disclosure_law(scores)
    assert agg.C_public_entity_def == 0


def test_disclosure_D_ignores_D1_and_D2_subcriteria() -> None:
    scores = _disclosure_all_zero()
    scores["D0"] = 1
    scores["D1_present"] = 1
    scores["D1_value"] = 500  # descriptive USD value
    scores["D2_present"] = 1
    scores["D2_value"] = 5  # descriptive percent value
    agg = rollup_disclosure_law(scores)
    assert agg.D_materiality == 1


def test_disclosure_E_higher_of_principal_or_lobbyist_for_base_items() -> None:
    """Base items (a, b, c, d, e, h_collapsed, i) follow 'higher of' per paper line 1224."""
    scores = _disclosure_all_zero()
    # E1 side: answer Yes to a,b,c → base = 3
    scores["E1a"] = 1
    scores["E1b"] = 1
    scores["E1c"] = 1
    # E2 side: answer Yes to a,b,c,d,e → base = 5
    scores["E2a"] = 1
    scores["E2b"] = 1
    scores["E2c"] = 1
    scores["E2d"] = 1
    scores["E2e"] = 1
    agg = rollup_disclosure_law(scores)
    # F (f-items), G (g-items), J all zero here.
    # max(3, 5) = 5.
    assert agg.E_info_disclosed == 5


def test_disclosure_E_F_exception_sums_across_both_sides() -> None:
    """f-items double across E1 and E2 per paper line 1230-1238."""
    scores = _disclosure_all_zero()
    # Set all f-items to 1 both sides — 4 + 4 = 8.
    for side in ("E1", "E2"):
        for suffix in ("f_i", "f_ii", "f_iii", "f_iv"):
            scores[f"{side}{suffix}"] = 1
    agg = rollup_disclosure_law(scores)
    # base for each side = 0; max(0, 0) = 0. f total = 8.
    assert agg.E_info_disclosed == 8


def test_disclosure_E_G_exception_sums_across_both_sides() -> None:
    scores = _disclosure_all_zero()
    for side in ("E1", "E2"):
        for suffix in ("g_i", "g_ii"):
            scores[f"{side}{suffix}"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.E_info_disclosed == 4


def test_disclosure_E_J_is_independent() -> None:
    """E1j is added on top of the higher-of, not max'd."""
    scores = _disclosure_all_zero()
    scores["E1j"] = 1
    # No other E items set; base = 0 on both sides; f/g = 0.
    agg = rollup_disclosure_law(scores)
    assert agg.E_info_disclosed == 1


def test_disclosure_E_h_collapses_for_frequent_intervals() -> None:
    """Any of monthly/quarterly/tri-annually → h_collapsed = 1 (paper line 1250)."""
    scores = _disclosure_all_zero()
    # E1a=1 so base > 0 and h_collapsed contributes
    scores["E1a"] = 1
    scores["E1h_ii"] = 1  # quarterly
    agg = rollup_disclosure_law(scores)
    # base_E1 = a + 0 + 0 + 0 + 0 + h_collapsed(=1) + 0 = 2
    # base_E2 = 0
    # max = 2.
    assert agg.E_info_disclosed == 2


def test_disclosure_E_h_does_not_collapse_for_only_semi_or_annual() -> None:
    """Only semi-annual or annual → h_collapsed = 0 (they are less frequent than needed)."""
    scores = _disclosure_all_zero()
    scores["E1a"] = 1
    scores["E1h_iv"] = 1  # semi-annually
    scores["E1h_v"] = 1  # annually
    agg = rollup_disclosure_law(scores)
    # h_collapsed = 0 because none of i/ii/iii are 1.
    # base_E1 = 1 (a only).
    assert agg.E_info_disclosed == 1


def test_disclosure_E_maximum_is_20() -> None:
    """All atomic items at their best value → E = 20, matching Table 5 column cap."""
    scores = _disclosure_all_zero()
    # Base side: a,b,c,d,e,h_collapsed(via h_i),i = 7 each side.
    for side in ("E1", "E2"):
        for suffix in ("a", "b", "c", "d", "e", "i", "h_i"):
            scores[f"{side}{suffix}"] = 1
        for suffix in ("f_i", "f_ii", "f_iii", "f_iv"):
            scores[f"{side}{suffix}"] = 1
        for suffix in ("g_i", "g_ii"):
            scores[f"{side}{suffix}"] = 1
    scores["E1j"] = 1
    agg = rollup_disclosure_law(scores)
    # max(7, 7) + (4+4) + (2+2) + 1 = 7 + 8 + 4 + 1 = 20
    assert agg.E_info_disclosed == 20


def test_disclosure_total_maximum_is_37() -> None:
    scores = _disclosure_all_zero()
    for i in range(1, 12):
        scores[f"A{i}"] = 1
    scores["B1"] = 0  # reverse: 1
    scores["B2"] = 0
    scores["B3"] = 1
    scores["B4"] = 1
    scores["C0"] = 1
    scores["D0"] = 1
    for side in ("E1", "E2"):
        for suffix in ("a", "b", "c", "d", "e", "i", "h_i"):
            scores[f"{side}{suffix}"] = 1
        for suffix in ("f_i", "f_ii", "f_iii", "f_iv"):
            scores[f"{side}{suffix}"] = 1
        for suffix in ("g_i", "g_ii"):
            scores[f"{side}{suffix}"] = 1
    scores["E1j"] = 1
    agg = rollup_disclosure_law(scores)
    assert agg.A_registration == 11
    assert agg.B_gov_exemptions == 4
    assert agg.C_public_entity_def == 1
    assert agg.D_materiality == 1
    assert agg.E_info_disclosed == 20
    assert agg.total == 37


def test_disclosure_null_A_item_makes_A_null() -> None:
    """Any None in the sub-aggregate's inputs → sub-aggregate is None, total is None."""
    scores = _disclosure_all_zero()
    scores["A3"] = None
    agg = rollup_disclosure_law(scores)
    assert agg.A_registration is None
    assert agg.total is None
    # Other sub-aggregates still computable
    assert agg.C_public_entity_def == 0


def test_disclosure_null_in_E_unreached_branch_still_propagates() -> None:
    """A null in one of the f-items propagates because F is always summed both sides."""
    scores = _disclosure_all_zero()
    scores["E1f_i"] = None
    agg = rollup_disclosure_law(scores)
    assert agg.E_info_disclosed is None


# ---------------------------------------------------------------------------
# Accessibility rollup
# ---------------------------------------------------------------------------


def _accessibility_all_zero() -> dict[str, float | None]:
    """Return atomic scores for the 22 items PRI 2010 scored; Q9-Q16 excluded (2026-only)."""
    ids = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
    ids += [f"Q7{ch}" for ch in "abcdefghijklmno"]
    ids.append("Q8")
    assert len(ids) == 22
    return {i: 0 for i in ids}


def test_accessibility_Q1_through_Q6_contribute_one_each() -> None:
    scores = _accessibility_all_zero()
    scores["Q1"] = 1
    scores["Q3"] = 1
    scores["Q5"] = 1
    agg = rollup_accessibility(scores)
    assert agg.Q1 == 1
    assert agg.Q2 == 0
    assert agg.Q3 == 1
    assert agg.Q4 == 0
    assert agg.Q5 == 1
    assert agg.Q6 == 0


def test_accessibility_Q7_raw_is_sum_of_Q7a_through_Q7o() -> None:
    scores = _accessibility_all_zero()
    for ch in "abc":
        scores[f"Q7{ch}"] = 1
    agg = rollup_accessibility(scores)
    assert agg.Q7_raw == 3


def test_accessibility_Q7_raw_max_is_15() -> None:
    scores = _accessibility_all_zero()
    for ch in "abcdefghijklmno":
        scores[f"Q7{ch}"] = 1
    agg = rollup_accessibility(scores)
    assert agg.Q7_raw == 15


def test_accessibility_Q8_normalized_divides_by_15() -> None:
    scores = _accessibility_all_zero()
    scores["Q8"] = 3  # raw 0-15
    agg = rollup_accessibility(scores)
    assert agg.Q8_normalized == pytest.approx(3 / 15)


def test_accessibility_Q8_max_normalized_is_one() -> None:
    scores = _accessibility_all_zero()
    scores["Q8"] = 15
    agg = rollup_accessibility(scores)
    assert agg.Q8_normalized == pytest.approx(1.0)


def test_accessibility_total_maximum_is_22() -> None:
    scores = _accessibility_all_zero()
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
        scores[q] = 1
    for ch in "abcdefghijklmno":
        scores[f"Q7{ch}"] = 1
    scores["Q8"] = 15
    agg = rollup_accessibility(scores)
    assert agg.total == pytest.approx(22.0)


def test_accessibility_null_Q8_propagates_to_total() -> None:
    scores = _accessibility_all_zero()
    scores["Q8"] = None
    agg = rollup_accessibility(scores)
    assert agg.Q8_normalized is None
    assert agg.total is None


# ---------------------------------------------------------------------------
# PRI reference-score loader + 50-state structural reconciliation
# ---------------------------------------------------------------------------


def test_load_pri_reference_disclosure_law_returns_50_states() -> None:
    ref = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    assert len(ref) == 50
    # USPS keys (two-letter), not full names.
    assert set(ref.keys()) == {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    }


def test_load_pri_reference_disclosure_law_matches_published_totals() -> None:
    """Structural reconciliation: A + B + C + D + E must equal published total_2010."""
    ref = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    for usps, agg in ref.items():
        assert isinstance(agg, DisclosureSubAggregates), f"{usps}: wrong shape"
        recomputed = (
            agg.A_registration + agg.B_gov_exemptions + agg.C_public_entity_def
            + agg.D_materiality + agg.E_info_disclosed
        )
        assert recomputed == agg.total, (
            f"{usps}: A+B+C+D+E={recomputed} != total={agg.total}"
        )


def test_load_pri_reference_disclosure_law_montana_spot_check() -> None:
    """Montana is PRI 2010 rank 1 (31 total). Verify columns match paper Table 5."""
    ref = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    mt = ref["MT"]
    assert mt.A_registration == 9
    assert mt.B_gov_exemptions == 3
    assert mt.C_public_entity_def == 0
    assert mt.D_materiality == 1
    assert mt.E_info_disclosed == 18
    assert mt.total == 31


def test_load_pri_reference_accessibility_returns_50_states() -> None:
    ref = load_pri_reference_scores("pri_accessibility", REPO_ROOT)
    assert len(ref) == 50


def test_load_pri_reference_accessibility_connecticut_spot_check() -> None:
    """Connecticut is PRI 2010 rank 1 accessibility (17.3 total)."""
    ref = load_pri_reference_scores("pri_accessibility", REPO_ROOT)
    ct = ref["CT"]
    assert ct.Q1 == 1
    assert ct.Q2 == 1
    assert ct.Q3 == 1
    assert ct.Q4 == 1
    assert ct.Q5 == 1
    assert ct.Q6 == 1
    assert ct.Q7_raw == 11
    assert ct.Q8_normalized == pytest.approx(0.3)
    assert ct.total == pytest.approx(17.3)


def test_load_pri_reference_accessibility_structural_reconciliation() -> None:
    """Q1+Q2+Q3+Q4+Q5+Q6+Q7_raw+Q8_normalized must equal published total_2010 (rounded to 1dp)."""
    ref = load_pri_reference_scores("pri_accessibility", REPO_ROOT)
    for usps, agg in ref.items():
        recomputed = (
            agg.Q1 + agg.Q2 + agg.Q3 + agg.Q4 + agg.Q5 + agg.Q6
            + agg.Q7_raw + agg.Q8_normalized
        )
        # PRI rounded to 1dp; allow 0.05 slack because Q8_normalized in the CSV is
        # 1dp-rounded relative to the implied raw value.
        assert abs(recomputed - agg.total) < 0.06, (
            f"{usps}: Q1..Q7_raw+Q8_normalized={recomputed} vs total={agg.total}"
        )


def test_load_pri_reference_rejects_unknown_rubric() -> None:
    with pytest.raises(ValueError):
        load_pri_reference_scores("focal_indicators", REPO_ROOT)  # not a PRI rubric


# ---------------------------------------------------------------------------
# Agreement metrics
# ---------------------------------------------------------------------------


def _ours_atomic_for_mt_matching_pri() -> dict[str, int | None]:
    """Construct atomic scores that roll up to Montana's PRI 2010 disclosure values."""
    scores = _disclosure_all_zero()
    # A_registration = 9: set A1..A9 = 1; A10, A11 = 0.
    for i in range(1, 10):
        scores[f"A{i}"] = 1
    # B_gov_exemptions = 3: B1=0 (reverse→1), B2=0 (reverse→1), B3=1, B4=0 → 1+1+1+0 = 3.
    scores["B1"] = 0
    scores["B2"] = 0
    scores["B3"] = 1
    scores["B4"] = 0
    # C_public_entity_def = 0: C0=0
    # D_materiality = 1: D0=1
    scores["D0"] = 1
    # E_info_disclosed = 18: pick atomic values that yield 18.
    # Use max(base_E1, base_E2) + fg_E1 + fg_E2 + E1j = 18.
    # Simplest: base_E1 = 7, base_E2 = 0, fg_E1 = 6, fg_E2 = 4, E1j = 1 → 7+6+4+1 = 18.
    for suffix in ("a", "b", "c", "d", "e", "i", "h_i"):
        scores[f"E1{suffix}"] = 1
    for suffix in ("f_i", "f_ii", "f_iii", "f_iv", "g_i", "g_ii"):
        scores[f"E1{suffix}"] = 1
    for suffix in ("f_i", "f_ii", "f_iii", "f_iv"):
        scores[f"E2{suffix}"] = 1
    scores["E1j"] = 1
    return scores


def test_agreement_identical_scores_yields_perfect_match() -> None:
    pri = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    ours = {"MT": _ours_atomic_for_mt_matching_pri()}
    report = compute_agreement(
        ours_atomic_by_state=ours,
        pri_by_state={"MT": pri["MT"]},
        rubric="pri_disclosure_law",
    )
    assert isinstance(report, AgreementReport)
    assert report.per_state["MT"].total_match is True
    # All 5 sub-components match.
    assert all(report.per_state["MT"].per_sub_component.values())


def test_agreement_single_disagreement_recorded() -> None:
    pri = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    # Flip one A item so A_registration becomes 8 instead of 9.
    ours_scores = _ours_atomic_for_mt_matching_pri()
    ours_scores["A1"] = 0
    report = compute_agreement(
        ours_atomic_by_state={"MT": ours_scores},
        pri_by_state={"MT": pri["MT"]},
        rubric="pri_disclosure_law",
    )
    assert report.per_state["MT"].per_sub_component["A_registration"] is False
    assert report.per_state["MT"].per_sub_component["B_gov_exemptions"] is True
    assert report.per_state["MT"].total_match is False


def test_agreement_null_sub_aggregate_counts_as_disagreement() -> None:
    pri = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    ours_scores = _ours_atomic_for_mt_matching_pri()
    ours_scores["A5"] = None  # unable_to_evaluate → A_registration becomes None
    report = compute_agreement(
        ours_atomic_by_state={"MT": ours_scores},
        pri_by_state={"MT": pri["MT"]},
        rubric="pri_disclosure_law",
    )
    assert report.per_state["MT"].per_sub_component["A_registration"] is False


def test_agreement_trust_partition_splits_overall() -> None:
    """With trust_partition=PRI_RESPONDER_STATES, overall exposes responder + non-responder rates."""
    pri = load_pri_reference_scores("pri_disclosure_law", REPO_ROOT)
    # MT is a responder; FL is not (check PRI_RESPONDER_STATES).
    assert "MT" in PRI_RESPONDER_STATES
    assert "FL" not in PRI_RESPONDER_STATES
    ours = {
        "MT": _ours_atomic_for_mt_matching_pri(),  # perfect match
        "FL": _disclosure_all_zero(),  # zero across the board (guaranteed disagreement)
    }
    report = compute_agreement(
        ours_atomic_by_state=ours,
        pri_by_state={"MT": pri["MT"], "FL": pri["FL"]},
        rubric="pri_disclosure_law",
        trust_partition=PRI_RESPONDER_STATES,
    )
    # Responder side: MT is in; its 5 sub-components all match → rate = 1.0
    assert report.overall.in_partition.per_sub_component_agreement_rate["A_registration"] == 1.0
    # Non-responder side: FL has all zeros, PRI FL is {10, 3, 0, 0, 9}; A/B/E don't match, C/D match.
    # So A_registration rate for non-responders = 0.0.
    assert report.overall.out_of_partition.per_sub_component_agreement_rate["A_registration"] == 0.0


def test_agreement_accessibility_rubric_supported() -> None:
    """Agreement must also work for accessibility rubric (Q1..Q8)."""
    pri = load_pri_reference_scores("pri_accessibility", REPO_ROOT)
    # Construct atomic scores that match Connecticut: Q1..Q6=1, Q7_raw=11 (sum of 11 sub-items), Q8 raw such that Q8/15 ≈ 0.3.
    scores = _accessibility_all_zero()
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
        scores[q] = 1
    for ch in "abcdefghijk":  # 11 of 15
        scores[f"Q7{ch}"] = 1
    scores["Q8"] = 5  # 5/15 ≈ 0.333 → rounds to 0.3 (PRI Table 6 is 1-dp)
    report = compute_agreement(
        ours_atomic_by_state={"CT": scores},
        pri_by_state={"CT": pri["CT"]},
        rubric="pri_accessibility",
    )
    # Exact-match check should treat Q8_normalized with 1-dp tolerance (PRI rounded).
    assert report.per_state["CT"].per_sub_component["Q7_raw"] is True
    assert report.per_state["CT"].per_sub_component["Q8_normalized"] is True

"""Ground-truth loader tests for PRI 2010.

The CPI 2015 C11 module owned a per-state per-indicator ground-truth loader
(700 cells). PRI 2010 publishes coarser data — 50 states x 5 disclosure-law
sub-aggregates + 50 states x 8 accessibility sub-components — and the existing
``scoring.calibration.load_pri_reference_scores`` already loads it (was built
for the archived pri-calibration branch's agreement metrics).

This module re-exports the existing loader under the projections namespace so
callers writing PRI 2010 projection code don't have to reach into the scoring
package. The tests verify the re-export carries the same data.
"""

from __future__ import annotations

from pathlib import Path

from lobby_analysis.projections.pri_2010 import (
    load_pri_2010_accessibility_reference,
    load_pri_2010_disclosure_law_reference,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_disclosure_law_returns_50_states():
    scores = load_pri_2010_disclosure_law_reference(REPO_ROOT)
    assert len(scores) == 50
    # All keys are USPS codes
    assert all(len(state) == 2 and state.isupper() for state in scores)


def test_load_disclosure_law_alabama_matches_published():
    """Published row from pri_2010_disclosure_law_scores.csv:
    Alabama,7,3,0,1,8,19,51.4,36
    Spec quote (rollup spec line 53): A+B+C+D+E = 7+3+0+1+8 = 19, percent 19/37*100 = 51.35%."""
    scores = load_pri_2010_disclosure_law_reference(REPO_ROOT)
    al = scores["AL"]
    assert al.A_registration == 7
    assert al.B_gov_exemptions == 3
    assert al.C_public_entity_def == 0
    assert al.D_materiality == 1
    assert al.E_info_disclosed == 8
    assert al.total == 19


def test_load_disclosure_law_arizona_max_state():
    """Arizona had the highest disclosure-law score in 2010 (rank 2; total 30):
    Arizona,11,3,1,0,15,30,81.1,2"""
    scores = load_pri_2010_disclosure_law_reference(REPO_ROOT)
    az = scores["AZ"]
    assert az.A_registration == 11  # all 11 actor-types required to register
    assert az.B_gov_exemptions == 3
    assert az.C_public_entity_def == 1  # AZ is one of 6 states with public-entity def
    assert az.D_materiality == 0
    assert az.E_info_disclosed == 15
    assert az.total == 30


def test_load_accessibility_returns_50_states():
    scores = load_pri_2010_accessibility_reference(REPO_ROOT)
    assert len(scores) == 50


def test_load_accessibility_alabama_matches_published():
    """Published row from pri_2010_accessibility_scores.csv:
    Alabama,1,1,1,1,0,0,3.0,0.1,7.1,32.4,37
    1+1+1+1+0+0+3.0+0.1 = 7.1 (published total_2010 column)."""
    scores = load_pri_2010_accessibility_reference(REPO_ROOT)
    al = scores["AL"]
    assert al.Q1 == 1
    assert al.Q2 == 1
    assert al.Q3 == 1
    assert al.Q4 == 1
    assert al.Q5 == 0
    assert al.Q6 == 0
    assert al.Q7_raw == 3
    assert abs(al.Q8_normalized - 0.1) < 1e-9
    assert abs(al.total - 7.1) < 1e-9


def test_load_accessibility_connecticut_top_state():
    """Connecticut had highest accessibility in 2010 (rank 1):
    Connecticut,1,1,1,1,1,1,11.0,0.3,17.3,78.5,1"""
    scores = load_pri_2010_accessibility_reference(REPO_ROOT)
    ct = scores["CT"]
    assert ct.Q1 == 1
    assert ct.Q2 == 1
    assert ct.Q3 == 1
    assert ct.Q4 == 1
    assert ct.Q5 == 1
    assert ct.Q6 == 1
    assert ct.Q7_raw == 11
    assert abs(ct.Q8_normalized - 0.3) < 1e-9
    assert abs(ct.total - 17.3) < 1e-9

"""TDD tests for the WI end-to-end chain composer (Phase 3 step 39).

Plan: ``docs/active/wi-allocation-matrix/plans/wi_allocation_matrix.md`` steps 38–40.

The chain composer stitches together the three Phase 3 inputs:

    - Allocation matrix (Phase 2 output): per-semester (lobbyist, principal)
      modeled hours.
    - Principal bill efforts (releases/wi/): per-principal-per-period bill
      identifiers with filed-percent.
    - Bill metadata (Phase 3 step 36): per-bill primary sponsors and committee.

It emits one row per (semester, principal, lobbyist, bill, sponsor) tuple, with
modeled_hours apportioned via the principal's filed-percent for that bill.

Phase 3 v1 scope baked into these tests:

- Bucket filter: ``Legislative Bills/Resolutions`` only. Other 3 buckets
  (Topics Not Yet Assigned, Budget Bill Subjects, Administrative Rulemaking)
  are deferred to Phase 3+ refinement.
- Unmatched bills (no metadata or zero structured sponsors) are skipped.
- Sponsor scope is primary-only.
- attribution_confidence is passed through from the allocation matrix.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from lobby_analysis.allocation.wi.chain import compose_chain  # noqa: F401 — drives RED
from lobby_analysis.allocation.wi.legislature import load_bill_sponsorships

_REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASES = _REPO_ROOT / "releases" / "wi"
ALLOCATIONS = _REPO_ROOT / "data" / "allocations" / "WI"
CSV_DIR = _REPO_ROOT / "data" / "bills" / "WI" / "2025"
LEGISLATORS_CSV = _REPO_ROOT / "data" / "bills" / "wi.csv"


@pytest.fixture(scope="module")
def chain_df() -> pd.DataFrame:
    """Real-data chain composed against the Phase 2 outputs + Phase 3 inputs."""
    return compose_chain(
        allocation_dir=ALLOCATIONS,
        release_dir=RELEASES,
        bill_metadata=load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV),
    )


# ---------------------------------------------------------------------------
# Plan step 39 — required tests
# ---------------------------------------------------------------------------


def test_doordash_chain_nonempty(chain_df: pd.DataFrame) -> None:
    """DoorDash (principal 11091) produces ≥1 chain row with real lobbyist + bill + sponsor."""
    dd = chain_df[chain_df["principal_id"] == 11091]
    assert len(dd) > 0
    row = dd.iloc[0]
    assert row["principal_name"] == "DoorDash, Inc."
    assert pd.notna(row["lobbyist_id"]) and int(row["lobbyist_id"]) > 0
    assert isinstance(row["lobbyist_name"], str) and row["lobbyist_name"]
    assert row["bill_id"] in {"SB 256", "AB 269"}
    assert isinstance(row["bill_title"], str) and row["bill_title"]
    assert isinstance(row["sponsor_lawmaker_id"], str) and row["sponsor_lawmaker_id"]
    assert isinstance(row["sponsor_lawmaker_name"], str) and row["sponsor_lawmaker_name"]


def test_doordash_chain_row_count_matches_join_arithmetic(chain_df: pd.DataFrame) -> None:
    """DoorDash chain row count equals product of factors per plan join arithmetic.

    From the data exploration probe:
      - 2 unique bills (SB 256, AB 269) each in both H1 and H2
      - 3 lobbyists per semester (same 3 across both)
      - SB 256: 4 primary sponsors → 3 × 4 × 2 = 24 rows
      - AB 269: 9 primary sponsors → 3 × 9 × 2 = 54 rows
      - Total: 78 rows
    """
    dd = chain_df[chain_df["principal_id"] == 11091]
    assert len(dd) == 78


def test_chain_confidence_column_uses_documented_values(chain_df: pd.DataFrame) -> None:
    """Every row's attribution_confidence is one of the documented allocation-matrix values."""
    allowed = {"exact", "ipf_fit", "zero_filed", "aggregation_flagged"}
    actual = set(chain_df["attribution_confidence"].dropna().unique())
    extra = actual - allowed
    assert not extra, f"unexpected confidence values: {extra}"
    assert not chain_df["attribution_confidence"].isna().any(), "confidence cannot be NaN"


# ---------------------------------------------------------------------------
# Schema completeness — every documented chain column must be populated
# ---------------------------------------------------------------------------


def test_chain_has_all_plan_required_columns(chain_df: pd.DataFrame) -> None:
    """Plan line 164: chain rows have these columns + a semester disambiguator."""
    required = {
        "principal_id",
        "principal_name",
        "lobbyist_id",
        "lobbyist_name",
        "bill_id",
        "bill_title",
        "modeled_hours",
        "principal_filed_percent",
        "sponsor_lawmaker_id",
        "sponsor_lawmaker_name",
        "attribution_confidence",
        "semester",
    }
    missing = required - set(chain_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_chain_individual_sponsor_id_is_ocd_person(chain_df: pd.DataFrame) -> None:
    """Rows for individual-legislator sponsors use ocd-person/... IDs."""
    # DoorDash SB 256 / AB 269 sponsors are all individuals
    dd = chain_df[chain_df["principal_id"] == 11091]
    individual_rows = dd[~dd["sponsor_lawmaker_id"].str.contains(" ", regex=False, na=False)]
    assert len(individual_rows) > 0
    for sid in individual_rows["sponsor_lawmaker_id"].unique():
        assert sid.startswith("ocd-person/"), f"unexpected sponsor_lawmaker_id: {sid}"


def test_chain_modeled_hours_equals_total_hours_times_percent(chain_df: pd.DataFrame) -> None:
    """modeled_hours = (hours_comm + hours_other) × (percent / 100) for each row.

    Spot-check DoorDash SB 256 H1: lobbyist 11077, total hours 37.81 + 9.21 = 47.01,
    21% on SB 256 → expected modeled_hours ≈ 9.87.
    """
    dd_h1_sb256_lob11077 = chain_df[
        (chain_df["principal_id"] == 11091)
        & (chain_df["lobbyist_id"] == 11077)
        & (chain_df["bill_id"] == "SB 256")
        & (chain_df["semester"] == "2025-H1")
    ]
    assert len(dd_h1_sb256_lob11077) >= 1
    row = dd_h1_sb256_lob11077.iloc[0]
    # principal_filed_percent is the float 0.21 (21%)
    assert row["principal_filed_percent"] == pytest.approx(0.21, abs=0.001)
    # hours_comm + hours_other = 37.805664 + 9.208608 = 47.014272; × 0.21 = 9.873
    assert row["modeled_hours"] == pytest.approx(9.873, abs=0.01)


def test_chain_only_emits_legislative_bucket_bills(chain_df: pd.DataFrame) -> None:
    """DoorDash has 5 'Topics Not Yet Assigned' efforts; chain emits only legislative-bucket rows.

    Total DoorDash chain rows must equal 78 (legislative path only), not 78 + something
    from the other 5 efforts.
    """
    dd = chain_df[chain_df["principal_id"] == 11091]
    assert len(dd) == 78
    # Every bill_id is in the OpenStates short form (SB/AB/etc.)
    bill_id_prefixes = {b.split()[0] for b in dd["bill_id"].unique()}
    assert bill_id_prefixes <= {"SB", "AB", "SJR", "AJR", "SR", "AR"}

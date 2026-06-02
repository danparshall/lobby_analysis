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


# ---------------------------------------------------------------------------
# Phase 3+ refinement — per-sponsor normalization
#
# The Phase 3 v1 chain replicates `modeled_hours` to every primary-sponsor row
# of a bill, so `SUM(modeled_hours) GROUP BY sponsor` over-counts a lobbyist's
# bill-allocated time once per primary sponsor. This becomes a systematic bias
# toward Assembly sponsors (Assembly bills typically have many primary
# co-authors, Senate bills fewer). The two new columns expose the uniform-share
# normalization so consumers can aggregate honestly per sponsor while keeping
# the original per-bill metric.
# ---------------------------------------------------------------------------


def test_chain_has_num_sponsors_on_bill_column(chain_df: pd.DataFrame) -> None:
    """num_sponsors_on_bill column exists with positive integer values on every row."""
    assert "num_sponsors_on_bill" in chain_df.columns
    assert not chain_df["num_sponsors_on_bill"].isna().any()
    assert (chain_df["num_sponsors_on_bill"] >= 1).all()
    # Must be integer-typed (real count, not float share)
    assert pd.api.types.is_integer_dtype(chain_df["num_sponsors_on_bill"])


def test_chain_has_modeled_hours_per_sponsor_column(chain_df: pd.DataFrame) -> None:
    """modeled_hours_per_sponsor column exists with non-negative float values."""
    assert "modeled_hours_per_sponsor" in chain_df.columns
    assert not chain_df["modeled_hours_per_sponsor"].isna().any()
    assert (chain_df["modeled_hours_per_sponsor"] >= 0).all()


def test_doordash_sb256_ab269_sponsor_normalization(chain_df: pd.DataFrame) -> None:
    """DoorDash spot-check: SB 256 has 4 sponsors, AB 269 has 9; per-sponsor share is modeled_hours / N.

    Kaericher × SB 256 × H1 baseline: modeled_hours = 9.873.
      - num_sponsors_on_bill must be 4 → modeled_hours_per_sponsor ≈ 2.468.
    Kaericher × AB 269 × H1: same modeled_hours = 9.873 (same allocation cell × same 21%).
      - num_sponsors_on_bill must be 9 → modeled_hours_per_sponsor ≈ 1.097.
    """
    sb256_rows = chain_df[
        (chain_df["principal_id"] == 11091)
        & (chain_df["lobbyist_id"] == 11077)
        & (chain_df["bill_id"] == "SB 256")
        & (chain_df["semester"] == "2025-H1")
    ]
    assert len(sb256_rows) == 4  # one row per primary sponsor
    for _, row in sb256_rows.iterrows():
        assert int(row["num_sponsors_on_bill"]) == 4
        assert row["modeled_hours_per_sponsor"] == pytest.approx(row["modeled_hours"] / 4, abs=1e-6)

    ab269_rows = chain_df[
        (chain_df["principal_id"] == 11091)
        & (chain_df["lobbyist_id"] == 11077)
        & (chain_df["bill_id"] == "AB 269")
        & (chain_df["semester"] == "2025-H1")
    ]
    assert len(ab269_rows) == 9
    for _, row in ab269_rows.iterrows():
        assert int(row["num_sponsors_on_bill"]) == 9
        assert row["modeled_hours_per_sponsor"] == pytest.approx(row["modeled_hours"] / 9, abs=1e-6)


def test_per_sponsor_sum_conserves_modeled_hours(chain_df: pd.DataFrame) -> None:
    """For any (semester, principal, lobbyist, item_id) group — i.e. one bill_efforts
    source row's emit cycle — the per-sponsor shares sum to the original modeled_hours.

    Group key uses `item_id` rather than `bill_id` because WI bill numbers collide
    within a biennium (multiple distinct `item_id`s with different titles can share
    canonical `bill_id` like "AB 1"). `item_id` is the unique source-row identifier;
    bill_id is its OpenStates-normalized projection. See
    `test_chain_item_id_disambiguates_bill_id_collisions` for the data shape.

    This is the conservation invariant that makes the normalization defensible:
    `SUM(modeled_hours_per_sponsor) GROUP BY sponsor` no longer inflates by
    sponsor count, while still preserving total bill-allocated lobbyist effort.
    """
    grp_keys = ["semester", "principal_id", "lobbyist_id", "item_id"]
    grouped = chain_df.groupby(grp_keys, as_index=False).agg(
        per_sponsor_sum=("modeled_hours_per_sponsor", "sum"),
        modeled_hours_first=("modeled_hours", "first"),
        modeled_hours_nunique=("modeled_hours", "nunique"),
    )
    # Each emit cycle's rows share a single modeled_hours value (precondition)
    assert (grouped["modeled_hours_nunique"] == 1).all()
    # And the per-sponsor sum reconstructs it
    assert ((grouped["per_sponsor_sum"] - grouped["modeled_hours_first"]).abs() < 1e-6).all()


def test_chain_has_item_id_column(chain_df: pd.DataFrame) -> None:
    """item_id column exists with positive integer values on every row.

    item_id is the source `WI_principal_bill_efforts.tsv` row identifier — the
    only stable handle for disambiguating WI's biennium-internal bill-number
    collisions (multiple distinct bills sharing canonical `bill_id="AB 1"`).
    """
    assert "item_id" in chain_df.columns
    assert not chain_df["item_id"].isna().any()
    assert (chain_df["item_id"] >= 1).all()
    assert pd.api.types.is_integer_dtype(chain_df["item_id"])


def test_chain_item_id_disambiguates_bill_id_collisions(chain_df: pd.DataFrame) -> None:
    """At least one (semester, principal_id, lobbyist_id, bill_id) group has
    multiple distinct item_ids — proving the collision is real and item_id
    resolves it.

    Empirically: principal 11473 filed effort on multiple distinct "Assembly Bill 1"
    items in 2025-H2 (e.g., item_ids 24507 voter-ID + 24521 education-assessment).
    """
    collisions = (
        chain_df.groupby(["semester", "principal_id", "lobbyist_id", "bill_id"])
        .agg(n_item_ids=("item_id", "nunique"))
        .reset_index()
    )
    multi = collisions[collisions["n_item_ids"] > 1]
    assert len(multi) > 0, (
        "expected at least one bill_id collision case; if WI portal cleaned up "
        "the duplicate-numbering issue this finding is stale and the test "
        "can be retired"
    )

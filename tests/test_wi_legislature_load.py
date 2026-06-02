"""TDD tests for the WI legislature loader (Phase 3 step 34).

Plan: ``docs/active/wi-allocation-matrix/plans/wi_allocation_matrix.md`` steps 34–37.

The loader reads the Plural Policy / OpenStates bulk CSV bundle for WI 2025
(downloaded to ``data/bills/WI/2025/``) plus the legislators roster
(``data/bills/wi.csv``), joins them, and exposes a per-bill metadata dict for
the Phase 3 chain composition. Two public entry points:

    normalize_bill_id(raw: str) -> str
        Canonicalize raw bill identifiers ("Senate Bill 3" / "SB 3" /
        "2025 SB 3" → "SB 3").

    load_bill_sponsorships(csv_dir, legislators_csv) -> dict[bill_key, BillMetadata]
        Per-bill metadata keyed by the canonical short identifier.

Phase 3 design decisions baked into these tests (see
``convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md`` once written):

- Bulk CSV is the source (not the OpenStates API or the JSON dump). 100% bill
  coverage and 99.8% sponsor person_id linkage confirmed by probe.
- Sponsor scope is PRIMARY-ONLY. CSV's ``classification`` column is exclusively
  ``'primary'`` across all 28,047 sponsorship rows — cosponsors live only in
  action description text and are deferred to Phase 3+ refinement.
- ``sponsor_lawmaker_id`` is the real ``ocd-person/...`` ID from the legislators
  roster, not a name string.
- 60 sponsorships have ``entity_type='organization'`` (Joint Legislative Council,
  Law Revision Committee) and no person_id. These are flagged as collective
  sponsors, not dropped.
- Committee name is parsed from the ``referral-committee`` action description
  text. The action's ``organization_id`` only identifies the chamber, not the
  receiving committee — committee name lives in text.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.allocation.wi.legislature import (  # noqa: F401 — drives RED
    BillMetadata,
    Sponsor,
    load_bill_sponsorships,
    normalize_bill_id,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = _REPO_ROOT / "data" / "bills" / "WI" / "2025"
LEGISLATORS_CSV = _REPO_ROOT / "data" / "bills" / "wi.csv"


# ---------------------------------------------------------------------------
# normalize_bill_id
# ---------------------------------------------------------------------------


def test_normalize_bill_id_canonicalizes_senate_long_form():
    """The verbose 'Senate Bill 3' (WI release form) collapses to OpenStates 'SB 3'."""
    assert normalize_bill_id("Senate Bill 3") == "SB 3"


def test_normalize_bill_id_canonicalizes_assembly_long_form():
    """'Assembly Bill 156' → 'AB 156'."""
    assert normalize_bill_id("Assembly Bill 156") == "AB 156"


def test_normalize_bill_id_passes_short_form_through():
    """'SB 3' / 'AB 156' are already canonical."""
    assert normalize_bill_id("SB 3") == "SB 3"
    assert normalize_bill_id("AB 156") == "AB 156"


def test_normalize_bill_id_strips_session_prefix():
    """'2025 SB 3' / '2025 Senate Bill 3' both → 'SB 3'."""
    assert normalize_bill_id("2025 SB 3") == "SB 3"
    assert normalize_bill_id("2025 Senate Bill 3") == "SB 3"


def test_normalize_bill_id_handles_joint_resolutions():
    """SJR / AJR forms."""
    assert normalize_bill_id("Senate Joint Resolution 1") == "SJR 1"
    assert normalize_bill_id("Assembly Joint Resolution 7") == "AJR 7"


# ---------------------------------------------------------------------------
# load_bill_sponsorships — total session coverage
# ---------------------------------------------------------------------------


def test_load_returns_all_2749_session_bills():
    """The full WI 2025 session has 2,749 bill records per the bulk CSV probe."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    assert len(bills) == 2749


def test_load_keys_are_canonical_short_identifiers():
    """Keys are normalized short forms like 'SB 3' / 'AB 156', not UUIDs or long forms."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    assert "SB 3" in bills
    assert "AB 156" in bills
    # No UUID-style keys
    assert not any(k.startswith("ocd-bill/") for k in bills)
    # No long-form keys
    assert "Senate Bill 3" not in bills


# ---------------------------------------------------------------------------
# load_bill_sponsorships — Senate Bill 3 metadata (the plan's known-bill spot-check)
# ---------------------------------------------------------------------------


def test_sb3_title_about_wind_and_solar():
    """SB 3 title is about local approval for wind/solar projects."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    sb3 = bills["SB 3"]
    assert "wind" in sb3.title.lower()
    assert "solar" in sb3.title.lower()


def test_sb3_has_five_primary_sponsors_named_correctly():
    """SB 3 has exactly 5 primary sponsors: Marklein, Tomczyk, Jacque, Nass, Quinn."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    sb3 = bills["SB 3"]
    assert len(sb3.primary_sponsors) == 5
    assert {sp.name for sp in sb3.primary_sponsors} == {
        "Marklein",
        "Tomczyk",
        "Jacque",
        "Nass",
        "Quinn",
    }


def test_sb3_sponsors_have_ocd_person_ids():
    """All 5 SB 3 primary sponsors are individuals with ocd-person/... IDs."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    sb3 = bills["SB 3"]
    for sp in sb3.primary_sponsors:
        assert sp.person_id is not None
        assert sp.person_id.startswith("ocd-person/")
        assert sp.is_collective is False


def test_sb3_sponsors_are_all_senators():
    """SB 3 is Senate-originated; all 5 primary sponsors are upper-chamber legislators."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    sb3 = bills["SB 3"]
    chambers = {sp.chamber for sp in sb3.primary_sponsors}
    assert chambers == {"upper"}


def test_sb3_committee_is_utilities_and_tourism():
    """SB 3 was referred to the Committee on Utilities and Tourism (parsed from action text)."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)
    sb3 = bills["SB 3"]
    assert sb3.committee_name == "Committee on Utilities and Tourism"


# ---------------------------------------------------------------------------
# Collective-entity sponsors (Joint Legislative Council, Law Revision Committee)
# ---------------------------------------------------------------------------


def test_collective_sponsor_is_flagged_not_dropped():
    """Bills sponsored by 'Joint Legislative Council' (an organization, not a person)
    are surfaced via is_collective=True and person_id=None — not silently dropped."""
    bills = load_bill_sponsorships(CSV_DIR, LEGISLATORS_CSV)

    # Find any bill whose primary_sponsors contains a Joint Legislative Council entry
    matches = [
        (key, b)
        for key, b in bills.items()
        if any(sp.name == "Joint Legislative Council" for sp in b.primary_sponsors)
    ]
    assert matches, "expected at least one bill with Joint Legislative Council sponsor"

    _, sample_bill = matches[0]
    jlc_sponsor = next(
        sp for sp in sample_bill.primary_sponsors if sp.name == "Joint Legislative Council"
    )
    assert jlc_sponsor.is_collective is True
    assert jlc_sponsor.person_id is None
    assert jlc_sponsor.chamber is None

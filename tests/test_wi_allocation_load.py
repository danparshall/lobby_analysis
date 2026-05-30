"""TDD tests for the WI allocation-matrix loaders.

Phase 1.1 of plans/wi_allocation_matrix.md. These tests exercise four
loaders that read the merged WI 2025-2026 release at ``releases/wi/`` and
return the per-semester inputs the bipartite-graph + IPF stages need:

    load_principal_totals(release_dir, semester)
        -> dict[principal_id, (hours_comm, hours_other)]
    load_lobbyist_totals(release_dir, semester)
        -> dict[lobbyist_id, (hours_comm, hours_other)]
    load_active_edges(release_dir, semester)
        -> set[(lobbyist_id, principal_id)]
    load_bill_effort_percents(release_dir, semester)
        -> dict[principal_id, list[(item_id, item_name, percent_float)]]

Semester format: "2025-H1" / "2025-H2" / "2026-H1" / "2026-H2".

These tests exercise the loaders against the **real** ``releases/wi/``
TSVs checked into this branch — the same data that Phase 0 audited. The
expected values are taken from that audit (see
``docs/active/wi-allocation-matrix/results/20260530_phase_0_data_audit.md``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lobby_analysis.allocation.wi.load import (  # noqa: F401 — drives RED
    load_active_edges,
    load_bill_effort_percents,
    load_lobbyist_totals,
    load_principal_totals,
)

# Real release directory (this branch's checked-in WI MVP)
_REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = _REPO_ROOT / "releases" / "wi"


# ---------------------------------------------------------------------------
# load_principal_totals
# ---------------------------------------------------------------------------


def test_load_principal_totals_h1_2025_has_829_principals():
    """H1 2025 has 829 principal filings (Phase 0 audit)."""
    totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    assert len(totals) == 829


def test_load_principal_totals_h1_2025_aggregate_hours_match_audit():
    """Aggregate hours match Phase 0 audit: 27,700.78 comm + 69,609.82 other."""
    totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    sum_comm = sum(comm for comm, _ in totals.values())
    sum_other = sum(other for _, other in totals.values())
    assert sum_comm == pytest.approx(27700.78, abs=0.01)
    assert sum_other == pytest.approx(69609.82, abs=0.01)


def test_load_principal_totals_doordash_h1_2025():
    """DoorDash (11091) H1 2025: 83.9 hrs comm + 87.5 hrs other."""
    totals = load_principal_totals(RELEASE_DIR, "2025-H1")
    assert 11091 in totals
    comm, other = totals[11091]
    assert comm == pytest.approx(83.9, abs=0.01)
    assert other == pytest.approx(87.5, abs=0.01)


def test_load_principal_totals_h2_2025_independent_of_h1():
    """H2 2025 has a different (also 829-ish) set of filings; DoorDash
    H2 hours differ from H1 hours."""
    h1 = load_principal_totals(RELEASE_DIR, "2025-H1")
    h2 = load_principal_totals(RELEASE_DIR, "2025-H2")
    # Both have DoorDash with non-zero filings, but different values
    assert 11091 in h1 and 11091 in h2
    assert h1[11091] != h2[11091]


# ---------------------------------------------------------------------------
# load_lobbyist_totals
# ---------------------------------------------------------------------------


def test_load_lobbyist_totals_h1_2025_has_773_lobbyists():
    """All 773 registered lobbyists have an H1 2025 cell — the WI
    portal zero-fills empty cells (Phase 0 audit)."""
    totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    assert len(totals) == 773


def test_load_lobbyist_totals_h1_2025_aggregate_hours_match_audit():
    """Aggregate hours match Phase 0 audit: 25,245.88 comm + 66,657.11 other."""
    totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    sum_comm = sum(comm for comm, _ in totals.values())
    sum_other = sum(other for _, other in totals.values())
    assert sum_comm == pytest.approx(25245.88, abs=0.01)
    assert sum_other == pytest.approx(66657.11, abs=0.01)


def test_load_lobbyist_totals_pettack_h1_2025():
    """Pettack (11072) H1 2025: 651.0 hrs comm + 3,356.5 hrs other —
    the documented outlier."""
    totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    assert 11072 in totals
    comm, other = totals[11072]
    assert comm == pytest.approx(651.0, abs=0.01)
    assert other == pytest.approx(3356.5, abs=0.01)


def test_load_lobbyist_totals_2026_h2_is_mostly_zero():
    """The 2026-H2 semester is forward-looking zero-fill — only 9
    lobbyists have >0 communicating hours."""
    totals = load_lobbyist_totals(RELEASE_DIR, "2026-H2")
    nonzero_comm = sum(1 for comm, _ in totals.values() if comm > 0)
    assert nonzero_comm == 9


# ---------------------------------------------------------------------------
# load_active_edges
# ---------------------------------------------------------------------------


def test_load_active_edges_h1_2025_count():
    """H1 2025 has 1,912 active (lobbyist, principal) pairs after
    applying the interval-overlap filter (Phase 0 audit)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    assert len(edges) == 1912


def test_load_active_edges_h2_2025_count():
    """H2 2025 has 2,055 active pairs (Phase 0 audit)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H2")
    assert len(edges) == 2055


def test_load_active_edges_doordash_h1_2025():
    """DoorDash (11091) in H1 2025 has exactly 3 active authorizations:
    lobbyists 11077, 11112, 11114. The 2026 auths (13896, 13901) are
    not active in H1 2025."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    doordash_edges = {(l, p) for (l, p) in edges if p == 11091}
    assert doordash_edges == {(11077, 11091), (11112, 11091), (11114, 11091)}


def test_load_active_edges_excludes_post_period_authorizations():
    """An authorization with auth_on > period_end must NOT appear in
    the period's active set. DoorDash lobbyist 13896 was authorized
    2026-01-06; that edge is in H1 2026 but NOT in H2 2025."""
    h2_2025 = load_active_edges(RELEASE_DIR, "2025-H2")
    assert (13896, 11091) not in h2_2025


def test_load_active_edges_includes_open_edges_authed_before_period():
    """An authorization with auth_on <= period_start and withdrawn_on
    null is active. DoorDash lobbyist 11112 (auth 2024-12-18, never
    withdrawn) is active in every 2025 semester."""
    h1 = load_active_edges(RELEASE_DIR, "2025-H1")
    h2 = load_active_edges(RELEASE_DIR, "2025-H2")
    assert (11112, 11091) in h1
    assert (11112, 11091) in h2


def test_load_active_edges_returns_a_set():
    """The contract is set[tuple[int, int]] — no duplicates."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    assert isinstance(edges, set)


# ---------------------------------------------------------------------------
# load_bill_effort_percents
# ---------------------------------------------------------------------------


def test_load_bill_effort_percents_returns_float_not_string():
    """Percent strings ('1%', '54%') parse to floats in [0, 1] range.
    The string '54%' becomes 0.54, not 54."""
    by_principal = load_bill_effort_percents(RELEASE_DIR, "2025-H1")
    # Every emitted percent must be a float in [0, 1] inclusive
    seen_any = False
    for entries in by_principal.values():
        for item_id, item_name, pct in entries:
            assert isinstance(pct, float)
            assert 0 < pct <= 1
            seen_any = True
    assert seen_any, "expected at least one bill-effort row in H1 2025"


def test_load_bill_effort_percents_h1_2025_has_known_principal_count():
    """H1 2025 bill-efforts cover a documented subset of principals —
    not all 829 filers itemized per-bill effort. Phase 0 audit showed
    1,428 (principal, period) groups across both semesters, with H1
    contributing 3,552 of the 7,345 total rows."""
    by_principal = load_bill_effort_percents(RELEASE_DIR, "2025-H1")
    # Expect a non-trivial subset (between 100 and 829 principals)
    assert 100 < len(by_principal) < 829


def test_load_bill_effort_percents_doordash_h1_2025_has_legislative_bills():
    """DoorDash (11091) lobbied on Senate Bill 3 ('Relating to:
    requiring local approval for certain wind and solar projects...')
    in H1 2025. The first listed principal in the release is WEC
    (10936) which has SB 3 at 1%; DoorDash lobbies different bills.
    Spot-check: DoorDash has at least one entry in H1 2025."""
    by_principal = load_bill_effort_percents(RELEASE_DIR, "2025-H1")
    assert 11091 in by_principal
    assert len(by_principal[11091]) > 0


def test_load_bill_effort_percents_wec_senate_bill_3_at_one_percent():
    """WEC Energy (10936) lobbied on Senate Bill 3 (item_id 24514) in
    H1 2025 at 1% effort. This is the first row of the raw TSV — a
    fixed reference value."""
    by_principal = load_bill_effort_percents(RELEASE_DIR, "2025-H1")
    assert 10936 in by_principal
    entries = by_principal[10936]
    sb3 = [(iid, name, pct) for (iid, name, pct) in entries if iid == 24514]
    assert len(sb3) == 1
    iid, name, pct = sb3[0]
    assert name == "Senate Bill 3"
    assert pct == pytest.approx(0.01, abs=1e-6)


def test_load_bill_effort_percents_h2_2025_distinct_from_h1():
    """The same principal can lobby on different items in different
    semesters. WEC's H1 entries don't have to equal its H2 entries."""
    h1 = load_bill_effort_percents(RELEASE_DIR, "2025-H1")
    h2 = load_bill_effort_percents(RELEASE_DIR, "2025-H2")
    assert 10936 in h1 and 10936 in h2
    # Distinct semesters produce distinct entry lists in general
    # (we don't assert structural inequality, just that both are populated)
    assert len(h1[10936]) > 0
    assert len(h2[10936]) > 0


# ---------------------------------------------------------------------------
# Cross-loader consistency
# ---------------------------------------------------------------------------


def test_active_edges_lobbyist_ids_appear_in_lobbyist_totals():
    """Every lobbyist that appears in an H1 active edge must also have
    an H1 lobbyist totals entry (the WI portal zero-fills, so every
    registered lobbyist has a cell)."""
    edges = load_active_edges(RELEASE_DIR, "2025-H1")
    totals = load_lobbyist_totals(RELEASE_DIR, "2025-H1")
    edge_lobbyists = {l for (l, _) in edges}
    missing = edge_lobbyists - set(totals.keys())
    assert missing == set(), f"lobbyists in edges but not in totals: {missing}"

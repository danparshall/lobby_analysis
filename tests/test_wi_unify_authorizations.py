"""Behavior tests for the lobbyist-side ⇄ principal-side authorization
table unification.

The unification step is what answers the load-bearing question of
this branch: "how many Schlaak-class lobbyists exist?" — lobbyists
that are reachable only via principal-side back-links, never via the
LobbyistList grid AJAX (the source the lobbyist-side scrape used).

Output schema adds two columns to the row dict:
- ``discovered_via``: one of ``lobbyist``, ``principal``, ``both``
- ``lobbyist_in_grid``: bool — was this lobbyist_id in the LobbyistList
  grid AJAX response when the lobbyist-side scrape ran?

Edge identity for matching across sides = (lobbyist_id, principal_id,
authorized_on). Re-authorization (same lobbyist+principal, different
authorized_on) produces two distinct rows.
"""

from __future__ import annotations

import logging
from datetime import date

from lobby_analysis.io.wi.unify_authorizations import unify_authorization_tables


def _row(lid: int, pid: int, auth: date | None, withd: date | None) -> dict:
    """Helper: build an edge dict in the same shape the TSV writers
    produce (string-typed dates, blank for None)."""
    return {
        "lobbyist_id": lid,
        "principal_id": pid,
        "authorized_on": auth.isoformat() if auth else "",
        "withdrawn_on": withd.isoformat() if withd else "",
    }


def test_unify_produces_three_provenance_classes():
    """Lobbyist side has edges A, B; principal side has edges B, C.
    Union has edges A, B, C with discovered_via lobbyist, both,
    principal respectively."""
    lobbyist_side = [
        _row(11042, 11158, date(2024, 12, 17), None),  # A — lobbyist only
        _row(11042, 11590, date(2025, 1, 3), date(2025, 6, 30)),  # B — both sides
    ]
    principal_side = [
        _row(11042, 11590, date(2025, 1, 3), date(2025, 6, 30)),  # B — both sides
        _row(12694, 12997, date(2026, 1, 8), None),  # C — principal only (Schlaak)
    ]
    grid_ids = {11042}  # 12694 (Schlaak) is NOT in the grid

    unified = unify_authorization_tables(
        lobbyist_side_rows=lobbyist_side,
        principal_side_rows=principal_side,
        lobbyist_grid_ids=grid_ids,
    )

    assert len(unified) == 3
    by_via = {r["discovered_via"]: r for r in unified}
    assert set(by_via.keys()) == {"lobbyist", "both", "principal"}
    assert by_via["lobbyist"]["principal_id"] == 11158
    assert by_via["both"]["principal_id"] == 11590
    assert by_via["principal"]["principal_id"] == 12997


def test_unify_surfaces_schlaak_class_with_lobbyist_in_grid_false():
    """Load-bearing test for the whole plan. A principal-only edge
    whose lobbyist_id is NOT in the LobbyistList grid response must
    appear in the unified output with discovered_via='principal' AND
    lobbyist_in_grid=False — that combination is the filter the
    results doc uses to count Schlaak-class lobbyists."""
    principal_side = [
        _row(12694, 12997, date(2026, 1, 8), None),  # Schlaak / WCTA
    ]
    grid_ids = set()  # empty — 12694 not in grid

    unified = unify_authorization_tables(
        lobbyist_side_rows=[],
        principal_side_rows=principal_side,
        lobbyist_grid_ids=grid_ids,
    )

    assert len(unified) == 1
    assert unified[0]["discovered_via"] == "principal"
    assert unified[0]["lobbyist_in_grid"] is False
    assert unified[0]["lobbyist_id"] == 12694


def test_unify_marks_lobbyist_in_grid_true_for_known_lobbyists():
    """A principal-only edge for a known-grid lobbyist (e.g., the
    parser missed the edge on the lobbyist's page but caught it on the
    principal's page — a parser bug, not a Schlaak case) must have
    lobbyist_in_grid=True. The Schlaak count must NOT include these."""
    principal_side = [
        _row(11042, 11158, date(2024, 12, 17), None),
    ]
    grid_ids = {11042}  # 11042 IS in grid

    unified = unify_authorization_tables(
        lobbyist_side_rows=[],
        principal_side_rows=principal_side,
        lobbyist_grid_ids=grid_ids,
    )

    assert unified[0]["discovered_via"] == "principal"
    assert unified[0]["lobbyist_in_grid"] is True  # NOT a Schlaak case


def test_unify_handles_reauthorization_as_two_distinct_rows():
    """Same (lobbyist, principal) but different authorized_on dates =
    a re-authorization, e.g., the lobbyist withdrew then was
    re-authorized in the same session. Edge identity includes
    authorized_on, so each authorization is its own row."""
    lobbyist_side = [
        _row(11042, 11158, date(2024, 12, 17), date(2025, 3, 1)),
        _row(11042, 11158, date(2025, 6, 1), None),
    ]

    unified = unify_authorization_tables(
        lobbyist_side_rows=lobbyist_side,
        principal_side_rows=[],
        lobbyist_grid_ids={11042},
    )

    assert len(unified) == 2
    auth_dates = sorted(r["authorized_on"] for r in unified)
    assert auth_dates == ["2024-12-17", "2025-06-01"]


def test_unify_takes_more_informative_withdrawn_on_when_sides_disagree(
    caplog,
):
    """Same edge, lobbyist side shows withdrawn_on=date, principal
    side shows N/A (None). The withdrawn date is more informative
    (the side that saw the withdrawal knows something the other
    doesn't, possibly due to portal-snapshot lag). Take the date.

    Log a WARNING so disagreements are auditable — silent reconciliation
    in a 944-principal scrape would mask portal inconsistencies that
    might point at a real data-quality issue."""
    lobbyist_side = [
        _row(11042, 11158, date(2024, 12, 17), date(2025, 3, 1)),
    ]
    principal_side = [
        _row(11042, 11158, date(2024, 12, 17), None),
    ]

    with caplog.at_level(logging.WARNING):
        unified = unify_authorization_tables(
            lobbyist_side_rows=lobbyist_side,
            principal_side_rows=principal_side,
            lobbyist_grid_ids={11042},
        )

    assert len(unified) == 1
    assert unified[0]["discovered_via"] == "both"
    assert unified[0]["withdrawn_on"] == "2025-03-01"
    assert any("withdrawn_on" in rec.message.lower() for rec in caplog.records)


def test_unify_takes_later_withdrawn_date_when_both_present_and_disagree(
    caplog,
):
    """Both sides show a withdrawn date but the dates differ. Take
    the later one (the earlier one is presumably stale) and warn."""
    lobbyist_side = [
        _row(11042, 11158, date(2024, 12, 17), date(2025, 3, 1)),
    ]
    principal_side = [
        _row(11042, 11158, date(2024, 12, 17), date(2025, 5, 15)),
    ]

    with caplog.at_level(logging.WARNING):
        unified = unify_authorization_tables(
            lobbyist_side_rows=lobbyist_side,
            principal_side_rows=principal_side,
            lobbyist_grid_ids={11042},
        )

    assert unified[0]["withdrawn_on"] == "2025-05-15"
    assert any("withdrawn_on" in rec.message.lower() for rec in caplog.records)

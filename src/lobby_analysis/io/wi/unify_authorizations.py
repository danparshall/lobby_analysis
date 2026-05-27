"""Unify the lobbyist-side and principal-side authorization tables
into a single bipartite edge table with provenance.

This is the deliverable that answers the load-bearing question of
the wi-disclosure-explore branch: **how many Schlaak-class lobbyists
exist?** — lobbyists reachable ONLY via principal-side back-link,
silently omitted from the LobbyistList grid AJAX (and therefore
also from the WI_directory_lobbyists.xls, which shares the grid's
filter rule).

Output schema = the 4-column authorization edge schema plus two
provenance columns:

* ``discovered_via ∈ {"lobbyist", "principal", "both"}`` — which
  side(s) of the scrape saw this edge.
* ``lobbyist_in_grid: bool`` — did the LobbyistList grid AJAX return
  this lobbyist_id? Schlaak-class lobbyists have
  ``lobbyist_in_grid=False``; filter on
  ``discovered_via='principal' AND lobbyist_in_grid=False`` to count
  them.

Edge identity for matching across sides = ``(lobbyist_id,
principal_id, authorized_on)``. Same lobbyist+principal with
different ``authorized_on`` (re-authorization within a session) =
two distinct edges.

When the two sides disagree on ``withdrawn_on`` for the same edge,
we take the more informative value (a date over ``None``; the later
date when both are dates) and emit a WARNING — silent reconciliation
in a 944-principal scrape would mask portal-snapshot lag or real
data-quality issues.
"""

from __future__ import annotations

import logging
from typing import Iterable

logger = logging.getLogger(__name__)


UNIFIED_FIELDNAMES = [
    "lobbyist_id",
    "principal_id",
    "authorized_on",
    "withdrawn_on",
    "discovered_via",
    "lobbyist_in_grid",
]


def _edge_key(row: dict) -> tuple[int, int, str]:
    """Edge identity = (lobbyist_id, principal_id, authorized_on as
    string). String comparison on ISO dates is order-preserving and
    sidesteps date-parsing for blanks."""
    return (
        int(row["lobbyist_id"]),
        int(row["principal_id"]),
        row["authorized_on"],
    )


def _reconcile_withdrawn_on(
    lobbyist_value: str, principal_value: str, edge_key: tuple
) -> str:
    """Pick the more informative of two ``withdrawn_on`` strings.

    Empty = None (still active per that source); ISO date string
    otherwise. Preference order:

    1. Both empty → empty.
    2. One empty, one date → the date (the source that saw the
       withdrawal knows something the other doesn't).
    3. Both dates, equal → that date.
    4. Both dates, different → the later (lexically max — works on
       ISO YYYY-MM-DD strings), with a WARNING.
    """
    if lobbyist_value == principal_value:
        return lobbyist_value
    if not lobbyist_value:
        logger.warning(
            "withdrawn_on disagreement on edge %s — lobbyist side=empty, "
            "principal side=%s; taking principal side.",
            edge_key,
            principal_value,
        )
        return principal_value
    if not principal_value:
        logger.warning(
            "withdrawn_on disagreement on edge %s — lobbyist side=%s, "
            "principal side=empty; taking lobbyist side.",
            edge_key,
            lobbyist_value,
        )
        return lobbyist_value
    # Both dates, differ — take the later (ISO strings are
    # lexicographically comparable as dates).
    later = max(lobbyist_value, principal_value)
    logger.warning(
        "withdrawn_on disagreement on edge %s — lobbyist=%s, principal=%s; "
        "taking later (%s).",
        edge_key,
        lobbyist_value,
        principal_value,
        later,
    )
    return later


def unify_authorization_tables(
    lobbyist_side_rows: Iterable[dict],
    principal_side_rows: Iterable[dict],
    lobbyist_grid_ids: set[int],
) -> list[dict]:
    """Unify two edge tables with provenance.

    See module docstring for output schema. Both input iterables must
    yield dicts in the same shape produced by
    ``write_authorizations_tsv`` (string-typed dates, blank for None).

    ``lobbyist_grid_ids`` is the set of lobbyist IDs returned by the
    LobbyistList grid AJAX at scrape time — used to compute the
    ``lobbyist_in_grid`` flag. Pass the 774-ID set captured by
    ``lobbyist_id_discovery.parse_lobbyist_ids`` against the grid
    snapshot.
    """
    lobbyist_by_key = {_edge_key(r): r for r in lobbyist_side_rows}
    principal_by_key = {_edge_key(r): r for r in principal_side_rows}

    all_keys = sorted(set(lobbyist_by_key) | set(principal_by_key))

    unified: list[dict] = []
    for key in all_keys:
        in_lobbyist = key in lobbyist_by_key
        in_principal = key in principal_by_key

        if in_lobbyist and in_principal:
            discovered_via = "both"
            l_row = lobbyist_by_key[key]
            p_row = principal_by_key[key]
            withdrawn_on = _reconcile_withdrawn_on(
                l_row["withdrawn_on"], p_row["withdrawn_on"], key
            )
            base = l_row  # both rows share lid/pid/auth; either is fine for those
        elif in_lobbyist:
            discovered_via = "lobbyist"
            base = lobbyist_by_key[key]
            withdrawn_on = base["withdrawn_on"]
        else:
            discovered_via = "principal"
            base = principal_by_key[key]
            withdrawn_on = base["withdrawn_on"]

        lobbyist_id = int(base["lobbyist_id"])
        unified.append(
            {
                "lobbyist_id": lobbyist_id,
                "principal_id": int(base["principal_id"]),
                "authorized_on": base["authorized_on"],
                "withdrawn_on": withdrawn_on,
                "discovered_via": discovered_via,
                "lobbyist_in_grid": lobbyist_id in lobbyist_grid_ids,
            }
        )

    return unified

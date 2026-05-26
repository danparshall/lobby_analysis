"""Behavior tests for principal ID discovery.

The principal-side scrape universe is the union of two sources:

* ``WI_directory_principals.xls`` — 904 registered principals (the
  Ethics Commission's official roster, filter rule empirically
  ``cessation_date IS NULL`` per the 2026-05-26 gap investigation).
* The existing lobbyist-side auth-graph TSV
  (``WI_lobbyist_principal_authorizations.tsv``) — 942 distinct
  principal IDs reached by the lobbyist-side scrape.

Their union is 944 IDs (902 intersection, 40 auth-only ceased/redacted,
2 dir-only Schlaak-class downstream consequences). We don't enumerate
the 10000-13500 ID range as a third source — that's deferred per the
plan's "What could change" notes.

Unit tests use hand-built tiny fixtures so they don't depend on shifts
in the real data shape between branches. A smoke test against the real
``.xls`` is included but skipped when the file isn't present (CI / fresh
worktrees).
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from lobby_analysis.io.wi.principal_id_discovery import (
    _ids_from_tsv,
    discover_principal_ids,
)


def _write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["lobbyist_id", "principal_id", "authorized_on", "withdrawn_on"],
            delimiter="\t",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_ids_from_tsv_extracts_distinct_principal_ids(tmp_path: Path):
    """Three rows, three distinct principal IDs → set of 3 ints."""
    tsv = tmp_path / "auth_graph.tsv"
    _write_tsv(
        tsv,
        [
            {"lobbyist_id": "100", "principal_id": "11000",
             "authorized_on": "2025-01-01", "withdrawn_on": ""},
            {"lobbyist_id": "101", "principal_id": "11001",
             "authorized_on": "2025-01-02", "withdrawn_on": ""},
            {"lobbyist_id": "102", "principal_id": "11002",
             "authorized_on": "2025-01-03", "withdrawn_on": ""},
        ],
    )

    ids = _ids_from_tsv(tsv)

    assert ids == {11000, 11001, 11002}
    assert all(isinstance(i, int) for i in ids)


def test_ids_from_tsv_handles_repeated_principal_ids(tmp_path: Path):
    """The auth-graph TSV has 2,251 (lobbyist, principal) rows for 942
    distinct principals — the same principal shows up many times (one
    row per authorizing lobbyist). The discovery function must
    deduplicate."""
    tsv = tmp_path / "auth_graph.tsv"
    _write_tsv(
        tsv,
        [
            {"lobbyist_id": "100", "principal_id": "11000",
             "authorized_on": "2025-01-01", "withdrawn_on": ""},
            {"lobbyist_id": "101", "principal_id": "11000",
             "authorized_on": "2025-01-02", "withdrawn_on": ""},
            {"lobbyist_id": "102", "principal_id": "11000",
             "authorized_on": "2025-01-03", "withdrawn_on": ""},
            {"lobbyist_id": "103", "principal_id": "11001",
             "authorized_on": "2025-01-04", "withdrawn_on": ""},
        ],
    )

    ids = _ids_from_tsv(tsv)

    assert ids == {11000, 11001}


def test_discover_unions_xls_and_tsv_sources(monkeypatch, tmp_path: Path):
    """The whole point of the discovery layer is the union — verify it.

    Mock ``_ids_from_xls`` so we don't need to ship a binary .xls
    fixture. The .xls reader is a thin pandas.read_excel wrapper;
    integration coverage comes from the live scrape, not unit tests.

    Hand-built TSV represents the auth-graph; the mocked .xls source
    returns a disjoint-with-overlap set; union should preserve all
    distinct IDs.
    """
    tsv = tmp_path / "auth_graph.tsv"
    _write_tsv(
        tsv,
        [
            {"lobbyist_id": "100", "principal_id": "11000",
             "authorized_on": "2025-01-01", "withdrawn_on": ""},
            {"lobbyist_id": "101", "principal_id": "11001",
             "authorized_on": "2025-01-02", "withdrawn_on": ""},
        ],
    )

    # Simulate the .xls source returning a different (overlapping) set.
    # 11001 overlaps with TSV; 11500, 12500 are dir-only (e.g., redacted
    # principals); 11000 is missing from .xls but present in TSV (e.g.,
    # a ceased principal the directory filter dropped).
    monkeypatch.setattr(
        "lobby_analysis.io.wi.principal_id_discovery._ids_from_xls",
        lambda _path: {11001, 11500, 12500},
    )

    ids = discover_principal_ids(
        directory_xls_path=Path("/nonexistent.xls"),
        auth_graph_tsv_path=tsv,
    )

    assert ids == {11000, 11001, 11500, 12500}


REAL_XLS = Path(
    "/Users/dan/data/lobby_analysis/disclosures/WI/WI_directory_principals.xls"
)


@pytest.mark.skipif(
    not REAL_XLS.exists(),
    reason="real .xls not present (CI / fresh worktree)",
)
def test_smoke_real_xls_loads_at_least_900_principal_ids():
    """Smoke test: production wiring through pandas → xlrd → header
    skip → Principal ID column must produce a sensible-size set of
    ints. Loose lower-bound check that survives data refreshes between
    sessions (the directory had 905 rows on 5/25 and 906 on the
    inspection in this session; expect that count to drift)."""
    from lobby_analysis.io.wi.principal_id_discovery import _ids_from_xls

    ids = _ids_from_xls(REAL_XLS)

    assert len(ids) >= 900
    assert all(isinstance(i, int) for i in ids)

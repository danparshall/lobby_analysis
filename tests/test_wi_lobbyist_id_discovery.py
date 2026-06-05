"""Behavior tests for extracting lobbyist IDs from the WI portal's
LobbyistList grid HTML.

The `.xls` directory export at ``data/disclosures/WI/WI_directory_lobbyists.xls``
carries lobbyist names but no Lobbyist ID column, so we recover IDs by
parsing them out of the grid's per-lobbyist detail-page hrefs
(``/Who/LobbyistInformation/{session}/Information/{id}``).

Ground truth comes from a real snapshot of the AJAX response that
populates the LobbyistList grid (fixture:
``tests/fixtures/wi/lobbyist_grid_2025REG.html`` — POST to
``/Who/Lobbyists/2025REG/ShowLobbyistList`` with ``pageSize=1000``,
captured 2026-05-26). The portal's UI footer reported "774 of 774
results" for the 2025-2026 session at capture time.
"""

from __future__ import annotations

from pathlib import Path

from lobby_analysis.io.wi.lobbyist_id_discovery import (
    parse_lobbyist_ids,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "wi"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_extracts_all_774_lobbyist_ids_from_grid_fixture():
    """The 2025REG grid snapshot has 774 distinct lobbyist detail-page
    URLs — the parser must recover all of them."""
    html = _load_fixture("lobbyist_grid_2025REG.html")

    ids = parse_lobbyist_ids(html)

    assert len(ids) == 774


def test_includes_canonical_lobbyist_11042():
    """Lobbyist 11042 is our parser-fixture target — the discovery step
    must surface that ID in the 2025REG grid, otherwise the rest of the
    pipeline can't reach it."""
    html = _load_fixture("lobbyist_grid_2025REG.html")

    ids = parse_lobbyist_ids(html)

    assert 11042 in ids


def test_returns_sorted_unique_ints():
    """Downstream code (checkpoint filenames, ordering for the scrape
    loop) assumes IDs are sorted unique ints — not strings, not in
    HTML-order with duplicates from the same row appearing twice."""
    html = _load_fixture("lobbyist_grid_2025REG.html")

    ids = parse_lobbyist_ids(html)

    assert ids == sorted(set(ids))
    assert all(isinstance(i, int) for i in ids)


def test_empty_html_returns_empty_list():
    """No matching hrefs → no IDs. Empty is a valid outcome (e.g.,
    a search query with no hits); we don't raise."""
    assert parse_lobbyist_ids("<html><body>nothing here</body></html>") == []

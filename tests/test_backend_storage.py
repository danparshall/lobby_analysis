"""Behavior tests for src/lobby_analysis/backend/storage.py.

Tests target the public CRUD surface: insert, get, list with filters,
search by filer name. The `engine` fixture (in conftest.py) connects to
the shared `lobby_test` postgres database; the autouse TRUNCATE fixture
gives each test a clean `filings` table.
"""

from lobby_analysis.backend.storage import (
    get_filing,
    insert_filing,
    list_filings,
    search_filings,
)
from lobby_analysis.models.entities import Person
from lobby_analysis.models.filings import LobbyingFiling


def _make_filing(
    id: str,
    state: str = "OH",
    filer_name: str = "Nathan Aichele",
    filer_role: str = "lobbyist",
) -> LobbyingFiling:
    return LobbyingFiling(
        id=id,
        state=state,
        filing_type="activity_report",
        filer_role=filer_role,
        filer_person=Person(id=f"p-{id}", name=filer_name, source_state=state),
    )


def test_insert_and_get_roundtrip(engine):
    filing = _make_filing("f-1")

    inserted_id = insert_filing(engine, filing)
    assert inserted_id == "f-1"

    retrieved = get_filing(engine, "f-1")
    assert retrieved is not None
    assert retrieved == filing


def test_get_returns_none_for_unknown_id(engine):
    assert get_filing(engine, "no-such-id") is None


def test_list_filters_by_state(engine):
    insert_filing(engine, _make_filing("oh-1", state="OH"))
    insert_filing(engine, _make_filing("ca-1", state="CA"))

    oh_only = list_filings(engine, state="OH")
    assert len(oh_only) == 1
    assert oh_only[0].id == "oh-1"


def test_list_returns_all_when_unfiltered(engine):
    insert_filing(engine, _make_filing("f-1"))
    insert_filing(engine, _make_filing("f-2"))

    all_filings = list_filings(engine)
    assert len(all_filings) == 2


def test_search_by_filer_name(engine):
    insert_filing(engine, _make_filing("f-1", filer_name="Nathan Aichele"))
    insert_filing(engine, _make_filing("f-2", filer_name="Mike Abrams"))

    hits = search_filings(engine, "Aich")
    assert len(hits) == 1
    assert hits[0].id == "f-1"


def test_search_is_case_insensitive(engine):
    insert_filing(engine, _make_filing("f-1", filer_name="Nathan Aichele"))

    hits = search_filings(engine, "aichele")
    assert len(hits) == 1

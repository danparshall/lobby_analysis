"""Behavior tests for src/lobby_analysis/backend/storage.py.

Tests target the public CRUD surface: insert, get, list with filters,
search by filer name. The `engine` fixture (in conftest.py) connects to
the shared `lobby_test` postgres database; the autouse TRUNCATE fixture
gives each test a clean `filings` table.
"""

from lobby_analysis.backend.storage import (
    count_filings,
    get_filing,
    insert_filing,
    list_filings,
    search_filings,
    stats,
)
from lobby_analysis.models.entities import Organization, Person
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


def _make_client_filing(
    id: str, org_name: str, total_expenditure: float, state: str = "WI"
) -> LobbyingFiling:
    return LobbyingFiling(
        id=id,
        state=state,
        filing_type="expenditure_report",
        filer_role="client",
        filer_organization=Organization(id=f"o-{id}", name=org_name, source_state=state),
        total_expenditure=total_expenditure,
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


def test_count_filings_respects_filters(engine):
    insert_filing(engine, _make_filing("oh-1", state="OH"))
    insert_filing(engine, _make_filing("oh-2", state="OH"))
    insert_filing(engine, _make_filing("ca-1", state="CA"))

    assert count_filings(engine) == 3
    assert count_filings(engine, state="OH") == 2
    assert count_filings(engine, state="CA") == 1


def test_list_offset_paginates(engine):
    for i in range(5):
        insert_filing(engine, _make_filing(f"f-{i}"))

    page1 = list_filings(engine, limit=2, offset=0)
    page2 = list_filings(engine, limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    # Disjoint pages — no id appears in both.
    assert {f.id for f in page1}.isdisjoint({f.id for f in page2})


def test_stats_totals_breakdowns_and_top_spenders(engine):
    insert_filing(engine, _make_filing("l-1", state="WI", filer_role="lobbyist"))
    insert_filing(engine, _make_client_filing("c-1", "DoorDash", 2_000_000.0))
    insert_filing(engine, _make_client_filing("c-2", "Acme Corp", 500_000.0))

    result = stats(engine)

    assert result["total"] == 3
    assert result["by_state"]["WI"] == 3
    assert result["by_filer_role"]["client"] == 2
    assert result["by_filer_role"]["lobbyist"] == 1
    # Ranked by summed total_expenditure, descending; lobbyist (no spend) excluded.
    assert result["top_spenders"][0] == {"name": "DoorDash", "total_expenditure": 2_000_000.0}
    assert [s["name"] for s in result["top_spenders"]] == ["DoorDash", "Acme Corp"]

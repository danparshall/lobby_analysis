"""Behavior tests for src/lobby_analysis/backend/api.py.

Uses FastAPI's TestClient with the `get_engine` dependency overridden to
point at an in-memory SQLite engine, so each test starts with a clean DB.
"""

import pytest
from fastapi.testclient import TestClient

from lobby_analysis.backend.api import app, get_engine
from lobby_analysis.backend.storage import init_engine
from lobby_analysis.models.entities import Person
from lobby_analysis.models.filings import LobbyingFiling


@pytest.fixture
def client():
    test_engine = init_engine(":memory:")
    app.dependency_overrides[get_engine] = lambda: test_engine
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _filing_dict(id: str, state: str = "OH", filer_name: str = "Test Lobbyist") -> dict:
    filing = LobbyingFiling(
        id=id,
        state=state,
        filing_type="activity_report",
        filer_role="lobbyist",
        filer_person=Person(id=f"p-{id}", name=filer_name, source_state=state),
    )
    return filing.model_dump(mode="json")


def test_post_then_get_roundtrip(client):
    r = client.post("/filings", json=_filing_dict("api-1"))
    assert r.status_code == 201

    r = client.get("/filings/api-1")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "api-1"
    assert body["state"] == "OH"


def test_get_404_for_unknown_id(client):
    r = client.get("/filings/no-such")
    assert r.status_code == 404


def test_list_filters_by_state(client):
    client.post("/filings", json=_filing_dict("oh-1", state="OH"))
    client.post("/filings", json=_filing_dict("ca-1", state="CA"))

    r = client.get("/filings", params={"state": "OH"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == "oh-1"


def test_list_unfiltered_returns_all(client):
    client.post("/filings", json=_filing_dict("f-1"))
    client.post("/filings", json=_filing_dict("f-2"))

    r = client.get("/filings")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_search_by_filer_name(client):
    client.post("/filings", json=_filing_dict("f-1", filer_name="Nathan Aichele"))
    client.post("/filings", json=_filing_dict("f-2", filer_name="Mike Abrams"))

    r = client.get("/search", params={"q": "Aich"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == "f-1"

"""FastAPI surface over the backend storage layer.

Endpoints:
    GET  /filings              List filings (filters: state, filer_role, limit).
    GET  /filings/{id}         Fetch one filing by id.
    POST /filings              Ingest one LobbyingFiling JSON body.
    GET  /search?q=...         Substring match on filer name.

Storage engine is injected via the `get_engine` dependency so tests can swap
in an in-memory SQLite engine without touching module state.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.engine import Engine

from lobby_analysis.backend.storage import (
    get_filing,
    init_engine,
    insert_filing,
    list_filings,
    search_filings,
)
from lobby_analysis.models.filings import LobbyingFiling

DEFAULT_DB = os.environ.get("BACKEND_DB", "data/backend/prototype.db")

app = FastAPI(title="Lobby Analysis Backend", version="0.1")

_engine: Engine | None = None


def get_engine() -> Engine:
    """Lazy-init the storage engine on first request; cached thereafter."""
    global _engine
    if _engine is None:
        _engine = init_engine(DEFAULT_DB)
    return _engine


@app.get("/filings", response_model=list[LobbyingFiling])
def list_filings_endpoint(
    state: str | None = None,
    filer_role: str | None = None,
    limit: int = 100,
    engine: Engine = Depends(get_engine),
) -> list[LobbyingFiling]:
    return list_filings(engine, state=state, filer_role=filer_role, limit=limit)


@app.get("/filings/{id}", response_model=LobbyingFiling)
def get_filing_endpoint(
    id: str,
    engine: Engine = Depends(get_engine),
) -> LobbyingFiling:
    filing = get_filing(engine, id)
    if filing is None:
        raise HTTPException(status_code=404, detail=f"no filing with id {id!r}")
    return filing


@app.post("/filings", status_code=201)
def post_filing_endpoint(
    filing: LobbyingFiling,
    engine: Engine = Depends(get_engine),
) -> dict[str, str]:
    inserted_id = insert_filing(engine, filing)
    return {"id": inserted_id}


@app.get("/search", response_model=list[LobbyingFiling])
def search_endpoint(
    q: str,
    limit: int = 100,
    engine: Engine = Depends(get_engine),
) -> list[LobbyingFiling]:
    return search_filings(engine, q, limit=limit)

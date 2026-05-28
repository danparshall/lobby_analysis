# Backend v0 Implementation Plan

**Date:** 2026-05-28
**Branch:** backend-prototype
**Originating brainstorm:** this session's chat (captured via `finish-convo` at end-of-session)

## Goal

Smallest viable end-to-end backend: persist a `LobbyingFiling` to SQLite, return it via HTTP, demonstrable via curl. Target: working in a few days.

## Cut list (deferred for prototype)

Postgres/Neon · pgvector / pg_trgm / FTS · R2 storage · GraphQL / Strawberry · MCP server · Django admin · confidence routing · Postgres work queue · entity resolution · 6-stage pipeline scaffolding · cloud deployment · async SQLAlchemy.

Each of these earns reconsideration once its absence becomes painful, not before.

## Stack

SQLite + SQLAlchemy 2.0 (sync) + FastAPI + Pydantic (`LobbyingFiling` already exists in `src/lobby_analysis/models/filings.py`) + pytest + httpx (TestClient).

## Layout

```
src/lobby_analysis/backend/
├── __init__.py
├── storage.py      # CRUD: insert_filing, get_filing, list_filings, search_filings
├── api.py          # FastAPI: GET /filings, GET /filings/{id}, POST /filings, GET /search
├── cli.py          # subcommands: ingest <json>, list, get <id>
└── __main__.py     # python -m lobby_analysis.backend <subcommand>

tests/
├── test_backend_storage.py
├── test_backend_cli.py
└── test_backend_api.py
```

DB file: `data/backend/prototype.db` (gitignored under existing `data/*` rule).

## Tasks (TDD red → green per phase)

**Phase 0 — setup**

1. Add `fastapi`, `sqlalchemy>=2`, `httpx` to `pyproject.toml`. Run `uv sync --extra dev`.
2. Verify `data/backend/` is gitignored (existing `data/*` + `!data/compendium/` rule should cover it; if not, append `data/backend/`).
3. Create empty `src/lobby_analysis/backend/__init__.py`.

**Phase 1 — Storage**

4. `tests/test_backend_storage.py` with three failing tests:
   - `test_insert_and_get_roundtrip` — insert a `LobbyingFiling`, fetch by id, deep-equal.
   - `test_list_filters_by_state` — insert 2 filings (OH + CA), `list_filings(state="OH")` returns 1.
   - `test_search_by_filer_name` — insert filing with filer "Aichele", `search_filings("Aich")` returns it.
5. Implement `storage.py`:
   - `init_engine(db_path) -> Engine` (creates table if missing).
   - `insert_filing(engine, filing: LobbyingFiling) -> str` (returns id).
   - `get_filing(engine, id) -> LobbyingFiling | None`.
   - `list_filings(engine, state=None, filer_role=None, limit=100) -> list[LobbyingFiling]`.
   - `search_filings(engine, q, limit=100) -> list[LobbyingFiling]` (LIKE on filer_name).
6. Tests green.

**Phase 2 — CLI**

7. `tests/test_backend_cli.py` with failing test: `main(["ingest", "<tmp.json>"])` lands a filing in a temp DB.
8. Implement `cli.py` + `__main__.py` — argparse, three subcommands.
9. Tests green.

**Phase 3 — API**

10. `tests/test_backend_api.py` with failing tests for the 4 endpoints via httpx `TestClient`.
11. Implement `api.py`.
12. Tests green.

**Phase 4 — Demo**

13. Add a small fixture `tests/fixtures/backend/sample_filing.json` (hand-constructed `LobbyingFiling` shape — OH Aichele AER scaled-down; doesn't depend on the live LLM extraction).
14. Run end-to-end: `python -m lobby_analysis.backend ingest tests/fixtures/backend/sample_filing.json && uvicorn lobby_analysis.backend.api:app` + curl screenshot in `results/20260528_v0_demo.md`.

**Phase 5 — Wrap**

15. Append session entry to `RESEARCH_LOG.md`; one-liner to `STATUS.md` Recent Sessions.
16. Commit, push, set upstream to `origin/backend-prototype`.

## Definition of done

- All new tests pass; no regressions in the existing suite.
- One filing ingested via CLI, retrievable via `curl localhost:8000/filings/{id}` returning structured JSON.
- Demo doc in `results/`.
- Branch pushed to origin.

## Edge cases (acknowledged, deferred)

- Concurrent writes — SQLite is single-writer; fine at prototype scale.
- Schema migrations — none yet; first migration cost paid when the schema changes.
- Auth — none; prototype runs locally only.
- Large payloads — none expected; `LobbyingFiling` JSON is small (KB).

## Open at plan-time

- API contract shape: mirror `LobbyingFiling` 1:1 (chosen for v0) vs flatter "filing view" model (deferred). Reconsider when real query patterns harden.
- Test DB strategy: in-memory SQLite via `sqlite:///:memory:` per test (chosen). Temp-file fixtures deferred unless we hit fixture-isolation pain.
- Fixture filing source: hand-constructed (chosen — keeps tests deterministic; doesn't block on LLM extraction completing). The real Dan-produced OH extract can replace it later.

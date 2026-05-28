# Research Log: backend-prototype

Created: 2026-05-28
Owner: Amina Rakhimbergenova
Track: Backend prototype — store + query + simple interface

## Purpose

Stand up a working backend prototype for the state lobbying data infrastructure, picking up from Gowrav Mannem's [`docs/active/ARCHITECTURE.md`](../ARCHITECTURE.md) (the 356-line backend system design he shipped on 2026-04-25 before stepping away from the project).

The goal is the **smallest viable end-to-end backend** that can:

1. Persist extracted `LobbyingFiling` records to durable storage,
2. Return them via a simple HTTP interface,
3. Be demonstrable in a curl session within a few days.

This is **not** an attempt to implement Gowrav's full spec. Several pieces are deferred for the prototype (see the kickoff convo when it lands). Once the prototype works end-to-end on one filing, we incrementally layer additional pieces (Postgres, GraphQL, MCP server, multi-stage pipeline) only as their absence becomes painful.

This branch is the **infrastructure counterpart** to Track B's per-state extraction work (`oh-portal-extraction`). Track B produces `LobbyingFiling` JSON records; this branch is where those records go to live and be queried.

## Sessions

(Newest entries first.)

### 2026-05-28 — Branch kickoff + v0 shipped end-to-end

- Cut `backend-prototype` worktree off `origin/main` (`9b189d2`).
- In-session brainstorm locked the v0 cut-list (defer Postgres / GraphQL / MCP / 6-stage pipeline / cloud deploy) and the v0 slice (SQLite + FastAPI + CLI, 4 endpoints).
- Drafted [`plans/20260528_v0_implementation.md`](plans/20260528_v0_implementation.md) — TDD-shaped, 5 phases.
- Phase 0: added `fastapi`, `sqlalchemy>=2`, `httpx`, `uvicorn` to `pyproject.toml`; `src/lobby_analysis/backend/` package created.
- Phase 1 (Storage TDD): 6/6 tests green. `storage.py` exposes `init_engine`, `insert_filing`, `get_filing`, `list_filings`, `search_filings` over a single `filings` table holding the full pydantic-serialized JSON plus a few denormalized indexed columns. `StaticPool` patch added for in-memory testing across multiple SQLAlchemy connections.
- Phase 2 (CLI TDD): 4/4 tests green. `python -m lobby_analysis.backend {ingest,get,list}` subcommands.
- Phase 3 (API TDD): 5/5 tests green. FastAPI app with `GET /filings`, `GET /filings/{id}`, `POST /filings`, `GET /search?q=`, using a `get_engine` dependency overridable in tests.
- Phase 4 (Demo): hand-crafted `tests/fixtures/backend/oh_aichele_sample.json` (4 bills, $20 Section II.D aggregate) ingested via CLI; uvicorn served the API on port 8765; curl roundtrip on all 4 endpoints verified against the fixture. Captured in [`results/20260528_v0_demo.md`](results/20260528_v0_demo.md).
- Surfaced macOS-specific root cause for the long-running editable-install corruption (UF_HIDDEN flag on `.pth` files; Python 3.12+ silently skips hidden `.pth` files). Local to this machine, not the repo; surgical workaround `PYTHONPATH=src .venv/bin/python -m ...` for all invocations. Saved to user memory.

## Plans

- [`20260528_v0_implementation.md`](plans/20260528_v0_implementation.md) — v0 backend: SQLite + FastAPI + CLI; 5 TDD phases.

## Convos

(Convo summary for this session lands via `finish-convo` at end-of-session.)

## Results

- [`20260528_v0_demo.md`](results/20260528_v0_demo.md) — End-to-end demo: fixture filing ingested via CLI, served via uvicorn, curl-verified on all 4 endpoints.

## Open questions

- `(agent, employer)` filing tuple schema gap surfaced again — the OH fixture sets both `filer_person` (Aichele) AND `filer_organization` (ARC Gaming), which the v1.x `LobbyingFiling` docstring discourages. Same gap pre-flagged on `oh-portal-extraction`; needs v1.4 conversation.
- API contract: mirror `LobbyingFiling` 1:1 (chosen for v0) vs flatter "filing-view" model — revisit when real query patterns surface.
- macOS `.pth` hidden-flag root cause on this machine (some local tool sets the flag on uv/virtualenv-created files). Investigation deferred — workaround is fine for now.

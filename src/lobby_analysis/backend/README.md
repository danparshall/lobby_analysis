# Backend prototype — API + frontend

A minimal end-to-end prototype for the state lobbying data infrastructure:
persist `LobbyingFiling` records in Postgres, serve them over HTTP, and browse
them in a small React UI.

This is the deliberately-simplified slice of Gowrav's `docs/active/ARCHITECTURE.md`
(REST instead of GraphQL, local Postgres instead of Neon, no MCP / 6-stage
pipeline). It exists to be *demoable*, not complete.

## Components

- `storage.py` — Postgres-backed CRUD over a single `filings` table (full
  pydantic JSON in `payload`, plus denormalized indexed columns). Includes
  `stats()` aggregation (totals, per-state/role breakdowns, top spenders).
- `api.py` — FastAPI app: `GET /filings`, `GET /filings/{id}`, `POST /filings`,
  `GET /search?q=`, `GET /stats`. Serves the built frontend at `/` if present.
- `cli.py` — `python -m lobby_analysis.backend {ingest,get,list}`.
- `ingest_wi.py` — maps `releases/wi/` TSVs into `LobbyingFiling` records.
- `../../../frontend/` — Vite + React + TS single-page app (search, browse,
  filing detail, stats dashboard).

## Running the prototype

### 1. Start Postgres

```bash
docker compose up -d postgres      # postgres:16, creates lobby_dev + lobby_test
```

The container persists data in the `postgres_data` named volume. Connection
URL: `postgresql+psycopg://lobby:lobby@localhost:5432/lobby_dev`.

### 2. Load data (once)

```bash
PYTHONPATH=src .venv/bin/python scripts/reingest_wi_postgres.py
```

Re-ingests the WI release (~4,800 filings in ~13s) and prints invariant checks
(DoorDash YTD should total $2,183,623.40).

### 3. Run the API

```bash
DATABASE_URL='postgresql+psycopg://lobby:lobby@localhost:5432/lobby_dev' \
  PYTHONPATH=src .venv/bin/python -m uvicorn lobby_analysis.backend.api:app --port 8765
```

### 4. Run the frontend

**Dev (hot reload):** the Vite server proxies API paths to `:8765`.

```bash
cd frontend && npm install && npm run dev      # http://localhost:5173
```

**Single-process demo:** build the frontend, then the API serves it at `/`.

```bash
cd frontend && npm run build                   # produces frontend/dist/
# restart uvicorn (step 3) → open http://localhost:8765
```

## Tests

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_backend_*.py -q
```

Tests connect to `lobby_test` (override with `TEST_DATABASE_URL`); each test is
isolated by a `TRUNCATE` in `tests/conftest.py`.

## Notes

- If `docker` CLI commands hang but the container is up, the API and tests can
  still reach Postgres directly on `localhost:5432` (the data plane is
  independent of the wedged control plane).

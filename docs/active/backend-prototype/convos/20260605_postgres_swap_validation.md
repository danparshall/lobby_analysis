# Postgres Swap Validation + Merge with Main

**Date:** 2026-06-05 (code written 2026-06-02, validated 2026-06-04/05)
**Branch:** backend-prototype

## Summary

The v0 backend's planned SQLite → Postgres migration shipped and was validated
end-to-end. The swap code (storage rewrite, docker compose stack, shared pytest
fixtures, one-shot WI re-ingest script) was written in an undocumented 2026-06-02
session; the long-running blocker was having no local Postgres to run it
against. That resolved this session by installing Docker Desktop, after which
the entire validation pass — tests, real-data re-ingest, live API checks —
succeeded without code changes.

The branch was then brought up to date with `origin/main` (Dan's compendium-2.0
/ WI-arc month of work, through `28f3e47`) so a later PR merge is clean. Three
conflicts (`pyproject.toml`, `uv.lock`, `STATUS.md`) resolved by union /
re-lock / keep-both-narratives respectively.

## Topics Explored

- `docker compose up -d postgres` (postgres:16) with `lobby_dev` +
  `lobby_test` databases created via `docker/postgres/init.sql`
- Test isolation model: session-scoped engine on `lobby_test`, autouse
  `TRUNCATE` per test (`tests/conftest.py`)
- Lossless-ingest invariants carried over from the SQLite run as the
  acceptance gate
- Merge hygiene for a long-lived branch against a fast-moving main

## Provisional Findings

- **All SQLite-run invariants reproduced exactly on Postgres:** 4,798 filings
  (1,706 client + 3,092 lobbyist), 944 orgs / 773 persons, DoorDash YTD
  **$2,183,623.40** via `/search`. Re-ingest wall time 12.55s (vs 3.1s on
  SQLite — per-insert commits over a real connection; acceptable for a
  one-shot script, batching is an option if it ever matters).
- All six curl checks pass against the live Postgres-backed API: list,
  state+role filter (1,706), name search, fetch-by-id (200), unknown id (404).
- 20/20 backend tests green against real Postgres, both before and after the
  main merge.
- `uv sync` after a lockfile merge drops dev extras — use `uv sync --extra dev`
  to keep pytest/ruff installed.
- A separate local-environment slowness issue surfaced during validation; it
  was diagnosed to be machine-specific (not the repo, not Postgres) and is
  tracked privately.

## Decisions Made

- Postgres is now the storage backend on this branch; SQLite path removed
  rather than kept behind a flag (YAGNI).
- `lobby-postgres` container left running as the local dev database
  (named volume `postgres_data` persists across restarts).
- Merged `origin/main` (`28f3e47`) into the branch — main's tip is now an
  ancestor, so the future PR merge is conflict-free.

## Results

- Validation evidence is inline above (test counts, invariants, curl checks);
  no separate results file — the re-ingest script
  (`scripts/reingest_wi_postgres.py`) reproduces the numbers on demand.

## Open Questions

- The four v1.4 schema gaps from the 2026-05-28 session remain open (hours
  fields, bill_efforts→filing join, authorizations→LobbyistRegistration,
  agent/employer tuple).
- Richer search (FTS on payload / bill-number search) vs. another state's
  release as the next slice — undecided.
- Postgres-specific opportunities not yet taken: JSONB payload column +
  GIN index (payload is currently `Text`), connection pooling for the API.

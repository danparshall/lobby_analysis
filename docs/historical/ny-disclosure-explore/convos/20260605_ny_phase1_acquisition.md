# NY Phase 1 — bulk-CSV acquisition layer

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Picked up the NY pipeline at the Phase 0 → Phase 1 handoff. Phase 0 (schema
verification) was already done and the no-allocation architecture locked, so
this session implemented **Phase 1 (acquisition)** from
[`plans/ny_disclosure_pipeline.md`](../plans/ny_disclosure_pipeline.md) test-first.

Before writing code, ran the full `pytest` baseline the plan mandates: **1636
passed, 3 failed**. The 3 failures were diagnosed as out-of-scope and not
introduced by this branch — all in `tests/test_pipeline.py` (the `scoring`
module already on `main`), failing `FileNotFoundError` because
`SNAPSHOT_DATE_DEFAULT = "2026-04-13"` is pinned but the only CA portal snapshot
in `data/` on this machine is `2026-05-01`. Left the `scoring` module untouched
(multi-committer hygiene) and captured the drift as a tracked task instead.

Implemented the acquisition layer (`io/ny/acquire.py`): a streaming bulk-CSV
downloader (the Phase-0-mandated primary path, since NY is denormalized ~1,300×
and can't be API-paginated) plus a thin Socrata JSON probe client for cheap
aggregate checks. Reused WI's *flow* and mock conventions without cloning its
HTML-scraper internals — NY's needs (streaming download, atomic rename) are
genuinely different.

## Topics Explored

- Phase 0 findings, plan, RESEARCH_LOG, GH #37 (pre-flight catch-up).
- `pytest` baseline triage — isolating the 3 `scoring` failures to data-version drift.
- WI `io/wi` fetcher conventions (`_FakeSession` transport-boundary mocking, typed
  errors, resume/checkpoint) as the pattern to adapt — not clone — for NY.

## Provisional Findings

- The repo's clean-baseline green count on this machine is **1636**, not the
  ~1550 the plan estimated; the 3 red tests are environmental (local `data/`
  snapshot state), likely passing in CI.
- A streaming bulk download with atomic `.part`-then-rename is the right shape
  for the resume/idempotency discipline the repo's Experiment Data Integrity
  rules require — an interrupted pull leaves no file a later resume treats as complete.

## Decisions Made

- **3 `scoring` baseline failures:** opened a tracked `task` issue for the
  module owner rather than fixing in this branch (Dan's call: option b). See
  Captured Tasks below.
- **Stop at the Phase 1 checkpoint** — did not proceed into Phase 2 this session.
- Acquisition API shape: `download_bulk_csv()` (resume-skip, `force`, app-token,
  typed `NYAcquisitionError`, atomic rename) + `SocrataProbeClient` (SoQL
  passthrough, `from_env` reads `SOCRATA_APP_TOKEN`).

## Results

- No results/ artifacts this session (code + tests only).
- Commit `db64354` — `io/ny/acquire.py`, `io/ny/__init__.py`,
  `tests/test_ny_acquire.py` (10 TDD tests, all green). Pushed.

## Open Questions

- Phase 2 column-map design: Phase 0 flagged inconsistent column names across
  the 6 datasets (`type_of_lobbying_focus` vs `lobbying_focus_type`, etc.) — the
  per-dataset map is the first Phase 2 task.
- GH #37 (semiannual-vs-bimonthly double-count) still open; it's a pre-merge
  reconciliation check, addressed when Phase 2/3 actually combine the two datasets.

## Captured Tasks

- [#38: scoring: test_pipeline FileNotFoundError — CA snapshot date pin drift](https://github.com/danparshall/lobby_analysis/issues/38) — captured 2026-06-05

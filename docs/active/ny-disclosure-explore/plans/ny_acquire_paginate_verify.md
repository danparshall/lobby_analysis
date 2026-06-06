# NY acquisition: paginate + verify in the library — Implementation Plan

**Goal:** Lift the paginate-and-verify pull logic out of `scripts/ny_pull_2025.py` into a reusable, tested `io/ny/acquire` library function, and add a mandatory row-count verification guard, so any large NY Socrata pull succeeds *and* can never again silently truncate.

**Originating conversation:** [`convos/20260606_ny_parties_lobbied_mvp.md`](../convos/20260606_ny_parties_lobbied_mvp.md) (the "Acquisition bug" thread) + the 2026-06-06 follow-up where Dan chose this scope ("Harden + paginate in lib").

**Context:** A single streamed `/resource/<id>.csv` request for all ~11.2M rows **silently truncated at 7,577,810 rows** — Socrata's CSV export is chunked (no `Content-Length`), so a server-side cap/timeout is a clean EOF that `requests` reads as a complete body, and the file was renamed as done with no row-count check. The bug is latent in `download_resource_csv` (any large caller inherits it); only `ny_pull_2025.py` was fixed this session (script-level). The old 9-col pull (1.9 GB) was verified complete after the fact, so **no shipped artifact is affected** — this is purely forward-looking hardening.

**Confidence:** High. This exact bucket-and-verify logic already ran end-to-end this session at the script level and verified `11,200,080 == live count(*)`; this plan moves proven logic into the library under test.

**Architecture:** Partition the pull by a low-cardinality, numeric/orderable key (`form_submission_id` — 8,613 distinct for 2025) into contiguous value-range buckets of ≤~800k rows; pull each with a `BETWEEN lo AND hi` filter (a whole key value is never split, so no keyset/offset tie hazard); verify each bucket's on-disk record count against its expected count (from a group-by) with retry; concatenate and verify the total against live `count(*)`. Separately, add an opt-in `expected_count` guard to the existing single-request `download_resource_csv` so it too fails loudly on a short read.

**Branch:** `ny-disclosure-explore` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/ny-disclosure-explore`).

**Tech Stack:** Python 3.12, `requests` (mocked at the transport boundary in tests), `csv` (quote-aware counting), pytest, ruff.

---

## Why the obvious alternatives don't work (don't re-discover these)

- **`$order=:id` keyset paging** forces a full-table sort that **times out** on the 11.2M-row view (verified: `ReadTimeout` even on a 5-row request). Do not use `:id`.
- **Offset paging on `form_submission_id`** is unsafe: it is **non-unique** (one submission = up to 2.22M rows), so `$limit/$offset` over a non-total order can skip/duplicate at page boundaries.
- **Value-range bucketing on `form_submission_id`** is correct because each whole key value lands entirely in one bucket — no split, no ties. This is the approach.

## Existing code to read first

- `src/lobby_analysis/io/ny/acquire.py` — `download_resource_csv`, `_stream_to_dest`, `resource_csv_url`, `SocrataProbeClient`. The bug locus + the function to extend.
- `tests/test_ny_acquire.py` — the `_FakeSession` / `_FakeResponse` mock boundary (canned responses in order; records url/params/headers; `_FakeResponse` supports `iter_content` for CSV and `json` for probes). **All new tests use this same boundary.** The existing 10 tests MUST stay green.
- `scripts/ny_pull_2025.py` — the current script-level implementation to lift and then replace with a thin call. It already contains working `_bucketize`, `_count_records`, `_pull_bucket`, `_concat` — port these, don't reinvent.

---

## Proposed library API (in `io/ny/acquire.py`)

```
def download_resource_csv_partitioned(
    dataset_id, dest_path, session, *,
    select: str,
    partition_key: str,            # e.g. "form_submission_id"
    where: str | None = None,
    partition_target_rows: int = 800_000,
    retries: int = 5,
    parts_dir: Path | None = None, # default: dest_path.parent / ".parts"
    base_url=DATA_NY_BASE, app_token=None,
    chunk_size=DEFAULT_CHUNK_SIZE, timeout=300,
) -> Path
```
Plus two pure helpers (factor for unit testing): `_bucketize(value_counts, target_rows)` and `_count_csv_records(path)`. And an **opt-in guard** on the existing function: add `expected_count: int | None = None` to `download_resource_csv` — when set, after streaming, count records and raise `NYAcquisitionError` (cleaning up `.part`) if it doesn't match. Default `None` keeps current behavior + the 10 existing tests green.

---

## Testing Plan

All behavior tests mock `requests` at the `_FakeSession` boundary (canned responses returned in order) and assert on **behavior** — bytes on disk, exceptions raised, network NOT hit on resume — never "the mock was called".

**Unit (pure functions):**
- `_bucketize`: contiguous values group into buckets ≤ target; a single value exceeding target becomes its own bucket (`lo == hi`); per-bucket `expected` equals the sum of its values' counts; the union of buckets covers every value exactly once.
- `_count_csv_records`: returns data-row count excluding the header; **counts correctly when a quoted field contains an embedded newline and an embedded comma** (this is the exact reason `wc -l` undercounts — the test must encode a real embedded-newline row and assert the count is right).

**Behavior (mocked session):**
- **Guard, short read raises:** `download_resource_csv(..., expected_count=N)` where the fake CSV body has fewer than N records → raises `NYAcquisitionError`, and **no `dest` file is left** (`.part` cleaned).
- **Guard, exact read passes:** count matches → file written, returns dest.
- **Paginated happy path:** fake session returns, in order, a `count(*)` JSON, a group-by JSON (e.g. ids 1–5 with small counts summing to the count), then one CSV response per bucket → assert `dest` is the concatenation of all data rows with the header exactly once, its record count == the live count, and the function returns `dest`.
- **Per-bucket truncation then retry:** a bucket's first CSV response is short, its second is complete → assert it retries and the final file is complete (no missing rows).
- **Persistent truncation raises:** a bucket is short on every attempt → after `retries`, raises `NYAcquisitionError`; `dest` not written.
- **Resume-skip:** pre-create a checkpoint part file with the correct record count → assert that bucket is **not** re-requested (the fake session is never asked for it) and the final file is still complete.
- **Group-by/count mismatch raises:** `count(*)` ≠ sum(group-by counts) → raise (data shifting mid-pull), before any bucket pull.
- **Empty result:** `count(*) == 0` → header-only `dest`, verification `0 == 0` passes.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Steps (bite-sized, TDD)

1. Write the failing unit test for `_bucketize` (contiguous grouping + over-target singleton + expected sums + full coverage).
2. Write the failing unit test for `_count_csv_records` (incl. the embedded-newline/comma quoted field).
3. Write the failing guard tests for `download_resource_csv(expected_count=...)` (short → raise + no file; exact → file written).
4. Write the failing paginated-pull behavior tests (happy path, retry-then-succeed, persistent-fail-raises, resume-skip, group-by mismatch, empty).
5. Run the new tests; confirm they fail for the right reason (missing function / `expected_count` kwarg), not import/typo errors.
6. Implement `_bucketize` + `_count_csv_records` (port from `scripts/ny_pull_2025.py`). Run unit tests → GREEN.
7. Implement the `expected_count` guard in `download_resource_csv` (count after stream, raise + unlink `.part` on mismatch). Run guard tests → GREEN; confirm the **10 existing acquire tests still pass**.
8. Implement `download_resource_csv_partitioned` (probe count(*), group-by partition_key, `_bucketize`, per-bucket pull-to-checkpoint with verify+retry, resume-skip, atomic concat, final verify). Run paginated tests → GREEN.
9. `ruff check` + `ruff format` the touched files.
10. Commit (`feat(ny-acquire): paginated + verified resource pull in the library`).
11. Re-point `scripts/ny_pull_2025.py` to call `download_resource_csv_partitioned` (thin caller — keep its logging/observability and the column list; delete the now-duplicated `_bucketize`/`_pull_bucket`/`_concat`/`_count_records`).
12. Manually re-run `uv run --active python scripts/ny_pull_2025.py` against live data to confirm it still VERIFIES `11,200,080 == live` (the data is already on disk; with resume-skip this should be fast or re-confirm cleanly). Commit.

---

**Testing Details:** Tests exercise real behavior at the transport mock boundary — the bytes assembled on disk, that a short read *raises* and leaves no file, that a truncated bucket is *retried* and the final file is complete, that a pre-existing checkpoint suppresses a network call (resume), and that quote-aware counting handles embedded newlines (the precise failure mode that made `wc -l` undercount). No test asserts only that a mock was called, and none tests datastructures or types.

**Implementation Details:**
- Port the proven helpers from `scripts/ny_pull_2025.py` verbatim where possible (they ran end-to-end this session); the lift is mostly relocation + parameterization (`partition_key`, `partition_target_rows`).
- Concat drops each bucket file's first physical line (the per-bucket header) — safe because the SODA CSV header never contains an embedded newline. Write one header (from `select`) at the top of `dest`.
- Per-bucket `$limit` = `expected + slack`; a bucket returning **more** than expected is also a mismatch (data added mid-pull) → retry/raise, never silently accept extra.
- The group-by uses `$order = partition_key` (cheap/indexed) with `$limit` high enough for the distinct-value count (60000 for 2025's 8,613); **never `$order=:id`**.
- Keep the guard opt-in (`expected_count=None` default) so the existing 10 tests and any small-pull callers are unaffected.
- Checkpoints under `.parts/` make an interrupted pull resumable; they are gitignored regenerable scratch.

**What could change:**
- If a future dataset has a single partition-key value approaching the truncation threshold (~1.6 GB / a few M rows), that one bucket could itself truncate; per-bucket verify+retry will catch it (loud), but a sub-split (e.g. by `reporting_period`) may then be needed. Not required for `client_semiannual` (the 2.22M mega-id streamed fine).
- Generalizing `partition_key` to other NY datasets (`lobbyist_bimonthly`, …) may need a different key; document the contract (numeric/orderable, low-cardinality enough to group in one aggregate request) rather than over-generalize now (YAGNI).

**Questions:**
1. Guard scope: keep `expected_count` **opt-in** (recommended — preserves existing behavior/tests), or make verification mandatory for every `download_resource_csv` call (would require passing an expected count everywhere + updating the 10 tests)?
2. Should `download_resource_csv_partitioned` probe `count(*)` itself (current assumption) or accept an injected expected total for callers that already have it? (Self-probing is simpler and matches the script; injection is one fewer request.)
3. Worth a tiny integration smoke that runs the partitioned pull against a 2-bucket *synthetic* fixture server, beyond the mocked tests? (Probably no — the mocked behavior tests + the live script re-run in step 12 cover it.)

---

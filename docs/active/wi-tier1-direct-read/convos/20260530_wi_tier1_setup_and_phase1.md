# WI Tier-1 direct-read — branch setup + Phase 1 (state-keying fix)

**Session:** 2026-05-30 → 2026-06-01 (UTC) · machine: `Dans-MacBook-Pro`
**Branch:** `wi-tier1-direct-read` (off `origin/main` @ `9b3de44`)
**Plan:** `plans/20260530_wi_2025_tier1_direct_read.md`
**Status at checkpoint:** Phase 1 **done + verified**; Phase 2 (paid run) **deferred to a higher-disk machine**; Phase 3 pending the run.

## Goal

Extend the Tier-1 direct-read legal-axis extraction harness from the OH 2025 pilot to Wisconsin 2025 — but first generalize `scripts/tier_1_direct_read_legal_axis.py` so a new state cannot collide with, or resume-skip into, the OH pilot's outputs.

## Decisions this session

- **Q1 — branch:** new branch off `origin/main` (per handoff). Worktree at `.worktrees/wi-tier1-direct-read`, `data/` + `.env.local` symlinked to main.
- **Q2 — models:** **both** (`claude-opus-4-7` + `gpt-5.2-2025-12-11`), 36 dispatches, to mirror the OH pilot for a like-for-like cross-state sigma_noise comparison.
- **Q3 — CLI args:** `--state`/`--vintage` are **required (no default)** — closes the accidental-bare-invocation OH-re-run footgun. (Plan Step 7's "OH default" became "OH *passed explicitly* still resolves the original-style bundle path.")

## Phase 1 — what changed (TDD)

`scripts/tier_1_direct_read_legal_axis.py`:
- Removed module-level `_STATE_ABBR`, `_VINTAGE_YEAR`, `_STATUTE_BUNDLE_DIR`, `_RESULTS_DIR`.
- Added `parse_args()` (required `--state`, `--vintage`), `resolve_bundle_dir(state, vintage)`, `resolve_results_dir(state, vintage, results_base=None)`.
- **Correctness-critical fix:** results/checkpoint dir is now keyed `…/results/tier_1/<STATE>_<VINTAGE>/`. The base moved from the now-archived `extraction-harness-brainstorm` path to `docs/active/wi-tier1-direct-read/results/tier_1/`.
- Threaded `bundle_dir`/`results_dir`/`state`/`vintage` through `_preflight`, `main(argv=None)`, and `_compute_and_print_agreement`. `dispatch_result_path` / `is_dispatch_done` signatures unchanged (already took `results_dir`).

`tests/test_tier_1_state_keying.py` (new, 6 tests, written first, watched fail):
- results dir is `<STATE>_<VINTAGE>`-keyed (WI ≠ OH; also vintage-keyed);
- resume isolation — only-OH-files-on-disk ⇒ WI dispatch not "done";
- CLI args thread into bundle (`…/WI/2025/sections`) + results (`WI_2025`) paths;
- `--state`/`--vintage` required (bare / partial invocation → `SystemExit`);
- OH passed explicitly still resolves `…/statutes/OH/2025/sections`.

## Verification (no API spend)

- New + existing Tier-1 tests: **34 passed**.
- Full suite: **1547 passed**, 3 skipped, 3 xfailed, **3 failed**.
- `ruff check` on changed files: clean.
- Dry-run path/roster check (`--state WI --vintage 2025`): bundle exists (16 `.txt`), results dir `…/WI_2025`, all 6 chunks present = **84 legal cells**, both models, **36 planned dispatches**.

## Pre-existing failures (NOT caused here — flagged for Dan)

`tests/test_pipeline.py` (3 failures): `load_snapshot("CA")` wants `data/portal_snapshots/CA/2026-04-13/manifest.json`, but on-disk is `…/CA/2026-05-01/`. The test's `SNAPSHOT_DATE_DEFAULT` (`2026-04-13`) lags the local snapshot date. These are Prong-2 portal data, orthogonal to Tier-1 statute work, and present on `origin/main`. **Not fixed** — bumping a shared global default date is a multi-committer change that could break CI if CI provisions the 2026-04-13 snapshot. Dan to decide.

## Disk / ENOSPC (why Phase 2 was deferred)

This machine's volume sat at ~98–99% (8.5–9.7 GiB free, oscillating) and intermittently hit **0 free mid-write**, throwing recurring ENOSPC that truncated command output (the session temp dir itself was empty — it's the volume, not the temp dir). The risk for a paid 36-dispatch run: a checkpoint JSON written during a 0-free window becomes corrupt-but-present, which the resume logic would then **skip** rather than re-dispatch, silently polluting sigma_noise. Dan's call: **push state + handoff, run Phase 2 on a machine with more disk.** Work-around used this session for visibility: redirect command output to a file, read it back.

## Known minor item

`_ORIGINATING_CONVO` still points at the OH Tier-0 convo (`convos/20260520_tier_0_direct_read_execution.md`) — it documents the harness's method lineage and is stamped into every result's provenance alongside the correct `state_abbr`/`vintage_year`. Left as-is (out of scope); update post-hoc if a WI-specific provenance pointer is wanted.

## Next

See `HANDOFF.md` for the exact Phase 2 run procedure on the target machine.

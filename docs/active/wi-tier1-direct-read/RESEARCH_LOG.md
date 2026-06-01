# Research Log: wi-tier1-direct-read

Created: 2026-05-30
Purpose: Extend the Tier-1 direct-read legal-axis extraction harness from the OH 2025 pilot to Wisconsin 2025 — but first generalize the script so a new state cannot collide with or resume-skip into the OH results (state-key the results/checkpoint paths).

Plan: `plans/20260530_wi_2025_tier1_direct_read.md`

---

## Session history (newest first)

### 2026-06-01 (later) — followups handoff written; MI substitutes for NC
Doc: `HANDOFF_followups.md`
- Two concrete pre-MI investigations captured: (1) Fix A int→Decimal regression on dict-shape value path, (2) `TimeThresholdCell.unit` literal-enum gap for v2.2 design ledger.
- Decision: **next state is MI, not NC.** Carried into STATUS row + the followups doc.
- Issue #31 (dispatch loop parallelization) noted as independent, can be done in parallel with 1/2 or with MI extraction.

### 2026-06-01 — Phase 2 (paid run) DONE on Air; Phase 3 written up
Convo: `convos/20260601_wi_tier1_phase2_run.md`
- Pre-flight: recreated `.env.local` from `.env.corporate` (lost in laptop data-loss); symlink chain wi-tier1 → compendium-source-extracts → main resolves. Tests 34/34, dry-run probe matches HANDOFF reference (6 chunks / 84 cells / 36 dispatches).
- **Run: 36/36 dispatched, 0 skipped, 0 dispatch failures, 20 min wall.** Total cost **$2.5708** (HANDOFF predicted $2-4; all 36 well under $1/call ceiling). Integrity check: 36 files / `corrupt: []` / file-cost sum matches log session_cost exactly.
- **σ_noise:** Claude **85.71%** (= OH 85.7%, state-invariant), GPT-5.2 **84.52%** (vs OH 73.8%, **+10.7 pts**). GPT's `scoreability_unstable` rose 2→7 — different failure mode than value-drift, worth metric segmentation.
- **Load-bearing structural finding:** both models, every single run (6/6) failed `lobbyist_registration_threshold_time_percent` instantiation on WI §13.62(11)'s 5-days-per-reporting-period lobbyist gate. Two distinct schema problems: (a) `magnitude: int=5` rejected — Fix A int→Decimal coercion (claimed-fixed on archived `extraction-harness-brainstorm` Tier-2 Step D) appears to NOT apply to this dict-shape value path — possible regression; (b) `TimeThresholdCell.unit` literal-enum has no `days_per_reporting_period` — schema can't represent WI's time threshold structure. Both findings are concrete v2.2 inputs.
- Captured GH issue [#31](https://github.com/danparshall/lobby_analysis/issues/31) for the embarrassingly-parallel dispatch loop (~15-20× wall-time speedup on the table).
- Next: investigate Fix A regression; capture TimeThresholdCell unit gap; decide whether to extend to NC.

### 2026-05-30 → 06-01 — branch created, Phase 1 DONE; Phase 2 deferred (disk)
Convo: `convos/20260530_wi_tier1_setup_and_phase1.md` · Handoff: `HANDOFF.md`
- Branched off `origin/main` (9b3de44) into `.worktrees/wi-tier1-direct-read`.
- Decisions (handoff + user): new branch off main (Q1); **both models** opus-4-7 + gpt-5.2 (Q2, mirror OH); **required** `--state`/`--vintage` args (Q3, closes accidental-OH-re-run footgun).
- **Phase 1 complete (TDD):** `scripts/tier_1_direct_read_legal_axis.py` parameterized by `--state`/`--vintage`; results/checkpoint dir state-keyed `…/results/tier_1/<STATE>_<VINTAGE>/`. New `tests/test_tier_1_state_keying.py` (6 tests). Verified: 34 Tier-1 tests pass; ruff clean; dry-run confirms WI bundle (16 txt), 6 chunks / 84 legal cells, 36 planned dispatches.
- **Also fixed (commit `a3bc1af`, on Dan's instruction):** bumped `SNAPSHOT_DATE_DEFAULT` 2026-04-13 → 2026-05-01 — the 04-13 portal snapshots were lost in the laptop data-loss event and re-fetched as 05-01 across all 8 states. Resolved 3 pre-existing `test_pipeline.py` failures; **full suite now 1550 pass / 0 fail**.
- **Phase 2 (paid 36-dispatch run) deferred:** this machine at 98–99% disk threw recurring ENOSPC (volume hitting 0-free mid-write). User will run Phase 2 on a higher-disk machine per `HANDOFF.md`.
- **Phase 3** pending the run.

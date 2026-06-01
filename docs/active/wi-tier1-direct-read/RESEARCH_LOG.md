# Research Log: wi-tier1-direct-read

Created: 2026-05-30
Purpose: Extend the Tier-1 direct-read legal-axis extraction harness from the OH 2025 pilot to Wisconsin 2025 — but first generalize the script so a new state cannot collide with or resume-skip into the OH results (state-key the results/checkpoint paths).

Plan: `plans/20260530_wi_2025_tier1_direct_read.md`

---

## Session history (newest first)

### 2026-05-30 → 06-01 — branch created, Phase 1 DONE; Phase 2 deferred (disk)
Convo: `convos/20260530_wi_tier1_setup_and_phase1.md` · Handoff: `HANDOFF.md`
- Branched off `origin/main` (9b3de44) into `.worktrees/wi-tier1-direct-read`.
- Decisions (handoff + user): new branch off main (Q1); **both models** opus-4-7 + gpt-5.2 (Q2, mirror OH); **required** `--state`/`--vintage` args (Q3, closes accidental-OH-re-run footgun).
- **Phase 1 complete (TDD):** `scripts/tier_1_direct_read_legal_axis.py` parameterized by `--state`/`--vintage`; results/checkpoint dir state-keyed `…/results/tier_1/<STATE>_<VINTAGE>/`. New `tests/test_tier_1_state_keying.py` (6 tests). Verified: 34 Tier-1 tests pass; ruff clean; dry-run confirms WI bundle (16 txt), 6 chunks / 84 legal cells, 36 planned dispatches.
- **Also fixed (commit `a3bc1af`, on Dan's instruction):** bumped `SNAPSHOT_DATE_DEFAULT` 2026-04-13 → 2026-05-01 — the 04-13 portal snapshots were lost in the laptop data-loss event and re-fetched as 05-01 across all 8 states. Resolved 3 pre-existing `test_pipeline.py` failures; **full suite now 1550 pass / 0 fail**.
- **Phase 2 (paid 36-dispatch run) deferred:** this machine at 98–99% disk threw recurring ENOSPC (volume hitting 0-free mid-write). User will run Phase 2 on a higher-disk machine per `HANDOFF.md`.
- **Phase 3** pending the run.

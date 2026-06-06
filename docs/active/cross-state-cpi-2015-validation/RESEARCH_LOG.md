# RESEARCH_LOG — cross-state-cpi-2015-validation

Newest entries first.

---

## 2026-06-05 — Branch cut off main; execution session opens

**Plan (inherited):** [`docs/historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`](../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md) (amended 2026-06-05 — 5 states × default-6-chunks × per-(state, indicator) de-jure exact-match).

**Originating convos (on the predecessor branch):**
- [`docs/historical/wi-ralph-cpi-renewal-cadence/convos/20260605_cross_state_planning.md`](../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_cross_state_planning.md) — original 10-state framing.
- [`docs/historical/wi-ralph-cpi-renewal-cadence/convos/20260605_pr40_pressure_test.md`](../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_pr40_pressure_test.md) — amendment to 5-state × default-6-chunks × de-jure-exact-match.
- [`docs/historical/wi-ralph-cpi-renewal-cadence/convos/20260605_phase_a_execution.md`](../../historical/wi-ralph-cpi-renewal-cadence/convos/20260605_phase_a_execution.md) — Phase A execution baseline (BinaryCell + EnumCell at scale on WI; A2.b dispatch shape; TDD discipline).

**Pre-execution checklist status (per plan §Pre-execution checklist):**
- [x] 1. Plan read end-to-end including §Amendment 2026-06-05 banner.
- [x] 2. Phase A execution convo read end-to-end.
- [x] 3. Both planning convos read (cross-state planning + PR 40 pressure-test amendment).
- [x] 4. CPI 2015 C11 projection mapping doc read end-to-end.
- [x] 5. `src/lobby_analysis/projections/cpi_2015_c11.py` read end-to-end — confirmed 6 de-jure helper APIs + `load_per_state_ground_truth()` signature.
- [x] 6. P1 (v2.1 + Phase A YAML on main at f97c73d), P2 (this branch + worktree cut + `data` and `.env.local` symlinked), P3 (dispatcher `_DEFAULT_CHUNKS` matches the 6 plan chunks 1:1), P4 (oracle CSV present) — all verified.
- [x] 7. TDD: RED → GREEN on `--results-base` CLI flag (3 new tests; 14/14 tier_1 tests pass). Audit script `scripts/cross_state_cpi_2015_audit.py` landed post-NY.
- [x] 8. Dispatch order: NY first as cost anchor → exceeded $2.50 threshold ($2.83) → Dan authorized envelope expansion to ~$15 → 4 parallel dispatches WI/OH/CA/TX landed cleanly.
- [x] 9. Audit run: Table A (30 per-cell verdicts) + Table B (5 per-state summaries) at [`results/20260605_cross_state_cpi_2015_validation.md`](results/20260605_cross_state_cpi_2015_validation.md).
- [x] 10. Finish-convo: convo at [`convos/20260605_cross_state_cpi_2015_validation_execution.md`](convos/20260605_cross_state_cpi_2015_validation_execution.md); STATUS updated; this RESEARCH_LOG updated; doc-link-graph walked.

**Execution session convo:** [`convos/20260605_cross_state_cpi_2015_validation_execution.md`](convos/20260605_cross_state_cpi_2015_validation_execution.md)
**Audit results:** [`results/20260605_cross_state_cpi_2015_validation.md`](results/20260605_cross_state_cpi_2015_validation.md)

**Headline:** 15 of 30 (50%) match per-(state, indicator) exact-match. **60% of the 15 misses are systematic projection-helper-vs-YAML-extraction vocabulary mismatches** on IND_199 (IntCell months vs string enum) + IND_207 (CPI's YES/MODERATE/NO vs internal structural enum), not extraction failures.

**Per-indicator match rate (across 5 states):**
- IND_196: 5/5 ✅ (cleanest cross-state signal)
- IND_197: 3/5 (WI + OH IND_197 errata candidate — extracted $0 threshold, oracle MODERATE)
- IND_199: 1/5 (vocab-mismatch on 4 of 5)
- IND_201: 2/5 (mix of value_unstable on OH/CA + over-projection on TX)
- IND_203: 4/5 (only OH misses)
- IND_207: 0/5 (vocab-mismatch on all 5)

**Per-state match rate:**
- NY 4/6 | WI 3/6 | OH 1/6 | CA 3/6 | TX 4/6

**Cost ledger ($14.4271 of $15 expanded envelope):**
- NY $2.8289 / WI $2.4825 / OH $3.7894 / CA $2.8428 / TX $2.4835
- 12 instantiation errors across 420 dispatches (2.9% — under the 5% pause threshold)
- σ_noise range: Claude 73.81% (TX) – 92.86% (OH); GPT 60.71% (TX) – 88.10% (NY/WI)

**Next-session highest-leverage move:** remediate IND_199 + IND_207 vocab-mismatch via projection-helper update (Open Q #1 option a in execution convo) — 9 of 15 misses collapse for $0 dispatch spend.

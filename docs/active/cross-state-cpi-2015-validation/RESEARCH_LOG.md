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
- [ ] 7. TDD: RED batch then GREEN batch (dispatch loop + audit script).
- [ ] 8. Dispatch order: NY first as cost anchor; pause-and-surface threshold at NY > $2.50.
- [ ] 9. Run X2 audit; populate Table A (30 per-cell verdicts) + Table B (5 per-state summaries); 1-sentence diagnosis per mismatch.
- [ ] 10. Finish-convo: walk doc-link-graph before commit.

**Branch shape note:** the dispatcher's `_DEFAULT_RESULTS_BASE` is hardcoded to `docs/active/wi-tier1-direct-read/results/tier_1/` (now archived). The plan calls for results under `docs/active/cross-state-cpi-2015-validation/results/tier_1/<STATE>_<VINTAGE>/`. `resolve_results_dir` already accepts a `results_base=` kwarg; only the CLI flag wiring needs adding. Tracked as the first TDD task this session.

**Cross-state envelope:** Fresh **$10** (per D6). ~$8 expected dispatched + ~$2 headroom for re-runs / one-off Ralph follow-ups.

**Dispatch order:** NY → WI → OH → CA → TX (D7).

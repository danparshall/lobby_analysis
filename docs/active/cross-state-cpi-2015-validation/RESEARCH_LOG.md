# RESEARCH_LOG — cross-state-cpi-2015-validation

Newest entries first.

---

## 2026-06-06 (later still) — Phase 2A executed (TimeThresholdCell escape hatch + row #5 promotion)

**Phase 2A EXECUTED** per [`plans/20260606_phase_2_schema_aware_prompt_hygiene.md`](plans/20260606_phase_2_schema_aware_prompt_hygiene.md) §Phase A. TDD: 4 RED tests landed first (3 `TimeThresholdCell.other_specification` behavior + 1 row #5 registry-membership assertion) → schema change in `src/lobby_analysis/models_v2/cells.py` (TimeThresholdCell gains `other_specification: Annotated[str, Field(max_length=500)] | None = None` + docstring updated to cover both rows; FloatCell docstring updated since no compendium row uses it post-2A) + TSV change in `compendium/disclosure_side_compendium_items_v2.1.tsv` (row #5 cell_type `typed Optional[float]` → `typed Optional[TimeThreshold]`; parser table already maps that string to TimeThresholdCell so no parser change) + FloatCell-coercion-test in `tests/test_tier_1_legal_axis.py` retargeted to a synthetic `CompendiumCellSpec` (since row #5 was the only FloatCell in the compendium) → 4 GREEN. Full pytest **1905 passed** (was 1901), 3 skipped, 3 xfailed unchanged. No model dispatches; $0 spend.

**Files touched:**
- `src/lobby_analysis/models_v2/cells.py` (TimeThresholdCell + FloatCell docstrings + field add)
- `compendium/disclosure_side_compendium_items_v2.1.tsv` (row #5)
- `tests/test_models_v2_cells.py` (+3 TimeThresholdCell.other_specification tests)
- `tests/test_tier_1_legal_axis.py` (FloatCell coercion refactor + row #5 TimeThresholdCell assertion)

**Next:** hand off to audit agent per [`plans/20260606_prompt_audit_all_questions.md`](plans/20260606_prompt_audit_all_questions.md). Phase 2B (7 lean-prompt rewrites) deferred to audit + execution agents per the Phase 2 plan's §Sequencing Update banner — the 7 drafts in §Phase B of the Phase 2 plan stay as worked-example reference drafts for the audit agent to compare its findings against. Phase 2C (legal-axis format-hint regression test) lands AFTER audit-driven prompt edits.

**Convo:** continues [`convos/20260606_phase_1_exec_and_de_jure_pivot.md`](convos/20260606_phase_1_exec_and_de_jure_pivot.md); Phase 2A is a same-day in-session execution from the handoff, no new convo file. Audit agent will open its own convo when it picks up.

---

## 2026-06-06 (later) — Phase 1 execution + Phase 2 redesign + de jure pivot

**Phase 1 EXECUTED** per [`plans/20260606_pre_dispatch_hygiene.md`](plans/20260606_pre_dispatch_hygiene.md) §Phase 1. TDD: 6 RED tests in `tests/projections/test_cpi_2015_c11_per_item.py` (IND_199 IntCell-months 0/6/12/24/36 paths; IND_207 CPI-enum YES/MODERATE/NO paths) → helper changes accepting both new YAML vocabularies + legacy string-enums → 6 GREEN; full pytest 1901 passed. Re-ran `scripts/cross_state_cpi_2015_audit.py` against Round 1 stored extractions: **19/30 (63.3%), up from 15/30 (50%)** — exactly the +4 cells the failure-mode doc Trend 1 predicted. Per-indicator deltas match prediction (IND_199 +3 NY/WI/OH/CA flip; IND_207 +1 NY's YES match; TX IND_199 flips from spurious-match to correct-mismatch). Committed as `cbcd3e2`; pushed.

**Post-fix audit captured:** [`results/20260606_round_1_post_phase_1_audit.md`](results/20260606_round_1_post_phase_1_audit.md) — Table A (per-cell) + Table B (per-state). Of the 11 remaining misses, 6 are Trend 5 (CPI more generous than extraction); 2 Trend 4 (TX sparse-corpus); 3 Trend 2/value-instability.

**Phase 2 redesigned around three corrections that surfaced mid-session:**
1. **Test/dispatch scope mismatch.** The dispatcher (`tier_1_direct_read_legal_axis.py`) filters to `axis == 'legal'`. The chunk-inventory's 11 underspecified prompts include 4 practical-axis ones not dispatched in this pipeline. Operational scope = 7 legal-axis prompts.
2. **Lean-prompt principle (Dan's framing).** "The agent doesn't need a long historical background... it just needs the actual friggin' question." Extraction stays granular; cross-rubric synthesis (e.g., HG Q13 OR-projection across reg-form-comp ∨ spending-report-comp) lives in projection helpers, not in the prompt.
3. **Schema asymmetry between rows #4 and #5.** Row #4 (`lobbyist_registration_threshold_time_percent`) uses TimeThresholdCell (magnitude+unit composite); row #5 (`lobbyist_filing_de_minimis_threshold_time_percent`) uses FloatCell (no unit slot) — same observable family, different cell types. Dan: states frame time thresholds variously (hours-per-week, days-per-session, %-of-time); forcing percent forces math-on-the-fly. Design: add `other_specification: str | None = None` escape hatch to TimeThresholdCell + promote row #5 from FloatCell to TimeThresholdCell.

**Two new plan docs landed (uncommitted on disk, finalized this session):**
- [`plans/20260606_phase_2_schema_aware_prompt_hygiene.md`](plans/20260606_phase_2_schema_aware_prompt_hygiene.md) — replaces Phase 2 of the prior plan. Three sub-phases: A (schema change + row #5 promotion + FloatCell-coercion-test refactor), B (7 lean prompt rewrites with Dan-review gate), C (legal-axis format-hint regression test).
- [`plans/20260606_prompt_audit_all_questions.md`](plans/20260606_prompt_audit_all_questions.md) — read-only audit agent produces ONE findings doc cataloging all ~131 legal-axis prompts (post-de-jure-pivot scope reduction); execution agents apply fixes in separate plans.

**Pedigree dig (n=8 example, `lobbyist_spending_report_includes_total_compensation`):** TSV `rubrics_reading` column tracks paper-level pedigree (8 papers); YAML `source_quotes:` only retained the pri_2010 quote. **50 multi-rubric TSV rows have only 1 YAML source quote.** Not Round-2-blocking under the lean-prompt principle (model only needs the actual question, not rubric chronology); deferred as Phase A pedigree-completeness pass.

**MAJOR ARCHITECTURAL DECISION (Dan, session end): combined-axis rows verboten henceforth. This research line is de jure only.** Reading statutes can answer "what does the law say" but not "what actually happens"; de facto is a separate research line entirely. The 3 remaining combined-axis rows (post-v2.1 Pattern C — `lobbyist_registration_required`, `lobbyist_registration_deadline_days_after_first_lobbying`, `lobbyist_spending_report_filing_cadence`) must be Pattern-C-split into single-axis pairs. The audit plan's HANDOFF UPDATE banner captures this for the next agent. The Phase 2 plan's §Risks wording about practical-axis "deferred until Prong 2" needs a small patch — flagged for the next agent.

**Round 2 reframing (Dan):** *"don't sweat Round 2... the whole point of doing a handful at a time is to stress-test our model against reality; we can make adjustments until we're properly capturing what's out there."* The original Phase 2 plan's σ_noise-comparability concern (Risk #1) is overcalibrated. Iterative model-vs-reality calibration is the design.

**Convo:** [`convos/20260606_phase_1_exec_and_de_jure_pivot.md`](convos/20260606_phase_1_exec_and_de_jure_pivot.md).

**Next-session candidates** (Dan's call):
- (a) Execute Phase 2 schema-aware plan (TDD; $0; ~75 min + Dan review gate).
- (b) Run the prompt audit on all questions (the audit agent must update the audit plan per the de jure handoff banner before executing; $0; ~3-4 hours).
- (c) Pattern-C split the 3 remaining combined-axis rows (new plan; precedent from v2.1; $0).
- (d) Phase 4 Round 2 dispatch CO/IL/WA/FL/NC at vintage 2015 (~$15; requires explicit Dan authorization; can proceed against current YAML or wait for Phase 2 application).

**Spend this session:** $0 (Phase 1 was code+test only; no model dispatches). Cross-state envelope unchanged at $14.43 of original $15 (now ~$18-25 effective ceiling after the Round 2 reframing).

---

## 2026-06-06 — Pre-dispatch review + hygiene plan

**Session shape:** review-and-plan, no dispatch. Triggered by Dan's "step back and review" pause before Day-2 5-state extension dispatch (per leave-behind-prep convo's 5-day plan). Two artifacts produced:

**Inventory report:** [`results/20260606_cpi_2015_c11_chunk_inventory.md`](results/20260606_cpi_2015_c11_chunk_inventory.md) — structural breakdown of the 6 default chunks. 93 cells: 84 de-jure / 9 de-facto; 78.5% BinaryCell, 21.5% structured (the structured-22% is where Round 1 vocab schism lived). Audited all 93 prompts; 11 (12%) lack explicit response-format clarification — listed in §4 with full text.

**Plan:** [`plans/20260606_pre_dispatch_hygiene.md`](plans/20260606_pre_dispatch_hygiene.md) — combined Paths (b) + (c) from the failure-mode doc: Phase 1 helper-side vocab fix for IND_199 + IND_207 ($0, ~30 min, expected Round 1 re-audit lift 50% → ~63%); Phase 2 prompt hygiene cleanup of the 11 underspecified prompts ($0, ~45 min, semantics-preserving); Phase 3 Round 1 re-audit checkpoint; Phase 4 Round 2 dispatch CO/IL/WA/FL/NC at vintage 2015 (~$15); Phase 5 N=10 writeup. Each phase has TDD discipline + acceptance gates; pre-execution checklist gates Phase 1 start.

**Convo:** [`convos/20260606_pre_dispatch_review.md`](convos/20260606_pre_dispatch_review.md).

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
**Audit results (data):** [`results/20260605_cross_state_cpi_2015_validation.md`](results/20260605_cross_state_cpi_2015_validation.md)
**Failure-mode trends + paths forward (analysis):** [`results/20260606_failure_mode_trends_and_paths_forward.md`](results/20260606_failure_mode_trends_and_paths_forward.md)

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

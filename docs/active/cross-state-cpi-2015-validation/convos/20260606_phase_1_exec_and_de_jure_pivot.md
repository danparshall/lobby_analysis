# Phase 1 execution + Phase 2 redesign + de jure pivot

**Date:** 2026-06-06
**Branch:** cross-state-cpi-2015-validation
**Worktree:** `.worktrees/cross-state-cpi-2015-validation`

## Summary

Session executed Phase 1 of the [`20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md) plan (helper-side vocab fix for IND_199 IntCell-months + IND_207 CPI-published-enum), confirmed the predicted Round 1 re-audit lift exactly (15/30 → **19/30**, +4 cells matching the failure-mode doc's Trend 1 prediction), then opened a Phase 2 redesign conversation that produced two new plan docs and one architectural decision.

The Phase 2 redesign started from an axis-filter scope check (the dispatcher only extracts legal-axis cells; only 7 of the 11 underspecified prompts are operationally relevant) and a lean-prompt principle (the YAML prompt should ask the actual question; cross-rubric synthesis lives in the projection layer, not in the prompt). Mid-redesign, Dan flagged a schema asymmetry between row #4 (`lobbyist_registration_threshold_time_percent`, TimeThresholdCell with magnitude+unit) and row #5 (`lobbyist_filing_de_minimis_threshold_time_percent`, FloatCell with no unit slot) — the kind of cell-type schism the failure-mode doc's Trend 6 anticipated. We designed an `other_specification` free-text escape hatch on TimeThresholdCell + a FloatCell → TimeThresholdCell promotion for row #5.

The session ended with a major architectural decision: **combined-axis rows are verboten henceforth. This research line is de jure only.** Reading statutes can answer "what does the law say" but not "what actually happens"; the de facto question is a separate research line. The 3 remaining combined-axis rows (post-v2.1 Pattern C) must be split into single-axis pairs following the v2.1 precedent. The audit plan's handoff banner captures this for the next agent.

## Topics Explored

- **Phase 1 execution (TDD).** Wrote 6 RED tests in `tests/projections/test_cpi_2015_c11_per_item.py` (IND_199 IntCell-months: 0/6/12/24/36 paths; IND_207 CPI-enum: YES/MODERATE/NO). Patched `project_ind_199` to accept IntCell + retain legacy string-enum fallback; patched `project_ind_207` to accept CPI vocab + retain legacy structural enum. All 1901 pytest tests green. Re-ran `scripts/cross_state_cpi_2015_audit.py` against Round 1 stored extractions; got 19/30 (63.3%), exactly the +4 prediction. Committed as `cbcd3e2`; pushed.

- **Phase 2 scope correction.** The plan's Phase 2 spec called for fixing 11 underspecified prompts; the chunk-inventory had counted both axes for combined-axis rows. The dispatcher (`scripts/tier_1_direct_read_legal_axis.py`) filters to `axis == 'legal'`, so only 7 of the 11 are operationally relevant. The 4 practical-axis cells would have required hybrid "for de-jure / for de-facto" prompts that have no operational pay-off.

- **Lean-prompt principle.** Dan's framing: *"the agent doesn't need a long historical background... it just needs the actual friggin' question."* The current prompts mostly carry a CPI rubric-quote preamble that's for human auditors, not the model. Cross-rubric synthesis (e.g., HG Q13's OR-projection across registration-form-comp ∨ spending-report-comp) belongs in projection helpers, not in the prompt — extraction stays granular, projection stays composable.

- **Pedigree audit.** TSV `rubrics_reading` column tracks paper-level pedigree (e.g., `cpi_2015;focal_2024;hg_2007;newmark_2005;newmark_2017;opheim_1991;pri_2010;sunlight_2015` for the n=8 row `lobbyist_spending_report_includes_total_compensation`). YAML `source_quotes:` tracks question-level pedigree. We discovered the YAML is lossy on multi-rubric rows — 50 multi-rubric TSV rows but only 1 multi-source YAML row (and that one is two questions from the same paper). The other 49 multi-rubric rows had their additional source quotes dropped at YAML-author time. Not Round-2-blocking under the lean-prompt principle (the model only needs the actual question, not the rubric chronology), but a real Phase A pedigree-completeness gap.

- **Schema asymmetry between rows #4 and #5.** Row #4 uses `TimeThresholdCell` (composite `magnitude + unit`); row #5 uses `FloatCell` (single value, no unit slot). Same observable family (time-based lobbyist threshold), different cell types. Dan's concern: "do ALL states frame their threshold as a percentage of the lobbyist's time? I would imagine most framed it as 'number of hours'..." Forcing percent on row #5 means the model does math-on-the-fly with assumed denominators.

- **`other_specification` escape hatch.** Dan's design: add `other_specification: str | None = None` to TimeThresholdCell. When the statute's unit doesn't fit the enumerated `TimeUnitLiteral` (currently 4 buckets), leave `unit=None` and put a verbatim description in `other_specification`. Future-proofs the schema without chasing every possible unit.

- **Promote row #5 from FloatCell to TimeThresholdCell.** Blast radius investigation showed row #5 is the only FloatCell row in the compendium; no projection helper reads it. The only test touchpoint is `test_coerce_string_to_float_for_floatcell` (line 99 of `test_tier_1_legal_axis.py`), which needs to retarget to a synthetic FloatCell spec (the class stays as a schema affordance).

- **Audit plan structure.** Dan asked for a plan covering an audit of all prompts to the lean-question discipline, with the audit agent identifying problems + drafting fixes in a handoff doc, and future execution agents (plural) applying the fixes. Designed: 8 audit dimensions per prompt (extraction-vs-projection, lean-question, return-shape spec, cell-type alignment, null semantics, axis disambiguation, scope clarity, schema mismatch); three verdicts (PASS / NEEDS-REVISION / SCHEMA-BLOCKED); chunk-by-chunk findings doc; strict read-only — audit agent doesn't edit YAML or code.

- **De jure pivot (session-end decision).** While reviewing the "combined-axis row" architecture (where one YAML prompt is shared between a legal-axis cell and a practical-axis cell with different return shapes), Dan ruled: combined-axis rows verboten henceforth; this research line is de jure only. The 3 remaining combined-axis rows (`lobbyist_registration_required`, `lobbyist_registration_deadline_days_after_first_lobbying`, `lobbyist_spending_report_filing_cadence`) must be Pattern-C-split into single-axis pairs.

## Provisional Findings

- **Round 1 post-fix match rate: 19/30 (63.3%).** Captured in [`results/20260606_round_1_post_phase_1_audit.md`](../results/20260606_round_1_post_phase_1_audit.md). Per-indicator and per-state deltas match the failure-mode doc Trend 1 prediction exactly (IND_199 +3, IND_207 +1, TX IND_199 flips from spurious-match to correct-mismatch). Confirms the vocab-schism diagnosis was precise.

- **Of the 11 misses post-Phase-1, 6 are Trend 5** (CPI more generous than extraction): IND_207 WI/OH/CA/(TX-variant) all show the helper now correctly mapping extracted MODERATE/NO, but the oracle disagrees because CPI's grading convention counts more arrangements as "regular auditing" than statute-literal extraction does. The audit script's "vocab-mismatch" warning column is stale on these cells — the helper now accepts those vocabularies; the mismatch is interpretive.

- **TSV pedigree is RICHER than YAML pedigree** for multi-rubric rows. The n=8 row `lobbyist_spending_report_includes_total_compensation` has 8 papers reading it per the TSV but only the PRI 2010 quote in the YAML. Not Round-2-blocking under the lean-prompt principle; flagged as deferred Phase A pedigree-completeness pass.

- **Row #5 is the only FloatCell in the compendium.** Promoting it to TimeThresholdCell leaves FloatCell as a class with zero consumers. Schema affordance retained for future rows; coercion-path test retargets to a synthetic spec.

- **TimeUnitLiteral domain has obvious gaps** (no `hours_per_week`, the most common state-statute framing) but the escape hatch makes these non-urgent. Document for future cleanup.

- **The "combined-axis row" architecture conflates extraction with two different observables.** "What the law says" and "what happens in practice" are independent questions; the YAML's one-prompt-per-row design forced them to share a prompt, which doesn't work when the legal-axis cell is BinaryCell and the practical-axis cell is GradedIntCell. De-jure-only pivot kills the source of the problem; future agents Pattern-C-split the 3 remaining rows.

## Decisions Made

- **Phase 1 committed and pushed** as `cbcd3e2`. Acceptance gate hit (pytest 1901 green; 19/30 ≥ 60% threshold; helper diff < 50 lines).

- **Phase 2 replaced by schema-aware plan:** [`plans/20260606_phase_2_schema_aware_prompt_hygiene.md`](../plans/20260606_phase_2_schema_aware_prompt_hygiene.md). Three sub-phases: A (schema change + row #5 promotion + FloatCell coercion-test refactor), B (7 lean prompt rewrites with Dan-review gate before commit), C (legal-axis format-hint regression test). Replaces the prior plan's Phase 2 wholesale.

- **Prompt audit plan landed:** [`plans/20260606_prompt_audit_all_questions.md`](../plans/20260606_prompt_audit_all_questions.md). Read-only audit agent produces one findings doc; execution agents apply fixes in separate plans. Carries a HANDOFF UPDATE banner with the de jure pivot's implications.

- **Combined-axis rows abolished.** This research line is de jure only. The 3 remaining combined-axis rows must be Pattern-C-split (separate plan; flagged in audit plan's handoff banner).

- **Test scope = dispatch scope.** The format-hint regression test in Phase 2C iterates only `axis == 'legal'` cells in the 6 default chunks, matching the dispatcher's filter.

- **Round 2 reframing.** Per Dan: *"don't sweat Round 2... the whole point of doing a handful at a time is to stress-test our model against reality; we can make adjustments until we're properly capturing what's out there."* The original Phase 2 plan's σ_noise-comparability concern is overcalibrated. Iterative model-vs-reality calibration is the design.

## Results

- [`results/20260606_round_1_post_phase_1_audit.md`](../results/20260606_round_1_post_phase_1_audit.md) — post-Phase-1 audit of Round 1 stored extractions; Table A (per-cell) + Table B (per-state); interpretation of remaining 11 misses by trend.

## Open Questions

- **Should the existing ~75 already-well-specified prompts also be tightened to the lean-question discipline?** They mostly follow `[rubric quote] + [clarification] + [format spec]` — bloated by Dan's principle, but rewriting is much larger scope and not Round-2-blocking. The audit plan covers this implicitly (all 131 legal-axis prompts, post-de-jure-pivot scope reduction).

- **When does the prompt audit agent run — same session as the Phase 2 execution, or fresh?** The two plans are independent. Likely-fresh per Nori-flow.

- **Should the 3 combined-axis-row splits be one plan or three?** The v2.1 Pattern C split (which already abolished 2 of 5 combined-axis rows) was done in a single coordinated session. The remaining 3 could follow that precedent. The audit plan's handoff banner flags this for the next agent's call.

- **Audit-script reporter staleness:** the audit script's "vocab-mismatch" warning column references the old helper expected-set. Should be updated after Phase 2 lands so future audit runs don't read misleadingly on the IND_207 cells. Small follow-up.

- **TimeUnitLiteral expansion (add `hours_per_week`):** deferred per the escape-hatch design. Revisit if Round 2 surfaces many `hours_per_week` statutes where structured magnitude+unit would be cleaner than free-text.

- **TimeSpentCell parallel cleanup** (same shape as TimeThresholdCell pre-fix; same escape-hatch gap). Not in the 6 default chunks; mirror the fix when that row goes into dispatch rotation.

- **YAML pedigree-completeness pass** (recover the 49 multi-rubric rows' dropped source quotes). Review-side work; separate plan when prioritized.

## Handoff for next agent

Two new plan docs sit on disk for execution by fresh sessions:

1. **Phase 2 (schema-aware prompt hygiene)** — `docs/active/cross-state-cpi-2015-validation/plans/20260606_phase_2_schema_aware_prompt_hygiene.md`. Has TDD discipline + Dan review gate before commit on Phase B. Updates `TimeThresholdCell`, promotes row #5, rewrites 7 prompts, adds a legal-axis format-hint regression test. The plan's §Risks still references "deferred until Prong 2" wording about practical-axis cells — the de jure pivot makes that wording misleading; the next agent should patch.

2. **Prompt audit (all questions)** — `docs/active/cross-state-cpi-2015-validation/plans/20260606_prompt_audit_all_questions.md`. **Read first the HANDOFF UPDATE banner at the top** — the de jure pivot reduces scope to ~131 legal-axis prompts, drops the combined-axis verdict dimension, and adds an escalation for splitting the 3 remaining combined-axis rows. The audit agent updates the plan before executing.

Phase 1 (helper vocab fix) is **DONE** (commit `cbcd3e2`, pushed). The pre-dispatch plan's Phases 3–5 remain as-written; Phase 4 (Round 2 dispatch ~$15) requires explicit Dan authorization before launch.

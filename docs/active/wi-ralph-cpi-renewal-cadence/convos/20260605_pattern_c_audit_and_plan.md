# Pattern C audit on v2 TSV + plan doc for v2.1 schema bump + parallel inverse fix

**Date:** 2026-06-05 (short pre-flight session; ran out of context budget before structural edits)
**Branch:** wi-ralph-cpi-renewal-cadence
**Plan:** [`../plans/20260605_pattern_c_row_split_v2_1.md`](../plans/20260605_pattern_c_row_split_v2_1.md)
**Predecessor convo:** [`20260604_phase_b_silent_unit_mismatch_sweep.md`](20260604_phase_b_silent_unit_mismatch_sweep.md) §"Post-session refinement"

## Summary

Short session. Picked up the iter-5-convo §"Post-session refinement" handoff and executed Step 1 of the 3-step next-session plan: the Pattern C row-axis-bug audit on `compendium/disclosure_side_compendium_items_v2.tsv`. Confirmed scope matches the convo's anticipation — exactly 1 egregious instance (`lobbying_violation_penalties_imposed_in_practice` carrying a category-error legal-axis cell) and 1 inverse / less-egregious instance (`lobbying_disclosure_audit_required_in_law` carrying a name-mis-keyed practical-axis cell). Other 3 `legal+practical` rows are neutrally-named and structurally coherent. **No API cost.**

Surfaced two scoping decisions to Dan before touching the shared TSV: (a) v2 in-place edit vs v2.1 schema bump; (b) fix the inverse row this session or defer. **Dan picked v2.1 + parallel inverse fix** — bigger scope than the convo's default but cleaner historical record. Session ran out of context budget before Step 2 (the structural edit), so the deliverable shifted from "Steps 2+3 executed" to "Step 2+3 plan doc written for next implementing agent."

The plan doc [`../plans/20260605_pattern_c_row_split_v2_1.md`](../plans/20260605_pattern_c_row_split_v2_1.md) is self-contained for cold pickup — captures Step 1 audit findings, both Dan-decided scoping calls, the 4 row-level changes (2 edits + 2 additions = 184 rows net), YAML population templates per cell type, downstream-consumer pointer updates, dispatch command for Step 3, cost projection ($0.30), and 2 open scoping questions (the `_audit_conducted_in_practice` vs `_audit_required_in_practice` naming choice; v2.1 pointer scope).

## Topics Explored

### 1. Pre-flight reads

Read STATUS.md (lines 1-46 for current focus header + compendium 2.0 success criterion), the iter-5 convo end-to-end including §"Post-session refinement," the RESEARCH_LOG.md trajectory (4 sessions: kickoff → iters 1+2 → iters 3+4 → sweep + iter 5), and confirmed branch state (clean working tree, up-to-date with origin, on `cf7c4ee`). The §"Post-session refinement" handoff sentence specified the exact next-session plan; this session executed Step 1 and converted Steps 2+3 to a plan doc for next session.

### 2. Step 1 — Pattern C audit (executed)

Grepped v2 TSV (182 rows) for `_in_practice|_in_law` substrings in `compendium_row_id`. Only 2 hits — matching the convo's anticipated scope exactly:

| Line | Row | Cell types | axis | Severity |
|---|---|---|---|---|
| 49 | `lobbying_disclosure_audit_required_in_law` | `enum (legal) + typed int 0-100 step 25 (practical)` | `legal+practical` | Inverse / less egregious |
| 72 | `lobbying_violation_penalties_imposed_in_practice` | `binary (legal) + typed int 0-100 step 25 (practical)` | `legal+practical` | Egregious Pattern C |

Cross-checked all 5 rows with `axis=legal+practical` to verify no name-vs-axis tension on the other 3 (`lobbyist_registration_required`, `lobbyist_spending_report_filing_cadence`, `lobbyist_registration_deadline_days_after_first_lobbying`) — all neutrally-named, dual-axis split semantically coherent, NOT bugs.

### 3. Scoping questions to Dan

Presented Step 1 findings + asked two scoping questions before editing the shared TSV (multi-committer repo norm per CLAUDE.md):

- **Q1 — v2 in-place vs v2.1 schema bump?** Dan picked v2.1. Cleaner historical record; v2 stays frozen as prior reference.
- **Q2 — Fix the inverse `_audit_required_in_law` row this session?** Dan picked fix in parallel. Doubles the structural change but addresses both bugs cleanly.

### 4. Plan doc written (deliverable)

Wrote `plans/20260605_pattern_c_row_split_v2_1.md` capturing:
- Step 1 findings preserved.
- Dan's 2 scoping decisions documented.
- 4 row-level changes specified: edit `_imposed_in_practice` (strip legal axis → practical-only), add `_defined_in_law` (binary, legal axis, `rubrics_reading: cpi_2015;hg_2007`), edit `_audit_required_in_law` (strip practical axis → legal-only), add new `_audit_conducted_in_practice` (typed int 0-100 step 25, practical axis, `rubrics_reading: cpi_2015`). Net 182 → 184 rows in v2.1.
- BinaryCell additive prompt template for the new `_defined_in_law` row.
- Downstream-consumer pointer updates flagged: `tier_1_direct_read_legal_axis.py`, `silent_unit_mismatch_sweep.py`, plus a `grep -rn` sweep for others.
- Step 3 dispatch command (`--chunks enforcement_and_audits`) + audit checklist + cost projection ($0.30).
- 2 open scoping questions for implementing agent: `_audit_conducted_in_practice` vs `_audit_required_in_practice` naming; v2.1 pointer scope (this branch only vs propagate to main).

## Provisional Findings

- **Pattern C audit scope was correctly anticipated by the iter-5 convo.** Only 1 egregious + 1 inverse instance in v2; other dual-axis rows are structurally coherent. This is good news — Pattern C is rare in the current compendium, not a systemic issue requiring broad refactoring.

- **The inverse fix on `_audit_required_in_law` is structurally analogous to the egregious one.** Same "split axis-mis-keyed cell to a new row" shape, just inverse direction (strip practical instead of strip legal). Doubles the row-edit cost but doesn't introduce new design questions.

- **The new `_audit_conducted_in_practice` row will not be dispatched by Step 3.** It's practical-axis-only; the legal-axis dispatcher (`tier_1_direct_read_legal_axis.py`) can't reach it. The practical-axis pipeline doesn't exist yet — so YAML population for that row is provenance-preservation only, not for immediate testing. Flag in plan.

## Decisions Made

- **Dan picked v2.1 schema bump over v2 in-place edit.** New file `compendium/disclosure_side_compendium_items_v2.1.tsv` rather than mutating v2. Captured in plan §"Dan's scoping decisions."

- **Dan picked parallel inverse fix.** Both `_imposed_in_practice` and `_audit_required_in_law` get Pattern C splits this session. Net 182 → 184 rows.

- **Session deliverable shifted from Steps 2+3 execution to Steps 2+3 plan doc.** Context budget too tight to safely execute the structural edits + YAML population + dispatch in one session. Plan doc captures full state for cold pickup.

- **No structural edits this session.** v2 TSV, YAML, and dispatcher scripts unchanged. Only deliverables: plan doc + this convo doc + RESEARCH_LOG/STATUS updates.

- **Implementing agent will be asked to confirm `_audit_conducted_in_practice` vs `_audit_required_in_practice` naming with Dan before adding that row.** Open scoping question documented in plan.

## Results

- **Plan doc:** [`../plans/20260605_pattern_c_row_split_v2_1.md`](../plans/20260605_pattern_c_row_split_v2_1.md) — self-contained for cold pickup; captures Step 1 findings + Dan's 2 scoping decisions + Step 2+3 execution spec.
- **No code, no API spend, no TSV/YAML edits.** wi-ralph cumulative spend unchanged at **$2.3573**. wi-tier1-direct-read unchanged at $7.2946. Grand total WI Phase 1/2 + Phase B: **$9.6519**.

## Open Questions

- **`_audit_conducted_in_practice` vs `_audit_required_in_practice` — which name?** Plan flags this for next session. Parallels `_penalties_imposed_in_practice` argue for "_conducted_in_practice"; CPI's IND_207/IND_208 split language may argue otherwise.

- **v2.1 pointer scope — this branch only or propagate to main?** Plan defaults to "this branch only; surface for merge after BinaryCell test confirms structural fix." Dan can override.

- **Does the practical-axis pipeline get scoped this session or deferred?** Implicit in adding `_audit_conducted_in_practice` and `_imposed_in_practice` (practical-only) — both rows would dangle uncovered. Worth flagging in next-session plan as a forward-pointing question; not blocking on Step 3.

## Session meta — short session by design

Context budget exhausted before structural edits could land. Right call to convert to plan doc rather than attempt half-execution and leave the shared TSV in an inconsistent intermediate state. The pattern (read handoff → audit → surface scoping decisions → write plan for next session) is reproducible and preserves Dan's scoping choices in durable docs.

The plan doc is the substantive deliverable. Step 1 audit work is preserved in both this convo AND the plan's "What's already done" section (intentional duplication — convo for trajectory record, plan for self-contained next-session execution).

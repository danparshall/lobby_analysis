# Phase B Ralph — iters 3 & 4 on `lobbyist_spending_report_filing_cadence`: additive pattern generalizes to EnumCell + robust to wrong-axis source quote

**Date:** 2026-06-04 (later evening, immediately after iter 1+2 on `renewal_cadence`)
**Branch:** wi-ralph-cpi-renewal-cadence
**Plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md) (Phase B kickoff plan — this is the second-row trial)
**Iterations log:** [`../results/20260604_filing_cadence_iterations.md`](../results/20260604_filing_cadence_iterations.md)
**Predecessor convo:** [`20260604_phase_b_iter_1_and_2.md`](20260604_phase_b_iter_1_and_2.md) — iter 1+2 on `renewal_cadence` (IntCell), established the additive-units pattern
**Sweep plan referenced (still candidate-b for a future session):** [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md)

## Summary

Picked up the handoff from iter 1+2 to test whether the additive cell-type-aligned-instruction pattern generalizes from IntCell to EnumCell. The handoff named `lobbyist_spending_report_filing_cadence` as the EnumCell wide-pass-failure candidate (~$0.30 budget). Pre-flight surfaced two structural complications the handoff hadn't seen:

1. The row is **split-axis** — `enum (legal) + typed int 0-100 step 25 (practical)` — and CPI's only indicator touching it (IND_202, not IND_201 as the handoff said) scores **only the practical axis**. The dispatcher only extracts the legal axis. So the wide-pass YAML's `prompt:` field (mechanically populated from IND_202's practical-axis source quote) was structurally asking the wrong-axis question against a legal-axis EnumCell.
2. There is **no CPI legal-axis oracle for this row.** The statute itself is the oracle: WI §13.68(1) puts the filing duty on the principal; §13.68(4) routes lobbyist info through the principal → expected legal-axis enum value = `'none'` (lobbyists do not file separately in WI).

After surfacing the path-choice to Dan, agreed Path α: continue on `filing_cadence` with rewritten legal-axis prompt; oracle = the statute reading. Two iterations dispatched against `lobbyist_spending_report` chunk (~$0.74/iter — chunk is 30 legal cells vs `renewal_cadence`'s 8). Iter 3 was vocab-strip + EnumCell-aligned legal-axis prompt; iter 4 ablation was wrong-axis CPI IND_202 quote prepended + same legal-axis prompt appended — a *stricter* ablation than iter 1+2's (wrong axis vs wrong vocab-same-axis).

**Both iterations converged 6/6 on `value: 'none'` at high confidence, all citing both §13.68(1) and §13.68(4).** Combined with iter 1+2 (IntCell), **4 of 4 iterations across 2 cell types converged 6/6 on statute-derived oracle values**. Phase A pre-flight YAML audit's pattern remains purely additive: append the cell-type-aligned actionable question; never need to strip the source quote (even when wrong-axis). Cumulative wi-ralph spend $2.0720 of $3-5 budget.

A bonus structural finding: the wide-pass Commit 3 audit (`docs/active/wi-tier1-direct-read/results/20260604_wi_wide_pass_audit.md` row 5 of "Decomposition of the 6 wide-pass disagreements") read Claude's wide-pass `"50"` on this row as semantically improved vs narrow-pass `"none"`. With the legal-axis oracle now in hand, the read **inverts** — narrow-pass `"none"` was substantively correct; wide-pass `"50"` was dragged WRONG by the CPI practical-axis vocab. This is the silent-mismatch class the sweep plan (candidate (b) from the prior session) was designed to catch; iter 3 surfaced a concrete instance, validating the sweep's motivating risk.

Production YAML now holds iter 4's prompt (CPI IND_202 quote at front + appended legal-axis question). Test suite unchanged — no code edits this session.

## Topics Explored

- **Pre-flight reads and chunk/cell/YAML inspection.** Verified row was in `lobbyist_spending_report` chunk (30 legal cells, 5× the size of `registration_mechanics_and_exemptions`). Read current YAML (`source_quotes.cpi_2015_IND_202` + matching prompt field — verbatim IND_202 practical-axis vocab). Read CPI projection mapping doc for IND_201 vs IND_202: **IND_201 reads three *different* rows** (`lobbyist_spending_report_required`, `_includes_itemized_expenses`, `_includes_compensation`); **IND_202 is the only CPI indicator touching `filing_cadence`** and it scores the practical axis only. Read CPI 2015 C11 per-state CSV: WI IND_201 = NO, WI IND_202 = 0. **Neither indicator scores the legal-axis enum cell that we extract.** Read EnumCell spec in `src/lobby_analysis/models_v2/cells.py` — bare EnumCell accepts any non-empty string today; no per-row Literal domain registered for `filing_cadence` in `enum_domains.py`. So **the prompt is the only constraint** on what gets emitted.

- **Vintage check (§13.68(1) + §13.68(4), 2015 vs 2025).** Both subsections identical between 2015 and 2025; the only change is "board" → "commission" reflecting the Ethics Commission rename, which doesn't touch cadence semantics. Oracle target for both vintages: `'none'` (lobbyists do not file separately).

- **Iter 0 inspection of pre-iter3 baseline JSONs** (Python script at `/tmp/inspect_filing_cadence.py`, ad hoc). Surfaced the dual failure mode that the wide-pass Commit 3 audit didn't fully capture: **Claude 3/3 emitted string `"50"` at confidence=medium** (semantically wrong-variable — a CPI tier score, NOT a cadence enum value; EnumCell accepted because bare); **GPT 3/3 emitted int 0 → instantiation_failed** (EnumCell wants string). Both models correctly identified the substantive WI law in their justifications (principals file, lobbyists route info); the disconnect was the YAML prompt asking the wrong-axis question.

- **Path-decision discussion with Dan.** Surfaced three options: (α) continue on `filing_cadence` with rewritten legal-axis prompt and statute-derived oracle; (β) switch target to `lobbying_disclosure_audit_required_in_law` (IND_207, EnumCell, has CPI legal-axis oracle YES, but already converges 6/6 wide-pass at MODERATE — different test shape, and likely models are right and CPI is stale); (γ) pause iter 3 and document only. Dan picked α with sub-option recommendation "iter 3 first, decide iter 4 ablation after."

- **Iter 3 prompt design + dispatch.** Drafted vocab-strip prompt with explicit enum members enumerated (annual / monthly / quarterly / semiannual / triannual / biennial / other / none) and explicit absence-case handling for the WI-specific routing-to-principal pattern. Source quote retained in YAML's `source_quotes:` for provenance; only the `prompt:` field changed. Archived pre-iter3 wide-pass JSONs to `_pre_iter3_filing_cadence/`. Dispatched via `--chunks lobbyist_spending_report`; $0.7404 cost, 0 errors, 6/6 converged on `'none'` at confidence=high, all citing both §13.68(1) AND §13.68(4).

- **Walk-through of CPI indicator terminology for Dan.** Dan asked "I don't know what 'IND201' is" — explained CPI 2015 State Integrity Investigation, the 14 IND_xxx indicators under Lobbying Disclosure category 11, the legal-axis (YES/MODERATE/NO) vs practical-axis (0/50/100) split, and why IND_201 vs IND_202 mattered for understanding which oracle exists for this row.

- **Iter 4 ablation design + dispatch.** Restored CPI IND_202 practical-axis quote at the front of the prompt + kept the iter-3 legal-axis question + EnumCell enumeration appended at end. Tests the stricter "wrong-axis source quote is harmless when paired with right-axis actionable question" hypothesis. Archived iter 3 JSONs to `_pre_iter4_filing_cadence/`. Dispatched; $0.7494 cost, 0 errors, 6/6 converged on `'none'` at confidence=high, citation pattern identical to iter 3 (§13.68(1) AND §13.68(4) on every run).

- **Cross-checked the wide-pass Commit 3 audit's row 5 interpretation.** The audit's "Decomposition of the 6 wide-pass disagreements" table characterized wide-pass Claude's `"50"` as semantically improved relative to narrow-pass `"none"` ("more correct — WI files semi-annually, matching the CPI 50-tier rubric"). The audit was anchored on assuming the YAML prompt was asking the right question. With the legal-axis oracle in hand from iter 3 + iter 4, this read **inverts**: narrow-pass `"none"` was substantively correct (lobbyists don't file separately); wide-pass `"50"` was dragged WRONG by the CPI practical-axis vocab. Wrote this up in the iterations log §Findings 4 + §Recommendations 6 without retroactively editing the wide-pass audit (matches the "don't retro-correct prior session narratives" principle from iter 1+2).

## Provisional Findings

- **The additive cell-type-aligned-instruction pattern generalizes to EnumCell.** 4 of 4 iterations across 2 cell types (IntCell from iter 1+2; EnumCell from iter 3+4) converged 6/6 on statute-derived oracle values. The actionable-question-plus-cell-type-enumeration shape works for both numeric (IntCell, "Answer in months as integer") and categorical (EnumCell, "Answer with one of: a, b, c, or 'none'") observables.

- **The additive pattern is robust to wrong-axis source-quote contamination — not just rubric-vocab-vs-cell-type mismatch.** Iter 4's ablation is structurally stricter than iter 1+2's iter 2 — the rubric quote is wrong-axis (practical-axis 100/50/0 vocab against a legal-axis enum), not just wrong-vocab-same-axis. The ablation cleared anyway. Phase A's per-row work doesn't need to identify or strip wrong-axis source quotes; appending the right actionable question is sufficient.

- **The wide-pass Commit 3 audit's interpretation of `filing_cadence` row 5 inverts with the legal-axis oracle in hand.** Wide-pass Claude `"50"` looked like an improvement vs narrow-pass `"none"` when graded against CPI's practical-axis 50-tier; against the statute (the right legal-axis oracle), `"none"` is correct and `"50"` is the regression. This is direct evidence of the silent-mismatch class — wide-pass JSONs cannot be trusted for legal-axis enum values on rows where the YAML prompt is wrong-axis. The sweep plan from candidate (b) is now better motivated.

- **Phase A pre-flight YAML audit scope across both tested axes of mismatch:** identify cell type, append cell-type-aligned actionable question if missing, leave source quote alone for provenance. No strip-and-rewrite. No wrong-axis-detection-and-strip. Just an additive sentence per row that needs it.

- **The wide-pass YAML population's structural blind spot** is now characterized: for rows where the source rubric reads only an axis the row doesn't extract, the mechanical-population pass populates a structurally wrong-axis prompt. **Candidate v2.2 or Phase A input class:** flag axis-mismatch per (row × source-rubric) pair; either populate a different rubric's quote (if available for the right axis) or fall back to an appended actionable question.

- **DecimalCell-non-negative and BinaryCell remain unconfirmed for pattern generalizability.** The two remaining wide-pass-failure rows (`lobbyist_filing_itemization_de_minimis_threshold_dollars` with the -1 sentinel pattern; `lobbying_violation_penalties_imposed_in_practice` with CPI 100/50 tier values against BinaryCell — also a known **Pattern C** v2.2 row-axis bug per the prior-art analysis) would close the 4-cell-type matrix in ~$0.60-1.50 of additional iterations in a follow-up session.

## Decisions Made

- **Phase A pattern is confirmed purely additive for IntCell + EnumCell, in both axis-aligned and wrong-axis cases.** Documented in iterations log §Findings 1-3 and §Recommendations 1, 3. Concrete fix template per cell type: IntCell → "Answer in [unit] as an integer (e.g., …)"; EnumCell → "Answer with one of: [allowed values]. Use '[null member]' if [absence case]."

- **Production YAML for `filing_cadence` holds iter 4's prompt** (CPI IND_202 quote at front + appended legal-axis EnumCell question). Same posture as iter 2 for `renewal_cadence` — provenance preserved, actionable question appended, ablation confirms this form is at least as good as strip-only.

- **No retroactive correction of the wide-pass Commit 3 audit's row 5 narrative.** Same posture as iter 1+2's no-retro-edit decision. Refinement lives in the iterations log §Findings 4 + §Recommendations 6 and this convo.

- **No code changes this session.** Dispatcher's hardcoded `_DEFAULT_RESULTS_BASE` (which puts wi-ralph JSONs under the wi-tier1 docs subtree) still flagged as low-priority cleanup; deferred again.

- **STATUS.md table row for wi-ralph-cpi-renewal-cadence to be added at finish-convo commit** (per Dan's confirmation at the start of this session — wi-ralph branch was missing from the Active Research Lines table even though Recent Sessions narrative covered both prior sessions).

- **Phase B continues.** Next-session candidates carry forward from iter 1+2:
  - (b) silent-unit-mismatch sweep on the 17 other CPI-readable rows — plan exists at [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md), better-motivated now after iter 3's silent-mismatch evidence
  - (a') second remaining cell-type trial — DecimalCell on `de_minimis_threshold_dollars` and/or BinaryCell on `penalties_imposed_in_practice`; ~$0.60-1.50 total
  - (c) Phase A pre-flight YAML audit at scale (now better-defined since pattern is confirmed across both tested cell types and both axis-cases)

## Results

- **No code change.** Dispatcher unchanged; tests unchanged (suite still 1687 pass / 0 fail / 3 xfailed from iter 1+2's last commit `5351072`).
- **YAML edit:** `compendium/source_quotes.yaml` — `lobbyist_spending_report_filing_cadence.prompt` updated to iter 4's pattern (CPI vocab preserved + appended legal-axis EnumCell question). `source_quotes:` field unchanged.
- **Iterations log:** [`../results/20260604_filing_cadence_iterations.md`](../results/20260604_filing_cadence_iterations.md) — full per-iteration tables with all 12 model responses, ablation reasoning, Phase A scope re-statement, spend ledger, recommendations.
- **Result JSONs (preserved):**
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter3_filing_cadence/` — 6 pre-iter-3 wide-pass JSONs
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter4_filing_cadence/` — 6 iter 3 JSONs
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*__lobbyist_spending_report__run*.json` — 6 iter 4 JSONs (current)
- **Spend ledger:** Iter 3 $0.7404 + Iter 4 $0.7494 = $1.4898 this session. wi-ralph cumulative **$2.0720** (against $3-5 ceiling, $0.93-$2.93 remaining).
- **Cross-branch ledger:** wi-tier1-direct-read $7.2946 (unchanged) + wi-ralph $2.0720 = **$9.3666** total WI Phase 1/2 + Phase B spend.

## Open Questions

- **Does the additive pattern generalize to DecimalCell-non-negative + BinaryCell?** The two remaining wide-pass-failure rows. ~$0.60-1.50 total to test in a follow-up session. The 4-cell-type matrix would close if both confirm.

- **Are there silent mismatches on the 17 other CPI-readable rows that DID instantiation-pass in the wide-pass?** Iter 3 just produced a concrete instance of this class (Claude wide-pass `"50"` on `filing_cadence` looked like an improvement, was actually a regression). The sweep plan (`plans/20260604_silent_unit_mismatch_sweep.md`) is the diagnostic.

- **Does the pattern port to non-CPI rubrics?** All 4 wide-pass failure rows are CPI-introduced. PRI's E1/E2 questions or Sunlight's 5-tier ordinals against EnumCells might need different cell-type instructions.

- **For rows where the source rubric is axis-mismatched to the cell's extraction axis, what's the Phase A pre-flight script's actionable detection?** A script can compute per-(row × rubric) axis alignment from the projection mapping docs + the TSV's `axis` column. Rows where every reading rubric is wrong-axis are the highest-priority candidates for an appended actionable question (currently they're getting wrong-axis prompts mechanically).

- **`lobbying_disclosure_audit_required_in_law` (IND_207, EnumCell, legal-axis) converges 6/6 at `"MODERATE"` in wide-pass, but WI's CPI 2015 oracle is YES.** Models cite §13.74(1) examination requirement and conclude MODERATE (compliance review, not full third-party audit). Plausible that models are right and CPI 2015's score for WI is stale or differently interpreted. Worth a closer look as part of the sweep candidate.

## Session meta — Dan's "explain it" was load-bearing

Mid-session, Dan asked "walk me through this? I don't know what 'IND_201' is." A productive question — I had been speaking jargon (CPI indicator IDs, axis terminology) that hadn't been grounded for him this session. The walk-through forced me to lay out the legal-axis vs practical-axis distinction cleanly and explain why the ablation's "wrong-axis" framing differs from iter 2's "wrong-vocab-same-axis" framing. After the walk-through, the iter 4 decision was much clearer. Lesson: when the conversation gets dense in domain-specific abbreviations (especially across sessions where I've internalized terminology that Dan hasn't), pause to ground them before asking decision questions.

Also: Dan's "let's just try a couple and see how we get" framing from iter 1+2 continued to pay off here — running iter 3 alone would have left the wrong-axis-ablation question open. The session went 2 iterations again with the same shape (one direct, one ablation), reproducing the iter 1+2 cadence. The pattern of "first iteration tests the intervention, second iteration runs the ablation in the OTHER direction" is becoming a Phase B house style.

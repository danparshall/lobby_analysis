# Phase B Ralph — iterations 1 & 2 on `lobbyist_registration_renewal_cadence` converged in two rounds

**Date:** 2026-06-04 (evening, immediately after the wi-ralph kickoff + plan landed)
**Branch:** wi-ralph-cpi-renewal-cadence
**Plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md)
**Iterations log:** [`../results/20260604_renewal_cadence_iterations.md`](../results/20260604_renewal_cadence_iterations.md)
**Predecessor convo:** [`20260604_phase_b_kickoff.md`](20260604_phase_b_kickoff.md)

## Summary

Picked up the wi-ralph kickoff plan with Dan's answers to the 4 plan questions: (1) merge wi-tier1-direct-read in first; (2) Option A (add `--chunks` flag); (3) vintage check first; (4) "let's just try a couple and see how we get." Executed the four pre-flight steps then ran two Ralph iterations on `lobbyist_registration_renewal_cadence`. Both iterations converged 6/6 on `value: 24` matching the CPI 2015 IND_199 MODERATE oracle exactly. Cumulative spend $0.5822, well under the $3-5 budget.

The substantive learning: **iter 2's ablation showed CPI's YES/MODERATE/NO vocab is harmless when paired with explicit cell-type-aligned units guidance.** Both prompts (vocab-strip + units, and vocab-kept + units appended) converge identically. The wide-pass failure was caused by *absent cell-type instruction*, not by *presence of CPI rubric vocab*. **This substantially shrinks Phase A pre-flight YAML audit scope:** instead of stripping rubric scoring vocab from every prompt (destructive, provenance-losing), Phase A's pattern is **additive** — append a cell-type-aligned instruction sentence to every prompt whose source rubric uses tier vocabulary against a typed cell.

Production YAML now carries iter 2's prompt (CPI vocab preserved + units instruction appended), committed in this session. Test suite stays at 1687 pass / 0 fail / 3 xfailed (added 4 new tests for the `--chunks` flag; no regressions on the merged-in 1683 baseline).

## Topics Explored

- **Pre-flight (4 steps, all clean).** (1) Merged wi-tier1-direct-read; resolved STATUS.md merge conflict (both branches prepended Recent Sessions entries) by interleaving via a one-off Python script in /tmp. (2) Vintage check on WI §13.63(1)(a) confirmed identical text 2015 → 2025 (both say "expire on December 31 of each even-numbered year") — biennial → CPI MODERATE oracle is valid for the 2025 extraction. (3) Added `--chunks <chunk_id> [<chunk_id> ...]` flag to `scripts/tier_1_direct_read_legal_axis.py` under TDD: 4 new tests in `tests/test_tier_1_chunks_filter.py` (omit = all six; single chunk filter; multi-chunk filter; unknown-chunk error path with valid list in message). RED → GREEN → full suite 1687 pass / 0 fail. Ruff clean. (4) Iteration 0: inspected the 6 wi-tier1 wide-pass JSONs for the target row's existing failure mode.

- **Iteration 0 baseline (no dispatch).** Read 6 result JSONs from the merged wi-tier1 wide-pass output. Failure mode confirmed: **Claude 3/3 instantiation failures** emitting `"YES"` or `"MODERATE"` (the wide-pass YAML's verbatim CPI text against IntCell), **GPT 3/3 instantiates but emits `2`** (years, not months) — the IntCell type has no unit enforcement so GPT's wrong-scale answer would pass silently. Both models correctly identify the statute (§13.63(1)(a) + §13.64(2)) and the biennial cadence; the disconnect is purely vocab-and-scale.

- **Iteration 1: vocab-strip + explicit units.** Replaced the YAML prompt with "How often must a lobbyist renew their registration under state law? Answer in months as an integer (e.g., 12 for annual, 24 for biennial, 36 for triennial). If no renewal is required, return null." Archived prior 6 chunk JSONs to `_pre_iter1_renewal_cadence/`. Dispatched via `--chunks registration_mechanics_and_exemptions` (the new flag in action). 6/6 dispatches, $0.2931 cost, ~2 min wall time. **6/6 converged on `value: 24`** with consistent §13.63(1)(a) citation and consistent biennial justification across both models.

- **Iteration 2: ablation — keep CPI vocab, append units.** To test what specifically about iter 1's change drove convergence, restored the original CPI YES/MODERATE/NO scoring text at the front of the prompt AND kept the cell-type-aligned units instruction at the end. Archived iter 1 JSONs to `_pre_iter2_renewal_cadence/`. Dispatched, $0.2891 cost. **6/6 again converged on `value: 24`.** Same oracle match. Claude's iter-2 justifications cite BOTH §13.63(1)(a) AND §13.64(2) (in iter 1 Claude cited only §13.63); GPT stays with just §13.63. Substantively identical answers; iter 2 justifications slightly richer.

- **Phase A scope re-estimation.** The ablation result implies Phase A pre-flight YAML audit is **additive, not destructive**: append "Answer in [unit] as an integer (e.g., …)" to every prompt with tier vocab against a typed cell. Doesn't require stripping the rubric scoring language. Substantially smaller scope than the wide-pass Commit 3 convo anticipated.

- **Mechanics note: per-iteration cost was ~$0.29, not the $0.05-0.10 the plan estimated.** The plan's estimate assumed a smaller chunk; `registration_mechanics_and_exemptions` has 8 legal cells, so the dispatch cost scales roughly linearly. At ~$0.29/iter, $5 budget supports ~17 iterations. Per-cell cost is ~$0.03-0.04 per model per run.

- **Dispatcher results-dir path is hardcoded to wi-tier1-direct-read.** When run from the wi-ralph worktree, `_DEFAULT_RESULTS_BASE` resolves to `<wi-ralph>/docs/active/wi-tier1-direct-read/results/tier_1/`. So this session's iter 1 + iter 2 JSONs land under the merged-in wi-tier1 docs path on the wi-ralph branch. Functionally fine (the original wi-tier1 branch still has its pristine post-wide-pass copies), but a future session may want to add a `--results-base` CLI flag so wi-ralph trials land at `docs/active/wi-ralph-cpi-renewal-cadence/results/...` for cleaner provenance. Flagged in iterations doc §recommendation 3, deferred this session.

## Provisional Findings

- **The wide-pass failure mode is solvable per-row in YAML via an additive sentence**, no schema change needed for `renewal_cadence`. The "IntCell with no unit metadata" concern was addressable at the prompt level for this row. Whether it generalizes across the other 3 wide-pass-failure rows (different cell types: EnumCell, DecimalCell, BinaryCell) is a follow-up question.

- **The cell-type-aligned units instruction is the load-bearing fix.** CPI's tier vocab is harmless when paired with that instruction. Phase A's pattern: append, don't strip. Preserves rubric provenance in the model-facing prompt.

- **Claude's instantiation-failure failure mode is safer than GPT's silent-wrong-value mode.** When Claude doesn't know how to answer in a cell-type-acceptable form, it loudly fails (instantiation_failed); when GPT can't, it sometimes emits a syntactically-valid but semantically-wrong value (e.g., 2 instead of 24). Loud failures are debuggable; silent ones become data-quality time bombs. The wide-pass Commit 3 audit caught Claude's failures because they were instantiation errors; GPT's `2`-vs-`24` mismatch was NOT caught because it passed instantiation and only the *unit semantics* were wrong.

- **The "first row by hand" framing was right.** Two iterations were enough to converge AND surface the additive-vs-destructive Phase A scope finding. A pre-automated Ralph loop would have iterated more without producing more learning.

- **`--chunks` flag is a clean per-iteration cost-controller.** Dispatches scoped to the target chunk; resume-skip behavior preserved on other chunks; per-iter cost ~$0.29 (linear in chunk size). 8-15 iterations realistic under the $5 ceiling.

## Decisions Made

- **Phase A pre-flight YAML audit pattern: additive, append cell-type-aligned instruction.** Documented in the iterations log §6 and this convo. Concrete pattern: "Answer in [unit] as an integer (e.g., …)" or equivalent for the relevant cell type. Sourced from iter 2's successful ablation.

- **Production YAML for `renewal_cadence` now holds iter 2's prompt.** CPI vocab preserved + units appended. Committed in this session.

- **No retroactive correction to the iter 0 baseline narrative.** The wi-tier1 wide-pass Commit 3 convo documented "rubric vocab is fatal for IntCell rows" as a tentative reading; iter 2 ablation now refines this to "absent cell-type instruction is fatal; rubric vocab is harmless." Refinement lives here, in the iterations log, and the eventual Phase A plan; we don't edit the Commit 3 convo.

- **Phase B continues:** next natural step is a **second-row trial** on `lobbyist_spending_report_filing_cadence` (CPI IND_201 = NO for WI; different cell type EnumCell) to test whether the additive pattern generalizes across cell types. ~$0.30 spend. Deferred to next session; Dan decides whether to greenlight.

- **No commit of the `--results-base` flag** this session. The hardcoded results path landed wi-ralph trials under the wi-tier1 docs subtree, which is fine for now (the original branch keeps its pristine copy).

## Results

- **Code change:** `scripts/tier_1_direct_read_legal_axis.py` — added `--chunks` flag + `resolve_active_chunks` helper. New tests in `tests/test_tier_1_chunks_filter.py` (4 tests, all passing). Full suite 1687 pass / 0 fail / 3 xfailed. Ruff clean. Commit `5351072`.
- **YAML edit:** `compendium/source_quotes.yaml` lobbyist_registration_renewal_cadence row's `prompt:` field updated to iter 2's pattern (CPI vocab + appended units instruction). `source_quotes:` field unchanged.
- **Iterations log:** [`../results/20260604_renewal_cadence_iterations.md`](../results/20260604_renewal_cadence_iterations.md) — full per-iteration table with all 12 model responses, ablation reasoning, Phase A scope re-estimation, spend ledger, recommendations.
- **Result JSONs (preserved):**
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter1_renewal_cadence/` — 6 iter 0 baseline JSONs (the wide-pass wi-tier1 versions)
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter2_renewal_cadence/` — 6 iter 1 JSONs
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json` (registration_mechanics_and_exemptions only) — 6 iter 2 JSONs (current)
- **Spend ledger:** Iter 1 $0.2931 + Iter 2 $0.2891 = **$0.5822 cumulative on wi-ralph**. Budget unused: $2.42-$4.42 (against $3-5 ceiling).
- **Cross-branch ledger:** wi-tier1-direct-read $7.2946 (unchanged) + wi-ralph $0.5822 = $7.8768 total WI Phase 1/2 + Phase B spend.

## Open Questions

- **Does the additive-units pattern generalize across cell types?** Iter 1 + iter 2 confirmed it on IntCell. Three other wide-pass-failure rows use EnumCell (`spending_report_filing_cadence`), DecimalCell-non-negative (`de_minimis_threshold_dollars`), and BinaryCell (`penalties_imposed_in_practice`). Pattern may need adaptation per cell type. ~$0.30 each to test; ~$0.90 to cover all 3.

- **Are there silent unit-mismatch issues** on the OTHER 17 CPI-readable rows that DID instantiation-pass in the wide-pass (so weren't flagged as failures)? GPT's iter-0 `2`-vs-`24` pattern is the diagnostic: cells where the model emits a syntactically-valid wrong-scale integer would pass instantiation but be semantically wrong. The wide-pass Commit 3 audit didn't catch these because they don't show up as instantiation_failed. A pass over the 21 CPI-readable rows looking for unit-mismatch patterns would be ~$2-3 of spend (re-dispatch all 6 chunks with current YAML and inspect unit-of-measure of every CPI-readable cell's value against the CPI per-state oracle).

- **Does the pattern port to non-CPI rubrics?** PRI's E1/E2 sub-aggregate questions ask differently shaped questions; Sunlight's 5-tier ordinals against EnumCells may need different cell-type instructions. The pattern's generalizability beyond CPI is not yet tested.

- **Should the production YAML pattern be iter 1 (vocab-strip) or iter 2 (vocab-kept + units)?** Both work. Iter 2 preserves CPI provenance in the model-facing prompt and produces slightly richer justifications (Claude cites both §13.63 + §13.64 in iter 2 vs only §13.63 in iter 1). Recommended iter 2 in the iterations log. The currently-committed YAML is iter 2.

- **Whether to add a `--results-base` CLI flag** so future wi-ralph dispatches land at the wi-ralph docs subtree rather than the wi-tier1 one. Functional concern is small; provenance/cleanliness concern is real. Defer until either (a) another wi-ralph trial happens, or (b) someone confuses wi-ralph iter outputs for wi-tier1 originals.

## Session meta — the ablation was the load-bearing move

If iter 1 had landed and I'd stopped there, the takeaway would have been "vocab-strip works; iterate on remaining wide-pass rows the same way." Iter 2's ablation revealed the actually-true finding ("units guidance alone suffices") and turned a wholesale-rewrite Phase A scope into an additive-sentence pattern. Same cost ($0.29 marginal), much bigger learning.

This is also a useful pattern for *any* "first-row-by-hand" trial: after one successful iteration, run the ablation in the OTHER direction (keep what you thought was the problem, change only what you thought was the fix) — the result tells you which variable actually moved the outcome.

Dan's "let's just try a couple and see how we get" framing was load-bearing here. Pushing to converge would have stopped at iter 1; the ablation was the second iteration's actual value.

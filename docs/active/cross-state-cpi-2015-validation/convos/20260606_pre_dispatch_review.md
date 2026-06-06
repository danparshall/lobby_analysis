# Pre-dispatch review + hygiene plan

**Date:** 2026-06-06
**Branch:** cross-state-cpi-2015-validation

## Summary

Session opened via handoff from leave-behind-prep: Day 2 of the 5-day Fellowship-wrap plan was to dispatch the cross-state CPI 2015 5-state extension (CO/IL/WA/FL/NC, ~$15). Dan picked Day 2 over Day 1 worktree pruning at the opening fork. Before authorizing the dispatch, Dan paused to ask about (a) which providers are being used and (b) a structural review of the dispatch: how many cells are de facto vs de jure, the cell-type histogram, and what the 6 chunks actually cover.

The provider check confirmed both Anthropic (`claude-opus-4-7`) and OpenAI (`gpt-5.2-2025-12-11`) in parallel per chunk per run — identical to Round 1. The structural review surfaced a 93-cell roster across the 6 default chunks: 90.3% de-jure, 78.5% BinaryCell, with the structured ~22% (Int/Float/Decimal/Enum/Set/Graded/FreeText/TimeThreshold) being where Round 1's vocab schism lived. A side-channel prompt-presence audit identified 11 of 93 prompts (12%) that lack explicit response-format clarification — Dan's "we need to make sure agents are told to respond in the expected format" instinct made operational.

Dan then asked for a plan combining Path (c) helper-side vocab fix + Path (b) prompt hygiene cleanup *before* the $15 dispatch, plus a formal breakdown report with more detail. Two artifacts landed: the chunk inventory report (results/) and the 5-phase pre-dispatch hygiene plan (plans/). RESEARCH_LOG updated; no code or YAML changes yet — Phase 1 + Phase 2 execution is for the next session under TDD discipline.

## Topics Explored

- Handoff resumption: leave-behind-prep convo's 5-day plan and the two load-bearing reframings (SMR-as-canonical, Anna Karenina)
- Day 1 vs Day 2 fork (worktree pruning vs cross-state dispatch); Dan picked Day 2
- Provider configuration — `claude-opus-4-7` + `gpt-5.2-2025-12-11`, both flagships in parallel
- Round 1 cost ledger ($14.43 / $15) and per-state cost range ($2.48–$3.79) for predicting Round 2
- Tension between cross-state RESEARCH_LOG's "vocab-fix-first" recommendation and leave-behind-prep convo's "5-state extension first" override — verified the override is intentional via Path 2-modified reasoning in the failure-mode doc §"My recommendation"
- Structural inventory: chunk-level + cell-type-level breakdown of the 6 default chunks
- Combined-axis row inventory (3 rows, 6 cells in the 6 default chunks)
- Prompt-presence audit: 93/93 with prompts, 82/93 with format-clarification keywords, 11/93 underspecified
- Grouping the 11 underspecified prompts by failure mode (4 terse/fragmentary, 6 CPI rubric language only, 1 instruction-shaped without enum/unit)
- Distinction between Round 1's documented failure mechanism (helper-YAML vocab schism, 9 cells) and the prompt-hygiene gap (11 cells) — partial overlap, different failure modes
- TDD sequence for both the helper update (existing test surface) and the prompt YAML update (new regression test gating future drift)
- Risks of changing experimental input mid-experiment (mitigation: semantics-preserving diff review)

## Provisional Findings

- **The 6 default chunks are overwhelmingly de-jure** (90.3% legal; 9.7% practical via combined-axis rows). This is by design — CPI-2015 C11 scores a de-jure rubric, so the chunk roster reflects that.
- **78.5% of cells are BinaryCell.** The structured 21.5% is where Round 1's vocab schism lived; specifically IND_199 (IntCell, 4-of-5 miss) + IND_207 (EnumCell, 5-of-5 miss).
- **The 11 underspecified prompts are a *different* failure mode than Round 1's documented misses.** Round 1's helper-YAML vocab schism happened on prompts that DO carry format hints ("Answer in months as an integer", "Answer with one of: YES, MODERATE, NO"); the underspecified-11 didn't cause Round 1's documented failures. Phase 2 prompt cleanup is forward hygiene, not Round 1 debt.
- **Phase 1 helper fix predicted to lift Round 1 re-audit from 15/30 to ~19/30** (50% → ~63%) per failure-mode doc Trend 1. The lift comes from IND_199 (4 states flip) + IND_207 (1 state flips); TX IND_199 (previously accidentally-matching) flips the other way.
- **Anna Karenina discipline holds.** This plan stays inside the CPI-2015 C11 module + the prompt YAML — no state-agnostic refactor sneaks in.
- **Cost discipline.** Round 2 envelope same ~$15. Anchor-first dispatch shape repeats Round 1's working pattern (NY first, then 4-parallel for the rest).

## Decisions Made

- **Plan to combine (b) + (c) before dispatching.** 5 phases: helper vocab fix ($0) → prompt hygiene ($0) → Round 1 re-audit ($0) → Round 2 dispatch (~$15) → N=10 writeup ($0). See [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md).
- **Phase 2 is semantics-preserving.** Closing sentences added per cell-type template; diff review with Dan before commit. Per-prompt exit ramp if any change risks shifting semantics.
- **Provider config unchanged.** Round 2 uses same `claude-opus-4-7` + `gpt-5.2-2025-12-11` as Round 1. Single-provider cost-halving rejected as it breaks σ_noise comparability.
- **Round 1 stored data gets re-projected post-Phase-1.** The audit script will produce a new Round 1 baseline (~63% predicted) before Round 2 dispatches — captured as a checkpoint in Phase 3.
- **Convo name + artifacts committed under one finish-convo.** This convo, the inventory report, the plan, and the RESEARCH_LOG update all land in one commit.

## Results

- [`../results/20260606_cpi_2015_c11_chunk_inventory.md`](../results/20260606_cpi_2015_c11_chunk_inventory.md) — 6-chunk structural inventory (de-jure/de-facto count, cell-type histogram, per-chunk themes + row lists, full text of the 11 underspecified prompts with grouping, implications for the dispatch). Includes manifest notes inline and combined-axis row provenance.

## Open Questions

- **CO/IL/WA/FL/NC bundle pre-flight.** Do all 5 Round 2 states have multi-file statute bundles? TX 2015's 1-file bundle was the source of Round 1's Trend 4 over-projection. Pre-Phase-4 check.
- **Will Phase 1's IND_199 IntCell-months path generalize across CO/IL/WA/FL/NC?** Round 1 showed 4 of 5 states extracted months cleanly (NY/WI/OH/CA at 24mo; TX at 12mo). N=10 will tell.
- **Will Trend 5 (CPI more generous on audits than our extraction) reproduce at N=10?** If yes, footnote it as known CPI scoring artifact in the projection mapping doc. If no, surface as state-specific extraction gap.
- **Phase 2 prompt-diff review process.** Dan will review the 11 prompt edits before commit. Does the diff review want a side-by-side template or just the raw YAML diff?

## Next Steps

- Fresh session (per Nori plan-then-fresh-session discipline) executes [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md) under TDD.
- Pre-execution checklist (in the plan) gates Phase 1 start.
- Phase 4 cost authorization (~$15) must be re-confirmed by Dan at execution time, even though this convo discussed the budget.

# 20260521 — Tier-1 direct-read legal-axis plan: executed end-to-end

**Date:** 2026-05-21 (UTC; session opened late 2026-05-20, ran past midnight)
**Branch:** extraction-harness-brainstorm
**Machine:** Dans-MacBook-Air (API keys sourced from `/Users/dan/code/lobby_analysis/.env.corporate`)
**Predecessor convo:** [`20260520_tier_0_direct_read_execution.md`](20260520_tier_0_direct_read_execution.md)
**Plan executed:** [`../plans/20260520_tier_1_direct_read_legal_axis.md`](../plans/20260520_tier_1_direct_read_legal_axis.md) — all 8 steps
**Writeup:** [`../results/tier_1/20260520_tier_1_legal_axis_writeup.md`](../results/tier_1/20260520_tier_1_legal_axis_writeup.md)

## Summary

Executed the Tier-1 plan in full: resolved the 6 CPI-2015 C11 de-jure chunks
(Step 1), wrote the value-coercion fix + legal-axis roster filter + σ_noise
metric test-first (Steps 2/3/5/6, TDD), built the 36-dispatch runner (Step 4),
ran it (`[claude-opus-4-7, gpt-5.2] × 6 chunks × 3 runs`, OH 2025, 84 legal
cells), and wrote the writeup (Step 7). Session cost **$2.94** (ceiling $10).

The four plan Questions were settled with the user up front: keep temp at the
SDK default (1.0 — Tier-0 actually ran at default, not temp-0 as the plan's Q1
assumed); N=3; Tier-1 scope ends at σ_noise (no CPI comparison); keep the $10
ceiling.

Headline result: legal-axis direct-read holds at chunk scale. **σ_noise: Claude
85.7 % cells stable, GPT 73.8 %** (both deflated by unpinned-enum label churn).
The Tier-0 string/int bug is gone — the coercion fix works. But the run
surfaced **3 new error classes** and reproduced Tier-0's abstention-calibration
problem at chunk scale.

## Topics explored

- Step 1: routing CPI items IND_196/197/199/201/203/207 through the §10.1
  rename resolver and `build_chunks()` to the 6 chunks.
- The value-typing fix (`_coerce_scalar_value`) and where it does / does not
  reach.
- Inter-run agreement design — stable / value-unstable / scoreability-unstable
  / incomplete; numeric spread.
- Whether legal-axis direct-read is ready to scale to 15 chunks / multi-vintage.

## Provisional findings

- **Coercion fix works (criterion 3 met).** Zero Tier-0 string/int errors.
  Claude scored all 4 `DecimalCell`s in `registration_thresholds` by emitting
  JSON strings → `_coerce_scalar_value` converts `str → Decimal`.
- **3 new error classes, reported not patched** (per plan discipline):
  - **A — `int → Decimal` strict rejection.** Model emits bare JSON `50`;
    strict-mode `DecimalCell` requires a `Decimal` instance. The Step-2 prompt
    nudge ("emit JSON numbers") *caused* this — GPT obeyed and walked into it.
  - **B — dict-shape cell fed a scalar.** `TimeThresholdCell`
    (`lobbyist_registration_threshold_time_percent`) — the plan's anticipated
    IND_197 dict-shape failure; Claude, all 3 runs.
  - **C — non-optional `FreeTextCell` fed `null`.** Conditional
    `*_cadence_other_specification` rows; both models, 100 % of runs, correctly
    emit `null` for a not-applicable cell. A schema gap, not a model error.
- **σ_noise is chunk-correlated, not IID per cell.** `principal_spending_report`
  shows a block of 5–6 cells flipping together when one run misreads the
  section. Effective sample size ≈ chunks × runs, not cells × runs.
- **Abstention-calibration problem reproduced at scale.** GPT abstains on the
  *entire* `registration_thresholds` chunk — consistently, with substantive
  reasons: OH triggers lobbyist status qualitatively ("main purpose"), not by
  dollar threshold. Claude encodes the qualitative-trigger case as `0`. Both
  defensible; the mapping doc favors `0`. This is the single largest source of
  cross-model divergence.
- **Cross-model agreement 85 %** (63/74 both-scored run-1 cells). Most
  disagreements are unpinned-enum label format; ~6 are substantive `True`/`False`
  reads — the verifier's core workload.
- **`lobbyist_registration_renewal_cadence` is mis-typed.** OH updates 3×/year
  (Jan/May/Sept per §101.72(B)); the `IntCell` "months" encoding has no clean
  value. Both models wrong/unstable — a compendium-schema finding.

## Decisions made

- Plan Questions 1–4 settled before the run (see Summary).
- New error classes A/B/C reported in the writeup, **not patched** — per the
  plan's stop-and-report discipline ("the failure mode is the deliverable").
- Verdict: legal-axis direct-read is "qualified yes" for scaling — 3 small
  schema/adapter fixes + enum-domain pinning + an abstention policy must land
  first. None are architectural.

## Deviations from the plan (all documented in the writeup)

- Tier-1 owns its dispatch wrappers (`max_tokens` 16384 vs Tier-0's 4096 — the
  30-cell chunk needs ~10K output tokens) and its system prompt.
- `DecimalCell` coercion targets `Decimal`, not the plan's `float` (strict mode).
- `GradedIntCell` coercion tested with on-grid `"50"`, not the plan's `"2"`
  (grid validator); a plain `IntCell` covers `"2" → int`.
- Steps 2/3/5 landed as 3 commits (coercion / runner / tests), each leaving the
  suite green, rather than the plan's per-step commits. TDD order honored.
- IND_201 row-ID drift: mapping-doc working name
  `lobbyist_spending_report_includes_compensation` → live
  `lobbyist_spending_report_includes_total_compensation` (same chunk).

## Results

- [`../results/tier_1/20260520_tier_1_legal_axis_writeup.md`](../results/tier_1/20260520_tier_1_legal_axis_writeup.md) — full writeup + verdict.
- `../results/tier_1/<model>__<chunk>__run<N>.json` — 36 dispatch files, each
  with provenance, legal roster, raw response, parsed cells, errors.

## Commits this session

- `aa970a5` — Step 2: `_coerce_scalar_value` in `_instantiate_cell` (tier-0 script).
- `5a467d6` — Step 4: `scripts/tier_1_direct_read_legal_axis.py` runner.
- `17a7a02` — Step 6: `tests/test_tier_1_legal_axis.py` (18 behavior tests).
- `f3931e2` — Step 7: writeup + 36 result JSONs.

Test suite: 515 passed, 3 `test_pipeline.py` baseline failures (unrelated,
missing CA portal-snapshot fixture), 8 skipped.

## Open questions / next steps

1. **Three schema/adapter fixes before scaling** (Tier-2 candidates): extend
   `_coerce_scalar_value` to `int → Decimal` (A); make conditional
   `FreeTextCell` rows optional or give them an N/A encoding (C); give
   dict-shape `value` an explicit per-cell-class schema or prompt shape (B).
2. **Pin enum domains** (`enum_domains.py`) for the unpinned `EnumCell` /
   `EnumSetCell` rows — otherwise σ_noise and cross-model agreement undercount
   semantically-identical answers.
3. **Abstention-calibration policy** — the qualitative-trigger case (`0` vs
   abstain). The Phase-2 verifier cannot be designed without it.
4. **`lobbyist_registration_renewal_cadence` row type** — `IntCell` months is a
   poor fit for enumerated-date cadences; flag to the compendium owner.
5. CPI published-score comparison still deferred to when
   `phase-c-projection-tdd`'s projection functions land.

## Session mechanics / caveats for the next agent

- API keys came from `/Users/dan/code/lobby_analysis/.env.corporate` (mixed
  file — load only `^[A-Za-z_]+=` lines). They are live and have appeared in
  session transcripts across multiple sessions now — **worth rotating.**
- The runner is resumable: re-running skips any `(model, chunk, run)` triple
  that already has a result JSON. This run completed in one pass; resume was
  not exercised live but the skip predicate is unit-tested.
- Claude pricing uses placeholder opus-4-6 rates (Tier-0 caveat still stands);
  cost figures are order-of-magnitude.

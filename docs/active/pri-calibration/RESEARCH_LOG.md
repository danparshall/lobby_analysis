# Research Log: pri-calibration

Created: 2026-04-17
Purpose: Calibrate the LLM scoring pipeline against PRI 2010 human-rater scores by scoring state lobbying statutes (2010 vintage) and iterating the scorer prompt until agreement reaches a defined target; then apply the calibrated prompt to current (2026-vintage) statutes to produce defensible 2026 state scores for the PRI accessibility + disclosure-law rubrics.

This branch was cut from `scoring` (not `main`) because it continues the scoring work — the pilot finding ("we're scoring portal summaries of the law, not the law itself") motivated a pivot to statute-based scoring, but the underlying pipeline is the same. Branch-off-main was considered and rejected: orthogonality was the original concern, but sharing pipeline scaffolding doesn't compromise intellectual orthogonality.

Originating discussion: `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md` (on the `scoring` branch, now also visible in this worktree since we branched from scoring).

## Trajectory

Newest first.

- **2026-04-17 — Branch kickoff, retrieval architecture decided.** Read the pri-ground-truth-calibration plan. Audited the PRI 2010 methodology: **no published inter-rater reliability** — PRI used single-coder preliminary analysis + state-official review (34/50 responded; 31 confirmed or corrected; 16 never validated externally). Implication: the plan's "match PRI IRR" convergence target doesn't exist and has to be set by discussion. Retrieval architecture simplified: **Justia serves both 2010 and current statutes** via `/codes/<state>/<year>/` stable URLs, unifying historical + current retrieval into one pipeline. Coverage is uneven across states (e.g., Colorado's earliest Justia year is 2016 — which, per Dan's Wayback check, actually reflects that CO didn't have the whole code up in 2010, not a Justia gap). Calibration-eligible states will be those with Justia coverage within ±2 years of 2010; asymmetric vintage delta is logged so we can distinguish "pre-2010 (may miss late-2009 changes)" from "post-2010 (may include reforms PRI didn't see)." Detail: `convos/20260417_calibration_kickoff.md`.

## Plans

- `plans/20260417_pri_ground_truth_calibration.md` — master calibration plan (7 phases). Carried from `scoring` branch; amended with the no-IRR finding, Justia-unified retrieval architecture, ±2 year vintage tolerance, and chapter-level availability check.
- `plans/20260417_statute_retrieval_module.md` — scoped sub-plan for the retrieval module + 50-state audit (execution slice for the master plan's Phase 1). TDD'd.

## Convos

- 2026-04-17 — `convos/20260417_calibration_kickoff.md` — Branch kickoff. Key decisions: no-IRR target (PRI didn't publish one; will be set by discussion); Justia-unified retrieval; ±2 year symmetric tolerance with asymmetric direction logging; chapter-level availability check; branch cut from `scoring`, not `main`.

## Results

(None yet. First artifact will be the 50-state Justia audit CSV + methodology note from Phase 1.)

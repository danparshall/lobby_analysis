# Research Log: pri-calibration

Created: 2026-04-17
Purpose: Calibrate the LLM scoring pipeline against PRI 2010 human-rater scores by scoring state lobbying statutes (2010 vintage) and iterating the scorer prompt until agreement reaches a defined target; then apply the calibrated prompt to current (2026-vintage) statutes to produce defensible 2026 state scores for the PRI accessibility + disclosure-law rubrics.

This branch was cut from `scoring` (not `main`) because it continues the scoring work — the pilot finding ("we're scoring portal summaries of the law, not the law itself") motivated a pivot to statute-based scoring, but the underlying pipeline is the same. Branch-off-main was considered and rejected: orthogonality was the original concern, but sharing pipeline scaffolding doesn't compromise intellectual orthogonality.

Originating discussion: `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md` (on the `scoring` branch, now also visible in this worktree since we branched from scoring).

## Trajectory

Newest first.

- **2026-04-17/18 — Phase 1 complete: Justia retrieval audit, 49/50 states eligible for 2010 calibration.** Session opened with a Phase 0 methodology audit of PRI 2010 (no published IRR — single-coder + state-official review; convergence target to be set post-baseline), pivoted the retrieval architecture from Wayback-primary to **Justia-unified** (stable `/codes/<state>/<year>/` URLs serve both 2010 and 2026 vintage). Cloudflare's JS challenge blocks curl + WebFetch + subagent dispatch; added Playwright with **fresh browser per request** as the working path (long-lived contexts get progressively challenged and never clear). TDD'd the Justia client + audit module + orchestrator `audit-statutes` subcommand — 26 new tests red-then-green, 35 total passing. Ran the 50-state audit: **49 eligible for 2010 calibration, CO the only exclusion** (earliest Justia year = 2016, out of ±2 tolerance), all 50 eligible for 2026-scoring; 34 states at exact 2010, 15 at 2009 (pre-preferred tie-break used, delta=-1), 0 post-2010. Responder overlap: 33 of 34 PRI responders eligible. Validates the plan's Phase 1 go-gate (>=40) by a wide margin — no Wayback / HeinOnline fallback needed. Phase 2 handoff plan at `plans/20260418_phase2_statute_retrieval_and_baseline.md`. Detail: `convos/20260417_calibration_kickoff.md`.

## Plans

- `plans/20260417_pri_ground_truth_calibration.md` — master calibration plan (7 phases). Carried from `scoring` branch; amended with the no-IRR finding, Justia-unified retrieval architecture, ±2 year vintage tolerance, and chapter-level availability check.
- `plans/20260417_statute_retrieval_module.md` — scoped sub-plan for the Phase 1 retrieval module + 50-state audit. **Complete** — TDD'd and executed 2026-04-17/18.
- `plans/20260418_phase2_statute_retrieval_and_baseline.md` — **next action.** Handoff for the next agent: Phase 3 calibration-subset selection, Phase 2 statute-text retrieval, and baseline scoring run. Originating convo: `convos/20260417_calibration_kickoff.md`.

## Convos

- 2026-04-17 — `convos/20260417_calibration_kickoff.md` — Branch kickoff + Phase 1 execution. Key decisions: no-IRR target (will be set post-baseline by discussion); Justia-unified retrieval; ±2 year symmetric tolerance with asymmetric direction logging; branch cut from `scoring`, not `main`; Playwright with fresh-browser-per-request clears Cloudflare. Phase 1 result: 49/50 states eligible for calibration; CO excluded.

## Results

- 2026-04-18 — `results/20260418_justia_retrieval_audit.csv` — one row per state with target-year eligibility + Justia vintage coverage.
- 2026-04-18 — `results/20260418_justia_retrieval_audit.md` — methodology note, summary statistics, CO exclusion analysis, CSV schema reference.

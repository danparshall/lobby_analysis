# Research Log: pri-calibration

Created: 2026-04-17
Purpose: Calibrate the LLM scoring pipeline against PRI 2010 human-rater scores by scoring state lobbying statutes (2010 vintage) and iterating the scorer prompt until agreement reaches a defined target; then apply the calibrated prompt to current (2026-vintage) statutes to produce defensible 2026 state scores for the PRI accessibility + disclosure-law rubrics.

This branch was cut from `scoring` (not `main`) because it continues the scoring work — the pilot finding ("we're scoring portal summaries of the law, not the law itself") motivated a pivot to statute-based scoring, but the underlying pipeline is the same. Branch-off-main was considered and rejected: orthogonality was the original concern, but sharing pipeline scaffolding doesn't compromise intellectual orthogonality.

Originating discussion: `docs/active/scoring/convos/20260417_pilot_and_calibration_pivot.md` (on the `scoring` branch, now also visible in this worktree since we branched from scoring).

## Trajectory

Newest first.

- **2026-04-18/19 — Phase 2 + Phase 3 scaffolding complete: rollup spec, calibration harness, statute-run orchestration, multi-run reporting.** Phase 2a had already landed the statute retrieval pipeline + fixtures for CA/TX/WY/NY/WI. This session closed Phase 2b and Phase 3 task 2, then surfaced and fixed two additional Phase 3 TDD gaps. Key finding: the plan's Phase 2b edge case "group by sub_component and sum" as the PRI rollup rule was **wrong** — PRI's published B/C/D/E aggregates use non-trivial rules (B1/B2 reverse, C/D gate-only, E higher-of-principal-or-lobbyist with F/G summed, J independent, h-frequency collapsed). Pinned this down from PRI paper §III.B-E + §IV.7-8 line citations into `results/20260419_pri_rollup_rule_spec.md` — doc is now the authoritative rollup reference for both `pri-calibration` and `pri-2026-rescore`'s eventual 50-state reporting. 9 methodology differences between our setup and PRI's 2010 protocol documented in the spec (coder type, sharpened guidance, Q8 holistic, null propagation, etc.). Added four new orchestrator subcommands: `calibrate-prepare-run` / `calibrate-finalize-run` (statute-path runs, 2 PRI rubrics only, new `StatuteRunMetadata` pydantic model, `coverage_tier="clean"`), `calibrate-analyze-consistency` (statute-path self-consistency; refactored `compute_consistency` to take a path dict so portal + statute reuse one core), and multi-run `calibrate` (accepts N run-ids, emits per-run sections + cross-run variance table — adjudicator deferred to Phase 4). 130/130 tests green. Commits `f435984` through `28ebba7`. Phase 3 scaffolding complete; live Phase 3 baseline dispatch is the next exploratory step. Detail: `convos/20260419_phase2b_phase3_scaffolding.md`.

- **2026-04-17/18 — Phase 1 complete: Justia retrieval audit, 49/50 states eligible for 2010 calibration.** Session opened with a Phase 0 methodology audit of PRI 2010 (no published IRR — single-coder + state-official review; convergence target to be set post-baseline), pivoted the retrieval architecture from Wayback-primary to **Justia-unified** (stable `/codes/<state>/<year>/` URLs serve both 2010 and 2026 vintage). Cloudflare's JS challenge blocks curl + WebFetch + subagent dispatch; added Playwright with **fresh browser per request** as the working path (long-lived contexts get progressively challenged and never clear). TDD'd the Justia client + audit module + orchestrator `audit-statutes` subcommand — 26 new tests red-then-green, 35 total passing. Ran the 50-state audit: **49 eligible for 2010 calibration, CO the only exclusion** (earliest Justia year = 2016, out of ±2 tolerance), all 50 eligible for 2026-scoring; 34 states at exact 2010, 15 at 2009 (pre-preferred tie-break used, delta=-1), 0 post-2010. Responder overlap: 33 of 34 PRI responders eligible. Validates the plan's Phase 1 go-gate (>=40) by a wide margin — no Wayback / HeinOnline fallback needed. Phase 2 handoff plan at `plans/20260418_phase2_statute_retrieval_and_baseline.md`. Detail: `convos/20260417_calibration_kickoff.md`.

## Plans

- `plans/20260417_pri_ground_truth_calibration.md` — master calibration plan (7 phases). Carried from `scoring` branch; amended with the no-IRR finding, Justia-unified retrieval architecture, ±2 year vintage tolerance, and chapter-level availability check.
- `plans/20260417_statute_retrieval_module.md` — scoped sub-plan for the Phase 1 retrieval module + 50-state audit. **Complete** — TDD'd and executed 2026-04-17/18.
- `plans/20260418_phase2_statute_retrieval_and_baseline.md` — **next action.** Handoff for the next agent: Phase 3 calibration-subset selection, Phase 2 statute-text retrieval, and baseline scoring run. Originating convo: `convos/20260417_calibration_kickoff.md`.

## Convos

- 2026-04-19 — `convos/20260419_phase2b_phase3_scaffolding.md` — Phase 2b calibration harness + Phase 3.2 orchestration + Phase 3.3 gap-fill (statute-aware consistency + multi-run calibrate). Rollup rule derived from paper; 130/130 tests green; scaffolding complete for Phase 3 live baseline.
- 2026-04-18 — `convos/20260418_phase2_kickoff_and_subset_selection.md` — Phase 2 kickoff: locked the 5-state subset (CA/TX/WY/NY/WI), committed manifest policy, rate-limit split, scorer-prompt source flag; Phase 2a architectural redesign from per-title slugs to curated `LOBBYING_STATUTE_URLS`.
- 2026-04-17 — `convos/20260417_calibration_kickoff.md` — Branch kickoff + Phase 1 execution. Key decisions: no-IRR target (will be set post-baseline by discussion); Justia-unified retrieval; ±2 year symmetric tolerance with asymmetric direction logging; branch cut from `scoring`, not `main`; Playwright with fresh-browser-per-request clears Cloudflare. Phase 1 result: 49/50 states eligible for calibration; CO excluded.

## Results

- 2026-04-20 — `results/20260420_ecosystem_notes.md` — civic-tech ecosystem reconnaissance (OpenStates scrapers/spatula/core, Free Law Project). No adoption decisions; notes for future per-state-scraping + entity-resolution work.
- 2026-04-19 — `results/20260419_pri_rollup_rule_spec.md` — line-cited PRI 2010 sub-aggregate rollup rule for disclosure law + accessibility. 9 methodology differences from PRI's original protocol documented. Authoritative for both `pri-calibration` agreement checks and `pri-2026-rescore`'s eventual 50-state reporting.
- 2026-04-18 — `results/20260418_justia_retrieval_audit.csv` — one row per state with target-year eligibility + Justia vintage coverage.
- 2026-04-18 — `results/20260418_justia_retrieval_audit.md` — methodology note, summary statistics, CO exclusion analysis, CSV schema reference.
- 2026-04-18 — `results/statute_manifests/<STATE>/<YEAR>/manifest.json` — committed provenance records for the 5-state calibration subset (CA/2010, TX/2009, NY/2010, WI/2010, WY/2010).

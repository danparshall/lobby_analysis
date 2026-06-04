# Research Log: wi-ralph-cpi-renewal-cadence

Created: 2026-06-04
Purpose: Phase B Ralph trial — first-row-by-hand iteration on `lobbyist_registration_renewal_cadence` (CPI 2015 IND_199, WI=MODERATE) to surface what is and isn't tractable about row-level rubric-anchored iteration before designing any automation. Outcomes feed (a) the automation-level decision (post-iteration), (b) the deferred Phase A pre-flight YAML audit scope (every fix this row needs in YAML is a fix Phase A needs to know how to make at scale).

Plan: [`plans/20260604_phase_b_ralph_renewal_cadence.md`](plans/20260604_phase_b_ralph_renewal_cadence.md)

Upstream lineage (this branch exists because of):
- [`wi-tier1-direct-read` Commit 3 convo](https://github.com/danparshall/lobby_analysis/blob/wi-tier1-direct-read/docs/active/wi-tier1-direct-read/convos/20260604_wide_pass_commit3_redispatch_and_audit.md) — Ralph loop brainstorm seeded.
- [`wi-tier1-direct-read` 9-rubric oracle audit](https://github.com/danparshall/lobby_analysis/blob/wi-tier1-direct-read/docs/active/wi-tier1-direct-read/results/20260604_oracle_granularity_audit.md) — confirmed CPI 2015 C11 (not PRI 2010) as the per-item × per-state oracle source.

---

## Session history (newest first)

### 2026-06-04 (evening) — Phase B kickoff: branch created, plan written, no code/dispatch
Convo: [`convos/20260604_phase_b_kickoff.md`](convos/20260604_phase_b_kickoff.md) · Plan: [`plans/20260604_phase_b_ralph_renewal_cadence.md`](plans/20260604_phase_b_ralph_renewal_cadence.md)
- **Branch created** from main (`28f3e47`) as `wi-ralph-cpi-renewal-cadence` worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-ralph-cpi-renewal-cadence/`. Symlinked `data → /Users/dan/data/lobby_analysis` and `.env.local → /Users/dan/code/lobby_analysis/.env.local` per CLAUDE.md multi-terminal data discipline. Seeded `docs/active/<branch>/{convos,plans,results}/`.
- **Plan written** at `plans/20260604_phase_b_ralph_renewal_cadence.md`. Self-contained Phase B Ralph plan targeting `lobbyist_registration_renewal_cadence` (CPI IND_199, WI=MODERATE, cell type `Optional[int_months]`). Plan covers: pre-flight reads (6 docs spanning this branch + wi-tier1-direct-read), target/oracle/starting-state spec, 3 dispatch-mechanism options (A=add `--chunks` flag $0.05-0.10/iter recommended; B=full re-dispatch ~$2.50/iter at chunk-cost averages; C=single-row script deferred), iteration loop (read state → compare oracle → decide change → edit YAML → re-dispatch → audit → log), results-logging schema, 4 stopping conditions (convergence; $5 budget hit; Dan-calls-it; structural-finding), edge cases (cell-type-vs-vocab is structural not just lexical; GPT vs Claude unit-axis behavior; cross-vintage drift; CPI data-quality glitches; chunk-mate row spillover; **branch starting state — wide-pass YAML lives on wi-tier1-direct-read, NOT main**), 4 pre-execution Dan questions, what's out of scope, optional test plan if Option A's dispatcher tweak is taken.
- **No code, no dispatch, no API spend** this session, per Dan's mid-session instruction: *"don't actually code Ralph up, just create a plan and then finish-convo."* This branch's cumulative spend ledger starts at $0.00.
- **Implementing-session shape:** agent reads plan + 6 pre-flight reads cold; confirms Dan's answers to the 4 questions (branch starting state, dispatch mechanism, vintage check, stopping rule); then iteration 0. Plan flags the merge step (`git merge wi-tier1-direct-read`) as the most likely first-action requirement since `compendium/source_quotes.yaml` on main lacks the wide-pass populated prompts.
- **Next:** implementing session. Plan deliberately stops short of execution — the first dollar of API spend waits on Dan's go-ahead to the dispatch mechanism choice.

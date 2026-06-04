# Phase B Ralph kickoff — branch + plan for renewal_cadence row

**Date:** 2026-06-04 (evening, immediately after the 9-rubric oracle-granularity audit landed on wi-tier1-direct-read)
**Branch:** wi-ralph-cpi-renewal-cadence
**Plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md)

## Summary

Kickoff session for the Phase B Ralph branch. No code, no dispatch — per Dan's mid-session instruction *"don't actually code Ralph up, just create a plan and then finish-convo."* The branch was created from `main` (commit `28f3e47`), data symlink + .env.local symlink added per CLAUDE.md multi-terminal data discipline, docs structure seeded (`convos/`, `plans/`, `results/`). A self-contained Phase B Ralph plan was written targeting `lobbyist_registration_renewal_cadence` (CPI 2015 IND_199, WI=MODERATE) as the first-row-by-hand iteration target.

The Phase B design and row pick come from two upstream sessions on `wi-tier1-direct-read`: the wide-pass Commit 3 audit (2026-06-04 afternoon) that diagnosed the YES/MODERATE/NO ↔ IntCell mismatch + brainstormed the Ralph loop, and the 9-rubric oracle-granularity audit (2026-06-04 evening) that confirmed CPI 2015 C11 — not PRI 2010 as the brainstorm originally recalled — is the actual per-item × per-state oracle source. Both convos are linked in the plan header for cross-branch lineage.

The plan is exploratory in character per Dan's framing: *"even if we don't get it perfect, we might be able to learn a lot about what is/n't hiccuping by inference."* Deliverable from the future implementation session is not a converged extraction; it's empirical signal about (a) what the per-iteration human-in-the-loop step looks like, (b) what kinds of prompt changes the model responds to, (c) whether convergence is achievable for this row with this oracle. Outcomes will feed the automation-level decision and the deferred Phase A pre-flight YAML audit scope.

## Topics Explored

- **Branch setup.** Created `wi-ralph-cpi-renewal-cadence` worktree off main (`28f3e47`). Symlinked `data → /Users/dan/data/lobby_analysis` and `.env.local → /Users/dan/code/lobby_analysis/.env.local`. Seeded `docs/active/wi-ralph-cpi-renewal-cadence/{convos,plans,results}/`. **Did not run setup or tests** — no code work this session; .venv installation deferred until the implementing session needs it.

- **Plan scope decision.** Single row, single state, single vintage. Specifically `lobbyist_registration_renewal_cadence` per audit recommendation. Reasoning: (a) it's the cleanest CPI-readable wide-pass regression; (b) WI's CPI IND_199 oracle value (MODERATE) is unambiguous; (c) the failure mode (YES/MODERATE/NO ↔ IntCell mismatch) is exactly the kind of fix Phase A pre-flight will need to know how to make at scale — so iteration findings are directly portable.

- **Dispatch-granularity question raised in plan.** Per-iteration cost depends on whether the dispatcher gets a `--chunks` filter argument (~$0.05-0.10 per iter under Option A) or we re-dispatch all 6 chunks (~$0.30-0.40 per iter — the Commit 3 estimate, but actually ~$2.50 per iter at chunk-cost averages). The plan recommends Option A but flags as a Dan-decides question. Under Dan's $3-5 budget, Option A gives ~10-30 iterations; Option B gives ~2-3.

- **Branch starting-state question raised in plan.** The wide-pass YAML lives on `wi-tier1-direct-read`, NOT on `main`. This new branch was forked from `main`, so its `compendium/source_quotes.yaml` is in the pre-wide-pass state (only 17 narrow-pass rows populated). The implementing agent will need to `git merge wi-tier1-direct-read` before iteration 0, or branch-base needs to change. Flagged as Q1 for Dan in the plan.

- **Cross-branch reference shape.** The plan references upstream convos + the audit deliverable via paths on `wi-tier1-direct-read` (which lives at `/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/`). Used GitHub permalink-style for cross-branch doc references where appropriate; relative paths within this branch for in-branch artifacts.

- **NOT discussed this session:** Ralph automation design, stopping-rule heuristics beyond "Dan calls it", multi-row scaling, cross-vintage validation, schema-fix decisions. All deferred to post-iteration findings.

## Provisional Findings

- **Branch is ready for the next session's implementing agent.** Worktree exists, symlinks resolve, docs structure seeded, plan written. Implementing agent's first action should be confirming Dan's answers to the 4 plan-level questions (branch starting state, dispatch mechanism, vintage check, stopping rule), then iteration 0.

- **Plan length is intentional.** Most of the plan's bulk is cross-branch context (the audit's role, the Phase A/B split, the wide-pass backstory). A returning agent skips to "Operational mechanics" + the iterations log; a cold agent reads the whole thing once.

- **No retroactive doc edits.** The Commit 3 convo recorded its tentative recollections about PRI 2010 in good faith; the audit corrects them in-place on wi-tier1-direct-read rather than editing Commit 3. This branch's plan references both — the original recollection + the corrected reading — for full provenance.

## Decisions Made

- **Branch name:** `wi-ralph-cpi-renewal-cadence` (Dan's chosen option, vs alternatives `phase-b-ralph-trial` and `ralph-cpi-c11`). Specific-to-first-row naming implies future row trials may get their own branches.

- **No code or dispatch this session.** Per Dan's mid-session pivot: *"don't actually code Ralph up, just create a plan and then finish-convo."*

- **Plan is self-contained for handoff.** Implementing agent should be able to start cold from the plan + the 6 pre-flight reads it names.

- **Phase A pre-flight YAML audit stays deferred.** The Ralph first-row iteration goes against the unpatched YAML deliberately, per the wi-tier1-direct-read Commit 3 convo's "even if we don't get it perfect, we might be able to learn a lot about what is/n't hiccuping by inference" framing.

## Results

- **Worktree created:** `/Users/dan/code/lobby_analysis/.worktrees/wi-ralph-cpi-renewal-cadence/`. Symlinks: `data/, .env.local`. Branch: `wi-ralph-cpi-renewal-cadence` (off main `28f3e47`). Setup not run (no Python execution required this session).
- **Phase B Ralph plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md) — full plan with pre-flight reads, target/oracle/starting-state spec, operational mechanics (3 dispatch options), iteration loop, results-logging schema, edge cases, 4 pre-execution Dan questions, what's out of scope, testing details, implementation details.
- **No API spend** (no dispatch). This branch's cumulative spend ledger starts at $0.00.

## Open Questions

(All deferred to the implementing session.)

1. **Branch starting state.** Merge `wi-tier1-direct-read` into this branch before iteration 0 (default), or branch off a different commit?

2. **Dispatch mechanism.** Option A (add `--chunks` flag — small 10-min code change, ~$0.05-0.10/iter), Option B (no code touch, ~$0.30-0.40/iter actually ~$2.50/iter at chunk-cost averages), or Option C (single-row script, deferred)?

3. **Vintage check first?** Does iteration 0 include manual confirmation that WI's current §13.62 renewal cadence matches the 2015 version CPI scored? ~5-10 min web research.

4. **Stopping rule.** Default = Dan-calls-it. More concrete metric possible (e.g., "stop when 4/6 runs project to MODERATE") but not pre-committed.

## Session meta — plan-not-code as the right pivot

Dan's mid-session course correction ("don't actually code Ralph up, just create a plan and then finish-convo") matched the Commit 3 convo's pattern: I was about to start spending money + dispatching infrastructure before the human-in-the-loop design was settled. The plan-not-code pivot defers the first dollar of spend until Dan has read the plan and made the 4 operational calls (branch state, dispatch mechanism, vintage check, stopping rule). This is the same shape as the Commit 3 brainstorm — "do NOT implement Ralph without discussion" — applied at the planning-vs-execution boundary rather than the design-vs-planning one.

The plan also surfaces something that wasn't visible in the brainstorm: the new branch was forked from `main`, but the failure mode lives on `wi-tier1-direct-read`. Without the merge step, iteration 0 would start against the wrong YAML state. Worth catching in the plan rather than the implementing agent's first dispatch.

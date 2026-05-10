# Opheim Cross-Validation — Kickoff and Worktree Setup

**Date:** 2026-05-10
**Branch:** cogel-extraction

## Summary

Resume session on `cogel-extraction` after the v2 grid pipeline shipped on
2026-05-07. User's stated goal was to start Opheim 1991 cross-validation
per the existing plan at `plans/20260507_opheim_cross_validation.md`.
Session was scoped down to two deliverables: (1) move the branch from
the main checkout into an isolated worktree per the user's preference for
parallel-branch capability, (2) review the Opheim plan and surface
pushback points that should be resolved before encoder code is written.
No Opheim code was written; no paper text was read; Phase 0 of the plan
has not started.

## Topics Explored

- Worktree provisioning for an existing branch already checked out in
  the main worktree. Sequence: switch main checkout to `main`, then
  `git worktree add .worktrees/cogel-extraction cogel-extraction`.
  `.gitignore` already contained `.worktrees/` from a prior decision.
- Whether the `use-worktree` skill's `data/` symlink advice fits this
  repo. It does not: `data/compendium/{disclosure_items.csv,
  framework_dedup_map.csv}` are tracked content (committed on this
  branch), so `data/` exists naturally on checkout. The first `ln -s`
  attempt created a nested `data/data` symlink because `data/` already
  existed; removed.
- Test-baseline check on the new worktree. 328 passed, 5 skipped, 3
  failures in `tests/test_pipeline.py`. Confirmed all 3 failures
  reproduce on `main` and predate `cogel-extraction` — they fail
  because `data/portal_snapshots/CA/2026-04-13/manifest.json` is not
  present on this machine (per STATUS 2026-04-17 note: snapshots
  live only on laptop, this machine has a placeholder).
- Read of the Opheim cross-validation plan and the v2 grid
  implementation convo for trajectory context.

## Provisional Findings

- Worktree at `/Users/dan/code/lobby_analysis/.worktrees/cogel-extraction`
  is operational. `uv sync --extra dev` succeeded with 16 + 6 packages.
- The 3 pre-existing test failures are infrastructure/data absence,
  not test code defects. Right fix is `pytest.mark.skipif` for
  missing-data integration tests, but that belongs on a different
  branch.
- The Opheim plan is internally well-structured (Phase 0 lift → Phase
  1 encode → Phase 2 score → Phase 3 diagnose) but has three
  load-bearing open questions and one stale assumption that should be
  addressed before encoder code is written.

## Pushback Raised on the Plan

1. **Three load-bearing open questions** in the plan need to be
   answered from `papers/text/Opheim_1991__state_lobby_regulation.txt`,
   not assumed:
   - "Review of all reports" — does Opheim require ALL types of review
     (desk AND field AND desk-or-field), or any-of? The plan author
     leaned any-of without a paper citation.
   - `disclose_compensation_by_employer` (COGEL T29) vs
     `disclose_sources_of_income` (Opheim) — these may not actually
     overlap. Needs cell-value verification on two known states.
   - Frequency-of-reporting: Opheim sourced this from *Book of States
     1988-89*, not the Blue Book. Our T29 freq columns are from the
     Blue Book 1990. This is a known cross-source ambiguity that will
     produce real deltas not attributable to extraction error.

2. **CA/FL missing from T30** is flagged in the plan as a known issue.
   Plan currently says Phase 2 will skip them. Open question: fix the
   T30 emission bug before Opheim, or run Opheim on 45 states first to
   collect a broader signal? Argued for defer-and-fix-after — Opheim
   on 45 states will already tell us if extraction is faithful.

3. **47-state count** — plan asserts Opheim excluded MT/SD/VA. Should
   be verified from paper text. Easy step in Phase 0.

4. **Plan's "no worktree" line is now stale.** Trivial doc fix.

5. **3 pre-existing test failures** unrelated to cogel — flag-only,
   not in scope for this branch.

## Decisions Made

- Worktree created at `.worktrees/cogel-extraction`. Main checkout
  flipped to `main`. `data/` left as the natural on-branch directory
  (no symlink — only tracked content is `data/compendium/`).
- Pre-existing test failures flagged but not addressed on this branch.
- Phase 0 of the plan (read Opheim paper text + lift Table 1 scores)
  is the agreed first concrete step on resume — but session ended
  before that started.

## Results

- None this session. No code, no encoders, no scored states. Worktree
  setup and pushback surfaced; Opheim execution deferred to next
  session.

## Open Questions

All five pushback items above are open. They are the entry point for
the next session.

## Next Steps

- Resume on Phase 0: read
  `papers/text/Opheim_1991__state_lobby_regulation.txt`, identify
  Table 1 + the methodology section that defines the 22-item coding
  rules, settle the three open questions, lift the 47-state published
  scores into `data/compendium/opheim_1991_published_scores.csv`.
- Update the plan doc to remove the stale "no worktree" line.
- Then proceed to Phase 1 (encoder TDD).

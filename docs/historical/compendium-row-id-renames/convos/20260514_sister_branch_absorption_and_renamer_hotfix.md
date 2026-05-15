# 20260514 — Sister-branch absorption + renamer hotfix

**Date:** 2026-05-14
**Branch:** compendium-row-id-renames (session conducted across three sister-branch worktrees and a fresh hotfix worktree off main)

## Summary

Operational coordination session: absorb the just-merged compendium v2 row-ID
renames (PR [#10](https://github.com/danparshall/lobby_analysis/pull/10) audit
+ PR [#14](https://github.com/danparshall/lobby_analysis/pull/14) execution)
into the three sister branches called out in the rename-execution handoff —
`extraction-harness-brainstorm`, `phase-c-projection-tdd`,
`oh-statute-retrieval`. For each branch: fast-forward pull origin, merge
`origin/main` (resolving STATUS.md conflicts by keeping both branches'
session entries), run `tools/v2_update_names.py --apply`, run `pytest`,
commit as "absorb v2 row-ID renames from main", push.

The renamer's dry-run on the first sister branch surfaced a real defect
that the rename-execution session itself had not anticipated:
`docs/active/compendium-row-id-renames/convos/20260514_rename_execution.md`
line 20 intentionally quotes the OLD row ID side-by-side with the NEW one
to document the Candidate-5 substring trap (the whole reason the renamer
uses word-boundary regex), and the renamer would auto-rewrite the OLD
quotation — collapsing the example to "X (old) is a substring of X (new)"
and destroying the design rationale. Surfaced to Dan before applying;
Dan chose "apply, then manually fix per branch" for the absorption work.
The defect was then fixed on main via a separate hotfix branch
(`compendium-renamer-skip-fix`, PR [#15](https://github.com/danparshall/lobby_analysis/pull/15)),
TDD-shaped with two new tests that lock the skip-list addition in place.

A separate small process note: the `oh-statute-retrieval` merge auto-completed
with no conflicts (it's the most-skeletal of the three sister branches and
had nothing to resolve), producing a default merge-commit message rather
than the handoff-prescribed `"absorb v2 row-ID renames from main"`. Asked
Dan how to handle the message asymmetry with the other two branches; he
picked "push as-is" — the merge IS the absorption on this branch and the
default message is honest about that.

## Topics Explored

- **Three-branch absorption mechanics.** Each sister branch had its own
  shape of merge: extraction-harness had STATUS.md conflict only; phase-c
  had STATUS.md conflicts in two regions (Active Research Lines table +
  Recent Sessions log) plus a 3-commits-behind-origin state from Dan's
  parallel sessions on Dans-MacBook-Pro requiring an FF-pull first;
  oh-statute auto-completed cleanly with default merge message.
- **Conflict-resolution discipline.** STATUS.md "Recent Sessions" conflicts
  on extraction-harness + phase-c resolved by keeping both branches' entries
  (HEAD entries above origin/main entries; intra-branch order preserved
  on each side), per multi-committer rule "only edit rows for the branch
  you're working on." TSV merged cleanly to main's renamed version on all
  three (verified with `diff` against main).
- **Substring-trap corruption discovery.** Dry-run on extraction-harness
  flagged the rename-execution convo as a target with 1 substitution.
  Inspected the diff before applying and recognized that line 20's
  OLD-name quotation was an intentional example, not stale content.
- **TDD on the hotfix.** Wrote two RED tests first — one unit
  (`should_skip_path` returns True for the convo path), one integration
  (`walk_and_apply` on a fixture of the actual line leaves it
  byte-identical). The integration test's RED failure visibly produced
  the corruption diff: `X (old) is a substring of X (new)`. Then added
  `Path("docs") / "active" / "compendium-row-id-renames"` to
  `_SKIP_SUBPATHS` (same precedent as `docs/historical/` and
  `compendium/_deprecated/`); both tests pass.

## Provisional Findings

- **Renamer skip-list had a missing tier.** The skip-list correctly protected
  the renamer's own module + tests + NAMING_CONVENTIONS.md + STATUS.md
  (those reference old IDs as data or as historical narrative), and the
  whole `docs/historical/` and `compendium/_deprecated/` paths. It missed
  one category: the active rename-execution convo, which is structurally
  in the same family as the historical archive (it documents WHY the
  rename was done, in the language of old-name → new-name) but lives in
  `docs/active/` for the duration of this branch's lifecycle. Hotfix
  closes the gap.
- **Sister-branch absorption surface was small.** Renamer dry-run on
  extraction-harness: 11 files / 56 substitutions (6 docs, 2 src, 3
  tests). On phase-c: 9 files / 26 substitutions. On oh-statute: 1 file /
  1 substitution (only the corruption case; nothing on this branch
  references old IDs because it's still skeletal). After the substring-
  trap restoration, renamer dry-run on main itself returns "no files
  contain old names — tree is already up to date" — confirming the
  rename-execution convo was the only file on main the renamer would
  have touched.
- **pytest deltas matched expectations.** Each branch reported only the
  three pre-existing `test_pipeline.py::test_*snapshot*/brief/stamp`
  failures (FileNotFoundError on gitignored `data/portal_snapshots/`
  fixture data) — identical to main's baseline; nothing new introduced
  by either the absorption or the hotfix.

## Decisions Made

- **Per-branch manual restoration of the substring-trap line in the
  absorb commit** rather than pausing absorption to fix the renamer
  first (Dan's call via AskUserQuestion). Rationale: the absorption work
  is independently valuable and the line restoration is mechanical
  one-line per branch; pausing would delay the absorption while the
  hotfix went through PR review.
- **Push the auto-merge commit as-is on `oh-statute-retrieval`** rather
  than amending the message or adding an empty commit (Dan's call via
  AskUserQuestion). Rationale: the merge IS the absorption when there
  are no own-branch references to old IDs and no conflicts; the default
  message accurately describes what happened.
- **Hotfix scope: whole `docs/active/compendium-row-id-renames/` directory,
  not just the one convo file.** Same precedent as
  `docs/historical/` and `compendium/_deprecated/`. The branch will
  eventually `git mv` to `docs/historical/` which is already skipped —
  this entry covers the active-docs interim. Future convos in this same
  directory (including this one) might also reference old IDs in
  narrative; the directory-level skip is forward-compatible.

## Results

- **3 absorb commits pushed:**
  - `extraction-harness-brainstorm` `151bad2 absorb v2 row-ID renames from main` (11 files / 56 substitutions; pytest 484 pass)
  - `phase-c-projection-tdd` `a83ede3 absorb v2 row-ID renames from main` (9 files / 26 substitutions; pytest 676 pass)
  - `oh-statute-retrieval` `54908f5 Merge remote-tracking branch 'origin/main' into oh-statute-retrieval` (auto-merge; pytest 342 pass)
- **Hotfix branch and PR:** `compendium-renamer-skip-fix` commit `660355e renamer: skip docs/active/compendium-row-id-renames/`; PR [#15](https://github.com/danparshall/lobby_analysis/pull/15) opened. pytest 344 pass (+2 over main baseline for the new tests, 0 regressions). Renamer dry-run on hotfix worktree post-fix: "no files contain old names — tree is already up to date."

## Open Questions

- **Should the absorbed sister branches re-merge main after PR #15
  lands?** They each already have the convo line correctly restored
  (manual fix in the absorb commit), so the renamer-fix doesn't change
  any content for them. But picking up the renamer fix would protect
  them from future re-runs of the script. Probably not urgent — the
  renamer isn't run regularly — but worth flagging when those branches
  next need to merge main for substantive reasons.
- **`compendium-row-id-renames` branch lifecycle.** The branch has been
  merged to main (via PR #14, `cb8ee4d`). This convo + RESEARCH_LOG
  update + STATUS.md one-liner now diverge it from main again. Standard
  options: (a) leave the divergence on the branch as research history
  until eventual archive; (b) cherry-pick or PR these doc updates to
  main; (c) wait until archive time (`git mv` to historical) and let
  the doc updates land as part of the archive PR. Not resolved this
  session.
- **Process gap on my side.** I should have caught the corruption case
  during a pre-flight review of the renamer's skip-list before running
  the dry-run on the first sister branch — the substring-trap convo is
  structurally in the same "documents the rename, references old names
  as data" family as the renamer module + its tests + NAMING_CONVENTIONS,
  all of which ARE in the skip-list. The category was right there in the
  comment block; I didn't extrapolate. Dry-run output caught it before
  any damage, but the more-disciplined version of this session would
  have caught it earlier.

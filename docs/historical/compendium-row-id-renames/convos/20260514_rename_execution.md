# 20260514 — Rename execution

**Date:** 2026-05-14
**Branch:** compendium-row-id-renames
**Predecessor convos:** [`compendium-naming-docs/convos/20260514_naming_taxonomy_kickoff.md`](../../../historical/compendium-naming-docs/convos/20260514_naming_taxonomy_kickoff.md), [`20260514_rename_review_and_plan.md`](../../../historical/compendium-naming-docs/convos/20260514_rename_review_and_plan.md), [`20260514_plan_sharpening.md`](../../../historical/compendium-naming-docs/convos/20260514_plan_sharpening.md)
**Originating plan:** [`compendium-naming-docs/plans/20260515_rename_execution_plan.md`](../../../historical/compendium-naming-docs/plans/20260515_rename_execution_plan.md)

## Summary

Session executed the 15 row-ID renames + 1 doc filename typo fix that were ratified on the `compendium-naming-docs` audit branch (merged via PR [#10](https://github.com/danparshall/lobby_analysis/pull/10) at session start). Two material architecture deviations from the originating plan emerged from in-session conversation with Dan: **(1)** no v2→v3 generation bump — the renames are a within-v2 contract refinement ("retroactively re-finalize" since v2 had only been finalized the prior day on `compendium-v2-promote`); **(2)** the renamer is a standalone find-and-replace script (`tools/v2_update_names.py` + `src/lobby_analysis/row_id_renamer.py`) rather than an extension to `tools/freeze_canonicalize_rows.py`, so sister branches can absorb the rename by merging main and running the tool on their own tree.

The session also surfaced and resolved three skip-rule problems that the dry-run caught before any file was written: (a) the renamer module and its tests reference old names as data and would corrupt themselves on a naive run; (b) `compendium/NAMING_CONVENTIONS.md` §10 documents the old→new pairs and would lose its candidate-list semantics on auto-rename; (c) `STATUS.md` session-log entries reference old names as historical narrative ("we renamed X to Y" would collapse to "Y to Y"). The fix was four skip-list entries plus archiving the `compendium-naming-docs/` audit docs to `docs/historical/` (which the existing `docs/historical/` skip-rule then covered). After those fixes, the apply surface dropped from 15 files / 157 substitutions to 4 files / 19 substitutions — the right surface.

Closing state: 4 commits on the branch, 36/36 renamer tests passing, 342/345 full test suite (3 pre-existing env failures unchanged), TSV at 181 rows with 0 old IDs and 15/15 new IDs present. Ready for finish-dev-branch and PR.

## Topics explored

- **Sequencing of execution vs sister-branch coordination.** Pushed back on Dan's first instinct to skip the deferral (the plan's coordination gate exists for a reason); Dan reformulated as "rename → merge to main → owners merge-main and run the script on their branches." Granted the reformulation — it redistributes the coordination cost (script-run is mechanical, ~1 min per branch) instead of pre-blocking on a multi-week wait for sister branches to settle.
- **Where the renamer code lives.** `tools/` is the CLI-script convention in this repo; tests can't import from there (no `__init__.py`). Refactored to put pure logic in `src/lobby_analysis/row_id_renamer.py` (importable, testable) with a thin CLI wrapper in `tools/v2_update_names.py`.
- **Word-boundary regex for the Candidate-5 substring trap.** `registration_deadline_days_after_first_lobbying` (old) is a substring of `lobbyist_registration_deadline_days_after_first_lobbying` (new). Naive find-and-replace would double-rename on idempotent re-runs (`lobbyist_lobbyist_registration_deadline_*`). `\b...\b` regex fixes this — `_` is a word character, so there's no word boundary at the `_r` join inside the new name.
- **§10 vs §10.1 split.** Plan §6 left "inline §10.1 vs external `V2_RENAME_RESOLVER.md`" open. Dan chose inline. The 16-entry RENAMES dict in the renamer module is the executable mirror of §10.1 — explicitly noted in §10.1's intro.
- **Test idempotency awareness.** One test (`test_real_tsv_non_id_columns_unchanged_for_renamed_rows`) assumed the live TSV would have old IDs at runtime. After applying the rename to the working tree, that precondition was gone and the test broke. Rewrote to look up source rows by old OR new ID, mirroring the script's own idempotency property. The fix preserves the invariant being tested (non-ID columns byte-identical for renamed rows) and works pre- and post-apply.

## Provisional findings

- The find-and-replace architecture is simpler than the plan's canonicalizer-extension approach and matches the sister-branch absorption model better. The plan's `tools/freeze_canonicalize_rows.py` extension would have required sister branches to also regenerate their TSV via that tool, which is more coordination than just running a script.
- The 4-commit structure (archive → renamer scaffold → NAMING_CONVENTIONS surgery → apply) made each commit independently reviewable. Splitting was worth the modest extra setup.
- The decision to skip NAMING_CONVENTIONS.md from auto-rename and hand-edit it instead was the right call — §10's candidate-list semantics required surgical attention (DONE markers + resolver table + body cross-ref updates) that no rule-based rewrite could produce cleanly.
- Three pre-existing env failures in `test_pipeline.py` (CA portal snapshots gitignored, not present in this worktree) are unrelated and identical to main — flagged in PR #10's test plan and again here.

## Decisions made

- **Architecture:** standalone find-and-replace script (`tools/v2_update_names.py`) backed by importable module (`src/lobby_analysis/row_id_renamer.py`). RENAMES dict has 16 entries (15 row renames + 1 doc filename typo).
- **Filename strategy:** keep `compendium/disclosure_side_compendium_items_v2.tsv` filename, update content in place. No v3 file, no `_deprecated/v2/` move. Sister-branch merges see a content-only change to one file.
- **Branch name:** `compendium-row-id-renames` (not the plan's speculative `compendium-row-renames-v3`).
- **Lifecycle:** `compendium-naming-docs` archived to `docs/historical/` in commit 1 (per workflow protocol — research line complete when its execution branch fires).
- **Sister-branch absorption:** owner work, not ours. Handoff sentence captured for use after this branch merges to main: each owner runs `git merge origin/main`, then `tools/v2_update_names.py --apply`, commits, pushes.

## Results

No results artifacts produced this session — the substantive output is the committed code (`src/lobby_analysis/row_id_renamer.py`, `tools/v2_update_names.py`, `tests/test_v2_update_names.py`) and the doc surgery on `compendium/NAMING_CONVENTIONS.md`. The post-rename prefix-survey regeneration is deferred (low priority — historical prefix-survey artifact at [`docs/historical/compendium-naming-docs/results/20260514_prefix_survey.md`](../../../historical/compendium-naming-docs/results/20260514_prefix_survey.md) still serves as the empirical baseline; the §3 "Plus 34 singleton families" claim is slightly stale post-rename but not load-bearing).

## Open questions

- **Prefix-survey regen** (low priority). The §2/§3 count tables in `NAMING_CONVENTIONS.md` have been hand-updated for the major families, but the "Plus 34 singleton families" claim is approximate post-rename. A clean regen would re-run the historical prefix-survey script against the renamed TSV and produce an updated artifact under `docs/active/compendium-row-id-renames/results/`. Deferred — not blocking PR.
- **`tools/freeze_canonicalize_rows.py` D-decision narrative.** The find-and-replace touched 2 substitutions in that tool's v1→v2 rename machinery. The D-decision-log narrative comments in that file still describe the old names as "current"; after rename, re-running the tool produces the new names directly. The narrative comments are stale but functionally correct. Future cleanup pass could refresh them.
- **NAMING_CONVENTIONS.md §3 singleton enumeration.** The full singleton-families list isn't in NAMING_CONVENTIONS.md — it's deferred to the prefix-survey artifact. Worth deciding whether to inline it on a future cleanup, or rely on the artifact link.

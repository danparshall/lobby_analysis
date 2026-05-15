# Research Log: compendium-row-id-renames

Created: 2026-05-14
Purpose: Execute the 15 row-ID renames + 1 README typo fix accepted on the (now archived) `compendium-naming-docs` audit branch — applying them across the v2 TSV, code, and prompts so the rename is retroactively part of v2's contract.

## Predecessor

- **Audit branch:** [`compendium-naming-docs`](../../historical/compendium-naming-docs/) (archived 2026-05-14 in PR [#10](https://github.com/danparshall/lobby_analysis/pull/10))
- **Originating plan:** [`docs/historical/compendium-naming-docs/plans/20260515_rename_execution_plan.md`](../../historical/compendium-naming-docs/plans/20260515_rename_execution_plan.md) — the 8-candidate walkthrough (15 row renames + 1 README typo) ratified across 3 sessions

## Deviations from the originating plan

The plan was written as a snapshot of pre-execution thinking; this branch implements it with two scope refinements:

1. **No "v3" — retroactive v2 finalization instead.** The plan called for a v3 TSV with the v2 TSV deprecated to `compendium/_deprecated/v2/`. We're keeping the filename `disclosure_side_compendium_items_v2.tsv` and updating its content in place. Rationale: v2 was finalized yesterday (2026-05-13) on `compendium-v2-promote`; the row-ID rename is a same-week contract refinement within v2, not a generation bump. Sister branches see a single content-change to one file (no path delete+add → no merge friction).

2. **Standalone find-and-replace script, not a `freeze_canonicalize_rows.py` extension.** The plan called for adding a `V2_TO_V3_RENAMES` dict + `--target-version=v3` flag to the existing v1→v2 canonicalizer. We're shipping `tools/v2_update_names.py` (CLI) + `src/lobby_analysis/row_id_renamer.py` (importable module with `RENAMES` dict). Rationale: sister branches need to be able to run the tool against their own working tree to absorb the rename after merging main; the canonicalizer-extension approach assumed a TSV-regeneration model that doesn't fit the find-and-replace use case.

The 15 row renames themselves match plan §1 verbatim. The LV-1 categorical exception (`lobbyist_filing_*` not `lobbyist_spending_report_*`) is preserved.

## Sessions

## Session: 2026-05-14 — rename execution

Full execution session — 4 commits land the rename end-to-end. Convo: [`convos/20260514_rename_execution.md`](convos/20260514_rename_execution.md).

### Topics Explored
- Architecture: standalone find-and-replace tool vs the plan's canonicalizer-extension; sister-branch absorption model; word-boundary regex for the Candidate-5 substring trap; skip-list design (renamer module + tests + NAMING_CONVENTIONS.md + STATUS.md + historical/deprecated paths).
- Doc surgery: §10 marked DONE (8 Issues), §10.1 resolver table added inline, §§2/3 prefix-family counts updated, body cross-refs updated through §§6/7/9/11.

### Provisional Findings
- Find-and-replace architecture is simpler than the plan's TSV-canonicalizer approach AND matches the sister-branch absorption model (each branch owner runs the script after merging main).
- Test design: making the byte-identity invariant test idempotency-aware (look up source row by old OR new ID) preserves the invariant pre- and post-apply.
- Apply surface shrank from 15 files / 157 subs to 4 files / 19 subs once the skip rules were in place — dry-run caught all three skip-rule gaps before any file was written.

### Decisions Made
- **No v3 file** — retroactive v2 finalization. Filename unchanged.
- **Branch name** `compendium-row-id-renames` (not the plan's speculative `*-v3`).
- **Sister-branch absorption** is owner work — handoff sentence captured.
- Audit branch `compendium-naming-docs` archived to `docs/historical/` (workflow protocol on completion).

### Results
None saved separately — the substantive session output is the 4 commits + the convo file. Prefix-survey regen against the renamed TSV deferred (low priority; historical prefix-survey artifact still serves as baseline).

### Next Steps
- finish-dev-branch on this branch: ruff check/format, push, open PR.
- After Dan merges PR: sister-branch owners apply the rename per the handoff sentence (each: merge origin/main, run `tools/v2_update_names.py --apply`, commit, push).

## Branch state

- **2026-05-14 (session 1, archived in PR #10):** Predecessor `compendium-naming-docs` produced the audit, ratified 8 rename candidates, drafted plan, sharpened. See historical convos/plans.

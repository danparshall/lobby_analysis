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

- **2026-05-14** — [in progress] Renamer module + CLI + 36 tests landed. Archive of `compendium-naming-docs` complete. Self-skip rules protect the renamer module, its tests, `compendium/NAMING_CONVENTIONS.md` (needs surgical hand-edit), and `STATUS.md` (session log is historical narrative). Pending: hand-update `compendium/NAMING_CONVENTIONS.md` (§10 → DONE, add §10.1 resolver table), apply rename script, PR.

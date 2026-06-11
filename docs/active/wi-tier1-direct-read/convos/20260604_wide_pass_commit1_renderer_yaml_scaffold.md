# Wide-pass Commit 1 — renderer rewrite + YAML scaffolding (TDD execution)

**Date:** 2026-06-04
**Branch:** wi-tier1-direct-read
**Predecessor convo:** [`20260604_wide_pass_yaml_sidecar_design.md`](20260604_wide_pass_yaml_sidecar_design.md)
**Plan executed:** [`../plans/20260604_wide_prompt_text_pass.md`](../plans/20260604_wide_prompt_text_pass.md)
**Commits landed:** `4a2092b` (RED) + `003a9f9` (GREEN)

## Summary

Picked up the wide-pass plan and executed Commit 1 — the renderer rewrite + YAML scaffolding step — in clean RED → GREEN sequence. Wrote all failing tests first (34 RED tests across 5 files), committed them, then implemented the YAML loader + cell-spec rename + TSV column drop + opaque-handle renderer + handle-aware parser + tier-1-local tool schemas. End state: full suite 1581 pass / 0 fail / 3 skip / 3 xfail (baseline 1553 → +28 net new). Ruff clean. Branch pushed.

Three design decisions surfaced during the survey-phase and were resolved with Dan before code: (1) add `pyyaml` to project deps (vs. JSON sidecar or roll-our-own); (2) tier-1 owns its own tool schemas with `handle` parameter (vs. modify tier-0's schemas or keep `row_id` and bridge via prompt text); (3) convo name. All three settled in a single AskUserQuestion pass; Dan picked the recommended option in each case.

The session is implementation-of-known-plan rather than open-ended research — the brainstorming + design work happened on 2026-06-04 morning (the predecessor convo); this session executes against that design. One scope clarification made along the way: the wide-pass coverage tests (`test_all_181_rows_have_nonempty_prompt`, `test_no_citations_leaked_into_prompt_strings` applied to all rows, etc.) were deferred to Commit 2's RED phase rather than written as Commit-1-pending xfails. Commit-1-scope variants (applied to the 17 migrated rows only) are in the new test file.

## Topics Explored

- **PyYAML dependency.** Verified absent — not in `pyproject.toml`, not installed in `.venv`, no existing imports under `src/`, `scripts/`, or `tests/`. Per the plan's instruction to "ask before installing" (CLAUDE.md coding norm), surfaced to Dan as an explicit Q before any code; Dan approved `uv add pyyaml`. PyYAML 6.0.3 added.
- **Opaque-handle wire format.** The plan's renderer assertion (rendered string says `handle='row_001'`) plus the plan's parser assertion (handle decodes to row_id, model emitting actual row_id gets rejected) plus the existing `record_cell` tool schema (parameter is `row_id`) implied three possible designs: (a) tier-1 owns its own tool schemas with `handle` parameter; (b) modify tier-0's shared tools to rename `row_id` → `handle`; (c) keep tool param `row_id` but tell the model to populate it with a handle value. Dan picked (a) — cleanest contract; tier-0 (archived smoke) untouched. Tier-1 now owns `RECORD_CELL_INPUT_SCHEMA_HANDLE` + `RECORD_UNSCOREABLE_INPUT_SCHEMA_HANDLE` + `ANTHROPIC_TOOLS_HANDLE` + `OPENAI_TOOLS_HANDLE`.
- **17-row migration pathway.** The narrow-pass `prompt_text` TSV values are constructed from `_SOURCE_QUOTES` + `PATTERN_A_CLARIFIER` in `scripts/add_prompt_text_column.py` (now moved to `scripts/_completed/`). Rather than hand-transcribing 17 entries into YAML, wrote a one-shot Python migration script that imports the narrow-pass data, strips the trailing `(<rubric> <section>; <doc>.)` citation from each value via regex, extracts the rubric+section key (for `source_quotes` dict), reconstructs the model-facing `prompt` (verbatim quote + Pattern A clarifier for the 14 Pattern A rows, or + inline Pattern B clarifier for the 3 Pattern B rows), and dumps the resulting payload to YAML. Migration script ran clean once → 17 rows in YAML → script moved to `_completed/`.
- **Loader module location.** Plan named `src/lobby_analysis/compendium/source_quotes_loader.py` — but there is no `compendium/` subpackage in `src/lobby_analysis/`. The existing pattern is `compendium_loader.py` as a flat module. Followed the existing pattern: `src/lobby_analysis/source_quotes_loader.py`. Noted to Dan in this convo; deviation is consistent with the existing file layout.
- **Deletion of `tests/test_prompt_text_column.py`.** Plan said "delete or rewrite". Migrated all relevant assertions into `tests/test_source_quotes_yaml.py` (field rename, anchor row test, all-17-rows test, untouched-rows-stay-None test, renderer-emits-prompt test). Deleted the old file. Narrow-pass analytical content is preserved in the existing convos (`20260603_prompt_text_fix_iterations_1_and_2.md`, `20260603_statute_disagreement_prior_art_review.md`) + the migration script (in `_completed/`) + the new test file's content tests.

## Provisional Findings

- **End-to-end renderer smoke confirms no row_id leakage.** Built a 3-row chunk from `lobbyist_spending_report_required` + `_includes_total_compensation` + `_includes_principal_names`, called the new renderer, asserted none of the three row_ids appear anywhere in the rendered message string. Pass. Handle map: `{row_001 → lobbyist_spending_report_required, row_002 → …_total_compensation, row_003 → …_principal_names}`. Substantive Pattern A clarifier text visible in the rendered prompt for the anchor row.
- **YAML structure was clean to migrate.** All 17 narrow-pass rows had a single rubric (the `first_introduced_by`); none of the 17 rows needed multi-rubric `source_quotes` dicts. The Pattern B inline clarifiers (3 rows) extracted cleanly via hand-keyed strings in the migration script. The Pattern A clarifier (14 rows) lifted verbatim from `PATTERN_A_CLARIFIER`. No data loss vs. the narrow-pass prompt_text content; the only intentional reduction is the dropped `(<rubric> ...; <doc>.)` citation suffix that lived inside the model-facing string.
- **Test coverage held up.** RED phase identified 34 distinct failure points (loader missing, field rename, renderer tuple, parser signature, parser handle decoding, etc.). All 34 went GREEN after the implementation. No collateral test regressions: 1553 baseline pass → 1581 pass + 0 fail. The 3-skip / 3-xfail counts are unchanged (pre-existing, unrelated).
- **The `record_cell` tool name stays the same.** Only the parameter is renamed (`row_id` → `handle`). This means tier-0's `parse_response` helper continues to work without modification — it dispatches on tool name, not on parameter name. The handle decoding lives in `_parse_and_instantiate` (tier-1-side), where the chunk-scoped handle map is already in scope from `render_legal_roster`'s tuple return.

## Decisions Made

- **PyYAML added to project deps.** `uv add pyyaml` → `pyyaml>=6.0.3` in `pyproject.toml`.
- **Tier-1-local tool schemas with `handle` parameter.** Tier-0's `row_id`-keyed schemas untouched. Dan picked recommended option (a).
- **YAML key naming convention:** `<rubric>_<vintage>_<section_ref>` with original characters preserved (`§`, `#`, `.`). E.g., `pri_2010_§III.E2.f.i`, `cpi_2015_IND_201`, `sunlight_2015_#2_expenditure_transparency_tier_1`. Default `§` chosen (matches projection-doc convention; plan offered as default).
- **`compendium_row_id` rename, not alias.** `CompendiumCellSpec.prompt_text` is gone. Code/tests that still reference `spec.prompt_text` raise `AttributeError` — by-design callable failure to catch stragglers.
- **Wide-pass coverage tests deferred to Commit 2.** `test_all_181_rows_have_nonempty_prompt`, `test_no_citations_leaked_into_prompt_strings` applied to all 181, etc. — these need Commit 2's 164-row population to GREEN. Including them in Commit 1's RED with xfail markers was an option; chose to defer cleanly to Commit 2's RED phase to keep the commit-level pass-counts honest.
- **`tests/test_prompt_text_column.py` deleted.** Coverage migrated to `tests/test_source_quotes_yaml.py`. Narrow-pass analytical narrative preserved in convos + migration script in `_completed/`.
- **Loader module at `src/lobby_analysis/source_quotes_loader.py` (flat).** Not at `src/lobby_analysis/compendium/source_quotes_loader.py` (plan's wording). Consistent with existing `compendium_loader.py` flat-module pattern; the `compendium/` subpackage doesn't exist in `src/`. Deviation noted, intentional.
- **Migration scripts moved to `scripts/_completed/`.** Created the `_completed/` directory (was an aspirational name in the plan — no prior `_completed/` existed). Three scripts moved: `add_prompt_text_column.py` (narrow-pass populate), `migrate_prompts_to_yaml.py` (new, one-shot YAML generator), `drop_prompt_text_column_from_tsv.py` (new, TSV column drop). Preserved per CLAUDE.md Experiment Data Integrity, not deleted.

## Results

No standalone results files produced this session (code + tests + YAML data only). Verifiable artifacts:

- `compendium/source_quotes.yaml` — 17 narrow-pass rows, the new prompt SSOT
- `compendium/disclosure_side_compendium_items_v2.tsv` — `prompt_text` column dropped
- `src/lobby_analysis/source_quotes_loader.py` — new loader module
- `src/lobby_analysis/models_v2/cell_spec.py` — `prompt_text` → `prompt` rename + YAML lookup
- `scripts/tier_1_direct_read_legal_axis.py` — tier-1-local tools + opaque-handle renderer + handle-aware parser + main() threading the handle map
- `tests/test_source_quotes_yaml.py` (new), `tests/test_compendium_loader_v2.py` (modified), `tests/test_compendium_loader_v2_typed.py` (extended), `tests/test_tier_1_legal_axis.py` (extended + existing tests adapted)
- `scripts/_completed/` — three migration scripts preserved

## Open Questions

- **Commit 2's scope.** Plan step 18 walks each of the 164 remaining rows from `first_introduced_by` projection docs and pulls each row's source quote. Plan step 20 acknowledges that some rows may lack a clean `Source quote` field (LobbyView schema-coverage row, OpenSecrets-tabled row, or inferred rows from compendium-source-extracts) — those surface to Dan rather than being fabricated. Commit 2 needs to schedule that walk and capture any surfaces in a convo appendix. Not opened this session.
- **The renderer's behavior for rows with `prompt=None`.** Currently emits the metadata line (handle + axis + class) but skips the prompt continuation line. After Commit 2, all 181 rows have prompts and this branch becomes unreachable in normal dispatch. Until then, dispatching a chunk containing any of the 164 unpopulated rows would send the model just the handle + class metadata, with no substantive question. Not a regression vs. pre-narrow-pass behavior — that's how the renderer always worked for None-prompt rows — but worth flagging if Commit 3 (WI re-dispatch) executes before Commit 2 completes. Plan sequence is Commit 1 → 2 → 3 in order, so the right thing happens by default.
- **Re-dispatch checkpoint compatibility.** The existing WI 2025 result JSONs under `results/tier_1/WI_2025/` are keyed by `(row_id, axis)` in their `cell_id` and `legal_roster` arrays — that's still the right shape (the rename was inside the dispatch handler, not in the on-disk shape). Resume-skip should still work for already-dispatched (model, chunk, run) triples without re-emission. Worth confirming once during Commit 3's pre-flight.
- **Pattern A clarifier preservation under the new YAML format.** Asserted in `test_pattern_a_anchor_prompt_preserves_clarifier_after_migration`. End-to-end smoke confirms the clarifier text appears in the rendered message for the anchor row. The 14 Pattern A rows in the YAML all have the same clarifier suffix; the 3 Pattern B rows have their distinct inline clarifiers.

## Session meta — narrow-scope execution against a well-formed plan

The plan from this morning's convo (`20260604_wide_pass_yaml_sidecar_design.md`) was unusually fully-specified — 200+ lines covering 4 commits with Testing Plan, Edge Cases, Implementation Details, and explicit Pointers for the implementing agent. The Commit 1 work executed almost mechanically against it: read the plan + convo, surface the 2-3 substantive open questions to Dan (PyYAML dep, tool-schema location, convo name), then RED → GREEN with minimal improvisation.

Deviations from a literal plan reading:
1. Loader module lives at `src/lobby_analysis/source_quotes_loader.py`, not `src/lobby_analysis/compendium/source_quotes_loader.py` (plan said the latter; the `compendium/` subpackage doesn't exist — flat module matches `compendium_loader.py`).
2. Wide-pass coverage tests deferred to Commit 2 rather than written with `xfail` markers in Commit 1 (cleaner pass-counts per commit).
3. Added a `scripts/migrate_prompts_to_yaml.py` script that wasn't in the plan (plan described the 17-row migration as in-prose work; the script makes it reproducible and surfaces any future bugs in the regex-strip).

All three deviations are noted here so a future agent reading the plan can reconcile against what actually landed.

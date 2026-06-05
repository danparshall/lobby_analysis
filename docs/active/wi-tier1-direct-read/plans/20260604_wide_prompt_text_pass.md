# Wide 181-row `prompt_text` Pass — Implementation Plan

**Goal:** Replace the TSV-embedded `prompt_text` column with a sidecar YAML SSOT at `compendium/source_quotes.yaml`, rewrite the Tier-1 dispatch renderer to send opaque per-chunk handles + substantive prompts (no row-IDs to the model), populate the YAML for all 181 v2 compendium rows from their source-rubric quotes, and re-dispatch WI as a sanity check.

**Originating conversation:** [`../convos/20260604_wide_pass_yaml_sidecar_design.md`](../convos/20260604_wide_pass_yaml_sidecar_design.md)

**Context:** The narrow 17-row `prompt_text` fix landed 2026-06-03 (evening) and validated cleanly (Pattern A 14/14 + Pattern B 3/3 → inter-model agreement 47/65 → 65/66). The fix proved that giving the model substantive prompt text disambiguates the row-label-as-question ambiguity that caused Pattern A. Three open paths followed: (a) wide pass for the remaining 164 rows; (b) MI Tier-1 dispatch with the current narrow-pass prompts; (c) Pattern C row-axis split. Dan chose (a). The wide pass also became the natural moment to fix architectural debt: the narrow pass embedded the prompt in a TSV column with citations baked into the model-facing string, and sent the row-ID alongside the prompt — both of which leak signals (rubric-name bias, row-name semantics) that the model shouldn't see going forward. The design walk in the originating convo settled on: sidecar YAML as prompt SSOT, opaque-handle renderer, citations dropped from model input.

**Confidence:** High on architecture (settled across 5 design rounds with Dan; the simpler-each-time pattern matched). Medium on YAML population — the 164-row walk will surface unknowns: rows whose projection-mapping doc lacks a clean `Source quote` field, rows whose v2 ID has diverged enough from the rubric's terminology that a synthesized prompt is needed. Population is mostly mechanical but the walk-through is the moment when those surface.

**Architecture:** Two-layer separation. Compendium TSV remains the row-set contract (181 rows, axes, cell types, rubric attribution). New sidecar YAML at `compendium/source_quotes.yaml` is the prompt SSOT. Per-row YAML schema is two flat fields: `source_quotes` (immutable dict keyed by rubric+section ref) + `prompt` (mutable flat string sent to the model). Runtime reads YAML at registry-build time; TSV's `prompt_text` column gets dropped. Renderer sends opaque per-chunk handles (`row_001`, `row_002`, …) + prompt only; result parser maps handles → row_ids on receipt. Row IDs stay internal to the code, never reach the model.

**Branch:** `wi-tier1-direct-read` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/`).

**Tech Stack:** Python 3.12 + `uv`; PyYAML for YAML loading (likely already a transitive dep; verify with `uv pip list | grep -i yaml` before adding); pytest for tests; ruff for lint; existing dispatch harness (Claude Opus 4.7 + GPT-5.2 via the Anthropic + OpenAI Python SDKs).

---

## Testing Plan

I will write **all tests before any implementation behavior**, per the test-driven-development skill.

### Unit tests — YAML loader (new file: `tests/test_source_quotes_yaml.py`)

- `test_yaml_file_exists_at_canonical_path` — loader points at `compendium/source_quotes.yaml`; file is present.
- `test_yaml_has_entry_for_every_v2_compendium_row` — for each of the 181 rows in `compendium/disclosure_side_compendium_items_v2.tsv`, the YAML contains a matching key. Catches "added a row to TSV, forgot to add to YAML" drift.
- `test_yaml_entry_has_source_quotes_dict_and_prompt_string` — every YAML entry has `source_quotes: dict` (non-empty) + `prompt: str` (non-empty).
- `test_yaml_loader_returns_typed_objects` — `load_source_quotes()` returns `dict[row_id, SourceQuotesEntry]` where `SourceQuotesEntry` is a small dataclass (or NamedTuple) with `source_quotes: dict[str, str]` and `prompt: str`. Behavior, not type structure: assert a known row's loaded value round-trips byte-identically through the loader.
- `test_yaml_loader_rejects_missing_required_keys` — a malformed YAML entry (missing `prompt:` or empty `source_quotes:`) raises a clear error pointing at the row_id.

### Unit tests — CompendiumCellSpec / registry (extend `tests/test_compendium_loader_v2.py` + `tests/test_compendium_loader_v2_typed.py`)

- `test_cellspec_has_prompt_field_populated_from_yaml` — `build_cell_spec_registry()` populates `CompendiumCellSpec.prompt` from the YAML, not from the TSV. For a known row, the spec's `prompt` matches the YAML's `prompt:` byte-identically.
- `test_cellspec_prompt_text_field_removed_or_aliased` — the old `prompt_text` field is gone (or aliased to `prompt` for one deprecation cycle; pick one — see Implementation Details).
- `test_tsv_loader_ignores_dropped_prompt_text_column` — if a stale TSV vintage still has `prompt_text` as a column, the loader either ignores it silently OR errors clearly (decide; pick one and test it). The 17 narrow-pass rows' TSV `prompt_text` data has already moved to YAML — the column gets dropped from the TSV file in this same commit.
- **Update existing pinned-column-set test in `tests/test_compendium_loader_v2.py`** — narrow pass added `prompt_text` to the pinned set; the column drops here, so the pinned set shrinks back.

### Unit tests — opaque-handle renderer (extend `tests/test_tier_1_legal_axis.py`)

- `test_render_legal_roster_uses_opaque_handles_not_row_ids` — for a 3-row chunk, the rendered string contains `handle='row_001'`, `handle='row_002'`, `handle='row_003'` and does NOT contain any of the 3 rows' `compendium_row_id` values verbatim. **This is the load-bearing behavioral test** — it directly asserts the row-name-suppression contract.
- `test_render_legal_roster_emits_substantive_prompt_per_row` — for each row in the chunk, the rendered string contains the row's `prompt` (from YAML) on its line.
- `test_render_legal_roster_omits_axis_metadata_redundancy` — same renderer, but check that the prompt string itself is on a clear line (not buried). Spec: each handle gets one line of metadata + one line of prompt (multiline prompts allowed via continuation).
- `test_handle_to_row_id_mapping_is_deterministic_per_chunk` — the handle→row_id map is a function of chunk membership + iteration order; two renders of the same chunk produce the same map.
- `test_handle_to_row_id_mapping_returned_alongside_message` — the renderer (or a sibling function) returns both the message string AND the handle→row_id map, so the dispatch handler can decode responses without parsing the prompt.

### Unit tests — dispatch result parsing (extend `tests/test_tier_1_legal_axis.py`)

- `test_result_parser_maps_handle_to_row_id` — given a model response that says `"row_001": <cell-record>`, the parser produces a result keyed by the original `compendium_row_id`, using the handle→row_id map from the renderer.
- `test_result_parser_rejects_unknown_handle` — if the model emits `"row_999"` (not in the chunk's handle set), the parser raises a clear error. We do NOT want silent drops.
- `test_result_parser_rejects_row_id_emission_by_model` — if the model emits a key matching a known `compendium_row_id` rather than a handle, parser also rejects (forces the contract; would catch a regression where the model started leaking row-IDs back at us because we forgot to strip them somewhere).

### Integration test — end-to-end render + parse (extend `tests/test_tier_1_legal_axis.py`)

- `test_render_then_parse_roundtrip_preserves_row_ids` — render a known chunk → mock a model response that produces one valid record_cell per handle → parser produces results keyed by the original row_ids. No row-IDs visible in the rendered message; all row-IDs recoverable from the parsed results. This is the integration-level behavioral guarantee.

### Wide-pass YAML population — sanity tests (extend `tests/test_source_quotes_yaml.py`)

- `test_all_181_rows_have_nonempty_prompt` — every row's `prompt:` is a non-empty string.
- `test_no_citations_leaked_into_prompt_strings` — check that no `prompt:` string contains substrings matching `(PRI 2010 §`, `(CPI 2015`, `(Newmark 2017`, etc. — i.e., the citation-bake-in pattern from the narrow pass has been stripped on migration.
- `test_known_pattern_a_row_prompt_still_includes_clarifier_text` — for `lobbyist_spending_report_required` (one of the 14 Pattern A rows), the YAML's `prompt:` includes the LOBBYIST-vs-PRINCIPAL clarifier text ("Asks whether the LOBBYIST is the named filer...") that the narrow pass added. Behavior preservation across migration.
- `test_two_outlier_rows_have_keyed_source_quotes` — `lobbyist_filing_distinguishes_in_house_vs_contract_filer` has a `lobbyview_2018_schema_field:` key; `separate_registrations_for_lobbyists_and_clients` has an `opensecrets_2022_tabled:` key.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Step-by-step Implementation

### Commit 1 — Renderer rewrite + YAML scaffolding

**Setup:**

1. Verify `pyyaml` is available: `uv run python -c "import yaml; print(yaml.__version__)"`. If missing, add to `pyproject.toml` (ask Dan before installing per CLAUDE.md "Ask before installing").
2. Create empty scaffold YAML at `compendium/source_quotes.yaml` with header comment explaining the schema.

**Tests first (all RED before any implementation):**

3. Write `tests/test_source_quotes_yaml.py` (the YAML-loader tests + the 17-row migration tests). Verify all RED.
4. Extend `tests/test_compendium_loader_v2.py` and `tests/test_compendium_loader_v2_typed.py` with the CompendiumCellSpec.prompt tests + drop the `prompt_text` from the pinned column set. Verify RED.
5. Extend `tests/test_tier_1_legal_axis.py` with the opaque-handle renderer + result-parser + integration tests. Verify RED.
6. Run `pytest -x tests/test_source_quotes_yaml.py tests/test_compendium_loader_v2.py tests/test_compendium_loader_v2_typed.py tests/test_tier_1_legal_axis.py` — record the RED count.
7. Commit the failing tests with message `wi-tier1: RED tests for YAML SSOT + opaque-handle renderer`.

**Implementation:**

8. Create `src/lobby_analysis/compendium/source_quotes_loader.py` (new module). Exposes `load_source_quotes() -> dict[str, SourceQuotesEntry]` and a `SourceQuotesEntry` dataclass. Loader path is `compendium/source_quotes.yaml` resolved relative to repo root (same pattern as `load_v2_compendium`).
9. Migrate the 17 narrow-pass rows from `compendium/disclosure_side_compendium_items_v2.tsv`'s `prompt_text` column into `compendium/source_quotes.yaml`:
   - For each of the 17 rows: lift the verbatim source quote into `source_quotes:` keyed by rubric+section ref (use the citation that's currently embedded inside the `prompt_text` string — e.g., `cpi_2015_IND_201:` for the CPI rows).
   - Set `prompt:` to the current `prompt_text` value MINUS the embedded `(<rubric> <section>; <doc>.)` citation suffix. The Pattern A clarifier text stays. Strip citations only.
   - Run `tests/test_source_quotes_yaml.py::test_known_pattern_a_row_prompt_still_includes_clarifier_text` to verify the clarifier-preservation. Should now be GREEN for the 17 rows.
10. Modify `src/lobby_analysis/models_v2/cell_spec.py`:
    - Rename `prompt_text` → `prompt` on the `CompendiumCellSpec` dataclass. **Pick rename, not alias** — semantic is now "what the model sees," distinct enough from the old "verbatim source quote" that aliasing would be confusing.
    - In `build_cell_spec_registry()`, replace the `prompt_text_raw = (row.get("prompt_text") or "").strip()` block with a call to `load_source_quotes()` and look up each row's `prompt:` field.
    - Drop the TSV `row.get("prompt_text")` read entirely.
11. Drop the `prompt_text` column from `compendium/disclosure_side_compendium_items_v2.tsv`:
    - Use `csv.DictReader` + `DictWriter` with `lineterminator='\n'` (same pattern as the narrow-pass `add_prompt_text_column.py` script) — preserves Unix line endings. Diff hygiene matters.
    - Write a one-off script `scripts/drop_prompt_text_column_from_tsv.py` that reads, removes the column from `fieldnames`, and writes back. Run it once and commit the TSV change as part of this same commit. Move the script to `scripts/_completed/` after (matching the existing pattern from `add_prompt_text_column.py` — verify what that pattern actually is by listing `scripts/`).
    - Run `pytest tests/test_compendium_loader_v2.py` — should be GREEN now (pinned column set shrank).
12. Rewrite `render_legal_roster()` in `scripts/tier_1_direct_read_legal_axis.py`:
    - Change signature to return `tuple[str, dict[str, str]]` — `(rendered_message, handle_to_row_id_map)`.
    - For each spec in `legal_specs`, assign a zero-padded handle: `f"row_{idx + 1:03d}"`.
    - Render each row's line as `f"- handle={handle!r}, axis='legal', expected_cell_class={cls.__name__}{_value_shape_hint(cls)}"`.
    - On the continuation line, render the spec's `prompt` field (which now comes from YAML via the registry).
    - **Remove the `row_id` field from rendered output entirely.** This is the load-bearing change.
    - Build the handle→row_id map and return it alongside the message.
13. Update the dispatch handler at `scripts/tier_1_direct_read_legal_axis.py` line 595 (the `user_message = render_legal_roster(...)` call) to consume the new tuple shape. Thread the `handle_to_row_id_map` to the result-parsing code path. Wherever the dispatch handler currently keys parsed cells by the `row_id` field on the model's response, change to: look up the handle, map to row_id via the chunk's map.
14. Modify the result parser (find it via grep for the function that consumes `record_cell` results) to reject responses keyed by anything other than known handles.
15. Run `pytest -x` (full suite). Fix any unrelated failures only if they were introduced by this commit; surface pre-existing failures to Dan rather than auto-fixing.
16. Run `ruff check` on all touched files; fix any new lint issues.
17. Commit with message `wi-tier1: YAML SSOT for prompts + opaque-handle renderer (drops row-IDs from model input)`.

### Commit 2 — YAML population for the remaining 164 rows

**Approach:** the 17 narrow-pass rows already landed in Commit 1. This commit populates the remaining 164.

18. Walk each row in `compendium/disclosure_side_compendium_items_v2.tsv` (skip the 17 already populated). For each:
    - Read `first_introduced_by` from the TSV.
    - Open the corresponding projection-mapping doc at `docs/historical/compendium-source-extracts/results/projections/<first_introduced_by>` and locate the row's atomic-indicator block. Locate the `Source quote` field within that block.
    - Add a YAML entry: `source_quotes` has the verbatim quote keyed by rubric+section ref; `prompt` is initially populated as the verbatim quote itself (no decoration).
    - **Citation never appears in the `prompt:` value** (only in the YAML key).
19. Handle the 2 outlier rows inline:
    - `lobbyist_filing_distinguishes_in_house_vs_contract_filer` (LobbyView schema-coverage): synthesize a `prompt:` like "Does the state's lobbyist registration filing distinguish in-house lobbyists from contract lobbyists?" Key the `source_quotes:` entry as `lobbyview_2018_schema_field:` with a value documenting the schema field origin.
    - `separate_registrations_for_lobbyists_and_clients` (OpenSecrets-tabled): use the verbatim quote from `docs/historical/compendium-source-extracts/results/_tabled/opensecrets_2022_tabled.md` line 48 ("the baseline score was three and states that require separate registrations for the lobbyists and clients were assigned a four"). Key as `opensecrets_2022_tabled:`.
20. **Rows where the projection-mapping doc lacks a clean `Source quote` field** (likely surface during the walk): flag and bring back to Dan rather than fabricating. Possible categories:
    - The atomic indicator exists but the rubric's source paper doesn't have a quotable question (e.g., LobbyView-style schema field).
    - The atomic indicator was added as an inferred row during compendium-source-extracts and the projection doc says "inferred."
    - The row's source quote is implicit in a multi-row tier definition (e.g., Sunlight Tier 0/1/2 splits).
    Capture each in a draft section of the convo (`../convos/20260604_wide_pass_yaml_sidecar_design.md` — append a "Wide-pass surfaces" section if you find any). DO NOT fabricate a prompt. Ask Dan.
21. Run the full test suite. The `test_all_181_rows_have_nonempty_prompt` and related coverage tests should now be GREEN.
22. Run a smoke probe — `uv run python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --dry-run` (verify the exact flag name in the script). Confirm: 6 chunks, 84 legal cells, 36 planned dispatches (matches Phase 2 baseline). Renderer output spot-check: no row_ids visible; opaque handles present; substantive prompts per row.
23. Commit with message `wi-tier1: populate source_quotes.yaml for 164 remaining rows (wide pass)`.

### Commit 3 — WI re-dispatch + audit

24. Confirm with Dan that the spend (~$2.50) is OK to fire (per CLAUDE.md "Independence — Do not make changes to ... third party APIs" + the narrow-pass convo's pattern of explicit Dan sign-off on paid runs).
25. Archive the existing WI Tier-1 result JSONs:
    - Source: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/`
    - Archive subdir: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_wide_pass/` (per CLAUDE.md Experiment Data Integrity).
26. Run the dispatch: `uv run python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025` (no `--dry-run`). Expected: 36/36 dispatched, 0 corrupt, ~20 min wall, ~$2.50.
27. Compute the audit. Reuse the audit script pattern from `results/disagreement_audit/` (referenced in `convos/20260603_statute_disagreement_prior_art_review.md`):
    - σ_noise per model (compare to narrow-pass baseline: Claude 86.90%, GPT 82.14%).
    - Inter-model agreement on jointly-stable cells (baseline: 65/66 = 98.5%).
    - Per-cell disagreement audit: which cells changed verdict from narrow-pass baseline?
    - Cell-instantiation error count (baseline: 6/6 runs failed `lobbyist_registration_threshold_time_percent` — known v2.2 Entry 1 schema gap, unchanged).
28. Write `results/20260604_wi_wide_pass_audit.md` with provenance header (`<!-- Generated during: convos/20260604_wide_pass_yaml_sidecar_design.md -->` + this plan's path).
29. **Watch for the failure mode the convo flagged:** any currently-passing row that *fails* under the new renderer because we accidentally relied on row_id semantic leakage in some passing case. If a previously-agreed row now disagrees, that's a wide-pass-introduced regression worth diagnosing before MI.
30. Commit with message `wi-tier1: WI Tier-1 wide-pass re-dispatch + audit (sanity check on YAML SSOT + opaque-handle renderer)`.

### Commit 4 — Optional stylistic-rename cleanup (DEFERRED)

This is a placeholder. Per the convo, the rename-cleanup commit is demoted to optional/stylistic. Skip unless Dan explicitly asks during the WI re-dispatch audit. If pursued: walk the wide pass for `compendium_row_id` strings that read awkwardly in YAML keys; propose renames; ship as a separate commit with TSV row-ID changes + YAML key updates + test-fixture updates in lockstep. NOT in scope for this plan's execution.

---

## Edge Cases

- **YAML parse error mid-load.** If `source_quotes.yaml` is malformed (bad indentation, unbalanced quotes), the loader should error clearly with the row_id (or the line number from PyYAML's MarkedYAMLError) — not crash with a stack trace deep in the registry builder.
- **Multi-line prompt YAML.** Pattern A clarifier rows have multi-paragraph prompts. YAML `|` (literal block scalar) preserves newlines; `>` folds them. Use `|`. Multiline behavior tested via the byte-identical round-trip test.
- **Row in TSV but missing from YAML.** Loader raises with the row_id. The `test_yaml_has_entry_for_every_v2_compendium_row` test catches this in CI rather than at dispatch time.
- **Row in YAML but not in TSV.** Loader logs a warning (not an error) — the YAML entry is just unused. Could happen during a row-removal flow where the TSV is updated first.
- **Handle collision across chunks.** Handles are scoped to a single chunk's render. If `row_001` appears in two different chunks' messages, that's fine — the dispatch handler tracks the handle→row_id map per-chunk. Verify the dispatch code path does this correctly (it should already, since chunks are dispatched independently).
- **Model emits a `row_id` key instead of a handle in its response.** Handled by the `test_result_parser_rejects_row_id_emission_by_model` test. The parser errors loudly.
- **Existing OH 2025 results.** Stored at `docs/active/wi-tier1-direct-read/results/tier_1/OH_2025/` (from prior sessions). NOT touched by this work — the renderer change only affects future dispatches. OH results stay as-is unless we choose to re-dispatch OH later (out of scope).
- **`tests/test_prompt_text_column.py` from the narrow pass.** Likely needs deletion or rewrite (its name implies it tested the now-dropped TSV column). Verify it doesn't test behavior that's still relevant before deleting. If any test in there tests "narrow-pass 17 rows have these specific prompts," that behavior moves to `tests/test_source_quotes_yaml.py`.
- **`scripts/add_prompt_text_column.py` from the narrow pass.** Idempotent populate script for the dropped TSV column. Move to `scripts/_completed/` (or wherever the established pattern lives) after Commit 1. Don't `rm`.

---

## Testing Details

The tests assert behavior, not types or implementation. The load-bearing assertions are:

- **No row-IDs in the rendered message.** `test_render_legal_roster_uses_opaque_handles_not_row_ids` directly asserts the model never sees `lobbyist_spending_report_required` (or any other v2 row_id) in the prompt. If a future refactor accidentally puts row-IDs back into the renderer output, this test fails.
- **Handles round-trip to row-IDs.** `test_render_then_parse_roundtrip_preserves_row_ids` asserts the end-to-end contract: the model sees opaque handles, the parser recovers original row-IDs. The map is the bridge.
- **Citations don't reach the model.** `test_no_citations_leaked_into_prompt_strings` checks every populated `prompt:` field against the citation-bake-in pattern from the narrow pass. The model sees the substantive question, not "(CPI 2015 IND_201; ...)".
- **YAML coverage matches TSV.** `test_yaml_has_entry_for_every_v2_compendium_row` catches the drift class where someone adds a TSV row but forgets to add a YAML entry. This is the integrity contract for the two-file SSOT split.
- **Narrow-pass clarifier preservation.** `test_known_pattern_a_row_prompt_still_includes_clarifier_text` is the migration-correctness anchor — it asserts that the work the narrow pass did (Pattern A clarifier vocabulary) survives the YAML migration byte-for-byte.

No tests check just types or data structures; no tests mock then assert the mock. All tests run against real loader + real renderer + real (small, in-test-fixture) YAML.

## Implementation Details

- The YAML SSOT lives at `compendium/source_quotes.yaml` (repo-relative). Loader resolves path via the same pattern as `load_v2_compendium()` — anchored to the repo root, not the worktree root.
- `CompendiumCellSpec.prompt_text` is **renamed** to `prompt` (not aliased). Old field name is gone in this commit. Any test or code that still references `prompt_text` becomes a callable failure on first run.
- `prompt_text` TSV column dropped in Commit 1. Use `csv.DictWriter` with `lineterminator='\n'` to preserve Unix endings. Verify the resulting TSV header line is `compendium_row_id\tcell_type\taxis\trubrics_reading\tn_rubrics\tfirst_introduced_by\tstatus\tnotes`.
- Handles use the format `row_{idx:03d}` (zero-padded 3 digits — supports up to 999 rows per chunk, which is far more than the largest current chunk of ~24).
- Multiline `prompt:` values use YAML `|` (literal block scalar), not `>` (folded). Preserves intentional line breaks in clarifier text.
- The handle→row_id map is **returned from the renderer**, not stored as module-level state. Each dispatch call owns its own map; no global mutation.
- Result parser rejection on unknown handle / leaked row_id is a loud failure, not a silent drop. Mistakes should be visible.
- No backward-compat shim for the old `prompt_text` field. Clean break; rename catches stragglers via test failures.
- 4 Edge-case scripts (`add_prompt_text_column.py`, `drop_prompt_text_column_from_tsv.py`) are one-shot migrations — move to `scripts/_completed/` or equivalent, do not delete.
- WI re-dispatch in Commit 3 archives prior results under `_pre_wide_pass/`, never `rm`s anything (Experiment Data Integrity).
- All new file content is text — no binary additions.

## What could change

- **Population strategy if the projection-mapping docs are inconsistent.** The walk-through (step 18) assumes each row's `first_introduced_by` doc has a clean `Source quote` field. If a meaningful fraction (>10%, say) lack clean quotes, the wide pass may need to split into "rows with clean quotes" (mechanical) + "rows requiring synthesis" (Dan review). Surface to Dan via the "Wide-pass surfaces" convo appendix if it happens.
- **Whether to include all rubrics' quotes in `source_quotes`, or just `first_introduced_by`'s.** Plan defaults to `first_introduced_by` only for the initial population — minimum viable. If post-WI audit shows specific rows where the multi-rubric framing variance is diagnostic (i.e., GPT and Claude disagree because they're reading different rubrics' implicit framing), populating the additional rubrics' quotes becomes a follow-up. Out of scope for the initial wide pass.
- **WI re-dispatch agreement target.** Baseline is 65/66 (98.5%). If wide-pass re-dispatch lands at ≥65/66, the renderer change validates and we move to MI. If it drops below 65/66, that's a regression and we diagnose before MI. If it improves (66/66 or beyond), that's a positive surprise — the row-ID-as-bias-signal hypothesis was real.
- **Whether the Ralph-loop infrastructure becomes part of this branch or its own.** Out of scope for the wide pass; the YAML SSOT is the prerequisite, not the loop itself.

## Questions

- **YAML key naming convention.** For rubric+section refs, I've been writing keys like `pri_2010_§III.E2.f.i:`. The `§` character is YAML-legal but slightly awkward; an alternative is `pri_2010_section_III.E2.f.i:`. Pick one in the first YAML entry written; stay consistent across all 181. Default: `§` (matches the projection docs' own usage).
- **Should the loader function be a registry-builder pure call or a memoized cached load?** First call loads YAML from disk; subsequent calls reuse. Default: simple uncached load (correctness > optimization at this scale; 181 entries is trivial). If profiling shows the registry builder being called per-row at dispatch time, add `functools.lru_cache` then.
- **Compendium version bump?** Dropping the `prompt_text` TSV column is technically a TSV schema change. The v2.1 → v2.2 line in the v2.2 ledger expects axis-splits / cell-class additions to move that line; a column drop may or may not count. Default: stay on v2.1; document the column drop as a change in the v2.2 ledger Entry 3 status (now also closed).
- **PyYAML dependency.** Verify it's already transitive before Commit 1; ask Dan if a fresh install is needed.

---

## Pointers for the implementing agent

### Existing relevant code (paths inside the worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-tier1-direct-read/`)

- `compendium/disclosure_side_compendium_items_v2.tsv` — the 181-row v2 TSV; the `prompt_text` column at position 9 gets dropped in Commit 1.
- `src/lobby_analysis/models_v2/cell_spec.py` (lines 35–50, 159–214) — `CompendiumCellSpec` dataclass + `build_cell_spec_registry()`. Modify both.
- `scripts/tier_1_direct_read_legal_axis.py`:
  - Line 205: `render_legal_roster()` — rewrite for opaque handles.
  - Line 595: `user_message = render_legal_roster(chunk_id, chunk.topic, legal)` — adapt to new tuple return.
- `scripts/add_prompt_text_column.py` — narrow-pass populate script; serves as the populate-script-shape template. Move to `_completed/` after.
- `tests/test_prompt_text_column.py` — narrow-pass tests; rewrite or delete during YAML migration.
- `tests/test_compendium_loader_v2.py` — has the pinned-column-set test; update.
- `tests/test_compendium_loader_v2_typed.py` — extend with `CompendiumCellSpec.prompt` tests.
- `tests/test_tier_1_legal_axis.py` — extend with opaque-handle renderer + result-parser tests.

### Existing relevant docs

- [`../convos/20260604_wide_pass_yaml_sidecar_design.md`](../convos/20260604_wide_pass_yaml_sidecar_design.md) — the originating convo. Read first.
- [`../convos/20260603_prompt_text_fix_iterations_1_and_2.md`](../convos/20260603_prompt_text_fix_iterations_1_and_2.md) — the narrow-pass implementation; reference for the 17 rows' migration content.
- [`../convos/20260603_statute_disagreement_prior_art_review.md`](../convos/20260603_statute_disagreement_prior_art_review.md) — the prior-art adjudication that established Pattern A/B/C; reference for the "where does each row's source quote live" question.
- [`../results/v2_2_schema_inputs.md`](../results/v2_2_schema_inputs.md) — v2.2 ledger; Entry 3 status will update on completion; Entry 4 closes implicitly via this plan.
- [`../results/20260603_prior_art_adjudication_of_18_disagreements.md`](../results/20260603_prior_art_adjudication_of_18_disagreements.md) — the detailed walk that identified Patterns A/B/C and the specific source quotes for the 17 rows.
- `docs/historical/compendium-source-extracts/results/projections/*.md` — the 9 projection-mapping docs containing `Source quote` fields per atomic indicator. The walk in step 18 reads from these.

### Source-quote retrieval recipe (for step 18)

For each row with `first_introduced_by = <rubric>_<vintage>_projection_mapping.md`:

1. Open `docs/historical/compendium-source-extracts/results/projections/<that_doc>.md`.
2. Search for `Compendium rows:` lines that mention the v2 row_id (the narrow-pass mentions ~5 known renames where the row_id won't match exactly — handle case-by-case; the source-quote block will be near the matching atomic-indicator entry).
3. Locate the `Source quote:` field within the atomic-indicator block.
4. Lift verbatim. Add the rubric+section ref as the YAML key.
5. Initial `prompt:` value is the verbatim quote — the Ralph loop or future sessions evolve it from there.

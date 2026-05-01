# Statute-Extraction Harness — Iteration 1 Implementation Plan

**Goal:** Build the scaffolding that reads OH 2025 statute text from the existing Justia bundle, extracts answers for the 7-row `definitions` compendium chunk, and emits a chunk-level `FieldRequirement` artifact with full provenance — completing one round of the iteration loop.

**Originating conversation:** [`docs/active/statute-extraction/convos/20260501_harness_brainstorm_kickoff.md`](../convos/20260501_harness_brainstorm_kickoff.md)

**Context:** The compendium is the universe; the SMR is keyed to the compendium; framework rubrics (PRI, FOCAL, Sunlight, Newmark, Opheim, CPI, OpenSecrets) are projections from a populated SMR — none privileged. The prior `statute-retrieval` MVP projected past PRI 2010 scores into the compendium-keyed shape; this branch replaces that data source with primary statute reading. The `definitions` chunk is the iter-1 scope because it's the smallest non-trivial chunk (7 rows), exercises the trickiest output shape (`required_conditional` + `condition_text` for §101.70(F)'s "main purposes" qualitative materiality test), and is where two of the prior MVP's known scorer blind spots concentrate.

**Confidence:** Exploratory. We have not yet observed how the bundle-inlined, regime-aware, atomic-per-row extraction shape performs. Iter-1's purpose is to produce inspectable output that drives the next iteration's prompt/scaffolding changes. Architecture choices (4-chunk by domain, regime-aware schema, multi-rubric validation) are well-grounded in prior empirical work and the regime-survey result, but the prompt itself is unobserved.

**Architecture:** Per-chunk subagent dispatch via the Claude Code Agent tool. The OH 2025 statute bundle (~36K tokens) is inlined as the brief's stable prefix — no Read-tool fetches, no files-read sidecar — to remove the dispatch-variance failure mode the prior MVP hit. The variable suffix per chunk is the filtered compendium-row briefs + a v2 scorer prompt. Output: per-`(compendium_row_id, regime, registrant_role)` `FieldRequirement` records.

**Branch:** `statute-extraction` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/statute-extraction/`).

**Tech Stack:** Python 3.12 (uv venv), pydantic v2 (existing models), pytest (existing suite). Reuses `src/scoring/{justia_client,statute_retrieval,statute_loader,bundle,provenance,consistency}.py` + `src/lobby_analysis/{models,compendium_loader}.py`. Adds new modules under `src/scoring/` for the v2 brief builder + extraction-flow orchestrator subcommands.

**Execution model:** Implementing agent follows the Nori workflow (per `CLAUDE.md`). Pre-flight reads `STATUS.md`, `README.md`, this branch's `RESEARCH_LOG.md`, the spawning convo above. Implementation uses TDD via `/Users/dan/.claude/skills/test-driven-development/SKILL.md` — every behavior change is preceded by a red test.

---

## What's in scope for this plan (iter-1 only)

1. v1.3 schema bump: `FieldRequirement` gains `condition_text`, `regime`, `registrant_role` (all `str | None`, default `None`, additive non-breaking).
2. v2 scorer prompt at `src/scoring/scorer_prompt_v2.md` — clean-slate compendium-shape; cherry-picks lessons from v1 per the convo's scorer-prompt-lessons section.
3. New brief-builder `src/scoring/extraction_brief.py` with `build_extraction_brief()` + `reconstruct_brief()`.
4. Extended provenance: `src/scoring/provenance.py` gains `iteration_label`, `prior_run_id`, `changes_from_prior`, `bundle_manifest_sha`, `compendium_csv_sha`, `chunk` fields on the meta record.
5. Orchestrator subcommands `extract-prepare-run` and `extract-finalize-run` forked from the existing `cmd_calibrate_*` pair, writing under `data/extractions/<STATE>/<VINTAGE>/<CHUNK>/<RUN_ID>/`.
6. Three temp-0 dispatches on the `definitions` chunk for OH 2025 (manual dispatch via Claude Code's Agent tool, not part of the orchestrator's automated pipeline at iter-1).
7. The first analysis doc at `docs/active/statute-extraction/results/iter-1_analysis.md` per the convo's template.

## What's explicitly NOT in scope (deferred to later plans)

- **The other 3 chunks** (reporting / registration / contact_log / other) — start small.
- **Full-SMR assembly** (`extract-build-smr`) — needs at least 2 chunks to be meaningful; defer until iter-2 lands a second chunk.
- **The validation tool** (`validate-smr` subcommand, compendium→rubric projection + multi-rubric agreement table). Iter-1's analysis doc can include manual rubric agreement annotations; the automated validation tool is a separate plan.
- **Scaling to other states** (Q7) — defer until OH iteration converges.
- **Per-rubric regime mapping data file** — surfaces in the validation-tool plan.
- **Locking `regime` and `registrant_role` value space** to `Literal[...]` — observe value distribution across multiple states first.

---

## Testing Plan

I will write all tests before any implementation. Tests target **behavior**, not types or mock interactions.

### Schema tests (Phase 0)

- **`test_field_requirement_v1_3_accepts_condition_text`** — Construct a `FieldRequirement` with `status="required_conditional"` and `condition_text="as one of the individual's main purposes"`; assert round-trips through `model_dump_json` → `model_validate_json` byte-for-byte.
- **`test_field_requirement_v1_3_accepts_regime`** — Construct with `regime="legislative"`; assert round-trip; assert `regime=None` is the model's default.
- **`test_field_requirement_v1_3_accepts_registrant_role`** — Same shape for `registrant_role="client_lobbyist"`.
- **`test_field_requirement_v1_2_data_still_loads`** — Load a fixture JSON written under v1.2 (no `condition_text`/`regime`/`registrant_role` keys); assert it deserializes with all three new fields = `None`. **This is the load-bearing non-breaking-change test.** Fixture lives at `tests/fixtures/state_master/oh_2025_v1_2.json` (regenerated from a known-good prior SMR).

### Brief-builder tests (Phase 1)

- **`test_extraction_brief_inlines_full_bundle`** — Given OH 2025 statute bundle (30 sections) + `definitions` chunk filter (7 rows from the real `compendium/disclosure_items.csv`), assert the brief string contains every section's text content verbatim (no Read-tool reference, no truncation).
- **`test_extraction_brief_lists_only_chunk_rows`** — Same input; assert the brief's row-briefs section names exactly the 7 `definitions`-domain row IDs (not all 108 statute-side rows).
- **`test_extraction_brief_includes_v2_scorer_prompt_path`** — Assert the brief references `src/scoring/scorer_prompt_v2.md` (not v1).
- **`test_reconstruct_brief_round_trip`** — Build a brief, save its variable suffix to `brief_suffix.md`, save its bundle manifest sha. Call `reconstruct_brief(suffix_path, bundle_dir, bundle_manifest_sha)`. Assert the reconstructed brief is sha-identical to the original.
- **`test_extraction_brief_includes_v1_3_output_schema`** — Assert the brief's "output schema" section names `condition_text`, `regime`, `registrant_role` as fields the model emits per row.

### Provenance tests (Phase 2)

- **`test_meta_json_includes_iteration_label`** — Build a meta record with `iteration_label="iter-1"`, `prior_run_id=None`, `changes_from_prior="first iteration baseline"`; serialize; assert all three fields present.
- **`test_meta_json_includes_provenance_shas`** — Assert `prompt_sha`, `bundle_manifest_sha`, `compendium_csv_sha`, `chunk` all populate from the inputs and validate as 64-char hex.
- **`test_meta_json_round_trip`** — Serialize then deserialize; assert byte-equality.

### Orchestrator integration tests (Phase 3)

- **`test_extract_prepare_run_writes_brief_and_meta`** — Run `cmd_extract_prepare_run` against `state=OH, vintage=2025, chunk=definitions`; assert `brief_suffix.md` and `meta.json` land at the expected path; assert their content satisfies the brief-builder + provenance contracts.
- **`test_extract_finalize_run_validates_raw_output`** — Given a fixture `raw_output.json` matching the v1.3 `FieldRequirement` shape, finalize → `field_requirements.json` is written + `meta.json` updates with `run_timestamp_utc`. Given an invalid raw_output (missing `legal_citation` field), finalize fails with a clear error.
- **`test_extract_finalize_run_rejects_unknown_compendium_id`** — Raw output references a `compendium_row_id` not in the chunk; finalize fails. (Catches drift between brief and output.)

### Iter-1 integration test (Phase 4)

- **`test_iter1_oh_definitions_run_produces_field_requirements`** — Live dispatch (skipped in CI, runs locally on demand): three subagent dispatches for OH 2025 `definitions` chunk; assert each produces 7+ `FieldRequirement` records (some rows may emit 2× per regime); assert each populated row has a `legal_citation` non-empty; assert no row has a `data/compendium/` (old) path reference. This is the smoke test that the whole pipeline runs end-to-end. **Marked `@pytest.mark.live`; not part of default `uv run pytest`.**

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Bite-Sized Steps

### Phase 0 — v1.3 schema bump

0.1. Read `src/lobby_analysis/models/state_master.py` to locate the existing `FieldRequirement` definition.
0.2. Write `tests/test_models_v1_3.py` with the four schema tests listed above. Run: assert all four fail (`AttributeError` on the new fields).
0.3. Add `condition_text: str | None = None`, `regime: str | None = None`, `registrant_role: str | None = None` to `FieldRequirement`. Run tests: assert all four pass.
0.4. Add the v1.2 fixture at `tests/fixtures/state_master/oh_2025_v1_2.json` (copy from a known-good prior SMR if one exists; otherwise a minimal hand-written stub).
0.5. Run full suite (`uv run pytest`): no regressions on the existing 24+ schema tests. Fix any tests that hardcoded the v1.2 field set.
0.6. Commit: `v1.3 FieldRequirement: add condition_text, regime, registrant_role (additive)`.

### Phase 1 — v2 scorer prompt + brief builder

1.1. Write `src/scoring/scorer_prompt_v2.md`. Cherry-pick from v1 per the convo's "v2 scorer-prompt lessons preserved" section. Output schema names the v1.3 fields. Status enumeration: `required` / `not_required` / `not_addressed` / `required_conditional`. Atomic-per-row rule explicit. **Drop** the files-read sidecar instruction (Rule 7) and the rubric-specific A5–A11 / C0 reading guidance (Rule 6). **Replace** Rule 6 with per-domain extraction notes for the four chunks. Add a clear regime-and-registrant-role emission rule: "if requirements differ across regimes or registrant roles in this state, emit one record per (compendium_row_id, regime, registrant_role) tuple; otherwise emit one record with regime=None and registrant_role=None."
1.2. Write `tests/test_extraction_brief.py` with the brief-builder tests. Run: assert all five fail (module doesn't exist).
1.3. Create `src/scoring/extraction_brief.py` skeleton with `build_extraction_brief()` and `reconstruct_brief()` signatures returning `NotImplementedError`. Run tests: assert they fail with NotImplementedError (not ImportError) — confirms the structure compiles.
1.4. Implement `build_extraction_brief()`:
  - Load the chunk-filtered compendium rows from `compendium/disclosure_items.csv` via `compendium_loader.load_compendium()`, filter by `domain`. (For the `other` chunk, filter on the union: `definitions ∪ financial ∪ revolving_door ∪ relationship`.)
  - Load the statute bundle from `data/statutes/<STATE>/<VINTAGE>/sections/`; build the artifact index (the existing `bundle.py` helper logic, reused).
  - Inline every section's text content into the brief's "statute corpus" section.
  - Render the row-briefs section: id, name, description, data_type, notes per row.
  - Append the v2 scorer-prompt body verbatim + the output-schema reminder.
  - Return the full brief string + a structured suffix-only string (just the chunk-specific portion that would be saved as `brief_suffix.md`).
1.5. Implement `reconstruct_brief()`: load suffix + bundle by manifest_sha → re-render full brief identical to the original.
1.6. Run brief-builder tests: assert all five pass.
1.7. Commit: `v2 scorer prompt + extraction_brief module`.

### Phase 2 — Provenance extension

2.1. Read `src/scoring/provenance.py` to locate the existing `StatuteRunMetadata` model and helper functions.
2.2. Write `tests/test_provenance_v1_3.py` with the three provenance tests. Run: assert they fail.
2.3. Extend `StatuteRunMetadata` (or add a new `ExtractionRunMetadata` if cleaner — decide during implementation based on field overlap). New fields: `iteration_label: str`, `prior_run_id: str | None`, `changes_from_prior: str`, `bundle_manifest_sha: str`, `compendium_csv_sha: str`, `chunk: str`.
2.4. Add helper `compute_compendium_sha(compendium_csv_path) -> str` (sha256 of the CSV file).
2.5. Add helper `compute_bundle_manifest_sha(bundle_dir) -> str` (sha256 of a stable serialization of the artifact index; see existing `bundle.py` for shape).
2.6. Run provenance tests: assert they pass.
2.7. Commit: `provenance v1.3: iteration_label, prior_run_id, bundle/compendium shas, chunk`.

### Phase 3 — Orchestrator extract-prepare-run / extract-finalize-run

3.1. Read `src/scoring/orchestrator.py` `cmd_calibrate_prepare_run` and `cmd_calibrate_finalize_run` to understand the argparse + IO + validation flow.
3.2. Write `tests/test_orchestrator_extract.py` with the three orchestrator tests. Run: assert they fail (subcommands don't exist).
3.3. Implement `cmd_extract_prepare_run(args)`:
  - Args: `--state`, `--vintage`, `--chunk`, `--iteration-label`, `--prior-run-id` (optional), `--changes-from-prior` (optional, default empty string), `--run-id` (optional, auto-generated if absent).
  - Compute paths: `data/extractions/<STATE>/<VINTAGE>/<CHUNK>/<RUN_ID>/`.
  - Build the brief via `build_extraction_brief()`; write `brief_suffix.md` (suffix only, not full brief).
  - Compute provenance shas; write initial `meta.json` (without `run_timestamp_utc`, which finalize stamps).
  - Print the run dir + dispatch instructions for the implementing user.
3.4. Implement `cmd_extract_finalize_run(args)`:
  - Args: `--state`, `--vintage`, `--chunk`, `--run-id`.
  - Load `raw_output.json`; validate every record against `FieldRequirement` v1.3.
  - Reject records whose `compendium_row_id` is not in the chunk's filtered row set (catches brief↔output drift).
  - Write validated records to `field_requirements.json`; stamp `run_timestamp_utc` into `meta.json`.
3.5. Wire the new subcommands into `main()`'s argparse subparsers.
3.6. Run orchestrator tests: assert they pass.
3.7. Run full suite: assert no regressions.
3.8. Commit: `orchestrator: extract-prepare-run + extract-finalize-run subcommands`.

### Phase 4 — Iter-1 dispatch on OH definitions chunk

4.1. Run `uv run python -m scoring.orchestrator --repo-root . extract-prepare-run --state OH --vintage 2025 --chunk definitions --iteration-label iter-1 --changes-from-prior "first iteration baseline"`. Inspect the generated `brief_suffix.md` and `meta.json`. Confirm bundle inlining is correct (statute text visible in the rendered brief, not Read-tool references).
4.2. Dispatch a Claude Code Agent subagent with the brief. Subagent writes `raw_output.json` to the run dir.
4.3. Run `extract-finalize-run` for the same run-id. Confirm `field_requirements.json` is written.
4.4. Repeat 4.1–4.3 for two more `--run-id`s with different auto-generated IDs (3 temp-0 runs total).
4.5. Inspect the three runs' `field_requirements.json`. Note inter-run disagreements per row + per regime.
4.6. Write `docs/active/statute-extraction/results/iter-1_analysis.md` per the template in the convo. Populate the per-row results table for all 7 definitions rows × however many regimes were emitted. Identify weak rows per the flag triggers (citation missing, inter-run disagreement, regime mis-attribution; multi-rubric agreement annotated manually for definitions rows where PRI/CPI/Newmark scored OH historically).
4.7. Update RESEARCH_LOG.md with the iter-1 entry referencing the analysis doc.
4.8. Commit: `iter-1: OH definitions chunk extraction + analysis`.
4.9. Push to origin.
4.10. Surface the analysis doc to the user for review and redirection.

---

## Edge Cases

- **Bundle manifest changes mid-iteration.** If a Justia retrieval re-run produces a different bundle manifest sha while a run is in progress, `cmd_extract_finalize_run` should detect the sha mismatch in `meta.json` and refuse to finalize. Add a check.
- **Chunk filter empty.** If `--chunk` doesn't match any compendium domain, `cmd_extract_prepare_run` should fail with a clear error listing valid chunk names. Add to argparse `choices=[...]`.
- **Compendium row count drift.** If a future compendium curation pass adds/removes rows in the `definitions` domain mid-iteration, the brief and `field_requirements.json` could diverge across runs. The `compendium_csv_sha` in `meta.json` catches this — add a finalize-time check that the current sha matches the run's recorded sha; warn if not.
- **Subagent output is malformed JSON.** `cmd_extract_finalize_run` should print a useful error pointing at the file + line + a suggestion to re-dispatch.
- **Subagent emits a row for a `(compendium_row_id, regime, registrant_role)` tuple that already appeared earlier in the array.** Treat as a hard error — duplicates indicate the model lost track of which combinations it had emitted.
- **`condition_text` populated but `status != "required_conditional"`.** Schema-valid but semantically suspicious. Add a validation warning (not error) at finalize time.
- **`regime` non-null in a state without multiple regimes** (e.g., model emits `regime="general"` for a single-regime state). Should be `None`, not the literal string `"general"`. Add a finalize-time check warning if this fires; the model's emission convention should be `regime=None` when uniform.

## What could change

- **The 4-chunk split.** If iter-1 reveals that the `definitions` chunk hits a specific failure mode that's chunk-cardinality-sensitive (e.g., too few rows for the model to use the chunked context productively), iter-2 might revise to combine chunks or re-cut along different axes. The brief-builder's `domain` filter is one line and easy to refactor.
- **`regime` and `registrant_role` value vocabulary.** The survey doc enumerated 8 regime values and 3 registrant_role values; the harness might emit values not in those lists, OR consistently produce values that suggest a tighter enumeration. After multiple states, lock as `Literal[...]` in v1.4.
- **Bundle inlining cost.** For larger states (CA's lobbying chapter is ~3× OH), the inlined-bundle approach might cross context-window thresholds. Plan-level decision deferred to Q7 / scaling-plan.
- **Schema-bump sequencing.** v1.3 ships `condition_text` + `regime` + `registrant_role` together. If iter-1 reveals that we don't actually need one of these fields (e.g., the harness never populates `registrant_role` for OH), we wouldn't roll it back — additive optional fields cost nothing — but iter-2 would skip exercising it.
- **Three runs vs more.** Q6 settled provisionally on 3 temp-0 runs; if observed variance on iter-1 is high enough that 3-run majority isn't useful, iter-2 might bump to 5 or invoke the 3-model consensus oracle.

## Implementation Details

- All paths in code use `pathlib.Path` rooted at `REPO_ROOT = Path(__file__).resolve().parents[N]` — never hardcoded absolute paths. The test fixtures use `tmp_path` for per-test isolation.
- The brief is a single string returned by `build_extraction_brief()` — no template engine, no jinja. Use Python f-strings + `json.dumps(..., indent=2)` as the existing `bundle.py` does.
- `brief_suffix.md` is the variable portion; the bundle text is NOT saved in the suffix file. `reconstruct_brief()` re-inlines the bundle from disk by `bundle_manifest_sha`.
- Run IDs use the existing `provenance.new_run_id()` helper (12-char hex; collision-free for our scale).
- The `compendium/disclosure_items.csv` lives at repo root (per commit `5537c92` on this branch). The loader's default path is correct; tests should not hardcode `data/compendium/`.
- The Justia retrieval bundle for OH 2025 already exists at `data/statutes/OH/2025/sections/` (30 files, ~143 KB, from the prior `statute-retrieval` branch). No retrieval needed for iter-1.
- Subagent dispatch is **manual** at iter-1 (the user invokes the Agent tool with the generated brief). Auto-dispatch via the orchestrator is a later plan concern.
- The 24/24 compendium tests must stay green; if a v1.3 schema change breaks any of them, fix the test (likely a hardcoded v1.2 field-set assertion) rather than rolling back the schema.
- TDD discipline: every behavior change is preceded by a red test that fails for the right reason. Per `testing-anti-patterns/SKILL.md`, do NOT mock the compendium loader, the schema models, or the bundle artifact reader — use real fixtures.

## Questions

1. **`StatuteRunMetadata` extension vs `ExtractionRunMetadata` new model.** The new fields overlap heavily with the existing `StatuteRunMetadata` (run_id, model_version, state, vintage_year, prompt_sha already present). If the field overlap is ≥80%, extending the existing model is cleaner; if there's substantial divergence (e.g., the existing model has rubric-shaped fields we don't need), a new model is cleaner. **Decision-on-implementation, not blocking the plan.**
2. **Where does the per-rubric regime mapping live for the validation tool?** Surfaces in the next plan (validation tool); not in this plan. Likely candidate: `compendium/rubric_regime_mapping.csv` alongside the dedup map.
3. **For iter-1, do we run all 3 dispatches first and analyze together, or analyze after each?** The convo committed to "3 runs, then measure variance" — implying run-then-analyze is one cycle. If a run obviously fails (e.g., the model emits zero rows), the implementing agent should pause after that run and surface to the user before continuing — don't burn 3 runs on a broken dispatch.
4. **The first iteration has no `prior_run_id`.** `meta.json` records `prior_run_id: null` and `changes_from_prior: "first iteration baseline"`. Confirmed in step 3.3 / 4.1 — but the plan should be explicit: this is the convention.

---

**Testing Details:** All tests target behavior — the schema accepts new fields and round-trips; the brief builder produces a string containing the bundle text and the chunk's row IDs; the reconstruct round-trip is byte-identical; the orchestrator subcommands write the expected files and validate output. No mock-heavy unit tests; every test exercises real fixtures (real compendium CSV, real OH 2025 bundle, real `FieldRequirement` model). The live integration test (4.x) is gated behind `@pytest.mark.live` so CI doesn't dispatch real subagents.

**Implementation Details (max 10 bullets):**
- v1.3 fields are additive, default `None`, do not break v1.2 deserialization.
- v2 scorer prompt drops Rule 6 (rubric-specific) and Rule 7 (files-read sidecar); keeps Rules 1, 2, 4, 5 in spirit.
- Bundle inlined; no Read-tool fetches in the new dispatch path.
- Brief suffix saved separately from bundle for storage efficiency; full brief reconstructible from `(suffix, bundle_manifest_sha)`.
- Provenance meta.json carries run_id, run_timestamp_utc, model_version, state, vintage_year, chunk, prompt_sha, bundle_manifest_sha, compendium_csv_sha, iteration_label, prior_run_id, changes_from_prior.
- Output emits per-(compendium_row_id, regime, registrant_role); `regime=None, registrant_role=None` for state-uniform rows.
- Status enumeration: `required` / `not_required` / `not_addressed` / `required_conditional`.
- Iter-1 scope: 7 rows × 3 runs on OH 2025 `definitions` chunk only.
- Manual subagent dispatch at iter-1; orchestrator auto-dispatch deferred.
- Existing `src/scoring/` infrastructure (Justia retrieval, statute_loader, consistency, provenance helpers) is reused.

**What could change:** The 4-chunk split may revise based on observed dilution; `regime`/`registrant_role` vocabulary may tighten to `Literal[...]`; bundle-inlining cost may force per-regime sub-bundles for larger states; multi-run count may bump from 3 if variance is high.

**Questions:** Listed above (4 items). All resolvable during implementation; none block plan acceptance.

---

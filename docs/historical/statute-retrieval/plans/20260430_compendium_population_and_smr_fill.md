# Compendium Population + Temporary SMR Fill — Implementation Plan

**Goal:** Populate the empty compendium (`CompendiumItem` data file) by unioning the rubric CSVs we already have, then produce a forward-compatible `StateMasterRecord` for OH (and CA, TX) by projecting the existing PRI score data through the populated compendium. The SMR is the load-bearing artifact; PRI is a temporary data source for Stage B that will be replaced by direct statute extraction in a later branch.

**Originating conversation:** `docs/active/statute-retrieval/convos/20260429_sunlight_pri_item_level_calibration.md`

**Context:** Phase 1 calibration confirmed OH's harness output is consistent with both PRI and Sunlight on every overlap cell. The compendium **schema** (`CompendiumItem`, `MatrixCell`) was shipped on the data-model-v1.1 branch (2026-04-22) but **never populated** — no `data/compendium/` directory, no `CompendiumItem` instances. Without a populated compendium, neither the `StateMasterRecord` instances nor the N×50×2 matrix can exist; everything else downstream depends on this. The user's correction during the originating convo: PRI was "first" by accident, but the compendium is the universe and the SMR is keyed to the compendium, not to any one rubric.

**Confidence:** High on the existence of the gap (the compendium is empty; verified). Medium-high on the unioning approach (4 source CSVs are stable artifacts already on main). Medium on the dedup judgment calls (FOCAL indicators vs PRI atomic items have different granularity; resolution is a curation judgment that may need a second-pass review). Lower on whether the temporary PRI-data SMR fill in Stage B is enough for the other fellows' immediate work — we accept that risk for MVP velocity and revisit if Track B feedback says coverage is insufficient.

**Architecture:**
- Stage A: a curated CSV (`data/compendium/disclosure_items.csv`) seeded from PRI 2010 disclosure (61) ∪ PRI 2010 accessibility (22) ∪ FOCAL 2024 (50) ∪ Sunlight 2015 unique (≈3–5 atomic facts), with `framework_references` populated. Loader function reads the CSV and returns `list[CompendiumItem]`.
- Stage B: a projection module (`src/scoring/smr_projection.py`) takes the existing per-item PRI score CSV and the populated compendium, looks up each PRI item's compendium target via `framework_references`, and emits a compendium-keyed `StateMasterRecord`. CLI subcommand `build-smr`.
- The `MatrixCell` projection layer is **out of scope** for this plan; called out as Stage C for a later branch.

**Branch:** `statute-retrieval` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval`)

**Tech stack:** Python 3.12, pydantic v2 (models exist), pytest, click (existing orchestrator pattern). No new dependencies.

---

## Stage A — Populate the compendium

### A.1 Inputs (verify all exist before starting)

- `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/docs/historical/pri-2026-rescore/results/pri_2010_disclosure_law_rubric.csv` (61 items, schema: `item_id, sub_component, item_text, data_type, pri_notes`)
- `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/docs/historical/pri-2026-rescore/results/pri_2010_accessibility_rubric.csv` (22 items)
- `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/docs/historical/focal-extraction/results/focal_2024_indicators.csv` (50 indicators — verify path; the focal-extraction branch was archived on 2026-04-22)
- `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` (5 categories, raw data only — atomic facts must be derived from the methodology paragraph in `papers/text/Sunlight_2015__state_lobbying_disclosure_scorecard.txt`)

### A.2 Output artifact

`/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/data/compendium/disclosure_items.csv`

Schema (matches `CompendiumItem` field-for-field):

```
id,name,description,domain,data_type,framework_references_json,maps_to_state_master_field,maps_to_filing_field,observable_from_database,notes
```

`framework_references_json` is a JSON-encoded `list[FrameworkReference]` per row. Examples:

```
"[{\"framework\":\"pri_2010_disclosure\",\"item_id\":\"E2f_i\",\"item_text\":\"Required component of disclosure report: Direct lobbying costs (compensation).\"},{\"framework\":\"sunlight_2015\",\"item_id\":\"compensation\",\"item_text\":\"Lobbyists disclose earnings received from client/employer for lobbying.\"}]"
```

`id` convention: `<DOMAIN_PREFIX>_<DESCRIPTOR>` in screaming snake case (e.g., `REG_LOBBYIST`, `RPT_LOBBYIST_COMPENSATION`, `RPT_BILL_REFERENCED`, `ACC_PORTAL_DOWNLOAD_BULK`). Stable; never repurposed.

### A.3 Curation steps (the human-judgment work)

This is data curation, not code. The implementing agent walks through each source CSV row and decides where it lands in the compendium. Use the following procedure:

1. **Start from PRI 2010 disclosure-law (61 atomic items).** PRI's atomic granularity is the finest in the source set, so it forms the spine. Each PRI row becomes one compendium row with one `FrameworkReference` to PRI. Compendium `id` is hand-assigned per the convention above.
2. **Walk PRI 2010 accessibility (22 items).** Same treatment. `domain="accessibility"` for these. Each becomes a new compendium row (no overlap with disclosure-law items).
3. **Walk FOCAL 2024 (50 indicators).** For each FOCAL indicator, decide:
   - **Clean 1:1 with an existing PRI item** → add a `FrameworkReference` to FOCAL on the existing compendium row; do not create a new row. The `FrameworkReference.item_id` is FOCAL's indicator id (e.g., `"7"`), and the *expression* in the dedup-mapping artifact (see below) is `"PRI:E1g_i"`.
   - **FOCAL covers what's 2+ PRI items combined (FOCAL is coarser)** → add `FrameworkReference` to FOCAL on each of the underlying PRI compendium rows so all atomic items are reachable from FOCAL. Record the parent indicator in the dedup-mapping artifact as a boolean expression over PRI ids (e.g., FOCAL 7 = `"PRI:E1g_i | PRI:E1g_ii"`). This preserves the "FOCAL is one indicator" semantics that's otherwise lost when its ref is sprinkled across N compendium rows.
   - **FOCAL has a concept PRI doesn't** → create a new compendium row with FOCAL as the only initial `FrameworkReference`. Mapping expression is `"NEW"`.
   - **Border cases worth flagging in `notes`** for review: anything where the granularity decision is debatable.

   **Dedup-mapping artifact:** maintain `data/compendium/framework_dedup_map.csv` alongside the compendium with schema `source_framework, source_item_id, target_expression, notes`. One row per source-rubric item (FOCAL: 50 rows, Sunlight: ≈8 rows after decomposition, PRI accessibility/disclosure: trivially `target_expression="PRI:<self_id>"`, included for completeness). The `target_expression` is a boolean expression over compendium-row references using `&`, `|`, `()`, or the literal `NEW`. This is the audit trail for "did FOCAL flag X?" and the input for any later re-aggregation across rubrics. Curation-time artifact; not loaded into the runtime data model in this plan.
4. **Walk Sunlight 2015 (5 categories → atomic facts).** Use the decomposition already done in `docs/active/statute-retrieval/results/20260429_sunlight_pri_item_level.md` § "Sunlight category → PRI item decomposition" as the starting point:
   - Lobbyist Activity (4 PRI items: E1g_i/ii, E2g_i/ii) — Sunlight category covers all 4. Add `FrameworkReference` to Sunlight on those 4 rows. Sunlight `2` (position-taken) implies a **new** compendium item not in PRI; add `RPT_LOBBYIST_POSITION_DISCLOSED` (or similar) as a new row with FOCAL+Sunlight refs if FOCAL has it, otherwise Sunlight-only.
   - Expenditure Transparency (8 PRI items: E\*f_*) — same treatment. Sunlight's "broad categories vs itemized w/ dates+desc" is finer than PRI's binary `E*f_iv`; add **a new** compendium item `RPT_EXPENDITURE_FORMAT_GRANULARITY` with `data_type="categorical"` and Sunlight as the only ref.
   - Expenditure Reporting Thresholds — **new** compendium item `RPT_EXPENDITURE_ITEMIZATION_THRESHOLD` (Sunlight's concept; PRI's D1 is a different concept — *registration* threshold, not *itemization* threshold; do not unify).
   - Document Accessibility — `domain="accessibility"`; add `FrameworkReference` to Sunlight on PRI 2010 accessibility items where they overlap; new accessibility compendium items where they don't.
   - Lobbyist Compensation — overlaps with PRI E1f_i + E2f_i; add Sunlight ref to those rows.
5. **Set `domain` on every row** using the literal values: `registration | reporting | financial | contact_log | relationship | gift | revolving_door | accessibility | enforcement | other` (per `compendium.py:21`). Bulk-assignable from PRI's `sub_component` column.
6. **Set `data_type`** using `boolean | numeric | categorical | free_text | compound`. PRI's column is mostly `binary` (→ `boolean`); FOCAL is also mostly boolean; Sunlight ordinal categories may be `categorical`.
7. **Set `observable_from_database`**: True for items whose required-status can be inferred from filings (e.g., "Are lobbyists required to disclose phone number?" is True — observe a filing without phone number to know it isn't required); False for items requiring statute reading (e.g., government-exemption B-items).
8. **Leave `maps_to_state_master_field` and `maps_to_filing_field` empty for now** unless trivially obvious. They are needed for the projection layer in Stage B but are not on the critical path of compendium population. Do them in Stage B's first step.

### A.4 Loader code

New file: `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/src/lobby_analysis/compendium_loader.py`

Public API (one function):

```python
def load_compendium(path: Path = DEFAULT_COMPENDIUM_CSV) -> list[CompendiumItem]:
    """Read the compendium CSV and return parsed CompendiumItem instances.
    Raises ValidationError on malformed rows; returns empty list if file missing
    is NOT acceptable (compendium is required infrastructure)."""
```

Default path: `data/compendium/disclosure_items.csv` (relative to repo root).

### A.5 Tests for Stage A (TDD-written first)

- `test_loader_reads_well_formed_compendium_csv` — write a tiny synthetic 3-row CSV to a tmp_path, call `load_compendium`, assert returns 3 valid `CompendiumItem` instances.
- `test_loader_parses_framework_references_json_column` — synthetic row with two framework refs in JSON; assert parsed `framework_references` has both with correct fields.
- `test_loader_raises_on_invalid_domain` — synthetic row with `domain="vibes"`; assert `ValidationError` (the literal type rejects it).
- `test_loader_raises_on_invalid_data_type` — same pattern.
- `test_loader_raises_on_missing_file` — call against a non-existent path; assert `FileNotFoundError`.
- `test_loaded_real_compendium_has_no_duplicate_ids` — loads `data/compendium/disclosure_items.csv` (the real artifact); asserts `id` uniqueness.
- `test_loaded_real_compendium_every_row_has_at_least_one_framework_reference` — every compendium row should reference at least one rubric (orphaned items are a curation bug).
- `test_loaded_real_compendium_includes_all_pri_2010_disclosure_items` — every PRI 2010 disclosure-law `item_id` appears in the framework_references of at least one compendium row. (Same test for PRI accessibility, FOCAL, Sunlight.) These four tests catch curation drops.

NOTE: I will write all tests before I add any implementation behavior.

### A.6 Implementation steps for Stage A

1. Verify all four source CSVs exist at the paths in A.1; verify FOCAL CSV path on the historical/focal-extraction branch.
2. Write the failing tests in `tests/test_compendium_loader.py`.
3. Run; confirm all fail (no module yet).
4. Implement `src/lobby_analysis/compendium_loader.py` against the schema test fixtures only — get the unit tests passing.
5. Curate `data/compendium/disclosure_items.csv` per A.3, starting with PRI disclosure-law as the spine and adding the other rubrics' references row-by-row. Commit incrementally per rubric (one commit for "PRI disclosure-law spine", one for "FOCAL refs added", etc.).
6. Run the four "loaded real compendium" tests; iterate on the CSV until they pass.
7. Commit the final compendium CSV with a clear message documenting the four-rubric union counts.

### A.7 Estimate

Half-day to full-day. The schema work is small; the time is in the curation walkthrough of ~140 rows.

---

## Stage B — Temporary SMR fill (PRI-data source)

**Why "temporary":** the SMR is supposed to be populated by the statute-extraction harness (Phase 3 of `docs/active/statute-retrieval/plans/20260429_multi_rubric_extraction_harness.md`). That harness doesn't exist yet. Stage B uses the per-item PRI score CSVs we already have as a stand-in data source so the other fellows can consume an SMR while the extraction harness is being designed. The SMR's *output shape* is the long-term shape (compendium-keyed); only the data source is temporary.

### B.1 Inputs

- The populated compendium from Stage A.
- The opus-4-7 + files-read-enforced PRI score CSVs:
  - CA: `data/scores/CA/statute/2010/590e9123a624/pri_disclosure_law.csv`
  - TX: `data/scores/TX/statute/2009/4fe9774234f3/pri_disclosure_law.csv`
  - OH: `data/scores/OH/statute/2010/38803d49e32f/pri_disclosure_law.csv`
- The PRI rubric (for item_text): `docs/historical/pri-2026-rescore/results/pri_2010_disclosure_law_rubric.csv`

### B.2 Output artifacts

`data/state_master_records/<state>/<vintage>/<run_id>.json` — one populated `StateMasterRecord` JSON per state. Gitignored (matches `data/scores/` convention).

### B.3 Projection module

New file: `src/scoring/smr_projection.py`

Public API (one entry point):

```python
def project_pri_scores_to_smr(
    pri_score_rows: list[dict],          # parsed pri_disclosure_law.csv rows
    compendium: list[CompendiumItem],    # from compendium_loader.load_compendium()
    state: str,                          # "OH"
    state_name: str,                     # "Ohio"
    vintage: int,                        # 2010
    run_id: str,                         # "38803d49e32f"
) -> StateMasterRecord:
    ...
```

Internal helpers (one per SMR sub-structure):

- `_project_registration_requirements(pri_rows, compendium) -> list[RegistrationRequirement]`
- `_project_de_minimis(pri_rows) -> tuple[float | None, str | None, float | None, str | None]`
- `_project_reporting_parties(pri_rows, compendium) -> list[ReportingPartyRequirement]`
- `_project_field_requirements(pri_rows, compendium) -> list[FieldRequirement]`

Each helper looks up its target compendium item by walking `compendium` and finding the row whose `framework_references` contains a `FrameworkReference(framework="pri_2010_disclosure", item_id=<pri_id>)`. The compendium membership is what makes this forward-compatible: when the statute-extraction harness comes online in a later branch, it emits the same `FieldRequirement` shape but populates `framework_references` with whatever rubrics independently flag the item, not via PRI as the data source.

### B.4 Mapping rules (PRI item → SMR slot via compendium)

| PRI item(s) | SMR slot | Compendium lookup |
|---|---|---|
| A1–A11 | `registration_requirements: list[RegistrationRequirement]` | Walk compendium for items where `domain=="registration"` and `framework_references` includes the PRI A-id; resolve `role` from a fixed A1→lobbyist, A2→volunteer_lobbyist, … map (per `state_master.py:80`). Emit one entry per PRI A-row, with `required = bool(score)` (emit False entries too — Track B needs the negative signal). |
| B1–B4 | `notes` (free-text paragraph) | No compendium-keyed slot. Append a "Government exemptions" paragraph to `StateMasterRecord.notes` summarizing the four B values + citations. |
| C0–C3 | `notes` (free-text paragraph) | Same. |
| D0 | gate; if 0, `de_minimis_*` fields stay None | |
| D1_present + D1_value | `de_minimis_financial_threshold` (float parse), `de_minimis_financial_citation` | |
| D2_present + D2_value | `de_minimis_time_threshold`, `de_minimis_time_citation` | |
| E1a, E2a | `reporting_parties: list[ReportingPartyRequirement]` | E1a → entity_role="client"; E2a → entity_role="lobbyist"; both report_type="activity_report"; filing_status from score. |
| E1h_*, E2h_* | `reporting_frequency` on the matching `ReportingPartyRequirement` | First true frequency wins; multiple → `"other"` + free-text in `notes`. |
| E1b–E1g, E1i, E1j, and E2 counterparts | `field_requirements: list[FieldRequirement]` | Walk compendium for the matching framework reference; resolve `field_path` from `compendium_item.maps_to_state_master_field` (must be populated as the first step of Stage B; see B.6 step 1). `reporting_party` from E1 vs E2 prefix. `status="required"` if score=1, `"not_applicable"` if 0. `framework_references` carried forward from the compendium row (which may include FOCAL, Sunlight, etc., since the compendium is the union — so the SMR row will reference all rubrics that flag this item, not just PRI). `evidence_notes` from CSV `notes`; `legal_citation` from the `evidence_quote` / inline `§…` reference. |

### B.5 Tests for Stage B

- `test_project_a1_lobbyist_required_yields_registration_requirement` — synthetic 1-row CSV with A1=1; assert resulting `RegistrationRequirement(role="lobbyist", required=True)`.
- `test_project_a2_volunteer_not_required_yields_registration_requirement_required_false` — A2=0; assert `required=False`. (Negative signal preserved.)
- `test_project_d_with_threshold_present` — D1_present=1, D1_value="200"; assert `de_minimis_financial_threshold == 200.0`.
- `test_project_d_with_no_threshold` — D1_present=0; assert `de_minimis_financial_threshold is None`.
- `test_project_e1a_creates_client_activity_reporting_party` — E1a=1; assert `ReportingPartyRequirement(entity_role="client", report_type="activity_report", filing_status="required")`.
- `test_project_eh_frequency_picks_quarterly` — E1h_ii=1, others=0; assert `reporting_frequency="quarterly"`.
- `test_project_eh_frequency_multiple_yields_other_with_notes` — multiple E1h_* set; assert `reporting_frequency="other"` + a `notes` field annotating which frequencies were set. **STOP-AND-NOTIFY:** if any real CA/TX/OH PRI CSV row has multiple E1h_* set, do not silently emit `"other"` — pause and surface to the user. Empirically unlikely, but if it happens we want to make the structured-vs-free-text decision deliberately, not by default.
- `test_project_field_requirement_carries_compendium_framework_references` — synthetic compendium with one PRI+FOCAL+Sunlight ref on E2f_i; project a TX-style row with E2f_i=1; assert resulting `FieldRequirement.framework_references` contains all three (compendium union, not just PRI).
- `test_project_field_requirement_score_zero_yields_not_applicable` — score=0; assert `status="not_applicable"`.
- `test_project_field_requirement_carries_legal_citation` — non-empty evidence_quote; assert `legal_citation` populated.
- `test_project_full_oh_smr_validates_against_schema` — load real compendium + real OH PRI CSV; project; assert pydantic validation passes; assert non-empty registration_requirements, reporting_parties, field_requirements; assert `state == "OH"`.
- `test_project_full_smr_round_trips_through_json` — write JSON, load JSON, assert round-trip equivalence.
- Parametrized variant for CA, TX, OH.

NOTE: I will write all tests before I add any implementation behavior.

### B.6 Implementation steps for Stage B

1. **Populate `maps_to_state_master_field` and `maps_to_filing_field` columns on `data/compendium/disclosure_items.csv`** for every E\*-series compendium item (the ones that map to `FieldRequirement.field_path`). This is curation, not code. Document the per-item mapping decisions inline in the `notes` column for any non-obvious choices. Commit.
2. Write the Stage B failing tests in `tests/test_smr_projection.py`. Use synthetic PRI rows + synthetic compendium for unit tests; use the real artifacts for the integration tests.
3. Run; confirm all fail.
4. Implement `_project_registration_requirements`. Run unit tests; pass.
5. Repeat for `_project_de_minimis`, `_project_reporting_parties`, `_project_field_requirements`.
6. Implement `project_pri_scores_to_smr` as the orchestrator that calls each helper.
7. Add `cmd_build_smr` orchestrator subcommand under `src/scoring/orchestrator.py` (existing pattern). Subcommand reads the per-item PRI CSV, calls `compendium_loader.load_compendium()`, calls `project_pri_scores_to_smr`, writes JSON. CLI shape: `build-smr --state OH --vintage 2010 --run-id 38803d49e32f`.
8. Run integration tests (full OH/CA/TX projection). Pass.
9. Manually inspect the OH SMR JSON for sanity. Spot-check: `registration_requirements` for `lobbyist` shows `required=True`; `de_minimis_financial_threshold` matches the published OH lobbyist threshold; the `field_requirements` rows for E2f_i (lobbyist compensation) carry both PRI and Sunlight references in `framework_references` (because OH is `Compensation = -1` per Sunlight; the row should reflect that the rubric flagged it even though OH says no).
10. Run the same projection on CA and TX. Verify.
11. Commit per logical milestone.

### B.7 Estimate

One full day after Stage A is complete. ~30% of the time is in step 1 (the field-path curation), the rest is straightforward TDD.

---

## Stage C — Outside this plan, called out for reference

Two tracks of follow-on work that this plan **deliberately does not include**, but which become clearly possible once Stages A+B ship:

- **Stage C.1: `MatrixCell` projection layer.** A function `project_smr_to_matrix(smr: StateMasterRecord, compendium: list[CompendiumItem]) -> list[MatrixCell]` that emits one `MatrixCell` per (compendium item, this state) pair. Combined across 50 SMRs, this produces the N×50×2 matrix. The `MatrixCell` schema already exists; the projection function is small. Deferred because there's no consumer of the matrix today; ship when Track A or B has an export use case.
- **Stage C.2: Statute-extraction harness (the real Phase 3).** Replaces Stage B's PRI-data source with direct statute extraction. Reads statute text → emits compendium-keyed `FieldRequirement` rows with citations and `framework_references` populated based on which rubrics flag each item (looked up from the compendium). The output `StateMasterRecord` shape is the same as Stage B's; only the upstream data source changes. This is the brainstorm-needed work flagged in `plans/20260429_multi_rubric_extraction_harness.md` § Phase 3. Trigger conditions: (a) Track B reviewers say PRI's coverage isn't enough for their use, or (b) we have a second rubric whose new compendium items the PRI-data fill can't surface (FOCAL likely qualifies once its compendium rows are in).

Stages C.1 and C.2 are independent of each other and can be picked up in either order on separate branches.

---

## What could change

- **Compendium dedup decisions might need a second pass.** The 4-way union is a curation judgment call; a fellow reviewing the compendium output may flag items that should be split or merged. The compendium CSV is the source of truth and is editable; no code changes are needed for curation revisions, but Stage B integration tests may need to be updated if `id`s shift.
- **FOCAL CSV path.** The plan assumes `docs/historical/focal-extraction/results/focal_2024_indicators.csv`. If the actual archived path differs, fix in step A.6.1. (Confirmed via STATUS.md archived-lines table that the branch was archived; haven't yet verified the file path from this worktree.)
- **`maps_to_state_master_field` curation may turn out to be ambiguous for some PRI items.** If we hit a PRI item that doesn't map cleanly to a `LobbyingFiling` field path, leave the field empty and rely on the compendium `id` itself as the identifier. The schema allows `None`. Flag in `notes`.
- **The temporary PRI-data SMR fill is bounded by PRI's coverage.** OH's expenditure-itemization threshold (a Sunlight item) won't appear in the OH SMR until either (a) we hand-curate Sunlight values into the compendium and add a Sunlight-data projection helper to Stage B, or (b) Stage C.2's statute-extraction harness ships and reads the threshold directly. Flag in the OH SMR's `notes` field that this is a known gap.
- **Sunlight asterisk modifiers** (`*`, `^`, `***`) in the published Sunlight CSV are not defined in the methodology document. The compendium curation should not depend on interpreting them; if they end up mattering for a specific row, add a `notes` field documenting the ambiguity.

## Questions to resolve before / during implementation

- **CSV vs YAML for the compendium artifact.** Plan uses CSV to mirror the existing rubric CSVs. YAML is more readable for the `framework_references_json` column (which is JSON in CSV). User confirmed mirroring → CSV. Revisit if curation pain motivates the swap.
- **`maps_to_state_master_field` schema.** The plan defers populating this until Stage B step 1. If the implementing agent finds that the field path conventions need their own design pass (e.g., handling repeated-field paths like `expenditures[].amount`), pause and surface to the user before committing the convention.
- **What `version` string convention to use on `StateMasterRecord.version`.** Proposed: `"pri-2010-baseline-{run_id_short}"` for Stage B's temporary fills; `"compendium-{compendium_version}-{harness_run_id}"` once Stage C.2 ships. Confirm with user on first SMR.
- **Per-state `effective_start` and `effective_end`.** PRI 2010 was scored against ~2009-2010 statutes. For Stage B, set `effective_start = vintage_year`, `effective_end = None` (current). Document in `notes` that the law has likely evolved since the vintage year; the SMR is a baseline, not a real-time read.

---

**Testing details:** Stage A tests verify the loader behavior (read CSV, parse JSON column, reject invalid enums, file not found) and the curation completeness (no duplicate IDs, every row has framework refs, every PRI/FOCAL/Sunlight item is referenced by at least one compendium row). Stage B tests verify the projection behavior end-to-end (PRI score row → correct SMR slot with correct framework references carried from the compendium). All integration tests use the real artifacts (`data/compendium/disclosure_items.csv`, the PRI score CSVs); unit tests use synthetic data. No tests of the pydantic models themselves (already covered in `tests/test_models_v1_1.py`) and no tests that only verify mock behavior.

**Implementation details:**

- All file paths in this plan are absolute paths through the worktree at `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval/`.
- Use the existing `src/scoring/orchestrator.py` click-subcommand pattern for `cmd_build_smr` (mirror `cmd_calibrate`, `cmd_expand_bundle`, etc.).
- Compendium CSV is committed; SMR JSON outputs are gitignored (per `data/scores/` convention).
- The compendium loader does **not** cache — it re-reads the CSV on each call. Curation iterations are cheap; cache complexity isn't justified at this scale.
- No new third-party dependencies. Curation is plain CSV.
- Commit boundary recommendations: per-rubric-spine commits in Stage A (4 commits); per-helper-passing commits in Stage B (5 commits); subcommand + integration test together (1 commit); generated SMR JSONs are gitignored so no commit there.

**Pre-flight check before starting:** confirm `data/compendium/` does not exist; confirm no `StateMasterRecord` JSON files exist anywhere under `data/`; confirm the four source rubric CSVs exist at the documented paths.

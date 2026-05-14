# Chunk-Grouping Function — Implementation Plan

**Goal:** Build `src/lobby_analysis/chunks_v2/` — a `Chunk` frozen dataclass, a hand-curated manifest constant, and a `build_chunks()` function that produces a `list[Chunk]` partitioning the 186-cell registry into ~15 topic-coherent chunks of 2-34 rows each. Pure-data; no LLM calls. Unblocks the brief-writer and informs the scorer-prompt rewrite.

**Originating conversation:** [`../convos/20260514_chunks_brainstorm.md`](../convos/20260514_chunks_brainstorm.md) — Q1–Q7 architectural decisions.
**Antecedent agenda:** [`20260514_chunks_plan_sketch.md`](20260514_chunks_plan_sketch.md).

**Predecessor (just landed):** [`20260514_v2_pydantic_cell_models_implementation_plan.md`](20260514_v2_pydantic_cell_models_implementation_plan.md) produced `src/lobby_analysis/models_v2/` with the 186-entry `CompendiumCellSpec` registry this function consumes.

**Context:** The kickoff brainstorm locked Q1 at "5-12 rows per chunk." This brainstorm **revised** that lock to "~30 cap, hard 34" once the user surfaced the prompt-caching architecture (statute in `system` cached across all chunk-calls for a state-vintage → per-chunk uncached cost is dominated by preamble + per-row instructions + outputs, not by the statute). The manifest below operationalizes the revised constraint.

**Confidence:** High on the manifest structure (verified against the real TSV — 181/181 coverage, no dupes, no typos), the `Chunk` dataclass shape (mirrors `CompendiumCellSpec`), and the testing approach (mirrors cell-models). Medium on the manifest's per-row assignments — implementing agent should refine during TDD where the topic-coherence isn't strong (flagged inline below).

**Architecture:**

```
src/lobby_analysis/chunks_v2/
├── __init__.py     # public exports: Chunk, ChunkDef, build_chunks, CHUNKS_V2
├── chunks.py       # Chunk frozen dataclass + build_chunks() function
└── manifest.py     # CHUNKS_V2: tuple[ChunkDef, ...] — the hand-curated chunk manifest

tests/
├── test_chunks_dataclass.py        # Chunk dataclass behavior
├── test_chunks_manifest.py         # CHUNKS_V2 invariants (coverage, no dupes, sizing)
└── test_chunks_build.py            # build_chunks() function behavior + integration
```

**Branch:** `extraction-harness-brainstorm` (worktree `.worktrees/extraction-harness-brainstorm/`).
**Implementation target:** An API sub-branch (e.g., `extraction-harness-brainstorm/chunks-impl`) that gets merged back to this branch.

**Tech Stack:** Python 3.12, `@dataclass(frozen=True)` (not Pydantic — matches `CompendiumCellSpec`'s pattern; chunks don't need Pydantic's validation features beyond what `__post_init__` provides). pytest, ruff. No new dependencies.

---

## Testing Plan

Written first per TDD. The implementing agent must add ALL tests below before writing ANY implementation code in `src/lobby_analysis/chunks_v2/`.

### `tests/test_chunks_dataclass.py`

Tests the `Chunk` and `ChunkDef` dataclasses in isolation:

1. **Chunk construction with valid fields succeeds.**
   ```python
   def test_chunk_constructs_with_valid_fields():
       from lobby_analysis.models_v2 import CompendiumCellSpec, BinaryCell
       spec = CompendiumCellSpec(
           row_id="law_includes_materiality_test",
           axis="legal",
           expected_cell_class=BinaryCell,
       )
       chunk = Chunk(
           chunk_id="lobbying_definitions",
           topic="What counts as lobbying or a lobbyist",
           cell_specs=(spec,),
           axis_summary="legal",
           notes=None,
       )
       assert chunk.chunk_id == "lobbying_definitions"
       assert chunk.cell_specs == (spec,)
   ```
2. **Chunk is frozen — mutation raises.** `chunk.chunk_id = "x"` raises `FrozenInstanceError` (or whatever `dataclass(frozen=True)` emits — `dataclasses.FrozenInstanceError`).
3. **Chunk `cell_specs` must be a tuple, not a list.** Constructing `Chunk(..., cell_specs=[spec], ...)` raises (enforced via `__post_init__` type check, since `@dataclass` itself doesn't enforce runtime types).
4. **Chunk with empty `cell_specs` raises** in `__post_init__` — a 0-cell chunk is meaningless.
5. **Chunk `axis_summary` must be one of `{"legal", "practical", "mixed"}`** — `__post_init__` raises `ValueError` for other strings.
6. **ChunkDef constructs and validates similarly** but with `member_row_ids: tuple[str, ...]` instead of resolved cell specs (since ChunkDef is the manifest-author-time struct, resolved into Chunk at `build_chunks()` time).

### `tests/test_chunks_manifest.py`

Tests the CHUNKS_V2 manifest constant in isolation (no registry lookup yet):

1. **Manifest is a tuple of ChunkDef.** `assert isinstance(CHUNKS_V2, tuple); assert all(isinstance(c, ChunkDef) for c in CHUNKS_V2)`.
2. **Exactly 15 chunks** (per the plan-locked design; implementer can revise but must update this test in the same commit).
3. **All chunk_ids are unique.** No accidental duplicate manifest entries.
4. **All chunk_ids are snake_case ASCII** matching `^[a-z][a-z0-9_]*$`. Brief-writer's preamble files are keyed by chunk_id and need filesystem-safe names.
5. **Every chunk has ≥ 1 member row_id.** No empty chunks in the manifest.
6. **No row_id appears in two different chunks.** Per-row uniqueness across the manifest.
7. **All chunk sizes are within configured bounds:** 1 ≤ rows ≤ 34. (The hard cap is 34 per the user's `lobbyist_spending_report` approval; 1-row chunks aren't forbidden by Q2 but the current manifest has none — if implementer keeps it that way, this test can tighten to `2 ≤ rows ≤ 34`.)
8. **Manifest entries are ordered deterministically.** Iteration over `CHUNKS_V2` produces the same sequence on every call. (Tuple is intrinsically ordered; this test guards against accidentally using a set or dict during refactor.)

### `tests/test_chunks_build.py`

Tests `build_chunks()` against the real `CompendiumCellSpec` registry:

1. **`build_chunks()` (no args) returns a list of `Chunk` instances** equal in count to `len(CHUNKS_V2)`.
2. **Every `(row_id, axis)` from the 186-cell registry appears in exactly one chunk's `cell_specs`.**
   ```python
   def test_build_chunks_covers_full_registry():
       from lobby_analysis.models_v2 import build_cell_spec_registry
       registry = build_cell_spec_registry()
       all_keys = set(registry.keys())  # 186 (row_id, axis) tuples
       covered_keys = set()
       for chunk in build_chunks():
           for spec in chunk.cell_specs:
               key = (spec.row_id, spec.axis)
               assert key not in covered_keys, f"Duplicate: {key}"
               covered_keys.add(key)
       assert covered_keys == all_keys
   ```
3. **Both halves of all 5 combined-axis rows land in the same chunk** (Q3 decision):
   ```python
   COMBINED_AXIS_ROWS = [
       "lobbyist_registration_required",
       "lobbyist_spending_report_filing_cadence",
       "lobbying_disclosure_audit_required_in_law",
       "lobbying_violation_penalties_imposed_in_practice",
       "registration_deadline_days_after_first_lobbying",
   ]
   def test_combined_axis_rows_in_same_chunk():
       chunks_by_row_id = defaultdict(list)
       for chunk in build_chunks():
           for spec in chunk.cell_specs:
               chunks_by_row_id[spec.row_id].append(chunk.chunk_id)
       for rid in COMBINED_AXIS_ROWS:
           assigned = set(chunks_by_row_id[rid])
           assert len(assigned) == 1, f"{rid} split across chunks: {assigned}"
   ```
4. **Each chunk's `axis_summary` matches its actual cells.**
   - All cells legal → `axis_summary == "legal"`
   - All cells practical → `axis_summary == "practical"`
   - Otherwise (combined-axis rows in chunk, or chunk spans both legal-only and practical-only rows) → `axis_summary == "mixed"`
   Enforced by `build_chunks()`'s resolution logic, asserted in test.
5. **`build_chunks(registry=test_registry)` accepts an injected registry.** Construct a minimal synthetic registry with 2-3 cells, pass to `build_chunks` with a synthetic manifest (or via dependency injection), assert chunk shape.
6. **`build_chunks()` raises if the manifest references a row_id not in the registry.** Construct a `ChunkDef` with a bogus member_row_id, pass to a test helper that runs the resolution. Assert a clear `KeyError` or custom exception.
7. **`build_chunks()` raises if a row in the registry has no chunk assignment.** Inverse of (2): trigger when the manifest doesn't cover the registry. Important for catching TSV growth that wasn't synced to the manifest.
8. **Anchor chunk: the `lobbying_definitions` chunk contains all 6 `def_target_*` rows + both `def_actor_class_*` rows.** Iter-1 continuity check; the v2 `lobbying_definitions` is the spiritual successor to iter-1's 7-row `definitions` chunk.
9. **Anchor chunk: the `lobbyist_spending_report` chunk contains all 34 `lobbyist_spending_*` rows** (the user-approved single-chunk-for-the-whole-cluster decision).
10. **Chunk ordering is stable.** Two calls to `build_chunks()` produce identical lists (same chunk_ids in same order).

### Tests I will NOT write

- Pydantic-style validation behavior (these are plain `@dataclass(frozen=True)`, not Pydantic). The frozen-mutation test catches the only framework feature we rely on.
- Tests that mock `build_cell_spec_registry()`. The chunk-coverage invariant is the test; running against the real registry is the point.
- Tests for chunk-frame preamble content. That's the brief-writer's domain.
- Tests for chunk-id-to-preamble lookup. Same.
- Tests that just assert attribute names (e.g., "`Chunk.chunk_id` exists"). Those test the dataclass framework.

NOTE: All tests written before any implementation, per TDD discipline carried forward from the cell-models plan.

---

## The Manifest (verified against the real TSV)

This manifest covers 181/181 TSV rows = 186/186 cells. Verified by the plan author's coverage script run 2026-05-14 against `compendium/disclosure_side_compendium_items_v2.tsv` at this branch's HEAD. **The implementer should re-run the coverage check (via the manifest tests above) at Phase 0 to confirm no TSV drift since.**

```python
# src/lobby_analysis/chunks_v2/manifest.py

from dataclasses import dataclass

@dataclass(frozen=True)
class ChunkDef:
    """Manifest-author-time chunk definition. Resolved into Chunk at build_chunks() time."""
    chunk_id: str
    topic: str
    member_row_ids: tuple[str, ...]
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.member_row_ids:
            raise ValueError(f"ChunkDef {self.chunk_id!r}: member_row_ids must be non-empty")
        if not self.chunk_id.replace("_", "").isalnum() or not self.chunk_id[0].isalpha():
            raise ValueError(f"ChunkDef chunk_id {self.chunk_id!r} must be snake_case ASCII")


CHUNKS_V2: tuple[ChunkDef, ...] = (
    ChunkDef(
        chunk_id="lobbying_definitions",
        topic="What counts as lobbying or a lobbyist — definitional rows",
        member_row_ids=(
            "lobbying_definition_included_activity_types",
            "lobbyist_definition_included_actor_types",
            "law_defines_public_entity",
            "law_includes_materiality_test",
            "def_target_executive_agency",
            "def_target_executive_staff",
            "def_target_governors_office",
            "def_target_independent_agency",
            "def_target_legislative_branch",
            "def_target_legislative_staff",
            "def_actor_class_elected_officials",
            "def_actor_class_public_employees",
            "public_entity_def_relies_on_charter",
            "public_entity_def_relies_on_ownership",
            "public_entity_def_relies_on_revenue_structure",
        ),
        notes="Spiritual successor to iter-1's 7-row `definitions` chunk. Three sub-axes (TARGET / ACTOR / THRESHOLD-qualitative); preamble will teach the disambiguation.",
    ),
    ChunkDef(
        chunk_id="actor_registration_required",
        topic="Which entity types must register as lobbyists",
        member_row_ids=(
            "actor_executive_agency_registration_required",
            "actor_governors_office_registration_required",
            "actor_independent_agency_registration_required",
            "actor_intergov_agency_lobbying_registration_required",
            "actor_legislative_branch_registration_required",
            "actor_lobbying_firm_registration_required",
            "actor_local_government_registration_required",
            "actor_paid_lobbyist_registration_required",
            "actor_principal_registration_required",
            "actor_public_entity_other_registration_required",
            "actor_volunteer_lobbyist_registration_required",
        ),
        notes="All 11 `actor_*_registration_required` rows. Mechanically uniform: 'is X-type entity required to register?'",
    ),
    ChunkDef(
        chunk_id="registration_thresholds",
        topic="Quantitative gates for lobbyist registration and disclosure",
        member_row_ids=(
            "compensation_threshold_for_lobbyist_registration",
            "expenditure_threshold_for_lobbyist_registration",
            "time_threshold_for_lobbyist_registration",
            "expenditure_itemization_de_minimis_threshold_dollars",
            "lobbyist_filing_de_minimis_threshold_dollars",
            "lobbyist_filing_de_minimis_threshold_time_percent",
        ),
        notes="The quantitative thresholds. Qualitative `law_includes_materiality_test` lives in `lobbying_definitions` since it functions definitionally, not as a numeric gate.",
    ),
    ChunkDef(
        chunk_id="registration_mechanics_and_exemptions",
        topic="Registration process: when, how, who's exempt",
        member_row_ids=(
            "lobbyist_registration_required",
            "lobbyist_registration_renewal_cadence",
            "lobbyist_registration_amendment_deadline_days",
            "registration_deadline_days_after_first_lobbying",
            "separate_registrations_for_lobbyists_and_clients",
            "lobbyist_required_to_submit_photograph_with_registration",
            "exemption_for_govt_official_capacity_exists",
            "exemption_partial_for_govt_agencies",
        ),
        notes="Contains 2 of the 5 combined-axis rows (`lobbyist_registration_required`, `registration_deadline_days_after_first_lobbying`). Mixed axis_summary expected.",
    ),
    ChunkDef(
        chunk_id="lobbyist_registration_form_contents",
        topic="What fields appear on the lobbyist registration form",
        member_row_ids=(
            "lobbyist_reg_form_includes_bill_or_action_identifier",
            "lobbyist_reg_form_includes_business_associations_with_officials",
            "lobbyist_reg_form_includes_compensation",
            "lobbyist_reg_form_includes_employment_type",
            "lobbyist_reg_form_includes_general_subject_matter",
            "lobbyist_reg_form_includes_lobbyist_business_id",
            "lobbyist_reg_form_includes_lobbyist_contact_details",
            "lobbyist_reg_form_includes_lobbyist_full_name",
            "lobbyist_reg_form_includes_lobbyist_legal_form",
            "lobbyist_reg_form_includes_lobbyist_prior_public_offices_held",
            "lobbyist_reg_form_includes_lobbyist_sector",
            "lobbyist_reg_form_includes_position_on_bill",
            "lobbyist_reg_form_lists_each_employer_or_principal",
        ),
        notes="All 13 `lobbyist_reg_form_includes_*` rows. Tight cluster.",
    ),
    ChunkDef(
        chunk_id="lobbyist_spending_report",
        topic="Lobbyist's periodic spending report — cadence, content, format",
        member_row_ids=(
            "lobbyist_spending_report_available_as_downloadable_database",
            "lobbyist_spending_report_available_as_pdf_or_image_on_web",
            "lobbyist_spending_report_available_as_photocopies_from_office_only",
            "lobbyist_spending_report_available_as_searchable_database_on_web",
            "lobbyist_spending_report_cadence_includes_annual",
            "lobbyist_spending_report_cadence_includes_monthly",
            "lobbyist_spending_report_cadence_includes_other",
            "lobbyist_spending_report_cadence_includes_quarterly",
            "lobbyist_spending_report_cadence_includes_semiannual",
            "lobbyist_spending_report_cadence_includes_triannual",
            "lobbyist_spending_report_cadence_other_specification",
            "lobbyist_spending_report_categorizes_expenses_by_type",
            "lobbyist_spending_report_filing_cadence",
            "lobbyist_spending_report_includes_bill_or_action_identifier",
            "lobbyist_spending_report_includes_compensation_broken_down_by_payer",
            "lobbyist_spending_report_includes_contacts_made",
            "lobbyist_spending_report_includes_expenditure_per_issue",
            "lobbyist_spending_report_includes_general_issues",
            "lobbyist_spending_report_includes_general_subject_matter",
            "lobbyist_spending_report_includes_gifts_entertainment_transport_lodging",
            "lobbyist_spending_report_includes_indirect_costs",
            "lobbyist_spending_report_includes_itemized_expenses",
            "lobbyist_spending_report_includes_lobbyist_contact_info",
            "lobbyist_spending_report_includes_position_on_bill",
            "lobbyist_spending_report_includes_principal_business_nature",
            "lobbyist_spending_report_includes_principal_contact_info",
            "lobbyist_spending_report_includes_principal_names",
            "lobbyist_spending_report_includes_specific_bill_number",
            "lobbyist_spending_report_includes_total_compensation",
            "lobbyist_spending_report_includes_total_expenditures",
            "lobbyist_spending_report_required",
            "lobbyist_spending_report_required_when_no_activity",
            "lobbyist_spending_report_scope_includes_household_members_of_officials",
            "lobbyist_spending_report_uses_itemized_format",
        ),
        notes="34 rows. Single chunk per user approval — the cluster is one coherent topic (the report). Contains 1 combined-axis row (`lobbyist_spending_report_filing_cadence`).",
    ),
    ChunkDef(
        chunk_id="principal_spending_report",
        topic="Principal's (employer's) periodic spending report",
        member_row_ids=(
            "principal_spending_report_cadence_includes_annual",
            "principal_spending_report_cadence_includes_monthly",
            "principal_spending_report_cadence_includes_other",
            "principal_spending_report_cadence_includes_quarterly",
            "principal_spending_report_cadence_includes_semiannual",
            "principal_spending_report_cadence_includes_triannual",
            "principal_spending_report_cadence_other_specification",
            "principal_spending_report_includes_business_nature",
            "principal_spending_report_includes_compensation_paid_to_lobbyists",
            "principal_spending_report_includes_contacts_made",
            "principal_spending_report_includes_general_issues",
            "principal_spending_report_includes_gifts_entertainment_transport_lodging",
            "principal_spending_report_includes_indirect_costs",
            "principal_spending_report_includes_lobbyist_contact_info",
            "principal_spending_report_includes_lobbyist_names",
            "principal_spending_report_includes_major_financial_contributors",
            "principal_spending_report_includes_principal_contact_info",
            "principal_spending_report_includes_specific_bill_number",
            "principal_spending_report_includes_total_expenditures",
            "principal_spending_report_required",
            "principal_spending_report_uses_itemized_format",
            "principal_or_lobbyist_reg_form_includes_member_or_sponsor_names",
            "principal_report_lists_lobbyists_employed",
        ),
        notes="21 `principal_spending_*` rows + 2 adjacent principal-side rows that don't fit elsewhere.",
    ),
    ChunkDef(
        chunk_id="lobbying_contact_log",
        topic="Contact-log disclosure: per-meeting records",
        member_row_ids=(
            "lobbying_contact_log_includes_beneficiary_organization",
            "lobbying_contact_log_includes_communication_form",
            "lobbying_contact_log_includes_date",
            "lobbying_contact_log_includes_institution_or_department",
            "lobbying_contact_log_includes_location",
            "lobbying_contact_log_includes_materials_shared",
            "lobbying_contact_log_includes_meeting_attendees",
            "lobbying_contact_log_includes_official_contacted_name",
            "lobbying_contact_log_includes_topics_discussed",
        ),
        notes="All 9 `lobbying_contact_log_*` rows.",
    ),
    ChunkDef(
        chunk_id="other_lobbyist_filings",
        topic="Other lobbyist/principal filings — itemized expenditures, special reports",
        member_row_ids=(
            "lobbyist_or_principal_reg_form_includes_lobbyist_board_memberships",
            "lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE",
            "lobbyist_or_principal_report_includes_time_spent_on_lobbying",
            "lobbyist_or_principal_report_includes_trade_association_dues_or_sponsorship",
            "lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying",
            "lobbyist_itemized_expenditure_identifies_employer_or_principal",
            "lobbyist_itemized_expenditure_identifies_recipient",
            "lobbyist_itemized_expenditure_includes_date",
            "lobbyist_itemized_expenditure_includes_description",
            "lobbyist_report_distinguishes_in_house_vs_contract_filer",
            "lobbyist_report_includes_campaign_contributions",
            "consultant_lobbyist_report_includes_income_by_source_type",
        ),
        notes="Catch-all for lobbyist/principal filing rows not in the two big spending-report chunks. Implementer: consider whether `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying` would fit better in `principal_spending_report` or `lobbyist_spending_report` — flagged as a coherence judgment call.",
    ),
    ChunkDef(
        chunk_id="enforcement_and_audits",
        topic="Does the regime have teeth — penalties and audits",
        member_row_ids=(
            "lobbying_violation_penalties_imposed_in_practice",
            "lobbying_disclosure_audit_required_in_law",
        ),
        notes="Only 2 rows but topically distinct. Implementer: if 2-row chunks feel too granular, merging into `oversight_and_government_subjects` is reasonable. Both rows are combined-axis (4 cells total).",
    ),
    ChunkDef(
        chunk_id="search_portal_capabilities",
        topic="Search & filter capabilities of the state's lobbying portal",
        member_row_ids=(
            "lobbying_search_filter_by_assigned_entity",
            "lobbying_search_filter_by_compensation",
            "lobbying_search_filter_by_funding_source",
            "lobbying_search_filter_by_lobbyist_location",
            "lobbying_search_filter_by_lobbyist_name",
            "lobbying_search_filter_by_misc_expenses",
            "lobbying_search_filter_by_principal",
            "lobbying_search_filter_by_principal_legal_status",
            "lobbying_search_filter_by_principal_location",
            "lobbying_search_filter_by_sector",
            "lobbying_search_filter_by_specific_date",
            "lobbying_search_filter_by_subject",
            "lobbying_search_filter_by_subsector",
            "lobbying_search_filter_by_time_period",
            "lobbying_search_filter_by_total_expenditures",
            "lobbying_search_simultaneous_multicriteria_capability",
        ),
        notes="All 16 `lobbying_search_*` rows. All practical-axis.",
    ),
    ChunkDef(
        chunk_id="data_quality_and_access",
        topic="Portal data quality, format, and downloadability",
        member_row_ids=(
            "lobbying_data_changes_flagged_with_versioning",
            "lobbying_data_current_year_present_on_website",
            "lobbying_data_downloadable_in_analytical_format",
            "lobbying_data_historical_archive_present",
            "lobbying_data_minimally_available",
            "lobbying_data_no_user_registration_required",
            "lobbying_data_open_data_quality",
            "lobbying_data_open_license",
            "lobbying_records_copy_cost_per_page_dollars",
            "sample_lobbying_forms_available_on_web",
        ),
        notes="All practical-axis. The `lobbying_data_open_data_quality` row is a `typed int 0-100 step 25 (practical)` GradedIntCell.",
    ),
    ChunkDef(
        chunk_id="disclosure_documents_online",
        topic="Online accessibility of the disclosure documents themselves",
        member_row_ids=(
            "lobbying_disclosure_data_includes_unique_identifiers",
            "lobbying_disclosure_data_linked_to_other_datasets",
            "lobbying_disclosure_documents_free_to_access",
            "lobbying_disclosure_documents_online",
            "lobbying_disclosure_offline_request_response_time_days",
        ),
        notes="All 5 practical `lobbying_disclosure_*` rows (excluding `lobbying_disclosure_audit_required_in_law` which is in enforcement_and_audits).",
    ),
    ChunkDef(
        chunk_id="lobbyist_directory_and_website",
        topic="Lobbyist directory format and the state's lobbying website itself",
        member_row_ids=(
            "lobbyist_directory_available_as_downloadable_database",
            "lobbyist_directory_available_as_pdf_or_image_on_web",
            "lobbyist_directory_available_as_photocopies_from_office_only",
            "lobbyist_directory_available_as_searchable_database_on_web",
            "lobbyist_directory_update_cadence",
            "online_lobbyist_registration_filing_available",
            "online_lobbyist_spending_report_filing_available",
            "lobbying_website_easily_findable",
            "state_has_dedicated_lobbying_website",
        ),
        notes="All practical-axis. Combines directory format with parent-website-existence rows.",
    ),
    ChunkDef(
        chunk_id="oversight_and_government_subjects",
        topic="Oversight agency activities and government-entity disclosure subjects",
        member_row_ids=(
            "oversight_agency_provides_efile_training",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_filing_deadline",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_industry",
            "oversight_agency_publishes_aggregate_lobbying_spending_by_year",
            "ministerial_diaries_available_online",
            "ministerial_diary_disclosure_cadence",
            "govt_agencies_subject_to_lobbyist_disclosure_requirements",
            "govt_agencies_subject_to_principal_disclosure_requirements",
        ),
        notes="Mixed axis: 6 practical (oversight + ministerial) + 2 legal (govt_agencies). Implementer: this is the chunk most likely to want refinement; if the legal vs practical mix is unwieldy, split `govt_agencies_*` into their own chunk and merge `enforcement_and_audits` into oversight here.",
    ),
)
```

**Coverage assertion** (the implementer's first Phase-0 verification): running this manifest against `build_cell_spec_registry()` produces 186 unique cells with no row_id appearing twice. Verified by plan author on 2026-05-14 against this branch's HEAD TSV.

---

## Steps

### Phase 0 — Scaffolding + coverage verification (15-30 min)

1. Read this plan, the originating brainstorm convo, the plan-sketch, and the cell-models plan (for the TDD discipline pattern). Read `manifest.py`'s draft above closely — the plan author wrote it but the implementer owns it.
2. `git -C .worktrees/extraction-harness-brainstorm status` — confirm clean tree on branch `extraction-harness-brainstorm` (or a sub-branch off it).
3. `uv run pytest -x` — capture baseline pass/skip/fail counts. Expected: 374 pass / 5 skip / 3 pre-existing `test_pipeline.py` failures (per the cell-models implementation convo).
4. **Verify the manifest covers the registry** as a one-off script (not yet a committed test): `python -c "from manifest_draft import CHUNKS_V2; ..."` against the real TSV. If coverage differs from 186/186, the TSV has grown since 2026-05-14 — flag to user before proceeding (the manifest may need a new row assignment).
5. Create the `src/lobby_analysis/chunks_v2/` directory with empty `__init__.py`. Commit "scaffolding: empty chunks_v2 module".

### Phase 1 — Write ALL tests (RED) before any implementation

1. Write `tests/test_chunks_dataclass.py` — all 6 tests above.
2. Write `tests/test_chunks_manifest.py` — all 8 tests above.
3. Write `tests/test_chunks_build.py` — all 10 tests above.
4. Run `uv run pytest tests/test_chunks_*.py`. All should fail with `ModuleNotFoundError` (no `lobby_analysis.chunks_v2` module yet).
5. Commit "tests (RED): full test suite for chunks_v2 layer".

### Phase 2 — Implement `Chunk` and `ChunkDef` dataclasses

1. Implement `src/lobby_analysis/chunks_v2/chunks.py` with:
   - `@dataclass(frozen=True) class Chunk` — fields: `chunk_id: str`, `topic: str`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary: str`, `notes: str | None = None`. `__post_init__` enforces: non-empty `cell_specs`, `cell_specs` is a `tuple` (not list), `axis_summary` ∈ `{"legal", "practical", "mixed"}`, `chunk_id` matches `^[a-z][a-z0-9_]*$`.
   - `@dataclass(frozen=True) class ChunkDef` — fields: `chunk_id: str`, `topic: str`, `member_row_ids: tuple[str, ...]`, `notes: str | None = None`. `__post_init__` enforces: non-empty `member_row_ids`, `chunk_id` regex, `member_row_ids` is a tuple.
2. Run `uv run pytest tests/test_chunks_dataclass.py`. All 6 tests pass.
3. Commit "chunks_v2: Chunk and ChunkDef dataclasses".

### Phase 3 — Add the manifest

1. Implement `src/lobby_analysis/chunks_v2/manifest.py` with the `CHUNKS_V2` constant exactly as drafted above (copy from the plan, paste into the file).
2. Run `uv run pytest tests/test_chunks_manifest.py`. All 8 tests pass.
3. Commit "chunks_v2: CHUNKS_V2 manifest (15 chunks, 186 cells)".

### Phase 4 — Implement `build_chunks()`

1. Implement `src/lobby_analysis/chunks_v2/chunks.py`'s `build_chunks()` function:
   ```python
   def build_chunks(
       registry: dict[tuple[str, str], CompendiumCellSpec] | None = None,
       manifest: tuple[ChunkDef, ...] = CHUNKS_V2,
   ) -> list[Chunk]:
       if registry is None:
           registry = build_cell_spec_registry()
       chunks: list[Chunk] = []
       seen_keys: set[tuple[str, str]] = set()
       for chunk_def in manifest:
           cell_specs: list[CompendiumCellSpec] = []
           axes_in_chunk: set[str] = set()
           for row_id in chunk_def.member_row_ids:
               # A row may appear in registry under "legal", "practical", or BOTH (5 combined-axis rows).
               matched = [(row_id, ax) for ax in ("legal", "practical") if (row_id, ax) in registry]
               if not matched:
                   raise KeyError(
                       f"ChunkDef {chunk_def.chunk_id!r}: row_id {row_id!r} not in registry"
                   )
               for key in matched:
                   if key in seen_keys:
                       raise ValueError(
                           f"Cell {key} assigned to multiple chunks (latest: {chunk_def.chunk_id})"
                       )
                   seen_keys.add(key)
                   cell_specs.append(registry[key])
                   axes_in_chunk.add(key[1])
           axis_summary = (
               "legal" if axes_in_chunk == {"legal"}
               else "practical" if axes_in_chunk == {"practical"}
               else "mixed"
           )
           chunks.append(Chunk(
               chunk_id=chunk_def.chunk_id,
               topic=chunk_def.topic,
               cell_specs=tuple(cell_specs),
               axis_summary=axis_summary,
               notes=chunk_def.notes,
           ))
       missing = set(registry.keys()) - seen_keys
       if missing:
           raise ValueError(
               f"Cells in registry not covered by manifest: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}"
           )
       return chunks
   ```
2. Run `uv run pytest tests/test_chunks_build.py`. All 10 tests pass.
3. Commit "chunks_v2: build_chunks() with full registry coverage validation".

### Phase 5 — Public exports

1. Implement `src/lobby_analysis/chunks_v2/__init__.py` with explicit re-exports:
   ```python
   from .chunks import Chunk, build_chunks
   from .manifest import ChunkDef, CHUNKS_V2

   __all__ = ["Chunk", "ChunkDef", "build_chunks", "CHUNKS_V2"]
   ```
2. Add one smoke test in `tests/test_chunks_init.py`: `from lobby_analysis.chunks_v2 import Chunk, ChunkDef, build_chunks, CHUNKS_V2` succeeds.
3. Run `uv run pytest tests/test_chunks_*.py`. Full chunks suite green.
4. Commit "chunks_v2: __init__ exports".

### Phase 6 — Full-suite green + lint

1. Run `uv run pytest`. Confirm full suite is at baseline + new tests. Expected: pre-existing 374 pass / 5 skip / 3 pre-existing failures → 374 + ~25 new passes / 5 skip / 3 pre-existing failures. **The 3 pre-existing failures must remain identical** (same `test_pipeline.py` `FileNotFoundError`s as before — fixing requires gitignored data not on this branch). Do not "fix" them — they're documented baseline.
2. Run `uv run ruff check src/lobby_analysis/chunks_v2/ tests/test_chunks_*.py` and `uv run ruff format` on the same paths.
3. Commit "chunks_v2: lint + format pass" if anything changed.

### Phase 7 — RESEARCH_LOG + STATUS + finish-convo

1. Update `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` with this session's entry pointing at the convo + plan + commit SHAs.
2. Update **only this branch's row** in `STATUS.md` (multi-committer hygiene).
3. Run finish-convo to commit + push the implementation session's convo summary.

---

## Out of scope for this plan

- The chunk-frame preamble texts themselves (chunk_id → preamble string). That's the brief-writer's domain.
- Brief-writer module that consumes `Chunk` instances.
- Scorer-prompt rewrite.
- Retrieval-agent v2 generalization (parallel component; see [`20260514_retrieval_implementation_plan.md`](20260514_retrieval_implementation_plan.md) once it lands).
- Anthropic SDK adoption.
- `data/` symlink decision.

---

## Edge cases the implementer must handle

- **A `ChunkDef.member_row_ids` entry refers to a row_id not in the registry.** Raise `KeyError` with a clear diagnostic. Tested explicitly.
- **A row in the registry isn't covered by any chunk.** Raise `ValueError` listing missing keys. Tested explicitly. This is the most likely failure mode if the TSV grows.
- **A row is assigned to two different chunks.** Raise `ValueError`. Tested via the `seen_keys` accumulator.
- **A combined-axis row** appears once in `member_row_ids` (the row_id is the key), but resolves to 2 entries in the registry (one per axis). The `build_chunks()` loop's `matched = [(row_id, ax) for ax in ("legal", "practical") if (row_id, ax) in registry]` handles this — both halves land in the same chunk per Q3.
- **An empty manifest** (`CHUNKS_V2 = ()`). `build_chunks()` returns `[]`; coverage check then complains that all 186 cells are uncovered. Fine — caught by tests.
- **`axis_summary` mismatch from chunk content.** The function derives `axis_summary` from the actual cells, so it can't be inconsistent. Test asserts the derivation works for all three cases.
- **Non-deterministic ordering.** `manifest` is a tuple (ordered); `seen_keys` is a `set` but only used for membership tests, not iteration; `chunks` is a `list` built in manifest order. Result: deterministic. Test (#10) asserts this.

---

## Risks + mitigations

- **Risk: the manifest's per-row assignments are wrong in places.** *Mitigation:* the implementer should re-read each ChunkDef's `notes` field and the row's `description` column in the TSV; if a row obviously belongs in a different chunk, move it (in the same commit as the move's test update). The coverage test enforces partition integrity; topic-coherence is the implementer's judgment.
- **Risk: TSV drift since 2026-05-14.** *Mitigation:* Phase 0's coverage script catches new/removed rows immediately. If a row was added, decide its chunk assignment before continuing. If a row was removed, drop it from the manifest.
- **Risk: 2-row `enforcement_and_audits` chunk feels wrong.** *Mitigation:* implementer can merge into `oversight_and_government_subjects` (test updates accordingly: the 15-chunk count becomes 14; that's allowed if surfaced as a deliberate refinement).
- **Risk: dataclass-vs-Pydantic mismatch with `CompendiumCellSpec`.** *Mitigation:* `CompendiumCellSpec` is itself a `@dataclass(frozen=True)` per cell-models plan. Same pattern here. If it turns out `CompendiumCellSpec` is actually Pydantic, switch `Chunk` to Pydantic for type consistency.

---

## How TDD discipline is enforced

- Every test file added before its corresponding implementation file (Phase 1 RED, then Phases 2-5 each turn a slice green).
- Commits ordered: scaffolding → RED → dataclasses → manifest → build_chunks → exports → lint → docs. Read `git log --oneline` on completion to verify the RED-then-GREEN pattern.
- The Phase 1 RED state must be visible in `git log` as a commit. Do NOT add test-and-implementation in the same commit.

---

## Testing Details

Tests target the **invariants** of the chunking design:
- The manifest is well-formed (uniqueness, ordering, regex, sizing).
- `build_chunks()` is deterministic and idempotent.
- The 186-cell registry is partitioned correctly (every cell in exactly one chunk).
- Combined-axis rows have both halves in the same chunk.
- The two anchor chunks (`lobbying_definitions`, `lobbyist_spending_report`) contain the expected member sets.

Tests do NOT target framework behavior (dataclass immutability is tested only via the frozen-mutation test; no tests on `@dataclass` itself).

## Implementation Details

- All new code in `src/lobby_analysis/chunks_v2/`.
- All new tests in `tests/test_chunks_*.py`.
- No new dependencies in `pyproject.toml`.
- Use `@dataclass(frozen=True)` (consistent with `CompendiumCellSpec`); do NOT switch to Pydantic.
- Imports from `lobby_analysis.models_v2` — the `CompendiumCellSpec` registry is the consumed contract.

## What could change

- **Manifest assignments.** Per-row chunk assignments are the implementer's most-likely refinement target. Coverage tests guard the invariants; topic coherence is the implementer's call.
- **Chunk count.** 15 is the plan's number; 14 or 16 are reasonable refinements (e.g., merging `enforcement_and_audits` into `oversight_*`).
- **Combined-axis handling.** If brief-writer brainstorm later reveals splitting combined-axis rows is better, revisit. Q3 is locked for now.
- **`axis_summary` field's value space.** Currently `{"legal", "practical", "mixed"}`. If a "combined" semantic becomes useful (distinct from "mixed legal-and-practical-only rows"), extend then.

## Questions

- **Should `Chunk.cell_specs` preserve manifest order, or sort by `(row_id, axis)`?** Plan: preserve manifest order (matches how a brief-writer would emit the preamble + per-row instructions). Revisit if downstream wants sorted.
- **Should the manifest live in a TSV/YAML data file rather than Python?** Per Q sub-decision in brainstorm: no, Python data. Revisit at ~30+ entries or external-tooling need.
- **Should `enforcement_and_audits` merge into `oversight_*`?** Plan: leave separate (topic distinct). Implementer can merge as a refinement.

---

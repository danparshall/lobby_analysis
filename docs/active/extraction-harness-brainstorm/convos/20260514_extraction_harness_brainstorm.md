# Extraction harness brainstorm: Phase 1 reading + Phase 2 architectural decisions

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Agenda followed:** [`../plans/20260514_kickoff_plan_sketch.md`](../plans/20260514_kickoff_plan_sketch.md) (Phases 1-3 of the brainstorm-then-plan sketch)
**Predecessor convo:** [`20260514_kickoff_orientation.md`](20260514_kickoff_orientation.md)

## Summary

The "real" brainstorm session the orientation convo + plan-sketch were teeing up. Executed Phase 1 (read 7 carry-forward artifacts) and Phase 2 (resolved 6 architectural questions + 1 new one surfaced by the reading). Output of this session: [`../plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](../plans/20260514_v2_pydantic_cell_models_implementation_plan.md) — the first TDD-shaped component plan (Pydantic v2 cell models), confirming the plan-sketch's recommendation.

Mid-session, `compendium-v2-promote` merged to main as `0a6804f`; this branch was merged with main so the canonical `compendium/disclosure_side_compendium_items_v2.tsv` path is live on the worktree before the plan was written.

## Findings from Phase 1 reading

Three findings that materially shaped Phase 2's decisions:

1. **`compendium-v2-promote` was unmerged at session start.** The plan-sketch + orientation convo + RESEARCH_LOG all reference `compendium/disclosure_side_compendium_items_v2.tsv` as the canonical path, but on main at session start the v2 TSV still only lived at `docs/historical/compendium-source-extracts/results/projections/`. Flagged to user; user merged `compendium-v2-promote` mid-session (`0a6804f`); this branch was then `git merge main`'d (matching the pattern `phase-c-projection-tdd` already used). Worktree state at plan-write time: v2 TSV at `compendium/disclosure_side_compendium_items_v2.tsv`, v2 loader `load_v2_compendium() -> list[dict[str, str]]` at `src/lobby_analysis/compendium_loader.py`.

2. **Anthropic SDK is NOT in `pyproject.toml`.** Dependencies are `beautifulsoup4`, `playwright`, `pydantic`, `requests` only. The orchestrator's module docstring explicitly notes "no anthropic SDK." Iter-1 must have worked via Claude Code subagent dispatch (Task tool calling Claude as a subagent), not direct SDK calls. **Decision: the v2 harness inherits this pattern.** Any LLM-calling component writes a brief to disk (per the existing `extraction_brief` module shape) and is dispatched via subagent or external mechanism, not via direct `anthropic.Anthropic()` calls. Adding the SDK is a separate, scoped decision left until/unless there's a clear reason to break the pattern.

3. **The v2 TSV has 5 `legal+practical` rows whose `cell_type` already encodes axis-conditional shapes.** Example: `lobbyist_registration_required` → `binary (legal) + typed int 0-100 step 25 (practical)`. Distribution: 126 legal-only rows + 50 practical-only rows + 5 combined rows. The compendium README phrases the projection-function input as `{row_id: typed_value}` (181 keys) — but a single `row_id` for the 5 combined rows naturally yields two cells with different types. **This issue was not in the plan-sketch's Open Questions section.** Surfaced explicitly to user; user confirmed the cell-ID space should flatten axis into the key.

## Locked Phase 2 decisions

### Q0 (new — surfaced by Phase 1 reading) — Cell ID space

**Decision:** `cell_id = (compendium_row_id, axis_str)` — flat 186-key space (181 rows: 126 legal-only + 50 practical-only get one entry each; 5 legal+practical get two). User-confirmed via AskUserQuestion.

**Rationale:** Phase C projection functions get a flat key space; no nested unwrapping or axis-aware Union types. Combined-row shape variation is absorbed into different cell classes (e.g., `BinaryCell` at `(row_id, "legal")` + `GradedIntCell` at `(row_id, "practical")`) rather than into a single hybrid type. Each cell instance has one typed value.

**Phase C contract:** `phase-c-projection-tdd`'s projection functions consume `dict[tuple[str, str], CompendiumCell]` (or `dict[tuple[str, str], TypedValue]` if they don't care about provenance/conditionality wrappers). The compendium README's `{row_id: typed_value}` phrasing is superseded by this decision — the README should be updated to reflect the (row_id, axis) keying, but that's a coordination item, not a blocker.

### Q1 — Prompt granularity

**Decision:** Hybrid — chunked-by-domain with a chunk-frame preamble per chunk + per-row instruction within the chunk. Chunk size target: 5-12 rows. Same prompt template across all chunks (criterion #2's "same prompt structure"); chunk-specific content lives in the preamble and per-row descriptions.

**Rationale:**
- **Empirical anchor:** iter-1's 7-row `definitions` chunk with chunk-frame preamble (`origin/statute-extraction:src/scoring/chunk_frames/definitions.md`) achieved 93.3% inter-run agreement on 3 temp-0 runs. That's the only data point on prompt granularity we have; throw it out only if Phase 1 reading reveals it shouldn't carry. It does carry — the v2 row IDs cluster naturally by domain prefix (`actor_*`, `def_target_*`, `def_actor_class_*`, `exemption_*`, `lobbyist_*`, `principal_*`, etc.).
- **Cell-type clustering emerges within domain clustering for free.** E.g., the 11 `actor_*_registration_required` rows are all `binary, legal`. The 4 threshold rows (`compensation_threshold_for_lobbyist_registration`, `expenditure_threshold_for_lobbyist_registration`, `expenditure_itemization_de_minimis_threshold_dollars`, `lobbyist_filing_de_minimis_threshold_dollars`) are all `typed Optional[Decimal], legal`. Chunking by domain gets cell-type uniformity within each chunk for free.
- **Same prompt template uniformly applied** preserves criterion #2's "ONE extraction pipeline." Chunk-specific content (preamble + row descriptions) is data, not prompt structure.

**What this rules out:** Per-row prompts (181 LLM calls per (state, vintage) is expensive and loses cross-row context that disambiguates axes), and mega-prompt for all 181 rows (loses focus; iter-1 evidence suggests chunks of ~7 hit a sweet spot).

### Q2 — Retrieval approach

**Decision:** Two-pass retrieval — already-implemented (`src/scoring/retrieval_agent_prompt.md`). Cross-reference walking → whole-bundle scoring. Carry forward.

**Empirical task added to implementation plan:** Before committing the two-pass design as the long-term answer, measure OH 2025's cross-ref-walked statute bundle size and prompt-overhead size vs Claude's context budget. If a 4-vintage same-state set bundles within budget comfortably, two-pass holds. If statute volume crashes the budget for a populous state, revisit RAG-style retrieval (some embedding work was done on the archived `compendium-source-extracts` branch; salvageable).

**Rationale:** Two-pass is the only retrieval design with empirical evidence (iter-1). RAG-style requires embedding infrastructure we don't have. Section-indexed-lookup requires section-locator metadata the v2 rows don't carry. Whole-bundle (single-pass) is what iter-1 effectively was after cross-ref walking; the second pass added cross-ref discovery before scoring. Don't introduce a third retrieval design absent evidence the existing one fails.

### Q3 — State × vintage iteration unit

**Decision:** Per-(state, vintage) as the **deliverable** unit; per-(state, vintage, chunk) as the **execution** unit. One statute bundle per (state, vintage); each chunk reads the bundle once per its own scope.

**Rationale:**
- Statute bundles are naturally per-(state, vintage). Reading the same bundle 181 times to emit one row per call is wasteful.
- `oh-statute-retrieval` is producing OH 2007 + OH 2010 + OH 2015 + OH 2025 (a 4-vintage same-state set for criterion #3 "multi-year reliability"). The harness must run cleanly against all 4 — which is operationally what (a) gives you.
- Within a (state, vintage), executing chunk-by-chunk lets each chunk's LLM call focus on a coherent row family.

**Deliverable per (state, vintage):** A `StateVintageExtraction` object with `cells: dict[tuple[str, str], CompendiumCell]` populated for every (row_id, axis) tuple in the canonical 186-cell roster. Missing cells are explicit `None` in `value` with a status flag, not silent absence — projection functions need to know whether a cell wasn't extracted vs was extracted as null.

### Q4 — v2 Pydantic model shape

**Decision:** New module `src/lobby_analysis/models_v2/` (user-confirmed). Per-cell-type Pydantic subclasses inheriting from a `CompendiumCell` ABC. `StateVintageExtraction` container keyed by `(row_id, axis)` tuple. `ExtractionRun` provenance wrapper around it.

**Module layout:**
```
src/lobby_analysis/models_v2/
├── __init__.py           # public exports
├── cells.py              # CompendiumCell ABC + subclasses (BinaryCell, DecimalCell, IntCell, etc.)
├── extraction.py         # StateVintageExtraction container, ExtractionRun provenance wrapper
└── provenance.py         # EvidenceSpan (citation pointer to statute section/span)
```

**Cell subclasses derived from the v2 TSV's `cell_type` column (29 distinct values, dominated by `binary` at 150/181):**
- `BinaryCell(value: bool)` — 150 rows
- `DecimalCell(value: Decimal | None)` — 5 rows (`typed Optional[Decimal]`)
- `IntCell(value: int | None)` — 2 rows (`typed Optional[int]`, `typed int (practical)`)
- `FloatCell(value: float | None)` — 1 row
- `GradedIntCell(value: int)` with validator `0 <= v <= 100 and v % 25 == 0` — 5+ rows (`typed int 0-100 step 25 (practical)`)
- `BoundedIntCell(value: int)` with validator `0 <= v <= 15` — 1 row
- `EnumCell(value: str)` parameterized by enum domain — for `typed Optional[enum]`, `typed enum` rows
- `EnumSetCell(value: frozenset[str])` — for `typed Set[enum]` rows
- `FreeTextCell(value: str)` — 2 rows
- Specialized: `UpdateCadenceCell`, `TimeThresholdCell`, `TimeSpentCell`, `SectorClassificationCell`, `CountWithFTECell`, `EnumSetWithAmountsCell` — these have richer struct content per cell_type column

**Common cell wrapper fields** (on `CompendiumCell` ABC):
- `cell_id: tuple[str, str]` — (row_id, axis)
- `value: <subclass-specific>` — the typed value
- `conditional: bool = False` — does the statute language make the answer conditional?
- `condition_text: str | None = None` — verbatim qualifier when `conditional=True`
- `confidence: Literal["high", "medium", "low"] | None = None`
- `provenance: EvidenceSpan | None = None` — citation pointer; `None` for not-yet-extracted

A `CompendiumCellSpec(row_id, axis, expected_cell_class)` registry maps each (row_id, axis) in the canonical 186-cell roster to the right `CompendiumCell` subclass. Built from the v2 TSV's `cell_type` + `axis` columns.

**Rationale for separate module (vs in-place):** v1.1 still serves `cmd_build_smr` + `smr_projection` + existing v1 tests (`test_compendium_loader.py`, `test_smr_projection.py`). Separate module keeps v1.1 fully untouched until Phase C retires it; retire-v1 becomes a clean delete commit. User-confirmed via AskUserQuestion.

### Q5 — Conditional / materiality-gate values

**Decision:** Wrapper fields (`conditional: bool` + `condition_text: str | None`), not a cell-type variant.

**Rationale:**
- Conditionality is **orthogonal** to value type. A `BinaryCell` answer can be unconditional ("statute requires registration") or conditional ("statute requires registration if expenditures exceed $X"); same for `DecimalCell`, `EnumCell`, etc. Branching that into `BinaryCell` + `BinaryConditionalCell` would double every cell-type subclass.
- Iter-1's `required_conditional` + verbatim `condition_text` pattern slots in cleanly: when the statute language is conditional, set `conditional=True` and capture the verbatim qualifier in `condition_text`.
- The materiality-gate canary from iter-1 captured this pattern across all 3 OH 2025 runs. The wrapper-field approach generalizes it across all 186 cells.

**What `law_includes_materiality_test` (a `binary, legal` row in the v2 TSV) means under this design:** It's a top-level binary observable about whether the statute *contains* a materiality test anywhere — `BinaryCell(value=True/False)`. Separately, *individual rows* may have `conditional=True` set when the answer to that specific row is gated by a materiality test. Both are useful: the binary cell tells projection functions "this state has a materiality test concept"; the per-cell `conditional` flag tells them "this specific cell's value depends on a conditional in the underlying statute." Independent.

### Q6 — Provenance per cell

**Decision:** Inside the cell wrapper (`provenance: EvidenceSpan | None`), not a parallel keyed structure.

**Rationale:**
- v1.1's `EvidenceSource` already lives inside `FieldRequirement` — established precedent.
- Parallel structures (separate `dict[(row_id, axis), Provenance]`) drift from the cell store over time. Coupling data + provenance prevents that drift.
- Phase C can ignore the `provenance` field if it doesn't care — Python attribute access is cheap, and Phase C's projection functions can read `cell.value` directly.

**`EvidenceSpan` shape** (sketch — settled in TDD): statute section reference (e.g., `"§101.70(B)(1)"`), file/artifact path, optional ≤30-word quoted span, optional URL. Inherits from or replaces v1.1's `EvidenceSource` — decision deferred to the implementation plan's TDD step.

## What this brainstorm produces

[`../plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](../plans/20260514_v2_pydantic_cell_models_implementation_plan.md) — the first TDD-able component plan. Picks the v2 Pydantic cell models as the first build target (plan-sketch's recommendation; reaffirmed). Pure-data; no LLM calls; unblocks both this branch's harness work and Phase C's projection function work. The next downstream component (chunk-grouping function) builds on the cell models' `CompendiumCellSpec` registry; the LLM-calling harness component builds on both.

## Open questions left for downstream

- **Empirical statute-bundle size for OH 2025.** Measure when the implementation plan's Phase 2 (chunk-grouping + spec registry) lands. If bundles fit comfortably, two-pass retrieval holds. If not, revisit Q2.
- **Per-cell enum domain registries.** For `EnumCell` and `EnumSetCell`, each row's enum domain is row-specific (`def_target_executive_agency` has nothing to do with `lobbying_definition_included_activity_types`'s 8-type enum). The cell models need a way to associate each row_id with its enum domain. Likely a separate `enum_domains.py` data file inside `models_v2/`, populated incrementally as we encounter each typed-enum row.
- **Whether to upgrade Phase C's input to typed models or keep raw-dict.** Plan-sketch posed this as a real decision. **Resolution from this session:** ship typed models alongside the raw-dict path. The raw-dict `load_v2_compendium()` stays the v2 contract Phase C starts cold against; this branch adds `load_v2_compendium_typed() -> list[CompendiumCellSpec]` as the typed wrapper. Phase C adopts at its own pace. No coordination friction.
- **`EvidenceSpan` vs `EvidenceSource` reuse.** Defer to plan; either way is fine.
- **Re-using `compendium-v2-promote`'s `compendium/README.md` projection-function input shape phrasing.** The README says `{row_id: typed_value}` but the (row_id, axis) decision supersedes that. Update README in a follow-up commit (not blocking; coordination item).

## Carry-forward predecessor work — disposition

- **Scorer prompt** (`src/scoring/scorer_prompt.md`, on main, v1) — PRI-specific guidance baked in (Rule 6 about A-series and C-series). Will need rewrite for the v2 rubric-agnostic harness. Not a Phase 1 task; happens when the LLM-calling component lands.
- **Retrieval agent prompt** (`src/scoring/retrieval_agent_prompt.md`, on main) — rubric-shaped guidance (referenced PRI items A5-A11, C0-C3). Generalize for v2; should survive structurally — the cross-reference-walking pattern is rubric-agnostic, only the rubric-items-affected field annotations need updating.
- **Chunk-frame definitions preamble** (`origin/statute-extraction:src/scoring/chunk_frames/definitions.md`) — uses v1.2 row IDs (`DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` etc.) **not** v2 names (`def_target_executive_agency` etc.). Will need redoing against v2 row IDs. The 3-axis disambiguation pattern (TARGET / ACTOR / THRESHOLD) carries forward as design template.
- **Iter-1 results** — narrative captured in this branch's RESEARCH_LOG (93.3% inter-run agreement on 7-row chunk; materiality-gate canary worked). Raw extraction data lives in gitignored `data/scores/` on the (paused, not archived) `statute-extraction` branch. Not accessible from this worktree; not needed for the implementation plan.
- **Existing v1.1 models** (`src/lobby_analysis/models/`) — UNTOUCHED. v2 lives in a separate module per Q4 decision.

## Out of scope (carried from plan-sketch)

- Multi-vintage OH statute retrieval — `oh-statute-retrieval`.
- Per-rubric projection functions — `phase-c-projection-tdd`.
- Full 50-state rollout — single-state pilot is this branch's bar.
- New LLM-calling components in the first implementation plan — those wait until pure-data cell models, the cell-spec registry, and chunk-grouping are TDD-ready first.

## Next session

Read [`../plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](../plans/20260514_v2_pydantic_cell_models_implementation_plan.md) and implement the first TDD-able component (Pydantic v2 cell models + `CompendiumCellSpec` registry mapped from the 186-cell roster). All tests written before implementation, per TDD.

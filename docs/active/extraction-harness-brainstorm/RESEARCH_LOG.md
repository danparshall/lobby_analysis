# Research Log: extraction-harness-brainstorm

Created: 2026-05-14
Purpose: Track B successor branch (per Option B locked 2026-05-13). Brainstorm-then-plan: design the **single** extraction harness / prompt architecture per the Compendium 2.0 success criterion #2 ("ONE extraction pipeline — same prompt structure, same model, same retrieval approach, applied uniformly across rows, states, and years"). The v2 row set (181 rows) is the input contract. Goal of this branch's kickoff session: a written plan (`docs/active/extraction-harness-brainstorm/plans/`) ready for the first TDD implementation session.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows. Promoted from `docs/historical/...` to repo-level `compendium/` on 2026-05-14 by the `compendium-v2-promote` branch (live contract for the two parallel-running successors; v1 artifacts retained at `compendium/_deprecated/v1/`). Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). Idempotent regen via `tools/freeze_canonicalize_rows.py`. (Path is live on main after `compendium-v2-promote` merges; until then read via the worktree-local view.)
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #2 (ONE extraction pipeline).
>
> **Carry-forward prompt architecture (from now-dead `statute-extraction` iter-2):** the v2 scorer prompt + chunk-frame preamble (`src/scoring/chunk_frames/definitions.md`) + tightened row-description axis labels. Iter-1 dispatched against OH 2025 `definitions` chunk achieved 93.3% inter-run agreement (3 temp-0 claude-opus-4-7 runs); the materiality-gate canary captured `required_conditional` + verbatim `condition_text` across all three regimes. **Note:** iter-2's tightened row descriptions targeted the v1.2 (141-row) compendium and may need redoing against the v2 (181-row) compendium.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A).
- Per-rubric projection function implementations — that lives on `phase-c-projection-tdd`.
- Full 50-state rollout — this branch's deliverable is a *single-state pilot-ready* plan + harness, not 50-state production scale.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. When this branch's first kickoff session generates gitignored data (e.g., extraction runs, scoring results), the kickoff agent should decide its own symlink approach at that point.

---

## Sessions

(Newest first.)

### 2026-05-14 — Chunks brainstorm-and-plan end-to-end; retrieval brainstorm started

Plan sketches: [`plans/20260514_chunks_plan_sketch.md`](plans/20260514_chunks_plan_sketch.md) + [`plans/20260514_retrieval_plan_sketch.md`](plans/20260514_retrieval_plan_sketch.md)
Brainstorm convos: [`convos/20260514_chunks_brainstorm.md`](convos/20260514_chunks_brainstorm.md) + [`convos/20260514_retrieval_brainstorm.md`](convos/20260514_retrieval_brainstorm.md) (retrieval in progress)
Implementation plan: [`plans/20260514_chunks_implementation_plan.md`](plans/20260514_chunks_implementation_plan.md)
Handoff: [`plans/_handoffs/20260514_retrieval_brainstorm_handoff.md`](plans/_handoffs/20260514_retrieval_brainstorm_handoff.md)

**Session strategy locked by user: brainstorm-and-plan all 4 downstream components in this branch with user-in-loop, then launch implementations as parallel API sub-branches that merge back.** This session covered component 1 (chunks) end-to-end and component 2 (retrieval) plan-sketch + Phase-1-brainstorm only. Two remain after retrieval (brief-writer, scorer-prompt rewrite).

**Chunks (complete).** Brainstorm resolved 7 Q's. **Critical revision** to the prior brainstorm's Q1 (5-12 rows/chunk): user surfaced prompt-caching architecture (statute in cached `system` block, chunk content in uncached `user`), which makes per-chunk cost largely chunk-size-independent. Revised lock: **~30 row soft cap, 34 hard cap** (for the natural `lobbyist_spending_report` single-chunk cluster). Iter-1's 7-row anchor remains an empirical reference point but is no longer a constraint. **Q3:** same chunk for both halves of all 5 combined-axis rows. **Q4:** `list[Chunk]` frozen dataclass (`chunk_id`, `topic`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary`, `notes`). **Q6:** `src/lobby_analysis/chunks_v2/` parallel to `models_v2/`. All locked via AskUserQuestion. Sub-Q's (size bounds Q2, stability mechanism Q5, function signature Q7, manifest storage sub-Q) proposed-and-locked: hand-curated `tuple[ChunkDef, ...]` constant in `manifest.py`; coverage test enforces partition invariant at `build_chunks()` call time; `build_chunks(registry=None) -> list[Chunk]` mirrors cell-models' default-param pattern. **Implementation plan inlines a complete 15-chunk manifest** covering 181/181 rows = 186/186 cells, no duplicates, no typos — verified by plan-author against the real TSV at this branch's HEAD. Chunk sizes range 2 rows (`enforcement_and_audits`, 4 cells via 2 combined-axis rows) to 34 rows (`lobbyist_spending_report`). Spiritual successor to iter-1's 7-row `definitions` chunk is `lobbying_definitions` (15 rows: 6 `def_target_*` + 2 `def_actor_class_*` + 3 `public_entity_def_*` + 4 singletons including `law_includes_materiality_test`).

**Retrieval (in progress).** Plan-sketch enumerates 7 Q's around scope (per-chunk vs per-state-vintage), output schema replacement for `rubric_items_affected`, substantive guidance translation, cell-aware vs cell-agnostic dispatch, deliverable shape (markdown only vs prompt + brief-writer vs prompt + brief-writer + parser), file location. Brainstorm convo's Phase 1 reading complete: identified the v1 prompt's two rubric-coupling sites (Rule 2 "person definition controls A5-A11/C0-C3" substantive anchor; output schema's `rubric_items_affected` field) and computed legal-vs-practical cell breakdown per chunk (5 fully-practical chunks don't need statute retrieval at all). Phase 2 stopped at Q1/Q3/Q6 ask — user wanted to clarify before locking. Four hunches floated in the final exchange (per-chunk retrieval may be cheap under prompt caching; v1 is identify-only not fetch-and-bundle; chunk-level anchors may simplify Q3; per-chunk dispatch may collapse the cell-level output schema in Q2). **User surfaced a load-bearing addendum after the AskUserQuestion:** even if per-chunk dispatch is cheap *per call* under caching, the **aggregate cost** (50 states × ~4 vintages × ~3-5 prompt-tuning iterations × ~10 legal-axis chunks if per-chunk = 6,000-10,000 calls per design cycle, vs ~600-1,000 if per-(state, vintage)) is an order-of-magnitude argument against per-chunk dispatch. This reweights Q1 hunch (i) — the per-call efficiency framing obscured the aggregate-rollout cost. **Next agent finishes this brainstorm + writes the TDD-shaped implementation plan + runs finish-convo;** see [`plans/_handoffs/20260514_retrieval_brainstorm_handoff.md`](plans/_handoffs/20260514_retrieval_brainstorm_handoff.md) for full pickup, including the aggregate-cost lens.

**No code written this session.** Docs only: 6 new files in `docs/active/extraction-harness-brainstorm/` (2 plan sketches, 2 brainstorm convos, 1 implementation plan, 1 handoff). Session is the model for the remaining 2 downstream components (brief-writer, scorer-prompt rewrite) — each follows the same plan-sketch → brainstorm → impl-plan cycle.

**Process notes.** (1) Initial chunks Q1 framing batched 4 options without the "hand-curated manifest" option that ultimately landed — user pushed back on the prompt-caching grounds and asked how many chunks pure first-2-token splitting would produce (53, mostly singletons); revised options exposed the manifest path. (2) Two AskUserQuestion calls hit a UI bug where the user couldn't answer all 4 batched Q's; second call (3 Q's instead of 4) worked cleanly. (3) Initial manifest draft had ~30 row_id typos (missing `_registration_required` suffixes etc.); rebuilt with a coverage-verification script that the implementer should re-run at Phase 0.

**Next session.** Next agent picks up retrieval per handoff. After retrieval lands, components 3 (brief-writer — consumes chunks + cells; orthogonal to retrieval; the cleaner next pick) and 4 (scorer-prompt rewrite — informed by retrieval bundle shape) remain.

### 2026-05-14 — v2 Pydantic cell models implementation (Phases 0-9 under strict TDD)

Convo: [`convos/20260514_v2_pydantic_cell_models_implementation.md`](convos/20260514_v2_pydantic_cell_models_implementation.md)
Plan: [`plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](plans/20260514_v2_pydantic_cell_models_implementation_plan.md)

**Executed the implementation plan end-to-end under strict TDD.** All 68 tests written first (RED, commit `44eee71`), then implementation phases 1-7 turned each phase's tests green in sequence. Phase 8 ran the full suite (374 pass / 5 skip / 3 pre-existing test_pipeline.py failures unchanged from baseline — user-approved). Phase 9 is this entry + STATUS update + finish-convo.

**The deliverable: `src/lobby_analysis/models_v2/` module.** A pure-data typed cell model layer parallel to v1.1 at `src/lobby_analysis/models/` (v1.1 untouched per Q4 decision):

- `cells.py` — `CompendiumCell` ABC (`frozen=True`, wrapper fields: `cell_id`, `conditional`, `condition_text`, `confidence`, `provenance`) + 15 concrete subclasses (BinaryCell, DecimalCell, IntCell, FloatCell, GradedIntCell, BoundedIntCell, EnumCell, EnumSetCell, FreeTextCell + 6 specialized: UpdateCadenceCell, TimeThresholdCell, TimeSpentCell, SectorClassificationCell, CountWithFTECell, EnumSetWithAmountsCell).
- `cell_spec.py` — `CompendiumCellSpec` (frozen dataclass) + `build_cell_spec_registry()` returning the canonical 186-entry `dict[tuple[row_id, axis], CompendiumCellSpec]` (181 TSV rows + 5 legal+practical doublings). Uses a `_CELL_TYPE_PARSER` table + a generic combined-axis splitter — no per-row hard-coding.
- `extraction.py` — `StateVintageExtraction(state, vintage, run_id, cells)` with post-validator enforcing `cell.cell_id` matches its dict key; `ExtractionRun(run_id, model_version, prompt_sha, started_at, completed_at)`.
- `provenance.py` — `EvidenceSpan(section_reference, artifact_path, quoted_span, url)` with 200-char `quoted_span` cap.
- `__init__.py` — public surface: 21 names re-exported.

**Phase 7 cross-module edit:** added `load_v2_compendium_typed() -> list[CompendiumCellSpec]` to `src/lobby_analysis/compendium_loader.py` as the typed wrapper around the registry. Phase C adopts at its own pace; the raw-dict `load_v2_compendium()` is unchanged.

**Specialized cell struct-shape resolution.** The handoff's instruction to read each specialized row's `notes` column turned out to be a partial map of the territory: `notes` carries provenance only (`'single-rubric (focal_2024)'`) or is empty (`UpdateCadenceCell`, `TimeThresholdCell`). Struct shapes live in the source-rubric projection mappings at `docs/historical/compendium-source-extracts/results/projections/{focal_2024,hiredguns_2007,newmark_2017,newmark_2005}_projection_mapping.md`. Surfaced all 6 to user with proposed shapes (anchored to the mappings); user approved all 6. Documented under "Decisions Made" in the convo.

**Unanticipated 7th cell_type.** The TSV has `typed Optional[int_months] (or enum)` for `lobbyist_registration_renewal_cadence` — not catalogued in the plan. User-approved YAGNI mapping to existing `IntCell` (the "months" semantic is documentation; the type stays `int | None`). The "(or enum)" suffix remains in the parser table as documentation.

**Plan's 29-distinct-cell_types claim was off.** Actual: 23 distinct values. Data-driven parser handles this without code change; flagged in convo's Topics Explored.

**Pre-existing CI failures unchanged.** 3 `test_pipeline.py` failures (portal-snapshot fixture data missing — same as on main, same as the previous v2-promote session). User approved leaving them.

**Commits this session (10):** `62daee7` scaffolding → `44eee71` RED tests → `de507f3` EvidenceSpan → `e3de953` ABC+BinaryCell → `5cac6bc` numerics → `ea6faf5` enum/freetext/specialized → `0e1ed2a` registry → `7c882b1` extraction container → `368cc21` exports+typed loader → `c66d808` ruff format pass.

**Next session.** The cell model layer unblocks 4 downstream components (chunk-grouping function, brief-writer module, retrieval-agent v2 generalization, scorer prompt rewrite). Each is its own brainstorm + TDD plan + implementation cycle. Pick one and start with a brainstorm session. SDK-vs-subagent-dispatch decision deferred until the first LLM-calling component lands. Dedicated handoff at [`plans/_handoffs/20260514_next_session_kickoff.md`](plans/_handoffs/20260514_next_session_kickoff.md) — dependency graph, recommendation (chunk-grouping first), cycle convention, and the two deferred decisions (data/ symlink, Anthropic SDK).

### 2026-05-14 — Extraction harness brainstorm (Phase 1 reading + Phase 2 architectural decisions) + first TDD plan

Convo: [`convos/20260514_extraction_harness_brainstorm.md`](convos/20260514_extraction_harness_brainstorm.md)
Plan: [`plans/20260514_v2_pydantic_cell_models_implementation_plan.md`](plans/20260514_v2_pydantic_cell_models_implementation_plan.md)
Antecedent agenda: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**The "real" brainstorm session.** Executed the plan-sketch's Phases 1-3 agenda: read 7 carry-forward artifacts, resolved 6 architectural questions + 1 new one (legal/practical axis split surfaced by Phase 1 reading), wrote the first TDD-able implementation plan.

**Mid-session merge.** `compendium-v2-promote` merged to main as `0a6804f` while this session was running (flagged finding #1: v2 TSV path wasn't actually on main at session start; user merged it mid-session). This branch was then `git merge main`'d to bring the canonical `compendium/disclosure_side_compendium_items_v2.tsv` path live on the worktree before the plan was written, matching `phase-c-projection-tdd`'s pattern (merge, not rebase).

**Phase 2 locked decisions (full rationale in convo).**

- **Q0 (new) — Cell ID space:** `(compendium_row_id, axis_str)` flat 186-key space (181 rows: 126 legal-only + 50 practical-only get one entry; 5 legal+practical get two). User-confirmed via AskUserQuestion. Supersedes `compendium/README.md`'s `{row_id: typed_value}` phrasing for the 5 combined-axis rows.
- **Q1 — Prompt granularity:** Hybrid — chunked-by-domain (5-12 rows) with chunk-frame preambles + per-row instructions, same template across all chunks. Preserves iter-1's empirical 93.3% on the 7-row `definitions` chunk.
- **Q2 — Retrieval approach:** Two-pass (cross-ref walking → bundle scoring), carry forward from `src/scoring/retrieval_agent_prompt.md`. Empirical bundle-size measurement added as downstream task.
- **Q3 — Iteration unit:** Per-(state, vintage) as deliverable unit; per-(state, vintage, chunk) as execution unit. Multi-year reliability tested by running same pipeline against `oh-statute-retrieval`'s 4-vintage OH set.
- **Q4 — v2 Pydantic model shape:** New module `src/lobby_analysis/models_v2/` (user-confirmed); per-cell-type subclasses of `CompendiumCell` ABC; `StateVintageExtraction` container keyed by `(row_id, axis)`; `ExtractionRun` provenance wrapper.
- **Q5 — Conditional / materiality-gate:** Wrapper fields (`conditional: bool`, `condition_text: str | None`), not a cell-type variant. Orthogonal to value type.
- **Q6 — Provenance per cell:** Inside the wrapper (`provenance: EvidenceSpan | None`), not parallel. Matches v1.1 `EvidenceSource`-inside-`FieldRequirement` precedent.

**Findings from Phase 1 reading flagged in convo:**

1. `compendium-v2-promote` was unmerged at session start (resolved mid-session by user merge).
2. **Anthropic SDK is NOT in `pyproject.toml`.** Iter-1 worked via Claude Code subagent dispatch. The v2 harness inherits this pattern; SDK is not added by the first implementation plan.
3. The v2 TSV's 5 `legal+practical` rows carry axis-conditional `cell_type` strings (e.g., `"binary (legal) + typed int 0-100 step 25 (practical)"`), surfacing Q0. Not in plan-sketch's Open Questions; surfaced explicitly to user.

**First implementation plan: v2 Pydantic cell models** (plan-sketch's recommendation, reaffirmed). 9 phases: scaffolding → `EvidenceSpan` → `CompendiumCell` ABC + `BinaryCell` → numeric subclasses → enum/specialized subclasses → `CompendiumCellSpec` registry (186-cell roster) → `StateVintageExtraction` + `ExtractionRun` → `__init__.py` + `load_v2_compendium_typed()` → suite-wide green + lint → RESEARCH_LOG + finish-convo. Pure-data; no LLM calls; unblocks Phase C.

**No code written this session** — docs only: brainstorm convo, implementation plan, this log entry, back-reference annotation in the plan sketch. Implementation work begins in the next session.

### 2026-05-14 — Kickoff orientation + plan sketch (NOT the real brainstorm)

Convo: [`convos/20260514_kickoff_orientation.md`](convos/20260514_kickoff_orientation.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**Originating context.** This branch was assigned plan-sketch work as a side-effect of the 2026-05-14 coordination session on `compendium-v2-promote` (see [`../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available post-merge). User wanted a "solidly sketched" plan in `plans/` so the kickoff agent isn't reading skeleton stubs cold.

**Locked decisions carried forward.** This branch owns the v2 Pydantic model rewrite (model shape = extraction output shape; Phase C consumes as a downstream contract). The v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows × 8 columns). The ⛔ PRI-out-of-bounds banner is gone — PRI is 1 of 8 rubrics on even footing.

**Sketch contents.** Three-phase agenda for the first real brainstorm session: (1) read carry-forward material (existing `src/scoring/scorer_prompt.md` + `retrieval_agent_prompt.md` on main; `chunk_frames/definitions.md` on `origin/statute-extraction`; predecessor harness plan in historical); (2) resolve 6 architectural questions (prompt granularity, retrieval approach, iteration unit, Pydantic model shape, conditional/materiality cell values, provenance per cell); (3) capture decisions in a follow-up implementation plan with a single TDD-able first component picked. **Recommended first component:** v2 Pydantic cell models — pure-data, easy to TDD, unblocks both this branch and Phase C.

**Open questions flagged for the real kickoff.** Does `oh-statute-retrieval` block first end-to-end test? Phase C's preferred input shape (Pydantic models vs raw dicts)? Where does the v2 model module live (in-place at `src/lobby_analysis/models/` vs new `models_v2/`)?

**Not implementation work.** No code, no tests written; only docs (the convo + plan sketch + this RESEARCH_LOG update + the Row-freeze contract path migration).


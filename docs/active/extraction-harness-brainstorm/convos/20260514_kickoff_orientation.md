# Kickoff orientation: extraction-harness-brainstorm

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm

## Summary

This is a **kickoff orientation convo**, not a brainstorm session. The 2026-05-14 coordination session on `compendium-v2-promote` (originating convo: [`../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available on main once that branch merges) checked whether this branch and `phase-c-projection-tdd` would conflict. They don't on core deliverables — but coordination produced two outputs relevant to this branch:

1. **`compendium-v2-promote` landed the v1→v2 deprecation in one place** so this branch starts with a clean v2 contract at a stable repo path (`compendium/disclosure_side_compendium_items_v2.tsv` instead of `docs/historical/...`). The branch's RESEARCH_LOG row-freeze-contract link has been updated this session.
2. **This branch was assigned ownership of the v2 Pydantic model rewrite.** Rationale: model shape = extraction output shape, so the branch designing what gets emitted per row naturally owns the model surgery. Phase C consumes the resulting models as a downstream contract.

This convo exists so the plan in `plans/20260514_kickoff_plan_sketch.md` has an originating-conversation reference per the `write-a-plan` skill. It captures the decisions already locked and the open questions the brainstorm session needs to resolve.

## Locked decisions (from coordination)

- **v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv`** (181 rows × 8 columns: `compendium_row_id`, `cell_type`, `axis`, `rubrics_reading`, `n_rubrics`, `first_introduced_by`, `status`, `notes`). See [`compendium/README.md`](../../../../compendium/README.md) and [`compendium/_deprecated/v1/README.md`](../../../../compendium/_deprecated/v1/README.md) (links resolve post `compendium-v2-promote` merge).
- **This branch owns the v2 Pydantic model rewrite.** The v1.1 models at `src/lobby_analysis/models/` encode PRI-specific Literal enums (registration roles A1–A11, reporting frequency E1h/E2h) and named `de_minimis_*` SMR fields. These need to be rebuilt for v2's cell-typed observable shape.
- **Phase C constraint on output:** projections consume `{compendium_row_id: typed_value}` dicts. Whatever this branch designs as the extraction output shape must be readily mappable to that dict shape — `phase-c-projection-tdd` is the immediate downstream consumer.
- **PRI is no longer out-of-bounds.** The `⛔ AGENT-CRITICAL: PRI 2010 IS OUT OF BOUNDS` STATUS.md banner was removed by `compendium-v2-promote`. PRI is 1 of 8 score-projection rubrics on even footing per ⭐ success criterion #4. The harness reads PRI rows like any other compendium row.
- **Compendium 2.0 success criterion #2 is the bar:** ONE extraction pipeline — same prompt structure, same model, same retrieval approach, applied uniformly across rows, states, and years. Not 9 different pipelines per rubric. See the ⭐ section in [`../../../../STATUS.md`](../../../../STATUS.md).

## Carry-forward material (predecessor work)

The now-paused `statute-extraction` branch (active research lines table in STATUS.md; not archived because the iter-2 design work has standalone value) shipped a prompt-architecture iteration that didn't make it to main:

- **Chunk-frame preamble** — `src/scoring/chunk_frames/definitions.md` on `origin/statute-extraction`. Organizes compendium rows into thematically-related chunks; each chunk gets a frame doc explaining the rows' axes (e.g., the `definitions` chunk frame organizes 7 lobbyist-definition rows along TARGET / ACTOR / THRESHOLD axes). Designed against the v1.2 141-row compendium; **will need redoing against the v2 181-row compendium.**
- **Scorer prompt** — `src/scoring/scorer_prompt.md` (already on main).
- **Retrieval agent prompt** — `src/scoring/retrieval_agent_prompt.md` (already on main).
- **Iter-1 results:** OH 2025 `definitions` chunk, 3 temp-0 claude-opus-4-7 runs, 93.3% inter-run agreement; materiality-gate canary captured `required_conditional` + verbatim `condition_text` across all three regimes.
- **Plan from iter-2 (paused):** `docs/historical/statute-retrieval/plans/20260429_multi_rubric_extraction_harness.md` — predecessor branch's harness plan with the chunk-frame design rationale.

These artifacts are **inspiration, not specification.** The brainstorm session decides which patterns survive against v2 and which need rethinking.

## Open architectural questions (the brainstorm targets)

The next session — the **real** kickoff session — needs to make architectural decisions on at least these axes. The plan sketch in `plans/` enumerates them with non-trivial trade-offs noted.

1. **Prompt granularity.** One prompt for all 181 rows, or chunked by cell_type / domain / axis, or one prompt per row? Iter-1 used chunk-level (7 rows). The chunk-frame preamble pattern argues for chunked; the success criterion #2 ("same prompt structure ... applied uniformly") argues for one canonical prompt template per chunk-size unit.
2. **Retrieval approach.** Whole-statute bundle vs. cross-reference-walked vs. retrieval-augmented? Predecessor work (`statute-retrieval`) ran two-pass: LLM cross-reference discovery → scoring agent against the bundle. Need to decide if that two-pass design survives.
3. **State × vintage iteration shape.** Per-state-per-vintage as the unit of extraction? Or per-row-across-states-and-vintages? The former matches how statute bundles are organized; the latter exploits row-level prompt similarity. Multi-year reliability (success criterion #3) is the harder bar.
4. **Output schema (= v2 Pydantic model shape).** Each cell's typed value (binary / threshold_dollars / threshold_hours / cadence_set / actor_set / activity_set) needs a Pydantic representation. What's the parent container — `ExtractedCompendiumCell`, `CompendiumExtractionRun`, `StateVintageExtraction`? How does it relate to the existing v1.1 `MatrixCell` and `CompendiumItem`?
5. **Materiality gates and qualitative conditions.** Iter-1's materiality-gate canary captured `required_conditional` + `condition_text`. The v2 row contract is binary `cell_type` for most rows but the underlying observable is often conditional. How does the harness emit conditional values?
6. **Confidence + provenance per cell.** The extracted value needs a model-confidence score and a citation pointer back to the source statute span. The v1.1 `EvidenceSource` model captures some of this; needs review for v2 adequacy.

## Phase C downstream constraints

`phase-c-projection-tdd`'s 8 projection functions consume the v2 cells. Each function reads a fixed subset of rows per its `*_projection_mapping.md`:

- CPI 2015 C11 reads 21 rows
- PRI 2010 reads 69 rows
- Sunlight 2015 reads 13 rows
- Newmark 2017 reads 14 rows
- Newmark 2005 reads 14 rows
- Opheim 1991 reads 14 row families / 15 in-scope items
- HG 2007 reads 38 rows
- FOCAL 2024 reads 58 rows

The harness must make the values at these rows readable by projection functions without per-rubric special-casing. **The most-validated row across all 8 is `lobbyist_spending_report_includes_total_compensation`** — if the harness can extract that row correctly for any (state, vintage), 8 projection functions get one data point each.

## Not decided yet

- Whether to spawn a worktree under this branch for the v2 Pydantic model rewrite, or do it inline as the first commit.
- Which state × vintage to target as the pilot (OH 2025 was iter-1's target; `oh-statute-retrieval` will add OH 2007 / OH 2015 to give a 4-vintage same-state set for multi-year reliability testing).

## Next session

The kickoff plan sketch ([`../plans/20260514_kickoff_plan_sketch.md`](../plans/20260514_kickoff_plan_sketch.md)) lays out an ordered brainstorm agenda. Expected output of the kickoff session: an implementation plan (a real one, not a sketch) ready for the first TDD-able harness component.

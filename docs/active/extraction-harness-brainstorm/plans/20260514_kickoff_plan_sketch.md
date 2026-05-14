# Extraction Harness Kickoff Plan Sketch

**Goal:** Get this branch from "skeleton seeded" to "first TDD-able harness component implemented" via a brainstorm-then-plan-then-implement arc.

**Originating conversation:** [`../convos/20260514_kickoff_orientation.md`](../convos/20260514_kickoff_orientation.md) (which itself is a thin handoff from [`../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available on main post-`compendium-v2-promote` merge).

**Context:** Compendium 2.0 landed 2026-05-14 with a 181-row cell-typed contract at `compendium/disclosure_side_compendium_items_v2.tsv`. The next deliverable per success criterion #2 is a single extraction pipeline applied uniformly across rows, states, and vintages. This branch is the brainstorm-then-plan branch for that pipeline. The carry-forward prompt-architecture material from the now-paused `statute-extraction` branch is inspiration, not specification — it was designed against the v1.2 141-row compendium and needs revisiting against v2's different shape (cell-typed observables across legal/practical axes vs. v1.2's yes/no diagnostic items).

**Confidence:** Exploratory. The architectural decisions enumerated below are open questions; this sketch is not a settled design — it's an agenda for the brainstorm session that produces the real plan.

**Architecture:** Single extraction pipeline emitting `{compendium_row_id: typed_value}` cells per (state, vintage). Architectural specifics (prompt granularity, retrieval approach, iteration unit, Pydantic schema, conditional/materiality handling, provenance) are the open questions this branch's first session resolves.

**Branch:** `extraction-harness-brainstorm` (worktree at `.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, `uv` for env, Pydantic 2.x for typed schemas, Anthropic SDK for LLM calls (assumed; verify in brainstorm), `pytest` for tests, `ruff` for lint. Existing carry-forward: `src/scoring/scorer_prompt.md`, `src/scoring/retrieval_agent_prompt.md`, `src/scoring/orchestrator.py` (PRI-MVP subcommands).

---

## Brainstorm agenda (the first real session)

This is **NOT a TDD plan** — it's a sequence of architectural decisions to work through *before* TDD becomes appropriate. Reach a settled answer on each, then capture in a follow-up implementation plan.

### Phase 1 — Read the carry-forward material (~30 min)

Read these artifacts before generating new design ideas. Each captures lessons from the v1.2-era harness work that should inform v2 decisions.

1. **`src/scoring/scorer_prompt.md`** (on main; load-bearing prior art for the prompt structure)
2. **`src/scoring/retrieval_agent_prompt.md`** (on main; two-pass retrieval design)
3. **`docs/historical/statute-retrieval/plans/20260429_multi_rubric_extraction_harness.md`** (predecessor branch's plan with the chunk-frame design rationale)
4. **Chunk-frame example** on `origin/statute-extraction` branch: `git show origin/statute-extraction:src/scoring/chunk_frames/definitions.md`. Read for the axis-disambiguation pattern; **don't port directly** — the row IDs are v1.2 (e.g., `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`), not v2 canonical names.
5. **v2 row contract:** `compendium/disclosure_side_compendium_items_v2.tsv` — read top 30 rows + a sample of each `cell_type` value to grasp the row shape variety.
6. **v2 README:** `compendium/README.md` — the row-shape contract section.
7. **Iter-1 results** (only if accessible): the OH 2025 `definitions` 3-run 93.3%-agreement run. May live in gitignored `data/` from the statute-extraction branch.

### Phase 2 — Resolve architectural questions in order (~2-3 hours)

Each question has non-trivial trade-offs. Reach a decision; capture the rationale in the implementation plan that comes out of this session.

#### Q1 — Prompt granularity

- **Options:** (a) one mega-prompt for all 181 rows, (b) chunked by `cell_type`, (c) chunked by `domain` / `axis` / row-family, (d) one prompt per row, (e) hybrid (chunk preamble + per-row instruction).
- **Trade-offs:** Mega-prompt has the strongest "same prompt structure" property (criterion #2) but worst per-row attention; per-row is the opposite. Iter-1 used row-family chunks with a chunk-frame preamble (option e) and got 93.3% inter-run agreement on the `definitions` chunk — meaningful but not strong evidence (single chunk, single state, single vintage).
- **Open question for brainstorm:** Does the v2 row contract's `cell_type` column give us a natural chunking dimension (group rows by cell_type → same parsing/typing logic across the chunk)? Or does row meaning matter more than cell_type for chunking?

#### Q2 — Retrieval approach

- **Options:** (a) whole-statute bundle (current `statute-retrieval` design), (b) cross-reference-walked sub-bundle (current two-pass design), (c) retrieval-augmented (chunk-and-embed-and-retrieve), (d) section-indexed lookup by row metadata.
- **Trade-offs:** Whole-bundle is simplest but blows context for long statute codes. Two-pass already implemented and gave reasonable results in iter-1. RAG-style requires embedding infrastructure (some embedding work was done on `compendium-source-extracts` and may be salvageable). Section-indexed assumes the v2 rows have section-locator hints, which they don't yet.
- **Open question for brainstorm:** Is statute volume actually the bottleneck? Empirical question — measure OH 2025 statute bundle size, see how much fits in a single Claude context with prompt + 181 row descriptions.

#### Q3 — State × vintage iteration unit

- **Options:** (a) per-(state, vintage) extraction run emitting all 181 cells, (b) per-row across all (state, vintage) pairs, (c) per-chunk per-(state, vintage), matching Q1's chunking choice.
- **Trade-offs:** (a) is operationally simple; one bundle, one extraction, one result. (b) lets you reuse row-specific prompts across many states but reads the bundle 181 times. (c) is the middle ground.
- **Constraint:** `oh-statute-retrieval` is preparing OH 2007 + 2015 + 2025 + 2025 bundles (4-vintage same-state set) for criterion #3 ("multi-year reliability"). The harness must run cleanly against all 4 — that argues for (a) at minimum.

#### Q4 — v2 Pydantic model shape

- **Owned by this branch** (per coordination decision). The v1.1 models at `src/lobby_analysis/models/` use PRI-shaped Literal enums (registration roles A1–A11; reporting frequency E1h/E2h list) and named `de_minimis_*` SMR fields. These break for v2.
- **Sketch direction:** Per-cell-type model classes (`BinaryCell`, `ThresholdDollarsCell`, `ActorSetCell`, etc.) implementing a common `CompendiumCell` ABC; a `StateVintageExtraction` container keyed by `compendium_row_id`; an `ExtractionRun` provenance wrapper around it.
- **Open question for brainstorm:** What does Phase C want as input? Pydantic models, or raw `dict[str, Any]`, or TypedDict? `phase-c-projection-tdd` will start with the raw-dict shape (per `load_v2_compendium()`'s minimal return). Decision: does this branch upgrade Phase C's input to typed models when ready, or does it ship typed models *alongside* the raw-dict path so Phase C can adopt them at its own pace?

#### Q5 — Conditional / materiality-gate values

- The v2 TSV's `cell_type` column treats most rows as `binary` — but real statute language is often conditional ("required if total expenditures exceed $X" or "required when lobbying on more than 3 issues"). Iter-1 added a `required_conditional` value with `condition_text` capturing the verbatim qualifier.
- **Open question for brainstorm:** Does every cell type need a "conditional" variant? Or is conditionality a separate field on the cell wrapper? Where does `condition_text` live?

#### Q6 — Provenance per cell

- The extraction needs to record: which statute section/span the value was extracted from, model confidence, extraction-run ID, vintage, retrieval bundle used.
- The v1.1 `EvidenceSource` model is the obvious starting point.
- **Open question for brainstorm:** Does provenance live inside each cell, or as a parallel `dict[row_id, EvidenceSource]` keyed by the same row IDs? The former couples the data and the provenance, which Phase C may not want to consume; the latter risks them getting out of sync.

### Phase 3 — Capture the architectural decisions in a follow-up plan (~30 min)

Write `plans/20260515_<topic>_implementation_plan.md` (or whatever the brainstorm session's date is). That plan IS TDD-shaped — pick a single first component to build test-first.

**Candidate first components** (pick one for the implementation plan):

- **The Pydantic v2 cell models.** Pure-data, easy to TDD: write tests that construct each cell type with valid + invalid values, assert validation behavior. No LLM calls involved. **Recommended starting point** — unblocks both the harness and Phase C.
- **The v2 row loader extension.** Add `load_v2_compendium_typed()` that returns `list[CompendiumCellSpec]` (typed metadata about each row's expected cell shape). Builds on `load_v2_compendium()` from `compendium-v2-promote`. Also pure-data.
- **The chunk-grouping function.** Given the 181 v2 rows + a chunking strategy (the Q1 decision), return ordered chunks with their frame metadata. Pure-data.
- **A single chunk-frame prompt against a fixed test fixture.** Higher complexity (involves LLM call); meaningful as an end-to-end smoke test. Would benefit from the three pure-data components above being TDD-ready first.

### Out of scope for this branch

Per the kickoff orientation:

- **Multi-vintage OH statute retrieval** — lives on `oh-statute-retrieval` (Track A). This branch consumes the bundles that branch produces.
- **Per-rubric projection functions** — live on `phase-c-projection-tdd`. This branch produces the cells those functions consume.
- **Full 50-state rollout** — this branch's deliverable is a single-state pilot-ready harness, not 50-state production scale.

---

## Testing Plan

Each architectural decision from Phase 2 becomes one or more components in Phase 3's follow-up plan. Each component gets a TDD cycle.

For the Pydantic v2 cell models (the recommended first component):

- I will add unit tests that construct each `CompendiumCell` subclass (`BinaryCell`, `ThresholdDollarsCell`, `ActorSetCell`, etc.) with valid values and assert the constructed instance has the expected attributes.
- I will add unit tests that construct each subclass with *invalid* values (wrong type, out-of-range threshold, set member not in the cell's enumeration) and assert Pydantic validation errors are raised.
- I will add an integration test that loads `compendium/disclosure_side_compendium_items_v2.tsv` via `load_v2_compendium()`, walks all 181 rows, and asserts each row's `cell_type` value maps to a known `CompendiumCell` subclass (no orphan cell types).
- I will NOT write tests that simply assert the data structure has certain keys or that types are typed — those are testing-anti-patterns. Tests must exercise behavior (construction succeeds with valid data, fails with invalid data, all 181 rows have implementations).

NOTE: I will write *all* tests before I add any implementation behavior.

For the harness's LLM-calling components (downstream, post-pure-data work):

- Tests will use real fixture statute text (a small slice of a real state code) rather than mocking the LLM client wholesale. Mocking the LLM defeats the purpose of testing extraction behavior.
- Where mocking is unavoidable (cost / time), tests will use small fixture responses and assert the harness's *behavior given those responses* (e.g., "given this LLM response, the extracted cell has value X and confidence Y") — never assert that the mock was called.

---

## What could change

This is a brainstorm orientation — most of it is provisional by design.

- **Prompt-architecture carry-forward.** If reading the v2 row set against the iter-1 chunk-frame design reveals the chunks don't map (e.g., v2's cell_type-typed observables don't cluster the way v1.2's diagnostic items did), the chunk-frame pattern may be discarded.
- **v2 Pydantic model shape.** Phase C may push back on a particular cell-shape design once they start consuming it for projection logic. The model rewrite is owned here but the contract is shared.
- **Retrieval approach.** Q2's trade-off depends on empirical statute-volume data. If OH 2025's bundle fits comfortably in one Claude context with full prompt overhead, the two-pass design may be overkill.
- **Iter-1 inter-run-agreement (93.3%) baseline.** That number was achieved on a 7-row chunk against a single state-vintage. The v2 181-row contract may have rows whose extraction is fundamentally less stable; the harness's success bar isn't "match 93.3% on every chunk" but "produce reliable enough cells that Phase C projections pass tolerance against published per-state scores."
- **Pydantic 2.x version.** The repo currently has `pydantic==2.13.3`. If a newer feature simplifies the cell-type ABC pattern, may bump.

---

## Open Questions

- **Does `oh-statute-retrieval` block this branch's first end-to-end harness test?** If yes, this branch's first implementable component must be a pure-data one (cell models, loader, chunk-grouping) that can run without statute bundles. If no — i.e., if OH 2025 bundle from main + iter-1 work is sufficient — the first LLM-calling test can land earlier.
- **Is the Anthropic SDK already wired up somewhere in the repo, or does this branch need to add it?** Check `src/scoring/scorer_prompt.md` usage to confirm.
- **Does Phase C want to consume Pydantic models or `dict[str, Any]` (or both)?** Phase C is starting cold against `load_v2_compendium() → list[dict[str, str]]` per `compendium-v2-promote`'s decision. This branch needs to coordinate with Phase C's kickoff to avoid producing models Phase C doesn't want.
- **Provenance: per-cell or parallel structure?** This depends on Phase C's read pattern. If Phase C only ever reads the cell value, parallel-keyed-by-row-id provenance is fine. If Phase C wants to surface "we extracted value X from statute span Y" in its output, per-cell provenance is cleaner.
- **Where does the v2 model rewrite live — `src/lobby_analysis/models/` (existing module) or a new `src/lobby_analysis/models_v2/` to keep v1.1 untouched until phase-c retires it?** Lean toward in-place with clean v2 module-level naming, but worth deciding before commit.

---

**Testing Details.** Pure-data components (Pydantic cell models, chunk-grouping, loader extensions) get unit tests via `pytest` against the real v2 TSV. LLM-calling components get integration tests against fixture statute text. No mocking of internal Pydantic validation logic; no tests that just assert type signatures or dict keys.

**Implementation Details.**

- Branch is in worktree `.worktrees/extraction-harness-brainstorm/`. All path references in implementation plans should be relative or worktree-aware.
- The v2 row contract at `compendium/disclosure_side_compendium_items_v2.tsv` becomes available on this branch after `compendium-v2-promote` merges to main and this branch rebases. **The Row-freeze contract link in this branch's RESEARCH_LOG already points at the new path** — but the file itself isn't on this branch until the rebase happens.
- Existing tests on this branch: 0 (skeleton only). The first implementation plan must add the first tests.
- Don't touch `cmd_build_smr` / `smr_projection` / `load_v1_compendium_deprecated` — those are PRI-MVP and `phase-c-projection-tdd` retires them.

**What could change:** See the "What could change" section above. Headline: prompt granularity, retrieval approach, Pydantic model shape are all open and depend on Phase 1's reading + brainstorm output.

**Questions:** See "Open Questions" above. Headline: does `oh-statute-retrieval` block this branch's first end-to-end test? what's Phase C's preferred input shape? where does the v2 model module live?

---

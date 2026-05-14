# Brief-Writer + Scorer-Prompt-v2 — Plan Sketch (brainstorm agenda)

> **Brainstorm outcome (2026-05-14):** All Q's resolved this session. Full locked package + decision audit trail in [`../convos/20260514_brief_writer_brainstorm.md`](../convos/20260514_brief_writer_brainstorm.md#decisions-made-audit-trail). This document remains the **agenda-shape** record of what was open at session start; the convo is the **outcome-shape** record of what was decided. Read the convo's "Locked package (synthesis)" section for the implementer-facing contract.

**Goal:** Take this branch from "v2 retrieval shipped with Citations + tool use" to "v2 **scoring** harness that consumes a `RetrievalOutput` and produces typed `CompendiumCell` instances per chunk." This sketch is the brainstorm-first agenda; the brainstorm convo resolves the Q's; the implementation plan that follows is the API-launchable artifact.

**Originating handoff:** [`_handoffs/20260514_next_session_kickoff.md`](_handoffs/20260514_next_session_kickoff.md) — the handoff treated this as **two** components (brief-writer = #3 + scorer-prompt-rewrite = #4). Pushed back in the kickoff exchange of [`../convos/20260514_brief_writer_brainstorm.md`](../convos/20260514_brief_writer_brainstorm.md) and user agreed: **combine.** Retrieval's experience (`retrieval_agent_prompt_v2.md` shipped together with `retrieval_v2/brief_writer.py` in one session) is the precedent.

**Sibling component shipped:** [`20260514_retrieval_implementation_plan.md`](20260514_retrieval_implementation_plan.md) — the retrieval brief-writer + prompt + tools + parser + models pattern is the load-bearing template for this component. **Mirror it deliberately.**

**v1 contract (carry-forward):** [`../../../../src/scoring/scorer_prompt.md`](../../../../src/scoring/scorer_prompt.md) + [`../../../../src/scoring/bundle.py`](../../../../src/scoring/bundle.py) — both for legal-bundle scoring (`build_statute_subagent_brief`) and portal scoring (`build_subagent_brief`). Read end-to-end. Key features:

- **v1 dispatch is subagent-via-Read-tool**, not direct SDK. v2 inherits retrieval's pivot to **direct SDK + Citations API + tool use** — user-confirmed in this session's kickoff exchange.
- **v1 has TWO brief-writers** (`build_subagent_brief` for portal, `build_statute_subagent_brief` for statute). v2's scope for this component centers on the **statute / legal-axis path** because that's where retrieval's output is consumed; portal / practical-axis is a related-but-separable design question (see Q6 below).
- **v1 output:** JSON array per rubric item, written to disk by the subagent via Write tool, parsed by `src/scoring/output_writer.py` into stamped CSVs. v2 will replace this with **tool-call-based output** (each `record_*_cell` tool call → one typed `CompendiumCell`), matching retrieval's tool-use pattern.
- **v1 rubric-coupling sites** (the PRI-keyed parts that need v2 replacement):
  1. **Rule 6 substantive guidance** — explicitly anchored to PRI rubric items `A5–A11` (registration coverage) and `C0` (public-entity definition). Multi-paragraph load-bearing prose. The v2 needs an equivalent surface, but anchored to v2 cells (`actor_*_registration_required`, `public_entity_def_*`, `law_defines_public_entity`). **This is the load-bearing scholarly work in the rewrite.**
  2. **Rule 7 files-read manifest** — under v1, the subagent emitted a separate `files_read.json` because the Read tool didn't structurally enforce coverage. Under Citations API, citations on text blocks structurally evidence what was read. Rule 7 may be redundant or may still be useful as a cross-check (Q7).
  3. **Output schema** — v1's `[{item_id, score, evidence_quote_or_url, source_artifact, confidence, unable_to_evaluate, notes}]` per-rubric-item JSON. v2 needs per-cell tool-call shape that maps cleanly to `CompendiumCell` subclasses.
- **Rubric-agnostic surfaces** (carry forward):
  - Rule 5 (read full statute layered: rule → exemption → exception → separate triggers).
  - Confidence as self-assessment, `high`/`medium`/`low`.
  - Notes for audit-trail capture.
  - The "evidence is mandatory" principle (which Citations API now enforces structurally).

**Already-locked context** (carry forward from prior sessions; don't re-litigate):

| Decision | Source | Status |
|----------|--------|--------|
| Combine brief-writer + scorer-prompt rewrite into one component | This session's kickoff exchange | **Locked** |
| Direct SDK + Citations API + tool use (no subagent dispatch) | Retrieval brainstorm Phase 2; reaffirmed this session | **Locked** |
| `anthropic>=0.102` in `pyproject.toml` | Retrieval impl commit `97a3fee`-vicinity | **Live** |
| Model: `claude-opus-4-7`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`, no sampling params | Retrieval brainstorm Q-set | **Locked** |
| Prompt-caching architecture: prompt in system block (cached), statute docs in user (cached via cache_control), per-call text in user (uncached) | Retrieval brief-writer pattern | **Locked** |
| Cell ID space: `(row_id, axis)` flat 186-key space | Kickoff brainstorm Q0 | **Locked** |
| Chunks: 15 chunks, hand-curated manifest, partition invariant | Chunks brainstorm | **Shipped** |
| `CompendiumCell` ABC + 15 concrete subclasses | Cell models impl | **Shipped** |
| Empirical accuracy floor before cost optimization | Retrieval brainstorm Phase 2 | **Locked** |

**Confidence:** Medium-high that the structural shape (brief-writer pattern, tool use, Citations) is settled by retrieval's precedent. **Lower** on the per-chunk preamble + substantive-guidance question (Q4/Q5 below) — this is where the bulk of the scholarly v2-rewrite work lives. **Lower still** on practical-axis cells (Q6) — the v1 portal-brief structure is qualitatively different from the statute path, and may warrant a separate component / brainstorm.

**Branch:** `extraction-harness-brainstorm` (worktree `.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, pytest, ruff, `anthropic>=0.102`, `pydantic`. No new dependencies.

---

## What this component is and isn't

**Is:**

- `src/scoring/scorer_prompt_v2.md` — v2-cell-anchored, rubric-agnostic scoring prompt (replaces v1 `scorer_prompt.md` for the legal-axis path).
- `src/lobby_analysis/scoring_v2/` Python module — parallel to `retrieval_v2/`:
  - `brief_writer.py` — `build_scoring_brief(state, vintage, chunks, retrieval_output, statute_bundle, ...) -> dict` (messages.create() kwargs).
  - `tools.py` — tool schemas for `record_*_cell` (shape decided by Q2).
  - `parser.py` — parses `Message` → `dict[(row_id, axis), CompendiumCell]` + provenance.
  - `models.py` — any scoring-specific Pydantic models (or reuse `models_v2.CompendiumCell` directly — Q9).
  - `docs.md` — module-level docs.
- Per-chunk preamble files (if Q4 lands on "author now") — `src/scoring/chunk_frames_v2/<chunk_id>.md` or similar.

**Isn't:**

- The orchestrator that **dispatches** the scoring brief at runtime — that lives in a downstream component (or `src/scoring/orchestrator.py`'s v2 rewrite, separate).
- The portal-side / practical-axis scoring path **unless Q6 lands on "unify"** — see Q6.
- Output persistence (CSV writing analogous to `output_writer.py`) — the parser produces typed cells in memory; persistence is downstream.
- Full 50-state rollout. This branch's deliverable is a single-state pilot-ready harness.
- The empirical accuracy validation against a single state — that's the implementer's T1+ smoke / T2+ multi-chunk work, downstream.

---

## Brainstorm agenda

### Phase 1 — Carry-forward reading (done in this session's kickoff exchange)

Already read end-to-end:

1. `src/scoring/scorer_prompt.md` — v1 scorer prompt; 8 rules; PRI-keyed Rule 6.
2. `src/scoring/bundle.py` — v1 `build_subagent_brief` / `build_statute_subagent_brief` / `build_retrieval_subagent_brief`. v1 subagent-dispatch pattern.
3. `src/scoring/output_writer.py` — v1 JSON-to-CSV stamping pipeline.
4. `src/lobby_analysis/retrieval_v2/brief_writer.py` + `models.py` — v2 retrieval pattern (load-bearing template).
5. `src/lobby_analysis/chunks_v2/docs.md` — 15-chunk manifest + invariants + the explicit forward reference to brief-writer's per-chunk preamble consumption.
6. `_handoffs/20260514_next_session_kickoff.md` — original 4-component split.

Confirmed during reading: `RetrievalOutput` carries `cross_references: tuple[CrossReference, ...]` and each `CrossReference` has `evidence_spans: tuple[EvidenceSpan, ...]` (machine-grounded citations) + `chunk_ids_affected: tuple[str, ...]` + `relevance: str`. **This is the consumer surface the scoring brief-writer assembles against.**

### Phase 2 — Resolve architectural questions (this session)

#### Q1 — Dispatch unit

Same Q the retrieval brainstorm answered. Options:

- **(a) Parameterized `chunks: list[str]`, default per-chunk** — mirror retrieval. 15 calls per (state, vintage). Lets the brief embed chunk-specific preambles. Empirically defensible: iter-1's 7-row chunk hit 93.3%.
- **(b) Per-(state, vintage) single call** — score all 186 cells in one call. ~15× fewer calls. Risk: prompt size grows; 186 tool calls in one response may strain the model; cross-chunk leakage in scoring reasoning.
- **(c) Per-(state, vintage, chunk-group)** — group chunks by axis (legal / practical / mixed) and dispatch 2-3 calls. Compromise.

Hunch: **(a)**. Same retrieval-side argument applies: accuracy gate before cost optimization; empirical-first; iter-1's 7-row baseline is what we have evidence on.

#### Q2 — Tool use shape

Each scored cell is one `CompendiumCell` instance. The model emits these via tool calls. Options:

- **(a) Single polymorphic `record_cell` tool** — args: `row_id`, `axis`, `value` (loose JSON), `conditional`, `condition_text`, `confidence`, `notes`. Parser dispatches by `row_id` → `expected_cell_class` from `CompendiumCellSpec` → instantiates the right subclass. **Simpler tool schema, validation in Python.**
- **(b) Per-cell-type tools** — `record_binary_cell`, `record_decimal_cell`, `record_enum_cell`, ... 15 tools (one per `CompendiumCell` subclass). Strict per-tool JSON-schema validation. **More verbose tool schemas, less parser branching.** Many subclasses share underlying value type (IntCell vs GradedIntCell vs BoundedIntCell are all int + different range constraints), so this is somewhat redundant.
- **(c) Per-value-family tools** — collapse the 15 subclasses to ~6-7 value families (`record_binary`, `record_int`, `record_decimal`, `record_enum`, `record_enum_set`, `record_free_text`, `record_struct`). Trades strict per-subclass validation for fewer tool definitions.

Sub-question: under Citations API + tool use, do per-tool JSON schemas materially constrain the model, or is the constraint mostly post-hoc validation? (Empirical — depends on Citations + tool use composition behavior, which is what retrieval's T1 will surface.)

Hunch: **(a) single polymorphic tool**, mirroring retrieval (which has 2 tools, not 15). Parser does the cell-class dispatch via `CompendiumCellSpec.expected_cell_class`. Defer (b)/(c) until evidence shows the model is mis-typing values.

#### Q3 — Statute bundle assembly

The scoring brief consumes statute text. The question is which text. Three options:

- **(a) Pass ALL statute files in the bundle** — the same set retrieval started from. Citations API can attribute to any of them. Maximally context-rich; relies on caching to keep cost down.
- **(b) Pass only the statutes cited by retrieval** — use `RetrievalOutput.cross_references[*].evidence_spans` to compute which statute files were cited; pass only those. Narrower context. Smaller prompt, possibly less noise.
- **(c) Pass the statute files PLUS retrieval's annotations** (text summary of `cross_references` with `relevance` + `chunk_ids_affected` + `evidence_spans` excerpted) — gives the scorer the retrieval agent's reasoning trail as context. Risk: the scorer trusts retrieval too much.
- **(d) Pass cited spans only, inline as quoted text** — no document blocks. Smallest context. **Breaks Citations API** (no source documents to cite against). Probably wrong.

Hunch: **(a) ALL statutes + retrieval annotations as user text** — combines (a) and (c). Lets the scorer cross-check retrieval's annotations against the underlying text, with Citations grounding any new spans the scorer emits. Cost is bounded by prompt caching (the statute set is cached after first call).

#### Q4 — Per-chunk preamble strategy

iter-1's `chunk_frames/definitions.md` was a chunk-frame preamble for the 7-row definitions chunk, establishing the TARGET/ACTOR/THRESHOLD sub-axis distinction. `chunks_v2/docs.md` explicitly says: "Future brief-writer module will key per-chunk preamble files by `chunk_id`." Options:

- **(a) Author preambles for all 15 chunks now** — substantial scholarly work; ~15 markdown files of substantive guidance. Equivalent in scope to rewriting v1 Rule 6 fifteen times. **High effort; gives the model the strongest grounding.**
- **(b) Author preambles only for chunks that need them** — start with the 2-3 chunks where substantive disambiguation is critical (`lobbying_definitions`, `lobbyist_spending_report`, `actor_registration_required`?). Other chunks get no preamble; the row roster + cell_type is the only chunk-level context. **Empirical: see which chunks need substantive guidance after T1+ smoke.**
- **(c) No preambles — use only the cell roster + axis** — radical YAGNI. Test whether the model can score from row_ids alone (the row_ids are self-descriptive). Iter-1's evidence is *against* this (the 7-row chunk needed the chunk-frame preamble to hit 93.3%).
- **(d) Optional preambles loaded from disk if present** — `src/scoring/chunk_frames_v2/<chunk_id>.md` (path keyed by `chunk_id`); brief-writer loads if file exists, skips if not. Lets us start with 0 and add per-chunk as empirical evidence accumulates. **Pragmatic: defers the scholarly work without locking it out.**

Sub-question: do the preambles fold the v1 Rule 6 substantive-guidance content per-chunk? (E.g., the `actor_registration_required` preamble inherits v1 Rule 6's A5-A11 paragraph, retargeted to the 11 actor cells.) **Likely yes** — this is the natural place for v2-cell-anchored substantive guidance.

Hunch: **(d) optional disk-loaded preambles, ship with 0 in the impl plan**, author them as empirical evidence accumulates from T1+ smoke runs.

#### Q5 — Per-cell substantive guidance

Closely related to Q4. v1 Rule 6 is per-rubric-item substantive guidance (PRI A5-A11 + C0). v2 has 186 cells; per-cell guidance would be ~186 paragraphs. Options:

- **(a) Per-chunk preambles carry all substantive guidance** (Q4 territory) — guidance lives in chunk_frames_v2/, scoped to its chunk's cells.
- **(b) Per-cell `substantive_guidance: str | None` field on `CompendiumCellSpec`** — touches the v2 TSV / `models_v2.py`. Granular. **Schema change to a shipped module.** Probably YAGNI for now.
- **(c) Hybrid: chunk-level preambles + per-cell `notes` column** — the v2 TSV already has a `notes` column (currently provenance-only); could repurpose / extend.

Hunch: **(a)** — concentrate substantive guidance in chunk preambles, which already exist as a planned artifact (Q4). Avoid schema churn on `CompendiumCellSpec`.

#### Q6 — Practical-axis cells / portal artifacts

The 186 cells split: ~131 legal-axis (statute-scored) + 50 practical-axis (portal-scored) + 5 dual-axis (both). v1 had two brief-writers for this exact reason (`build_subagent_brief` for portal, `build_statute_subagent_brief` for statute). Options:

- **(a) Defer practical-axis to a separate component / brainstorm.** This component ships the legal-axis brief-writer only; practical-axis is a sibling component (probably the next brainstorm in this branch). **Recognizes that portal artifacts (HTML/PDF/XLSX/ZIP/CSV) + Citations API behave qualitatively differently from statute text.**
- **(b) Unify into one brief-writer with branching on chunk axis.** Single `build_scoring_brief(state, vintage, chunks, axis="legal"|"practical"|"mixed", ...)` — legal path passes statute_bundle, practical path passes portal_snapshot, mixed path passes both. Larger surface; the prompt has to handle both modes. **Risk: mixed-axis chunks (5 of 15) become the complex case both paths have to anticipate.**
- **(c) Unify the *module* but keep two functions** — `scoring_v2/brief_writer.py` exposes both `build_legal_scoring_brief()` and `build_practical_scoring_brief()`. Shared infrastructure (tools.py, parser.py, models bindings); separate brief-writers per axis. Mixed-axis chunks call both and merge outputs. **Best of both: code reuse without prompt-level branching complexity.**

Hunch: **(a) defer practical-axis** for this brainstorm. Practical-axis scoring is a meaningful design problem in its own right (portal artifacts have suspicious-challenge-stub flags, role labels, multiple file formats), and lumping it in dilutes the legal-side design. Spin a sibling brainstorm after this one ships. **This is a real pushback against the user's "combine" decision from the kickoff exchange — the "combine" was about brief-writer + prompt-rewrite for legal scoring, not about legal + practical.**

This Q is the **biggest** of the brainstorm — it shapes whether this component is one piece or half-of-two.

#### Q7 — Carry-forward of v1 `scorer_prompt.md` rules

v1's 8 rules: keep, morph, or drop. Going one by one:

- **Rule 1 (evidence citation mandatory)** — **Drop the cite-by-artifact-filename guidance.** Citations API structurally enforces evidence-with-citation. Keep the **principle** as a one-liner in the v2 prompt.
- **Rule 2 (handle inaccessible evidence honestly: `unable_to_evaluate: true`, `score: null`)** — **Keep**. The v2 needs an equivalent: cells where the statute is silent or genuinely ambiguous should not be guessed. **Question: where does this land in the cell types?** `CompendiumCell` has `confidence: ConfidenceLevel` and `provenance: EvidenceSpan | None`; there's no `unable_to_evaluate: bool` wrapper field. Options: (i) add it as a wrapper field; (ii) use `confidence="low"` + empty `provenance` as the signal; (iii) use a sentinel value per cell type.
- **Rule 3 (score per data_type)** — **Carries forward** but the v2 mechanism is different: per-cell tool input value must match the cell-class's value shape. Per-cell-type or polymorphic-with-validation (Q2 determines).
- **Rule 4 (confidence as self-assessment, high/medium/low)** — **Keep.** `CompendiumCell.confidence` is already this shape.
- **Rule 5 (read full statute layered)** — **Keep, prominently.** This is rubric-agnostic and load-bearing. Citations API doesn't force the model to read everything; it only structurally proves what *was* cited.
- **Rule 6 (PRI A5-A11 + C0 substantive guidance)** — **Replace.** This is the load-bearing v2 rewrite work. The v1 paragraphs about registration-trigger reasoning + functional-vs-formal definitions of "public entity" are the substantive scholarly content. **Where does it land?** Q4/Q5 territory.
- **Rule 7 (files-read manifest)** — **Drop** in v2. Citations API structurally evidences which files were read; an explicit `files_read.json` is redundant. Counter-argument: a cross-check that the model cited from *every* statute file in the bundle (not just one) might still be useful as a coverage gate. Defer to validation tooling, not prompt rule.
- **Rule 8 (no preamble, no summary, no prose outside output format)** — **Replace with tool-use enforcement.** Under tool use, the model emits tool calls; freeform prose lives in text blocks between tool calls. The rule becomes: "respond by emitting `record_cell` tool calls; freeform text is allowed only as Citations-grounded reasoning before each tool call."

#### Q8 — Provenance shape per cell

Retrieval's pattern: `CrossReference.evidence_spans: tuple[EvidenceSpan, ...]` (multiple citations per claim). `CompendiumCell.provenance: EvidenceSpan | None` (single span). Options:

- **(a) Change `CompendiumCell.provenance` to `tuple[EvidenceSpan, ...]`** — mirror retrieval; schema change to a shipped module. Backward-compat concern (single-span code paths break).
- **(b) Keep single span; parser picks the first / most relevant** — preserves shipped schema; loses information.
- **(c) Add a parallel `evidence_spans: tuple[EvidenceSpan, ...]` field alongside `provenance: EvidenceSpan | None`** — additive; both populated by parser.

Hunch: **(a)** — mirror retrieval for consistency; it's a small, additive schema change (single span is just a length-1 tuple). The `CompendiumCell` ABC is shipped but downstream consumers (Phase C, etc.) haven't ramped yet — low blast radius.

#### Q9 — Parser output container

Options:

- **(a) `parse_scoring_response(message, state, vintage, chunk_id) -> dict[(row_id, axis), CompendiumCell]`** — returns just the cells from one call. Orchestrator merges per-chunk dicts into a full `StateVintageExtraction`.
- **(b) Returns a new `ScoringOutput` model (parallel to retrieval's `RetrievalOutput`)** — adds container shape with metadata (state, vintage, chunk_id, run timing). Symmetric to retrieval.
- **(c) Returns a partial `StateVintageExtraction`** — directly the v2 cell-models container, with only that chunk's cells populated.

Hunch: **(b)** — `ScoringOutput` matches retrieval's pattern (`RetrievalOutput` scoped to one call); orchestrator does merging. Symmetry.

#### Q10 — File location + naming

Options:

- **(a) `src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md`** — parallel to `retrieval_v2/`. Module name = function. **Locked-in by retrieval precedent.**
- **(b) `src/lobby_analysis/extraction_v2/`** — anticipating that scoring is the heart of "extraction." More commitment to a name.
- **(c) Reorganize `src/scoring/` itself** — pull v1 into `_deprecated/` and put v2 at top-level. Out of scope; let Phase C do this when v1 retires.

Hunch: **(a)** — boring choice, matches retrieval, requires no broader reorganization.

### Phase 3 — Capture in implementation plan

Output: `plans/20260514_brief_writer_implementation_plan.md` — TDD-shaped, API-launchable. Mirrors retrieval's implementation plan structure (phases, 30+ test signatures, plan-anchored prompt + tool schemas, integration-test gates).

---

## Testing Plan (high-level — depends on Q's)

Assuming Q2 = (a) single polymorphic tool, Q5 = (a) chunk-preamble guidance, Q6 = (a) defer practical, Q8 = (a) tuple of evidence_spans, Q9 = (b) ScoringOutput:

**Unit tests (T0 gate, no API key):**

- `test_tools.py` — `RECORD_CELL_TOOL` schema shape; coupling test: every `row_id` value in tool examples / docs is reachable via `build_cell_spec_registry()`.
- `test_models.py` — `ScoringOutput` frozen-ness; field types; `CompendiumCell.provenance` schema change.
- `test_brief_writer.py` — `build_scoring_brief(state="OH", vintage=2010, chunks=["lobbying_definitions"], retrieval_output=..., statute_bundle=...)` produces messages.create() kwargs with: model = `claude-opus-4-7`, document blocks for each statute file with `citations.enabled=True`, system block with `scorer_prompt_v2.md` content, user text containing state/vintage/chunk roster.
- `test_brief_writer.py` (continued) — unknown `chunk_id` raises `ValueError`; per-chunk preamble inserted IF `chunk_frames_v2/<chunk_id>.md` exists (Q4 = (d) optional disk-loaded).
- `test_parser.py` — fixture-based: hand-crafted Message JSON with N `record_cell` tool calls + citations on preceding text blocks; parser produces `dict[(row_id, axis), CompendiumCell]` with right subclass per row + evidence_spans attached.
- `test_prompt_invariants.py` — `scorer_prompt_v2.md` is non-empty, mentions Citations API instruction (cite before each tool call), does NOT mention v1 PRI keys (`A5`, `A6`, ..., `C0`-`C3` as word boundaries), does NOT mention v1 rubric / `files_read.json`.

**Integration test (T1 gate, requires `ANTHROPIC_API_KEY`, deferred to desktop run):**

- `test_scoring_v2_integration.py` — tiny statute fixture + 1 chunk (`lobbying_definitions` against OH 2010 short excerpt) → live API call → parser produces ≥1 cell with non-empty `evidence_spans`. Per-call cost ≈ $0.05; gated by env var via `skipif`.

I will NOT write tests that:

- Mock the SDK client and assert mock behavior (testing-anti-patterns).
- Snapshot the prompt text (locks editorial wording).
- Assert cell scoring *correctness* against a single state — that's empirical T2-T4 work, not unit-test work.

NOTE: All tests written before any implementation, per TDD discipline + the retrieval-impl precedent.

---

## Out of scope for this component

- **Practical-axis / portal-side scoring** — if Q6 lands on (a) defer, this becomes a sibling brainstorm.
- **Orchestrator runtime dispatch** — when the scoring brief gets handed to `client.messages.create()` in production, that's the orchestrator's concern; out of scope here.
- **Output persistence (CSV/Parquet of `StateVintageExtraction`)** — the parser returns typed cells in memory; persistence is downstream.
- **Phase C integration** — typed cells flowing into projection functions is Phase C's job; that branch consumes `CompendiumCell` instances as a contract.
- **Multi-vintage retrieval / `oh-statute-retrieval` integration** — Track A; the brief-writer accepts any vintage as a parameter.
- **Empirical accuracy validation across multiple states** — T2+ work; the brief-writer brainstorm ships the harness, not the validation data.
- **Per-chunk preamble *content* for chunks beyond what's needed for T1 smoke** — if Q4 = (b)/(d), the impl plan ships 0 preambles; preamble authoring is downstream scholarly work.

---

## What could change

- **Q6 outcome.** If we unify practical + legal, the entire brief-writer surface roughly doubles.
- **Q4 outcome.** If preambles are authored upfront, the scholarly content load is substantial.
- **Citations API + tool use composition behavior** under load (long statutes, many cells per call) — retrieval's T1 smoke will surface this; if behavior diverges from docs, the parser pairing rule may need revision, which feeds back into brief-writer assumptions.
- **`CompendiumCell.provenance` schema change** (Q8) — if downstream Phase C work has started consuming the single-span shape, the change has a small blast radius to coordinate.
- **Tool-use shape** (Q2) — if the model systematically mis-types values under polymorphic-single-tool, we'd need to pivot to per-type or per-family.

---

## Open questions for the brainstorm

The 10 Q's above. Headline: **Q6 (practical-axis scope)** is the load-bearing decision; if it's "defer," everything else stays narrow. **Q4 (per-chunk preamble strategy)** is the second-biggest, because it dictates how much scholarly content this session has to author. Q1, Q2, Q3, Q8, Q9, Q10 are mostly answered by mirroring retrieval; Q5, Q7 are sub-Q's that resolve once Q4 lands.

Secondary Q's that may surface:

- **Conditional + condition_text emission shape** — `CompendiumCell` wraps `conditional: bool` and `condition_text: str | None`. Tool input field for these? (iter-1's materiality-gate canary captured them across all 3 regimes.)
- **`unable_to_evaluate` analog** — v1 Rule 2's escape valve. Where does it live in v2? (Q7 territory.)
- **Run/extraction container.** Retrieval has `RetrievalOutput` scoped to one call. Where does `ExtractionRun` (already shipped in `models_v2`) get instantiated — by the orchestrator (out of scope) or by brief-writer/parser?
- **State of `src/scoring/orchestrator.py` and `src/scoring/output_writer.py`** — these are v1-coupled. Do they get retired in v2, or do they get a `_v2` sibling? Likely orchestrator gets a v2; output_writer may not be needed if persistence is downstream of this component.

---

## Why combining brief-writer + scorer-prompt-rewrite is the right shape

1. **Retrieval set the precedent.** `retrieval_agent_prompt_v2.md` + `retrieval_v2/brief_writer.py` shipped in one session because they're tightly coupled (brief-writer reads prompt at call time; prompt assumes brief-writer's tool definitions exist).
2. **Compendium 2.0 criterion #2** says "ONE extraction pipeline — same prompt structure." A separate prompt-rewrite session would design the prompt against a hypothetical brief-writer, not the real one.
3. **Test surface coupling.** The prompt-invariant tests (`test_prompt_invariants.py`) and the brief-writer assembly tests are in the same test file family; splitting them across two sessions creates artificial seams.
4. **The 4-component handoff was written before retrieval's experience.** The kickoff handoff (2026-05-14) anticipated subagent-dispatch + markdown-only prompt rewrites; retrieval's pivot to SDK + Citations + tool use changed the coupling structure.
5. **Parallel parallelization is lossy in this case.** Two fellows could theoretically work in parallel on brief-writer vs scorer-prompt, but the prompt's tool-call instructions reference the brief-writer's tool schemas — one of them would block on the other.

---

**Testing Details.** See Testing Plan above; depends on Q outcomes.

**Implementation Details.**

- New code in `src/lobby_analysis/scoring_v2/` (Q10).
- New prompt in `src/scoring/scorer_prompt_v2.md`.
- Per-chunk preambles (if Q4 = author-now) in `src/scoring/chunk_frames_v2/<chunk_id>.md`.
- New tests in `tests/test_scoring_v2_*.py` + `tests/test_scoring_v2_integration.py` (skipif-gated).
- Possible schema edit: `src/lobby_analysis/models_v2/cells.py` — `provenance` field (Q8).
- No new `pyproject.toml` dependencies (`anthropic` + `pydantic` already in).

**Questions.** Q1-Q10 above. Q6 is the load-bearing decision; Q4 is the second-biggest. Most others mirror retrieval.

# Retrieval Agent v2 Generalization — Plan Sketch (brainstorm agenda)

**Goal:** Take this branch from "v1 PRI-keyed retrieval prompt exists" to "v2 compendium-anchored retrieval prompt with TDD-able brief-writer." Plan-sketch is the brainstorm-first agenda; the brainstorm convo resolves the Q's; the implementation plan that follows is the API-launchable artifact.

**Originating handoff:** [`_handoffs/20260514_next_session_kickoff.md`](_handoffs/20260514_next_session_kickoff.md) — this is the second of the 4 downstream components, explicitly flagged as "the cleanest parallel work" since it's orthogonal to chunks/brief-writer/scorer.

**Sibling plan in this session:** [`20260514_chunks_plan_sketch.md`](20260514_chunks_plan_sketch.md) — chunks decides axis-summary semantics + chunk identity; retrieval may consume those.

**v1 contract (carry-forward):** [`../../../../src/scoring/retrieval_agent_prompt.md`](../../../../src/scoring/retrieval_agent_prompt.md). Read end-to-end. Key features:
- **Inputs:** state abbrev, vintage year, statute bundle (already retrieved chapter files), **a PRI rubric**, Justia URL pattern examples.
- **Algorithm:** read core chapter files → identify cross-references to **definitions** (esp. "person") + penalties + exemptions + cross-cited disclosure requirements → construct Justia URLs → output JSON.
- **Two-hop limit.** Hop-1 from core, hop-2 from added support chapters.
- **Rubric coupling sites** (the two PRI-specific surfaces that need v2 replacement):
  1. **Rule 2 substantive guidance:** "the definition is often NOT in the lobbying chapter — it's in a general definitions/construction act (e.g., TX Gov Code §311.005, OH Rev. Code §1.59). If the core lobbying chapter uses 'person' without defining it, finding the general definitions section is critical. **This definition directly controls rubric items A5–A11** (whether government entities must register) **and C0–C3** (public entity definition)."
  2. **Output schema:** `rubric_items_affected: list[str]` with values like `["A5", "A6", "A7", "A8", "A9", "A10", "A11"]`.
- **Rubric-agnostic surfaces** (carry forward as-is):
  - Two-hop limit + URL-construction-from-pattern logic.
  - URL confidence levels (high/medium/low).
  - `unresolvable_references` for human-readable references without specific section numbers.
  - The substantive cross-ref guidance about definitions / penalties / exemptions / disclosure requirements (only the *anchor examples* are rubric-specific; the categories are universal).

**Confidence:** High that the rewrite is mostly mechanical (the cross-ref logic is rubric-agnostic; only ~2 spots need v2 anchors). Medium on whether to add a Python brief-writer alongside the prompt rewrite (depends on how the harness dispatches retrieval calls).

**Branch:** `extraction-harness-brainstorm` (worktree `.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12 (for any brief-writer / template tests), pytest, ruff. The retrieval *prompt itself* is markdown text; no new dependencies.

---

## What this component is and isn't

**Is:** A v2-compendium-anchored retrieval agent prompt (markdown text), plus — depending on Q6 below — a Python brief-writer that fills the prompt template at runtime with state/vintage/chunk-specific values.

**Isn't:**
- The retrieval agent's runtime invocation (subagent dispatch lives in the orchestrator).
- The two-pass retrieval *architecture* — that's locked from the kickoff brainstorm's Q2 (carry forward).
- An embedding-based or RAG-style retrieval. The cross-ref-walking design is locked.

---

## Brainstorm agenda

### Phase 1 — Carry-forward reading (~15 min)

1. **`src/scoring/retrieval_agent_prompt.md`** (already on `extraction-harness-brainstorm`) — full re-read for the rubric-coupling sites.
2. **Compendium 2.0 README** (`compendium/README.md`) — understand the v2 row contract's structure (cell_types, axes) so the v2 retrieval prompt can reference cells correctly.
3. **A sample of `def_*` and `actor_*` rows** from `compendium/disclosure_side_compendium_items_v2.tsv` — these are the cells that the v1's "person definition" guidance would now anchor.

### Phase 2 — Resolve architectural questions (~1-2 hours)

#### Q1 — Input shape: what does the retrieval agent take as input?

The v1 takes "a rubric." The v2 has 186 cells across 15 chunks. Options:

- **(a) The whole 186-cell roster as a flat list** (with row_id, axis, cell_type, description). Most general. Agent scans all of them when deciding which cross-refs matter.
- **(b) A single chunk's cell_specs.** Scope retrieval per-chunk. Lets the agent focus, but means N retrieval calls per (state, vintage) — one per chunk.
- **(c) A curated "retrieval-relevant" subset** — likely just the legal-axis cells (~131 of 186). Practical-axis cells are about portal usability, not statute language; retrieving statute text isn't useful for them.
- **(d) Per-(state, vintage) with the full roster but axis-filtered.** Run retrieval once per (state, vintage); the agent ignores practical-axis cells when scoring relevance.

Sub-question: does retrieval *need* per-chunk scope? If two-pass retrieval can cover all relevant cross-refs in one (state, vintage) pass, per-chunk is wasteful. If per-chunk scoping produces tighter bundles, it's worth it. Iter-1 was effectively per-chunk against PRI (one chunk → one retrieval bundle).

#### Q2 — Output schema: what replaces `rubric_items_affected`?

The v1 emits `rubric_items_affected: ["A5", "A6", ...]`. v2 options:

- **(a) `cell_ids_affected: list[tuple[str, str]]`** — list of (row_id, axis) cells the cross-ref informs. Matches the cell_id_space decision (Q0 from the kickoff brainstorm).
- **(b) `chunk_ids_affected: list[str]`** — list of chunk_ids. Coarser. The brief-writer can resolve to cells if it wants to.
- **(c) Both** — `cell_ids_affected` for precision + `chunk_ids_affected` for coarse routing.

#### Q3 — Substantive guidance: what stays, what changes?

The v1's Rule 2 currently reads:

> Definitions — especially "person." This is your highest priority. Nearly every state's lobbying chapter uses the term "person" (or equivalent: "individual," "entity") to define who must register. The definition is often NOT in the lobbying chapter — it's in a general definitions/construction act (e.g., TX Gov Code §311.005, OH Rev. Code §1.59). If the core lobbying chapter uses "person" without defining it, finding the general definitions section is critical. This definition directly controls rubric items A5–A11 (whether government entities must register) and C0–C3 (public entity definition).

Three options for the v2 rewrite of this passage:

- **(a) Translate to v2 cell anchors.** Replace "A5–A11" with the explicit v2 cell list (`actor_executive_agency_registration_required`, ..., 11 cells from the `actor_registration_required` chunk) and "C0–C3" with `public_entity_def_relies_on_charter`, `public_entity_def_relies_on_ownership`, `public_entity_def_relies_on_revenue_structure`, `law_defines_public_entity`. Concrete, gives the LLM specific targets.
- **(b) Make generic.** "...controls definitional rows about which entities must register, and the legal definition of 'public entity.'" Loses concreteness; LLM has to infer which cells.
- **(c) Both.** Generic framing followed by the v2 cell list as anchor examples.

Same question for the smaller rubric-anchor mentions in the prompt (Rule 4 "the scorer needs for E-series items" → what's the v2 equivalent?).

#### Q4 — Cell-aware vs cell-agnostic retrieval

Does the retrieval agent know about cells, or does it just identify cross-refs and let downstream figure out which cells they touch?

- **(a) Cell-aware:** the agent receives cells/chunks as input and emits `cell_ids_affected` per cross-ref. Higher coupling; tighter guidance; requires the cells to be in the brief.
- **(b) Cell-agnostic:** the agent emits cross-refs with semantic tags (`tags: ["definitions:person", "definitions:public_entity", "penalties", "exemptions"]`); downstream maps tags to cells. Lower coupling; the prompt stays stable as the cell roster evolves; mapping happens in Python.

Sub-question: cell-aware means every cell-roster change forces a prompt update. Cell-agnostic means the prompt is stable but a Python mapping layer needs maintenance.

#### Q5 — Iteration unit (per-chunk vs per-(state, vintage))

Two-pass retrieval is locked. The question is *retrieval call scope*:

- **(a) One retrieval per (state, vintage).** Output: one bundle of cross-refs. All chunks use the same bundle for scoring.
- **(b) One retrieval per chunk per (state, vintage).** Output: per-chunk bundles. Some chunks might not need retrieval at all (e.g., `search_portal_capabilities` is all practical-axis — no statute cross-refs to chase).

Iter-1 used (b). Empirically the `definitions` chunk's retrieval found OH §311.005 ("person" definition) and the bundle included that. Other chunks may not need it.

#### Q6 — Implementation deliverable

The retrieval prompt is markdown text. The v1 was just a markdown file. For v2, options:

- **(a) Just the prompt rewrite.** No Python code added. The orchestrator's brief-writer (separate component) constructs the brief that includes the prompt + state-specific filler.
- **(b) Prompt + a Python brief-writer.** A function like `build_retrieval_brief(state, vintage, statute_bundle, cells_or_chunk) -> str` that templates the prompt with state-specific values. TDD-able.
- **(c) Prompt + brief-writer + a tested output parser.** Add a function `parse_retrieval_output(json_blob) -> RetrievalResult` that validates the agent's JSON output against the v2 schema. Increases the testable surface.

Sub-question: TDD discipline says we need Python code we can test. A markdown rewrite alone doesn't have automated tests. (b) or (c) gives us testable surface; pure (a) gives us none.

Counter: testing the markdown against "no `A5`, `A6`, ..., `C0`–`C3` references remain" is a real test that catches regressions. (a) is testable in that limited sense.

#### Q7 — File location

Where does the v2 prompt live?

- **(a) `src/scoring/retrieval_agent_prompt_v2.md`** parallel to v1 until phase-c retires v1. Matches the `models_v2/` pattern.
- **(b) Rewrite `src/scoring/retrieval_agent_prompt.md` in-place.** Loses the v1 reference for phase-c. Counterargument: v1 is still on `phase-c-projection-tdd`'s starting context if needed; the file can be retrieved from git history. Simpler going forward.
- **(c) `src/lobby_analysis/chunks_v2/retrieval_prompt.md`** — move to the chunks_v2 module. Doesn't really fit (retrieval isn't about chunks structurally).
- **(d) `src/lobby_analysis/harness/retrieval_prompt.md`** — anticipating a `harness/` module that contains brief-writer, scorer-prompt, orchestrator, retrieval-prompt. More commitment; YAGNI says wait.

### Phase 3 — Capture in implementation plan (~30 min)

Output: `plans/20260514_retrieval_implementation_plan.md` — TDD-shaped if Q6 lands on (b) or (c); minimal-test-shaped if (a). Pickup-able by an API-launched implementer.

---

## Testing Plan (high-level — depends on Q6)

If Q6 lands on (b) Python brief-writer:

- **Brief-writer template tests:** `build_retrieval_brief(state="OH", vintage=2010, ...)` produces a string that contains "Ohio" and "2010" (or the state/vintage values from input). Round-trip behavior.
- **Cell-list inclusion:** the brief contains the cell row_ids passed in (or the chunk_id if chunk-scoped).
- **Prompt-text invariants:** the rendered brief does NOT contain `"A5"`, `"A6"`, ..., `"C0"`, `"C1"`, `"C2"`, `"C3"` as standalone tokens (catches accidental PRI-key leak from v1 carryover).
- **Output parser tests** (if Q6 = c): given a valid retrieval JSON, parse and assert struct fields; given malformed JSON, raise.

If Q6 = (a) markdown only:

- **Markdown invariant tests:** open the .md file as a string, assert no `\bA[1-9]\b`, no `\bC[0-3]\b`, no `rubric` (word boundary). Plus assert the file is non-empty and contains certain v2 cell anchors expected by the rewrite.

I will NOT write tests that:
- Mock LLM calls and assert mock behavior.
- Test the *content* of the prompt text against a stored snapshot — that locks the wording and breaks on every editorial pass.
- Test that the agent's actual behavior changes — that's an integration test against the live retrieval pipeline, out of scope for this component.

NOTE: All tests written before any implementation, per TDD discipline.

---

## Out of scope for this component

- Brief-writer for the **scoring** prompt (separate component; scorer-prompt rewrite).
- Chunk-grouping function (sibling component in this session).
- Embedding-based retrieval (Q2 from kickoff is locked to two-pass cross-ref-walking).
- Anthropic SDK adoption.
- The orchestrator's runtime dispatch of retrieval calls (lives in `src/scoring/orchestrator.py` and is downstream).

---

## What could change

- **Q2 retrieval architecture** is locked from the kickoff brainstorm. If empirical bundle-size measurement (downstream task) reveals two-pass crashes Claude's context for populous states, the architecture revisits — and this component's prompt would need to adapt to whatever new retrieval design lands.
- **Cell-aware vs cell-agnostic** (Q4) — if the cell roster grows substantially post-Compendium-3.0, cell-agnostic becomes more attractive (less prompt churn).
- **Implementation deliverable shape (Q6)** depends on user's preference for TDD surface vs minimal scope.

---

## Open questions for the brainstorm

The 7 Q's above are the primary axes. Secondary Q's that may surface:

- **Should the v2 prompt support a "scope" hint** (e.g., "only legal-axis cells need retrieval")? Practical-axis cells don't need statute text. If the prompt accepts a scope param, it can short-circuit retrieval for practical-only chunks.
- **Cross-state generalization.** v1's TX/OH examples are concrete. v2 should keep concrete examples (LLMs benefit from grounding) but make clear they're *examples*, not a complete list of patterns.
- **Anchor row count.** The cells affected by "person" definition are 11 (`actor_*_registration_required`) + 1 (`law_defines_public_entity`) + 3 (`public_entity_def_*`) = 15 cells. Should the v2 prompt enumerate all 15, or just give the chunk names (`actor_registration_required`, `lobbying_definitions`)?

---

## Why this is a reasonable parallel component

Per the handoff:

1. **Orthogonal to chunks.** No dependency on chunk-grouping output (unless Q5 lands on per-chunk retrieval, in which case there's a one-way dependency — but it's the *interface contract*, not the implementation).
2. **Rewrite, not new build.** The v1 prompt is the starting point. Most of it carries forward.
3. **Clean parallelization candidate.** No coordination friction with chunks impl.
4. **Lower load on the user.** The substantive guidance is already in v1; the Q's are mostly "which v2 anchors replace which v1 anchors" — narrow scope.

---

**Testing Details.** See Testing Plan above; depends on Q6 outcome.

**Implementation Details.**
- All new code (if any) in the location chosen by Q7.
- All new tests (if any) in `tests/test_retrieval_*.py`.
- No new dependencies in `pyproject.toml`.

**Questions.** Q1–Q7 above. Headline: implementation deliverable shape (Q6) and substantive guidance v2 anchor mapping (Q3) are the load-bearing decisions; the rest are smaller.

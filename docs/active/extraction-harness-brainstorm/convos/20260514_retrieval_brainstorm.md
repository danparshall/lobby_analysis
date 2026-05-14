# Retrieval Agent v2 Generalization — Brainstorm Convo

**Date:** 2026-05-14 (started); resumed and completed same day in pickup session
**Branch:** extraction-harness-brainstorm
**Agenda followed:** [`../plans/20260514_retrieval_plan_sketch.md`](../plans/20260514_retrieval_plan_sketch.md)
**Predecessor in this session:** [`20260514_chunks_brainstorm.md`](20260514_chunks_brainstorm.md) — chunks decided per-cell-spec resolution + 15-chunk manifest. Retrieval may consume that.
**Implementation plan output:** [`../plans/20260514_retrieval_implementation_plan.md`](../plans/20260514_retrieval_implementation_plan.md) — TDD-shaped, API-launchable; written at the end of the pickup session.

## Summary

Brainstorm to design the v2 retrieval agent, which rewrites the v1 PRI-keyed cross-reference retriever (`src/scoring/retrieval_agent_prompt.md`) to anchor on the v2 compendium's chunk vocabulary. The first session (prior agent) completed Phase 1 reading and stopped mid-Phase-2 at Q1/Q3/Q6 because the user wanted to clarify before locking. The pickup session re-engaged with the aggregate-cost lens (the user's load-bearing addendum from the prior session: per-chunk dispatch at 50 states × 4 vintages × 3-5 prompt-tuning iterations × 10 chunks = ~8,000 calls vs ~800 for per-(state, vintage) — order of magnitude apart) and surfaced a fundamental design pivot: the user introduced the **Citations API** (`platform.claude.com/docs/en/build-with-claude/citations`), which structurally enforces provenance grounding for cited claims and reshapes the entire output schema.

Final package: parameterized `chunks: list[str]` dispatch (default per-chunk for experiments per the user's "if it's dirt cheap but only 50% accuracy, that's not actually a win" framing); Citations API enabled (incompatible with Structured Outputs, so output schema must use tool use instead of `output_config.format`); two tools (`record_cross_reference` + `record_unresolvable_reference`) with citations attached to surrounding text blocks for provenance; Anthropic SDK adopted into `pyproject.toml` for the first time in this codebase (closes a deferred kickoff decision); data dir local-only in worktree. Implementation plan covers T0 unit tests + T1 smoke-test gate against real Citations API; T2-T4 (multi-chunk → full-rollout) are downstream empirical work after this lands.



## Session frame

This is the **third brainstorm-then-plan cycle on this branch** (cells → chunks → retrieval), per the user's session strategy: brainstorm + plan all 4 downstream components first with user-in-loop, then launch implementations as API sub-branches in parallel, merge back.

Retrieval is the "cleanest parallel work" per the kickoff handoff — it's a rewrite of v1's `src/scoring/retrieval_agent_prompt.md`, not a new build. Most of the substantive guidance survives; only the rubric-coupling sites (PRI A5-A11 / C0-C3 references and `rubric_items_affected` output schema) need v2 anchors.

## Phase 1 — Carry-forward reading

### v1 retrieval prompt (`src/scoring/retrieval_agent_prompt.md`)

Re-read end-to-end. **Rubric-coupling sites:**

1. **Rule 2 substantive anchor:** "...the definition of 'person' directly controls rubric items A5–A11 (whether government entities must register) and C0–C3 (public entity definition)." → v2 anchor needs to point at `actor_*_registration_required` chunk (11 cells) + `public_entity_def_*` + `law_defines_public_entity` (= 4 cells in `lobbying_definitions` chunk).
2. **Output JSON schema:** `rubric_items_affected: ["A5", "A6", "A7", ...]` → v2 replaces with `cell_ids_affected: [["actor_executive_agency_registration_required", "legal"], ...]` (or `chunk_ids_affected: ["actor_registration_required"]`).
3. **Rule 4 implicit reference:** "If the lobbying chapter says 'as required by [other section],' that other section contains information the scorer needs for E-series items." E-series in PRI is reporting/spending items → in v2, this maps to the `lobbyist_spending_report`, `principal_spending_report`, `lobbying_contact_log`, `other_lobbyist_filings` chunks. Either name the chunks or describe generically.

**Rubric-agnostic surfaces** (carry forward verbatim or with minor tightening):
- The two-hop limit + URL-construction-from-pattern logic.
- URL confidence levels (high/medium/low) + reasoning fields.
- `unresolvable_references` schema.
- The substantive category list (definitions / penalties / exemptions / cross-cited disclosure requirements) — these are universal cross-ref categories.
- The OH 2010 §311.005 example as a concrete grounding for the "general definitions act" pattern.

**Empirical anchor.** Iter-1 dispatched this v1 prompt against OH 2025 and successfully retrieved §311.005 ("person" definition) as a hop-1 cross-ref. The v2 rewrite shouldn't regress that behavior — the v2 cells driving the "person" retrieval are equivalent to PRI's A5-A11/C0-C3, just labeled differently.

### v2 cell inventory for retrieval-relevant cells

Of the 186 cells, the legal-axis cells (~131) are the ones that genuinely need statute cross-ref retrieval. Practical-axis cells (50 + the 5 combined-axis practicals = 55 cells) are about portal usability and don't need statute text — they're scored against portal screenshots, not statute text.

By chunk, legal vs practical mix:

| Chunk | Legal | Practical | Mixed (combined) |
|-------|-------|-----------|------------------|
| `lobbying_definitions` | 15 | 0 | 0 |
| `actor_registration_required` | 11 | 0 | 0 |
| `registration_thresholds` | 6 | 0 | 0 |
| `registration_mechanics_and_exemptions` | 6 | 0 | 2 (combined) |
| `lobbyist_registration_form_contents` | 13 | 0 | 0 |
| `lobbyist_spending_report` | 29 | 4 | 1 (combined) |
| `principal_spending_report` | 23 | 0 | 0 |
| `lobbying_contact_log` | 9 | 0 | 0 |
| `other_lobbyist_filings` | 12 | 0 | 0 |
| `enforcement_and_audits` | 0 | 0 | 2 (combined) |
| `search_portal_capabilities` | 0 | 16 | 0 |
| `data_quality_and_access` | 0 | 10 | 0 |
| `disclosure_documents_online` | 0 | 5 | 0 |
| `lobbyist_directory_and_website` | 0 | 9 | 0 |
| `oversight_and_government_subjects` | 2 | 6 | 0 |

**Implication:** 5 chunks (`search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website`, and arguably `oversight_and_government_subjects` if its 2 govt_agencies rows are minor) don't need statute retrieval at all. Per-chunk retrieval lets us short-circuit those.

### Aggregate-cost lens — surfaced by user mid-session as load-bearing for Q1

The chunks brainstorm established that **per-chunk LLM dispatch is cheap *per call* under prompt caching** (statute in cached `system`, chunk content uncached). That framing makes per-chunk retrieval (Q1 option (a)) look attractive. But the user flagged at session end:

> "Even if it's relatively cheap per chunk, I'll have to do this 50x, for multiple years... and then we'll be doing that multiple times as we adjust the 'user prompt' to make sure we're correctly extracting."

Concrete arithmetic — **per-chunk dispatch** at production rollout:
- ~10 legal-axis-bearing chunks (per the 15-chunk manifest, after short-circuiting the 5 fully-practical chunks)
- × 50 states (eventual target)
- × ~4 vintages per state (e.g., the OH multi-vintage validation set: 2007, 2010, 2015, 2025)
- × ~3-5 prompt-tuning iterations during design

= **6,000–10,000 retrieval calls per design cycle.**

**Per-(state, vintage) dispatch** at the same rollout:
- × 1 retrieval call per state-vintage (instead of ~10)
- = **600–1,000 retrieval calls per design cycle.**

Order-of-magnitude difference. Even with statute caching making each call's *marginal* cost low, the **uncached prefix** (chunk preamble + per-row instructions + JSON output) compounds 10× when per-chunk. This is a real economic argument *against* per-chunk dispatch.

**Implication for Q1:** Don't lock on the "caching makes per-chunk cheap" framing alone. Per-(state, vintage) dispatch — option (b) of Q1 — has a clear aggregate-cost advantage that the per-call view obscures. The tradeoff vs per-chunk is bundle-size (does the single bundle fit Claude's context for all 131 legal-axis cells?) and granularity (does the agent get confused by 131 cells at once?). Iter-1's empirical baseline is per-chunk against 7 cells; per-(state, vintage) is untested empirically. Worth surfacing this lens explicitly in the next session's Q1 ask.

## Phase 2 — Architectural decisions

Pickup session resumed Phase 2 with the aggregate-cost lens explicit (per handoff). Initial agent proposal favored per-(state, vintage) dispatch on cost grounds; user pushed back ("If it's dirt cheap but only 50% accuracy, that's not actually a win") and re-anchored on **accuracy gate before cost optimization**. Mid-Phase-2 the user surfaced the **Citations API** as load-bearing — a feature the prior session hadn't considered. Pivot acknowledged: Citations changes Q2 (output schema) and Q6 (deliverable shape) substantially. Locks below reflect the post-pivot package.

### Q1 — Dispatch unit: **parameterized (`chunks: list[str]`), default per-chunk for experiments**

**Rationale:** iter-1's 93.3% empirical baseline was per-chunk against 7 cells. Per-(state, vintage) at 131 cells is untested. The aggregate-cost lens (8,000 vs 800 calls per design cycle) is a real argument for larger scope, but **accuracy at scope is unknown** — locking per-(state, vintage) without empirical data would risk the cheap-but-wrong failure mode. Defer the dispatch-unit decision to empirical comparison.

**Interface:** the brief-writer takes `chunks: list[str]` so the caller decides scope per call. Pass 1 chunk → iter-1-style per-chunk. Pass several → midpoint experiments. Pass all 10 legal chunks → per-(state, vintage). The brief-writer doesn't care; it templates the cell roster for whichever chunks it's handed.

**Citations API reweighting:** with structural span grounding (see Q2), hallucination risk drops at any scope. Larger scopes become more defensible *if* the agent's chunk-routing accuracy holds with 131 cells in view — but this is still empirical. Start at per-chunk; scale up the cell-group when accuracy data supports it.

### Q2 — Output schema: **tool use (`record_cross_reference` + `record_unresolvable_reference`)**

**Rationale:** the pivot's load-bearing constraint is **Citations API is incompatible with Structured Outputs** (`output_config.format` returns 400). v1's strict JSON `cross_references: [...]` can't be enforced via `output_config` if citations are enabled. Three candidate paths:

- **(α) Tool use** — `record_cross_reference` tool called once per finding; tool args carry structured fields; citations attach to text blocks before each call. Tool use **is** compatible with citations.
- **(β) Prose + parser** — agent emits free-form prose with citations; parser walks content blocks. More fragile; no schema enforcement.
- **(γ) JSON-fenced text** — agent emits ```json fenced text with citations attached. Brittle.

**Lock:** (α) tool use. Keeps v1's structured-output discipline; citations carry provenance separately. Tool input includes `chunk_ids_affected: list[str]` (the agent's chunk-routing claim) — replaces v1's `rubric_items_affected: ["A5",...]`. Two tools rather than one with a conditional flag: `record_unresolvable_reference` for references without specific section numbers (cleaner schemas).

**Provenance:** the citations attached to text blocks *preceding* each tool call become the `EvidenceSpan` list in the parsed `CrossReference`. Pairing rule: parser walks content blocks in order, accumulates citations from text blocks, attaches accumulated set to the next `tool_use` block, resets. **This rule needs empirical validation** — actual Claude output ordering may not always put cited reasoning before the corresponding tool call. The prompt's Rule 5 instructs the agent to "cite the statute span supporting each cross-reference *before* calling the tool" to make the rule load-bearing.

### Q3 — Substantive guidance anchoring: **chunk-name + count + descriptive**

**Rationale:** more durable than enumerating cell row_ids (which evolve as the compendium iterates), more concrete than chunk-name-only (which loses LLM grounding). The chunks manifest is frozen (15 chunks); the cell roster within a chunk is not.

**Example v2 Rule 2 anchor (replaces v1's "A5-A11/C0-C3"):**

> "...this definition directly controls the 11 cells in the `actor_registration_required` chunk (which entities must register as lobbyists) and the `public_entity_def_*` cells in the `lobbying_definitions` chunk (legal definition of 'public entity')."

Same shape for Rule 4's E-series reference: "...the `lobbyist_spending_report` chunk (29 cells covering spending disclosure) and `principal_spending_report` chunk (23 cells covering client/employer disclosure)."

### Q4 — Cell-aware at input, chunk-coarse at output

**Lock unchanged.** Agent input: chunks→cells grouped (the brief enumerates which cells are in scope for this call, organized by chunk). Agent output: `chunk_ids_affected: list[str]` (chunk-level routing claim). Cell-level precision is downstream-derivable from the chunks manifest if needed.

### Q5 — Iteration unit

**Collapsed into Q1.** No separate question — the `chunks: list[str]` parameter is the iteration unit per call. Per-call dispatch is the orchestrator's responsibility (out of scope for this component).

### Q6 — Implementation deliverable: **prompt + Python brief-writer + tool definitions + parser**

**Pivot reshapes this substantially.** Pre-pivot, my recommendation was markdown-only + invariant tests (brief-construction punted to orchestrator). Citations API forces real Python code:

- **`src/scoring/retrieval_agent_prompt_v2.md`** — the v2 prompt rewrite. Markdown body that's templated into the SDK call's user message.
- **`src/lobby_analysis/retrieval_v2/brief_writer.py`** — `build_retrieval_brief(state, vintage, statute_bundle, chunks: list[str]) -> dict` returning SDK call args (the `messages.create()` kwargs). Packages statute files as `type: "document"` content items with `citations: {enabled: true}` and `cache_control: {type: "ephemeral"}`.
- **`src/lobby_analysis/retrieval_v2/tools.py`** — tool definitions: `record_cross_reference` (section_reference, chunk_ids_affected, relevance, justia_url, url_confidence, url_confidence_reason) + `record_unresolvable_reference` (reference_text, referenced_from, reason).
- **`src/lobby_analysis/retrieval_v2/parser.py`** — `parse_retrieval_response(message) -> RetrievalOutput` that walks content blocks, pairs citations to tool calls, and emits typed Pydantic objects.
- **`src/lobby_analysis/retrieval_v2/models.py`** — Pydantic `RetrievalOutput`, `CrossReference`, `UnresolvableReference`, `EvidenceSpan` (reuses the v2 cell-models `EvidenceSpan` if shape matches; otherwise a retrieval-specific variant).

**TDD discipline:** unit tests for tool definitions (input schema validation), brief-writer (output shape), parser (citation-to-tool attribution). Integration test gated on `ANTHROPIC_API_KEY` — calls real API against a tiny hand-crafted statute fixture; validates end-to-end shape and surfaces any docs↔reality mismatches before the OH validation lands.

### Q7 — File location

- **`src/scoring/retrieval_agent_prompt_v2.md`** — prompt text, parallel to v1 at `src/scoring/retrieval_agent_prompt.md` (matches v1's location, mirrors `models_v2`/`chunks_v2` parallel-module pattern)
- **`src/lobby_analysis/retrieval_v2/`** — new module for Python code (brief-writer, tools, parser, models)
- **`tests/test_retrieval_v2_*.py`** — test files in standard tests dir

### Sampling and thinking — locked defaults

- **Model:** `claude-opus-4-7` (per `claude-api` skill default; the skill notes Opus 4.7 has `xhigh` effort which is the best for coding/agentic, but for retrieval `high` is the documented sweet spot)
- **Thinking:** `{"type": "adaptive"}` (per `claude-api` skill; Opus 4.7 supports adaptive only — `budget_tokens` returns 400)
- **Effort:** `output_config={"effort": "high"}` — start here; tune down to `medium` only if cost is a problem during prompt-tuning iterations
- **`max_tokens`:** 16000 (retrieval output is structured tool calls + citations, not long prose — 16K is generous)
- **Streaming:** non-streaming (`messages.create()`); retrieval is one call producing one structured output, not user-facing token-by-token rendering

### Data directory decision

**Lock:** `data/retrieval_v2/{state}_{vintage}/` **local-only in this worktree** for now. Reproducible from OH statute bundles (which live on `oh-statute-retrieval`); no durable artifacts yet. Revisit when retrieval output becomes input to scorer experiments downstream.

### Anthropic SDK adoption

**Lock:** add `anthropic` to `pyproject.toml`. Closes the deferred kickoff Q (finding #2 from `convos/20260514_extraction_harness_brainstorm.md`). The retrieval component is the first SDK consumer; downstream components (scorer prompt rewrite) will reuse it.

### What I'm aware we're locking blind

Since both Dan and I are first-time users of the Citations API, the package above assumes the docs are accurate about:

- Citation-to-tool-call attribution behavior (does Claude actually emit cited text immediately before each tool call, or does it sometimes consolidate citations at the end?)
- Stable behavior with `cache_control` on document blocks (does caching the statute body actually work, or does enabling citations invalidate the cache in subtle ways?)
- Tool-use + citations composition (the docs say compatible; we have no in-codebase precedent)
- Plain-text-source char-level citation accuracy on our statute extractions (our PDF→text extractions may have non-standard whitespace that affects sentence chunking)

The impl plan's integration test is the first chance to surface any of these as mismatches. If they bite, the parser's attribution rule and/or the prompt's Rule 5 will need tightening, possibly via a follow-up implementation pass. Flag explicitly in the plan that the implementer should pause and surface to the user (not silently patch) if integration test results don't match the documented behavior.

---

## Decisions made (audit trail)

| Q | Lock | Pre-pivot answer (if different) |
|---|---|---|
| Q1 | Parameterized `chunks: list[str]`, default per-chunk | (Agent recommended per-(state, vintage); user pushed back) |
| Q2 | Tool use (α): `record_cross_reference` + `record_unresolvable_reference` | (Pre-Citations: `chunk_ids_affected: list[str]` in JSON output schema) |
| Q3 | Chunk-name + count + descriptive | unchanged |
| Q4 | Cell-aware at input, chunk-coarse at output | unchanged |
| Q5 | Collapsed into Q1 | (no longer separate) |
| Q6 | Prompt + brief-writer + tools + parser (full Python module) | (Pre-Citations: markdown-only + invariants) |
| Q7 | `src/scoring/retrieval_agent_prompt_v2.md` + `src/lobby_analysis/retrieval_v2/` | unchanged shape; expanded surface |
| **deferred** | Anthropic SDK in pyproject.toml; data/ local-only in worktree | (deferred from kickoff) |

## Topics explored

- **Aggregate-cost lens vs per-call caching efficiency** — surfaced by user in prior session; agent over-weighted in pickup; user re-anchored on accuracy gate
- **Citations API** — surfaced by user mid-Phase-2; fundamentally reshapes Q2 and Q6 because of structured-outputs incompatibility
- **Plain text vs PDF vs custom-content document types** — chose plain text for char-level citations and existing `papers/text/` extractions
- **Tool use vs prose-with-parsing vs JSON-fenced** for output structure under Citations
- **Citation-to-tool-call attribution rule** — proximity-based, requires prompt instruction (Rule 5) to make load-bearing
- **Effort=high vs xhigh vs max for retrieval** — high is the documented sweet spot; xhigh/max reserved for harder agentic work
- **What we're locking blind** — both Dan and agent are first-time Citations users; integration test gates docs↔reality mismatches

## Next session

This convo is the brainstorm. Next: write `plans/20260514_retrieval_implementation_plan.md` (TDD-shaped, API-launchable) — sibling agent in this same session will pick up that work, then run finish-convo.

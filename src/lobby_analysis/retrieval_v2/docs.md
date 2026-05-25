# `lobby_analysis.retrieval_v2`

The v2 cross-reference retrieval agent: assembles an Anthropic
`messages.create()` brief (Citations API + tool use), parses the response
back into typed output. The module **does not call the SDK** — the caller
dispatches the brief and feeds the response into the parser.

## Public surface

```python
from lobby_analysis.retrieval_v2 import (
    build_retrieval_brief,
    parse_retrieval_response,
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
    CROSS_REFERENCE_TOOL,
    UNRESOLVABLE_REFERENCE_TOOL,
    ALL_TOOLS,
)
```

- **`build_retrieval_brief(state, vintage, statute_bundle, chunks, url_pattern="")`** — returns the kwargs dict for `client.messages.create(**brief)`. Validates `chunks` against `build_chunks()`; unknown chunk ids raise `ValueError`. Loads the prompt template at call time from `src/scoring/retrieval_agent_prompt_v2.md`.
- **`parse_retrieval_response(message, state_abbr, vintage_year, hop)`** — parses an Anthropic SDK `Message` (or an equivalent dict) into a `RetrievalOutput`. Accepts both shapes so the same parser works against fixtures and real API responses.
- **`CROSS_REFERENCE_TOOL` / `UNRESOLVABLE_REFERENCE_TOOL` / `ALL_TOOLS`** — JSON-schema tool definitions. `CROSS_REFERENCE_TOOL.chunk_ids_affected.items.enum` is sourced from `lobby_analysis.chunks_v2.build_chunks()`; a coupling test in `tests/test_retrieval_v2_tools.py` enforces no drift.
- **`CrossReference` / `UnresolvableReference` / `RetrievalOutput` / `EvidenceSpan`** — frozen Pydantic models (sequence fields are `tuple[...]` for hashability).

## Flow

```
caller (orchestrator, not in scope)
  │
  │  brief = build_retrieval_brief(state, vintage, statute_bundle, chunks)
  ▼
src/lobby_analysis/retrieval_v2/
  ├── brief_writer.py   → returns messages.create kwargs (dict)
  ├── tools.py          → CROSS_REFERENCE_TOOL, UNRESOLVABLE_REFERENCE_TOOL
  ├── parser.py         → parse_retrieval_response(message) → RetrievalOutput
  └── models.py         → Pydantic: RetrievalOutput, CrossReference, ...
  │
  ▼  client.messages.create(**brief)
Anthropic API (claude-opus-4-7 + Citations)
  │
  ▼  Message response (text blocks w/ citations + tool_use blocks)
parse_retrieval_response(message, state, vintage, hop) → RetrievalOutput
```

## Brief composition

- **Model:** `claude-opus-4-7`. `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`. No sampling params (Opus 4.7 returns 400 if any are supplied).
- **System block:** the prompt template as a single text content block with `cache_control={"type": "ephemeral"}` so it's cached across calls in the same scope.
- **User message content blocks:**
  - One `document` block per statute file (`type=text`, `media_type=text/plain`, `citations.enabled=true`, `cache_control=ephemeral`, `title` derived from path).
  - A trailing `text` block carrying the state/vintage/example URL pattern + chunks-scoped cell roster + tool-call instruction.
- **`max_tokens`:** 16000 (production default). Integration smoke test in `tests/test_retrieval_v2_integration.py` overrides to 2000 for cost discipline.
- **Tools:** `[CROSS_REFERENCE_TOOL, UNRESOLVABLE_REFERENCE_TOOL]`.

## Parser invariants

- **Citation→tool_use pairing.** Citations on text blocks accumulate into a buffer until a `tool_use` block; the buffer flushes onto that tool call's `evidence_spans` and resets. Test: `test_parser_resets_citation_buffer_after_each_tool_call`. Rule 5 of `src/scoring/retrieval_agent_prompt_v2.md` instructs the agent to cite before each tool call so this rule is non-vacuous.
- **Unknown tool names still flush + reset.** Prevents stale citations from bleeding into the next valid tool call.
- **Other block types pass through.** `thinking`, `server_tool_use`, etc. don't disturb the buffer or produce output.
- **Polymorphic input.** `parse_retrieval_response` works against SDK `Message` objects (attribute access) and JSON-loaded dicts (key access) — same path for fixtures and real responses.

## Provenance

- Design: [`docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_brainstorm.md`](../../../docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_brainstorm.md)
- Implementation plan: [`docs/active/extraction-harness-brainstorm/plans/20260514_retrieval_implementation_plan.md`](../../../docs/active/extraction-harness-brainstorm/plans/20260514_retrieval_implementation_plan.md)
- Implementation convo: [`docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_implementation.md`](../../../docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_implementation.md)
- Prompt text: [`src/scoring/retrieval_agent_prompt_v2.md`](../../scoring/retrieval_agent_prompt_v2.md)

## Empirical validation tiers (from the plan)

| Tier | What runs | Status |
|---|---|---|
| **T0 unit** | `tests/test_retrieval_v2_*.py` (excluding integration) | ✅ green |
| **T1 smoke** | `tests/test_retrieval_v2_integration.py` against `tiny_statute.txt` (2 sentences, 2 obvious xrefs); ~$0.02/run | ⏸ deferred to desktop (laptop has no `ANTHROPIC_API_KEY`) |
| **T2 single-chunk OH** | Manual run against one OH 2010/2025 chunk file; iter-1's 93.3% comparison point | ⏳ downstream |
| **T3 multi-chunk** | Manual run with 2-5 chunks at a time | ⏳ downstream |
| **T4 full** | 50-state × 4-vintage production rollout | ⏳ after scorer-prompt lands |

The T1 smoke test will overwrite `tests/fixtures/retrieval_v2/sample_response.json` with a real API response on first successful run. If the parser then fails against the real shape on subsequent runs, the docs↔reality divergence flagged in plan Phase 7 has triggered — pause and surface to user.

## Downstream consumers

- The orchestrator (not yet built) will iterate `chunks` and `hop` levels, dispatching briefs to the SDK and consuming `RetrievalOutput` instances.
- The scorer-prompt rewrite component will read `cross_references[*].evidence_spans` for cited statute support when populating downstream cell values.

## What this module does NOT do

- It does not call the Anthropic SDK. Brief writer returns a dict; the caller dispatches.
- It does not do compaction, streaming, or batching. Single non-streaming call.
- It does not do embedding-based retrieval. Locked off in kickoff brainstorm Q2.
- It does not implement per-rubric projection (that lives on `phase-c-projection-tdd`).
- It does not include the scorer prompt (next component after this lands).

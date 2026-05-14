# Retrieval Agent v2 — Implementation Plan

**Branch:** `extraction-harness-brainstorm`
**Implemented:** [`../convos/20260514_retrieval_implementation.md`](../convos/20260514_retrieval_implementation.md) — Phases 1-8 executed under strict TDD on 2026-05-14 laptop session (commits `a5d05c5` → `d1fa512`); T0 unit suite fully green (+48 tests; full suite 400 → 448). 2 plan deviations resolved + documented in convo (P6→P4 reorder; cell-roster format). **Phase 7 (T1 smoke) deferred to desktop run** — laptop has no `ANTHROPIC_API_KEY`; user runs `uv run pytest tests/test_retrieval_v2_integration.py` on Dans-MacBook-Pro.
**Goal:** Rewrite the v1 PRI-keyed retrieval agent as a v2-compendium-anchored retrieval pipeline that uses the **Anthropic Citations API** for span-level provenance grounding. Pure-Python; first SDK consumer in this codebase. Unblocks the brief-writer + scorer-prompt rewrite downstream.

## ⚠ PREREQUISITE — chunks_v2 must ship before retrieval impl can proceed past Phase 0

Three places in this plan import from `lobby_analysis.chunks_v2`:

- `src/lobby_analysis/retrieval_v2/tools.py` — `chunk_ids_affected.enum` sourced from `build_chunks()` (coupling test catches drift)
- `src/lobby_analysis/retrieval_v2/brief_writer.py` — `_format_cell_roster()` looks up cell rosters via `build_chunks()`
- `tests/test_retrieval_v2_tools.py::test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest` — load-bearing coupling test

**The chunks impl plan ([`20260514_chunks_implementation_plan.md`](20260514_chunks_implementation_plan.md)) must land first.** If you're picking up retrieval before chunks ships, stop and surface to user. The chunks handoff at [`_handoffs/20260514_chunks_implementation_handoff.md`](_handoffs/20260514_chunks_implementation_handoff.md) documents the dependency.

## Phase 0 may already be done — verify before re-running

A prior session (killed by user mid-execution due to the chunks prerequisite) committed Phase 0 scaffolding as `4c49888 retrieval_v2: scaffolding (empty module + anthropic SDK dependency)`. If that commit is on your branch HEAD, **skip Phase 0** and verify the scaffolding matches the spec below (empty `.py` files in `src/lobby_analysis/retrieval_v2/`, `anthropic>=0.102` in `pyproject.toml`, `tests/fixtures/retrieval_v2/.gitkeep`, `uv.lock` updated). If your branch HEAD does not have that commit, execute Phase 0 fresh.

**Originating brainstorm:** [`../convos/20260514_retrieval_brainstorm.md`](../convos/20260514_retrieval_brainstorm.md). Read this first — Phase 2 records every locked Q with rationale.

**Plan-sketch:** [`20260514_retrieval_plan_sketch.md`](20260514_retrieval_plan_sketch.md).

**Sibling contracts:**

- Chunks: [`20260514_chunks_implementation_plan.md`](20260514_chunks_implementation_plan.md) — the 15-chunk manifest is the chunk-routing vocabulary used by `record_cross_reference`'s `chunk_ids_affected` enum.
- Cell models: previously landed at `src/lobby_analysis/models_v2/` — `EvidenceSpan` may be reused for citation provenance.

**You (implementer) start with zero codebase context.** This plan is self-contained. Read the brainstorm convo first for the *why*; this plan covers the *what* and the *how*.

---

## Tech Stack

- Python 3.12 (project requirement)
- `uv` for env management; existing `.venv/`
- `pytest` (in `dev` extras already) for tests
- `ruff` (in `dev` extras already) for lint
- `pydantic >= 2.8` (already a top-level dep)
- **`anthropic` SDK — to be added** (this plan adds it to `pyproject.toml`). Current version at plan-author-time is **0.102.0** (released 2026-05-13, verified via PyPI). Python requirement `>=3.9` (we're on 3.12, fine).

Add to `pyproject.toml` `dependencies`:

```toml
"anthropic>=0.102",
```

Then `uv sync` to install. Verify with `uv run python -c "import anthropic; print(anthropic.__version__)"` — expect `0.102.0` or newer. If the implementer-time version is a major bump (1.x+), pause and surface — the kwarg shapes in the brief-writer (`output_config`, `thinking`, etc.) may have moved.

---

## Locked decisions (brainstorm reference)

| Q | Lock |
|---|---|
| Q1 dispatch unit | `chunks: list[str]` parameter; default per-chunk for experiments. Batch size escalates empirically (tiny fixture → 1 chunk → N chunks → 50 states × 4 vintages) — never commit to full rollout without intermediate accuracy data. |
| Q2 output schema | Tool use: two tools (`record_cross_reference` + `record_unresolvable_reference`). Citations attach to text blocks preceding tool calls. |
| Q3 anchor style | Chunk-name + count + descriptive (e.g., "the 11 cells in `actor_registration_required` chunk"). |
| Q4 cell vs chunk | Cell-aware at input, chunk-coarse at output. |
| Q6 deliverable | Prompt markdown + Python brief-writer + tool definitions + parser + Pydantic models. Full Python module. |
| Q7 file location | `src/scoring/retrieval_agent_prompt_v2.md` + `src/lobby_analysis/retrieval_v2/`. |
| SDK | Add `anthropic` to pyproject.toml. |
| Model/thinking/effort | `claude-opus-4-7`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`. No sampling params (would 400 on Opus 4.7). |
| Data dir | `data/retrieval_v2/{state}_{vintage}/` local-only in worktree. |

---

## Architectural shape

```
caller (orchestrator, not in scope)
  │
  │  build_retrieval_brief(state, vintage, statute_bundle, chunks)
  ▼
src/lobby_analysis/retrieval_v2/
  ├── brief_writer.py   ← assembles SDK call args (messages.create kwargs)
  ├── tools.py          ← tool definitions: record_cross_reference, record_unresolvable_reference
  ├── prompt.py         ← loads src/scoring/retrieval_agent_prompt_v2.md
  ├── parser.py         ← parses messages.create() response → RetrievalOutput
  └── models.py         ← Pydantic: RetrievalOutput, CrossReference, UnresolvableReference, EvidenceSpan
  │
  ▼  client.messages.create(**brief)
Anthropic API (claude-opus-4-7 + Citations)
  │
  ▼  Message response (text blocks w/ citations + tool_use blocks)
parser.parse_retrieval_response(message) → RetrievalOutput
```

**The brief-writer does NOT call the SDK.** It produces the kwargs dict. The orchestrator (or a test) calls `client.messages.create(**brief)`. This keeps the brief-writer testable without an API key.

---

## File deliverables

```
src/lobby_analysis/retrieval_v2/
├── __init__.py                 # Public exports
├── brief_writer.py             # build_retrieval_brief(state, vintage, statute_bundle, chunks)
├── tools.py                    # CROSS_REFERENCE_TOOL, UNRESOLVABLE_REFERENCE_TOOL
├── prompt.py                   # load_v2_prompt() → reads src/scoring/retrieval_agent_prompt_v2.md
├── parser.py                   # parse_retrieval_response(message) → RetrievalOutput
├── models.py                   # Pydantic models
└── docs.md                     # Module-level documentation

src/scoring/retrieval_agent_prompt_v2.md   # The prompt text (Phase 6 below has the full draft)

tests/
├── test_retrieval_v2_tools.py
├── test_retrieval_v2_models.py
├── test_retrieval_v2_brief_writer.py
├── test_retrieval_v2_parser.py
├── test_retrieval_v2_prompt.py
└── test_retrieval_v2_integration.py    # skip-unless-ANTHROPIC_API_KEY

tests/fixtures/retrieval_v2/
├── tiny_statute.txt                    # Hand-crafted minimal statute for integration test
└── sample_response.json                # Recorded API response for parser tests
```

---

## Empirical validation gates (graduated tiers)

The Citations API is new to this codebase. Both the plan author and the implementer are first-time users. **Each tier gates the next** — if a tier surfaces a docs↔reality mismatch, pause and surface to the user before moving on:

| Tier | What runs | Gates |
|---|---|---|
| **T0 unit** | All non-integration tests; no API key needed | Module ships, types validate, schema constraints hold |
| **T1 smoke** | Integration test against hand-crafted tiny statute fixture (~3 sentences, 1 obvious cross-ref) | Citations API returns *any* citations; tool calls fire; parser handles real response shape |
| **T2 single-chunk OH** | Manual run (not automated) against one OH 2010 or 2025 chunk file with one chunk scope | Iter-1's 93.3% per-chunk-against-7-cells comparison point; pause if accuracy drops materially |
| **T3 multi-chunk** | Manual run with 2-5 chunks at a time | Does accuracy hold as cell-scope grows? |
| **T4 full** | Production rollout (50 states × 4 vintages × N iterations) | Out of scope for this implementation — happens after the scorer-prompt component lands |

**This plan implements through T1 only.** T2-T4 are downstream empirical work the user runs once the module is shipped.

---

## Phase 0 — Scaffolding

1. Create `src/lobby_analysis/retrieval_v2/` directory with empty `__init__.py`.
2. Create `tests/fixtures/retrieval_v2/` directory with empty `.gitkeep`.
3. Create empty placeholder files: `brief_writer.py`, `tools.py`, `prompt.py`, `parser.py`, `models.py`, `docs.md` (placeholder `# retrieval_v2 — module documentation`).
4. Add `anthropic>=0.45` to `pyproject.toml` `dependencies`. Run `uv sync`. Verify import works.
5. Create local `data/retrieval_v2/.gitkeep` (directory exists; `data/` is gitignored).
6. Commit: `retrieval_v2: scaffolding (empty module + anthropic SDK dependency)`.

**Gate:** `uv run python -c "import lobby_analysis.retrieval_v2"` succeeds. `uv run python -c "import anthropic"` succeeds.

---

## Phase 1 — Write ALL tests (RED)

**Discipline:** write every test below before any implementation. Run `uv run pytest tests/test_retrieval_v2_*.py` and confirm everything fails (with `ImportError` / `AttributeError` / `NotImplementedError`, not because tests are malformed).

Test inventory below — write the test bodies from the assertions; specific identifiers are spelled out so you don't have to invent names.

### `tests/test_retrieval_v2_tools.py`

```python
# Test names + assertions:

def test_cross_reference_tool_has_documented_name():
    # CROSS_REFERENCE_TOOL["name"] == "record_cross_reference"

def test_unresolvable_reference_tool_has_documented_name():
    # UNRESOLVABLE_REFERENCE_TOOL["name"] == "record_unresolvable_reference"

def test_cross_reference_tool_required_fields():
    # input_schema.required == ["section_reference", "chunk_ids_affected", "relevance", "justia_url", "url_confidence"]

def test_cross_reference_tool_url_confidence_enum():
    # url_confidence.enum == ["high", "medium", "low"]

def test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest():
    # The chunk_ids_affected enum must equal the set of chunk_ids from chunks_v2.build_chunks()
    # COUPLING TEST: catches drift between tools.py and chunks manifest
    from lobby_analysis.chunks_v2 import build_chunks
    from lobby_analysis.retrieval_v2.tools import CROSS_REFERENCE_TOOL
    expected = {c.chunk_id for c in build_chunks()}
    actual = set(CROSS_REFERENCE_TOOL["input_schema"]["properties"]["chunk_ids_affected"]["items"]["enum"])
    assert actual == expected, f"Drift: tools enum {actual} ≠ chunks manifest {expected}"

def test_cross_reference_tool_chunk_ids_is_array():
    # chunk_ids_affected.type == "array"; items.type == "string"

def test_unresolvable_reference_tool_required_fields():
    # input_schema.required == ["reference_text", "referenced_from", "reason"]

def test_unresolvable_reference_tool_has_no_url_field():
    # By design — these are references we cannot construct URLs for
```

### `tests/test_retrieval_v2_models.py`

```python
def test_evidence_span_constructs_from_char_location_citation_dict():
    # EvidenceSpan(document_index=0, document_title="OH §101.70", cited_text="...",
    #              start_char_index=0, end_char_index=20, citation_type="char_location")
    # Constructs without error.

def test_cross_reference_pydantic_model_round_trips():
    # CrossReference(section_reference="§311.005", chunk_ids_affected=["lobbying_definitions"],
    #                relevance="...", justia_url="...", url_confidence="medium",
    #                url_confidence_reason="...", evidence_spans=[<EvidenceSpan>, ...])
    # .model_dump() → reconstructs identical

def test_cross_reference_evidence_spans_is_list():
    # Type annotation is list[EvidenceSpan], not optional

def test_cross_reference_evidence_spans_can_be_empty():
    # Empty list is valid — citations may be absent on some tool calls

def test_unresolvable_reference_pydantic_model():
    # UnresolvableReference(reference_text="as defined by applicable law",
    #                       referenced_from="sections/title1-101_72.txt", reason="...",
    #                       evidence_spans=[...])

def test_retrieval_output_collects_both_kinds():
    # RetrievalOutput(state_abbr="OH", vintage_year=2010, hop=1,
    #                 cross_references=[<CrossReference>, ...],
    #                 unresolvable_references=[<UnresolvableReference>, ...])

def test_retrieval_output_validates_hop_in_range():
    # hop must be 1 or 2 (two-hop limit from v1)
```

### `tests/test_retrieval_v2_brief_writer.py`

```python
# Fixture: a minimal statute_bundle = [{"path": "ch101.txt", "content": "...", "url_pattern": "..."}]

def test_brief_writer_returns_messages_create_kwargs():
    brief = build_retrieval_brief(state="OH", vintage=2010, statute_bundle=<fixture>, chunks=["actor_registration_required"])
    # brief must have keys: "model", "max_tokens", "thinking", "output_config", "system", "messages", "tools"

def test_brief_writer_uses_claude_opus_4_7():
    # brief["model"] == "claude-opus-4-7"

def test_brief_writer_uses_adaptive_thinking():
    # brief["thinking"] == {"type": "adaptive"}

def test_brief_writer_uses_effort_high():
    # brief["output_config"] == {"effort": "high"}

def test_brief_writer_omits_temperature():
    # "temperature" not in brief

def test_brief_writer_omits_top_p():
    # "top_p" not in brief

def test_brief_writer_omits_top_k():
    # "top_k" not in brief

def test_brief_writer_attaches_both_tools():
    # brief["tools"] is a list containing both CROSS_REFERENCE_TOOL and UNRESOLVABLE_REFERENCE_TOOL

def test_brief_writer_includes_state_vintage_in_user_text():
    # User message text contains "Ohio" (or "OH") and "2010" — state/vintage interpolated

def test_brief_writer_packages_statute_files_as_documents():
    # User message content has one type="document" block per statute file in the bundle

def test_brief_writer_enables_citations_on_all_documents():
    # All-or-nothing per Citations API. Every document block has citations.enabled == True

def test_brief_writer_applies_cache_control_to_documents():
    # Every document block has cache_control == {"type": "ephemeral"}

def test_brief_writer_uses_plain_text_source_type():
    # source.type == "text", media_type == "text/plain" on all document blocks

def test_brief_writer_sets_document_title():
    # Each document block has a "title" field — derived from the file path

def test_brief_writer_includes_only_requested_chunks_cell_roster():
    # User text mentions cells from chunks=["actor_registration_required"] only;
    # does NOT mention cells from other chunks (e.g., no "lobbyist_spending_report" cells when not requested)

def test_brief_writer_caches_system_prompt():
    # system block has cache_control too (frozen across calls per Q1 caching strategy)

def test_brief_writer_max_tokens_is_16000():
    # brief["max_tokens"] == 16000
```

### `tests/test_retrieval_v2_parser.py`

Fixture: `tests/fixtures/retrieval_v2/sample_response.json` — hand-crafted Message dict matching the documented Citations API response shape. Tests parse this fixture into `RetrievalOutput`. Phase 5 records a real API response that replaces the hand-crafted fixture if the shape diverges.

```python
def test_parser_extracts_cross_references_from_tool_calls():
    # Fixture has 2 record_cross_reference tool calls; output.cross_references has 2 entries

def test_parser_pairs_preceding_citations_to_following_tool_call():
    # text_block_with_citation → text_block_with_citation → tool_use
    # → The tool_use's CrossReference.evidence_spans contains both citations

def test_parser_resets_citation_buffer_after_each_tool_call():
    # text_with_citation_A → tool_use_1 → text_with_citation_B → tool_use_2
    # → tool_use_1.evidence_spans == [citation_A]; tool_use_2.evidence_spans == [citation_B]
    # NOT tool_use_2.evidence_spans == [citation_A, citation_B]

def test_parser_handles_tool_call_with_no_preceding_citations():
    # tool_use with no preceding cited text → evidence_spans == [] (valid, not an error)

def test_parser_handles_unresolvable_reference_tool_calls():
    # Mixed fixture with both tools; output.unresolvable_references populated separately

def test_parser_empty_response_returns_empty_output():
    # Message with no tool calls → RetrievalOutput.cross_references == [], unresolvable_references == []

def test_parser_propagates_state_vintage_hop():
    # Parser takes state_abbr, vintage_year, hop as args (caller supplies — agent doesn't echo them in tool calls)

def test_parser_skips_text_blocks_without_citations():
    # Plain text between tool calls (no citations) doesn't error and doesn't pollute evidence_spans
```

### `tests/test_retrieval_v2_prompt.py`

These run against `src/scoring/retrieval_agent_prompt_v2.md`. Invariant tests catch PRI-key leakage from v1 carryover.

```python
import re
from pathlib import Path

V2_PROMPT_PATH = Path("src/scoring/retrieval_agent_prompt_v2.md")
PROMPT = V2_PROMPT_PATH.read_text()

def test_prompt_exists_and_nonempty():
    # PROMPT.strip() not empty; len(PROMPT) > 1000

def test_prompt_no_pri_rubric_letter_refs():
    # No "A1", "A2", ..., "A11", "C0", "C1", "C2", "C3" as standalone tokens
    # Use word-boundary regex: r"\b[AC]\d{1,2}\b"
    matches = re.findall(r"\b[AC]\d{1,2}\b", PROMPT)
    assert not matches, f"PRI rubric letter leaks: {matches}"

def test_prompt_no_rubric_items_affected_string():
    # The v1 output field "rubric_items_affected" must not appear

def test_prompt_no_rubric_word():
    # "rubric" should not appear as a standalone word (case insensitive)
    # Acceptable: never mention rubric. v2 anchors on chunks + cells, not rubrics.

def test_prompt_mentions_record_cross_reference_tool():
    # Prompt must instruct the agent to call this tool

def test_prompt_mentions_record_unresolvable_reference_tool():
    # Prompt must instruct the agent to call this tool

def test_prompt_anchors_at_least_three_chunk_names():
    # Verify chunk-anchoring landed: at least actor_registration_required, lobbying_definitions,
    # lobbyist_spending_report are named

def test_prompt_instructs_citation_before_tool_call():
    # Rule 5 must be present — some phrase like "cite the supporting statute span before calling"
    # or "before each tool call, reference the statute"
    # Loose match; this is what makes the parser's pairing rule load-bearing
```

### `tests/test_retrieval_v2_integration.py`

```python
import os
import pytest
import anthropic

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Integration test requires ANTHROPIC_API_KEY"
)

# Fixture: tests/fixtures/retrieval_v2/tiny_statute.txt
# Contents (3 sentences, 1 obvious cross-ref):
#   "Section 1. Every lobbyist must register as required in §99.005. A lobbyist is any
#    person who attempts to influence legislation. Section 2. Violations are punished
#    under §99.999."
# Expected: agent identifies §99.005 (registration mechanism) and §99.999 (penalties)
# as cross-refs and emits record_cross_reference tool calls for each.

def test_real_api_call_returns_citations():
    brief = build_retrieval_brief(state="ZZ", vintage=2026, statute_bundle=<tiny>,
                                  chunks=["actor_registration_required"])
    client = anthropic.Anthropic()
    response = client.messages.create(**brief)
    # Assert at least one content block has a non-empty citations list

def test_real_api_call_produces_at_least_one_cross_reference():
    # Same setup; assert response has at least 1 tool_use block calling record_cross_reference

def test_parser_handles_real_api_response():
    # Run parser on the real response; output.cross_references not empty;
    # each entry's evidence_spans has at least one EvidenceSpan
    # Save the response to tests/fixtures/retrieval_v2/sample_response.json
    # (run once; subsequent unit tests load this fixture)
```

**Gate for Phase 1:** all tests fail with import/attribute errors (not with assertions). Commit: `retrieval_v2: failing tests written (RED, all phases)`.

---

## Phase 2 — Tool definitions (GREEN for tool tests)

Implement `src/lobby_analysis/retrieval_v2/tools.py`:

```python
"""Tool definitions for the v2 retrieval agent.

Two tools:
- record_cross_reference: agent calls once per identified cross-reference
- record_unresolvable_reference: agent calls for references it cannot construct URLs for
"""
from lobby_analysis.chunks_v2 import build_chunks

_CHUNK_IDS = sorted(c.chunk_id for c in build_chunks())  # 15 chunk ids; sorted for determinism

CROSS_REFERENCE_TOOL = {
    "name": "record_cross_reference",
    "description": (
        "Record a cross-reference found in the statute bundle that the scorer will need. "
        "Call this tool once per cross-reference. Cite the statute span(s) supporting "
        "the cross-reference in the preceding text — those citations will be attached "
        "to this tool call as provenance."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "section_reference": {
                "type": "string",
                "description": "Citation as it appears in the statute text (e.g., '§311.005(2)', 'section 102.01 of the Revised Code').",
            },
            "chunk_ids_affected": {
                "type": "array",
                "items": {"type": "string", "enum": _CHUNK_IDS},
                "description": "Which v2 compendium chunks this cross-reference informs. Use the chunk names from the brief.",
            },
            "relevance": {
                "type": "string",
                "description": "Why the scorer needs this cross-reference and what information it provides.",
            },
            "justia_url": {
                "type": "string",
                "description": "Constructed Justia URL for fetching this section. Use the URL pattern from the brief.",
            },
            "url_confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "high = same title/pattern as core chapters; medium = different title, pattern inferred; low = significant uncertainty.",
            },
            "url_confidence_reason": {
                "type": "string",
                "description": "Brief explanation, especially for medium/low confidence.",
            },
        },
        "required": ["section_reference", "chunk_ids_affected", "relevance", "justia_url", "url_confidence"],
    },
}

UNRESOLVABLE_REFERENCE_TOOL = {
    "name": "record_unresolvable_reference",
    "description": (
        "Record a reference found in the statute text that cannot be resolved to a specific "
        "section number (e.g., 'as defined by applicable law'). The orchestrator logs these "
        "to surface gaps in the statute bundle, even though they cannot be fetched."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reference_text": {
                "type": "string",
                "description": "The reference text as it appears in the statute (verbatim).",
            },
            "referenced_from": {
                "type": "string",
                "description": "Filename or path of the statute file containing this reference.",
            },
            "reason": {
                "type": "string",
                "description": "Why this reference cannot be resolved (e.g., no section number cited).",
            },
        },
        "required": ["reference_text", "referenced_from", "reason"],
    },
}

ALL_TOOLS = [CROSS_REFERENCE_TOOL, UNRESOLVABLE_REFERENCE_TOOL]
```

**Gate:** `uv run pytest tests/test_retrieval_v2_tools.py` all green. Commit: `retrieval_v2: tool definitions (record_cross_reference + record_unresolvable_reference)`.

---

## Phase 3 — Pydantic models (GREEN for model tests)

Implement `src/lobby_analysis/retrieval_v2/models.py`:

```python
"""Typed output models for the v2 retrieval agent."""
from typing import Literal
from pydantic import BaseModel, Field

CitationType = Literal["char_location", "page_location", "content_block_location"]


class EvidenceSpan(BaseModel):
    """A citation span emitted by the Citations API."""
    model_config = {"frozen": True}

    citation_type: CitationType
    document_index: int  # 0-indexed position in original document list
    document_title: str | None = None
    cited_text: str  # Verbatim text from the source document — doesn't count toward tokens

    # For plain text (char_location): start_char_index, end_char_index (0-indexed, exclusive end)
    start_char_index: int | None = None
    end_char_index: int | None = None

    # For PDF (page_location): start_page_number, end_page_number (1-indexed, exclusive end)
    start_page_number: int | None = None
    end_page_number: int | None = None

    # For custom content (content_block_location): start_block_index, end_block_index
    start_block_index: int | None = None
    end_block_index: int | None = None


class CrossReference(BaseModel):
    """A cross-reference the agent identified, with citation provenance."""
    model_config = {"frozen": True}

    section_reference: str
    chunk_ids_affected: tuple[str, ...]  # tuple for hashability/frozenness
    relevance: str
    justia_url: str
    url_confidence: Literal["high", "medium", "low"]
    url_confidence_reason: str = ""
    evidence_spans: tuple[EvidenceSpan, ...] = ()  # citations attached to this tool call


class UnresolvableReference(BaseModel):
    """A reference the agent found but could not construct a URL for."""
    model_config = {"frozen": True}

    reference_text: str
    referenced_from: str
    reason: str
    evidence_spans: tuple[EvidenceSpan, ...] = ()


class RetrievalOutput(BaseModel):
    """Parsed output of a single retrieval call."""
    model_config = {"frozen": True}

    state_abbr: str
    vintage_year: int
    hop: int = Field(ge=1, le=2)
    cross_references: tuple[CrossReference, ...] = ()
    unresolvable_references: tuple[UnresolvableReference, ...] = ()
```

**Gate:** `uv run pytest tests/test_retrieval_v2_models.py` all green. Commit: `retrieval_v2: Pydantic output models`.

---

## Phase 4 — Brief-writer (GREEN for brief-writer tests)

Implement `src/lobby_analysis/retrieval_v2/brief_writer.py`. Key responsibilities:

1. Load the v2 prompt (`src/scoring/retrieval_agent_prompt_v2.md`).
2. Compute the cell roster for `chunks: list[str]` by looking up `build_chunks()` and emitting a chunk-organized cell list.
3. Package statute files as `type: "document"` content blocks with `citations: {enabled: True}` and `cache_control: {"type": "ephemeral"}`.
4. Return the kwargs dict for `messages.create()`.

```python
"""Build a retrieval brief for a (state, vintage, chunks) scope."""
from pathlib import Path
from lobby_analysis.chunks_v2 import build_chunks
from lobby_analysis.retrieval_v2.tools import ALL_TOOLS

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "src" / "scoring" / "retrieval_agent_prompt_v2.md"


def build_retrieval_brief(
    state: str,
    vintage: int,
    statute_bundle: list[dict],  # [{"path": "ch101.txt", "content": "...", "title": "..."}, ...]
    chunks: list[str],
    url_pattern: str = "",  # Example Justia URL for the agent to infer the pattern
) -> dict:
    """Assemble messages.create() kwargs for a retrieval call.

    Args:
        state: Two-letter state abbreviation (e.g., "OH").
        vintage: Vintage year (e.g., 2010).
        statute_bundle: List of statute file dicts, each with 'path', 'content', 'title'.
        chunks: List of chunk_ids to scope retrieval. Use chunk_ids from build_chunks().
        url_pattern: An example Justia URL from the core chapters; the agent infers
            the pattern for constructing URLs to referenced sections.

    Returns:
        Dict suitable for client.messages.create(**brief).
    """
    # Validate chunks: every requested chunk must exist in the manifest
    all_chunks = {c.chunk_id: c for c in build_chunks()}
    unknown = set(chunks) - set(all_chunks)
    if unknown:
        raise ValueError(f"Unknown chunks: {unknown}")

    # Build the cell roster (chunks-organized) for the user message
    cell_roster_text = _format_cell_roster([all_chunks[cid] for cid in chunks])

    # Load the prompt template
    prompt_template = _PROMPT_PATH.read_text()

    # Package documents
    document_blocks = [
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": doc["content"],
            },
            "title": doc.get("title", doc["path"]),
            "citations": {"enabled": True},
            "cache_control": {"type": "ephemeral"},
        }
        for doc in statute_bundle
    ]

    # User-facing instruction (post-documents)
    user_text = _build_user_text(state, vintage, cell_roster_text, url_pattern)

    return {
        "model": "claude-opus-4-7",
        "max_tokens": 16000,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "high"},
        "system": [
            {
                "type": "text",
                "text": prompt_template,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    *document_blocks,
                    {"type": "text", "text": user_text},
                ],
            }
        ],
        "tools": ALL_TOOLS,
    }


def _format_cell_roster(chunks: list) -> str:
    """Format chunks → cell-roster text the agent can read."""
    lines = []
    for chunk in chunks:
        lines.append(f"\n### Chunk: {chunk.chunk_id} ({len(chunk.cell_specs)} cells, {chunk.axis_summary})")
        lines.append(f"Topic: {chunk.topic}")
        for spec in chunk.cell_specs:
            lines.append(f"- {spec.row_id} ({spec.axis}): {spec.description[:120]}")
    return "\n".join(lines)


def _build_user_text(state: str, vintage: int, cell_roster: str, url_pattern: str) -> str:
    """Build the user-message text following the statute documents."""
    return (
        f"State: {state}\n"
        f"Vintage: {vintage}\n\n"
        f"Example URL pattern: {url_pattern}\n\n"
        f"## Compendium cells in scope for this call:\n{cell_roster}\n\n"
        f"Identify cross-references in the statute documents above. For each, call "
        f"`record_cross_reference` with the supporting statute span cited in the preceding text. "
        f"For references you cannot resolve to a section number, call `record_unresolvable_reference`."
    )
```

**Note on the path:** `_PROMPT_PATH` resolves to `src/scoring/retrieval_agent_prompt_v2.md` from the module location. Adjust the parent count if the layout differs at install time — verify with a path-resolution test.

**Gate:** `uv run pytest tests/test_retrieval_v2_brief_writer.py` all green. Commit: `retrieval_v2: brief_writer.py with documents + citations + caching`.

---

## Phase 5 — Parser (GREEN for parser tests)

Hand-craft the fixture `tests/fixtures/retrieval_v2/sample_response.json` first (matches documented Citations API response shape). Then implement the parser.

### Fixture: `tests/fixtures/retrieval_v2/sample_response.json`

```json
{
  "id": "msg_test",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-4-7",
  "content": [
    {"type": "text", "text": "I found a cross-reference to "},
    {
      "type": "text",
      "text": "§311.005",
      "citations": [
        {
          "type": "char_location",
          "cited_text": "as defined in §311.005",
          "document_index": 0,
          "document_title": "OH §101.70",
          "start_char_index": 245,
          "end_char_index": 267
        }
      ]
    },
    {"type": "text", "text": " which defines 'person'."},
    {
      "type": "tool_use",
      "id": "toolu_01",
      "name": "record_cross_reference",
      "input": {
        "section_reference": "§311.005",
        "chunk_ids_affected": ["lobbying_definitions", "actor_registration_required"],
        "relevance": "Defines 'person' — controls which entities must register",
        "justia_url": "https://law.justia.com/codes/ohio/2010/title3/chapter311/311_005.html",
        "url_confidence": "medium",
        "url_confidence_reason": "Title number for Chapter 311 inferred from pattern"
      }
    },
    {"type": "text", "text": "I also found an unresolvable reference: "},
    {
      "type": "text",
      "text": "applicable law",
      "citations": [
        {
          "type": "char_location",
          "cited_text": "as required by applicable law",
          "document_index": 0,
          "document_title": "OH §101.70",
          "start_char_index": 412,
          "end_char_index": 441
        }
      ]
    },
    {
      "type": "tool_use",
      "id": "toolu_02",
      "name": "record_unresolvable_reference",
      "input": {
        "reference_text": "as required by applicable law",
        "referenced_from": "OH §101.70",
        "reason": "No specific section number cited"
      }
    }
  ],
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 1000, "output_tokens": 200}
}
```

**Warning:** this fixture matches the *documented* response shape. The Phase 7 integration test records a real response; if the real shape differs, the fixture (and tests) get updated. **Pause and surface to user** if real-API shape diverges materially.

### Implementation: `src/lobby_analysis/retrieval_v2/parser.py`

```python
"""Parse messages.create() response into typed RetrievalOutput."""
from typing import Any
from lobby_analysis.retrieval_v2.models import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
)


def parse_retrieval_response(
    message: Any,  # anthropic.types.Message OR dict for fixture testing
    state_abbr: str,
    vintage_year: int,
    hop: int,
) -> RetrievalOutput:
    """Parse a Citations API response into structured output.

    Pairing rule: citations from text blocks accumulate until a tool_use block
    is encountered; those citations attach to that tool_use's parsed output.
    The buffer resets after each tool_use.
    """
    content = _get_content(message)  # handles both Message obj and dict fixture

    cross_refs: list[CrossReference] = []
    unresolvables: list[UnresolvableReference] = []
    citation_buffer: list[EvidenceSpan] = []

    for block in content:
        block_type = _get(block, "type")
        if block_type == "text":
            for raw_cite in _get(block, "citations", default=[]) or []:
                citation_buffer.append(_parse_citation(raw_cite))
        elif block_type == "tool_use":
            tool_name = _get(block, "name")
            tool_input = _get(block, "input")
            spans = tuple(citation_buffer)
            citation_buffer = []  # reset after attaching

            if tool_name == "record_cross_reference":
                cross_refs.append(CrossReference(
                    section_reference=tool_input["section_reference"],
                    chunk_ids_affected=tuple(tool_input["chunk_ids_affected"]),
                    relevance=tool_input["relevance"],
                    justia_url=tool_input["justia_url"],
                    url_confidence=tool_input["url_confidence"],
                    url_confidence_reason=tool_input.get("url_confidence_reason", ""),
                    evidence_spans=spans,
                ))
            elif tool_name == "record_unresolvable_reference":
                unresolvables.append(UnresolvableReference(
                    reference_text=tool_input["reference_text"],
                    referenced_from=tool_input["referenced_from"],
                    reason=tool_input["reason"],
                    evidence_spans=spans,
                ))
            # Unknown tool names are silently skipped — log if needed downstream
        # thinking blocks, server_tool_use, etc. are ignored for retrieval output

    return RetrievalOutput(
        state_abbr=state_abbr,
        vintage_year=vintage_year,
        hop=hop,
        cross_references=tuple(cross_refs),
        unresolvable_references=tuple(unresolvables),
    )


def _parse_citation(raw: Any) -> EvidenceSpan:
    """Parse a single citation dict/object into EvidenceSpan."""
    cite_type = _get(raw, "type")
    common = {
        "citation_type": cite_type,
        "document_index": _get(raw, "document_index"),
        "document_title": _get(raw, "document_title"),
        "cited_text": _get(raw, "cited_text"),
    }
    if cite_type == "char_location":
        return EvidenceSpan(
            **common,
            start_char_index=_get(raw, "start_char_index"),
            end_char_index=_get(raw, "end_char_index"),
        )
    elif cite_type == "page_location":
        return EvidenceSpan(
            **common,
            start_page_number=_get(raw, "start_page_number"),
            end_page_number=_get(raw, "end_page_number"),
        )
    elif cite_type == "content_block_location":
        return EvidenceSpan(
            **common,
            start_block_index=_get(raw, "start_block_index"),
            end_block_index=_get(raw, "end_block_index"),
        )
    else:
        raise ValueError(f"Unknown citation type: {cite_type}")


def _get_content(message: Any) -> list:
    """Get content blocks from either a Message object or dict."""
    if hasattr(message, "content"):
        return message.content
    return message.get("content", [])


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Attribute or dict access, depending on what we got."""
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default
```

**Gate:** `uv run pytest tests/test_retrieval_v2_parser.py` all green. Commit: `retrieval_v2: parser with citation→tool_use proximity pairing`.

---

## Phase 6 — v2 prompt markdown (GREEN for prompt-invariant tests)

Write `src/scoring/retrieval_agent_prompt_v2.md`. **Full draft inlined here** — implementer reviews and commits:

```markdown
# Statute Cross-Reference Retrieval Agent — Prompt v2

You are a cross-reference retrieval agent for US state lobbying statutes. Your job is to read a state's core lobbying statute chapters and identify cross-references to other sections, chapters, or titles that are needed to populate the v2 compendium's cells.

You will be given:

1. A **state abbreviation** and **vintage year** (e.g., `OH`, `2010`).
2. A **statute bundle** — the core lobbying chapter files attached as `document` content blocks with citations enabled. Cite spans of these documents in your text when supporting a finding.
3. A **cell roster** — the v2 compendium cells in scope for this call, organized by chunk. Tells you what information the downstream scorer needs.
4. An **example URL pattern** — a Justia URL from the core chapters so you can construct URLs for referenced sections in the same state and vintage.

Your job is to find cross-references that the scorer will need and **record each one via the `record_cross_reference` tool**, with the supporting statute span cited in the preceding text. For references you cannot resolve to a section number, call `record_unresolvable_reference`.

## Rules

### 1. Read all core chapter files first.

Process every document content block. Understand the structure: what definitions are provided, what terms are used without definition, what other sections or chapters are explicitly cited.

### 2. Identify cross-references relevant to the cell roster.

For each cross-reference you find, ask: "Does the downstream scorer need this to populate any of the cells in the roster?" Focus on:

- **Definitions — especially "person."** This is your highest priority. Nearly every state's lobbying chapter uses the term "person" (or equivalent: "individual," "entity") to define who must register. The definition is often NOT in the lobbying chapter — it's in a general definitions/construction act (e.g., TX Gov Code §311.005, OH Rev. Code §1.59). If the core lobbying chapter uses "person" without defining it, finding the general definitions section is critical. **This definition directly controls the 11 cells in the `actor_registration_required` chunk** (which entities must register as lobbyists) **and the `public_entity_def_*` cells in the `lobbying_definitions` chunk** (legal definition of "public entity"). Also look for definitions of "lobbyist," "expenditure," "public entity," "employer," and "compensation."
- **Penalties and enforcement** — referenced penalty chapters that determine whether violations have consequences. Relevant for cells in the `enforcement_and_audits` chunk.
- **Exemptions** — cross-referenced exemption provisions that affect which entities must register or disclose. Relevant for cells in the `registration_mechanics_and_exemptions` chunk.
- **Disclosure requirements** — if the lobbying chapter says "as required by [other section]," that other section contains information for the cells in the `lobbyist_spending_report`, `principal_spending_report`, `lobbying_contact_log`, and `other_lobbyist_filings` chunks.

Do **not** chase every cross-reference. Ignore references to:

- Procedural rules (legislative rules of order, committee assignments)
- Unrelated regulatory frameworks (tax code, election code — unless they define a term used in the lobbying chapter)
- Internal cross-references within the same chapter (the scorer already has those files)

### 3. Construct Justia URLs for each cross-reference.

Use the example URL pattern provided to construct URLs for referenced sections. The pattern varies by state and vintage — infer it from the example.

For example, if the core chapter URL is:
```
https://law.justia.com/codes/ohio/2010/title1/chapter101/101_70.html
```

Then a reference to §311.005 would be at:
```
https://law.justia.com/codes/ohio/2010/title3/chapter311/311_005.html
```

**Be explicit about uncertainty.** Pass `url_confidence` as one of:

- `"high"` — same title/pattern as the core chapter URLs (you're confident).
- `"medium"` — different title or pattern inferred from limited examples.
- `"low"` — significant uncertainty about the URL structure.

Use `url_confidence_reason` to explain medium/low cases. Do not fabricate a URL you aren't confident about.

### 4. Two-hop limit.

After the orchestrator fetches your hop-1 cross-references, you may be invoked again with the expanded bundle. On that second pass, identify any additional cross-references from the newly added support chapters (hop-2). **Stop after hop 2.** Do not request further hops.

On hop-2 passes, only report NEW cross-references — do not re-report references already in the bundle.

### 5. Cite the supporting span before each tool call.

For every `record_cross_reference` or `record_unresolvable_reference` call, **first emit a brief text passage citing the relevant statute span** — quote the cross-reference as it appears, attributed to the source document. The Citations API will attach that span as machine-verified provenance to your tool call. This is **load-bearing**: without preceding citations, downstream consumers have no proof of where the cross-reference was found.

Example flow:

> Looking at §101.70, I see the phrase "as defined in §311.005". This is a cross-reference to a definitional section.
>
> [call `record_cross_reference` with section_reference="§311.005", relevance="Defines 'person' — controls which entities must register", chunk_ids_affected=["lobbying_definitions", "actor_registration_required"], justia_url="...", url_confidence="medium", url_confidence_reason="Title number for Chapter 311 inferred"]

The citation block will be automatically attached to your quote of `"as defined in §311.005"`.

### 6. Use `record_unresolvable_reference` for human-readable but unresolved references.

If the statute says something like "as required by applicable law" without a specific section number, call `record_unresolvable_reference` instead of fabricating a URL. The orchestrator logs these to surface gaps in the statute bundle.

### 7. When you are done, stop.

After identifying and recording all cross-references, end your response. Do not summarize or explain — your job is done when the tool calls are recorded.
```

**Gate:** `uv run pytest tests/test_retrieval_v2_prompt.py` all green. Implement `prompt.py`'s `load_v2_prompt()` if the brief-writer doesn't already inline-load it. Commit: `retrieval_v2: v2 prompt markdown (chunk-anchored, citations + tool-use shape)`.

---

## Phase 7 — Integration smoke test (T1 gate)

This is the **first time we exercise real Citations API behavior**. Both the plan author and you (implementer) are first-time users — what we expect from the docs may diverge from what we get.

### Cost discipline — smallest functional call

The integration test runs **automatically on every `uv run pytest` invocation when `ANTHROPIC_API_KEY` is set** (via `pytest.mark.skipif`). It does **not** require a special flag. To keep this cost-trivial:

- **Fixture is 2 sentences with 2 obvious cross-refs** — the minimum that meaningfully tests both `record_cross_reference` AND verifies citations attach to text blocks. Don't pad it.
- **`max_tokens=2000` in the integration brief** (override the production default of 16000). The test is a smoke check, not a real retrieval — 2K is plenty for "did Claude emit some tool calls with citations attached".
- **Single chunk in scope** — pass `chunks=["actor_registration_required"]` only. Limits the cell roster to ~11 cells in the user message; keeps input small.
- **Pricing estimate** (Opus 4.7 @ $5/M input + $25/M output): ~2K input + ~500 output ≈ **$0.02 per test run**. Negligible.

### Fixture: `tests/fixtures/retrieval_v2/tiny_statute.txt`

Two-sentence minimum:

```
A lobbyist must register as defined in §99.005. Violations are punished under §99.999.
```

Two obvious cross-references (§99.005 for "lobbyist" definition → `actor_registration_required` chunk; §99.999 for penalties → `enforcement_and_audits` chunk).

### Steps

1. Confirm `ANTHROPIC_API_KEY` is set. (`echo $ANTHROPIC_API_KEY | wc -c` — should be non-zero.)
2. Create `tests/fixtures/retrieval_v2/tiny_statute.txt` with the 2-sentence fixture above.
3. Run `uv run pytest tests/test_retrieval_v2_integration.py -v`.
4. **If tests fail because the response shape differs from the documented shape:** STOP. Surface to user. Do not silently patch the parser to handle the divergence — the user wants to know about docs↔reality mismatches before they get papered over.
5. **If tests pass:** save the real API response as `tests/fixtures/retrieval_v2/sample_response.json` (overwriting the hand-crafted fixture from Phase 5). Re-run `uv run pytest tests/test_retrieval_v2_parser.py` to confirm the parser still works against the real shape. If parser tests now fail, the divergence was subtle — surface to user.

After Phase 7 lands, every subsequent `uv run pytest` re-validates against the live Citations API (when key is set). This catches API drift early — if Anthropic changes citation response shape in a way that breaks the parser, our test suite tells us within one pytest run rather than during a real retrieval.

### What to verify by hand

- `response.content` contains both `text` blocks (with `citations` lists) and `tool_use` blocks.
- At least one `record_cross_reference` tool call fires.
- Citation `start_char_index` / `end_char_index` ranges in the fixture are sensible (point at expected substrings).
- `response.usage` shows non-zero `cache_creation_input_tokens` (first call writes cache) — on a *second* identical call, look for `cache_read_input_tokens` instead.

### Things that may go wrong (each requires pause + surface)

- **Citations don't attach to text blocks** (returned as empty `citations: []`). → Possible cause: tiny fixture is too short for the chunker; try a larger fixture.
- **Tool calls fire without any preceding cited text.** → Rule 5 isn't load-bearing enough; prompt needs sharpening.
- **Citations attach to text blocks AFTER tool calls instead of before.** → Pairing rule needs revision; may need a heuristic that walks BOTH directions or attaches to the nearest tool call.
- **`record_cross_reference` not called at all** (agent returns plain prose). → Tool-use guidance in the prompt is too weak; need to make tool-call mandatory in the wording.
- **Schema validation errors on `chunk_ids_affected`** (agent passes "actor_registration" instead of "actor_registration_required"). → Prompt needs the full chunk_id list explicit, or the enum needs synonyms.
- **`cache_control` doesn't work as expected with citations.** → Per docs it should; if it doesn't, the design's caching efficiency assumption breaks. Surface for re-evaluation.

**Gate:** integration tests pass; `sample_response.json` saved from real API. Commit: `retrieval_v2: integration test green; sample_response.json captured from real API`.

---

## Phase 8 — Suite-wide green + lint

1. `uv run pytest` — full suite passes. The 3 pre-existing `test_pipeline.py` failures (portal-snapshot fixture data missing on main) are expected; everything else green.
2. `uv run ruff check src/lobby_analysis/retrieval_v2/ tests/test_retrieval_v2_*.py`
3. `uv run ruff format src/lobby_analysis/retrieval_v2/ tests/test_retrieval_v2_*.py`
4. Update `src/lobby_analysis/retrieval_v2/__init__.py` to re-export public API:

```python
"""v2 retrieval agent — Citations API + tool use over the v2 compendium."""
from lobby_analysis.retrieval_v2.brief_writer import build_retrieval_brief
from lobby_analysis.retrieval_v2.models import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
)
from lobby_analysis.retrieval_v2.parser import parse_retrieval_response
from lobby_analysis.retrieval_v2.tools import (
    ALL_TOOLS,
    CROSS_REFERENCE_TOOL,
    UNRESOLVABLE_REFERENCE_TOOL,
)

__all__ = [
    "ALL_TOOLS",
    "CROSS_REFERENCE_TOOL",
    "CrossReference",
    "EvidenceSpan",
    "RetrievalOutput",
    "UNRESOLVABLE_REFERENCE_TOOL",
    "UnresolvableReference",
    "build_retrieval_brief",
    "parse_retrieval_response",
]
```

5. Write `src/lobby_analysis/retrieval_v2/docs.md` — module-level docs matching the existing `chunks_v2/docs.md` and `models_v2/docs.md` patterns.

Commit: `retrieval_v2: public exports + module docs; ruff clean`.

---

## Phase 9 — RESEARCH_LOG update + finish-convo

Update `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` with the implementation session entry. Then run finish-convo per `skills/finish-convo/SKILL.md`.

The RESEARCH_LOG entry should record:

- The Citations API pivot landing
- What worked vs what surprised you during integration test
- Whether the parser's pairing rule held up against real API behavior
- T1 gate passed; T2-T4 are downstream
- Anthropic SDK now in pyproject.toml

---

## Things explicitly out of scope

- **Calling the SDK in production.** The brief-writer returns kwargs; the orchestrator dispatches. No production-runner this session.
- **Compaction, streaming, batching.** Retrieval is a single non-streaming call.
- **Embedding-based retrieval.** Locked off in kickoff brainstorm Q2.
- **Per-rubric projection.** Lives on `phase-c-projection-tdd`.
- **The scorer prompt rewrite.** Next downstream component after this lands.
- **Multi-vintage validation.** Lives on `oh-statute-retrieval`.
- **Full 50-state runs.** T4 tier; downstream after the scorer-prompt component.

## Carry-forward links

1. [`../convos/20260514_retrieval_brainstorm.md`](../convos/20260514_retrieval_brainstorm.md) — origin convo with locked Q's
2. [`20260514_retrieval_plan_sketch.md`](20260514_retrieval_plan_sketch.md) — original 7-Q agenda
3. [`20260514_chunks_implementation_plan.md`](20260514_chunks_implementation_plan.md) — sibling contract (chunks manifest)
4. [`../../../../src/scoring/retrieval_agent_prompt.md`](../../../../src/scoring/retrieval_agent_prompt.md) — v1 prompt (rewrite source)
5. [`../../../../compendium/disclosure_side_compendium_items_v2.tsv`](../../../../compendium/disclosure_side_compendium_items_v2.tsv) — row-freeze contract (181 rows)
6. [`_handoffs/20260514_retrieval_brainstorm_handoff.md`](_handoffs/20260514_retrieval_brainstorm_handoff.md) — handoff that originated this session

## Commit log (anticipated)

| Phase | Commit |
|---|---|
| 0 | `retrieval_v2: scaffolding (empty module + anthropic SDK dependency)` |
| 1 | `retrieval_v2: failing tests written (RED, all phases)` |
| 2 | `retrieval_v2: tool definitions (record_cross_reference + record_unresolvable_reference)` |
| 3 | `retrieval_v2: Pydantic output models` |
| 4 | `retrieval_v2: brief_writer.py with documents + citations + caching` |
| 5 | `retrieval_v2: parser with citation→tool_use proximity pairing` |
| 6 | `retrieval_v2: v2 prompt markdown (chunk-anchored, citations + tool-use shape)` |
| 7 | `retrieval_v2: integration test green; sample_response.json captured from real API` |
| 8 | `retrieval_v2: public exports + module docs; ruff clean` |
| 9 | (RESEARCH_LOG update + finish-convo commit) |

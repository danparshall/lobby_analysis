"""Tool definitions for the v2 retrieval agent.

Two tools the agent calls during retrieval:

- ``record_cross_reference`` — once per identified cross-reference. Required
  fields capture what the downstream scorer needs (section reference, which
  v2 chunks it informs, a constructed Justia URL with explicit confidence).
- ``record_unresolvable_reference`` — for references that cannot be resolved
  to a section number (e.g., "as defined by applicable law"). No URL field
  by design.

The ``chunk_ids_affected`` enum is sourced from
:func:`lobby_analysis.chunks_v2.build_chunks` so the tool schema cannot drift
from the chunks manifest. A coupling test in ``tests/test_retrieval_v2_tools.py``
enforces equality.

Citations (Anthropic Citations API) attach to text blocks preceding each
tool call as machine-verified provenance — see Rule 5 in
``src/scoring/retrieval_agent_prompt_v2.md``.
"""

from lobby_analysis.chunks_v2 import build_chunks

_CHUNK_IDS = sorted(c.chunk_id for c in build_chunks())


CROSS_REFERENCE_TOOL: dict = {
    "name": "record_cross_reference",
    "description": (
        "Record a cross-reference found in the statute bundle that the scorer "
        "will need. Call this tool once per cross-reference. Cite the statute "
        "span(s) supporting the cross-reference in the preceding text — those "
        "citations will be attached to this tool call as provenance."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "section_reference": {
                "type": "string",
                "description": (
                    "Citation as it appears in the statute text "
                    "(e.g., '§311.005(2)', 'section 102.01 of the Revised Code')."
                ),
            },
            "chunk_ids_affected": {
                "type": "array",
                "items": {"type": "string", "enum": _CHUNK_IDS},
                "description": (
                    "Which v2 compendium chunks this cross-reference informs. "
                    "Use the chunk names from the brief."
                ),
            },
            "relevance": {
                "type": "string",
                "description": (
                    "Why the scorer needs this cross-reference and what "
                    "information it provides."
                ),
            },
            "justia_url": {
                "type": "string",
                "description": (
                    "Constructed Justia URL for fetching this section. "
                    "Use the URL pattern from the brief."
                ),
            },
            "url_confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": (
                    "high = same title/pattern as core chapters; "
                    "medium = different title, pattern inferred; "
                    "low = significant uncertainty."
                ),
            },
            "url_confidence_reason": {
                "type": "string",
                "description": (
                    "Brief explanation, especially for medium/low confidence."
                ),
            },
        },
        "required": [
            "section_reference",
            "chunk_ids_affected",
            "relevance",
            "justia_url",
            "url_confidence",
        ],
    },
}


UNRESOLVABLE_REFERENCE_TOOL: dict = {
    "name": "record_unresolvable_reference",
    "description": (
        "Record a reference found in the statute text that cannot be resolved "
        "to a specific section number (e.g., 'as defined by applicable law'). "
        "The orchestrator logs these to surface gaps in the statute bundle, "
        "even though they cannot be fetched."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reference_text": {
                "type": "string",
                "description": (
                    "The reference text as it appears in the statute (verbatim)."
                ),
            },
            "referenced_from": {
                "type": "string",
                "description": (
                    "Filename or path of the statute file containing this reference."
                ),
            },
            "reason": {
                "type": "string",
                "description": (
                    "Why this reference cannot be resolved "
                    "(e.g., no section number cited)."
                ),
            },
        },
        "required": ["reference_text", "referenced_from", "reason"],
    },
}


ALL_TOOLS: list[dict] = [CROSS_REFERENCE_TOOL, UNRESOLVABLE_REFERENCE_TOOL]

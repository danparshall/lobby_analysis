"""Tier-0 direct-read smoke test (Claude + GPT side-by-side).

See `docs/active/extraction-harness-brainstorm/plans/20260518_tier_0_direct_read_smoke_test.md`
for the full plan and the originating convo
`docs/active/extraction-harness-brainstorm/convos/20260518_tier_0_execution_pivot_to_direct_read.md`
for why this script exists in the shape it does.

Architecture: one API call per model, per chunk. The OH 2025 statute lives in
the cached system prompt; the per-chunk user message lists the questions; the
scorer emits `record_cell` (with free-text `cited_section` + 1-sentence
`justification` for downstream verifier provenance) or `record_unscoreable_cell`.

Single-file by design (YAGNI per the originating convo) — no new packaged
module. Parser tests load this file via `importlib.util` so the file stays
script-shaped while still being testable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Shared JSON Schemas — one source of truth, two SDK wrappers below.
# Anthropic puts schema under `input_schema`; OpenAI under `function.parameters`.
# ---------------------------------------------------------------------------

RECORD_CELL_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "row_id": {
            "type": "string",
            "description": "Compendium row id (one of the chunk's row_ids).",
        },
        "axis": {
            "type": "string",
            "enum": ["legal", "practical"],
        },
        "value": {
            # Loose JSON value; the script-side adapter validates per-cell-class
            # after registry lookup (some cell types take dicts, not scalars).
            "oneOf": [
                {"type": "number"},
                {"type": "integer"},
                {"type": "string"},
                {"type": "boolean"},
                {"type": "array"},
                {"type": "object"},
                {"type": "null"},
            ],
        },
        "condition_text": {"type": ["string", "null"]},
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
        "cited_section": {
            "type": "string",
            "description": (
                "Free-text statute section reference, e.g. '§101.85(B)(2)' or "
                "'section 101.85 of the Revised Code'. The downstream verifier "
                "reads this section and rules on whether it actually supports the value."
            ),
        },
        "justification": {
            "type": "string",
            "description": (
                "One sentence explaining how the cited section supports the value. "
                "Used by the downstream verifier."
            ),
        },
    },
    "required": [
        "row_id",
        "axis",
        "value",
        "confidence",
        "cited_section",
        "justification",
    ],
}

RECORD_UNSCOREABLE_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "row_id": {"type": "string"},
        "axis": {
            "type": "string",
            "enum": ["legal", "practical"],
        },
        "reason": {
            "type": "string",
            "description": (
                "Why this cell could not be scored from the bundle "
                "(e.g., 'penalty schedule referenced but §307.99 not included')."
            ),
        },
    },
    "required": ["row_id", "axis", "reason"],
}


# ---------------------------------------------------------------------------
# SDK wrappers — same logical tool, two wire formats.
# ---------------------------------------------------------------------------

_RECORD_CELL_DESCRIPTION = (
    "Record a typed answer for one compendium cell. Call this once per "
    "(row_id, axis) you can answer. Cite the specific statute section that "
    "supports the value; a one-sentence justification will be checked by a "
    "downstream verifier reading that section."
)

_RECORD_UNSCOREABLE_DESCRIPTION = (
    "Record that a compendium cell cannot be answered from the bundled "
    "statute text (e.g., the law references a penalty schedule in a "
    "different chapter that isn't shown). Provide a brief reason. "
    "Do not guess."
)


ANTHROPIC_TOOLS: list[dict[str, Any]] = [
    {
        "name": "record_cell",
        "description": _RECORD_CELL_DESCRIPTION,
        "input_schema": RECORD_CELL_INPUT_SCHEMA,
    },
    {
        "name": "record_unscoreable_cell",
        "description": _RECORD_UNSCOREABLE_DESCRIPTION,
        "input_schema": RECORD_UNSCOREABLE_INPUT_SCHEMA,
    },
]


OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "record_cell",
            "description": _RECORD_CELL_DESCRIPTION,
            "parameters": RECORD_CELL_INPUT_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unscoreable_cell",
            "description": _RECORD_UNSCOREABLE_DESCRIPTION,
            "parameters": RECORD_UNSCOREABLE_INPUT_SCHEMA,
        },
    },
]


KNOWN_TOOL_NAMES: frozenset[str] = frozenset({"record_cell", "record_unscoreable_cell"})


# ---------------------------------------------------------------------------
# Parser — returns `(tool_name, input_dict)` pairs, SDK-agnostic.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedToolCall:
    """One tool invocation pulled out of either SDK's response.

    `tool_name` is the model-emitted name (NOT yet validated against
    `KNOWN_TOOL_NAMES` — the caller decides whether to log+skip unknowns
    or treat them as fatal).

    `arguments` is the parsed argument dict — for OpenAI this means
    `json.loads`ing the wire-format string; for Anthropic the SDK already
    delivers a dict.
    """

    tool_name: str
    arguments: dict[str, Any]


def _attr_or_key(obj: Any, name: str) -> Any:
    """Read either attribute (SDK objects) or key (test fixtures / raw dicts).

    SDK responses ship Pydantic-shaped objects; tests pass plain dicts or
    SimpleNamespace. Supporting both keeps the parser usable in both worlds
    without forcing tests to construct full SDK types.
    """
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def parse_anthropic_response(response: Any) -> list[ParsedToolCall]:
    """Extract tool calls from an Anthropic Messages API response.

    Walks `response.content` for `tool_use` blocks. Raises `ValueError` if
    a tool_use block is missing required wire fields — that's a contract
    break worth surfacing, not silently dropping.
    """
    content = _attr_or_key(response, "content")
    if content is None:
        raise ValueError("Anthropic response has no `.content`")
    calls: list[ParsedToolCall] = []
    for block in content:
        block_type = _attr_or_key(block, "type")
        if block_type != "tool_use":
            continue
        name = _attr_or_key(block, "name")
        arguments = _attr_or_key(block, "input")
        if name is None or arguments is None:
            raise ValueError(
                f"Anthropic tool_use block missing name/input: {block!r}"
            )
        if not isinstance(arguments, dict):
            raise ValueError(
                f"Anthropic tool_use `input` should be a dict, got {type(arguments).__name__}"
            )
        calls.append(ParsedToolCall(tool_name=name, arguments=dict(arguments)))
    return calls


def parse_openai_response(response: Any) -> list[ParsedToolCall]:
    """Extract tool calls from an OpenAI chat.completions API response.

    Walks `response.choices[0].message.tool_calls`. Each call has
    `.function.name` and `.function.arguments` (a JSON string). Raises
    `json.JSONDecodeError` on malformed argument JSON — silently dropping a
    malformed tool call would hide a real model failure.
    """
    choices = _attr_or_key(response, "choices")
    if not choices:
        raise ValueError("OpenAI response has no choices")
    message = _attr_or_key(choices[0], "message")
    if message is None:
        raise ValueError("OpenAI response choice missing `.message`")
    tool_calls = _attr_or_key(message, "tool_calls") or []
    calls: list[ParsedToolCall] = []
    for tc in tool_calls:
        function = _attr_or_key(tc, "function")
        if function is None:
            raise ValueError(f"OpenAI tool_call missing `.function`: {tc!r}")
        name = _attr_or_key(function, "name")
        arguments_json = _attr_or_key(function, "arguments")
        if name is None or arguments_json is None:
            raise ValueError(
                f"OpenAI tool_call missing name/arguments: {tc!r}"
            )
        # Per the OpenAI contract, `arguments` is always a JSON-encoded string.
        # Let json.loads raise on malformed — surfacing the failure beats
        # dropping the call silently.
        arguments = json.loads(arguments_json)
        if not isinstance(arguments, dict):
            raise ValueError(
                f"OpenAI tool_call arguments should decode to a dict, "
                f"got {type(arguments).__name__}"
            )
        calls.append(ParsedToolCall(tool_name=name, arguments=arguments))
    return calls


def parse_response(
    response: Any,
    sdk: Literal["anthropic", "openai"],
) -> list[ParsedToolCall]:
    """Dispatch to the per-SDK parser. Single entry point for the script."""
    if sdk == "anthropic":
        return parse_anthropic_response(response)
    if sdk == "openai":
        return parse_openai_response(response)
    raise ValueError(f"Unknown sdk: {sdk!r}")


# ---------------------------------------------------------------------------
# Step 4 (smoke-test dispatch) lives below this point — added in a later
# commit. The schemas + parser above are independently testable from
# `tests/test_tier_0_smoke_parser.py`.
# ---------------------------------------------------------------------------

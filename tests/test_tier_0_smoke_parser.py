"""Parser unit tests for ``scripts/tier_0_direct_read_smoke.py``.

The script is intentionally single-file (YAGNI per the originating convo).
This test module loads it via ``importlib.util.spec_from_file_location`` so the
parser + schemas stay in ``scripts/`` while still being unit-testable.

What's tested:

- ``parse_response`` returns the right number of tool calls for each SDK
  shape.
- Each parsed call's ``arguments`` dict carries all required schema fields.
- ``parse_openai_response`` raises ``json.JSONDecodeError`` on malformed
  function arguments rather than silently dropping the call.
- ``parse_anthropic_response`` raises ``ValueError`` on tool_use blocks with
  missing wire fields.
- Both ``ANTHROPIC_TOOLS`` and ``OPENAI_TOOLS`` share the same underlying
  ``RECORD_CELL_INPUT_SCHEMA`` and ``RECORD_UNSCOREABLE_INPUT_SCHEMA`` —
  the SDK wrappers don't drift.

Fixtures are minimal SimpleNamespace + dict objects shaped to the documented
SDK contracts. After Tier-0 Step 5 runs, real frozen responses can be added
alongside these synthesized ones; they exercise the same parser code.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tier_0_direct_read_smoke.py"


def _load_script_module():
    """Load the smoke script as an importable module without executing main()."""
    spec = importlib.util.spec_from_file_location("tier_0_direct_read_smoke", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"could not load spec for {_SCRIPT_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


smoke = _load_script_module()


# ---------------------------------------------------------------------------
# Fixture builders — synthesized SDK responses shaped to documented contracts.
# ---------------------------------------------------------------------------


def _make_anthropic_response(content_blocks: list[dict]):
    """SDK ships Pydantic-typed objects; SimpleNamespace mimics the access shape."""
    blocks = [SimpleNamespace(**b) for b in content_blocks]
    return SimpleNamespace(content=blocks)


def _make_openai_response(tool_calls: list[dict]):
    """OpenAI tool_calls live under choices[0].message.tool_calls."""
    typed_calls = []
    for tc in tool_calls:
        function = SimpleNamespace(**tc["function"])
        typed_calls.append(SimpleNamespace(function=function, id=tc.get("id", "call_0"), type="function"))
    message = SimpleNamespace(tool_calls=typed_calls, role="assistant", content=None)
    choice = SimpleNamespace(message=message, finish_reason="tool_calls", index=0)
    return SimpleNamespace(choices=[choice])


_VALID_CELL_ARGS = {
    "row_id": "report_includes_lobbyist_count_total_and_FTE",
    "axis": "legal",
    "value": True,
    "condition_text": None,
    "confidence": "high",
    "cited_section": "§101.70(B)(2)",
    "justification": "Section 101.70(B)(2) requires the lobbyist count in every spending report.",
}

_VALID_UNSCOREABLE_ARGS = {
    "row_id": "consultant_lobbyist_report_includes_income_by_source_type",
    "axis": "practical",
    "reason": "Bundle does not include §307.99 referenced by §101.99 for penalties.",
}


# ---------------------------------------------------------------------------
# Anthropic-shape tests
# ---------------------------------------------------------------------------


def test_anthropic_parser_returns_one_call_per_tool_use_block():
    """Two tool_use blocks → two ParsedToolCalls, in source order."""
    response = _make_anthropic_response(
        [
            {"type": "text", "text": "First, a thought..."},
            {"type": "tool_use", "name": "record_cell", "input": _VALID_CELL_ARGS, "id": "tu_1"},
            {"type": "text", "text": "And another..."},
            {"type": "tool_use", "name": "record_unscoreable_cell", "input": _VALID_UNSCOREABLE_ARGS, "id": "tu_2"},
        ]
    )
    parsed = smoke.parse_response(response, "anthropic")
    assert len(parsed) == 2
    assert parsed[0].tool_name == "record_cell"
    assert parsed[1].tool_name == "record_unscoreable_cell"


def test_anthropic_parser_skips_non_tool_use_blocks():
    """Pure-text response (no tool calls at all) parses to an empty list."""
    response = _make_anthropic_response(
        [{"type": "text", "text": "I'd rather just write prose."}]
    )
    parsed = smoke.parse_response(response, "anthropic")
    assert parsed == []


def test_anthropic_record_cell_arguments_carry_all_required_fields():
    """Every required schema field comes through to ParsedToolCall.arguments."""
    response = _make_anthropic_response(
        [{"type": "tool_use", "name": "record_cell", "input": _VALID_CELL_ARGS, "id": "tu_1"}]
    )
    parsed = smoke.parse_response(response, "anthropic")
    args = parsed[0].arguments
    for field in smoke.RECORD_CELL_INPUT_SCHEMA["required"]:
        assert field in args, f"required field {field!r} missing from parsed arguments"


def test_anthropic_parser_raises_on_tool_use_missing_input():
    """A malformed tool_use block surfaces as ValueError rather than silent skip."""
    response = _make_anthropic_response(
        [{"type": "tool_use", "name": "record_cell", "id": "tu_1"}]  # no `input`
    )
    with pytest.raises(ValueError, match="missing name/input"):
        smoke.parse_response(response, "anthropic")


def test_anthropic_parser_raises_when_input_is_not_a_dict():
    """Anthropic's `input` is always a JSON object. A string sneaking through is a bug."""
    response = _make_anthropic_response(
        [{"type": "tool_use", "name": "record_cell", "input": "not a dict", "id": "tu_1"}]
    )
    with pytest.raises(ValueError, match="should be a dict"):
        smoke.parse_response(response, "anthropic")


def test_anthropic_parser_returns_independent_dict_copies():
    """The parsed `arguments` should not alias the response's input dict —
    downstream mutation must not bleed back into the captured response."""
    original = dict(_VALID_CELL_ARGS)
    response = _make_anthropic_response(
        [{"type": "tool_use", "name": "record_cell", "input": original, "id": "tu_1"}]
    )
    parsed = smoke.parse_response(response, "anthropic")
    parsed[0].arguments["confidence"] = "low"
    assert original["confidence"] == "high", "parser leaked a reference to the response's input dict"


# ---------------------------------------------------------------------------
# OpenAI-shape tests
# ---------------------------------------------------------------------------


def test_openai_parser_returns_one_call_per_tool_call():
    """Two tool_calls → two ParsedToolCalls."""
    response = _make_openai_response(
        [
            {
                "id": "call_a",
                "function": {
                    "name": "record_cell",
                    "arguments": json.dumps(_VALID_CELL_ARGS),
                },
            },
            {
                "id": "call_b",
                "function": {
                    "name": "record_unscoreable_cell",
                    "arguments": json.dumps(_VALID_UNSCOREABLE_ARGS),
                },
            },
        ]
    )
    parsed = smoke.parse_response(response, "openai")
    assert len(parsed) == 2
    assert parsed[0].tool_name == "record_cell"
    assert parsed[1].tool_name == "record_unscoreable_cell"


def test_openai_parser_handles_zero_tool_calls():
    """A text-only response (no tool calls) parses to an empty list."""
    message = SimpleNamespace(tool_calls=None, role="assistant", content="prose")
    response = SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason="stop", index=0)])
    parsed = smoke.parse_response(response, "openai")
    assert parsed == []


def test_openai_record_cell_arguments_carry_all_required_fields():
    """JSON decoding round-trips every required field."""
    response = _make_openai_response(
        [
            {
                "id": "call_a",
                "function": {
                    "name": "record_cell",
                    "arguments": json.dumps(_VALID_CELL_ARGS),
                },
            }
        ]
    )
    parsed = smoke.parse_response(response, "openai")
    args = parsed[0].arguments
    for field in smoke.RECORD_CELL_INPUT_SCHEMA["required"]:
        assert field in args, f"required field {field!r} missing from parsed arguments"


def test_openai_parser_raises_on_malformed_json_arguments():
    """Malformed JSON in `function.arguments` must raise, not silently drop."""
    response = _make_openai_response(
        [
            {
                "id": "call_a",
                "function": {
                    "name": "record_cell",
                    "arguments": "{not valid json",
                },
            }
        ]
    )
    with pytest.raises(json.JSONDecodeError):
        smoke.parse_response(response, "openai")


def test_openai_parser_raises_when_arguments_decode_to_non_dict():
    """`arguments` should always decode to a JSON object. A bare string is a bug."""
    response = _make_openai_response(
        [
            {
                "id": "call_a",
                "function": {
                    "name": "record_cell",
                    "arguments": json.dumps("just a string"),
                },
            }
        ]
    )
    with pytest.raises(ValueError, match="decode to a dict"):
        smoke.parse_response(response, "openai")


def test_openai_parser_raises_when_function_missing():
    """An OpenAI tool_call without `.function` is malformed; surface it."""
    tc = SimpleNamespace(id="call_a", type="function")
    message = SimpleNamespace(tool_calls=[tc], role="assistant", content=None)
    response = SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason="tool_calls", index=0)])
    with pytest.raises(ValueError, match="missing `.function`"):
        smoke.parse_response(response, "openai")


# ---------------------------------------------------------------------------
# Dispatch + cross-SDK schema sharing
# ---------------------------------------------------------------------------


def test_unknown_sdk_raises():
    """`parse_response(response, 'gemini')` should explicitly fail rather than treat one SDK as a default."""
    with pytest.raises(ValueError, match="Unknown sdk"):
        smoke.parse_response(SimpleNamespace(content=[]), "gemini")  # type: ignore[arg-type]


def test_sdk_wrappers_share_input_schemas():
    """ANTHROPIC_TOOLS[i].input_schema must be the same object as
    OPENAI_TOOLS[i].function.parameters — otherwise the two SDK schemas can
    drift silently and the cross-model comparison stops being apples-to-apples."""
    anthropic_by_name = {t["name"]: t for t in smoke.ANTHROPIC_TOOLS}
    openai_by_name = {t["function"]["name"]: t for t in smoke.OPENAI_TOOLS}
    assert set(anthropic_by_name) == set(openai_by_name) == smoke.KNOWN_TOOL_NAMES
    for name in smoke.KNOWN_TOOL_NAMES:
        assert (
            anthropic_by_name[name]["input_schema"]
            is openai_by_name[name]["function"]["parameters"]
        ), f"SDK wrappers for {name!r} reference different schema objects"

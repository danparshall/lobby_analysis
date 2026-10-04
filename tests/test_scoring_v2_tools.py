"""Tests for scoring_v2 tool definitions.

Phase 1 (RED): all tests fail with ImportError because the names below
don't yet exist in lobby_analysis.scoring_v2.tools.

The two tools mirror retrieval_v2's pattern:
- record_cell: single polymorphic per-cell record (Q2 lock).
- record_unscoreable_cell: parallel to retrieval's record_unresolvable_reference.
"""

from lobby_analysis.scoring_v2.tools import (
    RECORD_CELL_TOOL,
    RECORD_UNSCOREABLE_CELL_TOOL,
)


def test_record_cell_tool_has_documented_name():
    assert RECORD_CELL_TOOL["name"] == "record_cell"


def test_record_unscoreable_cell_tool_has_documented_name():
    assert RECORD_UNSCOREABLE_CELL_TOOL["name"] == "record_unscoreable_cell"


def test_record_cell_tool_required_fields():
    required = RECORD_CELL_TOOL["input_schema"]["required"]
    assert required == ["row_id", "axis", "value", "confidence"]


def test_record_cell_tool_axis_enum():
    properties = RECORD_CELL_TOOL["input_schema"]["properties"]
    assert properties["axis"]["enum"] == ["legal", "practical"]


def test_record_cell_tool_confidence_enum():
    properties = RECORD_CELL_TOOL["input_schema"]["properties"]
    assert properties["confidence"]["enum"] == ["high", "medium", "low"]


def test_record_cell_tool_value_is_loose_json():
    """value.oneOf permits every JSON type per plan-write decision #2."""
    properties = RECORD_CELL_TOOL["input_schema"]["properties"]
    one_of = properties["value"]["oneOf"]
    types_present = {entry["type"] for entry in one_of}
    expected = {"number", "integer", "string", "boolean", "array", "object", "null"}
    assert types_present == expected, f"value.oneOf mismatch: {types_present}"


def test_record_unscoreable_cell_tool_required_fields():
    required = RECORD_UNSCOREABLE_CELL_TOOL["input_schema"]["required"]
    assert required == ["cell_id", "reason", "confidence"]


def test_record_cell_tool_row_id_is_string_with_parser_side_validation():
    """row_id is a string (no enum) per plan-write decision #1.

    COUPLING TEST: build_cell_spec_registry() returns ≥1 key so the parser
    has something to dispatch against. Lives in tools tests so a tools.py /
    parser.py drift surfaces on tools CI runs too.
    """
    from lobby_analysis.models_v2 import build_cell_spec_registry

    properties = RECORD_CELL_TOOL["input_schema"]["properties"]
    assert properties["row_id"]["type"] == "string"
    assert "enum" not in properties["row_id"]
    assert len(build_cell_spec_registry()) > 0

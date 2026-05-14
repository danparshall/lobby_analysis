"""Tests for retrieval_v2 tool definitions.

Phase 1 (RED): all tests fail with ImportError because the names below
don't yet exist in lobby_analysis.retrieval_v2.tools.
"""

from lobby_analysis.chunks_v2 import build_chunks
from lobby_analysis.retrieval_v2.tools import (
    CROSS_REFERENCE_TOOL,
    UNRESOLVABLE_REFERENCE_TOOL,
)


def test_cross_reference_tool_has_documented_name():
    assert CROSS_REFERENCE_TOOL["name"] == "record_cross_reference"


def test_unresolvable_reference_tool_has_documented_name():
    assert UNRESOLVABLE_REFERENCE_TOOL["name"] == "record_unresolvable_reference"


def test_cross_reference_tool_required_fields():
    required = CROSS_REFERENCE_TOOL["input_schema"]["required"]
    assert required == [
        "section_reference",
        "chunk_ids_affected",
        "relevance",
        "justia_url",
        "url_confidence",
    ]


def test_cross_reference_tool_url_confidence_enum():
    properties = CROSS_REFERENCE_TOOL["input_schema"]["properties"]
    assert properties["url_confidence"]["enum"] == ["high", "medium", "low"]


def test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest():
    """COUPLING TEST: catches drift between tools.py and chunks manifest."""
    expected = {c.chunk_id for c in build_chunks()}
    actual = set(
        CROSS_REFERENCE_TOOL["input_schema"]["properties"]["chunk_ids_affected"][
            "items"
        ]["enum"]
    )
    assert actual == expected, f"Drift: tools enum {actual} != chunks manifest {expected}"


def test_cross_reference_tool_chunk_ids_is_array():
    properties = CROSS_REFERENCE_TOOL["input_schema"]["properties"]
    assert properties["chunk_ids_affected"]["type"] == "array"
    assert properties["chunk_ids_affected"]["items"]["type"] == "string"


def test_unresolvable_reference_tool_required_fields():
    required = UNRESOLVABLE_REFERENCE_TOOL["input_schema"]["required"]
    assert required == ["reference_text", "referenced_from", "reason"]


def test_unresolvable_reference_tool_has_no_url_field():
    """By design — these are references we cannot construct URLs for."""
    properties = UNRESOLVABLE_REFERENCE_TOOL["input_schema"]["properties"]
    assert "justia_url" not in properties
    assert "url" not in properties

"""Tests for retrieval_v2 response parser.

Phase 1 (RED): all tests fail with ImportError because parse_retrieval_response
doesn't yet exist in lobby_analysis.retrieval_v2.parser.

Parser pairing rule: citations on text blocks accumulate until a tool_use
block is encountered; those citations attach to that tool_use's parsed
output. The buffer resets after each tool_use.
"""

import json
from pathlib import Path

from lobby_analysis.retrieval_v2.parser import parse_retrieval_response

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "retrieval_v2" / "sample_response.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def _xref_tool_use(section: str = "§1") -> dict:
    return {
        "type": "tool_use",
        "name": "record_cross_reference",
        "input": {
            "section_reference": section,
            "chunk_ids_affected": ["lobbying_definitions"],
            "relevance": "test",
            "justia_url": "https://example.com",
            "url_confidence": "high",
        },
    }


def test_parser_extracts_cross_references_from_tool_calls():
    """Fixture has 1 record_cross_reference tool call; output has 1 cross-ref."""
    out = parse_retrieval_response(_load_fixture(), state_abbr="OH", vintage_year=2010, hop=1)
    assert len(out.cross_references) == 1


def test_parser_pairs_preceding_citations_to_following_tool_call():
    """text_block_with_citation -> tool_use -> first tool's evidence_spans has citation."""
    out = parse_retrieval_response(_load_fixture(), state_abbr="OH", vintage_year=2010, hop=1)
    xref = out.cross_references[0]
    assert len(xref.evidence_spans) >= 1
    assert any("§311.005" in span.cited_text for span in xref.evidence_spans)


def test_parser_resets_citation_buffer_after_each_tool_call():
    """First tool's citations must not bleed into second tool's evidence_spans."""
    out = parse_retrieval_response(_load_fixture(), state_abbr="OH", vintage_year=2010, hop=1)
    xref = out.cross_references[0]
    unres = out.unresolvable_references[0]
    xref_cited = {span.cited_text for span in xref.evidence_spans}
    unres_cited = {span.cited_text for span in unres.evidence_spans}
    assert xref_cited & unres_cited == set(), (
        f"Citation bleed across tools: shared={xref_cited & unres_cited}"
    )


def test_parser_handles_tool_call_with_no_preceding_citations():
    """tool_use with no preceding cited text -> evidence_spans == ()."""
    message = {"content": [_xref_tool_use()]}
    out = parse_retrieval_response(message, state_abbr="OH", vintage_year=2010, hop=1)
    assert out.cross_references[0].evidence_spans == ()


def test_parser_handles_unresolvable_reference_tool_calls():
    """Mixed fixture has both kinds; unresolvable_references populated separately."""
    out = parse_retrieval_response(_load_fixture(), state_abbr="OH", vintage_year=2010, hop=1)
    assert len(out.unresolvable_references) == 1


def test_parser_empty_response_returns_empty_output():
    """Message with no tool calls -> RetrievalOutput with empty tuples."""
    out = parse_retrieval_response({"content": []}, state_abbr="OH", vintage_year=2010, hop=1)
    assert out.cross_references == ()
    assert out.unresolvable_references == ()


def test_parser_propagates_state_vintage_hop():
    """Parser takes state_abbr, vintage_year, hop as args (caller supplies)."""
    out = parse_retrieval_response({"content": []}, state_abbr="TX", vintage_year=2025, hop=2)
    assert out.state_abbr == "TX"
    assert out.vintage_year == 2025
    assert out.hop == 2


def test_parser_skips_text_blocks_without_citations():
    """Plain text between tool calls (no citations) doesn't error or pollute spans."""
    message = {
        "content": [
            {"type": "text", "text": "Some prose with no citations."},
            _xref_tool_use(),
        ]
    }
    out = parse_retrieval_response(message, state_abbr="OH", vintage_year=2010, hop=1)
    assert out.cross_references[0].evidence_spans == ()

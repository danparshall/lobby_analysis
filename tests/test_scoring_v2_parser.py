"""Tests for scoring_v2 response parser.

Phase 1 (RED): all tests fail with ImportError because parse_scoring_response
doesn't yet exist in lobby_analysis.scoring_v2.parser.

Parser pairing rule mirrors retrieval_v2's: citations accumulate in a buffer
on text blocks until a tool_use block; then they attach to that tool call.
"""

import json
import logging
from pathlib import Path
from types import SimpleNamespace

from lobby_analysis.scoring_v2.parser import parse_scoring_response

FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "scoring_v2" / "sample_response.json"
)


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def test_parser_extracts_cells_from_record_cell_tool_calls():
    """Fixture has 2 record_cell tool calls; output.cells has 2 entries."""
    out = parse_scoring_response(
        _load_fixture(),
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    assert len(out.cells) == 2


def test_parser_dispatches_to_expected_cell_class_per_row():
    """Each record_cell tool call dispatches to spec.expected_cell_class via the registry."""
    from lobby_analysis.models_v2 import BinaryCell

    out = parse_scoring_response(
        _load_fixture(),
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    # First fixture cell is a BinaryCell-shaped (lobbying_violation_penalties_imposed_in_practice:legal).
    assert any(isinstance(c, BinaryCell) for c in out.cells)


def test_parser_pairs_preceding_citations_to_following_tool_call():
    """text_with_citation -> record_cell -> first tool's provenance has that citation."""
    out = parse_scoring_response(
        _load_fixture(),
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    assert len(out.cells) >= 1
    # At least the first cell has provenance (the fixture's first text block cites
    # the audit clause before record_cell #1).
    assert len(out.cells[0].provenance) >= 1


def test_parser_resets_citation_buffer_after_each_tool_call():
    """Citations from cell #1 do NOT bleed into cell #2's provenance.

    Load-bearing invariant — mirrors retrieval's
    test_parser_resets_citation_buffer_after_each_tool_call.
    """
    out = parse_scoring_response(
        _load_fixture(),
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    if len(out.cells) >= 2:
        cell_a = out.cells[0]
        cell_b = out.cells[1]
        a_cited = {s.cited_text for s in cell_a.provenance}
        b_cited = {s.cited_text for s in cell_b.provenance}
        assert a_cited & b_cited == set(), (
            f"Citation bleed across cells: shared={a_cited & b_cited}"
        )


def test_parser_extracts_unscoreable_cells_from_record_unscoreable_cell_tool_calls():
    """Fixture has 1 record_unscoreable_cell call; output.unscoreable_cells populated."""
    out = parse_scoring_response(
        _load_fixture(),
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    assert len(out.unscoreable_cells) == 1
    u = out.unscoreable_cells[0]
    assert u.confidence in {"high", "medium", "low"}
    assert u.reason


def test_parser_unknown_tool_name_resets_citation_buffer():
    """text_with_citation_A -> unknown tool -> text_with_citation_B -> record_cell

    Cell's provenance should contain only citation B (A flushed by unknown tool).
    """
    span_a = {
        "type": "char_location",
        "cited_text": "BUFFER_A_TEXT",
        "document_index": 0,
        "document_title": "doc",
        "start_char_index": 0,
        "end_char_index": 10,
    }
    span_b = {
        "type": "char_location",
        "cited_text": "BUFFER_B_TEXT",
        "document_index": 0,
        "document_title": "doc",
        "start_char_index": 20,
        "end_char_index": 30,
    }
    message = {
        "content": [
            {"type": "text", "text": "A.", "citations": [span_a]},
            {"type": "tool_use", "id": "t1", "name": "unknown_tool", "input": {}},
            {"type": "text", "text": "B.", "citations": [span_b]},
            {
                "type": "tool_use",
                "id": "t2",
                "name": "record_cell",
                "input": {
                    "row_id": "lobbying_violation_penalties_imposed_in_practice",
                    "axis": "legal",
                    "value": True,
                    "confidence": "high",
                },
            },
        ]
    }
    out = parse_scoring_response(
        message, state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits"
    )
    assert len(out.cells) == 1
    cited = {s.cited_text for s in out.cells[0].provenance}
    assert "BUFFER_A_TEXT" not in cited
    assert "BUFFER_B_TEXT" in cited


def test_parser_unknown_row_id_warns_and_skips(caplog):
    """tool_use record_cell with unknown row_id logs a warning and skips."""
    message = {
        "content": [
            {
                "type": "tool_use",
                "id": "t1",
                "name": "record_cell",
                "input": {
                    "row_id": "nonexistent_row_xyz",
                    "axis": "legal",
                    "value": True,
                    "confidence": "high",
                },
            },
        ]
    }
    with caplog.at_level(logging.WARNING):
        out = parse_scoring_response(
            message,
            state_abbr="OH",
            vintage_year=2015,
            chunk_id="enforcement_and_audits",
        )
    assert out.cells == ()
    assert any("nonexistent_row_xyz" in rec.message for rec in caplog.records)


def test_parser_polymorphic_over_message_object_and_dict():
    """Same fixture as dict and as a SimpleNamespace (attr-access) both parse identically."""
    raw = _load_fixture()
    out_dict = parse_scoring_response(
        raw, state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits"
    )

    # Convert content to attr-accessible objects (citations stay as dicts; the
    # parser's _get handles dict citation entries via _parse_citation).
    def _to_ns(d):
        if isinstance(d, dict):
            return SimpleNamespace(**{k: _to_ns(v) for k, v in d.items()})
        if isinstance(d, list):
            return [_to_ns(x) for x in d]
        return d

    ns = _to_ns(raw)
    out_ns = parse_scoring_response(
        ns, state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits"
    )
    assert len(out_dict.cells) == len(out_ns.cells)
    assert len(out_dict.unscoreable_cells) == len(out_ns.unscoreable_cells)


def test_parser_empty_response_returns_empty_scoring_output():
    out = parse_scoring_response(
        {"content": []},
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
    )
    assert out.cells == ()
    assert out.unscoreable_cells == ()

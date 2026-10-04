"""Tests for scoring_v2 Pydantic models.

Phase 1 (RED): all tests fail with ImportError because the names below
don't yet exist in lobby_analysis.scoring_v2.models.
"""

import pytest
from pydantic import ValidationError

from lobby_analysis.retrieval_v2 import EvidenceSpan
from lobby_analysis.scoring_v2.models import ScoringOutput, UnscoreableCell


def _evidence_span() -> EvidenceSpan:
    return EvidenceSpan(
        citation_type="char_location",
        document_index=0,
        document_title="tiny_statute.txt",
        cited_text="Section 1. The commission shall audit",
        start_char_index=0,
        end_char_index=40,
    )


def test_scoring_output_constructs_with_defaults():
    out = ScoringOutput(state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits")
    assert out.cells == ()
    assert out.unscoreable_cells == ()
    assert out.state_abbr == "OH"
    assert out.vintage_year == 2015
    assert out.chunk_id == "enforcement_and_audits"


def test_scoring_output_is_frozen():
    out = ScoringOutput(state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits")
    with pytest.raises(ValidationError):
        out.state_abbr = "TX"


def test_scoring_output_cells_field_is_tuple_not_list():
    out = ScoringOutput(
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
        cells=[],
    )
    assert isinstance(out.cells, tuple)


def test_scoring_output_unscoreable_cells_field_is_tuple():
    out = ScoringOutput(
        state_abbr="OH",
        vintage_year=2015,
        chunk_id="enforcement_and_audits",
        unscoreable_cells=[],
    )
    assert isinstance(out.unscoreable_cells, tuple)


def test_unscoreable_cell_required_fields():
    """Constructing without confidence raises ValidationError."""
    with pytest.raises(ValidationError):
        UnscoreableCell(cell_id="some_row:legal", reason="silent")


def test_unscoreable_cell_evidence_spans_defaults_to_empty_tuple():
    cell = UnscoreableCell(
        cell_id="some_row:legal",
        reason="statute is silent",
        confidence="high",
    )
    assert cell.evidence_spans == ()
    span = _evidence_span()
    cell_with_spans = UnscoreableCell(
        cell_id="some_row:legal",
        reason="statute is silent",
        confidence="high",
        evidence_spans=(span,),
    )
    assert cell_with_spans.evidence_spans == (span,)


def test_unscoreable_cell_is_frozen():
    cell = UnscoreableCell(
        cell_id="some_row:legal",
        reason="statute is silent",
        confidence="high",
    )
    with pytest.raises(ValidationError):
        cell.reason = "changed"

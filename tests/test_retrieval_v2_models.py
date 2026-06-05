"""Tests for retrieval_v2 Pydantic models.

Phase 1 (RED): all tests fail with ImportError because the names below
don't yet exist in lobby_analysis.retrieval_v2.models.
"""

import pytest
from pydantic import ValidationError

from lobby_analysis.retrieval_v2.models import (
    CrossReference,
    EvidenceSpan,
    RetrievalOutput,
    UnresolvableReference,
)


def _evidence_span() -> EvidenceSpan:
    return EvidenceSpan(
        citation_type="char_location",
        document_index=0,
        document_title="OH ch.101",
        cited_text="as defined in §311.005",
        start_char_index=0,
        end_char_index=20,
    )


def test_evidence_span_constructs_from_char_location_citation_dict():
    span = _evidence_span()
    assert span.citation_type == "char_location"
    assert span.document_index == 0
    assert span.start_char_index == 0
    assert span.end_char_index == 20


def test_cross_reference_pydantic_model_round_trips():
    span = _evidence_span()
    ref = CrossReference(
        section_reference="§311.005",
        chunk_ids_affected=("lobbying_definitions",),
        relevance="Defines 'person'",
        justia_url="https://example.com/x.html",
        url_confidence="medium",
        url_confidence_reason="title inferred",
        evidence_spans=(span,),
    )
    rebuilt = CrossReference(**ref.model_dump())
    assert rebuilt == ref


def test_cross_reference_evidence_spans_is_list():
    """evidence_spans is a tuple sequence (not Optional)."""
    ref = CrossReference(
        section_reference="§1",
        chunk_ids_affected=("lobbying_definitions",),
        relevance="...",
        justia_url="https://example.com",
        url_confidence="high",
    )
    assert isinstance(ref.evidence_spans, tuple)


def test_cross_reference_evidence_spans_can_be_empty():
    """Empty is valid — citations may be absent on some tool calls."""
    ref = CrossReference(
        section_reference="§1",
        chunk_ids_affected=("lobbying_definitions",),
        relevance="...",
        justia_url="https://example.com",
        url_confidence="high",
    )
    assert ref.evidence_spans == ()


def test_unresolvable_reference_pydantic_model():
    span = _evidence_span()
    ref = UnresolvableReference(
        reference_text="as defined by applicable law",
        referenced_from="sections/title1-101_72.txt",
        reason="No section number cited",
        evidence_spans=(span,),
    )
    assert ref.reference_text == "as defined by applicable law"
    assert ref.referenced_from == "sections/title1-101_72.txt"
    assert ref.reason == "No section number cited"
    assert len(ref.evidence_spans) == 1


def test_retrieval_output_collects_both_kinds():
    span = _evidence_span()
    xref = CrossReference(
        section_reference="§1",
        chunk_ids_affected=("lobbying_definitions",),
        relevance="...",
        justia_url="https://example.com",
        url_confidence="high",
        evidence_spans=(span,),
    )
    unr = UnresolvableReference(
        reference_text="as defined by applicable law",
        referenced_from="x.txt",
        reason="No section number cited",
    )
    out = RetrievalOutput(
        state_abbr="OH",
        vintage_year=2010,
        hop=1,
        cross_references=(xref,),
        unresolvable_references=(unr,),
    )
    assert out.state_abbr == "OH"
    assert out.vintage_year == 2010
    assert len(out.cross_references) == 1
    assert len(out.unresolvable_references) == 1


def test_retrieval_output_validates_hop_in_range():
    """hop must be 1 or 2 (two-hop limit from v1)."""
    with pytest.raises(ValidationError):
        RetrievalOutput(state_abbr="OH", vintage_year=2010, hop=3)
    with pytest.raises(ValidationError):
        RetrievalOutput(state_abbr="OH", vintage_year=2010, hop=0)

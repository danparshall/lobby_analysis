"""Tests for `lobby_analysis.models_v2.provenance.EvidenceSpan`.

Targets behavior described in the v2 Pydantic cell models implementation plan
(`docs/active/extraction-harness-brainstorm/plans/20260514_v2_pydantic_cell_models_implementation_plan.md`)
Phase 1:

    Fields: section_reference: str (required), artifact_path: str | None,
    quoted_span: str | None (max-length 200), url: str | None.

These tests target our row-semantic rules — NOT pydantic's framework behavior.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError


def test_evidence_span_with_only_required_field_validates():
    """A minimal EvidenceSpan needs only section_reference."""
    from lobby_analysis.models_v2.provenance import EvidenceSpan

    span = EvidenceSpan(section_reference="§101.70(B)(1)")
    assert span.section_reference == "§101.70(B)(1)"
    assert span.artifact_path is None
    assert span.quoted_span is None
    assert span.url is None


def test_evidence_span_with_all_fields_validates():
    """EvidenceSpan should accept and round-trip every optional field."""
    from lobby_analysis.models_v2.provenance import EvidenceSpan

    span = EvidenceSpan(
        section_reference="§101.70(B)(1)",
        artifact_path="papers/text/OH_2025.txt",
        quoted_span="An expenditure exceeding $200 per calendar quarter triggers registration.",
        url="https://codes.ohio.gov/ohio-revised-code/section-101.70",
    )
    assert span.section_reference == "§101.70(B)(1)"
    assert span.artifact_path == "papers/text/OH_2025.txt"
    assert span.quoted_span.startswith("An expenditure")
    assert span.url is not None and span.url.startswith("https://")


def test_evidence_span_rejects_quoted_span_over_max_length():
    """quoted_span has a 200-char ceiling — anything longer is a validation error.

    This is OUR semantic rule (preventing unbounded extraction), not pydantic
    framework behavior, so testing it is in scope per the plan's Testing Plan.
    """
    from lobby_analysis.models_v2.provenance import EvidenceSpan

    too_long = "x" * 201  # exceeds the 200-char limit by one
    with pytest.raises(ValidationError):
        EvidenceSpan(section_reference="§1", quoted_span=too_long)


def test_evidence_span_accepts_quoted_span_at_max_length():
    """Exactly 200 chars is the boundary — this MUST validate."""
    from lobby_analysis.models_v2.provenance import EvidenceSpan

    at_limit = "x" * 200
    span = EvidenceSpan(section_reference="§1", quoted_span=at_limit)
    assert span.quoted_span is not None
    assert len(span.quoted_span) == 200

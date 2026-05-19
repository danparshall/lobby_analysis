"""Typed output models for the v2 retrieval agent.

Hierarchy:

- :class:`EvidenceSpan` — one citation emitted by the Anthropic Citations API.
  Re-exported from :mod:`lobby_analysis.models_v2.citations` (where it lives so
  both cells and cross-references can import it without cycling through
  ``retrieval_v2/__init__.py``). Existing call sites importing from
  ``retrieval_v2`` or ``retrieval_v2.models`` continue to work.
- :class:`CrossReference` — one tool-call worth of cross-reference data plus
  the citation spans the agent emitted in the preceding text (machine-verified
  provenance per the Citations API's text↔citation attachment).
- :class:`UnresolvableReference` — same pattern, for references the agent
  cannot resolve to a section number.
- :class:`RetrievalOutput` — the parsed result of a single retrieval call,
  scoped to (state, vintage, hop).

All models are ``frozen=True``: a parsed retrieval output should be immutable
once produced. Sequence fields use tuples (not lists) for the same reason.
"""

from typing import Literal

from pydantic import BaseModel, Field

from lobby_analysis.models_v2.citations import CitationType, EvidenceSpan

__all__ = [
    "CitationType",
    "CrossReference",
    "EvidenceSpan",
    "RetrievalOutput",
    "UnresolvableReference",
]


class CrossReference(BaseModel):
    """A resolvable cross-reference the agent identified, with citation provenance."""

    model_config = {"frozen": True}

    section_reference: str
    chunk_ids_affected: tuple[str, ...]
    relevance: str
    justia_url: str
    url_confidence: Literal["high", "medium", "low"]
    url_confidence_reason: str = ""
    evidence_spans: tuple[EvidenceSpan, ...] = ()


class UnresolvableReference(BaseModel):
    """A reference the agent found but could not resolve to a section number."""

    model_config = {"frozen": True}

    reference_text: str
    referenced_from: str
    reason: str
    evidence_spans: tuple[EvidenceSpan, ...] = ()


class RetrievalOutput(BaseModel):
    """Parsed output of a single retrieval call, scoped to (state, vintage, hop)."""

    model_config = {"frozen": True}

    state_abbr: str
    vintage_year: int
    hop: int = Field(ge=1, le=2)
    cross_references: tuple[CrossReference, ...] = ()
    unresolvable_references: tuple[UnresolvableReference, ...] = ()

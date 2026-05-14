"""Typed output models for the v2 retrieval agent.

Hierarchy:

- :class:`EvidenceSpan` — one citation emitted by the Anthropic Citations API.
  Wraps any of the three documented citation types (``char_location`` for
  plain-text documents, ``page_location`` for PDFs, ``content_block_location``
  for custom content blocks). Citation-type-specific fields default to None
  so the same dataclass shape handles all three.
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

CitationType = Literal["char_location", "page_location", "content_block_location"]


class EvidenceSpan(BaseModel):
    """A single citation span emitted by the Anthropic Citations API."""

    model_config = {"frozen": True}

    citation_type: CitationType
    document_index: int
    cited_text: str
    document_title: str | None = None

    # char_location (plain text source documents)
    start_char_index: int | None = None
    end_char_index: int | None = None

    # page_location (PDF source documents)
    start_page_number: int | None = None
    end_page_number: int | None = None

    # content_block_location (custom content blocks)
    start_block_index: int | None = None
    end_block_index: int | None = None


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

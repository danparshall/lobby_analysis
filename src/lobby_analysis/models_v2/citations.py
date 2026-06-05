"""Citations-API span primitive used by both `models_v2` and `retrieval_v2`.

`EvidenceSpan` wraps any of the three documented Anthropic Citations API
citation types (``char_location`` for plain-text documents, ``page_location``
for PDFs, ``content_block_location`` for custom content blocks). It is
foundational provenance — used by `CompendiumCell.provenance` (cells) and by
`CrossReference.evidence_spans` / `UnresolvableReference.evidence_spans`
(retrieval cross-references) — so it lives at the bottom of the import graph,
in `models_v2`, not inside `retrieval_v2/`.

Located here (not in `retrieval_v2`) because importing it from `retrieval_v2`
triggers the full retrieval-agent module (brief_writer, parser, tools), which
in turn imports `chunks_v2.build_chunks` — closing a cycle through
`models_v2.cells` and breaking cold-load. Keeping the type definition
upstream of `retrieval_v2` dissolves that cycle structurally.

`retrieval_v2.models` re-exports `EvidenceSpan` from here for backward
compatibility — existing call sites like
``from lobby_analysis.retrieval_v2 import EvidenceSpan`` continue to work.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

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

"""Provenance citation pointer for extracted compendium cells.

`EvidenceSpan` is the citation attached to a `CompendiumCell.provenance` so
downstream consumers can trace each extracted value back to its source
statute section.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSpan(BaseModel):
    """A pointer to the statute span that produced a cell's value.

    `section_reference` is the only required field — e.g. "§101.70(B)(1)" —
    so any cell that records provenance must at minimum name the section it
    came from. Quoted spans are bounded at 200 chars to prevent unbounded
    extraction copy-out.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    section_reference: str
    artifact_path: str | None = None
    quoted_span: str | None = Field(default=None, max_length=200)
    url: str | None = None

"""Field-level extraction provenance."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ExtractionMethod = Literal[
    "direct_copy", "regex", "llm", "inferred", "human_corrected"
]


class Provenance(BaseModel):
    """Tracks how a field or sub-entity was extracted from source data.

    Attach to any value populated by LLM extraction, regex, or inference.
    Direct-copy structured fields use filing-level provenance only.
    """

    source_url: str | None = None
    source_document: str | None = None
    extraction_method: ExtractionMethod
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="[0, 1] for non-direct extractions; null for direct_copy",
    )
    model_version: str | None = None
    prompt_version: str | None = None
    extracted_at: datetime | None = None
    text_span: str | None = Field(
        default=None,
        description="Source text used as basis for extraction (LLM/regex auditability)",
    )

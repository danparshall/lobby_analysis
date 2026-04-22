"""Per-state extraction pipeline capability.

Companion to StateMasterRecord: SMR captures what the state's law requires;
ExtractionCapability captures what the pipeline can actually observe.
Together they resolve matrix cells to (required, available) pairs.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PortalTier = Literal[
    "clean_bulk_api",
    "structured_search",
    "html_search",
    "pdf_only",
    "paper_on_request",
    "mixed",
]

PipelineCadence = Literal[
    "monthly",
    "quarterly",
    "semi_annual",
    "annual",
    "on_change",
    "ad_hoc",
]


class ExtractionCapability(BaseModel):
    """What this state's extraction pipeline can and cannot do.

    One per state. Populated by the fellow owning that state. Feeds into
    the matrix export's practical_availability column.
    """

    state: str = Field(description="Two-letter abbreviation")
    portal_tier: PortalTier
    fields_extractable: list[str] = Field(
        default_factory=list,
        description="Dot-paths into LobbyingFiling/LobbyistRegistration we can reliably populate",
    )
    fields_unextractable: list[str] = Field(
        default_factory=list,
        description="Dot-paths required by state but blocked by portal",
    )
    known_limitations: list[str] = Field(
        default_factory=list,
        description="Free-text descriptions of pipeline gaps",
    )
    last_pipeline_run: datetime | None = None
    next_expected_run: datetime | None = None
    cadence: PipelineCadence | None = None
    parse_error_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of filings where extraction failed outright",
    )
    notes: str = ""

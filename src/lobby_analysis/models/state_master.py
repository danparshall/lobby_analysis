"""State Master Record — per-state field requirements and reporting topology.

Captures what each state's disclosure law requires, derived from the compendium
of external rubrics (PRI, FOCAL, Hired Guns, Newmark, Opheim, Sunlight,
OpenSecrets, LDA). Enables compliance monitoring: 'this filer omitted a field
that their state requires.'
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FieldStatus = Literal["required", "optional", "not_applicable", "unknown"]
FilingStatus = Literal["required", "optional", "not_required"]
ReportingFrequency = Literal[
    "monthly",
    "quarterly",
    "tri_annually",
    "semi_annually",
    "annually",
    "session_based",
    "other",
]

LegalAvailability = Literal[
    "public",
    "redacted",
    "access_restricted",
    "paper_on_request",
    "unknown",
]

PracticalAvailability = Literal[
    "structured_bulk",
    "structured_search",
    "html_search",
    "pdf_only",
    "not_available",
    "unknown",
]

EvidenceSource = Literal[
    "statute_verified",
    "database_inferred",
    "both",
    "fellow_judgment",
    "unknown",
]

FrameworkId = Literal[
    "pri_2010_disclosure",
    "pri_2010_accessibility",
    "focal_2024",
    "focal_2026",
    "hired_guns_2007",
    "newmark_2005",
    "newmark_2017",
    "opheim_1991",
    "sunlight_2015",
    "opensecrets_2022",
    "lda",
    "other",
]


class FrameworkReference(BaseModel):
    """A citation to an item in an external rubric/framework."""

    framework: FrameworkId
    item_id: str
    item_text: str | None = None


class RegistrationRequirement(BaseModel):
    """Whether a particular role must register as a lobbyist in this state."""

    model_config = ConfigDict(extra="forbid")

    role: Literal[
        "lobbyist",
        "volunteer_lobbyist",
        "principal",
        "lobbying_firm",
        "governors_office",
        "executive_agency",
        "legislative_branch",
        "independent_agency",
        "local_government",
        "government_lobbying_government",
        "other_public_entity",
    ]
    required: bool
    framework_references: list[FrameworkReference] = Field(default_factory=list)
    legal_citation: str | None = None
    notes: str = ""


class ReportingPartyRequirement(BaseModel):
    """What a particular filer role must file, and how often.

    Enables cross-reporting consistency checks: if a state requires both
    lobbyists and clients to file activity reports, a missing client report
    is detectable even before examining field-level completeness.
    """

    model_config = ConfigDict(extra="forbid")

    entity_role: Literal["lobbyist", "client", "firm", "official"]
    report_type: Literal[
        "activity_report",
        "expenditure_report",
        "gift_disclosure",
        "registration",
        "other",
    ]
    filing_status: FilingStatus
    reporting_frequency: ReportingFrequency | None = None
    framework_references: list[FrameworkReference] = Field(default_factory=list)
    notes: str = ""


class FieldRequirement(BaseModel):
    """Whether a specific data field is required for a given filer role.

    The field_path uses dot notation into the LobbyingFiling model,
    e.g. 'total_compensation', 'expenditures[].amount',
    'positions[].bill_reference'.
    """

    model_config = ConfigDict(extra="forbid")

    field_path: str
    reporting_party: Literal["lobbyist", "client", "firm", "all"]
    status: FieldStatus
    legal_availability: LegalAvailability = "unknown"
    practical_availability: PracticalAvailability = "unknown"
    evidence_source: EvidenceSource = "unknown"
    evidence_notes: str = ""
    framework_references: list[FrameworkReference] = Field(default_factory=list)
    legal_citation: str | None = None
    notes: str = ""


class StateMasterRecord(BaseModel):
    """Per-state metadata defining disclosure requirements.

    One per state. Captures what the state's law requires so that
    downstream compliance checks can distinguish 'state doesn't require
    this field' from 'filer failed to report a required field.'

    Population strategy: auto-generated from compendium scoring results,
    then manually verified by the fellow assigned to that state.
    """

    state: str = Field(description="Two-letter abbreviation")
    state_name: str
    version: str = Field(
        description=(
            "Version identifier for this record (e.g., '2026-Q1'). "
            "Bump when state law changes disclosure requirements."
        ),
    )
    effective_start: date = Field(
        description="Date these requirements took effect",
    )
    effective_end: date | None = Field(
        default=None,
        description="Date these requirements were superseded; null if current",
    )
    last_updated: date

    legal_citations: list[str] = Field(
        default_factory=list,
        description="Primary statute references for lobbying disclosure",
    )

    registration_requirements: list[RegistrationRequirement] = Field(
        default_factory=list
    )

    de_minimis_financial_threshold: float | None = Field(
        default=None,
        description="Dollar amount below which registration is exempt",
    )
    de_minimis_financial_citation: str | None = None
    de_minimis_time_threshold: float | None = Field(
        default=None,
        description="Percentage of compensated time below which exempt",
    )
    de_minimis_time_citation: str | None = None

    reporting_parties: list[ReportingPartyRequirement] = Field(
        default_factory=list
    )

    field_requirements: list[FieldRequirement] = Field(default_factory=list)

    notes: str = ""

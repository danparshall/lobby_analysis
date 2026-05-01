"""Compendium items and matrix cells.

The compendium is the union of field-level questions across all frameworks
(PRI, FOCAL, Hired Guns, Newmark, Opheim, Sunlight, OpenSecrets, LDA).
Each CompendiumItem is the N in the N x 50 x 2 matrix; each MatrixCell is
the projected value for a (compendium item, state) pair.
"""

from typing import Literal

from pydantic import BaseModel, Field

from lobby_analysis.models.state_master import (
    EvidenceSource,
    FieldStatus,
    FrameworkReference,
    LegalAvailability,
    PracticalAvailability,
)

CompendiumDomain = Literal[
    "definitions",
    "registration",
    "reporting",
    "financial",
    "contact_log",
    "relationship",
    "gift",
    "revolving_door",
    "accessibility",
    "enforcement",
    "other",
]

CompendiumDataType = Literal[
    "boolean",
    "numeric",
    "categorical",
    "free_text",
    "compound",
]


class CompendiumItem(BaseModel):
    """A universal field/question in the disclosure-regime universe.

    Compendium items union across rubric frameworks. Each item may trace back
    to zero, one, or many framework items.
    """

    id: str = Field(
        description="Stable compendium-native ID (e.g., 'C_LOBBYIST_COMPENSATION')"
    )
    name: str
    description: str
    domain: CompendiumDomain
    data_type: CompendiumDataType
    framework_references: list[FrameworkReference] = Field(default_factory=list)
    maps_to_state_master_field: str | None = Field(
        default=None,
        description="Dot-path into StateMasterRecord.field_requirements[].field_path",
    )
    maps_to_filing_field: str | None = Field(
        default=None,
        description="Dot-path into LobbyingFiling (e.g., 'total_compensation')",
    )
    observable_from_database: bool = Field(
        default=False,
        description=(
            "True if this item's required-status can be inferred from "
            "observing filings; False if it requires statute reading."
        ),
    )
    notes: str = ""


class MatrixCell(BaseModel):
    """One projected row of the N x 50 x 2 matrix output.

    Denormalizes the join (StateMasterRecord, CompendiumItem) for export.
    Generated from SMR + compendium, typically by an export/projection
    function rather than stored directly.
    """

    state: str
    compendium_item_id: str
    required: FieldStatus
    legal_availability: LegalAvailability
    practical_availability: PracticalAvailability
    evidence_source: EvidenceSource
    framework_references: list[FrameworkReference] = Field(default_factory=list)
    notes: str = ""

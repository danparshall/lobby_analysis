"""Reference entities: Person, Organization, BillReference.

Person and Organization follow Popolo (OCDEP 5).
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ContactDetail(BaseModel):
    """A contact method for a person or organization."""

    type: Literal["address", "phone", "email", "website"]
    value: str
    note: str = ""


class Identifier(BaseModel):
    """An external identifier linking to another system.

    Scheme examples: "open_states", "lobbyview", "state_registration",
    "opencorporates", "sec_cik", "ein".
    """

    scheme: str
    identifier: str


class PriorOffice(BaseModel):
    """A public office previously held by a lobbyist (revolving door, FOCAL 5.1)."""

    office: str
    institution: str = ""
    start_date: date | None = None
    end_date: date | None = None


class Person(BaseModel):
    """An individual — lobbyist, official, or other natural person.

    Follows Popolo: single display name, no first/middle/last segmentation.
    """

    id: str
    name: str = Field(description="Display-ready name (e.g., 'Jane Q. Doe')")
    name_components: dict[str, str] | None = Field(
        default=None,
        description=(
            "Original name components if the source provided them separately. "
            "Keys are labeled (e.g., {'first': 'Jane', 'middle': 'Q.', 'last': 'Doe'}). "
            "Null if the source provided a single name string."
        ),
    )
    contact_details: list[ContactDetail] = Field(default_factory=list)
    identifiers: list[Identifier] = Field(default_factory=list)
    prior_public_offices: list[PriorOffice] = Field(default_factory=list)
    source_state: str = Field(
        description="Two-letter state abbreviation where this record originates"
    )


class Organization(BaseModel):
    """A company, interest group, government body, lobbying firm, or other entity.

    Follows Popolo (OCDEP 5).
    """

    id: str
    name: str = Field(description="Legal name as filed")
    classification: str | None = Field(
        default=None,
        description=(
            "company, nonprofit, trade_association, lobbying_firm, "
            "government_agency, other"
        ),
    )
    contact_details: list[ContactDetail] = Field(default_factory=list)
    identifiers: list[Identifier] = Field(default_factory=list)
    sector: str | None = Field(default=None, description="Industry sector (FOCAL 4.5)")
    legal_form: str | None = Field(
        default=None,
        description="Public/private/nonprofit/NGO (FOCAL 4.3)",
    )
    source_state: str = Field(
        description="Two-letter state abbreviation where this record originates"
    )


class OrganizationRelationship(BaseModel):
    """A typed, time-bounded relationship between two organizations.

    Handles corporate hierarchies that Popolo can't represent
    (OCDEP 5 has no org-org memberships).
    """

    subject_org_id: str = Field(description="The child/member organization")
    object_org_id: str = Field(description="The parent/association organization")
    relationship_type: Literal[
        "subsidiary_of", "member_of", "subcontracts_to", "affiliate_of"
    ]
    start_date: date | None = None
    end_date: date | None = None
    source: str | None = Field(
        default=None, description="Where this relationship was disclosed"
    )


class BillReference(BaseModel):
    """A reference to legislation from a lobbying filing.

    Resolved references link to Open States canonical IDs.
    Unresolved references preserve the original text for later matching.
    """

    open_states_id: str | None = Field(
        default=None, description="Canonical Open States ID, null if unresolved"
    )
    original_text: str = Field(description="Bill reference as written in the filing")
    session: str | None = None
    chamber: str | None = None
    bill_number: str | None = None
    reference_type: Literal[
        "bill", "resolution", "regulation", "executive_order", "budget", "other"
    ] = "bill"
    is_resolved: bool = False
    inferred_from_range_expansion: bool = Field(
        default=False,
        description='True if expanded from a range like "HB 101-105"',
    )

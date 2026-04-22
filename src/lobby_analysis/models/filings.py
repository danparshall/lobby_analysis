"""Filing entities: LobbyistRegistration, LobbyingFiling, and sub-entities.

Follows Epton's Filing -> Sections -> Transactions pattern.
Amendment handling via filing_action + supersedes + is_current.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from lobby_analysis.models.entities import (
    BillReference,
    Organization,
    Person,
)
from lobby_analysis.models.provenance import Provenance


# ---------------------------------------------------------------------------
# Sub-entities (nested inside LobbyingFiling)
# ---------------------------------------------------------------------------


class LobbyingPosition(BaseModel):
    """A filer's stated position on a bill or issue during a reporting period."""

    bill_reference: BillReference | None = None
    position: Literal[
        "support", "oppose", "amend", "monitor", "engage", "mention"
    ] | None = None
    general_issue_area: str | None = Field(
        default=None, description="Broad topic (PRI E1g_i/E2g_i; FOCAL 8.9)"
    )
    description: str | None = None
    outcomes_sought: str | None = Field(
        default=None, description="What the filer wants (FOCAL 8.10)"
    )
    provenance: Provenance | None = None


class LobbyingExpenditure(BaseModel):
    """An itemized expenditure line from a filing."""

    category: Literal[
        "compensation",
        "reimbursement",
        "entertainment",
        "travel",
        "lodging",
        "gift",
        "campaign_contribution",
        "membership_sponsorship",
        "other",
    ]
    amount: float | None = None
    currency: str = "USD"
    recipient_name: str | None = None
    recipient_role: str | None = Field(
        default=None, description="official, agency, vendor, lobbyist, other"
    )
    purpose: str | None = None
    expenditure_date: date | None = None
    issue_area: str | None = Field(
        default=None, description="Expenditure per issue (FOCAL 7.8)"
    )
    provenance: Provenance | None = None


class LobbyingEngagement(BaseModel):
    """A specific act of lobbying — meeting, call, written communication.

    Most states do NOT require contact-level logging. This entity is relevant
    only for the subset that do (FOCAL category 8).
    """

    official_contacted: str | None = Field(
        default=None, description="Name (FOCAL 8.2)"
    )
    official_role: str | None = None
    institution: str | None = Field(
        default=None, description="Agency/department (FOCAL 8.3)"
    )
    contact_date: date | None = None
    form_of_contact: Literal[
        "in_person", "phone", "email", "video", "written", "event", "other"
    ] | None = Field(default=None, description="FOCAL 8.6")
    location: str | None = Field(default=None, description="FOCAL 8.7")
    attendees: list[str] = Field(
        default_factory=list, description="Names of all attendees (FOCAL 8.4)"
    )
    topics: list[str] = Field(default_factory=list, description="FOCAL 8.9")
    materials_shared: list[str] = Field(
        default_factory=list, description="FOCAL 8.8"
    )
    outcomes_sought: list[str] = Field(
        default_factory=list, description="FOCAL 8.10"
    )
    bill_references: list[BillReference] = Field(
        default_factory=list, description="FOCAL 8.11"
    )
    beneficiary_org: str | None = Field(
        default=None,
        description="Organization/interest represented (FOCAL 8.1)",
    )
    provenance: Provenance | None = None


class Gift(BaseModel):
    """A gift, meal, travel, or entertainment provided to a public official."""

    recipient_name: str
    recipient_role: str | None = None
    recipient_institution: str | None = None
    donor_name: str | None = None
    value: float | None = None
    description: str | None = None
    gift_date: date | None = None
    gift_type: Literal[
        "meal", "travel", "lodging", "entertainment", "event_ticket", "other"
    ] | None = None
    provenance: Provenance | None = None


# ---------------------------------------------------------------------------
# Top-level filing entities
# ---------------------------------------------------------------------------


class LobbyistRegistration(BaseModel):
    """The legal predicate: 'I am registered to lobby in state X.'

    Separate from periodic activity reports. Creates the legal basis
    for subsequent LobbyingFiling records.
    """

    id: str
    state: str = Field(description="Two-letter abbreviation")
    registration_id: str | None = Field(
        default=None, description="State's native registration ID"
    )
    lobbyist: Person
    employer: Organization | None = Field(
        default=None, description="Firm or in-house employer"
    )
    clients: list[Organization] = Field(
        default_factory=list, description="Principals/clients represented (FOCAL 6.1)"
    )
    lobbyist_type: Literal[
        "professional", "in_house_company", "in_house_org", "volunteer"
    ] | None = Field(default=None, description="FOCAL 1.1")
    contract_type: Literal["salaried", "contracted"] | None = Field(
        default=None, description="FOCAL 4.6"
    )
    compensation_type: Literal["compensated", "uncompensated"] | None = Field(
        default=None, description="FOCAL 7.7"
    )
    registration_date: date | None = None
    termination_date: date | None = None
    effective_period_start: date | None = None
    effective_period_end: date | None = None
    status: Literal["active", "terminated", "suspended", "expired"]
    general_issue_areas: list[str] = Field(
        default_factory=list,
        description="Broad subject areas registered to lobby on",
    )
    source_url: str | None = None
    source_document: str | None = None
    provenance: Provenance | None = None


class LobbyingFiling(BaseModel):
    """A periodic activity report — the main filing document.

    Contains financial totals and nested sub-entities for positions,
    expenditures, engagements, and gifts. Each amendment is a new
    LobbyingFiling with a supersedes link (Epton pattern).
    """

    id: str
    state: str = Field(description="Two-letter abbreviation")
    filing_id: str | None = Field(
        default=None, description="State's native filing ID"
    )
    filing_type: Literal[
        "activity_report",
        "expenditure_report",
        "gift_disclosure",
        "supplemental",
        "other",
    ]
    filer_person: Person | None = Field(
        default=None, description="Set if the filer is a natural person"
    )
    filer_organization: Organization | None = Field(
        default=None, description="Set if the filer is an organization"
    )
    filer_role: Literal["lobbyist", "client", "firm"]

    # Reporting period
    reporting_period_start: date | None = None
    reporting_period_end: date | None = None
    filed_date: date | None = None

    # Amendment handling (Epton pattern)
    is_current: bool = Field(
        default=True, description="True if this is the latest version"
    )
    supersedes: str | None = Field(
        default=None, description="filing_id of the prior version"
    )
    filing_action: Literal[
        "original", "amendment", "termination", "withdrawal"
    ] = "original"

    # Financial totals
    total_compensation: float | None = Field(
        default=None, description="Direct lobbying costs (PRI E1f_i/E2f_i)"
    )
    total_reimbursements: float | None = Field(
        default=None, description="Indirect costs (PRI E1f_ii/E2f_ii)"
    )
    total_other_costs: float | None = Field(
        default=None,
        description="Gifts/entertainment/travel/lodging (PRI E1f_iii/E2f_iii)",
    )
    total_expenditure: float | None = Field(
        default=None, description="Aggregate expenditure (FOCAL 7.6)"
    )
    total_income: float | None = Field(
        default=None,
        description="For consultant lobbyists/firms (FOCAL 7.1)",
    )
    income_per_client: dict[str, float] | None = Field(
        default=None,
        description="Client name or ID -> amount (FOCAL 7.2)",
    )
    is_itemized: bool | None = Field(
        default=None,
        description="Whether financials are itemized vs. lump-sum (PRI E1f_iv)",
    )

    # Nested sub-entities
    positions: list[LobbyingPosition] = Field(default_factory=list)
    expenditures: list[LobbyingExpenditure] = Field(default_factory=list)
    engagements: list[LobbyingEngagement] = Field(default_factory=list)
    gifts: list[Gift] = Field(default_factory=list)

    # Source
    source_url: str | None = None
    source_document: str | None = None
    provenance: Provenance | None = None
    raw_text: str | None = Field(
        default=None, description="Full text of the filing for auditability"
    )

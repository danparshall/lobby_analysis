"""Smoke tests for the lobbying data model.

Validates that models instantiate, serialize to JSON, and round-trip cleanly.
"""

from datetime import date

from lobby_analysis.models import (
    BillReference,
    ContactDetail,
    FieldRequirement,
    Gift,
    Identifier,
    LobbyingEngagement,
    LobbyingExpenditure,
    LobbyingFiling,
    LobbyingPosition,
    LobbyistRegistration,
    Organization,
    OrganizationRelationship,
    Person,
    PriorOffice,
    Provenance,
    RegistrationRequirement,
    ReportingPartyRequirement,
    StateMasterRecord,
)


def _make_person(**overrides) -> Person:
    defaults = {"id": "p-001", "name": "Jane Doe", "source_state": "CA"}
    return Person(**{**defaults, **overrides})


def _make_org(**overrides) -> Organization:
    defaults = {"id": "o-001", "name": "Acme Corp", "source_state": "CA"}
    return Organization(**{**defaults, **overrides})


class TestPerson:
    def test_minimal(self):
        p = _make_person()
        assert p.name == "Jane Doe"
        assert p.contact_details == []
        assert p.prior_public_offices == []

    def test_with_contact_and_identifiers(self):
        p = _make_person(
            contact_details=[
                ContactDetail(type="email", value="jane@example.com"),
                ContactDetail(type="phone", value="555-0100"),
            ],
            identifiers=[
                Identifier(scheme="open_states", identifier="ocd-person/abc123"),
            ],
            prior_public_offices=[
                PriorOffice(
                    office="State Senator",
                    institution="California State Senate",
                    end_date=date(2020, 1, 15),
                ),
            ],
        )
        assert len(p.contact_details) == 2
        assert p.identifiers[0].scheme == "open_states"
        assert p.prior_public_offices[0].office == "State Senator"

    def test_json_round_trip(self):
        p = _make_person()
        json_str = p.model_dump_json()
        p2 = Person.model_validate_json(json_str)
        assert p == p2


class TestOrganization:
    def test_minimal(self):
        o = _make_org()
        assert o.name == "Acme Corp"

    def test_with_classification(self):
        o = _make_org(
            classification="lobbying_firm",
            sector="energy",
            legal_form="private",
        )
        assert o.classification == "lobbying_firm"

    def test_json_round_trip(self):
        o = _make_org()
        json_str = o.model_dump_json()
        o2 = Organization.model_validate_json(json_str)
        assert o == o2


class TestOrganizationRelationship:
    def test_subsidiary(self):
        rel = OrganizationRelationship(
            subject_org_id="o-002",
            object_org_id="o-001",
            relationship_type="subsidiary_of",
            start_date=date(2015, 6, 1),
        )
        assert rel.relationship_type == "subsidiary_of"


class TestBillReference:
    def test_resolved(self):
        ref = BillReference(
            open_states_id="ocd-bill/abc123",
            original_text="HB 1249",
            session="2025-2026",
            chamber="lower",
            bill_number="HB 1249",
            is_resolved=True,
        )
        assert ref.is_resolved

    def test_unresolved(self):
        ref = BillReference(
            original_text="Senate Resolution on AI Safety",
            reference_type="resolution",
            is_resolved=False,
        )
        assert not ref.is_resolved
        assert ref.open_states_id is None


class TestProvenance:
    def test_llm_extraction(self):
        prov = Provenance(
            source_url="https://example.com/filing/123",
            extraction_method="llm",
            confidence=0.92,
            model_version="claude-sonnet-4-6",
            text_span="Total compensation: $45,000",
        )
        assert prov.confidence == 0.92

    def test_direct_copy_null_confidence(self):
        prov = Provenance(
            extraction_method="direct_copy",
            confidence=None,
        )
        assert prov.confidence is None


class TestLobbyistRegistration:
    def test_minimal(self):
        reg = LobbyistRegistration(
            id="r-001",
            state="CA",
            lobbyist=_make_person(),
            status="active",
        )
        assert reg.state == "CA"
        assert reg.clients == []

    def test_with_clients(self):
        reg = LobbyistRegistration(
            id="r-001",
            state="CA",
            lobbyist=_make_person(),
            employer=_make_org(id="o-firm", name="K Street Partners"),
            clients=[
                _make_org(id="o-c1", name="Pfizer Inc."),
                _make_org(id="o-c2", name="PhRMA"),
            ],
            lobbyist_type="professional",
            contract_type="contracted",
            status="active",
            registration_date=date(2025, 1, 15),
        )
        assert len(reg.clients) == 2
        assert reg.lobbyist_type == "professional"

    def test_json_round_trip(self):
        reg = LobbyistRegistration(
            id="r-001",
            state="CA",
            lobbyist=_make_person(),
            status="active",
        )
        json_str = reg.model_dump_json()
        reg2 = LobbyistRegistration.model_validate_json(json_str)
        assert reg == reg2


class TestLobbyingFiling:
    def test_minimal(self):
        filing = LobbyingFiling(
            id="f-001",
            state="CA",
            filing_type="activity_report",
            filer_person=_make_person(),
            filer_role="lobbyist",
        )
        assert filing.is_current is True
        assert filing.filing_action == "original"
        assert filing.positions == []

    def test_full_filing(self):
        filing = LobbyingFiling(
            id="f-001",
            state="CO",
            filing_id="CO-2025-Q1-12345",
            filing_type="activity_report",
            filer_person=_make_person(source_state="CO"),
            filer_role="lobbyist",
            reporting_period_start=date(2025, 1, 1),
            reporting_period_end=date(2025, 3, 31),
            filed_date=date(2025, 4, 15),
            total_compensation=45000.00,
            total_expenditure=52000.00,
            is_itemized=True,
            positions=[
                LobbyingPosition(
                    bill_reference=BillReference(
                        original_text="HB 25-1234",
                        bill_number="HB 25-1234",
                        is_resolved=False,
                    ),
                    position="support",
                    general_issue_area="energy",
                    description="Support clean energy tax credits",
                ),
            ],
            expenditures=[
                LobbyingExpenditure(
                    category="entertainment",
                    amount=250.00,
                    recipient_name="Sen. Smith",
                    recipient_role="official",
                    purpose="Working dinner",
                    expenditure_date=date(2025, 2, 10),
                ),
            ],
            gifts=[
                Gift(
                    recipient_name="Rep. Johnson",
                    value=75.00,
                    description="Event tickets",
                    gift_type="event_ticket",
                ),
            ],
        )
        assert len(filing.positions) == 1
        assert filing.positions[0].position == "support"
        assert len(filing.expenditures) == 1
        assert filing.expenditures[0].amount == 250.00
        assert len(filing.gifts) == 1

    def test_amendment_chain(self):
        original = LobbyingFiling(
            id="f-001",
            state="CA",
            filing_id="CA-2025-001",
            filing_type="activity_report",
            filer_person=_make_person(),
            filer_role="lobbyist",
            is_current=False,
            filing_action="original",
        )
        amendment = LobbyingFiling(
            id="f-002",
            state="CA",
            filing_id="CA-2025-001-A",
            filing_type="activity_report",
            filer_person=_make_person(),
            filer_role="lobbyist",
            is_current=True,
            supersedes="CA-2025-001",
            filing_action="amendment",
        )
        assert not original.is_current
        assert amendment.is_current
        assert amendment.supersedes == "CA-2025-001"

    def test_org_filer(self):
        """Firms and clients file as organizations, not persons."""
        filing = LobbyingFiling(
            id="f-003",
            state="TX",
            filing_type="expenditure_report",
            filer_organization=_make_org(source_state="TX"),
            filer_role="client",
        )
        assert filing.filer_person is None
        assert filing.filer_organization is not None

    def test_json_round_trip(self):
        filing = LobbyingFiling(
            id="f-001",
            state="CA",
            filing_type="activity_report",
            filer_person=_make_person(),
            filer_role="lobbyist",
            positions=[
                LobbyingPosition(
                    bill_reference=BillReference(
                        original_text="SB 100", is_resolved=False
                    ),
                    position="oppose",
                ),
            ],
        )
        json_str = filing.model_dump_json()
        filing2 = LobbyingFiling.model_validate_json(json_str)
        assert filing == filing2
        assert filing2.positions[0].position == "oppose"


class TestEngagement:
    def test_contact_log(self):
        eng = LobbyingEngagement(
            official_contacted="Director Chen",
            official_role="Agency Director",
            institution="Dept of Energy",
            contact_date=date(2025, 3, 15),
            form_of_contact="in_person",
            topics=["renewable energy standards", "grid modernization"],
            outcomes_sought=["support for RES increase to 50%"],
            bill_references=[
                BillReference(original_text="SB 350", is_resolved=False),
            ],
        )
        assert len(eng.topics) == 2
        assert eng.form_of_contact == "in_person"


class TestStateMasterRecord:
    def test_minimal(self):
        smr = StateMasterRecord(
            state="CO",
            state_name="Colorado",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 17),
        )
        assert smr.state == "CO"
        assert smr.effective_end is None
        assert smr.field_requirements == []

    def test_with_requirements(self):
        smr = StateMasterRecord(
            state="CO",
            state_name="Colorado",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 17),
            registration_requirements=[
                RegistrationRequirement(
                    role="lobbyist", required=True, pri_item_id="A1"
                ),
                RegistrationRequirement(
                    role="principal", required=True, pri_item_id="A3"
                ),
                RegistrationRequirement(
                    role="volunteer_lobbyist", required=False, pri_item_id="A2"
                ),
            ],
            de_minimis_financial_threshold=2000.0,
            de_minimis_financial_citation="C.R.S. § 24-6-301(2.5)",
            reporting_parties=[
                ReportingPartyRequirement(
                    entity_role="lobbyist",
                    report_type="activity_report",
                    filing_status="required",
                    reporting_frequency="monthly",
                ),
                ReportingPartyRequirement(
                    entity_role="client",
                    report_type="activity_report",
                    filing_status="required",
                    reporting_frequency="monthly",
                ),
            ],
            field_requirements=[
                FieldRequirement(
                    field_path="total_compensation",
                    reporting_party="lobbyist",
                    status="required",
                    pri_item_id="E2f_i",
                ),
                FieldRequirement(
                    field_path="positions[].bill_reference",
                    reporting_party="lobbyist",
                    status="required",
                    pri_item_id="E2g_ii",
                ),
                FieldRequirement(
                    field_path="engagements[].official_contacted",
                    reporting_party="lobbyist",
                    status="not_applicable",
                    notes="CO does not require contact-level logging",
                ),
            ],
        )
        assert len(smr.registration_requirements) == 3
        assert len(smr.reporting_parties) == 2
        assert smr.de_minimis_financial_threshold == 2000.0

        # Cross-reporting: both lobbyist and client file activity reports
        lobbyist_req = [
            r for r in smr.reporting_parties if r.entity_role == "lobbyist"
        ]
        client_req = [
            r for r in smr.reporting_parties if r.entity_role == "client"
        ]
        assert lobbyist_req[0].filing_status == "required"
        assert client_req[0].filing_status == "required"

    def test_compliance_check_pattern(self):
        """Demonstrate the compliance check: required field is null."""
        smr = StateMasterRecord(
            state="CO",
            state_name="Colorado",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 17),
            field_requirements=[
                FieldRequirement(
                    field_path="total_compensation",
                    reporting_party="lobbyist",
                    status="required",
                    pri_item_id="E2f_i",
                ),
            ],
        )
        filing = LobbyingFiling(
            id="f-001",
            state="CO",
            filing_type="activity_report",
            filer_person=_make_person(source_state="CO"),
            filer_role="lobbyist",
            total_compensation=None,  # Missing!
        )

        # Simple compliance check
        gaps = []
        for req in smr.field_requirements:
            if req.reporting_party in (filing.filer_role, "all"):
                if req.status == "required":
                    value = getattr(filing, req.field_path, None)
                    if value is None:
                        gaps.append(req.field_path)

        assert "total_compensation" in gaps

    def test_json_round_trip(self):
        smr = StateMasterRecord(
            state="WY",
            state_name="Wyoming",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 17),
            registration_requirements=[
                RegistrationRequirement(
                    role="lobbyist", required=True, pri_item_id="A1"
                ),
            ],
        )
        json_str = smr.model_dump_json()
        smr2 = StateMasterRecord.model_validate_json(json_str)
        assert smr == smr2

"""TDD tests for lobbying data model v1.1.

These tests fully specify v1.1 behavior. They are **expected to fail** until
an implementation agent adds:

- `FrameworkReference` model + `FrameworkId` enum in state_master.py
- New fields on `FieldRequirement`: legal_availability, practical_availability,
  evidence_source, evidence_notes, framework_references
- Replacement of pri_item_id/focal_indicator_id/pri_item_ids with
  framework_references on FieldRequirement, RegistrationRequirement, and
  ReportingPartyRequirement (clean-break migration)
- New module src/lobby_analysis/models/compendium.py with CompendiumItem
  and MatrixCell
- New module src/lobby_analysis/models/pipeline.py with ExtractionCapability

Follow the style of tests/test_models.py: one test class per model,
`_make_*` factory helpers, three canonical tests per entity (minimal,
with-options, JSON round-trip) plus validation-rejection tests where the
schema tightens.

See docs/active/data-model-v1.1/plans/20260422_v1.1_gap_closures.md for the
full gap analysis and implementation handoff.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from lobby_analysis.models import (
    CompendiumItem,
    ExtractionCapability,
    FieldRequirement,
    FrameworkReference,
    MatrixCell,
    RegistrationRequirement,
    ReportingPartyRequirement,
    StateMasterRecord,
)


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def _make_framework_ref(**overrides) -> FrameworkReference:
    defaults = {"framework": "pri_2010_disclosure", "item_id": "E1f_i"}
    return FrameworkReference(**{**defaults, **overrides})


def _make_field_requirement(**overrides) -> FieldRequirement:
    defaults = {
        "field_path": "total_compensation",
        "reporting_party": "lobbyist",
        "status": "required",
    }
    return FieldRequirement(**{**defaults, **overrides})


def _make_registration_requirement(**overrides) -> RegistrationRequirement:
    defaults = {"role": "lobbyist", "required": True}
    return RegistrationRequirement(**{**defaults, **overrides})


def _make_reporting_party_requirement(**overrides) -> ReportingPartyRequirement:
    defaults = {
        "entity_role": "lobbyist",
        "report_type": "activity_report",
        "filing_status": "required",
    }
    return ReportingPartyRequirement(**{**defaults, **overrides})


def _make_compendium_item(**overrides) -> CompendiumItem:
    defaults = {
        "id": "C_LOBBYIST_COMPENSATION",
        "name": "Lobbyist compensation disclosure",
        "description": "Whether the state requires disclosure of compensation paid to lobbyists.",
        "domain": "financial",
        "data_type": "boolean",
    }
    return CompendiumItem(**{**defaults, **overrides})


def _make_matrix_cell(**overrides) -> MatrixCell:
    defaults = {
        "state": "CA",
        "compendium_item_id": "C_LOBBYIST_COMPENSATION",
        "required": "required",
        "legal_availability": "public",
        "practical_availability": "structured_bulk",
        "evidence_source": "statute_verified",
    }
    return MatrixCell(**{**defaults, **overrides})


def _make_extraction_capability(**overrides) -> ExtractionCapability:
    defaults = {"state": "CA", "portal_tier": "structured_search"}
    return ExtractionCapability(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# FrameworkReference
# ---------------------------------------------------------------------------


class TestFrameworkReference:
    """The generic rubric-citation model replacing pri_item_id/focal_indicator_id."""

    def test_minimal(self):
        ref = _make_framework_ref()
        assert ref.framework == "pri_2010_disclosure"
        assert ref.item_id == "E1f_i"
        assert ref.item_text is None

    def test_with_item_text(self):
        ref = _make_framework_ref(
            item_text="Total compensation (direct lobbying costs).",
        )
        assert ref.item_text == "Total compensation (direct lobbying costs)."

    @pytest.mark.parametrize(
        "framework",
        [
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
        ],
    )
    def test_accepts_all_documented_frameworks(self, framework):
        ref = _make_framework_ref(framework=framework, item_id="X")
        assert ref.framework == framework

    def test_rejects_unknown_framework(self):
        with pytest.raises(ValidationError):
            _make_framework_ref(framework="bogus_framework_2099")

    def test_item_id_is_required(self):
        with pytest.raises(ValidationError):
            FrameworkReference(framework="pri_2010_disclosure")  # no item_id

    def test_json_round_trip(self):
        ref = _make_framework_ref(
            framework="focal_2024",
            item_id="3.3a",
            item_text="No user registration required for basic access.",
        )
        json_str = ref.model_dump_json()
        ref2 = FrameworkReference.model_validate_json(json_str)
        assert ref == ref2


# ---------------------------------------------------------------------------
# FieldRequirement v1.1
# ---------------------------------------------------------------------------


class TestFieldRequirementV11:
    """FieldRequirement gains availability axes, evidence source, and framework_references."""

    def test_minimal_with_v11_defaults(self):
        fr = _make_field_requirement()
        assert fr.field_path == "total_compensation"
        assert fr.legal_availability == "unknown"
        assert fr.practical_availability == "unknown"
        assert fr.evidence_source == "unknown"
        assert fr.evidence_notes == ""
        assert fr.framework_references == []

    def test_accepts_availability_enums(self):
        fr = _make_field_requirement(
            legal_availability="public",
            practical_availability="structured_bulk",
        )
        assert fr.legal_availability == "public"
        assert fr.practical_availability == "structured_bulk"

    @pytest.mark.parametrize(
        "legal",
        ["public", "redacted", "access_restricted", "paper_on_request", "unknown"],
    )
    def test_legal_availability_accepts_all_documented_values(self, legal):
        fr = _make_field_requirement(legal_availability=legal)
        assert fr.legal_availability == legal

    @pytest.mark.parametrize(
        "practical",
        [
            "structured_bulk",
            "structured_search",
            "html_search",
            "pdf_only",
            "not_available",
            "unknown",
        ],
    )
    def test_practical_availability_accepts_all_documented_values(self, practical):
        fr = _make_field_requirement(practical_availability=practical)
        assert fr.practical_availability == practical

    def test_rejects_unknown_availability_values(self):
        with pytest.raises(ValidationError):
            _make_field_requirement(legal_availability="sort_of_public")
        with pytest.raises(ValidationError):
            _make_field_requirement(practical_availability="carrier_pigeon")

    @pytest.mark.parametrize(
        "evidence",
        ["statute_verified", "database_inferred", "both", "fellow_judgment", "unknown"],
    )
    def test_evidence_source_accepts_all_documented_values(self, evidence):
        fr = _make_field_requirement(evidence_source=evidence)
        assert fr.evidence_source == evidence

    def test_rejects_unknown_evidence_source(self):
        with pytest.raises(ValidationError):
            _make_field_requirement(evidence_source="vibes")

    def test_evidence_notes_free_text(self):
        fr = _make_field_requirement(
            evidence_source="fellow_judgment",
            evidence_notes="State statute ambiguous; interpreted by fellow per §27-104 plain reading.",
        )
        assert "§27-104" in fr.evidence_notes

    def test_accepts_framework_references(self):
        fr = _make_field_requirement(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1f_i"),
                FrameworkReference(framework="focal_2026", item_id="7.6"),
                FrameworkReference(framework="lda", item_id="LD-2.line15"),
            ],
        )
        assert len(fr.framework_references) == 3
        assert fr.framework_references[0].framework == "pri_2010_disclosure"
        assert fr.framework_references[2].framework == "lda"

    def test_rejects_old_pri_item_id_field(self):
        """Clean-break migration: pri_item_id is removed in v1.1."""
        with pytest.raises(ValidationError):
            FieldRequirement(
                field_path="total_compensation",
                reporting_party="lobbyist",
                status="required",
                pri_item_id="E1f_i",  # v1.0 field, now removed
            )

    def test_rejects_old_focal_indicator_id_field(self):
        """Clean-break migration: focal_indicator_id is removed in v1.1."""
        with pytest.raises(ValidationError):
            FieldRequirement(
                field_path="total_compensation",
                reporting_party="lobbyist",
                status="required",
                focal_indicator_id="7.6",  # v1.0 field, now removed
            )

    def test_json_round_trip_full_v11(self):
        fr = _make_field_requirement(
            legal_availability="public",
            practical_availability="pdf_only",
            evidence_source="both",
            evidence_notes="Cross-confirmed via §27-104 reading + 2024 filing sample.",
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1f_i"),
                FrameworkReference(framework="focal_2026", item_id="7.6"),
            ],
            legal_citation="CA Gov Code §86114(b)(3)",
            notes="Compensation field required on every quarterly report.",
        )
        json_str = fr.model_dump_json()
        fr2 = FieldRequirement.model_validate_json(json_str)
        assert fr == fr2


# ---------------------------------------------------------------------------
# RegistrationRequirement v1.1 — framework_references migration
# ---------------------------------------------------------------------------


class TestRegistrationRequirementV11:
    def test_minimal_has_empty_framework_references(self):
        rr = _make_registration_requirement()
        assert rr.framework_references == []

    def test_accepts_framework_references(self):
        rr = _make_registration_requirement(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="A1"),
                FrameworkReference(framework="focal_2026", item_id="1.1"),
            ],
        )
        assert len(rr.framework_references) == 2

    def test_rejects_old_pri_item_id_field(self):
        """Clean-break migration: pri_item_id removed."""
        with pytest.raises(ValidationError):
            RegistrationRequirement(
                role="lobbyist",
                required=True,
                pri_item_id="A1",  # v1.0 field, now removed
            )

    def test_json_round_trip(self):
        rr = _make_registration_requirement(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="A1"),
            ],
            legal_citation="CA Gov Code §86100",
            notes="Registration required for any lobbyist over threshold.",
        )
        json_str = rr.model_dump_json()
        rr2 = RegistrationRequirement.model_validate_json(json_str)
        assert rr == rr2


# ---------------------------------------------------------------------------
# ReportingPartyRequirement v1.1 — framework_references migration
# ---------------------------------------------------------------------------


class TestReportingPartyRequirementV11:
    def test_minimal_has_empty_framework_references(self):
        rpr = _make_reporting_party_requirement()
        assert rpr.framework_references == []

    def test_accepts_framework_references(self):
        rpr = _make_reporting_party_requirement(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1h_i"),
                FrameworkReference(framework="focal_2026", item_id="2.1"),
            ],
        )
        assert len(rpr.framework_references) == 2

    def test_rejects_old_pri_item_ids_field(self):
        """Clean-break migration: pri_item_ids removed."""
        with pytest.raises(ValidationError):
            ReportingPartyRequirement(
                entity_role="lobbyist",
                report_type="activity_report",
                filing_status="required",
                pri_item_ids=["E1h_i", "E1h_ii"],  # v1.0 field, now removed
            )

    def test_json_round_trip(self):
        rpr = _make_reporting_party_requirement(
            reporting_frequency="quarterly",
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1h_iii"),
            ],
        )
        json_str = rpr.model_dump_json()
        rpr2 = ReportingPartyRequirement.model_validate_json(json_str)
        assert rpr == rpr2


# ---------------------------------------------------------------------------
# StateMasterRecord composite with v1.1 sub-entities
# ---------------------------------------------------------------------------


class TestStateMasterRecordV11:
    """Validates the composite loads cleanly with v1.1-shaped children."""

    def test_loads_with_v11_shaped_children(self):
        from datetime import date

        smr = StateMasterRecord(
            state="CA",
            state_name="California",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 22),
            legal_citations=["CA Gov Code §86100 et seq."],
            registration_requirements=[
                _make_registration_requirement(
                    framework_references=[
                        FrameworkReference(framework="pri_2010_disclosure", item_id="A1"),
                    ],
                ),
            ],
            reporting_parties=[
                _make_reporting_party_requirement(
                    reporting_frequency="quarterly",
                    framework_references=[
                        FrameworkReference(framework="pri_2010_disclosure", item_id="E1h_iii"),
                    ],
                ),
            ],
            field_requirements=[
                _make_field_requirement(
                    legal_availability="public",
                    practical_availability="structured_search",
                    evidence_source="statute_verified",
                    framework_references=[
                        FrameworkReference(framework="pri_2010_disclosure", item_id="E1f_i"),
                    ],
                ),
            ],
        )
        assert smr.state == "CA"
        assert smr.registration_requirements[0].framework_references[0].item_id == "A1"
        assert smr.field_requirements[0].legal_availability == "public"

    def test_json_round_trip(self):
        from datetime import date

        smr = StateMasterRecord(
            state="CA",
            state_name="California",
            version="2026-Q1",
            effective_start=date(2026, 1, 1),
            last_updated=date(2026, 4, 22),
        )
        json_str = smr.model_dump_json()
        smr2 = StateMasterRecord.model_validate_json(json_str)
        assert smr == smr2


# ---------------------------------------------------------------------------
# CompendiumItem
# ---------------------------------------------------------------------------


class TestCompendiumItem:
    """The N in the N x 50 x 2 matrix — union of items across frameworks."""

    def test_minimal(self):
        ci = _make_compendium_item()
        assert ci.id == "C_LOBBYIST_COMPENSATION"
        assert ci.domain == "financial"
        assert ci.data_type == "boolean"
        assert ci.framework_references == []
        assert ci.observable_from_database is False

    def test_with_all_optional_fields(self):
        ci = _make_compendium_item(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1f_i"),
                FrameworkReference(framework="focal_2026", item_id="7.6"),
                FrameworkReference(framework="sunlight_2015", item_id="compensation"),
            ],
            maps_to_state_master_field="field_requirements[].total_compensation",
            maps_to_filing_field="total_compensation",
            observable_from_database=True,
            notes="Cross-framework consensus item; reliable DB-inferrable.",
        )
        assert len(ci.framework_references) == 3
        assert ci.observable_from_database is True

    @pytest.mark.parametrize(
        "domain",
        [
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
        ],
    )
    def test_accepts_all_documented_domains(self, domain):
        ci = _make_compendium_item(domain=domain)
        assert ci.domain == domain

    def test_rejects_unknown_domain(self):
        with pytest.raises(ValidationError):
            _make_compendium_item(domain="vibes_based")

    @pytest.mark.parametrize(
        "dt", ["boolean", "numeric", "categorical", "free_text", "compound"]
    )
    def test_accepts_all_documented_data_types(self, dt):
        ci = _make_compendium_item(data_type=dt)
        assert ci.data_type == dt

    def test_rejects_unknown_data_type(self):
        with pytest.raises(ValidationError):
            _make_compendium_item(data_type="holographic")

    def test_json_round_trip(self):
        ci = _make_compendium_item(
            framework_references=[
                FrameworkReference(framework="hired_guns_2007", item_id="IndividualSpending_4"),
            ],
            maps_to_filing_field="total_compensation",
            observable_from_database=True,
            notes="Testing round-trip with full population.",
        )
        json_str = ci.model_dump_json()
        ci2 = CompendiumItem.model_validate_json(json_str)
        assert ci == ci2


# ---------------------------------------------------------------------------
# MatrixCell
# ---------------------------------------------------------------------------


class TestMatrixCell:
    """The projected (compendium item, state) pair — one row of the N x 50 x 2 matrix."""

    def test_minimal(self):
        cell = _make_matrix_cell()
        assert cell.state == "CA"
        assert cell.compendium_item_id == "C_LOBBYIST_COMPENSATION"
        assert cell.required == "required"
        assert cell.legal_availability == "public"
        assert cell.practical_availability == "structured_bulk"
        assert cell.evidence_source == "statute_verified"
        assert cell.framework_references == []
        assert cell.notes == ""

    def test_with_framework_references_and_notes(self):
        cell = _make_matrix_cell(
            framework_references=[
                FrameworkReference(framework="pri_2010_disclosure", item_id="E1f_i"),
                FrameworkReference(framework="focal_2026", item_id="7.6"),
            ],
            notes="Denormalized from SMR and CompendiumItem for export.",
        )
        assert len(cell.framework_references) == 2
        assert "export" in cell.notes

    def test_required_accepts_all_field_statuses(self):
        for status in ["required", "optional", "not_applicable", "unknown"]:
            cell = _make_matrix_cell(required=status)
            assert cell.required == status

    def test_rejects_unknown_required_status(self):
        with pytest.raises(ValidationError):
            _make_matrix_cell(required="somewhat_required")

    def test_json_round_trip(self):
        cell = _make_matrix_cell(
            legal_availability="redacted",
            practical_availability="not_available",
            evidence_source="fellow_judgment",
            framework_references=[
                FrameworkReference(framework="focal_2026", item_id="8.1"),
            ],
            notes="Contact-log field redacted under confidentiality provision §X.",
        )
        json_str = cell.model_dump_json()
        cell2 = MatrixCell.model_validate_json(json_str)
        assert cell == cell2


# ---------------------------------------------------------------------------
# ExtractionCapability
# ---------------------------------------------------------------------------


class TestExtractionCapability:
    """Per-state pipeline capability — companion to StateMasterRecord."""

    def test_minimal(self):
        ec = _make_extraction_capability()
        assert ec.state == "CA"
        assert ec.portal_tier == "structured_search"
        assert ec.fields_extractable == []
        assert ec.fields_unextractable == []
        assert ec.known_limitations == []
        assert ec.last_pipeline_run is None
        assert ec.cadence is None
        assert ec.parse_error_rate is None

    def test_with_full_metadata(self):
        ec = _make_extraction_capability(
            portal_tier="pdf_only",
            fields_extractable=["total_compensation", "total_expenditure"],
            fields_unextractable=["engagements[].official_contacted"],
            known_limitations=[
                "PDF filings require OCR pass; accuracy ~92% on scanned docs.",
                "Contact-log fields not populated in source PDFs.",
            ],
            last_pipeline_run=datetime(2026, 4, 20, 14, 30, 0),
            next_expected_run=datetime(2026, 7, 20, 14, 30, 0),
            cadence="quarterly",
            parse_error_rate=0.08,
            notes="Tier-3 state; extraction pipeline is PDF+LLM heavy.",
        )
        assert ec.portal_tier == "pdf_only"
        assert len(ec.fields_extractable) == 2
        assert ec.parse_error_rate == 0.08
        assert ec.cadence == "quarterly"

    @pytest.mark.parametrize(
        "tier",
        [
            "clean_bulk_api",
            "structured_search",
            "html_search",
            "pdf_only",
            "paper_on_request",
            "mixed",
        ],
    )
    def test_accepts_all_portal_tiers(self, tier):
        ec = _make_extraction_capability(portal_tier=tier)
        assert ec.portal_tier == tier

    def test_rejects_unknown_portal_tier(self):
        with pytest.raises(ValidationError):
            _make_extraction_capability(portal_tier="magical")

    @pytest.mark.parametrize(
        "cadence",
        [
            "monthly",
            "quarterly",
            "semi_annual",
            "annual",
            "on_change",
            "ad_hoc",
        ],
    )
    def test_accepts_all_cadences(self, cadence):
        ec = _make_extraction_capability(cadence=cadence)
        assert ec.cadence == cadence

    def test_rejects_unknown_cadence(self):
        with pytest.raises(ValidationError):
            _make_extraction_capability(cadence="whenever")

    def test_parse_error_rate_bounds(self):
        # Valid at 0.0 and 1.0
        assert _make_extraction_capability(parse_error_rate=0.0).parse_error_rate == 0.0
        assert _make_extraction_capability(parse_error_rate=1.0).parse_error_rate == 1.0
        # Rejected outside [0, 1]
        with pytest.raises(ValidationError):
            _make_extraction_capability(parse_error_rate=-0.1)
        with pytest.raises(ValidationError):
            _make_extraction_capability(parse_error_rate=1.1)

    def test_json_round_trip(self):
        ec = _make_extraction_capability(
            portal_tier="html_search",
            fields_extractable=["total_compensation"],
            cadence="monthly",
            last_pipeline_run=datetime(2026, 4, 1, 12, 0, 0),
            parse_error_rate=0.03,
        )
        json_str = ec.model_dump_json()
        ec2 = ExtractionCapability.model_validate_json(json_str)
        assert ec == ec2

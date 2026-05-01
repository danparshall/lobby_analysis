"""TDD tests for lobbying data model v1.3.

v1.3 adds three optional `str | None` fields to `FieldRequirement`
(condition_text / regime / registrant_role) and extends `FieldStatus`
to include the v2 scorer-prompt vocabulary
(required_conditional / not_required / not_addressed) without removing
the existing v1.2 values.

These tests are expected to fail until the v1.3 schema bump lands per
docs/active/statute-extraction/plans/20260501_statute_extraction_harness.md
Phase 0.
"""

from pathlib import Path

from lobby_analysis.models import FieldRequirement, StateMasterRecord


FIXTURE_V1_2 = (
    Path(__file__).parent / "fixtures" / "state_master" / "oh_2025_v1_2.json"
)


def test_field_requirement_v1_3_accepts_condition_text():
    """Round-trip a `required_conditional` row carrying the qualifying clause."""
    fr = FieldRequirement(
        field_path="lobbyist_threshold",
        reporting_party="lobbyist",
        status="required_conditional",
        condition_text="as one of the individual's main purposes",
    )
    assert fr.status == "required_conditional"
    assert fr.condition_text == "as one of the individual's main purposes"

    payload = fr.model_dump_json()
    fr2 = FieldRequirement.model_validate_json(payload)
    assert fr2.model_dump_json() == payload


def test_field_requirement_v1_3_accepts_regime():
    """`regime` is a free-string optional field; default None."""
    fr_default = FieldRequirement(
        field_path="lobbyist_threshold",
        reporting_party="lobbyist",
        status="required",
    )
    assert fr_default.regime is None

    fr = FieldRequirement(
        field_path="lobbyist_threshold",
        reporting_party="lobbyist",
        status="required",
        regime="legislative",
    )
    assert fr.regime == "legislative"

    payload = fr.model_dump_json()
    assert FieldRequirement.model_validate_json(payload).model_dump_json() == payload


def test_field_requirement_v1_3_accepts_registrant_role():
    """`registrant_role` is a free-string optional field; default None."""
    fr_default = FieldRequirement(
        field_path="lobbyist_threshold",
        reporting_party="lobbyist",
        status="required",
    )
    assert fr_default.registrant_role is None

    fr = FieldRequirement(
        field_path="lobbyist_threshold",
        reporting_party="lobbyist",
        status="required",
        registrant_role="client_lobbyist",
    )
    assert fr.registrant_role == "client_lobbyist"

    payload = fr.model_dump_json()
    assert FieldRequirement.model_validate_json(payload).model_dump_json() == payload


def test_field_requirement_v1_3_accepts_v2_status_values():
    """`FieldStatus` extends to include `not_required` and `not_addressed`.

    The v1.2 values (`required` / `optional` / `not_applicable` / `unknown`)
    must continue to validate; v1.3 adds three more.
    """
    for status_value in ("not_required", "not_addressed"):
        fr = FieldRequirement(
            field_path="lobbyist_threshold",
            reporting_party="lobbyist",
            status=status_value,
        )
        assert fr.status == status_value


def test_field_requirement_v1_2_data_still_loads():
    """A v1.2-shape SMR (no condition_text/regime/registrant_role keys)
    deserializes; the three new fields default to None.

    This is the load-bearing non-breaking-change test.
    """
    payload = FIXTURE_V1_2.read_text()
    smr = StateMasterRecord.model_validate_json(payload)

    assert smr.field_requirements, "fixture should contain field_requirements"
    for fr in smr.field_requirements:
        assert fr.condition_text is None
        assert fr.regime is None
        assert fr.registrant_role is None

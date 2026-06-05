"""TDD tests for lobbying data model v1.2.

These tests fully specify v1.2 behavior. They are **expected to fail** until
an implementation agent adds:

- `total_hours_communicating: float | None = None` to `LobbyingFiling`
- `total_hours_other: float | None = None` to `LobbyingFiling`

The bump is documentary (versioning lives in plans + RESEARCH_LOG, not a
code-level constant); v1.1's TDD pattern at `tests/test_models_v1_1.py` is the
template. Schema-layer scope reminder: this v1.2 bump applies to
`src/lobby_analysis/models/filings.py` (the disclosure-data contract). It does
NOT apply to `src/lobby_analysis/models_v2/cells.py` (the statute-metadata
contract for Prong 1) — the two layers version independently.

See docs/active/wi-disclosure-explore/plans/wi_tier_2_parser.md Phase 1 for
the originating plan and rationale (Wisconsin Tier-2 parser needs hours
fields per FOCAL 7.x time-spent + WI portal Total Lobbying Effort table).
"""

from lobby_analysis.models import (
    LobbyingFiling,
    Organization,
    Person,
)


# ---------------------------------------------------------------------------
# Factories (paralleling tests/test_models.py + tests/test_models_v1_1.py)
# ---------------------------------------------------------------------------


def _make_person(**overrides) -> Person:
    defaults = {"id": "WI-lobbyist-11052", "name": "Bryan Brooks", "source_state": "WI"}
    return Person(**{**defaults, **overrides})


def _make_org(**overrides) -> Organization:
    defaults = {
        "id": "WI-principal-11590",
        "name": "Dairy Business Association",
        "source_state": "WI",
    }
    return Organization(**{**defaults, **overrides})


def _make_minimal_filing(**overrides) -> LobbyingFiling:
    """Minimal valid LobbyingFiling — only the required fields, nothing else."""
    defaults = {
        "id": "wi-filing-001",
        "state": "WI",
        "filing_type": "activity_report",
        "filer_person": _make_person(),
        "filer_role": "lobbyist",
    }
    return LobbyingFiling(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# LobbyingFiling v1.2 — hours fields
# ---------------------------------------------------------------------------


class TestLobbyingFilingV12HoursFields:
    """The two new optional hours fields on `LobbyingFiling`.

    Sourced from the Wisconsin portal's per-(principal, semester) "Total
    Lobbying Effort" table — Communication hours and Other (non-communication)
    hours. These are the per-filing aggregate totals; itemized time-report
    breakdowns are tier-3 and not covered by this schema.
    """

    def test_accepts_total_hours_communicating(self):
        """The new field accepts a float value and round-trips through the field
        accessor."""
        filing = _make_minimal_filing(total_hours_communicating=102.50)
        assert filing.total_hours_communicating == 102.50

    def test_accepts_total_hours_other(self):
        """The companion field accepts a float value and round-trips through the
        field accessor."""
        filing = _make_minimal_filing(total_hours_other=566.00)
        assert filing.total_hours_other == 566.00

    def test_both_fields_default_to_none_when_omitted(self):
        """v1.2 is non-breaking: omitting the new fields still validates and
        leaves them at None, matching the existing total_compensation /
        total_expenditure default behavior."""
        filing = _make_minimal_filing()
        assert filing.total_hours_communicating is None
        assert filing.total_hours_other is None

    def test_accepts_zero_hours(self):
        """Zero hours is a valid value (low-activity periods file with zeros,
        not absent fields). 420 of 770 WI lobbyists on the 2026-05-26 snapshot
        have zero-hours in at least one period — the parser must emit those
        filings, not silently skip them. So 0.0 must validate as a real value
        distinct from None."""
        filing = _make_minimal_filing(
            total_hours_communicating=0.0,
            total_hours_other=0.0,
        )
        assert filing.total_hours_communicating == 0.0
        assert filing.total_hours_other == 0.0
        # Distinct from None — both fields are set, not omitted.
        assert filing.total_hours_communicating is not None
        assert filing.total_hours_other is not None

    def test_json_round_trip_with_hours_set(self):
        """Round-trip via model_dump + model_validate preserves both new fields
        with their numeric values."""
        filing = _make_minimal_filing(
            total_hours_communicating=102.50,
            total_hours_other=566.00,
        )
        dumped = filing.model_dump()
        restored = LobbyingFiling.model_validate(dumped)
        assert restored.total_hours_communicating == 102.50
        assert restored.total_hours_other == 566.00
        assert restored == filing

    def test_json_round_trip_with_hours_omitted(self):
        """An empty filing round-trips with both new fields as None."""
        filing = _make_minimal_filing()
        dumped = filing.model_dump()
        restored = LobbyingFiling.model_validate(dumped)
        assert restored.total_hours_communicating is None
        assert restored.total_hours_other is None
        assert restored == filing

    def test_exclude_none_omits_unset_hours_but_keeps_set_hours(self):
        """Serialization contract: with exclude_none=True, an empty filing
        omits the new keys (parity with total_compensation / total_expenditure),
        BUT a filing with hours set keeps them in the dump with their numeric
        values. This is a driving test — in RED, the set kwargs are silently
        dropped by pydantic's extra='ignore' default, so set_dump won't
        contain the keys at all and the value assertions fail."""
        unset = _make_minimal_filing()
        unset_dump = unset.model_dump(exclude_none=True)
        assert "total_hours_communicating" not in unset_dump
        assert "total_hours_other" not in unset_dump
        # Parity check: pre-existing None-defaulted optional float fields
        # behave the same way under exclude_none=True. Guards against a
        # pydantic-default-behavior surprise on either side of the bump.
        assert "total_compensation" not in unset_dump
        assert "total_expenditure" not in unset_dump

        set_filing = _make_minimal_filing(
            total_hours_communicating=102.50,
            total_hours_other=566.00,
        )
        set_dump = set_filing.model_dump(exclude_none=True)
        assert set_dump["total_hours_communicating"] == 102.50
        assert set_dump["total_hours_other"] == 566.00

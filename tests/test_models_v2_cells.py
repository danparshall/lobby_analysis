"""Tests for `lobby_analysis.models_v2.cells` cell subclasses.

Targets the v2 cell model semantic rules described in the implementation plan
Phases 2-4. Tests focus on OUR row-semantic rules (GradedIntCell's 25-step
grid, BoundedIntCell's 0-15 range, frozen immutability, cell_id requirement,
wrapper-field propagation) — NOT pydantic's framework validation behavior.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Common wrapper-field behavior — tested via BinaryCell (simplest concrete)
# ---------------------------------------------------------------------------


def test_binary_cell_constructs_with_defaults():
    """A minimal BinaryCell needs cell_id + value; wrapper fields default."""
    from lobby_analysis.models_v2.cells import BinaryCell

    cell = BinaryCell(
        cell_id=("lobbyist_registration_required", "legal"),
        value=True,
    )
    assert cell.value is True
    assert cell.cell_id == ("lobbyist_registration_required", "legal")
    assert cell.conditional is False
    assert cell.condition_text is None
    assert cell.confidence is None
    assert cell.provenance is None


def test_binary_cell_accepts_false_value():
    """Both True and False are valid for BinaryCell.value (sanity: not a truthy bug)."""
    from lobby_analysis.models_v2.cells import BinaryCell

    cell = BinaryCell(
        cell_id=("some_row", "legal"),
        value=False,
    )
    assert cell.value is False


def test_cell_requires_cell_id():
    """cell_id is required on every cell — constructing without it must fail."""
    from lobby_analysis.models_v2.cells import BinaryCell

    with pytest.raises(ValidationError):
        BinaryCell(value=True)  # type: ignore[call-arg]


def test_binary_cell_wrapper_fields_propagate():
    """conditional + condition_text + confidence + provenance all round-trip."""
    from lobby_analysis.models_v2.cells import BinaryCell
    from lobby_analysis.models_v2.provenance import EvidenceSpan

    span = EvidenceSpan(section_reference="§101.70(B)(1)")
    cell = BinaryCell(
        cell_id=("lobbyist_registration_required", "legal"),
        value=True,
        conditional=True,
        condition_text="if expenditures ≥ $200/quarter",
        confidence="high",
        provenance=span,
    )
    assert cell.conditional is True
    assert cell.condition_text == "if expenditures ≥ $200/quarter"
    assert cell.confidence == "high"
    assert cell.provenance is span


def test_binary_cell_rejects_non_bool_value():
    """OUR rule: BinaryCell.value must be a true bool, not a string like 'yes'.

    Pydantic 2 in strict mode rejects str-coerced-to-bool; we want the same
    behavior here so the model surfaces extraction-time format mismatches as
    validation errors rather than silently coercing.
    """
    from lobby_analysis.models_v2.cells import BinaryCell

    with pytest.raises(ValidationError):
        BinaryCell(
            cell_id=("some_row", "legal"),
            value="yes",  # type: ignore[arg-type]
        )


def test_binary_cell_is_frozen():
    """frozen=True (per iter-1 stamped-output discipline) — assignment raises."""
    from lobby_analysis.models_v2.cells import BinaryCell

    cell = BinaryCell(cell_id=("r", "legal"), value=True)
    with pytest.raises(ValidationError):
        cell.value = False  # type: ignore[misc]


def test_binary_cell_confidence_only_accepts_three_literals():
    """confidence is Literal['high', 'medium', 'low'] | None — 'maybe' is invalid."""
    from lobby_analysis.models_v2.cells import BinaryCell

    with pytest.raises(ValidationError):
        BinaryCell(
            cell_id=("r", "legal"),
            value=True,
            confidence="maybe",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Numeric cells (Phase 3)
# ---------------------------------------------------------------------------


def test_decimal_cell_accepts_decimal_and_none():
    """DecimalCell wraps Optional[Decimal]; both states must be expressible."""
    from lobby_analysis.models_v2.cells import DecimalCell

    cell = DecimalCell(cell_id=("compensation_threshold", "legal"), value=Decimal("200"))
    assert cell.value == Decimal("200")

    null_cell = DecimalCell(cell_id=("compensation_threshold", "legal"), value=None)
    assert null_cell.value is None


def test_decimal_cell_rejects_negative_threshold():
    """OUR rule: threshold dollars must be non-negative (negative is nonsensical)."""
    from lobby_analysis.models_v2.cells import DecimalCell

    with pytest.raises(ValidationError):
        DecimalCell(cell_id=("compensation_threshold", "legal"), value=Decimal("-1"))


def test_decimal_cell_rejects_string_value():
    """We use strict mode — '200' is not Decimal('200'); the extraction layer
    must emit Decimal, not str."""
    from lobby_analysis.models_v2.cells import DecimalCell

    with pytest.raises(ValidationError):
        DecimalCell(
            cell_id=("compensation_threshold", "legal"),
            value="200",  # type: ignore[arg-type]
        )


def test_int_cell_accepts_int_and_none():
    from lobby_analysis.models_v2.cells import IntCell

    assert IntCell(cell_id=("r", "legal"), value=10).value == 10
    assert IntCell(cell_id=("r", "legal"), value=None).value is None


def test_int_cell_rejects_float():
    """OUR rule: IntCell.value is strict int; 10.5 should not coerce to 10."""
    from lobby_analysis.models_v2.cells import IntCell

    with pytest.raises(ValidationError):
        IntCell(cell_id=("r", "legal"), value=10.5)  # type: ignore[arg-type]


def test_float_cell_accepts_float_and_none():
    from lobby_analysis.models_v2.cells import FloatCell

    assert FloatCell(cell_id=("r", "legal"), value=0.25).value == 0.25
    assert FloatCell(cell_id=("r", "legal"), value=None).value is None


# ---- GradedIntCell: 0..100 step 25 ----


@pytest.mark.parametrize("v", [0, 25, 50, 75, 100])
def test_graded_int_cell_accepts_on_grid_values(v: int):
    from lobby_analysis.models_v2.cells import GradedIntCell

    assert GradedIntCell(cell_id=("r", "practical"), value=v).value == v


@pytest.mark.parametrize("v", [-25, 1, 30, 49, 125])
def test_graded_int_cell_rejects_off_grid_or_out_of_range_values(v: int):
    """OUR rule: GradedIntCell is on the FOCAL 0/25/50/75/100 grid; anything else is invalid."""
    from lobby_analysis.models_v2.cells import GradedIntCell

    with pytest.raises(ValidationError):
        GradedIntCell(cell_id=("r", "practical"), value=v)


# ---- BoundedIntCell: 0..15 ----


@pytest.mark.parametrize("v", [0, 1, 8, 15])
def test_bounded_int_cell_accepts_in_range_values(v: int):
    from lobby_analysis.models_v2.cells import BoundedIntCell

    cell = BoundedIntCell(
        cell_id=("lobbying_search_simultaneous_multicriteria_capability", "practical"),
        value=v,
    )
    assert cell.value == v


@pytest.mark.parametrize("v", [-1, 16, 100])
def test_bounded_int_cell_rejects_out_of_range_values(v: int):
    """OUR rule: BoundedIntCell.value must be in [0, 15] inclusive."""
    from lobby_analysis.models_v2.cells import BoundedIntCell

    with pytest.raises(ValidationError):
        BoundedIntCell(
            cell_id=("lobbying_search_simultaneous_multicriteria_capability", "practical"),
            value=v,
        )


# ---------------------------------------------------------------------------
# Enum / FreeText (Phase 4 generics)
# ---------------------------------------------------------------------------


def test_enum_cell_accepts_arbitrary_nonempty_string():
    """Per Phase 4: EnumCell starts permissive — domain enforcement is per-row,
    added later via enum_domains.py. A bare EnumCell accepts any nonempty str."""
    from lobby_analysis.models_v2.cells import EnumCell

    cell = EnumCell(cell_id=("some_enum_row", "legal"), value="some_value")
    assert cell.value == "some_value"


def test_enum_set_cell_accepts_frozenset():
    from lobby_analysis.models_v2.cells import EnumSetCell

    cell = EnumSetCell(
        cell_id=("some_set_row", "legal"),
        value=frozenset({"a", "b", "c"}),
    )
    assert cell.value == frozenset({"a", "b", "c"})


def test_free_text_cell_accepts_short_text():
    from lobby_analysis.models_v2.cells import FreeTextCell

    cell = FreeTextCell(
        cell_id=("lobbyist_spending_report_cadence_other_specification", "legal"),
        value="biweekly",
    )
    assert cell.value == "biweekly"


def test_free_text_cell_rejects_over_max_length():
    """OUR rule: FreeTextCell is capped at 500 chars to prevent unbounded extraction."""
    from lobby_analysis.models_v2.cells import FreeTextCell

    too_long = "x" * 501
    with pytest.raises(ValidationError):
        FreeTextCell(
            cell_id=("lobbyist_spending_report_cadence_other_specification", "legal"),
            value=too_long,
        )


# ---------------------------------------------------------------------------
# Specialized cells (Phase 4) — struct shapes user-approved 2026-05-14
# ---------------------------------------------------------------------------


def test_update_cadence_cell_accepts_documented_enum_values():
    """User-approved struct: Literal['daily', 'weekly', 'monthly',
    'semiannual_or_less_often', 'none'] | None.
    Source: HG 2007 + FOCAL 2024 projection mappings converge on this enum.
    """
    from lobby_analysis.models_v2.cells import UpdateCadenceCell

    cell = UpdateCadenceCell(
        cell_id=("lobbyist_directory_update_cadence", "practical"),
        value="daily",
    )
    assert cell.value == "daily"
    null_cell = UpdateCadenceCell(
        cell_id=("lobbyist_directory_update_cadence", "practical"),
        value=None,
    )
    assert null_cell.value is None


def test_update_cadence_cell_rejects_unknown_cadence():
    from lobby_analysis.models_v2.cells import UpdateCadenceCell

    with pytest.raises(ValidationError):
        UpdateCadenceCell(
            cell_id=("lobbyist_directory_update_cadence", "practical"),
            value="hourly",  # type: ignore[arg-type]
        )


def test_time_threshold_cell_accepts_magnitude_and_unit():
    """User-approved struct: magnitude: Decimal | None; unit: Literal[...] | None.
    Source: Newmark 2005/2017 projection mappings (federal LDA 20% rule).
    """
    from lobby_analysis.models_v2.cells import TimeThresholdCell

    cell = TimeThresholdCell(
        cell_id=("time_threshold_for_lobbyist_registration", "legal"),
        magnitude=Decimal("20"),
        unit="percent_of_work_time",
    )
    assert cell.magnitude == Decimal("20")
    assert cell.unit == "percent_of_work_time"


def test_time_threshold_cell_accepts_both_fields_none():
    """A row where extraction found no threshold mentioned."""
    from lobby_analysis.models_v2.cells import TimeThresholdCell

    cell = TimeThresholdCell(
        cell_id=("time_threshold_for_lobbyist_registration", "legal"),
        magnitude=None,
        unit=None,
    )
    assert cell.magnitude is None
    assert cell.unit is None


def test_time_threshold_cell_rejects_unknown_unit():
    from lobby_analysis.models_v2.cells import TimeThresholdCell

    with pytest.raises(ValidationError):
        TimeThresholdCell(
            cell_id=("time_threshold_for_lobbyist_registration", "legal"),
            magnitude=Decimal("20"),
            unit="fortnights",  # type: ignore[arg-type]
        )


def test_time_spent_cell_accepts_magnitude_and_unit():
    """User-approved struct: same shape as TimeThreshold but semantically different
    (reads disclosed time, not threshold)."""
    from lobby_analysis.models_v2.cells import TimeSpentCell

    cell = TimeSpentCell(
        cell_id=("lobbyist_or_principal_report_includes_time_spent_on_lobbying", "legal"),
        magnitude=Decimal("10"),
        unit="hours_per_quarter",
    )
    assert cell.magnitude == Decimal("10")
    assert cell.unit == "hours_per_quarter"


def test_sector_classification_cell_accepts_open_string():
    """User-approved struct: value: str | None (LDA's 75 issue codes are one example;
    states use varied schemes — FOCAL mapping explicitly leaves this loose).
    """
    from lobby_analysis.models_v2.cells import SectorClassificationCell

    cell = SectorClassificationCell(
        cell_id=("lobbyist_reg_form_includes_lobbyist_sector", "legal"),
        value="TAX",
    )
    assert cell.value == "TAX"
    null_cell = SectorClassificationCell(
        cell_id=("lobbyist_reg_form_includes_lobbyist_sector", "legal"),
        value=None,
    )
    assert null_cell.value is None


def test_count_with_fte_cell_accepts_count_and_fte():
    """User-approved struct: count: int | None; fte: float | None."""
    from lobby_analysis.models_v2.cells import CountWithFTECell

    cell = CountWithFTECell(
        cell_id=(
            "lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE",
            "legal",
        ),
        count=5,
        fte=2.5,
    )
    assert cell.count == 5
    assert cell.fte == 2.5


def test_enum_set_with_amounts_cell_accepts_value_and_amounts():
    """User-approved struct: value: frozenset[Literal[...]];
    amounts: dict[str, Decimal].
    """
    from lobby_analysis.models_v2.cells import EnumSetWithAmountsCell

    cell = EnumSetWithAmountsCell(
        cell_id=("consultant_lobbyist_report_includes_income_by_source_type", "legal"),
        value=frozenset({"government_agency", "foundation"}),
        amounts={"government_agency": Decimal("1000"), "foundation": Decimal("500")},
    )
    assert cell.value == frozenset({"government_agency", "foundation"})
    assert cell.amounts["government_agency"] == Decimal("1000")


def test_enum_set_with_amounts_cell_rejects_unknown_source_type():
    from lobby_analysis.models_v2.cells import EnumSetWithAmountsCell

    with pytest.raises(ValidationError):
        EnumSetWithAmountsCell(
            cell_id=(
                "consultant_lobbyist_report_includes_income_by_source_type",
                "legal",
            ),
            value=frozenset({"alien_overlords"}),  # type: ignore[arg-type]
            amounts={},
        )

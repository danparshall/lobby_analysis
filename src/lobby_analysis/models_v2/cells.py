"""Compendium cell types for the v2 extraction harness.

Each cell is an immutable (frozen) Pydantic model carrying:

- `cell_id: tuple[row_id, axis]` — the canonical key from the
  `CompendiumCellSpec` registry.
- Value field(s) shaped per cell-type (e.g. `BinaryCell.value: bool`,
  `TimeThresholdCell.{magnitude, unit}`).
- Common wrapper fields: `conditional`, `condition_text`, `confidence`,
  `provenance`.

Frozen so cells round-trip iter-1's stamped-output discipline (temp-0,
no in-place mutation post-extraction).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .provenance import EvidenceSpan


class CompendiumCell(BaseModel):
    """Abstract base for every extracted compendium cell.

    Concrete subclasses add their own value field(s). Instantiation of the
    bare ABC is allowed for completeness but is never useful — every real
    cell is a typed subclass keyed in the cell-spec registry.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    cell_id: tuple[str, str]
    conditional: bool = False
    condition_text: str | None = None
    confidence: Literal["high", "medium", "low"] | None = None
    provenance: EvidenceSpan | None = None


class BinaryCell(CompendiumCell):
    """A yes/no observable about a state's disclosure regime.

    Dominant cell type in the v2 TSV (150 of 181 rows).
    """

    value: bool


class DecimalCell(CompendiumCell):
    """A monetary or other non-negative decimal threshold.

    Currency precision matters; we use Decimal (not float). Negative
    thresholds are nonsensical and rejected. `None` means "extraction ran
    and found no threshold mentioned" (distinct from "extraction not yet
    attempted," which is represented by the cell's absence from
    `StateVintageExtraction.cells`).
    """

    value: Decimal | None

    @field_validator("value")
    @classmethod
    def _value_non_negative(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("DecimalCell.value must be non-negative")
        return v


class IntCell(CompendiumCell):
    """An optional integer observable (e.g. registration_renewal_cadence in months,
    registration_deadline_days). Strict int — floats and strings do not coerce.
    """

    value: int | None


class FloatCell(CompendiumCell):
    """An optional float observable (e.g.
    `lobbyist_filing_de_minimis_threshold_time_percent`).
    """

    value: float | None


class GradedIntCell(CompendiumCell):
    """FOCAL-style 0/25/50/75/100 graded score on a practical-availability axis.

    Validator enforces the 25-step grid so downstream projection arithmetic
    can rely on the value being one of {0, 25, 50, 75, 100}.
    """

    value: int

    @field_validator("value")
    @classmethod
    def _value_on_grid(cls, v: int) -> int:
        if v < 0 or v > 100 or v % 25 != 0:
            raise ValueError(
                "GradedIntCell.value must be in {0, 25, 50, 75, 100}"
            )
        return v


class BoundedIntCell(CompendiumCell):
    """Closed-range bounded int observable.

    Used for the single TSV row `lobbying_search_simultaneous_multicriteria_capability`
    (cell_type `typed int ∈ 0..15`). Range is [0, 15] inclusive.
    """

    value: Annotated[int, Field(ge=0, le=15)]


# ---------------------------------------------------------------------------
# Generic enum + free-text cells
# ---------------------------------------------------------------------------


class EnumCell(CompendiumCell):
    """A single-valued enum observable with a per-row domain.

    Per-row enum domains are registered separately in `enum_domains.py`
    (added incrementally as each typed-enum row gets its domain pinned). A
    bare EnumCell accepts any non-empty string today; once a row's domain
    is registered the registry parser may swap in a Literal-typed subclass.
    """

    value: str


class EnumSetCell(CompendiumCell):
    """A set-valued enum observable (covers `typed Set[enum]`,
    `typed Set[enum] (8 types)`, and `typed Set[enum] (9 types)` rows).
    """

    value: frozenset[str]


class FreeTextCell(CompendiumCell):
    """Bounded-length free-text observable (e.g. `*_cadence_other_specification`
    rows). Capped at 500 chars to prevent unbounded extraction.
    """

    value: Annotated[str, Field(max_length=500)]


# ---------------------------------------------------------------------------
# Specialized cells — struct shapes user-approved 2026-05-14, sourced from
# the projection mappings in docs/historical/compendium-source-extracts/.
# ---------------------------------------------------------------------------


UpdateCadenceLiteral = Literal[
    "daily", "weekly", "monthly", "semiannual_or_less_often", "none"
]


class UpdateCadenceCell(CompendiumCell):
    """How often the state's lobbyist directory is refreshed.

    Cell type: `typed UpdateCadence` (1 row: `lobbyist_directory_update_cadence`).
    Both HG 2007 and FOCAL 2024 projection mappings converge on this enum.
    """

    value: UpdateCadenceLiteral | None


TimeUnitLiteral = Literal[
    "hours_per_quarter", "hours_per_year", "days_per_year", "percent_of_work_time"
]


class TimeThresholdCell(CompendiumCell):
    """The time-based threshold in a state's lobbyist registration definition
    (e.g. the federal LDA's 20% of work time rule).

    Cell type: `typed Optional[TimeThreshold]` (1 row:
    `time_threshold_for_lobbyist_registration`).
    Source: Newmark 2005/2017 projection mappings.
    """

    magnitude: Decimal | None
    unit: TimeUnitLiteral | None


class TimeSpentCell(CompendiumCell):
    """Time spent on lobbying as DISCLOSED in a filing (distinct from
    `TimeThresholdCell` which is the registration-triggering definitional
    threshold).

    Cell type: `typed Optional[TimeSpent]` (1 row:
    `lobbyist_or_principal_report_includes_time_spent_on_lobbying`).
    Source: FOCAL 2024 projection mapping.
    """

    magnitude: Decimal | None
    unit: TimeUnitLiteral | None


class SectorClassificationCell(CompendiumCell):
    """Sector / issue-area classification recorded on a lobbyist registration
    form. The FOCAL 2024 mapping explicitly describes this as "typed enum or
    free-text classification" — states use varied schemes (LDA's 75 issue
    codes, NAICS, ad-hoc), so the cell holds an open string. Schema-level
    constraints can be added later when a canonical scheme emerges.

    Cell type: `typed Optional[SectorClassification]` (1 row:
    `lobbyist_reg_form_includes_lobbyist_sector`).
    """

    value: str | None


class CountWithFTECell(CompendiumCell):
    """Disclosed total lobbyist count alongside FTE-equivalent figure.

    Cell type: `typed Optional[count_with_FTE]` (1 row:
    `lobbyist_or_principal_report_includes_lobbyist_count_total_and_FTE`).
    Source: FOCAL 2024 projection mapping.
    """

    count: int | None
    fte: float | None


IncomeSourceTypeLiteral = Literal[
    "government_agency", "foundation", "company", "individual", "other"
]


class EnumSetWithAmountsCell(CompendiumCell):
    """Income-by-source-type disclosure: a set of source types plus per-type
    monetary amounts.

    Cell type: `typed Set[enum] + amounts` (1 row:
    `consultant_lobbyist_report_includes_income_by_source_type`).
    Source: FOCAL 2024 Suppl Table 3 source-type enum.
    """

    value: frozenset[IncomeSourceTypeLiteral]
    amounts: dict[str, Decimal]

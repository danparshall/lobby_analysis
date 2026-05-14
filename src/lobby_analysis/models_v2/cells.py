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

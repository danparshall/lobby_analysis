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

from typing import Literal

from pydantic import BaseModel, ConfigDict

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

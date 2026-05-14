"""The compendium cell-spec registry.

`build_cell_spec_registry()` loads the v2 TSV and returns a canonical
`dict[tuple[row_id, axis], CompendiumCellSpec]` of 186 entries:

- 126 legal-only rows  → 1 entry each (axis="legal")
- 50 practical-only rows → 1 entry each (axis="practical")
- 5 legal+practical rows → 2 entries each (one per axis, each with its own
  per-axis cell class)

Total: 181 + 5 = 186 entries.

Each `CompendiumCellSpec` records the expected `CompendiumCell` subclass for
its (row_id, axis) — this is the contract Phase C's projection functions
consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from . import cells as _cells
from .cells import CompendiumCell


# ---------------------------------------------------------------------------
# CompendiumCellSpec dataclass
# ---------------------------------------------------------------------------


AxisLiteral = Literal["legal", "practical"]


@dataclass(frozen=True)
class CompendiumCellSpec:
    """Pin a (row_id, axis) tuple to the expected CompendiumCell subclass."""

    row_id: str
    axis: AxisLiteral
    expected_cell_class: type[CompendiumCell]


# ---------------------------------------------------------------------------
# cell_type → CompendiumCell subclass mapping
# ---------------------------------------------------------------------------

# Maps each distinct single-axis `cell_type` string in the TSV to its concrete
# CompendiumCell subclass. Combined-axis rows ("X (legal) + Y (practical)") are
# split first into halves and each half resolved through this table.
_CELL_TYPE_PARSER: dict[str, type[CompendiumCell]] = {
    # Binary (150 rows; dominant)
    "binary": _cells.BinaryCell,
    # Numeric
    "typed Optional[Decimal]": _cells.DecimalCell,
    "typed Optional[int]": _cells.IntCell,
    "typed int": _cells.IntCell,  # used in combined-axis "(legal)" half
    "typed Optional[float]": _cells.FloatCell,
    "typed int 0-100 step 25": _cells.GradedIntCell,
    "typed int ∈ 0..15": _cells.BoundedIntCell,
    # Enum-shaped
    "typed enum": _cells.EnumCell,
    "typed Optional[enum]": _cells.EnumCell,
    "enum": _cells.EnumCell,  # used in combined-axis halves
    "typed Set[enum]": _cells.EnumSetCell,
    "typed Set[enum] (8 types)": _cells.EnumSetCell,
    "typed Set[enum] (9 types)": _cells.EnumSetCell,
    # Free text
    "free-text": _cells.FreeTextCell,
    # Specialized (per-row cell_types user-approved 2026-05-14)
    "typed UpdateCadence": _cells.UpdateCadenceCell,
    "typed Optional[TimeThreshold]": _cells.TimeThresholdCell,
    "typed Optional[TimeSpent]": _cells.TimeSpentCell,
    "typed Optional[SectorClassification]": _cells.SectorClassificationCell,
    "typed Optional[count_with_FTE]": _cells.CountWithFTECell,
    "typed Set[enum] + amounts": _cells.EnumSetWithAmountsCell,
    # The unanticipated 7th cell_type — user-approved IntCell mapping
    # 2026-05-14 (semantic "months" is documentation; type is int | None).
    "typed Optional[int_months] (or enum)": _cells.IntCell,
}


def _resolve_cell_class(cell_type_fragment: str) -> type[CompendiumCell]:
    """Look up a single-axis cell_type fragment in the parser table.

    `cell_type_fragment` is the trimmed string from one half of a combined-axis
    row (or the whole `cell_type` value for a single-axis row), with any
    " (legal)" / " (practical)" suffix already stripped by the caller.
    """
    if cell_type_fragment not in _CELL_TYPE_PARSER:
        raise KeyError(
            f"No CompendiumCell subclass registered for cell_type "
            f"fragment {cell_type_fragment!r}; update _CELL_TYPE_PARSER in "
            f"src/lobby_analysis/models_v2/cell_spec.py."
        )
    return _CELL_TYPE_PARSER[cell_type_fragment]


def _strip_axis_suffix(fragment: str) -> str:
    """Strip a trailing ` (legal)` or ` (practical)` suffix, if present."""
    stripped = fragment.strip()
    for suffix in (" (legal)", " (practical)"):
        if stripped.endswith(suffix):
            return stripped[: -len(suffix)].strip()
    return stripped


def _parse_combined_cell_type(
    cell_type: str,
) -> tuple[type[CompendiumCell], type[CompendiumCell]]:
    """Parse a combined-axis cell_type string into (legal_class, practical_class).

    Handles strings of the form ``X (legal) + Y (practical)`` (and the
    semantically-equivalent ``Y (practical) + X (legal)``).
    """
    halves = [h.strip() for h in cell_type.split(" + ")]
    if len(halves) != 2:
        raise ValueError(
            f"Expected exactly two ' + '-separated halves in combined "
            f"cell_type {cell_type!r}; got {len(halves)}."
        )

    legal_class: type[CompendiumCell] | None = None
    practical_class: type[CompendiumCell] | None = None
    for half in halves:
        bare = _strip_axis_suffix(half)
        cls = _resolve_cell_class(bare)
        if half.endswith("(legal)"):
            legal_class = cls
        elif half.endswith("(practical)"):
            practical_class = cls
        else:
            raise ValueError(
                f"Combined-axis half {half!r} in cell_type {cell_type!r} "
                f"missing required '(legal)' or '(practical)' suffix."
            )

    if legal_class is None or practical_class is None:
        raise ValueError(
            f"Combined cell_type {cell_type!r} did not yield both legal and practical halves."
        )
    return legal_class, practical_class


# ---------------------------------------------------------------------------
# Public registry builder
# ---------------------------------------------------------------------------


def build_cell_spec_registry() -> dict[tuple[str, AxisLiteral], CompendiumCellSpec]:
    """Build the canonical 186-entry cell-spec registry from the v2 TSV.

    Calls `load_v2_compendium()` for the raw rows, walks each row, parses
    its `cell_type` + `axis` columns, and emits 1 or 2 entries per row.
    """
    # Local import: compendium_loader lives in the same package and imports
    # are otherwise circular if pulled at module-import time.
    from lobby_analysis.compendium_loader import load_v2_compendium

    registry: dict[tuple[str, AxisLiteral], CompendiumCellSpec] = {}
    for row in load_v2_compendium():
        row_id = row["compendium_row_id"]
        cell_type = row["cell_type"]
        axis = row["axis"]

        if axis == "legal":
            cls = _resolve_cell_class(_strip_axis_suffix(cell_type))
            registry[(row_id, "legal")] = CompendiumCellSpec(
                row_id=row_id, axis="legal", expected_cell_class=cls
            )
        elif axis == "practical":
            cls = _resolve_cell_class(_strip_axis_suffix(cell_type))
            registry[(row_id, "practical")] = CompendiumCellSpec(
                row_id=row_id, axis="practical", expected_cell_class=cls
            )
        elif axis == "legal+practical":
            legal_cls, practical_cls = _parse_combined_cell_type(cell_type)
            registry[(row_id, "legal")] = CompendiumCellSpec(
                row_id=row_id, axis="legal", expected_cell_class=legal_cls
            )
            registry[(row_id, "practical")] = CompendiumCellSpec(
                row_id=row_id, axis="practical", expected_cell_class=practical_cls
            )
        else:
            raise ValueError(
                f"Row {row_id!r} has unknown axis {axis!r}; expected one of "
                f"'legal', 'practical', 'legal+practical'."
            )
    return registry

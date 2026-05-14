"""Public exports for the v2 typed compendium cell model layer.

This module is the contract Phase C's projection functions and the extraction
harness consume. v1.1 at `src/lobby_analysis/models/` is parallel and remains
the contract for `cmd_build_smr` + the existing v1 tests; the two coexist
until v1.1 is retired by Phase C.
"""

from __future__ import annotations

from .cell_spec import CompendiumCellSpec, build_cell_spec_registry
from .cells import (
    BinaryCell,
    BoundedIntCell,
    CompendiumCell,
    CountWithFTECell,
    DecimalCell,
    EnumCell,
    EnumSetCell,
    EnumSetWithAmountsCell,
    FloatCell,
    FreeTextCell,
    GradedIntCell,
    IntCell,
    SectorClassificationCell,
    TimeSpentCell,
    TimeThresholdCell,
    UpdateCadenceCell,
)
from .extraction import ExtractionRun, StateVintageExtraction
from .provenance import EvidenceSpan

__all__ = [
    "BinaryCell",
    "BoundedIntCell",
    "CompendiumCell",
    "CompendiumCellSpec",
    "CountWithFTECell",
    "DecimalCell",
    "EnumCell",
    "EnumSetCell",
    "EnumSetWithAmountsCell",
    "EvidenceSpan",
    "ExtractionRun",
    "FloatCell",
    "FreeTextCell",
    "GradedIntCell",
    "IntCell",
    "SectorClassificationCell",
    "StateVintageExtraction",
    "TimeSpentCell",
    "TimeThresholdCell",
    "UpdateCadenceCell",
    "build_cell_spec_registry",
]

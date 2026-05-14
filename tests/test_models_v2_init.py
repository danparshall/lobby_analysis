"""Tests for `lobby_analysis.models_v2`'s public exports (Phase 7)."""

from __future__ import annotations


def test_models_v2_public_exports_resolve():
    """All public names listed in the plan must be importable from the
    top-level `lobby_analysis.models_v2` package.
    """
    from lobby_analysis.models_v2 import (
        BinaryCell,
        BoundedIntCell,
        CompendiumCell,
        CompendiumCellSpec,
        CountWithFTECell,
        DecimalCell,
        EnumCell,
        EnumSetCell,
        EnumSetWithAmountsCell,
        EvidenceSpan,
        ExtractionRun,
        FloatCell,
        FreeTextCell,
        GradedIntCell,
        IntCell,
        SectorClassificationCell,
        StateVintageExtraction,
        TimeSpentCell,
        TimeThresholdCell,
        UpdateCadenceCell,
        build_cell_spec_registry,
    )

    # Sanity: every imported name is non-None (catches accidentally setting an
    # export to None during a refactor).
    for name in (
        BinaryCell,
        BoundedIntCell,
        CompendiumCell,
        CompendiumCellSpec,
        CountWithFTECell,
        DecimalCell,
        EnumCell,
        EnumSetCell,
        EnumSetWithAmountsCell,
        EvidenceSpan,
        ExtractionRun,
        FloatCell,
        FreeTextCell,
        GradedIntCell,
        IntCell,
        SectorClassificationCell,
        StateVintageExtraction,
        TimeSpentCell,
        TimeThresholdCell,
        UpdateCadenceCell,
        build_cell_spec_registry,
    ):
        assert name is not None

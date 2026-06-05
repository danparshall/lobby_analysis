"""Tests for `lobby_analysis.compendium_loader.load_v2_compendium_typed`
(Phase 7) — the typed wrapper around the registry.
"""

from __future__ import annotations


def test_load_v2_compendium_typed_returns_186_specs():
    """The typed loader returns a list of 186 CompendiumCellSpec entries
    (one per (row_id, axis) combination) — same shape as build_cell_spec_registry()
    but as a list, for downstream consumers who want a sequence rather than a dict.
    """
    from lobby_analysis.compendium_loader import load_v2_compendium_typed
    from lobby_analysis.models_v2.cell_spec import CompendiumCellSpec

    specs = load_v2_compendium_typed()
    assert isinstance(specs, list)
    assert len(specs) == 186
    assert all(isinstance(s, CompendiumCellSpec) for s in specs)

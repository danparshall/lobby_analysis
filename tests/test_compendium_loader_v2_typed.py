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


def test_typed_loader_carries_prompt_for_narrow_pass_anchor_row():
    """Each typed spec for a narrow-pass row carries the YAML-sourced
    ``prompt`` field — proves the typed wrapper picks up the registry's
    YAML-backed plumbing end-to-end, not just the raw TSV row shape.

    Pattern A anchor row (``lobbyist_spending_report_required``) appears
    twice in the typed list (legal-only here, so once). It must have a
    non-empty ``prompt``."""
    from lobby_analysis.compendium_loader import load_v2_compendium_typed

    specs = load_v2_compendium_typed()
    anchors = [s for s in specs if s.row_id == "lobbyist_spending_report_required"]
    assert anchors, "anchor row missing from typed loader"
    for spec in anchors:
        assert spec.prompt is not None, (
            f"typed spec ({spec.row_id!r}, {spec.axis!r}) has prompt=None; "
            "expected non-empty YAML-sourced prompt after Commit 1 migration"
        )
        assert spec.prompt, f"typed spec ({spec.row_id!r}, {spec.axis!r}) has empty prompt"

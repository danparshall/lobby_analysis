"""Tests for `build_chunks()` against the real `CompendiumCellSpec` registry.

These tests are the partition-invariant enforcement: every cell in exactly one
chunk, both halves of combined-axis rows in the same chunk, `axis_summary`
matches actual cells, and downstream coupling errors (missing rows, missing
manifest coverage) raise loudly.
"""

from __future__ import annotations

from collections import defaultdict

import pytest


# Per Q3 brainstorm lock: both halves of these rows must land in the same chunk.
COMBINED_AXIS_ROWS = (
    "lobbyist_registration_required",
    "lobbyist_spending_report_filing_cadence",
    "lobbying_disclosure_audit_required_in_law",
    "lobbying_violation_penalties_imposed_in_practice",
    "lobbyist_registration_deadline_days_after_first_lobbying",
)


# ---------------------------------------------------------------------------
# Real-registry behavior
# ---------------------------------------------------------------------------


def test_build_chunks_returns_one_chunk_per_manifest_entry():
    from lobby_analysis.chunks_v2 import CHUNKS_V2, Chunk, build_chunks

    chunks = build_chunks()
    assert isinstance(chunks, list)
    assert len(chunks) == len(CHUNKS_V2)
    for c in chunks:
        assert isinstance(c, Chunk)


def test_build_chunks_partitions_full_registry():
    """Every (row_id, axis) in the 186-cell registry appears in exactly one
    chunk's cell_specs."""
    from lobby_analysis.chunks_v2 import build_chunks
    from lobby_analysis.models_v2 import build_cell_spec_registry

    registry = build_cell_spec_registry()
    all_keys = set(registry.keys())

    covered: set[tuple[str, str]] = set()
    for chunk in build_chunks():
        for spec in chunk.cell_specs:
            key = (spec.row_id, spec.axis)
            assert key not in covered, f"Duplicate cell coverage: {key}"
            covered.add(key)

    assert covered == all_keys, (
        f"missing from chunks: {sorted(all_keys - covered)[:5]}; "
        f"unexpected in chunks: {sorted(covered - all_keys)[:5]}"
    )


def test_combined_axis_rows_land_in_same_chunk():
    """Q3 lock: each of the 5 combined-axis rows has both its legal and
    practical halves in one chunk."""
    from lobby_analysis.chunks_v2 import build_chunks

    chunks_by_row_id: dict[str, set[str]] = defaultdict(set)
    for chunk in build_chunks():
        for spec in chunk.cell_specs:
            chunks_by_row_id[spec.row_id].add(chunk.chunk_id)

    for row_id in COMBINED_AXIS_ROWS:
        assigned = chunks_by_row_id[row_id]
        assert len(assigned) == 1, f"{row_id!r} split across chunks: {assigned}"


def test_axis_summary_matches_actual_cells():
    """`axis_summary` is derived by `build_chunks()` from the actual cells it
    resolved; tests assert the derivation is `legal` / `practical` / `mixed`."""
    from lobby_analysis.chunks_v2 import build_chunks

    for chunk in build_chunks():
        axes = {spec.axis for spec in chunk.cell_specs}
        if axes == {"legal"}:
            assert chunk.axis_summary == "legal", chunk.chunk_id
        elif axes == {"practical"}:
            assert chunk.axis_summary == "practical", chunk.chunk_id
        else:
            assert chunk.axis_summary == "mixed", (chunk.chunk_id, axes)


def test_build_chunks_ordering_stable():
    """Two calls return the same chunks in the same order."""
    from lobby_analysis.chunks_v2 import build_chunks

    first = [c.chunk_id for c in build_chunks()]
    second = [c.chunk_id for c in build_chunks()]
    assert first == second


# ---------------------------------------------------------------------------
# Anchor chunks (brainstorm carry-forward continuity)
# ---------------------------------------------------------------------------


def test_anchor_chunk_lobbying_definitions_members():
    """Iter-1 carry-forward: the v2 `lobbying_definitions` chunk is the spiritual
    successor to iter-1's 7-row `definitions` chunk. Must contain all 6
    `def_target_*` rows and both `def_actor_class_*` rows."""
    from lobby_analysis.chunks_v2 import build_chunks

    by_id = {c.chunk_id: c for c in build_chunks()}
    chunk = by_id["lobbying_definitions"]
    row_ids = {spec.row_id for spec in chunk.cell_specs}

    expected_targets = {
        "def_target_executive_agency",
        "def_target_executive_staff",
        "def_target_governors_office",
        "def_target_independent_agency",
        "def_target_legislative_branch",
        "def_target_legislative_staff",
    }
    expected_actor_classes = {
        "def_actor_class_elected_officials",
        "def_actor_class_public_employees",
    }
    assert expected_targets <= row_ids, expected_targets - row_ids
    assert expected_actor_classes <= row_ids, expected_actor_classes - row_ids


def test_anchor_chunk_lobbyist_spending_report_has_thirtyfour_rows():
    """Per the user's approval that the spending-report cluster stays a single
    chunk: all 34 distinct `lobbyist_spending_*` rows + the combined-axis
    `lobbyist_spending_report_filing_cadence` belong here."""
    from lobby_analysis.chunks_v2 import build_chunks

    by_id = {c.chunk_id: c for c in build_chunks()}
    chunk = by_id["lobbyist_spending_report"]
    distinct_row_ids = {spec.row_id for spec in chunk.cell_specs}
    assert len(distinct_row_ids) == 34, (
        f"`lobbyist_spending_report` has {len(distinct_row_ids)} distinct row_ids; expected 34"
    )


# ---------------------------------------------------------------------------
# Dependency injection + error paths (synthetic registries)
# ---------------------------------------------------------------------------


def _synthetic_spec(row_id: str, axis: str):
    from lobby_analysis.models_v2 import BinaryCell, CompendiumCellSpec

    return CompendiumCellSpec(row_id=row_id, axis=axis, expected_cell_class=BinaryCell)


def test_build_chunks_accepts_injected_registry_and_manifest():
    """`build_chunks(registry=..., manifest=...)` runs against a synthetic
    universe so we can isolate resolution logic from the real TSV."""
    from lobby_analysis.chunks_v2 import ChunkDef, build_chunks

    registry = {
        ("row_a", "legal"): _synthetic_spec("row_a", "legal"),
        ("row_b", "practical"): _synthetic_spec("row_b", "practical"),
        ("row_c", "legal"): _synthetic_spec("row_c", "legal"),
        ("row_c", "practical"): _synthetic_spec("row_c", "practical"),
    }
    manifest = (
        ChunkDef(chunk_id="legal_chunk", topic="t", member_row_ids=("row_a",)),
        ChunkDef(chunk_id="practical_chunk", topic="t", member_row_ids=("row_b",)),
        ChunkDef(chunk_id="combined_chunk", topic="t", member_row_ids=("row_c",)),
    )
    chunks = build_chunks(registry=registry, manifest=manifest)

    by_id = {c.chunk_id: c for c in chunks}
    assert by_id["legal_chunk"].axis_summary == "legal"
    assert by_id["practical_chunk"].axis_summary == "practical"
    # row_c is a combined-axis row (both halves in registry) → both land in one chunk → mixed.
    assert by_id["combined_chunk"].axis_summary == "mixed"
    combined_keys = {(s.row_id, s.axis) for s in by_id["combined_chunk"].cell_specs}
    assert combined_keys == {("row_c", "legal"), ("row_c", "practical")}


def test_build_chunks_raises_when_manifest_references_unknown_row_id():
    """If a `ChunkDef` names a row_id the registry doesn't know about, surface
    loudly — that means the TSV has shrunk or the manifest has a typo."""
    from lobby_analysis.chunks_v2 import ChunkDef, build_chunks

    registry = {("row_a", "legal"): _synthetic_spec("row_a", "legal")}
    manifest = (ChunkDef(chunk_id="anchor", topic="t", member_row_ids=("row_a", "bogus_row")),)
    with pytest.raises((KeyError, ValueError)):
        build_chunks(registry=registry, manifest=manifest)


def test_build_chunks_raises_when_manifest_misses_registry_rows():
    """If the registry has cells the manifest doesn't cover, surface loudly —
    that means the TSV has grown since the manifest was authored."""
    from lobby_analysis.chunks_v2 import ChunkDef, build_chunks

    registry = {
        ("row_a", "legal"): _synthetic_spec("row_a", "legal"),
        ("row_b", "legal"): _synthetic_spec("row_b", "legal"),
    }
    manifest = (ChunkDef(chunk_id="anchor", topic="t", member_row_ids=("row_a",)),)
    with pytest.raises(ValueError):
        build_chunks(registry=registry, manifest=manifest)

"""Tests for the `Chunk` and `ChunkDef` frozen dataclasses in
`lobby_analysis.chunks_v2`.

These tests cover construction, immutability, and `__post_init__` validation
in isolation — no manifest, no registry. Coverage / partition invariants are
tested in `test_chunks_build.py`.
"""

from __future__ import annotations

import dataclasses

import pytest


# ---------------------------------------------------------------------------
# Chunk dataclass
# ---------------------------------------------------------------------------


def _make_spec(row_id: str = "law_includes_materiality_test", axis: str = "legal"):
    """Helper: build a real `CompendiumCellSpec` from the v2 cell-model layer."""
    from lobby_analysis.models_v2 import BinaryCell, CompendiumCellSpec

    return CompendiumCellSpec(row_id=row_id, axis=axis, expected_cell_class=BinaryCell)


def test_chunk_constructs_with_valid_fields():
    from lobby_analysis.chunks_v2 import Chunk

    spec = _make_spec()
    chunk = Chunk(
        chunk_id="lobbying_definitions",
        topic="What counts as lobbying or a lobbyist",
        cell_specs=(spec,),
        axis_summary="legal",
        notes=None,
    )
    assert chunk.chunk_id == "lobbying_definitions"
    assert chunk.topic == "What counts as lobbying or a lobbyist"
    assert chunk.cell_specs == (spec,)
    assert chunk.axis_summary == "legal"
    assert chunk.notes is None


def test_chunk_is_frozen():
    from lobby_analysis.chunks_v2 import Chunk

    chunk = Chunk(
        chunk_id="anchor",
        topic="topic",
        cell_specs=(_make_spec(),),
        axis_summary="legal",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.chunk_id = "other"  # type: ignore[misc]


def test_chunk_rejects_list_for_cell_specs():
    """`cell_specs` must be a tuple; a list slips through `@dataclass(frozen=True)`
    without `__post_init__` enforcement, and would break downstream consumers
    that rely on hashability/immutability of `cell_specs`."""
    from lobby_analysis.chunks_v2 import Chunk

    with pytest.raises((TypeError, ValueError)):
        Chunk(
            chunk_id="anchor",
            topic="topic",
            cell_specs=[_make_spec()],  # type: ignore[arg-type]
            axis_summary="legal",
        )


def test_chunk_rejects_empty_cell_specs():
    from lobby_analysis.chunks_v2 import Chunk

    with pytest.raises(ValueError):
        Chunk(
            chunk_id="anchor",
            topic="topic",
            cell_specs=(),
            axis_summary="legal",
        )


def test_chunk_rejects_unknown_axis_summary():
    from lobby_analysis.chunks_v2 import Chunk

    with pytest.raises(ValueError):
        Chunk(
            chunk_id="anchor",
            topic="topic",
            cell_specs=(_make_spec(),),
            axis_summary="banana",
        )


# ---------------------------------------------------------------------------
# ChunkDef dataclass (manifest-author-time struct)
# ---------------------------------------------------------------------------


def test_chunkdef_basics():
    """`ChunkDef` parallels `Chunk` but carries `member_row_ids: tuple[str, ...]`
    rather than resolved cell specs. Exercises construction, frozen-ness, and
    its three `__post_init__` validation paths."""
    from lobby_analysis.chunks_v2 import ChunkDef

    # 1. Valid construction succeeds with all expected fields.
    cdef = ChunkDef(
        chunk_id="anchor_chunk",
        topic="topic",
        member_row_ids=("row_a", "row_b"),
        notes="ok",
    )
    assert cdef.chunk_id == "anchor_chunk"
    assert cdef.member_row_ids == ("row_a", "row_b")
    assert cdef.notes == "ok"

    # 2. Frozen.
    with pytest.raises(dataclasses.FrozenInstanceError):
        cdef.chunk_id = "other"  # type: ignore[misc]

    # 3. `member_row_ids` must be a tuple, not a list.
    with pytest.raises((TypeError, ValueError)):
        ChunkDef(
            chunk_id="anchor_chunk",
            topic="topic",
            member_row_ids=["row_a"],  # type: ignore[arg-type]
        )

    # 4. Empty `member_row_ids` raises.
    with pytest.raises(ValueError):
        ChunkDef(
            chunk_id="anchor_chunk",
            topic="topic",
            member_row_ids=(),
        )

    # 5. `chunk_id` must be snake_case ASCII (starts with [a-z], rest [a-z0-9_]).
    for bad in ("BadCaps", "1starts_with_digit", "has-dash", "has space"):
        with pytest.raises(ValueError):
            ChunkDef(
                chunk_id=bad,
                topic="topic",
                member_row_ids=("row_a",),
            )

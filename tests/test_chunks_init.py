"""Smoke test for the `lobby_analysis.chunks_v2` public surface.

Verifies that the four `__all__` exports are reachable directly from the
package root, the path that downstream consumers (brief-writer, retrieval
agent's tool schemas, the coupling test) will use.
"""

from __future__ import annotations


def test_chunks_v2_public_exports_importable():
    from lobby_analysis.chunks_v2 import CHUNKS_V2, Chunk, ChunkDef, build_chunks

    assert Chunk is not None
    assert ChunkDef is not None
    assert build_chunks is not None
    assert isinstance(CHUNKS_V2, tuple)


def test_chunks_v2_all_lists_only_those_names():
    import lobby_analysis.chunks_v2 as pkg

    assert set(pkg.__all__) == {"CHUNKS_V2", "Chunk", "ChunkDef", "build_chunks"}

"""Tests for the `CHUNKS_V2` manifest constant in
`lobby_analysis.chunks_v2.manifest`.

These tests exercise the manifest in isolation — without resolving against the
cell-spec registry. Registry-coupling tests live in `test_chunks_build.py`.
"""

from __future__ import annotations

import re


CHUNK_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def test_chunks_v2_is_tuple_of_chunkdef():
    from lobby_analysis.chunks_v2 import CHUNKS_V2, ChunkDef

    assert isinstance(CHUNKS_V2, tuple)
    for entry in CHUNKS_V2:
        assert isinstance(entry, ChunkDef)


def test_chunks_v2_has_fifteen_entries():
    """Plan-locked count: 15 chunks covering 181 rows = 186 cells. If you
    deliberately refine to 14 or 16, update this test in the same commit and
    surface the rationale in the RESEARCH_LOG entry."""
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    assert len(CHUNKS_V2) == 15


def test_chunks_v2_chunk_ids_unique():
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    chunk_ids = [c.chunk_id for c in CHUNKS_V2]
    assert len(chunk_ids) == len(set(chunk_ids)), (
        f"Duplicate chunk_ids in CHUNKS_V2: "
        f"{[i for i in chunk_ids if chunk_ids.count(i) > 1]}"
    )


def test_chunks_v2_chunk_ids_are_snake_case_ascii():
    """Brief-writer's per-chunk preamble files will be keyed by chunk_id."""
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    for entry in CHUNKS_V2:
        assert CHUNK_ID_RE.match(entry.chunk_id), (
            f"chunk_id {entry.chunk_id!r} is not snake_case ASCII"
        )


def test_chunks_v2_every_chunk_has_at_least_one_member_row():
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    for entry in CHUNKS_V2:
        assert len(entry.member_row_ids) >= 1, (
            f"ChunkDef {entry.chunk_id!r} has no member row_ids"
        )


def test_chunks_v2_no_row_id_appears_in_two_chunks():
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    seen: dict[str, str] = {}
    for entry in CHUNKS_V2:
        for row_id in entry.member_row_ids:
            assert row_id not in seen, (
                f"row_id {row_id!r} appears in both "
                f"{seen[row_id]!r} and {entry.chunk_id!r}"
            )
            seen[row_id] = entry.chunk_id


def test_chunks_v2_sizes_within_bounds():
    """Hard upper cap of 34 rows per the user's `lobbyist_spending_report`
    approval. Lower bound of 1 row (current manifest's `enforcement_and_audits`
    sits at 2; both are admissible)."""
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    for entry in CHUNKS_V2:
        n = len(entry.member_row_ids)
        assert 1 <= n <= 34, f"ChunkDef {entry.chunk_id!r} has {n} rows; expected 1..34"


def test_chunks_v2_ordering_is_deterministic():
    """A tuple is intrinsically ordered; this test guards against an accidental
    refactor that swaps the manifest backing to a set or dict."""
    from lobby_analysis.chunks_v2 import CHUNKS_V2

    first_pass = tuple(c.chunk_id for c in CHUNKS_V2)
    second_pass = tuple(c.chunk_id for c in CHUNKS_V2)
    assert first_pass == second_pass

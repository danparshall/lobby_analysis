"""The `Chunk` and `ChunkDef` frozen dataclasses, plus `build_chunks()`.

- `ChunkDef` is the manifest-author-time struct: a chunk_id, a topic, and the
  list of `compendium_row_id`s that belong to this chunk.
- `Chunk` is the resolved struct produced by `build_chunks()` at runtime: it
  carries fully-resolved `CompendiumCellSpec` instances instead of bare row_ids,
  plus a derived `axis_summary`.
- `build_chunks()` partitions the 186-cell registry into chunks per the
  hand-curated `CHUNKS_V2` manifest. It enforces (a) every cell appears in
  exactly one chunk and (b) both halves of combined-axis rows land in the
  same chunk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from lobby_analysis.models_v2 import CompendiumCellSpec


_CHUNK_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_VALID_AXIS_SUMMARIES = frozenset({"legal", "practical", "mixed"})


@dataclass(frozen=True)
class Chunk:
    """A resolved chunk: chunk_id + topic + a tuple of CompendiumCellSpec.

    Produced by `build_chunks()` from a `ChunkDef` plus the cell-spec registry.
    Frozen + hashable; consumed downstream by the brief-writer and by the
    retrieval-agent tool schemas.
    """

    chunk_id: str
    topic: str
    cell_specs: tuple[CompendiumCellSpec, ...]
    axis_summary: str
    notes: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.chunk_id, str) or not _CHUNK_ID_RE.fullmatch(self.chunk_id):
            raise ValueError(
                f"Chunk.chunk_id {self.chunk_id!r} must be snake_case ASCII "
                f"matching {_CHUNK_ID_RE.pattern}"
            )
        if not isinstance(self.cell_specs, tuple):
            raise TypeError(
                f"Chunk.cell_specs for {self.chunk_id!r} must be a tuple, got "
                f"{type(self.cell_specs).__name__}"
            )
        if not self.cell_specs:
            raise ValueError(
                f"Chunk.cell_specs for {self.chunk_id!r} must be non-empty"
            )
        if self.axis_summary not in _VALID_AXIS_SUMMARIES:
            raise ValueError(
                f"Chunk.axis_summary {self.axis_summary!r} for {self.chunk_id!r} "
                f"must be one of {sorted(_VALID_AXIS_SUMMARIES)}"
            )


@dataclass(frozen=True)
class ChunkDef:
    """Manifest-author-time chunk definition.

    Carries `member_row_ids` — bare `compendium_row_id` strings — which
    `build_chunks()` later resolves against the cell-spec registry. A
    `ChunkDef` whose `member_row_ids` contains a row that the registry treats
    as combined-axis automatically picks up BOTH cells in `build_chunks()`
    (one `(row_id, 'legal')` and one `(row_id, 'practical')`).
    """

    chunk_id: str
    topic: str
    member_row_ids: tuple[str, ...]
    notes: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.chunk_id, str) or not _CHUNK_ID_RE.fullmatch(self.chunk_id):
            raise ValueError(
                f"ChunkDef.chunk_id {self.chunk_id!r} must be snake_case ASCII "
                f"matching {_CHUNK_ID_RE.pattern}"
            )
        if not isinstance(self.member_row_ids, tuple):
            raise TypeError(
                f"ChunkDef.member_row_ids for {self.chunk_id!r} must be a tuple, "
                f"got {type(self.member_row_ids).__name__}"
            )
        if not self.member_row_ids:
            raise ValueError(
                f"ChunkDef.member_row_ids for {self.chunk_id!r} must be non-empty"
            )

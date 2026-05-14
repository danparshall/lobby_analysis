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

from lobby_analysis.models_v2 import CompendiumCellSpec, build_cell_spec_registry


_CHUNK_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_VALID_AXIS_SUMMARIES = frozenset({"legal", "practical", "mixed"})
_AXES: tuple[str, str] = ("legal", "practical")


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


def build_chunks(
    registry: dict[tuple[str, str], CompendiumCellSpec] | None = None,
    manifest: tuple[ChunkDef, ...] | None = None,
) -> list[Chunk]:
    """Resolve `manifest` (default: `CHUNKS_V2`) against `registry` (default:
    the canonical 186-cell registry built from the v2 TSV) into a `list[Chunk]`.

    Enforces:

    - Every `(row_id, axis)` in `registry` appears in exactly one resulting
      chunk's `cell_specs`. Cells missing from the manifest raise `ValueError`.
    - Cells appearing in two different chunks raise `ValueError`.
    - A `ChunkDef.member_row_ids` entry that the registry doesn't know about
      raises `KeyError`.

    A combined-axis row (i.e., a `row_id` present in `registry` under BOTH
    `"legal"` and `"practical"`) contributes both cells to the chunk that
    names it — both halves co-locate per the brainstorm's Q3 lock.

    The returned `Chunk.axis_summary` is derived from the actual axes of the
    chunk's resolved cells: `"legal"`, `"practical"`, or `"mixed"`.
    """
    if registry is None:
        registry = build_cell_spec_registry()
    if manifest is None:
        # Lazy import: manifest.py imports ChunkDef from this module, so the
        # default cannot be resolved at module-load time without a cycle.
        from .manifest import CHUNKS_V2

        manifest = CHUNKS_V2

    chunks: list[Chunk] = []
    seen_keys: set[tuple[str, str]] = set()
    for chunk_def in manifest:
        cell_specs: list[CompendiumCellSpec] = []
        axes_in_chunk: set[str] = set()
        for row_id in chunk_def.member_row_ids:
            matched_keys = [(row_id, ax) for ax in _AXES if (row_id, ax) in registry]
            if not matched_keys:
                raise KeyError(
                    f"ChunkDef {chunk_def.chunk_id!r}: row_id {row_id!r} "
                    f"not present in registry under either axis"
                )
            for key in matched_keys:
                if key in seen_keys:
                    raise ValueError(
                        f"Cell {key} assigned to multiple chunks "
                        f"(latest: {chunk_def.chunk_id!r})"
                    )
                seen_keys.add(key)
                cell_specs.append(registry[key])
                axes_in_chunk.add(key[1])

        if axes_in_chunk == {"legal"}:
            axis_summary = "legal"
        elif axes_in_chunk == {"practical"}:
            axis_summary = "practical"
        else:
            axis_summary = "mixed"

        chunks.append(
            Chunk(
                chunk_id=chunk_def.chunk_id,
                topic=chunk_def.topic,
                cell_specs=tuple(cell_specs),
                axis_summary=axis_summary,
                notes=chunk_def.notes,
            )
        )

    missing = set(registry.keys()) - seen_keys
    if missing:
        sample = sorted(missing)[:5]
        suffix = "..." if len(missing) > 5 else ""
        raise ValueError(
            f"Cells in registry not covered by manifest "
            f"({len(missing)} missing): {sample}{suffix}"
        )
    return chunks

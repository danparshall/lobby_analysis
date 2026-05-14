"""Hand-curated chunk manifest for the extraction-harness retrieval agent.

Partitions the 186-cell `CompendiumCellSpec` registry into ~15 topic-coherent
chunks. See `docs/active/extraction-harness-brainstorm/plans/20260514_chunks_implementation_plan.md`
for the design.
"""

from __future__ import annotations

from .chunks import Chunk, ChunkDef, build_chunks
from .manifest import CHUNKS_V2

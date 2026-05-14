# `lobby_analysis.chunks_v2`

Partitions the 186-cell `CompendiumCellSpec` registry into 15 topic-coherent chunks for the v2 extraction harness's per-chunk prompt dispatch.

## Public surface

```python
from lobby_analysis.chunks_v2 import Chunk, ChunkDef, build_chunks, CHUNKS_V2
```

- **`Chunk`** — frozen dataclass produced by `build_chunks()`. Carries `chunk_id`, `topic`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary` (`"legal"` / `"practical"` / `"mixed"`), and optional `notes`. `__post_init__` enforces immutability invariants.
- **`ChunkDef`** — frozen dataclass authored by humans in `manifest.py`. Carries `chunk_id`, `topic`, `member_row_ids: tuple[str, ...]`, optional `notes`. Resolved into a `Chunk` at `build_chunks()` call time by looking each `member_row_id` up in the cell-spec registry.
- **`build_chunks(registry=None, manifest=None) -> list[Chunk]`** — resolves a manifest (default: `CHUNKS_V2`) against a registry (default: `build_cell_spec_registry()` from `lobby_analysis.models_v2`). Enforces the partition invariant: every `(row_id, axis)` in the registry appears in exactly one chunk. Raises `KeyError` if the manifest names a row the registry doesn't know; raises `ValueError` if the registry has cells the manifest doesn't cover or if a cell ends up assigned to two chunks.
- **`CHUNKS_V2: tuple[ChunkDef, ...]`** — the hand-curated 15-chunk manifest covering the 181 v2 TSV rows = 186 cells.

## The 15 chunks

| chunk_id | rows | axis_summary | notes |
|----------|-----:|--------------|-------|
| `lobbying_definitions` | 15 | mixed | Iter-1 carry-forward. TARGET / ACTOR / THRESHOLD-qualitative sub-axes. |
| `actor_registration_required` | 11 | legal | All `actor_*_registration_required` rows. |
| `registration_thresholds` | 6 | legal | Quantitative gates: compensation, expenditure, time, de-minimis. |
| `registration_mechanics_and_exemptions` | 8 | mixed | Contains 2 combined-axis rows. |
| `lobbyist_registration_form_contents` | 13 | legal | All `lobbyist_reg_form_includes_*` rows. |
| `lobbyist_spending_report` | 34 | mixed | Largest chunk; user-approved single chunk for the spending-report cluster. 1 combined-axis row. |
| `principal_spending_report` | 23 | legal | Lobbyist-employer-side spending report. |
| `lobbying_contact_log` | 9 | legal | Per-meeting record fields. |
| `other_lobbyist_filings` | 12 | legal | Catch-all for filing rows not in the two big spending-report chunks. |
| `enforcement_and_audits` | 2 | mixed | Both rows are combined-axis → 4 cells. |
| `search_portal_capabilities` | 16 | practical | All `lobbying_search_*` rows. |
| `data_quality_and_access` | 10 | practical | Portal data quality + format + downloadability. |
| `disclosure_documents_online` | 5 | practical | Online accessibility of disclosure documents. |
| `lobbyist_directory_and_website` | 9 | practical | Directory format + parent website. |
| `oversight_and_government_subjects` | 8 | mixed | Oversight-agency activity + government-as-disclosure-subject rows. |

Total: 181 row slots → 186 cells (5 combined-axis rows contribute 2 cells each).

## Invariants

- **Every cell in exactly one chunk.** Enforced by `build_chunks()` and by `test_chunks_build.py::test_build_chunks_partitions_full_registry`.
- **Combined-axis rows are co-located.** Both halves of all 5 combined-axis rows ride in the same chunk per Q3 of the chunks brainstorm. Enforced by `test_combined_axis_rows_land_in_same_chunk`.
- **`chunk_id` is snake_case ASCII matching `^[a-z][a-z0-9_]*$`.** Required because brief-writer preamble files are keyed by `chunk_id` and need filesystem-safe names.
- **Chunk sizes are bounded `[1, 34]`.** Hard upper cap of 34 corresponds to `lobbyist_spending_report`'s natural cluster size.

## Provenance

- Design: [`docs/active/extraction-harness-brainstorm/convos/20260514_chunks_brainstorm.md`](../../../docs/active/extraction-harness-brainstorm/convos/20260514_chunks_brainstorm.md)
- Implementation plan: [`docs/active/extraction-harness-brainstorm/plans/20260514_chunks_implementation_plan.md`](../../../docs/active/extraction-harness-brainstorm/plans/20260514_chunks_implementation_plan.md)
- Implementation convo: [`docs/active/extraction-harness-brainstorm/convos/20260514_chunks_implementation.md`](../../../docs/active/extraction-harness-brainstorm/convos/20260514_chunks_implementation.md)
- Row-freeze contract: [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv)

## Downstream consumers

- `src/lobby_analysis/retrieval_v2/tools.py` — `CROSS_REFERENCE_TOOL.chunk_ids_affected.enum` will source from `build_chunks()`; coupling test asserts the tool schema enum matches the manifest's chunk_ids exactly.
- `src/lobby_analysis/retrieval_v2/brief_writer.py` — `build_retrieval_brief()` looks up cell rosters by chunk_id via `build_chunks()`.
- Future brief-writer module (separate component) will key per-chunk preamble files by `chunk_id`.

## What this module does NOT do

- It does not generate the per-chunk preamble text. That's the brief-writer's job.
- It does not call any LLM. Pure-data.
- It does not depend on the Anthropic SDK (the SDK is added by the retrieval scaffolding commit `4c49888` for a separate component).

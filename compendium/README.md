# `compendium/` — Compendium 2.0 source of truth

This directory contains the canonical row set used as input to the project's two parallel work tracks:

- **Track B — extraction harness** (`extraction-harness-brainstorm`): the single extraction pipeline emits compendium cells keyed by `compendium_row_id`.
- **Phase C — projection functions** (`phase-c-projection-tdd`): per-rubric projection functions consume `{row_id: typed_value}` dicts and return rubric scores.

## Files

| File | Role |
|------|------|
| `disclosure_side_compendium_items_v2.tsv` | **The contract.** 181 rows × 8 columns: `compendium_row_id`, `cell_type`, `axis` (legal/practical), `rubrics_reading`, `n_rubrics`, `first_introduced_by`, `status`, `notes`. |
| `_deprecated/v1/` | Compendium 1 artifacts (`disclosure_items.csv`, `framework_dedup_map.csv`) retained for traceability. **Do not load.** See [`_deprecated/v1/README.md`](_deprecated/v1/README.md). |

## How Compendium 2.0 was built

Compendium 2.0 is the output of the archived `compendium-source-extracts` branch (merged to main as `cac1469` on 2026-05-14; docs at `docs/historical/compendium-source-extracts/`). It replaces v1.x, which was structurally PRI-shaped — see [`_deprecated/v1/README.md`](_deprecated/v1/README.md) for why v1 was rebuilt rather than patched.

The branch produced:

1. **26 paper extractions** (7 originals + 14 predecessors + 5 author-hunt) treated on an even basis — no rubric privileged.
2. **9 per-rubric projection-mapping docs** at `docs/historical/compendium-source-extracts/results/projections/`:
   - `cpi_2015_c11_projection_mapping.md`
   - `pri_2010_projection_mapping.md`
   - `sunlight_2015_projection_mapping.md`
   - `newmark_2017_projection_mapping.md`
   - `newmark_2005_projection_mapping.md`
   - `opheim_1991_projection_mapping.md`
   - `hiredguns_2007_projection_mapping.md`
   - `focal_2024_projection_mapping.md`
   - `lobbyview_2018_2025_schema_coverage_mapping.md`
3. **30-decision freeze log** at [`docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md`](../docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md) (D1–D30, canonicalization + merges + in/out dispositions).
4. **Pre-merge factual audit (2026-05-13)** confirmed Newmark 2017 r=0.04 CPI↔PRI-disclosure correlation, PRI 2010 dense numerical claims, and FOCAL 1,372-cell weights all accurate (1 contact-log restoration, 1 openness clarity tightening, 1 Newmark 2017→2005 sourcing nit).

## Row-shape contract

Each row in the v2 TSV is one **canonical observable** about a state's lobbying-disclosure regime. The cell value at that row × (state, vintage) is what the extraction pipeline emits and what projection functions consume.

| Column | Meaning |
|---|---|
| `compendium_row_id` | Snake-case canonical name (e.g., `lobbyist_spending_report_includes_total_compensation`). |
| `cell_type` | The typed shape of a value at this row — `binary`, `threshold_dollars`, `threshold_hours`, `cadence_set`, `actor_set`, `activity_set`, etc. |
| `axis` | `legal` (what the statute requires) or `practical` (what the portal exposes). |
| `rubrics_reading` | Pipe-separated list of source rubrics that read this row (e.g., `pri_2010\|focal_2024\|newmark_2017`). |
| `n_rubrics` | Cardinality of `rubrics_reading`. The 8-rubric maximum is `lobbyist_spending_report_includes_total_compensation`. |
| `first_introduced_by` | Which projection-mapping doc first added this row to the union. |
| `status` | `firm` (180 rows) or `path_b_unvalidated` (1 row — `OS-1`). |
| `notes` | Free-form provenance / decision-log breadcrumbs. |

## Regeneration

The v2 TSV is the output of `tools/freeze_canonicalize_rows.py`, which is **idempotent** — given the v1 TSV at `docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v1.tsv` plus the D1–D19 canonicalization decisions (encoded as data structures in the script), it produces the v2 TSV. If you ever need to add a row or canonicalize further, edit the script's decision data structures rather than the TSV directly.

## Loading from Python

Minimal loader at `src/lobby_analysis/compendium_loader.py`:

```python
from lobby_analysis.compendium_loader import load_v2_compendium

rows = load_v2_compendium()  # list[dict[str, str]]; len == 181
```

This loader is intentionally minimal — raw `list[dict[str, str]]`, no typed model. Typed Pydantic models are the `extraction-harness-brainstorm` branch's surgery (model shape = extraction output shape; needs to be designed alongside the extraction harness).

The deprecated v1 loader is still present as `load_v1_compendium_deprecated()` so existing v1-shape tests (`tests/test_compendium_loader.py`, `tests/test_smr_projection.py`) stay green. **Do not call it from new code.**

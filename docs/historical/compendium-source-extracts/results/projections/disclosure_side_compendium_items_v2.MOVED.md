# ⚠️ This file has moved

The Compendium 2.0 row-freeze TSV is no longer here.

**New location (live source of truth):**

```
compendium/disclosure_side_compendium_items_v2.tsv
```

## Why it moved

On 2026-05-14, the `compendium-v2-promote` branch promoted v2 to a repo-level path so both parallel successor branches (`extraction-harness-brainstorm` and `phase-c-projection-tdd`) load the contract from a stable, non-historical path. Compendium 1 was simultaneously deprecated to `compendium/_deprecated/v1/`. See [`compendium/README.md`](../../../../../compendium/README.md) for the post-promote layout.

## If you hit this file via a hardcoded reference

**Update your code/docs to use the new path.** Any reference like:

```
docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv
```

should become:

```
compendium/disclosure_side_compendium_items_v2.tsv
```

The git history of the file is preserved through the rename — `git log --follow compendium/disclosure_side_compendium_items_v2.tsv` will show the full v2 row-freeze history from `compendium-source-extracts`.

## Related historical context (still at original paths)

These supporting docs stay under `docs/historical/compendium-source-extracts/`:

- [`20260513_row_freeze_decisions.md`](20260513_row_freeze_decisions.md) — 30-decision log (D1-D30) behind the v2 row set
- Nine `*_projection_mapping.md` files — per-rubric projection logic (the spec consumed by `phase-c-projection-tdd`)
- `cpi_2015_projection_mapping.md`, `pri_2010_projection_mapping.md`, `sunlight_2015_projection_mapping.md`, `newmark_2017_projection_mapping.md`, `newmark_2005_projection_mapping.md`, `opheim_1991_projection_mapping.md`, `hiredguns_2007_projection_mapping.md`, `focal_2024_projection_mapping.md`, `lobbyview_2018_2025_schema_coverage_mapping.md`

These remain historical because they document the **archived** rebuild work. The TSV moved because it's a **live contract**.

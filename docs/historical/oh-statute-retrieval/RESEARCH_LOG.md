# Research Log: oh-statute-retrieval

Created: 2026-05-14
Purpose: Track A successor branch (per Option B locked 2026-05-13). Adds OH 2007 and OH 2015 statute bundles to the existing OH 2010 + OH 2025 bundles, giving a 4-vintage same-state set for testing the Compendium 2.0 success criterion #3 ("multi-year reliability") on a single state where prior work has already established a baseline. Includes a sub-task to retrieve ground-truth scoring data for CPI Hired Guns 2007 (publicly available state-by-state results referenced in `papers/CPI_2007__hired_guns_state_lobbying.pdf` but not yet extracted as a machine-readable per-state matrix in `papers/text/` or `compendium/`). Statute retrieval reuses the Justia-unified retrieval infrastructure carried forward from the archived `pri-calibration` + `statute-retrieval` branches.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv`](../../historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv) — 181 rows. Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). Idempotent regen via `tools/freeze_canonicalize_rows.py`.
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). The multi-vintage OH set this branch produces is direct evidence for criterion #3 ("multi-year reliability").
>
> **Carry-forward infrastructure (from archived branches):** `justia_client`, `statute_retrieval`, `bundle` modules; `LOBBYING_STATUTE_URLS` registry with OH 2010 + OH 2025 entries; orchestrator subcommands (`retrieve-statutes`, `expand-bundle`, `ingest-crossrefs`, `export-statute-manifests`).

## Out of scope for this branch

- Designing the new extraction harness — that lives on `extraction-harness-brainstorm` (Track B).
- Implementing per-rubric projection functions — that lives on `phase-c-projection-tdd`.
- Other states beyond OH — this branch's deliverable is OH-specific (4 vintages on one state to validate multi-vintage reliability on the easiest baseline before scale-out).

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. When this branch's first kickoff session generates gitignored data (e.g., statute downloads, retrieval results), the kickoff agent should decide its own symlink approach at that point.

---

## Sessions

(Newest first.)

_No sessions yet — kickoff pending._

# Research Log: extraction-harness-brainstorm

Created: 2026-05-14
Purpose: Track B successor branch (per Option B locked 2026-05-13). Brainstorm-then-plan: design the **single** extraction harness / prompt architecture per the Compendium 2.0 success criterion #2 ("ONE extraction pipeline — same prompt structure, same model, same retrieval approach, applied uniformly across rows, states, and years"). The v2 row set (181 rows) is the input contract. Goal of this branch's kickoff session: a written plan (`docs/active/extraction-harness-brainstorm/plans/`) ready for the first TDD implementation session.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv`](../../historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv) — 181 rows. Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). Idempotent regen via `tools/freeze_canonicalize_rows.py`.
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #2 (ONE extraction pipeline).
>
> **Carry-forward prompt architecture (from now-dead `statute-extraction` iter-2):** the v2 scorer prompt + chunk-frame preamble (`src/scoring/chunk_frames/definitions.md`) + tightened row-description axis labels. Iter-1 dispatched against OH 2025 `definitions` chunk achieved 93.3% inter-run agreement (3 temp-0 claude-opus-4-7 runs); the materiality-gate canary captured `required_conditional` + verbatim `condition_text` across all three regimes. **Note:** iter-2's tightened row descriptions targeted the v1.2 (141-row) compendium and may need redoing against the v2 (181-row) compendium.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A).
- Per-rubric projection function implementations — that lives on `phase-c-projection-tdd`.
- Full 50-state rollout — this branch's deliverable is a *single-state pilot-ready* plan + harness, not 50-state production scale.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. When this branch's first kickoff session generates gitignored data (e.g., extraction runs, scoring results), the kickoff agent should decide its own symlink approach at that point.

---

## Sessions

(Newest first.)

_No sessions yet — kickoff pending._

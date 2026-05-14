# Research Log: extraction-harness-brainstorm

Created: 2026-05-14
Purpose: Track B successor branch (per Option B locked 2026-05-13). Brainstorm-then-plan: design the **single** extraction harness / prompt architecture per the Compendium 2.0 success criterion #2 ("ONE extraction pipeline — same prompt structure, same model, same retrieval approach, applied uniformly across rows, states, and years"). The v2 row set (181 rows) is the input contract. Goal of this branch's kickoff session: a written plan (`docs/active/extraction-harness-brainstorm/plans/`) ready for the first TDD implementation session.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows. Promoted from `docs/historical/...` to repo-level `compendium/` on 2026-05-14 by the `compendium-v2-promote` branch (live contract for the two parallel-running successors; v1 artifacts retained at `compendium/_deprecated/v1/`). Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). Idempotent regen via `tools/freeze_canonicalize_rows.py`. (Path is live on main after `compendium-v2-promote` merges; until then read via the worktree-local view.)
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

### 2026-05-14 — Kickoff orientation + plan sketch (NOT the real brainstorm)

Convo: [`convos/20260514_kickoff_orientation.md`](convos/20260514_kickoff_orientation.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**Originating context.** This branch was assigned plan-sketch work as a side-effect of the 2026-05-14 coordination session on `compendium-v2-promote` (see [`../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available post-merge). User wanted a "solidly sketched" plan in `plans/` so the kickoff agent isn't reading skeleton stubs cold.

**Locked decisions carried forward.** This branch owns the v2 Pydantic model rewrite (model shape = extraction output shape; Phase C consumes as a downstream contract). The v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows × 8 columns). The ⛔ PRI-out-of-bounds banner is gone — PRI is 1 of 8 rubrics on even footing.

**Sketch contents.** Three-phase agenda for the first real brainstorm session: (1) read carry-forward material (existing `src/scoring/scorer_prompt.md` + `retrieval_agent_prompt.md` on main; `chunk_frames/definitions.md` on `origin/statute-extraction`; predecessor harness plan in historical); (2) resolve 6 architectural questions (prompt granularity, retrieval approach, iteration unit, Pydantic model shape, conditional/materiality cell values, provenance per cell); (3) capture decisions in a follow-up implementation plan with a single TDD-able first component picked. **Recommended first component:** v2 Pydantic cell models — pure-data, easy to TDD, unblocks both this branch and Phase C.

**Open questions flagged for the real kickoff.** Does `oh-statute-retrieval` block first end-to-end test? Phase C's preferred input shape (Pydantic models vs raw dicts)? Where does the v2 model module live (in-place at `src/lobby_analysis/models/` vs new `models_v2/`)?

**Not implementation work.** No code, no tests written; only docs (the convo + plan sketch + this RESEARCH_LOG update + the Row-freeze contract path migration).


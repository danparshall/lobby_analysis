# Kickoff orientation: phase-c-projection-tdd

**Date:** 2026-05-14
**Branch:** phase-c-projection-tdd

## Summary

This is a **kickoff orientation convo**, not a TDD session. The 2026-05-14 coordination session on `compendium-v2-promote` (originating convo: [`../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available on main once that branch merges) checked whether this branch and `extraction-harness-brainstorm` would conflict. They don't on core deliverables — but coordination produced one output relevant to this branch:

**`compendium-v2-promote` landed the v1→v2 deprecation in one place** so this branch starts with a clean v2 contract at a stable repo path (`compendium/disclosure_side_compendium_items_v2.tsv` instead of `docs/historical/...`). The branch's RESEARCH_LOG row-freeze-contract link has been updated this session.

This convo exists so the plan in `plans/20260514_kickoff_plan_sketch.md` has an originating-conversation reference per the `write-a-plan` skill. It captures the decisions already locked, what's ready to TDD against, and what's still undecided.

## Locked decisions (from coordination)

- **v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv`** (181 rows). Load via `load_v2_compendium()` from `src/lobby_analysis/compendium_loader.py` (returns raw `list[dict[str, str]]` — minimal-by-design; typed Pydantic models are `extraction-harness-brainstorm`'s territory).
- **`extraction-harness-brainstorm` owns the v2 Pydantic model rewrite.** This branch consumes whatever shape that branch produces. Until harness ships its models, this branch operates on raw dicts keyed by `compendium_row_id`.
- **Locked rubric order** (in this branch's RESEARCH_LOG): CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024 (8 score-projection rubrics).
- **LobbyView 2018/2025 is NOT a Phase C projection** — schema-coverage only (already mapped on `compendium-source-extracts`; no projection function to implement).
- **PRI is no longer out-of-bounds.** The `⛔ AGENT-CRITICAL: PRI 2010 IS OUT OF BOUNDS` STATUS.md banner was removed by `compendium-v2-promote`. PRI is rubric #2 in the locked order; agents can read `papers/text/PRI_2010__state_lobbying_disclosure.txt` as the implementation spec.

## What's ready to TDD against

Phase C is the **most ready-to-execute** of the three successor branches. The per-rubric specs already exist:

| Rubric | Spec doc | Ground truth |
|---|---|---|
| CPI 2015 C11 | `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` | `docs/historical/.../cpi_2015_c11_per_state_scores.csv` (50 states × 14 items = 700 cells) + `papers/CPI_2015__sii_scores.csv` (50-state category aggregate) |
| PRI 2010 | `pri_2010_projection_mapping.md` | PRI 2010 50-state matrix in `papers/text/PRI_2010__state_lobbying_disclosure.txt` + reconstructed CSVs under `docs/historical/pri-2026-rescore/results/` (61 disclosure items + 22 accessibility items) |
| Sunlight 2015 | `sunlight_2015_projection_mapping.md` | `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` (50-state) |
| Newmark 2017 | `newmark_2017_projection_mapping.md` | `papers/text/Newmark_2017__state_lobbying_regulation.txt` (per paper p.421-422; 19-item index; r=0.04 CPI↔PRI verified pre-merge) |
| Newmark 2005 | `newmark_2005_projection_mapping.md` | `papers/text/Newmark_2005__lobbying_regulation_in_the_states.txt` |
| Opheim 1991 | `opheim_1991_projection_mapping.md` | Opheim Table 1 (47 states; MT/SD/VA missing) — published per-state index totals only; tolerance check is weak-inequality `projected_partial ≤ paper_total` |
| HG 2007 | `hiredguns_2007_projection_mapping.md` | Ground truth retrieval is on `oh-statute-retrieval` (Track A; HG 2007 sub-task). **Phase C HG projection depends on Track A's output.** |
| FOCAL 2024 | `focal_2024_projection_mapping.md` | `docs/historical/.../focal_2024_per_country_scores.csv` — L-N 2025 Suppl File 1; 1,372-cell ground truth |

**Per-rubric input row counts** (from this branch's RESEARCH_LOG): CPI 21, PRI 69, Sunlight 13, Newmark 2017 14, Newmark 2005 14, Opheim 14, HG 38, FOCAL 58.

**Most-validated v2 row across all 8 rubrics:** `lobbyist_spending_report_includes_total_compensation`. Extracting it correctly for one (state, vintage) gives 8 projection functions one data point each.

## CPI 2015 C11 first-rubric notes (from spec doc, 2026-05-07)

The spec was scoped to anticipate Phase C TDD:

- **14 atomic items** in scope (6 de jure + 8 de facto). De jure items use 2-tier or 3-tier scoring (YES/MOD/NO mapped to 100/50/0); de facto items use **5-tier scoring (0/25/50/75/100)** — the published xlsx criteria document only 100/50/0 anchors but CPI graders awarded 25/75 as partial-credit values. Doc-wide cell-type assumption: 5-tier int constrained to multiples of 25, not 3-tier enum.
- **Aggregation rule is empirical.** CPI publishes category-aggregate scores (0-100, letter grade, rank) but the formula isn't in their methodology archive. With per-item per-state ground truth (700 cells) + category-aggregate (50 cells), the aggregation rule can be **fitted** — candidate formulas: simple mean over 14 items, sub-category mean (5 sub-cats: 11.1-11.5), de jure half vs de facto half, sub-category × axis-weighted variants. Phase C fits this.
- **Data-quality footnotes:** 4 cell-level glitches in 700 (~99.4% clean) — 4 mixed-case YES/NO typos + 2 numeric-instead-of-categorical cells (IND_199, IND_203). Normalize before consumption; flag.

## What's still undecided (low-risk decisions for kickoff)

1. **Projection function input shape.** Raw `dict[str, str]` (matching `load_v2_compendium()`'s return) is the harness-independent starting point. Could also use a TypedDict for the projection's expected rows, or wait for harness's Pydantic models. **Recommended:** Start with raw `dict[str, Any]` keyed by `compendium_row_id`; each projection function asserts cell-type expectations internally. Coordinate with harness once their Pydantic shape exists.
2. **Module layout.** `src/lobby_analysis/projections/<rubric>.py` + `tests/projections/test_<rubric>.py`? Or co-locate under `src/scoring/`? **Recommended:** New `src/lobby_analysis/projections/` package — clean separation from the legacy `src/scoring/` (which is mostly PRI-MVP code that retires here).
3. **Test fixture strategy.** Hand-coded fixtures per state per rubric (say 5 representative states sampling the score distribution), or load the full ground-truth CSVs and run all 50 states as data-driven tests? **Recommended:** Both — fixtures for the TDD red/green cycle (deterministic, small), then a `test_<rubric>_against_published_scores.py` data-driven test that loads the ground-truth CSV and iterates.
4. **PRI-MVP retirement.** `cmd_build_smr` / `smr_projection` PRI-MVP code lives in `src/scoring/`. When in this branch's arc does it retire? **Recommended:** After PRI 2010 projection (rubric #2 in the locked order) has been TDD-implemented and validates against ground truth — then `smr_projection` is empirically superseded, not just abandoned.

## Out of scope (handed elsewhere)

- **Multi-vintage OH statute retrieval** — `oh-statute-retrieval` (Track A). HG 2007 ground truth comes from there as a sub-dependency.
- **The extraction harness itself** — `extraction-harness-brainstorm`. Phase C consumes hypothetically-correct compendium cells via test fixtures and ground-truth CSVs; the LLM-driven extraction pipeline that populates real cells is harness's concern.
- **LobbyView 2018/2025 score-projection** — LobbyView is schema-coverage only.
- **Designing the v2 Pydantic models** — owned by harness. Phase C uses raw dicts until harness models are ready, then adopts.

## Next session

The kickoff plan sketch ([`../plans/20260514_kickoff_plan_sketch.md`](../plans/20260514_kickoff_plan_sketch.md)) lays out a TDD agenda starting with CPI 2015 C11. Expected output of the kickoff session: passing CPI 2015 C11 projection function validating against the 700-cell ground truth (or, at minimum, a fitted aggregation rule + per-item projections passing on a sampled subset).

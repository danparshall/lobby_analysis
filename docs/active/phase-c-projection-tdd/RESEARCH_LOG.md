# Research Log: phase-c-projection-tdd

Created: 2026-05-14
Purpose: Phase C successor branch (per Option B locked 2026-05-13). TDD-implements per-rubric projection functions `f_rubric(compendium_cells_for_state_year) → rubric_score` in the **locked rubric order**:

1. **CPI 2015 C11** (smallest concrete target; 21 rows in v2 mapping; 14 atomic items from `PublicI/state-integrity-data/2015/criteria.xlsx`)
2. **PRI 2010** (69 rows in v2 mapping; ~52 NEW vs v1.2; sub-aggregate rollup rule already paper-derived in archived `pri-calibration`)
3. **Sunlight 2015** (13 rows in v2 mapping; 11 cross-rubric; three locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation)
4. **Newmark 2017** (14 rows; 8 reused, 6 new; load-bearing r=0.04 CPI↔PRI-disclosure correlation factually-audited 2026-05-13)
5. **Newmark 2005** (14 rows; **100% reuse** of Newmark 2017 mappings; 2005 mapping falsified the 2017 mapping's `contributions_from_others` parallel speculation)
6. **Opheim 1991** (14 row families / 15 in-scope items; **100% reuse**; β AND-projection 2nd concrete use; 1 catch-all un-projectable)
7. **HG 2007** (38 rows; 16 reused, 22 new; 42% reuse; ground-truth retrieval is a `oh-statute-retrieval` sub-task — depend on its output)
8. **FOCAL 2024** (58 rows post-FOCAL-1 / 22 reused, 36 new; 37.9% reuse — lowest single-mapping rate; **L-N 2025 Suppl File 1 weights** — 1,372-cell ground truth; US LDA 81/182 = 45%)

**LobbyView 2018/2025 is NOT in scope for Phase C** — it's a schema-coverage check (Federal_US LDA disclosure-observable coverage 14/18 = 78%), not a score-projection. Already documented as Phase B mapping #9; no projection function to implement.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`docs/historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv`](../../historical/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v2.tsv) — 181 rows. Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md).
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #4 (per-rubric projections as sanity checks on extraction accuracy).
>
> **Per-rubric projection mapping docs (Phase B output):** [`docs/historical/compendium-source-extracts/results/projections/`](../../historical/compendium-source-extracts/results/projections/) — one `<rubric>_projection_mapping.md` per rubric documents the column-by-column projection logic. Each TDD session can use the matching projection-mapping doc as its spec.
>
> **Factual-audit verdict (2026-05-13, pre-merge):** Newmark 2017's r=0.04 CPI↔PRI-disclosure correlation (load-bearing for unification rationale) verified exactly at paper p.421-422. PRI 2010's dense numerical claims (sub-component max counts A:11 + B:4 + C:1 + D:1 + E:20 = 37; B1/B2 reverse-scoring per footnotes 85/86; E rubric "higher of E1/E2 + F/G double-count + separate J") all confirmed exactly. FOCAL had 1 correction landed (contact-log 13/15 restored) + 1 clarity tightening (openness 11/15 vs open-data sub-theme 9/15). **Phase C agents can trust the projection-arithmetic values in these summaries.** One outstanding sourcing nit on Newmark 2017's parenthetical "0.71" comparator: it's sourced from Newmark 2005 (separate paper), not the 2017 PDF — extract from `papers/text/Newmark_2005__lobbying_regulation_in_the_states.txt` if needed.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A; Phase C HG 2007 projection depends on Track A's ground-truth retrieval sub-task).
- Designing the extraction harness — that lives on `extraction-harness-brainstorm` (Track B). Phase C projections operate on hypothetically-correct `compendium_cells`; the extraction pipeline that populates those cells is Track B's concern.
- LobbyView score-projection — LobbyView is schema-coverage only.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. Projection functions are pure code over compendium-keyed cells + tracked rubric ground-truth CSVs — likely no gitignored data needed at all for this branch.

---

## Sessions

(Newest first.)

_No sessions yet — kickoff pending._

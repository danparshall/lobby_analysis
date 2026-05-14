# Research Log: compendium-naming-docs

Created: 2026-05-14
Purpose: Document the Compendium 2.0 row-naming taxonomy. Walk every `compendium_row_id` in `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows), trace each name back to its originating decision/source, produce a naming-conventions reference, per-row provenance, and prefix-choice guidance for future rows. Audit-only on this branch — rename candidates are flagged in a "Naming issues" section but **not executed**, to keep sister-branch merges (`phase-c-projection-tdd`, `extraction-harness-brainstorm`, `oh-statute-retrieval`) clean.

> **Predecessor:** Cut off `main` at `f364973` (post-`compendium-v2-promote` merge `0a6804f`, 2026-05-14).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows, frozen 2026-05-13 in `compendium-source-extracts`, promoted to repo-level `compendium/` on 2026-05-14 by `compendium-v2-promote`. This branch treats the contract as **read-only** for the duration of the audit.
>
> **Scope decision (2026-05-14, kickoff):** Option A — audit + flag, defer renames. Documentation lands on this branch; any rename candidates surface in a "Naming issues" section of the deliverable for a later, separately-scoped follow-up branch (timed against sister-branch lifecycles).
>
> **Originating GH issue:** [#9 — Document compendium row-naming taxonomy; trace every name to source](https://github.com/danparshall/lobby_analysis/issues/9).
>
> **Originating convo:** [`docs/active/phase-c-projection-tdd/convos/20260514_rubric_plans_drafting.md`](../../phase-c-projection-tdd/convos/20260514_rubric_plans_drafting.md) — sub-0's convo. The discussion that surfaced this task lives in sub-1's convo (to be written via finish-convo there).
>
> **Key starting-point docs (from issue #9):**
> - [`docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md) — D1–D3 (compensation cluster merge, principal-side compensation merge, PRI E1/E2 prefix rename) + §§1, 5–6. Densest existing source of naming-decision context.
> - Per-rubric projection mapping docs in [`docs/historical/compendium-source-extracts/results/projections/`](../../historical/compendium-source-extracts/results/projections/) — each has a "Doc conventions" section and inline `[cross-rubric: ...]` annotations.
> - [`compendium/README.md`](../../../compendium/README.md) — currently a one-line gloss; this audit should expand it (or add a sibling `NAMING_CONVENTIONS.md`).

## Trajectory of thinking

(Newest entries first.)

### 2026-05-14 (sub-2) — Rename-candidate walkthrough + execution plan drafted

Successor to the audit-v1 kickoff. Walked Dan through all 8 §10 rename candidates one at a time, each accompanied by a pre-scanned downstream-consumer fan-out (TSV regen path via `tools/freeze_canonicalize_rows.py`, historical projection-mapping doc cross-refs, future `extraction-harness-brainstorm` Pydantic models, prompt strings, v1.1 Pydantic state).

**All 8 candidates accepted** → 15 row renames + 1 README typo fix. Per-candidate outcomes:

| # | Outcome | Notes |
|---|---|---|
| 1 | Accept | `principal_or_lobbyist_*` → `lobbyist_or_principal_*` (1 row, FOCAL) |
| 2 | Accept cluster, LV-1 to `_filing_*` | 6 rows: 5 to `_spending_report_*`, LV-1 categorically to `lobbyist_filing_*` (schema-coverage observable, not report-contents) |
| 3 | Accept all 3 high-traffic | Registration-threshold trio → `lobbyist_registration_threshold_<measure>_<unit>` shape (6-rubric `compensation` + 4-rubric `expenditure` and `time`) |
| 4 | Accept | `expenditure_itemization_de_minimis_threshold_dollars` → `lobbyist_filing_itemization_de_minimis_threshold_dollars` (1 row) |
| 5 | Accept | `registration_deadline_days_after_first_lobbying` → `lobbyist_registration_deadline_days_after_first_lobbying` (1 row) |
| 6 | Accept singular | `ministerial_diaries_available_online` → `ministerial_diary_available_online` (1 row) |
| 7 | Accept to `def_*` | 2 rows: `lobbying_definition_*` → `def_lobbying_activity_types`, `lobbyist_definition_*` → `def_lobbyist_actor_types` |
| 8 | Fix README in this branch | `cpi_2015_projection_mapping.md` → `cpi_2015_c11_projection_mapping.md` typo in `compendium/README.md` |

**Key methodological move:** the Candidate-2 LV-1 sub-decision (`_filing_*` vs `_spending_report_*`) was decided on **semantic faithfulness over mechanical cluster-uniformity**. Pushback delivered when Dan asked "won't this one be more consistent?" — clarified that "consistency" has two axes (cluster-uniformity rule favors `_spending_report_*`; family-membership / what-the-row-actually-measures favors `_filing_*`). Dan picked `_filing_*` after seeing the dual framing.

**Downstream-consumer pre-scan resolved one important question:** the v1.1 Pydantic models in `src/lobby_analysis/models/` are **row-ID-agnostic** — `compendium.py`, `state_master.py`, `compendium_loader.py` contain zero hard-coded candidate row IDs. The merge-cost consumer is the **future** v2 Pydantic work on `extraction-harness-brainstorm` (where `chunks_v2` etc. are likely to enumerate row IDs). This significantly de-risks execution timing.

**Deliverables this session:**

1. **[`convos/20260514_rename_review_and_plan.md`](convos/20260514_rename_review_and_plan.md)** — full walkthrough decisions, LV-1 sub-decision rationale, downstream-consumer pre-scan, open questions for execution.
2. **[`plans/20260515_rename_execution_plan.md`](plans/20260515_rename_execution_plan.md)** — 7-section execution brief. Rename set with old→new tables per cluster (§1); downstream-consumer fan-out per cluster with Phase 0 sister-branch grep gating execution (§2); test-first behavior tests for row-count invariance, old-absent / new-present, byte-identical non-ID columns, LV-1 categorical-exception preservation, Candidate-3 unit-suffix correctness (§3); 7-phase execution sequence with immediate-swap canonical strategy (§4); 7 edge cases including row-count drift, historical-archive non-edit rule, `provenance` column possibly harboring old-name strings (§5); what-could-change (§6); 5 questions for execution-time (§7).
3. **Minor doc-fix on this branch:** `compendium/NAMING_CONVENTIONS.md` §10 Issue 2 header corrected from "(5 rows)" → "(6 rows)". The body table already listed 6 rows; the header was a kickoff-session typo. Fixed here so the rename-execution branch doesn't carry the doc-state cleanup.

**Execution timing: deferred.** The plan stays in this branch as a planning artifact. The execution agent cuts a new branch off main (not off this branch) when `extraction-harness-brainstorm` Pydantic-model state and `phase-c-projection-tdd` projection-function rollout settle. Phase 0's pre-execution grep across sister branches is non-negotiable.

Doc-only commit; no code changes; no test run (no behavior changes here). Session convo: [`convos/20260514_rename_review_and_plan.md`](convos/20260514_rename_review_and_plan.md).

**Next steps (handoff for execution agent — likely a future branch, not this one):**

> Cut a new branch (`compendium-row-renames-v3` or similar) off **main**, not off `compendium-naming-docs`. Read the originating convo + the plan in this branch. Run Phase 0 (grep sister branches for the 15 old row IDs) BEFORE cutting the branch. Proceed test-first through Phases 1-7. Execution is purely mechanical given the plan; the hard part is sister-branch coordination.

### 2026-05-14 — Audit v1 drafted; 8 rename candidates surfaced

First substantive session produced three artifacts:

1. **`compendium/NAMING_CONVENTIONS.md`** (362 lines) — the deliverable for GH issue #9. 13 sections: ID shape, top-level prefix families (20 distinct 1-token prefixes), strong 3-token families (19 families with ≥2 members covering 147 of 181 rows), the def/actor triangle (D25), the α form-type split (D3), joint-actor rows (D7), three-threshold framework (D4), axis conventions, cell-type suffix hints, **8 rename candidates** flagged in §10, decision tree for new rows, per-row provenance pointer, maintenance.
2. **[`results/20260514_prefix_survey.py`](results/20260514_prefix_survey.py) + [`.md`](results/20260514_prefix_survey.md)** (175 + 406 lines) — empirical prefix histogram at 1/2/3-token granularity, family membership listing, cross-tabs of prefix × cell_type / axis / `first_introduced_by`. Reproducible.
3. **[`results/20260514_provenance_table.py`](results/20260514_provenance_table.py) + [`.md`](results/20260514_provenance_table.md)** (216 + 319 lines) — per-row provenance generator + table. Programmatically credits each of 181 rows to its `first_introduced_by` doc and any of D1–D30 that name it (60/181 = 33% have explicit D-refs; rest survived the freeze unchanged with provenance fully in the projection-mapping doc). Re-runnable when the TSV is regenerated by `tools/freeze_canonicalize_rows.py`. Family-grouped summary uses 1-token-then-2-token nesting so structurally-flat families like `actor_*` (11 singleton-shaped sub-prefixes) display as one family rather than 11 buckets.

**8 rename candidates surfaced** (§10 of NAMING_CONVENTIONS.md), in rough order of justification-clarity:

1. `principal_or_lobbyist_reg_form_includes_member_or_sponsor_names` — reversed ordering vs `lobbyist_or_principal_*` family (5 of 5 dominant)
2. D3 rename gaps: 6 leftover `_report_*` rows that should be `_spending_report_*` per the α split (D3's PRI-only rule didn't cover FOCAL/Newmark/LobbyView-introduced rows)
3. Lobbyist-status threshold family: `compensation_/expenditure_/time_threshold_for_lobbyist_registration` (3 high-traffic rows) don't join `lobbyist_registration_*` despite being load-bearing for HG Q2 (D22)
4. `expenditure_itemization_de_minimis_threshold_dollars` — singleton, could mirror `lobbyist_filing_de_minimis_*` family
5. `registration_deadline_days_after_first_lobbying` — should join `lobbyist_registration_*`
6. `ministerial_diaries_*` vs `ministerial_diary_*` plural drift
7. `lobbying_definition_*` / `lobbyist_definition_*` — defensible but outside `def_*` family
8. `compendium/README.md` filename-drift: lists `cpi_2015_projection_mapping.md` but file is `cpi_2015_c11_projection_mapping.md`

Rename **execution** stays deferred per the kickoff scope decision (sister-branch coordination cost). Rename candidates are flagged in the doc for a follow-up branch once `phase-c-projection-tdd` and `extraction-harness-brainstorm` lifecycles settle.

Session convo: [`convos/20260514_naming_taxonomy_kickoff.md`](convos/20260514_naming_taxonomy_kickoff.md). Commit `0e94f37`.

**Next steps (handoff for the next agent on this branch):** ✅ **Completed by 2026-05-14 (sub-2) session — see entry above.**

> Walk Dan through the 8 rename candidates in §10 of [`compendium/NAMING_CONVENTIONS.md`](../../../compendium/NAMING_CONVENTIONS.md) one at a time (accept / defer / reject for each), then draft a rename-execution plan at `plans/20260515_rename_execution_plan.md` enumerating the accepted set plus each rename's downstream-consumer fan-out (TSV regen path via `tools/freeze_canonicalize_rows.py`, projection-mapping doc cross-refs at `docs/historical/compendium-source-extracts/results/projections/`, future `extraction-harness-brainstorm` Pydantic models, prompt strings).

The 8 candidates, in rough order of justification-clarity (full detail in §10):

1. `principal_or_lobbyist_reg_form_*` (1 row) — reversed ordering vs the dominant `lobbyist_or_principal_*` family
2. D3 rename gaps: 6 leftover `_report_*` rows that should be `_spending_report_*` per the α split
3. Lobbyist-status threshold family (3 high-traffic rows; load-bearing for HG Q2 D22)
4. `expenditure_itemization_de_minimis_threshold_dollars` family fit
5. `registration_deadline_days_after_first_lobbying` family fit
6. `ministerial_diaries_*` vs `ministerial_diary_*` plural drift
7. `lobbying_definition_*` / `lobbyist_definition_*` outside the `def_*` family
8. `compendium/README.md` doc-drift (filename `cpi_2015_projection_mapping.md` → actually `cpi_2015_c11_projection_mapping.md`) — not a row-ID issue, but cheap to fix in the same branch

### 2026-05-14 — Branch cut, scope locked (kickoff)

GH issue #9 opened earlier the same day (carried out of sub-1's phase-c-projection-tdd convo). Branch `compendium-naming-docs` cut off `main` (`f364973`). Scope locked to **audit + flag, defer renames** to avoid coordination cost on parallel-running sister branches (`phase-c-projection-tdd`, `extraction-harness-brainstorm`, `oh-statute-retrieval`) — renames mid-flight would force one of those branches to absorb a non-trivial merge cost, since `extraction-harness-brainstorm` owns the v2 Pydantic models and any prompt strings that hard-code row names.

Sister-branch check (`extraction-harness-brainstorm`'s compendium delta) deferred to merge time per the kickoff decision.

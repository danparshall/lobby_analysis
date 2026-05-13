# 2026-05-13 (late-late-late-late eve) — Compendium 2.0 row-freeze brainstorm

**Branch:** `compendium-source-extracts`
**Plan executed:** [`../plans/_handoffs/20260513_row_freeze_brainstorm.md`](../plans/_handoffs/20260513_row_freeze_brainstorm.md) (full Phases 1–5)
**Predecessor convo:** [`20260513_union_step_and_premerge_audit.md`](20260513_union_step_and_premerge_audit.md)
**Decision log produced this session:** [`../results/projections/20260513_row_freeze_decisions.md`](../results/projections/20260513_row_freeze_decisions.md)
**Output TSV:** [`../results/projections/disclosure_side_compendium_items_v2.tsv`](../results/projections/disclosure_side_compendium_items_v2.tsv)
**Generation script:** [`tools/freeze_canonicalize_rows.py`](../../../../tools/freeze_canonicalize_rows.py)

## Goal

Lock the row set that will be in compendium 2.0 when this branch merges to main. Each row needs a freeze disposition; naming variants for the same observable get canonicalized to one row_id; LV-1..LV-4 + OS-1..OS-3 freeze-candidates resolved; per-mapping-doc Open Issues triaged.

## Topics explored

### Phase 1 + 1b — Tier triage + naming canonicalization (load-bearing)

Started by verifying the tier counts in `disclosure_side_compendium_items_v1.tsv`: 5 rows at 6-rubric, 3 at 5, 6 at 4, 9 at 3, 24 at 2, 135 at 1, plus 4 LobbyView freeze-candidates (n=0). Matches handoff arithmetic.

Greped the 9 mapping docs for cross-rubric naming drift on the canonical-load-bearing observables (compensation cluster, def_target_*, gifts/entertainment, threshold cells, contributions_received). Findings:

- **Compensation cluster naming drift confirmed.** Rows `lobbyist_report_includes_direct_compensation` (PRI E2f_i; v1 1-rubric) and `lobbyist_spending_report_includes_compensation` (CPI #201; v1 1-rubric) are both the same observable as `lobbyist_spending_report_includes_total_compensation` (v1 6-rubric). Every doc's cross-rubric annotation cites PRI E2f_i and CPI #201 as readers of the canonical row, but the union step kept them as separate row_ids because the first-introducing doc (PRI for direct, CPI for the bare `_includes_compensation`) used a different row_id. Mechanically the v1 TSV undercounts the most-validated row at 6-rubric when the doc narratives assert 7-8.
- **Principal-side compensation parallel.** Same drift between `principal_report_includes_direct_compensation` (HG+PRI; v1 2-rubric) and `principal_spending_report_includes_compensation_paid_to_lobbyists` (CPI; v1 1-rubric).
- **PRI E1/E2 prefix inconsistency.** PRI's atomic items use `lobbyist_report_includes_*` and `principal_report_includes_*` (without `spending_`), while every other rubric mapping uses `lobbyist_spending_report_includes_*`. Per the α form-type split convention (Decision Rule 4), report-content cells must be either reg-form-side or spending-report-side; the bare `_report_*` prefix is ambiguous. PRI 2010 paper section E is explicitly "Spending reports" — PRI E1/E2 should rename to `*_spending_report_*`.
- **`materiality_threshold_*` (PRI D1) conflicts with Sunlight's three-threshold-concept framework.** Sunlight 2015 mapping locked the three-threshold framework (lobbyist-status / filing-de-minimis / itemization-de-minimis); PRI D1 maps onto filing-de-minimis but uses PRI vocabulary `materiality_*`. Rename to `lobbyist_filing_de_minimis_threshold_*` for naming consistency.
- **`compensation_broken_down_by_client` naming.** Sunlight uses "client", Newmark uses "employer" — same observable. Newmark Open Issue 2 flags a rename to `_by_paying_entity` or `_by_employer_or_client`.
- **`def_target_legislative_or_executive_staff` vs `def_target_legislative_staff`.** Currently 2 separate rows; semantic overlap. Could split into `legislative_staff` + `executive_staff` (granularity-bias) or merge into one combined cell.
- **`lobbyist_disclosure_includes_business_associations_with_officials` / `_employment_type` prefix.** HG Q22 is reg-form; FOCAL descriptors is reg-form. Rename to `lobbyist_reg_form_includes_*`.

User decisions (D1-D8 in decision log):
- Merge compensation cluster (D1, D2) — auto-decided per cross-rubric evidence.
- Rename PRI E1/E2 prefix to `*_spending_report_*` (D3) — user-confirmed.
- Rename `compensation_broken_down_by_client` → `_by_payer` (D5) — user-confirmed (rubric-neutral, covers in-house and contract).
- Split `def_target_legislative_or_executive_staff` into `def_target_legislative_staff` + `def_target_executive_staff` (D6) — user-confirmed.
- Keep `contributions_received_for_lobbying` combined (D7) — user-confirmed (YAGNI; Newmark's source quote doesn't specify actor).
- Rename `materiality_threshold_*` → `lobbyist_filing_de_minimis_threshold_*` (D4) — auto.
- Rename `lobbyist_disclosure_*` → `lobbyist_reg_form_*` (D8) — auto.

### Phase 2 — Resolve named candidates (LV, OS, top Open Issues)

User decisions:
- LV-1 (`lobbyist_report_distinguishes_in_house_vs_contract_filer`) — **IN** (D12). Real distinguishing observable; LDA explicit; Kim 2025 GNN feature.
- LV-2 (amendment-vs-original) — **OUT** (D13). Operational metadata, not disclosure substance.
- LV-3 (`lobbying_disclosure_uses_standardized_issue_code_taxonomy`) — **OUT** (D14). User overrode the LobbyView mapping doc's recommendation; typed-enum complexity not worth it for a single-rubric observable that's federal-LDA-shaped.
- LV-4 (inferred bill links) — **OUT** (D15). Operational, recommended OUT by LobbyView mapping.
- OS-1 (`separate_registrations_for_lobbyists_and_clients`) — **IN under path-b** (D16). Real distinguishing statutory observable; entered as unvalidated (no current rubric reads it). Cost: 1 row.
- OS-2, OS-3 — **OUT (reversibly tabled)** (D17, D18). Real observables but more downstream-utility-shaped.
- Open Issue: full-text vs structured search split — **DEFER** (D19). YAGNI.

Three semantic cell_type conflicts also resolved (D9-D11): `lobbying_data_downloadable_in_analytical_format` becomes single binary; `lobbyist_registration_required` and `registration_deadline_days_after_first_lobbying` stay two-axis.

### Phase 3 — Walk single-rubric rows by family

User locked the **atomization meta-rule** (D20): keep current per-rubric atomization. PRI E1h/E2h cadence stays 12 binaries; PRI Q7a-o stays 15 binary search-filter cells; FOCAL scope.1/.4 stays 2 set-typed cells; FOCAL contact_log stays 9 atomized binaries; FOCAL descriptors stays 5 atomized binaries; HG Q31/Q32 stays 4 binary access-tier cells. Source-rubric atomization preserved; projection identical regardless of granularity choice.

With the meta-rule applied + Decision Rule 1 (single-rubric KEEP when observable is real), the 132 single-rubric rows in v2 are all KEEP (D25-D30 in the decision log batch-resolve them by family):

- `actor_*` family (PRI A1-A11, 11 binaries) — KEEP (D25)
- PRI E1/E2 contents (after D3 rename, 21 single-rubric rows) — KEEP (D26)
- PRI exemption / govt_agencies / public_entity_def / law_* — KEEP (D27)
- HG-distinctive practical-axis rows (lobbyist_directory_*, oversight_agency_*, etc.) — KEEP (D28)
- FOCAL-distinctive (contact_log, descriptors, openness, etc.) — KEEP (D29)
- CPI-distinctive (def_target_independent_agency, two-axis cells) — KEEP (D30)

### Phase 4 — Resolve remaining per-doc Open Issues

User decisions:
- HG-1 (`def_target_executive_agency` legislative-action-only carve-out split) — **DEFER** (D21). Single cell stays; HG-projection edge case.
- HG-2 (Q2 'make/spend' projection) — **`min(compensation_threshold, expenditure_threshold)` where both non-null** (D22). No new compendium row.
- Opheim catch-all un-projectable — **OUT-of-scope; document in Opheim mapping** (D23).
- ~7 remaining Open Issues across Sunlight / Newmark 2005 / Opheim cadence-monthly / HG Q12/Q23/Q24/itemized-detail / FOCAL partly-tier — **DEFERRED to Phase C** (D24). All are projection-logic questions, not row-identity questions.

### Phase 5 — Produce outputs

Wrote `tools/freeze_canonicalize_rows.py` (~250 lines): encodes D1-D19 as data structures (MERGES, RENAMES, PROMOTIONS, SPLIT_NEW_ROWS, OS_NEW_ROWS, DROPS, CELL_TYPE_NORMALIZE) and applies them to v1.tsv → v2.tsv. Idempotent: re-running reproduces v2 exactly. Future freeze edits made in the script + decision log, then re-run.

Generated `disclosure_side_compendium_items_v2.tsv`. 181 rows total: 180 firm + 1 unvalidated path-b (OS-1). Tier distribution:
- 8-rubric: 1 (`lobbyist_spending_report_includes_total_compensation` — single most-validated row in compendium 2.0)
- 6-rubric: 4 (gifts_entertainment lobbyist + principal pair, def_target_executive_agency, compensation_threshold)
- 5-rubric: 3
- 4-rubric: 6
- 3-rubric: 10
- 2-rubric: 24
- 1-rubric: 132
- 0-rubric: 1 (OS-1 unvalidated)

## Provisional Findings

- **Compendium 2.0 row set: 181 rows** (180 firm + 1 path-b unvalidated). Down from v1's 186 rows (182 firm + 4 freeze-candidates) — net change: -5 rows.
- **Single most-validated row**: `lobbyist_spending_report_includes_total_compensation` at **8 rubrics** (cpi_2015 + pri_2010 + sunlight_2015 + newmark_2017 + newmark_2005 + opheim_1991 + hg_2007 + focal_2024). The mechanical TSV undercounted at 6-rubric; canonicalization revealed PRI E2f_i + CPI #201 + the existing 6-rubric set all read the same observable.
- **Naming canonicalization had real effect on headline counts**: 4 row merges (D1+D2 + D6 collapse half) + 30 row renames (D3+D4+D5+D8) + 1 row split (D6 split half) reshape the inventory without losing distinguishing observables.
- **The freeze is a CONTRACT for successor branches.** OH retrieval, harness brainstorm, and Phase C projection TDD all reference v2 as their row set. Once `compendium-source-extracts` merges to main, row-set changes require a new branch.
- **3 LobbyView freeze-candidates dropped (LV-2/3/4); 1 added (LV-1).** 1 OpenSecrets-distinctive row added under path-b (OS-1); 2 stay reversibly tabled.
- **Atomization meta-rule preserves source-rubric structure.** No collapse of PRI binaries to enums; no atomization of FOCAL set-types to binaries. Projection logic is identical either way; the choice respects each rubric's own atomization choices.
- **All ~89 per-mapping-doc Open Issues triaged.** ~12 resolved at freeze (D9-D24); ~7 deferred to Phase C as projection-logic questions; ~70 were status notes / promotions / watchpoints already covered by the freeze decisions.

## Decisions

See decision log: [`../results/projections/20260513_row_freeze_decisions.md`](../results/projections/20260513_row_freeze_decisions.md). 30 numbered decisions D1-D30 plus appendix.

## Mistakes recorded

- Initially over-confident about LV-3 (recommended IN with typed enum); user overrode to OUT. Lesson: single-rubric LobbyView additions need stronger affirmative case than "could be typed enum"; YAGNI properly defers.
- Initially under-confident on Section 6 row-tier-count math; got confused tracing the merge effects. Re-derived correctly. Lesson: when applying multi-row merges, walk effect on each tier separately rather than netting.

## Results

- [`../results/projections/disclosure_side_compendium_items_v2.tsv`](../results/projections/disclosure_side_compendium_items_v2.tsv) — post-freeze canonical TSV (181 rows).
- [`../results/projections/20260513_row_freeze_decisions.md`](../results/projections/20260513_row_freeze_decisions.md) — decision log (30 decisions D1-D30 + Sections 1-7 + appendix).
- [`tools/freeze_canonicalize_rows.py`](../../../../tools/freeze_canonicalize_rows.py) — idempotent regen script.

## Next Steps

1. **`auditing-paper-summaries`** pass — verify the 16+ branch-added papers are in PAPER_INDEX + PAPER_SUMMARIES (the only remaining pre-merge audit per the prior session's deferred items).
2. **Merge `compendium-source-extracts` → main.** v2 row set becomes the contract.
3. **Cut 3 successor branches in parallel** (per Option B locked 2026-05-13):
   - **OH statute retrieval** (Track A; adds OH 2007 + OH 2015 to existing OH 2010 + OH 2025 bundles; HG 2007 ground-truth retrieval sub-task).
   - **Extraction harness brainstorm** (Track B; brainstorm-then-plan; inherits prompt-architecture from archived `statute-extraction` iter-2; references v2 row set).
   - **Phase C projection TDD** — locked order: CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024 (8 rubrics; LobbyView is schema-coverage, not score-projection).

## Forward-planning handoff

Not needed — the freeze is the freeze. Successor branches each get their own kickoff session referencing v2 as the row-set contract.

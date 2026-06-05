# 9-Rubric Oracle-Granularity Audit — Phase B Row-Pick Anchor

**Date:** 2026-06-04 (evening, immediately after Commit 3 wide-pass audit)
**Branch:** wi-tier1-direct-read
**Predecessor convo:** [`20260604_wide_pass_commit3_redispatch_and_audit.md`](20260604_wide_pass_commit3_redispatch_and_audit.md) (§"9-rubric oracle-granularity audit (deferred)")
**Audit deliverable:** [`../results/20260604_oracle_granularity_audit.md`](../results/20260604_oracle_granularity_audit.md)

## Summary

Executed the 9-rubric oracle-granularity audit deferred from the wide-pass Commit 3 session. Walked all archived rubric data under `docs/historical/` (especially `pri-2026-rescore`, `compendium-source-extracts`, `phase-c-projection-tdd`, `compendium-source-extracts/results/_tabled/`) plus `papers/`, classified each of the 9 source rubrics (PRI 2010, CPI 2015 C11, FOCAL 2024 + L-N 2025, Sunlight 2015, Newmark 2005/2017, Opheim 1991, HG 2007 = CPI 2003, OpenSecrets 2022, LobbyView 2018/2025) by what per-state ground-truth granularity is actually available in the project archive. Wrote per-rubric availability table plus Phase B Ralph-tractability classification.

**Headline finding:** Two of the Commit 3 brainstorm's recollections about oracle granularity were wrong, in opposite directions. (a) **PRI 2010 disclosure-law is per-CATEGORY × per-state, NOT per-item × per-state** — per-atomic-item per-state is not published. PRI 2010 accessibility has per-item × per-state only for Q1–Q6 (6 binary items), and those are portal-axis, not legal-axis. (b) **CPI 2015 C11 is the actual gold-standard per-item × per-state oracle** in the archive — 700 cells (14 indicators × 50 states), extracted on 2026-05-07 from `papers/CPI_2015__sii_criteria.xlsx` to `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`. The Commit 3 convo had filed CPI as "likely aggregate-only," which was the opposite of the truth.

Net effect on Phase B row pick: the convo's #1 candidate `lobbyist_registration_renewal_cadence` is still the right pick, but the **oracle source for it is CPI 2015 IND_199** (WI=MODERATE), not PRI 2010. 21 of the 181 compendium rows are read by `cpi_2015`; WI has CPI cells for all 14 indicators (full appendix in audit doc).

After audit landed, Dan greenlit moving to Phase B Ralph on CPI 2015. Operational decisions confirmed (via AskUserQuestion): (i) new worktree for Phase B; (ii) `lobbyist_registration_renewal_cadence` as first row; (iii) single-chunk dispatch (~$0.30-0.40/iter); (iv) $3-5 budget. Phase B work continues in a new branch / new convo; this convo closes with the audit deliverable as its principal output.

## Topics Explored

- **PRI 2010 archive walk.** Read `pri-2026-rescore/RESEARCH_LOG.md` Session 2026-04-13 §"Provisional Findings": "PRI publishes item-level data only for accessibility's 6 binary Qs, not for Q7 sub-criteria or for disclosure-law's E component." Confirmed against `pri_2010_disclosure_law_scores.csv` (5 per-category × per-state columns, NOT per-item) and `pri_2010_accessibility_scores.csv` (per-Q1..Q6 binary + Q7_raw aggregate + Q8_normalized). The Commit 3 convo had over-recalled this; cross-referenced with the Newmark 2017 mapping convo (line 24, "PRI 2010 per-item per-state via pri-2026-rescore") which also over-claimed — but `compendium-source-extracts/results/projections/pri_2010_projection_mapping.md` lines 36-37 explicitly document the correct read: 8 accessibility cells × 50 states for Q1-Q6+Q7_raw+Q8_norm, plus 5 disclosure-law sub-aggregates × 50 states. Per-atomic-item per-state NOT published.

- **CPI 2015 C11 archive walk.** Found `cpi_2015_c11_per_state_scores.csv` (700 rows: 14 indicators × 50 states) — extraction provenance documented in `compendium-source-extracts/convos/20260507_phase_b_projection_mappings.md` line 15: "Bonus discovery — the xlsx contains per-state per-indicator scores for all 50 states × 14 indicators." This is the strongest per-item × per-state oracle in the archive. Sample-verified WI's 14 IND values (IND_196..IND_209) → all populated; mix of YES/NO/MODERATE for de-jure indicators (196,197,199,201,203,207) and 0/25/50/100 5-tier ordinal for de-facto (198,200,202,204,205,206,208,209).

- **Per-rubric synthesis of validation regime tiers.** `phase-c-projection-tdd/RESEARCH_LOG.md` line 505 had already classified: Strong (CPI/HG/FOCAL: per-state per-item); Medium (PRI/Newmark 2017: per-state sub-aggregate); Weak-inequality only (Newmark 2005, Opheim 1991). Audit qualified this against actual archive completeness — HG and FOCAL are paper-strong but archive-weak: HG per-state-per-question is at CPI archives but unretrieved (Path A retrieval blocked on 2003-vintage statute data per `phase-c-projection-tdd/results/20260521_hg_vintage_correction.md`); FOCAL applied (L-N 2025) is per-country × per-indicator with US present only as Federal LDA (1 jurisdiction × 49 indicators), zero US-state cells.

- **Sunlight 2015 review.** Per-category × per-state for 5 categories on a 5-tier ordinal (-2..+2), 4 categories usable (item 4 excluded per `compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`). Per-category, not per-item: a single compendium row maps to one of N rows feeding a category — projection function is needed before the category score validates against any single row. Useful as a category-level coarser oracle, not a single-row oracle.

- **Newmark 2005, Opheim 1991, OpenSecrets 2022 review.** All three publish per-state TOTAL only (weak-inequality regime). Newmark 2005: 300 cells × 6 panels (1990-91 through 2003); Opheim 1991: 47 cells × 1 panel (1988-89, 3 states excluded by paper as data-unavailable, and 1988-89 statute snapshots not currently retrievable online); OpenSecrets 2022: 50 per-state 0-20 totals in article text; per-category 0-5 breakdowns (200 cells) exist behind a JS-rendered state-map widget at opensecrets.org/state-lobbying but NOT retrieved, NOT webfetch-accessible. OpenSecrets TABLED 2026-05-13 from compendium-source-extracts.

- **LobbyView 2018/2025 review.** Schema-coverage check rather than score projection (different shape, no per-state per-item scoring data). Out of Ralph-tractability framing.

- **Phase B first-row pick re-confirmed.** With CPI 2015 C11 as actual top oracle, `lobbyist_registration_renewal_cadence` is still the right first row but the oracle is CPI IND_199 (WI=MODERATE), not PRI 2010. Cross-tabulated all 6 wide-pass disagreements + 4 instantiation-failure rows against CPI-readability; identified 3 strong row candidates: `lobbyist_registration_renewal_cadence` (IND_199), `lobbyist_spending_report_filing_cadence` (IND_201), `lobbying_violation_penalties_imposed_in_practice` (IND_209).

- **Operational decisions for Phase B.** Asked Dan 4 questions: (i) branch — new worktree per Commit 3 convo's framing; (ii) first row — `renewal_cadence` per audit recommendation; (iii) dispatch unit — single-chunk containing target row (~$0.30-0.40/iter); (iv) spend ceiling — $3-5 (single-chunk × 8-15 iterations). All four defaults confirmed.

## Provisional Findings

- **The CPI 2015 C11 700-cell extract is the most valuable Ralph-oracle asset in the archive.** It already exists, is per-item × per-state, covers all 50 states for 14 indicators, and 21 of 181 compendium rows have `cpi_2015` in their `rubrics_reading` column. No retrieval work needed.

- **PRI 2010's role in Phase B Ralph is smaller than the Commit 3 convo assumed.** PRI 2010 disclosure-law provides sub-aggregate-level fitting only (5 columns × 50 states); no single PRI-only row can be validated row-level against PRI's published data. PRI 2010 accessibility's per-Q1-Q6 per-state data is per-item but on the portal axis we're not currently working — relevant only when Tier-3 portal extraction lands.

- **HG 2007 is named misleadingly across the codebase.** The actual statute year is 2003, not 2007 — the "2007" propagated from CPI's modern WordPress page metadata into Lacy-Nichols 2024/2025 and from L-N into the project spec doc. Per-state per-question scorecard at CPI archives is the largest potential ground-truth pool not currently in the archive (1,900 cells = 50 states × 38 in-scope items), but vintage-mismatched against modern statutes; retrieval requires a separate research line and is deferred.

- **For WI specifically, the row-level oracle pool is exactly 14 CPI cells** (one per IND_196..IND_209) plus cross-rubric overlap inferences. Other rubrics provide aggregate-tier signals but not per-row validation.

- **Two recollection errors in the Commit 3 convo went in opposite directions** (PRI overclaimed as per-item; CPI underclaimed as aggregate-only) and effectively canceled each other out for the row-pick conclusion — the right first row is the same one the convo named. But the *reason* it's the right row is CPI's oracle, not PRI's. This matters for Phase B mechanics because the CPI prompt vocab (YES/MODERATE/NO and 100/50/0 anchors) is exactly what the wide-pass YAML mis-landed against IntCell/BinaryCell rows; Ralph iteration on this row will be directly informative for Phase A pre-flight scope.

## Decisions Made

- **Audit deliverable landed** at [`../results/20260604_oracle_granularity_audit.md`](../results/20260604_oracle_granularity_audit.md). Per-rubric availability table + Phase B Ralph-tractability classification + WI's full CPI 14-indicator oracle row in appendix.

- **Phase B Ralph proceeds on CPI 2015 C11 as the row-level oracle, not PRI 2010.** First row: `lobbyist_registration_renewal_cadence` (CPI IND_199, WI=MODERATE).

- **Phase B Ralph branch: new worktree.** Per Commit 3 convo "Phase B (Ralph) deferred to its own branch / session." Branch name TBD in Phase B convo's first action — likely something like `ralph-cpi-c11-trial` or `phase-b-ralph-renewal-cadence`.

- **Per-iteration dispatch unit: single chunk containing target row** (~$0.30-0.40 per iteration using existing dispatcher; 2 models × 3 runs).

- **Spend budget: $3-5** for this exploratory session (~8-15 iterations).

- **Phase A pre-flight YAML audit (the previously-named Commit 4 on wi-tier1) is deferred for now.** The first Ralph row iteration is going against the unpatched YAML deliberately, per Dan's framing "even if we don't get it perfect, we might be able to learn a lot about what is/n't hiccuping by inference." Phase A may be informed by what Phase B Ralph surfaces on this row.

- **No retroactive correction to predecessor convos.** The Commit 3 convo recorded its tentative recollections about granularity in good faith; the audit corrects them in-place rather than editing Commit 3.

## Results

- **Audit doc:** [`../results/20260604_oracle_granularity_audit.md`](../results/20260604_oracle_granularity_audit.md) — per-rubric availability table (12 rows covering 9 rubrics with PRI/FOCAL/CPI split into legal-vs-accessibility / framework-vs-applied / C11-vs-other-categories), Ralph-tractability tiered classification, Phase B row-pick rationale with cross-tabulation of wide-pass affected rows × CPI-readable status, WI full 14-cell oracle appendix.

- **No API spend** this session. Cumulative WI Tier-1 ledger unchanged at $7.2946. Phase B Ralph spend starts in the new branch.

- **No code changes.** Pure audit + documentation session.

## Open Questions

- **Phase A pre-flight YAML audit scope.** Still open per Commit 3 convo. Was promoted to substantive Commit 4 on this branch; now deferred until Phase B Ralph runs at least one row and surfaces what kinds of prompt fixes the audit needs to be ready to make. Possibly: only patch the rows Ralph touches first, generalize after we see the per-row fix pattern.

- **Cross-vintage Ralph.** CPI 2015 is 2014-15 statute vintage; we're extracting from WI 2025 statutes. For `lobbyist_registration_renewal_cadence` specifically, has WI's renewal cadence law changed between 2015 and 2025? Worth checking before treating CPI MODERATE as the ground-truth target for the 2025 extraction. (If WI biennial renewal hasn't changed, the 2015 vintage target is still valid for 2025.)

- **HG 2007 retrieval scope-expansion.** The audit confirms HG per-state-per-question (1,900 cells if retrieved) is the second-largest potential oracle pool. Not in scope for Phase B but worth flagging — if Phase B convergence proves brittle on CPI-only oracles, HG retrieval becomes a higher priority. Currently tracked as a GH `task` issue per `phase-c-projection-tdd/results/20260521_hg_vintage_correction.md`.

- **Ralph's per-row stopping rule** (deferred from Commit 3). When does Ralph stop iterating on a single row? Options: (a) both models converge on the CPI-projected value across all 3 runs; (b) max iteration count hit; (c) cost ceiling hit; (d) Dan calls it. First-row-by-hand will probably default to (d).

## Session meta — audit changes the row-pick reason, not the row

The audit's most important effect is *not* changing what the Phase B first row is — `lobbyist_registration_renewal_cadence` is the right pick under either the wrong recollection or the corrected reading. The effect is changing *why* it's the right pick (CPI IND_199 oracle vs PRI E1c oracle) and what the convergence target is (CPI's YES/MODERATE/NO, which for WI = MODERATE, projecting to a v2 IntCell value like 24 months). Without the audit, Phase B might have started by looking up PRI 2010's per-state E1c value for WI — which doesn't exist. With the audit, the per-state target for WI is clear and singular: CPI IND_199 WI=MODERATE.

The audit also surfaced that the v2.2 ledger's "the prompts mis-landed against cell types" finding (from Commit 3) maps cleanly to CPI's published rubric vocabulary — YES/MODERATE/NO for de-jure indicators, 100/50/0 (sometimes 25/75) for de-facto 5-tier. So Phase B Ralph iteration on a CPI-readable row will be directly informative for the Phase A pre-flight audit scope: every fix Ralph requires on the renewal_cadence row's YAML prompt is a fix Phase A will need to make on every other CPI-readable row that has the same YES/MODERATE/NO vs IntCell mismatch.

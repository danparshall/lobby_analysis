# 20260513 — Union step + pre-merge audit (Phase B closure plumbing)

**Date:** 2026-05-13 (late-late-late eve, immediately after the Phase B closure session)
**Branch:** compendium-source-extracts

## Summary

Executed the mechanical post-Phase-B plumbing from the [2026-05-13 forward-planning handoff](../plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md): union step + pre-merge audit. Skipped the handoff's §3 "draft 3 successor plan docs" step after surfacing an ordering concern (the row-freeze brainstorm should happen BEFORE drafting successor plans, since the freeze decisions affect harness chunking, projection scoping, and OH retrieval targets — drafting plans against a v1 row set that will be re-baselined to v2 at freeze creates rework).

**Headline finding:** the actual disclosure-side compendium row count is **182 firm rows + 4 LobbyView freeze-candidates = 186**, NOT the handoff's running estimate of ~111. The 73-row gap is not a dedup miss (dedup correctly collapsed 271 table-rows → 184; one composite-row fix reduced that to 182). It's that the mapping docs **systematically undercount their own NEW-row contributions in narrative text vs what their tables actually carry** — PRI doc says "47 distinct disclosure-law rows" but the table has 61; HG doc says "22 NEW (14 legal + 8 practical)" but the table marks 29 NEW (12 legal + 17 practical); Newmark 2017 doc says 14 but table has 15. These narrative-vs-table drift errors accumulate ~73 rows.

The TSV exists at `results/projections/disclosure_side_compendium_items_v1.tsv`. It is **formally correct** (mechanical string-match dedup of row_ids across the 8 score-projection mapping docs + LobbyView freeze-candidates) but **cross-rubric counts are understated** because of naming drift across docs — e.g., `lobbyist_spending_report_includes_total_compensation` (FOCAL/HG/Newmark/Sunlight/Opheim spelling) vs `lobbyist_spending_report_includes_compensation` (CPI) vs `lobbyist_report_includes_direct_compensation` (PRI E2f_i) all describe the same observable but appear as 3 distinct row_ids. The doc-narrative "7-rubric-confirmed" claims for this row were based on the human author's understanding that these are the same; mechanically they're not (yet). Canonicalizing these is row-freeze-brainstorm work.

## Topics Explored

- **Sequencing pushback at session start.** The 2026-05-13 forward-planning handoff scoped this session to do union + audits + draft 3 successor plan docs (OH retrieval, harness brainstorm, Phase C projection TDD). Surfaced an internal tension: Option B's whole rationale for row-freeze BEFORE merge is that the 3 successor tracks need a stable row-set contract; drafting the plans first means they reference v1 of the union TSV, which row-freeze will regenerate to v2 → harness chunking and Phase C scoping plans need a re-pass. User agreed: start with union + audits, reassess based on context.

- **Mapping doc Summary-table format inventory.** The 9 mapping docs use 3 shape variants:
  - 5-col tables without Status column (CPI, Sunlight, PRI accessibility, PRI disclosure-law). Column 4 name varies: "Provenance hint" / "Cross-rubric readers" / "Other rubrics likely to read".
  - 6-col tables with Status column (Newmark 2017, Newmark 2005, Opheim, HG, FOCAL).
  - LobbyView is shaped differently (Coverage summary table grouped by table+coverage-status; 4 candidate NEW rows appear in narrative below).
  - PRI's Summary section has 2 subtables (Accessibility-side / Disclosure-law-side) with axis implied by section header rather than column.

- **Script architecture (`tools/union_projection_rows.py`).** Locates `## Summary of compendium rows touched` section per doc, extracts markdown tables, parses rows by header keyword (Cell type / Axis / Status / *items reading*). Composite row entries describing OR-projection reads of multiple existing cells (Opheim's 2-cell monthly aggregate; Newmark 2005's 8-cell more-frequent-than-annual aggregate) are expanded into reads-of-constituent-PRI-rows rather than creating phantom row_ids. LobbyView's 4 candidate NEW rows are hardcoded as freeze-candidates from narrative parsing.

- **TSV columns** (per the handoff suggestion, adapted): `compendium_row_id, cell_type, axis, rubrics_reading, n_rubrics, first_introduced_by, status, notes`. `first_introduced_by` walks the script's hardcoded `SCORE_PROJECTION_DOCS` order (CPI→PRI→Sunlight→Newmark 2017→Newmark 2005→Opheim→HG→FOCAL) and takes the first doc that reads each row.

- **Spot-check found a real issue: naming drift across docs.** CPI uses `lobbyist_spending_report_includes_compensation`; PRI uses `lobbyist_report_includes_direct_compensation` (E2f_i); later mappings use `lobbyist_spending_report_includes_total_compensation`. Script treats as 3 distinct row_ids. Doc-narrative "7-rubric-confirmed" depends on canonicalization that hasn't formally happened. The TSV's reported cross-rubric counts are therefore lower bounds.

- **Audit-docs findings:**
  - All 17 convos referenced in RESEARCH_LOG; all 5 plans + 3 handoffs have originating-conversation links.
  - **Structural bug found and fixed**: `20260503_pm_acquisition_and_descriptives.md` session entry body existed at RESEARCH_LOG lines ~865–931 but its `### 2026-05-03 (pm) — ...` heading was missing (only the `---` separator marked the entry boundary). Restored as `### 2026-05-03 (pm) — Blue Book / COGEL acquisition + cross-rubric descriptive stats`. Now 17 session entries match 17 convos.
  - ~35 results `.md` files lack the explicit `<!-- Generated during: convos/X -->` provenance header per skill literal — most have implicit provenance via `**Plan:**`, `**Source artifact:**`, paper methodology sections. Low-priority busywork to retrofit; not blocking merge.

- **Branch-hygiene findings (load-bearing for merge):**
  - ~9MB of embedding `.npy` binaries in branch git history (`embed_vectors__openai__text-embedding-3-large.npy` 6.25MB + 1.6MB across two commits; `embed_similarity_matrix__openai__text-embedding-3-large.npy` 1MB + 72KB). Regeneratable from `tools/embed_cross_rubric.py` + the rubric atomic-items CSV. CLAUDE.md guidance: "Keep branch history clean: no large data files, no checkpoint blobs. If you discover bloat, clean it up with `git filter-repo` before merge."
  - PAPER_INDEX.md has 17 entries vs 18 PDFs in `papers/`. Branch added 16+ new papers; need `auditing-paper-summaries` to confirm coverage.

## Provisional Findings

- **Compendium 2.0 disclosure-side inventory has 182 firm rows + 4 freeze-candidates (186 total), not ~111.** The handoff's running estimate has drifted low across Phase B sessions. The TSV is the authoritative count going into row-freeze.

- **Single-rubric rate is 135/182 = 74%.** Heavily PRI-driven: PRI introduces 81 first-read rows (most are fine-grained PRI-distinctive observables: A-family actor rows, B-family exemptions, C-family public-entity-def, E-family principal/lobbyist parallel reads, Q7a-o search-filter rows). FOCAL contributes 34 first-read rows (most contact_log + descriptors fine atomization). HG contributes 29 first-read rows (most practical-availability access-tier cells). These three rubrics drive most of the single-rubric mass; CPI/Sunlight/Newmark/Opheim contribute 1-21 first-read rows each.

- **Top cross-rubric rows are exactly the ones the doc narratives flagged.** 5 rows at 6-rubric confirmation: `lobbyist_spending_report_includes_total_compensation`, `lobbyist_report_includes_gifts_entertainment_transport_lodging`, `principal_report_includes_gifts_entertainment_transport_lodging`, `def_target_executive_agency`, `compensation_threshold_for_lobbyist_registration`. These are the load-bearing observables. Note: the TSV would show 7-rubric for `lobbyist_spending_report_includes_total_compensation` if the CPI + PRI naming variants were canonicalized to the same row_id.

- **Composite-row fix promoted PRI cadence rows from single-rubric to multi-rubric.** Before fix: 2 phantom row_ids (Opheim "lobbyist+principal cadence_includes_monthly OR" and Newmark 2005's 8-cell aggregate). After fix: 0 phantoms; PRI's 12 individual cadence rows have Opheim added as 1 reader on the 2 monthly cells and Newmark 2005 added as 1 reader on the 8 more-frequent-than-annual cells. Cleaner count: 182 firm rows.

- **Cell-type description format is inconsistent across docs.** 13 cell-type conflicts logged after script-level whitespace/backtick normalization: e.g., `typed Optional[<TimeThreshold>]` (Newmark 2017) vs `typed Optional[TimeThreshold]` (Newmark 2005, Opheim, FOCAL); `binary derived from CPI #206's 4-feature cell` (PRI) vs `binary` (FOCAL); `typed int ∈ 0..15` (PRI) vs `typed int 0..15` (FOCAL). All cosmetic — same underlying observable. Row-freeze should pick canonical formats.

- **RESEARCH_LOG had a structural bug (missing session header) that the audit-docs skill surfaced.** Before fix: only 16 session headers for 17 convos. After fix: 17 headers, properly reverse-chronological. The audit-docs skill is doing exactly what it's meant to do at pre-merge time.

## Decisions Made

| Topic | Decision |
|---|---|
| Session scope | Union + audits this session; defer row-freeze brainstorm and 3 successor plan drafts to subsequent sessions (per user direction). |
| Sequencing question (handoff's §3 plans before vs after row-freeze) | Surfaced as concern; user acknowledged the ordering question without forcing a decision. Implicitly: plans drafted AFTER row-freeze, against the canonical row set. |
| Union TSV columns | Stayed close to the handoff's suggestion: dropped `source_mapping_doc` (replaced with `first_introduced_by`); added `n_rubrics` count; status column tracks `firm` / `freeze-candidate`. |
| Composite row entries (Opheim 2-cell, Newmark 2005 8-cell) | Hardcoded expansion in script; no new row_ids created; constituent PRI rows get the reading rubric added. |
| LobbyView freeze-candidates (LV-1..LV-4) | Hardcoded into the script with `status=freeze-candidate`. LV-5 (`bill_client_link`) omitted per LobbyView mapping doc's "recommended OUT" disposition. |
| OpenSecrets-distinctive 3 candidates | NOT in the TSV; they're separate row-freeze-brainstorm inputs (only documented in convo summaries, not in any score-projection mapping doc table). |
| Missing 2026-05-03 (pm) session header in RESEARCH_LOG | Fixed in place: `### 2026-05-03 (pm) — Blue Book / COGEL acquisition + cross-rubric descriptive stats`. |
| Provenance-header retrofit for ~35 results .md files | Deferred (low-priority busywork; existing implicit provenance is adequate). |
| Embedding `.npy` bloat (~9MB in branch history) | Flagged for pre-merge consideration; NOT addressed this session (filter-repo is high-blast-radius; needs explicit user decision since multiple fellows push to this repo). |
| PAPER_INDEX 17 vs 18 (and 16+ new papers added) | Flagged for separate `auditing-paper-summaries` session before merge. |
| Cross-rubric count canonicalization (e.g., 3 distinct row_ids for total-compensation observable) | Deferred to row-freeze brainstorm — judgment call about canonical row_id per observable. |

## Results

- [`results/projections/disclosure_side_compendium_items_v1.tsv`](../results/projections/disclosure_side_compendium_items_v1.tsv) — union of 8 score-projection mapping doc Summary tables + 4 LobbyView freeze-candidates. 186 rows: 182 firm + 4 freeze-candidate. Columns: `compendium_row_id, cell_type, axis, rubrics_reading, n_rubrics, first_introduced_by, status, notes`.
- [`tools/union_projection_rows.py`](../../../../tools/union_projection_rows.py) — the union script (363 lines incl. composite-row expansion logic + LobbyView freeze-candidate hardcoding + 13 cell-type whitespace-normalization warnings).

## Open Questions

1. **Row-freeze brainstorm scope.** With 182 firm rows + 4 LV freeze-candidates + 3 OS-distinctive tabled + ~25+ Open Issues across the 8 mapping docs, the freeze session is meatier than the handoff anticipated. Should it be broken up by row-family (e.g., separate sessions for cadence family, contact_log family, threshold family) or done in one pass?

2. **Naming canonicalization sub-task.** Pre-row-freeze or during? The ~13 cell-type cosmetic conflicts + 3+ row_id naming variants (total-compensation observable; possibly others on def_target_*, def_actor_class_*, gifts/entertainment bundle) need a canonical pass. Could be a small standalone subtask (~½ session) to produce a `disclosure_side_compendium_items_v1_canonical.tsv` with naming choices documented in a corrections file.

3. **Embedding `.npy` cleanup decision.** Multi-fellow repo + ~9MB of regeneratable bytes in branch history. `git filter-repo` works but rewrites all branch SHAs → coordination with anyone who has a local clone of `compendium-source-extracts`. Alternative: leave it; 9MB isn't catastrophic; main history bloat is the cost. Needs explicit user call.

4. **The 73-row gap between handoff (~111) and TSV (182) wasn't expected.** Does this change anything about the row-freeze plan? E.g., higher-bar single-rubric review (135 single-rubric rows is a lot to walk individually), or accepting that many fine-grained PRI rows pass freeze automatically?

5. **Three known cell_type conflicts have non-cosmetic content** (per warnings):
   - `lobbying_data_downloadable_in_analytical_format`: PRI says "binary derived from CPI #206's 4-feature cell"; FOCAL says "binary". Are these the same cell or two cells?
   - `lobbyist_registration_required`: CPI says "binary (legal) + typed int 0-100 step 25 (practical)"; HG says "binary". Two-axis cell (legal + practical) vs one-axis (legal only)?
   - `registration_deadline_days_after_first_lobbying`: CPI two-axis; HG legal-only. Same question.
   - These are real schema questions for row-freeze.

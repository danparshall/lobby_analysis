# 20260513 — LobbyView Phase B final + FOCAL-1 resolution

**Date:** 2026-05-13 (late eve, immediately after FOCAL shipped)
**Branch:** compendium-source-extracts

## Summary

Closed Phase B with two pieces of work in one session:

1. **FOCAL-1 resolved.** The open scope-qualifier question flagged at the close of the FOCAL mapping session — whether to pull FOCAL `revolving_door.1` into Phase B scope or keep deferred — was surfaced at session start with a pushback recommendation (pull in) and resolved by user decision (pull in). The FOCAL mapping doc was updated in place: scope-qualifier section rewritten, aggregation math recalculated (in-scope max 175 → 180; only revolving_door.2 still excluded), Phase C validation totals updated (US LDA projected 75/175 = 43% → 81/180 = 45.0% with raw points matching the published 81 exactly), NEW per-item mapping section added for revolving_door.1, summary table extended (rows touched 57 → 58, NEW 35 → 36, reuse rate 38.5% → 37.9%), Open Issue FOCAL-1 marked RESOLVED, Correction 4 added documenting the post-checkpoint scope deviation. One NEW compendium row added: `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal). The previously-documented +6pt Phase C under-scoring tolerance on the US LDA validation anchor is **closed**.

2. **LobbyView 2018/2025 schema-coverage mapping shipped — the FINAL of 9 Phase B mappings.** Different shape from the 8 score-projection mappings: for each of LobbyView's 46 schema fields, classified into one of {COVERED, COVERED-PARTIAL, NOT_COVERED, OPERATIONAL_METADATA, EXTERNAL_ENRICHMENT}. Federal_US LDA disclosure-observable coverage = 14/18 = 78%, with 4 candidate NEW rows flagged for compendium 2.0 freeze brainstorm (LV-1 in-house-vs-contract flag; LV-2 amendment-vs-original flag; LV-3 standardized issue-code taxonomy; LV-4 full-text-search-index distinction). Three watchpoints walked: `contributions_from_others` final promotion check (CONFIRMED single-rubric across full 9-rubric set); `def_target_*` 4-cell extension validation (CONFIRMED via LDA §17 + 2 USC §1602(4)); FOCAL-1 row validation against LDA §18 (CONFIRMED — the just-added row is now 2-rubric-confirmed within the same session).

**Phase B is complete.** Next: union step into `disclosure_side_compendium_items_v1.tsv` + compendium 2.0 row-freeze brainstorm (separate plan).

## Topics Explored

- **FOCAL-1 resolution pushback and decision.** Surfaced at session start with full context (handoff doc + FOCAL mapping doc). Argued in favor of pulling revolving_door.1 IN on four grounds: (a) observable shape ≠ FOCAL category label — the cell is a registration-form disclosure observable, same shape as `descriptors.*` already in scope; (b) closes the load-bearing +6pt US LDA tolerance (raw points match exactly post-resolution); (c) trivial compendium cost (1 NEW row); (d) symmetric with rows already in scope (PRI A-family, HG Q21 household members, descriptors.* battery). Flagged the counter-argument that pulling revolving_door.1 in might retroactively reopen Newmark `prohib.revolving_door` — but argued no (Newmark reads the cooling-off rule itself, a prohibition; FOCAL revolving_door.1 reads the reg-form disclosure of prior offices — different observables on different axes). User concurred; revolving_door.1 IN, revolving_door.2 OUT.

- **FOCAL mapping doc updated in 7 edits:**
  1. Section title + body rewritten ("Scope qualifier — 2 items OUT" → "Scope qualifier — 1 item OUT (FOCAL-1 resolved 2026-05-13: revolving_door.1 IN, revolving_door.2 OUT)"); added rationale block; added non-retroactivity note for Newmark `prohib.revolving_door`.
  2. Aggregation rule math recalculated.
  3. Per-state/per-country data section updated.
  4. Phase C validation totals updated.
  5. NEW per-item mapping section "Revolving door battery" added with full template (rows, cell type, axis, scoring rule, source quote, FOCAL category-label-vs-observable note).
  6. Summary of compendium rows touched table extended.
  7. Open Issue FOCAL-1 marked RESOLVED with full disposition + cross-references.
  Plus Correction 4 added under "Corrections to predecessor mappings" documenting the post-checkpoint scope deviation and updating the union-step expectation (~110 rows → ~111 rows).

- **LobbyView source review.** Read both `items_LobbyView.md` (8-section methodology covering shape, sources, paper-to-production-schema relationship, federal-vs-state gap, open questions, downstream use) and `items_LobbyView.tsv` (46 schema fields with verbatim source quotes from LobbyViewPythonPackage README + Kim 2018 + Kim 2025 + lobbyview.org API docs).

- **Cross-rubric grep in inverted form** for the schema-coverage mapping shape. Instead of "before drafting a NEW row, check if other rubrics also read the same observable," the grep was "for each LobbyView field, which existing compendium row (across the 8 prior mappings) covers it?" Ran 4 parallel batched greps for {registrant/client/NAICS/quarter/report metadata}, {issue/section/agency-contacted/bill_id}, {position/revolving-door/legislator/Bioguide}, {bulk_download/full_text/portal/herfindahl}. Integrated grep results directly into the per-field coverage table.

- **LobbyView 46 fields classified into 5 coverage statuses:**
  - **COVERED (12):** client_name, registrant_name, report_quarter_code, amount, is_no_activity, gov_entity (partial), issue_text, covered_official_position, api_bulk_download, full_text_search_index (partial), bill_position (with nuance), various reg-form descriptor fields.
  - **NOT_COVERED candidate NEW rows (4):** is_client_self_filer, is_amendment, issue_code (Section 15 taxonomy), bill_client_link (recommended OUT — operational not disclosure).
  - **OPERATIONAL_METADATA (5):** report_uuid, client_uuid, registrant_uuid, report_year, issue_ordi, lobbyist_id (filing-identifier shape, not disclosure observables).
  - **EXTERNAL_ENRICHMENT (25):** all 11 Bills-table fields (Congress.gov + CRS), all 7 Legislators-table fields (Bioguide + GovTrack), 2 NAICS fields (industry merge), 2 firm fields (Compustat + Herfindahl), 1 Kim 2018 derived link, 2 Kim 2025 inferred-features fields, plus minor.

- **Three watchpoints walked:**
  - W1 (`contributions_from_others` final promotion check): NO match in LobbyView. LDA's LD-203 captures OUTGOING contributions, not INCOMING third-party-earmarked-for-lobbying. Newmark 2017's row is now **single-rubric across the entire 9-rubric contributing set.** Compendium 2.0 freeze recommendation: **KEEP** per Newmark-distinctive-observable rationale.
  - W2 (`def_target_*` 4-cell extension): all 4 cells `TRUE` for federal LDA per 2 USC §1602(4) "covered legislative branch official" definition (covers legislators, executive officials, executive office, AND staff). The FOCAL-introduced 4th cell (`def_target_legislative_or_executive_staff`) is empirically validated.
  - W3 (FOCAL-1 row validation): LDA §18 `covered_official_position` IS the registration-form disclosure of prior covered government employment within the previous 20 years (2 USC §1604(b)(2)(C)). Maps exactly onto the just-added `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` row. **The row is now 2-rubric-confirmed (FOCAL + LobbyView) within the same session.** FOCAL-1 decision validated by an independent rubric within hours of being made.

- **78% federal LDA coverage — shortfall analysis.** The handoff predicted ~100% federal LDA coverage. The 78% finding is because the denominator excludes 25 external enrichments and 5 operational-metadata fields; the actual 14/18 disclosure-observable coverage breaks down as 12 COVERED + 2 COVERED-PARTIAL + 4 NOT_COVERED. The 4 NOT_COVERED items are candidate NEW rows for compendium 2.0 freeze (LV-1 through LV-4), one of which (LV-5: bill_client_link) is recommended OUT as operational.

- **What LobbyView doesn't capture that other rubrics do.** Documented in mapping doc §"What LobbyView doesn't capture that other rubrics do": quantitative thresholds for registration; reporting cadence variations; portal-availability quality features (FOCAL openness.*, HG Q28-Q38, PRI accessibility.Q1-Q6); itemization-de-minimis thresholds (Sunlight #3, HG Q15); filing-de-minimis thresholds (PRI D1); gifts/entertainment/transport/lodging bundles; position-on-bill (single-state observable); per-meeting contact_log (FOCAL contact_log battery). Consistent with the source `items_LobbyView.md` §6 federal-vs-state gap enumeration.

## Provisional Findings

- **FOCAL-1 resolution is robust.** The row pulled in (revolving_door.1) was validated within the same session by LobbyView's `covered_official_position` field. Two independent rubrics now read the same registration-form prior-public-offices observable. The strict plan reading would have left this row out and accepted a permanent 6-point known under-scoring on US LDA — that would have been a worse outcome.

- **Phase B closes with ~111 compendium rows in the disclosure-side row inventory.** Composition: ~110 pre-FOCAL-1 from the 8 mappings + 1 from FOCAL-1 resolution + 0 from LobbyView at this step (LobbyView's candidate NEW rows are freeze-decision-deferred). If LV-1 through LV-4 are pulled in at compendium 2.0 freeze, the count grows to ~115; LV-5 is recommended OUT.

- **Row reuse rate distribution across 9 mappings is strongly bimodal:**
  - High-reuse mappings (100% reuse): Newmark 2005, Opheim 1991. These are within-tradition battery rubrics that share heritage with rubrics ahead of them in the order; they confirm row design rather than expand.
  - Mid-reuse mappings (50-80%): CPI 2015 C11 (broke ground for many shared rows), Sunlight 2015 (α form-type split innovator), Newmark 2017 (within-tradition with 6 new rows).
  - Low-reuse mappings (<50%): PRI 2010 (largest), HiredGuns 2007 (42% — finest practical-availability atomization), FOCAL 2024 (37.9% — per-meeting contact_log + descriptors atomization).
  - LobbyView (n/a — schema-coverage, not score-projection).

- **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` stays single-rubric across the entire 9-rubric contributing set.** All 8 score-projection cross-checks + LobbyView coverage check confirm NO PARALLEL elsewhere. **Compendium 2.0 freeze recommendation: KEEP** per Newmark-distinctive-observable rationale (the observable is real but unusual; MA principal reports list earmarked dues; some states explicitly require disclosure).

- **The `def_target_*` row family is now empirically validated against federal LDA** at all 4 cells (legislative_branch + executive_agency + governors_office_or_federal_equivalent + legislative_or_executive_staff). FOCAL scope.3 was the row family's expanding rubric; LobbyView's `gov_entity` + LDA §17 + 2 USC §1602(4) "covered legislative branch official" definition confirm the structure.

- **The cleanest framing of LobbyView's role in the compendium project** is from the items_LobbyView.md doc: "the schema fields LobbyView captures define questions our state-level compendium should also answer." The mapping doc operationalizes this as a coverage check, with 78% of LDA-disclosed observables covered + 4 candidate NEW rows + an explicit out-of-scope set (the 25 external enrichments that LobbyView ADDS on top of LDA).

## Decisions

| Topic | Decision |
|---|---|
| FOCAL-1 (revolving_door.1 scope) | **RESOLVED — pull in.** NEW row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal). revolving_door.2 stays deferred (enforcement-adjacent). |
| FOCAL mapping doc updates | 7 in-place edits + Correction 4 added; mapping count 57 → 58, NEW 35 → 36, reuse 38.5% → 37.9%. |
| US LDA Phase C tolerance after FOCAL-1 | Closed (+6pt → 0pt on raw points; ≤1pp residual percentage delta from denominator shift only). |
| LobbyView mapping shape | Schema-coverage check (5-status classification of 46 fields), NOT score-projection. |
| LobbyView Federal_US disclosure-observable coverage | 78% (14/18) — 12 COVERED + 2 COVERED-PARTIAL + 4 NOT_COVERED. 25 external enrichments and 5 operational-metadata fields excluded from denominator. |
| Candidate NEW rows from LobbyView | LV-1 (in-house-vs-contract), LV-2 (amendment-vs-original), LV-3 (standardized issue-code taxonomy), LV-4 (full-text-search-index split). All freeze-deferred. LV-5 (bill_client_link) recommended OUT as operational, not disclosure. |
| Watchpoint W1 (`contributions_from_others`) | CONFIRMED no parallel in LobbyView. Row stays single-rubric across full 9-rubric set. Freeze recommendation: KEEP. |
| Watchpoint W2 (`def_target_*` 4-cell extension) | CONFIRMED via LDA §17 + 2 USC §1602(4). All 4 cells `TRUE` for federal. |
| Watchpoint W3 (FOCAL-1 row validation) | CONFIRMED via LDA §18 `covered_official_position`. Row is now 2-rubric-confirmed (FOCAL + LobbyView) within the same session. |
| Phase B status | **COMPLETE** — all 9 mappings shipped. |
| Next | Union step into `disclosure_side_compendium_items_v1.tsv` + compendium 2.0 row-freeze brainstorm (separate plan). Then Phase C (code projections under TDD, locked order). |

## Open Issues surfaced

LobbyView mapping flagged 4 candidate NEW rows for compendium 2.0 freeze (LV-1 through LV-4) plus 2 broader items (LV-5 disposition; LV-6 external-enrichment surface). All deferred to the compendium 2.0 freeze brainstorm (separate session). FOCAL-1 is resolved.

## Mistakes recorded

None significant. FOCAL-1 resolution included an honest pushback on the strict plan reading; user concurred with the recommendation. LobbyView mapping followed the established workflow conventions cleanly. One minor over-count in the Summary table (per-battery reuse rates compute by row not by item, but I labeled the "scope" row 3/8 at item level — clarified in the table footnote).

## Results

- [`results/projections/focal_2024_projection_mapping.md`](../results/projections/focal_2024_projection_mapping.md) — updated for FOCAL-1 resolution (commit `1ecaf86`); 7 in-place edits + Correction 4. Row count 57 → 58, NEW 35 → 36, reuse 22 stable (reuse rate 37.9%).
- [`results/projections/lobbyview_schema_coverage.md`](../results/projections/lobbyview_schema_coverage.md) — NEW schema-coverage mapping doc (commit `e5ba35b`); 307 lines; 46 fields × 5 coverage statuses; 3 watchpoints walked; 6 open issues flagged.

## Next Steps

1. **Union step** — collect compendium-row references from all 9 mapping docs, dedupe, save as `results/projections/disclosure_side_compendium_items_v1.tsv`. Expected row count: ~111 (110 pre-FOCAL-1 + 1 from FOCAL-1 + 0 from LobbyView's freeze-deferred candidates).
2. **Compendium 2.0 row-freeze brainstorm** (separate plan). Inputs: the union TSV + each mapping doc's Promotions/Open Issues sections + the 4 LobbyView candidate NEW rows + the OpenSecrets-distinctive 3 rows currently tabled.
3. **Phase C: code projections under TDD.** Locked order: CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HiredGuns 2007 → FOCAL 2024 (federal-LDA validation last). LobbyView is not a Phase C target (no score to project).

---

## Post-checkpoint addendum (same session, after finish-convo)

After the initial finish-convo checkpoint (commit `6cc8c3b`), the user and I worked through the post-Phase-B forward plan in detail. Three decisions landed:

1. **Next session = union step.** Per the locked plan's Phase B done condition. The next-session agent produces `results/projections/disclosure_side_compendium_items_v1.tsv` (~111 firm rows + freeze-candidate annotations) plus runs pre-merge audits (`audit-docs` skill, paper-index sanity check, `git log --stat` glance for blob hygiene).

2. **Three parallel successor tracks identified and confirmed post-union-independent.** After the union TSV exists, the following 3 tracks have no cross-dependencies:
   - **OH statute retrieval pipeline** (Track A; extends archived `statute-retrieval` branch's `justia_client` + `LOBBYING_STATUTE_URLS`; adds OH 2007 + OH 2015 to existing OH 2010 + OH 2025 bundles; parallel sub-task = HG 2007 per-state ground-truth retrieval from Wayback Machine).
   - **Extraction harness brainstorm** (Track B; brainstorm-then-plan; inherits prompt-architecture pieces from archived `statute-extraction` branch's iter-2 work but NOT the projection code from `statute-retrieval` which is wrong shape).
   - **Phase C projection TDD — 8 rubrics** (not 9; LobbyView is schema-coverage not score-projection). Locked Phase C order CPI → PRI → Sunlight → Newmark 2017 → Newmark 2005 → Opheim → HG → FOCAL. Uses hand-populated synthetic cells for tests; independent of harness/extraction.

3. **Option B chosen for row-freeze sequencing.** Small standalone row-freeze brainstorm session happens BEFORE merge. Rationale: "freeze" should actually mean frozen at merge, so the 3 successor tracks have a stable row-set contract. The ~5-10 freeze-candidate deltas (LV-1..LV-4; 3 OS-distinctive; FOCAL Open Issues 2-11; HG Open Issues 1-7; Newmark Open Issue 1) are small but real — they affect harness chunking, projection scoping, and OH extraction targets.

**Sequencing through merge:**

| Session | Work | Branch | Output |
|---|---|---|---|
| Next | Union step + pre-merge audit + draft 3 plan docs | `compendium-source-extracts` | Union TSV + 3 plan docs at `plans/20260514_*.md` |
| Next-next | Row-freeze brainstorm | `compendium-source-extracts` | Freeze decisions; regenerate/update union TSV |
| Then | Merge → main; cut 3 successor branches in parallel | main → 3 new branches | `oh-statute-retrieval` / `extraction-harness-design` / `phase-c-projections` |

**Forward-planning handoff written:** [`../plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md`](../plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md). Self-contained brief for the next-session agent — captures Phase B closure, Option B decision, next-session scope (union + audits + 3 plan drafts), per-track plan-scaffolding notes, and 9 standing watchpoints carried forward (including the anti-pattern note about `statute-retrieval`'s `smr_projection` being the wrong shape for compendium 2.0). Supersedes the now-stale 2026-05-11 handoff which covered the now-completed Phase B work.

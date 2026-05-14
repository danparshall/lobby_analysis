# Compendium 2.0 row-freeze brainstorm — handoff

**Originating plan:** [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md) (Phase B done condition; row-freeze is the pre-merge step Option B locked in)
**Parent handoff:** [`20260513_phase_b_close_and_post_b_plan.md`](20260513_phase_b_close_and_post_b_plan.md) — this doc supersedes §4 of that handoff with the post-union findings folded in.
**Predecessor convo (this session):** [`../../convos/20260513_union_step_and_premerge_audit.md`](../../convos/20260513_union_step_and_premerge_audit.md)
**Date drafted:** 2026-05-13 (late-late-late eve, immediately after the union step + pre-merge audit shipped)
**Audience:** the next-session agent running the row-freeze brainstorm. Fresh-context-safe.
**Executed by convo:** [`../../convos/20260513_row_freeze_brainstorm.md`](../../convos/20260513_row_freeze_brainstorm.md) (2026-05-13 late-late-late-late eve). Outputs: `disclosure_side_compendium_items_v2.tsv` (181 rows) + decision log `20260513_row_freeze_decisions.md` (D1-D30).

---

## Why this handoff exists

The 2026-05-13 forward-planning handoff's §4 ("Hand off to row-freeze brainstorm session") was written before the union step ran. The union step surfaced material new information that reshapes the freeze scope:

1. **The TSV count is 182 firm rows + 4 LV freeze-candidates = 186**, not the ~111 the parent handoff anticipated. Mapping doc narratives systematically undercount their own table contributions (PRI doc claims 47 distinct disclosure-law rows; table has 61; HG doc claims 22 NEW; table has 29).
2. **74% single-rubric mass** (135 of 182 firm rows have only one rubric reading them). Heavily PRI / FOCAL / HG distinctive.
3. **Cross-rubric naming drift** surfaced: the same observable appears under different row_ids across docs (e.g., `lobbyist_spending_report_includes_compensation` (CPI) vs `lobbyist_report_includes_direct_compensation` (PRI E2f_i) vs `lobbyist_spending_report_includes_total_compensation` (Sunlight + Newmark 2017/2005 + Opheim + HG + FOCAL) — same observable, three row_ids). Doc-narrative cross-rubric promotion counts ("7-rubric-confirmed") are based on human-author canonical understanding; TSV's mechanical match shows 6.

Together these change the freeze session from "resolve ~10 candidate-row decisions" to "resolve ~10 candidate-row decisions + walk 135 single-rubric rows + canonicalize ~3-N naming variants + resolve ~30 per-mapping-doc Open Issues." It's a bigger session than the parent handoff anticipated.

**Read order for the next-session agent:**

1. This handoff (full read)
2. The convo summary: [`../../convos/20260513_union_step_and_premerge_audit.md`](../../convos/20260513_union_step_and_premerge_audit.md) — explains the union method + findings
3. The TSV: [`../../results/projections/disclosure_side_compendium_items_v1.tsv`](../../results/projections/disclosure_side_compendium_items_v1.tsv) — load into a spreadsheet/pandas; sort by `n_rubrics` descending for the "auto-keep" tier first
4. The parent handoff (skim): [`20260513_phase_b_close_and_post_b_plan.md`](20260513_phase_b_close_and_post_b_plan.md) — for the post-freeze sequencing (Option B: merge after freeze; cut 3 successor branches in parallel)
5. On demand: each mapping doc's "Open Issues" + "Promotions" sections (cited inline below)

---

## What freeze means (anti-confusion)

"Compendium 2.0 row-freeze" means **the row set that will be in the compendium when this branch merges to main.** Successor tracks (OH retrieval, harness brainstorm, Phase C projection TDD) reference this row set as a contract. Once merged, row-set changes require a new branch.

**Freeze does NOT mean:**
- Final compendium ever (future rubrics may add rows; future audits may consolidate)
- Final cell values (cells are populated by extraction, which is the harness's job)
- Final extraction prompt design (harness brainstorm is downstream of freeze)

**Freeze DOES mean:**
- Each row in the TSV has an in/out disposition (keep / drop / merge with another row)
- Naming variants for the same observable are canonicalized to one row_id
- LV-1..LV-4 + OS-distinctive 3 candidates are resolved (IN / OUT)
- Per-mapping-doc Open Issues that affect row identity / cell type / axis are resolved (or explicitly deferred-to-Phase-C with rationale)

---

## Stop / done conditions

The session is done when:

- [x] Every row in `disclosure_side_compendium_items_v1.tsv` has a freeze disposition: `keep` / `drop` / `merge-into:<canonical_row_id>` — done via D1-D30 in decision log; v2 TSV reflects all dispositions
- [x] A regenerated TSV (`disclosure_side_compendium_items_v2.tsv` OR `v1` updated in place — agent's call) reflects the freeze decisions — `disclosure_side_compendium_items_v2.tsv` (181 rows; idempotent regen via `tools/freeze_canonicalize_rows.py`)
- [x] All 4 LV freeze-candidates (LV-1..LV-4) resolved — D12 (LV-1 IN), D13/D14/D15 (LV-2/3/4 OUT)
- [x] All 3 OS-distinctive tabled candidates resolved — D16 (OS-1 IN under path-b), D17/D18 (OS-2/3 stay tabled)
- [x] All ~89 per-mapping-doc Open Issues triaged — ~12 resolved at freeze (D9-D24), ~7 deferred to Phase C as projection-logic questions (D24), remainder were status notes / promotions / watchpoints already covered
- [x] Naming canonicalization completed for at least the confirmed-load-bearing observables — D1+D2 (compensation cluster), D3 (PRI E1/E2 prefix, ~30 rows), D4 (filing-de-minimis threshold), D5 (compensation-broken-down-by-payer), D8 (lobbyist_disclosure → reg_form)
- [x] Decision log produced — [`../../results/projections/20260513_row_freeze_decisions.md`](../../results/projections/20260513_row_freeze_decisions.md) (D1-D30 + Sections 1-7 + appendix)
- [x] STATUS.md branch row updated + RESEARCH_LOG entry for the freeze session — both updated in commit `9765e33`
- [x] Convo summary written + commit + push — [`../../convos/20260513_row_freeze_brainstorm.md`](../../convos/20260513_row_freeze_brainstorm.md) (commits `9765e33`, `59c18d8`, `c70ac66`)

**Out of scope for this session:**
- Cell-type schema details (v2.0 schema bump is a separate plan)
- Implementing projections (Phase C is downstream)
- Drafting the 3 successor plan docs (those happen after freeze, against the canonical row set)
- Merging to main (that's a separate step after this session lands)

---

## Inputs (everything you need is in the worktree)

### Primary input: the union TSV

`docs/active/compendium-source-extracts/results/projections/disclosure_side_compendium_items_v1.tsv`

Columns:
- `compendium_row_id` — working name (NOT canonical until you decide)
- `cell_type` — typed declaration; cosmetic format conflicts noted in script warnings
- `axis` — `legal` / `practical` / `legal+practical` / `practical|legal` (last form = inconsistent across docs, needs resolution)
- `rubrics_reading` — semicolon-separated rubric tags reading this row (PER MECHANICAL ROW_ID MATCH ONLY — see naming-drift caveat below)
- `n_rubrics` — count of rubrics in the previous column
- `first_introduced_by` — mapping doc filename
- `status` — `firm` (in the union) / `freeze-candidate` (LobbyView LV-1..LV-4 hardcoded from script)
- `notes` — flags single-rubric rows + freeze-candidate context for LV-1..LV-4

**Tier the rows by `n_rubrics` for triage efficiency:**

| n_rubrics | count | strategy |
|---|---|---|
| 6 | 5 | Auto-KEEP. Most-validated observables. Just confirm row_id naming. |
| 5 | 3 | Auto-KEEP. |
| 4 | 6 | Probably KEEP; sanity-check naming. |
| 3 | 9 | Probably KEEP. |
| 2 | 24 | Walk individually. |
| 1 | 135 | **Walk individually with high care.** Many are real PRI-distinctive observables (Q7a-o search filters, A-family actor types, E-family principal/lobbyist parallels) — single-rubric is NOT a deletion criterion when the underlying observable is real (per the `contributions_received_for_lobbying` freeze rationale that was established 2026-05-13). Some may be over-atomization (e.g., when PRI splits cadence into 6 binaries + the projection always OR's them — granularity-bias says keep; YAGNI says collapse to enum). |

### Secondary input: LobbyView freeze-candidates

Already in the TSV with `status=freeze-candidate`. Discussion in [`../../results/projections/lobbyview_schema_coverage.md`](../../results/projections/lobbyview_schema_coverage.md) "Open Issues" section §§1-6:

| Candidate | Source | Argument for | Argument against | LobbyView mapping recommendation |
|---|---|---|---|---|
| LV-1 `lobbyist_report_distinguishes_in_house_vs_contract_filer` | LDA §10 / `is_client_self_filer` | Explicit LDA distinction; Kim 2025 uses it as a node feature | Implicit in α form-split + scope.2 | Defer to freeze (no recommendation) |
| LV-2 `lobbyist_filings_flagged_as_amendment_vs_original` | LDA amendment indicator / `is_amendment` | Empirically useful data-quality signal | Operational metadata, not disclosure substance | Defer to freeze |
| LV-3 `lobbying_disclosure_uses_standardized_issue_code_taxonomy` | LDA §15 / `issue_code` | Federal LDA distinctive; structural-quality signal | Weakly observable at state level | Pull in as typed enum {none / state_specific / lda / other} rather than binary |
| LV-4 `lobbying_report_records_inferred_bill_links` | `bill_client_link` (Kim 2018 pipeline) | (n/a — derived inference) | NOT a disclosure observable | **Recommended OUT** (operational, not disclosure) |

LV-5 (`bill_client_link` as separate row): documented as recommended-OUT in the LobbyView mapping; omitted from the TSV. If the freeze session reverses this, add it back.

### Secondary input: OpenSecrets-distinctive tabled candidates

The OS 2022 mapping was tabled (reversibly) 2026-05-12 because OS lacks per-tier scoring definitions. Three OS-distinctive row candidates were also tabled, documented in [`../../results/_tabled/opensecrets_2022_tabled.md`](../../results/_tabled/opensecrets_2022_tabled.md):

| Candidate | OS source | Distinguishes |
|---|---|---|
| OS-1 separate-registrations-vs-combined-employer-listing | OS scorecard | A state where 1 firm registering 50 lobbyists = 50 separate registrations vs 1 combined; affects entity-count downstream stats |
| OS-2 lobbyist-compensation-as-exact-vs-ranges | OS scorecard | Some states allow ranged disclosure (e.g., $10K-$50K); affects extraction granularity |
| OS-3 lobbyist-compensation-per-individual-vs-aggregate | OS scorecard | Some states report aggregate firm-level only; affects per-lobbyist analytics |

These are NOT in the TSV; freeze decision is whether to add them (and as what row_ids).

### Secondary input: per-mapping-doc Open Issues

Total ~89 numbered items across the 9 mapping docs. Many are status notes / promotions / watchpoints — not all are freeze decisions. Counts:

| Mapping doc | # Open Issue items | Of which are freeze decisions (rough estimate) |
|---|---:|---|
| `pri_2010_projection_mapping.md` | 11 | ~4 (E1h/E2h cadence atomization, materiality D-series gate, B-series direction, Q7a-o granularity) |
| `cpi_2015_c11_projection_mapping.md` | 6 | ~2 (typed-cell schema; 5-tier de-facto cell semantics) |
| `sunlight_2015_projection_mapping.md` | 5 | ~3 (item-4 underlying-cell retention; α form-type split lock; three-threshold-concept naming) |
| `newmark_2017_projection_mapping.md` | 6 | ~3 (def_actor_class_* family separation; client-vs-employer naming; contributions_received_for_lobbying actor-split) |
| `newmark_2005_projection_mapping.md` | 4 | ~1 (vintage-stability cell semantics) |
| `opheim_1991_projection_mapping.md` | 7 | ~3 (catch-all un-projectable disposition; β AND-projection lock; cadence-monthly cell narrowing) |
| `hiredguns_2007_projection_mapping.md` | 19 | ~7 (Q12 session-calendar metadata cell; Q23/Q24 partial-scope; Q31/Q32 4-tier-vs-binary; itemized-detail conditional-cascade) |
| `focal_2024_projection_mapping.md` | 17 | ~7 (set-typed cells scope.1/.4 atomization to 17 binaries?; per-meeting contact_log atomization keep/coarsen; descriptors atomization; partly-tier semantics) |
| `lobbyview_schema_coverage.md` | 14 | ~6 (LV-1..LV-5 already-tabulated above + external-enrichment surface as a separate question) |
| **Total** | **89** | **~36** real freeze decisions |

Open the relevant `## Open issues` section in each mapping doc when you're walking the rows that section pertains to.

### Tertiary input: naming canonicalization

**The TSV has at least 3 confirmed naming variants for the same observable. Likely more.** Surfaced examples:

| Observable | Variants in TSV | Confirmed-by-doc-narrative count |
|---|---|---|
| Lobbyist spending report includes total compensation | (a) `lobbyist_spending_report_includes_compensation` (CPI), (b) `lobbyist_report_includes_direct_compensation` (PRI E2f_i), (c) `lobbyist_spending_report_includes_total_compensation` (Sunlight + Newmark 2017/2005 + Opheim + HG + FOCAL) | 7-rubric (doc) vs 6-rubric (TSV mechanical) |
| (likely) `def_target_executive_agency` | one row_id in TSV at 6-rubric — likely consistent | — |
| (likely) Gifts/entertainment/transport/lodging bundle | TSV shows `lobbyist_report_includes_gifts_entertainment_transport_lodging` + `principal_report_includes_gifts_entertainment_transport_lodging` (the principal/lobbyist split is real — keep separate) | 6-rubric each |
| (probable) `def_actor_class_elected_officials` / `def_actor_class_public_employees` | Newmark 2017 introduced; 3-rubric-confirmed per docs | Confirm TSV count matches |
| (probable) Threshold cells (compensation / expenditure / time × for-registration) | typed Optional[Decimal/TimeThreshold]; backtick/whitespace format variants noted in script warnings | Confirm naming is consistent across CPI/Newmark/HG/FOCAL |

**A pre-freeze canonicalization pass would consolidate these.** Suggested workflow:

1. For each row_id at `n_rubrics ≥ 2` in the TSV, grep the row_id (and obvious variants) across all 9 mapping docs. If a variant turns up in another doc with the same observable definition: rename the variant to the canonical form and merge the rubric reads.
2. Re-run the union script (or update in place) → produce `disclosure_side_compendium_items_v1_canonical.tsv`.
3. Verify: cross-rubric counts in the canonical TSV should now match (or exceed) the doc-narrative claims for the load-bearing observables.

**The canonicalization is itself a freeze decision.** Don't auto-canonicalize without explicit rationale.

---

## Decision rules from prior sessions (carry forward)

The following decisions are LOCKED unless this session explicitly overturns:

1. **Single-rubric is NOT a deletion criterion when the underlying observable is real.** Established 2026-05-13 for `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (Newmark 2017 distinctive; MA principal reports list earmarked dues; some states require it). Apply this rule to ALL single-rubric rows: ask "is this observable real, or is it an artifact of one rubric's atomization preference?"

2. **Practical-availability cells are extracted by Track B (portal pipeline), not by this branch's harness.** Confirmed in the 2026-05-13 parent handoff. Practical cells stay null in the compendium until Track B populates them. ~50 of the 182 firm rows are practical-axis or legal+practical — freeze them but flag the practical side for Track B.

3. **`def_actor_class_*` family is 3-rubric-confirmed and load-bearing.** Newmark 2017 + Newmark 2005 + Opheim all read it. Newmark 2017 mapping's Open Issue 1 ("merge into def_target_* or actor_*?") should be **resolved at this freeze**, not deferred further. The Opheim mapping marks it resolved-in-principle; this session explicitly locks the row family.

4. **α form-type split is locked.** Sunlight introduced (2026-05-11): same content cell exists separately for the registration-form side and the spending-report side. HG Q5/Q20 is the canonical motivating case. Don't undo at freeze.

5. **β AND-projection is locked.** Opheim 1991 introduced (2026-05-13): a single rubric item reads multiple compendium cells via AND-projection. Don't undo at freeze.

6. **Three threshold concepts must stay distinct.** Locked in Sunlight 2015 mapping: lobbyist-status threshold (= for registration), filing-de-minimis threshold (= for filing), itemization-de-minimis threshold (= for itemized line items). Conflating them would break PRI D1 vs Sunlight #3 vs HG Q15 reads.

7. **Compendium 2.0 includes both axes.** Disclosure-side scope (this round) covers `legal_availability` (statute-text observable) AND `practical_availability` (portal-observation observable). Both axes have rows in the TSV. Practical-side rows ARE in scope for freeze; only their POPULATION is deferred to Track B.

8. **Jurisdiction scope: {50 US states} ∪ {Federal_US (LDA)}.** Federal-only rows (e.g., LDA's 20%-time rule, $3K/$13K thresholds) may exist in the freeze set; they're just unpopulated for state jurisdictions.

9. **`statute-retrieval` branch's `cmd_build_smr` / `smr_projection` is the WRONG SHAPE for compendium 2.0** (compendium-1.x-keyed + PRI-only). Do NOT use as a template. The harness brainstorm (separate plan, post-freeze) inherits prompt-architecture only from `statute-extraction` iter-2.

10. **PRI 2010 is out-of-bounds for compendium DESIGN, not for compendium USE.** The branch's top-of-file warning (PRI exclusion) was about the STRUCTURE / ATOMIZATION coming from PRI. By Phase B close, PRI has been added back as a contributing rubric on equal footing with the others — its 83 atomic items now read into the compendium row set via the same mapping-doc workflow. Freeze decisions about PRI rows are normal freeze decisions; don't apply the "no PRI" rule to row-keep decisions.

---

## Suggested session structure

(Adapt — this is a brainstorm, not a checklist.)

**Phase 1: Triage by `n_rubrics` tier** (~30 min)
- Auto-KEEP the 6-/5-/4-rubric rows after a sanity-check naming pass (the canonicalization sub-task — confirm row_ids match doc-narrative counts)
- Note which 3- and 2-rubric rows need walk-through

**Phase 2: Resolve named candidates** (~45 min)
- LV-1..LV-4 (LobbyView): decide IN/OUT per row
- OS-1..OS-3 (OpenSecrets-distinctive): decide IN/OUT per row; if IN, add to TSV with proposed row_ids
- Top per-doc Open Issues for n_rubrics ≥ 2 rows (e.g., Newmark 2017 Open Issue 2 client-vs-employer naming; Open Issue 3 contributions_received_for_lobbying actor-split)

**Phase 3: Walk single-rubric rows** (~90 min)
- This is the bulk of the work. 135 rows; budget ~40s per row average.
- For each: is the observable real? Is it over-atomization? Should it merge into a more general row? Should it be deferred to a follow-on session?
- PRI is the biggest contributor here (81 first-introduced); FOCAL is second (34); HG is third (29).
- Recommend NOT walking sequentially — group by row-family (e.g., all `actor_*` rows together; all Q7a-o search-filters together; all `lobbying_contact_log_includes_*` together) and decide family-by-family.

**Phase 4: Resolve remaining Open Issues** (~30 min)
- The harder per-doc Open Issues (e.g., FOCAL set-typed scope.1/.4 → atomize to 17 binaries? Probably yes per granularity-bias; HG Q31/Q32 4-tier-vs-typed-enum)
- Each gets resolved-at-freeze OR deferred-to-Phase-C with explicit rationale

**Phase 5: Produce outputs**
- Regenerated TSV (canonical row_ids)
- Decision log (key non-trivial decisions + rationale)
- STATUS / RESEARCH_LOG / convo updates per `update-docs` skill

**Total: ~3-4 hours.** Plausibly two sessions if context budget runs short — natural break point is between Phase 3 and Phase 4.

---

## What this handoff is NOT for

- Cell-type schema details (v2.0 schema bump is a separate plan; this session can FLAG schema gaps but not RESOLVE them)
- Phase C projection logic (downstream; freeze just locks the row set Phase C will project to/from)
- Harness brainstorm (downstream; depends on canonical row set + chunking strategy)
- OH statute retrieval (downstream; depends on canonical row set but mostly independent of row-design choices)
- Merging the branch to main (separate next-next step after this session)
- Drafting the 3 successor plan docs (post-merge work, against canonical row set)

---

## Watchpoints (carry forward)

1. **TSV cross-rubric counts are LOWER BOUNDS** until canonicalization. If a row appears to be 1-rubric in the TSV but the doc narratives suggest it's 3-rubric (because of naming variants), trust the doc narratives + canonicalize.
2. **Doc narratives have internal arithmetic errors** (PRI doc says 47 rows in disclosure-law; table has 61; doc's component sum is 59 not 47; etc.). When narrative and table disagree, the table is authoritative.
3. **Newmark 2017's `disc.contributions_from_others` row** stays single-rubric across the 9-rubric set after all checks. Freeze recommendation: **KEEP** per Newmark-distinctive-observable rationale. The row name in the TSV is `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`.
4. **FOCAL-1 row** (`lobbyist_reg_form_includes_lobbyist_prior_public_offices_held`) is 2-rubric-confirmed (FOCAL + LobbyView LDA §18). Freeze decision: KEEP. Locked 2026-05-13.
5. **`def_target_*` family extension to 4 cells** is validated against federal LDA. The 4th cell `def_target_legislative_or_executive_staff` is in the TSV; freeze locks it.
6. **Cell-type cosmetic conflicts in the TSV** (e.g., `typed Optional[<TimeThreshold>]` vs `typed Optional[TimeThreshold]`; `binary (practical)` vs `binary`) are NOT row-identity conflicts. Canonicalize the cell_type column for cleanliness but don't treat as freeze-blockers.
7. **3 cell_type conflicts ARE semantic** (per script warnings):
   - `lobbying_data_downloadable_in_analytical_format` — PRI says "binary derived from CPI #206's 4-feature cell"; FOCAL says "binary". Are these the same cell?
   - `lobbyist_registration_required` — CPI says two-axis (legal binary + practical typed); HG says legal binary only.
   - `registration_deadline_days_after_first_lobbying` — same two-axis-vs-one-axis question.
   These are real freeze decisions about whether the rows are single-axis or two-axis cells.

---

## Files this handoff references (index)

- [`disclosure_side_compendium_items_v1.tsv`](../../results/projections/disclosure_side_compendium_items_v1.tsv) — primary input; load into spreadsheet/pandas
- [`tools/union_projection_rows.py`](../../../../../tools/union_projection_rows.py) — script for regenerating the TSV after freeze decisions
- [`lobbyview_schema_coverage.md`](../../results/projections/lobbyview_schema_coverage.md) — LV-1..LV-5 candidate details
- [`_tabled/opensecrets_2022_tabled.md`](../../results/_tabled/opensecrets_2022_tabled.md) — OS-distinctive 3 candidates
- 8 score-projection mapping docs in [`results/projections/`](../../results/projections/) — Open Issues + Promotions sections for per-doc decisions
- [`20260513_phase_b_close_and_post_b_plan.md`](20260513_phase_b_close_and_post_b_plan.md) — parent handoff with §3a-c plan-doc scaffolding for the 3 successor tracks (post-merge work, not this session)
- [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md) — the locked Phase B/C plan

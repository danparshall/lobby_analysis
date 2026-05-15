# Compendium 2.0 post-framing review

**Date:** 2026-05-14
**Framing reference:** `docs/RESEARCH_ARC.md`
**Originating handoff:** `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260514_post_framing_compendium_review_handoff.md`

Read-only review. No re-opening of frozen D1–D30 decisions, naming-conventions PR #10, or the 181-row contract. Findings are advisory for downstream branches (`extraction-harness-brainstorm`, `phase-c-projection-tdd`, `oh-statute-retrieval`).

## Top 3-5 findings that should change what we work on next

1. **[BLOCKER for Phase C] Per-state per-atomic-item ground truth is only directly available for CPI 2015 (700 cells) and Sunlight 2015 (200 cells, 4 items in scope). The other six rubrics' validation is structurally weaker, and the Ralph-loop objective in RESEARCH_ARC §"Ralph loop objective" does not yet reflect this.** The objective treats every `(state, vintage, rubric)` summand uniformly. But:
   - PRI 2010: per-state per-item available *only* via `docs/historical/pri-2026-rescore/` (not in this branch's archive at the freeze point; check provenance before Phase C consumes).
   - Newmark 2017: sub-aggregate-only (50 × 2 cells = 100 anchors).
   - Newmark 2005, Opheim 1991: total-only, weak inequality `our_partial ≤ published_total` (per-section sub-aggregates not published).
   - HG 2007: per-item ground truth requires re-retrieval from CPI website (not in archive; flagged in `hiredguns_2007_projection_mapping.md` §"Per-state per-indicator data"). Without that retrieval, HG validation degrades to weak-inequality on the 83/100 disclosure partial.
   - FOCAL 2024: zero per-state US ground truth; only Federal LDA (81/180 raw points, exact match) plus 27 non-US country anchors. Cross-rubric overlap is the *only* US-state check.
   This is not a row-set defect — it is a Phase C plan defect waiting to happen. The `loss(prompt)` formula will overweight whatever rubric has the most projectable summands unless explicitly normalized. RESEARCH_ARC §"Three risks worth naming up front" risk #1 names the weighting issue abstractly; this is the concrete version that drops out of what each rubric *can actually contribute*. `phase-c-projection-tdd`'s kickoff should pick an explicit per-rubric normalization before any code is written, and the Ralph-loop budget calculation should not assume FOCAL contributes 50-state signal.

2. **[SHOULD-FIX, doc inconsistency] The TSV `status` column has all 181 rows marked `firm`, but `compendium/README.md` claims "180 firm + 1 path_b_unvalidated" and `compendium/NAMING_CONVENTIONS.md` makes the same claim.** The OS-1 row (`separate_registrations_for_lobbyists_and_clients`) is identified as unvalidated only via `n_rubrics=0` and the literal string `(unvalidated; path-b)` in the `rubrics_reading` column. README + naming-conventions doc claim a `path_b_unvalidated` status value that does not exist in the TSV. Doc-vs-data drift that any downstream code reading `status` will hit. Cheap to fix by either updating the TSV (regenerate via `tools/freeze_canonicalize_rows.py`) or updating the two docs to describe how unvalidated status is actually encoded. Per the "frozen contract" constraint, the doc-side fix is what the spawn was given license for — but the user should make the call on which side moves.

3. **[SHOULD-FIX, framing-driven gap] Legal-vs-practical-gap completeness is structurally asymmetric across the 181 rows.** Under the corrected framing (RESEARCH_ARC §"Three prongs": "the gap between what the statute *requires* and what the portal *actually exposes* is itself observable and queryable"), every legal-axis row that asserts a content requirement on a disclosure artifact (registration form, spending report, contact log) ought to have a queryable practical-axis counterpart. Empirically:
   - 35 `lobbyist_spending_report_includes_*` rows are legal-only. No row asks "does the portal expose `<field>` on filed spending reports?" The practical-axis surface for these content questions is bundled into 4 access-tier rows (`lobbyist_spending_report_available_as_*`) that measure *form of access*, not *which content fields are surfaced*.
   - Same pattern for `lobbyist_reg_form_includes_*` (13 rows, legal-only), `lobbying_contact_log_includes_*` (9 rows, legal-only), `principal_spending_report_includes_*` (mostly legal-only).
   - The 5 dual-axis rows (`lobbyist_registration_required`, `lobbyist_registration_deadline_days_after_first_lobbying`, `lobbyist_spending_report_filing_cadence`, `lobbying_disclosure_audit_required_in_law`, `lobbying_violation_penalties_imposed_in_practice`) handle the gap for *whether the artifact exists* — but say nothing about *which fields are actually surfaced on it*.
   Concretely: a state whose statute mandates `lobbyist_spending_report_includes_principal_business_nature=TRUE` but whose portal silently omits the field is unrepresentable in v2 — the gap-as-research-artifact (RESEARCH_ARC's second value-prop for Prong 1) cannot be queried for content-level asymmetries. This is a Prong 2 brief-writer concern, not a Phase C concern — but it should be a deliberate decision when `extraction-harness-brainstorm` spins up its practical-axis sibling component, not a discovered-late surprise. Two routes: (a) add per-content-field practical cells (would add ~50+ rows; expensive); (b) capture the gap as a single `practical_axis_observed_fields: Set[row_id]` cell on a portal-observation envelope that lives outside the 181-row TSV. Option (b) seems lower-cost and consistent with the cell-typed-schema posture, but is a real design decision that hasn't been articulated.

4. **[OBSERVATION] The 9 projection mapping docs use pre-rename row IDs throughout, and §10.1 of `NAMING_CONVENTIONS.md` is *only* a resolver table — there is no automated check that mapping references stay consistent with the v2 TSV.** Per the naming-conventions doc, this is deliberate ("§10.1 resolver table preserves old→new pairs verbatim for readers of archived material"). But: when `phase-c-projection-tdd` writes projection functions, it will read the mapping docs to learn which compendium rows each rubric reads. Every such read has to go through the §10.1 resolver — there are 247 old-name occurrences across the 9 mapping docs (counts from `grep -c` per file: focal=44, pri=72, newmark_2005=23, newmark_2017=14, opheim=19, hg=19, sunlight=3, cpi=2, lobbyview=7, plus 47 in the freeze-decisions log). Resolver lookups are easy to skip and produce silent miscoding. Cheap mitigation: a one-off `tools/check_mapping_doc_row_ids.py` that asserts every row_id mentioned in a mapping doc either (a) exists in `compendium/disclosure_side_compendium_items_v2.tsv` or (b) is a key in the `RENAMES` dict of `src/lobby_analysis/row_id_renamer.py`. Run as a pre-merge check on Phase C projection PRs. Not load-bearing for the Compendium 2.0 freeze; load-bearing for Phase C correctness.

## Q1. Row coverage of Phase C rubrics

All 8 rubrics have non-trivial v2 row coverage. Per-rubric row count (rows whose `rubrics_reading` includes the rubric tag, from `awk` over v2 TSV):

| Rubric | RESEARCH_ARC "Rows" col | v2 rows reading | Validation regime per RESEARCH_ARC |
|---|---:|---:|---|
| CPI 2015 C11 | 21 | 21 | Per-state per-item, 50 states (700 cells) |
| PRI 2010 | 69 | 83 | Per-state per-item, 50 states (4,150 cells nominal) |
| Sunlight 2015 | 13 | 13 | Per-state per-category (200 cells, 4 items) |
| Newmark 2017 | 14 | 15 | Sub-aggregate only (100 cells) |
| Newmark 2005 | 14 | 22 | Weak inequality (300 cells, 6 panels) |
| Opheim 1991 | 14 | 17 | Weak inequality (47 cells) |
| HG 2007 | 38 | 49 | Strong contingent on retrieval (1,900 nominal); otherwise weak |
| FOCAL 2024 | 58 | 60 | Federal-LDA only (81/180 anchor) + 27 non-US |

The RESEARCH_ARC counts are *source rubric atomic items*; the v2 row counts are higher because of granularity-bias splits (e.g., Sunlight #1's 1 tier maps to 6 compendium rows via the α form-type split). No rubric is undercovered for projection. **No blocker.**

The real concern is not coverage but *validation-regime asymmetry across the rubrics* — see Finding 1 above. RESEARCH_ARC §"Phase C rubric order" lists the validation regime per rubric, so the asymmetry is documented; the gap is that the Ralph-loop objective doesn't yet operationalize how to weight summands across regimes.

One narrow row-coverage caveat: HG 2007 Q39–Q47 (enforcement) and Q48 (cooling-off) are out of disclosure-only scope. HG's disclosure-side partial maxes at 83/100. This is documented in `hiredguns_2007_projection_mapping.md` and is a Phase C scoping concern, not a row-set defect.

## Q2. Prong-1 / Prong-2 axis seam

The seam is clean. Walked through the 50 practical-only rows + 5 dual-axis practical halves:

- **50 practical-only rows.** All are portal/data-system observables: `lobbying_data_*` (8), `lobbying_search_filter_*` (15), `lobbying_disclosure_documents_*` (3 free/online/response-time), `lobbyist_directory_available_as_*` (4), `lobbyist_spending_report_available_as_*` (4), `online_lobbyist_*_filing_available` (2), `oversight_agency_*` (4), `ministerial_diary_*` (2), `state_has_dedicated_lobbying_website` (1), `sample_lobbying_forms_available_on_web` (1), `lobbying_records_copy_cost_per_page_dollars` (1), `lobbying_website_easily_findable` (1), plus 4 others. Each is the kind of observation a portal scraper produces, not a statute reader.
- **5 dual-axis rows.** Each has a clean Prong-1 reading (legal axis) and a clean Prong-2 reading (practical axis): registration-required, registration-deadline, filing-cadence, audit-required-in-law, violation-penalties-imposed. These are the textbook cases where statute says X *and* portal exposes Y. The dual axis is preserved in the TSV (`legal+practical` axis value).

No mislabeling observed. No practical-only row sneaks in statute-reading work; no legal-only row sneaks in portal observation. **No finding.**

## Q3. Legal-vs-practical gap completeness

See Finding 3 above (SHOULD-FIX). Short version: the gap-as-research-artifact is queryable only for *artifact existence* (the 5 dual-axis rows), not for *content-field surfacing on the artifact*. The 35 legal-only `lobbyist_spending_report_includes_*` rows, the 13 legal-only `lobbyist_reg_form_includes_*` rows, and the 9 legal-only `lobbying_contact_log_includes_*` rows have no practical-axis sibling row that asks "does the portal actually expose this field?"

This is a real asymmetry under the corrected framing. It was rational under the pre-clarification framing (Compendium 2.0 was scoped as a typed-cell *contract* over what statutes describe; practical-axis cells were defined as the small set of portal-system observables that don't have a clean statute analogue). The framing shift in RESEARCH_ARC makes "legal-vs-practical gap" load-bearing in a way that wasn't designed for. The fix is a Prong-2-brief-writer design decision, not a v2 row-freeze re-opening.

## Q4. Naming-merge consistency

The naming-conventions merge (PR #10) renamed 15 row IDs + 1 doc-filename typo. The renames landed in:
- `compendium/disclosure_side_compendium_items_v2.tsv` (v2 row IDs, verified — all 15 new names present).
- `compendium/NAMING_CONVENTIONS.md` (the new contract).
- The mapping doc `compendium/README.md`'s cross-reference (`cpi_2015_projection_mapping` → `cpi_2015_c11_projection_mapping`).

The 9 per-rubric projection mapping docs at `docs/historical/compendium-source-extracts/results/projections/` **retain the pre-rename row IDs throughout** — by design per §10.1 ("preserves old→new pairs verbatim for readers of archived material"). Spot-checked CPI, HG, Newmark 2017 mappings: they reference `compensation_threshold_for_lobbyist_registration`, `registration_deadline_days_after_first_lobbying`, `lobbyist_report_includes_*`, `expenditure_itemization_de_minimis_threshold_dollars`, `ministerial_diaries_*`, `principal_or_lobbyist_reg_form_*` — all pre-rename.

This is consistent with the naming-conventions doc's "archived material is not rewritten" posture. But it has a downstream cost — see Finding 4 (OBSERVATION). When `phase-c-projection-tdd` writes projection functions referencing rows by name from these mapping docs, it MUST route through §10.1's resolver table or `src/lobby_analysis/row_id_renamer.py:RENAMES`. A pre-merge consistency check would prevent silent miscoding.

## Q5. P1-product-framing residue

Under the corrected framing ("Prong 1 is scaffolding for Prong 2 + queryable legal-vs-practical gap"), a row is "P1-product residue" if it satisfies *all* of: (a) no Phase C rubric reads it, (b) no portal-observable practical-axis counterpart, (c) doesn't surface in the queryable gap, (d) doesn't help cheapen Prong 2 via the schema-as-reference path.

Walking the 181 rows, the cleanest residue candidate is **OS-1: `separate_registrations_for_lobbyists_and_clients`** (legal, n_rubrics=0, status=firm-but-actually-unvalidated, path-b). Its D16 rationale explicitly says it was kept because it is "a real distinguishing statutory observable" — that is the "P1 as product" justification verbatim. Under "P1 as scaffolding": it earns its keep only if (i) the legal-vs-practical gap surfaces as observable on the portal (does the portal link or not link lobbyist + client filings), or (ii) a later rubric reads it. The D16 disposition notes "Watchpoint: if extraction reveals OS scoring would benefit from inclusion, OS-tabling reverses" — i.e., its survival is conditional on a future check. Flagging per the handoff's instructions, *not* proposing removal.

Other candidate clusters considered and *not* flagged:
- `def_target_*` (6), `def_actor_class_*` (2), `actor_*_registration_required` (11), `exemption_*` (2), `govt_*` (2), `public_entity_def_*` (3), `law_*` (2) — 28 rows total. All read by ≥1 Phase C rubric (CPI #196, Newmark/Opheim def battery, PRI A1–A11, etc.) and therefore earn projection rent. These are not residue under the corrected framing — they are the typed-schema reference Prong 2 reads against.
- The 50 practical-only rows — these are explicitly Prong-2-populated per RESEARCH_ARC, so they cannot be Prong-1 residue.
- Single-rubric rows (132 of 181) — single-rubric reading still earns Ralph-loop rent. Not residue.

**Net finding: 1 row (OS-1) is a plausible Q5 candidate. Cost to leave in: 1 cell × 50 states × N vintages. Low.**

## Out of scope / not checked

- Harness internals on `extraction-harness-brainstorm`: per the handoff, a parallel reviewer is auditing this. Not touched.
- Whether the `compendium-v2-promote` deprecation of `load_v1_compendium_deprecated` left any caller in the repo broken: I did not search the code tree.
- `STATUS.md` "Archived Research Lines" table consistency vs. `docs/historical/`: not checked.
- `PAPER_INDEX.md` / `PAPER_SUMMARIES.md` audit: not checked (handoff scoped this to the projection mappings + freeze log + naming-conventions doc).
- PRI 2010 mapping read in detail: skimmed for old-name occurrences; did not deep-read for projection-logic correctness.
- The 9 per-rubric projection mappings' factual claims against the source papers: per the README, a factual audit was completed 2026-05-13. Not re-audited.
- Track A (`oh-statute-retrieval`) and the OH 2007/2015 statute bundles: not in scope.
- `tools/freeze_canonicalize_rows.py` idempotence under the renames: not re-run.

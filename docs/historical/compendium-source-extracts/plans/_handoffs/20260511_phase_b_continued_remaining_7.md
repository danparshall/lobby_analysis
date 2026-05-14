# Phase B handoff (continued) — what changed during Sunlight mapping (3rd rubric)

**Originating plan:** [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md)
**Prior handoff:** [`20260507_phase_b_handoff.md`](20260507_phase_b_handoff.md) — read first; this handoff is delta on top of it.
**Originating convo (this handoff):** [`../../convos/20260511_sunlight_phase_b_mapping.md`](../../convos/20260511_sunlight_phase_b_mapping.md)
**Date:** 2026-05-11
**Audience:** the Phase B implementing agent for the remaining 7 rubrics — likely fresh-context.

---

## Why this handoff exists

The 2026-05-07 handoff covered the post-Phase-A state. Three Phase B mappings have shipped since (CPI 2015 C11, PRI 2010, Sunlight 2015). This handoff captures three decisions locked during the Sunlight session that affect every remaining mapping, plus per-rubric watchpoints surfaced during the cross-rubric grep.

**Read order for the next implementing agent:**
1. The locked plan: [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md)
2. The first handoff: [`20260507_phase_b_handoff.md`](20260507_phase_b_handoff.md)
3. This handoff (delta on top)
4. The three exemplar mappings: CPI, PRI, Sunlight in `../../results/projections/`
5. The Sunlight convo for narrative context on the new conventions: `../../convos/20260511_sunlight_phase_b_mapping.md`

---

## What's locked since the prior handoff

### Three new conventions

1. **Collect once, map to many.** Every compendium row is ONE statutory observable; multiple rubric projections read it at varying granularities. The Sunlight mapping made this explicit by annotating every candidate row with `[cross-rubric: <other readers>]`. **Continue this annotation discipline for every row you propose.** It's the seed for compendium-2.0 dedup.

2. **α — form-type split.** Where a rubric asks about content of "the spending report" OR "the registration form," split into separate compendium rows per form. Rationale: a state can require X on the spending report but not the registration form (HG Q5 vs Q20 is the canonical example). Granularity bias pays the extra-cell cost to preserve the distinction. Coarser rubrics' projections roll up via OR.

3. **β — Opheim AND-projection.** Opheim's `disclosure.legislation_supported_or_opposed` is one binary in `items_Opheim.tsv` that conflates bill-identifier AND position. Its projection reads two compendium cells AND'd: `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill`. Source TSV stays unedited. **Generalization:** when a source paper bundles N conceptually-distinct observables into one item, don't re-atomize the source — encode the bundling in the projection logic (AND/OR/derived expression as appropriate).

### Workflow fix

**Cross-rubric grep BEFORE drafting any compendium row, not after.** This session's Sunlight item 1 was almost proposed as a single-rubric row family until user pushback surfaced 7 other rubrics reading the same observables. **Mandatory workflow for the remaining 7 rubrics:**

Before drafting a compendium row entry, grep all 8 contributing-rubric TSV files PLUS the historical PRI 2010 disclosure-law rubric for the concept the row captures. Annotate the cross-rubric overlap in the row entry directly. Files to grep:

```
docs/active/compendium-source-extracts/results/items_HiredGuns.tsv
docs/active/compendium-source-extracts/results/items_FOCAL.tsv
docs/active/compendium-source-extracts/results/items_Newmark2017.tsv
docs/active/compendium-source-extracts/results/items_Newmark2005.tsv
docs/active/compendium-source-extracts/results/items_Opheim.tsv
docs/active/compendium-source-extracts/results/items_OpenSecrets.tsv
docs/active/compendium-source-extracts/results/items_CPI_2015_lobbying.tsv
docs/active/compendium-source-extracts/results/items_Sunlight.tsv
docs/active/compendium-source-extracts/results/items_LobbyView.tsv
docs/historical/pri-2026-rescore/results/pri_2010_disclosure_law_rubric.csv
```

Pre-approved bash pattern (list files explicitly, single grep call):
`grep -in -E "<pattern>" <file1> <file2> ...`

### Three threshold concepts must stay distinct in compendium 2.0

The Sunlight mapping surfaced and named these explicitly for the first time:

| Threshold type | Row name (working) | Reads |
|---|---|---|
| Lobbyist-status (compensation) | `compensation_threshold_for_lobbyist_registration` (CPI mapping) | CPI #197, HG Q2, Newmark 2017/2005 `def.compensation_standard`, Opheim `def.compensation_standard`, FOCAL scope.2 (partial) |
| Lobbyist-status (expenditure) | `expenditure_threshold_for_lobbyist_registration` (Newmark 2017 mapping, 2026-05-13) | Newmark 2017/2005 `def.expenditure_standard`, Opheim `def.expenditure_standard`, FOCAL scope.2 (partial) |
| Lobbyist-status (time) | `time_threshold_for_lobbyist_registration` (Newmark 2017 mapping, 2026-05-13; typed structured value `{magnitude, unit}` to accommodate hours/days/percent variants) | Newmark 2017/2005 `def.time_standard`, Opheim `def.time_standard`, Federal LDA 20%-of-work-time rule, FOCAL scope.2 (partial) |
| Filing-de-minimis | `lobbyist_filing_de_minimis_threshold_dollars` (PRI mapping; PRI D1) | PRI D1; possibly FOCAL scope.2 (combined) |
| Itemization-de-minimis | `expenditure_itemization_de_minimis_threshold_dollars` (Sunlight mapping) | Sunlight #3, HG Q15 |

Casual usage often conflates these. **The remaining rubric mappings must check** when they encounter a "threshold" item which of the five concepts is being read, and align with the corresponding compendium row. Don't propose new threshold rows without checking these five first.

**Correction logged 2026-05-13 (Newmark 2017 mapping session):** Earlier wording in this doc collapsed the three lobbyist-status threshold cells into a single row (with the readers column saying "Newmark/Opheim def.*_standard" as a family abbreviation). That collapse is wrong on its face — compensation / expenditure / time are independently extant in state statutes (federal LDA itself has compensation + time thresholds but no expenditure threshold), so the three cannot share one cell. Three separate typed cells, each read by the corresponding rubric binary via `IS NOT NULL`. The handoff's earlier per-rubric Newmark 2017 watchpoint ("Should read the existing CPI #197 cell ... Don't propose new binary rows") was shorthand for "follow the CPI #197 typed-cell-with-IS-NOT-NULL pattern" — not a literal claim that all three Newmark items read CPI #197. Corrected here for the Newmark-2005 and Opheim implementing agents who will encounter the same three concepts.

### Eight Phase B mappings done (as of 2026-05-13 late eve)

- [`../../results/projections/cpi_2015_c11_projection_mapping.md`](../../results/projections/cpi_2015_c11_projection_mapping.md) — 21 rows
- [`../../results/projections/pri_2010_projection_mapping.md`](../../results/projections/pri_2010_projection_mapping.md) — 69 rows touched (~52 new)
- [`../../results/projections/sunlight_2015_projection_mapping.md`](../../results/projections/sunlight_2015_projection_mapping.md) — 13 rows (11 cross-rubric)
- [`../../results/projections/newmark_2017_projection_mapping.md`](../../results/projections/newmark_2017_projection_mapping.md) — 14 rows (8 reused, 6 new) — added 2026-05-13
- [`../../results/projections/newmark_2005_projection_mapping.md`](../../results/projections/newmark_2005_projection_mapping.md) — 14 rows (14 reused, 0 new; **100% reuse**) — added 2026-05-13 pm
- [`../../results/projections/opheim_1991_projection_mapping.md`](../../results/projections/opheim_1991_projection_mapping.md) — 14 rows (14 reused, 0 new; **100% reuse**); 1 item un-projectable (`disclosure.other_influence_peddling_or_conflict_of_interest` catch-all → `unable_to_evaluate`) — added 2026-05-13 pm late
- [`../../results/projections/hiredguns_2007_projection_mapping.md`](../../results/projections/hiredguns_2007_projection_mapping.md) — **38 rows touched (16 reused, 22 new; 42% reuse, lowest of any single mapping pre-FOCAL)** — added 2026-05-13 eve. HG-distinctive observable cluster: Q7 amendment deadline, Q8 photograph, Q9 reg-form employer list, Q10 employment type, Q16-Q19 itemized-detail × 4, Q21 household members, Q22 business associations, Q24 outgoing campaign contributions disclosure, Q25 null/no-activity report, Q28-Q30 e-filing portal, Q31/Q32 access-tier 4-cell decomposition × 2 form types, Q33-Q37 portal/cost/aggregate cells, Q38 update cadence. **Plan/handoff figure of "47 items, Q1-Q38 + Q49-Q56" is incorrect** — HG has 48 items (Q1-Q48); disclosure-side scope = Q1-Q38 = 38 items. Documented as Correction 1 in the mapping doc.
- [`../../results/projections/focal_2024_projection_mapping.md`](../../results/projections/focal_2024_projection_mapping.md) — **57 rows touched (22 reused, 35 new; 38.5% reuse — new lowest single-mapping rate)** — added 2026-05-13 late eve. FOCAL-distinctive observable clusters: per-meeting contact_log (9 NEW: beneficiary-org, official-name, institution/dept, attendees, date, communication-form, location, materials-shared, topics-discussed), per-lobbyist descriptors (5 NEW reg-form-side: full-name, contact-details, legal-form, business-id, sector), openness quality features (5 NEW: ministerial-diaries-online, no-user-registration, open-license, unique-identifiers, linked-data, changes-flagged), financials-distinctive (5 NEW: income-by-source-type, FTE-count, time-spent-reporting, principal-side-total-expenditures, expenditure-per-issue, trade-association-dues), scope.1/scope.4 set-typed cells (2 NEW), 2025-only Lobbyist-list (1 NEW). `revolving_door.*` (2 items) DEFERRED per strict plan reading with revolving_door.1 flagged Open Issue FOCAL-1. **`contributions_from_others` parallel in FOCAL financials.* battery: NO PARALLEL** — Newmark 2017's row now single-rubric across 8 of 9 contributing rubrics; LobbyView is last check. 11 Open Issues + 3 Corrections + Promotions section.

---

## Remaining Phase B order (1 rubric)

> **Update 2026-05-13:** OpenSecrets 2022 has been **tabled** (was item 1 in the original 7-rubric order). See [`../../results/_tabled/opensecrets_2022_tabled.md`](../../results/_tabled/opensecrets_2022_tabled.md) for the tabling rationale (no published per-tier scoring definition; the recheck's "few-shot calibratable" criterion is softer than the branch's projection-vs-published bar) and the 3 OS-distinctive row candidates also tabled pending organic pickup by other rubrics or project-internal justification. Drop is reversible per reinstatement triggers documented there.
>
> **Update 2026-05-13 (pm):** Newmark 2005 shipped at 100% row reuse (14/14, zero new rows). **The Newmark 2017 mapping's speculation that Newmark 2005 confirms `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` as a cross-rubric row is FALSIFIED** — Newmark 2005 has only 6 disclosure items (vs 2017's 7), no `contributions_from_others` parallel.
>
> **Update 2026-05-13 (pm late):** Opheim 1991 shipped at 100% row reuse (14 row families / 15 in-scope items; 14 projectable, 1 catch-all un-projectable). Two structural promotions flagged for remaining mappings:
> - **`def_actor_class_elected_officials` / `def_actor_class_public_employees` row family is now 3-rubric-confirmed** (Newmark 2017 + Newmark 2005 + Opheim). Per the explicit guidance below ("three rubrics reading the same row family is high enough confidence to lock its design"), **Open Issue 1 from the Newmark 2017 mapping is now resolved-in-principle** — pull forward to compendium 2.0 freeze planning rather than indefinitely deferred. HG/FOCAL/LobbyView mappings need not re-examine.
> - **β AND-projection convention is now exemplified twice** (Sunlight 2026-05-11 locking + Opheim `disclosure.legislation_supported_or_opposed` 2026-05-13). Pattern is established: when a source bundles N conceptually-distinct observables into one item, encode the bundling in the projection logic, not in the source.
>
> **Update 2026-05-13 (eve):** HiredGuns 2007 shipped at 42% row reuse (16 of 38 in-scope items reused; 22 NEW rows — most of any single mapping). Phase B order below renumbered to **2 rubrics** (FOCAL, LobbyView). Three structural updates to flag for the remaining mappings:
> - **HG plan/handoff item-count correction.** Plan and prior handoff text say "47 items, Q1-Q38 + Q49-Q56." Both wrong — HG has 48 items (Q1-Q48); disclosure-side scope = Q1-Q38 = 38 items. Documented in HG mapping doc's "Corrections to predecessor mappings" section. The 50 × 38 = 1,900 per-cell HG ground-truth count (vs. the earlier 50 × 47 = 2,350) is the correct figure if CPI's per-state per-question scorecard is retrievable.
> - **HG is NOT a 4th reader of `def_actor_class_*`.** Walked Q1/Q2/Q3/Q4 — target/threshold/gateway/deadline observables, not actor-class definitional inclusion. Row family stays 3-rubric-confirmed. The handoff's prior speculation ("could be a 4th reader") was tentative and is now falsified.
> - **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` is now single-rubric across 7 of 9 contributing rubrics.** HG Q24 is OUTGOING campaign contributions disclosure (lobbyist → official), not the third-party-contributions INCOMING observable Newmark 2017 reads. Remaining promotion checks: **FOCAL `financials.*` battery and LobbyView** are the LAST chances to confirm this row cross-rubric. If both fail, the row is single-rubric across the entire contributing set — that's a compendium 2.0 freeze question (real Newmark-distinctive observable other rubrics miss, or Newmark over-atomization?).
>
> HG also surfaced 7 row-design Open Issues (HG-1 through HG-7) and 3 systemic issues all flagged for compendium 2.0 freeze planning; non-blocking for FOCAL and LobbyView.

Per the locked Phase C order (which Phase B mirrors):

1. ~~**Newmark 2017** (19 items)~~ — **DONE 2026-05-13**, see [`../../results/projections/newmark_2017_projection_mapping.md`](../../results/projections/newmark_2017_projection_mapping.md). 14 atomic items in scope (7 def + 7 disclosure; 5 `prohib.*` excluded); 14 distinct compendium rows touched (8 reused / 6 new).
2. ~~**Newmark 2005** (18 items)~~ — **DONE 2026-05-13 pm**, see [`../../results/projections/newmark_2005_projection_mapping.md`](../../results/projections/newmark_2005_projection_mapping.md). 14 atomic items in scope (7 def + 1 freq + 6 disclosure; 4 `prohib.*` + 1 `penalty_stringency_2003` excluded); **100% row reuse, zero new rows.** All three handoff watchpoints walked (PRI A-family no-overlap, three-threshold-cell confirmed against 2005 paper, penalty excluded).
3. ~~**Opheim 1991** (22 items, disclosure-side only)~~ — **DONE 2026-05-13 pm late**, see [`../../results/projections/opheim_1991_projection_mapping.md`](../../results/projections/opheim_1991_projection_mapping.md). 15 atomic items in scope (7 def + 1 freq + 6 information-category + 1 catch-all un-projectable; 7 `enforce.*` items excluded); **100% row reuse, zero new rows.** All four handoff watchpoints walked (β AND-projection applied as 2nd β use; `def_actor_class_*` 3-rubric-confirmed; cadence finer-cut confirmed; no contributions parallel).
4. ~~**HiredGuns 2007** (48 items, 38 in scope; Q39-Q47 enforce + Q48 cooling-off OOS)~~ — **DONE 2026-05-13 eve**, see [`../../results/projections/hiredguns_2007_projection_mapping.md`](../../results/projections/hiredguns_2007_projection_mapping.md). 38 atomic items in scope; **38 distinct compendium rows touched (16 reused / 22 new; 42% reuse — lowest single-mapping reuse rate).** All 7 handoff watchpoints walked (α split on Q5/Q20 applied; 5-tier reads on Q2/Q15 typed cells; Q23/Q24 partial-scope projection documented for Phase C tolerance; `contributions_from_others` no parallel; `def_actor_class_*` NOT a 4th reader; Q39-Q47 + Q48 OOS).
5. ~~**FOCAL 2024** (50 items, weighted aggregation)~~ — **DONE 2026-05-13 late eve**, see [`../../results/projections/focal_2024_projection_mapping.md`](../../results/projections/focal_2024_projection_mapping.md). 48 atomic items in scope (revolving_door.* deferred); **57 distinct compendium rows touched (22 reused / 35 new; 38.5% reuse — new single-mapping low).** All FOCAL watchpoints walked (revolving_door scope-qualifier deviation flagged FOCAL-1; contributions_from_others NO PARALLEL in financials.*; 2024→2025 application differences encoded). Sets up LobbyView as the only remaining Phase B mapping.
6. **LobbyView** (46 schema fields — schema-coverage rubric, different shape) — **next and final**

You can probably handle 1-2 per session given FOCAL's size and the LobbyView shape difference. Each session: cross-rubric grep, draft, sanity-check against existing 7 mappings for row reuse.

---

## Per-rubric watchpoints

### ~~OpenSecrets 2022~~ — TABLED 2026-05-13

See [`../../results/_tabled/opensecrets_2022_tabled.md`](../../results/_tabled/opensecrets_2022_tabled.md). The mapping attempt empirically confirmed the original 2026-05-07 Phase A1 DROP audit's structural finding: Cat 1 projects to {3, 4} from cells (no anchors for 0/1/2/5); Cats 2/3 partial-credit requires calibration-by-distribution rather than deterministic projection. Reinstatement triggers documented in the tabling doc. The 3 OS-distinctive row candidates (`separate_registrations_for_lobbyists_and_clients`, `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges`, `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate`) are also tabled pending organic pickup or project-internal need. The in-session/out-of-session cadence split is **not** tabled — Opheim 1991 reads the same split, so Opheim's mapping will introduce it.

### ~~Newmark 2017 (19 items)~~ — DONE 2026-05-13

See [`../../results/projections/newmark_2017_projection_mapping.md`](../../results/projections/newmark_2017_projection_mapping.md). 14 atomic items in scope (7 def + 7 disclosure; 5 `prohib.*` excluded); 14 distinct compendium rows touched.

**Six new rows added to compendium 2.0 by this mapping** (Newmark 2005 will reuse all of them):

| New row | Cell type | Used for |
|---|---|---|
| `def_actor_class_elected_officials` | binary; legal | elected-officials-as-lobbyists; Open Issue 1 — new third row family alongside `def_target_*` and `actor_*` |
| `def_actor_class_public_employees` | binary; legal | public-employees-as-lobbyists; same row-family question |
| `expenditure_threshold_for_lobbyist_registration` | typed `Optional[Decimal]`; legal | mirror of CPI #197 compensation cell |
| `time_threshold_for_lobbyist_registration` | typed `Optional[{magnitude, unit}]`; legal | accommodates federal LDA's 20%-of-work-time |
| `lobbyist_spending_report_includes_total_expenditures` | binary; legal | granularity-split from `_required` |
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` | binary; legal | Newmark-distinctive observable |

**Row design decisions locked this session** (relevant for remaining mappings):
- `disclosure.expenditures_benefiting_officials` reads the existing PRI bundle (gifts ∪ entertainment ∪ transport ∪ lodging × lobbyist/principal) projected as OR over the two actor sides. **Not split by benefit type.** HG Q23's gifts-specific granularity flagged for compendium 2.0 freeze, not now.
- The three `def.*_standard` items read **three separate typed cells** (compensation/expenditure/time), each via `IS NOT NULL`. See "Correction logged 2026-05-13" note under the threshold-concepts table above. Earlier wording in this handoff that suggested all three read CPI #197 was shorthand for the typed-cell pattern, not a literal claim.

**Watch out (carry-forward to remaining rubrics):**
- The `def_actor_class_*` row family is fragile. PRI A6 (or similar PRI A-family item) may overlap and force a fold. **Not directly walked in the Newmark 2017 session.** Newmark 2005 implementing agent should check PRI A-family content for `elected_officials` / `public_employees` reads before just reusing the new rows.

### ~~Newmark 2005 (18 items)~~ — DONE 2026-05-13 pm

See [`../../results/projections/newmark_2005_projection_mapping.md`](../../results/projections/newmark_2005_projection_mapping.md). 14 atomic items in scope (7 def + 1 freq + 6 disclosure; 5 OOS items: 4 `prohib.*` + 1 `penalty_stringency_2003`); **14 distinct row families touched, all reused (100%), zero new rows.**

**Three handoff watchpoints resolved:**
- **PRI A-family overlap check on `def_actor_class_*`: NO OVERLAP.** PRI A1–A11 (the `actor_*` row family) are structural/institutional-actor observables — does *the Governor's office as an institution* register when it lobbies. Newmark's `def_actor_class_*` is an individual-actor observable — does *an individual elected official personally lobbying* fall under the lobbyist definition. Conceptually adjacent but distinct; a state can answer YES to A7 (institution must register) and NO to `def_actor_class_elected_officials` (in-capacity individuals exempted), or vice versa. Both row families belong in the compendium; both are already there.
- **Three-threshold-cell verification against 2005 paper text: CONFIRMED.** Paper lines 120–121 enumerate "compensation standard, expenditure standard, and time standard in the deﬁnition of lobbying" as three separate components. Reuses the three typed cells the Newmark 2017 mapping introduced via `IS NOT NULL`.
- **`penalty_stringency_2003` exclusion: DOCUMENTED.** Enforcement-side, 2003-only, opaque sub-rubric, CO/TN/WV missing. Excluded per the disclosure-only Phase B qualifier; documented in the mapping doc's "Scope qualifier — 5 items OUT" table.

**Two structural findings worth carrying forward to the remaining rubrics:**
- **Newmark 2005 has 6 disclosure items, not 7.** Newmark 2017 added `disc.contributions_from_others` in revision; **Newmark 2005 does not have a parallel.** The Newmark 2017 mapping's speculation that 2005 would confirm `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` is **falsified.** That row remains Newmark-2017-distinctive within the contributing-rubric set; the open question is now whether HG 2007, FOCAL 2024, or LobbyView reads it — flagged in their respective per-rubric watchpoints below.
- **Newmark 2005's `freq_reporting_more_than_annual`** projects from the existing PRI E1h/E2h cadence row family via an 8-cell OR-projection (lobbyist + principal × {monthly, quarterly, triannual, semiannual}). Opheim 1991 also reads this row family at a *finer* binary cut (monthly-during-session-or-in-and-out-of-session only → 1; quarterly/semi-annual/annual → 0). The cadence row family is now confirmed as having three readers with different binary cuts on the same underlying cells; CPI #202's enum reading is a fourth.

### ~~Opheim 1991 (22 items, disclosure-side only)~~ — DONE 2026-05-13 pm late

See [`../../results/projections/opheim_1991_projection_mapping.md`](../../results/projections/opheim_1991_projection_mapping.md). 15 atomic items in scope (7 def + 1 freq + 6 information-category + 1 catch-all un-projectable; 7 `enforce.*` items excluded); 14 distinct row families touched, **all reused (100%), zero new rows.**

**All four handoff watchpoints walked:**
- **Watchpoint 1 — β AND-projection on `legislation_supported_or_opposed`: APPLIED.** Reads `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill` (both pre-existing from Sunlight's α form-type split). **Second concrete application of β** after the 2026-05-11 Sunlight locking — pattern is now established convention.
- **Watchpoint 2 — `def_actor_class_*` row family 3-rubric-confirmed: RESOLVED.** Opheim's `def.elective_officials` + `def.public_employees` are the third reader (after Newmark 2017 + Newmark 2005). Per this handoff's own guidance, **Open Issue 1 is pulled forward to compendium 2.0 freeze planning.** HG/FOCAL/LobbyView need not re-examine.
- **Watchpoint 3 — `disclosure.frequency` reads PRI cadence at finer cut: CONFIRMED.** Source quote (Opheim paper lines 115–118) verbatim confirms monthly-only-during-session-or-in-and-out → 1; quarterly/semi-annual/annual → 0. Tri-annual omitted from Opheim's prose; interpreted strictly as 0. Projection reads only the 2 monthly cells (lobbyist + principal) of the 8-cell PRI cadence family — Newmark 2005 reads the same family at the coarser >annual cut.
- **Watchpoint 4 — `contributions_from_others` parallel in 7-item info-category battery: NO PARALLEL.** Opheim's "sources of income" and "total income" structurally parallel Newmark's compensation pair (broken-down + total), not third-party-contributions. The catch-all (`disclosure.other_influence_peddling_or_conflict_of_interest`) could plausibly cover the observable but is operationally undefined and rejected as non-deterministic. **Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` stays single-rubric** in the current contributing set. Remaining checks: HG, FOCAL, LobbyView.

**Three structural findings worth carrying forward to the remaining rubrics:**
- **Opheim is the OLDEST contributing rubric (1988-89 vintage, published 1991).** Extends contributing-rubric ground-truth coverage to ~28 years end-to-end (1988-89 through 2015 via Opheim → Newmark 2005 ×6 panels → PRI 2010 → Sunlight 2015 + CPI 2015 + Newmark 2017). For BoS-sourced rows multiple rubrics read across multiple vintages, this gives Phase C a multi-decade cross-vintage stability check.
- **First contributing-rubric item with `unable_to_evaluate` projection.** Opheim's `disclosure.other_influence_peddling_or_conflict_of_interest` is operationally undefined (per `items_Opheim.md` §7: "the single most under-defined item in the index"). Excluded from projected partial; NOT defaulted to 0; NOT projected to a closest-adjacent row. Phase C tooling needs to support this outcome. When the deferred prohibitions / enforcement round expands compendium 2.0, the catch-all may admit a multi-cell OR projection or stay un-projectable.
- **Three row-family promotions from this mapping** (for compendium 2.0 freeze planning):
  - `def_actor_class_*` — 3-rubric-confirmed; Open Issue 1 resolved-in-principle.
  - Three lobbyist-status threshold cells (`compensation_threshold_*`, `expenditure_threshold_*`, `time_threshold_*`) — 3-rubric-confirmed.
  - Gifts/entertainment/transport/lodging bundle (`lobbyist_report_includes_*` + `principal_report_includes_*`) — 4-rubric-confirmed at combined granularity (PRI + Newmark 2017 + Newmark 2005 + Opheim; plus FOCAL `financials.10`).
- **One row family at maximum cross-rubric validation** (5 readers): `lobbyist_spending_report_includes_total_compensation` (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q13 + CPI #201 + PRI E2f_i = 6+ readers). This is the most-validated row in the compendium going into HG mapping.

### ~~HiredGuns 2007 (48 items total, 38 in scope)~~ — DONE 2026-05-13 eve

See [`../../results/projections/hiredguns_2007_projection_mapping.md`](../../results/projections/hiredguns_2007_projection_mapping.md). 38 atomic items in scope (Q1-Q38: 2 def + 8 ind-reg + 15 ind-spending + 2 emp-spending + 3 e-filing + 8 pub-access); 10 OOS items (Q39-Q47 enforce + Q48 cooling-off); **38 distinct compendium rows touched, 16 reused / 22 new (42% reuse rate — lowest single-mapping rate).**

**Seven handoff watchpoints resolved:**
- **Q5/Q20 α form-type split:** APPLIED. Pre-existing 6 Sunlight α rows reused exactly.
- **Q11/Q14/Q15 item-2 stack:** APPLIED. Q15's 5-tier ordinal reads `expenditure_itemization_de_minimis_threshold_dollars` (Sunlight #3) at finer granularity than Sunlight's 2-tier read.
- **Q13/Q27 compensation pair:** APPLIED. Q13 reuses Sunlight `lobbyist_spending_report_includes_total_compensation` (now 7-rubric-confirmed, most-validated row in compendium); Q27 reuses PRI `principal_report_includes_direct_compensation`.
- **Q2 5-tier on CPI #197 typed cell:** APPLIED. Finest read of `compensation_threshold_for_lobbyist_registration` in contributing set.
- **Q23 disclosure-only partial projection:** DOCUMENTED. Disclosure read = 1 pt of 3 max (limits + prohibition tiers OOS).
- **Q24 disclosure-only partial projection:** DOCUMENTED. Disclosure read = 1 pt of 2 max (prohibition tier OOS). HG Q24 is OUTGOING contributions disclosure — different observable from Newmark 2017's INCOMING third-party-contributions row.
- **`def_actor_class_*` 4th reader check:** NOT a 4th reader. HG Q1/Q2/Q3/Q4 read target/threshold/gateway/deadline. Row family stays 3-rubric-confirmed.

**Three structural findings worth carrying forward to FOCAL and LobbyView:**
- **HG introduces 22 new rows — the most of any single mapping.** 14 new legal-axis (Q7 amendment deadline, Q8 photograph, Q9 reg-form employer list, Q10 employment type, Q16-Q19 itemized-detail × 4, Q21 household members, Q22 business associations, Q24 outgoing campaign contributions, Q25 null/no-activity report + Q12 session-calendar metadata) + 8 practical-axis Q31/Q32 access-tier underlying cells + 5 other practical cells (Q28-Q30, Q33-Q38). After HG, the contributing-rubric set has converged at HG's atomization granularity for disclosure-side observables. **FOCAL is expected to be ≥70% reuse rate;** the FOCAL `financials.*` battery, `contact_log.*` battery, and `openness.*` battery should mostly read pre-existing rows at FOCAL granularity rather than introduce new structure.
- **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` is now single-rubric across 7 of 9 contributing rubrics.** Remaining checks: FOCAL `financials.*` battery (most likely candidate) and LobbyView. If both fail, the row is single-rubric across the entire contributing set — compendium 2.0 freeze question.
- **Q31/Q32 access-tier cell decomposition is novel.** 4 binary cells per side × 2 form types = 8 NEW practical-availability cells. These are the FIRST projection-friendly readers of Sunlight item-4's underlying observables (which were kept in compendium 2.0 even though Sunlight item-4 itself was excluded from projection). FOCAL `openness.1/4/5` provide finer-FOCAL-granularity overlap; LobbyView API infrastructure cells (`api_bulk_download`, `full_text_search_index`) are federal-side parallels.

### ~~FOCAL 2024 (50 items, weighted aggregation)~~ — DONE 2026-05-13 late eve

See [`../../results/projections/focal_2024_projection_mapping.md`](../../results/projections/focal_2024_projection_mapping.md). 48 atomic items in scope (2 `revolving_door.*` items DEFERRED per strict plan reading; revolving_door.1 flagged Open Issue FOCAL-1 for user reconsideration); **57 distinct compendium rows touched, 22 reused / 35 new (38.5% reuse — new single-mapping low rate).**

**Three handoff watchpoints walked:**
- **Watchpoint 1 — `contributions_from_others` parallel in `financials.*` battery: NO PARALLEL.** Walked all 11 FOCAL financials items. financials.1 = own total income; .2 = income per client; .3 = income source types (closest candidate — reads sources of OWN income, NOT third-party-INCOMING earmarked-for-lobbying); .4-9 = various consultant/expenditure observables; .10 = gifts (outgoing benefits); .11 = OUTGOING campaign contributions. **Newmark 2017's row remains single-rubric across 8 of 9 contributing rubrics.** LobbyView is the last remaining check.
- **Watchpoint 2 — Federal LDA jurisdiction validation.** US scored 81/182 = 45% per audit doc; with revolving_door.* deferred, projection max reaches 75/175 = 43% (6-point known under-scoring fully attributable to revolving_door.1 deferral). Tolerance documented in mapping doc's "Aggregation rule" and Phase C validation sections.
- **Watchpoint 3 — 2024→2025 application differences.** timeliness.1 + timeliness.2 MERGED in 2025 (read same compendium cell `lobbyist_directory_update_cadence`); "Lobbyist list" NEW indicator added to Relationships in 2025 (NEW row `principal_report_lists_lobbyists_employed`). Source TSV stays 2024; projection logic + per-country CSV handle the asymmetry.

**Three structural findings worth carrying forward to LobbyView (final remaining mapping):**
- **35 NEW rows is the most of any single Phase B mapping**, driven mostly by FOCAL's per-meeting contact_log atomization (9 NEW) + per-lobbyist descriptors atomization (5 NEW). LobbyView's federal LDA schema-coverage check will validate the atomization by checking which FOCAL-distinctive cells the LDA schema populates (LDA is quarterly aggregate so contact_log per-meeting cells will be uniformly NULL for federal jurisdiction; this is a known characteristic of LDA, not a flaw in compendium row design).
- **`def_target_*` family EXTENDED to 4 cells** with new `def_target_legislative_or_executive_staff` per FOCAL scope.3 partly-tier discrimination. LobbyView reads target-side identification; check whether LD-2's "Federal agencies contacted" field populates the 4-cell read (legislative + executive_agency + governors_office + staff).
- **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` final promotion check** is against LobbyView's federal LDA schema. LDA's LD-203 captures OUTGOING contributions (semi-annual under HLOGA), not INCOMING third-party-earmarked-for-lobbying. **Prediction: LobbyView NOT a reader.** Row stays single-rubric across the entire contributing set; compendium 2.0 freeze decision = KEEP per Newmark-distinctive-observable rationale.

### Historical content — pre-resolution watchpoints (kept for audit trail)

**Read first:** [`../../results/20260507_focal_a4_audit.md`](../../results/20260507_focal_a4_audit.md), the Suppl File 1 weights at [`../../results/items_FOCAL.tsv`](../../results/items_FOCAL.tsv), and the 1,372-cell per-country ground truth at [`../../results/focal_2025_lacy_nichols_per_country_scores.csv`](../../results/focal_2025_lacy_nichols_per_country_scores.csv).

**Aggregation rule (locked):** `score = base × weight`, base ∈ {0=no, 1=partly, 2=yes}, weight ∈ {1, 2, 3}. Max score = 182 (20×1 + 19×2 + 11×3 weights). US federal LDA's score in published L-N 2025 = 81/182 = 45% — the project's most important validation anchor (federal jurisdiction).

**Indicator category coverage:**
- `financials.*` (8 items) — strong overlap with CPI/HG/Newmark expenditure-disclosure stack
- `descriptors.*` (probably entity-description items)
- `contact_log.*` (multiple items including .10 position-on-bill, .11 bill-id-on-bill, .2 names-and-position-of-officials-contacted)
- `openness.*` (overlap with CPI #205-206 portal-availability stack)
- `relationships.*` (overlap with revolving-door — partly out-of-scope)
- `scope.*` (overlap with lobbyist-status threshold)
- `timeliness.*` (cadence overlap with CPI #199/#202, PRI E1h/E2h)
- `personnel.*` (some items OUT of scope per plan — out-of-scope for disclosure-only)
- `revolving_door.*` (deferred per plan)

**Watch:** Lacy-Nichols 2025 merged 2024's `timeliness.1` + `timeliness.2` into a single 2025 indicator. The TSV's per-row note flags this. Projection treats them as one merged indicator using the merged weight.

**Watch for `contributions_from_others` parallel.** Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row is **single-rubric across 6 of the 9 contributing rubrics** (CPI, PRI, Sunlight, Newmark 2005, Newmark 2017, Opheim — Newmark 2005 falsified the speculative parallel 2026-05-13 pm; Opheim's Watchpoint 4 walk 2026-05-13 pm late confirmed no parallel either). If HG mapping (next-up) also fails to confirm, FOCAL `financials.*` battery is the strongest remaining candidate — most likely the row that captures third-party-contributions-received as a distinct observable from `financials.10` (gifts) and the compensation/total-spending rows. **If FOCAL also fails**, LobbyView is the last check; if it also fails the row should be re-examined at compendium 2.0 freeze (single-rubric across the entire contributing set means either a real Newmark-distinctive observable other rubrics miss, or Newmark over-atomization).

### LobbyView (46 schema fields — DIFFERENT SHAPE)

**Tackle last.** LobbyView is schema-coverage, not score-projection:

```
coverage_check(compendium_rows, lobbyview_schema_fields) → coverage_map
```

Per the prior handoff: for each LobbyView field, does the compendium have a row that captures the same data? Validation is "for federal LDA, which LobbyView fields can the compendium populate from the LDA filing data?" → ideally ~100%.

**Three ambiguities flagged** (carry-forward from prior handoff):
1. `lobbyist_id` / `lobbyist_demographics` are in Kim 2025's GNN, NOT in the public LobbyView API
2. Kim 2018's bill-detection pipeline has no published precision/recall
3. `bill_position` is Wisconsin-only at the state level

Output: `results/projections/lobbyview_schema_coverage.md` (different shape from the other 9 mapping docs).

---

## After Phase B finishes

Per locked plan §Phase B done condition:

1. Union all 9 score-projection mapping docs' `compendium_rows` lists; de-dupe; save as `results/projections/disclosure_side_compendium_items_v1.tsv`.
2. Compendium-2.0 row freeze brainstorm (separate plan). The dedup pass uses the `[cross-rubric: …]` annotations from this session forward to identify which rows are most validated and which are deletion candidates.
3. Phase C: code projections under TDD per locked plan §Phase C.
4. Once Phase C validation lands, the statute-extraction harness rebuild can resume on the `statute-extraction` branch against compendium-2.0 row shape.

---

## Files this handoff is the index for

- Convo summary (this session): [`../../convos/20260511_sunlight_phase_b_mapping.md`](../../convos/20260511_sunlight_phase_b_mapping.md)
- Sunlight mapping doc: [`../../results/projections/sunlight_2015_projection_mapping.md`](../../results/projections/sunlight_2015_projection_mapping.md)
- Quick distribution tool: [`../../../../tools/sunlight_distributions.py`](../../../../tools/sunlight_distributions.py)

Non-repo artifacts produced this session (worth knowing but not part of compendium work):
- Project memory file: `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_use_preapproved_bash_patterns.md`
- Dotfiles note: `~/code/dotfiles/notes_bash_loop_permissions.md` (proposes adding `Bash(for *)` / `Bash(while *)` to global DENY rules)

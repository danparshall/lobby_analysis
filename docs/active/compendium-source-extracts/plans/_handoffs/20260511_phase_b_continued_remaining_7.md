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

### Four Phase B mappings done (as of 2026-05-13)

- [`../../results/projections/cpi_2015_c11_projection_mapping.md`](../../results/projections/cpi_2015_c11_projection_mapping.md) — 21 rows
- [`../../results/projections/pri_2010_projection_mapping.md`](../../results/projections/pri_2010_projection_mapping.md) — 69 rows touched (~52 new)
- [`../../results/projections/sunlight_2015_projection_mapping.md`](../../results/projections/sunlight_2015_projection_mapping.md) — 13 rows (11 cross-rubric)
- [`../../results/projections/newmark_2017_projection_mapping.md`](../../results/projections/newmark_2017_projection_mapping.md) — 14 rows (8 reused, 6 new) — added 2026-05-13

---

## Remaining Phase B order (6 rubrics)

> **Update 2026-05-13:** OpenSecrets 2022 has been **tabled** (was item 1 in the original 7-rubric order). See [`../../results/_tabled/opensecrets_2022_tabled.md`](../../results/_tabled/opensecrets_2022_tabled.md) for the tabling rationale (no published per-tier scoring definition; the recheck's "few-shot calibratable" criterion is softer than the branch's projection-vs-published bar) and the 3 OS-distinctive row candidates also tabled pending organic pickup by other rubrics or project-internal justification. Drop is reversible per reinstatement triggers documented there. Phase B order below renumbered to 6 rubrics.

Per the locked Phase C order (which Phase B mirrors):

1. ~~**Newmark 2017** (19 items)~~ — **DONE 2026-05-13**, see [`../../results/projections/newmark_2017_projection_mapping.md`](../../results/projections/newmark_2017_projection_mapping.md). 14 atomic items in scope (7 def + 7 disclosure; 5 `prohib.*` excluded); 14 distinct compendium rows touched (8 reused / 6 new).
2. **Newmark 2005** (18 items) — **next**
3. **Opheim 1991** (22 items, disclosure-side only)
4. **HiredGuns 2007** (47 items, disclosure-side only)
5. **FOCAL 2024** (50 items, weighted aggregation)
6. **LobbyView** (46 schema fields — schema-coverage rubric, different shape)

You can probably handle 2-3 per session given the locked conventions. Each session: cross-rubric grep, draft, sanity-check against existing CPI/PRI/Sunlight/Newmark2017 mappings for row reuse.

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

### Newmark 2005 (18 items) — next up

Essentially a subset/predecessor of Newmark 2017. After 2026-05-13's Newmark 2017 mapping ships, expected reuse rate for Newmark 2005 is ≥90% — almost all rows already exist in the Newmark 2017 mapping. Per `items_Newmark2005.tsv`: 4 def items (legislative_lobbying, administrative_agency_lobbying, elected_officials_as_lobbyists, public_employees_as_lobbyists) + threshold standards (compensation; check whether 2005 enumerates expenditure + time too — paper-text ambiguity from session-end greps) + 5 prohib (OUT) + 7 disc (all parallels of 2017's disclosure.* items) + 1 penalty_stringency_2003 (OUT — penalty/enforcement). Net disclosure-side scope ≈ 11–12 items, almost entirely reuse.

**Watch:**
- **Open Issue 1 check (`def_actor_class_*` row family) is now load-bearing.** Newmark 2017 mapping proposed this family; Newmark 2005 reuses the same rows. Before reusing, **grep PRI 2010 A-family items (`items_PRI_2010.tsv` `disclosure.A*`) for "elected" / "public employees" / "officials"** to confirm there's no PRI overlap that would force a fold into PRI's `actor_*` family. If overlap found, surface to user — do not unilaterally restructure.
- **Three threshold cells** (compensation / expenditure / time) now exist from Newmark 2017 mapping. Newmark 2005's threshold items reuse them via `IS NOT NULL`. Verify paper-text exact enumeration before mapping (the 2005 paper's verbatim is ambiguous in session-end greps).
- **`penalty_stringency_2003`** is enforcement-side and OUT of scope per disclosure-only Phase B qualifier. Excluded without further analysis. Document the exclusion in the per-rubric mapping doc (mirror the way Newmark 2017 mapping handled the 5 `prohib.*` exclusions).
- No FOCAL/Newmark cross-rubric stack design decision needed for 2005's `disc_expenditures_benefiting_officials` — the row design was locked during Newmark 2017 session (reuse PRI bundle, OR-projection over actor sides).

### Opheim 1991 (22 items, disclosure-side only)

- **Apply β here.** `disclosure.legislation_supported_or_opposed` projection reads `bill_id AND position` from compendium (locked this session).
- **Enforcement battery is OUT** (`enforce.*` items 23-27 — `file_independent_court_actions`, etc.). Disclosure-side only per plan.
- Watch `disclosure.*` items for cross-rubric reuse against CPI/PRI/Sunlight rows.
- Opheim is the oldest rubric (1991, CSG Blue Book 1988-89 baseline) — some compendium rows it reads may be obsolete (e.g., "fax disclosure" is not in Opheim but you might encounter equivalent obsolete observables). Treat obsolete rows as reading a NULL cell where appropriate.

### HiredGuns 2007 (47 items, disclosure-side only)

**Largest single mapping** in the remaining set. Key cross-rubric anchors:

- **Q5 (reg form) vs Q20 (spending report)** is the canonical α split case. Reuse the 6 form-type-split rows from Sunlight #1.
- **Q11 (gateway) / Q14 (categorized) / Q15 (itemized + threshold magnitude)** is the canonical item-2 stack. Q15 reads the same cell as Sunlight #3 (`expenditure_itemization_de_minimis_threshold_dollars`) at finer granularity.
- **Q13 (lobbyist compensation) / Q27 (principal compensation)** reuses Sunlight #5 / Newmark / CPI #201 / PRI E2f_i compensation rows.
- **Q2 (lobbyist-status threshold, 5-tier ordinal)** reads the CPI #197 cell.
- **Q39-Q47 enforcement is OUT** (plan: "Q39-Q47 enforcement = deferred"). **Q48 cooling-off is OUT**. Disclosure-only.
- Verify against the locked plan: disclosure-side scope per the plan §"Disclosure-side items (rough scope, by rubric)" gives HG Q1-Q38 + Q49-Q56 in scope; doublecheck Q49-Q56 are actually disclosure (accessibility-related per plan).

### FOCAL 2024 (50 items, weighted aggregation)

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

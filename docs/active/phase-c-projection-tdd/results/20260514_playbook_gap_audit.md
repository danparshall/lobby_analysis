<!-- Generated during: convos/20260514_rubric_plans_drafting.md (sub-session 0 of 5) -->

# Playbook gap audit — 6 remaining Phase C rubrics

**Date:** 2026-05-14
**Convo:** [`../convos/20260514_rubric_plans_drafting.md`](../convos/20260514_rubric_plans_drafting.md)
**Playbook under audit:** [`../plans/20260514_rubric_implementation_playbook.md`](../plans/20260514_rubric_implementation_playbook.md)

**Purpose:** Read intro + scope + aggregation + validation + Open Issues of each remaining spec doc to identify gaps the playbook didn't surface. These gaps will be baked into per-rubric plans (sub-sessions 1–3) so headless `claude -p` agents don't discover load-bearing surprises mid-implementation.

**Methodology:** Read 6 spec docs at `docs/historical/compendium-source-extracts/results/projections/<rubric>_projection_mapping.md`. Cross-reference against the playbook's per-rubric notes. Flag every load-bearing fact the playbook missed.

---

## Cross-cutting meta-patterns the playbook missed

Five patterns surface across multiple rubrics. These should be baked into every plan as shared conventions, not re-discovered per-rubric.

### Pattern 1 — "Disclosure-only Phase B" scope qualifier is a load-bearing convention applied to every remaining rubric

Every rubric in this branch's locked order has items excluded as enforcement / prohibition / penalty / cooling-off, per the disclosure-only Phase B qualifier from the originating plan. **The playbook does not mention this qualifier at all.** Per-rubric impact:

| Rubric | Items excluded | Reason | Max reproducible |
|---|---|---|---|
| Sunlight 2015 | 1 of 5 (item 4) | Data quality (5-tier conflates 3-4 sub-features + documented −1/−2 near-typo) | 4 of 5 items |
| Newmark 2017 | 5 of 19 (`prohib.*` × 5) | Prohibitions are restrictions, not disclosure requirements | `def.section_total` + `disclosure.section_total` (14 of 19) |
| Newmark 2005 | 5 of 18 (`prohib.*` × 4 + `penalty_stringency_2003`) | Prohibitions + enforcement-side penalty | 14 of 18 |
| Opheim 1991 | 8 of 22 (`enforce.*` × 7 + catch-all `other_influence_peddling`) | Enforcement + 1 operationally-undefined catch-all | 14 of 22 |
| HG 2007 | 10 of 48 (Q39–Q47 enforcement + Q48 cooling-off) | Enforcement + revolving-door prohibition | 83 of 100 |
| FOCAL 2024 | 1 of 50 (`revolving_door.2`) **after FOCAL-1 resolution** | Single enforcement-adjacent item; `revolving_door.1` was pulled IN scope by user decision because it's a registration-form disclosure observable | 180 of 182 |

**Implication:** Every plan needs a "Scope qualifier" section up front that names which items are excluded and why. Without this, a headless agent will try to project enforcement / prohibition items and either fabricate scoring rules or fail loudly mid-implementation.

**FOCAL-1 precedent:** The user pulled FOCAL `revolving_door.1` IN scope on 2026-05-13 because the cell is a registration-form disclosure observable, regardless of FOCAL's "revolving door" category label. The precedent: **scope-qualifier decisions are per-item, not per-category.** Plans should flag any borderline items for user review rather than defaulting to "category name says enforcement = exclude."

### Pattern 2 — Validation regime breaks into three tiers, not the playbook's three regimes

The playbook's regimes (1) per-state per-atomic-item, (2) per-state per-sub-aggregate, (3) no per-state ground truth — are correct in shape but the actual rubrics break out differently:

| Validation tier | Rubrics | Ground-truth cells | Phase C check |
|---|---|---|---|
| **Strong: per-state per-atomic-item** | CPI 2015 C11 (700 cells, completed); HG 2007 (1,900 cells **if scorecard retrievable**); FOCAL 2024 (1,372 cells, **28 countries — US federal only, NO per-state**) | Parameterize tests over all 50 states × atomic items | Helper per item validated against published cells; aggregation against published per-state score within ±1 |
| **Medium: per-state sub-aggregate only** | Newmark 2017 (100 cells: 2 sub-aggregates × 50 states); PRI 2010 (per-state per-sub-aggregate, completed — 50 × ~13 cells) | Per-item helpers fixture-tested; aggregation tested at sub-aggregate layer | Sub-aggregate match within ±1; per-item validation borrowed from cross-rubric overlap |
| **Weak-inequality only** | Newmark 2005 (300 cells × 6 panels — only `partial ≤ paper_total` checkable); Opheim 1991 (47 cells × 1 vintage — same; 3 states MT/SD/VA missing) | Fixtures + per-item; aggregation tested only at the `our_partial ≤ paper_total` inequality | The weak inequality must hold; cross-rubric overlap is the actual quality check |

**Implication:** Plans need an explicit "Validation regime" section choosing one of the three tiers and naming the consequences. Newmark 2005 and Opheim 1991 plans should NOT promise tolerance checks they cannot deliver.

### Pattern 3 — `unable_to_evaluate` convention is broader than the playbook implied

Playbook mentions Opheim's catch-all as "1 catch-all un-projectable, document and skip." Reality: the `unable_to_evaluate` convention applies across **every** rubric for OOS items:

- Items excluded by scope qualifier → `unable_to_evaluate`, **not zeroed**
- Items un-projectable due to operational under-definition (Opheim catch-all) → `unable_to_evaluate`
- Items requiring portal observation when only statute data is available (HG Q35–Q37 agency-self-report) → `unable_to_evaluate` for Phase C; revisit when Phase D extraction lands

**Why "not zeroed" matters:** Zeroing OOS items would understate `our_partial`, making the weak-inequality check `our_partial ≤ paper_total` look better than it should. The correct invariant is "the items we COULD project sum to a value that's ≤ the published total, where the gap accounts for items we couldn't project." Plans should adopt the convention explicitly.

### Pattern 4 — Same-row-different-binary-cut is a recurring per-item helper pattern

The playbook's cheat sheet lists patterns (binary → 0/1, 5-tier → passthrough, AND, OR, form-type partition, etc.) but misses one that recurs across the remaining rubrics:

**Pattern: rubric-specific binary cut on a shared multi-cell row family.**

Concrete instances:
- **PRI cadence row family** (8 binary cells: lobbyist/principal × monthly/quarterly/triannual/semiannual):
  - **Newmark 2005** reads OR over all 8 cells (`freq_reporting_more_than_annual`)
  - **Opheim 1991** reads OR over 2 cells (lobbyist monthly + principal monthly only)
  - PRI 2010 reads at full atomization
  - CPI 2015 reads as enum-derived
- **Threshold typed cells** (`compensation_threshold_*`, `expenditure_threshold_*`, `time_threshold_*`):
  - **HG 2007** Q2: 5-tier ordinal on dollar magnitude
  - CPI 2015: 3-tier read
  - **Newmark/Opheim**: binary `IS NOT NULL`
  - **FOCAL** scope.2: combined "any threshold" with scorer-judgment cutoff

**Implementation implication:** Per-item helpers in declarative-table modules need a 3-tuple spec `(row_or_family, axis, cut_function)` not just `(row, axis)`. Plans for Newmark 2005, Opheim, HG, and FOCAL should document the per-item cut function explicitly rather than embedding it in the helper.

### Pattern 5 — Row-promotion meta-pattern (`X-rubric-confirmed`) is the seed of Phase 4 cross-rubric audit

Every spec doc tracks "X-rubric-confirmed" status of rows it reads. Post-FOCAL state across all 6 remaining rubrics:

| Row | Confirmation level | Implication |
|---|---|---|
| `lobbyist_spending_report_includes_total_compensation` | **7-rubric-confirmed** | Most-validated row in the compendium. Lock at compendium 2.0 freeze. |
| Gifts/entertainment/transport/lodging bundle | **5-rubric-confirmed** | Lock. |
| `lobbyist_spending_report_includes_bill_or_action_identifier` | **5-rubric-confirmed** | Lock; α form-type split necessary. |
| `compensation_threshold_for_lobbyist_registration` | **5-rubric-confirmed at varying granularities** | Cleanest typed-cell example. |
| `def_actor_class_elected_officials` / `_public_employees` | **3-rubric-confirmed** | Newmark 2017 introduced; Newmark 2005 + Opheim reuse. Lock at compendium 2.0 freeze. |
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` | **1-rubric (Newmark-2017-distinctive)** | Genuine over-atomization or real Newmark-distinctive? Real per Newmark mapping; KEEP. |

**Implication:** Each plan should produce a "row-promotion delta" section in its results doc, so the cross-rubric audit (Phase 4, currently deferred) has explicit input. Plans for rubrics that introduce new rows (FOCAL especially — 36 new) need explicit lists of those new rows.

---

## Per-rubric gaps

### Sunlight 2015 (rubric #3) — already covered in chat; recapping for completeness

Playbook said: 13 rows, 11 cross-rubric, α form-type split, β Opheim AND, "collect once map many."

**Gaps:**
1. **Item 4 is EXCLUDED** (audit decision 2026-05-07). Projection covers **4 items**, not 5.
2. **Cannot reproduce published Total or letter Grade.** Per-item validation only against the published per-state CSV's 4 in-scope item columns.
3. **Letter grade exists in CSV** (A/B/C/D/F per state) — but our projection can't reproduce it. Playbook said "probable: no letter grade"; that's wrong-direction.
4. **Tier scale is signed** (`−1 to 2`, `−2 to 2`) not 0/1 or 0/25/.../100. Aggregation is arithmetic sum of signed tiers, not sum of binaries.
5. **Footnote markers** on CSV cells (`*`, `**`, `^`, `^^`) need stripping before comparison; cells with markers are caveated validation points.
6. **Item 1 is compound:** 6 compendium cells → 3 form-agnostic flags via OR → nested-tier table (−1/0/1/2). Item 2 is similar (3 cells → nested tier). Item 5 is OR-projection over 3 cells → binary tier. Item 3 reads a typed cell. **All 4 in-scope items have bespoke compound logic — recommend function-per-item.**

### Newmark 2017 (rubric #4)

Playbook said: 14 rows, 8 reused, 6 new, "load-bearing r=0.04 CPI↔PRI-disclosure correlation," index-based, possible reverse-scoring.

**Gaps:**
1. **5 `prohib.*` items OUT of scope** (disclosure-only Phase B). Cannot reproduce `index.total` (0–19); CAN reproduce `def.section_total` (0–7) + `disclosure.section_total` (0–7) = 100 sub-aggregate cells per state × 50 = **medium-validation tier**.
2. **No reverse-scoring** in disclosure-side items. The "Newmark may follow PRI's B1/B2 pattern" speculation in the playbook was for prohibitions, which are OOS here.
3. **Index-based ≠ binary-only.** 3 of the 7 def items are typed-cell `IS NOT NULL` reads (compensation / expenditure / time thresholds). Function-per-item OR declarative table with cut-function annotation.
4. **6 NEW rows introduced** (which Newmark 2005 + Opheim reuse): `def_actor_class_elected_officials`, `def_actor_class_public_employees`, `expenditure_threshold_for_lobbyist_registration`, `time_threshold_for_lobbyist_registration`, `lobbyist_spending_report_includes_total_expenditures`, `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`. **Newmark 2017 must land before Newmark 2005 or Opheim** because they depend on these new rows.
5. **`TimeThreshold` is a structured cell type** (`{magnitude: Decimal, unit: enum{hours_per_quarter, hours_per_year, days_per_year, percent_of_work_time, ...}}`). Not a simple `Optional[Decimal]`. Plan needs to specify whether v2-compendium loader supports this structured type or if it loads as opaque dict.
6. **Two no-variation items** (`def.legislative_lobbying`, `disclosure.expenditures_benefiting_officials`) — universally TRUE in 2015. Cells still extracted; projection still reads. Don't optimize them away.
7. **Newmark Table 2 published sub-aggregates** (`def.section_total`, `prohib.section_total`, `disclosure.section_total`, `index.total`) per state. Ground-truth loader returns these 4 numbers per state; only the first and third are checkable against `our_partial`.

### Newmark 2005 (rubric #5)

Playbook said: 14 rows, 100% reuse of Newmark 2017, "near-clone of 2017, consider extracting a shared helper."

**Gaps:**
1. **4 `prohib.*` items + `penalty_stringency_2003` OUT of scope.** Different exclusions than Newmark 2017 — `prohib_expenditures_over_threshold` is conceptually distinct from the `expenditure_threshold_for_lobbyist_registration` def cell. Plan needs to call out this distinction explicitly.
2. **NOT a near-clone of Newmark 2017.** Newmark 2005 has:
   - **4 sections** (def + freq + prohib + disclosure), not 3
   - **1 frequency item** (`freq_reporting_more_than_annual`) — absent in Newmark 2017
   - **6 disclosure items**, not 7 (no `contributions_from_others`)
   - **6 panels** (1990-91, 1994-95, 1996-97, 2000-01, 2002, 2003) — 300 ground-truth totals vs Newmark 2017's 50 cells × 4 sub-aggregates
3. **Weak-inequality validation regime.** Newmark 2005 publishes per-state TOTALS only — no sub-aggregate breakdown. Phase C check is `our_partial ≤ paper_total` only. **The playbook's "100% reuse" framing implies Phase C utility comparable to 2017; reality is much weaker.**
4. **Newmark 2005's role is temporal-coverage validation** (cross-vintage stability check) — NOT direct sub-aggregate validation. Plan should frame this honestly.
5. **`freq_reporting_more_than_annual` projection reads 8 cadence cells OR'd** (lobbyist + principal × monthly/quarterly/triannual/semiannual). NEW projection pattern (same-row-different-binary-cut, see Pattern 4). This is the FIRST place this pattern is exercised in a Phase C module.
6. **Shared-helper opportunity is real but narrower than playbook said.** Newmark 2005 + Newmark 2017 share: gifts/entertainment OR projection, `def_actor_class_*` binary reads, threshold `IS NOT NULL` reads. They do NOT share aggregation rule, sub-aggregate structure, or validation regime. Helper should extract per-row-family reads, not module-level abstraction.

### Opheim 1991 (rubric #6)

Playbook said: 14 row families / 15 in-scope items, 100% reuse, β AND-projection 2nd concrete use, 1 catch-all un-projectable.

**Gaps:**
1. **7 `enforce.*` items + 1 catch-all OUT of scope.** Cannot reproduce `index.total` (0–22); max reproducible = 14 (7 def + 7 disclosure with 1 catch-all dropped).
2. **47 states, NOT 50** — Montana, South Dakota, Virginia have no Opheim score (paper line 176). Plan needs to handle the 3 missing states explicitly.
3. **Weak-inequality validation regime** — same as Newmark 2005. Only 47 per-state `index.total` ground-truth cells available. No sub-aggregate breakdown published.
4. **1988-89 vintage** — earliest cross-rubric ground truth. Opheim's role is temporal-depth validation extending the contributing-set coverage to ~28 years.
5. **`disclosure.frequency` reads PRI cadence at finer cut** (monthly only — 2 cells OR'd) than Newmark 2005's same-family read (8 cells OR'd). The plan should explicitly show this 2-vs-8 cell distinction.
6. **`disclosure.legislation_supported_or_opposed` β AND-projection** reads `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill` — **both pre-existing from Sunlight α split**. Plan needs to specify Sunlight must land first to confirm the row designs.
7. **Catch-all `other_influence_peddling_or_conflict_of_interest`** is the canonical `unable_to_evaluate` example. Plan needs the convention specified (not zeroed; excluded from partial).
8. **No new rows introduced** — all 14 row families pre-exist from CPI / Sunlight / PRI / Newmark 2017.

### HG 2007 (rubric #7)

Playbook said: 38 rows, 16 reused, 22 new, 42% reuse, **ground-truth retrieval depends on `oh-statute-retrieval` Track A**.

**Gaps:**
1. **HG ground truth is the CPI 2007 per-state per-question scorecard** — NOT statute extraction. **The scorecard has NOT been retrieved into this branch's archive.** The playbook's "Track A dependency" is conflating two distinct retrievals:
   - **HG per-state scorecard** (CPI's 2007 scorecard pages, historical URL `publicintegrity.org/politics/state-politics/influence/hired-guns/` — current availability uncertain). This is what HG validation needs.
   - **OH statute extraction** (Track A `oh-statute-retrieval` for the OH-specific HG sub-task). This is OOS for Phase C HG projection module; it's Track B (extraction harness) work.

   Plan must specify scorecard retrieval as a separate Phase 0 pre-flight task with a STOP clause if it's unrecoverable.
2. **22 NEW rows include 13 practical-availability cells** (Q28–Q38: portal observability — online filing, copy costs, lobby list update cadence). These won't populate from statute extraction; they require portal observation. **Phase C can validate the 22 legal-axis items; the 13+ practical-axis items are Phase D (extraction pipeline) targets** with statute-based projection producing `unable_to_evaluate` for these cells.
3. **Aggregation has per-item point values** (not just 0/1). Per-category maxima: Def 7 + IndReg 19 + IndSpending 29 + EmpSpending 5 + EFiling 3 + PubAccess 20 + Enforcement 15 + RevolvingDoor 2 = 100. **5-tier and 4-tier ordinals on individual items** (Q2 5-tier, Q4 5-tier, Q12 4-tier, Q31/Q32/Q38 4-tier). Pattern is closer to FOCAL than to PRI's mostly-binary atomization.
4. **HG Q15 conditional cascade** — Q16–Q19 are conditional on Q15. Plan needs to specify the conditional-cascade behavior (if Q15 = 0, do Q16–Q19 default to 0 or are they `unable_to_evaluate`?).
5. **HG Q12 derived projection** requires session-calendar metadata (state legislative session lengths). New metadata cell needed OR derive via heuristic. Open Issue HG-5 in the spec doc — flag for plan.
6. **HG Q23 / Q24 partial-scope projection** — disclosure-side reads 1/3 and 1/2 of published points respectively. Maximum systematic under-scoring per state = 3 pts on the 100-point scale. Plan needs to document validation tolerance accordingly.
7. **CPI 2015 C11 is HG 2007's compression** — Phase C audit between CPI projection (already shipped) and HG projection (this plan) is the canonical cross-rubric audit case. Plan should produce explicit cross-rubric verification on the 8 rows both read.

### FOCAL 2024 (rubric #8)

Playbook said: 58 rows post-FOCAL-1 expansion, 22 reused, 36 new, 37.9% reuse, "L-N 2025 Suppl File 1 weights, 1,372-cell ground truth, US LDA score is 81/182 = 45%."

**Gaps:**
1. **NO per-state US ground truth.** FOCAL has been applied to 28 countries and to US federal LDA only — never to US states. 50 US states get projected but cannot be directly validated against FOCAL. **Cross-rubric is the ONLY check for state FOCAL projections.** This is the opposite regime from HG/CPI/Newmark (state-level ground truth, no federal).
2. **FOCAL-1 resolution (2026-05-13)** pulled `revolving_door.1` IN scope, kept `revolving_door.2` OUT. The playbook's "58 rows" count reflects the post-FOCAL-1 state. Plan needs to know this is a precedent the user set — scope decisions are per-item, not per-category.
3. **Aggregation is weighted sum**, not unweighted: `per_indicator_score = base × weight` where `base ∈ {0=no, 1=partly, 2=yes}` and `weight ∈ {1, 2, 3}`. Weights are 20×W1 + 19×W2 + 11×W3 = 91 → max 182. **FOCAL's L-N 2025 Suppl File 1 Table 4 is the canonical weight source.**
4. **Multiple cell types beyond binary:**
   - **`Set[enum]`** (scope.1 actor types, scope.4 activity types) — 9-element + 8-element sets
   - **`TimeThreshold`** structured value (scope.2)
   - **`UpdateCadence`** enum (timeliness.1+.2 merged)
   - **`SectorClassification`** typed value (descriptors.5)
   - **Various typed Optionals** for thresholds, counts, FTEs, time-spent
5. **Scorer-judgment cutoff in scope.2** (`LOW_DOLLAR_CUTOFF`, `LOW_TIME_CUTOFF`). FOCAL paper acknowledges the subjectivity (line 1206-1208). **Plan must pick a calibrated cutoff** (candidate: $1000 / 8 hours / 5% time). Document calibration in plan; this is the only scope.2-style scorer-judgment item.
6. **2024 → 2025 application differences encoded in projection logic**, not source TSV:
   - `timeliness.1 + timeliness.2` **merged** in 2025 (Lacy-Nichols 2025 line 202-204) — both 2024 indicators map to the same compendium cell
   - **NEW indicator "Lobbyist list"** added to Relationships in 2025 — not in `items_FOCAL.tsv`, but is in the per-country CSV ground truth
   - Plan needs to specify: per-item projections are written against 2024 numbering; ground-truth comparison uses 2025 numbering
7. **36 NEW rows is the largest single-rubric addition.** Per-battery breakdown: descriptors (5 new), contact_log (9 new), openness (5 new), relationships (3 new), revolving_door (1 new from FOCAL-1), financials (5 new), scope (4 new), timeliness (1 new), plus the 2025-only "Lobbyist list" mirror.
8. **11 Open Issues in spec doc** — the most of any rubric. Plan should triage which need user resolution before launch vs which can be deferred.
9. **US LDA validation target: 81 raw points exactly.** After FOCAL-1, the previously-documented +6pt tolerance closes; raw-points match exactly (denominator shift causes ≤1pp percentage delta only).

---

## Implications for the 4 remaining plan-drafting sub-sessions

### Stream 1 grouping (Sunlight + Opheim) — revisit?

Playbook implied these share the β AND-projection convention. They do. But structurally:

- **Sunlight 2015**: 4 in-scope items, all with bespoke compound logic (nested tier tables, OR projections, typed-cell reads). Function-per-item likely. 13 rows touched.
- **Opheim 1991**: 14 in-scope items + 1 un-projectable, all reusing pre-existing rows (3 cells from Sunlight α split, 8 cells from PRI cadence at finer cut). Weak-inequality validation. Largely a declarative-table dispatch.

They share the β AND-projection (Sunlight item 1 introduces the rows; Opheim's `disclosure.legislation_supported_or_opposed` reuses via AND). **Stream 1 dependency direction is one-way: Sunlight must land first; Opheim then piggybacks.**

**Recommendation:** Keep them in Stream 1 with Sunlight first. The convention-sharing argument holds.

### Stream 2 grouping (Newmark 2017 + Newmark 2005) — wrinkle

Newmark 2005 is NOT a near-clone of Newmark 2017. They share row reads but differ on aggregation, sub-aggregate structure, validation regime, and vintage count.

**Recommendation:** Keep them in Stream 2 with Newmark 2017 first. Newmark 2017 must introduce the 6 new rows; Newmark 2005 then reuses them. After Newmark 2017 lands, draft Newmark 2005 plan to capture the cadence projection + weak-inequality validation regime (which Newmark 2017 doesn't have). Shared-helper opportunity is at the per-row-family level (gifts OR, threshold IS-NOT-NULL, def_actor_class binary), not the module level.

### Stream 3 (FOCAL alone) — substantially heavier than the playbook suggests

FOCAL is the biggest rubric. Plan complexity may exceed all other plans combined:

- 49 in-scope indicators (after FOCAL-1)
- 36 NEW rows
- Federal-only US ground truth (no per-state validation possible directly)
- Set-typed cells and structured value types (atypical)
- Scorer-judgment cutoff for scope.2
- 2024 numbering with 2025 projection logic asymmetry
- L-N 2025 supplement weight extraction work
- 11 Open Issues in spec doc

**Question to surface to user:** Is FOCAL really a single plan? Or should it be batched into pieces (legal-side cells, practical-side cells, contact_log cells) like a multi-PR feature?

### HG 2007 — two retrieval blockers, not one

The playbook flagged "depends on Track A `oh-statute-retrieval`." That's only half the story:

- **Blocker 1 — HG per-state scorecard retrieval.** CPI's 2007 scorecard pages at `publicintegrity.org/politics/state-politics/influence/hired-guns/` — current availability uncertain. **NOT a Track A task.** Plan should specify scorecard retrieval as Phase 0 pre-flight with STOP clause if unrecoverable.
- **Blocker 2 — OH statute extraction (Track A).** This is for the OH-specific HG sub-task and is in `oh-statute-retrieval` worktree's scope. Track A status check needed before launching HG plan.

If scorecard isn't retrievable, validation regime falls back to weak-inequality only (50 states × 1 published-total cell × `our_partial ≤ paper_total`). Plan should have both paths.

---

## Convention proposals to bake into all 6 plans

To prevent each plan from re-inventing conventions:

1. **Scope qualifier** — every plan opens with a "Scope qualifier" section naming excluded items + reason + max-reproducible total. STOP clause: if a borderline item surfaces (FOCAL-1-style), ask user before deciding.
2. **`unable_to_evaluate` convention** — OOS items, un-projectable items, and Phase D portal-observation cells produce `unable_to_evaluate` (not zeroed). Excluded from partial; weak-inequality check `our_partial ≤ paper_total` holds.
3. **Validation regime declaration** — every plan declares Strong / Medium / Weak validation regime up front. Test structure follows from this; weak-regime plans don't promise tolerance checks they can't deliver.
4. **Row-promotion delta** — every plan's results doc has a "Row-promotion delta" section listing which rows shifted N → N+1 confirmation. Feeds Phase 4 audit.
5. **Spec-doc-vs-v2 cross-check** — load-bearing per the playbook. Every plan's Phase 0 pre-flight must run the row-name cross-check; STOP and write a diagnostic doc if drift exceeds 10% of expected rows.
6. **Per-item helper return signature** — every plan specifies per-item helper returns either:
   - `int` in some rubric-specific range (CPI 0..100; PRI 0/1 or 0..15; HG 0..4; FOCAL `base × weight`); OR
   - `Literal["unable_to_evaluate"]` for un-projectable items.
   Reverse-scoring lives in rollup, NOT in per-item helper (playbook's existing convention, reaffirmed).
7. **Function-per-item vs declarative table** — decision per rubric based on item-shape diversity:
   - Sunlight 2015 → function-per-item (4 bespoke items)
   - Newmark 2017 → declarative table (14 binary + 3 threshold IS-NOT-NULL)
   - Newmark 2005 → declarative table (similar shape)
   - Opheim 1991 → declarative table (14 binary, 1 un-projectable handled by exclusion)
   - HG 2007 → hybrid (point-valued items, conditional cascades, multiple ordinal tiers — declarative with bespoke fallbacks)
   - FOCAL 2024 → hybrid or function-per-item (50 indicators, multiple cell types, weighted aggregation)

---

## Decisions surfaced for user

1. **Should the FOCAL plan be split into pieces?** Or single-plan with explicit phasing inside it?
2. **Should HG plan be launched on faith that the CPI scorecard is retrievable, or held until retrieval is confirmed?** If retrievable: per-state per-item validation regime. If not: weak-inequality only.
3. **Are Stream 1 and Stream 2 still the right groupings given the structural deltas?** Stream 1 (Sunlight → Opheim) and Stream 2 (Newmark 2017 → Newmark 2005) — confirmed feasible per audit. No regrouping recommended.
4. **FOCAL-1-style precedent — any other borderline scope decisions to anticipate?** Plans for Newmark 2017, Newmark 2005, Opheim include their respective `prohib.*` / `enforce.*` exclusions per strict reading of the disclosure-only qualifier. If the user wants any pulled IN (parallel to `revolving_door.1`), flag before plan drafting.

---

## Provenance

This audit reads each spec doc's intro + scope qualifier + aggregation + validation + Open Issues + summary. It does NOT read every per-item mapping section — that level of detail goes into each rubric's plan, not into this cross-cutting gap audit. Sub-sessions 1–3 will read the per-item sections during plan drafting.

Audit completion timestamp: 2026-05-14, Dans-MacBook-Air.local.

# Sunlight 2015 — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (third rubric, after CPI and PRI).
**Handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_Sunlight.tsv`](../items_Sunlight.tsv) (5 items; **item 4 excluded** from this projection per the 2026-05-07 audit decision).
**Audit:** [`../20260507_sunlight_atomic_audit.md`](../20260507_sunlight_atomic_audit.md) — documents the item-4 exclusion rationale.
**Predecessor mappings (for conventions):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md).

---

## Doc conventions

The four conventions established in the CPI mapping doc apply here verbatim (compendium row IDs are working names, not cluster-derived; typed cells live on `MatrixCell.value`; granularity bias = split on every distinguishing case; axis = `legal_availability` for de jure / `practical_availability` for de facto). One new convention added in this session:

- **"Collect once, map to many."** Each compendium row is a single statutory observable; multiple rubric projections read it. Where a candidate row in this doc is ALSO read by other rubrics, the row entry includes a `[cross-rubric: …]` annotation listing the other readers. This is the seed for the compendium-2.0 deduplication pass — rows that several rubrics read at varying granularities will be merged (or aliased) so the row is observed and extracted once. None of the rows proposed here should be assumed unique to Sunlight; **Sunlight is a shallow rubric whose value is cross-rubric redundancy, not novel observables.**

## Aggregation rule

Sunlight published:
- 5 per-indicator scores per state (in [`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`](../../../../papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv))
- `Total` = arithmetic sum of all 5 indicator scores per state
- `Grade` = letter grade reverse-engineered from CSV (A ≥ 4; B 2-3; C 0-1; D −2 to −1; F ≤ −3); cutoffs not published, derived empirically in [`../items_Sunlight.md`](../items_Sunlight.md) §2.

**Item 4 is excluded from this projection** (audit decision: 5-tier ordinal conflates 3-4 sub-features with a documented −1/−2 near-typo; cell-from-tier function not well-defined). With item 4 excluded, **our projection cannot reproduce Sunlight's published Total or letter Grade.** Validation is per-item only.

**Phase C validation strategy (recommended, pending user confirmation):** validate the 4 individual per-criterion scores (items 1, 2, 3, 5) against the published CSV's per-state values for those columns. Do not attempt to reproduce `Total` or `Grade`. Honest about scope; doesn't smuggle external data into the projection layer.

## Per-state per-indicator data: distributions

From [`papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`](../../../../papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv) (50 states; footnote markers `*`, `**`, `^`, `^^` stripped):

| Item | Tier scale | Distribution |
|---|---|---|
| 1. Lobbyist Activity | 4-tier (−1 to 2) | −1=12, 0=25, 1=6, 2=7 |
| 2. Expenditure Transparency | 4-tier (−1 to 2) | −1=4, 0=4, 1=25, 2=17 |
| 3. Expenditure Reporting Thresholds | 2-tier (−1 to 0) | −1=33, 0=17 |
| 4. Document Accessibility *(excluded)* | 5-tier (−2 to 2) | −2=2, −1=5, 0=12, 1=10, 2=21 |
| 5. Lobbyist Compensation | 2-tier (−1 to 0) | −1=23, 0=27 |

Distribution skew worth noting:
- **Item 1:** mode is tier 0 ("general subjects only"). 50% of states score 0; only 26% score 1 or 2 (specific bills disclosed).
- **Item 2:** mode is tier 1 ("categorized"). Itemization (tier 2) is the minority; lump or none is rare.
- **Item 3:** mode is tier −1 (threshold exists). 66% of states have some expenditure-itemization-de-minimis threshold; only 34% require all expenditures itemized.
- **Item 5:** approximately even split. 46% of states require some form of compensation disclosure; 54% don't.

## Validation jurisdictions

50 US states × 2015 vintage × 4 items = **200 per-cell ground-truth values** for Phase C. Federal LDA out of scope (Sunlight is state-only).

Per-state CSV also carries footnote markers (`*`, `**`, `***`, `^`, `^^`) on individual cells; meaning undocumented (flagged in [`../items_Sunlight.md`](../items_Sunlight.md) §7). Phase C should strip markers before comparison; flag the marker-carrying cells as caveat'd validation points.

---

## Per-item mappings

### sunlight_2015.lobbyist_activity (4-tier, −1 to 2)

Decomposes into 3 nested binary observables per α (registration form vs spending report split) — **6 compendium rows total** for this single Sunlight item.

- **Compendium rows (registration-form side):**
  - `lobbyist_reg_form_includes_general_subject_matter` (binary; legal)
    [cross-rubric: HG Q5 subject-tier; FOCAL contact_log.11 broad reading]
  - `lobbyist_reg_form_includes_bill_or_action_identifier` (binary; legal)
    [cross-rubric: HG Q5 bill-tier; FOCAL contact_log.11 narrow reading]
  - `lobbyist_reg_form_includes_position_on_bill` (binary; legal)
    [cross-rubric: FOCAL contact_log.10 (when statute requires position disclosure on reg form rather than spending report — rare but extant)]
- **Compendium rows (spending-report side):**
  - `lobbyist_spending_report_includes_general_subject_matter` (binary; legal)
    [cross-rubric: HG Q20 subject-tier; Newmark 2017 `disclosure.influence_legislation_or_admin`; Newmark 2005 `disc_legislative_admin_action_to_influence`; PRI E2g_i (lobbyist-side); Opheim `disclosure.legislation_supported_or_opposed` (loose reading — see β note)]
  - `lobbyist_spending_report_includes_bill_or_action_identifier` (binary; legal)
    [cross-rubric: HG Q20 bill-tier; FOCAL contact_log.11; PRI E2g_ii]
  - `lobbyist_spending_report_includes_position_on_bill` (binary; legal)
    [cross-rubric: FOCAL contact_log.10; Opheim `disclosure.legislation_supported_or_opposed` (literal reading — see β note)]
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:** Sunlight is form-agnostic, so first derive form-agnostic flags:
  ```
  general_subject_anywhere = reg_form_general_subject OR spending_report_general_subject
  bill_id_anywhere = reg_form_bill_id OR spending_report_bill_id
  position_anywhere = reg_form_position OR spending_report_position
  ```
  Then nested-tier mapping:
  | general_subject | bill_id | position | tier |
  |---|---|---|---|
  | F | F | F | −1 |
  | T | F | F | 0 |
  | T | T | F | 1 |
  | T | T | T | 2 |

  Statutorily-inconsistent combinations (e.g., `bill_id=T AND general_subject=F`) are implausible but representable. **Phase C extraction should flag them as data oddities, not silently coerce.**
- **Source quote:** "Lobbyist Activity: Do lobbyists have to reveal which pieces of legislation or executive actions they are seeking to influence? Tier 2: Lobbyists report the bill/action discussed and position taken; Tier 1: Lobbyists report the bill/action discussed; Tier 0: Lobbyists report the general subjects of lobbying; Tier −1: Lobbyists do not report activity."
- **Note on β (Opheim conflation):** Opheim's source item `disclosure.legislation_supported_or_opposed` is one binary that conflates bill-identifier AND position — its projection reads `lobbyist_spending_report_includes_bill_or_action_identifier AND lobbyist_spending_report_includes_position_on_bill` (literal AND reading; user-confirmed 2026-05-11). Opheim's TSV is not edited; the conjunction lives in the projection, not in the source.
- **Decision note on α (form-type split):** Splitting reg-form vs spending-report adds 3 rows on top of the form-agnostic 3 rows. Net cost is 3 extra binary cells per state; net benefit is preserving the HG Q5/Q20 distinction (a state can require bill_id on the spending report but not the reg form — a statutorily real case). Coarser rubrics' projections roll the two halves up via OR; granularity bias prefers preserving the distinction.

### sunlight_2015.expenditure_transparency (4-tier, −1 to 2)

Decomposes into 3 binary observables (corresponding to gating tiers).

- **Compendium rows:**
  - `lobbyist_spending_report_required` (binary; legal)
    [cross-rubric: HG Q11 (gateway); CPI #201; implicitly the entire E-series of PRI/HG/Newmark/Opheim spending-disclosure batteries]
    Already in CPI mapping; pre-existing.
  - `lobbyist_spending_report_categorizes_expenses_by_type` (binary; legal)
    [cross-rubric: HG Q14 ("summaries of spending classified by category types"); Newmark 2017 implicit in `disclosure.section_total` enumeration ("categories of expenditures"); FOCAL `financials.*` battery]
  - `lobbyist_spending_report_includes_itemized_expenses` (binary; legal)
    [cross-rubric: CPI #201 (compound item — itemized is one of three reads); HG Q15 (which also adds threshold magnitude — see item 3 row); PRI E1f_iv "itemized format"; FOCAL `financials.6` "individual entries"]
    Already in CPI mapping; pre-existing.
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  | required | categorized | itemized | tier |
  |---|---|---|---|
  | F | * | * | −1 |
  | T | F | F | 0 |
  | T | T | F | 1 |
  | T | * | T | 2 |

  Itemized implies categorized (statutorily; itemization is finer than categorization), so the `T, F, T` combination is implausible but representable. Phase C flags as oddity.
- **Source quote:** "Expenditure Transparency: Are lobbyists required to itemize all the expenses associated with their work, such as travel, holding an event, or buying gifts for lawmakers? Tier 2: Lobbyists report itemized list of expenses with dates and description of direct expenditure; Tier 1: Lobbyists report list of expenses categorized under broad descriptions, e.g. food, travel, meetings, media, etc.; Tier 0: Lobbyists report lump total of expenditures; Tier −1: Lobbyists do not report total expenditures."
- **Note:** This is a clean nesting: each tier adds a requirement to the previous. All three rows are read by multiple rubrics — exactly the dedup-candidate pattern.

### sunlight_2015.expenditure_reporting_thresholds (2-tier, −1 to 0)

Single typed cell shared with HiredGuns Q15 at finer granularity.

- **Compendium rows:**
  - `expenditure_itemization_de_minimis_threshold_dollars` (typed `Optional[Decimal]`; legal)
    [cross-rubric: HG Q15 (5-tier ordinal on threshold magnitude — reads same cell at finer granularity)]
- **Cell type:** `Optional[Decimal]` representing the dollar threshold below which individual expenditures need NOT be itemized within a spending report. `None` (or `0`) = no threshold (all expenditures must be itemized); `>0` = threshold (expenditures below the value are exempt from itemization).
- **Axis:** `legal_availability`.
- **Scoring rule:** Sunlight reads only the presence/absence:
  ```
  threshold IS NULL OR threshold == 0 → 0
  threshold > 0 → −1
  ```
  HG Q15 reads the magnitude: `NULL/0 → 4`, `≤$25 → 3`, `>$25 → 2`, `>$100 → 1`, `>$500 → 0`. Same cell, two projections at different granularities — exactly the typed-cell pattern locked in CPI #197.
- **Source quote:** "Expenditure Reporting Thresholds: Does the state require lobbyists to include all expenses in reports, or only those above a certain amount? Tier 0: Lobbyists must disclose all expenditures; Tier −1: Lobbyists do not need to disclose individual expenditures or event expenses if under a certain amount."
- **CRITICAL distinction from other "threshold" rows:** Three distinct threshold concepts surface across rubrics, easily conflated:
  | Threshold type | Cell name | Reads |
  |---|---|---|
  | **Lobbyist-status** (becoming a registered lobbyist) | `compensation_threshold_for_lobbyist_registration` (per CPI mapping) | CPI #197, HG Q2, Newmark/Opheim def.*_standard, FOCAL scope.2 |
  | **Filing-de-minimis** (whether a registered lobbyist's activity triggers filing at all) | `lobbyist_filing_de_minimis_threshold_dollars` (PRI D1 in PRI mapping) | PRI D1; possibly FOCAL scope.2 (combined with above) |
  | **Itemization-de-minimis** (within a triggered filing, which line-items need itemizing) | `expenditure_itemization_de_minimis_threshold_dollars` (this row) | Sunlight #3, HG Q15 |

  Sunlight #3 is the *itemization-line* threshold, not the registration or filing trigger. Compendium 2.0 must keep these three distinct.
- **Note:** Sunlight's narrative discusses threshold magnitudes ranging from $2 to $50 (lines 88-94) but the rubric collapses to binary. HG Q15 reads the magnitude as ordinal. The cell carries the dollar value; projections read at whatever granularity each rubric needs.

### ~~sunlight_2015.document_accessibility (5-tier, −2 to 2)~~ — **EXCLUDED**

Per the 2026-05-07 audit decision ([`../20260507_sunlight_atomic_audit.md`](../20260507_sunlight_atomic_audit.md) "User decision (2026-05-07 pm)" section): the 5-tier ordinal conflates 3-4 sub-features (digital filing, registration form online, expenditure form online, blank forms online) and the −1/−2 tier descriptors are a documented near-typo ("either" vs "both" with logically inverted semantics). Function from underlying cells → tier is not well-defined.

The underlying observables (digital-filing availability, public access to forms, etc.) **are still in compendium 2.0** — they're read by other rubrics (CPI #205-206, HG Q28-34, PRI Q1-Q6 accessibility, FOCAL openness.*). They just aren't accessed via a `project_sunlight_doc_accessibility` function because the function would be ill-defined.

Implication for Phase C: when validating Sunlight's published `Total`, this projection cannot reproduce it (item 4's contribution is missing). Per-item validation only.

### sunlight_2015.lobbyist_compensation (2-tier, −1 to 0)

Form-agnostic; reads the OR of multiple compensation-disclosure cells.

- **Compendium rows:**
  - `lobbyist_spending_report_includes_total_compensation` (binary; legal)
    [cross-rubric: Newmark 2017 `disclosure.total_compensation`; Newmark 2005 `disc_total_compensation`; HG Q13 (binary, spending-report variant); CPI #201 (compound item, this is one read); PRI E2f_i "Direct lobbying costs (compensation)"]
  - `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal)
    [cross-rubric: Newmark 2017 `disclosure.compensation_by_employer`; Newmark 2005 `disc_compensation_by_employer`]
  - `lobbyist_reg_form_includes_compensation` (binary; legal)
    [cross-rubric: HG Q13 footnote ("Full points if information is on registration form instead")]
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule:**
  ```
  compensation_disclosed_anywhere = total_on_spending_report
                                    OR broken_down_on_spending_report
                                    OR on_reg_form
  → 0 if disclosed; −1 otherwise.
  ```
- **Source quote:** "Lobbyist Compensation: Does the state mandate that lobbyists disclose how much they receive from a client? Tier 0: Lobbyists disclose earnings received from client/employer for lobbying; Tier −1: Lobbyists do not disclose earnings received from client/employer for lobbying."
- **Note on OpenSecrets overlap:** OpenSecrets cat 2 ("How much are lobbyists getting paid") reads the same compensation rows but with a 5-tier ordinal on disclosure completeness (no / partial-by-ranges / partial-not-linked-to-individuals / full-baseline / exceeds-baseline). OpenSecrets's projection (in its own mapping doc, forthcoming) reads finer-grained cells than Sunlight does. Sunlight's binary projection is `any_compensation_cell == T`.

---

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | Sunlight items reading | Cross-rubric readers (dedupe candidates) |
|---|---|---|---|---|
| `lobbyist_reg_form_includes_general_subject_matter` | binary | legal | #1 | HG Q5 |
| `lobbyist_reg_form_includes_bill_or_action_identifier` | binary | legal | #1 | HG Q5 |
| `lobbyist_reg_form_includes_position_on_bill` | binary | legal | #1 | (rare; FOCAL contact_log.10 when applicable) |
| `lobbyist_spending_report_includes_general_subject_matter` | binary | legal | #1 | HG Q20; Newmark 2017/2005 influence_legislation; PRI E2g_i; Opheim (loose) |
| `lobbyist_spending_report_includes_bill_or_action_identifier` | binary | legal | #1 | HG Q20; FOCAL contact_log.11; PRI E2g_ii |
| `lobbyist_spending_report_includes_position_on_bill` | binary | legal | #1 | FOCAL contact_log.10; Opheim (literal AND) |
| `lobbyist_spending_report_required` | binary | legal | #2 | HG Q11; CPI #201 (existing, CPI mapping) |
| `lobbyist_spending_report_categorizes_expenses_by_type` | binary | legal | #2 | HG Q14; Newmark `categories_of_expenditures` |
| `lobbyist_spending_report_includes_itemized_expenses` | binary | legal | #2 | CPI #201, HG Q15, PRI E1f_iv, FOCAL financials.6 (existing, CPI mapping) |
| `expenditure_itemization_de_minimis_threshold_dollars` | typed `Optional[Decimal]` | legal | #3 | HG Q15 (reads magnitude at ordinal granularity) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | #5 | Newmark 2017/2005 total_compensation; HG Q13; CPI #201; PRI E2f_i |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | #5 | Newmark 2017/2005 compensation_by_employer |
| `lobbyist_reg_form_includes_compensation` | binary | legal | #5 | HG Q13 footnote |

**13 distinct compendium rows touched by 4 Sunlight items in scope.** 11 of 13 are read by ≥1 other rubric — Sunlight's contribution is cross-rubric redundancy on heavily-shared rows, not novel observables. Per the projection-success criterion's "minimum compendium" goal: these are exactly the kind of rows that survive (validated by many rubrics) — not deletion candidates.

## Open issues surfaced by Sunlight

1. **Phase C aggregation impossible without item 4.** With item 4 excluded, `project_sunlight(state, 2015)` produces 4 per-criterion scores; the published `Total` and `Grade` cannot be reproduced. Per-item validation only is the honest scope. (Confirmed in this doc; final user confirmation pending.)

2. **Form-type split (α) is granularity-bias-aligned but adds 3 rows per content concept.** For Sunlight #1 we now have 6 rows (3 disclosure-detail × 2 form-types) where a single combined row would have been 3. The cost is 3 binary cells per state to extract; the benefit is preserving the HG Q5 (reg form) vs HG Q20 (spending report) distinction (which IS a real statutory variable across states — e.g., CA requires more on spending reports than registration). Granularity bias says: pay the 3-cell cost.

3. **Opheim conflation (β) is a projection-layer concern, not a source-layer concern.** Opheim's `disclosure.legislation_supported_or_opposed` stays as one binary in `items_Opheim.tsv`; Opheim's projection reads two compendium cells AND'd. Locked 2026-05-11 (Reading 1 of three considered options). When the Opheim projection mapping doc is written, it should explicitly cite this AND projection.

4. **Three distinct "threshold" concepts must stay separate in compendium 2.0** (per item 3 mapping above): lobbyist-status threshold, filing-de-minimis threshold, itemization-de-minimis threshold. Conflating these would break PRI D1 vs Sunlight #3 distinction. Flagged for the v2.0 schema-row-set freeze.

5. **Footnote markers on per-state CSV cells (`*`, `**`, `***`, `^`, `^^`) are uninterpretable** without a published key. Phase C strips them before comparison; cells with markers are validation points with caveat. Worth a flag in the Phase C validation harness so we know to weight them less.

## What Sunlight doesn't ask that other rubrics will

For continuity with other rubric mappings: Sunlight does not read any registration-side requirements (Sunlight is spending-disclosure-focused), any prohibition/cooling-off battery (out of scope), any portal-accessibility cells beyond the excluded item 4, any per-contact contact-log granularity (FOCAL territory), any temporal cadence of disclosure (CPI #199/#202 / PRI E1h/E2h territory), any gift-disclosure-by-recipient breakdown (HG / Newmark territory). All of these enter compendium 2.0 from other rubric mappings, not Sunlight's.

Sunlight's role is **cross-rubric redundancy on heavily-shared rows**, not coverage.

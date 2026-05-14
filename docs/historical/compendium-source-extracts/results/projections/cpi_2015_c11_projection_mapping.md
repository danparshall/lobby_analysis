# CPI 2015 C11 (Lobbying Disclosure) — projection mapping

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B.
**Handoff:** [`../../plans/_handoffs/20260507_phase_b_handoff.md`](../../plans/_handoffs/20260507_phase_b_handoff.md).
**Atomic items source:** [`../items_CPI_2015_lobbying.tsv`](../items_CPI_2015_lobbying.tsv) (14 items: 6 de jure + 8 de facto).
**Pre-walk:** [`../20260507_cpi_2015_c11_vs_consensus.md`](../20260507_cpi_2015_c11_vs_consensus.md). This doc operationalizes the per-item fold-in table from there into the Phase B template, with explicit cell-type and axis decisions.

---

## Doc conventions

- **Compendium row IDs** are working names chosen to be projection-meaningful, not cluster-derived. Where a row corresponds to an existing 3-way consensus cluster, the cluster reference is a parenthetical provenance hint (`cf. strict-c_NNN` or `cf. loose-c_NNN`), not an authoritative identifier. The clusters are guidelines — the compendium row design falls out of what projection logic needs to read, not the other way around.
- **`strict-c_NNN`** = strict cluster file (≥8/9 method-runs); **`loose-c_NNN`** = loose-only cluster file (≥6/9). The two files use independent cluster numbering.
- **Cell type** is the type that the compendium cell carries — not the type of the rubric's score. Compendium cells carry underlying values (e.g., a threshold dollar amount); the projection function maps cell value → rubric score (e.g., `threshold == 0` → CPI YES, `threshold > 0` → MODERATE, `no statute` → NO).
- **Axis** is `legal_availability` for de jure items, `practical_availability` for de facto items. CPI 2015's de jure / de facto pairing is exactly the v1.1 schema's two-axis design — no new axis needed.
- **Granularity bias: split on every distinguishing case.** Where rubrics read different subsets of a concept (e.g., one rubric covers governor-personally, another covers admin-agencies, another covers both), the compendium splits into one row per case (binary cell each). Maximum flexibility for downstream consumers; projection logic combines rows as needed via Boolean expressions. Avoids losing information when one rubric is coarser than another. (User direction, 2026-05-07.)
- **Typed cells live on `MatrixCell.value`.** v1.1's `CompendiumItem.data_type` (`boolean / numeric / categorical / free_text / compound`) declares the cell type but `MatrixCell` doesn't yet have a `value` field — it carries `required` / `legal_availability` / `practical_availability` enums only. v2.0 schema bump adds `MatrixCell.value: Any` constrained by `CompendiumItem.data_type` and retires the PRI-shape vestigial named-scalar fields (`StateMasterRecord.de_minimis_financial_threshold` etc.) that currently carry typed values via a different pattern. Until v2.0 lands, projection mapping docs assume the cell-with-typed-value pattern; the schema migration is a separate plan.

## Aggregation rule (Phase C empirical, with strong inputs)

CPI publishes `Lobbying Disclosure` at category-aggregate level (0–100, letter grade, rank) in [`papers/CPI_2015__sii_scores.csv`](../../../../papers/CPI_2015__sii_scores.csv). **Plus** the criteria xlsx contains per-state per-indicator scores for all 50 states × 14 items, extracted to [`../cpi_2015_c11_per_state_scores.csv`](../cpi_2015_c11_per_state_scores.csv) (700 rows).

Phase C now has both:
- **Per-item ground truth** (700 cells) — supports validating each item's projection in isolation.
- **Category aggregate** (50 cells) — supports validating the aggregation rule once per-item projections are sound.

The aggregation rule itself is still empirical (CPI's methodology doc isn't in our archive). Candidate formulas to fit:
1. Simple mean over all 14 items → category score.
2. Sub-category mean (5 sub-cats: 11.1-11.5, item counts 2/4/3/2/3) → category mean.
3. De jure half / de facto half → mean of halves.
4. Sub-category × axis-weighted variants.

With per-item per-state data, fitting is well-determined: 50 states × 14 items → 50 category aggregates. Linear regression over candidate aggregations gives the answer cleanly. Phase B doesn't need the answer.

## Per-state per-indicator data: distributions

From [`../cpi_2015_c11_per_state_scores.csv`](../cpi_2015_c11_per_state_scores.csv), score distribution per indicator:

| ID | Type | Distribution (state count per score) | Notes |
|---|---|---|---|
| 196 | de jure (2-tier) | YES=46, NO=4 | clean 2-tier |
| 197 | de jure (3-tier) | YES=17, MOD=32, NO=1 | clean |
| 198 | **de facto (5-tier)** | 100=15, 75=13, 50=21, 25=1, 0=0 | 25/75 not in published criteria |
| 199 | de jure (3-tier) | YES=31, MOD=18, NO=0, "100"=1 | one cell hand-typed wrong |
| 200 | **de facto (5-tier)** | 100=17, 75=16, 50=7, 25=10, 0=0 | 25/75 not in published criteria |
| 201 | de jure (3-tier) | YES=15, MOD=29, NO=6 | clean |
| 202 | **de facto (5-tier)** | 100=5, 75=14, 50=17, 25=4, 0=10 | 25/75 not in published criteria |
| 203 | de jure (3-tier) | YES=19, MOD=15, NO=15, "100"=1 | one cell hand-typed wrong |
| 204 | **de facto (5-tier)** | 100=9, 75=8, 50=14, 25=2, 0=17 | 25/75 not in published criteria |
| 205 | **de facto (5-tier)** | 100=41, 75=4, 50=3, 25=2, 0=0 | 25/75 not in published criteria |
| 206 | **de facto (5-tier)** | 100=9, 75=5, 50=3, 25=22, 0=11 | 25/75 not in published criteria |
| 207 | de jure (3-tier) | YES=14, MOD=18, NO=18 | clean |
| 208 | **de facto (5-tier)** | 100=7, 75=0, 50=5, 25=16, 0=22 | 25/75 not in published criteria |
| 209 | **de facto (5-tier)** | 100=15, 75=7, 50=13, 25=9, 0=6 | 25/75 not in published criteria |

**Cell-type implication:** all 8 de facto items use 5-tier scoring (0/25/50/75/100) in the realized data, but the published xlsx criteria document only the 100/50/0 anchors. CPI graders awarded 25/75 as partial-credit intermediate values without documented boundary criteria. This forces a doc-wide change to my de facto cell types — they're not 3-tier enums, they're 5-tier (or equivalently typed int constrained to multiples of 25).

**Data-quality footnotes** (4 cell-level glitches across 700 cells, ~99.4% clean):
- 4 mixed-case typos: "Yes"/"No" instead of YES/NO. Normalize before consumption.
- 2 cells with numeric values where YES/MODERATE/NO expected (IND_199, IND_203 — 1 each). Treat as data-entry errors; flag in Phase C consumption.

## Validation jurisdictions

50 US states × 2015 vintage × 14 items = **700 per-cell ground-truth values** (pre-normalization). Federal LDA is out of scope (CPI is state-only).

---

## Per-item mappings

### IND_196: Definition recognizes executive-branch lobbyists alongside legislative

- **Compendium rows:** Multiple binary rows, one per distinguishing target case (per granularity-bias convention):
  - `def_target_legislative_branch` (cf. loose-c_013, plus PRI A1/A2)
  - `def_target_governors_office` (governor personally + governor's office staff)
  - `def_target_executive_agency` (cabinet officials, agency heads, and agency staff who promulgate rules; cf. loose-c_006 — Newmark `def_administrative_agency_lobbying`)
  - `def_target_independent_agency` (non-cabinet quasi-public bodies — distinct because some states cover one but not the other)
  - `def_target_legislative_staff` (separated from legislators because some states define lobbying narrowly to communications with elected legislators only)
  - These align with v1.1's `RegistrationRequirement.role` Literal which already enumerates `governors_office`, `executive_agency`, `legislative_branch`, `independent_agency` as separate roles.
- **Cell type:** binary per row.
- **Axis:** `legal_availability` per row.
- **Scoring rule:** Reading CPI's source quote ("communications with state legislators **and** executive officials, **including the governor**") as requiring legislative coverage AND specifically governor coverage:
  `def_target_legislative_branch AND def_target_governors_office → YES (100); else → NO (0)`.
  CPI's #196 is 2-tier (no MODERATE in the source quote). Alternative reading where any executive-branch target satisfies the "executive officials" clause would project as `def_target_legislative_branch AND (def_target_governors_office OR def_target_executive_agency)`. The strict-governor reading is more conservative and matches the literal text.
- **Source quote:** "A YES score is earned if in law, the definition of lobbying includes communications with state legislators and executive officials, including the governor. A NO score is earned if no such law exists or it exists, but the definition does not recognize communications with executive and legislative officials."
- **Note:** Other rubrics' Phase B mappings will populate the rest of these target-type rows (PRI A-series will likely add `def_target_judicial`, `def_target_local_government`, `def_target_government_lobbying_government`, etc.). CPI alone touches only legislative + governors_office + executive_agency; the other rows are listed here for cross-rubric continuity since they represent real distinguishing cases.

### IND_197: Anyone paid to carry out lobbying activity is defined as a lobbyist

- **Compendium rows:** `compensation_threshold_for_lobbyist_registration` (cf. strict-c_009 / loose-c_016: existing "compensation standard" cluster, but the rubric reads the **value** of the threshold, not just whether one exists).
- **Cell type:** typed: `Optional[Decimal]` representing the dollar threshold below which compensation does NOT trigger lobbyist status. `None` (or 0) = no threshold (anyone paid is a lobbyist); `>0` = some compensation level required; missing/`null` = no statute defines a compensation standard at all.
- **Axis:** `legal_availability`
- **Scoring rule:** `threshold == 0 → YES (100); threshold > 0 → MODERATE (50); no statute → NO (0)`.
- **Source quote:** "A YES score is earned if anyone paid any amount to carry out lobbying activity is defined as a lobbyist and must register as such. A MODERATE score is earned if only persons being paid more than a certain threshold are defined as a lobbyist. A NO score is earned if no such law exists."
- **Note:** Canonical example for the typed-cell pattern (Doc Conventions). The strict-c_009 cluster as currently shaped (`def_compensation_standard` from Newmark/Opheim) reads as a binary row in those rubrics — CPI #197 forces the cell to carry the threshold value, which Newmark's projection can still read as binary (`threshold IS NOT NULL`). **One row, one cell, two projections at different granularities** — exactly what the v2.0 `MatrixCell.value` migration enables. Until v2.0 lands, this projection assumes the typed cell exists.

### IND_198: All paid lobbyists actually register

- **Compendium rows:** `lobbyist_registration_required` (the de-jure pair: is registration required for any paid lobbyist regardless of target type? Distinct from the per-target-type rows used in #196 — those say "lobbying *of X* triggers registration"; this row says "*if* lobbying triggers registration, registration is actually mandatory rather than voluntary"). Not currently a strict cluster — the mandate is implicit across many rubrics but never atomized as a yes/no. Practical-availability axis carries the de-facto observation.
- **Cell type:** Legal axis: binary (registration required vs voluntary). Practical axis: typed `int` ∈ {0, 25, 50, 75, 100} (5-tier; the published criteria below document 100/50/0 anchors only, but realized scoring uses 25 and 75 as partial-credit intermediates — see Per-state per-indicator data section).
- **Axis:** `practical_availability` (CPI #198 reads only this axis; the legal axis exists for completeness and is read by other rubrics).
- **Scoring rule:** Cell value passthrough: `score = practical_availability_value` ∈ {0, 25, 50, 75, 100}.
- **Source quote:** "A 100 score is earned if all who are paid to lobby register as such. A 50 score is earned if most but not all who are paid to lobby register as such. A 0 score is earned if those who are paid to lobby rarely or never register."

### IND_199: In law, lobbyists are required to file a registration form on an annual basis

- **Compendium rows:** `lobbyist_registration_renewal_cadence` (no strict-cluster home; the closest existing structure is PRI E1h/E2h reporting-frequency family — strict-c_033 through c_038 — but those cover *spending-report* cadence, not registration-renewal cadence. Registration-renewal cadence is a distinct concept).
- **Cell type:** enum: `{annual, biennial, less_frequent_than_biennial, no_renewal_required, no_registration_required}`. Could collapse to typed: `Optional[int]` representing renewal-period-in-months (12 for annual, 24 for biennial, etc.) if a numeric is more useful for cross-rubric projections.
- **Axis:** `legal_availability`
- **Scoring rule:** `cadence == annual_or_more_frequent → YES (100); cadence in {biennial, less_frequent} → MODERATE (50); no_registration_required → NO (0)`.
- **Source quote:** "A YES score is earned if lobbyists must fill out and file a registration form with the state government at least once a year. A MODERATE score is earned where lobbyists must fill out and file a registration form, but with less frequency. A NO score is earned if no such law exists."
- **Note:** Candidate new compendium row distinct from spending-report cadence. Most state regimes have biennial registration tied to legislative session.

### IND_200: In practice, lobbyists file detailed registration forms within a few days of initiating lobbying activity

- **Compendium rows:** `registration_timeliness_after_first_lobbying_activity`. Practical-availability axis on a row whose de-jure pair is the statutory registration deadline (e.g., "must register within X days of first lobbying contact"). The de-jure pair isn't in our existing consensus clusters as a strict item — it's another candidate new row, distinct from #199 (which is renewal cadence, not initial-registration timing).
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough). Underlying observable features the cell encodes: `(typical_days_to_register: int, detail_present: bool)` — but for projection passthrough what matters is the single 0-100 quality score.
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 score is earned if lobbyists register before or within five days of initial lobbying activity. Forms provide detailed information, such as name of employer, lobbied issue, or bill number(s). A 50 score is earned if lobbyists register about 10 days after initial lobbying activity and/or occasionally forms lack detailed information. A 0 score is earned if lobbyists register 20 or more days after initial lobbying activity and/or registrations generally lack detailed information."
- **Note:** The de-jure pair (`registration_deadline_days_after_first_lobbying`, typed: `int`) belongs in compendium 2.0 even though no de-jure rubric in our current set asks for it explicitly — it's the substrate that #200 measures compliance against, and it's a cleanly-extractable statutory value.

### IND_201: In law, lobbyists are required to file detailed spending reports, including compensation/salary information

- **Compendium rows:** Compound item — needs three reads.
  1. `lobbyist_spending_report_required` (de-jure mandate that lobbyist files a spending report; partial provenance from loose-c_001 / strict-c_004 / strict-c_018 but those clusters bundle existence-of-mandate with what-must-be-included).
  2. `lobbyist_spending_report_includes_itemized_expenses` (cf. loose-c_001 / strict-c_001 family on total compensation/expenditures; the *itemization* aspect is loose-c_031 PRI E1f_iv "itemized format").
  3. `lobbyist_spending_report_includes_compensation` (cf. strict-c_018: HG Q13 + Sunlight `lobbyist_compensation`; loose-c_001 also covers).
- **Cell type:** binary on each of the three rows.
- **Axis:** `legal_availability`
- **Scoring rule:** Per the verbatim source quote: `(report_required AND itemized AND includes_compensation) → YES (100); (report_required AND (itemized XOR includes_compensation)) → MODERATE (50); else → NO (0)`. The MODERATE clause's "or" is the load-bearing logical OR between itemized-format and compensation-included — either alone is partial credit.
- **Source quote:** "A YES score is earned if lobbyists are required to file itemized spending reports (including name of employer, lobbied issues and bill number(s) and compensation/payments received for lobbying services). A MODERATE score is earned if lobbyists are required to file itemized spending reports or compensation/payments received, but not both. A NO score is earned if no such law exists."
- **Note:** Compound-item structure forces a decision on whether compendium 2.0 splits "report-required" vs "report-includes-X" or carries them as a typed object — recommend split rows for consistency with the granular HG/Newmark family.

### IND_202: In practice, lobbyists file detailed spending reports with reasonable frequency

- **Compendium rows:** `lobbyist_spending_report_filing_cadence`, with practical-availability axis on the de-jure pair `lobbyist_spending_report_cadence` (cf. strict-c_004 / loose-c_007 — frequency of reporting).
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough). Underlying observable features the cell encodes: `(filing_cadence: enum, detail_level: enum)`.
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 score is earned if lobbyists file at least quarterly, itemized expense reports, including amounts, descriptions and lobbied bill number(s). A 50 score is earned if lobbyists file at least semi-annual expense reports, or file them more frequently, but they lack sufficient details. A 0 score is earned if is earned where lobbyists file expense reports annually or less-frequently, and/or they usually lack details."
- **Note:** The de-jure cadence row already exists in consensus and PRI's E1h/E2h family enumerates the cadence options — projection here reads the practical-availability cell on the same row.

### IND_203: In law, employers or principals of lobbyists are required to fill out spending reports

- **Compendium rows:** `principal_spending_report_required` (de-jure) AND `principal_spending_report_includes_compensation_paid_to_lobbyists` (de-jure on whether the principal report itemizes lobbyist compensation). Both candidates from PRI E1a-family (currently consensus singletons — PRI's principal-side items don't co-cluster with lobbyist-side ones). loose-c_001 covers lobbyist-side `total_compensation`; principal-side is a parallel structure.
- **Cell type:** binary on each.
- **Axis:** `legal_availability`
- **Scoring rule:** `(principal_report_required AND includes_compensation) → YES (100); (principal_report_required AND NOT includes_compensation) → MODERATE (50); NOT principal_report_required → NO (0)`.
- **Source quote:** "A YES score is earned if employers or principals fill out spending reports including salary or fees paid to their lobbyist(s). A MODERATE score is earned if they file spending reports, but they fail to include the specific amount of salary or fees paid to their lobbyist(s). A NO score is earned if no such law exists."
- **Note:** Confirms compendium 2.0 must keep principal-side spending-report rows even though they're consensus singletons in PRI's atomization. Multiple rubrics (CPI #203, PRI E1a-family) read them.

### IND_204: In practice, employers/principals list lobbyist compensation on their spending reports

- **Compendium rows:** `principal_spending_report_includes_compensation_paid_to_lobbyists` — practical-availability axis on the de-jure row from #203 (cf. strict-c_024 Newmark `disc_compensation_by_employer` is a related but lobbyist-side concept; the principal-side practical-availability is what #204 reads).
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough). Underlying observable features the cell encodes: `(principals_file_reports: enum, reports_include_lobbyist_compensation: enum)`.
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 score is earned if employers/principals always file expenditure reports including salary or fees paid to their lobbyist(s). A 50 score is earned if employers/principals occasionally fail to file expenditure reports or they always do it, but they lack the salary or fees paid to their lobbyist(s). A 0 score is earned if employer/principals rarely or never file expenditure reports or salary or fees paid are not disclosed."

### IND_205: In practice, citizens can access lobbying disclosure documents within a reasonable time period and at no cost

- **Compendium rows:** Compound. Reads from:
  1. `lobbying_disclosure_documents_online` (cf. loose-c_009: lobbyist register online).
  2. `lobbying_disclosure_documents_free_to_access` (cf. loose-c_002: FOCAL openness.3 "free to access, open license").
  3. `lobbying_disclosure_offline_request_response_time_days` (typed: `int`; not currently in consensus — would be a new row).
- **Cell type:** practical-availability axis on (1) and (2) as binary; (3) as typed `int` (days). Composite read produces an effective 5-tier score (0/25/50/75/100) per realized data, but boundary semantics for 25/75 aren't documented in published criteria.
- **Axis:** `practical_availability`
- **Scoring rule:** Per published anchors: `(online AND free) OR (offline AND obtainable_within_7_days) → 100; offline_request_takes_2_weeks_with_visit_required_or_fee → 50; takes_more_than_a_month_or_prohibitive_or_unobtainable → 0`. 25/75 intermediate scores are scorer-judgment partial credit.
- **Source quote:** "A 100 score is earned if the all lobbying disclosure documents are available online at no cost, can be obtained electronically within a week, or in paper for no more than the cost of photocopies. A 50 score is earned if it takes two weeks to obtain these documents, requesters are required to visit an office, or a fee must be paid. A 0 score is earned if it takes more than a month to obtain these documents, the cost is prohibitive, or they cannot be obtained at all."

### IND_206: In practice, lobbying disclosure information is made available in an open data format

- **Compendium rows:** `lobbying_data_open_data_quality` (cf. loose-c_002: bundles openness.3 / openness.4 / OpenSecrets downloads / PRI Q6 — already a tight 4-rubric cluster on the de-jure side).
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough). Underlying observable features the cell encodes: `(online: bool, easy_access: bool, bulk_download: bool, machine_readable: bool)`.
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 is earned if lobbying disclosure information is made available online and can be easily accessed, downloaded in bulk, and in machine-readable format. A 50 is earned if where lobbying disclosure information is available online but cannot be easily accessed and/or downloaded in bulk, but can be downloaded in machine-readable format. A 0 is earned if lobbying disclosure information is not available online or it is but cannot be downloaded."
- **Note:** Single canonical row. The de-jure pair (e.g., "is the state required by law to publish in machine-readable format") may not exist statutorily in most states — practical-availability is the only meaningful axis here for many jurisdictions.

### IND_207: In law, there are requirements for the regular auditing of lobbying disclosure records

- **Compendium rows:** `lobbying_disclosure_audit_required_in_law` (cf. loose-c_023: HG Q40 + Opheim `enforce.thoroughness_of_reviews` — currently a 2-rubric loose pair; CPI #207 adds a third reader and would promote it toward strict territory in any re-run).
- **Cell type:** enum `{regular_third_party_audit_required, audit_only_when_irregularities_suspected_or_compliance_review, no_audit_requirement}` mapping to YES/MODERATE/NO.
- **Axis:** `legal_availability`
- **Scoring rule:** Direct passthrough → 100/50/0.
- **Source quote:** "A YES score is earned if there is a legal requirement for the regular auditing of lobbying disclosure records by an impartial third party. A MODERATE score is earned if independent auditing only occurs when financial irregularities are discovered or suspected or the law requires a compliance review. A NO score is earned if no such law exists."
- **Note:** Audit *requirements* (do they exist in law?) are kept in scope because they measure whether the disclosure regime can function, not enforcement strictness — see Open Issue 4. If Newmark/Opheim's enforcement battery (deferred to a later plan round) re-reads this row from a strictness angle, no rework needed.

### IND_208: In practice, lobbying disclosure records are independently audited

- **Compendium rows:** `lobbying_disclosure_audit_required_in_law` — practical-availability axis on the same row as #207.
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough).
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 score is earned if lobbying disclosures are audited yearly by an impartial third party. A 50 score is earned if lobbying disclosures are not always independently audited, or they are but audits may fail to identify problems in the information. A 0 score is earned if lobbying disclosures are not independently audited, or they generally fail to identify problems in the information."

### IND_209: In practice, penalties are imposed as necessary when lobbying reporting requirements are violated

- **Compendium rows:** `lobbying_violation_penalties_imposed_in_practice` — practical-availability axis on a de-jure row that asks "are penalties statutorily defined for reporting violations" (cf. HG Q41/Q42 enforcement battery — currently consensus singletons; the de-jure pair belongs in compendium even though it's enforcement-adjacent because CPI's practical read needs it).
- **Cell type:** practical-availability typed `int` ∈ {0, 25, 50, 75, 100} (5-tier passthrough).
- **Axis:** `practical_availability`
- **Scoring rule:** Cell value passthrough.
- **Source quote:** "A 100 score is earned if offenders are always sanctioned when violations to reporting requirements are discovered. A 50 score is earned if offenders are generally sanctioned, but documented evidence show some exceptions exist. A 0 score is earned if sanctions are rarely or never imposed even though they are necessary."
- **Note:** Same enforcement-adjacent caveat as #207. CPI's choice to put penalty-imposition under "Lobbying Disclosure" rather than a separate enforcement category is unusual and is part of why CPI 2015 abstracts so high — it folds enforcement into disclosure.

---

## Summary of compendium rows touched

For convenience; the union of these rows across all rubric mappings becomes `disclosure_side_compendium_items_v1.tsv` after Phase B's other 8 rubrics are mapped.

| Row id (working name) | Cell type | Axis(es) read | CPI items reading | Provenance hint |
|---|---|---|---|---|
| `def_target_legislative_branch` | binary | legal | #196 | loose-c_013, PRI A1 |
| `def_target_legislative_staff` | binary | legal | (#196 indirect) | PRI A2 |
| `def_target_governors_office` | binary | legal | #196 | v1.1 schema role |
| `def_target_executive_agency` | binary | legal | (#196 alt reading) | loose-c_006, Newmark/Opheim |
| `def_target_independent_agency` | binary | legal | (cross-rubric) | v1.1 schema role |
| `compensation_threshold_for_lobbyist_registration` | typed: `Optional[Decimal]` | legal | #197 | refines strict-c_009 / loose-c_016 |
| `lobbyist_registration_required` | binary (legal) + typed int 0-100 step 25 (practical) | legal + practical | #198 | new (implicit in PRI A-family) |
| `lobbyist_registration_renewal_cadence` | typed: `Optional[int_months]` (or enum) | legal | #199 | new (distinct from spending-report cadence) |
| `registration_deadline_days_after_first_lobbying` | typed: `int` (legal) + typed int 0-100 step 25 (practical) | legal + practical | #200 | new |
| `lobbyist_spending_report_required` | binary | legal | #201 | refines loose-c_001 / strict-c_004 / strict-c_018 |
| `lobbyist_spending_report_includes_itemized_expenses` | binary | legal | #201 | cf. loose-c_031 (PRI E1f_iv) |
| `lobbyist_spending_report_includes_compensation` | binary | legal | #201 | cf. strict-c_018 (HG Q13 + Sunlight) |
| `lobbyist_spending_report_filing_cadence` | enum (legal) + typed int 0-100 step 25 (practical) | legal + practical | #202 | strict-c_004 / loose-c_007 |
| `principal_spending_report_required` | binary | legal | #203 | new (PRI E1a-family singleton) |
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | binary (legal) + typed int 0-100 step 25 (practical) | legal + practical | #203 + #204 | parallel to strict-c_024 |
| `lobbying_disclosure_documents_online` | binary (practical) | practical | #205 | loose-c_009 |
| `lobbying_disclosure_documents_free_to_access` | binary (practical) | practical | #205 | loose-c_002 |
| `lobbying_disclosure_offline_request_response_time_days` | typed: `int` (practical) | practical | #205 | new |
| `lobbying_data_open_data_quality` | typed int 0-100 step 25 (practical) | practical | #206 | loose-c_002 |
| `lobbying_disclosure_audit_required_in_law` | enum (legal) + typed int 0-100 step 25 (practical) | legal + practical | #207 + #208 | loose-c_023 |
| `lobbying_violation_penalties_imposed_in_practice` | binary (legal) + typed int 0-100 step 25 (practical) | legal + practical | #209 | new (cf. HG Q41/Q42 singletons) |

21 distinct compendium rows touched by 14 CPI items (some rows read by multiple items via different axes; the per-target-type def rows above the table are partly populated by #196 and partly listed for cross-rubric continuity).

## Open issues surfaced by CPI for design-team review

1. **Typed cells require v2.0 schema bump.** CPI #197 (compensation threshold), #199 (registration cadence), #200 (registration-deadline days), #205 (offline-request-time days), and **all 8 de facto items (5-tier int 0-100 step 25)** require typed-value cells, not binary. v1.1 declares `CompendiumItem.data_type` as a Literal of `boolean / numeric / categorical / free_text / compound` but `MatrixCell` has no `value` field — the type declaration exists, the carrier doesn't. The v2.0 bump adds `MatrixCell.value: Any` constrained by the row's `data_type`, and retires the named-scalar `StateMasterRecord.de_minimis_*` fields (which are PRI-shape vestigial doing the same job at a different level). Tracked as a separate v2.0 schema plan; this projection mapping assumes typed cells exist.
2. **De facto items use 5-tier scoring (0/25/50/75/100) per realized data, but published criteria document only 100/50/0 anchors.** CPI graders awarded 25/75 as scorer-judgment partial credit without documented boundary criteria. Implication: compendium cells for de facto items must accommodate the full 5-tier range (modeled as typed `int` ∈ {0, 25, 50, 75, 100}). The 25/75 boundary semantics are a Phase C question — projection-from-cells either passes through the cell value directly (if the cell carries CPI-compatible 5-tier scores) or applies a deterministic mapping from underlying observable features to 5 tiers (if the cell carries primary observable data). The latter requires deciding the partial-credit boundaries explicitly, which CPI's published rubric doesn't help with.
3. **Compound items are normal, not exception.** IND_201 reads 3 rows; IND_205 reads 3 rows. Most rubric items will read 1-3 rows when the rubric concept doesn't atomize 1:1 against compendium granularity. The Phase B per-item template handles compound reads cleanly via the `Compendium rows: a, b, c` enumeration; no template change needed.
4. **Enforcement-adjacent items kept in scope.** IND_207 / IND_208 (audits) and IND_209 (penalties) measure whether enforcement *exists at all* (audits happen, sanctions get imposed when violations occur) — a precondition for the disclosure regime to function — rather than enforcement strictness (penalty schedules, prohibition completeness, which are deferred). CPI's choice to bundle them with C11 reflects this distinction. Included; not a violation of the disclosure-only scope qualifier.
5. **Evidence sourcing for de-facto items in non-2015 vintages.** v1.1 schema already carries `evidence_source` + `evidence_notes` + `legal_citation` on `FieldRequirement`. With Sonnet 4.6 + enforced-citation tool, statutory citations for de-jure cells are populated automatically. **De-facto cells (CPI #198, #200, #202, #204, #205, #206, #208, #209) are harder.** For the 2015 vintage specifically, CPI's published per-state scores ARE evidence — but populating cells from them and projecting CPI back from those cells is circular (validating against itself). Phase C round-trip validation requires de-facto cells to be populated from primary observation: portal scraping (#205, #206), published audit reports if any (#208), FOIA-able compliance data (#198, #209). For 2026 and other non-2015 vintages, no CPI-equivalent score exists — the practical-availability extraction pipeline (Track B / separate plan) has to produce these from primary evidence. **Implication:** Phase C validation for CPI on 2015 must avoid the circularity, or Phase C should be staged: validate the *de-jure half* of CPI's projection against published per-state scores first (cells populated from statute, no circularity); de-facto half stays open until practical-availability extraction can populate cells from primary evidence.
6. **Data-quality glitches in xlsx source data** (6 / 700 cells, ~0.9%): 4 mixed-case typos ("Yes"/"No" in IND_196, IND_197, IND_199, IND_203 — one each) plus 2 cells with numeric values where YES/MODERATE/NO expected (IND_199, IND_203 — one each). Phase C consumption layer should normalize: case-insensitive YES/NO matching; flag the 2 numeric cells as data errors and exclude from validation set or accept with caveat.

## What CPI doesn't ask that other rubrics will (Phase B for those rubrics)

For continuity with the cpi-vs-consensus pre-walk (which enumerates these in detail): gifts to officials (Newmark/FOCAL/PRI), revolving door / cooling-off (HG Q48 + Newmark2017), prohibitions (Newmark battery), itemization granularity (PRI E1f_i-iv), per-meeting contact log (FOCAL contact_log.*), reporting cadence detail beyond annual (PRI E1h/E2h), search/filter granularity (PRI Q7a-Q7o), registrant taxonomy beyond "anyone paid" (PRI A1-A11), bill numbers / specific legislation lobbied (FOCAL contact_log.11 + PRI E1g_ii), frequency of website updates (FOCAL timeliness.1 + HG Q38).

These rows enter compendium 2.0 from the other rubrics' projection mappings, not CPI's.

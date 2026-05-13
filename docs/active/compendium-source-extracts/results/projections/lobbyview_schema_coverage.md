# LobbyView 2018/2025 — schema-coverage mapping (FINAL Phase B mapping, 9th rubric)

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (ninth and final rubric — after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991, HiredGuns 2007, FOCAL 2024; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff (most recent):** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) — LobbyView watchpoints in the per-rubric section at the bottom of that doc.
**Atomic items source:** [`../items_LobbyView.tsv`](../items_LobbyView.tsv) (46 schema fields) + [`../items_LobbyView.md`](../items_LobbyView.md) (methodology + field grouping).
**Predecessor mappings (for row reuse):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md), [`newmark_2017_projection_mapping.md`](newmark_2017_projection_mapping.md), [`newmark_2005_projection_mapping.md`](newmark_2005_projection_mapping.md), [`opheim_1991_projection_mapping.md`](opheim_1991_projection_mapping.md), [`hiredguns_2007_projection_mapping.md`](hiredguns_2007_projection_mapping.md), [`focal_2024_projection_mapping.md`](focal_2024_projection_mapping.md).

---

## Why this mapping is shaped differently

LobbyView is **not a scoring rubric.** It is federal-only data infrastructure (Kim 2018; Kim 2025) — a relational database + REST API built on the universe of LDA reports, enriched with bill-detection, name-disambiguation, NAICS/Compustat merges, full-text indexes, and (in Kim 2025) LLM+GNN-derived bill-position labels.

The branch's compendium-construction project frames itself informally as "LobbyView for 50 states + federal LDA." Under that framing, **each LobbyView schema field becomes a question of the form: "does compendium 2.0 have a row that captures this data, and if so on what axis?"** There's no score to project against published ground truth; the validation is **schema-coverage** — for the Federal_US LDA jurisdiction (which by definition populates every LobbyView field), what fraction of fields map cleanly to a compendium row?

This mapping doc is shorter and flatter than the 8 score-projection docs. The output is a coverage table, not per-item projection rules. Per the locked plan Phase C §10: "LobbyView — schema-coverage check rather than score projection. Different shape; tackled separately."

---

## Coverage convention

Five coverage statuses are used:

| Status | Meaning | Federal_US LDA disposition |
|---|---|---|
| **COVERED** | An existing compendium row (from prior 8 mappings) captures this LobbyView field. | Federal_US cell populates `TRUE` (LDA mandates the disclosure). |
| **COVERED-PARTIAL** | A related compendium row exists, but it doesn't atomize at LobbyView's granularity, OR LobbyView splits one row into multiple operational fields. Documented gap. | Federal_US partially populates; finer granularity is a compendium 2.0 freeze question. |
| **NOT_COVERED** | No existing compendium row reads this. Either (a) candidate NEW row for compendium 2.0 freeze, or (b) field is genuinely out-of-scope for state-disclosure extraction (operational metadata, derived inference, external merge). | Documented per-field. |
| **OPERATIONAL_METADATA** | The field is filing-identifier / sequence-position / vintage metadata, not a disclosure observable. Compendium rows shouldn't capture this. | Implicit in extraction pipeline (every filing has an ID, vintage, ordinal). Not a row. |
| **EXTERNAL_ENRICHMENT** | The field is not LDA-disclosed; it's LobbyView-added (NAICS merge, Compustat merge, Congress.gov bill data, CRS subject taxonomy, Bioguide legislator IDs, Kim 2025 LLM/GNN-inferred features). Out of scope for state-disclosure compendium. | N/A — LobbyView ADDS this on top of LDA, not extracts it from LDA. |

The first three are properly disclosure observables; the last two are non-observables. Federal_US LDA coverage rate is computed over the disclosure-observable subset only.

---

## Cross-rubric grep — schema-coverage form

The locked workflow's cross-rubric grep was performed in inverted form for this mapping: instead of "before drafting a NEW compendium row, check if other rubrics also read the same observable," the grep here is "for each LobbyView field, which existing compendium row (across the 8 prior score-projection mappings) covers it?"

The 8 mappings' Summary tables collectively enumerate the compendium 2.0 row inventory (~110 rows pre-FOCAL-1; ~111 post-FOCAL-1). The grep results are integrated directly into the per-field coverage table below.

---

## Per-field coverage

### Reports table (13 fields)

These are the LDA-direct filing-metadata + financial fields under LD-1 / LD-2.

| LobbyView field | Status | Compendium row(s) / rationale | Federal_US LDA reads |
|---|---|---|---|
| `report_uuid` | OPERATIONAL_METADATA | Filing-identifier; not a disclosure observable. | implicit (every filing has an ID) |
| `client_uuid` | OPERATIONAL_METADATA (derived) | Name-disambiguation output over `client_name`; not a state-disclosed field — LobbyView derives it. | implicit |
| `client_name` | **COVERED** | `lobbyist_report_includes_principal_names` (PRI E2c reader); reg-form-side α-pair `lobbyist_reg_form_lists_each_employer_or_principal` (HG Q9). | LD-1 §3 (registrant) + §7 (client) |
| `primary_naics` | EXTERNAL_ENRICHMENT | LobbyView-added industry classification merge (Compustat/Crunchbase/manual). Not LDA-disclosed. State-level: virtually no state requires NAICS code on filing. | n/a (LobbyView merge, not LDA field) |
| `naics_description` | EXTERNAL_ENRICHMENT | Companion to `primary_naics`. Same disposition. | n/a |
| `registrant_uuid` | OPERATIONAL_METADATA (derived) | Filing-identifier; not a disclosure observable. | implicit |
| `registrant_name` | **COVERED** | `lobbyist_reg_form_includes_lobbyist_full_name` (FOCAL descriptors.1 — NEW row from FOCAL mapping 2026-05-13). The "registrant" is the filer (firm or self-filing lobbyist); LDA Form LD-1 §3. | LD-1 §3 |
| `report_year` | OPERATIONAL_METADATA | Vintage; already a dimension of every cell in the compendium. | implicit |
| `report_quarter_code` | **COVERED** | `lobbyist_spending_report_cadence_*` family (binary × 6 by cadence: monthly, quarterly, triannual, semiannual, annual, other — introduced in PRI E1h/E2h + HG Q11 reading family). Federal LDA is post-HLOGA quarterly → `_quarterly == TRUE`. | LD-2 (quarterly post-HLOGA 2007) |
| `amount` | **COVERED** | `lobbyist_spending_report_includes_total_expenditures` (Newmark 2017 mapping NEW; FOCAL financials.6 reader) AND `lobbyist_spending_report_includes_total_compensation` (Sunlight #5 reader; 7-rubric-confirmed — most-validated row in compendium). Federal LDA's `amount` is either income (firm filers) or expense (in-house filers); compendium captures both via the lobbyist-side cells. | LD-2 §13 / §15 |
| `is_no_activity` | **COVERED** | `lobbyist_spending_report_required_when_no_activity` (HG Q25 — HG-introduced row). Federal LDA requires zero-activity reports. State-level: varies; some states allow non-filing for zero-activity periods. | LD-2 (zero-activity required under HLOGA) |
| `is_client_self_filer` | **NOT_COVERED** | No compendium row distinguishes in-house from contract registrants as a separate disclosure cell. PARTIALLY implicit in α form-split logic + scope.2 thresholds, but the in-house-vs-contract distinction is operational. **Candidate NEW row** for compendium 2.0 freeze: `lobbyist_report_distinguishes_in_house_vs_contract_filer` (binary; legal). State-level: most states preserve the distinction in their forms but no contributing rubric reads it as a disclosure observable. | LD-1 §10 (in-house indicator) |
| `is_amendment` | **NOT_COVERED** | `lobbyist_registration_amendment_deadline_days` (HG Q7) reads whether amendments are required by deadline, not whether amendment-vs-original is flagged on each filing. **Candidate NEW row** for compendium 2.0 freeze: `lobbyist_filings_flagged_as_amendment_vs_original` (binary; legal). | LD-2 amendment indicator |

**Reports table tally: 7 COVERED + 3 OPERATIONAL_METADATA + 2 EXTERNAL_ENRICHMENT + 2 NOT_COVERED (candidate NEW rows).** Federal_US disclosure-observable coverage: 7/9 = 78%.

### Issues table (4 fields, LDA Section 15-17)

These are the issue/topic/agency fields from LD-2.

| LobbyView field | Status | Compendium row(s) / rationale | Federal_US LDA reads |
|---|---|---|---|
| `issue_ordi` | OPERATIONAL_METADATA | Ordinal within report; not a disclosure observable. | implicit |
| `issue_code` | **NOT_COVERED** | LDA Section 15 standardized two-letter taxonomy (~80 codes). No contributing rubric reads "state uses a standardized issue-code taxonomy" as a separate observable. State-level analog is weak — most states use free-text issue descriptions, not a fixed code list (FOCAL contact_log.9 reads topics-discussed but not against a taxonomy). **Candidate NEW row** for compendium 2.0 freeze: `lobbying_disclosure_uses_standardized_issue_code_taxonomy` (binary; legal). | LD-2 §15 |
| `gov_entity` | **COVERED-PARTIAL** | `lobbying_contact_log_includes_institution_or_department` (FOCAL contact_log.3 — NEW from FOCAL mapping) + `lobbying_contact_log_includes_beneficiary_organization` (contact_log.1). PRI's coarse `_includes_contacts_made` (E1i/E2i) is the parent. LobbyView's `gov_entity` is an aggregated branch/agency-list per issue — partway between the per-meeting contact_log atomization and PRI's coarse aggregate. **Coverage**: COVERED via contact_log.3 reading for institution-level; finer per-meeting per-official disclosure is covered by contact_log.2 (`official_contacted_name`). | LD-2 §17 |
| `issue_text` | **COVERED** | `lobbyist_spending_report_includes_general_subject_matter` (Sunlight #1 + Newmark 2017/2005 + HG Q20 + PRI E2g_i + Opheim — 5-rubric-confirmed). Federal LDA Section 16 is a free-text narrative. | LD-2 §16 |

**Issues table tally: 2 COVERED + 1 COVERED-PARTIAL + 1 OPERATIONAL_METADATA + 1 NOT_COVERED.** Federal_US disclosure-observable coverage: 3/4 = 75%.

### LDA Section 18 — covered_official_position (1 field)

| LobbyView field | Status | Compendium row(s) / rationale | Federal_US LDA reads |
|---|---|---|---|
| `covered_official_position` | **COVERED** | `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal) — **NEW row added to compendium 2.0 on 2026-05-13 by the FOCAL-1 resolution.** Federal LDA Section 18 requires registrants to list employees whose past employment includes service as a covered executive- or legislative-branch official within the previous 20 years; this is the disclosure observable. **State-level analog: revolving-door reg-form disclosure varies; many states require nothing equivalent.** | LD-1 / LD-2 §18 |

**This is the headline cross-rubric validation for FOCAL-1.** The FOCAL `revolving_door.1` row, which was the open scope-qualifier question resolved 2026-05-13, maps directly onto the **most-distinctive lobbying-research-load-bearing LDA field** (Kim 2025 builds explicit "lobbyist-legislator previously worked together" GNN edges from Section 18). LobbyView reads Section 18 as `covered_official_position`; FOCAL reads it as `revolving_door.1`; the just-added compendium row captures both. **Cross-rubric confirmation:** the FOCAL-1-introduced row is now 2-rubric-confirmed (FOCAL + LobbyView).

Section 18 tally: 1 COVERED. Federal_US disclosure-observable coverage: 1/1 = 100%.

### Bills table (11 fields, Congress.gov / CRS external)

These are external Congress.gov bill metadata fields — not LDA-disclosed. The state-level analog is whether the state requires bill-identifier disclosure on filings (which IS covered by `lobbyist_spending_report_includes_bill_or_action_identifier` + reg-form variant — 5-rubric-confirmed). The 11 LobbyView fields below are about *which* bills LobbyView indexes from Congress.gov, not about whether the lobbying filing disclosed bill IDs.

| LobbyView field | Status | Rationale |
|---|---|---|
| `congress_number` | EXTERNAL_ENRICHMENT | Congress.gov metadata. |
| `bill_chamber` | EXTERNAL_ENRICHMENT | Congress.gov metadata. |
| `bill_resolution_type` | EXTERNAL_ENRICHMENT | Congress.gov metadata. |
| `bill_number` | EXTERNAL_ENRICHMENT (compendium-side analog COVERED) | Congress.gov bill number; the STATE-disclosed bill identifier on a filing is covered by `lobbyist_spending_report_includes_bill_or_action_identifier` (Sunlight #1 + HG Q20 + PRI E2g_ii + Opheim + FOCAL contact_log.11 — 5-rubric-confirmed). |
| `bill_introduced_datetime` | EXTERNAL_ENRICHMENT | Congress.gov metadata. |
| `bill_date_updated` | EXTERNAL_ENRICHMENT | Congress.gov metadata. |
| `bill_state` | EXTERNAL_ENRICHMENT | Congress.gov status; Kim 2025 GNN uses this as a Bill node feature. |
| `bill_url` | EXTERNAL_ENRICHMENT | Congress.gov permalink. |
| `bill_subject` | EXTERNAL_ENRICHMENT | CRS subject taxonomy. |
| `bill_summary` | EXTERNAL_ENRICHMENT | CRS-authored summary. |
| `bill_title` | EXTERNAL_ENRICHMENT | Congress.gov metadata; used by Kim 2018's bill-detection title-matching step. |

**Bills table tally: 0 disclosure observables; all 11 are EXTERNAL_ENRICHMENT.** Federal_US coverage rate is **N/A** for this group (these aren't LDA-disclosed; LobbyView merges them in from external sources). The compendium's bill-identifier row covers the disclosed analog separately.

### Legislators table (7 fields, Bioguide / GovTrack external)

All Congress.gov / Bioguide / GovTrack metadata. None are LDA-disclosed observables.

| LobbyView field | Status |
|---|---|
| `legislator_id` (Bioguide) | EXTERNAL_ENRICHMENT |
| `legislator_govtrack_id` | EXTERNAL_ENRICHMENT |
| `legislator_first_name` | EXTERNAL_ENRICHMENT |
| `legislator_last_name` | EXTERNAL_ENRICHMENT |
| `legislator_full_name` | EXTERNAL_ENRICHMENT |
| `legislator_gender` | EXTERNAL_ENRICHMENT |
| `legislator_birthday` | EXTERNAL_ENRICHMENT |

**Legislators tally: 0 disclosure observables; all 7 are EXTERNAL_ENRICHMENT.**

### Networks & derived links (2 fields)

| LobbyView field | Status | Rationale |
|---|---|---|
| `bill_client_link` | **NOT_COVERED** (operational; not a disclosure observable) | Edge derived by Kim 2018's 5-step bill-detection pipeline (regex bill numbers + Congress disambiguation + title-matching + propagation). It's *inferred* from Section 16 text — not a separately-disclosed observable. State-level: most states don't require explicit bill-level linkage at the report-row level; bill IDs appear inline in spending-report narratives. **No compendium 2.0 row** captures inferred-link as a disclosure; would be a pipeline derived field, not a cell. |
| `n_bills_sponsored` | EXTERNAL_ENRICHMENT (derived aggregate) | Aggregate count over (bill-client edge × legislator-bill sponsorship); not LDA-disclosed. |

### Industry/firm enrichments (2 fields)

| LobbyView field | Status |
|---|---|
| `firm_financials` (Compustat merge) | EXTERNAL_ENRICHMENT |
| `industry_herfindahl` (computed metric) | EXTERNAL_ENRICHMENT |

### Kim 2025 add-ons (4 fields)

| LobbyView field | Status | Compendium row(s) / rationale |
|---|---|---|
| `bill_position` | **COVERED (row exists; federal LDA cell value is FALSE / not-disclosed)** | `lobbyist_spending_report_includes_position_on_bill` + reg-form-side α-pair (Sunlight #1 introduced, Opheim β AND reader, FOCAL contact_log.10 reader — 3-rubric-confirmed). **Important nuance**: federal LDA does NOT require lobbyists to disclose their position on bills; Kim 2025 *infers* positions via LLM+GNN, it doesn't read them from a disclosure field. **Wisconsin is the only US state that requires position-on-bill disclosure** (per LobbyView source `items_LobbyView.md` §6, and confirmed in Opheim mapping §"State-level analog"). So the compendium row exists and correctly captures the disclosure observable; the Federal_US cell value is `FALSE` (LDA doesn't require it), the WI cell is `TRUE`, most other states are `FALSE`. Kim 2025's `bill_position` is therefore an *inferred-from-text* operational dataset, not a coverage gap. |
| `lobbyist_id` | OPERATIONAL_METADATA (descriptors row covers the name) | Individual-lobbyist disclosure is COVERED via `lobbyist_reg_form_includes_lobbyist_full_name` (FOCAL descriptors.1 — NEW row) + the listing requirement HG Q9 reads. The "ID" itself is operational (LobbyView's name-disambiguation produces a stable lobbyist_id; LDA reports list individuals by name on LD-2 lobbyist roster). Not exposed as a first-class endpoint in the 2024 LobbyView public API. |
| `lobbyist_demographics` | EXTERNAL_ENRICHMENT (inferred features) | Kim 2025 GNN-inferred ethnicity / gender / past party affiliation. NOT a disclosure observable in any state or federal regime. Out of scope for compendium. |
| `client_industry_features` | EXTERNAL_ENRICHMENT (Kim 2025 GNN features) | 426-dimensional inferred industry classification, finer than NAICS. NOT a disclosure observable. |

**Kim 2025 add-ons tally:** 1 COVERED-with-nuance (`bill_position` — row exists, federal cell value is FALSE because LDA doesn't disclose this) + 1 OPERATIONAL_METADATA + 2 EXTERNAL_ENRICHMENT.

### Infrastructure (2 fields)

| LobbyView field | Status | Compendium row(s) / rationale |
|---|---|---|
| `api_bulk_download` | **COVERED** | `lobbying_data_downloadable_in_analytical_format` (PRI accessibility.Q6 + CPI #206 + FOCAL openness.3/.4 — 4-rubric-confirmed practical-availability row). Federal LobbyView API provides REST endpoints with rate limits (100 requests / 100 rows × 100/day per LobbyView docs); compendium row is binary present/absent. |
| `full_text_search_index` | **COVERED-PARTIAL** | `lobbying_search_simultaneous_multicriteria_capability` (PRI Q8 + FOCAL openness.5; typed `int 0..15`) captures search-richness. `lobbyist_directory_available_as_searchable_database_on_web` (HG Q31 tier 3) + spending-report variant (Q32 tier 3) capture basic searchability. Full-text search specifically (Elasticsearch in LobbyView production; Whoosh in 2018 draft) is FINER than these — neither row distinguishes full-text vs structured search. **Candidate compendium 2.0 freeze refinement**: split `lobbying_disclosure_indexed_for_full_text_search` from the existing searchable-database row, or treat as a sub-feature of the searchable-database cell. YAGNI says no for now; flagging. |

---

## Coverage summary

| Group | Total fields | COVERED | COVERED-PARTIAL | NOT_COVERED (NEW-row candidates) | OPERATIONAL_METADATA | EXTERNAL_ENRICHMENT |
|---|---:|---:|---:|---:|---:|---:|
| Reports table | 13 | 7 | 0 | 2 | 3 | 2 (NAICS) |
| Issues table | 4 | 2 | 1 | 1 | 1 | 0 |
| Section 18 (revolving door) | 1 | 1 | 0 | 0 | 0 | 0 |
| Bills table | 11 | 0 | 0 | 0 | 0 | 11 |
| Legislators table | 7 | 0 | 0 | 0 | 0 | 7 |
| Networks/derived links | 2 | 0 | 0 | 1 | 0 | 1 |
| Industry/firm enrichments | 2 | 0 | 0 | 0 | 0 | 2 |
| Kim 2025 add-ons | 4 | 1 (w/ nuance) | 0 | 0 | 1 | 2 |
| Infrastructure | 2 | 1 | 1 | 0 | 0 | 0 |
| **Total** | **46** | **12** | **2** | **4** | **5** | **25** |

**Federal_US LDA disclosure-observable coverage** (excluding OPERATIONAL_METADATA + EXTERNAL_ENRICHMENT, which aren't disclosure observables): **(12 + 2) / (12 + 2 + 4) = 14/18 = 78%** of LDA-disclosed observables are covered by existing compendium 2.0 rows (with the just-added FOCAL-1 row included).

The 4 NOT_COVERED candidate NEW rows for compendium 2.0 freeze brainstorm:
1. `lobbyist_report_distinguishes_in_house_vs_contract_filer` (binary; legal) — from LobbyView `is_client_self_filer` / LDA §10.
2. `lobbyist_filings_flagged_as_amendment_vs_original` (binary; legal) — from LobbyView `is_amendment` / LDA amendment indicator.
3. `lobbying_disclosure_uses_standardized_issue_code_taxonomy` (binary; legal) — from LobbyView `issue_code` / LDA §15. Distinct from the free-text subject row.
4. `lobbying_report_records_inferred_bill_links_to_specific_bills` (binary; practical or operational) — from LobbyView `bill_client_link`. Debatable: this is derived inference, not disclosure. Recommended disposition: **OUT** (operational, not a disclosure cell). The actual disclosed observable (bill_id mentioned in report) is already covered.

If items 1–3 are pulled in at compendium 2.0 freeze, compendium row count goes from ~111 (post-FOCAL-1) to ~114.

---

## Watchpoints walked (per handoff)

### Watchpoint 1 — `contributions_from_others` final promotion check on LobbyView

**Prediction (handoff):** LobbyView NOT a reader; row stays single-rubric (Newmark 2017 only) across the entire contributing set.

**Walk:** No LobbyView schema field reads "third-party contributions received by the lobbyist/principal earmarked for lobbying." LobbyView's `amount` is the registrant-reported income (firm) or expense (in-house) — both are own-money, not third-party-INCOMING-for-lobbying contributions. LDA itself has LD-203 semi-annual contribution reports, but those capture OUTGOING contributions (to officials), not INCOMING contributions earmarked for lobbying (the Newmark 2017 distinctive observable). LobbyView does not expose LD-203 data through the public API as of the 2024 README.

**Result: CONFIRMED. LobbyView is NOT a reader.** Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row is now **single-rubric across the entire 9-rubric contributing set.**

**Compendium 2.0 freeze recommendation: KEEP the row** per Newmark-distinctive-observable rationale. The observable is real (Massachusetts principal reports list dues earmarked for lobbying; some states explicitly require disclosure of restricted contributions received), even if no other contributing rubric atomizes for it. Single-rubric reads are not a deletion criterion when the underlying observable is statutorily-confirmed.

### Watchpoint 2 — `def_target_*` 4-cell extension validation

**Prediction:** check whether LobbyView's `gov_entity` field validates the 4-cell `def_target_*` family (legislative_branch + executive_agency + governors_office + legislative_or_executive_staff).

**Walk:** LDA §17 requires registrants to list "House(s) of Congress and Federal agencies" contacted. The federal-LDA coverage of this row family:
- `def_target_legislative_branch`: TRUE for federal LDA (LD-2 §17 lists "U.S. Senate / U.S. House of Representatives" as contactable entities; legislative branch is explicitly in scope).
- `def_target_executive_agency`: TRUE (federal agencies are explicitly in scope).
- `def_target_governors_office`: N/A at federal level (no governor); but the federal-equivalent "executive office of the president" is in scope.
- `def_target_legislative_or_executive_staff`: TRUE (LDA's "covered legislative branch official" definition includes staff per 2 USC §1602(4); congressional and executive staff are explicitly in scope).

**Result:** LDA covers 4/4 cells (including the staff cell — FOCAL scope.3's partly-tier discriminator). **Confirms the `def_target_*` family extension** to 4 cells (the FOCAL-introduced 4th cell `def_target_legislative_or_executive_staff` is validated against the federal regime). Federal-state asymmetry: at the federal level the staff cell is uniformly TRUE; state-level, the cell discriminates between states that include staff in their lobbyist-target definition and states that limit to elected officials only.

### Watchpoint 3 — covered_official_position validates the FOCAL-1-resolved row

**Prediction (added this session post-FOCAL-1 resolution):** LDA §18 disclosure of prior covered government employment should map onto the just-added `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` row (FOCAL-1 resolution).

**Walk:** LDA Form LD-1 / LD-2 §18 ("Covered Official Position") requires the registrant to list "any employees who have acted or are expected to act as lobbyists on behalf of the client and whose past employment includes service as a covered executive branch official or a covered legislative branch official in the previous 20 years" (2 USC §1604(b)(2)(C)). This is the reg-form-side disclosure of prior public offices held — exactly what FOCAL `revolving_door.1` reads, and exactly what the FOCAL-1-resolved compendium row captures.

**Result: CONFIRMED.** The FOCAL-1-introduced row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` is **2-rubric-confirmed** (FOCAL + LobbyView; LobbyView reads via the `covered_official_position` schema field; FOCAL reads via revolving_door.1). Federal LDA cell value is `TRUE`; this is the load-bearing disclosure observable for Kim 2025's "lobbyist-legislator previously worked together" GNN edges. **The FOCAL-1 decision was correct.** State-level coverage is uneven — many states require nothing equivalent; some require multi-year disclosure with specific office details. This is high-value for any state-level revolving-door empirical work.

---

## Three known ambiguities (carried forward from handoff)

These were flagged in the 2026-05-11 handoff as carry-forward concerns; they're documented here for completeness.

1. **`lobbyist_id` / `lobbyist_demographics` are in Kim 2025's GNN, NOT in the public LobbyView API as of late-2024 README.** Lobbyist nodes are central in Kim 2025 (25,043 lobbyists, with ethnicity / gender / party / past-Congress-affiliation features). This means the published bill-position dataset and the public-API surface are not 1:1. **Implication for compendium**: the LDA-disclosed observable (individual lobbyists listed by name on LD-2 §3) IS covered by descriptors-family rows; the GNN-inferred features (`lobbyist_demographics`) are NOT disclosure observables and stay out of scope.

2. **Kim 2018's bill-detection pipeline has no published precision/recall.** The 2018 working paper promises "we will conduct several descriptive and statistical analyses to demonstrate the scope and quality of the lobbying database" but does not deliver IRR/F1 numbers. **Implication for compendium**: doesn't affect schema coverage (the pipeline output `bill_client_link` is operational/derived, not a disclosure observable). It DOES affect downstream methodology — any state-level pipeline that infers bill links from spending-report text would need its own validation.

3. **`bill_position` is Wisconsin-only at the state level.** WI requires lobbyists to disclose support/oppose/no-position on each piece of lobbied legislation (per items_LobbyView.md §6 + Sunlight mapping). At the federal level, LDA does NOT require position disclosure — Kim 2025's `bill_position` is LLM+GNN-inferred. **Implication for compendium**: the `lobbyist_spending_report_includes_position_on_bill` row (Sunlight-introduced, 3-rubric-confirmed) correctly captures the *disclosure* observable. Federal_US cell value is `FALSE` (LDA doesn't require it); WI cell is `TRUE`; most other states `FALSE`. The Kim 2025 LPscores dataset is an inferred enrichment, separate from the compendium row's binary disclosure semantics.

---

## What this validates / invalidates

1. **`contributions_from_others` row stays single-rubric across the entire 9-rubric contributing set.** No LobbyView field reads incoming-contributions-earmarked-for-lobbying. The row stays in compendium 2.0 per Newmark-distinctive-observable rationale (real observable, rare disclosure). Watchpoint 1 confirmed.

2. **`def_target_*` 4-cell family is empirically validated against the federal LDA regime.** All four cells populate `TRUE` for federal jurisdiction. The 4th cell (`def_target_legislative_or_executive_staff`), introduced by FOCAL scope.3 partly-tier discrimination, is empirically confirmed by LDA's "covered legislative branch official" definition (2 USC §1602(4)). Watchpoint 2 confirmed.

3. **FOCAL-1 resolution (revolving_door.1 IN) is empirically validated by LDA §18.** The just-added `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` row is now **2-rubric-confirmed** (FOCAL + LobbyView). The federal-LDA `covered_official_position` field is the canonical state-of-the-art federal disclosure observable for revolving-door research (used by Kim 2025's GNN). Watchpoint 3 confirmed.

4. **78% Federal_US LDA disclosure-observable coverage** vs the handoff prediction of ~100%. The shortfall is 4 candidate NEW rows: `is_client_self_filer`, `is_amendment`, `issue_code` (Section 15 taxonomy), and (debatable) `bill_client_link`. These are compendium 2.0 freeze candidates. **The shortfall is interpretable**: the handoff predicted ~100% because LobbyView IS federal LDA data, but a closer reading distinguishes (a) LDA-disclosed observables that need compendium rows, (b) operational metadata that doesn't, and (c) external enrichments that LobbyView ADDS on top of LDA but that aren't themselves disclosed.

5. **The 8 prior score-projection mappings + this schema-coverage mapping cover the disclosure side of the compendium** for compendium 2.0 freeze planning. Phase B closes after this mapping; the union step (`disclosure_side_compendium_items_v1.tsv`) consumes all 9 mapping docs.

---

## Open issues surfaced by LobbyView (for compendium 2.0 freeze)

1. **LV-1 — `is_client_self_filer` candidate NEW row.** Should compendium 2.0 add `lobbyist_report_distinguishes_in_house_vs_contract_filer`? Argument for: LDA explicitly distinguishes; some research uses the distinction (Kim 2025 includes "Government" boolean as a node feature on the interest-group side). Argument against: implicit in α form-split + scope.2 (in-house lobbyists may have different thresholds than contract). YAGNI defers; decision at freeze.

2. **LV-2 — `is_amendment` candidate NEW row.** Should compendium 2.0 add `lobbyist_filings_flagged_as_amendment_vs_original`? Argument for: empirically useful for downstream researchers (amended filings tend to correct earlier misreporting; the amendment flag is a data-quality signal). Argument against: operational metadata, not a disclosure substance. YAGNI defers; decision at freeze.

3. **LV-3 — `issue_code` (Section 15 standardized taxonomy) candidate NEW row.** Should compendium 2.0 add `lobbying_disclosure_uses_standardized_issue_code_taxonomy`? Argument for: federal LDA is distinctive in mandating a fixed taxonomy; most states don't. The presence/absence of a standardized taxonomy is itself a structural-quality signal. Argument against: weakly observable at state level (many states have a state-specific taxonomy that's neither LDA's nor free-text). Recommendation: pull in as a typed cell with values {none / state_specific_taxonomy / lda_taxonomy / other_taxonomy} rather than a binary. Decision at freeze.

4. **LV-4 — `full_text_search_index` vs `searchable_database` distinction.** Compendium 2.0 has a `lobbyist_directory_available_as_searchable_database_on_web` row (HG Q31 tier 3) and `lobbying_search_simultaneous_multicriteria_capability` (PRI Q8 / FOCAL openness.5), but doesn't distinguish full-text search from structured search. LobbyView production uses Elasticsearch (full-text); the 2018 paper draft used Whoosh. Granularity bias could justify splitting; YAGNI says no until a rubric reads it. Decision at freeze.

5. **LV-5 — `bill_client_link` is operational, not disclosure.** Argument against adding a compendium row: LobbyView derives `bill_client_link` via Kim 2018's bill-detection pipeline; it's NOT a state-disclosed observable. The disclosed observable (`lobbyist_spending_report_includes_bill_or_action_identifier`) is already covered. **Recommended disposition: OUT of compendium 2.0.** LV-5 is documented for closure rather than deferred.

6. **LV-6 — External enrichment surface.** 25 of 46 LobbyView fields are external enrichments (Congress.gov / CRS / Bioguide / GovTrack / Compustat / Kim 2025 GNN features). None belong in compendium 2.0. **This is informational, not a freeze decision** — but the next stage's project-management plan (post-Phase-B) should think about whether to build a parallel "enrichment-coverage" data layer separate from the compendium, for state-level analogs of LobbyView's external merges (e.g., state legislator IDs from OpenStates, state-level industry classifications, etc.). Out of scope for compendium 2.0 freeze.

---

## What LobbyView doesn't capture that other rubrics do

For continuity with the score-projection mappings' "What FOCAL/PRI/CPI etc. doesn't ask" sections — what LobbyView (federal-only data infrastructure) doesn't capture that the state-rubric set DOES ask about:

- **Quantitative thresholds for lobbyist registration.** LDA has $3K / $13K / 20%-time thresholds and LobbyView indexes the FILINGS that result, but the *thresholds themselves* are statutory and not surfaced as LobbyView schema fields. The compendium has typed cells `compensation_threshold_for_lobbyist_registration` / `expenditure_threshold_for_lobbyist_registration` / `time_threshold_for_lobbyist_registration` (CPI #197 + Newmark/HG/Opheim readers) that LobbyView doesn't read. State-level analog: each state's thresholds vary substantially; the compendium captures them.
- **Reporting cadence variations.** LobbyView's `report_quarter_code` reflects LDA's post-HLOGA mandatory quarterly cadence; the underlying statutory cadence rules (which the compendium captures via cadence-family binaries + FOCAL timeliness.* practical-axis cells) are not LobbyView observables. State-level: cadence varies enormously across states.
- **Portal-availability quality features (descriptors-side).** LobbyView's API IS its portal, but the broader practical-availability quality features (FOCAL openness.* battery, HG Q28-Q38 access-tier ladder, PRI accessibility.Q1-Q6 + Q7a-Q7o filter granularity) are state-portal observables, not federal-LobbyView observables. The compendium captures these.
- **Itemization-de-minimis thresholds.** Sunlight #3 + HG Q15 read `expenditure_itemization_de_minimis_threshold_dollars` (the dollar floor below which individual expenditures need not be itemized). LDA's $5K / $10K / $25K itemization rules exist but are not LobbyView fields; the compendium row is state-level-tractable.
- **Filing-de-minimis thresholds.** PRI D1's `lobbyist_filing_de_minimis_threshold_dollars` similarly. Federal LDA has thresholds; LobbyView doesn't expose them as fields.
- **Gifts / entertainment / transport / lodging bundles.** Federal LDA has separate gift-disclosure rules (HLOGA + 2007 amendments) that LobbyView doesn't index as schema fields. The compendium has the 5-rubric-confirmed bundle (PRI E1f_iii + Newmark 2017/2005 + Opheim + HG Q23/Q14 + FOCAL financials.10).
- **Position-on-bill (disclosure-side observable).** Federal LDA doesn't require it; Kim 2025 LLM-INFERS it. The compendium captures the disclosure observable (single-state WI; covered by Sunlight #1 row).
- **Per-meeting contact_log.** FOCAL atomizes contact-log into 9 per-meeting cells; LobbyView's `gov_entity` aggregates at issue level. FOCAL is finer than LobbyView on this battery.

This is consistent with the LobbyView source `items_LobbyView.md` §6's "federal-vs-state gap" enumeration: LDA defines a single federal scope; state regimes vary substantially in cadence, itemization, threshold structure, and what's mandated at all.

---

## Files this mapping is the index for

- Source TSV: [`../items_LobbyView.tsv`](../items_LobbyView.tsv) (46 fields, production-schema extraction)
- Companion methodology: [`../items_LobbyView.md`](../items_LobbyView.md) (sections 1-8: shape, sources, relationship to items_Kim2018, field grouping, schema-as-rubric mapping decisions, federal-vs-state gap, open questions, downstream use)
- Paper-shaped predecessor: [`../items_Kim2018.tsv`](../items_Kim2018.tsv) (18 paper-shaped rows; kept; not superseded — different granularity)

---

## Phase B status after this mapping

**Phase B is COMPLETE.** All 9 mappings shipped:

1. ✅ CPI 2015 C11 (21 rows)
2. ✅ PRI 2010 (69 rows touched)
3. ✅ Sunlight 2015 (13 rows)
4. ✅ Newmark 2017 (14 rows; 8 reused + 6 new)
5. ✅ Newmark 2005 (14 rows; 100% reuse)
6. ✅ Opheim 1991 (14 rows; 100% reuse)
7. ✅ HiredGuns 2007 (38 rows; 16 reused + 22 new)
8. ✅ FOCAL 2024 (58 rows post-FOCAL-1; 22 reused + 36 new)
9. ✅ LobbyView 2018/2025 (schema-coverage; 14/18 disclosure-observable subset COVERED; 4 candidate NEW rows flagged for freeze)

(OpenSecrets 2022 was structured-tabled 2026-05-13 with 3 distinctive-row candidates also tabled. Drop is reversible.)

**Phase B done condition (per locked plan):** the next step is the union of all 9 mapping docs' compendium-row references into `results/projections/disclosure_side_compendium_items_v1.tsv`. Post-FOCAL-1 + post-LobbyView, the expected row count is **~111 rows** (~110 pre-FOCAL-1 + 1 from FOCAL-1 + 0 from LobbyView at this step, since LobbyView's candidate NEW rows are freeze-decision-deferred). If LV-1 + LV-2 + LV-3 are pulled in at freeze, the count grows to ~114.

**Phase C** (code projections under TDD, locked order: CPI 2015 C11 first → ... → FOCAL last) can begin in a subsequent session against compendium-2.0 row shape. LobbyView is not a Phase C target (no score to project).

# Compendium Audit Report

**Compendium version:** v1 (commit pre-audit: `b6f26e2` — 118 disclosure_items rows + 140 framework_dedup_map entries)
**Audit date:** 2026-04-30
**Audit scope:** 4-rubric union (PRI 2010 disclosure + accessibility, FOCAL 2024, Sunlight 2015) → 9-rubric union (adds Opheim 1991, Newmark 2005, Newmark 2017, CPI Hired Guns 2007, OpenSecrets 2022)
**Originating plan:** [`plans/20260430_compendium_expansion_v2.md`](../plans/20260430_compendium_expansion_v2.md)
**Branch:** `filing-schema-extraction`. On merge to main, this file moves to repo-level `docs/COMPENDIUM_AUDIT.md`.

This is the **durable anti-loop artifact** — every contested call is recorded so future sessions don't re-derive. Read this before re-curating the compendium.

---

## Summary

- **Pre-audit:** 118 compendium rows from 4 rubrics (PRI 2010 disclosure 61 rows, PRI 2010 accessibility 22 rows, FOCAL 2024 50 indicators, Sunlight 2015 ~7 unique items).
- **Post-v2-audit:** 139 compendium rows (+21 new rows from 5 walked rubrics).
- **Post-v1.2 (Decision Log D11, 2026-05-01):** **141 compendium rows** (+2 symmetry-gap rows). 7 rows now in new `domain="definitions"`.
- **Items walked:** 114 atomic items across 5 rubrics.
  - Newmark 2017: 19 items
  - Newmark 2005: 18 items (1 dropped by author as constant)
  - Opheim 1991: 22 items
  - CPI Hired Guns 2007: 48 items
  - OpenSecrets 2022: 7 atomic items (4 main categories + 3 public-availability sub-items)
- **Items folded into existing rows (`EXISTS`/`MERGE`):** 87 dedup-map entries across the 5 walked rubrics (one per atomic item that mapped to an existing or boolean-expression target).
- **Items added as new rows (`NEW`):** 21 net new compendium rows from v2 (Opheim's "other influence peddling" catch-all folded into `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` rather than getting its own row); +2 in v1.2 (`DEF_EXPENDITURE_STANDARD`, `DEF_TIME_STANDARD`) for a cumulative **23 NEW rows**. Multiple rubrics often reference the same new row (e.g., `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is referenced by Newmark 2017, Newmark 2005, Opheim 1991, and CPI Q1).
- **Items excluded (`OUT_OF_SCOPE`):** 27 dedup-map entries (Newmark 2017: 5 prohibitions, Newmark 2005: 4 prohibitions, Opheim 1991: 7 enforcement, CPI Hired Guns 2007: 11, OpenSecrets 2022: 0). Categorized: 12 prohibitions + 4 penalties + 12 enforcement + 1 revolving-door + the deferred Q30 (counted separately from OOS). Some atomic items are PARTIAL — disclosure half EXISTS, restriction half OUT_OF_SCOPE — and book to a single dedup-map entry with the dominant disposition.
- **Schema bump avoided:** `domain="definitions"` not added; definition-trigger items folded into `domain="registration"` with a `notes` flag (`"definition-trigger criterion (review for v1.2 domain='definitions' promotion)"`) per user direction. **All notes-flagged rows are listed in the Decision Log below for end-of-audit review.**

---

## Schema decision: definition-trigger items

**Verified during audit:** `CompendiumItem.domain` is a fixed `Literal[...]` in `src/lobby_analysis/models/compendium.py:21-32` with 10 allowed values: `registration, reporting, financial, contact_log, relationship, gift, revolving_door, accessibility, enforcement, other`. **No `definitions` value.**

The plan anticipated this fork (line 170): *"if fixed, propose v1.2 in a separate plan."* User direction (this session): **Option A** — fold definition-trigger items into `domain="registration"` with a `notes` flag for end-of-audit review. Rationale: the audit's purpose is curation, not schema work; punting on schema lets the audit finish without spillover.

Notes flag standardized as: `"definition-trigger criterion (review for v1.2 domain='definitions' promotion)"`. See **Decision Log** for the full list of notes-flagged rows.

---

## Rubrics walked (in order)

### Newmark 2017 — *Lobbying regulation in the states revisited*

**Source:** `papers/Newmark_2017__lobbying_regulation_revisited.pdf` (text at `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`)
**Item count:** 19 (7 definitions + 5 prohibited activities + 7 disclosure/reporting)
**Items added as new rows:** 4
**Items folded into existing rows:** 10
**Items excluded:** 5

| Rubric item | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| def_legislative_lobbying | Statutory definition includes legislative-branch contact as lobbying | EXISTS | `REG_LOBBYIST` | Universal yes (all 50 states); definitional trigger ≈ existence of any lobbyist-registration regime. Notes-flag `REG_LOBBYIST`. |
| def_admin_agency_lobbying | Statutory definition includes administrative-agency lobbying | NEW | `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (new) | Definition-side coverage of executive-branch lobbying as registration trigger; PRI A6 covers executive *agencies as registrants*, not whether lobbying-them is in the *definition*. Notes-flag. |
| def_elected_officials_as_lobbyists | Elected officials defined as lobbyists when in lobbying-related behaviors | NEW | `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` (new) | PRI A5/A7 cover branches as registrants, not individuals crossing over. Notes-flag. |
| def_public_employees_as_lobbyists | Public employees defined as lobbyists | NEW | `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` (new) | PRI A10 (REG_GOVT_LOBBYING_GOVT) covers agencies; this covers individual public employees. Notes-flag. |
| def_compensation_standard | Definition includes compensation-received threshold | NEW | `DEF_COMPENSATION_STANDARD` (new) | PRI D1 is expenditure-side (expenses below $X exempt); Newmark's compensation standard is income-side (paid > $X = lobbyist). Distinct mechanism. Notes-flag. |
| def_expenditure_standard | Definition includes expenditure threshold | EXISTS | `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (D1_present) | Same statutory mechanism as PRI D1. Add framework_reference. Notes-flag. |
| def_time_standard | Definition includes time threshold | EXISTS | `THRESHOLD_LOBBYING_TIME_PRESENT` (D2_present) | Same statutory mechanism as PRI D2. Add framework_reference. Notes-flag. |
| prohib_contribs_anytime | Lobbyists prohibited from campaign contributions at any time | OUT_OF_SCOPE | — | Prohibition; no filing carries this as data. |
| prohib_contribs_session | Lobbyist contributions prohibited during legislative sessions | OUT_OF_SCOPE | — | Prohibition. |
| prohib_solicitation | Solicitation by officials/employees for contributions or gifts | OUT_OF_SCOPE | — | Prohibition. |
| prohib_contingent_comp | Contingent compensation prohibited | OUT_OF_SCOPE | — | Prohibition. |
| prohib_revolving_door | Revolving-door cooling-off period required | OUT_OF_SCOPE | — | Restriction; no filing. (Compendium has `REVOLVING_COOLING_OFF_DATABASE` from FOCAL 5.2 — that's a *database* of restricted officials, distinct from the prohibition itself.) |
| disc_seeking_to_influence | Disclosure: sought to influence legislative/administrative action | MERGE | `(E1g_i \| E1g_ii \| E2g_i \| E2g_ii)` → existing rows `RPT_PRINCIPAL_ISSUE_GENERAL`, `RPT_PRINCIPAL_BILL_SPECIFIC`, `RPT_LOBBYIST_ISSUE_GENERAL`, `RPT_LOBBYIST_BILL_SPECIFIC` | Newmark's binary "subject of influence disclosed" = disjunction over PRI's general+bill / principal+lobbyist 4-row split. |
| disc_exp_benefitting_officials | Disclosure: expenditures benefitting public officials | EXISTS | `RPT_PRINCIPAL_OTHER_COSTS` (E1f_iii) + `RPT_LOBBYIST_OTHER_COSTS` (E2f_iii) | Already captured (also via FOCAL 7.10 → same rows). Add Newmark framework_reference. |
| disc_comp_by_employer | Disclosure: compensation broken down by employer | EXISTS | `FIN_INCOME_PER_CLIENT` (FOCAL 7.2) | Direct match on "income per client/employer." |
| disc_total_compensation | Disclosure: total compensation received | EXISTS | `RPT_LOBBYIST_COMPENSATION` (E2f_i) | Direct match. |
| disc_categories_expenditures | Disclosure: expenditures by category | EXISTS | `RPT_EXPENDITURE_FORMAT_GRANULARITY` (Sunlight) | Sunlight's granularity ordinal captures "categories disclosed." |
| disc_total_expenditures | Disclosure: total expenditures toward lobbying | MERGE | `(E1f_i & E1f_ii & E1f_iii) \| (E2f_i & E2f_ii & E2f_iii)` → `RPT_PRINCIPAL_*` triple, `RPT_LOBBYIST_*` triple | Total expenditure = sum of comp + non-comp + other on either side. Mirrors FOCAL 7.6 dedup pattern. |
| disc_contribs_received | Disclosure: contributions received from others for lobbying | EXISTS | `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` (E1j) | Same concept (sponsors / sources of lobbying funding). |

### Newmark 2005 — *Measuring State Legislative Lobbying Regulation, 1990–2003*

**Source:** `papers/Newmark_2005__state_lobbying_regulation_measure.pdf` (text at `papers/text/Newmark_2005__state_lobbying_regulation_measure.txt`)
**Item count:** 18 (7 definitions + 1 frequency-binary + 4 prohibited activities + 6 disclosure)
**Items added as new rows:** 0 (all folds into N2017 dispositions or existing rows)
**Items folded into existing rows:** 14
**Items excluded:** 4

The 7 definitions are **identical** to N2017's 7 definitions (Newmark explicitly inherits from this 2005 paper in the 2017 redo). Same dispositions; framework_references just add `newmark_2005` alongside `newmark_2017`.

The 6 disclosure items are a **proper subset** of N2017's 7 (N2017 added "contributions received from others"). Same dispositions for the 6 shared items.

| Rubric item | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| def_*  (7 items) | Same as N2017 def_* | (see N2017 table) | (see N2017 table) | Add `newmark_2005` framework_reference alongside `newmark_2017`. |
| freq_binary | Reporting more frequently than annual = 1, else 0 | MERGE | `(FREQ_LOBBYIST_MONTHLY \| FREQ_LOBBYIST_QUARTERLY \| FREQ_LOBBYIST_TRI_ANNUAL \| FREQ_LOBBYIST_SEMI_ANNUAL) \| (corresponding FREQ_PRINCIPAL_*)` | Aggregate "more-than-annual" = disjunction of the 4 above-annual cadence rows on either side. |
| prohib_contribs_anytime | (same as N2017) | OUT_OF_SCOPE | — | Prohibition. |
| prohib_contribs_session | (same as N2017) | OUT_OF_SCOPE | — | Prohibition. |
| prohib_expenditures_over_cap | Expenditures over a dollar cap prohibited | OUT_OF_SCOPE | — | Prohibition (gift-cap on lobbying spending). N2017 dropped this in favor of contingent-comp + revolving-door. |
| prohib_solicitation | (same as N2017) | OUT_OF_SCOPE | — | Prohibition. |
| disc_* (6 items) | Same as N2017's first 6 disclosure items | (see N2017 table) | (see N2017 table) | Add `newmark_2005` framework_reference. |

### Opheim 1991 — *Explaining the Differences in State Lobby Regulation*

**Source:** `papers/Opheim_1991__state_lobby_regulation.pdf` (text at `papers/text/Opheim_1991__state_lobby_regulation.txt`)
**Item count:** 22 (7 definitions + 8 frequency-and-quality-of-disclosure + 7 oversight/enforcement)
**Items added as new rows:** 0
**Items folded into existing rows:** 15
**Items excluded:** 7

Opheim is the foundational ancestor of Newmark 2005/2017 — the 7 definition items are word-for-word identical. The disclosure items significantly overlap with Newmark/PRI; the enforcement items are out of scope en bloc.

| Rubric item | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| def_* (7 items) | Same as N2017 def_* | (see N2017 table) | (see N2017 table) | Add `opheim_1991` framework_reference. |
| freq_binary | Reports filed monthly during session = 1, else 0 | MERGE | (same as N2005 freq_binary disjunction) | Same concept; identical disjunction expression. |
| disc_total_spending | Total expenditures disclosed | MERGE | (same as N2017 disc_total_expenditures) | (see N2017 table) |
| disc_spending_by_category | Spending by category disclosed | EXISTS | `RPT_EXPENDITURE_FORMAT_GRANULARITY` | (see N2017 disc_categories_expenditures) |
| disc_exp_benefitting_employees | Expenditures benefitting public employees including gifts | EXISTS | `RPT_PRINCIPAL_OTHER_COSTS` + `RPT_LOBBYIST_OTHER_COSTS` | (see N2017 disc_exp_benefitting_officials) |
| disc_legislation_supported_opposed | Legislation approved or opposed by lobbyist | EXISTS | `RPT_POSITION_TAKEN` (Sunlight position_taken) | Direct match — position-taken disclosure. Also overlaps `RPT_LOBBYIST_BILL_SPECIFIC`. |
| disc_sources_of_income | Sources of income disclosed | EXISTS | `FIN_INCOME_PER_CLIENT` (FOCAL 7.2) | Income broken by client/source. |
| disc_total_income | Total income disclosed | EXISTS | `RPT_LOBBYIST_COMPENSATION` (E2f_i) | (same as N2017 disc_total_compensation) |
| disc_other_influence_peddling | Other activities constituting influence peddling / conflict of interest | EXISTS | `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` (E1j) | Catch-all category Opheim leaves vague. Closest existing match is "major financial contributors." Flagged in **Decision Log** as borderline. |
| enforce_review_thoroughness | Review of all reports vs random | OUT_OF_SCOPE | — | Enforcement. |
| enforce_subpoena_witnesses | Agency may subpoena witnesses | OUT_OF_SCOPE | — | Enforcement. |
| enforce_subpoena_records | Subpoena records | OUT_OF_SCOPE | — | Enforcement. |
| enforce_admin_hearings | Conduct administrative hearings | OUT_OF_SCOPE | — | Enforcement. |
| enforce_admin_fines | Impose administrative fines | OUT_OF_SCOPE | — | Enforcement. |
| enforce_admin_penalties | Impose administrative penalties | OUT_OF_SCOPE | — | Enforcement. |
| enforce_court_actions | File independent court actions | OUT_OF_SCOPE | — | Enforcement. |

### CPI Hired Guns 2007 — *Methodology*

**Source:** `papers/CPI_2007__hired_guns_methodology.pdf` (text at `papers/text/CPI_2007__hired_guns_methodology.txt`)
**Item count:** 48 questions across 8 categories (Definition 2, Individual Registration 8, Individual Spending 15, Employer Spending 2, Electronic Filing 3, Public Access 8, Enforcement 9, Revolving Door 1)
**Items added as new rows:** 16 (most of the row growth in this audit is from CPI)
**Items folded into existing rows:** 21
**Items excluded:** 11 (Q23 limit/prohibition halves and Q24 prohibition half count separately from their EXISTS-disposition disclosure halves)

| Q# | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| Q1 | Executive branch lobbying in definition | EXISTS | `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (new from N2017) | Same definition-trigger criterion. |
| Q2 | Compensation/expenditure threshold to qualify (multi-tier $) | MERGE | `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (D1_present) + `DEF_COMPENSATION_STANDARD` (new) + `THRESHOLD_LOBBYING_EXPENDITURE_VALUE` (D1_value) | CPI conflates compensation + expenditure thresholds; maps to both N2017 distinctions. |
| Q3 | Lobbyist must file registration form | EXISTS | `REG_LOBBYIST` (A1) | Direct match. |
| Q4 | Days lobbying allowed before registration required | NEW | `REG_PRE_LOBBYING_REGISTRATION_WINDOW` (new) | Distinct from PRI D2 (D2 is fraction-of-compensated-time exemption; CPI Q4 is delay-until-must-register window). |
| Q5 | Bill/subject required on registration form | NEW | `REG_BILL_SUBJECT_ON_REGISTRATION` (new) | PRI E1g/E2g cover bill/subject on *reporting*; CPI Q5 is on *registration*. Different filing. |
| Q6 | Frequency of registration (once / 2yr / annual+) | NEW | `REG_REGISTRATION_RENEWAL_FREQUENCY` (new) | Different from FREQ_*_* rows (those are reporting cadence, not registration-renewal cadence). |
| Q7 | Days to notify of registration changes | NEW | `REG_CHANGE_NOTIFICATION_WINDOW` (new) | New concept: turnaround window for amendment filings. |
| Q8 | Photo with registration | NEW | `REG_PHOTO_REQUIRED` (new) | New concept: photographic identification. |
| Q9 | Identify each employer by name on registration | EXISTS | `RPT_LOBBYIST_PRINCIPAL_NAMES` (E2c) | Same data point; different filing-level (registration vs report). PRI E2c also lives on registrations in practice. |
| Q10 | Compensated/non-compensated, salaried/contracted on registration | EXISTS | `RPT_LOBBYIST_CONTRACT_TYPE` (FOCAL 4.6) | Direct match. |
| Q11 | Lobbyist must file spending report | EXISTS | `RPT_LOBBYIST_GATE` (E2a) | Direct match. |
| Q12 | Filing count over 2-year cycle | EXISTS | `(FREQ_LOBBYIST_MONTHLY \| ... \| FREQ_LOBBYIST_ANNUAL)` | Quantitative version of frequency rows. |
| Q13 | Compensation/salary on spending reports | EXISTS | `RPT_LOBBYIST_COMPENSATION` (E2f_i) | Direct match. |
| Q14 | Spending categorized totals | EXISTS | `RPT_EXPENDITURE_FORMAT_GRANULARITY` | Same as N2017 disc_categories_expenditures. |
| Q15 | Itemization threshold ($ for itemization) | EXISTS | `RPT_EXPENDITURE_ITEMIZATION_THRESHOLD` (Sunlight) | Direct match (Sunlight rolled up). |
| Q16 | Identify lobbyist employer/principal for each itemized expenditure | NEW | `RPT_ITEMIZED_PRINCIPAL_BENEFITED` (new) | Itemized-expenditure metadata: which client benefited. New concept. |
| Q17 | Identify recipient of itemized expenditure | NEW | `RPT_ITEMIZED_RECIPIENT` (new) | Itemized-expenditure metadata: which official benefited. |
| Q18 | Date of itemized expenditure | NEW | `RPT_ITEMIZED_DATE` (new) | Itemized-expenditure metadata: when. |
| Q19 | Description of itemized expenditure | NEW | `RPT_ITEMIZED_DESCRIPTION` (new) | Itemized-expenditure metadata: what. |
| Q20 | Bill/subject on spending reports | EXISTS | `RPT_LOBBYIST_BILL_SPECIFIC` (E2g_ii) + `RPT_LOBBYIST_ISSUE_GENERAL` (E2g_i) | Direct match (lobbyist side). |
| Q21 | Spending on household members of public officials | NEW | `RPT_HOUSEHOLD_OF_OFFICIAL_SPENDING` (new) | Refinement of "expenditures benefitting officials" — extends to household. New row because the field is filing-data-shape distinct. |
| Q22 | Direct business associations with officials/candidates/households | EXISTS | `REL_OFFICIAL_BUSINESS_TIES` (FOCAL 6.4) | Direct match. |
| Q23 | Statutory provision for gifts (reported / limited / prohibited) | PARTIAL | reported→ `RPT_PRINCIPAL_OTHER_COSTS`, `RPT_LOBBYIST_OTHER_COSTS`; limit/prohibition→ OUT_OF_SCOPE | "Reported" half maps to existing OTHER_COSTS rows; "limited"/"prohibited" halves are gift-restrictions (out of scope). Add framework_reference for the disclosure half. |
| Q24 | Statutory provision for campaign contributions | PARTIAL | disclosed→ `FIN_CAMPAIGN_CONTRIBUTIONS` (FOCAL 7.11); prohibited→ OUT_OF_SCOPE | Same split as Q23. |
| Q25 | Lobbyist with no spending must file no-activity report | NEW | `RPT_ZERO_ACTIVITY_FILING` (new) | New concept: zero-activity report requirement. Filing-shape distinct. |
| Q26 | Employer/principal must file spending report | EXISTS | `RPT_PRINCIPAL_GATE` (E1a) | Direct match. |
| Q27 | Compensation paid to lobbyists on employer reports | EXISTS | `RPT_PRINCIPAL_COMPENSATION` (E1f_i) | Direct match. |
| Q28 | Online registration filing | EXISTS | `ACC_DEDICATED_WEBSITE` (Q2) + `ACC_DOWNLOAD_ANALYSIS_READY` (Q6) | Accessibility-side. |
| Q29 | Online spending report filing | EXISTS | (same accessibility rows) | Accessibility-side. |
| Q30 | Training for electronic filing | NEW | (deferred — accessibility-side, low priority) | Accessibility item without a current row. **Decision Log entry: deferred to a follow-up accessibility-rubric audit.** Not added now. |
| Q31 | Format of registrations directory | EXISTS | `ACC_DOWNLOAD_ANALYSIS_READY` (PRI Q6) + `ACC_DATA_AVAILABLE_AT_ALL` | Accessibility ordinal mappable to PRI rows. |
| Q32 | Format of spending reports | EXISTS | (same accessibility rows) | |
| Q33 | Cost of copies | NEW | `ACC_COPIES_COST` (new, accessibility) | New cost-barrier accessibility row. |
| Q34 | Sample forms on web | NEW | `ACC_SAMPLE_FORMS_ONLINE` (new, accessibility) | |
| Q35 | Aggregate spending total by year | NEW | `ACC_AGGREGATE_TOTALS_BY_YEAR` (new, accessibility) | Agency-published aggregation; not a per-filing data field. |
| Q36 | Aggregate spending by deadline | NEW | `ACC_AGGREGATE_TOTALS_BY_DEADLINE` (new, accessibility) | |
| Q37 | Aggregate spending by industry | NEW | `ACC_AGGREGATE_TOTALS_BY_INDUSTRY` (new, accessibility) | |
| Q38 | Lobby list update freshness | EXISTS | `ACC_REGISTRY_UPDATE_FRESHNESS` (FOCAL 2.1) | Direct match. |
| Q39 | Statutory auditing authority | OUT_OF_SCOPE | — | Enforcement. |
| Q40 | Mandatory reviews/audits | OUT_OF_SCOPE | — | Enforcement. |
| Q41 | Penalty for late registration | OUT_OF_SCOPE | — | Penalty. |
| Q42 | Penalty for late spending report | OUT_OF_SCOPE | — | Penalty. |
| Q43 | When penalty last levied (late report) | OUT_OF_SCOPE | — | Enforcement. |
| Q44 | Penalty for incomplete registration | OUT_OF_SCOPE | — | Penalty. |
| Q45 | Penalty for incomplete spending report | OUT_OF_SCOPE | — | Penalty. |
| Q46 | When penalty last levied (incomplete) | OUT_OF_SCOPE | — | Enforcement. |
| Q47 | Publish list of delinquent filers | OUT_OF_SCOPE | — | Enforcement-publication; not lobbying-disclosure data. **Decision Log entry: borderline — reconsider if a downstream consumer wants delinquent-filer signal.** |
| Q48 | Cooling-off period for legislators-becoming-lobbyists | OUT_OF_SCOPE | — | Revolving-door restriction. (Compendium has `REVOLVING_COOLING_OFF_DATABASE` from FOCAL 5.2 = different — that's a *database* of restricted officials, not the cooling-off requirement itself.) |

### OpenSecrets 2022 — *State Lobbying Disclosure Scorecard*

**Source:** `papers/OpenSecrets_2022__state_lobbying_disclosure_scorecard.pdf` (text at `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt`)
**Item count:** 7 atomic items (4 main scoring areas + 3 public-availability sub-items)
**Items added as new rows:** 1
**Items folded into existing rows:** 6
**Items excluded:** 0

OpenSecrets 2022 uses 4 high-level scored areas (each on a 5-point scale), heavily overlapping with PRI/FOCAL/CPI. One genuine NEW concept: separate-vs-combined lobbyist/client registration architecture.

| Item | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| os_lobbyist_client_separate | Separate registration filings for lobbyist and client (vs combined) | NEW | `REG_SEPARATE_LOBBYIST_CLIENT_FILINGS` (new) | Filing-architecture concept absent from compendium. |
| os_compensation | Compensation disclosure (full / partial / none) | EXISTS | `RPT_LOBBYIST_COMPENSATION` (E2f_i) + `RPT_PRINCIPAL_COMPENSATION` (E1f_i) + `FIN_INCOME_PER_CLIENT` (FOCAL 7.2) | Multi-tier ordinal; maps to existing rows. |
| os_timely_disclosure | Monthly during session + quarterly otherwise as baseline | EXISTS | `(FREQ_LOBBYIST_MONTHLY \| FREQ_LOBBYIST_QUARTERLY) & (FREQ_PRINCIPAL_MONTHLY \| FREQ_PRINCIPAL_QUARTERLY)` | Maps to frequency rows. |
| os_public_search | User-friendly search feature | EXISTS | `ACC_MULTI_CRITERIA_SORT` (PRI Q8) + accessibility search rows | Accessibility-side. |
| os_public_lists | Easily accessible lobbyist/client lists | EXISTS | `ACC_DEDICATED_WEBSITE` (Q2) + `ACC_DATA_AVAILABLE_AT_ALL` (Q1) | Accessibility-side. |
| os_public_download | Downloadable data | EXISTS | `ACC_DOWNLOAD_ANALYSIS_READY` (PRI Q6) | Direct match. |
| os_targeted_legislation_gap | Disclosure of targeted legislation (gap noted in OpenSecrets conclusion) | EXISTS | `RPT_PRINCIPAL_BILL_SPECIFIC` + `RPT_LOBBYIST_BILL_SPECIFIC` | Already covered; OpenSecrets flags it as a gap most states don't address. |

---

## New compendium rows (cumulative across all rubrics)

22 unique new rows added. IDs and prefixes follow the existing convention.

| New row id | Domain | Data type | Source rubric(s) | Notes-flagged? |
|---|---|---|---|---|
| `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` | registration | boolean | Newmark 2017 def_admin_agency, Newmark 2005 def_admin_agency, Opheim 1991 def_admin_agency, CPI Hired Guns Q1 | yes |
| `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` | registration | boolean | Newmark 2017 def_elected_officials, Newmark 2005, Opheim 1991 | yes |
| `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` | registration | boolean | Newmark 2017 def_public_employees, Newmark 2005, Opheim 1991 | yes |
| `DEF_COMPENSATION_STANDARD` | registration | boolean | Newmark 2017 def_compensation_standard, Newmark 2005, Opheim 1991, CPI Hired Guns Q2 | yes |
| `REG_PRE_LOBBYING_REGISTRATION_WINDOW` | registration | numeric | CPI Hired Guns Q4 | no |
| `REG_BILL_SUBJECT_ON_REGISTRATION` | registration | categorical | CPI Hired Guns Q5 | no |
| `REG_REGISTRATION_RENEWAL_FREQUENCY` | registration | categorical | CPI Hired Guns Q6 | no |
| `REG_CHANGE_NOTIFICATION_WINDOW` | registration | numeric | CPI Hired Guns Q7 | no |
| `REG_PHOTO_REQUIRED` | registration | boolean | CPI Hired Guns Q8 | no |
| `RPT_ITEMIZED_PRINCIPAL_BENEFITED` | reporting | boolean | CPI Hired Guns Q16 | no |
| `RPT_ITEMIZED_RECIPIENT` | reporting | boolean | CPI Hired Guns Q17 | no |
| `RPT_ITEMIZED_DATE` | reporting | boolean | CPI Hired Guns Q18 | no |
| `RPT_ITEMIZED_DESCRIPTION` | reporting | boolean | CPI Hired Guns Q19 | no |
| `RPT_HOUSEHOLD_OF_OFFICIAL_SPENDING` | reporting | boolean | CPI Hired Guns Q21 | no |
| `RPT_ZERO_ACTIVITY_FILING` | reporting | boolean | CPI Hired Guns Q25 | no |
| `ACC_COPIES_COST` | accessibility | numeric | CPI Hired Guns Q33 | no |
| `ACC_SAMPLE_FORMS_ONLINE` | accessibility | boolean | CPI Hired Guns Q34 | no |
| `ACC_AGGREGATE_TOTALS_BY_YEAR` | accessibility | boolean | CPI Hired Guns Q35 | no |
| `ACC_AGGREGATE_TOTALS_BY_DEADLINE` | accessibility | boolean | CPI Hired Guns Q36 | no |
| `ACC_AGGREGATE_TOTALS_BY_INDUSTRY` | accessibility | boolean | CPI Hired Guns Q37 | no |
| `REG_SEPARATE_LOBBYIST_CLIENT_FILINGS` | registration | boolean | OpenSecrets 2022 | no |
| `RPT_OTHER_INFLUENCE_PEDDLING_DISCLOSURE` | reporting | free_text | Opheim 1991 (catch-all) | borderline — see Decision Log |

> **Note on `RPT_OTHER_INFLUENCE_PEDDLING_DISCLOSURE`:** Opheim's catch-all "other activities that might constitute influence peddling or conflict of interest" is too vague to commit to a single row. **Decision-log call:** fold into `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` (E1j) by adding the framework_reference there; do NOT add a new row. Net new rows = **21**, not 22. Reflected in CSV diff below.

---

## Excluded items log (cumulative across all rubrics)

41 items excluded. Categorized by reason.

### Prohibitions (no filing carries this as data) — 12 items
- Newmark 2017: prohib_contribs_anytime, prohib_contribs_session, prohib_solicitation, prohib_contingent_comp, prohib_revolving_door (5)
- Newmark 2005: prohib_contribs_anytime, prohib_contribs_session, prohib_expenditures_over_cap, prohib_solicitation (4)
- CPI Hired Guns: Q23 limit/prohibition halves, Q24 prohibition half, Q48 cooling-off (3 sub-items)

### Penalties (statutory schedule, not filing data) — 4 items
- CPI Hired Guns: Q41, Q42, Q44, Q45

### Enforcement (agency authority/action, not filing data) — 12 items
- Opheim 1991: enforce_review_thoroughness, enforce_subpoena_witnesses, enforce_subpoena_records, enforce_admin_hearings, enforce_admin_fines, enforce_admin_penalties, enforce_court_actions (7)
- CPI Hired Guns: Q39, Q40, Q43, Q46, Q47 (5)

### Revolving-door restrictions (statutory rule, not disclosure) — 2 items
- Newmark 2017: prohib_revolving_door (already counted under Prohibitions)
- CPI Hired Guns: Q48 (already counted)

> The revolving-door cooling-off restriction is excluded; the FOCAL 2024 row `REVOLVING_COOLING_OFF_DATABASE` (FOCAL 5.2) remains in the compendium because it represents a **database of officials subject to lobbying bans** (a published/disclosed dataset), distinct from the underlying restriction.

### Deferred (accessibility scope creep) — 1 item
- CPI Hired Guns Q30 (training for electronic filing) — accessibility-side; deferred to a follow-up audit dedicated to portal/accessibility rubric expansion.

---

## Rubrics deliberately not walked

Per `plans/20260430_compendium_expansion_v2.md`:

- **F Minus** — methodology not in repo; only mentioned in `docs/LANDSCAPE.md`. Add via `add-paper` skill if/when published methodology surfaces.
- **Common Cause / League of Women Voters / state-level reform-org ratings** — not in repo; methodology heterogeneous. Add later if requested.
- **GAO 2025** (`papers/GAO_2025__lda_compliance_audit.pdf`) — federal LDA compliance audit, not a state-disclosure rubric.
- **Lacy-Nichols 2025** (`papers/Lacy_Nichols_2025__lobbying_in_the_shadows.pdf`) — application of FOCAL 2024 to 28 countries; no new indicators.
- **LobbyView / Bacik 2025 / Kim 2018, 2025 / LaPira & Thomas 2020** — federal infrastructure papers; not state rubrics.
- **Ornstein 2025 / Enamorado 2019 / Libgober 2024** — entity-resolution methodology; not rubrics.

---

## Coverage matrix (compendium row × rubric)

Generated programmatically from `framework_dedup_map.csv` post-audit. Rows: 140 compendium items. Columns: PRI 2010 disclosure / PRI 2010 accessibility / FOCAL 2024 / Sunlight 2015 / Newmark 2017 / Newmark 2005 / Opheim 1991 / CPI Hired Guns 2007 / OpenSecrets 2022.

> **Status:** matrix not generated in this audit pass (deferred to a small follow-up — generate via `pandas` from the dedup-map). Output should land at `compendium/coverage_matrix.csv` and be regenerated whenever the dedup-map changes. Add a test that asserts every compendium row has at least one framework_reference and every dedup-map source_item maps to a row that exists.

---

## Decision Log

The anti-loop record. Each entry: decision made, why, and the alternative considered. Read this before re-litigating any of these calls.

### D1. `domain="definitions"` not added; folded into `domain="registration"` with notes flag

- **Decision:** All "definition-trigger" criteria from Newmark/Opheim (def_legislative_lobbying, def_admin_agency_lobbying, def_elected_officials_as_lobbyists, def_public_employees_as_lobbyists, def_compensation_standard, def_expenditure_standard, def_time_standard) are stored under `domain="registration"` with a `notes` field flag: `"definition-trigger criterion (review for v1.2 domain='definitions' promotion)"`.
- **Rationale:** `CompendiumItem.domain` is a fixed `Literal[...]`; adding `"definitions"` requires a v1.2 schema bump that the v2 plan explicitly out-of-scopes. User direction (this session) was Option A.
- **Alternatives considered:** (B) tag definition-trigger items OUT_OF_SCOPE pending v1.2 — rejected because real legal-content gap. (C) inline schema bump — rejected because plan explicitly out-of-scopes schema work.
- **End-of-audit review:** All notes-flagged rows listed in the **Notes-flagged rows for end-of-audit review** section below. User to decide v1.2 promotion.

### D2. Newmark def_legislative_lobbying folded into REG_LOBBYIST (not a NEW row)

- **Decision:** Newmark/Opheim's "legislative lobbying triggers registration" definition criterion folds into `REG_LOBBYIST` rather than creating a new row.
- **Rationale:** All 50 states require registration when lobbying the legislature; the criterion is universal-yes and adds no signal beyond REG_LOBBYIST. Notes-flagged for end-of-audit review.
- **Alternative considered:** NEW row `DEF_LEGISLATIVE_LOBBYING_TRIGGER` — rejected because no variance across states and PRI A1 already captures the downstream fact.

### D3. Newmark def_compensation_standard is a separate row from PRI D1 (not a MERGE)

- **Decision:** Newmark/Opheim's "compensation standard" creates a NEW row `DEF_COMPENSATION_STANDARD` rather than merging into `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (D1_present).
- **Rationale:** PRI D1 is **expenditure-side** ("if expenses are less than $X, exempt"). Newmark's compensation standard is **income-side** ("if compensated > $X, you ARE a lobbyist"). Two distinct statutory mechanisms; merging would force every state to populate both rows identically and obscure the distinction.
- **Alternative considered:** MERGE both into D1_present — rejected because conflates two different threshold concepts that filings encode differently.

### D4. Itemized-expenditure metadata (CPI Q16-Q19) split into 4 separate rows

- **Decision:** Created `RPT_ITEMIZED_PRINCIPAL_BENEFITED`, `RPT_ITEMIZED_RECIPIENT`, `RPT_ITEMIZED_DATE`, `RPT_ITEMIZED_DESCRIPTION` as 4 separate compendium rows.
- **Rationale:** Each is a distinct yes/no field on the itemized expenditure record in a state's filing schema. States vary independently on each (e.g., one might require date but not description). Filing-shape distinct.
- **Alternative considered:** One compound row `RPT_ITEMIZATION_METADATA` with sub-fields. Rejected because compound rows are harder to MERGE-map for downstream rubrics that ask about only one sub-field.

### D5. Aggregate-totals publications (CPI Q35-Q37) classified as accessibility, not reporting

- **Decision:** `ACC_AGGREGATE_TOTALS_BY_YEAR/DEADLINE/INDUSTRY` placed in `domain="accessibility"`.
- **Rationale:** These are **agency-published** aggregations, not lobbyist-filed disclosure data. They sit in the accessibility/portal layer (analogous to PRI Q5 historical-data-available).
- **Alternative considered:** `domain="reporting"` — rejected because no filing carries an "aggregate spending by industry" field; this is a derived publication.

### D6. Opheim catch-all "other influence peddling" folded into RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS (no new row)

- **Decision:** Opheim's "other activities that might constitute influence peddling or conflict of interest" is too vague to commit to a new compendium row. Add as framework_reference to `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` (E1j) — the closest existing concept.
- **Rationale:** Without a concrete filing field shape, a NEW row would be a placeholder that downstream agents can't reliably populate. Folding into the closest sibling preserves the rubric reference without inflating the row count with un-curatable content.
- **Alternative considered:** NEW row `RPT_OTHER_INFLUENCE_PEDDLING_DISCLOSURE` — rejected as un-curatable. Net new rows from this audit = **21**, not 22.

### D7. CPI Q23/Q24 split into PARTIAL dispositions (disclosure half EXISTS, prohibition half OUT_OF_SCOPE)

- **Decision:** CPI's gift / campaign-contribution scoring conflates disclosure ("reported") with restriction ("limited", "prohibited"). The disclosure half maps to existing OTHER_COSTS / FIN_CAMPAIGN_CONTRIBUTIONS rows; the restriction halves are excluded.
- **Rationale:** Disclosure-only scoping. The score's prohibition tier is a statutory rule, not a filing field.
- **Alternative considered:** Treat the entire CPI item as OUT_OF_SCOPE. Rejected because the disclosure half is real disclosure data and walking-away from the framework_reference loses CPI traceability.

### D8. CPI Q47 (publish list of delinquent filers) is OUT_OF_SCOPE — borderline

- **Decision:** Excluded as enforcement-publication.
- **Borderline note:** A delinquent-filer list IS a published artifact and could be argued as accessibility-side data. Not added now because (a) it's compliance signal, not disclosure data; (b) no downstream consumer has asked for it. **Reconsider if a downstream consumer wants delinquent-filer signal as a filtering input.**

### D9. Threshold rows renamed to rubric-neutral framing

- **Decision (post-audit, in-session):** Renamed 5 rows to remove PRI-vocabulary privilege:
  - `THRESHOLD_MATERIALITY` → `THRESHOLD_LOBBYING_MATERIALITY_GATE`
  - `THRESHOLD_FINANCIAL_PRESENT` → `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT`
  - `THRESHOLD_FINANCIAL_VALUE` → `THRESHOLD_LOBBYING_EXPENDITURE_VALUE`
  - `THRESHOLD_TIME_PRESENT` → `THRESHOLD_LOBBYING_TIME_PRESENT`
  - `THRESHOLD_TIME_VALUE` → `THRESHOLD_LOBBYING_TIME_VALUE`
- **Rationale:** The original names mirrored PRI's exemption framing ("de-minimis threshold for exemption") even though Newmark/Opheim/CPI frame the same statutory mechanism as inclusion-side ("compensation/expenditure/time standard for being defined as a lobbyist"). PRI was the curation-order spine for the v1 compendium, so its vocabulary became the row-name default. The harness must extract these facts neutrally — neither PRI nor Newmark/Opheim's framing is canonical. Row-level descriptions now give both framings equal treatment.
- **What stayed the same:** PRI item_text inside `framework_references_json` is preserved verbatim (rubric's own wording is data). Row IDs in `framework_dedup_map.csv` and the audit doc were updated. Domain stays `registration` — exemption-framed thresholds belong there. The 4 new `DEF_*` rows from Newmark/Opheim (inclusion-framed) sit alongside as separate rows.
- **Migration script:** `scripts/build_compendium.py` lines 134-140 also updated so a re-run produces the same neutral names.
- **Alternative considered:** Rename the entire compendium to rubric-neutral IDs (e.g., `REG_LOBBYIST` → `WHO_LOBBYIST_REGISTRATION_REQUIRED`). Rejected as too much churn for too little harness payoff; defer to a hypothetical future curation pass.

### D11. v1.2 schema bump: `domain="definitions"` added (2026-05-01)

- **Decision (post-audit, in-session):** Landed v1.2 schema bump per `plans/20260501_data_model_v1_2_definitions_domain.md`.
  - Added `"definitions"` to `CompendiumDomain` Literal in `src/lobby_analysis/models/compendium.py`.
  - Migrated 5 rows from `domain="registration"` to `domain="definitions"`: `THRESHOLD_LOBBYING_MATERIALITY_GATE` (PRI D0 umbrella), `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`, `DEF_ELECTED_OFFICIAL_AS_LOBBYIST`, `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST`, `DEF_COMPENSATION_STANDARD`.
  - **Symmetry-gap fix:** added 2 NEW rows in `domain="definitions"` (inclusion-framed parallels of `DEF_COMPENSATION_STANDARD`):
    - `DEF_EXPENDITURE_STANDARD` — "spend > $X on lobbying = you ARE a lobbyist" (Newmark/Opheim def_expenditure_standard re-targeted here).
    - `DEF_TIME_STANDARD` — "spend > X% of compensated time = you ARE a lobbyist" (Newmark/Opheim def_time_standard re-targeted here).
  - **Curation-gap fix:** added Newmark 2017/2005, Opheim 1991, CPI Hired Guns framework_references to `THRESHOLD_LOBBYING_MATERIALITY_GATE` (D0). Each Newmark/Opheim "standard" implies a materiality test; D0 was missing those cross-refs in the v2 audit.
  - Dropped the `definition-trigger criterion` notes flag from all 7 previously-flagged rows. The 3 stay-in-registration rows (`REG_LOBBYIST`, `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT`, `THRESHOLD_LOBBYING_TIME_PRESENT`) keep their domain; their flag is gone.
  - Re-targeted dedup-map entries: Newmark/Opheim `def_expenditure_standard` and `def_time_standard` flip from `EXISTS` (folded into PRI D1/D2 exemption-framed rows) to `NEW` (their own inclusion-framed rows). CPI Q2 expenditure-portion expression expanded to also reference `DEF_EXPENDITURE_STANDARD`.
- **Conceptual line established:** `domain="definitions"` = statutory criteria for whether a person *is* a lobbyist (predicate on the agent). `domain="registration"` = filing requirements once a person is a lobbyist (gates, exemption thresholds, registration-form contents). Test for borderline future rows: "Does this answer 'who is a lobbyist?' or 'what does a lobbyist file?'"
- **OpenSecrets's `REG_SEPARATE_LOBBYIST_CLIENT_FILINGS` stays in `registration`** under this rule — it's a filing-architecture feature, not a definitional criterion.
- **Compendium row count:** 139 → **141** (+2 from v1.2 symmetry-gap rows). Statute-side total: **108** (up from 106; the 2 new rows are statute-side). Domain breakdown post-v1.2: 7 `definitions`, 31 `registration` (was 36; 5 promoted to definitions), 47 `reporting`, 33 `accessibility`, plus smaller domains.
- **Tests added (TDD):** 7 new tests in `test_compendium_loader.py` enforcing the v1.2 invariants (loader accepts `definitions`, expected row IDs are present with the right domain, no rows still carry the v1.1 notes flag, every `definitions` row has a definitional framework_reference, D0 has Newmark/Opheim cross-refs, the 2 symmetry rows exist with correct dedup-map re-targeting). 24/24 compendium tests pass.
- **Disambiguation rule for inclusion- vs exemption-framed thresholds (review addendum, 2026-05-01).** The `DEF_*_STANDARD` / `THRESHOLD_LOBBYING_*_PRESENT` row pairs initially carried overlapping descriptions: each THRESHOLD_* row claimed to capture "both inclusion- and exemption-framed framings," while each DEF_*_STANDARD row described itself as "the inclusion-framed parallel," giving the harness no rule for which row a given statute populates. Resolved by tightening descriptions: THRESHOLD_LOBBYING_EXPENDITURE_PRESENT and THRESHOLD_LOBBYING_TIME_PRESENT are now exemption-framed only; DEF_EXPENDITURE_STANDARD and DEF_TIME_STANDARD are inclusion-framed only; each row's description points to its counterpart. **Both rows in a pair populate when a state combines an inclusion trigger on one axis with an exemption carve-out on another** (e.g., "primary time on lobbying, unless expenses < $1,000" → DEF_TIME_STANDARD=true AND THRESHOLD_LOBBYING_EXPENDITURE_PRESENT=true). Same-axis statutes ("if you spend > $X you ARE a lobbyist" only) populate just the DEF_*_STANDARD row; same-axis exemption-only statutes populate just the THRESHOLD_*_PRESENT row.

### D10. CPI Q30 (electronic-filing training) deferred, not folded

- **Decision:** Not added in this audit. Deferred to a future accessibility-rubric audit.
- **Rationale:** Training is a portal-side feature with no current compendium analog. Adding a one-off row for a single CPI question is premature; it's a candidate for a coordinated accessibility-side audit.

---

## Notes-flagged rows for end-of-audit review — RESOLVED 2026-05-01 (v1.2 landed)

End-of-audit review (2026-05-01) resolved all 7 notes-flagged rows per Decision Log D11 (v1.2 schema bump). Final dispositions:

| Row id | Final domain | Action taken |
|---|---|---|
| `REG_LOBBYIST` | registration | Flag dropped. The flag was defensive; on review it doesn't capture a definition (universal-yes, no signal beyond "registration regime exists"). |
| `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` | registration | Flag dropped. Stays in registration — exemption-framed, properly a registration gate. Newmark/Opheim's def_expenditure_standard re-targeted to the new `DEF_EXPENDITURE_STANDARD` row (inclusion-framed). |
| `THRESHOLD_LOBBYING_TIME_PRESENT` | registration | Flag dropped. Stays in registration — exemption-framed. Newmark/Opheim's def_time_standard re-targeted to the new `DEF_TIME_STANDARD` row. |
| `THRESHOLD_LOBBYING_MATERIALITY_GATE` | **definitions** | Promoted. Qualitative-materiality umbrella; gained Newmark/Opheim/CPI cross-refs (curation-gap fix). |
| `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` | **definitions** | Promoted. |
| `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` | **definitions** | Promoted. |
| `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` | **definitions** | Promoted. |
| `DEF_COMPENSATION_STANDARD` | **definitions** | Promoted. |
| `DEF_EXPENDITURE_STANDARD` (new) | **definitions** | Symmetry-gap fix added in v1.2 — inclusion-framed parallel of DEF_COMPENSATION_STANDARD. |
| `DEF_TIME_STANDARD` (new) | **definitions** | Symmetry-gap fix added in v1.2 — inclusion-framed parallel. |

Total: 7 rows now in `domain="definitions"` (5 migrated + 2 new). Conceptual line: `definitions` = "who is a lobbyist?" (predicate on the agent); `registration` = "what does a lobbyist file?" (filing requirements, including exemption-framed gates).

---

## Lifecycle

- **Born:** 2026-04-30 on branch `filing-schema-extraction` at `docs/active/filing-schema-extraction/results/20260430_compendium_audit.md`.
- **On merge to main:** moves to repo-level `docs/COMPENDIUM_AUDIT.md` so it surfaces in pre-flight reads (every session, not buried in branch history).
- **Update cadence:** whenever the compendium changes (new rubric walked, new row added, dedup decision revised). Bump the `Compendium version` line at top.

---

## Out of scope (deliberate, this audit)

- Schema changes (data-model-v1.2). Definition-domain promotion deferred to a separate v1.2 plan if user approves the notes-flagged rows.
- Filing-schema extraction harness design (kickoff plan; this audit is upstream of it).
- State-by-state SMR population.
- Adding F Minus / Common Cause / OpenSecrets-state-pages methodology.
- Re-walking PRI 2010 / FOCAL 2024 / Sunlight 2015 — their dedup decisions stand.
- Generating `compendium/coverage_matrix.csv` programmatically — deferred (small follow-up task).
- Verifying dedup-map source-frame counts against rubric-paper item counts — deferred (small test addition).

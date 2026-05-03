# Compendium Audit v3 — Phase 0 Reconciliation Note

**Branch:** statute-extraction  
**Sweep date:** 2026-05-02  
**Run 1 inputs:** `20260502_compendium_audit_concerns_run1.md` + `.csv`  
**Run 2 inputs:** `20260502_compendium_audit_concerns_run2.md` + `.csv`  
**Reconciler:** reconciler subagent (mechanical diff of run 1 + run 2)  
**Compendium snapshot:** `disclosure_items.csv` sha `ef31b3ba96cde2f9f426172ee7f446a32c13ce2d`, `framework_dedup_map.csv` sha `5e0df8ea2ebdd3593098f0c1129bf93e5128659d`, worktree HEAD `8598b3fb`  

## Overall agreement rate

Across 141 compendium rows, run 1 produced **100** active concerns, run 2 produced **132** active concerns (excluding 17 entries run 2 considered then retracted during its sweep — those are kept in run 2's audit trail but excluded from this reconciliation per the spec). The strict-agreement numerator (concerns where both runs flagged the same `(row_id, criterion, tag)` triple) is **45**; the union denominator is **186**. **Overall two-run agreement rate is 24.2%** (45/186). The canonical concerns doc accumulates **186 canonical entries** (45 both-runs / 18 tag-disagree rows arising from 9 disputed (row_id, criterion) keys / 46 run1-only / 77 run2-only).

**Plan threshold check:** the plan flagged `< ~60%` two-run agreement as a surprising result indicating tag boundaries are too fuzzy and Phase 1 should lead with taxonomy refinement. The observed rate of **24.2%** is below this threshold; DO surface this as a Phase 1 input.

### Per-tag agreement breakdown (canonical)

| tag | canonical total | both | tag-disagree | run1-only | run2-only |
|---|---|---|---|---|---|
| axis-ambiguous-name | 25 | 7 | 5 | 7 | 6 |
| name-misleading | 7 | 0 | 5 | 0 | 2 |
| description-broader-than-rubric | 12 | 2 | 3 | 1 | 6 |
| description-narrower-than-rubric | 50 | 16 | 3 | 16 | 15 |
| description-misscoped | 6 | 0 | 1 | 1 | 4 |
| rubric-source-ambiguous | 2 | 0 | 1 | 1 | 0 |
| cluster-asks-two-questions | 28 | 8 | 0 | 14 | 6 |
| cross-row-overlap | 39 | 7 | 0 | 4 | 28 |
| wrong-domain | 13 | 5 | 0 | 0 | 8 |
| other-issue | 4 | 0 | 0 | 2 | 2 |

Two-run agreement (`both`) accounts for 24% of canonical entries; one-run flags (46 run1-only + 77 run2-only = 123 total) account for 66%; tag-disagreements account for the remaining 10%. Read: when both runs noticed the same `(row_id, criterion)` issue they almost always agreed on the tag (very few tag-disagreements). The dominant source of canonical-entry growth over either single run is one-run-only flags.

## Disagreement table

Every (row_id, criterion) pair where the two runs differed (different tag set OR one flagged and the other didn't). Sorted by row_id then criterion. **132 disagreement entries.**

| row_id | criterion | run1_tag | run2_tag | canonical_resolution | note |
|---|---|---|---|---|---|
| (multiple) | C2 | (none) | other-issue | carry-forward: tags=other-issue; agreement=run2-only |  |
| ACC_AGGREGATE_TOTALS_BY_DEADLINE | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| ACC_AGGREGATE_TOTALS_BY_DEADLINE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| ACC_COPIES_COST | C2 | (none) | description-misscoped | carry-forward: tags=description-misscoped; agreement=run2-only |  |
| ACC_CURRENT_YEAR_DATA | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| ACC_DATA_AVAILABLE_AT_ALL | C2 | description-misscoped | (none) | carry-forward: tags=description-misscoped; agreement=run1-only |  |
| ACC_DATA_AVAILABLE_AT_ALL | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| ACC_DEDICATED_WEBSITE | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| ACC_DIARIES_ONLINE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| ACC_HISTORICAL_DATA | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| ACC_LINKED_DATA | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| ACC_MULTI_CRITERIA_SORT | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| ACC_MULTI_CRITERIA_SORT | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| ACC_MULTI_CRITERIA_SORT | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_REGISTRY_UPDATE_FRESHNESS | C2 | (none) | description-misscoped | carry-forward: tags=description-misscoped; agreement=run2-only |  |
| ACC_REGISTRY_UPDATE_FRESHNESS | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| ACC_REGISTRY_UPDATE_FRESHNESS | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_DATE | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_LEGAL_STATUS | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_LOBBYIST_NAME | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_PRINCIPAL_LOCATION | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_SECTOR | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_SORT_BY_TOTAL_EXPENDITURES | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| ACC_UNIQUE_IDENTIFIERS | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| ACC_WEBSITE_FINDABILITY | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| CONTACT_BENEFICIARY | C1 | (none) | name-misleading | carry-forward: tags=name-misleading; agreement=run2-only |  |
| CONTACT_INSTITUTION | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| CONTACT_LEGISLATIVE_REFERENCES | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| CONTACT_MEETING_ATTENDEES | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| CONTACT_OUTCOMES_SOUGHT | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C2 | rubric-source-ambiguous | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric,rubric-source-ambiguous; agreement=tag-disagree |  |
| DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| DEF_COMPENSATION_STANDARD | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| DEF_ELECTED_OFFICIAL_AS_LOBBYIST | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| DEF_EXPENDITURE_STANDARD | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| DEF_PUBLIC_ENTITY | C1 | axis-ambiguous-name | name-misleading | carry-forward: tags=axis-ambiguous-name,name-misleading; agreement=tag-disagree |  |
| DEF_PUBLIC_ENTITY | C2 | (none) | other-issue | carry-forward: tags=other-issue; agreement=run2-only |  |
| DEF_PUBLIC_ENTITY_CHARTER | C1 | axis-ambiguous-name | name-misleading | carry-forward: tags=axis-ambiguous-name,name-misleading; agreement=tag-disagree |  |
| DEF_PUBLIC_ENTITY_OWNERSHIP | C1 | axis-ambiguous-name | name-misleading | carry-forward: tags=axis-ambiguous-name,name-misleading; agreement=tag-disagree |  |
| DEF_PUBLIC_ENTITY_STRUCTURE | C1 | axis-ambiguous-name | name-misleading | carry-forward: tags=axis-ambiguous-name,name-misleading; agreement=tag-disagree |  |
| DEF_TIME_STANDARD | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| EXEMPT_GOVT_OFFICIAL_CAPACITY | C1 | axis-ambiguous-name | name-misleading | carry-forward: tags=axis-ambiguous-name,name-misleading; agreement=tag-disagree |  |
| EXEMPT_GOVT_OFFICIAL_CAPACITY | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| FIN_EXPENDITURE_PER_ISSUE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| FIN_TIME_SPENT_LOBBYING | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| FIN_TRADE_ASSOCIATION_DUES | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| FREQ_LOBBYIST_ANNUAL | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_LOBBYIST_MONTHLY | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_LOBBYIST_MONTHLY | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_LOBBYIST_OTHER | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_LOBBYIST_QUARTERLY | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_LOBBYIST_QUARTERLY | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_LOBBYIST_SEMI_ANNUAL | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_LOBBYIST_SEMI_ANNUAL | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_LOBBYIST_TRI_ANNUAL | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_PRINCIPAL_ANNUAL | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_PRINCIPAL_MONTHLY | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_PRINCIPAL_MONTHLY | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_PRINCIPAL_OTHER | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_PRINCIPAL_QUARTERLY | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| FREQ_PRINCIPAL_QUARTERLY | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| FREQ_PRINCIPAL_SEMI_ANNUAL | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| PARITY_GOVT_AS_LOBBYIST | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only | run 2 considered then retracted: retracted; carry to C4 cluster |
| PARITY_GOVT_AS_LOBBYIST | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| PARITY_GOVT_AS_PRINCIPAL | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| PARITY_GOVT_AS_PRINCIPAL | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_EXECUTIVE_AGENCY | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| REG_EXECUTIVE_AGENCY | C4 | cross-row-overlap | (none) | carry-forward: tags=cross-row-overlap; agreement=run1-only |  |
| REG_GOVERNORS_OFFICE | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_GOVT_LOBBYING_GOVT | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| REG_GOVT_LOBBYING_GOVT | C4 | cross-row-overlap | (none) | carry-forward: tags=cross-row-overlap; agreement=run1-only |  |
| REG_LOBBYING_ACTIVITY_FORMS_SCOPE | C1 | axis-ambiguous-name | (none) | carry-forward: tags=axis-ambiguous-name; agreement=run1-only |  |
| REG_LOBBYING_ACTIVITY_FORMS_SCOPE | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| REG_LOBBYIST | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| REG_LOBBYIST | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_PRE_LOBBYING_REGISTRATION_WINDOW | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_PRINCIPAL | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_REGISTRATION_RENEWAL_FREQUENCY | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REG_SEPARATE_LOBBYIST_CLIENT_FILINGS | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| REL_BOARD_SEATS | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| RPT_EXPENDITURE_FORMAT_GRANULARITY | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_EXPENDITURE_ITEMIZATION_THRESHOLD | C2 | (none) | description-misscoped | carry-forward: tags=description-misscoped; agreement=run2-only |  |
| RPT_HOUSEHOLD_OF_OFFICIAL_SPENDING | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_ITEMIZED_RECIPIENT | C2 | (none) | description-misscoped | carry-forward: tags=description-misscoped; agreement=run2-only |  |
| RPT_LOBBYIST_BILL_SPECIFIC | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_LOBBYIST_CONTRACT_TYPE | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| RPT_LOBBYIST_CONTRACT_TYPE | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| RPT_LOBBYIST_GATE | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| RPT_LOBBYIST_ISSUE_GENERAL | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_LOBBYIST_ITEMIZED | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_LOBBYIST_NON_COMPENSATION | C2 | description-broader-than-rubric | description-narrower-than-rubric | carry-forward: tags=description-broader-than-rubric,description-narrower-than-rubric; agreement=tag-disagree |  |
| RPT_LOBBYIST_OTHER_COSTS | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| RPT_LOBBYIST_OTHER_COSTS | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_LOBBYIST_PRINCIPAL_CONTACT | other-issue | other-issue | (none) | carry-forward: tags=other-issue; agreement=run1-only |  |
| RPT_LOBBYIST_PRINCIPAL_NAMES | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| RPT_LOBBYIST_PRINCIPAL_NAMES | C4 | cross-row-overlap | (none) | carry-forward: tags=cross-row-overlap; agreement=run1-only |  |
| RPT_LOBBYIST_PRINCIPAL_NATURE | C2 | rubric-source-ambiguous | (none) | carry-forward: tags=rubric-source-ambiguous; agreement=run1-only |  |
| RPT_LOBBYIST_PRINCIPAL_NATURE | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_OFFICIAL_DIARY_DISCLOSURE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| RPT_ORG_REGISTRATION_NUMBER | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| RPT_POSITION_TAKEN | C2 | description-broader-than-rubric | (none) | carry-forward: tags=description-broader-than-rubric; agreement=run1-only |  |
| RPT_POSITION_TAKEN | C4 | cross-row-overlap | (none) | carry-forward: tags=cross-row-overlap; agreement=run1-only |  |
| RPT_POSITION_TAKEN | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| RPT_PRINCIPAL_BILL_SPECIFIC | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_PRINCIPAL_BUSINESS_NATURE | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | C2 | description-misscoped | description-narrower-than-rubric | carry-forward: tags=description-misscoped,description-narrower-than-rubric; agreement=tag-disagree |  |
| RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | other-issue | other-issue | (none) | carry-forward: tags=other-issue; agreement=run1-only |  |
| RPT_PRINCIPAL_GATE | C1 | (none) | name-misleading | carry-forward: tags=name-misleading; agreement=run2-only |  |
| RPT_PRINCIPAL_GATE | C2 | description-narrower-than-rubric | (none) | carry-forward: tags=description-narrower-than-rubric; agreement=run1-only |  |
| RPT_PRINCIPAL_ISSUE_GENERAL | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_PRINCIPAL_ITEMIZED | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| RPT_PRINCIPAL_LOBBYIST_NAMES | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| RPT_PRINCIPAL_NON_COMPENSATION | C2 | description-broader-than-rubric | description-narrower-than-rubric | carry-forward: tags=description-broader-than-rubric,description-narrower-than-rubric; agreement=tag-disagree |  |
| RPT_PRINCIPAL_OTHER_COSTS | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| RPT_PRINCIPAL_OTHER_COSTS | C3 | cluster-asks-two-questions | (none) | carry-forward: tags=cluster-asks-two-questions; agreement=run1-only |  |
| RPT_SECTOR_DISCLOSED | C4 | (none) | cross-row-overlap | carry-forward: tags=cross-row-overlap; agreement=run2-only |  |
| THRESHOLD_LOBBYING_EXPENDITURE_PRESENT | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| THRESHOLD_LOBBYING_EXPENDITURE_PRESENT | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| THRESHOLD_LOBBYING_EXPENDITURE_VALUE | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| THRESHOLD_LOBBYING_EXPENDITURE_VALUE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| THRESHOLD_LOBBYING_EXPENDITURE_VALUE | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| THRESHOLD_LOBBYING_MATERIALITY_GATE | C2 | (none) | description-broader-than-rubric | carry-forward: tags=description-broader-than-rubric; agreement=run2-only |  |
| THRESHOLD_LOBBYING_MATERIALITY_GATE | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| THRESHOLD_LOBBYING_TIME_PRESENT | C3 | (none) | cluster-asks-two-questions | carry-forward: tags=cluster-asks-two-questions; agreement=run2-only |  |
| THRESHOLD_LOBBYING_TIME_PRESENT | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |
| THRESHOLD_LOBBYING_TIME_VALUE | C1 | (none) | axis-ambiguous-name | carry-forward: tags=axis-ambiguous-name; agreement=run2-only |  |
| THRESHOLD_LOBBYING_TIME_VALUE | C2 | (none) | description-narrower-than-rubric | carry-forward: tags=description-narrower-than-rubric; agreement=run2-only |  |
| THRESHOLD_LOBBYING_TIME_VALUE | C5 | (none) | wrong-domain | carry-forward: tags=wrong-domain; agreement=run2-only |  |

## Surprising-result threshold check

Per plan §'What constitutes a surprising result' — checking which thresholds the canonical numbers crossed:

- **Concern rate < 5/141 (~3%)** — would indicate iter-1's bug was a true outlier and v3 was over-scoped. Canonical: **186/141** total concerns; **109/141** (77%) rows have ≥1 concern. **NOT triggered (rate is much higher).**
- **Concern rate > 50/141 (~35%)** — would indicate structural drift requiring aggressive triage. Canonical: **186/141** concerns, **109/141** (77%) rows flagged. **TRIGGERED.** Phase 1 plan should expect cluster-grouping rather than fix-each-row.
- **Two-run agreement rate < ~60%** — would indicate fuzzy tag boundaries; Phase 1 leads with taxonomy refinement. Canonical: **24.2%**. **TRIGGERED.** Phase 1 should lead with tag-taxonomy refinement before pattern-grouping.
- **Tag distribution heavily skewed (>80% description-fidelity tags)** — would refocus v3 strategy away from axis-in-ID toward description rewrites. Canonical: description-tags = **70/186 = 38%**. **NOT triggered at the 80% bar**, but description-tags are still the single largest category and the PRI-verbatim pattern is the single largest sub-pattern (run1+run2 both list it as the #1 pattern for Phase 1). The user-proposed `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` axis-in-ID convention applies to a smaller fraction of rows than the brainstorm assumed; description rewrites are the bigger workstream.
- **Domain skew** — concerns concentrated in 1–2 domains would simplify Phase 2 batching. Canonical: spread across registration / reporting / accessibility / definitions; revolving_door has zero. **Partially triggered** — concentration is real but more domains than 1–2 are involved.
- **Cross-row-overlap clusters of 3+ rows** — suggests deeper scope-design issue beyond per-row rename. Canonical: Yes — DEF_PUBLIC_ENTITY 4-row cluster (parent + 3 sub-rows); agency-axis triangle (DEF_ADMIN_AGENCY_LOBBYING_TRIGGER + REG_EXECUTIVE_AGENCY + REG_GOVT_LOBBYING_GOVT); diary-disclosure 2–3-row cluster; ACC_SORT_BY_MONEY 3-row cluster (Q7g/Q7h/Q7i). **TRIGGERED.**

**Net read:** the canonical sweep is in the 'broad cleanup pass, multi-batch' regime. Phase 1 should treat it as cluster-grouping with description rewrites as the dominant fix-shape, plus an explicit D11 reopen (run 2 surfaced ≥10 D11-revisit concerns).
# Cross-state CPI 2015 C11 de-jure projection-accuracy audit

**States audited:** NY, WI, OH, CA, TX (vintage 2015)
**De-jure indicators:** IND_196, IND_197, IND_199, IND_201, IND_203, IND_207
**Total comparison cells:** 30
**Total matches:** 15 / 30 (50.0%)

Per-indicator match counts (across states):

- IND_196: 5 / 5
- IND_197: 3 / 5
- IND_199: 1 / 5
- IND_201: 2 / 5
- IND_203: 4 / 5
- IND_207: 0 / 5

## Table A — Per-cell comparison (state x indicator)

| State | Indicator | Chunk | Oracle | Projected | Match | Notes |
|---|---|---|---|---|---|---|
| NY | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| NY | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| NY | IND_199 | registration_mechanics_and_exemptions | 50 | 0 | no | vocab-mismatch: extracted IntCell=24 (months) but helper expects string enum {annual, biennial, ...}; oracle=50, projected=0 |
| NY | IND_201 | lobbyist_spending_report | 100 | 100 | YES | match |
| NY | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| NY | IND_207 | enforcement_and_audits | 100 | 0 | no | vocab-mismatch: extracted EnumCell='YES' but helper expects {'regular_third_party_audit_required', 'audit_only_when_irregularities_suspected_or_compliance_review'}; oracle=100, projected=0 |
| WI | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| WI | IND_197 | registration_thresholds | 50 | 100 | no | oracle=50 projected=100; lobbyist_registration_threshold_compensation_dollars=0 |
| WI | IND_199 | registration_mechanics_and_exemptions | 50 | 0 | no | vocab-mismatch: extracted IntCell=24 (months) but helper expects string enum {annual, biennial, ...}; oracle=50, projected=0 |
| WI | IND_201 | lobbyist_spending_report | 0 | 0 | YES | match |
| WI | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| WI | IND_207 | enforcement_and_audits | 100 | 0 | no | vocab-mismatch: extracted EnumCell='MODERATE' but helper expects {'regular_third_party_audit_required', 'audit_only_when_irregularities_suspected_or_compliance_review'}; oracle=100, projected=0 |
| OH | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| OH | IND_197 | registration_thresholds | 50 | 100 | no | oracle=50 projected=100; lobbyist_registration_threshold_compensation_dollars: scor_unstable (value=0) |
| OH | IND_199 | registration_mechanics_and_exemptions | 50 | 0 | no | vocab-mismatch: extracted IntCell=24 (months) but helper expects string enum {annual, biennial, ...}; oracle=50, projected=0 |
| OH | IND_201 | lobbyist_spending_report | 50 | 0 | no | oracle=50 projected=0; lobbyist_spending_report_required: value_unstable (value=True); lobbyist_spending_report_includes_itemized_expenses: value_unstable (value=False); lobbyist_spending_report_includes_total_compensation=False |
| OH | IND_203 | principal_spending_report | 50 | 0 | no | oracle=50 projected=0; principal_spending_report_required=False; principal_spending_report_includes_compensation_paid_to_lobbyists=False |
| OH | IND_207 | enforcement_and_audits | 100 | 0 | no | vocab-mismatch: extracted EnumCell='MODERATE' but helper expects {'regular_third_party_audit_required', 'audit_only_when_irregularities_suspected_or_compliance_review'}; oracle=100, projected=0 |
| CA | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| CA | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| CA | IND_199 | registration_mechanics_and_exemptions | 50 | 0 | no | vocab-mismatch: extracted IntCell=24 (months) but helper expects string enum {annual, biennial, ...}; oracle=50, projected=0 |
| CA | IND_201 | lobbyist_spending_report | 100 | 0 | no | oracle=100 projected=0; lobbyist_spending_report_required: value_unstable (value=False); lobbyist_spending_report_includes_itemized_expenses: value_unstable (value=True); lobbyist_spending_report_includes_total_compensation: value_unstable (value=False) |
| CA | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| CA | IND_207 | enforcement_and_audits | 100 | 0 | no | vocab-mismatch: extracted EnumCell='NO' but helper expects {'regular_third_party_audit_required', 'audit_only_when_irregularities_suspected_or_compliance_review'}; oracle=100, projected=0 |
| TX | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| TX | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| TX | IND_199 | registration_mechanics_and_exemptions | 0 | 0 | YES | match |
| TX | IND_201 | lobbyist_spending_report | 50 | 100 | no | oracle=50 projected=100; lobbyist_spending_report_required=True; lobbyist_spending_report_includes_itemized_expenses=True; lobbyist_spending_report_includes_total_compensation: value_unstable (value=True) |
| TX | IND_203 | principal_spending_report | 0 | 0 | YES | match |
| TX | IND_207 | enforcement_and_audits | 50 | 0 | no | vocab-mismatch: extracted EnumCell='NO' but helper expects {'regular_third_party_audit_required', 'audit_only_when_irregularities_suspected_or_compliance_review'}; oracle=50, projected=0 |

## Table B — Per-state summary

| State | Indicators matched | Dispatches | Instantiation errors | Total cost (USD) | Per-chunk diagnosis |
|---|---|---|---|---|---|
| NY | 4 / 6 | 36 | 2 | $2.8289 | lobbying_definitions->IND_196: match; registration_thresholds->IND_197: match; registration_mechanics_and_exemptions->IND_199: 0!=50; lobbyist_spending_report->IND_201: match; principal_spending_report->IND_203: match; enforcement_and_audits->IND_207: 0!=100 |
| WI | 3 / 6 | 36 | 6 | $2.4825 | lobbying_definitions->IND_196: match; registration_thresholds->IND_197: 100!=50; registration_mechanics_and_exemptions->IND_199: 0!=50; lobbyist_spending_report->IND_201: match; principal_spending_report->IND_203: match; enforcement_and_audits->IND_207: 0!=100 |
| OH | 1 / 6 | 36 | 0 | $3.7894 | lobbying_definitions->IND_196: match; registration_thresholds->IND_197: 100!=50; registration_mechanics_and_exemptions->IND_199: 0!=50; lobbyist_spending_report->IND_201: 0!=50; principal_spending_report->IND_203: 0!=50; enforcement_and_audits->IND_207: 0!=100 |
| CA | 3 / 6 | 36 | 1 | $2.8428 | lobbying_definitions->IND_196: match; registration_thresholds->IND_197: match; registration_mechanics_and_exemptions->IND_199: 0!=50; lobbyist_spending_report->IND_201: 0!=100; principal_spending_report->IND_203: match; enforcement_and_audits->IND_207: 0!=100 |
| TX | 4 / 6 | 36 | 3 | $2.4835 | lobbying_definitions->IND_196: match; registration_thresholds->IND_197: match; registration_mechanics_and_exemptions->IND_199: match; lobbyist_spending_report->IND_201: 100!=50; principal_spending_report->IND_203: match; enforcement_and_audits->IND_207: 0!=50 |


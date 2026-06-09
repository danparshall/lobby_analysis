# Cross-arm field agreement — sonnet / mini-medium / mini-low
Comparison set: **100 filings** present in all four arms (sonnet + mini-medium + mini-low + mini-minimal).
Filings missing per arm during intersection scan:
- medium_briefv3: 205 report_ids missing

## Definitions
- **both_null:** both arms emitted null on this field. Investigate; this is NOT counted as agreement per the 2026-06-09 design call.
- **one_null:** exactly one arm emitted null. Counted as disagreement.
- **both_emitted_agree:** both arms emitted non-null AND values are exactly equal after JSON canonicalization.
- **both_emitted_disagree:** both arms emitted non-null but values differ.
- **agreement_rate:** both_emitted_agree / (both_emitted_agree + both_emitted_disagree). Denominator excludes null cells so null asymmetry shows up separately in the both_null and one_null columns.

## sonnet vs medium_briefv3

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `reporting_period_start` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `reporting_period_end` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filed_date` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `total_compensation` | 100 | 100 | 0 | 0 | 0 | — |
| `total_reimbursements` | 100 | 100 | 0 | 0 | 0 | — |
| `total_other_costs` | 100 | 95 | 5 | 0 | 0 | — |
| `total_expenditure` | 100 | 28 | 63 | 9 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 61 | 39 | 0 | 0 | — |
| `filer_person` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `positions` | 100 | 0 | 0 | 94 | 6 | 94.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 14 | 86 | 14.0% |

## sonnet vs medium_briefv2

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 94 | 6 | 94.0% |
| `reporting_period_start` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `reporting_period_end` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filed_date` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `total_compensation` | 100 | 100 | 0 | 0 | 0 | — |
| `total_reimbursements` | 100 | 100 | 0 | 0 | 0 | — |
| `total_other_costs` | 100 | 96 | 4 | 0 | 0 | — |
| `total_expenditure` | 100 | 27 | 66 | 7 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 61 | 34 | 5 | 0 | 100.0% |
| `filer_person` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `positions` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 13 | 87 | 13.0% |

## medium_briefv2 vs medium_briefv3

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 94 | 6 | 94.0% |
| `reporting_period_start` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `reporting_period_end` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filed_date` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `total_compensation` | 100 | 100 | 0 | 0 | 0 | — |
| `total_reimbursements` | 100 | 100 | 0 | 0 | 0 | — |
| `total_other_costs` | 100 | 93 | 5 | 2 | 0 | 100.0% |
| `total_expenditure` | 100 | 88 | 5 | 7 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 95 | 5 | 0 | 0 | — |
| `filer_person` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `positions` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 43 | 57 | 43.0% |


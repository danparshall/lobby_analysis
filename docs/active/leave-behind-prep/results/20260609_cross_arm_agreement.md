# Cross-arm field agreement — sonnet / mini-medium / mini-low
Comparison set: **100 filings** present in all four arms (sonnet + mini-medium + mini-low + mini-minimal).
Filings missing per arm during intersection scan:
- medium: 205 report_ids missing

## Definitions
- **both_null:** both arms emitted null on this field. Investigate; this is NOT counted as agreement per the 2026-06-09 design call.
- **one_null:** exactly one arm emitted null. Counted as disagreement.
- **both_emitted_agree:** both arms emitted non-null AND values are exactly equal after JSON canonicalization.
- **both_emitted_disagree:** both arms emitted non-null but values differ.
- **agreement_rate:** both_emitted_agree / (both_emitted_agree + both_emitted_disagree). Denominator excludes null cells so null asymmetry shows up separately in the both_null and one_null columns.

## sonnet vs medium

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 98 | 2 | 98.0% |
| `reporting_period_start` | 100 | 0 | 13 | 74 | 13 | 85.1% |
| `reporting_period_end` | 100 | 0 | 15 | 77 | 8 | 90.6% |
| `filed_date` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `total_compensation` | 100 | 99 | 1 | 0 | 0 | — |
| `total_reimbursements` | 100 | 99 | 1 | 0 | 0 | — |
| `total_other_costs` | 100 | 90 | 10 | 0 | 0 | — |
| `total_expenditure` | 100 | 28 | 58 | 14 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 59 | 36 | 5 | 0 | 100.0% |
| `filer_person` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `positions` | 100 | 0 | 0 | 95 | 5 | 95.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 30 | 70 | 30.0% |

## sonnet vs low

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `reporting_period_start` | 100 | 0 | 20 | 64 | 16 | 80.0% |
| `reporting_period_end` | 100 | 0 | 32 | 54 | 14 | 79.4% |
| `filed_date` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `total_compensation` | 100 | 100 | 0 | 0 | 0 | — |
| `total_reimbursements` | 100 | 100 | 0 | 0 | 0 | — |
| `total_other_costs` | 100 | 96 | 4 | 0 | 0 | — |
| `total_expenditure` | 100 | 28 | 64 | 8 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 60 | 34 | 6 | 0 | 100.0% |
| `filer_person` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `positions` | 100 | 0 | 0 | 93 | 7 | 93.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 96 | 4 | 96.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 32 | 68 | 32.0% |

## medium vs low

| field | n | both_null | one_null | agree | disagree | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| `filer_role` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_id` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `filing_action` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `is_current` | 100 | 0 | 0 | 98 | 2 | 98.0% |
| `reporting_period_start` | 100 | 6 | 21 | 51 | 22 | 69.9% |
| `reporting_period_end` | 100 | 7 | 33 | 44 | 16 | 73.3% |
| `filed_date` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `total_compensation` | 100 | 99 | 1 | 0 | 0 | — |
| `total_reimbursements` | 100 | 99 | 1 | 0 | 0 | — |
| `total_other_costs` | 100 | 90 | 6 | 4 | 0 | 100.0% |
| `total_expenditure` | 100 | 84 | 8 | 8 | 0 | 100.0% |
| `total_hours_communicating` | 100 | 100 | 0 | 0 | 0 | — |
| `total_hours_other` | 100 | 100 | 0 | 0 | 0 | — |
| `total_income` | 100 | 100 | 0 | 0 | 0 | — |
| `is_itemized` | 100 | 91 | 4 | 5 | 0 | 100.0% |
| `filer_person` | 100 | 0 | 0 | 99 | 1 | 99.0% |
| `filer_organization` | 100 | 100 | 0 | 0 | 0 | — |
| `employer` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `positions` | 100 | 0 | 0 | 98 | 2 | 98.0% |
| `expenditures` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `engagements` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `gifts` | 100 | 0 | 0 | 100 | 0 | 100.0% |
| `extraction_warnings` | 100 | 0 | 0 | 47 | 53 | 47.0% |


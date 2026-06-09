<!-- Generated during: convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md -->

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

## Reading the both-null rows

Some fields are 99-100% both-null across every arm in the table below — and several of those are **regime-shape-correct null**, not extraction failure. The OH legislative AER is a person-files-for-org form: a natural-person lobbying agent files on behalf of an employer organization, and the form structurally has no other entities or money-flow disclosures. So for OH specifically:

- `filer_organization` (100% both-null everywhere): correct. OH AERs identify a natural-person filer (the agent), not an organizational filer. Goes to `filer_person`; the org goes to `employer`. **Note (2026-06-09):** the schema docstrings and OH brief were edited this session to clarify that `filer_person` and `filer_organization` are *independent*, not XOR — other states' regimes may populate both. The 100% both-null here is OH-shape, not schema-shape. See `src/lobby_analysis/models/filings.py` + `oh_portal/extraction_brief.py`.
- `total_compensation`, `total_reimbursements`, `total_hours_communicating`, `total_hours_other`, `total_income` (99-100% both-null): correct. OH AERs disclose **expenditures by the agent**, not compensation received or hours worked. See `docs/STATE_COVERAGE.md` for the per-state attribute matrix; OH structurally lacks principal↔lobbyist money disclosure.
- `total_other_costs` (90-96% both-null): probably regime-shape too, though worth a spot-check since the both-null rate isn't 100%.

The fields where both-null carries real signal (not regime-shape) are `total_expenditure` and `is_itemized` — those are populated when an AER discloses expenditures and the population rate aligns with the Day-1 finding that ~5% of OH AERs carry expenditures. The Sonnet 28-29 both_null on these reflects ~5% expenditures-carrying filings × 100; the mini both_null rates (60-91) are higher because mini is more conservative about emitting amounts when source is silent.

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


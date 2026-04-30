# Research Log: filing-schema-extraction
Created: 2026-04-30
Purpose: Replace the PRI-projection MVP `StateMasterRecord` data source with **direct filing-schema extraction from statute text** — required filings × required fields × cadence × triggers × exemptions × cross-references — so that the SMR is an authoritative legal reading of what each state's law actually requires from a disclosure filing. PRI 2010 + Sunlight 2015 + FOCAL 2024 (and eventually CPI Hired Guns + Newmark) become diagnostic *projections* of the schema, not data sources for it.

The compendium-keyed `field_requirements` shape (from data-model-v1.1) is the long-term target and is preserved. Only the data source changes — from PRI-rubric yes/no projections to direct statute extraction. The OH 2025 PRI-projection SMR (`docs/historical/statute-retrieval/results/20260430_oh_2025_vs_2010_diff.md`) is the calibration anchor — the new harness must produce ≥22 `field_requirements` for OH (parity with PRI projection) PLUS capture the legal complexity PRI's rubric is structurally blind to (qualitative materiality gates, conjunctive vs disjunctive field requirements, multi-regime parallel chapters, real-party-in-interest disclosure, itemized expenditure schedules, etc.).

## Conversations

(newest first)

## Plans

(newest first)

- **20260430_filing_schema_extraction_kickoff** — Initial design plan for the extraction harness. Defines the target output schema, calibration-anchor approach against the OH 2025 PRI-projection MVP, and an OH-first MVP path before templating to other priority states. Originated from the end-of-session discussion in `docs/historical/statute-retrieval/convos/20260430_oh_2025_baseline_smr.md` (the second mid-session reframe — "the rubric isn't the right product anyway").

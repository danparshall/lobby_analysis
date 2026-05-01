# Compendium Audit v2 — Execution

**Date:** 2026-04-30 (continued 2026-05-01)
**Branch:** filing-schema-extraction
**Originating plan:** [`plans/20260430_compendium_expansion_v2.md`](../plans/20260430_compendium_expansion_v2.md)

## Summary

Executed the v2 audit per plan: walked 5 previously-untouched rubrics (Newmark 2017, Newmark 2005, Opheim 1991, CPI Hired Guns 2007, OpenSecrets 2022) against the existing 118-row PRI/FOCAL/Sunlight-based compendium. The compendium grew to 139 rows (+21 net new) and the framework dedup map grew to 254 entries (+114 walked atomic items, one per rubric item). The durable audit report was born at `results/20260430_compendium_audit.md` and is intended to migrate to repo-level `docs/COMPENDIUM_AUDIT.md` on merge.

Schema decision: confirmed `CompendiumItem.domain` is a fixed `Literal[...]`. Per user direction, definition-trigger items were folded into `domain="registration"` with a notes flag rather than bumping the schema to v1.2. Seven rows now carry the flag, queued for end-of-audit review on whether to promote some to a future `domain="definitions"` value.

Mid-execution, the user pushed back on the audit's PRI-shaped vocabulary. Five threshold rows that originally had PRI-exemption-framed names (`THRESHOLD_FINANCIAL_PRESENT`, etc.) were renamed to rubric-neutral names (`THRESHOLD_LOBBYING_EXPENDITURE_PRESENT`, etc.) with descriptions that give inclusion-framed and exemption-framed framings equal treatment. Decision Log D9 records the rationale; full repo-wide PRI-neutralization was rejected as too much churn for too little harness payoff.

## Topics Explored

- Whether to bump `CompendiumItem.domain` schema to v1.2 to add `"definitions"` (declined; folded with notes flag instead)
- Per-rubric atomic-item enumeration for 5 unwalked rubrics (114 atomic items total)
- Disposition tagging (EXISTS / NEW / OUT_OF_SCOPE / MERGE) per item, with rationale captured in audit doc
- The threshold/trigger cluster: untangled inclusion-framed vs exemption-framed and compensation vs expenditure vs time
- PRI-vocabulary privilege in the compendium: where it shows up, where it bites, what to rename
- Re-scoping the kickoff plan (`plans/20260430_filing_schema_extraction_kickoff.md`) for the new 106-row statute-side MVP target (139 total compendium = 106 statute-side + 33 accessibility-side)

## Provisional Findings

- Disclosure-only scoping (per user reframe) excluded 41 of 114 walked items (prohibitions, penalties, enforcement, revolving-door restrictions). Most of the rest folded into existing rows; only 21 new compendium rows added.
- Newmark 2017 / 2005 / Opheim 1991 share 7 identical "definition" criteria — they're a single conceptual cluster. Two of those (expenditure standard, time standard) were folded into existing PRI threshold rows; three (admin agency, elected officials, public employees as lobbyists) and one new income-side concept (compensation standard) became new rows.
- CPI Hired Guns 2007 contributed the largest row growth (16 new rows, mostly itemized-expenditure metadata + registration-form fields).
- OpenSecrets 2022 contributed one new row (separate-vs-combined registration filings); the rest folded.
- The compendium had a structural PRI bias from curation order: the dedup map literally calls PRI "the spine." A neutral row vocabulary would require a much larger churn pass; in this audit we only renamed the threshold cluster.

## Decisions Made

- **D1.** `domain="definitions"` not added; folded into `registration` with notes flag (option A per user).
- **D2.** Newmark def_legislative_lobbying folds into REG_LOBBYIST (universal-yes; no signal).
- **D3.** `DEF_COMPENSATION_STANDARD` is a separate row from PRI D1 (income-side vs expenditure-side).
- **D4.** Itemized-expenditure metadata (CPI Q16-Q19) split into 4 separate rows.
- **D5.** Aggregate-totals publications (CPI Q35-Q37) classified `domain="accessibility"`, not reporting.
- **D6.** Opheim catch-all "other influence peddling" folded into RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS (no new row).
- **D7.** CPI Q23/Q24 split into PARTIAL dispositions (disclosure half EXISTS, prohibition half OUT_OF_SCOPE).
- **D8.** CPI Q47 (delinquent-filer list) OUT_OF_SCOPE; borderline.
- **D9.** Threshold rows renamed to rubric-neutral framing.
- **D10.** CPI Q30 (electronic-filing training) deferred to a future accessibility-rubric audit.

Full Decision Log lives in the audit doc.

## Results

- [`results/20260430_compendium_audit.md`](../results/20260430_compendium_audit.md) — the durable audit report (anti-loop artifact). Per-rubric tables, excluded-items log, coverage matrix placeholder, Decision Log (D1–D10), notes-flagged-rows review table.

Plus direct CSV / code changes:
- `data/compendium/disclosure_items.csv`: 118 → 139 rows (+21 new; 37 existing rows updated with new framework_references; 5 threshold rows renamed)
- `data/compendium/framework_dedup_map.csv`: 140 → 254 entries (+114 walked atomic items)
- `scripts/build_compendium.py`: threshold row IDs/names updated to neutral framing
- `tests/test_compendium_loader.py`: +5 per-rubric curation-drop tests (12 → 17 total; all passing)
- `docs/active/filing-schema-extraction/plans/20260430_filing_schema_extraction_kickoff.md`: re-scoped row-count targets (~90 → 106 statute-side MVP)

## Open Questions

- **Notes-flagged rows: RESOLVED 2026-05-01.** All 7 flags resolved via v1.2 schema bump per `plans/20260501_data_model_v1_2_definitions_domain.md` and Decision Log D11 in the audit doc. 5 rows promoted to new `domain="definitions"`; 3 stay in `registration` (flag dropped); 2 new symmetry-gap rows added (`DEF_EXPENDITURE_STANDARD`, `DEF_TIME_STANDARD`). Compendium grew 139 → 141; statute-side 106 → 108.
- **Coverage matrix:** placeholder in audit doc; deferred to a small follow-up that generates `data/compendium/coverage_matrix.csv` programmatically from the dedup map.
- **`REG_PHOTO_REQUIRED` / `REG_SEPARATE_LOBBYIST_CLIENT_FILINGS`:** added as statute-side rows but may be portal/process facts in some states; flagged for harness brainstorm to handle.
- **Inclusion-framed expenditure standard:** for symmetry with `DEF_COMPENSATION_STANDARD` we could add `DEF_EXPENDITURE_STANDARD` (inclusion-framed) alongside the renamed `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (exemption-framed). Deferred — user signaled rename was sufficient for now.

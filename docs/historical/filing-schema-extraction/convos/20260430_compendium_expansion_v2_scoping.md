# Compendium Expansion v2 — Scoping Conversation

**Date:** 2026-04-30
**Branch:** filing-schema-extraction

## Summary

Session began as a review of the kickoff plan `plans/20260430_filing_schema_extraction_kickoff.md`. The review surfaced a series of progressively-deeper scope questions that the kickoff plan did not address. The session ended with a new plan (`plans/20260430_compendium_expansion_v2.md`) that is upstream of the harness work — it expands the compendium against rubrics the project hasn't yet walked, before the filing-schema-extraction harness extracts against it.

The scoping arc went through four turns:

1. **Plan review.** Identified concerns with the kickoff plan: ~96-row "MVP target" conflated rows-to-assess with rows-to-populate; design questions Q1 (architecture) and Q2 (prompt shape) are coupled, not separable; multi-run calibration variance unaddressed (parent branch saw 21.3% inter-run disagreement on a simpler task); negative-finding evidence harder than the plan acknowledges; schema gap if `evidence_source.evidence_type="statute_silence"` is added.
2. **Compendium count discrepancy.** User asked about ~140 vs 118 row count. Resolved: 141 source-rubric items in `framework_dedup_map.csv` deduped to 118 compendium rows. Both are correct; different denominators.
3. **Other rubrics.** User asked about other rubrics besides the 4 in the dedup map (PRI disclosure, PRI accessibility, FOCAL 2024, Sunlight 2015). Identified 5 rubrics in `papers/` with extracted text but not yet walked: Opheim 1991, Newmark 2005, Newmark 2017, CPI Hired Guns 2007, OpenSecrets 2022.
4. **Book of States gap analysis.** Compared Book-of-States-derived measures (Newmark 2005, Opheim 1991) to the current compendium. Identified four content clusters in BoS: definitions (7 trigger criteria), prohibitions (gift caps, contribution bans), disclosure (6 types + frequency), penalties. Current compendium covers only disclosure. **User reframe:** "we'll be extracting the data for our consumers, but clearly we can only extract data which is required to be disclosed." This scoped expansion to disclosure-side rubric items only, with prohibitions / penalties / enforcement / cooling-off explicitly out of scope.

## Topics Explored

- Filing-schema-extraction kickoff plan review (8 specific concerns surfaced for the upcoming brainstorm)
- Compendium row-count provenance (141 source items → 118 deduped rows)
- Inventory of rubrics in `papers/` vs. rubrics walked into compendium
- Book-of-States content clusters and what each cluster contains
- Distinction between *statutory rules* (prohibitions/penalties — no filing field) and *disclosure data* (what filings carry)
- Borderline case: definition-trigger criteria ($-spent, time-spent, compensation standards) — structurally part of "definitions" but determines who must file, so disclosure-relevant

## Provisional Findings

- The 118-row compendium represents only 4 rubrics; 5 additional consumer-relevant rubrics are in `papers/` with extracted text but not yet walked.
- Newmark 2017's r=0.04 PRI×CPI cross-correlation suggests rubrics measure genuinely different concepts — argues *for* the union, not against it. Adding rubrics is unlikely to be redundant.
- Estimated additions from walking the 5 rubrics: 10–30 new compendium rows + 60–100 new dedup-map entries. Most items will fold into existing rows via cross-refs; new rows will mostly come from CPI Hired Guns and Newmark 2017.
- Most Book-of-States content (prohibitions, penalties) is out of scope under the disclosure-only reframe. Only the "definitions trigger criteria" cluster is borderline-in-scope.
- The kickoff plan's row-count assumptions (~96 rows for OH MVP) are stale if the compendium expands. The kickoff brainstorm should not run until v2 expansion is settled.

## Decisions Made

- **Compendium expansion is upstream of harness design.** The harness will extract against whatever the compendium defines as the universe; if the universe is wrong, the harness output is wrong.
- **Disclosure-only scoping.** Compendium rows must correspond to data a state could plausibly require to be disclosed in a filing. Prohibitions, penalties, enforcement, revolving-door restrictions are out of scope.
- **Definition-trigger criteria are in scope** as a new `domain="definitions"` value (Newmark/Opheim's "compensation standard / expenditure standard / time standard in the definition" cluster). Rationale: determines who must file, which is a disclosure-relevant statutory feature even though it's not itself a filing field.
- **Final report is repo-level, not branch-only.** The audit lands at `docs/COMPENDIUM_AUDIT.md` on merge so future pre-flight reads surface it; pinned via STATUS.md so agents can't miss it. Motivated by user's stated concern about losing context after a laptop drive crash — the report is the explicit anti-loop mechanism.
- **5 rubrics to walk, 5 to defer.** In-scope: Opheim 1991, Newmark 2005, Newmark 2017, CPI Hired Guns 2007, OpenSecrets 2022. Deferred: F Minus (no methodology in repo), Common Cause (not in repo), GAO 2025 (federal), Lacy-Nichols 2025 (no new indicators beyond FOCAL 2024), entity-resolution and federal-LobbyView papers (not rubrics).
- **Plan deliverable shape:** updated `disclosure_items.csv` + `framework_dedup_map.csv` + `docs/COMPENDIUM_AUDIT.md` (structured: per-rubric tables, excluded-items log, coverage matrix, decision log) + tests + STATUS.md update.

## Results

- `results/20260430_book_of_states_gap_analysis.md` — Comparison of Book-of-States-derived measures (Newmark 2005, Opheim 1991) against the current 118-row compendium. Provenance for the disclosure-only scoping decision.

## Plans Created

- [`plans/20260430_compendium_expansion_v2.md`](../plans/20260430_compendium_expansion_v2.md) — full audit plan with 9 rubrics inventoried, in/out-of-scope rules explicit, deliverables and final-report structure specified.

## Open Questions

- **Row-count estimate is uncertain.** 10–30 new rows is a guess. CPI's 48 questions could surface unexpected disclosure rows; OpenSecrets 2022 might be mostly accessibility-side (already covered).
- **`CompendiumItem.domain` allowed values.** If the field is a fixed enum, adding `domain="definitions"` is a v1.2 schema change; if free-text, it's curation only. To verify when audit starts.
- **Definition-trigger criteria scope call.** Decided to include as `domain="definitions"` rows, but could argue they belong as `notes` qualifiers on existing registration rows. Document the call in the final report's decision log; revise if walkthrough surfaces complications.
- **OpenSecrets 2022 paper depth.** Unclear whether the PDF has the full per-state methodology or only the rubric abstraction (the per-state evaluations may live only on their live web app). Flag during reading.
- **Kickoff-plan re-scoping.** Once v2 expansion lands, the kickoff plan's design questions (especially "MVP target ~96 rows") need updating against new row counts. Not blocking for v2 itself, but the kickoff brainstorm should not run before then.
- **Whether to commit the v2 plan + RESEARCH_LOG update before executing the audit.** User asked at end of session whether to commit and execute now or pause. Pending decision.

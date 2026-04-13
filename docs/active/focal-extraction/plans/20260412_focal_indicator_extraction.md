# FOCAL Indicator Extraction — Implementation Plan

**Goal:** Extract FOCAL's 8 categories and 50 indicators from Lacy-Nichols et al. 2024 into a machine-readable table so the indicators can be applied to US states in a follow-up scoring pass.

**Originating conversation:** `docs/active/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md`. Supporting synthesis: `docs/active/research-prior-art/results/scoring-rubric-landscape.md`.

**Context:** FOCAL is the most current peer-reviewed rubric for evaluating lobbying disclosure regimes (8 categories × 50 indicators, published 2024, synthesized from 15 prior frameworks). Lacy-Nichols applied FOCAL to countries, not to US states individually — so for this project to use FOCAL as the "content quality" half of the composite rubric (with PRI providing the "accessibility" half), the indicators first need to be lifted into a structured form that a scorer can apply state-by-state. Scoring against all 50 states is in scope *eventually* but deferred out of this plan; this pass ends at the machine-readable indicator table.

**Confidence:** High on the extraction task — the paper's Table 3 enumerates all 50 indicators and the surrounding prose defines each category. The only risk is pdftotext mangling of Table 3's layout, which will require PDF consultation, not just the extracted text.

**Architecture:** Pure literature extraction. No scoring, no portal inspection, no code. Output is a single CSV plus a short methodology note. The scoring-application pass will be a separate plan written after this one lands and after the PRI 2026 re-score has produced current evidence to inform shortlist selection.

**Branch:** `research-prior-art` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/research-prior-art`).

**Tech Stack:** Markdown + CSV. Manual PDF transcription, no automated extraction tooling.

---

## Testing Plan

Pure extraction task; no TDD. Validation is by three spot-checks:

1. **Count reconciliation.** After extraction, count rows in the CSV and confirm the total equals 50 indicators across exactly 8 categories. If counts don't match the paper's claims, the extraction is wrong.
2. **Category-level reconciliation.** The paper's Table 3 and prose (Lacy-Nichols text lines 919–1068) specify how many indicators belong to each of the 8 categories. Sum extracted indicators by category and confirm each category's count matches the paper. Mismatch on any category means the table-parsing pass missed an indicator or duplicated one.
3. **Verbatim spot-check.** Pick 5 indicators at random (covering at least 3 different categories). Compare the CSV `indicator_text` to the PDF wording. Any paraphrase that changes the measurement question is a defect.

NOTE: Validation happens immediately after extraction. Do not produce the methodology note or mark the task complete until all three spot-checks pass.

---

## Steps

### Phase 1 — Extraction (estimate: 1 session)

1. **First:** check for supplementary materials at the journal landing page (DOI: 10.34172/ijhpm.8497; journal: https://www.ijhpm.com). If a machine-readable indicator list already exists, download it, verify it contains all 50 indicators, and skip to Phase 2 — the manual transcription below becomes unnecessary.
2. If no supplementary materials: open `papers/Lacy_Nichols_2024__focal_scoping_review.pdf` directly in a PDF viewer (do **not** rely on `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt` alone — extracted text has table-layout breakage noted in the 2026-04-12 RESEARCH_LOG entry).
2. Locate Table 3 (referenced at text line 947). Read it side-by-side with the 8 category definitions in the prose (text lines 842–1068: scope, timeliness, openness, descriptors, revolving door, relationships, financials, contact log).
3. Create `docs/active/research-prior-art/results/focal_2024_indicators.csv` with columns: `indicator_id` (1.1, 1.2, ... 8.N), `category`, `category_definition` (one sentence from the prose), `indicator_text` (verbatim from Table 3), `measurement_guidance` (any prose from the paper clarifying how the indicator is assessed; may be blank), `supports_state_application` (yes/no — flag indicators that are specified at country-level and don't translate cleanly to US state level; blank if clearly applies), `source_framework` (if Lacy-Nichols attributes an indicator to a prior framework, record it; Table 2 summarizes the 15 source frameworks at framework-level, but indicator-level attribution may or may not be present — extractor checks during Phase 1 and reports back).
4. Sum rows and confirm total is 50. If not, return to PDF and re-read.
5. Sum per-category and reconcile against the paper's per-category counts. If not, re-read.
6. Run validation spot-check #3 (verbatim comparison on 5 random indicators).
7. Commit.

### Phase 2 — Methodology note (estimate: same session as Phase 1)

8. Write `docs/active/research-prior-art/results/focal_2024_methodology.md` covering:
   - What FOCAL is and why we're using it (1 paragraph, quoting the scoring-rubric-landscape doc where helpful).
   - The explicit exclusions FOCAL declares (enforcement, sanctions, ethics, whistleblower protections). Flag that these belong in a separate compliance-layer dimension sourced from GAO-25-107523 and state enforcement records.
   - Any indicators flagged `supports_state_application=no` during Phase 1, with a one-sentence rationale per flagged item.
   - Open questions about how specific indicators should be operationalized when applied to US state portals (e.g., "FOCAL's `timeliness` is specified in abstract terms — what filing-frequency thresholds count as 'timely' for a US state?"). These questions are the starting input for the deferred scoring-application plan.
9. Commit.

### Phase 3 — Handoff (estimate: same session)

10. Update `RESEARCH_LOG.md` with a new entry describing the FOCAL extraction deliverable and pointing at the CSV + methodology note.
11. Update `STATUS.md` one-liner under Recent Sessions.
12. Push.

**Explicitly out of scope for this plan:** scoring any US state against FOCAL. That is a separate plan to be written after the PRI 2026 re-score produces shortlist evidence and after the methodology note surfaces operationalization questions that need user input.

---

## Edge Cases

- **Table 3 layout breaks across PDF pages.** If Table 3 spans multiple pages, indicators at page boundaries are the most likely to be missed or duplicated. Count-reconciliation in Phase 1 should catch this, but the extractor should consciously check page boundaries.
- **Indicators that refer to non-US institutions.** FOCAL was built for cross-country comparison; some indicators reference EU-specific or national-register concepts. Flag these `supports_state_application=no` rather than silently dropping them, so the scoring-application plan inherits the full 50.
- **Indicators that overlap with PRI 22-item accessibility rubric.** FOCAL's `openness` category in particular may duplicate some PRI items. Do not de-duplicate in this plan — record FOCAL's full 50 verbatim. Reconciliation between the two rubrics is composition work, not extraction work, and belongs in a later plan.
- **The paper's supplementary materials** may contain a more structured indicator list than Table 3. If the PDF references supplementary materials (Table 2 in the online appendix is a possibility), check the journal's website for them *before* transcribing Table 3 manually — a pre-existing machine-readable version would bypass the whole transcription risk.

## What could change

- If the paper's supplementary materials turn out to contain a CSV or well-formatted table of all 50 indicators, Phases 1–2 collapse to "download and verify" rather than "transcribe by hand." Check supplementary materials first.
- If Lacy-Nichols has published a 2025 or 2026 FOCAL update (the 2025 Milbank Quarterly follow-up applied FOCAL to 28 countries), there may be a revised indicator list. Search for "FOCAL lobbying" updates before committing to the 2024 list as canonical.
- If during extraction the 50 indicators turn out to be structured in a way that doesn't map cleanly to a flat CSV (e.g., sub-indicators under parent indicators, or binary vs. gradient scoring per indicator type), switch to a hierarchical JSON or YAML format and document the decision in the methodology note.

## Questions

1. **Are we obligated to use FOCAL's exact 50 indicators as written, or can the US-state application adapt them?** The plan assumes verbatim extraction in Phase 1; any adaptation happens in the separate scoring-application plan with explicit lineage. Confirm this is the right split.
2. **Indicator-level provenance to source frameworks.** If the paper does attribute specific indicators to specific source frameworks, extract the attribution (column `source_framework`). If the paper only attributes at framework level (via Table 2), the column stays blank and this question becomes moot.
3. **If supplementary materials exist and contain the indicators in a better-structured form, do we use them directly (faster, less risk) or transcribe from the paper to preserve provenance to the publication of record?** Default is "use supplementary materials if they exist, cite them in the methodology note."

---

**Testing Details** Validation is by three spot-checks (total-count reconciliation, per-category-count reconciliation, verbatim comparison on 5 random indicators). All three must pass before the task is marked complete.

**Implementation Details**
- Primary input: `papers/Lacy_Nichols_2024__focal_scoping_review.pdf` (read directly, not via extracted text).
- All outputs under `docs/active/research-prior-art/results/`: one CSV, one methodology note.
- No database, no schema tool, no code. CSV is plain text with a header row.
- The extraction is manual. No LLM-assisted extraction in this plan — the risk of hallucinated indicators outweighs the time savings on a 50-row transcription task.
- Scoring application is **explicitly deferred**. A separate plan covers it; do not accidentally start scoring.
- If the supplementary-materials check (Edge Cases) yields a pre-formatted indicator list, Phases 1–2 collapse to a download+verify task and the plan's effort estimate drops by more than half.

**What could change:** See "What could change" section above.

**Questions:** See "Questions" section above — Q3 should be resolved before Phase 1 starts.

---

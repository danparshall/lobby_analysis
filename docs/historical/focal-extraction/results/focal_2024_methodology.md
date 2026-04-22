# FOCAL 2024 Indicator Extraction — Methodology Note

**Companion to:** `focal_2024_indicators.csv`
**Source:** Lacy-Nichols et al. 2024, "Lobbying in the Sunlight: Development of a Framework for Comprehensive and Accessible Lobbying Disclosures (FOCAL)," *International Journal of Health Policy and Management*, 13:8497. DOI: 10.34172/ijhpm.8497.
**Branch:** `focal-extraction`
**Date:** 2026-04-13

## What FOCAL is and why we're using it

FOCAL is the most current peer-reviewed rubric for evaluating lobbying disclosure regimes. It comprises 8 categories and 50 indicators, synthesized from a scoping review of 15 prior frameworks (Opheim 1991, Newmark 2005, Hired Guns 2007, PRI 2010, and 11 others). The paper itself applied FOCAL at the country level; the 2025 Milbank Quarterly follow-up ("Lobbying in the Shadows") applied it to 28 countries but not to US states individually.

In the `lobby_analysis` project, FOCAL will be scored against US state portals **in parallel with PRI 2010's full 59-item rubric** (37 disclosure-law + 22 accessibility). Both scorings run independently to completion; the composite rubric design is deferred to a **manual review with Corda Democracy Fellowship collaborators**, who will decide which schema (or which hybrid) to carry forward based on the actual two-rubric scoring output, not on rubric analysis alone.

This note covers the extraction of FOCAL's 50 indicators from Table 3 of the paper into `focal_2024_indicators.csv`. **Scoring application against US states is out of scope for *this* deliverable** (extraction only), but is *not* deferred as a project-level question — a separate scoring plan will follow, running in parallel with the PRI 2026 re-score already underway on the `pri-2026-rescore` branch.

### Relationship to PRI — two-dimensional overlap

Earlier framings (including an earlier draft of this note and the upstream `scoring-rubric-landscape.md`) described the PRI–FOCAL relationship as *PRI = accessibility, FOCAL = content*. That framing is wrong. Both rubrics span both dimensions:

| Dimension | PRI 2010 | FOCAL 2024 |
|---|---|---|
| Statutory disclosure requirements | 37 items | 41 items (Scope, Timeliness, Descriptors, Revolving door, Relationships, Financials, Contact log) |
| Portal accessibility | 22 items | 9 items (Openness category) |

The overlap is therefore **structural on both axes**, not at the edges. A composite rubric cannot be built by addition; it requires either a crosswalk (mapping each PRI item to zero/one/many FOCAL indicators and vice versa) or a spine choice (pick one rubric per dimension, treat the other as a checklist). **The project is not making that choice now.** Both rubrics will be scored separately; the composition decision lands with collaborators after data.

## Extraction method

- **Source surface:** Table 3 of the paper (single page, no page-boundary ambiguity).
- **Input used:** `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt` (pdftotext output). Table 3's layout was preserved cleanly enough that PDF viewer consultation was not required, contrary to the plan's risk forecast.
- **No LLM-assisted extraction.** Indicators were transcribed by a human reader (Claude acting in a research-assistant role, no scraping).
- **Ligature normalization:** PDF ligatures `ﬁ`, `ﬂ` were normalized to `fi`, `fl` in the CSV. No other wording changes were made relative to the paper.
- **Supplementary materials check:** `Lacy-Nichols-Supple-File-1-IJHPM.pdf` contains database search strategies, not a structured indicator list, so manual transcription from Table 3 remains the canonical source (confirmed in the 2026-04-12 planning session).

## Validation

Three spot-checks from the plan, all passed:

1. **Count reconciliation:** CSV contains exactly 50 rows across 8 categories.
2. **Per-category reconciliation:** Scope 4 / Timeliness 3 / Openness 9 / Descriptors 6 / Revolving door 2 / Relationships 4 / Financials 11 / Contact log 11 = 50. Matches Table 3's rows.
3. **Verbatim spot-check (5 indicators across 4 categories):** 1.2, 3.3, 5.2, 7.10, 8.11 compared against Table 3 wording. Content identical, modulo ligature normalization noted above.

## Explicit FOCAL exclusions

FOCAL deliberately excludes four dimensions "for feasibility" (paper, lines 822–825):

- **Enforcement and sanctions** (who investigates, what penalties exist, whether they are applied)
- **Ethics provisions** beyond revolving-door rules
- **Whistleblower protections**

For the project, **these belong in a separate compliance-layer dimension**, sourced primarily from GAO-25-107523 (federal LDA compliance audit, April 2025) and state-level enforcement records. They must not be folded into the FOCAL-based content score. This echoes FOCAL's own scope choice and aligns with the scoring-rubric-landscape recommendation to treat enforcement as an independent axis.

## State-applicability flags

The plan asked the extractor to flag any indicators that "don't translate cleanly to US state level" with `supports_state_application=no`. After review of all 50, **none are being flagged as non-applicable.** All 50 translate to US-state portals with operationalization work. The CSV's `supports_state_application` column is left blank per plan convention (blank = applies).

However, two indicators carry operationalization caveats recorded in the CSV's `measurement_guidance` column:

- **1.3 (targets of lobbying):** Uses Westminster-system role names (Ministers, Deputy Ministers, Director-Generals, MPs). US-state application requires translation to governor / lt. governor / legislators / agency heads / staff. This is a straightforward mapping, not a non-applicability.
- **2.3 and 3.2 (ministerial diaries):** "Ministerial diary" is a UK/Australia mechanism. The US-state analog is executive calendar or meeting-log disclosure, which exists only rarely at state level. The indicator *can* be scored (most states will score 0), but the scoring-application plan should decide whether to (a) keep the indicator as-is (most states fail), (b) rename to "executive calendar disclosure" to match US vocabulary, or (c) drop as structurally inapplicable to the US context. Recommend option (b): keep the concept, normalize the language.

## Compound / multi-part indicators

One indicator in the extraction is visibly compound and warrants attention during scoring:

- **3.3** combines five distinct sub-conditions: (1) available without registration, (2) free to access, (3) open license, (4) non-proprietary format, (5) machine readable. Scoring it as a single yes/no will suppress variance across states — most states will satisfy some but not all sub-conditions. Recommend decomposing 3.3 into 3.3a–3.3e during the scoring-application plan, with explicit weighting. This is the single biggest structural deviation from verbatim FOCAL we expect to make, and it should be called out in the scoring-plan's rubric-lock section.

The decomposition is deliberately **not** done in this extraction pass because the deliverable is verbatim FOCAL. Adaptation happens in the later scoring plan, with explicit lineage to the original.

## Source-framework provenance

The CSV contains a `source_framework` column, included per plan because the paper's Table 2 summarizes the 15 source frameworks. However, **Table 2 provides framework-level not indicator-level attribution**: it tells us that 13 of 15 frameworks included a "scope" dimension, but not which specific scope indicator came from which framework. The `source_framework` column is therefore blank throughout the CSV. The paper does provide some category-level attribution in prose (e.g., the Financials category is "especially US-centric, with many indicators originating from the Hired Guns framework"), but this is documented here rather than in the row-level CSV.

## Open operationalization questions (input to the deferred scoring plan)

1. **Timeliness thresholds.** FOCAL specifies "real time (eg, daily)" and "monthly (or more frequently)" for different indicators. For US states with quarterly filing cycles, what ordinal scoring (0/1/2/3) should be applied? Does quarterly filing score 0 on 2.1 and 2.2, or partial credit?
2. **Indicator 3.3 decomposition.** As above. Keep compound or split into 5? Recommend split.
3. **Ministerial diaries (2.3, 3.2).** Keep verbatim, rename to US vocabulary, or drop? Recommend rename.
4. **Westminster role names (1.3).** Create an explicit US-state role-translation table as part of the scoring rubric, so scorers apply it consistently.
5. **PRI-FOCAL composition.** Both rubrics span both the statutory-content and portal-accessibility dimensions (see table above). The project is deliberately **not** reconciling them pre-scoring — PRI and FOCAL will be scored independently, and collaborators will choose the composite after reviewing both sets of results. No reconciliation pass is needed before scoring; it is needed *after*, driven by human judgment on the data.
6. **Financial thresholds (1.2).** "No (or low) financial or time threshold" — paper acknowledges this is context-dependent. Need a concrete US-state threshold for scoring (e.g., lobbyist-registration income threshold in $).
7. **Scoring granularity.** Binary (yes/no) vs. ordinal (e.g., 0/1/2). FOCAL itself does not prescribe a scoring scheme — the paper describes it as a framework for evaluating registers, not a numerical scoring instrument. Choice of granularity is an open design decision.

## Next: FOCAL scoring plan (to be written)

A separate plan will cover applying FOCAL to US state portals, running in parallel with the PRI 2026 re-score already underway. That plan should:

1. Resolve the open operationalization questions above (scoring granularity, timeliness thresholds, ministerial-diary handling, Westminster role translation, 3.3 decomposition, 1.2 thresholds).
2. Define the scoring scheme (binary vs. ordinal) per indicator.
3. Pilot-score 3 states before scaling to 50.
4. Output a per-state FOCAL score table in the same shape as the PRI output, so both can be reviewed side-by-side.

**Explicitly not in scope for the FOCAL scoring plan:** reconciliation with PRI. That is a downstream collaborator-review task that happens after both rubrics have produced 50-state scores.

---

**Source file:** `papers/Lacy_Nichols_2024__focal_scoping_review.pdf` (Table 3, page 10 of the published PDF, text lines 946–1030 in the extracted text).

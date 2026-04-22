<!-- Generated during: convos/20260413_pri_phase1_phase2_transcription.md -->

# PRI 2026 Rubrics — Methodology Note

**Status:** Internal. Not for external publication without a polish+review pass.
**Scope:** Documents the 2026 updates to PRI's 2010 state lobbying disclosure-law and accessibility rubrics.

## Design decisions

### Disclosure-law rubric (61 items)

- **No modernizations.** All 61 atomic items from PRI 2010 are retained verbatim.
- **Reverse-scoring documented.** Two items (B1, B2) were reverse-scored in PRI 2010 but the paper documented this only in footnotes (footnotes 85 and 86). The 2026 CSV makes this explicit via a `scoring_direction=reverse` column and quoted scoring guidance:
  - **B1** (government/official exemption exists): 1 = no such exemption; 0 = exemption exists.
  - **B2** (government agencies relieved from non-gov regs): 1 = not relieved; 0 = relieved.
- **E-component scoring deferred.** PRI 2010's 20-point max for the E (Information Disclosed) component is not cleanly decomposable at the item level in the paper body — it aggregates as "higher of E1/E2 + double-count on F/G when both sides report + separate J." For 2026 we collect every E1 and E2 sub-item as raw data but do not attempt to reproduce PRI's 20-point aggregation. Scoring is treated as an internal post-collection step; no published deliverable depends on reproducing PRI's exact weights.
- **Known ambiguities carried forward** (flagged in `pri_notes` on each item):
  - C0/C1–C3: PRI 2010 scored C as 0/1 overall even though three sub-criteria are described. Sub-criteria collected but their contribution to the composite is unresolved.
  - D0/D1/D2: similar — D scored 0/1 but two sub-criteria described. Raw threshold values captured (`numeric_usd_or_null` for D1, `numeric_percent_or_null` for D2).
  - E1h/E2h reporting frequency: PRI footnote 89 scoring rule is awkwardly worded ("1 point for reporting … less than three times a year"). We collect every frequency option as binary and defer the scoring rule.

### Accessibility rubric (59 items)

**Retained from PRI 2010 (22 items, `source=pri_2010_kept`):** Q1–Q8 including Q7's 15 sort-criterion sub-items and Q8's 0–15 raw simultaneous-sorting score. Two items have sharpened 2026 scoring guidance:
- **Q3** "website identification" — 2026 operationalizes PRI's undefined "easily" as "first 5 organic Google results for `<state> lobbying disclosure`."
- **Q5** "historical data availability" — 2026 operationalizes PRI's undefined horizon as "at least 5 prior years accessible."
- **Q8** simultaneous sorting — 2026 defines the 0–15 raw score as "count of Q7 sub-criteria combinable in a single query." PRI never specified how to arrive at the 0–15 number.

**Added for 2026 (37 items, `source=new_2026`):**

| Addition | Sub-items | Rationale |
|----------|-----------|-----------|
| **Q9 — Downloadable sort results** | 15 (Q9a–Q9o, mirroring Q7) | Captures the 2026 failure mode where portals let users filter-to-view but will not export the filtered result. A research workflow needs the data, not a screenshot. |
| **Q10 — Bulk download** | 1 | Separate from Q6 (format) and Q9 (per-search): can the *entire dataset* be downloaded as a few files, not per-record or per-search? Fundamental to any downstream pipeline. |
| **Q11 — Open API** | 1 | Documented, free programmatic access. Paid-only APIs do not satisfy. Rate limits noted qualitatively but do not zero out the score by themselves. |
| **Q12 — No authentication barrier** (reverse) | 1 | Reverse-scored. Any login/paywall/attestation gating any part of the data → 0. Several real 2026 portals (historically NY, some city-level) have done this. |
| **Q13 — Data dictionary** | 15 (14 fields + record ID) | Fractional per-field score over the union of fields PRI's E1/E2 already requires states to disclose. A portal with undocumented fields forces researchers to reverse-engineer semantics, which silently corrupts analysis. Machine-readable unique record IDs folded in as Q13o per user direction. |
| **Q14 — Persistent record URLs** | 1 | Each filing has a stable, citable URL. Session-token or AJAX-only views score 0. Critical for reproducibility. |
| **Q15 — Raw filing access** | 1 | Original filed documents retrievable alongside parsed fields. Portal extraction errors silently corrupt downstream data; raw access is the audit trail. |
| **Q16 — Freshness** | 2 (Q16a timestamp present, Q16b actually fresh) | Two sub-items: (a) does the portal display a "last updated" timestamp, and (b) is the data actually current per the state's own filing cadence? The two failure modes are distinct: a portal can display a fresh timestamp while silently missing recent filings, and up-to-date democracy measurement requires both. |

### Scoring normalization (deferred)

Per user direction, this rubric is used to **collect raw data**. Scoring weights and aggregation are applied downstream:

- Binary items contribute raw 0/1.
- Q8 raw 0–15 → 0–1 via /15 (as PRI 2010).
- Q13 raw 0–15 → 2.5 points (anchor the "data dictionary" cluster at 2.5 overall).
- All other multi-item sections aggregate as sum unless explicitly normalized.

If we later want a published 2026 index, normalization choices and per-item weights go in a separate scoring-methodology doc; the rubric stays as raw-collection definitions.

## Omitted / rejected additions

- **Rate limits** — folded into Q11 scoring guidance rather than a standalone item.
- **FOIA / records-request alternative pathway** — already covered by PRI Q1.
- **Data retention horizon** — sharpened Q5 rather than added. Deeper retention analysis belongs downstream.
- **Per-search export completeness** — covered by Q9.

## Open items

1. **E-component scoring** for disclosure-law: once we have 2026 state data, decide whether to reproduce PRI's "higher of E1/E2 + F/G double-count + J" aggregation or re-specify from scratch.
2. **Q13 normalization constant** (currently 2.5 max). May want to revisit after seeing 2026 data distribution — if no state scores above 10/15 field-documentation, a 2.5 max caps most states too low.
3. **Q8 modernization candidate**: is "count of Q7 sub-criteria combinable" the right 2026 operationalization, or should it be a continuous API-query-language score instead? Defer.
4. **Q12 binary vs graded**: currently binary (any auth = 0). Could be graded if several states have partial gating. Revisit post-pilot.


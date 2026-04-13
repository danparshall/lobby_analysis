# Research Log: pri-2026-rescore

**Created:** 2026-04-12
**Purpose:** Re-score all 50 US state lobbying disclosure portals against updated versions of Pacific Research Institute 2010's 22-item accessibility rubric and 37-item disclosure-law rubric, producing a 2026 State Lobbying Data Accessibility Index as a standalone deliverable and feeding the priority-state shortlist decision.

**Originating plan:** `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md`
**Originating convo:** `docs/historical/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md`
**Upstream synthesis:** `docs/historical/research-prior-art/results/scoring-rubric-landscape.md`

---

## Session: 2026-04-13 — pri_phase1_phase2_transcription

### Topics Explored
- Transcription of PRI 2010 accessibility rubric (Section IV) and disclosure-law rubric (Section III) into atomic-item CSVs
- Transcription of PRI 2010 per-state scores (Tables 5 and 6) into machine-readable score CSVs
- Structure of PRI's scoring: accessibility = 8 questions (22 atomic items); disclosure-law = 5 sub-components (A/B/C/D/E → 37) where item-level detail is underspecified for E

### Provisional Findings
- Rubric CSVs written with `item_id`, `category`, `item_text` (verbatim), `data_type`, `pri_notes` schema. Scoring deferred to Phase 3.
- 2010 score CSVs reconcile cleanly: all 50 states, both rubrics, zero mismatches between sub-component sums and published totals.
- Validation #1 (verbatim spot-check on 3 items per rubric): pass.
- Validation #2 (plan asked for 5-state reconciliation): exceeded, full-50 reconciliation is clean.
- Structural finding: the plan's "22-item" and "37-item" framings need qualification — PRI publishes item-level data only for accessibility's 6 binary Qs, not for Q7 sub-criteria or for disclosure-law's E component.

### Results
- `results/pri_2010_accessibility_rubric.csv` (22 items)
- `results/pri_2010_disclosure_law_rubric.csv` (61 items)
- `results/pri_2010_accessibility_scores.csv` (50 states)
- `results/pri_2010_disclosure_law_scores.csv` (50 states)

### Phase 3 (added same session)
- Built `pri_2026_accessibility_rubric.csv` (59 items) and `pri_2026_disclosure_law_rubric.csv` (61 items) with `source` and `scoring_direction` columns.
- Added 37 new accessibility items: Q9 download-per-sort-criterion (15), Q10 bulk download, Q11 open API, Q12 auth barrier (reverse), Q13 data dictionary per PRI E-union fields (15 including record ID), Q14 persistent URLs, Q15 raw filings, Q16a/b timestamp+freshness.
- Disclosure-law: no modernizations; B1/B2 reverse-scoring made explicit.
- `pri_2026_methodology.md` written with rationale and open items.
- User reviewed and signed off on both 2026 rubrics. Phase 3 gate passed.

### Next Steps
- Phase 4: scoring pipeline build. Decide keep/modernize/obsolete per item, propose additions (API, bulk download, auth barriers, data dictionaries), resolve open questions on B1 polarity, Q8 scoring, E-aggregation structure, frequency-scoring rule. Gate: user sign-off before Phase 4.

---

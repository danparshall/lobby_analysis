# Research Log: pri-2026-rescore

**Created:** 2026-04-12
**Purpose:** Re-score all 50 US state lobbying disclosure portals against updated versions of Pacific Research Institute 2010's 22-item accessibility rubric and 37-item disclosure-law rubric, producing a 2026 State Lobbying Data Accessibility Index as a standalone deliverable and feeding the priority-state shortlist decision.

**Originating plan:** `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md`
**Originating convo:** `docs/historical/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md`
**Upstream synthesis:** `docs/historical/research-prior-art/results/scoring-rubric-landscape.md`

---

## Session: 2026-04-13 — pri_phase4_data_collection_prep

### Topics Explored
- Scoping "data-collection pipeline" to snapshots-first, Sonnet-directed URL discovery, browser-UA curl for raw capture.
- Architectural pivot: Claude Code subagents over Python/Anthropic SDK pipeline (plan's Q3 default). Tore down scaffold; saved feedback memory.
- Role-vocabulary discipline during discovery; WAF/SPA behavior during snapshotting; `suspicious_challenge_stub` flag for HTML <2KB.
- Policy-gap framing: WAF + no-API + no-bulk is a real configuration the PRI 2026 rubric should penalize — not a pipeline bug.

### Provisional Findings
- Stage 1 complete: 50/50 states have a seed URL JSON in `data/portal_urls/`, zero fabricated URLs, 15 states with flagged seeds catalogued in `_flagged.md`.
- Stage 2 complete: 50/50 states have a snapshot manifest; 981 artifacts, ~350 MB on disk, 17 `suspicious_challenge_stub` flags, 54 honest skips.
- Coverage tiers: 40 states cleanly captured; 8 partial (WAF/SPA on subset); 2 near-empty (AZ, VT — 100% WAF-blocked).
- Subagent tool-loading is probabilistic — 2/50 Stage 1 dispatches needed retry with explicit tool-availability hint.
- SPA coverage gap is real: ~12 states' public portals serve byte-identical JS shells to curl. Playwright follow-up needed for rubric-UX items.

### Results
- `data/portal_urls/*.json` — 50 seed URL JSONs (not in docs; lives in `data/`).
- `data/portal_urls/_flagged.md` — 15 states with flagged seed URLs for collaborator re-verification.
- `data/portal_snapshots/<STATE>/2026-04-13/` — 50 per-state snapshot directories + manifests.
- [`results/20260413_stage1_stage2_collection_summary.md`](results/20260413_stage1_stage2_collection_summary.md) — aggregate + per-state table, coverage tiers, findings.

### Next Steps
- Collaborator pass: manually verify WAF'd / DNS-failed / SPA-only URLs in `_flagged.md`; update seed JSONs.
- Playwright supplement for ~10 SPA/WAF'd states (AZ, VT, MA, NH, ID, ND, SC, GA, NM, ME).
- Phase 5: build Sonnet scoring function, pilot on CA/CO/WY, iterate rubric if disagreements surface.

### 2026-04-14 addendum — handoff to unified PRI+FOCAL scoring chain
- **Decision:** PRI and FOCAL rubrics will be scored against the same snapshot corpus in a single chained scoring pass per state (not two independent passes). Rationale: shared evidence, cross-rubric consistency, per-project decision to defer composite-rubric choice to post-data collaborator review.
- **Handoff doc:** [`plans/20260414_pri_focal_unified_scoring_handoff.md`](plans/20260414_pri_focal_unified_scoring_handoff.md) — captures current state, reproducibility commitments, recommended next steps, known issues. Next agent should read this before starting Phase 5.
- **Reproducibility commitments locked:** versioned scorer prompt, provenance stamping per score row, 3× temp-0 runs per state, raw outputs retained alongside adjudicated scores. Honest note: Stages 1+2 are not reproducible (LLM-chosen search terms + link selections); the frozen snapshot bytes are the reproducibility anchor, not the assembly pipeline.
- **Next session:** other agent takes over from this handoff. Likely first task: branch strategy decision (merge focal-extraction into pri-2026-rescore, or both into a new `scoring` branch).

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

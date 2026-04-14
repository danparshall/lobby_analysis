# Research Log: focal-extraction

Created: 2026-04-13
Purpose: Extract FOCAL 2024's 8 categories × 50 indicators (Lacy-Nichols et al.) from Table 3 of the paper into a machine-readable CSV, with a methodology note. Scoring against US states is explicitly deferred to a later plan.

Originating convo: `docs/historical/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md`
Plan: `plans/20260412_focal_indicator_extraction.md` (copied from historical branch)
Upstream synthesis: `docs/historical/research-prior-art/results/scoring-rubric-landscape.md`

## Plans

- [`plans/20260412_focal_indicator_extraction.md`](plans/20260412_focal_indicator_extraction.md) — Extraction (complete, shipped 2026-04-13).
- [`plans/20260413_focal_50_state_scoring.md`](plans/20260413_focal_50_state_scoring.md) — 50-state scoring against locked FOCAL rubric, reusing PRI's snapshot infrastructure (drafted 2026-04-13, awaiting kickoff).

## Results

- [`results/focal_2024_indicators.csv`](results/focal_2024_indicators.csv) — 50 FOCAL indicators, 8 categories, verbatim from Lacy-Nichols Table 3.
- [`results/focal_2024_methodology.md`](results/focal_2024_methodology.md) — Extraction methodology, PRI–FOCAL overlap table, open operationalization questions.
- [`results/20260413_snapshot_sufficiency_audit.md`](results/20260413_snapshot_sufficiency_audit.md) — Cross-rubric audit of PRI Stage-1/Stage-2 portal snapshots. Conclusion: sufficient to begin pipeline build and pilot on clean-capture states; Playwright supplementation for SPA/WAF states as a parallel workstream.

## Sessions

(Newest first)

- **2026-04-13 (pm)** — Audited PRI Stage-1/Stage-2 snapshot sufficiency across both rubrics. Findings in [`results/20260413_snapshot_sufficiency_audit.md`](results/20260413_snapshot_sufficiency_audit.md). Decision: proceed with option (1) — build pipeline now, pilot on clean-capture states (~25), run Playwright supplement in parallel for SPA/WAF states (~13). AZ and VT scored from statute-only evidence with explicit null markers.
- **2026-04-13** — [convos/20260413_focal_indicator_extraction.md](convos/20260413_focal_indicator_extraction.md) — Executed the FOCAL extraction plan end-to-end in one session. CSV of 50 indicators across 8 categories produced, all three validation spot-checks passed, methodology note written. Mid-session correction of the PRI–FOCAL framing (two-dimensional overlap, not edge overlap). Decision: score both rubrics in parallel and defer composite design to collaborator review post-data. Next: design FOCAL scoring plan, decide whether to reuse the PRI pipeline infrastructure.

## Deliverables

- `results/focal_2024_indicators.csv` — 50 FOCAL indicators (8 categories × 50), verbatim from Lacy-Nichols et al. 2024 Table 3, with operationalization caveats in `measurement_guidance` column.
- `results/focal_2024_methodology.md` — extraction method, validation, PRI–FOCAL overlap table, 7 open questions for the FOCAL scoring plan.

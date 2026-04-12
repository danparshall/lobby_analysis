# PRI 2026 Accessibility Re-Score — Implementation Plan

**Goal:** Produce a 2026 State Lobbying Data Accessibility Index by re-scoring all 50 US state lobbying portals against updated versions of Pacific Research Institute's 2010 22-item accessibility rubric **and** its 37-item disclosure-law rubric (59 items combined), using a Sonnet-based scoring pipeline with subagent parallelization and human validation.

**Originating conversation:** `docs/active/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md`. Supporting synthesis: `docs/active/research-prior-art/results/scoring-rubric-landscape.md`.

**Context:** The project needs a current-vintage, methodologically defensible scoring of state lobbying portal accessibility to (a) select the 5–8 priority states with evidence rather than tier guesses, and (b) produce a publishable external deliverable independent of pipeline code. PRI 2010 is the most directly applicable prior art (37 disclosure-law + 22 accessibility criteria, applied to all 50 states) but is 16 years stale; the *rubric* survives even though the *scores* don't.

**Confidence:** Medium-high on the approach (PRI's rubric is the best available starting point and its limitations are well-understood), medium on the scope (whether "all 50" or "all 50 plus a modernization pass on the rubric itself" is correct — see Questions).

**Architecture:** Literature-extraction + LLM-assisted structured-data-collection. A small scoring pipeline (Sonnet as the scorer, one subagent per state) applies the locked 2026 rubric to portal content with explicit evidence requirements per item. Human validators verify a calibration set and audit disagreements. Outputs are machine-readable rubric definitions, per-state scoring CSVs with evidence trails, and a short written index document.

**Branch:** `research-prior-art` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/research-prior-art`).

**Tech Stack:** Markdown for docs; CSV for structured data. Python + `uv` for the scoring pipeline. Claude Sonnet via the Anthropic SDK for scoring (subagents launched one per state). Playwright or `requests` + `httpx` for portal fetching (decision deferred to pipeline-build phase). Evidence archival via stored portal snapshots.

---

## Testing Plan

This is an analysis/data-collection task, not code. Per the write-a-plan skill, TDD does not apply. Instead, the plan is validated by three spot-checks:

1. **Rubric transcription spot-check.** After transcribing PRI's 22 items from the PDF into the rubric CSV, pick 3 items at random and compare the CSV text to the PDF wording. Any paraphrase that changes the scoring question is a defect.
2. **2010 baseline reproduction.** Transcribe PRI's published per-state 2010 scores for 5 states (3 top, 2 bottom) into the scoring worksheet. Sum the 22 items and confirm the total matches PRI's published combined accessibility score for each of the 5 states. If totals don't reconcile, the rubric interpretation is wrong and the transcription step must be reworked before any 2026 scoring.
3. **LLM self-consistency check.** Each Sonnet scoring run is repeated 3× per state with temperature 0 but separate sessions. Items with disagreement across the 3 runs indicate rubric ambiguity (not model flakiness — temp-0 Sonnet disagreeing with itself means the rubric item was interpretable more than one way against the same portal snapshot). High disagreement rate (>10% of items across states) is the signal that the rubric must be tightened before the full run proceeds. Flagged items go to a `human_review_queue.csv` for rubric-sharpening pass, not case-by-case score adjudication.
4. **Pilot spot-check, not calibration gate.** Before the full 50-state run, score 3 states (CA, CO, WY — one expected-high, one expected-medium, one expected-low) and have the user skim the results against the portal snapshots. The goal is not human-vs-Sonnet agreement; it's confirming the evidence quotes cited in the output are real, relevant, and that the rubric item was correctly applied. Problems found here are treated as rubric-clarity bugs and fixed in Phase 3.

NOTE: Validation happens after each step, not only at the end. The step order is "transcribe → reproduce 2010 → modernize → build pipeline → pilot → full run" so rubric errors surface before 47 states of Sonnet calls have been made. **The rubric, not the scorer, is the source of truth** — any failure mode resolves by sharpening the rubric.

---

## Steps

### Phase 1 — Rubric transcription, 22 accessibility + 37 disclosure-law items (estimate: 1–2 sessions)

1. Open `papers/PRI_2010__state_lobbying_disclosure.pdf` and `papers/text/PRI_2010__state_lobbying_disclosure.txt`.
2. Locate the **accessibility rubric** in Section IV (text file lines ~1468–1522 list the 8 category headers; the full 22-item breakdown is in the body + Appendix E).
3. Locate the **disclosure-law rubric** (37 items across 5 sub-components, per the scoring-rubric-landscape doc). This is in Section III of the paper with detail in Appendix C.
4. Transcribe into two files:
   - `docs/active/research-prior-art/results/pri_2010_accessibility_rubric.csv`: 22 items, columns = `item_id`, `category`, `item_text` (verbatim), `scoring_scale`, `max_points`, `pri_notes`.
   - `docs/active/research-prior-art/results/pri_2010_disclosure_law_rubric.csv`: 37 items, same schema plus a `sub_component` column for the 5 law sub-components.
5. Sum `max_points`: accessibility total must equal 22; disclosure-law total must match PRI's stated max (confirm from paper — typical PRI methodology is weighted, so the sum may not be 37 if items have different weights). Document the scoring model used.
6. Run validation spot-check #1 on 3 items from each rubric.
7. Commit.

### Phase 2 — 2010 baseline transcription (estimate: 1–2 sessions)

8. Locate per-state score tables for both rubrics (Appendices C and E, plus the combined-ranking table in Section V).
9. Transcribe into two CSVs:
   - `pri_2010_accessibility_scores.csv`: `state` + one column per accessibility `item_id` + `total_accessibility_2010` + `rank_accessibility_2010`.
   - `pri_2010_disclosure_law_scores.csv`: same shape for the 37 disclosure-law items.
10. Run validation spot-check #2: for 5 states (CT, IN, TX, NH, WY), sum both rubrics and confirm totals match PRI's published per-state scores. **Both rubrics must reconcile** — if either fails, return to Phase 1.
11. If totals reconcile: commit. If not, the rubric weighting or category membership is wrong; fix Phase 1 first.

### Phase 3 — 2026 rubric modernization (estimate: 1–2 sessions)

12. For each item in both rubrics, classify as **keep** / **obsolete** / **modernize** (accessibility, e.g., "website existence" is likely obsolete; "data format" needs modernization) and propose **additions** (API access, authentication barriers, bulk-download, rate limits, documented data dictionaries). Cap accessibility additions at ~6 to preserve rubric shape. Disclosure-law rubric is less likely to need additions — most modernization there will be rewording items for current statutory vocabulary (e.g., "electronic filing requirement" is a yes/no question that wasn't meaningful in 2010 for most states).
13. Write `pri_2026_accessibility_rubric.csv` and `pri_2026_disclosure_law_rubric.csv` mirroring Phase 1 schemas, with an added `source` column (`pri_2010_kept` / `pri_2010_modernized` / `new_2026`) and a `scoring_guidance` column giving the LLM scorer explicit evidence criteria for each item (e.g., "score 1 if bulk CSV download is available without authentication; 0 otherwise; evidence = URL of download link").
14. Write `docs/active/research-prior-art/results/pri_2026_methodology.md` documenting the modernization decisions per item with one-sentence rationale.
15. **Gate: present both modernized rubrics to the user for review.** Do not proceed to Phase 4 until user signs off. The rubric is the primary point of failure for LLM-assisted scoring — if the rubric is sharp, the scores will be; if not, no amount of prompt engineering will rescue them.

### Phase 4 — Scoring pipeline build (estimate: 2–3 sessions)

16. Create `src/pri_scoring/` with a minimal Python package. Dependencies: `anthropic`, `pydantic` for typed outputs, and a portal-fetching library (decision between `httpx`+`beautifulsoup4` for static pages vs. `playwright` for JS-rendered portals — make this call per-state during fetch, and default to playwright for robustness).
17. Build the scoring function: input = `(state, rubric_csv, portal_snapshot)`; output = one row per rubric item with `score`, `evidence_quote_or_url`, `confidence`, `notes`. Sonnet call uses temperature 0, structured output via pydantic model, rubric items delivered one at a time (not batched) to keep each scoring decision independently auditable.
18. Build the portal-snapshot step: given a state, fetch the primary lobbying disclosure portal landing page + up to N linked pages (search, download, historical). Archive raw HTML + any downloaded files to `data/portal_snapshots/<state>/<date>/`. Snapshots are the evidence backbone — everything Sonnet scores against must be traceable to a snapshot.
19. Build the subagent orchestrator: one subagent per state, launched in parallel, writing to per-state output files. Use the Agent tool with a purpose-built scoring-agent prompt (spec TBD in this phase) that locks Sonnet to evidence-cited scoring with no extrapolation.
20. **Test the pipeline on 2 states first (pick one from the calibration set that will be human-scored in Phase 5, and one outside it) before launching all 50.** Verify the output CSV shape matches the 2010 baseline schema and every score has a non-empty evidence field.
21. Commit the pipeline. Data outputs (portal snapshots) are in `data/` which is symlinked out of the worktree — do not commit those.

### Phase 5 — Pilot run (estimate: 1 session)

22. Run the Sonnet pipeline on 3 pilot states: California, Colorado, Wyoming.
23. Run the self-consistency check (validation #3): score each pilot state 3× in separate sessions at temp 0. Items where the 3 runs disagree on the same portal snapshot are flagged — these signal rubric ambiguity, not random model variation.
24. User skims results against the portal snapshots. Questions the review checks:
    - Does every score have a real, relevant evidence quote or URL?
    - Do the scored items actually match what the portal shows?
    - Did the rubric item get interpreted as intended?
25. **Any defect found is fixed as a rubric-sharpening pass in Phase 3, not as a per-score adjudication.** Re-lock rubric and re-run the pilot. Iterate until the pilot passes cleanly.
26. Commit the pilot results and any rubric revisions.

### Phase 6 — Full 50-state scoring (estimate: 1 session of wall-clock, hours of model time)

27. With the rubric locked after pilot, launch subagents across the remaining 47 states in parallel. Pilot states (CA, CO, WY) stay fixed — do not re-score.
28. Run the self-consistency check across all 50 (3× per state). Items with inter-run disagreement go to `human_review_queue.csv`. These are again rubric-interpretation issues more than score issues — but at this stage, adjudicating per-item is cheaper than restarting the full run, so the queue is reviewed and resolved item-by-item with the original model outputs preserved alongside.
29. If the disagreement rate exceeds ~10% of items across states, stop. That volume means the rubric still has systemic ambiguity and the full run is not salvageable item-by-item — return to Phase 3.
30. Commit the final scores CSVs.

### Phase 7 — Deliverable synthesis (estimate: 1–2 sessions)

31. Produce `docs/active/research-prior-art/results/state_accessibility_index_2026.md` — external-facing deliverable. Contents: ranking tables (both rubrics, combined + individual), category-level sub-rankings, 2010-vs-2026 delta table, analysis of surprises, methodology section disclosing the LLM-assisted pipeline and its calibration performance (this transparency is not optional for a publishable deliverable).
32. Update `docs/active/research-prior-art/results/state-infrastructure-tiers.md` to reconcile with 2026 evidence. Revisit the 8-state shortlist.
33. Update `RESEARCH_LOG.md` and `STATUS.md`. Commit, push.

---

## Edge Cases

- **States with multiple disclosure portals** (e.g., one for lobbyist registration, another for expenditures). The snapshot step must fetch all relevant portals per state; scoring is against the union with per-item notes on which portal produced the evidence.
- **States where the portal redirects or changes URL between snapshot date and scoring completion.** Snapshot date is frozen per state; if a portal changes during the scoring window, the earlier snapshot is authoritative for that state. Document snapshot dates per state.
- **States with paywalled or login-gated data.** Authentication barriers count as scoring penalties on the relevant rubric items. Do not authenticate. The pipeline must detect and record auth walls rather than trying to bypass them.
- **JS-rendered portals where `httpx` returns an empty shell.** Default to playwright for snapshots to avoid this failure mode silently.
- **Items where 2010 binary scoring doesn't capture 2026 gradient** (e.g., "data format" when a state has CSV, API, and PDF-only historical data). Use multi-point scales from Phase 3; if insufficient, flag during calibration (Phase 5) and refine rubric before full run.
- **States that launched all-electronic mandates between 2010 and 2026** (e.g., Montana via HB 804, October 2025). The 2026 score reflects 2026 portals; historical-coverage items penalize states with only-recent electronic data. Record transition dates in state-level notes.
- **Sonnet refusing to score an item** because of ambiguous evidence. The pipeline treats "unable to determine from snapshot" as a legitimate output (score = null, flagged for human review) rather than forcing a guess. This is a feature, not a bug.
- **Subagent failures / rate limits** during the full-50 run. Orchestrator must checkpoint per-state completion and be re-runnable; a partial failure should not force re-scoring already-completed states.

## What could change

- If FOCAL's 50 indicators turn out to overlap more than expected with PRI's 22 (specifically FOCAL's "openness" category), the rubric-modernization step may pull in FOCAL items rather than invent new ones. Check the FOCAL extraction deliverable (sister plan) before finalizing the 2026 rubric.
- If F Minus 2024's methodology gets verified in a separate workstream and turns out to be defensible, some of its indicators may also be candidates for 2026 rubric additions.
- If the user decides partway through that scoring all 50 states is overkill and only the 8-state shortlist matters, Phase 4 can stop early and the deliverable in Phase 5 can be scoped as a shortlist-only preview.
- If the modernized rubric diverges too far from PRI 2010 (e.g., >40% of items changed), the "re-score" framing breaks down and this should be renamed to "2026 State Lobbying Data Accessibility Index, inspired by PRI 2010." The user should make that call when Phase 3 delivers.

## Questions

1. ~~**Publication target for the deliverable.**~~ **Resolved 2026-04-12:** repo-internal for now, external publication TBD. Phase 7 scopes to a repo-internal deliverable; if later promoted externally, add a polish+review pass.
2. **Portal snapshot retention and publication.** Snapshots are the evidence backbone. Publish alongside the deliverable (transparency win, but potentially large and may include sensitive third-party content) or keep internal, evidence-on-request? Affects Phase 7 scope.
3. **Sonnet-via-subagents vs. Sonnet-via-SDK.** Plan defaults to Agent-tool subagents (per-state context isolation). Alternative: direct SDK script calling Sonnet in parallel (simpler to rerun/debug). User can override the default.
4. **Self-consistency disagreement threshold for aborting a full run.** Plan sets this at ~10% of items. Calibration on a real pilot might argue for a different number.

---

**Testing Details** Validation is by spot-checks (rubric transcription against PDF, 2010 total reproduction, inter-rater sanity on 2026 scores), not automated tests. Each spot-check is specified with a concrete failure condition that forces rework of an earlier phase before proceeding.

**Implementation Details**
- Primary inputs: `papers/PRI_2010__state_lobbying_disclosure.pdf` (both 22-item accessibility and 37-item disclosure-law rubrics). Secondary inputs: state portal URLs discovered during Phase 4 snapshot step.
- Document outputs under `docs/active/research-prior-art/results/`. Portal snapshots under `data/portal_snapshots/<state>/<date>/` (symlinked out of the worktree, not committed).
- Code under `src/pri_scoring/` — minimal Python package, `uv`-managed, one scoring module + one orchestrator module + pydantic models.
- CSVs plain-text with header rows. No database.
- Two hard gates: user review at Phase 3→4 (rubric lock) and calibration threshold at Phase 5→6 (Sonnet vs. human). Neither can be skipped.
- Subagents run in parallel in Phase 6. Checkpoint per-state so rate-limit failures don't force full re-runs.
- Rubric is the leverage point. If calibration fails, fix the rubric before the prompt. If rubric can't be sharpened enough, the plan's core assumption is wrong and we revert to human-only scoring.
- Transparency non-negotiable: evidence field is required on every score, calibration performance is published in methodology, raw model outputs are retained alongside adjudicated scores.

**What could change:** See "What could change" section above.

**Questions:** See "Questions" section above — Q1 and Q4 should be resolved before Phase 1 starts.

---

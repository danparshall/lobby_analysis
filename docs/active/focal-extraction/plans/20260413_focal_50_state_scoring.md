# FOCAL 50-State Scoring — Implementation Plan

**Goal:** Produce per-state, per-indicator FOCAL 2024 scores for all 50 US states, output as a single CSV with evidence trails. Sister deliverable to the PRI 2026 re-score; both will be reviewed by Corda Democracy Fellowship collaborators to decide the composite-rubric path forward.

**Originating conversation:** `docs/active/focal-extraction/convos/20260413_focal_indicator_extraction.md`. Upstream: `docs/historical/research-prior-art/convos/20260412_paper-retry-and-scoring-synthesis.md` and `docs/historical/research-prior-art/results/scoring-rubric-landscape.md`.

**Context:** FOCAL (Lacy-Nichols et al. 2024) is a 2024 peer-reviewed rubric — 8 categories × 50 indicators — synthesized from 15 prior frameworks. It overlaps PRI 2010 substantially: both rubrics span statutory-content requirements (PRI 37 / FOCAL 41) and portal-accessibility mechanics (PRI 22 / FOCAL 9 in Openness). The project's explicit decision (2026-04-13) is to score both rubrics independently and let collaborators design any composite from data, not from a-priori rubric reconciliation. PRI's scoring is in flight on `pri-2026-rescore`. This plan covers FOCAL's parallel run.

**Confidence:** High on the rubric (extraction shipped today, validation passed). Medium-high on the approach (mirrors the PRI architecture, which is itself unproven until PRI's pilot lands). Medium on the snapshot-reuse assumption — see Edge Cases.

**Architecture:** Sonnet-subagent scoring (one per state) against locked FOCAL rubric. Snapshots are **read from the existing PRI snapshot tree** at `data/portal_snapshots/<state>/<date>/` — no parallel snapshot infrastructure. A small additive snapshot extension fetches form PDFs and contact-log landings (the only evidence surfaces FOCAL needs that PRI's protocol skipped). Outputs are a per-state per-indicator scoring CSV with evidence quotes/URLs and a short methodology note.

**Branch:** `focal-extraction` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/focal-extraction`).

**Tech Stack:** Markdown for docs; CSV for structured data. Python + `uv` for the scoring pipeline. Claude Sonnet via Agent-tool subagents (one per state). For the additive snapshot pass: `httpx` for PDF downloads, `playwright` only if needed for JS-rendered contact-log pages.

---

## Snapshot situation (as of 2026-04-13)

The PRI snapshot agent has fetched all 50 states into `data/portal_snapshots/<state>/<date>/`, with `manifest.json` per state cataloging URL/role/local_path for each artifact. Artifact roles already captured per state include: `landing`, `registration`, `expenditures`, `bulk_download`, `data_dictionary`, `faq`, `search`, `other`, plus 10–15 `linked` pages (forms index, glossary, statutes, ethics training, etc.). `data/` is a symlink shared across worktrees (PRI, FOCAL, main), so FOCAL scoring reads PRI's snapshots directly with zero copy.

What's missing from this snapshot for FOCAL purposes:

1. **Form PDFs.** PRI fetched the forms-index HTML page but not the actual form PDFs (e.g., CA Form 601–635 family). Form PDFs are the canonical schema for what the law requires reporters to disclose. Useful for both rubrics, essential for FOCAL Descriptors / Revolving Door / Relationships / Financials / Contact log indicators where "is this field on the form?" is the scoring question.
2. **Contact log landings.** Most US states have no contact-log mechanism (those indicators score 0 across the board). Where one exists (executive-calendar disclosures, agency-meeting logs), the landing page is needed. Estimated <10 states.
3. **Sample bulk-download file.** Optional. Useful for confirming machine-readability claims (FOCAL 3.3 sub-conditions) and seeing what columns exist (Descriptors, Financials), but the data dictionary + forms cover most of this from the schema view. Defer unless Phase 4 pilot reveals scoring gaps.

The additive snapshot pass (Phase 2) is bounded: ~3 extra fetches per state, ~150 total, additive into existing `data/portal_snapshots/<state>/<date>/` directories with new role names (`form_pdf_NN.pdf`, `contact_log_NN.html`), appending to the same `manifest.json`.

---

## Testing Plan

Mirrors PRI's validation strategy. Three spot-checks plus one pilot:

1. **Rubric-lock spot-check.** After Phase 1 operationalization (the 7 open questions from the methodology note), the locked scoring rubric must be reviewable by the user. Pick 3 indicators where operationalization required a decision (3.3 decomposition, 2.3 ministerial-diary handling, 1.2 threshold) and confirm the locked text matches the user-approved decision.
2. **LLM self-consistency check.** Each Sonnet scoring run is repeated 3× per state with temperature 0 in separate sessions. Items with disagreement across runs indicate rubric ambiguity, not model flakiness. Disagreement rate >10% across the pilot signals rubric must be re-tightened before the full run.
3. **Pilot evidence spot-check.** Before the full 50-state run, score 3 pilot states (CA, CO, WY — same set as PRI for cross-rubric comparability) and have the user skim the results against the snapshots. The check is: does each score have a real, relevant evidence quote/URL, and was the indicator interpreted as intended?

NOTE: As with PRI, **the rubric is the source of truth, not the scorer.** Pilot defects resolve by sharpening the rubric, not by adjudicating individual scores.

---

## Steps

### Phase 1 — Rubric lock (estimate: 1 session)

The 50 verbatim FOCAL indicators are in `results/focal_2024_indicators.csv` from the extraction phase. Phase 1 here is **operationalization, not transcription** — convert verbatim indicators into machine-applicable scoring questions with explicit evidence criteria.

1. Resolve the 7 open questions documented in `results/focal_2024_methodology.md`:
   - Scoring scheme (recommend binary 0/1 for cross-rubric comparability with PRI; ordinal as alternative if user prefers).
   - Indicator 3.3 decomposition into 3.3a–3.3e (5 sub-conditions: no registration, free, open license, non-proprietary format, machine readable). Each scored independently.
   - Timeliness thresholds (2.1, 2.2, 2.3): what filing cadence scores 1? Recommend "monthly or more frequent = 1" as a clean cut.
   - Indicator 1.2 financial threshold: what dollar amount counts as "low"? Recommend the median lobbyist-registration income threshold across the 50 states (computed in Phase 2).
   - Westminster role translation for 1.3: explicit US-state mapping table (Ministers → governor + cabinet, MPs → state legislators, etc.).
   - Ministerial diaries (2.3, 3.2): rename as "executive calendar disclosure" in the locked rubric, keep the indicator concept.
   - Compound-indicator handling: 3.3 is the only one needing decomposition (already addressed).
2. Write `results/focal_2026_scoring_rubric.csv`. Schema: `indicator_id` (1.1, 1.2, ..., 3.3a-3.3e, ..., 8.11), `category`, `indicator_text` (locked, post-operationalization), `scoring_scale` (binary or ordinal), `scoring_guidance` (explicit evidence criteria for each score level — what constitutes a 1 vs. a 0), `evidence_surface` (which artifact roles in the snapshot the scorer should look at: landing / registration / forms / expenditures / bulk_download / contact_log).
3. Sum: locked indicator count = 54 (50 minus 1 compound + 5 decomposed, assuming only 3.3 splits).
4. Write `results/focal_2026_methodology.md` documenting each operationalization decision with one-sentence rationale. This is the public-facing companion to the rubric CSV.
5. **Gate: present the locked rubric to the user for review.** No Phase 4 without sign-off. The rubric is the primary failure mode.
6. Commit.

### Phase 2 — Additive snapshot pass (estimate: 1 session, mostly wall-clock for fetches)

7. Build a small fetcher script (`src/focal_scoring/snapshot_extend.py`): for each state, read `data/portal_urls/<state>.json` and the existing `manifest.json`, identify form-PDF links from the captured `linked` and `forms` pages, and download up to 2 form PDFs per state (registration form + primary expenditure/activity form). Store as `data/portal_snapshots/<state>/<existing-date>/form_pdf_NN.pdf` and append fetch records to the same `manifest.json` with role `form_pdf`.
8. For each state, search the captured snapshot for contact-log evidence (keyword search on landing/linked pages: "diary", "calendar", "contact", "meeting log", "schedule"). For positive hits, fetch the contact-log landing page and store as `contact_log_NN.html`. For negative results, write a `_focal_no_contact_log.flag` file in the state directory. This makes the absence explicit (FOCAL category 8 will score 0 across these states).
9. Optional: sample bulk-download file. Skip in Phase 2; revisit only if Phase 4 pilot scoring reveals 3.3 sub-conditions are unverifiable from the data dictionary alone.
10. **Hand-spot-check 3 states** (CA, CO, WY) to confirm the additive fetches worked: form PDFs are non-empty, contact-log decision is plausible.
11. Commit only the script and a manifest of what was added per state. Snapshot files themselves are gitignored under `data/`.

### Phase 3 — Scoring pipeline build (estimate: 2–3 sessions)

12. Create `src/focal_scoring/` Python package. Dependencies: `anthropic`, `pydantic`, `pypdf` (for reading form PDFs into text). **Decision: subagents-via-Agent-tool, not direct SDK** — consistent with PRI's architecture and per-session memory in this profile (auto-memory `feedback_prefer_subagents_over_sdk.md`). Confirm with user if PRI ended up choosing differently.
13. Build the scoring function: input = `(state, locked_rubric_csv, snapshot_dir)`; output = one row per indicator with `score`, `evidence_quote_or_url`, `confidence`, `notes`, `source_artifact` (which file in the snapshot dir produced the evidence). Sonnet temperature 0, structured output via pydantic, **indicators delivered one at a time** (not batched) for independent auditability.
14. Build snapshot loader: enumerate `manifest.json` for the state, expose artifacts to the scorer indexed by role. The scorer's prompt routes each indicator to the relevant artifacts via `evidence_surface` from Phase 1.
15. Build subagent orchestrator: one subagent per state, parallel launch, per-state output files. Each subagent receives the locked rubric + snapshot manifest + scoring prompt; emits a state CSV.
16. **Test pipeline on 2 states first** (one pilot, one non-pilot) before launching Phase 4. Verify CSV shape, every score has non-empty evidence, source_artifact references resolve to real files.
17. Commit pipeline. Snapshots themselves remain in `data/` (gitignored).

### Phase 4 — Pilot run (estimate: 1 session)

18. Run pipeline on CA, CO, WY (same set as PRI for cross-rubric comparability).
19. Run self-consistency check: 3× per state at temp 0 in separate sessions. Items with inter-run disagreement on the same snapshot are flagged as rubric-ambiguity issues.
20. **User skims results against the snapshots.** Questions checked:
    - Does every score have a real, relevant evidence quote or URL?
    - Did each indicator get interpreted per Phase 1 operationalization?
    - For 3.3a–3.3e (decomposed compound indicator), are all 5 sub-conditions independently scored against distinct evidence?
21. **Defects resolve in Phase 1 (rubric sharpening), not per-score adjudication.** Re-lock and re-pilot until clean.
22. Commit pilot results + any rubric revisions.

### Phase 5 — Full 50-state scoring (estimate: 1 wall-clock session, hours of model time)

23. With rubric locked post-pilot, launch subagents across remaining 47 states in parallel. Pilot states (CA, CO, WY) stay fixed.
24. Self-consistency check across all 50. Items with inter-run disagreement go to `human_review_queue.csv`.
25. Disagreement rate >10% across states → stop, return to Phase 1. <10% → adjudicate the queue item-by-item with raw model outputs preserved alongside adjudicated scores.
26. Commit final scores CSV: `results/focal_2026_scores.csv`. Schema: one row per `(state, indicator_id)` with `score`, `evidence_quote_or_url`, `source_artifact`, `confidence`, `notes`, `consistency_runs_agreed` (3/3 or fewer).

### Phase 6 — Handoff to collaborator review (estimate: 1 session)

27. Produce `results/focal_2026_summary.md`: per-state totals, per-category sub-totals, distribution analysis (where do states cluster?), comparison-ready format alongside PRI's deliverable. **No composite scoring with PRI in this phase** — that's the collaborator decision.
28. Update `RESEARCH_LOG.md` and `STATUS.md`. Push.
29. Notify Dan/collaborators that both PRI and FOCAL 50-state scorings are complete and ready for review.

---

## Edge Cases

- **PRI snapshot date drift.** PRI snapshotted all 50 states on 2026-04-13. If FOCAL scoring takes >2 weeks of wall-clock to land, snapshot freshness becomes an issue (portals change). Decision rule: if any state's snapshot is >30 days old at the time of scoring, refetch that state's snapshot before scoring. Document refresh dates in the output CSV.
- **PRI snapshot incomplete for a state.** If a state's PRI snapshot is missing key artifacts (e.g., CA's cal-access search is WAF-blocked, returning a 212-byte Incapsula stub), FOCAL scoring of accessibility indicators against that state will be evidence-thin. Allowed output: `score=null, notes="evidence unavailable, see <stub_path>"`. Do not score against the WAF stub.
- **Form PDFs unfetchable.** Some states gate form PDFs behind login or use form-builder web apps with no canonical PDF. In Phase 2, write a `_focal_no_form_pdf.flag` and proceed to score from the registration HTML page alone. Document per-state evidence quality in the output.
- **Compound indicator 3.3 disagreements between sub-conditions.** Most states will satisfy some but not all of 3.3a–3.3e. The total FOCAL score must reflect this granularity — do not collapse 3.3a–3.3e back into a single 0/1 in the final output.
- **Westminster role translation gaps in indicator 1.3.** US states have role categories that don't map cleanly (e.g., independently elected attorneys general, county-level officials with state lobbying overlap). Document per-state mapping decisions in `notes` if non-obvious.
- **Contact log evidence ambiguity.** Some states have *partial* contact-log mechanisms (e.g., agency-specific calendars but no statewide register). Score against the strongest available mechanism with notes; do not aggregate to a single 0/1 unless the indicator inherently requires it.
- **Subagent failures / rate limits during the full-50 run.** Orchestrator must checkpoint per-state completion. A partial failure should not force re-scoring already-completed states. (Same as PRI.)
- **FOCAL indicators that genuinely don't translate to US-state context.** None were flagged `supports_state_application=no` during extraction, but pilot scoring may surface cases where an indicator is structurally inapplicable (e.g., "Director-Generals" has no clean US equivalent). Allowed output: `score=null, notes="indicator not applicable in US-state context"`. Record these for the methodology note.

## What could change

- If PRI's pilot exposes that the Sonnet-subagent architecture has a fundamental flaw (e.g., context-window thrashing, inconsistent evidence selection), FOCAL must inherit the fix before its own pilot. **Recommend: wait for PRI pilot results before starting FOCAL Phase 3.**
- If collaborators decide mid-stream that only the 8-state shortlist matters (not all 50), Phase 5 can stop early. Output schema is unchanged.
- If the additive snapshot pass (Phase 2) reveals that form PDFs are unfetchable for a large minority of states (>15), Phase 1 evidence_surface routing may need to be revised to lean harder on the data dictionary and registration HTML.
- If Sonnet's scoring of compound indicator 3.3 is unstable across runs, the decomposition into 3.3a–3.3e may need to be revisited or made more granular.

## Questions

1. **Subagents-via-Agent-tool vs. SDK.** Default is Agent-tool subagents (consistent with PRI plan and the `feedback_prefer_subagents_over_sdk.md` memory). Confirm before Phase 3.
2. **Wait for PRI pilot before starting FOCAL Phase 3?** Recommended yes — PRI's pilot will surface architecture flaws that FOCAL would otherwise re-discover. Confirm scheduling.
3. **Scoring scheme: binary or ordinal?** Plan defaults to binary 0/1 for cross-rubric comparability with PRI. Ordinal would give more signal but complicates collaborator review.
4. **Self-consistency disagreement threshold.** Plan inherits PRI's ~10% threshold. Calibration on FOCAL pilot may argue for a different number.
5. **Snapshot age refresh threshold.** Plan defaults to 30 days. Confirm.
6. **Bulk-download file sampling (Phase 2 step 9).** Currently deferred. Confirm whether to skip entirely or trigger on Phase 4 pilot evidence gaps.

---

**Testing Details** Validation by spot-checks (rubric-lock review, self-consistency, pilot evidence spot-check). No automated tests; this is an analysis/data-collection task.

**Implementation Details**
- Primary input: `results/focal_2024_indicators.csv` (extraction output, locked).
- Secondary inputs: `data/portal_snapshots/<state>/<date>/` (read-only — PRI's snapshots, shared via `data/` symlink) and `data/portal_urls/<state>.json` (PRI's seed URLs, shared).
- Document outputs under `docs/active/focal-extraction/results/`. Snapshot extensions write into existing PRI directories under `data/portal_snapshots/<state>/<date>/` with `form_pdf_*` and `contact_log_*` role names; gitignored.
- Code under `src/focal_scoring/` — minimal Python package, `uv`-managed: scoring module, snapshot loader, snapshot-extension fetcher, orchestrator, pydantic models.
- One hard gate: user review at Phase 1→2 (rubric lock). Pilot review at Phase 4→5 is iterative, not pass/fail.
- Subagents run in parallel in Phase 5. Per-state checkpointing required.
- Evidence field is required on every score. Raw model outputs retained alongside any adjudicated scores.
- **No PRI-FOCAL composite scoring** anywhere in this plan. Composite is a downstream collaborator decision after both rubrics produce 50-state CSVs.

**What could change:** See section above.

**Questions:** See section above — Q1, Q2, Q3 should be resolved before Phase 3 starts.

---

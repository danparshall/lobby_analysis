# Phase 2 — Statute Retrieval + Baseline Scoring Run

**Goal:** Retrieve 2010-vintage state-statute text for a 5-state calibration subset via Justia, package into statute bundles compatible with the existing scoring pipeline, run the current scorer prompt against them, and measure agreement with PRI 2010 reference scores. Output: a baseline agreement number against which Phase 4 prompt iterations will be evaluated.

**Originating conversation:** [`docs/active/pri-calibration/convos/20260417_calibration_kickoff.md`](../convos/20260417_calibration_kickoff.md)

**Parent plan:** [`plans/20260417_pri_ground_truth_calibration.md`](20260417_pri_ground_truth_calibration.md) — this plan executes that plan's Phase 2 (calibration harness) + Phase 3 (baseline run).

**Previous phase:** Phase 1 Justia audit complete (2026-04-18). 49/50 states eligible for 2010 calibration. See [`results/20260418_justia_retrieval_audit.{csv,md}`](../results/20260418_justia_retrieval_audit.md).

**Context:** The `scoring` branch pilot found that PRI disclosure-law inter-run disagreement is driven by ambiguity between `unable_to_evaluate` and `score=0` when the snapshot corpus only captures portal *summaries* of the law, not the law itself. This branch responds by retrieving the actual statutes and scoring against them. The calibration target — how close our LLM scores need to come to PRI 2010 — is deferred to post-baseline (Phase 3) because PRI did not publish an IRR and we need empirical numbers before setting a threshold.

**Confidence:** Medium. Phase 1 validated the Justia retrieval approach at year-index granularity. Title-page + section-range parsing is a reasonable extension but untested; live section-range pages may have structural variations across states. Expect at least one state-specific parsing surprise.

**Architecture:** Extend the existing `src/scoring/` pipeline (reuse, don't parallel-build). Add `parse_title_page` + `parse_section_range` to `justia_client.py`. Add `retrieve_statute_bundle` to `statute_retrieval.py`. Add `statute_loader.py` mirroring `snapshot_loader.py`. Add `build_subagent_brief` support for `role=statute` artifacts in `bundle.py`. Add `calibrate` subcommand to `orchestrator.py`. Scoring uses the existing scorer prompt unchanged — this produces the **baseline** number the calibration target will be set against.

**Branch:** `pri-calibration` (already set up, off `scoring`). Absolute worktree path: `/Users/dan/code/lobby_analysis/.worktrees/pri-calibration`. Data directory is a symlink to main's `data/`; statute bundles will land at `data/statutes/<STATE>/<YEAR>/`.

**Tech Stack:** Python 3.12, uv, pydantic, requests + beautifulsoup4 (parsing), playwright (Cloudflare clearance, fresh browser per request). All deps already added in Phase 1.

---

## Pre-flight reads (first session picking up this plan)

In order:

1. `STATUS.md` — current branch inventory + "Recent Sessions"
2. `README.md` — project framing
3. `docs/active/pri-calibration/RESEARCH_LOG.md` — this branch's trajectory
4. `docs/active/pri-calibration/convos/20260417_calibration_kickoff.md` — the originating convo; pay attention to the "Session outcome" section at the bottom which captures today's actual execution
5. `docs/active/pri-calibration/results/20260418_justia_retrieval_audit.md` — Phase 1 audit result (49/50 eligible, CO excluded)
6. `docs/active/pri-calibration/results/20260418_justia_retrieval_audit.csv` — the eligibility data
7. `plans/20260417_pri_ground_truth_calibration.md` — master plan (this plan implements its Phase 2 + Phase 3)
8. `plans/20260417_statute_retrieval_module.md` — Phase 1 sub-plan (for module-boundary patterns to mirror)
9. `src/scoring/justia_client.py` — existing parsers + `PlaywrightClient`; you'll extend this
10. `src/scoring/statute_retrieval.py` — existing audit logic; you'll extend this
11. `src/scoring/snapshot_loader.py` — the pattern `statute_loader.py` will mirror
12. `src/scoring/bundle.py` — where statute bundle → subagent brief lives; you'll extend this
13. `src/scoring/orchestrator.py` — existing subcommands + `audit-statutes`; you'll add `retrieve-statutes` and `calibrate`
14. `tests/fixtures/justia/california_2010_gov_title.html` — title page fixture (lists section-range leaves)
15. `tests/fixtures/justia/california_2010_gov_sections_86100_86118.html` — section-range leaf fixture (Political Reform Act Art. 1)
16. `docs/active/pri-2026-rescore/results/pri_2010_disclosure_law_scores.csv` — PRI ground-truth disclosure-law scores
17. `docs/active/pri-2026-rescore/results/pri_2010_accessibility_scores.csv` — PRI ground-truth accessibility scores
18. `papers/text/PRI_2010__state_lobbying_disclosure.txt` — paper text (lines 1120–1250 for methodology detail)

**Dan's working preferences (memory-backed — don't re-learn):**
- Don't write throwaway `scripts/foo.py` with hardcoded values. Extend the `scoring.orchestrator` CLI.
- Subagent dispatch prompts must say "use Read tool only; do NOT subprocess/shell/pdftotext/unzip."
- No `---` separators in chained bash output.
- Rate-limit-safe subagent dispatch is ~4 concurrent.
- Auto-add top-500 PyPI single-purpose mature deps (requests, bs4, etc.). Ask before adding architecture-shapers or heavy deps (see `feedback_dep_approval.md`).

---

## Stopping point before code: calibration-subset selection (DISCUSS WITH DAN)

This is a **user-facing decision** that should not be made silently. Propose 5 states to Dan and get explicit approval. Good selection criteria:

1. **All 5 eligible for 2010 calibration.** Drop CO from consideration (only exclusion).
2. **Weighted toward PRI responders** — the 34 responder states are higher-trust ground truth. At minimum 4 of 5 should be responders.
3. **Span the PRI 2010 disclosure-law score distribution.** Pick from top / upper-median / median / lower-median / bottom quartile so iteration signal isn't dominated by one part of the curve.
4. **Pragmatic pilot state choice.** CA is already deep in the team's context (prior pilot + dry-run); including CA gives us apples-to-apples comparison against the `scoring` branch's portal-based result.

Suggested starter set (verify against `20260418_justia_retrieval_audit.csv` + `pri_2010_disclosure_law_scores.csv`):

- **CA** (rank ~10–15, responder, team familiarity)
- **TX** (rank 4, responder, large-state stress test)
- **WY** (rank 50 — bottom, responder, minimal-statute stress test)
- **NY** (rank 3, responder, upper-quartile)
- **one near-median responder** — e.g., WI (rank 18, Wisconsin, responder) or NE (rank 23, Nebraska, responder)

Present the set + rationale to Dan. He'll approve or adjust. Record the chosen set in the convo file before proceeding.

---

## Testing Plan

This plan has two modes:

**TDD (for implementation):** retrieval parsers, bundle loader, `bundle.py` extension, `calibration.py` agreement metrics, orchestrator subcommands. All tests written before implementation. Tests work against fixture HTML for parsers; fixtures for bundle loader; synthetic inputs for agreement metrics.

I will add parser tests that exercise `parse_title_page` against `california_2010_gov_title.html` (expect 400+ section-range entries) and `parse_section_range` against `california_2010_gov_sections_86100_86118.html` (expect text content with section headers preserved). I will test `retrieve_statute_bundle` as an integration test with a `FakeClient` that returns canned HTML for a known CA title + 2 section-range pages, verifying that a manifest.json with correct sha256, vintage year, and direction is written.

I will add `agreement_metrics` tests with synthetic inputs covering: identical scores (100% agreement), disjoint scores (near-zero), LLM `unable_to_evaluate` vs PRI numeric (counted as disagreement), sub-aggregate rollup of atomic items matching PRI published totals (regression check against 50 known values).

I will add a `calibrate` subcommand integration test: fixture LLM scores + fixture PRI reference → expected agreement report.

**Exploration (for Phase 3 baseline run):** not TDD. Document what was run, what was observed, what constitutes a surprising result.

NOTE: I will write *all* unit/integration tests before I add any implementation behavior.

---

## Phase 2a — Statute retrieval pipeline (~1 day, TDD)

### Task list (bite-sized)

1. Capture two more Justia fixtures if needed:
   - A title page for a state where lobbying lives in a differently-named title (e.g., TX "Government Code" or NY "Legislative Law") to test the parser isn't CA-specific.
   - A section-range leaf from a different state.
   Use `tests/fixtures/justia/_capture.py` — add URLs, rerun, commit. Fresh-browser-per-request is already the pattern.

2. **RED: write parser tests.** In `tests/test_justia_client.py`, add:
   - `test_parse_title_page_ca_gov_returns_section_ranges` — CA Gov title fixture → list of section-range entries (range-string, url, optional chapter/article heading).
   - `test_parse_title_page_extracts_section_numbers` — the ranges have structured start/end section numbers (integers or strings where sections have suffixes like "86100.5").
   - `test_parse_section_range_preserves_statute_text` — CA §§86100-86118 fixture → text output contains known statute phrases ("means any individual" is a canonical definitional phrase in §86100; verify exact match).
   - `test_parse_section_range_strips_navigation_chrome` — text does NOT contain Justia navigation elements ("Find a Lawyer", "Get your case reviewed", footer legal disclaimer).
   - `test_parse_section_range_captures_section_headers` — each section's number and heading are preserved in the extracted text.

3. Run them. Confirm all fail.

4. **GREEN:** implement `parse_title_page(html) -> list[SectionRangeEntry]` and `parse_section_range(html) -> SectionRangeText` in `justia_client.py`. Minimal bs4-based implementations.

5. **RED: write retrieval/bundle tests.** In a new `tests/test_statute_retrieval_bundle.py`:
   - `test_retrieve_statute_bundle_happy_path` — with FakeClient returning canned HTML for a state-title + 2 section-range URLs, `retrieve_statute_bundle` writes `data/statutes/<STATE>/<YEAR>/manifest.json` + `sections/<range>.txt` files. Manifest has `state_abbr`, `vintage_year`, `year_delta`, `direction`, `pri_state_reviewed`, `retrieved_at`, `artifacts` with sha256 + url + local_path.
   - `test_retrieve_statute_bundle_sha256_matches_contents` — after retrieval, sha256 in manifest matches actual file bytes.
   - `test_retrieve_statute_bundle_fails_on_empty_title` — if a title has no section-range entries, raise with a clear error (don't silently write an empty bundle).

6. **GREEN:** implement `retrieve_statute_bundle(client, state_abbr, year, title_slug, dest_dir)` in `statute_retrieval.py`. Takes a title slug (e.g., "gov" for CA) — the per-state mapping of "which title contains lobbying law" is a separate concern (see next task).

7. **Per-state lobbying-title map.** Create `src/scoring/lobbying_titles.py` — a hand-curated dict `{state_abbr: [title_slug, ...]}` that lists the Justia title slug(s) containing lobbying law for each state. For the 5-state calibration subset only, populate these slugs by consulting:
   - Each state's `/codes/<state>/<chosen_year>/` title index (already captured for CA).
   - PRI 2010 paper's footnote 84 (NCSL links) for hints.
   - State-statute-name research (external web browsing via WebFetch if needed).
   Document the provenance (which URL or source) in a comment per state.
   No tests needed — this is static data. But do add `test_lobbying_titles_covers_calibration_subset` to verify all 5 calibration states are keyed.

8. **RED: write `statute_loader` tests.** In `tests/test_statute_loader.py`:
   - `test_load_statute_bundle_validates_manifest` — fixture bundle directory → returns validated StatuteBundle pydantic model.
   - `test_load_statute_bundle_missing_manifest_raises` — directory without manifest.json → FileNotFoundError.
   - `test_load_statute_bundle_sha_mismatch_raises` — tampered section file (sha256 doesn't match manifest) → raises.

9. **GREEN:** implement `src/scoring/statute_loader.py`. Mirror `snapshot_loader.py`'s shape — pydantic model, load function, sha256 verification. Add `StatuteArtifact` and `StatuteBundle` to `models.py`.

10. **RED: write `bundle.py` extension test.** In `tests/test_pipeline.py` (or a new `tests/test_bundle_statute.py`):
    - `test_build_subagent_brief_from_statute_bundle` — given a small StatuteBundle + a rubric, `build_subagent_brief` produces a brief with the statute text embedded and artifact role=statute. Existing snapshot-brief test still passes.

11. **GREEN:** extend `src/scoring/bundle.py` to accept a StatuteBundle where it currently accepts a SnapshotBundle. Union type or overload — keep the snapshot path unchanged. Brief format should make clear to the scorer that the source is statute text, not portal guidance.

12. **RED: write `orchestrator retrieve-statutes` integration test.** In `tests/test_orchestrator_retrieve_statutes.py`:
    - `test_retrieve_statutes_subcommand_produces_bundle` — with monkeypatched PlaywrightClient factory, run `orchestrator retrieve-statutes --state CA --vintage 2010`. Verify `data/statutes/CA/2010/` exists with manifest + sections files.

13. **GREEN:** add `retrieve-statutes` subcommand to `orchestrator.py`. Takes `--state`, `--vintage`, `--output-dir` (default `data/statutes/`), `--rate-limit-seconds`. Uses `lobbying_titles` mapping to decide which title(s) to retrieve per state.

14. Full regression: `uv run pytest`. All new tests green + all 35 existing green.

15. **Live smoke test.** Run `orchestrator retrieve-statutes --state CA --vintage 2010` against real Justia. Verify bundle lands, spot-check manifest + a section file. Commit the bundle artifacts under `data/statutes/CA/2010/` (they're gitignored in data/; but optionally commit the manifest.json for provenance — check with Dan first).

16. **Live run for the 5-state subset.** Retrieve each of the 5 calibration states. 5 states × 5-10 title-range pages each × (browser launch 10s + fetch 10s + rate-limit 2s) ≈ 20-40 min wall time. Monitor for failures; any states with section-range structural variations will surface here and need a parser patch.

17. Commit a checkpoint: retrieval code + commit message listing which 5 states were retrieved and any per-state parsing patches.

### Edge cases for Phase 2a

- Section ranges with suffixes ("86100.5", "86105.1"). These aren't integers; preserve as strings in the SectionRangeEntry model.
- Titles without a flat section-range list — some states organize titles into chapters first, then sub-chapters, before reaching section-range leaves. Handle by recursing into sub-lists until a section-range leaf is found.
- Sections with repealed/renumbered notes. Include them as text; the scorer can interpret.
- Multiple lobbying-relevant titles in one state (e.g., both "Government Code" and "Political Reform Act" as separate titles). `lobbying_titles` dict maps to a list; iterate and combine artifacts into one bundle.
- Justia back-fills partial coverage in older years. If a chosen year is missing the lobbying title, the retrieval will 404 on the title page. Catch and surface per-state — the audit didn't check this (deferred from Phase 1 on purpose).
- A section-range page may redirect (301) to a canonical URL. Playwright follows redirects automatically; verify the final URL in the manifest matches the fetched URL.

---

## Phase 2b — Calibration harness (~half day, TDD)

### Task list

1. **RED: write agreement metrics tests.** In `tests/test_calibration.py`:
   - `test_agreement_metrics_identical` — identical score vectors → 100% agreement.
   - `test_agreement_metrics_full_disagreement` — disjoint scores → near-zero agreement.
   - `test_agreement_metrics_null_handling` — LLM `unable_to_evaluate` vs PRI numeric → counted as disagreement (not missing).
   - `test_agreement_metrics_trust_partition` — given `trust_partition=PRI_RESPONDER_STATES`, computes responder vs non-responder agreement separately.
   - `test_rollup_to_sub_aggregates_disclosure_law` — 61 atomic items per state rolled up to A/B/C/D/E sub-component totals. Assert rollup matches PRI's published sub-component total for each of the 50 known states (regression check against `pri_2010_disclosure_law_scores.csv`).
   - `test_rollup_to_sub_aggregates_accessibility` — 22 atomic items, where Q7_raw is sum of 15 sub-items. Verify against `pri_2010_accessibility_scores.csv`.
   - `test_load_pri_reference_scores_disclosure_law` — loads the published CSV, returns dict{state_abbr → dict{subcomponent_id → score}}.
   - `test_load_pri_reference_scores_accessibility` — same for accessibility.

2. Run them. Confirm all fail.

3. **GREEN:** implement `src/scoring/calibration.py` with `load_pri_reference_scores`, `rollup_our_scores_to_sub_aggregates`, `agreement_metrics`. Pure functions — no I/O except CSV reads.

4. **RED: write `calibrate` subcommand test.** In `tests/test_orchestrator_calibrate.py`:
   - `test_calibrate_subcommand_produces_report` — given fixture LLM-scored CSVs for a 2-state subset + the real PRI reference scores, `orchestrator calibrate --rubric pri_disclosure_law --state-subset CA,TX` produces a markdown report with per-state agreement + responder-partition breakdown.

5. **GREEN:** add `calibrate` subcommand to `orchestrator.py`. Takes `--rubric`, `--run-id` (the LLM scoring run to evaluate), `--state-subset` (comma-separated USPS codes), `--output` (markdown path).

6. Full regression. All green.

### Edge cases for Phase 2b

- PRI sub-component rollup of atomic items: the 2010 rubric CSV already has a `sub_component` column (see `pri_2010_disclosure_law_rubric.csv`). Group by that column. Confirm the sums match PRI's published totals across all 50 states before trusting the rollup (a single mismatch means a transcription error that needs flagging).
- Accessibility Q7_raw: 0–15 integer sum of 15 binary sub-items. Our LLM output has 15 atomic rows; their binary sum must equal Q7_raw.
- Accessibility Q8: "normalized" per paper — check lines 240-250 of the PRI paper for the formula and document in a code comment.
- The 2026 rubric has 37 new accessibility items (Q9–Q16) with no PRI 2010 ground truth. These are **excluded from calibration agreement** — only score the 22 items that have 2010 references.
- PRI's scoring is binary (0/1) per paper methodology. Our scorer may occasionally emit non-binary for gray-area items — coerce to 0/1 at comparison time, with a log.

---

## Phase 3 — Baseline scoring run (~1 day, exploration)

### Task list

1. For each of the 5 calibration states, dispatch 3 temp-0 runs × 2 PRI rubrics using the **current unchanged** `scorer_prompt.md` against the statute bundle (not portal snapshots). That's 5 × 2 × 3 = 30 subagent dispatches. Batches of 4 per rate-limit lessons.
2. Use `orchestrator prepare-run` / `finalize-run` with a new `--source statute` flag (or similar — extend `bundle.py` to route on bundle type). The 3-run self-consistency pattern from the pilot still applies.
3. Each scored CSV lands under `data/scores/<STATE>/<vintage_year>/<run_id>/`.
4. Run `orchestrator calibrate --rubric pri_disclosure_law --state-subset CA,TX,WY,NY,WI --run-id <merged>` and same for `pri_accessibility`. Output: `results/<date>_calibration_baseline.md`.
5. Write up findings:
   - Per-state + per-rubric agreement numbers.
   - Responder-partition breakdown (should be N/A here since all 5 are responders under suggested subset — but the machinery should exist for when non-responders are added in held-out validation).
   - Which items/sub-aggregates show max disagreement.
   - Inter-run disagreement — should be LOWER than the portal-based pilot (statute text is clearer than portal guidance). If not, stop and surface.

### What constitutes a "surprising" baseline result

- Agreement already ≥ 90% on disclosure-law → surface to Dan. Would suggest the pilot's disagreement was entirely snapshot-driven and the current prompt is already calibrated against statutes.
- Agreement < 40% → something bigger is wrong (rubric misinterpretation, statute wrong vintage, rollup bug). Debug before iterating.
- Inter-run disagreement ≥ the 2026-portal pilot's disagreement → the calibration pivot's premise is weak. Stop and surface.

### Stopping point before Phase 4

After the baseline numbers are in, **pause and discuss the convergence target with Dan**. Candidates:

- **Fiat:** e.g., "90% exact agreement on responder states."
- **Bootstrap:** Dan hand-scores 1-2 calibration states, and the target is our-agreement-with-Dan (where Dan's hand-score acts as a second-rater for PRI).
- **Asymmetric:** higher target on responder states, lower on non-responders.

Do NOT proceed to Phase 4 (prompt iteration) without an explicit target.

---

**Testing Details:**

- Unit tests for pure parser functions (no network), pure rollup/agreement functions (synthetic inputs), pure bundle-loading (fixture directories).
- Integration tests for the three new orchestrator subcommands (`retrieve-statutes`, `calibrate`), each with fake/monkeypatched dependencies for deterministic CI.
- Regression: all 35 existing tests continue to pass.
- Behavior-focused — no tests for datastructures or types alone. `parse_section_range` tested by the actual text it returns, not by shape of the returned object.

**Implementation Details:**

- New modules: `src/scoring/statute_loader.py`, `src/scoring/calibration.py`, `src/scoring/lobbying_titles.py`.
- Extended modules: `src/scoring/justia_client.py` (parsers), `src/scoring/statute_retrieval.py` (retrieve function), `src/scoring/bundle.py` (statute bundles), `src/scoring/orchestrator.py` (2 new subcommands), `src/scoring/models.py` (StatuteArtifact, StatuteBundle, SectionRangeEntry, SectionRangeText).
- New pydantic models match the shapes of existing SnapshotArtifact / SnapshotBundle for consistency.
- Statute data layout: `data/statutes/<STATE>/<YEAR>/manifest.json` + `sections/<range>.txt`.
- Rate-limit: ~5s courtesy delay; fresh Playwright browser per request (established in Phase 1).
- Subagent dispatch in batches of 4; prompts must say "Read tool only; no subprocess/shell/pdftotext/unzip."
- Commit after each TDD cycle (not once at the end).

**What could change:**

- Section-range parser may need per-state tweaks. Treat the first state with a parser-surprise as data; document the quirk, patch cleanly, and move on.
- `lobbying_titles` map may need multiple slugs per state (e.g., CA has both Gov Code and — arguably — the Political Reform Act; the Act IS in Gov Code §§81000–91015). Start with single-slug-per-state; expand only if baseline scoring misses obvious provisions.
- If Phase 3 baseline shows agreement ≥ 85% on both rubrics, Phase 4 may not be needed at all. Scope down.
- If Justia's section-range HTML format turns out to have dramatic variation across states, consider a per-state parser dispatch (`parse_section_range_by_state`) — but only if needed.
- The convergence-target value can't be set until after Phase 3. Bake a stopping point at that decision.

**Questions:**

1. **Calibration subset selection** — the suggested set (CA/TX/WY/NY + one median responder) is illustrative. Dan's call on the specific 5.
2. **Statute-bundle commit policy** — full statute text bundles under `data/statutes/` are gitignored (follows `data/portal_snapshots/` pattern). Should we commit the manifest.json files for provenance? Propose: yes (they're small), confirm with Dan.
3. **Scorer prompt source flag** — should the prompt include explicit "this is statute text, not portal guidance" framing? Proposal: yes, add a single sentence to the brief header; the prompt body stays unchanged. Surface this as a minimal scorer-prompt change and commit it separately from any later calibration-iteration changes.
4. **Dispatch architecture** — Phase 3 reuses the scoring branch's subagent-dispatch pattern. No change proposed. If rate-limit reality differs now (2026-04-18+), surface and adjust batch size.

---

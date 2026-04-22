# Statute Retrieval Module — Implementation Sub-Plan

**Parent plan:** `20260417_pri_ground_truth_calibration.md`
**Originating conversation:** `convos/20260417_calibration_kickoff.md`
**Scope:** Phase 1 of the master plan only. Build Justia retrieval + 50-state eligibility audit. Does NOT cover the calibration harness (Phase 2), which is a separate implementation slice once we know the eligible state pool.

**Confidence:** High on architecture (Justia URLs are stable, HTML structure is uniform enough to parse), moderate on per-state robustness (state-code titles and chapter organization vary). TDD against captured fixture pages de-risks the parser.

---

## Goal

Produce `docs/active/pri-calibration/results/20260418_justia_retrieval_audit.csv`: one row per state with 2010 / nearest-year / current-year Justia availability, whether each has the lobbying chapter, and eligibility flags for both calibration (2010-anchored) and 2026-scoring use.

Also: a reusable `orchestrator retrieve-statutes` subcommand that, given a state + vintage year, fetches the state's lobbying-chapter full text and writes a statute bundle with manifest.json.

---

## Module boundaries

Three new modules in `src/scoring/`:

**`src/scoring/justia_client.py`** — pure HTTP client + HTML parsing. No business logic. Given a Justia URL, return structured data.
- `fetch_page(url) -> JustiaPage` — returns html text + sha256 + fetched_at timestamp. Uses a realistic browser UA. Respects a configurable rate-limit (default 1 req/sec). Raises on non-200.
- `parse_state_year_index(html) -> list[YearEntry]` — parse `law.justia.com/codes/<state>/` to extract list of available years.
- `parse_year_title_index(html) -> list[TitleEntry]` — parse `law.justia.com/codes/<state>/<year>/` to extract title list (title number, title name, URL).
- `parse_title_chapter_index(html) -> list[ChapterEntry]` — parse a title page to extract chapter list.
- `parse_section_text(html) -> SectionText` — extract the statute body text from a section leaf page.
- `LOBBYING_TITLE_KEYWORDS` — heuristic for detecting a title that contains lobbying regulation (e.g., "lobby", "ethics", "legislative agent"). Used by `statute_retrieval`, not hardcoded in the client.

**`src/scoring/statute_retrieval.py`** — audit + retrieval business logic.
- `audit_state(state, target_year=2010, tolerance=2) -> StateAudit` — run the eligibility ladder for one state; return structured result.
- `audit_all_states(states, target_year=2010, tolerance=2) -> list[StateAudit]` — runs the audit serially (rate-limited).
- `pick_year_within_tolerance(years_available, target, tolerance) -> (chosen_year, delta, direction) | None` — pure function, chooses closest-to-target year within ±tolerance.
- `find_lobbying_title(title_entries) -> TitleEntry | None` — scan titles for lobbying-related keywords.
- `retrieve_statute_bundle(state, year, dest_dir) -> StatuteBundle` — find lobbying title, walk down through chapters and sections, save text to dest_dir, emit manifest.json.
- `PRI_RESPONDER_STATES: set[str]` — the 34 states from PRI footnote 80. Used to mark trust-weighting in audit output.

**`src/scoring/statute_loader.py`** — loads a previously-retrieved statute bundle (mirrors `snapshot_loader.py`).
- `load_statute_bundle(state, repo_root, vintage_year) -> StatuteBundle` — reads manifest.json, validates, returns pydantic model.
- Not needed for Phase 1 audit per se, but Phase 2 (calibration harness) needs it; worth building now since the manifest shape is decided here.

**New pydantic models** in `src/scoring/models.py`:
- `YearEntry`, `TitleEntry`, `ChapterEntry`, `SectionText` — parser outputs.
- `StateAudit` — per-state audit result.
- `StatuteArtifact`, `StatuteBundle` — bundle models (parallel to `SnapshotArtifact`, `SnapshotBundle`).

**Orchestrator subcommands** in `src/scoring/orchestrator.py`:
- `audit-statutes` — runs audit across all states, emits CSV + markdown summary.
  ```
  uv run python -m scoring.orchestrator audit-statutes \
      --target-year 2010 --tolerance 2 \
      --output-csv docs/active/pri-calibration/results/20260418_justia_retrieval_audit.csv
  ```
- `retrieve-statutes` — retrieves a single state's statute bundle at a given vintage.
  ```
  uv run python -m scoring.orchestrator retrieve-statutes \
      --state CA --vintage 2010 \
      --output-dir data/statutes
  ```
  (Batch retrieval for many states handled by looping this command in a shell or via a future `retrieve-statutes-all` subcommand — YAGNI until Phase 3 needs it.)

---

## Data shapes

### Audit CSV columns

```
state                                 e.g. "CA"
state_name                            e.g. "California"
pri_2010_disclosure_rank              integer 1-50 (from pri_2010_disclosure_law_scores.csv)
pri_2010_accessibility_rank           integer 1-50
pri_state_reviewed                    bool — in PRI's 34-state responder list (footnote 80)
justia_2010_available                 bool
justia_2010_has_lobbying_title        bool | null — null if 2010 not available
justia_nearest_year_to_2010           int | null — if 2010 unavailable, nearest within ±tolerance
year_delta                            int — signed delta from 2010 (negative = pre, positive = post)
direction                             "exact" | "pre" | "post" | "none"
nearest_has_lobbying_title            bool | null
justia_current_year                   int — most recent year Justia hosts for this state
current_has_lobbying_title            bool
eligible_for_calibration              bool — (2010 or nearest within ±tolerance) AND has lobbying title
eligible_for_2026_scoring             bool — current year has lobbying title
notes                                 free text — any detected anomalies
```

### Statute bundle manifest.json shape

```json
{
  "state_abbr": "CA",
  "vintage_year": 2010,
  "year_delta": 0,
  "direction": "exact",
  "pri_state_reviewed": true,
  "retrieved_at": "2026-04-18T10:00:00Z",
  "justia_title_slug": "lobbyists-and-legislative-agents",
  "justia_title_number": "GOV",
  "artifacts": [
    {
      "url": "https://law.justia.com/codes/california/2010/gov/title-9/...",
      "role": "statute_section",
      "section_id": "86100",
      "section_title": "Definitions",
      "local_path": "data/statutes/CA/2010/sections/section_86100.txt",
      "bytes": 4821,
      "sha256": "abc123..."
    }
  ]
}
```

Directory layout:
```
data/statutes/<STATE>/<YEAR>/
  manifest.json
  sections/
    section_<id>.txt
    ...
```

Note: `<YEAR>` is the Justia vintage actually retrieved, not the target year. So if CA target was 2010 and we got 2010 exact, directory is `data/statutes/CA/2010/`. If CO target was 2010 and we got 2016 (nearest), directory is `data/statutes/CO/2016/` with `target_year: 2010` and `year_delta: 6` in the manifest.

---

## TDD test list

Written BEFORE any implementation. All should fail at first.

### `tests/test_justia_client.py`

Fixtures: HTML snippets captured from Justia (checked into `tests/fixtures/justia/`). No live HTTP in unit tests.

- `test_parse_state_year_index_california` — fixture `california_codes_index.html` → parser returns list of YearEntry with 2009, 2010, 2011, ... etc.
- `test_parse_state_year_index_empty_state` — fixture with no year list → returns empty list (not raise).
- `test_parse_year_title_index_ca_2010` — fixture `ca_2010_index.html` → returns titles including Government Code, Penal Code, etc. with URLs.
- `test_parse_title_chapter_index` — fixture for CA Gov Code title → returns chapter list with numbers + slugs.
- `test_parse_section_text_strips_nav_and_footer` — fixture of a section leaf page → returns clean statute body text without Justia nav chrome.
- `test_fetch_page_retries_on_5xx` — monkeypatched HTTP that returns 503 twice then 200 → client retries and returns success.
- `test_fetch_page_raises_on_404` — 404 → raises `JustiaNotFound`.
- `test_fetch_page_uses_realistic_user_agent` — assert the UA header looks like a browser (not `python-requests/...`).

### `tests/test_statute_retrieval.py`

- `test_pick_year_within_tolerance_exact` — years=[2008, 2010, 2012], target=2010 → returns (2010, 0, "exact").
- `test_pick_year_within_tolerance_pre` — years=[2008, 2012], target=2010 → returns (2008, -2, "pre") (both within ±2; prefer pre because pre ≤ PRI scoring vintage).
- `test_pick_year_within_tolerance_post` — years=[2012], target=2010 → returns (2012, 2, "post").
- `test_pick_year_within_tolerance_none` — years=[2016, 2020], target=2010, tolerance=2 → returns None (out of band).
- `test_pick_year_within_tolerance_tie_prefers_pre` — years=[2008, 2012], target=2010 → pre wins.
- `test_find_lobbying_title_matches_keywords` — titles include "Government Ethics Act" → matched.
- `test_find_lobbying_title_no_match` — titles of no interest → returns None.
- `test_find_lobbying_title_picks_most_specific` — both "Ethics" and "Lobbying and Legislative Agents" titles present → picks the more specific one (preference order: exact "lobby" mention > "legislative agent" > "ethics").
- `test_audit_state_happy_path` — monkeypatched client returns CA with 2010 available, Gov Code title with lobbying chapter → StateAudit with eligible_for_calibration=True.
- `test_audit_state_no_2010_but_nearest_available` — monkeypatched CO with years=[2016,2017,2018,...] → StateAudit with 2010 not available, nearest=None (out of tolerance), eligible_for_calibration=False, eligible_for_2026_scoring=True.
- `test_audit_state_nearest_within_tolerance` — years=[2009, 2011, 2012], target=2010 → picks 2009 (pre, delta=-1), eligible.
- `test_audit_state_year_available_but_no_lobbying_title` — year=2010 exists but no matching title → eligible_for_calibration=False, note explains.
- `test_pri_responder_states_has_34_entries` — the hard-coded responder set matches paper footnote 80.

### `tests/test_statute_loader.py`

- `test_load_statute_bundle_validates_manifest` — fixture bundle directory → returns validated StatuteBundle.
- `test_load_statute_bundle_missing_manifest_raises` — directory without manifest.json → FileNotFoundError.
- `test_load_statute_bundle_sha_mismatch_raises` — tampered section file (sha doesn't match manifest) → raises.

### `tests/test_orchestrator_audit_statutes.py` (integration)

- `test_audit_statutes_subcommand_emits_csv` — run orchestrator against fixture Justia (monkeypatched client) for a 3-state mini-set → CSV with expected columns and values exists.
- `test_audit_statutes_subcommand_emits_summary_md` — same, emits methodology md alongside the CSV.

### `tests/test_orchestrator_retrieve_statutes.py` (integration)

- `test_retrieve_statutes_subcommand_produces_bundle` — run retrieve for CA 2010 against fixture Justia → data/statutes/CA/2010/manifest.json + sections/*.txt exist, manifest validates.

### Regression

- `tests/test_pipeline.py` — all 9 existing tests continue to pass.

---

## Implementation order (red → green)

1. Write all tests above (red).
2. Capture Justia HTML fixtures by hand (one-time): fetch CA codes index, CA 2010 index, CA Gov Code title index, one CA section leaf page, one CO codes index (which lacks 2010), one empty-state hypothetical. Save to `tests/fixtures/justia/`.
3. Define pydantic models in `models.py`.
4. Implement `justia_client.py` parser functions. Tests go green one by one.
5. Implement `statute_retrieval.py` audit logic. Tests go green.
6. Implement `statute_loader.py`. Tests go green.
7. Wire `audit-statutes` subcommand. Integration test goes green.
8. Wire `retrieve-statutes` subcommand. Integration test goes green.
9. Run full test suite + existing pipeline tests. All green.

---

## Dependencies to add

- `requests` — HTTP client.
- `beautifulsoup4` — HTML parsing.

I'll ask Dan explicitly before adding these to `pyproject.toml` (per CLAUDE.md: "Prefer third-party libraries instead of rolling your own. Ask before installing.").

Alternative considered: `httpx` (more modern than requests), or parsing HTML with regex (don't — fragile). Going with `requests` + `bs4` because they're battle-tested, well-documented, and what every Python scraper uses; team familiarity likely highest.

---

## Operational notes

- **Rate-limiting:** 1 request/second default. 50 states × ~20 pages each = 1000 pages × ~1.5 sec/page (with courtesy delays + retries) ≈ 25 min of wall time for the full audit. Acceptable.
- **Caching:** the client saves every fetched HTML page to `data/justia_cache/<url-hash>.html` + a fetched_at stamp. Re-running the audit within 24h uses cache; after 24h re-fetches. Rationale: iterative development on the audit logic shouldn't spam Justia.
- **Cloudflare:** Justia is Cloudflare-protected but does NOT block realistic UAs. If this changes mid-project, fall back to WebFetch dispatch via subagents.
- **Single script per Dan's feedback:** the audit is ONE CLI invocation, not 50 separate dispatches. Dan approves once.

---

## What this sub-plan does NOT cover

- Calibration harness (master plan Phase 2).
- Scoring pipeline integration (master plan Phase 3+).
- Multi-state parallelization for retrieval (master plan Phase 6; not needed for Phase 1 audit since audit is only reading index pages).
- Section-text extraction fidelity (acceptable if Justia-formatted statute body passes through clean; no OCR, no PDF parsing).

These land on subsequent sub-plans once the Phase 1 audit output is in and we know the calibration state pool.

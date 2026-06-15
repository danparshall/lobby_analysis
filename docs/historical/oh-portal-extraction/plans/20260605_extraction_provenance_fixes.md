# OH Extraction Provenance Fixes — Implementation Plan

**Goal:** Make each extracted `LobbyingFiling` faithful to its source: (Part 1) populate `raw_text` deterministically in code instead of trusting the model to echo it, and (Part 2) capture the true OLAC regime (legislative / executive / retirement) per filing instead of hardcoding "legislative".

**Originating conversation:** [docs/active/oh-portal-extraction/convos/20260605_oh_discover_all_and_slice_validation.md](../convos/20260605_oh_discover_all_and_slice_validation.md)

**Context:** The 300-filing validation slice surfaced two provenance defects. (1) `raw_text` (the audit field) was missing on ~64% of extracted filings — root-caused to it being an *optional model-emitted* field, omitted even on trivial nil filings (71% of those lack it), so not a truncation issue. When present it is byte-identical to `html_to_aer_text(raw.html)` (verified EXACT match on filing 1509340), i.e. the model is re-transcribing text the pipeline already computes. (2) The agent-axis crawl pulls AERs across all three OH disclosure regimes (~86% legislative / ~13% executive / ~1% retirement in the raw-text subsample), but `pipeline.py` runs every one through the *legislative* brief and stamps `regime="legislative"`.

**Confidence:** High for Part 1 (root-caused with a verified byte-identical comparison; fix is deterministic). High that Part 2's problem is real (regimes observed in the extracted data); Medium on the exact OLAC category encoding (L/E and the retirement letter must be confirmed against live pages).

**Architecture:** Part 1 — factor the post-API filing assembly into a pure function, set `raw_text = aer_text` there, and strip `raw_text` from the tool `input_schema` so the model no longer emits it. Part 2 — add the OLAC "Category" column to discover's `FiledForm` + TSV, map it to a regime, thread that regime through `batch` → `extract_one_filing` → `extraction_run.json`, and (interim safety) flag/segregate non-legislative filings rather than silently running them through the legislative brief.

**Branch:** `oh-portal-aprime-batch` (worktree: `.worktrees/oh-portal-aprime-batch/`). All paths below are repo-root-relative to that worktree.

**Tech Stack:** Python 3.12, Pydantic v2, Anthropic SDK (tool-use), BeautifulSoup, pytest, `uv`.

---

## Testing Plan

**Part 1 (`raw_text`):**
- **Unit (pure, no mocks):** new function `assemble_filing(tool_input: dict, aer_text: str, provenance) -> LobbyingFiling`. Two tests: (a) when `tool_input` *omits* `raw_text`, the returned `filing.raw_text == aer_text`; (b) when `tool_input` *includes* a different `raw_text` value, the returned `filing.raw_text` is still the code-supplied `aer_text` (code is authoritative, model value ignored). These test the actual behavior — source-text wins, regardless of what the model emitted.
- **Unit (pure):** `build_tool_schema()` excludes `raw_text` — assert `"raw_text" not in build_tool_schema()["properties"]` AND a normal field (e.g. `"positions"`) is still present (guards against nuking the whole schema).

**Part 2 (regime):**
- **Unit (parser, matches existing convention in `test_oh_portal_discover.py`):** extend the existing `FORMS_FILED_HTML` fixture (it already has Category `L` and `E` rows) — assert `parse_forms_filed` now returns each row's `category`, and that a `category_to_regime` mapping yields `L→legislative`, `E→executive`, (and `R→retirement_system` once confirmed), with an unknown/blank category → `None` (not a silent "legislative" default).
- **Unit:** `extract_one_filing` stamps the regime it is given (pass `regime="executive"` → `extraction_run.json["regime"] == "executive"`), instead of the module constant.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Part 1 — Code-populate `raw_text`, drop it from the model schema

1. Write the failing unit test for `assemble_filing` omitting `raw_text` → `filing.raw_text == aer_text`. (`tests/test_oh_portal_extract.py`, new file.)
2. Write the failing unit test for `assemble_filing` with a *conflicting* model `raw_text` → code value wins.
3. Write the failing unit test for `build_tool_schema()` excluding `raw_text` but keeping `positions`.
4. Run them — confirm they fail because the functions don't exist yet (not import typos).
5. In `src/lobby_analysis/oh_portal/extract.py`, add `build_tool_schema()` — `schema = LobbyingFiling.model_json_schema(); schema.get("properties", {}).pop("raw_text", None)` then return `schema`. (`raw_text` is optional, so it won't be in `required`; no further edit needed — assert this in a quick check.)
6. In `extract.py`, add `assemble_filing(tool_input, aer_text, provenance)` factoring out current lines 85-88: validate → set `filing.raw_text = aer_text` → set `filing.provenance = provenance` → return.
7. Rewire `extract_oh_legislative_filing` to use `build_tool_schema()` for the tool's `input_schema` and `assemble_filing(...)` for the post-response assembly (pass the already-computed `aer_text`).
8. Run the new tests — confirm green.
9. Run `uv run pytest -k oh_portal -q` — confirm the existing 21 still pass.
10. Commit: `oh_portal: code-populate raw_text from source; drop it from model schema`.

## Part 2 — Capture and stamp the true regime

11. Write the failing parser test: `parse_forms_filed` returns `category` for each row (extend the existing fixture assertions).
12. Write the failing test for `category_to_regime` (L/E/R → regime; unknown → None).
13. Write the failing test: `extract_one_filing(..., regime="executive")` stamps `"executive"` in `extraction_run.json`.
14. Run them — confirm they fail for the right reason.
15. In `src/lobby_analysis/oh_portal/discover.py`: add `category` to the `FiledForm` dataclass, populate it in `parse_forms_filed` (the Category column — verify its index against a real `FormsFiled` page), add a `category_to_regime` mapping, and add a `regime` column to `TSV_HEADER` + the row dicts.
16. In `src/lobby_analysis/oh_portal/batch.py`: when reading the discover TSV, carry the per-row `regime` alongside the URL, and pass it to `extract_one_filing`.
17. In `src/lobby_analysis/oh_portal/pipeline.py`: replace the module-level `REGIME = "legislative"` with a `regime` parameter on `extract_one_filing` (default `"legislative"` for back-compat with the single-URL CLI), and stamp the passed value into `run_meta["regime"]`.
18. **Interim safety for the wrong-brief problem:** in `extract_one_filing`, if `regime != "legislative"`, append an `extraction_warnings` entry ("extracted with legislative brief; <regime> brief not yet implemented") and/or have `batch` skip non-legislative rows by default behind a `--include-nonlegislative` flag. Decide with the user (see Questions).
19. Run the new tests + `uv run pytest -k oh_portal -q` — confirm green.
20. Commit: `oh_portal: capture OLAC regime in discover; stamp true regime per filing`.

## Adjacent cleanup (optional, same code, low risk)

21. While in `discover.py`, fix the doubled cache path (task #8): `_discover_dir` does `data_dir / "oh_portal" / "discover"` but `data_dir` already ends in `oh_portal` → cache lands at `data/oh_portal/oh_portal/discover/`. Drop the extra segment, and **migrate the existing cache** (`git mv`/`mv` the doubled dir up one level) so the ~3k cached pages aren't re-fetched. Separate commit. Skip if it risks scope creep.

---

**Testing Details:** The Part 1 tests assert the *behavior* "the persisted audit text equals the fetched source text, independent of what the model returned" — the conflicting-value test is the one that proves code authority (a model that paraphrases can't corrupt the audit field). No API mocking: `assemble_filing` is pure over a fixture `tool_input` dict + a known `aer_text` string. The Part 2 parser tests reuse the real captured OLAC markup already in the test fixture; the regime-stamp test asserts the sidecar metadata reflects the input, not a constant.

**Implementation Details:**
- `aer_text` is already computed at `extract.py:47`; Part 1 reuses it — no new fetch/parse.
- Keep `raw_text` on the `LobbyingFiling` model (so code can set it); only remove it from the *tool* schema the model sees.
- Dropping `raw_text` from the schema also saves output tokens on every call (relevant to the 45K full run / issue #35).
- `category_to_regime`: `L→legislative`, `E→executive`, `R→retirement_system` — **confirm the letters against live OLAC pages before trusting**, especially retirement.
- Don't default unknown categories to `legislative` — that's the bug we're removing. Use `None` + a warning.
- This plan is independent of issue #35 (the Batches-API full-run build); do it first so the eventual full run produces faithful records.

**What could change:**
- If live OLAC `FormsFiled` pages encode the category differently than the `L`/`E` test fixture (e.g. full words, or retirement under a different column), Part 2 step 15 changes accordingly.
- If executive/retirement AER page structure is close enough to legislative that the legislative brief extracts them acceptably, step 18's segregation may be relaxed — but that needs a small validation pass (extract a few known executive AERs and eyeball them).

**Questions:**
- Part 2 step 18: for non-legislative filings right now, prefer (a) extract-with-warning, or (b) skip-by-default behind a flag? (Default recommendation: skip-by-default + warning, so the corpus stays trustworthy until exec/retirement briefs exist.)
- Should `raw_text` (code-populated, possibly large) stay inline in `filing.json`, or move to a sidecar to keep the JSON lean? (The raw HTML is already saved separately under `data/oh_portal/raw/...`.)

---

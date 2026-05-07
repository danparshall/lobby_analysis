# OH (A') Single-Filing Round-Trip Implementation Plan

**Goal:** Drive one real OH legislative-agent Activity & Expenditure Report from OLAC through fetch → LLM extract → fully-populated `LobbyingFiling` JSON, hand-validated against the source PDF.

**Originating conversation:** [`docs/active/oh-portal-extraction/convos/20260507_oh_a_prime_brainstorm.md`](../convos/20260507_oh_a_prime_brainstorm.md)

**Context:** Track B has been in scoping since 2026-04-30. The (A') deliverable is the smallest test of whether the v1.3 `LobbyingFiling` schema fits OH reality end-to-end. It exists to surface schema-fit problems (and any Anthropic-SDK / tool-use integration friction) *before* we scale to (B') batch extraction. It is intentionally not generalizable — OH-specific, regime-specific, single-sample.

**Confidence:** Exploratory. We have not run an LLM extraction on a real OLAC PDF before. We do not know whether OLAC PDFs are clean text or scanned images, whether the SDK's tool-use cleanly supports `LobbyingFiling`'s nested optionals/discriminated unions, or what schema gaps will surface. Most steps are TDD-able; the "did the round trip work" check is necessarily one real LLM call against one real PDF.

**Architecture:** Single Python module under `src/lobby_analysis/oh_portal/`. One fetcher, one extraction-brief builder, one extractor that calls the Anthropic SDK with a tool-schema generated from `LobbyingFiling`. Output is `LobbyingFiling.model_dump_json()` plus an `extraction_run.json` sidecar. Hand-validation is a markdown table in `results/`.

**Branch:** `oh-portal-extraction` (worktree at `.worktrees/oh-portal-extraction/`)

**Tech Stack:** Python 3.12, `requests` (already a dep), `pydantic` (already a dep), `anthropic` (NEW dep — flagged below), `claude-opus-4-7` for parity with Track A.

---

## Testing Plan

I will add a unit test for the extraction-brief builder that ensures, given a regime label and sample metadata, the returned brief contains: the regime's statute citation, a non-empty field-glossary section, and an explicit "leave fields null when not stated" instruction. The test asserts on substring presence in the rendered prompt — i.e., on **observable behavior** (what the LLM sees), not on data structure shape.

I will add a unit test for the provenance builder that ensures the constructed `Provenance` has all five required fields (source URL, sha256, fetched-at timestamp, extractor identity, model ID) and round-trips through `Provenance.model_validate_json()` cleanly. This tests that we *populate* provenance correctly from real fetch metadata, not that the Pydantic class itself works.

I will NOT add mocked-LLM extraction tests. Per `skills/testing-anti-patterns/SKILL.md`, those test the mock, not the system. The "did the extraction round-trip work" verification is the real LLM call against the real PDF, recorded in the validation results doc.

I will NOT add integration tests that hit live OLAC. They are slow, externally dependent, and the pre-existing `data/portal_snapshots/CA/...` fixture-failure pattern (3 currently failing tests on `main`) shows what happens when the test suite assumes laptop-local data.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Tasks

**Phase 0 — Setup**

1. Verify `data/oh_portal/` is not tracked by git: run `git check-ignore -v data/oh_portal/` from the worktree. If it doesn't match an existing rule, append `data/oh_portal/` to `.gitignore` and commit. (`data/compendium/` is now tracked, so the gitignore is path-specific — don't assume `data/` is fully ignored.)
2. Add `anthropic>=0.40` to `pyproject.toml` `[project.dependencies]`. Run `uv sync --extra dev`. This is a NEW dep — flag in the next weekly update so Dan + Gowrav are aware. If team feedback prefers matching Dan's subagent-dispatch pattern (see "What could change" below), revisit before merging this branch.
3. Pick the (A') sample. From a browser, navigate OLAC's public search at https://www2.olig.ohio.gov/lobbying-search-public.aspx (or current OLAC URL — verify before relying). Filter to: regime = legislative agent, year = 2024 or 2025, has activity. Pick a mid-sized filer (one whose Activity & Expenditure Report has 5–20 bills/issues listed and 5–20 expenditure lines — avoid empty filings and avoid 50-page mega-filings). Record the report ID and PDF URL in `results/20260507_a_prime_sample_selection.md` with selection rationale.

**Phase 1 — Tests first**

4. Create `tests/test_oh_portal_extraction_brief.py` with one failing test for `build_oh_legislative_brief(sample_meta) -> str`. Test asserts the returned string contains: `"ORC"` (statute citation), the substring `"position"` (a `LobbyingFiling` field name), and the substring `"null when not stated"` (the explicit "don't guess" instruction).
5. Run `uv run --active pytest tests/test_oh_portal_extraction_brief.py -v` and confirm it fails with `ImportError` (module doesn't exist yet).
6. Create `tests/test_oh_portal_provenance.py` with one failing test for `build_provenance(fetch_meta) -> Provenance`. Test asserts the returned `Provenance` has non-null source URL, sha256, fetched-at, extractor identity, and model ID, and round-trips through `model_dump_json()` + `model_validate_json()`.
7. Run pytest on the new file; confirm it fails with `ImportError`.
8. Commit the failing tests: `oh_portal: failing tests for extraction_brief + provenance`.

**Phase 2 — Implementation**

9. Create `src/lobby_analysis/oh_portal/__init__.py` (empty) and `src/lobby_analysis/oh_portal/extraction_brief.py` with a minimal `build_oh_legislative_brief()` that returns a string covering the three asserted substrings. Re-run pytest; the brief test should pass.
10. Create `src/lobby_analysis/oh_portal/provenance.py` with a `build_provenance(fetch_meta)` function returning a `Provenance` instance. Re-run pytest; the provenance test should pass.
11. Run the full suite: `uv run --active pytest`. Confirm 305+/3-pre-existing-failures (the `data/portal_snapshots/CA/...` fixture errors are unrelated and pre-existing — do not chase them).
12. Commit: `oh_portal: implement extraction_brief + provenance`.
13. Create `src/lobby_analysis/oh_portal/fetch.py` with `fetch_olac_pdf(url) -> Path`. Behavior: GET with Chrome UA per Dan's snapshot pattern, fail loudly on non-200 (no retry), write bytes to `data/oh_portal/raw/<report_id>/<fetched_at_iso>/raw.pdf`, write sibling `meta.json` with URL/sha256/timestamp/content-type/HTTP status, return the raw.pdf Path. No fancy abstractions — one function.
14. Create `src/lobby_analysis/oh_portal/extract.py` with `extract_oh_legislative_filing(pdf_path, brief, provenance) -> LobbyingFiling`. Behavior: call `anthropic.Anthropic().messages.create()` with `claude-opus-4-7`, attach the PDF as a document block, pass a tool whose `input_schema` is generated from `LobbyingFiling.model_json_schema()`, and require the model to call that tool. Validate the tool-call's `input` through `LobbyingFiling.model_validate(...)`. Attach the passed-in `provenance` to the returned filing. On any error (HTTP, tool-call missing, Pydantic validation fail), dump the full response to `data/oh_portal/extracted/<report_id>/<run_id>/error.json` and raise — no graceful fallback at (A') scale.
15. Create `src/lobby_analysis/oh_portal/__main__.py` that takes a URL on the CLI, runs fetch → brief → extract → write JSON, and prints the output path. Single-file script, ~30 lines.
16. Commit: `oh_portal: fetcher, extractor, CLI entrypoint`.

**Phase 3 — End-to-end run + validation**

17. From the worktree, run `uv run --active python -m lobby_analysis.oh_portal <SAMPLE_URL>`. Capture stdout (output JSON path). If it crashes, debug and fix; do not retry blindly.
18. Open the source PDF and the emitted JSON side-by-side. For each populated field in the JSON, tag it **CORRECT / WRONG / MISSING / SCHEMA-GAP** in `results/20260507_oh_a_prime_validation.md`. Use the provenance header per the `update-docs` skill.
19. Compute summary stats: % CORRECT, count of WRONG, count of MISSING, count of SCHEMA-GAP. If CORRECT < 80%, decide whether the issue is prompt-fixable or model-limited; either way, document in the convo summary before iterating.
20. Append session entry to `RESEARCH_LOG.md` (newest first).
21. Append one-liner to `STATUS.md` Recent Sessions.
22. Commit: `oh_portal (A'): end-to-end run on <sample id> + validation`.
23. Push: `git push origin oh-portal-extraction`.

**Phase 4 — Hand-off / graduation gate**

24. Schema-gap rows in the validation table: write a one-paragraph proposal per gap in the convo summary (NOT in commits). Flag for Dan + Gowrav at next weekly sync. Do NOT bump the schema unilaterally.
25. If validation passes graduation gate (no fatal mismatch + team consensus on any gaps), open a new convo file `convos/20260514_b_prime_kickoff.md` (or whenever the next session lands) and start brainstorming (B').

---

## Edge cases

- **PDF is image-only / scanned.** OLAC's older PDFs may be scanned. Fall back to the HTML detail page once. If both fail, swap sample. Do not introduce OCR at (A') scale.
- **Anthropic SDK tool-use rejects `LobbyingFiling` schema.** The model has nested optionals and `Literal` enums. If `model_json_schema()` produces a tool-input schema the SDK rejects, simplify by emitting a flat dict from the LLM and calling `LobbyingFiling.model_validate(dict)` post-hoc. Document the workaround in the convo summary; this is a real signal about model-vs-SDK fit.
- **OLAC requires a session cookie / CAPTCHA.** Dan's 2026-04-13 snapshot didn't flag this, but he was scraping discovery pages, not per-report PDFs. If the fetch fails with a redirect to a login page, document it in the sample-selection results doc and either (a) find a publicly downloadable equivalent or (b) flag as a Track B blocker for team discussion.
- **Report URL is not stable.** OLAC may serve PDFs through a session-bound URL (e.g., `download.aspx?token=...`). If so, record the *report ID* and the *search query that produces it*, not just the URL — future re-runs need a path back.
- **Provenance attachment fails.** `Provenance` is a top-level `LobbyingFiling` field per `src/lobby_analysis/models/provenance.py` and `filings.py`. Verify before extraction; if the field doesn't exist where expected, surface in the convo summary as a possible v1.4 gap.

---

## Open questions

- Does the team prefer the Anthropic SDK or Dan's subagent-dispatch pattern (CLI invocation writing to JSON)? The plan as drafted uses the SDK; switching is a 1–2 hour refactor at (A') scale but a meaningful pattern divergence at (B') scale. **Worth raising before Phase 2 ships.**
- What's the canonical `regime` enum value Dan adopted for OH legislative-agent in `statute-extraction`? Strings like `"legislative"`, `"legislative_agent"`, `"OH_LEGISLATIVE"` are all plausible. Read `src/lobby_analysis/models/state_master.py` on `origin/statute-extraction` (without merging) to align *before* writing the extraction brief.
- Is there a sanctioned location for new packages — `src/lobby_analysis/oh_portal/` per this plan, or `src/scoring/oh_portal/`? Existing convention puts pipeline code in `src/lobby_analysis/` and harness/scoring code in `src/scoring/`; the plan follows that. Confirm with Dan if uncertain.

---

**Testing Details:** Two tightly scoped unit tests — one for the extraction brief (asserts substring presence in the rendered prompt; tests *what the LLM sees*, not data shape), one for the provenance builder (asserts populated-field correctness on a real fetch-metadata input; round-trips JSON). The end-to-end behavioral test is one real LLM call against one real OLAC PDF, with hand-validation in `results/`. Mocked-LLM extraction-quality tests are explicitly out of scope per `testing-anti-patterns`.

**Implementation Details:**
- New module: `src/lobby_analysis/oh_portal/` (`__init__.py`, `extraction_brief.py`, `provenance.py`, `fetch.py`, `extract.py`, `__main__.py`).
- New tests: `tests/test_oh_portal_extraction_brief.py`, `tests/test_oh_portal_provenance.py`.
- New dep: `anthropic>=0.40` in `pyproject.toml`.
- New gitignore entry: `data/oh_portal/` (verify first).
- Output landing (gitignored): `data/oh_portal/raw/<report_id>/<fetched_at_iso>/{raw.pdf,meta.json}`, `data/oh_portal/extracted/<report_id>/<run_id>/{filing.json,extraction_run.json}`.
- Branch deliverables (committed): convo summary, this plan, validation results doc, RESEARCH_LOG entry, STATUS.md one-liner.
- Use `claude-opus-4-7` to match Track A's model choice.
- Provenance fields populated: source URL, sha256, fetched-at ISO timestamp, extractor identity (`oh-portal-extraction/v0.1`), model ID (`claude-opus-4-7`), prompt sha256.
- Hand-validation tagging: CORRECT / WRONG / MISSING / SCHEMA-GAP, summarized in the results doc with per-tag count.
- Definition of done: the four conditions in the convo summary's "Decisions Made" section.

**What could change:**
- If the team prefers subagent-dispatch over the Anthropic SDK, Phase 2 swaps `extract.py` for a CLI subprocess invocation against a `claude` runner. Tests of `extraction_brief` and `provenance` are unchanged.
- If `LobbyingFiling.model_json_schema()` is too complex for tool-use, fall back to plain JSON output + post-hoc Pydantic validation (documented in edge cases). Implementation differs; behavior contract is the same.
- If the OH SMR converges quickly during this work (Dan finishes the other 3 chunks of `statute-extraction`), (A')'s validation can opportunistically cross-check populated fields against the SMR's `field_requirements` for legislative regime — strengthens the result without changing the plan's definition of done.
- If schema gaps surface (likely), a v1.4 conversation lands in the next weekly sync; (B') waits on that consensus.

**Questions:**
- Convo summary's open question about v1.4 schema-gap handling protocol — RFC-style or convo+review? Raise at next weekly sync.
- Are there OH-specific filing types the team wants (A') to NOT cover (e.g., late filings, amendments)? Plan currently picks an unambiguous Activity & Expenditure Report from a normal filer; amendments are deferred to (B') by virtue of the sample-selection criteria.

---

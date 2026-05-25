# 20260514 — Retrieval v2 T1 desktop run + fixture decoupling

**Date:** 2026-05-14
**Branch:** `extraction-harness-brainstorm`
**Predecessor convo:** [`20260514_retrieval_implementation.md`](20260514_retrieval_implementation.md) (shipped retrieval_v2 module at T0; T1 deferred to desktop)
**Concurrent session:** another agent ran brief-writer brainstorm in parallel ([`20260514_brief_writer_brainstorm.md`](20260514_brief_writer_brainstorm.md)) — no file overlap, clean fast-forward at commit time.

## Summary

Picked up the T1 smoke gate that the laptop session explicitly deferred to a desktop machine with `ANTHROPIC_API_KEY` set. Ran `pytest tests/test_retrieval_v2_integration.py` against the real Anthropic Citations API: **3/3 passed in ~21s, ~$0.06 spent** (three separate `messages.create` calls, one per test function). Real API attaches citations to text blocks, fires `record_cross_reference` tool calls, and the parser yields a valid `RetrievalOutput` with non-empty `evidence_spans`. T1 gate cleared.

**Then 3 parser unit tests went red against the now-overwritten fixture** — exactly the failure mode the laptop convo's "Open Questions" section flagged as a pre-known risk. Diagnosis: NOT a parser bug; **test design coupling**. The integration test's side-effect-write to `sample_response.json` (the same file parser unit tests consume) caused hand-crafted-shape-specific assertions to break against the new real-shape data. Per the plan's Phase 7 "pause-and-surface, don't silently patch" directive, surfaced to user with full diagnosis and three structural options. User locked **Option A: split the fixture paths.** Executed as a single commit (`5f262e9`).

After fix: parser unit suite back to 8/8 green; full retrieval_v2 unit suite 48/48; T1 re-run against the new path also 3/3 green. The real-API response file is now gitignored (`sample_response_real.json`) to prevent multi-committer churn; the hand-crafted parser fixture is preserved at `sample_response_handcrafted.json` (md5 `d2e3fe0a…` unchanged from laptop session).

## Topics Explored

- **Concurrent-session sanity at session start.** Branch `extraction-harness-brainstorm` had 21 unpushed laptop commits since main; another live session pushed brief-writer brainstorm docs (`c9419e0`) mid-session. Fast-forwarded cleanly with no file overlap. 6 active `claude` PIDs visible via `ps`; coordinated by working on disjoint file sets.
- **Hand-crafted vs real-API response shape on `tiny_statute.txt`.** Real has 5 content blocks (1 `thinking` + 3 `text` + 1 `tool_use record_cross_reference`); hand-crafted has 7 (3 `text` + 1 `tool_use record_cross_reference` + 2 `text` + 1 `tool_use record_unresolvable_reference`). Real response also carries new top-level keys (`container`, `stop_details`, `stop_sequence`) not present in the hand-crafted; parser handles them transparently (ignores).
- **Three parser-unit-test failure modes from fixture swap.**
  1. Hardcoded literal assertion: `assert any("§311.005" in span.cited_text …)` — real fixture's citation is `§99.005` (from `tiny_statute.txt`). Pairing works; the test pinned to a string that no longer exists.
  2. `out.unresolvable_references[0]` → `IndexError`: real fixture has zero unresolvable refs (agent didn't emit any on the tiny 2-sentence statute, because there *are* none).
  3. `len(out.unresolvable_references) == 1` → `0 != 1`: same root cause.
- **Why the unresolvable-ref code path can't be live-tested on `tiny_statute.txt`.** The fixture has 2 obvious cross-refs (`§99.005`, `§99.010`); nothing genuinely unresolvable. To exercise that code path against real API, would need a deliberately-messy statute fixture (phantom section reference, ambiguous "the act," etc.). Not in scope this session.
- **Permission-prompt friction with `.venv/bin/pytest`.** User flagged mid-session that they were getting "a bazillion permission requests." Root cause: `Bash(pytest *)` allows only fire when the command literally *starts* with `pytest`; `.venv/bin/pytest` doesn't match. Verified `uv run pytest` from inside the worktree resolves to the worktree's `.venv` correctly (not main's, despite parent shell's `VIRTUAL_ENV=...`). Switched remaining session calls to `uv run`.

## Provisional Findings

- **Real Anthropic Citations API behaves as the plan-author predicted.** Citations attach to text blocks, tool_use blocks fire after cited text, parser's polymorphic dict/SDK access works on real `Message` objects. No 400s, no auth issues, no schema drift in tool-use validation. T1 gate cleared on first try.
- **Opus 4.7's adaptive `thinking` block is in real responses.** Was untested against real API on the laptop (hand-crafted fixture had none). Parser already passes it through (matches plan's "thinking, server_tool_use pass through"); confirmed empirically here. Worth a note in `parser.py`'s docstring if not already present (haven't checked).
- **Plan-author's "side-effect surfaced for review" was vindicated on first real run.** The convo's pro/con argument explicitly anticipated this — con bit. Fix is structural (path decoupling), not gating-with-`if not exists`.
- **Cost: ~$0.06 per full T1 run** (3 API calls — not 1). Plan estimate "~$0.02/run" was per-call. Not a blocker; T1 will continue to run cleanly on `uv run pytest` whenever the desktop runs the suite.

## Decisions Made

- **Option A locked: split fixture paths.** Hand-crafted at `sample_response_handcrafted.json` (committed; consumed by parser unit tests; exercises edge cases real API may not naturally produce — mixed tool types, multi-tool buffer reset). Real-API capture at `sample_response_real.json` (gitignored; T1 writes here as local-inspection aid; no test consumes it).
- **Rejected B (gate the write with `if not exists`)** and **C (live with breakage).** A is the only design that preserves unit-test invariants while keeping T1 as a live API exercise.
- **Did NOT add the optional "shape-tolerant real-fixture test"** under YAGNI. T1 itself tests parser against real-API on every desktop run; an additional file-loading shape-tolerant test would be redundant and would re-introduce a fixture-file-dependent test path. Surfaced as a future option; not added.
- **Did NOT silently patch the parser or dumb down the unit tests** to match the new fixture shape. Both would have lost real signal (parser is correct; unit tests' invariants are real-coverage of mixed-tool / multi-tool behavior).
- **Permission-prompt fix:** switched to `uv run pytest` / `uv run ruff` for the rest of session. Verified worktree venv resolution.

## Results

- **Single code commit:** `5f262e9 retrieval_v2: decouple parser test fixture from integration write path` — renamed `sample_response.json` → `sample_response_handcrafted.json` (100% similarity per git), added gitignore rule for `sample_response_real.json`, updated `FIXTURE_PATH` in `tests/test_retrieval_v2_parser.py` and `SAMPLE_RESPONSE_PATH` + docstring in `tests/test_retrieval_v2_integration.py`.
- **Tests state:**
  - `test_retrieval_v2_parser.py`: 8/8 pass (was 5/8 after T1 fixture write; back to 8/8 after decoupling)
  - `test_retrieval_v2_integration.py`: 3/3 pass on both T1 runs (pre- and post-decoupling)
  - Full `retrieval_v2` unit suite: 48/48 pass
- **No results files generated this session** (no analysis outputs to save).

## Open Questions

- **Shape-tolerant real-fixture parser test?** Could add a test that loads `sample_response_real.json` (if present) and asserts only "valid `RetrievalOutput` returned" + "every cross_reference has ≥1 evidence_span." Catches Anthropic-side response-shape drift between T1 runs without requiring an API call. Cost: minor; value: redundant with T1's `test_parser_handles_real_api_response`. Punted under YAGNI.
- **Parser doc update for `thinking` block?** Now empirically known to appear in real responses. `parser.py`'s docstring may not mention this explicitly. Quick fix when scoring_v2 or someone else next touches the parser.
- **Unresolvable-reference live test?** Currently un-exercised against real API. Would need a deliberately-messy statute fixture. Worth raising in the brief-writer / scoring impl session, where unscoreable cells will have an analogous path (`record_unscoreable_cell` per the brief-writer brainstorm convo's locked package).
- **`max_tokens=2000` override in integration test.** Single-chunk, tiny-statute scenario; production default is 16000. Plan's discipline. When the brief-writer/scoring impl writes its own integration test, same discipline should apply but with appropriate sizing (more chunks, longer real statutes).

## Commits this session (1)

| Commit | What |
|---|---|
| `5f262e9` | retrieval_v2: decouple parser test fixture from integration write path (rename + gitignore + 2 test edits) |

## Captured Tasks

- [#11: retrieval_v2: document Opus 4.7 thinking-block passthrough in parser.py](https://github.com/danparshall/lobby_analysis/issues/11) — captured 2026-05-14
- [#12: retrieval_v2: live-test record_unresolvable_reference path with a deliberately-messy statute fixture](https://github.com/danparshall/lobby_analysis/issues/12) — captured 2026-05-14
- [#13: retrieval_v2: optional shape-tolerant parser test against sample_response_real.json](https://github.com/danparshall/lobby_analysis/issues/13) — captured 2026-05-14

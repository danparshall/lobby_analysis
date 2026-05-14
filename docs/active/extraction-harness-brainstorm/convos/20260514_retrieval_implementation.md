# 20260514 — Retrieval v2 implementation

**Date:** 2026-05-14
**Branch:** `extraction-harness-brainstorm`
**Plan executed:** [`../plans/20260514_retrieval_implementation_plan.md`](../plans/20260514_retrieval_implementation_plan.md)
**Originating brainstorm:** [`20260514_retrieval_brainstorm.md`](20260514_retrieval_brainstorm.md)
**Predecessor session:** [`20260514_chunks_implementation.md`](20260514_chunks_implementation.md) (shipped `chunks_v2` which this work consumes)
**Precondition met:** Phase 0 scaffolding at `4c49888` was an ancestor of HEAD (verified via `git merge-base --is-ancestor`); `anthropic 0.102.0` installed; `build_chunks()` returns the expected 15 chunks.

## Summary

Executed the retrieval implementation plan end-to-end under strict TDD on the laptop (Dans-MacBook-Air). Wrote **51 RED tests** across 6 files first (commit `a5d05c5`), then turned them green file-by-file across five GREEN commits. **T0 unit gate is fully green** (448 passed in the full suite, up from 400 pre-retrieval); **T1 smoke (integration test against real Anthropic API) is deferred to a desktop run** because this laptop has no `ANTHROPIC_API_KEY` — user flagged this mid-session and asked to defer T1 explicitly. The integration test machinery is in place (skipif-gated, `tiny_statute.txt` fixture committed); desktop run = `uv run pytest tests/test_retrieval_v2_integration.py` with the key in env.

The deliverable is **`src/lobby_analysis/retrieval_v2/`** — five thin modules (`tools.py`, `models.py`, `brief_writer.py`, `parser.py`, `prompt.py` left empty per YAGNI) wired into a clean public surface via `__init__.py`. The brief-writer returns a `messages.create()` kwargs dict but does **not** call the SDK; the orchestrator (downstream, not in scope) is the dispatcher. The parser is **polymorphic over SDK `Message` objects and JSON-loaded dicts** so the same path handles fixtures + real responses — load-bearing for desktop T1 where the parser meets real-API shape for the first time. `src/scoring/retrieval_agent_prompt_v2.md` lands as the v2 prompt (chunk-anchored, zero PRI rubric leakage).

**Two plan deviations surfaced and resolved**, both minor but worth flagging for the next reader: (1) phase ordering — `brief_writer.py` reads the prompt file at call time, so Phase 6 (prompt.md) had to land before Phase 4 (brief_writer) for tests to clear; commit messages preserve plan-numbered phase names so the audit trail stays intact; (2) `CompendiumCellSpec` has no `description` field (only `row_id`, `axis`, `expected_cell_class`) and the underlying compendium TSV has no description column either, so the plan's `spec.description[:120]` rendering was unimplementable. Dropped to `- {row_id} ({axis}) [{cell_class}]` per-cell line; row_ids are self-describing in this codebase. Plan-author drift caught by reality, resolved at use-time.

## Topics Explored

- **Plan-vs-reality drift in `CompendiumCellSpec`.** Plan inlined `_format_cell_roster` with `spec.description[:120]`. Verified by inspection that `CompendiumCellSpec` fields are `(row_id, axis, expected_cell_class)` only — no description anywhere. Compendium TSV (`compendium/disclosure_side_compendium_items_v2.tsv`) also has no description column (only `rubrics_reading`, `n_rubrics`, `first_introduced_by`, `status`, `notes` — all provenance, not prose). YAGNI on synthesizing descriptions; row_ids carry enough semantic load.
- **Phase ordering when prompt is read at call time.** Tested whether brief_writer could load the prompt lazily / from a default placeholder. Concluded the cleanest fix is the phase reorder — no production code path should silently swallow a missing prompt file. Phase numbering preserved in commit messages so future readers can map back to the plan.
- **Polymorphic parser shape.** Plan-author noted that SDK objects use attribute access; fixture dicts use key access. Added a `_get` helper that does `hasattr` → `getattr` → `isinstance dict` → `dict.get` fallback. Same path works for both. Critical for T1 — when desktop run lands, the parser meets real API responses for the first time and must not crash on unexpected attribute layouts.
- **Side-effect-in-test concern for the integration smoke.** Plan's Phase 7 has `test_parser_handles_real_api_response` writing real response back to `sample_response.json` on every successful run. Flagged as a slight anti-pattern (side effect in test, fixture churn across runs) — but matches plan intent of "live-validate parser against current API shape." Kept the plan's design; surfaced the concern in this convo for the next agent to weigh in if it bites.
- **Cost discipline for T1.** Integration brief overrides `max_tokens=2000` (production default is 16000), single chunk in scope (`actor_registration_required` → 11 cells), 2-sentence statute fixture. Plan estimate ~$0.02/run; this holds.

## Provisional Findings

- **T0 unit suite is fully green** for retrieval_v2: 48 new tests passing (8 tools + 7 models + 17 brief_writer + 8 parser + 8 prompt invariants), plus 3 integration tests SKIPPED cleanly without an API key. Pre-existing baseline (3 `test_pipeline.py` FileNotFoundErrors from missing portal-snapshot fixtures) unchanged.
- **Coupling test between tools schema and chunks manifest works.** `test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest` reads `build_chunks()` and asserts the tool's `chunk_ids_affected.items.enum` equals the manifest's 15 chunk_ids exactly. Catches future drift in either direction.
- **Prompt invariants caught no v1 leakage** — zero `\b[AC]\d{1,2}\b` matches (PRI letter keys), zero `rubric_items_affected` occurrences, zero `rubric` standalone words. v2 prompt is properly chunk-anchored and tool-anchored.
- **Parser's reset-after-tool invariant is non-vacuous.** `test_parser_resets_citation_buffer_after_each_tool_call` reads the hand-crafted fixture (which has TWO tool calls with distinct preceding citations) and asserts the two evidence_span sets have empty intersection. Real-API behavior may differ; T1 will tell.

## Decisions Made

- **Plan deviation #1 (phase reorder): P6 → P4 → P5.** Brief-writer reads prompt at call time; prompt file has to exist for brief-writer tests to pass. Reordered execution to P2 (tools) → P3 (models) → **P6 (prompt.md)** → **P4 (brief_writer)** → P5 (parser + sample fixture) → P7 prep → P8 (exports + docs + ruff). Commit messages preserve plan-numbered phase names ("Phase 6 of plan", "Phase 4 of plan", etc.) so the audit trail stays intact.
- **Plan deviation #2 (cell roster format): drop `.description[:120]`.** `CompendiumCellSpec` has no description; emit `- {row_id} ({axis}) [{cell_class}]` instead. Matches reality of the v2 schema; `test_brief_writer_includes_only_requested_chunks_cell_roster` (which checks for chunk_id substring presence/absence in the user text) is satisfied.
- **Phase 7 (T1 smoke) deferred to desktop run.** User decision mid-session: this laptop has no `ANTHROPIC_API_KEY`; user runs the smoke test on the desktop machine. Prep work done on laptop: `tiny_statute.txt` fixture committed; integration test skips cleanly without key (verified `3 skipped in 0.01s`); module shipped at T0-green state. Desktop instructions in [Open Questions](#open-questions) below.
- **`prompt.py` left as empty Phase-0 scaffolding.** YAGNI: brief_writer inline-loads the prompt via `_PROMPT_PATH.read_text()`. The plan's Phase 6 wording ("Implement prompt.py's load_v2_prompt() if the brief-writer doesn't already inline-load it") explicitly allows this.

## Results

- Implementation lives at [`src/lobby_analysis/retrieval_v2/`](../../../../src/lobby_analysis/retrieval_v2/) with full module docs in [`docs.md`](../../../../src/lobby_analysis/retrieval_v2/docs.md).
- v2 prompt at [`src/scoring/retrieval_agent_prompt_v2.md`](../../../../src/scoring/retrieval_agent_prompt_v2.md).
- Hand-crafted parser fixture at [`tests/fixtures/retrieval_v2/sample_response.json`](../../../../tests/fixtures/retrieval_v2/sample_response.json) (Phase 7 desktop run will overwrite with real-API shape).
- T1 smoke fixture at [`tests/fixtures/retrieval_v2/tiny_statute.txt`](../../../../tests/fixtures/retrieval_v2/tiny_statute.txt).

## Commits this session (8)

| Commit | Phase | What |
|---|---|---|
| `a5d05c5` | 1 | RED tests across 6 files (51 tests; ImportError + FileNotFoundError + SKIP) |
| `191873b` | 2 | `tools.py` — CROSS_REFERENCE_TOOL + UNRESOLVABLE_REFERENCE_TOOL, chunks-coupled enum |
| `16beb1d` | 3 | `models.py` — frozen Pydantic models (EvidenceSpan, CrossReference, UnresolvableReference, RetrievalOutput) |
| `1686474` | 6 | `retrieval_agent_prompt_v2.md` (executed early — see plan deviation #1) |
| `97a3fee` | 4 | `brief_writer.py` — documents + citations + caching |
| `aab535f` | 5 | `parser.py` + hand-crafted `sample_response.json` |
| `22703fa` | 7-prep | `tiny_statute.txt` fixture; real API call deferred to desktop |
| `d1fa512` | 8 | `__init__.py` exports + `docs.md` + ruff format pass |

## Open Questions

### What to do on the desktop for T1

When you run `uv run pytest tests/test_retrieval_v2_integration.py` on Dans-MacBook-Pro with `ANTHROPIC_API_KEY` set:

1. **All 3 pass:** great — `test_parser_handles_real_api_response` will have side-effect-written the real response to `tests/fixtures/retrieval_v2/sample_response.json`. Subsequent `uv run pytest` invocations re-run the parser unit tests against that real-shape fixture. If parser tests **stay green** after the fixture is overwritten, the hand-crafted shape matched reality and the parser is solid.

2. **Parser unit tests go red after the fixture write:** the hand-crafted shape diverged from reality. Per plan Phase 7's "Things that may go wrong" section: **pause and surface to user**. Do NOT silently patch the parser to handle the divergence — the docs↔reality mismatch is itself a finding the user wants to know about.

3. **No citations attach to text blocks** (`test_real_api_call_returns_citations` fails with empty citations): possible cause is fixture too short for sentence-chunker. Try padding `tiny_statute.txt` to 4-5 sentences and retry.

4. **No `record_cross_reference` tool call fires** (`test_real_api_call_produces_at_least_one_cross_reference` fails): Rule 5 in the prompt isn't load-bearing enough. Prompt needs sharpening — surface to user with a quote of the actual response.

5. **Schema validation error on `chunk_ids_affected`** (e.g., agent passes `"actor_registration"` instead of `"actor_registration_required"`): tool-use validates input against the JSON schema's enum, so this should 400 with a clear error. If the agent consistently misnames chunk_ids, the prompt needs full chunk_id list explicit (currently the agent infers from the brief's cell roster).

### Side effect in test_parser_handles_real_api_response

The plan's design has this test overwrite `sample_response.json` on every successful run. Functionally that means real-API responses gradually churn the fixture across runs (different response, different IDs, slightly different content). Two ways to read this:

- **Pro:** fixture stays in sync with current API shape, parser tests re-validate against fresh data every run.
- **Con:** test has a side effect; parser unit-test results depend on a global file mutated by the integration test; fixture isn't reproducible.

Plan author chose pro. If con bites (e.g., fixture-churn-induced parser flakes), the simplest fix is gating the write with `if not SAMPLE_RESPONSE_PATH.exists():`. Not changing this until the user weighs in or T2-T4 show the side effect causes real noise.

### Next downstream components (per the kickoff strategy)

- **Brief-writer brainstorm** is the cleanest next pick (orthogonal to retrieval — depends only on cells + chunks, both shipped). Same brainstorm → plan → impl cycle.
- **Scorer-prompt rewrite** is the fourth component; depends on retrieval bundle shape (which is now known: `RetrievalOutput` with `cross_references[*]` carrying `evidence_spans` for cited statute support).

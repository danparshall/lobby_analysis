# 20260519 — Tier-0 direct-read plan, Steps 1–4 executed; Step 5 pending on a keyed machine

**Date:** 2026-05-19
**Branch:** extraction-harness-brainstorm
**Predecessor convo:** [`20260518_tier_0_execution_pivot_to_direct_read.md`](20260518_tier_0_execution_pivot_to_direct_read.md)
**Plan executed:** [`../plans/20260518_tier_0_direct_read_smoke_test.md`](../plans/20260518_tier_0_direct_read_smoke_test.md) — Steps 1–4 of 7
**Machine:** Dans-MacBook-Air (no API keys; deliberately partial execution)

## Summary

Session began with a handoff from the previous agent pointing at the new direct-read plan and noting that Dans-MacBook-Air has no API keys. After pre-flight reads (STATUS, README, branch RESEARCH_LOG, predecessor convo, the plan itself), user chose the keyless-friendly subset: do Steps 1–4 here (pure-code, no dispatch), leaving Steps 5–7 for whichever machine has both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` exported. Goal: when a keyed agent picks this up, they should be able to run `uv run python scripts/tier_0_direct_read_smoke.py` and have the wiring already in place.

Four commits shipped, all on top of `cce8542`. Test suite went from 480 → 497 passing (+14 parser tests, +3 cold-load regression tests); the 3 pre-existing `test_pipeline.py` baseline failures (missing CA portal-snapshot fixture, unrelated to this work) are unchanged.

## What shipped (commit-by-commit)

### `62e02c0` — Step 1: relocate `EvidenceSpan` to break the cold-load import cycle

The cycle the prior session diagnosed: `chunks_v2 → models_v2.cells → retrieval_v2.models → retrieval_v2/__init__ → brief_writer → chunks_v2`. (The prior convo named `retrieval_v2/tools.py:22` as the closing edge, but the actual closing edge is `brief_writer.py:30` — same cycle, slightly different trace.) Test suite couldn't catch it because tests import lazily inside test functions; a fresh interpreter (`uv run python -c "from lobby_analysis.chunks_v2 import build_chunks"`) reproduced the `ImportError`.

Structural fix per the plan: `EvidenceSpan` is foundational provenance (used by both cells and cross-refs), not retrieval-specific. New module `src/lobby_analysis/models_v2/citations.py` defines `EvidenceSpan` + `CitationType`. `models_v2/cells.py` now does `from .citations import EvidenceSpan`. `retrieval_v2/models.py` re-exports from the new home; all existing call sites (`from lobby_analysis.retrieval_v2 import EvidenceSpan`, `.../retrieval_v2/models import EvidenceSpan`) still work — verified by identity check across all four import paths.

Three regression tests at `tests/test_v2_cold_load.py`:
- `test_chunks_v2_loads_cold` — fresh `subprocess` interpreter imports `build_chunks` cleanly.
- `test_models_v2_cells_loads_cold` — loading `models_v2.cells` alone does not pull `retrieval_v2` into `sys.modules`.
- `test_retrieval_v2_evidence_span_back_compat` — identity preserved across all four import paths.

### `a7fbbb6` — Step 2: `uv add openai`

`openai==2.37.0` installed. `pyproject.toml` + `uv.lock` updated.

### `02cad4f` — Step 3: tool schemas + cross-SDK parser + 14 parser tests

`scripts/tier_0_direct_read_smoke.py` (single file per the plan's YAGNI directive — no new packaged module). Contains:

- Shared `RECORD_CELL_INPUT_SCHEMA` + `RECORD_UNSCOREABLE_INPUT_SCHEMA` (one source of truth for both SDKs).
- `ANTHROPIC_TOOLS` (keys schema under `input_schema`) and `OPENAI_TOOLS` (wraps as `function.parameters`).
- `parse_response(response, sdk)` returning `list[ParsedToolCall]` regardless of SDK.
- Anthropic path walks `response.content` for `tool_use` blocks; raises `ValueError` on missing wire fields.
- OpenAI path walks `response.choices[0].message.tool_calls`; `json.loads` raises on malformed argument JSON rather than silently dropping the call.
- Parsed `arguments` is an independent dict copy (verified by a mutation test) so downstream changes don't leak back into the captured response.

Tests at `tests/test_tier_0_smoke_parser.py` load the script via `importlib.util.spec_from_file_location` (with `sys.modules` registration so `@dataclass` works on the loaded module), exercise both SDK shapes with hand-built `SimpleNamespace` fixtures shaped to the documented contracts, and assert the cross-SDK schema-sharing invariant (`ANTHROPIC_TOOLS[i].input_schema is OPENAI_TOOLS[i].function.parameters`).

### `b0a1b2d` — Step 4: smoke-test script body

Completed `scripts/tier_0_direct_read_smoke.py` (now 565 lines). Production path:

1. **Preflight.** Checks `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` are set and the OH 2025 statute bundle path resolves. Exits cleanly with `sys.exit(2)` and a clear stderr message before any API call if either fails. Verified empirically: `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY uv run python scripts/tier_0_direct_read_smoke.py` exits 2.
2. **Statute loader.** Reads all 30 `.txt` files under `data/statutes/OH/2025/sections/`, concatenates with `=== filename ===` dividers.
3. **Chunk roster.** Loads `enforcement_and_audits` (2 rows × 2 axes = 4 cells: BinaryCell/EnumCell/GradedIntCell × 2).
4. **Cached system prompt.** Statute embedded as a cache-controlled block for Anthropic; OpenAI auto-caches ≥1024 tokens.
5. **Dispatch + parse + instantiate.** `_instantiate_cell` adapter handles both scalar cells (Binary/Decimal/Int/Float/Graded/Bounded/Enum/EnumSet/FreeText/UpdateCadence/SectorClassification) and dict-shape cells (TimeThreshold/TimeSpent/CountWithFTE/EnumSetWithAmounts). Bad cells go into an `errors` list instead of crashing the run.
6. **Result saving.** Raw + parsed JSON per model to `docs/active/extraction-harness-brainstorm/results/` with a structured `provenance` field on each (originating convo, model, chunk, prompt sha256, timestamp). JSON doesn't support markdown `<!-- ... -->` comments, so the plan's provenance-header pattern becomes a sibling JSON field.
7. **Side-by-side printer.** Per-cell comparison + per-model usage + cost.
8. **Cost ceiling.** Aborts the whole run with exit 3 if any one call exceeds $1 — strict reading of the plan's "stop and investigate."

## Decisions Made

- **EvidenceSpan home:** plan-suggested `models_v2/citations.py` chosen (Question 1 from the plan resolved). No reason surfaced during implementation to prefer a top-level `lobby_analysis/citations.py`.
- **Cell wrapper shape:** plan-suggested option (a) — wrap each cell in `{cell, cell_class, cited_section, justification}` (Question 3 resolved). `CompendiumCell` itself unchanged.
- **Provenance in JSON results:** structured `provenance` field on the top-level object, not a markdown comment header (JSON can't have comments). Same information, queryable shape.
- **Test fixture strategy:** hand-built `SimpleNamespace` fixtures shaped to the documented SDK contracts for now. After Step 5 ships, real frozen responses can be added alongside without touching the parser test logic.

## Caveats for the next agent (Step 5)

1. **Pricing numbers are best-guess.** `_PRICING_USD_PER_MTOK` uses opus-4-**6** rates from `personal_info.md` (March 2026) as a placeholder for opus-4-**7**. They feed the $1/call abort ceiling + a printed cost estimate. If cost matters for the writeup verdict, re-verify against current Anthropic pricing.

2. **OH 2015 sections ARE on Dans-MacBook-Air now.** `/Users/dan/data/lobby_analysis/statutes/OH/{2010,2015,2025}/` all exist on this machine as of 2026-05-19. The predecessor convo noted OH 2015 was absent on 2026-05-18 — either added since or the prior check missed. Doesn't change the Tier-0 retarget (still OH 2025), but the rationale should be revisited if vintage choice matters downstream.

3. **Dict-shape cells aren't exercised by this chunk.** `enforcement_and_audits` is all scalar cells. The `_instantiate_cell` adapter supports TimeThresholdCell/TimeSpentCell/CountWithFTECell/EnumSetWithAmountsCell, but those paths aren't smoke-tested by this run. First chunk that hits one of those cell types will be the first integration test for the dict-shape path.

4. **Cost ceiling aborts the whole run** if any single call exceeds $1. If you want to see what the second model produced when the first overspends, relax `_PER_CALL_COST_CEILING_USD` or refactor to record-and-continue rather than abort.

## Results

(No analytical outputs this session — the deliverables are the 4 commits + the wiring. Results files come from Step 5's run.)

## Open Questions (carry-forward)

From the plan, none newly resolved this session. The next agent will hit these when Step 5 runs:

- Concrete prompt language tuning for the "your response will be verified by another model" framing (plan Q2).
- Whether $5 session ceiling should be tightened or kept at $5 for retry headroom (plan Q4).
- Real-vs-synthesized parser fixtures — should the new frozen responses replace the synthesized ones, or live alongside them parametrically? My preference: keep both. Synthesized fixtures are the contract assertion (parser handles documented shape); real fixtures are regression evidence (parser handles what the live API actually emitted).

## Next Steps

1. Move to a keyed machine (MacBook-Pro or tarragon).
2. `cd /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm && git pull`.
3. Sanity check: `uv run pytest tests/test_v2_cold_load.py tests/test_tier_0_smoke_parser.py` (17 tests should be green).
4. `uv run python scripts/tier_0_direct_read_smoke.py`.
5. Hand-eyeball writeup at `results/20260518_tier_0_direct_read_writeup.md` per the plan's Step 6.
6. Finish-convo on that session's execution date (not 20260519 — this convo *is* the finish-convo for the keyless-machine session that shipped Steps 1–4; the keyed-machine session ending Steps 5–7 writes its own finish-convo).

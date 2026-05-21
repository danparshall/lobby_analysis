# Tier 1 — Direct-read legal-axis run over the CPI-2015 de-jure chunks Implementation Plan

**Goal:** Scale the Tier-0 direct-read smoke into a legal-axis-only run across the 6 chunks containing the CPI-2015 C11 de-jure items, fix the value-typing bug Tier-0 surfaced, and measure run-to-run noise (σ_noise) via N=3 re-runs per model.

**Originating conversation:** [`../convos/20260520_tier_0_direct_read_execution.md`](../convos/20260520_tier_0_direct_read_execution.md)

**Context:** Tier-0 ([writeup](../results/20260518_tier_0_direct_read_writeup.md)) proved the direct-read wiring works for the legal (de jure) axis but surfaced two defects: (a) `record_cell.value` arrives as a JSON **string** and fails `GradedIntCell` instantiation (criterion-5 failure); (b) the scorer was handed `practical`-axis cells it should never see — the practical/de facto axis is **Prong 2's** job, scored later against the same compendium items. Tier-1 fixes both and scales to the CPI-relevant chunks so the outputs are positioned for later projection-validation against CPI's published OH scores.

**Confidence:** Moderate. The architecture is inherited and proven by Tier-0; the scale-up is mechanical. But Tier-0 only exercised scalar cells — Tier-1 will hit **dict-shape cells** (`TimeThresholdCell`, `CountWithFTECell`, etc.) for the first time. Expect 1–3 more wiring bugs of the Tier-0 string/int class. Stop-and-report discipline applies.

**Architecture:** Same as Tier-0 — one cached-statute system prompt per model, per-chunk user message, `record_cell` / `record_unscoreable_cell` tools. Three deltas: (1) coerce `record_cell.value` to the cell class's expected scalar type before instantiation; (2) filter the cell roster to `axis == "legal"` before dispatch; (3) wrap dispatch in an N=3 re-run loop with per-dispatch checkpointing and a per-cell inter-run agreement metric.

**Branch:** `extraction-harness-brainstorm` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, `uv`, Anthropic SDK, OpenAI SDK, Pydantic v2.

---

## Pre-flight reads (mandatory before touching code)

1. `STATUS.md` (repo root) — current focus, ⭐ Compendium 2.0 criterion, branch inventory.
2. [`../convos/20260520_tier_0_direct_read_execution.md`](../convos/20260520_tier_0_direct_read_execution.md) — Tier-0 execution + the de jure/de facto clarification that motivates the roster filter.
3. [`20260518_tier_0_direct_read_smoke_test.md`](20260518_tier_0_direct_read_smoke_test.md) — the Tier-0 plan; this plan reuses its architecture, schemas, and parser.
4. [`../results/20260518_tier_0_direct_read_writeup.md`](../results/20260518_tier_0_direct_read_writeup.md) — the empirical signal Tier-1 builds on (note the `[Amended 2026-05-20.]` sections).
5. `scripts/tier_0_direct_read_smoke.py` — the existing single-file script; Tier-1 imports its schemas/tools/parser/`_instantiate_cell`.
6. `src/lobby_analysis/chunks_v2/docs.md` — the 15-chunk table.

---

## Prerequisites — verify BEFORE writing code

`ls` / `grep` each one; trust the filesystem, not this prose.

1. **Tier-0 sanity tests green:** `uv run pytest tests/test_v2_cold_load.py tests/test_tier_0_smoke_parser.py` → 17 passed.
2. **OH 2025 statute bundle:** `ls data/statutes/OH/2025/sections/ | wc -l` → 30.
3. **Both API keys exported.** `ANTHROPIC_API_KEY` + `OPENAI_API_KEY`. (This session sourced them from `/Users/dan/code/lobby_analysis/.env.corporate` — a *mixed* file; load only the `KEY=` lines: `. <(grep -E '^[A-Za-z_]+=' /Users/dan/code/lobby_analysis/.env.corporate)`. If absent, stop and ask.)
4. **CPI-2015 mapping doc present:** `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` and `cpi_2015_c11_per_state_scores.csv` (the 700-cell ground truth, kept for the *later* projection step — not consumed by Tier-1).

---

## Step 1 — Identify the 6 de-jure chunks

The 6 CPI-2015 C11 **de jure** items are **IND_196, IND_197, IND_199, IND_201, IND_203, IND_207** (the items labelled "de jure" in the mapping doc's distribution table; the other 8 are de facto).

- For each item, read its per-item section in `cpi_2015_c11_projection_mapping.md` and note the **compendium row(s)** it maps to. NB: the mapping doc uses **pre-rename row IDs** (per NAMING_CONVENTIONS.md §10.1). Route each through the rename resolver (resolver table in `compendium/NAMING_CONVENTIONS.md` §10.1) to get the live v2 row IDs.
- For each live row ID, find its chunk: `build_chunks()` from `lobbery_analysis.chunks_v2`, look up which `Chunk` contains the `(row_id, "legal")` cell.
- Expected outcome: ~6 chunks (likely `lobbying_definitions`, a registration chunk, `lobbyist_spending_report`, `principal_spending_report`, `enforcement_and_audits`, and one more). **Record the exact resolved chunk list in the writeup.** If it resolves to materially more or fewer than 6 chunks, surface to the user before running.
- This is analysis, not code — no test. Output: a short table (CPI item → live row_id → chunk) saved into the Step-7 writeup.

## Step 2 — Fix the value-typing bug (TDD)

Root cause (Tier-0): the shared `RECORD_CELL_INPUT_SCHEMA` `value` is a loose `oneOf` that admits `string`; the model emitted `"2"` for a `GradedIntCell`; Pydantic (strict) rejected it.

- The fix lands in **`_instantiate_cell`** in `scripts/tier_0_direct_read_smoke.py` (the shared instantiation adapter — so both scripts benefit). Add a normalization step: keyed on the expected cell class, coerce a JSON-string scalar to its target Python type (`IntCell`/`GradedIntCell`/`BoundedIntCell` → `int`; `DecimalCell`/`FloatCell` → `float`; `BinaryCell` → `bool` from `"true"`/`"false"`). If coercion is not clean (e.g. `"banana"` → `int`), leave the cell in the existing `errors` list — do **not** silently swallow it.
- Add a prompt nudge in the system-prompt text: "emit numeric answers as JSON numbers, not quoted strings." Belt-and-suspenders; coercion is the real fix.
- Steps: (1) write the failing unit tests (Step 6 below); (2) run them, watch them fail; (3) implement the coercion; (4) run, watch them pass; (5) commit `tier-1: coerce JSON-string scalar values in _instantiate_cell`.

## Step 3 — Add the legal-axis roster filter (TDD)

- In the new Tier-1 script, when building a chunk's cell roster, filter to `axis == "legal"`. Mixed chunks contribute only their legal cells; the practical (de facto) cells are Prong 2's and must never be dispatched.
- Write the failing test first (Step 6), then implement, then commit `tier-1: legal-axis roster filter`.

## Step 4 — Write the Tier-1 runner script

Create `scripts/tier_1_direct_read_legal_axis.py`. It **imports** the reusable pieces from the Tier-0 script — `RECORD_CELL_INPUT_SCHEMA`, `RECORD_UNSCOREABLE_INPUT_SCHEMA`, `ANTHROPIC_TOOLS`, `OPENAI_TOOLS`, `parse_response`, `_instantiate_cell`, the statute loader, the dispatch helpers — rather than duplicating them. (If this script-imports-script pattern gets ugly, that is the signal to finally extract a `scoring_v2/` module — but not in this plan; YAGNI.)

Behavior:
1. Load the OH 2025 statute bundle once; build the cached system prompt once (shared across all chunks/runs — cache-friendly).
2. For each of the 6 chunks, build the legal-only roster (Step 3).
3. **Dispatch loop:** for each `(model, chunk, run)` in `[claude-opus-4-7, gpt-5.2] × 6 chunks × 3 runs` = 36 dispatches:
   - **Checkpoint + resume:** before dispatching, check whether `results/tier_1/<model>__<chunk>__run<N>.json` already exists; if so, skip. Save each dispatch's raw + parsed result immediately on completion. A crash at dispatch 30 must not redo 1–29. (Experiment Data Integrity — mandatory.)
   - Each saved file carries a `provenance` block: model, chunk_id, run index, prompt sha256, timestamp, originating convo.
4. After all dispatches: compute the **agreement metric** (Step 5) and write the writeup (Step 7).
5. Keep Tier-0's `$1`-per-call abort. Raise the session ceiling to `$10` (36 calls; ≈ $2–4 expected — see Questions).
6. Commit `tier-1: direct-read legal-axis runner over the 6 CPI de-jure chunks`.

## Step 5 — Agreement metric / σ_noise (TDD)

For each `(model, cell)`, across that model's 3 runs:
- **Stable** iff all 3 runs agree on the value (exact match), or all 3 abstain.
- **Scoreability-unstable** iff the model sometimes scores and sometimes abstains (this is the Tier-0 Claude/GPT divergence, surfaced *within* a model).
- For numeric-valued cells, also report the spread (min/max/stdev) of the 3 values.
- Aggregate per model: `% cells stable`. This is the σ_noise proxy — the Ralph loop must not chase differences smaller than this floor.

Write the failing tests first (Step 6), implement, commit `tier-1: inter-run agreement / σ_noise metric`.

## Step 6 — Tests (write ALL of these before Steps 2/3/5 implementation)

**Testing Plan**

I will add **unit tests for behavior**, not for datastructures:

- `_instantiate_cell` coercion: a `record_cell` arg dict with `value="2"` for a `GradedIntCell` row instantiates to `GradedIntCell(value=2)` (int); `value="3.5"` for a `FloatCell` row → `FloatCell(value=3.5)`; `value="banana"` for an int cell goes to the `errors` list, not a silent pass. Tests the coercion *behavior* against real `models_v2` cell classes (no mocks).
- Legal-axis roster filter: given a known mixed chunk (e.g. `enforcement_and_audits`, 2 legal + 2 practical cells), the built roster contains exactly the 2 legal cells and zero `axis=="practical"` cells.
- Agreement metric: fed three synthetic per-run cell outputs — `[2,2,2]` → stable; `[2,2,3]` → unstable; `[scored, scored, abstained]` → scoreability-unstable; numeric spread reported correctly for `[2,2,3]`.
- Resume logic: with one `results/tier_1/<model>__<chunk>__run1.json` pre-placed, the runner's skip check reports that triple as already-done and does not re-dispatch it (test the skip predicate directly — no API call).

The parser itself is already covered by `tests/test_tier_0_smoke_parser.py`; Tier-1 reuses it unchanged.

The **6-chunk run itself is the integration test** — it is exploration, not TDD. Pass/fail criteria are in "Success criteria" below.

NOTE: I will write *all* tests before I add any implementation behavior.

## Step 7 — Hand-eyeball + writeup

- Spot-check cited sections against the OH 2025 bundle for a sample of cells per chunk (the bundle is small).
- Write `results/tier_1/20260520_tier_1_legal_axis_writeup.md` (provenance header) covering: the resolved CPI-item→row→chunk table (Step 1); per-model per-chunk cell counts (scored / unscoreable / errored); the σ_noise figure per model; cross-model agreement per cell; dict-shape cells encountered and whether they instantiated cleanly; cost + wall-clock; surprises; and whether legal-axis direct-read looks ready to scale to all 15 chunks / multi-vintage.
- Commit `tier-1: legal-axis run writeup + σ_noise`.

## Step 8 — Finish-convo

New convo `convos/20260520_tier_1_*.md` (or append, if same calendar session), update `RESEARCH_LOG.md` + `STATUS.md`, commit, push. Do not merge.

---

## Success criteria

1. Steps 2/3/5 tests all green; full suite shows no new failures beyond the 3 pre-existing `test_pipeline.py` baseline failures.
2. The 36-dispatch run completes (or resumes cleanly after an abort) with all reachable `results/tier_1/*.json` files written.
3. After the typing fix, **zero** `instantiation_failed` errors of the string/int class. Any *new* error class (e.g. dict-shape cell failures) is stopped-and-reported, not patched.
4. No `practical`-axis cell is ever dispatched (verify in the saved rosters).
5. A σ_noise figure (`% cells stable across N=3`) is produced per model.

If 1–4 fail, **stop and report** rather than patching — same discipline as Tier-0.

---

## Edge cases to anticipate

- **Dict-shape cells fire for the first time.** `IND_197` is a compensation *threshold* (`registration_thresholds` chunk → likely `TimeThresholdCell`/typed cells). The `_instantiate_cell` dict-shape path is untested by real API output. Expect failures; stop-and-report.
- **Empty legal roster.** A chunk could (in principle) have no legal cells after filtering. The 6 CPI chunks are de-jure-selected so this is unlikely, but the runner must skip an empty-roster chunk gracefully, not crash.
- **Mid-loop crash / cost abort.** Checkpointing makes this safe — the resume check skips completed triples. Verify by killing the run halfway and restarting.
- **One model fails, the other succeeds.** Save what completed; the writeup notes the asymmetry.
- **Cost overrun.** `$1`/call abort retained; `$10` session ceiling. If a single call exceeds `$1`, stop and investigate before continuing.

---

**Testing Details:** Four behavior-focused unit test groups (value coercion against real `models_v2` cell classes; legal-axis roster filtering; the agreement/σ_noise metric; the resume-skip predicate). None test datastructures, types, or mocks-of-mocks. The 6-chunk dispatch is the integration test and is exploratory (no TDD), with explicit pass/fail criteria above.

**Implementation Details:**
- Typing fix lives in `_instantiate_cell` (shared, in the Tier-0 script); Tier-1 imports it.
- Tier-1 is a new script `scripts/tier_1_direct_read_legal_axis.py`; imports — does not duplicate — Tier-0's schemas/tools/parser.
- Outputs go to a new `results/tier_1/` directory, one JSON per `(model, chunk, run)` triple, each with a provenance block.
- Per-dispatch checkpoint + resume is mandatory (Experiment Data Integrity) — 36 dispatches must not be re-run wholesale on a crash.
- σ_noise = `% cells stable across N=3 runs`, per model; plus numeric spread for numeric cells.
- Statute system prompt is built once and shared across all 36 dispatches (prompt cache hit).
- `$1`/call abort retained; session ceiling raised to `$10`.

**What could change:**
- If dict-shape cells fail en masse, the typing fix may need to extend into the dict-shape path — but that is a *finding* to surface, not a patch to apply mid-run.
- The CPI item→row→chunk resolution (Step 1) may yield a chunk count other than 6; the run scales to whatever it resolves to.
- If σ_noise is high (say, <80% stable), legal-axis direct-read may not be reliable enough to scale, and the verifier agent (Phase 2) becomes load-bearing sooner than planned.

**Questions:**
1. **Temperature for the N=3 runs** — keep whatever `tier_0_direct_read_smoke.py` currently uses (verify it), or bump above 0 to capture more of the noise envelope? σ_noise at temp-0 still captures genuine nondeterminism, but understates the envelope a higher-temp production run would see.
2. **N=3 vs N=5** — is 3 re-runs enough to estimate a noise floor, or should it be 5? (3 matches the iter-1 precedent — 93.3% inter-run agreement on the `definitions` chunk.)
3. **CPI ground-truth comparison is deferred.** Tier-1 stops at σ_noise + hand-eyeball. Projecting these cells onto CPI's published OH scores needs the projection functions from `phase-c-projection-tdd` (not yet built). Confirm Tier-1's scope ends before that comparison.
4. **Cost ceiling** — `$10` session ceiling for 36 calls (≈ $2–4 expected). Keep, or tighten?

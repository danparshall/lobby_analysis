# Tier 0 — Direct-read smoke test (Claude + GPT side-by-side)

**Goal:** Smoke-test a direct-read scoring architecture against the OH 2025 `enforcement_and_audits` chunk on **both** Claude (Opus 4.7) and GPT (5.2) independently. Verify the wiring works end-to-end; compare typed `CompendiumCell` outputs across models; eyeball plausibility. No retrieval pre-pass, no Citations API, no orchestrator.

**Originating convo:** [`../convos/20260518_tier_0_execution_pivot_to_direct_read.md`](../convos/20260518_tier_0_execution_pivot_to_direct_read.md) — read in full; this plan exists because the prior Tier-0 plan failed four preconditions at execution time and the architecture was reframed.

**Superseded plan:** [`_tabled/20260518_tier_0_minimal_pipeline.md`](_tabled/20260518_tier_0_minimal_pipeline.md) — kept for provenance, do not execute.

**Branch:** `extraction-harness-brainstorm` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`)

**Confidence:** Exploratory. The deliverable is a wiring smoke + an empirical signal on whether direct-read is viable. Surprises are expected and informative; the architecture decision (direct-read vs Citations+retrieval) depends on what this run produces.

**Tech stack:** Python 3.12, `uv`, Anthropic SDK (already in pyproject), OpenAI SDK (Step 2 below adds it), Pydantic v2.

---

## Pre-flight reads (mandatory before touching code)

The implementing agent has zero context. Read these in order:

1. `STATUS.md` (repo root) — current focus, branch inventory, ⭐ Compendium 2.0 success criterion.
2. `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` — branch trajectory; the most recent session entry is for the pivot that produced this plan.
3. **This plan's originating convo:** `docs/active/extraction-harness-brainstorm/convos/20260518_tier_0_execution_pivot_to_direct_read.md` — substantive reasoning behind the pivot, the four preconditions that failed last time, what to NOT repeat.
4. `docs/RESEARCH_ARC.md` (repo root) — three-prong arc, Phase C eval framing, Ralph loop concretization.
5. `src/lobby_analysis/models_v2/docs.md`, `src/lobby_analysis/chunks_v2/docs.md` — the 2 v2 modules this script consumes.
6. The superseded plan (`plans/_tabled/20260518_tier_0_minimal_pipeline.md`) — *for context only*. Do not execute it. Its Tier-1 forward-pointer section is still valid; the Tier-0 portion is not.

---

## Prerequisites — verify BEFORE writing code

Each of these failed on the prior plan attempt. **`ls` or `grep` each one before declaring it satisfied.** Do not trust prose; trust the filesystem.

1. **OH 2025 statute bundle readable from the worktree.**
   - Canonical path: `/Users/dan/data/lobby_analysis/statutes/OH/2025/`
   - Worktree symlink: `data/statutes -> /Users/dan/data/lobby_analysis/statutes` (created 2026-05-18; gitignored so not in `git ls-files`).
   - Verify: `ls /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/data/statutes/OH/2025/sections/ | wc -l` should return 30.
   - If the symlink is missing on the machine you're on: `ln -s /Users/dan/data/lobby_analysis/statutes /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/data/statutes` (sibling-symlink alongside the gitignored `data/retrieval_v2/.gitkeep` placeholder).
   - If `/Users/dan/data/lobby_analysis/statutes/OH/2025/` doesn't exist on this machine: **stop and ask user**. Do not substitute another vintage.

2. **`ANTHROPIC_API_KEY` and `OPENAI_API_KEY` in env.**
   - Both required. Tier 0 dispatches both models.
   - If either is missing: stop and ask. Do **not** stub. The deliverable depends on real API output for both models.

3. **`openai` package in `pyproject.toml`.**
   - Currently absent (Step 2 below adds it).
   - Verify post-Step-2: `uv run python -c "import openai; print(openai.__version__)"` returns a version ≥ 1.0.

4. **Cold-load smoke for the import graph.**
   - Before doing anything: `uv run python -c "from lobby_analysis.chunks_v2 import build_chunks; chunks = {c.chunk_id: c for c in build_chunks()}; print(len(chunks))"` should print `15`.
   - If it fails with `ImportError: cannot import name 'build_chunks' from partially initialized module`: the circular import is still present. **Step 1 below must fix this before any other work.** Do not proceed with lazy-import patches — those treat the symptom, not the cause.

---

## Why this is an exploration task

Tier 0's deliverable is the smoke run itself plus an empirical signal on whether direct-read produces correct cells. The "test" is the end-to-end run. Unit-level TDD applies to the small inline helpers (statute loading, prompt assembly, response parsing) introduced in Step 3 — those should be test-first using frozen fixtures captured from the first real runs.

---

## Architecture — what this script does

**Single API call per model, per chunk.** No retrieval pass. No orchestrator. Statute lives in the system prompt (cached); per-chunk user message lists the questions.

```
For each model in [Claude Opus 4.7, GPT 5.2]:
  - system = task instructions + adversarial framing + full OH 2025 statute (cached)
  - user message = chunk-specific questions ("answer these 4 cells via record_cell")
  - tools = [record_cell, record_unscoreable_cell]
  - dispatch → response → parse into typed CompendiumCell instances
  - save raw + parsed to results/

Compare outputs cell-by-cell, hand-eyeball plausibility.
```

**No Citations API.** Scorer is instructed to emit a free-text `cited_section` (e.g., "§101.85(B)(2)") and 1-sentence `justification` per cell. Machine-checkable provenance becomes a downstream verifier (Phase 2, separate plan).

**Cross-model framing is literal.** Both models will see each other's output downstream. Prompt language: "your response will be independently verified by another model reading the cited section." True statement, not deception.

---

## Success criteria

Tier 0 passes if all of:

1. Script runs to completion for both models (no uncaught exceptions).
2. Each model produces a `ScoringOutput`-like structure (one per model, not packaged — inline dataclass or dict is fine for the smoke) with `state_abbr="OH"`, `vintage_year=2025`, `chunk_id="enforcement_and_audits"`.
3. Each output contains exactly 4 cells: 2 row_ids × 2 axes (per the `enforcement_and_audits` chunk manifest — both rows are combined-axis, so 4 cells total). **NB: this differs from the prior plan, which scoped to "2 legal cells" — the new plan stops filtering to legal-axis since direct-read has no reason to constrain that way.**
4. Each cell carries a non-empty `cited_section` (free-text statute reference) and `justification` (prose).
5. Each cell's `value` type-checks against `CompendiumCellSpec.expected_cell_class` for its `(row_id, axis)`.
6. Hand-eyeball read of cell values is plausible against OH 2025 statute text (~10 minutes per model).
7. Cell-by-cell side-by-side comparison between Claude and GPT — record agreements and disagreements. (Not a pass/fail criterion on its own, but the comparison is part of the deliverable.)

If any of (1)–(5) fail, **stop and report rather than patching**. The failure mode is the deliverable.

---

## Implementation steps

### Step 1 — Relocate `EvidenceSpan` to break the import cycle

**Current state:** `models_v2/cells.py:23` imports `from lobby_analysis.retrieval_v2.models import EvidenceSpan` for the `CompendiumCell.provenance` type annotation. This triggers `retrieval_v2/__init__.py` → `retrieval_v2/tools.py:22` (`from lobby_analysis.chunks_v2 import build_chunks`) → cycle when `chunks_v2` is the entry point.

**Fix:** Move `EvidenceSpan` to a foundational location. Recommended: `src/lobby_analysis/models_v2/citations.py` (new file). Reasoning: `EvidenceSpan` is a Citations-API span primitive used (or potentially used) by both cells (`models_v2`) and cross-references (`retrieval_v2`); it's foundational provenance, not retrieval-specific. `models_v2/` is the natural home — no v2 module depends on it, and both `cells.py` and `retrieval_v2/models.py` can import from there without cycling.

**Steps:**
1. Create `src/lobby_analysis/models_v2/citations.py` containing the current `retrieval_v2.EvidenceSpan` class definition verbatim (Citations-API shape — `citation_type`, `cited_text`, `document_index`, `document_title`, `start_char_index`, `end_char_index`, `start_page_number`, `end_page_number`, `start_block_index`, `end_block_index`, plus the Pydantic config). Re-export from `models_v2/__init__.py`.
2. Update `src/lobby_analysis/models_v2/cells.py:23` to `from .citations import EvidenceSpan`.
3. Update `src/lobby_analysis/retrieval_v2/models.py` to import `EvidenceSpan` from `lobby_analysis.models_v2.citations` (or `lobby_analysis.models_v2`) instead of defining it locally. Re-export it for backward compatibility (other code does `from lobby_analysis.retrieval_v2 import EvidenceSpan`).
4. Verify cold-load: `uv run python -c "from lobby_analysis.chunks_v2 import build_chunks; print(len({c.chunk_id for c in build_chunks()}))"` returns `15` with no ImportError.
5. Run full test suite: `uv run pytest`. Expectation: same pre-existing 3 baseline failures in `test_pipeline.py` (unrelated), everything else green. If new failures appear, **stop and surface**.
6. **Add a cold-load test** at `tests/test_v2_cold_load.py` containing:
   ```python
   import subprocess, sys
   def test_chunks_v2_loads_cold():
       """Regression: 0979779 introduced an import cycle that tests
       didn't catch because they imported lazily inside functions.
       This test invokes a fresh interpreter so cold-load order matches
       what scripts and orchestrators actually do."""
       result = subprocess.run(
           [sys.executable, "-c", "from lobby_analysis.chunks_v2 import build_chunks; build_chunks()"],
           capture_output=True, text=True,
       )
       assert result.returncode == 0, f"cold load failed:\n{result.stderr}"
   ```
7. Commit: `models_v2: relocate EvidenceSpan to models_v2.citations (breaks import cycle)`.

### Step 2 — Add openai SDK

- `uv add openai` (project-level, not dev — the smoke-test script imports it).
- Verify: `uv run python -c "import openai; print(openai.__version__)"` returns ≥ 1.0.
- Commit: `deps: add openai SDK for cross-model smoke test`.

### Step 3 — Write the inline tool schema + parser

Both Claude and GPT consume the same logical tool. Define once as a shared JSON Schema dict; build SDK-specific wrappers.

Place all of this in `scripts/tier_0_direct_read_smoke.py` (no new package — YAGNI per the originating convo). Inline, not modular.

**Shared schema (proposed):**

```python
RECORD_CELL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "row_id": {"type": "string", "description": "Compendium row id (one of the chunk's row_ids)."},
        "axis": {"type": "string", "enum": ["legal", "practical"]},
        "value": {
            # Loose JSON; parser validates per-cell-class after registry lookup.
            "oneOf": [
                {"type": "number"}, {"type": "integer"}, {"type": "string"},
                {"type": "boolean"}, {"type": "array"}, {"type": "object"}, {"type": "null"},
            ],
        },
        "condition_text": {"type": ["string", "null"]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "cited_section": {
            "type": "string",
            "description": "Free-text statute section reference, e.g. '§101.85(B)(2)' or 'section 101.85 of the Revised Code'.",
        },
        "justification": {
            "type": "string",
            "description": "One sentence explaining how the cited section supports the value. Used by the downstream verifier.",
        },
    },
    "required": ["row_id", "axis", "value", "confidence", "cited_section", "justification"],
}

RECORD_UNSCOREABLE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "row_id": {"type": "string"},
        "axis": {"type": "string", "enum": ["legal", "practical"]},
        "reason": {"type": "string", "description": "Why this cell could not be scored from the bundle (e.g., 'penalty schedule referenced but §307.99 not included')."},
    },
    "required": ["row_id", "axis", "reason"],
}
```

**Anthropic wrapper:**

```python
ANTHROPIC_TOOLS = [
    {"name": "record_cell", "description": "...", "input_schema": RECORD_CELL_INPUT_SCHEMA},
    {"name": "record_unscoreable_cell", "description": "...", "input_schema": RECORD_UNSCOREABLE_INPUT_SCHEMA},
]
```

**OpenAI wrapper:**

```python
OPENAI_TOOLS = [
    {"type": "function", "function": {"name": "record_cell", "description": "...", "parameters": RECORD_CELL_INPUT_SCHEMA}},
    {"type": "function", "function": {"name": "record_unscoreable_cell", "description": "...", "parameters": RECORD_UNSCOREABLE_INPUT_SCHEMA}},
]
```

**Parser:** one function `parse_response(response, sdk: Literal["anthropic", "openai"]) -> list[dict]` that returns a list of `(tool_name, input_dict)` pairs. Anthropic: iterate `response.content` for `tool_use` blocks. OpenAI: iterate `response.choices[0].message.tool_calls`, parsing the `function.arguments` JSON string. ~30 lines.

**Unit tests** (TDD per researcher coding norms): freeze a handful of fixture responses (one Anthropic, one OpenAI) after the first successful run. Tests assert: (a) parser returns the right number of tool calls; (b) each tool call's input dict has all required fields; (c) parser raises on malformed JSON arguments rather than silently dropping. Run green before proceeding to Step 4.

Commit: `tier-0: inline tool schemas + cross-SDK response parser + parser tests`.

### Step 4 — Write the smoke-test script

`scripts/tier_0_direct_read_smoke.py`. Single file. ~150–200 lines total including the schema/parser from Step 3.

**Behavior:**

1. **Load statute bundle.** Read all 30 `.txt` files under `data/statutes/OH/2025/sections/`. Concatenate with section-header dividers (e.g., `\n\n=== title1-chapter101-101_70.txt ===\n\n`) so the model can cite by filename if it wants.

2. **Build chunk roster.** Load `enforcement_and_audits` from `chunks_v2.build_chunks()`. The chunk has 2 rows × 2 axes = 4 cells; render the roster as text the scorer reads in the user message (row_id, axis, expected_cell_class.__name__).

3. **Compose system prompt:**
   ```
   You are a legal analyst extracting structured answers from US state lobbying disclosure law. You will be shown the full statute text for one state-vintage and asked to answer specific compendium questions about that law.

   For each question, emit `record_cell` with the typed answer, the specific section that supports it, and a one-sentence justification.

   If a question's answer requires information not present in the bundled statute text (e.g., the law references a penalty schedule in a different chapter that isn't shown), emit `record_unscoreable_cell` with a brief reason. Do not guess.

   Your response will be independently verified by another model reading the cited section. Cite precisely.

   === STATUTE TEXT FOLLOWS ===

   <concatenated bundle here>
   ```
   Cache the system block (`cache_control: ephemeral` for Anthropic; OpenAI prompt-caches automatically).

4. **Compose user message:** chunk roster + instruction to answer all 4 cells.

5. **Dispatch both models in parallel** (or sequentially; doesn't matter for one chunk). Capture raw response objects.

6. **Save raw responses** to:
   - `results/20260518_tier_0_raw_claude_enforcement_and_audits.json`
   - `results/20260518_tier_0_raw_gpt_enforcement_and_audits.json`
   Each with provenance header: `<!-- Generated during: convos/20260518_tier_0_execution_pivot_to_direct_read.md -->`

7. **Parse both responses** via the Step-3 parser. For each tool call, look up `(row_id, axis)` in `build_cell_spec_registry()`, instantiate the appropriate `CompendiumCell` subclass with the typed `value`, attach `cited_section` and `justification` as fields on a thin wrapper (or alongside in the dict — pick whichever is least invasive; `CompendiumCell` itself stays unchanged for now).

8. **Save parsed outputs** to:
   - `results/20260518_tier_0_parsed_claude_enforcement_and_audits.json`
   - `results/20260518_tier_0_parsed_gpt_enforcement_and_audits.json`

9. **Print a side-by-side comparison** to stdout: per cell, show Claude's value vs GPT's value, both citations, both justifications. ~30 lines of text per cell × 4 cells.

10. **Capture cost + wall-clock** for each model. Print at end.

Commit: `tier-0: direct-read smoke-test script (Claude + GPT side-by-side)`.

### Step 5 — Run it

- Verify both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are exported.
- `uv run python scripts/tier_0_direct_read_smoke.py`
- Verify all 6 result files write successfully.
- Verify the printed comparison shows 4 cells from each model.

If the script crashes: **stop, capture the traceback, report.** Do not iterate fixes mid-session beyond obvious typos.

If retrieval emits zero cells or returns malformed responses: **stop, report.** That's the empirical finding for this session.

### Step 6 — Hand-eyeball + writeup

- Read each cited section of OH 2025 statute (the bundle is small; this is ~15 minutes).
- For each cell from each model, judge: does the cited section actually support the claimed value?
- Tally: how many cells match between Claude and GPT? How many disagreements? How many `record_unscoreable_cell` emissions (and were the cross-references actually out-of-bundle)?

Write `results/20260518_tier_0_direct_read_writeup.md` (with provenance header):

- What the script does (~5 lines).
- Per-cell Claude vs GPT comparison (table).
- Hand-eyeball verdict per cell (correct/wrong/can't-tell) for each model.
- Unscoreable rate per model + whether the model was right that the answer was out-of-bundle.
- Wall-clock + cost per model.
- **Architecture verdict:** does direct-read look viable? If yes, what's the next step (more chunks? more vintages? Phase 2 verifier?). If no, what specifically went wrong, and does that re-validate the original Citations+retrieval architecture?
- Surprises encountered.

Commit: `tier-0: direct-read smoke-test writeup + architecture verdict`.

### Step 7 — Finish-convo

- New convo file `docs/active/extraction-harness-brainstorm/convos/<YYYYMMDD>_tier_0_direct_read_execution.md` (date of execution, not 20260518 — that's the planning date).
- Back-link from this convo file to the writeup.
- Prepend a session entry to `RESEARCH_LOG.md` (newest first).
- Append one line to `STATUS.md` under "Recent Sessions" (do not rewrite other content).
- Commit + push. Do not merge to main.

---

## Edge cases to anticipate

- **Statute bundle exceeds context window.** OH 2025 bundle is ≈ 50K tokens. Both Opus 4.7 (200K window) and GPT-5.2 (long window) handle this with room. If a future state has a much larger statute, this assumption fails — but for OH 2025, it holds. Verify token count before dispatch: `len(bundle_text) / 4` ≈ token estimate.
- **Model emits a different tool name** (typo, hallucination). Parser should log and skip the tool call rather than crash. Surface count of skipped tool calls in writeup.
- **Model emits `record_cell` with a `(row_id, axis)` not in the chunk.** Same — log, skip, surface count.
- **Cell `value` doesn't type-check against `expected_cell_class`.** Pydantic will raise. Wrap each instantiation in try/except so one bad cell doesn't kill the run; record the failure.
- **One model dispatches, the other fails.** Save what you got. Writeup notes the asymmetry; don't artificially skip the successful one.
- **Cost overrun.** If either model's call costs >$1, stop and investigate before iterating. Budget ceiling: $5 total across the session.
- **All cells come back as `record_unscoreable_cell`.** That's a meaningful finding — direct-read isn't viable for enforcement_and_audits on OH 2025. Writeup names what was missing; this re-validates the Citations+retrieval architecture as the next path.

---

## Confidence checkpoints — don't barrel through

| Checkpoint | If it fails... |
|---|---|
| Cold-load test passes after Step 1 | Stop; EvidenceSpan relocation didn't break the cycle; surface the new trace |
| `uv run pytest` green after Step 1 | Stop; the relocation broke something downstream; surface |
| Script runs to completion on both models | Stop; the wiring isn't working; capture traceback |
| Each model emits 4 record_cell or record_unscoreable_cell calls | Stop if 0 or far more; the prompt isn't scoping output correctly |
| Cells type-check against expected_cell_class | Stop if mass failure; the prompt isn't getting the value shape across |

---

## After Tier 0 — what comes next (forward-pointer)

Two branches depending on what Tier 0 produces:

**If direct-read looks viable** (most cells correct on hand-eyeball, low unscoreable rate, Claude/GPT mostly agree):
- **Tier 1 direct-read** — same architecture across the 6 chunks covering CPI 2015's 6 de-jure items. σ_noise via N=3 re-runs per model. Compare both models against CPI 2015 OH 2010 / 2025 published scores (after the projection function lands on `phase-c-projection-tdd`).
- **Verifier agent (Phase 2)** — separate plan. Take each model's `cited_section` + `justification` + cell value, dispatch a verifier prompt (cross-model: GPT verifies Claude, Claude verifies GPT), produce agree/disagree judgments. Disagreements get flagged for human review.

**If direct-read looks broken** (high unscoreable rate due to out-of-bundle cross-refs, or low Claude/GPT agreement, or many cells hand-eyeball wrong):
- **Escape hatch: Citations + retrieval + bundle expansion.** The 1380-line `scoring_v2` impl plan ([`20260514_brief_writer_implementation_plan.md`](20260514_brief_writer_implementation_plan.md)) was written for this case. Ship `scoring_v2/` as a proper module per that plan, build the orchestrator that iterates retrieval hops, then redo Tier 0 against the expanded bundle.

The Tier-0 writeup is the empirical signal that picks which branch.

---

## Out of scope (do not do, even if tempted)

- Other chunks beyond `enforcement_and_audits`.
- Other state-vintages.
- Projection comparison (CPI / PRI / Sunlight / Newmark / Opheim / HG / FOCAL — none of these).
- σ_noise re-runs (Tier 1's job).
- Packaging the inline script as a `scoring_v2/` module.
- Building the verifier agent (Phase 2's job).
- Refactoring `models_v2` / `chunks_v2` / `retrieval_v2` beyond the EvidenceSpan relocation in Step 1.
- Citations API plumbing (deferred to the escape-hatch path if Tier 0's verdict requires it).
- Any test infrastructure beyond the cold-load regression test (Step 1) + the parser unit tests (Step 3).

---

## Testing details

- **Cold-load smoke test** (Step 1, Step 6): mandatory regression — the cycle that bit the prior session was hidden by lazy-inside-function imports. The cold-load test catches it from a fresh interpreter.
- **Parser unit tests** (Step 3): frozen fixtures from the first successful real run. Not mocks of behavior. Verify wiring shape, not Pydantic semantics.
- **The smoke run itself** is the integration test for the full pipeline. Pass/fail criteria above.

NOTE: I will write the cold-load test + parser unit tests *before* the smoke-test dispatch logic. Step 5's run is the empirical deliverable, not a thing tests can stand in for.

---

## Implementation details

- Script lives at `scripts/tier_0_direct_read_smoke.py` — single file, inline, no new packaged module.
- Results files get the provenance header: `<!-- Generated during: convos/20260518_tier_0_execution_pivot_to_direct_read.md -->`.
- All paths relative to worktree root unless prefixed `/Users/...`.
- Models: Anthropic `claude-opus-4-7`, OpenAI `gpt-5.2-2025-12-11`. Override only with documented reason in the writeup.
- Cost budget: ≈ $0.60 expected, $5 ceiling.
- Per multi-committer rules: `phase-c-projection-tdd` and `oh-statute-retrieval` are sister branches with active work. Do NOT modify them. If Tier 0 surfaces a need for changes to shared infrastructure, stop and surface.

---

## What could change

- **Direct-read's coverage of cross-referenced sections.** OH 2025's Chapter 101 may or may not be self-contained for `enforcement_and_audits`. If §101.99 says "penalties under §307.99" and the bundle doesn't include §307.99, the scorer should emit `record_unscoreable_cell`. The unscoreable rate IS the architectural signal.
- **Claude vs GPT prompt-following parity.** GPT may handle the document-in-system-prompt + per-chunk-question pattern differently than Claude. Surprises here become input to the writeup.
- **`record_cell.value` field's loose JSON typing.** May fail to type-check against `expected_cell_class` for shaped cells (`TimeThresholdCell`, etc.). If this happens often, the schema may need to be stricter — but that's a Tier-1 problem.

---

## Questions (for the implementer to surface, not pre-decide)

1. **EvidenceSpan home — `models_v2/citations.py` or a new top-level `lobby_analysis/citations.py`?** This plan proposes the former. If a reason surfaces during Step 1 to prefer the latter (e.g., another non-v2 module wants the type), surface to user before committing.

2. **Concrete prompt language for the adversarial framing.** This plan proposes "your response will be independently verified by another model reading the cited section." If empirical prompt-engineering literature has a sharper phrasing, use that and note the source in the writeup.

3. **How to surface `cited_section` and `justification` in the saved parsed output?** `CompendiumCell` (per `0979779`) doesn't have these fields. Options: (a) wrap each cell in a `{cell: CompendiumCell, cited_section: str, justification: str}` dict; (b) extend `CompendiumCell` with optional fields (touches `models_v2`); (c) save them as a separate parallel structure keyed by `(row_id, axis)`. Plan proposes (a) for YAGNI — least invasive, doesn't touch `models_v2`. Reopen if (b) becomes obviously cleaner during implementation.

4. **Cost ceiling reconsideration?** $5 across the session feels generous for ≈ $0.60 of actual dispatch. Lower it (say, $2) for tighter discipline, or keep $5 for headroom on retries?

# Handoff: write the brief-writer + scorer-prompt-v2 implementation plan

**Date written:** 2026-05-14
**Written by:** the agent that ran the brief-writer brainstorm end-to-end this session (all 10 Q's + 2 pushbacks locked; full decision audit trail in the convo).
**For:** the next agent picking up the implementation-plan-write step on `extraction-harness-brainstorm`.

## Handoff sentence

Working on `extraction-harness-brainstorm`; the brief-writer brainstorm completed 2026-05-14 with all architectural Q's locked. Your job is to write `plans/20260514_brief_writer_implementation_plan.md` — TDD-shaped, API-launchable, mirroring the retrieval implementation plan's shape and rigor — then run finish-convo. The locked package is fully specified in the brainstorm convo's "Locked package (synthesis)" section; you are NOT re-litigating decisions, only translating them to a TDD-shaped phased plan with inlined tool schemas, prompt content, and test signatures. **Two pushbacks against the user's prior framing were accepted this session** (combine brief-writer + scorer-prompt rewrite; defer practical-axis to a sibling brainstorm) — those are now locked context, not open Q's.

## Where things stand

**Completed and committed in this branch this session:**

- `docs/active/extraction-harness-brainstorm/plans/20260514_brief_writer_plan_sketch.md` — brainstorm-first agenda, with outcome back-link at the top
- `docs/active/extraction-harness-brainstorm/convos/20260514_brief_writer_brainstorm.md` — Phase 1 reading recap + 10 Q's + 2 pushbacks locked + full audit trail + "Locked package (synthesis)" section + "Things this brainstorm is locking blind on"

**To be added by your session:**

- `docs/active/extraction-harness-brainstorm/plans/20260514_brief_writer_implementation_plan.md` — TDD-shaped impl plan (your deliverable)
- RESEARCH_LOG.md entry for the impl-plan-write session (chained from this session's entry)
- STATUS.md row update (only this branch's row, per multi-committer rules)

**Branch sync at handoff time:** TBD by this session's finish-convo commit. Your session starts by `git pull --ff-only origin extraction-harness-brainstorm` to pick up the brainstorm commit.

## The locked package (verbatim from the brainstorm convo's synthesis)

Read the convo's "Locked package (synthesis)" section in full. The 6-piece deliverable:

1. **`src/lobby_analysis/scoring_v2/` module** — parallel to `retrieval_v2/`:
   - `models.py` — `ScoringOutput` + `UnscoreableCell` (new Pydantic models, frozen, mirror `RetrievalOutput` + `UnresolvableReference`).
   - `tools.py` — `RECORD_CELL_TOOL` + `RECORD_UNSCOREABLE_CELL_TOOL`. Coupling test: any `row_id` enum in tool schema (if used) sourced from `build_cell_spec_registry()` keys.
   - `brief_writer.py` — `build_scoring_brief(state, vintage, chunks: list[str], retrieval_output: RetrievalOutput, statute_bundle: list[dict], url_pattern: str = "") -> dict`. Loads optional preambles from `src/scoring/chunk_frames_v2/<chunk_id>.md` if present, skips silently if not.
   - `parser.py` — `parse_scoring_response(message, state_abbr, vintage_year, chunk_id) -> ScoringOutput`. Pairing rule: citations on text blocks accumulate; on `record_cell`/`record_unscoreable_cell` tool_use, flush onto that tool call's `evidence_spans`/`provenance` and reset. Unknown tool names reset. Polymorphic over SDK `Message` objects (attr access) and JSON dicts (key access) — same path works for fixtures + real responses.
   - `__init__.py` — public exports: `ScoringOutput`, `UnscoreableCell`, `build_scoring_brief`, `parse_scoring_response`.
   - `docs.md` — module-level docs matching `retrieval_v2`/`chunks_v2`/`models_v2` pattern.

2. **`src/scoring/scorer_prompt_v2.md`** — the v2 scoring prompt. Plan must **inline the full prompt text** (precedent: retrieval impl plan inlined `retrieval_agent_prompt_v2.md` in full; chunks impl plan inlined the 15-chunk manifest in full). Load-bearing artifacts are plan-anchored. Prompt requirements:
   - Drops rubric language; cell-anchored ("you will score cells from a chunk's `cell_specs`").
   - Drops Rules 1, 7 (Citations + tool-use structurally enforce); replaces Rules 6, 8 (preambles + tool-use); morphs Rule 3 (per-tool parser validation); keeps Rules 2 (escape valve = `record_unscoreable_cell`), 4 (confidence), 5 (read full statute layered).
   - Promotes Rule 5 ("read full statute layered: rule → exemption → exception → separate triggers") as load-bearing.
   - Instruction: "cite (via Citations API) before each tool call" — makes the parser's pairing rule non-vacuous.
   - **No PRI keys** (`A5`-`A11`, `C0`-`C3`) remain as word-boundary tokens — verified by `test_prompt_invariants.py`.

3. **`src/scoring/chunk_frames_v2/.gitkeep`** — directory exists, **0 preamble files**. Brief-writer's path resolution gracefully handles absent preambles. Per the brainstorm's Q4 lock, scholarly preamble authoring is downstream work.

4. **`src/lobby_analysis/models_v2/cells.py` edit** — `provenance: tuple[EvidenceSpan, ...] = ()` (was `EvidenceSpan | None = None`). All existing tests/fixtures that construct `CompendiumCell` with `provenance=None` or `provenance=<single EvidenceSpan>` need updating. **Audit at impl-plan-write time:** grep tests + fixtures for `provenance=` usages; list updates in plan.

5. **Tests, written RED first per TDD:**
   - `test_scoring_v2_tools.py` — tool schemas (`RECORD_CELL_TOOL`, `RECORD_UNSCOREABLE_CELL_TOOL`); coupling tests against `build_cell_spec_registry()`.
   - `test_scoring_v2_models.py` — `ScoringOutput` frozen-ness; `UnscoreableCell` shape; field types.
   - `test_scoring_v2_brief_writer.py` — `build_scoring_brief()` assembly + validation: unknown chunk_id raises; document blocks correct shape with `citations.enabled=True`; system block contains scorer_prompt_v2.md; user text contains state/vintage/cell roster + retrieval annotations; preamble loading IF `chunk_frames_v2/<chunk_id>.md` exists (test with tmp file).
   - `test_scoring_v2_parser.py` — fixture-based: hand-crafted Message JSON with N `record_cell` + M `record_unscoreable_cell` tool calls + citations on preceding text; parser produces `ScoringOutput` with right subclass per cell (via `expected_cell_class` lookup) + evidence_spans attached + `unscoreable_cells` populated.
   - `test_scoring_v2_prompt_invariants.py` — `scorer_prompt_v2.md` is non-empty; mentions Citations API instruction; mentions tool-use enforcement; **does NOT** contain word-boundary `A5`-`A11`, `C0`-`C3`, `rubric`, `files_read.json`, `unable_to_evaluate` (replaced by `record_unscoreable_cell`).
   - `test_scoring_v2_integration.py` — T1 smoke; `skipif` on `ANTHROPIC_API_KEY`; tiny statute fixture + 1 chunk against OH 2010 short excerpt; verifies ≥1 cell with non-empty `evidence_spans`; cost ≈ $0.05 per run. **Inherits the same side-effect-on-fixture flag from retrieval's T1** (see brainstorm's "Things this brainstorm is locking blind on" section).

6. **`pyproject.toml`** — no new dependencies (`anthropic>=0.102` + `pydantic` already in from retrieval).

## Plan-write shape (mirror retrieval impl plan structure)

Re-read [`../20260514_retrieval_implementation_plan.md`](../20260514_retrieval_implementation_plan.md) end-to-end as your structural template. The retrieval plan has:

- Header with Branch, Prerequisite section (chunks must have shipped), Phase 0 status, Goal
- "What this plan ships / does not ship" section
- "Cells in scope" table or equivalent (you adapt: "Chunks in scope" mapping chunk_id → axis_summary → cell count)
- Phase-by-phase TDD plan (one commit per phase; each phase turns its target test file green)
- **Full prompt inlined** in its phase (precedent: retrieval did this in Phase 6)
- **Full tool schemas inlined** in their phase
- **30+ test signatures listed by name** across the 6 test files
- Integration-test gate description
- Testing Plan section
- "Things that may go wrong" / pause-and-surface instructions

**Phase order suggestion (mirror retrieval):** scaffolding → RED tests → models (Phase 3 equivalent) → tools (Phase 2 equivalent) → prompt md (Phase 6 equivalent — must land BEFORE brief_writer per retrieval's executed-out-of-numerical-order precedent if brief_writer.py reads the prompt file at call time) → brief_writer (Phase 4 equivalent) → parser (Phase 5 equivalent) → integration fixture + tiny statute → exports + docs.md + ruff.

**Critical:** if `brief_writer.py` reads `scorer_prompt_v2.md` at call time (it should, mirroring retrieval), the prompt-write phase MUST land BEFORE the brief_writer green phase. Retrieval session's "Plan deviations surfaced and resolved" entry #1 documents this exact lesson — don't repeat the audit-trail problem.

## What you do NOT decide

**These are LOCKED by the brainstorm — do not re-open in the plan:**

- Single polymorphic `record_cell` tool (Q2). If you have doubts, surface to user via AskUserQuestion — but expect to ship with this.
- `UnscoreableCell` + `record_unscoreable_cell` tool (Q7-sub). Symmetry with retrieval is intentional.
- Per-chunk preamble strategy = optional disk-loaded, ship 0 (Q4). Do NOT author preambles in the impl plan.
- `provenance: tuple[EvidenceSpan, ...]` schema change (Q8).
- File location `src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md` (Q10).
- Practical-axis scope deferred to sibling brainstorm (Q6). Brief-writer signature assumes legal-axis chunks; parser may emit warning (not error) if model emits practical-axis cell tool call, but don't design around practical-axis cells.

## What you DO decide

**Smaller plan-level decisions that don't change the locked package:**

- Exact phase numbering + commit messages (your call, but match retrieval's phase-named pattern).
- Specific test signatures (the convo names ~30 by name; you can add more, can't drop the named ones).
- Exact JSON schema details for `RECORD_CELL_TOOL.input_schema.value` (loose JSON; ` oneOf: [number, integer, string, boolean, array, object, null]`). Make a call; document.
- Whether `RECORD_CELL_TOOL` has a `row_id.enum` sourced from registry, or just a string with parser-side validation. (Coupling test against the registry is the same either way.) Make a call; document.
- Exact prompt-text wording (you draft the full v2 prompt to inline). User reviews at the next stage (impl session).

## Critical context (don't re-derive)

### The retrieval brief-writer precedent

`src/lobby_analysis/retrieval_v2/brief_writer.py` is the load-bearing template. Read it end-to-end. Specifically:

- Returns kwargs dict; does NOT call SDK.
- `system` block = prompt text with `cache_control: ephemeral`.
- `messages[0].content = [doc_block_1, ..., doc_block_N, {type: "text", text: user_text}]`. Document blocks ephemeral-cached.
- `_format_cell_roster()` produces per-chunk markdown sections in user text.
- `_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "src" / "scoring" / "..."` — same path-resolution pattern.
- Model `claude-opus-4-7`, `max_tokens=16000`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`. **No sampling params** (Opus 4.7 returns 400).

Use the same constants, the same structure. Differences for scoring:

- Additional input: `retrieval_output: RetrievalOutput`. Brief-writer appends "Retrieval annotations" section to user text after the cell roster, summarizing per cross-reference (section_reference, relevance, chunk_ids_affected, key evidence_spans excerpted).
- Optional per-chunk preamble loading: before the cell roster, brief-writer inserts the preamble if `chunk_frames_v2/<chunk_id>.md` exists. Multi-chunk calls: concatenate preambles in chunk order.

### `RetrievalOutput` shape (your input)

```python
class RetrievalOutput(BaseModel):
    state_abbr: str
    vintage_year: int
    hop: int  # 1 or 2
    cross_references: tuple[CrossReference, ...]
    unresolvable_references: tuple[UnresolvableReference, ...]

class CrossReference(BaseModel):
    section_reference: str
    chunk_ids_affected: tuple[str, ...]
    relevance: str
    justia_url: str
    url_confidence: Literal["high", "medium", "low"]
    url_confidence_reason: str
    evidence_spans: tuple[EvidenceSpan, ...]
```

The scoring brief includes the retrieval cross_references filtered to the brief's chunks (`any(c in chunks for c in cross_ref.chunk_ids_affected)`). Unfilterable: include all.

### `ScoringOutput` shape (your output)

```python
class ScoringOutput(BaseModel):
    model_config = {"frozen": True}
    state_abbr: str
    vintage_year: int
    chunk_id: str  # scoped to one call per brainstorm Q9
    cells: tuple[CompendiumCell, ...] = ()
    unscoreable_cells: tuple[UnscoreableCell, ...] = ()

class UnscoreableCell(BaseModel):
    model_config = {"frozen": True}
    cell_id: str  # matches CompendiumCellSpec.row_id + axis convention
    reason: str
    confidence: ConfidenceLevel  # from models_v2 — reuse, don't redefine
    evidence_spans: tuple[EvidenceSpan, ...] = ()
```

If a `build_scoring_brief()` call covers multiple chunks (parameterized list), the parser may produce one `ScoringOutput` per chunk_id, OR `chunk_id` becomes `tuple[str, ...]` to scope to the multi-chunk call. Make the call; document. Hunch: per-call `chunk_id: str`, with default per-chunk dispatch (Q1) → single chunk_id per call is the common path; multi-chunk calls are advanced usage.

### `CompendiumCell.provenance` schema edit blast radius

Run `grep -rn "provenance=" tests/ src/` before the plan ships. Audit list goes in the plan's "Things to update" section.

### Practical-axis chunks and dual-axis chunks

Per Q6 = defer practical:

- **Practical-only chunks** (the 4 `search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website`) → brief-writer cannot score these; caller (orchestrator, out of scope) should not pass them.
- **Mixed chunks** (the 5 with `axis_summary="mixed"`: `lobbying_definitions`, `registration_mechanics_and_exemptions`, `lobbyist_spending_report`, `enforcement_and_audits`, `oversight_and_government_subjects`) → brief-writer scores only the `axis == "legal"` cells; filter `chunk.cell_specs` accordingly. Practical cells in mixed chunks will be scored by the sibling practical-axis brief-writer later.

Brief-writer behavior: when filtering, if a chunk has 0 legal cells after filtering, raise `ValueError` (don't silently produce an empty brief). User would want to catch this misuse.

### Carry-forward links

In session-start order:

1. [`../../../../STATUS.md`](../../../../STATUS.md) — current focus
2. [`../../../../README.md`](../../../../README.md) — project framing
3. [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — branch trajectory; brief-writer brainstorm entry at top
4. [`../../convos/20260514_brief_writer_brainstorm.md`](../../convos/20260514_brief_writer_brainstorm.md) — **the brainstorm convo; read in full, especially "Locked package (synthesis)"**
5. [`../20260514_brief_writer_plan_sketch.md`](../20260514_brief_writer_plan_sketch.md) — the agenda; outcome back-link at top
6. [`../20260514_retrieval_implementation_plan.md`](../20260514_retrieval_implementation_plan.md) — **structural template for your plan; mirror its phase shape**
7. [`../../convos/20260514_retrieval_implementation.md`](../../convos/20260514_retrieval_implementation.md) — retrieval impl session's "Plan deviations surfaced and resolved" section — read for the phase-order lesson (Phase 6 had to land before Phase 4 because brief_writer reads prompt at call time)
8. [`../../../../src/scoring/scorer_prompt.md`](../../../../src/scoring/scorer_prompt.md) — v1 scorer prompt, your rewrite source
9. [`../../../../src/lobby_analysis/retrieval_v2/`](../../../../src/lobby_analysis/retrieval_v2/) — load-bearing pattern template for your module

## What this handoff does NOT do

- **Does not draft the v2 prompt content.** That's your plan-write work — inline it in the plan, mirroring how retrieval inlined `retrieval_agent_prompt_v2.md`.
- **Does not draft the JSON tool schemas.** Same — inline in plan.
- **Does not write the impl tests.** Tests are written RED first by the IMPLEMENTATION agent (separate session), per TDD discipline. Your plan LISTS test signatures by name; the impl agent writes the test bodies.
- **Does not re-open the locked Q's.** If during plan-write you discover a hole in the locked package, surface to the user explicitly — don't unilaterally re-decide.
- **Does not commit to a Phase C audit script for the `provenance` schema change.** The plan flags this as "things to update in same commit"; the impl agent does the grep + updates.

## After your session (post-impl-plan)

- **Implementation session** — separate API-launched sub-branch of `extraction-harness-brainstorm`; runs through your plan under strict TDD; produces commits per phase; ends with finish-convo. Same pattern as retrieval's impl session.
- **Practical-axis brief-writer brainstorm** (sibling) — your session does NOT do this, but it's the next brainstorm in the queue after legal-side impl ships. Or interleaved if user prefers.
- **End-to-end pilot** — legal-axis brief-writer + retrieval + cell-models integrated against one (state, vintage) — downstream of impl session.

## Cycle convention (same as the prior components)

1. **Plan sketch (done)** — `plans/20260514_brief_writer_plan_sketch.md`. Read it for the agenda-shape record.
2. **Brainstorm convo (done)** — `convos/20260514_brief_writer_brainstorm.md`. Read in full.
3. **Implementation plan (TO WRITE)** — `plans/20260514_brief_writer_implementation_plan.md`. **Your deliverable.** TDD-shaped, API-launchable. Mirror retrieval's plan shape.
4. **Implementation session** — separate API-launched sub-branch; not in scope for your session.

## Don't skip the convo's "Things this brainstorm is locking blind on" section

The brainstorm flagged three lock-blind areas. Your plan should reference them, surface them in the impl plan's "Things that may go wrong" section, and inherit retrieval's pause-and-surface posture for the integration test phase:

- Citations API + tool use composition behavior under longer statutes + more tool calls per response. Retrieval's T1 smoke (deferred to desktop) is the canary. If retrieval's parser pairing rule turns out to mismatch reality, scoring inherits the fix.
- `CompendiumCell.provenance` schema change tolerance — verify Phase C hasn't started consuming the single-span shape before shipping.
- Practical-axis brief-writer feasibility — entirely out of scope but flagged in sibling-brainstorm queue.

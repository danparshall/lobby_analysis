# Scoring v2 Brief-Writer + Scorer-Prompt-v2 — Implementation Plan

**Branch:** `extraction-harness-brainstorm`
**Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`
**Originating brainstorm:** [`../convos/20260514_brief_writer_brainstorm.md`](../convos/20260514_brief_writer_brainstorm.md) — read in full; especially the "Locked package (synthesis)" and "Things this brainstorm is locking blind on" sections.
**Plan sketch (agenda-shape):** [`20260514_brief_writer_plan_sketch.md`](20260514_brief_writer_plan_sketch.md)
**Written-from handoff:** [`_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`](_handoffs/20260514_brief_writer_impl_plan_write_handoff.md)
**Structural template:** [`20260514_retrieval_implementation_plan.md`](20260514_retrieval_implementation_plan.md) — mirror its phase shape, inlined-prompt pattern, inlined-tool-schemas pattern, named-test-signature pattern, "Things that may go wrong" pattern.
**Sibling impl-convo (load-bearing lessons):** [`../convos/20260514_retrieval_implementation.md`](../convos/20260514_retrieval_implementation.md) — read its "Plan deviations surfaced and resolved" section for the prompt-md-must-land-before-brief-writer lesson; baked into this plan's phase ordering from the start.

**Goal:** Ship the v2 legal-axis **scoring** harness — a parallel of `retrieval_v2/` that consumes a `RetrievalOutput` plus a statute bundle and emits typed `CompendiumCell` instances per chunk via the Anthropic Citations API + tool use. The output container is `ScoringOutput` (one per chunk call); unscoreable cells route through a `record_unscoreable_cell` tool and surface as `UnscoreableCell` instances (parallel to retrieval's `UnresolvableReference`). Unblocks the orchestrator + the first end-to-end Ralph-loop iteration (per RESEARCH_ARC); the Tier-0 smoke test ([`20260518_tier_0_minimal_pipeline.md`](20260518_tier_0_minimal_pipeline.md)) is the first downstream consumer.

## ⚠ PREREQUISITES — all already shipped

This plan is **executable today** (no upstream blockers). Prerequisites listed for the implementer's pre-flight verification:

- **`models_v2`** (`src/lobby_analysis/models_v2/`) — shipped; `CompendiumCell` ABC + 15 concrete subclasses + `build_cell_spec_registry()` + `EvidenceSpan` (the statute-semantic one, **NOT** the one this plan reuses — see audit below).
- **`chunks_v2`** (`src/lobby_analysis/chunks_v2/`) — shipped; `build_chunks()` returns 15 `Chunk` instances with `axis_summary ∈ {legal, practical, mixed}`.
- **`retrieval_v2`** (`src/lobby_analysis/retrieval_v2/`) — shipped through T1 (commit `5f262e9` chain); `RetrievalOutput`, `CrossReference`, `UnresolvableReference`, `EvidenceSpan` (Citations-API-shape) are imported by the scoring brief-writer and parser. **This is the `EvidenceSpan` `CompendiumCell.provenance` will hold a tuple of** — see Phase A and the audit-at-plan-write-time section below.
- **`anthropic>=0.102`** in `pyproject.toml` — live since the retrieval impl session. No new dependencies.

If any of the above is missing on your branch HEAD, **stop and surface to user** rather than attempting to ship `scoring_v2` standalone.

**You (implementer) start with zero codebase context.** This plan is self-contained — the prompt is inlined in full, the tool schemas are inlined in full, every test signature is named. Read the brainstorm convo first for the *why*; this plan covers the *what* and the *how*.

---

## Tech Stack

- Python 3.12 (project requirement)
- `uv` for env management; existing `.venv/`
- `pytest` (in `dev` extras) for tests
- `ruff` (in `dev` extras) for lint
- `pydantic >= 2.8` (top-level dep)
- `anthropic >= 0.102` (top-level dep; shipped by retrieval)

**No new `pyproject.toml` edits.** Verify with `uv run python -c "import anthropic; print(anthropic.__version__)"` — expect `0.102.0` or newer.

---

## Locked decisions (brainstorm reference — DO NOT REOPEN)

If during implementation you discover what feels like a hole in any of these, **pause and surface to the user via AskUserQuestion**. The handoff explicitly mandates this — do not unilaterally re-decide.

| Q | Lock | Source |
|---|---|---|
| Q1 dispatch unit | `chunks: list[str]`, default per-chunk call | Brainstorm Q1 |
| Q2 tool use shape | Single polymorphic `record_cell` + `record_unscoreable_cell` (2 tools total) | Brainstorm Q2 + Q7-sub |
| Q3 statute bundle | All statutes (same set retrieval consumed) + retrieval annotations as user text | Brainstorm Q3 |
| Q4 per-chunk preambles | Optional disk-loaded from `src/scoring/chunk_frames_v2/<chunk_id>.md`; ship 0 | Brainstorm Q4 |
| Q5 substantive guidance | Lives in preambles (when authored), NOT in `CompendiumCellSpec` | Brainstorm Q5 |
| Q6 practical-axis | **Deferred to sibling brainstorm.** This plan ships legal-axis only | Brainstorm Q6 |
| Q7-rules | Drop v1 Rules 1, 7; replace 6, 8; morph 3; keep 2 (via Q7-sub), 4, 5 | Brainstorm Q7-rules |
| Q7-sub unscoreable | Separate `UnscoreableCell` model + `record_unscoreable_cell` tool | Brainstorm Q7-sub |
| Q8 provenance | `CompendiumCell.provenance: tuple[EvidenceSpan, ...] = ()`. The `EvidenceSpan` is **`retrieval_v2.EvidenceSpan`** (Citations-API shape), not `models_v2.EvidenceSpan` (statute-semantic shape) — see post-framing review F1 resolution at Tier-0 plan Step 2. | Brainstorm Q8 + post-framing F1 |
| Q9 output container | `ScoringOutput` mirroring `RetrievalOutput`; `chunk_id: str` (one per call) | Brainstorm Q9 |
| Q10 file location | `src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md` | Brainstorm Q10 |
| Model/thinking/effort | `claude-opus-4-7`, `thinking={"type": "adaptive"}`, `output_config={"effort": "high"}`; no sampling params (Opus 4.7 returns 400) | Mirror retrieval |
| Prompt caching | System block ephemeral-cached; statute document blocks ephemeral-cached; per-call user text uncached | Mirror retrieval |

---

## Decisions made at plan-write time (these are MINE, not the brainstorm's)

The handoff named the smaller decisions the plan-writer makes without re-opening locked Q's. Recording them here for the implementer's reference:

1. **`RECORD_CELL_TOOL.input_schema.row_id` is a `string` with parser-side validation, NOT an enum sourced from `build_cell_spec_registry()`.** Rationale: 186 row_id × 2 axis = a 186-entry enum would inflate every tool-schema dump, and the parser already does cell-class dispatch via `build_cell_spec_registry()[(row_id, axis)].expected_cell_class` — so the registry is the single source of truth either way. Enum-on-the-wire is redundant validation, not additional coverage. Coupling test against `build_cell_spec_registry()` lives on the parser side (`test_parser_dispatches_to_expected_cell_class_per_row`) regardless of where the enum lives. **The handoff explicitly allowed either choice.**
2. **`RECORD_CELL_TOOL.input_schema.value` is `oneOf: [{type: number}, {type: integer}, {type: string}, {type: boolean}, {type: array}, {type: object}, {type: "null"}]`.** Loose JSON; parser validates per-cell-type after `expected_cell_class` lookup. Per Q2, mis-typing surfaces in T2+ empirical evidence, not in the tool schema.
3. **`ScoringOutput.chunk_id: str`** (one per call), per the handoff's hunch. Multi-chunk dispatch is advanced usage; per-chunk default keeps the common path simple. Orchestrator merges per-chunk `ScoringOutput`s into `StateVintageExtraction`.
4. **Phase numbering follows retrieval's pattern.** Commit messages preserve the plan's phase names so the audit trail stays intact even when execution order differs from numerical order (see Phase Ordering note below).
5. **`UnscoreableCell.confidence` is typed as `Literal["high", "medium", "low"]`** (matches `CompendiumCell.confidence` shape — NOT `| None`, since an unscoreable cell that doesn't even self-assess confidence is meaningless). Note: `models_v2.cells` has no exported `ConfidenceLevel` alias — it's an inline `Literal`. The handoff phrased it as "ConfidenceLevel enum your `UnscoreableCell` reuses"; the actual code shape is `Literal["high", "medium", "low"]` and `scoring_v2.models` should mirror that inline rather than introduce a new alias. Flagged to parent session in the report-back.

---

## Phase ordering note (load-bearing — read before executing)

**The prompt markdown phase MUST land BEFORE the brief-writer phase.** The brief-writer reads `src/scoring/scorer_prompt_v2.md` at call time (mirroring retrieval's `_PROMPT_PATH.read_text()` pattern), so brief-writer tests will fail with `FileNotFoundError` if the prompt file doesn't exist yet.

Retrieval's plan-deviation #1 documented this exact lesson (see [`../convos/20260514_retrieval_implementation.md`](../convos/20260514_retrieval_implementation.md) "Plan deviations surfaced and resolved" section). This plan bakes the ordering in from the start: Phase 6 (prompt md) lands **before** Phase 4 (brief-writer) in execution, while commit messages preserve plan-phase-numbered names so the numerical-order audit trail stays intact.

**Execution order:** P0 (scaffold) → P1 (RED tests) → P2 (tools) → P3 (models) → **P6 (prompt md)** → **P4 (brief_writer)** → P5 (parser + fixture) → P7 (provenance schema edit + audit) → P8 (integration) → P9 (exports + docs.md + ruff).

---

## Audit at plan-write time — `provenance=` blast radius

The handoff §"4. `src/lobby_analysis/models_v2/cells.py` edit" requires running `grep -rn "provenance=" tests/ src/` and listing what needs updating. Result (run 2026-05-18 on this worktree's HEAD `488b63d`):

**Total: 1 file, 1 line.**

| File | Line | Current |
|---|---|---|
| `tests/test_models_v2_cells.py` | 69 | `provenance=span,` (single `EvidenceSpan`, not tuple) — inside `test_binary_cell_wrapper_fields_propagate` |

That's it. No source-side `provenance=` constructions anywhere in `src/`. Phase 7 (provenance schema edit) updates `cells.py` plus this one test. **Low blast radius — the Q8 brainstorm-time prediction held.**

**Subtle but important:** the test at line 60 imports `from lobby_analysis.models_v2.provenance import EvidenceSpan` (statute-semantic shape). Per the Q8 lock + the Tier-0 plan Step 2 / post-framing review F1 resolution: **the new shape uses `retrieval_v2.EvidenceSpan` (Citations-API shape)**. So the Phase 7 edit ALSO updates this test's import to the retrieval-side `EvidenceSpan` and the construction call to match its shape (`citation_type=...`, `document_index=...`, `cited_text=...` instead of `section_reference=...`). The test's intent (verify wrapper fields propagate) is preserved.

**Tier-0 plan coordination:** the Tier-0 plan's Step 2 owns this same edit. If Tier-0 ships first, this plan's Phase 7 becomes a verify-already-done step; if `scoring_v2` ships first, Tier-0's Step 2 becomes verify-already-done. **Coordinate via STATUS.md / parent session.** This plan's Phase 7 instruction: re-run the grep + `git log -p src/lobby_analysis/models_v2/cells.py` to determine which side is acting and skip-or-execute accordingly.

---

## Architectural shape

```
caller (orchestrator OR tier_0_smoke_test.py — out of scope for this plan)
  │
  │  build_scoring_brief(state, vintage, chunks, retrieval_output, statute_bundle, url_pattern="")
  ▼
src/lobby_analysis/scoring_v2/
  ├── brief_writer.py   ← assembles messages.create kwargs (loads prompt md + optional preambles)
  ├── tools.py          ← tool definitions: record_cell, record_unscoreable_cell
  ├── parser.py         ← parses Message → ScoringOutput (cell-class dispatch via registry)
  └── models.py         ← Pydantic: ScoringOutput, UnscoreableCell
  │
  ▼  client.messages.create(**brief)
Anthropic API (claude-opus-4-7 + Citations + tools)
  │
  ▼  Message response (text blocks w/ citations + record_cell / record_unscoreable_cell tool_use blocks)
parse_scoring_response(message, state_abbr, vintage_year, chunk_id) → ScoringOutput(cells, unscoreable_cells)
```

**The brief-writer does NOT call the SDK.** Same pattern as retrieval — returns kwargs dict; caller dispatches. Keeps the brief-writer testable without an API key.

---

## What this plan ships

- `src/lobby_analysis/scoring_v2/` — full module (5 .py files + `docs.md`)
- `src/scoring/scorer_prompt_v2.md` — v2 prompt (full text inlined in Phase 6 below)
- `src/scoring/chunk_frames_v2/.gitkeep` — directory exists; **0 preamble files**
- `src/lobby_analysis/models_v2/cells.py` edit — `provenance` schema change (Phase 7, coordinated with Tier-0)
- 6 test files in `tests/` (named in Phase 1)
- Test fixture `tests/fixtures/scoring_v2/sample_response.json` (hand-crafted, mirror retrieval's pattern)
- Test fixture `tests/fixtures/scoring_v2/tiny_statute.txt` (for T1 integration)
- Public exports via `scoring_v2/__init__.py`
- Module docs at `scoring_v2/docs.md`

## What this plan does NOT ship

- **Practical-axis brief-writer** (Q6 deferred to sibling brainstorm). Brief-writer accepts only chunks with `axis_summary ∈ {"legal", "mixed"}`; mixed chunks score only their `axis == "legal"` cells. Practical-only chunks (`search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website`) → raise `ValueError`.
- **Scholarly v2-rewrite of v1 Rule 6 substantive guidance** (PRI A5-A11 + C0 functional-public-entity content). Per Q4, this lands in chunk preambles when authored — downstream scholarly work, informed by T1+ empirical evidence of where the model under-grounds.
- **The orchestrator / Ralph loop runtime** that dispatches scoring briefs in production. Out of scope per Q9 + handoff. Tier-0 ([`20260518_tier_0_minimal_pipeline.md`](20260518_tier_0_minimal_pipeline.md)) is the first thin caller; the packaged orchestrator is downstream of Tier-1.
- **`output_writer.py`-style CSV persistence.** Parser produces typed cells in memory; persistence is downstream.
- **Per-cell-type tools (15)**. Single polymorphic `record_cell` per Q2. Revisit only on T2+ evidence of value mis-typing.
- **`models_v2.EvidenceSpan` deletion** — Tier-0 Step 2 deprecates the class; deletion requires a separate import-graph audit.

---

## Chunks in scope

Per Q6, `build_scoring_brief` accepts only chunks whose cell roster contains at least one `axis == "legal"` cell. The 15 chunks split:

**Legal-only (6 chunks, all cells scoreable):**

| chunk_id | legal cells |
|---|---:|
| `actor_registration_required` | 11 |
| `registration_thresholds` | 6 |
| `lobbyist_registration_form_contents` | 13 |
| `principal_spending_report` | 23 |
| `lobbying_contact_log` | 9 |
| `other_lobbyist_filings` | 12 |

**Mixed (5 chunks, scoreable BUT filtered to legal half — practical cells silently dropped from the cell roster):**

| chunk_id | total cells | legal cells (scored) | practical cells (out of scope) |
|---|---:|---:|---:|
| `lobbying_definitions` | 15 | varies (legal halves + legal-only rows) | varies (practical halves) |
| `registration_mechanics_and_exemptions` | 8 | 6 + 2 legal halves = ~8 | 2 practical halves |
| `lobbyist_spending_report` | 34 | 33 + 1 legal half | 1 practical half |
| `enforcement_and_audits` | 2 rows / 4 cells | 2 legal halves | 2 practical halves |
| `oversight_and_government_subjects` | 8 | 2 legal (`govt_agencies_*`) | 6 practical (oversight + ministerial) |

The exact legal/practical split per mixed chunk is computed at runtime by filtering `chunk.cell_specs` to `spec.axis == "legal"`. **If filtering leaves 0 legal cells, brief-writer raises `ValueError`** (the caller passed a chunk this brief-writer cannot score — almost certainly user misuse worth catching).

**Out of scope (4 chunks, brief-writer raises `ValueError`):**

`search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website` — all `axis_summary == "practical"`. Sibling brainstorm territory.

---

## File deliverables

```
src/lobby_analysis/scoring_v2/
├── __init__.py                 # Public exports
├── brief_writer.py             # build_scoring_brief(state, vintage, chunks, retrieval_output, statute_bundle, url_pattern="")
├── tools.py                    # RECORD_CELL_TOOL, RECORD_UNSCOREABLE_CELL_TOOL, ALL_TOOLS
├── parser.py                   # parse_scoring_response(message, state_abbr, vintage_year, chunk_id) → ScoringOutput
├── models.py                   # Pydantic: ScoringOutput, UnscoreableCell
└── docs.md                     # Module-level documentation (matches retrieval_v2/docs.md pattern)

src/scoring/
├── scorer_prompt_v2.md         # The v2 prompt (Phase 6 below has the full draft)
└── chunk_frames_v2/
    └── .gitkeep                # Directory exists; 0 preamble files

src/lobby_analysis/models_v2/cells.py    # Edit: provenance: tuple[retrieval_v2.EvidenceSpan, ...] = ()

tests/
├── test_scoring_v2_tools.py
├── test_scoring_v2_models.py
├── test_scoring_v2_brief_writer.py
├── test_scoring_v2_parser.py
├── test_scoring_v2_prompt_invariants.py
└── test_scoring_v2_integration.py        # skipif-gated on ANTHROPIC_API_KEY

tests/fixtures/scoring_v2/
├── tiny_statute.txt                       # Hand-crafted minimal statute for integration test
└── sample_response.json                   # Hand-crafted Message dict mirroring Citations + record_cell shape
```

---

## Empirical validation gates (graduated tiers)

Mirror retrieval's pattern. Both you (implementer) and the plan author are first-time users of Citations + tool use *for scoring* (retrieval cleared T1, but scoring's tool-call density per response will be higher). Each tier gates the next.

| Tier | What runs | Gates |
|---|---|---|
| **T0 unit** | All non-integration tests; no API key needed | Module ships, types validate, schema constraints hold, parser dispatch works on hand-crafted fixture |
| **T1 smoke** | `tests/test_scoring_v2_integration.py` against `tiny_statute.txt` + 1 chunk (`enforcement_and_audits` — 2 rows, smallest meaningful chunk) | Citations API attaches to text; `record_cell` fires for at least 1 cell with non-empty `evidence_spans`; parser handles real response shape. Cost ≈ $0.05/run. |
| **T2 single-chunk OH** | Manual run via `scripts/tier_0_smoke_test.py` (Tier-0 plan owns this) against OH 2015 + `enforcement_and_audits` | Pipeline wires end-to-end; cell values plausible against statute text |
| **T3 multi-chunk** | Tier-1 territory: 6 chunks per CPI 2015 de-jure rubric | Across-chunk consistency; σ_noise estimable |
| **T4 full** | 50-state × 4-vintage Ralph-loop production | Out of scope; downstream of orchestrator |

**This plan implements through T1 only.** T2-T4 are downstream empirical work the user runs once the module + Tier-0 ship.

---

## Phase 0 — Scaffolding

1. Create `src/lobby_analysis/scoring_v2/` directory with empty `__init__.py`.
2. Create empty placeholder files: `brief_writer.py`, `tools.py`, `parser.py`, `models.py`, `docs.md` (placeholder line `# scoring_v2 — module documentation`).
3. Create `tests/fixtures/scoring_v2/` directory with `.gitkeep`.
4. Create `src/scoring/chunk_frames_v2/` directory with `.gitkeep` (0 preamble files this plan).
5. Verify imports: `uv run python -c "import lobby_analysis.scoring_v2"` succeeds (empty `__init__.py` is enough).

**Gate:** `uv run python -c "import lobby_analysis.scoring_v2"` succeeds. `uv run python -c "from lobby_analysis.retrieval_v2 import RetrievalOutput, EvidenceSpan"` succeeds (Phase 0's role is verifying upstream deps are healthy before we add new code on top).

Commit: `scoring_v2: scaffolding (empty module + chunk_frames_v2 dir)`

---

## Phase 1 — Write ALL tests (RED)

**Discipline:** write every test below before any implementation. Run `uv run pytest tests/test_scoring_v2_*.py` and confirm everything fails with `ImportError` / `AttributeError` / `NotImplementedError` (NOT with malformed-assertion errors).

Test inventory below — write the test bodies from the assertions; specific identifiers spelled out so the implementer doesn't have to invent names.

### `tests/test_scoring_v2_tools.py` (8 tests)

```python
# Tools schema + coupling-test surface

def test_record_cell_tool_has_documented_name():
    # RECORD_CELL_TOOL["name"] == "record_cell"

def test_record_unscoreable_cell_tool_has_documented_name():
    # RECORD_UNSCOREABLE_CELL_TOOL["name"] == "record_unscoreable_cell"

def test_record_cell_tool_required_fields():
    # input_schema.required == ["row_id", "axis", "value", "confidence"]
    # Optional: "conditional", "condition_text", "notes"

def test_record_cell_tool_axis_enum():
    # axis.enum == ["legal", "practical"] — the brainstorm scope is legal, but
    # the schema permits "practical" so the parser can warn-not-error on
    # mistaken practical-axis tool calls from a model under a mixed-chunk brief.

def test_record_cell_tool_confidence_enum():
    # confidence.enum == ["high", "medium", "low"]

def test_record_cell_tool_value_is_loose_json():
    # value.oneOf contains exactly: {type: number}, {type: integer}, {type: string},
    # {type: boolean}, {type: array}, {type: object}, {type: "null"}
    # Per plan-write decision #2 — loose JSON; parser validates per cell class.

def test_record_unscoreable_cell_tool_required_fields():
    # input_schema.required == ["cell_id", "reason", "confidence"]
    # Optional: none (evidence_spans attach via Citations, not as a tool input field)

def test_record_cell_tool_row_id_is_string_with_parser_side_validation():
    # row_id.type == "string"; no enum on row_id (plan-write decision #1).
    # Parser validates (row_id, axis) ∈ build_cell_spec_registry().keys().
    # COUPLING TEST: build_cell_spec_registry() returns ≥1 key; verify the
    # parser knows how to look these up. Lives here (not in parser tests) so
    # tools.py / parser.py drift is caught on tools.py CI runs.
    from lobby_analysis.models_v2 import build_cell_spec_registry
    assert len(build_cell_spec_registry()) > 0
```

### `tests/test_scoring_v2_models.py` (7 tests)

```python
# Pydantic models: ScoringOutput, UnscoreableCell — shape + invariants

def test_scoring_output_constructs_with_defaults():
    # ScoringOutput(state_abbr="OH", vintage_year=2015, chunk_id="enforcement_and_audits")
    # → cells == (); unscoreable_cells == ()

def test_scoring_output_is_frozen():
    # Attempting to mutate after construction raises ValidationError

def test_scoring_output_cells_field_is_tuple_not_list():
    # type annotation is tuple[CompendiumCell, ...]; list input coerces to tuple via Pydantic

def test_scoring_output_unscoreable_cells_field_is_tuple():
    # type annotation is tuple[UnscoreableCell, ...]

def test_unscoreable_cell_required_fields():
    # cell_id: str, reason: str, confidence: Literal["high","medium","low"]
    # Constructing without confidence raises ValidationError

def test_unscoreable_cell_evidence_spans_defaults_to_empty_tuple():
    # evidence_spans field defaults to (), accepts tuple of retrieval_v2.EvidenceSpan

def test_unscoreable_cell_is_frozen():
    # frozen=True — assignment raises
```

### `tests/test_scoring_v2_brief_writer.py` (16 tests)

```python
# Brief assembly + validation. Fixture: minimal statute_bundle + RetrievalOutput

def test_brief_writer_returns_messages_create_kwargs():
    # brief = build_scoring_brief(state="OH", vintage=2015, chunks=["enforcement_and_audits"],
    #                             retrieval_output=<fixture>, statute_bundle=<fixture>)
    # brief has keys: "model", "max_tokens", "thinking", "output_config", "system", "messages", "tools"

def test_brief_writer_uses_claude_opus_4_7():
    # brief["model"] == "claude-opus-4-7"

def test_brief_writer_uses_adaptive_thinking():
    # brief["thinking"] == {"type": "adaptive"}

def test_brief_writer_uses_effort_high():
    # brief["output_config"] == {"effort": "high"}

def test_brief_writer_omits_sampling_params():
    # "temperature" not in brief; "top_p" not in brief; "top_k" not in brief

def test_brief_writer_max_tokens_is_16000():
    # brief["max_tokens"] == 16000

def test_brief_writer_attaches_both_tools():
    # brief["tools"] is a list with RECORD_CELL_TOOL and RECORD_UNSCOREABLE_CELL_TOOL

def test_brief_writer_system_block_loads_scorer_prompt_v2():
    # system[0].text contains a distinctive phrase from scorer_prompt_v2.md
    # (e.g., "cite the supporting statute span before each tool call")
    # AND has cache_control == {"type": "ephemeral"}

def test_brief_writer_packages_statute_files_as_documents_with_citations():
    # user message content has one type="document" block per file; each has
    # citations.enabled=True, cache_control={"type":"ephemeral"}, source.type="text"

def test_brief_writer_user_text_includes_state_and_vintage():
    # User-text block (the trailing text block after the document blocks)
    # contains "OH" and "2015"

def test_brief_writer_user_text_includes_cell_roster_for_legal_axis_only():
    # User text mentions row_ids for axis=="legal" cells of the chunk
    # AND does NOT mention any row_id that is practical-only.
    # Use enforcement_and_audits (mixed) — should include both legal halves'
    # row_ids, exclude both practical halves.

def test_brief_writer_user_text_includes_retrieval_annotations():
    # User text has a section summarizing retrieval_output.cross_references
    # filtered to this chunk: section_reference, relevance, key evidence_spans excerpted.

def test_brief_writer_unknown_chunk_raises_value_error():
    # build_scoring_brief(..., chunks=["nonexistent_chunk"]) raises ValueError
    # mentioning the unknown chunk id

def test_brief_writer_practical_only_chunk_raises_value_error():
    # build_scoring_brief(..., chunks=["search_portal_capabilities"]) raises ValueError
    # mentioning "no legal cells" or similar — practical-only chunks are out of scope

def test_brief_writer_loads_preamble_if_present(tmp_path, monkeypatch):
    # If src/scoring/chunk_frames_v2/<chunk_id>.md exists, brief-writer inserts
    # its content into user text before the cell roster. Use monkeypatch to
    # point the preamble path at tmp_path, write a sentinel preamble, verify
    # the sentinel string appears in user text.

def test_brief_writer_skips_silently_if_preamble_absent():
    # Default state (ship 0 preambles): no preamble file → brief assembles without
    # error and user text contains no preamble sentinel.
```

### `tests/test_scoring_v2_parser.py` (9 tests)

Fixture: `tests/fixtures/scoring_v2/sample_response.json` — hand-crafted Message dict matching Citations + record_cell shape. Parser tests pin to this hand-crafted fixture (see retrieval's lesson — do NOT couple integration-written real fixtures to parser unit tests; commit `5f262e9`).

```python
def test_parser_extracts_cells_from_record_cell_tool_calls():
    # Fixture has 2 record_cell tool calls; output.cells has 2 entries

def test_parser_dispatches_to_expected_cell_class_per_row():
    # For each record_cell tool call, parser looks up (row_id, axis) in
    # build_cell_spec_registry() and instantiates spec.expected_cell_class.
    # Fixture has at least one BinaryCell case; verify type(output.cells[0]) is BinaryCell.

def test_parser_pairs_preceding_citations_to_following_tool_call():
    # text_with_citation_A → record_cell_1 → text_with_citation_B → record_cell_2
    # → output.cells[0].provenance == (span_A,); cells[1].provenance == (span_B,)

def test_parser_resets_citation_buffer_after_each_tool_call():
    # text_with_citation_A → text_with_citation_B → record_cell_1 → record_cell_2
    # → cells[0].provenance == (span_A, span_B); cells[1].provenance == ()
    # Load-bearing — same invariant as retrieval's
    # test_parser_resets_citation_buffer_after_each_tool_call

def test_parser_extracts_unscoreable_cells_from_record_unscoreable_cell_tool_calls():
    # Fixture mixes both tools; output.unscoreable_cells populated separately
    # with right cell_id / reason / confidence / evidence_spans

def test_parser_unknown_tool_name_resets_citation_buffer():
    # text_with_citation_A → tool_use(name="garbage") → text_with_citation_B → record_cell_1
    # → cells[0].provenance == (span_B,)  # span_A flushed by unknown tool

def test_parser_unknown_row_id_raises_or_warns(caplog):
    # tool_use record_cell with row_id="nonexistent_row" — parser should NOT
    # silently drop. Either raise ValueError OR log a warning + skip cell.
    # Plan-write hunch: log warning + skip (matches retrieval's "unknown tool
    # name" handling). Verify caplog has the warning.

def test_parser_polymorphic_over_message_object_and_dict():
    # Same fixture loaded both as a dict (json.load) and as an SDK-shape
    # Message-like namespace object; both produce identical ScoringOutput.

def test_parser_empty_response_returns_empty_scoring_output():
    # Message with no tool_use blocks → cells == (), unscoreable_cells == ()
```

### `tests/test_scoring_v2_prompt_invariants.py` (8 tests)

These run against `src/scoring/scorer_prompt_v2.md`. Invariant tests catch v1 leak.

```python
import re
from pathlib import Path

V2_PROMPT_PATH = Path("src/scoring/scorer_prompt_v2.md")
PROMPT = V2_PROMPT_PATH.read_text()

def test_prompt_exists_and_nonempty():
    # PROMPT.strip() not empty; len(PROMPT) > 1500

def test_prompt_no_pri_rubric_letter_refs():
    # No A1-A11, C0-C3 as standalone tokens (word-boundary)
    matches = re.findall(r"\b[AC]\d{1,2}\b", PROMPT)
    assert not matches, f"PRI rubric letter leaks: {matches}"

def test_prompt_no_rubric_word():
    # "rubric" should not appear as a standalone word (case-insensitive)
    assert not re.search(r"\brubric\b", PROMPT, re.IGNORECASE)

def test_prompt_no_files_read_json_reference():
    # v1 Rule 7 mechanism — should be dropped
    assert "files_read.json" not in PROMPT
    assert "files_read" not in PROMPT

def test_prompt_no_unable_to_evaluate_token():
    # v1 Rule 2 mechanism — replaced by record_unscoreable_cell tool
    assert "unable_to_evaluate" not in PROMPT

def test_prompt_mentions_record_cell_tool():
    # Prompt must instruct the agent to call this tool
    assert "record_cell" in PROMPT

def test_prompt_mentions_record_unscoreable_cell_tool():
    # Prompt must instruct the agent to call this tool
    assert "record_unscoreable_cell" in PROMPT

def test_prompt_instructs_citation_before_each_tool_call():
    # Rule 5 must be present — something like "cite ... before ... tool call"
    # Loose match; this is what makes the parser's pairing rule non-vacuous.
    assert re.search(r"cite.{0,80}before.{0,40}tool call", PROMPT, re.IGNORECASE)
```

### `tests/test_scoring_v2_integration.py` (3 tests)

```python
import os
import pytest
import anthropic

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Integration test requires ANTHROPIC_API_KEY"
)

# Fixture: tests/fixtures/scoring_v2/tiny_statute.txt
# Contents (3 sentences, 1 audit-required clause, 1 penalty clause):
#   "Section 1. The commission shall audit each lobbyist's report annually.
#    Section 2. Failure to file is punished by a fine not to exceed $1000.
#    Section 3. The commission may waive audit for filers under §99.005."
# Chunk: enforcement_and_audits (2 rows, both combined-axis; 2 legal cells
# scored; smallest meaningful chunk for cost discipline)

def test_real_api_call_returns_citations():
    # build a brief against tiny_statute + enforcement_and_audits;
    # client.messages.create(**brief); assert ≥1 content block has non-empty citations.
    # OVERRIDE max_tokens=2000 for cost discipline.

def test_real_api_call_produces_at_least_one_record_cell():
    # Same setup; assert response has ≥1 tool_use block with name="record_cell"

def test_parser_handles_real_scoring_response():
    # Same call; pass through parse_scoring_response(); output.cells has ≥1
    # entry with non-empty provenance. Save the response to
    # tests/fixtures/scoring_v2/sample_response_real.json (gitignored — same
    # split-fixture pattern as retrieval's, per commit 5f262e9).
```

**Gate for Phase 1:** all 51 tests fail with import/attribute errors. Commit: `scoring_v2: failing tests written (RED, all phases)`

---

## Phase 2 — Tool definitions (GREEN for tool tests)

Implement `src/lobby_analysis/scoring_v2/tools.py`:

```python
"""Tool definitions for the v2 scoring agent.

Two tools — direct parallel to retrieval's surface:

- ``record_cell`` — agent calls once per scored compendium cell. Single
  polymorphic tool (Q2 lock); ``value`` is loose JSON; parser does cell-class
  dispatch via ``build_cell_spec_registry()``.
- ``record_unscoreable_cell`` — agent calls when a cell cannot be scored
  from the statute bundle (parallel to retrieval's ``record_unresolvable_reference``).

Citations (Anthropic Citations API) attach to text blocks preceding each
tool call as machine-verified provenance — see Rule 5 in
``src/scoring/scorer_prompt_v2.md``.

Note on the ``row_id`` field: it is a string (not an enum sourced from
``build_cell_spec_registry()``). Parser validates ``(row_id, axis)`` is in
the registry on dispatch; enum-on-the-wire was rejected at plan-write time
because 186 entries would inflate every tool dump without adding coverage.
"""

RECORD_CELL_TOOL: dict = {
    "name": "record_cell",
    "description": (
        "Record a scored compendium cell from the statute documents. Call this "
        "tool once per cell in the brief's roster. Cite the statute span(s) "
        "supporting the score in the preceding text — those citations will be "
        "attached to this tool call as machine-verified provenance."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "row_id": {
                "type": "string",
                "description": (
                    "The compendium row id (e.g., 'lobbying_violation_penalties_imposed_in_practice'). "
                    "Must be one of the row_ids listed in the brief's cell roster."
                ),
            },
            "axis": {
                "type": "string",
                "enum": ["legal", "practical"],
                "description": (
                    "Axis label. This brief-writer scopes to legal-axis cells; emit "
                    "'practical' only if the brief's roster explicitly includes the "
                    "(row_id, 'practical') cell — currently the brief excludes those, "
                    "so emit 'legal'."
                ),
            },
            "value": {
                "oneOf": [
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "string"},
                    {"type": "boolean"},
                    {"type": "array"},
                    {"type": "object"},
                    {"type": "null"},
                ],
                "description": (
                    "Cell value. Shape per the cell's expected class (e.g., bool for "
                    "BinaryCell, decimal for DecimalCell, set-of-strings for EnumSetCell). "
                    "Parser validates value shape against the expected_cell_class for "
                    "(row_id, axis)."
                ),
            },
            "conditional": {
                "type": "boolean",
                "description": (
                    "True if the value applies only under a condition (e.g., 'audit "
                    "required only when expenditures exceed threshold'). Default false."
                ),
            },
            "condition_text": {
                "type": "string",
                "description": (
                    "Verbatim or close-paraphrase statement of the condition under which "
                    "the value applies. Required if conditional=true."
                ),
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": (
                    "high = explicit statute support, no ambiguity; "
                    "medium = present but requires light interpretation; "
                    "low = indirect/partial — consider record_unscoreable_cell instead."
                ),
            },
            "notes": {
                "type": "string",
                "description": (
                    "Optional ≤80-word note for audit trail (threshold values, "
                    "statute-language ambiguities partially supporting the score, etc.)."
                ),
            },
        },
        "required": ["row_id", "axis", "value", "confidence"],
    },
}


RECORD_UNSCOREABLE_CELL_TOOL: dict = {
    "name": "record_unscoreable_cell",
    "description": (
        "Record a cell from the brief's roster that cannot be scored from the "
        "statute bundle (e.g., the statute is silent on this cell, or what is "
        "written is too ambiguous to score with even low confidence). Direct "
        "parallel to retrieval's record_unresolvable_reference."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "cell_id": {
                "type": "string",
                "description": (
                    "Cell identifier in the form '<row_id>:<axis>' (e.g., "
                    "'lobbying_violation_penalties_imposed_in_practice:legal')."
                ),
            },
            "reason": {
                "type": "string",
                "description": (
                    "Why this cell cannot be scored (e.g., 'statute is silent on audit "
                    "requirement', 'language is too ambiguous to score binary')."
                ),
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": (
                    "Confidence in the unscoreable verdict itself (high = sure the "
                    "statute is silent; low = unsure whether more careful reading "
                    "would yield a score)."
                ),
            },
        },
        "required": ["cell_id", "reason", "confidence"],
    },
}


ALL_TOOLS: list[dict] = [RECORD_CELL_TOOL, RECORD_UNSCOREABLE_CELL_TOOL]
```

**Gate:** `uv run pytest tests/test_scoring_v2_tools.py` all green.

Commit: `scoring_v2: tool definitions (record_cell + record_unscoreable_cell)`

---

## Phase 3 — Pydantic models (GREEN for model tests)

Implement `src/lobby_analysis/scoring_v2/models.py`:

```python
"""Typed output models for the v2 scoring agent.

Two new models — direct parallel to retrieval's pattern:

- :class:`UnscoreableCell` — a cell the agent declined to score (parallel to
  retrieval's :class:`UnresolvableReference`).
- :class:`ScoringOutput` — the parsed result of a single scoring call,
  scoped to ``(state_abbr, vintage_year, chunk_id)`` (parallel to
  :class:`RetrievalOutput`).

The scored cells themselves are :class:`CompendiumCell` subclass instances
from ``lobby_analysis.models_v2`` — the parser dispatches by ``(row_id, axis)``
via ``build_cell_spec_registry()``. Their ``provenance`` field carries a
``tuple[EvidenceSpan, ...]`` of Citations-API spans (where ``EvidenceSpan``
is from ``lobby_analysis.retrieval_v2``, NOT ``lobby_analysis.models_v2``;
see Phase 7 schema edit + Tier-0 plan Step 2).
"""

from typing import Literal

from pydantic import BaseModel

from lobby_analysis.models_v2 import CompendiumCell
from lobby_analysis.retrieval_v2 import EvidenceSpan


class UnscoreableCell(BaseModel):
    """A cell the agent declined to score, with reason + provenance."""

    model_config = {"frozen": True}

    cell_id: str
    reason: str
    confidence: Literal["high", "medium", "low"]
    evidence_spans: tuple[EvidenceSpan, ...] = ()


class ScoringOutput(BaseModel):
    """Parsed output of a single scoring call, scoped to one chunk."""

    model_config = {"frozen": True}

    state_abbr: str
    vintage_year: int
    chunk_id: str
    cells: tuple[CompendiumCell, ...] = ()
    unscoreable_cells: tuple[UnscoreableCell, ...] = ()
```

**Gate:** `uv run pytest tests/test_scoring_v2_models.py` all green.

Commit: `scoring_v2: Pydantic output models (ScoringOutput + UnscoreableCell)`

---

## Phase 6 (executed early) — v2 prompt markdown (GREEN for prompt-invariant tests)

**Phase ordering reminder:** brief_writer.py reads this file at call time. The prompt md MUST land before the brief-writer phase. See "Phase ordering note" above.

Write `src/scoring/scorer_prompt_v2.md`. **Full draft inlined below — implementer reviews, may polish wording (preserve the rule structure + tool-call mandates), and commits.**

```markdown
# Lobbying Statute Scorer — Prompt v2

You are a compendium cell scorer for US state lobbying statutes. Your job is to read the state's lobbying statute documents and score the cells in a compendium **chunk** — the small, topic-coherent slice the brief gives you.

You will be given:

1. A **state abbreviation** and **vintage year** (e.g., `OH`, `2015`).
2. A **statute bundle** — the state's lobbying chapter files (and any cross-referenced chapters the retrieval agent identified) attached as `document` content blocks with citations enabled. Cite spans of these documents in your text when supporting a score.
3. A **cell roster** — the compendium cells in scope for this call, listed as `row_id (axis) [ExpectedCellClass]`. The `ExpectedCellClass` tells you the value shape (e.g., `BinaryCell` → bool; `DecimalCell` → number or null; `EnumSetCell` → array of strings).
4. **Retrieval annotations** — the cross-references the retrieval agent identified for this chunk, with their `relevance` and key evidence spans excerpted. Treat these as context (where to look first), not as constraints (your reading governs the score).

Your job is to score each cell in the roster and **record each one via the `record_cell` tool**, with the supporting statute span(s) cited in the preceding text. For cells you cannot score (statute is silent, language too ambiguous to score even with low confidence), call `record_unscoreable_cell` instead — do not guess.

## Rules

### 1. Read the full statute before scoring any cell.

Lobbying statutes are structured as layers: a general rule → exemptions → exceptions to the exemptions → separate disclosure requirements that apply to non-exempt entities. **If you stop reading at the exemption layer, you will systematically under-score.** In particular:

- An exemption for *some* entities does not mean *all* entities of that type are exempt. Check who is NOT covered by the exemption.
- Registration triggers based on expenditure thresholds or compensation apply regardless of entity type unless the entity is explicitly exempted. If anyone who spends $X lobbying must register, that includes government employees unless a specific exemption removes them.
- Do not treat "the definition of person doesn't list government entities" as equivalent to "government entities are exempt." The registration trigger may be activity-based (anyone who spends/receives above a threshold), not entity-based.

### 2. Score each cell to its `ExpectedCellClass` shape.

The cell roster lists each cell as `row_id (axis) [ExpectedCellClass]`. Make the `record_cell` `value` field match the cell class:

- `BinaryCell` → `true` or `false`.
- `IntCell` / `BoundedIntCell` / `GradedIntCell` → integer (or `null` if optional and the statute is silent on the count).
- `DecimalCell` → number (or `null`). Currency precision matters — pass the exact threshold figure.
- `FloatCell` → number (or `null`).
- `EnumCell` → string.
- `EnumSetCell` → array of strings.
- `FreeTextCell` → string (≤500 chars).
- Specialized cells (`TimeThresholdCell`, `TimeSpentCell`, `CountWithFTECell`, `UpdateCadenceCell`, `SectorClassificationCell`, `EnumSetWithAmountsCell`) → object matching the field shape (e.g., `{"magnitude": 20, "unit": "percent_of_work_time"}` for `TimeThresholdCell`).

The parser validates your `value` against the cell class; a mismatch surfaces as a validation error at parse time.

### 3. Cite the supporting span before each tool call.

For every `record_cell` or `record_unscoreable_cell` call, **first emit a brief text passage citing the relevant statute span** — quote the language as it appears, attributed to the source document. The Citations API will attach that span as machine-verified provenance to your tool call. This is **load-bearing**: without preceding citations, downstream consumers have no proof of where the score was grounded.

Example flow:

> Looking at §99.005, I see "The commission shall audit each lobbyist's report annually." This is an unconditional audit requirement in law.
>
> [call `record_cell` with row_id="lobbying_disclosure_audit_required_in_law", axis="legal", value=true, confidence="high"]

The citation block will be automatically attached to your quote.

### 4. Use `record_unscoreable_cell` when the statute is silent or too ambiguous.

If you have read the bundle and the statute does not address the cell (or the language is so ambiguous that even a low-confidence score would be a guess), call `record_unscoreable_cell` with `cell_id="<row_id>:<axis>"`, a `reason` (why you cannot score), and your `confidence` in the unscoreable verdict itself (high = certain the statute is silent; low = uncertain whether more careful reading would surface a score).

**A low-confidence guess masquerading as a score is worse than an honest unscoreable.** Do not guess.

### 5. Confidence is a self-assessment.

For `record_cell.confidence`:

- `high` — evidence is explicit, cited span is authoritative, no ambiguity.
- `medium` — evidence is present but requires light interpretation.
- `low` — evidence is indirect or partial; you inferred from adjacent material. **Consider whether `record_unscoreable_cell` is more honest than a low-confidence score.**

### 6. Handle conditionality.

If a cell's value applies only under a condition (e.g., "audits required only when expenditures exceed $5000"), set `record_cell.conditional=true` and supply `condition_text` (verbatim or close paraphrase). Cells with conditional values are valid; the downstream consumer surfaces the condition alongside the value.

### 7. Respond only via tool calls.

Your response must consist of:

- Text blocks containing brief Citations-grounded reasoning (one per cell — the quote the Citations API attaches to the following tool call).
- `record_cell` / `record_unscoreable_cell` tool calls.

No summaries, no preambles, no prose outside the per-cell reasoning quotes. When you have called `record_cell` or `record_unscoreable_cell` for every cell in the roster, stop.
```

**Gate:** `uv run pytest tests/test_scoring_v2_prompt_invariants.py` all green.

Commit: `scoring_v2: v2 prompt markdown (Phase 6 of plan — executed early before brief_writer)`

---

## Phase 4 — Brief-writer (GREEN for brief-writer tests)

Implement `src/lobby_analysis/scoring_v2/brief_writer.py`. Key responsibilities:

1. Load the v2 prompt (`src/scoring/scorer_prompt_v2.md`).
2. Validate `chunks` — every requested chunk must exist; raise if any practical-only chunk is requested.
3. For each chunk, filter `cell_specs` to `axis == "legal"`; raise if filtering leaves 0 legal cells.
4. Optionally load per-chunk preambles from `src/scoring/chunk_frames_v2/<chunk_id>.md` if present; skip silently if not.
5. Compute the cell roster (chunk-organized) for the user message.
6. Compute the retrieval-annotations section: for each `cross_reference` in `retrieval_output.cross_references` whose `chunk_ids_affected` intersects the requested chunks, render `section_reference`, `relevance`, and excerpts of key `evidence_spans` as user text.
7. Package statute files as `type: "document"` blocks with `citations.enabled=True` + `cache_control: ephemeral`.
8. Return the kwargs dict for `messages.create()`.

```python
"""Build a scoring brief — the ``messages.create()`` kwargs dict for one scoring call.

Mirror of ``retrieval_v2.brief_writer``: returns the kwargs dict; does **not**
call the SDK. The caller (orchestrator, Tier-0 script, or integration test)
hands the result to ``client.messages.create(**brief)``.

Scope: legal-axis cells only (Q6 lock). Practical-only chunks raise; mixed
chunks score only their ``axis == "legal"`` cells.
"""

from pathlib import Path

from lobby_analysis.chunks_v2 import build_chunks
from lobby_analysis.retrieval_v2 import RetrievalOutput
from lobby_analysis.scoring_v2.tools import ALL_TOOLS

_PROMPT_PATH = (
    Path(__file__).parent.parent.parent.parent / "src" / "scoring" / "scorer_prompt_v2.md"
)
_PREAMBLE_DIR = (
    Path(__file__).parent.parent.parent.parent / "src" / "scoring" / "chunk_frames_v2"
)

_MODEL = "claude-opus-4-7"
_MAX_TOKENS = 16000


def build_scoring_brief(
    state: str,
    vintage: int,
    chunks: list[str],
    retrieval_output: RetrievalOutput,
    statute_bundle: list[dict],
    url_pattern: str = "",
) -> dict:
    """Assemble ``messages.create()`` kwargs for a scoring call.

    Args:
        state: Two-letter state abbreviation.
        vintage: Vintage year.
        chunks: Chunk ids in scope. Each must exist in build_chunks(); each
            must have at least one ``axis == "legal"`` cell after filtering
            (practical-only chunks raise ValueError).
        retrieval_output: The RetrievalOutput from the retrieval agent for
            this (state, vintage). Cross-references whose chunk_ids_affected
            intersects ``chunks`` are summarized in the user text.
        statute_bundle: List of statute file dicts (``{path, content, title?}``).
            Packaged as type=document blocks with citations enabled.
        url_pattern: Example Justia URL — included in retrieval annotations
            so the scorer can resolve cited section references if needed.

    Returns:
        Dict suitable for ``client.messages.create(**brief)``.

    Raises:
        ValueError: If any chunk id is unknown, or any chunk has 0 legal cells.
    """
    all_chunks_by_id = {c.chunk_id: c for c in build_chunks()}
    unknown = set(chunks) - set(all_chunks_by_id)
    if unknown:
        raise ValueError(f"Unknown chunks: {sorted(unknown)}")

    legal_chunks_with_filtered_specs = []
    for cid in chunks:
        chunk = all_chunks_by_id[cid]
        legal_specs = tuple(s for s in chunk.cell_specs if s.axis == "legal")
        if not legal_specs:
            raise ValueError(
                f"Chunk {cid!r} has 0 legal-axis cells; scoring_v2 is legal-axis-only. "
                f"Practical-only chunks belong to the practical-axis sibling brief-writer."
            )
        legal_chunks_with_filtered_specs.append((chunk, legal_specs))

    prompt_template = _PROMPT_PATH.read_text()

    document_blocks = [
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": doc["content"],
            },
            "title": doc.get("title") or doc["path"],
            "citations": {"enabled": True},
            "cache_control": {"type": "ephemeral"},
        }
        for doc in statute_bundle
    ]

    user_text = _build_user_text(
        state, vintage, legal_chunks_with_filtered_specs, retrieval_output, url_pattern
    )

    return {
        "model": _MODEL,
        "max_tokens": _MAX_TOKENS,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "high"},
        "system": [
            {
                "type": "text",
                "text": prompt_template,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    *document_blocks,
                    {"type": "text", "text": user_text},
                ],
            }
        ],
        "tools": ALL_TOOLS,
    }


def _build_user_text(state, vintage, chunks_with_legal_specs, retrieval_output, url_pattern):
    parts: list[str] = [
        f"State: {state}",
        f"Vintage: {vintage}",
    ]
    if url_pattern:
        parts.append(f"Example URL pattern: {url_pattern}")
    parts.append("")  # blank line

    requested_chunk_ids = {c.chunk_id for c, _ in chunks_with_legal_specs}
    for chunk, legal_specs in chunks_with_legal_specs:
        preamble = _load_preamble_if_present(chunk.chunk_id)
        if preamble:
            parts.append(preamble)
            parts.append("")

        parts.append(f"### Chunk: {chunk.chunk_id} ({len(legal_specs)} legal cells)")
        parts.append(f"Topic: {chunk.topic}")
        for spec in legal_specs:
            cell_class = spec.expected_cell_class.__name__
            parts.append(f"- {spec.row_id} ({spec.axis}) [{cell_class}]")
        parts.append("")

    parts.append("## Retrieval annotations")
    annotations = _format_retrieval_annotations(retrieval_output, requested_chunk_ids)
    parts.append(annotations or "(no cross-references for the requested chunks)")
    parts.append("")

    parts.append(
        "Score each cell in the roster above by calling `record_cell`. For cells "
        "the statute does not address, call `record_unscoreable_cell` instead. "
        "Cite the supporting statute span in text before each tool call so the "
        "Citations API can attach it as provenance."
    )
    return "\n".join(parts)


def _format_retrieval_annotations(retrieval_output, requested_chunk_ids):
    lines: list[str] = []
    for xref in retrieval_output.cross_references:
        if not (set(xref.chunk_ids_affected) & requested_chunk_ids):
            continue
        lines.append(f"- **{xref.section_reference}** ({xref.justia_url})")
        lines.append(f"  relevance: {xref.relevance}")
        lines.append(f"  chunks_affected: {list(xref.chunk_ids_affected)}")
        if xref.evidence_spans:
            for span in xref.evidence_spans[:2]:  # cap excerpts at 2 for prompt size
                excerpt = (span.cited_text or "")[:200]
                lines.append(f"  cited: {excerpt!r}")
    return "\n".join(lines)


def _load_preamble_if_present(chunk_id: str) -> str | None:
    path = _PREAMBLE_DIR / f"{chunk_id}.md"
    if path.exists():
        return path.read_text()
    return None
```

**Gate:** `uv run pytest tests/test_scoring_v2_brief_writer.py` all green.

Commit: `scoring_v2: brief_writer.py with documents + citations + caching + preamble + retrieval annotations`

---

## Phase 5 — Parser + hand-crafted fixture (GREEN for parser tests)

Hand-craft the fixture `tests/fixtures/scoring_v2/sample_response.json` first. Shape mirrors retrieval's `sample_response_handcrafted.json` (read [`tests/fixtures/retrieval_v2/sample_response_handcrafted.json`](../../../../tests/fixtures/retrieval_v2/sample_response_handcrafted.json) as the template).

Fixture must cover:

- 2 `record_cell` tool calls (one `BinaryCell` shape, one different shape — e.g., `IntCell` with a null value)
- 1 `record_unscoreable_cell` tool call
- text blocks with `citations` arrays preceding each tool call
- one citation-only-no-tool case (verifies citations not stranded)
- one tool-call-with-no-preceding-citation case (verifies empty `evidence_spans` allowed)
- one mixed case where multiple citations accumulate before a single tool call

### Parser implementation: `src/lobby_analysis/scoring_v2/parser.py`

```python
"""Parse a ``messages.create()`` response into typed :class:`ScoringOutput`.

Pairing rule (identical to retrieval's): citations on text blocks accumulate
in a buffer until a ``tool_use`` block; the buffer flushes onto that tool
call's parsed output and resets. Unknown tool names still flush + reset
(prevents stale citations bleeding into the next valid call). Other block
types (``thinking``, ``server_tool_use``) pass through.

Polymorphic over Anthropic SDK Message objects (attr access) and JSON dicts
(key access) — same path works against the hand-crafted fixture AND real
API responses.

Cell-class dispatch: each ``record_cell`` tool call's ``(row_id, axis)`` is
looked up in ``build_cell_spec_registry()`` to find the expected
``CompendiumCell`` subclass. Pydantic instantiation enforces value shape.
Unknown ``(row_id, axis)`` pairs log a warning and are skipped (mirrors
retrieval's unknown-tool-name handling).
"""

import logging
from typing import Any

from lobby_analysis.models_v2 import CompendiumCell, build_cell_spec_registry
from lobby_analysis.retrieval_v2 import EvidenceSpan
from lobby_analysis.retrieval_v2.parser import _get, _get_content, _parse_citation, _input
from lobby_analysis.scoring_v2.models import ScoringOutput, UnscoreableCell

_logger = logging.getLogger(__name__)


def parse_scoring_response(
    message: Any,
    state_abbr: str,
    vintage_year: int,
    chunk_id: str,
) -> ScoringOutput:
    """Parse a Citations + tool_use response into a ScoringOutput.

    Args:
        message: An anthropic.types.Message instance or an equivalent dict.
        state_abbr: Two-letter state abbreviation (echoed into output).
        vintage_year: Vintage year (echoed into output).
        chunk_id: The chunk this call was scoped to (echoed into output).

    Returns:
        ScoringOutput with cells + unscoreable_cells populated.
    """
    content = _get_content(message)
    registry = build_cell_spec_registry()

    cells: list[CompendiumCell] = []
    unscoreable: list[UnscoreableCell] = []
    citation_buffer: list[EvidenceSpan] = []

    for block in content:
        block_type = _get(block, "type")

        if block_type == "text":
            for raw_cite in _get(block, "citations", default=[]) or []:
                citation_buffer.append(_parse_citation(raw_cite))

        elif block_type == "tool_use":
            tool_name = _get(block, "name")
            tool_input = _get(block, "input") or {}
            spans = tuple(citation_buffer)
            citation_buffer = []

            if tool_name == "record_cell":
                cell = _build_cell_from_tool_input(tool_input, spans, registry)
                if cell is not None:
                    cells.append(cell)
            elif tool_name == "record_unscoreable_cell":
                unscoreable.append(
                    UnscoreableCell(
                        cell_id=_input(tool_input, "cell_id"),
                        reason=_input(tool_input, "reason"),
                        confidence=_input(tool_input, "confidence"),
                        evidence_spans=spans,
                    )
                )
            # Unknown tool names: buffer already reset above; skip silently.

    return ScoringOutput(
        state_abbr=state_abbr,
        vintage_year=vintage_year,
        chunk_id=chunk_id,
        cells=tuple(cells),
        unscoreable_cells=tuple(unscoreable),
    )


def _build_cell_from_tool_input(tool_input, evidence_spans, registry):
    row_id = _input(tool_input, "row_id")
    axis = _input(tool_input, "axis")
    key = (row_id, axis)
    spec = registry.get(key)
    if spec is None:
        _logger.warning(
            "scoring_v2.parser: unknown (row_id, axis)=%r in record_cell tool call; skipping",
            key,
        )
        return None
    cell_class = spec.expected_cell_class
    kwargs = {
        "cell_id": key,
        "value": _input(tool_input, "value"),
        "conditional": _input(tool_input, "conditional", default=False),
        "condition_text": _input(tool_input, "condition_text"),
        "confidence": _input(tool_input, "confidence"),
        "provenance": evidence_spans,
    }
    # Specialized cells (TimeThresholdCell, CountWithFTECell, etc.) split the
    # "value" tool field into multiple Python fields. Adapt here. Common case
    # (value: single field) is the default; specialized classes override.
    return _instantiate_with_special_shapes(cell_class, kwargs)


def _instantiate_with_special_shapes(cell_class, kwargs):
    """Adapt kwargs to special cell-class shapes (TimeThresholdCell, etc.).

    For most subclasses, ``value`` maps 1:1 to the cell's ``value`` field. For
    specialized classes whose tool ``value`` is a dict mapping to multiple
    Python fields (e.g., TimeThresholdCell has ``magnitude`` + ``unit``), the
    dict is unpacked and ``value`` is dropped from kwargs.
    """
    # Cell classes whose tool-input ``value`` is a dict of field kwargs.
    from lobby_analysis.models_v2 import (
        CountWithFTECell,
        EnumSetWithAmountsCell,
        TimeSpentCell,
        TimeThresholdCell,
    )

    multi_field_classes = (
        TimeThresholdCell, TimeSpentCell, CountWithFTECell, EnumSetWithAmountsCell,
    )
    if cell_class in multi_field_classes and isinstance(kwargs.get("value"), dict):
        nested = kwargs.pop("value")
        kwargs.update(nested)
    return cell_class(**kwargs)
```

**Note on reusing retrieval's helpers:** the parser imports `_get`, `_get_content`, `_parse_citation`, `_input` from `retrieval_v2.parser`. These are private (`_`-prefixed) but they're stable and load-bearing. Reusing them avoids drift; if duplication later proves cleaner, refactor to a shared `_message_walker.py`. **This plan does NOT do that refactor preemptively** — YAGNI; revisit when a third consumer appears.

**Gate:** `uv run pytest tests/test_scoring_v2_parser.py` all green.

Commit: `scoring_v2: parser + hand-crafted sample_response fixture (Phase 5 of plan)`

---

## Phase 7 — `CompendiumCell.provenance` schema edit + audit-driven test updates

**Coordinate with Tier-0 plan Step 2.** Both this plan's Phase 7 and the Tier-0 plan's Step 2 own the same edit to `src/lobby_analysis/models_v2/cells.py`. At Phase-7 execution time:

1. `git -C /Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm log -p src/lobby_analysis/models_v2/cells.py` to see if Tier-0 has already shipped the edit.
2. If the edit is already in: skip steps 3-5 below, jump to Phase 8.
3. If not: run `grep -rn "provenance=" tests/ src/` to confirm the audit list (plan-write-time result: 1 file, 1 line — `tests/test_models_v2_cells.py:69`). If the count differs, **stop and surface to user** (someone added new `provenance=` usages between plan-write and execution; coordinate before touching).
4. Edit `src/lobby_analysis/models_v2/cells.py` — change line 40:
   ```python
   # BEFORE
   provenance: EvidenceSpan | None = None
   # AFTER
   from lobby_analysis.retrieval_v2 import EvidenceSpan as _RetrievalEvidenceSpan
   provenance: tuple[_RetrievalEvidenceSpan, ...] = ()
   ```
   (Import at top of file; aliased to avoid name-shadow with the now-deprecated `models_v2.provenance.EvidenceSpan` which is still imported at line 23. Per Tier-0 Step 2, add deprecation notice to `models_v2/provenance.py` docstring; deletion deferred.)
5. Update `tests/test_models_v2_cells.py:60-69` — change import to `from lobby_analysis.retrieval_v2 import EvidenceSpan`, update the construction call:
   ```python
   span = EvidenceSpan(
       citation_type="char_location",
       document_index=0,
       cited_text="as required by §101.70(B)(1)",
       document_title="OH §101.70",
       start_char_index=0,
       end_char_index=24,
   )
   cell = BinaryCell(..., provenance=(span,))  # tuple, not single span
   ```
6. Run the full test suite: `uv run pytest`. Expected: all previously-green tests stay green; the test_scoring_v2_models.py UnscoreableCell test that uses `evidence_spans: tuple[EvidenceSpan, ...]` continues to import correctly.

Commit: `scoring_v2 / models_v2: lock CompendiumCell.provenance to retrieval_v2.EvidenceSpan tuple`

(If Tier-0 already shipped this edit, no commit; jump to Phase 8.)

---

## Phase 8 — Integration smoke test (T1 gate)

This is the **first time we exercise real Citations + tool use behavior for the scoring use case**. Higher tool-call density per response than retrieval; the same parser pairing rule applies but at greater load.

### Cost discipline — smallest functional call

The integration test runs automatically on every `uv run pytest` when `ANTHROPIC_API_KEY` is set (via `pytest.mark.skipif`). To keep it cost-trivial:

- **Fixture is 3 short sentences** — minimum to test both `record_cell` AND verify citations attach.
- **`max_tokens=2000`** in the integration brief (override the production default of 16000).
- **Single chunk in scope**: `chunks=["enforcement_and_audits"]` — only 2 legal cells in the roster; smallest meaningful chunk.
- **Empty `retrieval_output`** (no `cross_references`) is fine — retrieval annotations are optional context; absence is well-defined.
- **Pricing estimate** (Opus 4.7 @ $5/M input + $25/M output): ~3K input + ~1K output ≈ **$0.04 per test run**. Matches the brainstorm's ≈$0.05 hunch.

### Fixture: `tests/fixtures/scoring_v2/tiny_statute.txt`

```
Section 1. The commission shall audit each lobbyist's report annually.
Section 2. Failure to file is punished by a fine not to exceed $1000.
Section 3. The commission may waive audit for filers under §99.005.
```

Two scoreable cells in `enforcement_and_audits`:
- `lobbying_violation_penalties_imposed_in_practice` (legal half) — should score true (penalty exists in law).
- `lobbying_disclosure_audit_required_in_law` (legal half) — should score true with possible `conditional=true` for the §99.005 waiver.

### Steps

1. Confirm `ANTHROPIC_API_KEY` is set.
2. Create `tests/fixtures/scoring_v2/tiny_statute.txt`.
3. Add `tests/fixtures/scoring_v2/sample_response_real.json` to `.gitignore` (mirror retrieval's split-fixture pattern from commit `5f262e9`).
4. Run `uv run pytest tests/test_scoring_v2_integration.py -v`.
5. **If tests fail because the real response shape diverges from hand-crafted fixture:** STOP. Surface to user. Do not silently patch the parser to accommodate — the user wants to know about docs↔reality mismatches before they get papered over. (Retrieval's parser pairing rule is the canary here; if it broke at this load, we need to know.)
6. **If tests pass:** save the real response as `tests/fixtures/scoring_v2/sample_response_real.json` (gitignored; for inspection only — does NOT replace `sample_response.json` which parser unit tests consume).

### What to verify by hand

- `response.content` contains text blocks (with `citations`) and `tool_use` blocks for both `record_cell` calls.
- At least one citation `start_char_index` / `end_char_index` points at the audit clause; another at the penalty clause.
- `response.usage.cache_creation_input_tokens` non-zero on first call; `cache_read_input_tokens` non-zero on a second identical call.
- Parsed `ScoringOutput.cells` has 2 entries, each `BinaryCell` with `value=True` and non-empty `provenance`.

Commit: `scoring_v2: integration test green; sample_response_real.json captured (gitignored)`

---

## Phase 9 — Public exports + module docs + ruff (suite-wide green)

1. `uv run pytest` — full suite passes. The pre-existing `test_pipeline.py` failures (portal-snapshot fixture data missing on main) are expected; everything else green.
2. `uv run ruff check src/lobby_analysis/scoring_v2/ tests/test_scoring_v2_*.py`
3. `uv run ruff format src/lobby_analysis/scoring_v2/ tests/test_scoring_v2_*.py`
4. Update `src/lobby_analysis/scoring_v2/__init__.py`:

```python
"""v2 scoring agent — Anthropic Citations API + tool use over the v2 compendium.

Builds a ``messages.create()`` brief for one chunk's worth of legal-axis cells;
parses the response back into a typed ``ScoringOutput`` (cells + unscoreable_cells).
Does NOT call the SDK itself — the caller (orchestrator or Tier-0 script)
dispatches the brief and feeds the response into the parser.

Practical-axis cells are out of scope (Q6 lock); the sibling brief-writer
will own those.
"""

from lobby_analysis.scoring_v2.brief_writer import build_scoring_brief
from lobby_analysis.scoring_v2.models import ScoringOutput, UnscoreableCell
from lobby_analysis.scoring_v2.parser import parse_scoring_response
from lobby_analysis.scoring_v2.tools import (
    ALL_TOOLS,
    RECORD_CELL_TOOL,
    RECORD_UNSCOREABLE_CELL_TOOL,
)

__all__ = [
    "ALL_TOOLS",
    "RECORD_CELL_TOOL",
    "RECORD_UNSCOREABLE_CELL_TOOL",
    "ScoringOutput",
    "UnscoreableCell",
    "build_scoring_brief",
    "parse_scoring_response",
]
```

5. Write `src/lobby_analysis/scoring_v2/docs.md` — mirror `retrieval_v2/docs.md` structure: public surface, flow diagram, brief composition section, parser invariants section, provenance links (to brainstorm + this plan + impl convo), empirical validation tier table, downstream consumers, "what this module does NOT do".

Commit: `scoring_v2: public exports + module docs; ruff clean`

---

## Things that may go wrong (pause-and-surface)

Per the handoff's "Don't skip the convo's 'Things this brainstorm is locking blind on'" — three lock-blind areas. Each requires pause + surface, not silent patching:

1. **Citations + tool use composition behavior at scoring load.** Retrieval's T1 cleared on a 2-sentence fixture with 2 tool calls. Scoring's T1 is similarly minimal (3 sentences, 2 tool calls), but production scoring will hit 30+ cells per chunk × multiple tool calls per cell. **If T1 surfaces that the parser's pairing rule breaks at this density (e.g., citations don't attach predictably to the immediately-following tool call when many tools fire in a row), STOP.** Surface for re-evaluation; do not silently patch the parser to accommodate divergence from the hand-crafted-fixture invariant. (Retrieval's pairing-rule lesson — commit `5f262e9` — was learned exactly this way.)

2. **`CompendiumCell.provenance` schema-change blast radius.** Audit at plan-write time found 1 site (`tests/test_models_v2_cells.py:69`). **If at Phase 7 execution time the count differs (someone added new `provenance=` constructions between plan-write and impl session), STOP** and surface — the audit is no longer authoritative, and silent updates may break someone else's in-flight work on a sister branch (multi-committer repo).

3. **Practical-axis brief-writer feasibility — out of scope, flagged forward.** This plan ships legal-axis only. The sibling brainstorm (queued) will need to design portal-artifact (HTML/PDF/XLSX/ZIP) handling under Citations API, which is empirically unmeasured. **If during scoring_v2 impl the user asks to extend to practical, push back**: the brief-writer signature commits to `statute_bundle: list[dict]` of text documents; portal-snapshot handling is qualitatively different (`suspicious_challenge_stub` flags, mixed media types, role labels) and warrants its own brainstorm.

Other concrete failure modes worth pre-flighting:

4. **Specialized cell-class value shape divergence.** The plan inlines `_instantiate_with_special_shapes` to handle `TimeThresholdCell` / `CountWithFTECell` / `EnumSetWithAmountsCell` / `EnumSetCell`-like cells whose tool `value` is a dict not a scalar. **If T1 reveals the model emits a flat scalar where the parser expects a dict** (or vice versa), surface for prompt-text tightening rather than parser leniency — let validation errors stay loud.

5. **Model emits `axis="practical"` under a mixed-chunk brief.** Per Q6, practical halves are filtered out of the cell roster; the model should never emit them. If it does anyway: the parser's registry lookup will find the `(row_id, "practical")` cell, dispatch normally, and the resulting cell will technically validate — but the downstream consumer expects legal-only. **Plan-write call:** parser logs a warning but does NOT drop; let the orchestrator + Phase C consumers decide whether to filter. (If the user prefers strict filtering at parse time, surface for a Q6.5 lock.)

6. **Empty `cells` AND empty `unscoreable_cells` from a non-empty roster.** The model returned without scoring any cell in scope. `ScoringOutput` will have `cells == () and unscoreable_cells == ()`. **Parser doesn't raise** (the message was well-formed), but the orchestrator should treat this as a soft failure to retry. Diagnostics-only at T1; the orchestrator can decide what to do at T2+.

---

## Carry-forward links

In session-start read order (matches handoff's link list):

1. [`../../../../STATUS.md`](../../../../STATUS.md) — current focus
2. [`../../../../README.md`](../../../../README.md) — project framing
3. [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — branch trajectory; brief-writer brainstorm entry at top
4. [`../convos/20260514_brief_writer_brainstorm.md`](../convos/20260514_brief_writer_brainstorm.md) — **the brainstorm convo; read in full**
5. [`20260514_brief_writer_plan_sketch.md`](20260514_brief_writer_plan_sketch.md) — the brainstorm agenda
6. [`20260514_retrieval_implementation_plan.md`](20260514_retrieval_implementation_plan.md) — **structural template**
7. [`../convos/20260514_retrieval_implementation.md`](../convos/20260514_retrieval_implementation.md) — retrieval impl convo's "Plan deviations" section (phase-order lesson)
8. [`../convos/20260514_retrieval_v2_t1_and_fixture_decouple.md`](../convos/20260514_retrieval_v2_t1_and_fixture_decouple.md) — fixture-split pattern (Option A; commit `5f262e9`)
9. [`../../../../src/scoring/scorer_prompt.md`](../../../../src/scoring/scorer_prompt.md) — v1 scorer prompt (rewrite source)
10. [`../../../../src/lobby_analysis/retrieval_v2/`](../../../../src/lobby_analysis/retrieval_v2/) — load-bearing pattern template for the module
11. [`20260518_tier_0_minimal_pipeline.md`](20260518_tier_0_minimal_pipeline.md) — first downstream consumer; coordinate Phase 7 schema edit

---

## Commit log (anticipated)

| Phase | Commit |
|---|---|
| 0 | `scoring_v2: scaffolding (empty module + chunk_frames_v2 dir)` |
| 1 | `scoring_v2: failing tests written (RED, all phases)` |
| 2 | `scoring_v2: tool definitions (record_cell + record_unscoreable_cell)` |
| 3 | `scoring_v2: Pydantic output models (ScoringOutput + UnscoreableCell)` |
| 6 | `scoring_v2: v2 prompt markdown (Phase 6 of plan — executed early before brief_writer)` |
| 4 | `scoring_v2: brief_writer.py with documents + citations + caching + preamble + retrieval annotations` |
| 5 | `scoring_v2: parser + hand-crafted sample_response fixture (Phase 5 of plan)` |
| 7 | `scoring_v2 / models_v2: lock CompendiumCell.provenance to retrieval_v2.EvidenceSpan tuple` (skip if Tier-0 already shipped) |
| 8 | `scoring_v2: integration test green; sample_response_real.json captured (gitignored)` |
| 9 | `scoring_v2: public exports + module docs; ruff clean` |

---

## Testing Plan

**T0 (unit, no API key):** 6 test files × ~51 named test signatures total. Each phase turns its target test file green. Discipline: write all tests RED in Phase 1; don't touch them after their phase ships green.

**T1 (integration, requires `ANTHROPIC_API_KEY`):** `tests/test_scoring_v2_integration.py`, 3 tests, ~$0.04 per run. Gated by `pytest.mark.skipif`; clean skip if no key. Runs automatically on every `uv run pytest` when key is set — catches Citations API drift early.

**Anti-patterns this plan refuses to write (per `skills/testing-anti-patterns/SKILL.md`):**

- No tests that mock the SDK client and assert mock-only behavior.
- No prompt-text snapshot tests (locks editorial wording).
- No tests asserting cell-scoring *correctness* against a single state — that's T2+ empirical work, not unit-test surface.
- No tests of Pydantic framework validation (testing the library).

NOTE: All tests written before any implementation, per TDD discipline + the retrieval-impl precedent.

---

## Out-of-scope reminders (won't re-explain)

- Practical-axis brief-writer (Q6).
- Per-chunk preamble content authoring (Q4 — 0 preambles ship).
- The orchestrator / Ralph loop runtime (handoff).
- CSV/Parquet persistence of `StateVintageExtraction` (handoff).
- Per-cell-type tools (Q2 — single polymorphic).
- `models_v2.EvidenceSpan` deletion (Tier-0 deprecates; deletion later).
- T2/T3/T4 empirical accuracy validation (downstream).

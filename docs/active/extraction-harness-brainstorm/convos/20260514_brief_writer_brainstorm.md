# Brief-Writer + Scorer-Prompt-v2 Brainstorm — Convo Summary

**Date:** 2026-05-14
**Branch:** `extraction-harness-brainstorm`
**Plan sketch:** [`../plans/20260514_brief_writer_plan_sketch.md`](../plans/20260514_brief_writer_plan_sketch.md)
**Sibling plan (shipped):** [`../plans/20260514_retrieval_implementation_plan.md`](../plans/20260514_retrieval_implementation_plan.md) — load-bearing pattern template.
**Originating handoff:** [`../plans/_handoffs/20260514_next_session_kickoff.md`](../plans/_handoffs/20260514_next_session_kickoff.md) — split this into 2 components; pushback below merged them.
**Outgoing handoff:** [`../plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md`](../plans/_handoffs/20260514_brief_writer_impl_plan_write_handoff.md) — for the impl-plan-write session.

---

## Session goal

Resolve architectural Q's for the v2 **scoring** harness (legal-axis path), so the next session can write a TDD-shaped implementation plan and an API-launched implementer can execute it end-to-end.

---

## Phase 1 — Carry-forward reading (done)

Read end-to-end:

1. **`src/scoring/scorer_prompt.md`** — v1 scorer prompt; 8 rules. Rule 6 is PRI-keyed (A5-A11 + C0); Rule 5 is rubric-agnostic (read full statute layered); Rule 7 is files-read manifest (probably obsolete under Citations API).
2. **`src/scoring/bundle.py`** — v1 has 3 brief-builders: `build_subagent_brief` (portal), `build_statute_subagent_brief` (statute), `build_retrieval_subagent_brief` (retrieval). All produce instruction text for a **Claude Code subagent** that uses Read/Write tools — not direct SDK + Citations.
3. **`src/scoring/output_writer.py`** — v1 parses subagent-written JSON arrays into `ScoredItem` pydantic instances, then writes stamped CSVs with orchestrator-added columns (model_version, prompt_sha, run_id, etc.).
4. **`src/lobby_analysis/retrieval_v2/brief_writer.py` + `models.py`** — v2 retrieval pattern: `build_retrieval_brief()` returns `messages.create()` kwargs; document blocks with `citations.enabled=True`; tool use (`record_cross_reference` / `record_unresolvable_reference`); `RetrievalOutput` carries `cross_references` with `evidence_spans`.
5. **`src/lobby_analysis/chunks_v2/docs.md`** — 15-chunk manifest + invariants. Explicitly forward-references the brief-writer: "Future brief-writer module will key per-chunk preamble files by `chunk_id`."

**Findings from reading:**

- **Architectural pivot already happened on retrieval.** v1 was subagent-dispatch; v2 retrieval went SDK + Citations + tool use. The "Anthropic SDK is NOT in `pyproject.toml`" deferred decision from the kickoff brainstorm is effectively resolved — `anthropic>=0.102` is live.
- **Two paths in v1, not one.** `build_subagent_brief` (portal) and `build_statute_subagent_brief` (statute) were already separate because the input shapes differ qualitatively (HTML/PDF/XLSX/ZIP/CSV portal artifacts vs clean statute text). This precedent affects Q6 below.
- **Per-chunk preamble forward reference** in chunks_v2 docs is a soft commitment that this brainstorm has to honor or explicitly walk back.

---

## Kickoff exchange — two pushbacks accepted

**Pushback 1: Combine brief-writer + scorer-prompt-rewrite into ONE component.**

The kickoff handoff (`_handoffs/20260514_next_session_kickoff.md`) treated brief-writer (component 3) and scorer-prompt-rewrite (component 4) as separate sessions. But retrieval's experience says: prompt and brief-writer are inseparable — the brief-writer reads the prompt at call time, the prompt assumes the brief-writer's tool definitions exist, and prompt invariants are part of the brief-writer's test surface. Splitting them creates an artificial seam.

**Decision:** **Combine.** This brainstorm + impl plan covers: `scorer_prompt_v2.md` + `brief_writer.py` + `tools.py` + `parser.py` + per-chunk preambles (subject to Q4) + models bindings — all designed against each other.

User-confirmed via AskUserQuestion. Counter-argument acknowledged in the offered option: parallel-fellow-work is a process gain but technical coupling makes it lossy.

**Pushback 2: Follow retrieval's precedent — direct SDK + Citations API + tool use, not subagent dispatch.**

The kickoff handoff deferred the SDK adoption decision. But retrieval already shipped with direct SDK + Citations + tool use, adding `anthropic>=0.102` to `pyproject.toml`. The "ONE pipeline" criterion (Compendium 2.0 #2) says scoring should follow the same pattern for consistency.

**Decision:** **Follow retrieval.** Direct SDK; brief-writer returns `messages.create()` kwargs; Citations API for provenance grounding; tool use for typed-cell output.

User-confirmed via AskUserQuestion.

---

## Already-locked context (from prior brainstorms, carry forward; don't re-litigate)

| Decision | Source | Status |
|----------|--------|--------|
| Combine brief-writer + scorer-prompt rewrite | This session pushback 1 | **Locked this session** |
| Direct SDK + Citations API + tool use | This session pushback 2 (reaffirms retrieval brainstorm) | **Locked this session** |
| `anthropic>=0.102` in `pyproject.toml` | Retrieval impl | **Live** |
| Model + thinking + effort config | Retrieval brainstorm | **Locked (mirror)** |
| Prompt-caching architecture (prompt in cached system; docs in cached user; per-call text uncached) | Retrieval brief-writer pattern | **Locked (mirror)** |
| Cell ID space `(row_id, axis)` | Kickoff brainstorm Q0 | **Locked** |
| 15 chunks, hand-curated manifest | Chunks brainstorm | **Shipped** |
| `CompendiumCell` ABC + 15 subclasses | Cell models impl | **Shipped** |
| Accuracy gate before cost optimization | Retrieval brainstorm Phase 2 | **Locked** |

---

## Phase 2 — Resolve architectural questions

(Filled in as the session progresses.)

### Q6 — Practical-axis cells / portal artifacts: **DEFER**

Three options on the table; user locked **(a) defer** via `AskUserQuestion`.

This brainstorm's scope is the **legal-axis** path only:
- Pure-legal chunks (~6): `actor_registration_required`, `registration_thresholds`, `lobbyist_registration_form_contents`, `principal_spending_report`, `lobbying_contact_log`, `other_lobbyist_filings`.
- Mixed chunks (~5): `lobbying_definitions`, `registration_mechanics_and_exemptions`, `lobbyist_spending_report`, `enforcement_and_audits`, `oversight_and_government_subjects` — these have practical cells that THIS brief-writer **will not score**; orchestrator will route the legal cells here and the practical cells elsewhere when the practical-axis sibling brainstorm lands.

**Implication for tools and parser:** brief-writer receives a chunk's `cell_specs` filtered to `axis == "legal"`. Parser must reject (or ignore with warning) any tool call whose `(row_id, axis)` resolves to `axis == "practical"`.

**Implication for orchestrator (out of scope for THIS brainstorm but flagged):** practical-axis sibling will be brainstormed next; orchestrator merges per-axis scoring outputs into a unified `StateVintageExtraction`.

**This is a second pushback against the user's "combine" decision** — the combine was about brief-writer + prompt-rewrite *for legal scoring*, not about legal + practical. Surfaced explicitly; user agreed.

### Q4 — Per-chunk preamble strategy: **OPTIONAL DISK-LOADED, SHIP 0**

User locked **(d) optional disk-loaded, ship 0** via `AskUserQuestion`.

- Brief-writer logic: `preamble_path = REPO_ROOT / "src/scoring/chunk_frames_v2" / f"{chunk_id}.md"`; if exists, read + insert into user message before cell roster; if not, skip silently.
- Impl plan ships **0** preambles. The directory `src/scoring/chunk_frames_v2/` is created (with `.gitkeep`) so the brief-writer's path resolution doesn't 404 on its parent.
- Preamble authoring becomes **downstream scholarly work**, informed by T1+ smoke evidence of where the model under-grounds.
- **Q5 implication:** v1 Rule 6 substantive guidance (PRI A5-A11 + C0 functional-public-entity content) lands in preambles when authored — likely `actor_registration_required.md` for A5-A11 content + `lobbying_definitions.md` for C0 content. NOT in `CompendiumCellSpec` schema (no v2 TSV/models churn).

---

### Q1 — Dispatch unit: **PARAMETERIZED chunks: list[str], DEFAULT per-chunk**

User locked **mirror retrieval** via `AskUserQuestion`. 15 calls per (state, vintage) for the full legal-axis sweep (11 chunks if practical-only chunks are excluded; 15 if not — but per Q6 practical-only chunks won't be scored by this brief-writer at all).

- `build_scoring_brief(state, vintage, chunks: list[str], retrieval_output, statute_bundle, ...)`.
- Brief-writer validates `chunks` against `build_chunks()` — unknown chunk_id raises `ValueError`.
- Per-chunk default — same accuracy-first rationale as retrieval. Aggregate cost is bounded by prompt caching.

### Q2 — Tool use shape: **SINGLE POLYMORPHIC `record_cell` (plus `record_unscoreable_cell` per Q7-sub)**

User locked **(a) single polymorphic** via `AskUserQuestion`.

- `record_cell(row_id, axis, value, conditional, condition_text, confidence, notes)` — value is loose JSON; parser dispatches by `row_id` → `CompendiumCellSpec.expected_cell_class` → instantiates the right subclass.
- Two tools total: `record_cell` + `record_unscoreable_cell` (per Q7-sub). Mirrors retrieval's two-tool surface.
- Per-cell-type tools (15) deferred — if T2-T4 evidence shows the model systematically mis-types values, revisit.

### Q3 — Statute bundle assembly: **ALL STATUTES + RETRIEVAL ANNOTATIONS AS USER TEXT**

User locked **(a) all + annotations** via `AskUserQuestion`.

- Document blocks: same statute set retrieval consumed. Identical doc order → cache-friendly cross-call sharing with retrieval. `citations.enabled=True` + `cache_control: {"type": "ephemeral"}` on each.
- User-text section: summarize `RetrievalOutput.cross_references` (per cross-ref: `section_reference`, `relevance`, `chunk_ids_affected`, key `evidence_spans` excerpted as quoted text). Frames retrieval's findings as context-with-evidence, not constraint.
- Practical implication: brief-writer signature includes `retrieval_output: RetrievalOutput`. Practical-only chunks (deferred per Q6) wouldn't have a retrieval_output, so this signature is legal-axis-only — consistent with Q6.

### Q7-sub — `unable_to_evaluate` equivalent: **SEPARATE `UnscoreableCell` MODEL + `record_unscoreable_cell` TOOL**

User locked **(a) parallel to retrieval** via `AskUserQuestion`. Direct symmetry with retrieval:

| Retrieval | Scoring |
|-----------|---------|
| `record_cross_reference` | `record_cell` |
| `record_unresolvable_reference` | `record_unscoreable_cell` |
| `RetrievalOutput.cross_references` | `ScoringOutput.cells` |
| `RetrievalOutput.unresolvable_references` | `ScoringOutput.unscoreable_cells` |
| `CrossReference` | `CompendiumCell` (existing) |
| `UnresolvableReference` | `UnscoreableCell` (NEW) |

`UnscoreableCell` shape (proposed): `cell_id: str`, `reason: str`, `confidence: ConfidenceLevel`, `evidence_spans: tuple[EvidenceSpan, ...] = ()`. Cell_id matches `CompendiumCellSpec.row_id` + axis convention.

No `CompendiumCell` schema churn for the unscoreable case — clean separation.

### Q8 — `CompendiumCell.provenance`: **CHANGE TO `tuple[EvidenceSpan, ...]`**

User locked **(a) change to tuple** via `AskUserQuestion`. Schema edit to `src/lobby_analysis/models_v2/cells.py`:

```python
# BEFORE
provenance: EvidenceSpan | None = None

# AFTER
provenance: tuple[EvidenceSpan, ...] = ()
```

Low blast radius: shipped but downstream consumers (Phase C) haven't ramped yet. Length-1 tuple covers the prior single-span semantic. Mirror retrieval's `CrossReference.evidence_spans` shape exactly.

**Important:** this schema change requires updating any existing test/fixture/seed that constructed a `CompendiumCell` with `provenance=None` or `provenance=<EvidenceSpan>`. Audit at impl-plan-write time.

### Q7-rules — v1 `scorer_prompt.md` rule-by-rule carry-forward

| v1 Rule | v2 Disposition | Rationale |
|---------|----------------|-----------|
| 1 (evidence cite mandatory) | **Drop** — subsume into prompt instruction "cite via Citations before each tool call" | Citations API structurally enforces |
| 2 (handle inaccessible honestly: `unable_to_evaluate`) | **Keep** as principle; mechanism = `record_unscoreable_cell` (Q7-sub) | The escape-valve is load-bearing |
| 3 (score per data_type) | **Morph** — parser validates per-cell-type after lookup; prompt names the cell roster + axis labels so model knows what shape | Mechanism is tool-use + parser, not output-schema |
| 4 (confidence as self-assessment) | **Keep** — already in `CompendiumCell.confidence` and tool input | Rubric-agnostic |
| 5 (read full statute layered) | **Keep, prominently** — rubric-agnostic + critical for legal accuracy | Citations API doesn't enforce read coverage |
| 6 (PRI A5-A11 + C0 substantive guidance) | **Replace** — content moves to per-chunk preambles (Q4 = optional disk-loaded; ship 0; author when needed) | The v2-rewrite scholarly work, deferred |
| 7 (files-read manifest) | **Drop** — Citations evidences read coverage structurally | Coverage cross-check, if needed, lives in validation tooling |
| 8 (no preamble, no summary) | **Replace** with tool-use enforcement: "respond only by emitting `record_cell` / `record_unscoreable_cell` tool calls; freeform text allowed only as Citations-grounded reasoning preceding each tool call" | Tool use is the v2 output channel |

### Q9 — Parser output container: **`ScoringOutput` (mirror `RetrievalOutput`)**

Locked by elimination — once Q7-sub picked the parallel `UnscoreableCell` model, the container shape follows symmetry:

```python
class ScoringOutput(BaseModel):
    model_config = {"frozen": True}
    state_abbr: str
    vintage_year: int
    chunk_id: str
    cells: tuple[CompendiumCell, ...] = ()
    unscoreable_cells: tuple[UnscoreableCell, ...] = ()
```

Scoped to one call: `(state, vintage, chunk_id)`. Orchestrator merges per-chunk outputs into a `StateVintageExtraction` (orchestrator out of scope for THIS brainstorm).

### Q10 — File location: **`src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md`**

Locked by precedent — mirror retrieval. Optional disk-loaded preambles in `src/scoring/chunk_frames_v2/<chunk_id>.md` (Q4); directory shipped with `.gitkeep`, 0 preambles authored.

---

## Decisions made (audit trail)

| Q | Decision | Date | Rationale |
|---|----------|------|-----------|
| (kickoff) Combine brief-writer + scorer-prompt-rewrite | YES | 2026-05-14 | Retrieval set precedent; tight coupling makes parallel work lossy |
| (kickoff) Direct SDK + Citations API + tool use | YES | 2026-05-14 | Retrieval precedent; "ONE pipeline" consistency |
| Q6: Practical-axis cells | **Defer to sibling brainstorm** | 2026-05-14 | Empirical Citations-API-on-portal-HTML behavior unmeasured; portal artifacts qualitatively different; combining dilutes legal-side design |
| Q4: Per-chunk preamble strategy | **Optional disk-loaded, ship 0** | 2026-05-14 | Pragmatic; preserves iter-1 chunk-frame pattern as a hook without committing to scholarly v2 rewrite content this session; downstream-informed authoring |
| Q5: Per-cell substantive guidance | **Lives in chunk preambles (when authored), NOT in CompendiumCellSpec** | 2026-05-14 | Follows from Q4; avoids schema churn on shipped `models_v2` |
| Q1: Dispatch unit | **Parameterized `chunks: list[str]`, default per-chunk** | 2026-05-14 | Mirrors retrieval; accuracy-first; iter-1's 7-row baseline is the comparison point |
| Q2: Tool use shape | **Single polymorphic `record_cell` + `record_unscoreable_cell`** | 2026-05-14 | Mirrors retrieval's 2-tool surface; parser does cell-class dispatch via registry |
| Q3: Statute bundle assembly | **All statutes + retrieval annotations as user text** | 2026-05-14 | Cache-friendly with retrieval (same doc set); preserves scorer's right to disagree with retrieval scope |
| Q7-sub: Unscoreable cell | **Separate `UnscoreableCell` + `record_unscoreable_cell` tool** | 2026-05-14 | Direct parallel to retrieval's `UnresolvableReference`; no `CompendiumCell` wrapper churn |
| Q7-rules: v1 rule carry-forward | **Drop 1,7; replace 6,8; morph 3; keep 2 (mechanism=Q7-sub), 4, 5** | 2026-05-14 | Citations API + tool use shift the structural enforcement; substantive guidance moves to preambles |
| Q8: `provenance` schema | **Change to `tuple[EvidenceSpan, ...]`** | 2026-05-14 | Mirror retrieval; Citations returns multiple spans; low blast radius (Phase C not yet ramped) |
| Q9: Parser output container | **`ScoringOutput` (mirror `RetrievalOutput`)** | 2026-05-14 | Symmetry with retrieval; scoped to one call |
| Q10: File location | **`src/lobby_analysis/scoring_v2/` + `src/scoring/scorer_prompt_v2.md`** | 2026-05-14 | Mirror retrieval naming; YAGNI on broader reorg |

---

## Locked package (synthesis)

The implementation plan must produce, in shipped order:

1. **`src/lobby_analysis/scoring_v2/` module** — parallel to `retrieval_v2/`:
   - `models.py` — `ScoringOutput` + `UnscoreableCell` (new pydantic models).
   - `tools.py` — `RECORD_CELL_TOOL` + `RECORD_UNSCOREABLE_CELL_TOOL`. Coupling test: row_id enum (if any in tool schema) sourced from `build_cell_spec_registry()` keys; no drift.
   - `brief_writer.py` — `build_scoring_brief(state, vintage, chunks: list[str], retrieval_output: RetrievalOutput, statute_bundle: list[dict], url_pattern: str = "") -> dict`. Loads optional preambles from `src/scoring/chunk_frames_v2/<chunk_id>.md` if present.
   - `parser.py` — `parse_scoring_response(message, state_abbr, vintage_year, chunk_id) -> ScoringOutput`. Pairing rule: citations on text blocks accumulate; on `record_cell`/`record_unscoreable_cell` tool_use, flush onto that tool's evidence_spans / cell.provenance and reset. Unknown tool names reset.
   - `__init__.py` — public exports: `ScoringOutput`, `UnscoreableCell`, `build_scoring_brief`, `parse_scoring_response`.
   - `docs.md` — module-level docs matching `retrieval_v2`/`chunks_v2`/`models_v2` pattern.

2. **`src/scoring/scorer_prompt_v2.md`** — the v2 scoring prompt:
   - Drops rubric language; cell-anchored.
   - Drops Rules 1, 7; replaces Rules 6, 8; morphs Rule 3; keeps Rules 2 (mechanism = `record_unscoreable_cell`), 4, 5.
   - Rule 5 ("read full statute layered") promoted as load-bearing.
   - Instruction: cite (via Citations API) before each tool call.
   - No PRI keys (`A5`-`A11`, `C0`-`C3`) remain — verified by `test_prompt_invariants.py`.

3. **`src/scoring/chunk_frames_v2/.gitkeep`** — directory exists, 0 preamble files. Brief-writer's path resolution gracefully handles absent preambles.

4. **`src/lobby_analysis/models_v2/cells.py` edit** — `provenance: tuple[EvidenceSpan, ...] = ()` (was `EvidenceSpan | None = None`). All existing tests/fixtures that construct `CompendiumCell` with `provenance=None` or `provenance=<EvidenceSpan>` need updating.

5. **Tests, written RED first per TDD:**
   - `test_scoring_v2_tools.py` — tool schemas, coupling tests
   - `test_scoring_v2_models.py` — ScoringOutput, UnscoreableCell shapes
   - `test_scoring_v2_brief_writer.py` — assembly, validation, optional preamble loading
   - `test_scoring_v2_parser.py` — fixture-based; citation pairing; cell-class dispatch
   - `test_scoring_v2_prompt_invariants.py` — no PRI keys; Citations instruction present; tool-use rule present
   - `test_scoring_v2_integration.py` — T1 smoke; `skipif` on `ANTHROPIC_API_KEY`; cost ≈ $0.05 per run

6. **`pyproject.toml`** — no new dependencies (`anthropic` + `pydantic` already in).

---

## Things this brainstorm is locking blind on

- **Citations API + tool use composition behavior** for the scoring use case (longer statutes, more cells per call, more tool calls per response than retrieval). Retrieval's T1 smoke (deferred to desktop) is the canary; if its parser pairing rule turns out to mismatch, scoring inherits the fix.
- **Single polymorphic tool vs per-type tools** for value-typing accuracy — no direct iter-1 evidence. T2+ evidence will determine if per-type is needed.
- **`CompendiumCell.provenance` schema change tolerance** — Phase C consumer-side hasn't ramped; verify before shipping the impl plan.
- **Practical-axis brief-writer design** — entirely deferred to sibling brainstorm; assuming portal artifacts under Citations API will be its own design problem.
- **Empirical accuracy floor for the legal-axis scoring** — iter-1's 93.3% was on a single 7-row chunk against PRI rubric. v2's 186-cell space is much broader; per-chunk accuracy will vary.

---

## Process notes

1. Agent pushed back on the kickoff handoff's 4-component framing in the opening exchange of the session, **before** writing the plan-sketch. The plan-sketch reflects the consolidated framing rather than re-litigating the handoff's split.
2. Two architectural pushbacks were batched into a single `AskUserQuestion` call, both accepted. Saved a round-trip.
3. Per the user memory note about not patchwork-shipping: drafted the plan-sketch + brainstorm convo before any Phase-2 `AskUserQuestion` calls, so the link graph was consistent at every commit boundary.
4. **Second pushback (Q6 = defer practical-axis)** was a deliberate re-fork of the kickoff "combine" decision — surfacing explicitly that "combine" was about prompt+brief-writer for legal scoring, not about legal+practical. User agreed.
5. **Six locked Q's mirror retrieval directly** (Q1, Q2, Q3, Q7-sub, Q8, Q9, Q10) — the cost is consistency-and-symmetry; the gain is a code-reviewable parallel structure. Process inertia is real and intentional here.
6. **One Q (Q4) deferred scholarly work** — the v1 Rule 6 substantive content (PRI A5-A11 + C0 functional-public-entity guidance) didn't get rewritten this session; it lands in chunk preambles when authored, informed by empirical evidence of where the model under-grounds.

---

## Things this brainstorm is locking blind on (so far)

- Citations API + tool use composition behavior — retrieval's T1 smoke (deferred to desktop run) will surface this. If retrieval's parser pairing rule turns out to mismatch reality, brief-writer's parser inherits the fix.
- `CompendiumCell.provenance` schema change tolerance — single-span vs tuple-of-spans (Q8). Phase C consumer-side hasn't ramped yet, so blast radius should be small, but verify before shipping.
- Practical-axis brief-writer feasibility under Citations API — portal HTML/PDF behavior with citations is empirically unmeasured. If we defer practical-axis to a sibling brainstorm (Q6 = a), this lock-blind transfers there.

---

## Process notes (so far)

1. Agent pushed back on the kickoff handoff's 4-component framing in the opening exchange of the session, **before** writing the plan-sketch. The plan-sketch reflects the consolidated framing rather than re-litigating the handoff's split.
2. Two architectural pushbacks were batched into a single `AskUserQuestion` call, both accepted. Saved a round-trip.
3. Per the user memory note about not patchwork-shipping: drafting the plan-sketch + brainstorm convo before any AskUserQuestion calls on Phase 2 Q's, so the link graph is consistent at every commit boundary.

# Chunk-Grouping Function — Brainstorm Convo

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Agenda followed:** [`../plans/20260514_chunks_plan_sketch.md`](../plans/20260514_chunks_plan_sketch.md)
**Predecessor convos:** [`20260514_v2_pydantic_cell_models_implementation.md`](20260514_v2_pydantic_cell_models_implementation.md) (built the registry this consumes) and [`20260514_extraction_harness_brainstorm.md`](20260514_extraction_harness_brainstorm.md) (Q0–Q6 architectural decisions, esp. Q1's chunked-by-domain 5-12 lock)

## Session frame

This is the **second brainstorm-then-plan cycle on this branch**, following the same structure as the kickoff brainstorm that produced the cell-models plan. The chunks plan-sketch (linked above) is the agenda; this convo executes it.

**Session strategy:** the user proposed (and locked in advance) a higher-level workflow — brainstorm and plan all 4 downstream components first, with the user in the loop, then launch implementation work as API sub-branches in parallel and merge back. This convo is the first half of that strategy for component 1 (chunks). The retrieval brainstorm/plan follows in this same session.

## Phase 1 — Carry-forward reading

### Iter-1 `definitions` chunk-frame (`origin/statute-extraction:src/scoring/chunk_frames/definitions.md`)

Re-read end-to-end. Key takeaways for the chunking function design:

1. **Chunk-frame preambles are substantive tutorials, not metadata.** The iter-1 `definitions` frame teaches the LLM a three-axis decomposition (TARGET / ACTOR / THRESHOLD) of "what makes someone count as a lobbyist," includes per-row axis assignments, and provides linguistic disambiguation cues ("contact with X" → TARGET; "X engages in" → ACTOR; "exceeds $X" → THRESHOLD).
2. **The frame names individual rows by ID and explains each row's axis.** The chunking function's output must therefore expose stable row-level membership so the preamble author can reference rows by ID.
3. **A chunk can have rows that span multiple axes** (the `definitions` chunk has TARGET, ACTOR, and THRESHOLD rows together) — chunks are **topic-coherent**, not axis-homogeneous.
4. **v1.2 row IDs in the iter-1 frame:** `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`, `DEF_ELECTED_OFFICIAL_AS_LOBBYIST`, `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST`, `DEF_COMPENSATION_STANDARD`, `DEF_EXPENDITURE_STANDARD`, `DEF_TIME_STANDARD`, `THRESHOLD_LOBBYING_MATERIALITY_GATE`. The v2 equivalents map roughly to `def_target_executive_agency` (+ `executive_staff` + `governors_office` + `independent_agency` + `legislative_branch` + `legislative_staff` = 6 rows), plus selected `actor_*` rows (the lobbyist-identifying ones, like `actor_paid_*`, `actor_volunteer_*`), plus `compensation_threshold_for_lobbyist_registration`, `expenditure_threshold_for_lobbyist_registration`, `time_threshold_for_lobbyist_registration`, and `law_includes_materiality_test`. So **the v2 successor to the iter-1 `definitions` chunk is likely 10-14 rows** — well within the 5-12 target with a small bleed.

### Q1's prior locked decision

From the kickoff brainstorm: "Hybrid — chunked-by-domain with a chunk-frame preamble per chunk + per-row instruction within the chunk. Chunk size target: 5-12 rows. Same prompt template across all chunks." The "5-12" is a target with implicit tolerance, not a hard constraint. The iter-1 7-row chunk is the only empirical anchor.

### TSV ground truth

Captured in [the plan-sketch's TSV section](../plans/20260514_chunks_plan_sketch.md#tsv-ground-truth-informs-the-brainstorm) — 4 over-sized first-2-token domains (34, 21, 16, 13), 5 combined-axis rows, ~20-25 singletons/small-cluster rows.

## Phase 2 — Architectural decisions

### Q1-revised — Chunk-size economics changed when prompt-caching architecture surfaced

**The plan-sketch enumerated three Q1 options (a/b/c) all anchored to the kickoff brainstorm's 5-12 row target. The user flagged at the start of this brainstorm that the chunk-size constraint is fundamentally different in a prompt-caching architecture:**

- The state-vintage statute bundle goes in the LLM call's `system` block — cached across all chunk-calls for that (state, vintage).
- The chunk-specific preamble + per-row instructions go in `user` — uncached.
- So per-chunk *uncached* cost is dominated by the chunk-frame preamble + N × per-row-instruction + N × output cells. The statute itself is amortized free across all chunks for that (state, vintage).
- Iter-1's 7-row chunk-size was sized against a non-cached prompt where every chunk re-paid the statute cost. Under caching, that economic constraint goes away.

**Decision: revise the prior brainstorm's "5-12 rows per chunk" lock to "~30 rows per chunk soft cap, flex to ~34 for natural single-topic clusters."** The 5-12 lock is superseded. Iter-1's 7-row anchor remains an *empirical agreement point* (93.3% inter-run agreement on a small chunk), but it's not a *constraint* — bigger chunks should work as well or better under caching since cross-row context is even more available within a chunk.

**Implication for Q1 taxonomy:** Pure first-2-token splitting produces 53 chunks (34 of them singletons) — too many. A hand-curated topic manifest under the ~30 cap produces ~15 chunks of 3-34 rows each, drawn for topic coherence. **Hand-curated topic manifest is the locked taxonomy.**

User-confirmed via AskUserQuestion 2026-05-14.

### Q2 — Hard size bounds + handling of small/large clusters

**Decision:** Soft cap at 30 rows, hard cap at 34 (the `lobbyist_spending_report` cluster as a single chunk). No hard floor — small coherent chunks (3-5 rows) are fine when they're topically distinct from neighbors.

**Rationale:**
- The 34-row `lobbyist_spending_report` cluster has internal sub-structure (cadence / available_as / includes_* / required+format) but the cluster as a whole is "what's in a lobbyist's spending report" — the iter-1 evidence is that topical coherence wins over sub-splitting. Same prompt framing applies to all 34 rows.
- Below 30, chunk size is driven by topic coherence, not by minimum-size considerations. A 3-row `registration_mechanics` chunk is fine.
- Above 34: split into sub-chunks at the most natural topic boundary. No current cluster hits this.

**No "misc" bucket.** Every row gets a topically-coherent home. The few rows that resist grouping (e.g., `lobbying_definition_included_activity_types`) join their closest semantic neighbor; the manifest documents the assignment rationale per-row when it's non-obvious.

### Q3 — Combined-axis row handling

**Decision:** Same chunk for both halves of all 5 legal+practical rows.

**Rationale:**
- The legal-axis answer often constrains the practical-axis score (e.g., if `lobbyist_registration_required` is `BinaryCell(value=False)` at legal, then the practical-axis GradedIntCell has no portal to score). Cross-axis context helps the LLM.
- Most practical-axis rows cluster in `lobbying_search_*` / `lobbying_data_*` / `lobbyist_directory_*` (portal family), domain-distinct from legal-axis statute-shape rows. The 5 combined rows are the *only* forced-cross-axis cases; treating them as natural same-chunk preserves axis-cohesion elsewhere.

User-confirmed via AskUserQuestion 2026-05-14.

### Q4 — Output data shape

**Decision:** `list[Chunk]` where `Chunk` is a frozen dataclass:

```python
@dataclass(frozen=True)
class Chunk:
    chunk_id: str                              # stable identifier; matches preamble file basename
    topic: str                                 # human-readable
    cell_specs: tuple[CompendiumCellSpec, ...]  # frozen tuple for immutability
    axis_summary: str                          # "legal", "practical", or "mixed"
    notes: str | None = None                   # rationale for non-obvious assignments
```

**Rationale:**
- Mirrors `CompendiumCellSpec`'s frozen-dataclass pattern from cell-models work.
- `chunk_id` gives the brief-writer a stable key for preamble lookup (whether preambles live in code, data files, or are generated).
- `axis_summary` lets downstream consumers filter / report by axis without re-walking `cell_specs`.
- `notes` field captures manifest-author rationale, which matters because the manifest is hand-curated.

User-confirmed via AskUserQuestion 2026-05-14.

### Q5 — Stability under TSV growth

**Decision:** Chunk-membership is enforced by a **coverage test**, not by an algorithm. The manifest is the contract.

**Mechanism:**
- `build_chunks()` calls `build_cell_spec_registry()` (which has 186 entries pinned).
- It walks the manifest, producing `Chunk` objects.
- A post-build invariant check asserts: every `(row_id, axis)` in the registry appears in exactly one `Chunk.cell_specs`, and no chunk references a `(row_id, axis)` not in the registry.
- Test asserts the same invariant; if a TSV row is added without a manifest update (or vice versa), the test fails with a precise diagnostic.

**Implication for TSV evolution:** Adding a row → developer edits the manifest to assign it. This is the correct workflow — the manifest IS the design lever, and a new row deserves a deliberate chunk-assignment decision, not an algorithmic auto-place.

**`chunk_id` stability:** chunk_ids are part of the manifest (string literals), so they're stable across registry growth as long as the manifest preserves chunk identities. Adding new chunks (for new domains) doesn't perturb existing ones. iter-1's `definitions` chunk's successor keeps `chunk_id="lobbying_definitions"` (or whatever the manifest assigns) regardless of how many rows it contains.

### Q6 — Module location

**Decision:** `src/lobby_analysis/chunks_v2/` — parallel to `models_v2/`.

**Structure:**
```
src/lobby_analysis/chunks_v2/
├── __init__.py     # public exports: Chunk, build_chunks, CHUNKS_V2 (manifest constant)
├── chunks.py       # Chunk dataclass + build_chunks() function
└── manifest.py     # CHUNKS_V2: tuple[ChunkDef, ...] — the hand-curated chunk manifest
```

Where `ChunkDef` is a lightweight authoring-time struct (chunk_id, topic, member_row_ids, axis_summary, notes) that gets resolved into `Chunk` objects at `build_chunks()` call time by looking up each `member_row_id` against both axes in the registry.

User-confirmed via AskUserQuestion 2026-05-14.

### Q7 — Function signature

**Decision:** `build_chunks(registry: dict[tuple[str, str], CompendiumCellSpec] | None = None) -> list[Chunk]`.

- `registry=None` → internal call to `build_cell_spec_registry()`. Matches cell-models' `build_cell_spec_registry(tsv_path=...)` default-param pattern.
- Injectable registry param lets tests build chunks against synthetic registries for edge-case checks (e.g., "what happens when a manifest entry references a row not in the registry?").

Not a decision worth its own AskUserQuestion; falls out of the cell-models pattern.

### Sub-Q — Manifest storage: Python data vs external file?

**Decision:** Python data (`tuple[ChunkDef, ...]` in `manifest.py`). YAGNI on TSV/YAML.

**Rationale:** the manifest is ~15 entries, each with a stable structure. Python lets us type-check it (and lint enforces no orphan row_ids if we add a build-time validator). External file would require parsing + schema + I/O for no gain over the in-code manifest at this size.

Revisit if/when the manifest grows past ~30 entries or external tooling needs to consume it.

## What this brainstorm produces

[`../plans/20260514_chunks_implementation_plan.md`](../plans/20260514_chunks_implementation_plan.md) — the TDD-shaped implementation plan an API-launched implementer can run end-to-end.

## Open questions left for downstream

- **Preamble storage** (chunk_id → preamble text) is for the brief-writer brainstorm to decide. The chunk-grouping function only emits `chunk_id`; the brief-writer chooses how to look up the preamble (in-code dict, data files under `chunks_v2/preambles/`, or generated from chunk metadata).
- **Per-chunk LLM call concurrency** (do we fire all chunk-calls for one (state, vintage) in parallel, or sequentially?) is for the orchestrator brainstorm. The chunk-grouping function's output is order-stable so deterministic-sequence-execution is straightforward; parallel-execution is also straightforward since chunks are independent.
- **Manifest evolution policy** for downstream rubric additions: the v2 row set is frozen at 181 rows per Compendium 2.0 success criterion #1. Future rubric additions (e.g., a 9th rubric) trigger a Compendium 3.0 promotion event, not a silent manifest edit. So the manifest is stable at ~15 chunks for the foreseeable future.

## Carry-forward to retrieval brainstorm

The chunks output's `axis_summary` field interacts with retrieval: a `practical`-axis chunk only needs portal screenshots / portal source code, not statute text; a `legal`-axis chunk needs statute text. The retrieval brainstorm should pick this up.

## Next session (for this branch)

Execute the chunks implementation plan via API sub-branch, then retrieval (after this convo) → its implementation plan → its API sub-branch → merge both back to `extraction-harness-brainstorm`.


# Chunk-Grouping Function — Plan Sketch (brainstorm agenda)

**Goal:** Take this branch from "v2 cell models + 186-cell registry landed" to "chunk-grouping function TDD-able and ready to ship via API sub-branch." Plan-sketch is the brainstorm-first agenda; the brainstorm convo resolves the Q's; the implementation plan that follows is the API-launchable artifact.

**Originating handoff:** [`_handoffs/20260514_next_session_kickoff.md`](_handoffs/20260514_next_session_kickoff.md) — recommends chunk-grouping as the first downstream component (pure-data, depends only on the frozen `CompendiumCellSpec` registry, unblocks brief-writer + scorer-prompt).

**Prior binding decisions:** [`../convos/20260514_extraction_harness_brainstorm.md`](../convos/20260514_extraction_harness_brainstorm.md) — Q0–Q6.
The relevant one for this component is **Q1 (Prompt granularity)**: *"Hybrid — chunked-by-domain (5-12 rows) with a chunk-frame preamble per chunk + per-row instruction within the chunk. Same prompt template across all chunks."* The chunk-grouping function operationalizes that decision against the 186-cell roster.

**Empirical anchor:** Iter-1's 7-row `definitions` chunk against OH 2025 hit **93.3% inter-run agreement** across 3 temp-0 claude-opus-4-7 runs. That chunk lives at `origin/statute-extraction:src/scoring/chunk_frames/definitions.md` and uses v1.2 row IDs (e.g., `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`), not v2 (e.g., `def_target_executive_agency`). The 7-row size is the only data point we have on chunk granularity; it sits in the middle of Q1's locked 5-12 range, which is where chunks should cluster.

**Confidence:** Exploratory on chunking taxonomy + output shape; high on the size target (Q1 locked 5-12). The TSV row inventory below is hard ground; the open Q's are about how to slice it.

**Branch:** `extraction-harness-brainstorm` (worktree `.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, Pydantic 2.x (for the chunk dataclass if needed; alternatively `@dataclass(frozen=True)` to match `CompendiumCellSpec`'s pattern). Tests via pytest, lint via ruff. No new dependencies expected.

---

## What this component is and isn't

**Is:** A pure-data function that takes the canonical 186-cell roster (from `build_cell_spec_registry()`) and returns an ordered partition of it into prompt-sized chunks. Each chunk carries enough metadata for the brief-writer to emit a chunk-frame preamble + per-row instructions.

**Isn't:**
- The chunk-frame preambles themselves (those are content per chunk; produced by the brief-writer or live as data files alongside the chunking function).
- The brief-writer module (consumes this function's output; separate component).
- The LLM-calling harness (consumes briefs; further downstream).
- Anything that touches the Anthropic SDK or makes network calls.

---

## TSV ground truth (informs the brainstorm)

Run against `compendium/disclosure_side_compendium_items_v2.tsv` at this branch's HEAD:

**Axis distribution:** 126 legal-only + 50 practical-only + 5 legal+practical = 181 TSV rows → 186 cells.

**Largest first-2-token clusters (>=5 rows):**

| Cluster | Rows | Notes |
|---------|------|-------|
| `lobbyist_spending` | 34 | Splits at first-3-token boundary into 5 sub-clusters: `*_report_available_as_*` (4 practical), `*_report_cadence_*` (7 legal), `*_report_filing_cadence` (1 combined), `*_report_includes_*` (15 legal), top-level required/scope/format (5+ legal). One row is combined-axis. |
| `principal_spending` | 21 | Mirrors `lobbyist_spending_report`: cadence (7), `*_includes_*` (12), top-level required/format (2). All legal. |
| `lobbying_search` | 16 | `*_filter_by_*` (15 practical) + `*_simultaneous_multicriteria_capability` (1 practical). All practical. |
| `lobbyist_reg` | 13 | `lobbyist_reg_form_includes_*` (13 legal). Right at the chunk-size upper bound. |
| `lobbying_contact` | 9 | `lobbying_contact_log_includes_*` (9 legal). Inside 5-12; good as-is. |
| `lobbying_data` | 8 | All practical, portal data quality + format. |
| `def_target` | 6 | All legal, the "what is a lobbying target" definitions. Direct successor to iter-1's `definitions` chunk. |
| `lobbying_disclosure` | 6 | Mixed: 1 combined-axis (audit_required_in_law), 5 practical. |
| `lobbyist_or` | 5 | All legal. |
| `lobbyist_directory` | 5 | All practical. |

**Long tail of singletons / 2-row prefixes:** `actor_*` (11 rows, all 1-row prefixes, all legal — these are the registration-required-by-actor-class rows), `def_actor` (2), `exemption_*` (2), `expenditure_*` (2), `compensation_threshold` (1), `time_threshold` (1), `law_*` (2), and ~10 others. **~20-25 rows total are in singletons or small (≤2) clusters and need a collapse strategy.**

**The 5 combined-axis rows** all live in `lobbying_*` / `lobbyist_*` / `registration_*` families:
- `lobbyist_registration_required` — `binary (legal) + typed int 0-100 step 25 (practical)`
- `lobbyist_spending_report_filing_cadence` — `enum (legal) + typed int 0-100 step 25 (practical)`
- `lobbying_disclosure_audit_required_in_law` — `enum (legal) + typed int 0-100 step 25 (practical)`
- `lobbying_violation_*` — `binary (legal) + typed int 0-100 step 25 (practical)`
- `registration_deadline_*` — `binary (legal) + typed int 0-100 step 25 (practical)`

Each produces 2 cells in the registry. Chunk assignment for both halves is open.

---

## Brainstorm agenda (the second real brainstorm session on this branch)

### Phase 1 — Re-read the carry-forward chunk-frame (~15 min)

1. **`origin/statute-extraction:src/scoring/chunk_frames/definitions.md`** — the iter-1 7-row definitions chunk-frame. Read for: (a) what's in the preamble that's chunk-specific (axis disambiguation, target/actor/threshold framing), (b) what's reusable structurally for other chunks, (c) the row IDs are v1.2 — note which v2 rows the chunk targeted (the 6 `def_target_*` + 1 `actor_*` likely, based on the topic).
2. **`../convos/20260514_extraction_harness_brainstorm.md`** — re-read Q1's locked decision and its iter-1 rationale (chunks-by-domain prefix, cell-type clustering emerges within domain clustering for free).

### Phase 2 — Resolve architectural questions (~1-2 hours)

#### Q1 — Chunking taxonomy

Three real candidates emerge from the TSV inspection:

- **(a) Pure first-2-token prefix.** Group by `actor_*`, `def_target_*`, etc. **Problem:** 4 over-sized domains (34, 21, 16, 13) need splitting; many singletons need collapsing into a "misc" bucket. The mechanism for both is open.
- **(b) First-3-token prefix.** Naturally splits `lobbyist_spending_report` into 5 sub-chunks (cadence, available_as, includes, filing_cadence, top-level), `principal_spending_report` into 3. **Tradeoff:** finer-grained but probably *the* right grouping for the bigger domains; for small domains, first-3-token over-splits (every singleton becomes its own chunk).
- **(c) Hybrid: first-3-token where it falls within 5-12, first-2-token otherwise, hand-curated "misc" chunks for orphans.** Algorithmic with a small amount of hand-tuning to land each chunk in the target range. **Tradeoff:** clearer chunks but more code; also requires a deterministic tie-breaker so chunk-IDs stay stable across TSV growth.

Sub-question: should chunks be **named** (e.g., `definitions`, `lobbyist_spending_report.includes`) or **numbered** (`chunk_001`)? The iter-1 precedent (`definitions.md`) uses topic names. Topic names make the brief-writer's preamble lookup trivial. **Lean: topic names**, but stability under TSV growth needs to be designed.

#### Q2 — Hard size bounds + over/under handling

Q1 locked 5-12 as the target. Open:

- **Hard min:** is a 1-row "chunk" allowed? Iter-1 reasoning suggests no (cross-row context disambiguates axes). What about 2-3? Mechanism for collapsing singletons: a `misc_definitions` chunk that aggregates 1-row singletons across unrelated domains (worst case for prompt coherence), or fold each singleton into its closest semantic neighbor (best for coherence, worst for determinism)?
- **Hard max:** is 12 a hard cap, or a soft target with bleed to 13-15 allowed? `lobbyist_reg_form_includes_*` has 13 rows naturally; splitting it loses the "everything you might find on a registration form" framing.
- **Over-sized splitting:** for `lobbyist_spending_report_includes_*` (15 rows), is the right move to (i) split at sub-sub-prefix (`includes_total_*` vs `includes_compensation_*` vs ...) or (ii) split arbitrarily into 7+8?

#### Q3 — Combined-axis row handling

Each of the 5 `legal+practical` rows produces 2 cells with different cell types (e.g., `BinaryCell` at "legal" + `GradedIntCell` at "practical"). Options:

- **(a) Same chunk for both halves.** Brief preamble discusses both axes for the row in one place. Prompt naturally cross-references the two halves ("the binary legal answer constrains what the practical-axis score can be"). Easier for cell-type-mixed chunks.
- **(b) Split by axis.** All "legal" halves go into legal-themed chunks; all "practical" halves into practical-themed chunks. The 5 combined rows get split. Cleaner per-chunk cell-type homogeneity at the cost of cross-axis context.

Note: most practical-axis rows already cluster in `lobbying_search_*`, `lobbying_data_*`, `lobbyist_directory_*` (the portal/website family), which are domain-distinct from the legal-axis statute-shape rows. So option (b) is partially natural — only the 5 combined rows force the issue.

#### Q4 — Output data shape

What does the chunk-grouping function return? Three candidates:

- **(a) `list[list[CompendiumCellSpec]]`** — bare list-of-lists. Brief-writer infers chunk metadata from cell membership. **Tradeoff:** minimal data structure; brief-writer carries the "what is this chunk" knowledge.
- **(b) `list[Chunk]` with `Chunk` as a frozen dataclass.** Fields: `chunk_id: str` (stable identifier), `topic: str` (human-readable), `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_homogeneous: bool`, `notes: str | None`. Brief-writer reads `chunk_id` and looks up its preamble template by ID. **Tradeoff:** clearest contract; tiny dataclass.
- **(c) `dict[str, list[CompendiumCellSpec]]`** keyed by topic. Loses ordering unless we keep insertion order or pair with a separate order list.

The data-flow question: where do the preamble texts live? Three options:
- **In code** as a `CHUNK_PREAMBLES: dict[chunk_id, str]` (compiles into the package).
- **In data files** under `src/lobby_analysis/chunks_v2/preambles/<chunk_id>.md` (matches the iter-1 pattern where preambles were `.md` files).
- **Generated on-the-fly by the brief-writer** from chunk metadata (`topic`, `cell_specs`, `axis`). Highest YAGNI but loses the iter-1 "human-tuned preamble" lever.

This sketch is for the **chunking function only**; preamble storage is for the brief-writer brainstorm. But the chunk output shape constrains what the brief-writer can find later, so the brief-writer Q has to be partially anticipated.

#### Q5 — Stability under TSV growth

Suppose the TSV gains a new row (e.g., a new `lobbyist_spending_report_includes_X` field added by a future rubric update). Open:

- Does the new row get appended to an existing chunk (potentially pushing it over the size cap)?
- Does the chunk re-balance and possibly re-name?
- Does `chunk_id` stay stable so iter-1's `definitions` baseline remains comparable?

If chunk membership is deterministic and stable, then re-running iter-1's `definitions` extraction against the v2 chunks will produce comparable results.

#### Q6 — Where the module lives

Options:

- **(a) `src/lobby_analysis/chunks_v2/`** — parallel to `models_v2/`. Module-level grouping by abstraction layer.
- **(b) Inside `src/lobby_analysis/models_v2/` as `chunks.py`.** Same module as the cell models since the chunks consume the registry. **Tradeoff:** keeps `models_v2/` clean of harness logic.
- **(c) `src/lobby_analysis/harness/` (new).** Anticipating the brief-writer, scorer-prompt, and orchestrator all want to live in a new `harness/` module rather than scattered. **Tradeoff:** more up-front commitment; YAGNI says wait until the third file lands there.

#### Q7 — Function signature

Two surfaces:

- **`build_chunks(registry: dict[tuple[str, str], CompendiumCellSpec]) -> list[Chunk]`** — caller passes the registry. Easier to test (inject test registries).
- **`build_chunks() -> list[Chunk]`** — function loads the registry internally via `build_cell_spec_registry()`. Easier to call.

The cell-models pattern (`build_cell_spec_registry(tsv_path=...)`) takes a default-pathed param. Likely best to mirror: `build_chunks(registry=None)` where `registry=None` triggers internal loading.

### Phase 3 — Capture decisions in the implementation plan (~30 min)

Output: `plans/20260514_chunks_implementation_plan.md` — TDD-shaped. Has Testing Plan section listing every test before any implementation. Pickup-able by an API-launched implementer.

---

## Testing Plan (high-level — implementation plan elaborates)

For the chunk-grouping function:

- **Size-bound tests:** every chunk has between MIN and MAX rows (constants set during brainstorm; likely 5 and 12 with documented exceptions).
- **Coverage tests:** every (row_id, axis) in the 186-cell registry appears in exactly one chunk (assert via set comparison).
- **Determinism tests:** running `build_chunks()` twice produces identical output (same chunk count, same chunk_ids, same ordering).
- **Anchor tests:** the `def_target_*` family lands in a "definitions"-themed chunk (iter-1 continuity).
- **Combined-axis tests:** depending on Q3 outcome, either (a) all 5 combined-axis rows have both halves in the same chunk, OR (b) each half lands in its axis-appropriate chunk.
- **Topic-naming tests:** each chunk's `chunk_id` matches a topic-name pattern (no random integers, no machine-generated noise).
- **Edge case:** registry-stripping test — pass a registry with one row removed; assert the chunking adapts cleanly (or raises a clear error if the row's removal breaks an invariant).

I will NOT write tests that:
- Assert pydantic/dataclass framework behavior (e.g., "test that `tuple` field is `tuple`").
- Test chunk content (the brief-writer's preamble) — that's the brief-writer's domain.
- Mock `build_cell_spec_registry()` — tests run against the **real** registry (or a controlled subset built from the real TSV).

NOTE: All tests written before any implementation, per TDD discipline carried forward from the cell-models plan.

---

## Out of scope for this component

- Brief-writer module (consumes chunks).
- Scorer prompt rewrite (consumes chunks + retrieval bundle).
- Chunk-frame preambles themselves (content; depends on Q4 storage decision but the *function* doesn't ship preambles, just the chunk structure).
- Retrieval agent v2 generalization (parallel component; see separate plan-sketch).
- Anthropic SDK adoption (deferred per handoff; pure-data here).
- `data/` symlink decision (deferred per handoff; pure-data here, no data emission).

---

## Open questions for the brainstorm

The 7 Q's above are the primary axes. Secondary Q's that may surface:

- **Chunk ordering:** alphabetical by `chunk_id`? Topic-clustered (all "definitions" → "registration" → "reporting" → "transparency")? Does the brief-writer care about order, or does it consume chunks in parallel?
- **Persistence:** should the chunk inventory be written to disk (e.g., `compendium/chunks_v2.tsv`) as a separate artifact, parallel to the TSV? Or always-computed at runtime? Parallel-to-TSV gives downstream tools a stable contract; runtime-computed avoids drift.
- **Empty-cell-class handling:** if a row's `expected_cell_class` is `FreeTextCell` (only 2 rows, both `*_cadence_other_specification`), does that influence chunk assignment? Probably no, but flag if anything weird emerges.

---

## What could change

- **Q1's "5-12 rows" range** is a locked decision from the prior brainstorm; the iter-1 anchor is 7. If the brainstorm reveals natural chunks fall outside this comfortably (e.g., `lobbyist_reg_form_includes_*` at 13 wants to stay whole), revisit Q1 — but flag it explicitly rather than silently breaking the prior contract.
- **The combined-axis decision** (Q3) interacts with the brief-writer's preamble style. If the brief-writer brainstorm later changes its approach, the chunking decision may need revisiting.
- **Storage location** (Q6) interacts with whether the brief-writer ends up in the same module. If we land `chunks_v2/` standalone now and later realize brief-writer should live with it, a rename costs little.

---

**Testing Details.** See Testing Plan above. Tests run against the real `CompendiumCellSpec` registry; no mocks. Pure-data; no I/O beyond the TSV load (which already happens in `build_cell_spec_registry()`).

**Implementation Details.**
- All new code in the module location chosen by Q6.
- All new tests in `tests/test_chunks_*.py` (or wherever Q6 lands them).
- No new dependencies in `pyproject.toml`.
- Pydantic 2.x patterns if a `Chunk` dataclass is needed; or plain `@dataclass(frozen=True)` to match `CompendiumCellSpec`.

**Questions.** Q1–Q7 above. Headline: chunking taxonomy (Q1) and combined-axis handling (Q3) are the biggest substantive Q's; output shape (Q4) is the biggest interface Q with downstream consumers.

---

## Why this is the right next component

Per the handoff:

1. Pure-data, easy TDD — matches the cell-models cycle that just landed.
2. Depends only on the frozen `CompendiumCellSpec` registry — no coordination friction with Phase C, `oh-statute-retrieval`, or other fellows.
3. Unblocks brief-writer (which can't be designed without knowing the chunk shape) and informs scorer-prompt rewrite.
4. Iter-1's 7-row chunk-frame is the closest empirical evidence we have on prompt design; this function operationalizes it across all 186 cells.

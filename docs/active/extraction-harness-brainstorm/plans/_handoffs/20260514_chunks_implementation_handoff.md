# Handoff: Implement chunks_v2 module (chunks impl session)

**Date written:** 2026-05-14
**Written by:** the agent that brainstormed-and-planned retrieval (and noticed mid-way that retrieval's plan has a hard dependency on chunks_v2 that does not yet exist).
**For:** the next agent picking up the **chunks implementation** on `extraction-harness-brainstorm`.

## Handoff sentence

Working on `extraction-harness-brainstorm`. The user-locked session strategy is: brainstorm + plan all 4 downstream components here (cells ✓ / chunks ✓ / retrieval ✓ / brief-writer / scorer-prompt) with user-in-loop, then launch implementations as parallel API sub-branches that merge back. **Your sub-branch task is chunks implementation.** The chunks brainstorm + impl plan are both already written and committed; you execute the plan. **Critical:** chunks is a blocking prerequisite for retrieval — retrieval's plan imports from `lobby_analysis.chunks_v2`, which doesn't exist yet. Until chunks ships, retrieval cannot proceed past its Phase 0.

## Where things stand

**Done (don't redo):**

- [`plans/20260514_chunks_plan_sketch.md`](../20260514_chunks_plan_sketch.md) — brainstorm-first agenda (7 Q's)
- [`convos/20260514_chunks_brainstorm.md`](../../convos/20260514_chunks_brainstorm.md) — Q's resolved; full 15-chunk manifest decision locked
- [`plans/20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md) — **your spec.** TDD-shaped, full 15-chunk manifest inlined, verified 181/181 row coverage against the real TSV at plan-write time.
- [`plans/20260514_retrieval_plan_sketch.md`](../20260514_retrieval_plan_sketch.md), [`convos/20260514_retrieval_brainstorm.md`](../../convos/20260514_retrieval_brainstorm.md), [`plans/20260514_retrieval_implementation_plan.md`](../20260514_retrieval_implementation_plan.md) — retrieval brainstorm + plan. **Not your scope this session** — a separate sub-branch picks up retrieval after chunks lands.

**Partially done (left over from a killed parallel session — do NOT touch this session):**

- Local commit `4c49888 retrieval_v2: scaffolding (empty module + anthropic SDK dependency)` — Phase 0 of the retrieval impl plan, executed by a now-killed parallel session. Contents:
  - `pyproject.toml` — adds `anthropic>=0.102` to dependencies
  - `uv.lock` — 170 lines of lockfile updates
  - `src/lobby_analysis/retrieval_v2/` — 6 empty placeholder `.py` files + `docs.md`
  - `tests/fixtures/retrieval_v2/.gitkeep`
- This commit IS on the branch (HEAD) and may or may not be pushed by the time you start. Either way: **leave it alone.** The retrieval implementation will resume from this scaffolding in a separate session once chunks lands. Touching `retrieval_v2/` or `tests/fixtures/retrieval_v2/` in your session adds noise that complicates the retrieval pickup.

**Not done (your job):**

- `src/lobby_analysis/chunks_v2/` — does not exist. Your work creates it per [`plans/20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md).

## What you do

1. **Pre-flight reads:**
   - [`../../../../STATUS.md`](../../../../STATUS.md) — current focus, branch inventory
   - [`../../../../README.md`](../../../../README.md) — project framing
   - [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — branch trajectory; the 2026-05-14 (pickup) entry summarizes the retrieval brainstorm that put this handoff into play
   - [`../20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md) — **your spec; read this end-to-end**
2. **Verify `git status` is clean before starting.** If `retrieval_v2/` shows uncommitted modifications, stop and surface to user — that's not your work.
3. **Execute the chunks impl plan.** Follow TDD discipline: write all tests RED first, then turn green in phases per the plan's structure. Commit per phase per the plan's commit log.
4. **Stay strictly in chunks scope.** Files you touch:
   - `src/lobby_analysis/chunks_v2/` (new)
   - `tests/test_chunks_*.py` (new)
   - `src/lobby_analysis/chunks_v2/docs.md` (new)
   - **NOT** `src/lobby_analysis/retrieval_v2/` (existing scaffolding, not your scope)
   - **NOT** `src/scoring/retrieval_agent_prompt_v2.md` (retrieval's deliverable)
   - **NOT** `pyproject.toml` unless the chunks plan calls for a new dep (it shouldn't — chunks is pure-Python; `anthropic` was added by the retrieval scaffolding commit and you don't need it)
5. **Run finish-convo when done.** Per `skills/finish-convo/SKILL.md`. Add a session entry to RESEARCH_LOG; update STATUS.md's `extraction-harness-brainstorm` row to mark chunks impl complete; commit + push.

## Why retrieval is blocked on chunks

Three places in the retrieval impl plan import from `lobby_analysis.chunks_v2`:

- `src/lobby_analysis/retrieval_v2/tools.py` — `CROSS_REFERENCE_TOOL`'s `chunk_ids_affected.enum` is sourced from `build_chunks()` (coupling test catches drift between chunks manifest and retrieval tool schema)
- `src/lobby_analysis/retrieval_v2/brief_writer.py` — `build_retrieval_brief()` looks up cell rosters by chunk_id via `build_chunks()` for the user-message text
- `tests/test_retrieval_v2_tools.py::test_cross_reference_tool_chunk_ids_enum_matches_chunks_manifest` — load-bearing coupling test

If retrieval impl runs before chunks ships, all three fail with `ImportError`. The killed session (4c49888) hit Phase 0 (which doesn't import yet), then noticed the dependency before Phase 1 (which does).

**The retrieval impl plan has been updated** (commit included with this handoff) with a "Prerequisite" note at the top stating chunks must ship first, and a "Phase 0 may already be done — verify before re-running" note for whoever picks up retrieval next.

## Pickup-context — what the chunks plan delivers

From [`plans/20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md):

- `src/lobby_analysis/chunks_v2/` module with:
  - `Chunk` frozen dataclass (`chunk_id`, `topic`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary`, `notes`)
  - `ChunkDef` manifest-author-time struct
  - Hand-curated `CHUNKS_V2` manifest constant — 15 chunks covering 181/181 rows = 186/186 cells (verified against real TSV; no duplicates)
  - `build_chunks(registry=None) -> list[Chunk]` function with coverage partition invariant
  - Public exports via `__init__.py`
- Test suite enforcing partition invariant, chunk_id uniqueness, snake_case ASCII format, deterministic ordering, manifest↔registry coverage

The 15 chunks (chunk_id list — the retrieval tools enum depends on these names being exact):

1. `lobbying_definitions`
2. `actor_registration_required`
3. `registration_thresholds`
4. `registration_mechanics_and_exemptions`
5. `lobbyist_registration_form_contents`
6. `lobbyist_spending_report`
7. `principal_spending_report`
8. `lobbying_contact_log`
9. `other_lobbyist_filings`
10. `enforcement_and_audits`
11. `search_portal_capabilities`
12. `data_quality_and_access`
13. `disclosure_documents_online`
14. `lobbyist_directory_and_website`
15. `oversight_and_government_subjects`

If the plan's manifest produces a different set of chunk_ids (e.g., a renamed chunk that you spot during implementation), **stop and surface** — retrieval's tool schema enum depends on these exact names, and changing them silently here breaks the coupling test that will fire when retrieval impl runs.

## Multi-committer / multi-session note

This worktree had concurrent activity earlier today — one session (mine) wrote the retrieval plan, another session (killed by user) started the retrieval impl. **Before starting your work**, run `git fetch origin && git status` and verify nothing else is in-flight. If `retrieval_v2/` shows uncommitted changes or another branch is in front of `extraction-harness-brainstorm` on origin, **pause and ask the user** before proceeding.

## Carry-forward links

In session-start order:

1. [`../../../../STATUS.md`](../../../../STATUS.md) — current focus
2. [`../../../../README.md`](../../../../README.md) — project framing
3. [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — branch trajectory
4. [`../20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md) — **your spec**
5. [`../../convos/20260514_chunks_brainstorm.md`](../../convos/20260514_chunks_brainstorm.md) — Q-resolution context for the chunks design decisions
6. [`../../../../compendium/disclosure_side_compendium_items_v2.tsv`](../../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181-row row-freeze contract that the manifest partitions
7. [`../../../../src/lobby_analysis/models_v2/`](../../../../src/lobby_analysis/models_v2/) — `CompendiumCellSpec` definition that `Chunk.cell_specs` is typed by
8. [`../20260514_retrieval_implementation_plan.md`](../20260514_retrieval_implementation_plan.md) — for reference; the downstream consumer of `build_chunks()`. Read the tool schemas in Phase 2 to see how `chunk_ids_affected.enum` consumes the chunks you ship.

## What this handoff does NOT do

- **Does not pre-commit to chunk_id renames or manifest changes.** The plan is authoritative on chunk_ids and row partitioning; if the implementer spots a needed change, surface to user.
- **Does not touch retrieval_v2/.** That's a separate sub-branch's work after chunks lands.
- **Does not push the 4c49888 commit if it's not already pushed.** That's the prior-session author's responsibility / the user's call.

## After chunks finishes (post-your-session)

Two open downstream-component brainstorms remain (brief-writer, scorer-prompt), plus the retrieval implementation sub-branch can resume once chunks is on origin. Brief-writer is the cleaner next brainstorm pick (orthogonal to retrieval; depends only on cells + chunks, both of which now exist). Scorer-prompt should wait until retrieval lands so the brainstorm can anchor on the retrieval bundle shape.

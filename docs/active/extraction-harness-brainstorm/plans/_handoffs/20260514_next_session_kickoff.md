# Handoff: next session kickoff after v2 cell model layer landed

**Date written:** 2026-05-14
**Written by:** the agent that just executed [`../20260514_v2_pydantic_cell_models_implementation_plan.md`](../20260514_v2_pydantic_cell_models_implementation_plan.md) end-to-end.
**For:** the next agent picking up this branch.

## Handoff sentence

Working on `extraction-harness-brainstorm`; the v2 cell model layer landed under strict TDD on 2026-05-14 (10 commits, `62daee7` → `c66d808`; see [`../../convos/20260514_v2_pydantic_cell_models_implementation.md`](../../convos/20260514_v2_pydantic_cell_models_implementation.md) for the full session). The next move is to brainstorm the **chunk-grouping function** as the second TDD-able component, since it's the only downstream piece that depends solely on what already landed (the `CompendiumCellSpec` registry) and unblocks brief-writer + scorer prompt rewrite. Use the same plan-sketch → brainstorm convo → implementation-plan cycle this branch's first two sessions established. Two cross-cutting decisions (data/ symlink, Anthropic SDK adoption) are deferred and need answering when the first LLM-calling component lands — flag them when the brainstorm gets that far rather than answering them now.

## Where things are right now

**On the branch:**
- `src/lobby_analysis/models_v2/` — pure-data typed cell model layer. `CompendiumCell` ABC + 15 concrete subclasses; `CompendiumCellSpec` + 186-entry registry built from the real v2 TSV; `StateVintageExtraction` + `ExtractionRun`; `EvidenceSpan`. Frozen Pydantic 2.x. No LLM dependencies.
- `src/lobby_analysis/compendium_loader.py` — gained `load_v2_compendium_typed() -> list[CompendiumCellSpec]` alongside the existing raw-dict `load_v2_compendium()`. Both unchanged in behavior from each other's perspective.
- `tests/test_models_v2_*.py` + `tests/test_compendium_loader_v2_typed.py` — 68 new tests, all green.
- Full suite: 374 pass / 5 skip / 3 pre-existing `test_pipeline.py` failures (portal-snapshot fixture data not bundled — same as on main; user-approved leaving them).
- v1.1 at `src/lobby_analysis/models/` is **UNTOUCHED**. Phase C retires it when ready.

**Branch sync:** local matches `origin/extraction-harness-brainstorm` at the finish-convo commit; pushed cleanly.

## The 4 unblocked downstream components

From the plan's "Out of scope" list (plus the brainstorm convo's "What this brainstorm produces" section):

| # | Component | Depends on | Independent of |
|---|-----------|-----------|----------------|
| 1 | **Chunk-grouping function** — partition the 186-cell roster into prompt-sized groups (target 5-12 rows per chunk per Q1's hybrid decision) | `CompendiumCellSpec` registry (done) | LLM, retrieval, brief shape |
| 2 | **Cross-reference retrieval agent's v2 generalization** — rewrite `src/scoring/retrieval_agent_prompt.md` (currently v1.2-rubric-shaped with PRI A5-A11 / C0-C3 refs) to be rubric-agnostic | Existing v1 prompt (rewrite, not new build) | Cells, chunks, scorer |
| 3 | **Brief-writer module** — per-chunk extraction brief (text file written to disk per iter-1 pattern; chunk-frame preamble + per-row instructions) | Cells (done) + chunks (component 1) | Retrieval (orthogonal) |
| 4 | **Scorer prompt rewrite** — rubric-agnostic v2-compendium-shaped scorer prompt template | Cells + chunks; informed by retrieval bundle structure | (depends on 1 + 2 ideally) |

### Dependency graph

```
            ┌─ Brief-writer (3) ─┐
            │                    │
Registry ──┤                    ├─→ end-to-end LLM call
            │                    │
            └─ Chunks (1) ───────┘
                                 ↑
                Retrieval (2) ───┘  (orthogonal; can parallelize)

Scorer prompt (4) — prompt-template work; can land before or after the above.
```

### Recommended first pick: **chunk-grouping**

Reasons in order:
1. **Pure-data, no LLM, easy TDD.** Matches the cell-models work that just landed; same shape of session.
2. **Depends only on the registry**, which is done. No coordination friction with Phase C or other fellows.
3. **Unblocks brief-writer and informs scorer prompt** — the most "load-bearing" of the 4 in terms of downstream count.
4. **Iter-1 evidence applies directly.** The 7-row `definitions` chunk hit 93.3% inter-run agreement; chunk-grouping operationalizes that finding. Brainstorm Q1 anchored the 5-12 rows/chunk target.

### Reasonable alternative: **retrieval agent v2 generalization**

If another fellow is on this branch in parallel, the retrieval agent is the cleanest parallel work: no dependency on chunks, no overlap with cell-models territory, and it's a rewrite of existing code (so the design constraint is "what about the v1 prompt was rubric-specific and how does the v2 schema swap those refs").

### Don't pick **brief-writer** or **scorer prompt** first

Brief-writer needs chunks. Scorer prompt rewrite benefits from knowing the retrieval bundle structure (which doesn't crystallize until retrieval generalization lands). Doing either before #1 or #2 is out-of-order work that'll likely need redoing.

## Cycle convention to follow

This branch's first two sessions established a 4-stage pattern. Use the same for the next component:

1. **Plan sketch** (`plans/YYYYMMDD_<component>_plan_sketch.md`) — brainstorm-first agenda; lists architectural questions to resolve; sketches struct shapes. No code yet.
2. **Brainstorm convo** (`convos/YYYYMMDD_<component>_brainstorm.md`) — executes the sketch's agenda. Resolves the architectural Q's via direct user input / `AskUserQuestion`. Produces decisions to lock.
3. **Implementation plan** (`plans/YYYYMMDD_<component>_implementation_plan.md`) — TDD-shaped concrete plan that the implementing agent can execute end-to-end. References the originating brainstorm convo. Has a Testing Plan section listing every test before implementation.
4. **Implementation session** (next `convos/YYYYMMDD_<component>_implementation.md`) — executes the implementation plan under strict TDD per the handoff's "write all tests before any implementation" override. Commits per phase. Ends with finish-convo.

**Do not skip stages.** Process notes in STATUS.md (2026-05-14 v2-promote session) document what happens when agents skip the sketch or skip reading skills — process drift the user has caught and corrected multiple times.

## Two deferred decisions — flag them when they bite

Both are not blockers for the chunk-grouping work, but they'll come up during the LLM-calling components (3 and 4) and need user input then. Don't decide unilaterally.

### 1. `data/` symlink convention

[`RESEARCH_LOG.md`](../../RESEARCH_LOG.md) "Data symlink note" section: "The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share."

**When this matters:** the first LLM-calling component (brief-writer, or whatever runs an extraction and produces gitignored output) needs to decide where its output lands.

**What to do:** when starting on a component that writes gitignored data, ask the user: "We need a `data/` strategy — symlink to shared main-repo data/, or local-only data/ for this worktree? The branch RESEARCH_LOG deferred this."

### 2. Anthropic SDK in `pyproject.toml`

[`convos/20260514_extraction_harness_brainstorm.md`](../../convos/20260514_extraction_harness_brainstorm.md) Finding #2: "Anthropic SDK is NOT in `pyproject.toml`. Dependencies are `beautifulsoup4`, `playwright`, `pydantic`, `requests` only. The orchestrator's module docstring explicitly notes 'no anthropic SDK.' Iter-1 must have worked via Claude Code subagent dispatch (Task tool calling Claude as a subagent), not direct SDK calls. **Decision: the v2 harness inherits this pattern.** Any LLM-calling component writes a brief to disk (per the existing `extraction_brief` module shape) and is dispatched via subagent or external mechanism, not via direct `anthropic.Anthropic()` calls. Adding the SDK is a separate, scoped decision left until/unless there's a clear reason to break the pattern."

**When this matters:** any component that wants to call Claude directly (brief-writer probably doesn't; an end-to-end extraction-runner would).

**What to do:** if the brainstorm session for a component wants to add the SDK, flag it as a separate scoped decision rather than just adding it. Use the `claude-api` skill if/when adoption is approved.

## Carry-forward links (everything the next agent should read)

In session-start order:

1. [`../../STATUS.md`](../../../../STATUS.md) — current focus, this branch's row
2. [`../../README.md`](../../../../README.md) — project framing
3. [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — newest first; the cell-models session's entry is at the top
4. [`../../convos/20260514_v2_pydantic_cell_models_implementation.md`](../../convos/20260514_v2_pydantic_cell_models_implementation.md) — what just landed; "Next session" section
5. [`../../convos/20260514_extraction_harness_brainstorm.md`](../../convos/20260514_extraction_harness_brainstorm.md) — Q0–Q6 architectural decisions; still binding
6. [`../20260514_v2_pydantic_cell_models_implementation_plan.md`](../20260514_v2_pydantic_cell_models_implementation_plan.md) — the plan just executed; its "Out of scope" section names the 4 downstream components
7. [`../20260514_kickoff_plan_sketch.md`](../20260514_kickoff_plan_sketch.md) — the antecedent agenda; shows the plan-sketch shape Dan prefers

## What this handoff does NOT do

- **Does not name a specific brainstorm Q list for chunk-grouping.** That's the kickoff agent's job — Q's emerge from re-reading the v2 TSV's domain-prefix patterns + iter-1's chunk-frame design.
- **Does not commit the user to chunk-grouping first.** The recommendation is principled but you (the next agent) and Dan can pick differently if there's reason to.
- **Does not pre-commit the data/ or SDK decisions** — those are explicit deferrals to be raised at the right moment.

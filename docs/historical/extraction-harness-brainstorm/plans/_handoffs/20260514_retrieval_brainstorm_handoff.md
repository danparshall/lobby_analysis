# Handoff: finish the retrieval brainstorm + implementation plan

**Date written:** 2026-05-14
**Written by:** the agent that brainstormed-and-planned the chunks component end-to-end and started but did not finish the retrieval brainstorm. Session ran short on context.
**For:** the next agent picking up Retrieval on `extraction-harness-brainstorm`.

## Handoff sentence

Working on `extraction-harness-brainstorm`; user's session strategy is to **brainstorm + plan all 4 downstream components in this branch (with user-in-loop), then launch implementations as separate API sub-branches in parallel, merged back to this branch before any eventual main-merge.** The previous session brainstormed-and-planned **chunks** end-to-end (3 files, all committed at the end of this same session — see commit log) and started **retrieval** but stopped mid-Phase-2 (the user wanted to clarify Q1/Q3/Q6 before locking; clarification context is below). Your job: resume the retrieval brainstorm at Phase 2, finish the Q's, write the TDD-shaped implementation plan, run finish-convo. Two more components (brief-writer, scorer-prompt rewrite) remain after retrieval — not in scope for your session unless you have room.

## Where things stand

**Completed and committed in this branch:**

- `docs/active/extraction-harness-brainstorm/plans/20260514_chunks_plan_sketch.md` — chunks brainstorm-first agenda
- `docs/active/extraction-harness-brainstorm/convos/20260514_chunks_brainstorm.md` — all 7 Q's resolved; manifest decision locked
- `docs/active/extraction-harness-brainstorm/plans/20260514_chunks_implementation_plan.md` — TDD-shaped; full 15-chunk manifest inlined; verified 181/181 row coverage against the real TSV at this branch's HEAD on 2026-05-14
- `docs/active/extraction-harness-brainstorm/plans/20260514_retrieval_plan_sketch.md` — retrieval brainstorm-first agenda (7 Q's enumerated)
- `docs/active/extraction-harness-brainstorm/convos/20260514_retrieval_brainstorm.md` — Phase 1 reading complete (v1 prompt rubric-coupling sites identified; legal-vs-practical breakdown per chunk computed); **Phase 2 unresolved**

**Branch sync:** local matches `origin/extraction-harness-brainstorm` after this session's finish-convo push.

## Why retrieval stopped where it did

I batched three Q's (Q1 collapsed-with-Q4-and-Q5 = scope; Q3 = substantive-guidance translation; Q6 = implementation deliverable shape) into a single AskUserQuestion. The user replied "I want to clarify these questions" — i.e., they hadn't decided yet and wanted to discuss. I asked an open "what would you like to clarify" follow-up with 4 hunches I'd been weighing. The user's next message was "give me handoff" — meaning their clarification thinking isn't yet captured in the convo and is on them to surface when you re-engage.

**Read the open-Q's section below before re-asking** — the hunches I surfaced may shift Q1/Q3/Q6's option framings substantially.

## Where to pick up

1. **Read `convos/20260514_retrieval_brainstorm.md` start to finish.** Phase 1 reading + decision-table-by-chunk are done; Phase 2 has only a stub.
2. **Read `plans/20260514_retrieval_plan_sketch.md`** for the 7 Q's enumeration.
3. **Re-engage the user on Q1/Q3/Q6.** They wanted to clarify. The four hunches I floated in the prior session's last message — **but read the cost-multiplier note below first because it materially changes how to weight hunch (i):**
   - **(i) Per-chunk retrieval may be cheap *per call* under prompt caching, but the aggregate is meaningful.** User flagged in the prior session's closing exchange: "even if it's relatively cheap per chunk, I'll have to do this 50x for multiple years, and then multiple times as we adjust the user prompt to make sure we're correctly extracting." Concretely: per-chunk dispatch at 10 legal-axis-bearing chunks × 50 states × ~4 vintages × ~3-5 prompt-tuning iterations = **6,000-10,000 retrieval calls per design cycle**. Per-(state, vintage) dispatch would be ~600-1,000 — an order of magnitude lower. The per-call uncached prefix (preamble + per-row instructions) compounds even when the cached statute is amortized. **This is a real argument *against* per-chunk dispatch and favors per-(state, vintage)** despite the per-call efficiency of caching. Don't lock Q1 on the "caching makes per-chunk cheap" framing alone — surface the aggregate-cost lens explicitly.
   - **(ii) The v1 prompt is identify-only, not fetch-and-bundle.** Output is a JSON of cross-refs; the orchestrator fetches them. Confirm we're keeping that split for v2 (probably yes — orthogonal to the v2 generalization).
   - **(iii) Q3's anchor question may resolve cleaner at the chunk level.** Rather than enumerating cells in the prompt, reference chunks (e.g., "see `actor_registration_required` chunk"). Chunks are stable as the cell roster evolves within a chunk; cells aren't. Could simplify Q3.
   - **(iv) Output schema may not need cell-level affected list.** If retrieval is per-chunk OR per-(state, vintage) with chunk-level routing in the brief, the chunk_id is known from the dispatch context. The output's `cell_ids_affected` field may become redundant; `relevance` (free-text) is enough. This collapses Q2 too. Direction-of-collapse changes depending on Q1 outcome.
4. **Lock Q1, Q3, Q6** (and re-check Q2, Q7 defaults the prior session proposed):
   - **Q2 proposed default:** output schema replaces v1's `rubric_items_affected: ["A5",...]` with `cell_ids_affected: list[tuple[str, str]]`. **Reconsider if hunch (iv) above lands** — the field may not be needed at all under per-chunk dispatch.
   - **Q7 proposed default:** v2 prompt at `src/scoring/retrieval_agent_prompt_v2.md`, parallel to v1 (matches `models_v2/` and `chunks_v2/` parallel-module pattern). Probably uncontroversial.
5. **Write `plans/20260514_retrieval_implementation_plan.md`** — TDD-shaped, API-launchable. Shape depends on Q6 (markdown-only vs prompt+brief-writer vs prompt+brief-writer+parser).
6. **Run finish-convo.** Update RESEARCH_LOG with the retrieval-brainstorm session entry; update STATUS.md (only this branch's row); commit; push.

## Critical context (don't re-derive)

### Prompt caching changes chunk-size economics — relevant for Q1 framing

In the chunks brainstorm, the user surfaced that **the statute bundle goes in the LLM call's `system` block (cached)**, with chunk-specific preamble + per-row instructions in `user` (uncached). This:
- Relaxed chunks' Q1 from "5-12 rows/chunk" to "~30 cap, hard 34" — the iter-1 anchor at 7 rows was sized for uncached prompts.
- Makes per-chunk retrieval calls cheap (cache hit on statute body for the second+ chunk per state-vintage).
- May favor per-chunk retrieval in Q1 here. **Don't carry forward the 5-12 framing in your retrieval brainstorm — it's superseded.**

### The chunks manifest interface

`build_chunks()` returns `list[Chunk]` where `Chunk` has `chunk_id`, `topic`, `cell_specs: tuple[CompendiumCellSpec, ...]`, `axis_summary: "legal" | "practical" | "mixed"`, `notes: str | None`. The 15 chunks and their cell membership are fixed by the manifest at `chunks_v2/manifest.py` (per the impl plan).

The 5 fully-practical chunks (`search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website`) don't need statute retrieval — they're scored against portal screenshots, not statute text. `oversight_and_government_subjects` is mixed (6 practical + 2 legal). The legal-axis-bearing chunks total ~10 of the 15.

**This breakdown is in the retrieval brainstorm convo's Phase 1 section** as a chunk-by-chunk table.

### Iter-1 empirical baseline

The v1 retrieval prompt dispatched against OH 2025 retrieved `OH §311.005` ("person" definition) as a hop-1 cross-ref. The v2 cells that this retrieval informs are: the 11 `actor_*_registration_required` cells (in `actor_registration_required` chunk) + `law_defines_public_entity` + the 3 `public_entity_def_*` cells (in `lobbying_definitions` chunk). The v2 prompt shouldn't regress this behavior.

### Subagent dispatch is the locked invocation pattern

From the kickoff brainstorm's finding #2: **Anthropic SDK is NOT in `pyproject.toml`.** Iter-1 worked via Claude Code subagent dispatch (Task tool). v2 inherits this. So if Q6 lands on "prompt + Python brief-writer," that brief-writer **writes a brief to disk and the orchestrator dispatches via subagent** — it does NOT call `anthropic.Anthropic()`. Adding the SDK is still a separately-scoped decision (see deferred decisions below).

## Two deferred decisions — still deferred, may bite retrieval

From the kickoff handoff (`_handoffs/20260514_next_session_kickoff.md`), still unresolved:

### 1. `data/` symlink convention

When the first LLM-calling component lands gitignored data (retrieval bundles per state-vintage are a likely candidate), decide: symlink to shared main-repo `data/` or local-only worktree `data/`?

**Bites retrieval if:** Q6 lands on "implementation deliverable includes Python code that emits or consumes retrieval bundles." If Q6 is markdown-only or just brief-writer (no bundle persistence), it doesn't bite yet.

**What to do if it bites:** ask the user, "We need a `data/` strategy now — retrieval bundle outputs land where?"

### 2. Anthropic SDK in `pyproject.toml`

If the retrieval implementation deliverable wants to call Claude directly (e.g., a test that runs end-to-end retrieval to verify the prompt), the SDK question lands.

**Probable answer for retrieval specifically:** no SDK needed. The prompt itself is markdown; the brief-writer (if any) just templates strings; the actual LLM call happens via subagent dispatch managed by the orchestrator (separate component). Confirm with user before adding the SDK.

## Cycle convention (same as the prior two components)

1. **Plan sketch (done)** — `plans/20260514_retrieval_plan_sketch.md`. Read this for the 7 Q's enumeration.
2. **Brainstorm convo (in progress)** — `convos/20260514_retrieval_brainstorm.md`. Phase 1 done; resume at Phase 2.
3. **Implementation plan (to write)** — `plans/20260514_retrieval_implementation_plan.md`. TDD-shaped if Q6 = (b) or (c); minimal-test-shaped if (a). Must include a full Testing Plan section listing every test before any implementation.
4. **Implementation session (later)** — done by a separate API-launched implementer on a sub-branch of `extraction-harness-brainstorm`, then merged back. Not in scope for your session.

## Don't skip stages

The user has explicitly enforced the plan-sketch → brainstorm → impl-plan cycle across multiple prior sessions. The chunks session did all three; you do the same for retrieval. **Do not write the implementation plan before the brainstorm is complete** — the impl plan's shape depends on Q6's outcome.

## Don't over-engineer Q6

The v1 prompt is just a markdown file. The TDD-discipline question is: "what's the minimum testable surface that catches regressions?" The user previously chose plan author drafts manifest inline for chunks (i.e., the load-bearing artifact is plan-anchored, not algorithm-derived). They may prefer the same shape here: the plan inlines the v2 markdown rewrite, the impl agent reviews + commits. If Q6 lands on "markdown only + invariant tests," that's still a real TDD pattern (the tests catch PRI-key regressions). Don't push hard on adding a Python brief-writer if the user doesn't see value.

## Carry-forward links

In session-start order:

1. [`../../../../STATUS.md`](../../../../STATUS.md) — current focus
2. [`../../../../README.md`](../../../../README.md) — project framing
3. [`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md) — branch trajectory; newest entry is the brainstorm-and-plan session this handoff is from
4. [`../20260514_retrieval_plan_sketch.md`](../20260514_retrieval_plan_sketch.md) — your agenda
5. [`../../convos/20260514_retrieval_brainstorm.md`](../../convos/20260514_retrieval_brainstorm.md) — Phase 1 reading + Q2 stub
6. [`../20260514_chunks_implementation_plan.md`](../20260514_chunks_implementation_plan.md) — chunks contract that retrieval may consume; read the **manifest section** for the 15 chunk_ids and the legal-vs-practical breakdown
7. [`../../convos/20260514_chunks_brainstorm.md`](../../convos/20260514_chunks_brainstorm.md) — locked decisions for chunks, including prompt-caching architecture surface point (Q1-revised section)
8. [`20260514_next_session_kickoff.md`](20260514_next_session_kickoff.md) — the parent handoff from the cell-models session; still load-bearing for the 2 deferred decisions
9. [`../../../../src/scoring/retrieval_agent_prompt.md`](../../../../src/scoring/retrieval_agent_prompt.md) — v1 prompt, your rewrite source

## What this handoff does NOT do

- **Does not pre-commit you to Q1/Q3/Q6 answers.** The user wanted to clarify; you re-engage on those.
- **Does not write the v2 prompt text.** That's part of the impl plan (in Q6's lands-on-markdown case) or the impl-session work (in Q6 = b/c case).
- **Does not decide the data/ or SDK questions.** Both are explicit deferrals — surface to the user if they bite.

## After retrieval finishes (post-your-session)

Two components remain unbrainstormed:

3. **Brief-writer module** — depends on chunks (done) + cells (done); orthogonal to retrieval. Writes per-chunk extraction briefs to disk.
4. **Scorer prompt rewrite** — depends on cells + chunks + retrieval bundle shape (ideally).

Both follow the same plan-sketch → brainstorm → impl-plan cycle. Brief-writer is the cleaner of the two to do next (more concrete inputs, scorer prompt benefits from knowing retrieval's output shape which lands in your session).

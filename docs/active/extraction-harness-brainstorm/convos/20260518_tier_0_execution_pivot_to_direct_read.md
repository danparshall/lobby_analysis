# 20260518 — Tier-0 execution attempt, four preconditions failed, pivot to direct-read

**Date:** 2026-05-18 (continued into 2026-05-19 UTC)
**Branch:** extraction-harness-brainstorm
**Predecessor convos:** [`20260518_synopsis_walkthrough_and_tier_0_scoping.md`](20260518_synopsis_walkthrough_and_tier_0_scoping.md), [`20260518_tier_0_review_scoring_v2_plan_evidencespan_resolve.md`](20260518_tier_0_review_scoring_v2_plan_evidencespan_resolve.md)
**Plan attempted (now superseded):** [`plans/_tabled/20260518_tier_0_minimal_pipeline.md`](../plans/_tabled/20260518_tier_0_minimal_pipeline.md)
**New plan (replaces above):** [`plans/20260518_tier_0_direct_read_smoke_test.md`](../plans/20260518_tier_0_direct_read_smoke_test.md)

## Summary

Session opened with an instruction to execute Tier-0 end-to-end per the plan. Within the first three implementation steps, four independent preconditions failed in ways that weren't catchable from reading the plan alone — they only surfaced under execution. Surfaced each, paused, asked. After the third failure the user pushed back on whether the plan's architecture was right at all, and we walked through what retrieval-then-score actually buys us. Conclusion: we don't have empirical evidence the two-call architecture is necessary; a single direct-read call against the cached statute may suffice. Session pivoted to: (1) supersede the original Tier-0 plan, (2) write a new plan for a direct-read smoke test with cross-model (Claude + GPT) side-by-side as the YAGNI primary, (3) leave Citations+retrieval+bundle-expansion in the drawer as the escape hatch for the case where direct-read produces too many unscoreable cells. No code shipped this session — pivot is fully captured in docs for the next agent.

## What went wrong with the original plan

Four preconditions failed at execution time. Each is a "plan was written from a confident-sounding model rather than from `ls` and `grep`" pattern.

1. **Wrong data paths.** Plan said `~/data/statutes/OH/2015/`; actual canonical layout is `~/data/lobby_analysis/statutes/OH/<vintage>/`. Two facts wrong (parent dir and vintage availability). OH 2015 was not on Dans-MacBook-Air; OH 2010 and OH 2025 are. User authorized retarget to OH 2025 (committed as `2b9528c` — plan retarget + path correction). The retarget is *durable* — the Tier-0 plan now references real paths/vintages — but it doesn't recover the session from later failures.

2. **No `ANTHROPIC_API_KEY` on this machine.** Plan prerequisite: live API calls (~$1–2/run). Reality: `retrieval_v2/docs.md:78` already noted the laptop is keyless ("⏸ deferred to desktop"). Plan named a prereq that the branch's own docs contradicted.

3. **`scoring_v2/` module does not exist as code.** Plan called for "a thin wiring script that dispatches the scorer call ... using the scorer prompt + tool schemas inlined in the scoring_v2 implementation plan." Reality: only the 1380-line impl plan exists. No scorer prompt on disk, no `record_cell` tool implementation, no parser for the scorer response. "Thin wiring script" understates the work by ~10×. Tier 0 as specified is "first implementation of scoring_v2" wearing a smoke-test costume.

4. **Circular import surfaced under cold load.** `chunks_v2 → models_v2 → retrieval_v2.tools → chunks_v2` is a four-node cycle. Tests don't catch it (they import lazily inside test functions). `uv run python -c "from lobby_analysis.chunks_v2 import build_chunks"` fails with `ImportError`. Plan Step 2 ("EvidenceSpan migration in `0979779` — single tight commit, 480 tests pass") declared the migration done; the migration introduced (or surfaced) a structural cycle that the tests' import-laziness hides. The plan's prior draft had warned "deletion requires a full import-graph audit; defer" and then the audit didn't happen.

**Pattern across all four:** the plan over-claimed executability. It read as confidently runnable but actually required unbuilt scoring_v2 code, API keys not on this machine, data at paths that don't exist, and was gated on a cycle introduced two commits earlier.

## Architectural pivot — why direct-read first

After the third failure, user asked whether the plan itself was broken. Walked through what the two-call retrieval+score architecture actually buys us:

- **Premise of retrieval+score:** statutes cross-reference other sections; a scorer reading just the core chapter would emit "unscoreable" for any question whose answer lives in a referenced-but-not-bundled section (e.g., `§101.99` → "penalties under §307.99"). Retrieval finds the cross-references; orchestrator fetches them; scorer reads the expanded bundle.

- **Empirical status of that premise:** untested. The brainstorm Q1 locked chunks-as-dispatch-unit and the retrieval+score sequence, but no run has ever measured how often direct-read would produce unscoreable cells on a real chunk. The architecture was designed against a worry, not an observation.

- **What direct-read actually looks like:** single API call. System prompt = task instructions + the full statute text concatenated (cached via `cache_control: ephemeral`). User message per chunk = chunk-specific questions ("answer these 4 cells via `record_cell`"). Tools = `record_cell` + `record_unscoreable_cell`. No Citations API, no retrieval pass, no orchestrator. ~150–200 lines of inline script.

- **Cost math:** statute ≈ 50K tokens (~$0.15 first call at Opus 4.7 pricing); cached-read on subsequent chunks (~10%, ~$0.015 each). 15 chunks ≈ $0.30 total. Same shape on GPT-5.2.

- **Where direct-read might fail:** unscoreable cells caused by out-of-bundle cross-references. That's the empirical signal. If direct-read produces >N unscoreable cells per chunk for cross-reference reasons, retrieval+bundle-expansion becomes load-bearing — *as an escape hatch, not as upfront scaffolding*.

- **Provenance without Citations API.** Scorer is instructed to cite the specific statute section supporting each answer (free-text, e.g., "§101.85(B)(2)") and provide a 1-sentence justification. A downstream verifier agent (Phase 2, not tonight) reads the cited section and rules whether it actually supports the claim. Machine-checkable provenance without the Citations API plumbing in the primary call. `CompendiumCell.provenance` stays defaulted to `()` for now; verifier output gets a separate model when/if we build it.

- **Cross-model verification.** User has both Anthropic and OpenAI keys. Run direct-read on Claude *and* GPT independently; compare outputs cell-by-cell. Adversarial-evaluation framing in the prompt ("your response will be independently verified by another model reading the cited section") is literal, not a prompt-engineering trick. Phase 1 is side-by-side comparison. Phase 2 (later) is cross-model verification.

## EvidenceSpan relocation — why still load-bearing

Even though direct-read drops Citations API for the primary call, the import cycle still bites any cold-load entry-point that touches `chunks_v2`. `models_v2/cells.py:23` imports `retrieval_v2.EvidenceSpan` for the `CompendiumCell.provenance` type annotation (defaulted to `()`, but the annotation needs to resolve). The annotation triggers `retrieval_v2/__init__.py`, which loads `tools.py`, which imports `chunks_v2.build_chunks` — cycle.

Right fix: `EvidenceSpan` is the Citations-API span primitive used (or potentially used) by both cells (`models_v2`) and cross-references (`retrieval_v2`). It's foundational, not retrieval-specific. The 0979779 commit consolidated on the right *shape* (Citations-API span, not statute-semantic) but located it in the wrong module. Relocate to `models_v2/citations.py` (or similar foundational location); update `models_v2/cells.py` and `retrieval_v2/models.py` to import from there. Cycle dissolves structurally.

Lazy imports (which I partially shipped this session before reverting) treat the symptom; relocation fixes the structure.

## Decisions Made

- **Tier 0 (original plan) is superseded.** The plan as written is not executable on this machine without ~10× the work it claimed. Moved to `plans/_tabled/` with a SUPERSEDED banner per the "never delete analytical work" rule. Kept intact for provenance — the path/vintage retarget commit `2b9528c` lives on top of it as a record of what was tried.

- **New plan: direct-read smoke test with cross-model side-by-side.** Written this session, lives at `plans/20260518_tier_0_direct_read_smoke_test.md`. Self-contained for the next agent: EvidenceSpan relocation as prerequisite, `uv add openai` as prerequisite, single-call dual-model script, save outputs, hand-eyeball comparison. Citations API + retrieval flagged as escape hatch with an empirical decision criterion.

- **Provenance via free-text citation + future verifier.** `record_cell` tool gets `cited_section` (free-text section reference) and `justification` (1-sentence prose) fields. `CompendiumCell.provenance` stays defaulted to `()` — Citations-API EvidenceSpans are not populated by direct-read; we keep the field for the escape-hatch path. Verifier is a Phase 2 component, separate plan.

- **Cross-model framing is literal.** User has both keys. Prompt language: "your response will be independently verified by another model reading the cited section." True statement once we run both models, not a prompt-engineering trick masquerading as deception.

- **No code ships this session.** Pivot is captured in docs only. Tonight's deliverable is: superseded old plan + new plan + this convo + RESEARCH_LOG/STATUS updates. Next agent implements off the new plan.

## Findings worth carrying forward (beyond this branch)

- **The plan was written under sycophantic load.** Confident-sounding executability that didn't survive contact with the filesystem or the import graph. Mitigation for future plan-writing: every prerequisite stated in a plan should be `ls`'d or `grep`'d at plan-write time, not asserted from memory. The plan's own "Prerequisites" section was the right place to catch all four of tonight's failures.

- **0979779's "tight single commit" framing hid a real bug.** The migration *was* tight in line-count, but it introduced a structural cycle that the test suite couldn't catch because tests import lazily inside functions. "Tests pass" is necessary but not sufficient for migration safety when the import graph changes. For future schema migrations: add a cold-load smoke test (`python -c "from <package_root> import <foundational_module>"`) to verify the import graph still works from a fresh interpreter.

- **YAGNI applies to architecture, not just to features.** The brainstorm Q1 locked retrieval+score-as-two-calls as an architectural choice without empirical grounding. Direct-read is the YAGNI default; the multi-call architecture should require evidence of need (high unscoreable-rate) to ship.

## Results

(No analysis outputs this session — the deliverables are the new plan doc + this convo + the superseding move on the old plan.)

## Open Questions

- **Where exactly does `EvidenceSpan` live after relocation?** Two candidates: `src/lobby_analysis/models_v2/citations.py` (puts it in the foundational module where it conceptually belongs — provenance primitive shared by both cells and cross-refs) or a new top-level `src/lobby_analysis/citations.py` (avoids putting cross-module primitives inside `models_v2`'s tree). New plan proposes the former; next agent's call if a reason surfaces for the latter.

- **What verifier model in Phase 2?** Claude verifies GPT and vice versa, or one designated verifier (probably opposite-shop from the scorer)? Not blocking — Phase 2 hasn't been planned yet.

- **`record_cell` schema parity across SDKs.** Anthropic uses `input_schema` (JSON Schema); OpenAI uses `function.parameters` (JSON Schema with different wrapper). New plan proposes a shared JSON Schema dict with two thin SDK adapters; next agent should empirically verify the two wrappers don't impose incompatible field constraints on tool definitions.

- **Cost ceiling for the smoke run.** Original plan said $5; new plan keeps that. With dual-model (Claude + GPT) on one chunk, real cost is ≈ $0.30 + $0.30 ≈ $0.60. Plenty of headroom.

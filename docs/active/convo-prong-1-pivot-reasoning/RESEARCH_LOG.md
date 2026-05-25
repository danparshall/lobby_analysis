# Research Log: convo-prong-1-pivot-reasoning

Created: 2026-05-24
Purpose: Thin holding branch for a single convo doc that captures the reasoning trajectory of the 2026-05-24 session — a meta-session that ran on `main` (no associated research branch), produced the Prong 1 pause + gather-first / v2.2 pivot, and landed via 5 PRs (#22–#26) directly on `main`.

This branch exists only as a place to host the convo doc — there's no code or further research planned here. The cleanest long-term home for the convo is probably `docs/historical/extraction-harness-brainstorm/convos/` (since that's the branch whose Tier-1/Tier-2 work most directly drove the pivot), via a follow-up integration if/when worthwhile. The user gets to decide.

> **Predecessor:** `main` at `28121e6` (post-PR-#26 merge — the pivot doc PR).
> **Substantive output:** lives on `main` already (PRs #22–#26).
> **This branch:** convo doc only.

---

## Sessions

(Newest first.)

### 2026-05-24 — Prong 1 pause + gather-first / v2.2 pivot reasoning

Convo: [`convos/20260524_prong_1_pivot_reasoning.md`](convos/20260524_prong_1_pivot_reasoning.md)

**Topics explored:**
- Session bootstrap: clean-worktrees pass on accumulated worktrees (9 → 4 active after this session's archives); identified `state-codes-inspect` as having 26 unpushed commits + no remote (pushed)
- Tier-1/Tier-2 verdict from `extraction-harness-brainstorm`: blockers A/B/C cleared in code; remaining open: enum-pinning + abstention-calibration
- Deep technical walk on OH 2025 qualitative-trigger statute through 5 rubric projections; surfaced mutually-incompatible encoding conventions for the 3 threshold cells
- User pushback sequence forced me from "fix the encoding" → "the schema can't represent reality" → "gather-first / v2.2"
- Caught my own Goodhart anti-pattern (proposed schema discriminator was exactly what RESEARCH_ARC Risk #2 warns against)

**Provisional findings:**
- LLMs CAN read state lobbying statutes (Tier-1: σ_stable 85.7% Claude / 73.8% GPT on OH 2025 legal axis, $2.94, no hallucinated citations)
- v2.1 typed-cell schema CANNOT yet faithfully represent statute reality on qualitative-trigger states (Tier-2 Step D: "model right, schema can't represent the answer")
- 8 rubric projections have mutually-incompatible encoding conventions; the right fix is projection-side substantive judgment, not extractor-side convention choice
- PRI 2010's binary actor-cell shape sidesteps the whole threshold-encoding mess

**Results / Provenance:**
- PR #22 (v2-promote archive) — merged `0a14113`
- PR #23 (phase-c-projection-tdd merge) — merged `c65e5ac`
- PR #24 (extraction-harness-brainstorm merge) — merged `7687d31`
- PR #25 (oh-statute-retrieval merge) — merged `55fe8a6`
- PR #26 (Prong 1 pause: archive all 3 + README/RESEARCH_ARC/STATUS pivot docs) — merged `28121e6`

**Next steps:**
- Pivot is now landed and discoverable from session-start reads (README "Research question", RESEARCH_ARC "Status: Prong 1 paused", STATUS Current Focus 2026-05-24 update)
- Open architectural question for next Prong 1 chapter: gather-first branch naming + chunking strategy + boundary between "all 50" and "5-8 priority states"
- Product focus shifts to Prong 2 (portal extraction) — not addressed in this session

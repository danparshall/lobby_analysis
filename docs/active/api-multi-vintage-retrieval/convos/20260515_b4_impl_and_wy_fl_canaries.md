# B4 implementation + WY/FL canaries (Chunks 1–3 of handoff)

**Date:** 2026-05-15
**Branch:** `api-multi-vintage-retrieval`
**Worktree:** `.worktrees/api-vintage`
**Session pickup:** `26894aa` (handoff doc, 2 doc-only commits past `dcdb04d` RED checkpoint).
**Session end commit:** `5b76fd3` (Chunk 3 docs + push).

## Summary

This session picked up [`plans/20260515_b4_handoff_to_fresh_agent.md`](../plans/20260515_b4_handoff_to_fresh_agent.md) cold, with 5 RED B4 tests waiting on implementation and a `$1.00`-capped canary script ready for live spend. The handoff anticipated 30–60 min for the implementation chunk and ~$0.10 of canary spend across FL+WY; both came in on or under those estimates.

Chunk 1 (B4 orchestrator GREEN) landed on first compile — `discover_urls_for_pair_three_pass` + `ChosenChapter` + `Pass1Pass2Pass3Result` + serialize/deserialize + batch surface, all in one Edit, all 5 RED tests → GREEN, full 44-test suite passing. B3PW's 9 tests untouched. Some code duplication between two-pass and three-pass kept per the plan's "readability > DRY" guidance.

Chunk 2 (canary-script extension) added `CANARY_MODE=B4` and `CANARY_MODE=B4_10PAIR` modes; wired NY/TX/OH into `SINGLE_PAIR_TARGETS` for Chunk 4; passes the production pass-2 prompt as both `pass2_template` and `pass3_template` (Rule 6 is depth-agnostic; PASS_2/PASS_3 markers are test-only). Script stays gitignored.

Chunk 3 (re-canary FL + WY) closed the chapter-TOC ceiling exactly as the plan predicted. **WY 2010: 1/1 GT-hit, $0.024, 31.7s** (pass-3 correctly skipped — chapter7.html children-TSV is empty; orchestrator emits pass-2 ProposedURL with role + rationale intact, regression-preserving B3PW's WY 1/1). **FL 2010: 6/6 GT-hit, $0.087, 67.1s** (pass-3 fired on chapter11 + chapter112; all 6 Ch.11 GT sections hit; pass-3 on chapter112 returned `PARTIII.html` — a sub-chapter TOC, not a section leaf). Combined: **7/7 = 100% recall, $0.111 spend, zero anti-bot incidents** across 8 Playwright fetches.

Session paused before Chunk 4 by user request to allow a fresh session to pick up at NY/TX/OH single-pairs. The FL Ch.112 PARTIII observation is the one piece of evidence not in the existing handoff plan that matters going forward — flagged in the results doc + RESEARCH_LOG since OH 2010's 30 GT URLs live at section-leaf depth and may surface the same partial-TOC pattern.

## Topics Explored

- **B4 plan adaptive-pass-3 semantics:** pass-3 fires iff `_build_justia_link_tsv(chapter_html, chapter_url)` returns non-empty. Empty TSV → chapter IS the leaf → orchestrator emits pass-2 ProposedURL with role + rationale intact. Non-empty TSV → pass-3 with chapter rationale + children TSV.
- **Role-preservation pattern for the skipped-pass-3 case:** the orchestrator carries a `chapter_proposals: list[tuple[ChosenChapter, ProposedURL]]` sidetable through pass-2, so when the children-probe returns empty, the *original* pass-2 ProposedURL (carrying its role tag) is what gets added to `parsed_urls`. ChosenChapter's `{url, rationale}` shape stays identical to ChosenTitle per the plan.
- **Production prompt-reuse for pass-3** — canary script reads `api_seed_discovery_pass2_prompt.md` once and passes it as both `pass2_template` and `pass3_template`. Real model never sees PASS_2/PASS_3 markers; those are minimal-template-only test discriminators.
- **Canary script extension surface:** B3PW modes kept verbatim; B4 functions added as parallel implementations rather than refactoring shared print/diff logic out (plan's "readability > DRY"). Modes added: `B4` (default), `B4_10PAIR`. NY/TX/OH entries added to `SINGLE_PAIR_TARGETS`.
- **WY 2010 canary trajectory:** state-year-index → pass-1 picks `Title28/Title28.html` ("Wyoming's lobbying registration and disclosure requirements... codified under Title 28") → pass-2 picks `Title28/chapter7.html` → children-probe finds only a back-nav link to the year index (outside the chapter7 namespace) → empty TSV → pass-3 skipped → final URL = chapter7.html.
- **FL 2010 canary trajectory:** state-year-index → pass-1 picks Title III + Title X (multi-pick from B3PW canary fixes carrying through) → pass-2 picks chapter11 + chapter112 → children-probe finds 3 sections under each → pass-3 fires twice → Ch.11 pass-3 returns 7 URLs (6 GT-hit + 11_044 support_chapter); Ch.112 pass-3 returns 1 URL (PARTIII.html, a sub-chapter TOC).
- **Chapter-TOC partial-depth issue (FL Ch.112):** Florida's Ch.112 has a 4th structural layer (Title → Chapter → Part → Section), so pass-3 against the chapter-page TSV picks the Part-level TOC URL rather than drilling all the way to section leaves. Doesn't penalize FL on this canary (no Ch.112 GT for 2010) but signals a recursion-might-be-needed pattern relevant to Chunk 4's OH 2010 evaluation.

## Provisional Findings

- **B4 orchestrator works on first compile.** No defects surfaced during implementation; the 5 RED tests pinned the surface precisely enough that the GREEN path was a single Edit.
- **B4 closes B3PW's chapter-TOC ceiling without prompt tuning.** The model's role-tagging on FL Ch.11 sections (`core_chapter` for lobbying statutes, `support_chapter` for cross-references like 11_044) shows it's correctly applying Rule 6 at chapter-page-snapshot depth. The plan's "Rule 6 is depth-agnostic" hypothesis held.
- **WY-style chapter-leaf states remain 1/1** under B4 — the adaptive children-probe doesn't add false positives or extra LLM calls when the chapter is the answer.
- **Combined cost-per-pair: $0.056 mean** ($0.024 chapter-leaf + $0.087 multi-chapter-TOC). Projects 350-pair fan-out to ~$19.5 (vs the plan's ~$21 estimate). No new pricing surprises.
- **Zero anti-bot incidents** across 8 Playwright fetches × 2 canaries. The `_is_cloudflare_challenge` heuristic in the canary script never fired.
- **Wall time slight overage** but within order of magnitude: WY 31.7s vs plan's ~25s estimate; FL 67.1s vs plan's ~38s + ~20s margin = ~58s estimate. Small, not concerning.
- **Pass-3 precision is 6/8 on FL** (75%) — 11_044 (support_chapter, intra-chapter cross-reference) + PARTIII.html (sub-TOC) are the two non-GT picks. The plan's gate is recall (GT-hit rate, 6/6 = 100%), so this is within target; whether downstream extraction wants the extras is an extraction-side decision.

## Decisions Made

- **Chunk 1 committed standalone** (`3b124d9`) — orchestrator + tests GREEN before any canary spend; clean rollback point if a canary surfaces an unrecoverable defect.
- **Chunk 3 docs committed together** (`5b76fd3`) — results doc + RESEARCH_LOG + STATUS in one commit, with the canary script staying as untracked-by-design.
- **No code refactor.** B3PW's `discover_urls_for_pair_two_pass` + 9 tests preserved unchanged. Some code duplication between the two-pass and three-pass orchestrators is acceptable per the plan.
- **Results doc continues `20260514_b3pw_pilot_canaries.md`'s structure** (TL;DR + per-canary writeup + open observations + appendix) — per the handoff plan's explicit instruction to append Chunk 4's NY/TX/OH outcomes to the same file rather than starting a new one.
- **Branch pushed to `origin/api-multi-vintage-retrieval` at `5b76fd3`** for handoff safety. Local commits: `3b124d9` (orchestrator) + `5b76fd3` (Chunk 3 docs).

## Results

- [`results/20260515_b4_pilot_canaries.md`](../results/20260515_b4_pilot_canaries.md) — per-canary writeups for WY 2010 + FL 2010; TL;DR, metrics tables, trajectory, open observations (PARTIII), appendix with exact commands, handoff section for Chunk 4.

## Open Questions

- **Does Ch.112's PARTIII-style sub-TOC generalize to OH 2010?** OH 2010's 30 GT URLs live at section-leaf depth under `title1/chapter101/` and `chapter121/`. If OH chapters are also Part-split (or similarly multi-layered), pass-3 may stop at an intermediate level. Chunk 4's OH canary is the test.
- **Should the orchestrator recurse beyond pass-3?** Plan explicitly defers (Phase 7 / out-of-scope). Current behavior: pass-3 is the final pass; partial-TOC URLs in its output get added to `parsed_urls` and downstream extraction handles them. Reconsider only if multiple states' GT lives below pass-3 depth.
- **Pass-3 precision tuning** — 6/8 on FL is plan-acceptable (gate is recall). If precision becomes load-bearing for downstream extraction cost, pass-3 prompt's Rule 4 filtering could be tightened, but that's optimization not correction.

## Next Steps

- **Chunk 4** (next session): run B4 against NY 2010, TX 2009, OH 2010. NY/TX target 1/1, OH target ≥25/30. Targets already wired into `SINGLE_PAIR_TARGETS`. Append outcomes to `results/20260515_b4_pilot_canaries.md`. Projected spend ~$0.20.
- **Chunk 5** (gated): 10-pair B4 canary only if Chunks 3+4 collectively show ≥80% aggregate GT-hit + 0 anti-bot across CA/TX/NY/WI/WY. Currently 1 of 5 pilots done (WY pass; FL is sanity-only). NY/TX/WI need Chunk 4 + CA needs a baseline before the gate evaluates. Projected spend ~$0.70 if it fires.
- **Chunk 6**: final RESEARCH_LOG + STATUS wrap-up commit + push at end-of-Chunk-5.

## Provenance

This convo was checkpointed via the finish-convo flow at session pause (before Chunk 4) at user request. Implementation commits: `3b124d9` (B4 orchestrator GREEN), `5b76fd3` (Chunk 3 docs). The canary script (`scripts/canary_discovery.py`) is gitignored-by-design and stays as an untracked modification in the worktree with the B4 mode extensions ready for the next agent.

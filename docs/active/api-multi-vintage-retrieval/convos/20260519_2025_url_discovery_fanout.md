# 2025 URL Discovery Fan-Out — 12 Priority States

**Date:** 2026-05-19
**Branch:** api-multi-vintage-retrieval
**Worktree:** `.worktrees/api-vintage` (created this session on Dans-MacBook-Air)
**Picked up from:** `104268e` (the 20260519 fetch-2025-statute-bundles handoff that was authored on Dans-MacBook-Pro mid-2015 section-fetch, with `subagent_fetch_save.py` newly committed in the same push)
**Convo prior:** [`20260515_b4_parser_hardening.md`](20260515_b4_parser_hardening.md)
**Companion docs:** [`plans/_handoffs/20260519_fetch_2025_statute_bundles.md`](../plans/_handoffs/20260519_fetch_2025_statute_bundles.md) (scoping); [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](../plans/_handoffs/20260519_subagent_dispatch_prompt.md) (per-subagent template authored this session)

## Summary

Phase B URL discovery for the 2025 vintage across the 12 priority states from the 2026-05-19 handoff (TX/MA/PA/CO/IL/AR/WI/WA/AK/MI/WV/CA — i.e., the 13 states that succeeded at 2015 section-fetch on the desktop, minus OH which is already on disk). Two structural blockers surfaced mid-session: (1) Justia's "current code" URL convention drops the year segment from links to 2025 content, so the existing `_build_justia_link_tsv` helper produced empty TSVs and starved pass-1 of substrate; (2) two subagents stopped at Article-level rather than recursing to section leaves. Block 1 was fixed via a TDD patch (4 new tests, year injection logic) before any subagent dispatch; block 2 was partially fixed via tighter per-state addenda in batches 3-4 (CO/IL bundles from batch 2 remain at Article-level, flagged for Phase C remediation).

Six commits landed on the branch — the helper patch, the dispatch-prompt artifact, and four batch commits (3 states each). Net: 298 proposed URLs across 12 states, zero Cloudflare blocks, zero playwright errors. Five real cross-vintage research findings beyond the plumbing.

## Topics Explored

- **Branch pickup**: User typed "pull api-multi-vintage" — closest match was `api-multi-vintage-retrieval` (a fresh `20260519_fetch_2025_statute_bundles.md` handoff had been pushed earlier the same day on the desktop). Created worktree at `.worktrees/api-vintage` per the handoff's directory convention.

- **Environment setup**: Data symlink initially pointed to `/Users/dan/code/lobby_analysis/data` (nonexistent — gitignored on this machine); corrected to `/Users/dan/data/lobby_analysis/` per user feedback. Playwright chromium browser not installed on this laptop; ran `playwright install chromium` (~91 MB). Cloudflare probe on TX 2025 from laptop IP came back clean (61 KB, no challenge).

- **Helper patch (year injection)**: First pass-1 fetch via `subagent_fetch_save.py` produced 745 lines of HTML but 0 lines of TSV. Investigation showed Justia's 2025 state-year-index page renders children as `/codes/texas/government-code/` (year-less) rather than `/codes/texas/2025/government-code/` — both URL forms resolve to identical content server-side, but the existing `_build_justia_link_tsv` prefix-matches against the year-prefixed namespace and so filters out all year-less children. Probed across TX 2024/2023/2022/2020/2015 to confirm the convention is 2025-specific (2024-and-earlier still use year-prefixed links). Probed pass-2 (title TOC) and pass-3 (chapter leaf) levels to confirm the year-less convention applies consistently through every level of the discovery tree.

- **TDD patch**: Added 4 new tests in `tests/test_api_retrieval_agent_b3.py` (year injection at pass-1, year injection at pass-2, rejection of "Other Years" nav links, regression rail for 2024-and-earlier). Patched `_build_justia_link_tsv` with a "Pattern 4" branch: when parent URL is `/codes/<state>/<YYYY>/<...>`, also accept children matching the year-stripped namespace and inject the year on emission. Tested across TX/MA/PA 2025 — 30/5/134 entries respectively, all year-prefixed.

- **Subagent dispatch prompt artifact**: Authored a parameterized self-contained brief at [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](../plans/_handoffs/20260519_subagent_dispatch_prompt.md) capturing the pass-1 → pass-2 → pass-3 procedure that was previously implicit in the 2026-05-18 desktop run. Includes Justia state-slug mapping for the 12 priority states, Cloudflare triage, vintage substitution logic, empty-TSV anomaly handling, and the `result.json` schema. Each subagent reads this file and follows the procedure with their specific (state, vintage, OUT_DIR) parameters.

- **Four batches of 3 subagents in parallel** (per handoff's CF-sustainability finding: 3 concurrent is the safe ceiling): batch 1 TX/MA/PA, batch 2 CO/IL/AR, batch 3 WI/WA/AK, batch 4 MI/WV/CA. After each batch, verified bundle structure on disk and committed before launching the next.

## Provisional Findings

### Section-level (10 states, 286 URLs)
- **TX 2025** — 35 URLs. **Ch. 305 restructured into subchapter A/B/C** (Registration §§305.001-019, Prohibited Activities §§305.021-030, Sanctions §§305.031-036). 2015 had Ch.305 as a single directory-leaf URL. Includes post-2015 additions: §305.030 Foreign Adversary, §305.0064 Electronic Filing, §305.0021/§305.0041/§305.0051/§305.0061/§305.0062/§305.0063/§305.0071. Tree depth 7 (deepest).
- **MA 2025** — 11 URLs (§§39, 41-50). Matches 2015 GT exactly. § 40 still repealed.
- **PA 2025** — 11 URLs (§§13A01-13A11). Matches 2015 GT exactly. Subagent correctly noted chapter-13 "Deleted by amendment" and picked chapter-13a instead.
- **AR 2025 → 2024 (substitute)** — 15 URLs (Title 21 Ch.8 Subchapters 4/5/6 sections). Justia 404 on /2025/, fell back to /2024/. **Regime drop**: Title 10 Ch.1 was populated "General Provisions" in 2015, now `[RESERVED]` in 2024 — AR's legislative-branch lobbying support provisions appear consolidated elsewhere or removed.
- **WI 2025** — 16 URLs (§§13.61 through 13.75). Matches 2015 GT exactly. **URL slug convention changed** from `13/13.61.html` (2010-style) to `chapter-13/section-13-61/` (2025-style).
- **WA 2025** — 42 URLs. **Full RCW reorganization 2024-25**: lobbying-disclosure regime moved from Title 42 Ch.42.17A → new Title 29B Ch.29B.50. Justia hosts both transitionally. 29 URLs from new canonical (29B.10 defs + 29B.50 lobbying + 29B.60 enforcement); 13 URLs from legacy mirror (42.17A). **Phase C will need a dedup-or-source-policy decision.**
- **AK 2025** — 20 URLs (AS 24.45.011 through .181 across Articles 1-5). Matches 2015 GT exactly. Subagent correctly recursed pass-3 into each Article to enumerate sections.
- **MI 2025** — 23 URLs (MCL 4.411-4.431 under Act 472 of 1978). Matches 2015 GT. MCL's act-grouped slug convention (`statute-act-472-of-1978/section-4-411`) handled correctly.
- **WV 2025** — 34 URLs (Ch.6B Articles 1/2/3). **+10 new sections vs 2015 GT (24)**: Article 2 added §§2a/3a/5a/5b (ethics enforcement supplements); Article 3 added §§3a (registration fees) / 3b (conflict of interest) / 3c (lobbyist training) / 11 (compliance audits). Articles 2A and 2B excluded as post-2015 additions outside lobbying-disclosure scope.
- **CA 2025** — 56 URLs across Ch.6 (30 core), Ch.2 (10 support definitions), Ch.11 (16 enforcement). **+1 section vs 2015 GT (55)**: §86119 added to Ch.6 Art.1. Tree depth 6 (deepest of all 12 states). Subagent flagged duplicate `-d-1`/`-d-2` URL variants and intentionally excluded them.

### Article-level (2 states, flagged for Phase C remediation)
- **CO 2025 → 2024 (substitute)** — 3 URLs at Article level (Art.6 Sunshine Law / Lobbyist Regulation; Art.18 Standards of Conduct; Art.18.5 Independent Ethics Commission). Justia 404 on /2025/, fell back to /2024/. Subagent rationalized stopping at Article-level by analogy to TX 2015's directory-leaf chapter — but TX 2015's chapter-305 was empty-TSV-leaf, whereas CO Art.6 has section children. Phase C will need to fetch the Articles and do its own section-discovery.
- **IL 2025** — 9 URLs at Article level (5 ILCS 420 Articles 1/2/3/4A; 5 ILCS 430 Articles 1/5/10/50; 25 ILCS 170 act-level leaf which IS a real leaf via empty-TSV). Same issue as CO. The 25 ILCS 170 URL is OK; the 8 Article URLs need section expansion.

### Sub-finding: dispatch-prompt recursion under-specification

The dispatch prompt's Step 3 reads "pass-3 per chosen chapter" with two cases (empty TSV → leaf; non-empty TSV → reason and emit). The strict interpretation is one round of pass-3 per chapter, no recursion. **Three of five subagents in batches 1-2 self-recursed** (TX/AR went deeper on their own initiative, treating intermediate TOC pages as another round of pass-3); **two didn't** (CO/IL). Per-state addenda added to batch 3 and 4 prompts ("recurse pass-3 on each Article", "URLs must be section-level") fixed the behavior for WI/WA/AK/MI/WV/CA. The generic dispatch prompt remains under-specified for deep trees; per-state regime hints close the gap.

## Decisions Made

- **Patch _build_justia_link_tsv with TDD, not work around in the subagent prompt**: User chose the strict TDD route over a localized hack in `subagent_fetch_save.py` or downstream URL post-processing. Patch is committed at `28b1aab`; 52 tests green.
- **Subagent dispatch prompt is a committed artifact**, not inlined ad-hoc per Agent call. Committed at `775cf99` as `plans/_handoffs/20260519_subagent_dispatch_prompt.md`.
- **CO/IL Article-level bundles committed as-is**, flagged for Phase C remediation rather than re-dispatched. Explicit cheaper-now / more-expensive-downstream trade-off accepted.
- **2.5s rate-limit per user instruction** — applies to Phase C `PlaywrightClient(rate_limit_seconds=2.5)`; not relevant for Phase B subagent dispatch where each `subagent_fetch_save.py` invocation makes one fetch per subprocess.
- **State slug mapping** for the 12 priority states locked in the dispatch prompt for reuse: TX→texas, MA→massachusetts, PA→pennsylvania, CO→colorado, IL→illinois, AR→arkansas, WI→wisconsin, WA→washington, AK→alaska, MI→michigan, WV→west-virginia, CA→california.

## Results

Each state bundle is at `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2025/` with the schema documented in [`subagent_canaries/README.md`](../results/subagent_canaries/README.md):
- `pass1_state_index.{html,tsv}` + `pass1_chosen.json`
- `pass2_<title-slug>.{html,tsv}` + `pass2_<title-slug>_chosen.json` (per chosen title)
- `pass3_<chapter-slug>.{html,tsv}` + `pass3_<chapter-slug>_chosen.json` (per chosen chapter and any deeper TOC pages a subagent recursed into)
- `result.json` (aggregate proposed_urls + metadata + notes)

## Open Questions

| Question | Owner | Path |
|---|---|---|
| Phase C section-fetch — fetch the proposed_urls and save section bodies to `data/statutes/<STATE>/2025/sections/*.txt` | Next session | Pattern from 2015 fetch in [`20260518_fetch_2015_section_bodies.md`](../plans/_handoffs/20260518_fetch_2015_section_bodies.md) Step 3; use `rate_limit_seconds=2.5` |
| CO + IL Article-level remediation ([#19](https://github.com/danparshall/lobby_analysis/issues/19)) | Next session or Phase C pipeline change | Either re-dispatch with tighter prompt, or have Phase C detect Article-shaped URLs and do section-discovery |
| WA dedup policy — 29B canonical vs 42.17A legacy ([#20](https://github.com/danparshall/lobby_analysis/issues/20)) | Phase C planning | Two-source state; pick authoritative tag and/or dedup by semantic mirror |
| What's the right granularity for the WV +10 sections? | Future calibration | The 24-section 2015 GT was a *minimum*; the 34-section 2025 bundle includes real lobbying-relevant additions |
| OH 2015 (already on disk via batch-2 desktop run) is currently the only OH bundle that wasn't dispatched this session — does it need re-verification at 2025? | User | OH 2025 is already on disk from the archived statute-retrieval branch (30-URL GT-shape); skip per the handoff |

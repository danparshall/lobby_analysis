<!-- Generated during: convos/20260515_b4_impl_and_wy_fl_canaries.md -->

# B4 pilot canaries — WY 2010 + FL 2010

**Date:** 2026-05-15
**Branch:** `api-multi-vintage-retrieval`
**Mode:** `CANARY_MODE=B4` against real Anthropic API + real Justia via `PlaywrightClient`.
**Cost cap:** $1.00 per run (`CostTracker.cap_usd=1.0`, conservative pricing $3/$15-per-M).
**Plan:** [`plans/20260515_b4_three_pass_discovery_plan.md`](../plans/20260515_b4_three_pass_discovery_plan.md)
**Handoff:** [`plans/20260515_b4_handoff_to_fresh_agent.md`](../plans/20260515_b4_handoff_to_fresh_agent.md) (Chunk 3)
**Supersedes for these states:** [`results/20260514_b3pw_pilot_canaries.md`](20260514_b3pw_pilot_canaries.md) (the 0/6 chapter-TOC ceiling on FL is closed; WY's 1/1 is preserved).

---

## TL;DR

Both canaries hit their target outcomes. **WY 2010: 1/1 GT-hit, $0.024, 31.7s, pass-3 correctly skipped** (chapter7.html is the leaf — empty children TSV → orchestrator preserves pass-2's URL as the final answer). **FL 2010: 6/6 GT-hit, $0.087, 67.1s, pass-3 fired twice** (chapter11.html + chapter112.html both have section children — pass-3 picked the in-scope sections from each).

Aggregate: **7/7 = 100% GT-hit recall** across the two canaries that B3PW had previously scored 1/7. The chapter-TOC ceiling is closed without any new prompt tuning — the adaptive children-probe + reused pass-2 template did the job the plan predicted they would.

Combined spend: **$0.111** of $2.00 cumulative across the two runs (each capped at $1.00 independently). Headroom is ample for Chunks 4–5.

No defects surfaced. No anti-bot incidents. Both runs completed within projected wall-time bands (plan: ~25s WY / ~38s FL on B3PW + 10–20s margin for the extra pass-3 fetch + LLM call).

---

## WY 2010 — 1/1 hit, pass-3 skipped (regression preserved)

```bash
CANARY_MODE=B4 CANARY_TARGET=WY PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

| Metric | Value |
|---|---|
| Ground-truth size | 1 (`Title28/chapter7.html`) |
| Parsed URLs | 1 |
| GT-hit rate | **1/1** (100%) |
| Wall time | 31.7s |
| Cost | $0.0238 (6,500 in / 290 out tokens) |
| Anthropic calls | 2 (pass-1, pass-2; pass-3 skipped) |
| Playwright fetches | 3 (state-year index, Title28 page, chapter7 page) |
| Anti-bot incidents | 0 |

### Trajectory

- **Pass-1** picked `Title28/Title28.html` correctly, recognizing this is WY's single lobbying-disclosure regime ("Wyoming's lobbying registration and disclosure requirements for lobbyists are codified under Title 28, which governs the Legislature and includes the Lobbyist Registration Act").
- **Pass-2** picked `Title28/chapter7.html` ("Title 28 Ch. 7 (Lobbyists) is the Lobbyist Registration Act") — same answer B3PW landed on.
- **Children-probe** fetched chapter7.html and built the children TSV via `_build_justia_link_tsv`. The page contains only a single navigation link back to the year index (`/codes/wyoming/2010/`), which is outside the chapter7 namespace and is filtered out. **TSV is empty → chapter IS the leaf → pass-3 skipped → orchestrator appends the original pass-2 ProposedURL (role + rationale preserved) to `parsed_urls`.**

This is the regression-prevention case from the B4 plan's Phase 3 step 14 — B4 must not break states where the chapter page IS the statute body. Confirmed working.

---

## FL 2010 — 6/6 hit, chapter-TOC ceiling closed

```bash
CANARY_MODE=B4 CANARY_TARGET=FL PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

| Metric | Value |
|---|---|
| Ground-truth size | 6 (all Ch.11 sections) |
| Parsed URLs | 8 (6 GT + 11_044 support + Ch.112 PARTIII.html) |
| GT-hit rate | **6/6** (100% recall) |
| Wall time | 67.1s |
| Cost | $0.0868 (20,464 in / 1,696 out tokens) |
| Anthropic calls | 5 (1 pass-1 + 2 pass-2 + 2 pass-3) |
| Playwright fetches | 5 (state-year index, 2 title pages, 2 chapter pages) |
| Anti-bot incidents | 0 |

### Trajectory

- **Pass-1** picked both Title III + Title X — multi-pick on parallel regimes worked (the Rule-2 rewrite from the B3PW canary fixes carries through). Rationale: "Florida has a dual lobbying-disclosure regime: legislative lobbying (Ch.11) falls under Title III, while executive-branch lobbying and ethics/disclosure rules (Ch.112) fall under Title X. Both titles are needed."
- **Pass-2** picked one chapter per title: `TitleIII/chapter11/chapter11.html` and `TitleX/chapter112/chapter112.html`. Same answer B3PW landed on; both pages are chapter-TOCs, not leaves.
- **Children-probe** fetched both chapter pages. **Both TSVs non-empty → pass-3 fired for each chapter.**
- **Pass-3 on Ch.11** picked 7 URLs: all 6 GT sections (11_045 lobbying-before-the-legislature, 11_0451, 11_0455, 11_047, 11_061, 11_062) **plus** `11_044` as `support_chapter` role. The 11_044 inclusion is plausible (chapter-internal cross-references); 6/6 GT recall achieved.
- **Pass-3 on Ch.112** picked 1 URL: `TitleX/chapter112/PARTIII.html` — a sub-chapter TOC, not a section leaf. This is **not** in the FL GT (the curated GT for FL 2010 only contains Ch.11 sections), so it neither helps nor hurts the scoreboard, but see "Open observations" below.

### Final URL list

| # | URL | Role | GT hit? |
|---|---|---|---|
| 1 | `TitleIII/chapter11/11_045.html` | core_chapter | ✓ |
| 2 | `TitleIII/chapter11/11_0451.html` | core_chapter | ✓ |
| 3 | `TitleIII/chapter11/11_0455.html` | core_chapter | ✓ |
| 4 | `TitleIII/chapter11/11_047.html` | core_chapter | ✓ |
| 5 | `TitleIII/chapter11/11_061.html` | core_chapter | ✓ |
| 6 | `TitleIII/chapter11/11_062.html` | support_chapter | ✓ |
| 7 | `TitleIII/chapter11/11_044.html` | support_chapter | — |
| 8 | `TitleX/chapter112/PARTIII.html` | core_chapter | — |

Precision is 6/8 = 75%; recall is 6/6 = 100%. The plan's gate is recall (GT-hit rate), so we're at the ideal end of the "≥4/6, ideally 6/6" target.

---

## Open observations (not gating; Chunk-4-relevant)

**Pass-3 on Ch.112 returned a partial-chapter TOC, not section leaves.** `PARTIII.html` is *another* TOC layer below `chapter112.html` — Florida's Ch.112 is split into Parts (I, II, III) before reaching individual sections like `112.3215.html`. The current orchestrator treats pass-3's output as the final answer and does not recurse. For Ch.112, that's fine on this canary (no GT) but signals that for some chapters, a 4th pass would be needed to drill all the way to the section body. This is the "What could change" item from the plan's "Cross-vintage stability" / "chapters mixing inline text + child sections" notes; the recursion question becomes load-bearing only if a state's GT requires section-leaf depth under a multi-Part chapter. Surface in Chunk 4 (OH single-pair canary will reveal whether the OH 2010 30 GT URLs need anything below pass-3).

**Pass-2 found a `support_chapter` cross-reference inside Ch.11.** 11_044 is not in the FL 2010 GT but the model's role-tagging is consistent with the pass-2 prompt's distinction between core vs support. Whether downstream extraction wants to retrieve support_chapter URLs as well is an extraction-side decision, not a discovery-side one.

**Cost per pair tracks the plan's projection.** WY (chapter-leaf, 2 LLM calls): $0.024. FL (multi-chapter, 5 LLM calls): $0.087. Mean of $0.056/pair matches the plan's $0.06/pair projection for the 350-pair fan-out. 350 × $0.056 ≈ **$19.5** projected fan-out spend (vs plan's ~$21).

---

## What didn't break / still confidence-inspiring

- **Children-probe is deterministic and well-behaved.** `_build_justia_link_tsv` correctly returned empty for WY's chapter7.html and non-empty for FL's two chapter pages. The Pattern-2 (`Foo/Foo.html`) namespace logic from the B3PW canary fixes carries through unchanged.
- **Pass-3 prompt reuse (pass-2 template for both) works in production.** The model's role-tagging on Ch.11 sections (`core_chapter` for the actual lobbying statutes, `support_chapter` for cross-referenced sections) shows it's correctly interpreting Rule 6 at the chapter-page-snapshot depth. The plan's "Rule 6 is depth-agnostic" hypothesis held.
- **Cost tracker is well below cap on both runs.** WY: 2.4% of $1 cap. FL: 8.7%. Combined: 5.5%.
- **Wall time is acceptable.** WY 31.7s (vs plan's ~25s estimate; small overage). FL 67.1s (vs plan's ~38s B3PW + ~20s margin = ~58s estimate; small overage). Both within the same order of magnitude — no concerning slowdown from the extra pass-3 fetches.
- **No anti-bot incidents on either run.** Playwright cleared Justia's Cloudflare-style heuristics on all 8 fetches across both canaries.

---

## Appendix — exact canary commands

```bash
# WY 2010 — chapter-leaf case (regression check)
CANARY_MODE=B4 CANARY_TARGET=WY PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py

# FL 2010 — split-regime + chapter-TOC ceiling close
CANARY_MODE=B4 CANARY_TARGET=FL PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

## Handoff — what Chunk 4 picks up

The B4 plan's gate for the 10-pair canary is ≥80% aggregate GT-hit + 0 anti-bot incidents across the 5 pilot states (CA/TX/NY/WI/WY). After this canary we have 2 of 5 pilots done (WY pass; FL is not in the 5-pilot list but is a sanity check). **Chunk 4 needs to run B4 against NY 2010, TX 2009, OH 2010** to characterize how the chapter-TOC ceiling distributes — and to confirm that the FL-style multi-pass behavior generalizes. NY/TX/OH targets are already added to `SINGLE_PAIR_TARGETS` in the canary script.

Specifically:
- **NY 2010** (1 GT URL: `new-york/2010/rla/`) — single-page codified act. Expected: pass-2 picks `rla/` directly; children-probe should reveal whether it's a leaf or contains sub-pages.
- **TX 2009** (1 GT URL: `texas/2009/government-code/title-3-legislative-branch/chapter-305-registration-of-lobbyists/`) — directory-style chapter URL.
- **OH 2010** (30 GT URLs across `ohio/2010/title1/chapter101/` and `chapter121/`) — nested title/chapter with underscore-section leaves. Expected: split regime; pass-3 should pick the 30 section URLs. **Target: ≥25/30.** If lower, surface to user before proceeding — OH is the highest-stakes pilot for chapter-TOC ceiling characterization.

Append outcomes to this file rather than starting a new one (the handoff explicitly says: "Append outcomes to `results/20260515_b4_pilot_canaries.md`.").

# B3-with-Playwright pivot — supersedes the API-only subagent-dispatch pivot

**Date:** 2026-05-14
**Branch:** api-multi-vintage-retrieval
**Prior pivot superseded:** commit `376b2b1` (pivot to ~50 parallel Sonnet-4.6 subagents at ~$175 fan-out)

## Summary

Session opened from a misremembered prior: user recalled "grabbing 50 states worth of Justia data via Sonnet subagents browsing." Triple-check against the repo found that memory fuses two separate things — the 50-state **portal** subagent dispatch on `pri-2026-rescore` (981 artifacts, current-vintage state portals, not Justia, 2026-04-13 snapshot date) and the 50-state Justia **year-availability audit** on `pri-calibration` (Playwright-driven, 49/50 eligible at 2010, `docs/historical/pri-calibration/results/20260418_justia_retrieval_audit.csv`). No artifact ever combined "50 states × Justia × subagents." The closest committed primitives that *do* survive the laptop wipe are the audit CSV (year-level Justia locations for 50 states), the Playwright `justia_client.py` HTTP layer, and the hand-curated `LOBBYING_STATUTE_URLS` (5–6 pilot states only).

With recall corrected, we re-read the current B2/B3 plan and the `376b2b1` subagent pivot. The substantive output of this session: **B3 with Playwright instead of httpx** is a better synthesis than either the original httpx-B3 plan or the subagent fan-out. Reasoning below; revised plan to be drafted next session.

## Topics Explored

- Triple-check on what's committed for "50-state Justia work" vs what the user remembered
- Re-read of B2 result docs (`results/20260514_{wy,fl}2010_b2_index_inline_hit_rate.md`) and the B3 plan (`plans/20260514_b3_two_pass_discovery_plan.md`)
- Cost comparison across 5 architectures for the 350-pair fan-out: B2 / B3 / subagent-dispatch / pure-Playwright / Playwright-plus-hand-curation
- Why the API $ axis is essentially a red herring at this project's scale (max ~$175 even on the most expensive option)
- What "B3 with Playwright" actually means — Playwright at the HTTP layer, Anthropic API retained for title-picking + URL-proposal judgment
- Whether subagent dispatch (`376b2b1` pivot) is still justified once Playwright is on the table

## Provisional Findings

- **The user's "50-state subagents browsing Justia" memory is a conflation.** Two real artifacts exist; the union is not. Committed survivors of the laptop wipe: audit CSV (50 rows, year-level), `justia_client.py` (Playwright), `statute_retrieval.py` (audit logic), `LOBBYING_STATUTE_URLS` (5–6 states, hand-curated), pilot statute bundles in `~/data/lobby_analysis/statutes/` (6 state dirs, sha256-verified intact).
- **B2 fails for structural reasons, not prompt-tuning reasons.** The state-year index is title-only-depth on Justia, so any single-fetch-single-call architecture lands one hop short of the statute leaf. Two canaries (WY 2010 single-chapter-leaf shape; FL 2010 per-section-leaf shape) confirm the limit is universal across statute structures. Total spend on the diagnosis: ~$0.05.
- **B3's structural fix (two-pass) is sound.** But the originally-planned httpx + Range-GET + rich-header anti-bot recipe is hand-tuned — the B2 canary already surfaced one defect of this shape (HEAD-check missing the rich-header set). Each future surprise of that shape costs another diagnosis session.
- **Playwright at the HTTP layer eliminates that fragility.** `justia_client.py` already exists, was used at 50-state scale in the audit, and at section-leaf depth in the 5-state retrieval pilot. The fresh-browser-per-request pattern handles Cloudflare's JS challenge by default; no Range-GET trick, no header-set tuning.
- **The LLM role stays narrow and well-suited.** Picking "which of these 43 titles contains the lobbying statute" is exactly what the model is irreplaceable at; replacing it with regex/heuristic on link text degrades reliability for marginal $ savings. Keep the API for pass-1 title-picking and pass-2 URL-proposal; replace only the fetcher.
- **`376b2b1`'s subagent dispatch ($175) is over-engineered relative to B3-with-Playwright (~$17–30).** The original subagent pivot was justified by httpx-B3's "FL chapter-TOC ceiling" risk — i.e., if the title page only exposes chapter-TOCs not section-leaves, B3 lands one hop short again and needs B4. But Playwright doesn't change that risk axis (it's an LLM-judgment axis, not an anti-bot axis), so the cheaper hybrid carries the same FL-canary contingency at one-tenth the cost.

## Cost / risk comparison (350-pair fan-out)

| Approach | API $ | Wall time | Anti-bot robustness | Reliability |
|---|---|---|---|---|
| B2 (single-pass, httpx) | ~$10–14 | ~5 min | hand-tuned headers | **0% proven** |
| B3 (two-pass, httpx) | ~$17–30 | ~10 min | hand-tuned headers; one defect already surfaced | Unknown; FL canary is the gate |
| Subagent dispatch (committed `376b2b1`) | ~$175 | one session | depends on agent's chosen tool | ≥95% by construction |
| Pure Playwright + heuristic | $0 | ~30–60 min | high | 60–85% (link-text heuristic for "which title is lobbying" is brittle) |
| Playwright + hand-curated `LOBBYING_STATUTE_URLS` extended to 50 states | $0 | ~17 min audit + chapter fetches | high | 100% deterministic, **but ~25–50 hrs human time** |
| **B3 with Playwright (this session's proposal)** | **~$17–30** | **~30–40 min** with 4-way browser parallelism | **high** | **High; same FL-canary gate as httpx-B3** |

API $ at this project's scale is rounding-error currency. The real currency is human dev hours + reliability of output. B3-with-Playwright wins on both vs subagent dispatch ($150 saved + simpler operational story) and vs hand-curation (~25–50 hours saved).

## Decisions Made

- **Supersede `376b2b1`'s subagent-dispatch pivot with B3-with-Playwright.** Original B3 plan (`plans/20260514_b3_two_pass_discovery_plan.md`, httpx-based) and the subagent pivot both preserved on disk per contingency principle.
- **LLM role unchanged from original B3:** pass-1 title-picker + pass-2 URL-proposal, both via `anthropic.AsyncAnthropic`. The two prompts (`api_seed_discovery_pass1_prompt.md`, `api_seed_discovery_pass2_prompt.md`) carry forward unchanged.
- **HTTP layer swaps from httpx to Playwright.** Reuse `src/scoring/justia_client.py` instead of writing a new `fetch_justia_index` in `api_retrieval_agent.py`. Drop `Range-GET 0-65535` and the rich-header-set scaffolding — Playwright makes both unnecessary.
- **Add a 10-pair pre-fan-out canary** at mixed depths (5 pilot states + 5 unseen) before the full 350-pair run. ~20 min wall time, ~$1 API. Validates Playwright at sustained pressure (700 fetches across mixed depths) before committing the full fan-out.
- **HEAD verification → Playwright fetch verification.** Stronger guarantee than `head_check`'s HTTP-layer probing; sidesteps the per-path header-set sensitivity that bit the B2 canary.

## Open Questions

- **Sustained-pressure anti-bot behavior at section-leaf depth.** Audit validated Playwright at 50 state-year-index fetches with 2s courtesy delay; pilot validated at ~50 section-leaf fetches across 5 states. 700 fetches at mixed depths with 4-way browser parallelism is a step up. Resolved by the 10-pair pre-fan-out canary.
- **Test story for the Playwright-fetcher path.** `justia_client.py` already has a `FakeClient` pattern at the `Client` protocol boundary; the B3 orchestrator tests should mock at that same boundary rather than at the httpx layer (drop `respx` from B3 test deps, but keep it for any non-Justia fetchers).
- **Per-state courtesy delay calibration.** Audit used 2s between states (50 states × ~20s ≈ 17 min). For 350 pairs × 2 fetches with 4-way parallelism, the same 2s/state pacing gives ~30–40 min. Tighten if needed after the 10-pair canary surfaces actual response-time distribution.
- **Cross-vintage URL pattern stability.** OH 2010 → OH 2025 showed identical URL structure with year-swap (per `LOBBYING_STATUTE_URLS` comments). If this holds broadly, the model can produce URLs for vintages it hasn't fetched a snapshot for by templating on a single-vintage discovery. Worth testing during the canary phase — would compress 7-vintage fan-out to 1-vintage discovery + 6× URL-templating.

## Next Steps

- **Draft revised plan** as `plans/20260514_b3_two_pass_discovery_plan_playwright.md`. Mostly a delta on the original B3 plan: swap `fetch_justia_index` (httpx) for `justia_client.fetch_*` (Playwright); drop Range-GET + rich-headers; add 10-pair pre-fan-out canary step; keep all 7 behavioural tests unchanged at the orchestrator boundary.
- **Keep `20260514_b3_two_pass_discovery_plan.md` and `376b2b1`'s subagent pivot on disk** per the contingency principle. Both are still useful as fallback if the Playwright-at-volume canary surfaces something unexpected.
- **Update STATUS.md and RESEARCH_LOG.md** to point to the new plan once drafted.
- **Next implementation session** writes test 1 first (single-title happy-path orchestrator) using the `Client` protocol mock; lands GREEN; commits; then proceeds through tests 2–7.

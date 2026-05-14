# Canary call (WY 2010) + URL-convention gap diagnosis

**Date:** 2026-05-14
**Branch:** api-multi-vintage-retrieval
**Worktree:** `.worktrees/api-vintage`

## Summary

Picked up from Phase 0-1's `a475bdd` commit with the next concrete plan step: the proof-of-life canary call against `("WY", 2010)` using `discover_urls_for_pair` against the real Anthropic API. The session caught two prerequisite gaps the prior session hadn't shipped (Phase 4's seed-discovery prompt template was missing; the plan's documented model `claude-sonnet-4-7` doesn't exist — Sonnet only goes up to 4.6 as of today), closed both, and then ran the canary. Result: pipeline plumbing works end-to-end, but **0 of 9 proposed URLs resolve** on Justia. The model nails semantic identification (WY Title 28 Ch. 7) but gets the URL convention completely wrong — lowercase `title28` instead of Justia's capital-T `Title28`, and 8 speculative section-leaf URLs that Justia doesn't host. HEAD verification cannot rescue proposal-side failures.

This is exactly the **"Justia URL-convention drift"** edge case the plan named in §Edge cases #2. The canary did its job — caught the architectural gap before a 50-state fan-out burned budget on ~0% hit rate. Decision: checkpoint here; pick up B2 (pre-fetch Justia state-index page, inline in prompt) next session before considering B3 (two-pass discovery).

## Topics Explored

- Prereq gap analysis before the canary (caught: missing prompt template, non-existent model)
- Authoring `src/scoring/api_seed_discovery_prompt.md` v1 (5 in-context conventions: CA range-leaf, TX full-chapter directory + 2009 substitution, NY single-page codified act, WI per-section leaf, OH nested title/chapter underscore-section; WY held out)
- Tolerant JSON fence-stripping in `_parse_response_text` (defensive: models often add ` ```json ` fences despite prompt discipline)
- Availability metadata side-channel (`justia_unavailable` + `alternative_year` + `notes` captured per call; batch writes `availability.jsonl` line when `justia_unavailable=true`) — addresses plan §Edge cases #1 (CO pre-2016 has no Justia coverage)
- Sonnet 4.6 vs the plan's documented `claude-sonnet-4-7` (the latter doesn't exist; `claude-opus-4-7` does — looks like plan-author misread the Opus version as a Sonnet release)
- WY 2010 canary execution (4,941 in / 921 out tokens / ~$0.018)
- HEAD verification via `httpx` (browser User-Agent + GET-range fallback to bypass Justia's anti-bot 403 on bare requests)
- Architecture options for the URL-convention gap (B1 examples-only band-aid / B2 index-fetch / B3 two-pass)

## Provisional Findings

- **Pipeline works end-to-end.** SDK auth, prompt rendering, parser (with fence-strip + availability metadata), all clean.
- **Semantic recall is fine.** Model correctly identifies WY Title 28 Ch. 7 as the lobbying-disclosure statute — semantic knowledge of state statutes is not the bottleneck.
- **URL convention prediction is the bottleneck for cold discovery.** Model defaulted to lowercase `title28` (CA/TX/NY/WI/OH examples use lowercase) and overgeneralized WI's per-section convention to invent 8 non-existent section pages. Justia is case-sensitive; all 9 proposals 404.
- **HEAD verification cannot rescue this.** The plan's "model proposes wide, HEAD filters" architecture doesn't work when the model can't propose any correct URL in the first place. The fix has to be proposal-side.
- **The canary did its job.** Surfaced an architectural gap for ~$0.02, before a 350-pair fan-out at ~$6 would have returned ~0% hit rate.
- **`claude-sonnet-4-7` doesn't exist.** Anthropic's `models.list()` shows latest Sonnet is `claude-sonnet-4-6` (Feb 2026); `claude-opus-4-7` (Apr 2026) is the model the plan-author may have confused with it. Corrected throughout this branch.
- **Justia anti-bot defenses.** Bare httpx requests get 403; need browser User-Agent + Range-GET to probe URLs. The existing Playwright `justia_client` is unaffected (it's a real browser). This is a wrinkle for the eventual `url_verification.py` (plan Phase 2): bare HEAD won't work; need User-Agent at minimum.

## Decisions Made

- **Hold WY out of the seed-discovery prompt's in-context examples** — keeps the canary a real cold-discovery test rather than a copy-from-context exercise.
- **Sonnet 4.6 as the default model** for discovery (plan's `4-7` corrected). Escalate to `claude-opus-4-7` only if a future canary at index-augmented prompt shape still hits poorly.
- **Tolerant JSON parsing is the right call** (Dan's framing: "json is hard for models, we don't need to crush them"). Added defensively even though this session's canary returned raw JSON without fences.
- **Availability metadata captured per call + side-channeled to `availability.jsonl`** for batch-level visibility into missing-data pairs (Dan's framing: "we should be aware of missing data").
- **Architecture decision deferred to next session.** B2 (index-fetch) over B1 (more examples). B3 (two-pass) gated on B2's results — B2's work is a strict subset of B3, so trying B2 first is a no-regret move.

## Results

- [`results/20260514_wy2010_canary_url_hit_rate.md`](../results/20260514_wy2010_canary_url_hit_rate.md) — full canary output, HEAD probe table, diagnosis, next-step options.

## Open Questions

- **Will B2 (index-fetch + prompt augmentation) be enough, or will we still need B3 (two-pass)?** Unknown until tried. WY 2010 should be a fair test — single chapter-leaf state with sui-generis convention. If B2 works for WY, the long tail of 50-state quirks probably yields too.
- **What's Justia's coverage like for older vintages across all 50 states?** The plan assumes ~7 vintages per state with some `justia_unavailable=true` cases (CO pre-2016 named). Until the index-fetch is in place, we don't know how many `(state, vintage)` pairs will be `justia_unavailable` — could be 10%, could be 50%. The `availability.jsonl` side-channel will surface this once the discovery pipeline actually runs.
- **Should `url_verification.py` (plan Phase 2) standardize the browser-User-Agent + GET-range pattern?** Probably yes — bare HEAD against Justia 403s every time, including the curated-good ground-truth URL. This is information the plan didn't have.
- **The canary script `scripts/canary_discovery.py` is not gitignored** — relying on "don't `git add` it" is fragile. Worth adding `scripts/canary_*.py` to `.gitignore`? Or moving canary scripts under `data/` (which is gitignored)?
- **Prompt iteration cadence.** Each prompt change costs at least one canary API call to validate. Worth thinking about how to test prompt changes without burning tokens — e.g., a cheap "does the output schema parse?" check on cached canary fixtures before the live retry.

## Next Steps

- Read this session's results doc, then start a B2 session: pre-fetch `https://law.justia.com/codes/<state>/<year>/` for the target pair, inline the response (or a model-extracted summary of titles) in the discovery prompt, re-run the WY 2010 canary.
- If B2 lifts hit rate convincingly (e.g., gets the case right + correct chapter-leaf shape), scale to canaries on the other 4 pilot states at 2010 and at 2015 before the full 50-state fan-out.
- Open the question with Dan: do we want to commit the canary-discovery script under a gitignored path, or keep it as a one-off recreated per session?

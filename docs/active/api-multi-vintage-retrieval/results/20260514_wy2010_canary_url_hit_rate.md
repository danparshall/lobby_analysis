<!-- Generated during: convos/20260514_canary_wy2010_url_convention_gap.md -->

# WY 2010 canary — URL hit rate against Justia

**Date:** 2026-05-14
**Pair tested:** `("WY", 2010)`
**Model:** `claude-sonnet-4-6`
**Prompt:** `src/scoring/api_seed_discovery_prompt.md` v1 (14.6 KB / ~3.7k tokens, 5 in-context examples CA/TX/NY/WI/OH 2010, WY held out)
**Ground truth (curated):** `https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html`

## API call

| Metric | Value |
|---|---|
| Input tokens | 4,941 |
| Output tokens | 921 |
| Approx cost (Sonnet 4.6) | ~$0.018 |
| Response shape | JSON, no markdown fences, parseable on first try |
| `justia_unavailable` | `false` |
| `alternative_year` | `null` |
| Schema violations | 0 |

## URLs proposed (9 total)

| # | URL | Role |
|---|---|---|
| 1 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/` | core_chapter |
| 2 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-101/` | core_chapter |
| 3 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-102/` | core_chapter |
| 4 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-103/` | core_chapter |
| 5 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-104/` | core_chapter |
| 6 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-105/` | core_chapter |
| 7 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-106/` | core_chapter |
| 8 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-107/` | core_chapter |
| 9 | `https://law.justia.com/codes/wyoming/2010/title28/chapter7/section28-7-108/` | support_chapter |

## HEAD verification (via `httpx` + browser User-Agent, GET-range fallback)

Bare httpx requests get 403 from Justia (anti-bot). Adding a Chrome-style User-Agent + `Range: bytes=0-2047` GET headers gets through.

| URL | Status | Notes |
|---|---|---|
| Ground truth `Title28/chapter7.html` | **206** (live) | Capital-T, single .html chapter-leaf |
| Proposed `title28/chapter7/` | **404** | Redirects to `chapter7/chapter7.html` (404 page, 58 KB) |
| Proposed 8× `section28-7-NNN/` | **404** each | All redirect to `section28-7-NNN/section28-7-NNN.html` (404 pages) |

**Hit rate: 0 / 9.**

## Diagnosis

Two independent failure modes, both proposal-side (HEAD verification cannot rescue either):

1. **Case-sensitivity.** Justia's WY URLs use capital-T `Title28`. None of the 5 in-context examples (CA `gov/`, TX `government-code/title-3-...`, NY `rla/`, WI `13/`, OH `title1/chapter101/`) teach this casing — model defaulted to lowercase `title28`.
2. **Convention overgeneralization.** WY 2010 is a single chapter-leaf .html page (1 URL total, like NY's codified-act page). Model picked up WI's per-section enumeration convention from context and applied it to WY, inventing 8 `section28-7-NNN/` URLs that don't exist on Justia.

The model's `notes` field self-flagged uncertainty: *"If Justia uses a different slug convention for Wyoming (e.g., without 'section' in the path, or with hyphenated section numbers), some leaf URLs may 404 and should be filtered."*

Semantic recall is fine — model correctly identified WY Title 28 Ch. 7 as the lobbying-disclosure statute. The gap is convention prediction for states with sui-generis URL slugs.

## What this means for the plan

The plan's discovery architecture (model proposes URLs → HEAD filters hallucinations → Playwright fetches survivors) does not survive contact with Justia's per-state slug conventions for WY 2010 — and likely fails similarly for many of the 50 states whose conventions aren't represented in the in-context example set. This is exactly the **"Justia URL-convention drift"** edge case the plan named in §Edge cases #2; the canary's role was to surface it before a 50-state fan-out burned token + clock budget on ~0% hit rate.

## Next-session options

- **B1** — Add more in-context examples covering capital-T `Title<N>` + single-leaf .html conventions. Band-aid; unlikely to generalize across 10+ Justia per-state quirks.
- **B2** — Pre-fetch the per-state Justia index page (`https://law.justia.com/codes/<state>/<year>/`), inline it in the discovery prompt. One extra HTTP call per pair; ~10k extra tokens worst case (~$0.04 → ~$14 for the full fan-out). Should fix casing immediately because the model sees `Title28` literally on the index page.
- **B3** — Two-pass discovery: pass 1 reads state index, picks chapter; pass 2 reads chapter index, enumerates only leaf URLs that are actually listed. Near-100% URL hit rate by construction; 2–3 HTTP fetches per pair + 2 API calls; ~2–3 days of work vs. B2's ~1 day.

Recommended ordering: **B2 first.** Its work is a strict subset of B3 — if B2's hit rate is acceptable, ship; if not, B3 reuses the index-fetch helper, prompt-augmentation pattern, and tests.

## Reproducibility

- Canary script: `scripts/canary_discovery.py` (not committed, per plan)
- Prompt: `src/scoring/api_seed_discovery_prompt.md` (v1, committed this session)
- Model: `claude-sonnet-4-6`
- Anthropic SDK: `anthropic>=0.102.0`

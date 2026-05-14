<!-- Generated during: convos/20260514_b2_justia_index_inline_recanary.md (pending) -->

# WY 2010 B2 canary — state-index inlined into discovery prompt

**Date:** 2026-05-14
**Pair tested:** `("WY", 2010)`
**Model:** `claude-sonnet-4-6`
**Prompt:** `src/scoring/api_seed_discovery_prompt.md` v2 (now with `{state_index}` placeholder + Rule 6)
**Ground truth (curated):** `https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html`
**Baseline to beat:** B1 (no index) was 0/9 — see `20260514_wy2010_canary_url_hit_rate.md`.

## The architecture being tested

Pre-fetch `https://law.justia.com/codes/wyoming/2010/` with browser-emulating headers (Range-GET is the only request shape that gets past Justia's anti-bot — bare UA-only GETs 403 the index page). Extract `<a href>` links whose href is a descendant of `/codes/wyoming/2010/`. Inline as TSV `<absolute-url>\t<anchor-text>` lines in the discovery prompt's new `{state_index}` placeholder. New Rule 6 instructs the model to:

1. Copy URL casing literally from the snapshot.
2. Not propose URLs deeper than the snapshot exposes.
3. Filter to in-scope statutes (Rule 4) but choose from the snapshot.

## What the snapshot exposed

| Metric | Value |
|---|---|
| HTML fetched | 61,946 bytes (range 0–65535) |
| Anchors in scope | 43 (one per title; one level deep only) |
| Token cost added to prompt | ~1,000 tokens (~$0.003) — well under the "10k worst case" diagnostic estimate |

The state-year index only exposes **title-level leaves** (`Title28/Title28.html`, etc.). Chapter- and section-level URLs within each title are not on this page. The relevant entry the model sees:

```
https://law.justia.com/codes/wyoming/2010/Title28/Title28.html	Title 28 - Legislature
```

## API call

| Metric | Value |
|---|---|
| Input tokens | 6,822 (vs B1: 4,941; +38%) |
| Output tokens | 284 (vs B1: 921; −69% — model returned tighter answer) |
| Approx cost (Sonnet 4.6) | ~$0.025 (vs B1: ~$0.018) |
| Response shape | JSON, no markdown fences, parseable on first try |
| `justia_unavailable` | `false` |
| Schema violations | 0 |

## URL proposed (1 total)

| # | URL | Role |
|---|---|---|
| 1 | `https://law.justia.com/codes/wyoming/2010/Title28/Title28.html` | core_chapter |

Model's `notes`:
> "Wyoming's lobbying disclosure statutes are found in Title 28 (Legislature), Chapter 7 (Lobbyists). The snapshot only exposes title-level pages, so the deepest available leaf for the lobbying chapter is the Title 28 index page. ... No per-section or per-chapter URLs are exposed at the snapshot level, so only the title-level URL is proposed to avoid hallucinated deeper paths."

## HEAD verification

Initial run reported 0/1 LIVE (`Title28/Title28.html` → 403). Diagnosed as a **HEAD-check defect** in this canary, not a dead URL: `head_check()` was missing the rich-header set (`Accept`, `Accept-Language`, `Connection`, `Upgrade-Insecure-Requests`) that the fetcher needed. With those added, all three relevant URLs return 206:

| URL | Status (rich headers) | Notes |
|---|---|---|
| Proposed `Title28/Title28.html` | **206** (live) | Title-level index page, ~6.8 KB |
| Ground-truth `Title28/chapter7.html` | **206** (live) | Capital-T, single chapter-leaf, ~6.7 KB |
| Lowercase `title28/chapter7.html` (B1's pick) | **404** | Confirms case-sensitivity is real |

**Hit rate (statute-leaf precision): 0 / 1.** The model's proposal is a live URL, but it's the title-index page, not the lobbying-chapter leaf.

The HEAD-check fix is captured in the canary script — `head_check()` now uses the same header set as `fetch_state_index`. Verification correctness was previously coupled to a header set that worked for *some* Justia URLs but not all; the fix removes that asymmetry.

## What B2 fixed, what B2 didn't

### Fixed: Mode 1 (casing)

B1 produced lowercase `title28/...` and 404'd uniformly. B2's model saw `Title28` literally in the snapshot and used that casing throughout. **Resolved by construction.**

### Fixed: Mode 2 (invented section URLs) — but by being conservative, not by being right

B1 invented 8 `section28-7-NNN/` URLs by overgeneralizing from Wisconsin's per-section convention in the in-context examples. B2's model, per Rule 6, refused to extrapolate beyond the snapshot — it explicitly noted "to avoid hallucinated deeper paths."

That's the **right behavior** under Rule 6, but the snapshot doesn't go deep enough to reach the actual statute leaf. **Mode 2 is fixed at the cost of recall.**

### Not fixed: chapter-leaf recall

The lobbying statute lives at `Title28/chapter7.html` — two hops below the state-year root. The state-year index page exposes only one hop (title-level). For the model to propose `chapter7.html`, it would need to either:

1. **Extrapolate** from the snapshot's title-naming convention (`TitleN/TitleN.html` → maybe `TitleN/chapterM.html`) — but this is exactly the hallucination behavior Rule 6 forbids.
2. **See the title-level page** — which only happens if the pipeline does a second fetch after the model picks Title 28.

The B2 architecture can't produce option 2 with one HTTP fetch + one API call. **This is structural, not a tuning problem.**

## Recommendation

**Promote to B3 (two-pass discovery).** The B2 evidence is that:

- A shallow snapshot grounds the model on casing perfectly but stops one hop short of the statute leaf for states whose statutes live below the title level.
- Loosening Rule 6 to "extrapolate from snapshot patterns" reintroduces the B1 invention-risk failure mode — we'd be re-inviting `section28-7-NNN/` style hallucinations.
- The model behaves *correctly* on B2; the architecture is the bottleneck.

B3 shape:

1. **Pass 1:** state-year index inlined as in B2 → model identifies the relevant title (e.g., Title 28).
2. Pipeline fetches the title-level page (`Title28/Title28.html`) — for WY 2010 this is ~6.8 KB, similar token budget to the state-year index.
3. **Pass 2:** title-level index inlined → model proposes chapter / section URLs from what the title page actually exposes.

Cost projection for the 50 × ~7 = 350-pair fan-out:
- B2 cost: 1 HTTP fetch + 1 API call/pair ≈ ~$10–14.
- B3 cost: 2 HTTP fetches + 2 API calls/pair ≈ ~$25–30. Some pairs (those where the title page itself lists chapter leaves rather than further index pages) finish in 2 fetches + 2 calls; rare cases may need a 3rd hop. Still trivial budget.

The diagnostic doc's framing held up: "B2 first; B3 gated on B2 results — B2's work is a strict subset of B3 so trying B2 first is no-regret." The reusable subset from B2:

- `fetch_state_index()` with anti-bot-aware headers
- `head_check()` with the matching header set
- Rule 6 in the prompt (still applies; in B3 it gates against extrapolation in both passes)
- The `{state_index}` placeholder pattern (B3 reuses it for the second-pass title-level index)

What needs to be added for B3:

- A title-page fetcher (essentially `fetch_state_index` parameterized on path depth)
- A two-call orchestrator that threads the model's pass-1 title pick into the pass-2 prompt
- A new prompt variant (or a new placeholder section) for pass 2 that emphasizes "you have already identified Title X; now propose chapter URLs from the title-level snapshot below"

## Reproducibility

- Canary script: `scripts/canary_discovery.py` (not committed, per plan)
- Prompt: `src/scoring/api_seed_discovery_prompt.md` (v2, this session)
- Agent: `src/scoring/api_retrieval_agent.py` (added `state_index: str = ""` kwarg to `_format_prompt` + `discover_urls_for_pair`; backward-compat via `str.format` ignoring unused kwargs — confirmed by all 9 pre-existing tests still passing)
- Index URL used: `https://law.justia.com/codes/wyoming/2010/` (Range-GET 0–65535)
- Model: `claude-sonnet-4-6`

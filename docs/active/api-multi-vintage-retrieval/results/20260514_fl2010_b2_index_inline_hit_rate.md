<!-- Generated during: convos/20260514_b2_justia_index_inline_recanary.md (pending) -->

# FL 2010 B2 canary — second-state confirmation

**Date:** 2026-05-14
**Pair tested:** `("FL", 2010)`
**Model:** `claude-sonnet-4-6`
**Prompt:** `src/scoring/api_seed_discovery_prompt.md` v2 (same prompt as WY 2010 B2 run)
**Sister result:** [`20260514_wy2010_b2_index_inline_hit_rate.md`](20260514_wy2010_b2_index_inline_hit_rate.md) — first B2 run; introduces the architecture and Rule 6.

## Why this canary

WY 2010 B2 ran 0/1 on statute-leaf precision. Before promoting to B3, run one more state to confirm the WY result reflects a structural limit of B2 — not a WY-specific quirk (e.g., title-only-depth being unusual for Justia, or the model misbehaving on this particular pair).

FL 2010 chosen because:

- **Non-pilot state** — not in the prompt's in-context examples (CA, TX, NY, WI, OH), so no memorized URL convention.
- **Different shape from WY** — FL Statutes Ch. 11 has ~70 per-section leaves; if B2 were going to extrapolate beyond the snapshot for any state, a per-section structure (closer to WI's in-context example) would be more tempting than WY's chapter-leaf.
- **Multi-URL ground truth** — exercises the canary's URL-set comparison cleanly. Core target: `chapter11/11_045.html` (Lobbying before the Legislature). Adjacent: `11_0451.html`, `11_0455.html`, `11_047.html`, `11_061.html`, `11_062.html` (~6 URLs total in scope).

## State index snapshot

| Metric | Value |
|---|---|
| HTML fetched | 65,769 bytes (range 0–65535) |
| Anchors in scope | 48 (title-level only, e.g., `TitleI/TitleI.html` ... `TitleXLVIII/TitleXLVIII.html`) |
| Token cost added to prompt | ~923 tokens (~$0.003) |

Same shape as WY 2010: state-year index exposes title-level links only. Chapter-level URLs (where the lobbying statute actually lives) are not present.

## API call

| Metric | Value |
|---|---|
| Input tokens | 7,014 (close to WY's 6,822) |
| Output tokens | 291 (close to WY's 284) |
| Approx cost (Sonnet 4.6) | ~$0.025 |
| Response shape | JSON, parseable on first try |
| `justia_unavailable` | `false` |
| Schema violations | 0 |

## URLs proposed (1 total)

| # | URL | HEAD status |
|---|---|---|
| 1 | `https://law.justia.com/codes/florida/2010/TitleIII/TitleIII.html` | **206** (live) |

The model's `notes` are the headline finding:

> "The fetched state index only exposes Title-level pages (e.g., TitleIII.html), not individual chapter or section leaves. Florida's lobbyist registration and disclosure statute is codified at **Chapter 11 (Legislative Organization, Procedures, and Lobbyists)**, which falls under Title III (Legislative Branch). The snapshot does not expose deeper chapter or section URLs, so only the Title III directory page is proposed here. Downstream verification should follow links from TitleIII.html to locate Chapter 11 sections **11.045 (lobbyist registration)** and related provisions. Title IV (Executive Branch) may also contain executive-branch lobbying disclosure provisions (under Chapter 16 or similar), but no chapter-level URL is available in the snapshot to propose with confidence."

The model **names the right chapter and the right core section by number** — and explicitly refuses to propose them as URLs because Rule 6 forbids extrapolation beyond the snapshot.

## Statute-leaf precision: 0 / 6

The model proposed `TitleIII/TitleIII.html`; none of the 6 ground-truth chapter-leaf URLs (`chapter11/11_045.html`, `11_0451.html`, `11_0455.html`, `11_047.html`, `11_061.html`, `11_062.html`) appear in the proposed set.

This is the same pattern as WY 2010: 0 / N where N is the number of statute-leaf URLs that exist for the pair. The model is doing the right thing under Rule 6; the architecture is the ceiling.

## Consolidated B2 verdict (across WY 2010 + FL 2010)

Two states, two structural shapes (single chapter-leaf vs many per-section leaves), one outcome: **B2 lands the model on the title-index page, never on the statute leaf, in both cases**. Token budget per call comes in well under the diagnostic's worst-case estimate (~1k extra tokens, not ~10k). The cost premium for B2 over B1 is trivial (~$0.007/pair, ~$2 across a 350-pair fan-out).

The FL run **strengthens** the WY conclusion in three ways:

1. **Same outcome despite different statute structure.** WY's lobbying chapter is a single `chapter7.html` leaf; FL's is ~6 per-section leaves. Both fail B2 identically. Title-only-depth on the state-year index is what's load-bearing, and that appears to be the universal Justia structure.
2. **Model behavior is robustly Rule-6-compliant.** FL's model output explicitly names the right chapter and section in narrative, while declining to emit URLs for them — confirming the model isn't an obstacle, the architecture is.
3. **The ceiling on B2 isn't recall in a soft sense; it's structural.** No prompt-tuning will push B2 past it. The only way to expose chapter-leaf URLs to the model is to fetch a deeper page.

## Recommendation

**Promote to B3.** Same conclusion as the WY writeup, now with confirming evidence on a structurally distinct state. The diagnostic doc's framing held: B2 was no-regret to try first because its work is a strict subset of B3, but B2 alone is not sufficient.

B3 shape (unchanged from WY writeup):

1. Pass 1 = state index inlined → model picks title.
2. Pipeline fetches that title's page (e.g., `TitleIII/TitleIII.html` is ~58 KB; with a `bytes=0-65535` range the chapter-list is fully captured).
3. Pass 2 = title-level page inlined as the new `{state_index}` content → model proposes chapter / section URLs from what the title page actually exposes.

The B2 building blocks all transfer to B3 directly:

- `fetch_state_index(slug, vintage)` — generalize to `fetch_path(absolute_url)` for the second hop
- `head_check` — unchanged
- Rule 6 — unchanged; in B3 it gates extrapolation in both passes
- `{state_index}` placeholder — unchanged; in B3 it's filled with the deeper page on pass 2
- The `state_index` kwarg on `discover_urls_for_pair` — unchanged; B3 just calls discover twice with different `state_index` payloads

What B3 needs that's net-new:

- A two-call orchestrator that threads the model's pass-1 title pick into the pass-2 prompt
- A pass-2 prompt variant (or modified system text) that frames "you already identified Title X on pass 1; now propose chapter/section URLs from the title-level snapshot below"
- Possibly a tweak to Rule 6's wording for pass 2, since the model has more reason to extrapolate within a chapter than across the whole state index

## Reproducibility

- Canary script: `scripts/canary_discovery.py` (not committed; parameterized via `CANARY_TARGET=FL` env var this session)
- Prompt: `src/scoring/api_seed_discovery_prompt.md` (v2, unchanged from the WY 2010 B2 run)
- Index URL used: `https://law.justia.com/codes/florida/2010/` (Range-GET 0–65535)
- Model: `claude-sonnet-4-6`

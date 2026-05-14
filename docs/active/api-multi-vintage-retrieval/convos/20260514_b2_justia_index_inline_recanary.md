# B2 Justia state-index inline + re-canary

**Date:** 2026-05-14
**Branch:** api-multi-vintage-retrieval

## Summary

The previous session's WY 2010 canary (`20260514_canary_wy2010_url_convention_gap.md`) returned 0/9 URL hits against Justia due to two failure modes: case-sensitivity (lowercase `title28` vs Justia's capital-T `Title28`) and convention overgeneralization (model invented 8 per-section URLs by extrapolating from Wisconsin's in-context example). The diagnostic flagged three architecture options to investigate, with `B2` (pre-fetch the per-state Justia index page, inline in discovery prompt) recommended first because its work is a strict subset of `B3` (two-pass discovery).

This session implemented and tested B2 against WY 2010, and then ran a confirming second canary against FL 2010 (non-pilot state, structurally distinct). Both runs produced the same shape of outcome: the model copies URL casing literally from the snapshot, refuses to extrapolate beyond what the snapshot exposes (per Rule 6 added to the prompt), and lands on the title-index page — never the actual statute leaf. This is structural: Justia's state-year index only goes one level deep, so the chapter-level URLs the model needs to land on are never visible to it via a single fetch + single API call. The recommendation is to promote to B3 (two-pass): state index → model picks title → fetch that title's page → model proposes chapter URLs from the title-level snapshot.

A side finding from the WY canary was a HEAD-check defect in the previous canary's verification code — UA + Range alone is sufficient for some Justia paths (the WY ground-truth chapter URL) but not others (the title-index page). Fixed by extending `head_check` to the same rich-header set as the fetcher. Initial WY B2 run misreported the proposed URL as 403/DEAD until the fix landed.

## Topics Explored

- Adding `{state_index}` placeholder + Rule 6 to the discovery prompt template
- Adding `state_index: str = ""` kwarg to `_format_prompt` and `discover_urls_for_pair` while preserving backward compatibility for index-free templates (str.format ignores unused kwargs)
- Anti-bot characterization of Justia: plain GETs 403 even with browser UA; Range-GETs (`bytes=0-65535`) get 206 with the full state-year index in the first chunk
- WY 2010 B2 canary execution (~$0.025; 1 URL proposed; 0 statute-leaf hit)
- FL 2010 B2 canary execution (~$0.025; 1 URL proposed; 0 statute-leaf hit out of 6 ground-truth URLs); ground truth constructed live by inspecting `TitleIII/chapter11/chapter11.html` for the lobbying chapter sections
- Whether B2's "right idea, wrong depth" failure is WY-specific or universal

## Provisional Findings

- **Mode 1 (URL casing) — fixed by construction.** Model copies `Title28`/`TitleIII` literally from the snapshot. The lowercase variant that B1 produced no longer appears.
- **Mode 2 (invented section URLs) — fixed via Rule 6 conservatism, not via correct extrapolation.** Model explicitly notes "to avoid hallucinated deeper paths" and stops at the title-index page.
- **Statute-leaf hit rate is 0 / N across both states.** WY 0/1 (single chapter-leaf statute body); FL 0/6 (per-section leaf statute body). Same outcome despite very different statute structures.
- **FL's model output names the right chapter and section by number** ("Chapter 11 (Legislative Organization, Procedures, and Lobbyists) ... 11.045 (lobbyist registration)") while refusing to emit them as URLs — strongest possible evidence that Rule 6 is working as designed and the architecture, not the prompt, is the ceiling.
- **Token budget came in at ~1k snapshot tokens, not the diagnostic's ~10k worst-case estimate.** Per-call cost ~$0.025 — full 350-pair B2 fan-out would be ~$10–14.
- **Justia anti-bot is path-specific.** Some chapter-leaf URLs (the ground-truth for WY) tolerate UA + Range alone; title-index pages need the full Accept/Accept-Language/Connection set. Verification correctness now standardized to the richer set in `head_check`.

## Decisions Made

- Prompt template v2 landed (commit `8d9b86c`): `{state_index}` placeholder section + Rule 6 forbidding extrapolation beyond the snapshot.
- `api_retrieval_agent.py` extended with optional `state_index` kwarg on the single-pair surface (`_format_prompt` + `discover_urls_for_pair`). Batch surface (`discover_urls_for_pairs`) intentionally not extended yet — full fan-out is gated on B2 vs B3 decision, no point widening the API before architecture is settled.
- Canary script parameterized by `CANARY_TARGET` env var for multi-state runs; remains gitignored per B1 policy.
- HEAD-check header set standardized to match the fetcher's; verification correctness now decoupled from per-path anti-bot heuristics.
- **B2 alone is not sufficient.** Promote to B3 (two-pass discovery: state index → model picks title → fetch that title's page → model proposes chapter URLs from the title-level snapshot).

## Results

- [`results/20260514_wy2010_b2_index_inline_hit_rate.md`](../results/20260514_wy2010_b2_index_inline_hit_rate.md) — WY 2010 B2 canary, 0/1 statute-leaf hit, surfaces architecture + Rule 6
- [`results/20260514_fl2010_b2_index_inline_hit_rate.md`](../results/20260514_fl2010_b2_index_inline_hit_rate.md) — FL 2010 confirmation, 0/6 statute-leaf hit, model names Ch.11/§11.045 in narrative but won't emit them

## Open Questions

- **B3 prompt design:** does pass 2 reuse the same Rule 6 unchanged, or does it need a softer wording? Within a single title page the model has more legitimate reason to extrapolate (e.g., from a chapter-list to per-section leaves Justia clearly exposes), but the failure mode we just fixed was extrapolation. Need to think about whether Rule 6 should be pass-specific.
- **B3 pass-2 input shape:** is the right input "the full title page link list" (like the B2 state-index snippet) or "the title page link list + chapter context the model selected on pass 1"? The latter is more focused; the former is more honest.
- **Recovery from a wrong pass-1 pick.** If the model picks the wrong title, B3's second fetch is on a useless page. Three possible answers: (a) trust the model and accept the rare miss; (b) propose top-2 titles on pass 1 and fetch both; (c) include "wrong-title" detection in pass 2 with a re-pick mechanism. (a) is simplest; (b)/(c) are YAGNI until we see a real failure.
- **HG 2007 split-vintage pairs.** The plan's HG 2007 entry was "two bundles per state (2002/ and 2007/)" — does B3 fan out across both, or only against the target year? Already settled in the kickoff plan (two bundles); flagging here to confirm B3 inherits.
- **Should `scripts/canary_*.py` be gitignored explicitly?** Carried over from B1; still open.

## Next Steps

- Write B3 implementation plan (this is the immediate next step)
- Implement B3 test-first per the plan
- Re-canary WY 2010 + FL 2010 against B3 to confirm statute-leaf hit rate improves
- If B3 hit rates are acceptable across both pilot states, canary 2–3 more pilot states at 2010 + 2015 to spot-check generalization before the full 350-pair fan-out

# B4 parser hardening: try/except + prompt strengthening + AR/WV re-canary

**Date:** 2026-05-15
**Branch:** `api-multi-vintage-retrieval`
**Picked up from:** `2a20284` (prior session's Chunk 6 finish-convo)
**Originating context:** [`results/20260515_b4_10pair_canary.md`](../results/20260515_b4_10pair_canary.md) — surfaced Defect 1 (`JSONDecodeError` on prose-only responses) blocking full fan-out.
**Cumulative API spend this session:** $0.20 ($0.06 AR + $0.11 WV + $0.024 WY regression check)

---

## What we did

The 10-pair canary on 2026-05-15 surfaced two defects gating fan-out. The user picked items 1-3 from the suggested remediation list:

1. **Parser hardening (TDD).** Add try/except around `json.loads` in `_parse_response_text` and `_parse_pass1_response`. On `JSONDecodeError`, return empty list + a schema-violations entry recording the failure + availability marker `justia_unavailable=True` with a 200-char prose preview in `notes`. Routes the pair to manual review instead of crashing.
2. **Pass-1 prompt strengthening.** Rewrite Rule 3 to explicitly route the soft-refusal mode through the JSON shape — the existing prompt told the model "JSON only" multiple times but inadvertently authorized prose via "better to return nothing than to guess." The fix: explicit JSON example for the no-titles branch + framing that empty-list-with-`justia_unavailable: true` IS the honest answer.
3. **Re-run AR + WV canary** against real API to validate the fixes in production.

Items 4 (WA/CO ground truth) and 5 (concurrency decision) deferred.

---

## Sequence

### Step 1 — RED tests for both parsers

Added three new tests:

- `test_parser_degrades_gracefully_on_prose_only_response` (test_api_retrieval_agent.py): exercises `_parse_response_text` against a realistic prose-only fixture matching the documented crash mode. Asserts empty parsed list + schema_violations entry starting with "non-JSON response:" + availability with `justia_unavailable=True` and bounded-length notes preview.
- `test_parser_degrades_gracefully_on_empty_response` (test_api_retrieval_agent.py): degenerate variant — empty string input. Same contract.
- `test_pass1_parser_degrades_gracefully_on_prose_only_response` (test_api_retrieval_agent_b3.py): mirror coverage for `_parse_pass1_response`.

All three went RED with the exact `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` exception that AR/WV produced in the 10-pair canary log — reproduced the crash deterministically with synthetic fixtures.

### Step 2 — GREEN fix in `src/scoring/api_retrieval_agent.py`

Extracted a shared helper `_unparseable_response_fallback(text) -> tuple[violations, availability]` so both parsers route through one place. Truncation cap `_PROSE_PREVIEW_CHARS = 200`. Wrapped both `json.loads` call sites (lines 144, 388 post-edit) in try/except. The two callers consume the helper's return tuple in different orders to match their existing public return signatures.

Confirmed GREEN on all 26 tests in the agent suite (23 prior + 3 new). No regressions in B3PW or B4 orchestrators.

### Step 3 — Prompt update with format-string footgun

Rewrote Rule 3 in `src/scoring/api_seed_discovery_pass1_prompt.md` from "better to return nothing than to guess" to explicit JSON-shape-is-the-honest-answer framing. Added an inline JSON example.

**Caught a self-inflicted bug on first canary attempt:** the prompt is loaded via `str.format(state=..., vintage=..., state_index=...)`, which interprets literal `{...}` as format placeholders. The pre-existing schema block at the top of the prompt correctly escapes braces (`{{ "chosen_titles": ... }}`); my new example was unescaped, so `template.format(...)` raised `KeyError: '"chosen_titles"'` before any API call even fired. Fixed by escaping the example's braces. Added a regression test `test_pass1_prompt_template_renders_without_keyerror` that renders the production prompt with typical inputs — would have caught this in CI rather than on a real-API canary.

### Step 4 — AR + WV re-canary (real API, real Justia)

| State | Wall | Cost | Pass-1 titles | Pass-2 chapters | Pass-3 calls | Final URLs | Outcome |
|---|---|---|---|---|---|---|---|
| AR 2010 | 58.9s | $0.060 | 2 (Title 21 Public Officers + Title 10 General Assembly) | 2 | 1 | 5 | No crash — model found Title 21 Ch. 8 ethics regime + fanned to subchapters 1/4/5/6 |
| WV 2010 | 79.2s | $0.113 | 1 (Chapter 6B Ethics Act) | 3 (articles 1/2/3) | 3 | 27 | No crash — model found Chapter 6B Article 3 lobbyists + Article 2 ethics commission + Article 1 definitions |

**Both states went from `JSONDecodeError` crash → productive output.** The model now correctly identifies AR's lobbying regime as Title 21 Public Officers / Chapter 8 Ethics (consistent with Ark. Code §§ 21-8-101 et seq.) and WV's as Chapter 6B Ethics Act / Article 3 Lobbyists (consistent with W. Va. Code §§ 6B-3-1 et seq.).

Without curated GT we can't measure recall, but the structural outputs look plausible enough to add to the manual-validation queue.

### Step 5 — WY regression check

The prompt change is theoretically additive (only strengthens the no-titles branch), but the safest validation is to confirm it doesn't degrade a known-positive case. WY 2010 was the cheapest pilot at $0.024 / 26.9s. **Result: 1/1 GT-hit, $0.024, 26.9s — identical to Chunk 3's outcome.** Pass-3 skipped correctly (chapter7.html is a leaf). Prompt change confirmed neutral on positive cases.

---

## Trajectory of thinking

The handoff framed the prompt update as "incrementally nicer but lower-priority" — parser hardening was the load-bearing safety net. I echoed that framing in my pre-work briefing: "the prompt update is belt-and-suspenders, not a primary fix."

**That framing was wrong.** The AR + WV re-canary results show the prompt update moved the model from soft-refusal-as-prose to productive multi-title engagement. Without the parser hardening, the runs would still have succeeded (no prose to crash on — the model returned valid JSON). The parser hardening is the safety net for the *next* unanticipated prose-mode trigger; the prompt update is what actually changed AR/WV outcomes from "crash" to "useful data."

Both fixes were necessary, but for different reasons:
- **Prompt update:** load-bearing improvement to *model behavior* — pushed the model from soft-refusal to engagement on hard states. Lifted productive output rate.
- **Parser hardening:** durable defensive layer against *any* future non-JSON response from any model version, any prompt shape, any failure mode. Caps blast radius.

The "belt-and-suspenders" framing undervalued the prompt update by ~one order of magnitude in observed impact. Worth recalibrating: prompt fixes can have outsized effects on model behavior even when the prompt already says "JSON only" five different ways — the *framing* of the no-match branch matters as much as the *instruction* about the no-match branch.

## Decisions

- **Shared `_unparseable_response_fallback` helper** rather than inline try/except at both sites. Two callers, one truncation policy, one preview-format string — DRY is correct here.
- **`justia_unavailable=True` on parse failure** routes the pair to the manual-review log instead of the retry log. The call completed; the issue is response shape, not transient API state. Retries on the same prompt will produce more prose, not JSON.
- **200-char preview cap** for both `schema_violations.reason` and `availability.notes`. Long enough to diagnose; short enough to keep checkpoints small. Tested with an explicit `len(notes) <= 300` bound (300 to leave headroom for the "non-JSON response: " prefix in the violation reason).
- **AR + WV added to `SINGLE_PAIR_TARGETS`** with `ground_truth: []` — they become permanent graceful-degrade regression rails. (Note: `scripts/canary_discovery.py` is untracked-but-not-gitignored, so this addition is machine-local; if the canary script ever gets committed, AR/WV stay with it.)
- **Added prompt-template renderability test** as a regression rail for the `str.format()` footgun. Cheap and exactly the kind of test that pays for itself the next time someone edits the prompt.
- **WY regression check after prompt edit** — defensive due diligence. Could've skipped (the change is structurally additive), but $0.024 + 30s for confirmation is the right ratio.

## Open questions handed back to the user

The remaining items from the post-canary punch list are unchanged by this session:

1. **Defect 2 (silent-empty WA/CO):** unchanged — no GT added. The post-fix canaries didn't exercise WA or CO; their silent-empty behavior remains undecidable. Recommend a manual GT pass on at least one of WA/CO before fan-out (per item 4 of the original suggested order).
2. **Concurrency model:** unchanged. With Defect 1 fixed, the safety blocker for parallel fan-out is gone, but the wall-time data hasn't changed (~7h sequential at observed mean). User's call when to land this decision.
3. **Cost projection refresh:** AR ($0.060) + WV ($0.113) are now baseline-comparable to other states. The 10-pair mean was $0.083; including the post-fix AR/WV runs nudges the mean slightly. Still in the $25-30 range for full fan-out — same order of magnitude as the plan's $21 estimate. Recommend folding this into the plan's projection if/when fan-out is greenlit.

## What worked well

- **TDD on the AR/WV crash bytes** caught the contract clearly. Synthetic prose fixture reproduced `JSONDecodeError` deterministically; once GREEN, the same try/except handled real-API responses cleanly without re-architecting anything.
- **Catching the prompt-template footgun on the first canary attempt** rather than mid-fan-out. The `KeyError: '"chosen_titles"'` was loud and immediate; the regression test means the next prompt edit won't repeat it.
- **Defensive WY re-canary** turned out to be cheap and ruled out a hypothetical regression — small cost, high information value.

## What I'd do differently

- **Pre-work framing on the prompt update.** I told the user "minor belt-and-suspenders, zero-risk." The change had outsized impact (moved AR/WV from crash to productive output) AND introduced a real bug (the unescaped braces). Neither part of that "minor zero-risk" framing was accurate. Calibrating prompt changes as load-bearing-by-default would be more honest.
- **Should have written the prompt-template renderability test BEFORE editing the prompt**, not after. TDD-on-prompt-edits is the correct discipline; I retrofitted the test, which means the canary served as the unit test in the meantime.

## Pre-existing test failures (out of scope)

`pytest tests/` shows 338 passed, 3 failed. All 3 failures are in `test_pipeline.py` and trace to missing `data/portal_snapshots/CA/2026-04-13/manifest.json` — pre-existing data-loss from the user's laptop crash, documented in the 2026-05-14 kickoff session as "tabled for later in this branch." Not addressable from agent code; would require restoring the snapshot from elsewhere. Surfacing here so it stays visible.

---

## Next steps

The user's original items 4 + 5 from the briefing list remain:

- **Add manual GT for WA or CO** to discriminate silent-correct from silent-wrong (item 4).
- **Pick concurrency model** for fan-out — sequential ~7h vs parallel with the parser now hardened (item 5).

The branch is ready for either, or for fan-out itself once those two are settled.

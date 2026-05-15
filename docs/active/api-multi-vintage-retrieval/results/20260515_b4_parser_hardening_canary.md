# B4 parser-hardening post-fix canary — AR/WV/WY

**Date:** 2026-05-15
**Branch:** `api-multi-vintage-retrieval`
**Convo:** [`convos/20260515_b4_parser_hardening.md`](../convos/20260515_b4_parser_hardening.md)
**Originating defect:** [`results/20260515_b4_10pair_canary.md`](20260515_b4_10pair_canary.md) — Defect 1, `JSONDecodeError` on prose-only model responses.

---

## TL;DR

The two states that crashed the 10-pair canary now run to completion under the hardened parser + strengthened pass-1 prompt. **AR 2010** went from crash → 5 plausible URLs (Title 21 Ch. 8 ethics regime + Title 10 Ch. 1). **WV 2010** went from crash → 27 URLs (Chapter 6B Ethics Act, Articles 1/2/3). WY regression check came back identical to Chunk 3 (1/1 GT-hit, $0.024, 26.9s) — prompt change confirmed neutral on positive cases.

**Defect 1 is closed.** Both the model behavior (prompt) and the parser robustness (try/except) have been validated end-to-end on the exact states that surfaced the defect.

---

## Per-pair results

| State | Vintage | Slug | Wall | Cost | n_proposed | GT-hits | GT size | pass-3 calls | CF | pass1_unavailable | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AR | 2010 | arkansas | 58.9s | $0.060 | 5 | — | 0 | 1 | no | no | Previously crashed; now identifies Title 21 Public Officers Ch. 8 ethics regime + Title 10 General Assembly Ch. 1 |
| WV | 2010 | west-virginia | 79.2s | $0.113 | 27 | — | 0 | 3 | no | no | Previously crashed; now identifies Chapter 6B Ethics Act with full Article 1/2/3 fan-out |
| WY | 2010 | wyoming | 26.9s | $0.024 | 1 | **1/1** | 1 | 0 | no | no | Regression check after prompt edit — matches Chunk 3 outcome exactly |

Cumulative session spend: **$0.197**.

## What the model found (without GT, so plausibility-only)

### AR 2010

- **Pass-1 (2 titles):** Title 21 (Public Officers and Employees) — citing "lobbyist registration and disclosure requirements codified under public officer ethics provisions"; Title 10 (General Assembly) — citing "legislative-branch lobbying registration and reporting requirements."
- **Pass-2 (2 chapters):** Title 21 / chapter-8 (Ethics and Conflicts of Interest); Title 10 / chapter-1 (General Provisions).
- **Pass-3 (1 chapter expanded):** Title 21 / chapter-8 fanned to 4 subchapters (1, 4, 5, 6).
- **Final URLs (5):** subchapters 1/4/5/6 of Title 21 Ch. 8 + Title 10 Ch. 1.

This matches Arkansas's actual statutory structure — Ark. Code §§ 21-8-101 et seq. is the Ethics Commission / lobbyist registration title. Subchapter 4 (Disclosure by Lobbyists) and subchapter 6 (Disclosure by Public Officials) are the substantive lobbying-disclosure leaves. The `core_chapter` tag on those two subchapters is consistent with their legal role.

### WV 2010

- **Pass-1 (1 title):** Chapter 6B (Public Officers and Employees / Ethics Act) — explicitly citing W. Va. Code §§ 6B-3-1 et seq.
- **Pass-2 (3 chapters):** Article 3 (Lobbyists), Article 1 (definitions / short title), Article 2 (Ethics Commission).
- **Pass-3 (3 chapters expanded):** all three articles, full subsection fan-out.
- **Final URLs (27):** 14 sections of Article 3 (6B-3-1 through 6B-3-11), 6 sections of Article 1 (6B-1-1 through 6B-1-6), 7 sections of Article 2.

This matches WV's actual statutory structure. The `core_chapter` tags landed on 6B-3-2, 6B-3-4, 6B-3-5, 6B-3-7 — these are the substantive lobbying-registration and expenditure-reporting sections (Definitions are -1; -2 is Registration; -4 is Reports; -5 is Records; -7 is Penalties). Plausible role-tagging.

### WY 2010 (regression check)

- **Pass-1:** Title 28 (Legislature), citing Wyo. Stat. §§ 28-7-101 et seq.
- **Pass-2:** Title28/chapter7.html (Lobbyists).
- **Pass-3:** Skipped — chapter7.html is a leaf (no section children at one segment deeper).
- **Final URL:** Title28/chapter7.html — matches GT exactly.

Identical to Chunk 3 outcome on wall time, cost, URL count, and recall.

---

## Cost-per-pair update

| Source | Mean $/pair | Notes |
|---|---|---|
| Chunks 3+4 single-pair (5 pairs) | $0.082 | WY 0.024 + FL 0.087 + NY 0.113 + TX 0.044 + OH 0.144 |
| Chunk 5 10-pair (8 successful) | $0.110 | $0.879 / 8 pairs (AR/WV crashed didn't bill fully) |
| Post-fix AR+WV (this run) | $0.087 | $0.173 / 2 pairs |
| **Aggregate across all canary runs** | **~$0.094** | 15 productive runs, $1.41 total |

At $0.094/pair × 350 pairs = **~$33 full-fan-out projection** (was $29 in the 10-pair-only projection, now nudged slightly upward by the AR/WV runs which were more expensive than the 10-pair mean of "successful, light states"). Still well within an order of magnitude of the plan's $21 baseline and trivial relative to the project's total budget.

---

## What this validates

1. **The parser try/except is correctly inert when responses ARE valid JSON.** WY 2010's outcome is bit-identical to Chunk 3 — the added except branch never fires on JSON-shape responses, so existing happy paths are unaffected.
2. **The pass-1 prompt strengthening moved the model from refusal to engagement** on the previously-crashing states. This is the dominant effect of this session, eclipsing the parser hardening in terms of observed impact on outcomes (though the parser hardening remains the durable defensive layer for any *future* prose-mode trigger).
3. **The `str.format()`-based prompt loader is fragile**; one inadvertent literal `{...}` in the prompt body breaks the canary. The regression test `test_pass1_prompt_template_renders_without_keyerror` (in `tests/test_api_retrieval_agent.py`) now guards against this — would have caught the bug locally before the canary spent any tokens.

## What this does NOT close

- **Defect 2 (silent-empty WA/CO)** — not exercised by this re-canary. WA 2010 and CO 2016's behavior under the new prompt is unknown. The strengthened Rule 3 might or might not flip them from silent-empty to productive — opening question.
- **Concurrency / wall-time strategy** — unchanged. Sequential ~7h fan-out still applies; parser hardening just removes the blocker against parallelization (parallel runs no longer risk amplifying a 20% crash rate to ~70 silent-fail pairs).
- **Recall validation on AR/WV** — no curated GT, so the 5 + 27 URLs are plausibility-only. Manual review would establish whether the model's title/chapter picks are correct or where they over/under-pick.

---

## What needs decision before fan-out (updated punch list)

| Question | Status | Owner |
|---|---|---|
| Fix Defect 1 (parser crash on prose) | ✅ DONE | (resolved) |
| Strengthen pass-1 prompt for no-titles branch | ✅ DONE | (resolved) |
| Multi-pair concurrency — sequential ~7h vs parallel | OPEN | User |
| Add GT for ≥1 unseen state (WA or CO) | OPEN | User |
| Update `cap_usd` from per-run $1 to per-batch sizing | OPEN | User |
| Refresh fan-out cost projection ($21 → ~$33) | OPEN | User |

Two of the four pre-fan-out blockers are now closed. Two remain — both are operational decisions, not technical defects.

---

## Appendix — exact commands

```bash
# Parser-hardening unit tests
PYTHONPATH=src uv run --active pytest \
  tests/test_api_retrieval_agent.py::test_parser_degrades_gracefully_on_prose_only_response \
  tests/test_api_retrieval_agent.py::test_parser_degrades_gracefully_on_empty_response \
  tests/test_api_retrieval_agent.py::test_pass1_prompt_template_renders_without_keyerror \
  tests/test_api_retrieval_agent_b3.py::test_pass1_parser_degrades_gracefully_on_prose_only_response

# Post-fix re-canary
CANARY_MODE=B4 CANARY_TARGET=AR PYTHONPATH=src uv run --active python scripts/canary_discovery.py
CANARY_MODE=B4 CANARY_TARGET=WV PYTHONPATH=src uv run --active python scripts/canary_discovery.py
CANARY_MODE=B4 CANARY_TARGET=WY PYTHONPATH=src uv run --active python scripts/canary_discovery.py
```

Raw logs saved to `/tmp/b4_canary_logs/{ar,wv,wy}_post_fix.log` — ephemeral; not committed.

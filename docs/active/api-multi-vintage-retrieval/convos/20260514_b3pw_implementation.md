# B3PW implementation + pilot canaries

**Date:** 2026-05-14
**Branch:** `api-multi-vintage-retrieval`
**Worktree:** `.worktrees/api-vintage`
**Plan:** [`plans/20260514_b3_two_pass_discovery_plan_playwright.md`](../plans/20260514_b3_two_pass_discovery_plan_playwright.md)
**Results:** [`results/20260514_b3pw_pilot_canaries.md`](../results/20260514_b3pw_pilot_canaries.md)

## Summary

User opened the session with "see plans/20260514_b3_two_pass_discovery_plan_playwright.md and let's give it a shot." Session executed Phases 1–4 of the B3PW plan: authored pass-1 and pass-2 prompts; wrote 7 RED behavioural tests for the two-pass orchestrator at the `Client`-protocol mock boundary; implemented `discover_urls_for_pair_two_pass` + `Pass1Pass2Result` + `_parse_pass1_response` + `_build_justia_link_tsv` + cost-tracking + batch orchestrator; got all 7 tests GREEN; ran WY 2010 + FL 2010 canaries against real Anthropic + real Justia under a $1 cumulative-cost cap. User gave mid-session green light for canary spend ("you can actually launch them sequentially, and set a cap so that if anything costs more than $1, you kill it"), so canary work proceeded autonomously while user was on phone.

WY canary: 1/1 ground-truth hit, clean execution. FL canary: 0/6 ground-truth section-leaves, but the failure mode is exactly the "chapter-TOC ceiling" the original B3 plan anticipated — pass-1 correctly identified both parallel statute regimes (TitleIII/Ch.11 + TitleX/Ch.112); pass-2 correctly picked the right chapter URLs; the section bodies live one hop deeper than the title-page snapshot exposes. The plan explicitly said this outcome should be surfaced to the user before further work, so the canary loop stopped after FL. Cost spent: ~$0.07 of $1 cap.

Three pre-existing defects surfaced and were fixed during canary work (all three with new unit tests so they don't regress).

## Topics Explored

- Authoring pass-1 (title-picker, narrow output schema) and pass-2 (URL-proposer, evolution of B2 prompt with `{chosen_title_rationale}` carry-forward) prompts
- 7 RED behavioural tests via FakeAsyncClient (Anthropic) + FakeJustiaClient (`Client` protocol) — no `respx`, no http-layer mocks
- `Pass1Pass2Result` dataclass + `_parse_pass1_response` parser + `_build_justia_link_tsv` TSV-formatter helper + async/sync bridge via `asyncio.to_thread`
- `CostTracker` with conservative Sonnet pricing ($3/M in, $15/M out, no cache discount) and a hard `cap_usd` that raises `CostCapExceeded`
- WY 2010 canary against real APIs — surfaced and fixed the `Foo/Foo.html`-pattern defect in the TSV helper
- FL 2010 canary — surfaced and fixed the terse-anchor-text defect (sibling-`<td>` subject names)
- FL 2010 second canary — surfaced and fixed the pass-1 prompt's over-conservative single-title bias
- FL 2010 third canary — surfaced the "chapter-TOC ceiling" the original B3 plan anticipated; verified via `parse_statute_text` probe that `chapter11.html` is a section TOC, not a statute leaf

## Provisional Findings

- **B3PW is structurally sound.** WY 2010 (single-chapter-leaf state) hit 1/1 ground truth cleanly. The two-pass discovery architecture, the PlaywrightClient HTTP layer, the prompt + parser plumbing, and the cost guard all worked correctly on first real-API invocation.
- **The chapter-TOC ceiling is real for FL-shaped states.** Pass-2 lands on the right chapter URL (e.g., `chapter11/chapter11.html`) but that page is a section TOC — section bodies (the actual ground truth) require one more hop. Pre-canary, this was the principal open question; FL's 0/6 confirms it. The original B3 plan explicitly framed this as the trigger for a B4 design discussion.
- **The model can read section TOCs correctly** — pass-2's narrative on FL `chapter11.html` named all 6 ground-truth section numbers (11.045, 11.0451, 11.0455, 11.047, 11.061, 11.062) even though Rule 6 prevented it from emitting them as URLs (they weren't in the snapshot). Suggests B4 three-pass would close the gap cleanly without prompt-tuning.
- **Multi-title pick is essential for split-regime states.** FL splits its lobbying disclosure across TitleIII (legislative branch) and TitleX (executive branch / ethics). The original pass-1 prompt's "prefer single title" framing prevented the model from picking both even when its own narrative identified the split. Rewriting Rule 2 to make multi-pick explicit on parallel regimes fixed this.
- **TSV anchor enrichment is essential for Roman-numeral states.** FL's state-year-index uses `<td><a>TITLE III</a></td><td>LEGISLATIVE BRANCH; COMMISSIONS</td>` — anchor alone is uninformative. Walking up to the `<tr>` ancestor picks up the subject name. WY's `<li>` anchor was already informative, so this was a FL-shape-specific defect that wouldn't have surfaced if only WY had been canaried.
- **`Foo/Foo.html` is the WY state-year-index pattern, not just a title-page pattern.** Originally I assumed it only appeared at the title-page level (where Pattern 2 applies); WY's state-year-index actually uses it too. The directory-parent code path now accepts this narrow exception.
- **Cost projections were conservative.** Reported cost ($0.07) used $3/$15-per-M pricing; actual is lower. Cost cap mechanism never came close to triggering — the $1 budget has ~10× headroom for additional canary iterations.
- **No anti-bot incidents.** PlaywrightClient handled 5 distinct Justia URLs across both canaries in <60s wall time. The Cloudflare-challenge risk the plan worried about did not materialize at this scale.

## Decisions Made

- **Convo name:** `20260514_b3pw_implementation` (user implicitly accepted by saying "great, do what you can and then push").
- **Cost cap of $1.00** with conservative pricing — user-approved mid-session.
- **B3PW orchestrator surface frozen** per the plan: 7 tests carried forward unchanged from original B3 plan; `discover_urls_for_pair_two_pass` / `Pass1Pass2Result` / `_parse_pass1_response` / `_build_justia_link_tsv` / batch orchestrator at concurrency cap 4.
- **Pass-1 prompt Rule 2 rewritten** to encourage multi-title picks on parallel regimes. Answers Question #1 from the plan ("Should pass-1 prompt cap multi-title picks at 2?"): no cap; explicit multi-pick framing for parallel regimes.
- **`_build_justia_link_tsv` handles 3 Justia parent-page patterns**: directory, `Foo/Foo.html`, `foo.html`. Anchor description enriched via parent-row text walk-up for `<tr>` / `<li>` / `<dt>` containers.
- **Canary loop stopped at FL** per the plan's step 26: "If B3 hit-rate is <50% on FL (chapter-TOC ceiling), surface a B4 design discussion before further work."
- **10-pair canary deferred** until user decides on B3 vs B4 vs hybrid heuristic.

## Open Questions

- **B3 vs B4 vs heuristic chapter→sections expansion** — three options laid out in detail in [`results/20260514_b3pw_pilot_canaries.md`](../results/20260514_b3pw_pilot_canaries.md) §"What this leaves open." This implementer's recommendation is Option B (three-pass), but the user owns the call — it's an architecture decision, not an implementation detail.
- **Cross-vintage URL pattern stability** (Question #3 from the playwright plan) — untested this session because the canaries were 2010-only. WY 2010 → 2025 URL templating could compress 7-vintage fan-out by 6× if Justia's URLs are stable. Worth testing once B3-vs-B4 is resolved.
- **NY / TX / OH single-pair canaries** — would help characterize how widespread the chapter-TOC ceiling is. If TX and NY are CA-style range-leaves (single hop from title to statute body), the ceiling is FL-specific; if NY/OH also hit the ceiling, B4 is unambiguously the right call.
- **Whether the chapter-TOC page's section-title list is useful as a downstream extraction artifact** — `parse_statute_text` on `chapter11.html` returned 5 KB containing all the section titles. Could downstream extraction read section names from there + fetch each section leaf opportunistically? That's effectively Option C (hybrid).
- **Whether to keep the WY canary's chapter-leaf as a separate "GT-clean" anchor** even after B4 lands — i.e., should B4 short-circuit when pass-2 confidently picks a single chapter leaf, or always go three-pass for uniformity? Plan deferred this.

## Next Steps

- **Wait for user input on B3 vs B4.** This is a real architecture decision that the canary surfaced exactly as the plan said it would. Per the plan: "surface a B4 design discussion before further work — the structural cost of three-pass may be worth it, but the user should weigh in."
- **If user picks B4:** new plan doc (`plans/20260515_b4_three_pass_discovery_plan.md` or similar), 4–6 new tests (single chapter, multi-chapter dedup, chapter-TOC vs full-text chapter detection, failure isolation), implementation extending the existing two-pass orchestrator with a third pass, re-canary FL + add NY/TX/OH.
- **If user picks Option A or C:** smaller implementation — add a children-enumeration step after pass-2 either in the batch orchestrator or in the downstream extraction pipeline.
- **If user wants more diagnostic data first:** run single-pair canaries on NY 2010 + TX 2009 + OH 2010 (~$0.07 total) to map the chapter-TOC ceiling's prevalence before committing to an architecture.
- **Sister-branch reminder:** `phase-c-projection-tdd` consumes the audit CSV's vintage table independently of this discovery work, so the B3-vs-B4 decision doesn't gate calibration progress — just multi-vintage retrieval.

## Files added / changed this session

Code:
- `src/scoring/api_seed_discovery_pass1_prompt.md` (new)
- `src/scoring/api_seed_discovery_pass2_prompt.md` (new)
- `src/scoring/api_retrieval_agent.py` — new symbols only; existing B2 surface untouched
- `tests/test_api_retrieval_agent_b3.py` (new, 9 tests: 7 orchestrator + 2 helper)
- `scripts/canary_discovery.py` — gitignored; rewritten for B3PW + B3PW_10PAIR modes

Docs:
- `docs/active/api-multi-vintage-retrieval/results/20260514_b3pw_pilot_canaries.md` (new)
- `docs/active/api-multi-vintage-retrieval/convos/20260514_b3pw_implementation.md` (this file)
- `docs/active/api-multi-vintage-retrieval/RESEARCH_LOG.md` — new session entry
- `STATUS.md` — one-line entry in Recent Sessions

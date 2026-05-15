# B4 Three-Pass Discovery Implementation Plan

**Goal:** Extend B3PW's two-pass orchestrator with a **third pass** that lands the model on actual statute section-leaf URLs for states whose title pages expose chapter-TOC URLs (not chapter-leaves). Pass-3 fetches the chapter-TOC page and prompts the model to pick the in-scope section URLs from its children. For chapters that ARE the leaf (no deeper children), pass-3 is skipped and pass-2's chapter URL is the final answer.

**Originating conversation:** [`docs/active/api-multi-vintage-retrieval/convos/20260514_b3pw_implementation.md`](../convos/20260514_b3pw_implementation.md)

**Originating result:** [`docs/active/api-multi-vintage-retrieval/results/20260514_b3pw_pilot_canaries.md`](../results/20260514_b3pw_pilot_canaries.md) — WY/FL canaries surfaced the "chapter-TOC ceiling" exactly as the original B3 plan predicted. User decision: pursue **Option B (three-pass)**.

**Supersedes for fan-out purposes:** B3PW (two-pass). B3PW's orchestrator (`discover_urls_for_pair_two_pass`) is preserved unchanged as a backstop and as the inner-stage building block — B4 calls into the same pass-1 and pass-2 logic.

**Branch:** `api-multi-vintage-retrieval` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/api-vintage`)

**Tech stack:** unchanged from B3PW — `anthropic.AsyncAnthropic`, `playwright` via `PlaywrightClient`, `pytest` + `pytest-asyncio`, Python 3.12 + `uv`. The pass-2 prompt is **reused for pass-3** because its Rule 6 wording already handles "propose the URLs that constitute the statute body — could be a single chapter-leaf, multiple per-section leaves, or a chapter-level TOC." Only the snapshot scope changes (chapter page vs title page).

---

## Architectural delta from B3PW

| Stage | B3PW | B4 |
|---|---|---|
| Pass 1 | state-year index → pick title(s) | unchanged |
| Pass 2 | title page → pick statute URL(s) — final | title page → pick chapter URL(s) — provisional |
| Adaptive step | n/a | for each chapter URL, fetch and probe children via `_build_justia_link_tsv`. **No children → chapter IS the leaf; add to `parsed_urls` directly.** **Children present → run pass-3.** |
| Pass 3 | n/a | chapter page → pick in-scope section URL(s) — final. Reuses pass-2 prompt with the chapter rationale + chapter-page snapshot. |

The adaptive children-probe is **deterministic** (no LLM judgment) — it just runs `_build_justia_link_tsv(chapter_html, chapter_url)` and branches on emptiness. This keeps WY-style single-chapter-leaf states working without prompt-tuning (their chapter page has no deeper children, so pass-3 is skipped and we hit the GT URL on pass-2 exactly as before).

### Why reuse the pass-2 prompt

The pass-2 prompt's Rule 6 is depth-agnostic — it talks about "the URLs that constitute the statute body" within whatever snapshot is provided. A chapter-page snapshot showing 50 section URLs is the same shape of input to the model as a title-page snapshot showing 20 chapter URLs. The model's job is identical: filter to in-scope, return what's exposed.

The only adjustment: when invoking pass-3, the orchestrator passes the **chapter rationale** (from pass-2's `ChosenChapter`) into the `{chosen_title_rationale}` placeholder instead of the title rationale. The prompt template doesn't care which.

This is YAGNI-aligned — a new pass-3 prompt would be ~95% copy-paste of pass-2 with only the framing-paragraph language changed. Reusing pass-2 keeps prompt drift singular.

---

## New surface area in `api_retrieval_agent.py`

- `ChosenChapter` dataclass (mirror of `ChosenTitle`): `url`, `rationale`, Justia-hostname enforcement at `from_raw`.
- `Pass1Pass2Pass3Result` dataclass — extends `Pass1Pass2Result`'s shape with:
  - `chosen_chapters: list[ChosenChapter]` — flat list across all titles
  - `pass3_prompts: list[dict]` — per-chapter `{url, prompt, response}`
  - `chapter_fetch_failures: list[dict]` — per-chapter `{url, error, retrieved_at}`
  - `parsed_urls: list[ProposedURL]` — union of pass-2 leaves (no-children chapters) + pass-3 sections
- `discover_urls_for_pair_three_pass(...)` — single-pair orchestrator. Same kwargs as `discover_urls_for_pair_two_pass`, returns `Pass1Pass2Pass3Result`.
- `serialize_pass1_pass2_pass3_result` / `deserialize_pass1_pass2_pass3_result` — checkpoint round-trip.
- `discover_urls_for_pairs_three_pass(...)` — batch surface mirroring `discover_urls_for_pairs_two_pass`. Default concurrency cap **4** (unchanged from B3PW; the extra Playwright fetches per pair come at the per-pair level, not the batch level).

`discover_urls_for_pair_two_pass` and `Pass1Pass2Result` are **preserved unchanged** — three-pass internally invokes the same pass-1 + pass-2 logic via shared private helpers (extracted in this plan if not already factored). B3PW's 7 tests remain GREEN throughout.

---

## Testing plan — 5 new behavioural tests

All in a new `tests/test_api_retrieval_agent_b4.py`. Same mock boundary as B3PW: `FakeAsyncClient` for Anthropic, `FakeJustiaClient` for HTTP. Pass-1 / pass-2 / pass-3 distinguished by marker line in the prompt body (`PASS_1` / `PASS_2` / `PASS_3` — pass-3 requires its own marker since the template is shared with pass-2). Actually, since pass-3 reuses the pass-2 prompt template, the **caller must inject the PASS_3 marker** into the rendered prompt for tests — simplest: render the template, then string-replace `PASS_2` → `PASS_3` before calling Anthropic. The production code does NOT need to do this; only the tests' FakeAsyncClient differentiates by marker. **Cleaner alternative:** add a `_pass_marker` kwarg to the template, default empty. The pass-2 prompt's content stays the same; only the discriminator changes. I'll go with the kwarg.

1. **`test_three_pass_skips_pass3_when_chapter_has_no_children`** — WY-shape. Pass-1 picks title; pass-2 picks `chapter7.html`; helper probes its HTML, finds no children; orchestrator skips pass-3; `parsed_urls` contains exactly the chapter URL. Asserts Anthropic was called twice (no pass-3 call) and `pass3_prompts` is empty.

2. **`test_three_pass_runs_pass3_when_chapter_has_children`** — FL-shape. Pass-1 picks title; pass-2 picks `chapter11/chapter11.html`; helper finds children (`11_045.html`, `11_062.html`, plus unrelated `11_011.html`); pass-3 picks the lobbying subset; `parsed_urls` contains exactly those subset URLs. Asserts Anthropic was called 3 times, `pass3_prompts` has one entry.

3. **`test_three_pass_fans_out_across_multiple_chapters`** — multi-chapter case (Title III/Ch.11 + Title X/Ch.112 from FL). Both chapters have section children; pass-3 runs twice; `parsed_urls` is the dedup'd union.

4. **`test_three_pass_isolates_chapter_fetch_failure`** — pass-2 returns two chapter URLs; one chapter-page fetch raises; pass-3 runs once (on the surviving chapter); `chapter_fetch_failures` records the failed one with its error.

5. **`test_three_pass_pair_checkpoint_records_all_three_passes`** — checkpoint round-trip. Asserts pass1_prompt/response, pass2_prompts (with chosen_titles), pass3_prompts (with chosen_chapters), chapter_fetch_failures, parsed_urls all serialize and deserialize cleanly.

No new unit test for the batch orchestrator — same delegation rationale as B3PW (batch is a thin wrapper around the single-pair orchestrator + the existing failure-isolation / availability / resume scaffolding).

---

## Steps

### Phase 0 — Setup
1. Read this plan + the [B3PW canary results doc](../results/20260514_b3pw_pilot_canaries.md). Understand which pieces carry forward unchanged (pass-1 + pass-2 logic, prompts, TSV helper, cost tracker, batch scaffolding).
2. Confirm worktree clean. `git -C /Users/dan/code/lobby_analysis/.worktrees/api-vintage status` clean modulo gitignored `scripts/canary_discovery.py` + `data/` symlink.
3. Run existing test suite. `PYTHONPATH=src uv run --active pytest tests/test_api_retrieval_agent.py tests/test_api_retrieval_agent_b3.py tests/test_justia_client.py -q` — expect 39 + N passing.

### Phase 1 — Tests (all 5 first, RED)
4. Create `tests/test_api_retrieval_agent_b4.py`. Reuse `FakeAsyncClient` + `FakeJustiaClient` patterns from B3's test file. Add a `PASS_3` marker recognition path.
5. Write tests 1–5 in order; run after each to confirm RED.
6. Run the file; all 5 should fail with `ImportError` on `discover_urls_for_pair_three_pass` / `Pass1Pass2Pass3Result` / `ChosenChapter` etc.

### Phase 2 — Implementation
7. Add `ChosenChapter` dataclass + `Pass1Pass2Pass3Result` dataclass.
8. Add `discover_urls_for_pair_three_pass(...)` orchestrator. Behavior:
   1. Same pass-1 + pass-2 flow as `discover_urls_for_pair_two_pass`, but treat pass-2's URLs as **provisional `ChosenChapter` objects** instead of final `ProposedURL` objects. Store them in `chosen_chapters`.
   2. For each chosen chapter:
      a. Fetch the chapter page via `_fetch_via_client`.
      b. On exception: log to `chapter_fetch_failures` and continue.
      c. Build the children TSV via `_build_justia_link_tsv(chapter_html, chapter_url)`.
      d. If the TSV is empty: the chapter IS the leaf. Add a `ProposedURL` for it to `parsed_urls`.
      e. If the TSV is non-empty: render the pass-2 prompt with `chosen_title_rationale = chapter.rationale` and `state_index = children TSV`. Inject the PASS_3 marker. Call Anthropic. Parse via `_parse_response_text`. Add results to `parsed_urls` (dedup on `(url, role)`).
9. Add `serialize_pass1_pass2_pass3_result` / `deserialize_pass1_pass2_pass3_result`.
10. Run tests one at a time; fix defects. Each green commits.
11. Add `discover_urls_for_pairs_three_pass(...)` batch orchestrator — mirrors B3PW's batch surface; calls the three-pass single-pair orchestrator internally.

### Phase 3 — Re-canary FL with B4
12. Update `scripts/canary_discovery.py` to add a `CANARY_MODE=B4` mode (also `B4_10PAIR` for the next phase). Mode dispatches to `discover_urls_for_pair_three_pass`. Cost cap unchanged at $1.
13. Run `CANARY_MODE=B4 CANARY_TARGET=FL`. Expected outcome: pass-1 picks TitleIII + TitleX (same as B3PW); pass-2 picks chapter11 + chapter112; pass-3 picks the 6 GT section URLs from chapter11 + the relevant Ch.112 section URLs. Hit rate ≥4/6 on Ch.11 GT, ideally 6/6.
14. Run `CANARY_MODE=B4 CANARY_TARGET=WY`. Expected: pass-3 is skipped (WY chapter7.html has no children); `parsed_urls` = `[chapter7.html]`. **Regression-prevents WY's B3PW 1/1 hit.**
15. Document both in `results/20260515_b4_pilot_canaries.md`.

### Phase 4 — Diagnostic single-pair canaries
16. Run B4 against NY 2010, TX 2009, OH 2010 — single-pair each. Goal: characterize how the chapter-TOC ceiling distributes across pilot states.
    - NY: single-page codified act (`rla/`). Expected: pass-2 picks `rla/`; chapter-probe finds children if NY 2010 exposes per-section leaves under `/rla/`, otherwise pass-2 URL is the answer. Hit rate vs `LOBBYING_STATUTE_URLS[("NY", 2010)] = ["https://law.justia.com/codes/new-york/2010/rla/"]` is the test.
    - TX: directory-style chapter (`chapter-305-registration-of-lobbyists/`). Expected: pass-2 picks the chapter directory URL; children probe finds section URLs underneath; pass-3 picks them (TX has a single chapter purely for lobbying, so all children are in-scope). Hit rate vs `LOBBYING_STATUTE_URLS[("TX", 2009)]` = full directory hit.
    - OH: nested title/chapter with underscore-section leaves. Expected: pass-1 picks title1 (or wherever lobbying lives); pass-2 picks chapter101 + chapter121 (split regime); pass-3 picks the 30 section URLs. Hit rate vs `LOBBYING_STATUTE_URLS[("OH", 2010)]` = subset of the 30 hit.
17. Document in same results file.

### Phase 5 — 10-pair canary
18. If Phase 3+4 surface no anti-bot incidents and ≥80% aggregate GT hit rate across the 5 pilot states (CA/TX/NY/WI/WY), run the 10-pair pre-fan-out canary with B4. 5 pilots + 5 unseen (AK/WA/CO 2016/AR/WV). Cost projection: ~$0.70 at $0.07/pair × 10. Wall time: ~7–10 minutes with 4-way concurrency. Cost cap stays at $1 — if exceeded, abort.
19. Document in `results/20260515_b4_10pair_canary.md`. Aggregate hit rate, anti-bot incidents, wall-time p50/p95, per-pair table.

### Phase 6 — Docs + commit
20. Update RESEARCH_LOG.md with a new top-of-log entry covering Phases 1–5.
21. Update STATUS.md with one-line entry in Recent Sessions + adjust api-multi-vintage-retrieval row's Status column.
22. Commits in 3–5 logical chunks: "b4: tests + dataclasses (RED)", "b4: orchestrator + tests GREEN", "b4: re-canary FL + WY", "b4: pilot diagnostics NY/TX/OH", "b4: 10-pair canary + log/status". Push at each.

### Phase 7 — Out of scope (NOT this plan)
- Full 350-pair fan-out at ~$25. Gated on user approval after seeing the 10-pair canary results.

---

## Cost / wall-time projections

- Per-pair: ~3 LLM calls (1 + N_titles + Σ chapters-with-children) ≈ ~$0.07/pair for FL-shape (3 calls) and ~$0.05/pair for WY-shape (2 calls — pass-3 skipped). Mixed average across 50 states: ~$0.06/pair.
- 50-state × 7-vintage = 350 pairs × $0.06 ≈ **~$21** for the full fan-out (vs B3PW's ~$17 and original B3-httpx's ~$17). Rounding error at this project's scale.
- Wall time per pair: ~3 fetches × ~5s rate-limit (~15s) + 3 LLM calls (~5s each) ≈ 30s/pair. With 4-way concurrency: 350 × 30 / 4 ≈ **44 min** for full fan-out. B3PW projected 30–40 min, so B4 adds ~10 min.
- 10-pair canary: ~$0.70, ~3 minutes wall time.

---

## What could change

- **Pass-3 returns []** for chapters that have children but none are lobbying-related. The orchestrator currently doesn't fall back to anything in that case — `parsed_urls` just doesn't gain anything from that chapter. If this surfaces as a real failure mode (pass-3 incorrectly filters out lobbying sections because of prompt under-specification), the remediation is either: (a) tighter pass-3 prompt with a "if all sections look lobbying-adjacent, return the chapter URL itself as a fallback" rule, or (b) post-pass-3 fallback in the orchestrator if pass-3 returns empty for a chapter whose pass-2 narrative confidently named lobbying.
- **Pass-3 over-picks** (returns every section, not just lobbying ones). Pass-2 prompt's Rule 4 already filters to in-scope; same wording applied via pass-3 should work. If FL canary shows pass-3 returning all 50 Ch.11 sections instead of the 6, that's a prompt-tuning task.
- **The PASS_3 marker injection trick** (kwarg into the template) is slightly clunky. If it produces test/production divergence (real model sees `PASS_3` in the prompt; pass-2 production never does), reconsider — write a separate pass-3 prompt file at that point. Default: keep the kwarg; the model treats `PASS_3` as just a label, not load-bearing instruction.
- **Chapter pages that mix full text AND child sections** (rare; some states' chapters are partly inline + partly leaved). Current logic adds both pass-2's chapter URL (since helper finds children) AND pass-3's section URLs to `parsed_urls`. Downstream extraction handles dedup. If this is wrong, the children-probe needs a "is this page mostly content or mostly TOC?" heuristic.
- **Cross-vintage stability** is still untested. After 10-pair canary, worth probing OH 2010 → OH 2025 and WY 2010 → WY 2025 to see if URL structure is year-swap-stable. If yes, the 7-vintage fan-out can compress to 1-vintage discovery + URL templating.

---

## Questions

1. **Should pass-3 fall back to the chapter URL if it returns empty?** Default per the plan: no — empty means no lobbying sections found, that pair has no result from this chapter. Revisit if FL canary shows pass-3 mis-filtering.
2. **Should the children-probe use a different parser than `_build_justia_link_tsv`?** Currently uses the same helper; same Pattern-1/2/3 logic applies (a chapter URL is typically directory-style `/chapter11/` or file-style `/chapter11.html`, both handled). If a chapter uses an unexpected URL form, surface and add handling there.
3. **Should B3PW be retired now that B4 ships?** Defer. B3PW stays for now as a "shorter / cheaper" option if a future caller wants chapter-level URLs only (e.g., for a tool that consumes chapter-level metadata). Cost of keeping it: ~250 LOC of orchestrator + 9 unit tests. Cheap.

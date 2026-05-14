# B3 Two-Pass Discovery Implementation Plan — Playwright variant

**Goal:** Same as the original B3 plan — land the model on actual lobbying-disclosure statute-leaf URLs via two-pass discovery (state-year-index → pick title → title-page → propose chapter URLs). **Difference:** HTTP fetches use `PlaywrightClient` (the proven anti-bot path from `pri-calibration`'s 50-state audit and `statute-retrieval`'s 5-state pilot) instead of `httpx` + Range-GET + hand-tuned rich-header set. The LLM role is unchanged.

**Originating conversation:** [`docs/active/api-multi-vintage-retrieval/convos/20260514_b3_with_playwright_pivot.md`](../convos/20260514_b3_with_playwright_pivot.md)

**Supersedes:** the httpx-based original B3 plan at [`docs/active/api-multi-vintage-retrieval/plans/20260514_b3_two_pass_discovery_plan.md`](20260514_b3_two_pass_discovery_plan.md) and the subagent-dispatch pivot in commit `376b2b1`. Both prior plans preserved on disk per contingency principle.

**Branch:** `api-multi-vintage-retrieval` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/api-vintage`)

**Tech stack:** `anthropic.AsyncAnthropic` (SDK v0.102+) for LLM calls; `playwright` + existing `src/scoring/justia_client.PlaywrightClient` for HTTP fetches; `bs4` parsers in `justia_client.py` (especially `parse_children_list`) for link extraction; `pytest` + `pytest-asyncio` for tests; Python 3.12 + `uv`. **Dropped:** `httpx` direct usage, `respx`, Range-GET trick, hand-tuned anti-bot header set.

---

## Delta from the original (httpx-based) B3 plan

Read the original B3 plan first — the orchestrator surface, prompts, dataclasses, and 7-test shape carry forward unchanged. This plan documents only the differences.

| Surface | Original (httpx) | This plan (Playwright) |
|---|---|---|
| Fetcher | New `fetch_justia_index(url)` in `api_retrieval_agent.py` — httpx + Range-GET 0–65535 + rich headers (Accept, Accept-Language, Connection, Upgrade-Insecure-Requests) | Reuse `justia_client.PlaywrightClient.fetch_page(url)` — fresh-browser-per-request, handles Cloudflare JS challenge by default |
| Link-list extraction | New TSV-builder in `api_retrieval_agent.py` | Reuse `justia_client.parse_children_list(html, parent_url)` for both pass-1 and pass-2 link lists |
| Async bridging | httpx is already async | `PlaywrightClient.fetch_page` is sync; orchestrator wraps each call in `asyncio.to_thread()` so the async batch surface is unchanged |
| HEAD verification | New `head_check()` with rich headers (already shipped in B2, but defect-prone) | Drop `head_check`; pass-2 URLs are verified by `client.fetch_page(url)` returning non-challenge HTML. Single source of truth for "this URL works." |
| Test boundary | `respx` mocks httpx | `FakeClient` satisfying the `Client` protocol (existing pattern in `justia_client.py` and its tests). Drop `respx` from this branch's test deps |
| Anti-bot scaffolding | `_JUSTIA_HEADERS` module-level constant, Range-GET helper, per-path header sensitivity diagnosed in B2 | None — all owned by `PlaywrightClient` |

The 7 behavioural tests, prompt files (`api_seed_discovery_pass{1,2}_prompt.md`), parser shape (`_parse_pass1_response`), orchestrator dataclasses (`Pass1Pass2Result`, `ChosenTitle`, `ProposedURL`), batch surface (`discover_urls_for_pairs_two_pass`), per-pair checkpoint shape, availability-side-channel JSONL, and Justia-hostname schema enforcement all carry forward from the original B3 plan unchanged.

---

## Testing Plan

Same 7 tests as the original B3 plan, identically named, identically scoped. The only change is the mock boundary:

- **Anthropic stub** unchanged from original — `FakeAsyncClient` differentiating pass-1 from pass-2 by marker in the prompt body.
- **Justia stub** moves from `respx` to a `FakeClient` class with a `fetch_page(url: str) -> str` method. Tests register a `dict[str, str]` URL → HTML mapping; the fake returns the canned HTML (or raises a registered exception, for test 5). Parses real HTML via `parse_children_list`, so the test's HTML fixtures exercise real parsing code.

This boundary is strictly better than `respx` for our case because it's the same boundary `justia_client.py`'s own tests use — one fewer mock convention to maintain in the codebase.

---

## Steps

### Phase 0 — Setup + baseline

1. **Read the originating convo + the original B3 plan.** Convo: `docs/active/api-multi-vintage-retrieval/convos/20260514_b3_with_playwright_pivot.md`. Original B3 plan: `plans/20260514_b3_two_pass_discovery_plan.md`. Understand which load-bearing pieces carry forward (orchestrator, prompts, dataclasses, tests) and which are being replaced (httpx, Range-GET, rich-headers, head_check, respx).

2. **Confirm worktree.** `git -C /Users/dan/code/lobby_analysis/.worktrees/api-vintage status` clean modulo `data/` symlink + gitignored `scripts/canary_discovery.py`. If not, sync with the user.

3. **Verify Playwright is installable in the worktree's venv.** `cd /Users/dan/code/lobby_analysis/.worktrees/api-vintage && PYTHONPATH=src uv run --active python -c "from playwright.sync_api import sync_playwright; print('ok')"`. If Playwright or its Chromium browser isn't installed, run `uv run --active playwright install chromium` (one-time per machine). The `pri-calibration` work already added `playwright` to the deps; confirm in `pyproject.toml`.

4. **Run the existing test suite once.** `cd /Users/dan/code/lobby_analysis/.worktrees/api-vintage && PYTHONPATH=src uv run --active pytest tests/test_api_retrieval_agent.py tests/test_justia_client.py -q`. Expect 9 + N passing. If anything fails, stop and surface it.

### Phase 1 — Prompts

5. **Use the prompts from the original B3 plan unchanged.** Files: `src/scoring/api_seed_discovery_pass1_prompt.md` (title-picker, output schema with `chosen_titles[]`); `src/scoring/api_seed_discovery_pass2_prompt.md` (URL-proposer with `{state_index}` carrying the title-page snapshot + `{chosen_title_rationale}`). Authoring details, Rule 6 wording, in-context examples retained from original B3 plan steps 4 and 5.

### Phase 2 — Tests (all 7 first, RED)

6. **Create `tests/test_api_retrieval_agent_b3.py`** with `FakeAsyncClient` (Anthropic) + `FakeJustiaClient` (HTTP). The Justia fake satisfies the existing `Client` protocol — single `fetch_page(url: str) -> str` method — and is constructed with a `dict[str, str]` URL→HTML mapping plus an optional `dict[str, Exception]` URL→exception mapping for failure-isolation tests.

7. **Write test 1** (`test_two_pass_returns_pass2_urls_for_single_title`). HTML fixtures: a state-year-index HTML with one in-scope title link, and that title's page with one in-scope chapter link. Pass-1 fake returns that title URL; pass-2 fake returns that chapter URL. Assert `parsed_urls` contains exactly the chapter URL. RED.

8. **Write test 2** (`test_two_pass_fans_out_to_multiple_titles`). Pass-1 fake returns two title URLs; HTML fixtures supply both title pages; pass-2 fake runs twice, returning chapter URLs from each; assert dedup on URL across both. RED.

9. **Write test 3** (`test_two_pass_rejects_non_state_year_titles_from_pass1`). Pass-1 fake returns one valid title URL + one out-of-namespace URL (wikipedia, wrong-state). Assert orchestrator drops the bad URL into `pass1_schema_violations` and proceeds with the valid one. RED.

10. **Write test 4** (`test_two_pass_propagates_justia_unavailable_from_pass1`). Pass-1 fake returns `{"chosen_titles": [], "justia_unavailable": true, ...}`. Assert orchestrator short-circuits — Anthropic fake sees exactly one call (pass 1), Justia fake sees exactly one fetch (the state-year index), `parsed_urls` is empty. RED.

11. **Write test 5** (`test_two_pass_isolates_title_fetch_failure`). Pass-1 fake returns two title URLs; Justia fake raises `RuntimeError("simulated outage")` on one of them, returns canned HTML on the other. Pass-2 fake runs once on the surviving title. Assert `title_fetch_failures` contains the failed URL + error; `parsed_urls` contains only the surviving title's pass-2 output. RED.

12. **Write test 6** (`test_pass1_response_schema_records_chosen_titles`). Direct unit test on `_parse_pass1_response` — JSON-with-fence variant; assert parsed `chosen_titles` list contains `(url, rationale)` tuples and that markdown fences are tolerated identically to `_parse_response_text`. RED.

13. **Write test 7** (`test_two_pass_pair_checkpoint_records_both_passes`). Run the orchestrator end-to-end with both fakes; serialize the result to the per-pair checkpoint JSON; deserialize; assert all fields round-trip (pass1_prompt, pass1_response, pass2_prompts list with per-title `{url, prompt, response}`, chosen_titles, parsed_urls, pass1_availability, schema_violations, title_fetch_failures). RED.

14. **Run the file.** All 7 RED with `ImportError`/`AttributeError`. Confirms tests will exercise real behavior.

### Phase 3 — Implementation (one function at a time, GREEN)

15. **Add a TSV-formatter helper** that takes `(html: str, parent_url: str) -> str` and returns `parse_children_list(html, parent_url)` lines as `<absolute-url>\t<anchor-text>` (same shape B2 used). Add it in `api_retrieval_agent.py` as a small private helper, not in `justia_client.py` — it's prompt-shaping logic, not parsing logic. The `parent_url` is the URL the snapshot was fetched from; `parse_children_list` already filters to that namespace.

16. **Add `async def _fetch_via_client(client: Client, url: str) -> str`** in `api_retrieval_agent.py` — thin wrapper around `asyncio.to_thread(client.fetch_page, url)`. This is the single async/sync bridge point; all Playwright contact funnels through it. Tests pass a `FakeJustiaClient` whose `fetch_page` is sync but fast; production passes `PlaywrightClient`.

17. **Add `_parse_pass1_response(text: str) -> tuple[list[ChosenTitle], dict, list[dict]]`** — pass-1 parser. Same markdown-fence tolerance as `_parse_response_text`; same Justia-hostname enforcement; drops out-of-namespace URLs to a `schema_violations` list (returned as the third tuple element).

18. **Run test 6 alone.** It should pass; others still RED.

19. **Add `async def discover_urls_for_pair_two_pass(...)` orchestrator.** Signature:
    ```python
    async def discover_urls_for_pair_two_pass(
        anthropic_client,
        justia_client: Client,           # PlaywrightClient or FakeClient
        *,
        state: str,
        vintage: int,
        slug: str,                       # e.g., "wyoming" for WY
        pass1_template: str,
        pass2_template: str,
        model: str = "claude-sonnet-4-6",
        max_output_tokens: int = 4096,
    ) -> Pass1Pass2Result:
    ```
    Behavior:
    1. Fetch state-year index: `html = await _fetch_via_client(justia_client, f"https://law.justia.com/codes/{slug}/{vintage}/")`.
    2. Build TSV link list via the helper; render pass-1 prompt; call `anthropic_client.messages.create`; parse via `_parse_pass1_response`.
    3. If `justia_unavailable=true` or `chosen_titles` empty: return result with empty `parsed_urls`, populated availability, empty pass-2 fields.
    4. For each chosen title: `await _fetch_via_client(justia_client, title_url)`. On exception, log to `title_fetch_failures` and skip.
    5. For each surviving title: build TSV link list (now over the title page's child URLs); render pass-2 prompt with `{state_index}` = title-page snapshot + `{chosen_title_rationale}` from the matching pass-1 entry; call Anthropic; parse via existing `_parse_response_text`.
    6. Union pass-2 URLs across titles, dedup on `(url, role)`. Return the result dataclass.

    `Pass1Pass2Result` dataclass fields per the original B3 plan step 19.

20. **Run tests 1, 2, 4, 3, 5, 7** in that order, fixing implementation defects as they surface. Each test reaching GREEN gets a commit (or one logical commit covering tests 1–2, another for 3–5, another for 7 — implementer's call).

21. **Add `async def discover_urls_for_pairs_two_pass(...)` batch orchestrator.** Identical surface to B2's `discover_urls_for_pairs` (concurrency cap via `asyncio.Semaphore`, per-pair checkpoint resume, `failures.jsonl`, `availability.jsonl`), but calling `discover_urls_for_pair_two_pass` internally. The Playwright client's 5s per-fetch rate limit means each pair takes ≥10s (two fetches) plus API latency. With 4-way concurrency (`max_concurrent=4`), 350 pairs ≈ 30–40 min wall time. **Lower the default concurrency cap from B2's 8 to 4** — Playwright is heavier than httpx and we want to be conservative with Justia at sustained pressure.

22. **No unit test for the batch orchestrator** beyond what B2's tests already cover — same delegation rationale as the original B3 plan step 22. The integration smoke test happens at canary time (Phase 4).

### Phase 4 — Canary against real Anthropic + real Justia

23. **Update `scripts/canary_discovery.py`** to add `CANARY_MODE=B3PW` (Playwright variant) alongside the existing `B2` mode. Reuse the `_TARGETS` dict (WY 2010 + FL 2010 ground-truth URL sets).

24. **Run `CANARY_TARGET=WY CANARY_MODE=B3PW`.** Expected: pass-1 picks `Title28/Title28.html`; orchestrator Playwright-fetches it; pass-2 proposes `Title28/chapter7.html`; final fetch (verification) confirms statute text comes back. Hit rate 1/1.

25. **Run `CANARY_TARGET=FL CANARY_MODE=B3PW`.** Same pass/fail analysis as original B3 plan step 25 — this is the load-bearing canary for whether two-pass is enough or whether B4 (three-pass: state → title → chapter → leaves) is needed. Document outcome in `results/20260514_b3pw_pilot_canaries.md`.

26. **If WY + FL both clean, run the 10-pair pre-fan-out canary** (this is the **new** step vs the original B3 plan). Pick: 5 pilot states (CA/TX/NY/WI/WY) at their `LOBBYING_STATUTE_URLS` vintages + 5 unseen states sampled across the audit's coverage tiers (e.g., AK 2010 / WA 2010 / CO 2016 [boundary case] / AR 2010 / WV 2010). Goal: confirm Playwright behavior holds at sustained pressure (10 pairs × ~2 fetches each = 20 fetches with 4-way concurrency, ~3 min wall time, ~$0.50 API). Outputs:
    - Per-pair hit rate vs ground truth (for the 5 pilot states with curated URLs).
    - Anti-bot incident log: any pair where Playwright returned a Cloudflare "Just a moment" page instead of statute HTML. If >0, **stop** and surface — the courtesy delay or concurrency cap needs tuning before fan-out.
    - Wall-time distribution: per-pair p50/p95 should be within 5–15s. If anything is >30s, that's a Cloudflare-challenge artifact and same response as above.

    Document in `results/20260514_b3pw_10pair_canary.md`. **Gate to Phase 5 fan-out:** ≥80% hit rate on the 5 ground-truth pairs, 0 anti-bot incidents, p95 wall time ≤30s.

27. **Read the canary results against the diagnostic framing.** Same pass/fail rubric as original B3 plan step 26, plus the new "stop on anti-bot incident" gate from step 26.

### Phase 5 — Document + commit + fan-out

28. **Update `RESEARCH_LOG.md`** with a session entry following the existing convention. Reference the canary results files from steps 25–26.

29. **Update `STATUS.md`** with a one-line entry in "Recent Sessions". Don't rewrite the Active Research Lines row beyond the Status column.

30. **Commit prompts + tests + agent changes + canary script update + results docs** in 3–5 logical commits (e.g., "b3pw: prompts and parser", "b3pw: orchestrator + tests", "b3pw: WY/FL canary", "b3pw: 10-pair canary", "b3pw: log + status").

31. **If the 10-pair canary gate passes, run the full 350-pair fan-out.** Single command, ~30–40 min wall time, ~$30 API. Checkpoint files land under `~/data/lobby_analysis/justia_discovery/<STATE>/<vintage>/discovered_urls.json` (or wherever the existing `data/` symlink chain points). Commit nothing data-side (the symlink convention handles it); commit a summary doc `results/20260514_b3pw_full_fanout_summary.md` with aggregate hit rate, schema violations, anti-bot incidents, and pairs-needing-human-review count.

32. **Push to origin.** `git push` should fast-forward.

---

## Testing Details

Identical to the original B3 plan §"Testing Details". The orchestrator's behavior tests are the load-bearing ones (tests 1, 2, 5, 7); schema/parsing tests (3, 4, 6) are narrower and target specific failure modes. The two real-Justia canaries (steps 24–25) plus the 10-pair canary (step 26) are the validation layer that unit tests can't reach.

## Implementation Details

- **Carry-forward from B2:** the prompt structure (`{state_index}` placeholder, Rule 6, JSON-output discipline), `_parse_response_text` (still used by pass 2), the `ProposedURL` dataclass with Justia-hostname enforcement, batch checkpoint/resume/failure-isolation pattern. Drop the `_JUSTIA_HEADERS` constant + Range-GET helper + `head_check` — all owned by `PlaywrightClient` now.
- **Carry-forward from `justia_client`:** `PlaywrightClient` (live HTTP), `Client` protocol (mock boundary), `parse_children_list` (link extraction), `parse_year_title_index` (deprecated for general use per its docstring — `parse_children_list` is the load-bearing parser here).
- **Async/sync bridge:** `asyncio.to_thread(client.fetch_page, url)` in `_fetch_via_client`. Confined to one helper. Tests don't need the bridge — `FakeJustiaClient.fetch_page` is fast-and-sync, and `asyncio.to_thread` on a fast function is effectively a no-op.
- **`Pass1Pass2Result` dataclass** identical to original B3 plan step 19.
- **`ChosenTitle` and `ProposedURL`** identical to original B3 plan.
- **Concurrency:** `max_concurrent=4` (down from B2's 8). Per-fetch rate limit is 5s inside `PlaywrightClient`, so each pair takes ≥10s for fetches alone. 350 pairs × 10s ÷ 4 concurrent = ~15 min minimum; add API latency → realistic 30–40 min.
- **Wall-time courtesy:** if the 10-pair canary surfaces any Cloudflare incident, the first remediation is `max_concurrent=2` and `rate_limit_seconds=10`. Don't tighten more than that without surfacing — Justia's anti-bot tuning has shifted before and we want a real diagnosis, not a louder hammer.
- **Cost per pair:** ~$0.05 API (2× B2's per-call cost). Full 350-pair fan-out: ~$17. Same as original B3.
- **What stays gitignored:** `scripts/canary_discovery.py` (per the B1 policy carried through B2 and now B3).

## What could change

- **Cloudflare under sustained pressure.** This is the principal unknown the 10-pair canary exists to resolve. If anti-bot bites at section-leaf depth × multiple parallel browsers, the remediation is tighter concurrency / longer rate-limit, possibly per-state pacing instead of global. The audit was 50 fetches at the state-level with 2s pacing; the pilot was ~50 section-leaf fetches across 5 states. 700 fetches at mixed depths is a step up, but not by orders of magnitude.
- **FL chapter-TOC ceiling** (same risk as original B3 plan). Playwright doesn't change this — it's a model-judgment axis, not an HTTP axis. If pass-2 lands on `chapter11/chapter11.html` instead of section leaves, B4 (three-pass) is the next escalation, same as original.
- **Cross-vintage URL pattern stability.** If OH 2010 → OH 2025's "year-swap only" pattern holds broadly, the 7-vintage fan-out could compress to 1-vintage discovery + 6× URL-templating. Worth testing during the canary: pick one state from the 10-pair set and run it at 2 vintages; compare URL structure. If templating works, that's a ~5× reduction in the fan-out cost. Document but don't block on it — the conservative path (full per-vintage discovery) is still cheap enough.
- **Playwright sync vs async.** If `asyncio.to_thread` overhead surfaces as a bottleneck during fan-out (unlikely at ≤4-way concurrency), switch `PlaywrightClient` to `playwright.async_api` for a native-async path. Wait until profiling shows it's actually a problem.
- **PlaywrightClient's `rate_limit_seconds=5` default.** That's per-instance. With 4-way concurrency we have 4 instances each pacing themselves, so effective fetch rate is ~0.8 fetches/sec at Justia. Audit ran at 0.4 fetches/sec (sequential, 2s pacing) without anti-bot incident. Twice the audit's rate is the relevant comparison — should be fine, but the 10-pair canary is what confirms it.

## Questions

1. **Should pass-1 prompt cap multi-title picks at 2?** Same question as original B3 plan #1. Open — let the data answer during canary.
2. **Pass-2 Rule 6 wording — strict or chapter-scoped extrapolation?** Same as original B3 plan #2.
3. **`chosen_title_rationale` carryover.** Same as original B3 plan #3.
4. **`PlaywrightClient` instance reuse vs per-call construction.** Currently the class instance is reused (caller pattern); each `fetch_page` call still spins a fresh browser context internally per Cloudflare-fingerprinting concerns. Should the orchestrator construct one `PlaywrightClient` per worker, or one per pair? **Default: one per worker** (4 instances total for the fan-out). Per-pair would mean 350 instance constructions with no benefit. Validate during canary.
5. **HEAD verification → full-fetch verification cost.** The original B3 plan's `head_check` was a cheap probe (HEAD + Range or small GET). Playwright fetch-verification is ~5s + browser overhead per URL, but it doubles as the actual statute-text fetch for the downstream pipeline. Recommend: **integrate verification into the eventual pull step**, not as a separate canary post-step. The 10-pair canary verifies a small sample explicitly; full fan-out trusts pass-2 output and verifies opportunistically when the statute text is later fetched.
6. **HG 2007 split-vintage pairs.** Same as original B3 plan #6 — B3PW inherits the two-bundles-per-state design from the kickoff plan automatically.

---

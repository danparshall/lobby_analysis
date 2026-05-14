# B3 Two-Pass Discovery Implementation Plan

**Goal:** Add a two-pass discovery surface to `api_retrieval_agent.py` that lands the model on actual lobbying-disclosure statute-leaf URLs instead of one-hop-short title-index pages — by fetching Justia's title-level page between the state-year-index pass (B2) and the URL-proposal pass.

**Originating conversation:** [`docs/active/api-multi-vintage-retrieval/convos/20260514_b2_justia_index_inline_recanary.md`](../convos/20260514_b2_justia_index_inline_recanary.md)

**Context:** B2 canaries against WY 2010 and FL 2010 both produced 0 / N statute-leaf hit (where N is 1 and 6 respectively) despite the model behaving correctly under Rule 6. The model copies URL casing literally, refuses to hallucinate deeper paths, and explicitly names the right chapter/section in narrative (FL: "Chapter 11 ... 11.045") — but the state-year index page only goes one level deep, so the model never sees the actual chapter URLs and so can't propose them. This is structural: a single-fetch single-call architecture can't reach the statute body for any state whose statute lives below the title level. Two B2 canaries across two structurally distinct states (single chapter-leaf vs per-section leaves) confirmed the limit isn't WY-specific.

**Confidence:** Architecture decision (two-pass) is high-confidence — strongly supported by two canaries. Specific design choices within two-pass (single vs. multiple title pick, pass-2 Rule 6 wording, multi-statute-body states) are medium — see Open Questions, and the B3 canary should be run against ≥2 pilot states before fan-out.

**Architecture:** Pass 1 fetches the state-year index (`https://law.justia.com/codes/<slug>/<vintage>/`) and inlines it into a title-picker prompt; the model returns one or more title-level URLs that contain the lobbying-disclosure statute. The orchestrator then fetches each of those title-level pages and inlines them into a URL-proposal prompt; the model returns the URLs that constitute the statute body (chapter-leaf, section-leaves, or chapter-TOC, depending on what the title page exposes). Both passes use the same `client.messages.create` boundary, the same `state_index` placeholder pattern, and Rule 6 unchanged.

**Branch:** `api-multi-vintage-retrieval` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/api-vintage`)

**Tech Stack:** `anthropic.AsyncAnthropic` (SDK v0.102+); `httpx` (transitively via anthropic) for Justia fetches; `beautifulsoup4` for index parsing; `pytest` + `pytest-asyncio` + `respx` for tests; Python 3.12 + `uv`.

---

## Testing Plan

I will add behavioural tests in `tests/test_api_retrieval_agent_b3.py` covering the two-pass orchestrator end-to-end. Each test exercises real code from the orchestrator boundary downward; the two external boundaries (Anthropic API, Justia HTTP) are stubbed:

- **Anthropic stub** reuses the existing `FakeAsyncClient` pattern from `tests/test_api_retrieval_agent.py` — a `responder` callable that takes `(state, vintage, pass_number)` and returns either response text or an exception. The responder pattern is required to differentiate pass-1 ("which title?") from pass-2 ("which leaves?") responses for the same pair.
- **Justia stub** uses `respx` to mock `httpx` responses. Tests register the state-year-index URL and any title-level URLs they expect the orchestrator to fetch, with canned HTML bodies that exercise the link-extraction logic. (`respx` is already in `dev` deps from the B1 session.)

Tests (all behavioural — no datatype/mock-only checks):

1. **`test_two_pass_returns_pass2_urls_for_single_title`** — pass-1 model picks one title-URL from the state-year index; orchestrator fetches that URL via stubbed Justia; pass-2 model proposes a single statute-leaf URL from the title-page; orchestrator returns that URL. Asserts the returned list contains exactly the pass-2 URL, and asserts the orchestrator's second `client.messages.create` was called with the pass-2 prompt containing the title-page snapshot in `{state_index}`.

2. **`test_two_pass_fans_out_to_multiple_titles`** — pass-1 model picks two title-URLs (simulates OH's "Title 1 contains both Ch. 101 and Ch. 121" or a state with parallel statute bodies in different titles); orchestrator fetches both; pass-2 runs once per title; returned list is the union of both pass-2 outputs. Asserts deduplication on URL (no double-emit if both title pages link to the same URL).

3. **`test_two_pass_rejects_non_state_year_titles_from_pass1`** — pass-1 model returns a URL that's not a descendant of `/codes/<slug>/<vintage>/` (e.g., a wikipedia link or a wrong-state URL); orchestrator drops it, records it in a `schema_violations`-style field on the checkpoint, and proceeds with any valid titles. If no valid titles remain, returns empty list and records pass-1-failed availability metadata.

4. **`test_two_pass_propagates_justia_unavailable_from_pass1`** — pass-1 model returns `{"urls": [], "justia_unavailable": true, "alternative_year": null, "notes": "..."}`. Orchestrator records availability and short-circuits — does NOT call pass-2, does NOT fetch any title page. Asserts the FakeAsyncClient saw exactly one call (pass 1), and the returned list is empty.

5. **`test_two_pass_isolates_title_fetch_failure`** — pass-1 picks two titles; the orchestrator's title-page fetch fails for one (HTTP 500 or timeout) and succeeds for the other. The failed title is recorded in a per-pair failure log; pass-2 still runs on the successful title; returned list contains pass-2 URLs from the surviving title only. Asserts the failure is loggable (not silently swallowed) — a missing title indicates either a Justia outage or a bad pass-1 pick, both of which should be reviewable.

6. **`test_pass1_response_schema_records_chosen_titles`** — pass-1 prompt produces a structured response (`{"chosen_titles": [{"url": "...", "rationale": "..."}], "justia_unavailable": false, ...}`); orchestrator parses it via a pass-1-specific parser. Asserts the parser extracts chosen_titles with their rationales, and tolerates the same markdown fences the existing `_parse_response_text` tolerates.

7. **`test_two_pass_pair_checkpoint_records_both_passes`** — the per-pair checkpoint file written under `<checkpoint_root>/<STATE>/<vintage>/discovered_urls.json` includes both API calls' prompts and responses (e.g., `pass1_prompt`, `pass1_response`, `pass2_prompts: [{url: title-url, prompt: ..., response: ...}, ...]`). Full reproducibility — a future agent re-running on the same pair should see exactly what was sent and received at both stages. Asserts the field shape is stable enough that re-loading from disk reconstructs the parsed URL list without re-querying.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Steps

### Phase 0 — Plan review + setup

1. **Read the originating convo and both B2 result docs.** Files: `docs/active/api-multi-vintage-retrieval/convos/20260514_b2_justia_index_inline_recanary.md`; `docs/active/api-multi-vintage-retrieval/results/20260514_wy2010_b2_index_inline_hit_rate.md`; `docs/active/api-multi-vintage-retrieval/results/20260514_fl2010_b2_index_inline_hit_rate.md`. Goal: understand exactly what B2 fixed, what B2 didn't, and why the architectural ceiling is title-only-depth on the state-year index.

2. **Confirm worktree.** `git -C /Users/dan/code/lobby_analysis/.worktrees/api-vintage status` should be clean (modulo `data/` symlink + gitignored `scripts/canary_discovery.py`). If not, sync with the user before touching code.

3. **Run the existing test suite once** as a baseline: `cd /Users/dan/code/lobby_analysis/.worktrees/api-vintage && PYTHONPATH=src uv run --active pytest tests/test_api_retrieval_agent.py -q`. Expect 9 passing. If anything fails, stop and surface it — don't proceed with B3 work on top of a broken baseline.

### Phase 1 — Prompts

4. **Author `src/scoring/api_seed_discovery_pass1_prompt.md`.** Minimal title-picker prompt. Inputs: `{state}`, `{vintage}`, `{state_index}` (the state-year index link list as in B2). Output schema:
   ```
   {
     "chosen_titles": [
       {"url": "https://law.justia.com/codes/<slug>/<year>/Title<X>/Title<X>.html",
        "rationale": "Why this title contains the lobbying-disclosure statute."}
     ],
     "justia_unavailable": false,
     "alternative_year": null,
     "notes": ""
   }
   ```
   Rules to include:
   - Output JSON only (same as B2).
   - URLs must be Justia and must be children of `/codes/<slug>/<vintage>/`.
   - Pick the title containing the lobbyist-registration / lobbying-disclosure statute. If the state's statute body is split across multiple titles (rare; e.g., separate executive-branch and legislative-branch lobbying titles), include all relevant titles. **Be conservative** — picking one wrong title is cheaper than picking three irrelevant ones, because each title triggers a second HTTP fetch + API call.
   - Same `justia_unavailable` semantics as B2.
   - No in-context examples necessary for pass 1 — the task is narrow ("which entry in this list is the lobbying title") and the snapshot gives literal evidence.

5. **Author `src/scoring/api_seed_discovery_pass2_prompt.md`.** This is the B2 prompt's evolution: title-level snapshot replaces state-year snapshot in `{state_index}`. Additions to the B2 prompt:
   - New input `{chosen_title_rationale}` — passed through from pass 1 so pass 2 knows why the title was picked.
   - Rule 6 wording adjusted: "The snapshot below is for the title you previously identified as containing the lobbying-disclosure statute. Within this title, propose the URLs that constitute the statute body — could be a single chapter-leaf with full statute text, multiple per-section leaves, or a chapter-level TOC page that itself contains the full text. Use the link structure in the snapshot to judge depth; do not invent URLs deeper than the snapshot exposes." (Same conservatism principle; pass-2-specific framing.)
   - Keep the 5 in-context examples (CA/TX/NY/WI/OH 2010) — they still illustrate the 5 convention shapes and the model needs them to know the *shape* of what to propose.

### Phase 2 — Tests (all 7 first, RED)

6. **Create `tests/test_api_retrieval_agent_b3.py`** with the duck-typed Anthropic fake adapted from `tests/test_api_retrieval_agent.py`. The fake needs to differentiate pass-1 calls from pass-2 calls (e.g., by detecting the marker `PASS_1` / `PASS_2` in the prompt body, or by call order). Add a small `MINIMAL_PASS1_TEMPLATE` + `MINIMAL_PASS2_TEMPLATE` constants for tests (don't load the real prompt files in unit tests).

7. **Write test 1** (`test_two_pass_returns_pass2_urls_for_single_title`). Run pytest → confirm RED (function doesn't exist).

8. **Write test 2** (`test_two_pass_fans_out_to_multiple_titles`). RED.

9. **Write test 3** (`test_two_pass_rejects_non_state_year_titles_from_pass1`). RED.

10. **Write test 4** (`test_two_pass_propagates_justia_unavailable_from_pass1`). RED.

11. **Write test 5** (`test_two_pass_isolates_title_fetch_failure`). RED.

12. **Write test 6** (`test_pass1_response_schema_records_chosen_titles`). RED.

13. **Write test 7** (`test_two_pass_pair_checkpoint_records_both_passes`). RED.

14. **Run the whole test file** — all 7 tests should fail with `ImportError` or `AttributeError`. This confirms the tests will exercise real behavior, not pass on import accident.

### Phase 3 — Implementation (one function at a time, GREEN)

15. **Add `fetch_justia_index(url: str) -> tuple[str, str]`** to `scripts/canary_discovery.py` first as the simplest place to generalize the fetcher (was `fetch_state_index(slug, vintage)`; new function takes a full URL). The state-year-specific wrapper becomes a thin caller. This is the canary script — gitignored, doesn't need tests. Make sure it produces the same `(html, link_list)` output shape.

16. **Lift the fetcher into the agent module** as `fetch_justia_index(url: str) -> tuple[str, str]` in `src/scoring/api_retrieval_agent.py`. Same anti-bot headers as the canary; same TSV `<absolute-url>\t<anchor-text>` link-list shape. Take an `httpx.Client` parameter so the orchestrator can pass a shared client (and tests can pass a respx-stubbed one). Default: construct a new client per call.

17. **Add `_parse_pass1_response(text: str) -> tuple[list[ChosenTitle], dict]`** — parser for the pass-1 response schema. Returns parsed `ChosenTitle` dataclass list (url + rationale) and the availability metadata dict. Same markdown-fence tolerance as `_parse_response_text`. Same Justia-hostname + state-year-prefix schema enforcement; dropped URLs go to a `schema_violations` field.

18. **Run tests 6** alone (`test_pass1_response_schema_records_chosen_titles`). It should now pass. Other tests still RED.

19. **Add `async def discover_urls_for_pair_two_pass(...)` orchestrator** to `src/scoring/api_retrieval_agent.py`. Signature:
    ```python
    async def discover_urls_for_pair_two_pass(
        client,
        *,
        state: str,
        vintage: int,
        slug: str,                          # e.g., "wyoming" for WY
        pass1_template: str,
        pass2_template: str,
        http_client: httpx.AsyncClient | None = None,
        model: str = "claude-sonnet-4-6",
        max_output_tokens: int = 4096,
    ) -> Pass1Pass2Result:
    ```
    where `Pass1Pass2Result` is a dataclass with fields:
    - `parsed_urls: list[ProposedURL]` (final pass-2 union, deduped)
    - `chosen_titles: list[ChosenTitle]` (pass-1 picks)
    - `pass1_prompt: str`, `pass1_response: str`
    - `pass2_prompts: list[dict]` (per-title `{url, prompt, response}`)
    - `pass1_availability: dict`
    - `pass1_schema_violations: list[dict]`
    - `title_fetch_failures: list[dict]` (per-title `{url, error, retrieved_at}`)
    
    Behavior:
    1. Fetch state-year index via `fetch_justia_index(f"https://law.justia.com/codes/{slug}/{vintage}/")`.
    2. Render pass-1 prompt; call client; parse via `_parse_pass1_response`.
    3. If pass-1 reports `justia_unavailable=true` or returns empty `chosen_titles`, short-circuit and return result with empty `parsed_urls`.
    4. For each chosen title, fetch its page via `fetch_justia_index(title_url)`. Title fetches that error get logged to `title_fetch_failures` and don't propagate. Surviving titles continue.
    5. For each surviving title, render pass-2 prompt with the title-page snapshot in `{state_index}` and `{chosen_title_rationale}`; call client; parse via existing `_parse_response_text`.
    6. Union the per-title pass-2 URL lists (dedup on `(url, role)`); return the result dataclass.

20. **Run tests one at a time, fixing implementation defects as they surface.** Order: test 1 first (single title happy-path), then test 2 (multi-title fan-out), then test 4 (early-exit on `justia_unavailable`), then test 3 (schema-violation on bad pass-1 URL), then test 5 (title-fetch failure isolation), then test 7 (checkpoint shape). Each test reaching GREEN gets a commit.

21. **Add `discover_urls_for_pairs_two_pass(...)` batch orchestrator** (parallel to existing `discover_urls_for_pairs`). Per-pair checkpoint at `<root>/<STATE>/<vintage>/discovered_urls.json` includes both passes' prompts + responses + the chosen titles + parsed final URLs + schema violations + title fetch failures + availability. Resume logic identical to B2's: if the checkpoint exists, load and skip. Concurrency cap via `asyncio.Semaphore`. Per-pair failure isolation to `<root>/failures.jsonl`. Availability log `<root>/availability.jsonl` for `justia_unavailable=true` pairs.

22. **Don't add a unit test for the batch orchestrator beyond what B2 already covers in spirit** — the parallel functions in B2 (`discover_urls_for_pairs`) already have concurrency / resume / failure-isolation tests, and the batch is a thin wrapper around the single-pair orchestrator. Add an integration smoke test only if a real failure surfaces during the canary.

### Phase 4 — Canary against real Anthropic + real Justia

23. **Update `scripts/canary_discovery.py`** to add a `CANARY_MODE=B3` env var path that calls `discover_urls_for_pair_two_pass` and prints both passes' outputs + HEAD-verifies the final URL list. Keep `CANARY_MODE=B2` working for regression comparison. Reuse the `_TARGETS` dict (WY + FL ground-truth URL sets).

24. **Run `CANARY_TARGET=WY CANARY_MODE=B3` against the real Anthropic + real Justia.** Expected outcome: model picks `Title28/Title28.html` on pass 1; orchestrator fetches Title 28 page; model proposes `Title28/chapter7.html` on pass 2; HEAD-verify confirms 206 LIVE. Hit rate 1/1. If hit rate is 0/1, capture exactly what the model proposed at pass 2 (chapter-TOC page? wrong chapter? section-level URLs?) — that's the next-iteration signal.

25. **Run `CANARY_TARGET=FL CANARY_MODE=B3`.** This is the harder case: title page exposes chapter-level links; the actual statute body lives in section-level leaves under `chapter11/`. **Two possible outcomes are both informative:**
    - **Pass-2 proposes `chapter11/chapter11.html` (chapter-TOC page)** — interpret: title page exposes chapters, not sections; B3 lands one hop short again. The next architecture iteration would be three-pass (state → title → chapter → leaves), but check first whether the chapter-TOC page itself contains full statute text (in which case 1/6-but-actually-fine is acceptable for downstream extraction).
    - **Pass-2 proposes all 6 statute-leaf URLs** (`chapter11/11_045.html`, etc.) — interpret: title page exposes section links transitively (e.g., via embedded chapter-page summaries) OR the model legitimately extrapolated from chapter11/ + the snapshot's casing conventions. Hit rate 6/6 is the ideal.
    
    Save the result either way to `docs/active/api-multi-vintage-retrieval/results/20260514_b3_pilot_canaries.md` with the same structure as the B2 result docs.

26. **Read the result against the diagnostic doc's framing.** If B3 hit-rate is ≥80% across WY + FL, recommend canary-2-more-pilot-states (NY, TX, OH, or all three) before fan-out. If B3 hit-rate is <50% on FL (i.e., chapter-TOC ceiling), surface a B4 design discussion before further work — the structural cost of three-pass may be worth it, but the user should weigh in.

### Phase 5 — Document + commit

27. **Update `RESEARCH_LOG.md` for the branch** with a session entry following the existing convention (Topics Explored / Provisional Findings / Decisions Made / Open Questions / Next Steps). Reference the canary results file from step 25.

28. **Update `STATUS.md`** with a one-line entry in "Recent Sessions". Don't rewrite the Active Research Lines row; just add the session entry.

29. **Commit the prompts + tests + agent changes + canary update + results doc** in 2–4 logical commits (e.g., "b3: prompts and parser", "b3: orchestrator + tests", "b3: canary results"). Each commit should leave tests passing.

30. **Push to origin.** This branch has been pushed before (`origin/api-multi-vintage-retrieval`) — `git push` should fast-forward without prompting.

---

## Testing Details

The B3 tests exercise the orchestrator's behavior, not its types or mocks:

- **Test 1** verifies the two-pass flow produces a final URL list that matches what pass 2 returned — i.e., the orchestrator threads pass-1 → fetch → pass-2 correctly and doesn't accidentally return pass-1 URLs.
- **Test 2** verifies multi-title fan-out is real (two fetches, two pass-2 API calls, union of results) — not just "the orchestrator accepted a list input."
- **Test 3** verifies the schema check on pass-1 URLs is active. Without this, the orchestrator would happily fetch wikipedia.org or a sibling state's URL, wasting tokens.
- **Test 4** verifies the `justia_unavailable=true` shortcut. Without this, the orchestrator would spend a no-op pass-2 call for every pair where the model knows no statute exists.
- **Test 5** verifies that one bad title fetch doesn't sink the whole pair. Real Justia outages, slow responses, and pass-1 picking a temporarily-down title-page are all possible.
- **Test 6** verifies the pass-1 parser extracts the rationale alongside the URL — pass 2 reads the rationale to know which statute body the pass-1 model was targeting, so losing it would degrade pass-2 prompt quality.
- **Test 7** verifies the checkpoint shape is faithful enough that a re-run can reconstruct everything (both prompts, both responses, parsed URLs, schema violations, fetch failures). This is the experiment-data-integrity safeguard for B3.

The two canaries (steps 24–25) are the real validation — unit tests can't tell us whether the model + Rule 6 + the title-page snapshot actually produce the right URLs. The behavioural prediction for each canary is documented in the step itself so the implementing agent has a clear pass/fail criterion.

## Implementation Details

- B2 building blocks (`fetch_state_index` → generalized to `fetch_justia_index`, `head_check`, `_parse_response_text`, `state_index` placeholder, Rule 6) all carry forward unchanged in structure; only `fetch_state_index` gets generalized.
- Two prompts (pass 1, pass 2) rather than one shared prompt — pass 1 is narrow ("which title?") and doesn't need the 5 in-context convention examples; pass 2 is the B2 prompt evolved.
- `ProposedURL` and `ChosenTitle` are separate dataclasses — same `from_raw` Justia-hostname enforcement on both, but they carry different shapes (rationale-only on pass 1; role + rationale on pass 2).
- Per-pair checkpoint shape extended; old B2 checkpoints will not be re-readable by the B3 batch orchestrator (acceptable — there's only one in-progress B2 run, the WY canary, and it's gitignored).
- Anti-bot header set is captured in one place (the `_JUSTIA_HEADERS` module-level constant in `api_retrieval_agent.py`) and reused by both `fetch_justia_index` and `head_check`. The B2 canary already standardized on this set; B3 inherits.
- `discover_urls_for_pair` (B2 single-pass) remains unchanged and supported — useful for any caller who wants single-pass behavior, and as a regression comparator if B3 produces surprising results.
- Cost per pair: ~$0.05 (2× B2's per-call cost). Full 350-pair fan-out: ~$17. Still trivial.
- Concurrency: each pass-2 call has its own slot in the semaphore — a pair with N titles uses N+1 sequential calls inside the per-pair semaphore slot (or N+1 calls under whatever cap the per-pair task has). Keep the cap setting unchanged from B2 (`max_concurrent=8`).
- The `chosen_title_rationale` field is passed *as text* into pass-2's prompt — no special escaping needed beyond what `str.format` already does for braces in the rationale text. Pre-emptive defensive: pass the rationale through a brace-escape helper (`text.replace("{", "{{").replace("}", "}}")`) before substitution.

## What could change

- **If FL 2010 B3 canary lands on chapter-TOC pages instead of section-leaves**, the architecture needs a third pass (chapter → section enumeration). The plan as written ships two-pass; B4 would be a follow-on plan, not a revision of this one. The dataclass + orchestrator surface could extend naturally — `discover_urls_for_pair_three_pass(...)` or a recursive `discover_urls_for_pair_n_pass(...)`.
- **If a state's lobbying statute spans multiple titles** (rare; possibly some states with separate executive-branch and legislative-branch lobbying statutes), pass-1 returns multiple titles and B3's fan-out covers it. If the spread is across multiple titles but the model only picks one, the missed URLs will surface as low recall on calibration runs and the prompt needs adjustment.
- **If Justia anti-bot tightens** (e.g., the Range-GET trick stops working for some URLs), the fetcher needs updating but the orchestrator surface is unaffected. Capture any new anti-bot findings in a follow-up note alongside `notes/claude_silent_deny_api_multi_vintage.md`.
- **If the model becomes too conservative on pass 2** (e.g., refuses to propose section-leaves even when the chapter page lists them explicitly), the pass-2 Rule 6 wording needs softening. Watch for "snapshot only exposes chapter-level links" language in pass-2 responses — that's the canary signal.
- **The Compendium 2.0 success criterion (multi-rubric × multi-year validation)** means we need reliable retrieval across vintages, not just at 2010. After WY + FL pilot, run B3 against (WY, 2015), (WY, 2024) or similar to confirm vintage stability before fan-out.

## Questions

1. **Pass-1 multi-title cap.** Should pass-1 be allowed to return up to N titles? Current plan: no explicit cap; the prompt's "be conservative" framing is the soft cap. If the model regularly returns 3-4 titles for states with one statute body, add an explicit cap.
2. **Pass-2 Rule 6 wording.** Should pass-2 forbid extrapolation strictly (like B2 did), or allow within-chapter extrapolation if the snapshot shows the chapter-leaf is itself a TOC of section-leaves? Strict is safer but caps recall on per-section-leaf states. The FL canary outcome will be the key data point.
3. **`chosen_title_rationale` carryover.** Is feeding the rationale into pass 2 actually useful, or does it just bias the model? Alternative: pass 2 sees only the title-page snapshot and re-reasons from scratch. Cheapest test: run both variants on FL 2010 and compare.
4. **Canary cost guardrail.** For the canary runs (step 24-25), set a hard token-budget guard — if cumulative input tokens for one pair exceed some threshold (say, 30k), abort and surface. Title pages can be larger than state-year indexes (e.g., FL's TitleIII.html is ~58 KB); a Range-GET of 0-65535 should still capture the link structure, but worth checking.
5. **Should the B3 unit tests use real Anthropic SDK objects?** No — the `respx` + `FakeAsyncClient` pattern is the right boundary. Real Anthropic comes in via the canary, where the API surface is genuinely the thing being tested.
6. **HG 2007 split-vintage pairs.** The kickoff plan handled HG 2007 as two bundles per state (2002 + 2007). B3 inherits this automatically — both pairs go through the same two-pass discovery. No special handling.

---

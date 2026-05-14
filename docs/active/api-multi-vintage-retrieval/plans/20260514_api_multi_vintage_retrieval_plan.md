# API-Driven Multi-Vintage Statute Retrieval Implementation Plan

**Goal:** Build a Python module that uses the Anthropic API (`anthropic.AsyncAnthropic`) to discover Justia URLs for `(state, vintage)` pairs across all 50 states and ~6 historical vintages, with HEAD-verification and checkpoint-per-pair resume safety, feeding the existing Playwright `retrieve-statutes` fetcher.

**Originating conversation:** [`../convos/20260514_api_multi_vintage_kickoff.md`](../convos/20260514_api_multi_vintage_kickoff.md)

**Context:** Multi-rubric calibration of our extraction prompts requires reading state lobbying statutes at the vintages prior researchers (PRI 2010, CPI 2015, Sunlight 2015, HG 2007, Newmark 2017) actually scored — so that our LLM's reading of *today's* statutes can be validated against ground-truth scores established by humans on older vintages. The existing curated `LOBBYING_STATUTE_URLS` table covers 6 pilot states × 1–2 vintages; scaling to all 50 states × 6 vintages by hand-curation is infeasible. Using Anthropic API directly (vs. Claude Code subagents) is preferred because the work is embarrassingly parallel and the user is token-constrained on the Claude Code session budget.

**Confidence:** Medium-high. The Playwright fetcher half is proven (1.35 MB of verified bundles already on disk). The API-driven discovery half is greenfield but architecturally straightforward — async fan-out + structured-output prompting. Main unknown is whether the LLM reliably produces valid Justia URLs from cold (no seed bundle); existing prompt is hop-1-cross-ref-shaped and likely needs a sibling for seed discovery.

**Architecture:** Two new modules. `api_retrieval_agent.py` wraps `anthropic.AsyncAnthropic` with a structured prompt template that takes `(state, vintage)` and returns a list of proposed Justia URLs with role labels (`core_chapter`, `support_chapter`) and rationale. `url_verification.py` does parallel HEAD requests to filter out hallucinated URLs before passing the valid set to the existing `cmd_retrieve_statutes` orchestrator subcommand for Playwright fetch. Both modules write checkpoints under `data/statutes/<state>/<vintage>/` so re-runs are idempotent.

**Branch:** `api-multi-vintage-retrieval` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/api-multi-vintage-retrieval`)

**Tech Stack:** Python 3.12, `uv`, `anthropic` SDK (new dep — needs install), `httpx` (already transitively present via Playwright; used for HEAD probes), `pytest`, `pytest-asyncio`, `respx` or `pytest-httpx` for HTTP mocking, existing `scoring.justia_client` (unchanged), existing `scoring.orchestrator` (extended with one new subcommand).

**Architecture vs. headless `claude -p`:** `phase-c-projection-tdd` is moving onto headless Claude Code sessions via `claude -p`, billing the same `ANTHROPIC_API_KEY` (see [`../../../active/phase-c-projection-tdd/plans/20260514_headless_api_key_handoff.md`](../../phase-c-projection-tdd/plans/20260514_headless_api_key_handoff.md)). This branch deliberately picks **direct SDK** instead, because URL discovery is a narrow structured-output task that doesn't need Claude Code's tooling / skills / sub-agent infrastructure; the per-call overhead of a full CC session is wasted on it. The two approaches share the API-key budget but not the runtime.

**API-key source:** `.env.local` at the repo root (gitignored via `.env*`, symlinked from main worktree into this worktree per the `use-worktree` skill). A minimal `.env.local` parser at module load — no new `python-dotenv` dep — reads only the keys the script needs and sets them in `os.environ`. The `anthropic` SDK picks up `ANTHROPIC_API_KEY` automatically from env once it's there. The key MUST NOT be logged, included in checkpoints, or referenced in commits.

---

## Vintages in scope

Derived from `docs/active/phase-c-projection-tdd/results/20260514_rubric_data_years.md`. Justia-feasible only; pre-2005 BoS-era rubrics (Opheim 1991, Newmark 2005 panels) are explicitly out of scope and deferred to a successor branch.

| Vintage | Rubric(s) | Implementation note |
|---|---|---|
| 2002 | HG 2007 Q35-Q37 | Separate bundle directory, distinct from 2007. Expect lower Justia coverage. |
| 2006 or 2007 | HG 2007 main (Q1-Q34, Q38) | Pick one nominal year (lean 2007); ±2yr tolerance via existing audit. |
| 2009 or 2010 | PRI 2010 | Pilot states already done — resume logic must skip them. |
| 2014 or 2015 | CPI 2015 C11 + Sunlight 2015 | Pick one (lean 2015). |
| 2015 or 2016 | Newmark 2017 | Could be merged with 2014-15 if statutes look stable; treat as separate target for safety. |
| 2021 | L-N 2025 (calibration-free for states) | Include — cheap to add to the fan-out. |
| 2025 | "Today" baseline | OH 2025 already done. |

**Expected scale:** 50 states × 7 target vintages = 350 `(state, vintage)` pairs. Minus the ~7 pairs already retrieved (6 pilot states at 2010 + OH 2025), ~343 new discovery calls.

---

## Testing Plan

I will write the following tests, all *before* any implementation code, and verify each fails first.

### `tests/test_api_retrieval_agent.py`

**Test 1 — single-pair discovery returns structured URL list.**
Mock `anthropic.AsyncAnthropic` at the SDK boundary so its `messages.create` returns a canned response containing a valid structured `urls` payload for `("CA", 2015)`. Call `discover_urls_for_pair(client, state="CA", vintage=2015, prompt_template=...)`. Assert the function returns a list of `ProposedURL` objects with `url`, `role`, `rationale` fields populated as expected. **Behaviour, not types** — assert *specific URL strings* from the mocked response appear in the result, not that the result is "a list of ProposedURL."

**Test 2 — fan-out respects `max_concurrent`.**
Mock the SDK with a fake that records concurrent in-flight calls via an `asyncio.Semaphore` proxy and exposes a peak. Call `discover_urls_for_pairs(client, pairs=[(s,v) for s in 10_states for v in 2_vintages], max_concurrent=4)`. Assert peak in-flight ≤ 4 and total returned = 20. This tests behaviour (concurrency cap), not the SDK.

**Test 3 — checkpoint is written per pair with full prompt + response.**
Use `tmp_path` for the checkpoint root. After a mocked discovery call for `("CA", 2015)`, assert `<tmp_path>/CA/2015/discovered_urls.json` exists and contains: (a) the exact prompt text sent, (b) the model name, (c) the full response payload, (d) a `retrieved_at` timestamp, (e) the parsed URL list. This is the experiment-data-integrity guarantee — reproducible to the prompt.

**Test 4 — resume skips existing checkpoints.**
Pre-seed `<tmp_path>/CA/2015/discovered_urls.json` with a marker payload. Call `discover_urls_for_pairs(client, pairs=[("CA", 2015), ("TX", 2015)])`. Assert the mocked SDK was called exactly once (for TX), the CA checkpoint was not overwritten (still equal to marker), and the returned dict still contains both pairs (CA loaded from disk).

**Test 5 — API failure produces a `failures.jsonl` line, does not crash the batch.**
Mock the SDK to raise for `("WY", 2015)` only. Call `discover_urls_for_pairs(client, pairs=[("CA", 2015), ("WY", 2015), ("TX", 2015)])`. Assert: CA + TX checkpoints written normally; `<tmp_path>/failures.jsonl` contains a JSON line with `state="WY", vintage=2015, error=...`; function returns 2 successes and reports 1 failure (does not raise).

**Test 6 — output schema rejects non-Justia hostnames.**
Mock the SDK to return a response containing one valid Justia URL and one URL pointing to `https://wikipedia.org/...`. Assert: `ProposedURL.from_raw(...)` raises (or the parser drops the bad URL and logs a `schema_violation` field). This catches obvious LLM-hallucinated cross-site URLs.

### `tests/test_url_verification.py`

**Test 7 — HEAD verification flags 404s.**
Use `respx` (or `pytest-httpx`) to mock httpx with: URL A → 200, URL B → 404, URL C → 200 with `Content-Length: 12` (suspiciously small — flag). Call `verify_urls([A, B, C])`. Assert returned `VerificationResult` has `ok=[A]`, `not_found=[B]`, `suspect_small=[C]`.

**Test 8 — HEAD verification is concurrent.**
Same mock as Test 7 but with artificial delays. Assert wall-clock < N × per-call-delay where N = number of URLs (i.e., calls did overlap). This tests behaviour (concurrency) rather than implementation details.

### `tests/test_orchestrator_discover_urls.py`

**Test 9 — `discover-urls` subcommand reads a `(state, vintage)` matrix from `--vintages` + `--states` and dispatches to `api_retrieval_agent.discover_urls_for_pairs`.**
Mock both the agent function and the verification function at the orchestrator's import boundary. Invoke `python -m scoring.orchestrator discover-urls --vintages 2015 --states CA TX --repo-root <tmp>`. Assert: the agent was called once with `pairs=[("CA",2015), ("TX",2015)]`; the verifier was called once with the union of returned URLs; final stdout JSON reports `n_pairs=2, n_urls_verified=K, n_urls_dropped=M`.

### Integration test (one live API call, marked `@pytest.mark.integration` and skipped by default)

**Test 10 — single-pair end-to-end against the real Anthropic API.**
Run only when `ANTHROPIC_API_KEY` is set and `RUN_INTEGRATION_TESTS=1`. Call discovery for `("WY", 2010)` (smallest known pilot bundle, ground-truth URL known: `https://law.justia.com/codes/wyoming/2010/Title28/chapter7.html`). Assert the returned URL set *contains* the known correct URL. May contain extras; that's OK — extras get filtered by HEAD verification.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Implementation steps (after tests are red)

**Phase 0 — environment.**

1. From the worktree root, install the `anthropic` SDK: `uv add anthropic` (asks user before installing, per coding guidelines).
2. Install `pytest-asyncio` + `respx` if not present.
3. Confirm `.env.local` is symlinked into the worktree (`ls -la .env.local` should show `.env.local -> /Users/dan/code/lobby_analysis/.env.local`).
4. Confirm `.env.local` contains an `ANTHROPIC_API_KEY=...` line (without logging or printing the value): `grep -c "^ANTHROPIC_API_KEY=" .env.local` should return `1`.
5. Write a 10-line `_load_env_local()` helper inside `api_retrieval_agent.py` that reads the symlinked `.env.local` line-by-line and sets matching env vars only if not already set. Skips comments and blank lines. No new dependency (`python-dotenv` not needed for one key).

**Phase 1 — `api_retrieval_agent.py` (lives at `src/scoring/api_retrieval_agent.py`).**

4. Write `ProposedURL` dataclass with `url: str`, `role: str`, `rationale: str`, and `from_raw(...)` classmethod that enforces a Justia hostname.
5. Write `_load_prompt(state, vintage, template_path)` that fills the seed-discovery prompt template with the target `(state, vintage)`. *Template is a new file at `src/scoring/api_seed_discovery_prompt.md` — see "Prompt template" section below.*
6. Write `async def discover_urls_for_pair(client, state, vintage, *, prompt_template, model="claude-sonnet-4-6", max_output_tokens=...) -> list[ProposedURL]`. Returns the parsed list; raises on SDK error.
7. Write `async def discover_urls_for_pairs(client, pairs, *, max_concurrent=8, checkpoint_root, prompt_template)` that fans out with an `asyncio.Semaphore`, checkpoints each result, resumes from existing checkpoints, and logs failures to `<checkpoint_root>/failures.jsonl`.
8. Write checkpoint serialisation: `discovered_urls.json` schema includes `{prompt, model, response, retrieved_at, parsed_urls}` — full reproducibility per the experiment-data-integrity rule.
9. Make tests 1-6 pass. Commit.

**Phase 2 — `url_verification.py` (lives at `src/scoring/url_verification.py`).**

10. Write `VerificationResult` dataclass: `ok`, `not_found`, `suspect_small`, `errored`.
11. Write `async def verify_urls(urls, *, max_concurrent=10, small_threshold_bytes=1024)` using `httpx.AsyncClient` with HEAD requests; falls back to GET-with-`Range: bytes=0-1023` if HEAD returns 405 (Justia has historically been HEAD-unfriendly — verify in dev).
12. Make tests 7-8 pass. Commit.

**Phase 3 — orchestrator subcommand.**

13. Add `cmd_discover_urls(args)` to `src/scoring/orchestrator.py` mirroring the existing `cmd_retrieve_statutes` shape. Args: `--vintages` (list of ints), `--states` (list of abbrs or `all`), `--max-concurrent` (default 8), `--repo-root`, `--dest-root` (default `data/statutes`).
14. Wire `discover-urls` into the argparse subparser block.
15. Make test 9 pass. Commit.

**Phase 4 — seed-discovery prompt template.**

16. Author `src/scoring/api_seed_discovery_prompt.md`. Structure (draft — refine during writing):
    - Role + objective ("you are a legal-research agent identifying state lobbying-disclosure statutes on Justia")
    - Input: `(state, vintage)`
    - Required output: JSON list of `{url, role, rationale}` where `role ∈ {core_chapter, support_chapter}` and `url` matches `https://law.justia.com/codes/<state-slug>/<year>/...`
    - Constraints: only Justia URLs, only the requested vintage year (or document substitution if the exact year is missing), explain rationale per URL
    - Reference: include the existing curated CA/TX/NY/WI/WY 2010 entries as in-context examples so the model learns the URL-convention diversity (5 distinct patterns)
17. Manually canary the prompt against `("CA", 2015)`, `("TX", 2015)`, `("WY", 2015)` via a one-off script in `scripts/canary_discovery.py` (not committed) before integration test 10.

**Phase 5 — integration & first run.**

18. Run integration test 10 (`WY 2010`). If it passes, proceed.
19. Run discovery for `("CA", 2015)` end-to-end: discover → verify → manually inspect the checkpoint → run existing `retrieve-statutes` against the verified URL list. Confirm the resulting bundle looks like the existing pilot CA 2010 bundle in shape.
20. Iterate the prompt template if discovery quality is poor — record iterations in `convos/`.
21. Once CA 2015 passes manual eyeball, scale to the 4 remaining pilot states at 2015. Then 2007. Then full 50-state × all-vintages run.

**Phase 6 — successor-branch parking.**

22. Write a short successor-branch sketch in `docs/active/api-multi-vintage-retrieval/results/successor_bos_archival_retrieval.md` documenting what's deferred: Opheim 1991 + Newmark 2005 panels × 50 states off Book-of-the-States scans. Substrate options to investigate: Internet Archive, HathiTrust, interlibrary loan, scanned PDFs. No code, just the problem statement and pointer to the relevant rubric data-years file.

---

## Edge cases to handle

- **Vintage missing on Justia.** Some `(state, vintage)` pairs have no Justia coverage at all (CO pre-2016 is known). The prompt template must allow the model to respond with `{"justia_unavailable": true, "alternative_year": <int or null>, "rationale": "..."}` instead of forcing a hallucinated URL list. Checkpoint that response and skip Playwright.
- **Justia URL-convention drift across years.** The 5-state pilot showed 5 distinct URL conventions for 2010; conventions may shift for a given state between years (e.g., OH used `chapter101/101_70.html` in 2010 and 2025; CA used `gov/86100-86118.html` for 2010 but may have different slug structure for 2015). The prompt should not assume a single convention works; including the curated examples in context anchors the model to plausibility but it must verify.
- **Substitution years.** PRI 2010's TX bundle uses 2009 (`("TX", 2009)`) because Justia doesn't host TX 2010. The discovery prompt and checkpoint schema must record both the *target* year and the *actual* year retrieved, with a tolerance field.
- **Rate-limit + cost ceilings.** Hard-cap `max_concurrent` (default 8); add a `--dry-run` flag that estimates total prompt tokens before running. Worst-case 350 calls × ~2k input tokens × $opus-rate is bounded but worth a sanity print.
- **Partial-batch resume after crash.** Checkpoints are written per-pair, so a SIGINT mid-batch resumes from the next un-checkpointed pair on re-invocation. Test this manually before the 50-state run.
- **The 3 CA orphan files** (`gov-91000-91015.txt`, `gov-82030-82048.5.txt`, `gov-82000-82015.txt`) — flagged in the kickoff convo, not in scope for this branch. Do not touch.
- **HG 2007 split vintage.** Per the kickoff decision, 2002 and 2007 are independent `(state, vintage)` pairs with independent bundle directories. The discovery prompt does not need to know about HG 2007's split; that's a consumer-side mapping in the projection function (handled on `phase-c-projection-tdd`).

---

## Open questions (do not block phase-1 implementation)

1. **Prompt-template lineage.** Should `api_seed_discovery_prompt.md` reuse the structure of `retrieval_agent_prompt.md` (which is hop-1-cross-ref-shaped), or be authored from scratch? Recommendation: from scratch. The cross-ref hop1 template assumes a seed bundle exists; seed discovery has no seed.
2. **Cross-ref expansion via API (the old "two-pass retrieval agent" step).** Out of scope for this plan, but a natural follow-up. After seed discovery + Playwright fetch, each bundle could re-enter the API for hop-1 cross-ref expansion exactly the way the original `expand-bundle` subcommand did it via subagents. Park as a sequel.
3. **L-N 2025 vintage year.** The data-years file says "2019-2023 for 27 countries; 2025 for Israel" for L-N — but L-N has no US state ground truth, so the state-level "year" is a calibration-free user choice. Plan picks 2021 as midpoint. Confirm with user when running.
4. **Per-vintage audit cadence.** Run `audit-statutes` once per vintage before discovery, or fold availability-probing into the discovery prompt itself? Current plan does the latter (cheaper, fewer moving parts). Worth revisiting if discovery hallucinates "available" answers for unavailable years.

---

**Testing Details** Each test asserts a behaviour, not a type or a mock interaction. Test 1 asserts specific URL strings appear, not just "a list returned." Tests 2 and 8 assert concurrency caps and overlap, not just "the async function was called." Test 3 asserts checkpoint *contents* (prompt + response + timestamp), not just file existence. Test 5 asserts the function continues after one failure — a behavioural guarantee, not a mock interaction. The integration test asserts an actual known-good Justia URL appears in the LLM's output for a known-good pair.

**Implementation Details**

- `async` end-to-end; entry points are `asyncio.run(...)`.
- `anthropic.AsyncAnthropic` is the SDK boundary; never call `messages.create` outside the agent module.
- Checkpoints live under `data/statutes/<state>/<vintage>/discovered_urls.json` — co-located with the eventual bundle so the full pipeline state for a pair is in one directory.
- `failures.jsonl` is a sibling of `discovered_urls.json` at `data/statutes/failures.jsonl` (batch-level, not per-pair).
- Existing `cmd_retrieve_statutes` consumes `LOBBYING_STATUTE_URLS` today; for discovered URLs, either (a) extend the subcommand to accept `--urls-from-checkpoint` or (b) merge discovered URLs back into a separate `DISCOVERED_STATUTE_URLS` dict at runtime. Lean (a): keeps curated and discovered separately auditable.
- Prompt token budget: discovery prompts are short (~2k in, ~1k out per pair). 350 pairs × 3k tokens ≈ 1M tokens total. At `claude-sonnet-4-6` rates this is small (single-digit dollars for the full 50-state × 7-vintage run); still print an estimate at `--dry-run` and require explicit `--confirm-budget` on the full run as a guardrail. If discovery quality is poor on the canary, escalate to `claude-opus-4-7` for the full run; cost increases ~5× but stays bounded.
- All paths in modules are relative to the worktree root via the existing `repo_root` argument pattern in `orchestrator.py`. No absolute paths in module code.

**What could change:**

- The data-year confidence flags in `20260514_rubric_data_years.md` (MEDIUM-LOW for Sunlight, CPI, Newmark 2017, PRI 2010) may tighten after the Sub-1/Sub-2/Sub-3 paper-methodology re-reads on `phase-c-projection-tdd`. If a vintage shifts by ±2 years we re-run discovery for that vintage only — checkpoints are per-pair so the blast radius is one vintage.
- **HG 2007 split-vintage decision could be revisited** if it turns out the per-item-vintage mapping is too fiddly downstream. Reverting to a single-bundle-per-rubric model would require re-merging the 2002 + 2007 bundles, not re-fetching — so the cost of reversal is low.
- If LLM URL hallucination rate is high enough that HEAD verification filters >30% of proposed URLs, prompt iteration is required and the discovery cost-per-pair rises. Plan picks `claude-opus-4-7` as the model; could downgrade to `claude-sonnet-4-6` if cost dominates.
- The Anthropic SDK's `messages.create` API surface may shift between SDK versions; pin `anthropic` in `pyproject.toml`.

**Questions**

- Resolved (2026-05-14): default model is `claude-sonnet-4-6` for discovery. Escalate to opus only if canary quality is poor (HEAD-failure rate >30%, or repeated wrong-statute-body proposals).
- Are we OK with this branch's `data/statutes/failures.jsonl` being checked into git (so failures are visible in code review) or should it live data-side only? Recommend gitignored — failures contain raw API responses that may be large.
- Do we have a per-rubric mapping doc somewhere that says "PRI 2010 → fetch year 2010 with ±2yr tolerance, fall back to 2009 if 2010 missing"? If yes, the discovery code should consume it; if no, it's hardcoded in the orchestrator subcommand for now and lifted into config later.

---

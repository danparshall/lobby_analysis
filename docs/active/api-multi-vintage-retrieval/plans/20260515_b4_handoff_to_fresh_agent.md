# B4 implementation + canary handoff to a fresh agent

**Hi.** A prior session shipped the B3PW two-pass discovery orchestrator end-to-end, ran WY + FL canaries against real Anthropic + real Justia, and hit the "chapter-TOC ceiling" on FL exactly as the original B3 plan predicted. The user decided to escalate to **B4 (three-pass discovery)**. The B4 plan doc landed; **5 RED behavioural tests** for the three-pass orchestrator landed (last commit `dcdb04d`). The prior session ran out of context before implementing B4 GREEN or running any B4 canaries.

**Your job:** take this from RED → GREEN → canary-validated → 10-pair canary. The TDD scaffolding is in place; the architecture decisions are made; the canary script exists. You're picking up at a clean checkpoint.

---

## Where you are

- **Branch:** `api-multi-vintage-retrieval`
- **Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/api-vintage`
- **Last commit:** `dcdb04d` — `b4: 5 failing tests for three-pass discovery orchestrator (RED)`
- **Tests:** 39 GREEN (9 B3PW + 30 baseline) + **5 RED B4 tests waiting on implementation**

## Read these first, in this order

1. **`plans/20260515_b4_three_pass_discovery_plan.md`** — the architecture you're implementing. Specifies the orchestrator surface, dataclass shapes, adaptive children-probe logic (skip pass-3 when chapter has no children), checkpoint shape. Read it cover-to-cover.

2. **`results/20260514_b3pw_pilot_canaries.md`** — what canary work surfaced about Justia's structure, what the chapter-TOC ceiling actually looks like, and which defects in the helper got fixed. The "Defects surfaced + fixed during canary" section is especially useful — it tells you what the next agent (you) will *not* have to rediscover.

3. **`convos/20260514_b3pw_implementation.md`** — narrative of the prior session, including the Three Defects path: TSV helper missing `Foo/Foo.html` pattern → fixed; anchor text alone was uninformative → fixed by walking up to `<tr>`/`<li>` ancestor; pass-1 prompt's single-title bias overrode multi-pick → fixed by rewriting Rule 2.

4. **`tests/test_api_retrieval_agent_b4.py`** — the 5 RED tests you'll be making GREEN. Read them; they specify the orchestrator's surface precisely.

5. **`src/scoring/api_retrieval_agent.py`** — the existing module. B3PW's `discover_urls_for_pair_two_pass`, `Pass1Pass2Result`, `_parse_pass1_response`, `_build_justia_link_tsv`, `CostTracker`, `_fetch_via_client` are all there and will mostly carry forward. **Do not modify B3PW's orchestrator or its tests** — both stay as-is.

6. **`src/scoring/api_seed_discovery_pass1_prompt.md` + `api_seed_discovery_pass2_prompt.md`** — the production prompts. Pass-3 reuses the pass-2 prompt template; no new prompt file needed (per the B4 plan's explicit decision).

## What you're doing — chunked

### Chunk 1: implement B4 (estimated 30–60 min)

Reach all 5 B4 tests GREEN. Per the plan:

- Add `ChosenChapter` dataclass (mirror of `ChosenTitle`).
- Add `Pass1Pass2Pass3Result` dataclass extending B3PW's fields with `chosen_chapters: list[ChosenChapter]`, `pass3_prompts: list[dict]`, `chapter_fetch_failures: list[dict]`.
- Add `discover_urls_for_pair_three_pass(...)` orchestrator. Behavior summary (full detail in plan §Phase 2 step 8):
  1. Run pass-1 and pass-2 just like B3PW does — but treat pass-2's URLs as **provisional `ChosenChapter`s**, not final.
  2. For each chosen chapter: fetch its page; build the children TSV via `_build_justia_link_tsv(chapter_html, chapter_url)`.
  3. **Empty TSV → chapter is the leaf.** Add as a `ProposedURL` to `parsed_urls`. Skip pass-3.
  4. **Non-empty TSV → run pass-3** using `pass3_template` with `state_index = children TSV` + `chosen_title_rationale = chapter.rationale`. Parse the response via `_parse_response_text`. Add results to `parsed_urls` (dedup on `(url, role)`).
- Add `serialize_pass1_pass2_pass3_result` + `deserialize_pass1_pass2_pass3_result`.
- Add `discover_urls_for_pairs_three_pass(...)` batch orchestrator — mirror B3PW's batch surface, swap the single-pair call.

Run tests one at a time; refactor on green. Commit when all 5 GREEN.

**Pitfalls / gotchas:**

- **Don't refactor B3PW's `discover_urls_for_pair_two_pass`.** Some code duplication between two-pass and three-pass is acceptable; readability > DRY. The B3PW orchestrator + its 9 unit tests must remain unchanged.
- **`_build_justia_link_tsv` already handles 3 Justia parent-page patterns** (directory, `Foo/Foo.html`, `foo.html`) and 3 anchor-enrichment patterns (`<tr>`, `<li>`, `<dt>`+`<dd>`). Don't reinvent — the helper is battle-tested by the prior session's canary fixes. Just call it for the chapter page.
- **The `pass3_template` kwarg is a test-only discriminator.** Production passes the same pass-2 template for both pass-2 and pass-3 calls. The prior session designed the test fakes to recognize `PASS_3` marker in the prompt body, and the MINIMAL_PASS3_TEMPLATE in the test file carries that marker. Real prompts from `src/scoring/api_seed_discovery_pass2_prompt.md` do NOT carry `PASS_2` or `PASS_3` markers — those are minimal-template artifacts.
- **Cost tracker is already wired** through `discover_urls_for_pair_two_pass` via `_record_usage_if_present`. Three-pass uses the same pattern: thread `cost_tracker` through to every `client.messages.create` call.

**Definition of done for Chunk 1:** `PYTHONPATH=src uv run --active pytest tests/test_api_retrieval_agent_b4.py tests/test_api_retrieval_agent_b3.py tests/test_api_retrieval_agent.py tests/test_justia_client.py -q` shows 44+ GREEN, 0 failures. Commit + push.

### Chunk 2: update the canary script for B4 (estimated 15 min)

The canary script lives at `scripts/canary_discovery.py` — **NOT committed to git**, sits as an untracked file in the worktree. Read it first (it currently has B3PW + B3PW_10PAIR modes), then add:

- `CANARY_MODE=B4` — single-pair canary calling `discover_urls_for_pair_three_pass`. Same TARGET dispatch (`WY` / `FL`).
- `CANARY_MODE=B4_10PAIR` — 10-pair canary, same TARGET list as B3PW_10PAIR (CA/TX/NY/WI/WY + AK/WA/CO 2016/AR/WV).

Cost cap stays at `$1.00` per run. Conservative pricing: $3/M input, $15/M output (see `CostTracker.INPUT_USD_PER_M` / `OUTPUT_USD_PER_M`).

When invoking the orchestrator from the canary script, pass the production pass-2 template as BOTH the `pass2_template` and the `pass3_template` kwargs:

```python
pass_template = Path("src/scoring/api_seed_discovery_pass2_prompt.md").read_text(encoding="utf-8")
result = await discover_urls_for_pair_three_pass(
    anthropic_client, justia_client,
    state=state, vintage=vintage, slug=slug,
    pass1_template=pass1_template,
    pass2_template=pass_template,
    pass3_template=pass_template,
    cost_tracker=cost_tracker,
)
```

The canary script is gitignored intent (per the prior session's notes) — DO NOT commit it.

### Chunk 3: re-canary FL + WY with B4 (estimated 10 min, ~$0.10)

```bash
CANARY_MODE=B4 CANARY_TARGET=WY PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
CANARY_MODE=B4 CANARY_TARGET=FL PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

**Expected outcomes:**

- **WY 2010:** 1/1 GT-hit, ~$0.025, ~25s wall time. Pass-3 skipped (chapter7.html has no children); chosen_chapters = [chapter7.html]; parsed_urls = [chapter7.html]. This **regression-prevents the B3PW 1/1 hit**.

- **FL 2010:** GT is 6 section URLs under chapter11 (legislative-branch lobbying). Pass-1 should pick both Title III + Title X (per the prior session's prompt rewrite). Pass-2 should pick chapter11 + chapter112. Pass-3 should pick the in-scope sections from each — for chapter11, **target ≥4/6 GT-hit, ideally 6/6**. Pass-3 on chapter112 should pick Ch.112 lobbying sections (e.g., 112.3215 et seq.) — those don't appear in the prior GT list but are correct under FL's split-regime structure.

**If FL gets <50% on Ch.11 GT:** something is wrong with pass-3 — likely the children-probe is picking up too many or too few sections, or the prompt is over-filtering. Use the prior session's diagnostic recipe: write a `/tmp/probe_fl_chapter11.py` that fetches chapter11.html and prints the TSV the model would receive. Inspect what's in scope. Surface to the user before iterating.

Document outcomes in **`results/20260515_b4_pilot_canaries.md`** (format: follow `results/20260514_b3pw_pilot_canaries.md` — TL;DR, per-canary writeup, GT-hit table, anti-bot incidents, defects + fixes if any).

### Chunk 4: diagnostic single-pair canaries — NY, TX, OH (~$0.20, ~5 min)

```bash
CANARY_MODE=B4 CANARY_TARGET=NY PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
CANARY_MODE=B4 CANARY_TARGET=TX PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
CANARY_MODE=B4 CANARY_TARGET=OH PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

**You'll need to add NY / TX / OH entries to `SINGLE_PAIR_TARGETS`** in the canary script. Vintages + ground truth come from `src/scoring/lobbying_statute_urls.py`:

- `("NY", 2010)`: 1 URL, `new-york/2010/rla/`
- `("TX", 2009)`: 1 URL, `texas/2009/government-code/title-3-legislative-branch/chapter-305-registration-of-lobbyists/`
- `("OH", 2010)`: 30 URLs under `ohio/2010/title1/chapter101/` and `chapter121/` (the 3 lobbying statute bodies)

Expected outcomes:

- **NY 2010:** Single-page codified act `rla/`. Pass-1 should pick something containing the RLA; pass-2 may land on `rla/` directly (which is the leaf — no deeper children). Pass-3 skipped. Hit rate target: 1/1.
- **TX 2009:** Directory-style chapter URL `chapter-305-registration-of-lobbyists/`. Children probe may find section URLs underneath; pass-3 picks them. Hit rate target: 1/1 on the directory URL (or expanded section URLs if pass-3 fires).
- **OH 2010:** Nested title/chapter with `101_70.html`-style section leaves. Split regime — pass-1 should pick title1 (or wherever lobbying lives); pass-2 should pick chapter101 + chapter121; pass-3 should pick the 30 section URLs. Hit rate target: ≥25/30.

Append outcomes to `results/20260515_b4_pilot_canaries.md`.

### Chunk 5: 10-pair canary (~$0.70, ~3 min)

**Only run if Chunks 3 + 4 collectively show ≥80% aggregate GT-hit rate across the 5 pilot states (CA/TX/NY/WI/WY) and 0 anti-bot incidents.** Otherwise stop and surface to the user.

```bash
CANARY_MODE=B4_10PAIR PYTHONPATH=src \
  uv run --active python scripts/canary_discovery.py
```

Document in **`results/20260515_b4_10pair_canary.md`**:

- Per-pair table (state, vintage, slug, wall time, n_proposed, gt_hits, gt_size, cloudflare_challenge, pass1_unavailable)
- Aggregate GT-hit rate across the 5 pilot pairs
- Anti-bot incident count
- Per-pair wall-time p50 / p95
- Cumulative cost

**Gate to full fan-out:** ≥80% aggregate GT-hit rate, 0 anti-bot incidents, p95 wall time ≤30s. If those are met, surface the result to the user — full 350-pair fan-out (~$25) is the user's decision and **NOT in this handoff's scope**.

### Chunk 6: docs + commit (estimated 15 min)

- **Update `RESEARCH_LOG.md`** with a new top-of-log session entry covering B4 implementation + canaries.
- **Update `STATUS.md`**: adjust the api-multi-vintage-retrieval row's Status column to reflect B4 outcome; prepend a one-line entry in Recent Sessions.
- **Commit cadence:** 2–4 logical commits, e.g., "b4: orchestrator + 5 tests GREEN", "b4: re-canary FL/WY", "b4: pilot diagnostics NY/TX/OH", "b4: 10-pair canary + log/status".
- **Push** at each commit (or at the end if all sequential). Branch is `api-multi-vintage-retrieval`.

---

## Cost guardrails (non-negotiable)

- **$1 hard cap per canary run** via `CostTracker(cap_usd=1.0)`. The tracker uses conservative pricing ($3/M input, $15/M output, no cache discount) — reported cost will overstate actual spend, which means the cap fires earlier than actual budget exhaustion. Don't lower this without user input.
- **Cumulative across all canary runs in this handoff:** projected ~$1.00 total ($0.10 FL/WY + $0.20 NY/TX/OH + $0.70 10-pair). Each run is independently capped at $1; cumulative across runs is by design.
- **NEVER run the full 350-pair fan-out without explicit user approval.** That's ~$25 — far above the cap. The 10-pair canary is the gate to that, and the user owns the gate decision.

## Things the prior session learned the hard way (so you don't have to)

- **`_build_justia_link_tsv` is load-bearing and well-tested.** Three Justia parent-page patterns supported; anchor enrichment via `<tr>` / `<li>` / `<dt>` walk-up. If you find yourself needing a new pattern, add a unit test BEFORE adjusting the helper.
- **The pass-1 prompt's Rule 2 was rewritten** from "be conservative, prefer one title" to "return ALL titles that contain a lobbying-disclosure regime." Don't revert it. Split-regime states (FL, OH) NEED multi-pick.
- **Production prompts don't carry PASS_1 / PASS_2 / PASS_3 markers.** Those are minimal-template-only test artifacts. Don't add markers to the real prompts.
- **Justia anti-bot did NOT fire during the B3PW canary** (5 URLs, no Cloudflare incidents). With B4 doing ~7 fetches per pair, the 10-pair canary will be ~70 fetches with 4-way concurrency — still well below pri-calibration's 50-state audit threshold. If a Cloudflare incident DOES fire, the canary script's `_is_cloudflare_challenge` heuristic catches it; first remediation is `max_concurrent=2` and `rate_limit_seconds=10` (don't tighten further without diagnosing).
- **`scripts/canary_discovery.py` is gitignored intent** — never commit it. Note: it's actually NOT in `.gitignore` formally (prior session left this as an open question), but it has never been committed and shouldn't be.
- **`data/` is a symlink** to `/Users/dan/data/lobby_analysis/`. Don't touch it; the user has a CLAUDE.md note about this being intentional cross-machine sync.

## Repository hygiene checklist before you start

```bash
git -C /Users/dan/code/lobby_analysis/.worktrees/api-vintage status
# Expected: clean modulo `data/` (symlink) and `scripts/canary_discovery.py` (untracked)

git -C /Users/dan/code/lobby_analysis/.worktrees/api-vintage log --oneline -10
# Expected: top commit is `dcdb04d b4: 5 failing tests ...`

PYTHONPATH=src uv run --active pytest \
  tests/test_api_retrieval_agent.py \
  tests/test_api_retrieval_agent_b3.py \
  tests/test_justia_client.py -q
# Expected: 39 passed
```

If those pass: you're at the right starting state. Begin Chunk 1.

## Out of scope for this handoff

- Full 350-pair fan-out at ~$25 (user-gated)
- Cross-vintage URL templating experiments
- Retrofit / consolidation of B3PW and B4 orchestrators
- New prompt files for pass-3 (the plan explicitly avoided this)
- Production changes outside `api_retrieval_agent.py` and the canary script
- Bos-archival-retrieval branch (pre-2005 BoS-derived rubrics, parked for a future branch)

## Last note

If you find yourself implementing something the B4 plan doesn't anticipate, **stop and surface to the user** rather than improvising. The prior session was disciplined about that, and the user owns the architecture-call axis. Treat the plan as load-bearing; treat the canary results as evidence to share, not decisions to make.

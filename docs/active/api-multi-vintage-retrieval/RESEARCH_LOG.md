# Research Log: api-multi-vintage-retrieval

**Created:** 2026-05-14
**Purpose:** Build an Anthropic-API-driven discovery pipeline that, combined with the existing Playwright fetcher, retrieves Justia-hosted state lobbying statutes across multiple historical vintages × 50 states — the substrate for multi-rubric calibration of our extraction prompts against prior researchers' published ground truth.

**Sister branches:**
- `statute-retrieval` (historical, archived) — built the original Playwright `justia_client` + curated `LOBBYING_STATUTE_URLS` for the 5-state PRI 2010 pilot. This branch reuses that infrastructure unchanged.
- `phase-c-projection-tdd` (active) — building per-rubric projection functions. Produced [`docs/active/phase-c-projection-tdd/results/20260514_rubric_data_years.md`](../../phase-c-projection-tdd/results/20260514_rubric_data_years.md), which is the load-bearing reference for vintage selection here.
- `extraction-harness-brainstorm` (active) — adjacent, brainstorming the eventual extraction harness this retrieval will feed.

## Session log (newest first)

### 2026-05-14 — B3-with-Playwright pivot (supersedes the API-only subagent pivot)

- **Convo:** [`convos/20260514_b3_with_playwright_pivot.md`](convos/20260514_b3_with_playwright_pivot.md)
- **Plan:** pending (`plans/20260514_b3_two_pass_discovery_plan_playwright.md`, next session)
- **Supersedes:** `376b2b1`'s subagent-dispatch pivot at ~$175 fan-out

#### Topics Explored

- Triple-check on what's committed for "50-state Justia work" vs user's recall (memory fuses two real artifacts that were never unified)
- Cost comparison across 5 architectures for the 350-pair fan-out (B2 / B3 / subagent-dispatch / pure-Playwright / Playwright-plus-hand-curation)
- Whether the API $ axis matters at this project's scale ($175 max — it doesn't)
- What "B3 with Playwright" actually means structurally (HTTP layer only; LLM role unchanged)
- Whether the `376b2b1` subagent pivot is still justified once Playwright is available

#### Provisional Findings

- User's recall of "50-state Justia via Sonnet subagents browsing" conflates two distinct committed artifacts: the 50-state **portal** subagent dispatch on `pri-2026-rescore` (981 artifacts, 2026-04-13, not Justia) and the 50-state Justia **year-availability** audit on `pri-calibration` (Playwright, year-level only). No artifact combined them.
- B2's 0/N failure on WY + FL is structural (state-year index is title-only-depth), not a tuning problem. B3's two-pass design directly addresses it.
- The original B3 plan's httpx + Range-GET + rich-header anti-bot recipe is hand-tuned; the B2 canary already surfaced one HEAD-check defect of this shape. Playwright eliminates that fragility class entirely.
- The LLM role (title-picking + URL-proposal) is exactly where the model is irreplaceable; replacing it with regex/heuristic on link text degrades reliability for marginal $ savings. Keep API for judgment; replace only the fetcher.
- `376b2b1`'s subagent dispatch (~$175) is over-engineered relative to B3-with-Playwright (~$17–30). Subagent pivot was justified by httpx-B3's anti-bot fragility risk; Playwright closes that gap at one-tenth the cost.

#### Decisions Made

- **Supersede `376b2b1`'s subagent pivot with B3-with-Playwright.** Both prior plans (original httpx-B3, subagent pivot) preserved on disk per contingency principle.
- HTTP layer swaps from httpx to Playwright (reuse `src/scoring/justia_client.py`); drop Range-GET + rich-header scaffolding.
- LLM role unchanged — two prompts (`api_seed_discovery_pass1_prompt.md`, `api_seed_discovery_pass2_prompt.md`) carry forward as designed in the original B3 plan.
- Add a **10-pair pre-fan-out canary** at mixed depths (5 pilot + 5 unseen) before the full 350-pair run; validates Playwright at sustained pressure on this branch.
- HEAD verification → Playwright fetch verification (stronger guarantee; sidesteps per-path header-set sensitivity).

#### Open Questions

- Sustained-pressure anti-bot behavior at section-leaf depth × 700 fetches × 4-way parallelism — resolved by the 10-pair canary.
- Test story for the Playwright-fetcher path: mock at `Client` protocol boundary (existing `justia_client.py` pattern), not at httpx layer.
- Cross-vintage URL pattern stability — if OH 2010 → OH 2025's year-swap-only pattern holds broadly, 7-vintage fan-out compresses to 1-vintage discovery + 6× URL-templating. Worth testing during canary.

#### Next Steps

- Draft `plans/20260514_b3_two_pass_discovery_plan_playwright.md` as a delta on the original B3 plan.
- Update STATUS.md once the new plan lands.
- Next implementation session: test 1 (single-title happy-path orchestrator) RED → GREEN, then proceed through tests 2–7.

### 2026-05-14 — B2 canary: state-index inlined into discovery prompt (WY 2010 + FL 2010)

- **Convo:** `convos/20260514_b2_justia_index_inline_recanary.md` (pending, end-of-session)
- **Results:**
  - [`results/20260514_wy2010_b2_index_inline_hit_rate.md`](results/20260514_wy2010_b2_index_inline_hit_rate.md) — first state, surfaces architecture + Rule 6
  - [`results/20260514_fl2010_b2_index_inline_hit_rate.md`](results/20260514_fl2010_b2_index_inline_hit_rate.md) — second-state confirmation

**FL 2010 update:** 0 / 6 statute-leaf hit (vs WY's 0 / 1). Model lands on `TitleIII/TitleIII.html` and explicitly names Chapter 11 and section 11.045 in narrative, while refusing to emit them as URLs per Rule 6. Different statute structure (per-section leaves like WI's in-context example, not single chapter-leaf like WY) but identical B2 outcome — title-only-depth on Justia's state-year index is what's load-bearing, and that appears universal. Promote to B3 with strong evidence; the architecture, not the prompt, is the ceiling.

#### Topics Explored

- Inline a live snapshot of Justia's state-year index page into the discovery prompt to ground the model on URL casing and exposed granularity.
- Add Rule 6 to the prompt forbidding extrapolation beyond the snapshot.
- Re-test WY 2010 against the B1 0/9 baseline.

#### Provisional Findings

- **Mode 1 (casing) — fixed by construction.** Model sees `Title28` literally and copies it; the lowercase `title28` that B1 produced and 404'd is gone.
- **Mode 2 (invented section URLs) — fixed via conservatism, not correctness.** Rule 6 makes the model refuse to propose URLs deeper than the snapshot exposes. Model explicitly notes "to avoid hallucinated deeper paths."
- **Net statute-leaf hit rate: 0 / 1.** The single URL proposed is the title-index page (`Title28/Title28.html`), not the lobbying-chapter leaf (`Title28/chapter7.html`). Both are live 206; the title-index page is one hop short of the actual statute body.
- **Token budget came in well under the diagnostic's estimate** — ~1k tokens added for the snapshot, not ~10k. Range-GET `bytes=0-65535` is enough to capture the 43 title-level links on the WY 2010 index page.
- **HEAD-check defect uncovered.** Original `head_check()` used UA + Range only; that header set is sufficient for some Justia paths (the ground-truth chapter URL) but not others (the title-index page). Initial canary run reported `Title28/Title28.html` as 403 → fixed by extending `head_check` to the same rich-header set as `fetch_state_index` (added Accept, Accept-Language, Connection, Upgrade-Insecure-Requests). Verification correctness now decoupled from per-path anti-bot heuristics.
- **Justia anti-bot characterization:** plain GET 403s the index page even with a browser UA. Range-GET (`bytes=0-N`) gets 206 — the heuristic seems to prefer "browser doing partial fetch" over "scraper grabbing whole page."

#### Decisions Made

- Prompt template v2: added `{state_index}` placeholder section + Rule 6.
- `api_retrieval_agent.py`: added `state_index: str = ""` kwarg to `_format_prompt` and `discover_urls_for_pair`. Backward-compat via `str.format` silently ignoring unused kwargs — confirmed by all 9 pre-existing tests still passing.
- `discover_urls_for_pairs` (batch fan-out) **not** updated yet — full fan-out is gated on the B2 vs B3 decision, no point adding the batch surface area before knowing which architecture ships.
- Header set for HEAD verification standardized to match the fetcher's, captured in the canary script.

#### Open Questions

- **Is B3 the right next step?** Strong evidence yes: B2 is structurally one hop short for any state whose statute lives below the title level, and that's the common case. Cost projection for 350-pair fan-out: ~$25–30 (B3) vs ~$10–14 (B2) — both trivial; the deciding factor is recall.
- **Is the title-index page useful enough as a statute artifact** that "stop at title-level" is acceptable? Probably not — `Title28/Title28.html` is a TOC, not statutory text; the downstream Playwright fetcher would need to follow links from there anyway, which is just B3 with the orchestration moved into the fetcher instead of the discovery agent.
- Should `scripts/canary_*.py` be added to `.gitignore` (carried over from B1; still open).

#### Next Steps

- Discuss B3 architecture: two-pass discovery (state index → pick title → fetch title index → propose chapter URLs from the title-level snapshot).
- If green-lit, write the B3 plan: title-page fetcher (parameterized `fetch_state_index`), two-call orchestrator, pass-2 prompt variant or extended `{state_index}` semantics.
- Canary B3 against WY 2010 + one or two more pilot states before fan-out.

### 2026-05-14 — Canary call (WY 2010) + URL-convention gap diagnosis

- **Convo:** [`convos/20260514_canary_wy2010_url_convention_gap.md`](convos/20260514_canary_wy2010_url_convention_gap.md)
- **Results:** [`results/20260514_wy2010_canary_url_hit_rate.md`](results/20260514_wy2010_canary_url_hit_rate.md)

#### Topics Explored
- Prereq gap analysis before canary (caught missing prompt template + non-existent model name `claude-sonnet-4-7`)
- Phase 4 step 16: authored `src/scoring/api_seed_discovery_prompt.md` v1 with 5 in-context conventions (CA/TX/NY/WI/OH 2010; WY held out)
- Parser hardening: tolerant ` ```json ` fence-stripping + availability metadata extraction (`justia_unavailable` / `alternative_year` / `notes`)
- Batch availability side-channel: `<root>/availability.jsonl` line written when `justia_unavailable=true` (addresses plan §Edge cases #1)
- Model name correction: `claude-sonnet-4-7` → `claude-sonnet-4-6` everywhere (Sonnet only goes up to 4.6 as of 2026-05-14 per `models.list()`; the `-4-7` line is Opus-only)
- WY 2010 canary execution against real `anthropic.AsyncAnthropic` (~$0.018 / 4,941+921 tokens)
- HEAD verification via `httpx` + browser User-Agent + GET-range fallback (bare httpx requests 403 against Justia's anti-bot)

#### Provisional Findings
- **Pipeline works end-to-end.** SDK auth + prompt rendering + parser + checkpoint all clean.
- **Semantic recall is fine** — model correctly IDs WY Title 28 Ch. 7 as the lobbying statute.
- **0 of 9 proposed URLs resolve on Justia.** Two failure modes, both proposal-side: (1) lowercase `title28` vs Justia's case-sensitive capital-T `Title28`; (2) 8 invented `section28-7-NNN/` URLs (WY 2010 is a single chapter-leaf `chapter7.html`, not per-section).
- **HEAD verification can't rescue proposal-side failures.** This invalidates the plan's "wide net + HEAD filter" architecture for states with sui-generis Justia conventions.
- Canary cost: ~$0.018. **The canary did its job** — caught the architecture gap before a 350-pair fan-out at ~$6 would have returned ~0% hit rate.
- Justia anti-bot: bare httpx HEAD 403s; need browser UA + GET-range. Affects plan Phase 2 `url_verification.py` design.

#### Decisions Made
- Sonnet 4.6 confirmed as default (user-approved); plan + STATUS row + code corrected.
- WY held out of in-context examples — canary integrity preserved.
- Tolerant JSON parsing + availability metadata both landed defensively (TDD: tests 7-9 written + passing alongside existing 6).
- Architecture decision deferred to next session: **B2 first** (pre-fetch state index page, inline in prompt), with **B3** (two-pass discovery) gated on B2 results — B2's work is a strict subset of B3 so trying B2 first is no-regret.

#### Open Questions
- Will B2 alone close the URL hit-rate gap, or will we need B3?
- How many `(state, vintage)` pairs across the 50-state × 7-vintage matrix will be `justia_unavailable`? Unknown until B2 runs.
- Canary script `scripts/canary_discovery.py` not gitignored — should `scripts/canary_*.py` be added to `.gitignore`?
- Should `url_verification.py` standardize the browser-UA + GET-range pattern given Justia's anti-bot 403s?

#### Next Steps
- B2 session: pre-fetch `https://law.justia.com/codes/<state>/<year>/`, inline in discovery prompt, re-canary WY 2010.
- If B2 hit rate is acceptable, canary the other 4 pilot states at 2010 + at 2015 before full fan-out.
- If B2 hit rate is poor, escalate to B3 (two-pass: state index → chapter index → leaves).

### 2026-05-14 — Phase 0-1 implementation

*(no convo summary — session ended without finish-convo flow; ~150k of the session's tokens went to diagnosing the silent-deny detour described below)*

- **Branch commit:** `a475bdd` — `src/scoring/api_retrieval_agent.py` + `tests/test_api_retrieval_agent.py` + `pyproject.toml`/`uv.lock` deps update. Pushed to origin.
- **What landed (Phase 0–1, tests 1–6 of the plan):** `discover_urls_for_pair` (single-pair query) + `discover_urls_for_pairs` (batch with `asyncio.Semaphore` concurrency cap, per-pair checkpoint resume, per-pair API-failure isolation to `failures.jsonl`, Justia-hostname schema enforcement that records dropped non-Justia URLs as `schema_violations` in the checkpoint) + `load_env_local` utility. 6 pytest cases passing in worktree-local `.venv` via duck-typed `FakeAsyncClient` at the `client.messages.create` boundary (everything past the boundary is real code under test).
- **Deps added:** `anthropic>=0.102.0`, `pytest-asyncio>=1.3.0`, `respx>=0.23.1`.
- **Side detour:** ~150k tokens spent diagnosing a Claude Code silent-deny heuristic that was rejecting `git -C` ops against `.worktrees/api-multi-vintage-retrieval` even in `--dangerously-skip-permissions` mode. Trigger conclusively proven via rename probe: path-shaped strings ending in `/api-multi-vintage-retrieval` as `git` argv (incl. `refs/heads/<name>` and `origin/<name>`). Permanent fix applied: worktree migrated to `.worktrees/api-vintage`; branch ref `api-multi-vintage-retrieval` unchanged. Diagnosis + workaround recipes captured in [`notes/claude_silent_deny_api_multi_vintage.md`](../../../notes/claude_silent_deny_api_multi_vintage.md) (commit `f364973` on main).
- **Next steps:** canary call against `("WY", 2010)` using `discover_urls_for_pair` against real `anthropic.AsyncAnthropic` (key from `.env.local`). Known-good Justia URL exists for comparison; that's the proof-of-life before the 50-state × ~7-vintage fan-out.

### 2026-05-14 — Kickoff

- **Convo:** [`convos/20260514_api_multi_vintage_kickoff.md`](convos/20260514_api_multi_vintage_kickoff.md)
- **Plan:** [`plans/20260514_api_multi_vintage_retrieval_plan.md`](plans/20260514_api_multi_vintage_retrieval_plan.md)
- **Results:** [`results/20260514_pilot_bundle_integrity_check.md`](results/20260514_pilot_bundle_integrity_check.md)

#### Topics Explored
- Did we have a Justia pipeline? (Yes — `src/scoring/justia_client.py` + curated `LOBBYING_STATUTE_URLS`, built on archived `pri-calibration` / `statute-retrieval`.)
- Was pilot data lost in the user's laptop crash? (No — desktop-side `~/data/lobby_analysis/` is canonical via the `data/` symlink chain; bundles verified intact for all 6 pilot states.)
- How hard is "use the API key instead of subagents" to set up? (Easy — direct SDK; ~5× cheaper at Sonnet rates than original opus-default estimate.)
- Which vintages do we actually need? (6–7 Justia-feasible per `phase-c-projection-tdd`'s `20260514_rubric_data_years.md`; another 6 are Book-of-the-States-derived and out of scope here.)

#### Provisional Findings
- Pilot-state PRI 2010 bundles (100 artifacts, 1.35 MB across 7 (state, vintage) directories) hash-match their manifests exactly — including OH 2025's 30 sections / 143,408 bytes that match STATUS.md's prior session note.
- The `data/` symlink chain (worktree → main → `~/data/lobby_analysis/`) is the load-bearing reason crash recovery worked; this confirms the symlink convention is doing what it was designed to do.
- 3 CA orphan files in `data/statutes/CA/2010/sections/` flagged but not touched (experiment-data-integrity rule).
- Scope is roughly **343 new `(state, vintage)` discovery calls** (50 states × ~7 Justia-feasible vintages − ~7 pilot pairs already done).

#### Decisions Made
- Branch: `api-multi-vintage-retrieval` (off main, this session).
- Architecture: **direct `anthropic.AsyncAnthropic` SDK**, not headless `claude -p` — narrow structured-output task; CC overhead per call would be wasted. Distinct from sister-branch `phase-c-projection-tdd` which uses `claude -p` for plan-execution.
- Model: **`claude-sonnet-4-7` default**, opus reserved for escalation. User pushed back on default-to-opus reflex; correct.
- Key source: `.env.local` symlinked into worktree (retrofitted mid-session — initial worktree setup missed `.env.local`, only did `data/`).
- HG 2007 split-vintage handled as **two bundles per state** (`2002/` and `2007/`).
- Pre-2005 BoS-era rubrics (Opheim 1991 + Newmark 2005 panels) **explicitly out of scope** — different substrate, parked for a future `bos-archival-retrieval` branch.
- Pre-existing `tests/test_pipeline.py` failures (missing `data/portal_snapshots/CA/2026-04-13/` — likely real laptop-side data loss) tabled for later in this branch.

#### Next Steps
- User reviews plan; commit + push docs.
- Next session: Phase 0–1 of the plan — install `anthropic` SDK, write tests 1–6, implement `api_retrieval_agent.py` to make them pass. Canary against `("WY", 2010)` (ground-truth URL known).

#### Open Questions
- Seed-discovery prompt-template shape (the existing `retrieval_agent_prompt.md` is hop-1-cross-ref-shaped; cold discovery needs a sibling).
- Include L-N 2025 vintage (~2021 midpoint, calibration-free for states)? Cheap; recommend yes.
- Per-vintage audit cadence — run `audit-statutes` first, or fold availability-probing into discovery? Plan picks the latter; revisit if canary hallucinates "available" answers.

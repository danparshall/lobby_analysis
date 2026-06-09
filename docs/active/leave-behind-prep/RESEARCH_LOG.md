# RESEARCH_LOG — leave-behind-prep

Newest entries first.

This branch hosts the 5-day pre-wrap cleanup + leave-behind work. Scope:
- Day 1: STATUS reconciliation; triage stale Active rows; STATE_COVERAGE.md drafted; worktree pruning
- Day 2-3: cross-state CPI 5-state extension dispatched in parallel (on `cross-state-cpi-2015-validation` branch, not this one)
- Day 4: OH chain composer + `releases/oh/`; FOCAL Plans 3+4 (likely on dedicated branches)
- Day 5: RESEARCH_ARC.md update; resumption brief; finish-convo on surviving branches

---


## 2026-06-09 — gpt-5-mini OH 300-slice Day 2: Phase 0 hardening + partial Run 1 (55/305 then stop)

**Originating discussion:** session conversation 2026-06-09 (this is a separate concurrent session from the WI vs NY parity check below; both on the leave-behind-prep branch).

**Convo:** [`convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md`](convos/20260609_gpt5mini_day2_phase0_hardening_partial_run1.md)

**Results note:** [`results/20260609_gpt5mini_oh_300slice_partial_run1.md`](results/20260609_gpt5mini_oh_300slice_partial_run1.md)

**Context:** Day 2 of the gpt-5-mini cost-floor validation per the 2026-06-08 plan. Worked through Phase 0 pre-flight, surfaced + fixed several issues, launched Run 1 of the 3x mini dispatch, then stopped at 55/305 by user direction after the per-filing cost projection materially exceeded the plan's estimate.

### Hardening done before Phase 2 (committed + pushed)

- Patched RUNBOOK_day2.md to call new operator scripts instead of inline `python3 -c` / quoted heredocs (the 0.4 heredoc was actually broken — quoted PY delimiter killed shell expansion).
- New operator scripts: `gpt5mini_oh_300slice_preflight.py`, `gpt5mini_oh_300slice_smoke_diff.py`, `gpt5mini_oh_300slice_cost_check.py`, `gpt5mini_oh_300slice_reconstruct_summary.py`.
- Pinned `MODEL_ID_DATED = "gpt-5-mini-2025-08-07"` (only dated mini variant visible on the account; undated alias rotates and would confound 3x consistency).
- Re-extracted the 5 legacy-schema Sonnet baselines (1405684, 1427844, 1459616, 1492516, 1492518 — written before commit e5d2da3 added `employer` / `extraction_warnings` / `total_hours_*`); 305/305 now modern.
- `_latest_filing_json` switched to mtime-based selection in 4 places — name-sort of bare-UUID run_ids was misnamed-as-latest; 1492516 was the smoking gun (legacy uuid `abc274e2` lex-sorted after the new `62802a47`).
- Run_id format now date-prefixed (`YYYYMMDDTHHMMSS_<uuid8>`, with `run_label_` first for the OpenAI side to preserve startswith() filters).
- Smoke-diff symmetric WARN (key-set asymmetry in either direction is informational; only wild array-length divergence is a hard fail — original strict check baked in "Sonnet is ground truth" which the validation explicitly doesn't assume).

### Findings (the reason we stopped)

- **Mini per-filing cost: $0.0070** (4,585 prompt + 2,933 completion tokens avg, n=55). Plan estimate implied $0.0022-$0.0033 (i.e. ~$100-150 for full 45,605 corpus). Actual full-corpus 1x mini projection: **$317**.
- Sonnet vs mini *ratio* still favorable (~2.5x cheaper, vs the 5-8x the plan hoped for). $800 Sonnet → $317 mini is real cost reduction, just smaller than the plan's leave-behind framing implied.
- Driver: mini emits **~3x more completion tokens than Sonnet** at the same input. Sonnet's $800 implies ~1K output tokens/filing assuming prompt caching on the brief; mini emits ~2,900. Cause not yet investigated — possibilities in results note (nested-entity full skeletons, verbose extraction_warnings, new schema fields).
- Dispatcher is serial — ~32s per filing → ~2.7 hr per pass at 305 filings. HTTP-bound; a thread pool would cut to ~15-20 min per pass.

### Next steps (deferred, not for this session)

- Parallelize the dispatcher (10-way ThreadPoolExecutor on `run_one_pass`) before resuming.
- Investigate why mini is verbose — look at any one mini output vs the Sonnet baseline for the same report_id; the difference should be visible.
- Decide whether to (a) resume the 3-pass validation at higher actual cost (~$6-7, fine in absolute terms), or (b) trim the schema/brief to reduce verbosity first, or (c) reframe the leave-behind for Suhan around the actual $317 number.

### Decisions Made

- Stop Run 1 mid-pass rather than spend $2 to complete a serial pass on data that's projected to overshoot the budget — partial data is sufficient for the verbosity investigation.
- Don't parallelize in this session; user explicitly asked another agent to take that on.

### Day-2 spend

~$0.72 total: $0.31 Anthropic (5 re-Sonnet runs for legacy-baseline cleanup) + ~$0.41 OpenAI (smoke runs + the 55-filing partial Run 1).

---

## 2026-06-09 — WI vs NY chain parity check; two cross-state-infra tasks captured

**Originating discussion:** session conversation 2026-06-09 (third leave-behind-prep session).

**Convo:** [`convos/20260609_wi_vs_ny_chain_parity.md`](convos/20260609_wi_vs_ny_chain_parity.md)

**Context:** Dan opened the session asking whether WI had reached parity with NY's chain — referencing the 2026-06-08 NY `parties_lobbied` integration on `ny-disclosure-explore`. Session walked through a parity comparison + an IPF-on-dollars false start + cross-state shareable-infrastructure framing, ending with two GH issues captured for successor-Fellow handoff.

### Topics Explored

- WI chain (`releases/wi/chain/`, on main) vs NY chain (`releases/ny/chain/`, on `ny-disclosure-explore`, not yet merged) artifact-level comparison
- Three categories of difference: structural (NY's `parties_lobbied` has no WI analog; WI lobbying disclosure doesn't require disclosing which lawmakers were contacted), modeling-architecture (NY = clean JOIN; WI = IPF because WI lobbyists report only aggregate hours), and a mis-framed "fixable" $-attribution gap
- Dan's IPF-on-dollars idea — falsified because WI lobbyists file Time Reports only (no compensation-received field) → no column marginals; IPF underdetermined without external lobbyist-revenue data
- Hours ∝ spending rule of thumb: structurally untestable across all 10 priority states (each state discloses one of {$, hours} but not both at per-(lobbyist, client, bill) grain)
- CFIS as WI-specific name vs FTM as 50-state aggregator (with API-only access surface, basic-tier quota, Institute review on quota-exceed)
- FTM-in-OpenSecrets-integration sunset mode (banner observation that post-dates the wi-cfis-scoping work — long-term API contract may not survive the merger)
- Architectural axis count: lobbying disclosure (per-state, bespoke), bill sponsorship (shared via Plural Policy), campaign finance (shareable via FTM — not yet built)

### Provisional Findings

- WI chain is structurally complete given WI's disclosure shape. The `comp_per_cell` column I initially proposed would have stacked 4 layers of modeling (IPF + proportional bill attribution + per-sponsor split + per-principal $/hr rescaling) under a number that reads as disclosed — explicitly rejected as surface parity.
- WI vs NY are at parity *relative to their respective data sources*. Differences are data-shape, not pipeline-completeness, and not "gaps" in either direction.
- Cross-state shareable infrastructure confirmed on two of three chain legs: Plural Policy (already in active use on `wi-allocation-matrix` and `ny-disclosure-explore`), FTM (50-state, not yet built). Lobbying disclosure remains per-state Anna Karenina by data-acquisition shape.
- FTM API may not be the long-term contract — site is "not maintained as we integrate with OpenSecrets"; URL/endpoint pattern may change. Worth confirming before #43 implementation starts.

### Results

- GH issue [#42](https://github.com/danparshall/lobby_analysis/issues/42): "Extract Plural Policy bulk-CSV ingest into shared cross-state library"
- GH issue [#43](https://github.com/danparshall/lobby_analysis/issues/43): "Build reusable FollowTheMoney ingest for cross-state campaign-finance leg" (body updated with the OpenSecrets-integration finding)

### Next Steps

- Day 4 (OH chain composer + `releases/oh/`) remains the next leave-behind action item per the 2026-06-08 revised 5-day plan. This session's work is captured-task externalization, not Day 4 execution.
- If Day 5 (RESEARCH_ARC.md update) covers Anna Karenina principle propagation, fold in the cross-state shareable axes (Plural Policy + FTM) finding from this session as a sub-point.

### Decisions Made

- No WI chain `comp_per_cell` work. Rejected as surface-parity dressing.
- Two tasks externalized to GH issues (#42, #43) rather than absorbed into Day 4/5 scope — they're successor-Fellow handoff work, not pre-Thursday work.

---

## 2026-06-08 — STATUS sweep to main + gpt-5-mini cost-floor plan

**Originating discussion:** session conversation 2026-06-08 (second leave-behind-prep session).

**Convo:** [`convos/20260608_status_sweep_and_gpt5mini_plan.md`](convos/20260608_status_sweep_and_gpt5mini_plan.md)

**Context:** Session opened on the question "what's our status on leave-behind-prep" but pivoted twice. First to STATUS propagation (Dan: "make sure main knows about this branch + state branches"), then to OH extraction decision space (Dan working through the "$800 dispatch — yes or no?" question for an eventual Suhan decisions doc).

### Topics Explored

- Session-start credential diagnostic failure (empty `$TOKEN` in fresh bash shell looked like an expired PAT; agent over-confidently escalated; corrected after Dan's screenshot)
- Git CLI vs Contents API as the user-repo interaction surface (CLI wins for branches-mode work)
- CLAUDE.md `Never make changes directly on main` norm vs sole-Fellow exception
- OH extraction cost decomposition: $800 = single-model Sonnet-4-6 already; Batches+caching brings it down from $1,600 floor
- 4-node × 6-edge × 3-attribute framework as the right unit for the OH-extraction decision
- Which OH edges come from AER data (4 of 5 populated edges) vs Plural Policy (`lawmaker↔bill`, free)
- Ask-then-extract vs extract-then-ask framing as orthogonal to model choice
- Classical NLP vs LLM extraction: hybrid possible post-Fellowship, false economy before Thursday
- Vendor swap cost analysis: GPT-5.5 *more* expensive than Sonnet; flagship swaps don't save money
- Tier-drop cost analysis: GPT-5-mini ~6-12× cheaper than Sonnet → ~$80-150 full corpus IF validation passes
- Benchmark-substitution trap: SWE-bench / GPQA scores irrelevant for AER extraction; only relevant signal is prior σ_noise work on `extraction-harness-brainstorm`
- Asymmetric comparator design: mini 3x for σ_noise, Sonnet 1x as reference (saves +$30 / +4hr but limits claimable findings)

### Provisional Findings

- STATUS.md on main was 4 commits behind `leave-behind-prep` pre-session (the Day 1 reconciliation hadn't propagated). Treating main's STATUS as session-start canon for fresh sessions required cherry-picking the Day 1 commits across.
- `mi-disclosure-explore` (stale base 2026-06-02) and `nc-disclosure-explore` (stale base 2026-05-25) exist on origin but appeared in neither STATUS table on either branch — real gap that Day 1's reconciliation missed. Both need rebase or merge-main before resuming.
- No `fl-*` branch exists; FL is in `STATE_COVERAGE.md`'s "Prong 1 statute SMR only" bucket along with 6 other states.
- OH full-corpus extraction at $800 is **already optimized** (single-model Sonnet + Batches + prompt caching). Tier-1's two-model side-by-side was a one-time validation, not the production config.
- Flagship vendor swap doesn't reduce cost: GPT-5.5 at $5/$30 is more expensive than Sonnet at $3/$15; GPT-5.4 input ~15% cheaper but task is output-heavy.
- Tier-drop is the real cost lever: GPT-5-mini at $0.25/$2 = ~12×/7.5× cheaper than Sonnet → ~$80-150 projected for full OH corpus IF mini handles AER extraction adequately. **Currently no evidence either way for AER.**
- For OH, 4 of 5 populated lobbying-chain edges come from AER data; `lawmaker↔bill` is the exception (Plural Policy bulk-CSV, $0).
- The $800 is *not* the cost of `releases/oh/` — extraction is one of three pending items: (a) Sonnet full-corpus run [$800], (b) Plural Policy OH bulk-CSV [$0], (c) chain composer [Day 4 leave-behind work, time only].

### Results

- **5 commits pushed to `origin/main`** (`83ad0fe` → `6cc5bf0`): cherry-picked Day 1 STATE_COVERAGE.md + STATUS reconciliation + Day 1 finish-convo + NY skeleton fill from this branch + one new commit adding mi/nc stub rows. STATUS.md on main now lists all 6 live branches.
- **`docs/STATE_COVERAGE.md` now on main** (was leave-behind-prep-only pre-session).
- **gpt-5-mini 3x validation plan committed** (`5df4f39`) at [`plans/20260608_gpt5mini_on_oh_300slice.md`](plans/20260608_gpt5mini_on_oh_300slice.md). 164 lines, Phase 0-3, hard-stop guardrails, asymmetric-comparator caveat documented.

### Decisions Made

- **STATUS propagation strategy:** cherry-pick all 4 leave-behind-prep commits onto main as-is (not surgical-pick STATUS hunks). Day 5 wrap-up merge will be cleaner; `docs/active/leave-behind-prep/` files landing on main early is acceptable given the leave-behind nature.
- **mi/nc stub-row convention:** "exists, scope TBD" + latest-commit + merge-base metadata. Candidate convention worth standardizing for future stub additions.
- **Direct push to main:** authorized as sole-Fellow exception. CLAUDE.md norm preserved for the multi-committer rationale that no longer applies.
- **gpt-5-mini validation: 3 runs of mini, Sonnet stays at 1x.** Asymmetric comparator with explicit caveat — supports σ_noise + agreement claims, NOT ranked accuracy.
- **5-day plan revised:** Day 2 mini-validation → Day 3 cross-state CPI 5-state dispatch → Day 4 OH chain composer + `releases/oh/` (FOCAL Plans 3+4 cut) → Day 5 RESEARCH_ARC + resumption brief. No slack — Day 5 lands on Thursday.
- **Suhan-facing doc genre:** *decisions doc*, not weekly-update status doc. Per-decision structure with options + recommendation + deadline. Distinct from Day 5 resumption brief. Decisions doc not yet drafted.

### Next Steps

- **Execute gpt-5-mini plan today (Day 2).** Hard-stop at Phase 1 + 3 hours if OpenAI structured-output schema translation blocks. If hard-stop hit, write up the engineering blocker as a result file and recover to Day 3.
- **Day 3 (Tue 2026-06-09):** Cross-state CPI 5-state extension dispatch on `cross-state-cpi-2015-validation` (~$15, CO/IL/WA/FL/NC at vintage 2015).
- **Day 4 (Wed 2026-06-10):** OH chain composer (`src/lobby_analysis/oh/`, JOIN-based per Anna Karenina) + `releases/oh/`. Requires Plural Policy OH bulk-CSV downloaded first (~30 min task, free, parallel-able with anything).
- **Day 5 (Thu 2026-06-11):** RESEARCH_ARC.md update with Anna Karenina + SMR-as-canonical principle propagated; resumption brief; finish-convo on surviving branches.
- **Suhan decisions doc** still pending. Genre clarified this session; decision list itself awaits Dan filter. Likely a Wednesday-or-Thursday task; results from Day 2 mini-validation feed directly into the OH-extraction option framing.

---



**Originating discussion:** session conversation 2026-06-06 (this branch's first session).

**Context:** Fellowship ends ~2026-06-11 (presentation Thursday). Three active fronts confirmed empirically:
1. `cross-state-cpi-2015-validation` — 5 states dispatched + trends-at-N=5 doc landed
2. `ny-disclosure-explore` — `parties_lobbied` MVP shipped; chain composer pending
3. `oh-portal-aprime-batch` — extraction pipeline + 300-slice validation done; chain composer pending

Contribution data: Dan 699 non-merge commits (98%); Amina 13 (1.8%); Gowrav 4 (0.6%).

**Convo:** [`convos/20260606_take_stock_and_day1_hygiene.md`](convos/20260606_take_stock_and_day1_hygiene.md)

### Topics Explored

- Pre-flight project stocktake (STATUS Active table reconciliation; 3 active fronts identified vs 4 stale rows)
- 5-day plan shaping (Fellowship-ends-project-continues scope; substantive-push-with-day-1-hygiene framing)
- Cross-state CPI 2015 N=5 trends doc — Trends 1/2/6 unpacked and then reframed per SMR-as-canonical principle
- NY scope — "full chain like WI" with "+ spending"
- OH portal data structure (OLAC discovery; AER detail page; Section I bills; Section II.A-D itemized gifts/meals)
- Plural Policy / OpenStates as the bill→sponsor leg (free bulk-CSV, all 50 states)
- Anna Karenina principle as architectural correction
- Commit-author contribution data (Dan 699 / Amina 13 / Gowrav 4 — 98% Dan)
- 4-node × 6-edge × 3-attribute (money/time/stance) coverage framework
- OH AER header-level compensation field (via subagent — structurally missing)

### Provisional Findings

- Cross-state CPI trends split: Trends 1+6+2 reframed as projection/engineering work (NOT v2.2 schema design); Trends 3/4/5 are prior-art-disagreement noise. Path 2-modified (5 more states at vintage 2015) is the bounded next step.
- OH structurally lacks principal↔lobbyist money disclosure — same shape as WI on this edge. `LobbyingFiling.total_compensation` exists but is null on all OH extractions.
- OH AER has richer lobbyist↔lawmaker transactional layer than WI (Section II.A gifts + II.B meals natively itemize lawmaker recipient + $).
- Plural Policy bulk-CSV covers all 50 states including OH; OH not yet downloaded.
- Anna Karenina: per-state pipelines are bespoke; "stairs of leverage" in RESEARCH_ARC overstates per-state amortization.

### Results

- [`docs/STATE_COVERAGE.md`](../../STATE_COVERAGE.md) — per-state edge×attribute coverage matrix (committed `92b4ff8`; OH cell corrected `546663e`). Lives at repo-root per convention.
- STATUS.md Active+Archived reconciliation (commit `546663e`): 4 stale rows Archived; 4 fresh rows Active.

### Decisions Made

- 5-day plan provisionally locked: Day 1 hygiene → Days 2-3 cross-state CPI N=10 extension (~$15) → Day 4 OH chain composer + FOCAL Plans 3+4 → Day 5 RESEARCH_ARC update + resumption brief.
- B reframed: NOT v2.2 schema design pass; resumption brief + projection-translation convention codification.
- No state-agnostic refactor; per-state modules under `src/lobby_analysis/<state>/`.
- Honest register in resumption brief; diplomatic framing preserved for Thursday presentation + repo-root institutional courtesy.

### Next Steps

- Dan reviews this session's commits (`92b4ff8`, `546663e`).
- Next session: (a) finish Day 1 worktree pruning audit, or (b) jump to Day 2 cross-state CPI 5-state extension dispatch (~$15 — needs cost authorization).
- Day 5 to propagate Anna Karenina + SMR-as-canonical to `docs/RESEARCH_ARC.md`.

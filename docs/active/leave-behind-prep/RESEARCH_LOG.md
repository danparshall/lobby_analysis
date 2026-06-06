# RESEARCH_LOG — leave-behind-prep

Newest entries first.

This branch hosts the 5-day pre-wrap cleanup + leave-behind work. Scope:
- Day 1: STATUS reconciliation; triage stale Active rows; STATE_COVERAGE.md drafted; worktree pruning
- Day 2-3: cross-state CPI 5-state extension dispatched in parallel (on `cross-state-cpi-2015-validation` branch, not this one)
- Day 4: OH chain composer + `releases/oh/`; FOCAL Plans 3+4 (likely on dedicated branches)
- Day 5: RESEARCH_ARC.md update; resumption brief; finish-convo on surviving branches

---

## 2026-06-06 — Branch cut for pre-wrap hygiene + leave-behind work

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

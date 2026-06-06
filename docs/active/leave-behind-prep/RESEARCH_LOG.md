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

**Day 1 deliverables landed:**
- `docs/STATE_COVERAGE.md` — per-state edge×attribute coverage matrix with quality + source per cell, framed around 4 nodes (principal/lobbyist/lawmaker/bill) × 6 edges × 3 attributes (money/time/stance). NY left as skeleton with validation checklist; CA/TX/CO/IL/WA/FL/NC documented as "Prong 1 only."

**Architectural finding captured:** Per-state pipelines are bespoke (Anna Karenina principle). Shared infrastructure lives downstream of extraction. No state-agnostic chain composer; per-state modules under `src/lobby_analysis/<state>/`. Recorded in STATE_COVERAGE.md's Anna Karenina note and to be propagated to RESEARCH_ARC.md on Day 5.

**Convo:** TBD (this session not yet finish-convo'd; pending session continuation)

**Next:** STATUS.md reconciliation — surface NY + cross-state-CPI as Active; triage 4 stale rows (`compendium-v2-promote`, `oh-portal-extraction`, `filing-schema-extraction`, `wi-tier1-direct-read`); worktree pruning audit.

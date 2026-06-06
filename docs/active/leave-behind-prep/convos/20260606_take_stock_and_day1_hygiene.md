# Take stock + Day 1 hygiene

**Date:** 2026-06-06
**Branch:** leave-behind-prep

## Summary

Session opened with Dan asking to discuss overall project status with ~5 days to Fellowship wrap. Quickly surfaced that the STATUS Active table was substantially stale: 4 of 4 listed branches not actively producing findings, while the actual live frontier (`cross-state-cpi-2015-validation`, with trends-doc landed today) wasn't in the table. Dan also surfaced two more live fronts I hadn't appreciated — `ny-disclosure-explore` (parties_lobbied disclosed-lawmaker edge MVP shipped hours before session start) and the OH portal work, which Dan had taken over from Amina under `oh-portal-aprime-batch` after her handoff stalled. Took stock of all three fronts, then committed Day 1 hygiene: drafted `docs/STATE_COVERAGE.md` per Dan's 4-node × 6-edge × 3-attribute (money/time/stance) framework, then reconciled STATUS.md Active+Archived tables.

Two substantive reframings landed during the session — both from Dan, both load-bearing. First, the v2.2 schema design framing for cross-state failure-mode trends (Trends 1/2/6) was wrong: the SMR is the canonical statute-literal record; projection functions translate per-rubric; the cell-type-vs-rubric-tier mismatch is *projection-translation engineering*, not schema design. Matching prior art is a CHECK, not the goal. Second, "each state has its own pipeline — this is an Anna Karenina problem" — premature generalization toward a state-agnostic chain composer is fighting structural diversity; per-state modules under `src/lobby_analysis/<state>/` are the right shape, forever. The "shared infrastructure" lives downstream of extraction (canonical filing schema, typed-cell schema, projection functions, release format), not upstream.

A 5-day plan was provisionally locked: Day 1 hygiene + STATE_COVERAGE.md → Days 2-3 cross-state CPI 5-state extension (CO/IL/WA/FL/NC at vintage 2015, ~$15) → Day 4 OH chain composer + FOCAL Plans 3+4 → Day 5 RESEARCH_ARC.md update with Anna Karenina principle propagated + resumption brief (the new shape of B, after the reframing). NY chain ("full chain like WI" — principal → lobbyist → lawmaker → bill + spending) accepted as plausible in 5 days at Dan's actual commit cadence, after I was wrong to call WI's chain "weeks of dedicated work" — Dan's WI chain commits show 3 working days from kickoff to ship-and-archive.

## Topics Explored

- Pre-flight project stocktake (STATUS Active table reconciliation; 3 active fronts identified vs 4 stale rows)
- 5-day plan shaping (Fellowship-ends-project-continues scope; substantive-push-with-day-1-hygiene framing)
- Trends 1/2/6 from cross-state CPI 2015 N=5 trends doc — unpacked and then reframed per SMR-as-canonical principle
- NY scope — "full chain like WI" with "+ spending"
- OH portal data structure (OLAC discovery 3-step chain; AER detail page; Section I bills; Section II.A-D itemized gifts/meals)
- Plural Policy / OpenStates as the bill→sponsor leg for both OH and NY (free bulk-CSV, all 50 states)
- Anna Karenina principle as architectural correction (premature generalization risk; state-bespoke pipelines)
- Commit-author contribution data (Dan 699 / Amina 13 / Gowrav 4 — 98% Dan)
- Diplomatic vs honest register split (presentation framing vs resumption brief framing)
- 4-node × 6-edge × 3-attribute (money/time/stance) coverage framework
- OH AER header-level compensation field check (via subagent — structurally missing)

## Provisional Findings

- **Cross-state CPI 2015 N=5 trends are split into projection/engineering work (Trends 1+6+2) and prior-art-disagreement noise (Trends 3/4/5).** Path 2-modified (5 more states at vintage 2015) is the bounded next step; Path 1 vocab fix is a cheap bolt-on. v2.2 design pass should NOT be committed at N=5.
- **OH structurally lacks the principal↔lobbyist money edge.** AER form doesn't disclose compensation paid by employer to agent; `LobbyingFiling.total_compensation` exists but is null on all OH extractions. Same structural shape as WI.
- **OH AER has a richer lobbyist↔lawmaker transactional layer than WI** — Section II.A (gifts) and II.B (itemized meals) name recipient + $ per row. WI's structurally-missing $-flow leg (scoped on `wi-cfis-scoping`) is partially present in OH natively.
- **OH 300-slice validation closed clean** (300/300 effective extraction rate; 0 schema failures; ~$10 spend). Full corpus extraction (45,605 AERs) projected at ~$800 / ~24 hr via Batches API + caching + retry — pending dev work.
- **NY is structurally analogous to WI on chain shape** but with a richer parties_lobbied disclosed-lawmaker layer that may obviate WI's IPF requirement (JOIN-only composition, like OH).
- **Plural Policy bulk-CSV covers all 50 states**, including OH — same path as WI; OH not yet downloaded but the schema is universal.
- **Anna Karenina:** each state's pipeline is bespoke; the "stairs of leverage" in RESEARCH_ARC.md overstates per-state amortization; per-state engineering is ~3 working days at TDD discipline regardless of how many states preceded it.

## Decisions Made

- **5-day plan (provisional):**
  - Day 1: Hygiene (STATUS reconciliation + STATE_COVERAGE.md + worktree pruning) — partially landed this session
  - Days 2-3: Cross-state CPI 5-state extension dispatched on `cross-state-cpi-2015-validation` (~$15)
  - Day 4: OH chain composer (per-state module `src/lobby_analysis/oh/`, JOIN-based, no IPF) + FOCAL Plans 3+4 ($0, clean Phase C closure)
  - Day 5: RESEARCH_ARC.md update propagating Anna Karenina + SMR-as-canonical principle; resumption brief; finish-convo on surviving branches
- **B reframed:** NOT a v2.2 schema design pass. Resumption brief + ONE concrete proposal codifying the projection-translation convention from Trends 1+6 as architectural pattern.
- **No state-agnostic refactor:** per-state modules under `src/lobby_analysis/<state>/`. WI legislature loader is OH's template, not its parent class.
- **NY chain target:** principal → lobbyist → lawmaker → bill + spending (where spending leg comes from client semiannuals natively if present, NOT requiring CFIS-style external source).
- **Honest register in resumption brief:** Fellowship-collaborative framing kept for Thursday presentation + repo-root README institutional courtesy; resumption brief is honest about Dan being 98% of commits.

## Results

- `docs/STATE_COVERAGE.md` — per-state edge×attribute coverage matrix (committed `92b4ff8`; OH cell corrected `546663e`). Lives at repo-root per convention (alongside `RESEARCH_ARC.md`, `LANDSCAPE.md`). See file for WI/OH detailed matrices, NY skeleton with validation checklist, CA/TX/CO/IL/WA/FL/NC as "Prong 1 only," summary scorecard, and Anna Karenina note.
- STATUS.md Active+Archived reconciliation (commit `546663e`): 4 stale Active rows moved to Archived (`wi-tier1-direct-read`, `compendium-v2-promote`, `oh-portal-extraction`, `filing-schema-extraction`); 4 fresh Active rows added (`cross-state-cpi-2015-validation`, `ny-disclosure-explore`, `oh-portal-aprime-batch`, `leave-behind-prep`).
- Contribution data (output of Explore subagent; not saved to results/): Dan 699 non-merge commits (98%); Amina 13 (1.8%); Gowrav 4 (0.6%, single day). Cited in this convo + STATE_COVERAGE.md's structural framing.
- OH AER header compensation verification (output of second Explore subagent; not saved to results/): `total_compensation` field exists on `LobbyingFiling` schema (intended as PRI E1f federal concept) but null on all OH extractions; OH AER form structurally lacks compensation disclosure. Cited in STATE_COVERAGE.md OH section footnote ¹.

## Open Questions

- **NY validation checklist** (to be resolved on next `ny-disclosure-explore` session): does client semiannual include compensation $ per (principal, lobbyist) pair? Does parties_lobbied carry bill/subject context? Does NY disclose stance? Time dimension on parties_lobbied? Principal↔lawmaker direct payment scope?
- **`ny-disclosure-explore` allocation/wi/ coupling check** — does NY code import from `allocation/wi/` (the WI legislature loader)? If yes, undo while cheap. Dan to check on his next NY session.
- **OH full-corpus run pre-Thursday?** Optional ~$800 / ~24 hr async run via Batches API; alternative is "300-slice + projection to full corpus" as Thursday-presentable.
- **Worktree pruning audit** — 14 worktrees, many for archived branches; Day 1 remainder.
- **Substantive-push pace** — if Dan's energy holds, push NY/OH chain + FOCAL more aggressively than the conservative 5-day plan; hygiene pieces are mostly done after this session.

## Next Steps

- Dan reviews this session's commits (`92b4ff8`, `546663e`) — particularly the 4 fresh STATUS Active rows, the 4 archived rows (especially `oh-portal-extraction` Amina-stall framing and `wi-tier1-direct-read` "dormant" call), and STATE_COVERAGE.md accuracy on WI/OH cells.
- Next session: either (a) finish Day 1 worktree pruning, or (b) jump to Day 2 cross-state CPI 5-state extension dispatch on `cross-state-cpi-2015-validation` (~$15, requires explicit cost authorization).
- Day 5 will need to propagate Anna Karenina principle + SMR-as-canonical principle to `docs/RESEARCH_ARC.md` (existing doc, needs update not rewrite).

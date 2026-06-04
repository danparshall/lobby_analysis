# RESEARCH_LOG — wi-campaign-finance

Branch: `wi-campaign-finance` — cut 2026-06-04 off post-merge main `28f3e47` (merge of wi-cfis-scoping PR #34).

Origin: Phase 4 of the archived `wi-allocation-matrix` plan (`docs/historical/wi-allocation-matrix/plans/wi_allocation_matrix.md` §178-187) flagged the WI Ethics Commission's CFIS as the structurally missing **$-flow leg** of the published chain TSV (`releases/wi/chain/WI_chain_2025.tsv`). The `wi-cfis-scoping` branch (archived 2026-06-04 to `docs/historical/wi-cfis-scoping/`) characterized the access surface, ran an FTM API sample query end-to-end, decoded the 15-field transactional schema, cross-validated FTM coverage against the chain's SB 28 / electric-utility coalition, and produced the handoff plan at [`plans/wi_campaign_finance.md`](plans/wi_campaign_finance.md). The canonical scoping evidence lives at `docs/historical/wi-cfis-scoping/` (Phase 4 scoping doc + FTM sample-query writeup).

**Scope of this branch:** execute the three-phase handoff plan — Phase 0 calendar wait for FTM Institute expanded-access review → Phase 1 FTM ingest + lawmaker/principal/lobbyist crosswalks + materialize `releases/wi/campaign_finance/` TSVs → conditional Phase 2 Selenium-Sunshine gap-fill.

**Phase 0 trigger:** basic-tier API quota exhausted during scoping on 2026-06-03; Institute's quota-exceed response promised review within ~2 business days. Dan emailed `info@opensecrets.org` proactively 2026-06-03 to accelerate. Phase 0 is **calendar wait until the review email arrives**; zero code.

## Sessions

Newest first.

| Date | Convo | Status |
|---|---|---|
| 2026-06-04 | [`convos/20260604_wi_campaign_finance_branch_setup.md`](convos/20260604_wi_campaign_finance_branch_setup.md) | Branch + worktree setup; Phase 0 calendar wait initiated |

## Results

(None yet — Phase 0 produces no code or analysis; Phase 1 starts after the FTM Institute review email lands.)

## Plans

| Date | Plan | Originating convo | Phase |
|---|---|---|---|
| 2026-06-03 (copied 2026-06-04) | [`plans/wi_campaign_finance.md`](plans/wi_campaign_finance.md) — three-phase handoff plan copied from `docs/historical/wi-cfis-scoping/plans/wi_campaign_finance.md` with relative-path adjustments. Originating convo: [`../../historical/wi-cfis-scoping/convos/20260603_wi_cfis_access_surface_scoping.md`](../../historical/wi-cfis-scoping/convos/20260603_wi_cfis_access_surface_scoping.md) | [2026-06-03 scoping](../../historical/wi-cfis-scoping/convos/20260603_wi_cfis_access_surface_scoping.md) | All 3 phases of the plan; currently Phase 0 |

---

## Session: 2026-06-04 — wi_campaign_finance_branch_setup

### Topics Explored

- wi-cfis-scoping branch-finalization + merge to main (via `finishing-a-research-branch`; PR #34 merged at `28f3e47`) — prerequisite per the plan's "cut off post-merge main after wi-cfis-scoping lands" directive.
- Cutting the `wi-campaign-finance` worktree off updated main; symlinking `data/` (to `~/data/lobby_analysis/`) and `.env.local` (to main's file) per the data-discipline rules in `~/.claude/CLAUDE.md`.
- Seeding `docs/active/wi-campaign-finance/` with `RESEARCH_LOG.md`, `convos/`, `plans/`, `results/`; copying the handoff plan into `plans/` with relative-path adjustments for the new historical/ location.

### Provisional Findings

- Plan + scoping evidence are now reachable on this branch via `docs/historical/wi-cfis-scoping/` (canonical) and `docs/active/wi-campaign-finance/plans/wi_campaign_finance.md` (working copy with adjusted links).
- Phase 0 is open-ended calendar wait; no code, no API queries until expanded access is confirmed.

### Decisions Made

- Phase 0 = wait for FTM Institute expanded-access review email. Dan's proactive 2026-06-03 email to `info@opensecrets.org` may shorten the wait; otherwise default SLA is ~2 business days from the original quota-exhaustion event (so contact expected by 2026-06-05 EOB).
- Phase 1 begins only after a small probe query against the WI 2024 candidate list confirms expanded access is live.

### Next Steps

- Watch the account inbox for the Institute's review message.
- When it arrives, reply with the Corda Democracy Fellowship / open-source / non-commercial / 5-8 priority states / CC BY-NC-SA 3.0 US attribution framing per the sample-query writeup §6 (`docs/historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md`).
- If no contact by EOD 2026-06-06 (proactive email day 3) or 2026-06-09 (original quota-exhaust day 4-5), send a follow-up status-check email per §6 of the same writeup.
- Once confirmed, execute Phase 1 starting at §1.1 (`uv add httpx pydantic`) → §1.2 FTM client TDD.

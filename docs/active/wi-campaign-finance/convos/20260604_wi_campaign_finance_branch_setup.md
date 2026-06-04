# 20260604_wi_campaign_finance_branch_setup

**Date:** 2026-06-04
**Branch:** wi-campaign-finance

## Summary

Procedural setup session for the successor to `wi-cfis-scoping`. The opening handoff was: *"Cut a wi-campaign-finance worktree off post-merge main, then execute docs/active/wi-cfis-scoping/plans/wi_campaign_finance.md starting at Phase 0 (calendar wait for FTM Institute's expanded-access review — Dan emailed info@opensecrets.org proactively on 2026-06-03 to accelerate). The plan + the two results docs in docs/active/wi-cfis-scoping/ carry the full upstream context."*

Pre-flight confirmed `wi-cfis-scoping` was unmerged (the plan's own §17 directive requires "cut off post-merge main after wi-cfis-scoping lands"). After Dan's confirmation, ran `finishing-a-research-branch` to archive + merge wi-cfis-scoping (PR #34, merge `28f3e47`), then cut the `wi-campaign-finance` worktree off updated main, symlinked `data/` and `.env.local`, and seeded the branch docs with the handoff plan + this convo.

Zero substantive code or analysis this session — by design. Phase 0 is calendar wait for FTM Institute expanded-access review; nothing runs against the API until expanded access is confirmed.

## Topics Explored

- **Branch ordering decision:** the plan was authored on `wi-cfis-scoping`, but the path the handoff referenced (`docs/active/wi-cfis-scoping/plans/wi_campaign_finance.md`) only existed there — main was at `e84d2a1` and didn't yet have the docs. Asked Dan to confirm the path; he chose the `finishing-a-research-branch` route to land the plan + scoping evidence on main before cutting the successor worktree.
- **wi-cfis-scoping merge:** ran `finishing-a-research-branch` end-to-end — finish-convo wrap (created `20260604_branch_finalization.md` on that branch), audit-docs (clean), `git mv docs/active/wi-cfis-scoping → docs/historical/wi-cfis-scoping`, STATUS row moved Active → Archived, PR #34 opened with full scoping summary, merged with `gh pr merge --merge` at Dan's confirm. Main fast-forwarded `e84d2a1 → 28f3e47`.
- **Worktree cut:** `git worktree add .worktrees/wi-campaign-finance -b wi-campaign-finance main` against updated main; symlinks added for `data → ~/data/lobby_analysis` and `.env.local → main's .env.local` per the data-discipline rules in `~/.claude/CLAUDE.md`.
- **Plan copy + path adjustment:** copied the handoff plan from `docs/historical/wi-cfis-scoping/plans/` into `docs/active/wi-campaign-finance/plans/`; updated relative paths so links from the new location point at the canonical scoping evidence in `docs/historical/wi-cfis-scoping/`.
- **Test-suite baseline (pre-merge of wi-cfis-scoping, on that branch):** 3 failed / 1636 passed / 3 skipped / 3 xfailed — identical to wi-allocation-matrix merge baseline; no regressions.

## Provisional Findings

- The branch is set up to execute Phase 0 (wait) and then Phase 1 (FTM ingest + 3 crosswalks + materialize `releases/wi/campaign_finance/`).
- The scoping evidence + sample-query findings are reachable via `docs/historical/wi-cfis-scoping/` from any agent on this branch.
- Phase 0's success criterion is administrative, not technical — green-light email from the FTM Institute.

## Decisions Made

- **Order of operations confirmed by Dan:** merge wi-cfis-scoping → main first, then cut wi-campaign-finance off updated main. Plan copy carries the originating-convo and originating-result links pointed at `docs/historical/wi-cfis-scoping/`.
- **Plan working location:** `docs/active/wi-campaign-finance/plans/wi_campaign_finance.md` (this branch's working copy with adjusted relative paths). Canonical original preserved at `docs/historical/wi-cfis-scoping/plans/wi_campaign_finance.md`.
- **Phase 0 entry posture:** zero API queries against the throttled basic-tier account until expanded access is confirmed. Dan's proactive email to `info@opensecrets.org` on 2026-06-03 may shorten the wait.

## Results

(None — Phase 0 produces no code or analysis.)

## Open Questions

- **Q1 (Phase 0 deadline):** what does the actual review timeline turn out to be? Default SLA is 2 business days from quota-exhaustion event (2026-06-03), so contact expected by 2026-06-05 EOB. Dan's proactive email may shift this earlier.
- **Q2 (expanded-access scope):** what does the Institute's grant look like operationally — unlimited, daily cap, monthly cap? Confirm at Phase 0 end before sizing Phase 1 batches (plan §216).
- **Q3 (OpenStates `Person.identifiers[]`):** does it already contain FTM eids for WI legislators? Worth a 5-minute probe before committing to manual lawmaker crosswalk (plan §225, §1.4).

## Next Steps

- Watch the FTM account inbox for the Institute's review email.
- Send the prepared reply (Corda Democracy Fellowship / open-source / non-commercial / 5-8 priority states / CC BY-NC-SA 3.0 US attribution) when it arrives.
- If no contact by EOD 2026-06-06 (3 business days post Dan's proactive email) or 2026-06-09 (4-5 business days post original quota event), send the follow-up status-check email per `docs/historical/wi-cfis-scoping/results/20260603_ftm_sample_query_lemahieu.md` §6.
- Once expanded access is confirmed, run a probe query against the WI 2024 candidate list, then proceed to plan §1.1 (`uv add httpx pydantic`) → §1.2 (FTM client TDD).

# 2026-05-26 — NC + FL URL discovery (2015 retry + 2015/2025 fresh)

**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Handoff:** [`plans/_handoffs/20260526_nc_fl_url_discovery.md`](../plans/_handoffs/20260526_nc_fl_url_discovery.md)
**Dispatch template:** [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](../plans/_handoffs/20260519_subagent_dispatch_prompt.md)
**Machine:** Dans-MacBook-Air
**Picked up from:** `94dc75d` (main, post `20260524` Prong-1 pause weekly update) — worktree was at `291fb7d` (2026-05-19 post-finish-convo with GH issue back-links)

## Topics Explored

_(filled in at finish-convo)_

## Provisional Findings

_(filled in at finish-convo)_

## Decisions Made

- Convo name approved: `20260526_nc_fl_url_discovery` (NC 2015 retry is part of NC scope, no separate billing).
- Existing partial NC 2015 bundle preserved by renaming `subagent_canaries/NC_2015/` → `subagent_canaries/NC_2015_20260519_pass3_cf_blocked/` (mv-over-rm rule for research artifacts).
- Wave plan: 3 parallel subagents (NC 2015 retry, NC 2025, FL 2015), commit, then 1 solo subagent (FL 2025). CF-safe concurrency ceiling = 3 per the 2026-05-19 batch finding.
- Per-state addenda authored in the handoff to compensate for the generic dispatch prompt's deep-tree under-specification (per the 2026-05-19 CO/IL Article-level lesson). NC: enumerate 8 articles, recurse pass-3 per article. FL: pick BOTH Title III + Title X, recurse pass-3 on Ch.112's Part-level sub-TOC.

## Results

_(filled in at finish-convo — link to `results/20260526_nc_fl_url_discovery_inventory.md`)_

## Next Steps

_(filled in at finish-convo)_

## What could have gone better

_(filled in at finish-convo)_

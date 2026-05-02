# 2026-05-01 (eve) — Issue #6: post-laptop-crash data restoration

**Date:** 2026-05-01 (rolled into 2026-05-02)
**Branch:** statute-extraction
**Issue:** [#6](https://github.com/danparshall/lobby_analysis/issues/6) — Rerun Justia statute pull + portal snapshots after laptop data loss

## Summary

Restored the runtime data wiped in the pre-2026-04-30 laptop drive crash: 3 missing Justia statute bundles (NY/WI/WY) re-fetched via the existing orchestrator, and the entire `data/portal_snapshots/` corpus (50 states × ~981 artifacts in the original) replaced by a much smaller priority-state set (8 states) using a new deterministic Stage 2 Python script. The 3 failing `tests/test_pipeline.py` tests are now green; full suite 337/337.

The architectural change of note: the original Stage 2 was 50 parallel subagents driving `curl`, which produced a permissions storm on the user's end (every fetch needed approval). Replaced with a single Python script (`src/scoring/portal_snapshot.py`) that runs as one approved process. Stage 1 (URL discovery) remains subagent work — but only when needed (the Stage 1 JSONs are now committed at `compendium/portal_urls/<ABBR>.json`, the un-gitignored locked-contract location, so the next laptop crash can't take them out).

A framing correction landed mid-session: my initial proposal claimed "Justia is the SSOT for statutes" — pushback from the user was that Justia is just our **operational** SSOT (stable per-vintage URLs, programmatic), not the canonical authority (each state's own legislative codification — analog to the Federal Register / U.S. Code). Updated `lobbying_statute_urls.py` docstring and added a body-skip in Stage 2 for `statute`-role URLs (record metadata, don't redownload — Justia handles content).

## Topics Explored

- Inventory of what survived the crash (statutes/CA/2010, TX/2009, OH/2010, OH/2025; all `data/portal_snapshots/`, `data/portal_urls/`, NY/WI/WY statutes lost).
- The 3 failing pipeline tests (all need `data/portal_snapshots/CA/2026-04-13/manifest.json` — fixable by capturing fresh + bumping `SNAPSHOT_DATE_DEFAULT`).
- Permission-pattern fixes (`unset VIRTUAL_ENV` no longer needed; uv now warns + ignores mismatched VIRTUAL_ENV from worktree shells).
- Stage 1 vs Stage 2 design — keeping discovery as one-shot subagent work, scripting capture.
- API key check (option (b) Anthropic-SDK Stage 1 ruled out — key was deleted in the crash).
- Stub detection threshold (`<2KB HTML` + WAF marker tokens).
- Body-size cap on artifacts (100 MB streaming cap — CA's CalAccess `dbwebexport.zip` is 650 MB).
- Per-state Stage 1 priming risk (training-data state-government facts; mitigated by subagent's WebFetch verification — WA agent caught and corrected a wrong RCW citation).

## Provisional Findings

- 8 of 50 states cover the README's "5–8 priority" scope (CA + CO/NY/WA/TX/WI/IL/FL). 18-day Stage 1 re-discovery surfaced real portal drift on 5 of the 8 — see `results/20260501_state_portal_drift.md`.
- IL's WAF posture (every `ilsos.gov` host blocks WebFetch) appears unchanged from the historical pass. Stage 2 reproduces the partial-capture state without Playwright; that's a known structural gap.
- FL is genuinely bifurcated (legislative + executive disclosure regimes); Stage 1 captured both, ~5 seeds per regime + 5 cross-regime.
- The Stage 2 script's "skip statute body" rule is a small win (~50–150 KB per state saved) but the framing fix in `lobbying_statute_urls.py` is the bigger value — prevents future agents from making the same SSOT-confusion mistake I made.

## Decisions Made

| topic | decision |
|---|---|
| Stage 1 location | `compendium/portal_urls/<ABBR>.json` at repo root (un-gitignored, alongside the locked compendium CSVs) — not `data/portal_urls/` (gitignored, what the original used) |
| Stage 2 implementation | deterministic Python script (`src/scoring/portal_snapshot.py`) + `cmd_capture_snapshots` orchestrator subcommand; not subagents |
| Stage 1 dispatch | one foreground subagent at a time (sequential); 50-parallel pattern from the original is what produced the permissions storm |
| Body cap | 100 MB streaming cap per artifact; matches historical pragmatic behavior |
| `statute`-role | record URL + Stage 1 verified status as portal-accessibility metadata; skip body fetch — Justia is our operational SSOT |
| `SNAPSHOT_DATE_DEFAULT` | bumped 2026-04-13 → 2026-05-01 |
| Scope cap | 8 priority states this session; remaining 42 deferred to future session (script + orchestrator handle scale-out without architectural work) |
| Worktree gotcha note | marked verified-resolved (uv now warns+ignores mismatched VIRTUAL_ENV); kept the section for paper trail if it recurs |

## Results

- [`results/20260501_state_portal_drift.md`](../results/20260501_state_portal_drift.md) — per-state URL migrations and regulator changes discovered during Stage 1 re-discovery, vs the 2026-04-13 baseline.

## Open Questions

- Should the remaining 42 states get the same Stage 1 + Stage 2 treatment, or only on-demand (when a downstream task needs that state)?
- WI's SSRS canned-report endpoints, FL's SPA-shell stubs, IL's WAF-blocked apps — should we add Playwright capture as a Stage 3 pass for these specific cases, or accept the structural gap?
- The 100 MB body cap means CA's CalAccess `dbwebexport.zip` is truncated. Is the truncated artifact useful for anything, or should we either (a) cap lower (saving disk) or (b) make it state-specific and stream the full ZIP for CA?
- The dl_data.cfm files on FL's portal show timestamps frozen at 12/31/2014 despite "daily-refreshed" advertising — needs a HEAD-check follow-up (flagged in FL.json observations).

## Code/Commits

- `6673d99` — portal-snapshot Stage 2 script + CA capture (initial CA Stage 1 + manifest, `SNAPSHOT_DATE_DEFAULT` bump, worktree gotcha doc fix, 8 unit tests).
- `d9be039` — Stage 1 JSONs for 7 priority states (CO/NY/WA/TX/WI/IL/FL) + statute-role body skip + framing docstring on `lobbying_statute_urls.py`.

## Captured Tasks

GH issue #6 status: infrastructure restored; 8 of 50 states captured. Remaining 42 are "more of the same" — script and dispatch loop work, no architectural blockers.

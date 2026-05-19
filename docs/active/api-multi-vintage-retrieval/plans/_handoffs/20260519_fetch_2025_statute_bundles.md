# Handoff: populate `data/statutes/<STATE>/2025/` for priority states

**Date opened:** 2026-05-19 ~13:00 UTC
**Opened from:** Dans-MacBook-Pro, mid-2015 section-fetch on `.worktrees/api-vintage` (handoff `20260518_fetch_2015_section_bodies.md`)
**Branch:** `api-multi-vintage-retrieval`
**Target machine:** Dans-MacBook-Air (the user is moving the 2025 work to laptop while 2015 finishes on the desktop)
**Companion doc:** `20260518_fetch_2015_section_bodies.md` (same branch, in this directory) — **read it first**; this handoff defers procedural detail to that doc and only highlights 2025-specific deltas.

---

## Why this handoff exists

The 2015 section-fetch handoff (parallel doc in this directory) is mid-execution on Dans-MacBook-Pro. The user wants the 2025 vintage built out on a different machine, in parallel, so the multi-vintage substrate covers both ends of the time range we care about for Compendium 2.0 multi-rubric calibration.

For 2025, **only `data/statutes/OH/2025/` exists today** (30 files, ~184 KB, from the archived `statute-retrieval` branch — the canonical 30-URL ground-truth-shaped bundle the user is currently testing compendium population against). Every other priority state's 2025 directory is empty.

---

## TL;DR

1. **URL discovery has NOT been done for 2025 yet** for any state except OH. The 2015 substrate is the result of a two-day subagent-dispatch run that produced canary bundles under `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2015/`. **There is no `<STATE>_2025` bundle for any state but OH** — you have to run URL discovery first, then fetch sections.
2. The URL-discovery workflow is the **same** as 2015 (subagent dispatch, three-pass prompt, `subagent_fetch_save.py` for HTML+TSV capture). The Anthropic workspace credit is still spent — **direct-API discovery is not available** — so the subagent path is the only path.
3. The section-fetch step is identical to 2015 — `retrieve_statute_bundle()` from `src/scoring/statute_retrieval.py`, parameterized by state, vintage, URL list.
4. **Vintage substitution is more likely at 2025 than 2015.** Justia hosts state codes at varying recencies; some states' most recent vintage may be 2023 or 2024. Use the same `actual_vintage_used` substitution pattern the 2015 run used for CO (intended 2015 → actual 2016). Record the substitution in the canary `result.json`.
5. **Cloudflare risk is still live.** The 2015 run hit CF blocks during URL discovery in the afternoon of 2026-05-18 (GA, NC pass-3; VA, AZ pass-1). Today's 2026-05-19 section-fetch probe came up clean from Dans-MacBook-Pro after the user's IP changes, but CF state can re-engage at any time. Sequential state-by-state, sanity-check every bundle.

---

## What needs to happen (in order)

### Phase A — pick the state list

Default recommendation: **mirror the 13 states that succeeded at 2015 section-fetch** (TX, MA, PA, CO, IL, AR, WI, WA, AK, MI, WV, OH, CA), because:

- Their URL structures and slug shapes are known from the 2015 canary work.
- OH already has 2025 on disk — keeping OH in the list gives an idempotent skip (the existing `if dest.exists(): skip` guard handles it).
- The 17-state 2015 superset includes 4 CF-blocked states (GA, NC, AZ, VA) and 3 lossy states (WY, FL, NY) — don't try those here; they're URL-discovery problems, not 2025-specific problems.

**Confirm the list with Dan before starting Phase B** — he may want a tighter scope (the 5–8 priority states per the README) or to swap in different states for political/data-quality reasons.

### Phase B — URL discovery via subagent dispatch

For each state in the list (skip OH), produce a canary bundle at `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2025/`.

The bundle format is fixed — see `results/subagent_canaries/README.md` for the schema. Each bundle contains:
- `pass1_state_index.html` + `.tsv`
- `pass1_chosen.json`
- One `pass2_<title-slug>.{html,tsv,chosen.json}` triple per chosen title
- One `pass3_<chapter-slug>.{html,tsv,chosen.json}` triple per chosen chapter (when pass-3 fires)
- `result.json` aggregating `proposed_urls[]`, `actual_vintage_used`, `tree_depth`, `playwright_errors`, `prompt_git_rev`

**Workflow per state**, exactly as 2015:

1. Dispatch a Claude Code subagent (`Agent` tool) with the pass-1 prompt at `src/scoring/api_seed_discovery_pass1_prompt.md`. The subagent fetches `https://law.justia.com/codes/<state-slug>/2025/` via Playwright (uses `scripts/subagent_fetch_save.py` to write HTML+TSV to the bundle dir), then applies pass-1 LLM reasoning to choose titles.
2. For each chosen title, the subagent fetches the title-level index, applies pass-2 reasoning (using `src/scoring/api_seed_discovery_pass2_prompt.md`) to choose chapters.
3. For each chosen chapter where the chapter-level page doesn't itself contain statute text (i.e., tree depth ≥ 3), pass-3 fires using the same pass-2 prompt as a template, choosing sections.
4. The subagent emits a final `result.json` with the proposed URLs and metadata.

**If `https://law.justia.com/codes/<state-slug>/2025/` returns 404 or redirects** — Justia doesn't host 2025 for that state. Try 2024, 2023 in order. Record the substituted vintage in `result.json`'s `actual_vintage_used` field. If even 2023 isn't there, defer the state and report.

**If the pass-1 index returns a Cloudflare challenge page** (HTML ~30 KB containing "Just a moment" or "Performing security verification") — STOP for that state. Surface to user. Don't burn the subagent context retrying; CF blocks at pass-1 level escalated through the 2015 run (see `subagent_canaries/README.md` and the 2015 handoff's "Cloudflare context" section).

Batching: dispatch 3 subagents in parallel per batch (the 2015 run found this was the sustainable concurrency before CF started noticing). Wait for the batch to finish before dispatching the next 3.

### Phase C — section fetch

Once you have `<STATE>_2025` canary bundles, the section-fetch step is a direct clone of the 2015 script with `intended_vintage=2025`. Template:

```python
# /tmp/fetch_2025_sections.py — mirror of /tmp/fetch_2015_sections.py
FETCH_ORDER = [
    # (state, intended_vintage, actual_vintage)
    # populate from result.json's actual_vintage_used field per state
]
# rest identical to the 2015 script — see /tmp/fetch_2015_sections.py on Dans-MacBook-Pro
```

Smallest-first ordering, sequential, sanity-check every bundle for files <500 bytes (CF stubs). Same `rate_limit_seconds` tuning as 2015 — the user halved this to 2.5s on the 2026-05-19 run and confirmed clean.

The script template is on Dans-MacBook-Pro at `/tmp/fetch_2015_sections.py`. **It is NOT committed** (it's a transient driver script). Either rsync it from the desktop, or rewrite from scratch using the body in the 2015 handoff's Step 3.

---

## Dependencies the laptop needs

The laptop already has the worktree if the user has pulled this branch. After pull, verify:

| Artifact | Location | Committed? |
|---|---|---|
| Pass-1 / pass-2 prompts | `src/scoring/api_seed_discovery_pass1_prompt.md`, `api_seed_discovery_pass2_prompt.md` | Yes |
| `retrieve_statute_bundle()` | `src/scoring/statute_retrieval.py` | Yes |
| `PlaywrightClient` | `src/scoring/justia_client.py` | Yes |
| `_build_justia_link_tsv` | `src/scoring/api_retrieval_agent.py` | Yes |
| `subagent_fetch_save.py` helper | `scripts/subagent_fetch_save.py` | Committed in this push (was machine-local on the desktop) |
| 2015 canary bundles (reference) | `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2015/` | Committed in this push |
| 2015 handoff (procedural template) | `docs/active/api-multi-vintage-retrieval/plans/_handoffs/20260518_fetch_2015_section_bodies.md` | Committed in this push |
| 2025 handoff (this doc) | `docs/active/api-multi-vintage-retrieval/plans/_handoffs/20260519_fetch_2025_statute_bundles.md` | Committed in this push |
| 2015 section-fetch driver | `/tmp/fetch_2015_sections.py` on Dans-MacBook-Pro | **Not committed** — rebuild from 2015 handoff Step 3 |

The laptop's `data/` symlink — confirm it points to `~/data/lobby_analysis/` before fetching. New bundles land under the symlink target, not in the worktree's git index.

---

## Things explicitly NOT in scope for this handoff

- ❌ Do NOT try to use the Anthropic direct-API path via `scripts/canary_discovery.py`. Workspace credit is still spent; no timeline on the manual quota request.
- ❌ Do NOT re-run URL discovery for any 2015 state. The 2015 bundles are frozen reproducibility records.
- ❌ Do NOT touch `data/statutes/OH/2025/`. It's the canonical 30-URL GT-shaped bundle from the archived `statute-retrieval` branch.
- ❌ Do NOT try to fetch 2025 for GA, NC, AZ, VA (CF-blocked at 2015), WY, FL, NY (lossy at 2015). Those need URL-discovery cleanup at 2015 first, not a 2025 leap.
- ❌ Do NOT commit anything that lands under `data/` (it's the symlink path, machine-local).

---

## Done-condition for this handoff

The handoff is complete when:

- Each state in the agreed-on list has either a populated `data/statutes/<STATE>/2025/sections/` directory (median file size 1–15 KB, no CF stubs) OR a documented `actual_vintage_used` substitution with the actual-vintage directory populated.
- Each state has a `subagent_canaries/<STATE>_2025/` reproducibility bundle so a future direct-API replay is possible once the Anthropic workspace credit clears.
- The user has a per-state inventory report: which states succeeded at intended 2025, which were substituted (and to what vintage), which (if any) tripped CF or weren't hosted by Justia at all.

---

## Cross-reference

Read in order before starting:

1. This doc (you're here).
2. `20260518_fetch_2015_section_bodies.md` (same dir) — procedural template; especially "Step 1 — Cloudflare probe" (run the equivalent for 2025), "Cloudflare context for the resuming agent", and "Things explicitly NOT in scope".
3. `results/subagent_canaries/README.md` — bundle schema.
4. `src/scoring/api_seed_discovery_pass1_prompt.md` + `api_seed_discovery_pass2_prompt.md` — the LLM-judgment substrate for URL discovery.

# HANDOFF — Justia 2025 statute discovery, 30 states remaining

**Audience:** Suhan Kacholia's Claude Code agent.
**Branch:** `api-multi-vintage-retrieval` (this branch — DO NOT merge to `main`).
**Date authored:** 2026-06-10
**Author:** Dan Parshall's agent (Dans-MacBook-Pro), after Cloudflare rate-limited Dan's IPs mid-fan-out on 2026-06-09.

This doc is **self-contained**. You should not need to read anything else to do the work. Companion docs (`README.md`, dispatch template, prior session logs) are linked where the procedure crosses them; pull them in only if you hit a case this doc doesn't cover.

---

## TL;DR — what to do

1. Check out branch `api-multi-vintage-retrieval`. Set up Python env and Playwright (~5 min, instructions below).
2. **CF probe first** (no API spend) — single Playwright fetch of one Justia state-year-index page. If it returns clean HTML, your IP is good. If it returns a "Just a moment…" interstitial, STOP — Cloudflare blocks Justia at your IP too, and this whole task is moot until that changes.
3. Run 30 Method B canary dispatches (each a `general-purpose` Claude Code subagent) to discover the Justia statute URLs for the 30 (state, 2025) pairs listed below. **Pace at 2-concurrent with a ~5-minute cooldown between batches.**
4. Each dispatch writes a reproducibility bundle under `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2025/`. The bundles are the deliverable.
5. Commit and push the bundles to `origin/api-multi-vintage-retrieval`. **Do not merge to main.** Done.

**You are not asked to do the section-body fetch (Phase 3).** Dan's side will run that once your canary bundles land. Section bodies are gitignored anyway — you couldn't easily ship them back through git even if you wanted to.

**Budget:** plan for **$15–$27** at Anthropic opus rates (30 dispatches × ~$0.45–$0.90 each, calibrated 2026-06-09). At sonnet rates: ~$6–$11. Each subagent is a one-shot dispatch; you control the model and concurrency.

---

## Why we're handing this off

Dan's home and laptop IPs both got CF-blocked mid-session on 2026-06-09 after about 25–30 cumulative Justia fetches. The block appears to be a per-IP cumulative-fetch rate-limit that decays over time but doesn't fully reset between batches. Fresh IPs (yours) should be CF-clear at the start. Don't burn the goodwill: pace yourself per the protocol below.

---

## What `done` looks like

30 new directories at `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2025/`, each containing:

- `pass1_state_index.html` + `.tsv` (state-year-index page)
- `pass1_chosen.json` (subagent's title pick)
- `pass2_<title-slug>.html` + `.tsv` + `_chosen.json` (one set per chosen title)
- `pass3_<chapter-slug>.html` + `.tsv` + `_chosen.json` (one set per chosen chapter that has subsections)
- `result.json` (aggregate output — the load-bearing file)

Each `result.json` must have:
- `playwright_errors: []`
- `proposed_urls` count **≥ 4** (anything less suggests TOC-page mis-fetch; flag in `notes`)
- `actual_vintage_used: 2025` (or `2024` / `2023` / etc. if Justia doesn't host 2025 — record the actual year and flag)

Bundle schema: [`results/subagent_canaries/README.md`](results/subagent_canaries/README.md).

Push the branch when you're done (or every few batches as a backup). Notify Dan via whatever channel he set up with Suhan.

---

## The 30 states

### 28 fresh dispatches (no prior canary work)

CT, DE, HI, ID, IN, IA, KS, KY, ME, MD, MN, MS, MO, MT, NV, NH, NJ, NM, ND, OK, OR, RI, SC, SD, TN, UT, VT, WY

Notes from the prior agent on awkward states (regime priors don't have to be exact — the canary self-corrects by reading the actual Justia TSV — but a rough prior shortens pass-1 reasoning):

| State | Likely regime | Notes |
|---|---|---|
| **WY** | Justia probably hosts only 2010 | Expect vintage substitution. Subagent should fall back via `2024`, `2023`, etc.; if even `2010` is the only year, record `actual_vintage_used: 2010` and flag for human review. |
| **DE** | Title 29 Ch. 58 (Public Officers) + possibly Ch. 91 (Public Integrity Commission) | Two-body — watch for split disclosure provisions. |
| **MD** | State Government Article §§15-101 et seq. (Public Ethics Law) | NOT under a "Lobby" title; pass-1 must find Ethics. |
| **HI** | Hawaii Rev. Stat. Ch. 97 (Lobbyists) | Single-body; flat per-section. |
| **VT** | 2 V.S.A. §261 et seq. (Lobbyist Disclosure) | |
| **WY** (again — emphasis) | Vintage sub almost certain | |

For the rest, use your own knowledge or the state's actual Justia state-year-index TSV to seed the regime prior.

### 2 partial resumes (some pass-1 work already on disk)

| State | What's on disk | What to do |
|---|---|---|
| **AZ** | `subagent_canaries/AZ_2025/pass1_*` (pass-1 picked Title 41 — correct per A.R.S. Title 41 Ch. 7 Art. 8.1); CF fired at pass-2 | Resume from pass-2. Re-fetch the Title 41 TOC and continue. |
| **GA** | `subagent_canaries/GA_2025/pass1_state_index.html` is the CF interstitial; no real work done | Restart from pass-1. Treat as fresh. |

---

## Setup (one-time, ~5 min)

```bash
# 1. Clone (skip if already done)
git clone git@github.com:danparshall/lobby_analysis.git
cd lobby_analysis

# 2. Check out the branch
git fetch origin
git checkout api-multi-vintage-retrieval

# 3. Python env — pinned to 3.12 via .python-version
uv venv
uv sync

# 4. Playwright browser (~91 MB)
uv run --active playwright install chromium

# 5. Smoke-test the helper imports
PYTHONPATH=src uv run --active python -c \
  "from scoring.justia_client import PlaywrightClient; \
   from scoring.api_retrieval_agent import _build_justia_link_tsv; \
   print('ok')"
```

**Anthropic API key:** the Method B subagent runs from your Claude Code session and inherits parent auth. You do not need to set `ANTHROPIC_API_KEY` in the env unless you're using a script-based direct-API path (not the case here).

**Don't make a `.env.local` symlink.** Dan's machine has one; it's machine-local and not needed for this work.

**`data/` directory:** Dan's machine symlinks `data/` to `~/data/lobby_analysis/` as a cross-machine sync pattern. You don't need it for this handoff because you're not doing Phase 3 section fetch. If `data/` doesn't exist on your machine, that's fine.

---

## CF probe — do this FIRST, before any dispatches

```bash
PYTHONPATH=src uv run --active python scripts/subagent_fetch_save.py \
    /tmp/cf_probe pass1 https://law.justia.com/codes/hawaii/2025/
```

- **Good:** TSV file at `/tmp/cf_probe/pass1_state_index.tsv` is non-empty and contains Hawaii's titles.
- **Bad:** HTML at `/tmp/cf_probe/pass1_state_index.html` contains `"Just a moment"` or `"Performing security verification"`. STOP. Notify Dan; this task can't proceed from your IP until CF clears.

Re-probe between batches (every 2–3 dispatches) with a different state. If CF starts blocking mid-fan-out, drop concurrency to 1 and lengthen cooldowns; if still blocking, stop and notify Dan.

---

## Dispatch protocol

### The canonical dispatch template

[`docs/active/api-multi-vintage-retrieval/plans/_handoffs/20260519_subagent_dispatch_prompt.md`](plans/_handoffs/20260519_subagent_dispatch_prompt.md) — the parameterized brief that each Method B subagent reads. It includes the pass-1/2/3 reasoning steps, the Cloudflare triage rules, the `result.json` schema, and the helper-script invocation.

### Per-dispatch invocation

For each state in the 28-fresh list and for the 2 partials, call the Claude Code Agent tool with:

- `subagent_type: "general-purpose"`
- `description`: e.g. `"Justia 2025 URL discovery: HI"`
- `prompt`: a wrapper that:
  1. Names the state, slug (lowercase full state name — `hawaii`, `connecticut`, etc.), vintage (`2025`), `OUT_DIR` (absolute path to `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2025/`), and `WORKING_DIR` (absolute path to your repo checkout).
  2. Points at the dispatch template above for procedure.
  3. Includes a one-paragraph regime prior if you have one (see the table in "28 fresh dispatches" above; use your own knowledge for the rest).
  4. Reiterates acceptance: `playwright_errors: []`, `proposed_urls` ≥ 4, `actual_vintage_used` matches the request (or is recorded if substituted).

### Pacing

- **2 concurrent subagents per batch.** (The 2026-05-18 ceiling was 3, but Dan's 2026-06-09 batch tripped CF at 3 — drop to 2 by default.)
- **~5-minute cooldown between batches.** Set a wall-clock wait.
- **Re-probe CF every 2–3 batches** with a single helper invocation (no API spend).
- **15 batches × 2 = 30 dispatches.** Plan ~2–3 hours total wall time including cooldowns; less of your active time since the subagents run in parallel.

### Per-batch verification (before launching the next batch)

For each completed bundle:

1. `result.json` exists.
2. `playwright_errors: []`.
3. `proposed_urls` count ≥ 4.
4. `actual_vintage_used` is 2025 (or note the substituted year).

If any bundle fails (e.g., CF block, empty TSV, prose-only LLM response): mark the state for retry in a later batch — don't loop the same state immediately.

### Commit cadence

Commit after each batch (2 bundles per commit). Push every 2–3 batches as backup. Use a message format like:

```
canaries: batch N (HI/CT) for 50-state 2025 expansion — 2/2 clean
```

Do **not** force-push, rebase, or rewrite history on this branch.

---

## Key files and where they live

| File | Role |
|---|---|
| [`docs/active/api-multi-vintage-retrieval/README.md`](README.md) | Branch overview — Method A vs Method B, operational lessons accumulated across sessions. Read after this doc if you want background. |
| [`docs/active/api-multi-vintage-retrieval/plans/_handoffs/20260519_subagent_dispatch_prompt.md`](plans/_handoffs/20260519_subagent_dispatch_prompt.md) | The canonical per-subagent dispatch template. Each Method B subagent reads this. |
| [`docs/active/api-multi-vintage-retrieval/results/subagent_canaries/README.md`](results/subagent_canaries/README.md) | Bundle schema — what each `<STATE>_<VINTAGE>/` directory must contain. |
| [`scripts/subagent_fetch_save.py`](../../../scripts/subagent_fetch_save.py) | Playwright fetch + TSV-building helper. All Justia fetches go through this. |
| [`src/scoring/api_seed_discovery_pass1_prompt.md`](../../../src/scoring/api_seed_discovery_pass1_prompt.md) | Pass-1 reasoning template (title selection). |
| [`src/scoring/api_seed_discovery_pass2_prompt.md`](../../../src/scoring/api_seed_discovery_pass2_prompt.md) | Pass-2 AND pass-3 reasoning template (chapter / section selection). |

### Reference canary bundles (study these before dispatching)

These are clean, well-formed bundles from prior sessions — match this shape:

- `subagent_canaries/AL_2025/` — single-body, per-section leaves
- `subagent_canaries/LA_2025/` — two-body (Title 24 + Title 49)
- `subagent_canaries/NE_2025/` — unicameral flat-chapter
- `subagent_canaries/VA_2025/` — deeper hierarchy (Title 2.2 / Ch. 4 / Art. 3)

---

## Branch-hygiene rules (multi-committer repo)

Multiple fellows push to this repo. These rules are load-bearing — please follow them:

- **Never merge this branch to `main`.** Dan decides when research lines merge.
- **Never rebase, force-push, or rewrite history** on this branch.
- **Never delete remote branches** (yours or anyone else's).
- **Only touch files under `docs/active/api-multi-vintage-retrieval/`** plus the `STATUS.md` row for this branch (the table at the top of `STATUS.md` — only edit the `api-multi-vintage-retrieval` row, leave others alone). Don't touch other fellows' branch docs.
- **Don't add features that weren't asked for.** YAGNI. If you find something that looks like it needs fixing outside the dispatch flow, surface it in your hand-back report rather than fixing it.

---

## Failure modes you may hit

| Symptom | What it means | What to do |
|---|---|---|
| `pass1_state_index.html` contains "Just a moment…" or "Performing security verification" | Cloudflare blocked the fetch | Record `playwright_errors: ["cloudflare_blocked_at_pass1"]`, do not retry this state, pause the whole fan-out, re-probe CF after cooldown. |
| `pass1_state_index.tsv` is empty but HTML is well-formed | Justia layout shift the helper doesn't anticipate (rare — the 2026-05-19 patch covers known 2025 conventions) | Record `playwright_errors: ["pass1_tsv_empty_unexpected"]`, paste first 1000 chars of HTML into `notes`, move on. |
| Justia 404 / "Codes Not Found" on `/codes/<slug>/2025/` | Justia doesn't host 2025 for this state | Retry pass-1 with `2024`, then `2023`. Record `actual_vintage_used` accordingly. If `2010` is the latest, accept it (this is what we expect for WY). |
| Subagent returns prose instead of JSON in a `chosen.json` | Pass-1 prompt's `justia_unavailable: true` branch triggered with bad output shape | Subagent should fall back to `_unparseable_response_fallback` (parser was hardened 2026-05-15). If you see this in `result.json` with `proposed_urls: []` and prose in `notes`, mark the state for retry with a stronger regime prior. |
| `proposed_urls` count is high but URLs look like TOC pages, not section pages | CO-2025 bug pattern (TOC mistaken for section) | Spot-check `proposed_urls`: do they end in something like `/section-X-Y/` or just `/article-N/`? If Article-level, flag in `notes` — Phase 3 will catch it via the median-size gate, but flagging here is faster. |
| Subagent runs over budget / many retries on one state | Pathological state, possibly a regime prior mismatch | Stop the subagent, mark the state for follow-up, move on. Don't burn budget on one stuck state. |

---

## What to do if you finish early (or if some states fail)

- If you finish all 30 cleanly: push the branch, notify Dan.
- If some states failed (CF, empty TSV, prose, etc.): push what you have, list the failed states in a brief hand-back message, and stop. Don't loop on retries — Dan / another agent will re-attempt later under different conditions.
- If CF starts blocking your IP early: push what you have, document the CF observation (which state, which pass, cumulative-fetch count) in a short note appended to the bottom of this HANDOFF doc or in a new file at `docs/active/api-multi-vintage-retrieval/results/20260610_suhan_cf_observation.md`. The CF posture data is itself useful research.

---

## Hand-back to Dan

When done (success or partial), push the branch and provide a short report containing:

1. How many of 30 are clean (`playwright_errors: []`, `proposed_urls` ≥ 4).
2. List of states with failures, with the failure type (CF block / empty TSV / prose / other).
3. Total cost spent (rough estimate from the subagent-dispatch telemetry).
4. Any CF observations from your IP / network.
5. Anything else you noticed that would inform the next session — e.g., a state with an unusual regime, a Justia layout case the helper doesn't handle, a prior in the table above that turned out wrong.

That's it. Thank you.

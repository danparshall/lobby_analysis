# Handoff: fetch 2015 section bodies + populate `data/statutes/<STATE>/2015/`

**Date opened:** 2026-05-18 12:45 UTC
**Branch:** `api-multi-vintage-retrieval` (worktree at `.worktrees/api-vintage`)
**Top commit at handoff:** `8db1ad4` (b4: parser hardening + pass-1 prompt strengthening — Defect 1 closed)
**Originating convos / results:**
- 2026-05-18 subagent dispatch (8 batches of 3 subagents each running the three-pass URL discovery in their own context, bypassing the spent Anthropic workspace credit awaiting Dan's manual quota request)
- All result.json + HTML + TSV bundles live under `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_<VINTAGE>/`
- Helper script: `scripts/subagent_fetch_save.py` (untracked, machine-local)

**Why this handoff exists:** the URL-discovery work is done for 20 states at 2015. The user asked to populate `data/statutes/<STATE>/2015/sections/*.txt` from those URLs (so they can start testing compendium-population locally, parallel to the OH 2010 + OH 2025 pair that's already on disk). The fetch attempt **immediately hit Cloudflare** on the first probe (TX 2015 single section returned the 365-byte CF challenge page instead of statute text). User changed IP mid-attempt; the resuming agent needs to retry under the new IP.

---

## TL;DR for the resuming agent

1. **Verify the new IP isn't CF-blocked** — do a single-section probe (see [Step 1](#step-1--cloudflare-probe)). If it returns a real statute body (typically ≥1 KB, doesn't contain "Performing security verification"), proceed. If it's still the 365-byte CF stub, stop and surface to the user.
2. **Read this whole doc before fetching anything else** — there are 17 states' worth of URLs to process (~271 URLs total), and several have notes about scope, vintage substitution, or partial-blocking that matter.
3. **Delete the bogus `data/statutes/TX/2015/` bundle** that's left over from the failed probe **only after** you've confirmed the new IP is clean (it's currently retained as evidence of the pre-IP-switch CF state).
4. **Fetch one state at a time, smallest first.** Sequential, not concurrent — concurrent fetches from one IP were what surfaced the CF block to begin with. The existing pipeline's `PlaywrightClient(rate_limit_seconds=5.0)` handles per-request throttling within a state; you provide the inter-state pacing by going one at a time.
5. **Sanity-check every bundle after writing it.** A real statute body is typically 1-15 KB; anything under ~500 bytes is suspect (probably another CF stub or a 404 placeholder).
6. **Do NOT delete or modify the existing `subagent_canaries/<STATE>_2015/` bundles** under `docs/active/`. Those are the URL-discovery reproducibility bundles; this fetch task consumes them but doesn't overwrite them.

---

## Background context (skip if you already know the branch)

This branch builds an LLM-driven Justia URL-discovery pipeline so we can pull state lobbying-disclosure statutes across all 50 states × ~7 historical vintages, as substrate for multi-rubric calibration per the Compendium 2.0 success criterion (one extraction pipeline, multi-year reliability, per-rubric projections validate against published per-state scores).

The orchestrator (`src/scoring/api_retrieval_agent.py`) normally does URL discovery via direct `anthropic.AsyncAnthropic` calls. The Anthropic workspace credit is currently spent — **no automatic reset; awaiting Dan's manual quota-increase request to Anthropic**, no timeline known. To keep moving, today's work used **Claude Code Agent subagents as the LLM-judgment substrate** instead — each subagent fetched Justia TOC pages via Playwright, applied the pass-1/pass-2/pass-3 prompts in its own reasoning, and emitted a structured `result.json` of proposed URLs. Bundles include the raw HTML + cleaned TSV input to each pass, so a future direct-API run can replay against identical inputs (see `subagent_canaries/README.md`).

**The URL-discovery is done.** What remains: fetch the actual section bodies at each proposed URL and stash them as `data/statutes/<STATE>/<VINTAGE>/sections/*.txt`, matching the format the `statute-retrieval` branch produced for OH 2010 + OH 2025.

---

## What's already on disk vs what needs fetching

### Already populated (don't touch)

`data/statutes/<STATE>/<VINTAGE>/sections/` is populated for:

| State | Vintage | Section files | Notes |
|---|---|---|---|
| CA | 2010 | yes | from `statute-retrieval` |
| NY | 2010 | yes | from `statute-retrieval` |
| OH | 2010 | 38 files | from `statute-retrieval` (includes hop-1 cross-refs) |
| OH | 2025 | 30 files | from `statute-retrieval` (clean 30-URL GT shape) |
| TX | 2009 | yes | from `statute-retrieval` |
| WI | 2010 | yes | from `statute-retrieval` |
| WY | 2010 | yes | from `statute-retrieval` |

OH 2010 ↔ OH 2025 is the canonical multi-vintage pair the user is currently testing compendium population against. Don't touch.

### Bogus bundle from the failed probe (delete after verifying new IP)

`data/statutes/TX/2015/`
- Contains `sections/government-code-title-3-subtitle-a-chapter-305.txt` (**365 bytes — Cloudflare challenge page text**, NOT a statute body)
- Contains `manifest.json` claiming the bogus file is a "curated core lobbying chapter"
- Was retained against this agent's instinct-to-delete because the user wanted it preserved across the IP switch as evidence of the pre-switch CF state
- **Delete this entire dir once the new IP's first successful fetch confirms we're past the CF state.** Otherwise compendium-population code will treat the 365-byte CF stub as real statute text.

### To fetch (17 states at 2015)

Source of URLs: each state's `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_2015/result.json`, field `proposed_urls[].url`.

| State | URLs | Bundle quality | Notes |
|---|---|---|---|
| TX | 1 | full | Government Code Ch. 305 — single directory-leaf URL; tree depth 5; smallest, best probe target |
| MA | 11 | full | c. 3 §§ 39-50 minus § 40 (repealed); tree depth 4 |
| PA | 11 | full | 65 Pa.C.S. §§ 13A01-13A11; tree depth 3; byte-equivalent structure to PA 2010 |
| CO | 11 | full | **Vintage substituted to 2016** (Justia doesn't host CO 2015); Title 24 Art. 6 Part 3 §§ 24-6-301 to 24-6-309 |
| IL | 12 | full | 25 ILCS 170 + 5 ILCS 420 + 5 ILCS 430 article-level pages; tree depth 4; slug shift from 2010 |
| AR | 16 | full | Title 21 Ch. 8 Subchs. 4/5/6 + Title 10 Ch. 1; tree depth 4 |
| WI | 16 | full | Ch. 13 §§ 13.61-13.75; per-section leaves; matches WI 2010 GT structure modulo slug shape |
| WA | 19 | full | Title 42 Ch. 42.17A §§ .005-.770; **resolved Defect 2** (2010 silent-empty was a real miss) |
| AK | 20 | full | Title 24 Ch. 24.45 §§ .011-.181 across Articles 1-5; tree depth 4 |
| MI | 23 | full | Act 472 of 1978 (MCL 4.411-4.431); tree depth 4 |
| WV | 24 | full | Ch. 6B Ethics Act Articles 1/2/3; tree depth 4 |
| OH | 52 | full | Title 1 Chs. 101 + 121 + 102; tree depth 3; **biggest expected pull** |
| CA | 55 | full | code-gov Title 9 Chs. 2/6/11; tree depth 6 (deepest) |
| **GA** | **2** | **partial** | only article-TOC URLs (Art. 4 + Art. 1); pass-3 was CF-blocked. **Fetching these will save TOC pages, not statute bodies** — likely useful only as cross-reference index, not as statute text |
| **NC** | **8** | **partial** | only article-TOC URLs (8 articles of Ch. 120C); same caveat as GA |
| **AZ** | **0** | **empty** | CF-blocked at pass-1; nothing to fetch |
| **VA** | **0** | **empty** | CF-blocked at pass-1; nothing to fetch |

**Total fetches if you do all 17:** ~281 URLs (271 from full bundles + 10 from GA/NC partials)
**Recommended order:** TX (1) → MA (11) → PA (11) → CO (11) → IL (12) → AR (16) → WI (16) → WA (19) → AK (20) → MI (23) → WV (24) → OH (52) → CA (55)
**Recommended scope:** SKIP GA + NC + AZ + VA for now. Re-canary those (URL discovery, not section fetch) once CF clears, then come back.

### 2015 states with NO bundle on disk

Three 2015 states were canaried in the early "lossy" batch before TSV-capture was added: **WY, FL, NY**.

**Update 2026-05-18 (verified):** The original handoff suggested URLs could be recovered from "the conversation transcript on commit `8db1ad4`" by grepping `convos/` and `RESEARCH_LOG.md`. A subsequent agent verified this is **not feasible** — those locations contain no WY/FL/NY 2015 entries (case-insensitive grep on state codes, full names, "lossy", and "/2015" URLs all came back empty outside the saved subagent_canaries bundles). The lossy batch's subagents emitted prose-only logs, not `result.json`-shaped artifacts, and the prose itself wasn't preserved in committed docs.

Recovery options, narrowed:
- **Re-canary them** under the current subagent dispatch once Cloudflare is passing (cheap, ~$0.50 of Max-plan tokens). **Now the only realistic path.**
- The Claude Code session transcripts under `~/.claude/projects/-Users-dan-code-lobby-analysis/` (JSONL, not git-tracked) may contain the URLs verbatim from the original lossy run; high effort to extract, uncertain payoff.

Defer this until either Cloudflare clears or the section-fetch work for the 17 fully-discovered states is otherwise unblocked.

---

## Step-by-step

### Step 0 — orient

1. `cd /Users/dan/code/lobby_analysis/.worktrees/api-vintage` (stay in this worktree, NOT the main checkout)
2. Read `subagent_canaries/README.md` for the bundle format
3. Read `src/scoring/statute_retrieval.py` lines 248-325 for `retrieve_statute_bundle()` — the function you'll be calling
4. Read `src/scoring/justia_client.py` lines 223-261 for `PlaywrightClient.fetch_page()` — note the `rate_limit_seconds=5.0` default and `challenge_timeout_seconds=30.0` default

### Step 1 — Cloudflare probe

Run a single-section fetch against TX 2015's one URL and inspect the result before doing anything else:

```bash
cd /Users/dan/code/lobby_analysis/.worktrees/api-vintage && PYTHONPATH=src uv run --active python <<'PY'
import json
from pathlib import Path
from scoring.justia_client import PlaywrightClient

result = json.loads(Path("docs/active/api-multi-vintage-retrieval/results/subagent_canaries/TX_2015/result.json").read_text())
url = result["proposed_urls"][0]["url"]
print(f"Fetching: {url}")
html = PlaywrightClient().fetch_page(url)
print(f"Fetched {len(html)} bytes")
print(f"Title check: {'Just a moment' in html[:5000]}  (True = CF challenge, False = real page)")
print(f"Statute marker check: {'305.' in html[:50000] or 'lobby' in html.lower()[:50000]}  (True suggests real TX Government Code Ch. 305 content)")
PY
```

**Decision tree:**
- **HTML ~31 KB + "Just a moment" True + statute marker False** → CF is still blocking. **STOP. Surface to user.** Do not proceed.
- **HTML ≥10 KB + "Just a moment" False + statute marker True** → CF cleared, proceed to Step 2.
- **Anything else** (e.g. tiny HTML, ambiguous markers) → surface to user with the raw `html[:1000]` snippet.

### Step 2 — clean up the bogus TX 2015 bundle

ONLY if Step 1 confirms CF is clear:

```bash
rm -rf data/statutes/TX/2015
ls data/statutes/TX/   # expect: only "2009" remains
```

### Step 3 — fetch the 13 fully-bundled states, sequentially, smallest first

```bash
PYTHONPATH=src uv run --active python <<'PY'
import json
import sys
from pathlib import Path
from scoring.justia_client import PlaywrightClient
from scoring.statute_retrieval import retrieve_statute_bundle

# Order: smallest first, so we fail fast if CF re-engages mid-run
FETCH_ORDER = [
    ("TX", 2015, 2015),
    ("MA", 2015, 2015),
    ("PA", 2015, 2015),
    ("CO", 2015, 2016),  # vintage-substituted at canary time
    ("IL", 2015, 2015),
    ("AR", 2015, 2015),
    ("WI", 2015, 2015),
    ("WA", 2015, 2015),
    ("AK", 2015, 2015),
    ("MI", 2015, 2015),
    ("WV", 2015, 2015),
    ("OH", 2015, 2015),
    ("CA", 2015, 2015),
]
CANARY_DIR = Path("docs/active/api-multi-vintage-retrieval/results/subagent_canaries")
STATUTES_DIR = Path("data/statutes")
client = PlaywrightClient()

for state, intended_vintage, actual_vintage in FETCH_ORDER:
    result = json.loads((CANARY_DIR / f"{state}_{intended_vintage}" / "result.json").read_text())
    urls = [p["url"] for p in result["proposed_urls"]]
    dest = STATUTES_DIR / state / str(intended_vintage)
    if dest.exists():
        print(f"[skip] {state} {intended_vintage}: dest already exists at {dest}", file=sys.stderr)
        continue
    print(f"[start] {state} {intended_vintage} → {len(urls)} URLs → {dest}", flush=True)
    manifest_path = retrieve_statute_bundle(
        client,
        state_abbr=state,
        vintage_year=intended_vintage,
        urls=urls,
        dest_dir=dest,
        year_delta=actual_vintage - intended_vintage,
        direction="exact" if actual_vintage == intended_vintage else ("post" if actual_vintage > intended_vintage else "pre"),
    )
    # SANITY CHECK: scan for CF stubs (any file <500 bytes likely bogus)
    suspect = []
    for txt in (dest / "sections").iterdir():
        size = txt.stat().st_size
        if size < 500:
            head = txt.read_text(errors="replace")[:200]
            if "Performing security verification" in head or "Just a moment" in head:
                suspect.append((txt.name, size, "CF_STUB"))
            else:
                suspect.append((txt.name, size, "TINY"))
    if suspect:
        print(f"[ALERT] {state} {intended_vintage} has {len(suspect)} suspect files: {suspect[:5]}", file=sys.stderr)
        print(f"[STOP] CF likely re-engaged. Surfacing to user.", file=sys.stderr)
        break
    print(f"[done] {state} {intended_vintage}: {len(list((dest/'sections').iterdir()))} files written", flush=True)

print("All states processed.")
PY
```

**Run this in foreground** (not background) so you can watch the per-state status lines. Expected total wall time at 5s rate-limit × 271 fetches = ~22 minutes minimum, probably 25-30 with Playwright startup overhead per state.

If the script stops on a CF re-engagement, **don't retry the failing state automatically** — surface to user. They may want to switch IP again, wait, or pivot to a different fetcher (playwright-stealth, non-headless browser, etc.).

### Step 4 — verify after each successful state

After each state's bundle lands, the manifest gets written. Spot-check a couple:

```bash
PYTHONPATH=src uv run --active python <<'PY'
import json
from pathlib import Path
for state, vintage in [("TX", 2015), ("PA", 2015), ("WI", 2015)]:
    m = Path(f"data/statutes/{state}/{vintage}/manifest.json")
    if not m.exists():
        continue
    manifest = json.loads(m.read_text())
    n = len(manifest["artifacts"])
    sizes = sorted(a["bytes"] for a in manifest["artifacts"])
    print(f"{state} {vintage}: {n} sections, byte range {sizes[0]} → {sizes[-1]}, median {sizes[n//2]}")
PY
```

Healthy range: 500 bytes (very short section) to 30+ KB (long section like OH 101.72). Median typically 1-5 KB. Anything with min <500 is suspect.

### Step 5 — commit + surface to user

Once all 13 states are done (or the script stops with CF re-engagement):

```bash
git add data/statutes/  # if data/ is tracked (it's symlinked; check `git status` first)
git status
# probably need to instead add the manifests + sections explicitly given the symlink situation
```

Note: `data/` in this worktree is a symlink to `~/data/lobby_analysis/`. New files written under `data/statutes/<STATE>/2015/` land in the shared data directory, NOT inside the worktree's git index. They persist across worktrees but are not committable from here. The user's CLAUDE.md memory has a note: "data/ symlink is intentional, don't auto-fix" — respect that. If the user wants these tracked, they'll surface it.

The handoff completion message to the user should report:
- Which states succeeded (with per-state file count and byte range)
- Which states (if any) tripped CF and stopped the script
- The current state of the lossy 3 (WY, FL, NY at 2015 — still unfetched, deferred)
- The current state of GA + NC + AZ + VA (URL discovery incomplete; recommend deferring section fetch)

---

## Cloudflare context for the resuming agent

Today's full timeline of Cloudflare interactions:
- **Batches A-D (12 states)** — 0 CF errors across ~36 page fetches; sustained URL-discovery worked cleanly
- **Batch E (MI, GA, NC)** — MI clean; GA's pass-3 of Art. 4 blocked across 3 retries; NC's pass-3 of all 8 articles blocked
- **Batch F (VA, AZ) post-IP-switch attempt** — both blocked at pass-1 (state index itself), most aggressive block yet
- **Post-second-IP-switch single-section probe (Step 1 of this task)** — TX 2015's single statute section returned 365-byte CF challenge text

**Pattern:** Cloudflare appears to be progressively widening the block as the day went on. Started with pass-3-only blocks on specific articles, ended with pass-1 blocks even on state-index pages. The user's IP switches haven't fully cleared it, which suggests the bot signal isn't purely IP — likely also Playwright headless Chromium fingerprint (User-Agent string, navigator.webdriver, etc.).

**If Step 1 still shows CF blocking on a new IP:** technical workarounds available, in rough order of effort:
1. `playwright-stealth` Python package — masks ~15-20 fingerprint leaks; `uv add playwright-stealth` + light code change in `justia_client.py`
2. Non-headless Playwright (`p.chromium.launch(headless=False)`) — slower (visible browser) but fewer bot signals
3. Different egress entirely — different machine (tarragon vs the macbooks)
4. Wait 24-48h for Cloudflare's state to age out
5. Contact Justia directly per the Section 29 ToS framing the user worked out today (state codes are public-domain, PRO doesn't have viable coverage, asking for technical cooperation only)

The user's preference if all else fails is probably option 5 (contact Justia) — they already drafted the framing.

---

## Things explicitly NOT in scope for this handoff

- ❌ Do NOT re-run subagent canaries for GA / NC / AZ / VA URL discovery. Those need CF to be passing on **TOC** fetches, which is even more sensitive than section fetches. Defer until after the main 13-state section fetch lands.
- ❌ Do NOT modify the URL-discovery prompts (`api_seed_discovery_pass1_prompt.md` / `api_seed_discovery_pass2_prompt.md`). The URL discovery is done.
- ❌ Do NOT make any Anthropic API calls — workspace credit is spent. **No automatic reset**; Dan needs to manually request a quota increase from Anthropic before direct-API calls resume. No timeline.
- ❌ Do NOT commit anything new to git unless the user asks. The data/ symlink situation needs care.
- ❌ Do NOT touch `data/statutes/OH/2010/`, `data/statutes/OH/2025/`, or any other pre-existing populated state-vintage dir. Those are the canonical bundles from the `statute-retrieval` branch.
- ❌ Do NOT delete the `subagent_canaries/<STATE>_2015/` bundles. They're the reproducibility record for the URL-discovery work and are needed for replay once the Anthropic workspace credit is restored.

---

## Quick-reference: the bundle format you're consuming

Each `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_<VINTAGE>/result.json` has this schema (you only need `proposed_urls`):

```json
{
  "state": "...",
  "vintage": 2015,
  "actual_vintage_used": 2015,
  "prompt_git_rev": "8db1ad4654...",
  "proposed_urls": [
    {"url": "https://law.justia.com/codes/.../section-XXX/", "role": "core_chapter|support_chapter|leaf", "rationale": "..."}
  ],
  "pass1_chosen_titles": [...],
  "pass2_chosen_chapters": [...],
  "pass3_invoked_on": [...],
  "tree_depth": 3,
  "playwright_errors": [],
  "notes": "..."
}
```

You only need `proposed_urls[].url` for this task. The other fields are URL-discovery metadata for direct-API replay later.

---

## Done-condition for this handoff

The handoff is complete when one of these is true:

- **All 13 fully-bundled states have populated `data/statutes/<STATE>/2015/sections/` with median section size in the 1-15 KB range** (no CF stubs detected). Update the user with the final state inventory.
- **CF re-engaged partway through.** Update the user with which states succeeded, which one stopped the run, and the current `data/statutes/*/2015/` inventory.
- **CF blocking from the start (Step 1 probe failed).** Update the user immediately; no further fetches attempted.

The 4 incomplete-discovery states (GA, NC, AZ, VA) and the 3 lossy states (WY, FL, NY) remain explicitly deferred regardless — those are URL-discovery problems, not section-fetch problems.

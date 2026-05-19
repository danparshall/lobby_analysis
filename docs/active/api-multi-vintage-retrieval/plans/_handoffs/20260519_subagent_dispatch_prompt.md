# Subagent Dispatch Prompt — per-(state, vintage) Justia URL discovery

**Date authored:** 2026-05-19
**Branch:** `api-multi-vintage-retrieval` (worktree `.worktrees/api-vintage`)
**Purpose:** Self-contained brief executed by a Claude Code subagent (Agent tool, subagent_type=`general-purpose`) to produce one reproducibility bundle at `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_<VINTAGE>/` for one `(state, vintage)` pair. Used by the 2025 fan-out (per [`20260519_fetch_2025_statute_bundles.md`](20260519_fetch_2025_statute_bundles.md)) and reusable for any future vintage.

**Calling convention:** the dispatcher fills in `<STATE>`, `<STATE_SLUG>`, `<VINTAGE>`, `<OUT_DIR>` and pastes the rendered prompt into the Agent tool call. Each subagent handles one pair; the dispatcher batches in groups of 3 (per the 2026-05-18 desktop CF-sustainability finding).

---

## Inputs (filled in at dispatch time)

- `STATE`: e.g., `TX`
- `STATE_SLUG`: Justia URL slug, lowercase full state name. The 12 priority states for the 2025 fan-out:
  - `TX` → `texas`
  - `MA` → `massachusetts`
  - `PA` → `pennsylvania`
  - `CO` → `colorado`
  - `IL` → `illinois`
  - `AR` → `arkansas`
  - `WI` → `wisconsin`
  - `WA` → `washington`
  - `AK` → `alaska`
  - `MI` → `michigan`
  - `WV` → `west-virginia`
  - `CA` → `california`
- `VINTAGE`: e.g., `2025`
- `OUT_DIR`: absolute path to the bundle, typically `/Users/dan/code/lobby_analysis/.worktrees/api-vintage/docs/active/api-multi-vintage-retrieval/results/subagent_canaries/<STATE>_<VINTAGE>/`
- `WORKING_DIR`: `/Users/dan/code/lobby_analysis/.worktrees/api-vintage`

---

## Read these first (one-shot, before any fetches)

1. `src/scoring/api_seed_discovery_pass1_prompt.md` — pass-1 reasoning template (title selection)
2. `src/scoring/api_seed_discovery_pass2_prompt.md` — pass-2 AND pass-3 reasoning template (chapter / section selection)
3. `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/README.md` — bundle schema you must emit
4. `docs/active/api-multi-vintage-retrieval/results/subagent_canaries/TX_2015/result.json` — example of the final `result.json` shape

**Note on the helper:** `_build_justia_link_tsv` was patched 2026-05-19 (commit `28b1aab`) to handle Justia's year-less "current code" link convention for 2025. You don't need to do anything special — the helper produces year-prefixed URLs uniformly. Just be aware that the TSV's URLs are reliable and the year-prefixed form is the canonical one for downstream Phase C.

---

## Procedure

### Step 1 — Pass 1 (state-year index)

Fetch via helper from `WORKING_DIR`:

```
PYTHONPATH=src uv run --active python scripts/subagent_fetch_save.py \
    <OUT_DIR> pass1 https://law.justia.com/codes/<STATE_SLUG>/<VINTAGE>/
```

The helper writes `<OUT_DIR>/pass1_state_index.html` and `.tsv` and prints the TSV to stdout.

**Triage the result:**

- **Cloudflare challenge** (HTML contains `Just a moment` or `Performing security verification` in the first 5000 chars): STOP. Emit `result.json` with `playwright_errors: ["cloudflare_blocked_at_pass1"]`, `proposed_urls: []`, `actual_vintage_used: null`, `notes` explaining the block. Do NOT retry.
- **404 / "Codes Not Found" / empty HTML**: Justia doesn't host `<VINTAGE>` for this state. Retry with `<VINTAGE>-1`, then `<VINTAGE>-2`. Record the substituted year in `actual_vintage_used`. If even `<VINTAGE>-2` fails, emit `result.json` with `playwright_errors: ["no_justia_vintage_within_range"]`, `proposed_urls: []`, exit.
- **Well-formed HTML but empty TSV**: surface as a structural anomaly — the year-less patch should already handle 2025; an empty TSV here suggests a different layout shift. Emit `result.json` with `playwright_errors: ["pass1_tsv_empty_unexpected"]`, `proposed_urls: []`, paste the first 1000 chars of HTML into `notes`, exit.
- **Populated TSV**: proceed.

After successful fetch: read `<OUT_DIR>/pass1_state_index.tsv`. Apply pass-1 reasoning (the template at `src/scoring/api_seed_discovery_pass1_prompt.md` with `{state}`, `{vintage}`, `{state_index}` filled in by you — `state_index` is the TSV content verbatim). Emit `<OUT_DIR>/pass1_chosen.json` conforming exactly to the schema in that prompt: `chosen_titles[]`, `justia_unavailable`, `alternative_year`, `notes`.

### Step 2 — Pass 2 (one per chosen title)

For each title in `pass1_chosen.json.chosen_titles`:

```
PYTHONPATH=src uv run --active python scripts/subagent_fetch_save.py \
    <OUT_DIR> pass2 <title-url>
```

The helper derives the filename slug from the URL's last path segment. Read the TSV. Apply pass-2 reasoning (template at `src/scoring/api_seed_discovery_pass2_prompt.md`). Emit `<OUT_DIR>/pass2_<title-slug>_chosen.json`.

**Triage failures per-title** (do NOT abort the whole subagent):

- Cloudflare at pass-2 → record in `playwright_errors`, skip this title.
- Empty TSV at pass-2 → either the title page is itself a leaf (rare; record and skip), or there's a layout issue (record `pass2_tsv_empty_for_<title>` and continue with other titles).

### Step 3 — Pass 3 (one per chosen chapter)

For each chapter in `pass2_<title-slug>_chosen.json.chosen_chapters`:

```
PYTHONPATH=src uv run --active python scripts/subagent_fetch_save.py \
    <OUT_DIR> pass3 <chapter-url>
```

Read the TSV. Two cases:

1. **Empty TSV** — the chapter page IS the leaf (full statute body lives at that URL). Add the chapter URL to `proposed_urls` with `role: "core_chapter"`. **Do NOT run pass-3 reasoning** for this chapter. (Empirically common: TX-style directory-leaf chapters.)
2. **Non-empty TSV** — the chapter has subsections. Apply pass-3 reasoning (reuse `api_seed_discovery_pass2_prompt.md` as the template; pass the chosen-title rationale through). Emit `<OUT_DIR>/pass3_<chapter-slug>_chosen.json`. Add each chosen section URL to `proposed_urls` with `role: "core_chapter"`.

### Step 4 — Aggregate `result.json`

Compute:

- `tree_depth`: number of `/`-separated path segments at the deepest leaf (e.g., TX 2015 was 5: `state → code → title → subtitle → chapter`).
- `prompt_git_rev`: shell `git -C <WORKING_DIR> rev-parse HEAD`.
- `proposed_urls`: union of all chosen URLs across passes 2 and 3, deduplicated by `(url, role)`.

Emit `<OUT_DIR>/result.json` matching this shape (mirror `TX_2015/result.json` exactly):

```json
{
  "state": "<STATE>",
  "vintage": <VINTAGE>,
  "actual_vintage_used": <int or null>,
  "prompt_git_rev": "<git rev>",
  "proposed_urls": [
    {"url": "...", "role": "core_chapter|support_chapter", "rationale": "..."}
  ],
  "pass1_chosen_titles": ["..."],
  "pass2_chosen_chapters": ["..."],
  "pass3_invoked_on": ["..."],
  "tree_depth": <int>,
  "playwright_errors": [],
  "notes": "<free-text: regime structure, vintage substitution rationale, anything noteworthy>"
}
```

---

## Constraints

- **ALL Justia fetches via `scripts/subagent_fetch_save.py`.** No `curl`, no `requests`, no direct Playwright code. The helper handles Playwright session lifecycle + rate-limiting.
- **Sequential fetches within your own context.** No parallel subprocesses inside the subagent.
- **Bundle structure MUST match `subagent_canaries/README.md`** — downstream Phase C section-fetch consumes these bundles.
- **Do NOT modify files outside `<OUT_DIR>`.**
- **Do NOT commit anything.** The dispatcher commits at batch boundaries.
- **Cloudflare → STOP at the affected pass.** Don't retry, don't burn context probing.
- **No prose in `chosen.json` files.** The pass-1/pass-2 prompts are explicit: JSON only. Prose responses crash downstream consumers.

---

## When done

Report back with a single message containing:

1. `STATE`, `actual_vintage_used`
2. Count of `proposed_urls`
3. Any `playwright_errors`
4. Full content of `result.json`

Do NOT include a narrative of your work. Just the final state — the dispatcher needs structured output for the per-state inventory the parent handoff requires.

---

## Failure modes the dispatcher should be aware of

- **Cloudflare blocking** — entire pair lost; re-canary later under different IP.
- **Wrong title pick at pass-1** — pass-2 fetches an irrelevant title page. Detectable by: pass-2 chapter URLs don't match the state's known lobbying-disclosure regime structure. The dispatcher should spot-check `proposed_urls` against the regime patterns documented in [`20260518_fetch_2015_section_bodies.md`](20260518_fetch_2015_section_bodies.md) (per-state regime notes).
- **Helper TSV empty for non-CF reasons** — Justia layout shift the patched helper doesn't anticipate. Bundle gets quarantined with `pass*_tsv_empty_unexpected`; dispatcher investigates HTML in `notes`.
- **Vintage substitution succeeded silently** — `actual_vintage_used` differs from `vintage`; downstream Phase C must thread `year_delta` and `direction` correctly into `retrieve_statute_bundle()`.

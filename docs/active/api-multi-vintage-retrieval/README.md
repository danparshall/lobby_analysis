# api-multi-vintage-retrieval — Justia statute retrieval pipeline

> ## 📬 Handoff in flight (2026-06-10)
>
> Dan's IPs got CF rate-limited mid-fan-out on 2026-06-09. The remaining 28 fresh + 2 partial-resume Method B canary dispatches for the 50-state 2025 expansion have been handed off to Suhan's agent. **If you are Suhan's agent — go to [`HANDOFF.md`](HANDOFF.md). That doc is self-contained and is your one-stop entry point.**
>
> The rest of this README is background.

**Branch home for:** the Anthropic-API-driven discovery + Playwright-driven fetch pipeline that retrieves Justia-hosted state lobbying statutes across multiple historical vintages (2010 / 2015 / 2025) for all 50 states. The substrate for multi-rubric calibration (PRI 2010, CPI 2015, Sunlight 2015, FOCAL 2024, etc.) and for the project's data-layer commitment to up-to-date lobbying disclosure infrastructure.

**Started:** 2026-05-14. Active. Coverage at last update: see [`results/`](results/) for per-session inventories.

## The two retrieval paths

### Method A — curated URL lists (`src/scoring/lobbying_statute_urls.py`)

For (state, vintage) pairs where someone has hand-curated the section URLs that constitute the state's lobby-disclosure statute body. Lookup is a dict literal; fetch is `retrieve_bundles_for_states()` → `retrieve_statute_bundle()` → write `data/statutes/<STATE>/<VINTAGE>/sections/*.txt` + `manifest.json`.

**Use Method A when:**
- An exact (state, vintage) entry exists in `LOBBYING_STATUTE_URLS`.
- A prior Method-B canary produced a `result.json` whose `proposed_urls` you've reviewed and want to promote to the curated table.

Method A is fast (~2.5s/section, single Playwright session), deterministic, and the source of truth for downstream Phase C. The curated table currently contains 6 entries (CA/NY/WI/WY/TX × 2010 / 2009; OH × 2010 + 2025) and is intentionally *not* the bottleneck — the Method B discovery pipeline produces fresh `result.json` bundles that the Phase C section-fetch driver consumes directly without round-tripping through `LOBBYING_STATUTE_URLS`.

### Method B — agent-driven URL discovery (the dispatch template)

For (state, vintage) pairs where no curated URLs exist. A general-purpose Claude Code subagent walks Justia's hierarchy via 3 passes:

1. **Pass 1** — fetch the state-year index at `https://law.justia.com/codes/<slug>/<vintage>/`, parse to TSV, select probable lobbying-disclosure title(s).
2. **Pass 2** — for each chosen title, fetch its TOC, parse to TSV, select probable lobbying chapter(s).
3. **Pass 3** — for each chosen chapter, fetch its TOC. Two cases: chapter URL IS the leaf (e.g., TX directory-leaf chapters) — add the chapter URL with `role: "core_chapter"` and skip pass-3 reasoning; OR chapter has subsections — apply pass-3 reasoning to pick section URLs.

The subagent emits a reproducibility bundle at [`results/subagent_canaries/<STATE>_<VINTAGE>/`](results/subagent_canaries/) containing raw HTML + cleaned TSV + per-pass `chosen.json` + an aggregate `result.json`. The bundle format is documented at [`results/subagent_canaries/README.md`](results/subagent_canaries/README.md).

**Use Method B when:**
- No curated entry in `LOBBYING_STATUTE_URLS`.
- A state's regime structure is unknown or has changed (e.g., a renumbering between vintages).
- You want a fresh inventory of what Justia actually hosts for a (state, vintage).

## How to add a (state, vintage) — Method B recipe

### Prerequisites

- Worktree: `.worktrees/api-vintage` (this branch).
- Venv: `.venv` populated; `PYTHONPATH=src uv run --active python -c "from scoring.justia_client import PlaywrightClient; from scoring.api_retrieval_agent import _build_justia_link_tsv" should succeed.
- `.env.local` with `ANTHROPIC_API_KEY` (the subagent runs from your Claude Code session, which inherits parent auth; no extra config needed unless you're using the script-based canary path).

### Step 1 — CF probe (free, cheapest move first)

Before any API spend, verify Cloudflare is open from your network:

```bash
cd .worktrees/api-vintage
PYTHONPATH=src uv run --active python scripts/subagent_fetch_save.py \
    /tmp/cf_probe pass1 https://law.justia.com/codes/<state-slug>/<vintage>/
```

If the TSV is non-empty and contains the state's titles, CF is open. If you see "Just a moment..." or "Performing security verification" in the HTML, CF is closed — STOP, retry later or switch surface (VPN / hotspot / different time of day).

The 2026-06-09 session found that CF appears to enforce a **per-IP cumulative-fetch rate-limit** (not pure concurrency) — even a clean probe doesn't guarantee CF will hold across an entire fan-out session. Re-probe between batches.

### Step 2 — Dispatch the Method B subagent

The dispatch prompt template is [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](plans/_handoffs/20260519_subagent_dispatch_prompt.md). Send a general-purpose Claude Code subagent (Agent tool, `subagent_type: general-purpose`) with a wrapper prompt that:

1. Names the state, slug, vintage, OUT_DIR, WORKING_DIR.
2. Points at the dispatch template for the procedure.
3. Provides a one-paragraph regime prior (which title / chapter / section range to expect). Regime priors don't have to be exact — the canary self-corrects to ground truth by reading Justia's actual TSV. But a roughly-correct prior shortens pass-1 reasoning.
4. Reiterates acceptance criteria: `playwright_errors: []`, `proposed_urls` ≥ 4, `actual_vintage_used` matches the request.

Examples of strong canary dispatches that handle structurally diverse regimes:
- [`results/subagent_canaries/AL_2025/`](results/subagent_canaries/AL_2025/) — single-body, per-section leaves
- [`results/subagent_canaries/LA_2025/`](results/subagent_canaries/LA_2025/) — two-body (Title 24 + Title 49), Wisconsin-style per-section URLs within each title
- [`results/subagent_canaries/NE_2025/`](results/subagent_canaries/NE_2025/) — unicameral flat-chapter, no title level

### Step 3 — Pace the fan-out

Per the 2026-05-18 CF-sustainability finding, **batches of 3 concurrent** historically worked. The 2026-06-09 session found this floor may have shifted lower; user directive after batch 1 tripped CF: **drop to 2-concurrent** for any subsequent fan-out and add a cooldown (~5+ min) between batches.

Each subagent costs roughly **$0.45–$0.90 at opus rates** (per the 2026-06-09 calibration on 6 canaries, avg ~82K subagent_tokens). Budget accordingly: 30 states × $0.90 = ~$27 worst case.

### Step 4 — Phase C section-body fetch

Once all `result.json` bundles exist, write a one-off Python driver (analogous to [`scripts/fetch_gap_cells_sections.py`](../../../scripts/fetch_gap_cells_sections.py)):

```python
from scoring.justia_client import PlaywrightClient
from scoring.statute_retrieval import retrieve_statute_bundle

client = PlaywrightClient(rate_limit_seconds=2.5)
for state, vintage in CELLS:
    result_json = json.loads((CANARY / f"{state}_{vintage}/result.json").read_text())
    urls = [u["url"] for u in result_json["proposed_urls"]]
    retrieve_statute_bundle(
        client, state_abbr=state, vintage_year=vintage,
        urls=urls, dest_dir=BASE / state / str(vintage),
    )
```

This writes `data/statutes/<STATE>/<VINTAGE>/sections/<filename>.txt` + `manifest.json`. Section files are **gitignored** (machine-local under `~/data/lobby_analysis/statutes/`) — only the discovery canaries + manifests + convos/results live in git.

### Step 5 — Size-sanity gate

After section fetch, verify per state:

- **Median section size ≥ 2 KB** — anything below suggests TOC-page mis-fetches (the 2026-05-27 CO 2025 bug). STOP and inspect.
- **No file < 500 B** — anything below suggests CF stub contamination or parse miss. Flag for human review.

The fetch driver should emit a summary table per state with file count, median size, and any flagged small files.

## Operational lessons (accumulated)

| Lesson | Source session | Implication |
|---|---|---|
| 3 concurrent subagents is the (historic) CF sustainability ceiling. May have shifted lower. | 2026-05-18; revised 2026-06-09 | Default 2-concurrent now; CF-probe before each batch. |
| `_build_justia_link_tsv` had 4 URL conventions; FL 2010 surfaced a 5th (flat-sibling Part page). | 2026-06-05 | Pattern not yet added to helper; surfaced as a Method-A automation gap. |
| Justia 2025 uses a year-less "current code" link convention. | 2026-05-19 (commit `28b1aab`) | Helper patched to produce year-prefixed URLs uniformly. |
| Vintage substitution can happen silently — `actual_vintage_used` ≠ requested vintage. | 2026-05-19, 2026-05-27 | Phase C must thread `year_delta` and `direction` correctly. CO 2010 historically used 2016; flagged for human review. |
| Per-IP CF rate-limit appears cumulative, not just per-batch. | 2026-06-09 | A clean probe doesn't guarantee the whole session. Network surface diversity (VPN, hotspot) or stealth-playwright may be needed for large fan-outs. |
| Regime priors don't have to be exact. | 2026-06-09 (LA, NE, VA) | The canary self-corrects by reading the actual TSV. LA's section ranges (24:50-58.1 vs 24:50-63), NE's section truncation (49-1492.01 vs 49-1492.06), and VA's chapter renumbering (Chapter 4 Article 3 vs "Chapter 4.4") were all caught by the canary. |
| Lossy bundles (pre-2026-05-18) only have URL outputs, no HTML/TSV capture. | 2026-05-18 (capture format added) | These need re-canary if a future direct-API run wants to replay pass reasoning. List at [`results/subagent_canaries/README.md`](results/subagent_canaries/README.md). |
| Median <2KB → STOP gate. | 2026-05-27 (CO TOC-page bug) | Was originally <500B; raised after CO 2025 fetched TOC pages mistaken as section bodies. |
| Cross-machine sync is manual. | All sessions | Section bodies are machine-local; pushing the branch syncs the discovery canaries + convos + results to GitHub, but not `data/statutes/`. Sync to Air / tarragon happens out-of-band. |

## Coverage status

Per-(state, vintage) inventory lives in the per-session results docs. Most recent:

- [`results/20260605_top10_statute_coverage.md`](results/20260605_top10_statute_coverage.md) — top-10 priority states × 3 vintages, 30/30 covered as of 2026-06-05
- [`results/20260527_statute_inventory.md`](results/20260527_statute_inventory.md) — 2025 cohort 3 → 15 states, 5/27
- [`results/20260609_50_state_2025_expansion_session_summary.md`](results/20260609_50_state_2025_expansion_session_summary.md) — 50-state 2025 expansion mid-progress (16 + 4 clean + 2 partial; 28 remaining)

Aggregate inventory across sessions is not yet maintained as a single doc; recommended future work.

## Related infrastructure

- Helper script: [`scripts/subagent_fetch_save.py`](../../../scripts/subagent_fetch_save.py) — Playwright fetch + TSV building for one pass.
- Dispatch prompt: [`plans/_handoffs/20260519_subagent_dispatch_prompt.md`](plans/_handoffs/20260519_subagent_dispatch_prompt.md) — the canonical Method B procedure.
- Bundle schema: [`results/subagent_canaries/README.md`](results/subagent_canaries/README.md).
- Pass-1 reasoning template: `src/scoring/api_seed_discovery_pass1_prompt.md`.
- Pass-2 / Pass-3 reasoning template: `src/scoring/api_seed_discovery_pass2_prompt.md`.
- Section-body fetch driver pattern: [`scripts/fetch_gap_cells_sections.py`](../../../scripts/fetch_gap_cells_sections.py) (2026-06-05 example).
- Sister branches: `statute-retrieval` (archived; Method A pioneer), `phase-c-projection-tdd` (archived; produced the vintage-selection reference), `extraction-harness-brainstorm` (archived; the downstream extraction harness this retrieval feeds).

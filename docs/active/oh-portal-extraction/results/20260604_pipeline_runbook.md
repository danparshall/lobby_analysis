# OH portal pipeline — runbook

**As of 2026-06-04.** The OH disclosure grab is a reproducible, committed pipeline —
not a pile of one-off scripts. Three composable stages, each a module CLI under
`src/lobby_analysis/oh_portal/`. Run from the repo (or worktree) root.

Prereqs: `uv sync --extra dev`; `ANTHROPIC_API_KEY` in `.env.local` (the
extraction stages self-load it — no `export` needed). Discovery needs **no** key.

## Stage 1 — discover (scrape the report_id universe, agent axis)

No LLM, no key. Caches raw responses under `data/oh_portal/discover/` (resumable).

```bash
# Targeted (cheap; validation or a known agent):
python -m lobby_analysis.oh_portal.discover \
    --years 2025,2026 --agent-ids 5272 \
    --out data/oh_portal/discover/recent.tsv

# Full crawl (all ~1,502 agents -> all recent AERs). Heavier; see "scale" below.
python -m lobby_analysis.oh_portal.discover \
    --years 2025,2026 --all \
    --out data/oh_portal/discover/recent.tsv
```

Output TSV columns: `report_id, agent, agent_id, employer, year, reporting_period,
form_type, aer_url`. The `employer` column captures the (agent, employer) tuple
straight from the index — independent of the detail-page extraction.

## Stage 2 — extract (fetch + LLM-parse each filing)

Reads the Stage-1 TSV directly (pulls the `aer_url` column). Idempotent: a
`report_id` already extracted is skipped (resume). Self-loads the API key.

```bash
python -m lobby_analysis.oh_portal.batch --file data/oh_portal/discover/recent.tsv
```

Per filing: writes `data/oh_portal/extracted/{report_id}/{run_id}/filing.json`
(a `LobbyingFiling`) + `extraction_run.json`. One filing's failure is isolated;
the batch finishes and reports `N extracted / M skipped / K failed`.

Single filing (debug / one-off): `python -m lobby_analysis.oh_portal <AER_URL>`.

## Stage 3 — (not built) load/aggregate

`filing.json` records are the current deliverable. Aggregation into the v2.2 SMR
practical-axis cells / a queryable store is future work (see RESEARCH_ARC Prong 2).

## Scale / etiquette notes

- One agent (Aichele) has ~2,213 lifetime forms; filtered to 2025–2026 → 139 AERs.
  A full `--all` recent crawl is **thousands** of AERs → thousands of LLM calls.
  Discover first (cheap), review the TSV, then decide how much to extract.
- `discover --all` is ~3,000 lightweight GETs (roster + per-surname search +
  per-agent FormsFiled). Each *live* request is throttled by
  `fetch.REQUEST_DELAY_SECONDS` (0.5 s; cache hits are not throttled), so a cold
  full crawl runs ~25 min. The crawler identifies honestly via
  `fetch.USER_AGENT` (`lobby_analysis-research/...`) — no browser spoofing.
- **robots.txt / ToS (checked 2026-06-04):** `https://www2.jlec-olig.state.oh.us/robots.txt`
  returns 404 (no crawl policy published); OLAC exposes no Terms of Use (landing
  page carries only a `©` notice). The data is Ohio statutory public record
  (ORC §§101.70+) published for public access. Re-check before any future bulk run.
- Everything under `data/` is gitignored (raw HTML, extracted JSON, discover
  cache). The pipeline regenerates it; git carries only code + docs.
```

# OH schema retarget + (B') discovery + reproducible pipeline

**Date:** 2026-06-04 (continuous session from 2026-06-03)
**Branch:** `oh-portal-aprime-batch` (forked off `oh-portal-extraction`)

## Summary

Continuation of the 2026-06-03 session (see `20260603_oh_aprime_run_and_batch.md`).
Three threads closed out today: (1) a schema-version scare that turned out to be a
category error, (2) the (B') filing-ID enumeration gap — the thing that stood
between "batch over 3 known seeds" and "batch over all of OH" — now solved
agent-axis, and (3) wiring the stages into a single reproducible pipeline that
runs from a clean shell with no wrapper scripts.

The session also course-corrected on process: an agent-introduced "v1.4 schema
bump, loop in Gowrav" framing was dropped once the evidence showed the schema was
already current and adequate. Lesson logged: don't propagate inherited
terminology (Amina's "v1.4") without reconciling it against the current repo.

## Topics Explored

- **"v1.4" vs "v2.2" reconciliation.** Dan flagged that the SMR is on v2.2, so why
  was the agent saying v1.4? Investigation: the v1→v2 transition was the
  **SMR/compendium** schema (Prong 1, statute requirements). The OH parser targets
  **`LobbyingFiling`** (Prong 2, the disclosure record) — a *different* model on an
  incremental version line. Two different schemas, conflated in the inherited docs.
- **"Amina's code is ancient" — tested, false.** `git merge-base` puts her branch
  base at 2026-05-18 (postdates Compendium 2.0/v2, 2026-05-14). The only delta to
  `LobbyingFiling` on main since was **two optional fields** (`total_hours_communicating`,
  `total_hours_other`). Surgically pulled them in; the parser now targets current main.
- **OLAC enumeration probe (read-only).** Mapped the public Reports area and the
  agent-axis discovery chain end to end.
- **Built `discover.py`** (TDD) + wired the pipeline + closed the API-key seam.

## Provisional Findings

- **Schema is current and adequate; no v1.4 needed.** Re-extraction showed the
  employer *can* land in `filer_organization` (it did on the second run, was null on
  the first) — so the earlier "employer dropped, schema gap" is **stochastic
  brief-consistency, not a schema limitation**. A one-line brief instruction would
  make it deterministic; no model/schema change.
- **Enumeration solved, agent-axis.** `Agents/List` (CSV roster, 1,502 agents) →
  `Agents/FormsFiledSearch?LastName=` (agent IDs; a surname can map to several) →
  `Agents/{id}/FormsFiled` (full filing history table: Year | Employer | Type | …
  | Period | View→/olac/AERs/{id}/View). Filter `Type==AER` & recent years → the AER
  universe. Verified: agent 5272 = Nathan Aichele, 139 recent (2025–26) AERs of 2,213
  lifetime forms, all 3 seeds present with correct employers.
- **The discovery index carries the employer per filing** — captures (agent,
  employer) structurally, independent of the (stochastic) detail-page extraction.
- **The OLAC "timeout" (from 2026-06-03) is confirmed an outside-US issue** — all of
  today's ~dozen probe + discovery fetches worked first try from DC.

## Decisions Made

- **Fork's parser retargeted to current `LobbyingFiling`** (2 hours-fields). Committed.
- **Dropped the v1.4 / Gowrav-review ceremony** — schema accepted as-is (Dan).
- **(B') is agent-axis, recent ≤2 years** (default `--years 2025,2026`) — Dan's scope.
- **Pipeline is the deliverable, not the files** (Dan) → made the stages compose:
  `discover --out x.tsv` → `batch --file x.tsv`; CLIs self-load the API key. Runbook
  committed so it's reproducible-by-instruction.
- **Full `--all` crawl deferred to a fresh agent** (Dan will drive) — pending a
  robots.txt/ToS check and a model-cost decision (opus vs sonnet for bulk).

## Results

- `results/20260604_pipeline_runbook.md` — the runnable 3-stage pipeline.
- `results/20260507_oh_a_prime_validation.md` — (A') validation (filled 2026-06-03).
- New code: `discover.py`, `env_local.py`; `batch.py`/`__main__.py` pipeline wiring;
  `tests/test_oh_portal_discover.py` (+ 2 batch TSV tests). 17 discover+batch tests
  pass; full suite 365 / 3 pre-existing data-only fails.

## Open Questions / Next Steps (for the fresh agent doing the crawl)

1. **Check `robots.txt` / ToS** before `discover --all` (~3,000 GETs).
2. **Run `discover --all --years 2025,2026 --out recent.tsv`** → get the real AER count.
3. **Model-cost decision for bulk extraction:** opus-4-7 hit 93.5% on this simple
   form; sonnet would likely match at a fraction of the cost over thousands of filings.
   Consider parameterizing `MODEL_ID` (currently hardcoded in `extract.py`).
4. **Surname-search coverage:** verify common surnames aren't capped/paginated (the
   "no silent caps" concern) during the full crawl.
5. **Brief tweak (optional):** pin the employer into `filer_organization` and set
   `is_itemized=false` on Non-Itemized-only filings — both prompt-level.
6. **Stage 3 (future):** aggregate `filing.json` → v2.2 SMR practical-axis cells.

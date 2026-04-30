# Research Log: oh-portal-extraction

Created: 2026-04-30
Owner: Amina Rakhimbergenova
Track: B (portal scraping → `LobbyingFiling`)
Test state: Ohio

## Purpose

Extract actual lobbying disclosures from the Ohio state portal into the `LobbyingFiling` model (`src/lobby_analysis/models/filings.py`). Ohio is the team-wide test state for shaking out the end-to-end pipeline before broadening to other priority states.

This is the data-acquisition counterpart to Dan's `statute-retrieval` branch (Track A). The two tracks share a target schema (data model v1.1) but operate independently.

## Sessions

(Newest entries first.)

### 2026-04-30 — Branch kickoff

- Cut `oh-portal-extraction` worktree off `main` (eb849ca).
- Seeded `docs/active/oh-portal-extraction/{convos,plans,results}/` and this log.
- Baseline check: tests passing, environment clean.
- Next: brainstorming session on what the OH portal looks like (existing snapshot in `docs/historical/pri-2026-rescore/` is the starting artifact). Decide scrape strategy before writing any extraction code.

## Plans

(Plans are added under `plans/` and listed here once written.)

_None yet._

## Convos

(Convo summaries land under `convos/YYYYMMDD_topic.md` and are listed here.)

_None yet._

## Open questions

- What tier is the OH snapshot under `docs/historical/pri-2026-rescore/` — clean / partial WAF-SPA / near-empty? Determines whether the existing capture is reusable or we need a fresh fetch.
- Does OH publish bulk download or are we PDF/HTML-scraping per filing?
- What's the right `ExtractionCapability` (`src/lobby_analysis/models/pipeline.py`) shape for OH — populated as a side-effect of the pipeline, or curated up-front?

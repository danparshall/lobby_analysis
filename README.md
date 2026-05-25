# lobby_analysis

**LobbyView, for all 50 states.**

`lobby_analysis` is open-source infrastructure to make state-level lobbying disclosure data usable as an up-to-date input for democracy measurement — filling the state-side gap that LobbyView (MIT, federal-LDA only) and OpenSecrets (federal-only / 31-state summary scorecard) leave open.

Group project of the **Corda Democracy Fellowship**. Project lead: Suhan Kacholia (Co-Founder, Analogy Group). Multiple fellows contribute to this repo.

Weekly updates for Corda are mirrored to [this shared Google Doc](https://docs.google.com/document/d/1vMHOV2zPcYTA0cKBiHlpzqNBMasTZcI8uScxASJm2fU/edit?usp=sharing); canonical versions live in [`docs/weekly_updates/`](docs/weekly_updates/).

## Why this exists

Policy capture — when private interests systematically shape government decisions at the expense of the public — is one of the clearest indicators of democratic backsliding. At the US state level, lobbying disclosure data is the most direct signal of who is trying to influence policy and how much they're spending to do it.

That data is hard to use today. State portals bury it in inconsistent formats, PDFs, and clunky search interfaces. The best existing aggregators (OpenSecrets, FollowTheMoney) cover only a subset of states and only summary totals — without the enrichment that makes it actionable: which specific bills were lobbied on, what positions were taken, which officials received gifts, how the same entities operate across states and at the federal level.

The research literature on state lobbying regulation responds to this gap by building scorecards (PRI 2010, CPI Hired Guns 2007, Sunlight 2015, OpenSecrets 2022) and academic measures (Opheim 1991, Newmark 2005/2017) — each with its own atomization, weighting, and category structure. Newmark 2017 found that two of the most-cited disclosure measures (PRI's and CPI's) correlate at **r = 0.04**: they purport to measure the same thing and are essentially unrelated. This is not a measurement disagreement to arbitrate; it is evidence that *no single rubric should be privileged* as the project's foundation.

## Research question

Operationally, the project's central open question is:

**Can frontier LLMs read a state's lobbying statute and produce a reliable, evidence-cited record of what that state's disclosure regime requires?**

The answer determines whether the data layer below can be populated at all. We attempted a typed-cell answer first — Compendium 2.0, a 181-row schema with cell types pinned in advance — and ran the first state-level pilot against it (OH 2025) in May 2026. Pilot results show that frontier LLMs *can* read the statute (high cross-vintage stability, low cost, no hallucinated citations), but the typed-cell schema *cannot yet faithfully represent what the statute actually says* — most visibly on qualitative-trigger states like OH, where the lobbyist definition is non-numeric ("main purpose" rather than a dollar floor) and the numeric threshold cells force a lossy encoding.

We're therefore pivoting to **gather-first**: collect per-(state, vintage, question) answers in a flexible intermediate format (JSON: agent's freeform answer + statute citation + confidence), then design the **v2.2** typed schema based on what statutes actually say. **v2.1** — the current typed schema with column-rename refinements (`compendium/disclosure_side_compendium_items_v2.tsv`) — remains the immediate reference; v2.2 is the next compendium generation, post-data.

Prong 1 (statute → SMR) is **paused as of 2026-05-24** after this first round of evidence — see `docs/RESEARCH_ARC.md` for the three-prong framing and `docs/historical/{phase-c-projection-tdd, extraction-harness-brainstorm, oh-statute-retrieval}/` for the work that produced the evidence. Prong 2 (portal extraction) and Prong 3 (display) are unaffected.

## What we deliver

A common, rubric-agnostic **data layer** — a structured per-state record of what each state's lobbying-disclosure regime requires and what its public-facing data actually contains — built so that researchers, activists, and journalists can apply their *own* weights, definitions, and rankings on top of it.

Concretely:

- **A field compendium.** A union of items drawn from the major published rubrics and frameworks, atomized to the granularity of a single observable about a state's lobbying-disclosure regime. Compendium 2.0 (181 cell-typed rows, frozen 2026-05-13, merged to main 2026-05-14) lives at `compendium/disclosure_side_compendium_items_v2.tsv`; see `compendium/README.md`. Built on the archived `compendium-source-extracts` branch from 9 source rubrics treated on even footing (PRI 2010, CPI 2015, CPI Hired Guns 2007, Sunlight 2015, Newmark 2005/2017, Opheim 1991, FOCAL 2024, OpenSecrets 2022, plus LobbyView 2018/2025 schema-coverage).
- **A per-state record (`StateMasterRecord`) keyed to the compendium.** For each state, what does the statute *require* (legal availability), and what does the state portal *actually expose* (practical availability). The schema lives in `src/lobby_analysis/models/`.
- **Pull pipelines.** LLM-driven extraction of structured filings (lobbyist registrations, expenditure reports, contact logs) from state portals into a uniform schema. Knowing what *should* exist per the compendium makes downstream extraction substantially more tractable.
- **Schema compatibility with Popolo / Open Civic Data.** Entity-side (lobbyists, clients, public officials, posts, memberships) follows the Popolo conventions adopted by Open States. Filing-side uses a complementary OCD-style `Disclosures` schema since Popolo does not cover filings.

We do **not** publish a "Corda Rubric" or composite ranking. Researchers can re-aggregate the data layer into PRI-style scorecards, FOCAL-style transparency assessments, or any other framing they prefer.

## Project state

- **Active branches** and current focus: see `STATUS.md`.
- **Compendium 2.0 landed 2026-05-14** as merge commit `cac1469` on main and was promoted to the repo-level `compendium/` path by `compendium-v2-promote` later the same day. 181 cell-typed rows across legal/practical axes. Three parallel successor branches worked off this contract — all three **merged and archived 2026-05-24** as part of the Prong 1 pause + gather-first pivot: `oh-statute-retrieval` (stub — multi-vintage OH bundles + HG 2007 ground-truth retrieval, blocked on vintage findings), `extraction-harness-brainstorm` (Tier-0 + Tier-1 + Tier-2 harness, surfaced the structural finding that drove the pivot), `phase-c-projection-tdd` (5 of 8 rubric projections shipped + 2 of 4 FOCAL plans; HG 2007 and Opheim 1991 deferred on vintage).
- **What v1 is and is not.** Compendium 1 (`compendium/_deprecated/v1/disclosure_items.csv`, 141 rows) and the v1.1 Pydantic models (`src/lobby_analysis/models/` — `CompendiumItem`, `FieldRequirement` with availability axes, `MatrixCell`, `ExtractionCapability`, generic `FrameworkReference`) are the working scaffold that produced the `statute-retrieval` MVP. The Pydantic *abstractions* (FrameworkReference, availability axes, the SMR row shape) carry forward; the Literal enumerations (`registration_role: PRI A1–A11`, `reporting_frequency: PRI E1h/E2h`) and named `de_minimis_*` SMR fields will be rebuilt for v2 alongside the extraction-harness work. The deprecated v1 loader (`load_v1_compendium_deprecated()`) remains functional; the PRI-projection-MVP code (`cmd_build_smr`, `smr_projection`) was retired by `phase-c-projection-tdd` on 2026-05-14 — `smr_projection.py` lives at `src/scoring/_deprecated/smr_projection.py` (preserved, not deleted) and its tests at `tests/_deprecated/test_smr_projection.py` (excluded from default pytest collection via `norecursedirs`).
- **Initial state coverage:** field rollout starts with 5–8 priority states selected for data quality and political significance, with the architecture built to support all 50 over time.

## Repo layout

This repo follows the research-first documentation workflow. See `CLAUDE.md` for the full description.

- `STATUS.md` — current focus, branch inventory, recent sessions
- `PAPER_INDEX.md` / `PAPER_SUMMARIES.md` — literature index and key findings
- `papers/` — source PDFs; `papers/text/` — extracted text for search
- `compendium/` — Compendium 2.0 source of truth (`disclosure_side_compendium_items_v2.tsv`); `compendium/_deprecated/v1/` retains v1 artifacts for traceability
- `docs/active/<branch>/` — active research lines (convos, plans, results, RESEARCH_LOG)
- `docs/historical/<branch>/` — archived research lines (see STATUS.md table)
- `docs/LANDSCAPE.md` — fellow-facing landscape report (positioning vs LobbyView / OpenSecrets / Sunlight / FOCAL / CSG)


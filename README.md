# lobby_analysis

**LobbyView, for all 50 states.**

`lobby_analysis` is open-source infrastructure to make state-level lobbying disclosure data usable as an up-to-date input for democracy measurement — filling the state-side gap that LobbyView (MIT, federal-LDA only) and OpenSecrets (federal-only / 31-state summary scorecard) leave open.

Group project of the **Corda Democracy Fellowship**. Project lead: Suhan Kacholia (Co-Founder, Analogy Group). Multiple fellows contribute to this repo.

Weekly updates for Corda are mirrored to [this shared Google Doc](https://docs.google.com/document/d/1vMHOV2zPcYTA0cKBiHlpzqNBMasTZcI8uScxASJm2fU/edit?usp=sharing); canonical versions live in [`docs/weekly_updates/`](docs/weekly_updates/).

## Why this exists

Policy capture — when private interests systematically shape government decisions at the expense of the public — is one of the clearest indicators of democratic backsliding. At the US state level, lobbying disclosure data is the most direct signal of who is trying to influence policy and how much they're spending to do it.

That data is hard to use today. State portals bury it in inconsistent formats, PDFs, and clunky search interfaces. The best existing aggregators (OpenSecrets, FollowTheMoney) cover only a subset of states and only summary totals — without the enrichment that makes it actionable: which specific bills were lobbied on, what positions were taken, which officials received gifts, how the same entities operate across states and at the federal level.

The research literature on state lobbying regulation responds to this gap by building scorecards (PRI 2010, CPI Hired Guns 2007, Sunlight 2015, OpenSecrets 2022) and academic measures (Opheim 1991, Newmark 2005/2017) — each with its own atomization, weighting, and category structure. Newmark 2017 found that two of the most-cited disclosure measures (PRI's and CPI's) correlate at **r = 0.04**: they purport to measure the same thing and are essentially unrelated. This is not a measurement disagreement to arbitrate; it is evidence that *no single rubric should be privileged* as the project's foundation.

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
- **Compendium 2.0 landed 2026-05-14** as merge commit `cac1469` on main and was promoted to the repo-level `compendium/` path by `compendium-v2-promote` later the same day. 181 cell-typed rows across legal/practical axes. Three parallel successor branches work off this contract: `oh-statute-retrieval` (multi-vintage OH bundles for extraction validation), `extraction-harness-brainstorm` (the single extraction pipeline + v2 Pydantic models), `phase-c-projection-tdd` (per-rubric projection functions in locked order CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017/2005 → Opheim 1991 → HG 2007 → FOCAL 2024).
- **What v1 is and is not.** Compendium 1 (`compendium/_deprecated/v1/disclosure_items.csv`, 141 rows) and the v1.1 Pydantic models (`src/lobby_analysis/models/` — `CompendiumItem`, `FieldRequirement` with availability axes, `MatrixCell`, `ExtractionCapability`, generic `FrameworkReference`) are the working scaffold that produced the `statute-retrieval` MVP. The Pydantic *abstractions* (FrameworkReference, availability axes, the SMR row shape) carry forward; the Literal enumerations (`registration_role: PRI A1–A11`, `reporting_frequency: PRI E1h/E2h`) and named `de_minimis_*` SMR fields will be rebuilt for v2 alongside the extraction-harness work. The deprecated v1 loader (`load_v1_compendium_deprecated()`) and PRI-projection-MVP code (`cmd_build_smr`, `smr_projection`) remain functional until `phase-c-projection-tdd` retires them.
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


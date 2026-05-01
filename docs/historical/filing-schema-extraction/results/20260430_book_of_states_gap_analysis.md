<!-- Generated during: convos/20260430_compendium_expansion_v2_scoping.md -->

# Book of States Gap Analysis vs Current Compendium

**Date:** 2026-04-30
**Compendium version at time of analysis:** 118 rows (statute-retrieval branch artifact, post-Stage-A walkthrough of PRI 2010 ∪ FOCAL 2024 ∪ Sunlight 2015)
**Purpose:** Identify what the historical *Book of the States* lobbying-regulation data covered that the current compendium does not, and decide what should and shouldn't expand the compendium given the project's data-extraction scope.

## Background

*The Book of the States* (Council of State Governments, annual since 1935) carried a lobbying-regulation data section through ~2005, when CSG dropped it (per Newmark 2017's reasoning for shifting to primary-source statute review for his 2015 index). Two academic measures were derived directly from it:

- **Opheim 1991** — 22 binary items, 3 dimensions: definitions (7), disclosure (8), oversight/enforcement (7). R²=0.58 against state political-culture predictors.
- **Newmark 2005** — 17 binary items + 1–4 penalty supplement, 6 time periods (1990–2003). r=0.84 against Opheim 1991. Mean state regulation rose 6.54 → 10.34 (1990 → 2003).

This gives us a concrete inventory of what BoS-era disclosure-regulation analysis tracked.

## Content cluster comparison

| Cluster | Book-of-States content | In current 118-row compendium? | In scope for this project? |
|---|---|---|---|
| **Definitions** (7 trigger criteria) | legislative-lobbying coverage, administrative-agency coverage, elected officials as lobbyists, public employees as lobbyists, compensation standard, expenditure standard, time standard *in the definition of lobbying* | Partial — PRI A-series covers categories of person (lobbyist / volunteer / in-house) but not the trigger-threshold criteria inside the statutory definition itself | **Borderline-in.** Determines who must file. Decision: include as new `domain="definitions"` rows. |
| **Prohibitions** | campaign contributions any time, campaign contributions during session, expenditure / gift caps, solicitation by officials, contingent fees, revolving door / cooling-off | None | **Out of scope.** Statutory rules; no filing carries them as data fields. |
| **Disclosure** (6 types + frequency) | influenced action, expenditures benefiting officials, compensation by employer, total compensation, expenditure categories, total expenditures, reporting cadence | Yes — covered by PRI E-series + FOCAL + Sunlight at finer granularity than Newmark/Opheim | **In.** This is exactly what the compendium models. Walking Newmark/Opheim mostly produces cross-refs on existing rows, not new rows. |
| **Penalties** (Newmark add-on) | felony classification, max fine, debarment, jail time | None | **Out of scope.** No filing. |

## The reframing call

User reframe (verbatim): *"we'll be extracting the data for our consumers, but clearly we can only extract data which is required to be disclosed."*

This collapses what initially looked like a major schema-expansion question (do we need new domains for prohibitions / penalties / enforcement?) into a much narrower curation question (do the unwalked rubrics surface new disclosure-side rows?). Specifically:

- The pipeline reads filings, not statute-text-as-output. A row in the compendium represents data the project *extracts from a filing*. Prohibitions don't generate filings; they constrain behavior outside the disclosure record.
- The downstream consumer (academic / activist / journalist) querying the project's database is asking "what did entity X disclose," "how much did they spend," "on which bills" — not "what is OH's gift cap?" The latter is in `LANDSCAPE.md` territory or a separate statutory-reference document, not in the compendium.

## Implications for compendium expansion

Walking the 5 unwalked rubrics (Opheim 1991, Newmark 2005, Newmark 2017, CPI Hired Guns 2007, OpenSecrets 2022) against the disclosure-only filter:

- Most items in Newmark 2005 / Opheim 1991 fold into existing PRI/FOCAL/Sunlight rows via cross-refs. Their "disclosure" cluster is coarser than PRI E-series.
- Their **prohibitions** items are skipped entirely (~25–30% of items across both). Recorded in `framework_dedup_map.csv` with `target_expression="OUT_OF_SCOPE"` and exclusion reason in `notes`.
- Their **definitions** items become new `domain="definitions"` rows (the borderline call) — possibly 5–7 new rows.
- Newmark 2017's primary-source review items are most likely to surface unexpected disclosure rows (it post-dates Sunlight 2015 + PRI 2010 + Opheim/Newmark 2005, has primary-source vintage).
- CPI Hired Guns 2007's 48 questions span 8 categories including Public Access (20 pts) and Enforcement (15 pts) — Public Access is portal-side (folds into existing accessibility rows); Enforcement is mostly out-of-scope (audit cadence, etc.).
- OpenSecrets 2022 is the recent successor to Sunlight 2015; mostly overlaps but at finer granularity in places.

## Quantitative estimate

- Items walked across 5 rubrics: ~125 atomic items total (Opheim 22, Newmark 2005 17, Newmark 2017 19, CPI 48, OpenSecrets ~20).
- Estimated dispositions:
  - **EXISTS** (fold into existing row, add cross-ref): ~60% (~75 items)
  - **OUT_OF_SCOPE** (prohibition/penalty/enforcement/revolving-door): ~25% (~30 items)
  - **NEW** (new compendium row): ~10–15% (~12–20 items)
  - **MERGE** (rubric coarser than compendium, cross-refs added to multiple rows): ~5% (~5 items)
- Net compendium growth: 118 → ~130–140 rows (10–20% growth, mostly Newmark 2017 + CPI + a few definitions rows).

These are estimates from skim, not curation. Actual numbers will fall out of the audit walkthrough.

## Out-of-scope items (illustrative, not exhaustive — the audit will produce the full list)

These are the kinds of items the audit will exclude from the compendium and record in the dedup map's exclusion section, so they're never re-litigated:

- "Campaign contributions banned during legislative session" (Newmark 2005, Opheim 1991) — prohibition
- "Solicitation by officials banned" (Newmark 2005) — prohibition
- "Felony class for violations" (Newmark 2005 penalty supplement) — penalty
- "Maximum fine amount" (Newmark 2005, CPI 2007) — penalty
- "Agency conducts audits" (CPI 2007 Enforcement category) — enforcement metric, not filing data
- "Two-year cooling-off period for legislators-turned-lobbyists" (CPI 2007 Revolving Door) — restriction, not filing data (unless the state requires post-employment disclosure filings, which would be in scope)
- "Lobbyist registration deadline length in days" (Opheim 1991) — statute structural feature, not a filing field

## Why this analysis exists as a saved artifact

User context (verbatim): *"my laptop hard drive crashed and I lost a bunch of data."*

Without preserved provenance, the disclosure-only scoping reframe gets re-derived in every future session that hits the prohibitions / penalties question. This file pins the reasoning so the next agent can read it instead of asking "wait, why aren't gift caps in the compendium?" The final audit report (`docs/COMPENDIUM_AUDIT.md`, deliverable of `plans/20260430_compendium_expansion_v2.md`) carries the full curation-time decision log; this file is the upstream "why disclosure-only" rationale.

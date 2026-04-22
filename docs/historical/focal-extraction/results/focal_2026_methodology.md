# FOCAL 2026 Scoring Rubric — Operationalization Methodology

**Companion to:** `focal_2026_scoring_rubric.csv`
**Input:** `focal_2024_indicators.csv` (verbatim extraction from Lacy-Nichols et al. 2024 Table 3)
**Date:** 2026-04-14
**Branch:** `focal-extraction`

## Purpose

Convert FOCAL's 50 verbatim indicators into a machine-applicable scoring rubric with explicit evidence criteria and scoring guidance. Parallel to PRI's `pri_2026_accessibility_rubric.csv` / `pri_2026_disclosure_law_rubric.csv` so both rubrics share the same column schema and can be scored against the same snapshot corpus in a unified pipeline.

**Scope:** US-state application. Original Westminster/country-level language adapted where necessary; original verbatim wording preserved in `focal_2024_indicators.csv` for audit lineage.

## Count reconciliation

- Input: 50 verbatim indicators.
- Output: **54 scoring rows** (50 − 1 compound + 5 decomposed = 54).
- Source breakdown:
  - `focal_2024_verbatim`: 43 indicators carried with no modification
  - `focal_2024_operationalized`: 6 indicators with operationalized wording (Westminster role translation; ministerial-diary → executive-calendar rename; timeliness threshold made explicit)
  - `focal_2024_decomposed`: 5 sub-indicators replacing FOCAL's compound indicator 3.3
- Per-category: Scope 4 / Timeliness 3 / Openness 13 / Descriptors 6 / Revolving door 2 / Relationships 4 / Financials 11 / Contact log 11 = 54.

## Schema

Matches PRI's rubric schema for pipeline parity:

| Column | Purpose |
|---|---|
| `indicator_id` | Stable ID. Decimal format `category.N` (e.g., `1.1`, `3.3a`). |
| `category` | One of FOCAL's 8 categories. |
| `indicator_text` | Locked scoring question (post-operationalization). |
| `data_type` | `binary` for all 54 rows. |
| `source` | `focal_2024_verbatim` / `focal_2024_operationalized` / `focal_2024_decomposed`. |
| `scoring_direction` | `normal` (higher = more transparent) for all 54 rows. |
| `scoring_guidance` | Explicit evidence surfaces + score-1 vs. score-0 criteria for the LLM scorer. |
| `notes` | Optional — rationale, caveats, cross-references. |

## Operationalization decisions

### 1. Scoring scale: binary (0/1)

Chosen for cross-rubric comparability with PRI, which also uses binary item scoring. Ordinal scales were considered but add adjudication complexity during collaborator review without strong corresponding signal. Aggregates are the sum of items scored 1.

### 2. Compound indicator 3.3 decomposed into 3.3a–3.3e

FOCAL 3.3 ("Available without registration, free to access, open license, non-proprietary format, machine readable") is 5 distinct conditions compressed into one indicator. Scored as a single yes/no it would suppress cross-state variance; most states satisfy some but not all sub-conditions. Decomposition:

- 3.3a: no user registration required for basic access
- 3.3b: free of charge
- 3.3c: open license
- 3.3d: non-proprietary format
- 3.3e: machine-readable

Original FOCAL 3.3 text preserved in `focal_2024_indicators.csv`. Lineage column (`source = focal_2024_decomposed`) on all 5 rows.

### 3. Ministerial diaries → executive calendar disclosures (indicators 2.3, 3.2)

FOCAL's "ministerial diary" is a UK/Australia concept; US-state analog is executive calendar or meeting-log disclosure. Renamed in the locked text to "executive calendar / meeting-log disclosures" while preserving the indicator concept. Most US states have no equivalent mechanism — scoring 0 for them is informative, not a defect.

### 4. Timeliness thresholds made explicit (indicators 2.1, 2.2, 2.3)

FOCAL's original text says "close to real time (eg, daily)" and "monthly (or more frequently)" depending on the indicator. For scoring, "at least monthly" is used as a clean-cut threshold across all three. Rationale: sits between the International Standards "minimum quarterly, ideally close to real-time" anchors Lacy-Nichols cites; monthly filing cadence is the practical ceiling for most US state systems.

### 5. Westminster role translation for indicator 1.3

Original text enumerates "Ministers, Deputy Ministers, members of parliament, Director-Generals and senior officials" — not US-state vocabulary. Mapping baked into `scoring_guidance`:

| FOCAL term | US-state translation |
|---|---|
| Ministers / Deputy Ministers | Governor + lt. governor + cabinet secretaries |
| Members of parliament | State legislators |
| Director-Generals / senior officials | Agency heads and deputy heads |
| Staff | Legislative staff + gubernatorial staff |

Score 1 if state's definition covers at least 3 of: legislators, executive-branch officials, agency heads, staff.

### 6. Financial threshold in indicator 1.2 pinned to federal LDA benchmark

FOCAL indicator 1.2 ("no or low financial or time threshold") requires a concrete threshold to score against. Chose federal LDA's $3,500 quarterly income / 20% time threshold as the benchmark (well-known, defensible, externally anchored). States with a threshold at or below the federal benchmark cast at least as wide a net as federal law and score 1; states with higher thresholds score 0 (and the actual threshold is recorded in notes).

An empirical "median across 50 states" alternative was considered and rejected: scoring a state as "low" relative to other states is circular (moves the goalposts with every state added).

### 7. Business entity identifier for indicator 4.4 (Company registration number)

FOCAL's original "company registration number" is a UK concept. US-state translation accepts either the state Secretary-of-State business entity ID OR the federal EIN. Either satisfies the indicator.

## What was NOT operationalized (preserved as open questions for the scoring pilot)

- **Indicator 1.1 threshold for "multiple lobbyist types."** Pinned at "at least 3 of 5 enumerated types" — but the pilot (CA/CO/WY) should stress-test whether this threshold produces meaningful variance or is trivially satisfied.
- **Indicator 3.5 (simultaneous sorting) on SPA-only portals.** For ~10 states the public search UI is SPA-rendered and uninspectable from curl snapshots. Flag for Playwright supplement rather than null-score; scoring guidance instructs scorer to mark `unable_to_evaluate: true` if the captured evidence is a SPA shell.
- **Contact log category 8 (all 11 indicators).** Auto-scores 0 for states lacking a mechanism. For the minority with partial mechanisms (executive-calendar-adjacent disclosures), scoring may require case-by-case adjudication during pilot review.

## Explicitly deferred (downstream of scoring)

- **PRI-FOCAL composite design.** Per the 2026-04-13 project decision, composition is a collaborator review task after both rubrics produce 50-state CSVs. No pre-scoring reconciliation.
- **Evidence verification layer** ("does the portal actually populate field X in practice?"). Applies to schema-view indicators across both rubrics; requires actual record fetching. Not in scope for first-pass scoring.

## Lineage guarantee

Every row's `source` column and `notes` column together allow reconstruction of what changed from FOCAL's original text. `focal_2024_verbatim` rows are identical in meaning to Lacy-Nichols Table 3 wording. `focal_2024_operationalized` rows have original text preserved in `focal_2024_indicators.csv`. `focal_2024_decomposed` rows (5 sub-indicators replacing 3.3) are all tagged to FOCAL's original 3.3 and the decomposition is documented here in §2.

## For the scoring pipeline

- Input: `focal_2026_scoring_rubric.csv` (this rubric).
- Evidence: `data/portal_snapshots/<STATE>/<DATE>/` + manifest.json.
- Output schema: one row per `(state, indicator_id)` with `score`, `evidence_quote_or_url`, `source_artifact`, `confidence`, `unable_to_evaluate` flag, `notes`.
- No compositing with PRI at scoring time. Output CSV is standalone; joins to PRI output happen in the deliverable-synthesis phase under collaborator direction.

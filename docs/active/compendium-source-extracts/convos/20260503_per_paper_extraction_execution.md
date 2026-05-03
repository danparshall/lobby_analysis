# 2026-05-03 — Per-paper extraction execution

**Branch:** `compendium-source-extracts`
**Status:** Closed (extractions complete; user review pending)
**Originating plan:** [`plans/20260502_per_paper_source_extraction.md`](../plans/20260502_per_paper_source_extraction.md)
**Originating convo:** [`convos/20260502_pm_compendium_rebuild_pivot.md`](20260502_pm_compendium_rebuild_pivot.md)

## Summary

Executed the per-paper extraction plan. User approved the plan at session start with several modifications: (1) **no template-first sequencing** — all papers extracted independently, format review *after* user has seen all outputs; (2) **dispatch citation-collectors first** to enumerate predecessor frameworks from FOCAL 2024 + Newmark 2017, then download as much of the cited universe as possible before extraction; (3) **README headline swapped to "LobbyView, for all 50 states"** to anchor the project framing.

The session ran in roughly four phases:

1. **Citation-collection** — two background agents enumerated predecessor citations from FOCAL 2024 (26 entries) and Newmark 2017 (25 entries). Output to `predecessors_FOCAL_2024.md` and `predecessors_Newmark_2017.md`.
2. **Predecessor download wave** — single background agent attempted retrieval of every cited paper not already on disk. Result: 17 retrieved (14 PDFs + 2 HTML archives + 1 text-only summary), 3 verified-on-disk, 13 paywalled, 1 not-found, 3 books. User then ran a manual author-page hunt and dropped 5 additional PDFs into main worktree's `papers/`; assistant moved + renamed + text-extracted them. Manifest at `predecessor_download_manifest.md`.
3. **Test set of 3 extractions** — Opheim 1991, CPI Hired Guns 2007, Sunlight 2015. Confirmed format works across three different rubric shapes (thin-label/BoS-fallback / numbered-Q-structured / heterogeneous-tier-ordinal). User reviewed and approved.
4. **Wave dispatch (waves 1, 2, 3a, 3b)** — 23 more papers extracted in parallel batches of 6, 6, 6, 5. All 26 papers extracted by end of session.

## Topics Explored

- **Per-paper indicator extraction** following the locked plan's TSV+MD spec at `docs/active/compendium-source-extracts/results/items_<Paper>.{tsv,md}`. Each agent told to extract the *actual evaluation items the framework uses to score states*, with verbatim source-quote line refs in every TSV row, and to verify FOCAL's secondary-description claims against the paper directly.
- **Predecessor citation enumeration** before extraction — citation-collectors against FOCAL 2024 (26 frameworks named) and Newmark 2017 (25 frameworks named) gave us a deduplicated download-target list of ~37 candidates.
- **Author-page hunt round 1** by the user — 5 additional papers retrieved (Strickland 2014, Mihut 2008, Chung 2024, LaPira & Thomas 2014, CPI 2015 SII Kusnetz) from sources beyond the agent's reach.
- **Working-directory disambiguation issue** caught mid-session — assistant's bash cwd was sometimes the main worktree rather than the compendium-source-extracts worktree. 5 PDFs were inadvertently moved to main's `papers/` and had to be copied across. Future sessions: prefer absolute paths over relative, especially for cross-worktree file ops.
- **README headline change** — "LobbyView, for all 50 states" landed as the anchor framing.

## Provisional findings

### BoS-tradition runs deeper than expected

5 of 26 extracted papers are pure secondary-source-coding rather than own statute reading:

- **Opheim 1991:** 21/22 items coded from CSG's *Campaign Finance, Ethics and Lobby Law: Special Edition* (1988-89, the "Blue Book"); 1/22 from CSG's *Book of the States* 1988-89. Zero own-statute reading.
- **Newmark 2005:** 18/18 main-index items operationally defined by *Book of the States*. Newmark explicitly aligns: *"Similar to Opheim's (1991) measure"*.
- **Newmark 2017:** Hybrid — inherits Newmark 2005's BoS-derived structure + item names, but the 2015 binary values are paper-coded from direct statute examination (BoS data was last collected 2005, contained errors per Newmark footnote 9). Operational threshold magnitudes still not specified.
- **Strickland 2014:** Reapplies Newmark 2005 unchanged at item level + temporally extends 1991-2003 → 1988-2013 using **COGEL Blue Books** (Council on Governmental Ethics Laws — distinct from CSG's Blue Book) + **State Capital Law Firm Group, *Lobbying, PACs, and Campaign Finance: 50 State Handbook*** (post-2004 BoS replacement after CSG stopped collecting lobbying data). Does not read statutes.
- **Flavin 2015:** Applies Newmark 2005 unchanged as single scalar covariate.

The CSG/COGEL/State Capital reference-work tradition is the real ancestor of the older state-rubric line — older than PRI 2010, older than CPI Hired Guns 2007, predates the modern transparency movement. **Acquiring those reference works is critical if compendium-2.0 keeps any of these older rubrics as load-bearing.**

### Many "predecessors" turn out not to be rubrics

Of 26 papers extracted, only ~13 are independent measurement rubrics. The rest split into:

- **Empirical applications of others' rubrics** (Strickland 2014, Flavin 2015, Chung 2024 — uses OpenSecrets data; Mihut 2008 — comparative narrative)
- **Survey studies that consume a typology** (Hogan/Murphy/Chari 2008 — uses Chari/Murphy/Hogan 2007 PQ typology)
- **Subset-displays of multiple rubrics** (Bednařová 2020 — applies CPI HG 48 + CII 47, displays 36 non-zero; the underlying methodology is unchanged)
- **Construct-defining work** (LaPira & Thomas 2014 — operationalizes revolving-door measurement)
- **Federal-data infrastructure** (Kim 2018 LobbyView — *not* a rubric; data fields + enrichment pipeline)
- **Methodological scoping reviews** (Lacy-Nichols 2023 — what researchers can do with disclosure data; downstream half of the FOCAL research program)
- **Empirical evaluation papers** (McKay & Wozniak 2020 — applies CPI HG + Piotrowski & Liao 2012 usability framework to UK)

### FOCAL Table 2 secondary-descriptions: not authoritative

Right (10): Opheim, Newmark 2017, CPI Hired Guns 2007, FOCAL self, ALTER-EU 2013, AccessInfo 2015, IBAC 2022, GDB 2022 (within scope), CoE 2017 (41 vs 42, within tolerance), SOMO 2016.

Wrong (3): Newmark 2005 (3 vs 4 categories), Carnstone 2020 (FOCAL conflated with Roth 2020 — wrong category labels + wrong count), TI 2016 ("methodological touchstone" framing overstates what is a 4-bullet TI-UK lens applied subjectively to 3 datasets).

Approximate / not-a-rubric (3): Bednařová 2020, Hogan/Murphy/Chari 2008, Kim 2018.

This is a useful reliability signal: when designing compendium-2.0, treat FOCAL's secondary-description Table 2 as a starting point, not a contract.

### FOCAL is the most useful synthesis but explicitly unweighted

FOCAL 2024 has 50 indicators in 8 categories (Scope 4, Timeliness 3, Openness 9, Descriptors 6, Revolving door 2, Relationships 4, Financials 11, Contact log 11). All 50 rows have `scoring_rule = "Not specified"` — FOCAL is the *checklist of what should be disclosed*, not the rubric for *how to score states against it*. Authors explicitly flag weighting as "future Delphi work." So FOCAL gives compendium-2.0 the field universe; not a way to grade states.

### Federal-vs-state cross-walk gap is consistent

Three federal-data papers (Kim 2018, Chung 2024, LaPira & Thomas 2014) all surface the same set of federal infrastructural advantages that don't exist at state level:

- Single LDA statute → uniform schema (vs 50 distinct state statutes)
- Canonical H.R./S. bill numbering (vs per-state ID schemes)
- Complete CRS bill database with subject terms (vs OpenStates' weaker bill metadata)
- Quarterly single-Congress cadence (vs varying state cadences)
- SEC-traceable corporate clients via Compustat (vs many non-Compustat state lobbying clients)
- Biographical infrastructure: LegiStorm, CQ First Street, CRP, SOPR (no state equivalents)

LaPira & Thomas 2014's headline finding sharpens the case for LLM enrichment: **LDA self-reporting captures only 29.7% of the 51.7% true verified revolving-door rate** — disclosure substantially under-reports. Same problem at state level, plausibly worse.

### The CDoH parallel measurement universe

Lacy-Nichols 2023 (FOCAL ref #21, by overlapping authors) cites 8 frameworks from the public-health / Commercial Determinants of Health discipline that **have zero overlap with FOCAL 2024's 15-framework reviewed corpus**:

- Mialon, Swinburn & Sacks 2015 (data-source-list precursor)
- Corporate Political Activity Framework (Savell 2014)
- Policy Dystopia Framework (Ulucanlar 2016)
- Corporate Permeation Index (Madureira Lima 2019)
- Corporate Financial Influence Index (Allen 2022)
- CDoH Index (Lee 2022)
- OECD Lobbying in the 21st Century (2021)
- (GDB Political Integrity module 2022 — already in our set)

These approach lobbying from the *corporate-actor side* rather than the *regulatory-disclosure side* — different lens, similar territory. If compendium-2.0 wants comprehensive measurement-universe coverage, this corpus deserves its own retrieval pass.

## Decisions

| topic | decision |
|---|---|
| Plan modifications | No template-first; predecessor citation-collection + download wave before extraction; README headline → "LobbyView for 50 states" |
| Extraction scope | 26 papers extracted = 7 originals + 14 retrieved predecessors + 5 author-hunt-round-1 retrievals. Federal trio (LaPira 2020 LDA at 25, GAO 2025) deferred. Roth 2020 deferred (text-only summary). Newmark & Vaughan 2014 dropped (scandals/media, not lobbying). Lacy-Nichols 2025 skipped (FOCAL application, not predecessor) |
| Predecessor-of-predecessor chase | New acquisition list created (Task #11): CSG Blue Book + BoS volumes + COGEL Blue Books + State Capital handbook; CII methodology source; GDB research handbook; TI-UK open-data rubric; Piotrowski & Liao 2012; Keeling et al. 2017; Chari/Murphy/Hogan 2007 PQ; CDoH-corpus 7 frameworks; new candidates surfaced from extraction lit reviews (Pross 2007, Chari & Murphy 2006, Malone 2004, Hamm/Weber/Anderson 1994, Brasher/Lowery/Gray 1999, Lowery & Gray 1993/1994/1996 vintages, LaPira 2016, Rosenthal 2001) |
| Author-emailing list | Task #10 maintained: post-2000 still-missing papers (Witko 2005/2007, Ozymy 2010/2013, Laboutková & Vymětal 2022/23, Vaughan & Newmark 2008, Roth 2020 thesis, plus the new Chari/Murphy/Hogan 2007 PQ ask) |
| Compendium-2.0 design | Still deferred per the locked plan. Not part of this session. User reviews the 26 extracts personally before design begins |

## Mistakes recorded

For honesty + future-session context:

1. **Working-directory confusion** — assistant's bash cwd was the main worktree rather than `compendium-source-extracts/` for several commands mid-session. Caused 5 PDFs (Strickland, Mihut, Chung, LaPira & Thomas 2014, CPI 2015 Kusnetz article) to land in main's `papers/` instead of the worktree's. Surfaced when an extraction agent reported "PDF not found." Recovered by copying the files across, but should have used absolute paths from the start.
2. **Spec error on Sunlight 2015** — assistant's prompt told the agent "Sunlight uses 4-tier ordinal scales per indicator." Wrong — only 2/5 indicators are 4-tier; one is 5-tier; two are 2-tier (boolean). Agent caught the spec error and captured the actual structure verbatim. Good behavior; assistant's prompt-confidence was the failure.
3. **CPI Hired Guns title** — agent's prompt referred to a `papers/text/CPI_2007__hired_guns_methodology.txt` that doesn't exist alongside the HTML archive. Recovered fine, but the agent flagged that the parent prompt's path-existence claim wasn't accurate.
4. **Conflation in plan/prompt:** Carnstone 2020 prompt warned about Roth 2020 having the same 6/23 layout. The agent confirmed FOCAL conflated the two — but my prompt acknowledging the warning meant we caught it. (Good outcome; original FOCAL Table 2 mistake.)
5. **`papers/extracts/` stray artifacts from prior session** — never cleaned up. Still untracked; not committed. Per the plan's instruction.

## Goal of this session

Execute the per-paper extraction plan and surface findings for user review.

Outcome: 26 extractions complete. 22 new acquisition targets surfaced. User now has the full corpus to review before compendium-2.0 design begins.

## Next steps

- User reviews the 26 TSV+MD pairs.
- After review: separate plan for compendium-2.0 design (per locked plan).
- Author-emailing skill executes Task #10 to retrieve Witko/Ozymy/Laboutková/Vaughan&Newmark/Chari/Roth.
- CSG/COGEL/State Capital reference-work acquisition (Task #11) — likely via Adam Newmark contact + library/HathiTrust hunt.
- Optional follow-up: CDoH-corpus expansion (the 7 health-discipline frameworks).
- Optional follow-up: federal-extension extracts (LaPira 2020 LDA at 25, GAO 2025) if user wants federal LDA in scope.

## Results

All artifacts at `docs/active/compendium-source-extracts/results/`:

**Predecessor work (3):**
- `predecessors_FOCAL_2024.md` — 26 entries
- `predecessors_Newmark_2017.md` — 25 entries
- `predecessor_download_manifest.md` — full manifest with status per candidate

**Per-paper extracts (26 TSV+MD pairs):**
- `items_Opheim.{tsv,md}` — 22 atomic + 4 composite, 100% BoS-defined
- `items_HiredGuns.{tsv,md}` — 48 questions, own statute reading + agency interviews
- `items_Sunlight.{tsv,md}` — 5 ordinal indicators (heterogeneous tiers)
- `items_Newmark2005.{tsv,md}` — 18 main + 1 penalty, 100% BoS-defined
- `items_Newmark2017.{tsv,md}` — 19 atomic + 3 sub + 1 composite, hybrid BoS-structure / paper-coded values
- `items_OpenSecrets.{tsv,md}` — 7 indicators, no predecessors cited, 19-state gap acknowledged
- `items_FOCAL.{tsv,md}` — 50 indicators, unweighted checklist
- `items_CouncilEurope.{tsv,md}` — 41 items (FOCAL said 42), 11 categories
- `items_Carnstone.{tsv,md}` — 25 items in 5 principles (FOCAL conflated with Roth)
- `items_ALTER_EU.{tsv,md}` — 25 recommendations across 11 categories
- `items_AccessInfo.{tsv,md}` — 75 rows = 38 top-level + 34 sub + 3 principles (72 scored items)
- `items_Bednarova.{tsv,md}` — 38 rows (subset display of CPI HG 48 + CII 47)
- `items_IBAC.{tsv,md}` — 23 substantive items + 1 preamble, 8 categories
- `items_HoganMurphyChari.{tsv,md}` — 10 items, attitudinal survey not rubric
- `items_GDB.{tsv,md}` — 3 indicator-stems (full sub-questions in handbook)
- `items_SOMO.{tsv,md}` — 76 items in 12 categories (largest extracted)
- `items_McKayWozniak.{tsv,md}` — 18 items, applies CPI HG + Piotrowski & Liao usability
- `items_TI_2016.{tsv,md}` — 38 rows, applies TI-UK 4-criterion rubric
- `items_CPI_2015.{tsv,md}` — 16 rows; 13 categories captured but lobbying questions not enumerated in available materials
- `items_Kim2018.{tsv,md}` — 18 LobbyView data fields (federal infrastructure)
- `items_LacyNichols2023.{tsv,md}` — 35 rows across 4 typologies; downstream half of FOCAL research program
- `items_Strickland.{tsv,md}` — 0 own + 1 meta-row (applies Newmark 2005 unchanged + extends with COGEL/State Capital)
- `items_Mihut.{tsv,md}` — 20 dimensions, comparative narrative not rubric
- `items_Chung.{tsv,md}` — 14 rows of analytical primitives, federal-only mapping
- `items_LaPiraThomas2014.{tsv,md}` — 18 rows operationalizing revolving-door construct
- `items_Flavin.{tsv,md}` — 0 own + 1 meta-row (applies Newmark 2005)

## Plan produced

None this session — compendium-2.0 design plan deferred per the locked plan until after user review of these 26 extracts.

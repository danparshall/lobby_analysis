# Comprehensive item set — v2  (20260506)


Working draft for compendium 2.0. Assembled from per-rubric source 
extracts shipped 2026-05-03, a coverage-gap extension from Opheim 
1991 (identified via OpenAI `text-embedding-3-large` similarity 
analysis), and all PRI 2010 items (added 2026-05-06 per explicit 
user clearance to use PRI as a non-default coverage source).

> **PRI inclusion note:** PRI 2010 items are tagged 
> `ext_pri_2010_*` to make their non-default status durable. 
> PRI is NOT a structural anchor here. The STATUS.md ⛔ block 
> on PRI remains in force for all OTHER uses (no PRI-derived 
> seeding, no "match PRI" calibration, no bootstrapping new 
> artifacts from PRI rubric structure).

## Composition

- **Total items:** 209

| compendium_role | n | source rubric |
|---|---:|---|
| core_hg | 47 | CPI Hired Guns 2007 (50-state report-card on lobbying disclosure) |
| core_focal | 50 | FOCAL / Lacy-Nichols 2024 (cross-jurisdiction normative checklist) |
| core_newmark2017 | 19 | Newmark 2017 (state lobbying-regulation index, 19-component) |
| ext_opheim_enforce | 6 | Opheim 1991 — agency enforcement powers (Table 31 of the COGEL Blue Book; Newmark dropped these) |
| ext_opheim_income | 2 | Opheim 1991 — income disclosure (distinct from compensation) |
| ext_opheim_oversight | 1 | Opheim 1991 — review intensity dimension |
| ext_opheim_catchall | 1 | Opheim 1991 — influence-peddling catch-all |
| ext_pri_2010_disclosure | 61 | PRI 2010 disclosure-law rubric (61 atomic items; transcribed 2026-04-13 from PRI 2010 §III) |
| ext_pri_2010_accessibility | 22 | PRI 2010 accessibility rubric (22 atomic items; transcribed 2026-04-13 from PRI 2010 §IV) |

## Method

Coverage analysis: for each non-core atomic item, computed cosine 
similarity to every core-3 item under text-embedding-3-large; took 
the per-item argmax as best-core-match. Items with best-core-match 
sim < 0.55 are uncovered; sim 0.55-0.60 are partial; sim ≥ 0.60 are 
covered (with the caveat that single-link clustering at sim ≥ 0.68 
tends to under-bridge cross-tradition pairs).

Pulled in: 8 Opheim items at sim < 0.55 (clearly uncovered) plus 2 
borderline items (sim 0.55-0.60) that add conceptually distinct 
content beyond their lexical near-matches.

Skipped (covered): all Newmark2005 (short-label artifacts of items 
in Newmark2017), all OpenSecrets (fully covered), all Sunlight 
(short labels), all CPI_2015 (multi-domain integrity scorecard, 
most items not lobbying-specific).

European-tradition rubrics deferred — most items are out of 
US-state-lobbying-disclosure scope. A future pass may flag a small 
subset (e.g. IBAC MP-meeting-disclosure cluster) for 
coverage-comparison reference; not in this round.

PRI 2010 added in v2 (this round) per explicit user clearance 
2026-05-06: "include all PRI items, now that we aren't locked 
onto them". All 83 PRI atomic items pulled in unfiltered (22 
accessibility + 61 disclosure-law). They are NOT in the 509-item 
embedding space (PRI was excluded from the 26-paper extraction 
round), so `best_core_match_*` columns are blank for PRI rows. A 
follow-up coverage analysis could embed them and identify which 
PRI items are redundant with existing rows; for now all are kept 
verbatim.

## Files

- TSV: `20260506_comprehensive_set_v2.tsv`  (209 rows × 13 cols)
- Source extracts: `items_HiredGuns.tsv`, `items_FOCAL.tsv`, 
  `items_Newmark2017.tsv`, `items_Opheim.tsv`
- Embedding artifacts: `embed_*__openai__text-embedding-3-large.{npy,csv,txt}`

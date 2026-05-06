# Compendium assembly via embeddings — v1  (20260506)

> **Caveat:** one candidate item set produced by ONE assembly method
> (embedding-based coverage analysis with manually-selected Opheim
> extensions). NOT the comprehensive set / NOT THE answer for compendium
> 2.0. Parallel assemblies (`comp_assembly_regex`, possibly others) will
> produce alternate candidate sets; the comprehensive set is whatever
> falls out of comparing/reconciling those, not what any single method
> produces.

Assembled from per-rubric source extracts shipped 2026-05-03, plus a
coverage-gap extension from Opheim 1991 identified via OpenAI
`text-embedding-3-large` similarity analysis. Vectors at
`embed_vectors__openai__text-embedding-3-large.npy`; index at
`embed_index__openai__text-embedding-3-large.csv`.

## Composition

- **Total items:** 126

| compendium_role | n | source rubric |
|---|---:|---|
| core_hg | 47 | CPI Hired Guns 2007 (50-state report-card on lobbying disclosure) |
| core_focal | 50 | FOCAL / Lacy-Nichols 2024 (cross-jurisdiction normative checklist) |
| core_newmark2017 | 19 | Newmark 2017 (state lobbying-regulation index, 19-component) |
| ext_opheim_enforce | 6 | Opheim 1991 — agency enforcement powers (Table 31 of the COGEL Blue Book; Newmark dropped these) |
| ext_opheim_income | 2 | Opheim 1991 — income disclosure (distinct from compensation) |
| ext_opheim_oversight | 1 | Opheim 1991 — review intensity dimension |
| ext_opheim_catchall | 1 | Opheim 1991 — influence-peddling catch-all |

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

PRI 2010 deliberately excluded per STATUS.md ⛔ block. Future task: 
after this set is in shape, scan PRI for items uniquely capturing 
government-funded lobbying that the core 3 + Opheim extension 
miss. PRI is a non-default coverage source only.

## Files

- TSV: `20260506_comp_assembly_embed_v1.tsv`  (126 rows × 13 cols)
- Source extracts: `items_HiredGuns.tsv`, `items_FOCAL.tsv`, 
  `items_Newmark2017.tsv`, `items_Opheim.tsv`
- Embedding artifacts: `embed_*__openai__text-embedding-3-large.{npy,csv,txt}`

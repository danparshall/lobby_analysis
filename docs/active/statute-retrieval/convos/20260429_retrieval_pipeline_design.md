# 2026-04-29: Retrieval Pipeline Design & Calibration

**Date:** 2026-04-29
**Branch:** statute-retrieval

## Summary

Long session covering the full arc from design through implementation through calibration. Built a two-pass statute retrieval pipeline (retrieval agent identifies cross-references in core lobbying chapters → orchestrator fetches support chapters → scoring agent scores the expanded bundle against PRI 2010 rubric). Ran multiple calibration rounds on OH, CA, and TX, iterating on the scorer prompt to improve agreement with PRI 2010 ground-truth disclosure-law scores.

The retrieval infrastructure works well — the retrieval agent reliably finds cross-references, the enriched manifest provides an audit trail, and the ingest pipeline deduplicates and fetches correctly. The remaining gaps are in scorer interpretation, particularly around how to read exemption clauses and how entity-type coverage interacts with activity-based registration triggers.

## Topics Explored
- Cleaned up merged worktrees (lobbying-data-model, scoring) and verified data safety
- Redesigned calibration subset: CA, TX, OH (dropped WY, kept WI URLs)
- Designed two-pass retrieval architecture (LLM-driven cross-reference discovery, 2-hop limit, enriched manifests)
- TDD implementation: Phase 1 (enriched StatuteArtifact model + loader + retriever), Phase 2 (retrieval agent prompt + brief builder + ingest_crossrefs + orchestrator subcommands)
- Ran retrieval agents on all 3 states: OH found 9 cross-refs, CA found 5, TX found 7
- Discovered Justia 404 gap for CA 2010 definitions chapter (§§82000-82054); used 2007 vintage as fallback
- Multiple scorer prompt iterations targeting A-series (registration coverage), C-series (public entity definition), and E-series (disclosure cascade)

## Provisional Findings

### Retrieval pipeline
- LLM-driven cross-reference discovery (approach C) works well. The retrieval agent consistently identifies relevant cross-references and constructs valid Justia URLs.
- OH: 9 cross-refs found (all URLs valid), 4 unresolvable (federal/constitutional — correct)
- CA: 5 cross-refs found, but 3 URLs returned 404s due to Justia vintage gap. Fallback to 2007 vintage resolved it.
- TX: 7 cross-refs found including the critical §311.005 "person" definition

### Scorer calibration (best results per state)

| Sub-aggregate | CA (run 3) | TX (run 4) | OH (run 4) |
|---|---|---|---|
| A_registration | 7/6 (+1) | 2/7 (-5) | 8/7 (+1) |
| B_gov_exemptions | 3/2 (+1) | 2/3 (-1) | 2/2 match |
| C_public_entity_def | 0/0 match | 0/0 match | 1/1 match |
| D_materiality | 1/1 match | 1/1 match | 0/1 (-1) |
| E_info_disclosed | 17/14 (+3) | 11/18 (-7) | 17/15 (+2) |

- **D matches 2/3 states** (was 3/3 before last prompt change — OH regressed)
- **C matches 3/3 states** — functional definition guidance works
- **CA and OH A-series within ±1** of PRI; TX A-series is -5, a harder problem
- **TX E-series has a cascade bug**: scorer reads §305.004(4) principal exemption as blanket, scores E1a=0, which zeros all 15 E1 items. PRI says TX E=18.

### Key scorer prompt insights
- "Read the full statute before scoring" is necessary but not sufficient for TX
- Exemption-narrowness guidance helps CA/OH but doesn't fix TX's interaction between two registration triggers (expenditure-based vs compensation-based)
- The scorer reads bottom-up (definition → who's included) but PRI reads top-down (trigger → who's exempt from the trigger). TX exposes this because its §305.003(a)(1) expenditure trigger is entity-agnostic even though its "person" definition is narrow.

## Decisions Made
- Two-pass architecture with enriched manifests (see plan doc)
- `expand-bundle` and `ingest-crossrefs` as separate orchestrator subcommands
- PRI 2010 scores as TDD-equivalent test suite
- Scorer prompt iterates on scorer interpretation, not retrieval (retrieval is working)
- Plan doc: `plans/20260429_two_pass_retrieval_agent.md`

## Results
- `results/20260429_calibration_comparison.md` — cross-state calibration results table

## Open Questions
1. **TX A-series**: How did PRI score A=7 when §305.002(8) "person" doesn't include government entities? Likely PRI read the expenditure trigger (§305.003(a)(1)) as entity-agnostic, covering government entities despite the narrow "person" definition. Scorer needs to reason about trigger-vs-entity interaction.
2. **TX E1 cascade**: §305.004(4) exempts principals whose *only* activity is compensating a lobbyist, but non-exempt principals must register under §305.005 and disclose under §305.006. Scorer treats the partial exemption as blanket. Multiple prompt fixes haven't resolved this.
3. **E over-scoring on CA/OH**: Consistently +2-3 on E across CA and OH. Without item-level PRI truth, can't pinpoint which items. May be PRI under-counting rather than pipeline error.
4. **Justia 404 handling**: CA 2010 definitions chapter not on Justia; used 2007 fallback. Pipeline needs systematic 404 detection and adjacent-vintage fallback logic.
5. **OH D regressed**: Was matching, now 0/1 after last prompt change. The "unable_to_evaluate" items may be related.

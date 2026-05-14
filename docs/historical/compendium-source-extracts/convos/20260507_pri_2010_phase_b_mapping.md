# PRI 2010 Phase B projection mapping

**Date:** 2026-05-07 (late eve, third session today)
**Branch:** compendium-source-extracts
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (second rubric — PRI 2010, after CPI 2015 C11)
**Handoffs consumed:**
- [`plans/_handoffs/20260507_phase_b_handoff.md`](../plans/_handoffs/20260507_phase_b_handoff.md) (state-of-Phase-A locked)
- Predecessor convo [`convos/20260507_phase_b_projection_mappings.md`](20260507_phase_b_projection_mappings.md) (CPI 2015 mapping that locked the conventions PRI inherits)

## Summary

Second Phase B mapping doc shipped: PRI 2010 (combined disclosure-law + accessibility, 83 items × 50 states, total 919 lines). Stress-tested the per-item template at scale — handles compound/parallel/typed/enum/free-text shapes without modification. The doc-conventions block carried straight over from CPI without changes; PRI didn't surface any need to extend the convention set.

Single-pass execution per user direction (a1, "do them all"). No mid-session review cycles needed — the conventions were tight enough that all 83 items resolved deterministically against them.

## Topics Explored

- Per-item mapping for all 83 PRI 2010 atomic items: 22 accessibility (Q1-Q6 baseline binaries + Q7a-o 15-criteria search-filter battery + Q8 ordinal_0_to_15) + 61 disclosure-law (A1-A11 actor-side registrant taxonomy + B1-B4 government-exemption + C0-C3 public-entity-def + D0/D1/D2 materiality with typed-cell pattern + E1a-E1j 19 principal-side + E2a-E2i 18 lobbyist-side).
- Conceptual distinction: PRI A is **actor-side** ("who must register as a lobbyist"); CPI #196 is **target-side** ("definition recognizes communications with X as lobbying"). Compendium splits accordingly into separate `actor_*` and `def_target_*` row families.
- E1/E2 parallelism: PRI atomizes principal-side (E1) and lobbyist-side (E2) in deliberate structural parallel. Per granularity-bias, compendium 2.0 keeps these as **separate** rows (`principal_*` and `lobbyist_*`) because regimes can regulate the two actors asymmetrically. The consensus method correctly identified the parallel pairs (loose-c_028 through c_039 are mostly E1*/E2* mirror pairs).
- Typed-cell pattern at PRI granularity: D1_present + D1_value collapse into ONE row carrying typed `Optional[Decimal]`; D2 same with `Optional[float]`. Two PRI atomic items, one compendium cell, two different projections (presence-flag vs raw-value).
- E1h/E2h cadence representation: PRI's 6-binary atomization conflicts with CPI #202's enum cell. Resolution: adopt PRI's binary representation as canonical (more general — handles multi-cadence regimes naturally); CPI #202's enum becomes a derived projection. Flagged for design-team review (Open Issue 4).
- Aggregation rule structure verified empirically: accessibility max=22 (sum of Q1-Q6 binaries + Q7_raw 0-15 + Q8_normalized 0-1), disclosure-law max=37 (A_registration ~11 + B ~4 + C 1 gate + D 1 gate + E_info_disclosed ~20). Spot-checked Alabama/Alaska percentages — match published values to ≤0.2% error.
- Within-E rollup ambiguity: PRI paper does NOT specify how E1f_i-iv (4 binaries) → E1f sub-aggregate slot (1 point? 4 points?); same for E1g_i-ii, E1h_i-vi, etc. Phase C will need to fit empirically against the per-state E_info_disclosed values. Historical pri-calibration's "9 methodology differences" doc is the input. Phase B punts.
- Cluster reference enrichment: ran `grep` over 3-way consensus output to identify all PRI items in strict (3) and loose (32) clusters; mapping doc references provenance hints throughout (cf. strict-c_NNN / loose-c_NNN).
- Q8's 0-15 ordinal partition: per user direction (a2), treated as Open Issue analogous to CPI 25/75 partial-credit. Cell carries the raw ordinal; partition decision deferred to Phase C.

## Provisional Findings

- **Per-item template scales to PRI's atomic resolution without modification.** 83 items mapped into the same per-item structure used for CPI's 14. Compound items, parallel pairs, typed-with-presence-flag, free-text companions all fit cleanly. The granularity-bias convention does most of the work — PRI was already finely atomized in the source rubric, so the convention is mostly *preserving* PRI's atomization rather than expanding it further.
- **PRI adds ~52 NEW compendium rows on top of CPI's 21**, matching the handoff's prediction of 30-50. Rough breakdown: 18 NEW accessibility rows (most of Q7a-o + a few Q1-Q5 specifics), 11 actor-side registrant-taxonomy rows (A1-A11), 4 government-exemption rows (B1-B4), 4 public-entity-def rows (C0-C3, with C1-C3 captured but unread by PRI projection), 3 materiality rows (D-series condensed via typed cells), and ~12 principal/lobbyist-side report-content rows that CPI's compound reads didn't surface separately.
- **Total compendium rows touched after CPI + PRI: ~85** (21 from CPI + ~52 new from PRI + ~12 shared/refined rows). Both rubrics' projections read overlapping rows on the cross-rubric core (lobbyist registration, spending-report itemization, cadence, contact disclosure) — exactly the behavior the success criterion expects.
- **PRI's published per-state ground truth is sub-aggregate-level only** — 5 disclosure-law sub-aggregates × 50 states + 8 accessibility sub-components × 50 states = 650 ground-truth values. Per-atomic-item validation impossible against PRI's published data (PRI does not publish per-Q7-sub-criterion or per-A-item per-state scores). Phase C validation tolerance for PRI must be at sub-aggregate granularity, not per-item. Cross-rubric per-item validation via CPI's 700-cell ground truth still works for shared rows.
- **The compendium row design is converging across rubrics.** PRI adds rows but doesn't *contradict* CPI's row design — every CPI row that PRI touches reads the same observable. This validates the projection-driven row-design approach (clusters as guidelines, projection needs as authoritative).

## Decisions Made

| Topic | Decision |
|---|---|
| PRI's E1/E2 parallel pairs | Two compendium rows per pair (`principal_*` + `lobbyist_*`); regimes may regulate asymmetrically |
| PRI A vs CPI #196 | Distinct: A is actor-side registrant taxonomy, CPI #196 is target-side def-of-lobbying. Two row families. |
| D1/D2 representation | One typed `Optional[Decimal]` (D1) / `Optional[float]` (D2) cell per threshold; D_present is `IS NOT NULL` projection |
| C1-C3 in compendium | Captured as compendium rows even though PRI projection doesn't read them; cross-rubric & downstream-consumer use justifies inclusion |
| E1h/E2h cadence | 6 binary rows per actor (canonical); CPI's enum becomes derived projection. Retroactive change to CPI mapping flagged |
| E1h_vi/E2h_vi "Other" | 2-row pair: binary indicator + free-text specification companion |
| Q8 partition | Open Issue; cell carries raw 0-15 ordinal; partition decision deferred to Phase C (per user direction a2) |
| B1/B2 scoring direction | Provisional +1 for True; Phase C empirical fit against B_gov_exemptions sub-aggregate will confirm or flip |
| Single-pass execution | Per user direction a1; no mid-session review cycles |

## Results

- [`results/projections/pri_2010_projection_mapping.md`](../results/projections/pri_2010_projection_mapping.md) — 919-line Phase B mapping doc (83 atomic items × 69 distinct compendium rows touched, 9 open issues for design-team review)

## Open Questions

(Same set as the mapping doc's Open Issues section, repeated here for convo-summary completeness.)

1. **Q8 0-15 partition** — defer to Phase C (analogous to CPI 25/75).
2. **PRI's "flag for Phase 3" items** — Q3 ("easily found"), Q5 ("historical horizon"), Q6 ("immediately useable format"), Q7 sub-component scoring rule, Q8 anchors. Phase C operationalizes; Phase B records the open-ness.
3. **B1/B2 scoring direction** — Phase C empirical fit reveals.
4. **E1h/E2h enum-vs-binary tension with CPI #202** — provisionally adopting PRI's binary as canonical; design-team review needed.
5. **E1j independent aggregation** — Phase C consumption layer must respect PRI's "scored independently of E" carve-out per paper §III.E intro.
6. **C1-C3 / D1_value / D2_value in compendium but not read by PRI projection** — clean example of compendium rows kept for cross-rubric value; OK as-is.
7. **De-jure / de-facto staging recommendation** carries forward from CPI: stage de-jure first, hold de-facto until practical-availability extraction can populate from primary observation. Same decision pending for both CPI 2015 and PRI 2010 accessibility.
8. **Per-atomic-item ground truth not published for PRI** — Phase C validation must be at sub-aggregate granularity for PRI; per-item via CPI cross-rubric where rows overlap.
9. **Two-row vs one-row-with-actor-enum for E1/E2 parallel pairs** — flagged for review; current design is two rows.

## Next Steps

1. **Sunlight 2015 Phase B mapping.** 4 of 5 items (item 4 excluded per Phase A handoff). Smallest remaining rubric. Should be quick.
2. **OpenSecrets 2022 Phase B mapping.** 4 categories (Cat 1 binary, Cats 2/3 few-shot, Cat 4 decomposed). Different shape — few-shot anchors enter the mapping doc explicitly.
3. **Newmark 2017 / 2005 / Opheim / HiredGuns Phase B.** Standard shape, varying granularities.
4. **FOCAL 2024 Phase B.** Largest after PRI; per-country ground truth from L-N 2025 Suppl File 1; main interesting bit is the 50-indicator weighted-aggregation rule.
5. **LobbyView Phase B (schema-coverage).** Different shape; tackled last.
6. **After all 9 mappings done:** union compendium rows → `disclosure_side_compendium_items_v1.tsv`. The compendium 2.0 row set falls out as a byproduct; rows in consensus-but-no-projection get flagged "keep / delete?"; rows in projection-but-no-consensus get added. Deduplication/normalization of working-name row IDs across the 9 docs is its own pass.
7. **Then Phase C scaffolding:** `tests/fixtures/projection_inputs/<rubric>_<state>_<vintage>.json` hand-population from the per-state ground truth; projection-function implementation; validation against published data with the staging recommendation (de-jure first).

## Mistakes recorded

None — single-pass execution; no rework cycles. Conventions from CPI session were tight enough that all 83 items resolved deterministically.

If anything, the doc may have been slightly *over*-cautious on the E1h/E2h cadence representation (flagging it as a retroactive CPI modification when in practice it's just two valid representations of the same observable, and CPI's projection can read either). Will let the user adjudicate the framing in review.

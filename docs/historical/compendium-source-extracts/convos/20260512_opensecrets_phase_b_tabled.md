# OpenSecrets 2022 — Phase B attempt → tabled

**Date:** 2026-05-12 (work) / 2026-05-13 (cleanup + finish-convo)
**Branch:** compendium-source-extracts
**Plan:** [`../plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (was 4th rubric per handoff order; ended up tabled instead).
**Handoff that pointed here:** [`../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) (now updated to remove OpenSecrets and renumber Phase B remaining to 6 rubrics).

## Summary

This session opened as the 4th Phase B projection mapping (OpenSecrets 2022) following the locked Phase C order. The mapping doc was drafted to completion before user pushback surfaced a structural problem the recheck had glossed: OpenSecrets's published rubric has no per-tier scoring definition for scores 0–3 in Cats 1/2/3, no score-5 anchor for Cat 1, and no published per-state per-category numerical data accessible without JS-widget scraping. Per the branch's success criterion — projection functions reproducible from compendium cells, validated against published prior data as sanity checks on extraction accuracy — OpenSecrets fails. The original 2026-05-07 Phase A1 DROP verdict was structurally correct on that criterion; the 2026-05-07 recheck overturned it on the weaker "few-shot calibratable from worked examples" criterion, which doesn't actually serve the branch's stated purpose.

Decision: **table OpenSecrets** (not permanently drop — research decisions stay reversible). The 3 OS-distinctive row candidates (separate-registrations, exact-vs-ranges compensation, per-individual-vs-aggregate compensation) are tabled alongside, pending organic pickup by another rubric's mapping or project-internal data-infrastructure justification.

Implementation: new tabled doc at `results/_tabled/opensecrets_2022_tabled.md` documenting reasoning + reinstatement triggers + the 3 row candidates with per-row pickup possibilities; reversal addendum on the recheck doc; handoff doc updated to renumber the Phase B order to 6 rubrics with Newmark 2017 as next; STATUS.md + RESEARCH_LOG.md session entries.

## Topics Explored

- Cross-rubric grep across 9 rubric TSVs + historical PRI 2010 disclosure-law CSV for OpenSecrets's 4-category concepts (separate-registration, compensation, cadence, portal accessibility). Heavy overlap confirmed for Cats 2 and 4; Cat 3's in-session/out-of-session cadence split also covered by Opheim 1991. Cat 1's `separate_registrations` is OS-distinctive but has a weak LobbyView analog (registrant_uuid + client_uuid).
- Per-category projection logic drafted and reviewed against source-article anchors. Cat 1's projection is degenerate (emits {3, 4} only — no anchors for 0/1/2/5). Cats 2/3's partial-credit (scores 1–3) requires calibration-by-distribution rather than deterministic projection.
- Discovery during user check-in: OS has no published per-tier scoring definitions; the article methodology (lines 196–216) is the entire published rubric universe, supplemented only by worked examples in the Rankings narrative + the JS-rendered state-map widget (not pulled).
- Branch-purpose re-anchoring: per STATUS.md, the success criterion is projection-vs-published-data validation as a sanity check on extraction accuracy. The "few-shot calibratable" criterion the 2026-05-07 recheck applied is softer than this bar.
- Tabling vs permanent drop framing: user explicit direction — "this is tabled, not dropped eternally. Remember this is research, so we don't make permanent everlasting decisions."

## Provisional Findings

- **OpenSecrets 2022's published rubric is too thin to serve as a Phase C projection-validation target.** Cat 1: 2 anchors (3, 4) for a 0–5 range. Cat 2: 3 anchors (0, 4, 5-undefined). Cat 3: 2 anchors (4, 5). Cat 4: explicit sub-facet weights but partial-credit boundaries unquantized; OS itself flags Cat 4 as "more subjective." No inter-coder reliability published. No per-state per-category numerical data in accessible form.
- **The original Phase A1 DROP verdict was structurally correct on the branch's criterion.** The recheck's overturn used a weaker criterion and didn't actually unblock projection-vs-published validation. The mapping attempt today empirically confirmed the original audit's structural finding.
- **The mapping work surfaced 3 statutory observables OS would have read but no other current rubric reads at the same granularity** — `separate_registrations_for_lobbyists_and_clients`, `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges`, `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate`. These are real distinguishing cases in state statutes. Tabled alongside the rubric pending organic pickup.
- **Cadence in-session/out-of-session split is NOT OS-distinctive.** Opheim 1991 reads the same split as a binary. Opheim's mapping will introduce the row family. The CPI mapping's Open Issue 4 (cadence representation) remains open but no longer needs OS as the forcing case.
- **Cat 4 portal sub-facets fold cleanly into existing CPI/FOCAL/HG rows.** Compendium 2.0 dedup will collapse these without OS being a contributing rubric.

## Decisions

| topic | decision |
|---|---|
| OpenSecrets 2022 status | **TABLED 2026-05-13** — set aside from contributing-rubric set; reinstatement triggers documented in `_tabled/opensecrets_2022_tabled.md` |
| Tabling vs dropping | Tabled, not dropped permanently. Drop is reversible. |
| Reason of record | No published per-tier scoring definition lets us project from cells deterministically; few-shot calibration doesn't meet the branch's projection-vs-published-data sanity-check bar |
| 3 OS-distinctive row candidates | Also tabled. Two reinstatement paths documented: (a) organic pickup by another rubric's mapping, (b) project-internal data-infrastructure justification at compendium 2.0 row-set freeze |
| Cadence in-session/out-of-session split | NOT tabled — Opheim 1991 will pick it up |
| Cat 4 portal sub-facets | NOT tabled — fold into existing CPI/FOCAL/HG rows during compendium 2.0 dedup |
| Phase B order | Renumbered to 6 rubrics. **Next: Newmark 2017** |
| Recheck verdict | Reversal addendum appended to `20260507_opensecrets_recheck.md`; original Phase A1 DROP audit re-established as structurally correct |

## Results

- [`../results/_tabled/opensecrets_2022_tabled.md`](../results/_tabled/opensecrets_2022_tabled.md) — new tabling doc; reasoning, reinstatement triggers, 3 OS-distinctive row candidates with per-row pickup possibilities.
- Reversal addendum appended to [`../results/20260507_opensecrets_recheck.md`](../results/20260507_opensecrets_recheck.md).
- Handoff [`../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) updated: 7 rubrics → 6 rubrics; OpenSecrets watchpoint replaced with tabling pointer; Newmark 2017 reordered to position 1.

## Mistakes recorded

1. **Executed handoff without re-checking branch purpose at session start.** The handoff said "do OpenSecrets next per the locked order"; I executed without reading the recheck doc with a critical eye and without comparing the recheck's "few-shot calibratable" criterion against STATUS.md's success criterion. User pushback (asking "where's the detailed rubric?" and then "if they aren't reproducible, then there's no point, right?") surfaced what should have been visible from session-start. **Lesson:** when a handoff points at a rubric, re-read the audit/recheck artifacts with the branch's success criterion in mind before drafting; don't assume the prior agent's verdict aligns with the criterion. The recheck doc itself documented its weaker criterion — should have been a flag.
2. **Attempted `rm` on the projection-mapping doc instead of `git mv`-with-SUPERSEDED-banner when reframing to tabled.** User pushed back mid-execution ("are you deleting datafiles?"). The `rm` was issued in parallel with an Edit that the user separately cancelled; the parallel-tool rollback also cancelled the `rm`, so the file was still on disk when I rechecked. Properly moved 2026-05-13 to [`results/_tabled/opensecrets_2022_projection_mapping_superseded.md`](../results/_tabled/opensecrets_2022_projection_mapping_superseded.md) with a SUPERSEDED banner pointing at the tabling doc. Generalize: **prefer move-with-banner over delete for analytical artifacts, even un-committed; the user's research-data preservation principle extends to analysis, not just experiment data.** Lucky outcome this time, but the lesson is independent of the outcome.
3. **Did not flag the recheck-vs-success-criterion mismatch on first read.** The recheck explicitly applied a weaker criterion than the branch's stated bar, and even said "operationally too strict" about the original audit's framing. A more rigorous read at session start would have noticed this mismatch and surfaced the question to the user before drafting any mapping. **Lesson:** "agent overcorrection in response to prior user pushback" is a real failure mode in research workflows; flag it when reading prior session artifacts.

## Open Questions

1. ~~Should the projection-mapping doc be reconstructed?~~ Resolved: the original draft was preserved at [`../results/_tabled/opensecrets_2022_projection_mapping_superseded.md`](../results/_tabled/opensecrets_2022_projection_mapping_superseded.md) after the failed `rm` and the move-with-banner cleanup. No reconstruction needed.
2. **State-map widget JS pull** — recheck note's "open option" to convert OS from worked-examples calibration to per-cell-ground-truth validation. Still unblocked; would re-qualify OS for the contributing-rubric set per reinstatement trigger 2 in the tabling doc. Not done; not on critical path.
3. **Compendium 2.0 row freeze should explicitly decide on the 3 OS-distinctive row candidates.** Currently they're tabled with two reinstatement paths (organic pickup / project-internal need). The freeze pass should make an active decision rather than carrying them as ambiguous indefinitely.

## Next Steps

1. **Next rubric: Newmark 2017** per updated handoff. 19 items, mostly binary disclosure.* rows with strong existing-row reuse from CPI/Sunlight mappings; key new row is `disclosure.expenditures_benefitting_officials` (FOCAL/Newmark cross-rubric stack). See handoff per-rubric watchpoint.
2. **Optionally:** decide on (a) reconstructing the projection-mapping doc as a research artifact (open question 1) and (b) state-map widget pull as a reinstatement attempt (open question 2). Both are punt-able.
3. **Compendium 2.0 row freeze** (separate plan, post-Phase-B-completion) must make an active decision on the 3 OS-distinctive row candidates and on the CPI mapping's Open Issue 4 (cadence representation).

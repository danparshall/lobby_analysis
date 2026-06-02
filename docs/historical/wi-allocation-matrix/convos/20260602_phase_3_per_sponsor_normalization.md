# phase_3_per_sponsor_normalization

**Date:** 2026-06-02
**Branch:** wi-allocation-matrix

## Summary

Took the Phase 3 chain output (115,229 rows, `data/allocations/WI/WI_chain_2025.tsv`) and addressed refinement candidate #1 from the Phase 3 writeup: the systematic Assembly bias in `SUM(modeled_hours) GROUP BY sponsor` caused by replicating a bill's modeled hours to every primary-sponsor row. Added a uniform-share normalization that makes per-sponsor aggregation honest while keeping the original per-bill metric intact. Surfaced a second finding mid-implementation — WI bill numbers collide within a biennium (multiple distinct `item_id`s share canonical `bill_id="AB 1"`) — and added `item_id` to the schema so consumers can disambiguate.

The session was a tight TDD pass: 6 RED tests, GREEN with two minimal edits to `chain.py` (per-sponsor math at row emit + schema column-order). Full WI allocation suite + global suite both green; 1,636 pass + the same 3 pre-existing baseline failures from `test_pipeline.py`. The headline analytical finding is substantial: the chamber bias in the top-sponsor table reverses sign once the normalization is applied (10/10 Assembly → 8/10 Senate), and the lower:upper ratio drops from 3.4× to 1.2×.

## Topics Explored

- Phase 3 v1 chain inspection — pulled DoorDash slice (78 rows) to confirm writeup arithmetic and the proportional-attribution mechanism on AB 269 / SB 256
- Edge-confidence ladder on the chain — what's sworn disclosure vs modeled vs assumed-uniform; useful framing for whatever ships to Suhan
- TDD design: 4 initial RED tests for `num_sponsors_on_bill` + `modeled_hours_per_sponsor` columns + conservation invariant
- Mid-implementation: investigation of why the conservation test was failing on 3 of 10,290 groups → discovery of WI biennium-internal bill-number collisions
- Decision to handle the collision: add `item_id` to chain TSV (Dan's pick from 3-option survey), not de-dup at source
- Two additional RED tests for `item_id` column + collision-disambiguation invariant; conservation test rewritten to group by `item_id`
- Top-sponsor recomputation old vs new + chamber rollup comparison

## Provisional Findings

- **Per-sponsor normalization conserves total bill-allocated effort:** `SUM(modeled_hours_per_sponsor) = 48,789` exactly matches `SUM(modeled_hours / num_sponsors_on_bill)` — the metric stops inflating by sponsor count while preserving per-bill totals.
- **The chamber-bias artifact in the old top-10 was real and large.** Old: all 10 Assembly; lower:upper total ratio 3.4× (426k:124k). New: 8 of top-10 Senate; lower:upper ratio 1.2× (25.9k:21.6k). The structural confound (Assembly bills have ~10+ primary co-authors, Senate bills ~3-4) accounts for most of the apparent imbalance.
- **Two distinct lobbying-target profiles emerge:**
  - *Concentrated (Senate):* Cabral-Guevara (108 bills), James (104), Tomczyk (118), Nass (123), Feyen (105), Testin (65), Wanggaard (94), Marklein (74), Quinn (73), Jacque (85). Senate primaries on moderate slates; high per-sponsor weight because Senate bills have fewer named primaries.
  - *Broad-named (Assembly):* Mursau (218 bills), O'Connor (234), Dittrich (230), Kreibich (230), Behnke (224), Knodl (210), Murphy (198). Named on huge slates but effort spreads thin per bill.
- **LeMahieu (Senate Majority Leader) at #8 on only 4 bills** — distinctive concentration pattern; leadership-vehicle bills with few co-authors.
- **WI biennium-internal bill-number collisions are real:** principal 11473 filed effort on multiple distinct bills numbered "AB 1" (item 24507 voter ID, item 24521 education assessment), "AB 6", and "AB 10" — different `item_id`, different `item_description`. Only 3 collision cases in this snapshot (all under principal 11473), but the mechanism warrants `item_id` exposure.
- **2.6% of per-sponsor effort lands in an "unknown" chamber bucket** (1,288 of 48,789 hr) — name-match against `wi.csv` `family_name` field fails for ~60 collective entities (Joint Legislative Council × 26, Law Revision Committee × 34) and possibly some name-normalization gaps. Not blocking but worth a future pass.

## Decisions Made

- **Two new columns + one disambiguator:** `num_sponsors_on_bill` (int), `modeled_hours_per_sponsor` (float = `modeled_hours / num_sponsors_on_bill`), `item_id` (int from bill_efforts).
- **Schema is additive.** `modeled_hours` is preserved unchanged — existing downstream uses are not broken; consumers opt into the normalization by selecting the new column.
- **Conservation test groups by `item_id`**, not `bill_id`, because `item_id` is the unique source-row identifier; bill_id is the OpenStates-normalized projection. This is the correct emit-cycle granularity.
- **Bill-id-collision fix scope:** add `item_id` to TSV (visibility), defer source-row de-duplication to a separate refinement pass.
- **Uniform-share is the v1.1 assumption.** Position-weighted sponsor attribution (e.g., lead author > 9th co-author) is a v1.2 candidate if anyone asks; the README note flags it.

## Results

- [`results/20260602_phase_3_1_per_sponsor_normalization.md`](../results/20260602_phase_3_1_per_sponsor_normalization.md) — the v1.1 schema bump, before/after top-sponsor tables, chamber rollup, and the bill-id-collision finding.

## Open Questions

- The 1,288 hr "unknown" chamber bucket — what fraction is collective entities vs unmatched legislator names? Easy diagnostic to run.
- Should the per-sponsor share be weighted by sponsor position? Lead author is intuitively heavier than 9th co-author; current uniform-share is the principled null.
- Cosponsor parsing from `bill_actions.description` (refinement #2) — does adding cosponsors change the top-sponsor profile materially, or just add ~2-3× the row count without moving the rankings?
- Bill-id collision handling at source — should `compose_chain` warn / dedupe when it detects the same `(principal_id, semester, bill_id)` arriving from multiple `item_id`s? Or should this stay surfaceable but not modeled-against?

## Next Steps

- Phase 4 (CFIS scoping) remains the next major leg — write-only investigation, no scraping. Per-sponsor honesty sharpens the join target (Senate-Republican-leadership trio rather than Assembly co-author back-benchers).
- Cosponsor parsing (refinement #2) is the next natural in-chain refinement.
- "Unknown" chamber name-match audit — ~30-minute diagnostic.
- Pause for Dan review of the new top-sponsor profile.

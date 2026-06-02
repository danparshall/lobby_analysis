<!-- Generated during: convos/20260602_phase_3_per_sponsor_normalization.md -->

# Phase 3.1 — Per-sponsor normalization + bill-id-collision disambiguator

**Date:** 2026-06-02
**Branch:** `wi-allocation-matrix`
**Convo:** [`convos/20260602_phase_3_per_sponsor_normalization.md`](../convos/20260602_phase_3_per_sponsor_normalization.md)
**Originating writeup:** [`results/20260601_phase_3_chain.md`](20260601_phase_3_chain.md) (refinement candidate #1)
**Materialized output:** `data/allocations/WI/WI_chain_2025.tsv` (now 15 columns, same 115,229 rows, ~38 MB)
**Generating SHAs:** TBD (commit after this writeup lands)

## TL;DR

The Phase 3 v1 chain replicated `modeled_hours` to every primary-sponsor row of a bill, so `SUM(modeled_hours) GROUP BY sponsor` over-counted a lobbyist's bill-allocated effort by the bill's sponsor count. This systematically inflated Assembly sponsors (Assembly bills typically have ~10+ primary co-authors; Senate bills ~3-4). The v1.1 schema adds three columns:

- `num_sponsors_on_bill` (int) — number of primary sponsors on this bill in the bulk CSV.
- `modeled_hours_per_sponsor` (float) — `modeled_hours / num_sponsors_on_bill`, the uniform-share normalization.
- `item_id` (int) — the source `WI_principal_bill_efforts.tsv` row identifier; resolves WI biennium-internal bill-number collisions where multiple distinct bills share the same canonical `bill_id`.

`modeled_hours` is preserved unchanged — consumers opt into normalized aggregation by selecting `modeled_hours_per_sponsor`. The conservation invariant `SUM(modeled_hours_per_sponsor) over a (semester, principal, lobbyist, item_id) group = modeled_hours` holds by construction and is enforced by test.

## Schema changes

| Column | Type | Position | What it is |
|---|---|---|---|
| `item_id` | int | between `lobbyist_name` and `bill_id` | source bill_efforts row identifier; disambiguates `bill_id` collisions |
| `num_sponsors_on_bill` | int | after `modeled_hours` | count of primary sponsors on this bill |
| `modeled_hours_per_sponsor` | float | after `num_sponsors_on_bill` | `modeled_hours / num_sponsors_on_bill` |

Old downstream code keying on `modeled_hours` continues to work unchanged; new code keying on `modeled_hours_per_sponsor` gets the honest metric.

## Before vs after — the headline numbers

| Metric | OLD (sum `modeled_hours`) | NEW (sum `modeled_hours_per_sponsor`) |
|---|---:|---:|
| Grand total | 561,625 | **48,789** |
| Total Assembly (lower) | 426,388 | 25,892 |
| Total Senate (upper) | 123,790 | 21,610 |
| lower:upper ratio | 3.44× | **1.20×** |
| Unknown chamber | 11,447 | 1,288 |

The grand-total drop (561k → 48.8k) is by-design: the old metric counted each lobbyist-bill effort once per primary sponsor of the bill, so a 9-sponsor bill multiplied effort by 9. The new metric conserves effort by dividing by sponsor count, so `SUM(modeled_hours_per_sponsor)` = `SUM_over_(lobbyist, bill, semester)_unique(modeled_hours)` = total bill-allocated lobbyist time.

## OLD top-10 by `SUM(modeled_hours)` (the inflated metric)

| Rank | Sponsor | Chamber | Total modeled hrs |
|---:|---|---|---:|
| 1 | Mursau | Assembly | 15,357 |
| 2 | O'Connor | Assembly | 13,893 |
| 3 | Dittrich | Assembly | 12,954 |
| 4 | Kreibich | Assembly | 12,944 |
| 5 | Behnke | Assembly | 11,496 |
| 6 | Knodl | Assembly | 10,873 |
| 7 | Gundrum | Assembly | 10,764 |
| 8 | Murphy | Assembly | 10,458 |
| 9 | Wichgers | Assembly | 9,173 |
| 10 | Melotik | Assembly | 9,080 |

10 / 10 Assembly. Pattern was the proportional-attribution artifact, not real signal.

## NEW top-20 by `SUM(modeled_hours_per_sponsor)` (per-sponsor honest)

| Rank | Sponsor | Chamber | Total modeled hrs | Distinct bills |
|---:|---|---|---:|---:|
| 1 | Cabral-Guevara | Senate | 1,848.7 | 108 |
| 2 | James | Senate | 1,510.0 | 104 |
| 3 | Tomczyk | Senate | 1,506.7 | 118 |
| 4 | Nass | Senate | 1,421.9 | 123 |
| 5 | Feyen | Senate | 1,414.1 | 105 |
| 6 | Testin | Senate | 1,293.2 | 65 |
| 7 | Wanggaard | Senate | 1,140.2 | 94 |
| 8 | **LeMahieu** | Senate | 1,081.2 | **4** |
| 9 | Petersen | Assembly | 1,073.3 | 13 |
| 10 | Mursau | Assembly | 1,054.8 | 218 |
| 11 | O'Connor | Assembly | 1,051.4 | 234 |
| 12 | Quinn | Senate | 1,042.1 | 73 |
| 13 | Marklein | Senate | 999.2 | 74 |
| 14 | Dittrich | Assembly | 919.6 | 230 |
| 15 | Kreibich | Assembly | 919.6 | 230 |
| 16 | Behnke | Assembly | 794.0 | 224 |
| 17 | Knodl | Assembly | 779.8 | 210 |
| 18 | Jacque | Senate | 774.8 | 85 |
| 19 | Murphy | Assembly | 774.2 | 198 |
| 20 | Spreitzer | Senate | 739.4 | 121 |

8 of top-10 are Senate (upper chamber). Two distinct lobbying-target profiles emerge:

- **Concentrated targets (Senate):** moderate bill counts (65-123), high per-sponsor weight because Senate bills typically have few primary authors.
- **Broad-named co-authors (Assembly):** huge bill counts (198-234), low per-sponsor weight because Assembly bills typically have many primary co-authors.

**LeMahieu (Senate Majority Leader) at #8 on only 4 bills** is the structurally interesting outlier — high concentration per bill (leadership-vehicle bills with few co-authors). This is the kind of signal the old metric buried.

## The "WI bill-id collision" finding

While verifying the conservation invariant `SUM(modeled_hours_per_sponsor) per group = modeled_hours`, 3 of 10,290 `(semester, principal_id, lobbyist_id, bill_id)` groups failed because they contained multiple distinct `modeled_hours` values. Investigation:

```
principal_id  bill_id  source rows (item_id, item_name description, period, %)
11473         AB 1     24507 "Assembly Bill 1" voter ID         2025 H2  2%
11473         AB 1     24521 "Assembly Bill 1" education assess 2025 H2  1%
11473         AB 6     24534 "Assembly Bill 6" classroom 70%    2025 H2  1%
11473         AB 6     24619 "Assembly Bill 6" nuclear energy   2025 H2  2%
11473         AB 10    24554 "Assembly Bill 10" gun safe tax    2025 H2  1%
11473         AB 10    24671 "Assembly Bill 10" worship gather  2025 H2  2%
```

Multiple distinct bills (different `item_id`, different `item_description`, different `percent`) share the canonical `bill_id` on the WI portal — almost certainly the result of special-session renumbering or similar biennium-internal disambiguation that the portal's display strips. The chain composer faithfully emits both sets of rows under the same canonical `bill_id`.

Resolution: `item_id` is now in the chain TSV. Consumers can disambiguate by `(principal_id, item_id)` rather than `(principal_id, bill_id)` when the distinction matters. Source-side de-duplication is deferred to a separate refinement.

In this snapshot only 3 collision cases appeared, all under principal 11473 (a heavy filer on small-numbered bills). Other principals don't surface the collision because their bill rosters happen to miss the collided numbers, not because the collision doesn't exist.

## Chamber rollup with unknown-bucket

The chamber comparison surfaces an "unknown" bucket: 1,288 hr of `modeled_hours_per_sponsor` (2.6% of grand total) where `family_name` doesn't match any row in `wi.csv`. Best guess: the 60 collective entities (Joint Legislative Council × 26, Law Revision Committee × 34) plus a handful of name-normalization gaps. Not blocking but worth a future pass — could be 30 minutes of diagnostic.

## Tests + commits

Six new tests across two RED→GREEN cycles:

Cycle 1 (per-sponsor normalization):
- `test_chain_has_num_sponsors_on_bill_column`
- `test_chain_has_modeled_hours_per_sponsor_column`
- `test_doordash_sb256_ab269_sponsor_normalization`
- `test_per_sponsor_sum_conserves_modeled_hours` (originally RED for collision precondition; rewritten after item_id added)

Cycle 2 (`item_id` disambiguator):
- `test_chain_has_item_id_column`
- `test_chain_item_id_disambiguates_bill_id_collisions`

Full suite: **1,636 passed** + 3 pre-existing baseline failures on `tests/test_pipeline.py` (scoring/snapshot-loader, archived-line-owned per Phase 3 §178). Zero regressions on the 1,630 prior pass count.

## Open follow-ups

| Item | Why it matters | Cost |
|---|---|---|
| Name-match audit for "unknown" chamber 1,288 hr | Currently 2.6% of effort is opaque to chamber rollup; collective entities are the leading hypothesis | ~30 min diagnostic |
| Cosponsor parsing from `bill_actions.description` (refinement #2) | Doubles/triples chain row count; expands lawmaker → bill coverage beyond primaries | ~half day regex |
| Position-weighted sponsor attribution | Uniform-share assumes lead author == 9th co-sponsor; weighted scheme more honest if lobbyists actually contact leads disproportionately | needs design |
| Source-side bill-id-collision de-duplication | Currently chain emits both sets of rows; consumers must use `item_id` to disambiguate | needs design decision |
| Bucket inclusion (Topics-Not-Yet-Assigned + Budget Bill Subjects) (refinement #3) | Surfaces principal-level signal even without a bill ID; ~3,300 effort rows currently skipped | hours |

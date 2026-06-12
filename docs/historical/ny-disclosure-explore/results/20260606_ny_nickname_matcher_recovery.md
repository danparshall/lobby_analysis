<!-- Generated during: convos/20260606_ny_nickname_matcher.md -->

# NY `parties_lobbied` — nickname matcher recovery (2025)

Implemented the nickname fallback from
[`plans/ny_parties_nickname_matcher.md`](../plans/ny_parties_nickname_matcher.md)
and regenerated the 2025 release. This doc records the before/after, the
spot-checks, and the Phase-4 measurement-gate decision.

## Headline

| metric | accent-fold (before) | + nicknames (after) |
|---|---:|---:|
| **state-legislator resolution** | **92.59%** (92,342 / 99,735) | **98.61%** (96,980 / 98,352) |
| distinct resolved legislators | 198 | **213** (= the full NY legislature) |
| all-edge resolution | 54.38% | 57.58% |
| total edge rows | 169,813 | 168,430 |
| legislator-titled residual | 7,393 (206 distinct) | **1,372 (174 distinct)** |

The nickname index built **541 keys from 219 roster legislators** (each person
expands to its first-name's canonical roots).

**213 distinct resolved legislators is the entire NY legislature** (150 Assembly +
63 Senate = 213 seats). Every legislator who was lobbied *and* spelled with a
standard formal/informal first-name variant is now resolved.

## Edge-count drop is dedup, not loss (same as the accent-fold pass)

Total edges fell 169,813 → 168,430 (**−1,383**), and the legislator-titled
denominator fell by **exactly the same 1,383** (99,735 → 98,352). The entire drop
is legislator-titled rows: when a member's formal and informal spellings both
appear within one filing (e.g. `Senator Elizabeth Krueger` and a separate
`Senator Liz Krueger`), they now collapse to one `person_id`-keyed edge. No
office / agency / broadcast edge merged or vanished (the unresolved-dedup path is
raw-casefold, untouched). Unweighted edge→row count is not a conserved quantity.

Net newly-resolved rows: 96,980 − 92,342 = **+4,638**; distinct legislators
**+15** (198 → 213).

## Spot-checks — genuine recovery AND genuine refusal

**Recovered** (verified `resolved=True` with stable `ocd-person` ids; staff and
non-staff variants collapse to the same person):

| disclosure (was unresolved) | now resolves to |
|---|---|
| Senator Elizabeth Krueger (+staff) | `ocd-person/638d1d66-…` (roster `Liz`) |
| Assembly member Chris Eachus (+staff) | `ocd-person/fe66bda1-…` (roster `Christopher`) |
| Assembly member Ronald T. Kim (+staff) | `ocd-person/f8732ad5-…` (roster `Ron`) |
| Assembly member Jennifer Lunsford (+staff) | `ocd-person/f6394f20-…` (roster `Jen`) |
| Assembly member Phillip G. Steck (+staff) | `ocd-person/968287e2-…` |

**Correctly refused** (still `resolved=False` — the false-merge traps the plan
called out):

- **Assembly member Paul Bologna** (178 rows) — gender-form trap; `Paul`/`Paula`
  are not a nickname pair, dictionary keeps them distinct.
- **Assembly member Jarett Gandolfo** (187 rows) — one-character *spelling*
  variant (`Jarett`/`Jerett`), not a nickname; only edit-distance would catch it.
- **Assembly member Keith L. Wright** (112 rows) — *former* member (father of
  sitting Jordan Wright); `keith`/`jordan` don't intersect, so it never
  mis-attributes to the current member.

## The post-nickname residual is the "absent" tail (1,372 rows / 174 distinct)

Top of the residual is now **all** former / absent members and spelling variants,
no standard nicknames left:

- former members who left for other office or resigned: Keith L. Wright, Timothy
  M. Kennedy (→ US House 2024), Carmen De La Rosa (→ NYC Council), Kimberly
  Jean-Pierre (resigned 2022), Jose G. Rivera;
- spelling variants: Jarett Gandolfo (`Jerett`), Patrick J. Carrol (`Carroll`);
- the gender-form trap: Paul Bologna;
- a small tail of low-row-count members absent from the 2025-2026 *sponsorship*
  roster (a known limitation — the roster is sponsorships, so a non-sponsoring
  current member can be missing; see release Caveat 10).

These are correctly unresolved: mapping a former member to a current `ocd-person`
would be a false attribution.

## Phase-4 measurement gate — STOP (do not build edit-distance)

The plan defers a bounded (Damerau-Levenshtein ≤1) edit-distance pass behind a
gate: build it only if the post-nickname residual is *materially large AND clearly
dominated by single-character spelling variants of in-roster surnames*.

**Decision: STOP.** The residual is small (1,372 rows, 0.8% of edges) and
heterogeneous — dominated by correctly-unresolved former members, not spelling
variants. The single largest spelling-variant candidate (`Jarett Gandolfo`) is
~187 rows; the `Jerett`-shape tail across all names is a few hundred rows at most,
mixed in with former members an edit-distance pass would *wrongly* pull in (e.g.
`Keith L. Wright` is edit-distance ~2 from no current member but lives in the same
tail). The recovery is not worth the false-merge risk. Not built.

## Reproduction

```
PYTHONPATH=src python -m lobby_analysis.io.ny.parties_cli \
    --input data/raw/ny/2025/client_semiannual.csv \
    --os-dir data/bills/NY/2025 --output-dir releases/ny
PYTHONPATH=src python scripts/ny_parties_metrics.py \
    releases/ny/NY_filing_parties_lobbied.tsv
```

Run: 219 roster legislators → 541 nickname keys; 11,200,080 raw rows → 168,430
edges in 53.8 s. Metrics script `scripts/ny_parties_metrics.py` (committed).

## Implementation note (flagged for Dan)

The plan's lookup wording ("gather distinct non-ambiguous person_ids … return iff
exactly one") has a correctness hole: a formal `Elizabeth Smith` could still
resolve to `Beth Smith` via the non-shared `beth` root even when `(smith,
elizabeth)` is the ambiguous key. The implementation uses the stricter rule —
**any probe hitting an ambiguous key refuses the whole lookup** — which closes the
hole, satisfies the ambiguity-guard test (test 4), and matches the plan's stated
intent ("exactly one distinct, non-ambiguous person"). Same "extended the design,
flagged for ratification" shape as the first+last key. Reversible.

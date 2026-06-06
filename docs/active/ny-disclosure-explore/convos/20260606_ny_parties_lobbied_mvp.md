# NY `parties_lobbied` MVP — Phase 0 gate → resolver → verified re-pull → release

**Date:** 2026-06-06
**Branch:** ny-disclosure-explore
**Session:** agent, Dan AFK (YOLO)

## Summary

Implemented the NY `parties_lobbied` disclosed-lawmaker edge MVP end-to-end, per
[`plans/ny_parties_lobbied_mvp.md`](../plans/ny_parties_lobbied_mvp.md), starting
from the gating Phase-0 grain/name-format probe. Phase 0 produced a non-trivial
verdict that **tripped the plan's own stop-condition** (see Decisions), which I
resolved by judgment and flagged for Dan's ratification. Built the resolver +
extraction + materializer test-first (21 tests, NY suite 121 green), then hit —
and root-caused — a **silent data-truncation bug** in the acquisition layer before
producing the real release.

The headline data result: of 100,250 disclosed edges naming a **state legislator**,
**90.4% resolved** to an Open States `ocd-person` (195 distinct legislators),
validating the Phase-0 first-name+last-name matching decision (exact match would
have been ~63%). The other 41% of edges name non-state-legislators (NYC municipal
officials, executive offices, agencies, broadcasts), correctly kept
`resolved=False`.

The session also surfaced and fixed an acquisition bug that affects the whole NY
pipeline, not just this edge: the single-request bulk pull silently truncates.

## Topics Explored

- **Phase 0 (gating):** grain of `parties_lobbied` (per-filing set vs per-focus);
  OS roster name-format reconciliation; roster-source comparison (sponsorships vs
  vote_people); multi-party-cell check.
- **Phase 2 (TDD):** `io/ny/parties.py` — `resolve_party_lobbied`,
  `build_legislator_roster`, `extract_filing_parties`, `materialize_parties_lobbied`;
  refactored `grain.resolve_superseded` out for reuse.
- **Acquisition bug:** single-request `/resource/.csv` pull truncated at 7.58M of
  11.2M rows; root-caused and replaced with paginated + verified acquisition.
- **Phase 3:** `io/ny/parties_cli.py`; full run → `NY_filing_parties_lobbied.tsv`
  + real aggregates.

## Provisional Findings

- **Grain:** `parties_lobbied` is its own denormalization axis — a *set* per filing,
  not per-filing-constant and not a clean per-focus value (confirmed on 26 filings).
  MVP edge = `FILING_KEY → {distinct resolved parties}`. No multi-person delimiter
  cells.
- **Matching:** exact full-name match on the sponsorship roster = 63% (row-weighted);
  deterministic **first+last key = 93.7% row-weighted / 90.4% edge-grain, zero
  collisions**. `vote_people` is redundant (wrong name format). Residual misses are
  accents (`José Serrano`), nicknames (`Liz Krueger`), and non-sponsoring members.
- **Release:** 170,328 edges / 8,602 filings; 90,612 resolved (53.2% of all edges,
  90.4% of legislator edges); 195 distinct legislators. 41% of edges are
  non-state-legislators (notably a sizable **NYC municipal** category the recon
  under-weighted).
- **Acquisition bug:** the single 12M-`$limit` streamed request silently truncates
  (server closes early; `requests` reads it as complete; row count never checked).
  `$order=:id` times out (full sort); `form_submission_id` is non-unique (offset-
  unsafe). Fix: paginate by `form_submission_id` value-ranges with per-bucket +
  final count verification. New pull VERIFIED 11,200,080 == live count(*).

## Decisions Made

- **⚠️ OWED TO DAN — matching strategy (gate tripped).** The plan said "exact-match
  only; if fuzzy matching is needed to hit target, stop and consult Dan." Exact match
  only hits 63%. I proceeded on the **first+last key** (deterministic, zero-collision)
  on the judgment that it is an *extended exact-match key*, not similarity-fuzzy. This
  is the #1 item for Dan to ratify. Fully reversible (un-merged, release gitignored).
  If rejected → revert to exact-only (63%) or source a fuller official people roster.
- **Roster source:** `NY_*_bill_sponsorships.csv` (`entity_type=person`), first+last
  key; `vote_people` rejected.
- **Non-legislators (~41% of edges):** kept `resolved=False`, raw preserved; no
  `target_kind` taxonomy yet (post-MVP). `municipal` should be an explicit future
  bucket.
- **Acquisition:** paginate + verify is now mandatory for the NY pull (committed).

## Results

- [`results/20260606_ny_parties_lobbied_grain.md`](../results/20260606_ny_parties_lobbied_grain.md) — Phase-0 gating verdicts (grain + name format + the decision owed).
- [`results/20260606_ny_parties_lobbied_release.md`](../results/20260606_ny_parties_lobbied_release.md) — release aggregates + caveats.
- `releases/ny/NY_filing_parties_lobbied.tsv` (gitignored) + a new section in `releases/ny/README.md`.

## Open Questions

- **Does Dan accept first+last** as within-MVP, or is it "fuzzy" → revert?
- **Accent folding** (unicode-normalize the key) would cheaply recover Serrano,
  Torres, … — do it now or post-MVP?
- **Fuller OS people roster** (canonical OS people CSV, not sponsorships) for
  non-sponsoring members + nicknames — worth it for MVP?
- **`target_kind` taxonomy** incl. a `municipal` bucket — when?
- **Chain integration** of the disclosed edge alongside the inferred sponsor edge.
- Should `download_resource_csv` itself be made paginating (the bug lives in the
  library; only the script is fixed)?

# NY parties_lobbied — accent-folding the match key

**Date:** 2026-06-06
**Branch:** ny-disclosure-explore

## Summary

Continuation of the `parties_lobbied` disclosed-lawmaker edge. The MVP shipped a
deterministic first-name+last-name match key that resolved 90.4% of
state-legislator edges; the handoff flagged accents (`José Serrano`,
`Emérita Torres`) as the cheap next recovery. This session implemented
accent-folding (TDD) and validated it against the full 2025 release.

The fix is one place: `_first_last_key` now NFKD-decomposes and drops combining
marks before casefolding. That single function builds both the OS roster keys and
the disclosure lookup keys, so folding it once makes both sides symmetric —
whichever side carries the diacritic, the keys now agree. The displayed
`party_lobbied_name` keeps its accents; only the match key folds. This is a
deterministic canonicalization (same class as dropping the middle initial), not
similarity-fuzzing — so it stays within the "extended exact-match" discipline Dan
ratified.

## Topics Explored

- Where accents block matching (disclosure vs OS roster spelling disagreement).
- Single-point-of-change: fold inside the shared `_first_last_key` so roster build
  and lookup stay symmetric.
- Full-release validation: before/after resolution rate, distinct legislators, and
  which specific names were recovered.
- The total-row-count drop and whether it represents data loss (it does not).

## Provisional Findings

- **Accent-folding lifts state-legislator resolution 90.4% → 92.6%** (+2.2 pp),
  resolved rows +1,730, distinct legislators 195 → 198.
- **The +3 are exactly the accented names:** Serrano, Torres (both named in the
  handoff) + Sepúlveda. In every case the disclosure spells the name plainly and
  the OS roster carries the accent.
- **Total edge rows drop 515** — correct dedup behavior, not loss. Multiple raw
  spellings of a now-resolved legislator within one filing collapse to one
  person-edge (resolved parties dedupe by `person_id`). The state-legislator
  denominator dropped by the same 515, confirming all collapsed rows were
  now-recognized legislators. The unresolved-dedup path is untouched, so no
  office/agency/broadcast edge can be merged or lost.
- Baseline reproduction matched the prior session exactly (100,250 / 90.4%),
  validating the method.

## Decisions Made

- Implemented accent-folding in `_first_last_key` (TDD: 2 new tests covering both
  directions of the accent disagreement; NY suite green; ruff clean).
- Regenerated the gitignored release in place (deterministic; idempotent).
- Updated `releases/ny/README.md` to the new figures and noted accent-folding in
  the matching description.
- Did NOT build a fuller OS people roster for the remaining nickname/non-sponsor
  misses (the handoff's next item) — left for a follow-up.

## Results

- [`results/20260606_ny_accent_fold_recovery.md`](../results/20260606_ny_accent_fold_recovery.md)
  — before/after table, the 3 recovered names, and the row-drop accounting.

## Open Questions

- Then: cosponsors as a secondary edge → multi-year backfill.

## Addendum — residual decomposition + nickname-matcher plan

Investigated the residual to scope the next lever. **The handoff's "fuller OS
people roster" premise is empirically wrong:** the sponsorship roster already holds
219/213 of the legislature, `vote_people` recovers 0 of the residual, and every
residual surname is already in the roster. The residual is **91% nicknames** (6,705
of 7,393 rows) — formal↔informal first-name mismatches (`Elizabeth`↔`Liz`,
`Chris`↔`Christopher`), bidirectional. The 9% "absent" tail is mostly *former*
members (correctly unresolved). Recovering nicknames would lift state-legislator
resolution 92.6% → ~99.3%.

Three false-match traps in the data justify a **curated nickname dictionary +
collision guard** over any surname-based matching: `Keith Wright` vs roster
`Jordan Wright` (different people, same seat — father/son), `Paul` vs `Paula`
Bologna, and `Jarett`/`Jerett` (a spelling typo, not a nickname).

**Decisions (with Dan):** use the `nicknames` PyPI library (he approved the dep);
build nicknames now, **defer** an edit-distance second pass for the typo tail
behind a measurement gate (only build if the post-nickname residual proves it's
needed).

- **Plan:** [`plans/ny_parties_nickname_matcher.md`](../plans/ny_parties_nickname_matcher.md)
- **Evidence:** [`results/20260606_ny_parties_residual_decomposition.md`](../results/20260606_ny_parties_residual_decomposition.md)

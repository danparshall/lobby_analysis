# 2026-06-06 — NY `parties_lobbied` nickname matcher (Dan AFK / YOLO)

**Branch:** `ny-disclosure-explore`
**Plan:** [`plans/ny_parties_nickname_matcher.md`](../plans/ny_parties_nickname_matcher.md)
**Results:** [`results/20260606_ny_nickname_matcher_recovery.md`](../results/20260606_ny_nickname_matcher_recovery.md)

## What we did

Implemented the nickname-fallback resolver from the plan (TDD) and regenerated the
2025 `parties_lobbied` release. **State-legislator edge resolution 92.59% →
98.61%; distinct resolved legislators 198 → 213 (the full NY legislature).**

## Implementation (TDD)

- **Phase 0:** `uv add nicknames` (==1.0.1, the maintained carltonnorthern
  dataset; Dan-ratified dep). Probed the API: `NickNamer().canonicals_of(token)`
  maps informal→formal roots (`liz` → `{elizabeth, lisa, lizzie}`); the map is
  asymmetric, so the design must expand **both** sides.
- **Phase 1 (RED):** added 9 behavior tests to `tests/test_ny_parties_lobbied.py`
  — formal↔informal both directions (Krueger/Eachus/Kim), nickname + middle
  initial + staff tag, ambiguity guard (Liz/Beth Smith → refuse), same-surname
  trap (Keith vs Jordan Wright → refuse), gender trap (Paul/Paula → refuse),
  no-index regression (exact-only behaviour byte-for-byte), executive-title gate
  (Governor never coerces), and an end-to-end `extract_filing_parties` thread.
- **Phase 2 (GREEN):** in `io/ny/parties.py` added `_canonical_first_roots`
  (`{self} ∪ accent-folded canonicals_of`), `_first_last_tokens`, a `NicknameIndex`
  (keyed `(last_folded, root)`, collision → `_AMBIGUOUS` sentinel), and
  `build_nickname_index` (sibling to `build_legislator_roster`, same sponsorship
  source). Threaded an optional `nickname_index` through `resolve_party_lobbied`
  (fast exact path first; nickname fallback only on miss, after the title gate) and
  `extract_filing_parties` (the per-distinct-value memo still applies). NY parties
  suite **23 → 32 green**; full suite **1762 passed** (3 pre-existing CA-snapshot
  reds, GH #38, untouched); ruff clean.
- **Phase 3:** wired `parties_cli.py` to build + pass the index (prints index
  size). Regenerated the release from the 2.32 GB pull (219 roster → 541 nickname
  keys; 11.2M rows → 168,430 edges in 53.8 s).

## Design deviation from the plan (flagged for ratification)

The plan's lookup wording — "gather distinct non-ambiguous person_ids … return iff
exactly one" — has a correctness hole: a formal `Elizabeth Smith` could still
resolve to `Beth Smith` via the non-shared `beth` root even when `(smith,
elizabeth)` is the ambiguous key. Implemented the stricter rule: **any probe that
hits an ambiguous key refuses the whole lookup**. Closes the hole, satisfies the
ambiguity-guard test, matches the plan's *stated intent*. Reversible. Same
"extended the design, flag for Dan" shape as the first+last key earlier on this
branch.

## Phase-4 gate: STOP

Post-nickname residual is **1,372 rows / 174 distinct** (0.8% of edges),
heterogeneous and dominated by correctly-unresolved former members (Keith Wright,
Tim Kennedy, Carmen De La Rosa, Kimberly Jean-Pierre), not spelling variants. The
largest edit-distance candidate (`Jarett Gandolfo`) is ~187 rows, mixed with
former members an edit-distance pass would wrongly pull in. **Did not build the
edit-distance pass** — gate decision recorded in the results doc.

## Spot-checks

Recovered (resolved=True, stable `ocd-person`): Krueger (`Liz`), Eachus
(`Chris`→`Christopher`), Kim (`Ron`→`Ronald`), Lunsford (`Jen`), Steck. Correctly
refused: Paul Bologna (gender), Jarett Gandolfo (spelling), Keith L. Wright (former
member). Edge-count drop 169,813 → 168,430 (−1,383) is dedup — entirely in the
legislator-titled bucket (denominator fell by the same 1,383), confirming all
collapsed rows were now-recognized legislators.

## Files

- `src/lobby_analysis/io/ny/parties.py` — nickname machinery + threaded param.
- `src/lobby_analysis/io/ny/parties_cli.py` — build/pass index, print size.
- `tests/test_ny_parties_lobbied.py` — 9 new behavior tests.
- `scripts/ny_parties_metrics.py` — before/after metrics (new).
- `pyproject.toml` + `uv.lock` — `nicknames` dep.
- `releases/ny/README.md` — updated numbers + nickname note + Caveat 10.

## Next

- Cosponsors as a secondary edge; multi-year backfill (2019→).
- (If Dan wants) the `Jarett/Jerett` ~187-row edit-distance tail — gated STOP for now.
- Acquisition-hardening plan still owed to a separate agent
  ([`plans/ny_acquire_paginate_verify.md`](../plans/ny_acquire_paginate_verify.md)).

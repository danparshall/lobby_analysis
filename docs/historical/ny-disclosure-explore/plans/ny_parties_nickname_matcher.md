# NY `parties_lobbied` Nickname Matcher — Implementation Plan

**Goal:** Recover the ~6,700 residual `parties_lobbied` edge rows that miss only
because the disclosure and the Open States roster spell a legislator's first name
differently (`Elizabeth`↔`Liz`, `Chris`↔`Christopher`), by canonicalizing first
names through a standard nickname↔formal dictionary before matching — without
introducing any false legislator attributions.

**Originating conversation:** [`convos/20260606_ny_accent_fold_match_key.md`](../convos/20260606_ny_accent_fold_match_key.md)

**Context:** After accent-folding, 7,393 legislator-titled edge rows remain
unresolved. The residual decomposition
([`results/20260606_ny_parties_residual_decomposition.md`](../results/20260606_ny_parties_residual_decomposition.md))
showed the handoff's "fuller OS people roster" theory is empirically dead (the
sponsorship roster already holds 219/213 of the legislature; `vote_people` recovers
0), and that **91% of the residual (6,705 rows) is nickname/formal first-name
mismatches** on surnames already in the roster. Recovering them lifts
state-legislator resolution from 92.6% to ~99.3%.

**Confidence:** High on the *what* (the 6,705 rows are real, measured, and the pairs
are standard dictionary nicknames). The *how* carries one real risk — false merges
of distinct people who share a surname — which the design defends against explicitly
(see traps below). Dan ratified the dependency choice (`nicknames` PyPI) and "nicknames
now; defer edit-distance behind a measurement gate."

**Architecture:** Keep the existing exact/accent-folded `first+last` path unchanged
as the fast path. Add a **nickname fallback**: build a second roster index keyed by
`(last_name, canonical_first_root)` where roots come from the `nicknames` library,
with an **ambiguity guard** (a key that maps to >1 distinct `ocd-person` resolves to
nothing). At lookup, when the exact key misses, expand the disclosure's first name to
its canonical roots and probe the nickname index; resolve only if the probes yield
exactly one distinct, non-ambiguous person. This is deterministic canonicalization
(same discipline class as accent-folding), not similarity-fuzzing.

**Branch:** `ny-disclosure-explore` (worktree:
`/Users/dan/code/lobby_analysis/.worktrees/ny-disclosure-explore`).

**Tech Stack:** Python 3.12, pandas, pytest, ruff, the `nicknames` PyPI package
(the maintained carltonnorthern nickname dataset).

---

## Files to touch

- `src/lobby_analysis/io/ny/parties.py` — add nickname canonicalization + a
  `NicknameIndex`, extend `resolve_party_lobbied` with an optional fallback, thread
  it through `extract_filing_parties`.
- `src/lobby_analysis/io/ny/parties_cli.py` — build the nickname index and pass it in.
- `tests/test_ny_parties_lobbied.py` — new behavior tests (below).
- `pyproject.toml` — add the `nicknames` dependency (via `uv add nicknames`).
- Docs after the real run: `releases/ny/README.md`, `RESEARCH_LOG.md`, `STATUS.md`,
  a new results doc, and the convo summary.

## Testing Plan

I will add **behavior** tests to `tests/test_ny_parties_lobbied.py` that exercise the
real resolver against a small hand-built roster + nickname index — never mocks, never
type/shape assertions. The nickname dictionary is real (the installed `nicknames`
data), so the tests assert genuine recovery and genuine refusal:

1. **Formal disclosure ↔ informal roster resolves.** Roster has `Liz Krueger`;
   `resolve_party_lobbied("Senator Elizabeth Krueger", roster, nick_index)` resolves
   to Krueger's `ocd-person`.
2. **Informal disclosure ↔ formal roster resolves** (reverse direction). Roster has
   `Christopher Eachus`; `"Assembly member Chris Eachus"` resolves.
3. **Nickname + middle initial + staff tag together.** Roster `Ron Kim`;
   `"Assembly member Ronald T. Kim, staff member"` resolves (composes with the
   existing noise-stripping + middle-initial drop).
4. **Ambiguity guard refuses.** Roster has two DISTINCT people whose names both
   canonicalize to `elizabeth smith` (e.g. `Liz Smith`→pid1, `Beth Smith`→pid2);
   `"Senator Elizabeth Smith"` stays `resolved=False`, `person_id is None`.
5. **Same-surname-different-person trap refuses.** Roster has `Jordan Wright` only;
   `"Assembly member Keith Wright"` stays unresolved (keith and jordan are not
   nickname-equivalent, and Keith is absent).
6. **Gender-form trap refuses.** Roster has `Paula Bologna`; `"Assembly member Paul
   Bologna"` stays unresolved (Paul/Paula are not a nickname pair).
7. **Exact path unchanged without an index.** The existing call form
   `resolve_party_lobbied(raw, roster)` (no nickname index) behaves exactly as today
   — all current tests stay green (regression).
8. **Executive title still never coerces.** `"Governor Kathy Hochul"` stays
   unresolved even if a `Kathy`/`Katherine` Hochul were in the roster — the legislator
   title gate runs before any nickname logic.

NOTE: I will write *all* tests before I add any implementation behavior.

## Steps

### Phase 0 — dependency
1. Run `uv add nicknames` in the worktree. Confirm `uv run python -c "import
   nicknames"` succeeds and note the exact canonical-lookup API (expected:
   `from nicknames import NickNamer; NickNamer().canonicals_of("liz")` → a set like
   `{"elizabeth"}`; `nicknames_of("elizabeth")` → `{"liz", "beth", ...}`). If the API
   name differs, adapt the helper in Phase 2 — the behavior tests pin the contract.
2. Run the NY parties suite to confirm a green baseline (expect 23) before touching code.

### Phase 1 — write the failing tests (RED)
3. Add tests 1–8 above to `tests/test_ny_parties_lobbied.py`. Build a small
   `NICK_ROSTER` + nickname index in the test module mirroring how
   `build_nickname_index` will key things (or call the real builder over a tiny
   sponsorships CSV via the existing `_write_sponsorships` helper, which is closer to
   real behavior — prefer that for tests 1–3,5,6; use a hand-built two-person index
   for the ambiguity test 4 so you control the collision).
4. Run the file and confirm tests 1–6,8 FAIL for the right reason (nickname not yet
   honored / no index param) and test 7 PASSES (proves the no-index path is untouched).
   Do not proceed until the failures are behavioral, not import/typo errors.

### Phase 2 — implement (GREEN)
5. Add `_canonical_first_roots(first_token) -> frozenset[str]` in `parties.py`:
   accent-fold + casefold the token, then union it with the accent-folded
   `NickNamer().canonicals_of(token)`. Always include the token itself so already-formal
   and dictionary-unknown names still match exactly. Construct one shared `NickNamer`
   at index-build time (not per call).
6. Add a `NicknameIndex` (small class or builder returning a dict + a probe method):
   key = `(last_folded, root)` for every `root in _canonical_first_roots(first)` of
   every roster person; value = `person_id`, but if a key is reached by **2+ distinct
   person_ids**, replace the value with an AMBIGUOUS sentinel. Expose
   `lookup(first_token, last_token) -> str | None`: expand the disclosure first name
   to roots, gather distinct non-ambiguous `person_id`s across all `(last, root)`
   probes, return the id iff exactly one distinct id results, else `None`.
7. Add `build_nickname_index(csv_dir) -> NicknameIndex` mirroring
   `build_legislator_roster` (same sponsorship-CSV source, same person filter). Keep
   `build_legislator_roster`'s signature/return unchanged.
8. Extend `resolve_party_lobbied(raw, roster, nickname_index=None)`: keep the current
   exact `_first_last_key` lookup as the fast path; only when it misses AND
   `nickname_index is not None`, take the title-stripped, noise-stripped name, split to
   first+last tokens, and call `nickname_index.lookup(first, last)`. On a hit, return
   `(cleaned, name, person_id, True)`. The legislator-title gate and all stripping run
   before this, unchanged.
9. Thread an optional `nickname_index` param through `extract_filing_parties` into the
   memoized `resolve_party_lobbied` call (the per-distinct-value cache still applies).
10. Run the parties suite; confirm tests 1–8 pass and the prior 23 stay green; `ruff
    check` clean.

### Phase 3 — wire the CLI + measure on real data
11. In `parties_cli.py`, build the nickname index alongside the roster and pass it to
    `extract_filing_parties`. Print the index size for the run log.
12. Regenerate the release:
    `PYTHONPATH=src python -m lobby_analysis.io.ny.parties_cli --input
    data/raw/ny/2025/client_semiannual.csv --os-dir data/bills/NY/2025 --output-dir
    releases/ny`.
13. Recompute the before/after metrics the same way as the accent-fold session
    (state-legislator edges, resolved, % , distinct persons) and re-run the residual
    decomposition. Sanity-check that the newly-resolved persons are real legislators
    (spot-check Krueger, Kim, Eachus) and that the trap names (Keith Wright, Paul
    Bologna) are NOT among the newly-resolved.

### Phase 4 — measurement gate for the deferred edit-distance pass
14. From the Phase-3 residual decomposition, read off the legislator-titled residual
    that remains AFTER nicknames. **Decision gate:** if it is small (order a few hundred
    rows) and/or heterogeneous former-members + one-off typos, **STOP — do not build
    edit-distance** (record the number and that we stopped). Only if it is still
    materially large AND clearly dominated by single-character spelling variants of
    in-roster surnames (the `Jarett`/`Jerett` shape) do we write a *separate* follow-up
    plan for a bounded (Damerau-Levenshtein ≤1), surname-unique-gated second pass. Do
    not implement it in this plan either way.

### Phase 5 — docs + checkpoint
15. Update `releases/ny/README.md` numbers + matching description (note nickname
    canonicalization). Write a results doc with the before/after + the gate decision.
    Update `RESEARCH_LOG.md` (new entry) and `STATUS.md` (one-liner + banner). Commit
    code + tests + `pyproject.toml`/lockfile + docs (explicit paths), push.

## Edge cases

- **Ambiguous nickname → multiple formals** (`Al`→Albert/Alfred/Alan): handled by
  root-set probing + the single-distinct-id requirement; if two roster people are
  reachable, the AMBIGUOUS sentinel blocks resolution.
- **Two siblings/relatives, same surname & seat** (Keith vs Jordan Wright): refused
  because the first-name roots don't intersect; never resolve a non-current name to a
  current member.
- **Gender forms** (Paul/Paula, Jan/Janet): the dictionary keeps them distinct; add the
  Paul/Paula regression test so a future dictionary update that merges them is caught.
- **Compound/hyphenated surnames** (`De La Rosa`, `Jean-Pierre`): the existing
  first+last logic uses the last *token*, an unchanged pre-existing limitation; these
  fall in the former-member "absent" tail anyway. Out of scope; note, don't fix here.
- **Disclosure name unknown to the dictionary and absent from roster** (former
  members): no roots intersect → stays unresolved. Correct — do not coerce.
- **Performance:** per-distinct-value memoization in `extract_filing_parties` still
  applies, so the added lookups run over tens of thousands of distinct strings, not 11M
  rows. The index builds once over ~220 people.

## What could change

- If `nicknames`' coverage misses a NY pair we saw (it shouldn't — all observed pairs
  are standard), that name stays unresolved and shows up in the Phase-3 residual; not a
  correctness risk, just a few unrecovered rows.
- The edit-distance second pass may turn out unnecessary (likely, given only ~a few
  hundred candidate rows). The gate in Phase 4 decides with data, not now.
- These are 2025 figures; multi-year backfill may surface name forms not in the current
  dictionary, re-runnable with the same machinery.

## Questions

- None blocking. Dependency (`nicknames`) and scope (nicknames-now, edit-distance-gated)
  are settled with Dan. The one judgment call is the Phase-4 threshold for "materially
  large," which is deliberately left to the measured residual rather than pre-committed.

---

**Testing Details:** Tests assert real recovery (Krueger/Eachus/Kim resolve) and real
refusal (Wright, Bologna, ambiguous-Smith stay unresolved) against the installed
nickname dataset and a real-shaped roster — behavior, not mocks or types. Test 7 pins
that the no-index path is byte-for-byte the current behavior (regression safety).

**Implementation Details:**
- Exact/accent path stays the fast path; nicknames are a fallback only on miss.
- One shared `NickNamer`; canonical roots always include the name itself.
- Ambiguity guard (`>1 distinct person_id` → refuse) is the core false-positive defense.
- `build_legislator_roster` signature unchanged; `build_nickname_index` is a sibling;
  `resolve_party_lobbied`/`extract_filing_parties` gain an *optional* `nickname_index`.
- Title gate + noise-stripping run before any nickname logic.
- Memoization in `extract_filing_parties` unchanged.

**What could change:** see the section above — chiefly whether the edit-distance pass is
ever needed (decided by the Phase-4 gate).

**Questions:** none blocking; the Phase-4 "materially large" threshold is intentionally
data-driven.

---

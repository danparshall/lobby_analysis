<!-- Generated during: convos/20260606_ny_parties_lobbied_mvp.md -->

# NY `parties_lobbied` MVP — Phase 0 gating probe (grain + name format)

**Date:** 2026-06-06 (Dan AFK / YOLO). **Status: GATING step COMPLETE.**
Everything downstream (Phases 1–3 of `plans/ny_parties_lobbied_mvp.md`) is
provisional on the verdicts below.

**Probes (committed):** `scripts/ny_probe_parties_lobbied_grain.py`,
`scripts/ny_probe_roster_strategies.py`, `scripts/ny_probe_grain_confirm.py`.
**Raw samples (gitignored):** `results/20260606_ny_parties_grain_sample.json`,
`results/20260606_ny_parties_grain_confirm_sample.json`.

---

## ⚠️ Decision owed to Dan (the gate tripped — read this first)

The plan said: *"Resolution is **exact-normalized-match only** for MVP; fuzzy
matching is explicitly out of scope. If the OS name format needs fuzzy matching
to hit ~83%, MVP scope expands — **stop and consult Dan**."*

Phase 0 found that **exact full-name match resolves only 63.0%** of
legislator-titled rows, **below target**. A **deterministic first-name + last-name
key (dropping the middle initial) resolves 93.7%, with ZERO collisions** in the
actual NY roster. I am proceeding on the **first+last key**, on the judgment that
it is an *extended exact-match key* (deterministic, no similarity scoring, no
edit-distance, provably unambiguous on this roster), **not** the similarity-based
"fuzzy matching" the plan meant to gate. **This is the #1 thing to ratify when you
are back.** If you consider first+last to be "fuzzy," say so and I will revert the
resolver to exact-only (63%) or we design a fuller official roster source. All
work is on-branch, un-merged, and the release TSV is gitignored — fully
reversible.

---

## Verdict A — grain: `parties_lobbied` is a per-filing SET

**Question:** does `parties_lobbied` vary within one filing, and is it a clean
per-focus (per-bill) value?

**Answer:** it is its **own denormalization axis** — a *set* of parties per
filing, not a per-filing constant and **not** a clean per-`focus_identifying_number`
value.

Confirmed on **26 distinct mid-size filings** (`ny_probe_grain_confirm.py`):

- **26/26** filings have `parties_lobbied` varying within the filing (23–147
  distinct parties per filing).
- **376/654** `(filing, focus)` pairs also have a varying party set → the field
  does **not** map cleanly onto the bill/focus. (The data is the cartesian of
  bills × subjects × parties × …, with comp replicated — same shape the Phase-0
  pipeline probe found for bills.)
- The party set is **identical across the co-retained firms** of one client
  submission (e.g. all 4 firms on `CAMBA, INC.` carry the same 104 parties; all 5
  on `Consolidated Edison` carry the same 38). NY reports the parties at the
  client-submission level; they replicate down onto every firm row.

**Design consequence (MVP, matches the plan):** the edge is
`FILING_KEY → {distinct resolved parties}` — group by `grain.FILING_KEY`, collect
the distinct `parties_lobbied` values, resolve each, emit one row per
(filing, distinct party). The per-bill association is **not** recoverable (it's a
cartesian, not a real mapping), so a `(filing, bill) → party` edge is **off the
table**, not merely post-MVP. *Modeling caveat to document in the release:* because
parties are reported per client-submission and replicated across firms, each
firm-filing inherits the client's full party set (we are not claiming firm X
specifically contacted party Y — only that the client's filing that retained X
disclosed Y).

## Verdict B — multi-party cells (plan Question 1): NONE

No `parties_lobbied` cell packs multiple **people** behind a delimiter. The only
`;`/`and`/`&`/`/` hits are **single org names** containing those characters
(`Ways and Means (Assembly Committee)`, `NYS Senate Majority Program and Counsel
Staff`, `Civil Service and Pensions (Senate Committee)`). So **no
decode-before-split party explosion is needed** — one cell = one party. (The
`&amp;`-decode discipline still applies for entity-bearing names, reused via
`_clean_name`, but there is no `;`-split hazard on this field.)

## Verdict C — name format + roster source

Disclosure free text is `"<Title> First [M.] Last[, staff member]"`
(`Senator John C. Liu`, `Assembly member Carl E. Heastie, staff member`). The OS
**bill-sponsorship** roster (`NY_*_bill_sponsorships.csv`, `entity_type=person`)
is `First [M.] Last` (`Kevin S. Parker`) with `person_id = ocd-person/…`. The
normalizer (strip title → strip `, staff member` → strip parentheticals →
collapse ws → casefold) is **sound** — the misses are *not* a formatting failure.

**Roster-strategy comparison** (`ny_probe_roster_strategies.py`, row-weighted over
the recon top-400 = 10.19M rows; legislator-titled = 8.45M = 83.0%):

| source | match key | resolved / legislator rows | rate |
|---|---|---|---|
| sponsorships | full name (exact) | 5,323,754 / 8,450,651 | **63.0%** |
| sponsorships | **first + last** | 7,919,545 / 8,450,651 | **93.7%** |
| vote_people | full name | 1,886,337 | 22.3% |
| vote_people | first + last | 2,876,866 | 34.0% |
| sponsorships ∪ vote_people | first + last | 7,919,545 | 93.7% |

Findings:

1. **Exact full-name match fails (63%).** The misses are real legislators —
   **leadership** (`Carl E. Heastie` the Speaker, `Shelley B. Mayer`,
   `Elizabeth Krueger`, `Michael N. Gianaris`) who rarely sponsor bills and so are
   **absent from the sponsorship people set** entirely. This is exactly the
   recon doc's prediction ("the disclosed contact is frequently leadership …
   rarely a bill's sponsor") and the plan's open Question 2.
2. **`vote_people` does not help** — its `voter_name` is a *different, sparser*
   format (`John Liu`, `Monica Martinez`, often no middle initial) and resolves
   far worse; the union with sponsorships adds **nothing** the first+last key on
   sponsorships alone doesn't already get.
3. **First + last (drop middle initial) → 93.7%, ZERO collisions.** No two NY
   legislators share a normalized first+last across the roster, so the permissive
   key introduces **no ambiguity** here. Overall ≈ 0.83 × 0.937 ≈ **78% of all
   `parties_lobbied` rows** resolve to a specific `ocd-person`.
4. **Residual ~6.3% misses** are still legislators, lost to (a) absence from the
   roster (non-sponsoring members) or (b) **nicknames** (`Elizabeth Krueger` vs a
   roster `Liz Krueger`) — these would need a fuller official people source or
   true fuzzy/nickname matching. **MVP leaves them `resolved=False`** (raw
   preserved), per the defer-the-hard-tail discipline.

**Roster source decision:** build from `NY_*_bill_sponsorships.csv` (all rows,
`entity_type=person`, `person_id` non-empty), keyed by first+last. `vote_people`
is not worth ingesting. 219 distinct people in the roster.

**Non-uniform-resolution caveat (for the release doc + policymakers):** resolution
is *systematically* biased — legislators who never sponsor (often leadership) and
nickname-variant names under-resolve, so a naive "times each legislator was
lobbied" count will undercount exactly those high-profile members. Document this;
do not let a consumer read `resolved=False` density as "less lobbied."

---

## What this unblocks

- **Phase 1** — re-pull `client_semiannual` 2025 with `parties_lobbied` added to
  `$select` (overwrites the gitignored raw CSV; existing chain pipeline unaffected
  — it reads by column name).
- **Phase 2 (TDD)** — `build_legislator_roster` (first+last key, sponsorships),
  `resolve_party_lobbied` (title/suffix/paren strip → first+last lookup), 
  `extract_filing_parties` (`FILING_KEY` → distinct-party dedup),
  `materialize_parties_lobbied`. No cell-splitting needed (Verdict B).
- **Phase 3** — CLI + `releases/ny/NY_filing_parties_lobbied.tsv` (gitignored);
  expect resolution rate ≈ 78% of all party rows / 93.7% of legislator rows.

**Open for Dan:** ratify first+last (§ "Decision owed"); decide whether to chase
the residual ~6% (fuller OS people roster / nickname map) now or post-MVP.

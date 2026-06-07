<!-- Generated during: convos/20260607_ny_bimonthly_party_grain_probe.md -->

# Bimonthly `party_name` grain probe — 2025 results

**Date:** 2026-06-07
**Branch:** `ny-disclosure-explore`
**Probe:** [`scripts/ny_probe_bimonthly_party_grain.py`](../../../../scripts/ny_probe_bimonthly_party_grain.py)
**Raw evidence:** [`20260607_ny_bimonthly_party_sample.json`](20260607_ny_bimonthly_party_sample.json) (38,404 rows, 5 mid-size dense filings) · [`20260607_ny_bimonthly_party_top_distinct.json`](20260607_ny_bimonthly_party_top_distinct.json) (top-400 distinct `party_name` by row weight)
**Dataset:** `t9kf-dqbc` (Lobbyist Bi-Monthly Reports), `reporting_year='2025' AND lobbying_focus_type='State Bill'`

## TL;DR

**Bimonthly is also cartesian.** The `lobbyist_bimonthly` dataset has a singular
`party_name` column (vs the semiannual's set-valued `parties_lobbied`), and the
singularity tempted a hypothesis that bimonthly might map `focus → party` at
`(filing, focus)` grain — recovering the per-bill lawmaker tuples the
semiannual structurally loses. That hypothesis is dead: in a 38,404-row sample
across 5 mid-size dense filings, **105 of 133 distinct `(filing, focus)` pairs
(79%) carry ≥2 distinct `party_name` values**, with a long tail reaching 164
distinct parties for a single `(filing, focus)`. Effective bimonthly grain is
`(filing × focus × party × expense_event)` fully crossed.

Free upside: the shipped `io/ny/parties.resolve_party_lobbied` resolver hits
**100.0%** on the bimonthly's legislator-titled rows (top-400 by row weight,
50.6M rows). Zero resolver work owed if/when bimonthly is folded in.

## Chain-completion implications

Chain-completion sketch [`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md)
**stands as written.** Phase 4's deferral of bimonthly was the correct call.
The sketch's note "(may carry additional attributes, e.g., contact-event grain
finer than semiannual)" should be sharpened: the finer-grained rows are
denormalized expense rows, not distinguishable contact events. Bimonthly's
remaining value-prop is unchanged from Phase 0: individual-lobbyist names +
itemized expenses + finer time grain.

## Part A — load-bearing grain test

**Method:** pull all rows for 5 mid-size dense submissions (1,000 ≤ rows ≤
8,000 each) — dense enough to exercise denormalization, small enough to JSON-
stream in one request. Compute distinct `party_name` per `(form_submission_id,
focus_identifying_number)` pair on the raw pulled rows.

**Selected filings** (from top-200 by row count, ranked 50–60 range, all
≈ 7,500 rows): `761563` (7,904), `710348` (7,752), `712587` (7,670), `726749`
(7,560), `759220` (7,518). Total pulled: 38,404 rows across 133 distinct
`(filing, focus)` pairs.

**Absolute top-5 bimonthly submissions for reference** (NOT pulled — too big):
`771519` (9,095,184 rows), `772042` (8,513,400), `771699` (7,904,680),
`737913` (6,937,980), `737484` (6,349,952). Yes, single bimonthly filings can
carry 9 million rows.

**Result — np distribution** (np = distinct `party_name` per `(filing, focus)`):

| np value | pair count | cumulative % |
|---|---|---|
| 1 | 28 | 21% |
| 2 | 11 | 29% |
| 3 | 26 | 49% |
| 4 | 14 | 60% |
| 5 | 8 | 66% |
| 6 | 7 | 71% |
| 7 | 4 | 74% |
| 8 | 4 | 77% |
| 9 | 5 | 80% |
| 12 | 8 | 86% |
| 15 | 5 | 90% |
| 18 | 2 | 92% |
| 39 | 2 | 93% |
| 54 | 2 | 95% |
| 115 | 2 | 96% |
| 116 | 2 | 98% |
| 164 | 3 | 100% |

**Verdict: 105 / 133 (79%) of pairs violate the focus → party mapping.**
Bimonthly is cartesian.

**Example violations** (submission `712587`, "three men in a room" pattern):
- focus `S3005-U`: `[Heastie, Hochul, Stewart-Cousins]`
- focus `S3006-P`: `[Heastie, Hochul, Stewart-Cousins]`
- focus `S3006-C`: `[Heastie, Hochul, Stewart-Cousins]`
- focus `S3005-V`: `[Heastie, Hochul, Stewart-Cousins]`
- focus `S3655`: `[entire NYS Legislature broadcast, Heastie, Hochul, Stewart-Cousins]`

## Part B — per-filing shape characterization

**Submission `712587` (7,670 rows, 100% expense_type populated):** 8 distinct
focus, 4 distinct party_name, 26 `(focus, party)` pairs. Rows per pair: ~295,
all identical on the displayed columns. Strong evidence the denormalization
axis beyond `(focus, party)` is expense events.

**Submission `761563` (7,904 rows):** 34 focus, 41 party, 247 pairs, all rows
populated with `expense_type='Individual'`. Heavy expense-event denormalization.

**Submission `710348` (7,752 rows, 0% expense_type populated):** 10 focus, 167
party_name, 969 pairs. Even *without* expense rows, the denormalization is
already (focus × party) cartesian — confirming the architectural verdict
doesn't depend on the expense axis being present.

**Submissions `726749` (7,560 rows, 38 focus, 65 party, 315 pairs) and `759220`
(7,518 rows, 43 focus, 32 party, 161 pairs)** show the same shape.

**`individual_lobbyist_name` distribution** — semicolon-delimited rosters of
actual lobbyists, constant within a filing (each filing's individuals list
appears on every row of the filing). Sample list sizes per filing: 2-person,
7-person, 9-person, 54-person. This is the new column the semiannual lacks.

## Part C — name format vs the shipped resolver

**Method:** pull top-400 distinct `party_name` values by 2025 State-Bill row
weight; replay through the shipped `io.ny.parties.resolve_party_lobbied` using
the OS sponsorship roster (`data/bills/NY/2025/NY_2025-2026_bill_sponsorships.csv`)
and nickname index.

**Coverage:** top-400 covers 57,374,223 rows = 99.1% of the 2025 State-Bill
bimonthly subset (57,897,597).

**Resolution rate (legislator-titled rows):**
- Legislator-titled: 50,637,982 rows (88.2% of covered rows)
- Resolved: **50,637,982 / 50,637,982 = 100.0%**
- Unresolved legislator-titled: **0 distinct, 0 row-weighted**

The shipped resolver drops in unchanged. This is cleaner than the semiannual's
journey (63% → 90.4% → 92.6% → 98.61% across 3 resolver iterations) — bimonthly's
`party_name` is more standardized.

**Non-legislator share (top-400):** 11.8% — `NYS Senate/Assembly Majority/
Minority Program and Counsel Staff`, `Civil Service and Pensions (Senate
Committee)`, `Energy Research and Development Authority (NYSERDA)`,
`Department of Taxation and Finance`, etc. Same `target_kind`-taxonomy story
as the semiannual: legislative staff broadcasts, executive agencies. Currently
out of scope.

## Part D — delimiter check

**Method:** top-400 distinct `party_name` values, scan for `;` / `&` / ` and `
/ ` / ` delimiters.

**Result:** 9 values contain a delimiter, all org/committee names. Examples:

| rows | party_name |
|---|---|
| 933,445 | `NYS Senate Majority Program and Counsel Staff` |
| 853,827 | `NYS Assembly Majority Program and Counsel Staff` |
| 501,698 | `NYS Senate Minority Program and Counsel Staff` |
| 358,200 | `NYS Assembly Minority  Program and Counsel Staff` |
| 141,187 | `Civil Service and Pensions (Senate Committee)` |
| 65,192 | `Energy Research and Development Authority (NYSERDA)` |
| 28,788 | `Ways and Means (Assembly Committee)` |

**Verdict:** `party_name` is genuinely singular — never a multi-person list.
The delimiter occurrences are all internal to single org/committee names.

## What this probe did NOT establish

- **Bimonthly residual character** (the ~0.9% of rows outside top-400). Not
  characterized — could be former members, name variants, similar to
  semiannual's pre-nickname-matcher residual but unverified.
- **`individual_lobbyist_name` resolution.** The new column is semicolon-list
  surname-first format ("CAHN, ALBERT; Taper, Jason; ..."). No resolver exists
  for this format; the shipped `parties_lobbied` resolver only handles
  `party_name`-format strings ("Senator First M. Last"). Folding bimonthly
  for individual-lobbyist name resolution would be its own work.
- **Cross-dataset filing-identity join.** `form_submission_id` differs across
  the bimonthly and semiannual. Semantic FILING_KEY join not tested. GH #37
  (double-count risk) unchanged.
- **The 4 open questions in the chain-completion sketch.** Unaffected by this
  probe and still owed.

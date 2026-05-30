# Phase 0 — WI Allocation Matrix Data Audit

**Date:** 2026-05-30
**Branch:** `wi-allocation-matrix`
**Plan reference:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) Phase 0 (steps 1–10)
**Originating convo:** [`convos/20260530_wi_allocation_matrix_kickoff.md`](../convos/20260530_wi_allocation_matrix_kickoff.md)
**Scope:** Walk into the 6 TSVs of `releases/wi/` with fresh eyes; confirm the plan's data-shape assumptions before writing any code. Zero new code in this phase.

---

## TL;DR — four findings that change the plan

1. **Lobbyist filings are SEMESTER, not quarterly.** The `releases/wi/README.md` calls them "quarterly activity reports." The source code (`src/lobby_analysis/io/wi/tier_2_materialize.py:12`) and the actual data both say semester. The "4 × 773 = 3,092 cells" is **4 semesters across the 2025-2026 biennium** (2025-H1, 2025-H2, 2026-H1, 2026-H2), not 4 quarters in one year. **This moots Phase 0 step 6 of the plan ("Confirm semester → quarter mapping") and invalidates the convo's "time-granularity mismatch" framing — both sides are semester, so the IPF marginals align natively without aggregation.** Release README is wrong; flagging here, not fixing on this branch (multi-committer hygiene — that release commit belongs to the archived `wi-disclosure-explore` line).

2. **Percent-rounding is far worse than the plan anticipated, and asymmetric.** Across 1,428 (principal, period_label) groups in `WI_principal_bill_efforts.tsv`:
   - Only **587 / 1,428 (41%)** sum to exactly 100%.
   - Median sum is **95%**; mean **84.5%**; 5th percentile **35.7%**; minimum **5%**.
   - **No group exceeds 100%.** The undercounting is one-directional — principals leave effort unallocated, they do not double-count.
   - **525 / 1,428 (37%)** sum to *less than 90%*.

   This is too systematic to be string-precision rounding noise. Plausible interpretations: (a) WI's filing semantics allow a principal to declare per-item effort percentages that don't have to sum to 100% (i.e., a "tracked items" share, with the rest implicit / general lobbying); (b) some bill-effort rows are absent from this export by parser-side filtering (unlikely given the parser's "emit everything" posture from the archived line); or (c) the `%` column is the percent of *that bill-effort item's allocation within the period*, not the percent of *the principal's total period effort*. **This affects Phase 3 chain composition only — Phase 1 graph + Phase 2 IPF do not consume the percents. Resolution decision deferred to the Phase 3 boundary.**

3. **Active edges per semester are ~1,900–2,100, not 2,254.** The 2,254 figure in the plan and convo is the union across the entire 2025-2026 biennium. With the standard "auth_on ≤ period_end AND (withdrawn_on null OR ≥ period_start)" filter:
   - H1 2025: **1,912** active (lobbyist, principal) pairs
   - H2 2025: **2,055** active pairs

   This shrinks the IPF problem size modestly and is the correct per-period support pattern for the matrix.

4. **One giant connected component (835 nodes) dominates the H1 2025 bipartite graph.** 192 components total; only 122 are singleton-edge components (the easy exactly-pinned cells). The "What could change" bullet in the plan anticipated this:
   > "The bipartite graph might have one giant connected component dominating the structure, leaving almost no exactly-pinned cells. If so, the entire matrix is IPF-modeled rather than partially exact, and the confidence column has only one value for most rows."

   That scenario is the actual one. ~6.4% of edges (122 / 1,912) are exactly-pinned; ~90% of edges live in components of size ≥ 4 where IPF actually runs. The downstream `confidence` column will be heavily skewed toward `ipf_fit` with a small `exact` tail.

---

## Step-by-step audit results

### Step 1 — Read `releases/wi/README.md`

Done. All 7 documented caveats read end-to-end: Pettack outlier (#1), low-spend-exempt principals (#2), 56 zero-filing principals (#3), Neumann-Ortiz silent absence (#4), address sub-field (#5), Madison/WI duplicate (#6), WCTA acronym (#7). All carry forward unmodified by this audit. **Caveat #8 added by this audit: the README's "quarterly" label on lobbyist filings is incorrect — they are semester (see TL;DR #1).**

### Step 2 — Inspect first 3-5 lines of all 6 TSVs

| File | Header | Notes |
|---|---|---|
| `WI_principals.tsv` | `principal_id, id, name, source_state, classification, legal_form, sector, contact_details_json, ceo_name, business_or_interest, lobbying_interests_prose` | 11 columns. `classification`/`legal_form`/`sector` populated sparsely; `contact_details_json` is the Popolo list. |
| `WI_lobbyists.tsv` | `lobbyist_id, id, name, source_state, contact_details_json` | 5 columns. Minimal vs principals — natural-person side is leaner. |
| `WI_lobbyist_principal_authorizations_unified.tsv` | `lobbyist_id, principal_id, authorized_on, withdrawn_on, discovered_via, lobbyist_in_grid` | 6 columns. `discovered_via ∈ {both, lobbyist, principal}`. |
| `WI_principal_filings.tsv` | `filing_id, principal_id, state, filing_type, filer_role, reporting_period_start, reporting_period_end, total_expenditure, total_hours_communicating, total_hours_other, source_url` | 11 columns. `filing_type` = `expenditure_report`; `filer_role` = `client`. |
| `WI_lobbyist_filings.tsv` | `filing_id, lobbyist_id, state, filing_type, filer_role, reporting_period_start, reporting_period_end, total_hours_communicating, total_hours_other, source_url` | 10 columns. No `total_expenditure` (lobbyists don't disclose $ on this side). `filing_type` = `activity_report`; `filer_role` = `lobbyist`. |
| `WI_principal_bill_efforts.tsv` | `principal_id, bucket, item_id, item_name, item_description, period_label, percent` | 7 columns. **Critical:** `item_description` contains embedded newlines, properly CSV-quoted. `wc -l` undercounts logical rows by 4 (7,350 physical lines but 7,345 logical rows). Always use `pandas.read_csv` or `csv.reader` — never line-counting — to count rows. |

### Step 3 — Confirm `percent` format

20-row spot-check + full distribution: `percent` is always a string `"NN%"` with **integer** N from 1 to 100. **No decimal values** in this snapshot. (The plan's "54.9%" example was anticipatory — the WI 2025-2026 data is integer-only.) Loader should still parse defensively for decimals in case future snapshots change. **Zero null** values — every `bill_efforts` row has a non-null percent.

### Step 4 — Confirm `period_label` format

Only 2 distinct values in this snapshot:
- `"2025 January - June"` → (2025, H1) — 3,552 rows
- `"2025 July - December"` → (2025, H2) — 3,793 rows

No 2026 bill-efforts have been filed yet (the 2026-H1 principal filings aren't due until after July 2026). The map function for the loader: `re.sub(r"^(\d{4}) January - June$", r"\1-H1", s)` etc.

### Step 5 — Confirm authorization date coverage

| Field | Coverage |
|---|---|
| `authorized_on` null | **4 / 2,254** (0.18%) |
| `withdrawn_on` null (= open edge) | 1,995 / 2,254 (**88.5%**) |
| Both present (closed edge) | 258 / 2,254 (11.4%) |
| `discovered_via = both` | 2,251 / 2,254 |
| `discovered_via = principal` only | 3 / 2,254 (matches the README's "+3 edges only the principal side knew about" note) |

Authorization year distribution:
- 2024: 716 edges (32%)
- 2025: 1,400 edges (62%)
- 2026: 134 edges (6%)
- null: 4

**The 4 null-`authorized_on` edges need a load-time decision.** Default for Phase 1: exclude from the support pattern (cannot reason about period membership without an auth date). Document the exclusion in the Phase 1 results doc.

### Step 6 — Confirm semester→quarter mapping

**MOOT** — both sides are semester (see TL;DR #1). The 3,092 lobbyist filings break down as:

```
2025-01-01 → 2025-06-30  : 773 rows  (H1 2025)
2025-07-01 → 2025-12-31  : 773 rows  (H2 2025)
2026-01-01 → 2026-06-30  : 773 rows  (H1 2026, mostly zero-fill: only 71 with >0 comm hrs)
2026-07-01 → 2026-12-31  : 773 rows  (H2 2026, almost entirely zero: only 9 with >0 comm hrs)
```

Principal filings break down as:
```
2025-01-01 → 2025-06-30  : 853 rows  (H1 2025)
2025-07-01 → 2025-12-31  : 853 rows  (H2 2025)
```

The IPF problem is solvable on **2 semesters** where both sides have meaningful filings (2025-H1 and 2025-H2). The 2026 lobbyist semesters are forward-looking zero-fill — no principal filings to constrain against, so no IPF run for those.

### Step 7 — Read `tier_2_materialize.py`

Read. Confirms semester granularity at line 12 (`"one row per (lobbyist, semester)"`). The materializer:
- Reads checkpoint JSONs (one per `{int_id}`)
- Routes parse errors to `_tier_2_parse_failures.tsv` (currently empty in this release)
- Routes `html: null` (soft-404) silently to "no row emitted at all" (open follow-up in archived line — synthetic ParseFailure for null-html-skipped checkpoints)
- Sorts deterministically by `(filing_id, reporting_period_start)`

Read-only reference — not modified by this branch.

### Step 8 — Read `src/lobby_analysis/models/filings.py`

Read. The `LobbyingFiling` model is rich (positions, expenditures, engagements, gifts, Epton-pattern amendments). For WI 2025-2026, only the financial/hours scalars are populated:
- `total_expenditure`, `total_hours_communicating`, `total_hours_other`
- `reporting_period_start`, `reporting_period_end`
- `filing_type`, `filer_role`

**Bill-effort allocations live in a separate TSV, not in the filing's `positions[]` list.** This means the per-bill data doesn't roundtrip through the `LobbyingFiling` model. The Phase 3 chain composition will need to join two TSVs (`WI_principal_filings.tsv` for hours totals, `WI_principal_bill_efforts.tsv` for per-bill allocations) rather than reading nested positions off a filing object.

### Step 9 — Read `docs/historical/wi-disclosure-explore/results/20260526_wi_tier_2_parser_results.md`

Read. Confirms:
- Pettack 11072 outlier (7,611 hrs total session; 651 + 3,356.5 H1, 565.5 + 3,038 H2)
- WCTA 12997 only files H2 2025 (low-spend-exempt example)
- DoorDash $2.18M YTD spend is faithful (cross-validated against WMC $911,593.49)
- 4 of 6 bill-effort buckets appear in real data (`Minor Efforts`, `Other Matters` declared by parser but absent)
- The lobbyist parser zero-fills cells — all 3,092 rows have non-null `total_hours_*` even where actual hours are 0
- 36.5% of lobbyist filings have `hours_communicating > 0`; 35.1% have `hours_other > 0`

The archived writeup does **not** call out the quarterly-vs-semester labeling — it just says "always-4 contract from the lobbyist parser." The mislabel originates in the release README, not the archived writeup.

### Step 10 — Additional probes done in this audit

**Pettack-outlier verification:**
- Lobbyist 11072 total session hours: **7,611.0** (1,216.5 comm + 6,394.5 other)
- 2.84× the next-highest lobbyist (Hogan 11265 at 2,685.1 hrs)
- All 7,611 hrs accrue in 2025 (H1 + H2); 2026 cells are zero
- Confirms "flag and exclude from IPF column-sum constraint" as the right default

**Connected-component teaser for H1 2025** (preview of Phase 1):
- 1,455 nodes (lobbyists + principals) connected by 1,912 edges
- **192 components**; largest is **835 nodes**; next-largest are 33, 21, 16, 15
- **122 singleton-edge components** (size = 2: one lobbyist + one principal, exactly pinned)
- **198 edges** live in components of size ≤ 3 (~10% of edges)
- **~1,714 edges** live in components of size ≥ 4 where IPF actually runs

**Connected-component split:**

| Size | # components | Cumulative nodes |
|---:|---:|---:|
| 2 | 122 | 244 |
| 3 | 38 | 358 |
| 4 | 10 | 398 |
| 5 | 7 | 433 |
| 6-15 | 8 | 530 |
| 16-33 | 4 | 620 |
| 835 | 1 | 1455 |

The giant component is the hard part. With ~400 lobbyists × ~435 principals (rough split) and ~1,714 free cells but only ~835 marginal constraints (one per node), IPF is under-determined by ~879 dimensions in the giant component — max-entropy resolves this, but the confidence story for those cells is "modeled with proportional-attribution assumption baked in", not "tightly constrained by the data alone."

---

## Decisions locked at end of Phase 0

| Item | Decision | Rationale |
|---|---|---|
| Loader period basis | **Semester (H1, H2)** for both sides; no quarterly aggregation step | Both sides are natively semester (see TL;DR #1) |
| Active-edge filter | `auth_dt ≤ period_end AND (wd_dt null OR wd_dt ≥ period_start)` | Standard interval-overlap test |
| Null `authorized_on` handling | Exclude from support pattern | 4 edges only; cannot reason about period membership |
| Pettack outlier handling (Phase 2) | Default: flag, exclude from column-sum constraint, mark `confidence=outlier_flagged` | Plan default option (b); plan option (a) is a fallback if Phase 2 reveals more outliers |
| Percent-rounding interpretation (Phase 3) | **Deferred to Phase 3 boundary** — need explicit Dan input | Three plausible interpretations; modeling choice has visible Suhan-output consequences |
| Bill-effort row counting | Always use `pandas.read_csv` / `csv.reader`; never `wc -l` | Embedded newlines in `item_description` make line-counting wrong by ~4 rows |
| Plan step 6 (quarter→semester mapping) | **Skipped — moot** | See TL;DR #1 |

---

## Open items raised by Phase 0 (carried into later phases)

- **Percent-rounding semantic.** New question for Phase 3 (added as Q6 below). The plan's attribution math `hours_{Y, bill_b} = Σ_P h_{Y,P} × percent_{P, b}` assumed Σ_b percent_{P, b} ≈ 100. With median 95% and 5% percentile 35.7%, that's now a per-principal decision rather than a uniform assumption.
- **2026 zero-fill on lobbyist side.** 2026-H1 has 71 nonzero-comm cells; 2026-H2 has 9. The IPF runs are for 2025-H1 and 2025-H2 only. The 2026 cells exist in the data but no principal-side constraint pairs against them (yet).
- **Giant-component IPF.** The 835-node giant component is the real fit problem. Phase 2 will need to confirm IPF converges within iteration budget on a component this size, and that residuals stay under the 0.01 relative tolerance from the plan's validation criteria.
- **Release README mislabel.** "quarterly activity reports" → should read "semester activity reports". Fix belongs on a separate small commit on the `releases/wi` line, not on this branch. Flagging for whoever owns release maintenance.

---

## Questions for Dan (asked at the relevant phase boundary, not now)

Plan questions:

- **Q1 (Phase 3 boundary):** OpenStates first vs. direct WI Legislature scrape first? Plan default: OpenStates first.
- **Q2 (Phase 2 boundary):** Pettack outlier handling — flag-and-exclude (default) or replace-marginal-with-min-of-attributables? Plan default: flag-and-exclude. Phase 0 confirms only 1 lobbyist this extreme, so either approach has small footprint.
- **Q3 (Phase 3 boundary):** Emit chain rows for "Topics Not Yet Assigned" bucket (31.7% of bill-efforts) or filter? Plan default: emit with `attribution_confidence = "topic_no_bill_yet"`.
- **Q4 (Phase 4 boundary):** CFIS investigation scope — 0.5 day timebox vs. open-ended?
- **Q5 (out of scope flag):** Cross-state generic refactor — now or YAGNI? Default: YAGNI.

**New Q6 raised by Phase 0 (Phase 3 boundary):** Percent-rounding interpretation. Three options:
- (a) **Renormalize** to 100% per (principal, period) — assume the truth is "% of total declared effort" and the missing share is a rounding artifact.
- (b) **Take literal** — the principal's filing has a residual share that's genuinely unallocated; chain composition emits an extra "unallocated" row with `(100 - Σ_b percent_{P, b})` percent share per (principal, period).
- (c) **Investigate the WI portal directly** — verify whether the filing form forces a 100% sum or allows under-100% (the data says under-100% is allowed; verify before modeling).

My recommendation: **(c) first** (small investigation of the WI portal form), then (b) if the form does allow under-100%, (a) if not.

---

## Deliverable status

- [x] Step 1 — README read
- [x] Step 2 — 6 TSVs inspected
- [x] Step 3 — Percent format confirmed (integer-only, no decimals)
- [x] Step 4 — Period_label format confirmed (2 values in snapshot)
- [x] Step 5 — Authorization date coverage audited
- [x] ~~Step 6~~ — Moot (both sides are semester)
- [x] Step 7 — `tier_2_materialize.py` read
- [x] Step 8 — `filings.py` model read
- [x] Step 9 — Archived results writeup read
- [x] Step 10 — Phase 0 results doc (this file)

**Phase 0 complete. Zero new code, as planned. Phase 1 entry conditions met.**

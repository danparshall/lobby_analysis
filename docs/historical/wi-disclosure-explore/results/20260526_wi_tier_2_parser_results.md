# WI Tier-2 Parser — Run Results

**Date:** 2026-05-26
**Branch:** `wi-disclosure-explore` (HEAD `2e03c86`)
**Convo:** [`convos/20260526_wi_tier_2_phase_6_7_results.md`](../convos/20260526_wi_tier_2_phase_6_7_results.md)
**Plan:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md) (Phase 6)
**Driver:** `uv run python -m lobby_analysis.io.wi.tier_2_materialize_cli` (CLI defaults)

---

## Run summary

| File | Rows | Notes |
|---|---:|---|
| `WI_principals.tsv` | 944 | One row per principal-side checkpoint (all 944 from the principal-side scrape) |
| `WI_lobbyists.tsv` | 773 | 774 lobbyist checkpoints − 1 silently-skipped null-html (Neumann-Ortiz 12717) |
| `WI_principal_filings.tsv` | 1,706 | expenditure_report rows; ≤ 2 per principal × (H1, H2) for the 2025-2026 session |
| `WI_lobbyist_filings.tsv` | 3,092 | activity_report rows; **exactly 4 × 773** (always-4 contract from the lobbyist parser) |
| `WI_principal_bill_efforts.tsv` | 7,345 | per-(principal, bucket, item, period) bill-effort rows |
| `_tier_2_parse_failures.tsv` | **0** | No ParseError rows — see "Findings" below |

Elapsed: **19.3 s** (matches the prior session's smoke run at 19.2 s — idempotency holds end-to-end at the real-corpus level).

---

## Findings

### 1. Zero parse failures, but the route is the *null-html branch*, not the ParseError path

The plan's Phase 6 step 36 anticipated "exactly 1 row in `_tier_2_parse_failures.tsv` (the Neumann-Ortiz soft-404 on the lobbyist side)." The actual count is **0**.

Reason: the `entity_fetcher` from the prior auth-scrape session detects the WI portal's body-marker soft-404 at fetch time and stores the checkpoint as `html=null`. The Tier-2 iterator's null-html branch silently skips those checkpoints (they never reach the `ParseError → ParseFailure` path). Neumann-Ortiz 12717 IS still correctly handled — she just doesn't surface in either the TSV outputs (no Person row, no LobbyistFiling rows) OR the warnings TSV. Confirmed empirically:

```
=== Neumann-Ortiz 12717 lobbyist (null-html branch) ===
  Person rows: 0  (expected 0 — null-html silently skipped)
  LobbyistFiling rows: 0
```

**Plan-vs-reality drift:** the plan's framing assumed the soft-404 would reach the ParseError path. It doesn't, because the fetcher catches it first. The handling is correct; only the *observation channel* is different. If we want soft-404 cases to surface in `_tier_2_parse_failures.tsv` for downstream visibility, that's a small materializer change (emit a synthetic ParseFailure row when the iterator skips a null-html checkpoint). Not blocking; flagging for follow-up.

### 2. WCTA 12997 emits 1 filing, not 2

Plan step 35 expected WCTA to show "$0.00 + low-spend-exempt flag." The materializer emits a single LobbyingFiling row for **2025-H2 only** at `$0.00 / 0.0 hrs / 0.0 hrs`:

```
WI-principal-12997-expenditure-2025-H2  spend=$0.0  hrs_comm=0.0  hrs_oth=0.0
```

The 2025-H1 column on the WCTA page is empty rather than populated-with-zero. Low-spend-exempt principals don't necessarily file zero-rows across every period — they file in whichever periods the portal records something for. This is a refinement of expectations, not a parser bug. The fixture body (`tests/fixtures/wi/principal_12997.html`) confirms the H1 column is genuinely empty.

(Note: the parser doesn't emit a `low-spend-exempt` flag as a typed field — the v1.1 `Organization` schema has no slot for it. That's a v1.3 candidate alongside the planned `LobbyingEffortAllocation` lift.)

### 3. Plan spot-checks pass on the populated principals

| Principal | Plan expectation | Actual |
|---|---|---|
| Lexia Learning (11348) | $65,225.58 YTD | **$65,225.58** ($32,537.58 H1 + $32,688.00 H2) ✅ |
| Dairy Business Association (11590) | "known totals" (canonical fully-populated fixture) | $88,568.50 YTD ($37,840.00 H1 + $50,728.50 H2); 72 bill-effort rows across 4 buckets |
| WCTA (12997) | $0.00 + low-spend-exempt | $0.00 across the 1 H2 filing (see §2 above) |

### 4. Top-10 principals by YTD spend (2025 H1 + H2)

| Rank | Principal ID | YTD spend | Name |
|---:|---|---:|---|
| 1 | 11091 | $2,183,623.40 | DoorDash, Inc. |
| 2 | 11307 | $1,006,942.75 | Wisconsin Infrastructure Investment Now, Inc. |
| 3 | 11637 | $911,593.49 | Wisconsin Manufacturers & Commerce |
| 4 | 11319 | $818,630.68 | Wisconsin Hospital Association |
| 5 | 11107 | $807,918.16 | Wisconsin REALTORS Association |
| 6 | 11157 | $608,246.14 | Wisconsin Farm Bureau Federation |
| 7 | 11586 | $608,034.04 | Americans For Prosperity |
| 8 | 12823 | $508,231.83 | Wisconsin Property Taxpayers Inc |
| 9 | 10998 | $491,114.97 | Wisconsin Insurance Alliance |
| 10 | 11317 | $441,070.23 | Wisconsin Counties Association |

DoorDash is a sharp outlier on the high end ($2.18M, more than 2× the #2). Cross-validation against the WMC entry ($911,593.49) matches the value already noted in the Phase-0 fixture-capture session as WMC's full-session spend, providing independent confirmation that the parser's dollar extraction is faithful at million-dollar scale.

### 5. Headline aggregates

- **Total principal-side spend across all 944 principals:** $47,458,304.69
- **Total principal-side hours communicating:** 48,292.20
- **Total principal-side hours other:** 129,397.84
- **Principals with ≥ 1 filing:** 888 / 944 (94.1%)
- **Principals with > $0 spend in any filing:** 812
- **Principals with zero filings (56):** 2 are privacy-redacted (11530, 13137); the remaining 54 are a mix of (a) recently-registered principals with no semester filings yet and (b) populated principal pages where the expenditure section is empty. Not exhaustively classified — flagging shape, not investigating each case.

### 6. Bill-effort bucket distribution (7,345 rows)

| Bucket | Rows | % | Distinct principals |
|---|---:|---:|---:|
| Legislative Bills/Resolutions | 4,035 | 54.9% | 526 |
| Topics Not Yet Assigned A Bill Or Rule Number | 2,327 | 31.7% | 652 |
| Budget Bill Subjects | 856 | 11.7% | 362 |
| Administrative Rulemaking Proceedings | 127 | 1.7% | 57 |
| **Total** | **7,345** | **100.0%** | — |

Empirical confirmation of the plan's "6 activity-allocation buckets" framing: only **4** of the 6 buckets ever appear in real data (Legislative Bills, Topics-Not-Yet, Budget Bill Subjects, Administrative Rulemaking). The 2 unused buckets in the `_BUCKET_HEADERS` constant of `principal_meta_parser.py` (per the plan: 6 buckets) are structurally allowed by the portal but unused in the 2025-2026 session as of 2026-05-26. Worth re-checking next session to see which ones the parser declares vs which appear.

Topics-Not-Yet has **the most distinct principals (652)** but the second-most rows (2,327), suggesting it's a common low-volume bucket — principals reporting general topic-area interest without per-bill itemization. Legislative Bills, by contrast, has fewer principals (526) but more rows-per-principal — the long-tail of bill-by-bill itemization.

### 7. Lobbyist-filing hours distribution (3,092 filings)

All 3,092 filings have non-null hours fields (the lobbyist parser zero-fills unpopulated cells per the v1.1 contract). The interesting cut is the **non-zero** subset:

- **Filings with hours_communicating > 0:** 1,128 of 3,092 (36.5%). Min 0.08, max 651.0, mean 39.9, median 15.0.
- **Filings with hours_other > 0:** 1,084 of 3,092 (35.1%). Min 0.15, max 3,356.5, mean 115.7, median 34.5.

`hours_communicating > 0` distribution:

| Range | Count |
|---|---:|
| [0–1) | 48 |
| [1–5) | 228 |
| [5–10) | 166 |
| [10–25) | 254 |
| [25–50) | 160 |
| [50–100) | 136 |
| [100–250) | 117 |
| [250–500) | 17 |
| [500–1000) | 2 |
| [1000+) | 0 |

The 2 filings in [500-1000) are both attributable to **Deanna Pettack (11072, School Administrators Alliance)** — H1 2025 reports 651 hrs communicating + 3,356.5 hrs "other"; H2 2025 reports 565.5 + 3,038. Per-filing totals of 4,007 and 3,604 hours imply ≈32 working hours per day across a 125-working-day semester. **This is not physically possible for one individual.** Probable interpretation: the SAA registers Pettack as their lobbyist and books cumulative organization-wide lobbying-adjacent staff hours under her registration. This is a portal/registrant data-entry pattern, not a parser bug — the parser faithfully reflects what the page serves. Worth a cross-state comparison once a second state is parsed (does the "organization aggregates hours under one lobbyist" pattern persist?).

Top-10 lobbyists by total hours (sum of communicating + other across all 4 periods) all live in this domain — most are at 1,500–3,000 hrs total for the session, several plausibly accounting for individual heavy lobbying load (≈12–25 hrs/week sustained), with Pettack as a clear outlier:

| Rank | Lobbyist ID | Total hours | Name |
|---:|---|---:|---|
| 1 | 11072 | 7,611.00 | Deanna Pettack (outlier — see above) |
| 2 | 11265 | 2,685.10 | Rebecca Hogan |
| 3 | 11221 | 2,301.00 | Cori Lamont |
| 4 | 12667 | 2,094.25 | Paul Rozeski |
| 5 | 11141 | 2,067.25 | Eric Petersen |
| 6 | 11293 | 1,912.00 | Justin Moralez |
| 7 | 11202 | 1,875.50 | Catherine McDermott |
| 8 | 11239 | 1,824.75 | Andrew Engel |
| 9 | 11411 | 1,662.50 | Steve Lyons |
| 10 | 11290 | 1,650.75 | Forbes McIntosh |

### 8. `contact_details_json` address bug — **diagnosed and fixed mid-session**

**Original framing in this doc was wrong** — I told you "the parser correctly preserves what the WI portal serves; the address blob is malformed at source." A code-reviewer pass before merge surfaced that the address pollution is **parser-side concatenation**, not portal-side serving. The WI portal serves the contact card with each field as a distinct visual element prefixed with an `<i class="fa-{phone,envelope,globe}">` icon; the value text follows the icon as a NavigableString *sibling*, not a descendant. Both parsers' `_extract_address` were treating those NavigableString siblings as part of the address.

Two distinct leaks were happening:

1. **Phone digits leaked into address on every row, both sides** — the icon-skip logic skipped the `<i>` tag but not the immediately-following NavigableString that holds the phone number.
2. **Firm name leaked into address on the lobbyist side** — the lobbyist parser walked `person_info.descendants`, and the firm-name `<div>` (no class to filter on) passed through. So Brooks's address ended up as `"Paladin Consulting Group LLC\n1 S. Pinckney Street, Suite 318\nMadison, WI 53703\n(608) 467-7933"` instead of `"1 S. Pinckney Street, Suite 318\nMadison, WI 53703"`.

**Fix:**

- **`principal_meta_parser._extract_address`** — track whether the previous child during the sibling-walk was an `<i>` tag; if so, skip the next NavigableString (it's the icon's value text, handled in the typed extractors).
- **`lobbyist_time_report_parser._extract_address`** — replaced the descendants-walk with a structural-target: find the `col-lg-6` div that has no `<i>` children (the address column, distinguished from the contact column by absence of icons), walk only its NavigableString children.

**TDD coverage added** (4 new tests):

- `test_dairy_address_is_only_street_and_city_state_zip` — Dairy 11590 (principal)
- `test_lexia_address_is_only_street_and_city_state_zip` — Lexia 11348 (principal)
- `test_brooks_address_is_only_street_and_city_state_zip` — Brooks 11052 (lobbyist)
- `test_pfaff_address_is_only_street_and_city_state_zip` — Pfaff 11042 (lobbyist)

Each test asserts exact-equality on the expected clean address. All 4 RED at first, all 4 GREEN after the fixes.

**TSVs re-materialized** with the fixed parsers (18.9 s wall, identical row counts 944/773/1706/3092/7345/0). Spot-check on the 5 rows shown above (`11040`, `11041`, `11044`, `11308`, `11590`, `11052`) confirms clean addresses: no phone duplication, no firm-name pollution, no "Self-Employed Lobbyist - No Firm or Org" string.

**One real portal-side data-entry artifact preserved** (genuinely portal, not parser): lobbyist 11308 (Nels Rude) still shows `"Madison, WI 53703, WI 53703"` — the duplicated state-zip is in the WI portal HTML itself, exactly as served. No parser action warranted.

**Open follow-up** (deferred to a separate branch): split the typed `address` ContactDetail into structured sub-fields (street vs city-state-zip) for downstream geocoding. Currently the typed entry is correct at the postal-address granularity but not pre-split into typed lines. Lower priority than the bug fix, hence the separate branch.

---

## Process note (also added to Phase 7 doc-drift fix)

The plan-Phase-7 WCTA doc drift (`results/20260526_wi_principal_side_scrape_results.md` line 65, "Wisconsin Cable Telecommunications Association" → "Wisconsin County Treasurers Association") is fixed in the same commit as this results doc. The principle going forward: **future writeups should verify entity names from the page body, not infer from the acronym + context.** "WCTA" is genuinely ambiguous in Wisconsin lobbying — both Cable Telecommunications and County Treasurers use it — and the principal-side scrape writeup inferred the wrong expansion from context.

---

## Open items (not for this session)

- **Synthetic ParseFailure rows for null-html-skipped checkpoints** — small materializer change to make soft-404 cases observable in the warnings TSV. (Finding §1.)
- **Low-spend-exempt flag on Organization** — v1.3 candidate. (Finding §2.)
- **Address sub-field split** — the address ContactDetail is correct at the postal-address granularity now (Finding §8 fix landed), but downstream geocoding may want it pre-split into street vs city-state-zip typed entries. Lower priority than the bug that motivated the rewrite.
- **Cross-state validation of the "organization-aggregates-hours-under-one-lobbyist" pattern** — open until a second state's Tier-2 lands. (Finding §7, Pettack outlier.)
- **Classify the 56 zero-filing principals** — distinguish new-registrant vs empty-expenditure-section vs other shapes. (Finding §5.)
- **6 vs 4 bucket count** — the parser/plan reference "6 activity-allocation buckets" but only 4 ever appear in real data. Confirmed by reading `_BUCKET_HEADERS` in `principal_meta_parser.py`: the parser declares all 6 (`Legislative Bills/Resolutions`, `Budget Bill Subjects`, `Administrative Rulemaking Proceedings`, `Topics Not Yet Assigned A Bill Or Rule Number`, `Minor Efforts`, `Other Matters`) but the last two have 0 rows in 2025-2026. Worth re-checking next session whether they're portal-allowed-but-unused or dead-code constants.

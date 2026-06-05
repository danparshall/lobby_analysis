# Wisconsin lobbying disclosure — 2025-2026 session (MVP release)

A snapshot of structured lobbying-disclosure data extracted from the [Wisconsin Ethics Commission's lobbying portal](https://lobbying.wi.gov) for the **2025-2026 legislative session**. This is the first MVP release from the `lobby_analysis` project — six normalized TSVs covering principals (the organizations doing the lobbying), lobbyists, their authorization edges, and per-filing expenditure / hours / bill-effort records.

**Audience:** colleagues kicking the tires on the project's pull-track output. This is provisional research data, not a published product — see "Caveats" below.

---

## Provenance

| | |
|---|---|
| **Source** | `https://lobbying.wi.gov` (principal-side and lobbyist-side scrape, 2026-05-25 → 2026-05-26 snapshot) |
| **Coverage** | Wisconsin 2025-2026 legislative session — semester filings H1 (Jan-Jun 2025) and H2 (Jul-Dec 2025) |
| **Pipeline** | Two-tier scrape: Tier-1 = authorization grid (lobbyist↔principal edges); Tier-2 = detail pages (principal expenditure reports + lobbyist activity reports + per-bill effort allocations) |
| **Generating code** | [`src/lobby_analysis/io/wi/`](../../src/lobby_analysis/io/wi/) at merge commit [`5fcc6ac`](https://github.com/danparshall/lobby_analysis/commit/5fcc6ac). Address-parser fix at [`fbd8a4c`](https://github.com/danparshall/lobby_analysis/commit/fbd8a4c) is included in these files. |
| **Reproducer** | `uv run python -m lobby_analysis.io.wi.tier_2_materialize_cli` (after running the Tier-1 scrape; see the [archived branch's RESEARCH_LOG](../../docs/historical/wi-disclosure-explore/RESEARCH_LOG.md) for full pipeline order) |
| **Run wall time** | ~19 s end-to-end (Tier-2 materialize from cached HTML checkpoints) |
| **Parse failures** | 0 |

---

## Files

All files are tab-separated (`.tsv`) with a single header row. Total size: **~2.9 MB**.

### Entities

| File | Rows | What it is |
|---|---:|---|
| **`WI_principals.tsv`** | 944 | One row per registered principal (the organization). Columns: `principal_id`, `id`, `name`, `source_state`, `classification`, `legal_form`, `sector`, `contact_details_json`, `ceo_name`, `business_or_interest`, `lobbying_interests_prose`. |
| **`WI_lobbyists.tsv`** | 773 | One row per registered lobbyist (the natural person). Columns: `lobbyist_id`, `id`, `name`, `source_state`, `contact_details_json`. |
| **`WI_lobbyist_principal_authorizations_unified.tsv`** | 2,254 | The lobbyist↔principal edge graph. Columns: `lobbyist_id`, `principal_id`, `authorized_on`, `withdrawn_on`, `discovered_via` ∈ {`lobbyist`, `principal`, `both`}, `lobbyist_in_grid`. The `discovered_via` column records provenance: principal-side scrape is a strict superset of the lobbyist-side on this snapshot (+3 edges only the principal side knew about). |

### Filings

| File | Rows | What it is |
|---|---:|---|
| **`WI_principal_filings.tsv`** | 1,706 | Semester expenditure reports filed by principals. ≤ 2 rows per principal × (H1 2025, H2 2025). Columns: `filing_id`, `principal_id`, `state`, `filing_type` (= `expenditure_report`), `filer_role`, `reporting_period_start`, `reporting_period_end`, `total_expenditure`, `total_hours_communicating`, `total_hours_other`, `source_url`. |
| **`WI_lobbyist_filings.tsv`** | 3,092 | Quarterly activity reports filed by lobbyists. Exactly **4 × 773** rows (the WI portal always emits 4 quarterly cells per registered lobbyist; cells with no activity zero-fill). Columns: `filing_id`, `lobbyist_id`, `state`, `filing_type` (= `activity_report`), `filer_role`, `reporting_period_start`, `reporting_period_end`, `total_hours_communicating`, `total_hours_other`, `source_url`. |
| **`WI_principal_bill_efforts.tsv`** | 7,345 | Per-(principal, bucket, item, period) bill-effort allocations from principal expenditure reports. Columns: `principal_id`, `bucket`, `item_id`, `item_name`, `item_description`, `period_label`, `percent`. |

### Schema reference

Field semantics come from the Pydantic models at [`src/lobby_analysis/models/`](../../src/lobby_analysis/models/) (entity-side follows [Popolo](http://www.popoloproject.com/) / Open Civic Data conventions; filing-side uses a complementary OCD-style `Disclosures` schema). `contact_details_json` is a JSON-encoded list of Popolo-style `ContactDetail` objects (`{type, value, note}` with `type ∈ {phone, email, address}`).

### Derived datasets

- **[`chain/`](chain/)** — modeled per-(semester, principal, lobbyist, bill, sponsor) chain joining these source TSVs to bill sponsorship from the WI Legislature (via Plural Policy / OpenStates), with per-lobbyist effort hours inferred via IPF and per-sponsor effort hours normalized by primary-sponsor count. See [`chain/README.md`](chain/README.md) for schema, methodology, and limitations. 115,229 rows / ~38 MB.

---

## Headline aggregates

(Reproduced from [the run results doc](../../docs/historical/wi-disclosure-explore/results/20260526_wi_tier_2_parser_results.md) — see that file for the full writeup, including methodology notes and parser-vs-portal caveats.)

- **Total principal-side spend across all 944 principals:** **$47,458,304.69**
- **Total principal-side hours communicating:** 48,292.20
- **Total principal-side hours other:** 129,397.84
- **Principals with ≥ 1 filing:** 888 / 944 (94.1%)
- **Principals with > $0 spend:** 812

### Top-10 principals by YTD spend (2025 H1 + H2)

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

DoorDash is a sharp outlier (>2× the #2). Cross-validation against the WMC entry ($911,593.49) matched the value independently captured during the Phase-0 fixture-capture session.

### Bill-effort bucket distribution (7,345 rows)

| Bucket | Rows | % | Distinct principals |
|---|---:|---:|---:|
| Legislative Bills/Resolutions | 4,035 | 54.9% | 526 |
| Topics Not Yet Assigned A Bill Or Rule Number | 2,327 | 31.7% | 652 |
| Budget Bill Subjects | 856 | 11.7% | 362 |
| Administrative Rulemaking Proceedings | 127 | 1.7% | 57 |
| **Total** | **7,345** | **100.0%** | — |

The WI portal structurally allows 6 buckets; only 4 appear in real 2025-2026 data. The two unused (`Minor Efforts`, `Other Matters`) are portal-allowed-but-empty for this session.

---

## Caveats

These are known data shapes that don't map cleanly into the schema, or genuine portal-side artifacts the parser faithfully preserves. **Read before using the data for any quantitative claim.**

1. **Pettack outlier in lobbyist hours.** Lobbyist 11072 (Deanna Pettack, School Administrators Alliance) shows 7,611 total hours across the session — physically impossible for one individual (≈32 working-hours/day for 125 working days). Probable interpretation: the SAA registers Pettack as their lobbyist and books cumulative org-wide lobbying-adjacent staff hours under her registration. This is a portal/registrant data-entry pattern, not a parser bug. Worth flagging in any per-lobbyist analysis.

2. **Low-spend-exempt principals.** Some principals (e.g., WCTA 12997) file with `$0.00` in only one of the two semester periods rather than emitting a zero-row for both. The v1.1 `Organization` schema has no `low_spend_exempt` flag yet (v1.3 candidate). Empty-period semantics: a missing period for a principal that has ≥1 filing means "no filing emitted for that period," not "$0 in that period."

3. **56 principals with zero filings.** 2 are privacy-redacted (IDs 11530, 13137); the other 54 are a mix of recently-registered principals with no semester filings yet and populated principal pages where the expenditure section is empty. Not exhaustively classified.

4. **Lobbyist 12717 (Neumann-Ortiz) silently absent.** The lobbyist-side fetcher detected a soft-404 at scrape time (body marker, not HTTP status), so this lobbyist has no row in `WI_lobbyists.tsv` and contributes nothing to `WI_lobbyist_filings.tsv`. There is no synthetic ParseFailure row for null-html-skipped checkpoints (open follow-up).

5. **Address sub-field split (open follow-up).** `contact_details_json` addresses are clean at the postal-address granularity (the phone-and-firm-name leak bug, [`fbd8a4c`](https://github.com/danparshall/lobby_analysis/commit/fbd8a4c), is fixed in this release), but addresses are *not* pre-split into typed street / city / state / zip lines. Geocoding consumers will need to parse the address string.

6. **One genuine portal-side data artifact preserved.** Lobbyist 11308 (Nels Rude) has `"Madison, WI 53703, WI 53703"` — duplicated state+zip in the WI portal HTML itself, exactly as served. No parser action warranted.

7. **"WCTA" is ambiguous in Wisconsin lobbying.** Both Wisconsin Cable Telecommunications Association and Wisconsin County Treasurers Association use the acronym. Always verify expansion from the principal name in `WI_principals.tsv`, not from acronym + context.

---

## License & usage

Source data is public-record disclosure data published by the Wisconsin Ethics Commission. This MVP release is shared under the project's repo license (see repo root). If you build on it, please cite the source portal and the generating commit ([`5fcc6ac`](https://github.com/danparshall/lobby_analysis/commit/5fcc6ac)).

For methodology details, the multi-session research log on the archived [`wi-disclosure-explore`](../../docs/historical/wi-disclosure-explore/) branch documents the full Tier-1 and Tier-2 development arc.

# New York lobbying disclosure — 2025 (MVP release)

A snapshot of structured lobbying-disclosure data extracted from [New York State's Open NY portal](https://data.ny.gov) — specifically the *Client Semi-Annual Report* dataset filed with the [Joint Commission on Public Ethics / Commission on Ethics and Lobbying in Government](https://ethics.ny.gov/) — for **reporting year 2025**. Four normalized TSVs covering the clients, lobbyist firms, their per-filing compensation, and the bill-level engagements those filings disclose.

**Audience:** project colleagues evaluating the NY pull-track output. This is provisional research data, not a published product — read "Caveats" before any quantitative use.

NY is structurally different from the Wisconsin release: the lobbyist→bill link WI had to *model* (WI lobbyists file only aggregate hours) is **directly disclosed** in NY, transactionally and bill-keyed. So there is no IPF/allocation layer — `NY_filing_bill_links.tsv` is a direct projection of what filers reported. The lawmaker → bill half of the chain (via Open States) is Phase 4, not in this release.

---

## Provenance

| | |
|---|---|
| **Source** | `https://data.ny.gov` — `client_semiannual` dataset (Socrata id [`qym9-xzj6`](https://data.ny.gov/d/qym9-xzj6), "Client Semi-Annual Report (Beginning 2019)"), pulled 2026-06-05 |
| **Coverage** | New York **reporting year 2025**, both semi-annual periods (`Jan/June` + `July/Dec`) |
| **Acquisition** | `io/ny/acquire.download_resource_csv` over the SODA `/resource/<id>.csv` endpoint, projected to the 9 consumed columns and filtered `$where=reporting_year='2025'` → 11,200,080 raw rows / 1.9 GB (gitignored under `data/raw/ny/2025/`). Row count verified against the live `count(*)` aggregate. |
| **Pipeline** | `read_csv → columns.normalize_columns → parse.add_bill_id_column → grain.collapse_to_filing_grain → materialize.materialize_ny`. NY filings are denormalized ~1,300× (11.2M rows → 10,870 filings); the grain step resolves amendment-supersession (keep `max(form_submission_id)` per business key) and collapses the row explosion, carrying — never summing — the replicated filing compensation. |
| **Generating code** | [`src/lobby_analysis/io/ny/`](../../src/lobby_analysis/io/ny/) at commit `cb59653` (acquisition `download_resource_csv` at `4614d73`). |
| **Reproducer** | `uv run python scripts/ny_pull_2025.py` then `uv run python -m lobby_analysis.io.ny.materialize_cli --input data/raw/ny/2025/client_semiannual.csv --dataset client_semiannual --output-dir releases/ny` |
| **Run wall time** | ~5.2 min pull + ~55 s materialize |
| **Money discipline** | `Decimal` end-to-end (the materializer bypasses `LobbyingFiling.total_compensation`, which is typed `float`); `"$"`/`""`/absent → empty cell, never a fabricated `0`. |

---

## Files

All files are tab-separated (`.tsv`) with a single header row. Total size: **~11 MB**.

### Entities

| File | Rows | What it is |
|---|---:|---|
| **`NY_clients.tsv`** | 4,373 | One row per distinct beneficial client (Popolo `Organization`, id `NY-client-{slug}`). Columns: `id`, `name`, `source_state`, `classification`, `legal_form`, `sector`, `contact_details_json`. |
| **`NY_lobbyists.tsv`** | 1,333 | One row per distinct principal-lobbyist firm (Popolo `Organization`, id `NY-lobbyist-{slug}`). Same column set as clients. |

### Filings

| File | Rows | What it is |
|---|---:|---|
| **`NY_filings.tsv`** | 10,870 | One row per firm-filing — a `(reporting_year, reporting_period, form_submission_id, lobbyist firm, client)` tuple. Columns: `filing_id` (= `form_submission_id`, the **client's** report id), `id` (`NY-filing-{submission}-{firm}-{client}`, unique), `state`, `filing_type` (= `expenditure_report`), `filer_role` (= `firm`), `reporting_year`, `reporting_period`, `lobbyist_id`, `client_id`, `total_compensation`. |
| **`NY_filing_bill_links.tsv`** | 47,204 | One row per `(firm-filing, real state bill)`. Columns: `filing_id`, `lobbyist_id`, `client_id`, `bill_id` (canonical, amendment suffix preserved), `bill_print_version`, `comp_per_bill` (even-split), `filing_compensation`, `n_bills_in_filing`, `reporting_year`, `reporting_period`. A filing with no real bill appears in `NY_filings.tsv` (its dollars are preserved) but contributes **zero** link rows. |

### Disclosed lawmaker contacts (`parties_lobbied`)

| File | Rows | What it is |
|---|---:|---|
| **`NY_filing_parties_lobbied.tsv`** | 168,430 | One row per `(firm-filing, distinct party lobbied)` — NY's **disclosed** "who was lobbied" field, resolved to Open States `ocd-person` ids where it names a state legislator. Columns: `reporting_year`, `reporting_period`, `filing_id`, `lobbyist_id`, `client_id`, `party_lobbied_raw` (the verbatim disclosed string), `party_lobbied_name` (title/noise-stripped legislator name, when resolved), `party_lobbied_person_id` (`ocd-person/…`, when resolved), `resolved` (`True`/`False`). |

**Disclosed, not inferred — this is a different edge from the sponsor chain.** The
chain's lawmaker edge (Phase 4) is the bill *primary sponsor*, *inferred* via Open
States. `parties_lobbied` is the genuinely *disclosed* contact, and it surfaces
leadership, committee chairs, executive offices, and municipal officials a sponsor
join never could. **Unweighted** — it carries no compensation (no conservation
invariant); the metric is the resolution rate.

**Resolution (2025):** of 98,352 edges that name a **state legislator**
(`Senator` / `Assembly member`), **98.6% resolved** to a specific `ocd-person`
(**213 distinct legislators — the full NY legislature**, 150 Assembly + 63
Senate). The other ~40% of all edges name parties that are **not** state
legislators — NYC municipal officials (Council members, the Mayor's office), state
executive offices / agencies, chamber program/counsel staff, and
"entire-legislature" broadcasts — kept verbatim with `resolved=False`, never
coerced into a legislator id. Overall **57.6%** of edges resolve. Matching is a
deterministic first-name+last-name key, **accent-folded** (NFKD diacritic strip,
so the disclosure's `Jose Serrano` and the roster's `José Serrano` agree) and
**nickname-canonicalized** (the `nicknames` dictionary maps `Liz`↔`Elizabeth`,
`Chris`↔`Christopher` in both directions, with a collision guard so distinct people
who share a surname are never merged); zero collisions on the NY roster; see
[Phase 0](../../docs/active/ny-disclosure-explore/results/20260606_ny_parties_lobbied_grain.md)
and the [nickname recovery](../../docs/active/ny-disclosure-explore/results/20260606_ny_nickname_matcher_recovery.md).
The residual ~1.4% of legislator edges are *former* members (left for other
office, resigned), one-character spelling variants, and a few non-sponsoring
current members absent from the sponsorship roster. **Caveat 10** has the full
discipline. Aggregates:
[`results/20260606_ny_parties_lobbied_release.md`](../../docs/active/ny-disclosure-explore/results/20260606_ny_parties_lobbied_release.md).

### Schema reference

Field semantics come from the Pydantic models at [`src/lobby_analysis/models/`](../../src/lobby_analysis/models/) (entity-side follows [Popolo](http://www.popoloproject.com/) / Open Civic Data; filing-side an OCD-style disclosure schema). `contact_details_json` is a JSON list of Popolo `ContactDetail` objects — empty (`[]`) for every NY client/firm, since `client_semiannual` carries no contact info.

### `comp_per_bill` — the even-split model

NY discloses **no per-bill dollar weight**: a filing reports one total compensation and lists the bills lobbied. `comp_per_bill = filing_compensation / n_bills_in_filing`, distributed with integer-cent arithmetic so `SUM(comp_per_bill) == filing_compensation` **exactly** per filing (verified: 0 violations across 4,328 bill-linked filings). This is a *uniform* split (analogous to WI's per-sponsor split, **not** its disclosed-percent per-bill split) — NY's spend chain is less modeled than WI's, because NY filers don't report the weighting. Always carry `filing_compensation` + `n_bills_in_filing` alongside `comp_per_bill` so a consumer can re-weight.

---

## Headline aggregates

- **Total compensation, 2025:** **$345,762,462.00** across 10,870 firm-filings. (Independently reconciled against a from-raw recompute, delta $0.00.)
- **Clients:** 4,373 · **Lobbyist firms:** 1,333 · **Firm-filings:** 10,870 · **Bill-link rows:** 47,204
- **Distinct bills lobbied:** 6,352 (as filed, with amendment suffix). Stripping the suffix for the Open States join key collapses these to **5,449** distinct base bills — Phase 4 measures match rate both ways.
- **Chain reach:** $153,064,191 (44%) of compensation is on filings that name ≥1 real state bill; the remaining $192,698,271 (56%) is on filings whose focus is non-bill (funding, rulemaking, municipal matters, procurement) or whose bill reference doesn't parse — money preserved in `NY_filings.tsv`, but not chain-eligible.

### Top 10 lobbyist firms by 2025 compensation

| Rank | YTD comp | Firm |
|---:|---:|---|
| 1 | $24,217,924 | Brown & Weinraub Advisors, LLC |
| 2 | $17,330,648 | Bolton-St. Johns, LLC |
| 3 | $17,287,375 | Kasirer LLC |
| 4 | $14,927,102 | Greenberg Traurig, LLP |
| 5 | $9,442,961 | Ostroff Associates, Inc. |

These are New York's recognized top-tier lobbying firms, a strong face-validity check. The Brown & Weinraub total was independently reconciled to the raw API (exact match, including the multi-firm shared-submission filings that the Phase-3 spot-check used to surface a dollar-loss bug — see Caveat 1).

### Focus-type & bill parse coverage

`type_of_lobbying_focus` is **State Bill** on 87.7% of raw rows; the remainder is State Funding (2.5%), Municipal Bill (2.3%), Municipal Land Use (2.3%), rulemaking, procurement, etc. Of State-Bill rows, **85.4% carry a `focus_identifying_number` that parses to a canonical `bill_id`** (`S###`/`A###`, optional `-A/-B` suffix). The non-parsing 14.6% are prose ("100 foot rule", "$100m Community schools") or non-canonical references that embed a bill number in free text (e.g. "100 Foot Rule (S8417/A8888)") — a Phase-4 extraction opportunity, not corrupted data (`derive_bill_id` degrades them to "not chain-eligible").

---

## Caveats

**Read before using the data for any quantitative claim.**

1. **`form_submission_id` is the *client's* semi-annual report id — not a per-firm filing key.** One submission is shared across every firm a client retains (26% of 2025 submissions list >1 firm; e.g. Accenture's report lists 6 firms, each with its own compensation). Filing identity here is therefore `(year, period, submission, firm, client)`. An earlier materializer keyed on `(submission, client)` and silently dropped co-retained firms' dollars (a $108.9M / 32% loss); the live Phase-3 spot-check caught it and it is fixed in this release ([`grain.py`](../../src/lobby_analysis/io/ny/grain.py) `FILING_KEY`, [`materialize.py`](../../src/lobby_analysis/io/ny/materialize.py)). If you join these tables, **always include `lobbyist_id`**, never `filing_id` alone.

2. **Compensation only — no expenses.** `client_semiannual` reports compensation paid to firms. Itemized lobbying expenses (and individual-lobbyist names) live in the separate `lobbyist_bimonthly` dataset, **not** in this build. "Total compensation" here is not "total lobbying spend."

3. **Coalition `beneficial_client` cells.** Some filings pack many beneficiaries into one semicolon-delimited `beneficial_client` field; the parser treats the whole list as a single client entity (with a very long slug id). Splitting them is a modeling decision with no disclosed per-beneficiary dollar weight — deferred. Such composite-client rows are real filings, not duplicates.

4. **HTML entities are decoded.** Client names arrive HTML-encoded from the portal (`Solow Realty &amp; Development`); the parser decodes them to literal characters (`Solow Realty & Development`) and derives entity ids from the decoded name. This is load-bearing for the chain: the encoded `&amp;` ends in `;`, the coalition delimiter, so an undecoded name would fracture in the chain's coalition split (`AT&amp;T` → `AT&amp` + `T`).

5. **`bill_id` and `bill_print_version` are identical in this release** (both the suffixed canonical form, e.g. `S550-A`). The suffix is deliberately preserved at this stage; the Phase-4 chain normalizer strips it to the Open States base key and uses `bill_print_version` to measure match rate both ways.

6. **Bill-number zero-padding is inconsistent at the source** (`A00804-C` vs `A804` vs `A1001`). `derive_bill_id` preserves the digits as filed, so two paddings of the same bill currently fork into distinct `bill_id`s. Phase 4's Open States normalizer must canonicalize padding before the join.

7. **2025 only.** This is a single-year MVP. The dataset spans 2019–present (66.9M rows); multi-year materialization is deferred.

8. **No stance/position.** NY discloses *which* bills were lobbied, not *for or against*. There is no support/oppose signal in this data (confirmed in Phase 0).

9. **`LobbyingFiling.total_compensation` is typed `float`.** The materializer writes the exact `Decimal` straight from the grain (TSVs are exact), but the Pydantic model field would coerce to `float`; a `Decimal`-typing pass is an open follow-up. Trust the TSV, not a round-trip through the model field.

10. **`parties_lobbied` resolution is non-uniform — do NOT read `resolved=False` density as "less lobbied."** Only legislator-titled values that matched the state legislator roster are resolved (`resolved=True` ⟺ a specific named *state* legislator). The unresolved rows are biased two ways: (a) by design, parties that aren't state legislators (NYC municipal officials, executive offices, agencies, broadcasts — 41% of edges); and (b) a known residual gap — accents and standard nicknames are now canonicalized, so the remaining unresolved legislators are *former* members (correctly not mapped to a current `ocd-person`), one-character spelling variants, and the occasional non-sponsoring current member absent from the *sponsorship* roster. A naive "times each legislator was lobbied" count will undercount exactly the harder-to-match members. The edge is also reported per-firm: NY discloses `parties_lobbied` at the client-submission level and it replicates onto each co-retained firm's filing, so a party attaches to every firm on the client's filing, not to a specific firm's contact.

---

## License & usage

Source data is public-record disclosure data published by New York State (Open NY / Commission on Ethics and Lobbying in Government). This MVP release is shared under the project's repo license (see repo root). If you build on it, please cite the source portal and the generating commit (`cb59653`).

For the full development arc, see the [`ny-disclosure-explore` research log](../../docs/active/ny-disclosure-explore/RESEARCH_LOG.md).

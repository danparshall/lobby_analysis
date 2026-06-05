# NY lobbying chain — `NY_chain_2025.tsv`

The end-to-end **company → lobbyist → bill → lawmaker → $** chain for New York
state lobbying, 2025. One row links a beneficiary (the company that benefits),
the lobbying firm it retained, a bill that firm lobbied on its behalf, that
bill's sponsoring lawmaker, and the compensation attributed to that
company–bill cell.

Built from the Phase-3 `releases/ny/` tables joined to the Open States / Plural
Policy NY bill-sponsorship bundle. **No IPF / allocation modeling** — unlike WI
(whose lobbyist↔bill link had to be modeled because WI lobbyists report only
aggregate hours), NY discloses the lobbyist→bill link directly, so the chain is
a join plus two deterministic transforms (coalition split + bill-id
normalization).

## Aggregates (2025)

| metric | value |
|---|---|
| chain rows | 87,534 |
| distinct lobbying firms | 927 |
| distinct beneficiaries (post coalition-split) | 1,892 |
| distinct bills (source `bill_id`) | 6,352 |
| distinct sponsoring lawmakers (`ocd-person`) | 213 (= full NY legislature: 150 Assembly + 63 Senate) |
| rows resolved to an OS bill+sponsor (`os_matched=True`) | 87,446 (99.9%) |
| distinct bills **un**matched (flagged, not dropped) | 30 (0.5%) |
| coalition filings (M>1 beneficiaries) | 476 |
| **total compensation, summed over distinct cells** | **$153,064,191.00** |

The total reconciles **exactly** ($0 delta) against the Phase-3 release's
bill-linked compensation. This is the bill-linked subset of NY lobbying spend;
the full 2025 release compensation is $345.76M (the remainder is on filings with
no `State Bill` focus, which are not chain-eligible).

## Schema

One row per `(reporting_period, lobbyist_firm, beneficiary, bill, sponsor)`.

| column | meaning |
|---|---|
| `reporting_year`, `reporting_period` | filing period (`Jan/June` / `July/Dec`) |
| `filing_id` | NY `form_submission_id` — the **client's** semi-annual report id, shared across every firm the client retains |
| `lobbyist_id`, `lobbyist_name` | the lobbying **firm** (`principal_lobbyist`) hired to do the work |
| `client_id` | the raw disclosed `beneficial_client` cell (the coalition parent, for traceability back to `releases/ny/`) |
| `beneficiary_id`, `beneficiary_name` | one beneficiary after splitting a semicolon-delimited coalition cell |
| `bill_id` | the source NY bill id (base form, e.g. `A1668`) |
| `bill_print_version` | the suffixed print actually lobbied (e.g. `S550-A`), preserved |
| `os_bill_identifier` | the Open States join key (`A 1668`), empty if unmatched |
| `bill_title` | Open States bill title |
| `sponsor_lawmaker_id`, `sponsor_lawmaker_name` | the bill's **primary sponsor** (`ocd-person` id + name); empty if unmatched |
| `comp_per_cell` | compensation attributed to this (beneficiary, bill) cell |
| `filing_compensation` | the filing's total compensation (carried, for re-aggregation) |
| `n_beneficiaries_in_filing` (M), `n_bills_in_filing` (N) | the split denominators |
| `os_matched` | `True` if the bill resolved to an OS bill with a structured sponsor |

## How dollars are attributed (conservation)

A filing with compensation `C`, `M` beneficiaries and `N` bills is split evenly
into `M·N` cells, each carrying `comp_per_cell = C / (M·N)`. The split is a
single integer-cent `even_split(C, M*N)`, so the cells sum to `C` **exactly**
(no rounding loss, remainders never compound across the two axes).

Two **load-bearing** rules for anyone aggregating this file:

1. **A cell's identity is `(filing_id, lobbyist_id, beneficiary_id, bill_id)` —
   never `filing_id` alone.** `filing_id` is the client's shared submission id;
   26% of submissions list more than one firm, each with its own compensation.
   Summing `comp_per_cell` after de-duplicating on `filing_id` alone silently
   drops co-retained firms' dollars (the chain-layer analog of the $108.9M
   Phase-3 firm-collapse bug).
2. **Do not sum `comp_per_cell` across the sponsor rows of one cell.** When a
   bill has multiple primary sponsors, the cell's `comp_per_cell` is
   **replicated** across those sponsor rows (the dollars attach to the bill, not
   subdivided per lawmaker). De-duplicate to distinct cells before summing.

NY discloses no per-bill or per-beneficiary effort weight, so the split is
**uniform** — an explicit modeling assumption, not a disclosed allocation.

## Honest limitations

- **The lawmaker is the bill's _primary sponsor_, not a disclosed lobbying
  contact.** The edge means "this company paid to lobby on a bill that lawmaker
  X sponsored" — an *inferred* connection via Open States, **not** a disclosed
  "company lobbied lawmaker Y" meeting. NY *does* publish a `parties_lobbied`
  field (a genuine disclosed lawmaker edge), but it was deliberately out of v1
  scope; it is free-text names/titles that would need resolution to canonical
  lawmakers. Ingesting it is the top v1.1 follow-up — see below.
- **Primary sponsors only.** NY bills carry exactly one primary sponsor;
  cosponsors (≈83k edges, in the OS bundle) are excluded from v1.
- **No stance / position.** NY disclosure records *that* a bill was lobbied, not
  for or against.
- **0.5% of bills don't resolve to Open States.** These are flagged
  (`os_matched=False`), never dropped, with dollars preserved. They are mostly
  malformed source ids (e.g. `A51578` — NY Assembly tops out near `A 11019`),
  i.e. lobbyist typos, plus a few plausible numbers absent from the 2025-2026
  OS session.
- **HTML entities (`&amp;`) are undecoded** in some beneficiary names, carried
  verbatim from the Phase-3 release for source fidelity.
- **Session scope.** The OS spine is the NY **2025-2026** regular session; the
  bill-id join uses the base bill (suffix stripped — see methodology).

## Bill-id normalization (the join key)

Open States NY identifiers are `<LETTER><SPACE><UNPADDED-DIGITS>` (`A 1668`,
`S 550`) — a single space, no zero-padding, no print suffix. The lobbying side
is inconsistently padded (`A00804` vs `A804`) and carries print suffixes
(`S550-A`). `normalize_bill_id_to_os` strips the suffix, drops leading zeros,
and inserts the space to match OS exactly. Measured match rate: **99.5% of
distinct bills, 99.8% of link rows** with suffix-stripping, vs only 81.3%
without — i.e. suffix-stripping is worth ~18 points of chain closure.

## Regenerating

```
uv run --active python -m lobby_analysis.allocation.ny.cli chain \
    --release-dir releases/ny \
    --bill-csv-dir data/bills/NY/2025 \
    --output releases/ny/chain/NY_chain_2025.tsv
```

Requires the Open States NY 2025-2026 CSV bundle staged under
`data/bills/NY/2025/` (gitignored; download from
`open.pluralpolicy.com/data/session-csv/`, "New York 2025 Regular Session").

## v1.1 follow-ups

- **`parties_lobbied` as a second, disclosed lawmaker edge.** Requires
  re-pulling `client_semiannual` with the `parties_lobbied` /
  `..._person_lobbied` fields added to the `$select` (the 2025 pull fetched only
  9 fields), then resolving the free-text names/titles to `ocd-person` ids.
- Decode `&amp;` HTML entities in names.
- Fold in cosponsors as a secondary sponsor edge.
- Multi-year backfill (2019→) once the single-year chain is proven.

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

**Audience:** colleagues who want the influence graph "company → lobbyist → bill → lawmaker" for NY 2025 without having to assemble it from the 5 source TSVs themselves. This is a *derived* artifact — different shape than the source TSVs in [`releases/ny/`](..). Read "How dollars are attributed" and "Disclosed lawmakers vs inferred sponsors" before quantitative use.

---

## TL;DR

| | |
|---|---|
| **Rows** | 83,786 |
| **Coverage** | New York State, reporting year 2025 (Jan/June + July/Dec periods) |
| **Distinct lobbying firms** | 927 |
| **Distinct beneficiaries** (post coalition-split) | 1,812 |
| **Distinct bills** (source `bill_id`) | 6,352 |
| **Distinct sponsoring lawmakers** | 213 (= full NY legislature: 150 Assembly + 63 Senate) |
| **Total compensation, conserved** | $153,064,191.00 ($0 delta vs Phase-3 release) |
| **`os_matched` rate** | 99.9% (83,704 of 83,786 rows; 30 distinct bills unmatched and flagged, never dropped) |
| **Modeling layers** | JOIN + coalition split + bill-id normalization — no IPF |

---

## Aggregates (2025)

| metric | value |
|---|---|
| chain rows | 83,786 |
| distinct lobbying firms | 927 |
| distinct beneficiaries (post coalition-split) | 1,812 |
| distinct bills (source `bill_id`) | 6,352 |
| distinct sponsoring lawmakers (`ocd-person`) | 213 (= full NY legislature: 150 Assembly + 63 Senate) |
| rows resolved to an OS bill+sponsor (`os_matched=True`) | 83,704 (99.9%) |
| distinct bills **un**matched (flagged, not dropped) | 30 (0.5%) |
| coalition filings (M>1 beneficiaries) | 276 |
| **total compensation, summed over distinct cells** | **$153,064,191.00** |
| rows with ≥1 resolved disclosed lawmaker (`disclosed_lawmakers ≠ ""`) | 81,803 (97.63%) |
| matched rows where the primary sponsor is in the disclosed set (`sponsor_in_disclosed_set=True`) | 46,937 / 83,704 (56.07%) |
| per-(filing, lobbyist) median `disclosed_only_lawmaker_count` | 24 (mean 35, p75 69, max 200) |

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
| `disclosed_lawmakers` | **filing-grain metadata.** Sorted, `;`-joined set of resolved `ocd-person` IDs from `NY_filing_parties_lobbied.tsv` for this row's `(filing_id, lobbyist_id)`. Empty when no resolved contacts. Attaches to the FILING, not to this specific bill — see caveat below. |
| `sponsor_in_disclosed_set` | `True` iff `sponsor_lawmaker_id` ∈ this row's `disclosed_lawmakers`. Empty sponsor → always `False`. **Read as "this filer disclosed contact with this sponsor on *something* in this filing," NOT as bill-specific evidence** — see caveat. |
| `disclosed_only_lawmaker_count` | per `(filing, lobbyist)`, count of resolved disclosed lawmakers who are NOT primary sponsors of any *matched* bill in the filing. The "leadership / committee-chair" signal. Same int on every row of the group. |

## What this is — a 30-second tour of the chain construction

NY's chain is structurally much simpler than WI's: it's a JOIN, not an IPF. Three steps:

1. **Lobbying disclosure → chain rows.** NY filers (lobbying firms, on behalf of beneficial clients) report `total_compensation` semi-annually, plus the list of bills they lobbied on for that client. The chain composer reads `releases/ny/NY_filings.tsv` and `NY_filing_bill_links.tsv`, then joins on `os_bill_identifier` against the Open States NY 2025-2026 bill bundle to attach each bill's primary sponsor (`ocd-person`).
2. **Coalition split.** When a filing's `beneficial_client` cell names multiple beneficiaries separated by `;` (276 filings in 2025), the compensation is split evenly across `M` beneficiaries. This is a *uniform-share modeling assumption* — no per-beneficiary dollar weight is disclosed.
3. **Per-bill split + sponsor replication.** Within each (beneficiary, bills) sub-filing, compensation is split evenly across the `N` bills lobbied: `comp_per_cell = C / (M·N)`. Each resulting (beneficiary, bill) cell is then **replicated** across the bill's primary-sponsor rows. NY bills in 2025 each have exactly one primary sponsor, so this replication is 1:1 in practice — but the schema and conservation rules are written for general N≥1 forward compatibility.

Step (2) and step (3) both use integer-cent `even_split` arithmetic so cells sum to the filing's compensation **exactly** with no rounding loss.

The chain detects *that* a beneficiary's firm lobbied on a bill whose sponsor is X — it does *not* claim that the firm lobbied X *about that bill*. The disclosed-contact field (`disclosed_lawmakers`) is at the *filing* grain and tells a different story; see "Disclosed lawmakers vs inferred sponsors" below.

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

## Disclosed lawmakers vs inferred sponsors (read this before consuming the new columns)

The chain carries **two** lawmaker signals per row, and they answer different questions:

1. **Inferred (`sponsor_lawmaker_id`, `sponsor_lawmaker_name`).** The bill's
   *primary sponsor* per Open States. This is "who's on the bill," derived from
   the legislative side — not from the filer's disclosure. It is bill-specific.
2. **Disclosed (`disclosed_lawmakers`, `sponsor_in_disclosed_set`,
   `disclosed_only_lawmaker_count`).** Resolved `ocd-person` IDs from
   `NY_filing_parties_lobbied.tsv` (the genuinely disclosed contact field NY
   requires). **Grain: per `(filing_id, lobbyist_id)`** — the same set attaches
   to every chain row in that group, regardless of which bill the row is about.
   This is "who the filer reported lobbying, anywhere in this filing."

**Why `disclosed_lawmakers` is not per-bill.** A Phase-0 grain probe
(2026-06-08, `docs/active/ny-disclosure-explore/results/`) confirmed that
`parties_lobbied` is cartesian against the filing's bill list, not a map. NY
filers disclose a set of contacts per filing, not contact-per-bill. We cannot
recover the per-(lawmaker, bill) tuple from `parties_lobbied`; future schema
work might, this release doesn't claim to.

**Why `sponsor_in_disclosed_set=True` is not bill-specific evidence.** With a
typical fan-out of 36+ disclosed legislators per `(filing, lobbyist)` and a max
near 209 (the full legislature on the biggest filings), inclusion is consistent
with base-rate matching, not specific intent. Read True as "this filer
disclosed contact with this sponsor on *something* in this filing," **not** as
"this filer lobbied this sponsor about this bill." That said, the observed
in-set rate on the matched chain (2026-06-08 build: 56.07% of 83,704 matched
rows) is well short of the saturation you'd see if every sponsor were captured
by sheer set size — so the negative case (`False`) carries some real signal:
44% of matched chain rows have a primary sponsor the filer did NOT disclose
contact with (working through cosponsors, leadership, staff, or non-individual
parties — agencies, broadcasts — that fall outside the resolved-legislator
set).

**The genuinely informative per-group signal** is `disclosed_only_lawmaker_count`
— the count of disclosed lawmakers who are NOT primary sponsors of any matched
bill in the filing. Large values flag leadership / committee chairs / executive
contacts a filer discloses lobbying but whose bills don't appear in the
beneficial-client engagement set. Combined with `sponsor_in_disclosed_set`, a
useful per-group reading is: high `sponsor_in_disclosed_set` rate + low
`disclosed_only_lawmaker_count` → the filer's disclosed contacts and the
engaged bills' sponsors are aligned. High `disclosed_only_lawmaker_count` →
substantial off-sponsor lobbying activity worth surfacing separately.

## Honest limitations

- **The chain's `sponsor_lawmaker_id` is the bill's _primary sponsor_, not a
  disclosed lobbying contact.** That edge means "this company paid to lobby on
  a bill that lawmaker X sponsored" — an *inferred* connection via Open States,
  **not** a disclosed "company lobbied lawmaker Y" meeting. The disclosed
  contact lives in the three new metadata columns (`disclosed_lawmakers`,
  `sponsor_in_disclosed_set`, `disclosed_only_lawmaker_count`) — read the
  "Disclosed vs inferred" section above before using them. Disclosed contact
  attaches at the *filing* grain, not per bill.
- **Primary sponsors only.** NY bills carry exactly one primary sponsor;
  cosponsors (≈83k edges, in the OS bundle) are excluded from v1.
- **No stance / position.** NY disclosure records *that* a bill was lobbied, not
  for or against.
- **0.5% of bills don't resolve to Open States.** These are flagged
  (`os_matched=False`), never dropped, with dollars preserved. They are mostly
  malformed source ids (e.g. `A51578` — NY Assembly tops out near `A 11019`),
  i.e. lobbyist typos, plus a few plausible numbers absent from the 2025-2026
  OS session.
- **HTML entities are decoded.** Names arrive HTML-encoded (`A&amp;E`); the
  parser decodes them (`A&E`) before the coalition split. This is load-bearing,
  not cosmetic: the encoded ampersand `&amp;` ends in a `;`, the same delimiter
  the coalition splitter uses, so an undecoded `AT&amp;T` would fracture into the
  phantom beneficiaries `AT&amp` + `T`. (An earlier build shipped this bug; it
  inflated the coalition-filing count to 476 and split 3,748 rows' dollars across
  phantom members. The fix conserves the per-filing total to the cent.)
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

## Sample analyses (with protective patterns called out)

Each snippet below demonstrates a correct aggregation pattern that respects the conservation rules above. Comments name the gotcha each one avoids.

```python
import pandas as pd
chain = pd.read_csv("NY_chain_2025.tsv", sep="\t")
```

### 1. Top beneficiaries on a given bill

```python
# Each (filing, lobbyist, beneficiary, bill) cell is replicated across the
# bill's primary-sponsor rows with `comp_per_cell` repeated. Dedupe to the cell
# key BEFORE summing comp_per_cell. (In 2025 each bill has exactly one primary
# sponsor so the replication is 1:1, but the rule preserves correctness for
# future builds and is the right discipline regardless.)
target = chain[chain["bill_id"] == "S550"]
cells = target.drop_duplicates(
    subset=["filing_id", "lobbyist_id", "beneficiary_id", "bill_id"]
)
top = (
    cells.groupby("beneficiary_name")["comp_per_cell"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
```

### 2. Top primary sponsors by chain-attributed compensation

```python
# Filter to os_matched=True so unmatched bills (empty sponsor) don't drag in
# a phantom "empty sponsor" bucket. Then dedupe to cell key before summing —
# even though in 2025 N_sponsors=1 always, the dedupe is a no-op safety net
# that protects against future multi-sponsor data without changing today's
# answer.
matched = chain[chain["os_matched"] == True]
cells = matched.drop_duplicates(
    subset=["filing_id", "lobbyist_id", "beneficiary_id", "bill_id"]
)
top_sponsors = (
    cells.groupby(["sponsor_lawmaker_id", "sponsor_lawmaker_name"])[
        "comp_per_cell"
    ]
    .sum()
    .sort_values(ascending=False)
    .head(20)
)
```

### 3. Off-sponsor lobbying activity by (filing, lobbyist)

```python
# `disclosed_only_lawmaker_count` is the count of disclosed lawmakers who are
# NOT primary sponsors of any matched bill in the filing — the leadership /
# committee-chair / executive-contact signal that survives base-rate noise.
# It's the SAME int on every row of a (filing_id, lobbyist_id) group, so
# DEDUPE TO THAT GROUP before ranking by it, or you'll be ranking by
# group-row-count, not by group-value.
off_sponsor = (
    chain.drop_duplicates(subset=["filing_id", "lobbyist_id"])
    .nlargest(20, "disclosed_only_lawmaker_count")[
        ["lobbyist_name", "client_id", "filing_id",
         "disclosed_only_lawmaker_count"]
    ]
)
# sponsor_in_disclosed_set=True is largely base-rate (typical fan-out 36+
# disclosed legislators per filing). disclosed_only_lawmaker_count is the
# genuinely informative per-group signal.
```

### 4. Coalition decomposition for a multi-beneficiary filing

```python
# When a filing names multiple beneficiaries (M>1), NY's chain splits
# filing compensation evenly across (beneficiaries × bills). Pick one
# coalition filing and see the M·N grid of beneficiary × bill cells.
coalition = chain[chain["n_beneficiaries_in_filing"] > 1]
example_filing = coalition.iloc[0]["filing_id"]
this_filing = chain[chain["filing_id"] == example_filing]
# Conservation: comp_per_cell summed across distinct cells of one
# (filing, lobbyist) equals that filing's filing_compensation, exactly.
this_filing_cells = this_filing.drop_duplicates(
    subset=["filing_id", "lobbyist_id", "beneficiary_id", "bill_id"]
)
print(
    this_filing_cells["comp_per_cell"].sum(),
    "==",
    this_filing_cells["filing_compensation"].iloc[0],
)
```

### 5. Joining to external bill-text or bill-actions data via the OS canonical key

```python
# `os_bill_identifier` is the Open States canonical form (`A 1668` / `S 550`)
# — suffix-stripped and zero-unpadded. Use it as the join key against any
# Plural Policy / Open States bill metadata table. The source `bill_id`
# column preserves the lobbying-side form (may be padded or suffixed) and
# `bill_print_version` is the suffixed print actually lobbied (which the
# filer specified). For external joins, prefer os_bill_identifier.
os_bills = (
    chain[chain["os_matched"] == True]
    .drop_duplicates(subset=["os_bill_identifier"])
    [["os_bill_identifier", "bill_id", "bill_print_version", "bill_title"]]
)
```

## Reproducer

The chain depends on the 4 source TSVs in `releases/ny/` (already in this repo on the `ny-disclosure-explore` branch) plus the Open States NY 2025-2026 bulk CSV bundle (external to this repo, gitignored).

```bash
# 1. Fetch the Open States / Plural Policy NY 2025-2026 bill bundle
#    (~few hundred kB)
#    Download "New York 2025 Regular Session" from:
#    https://open.pluralpolicy.com/data/session-csv/
#    Stage it under data/bills/NY/2025/ (gitignored).

# 2. Compose the chain
uv run --active python -m lobby_analysis.allocation.ny.cli chain \
    --release-dir releases/ny \
    --bill-csv-dir data/bills/NY/2025 \
    --output releases/ny/chain/NY_chain_2025.tsv
```

Wall time is on the order of a minute (this is a JOIN, not an IPF). The materialized output is sorted deterministically, so re-runs produce a byte-identical TSV when sources are unchanged.

## v1.1 follow-ups

- **`parties_lobbied` integrated into the chain (2026-06-08).** The disclosed
  contact field is now joined as filing-grain metadata via the three new
  columns above. The full disclosed-contact edge (one row per disclosed
  lawmaker, with raw/resolved fields, including the ~17% non-individual rows —
  agencies, executive offices, broadcasts) continues to live separately in
  `releases/ny/NY_filing_parties_lobbied.tsv` since it is not per-(beneficiary,
  bill) and would be cartesian against the chain's bill grain.
- Fold in cosponsors as a secondary sponsor edge.
- Multi-year backfill (2019→) once the single-year chain is proven.
- A possible Phase-4: a `target_kind` taxonomy for the ~42% non-legislator
  `parties_lobbied` rows (currently `resolved=False`), so the disclosed edge
  becomes fully typed rather than half-resolved.

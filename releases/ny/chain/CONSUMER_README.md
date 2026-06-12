# New York lobbying chain — reader's guide

**A row-per-link record of who paid whom to lobby on which bill in New York
State during calendar year 2025, with the bill's primary sponsor attached.**

This document is the consumer-facing companion to `NY_chain_2025.tsv`. It is
written for someone (or an AI agent) seeing the file for the first time: it
explains what the data is, where it comes from, what questions it can answer,
how to aggregate it without introducing artifacts, and the half-dozen things
that, if you don't know them, will make your analysis subtly wrong.

> If you are already familiar with the project's internals and want the dense
> technical reference (Phase-3/Phase-4 vocabulary, regeneration command, full
> caveats list), read `README.md` in this same directory instead. This file
> intentionally avoids project-internal jargon.

---

## What this is, in plain English

The State of New York requires every lobbying firm to file twice a year and
disclose, among other things: which clients it represents, how much each
client pays, which specific bills it lobbied on for each client, and which
people in state government it directly contacted. NY publishes these filings
as open data on its Socrata portal at <https://data.ny.gov>.

Those raw filings are *transactional* and need significant cleanup before they
answer interesting questions. This chain is the cleaned, joined output: one row
per (filing period, lobbying firm, beneficiary company, bill, primary sponsor)
combination. Each row tells a complete little story:

> "In the first half of 2025, **Whiteman Osterman & Hanna LLP** was paid as
> one of many firms representing a 21-member coalition that included **VSP
> Vision, Inc.**, and lobbied on **S 1464** (the packaging-reduction bill,
> primary sponsor: **Senator Pete Harckham**). The portion of the firm's
> compensation attributed to this specific company-bill cell was **$16.61**."

That's one row of this file. There are 83,786 of them.

This is the **bill-linked** subset of NY lobbying spend: the rows here total
**$153,064,191** across all of 2025. NY's full 2025 lobbying compensation is
about **$345.8M**; the difference (~$192.7M) is on filings that didn't list a
state bill as the lobbying focus (e.g. procurement-related lobbying, executive
agency lobbying), which a bill-keyed chain has no rows for.

## Provenance

| | |
|---|---|
| **Source** | NY State `client_semiannual` dataset (Socrata id `qym9-xzj6`) on <https://data.ny.gov>. NY's filings are administered by the Commission on Ethics and Lobbying in Government (COELIG, formerly JCOPE). |
| **Coverage** | Calendar year 2025, both semi-annual reporting periods (`Jan/June` + `July/Dec`). |
| **Bill metadata** | Open States / Plural Policy NY 2025-2026 regular session bundle, used to attach each bill's title, identifier, and primary sponsor. |
| **Last raw pull** | 2026-06-06 (11,200,080 rows from `data.ny.gov`, verified against the live row count). |
| **This chain built** | 2026-06-08. |
| **Status** | Research artifact, not an official NY State product. The underlying disclosures are public; this is one researcher's pipeline output and its joins/conventions are documented here so a careful reader can verify them. |

## What questions this file is good for

Some example questions and the (correct) way to answer each:

### "Who are the biggest lobbying firms by 2025 spend?"

```python
import pandas as pd
df = pd.read_csv("NY_chain_2025.tsv", sep="\t", dtype=str, keep_default_na=False)
df["comp_per_cell"] = pd.to_numeric(df["comp_per_cell"], errors="coerce")

# Deduplicate to distinct cells FIRST — see "How dollars work" below.
cells = df.drop_duplicates(["filing_id", "lobbyist_id", "beneficiary_id", "bill_id"])
top_firms = (cells.groupby("lobbyist_name")["comp_per_cell"]
                  .sum()
                  .sort_values(ascending=False)
                  .head(10))
```

### "Which bills had the most lobbying money behind them?"

```python
top_bills = (cells.groupby(["os_bill_identifier", "bill_title"])["comp_per_cell"]
                  .sum()
                  .sort_values(ascending=False)
                  .head(20))
```

### "Which beneficiary companies spent the most lobbying on a specific topic?"

Filter `bill_title` for a keyword (e.g. "cannabis", "packaging", "Medicaid"),
then aggregate by `beneficiary_name`. Beware: bill titles are short and not a
substitute for an actual topic taxonomy — they're a useful starting filter,
not the final word.

### "Which lawmakers had the most bills lobbied on?"

```python
lawmaker_bills = (cells[cells["sponsor_lawmaker_id"] != ""]
                  .drop_duplicates(["sponsor_lawmaker_id", "bill_id"])
                  .groupby(["sponsor_lawmaker_id", "sponsor_lawmaker_name"])
                  .size()
                  .sort_values(ascending=False))
```

### "Where is leadership being lobbied off-bill?"

This is the genuinely novel signal this file enables. `disclosed_only_lawmaker_count`
counts, per filing, how many lawmakers were disclosed-as-contacted but are not
primary sponsors of any of the filing's engaged bills. Filings with a high
count are lobbying leadership / committee chairs / floor leaders without
those people being on the bills. Median value across the file is 24; p75 is 69.

```python
leadership_lobbying = (cells.groupby(["filing_id", "lobbyist_id", "lobbyist_name"])
                            [["disclosed_only_lawmaker_count", "comp_per_cell"]]
                            .agg({"disclosed_only_lawmaker_count": "first",
                                  "comp_per_cell": "sum"})
                            .sort_values("disclosed_only_lawmaker_count", ascending=False))
```

## Schema

One row per `(reporting_period, lobbying_firm, beneficiary, bill, primary_sponsor)`.

| column | meaning |
|---|---|
| `reporting_year` | Always 2025 in this file. |
| `reporting_period` | `Jan/June` or `July/Dec` — NY files semi-annually. |
| `filing_id` | The NY `form_submission_id`. **Important:** this is the *client's* report ID, not the firm's. When one client retains multiple firms, the same `filing_id` appears on rows for each firm. |
| `lobbyist_id`, `lobbyist_name` | The lobbying firm hired to do the work. Disambiguates rows that share a `filing_id`. |
| `client_id` | An ID for the row in the upstream `NY_clients.tsv` (see "Companion files" below). For coalition filings (one report for multiple beneficiaries) this points to the coalition parent. |
| `beneficiary_id`, `beneficiary_name` | One company that benefits from the lobbying. For non-coalition filings, this matches the client. For coalition filings, the `client_id`'s coalition string has been split and this row is one beneficiary out of M. |
| `bill_id` | The NY bill ID as the lobbyist reported it (e.g. `A1983`, `S1464`). |
| `bill_print_version` | The amendment-suffixed print actually lobbied (e.g. `S1858-A`). Preserved separately because the bill-id join strips the suffix. |
| `os_bill_identifier` | The Open States join key (e.g. `A 1983`, with a space, no leading zeros). Empty when the bill didn't resolve to Open States. |
| `bill_title` | The bill's title per Open States. Empty when unmatched. |
| `sponsor_lawmaker_id` | The bill's *primary* sponsor as an OpenStates `ocd-person/…` ID. Empty for unmatched bills and for bills whose primary sponsor is a committee rather than an individual (e.g. budget bills sponsored by `Budget Committee`). |
| `sponsor_lawmaker_name` | The primary sponsor's display name (e.g. `Amy Paulin`). For committee sponsors, the committee name. |
| `comp_per_cell` | The compensation attributed to this beneficiary-bill cell, in dollars. Read the next section before summing this. |
| `filing_compensation` | The filing's total reported compensation (the same value appears on all rows of one filing × firm, so a consumer can re-weight without leaving the file). |
| `n_beneficiaries_in_filing` | M — the coalition size for this filing. |
| `n_bills_in_filing` | N — the number of bills this filing lobbied on. |
| `os_matched` | `True` if `os_bill_identifier` resolved AND the bill had at least one structured primary sponsor. |
| `disclosed_lawmakers` | A semicolon-joined list of OpenStates IDs for lawmakers this filer *disclosed* lobbying on this filing. **NOT per-bill** — see "Two lawmaker signals" below. Empty when none resolved. |
| `sponsor_in_disclosed_set` | `True` iff this row's `sponsor_lawmaker_id` appears in this row's `disclosed_lawmakers`. **Read carefully** — see "Two lawmaker signals." |
| `disclosed_only_lawmaker_count` | The count of disclosed lawmakers (for this filing × firm) who are NOT primary sponsors of any of the filing's bills. The "leadership / committee-chair / off-bill contact" signal. |

## How dollars work — please read this

NY discloses one total compensation per filing × firm, plus the bills that
filing lobbied on. NY does *not* disclose how the dollars split across bills
or across beneficiaries (when a coalition files together). This chain handles
that uniformly: for a filing with compensation `C`, M beneficiaries, and N
bills, every (beneficiary × bill) cell carries `comp_per_cell = C / (M × N)`,
distributed with integer-cent arithmetic so the per-cell amounts sum to `C`
**exactly**, with no rounding loss.

This uniform split is a modeling assumption, not a disclosure. If a different
weighting is more appropriate for your analysis (e.g. weighting by how often
each bill was actually lobbied), use `filing_compensation`, `n_beneficiaries_in_filing`,
and `n_bills_in_filing` to re-weight.

**Two rules you must follow when aggregating dollars in this file:**

1. **A cell's identity is `(filing_id, lobbyist_id, beneficiary_id, bill_id)`** —
   never `filing_id` alone. About 26% of filings have multiple firms each with
   their own compensation; deduplicating on `filing_id` alone silently drops
   co-retained firms' dollars. Always `df.drop_duplicates([filing_id, lobbyist_id,
   beneficiary_id, bill_id])` *before* summing `comp_per_cell`.

2. **Do not sum `comp_per_cell` across the sponsor rows of one cell.** When a
   bill has multiple primary sponsors (rare in NY, but it happens), the same
   cell appears on multiple rows — once per sponsor. The cell's
   `comp_per_cell` is replicated, not subdivided. Dedup to distinct cells before
   summing.

The total of `comp_per_cell` over distinct cells in this file is exactly
**$153,064,191.00** — a quick sanity check after any aggregation that should
preserve the total.

## Two lawmaker signals — they answer different questions

This file carries **two** kinds of lawmaker connection, and confusing them is
the most likely way to get a wrong analysis.

**1. Inferred via the bill (`sponsor_lawmaker_id`, `sponsor_lawmaker_name`).**
   These come from Open States. They say "this is the person who sponsored
   this bill" — which is who's *on* the bill in the legislature, not anything
   the lobbying filer disclosed. If a firm lobbied on a bill, this column
   tells you whose bill they were lobbying on. The connection is bill-specific.

**2. Disclosed by the filer (`disclosed_lawmakers`, `sponsor_in_disclosed_set`,
   `disclosed_only_lawmaker_count`).** NY requires every filing to disclose
   which "parties" the filer lobbied. After resolving titles, nicknames, and
   accent variations against the legislator roster, ~57.6% of those edges
   resolve to a specific NY state legislator's OpenStates ID (the rest are
   NYC municipal officials, state executive offices, agencies, committee
   counsel staff, and "communication sent to entire NYS Legislature"
   broadcasts — kept verbatim in the upstream file but not in the chain's
   resolved set). The disclosed set is at the **filing × firm** level: NY
   filers report *who they contacted on this filing*, not *who they contacted
   about which bill*. The same set attaches to every chain row in that filing
   × firm group.

**This grain mismatch is load-bearing.** `disclosed_lawmakers` is NOT a
per-bill claim. A filing that lobbied on 50 bills and contacted 40
legislators discloses *that* set of 40 contacts; we cannot tell from the
filing which contacts went with which bills. So:

- `sponsor_in_disclosed_set=True` means **"this firm disclosed contacting
  this sponsor on something in this filing"** — possibly about this exact
  bill, possibly about a different one. It is not specific evidence of a
  bill-on-bill conversation.
- `sponsor_in_disclosed_set=False` means **"this firm did not (resolvedly)
  disclose contacting this sponsor"** — but be careful: 44% of matched chain
  rows fall here, and some of those will be cases where the firm did contact
  the sponsor but via an unresolved channel (committee staff, broadcast, etc.)
  rather than a clean named-legislator entry.

In aggregate, 56.07% of matched chain rows have `sponsor_in_disclosed_set=True`.
That's well below saturation (high fan-out would push much higher if matching
were noise), so the column is informative — but only at aggregate scale, not
as a per-row "did they meet" indicator.

## Sample rows

Eight random rows, with `disclosed_lawmakers` truncated for legibility (real
values are unabridged in the file):

| filing_id | firm | beneficiary | bill | sponsor | $/cell | M×N | matched | sponsor_in_set | disclosed_only |
|---|---|---|---|---|---:|---|---|---|---:|
| 743146 | Whiteman Osterman & Hanna LLP | VSP Vision | S 1464 (packaging act) | Pete Harckham | $16.61 | 21×43 | ✓ | True | 69 |
| 772314 | Cozen O'Connor Pub. Strategies | Memorial Sloan Kettering | A 1983 (interstate medical licensure) | Amy Paulin | $1,578.95 | 1×19 | ✓ | True | 5 |
| 779444 | Northeast Govt Consulting | Wireless Infrastructure Assn | S 4902 (cell tower backup power) | Pete Harckham | $128.57 | 20×21 | ✓ | True | 47 |
| 741656 | Defenders Association (NYS) | Defenders Association (NYS) | S 404 (reverse keyword searches) | Zellnor Myrie | $92.53 | 1×62 | ✓ | True | 28 |
| 780717 | Citizens for Affordable Rates | Citizens for Affordable Rates | A 9218 (tort damages) | Brian Cunningham | $0.00 | 1×1 | ✓ | False | 1 |
| 762871 | The Parkside Group | Assn of Social Work Boards | A 3005 (FY26 budget) | *Budget Committee* | $443.78 | 13×13 | ✓ | False† | 16 |
| 777987 | Assn of Health Care Providers | (same) | A 8137 (Medicaid auth repeal) | Amy Paulin | $23,771.80 | 1×5 | ✓ | False | 18 |
| 735364 | Hinman Straub Advisors | Jewish Home of Rochester | S 1858-A (adult care facility safety) | Gustavo Rivera | $1,800.00 | 1×10 | ✓ | *(empty)* | 0 |

A few things this sample makes concrete:

- **Row 1** shows how big coalitions get: 21 beneficiaries × 43 bills = 903
  cells in this one filing × firm. The firm's compensation is split evenly
  across all of them.
- **Row 5** ($0 cell) reflects an actual $0 filing-compensation report —
  this is a real value, not a missing one.
- **Row 6 (†)** has a *Budget Committee* sponsor (no individual `ocd-person`),
  so `sponsor_in_disclosed_set` is `False` by construction even though 19
  legislators were disclosed.
- **Row 7** is a paradigm "disclosed but not the sponsor" case — 19 lawmakers
  contacted, but Paulin (the bill's sponsor) isn't among them.
- **Row 8** has `disclosed_lawmakers` empty even though `os_matched=True`. The
  filer's disclosed parties resolved to zero legislators (likely all agencies
  or broadcasts), and the row inherits an empty set. 2.37% of chain rows look
  like this.

## Companion files in `releases/ny/`

The chain is one of several normalized tables in this release. For most
questions about *the chain itself*, just this file is enough. But several
follow-up questions need the companion tables:

- **`NY_clients.tsv`** — the beneficiary companies, indexed by `client_id`.
  The `client_id` in the chain points here. For coalitions, the raw
  semicolon-joined name lives in this file's `name` field; the chain
  pre-splits it into per-beneficiary rows.
- **`NY_lobbyists.tsv`** — the lobbying firms, indexed by `lobbyist_id`.
- **`NY_filing_parties_lobbied.tsv`** — one row per disclosed lawmaker /
  agency / broadcast, *unaggregated*. Useful when you need to inspect the
  raw disclosed contacts (including the 42% that are NYC officials,
  executive offices, agencies, or broadcasts — those are excluded from the
  chain's `disclosed_lawmakers` column, which only contains resolved state
  legislators).
- **`releases/ny/README.md`** — the upstream tables' full schema and the
  pipeline's broader caveats. Read this if you want to go upstream of the
  chain (e.g. into the raw `client_semiannual` field semantics).

## Limitations — please read before drawing conclusions

These are the half-dozen things that, if you don't know them, will make your
analysis subtly wrong:

1. **Sponsors are inferred from Open States, not disclosed.** The
   `sponsor_lawmaker_*` columns are not a record of who the lobbying firm met
   with. They are the bill's primary sponsor per the legislative record.
   "This firm paid to lobby on a bill that lawmaker X sponsored" is the
   correct reading of the chain edge, not "this firm lobbied lawmaker X." See
   the "Two lawmaker signals" section above for the disclosed counterpart.

2. **Primary sponsors only.** NY bills have one primary sponsor. Cosponsors
   exist and matter (there are ~83,000 of them in the OS bundle), but they
   are not in this chain. If a firm lobbied a bill heavily cosponsored by
   a legislator they cared about, the chain won't show that lawmaker.

3. **No stance / no direction.** NY discloses *that* a bill was lobbied. It
   does not disclose for or against. Do not draw conclusions about whether
   a company supported or opposed a bill from this file alone.

4. **Compensation split is uniform.** Across each filing × firm's
   beneficiary × bill cells, dollars are split evenly. NY does not disclose
   actual per-bill effort, so this is a modeling assumption. If you need
   weighted splits (e.g., by lobbyist hours, by bill prominence), you'll
   need to apply them yourself using `filing_compensation` and the M/N
   columns.

5. **0.5% of bills don't resolve to Open States.** These are flagged
   `os_matched=False`, never dropped, with dollars preserved (and an empty
   `sponsor_lawmaker_*`). They are mostly lobbyist typos (e.g. `A51578` when
   the Assembly tops out near `A 11019`), plus a few plausible numbers
   absent from the 2025-2026 session.

6. **Session scope: NY 2025-2026 regular session only.** The chain joins
   only against the current regular session's bills. If a 2025 filing
   lobbied a 2023-2024 carryover bill, that won't match.

7. **Bill IDs are normalized for the join.** Amendment-print suffixes
   (`-A`, `-B`) are stripped to find the base bill, and leading zeros are
   dropped (`A00804` → `A 804`). The amendment-suffix print actually
   lobbied is preserved separately in `bill_print_version`.

8. **The disclosed-lawmaker set resolves only individual NY state
   legislators.** ~42% of disclosed parties are not individual legislators
   (NYC municipal officials, executive offices / agencies, committee staff,
   broadcasts) and don't appear in `disclosed_lawmakers`. They are kept
   verbatim in the upstream `NY_filing_parties_lobbied.tsv`. So a
   `disclosed_only_lawmaker_count` of 0 doesn't mean "no off-bill lobbying"
   — it means no off-bill lobbying *of resolvable state legislators*.

## A pointer for further questions

If you have questions about how a specific row came to be the way it is, the
upstream tables in `releases/ny/` are tracked at the same time as this chain
and use the same `filing_id` / `lobbyist_id` / `client_id` keys. For
questions about the pipeline itself, the internal `README.md` in this
directory carries more detail; for the broader project context, see the
`releases/ny/README.md` one level up.

This is a research artifact built from one researcher's pipeline. If something
in this file looks wrong, it might well be — please report.

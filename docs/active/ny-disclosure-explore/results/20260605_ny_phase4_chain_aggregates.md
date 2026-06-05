<!-- Generated during: convos/20260605_ny_phase4_chain_composer.md -->

# NY Phase 4 chain — aggregates, match rate, conservation (2025)

Source: `releases/ny/chain/NY_chain_2025.tsv`, composed from `releases/ny/` +
the Open States NY 2025-2026 bundle (`data/bills/NY/2025/`, gitignored).
Probe scripts run ad hoc this session (not committed).

## Chain aggregates

| metric | value |
|---|---|
| chain rows | 87,534 |
| distinct lobbying firms | 927 |
| distinct beneficiaries (post coalition-split) | 1,892 |
| distinct source bills (`bill_id`) | 6,352 |
| distinct sponsoring lawmakers (`ocd-person`) | 213 (full NY legislature) |
| rows `os_matched=True` | 87,446 (99.9%) |
| distinct **un**matched bills (flagged, not dropped) | 30 (0.5%) |
| coalition filings (M>1) | 476 |
| reporting periods | Jan/June 60,438 rows · July/Dec 27,096 rows |

## Conservation (no-loss invariant)

Summing `comp_per_cell` over **distinct `(filing_id, lobbyist_id,
beneficiary_id, bill_id)` cells**:

```
chain distinct-cell total : $153,064,191.00
release bill-linked total  : $153,064,191.00
DELTA                      : $0.00
```

The cell key MUST include `lobbyist_id` (a smoke test that omitted it showed a
−$68.6M phantom loss — the chain-layer echo of the Phase-3 firm-collapse bug).
`comp_per_cell` is replicated across a bill's sponsor rows and must not be summed
across them.

This $153.06M is the **bill-linked subset**; full 2025 release compensation is
$345.76M (non-`State Bill` focus rows are not chain-eligible).

## Bill-id match rate (Decision 8 validation)

OS NY identifier format = `<LETTER><SPACE><UNPADDED-DIGITS>` (`A 1668`, `S 550`),
verified against the staged bundle (25,250 bills).

| normalization | distinct bills matched | link rows matched |
|---|---|---|
| **strip suffix** (the normalizer) | 6,322 / 6,352 = **99.5%** | 47,123 / 47,204 = **99.8%** |
| keep suffix | 5,163 / 6,352 = 81.3% | — |

Suffix-stripping buys ~18 points of closure. Unmatched bills are mostly
malformed source ids (`A51578`, `S35005-B` — NY Assembly tops out near `A 11019`)
plus a few plausible numbers absent from the 2025-2026 OS session.

## Coalition prevalence (Decision 7)

- 346 coalition clients (M>1) of 4,373; M ranges 2–31 (largest a 31-member
  coalition led by Pace University / MGM Resorts).
- 6,053 / 47,204 link rows (12.8%) reference a coalition client.
- 189 client names contain undecoded `&amp;` (semicolon split unaffected).

## Sponsorship structure

- NY bills carry **exactly one primary sponsor** (25,250 primaries = 25,250
  bills); `person_id` (`ocd-person`) populated 99.5%.
- Cosponsors: ~83k edges in the OS bundle, excluded from v1.
- 520 committee ("organization") primaries kept as collective sponsors
  (`person_id=None`), not dropped.

## parties_lobbied (the disclosed-but-unfetched lawmaker edge)

The 2025 raw pull is a filtered SODA `$select` of **9 fields only**
(`form_submission_id`, `reporting_year`, `reporting_period`,
`principal_lobbyist`, `beneficial_client`, `contractual_client_name`,
`current_period_compensation`, `type_of_lobbying_focus`,
`focus_identifying_number`). `parties_lobbied` /
`first_and_last_name_or_title_of_person_lobbied` were **not fetched**, so the
disclosed lawmaker edge could not be characterized this session. Ingesting it =
re-pull with those fields + resolve free-text names/titles to `ocd-person`.

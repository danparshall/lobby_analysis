<!-- Generated during: convos/20260605_ny_phase3_pull_firm_collapse_fix.md -->

# NY 2025 — Phase 3 release aggregates (validated)

Source: live `client_semiannual` (`qym9-xzj6`) 2025 pull → `releases/ny/` at
commit `cb59653` (materialize fix) / `05dee22` (release). Raw: 11,200,080 rows
(row count verified against live `count(*)`).

## Counts

| metric | value |
|---|---:|
| raw rows pulled | 11,200,080 |
| grain rows | 56,985 |
| clients (`NY_clients.tsv`) | 4,373 |
| lobbyist firms (`NY_lobbyists.tsv`) | 1,333 |
| firm-filings (`NY_filings.tsv`) | 10,870 |
| bill-link rows (`NY_filing_bill_links.tsv`) | 47,204 |
| distinct bill_id (suffixed, as filed) | 6,352 |
| distinct base bill (after `-A/-B` strip) | 5,449 |

## Compensation

| metric | value |
|---|---:|
| total compensation, 2025 | **$345,762,462.00** |
| ... on bill-linked filings (chain-eligible) | $153,064,191.00 (44%) |
| ... on no-bill filings (preserved, not chain-eligible) | $192,698,271.00 (56%) |

**Independent validations (different code path from the pipeline):**

- Full from-raw recompute (supersede by business key → sum once per filing):
  $345,762,462.00 — **delta $0.00**; distinct surviving filings 10,870 (matches).
- Top firm Brown & Weinraub: pipeline $24,217,924.00 == raw recompute
  $24,217,924.00, 0 submissions dropped.
- Even-split conservation `SUM(comp_per_bill) == filing_compensation`: **0
  violations / 4,328 bill-linked filings.**

## Top 10 lobbyist firms by 2025 compensation

| rank | comp | firm |
|---:|---:|---|
| 1 | $24,217,924 | BROWN & WEINRAUB ADVISORS, LLC |
| 2 | $17,330,648 | BOLTON-ST. JOHNS, LLC |
| 3 | $17,287,375 | KASIRER LLC |
| 4 | $14,927,102 | GREENBERG TRAURIG, LLP |
| 5 | $9,442,961 | OSTROFF ASSOCIATES, INC. |

## Coverage

- `type_of_lobbying_focus` = **State Bill** on 9,824,399 / 11,200,080 rows (87.7%).
  Next: State Funding 2.5%, Municipal Bill 2.3%, Municipal Land Use 2.3%.
- State-Bill bill-id parse rate: **85.4%** of State-Bill rows
  (8,387,476 / 9,824,399) carry a `focus_identifying_number` that parses to a
  canonical `bill_id`. 10,610 distinct focus numbers; 6,369 parse. Non-parsers are
  prose ("100 foot rule") or non-canonical refs ("100 Foot Rule (S8417/A8888)").

## The form_submission_id finding (root cause of the fixed bug)

`form_submission_id` is the **client's** report id, shared across firms:
**2,249 / 8,613 (26%)** of 2025 submissions list >1 distinct `principal_lobbyist`.
Example — submission 735314 (ACCENTURE's report) lists 6 firms with distinct comp:
ACCENTURE in-house $179, Brown & Weinraub $45,000, Mercury $25,000, Davidoff
$48,000, CMW $54,000, Betty Gray $54,000. The pre-fix materializer kept only one
per `(submission, client)`, dropping $108.9M (32%) of total comp.

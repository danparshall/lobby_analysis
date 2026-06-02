# Phase 3 — End-to-end chain composition

**Date:** 2026-06-01
**Branch:** `wi-allocation-matrix`
**Plan:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) steps 32–42
**Originating convo:** [`convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md`](../convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md)
**Materialized output:** `data/allocations/WI/WI_chain_2025.tsv` (33 MB, 115,229 rows)

## TL;DR

The Phase 3 chain — `principal → lobbyist → bill → sponsor` — landed end-to-end against the WI 2025 release for the Legislative Bills/Resolutions bucket. The plan's pyopenstates/API path was abandoned for a Plural Policy bulk CSV download that ships with structured `ocd-person/...` IDs, making `sponsor_lawmaker_id` a real identifier instead of a name string. Coverage clears the plan's §217 bar by a wide margin (97.9% of legislative effort rows produce ≥1 chain row, target ≥80%).

| Metric | Value |
|---|---|
| Chain rows | **115,229** (46,446 H1 + 68,783 H2) |
| Unique principals | 525 |
| Unique lobbyists | 511 |
| Unique bills | 984 |
| Unique sponsors | 133 (132 legislators + 1 collective entity) |
| Total modeled hours | 561,625 |
| Coverage vs effort rows | **97.9%** (3,947 of 4,030 unique 2025 legislative effort rows) |
| Confidence distribution | 87.8% `ipf_fit` / 8.0% `exact` / 4.2% `zero_filed` |

## Scope (what this chain does and doesn't include)

Phase 3 v1 emits chain rows for **Legislative Bills/Resolutions only** — the bucket that has named bill IDs principals filed effort percents against. Three other bill_efforts buckets are deferred to Phase 3+ refinement:

| Bucket | Effort rows | Phase 3 v1 treatment |
|---|---|---|
| Legislative Bills/Resolutions | 4,035 | Full chain rows emitted |
| Topics Not Yet Assigned A Bill Or Rule Number | 2,327 | Skipped (plan Q3 default was "emit with `topic_no_bill_yet` flag" — deferred) |
| Budget Bill Subjects | 856 | Skipped |
| Administrative Rulemaking Proceedings | 127 | Skipped |

Other v1 simplifications:

- **Primary sponsors only.** The bulk dump's structured sponsor list contains only `classification='primary'` rows across all 28,047 entries; cosponsors and later add-ons live in `bill_actions.description` text. Cosponsor parsing is a Phase 3+ refinement candidate.
- **16 bills with zero structured sponsors** (likely procedural / Joint Legislative Council vehicles) are skipped — no rows emitted. They show up in `bill_efforts` but produce no chain rows.
- **2026 periods are not in chain.** Phase 2's allocation matrix covers 2025-H1 and 2025-H2; bill_efforts rows with `period_label` starting `2026 ...` are skipped.
- **Lawmaker disambiguation deferred for Phase 4.** Chain provides `sponsor_lawmaker_id` as `ocd-person/...` from OpenStates. The CFIS join (Phase 4) will need its own ID space; the join key TBD.

## Pivot from plan: bulk CSV instead of pyopenstates/API

The plan's step 33 default was "use `pyopenstates` or the JSON API to get all WI 2025-2026 bills with sponsors." Three findings from probing the API path before writing code argued for a pivot:

1. **OpenStates v3 API enforces a key** — no anonymous access (HTTP 401-equivalent). Without a key, no probe possible.
2. **The key's free tier is 10 requests/minute + 500 records/day** — tighter than expected. WI 2025-2026 has ~1,000 unique bills to look up; one-shot-per-bill exceeds the daily budget.
3. **`pyopenstates` swallows HTTP status + headers** — `raise APIError(response.text)` only. Any rate-limit telemetry from response headers is invisible.

Plural Policy's bulk download path (https://open.pluralpolicy.com/data/session-csv/ and `/data/legislator-csv/`) sidesteps all three: no rate limit, no auth budget, and 15 normalized CSV tables instead of nested JSON.

The CSV bundle's `WI_2025_bill_sponsorships.csv` table also brought one structural upgrade over the JSON dump: each row carries a `person_id` field (`ocd-person/...`) for 27,987 of 28,047 rows (99.8%). The remaining 60 are collective entities (Joint Legislative Council × 26, Law Revision Committee × 34) with `entity_type='organization'` and no `person_id`. These surface in the chain as sponsors with `sponsor_lawmaker_id = name_string` (the only available identifier).

`pyopenstates` was added briefly during the probe and then removed (`uv remove pyopenstates`) once the bulk path was confirmed — no production dependency.

## Materialized output schema

`data/allocations/WI/WI_chain_2025.tsv`, 12 columns, tab-separated:

| Column | Type | Example | Notes |
|---|---|---|---|
| `semester` | str | `2025-H1` / `2025-H2` | Disambiguator added beyond plan literal — same tuple may appear in both semesters with different hours and percents |
| `principal_id` | int | `11091` | from `releases/wi/WI_principals.tsv` |
| `principal_name` | str | `DoorDash, Inc.` | from same |
| `lobbyist_id` | int | `11077` | from Phase 2 allocation matrix |
| `lobbyist_name` | str | `Clark Kaericher` | from `releases/wi/WI_lobbyists.tsv` |
| `bill_id` | str | `SB 256` | OpenStates short identifier |
| `bill_title` | str | `Relating to: ...` | from `WI_2025_bills.csv` |
| `modeled_hours` | float | `9.872997` | `(hours_comm + hours_other) × (filed_percent / 100)` |
| `principal_filed_percent` | float | `0.21` | float in [0, 1] |
| `sponsor_lawmaker_id` | str | `ocd-person/...` | OpenStates person ID, or collective entity name |
| `sponsor_lawmaker_name` | str | `Marklein` | surname (or collective entity name) |
| `attribution_confidence` | str | `ipf_fit` | pass-through from allocation matrix |

Rows are sorted deterministically by `(semester, principal_id, lobbyist_id, bill_id, sponsor_lawmaker_id)` for diff-able output.

## DoorDash worked example (plan §215 anchor)

DoorDash (principal_id 11091) filed effort percentages against 2 unique legislative bills in 2025: SB 256 and AB 269, each in both H1 and H2. DoorDash had 3 authorized lobbyists in both semesters: Clark Kaericher (11077), Brian Taffora (11112), Mike Kuglitsch (11114).

**Total DoorDash chain rows: 78** = (3 lob × 4 SB-256-sponsors × 2 semesters) + (3 lob × 9 AB-269-sponsors × 2 semesters) = 24 + 54.

| bill_id | semester | rows | modeled_hours total | filed % |
|---|---|---|---|---|
| SB 256 | 2025-H1 | 12 | 143.98 | 21% |
| SB 256 | 2025-H2 | 12 | 50.27 | 16% |
| AB 269 | 2025-H1 | 27 | 323.95 | 21% |
| AB 269 | 2025-H2 | 27 | 113.11 | 16% |

**Arithmetic spot-check** for Clark Kaericher × SB 256 × 2025-H1:
- Phase 2 cell: `hours_comm = 37.806, hours_other = 9.209` → total = 47.014
- × `filed_percent = 0.21` → `modeled_hours = 9.873`
- Each of 4 SB 256 sponsors (Marklein, Testin, Cabral-Guevara, Bradley) receives the same 9.873 from this lobbyist's effort on this bill.

The chain assumes uniform attribution: a lobbyist's hours for a principal are spread across that principal's bill efforts in proportion to the filed percents, and that bill-allocated time is attributed to each primary sponsor of the bill equally. The plan flagged this proportional-attribution assumption (§240) as challengeable without per-lobbyist-per-bill ground truth; the chain's design surfaces it transparently via the `principal_filed_percent` column.

## Top-10 (lobbyist, sponsor) pairs by total modeled hours

Two lobbyists dominate: Kelly McDowell (11465) and Nicole Hudzinski (11446). Both pair heavily with multiple primary sponsors of the same set of large bills — a natural artifact of the proportional-attribution model when a single bill has many primary sponsors.

| Rank | Lobbyist | Sponsor | Total modeled hrs |
|---|---|---|---|
| 1 | Kelly McDowell | O'Connor | 500.45 |
| 2 | Nicole Hudzinski | Mursau | 484.62 |
| 3 | Kelly McDowell | Gundrum | 480.25 |
| 4 | Kelly McDowell | Behnke | 480.25 |
| 5 | Nicole Hudzinski | Gustafson | 480.02 |
| 6 | Nicole Hudzinski | Sinicki | 475.41 |
| 7 | Nicole Hudzinski | Behnke | 461.61 |
| 8 | Nicole Hudzinski | Melotik | 452.40 |
| 9 | Kelly McDowell | Callahan | 439.85 |
| 10 | Kelly McDowell | Maxey | 439.85 |

## Top-10 sponsors by total modeled hours received

| Rank | Sponsor | Chamber | Total modeled hrs |
|---|---|---|---|
| 1 | Mursau | Assembly | 15,357 |
| 2 | O'Connor | Assembly | 13,893 |
| 3 | Dittrich | Assembly | 12,954 |
| 4 | Kreibich | Assembly | 12,944 |
| 5 | Behnke | Assembly | 11,496 |
| 6 | Knodl | Assembly | 10,873 |
| 7 | Gundrum | Assembly | 10,764 |
| 8 | Murphy | Assembly | 10,458 |
| 9 | Wichgers | Assembly | 9,173 |
| 10 | Melotik | Assembly | 9,080 |

All Assembly. Pattern likely reflects that Assembly bills (which originate where Republicans hold majority) tend to have multiple Republican co-author primary sponsors, while Senate bills more often have a small number of named sponsors. Worth digging into more — *not* a claim that these legislators are "most lobbied;" the modeled-hours metric counts a lobbyist's bill-allocated time once per primary sponsor of that bill.

## Findings worth carrying forward

### Pettack (lobbyist 11072) produces zero chain rows

Phase 2 flagged Pettack with `attribution_confidence='aggregation_flagged'` based on her 7,611 hours filed — the org-aggregation pattern of staff hours under one registered lobbyist's name. The chain composition has **zero rows** for her despite that flag, because **the 6 SAA-family principals she's authorized for did not file Legislative-bucket bill efforts**. They filed in other buckets (Topics Not Yet Assigned / Administrative Rulemaking / Budget Bill Subjects) which the v1 chain skips.

This is real signal, not a bug. The `aggregation_flagged` label is on the **lobbyist axis** (a hours-side anomaly), but legislative attribution lives on the **principal axis** (which bills a principal filed). The two are decoupled by design. Operationally: Pettack's hours are recoverable from the Phase 2 allocation matrix but invisible in the legislative chain.

A Phase 3+ refinement that includes the Topics-Not-Yet-Assigned bucket would surface Pettack's principals (and their bill-less effort attributions) in the chain, partially.

### Small-CC over-attribution pattern (Phase 2 finding) is invisible in the chain too

The Phase 2 writeup flagged 8 H1 CCs (and similar in H2) where principals' filed hours exceed the sum of their authorized lobbyists' reported hours — IPF assigns the excess to the one lobbyist with non-zero filings, inflating that lobbyist's modeled cell for those principals. The chain inherits this: a row whose `attribution_confidence='ipf_fit'` may be over-attributing if the underlying CC has unbalanced marginals. The chain doesn't currently expose per-cell IPF row residual, so consumers can't distinguish "tightly-pinned `ipf_fit`" from "absorbed-over-attribution `ipf_fit`." Phase 3+ refinement candidate, related to the row-residual exposure question Phase 2 left open.

### Top sponsors are all Assembly

All 10 top sponsors are Assembly members; no senators in the top 10. Total modeled hours flowing to Assembly sponsors > flowing to Senate sponsors. Two possible drivers:
1. **Multi-author Assembly bills inflate per-sponsor counts.** When an Assembly bill has 12 primary sponsors and a Senate bill has 3, the same lobbyist effort spreads across 12 vs 3 cells. This is the proportional-attribution effect, not a real "more lobbied" signal.
2. **Real partisan-skew effect.** Republican Assembly members may genuinely receive more lobbying-relevant bill activity in this session.

Both are testable: divide modeled hours by sponsor count per bill before aggregating to compare per-sponsor-mass. Deferred to Phase 3+ refinement.

## Open questions surfaced to user at writeup time

These were collected but **not blocking** for the v1 deliverable. Ranked by load-bearing-ness:

- **Q3 (revised):** Phase 3 v1 skips the Topics-Not-Yet-Assigned bucket (2,327 effort rows). Plan default was emit-with-`topic_no_bill_yet`. Should v1.1 add these? They preserve principal-level signal even without a bill ID, but require a different sponsor field (e.g., `sponsor_lawmaker_id=null` and `attribution_confidence='topic_no_bill_yet'`).
- **Cosponsor parsing.** The bulk CSV's structured sponsor list is primary-only; cosponsors live in `bill_actions.description` text. Phase 3+ candidate. Roughly half a day of regex work; doubles or triples chain rowcount.
- **Per-cell row-residual exposure** (carried forward from Phase 2) — would help distinguish well-pinned `ipf_fit` rows from over-attribution-absorbing ones.
- **Two-axis lobbyist-sponsor aggregation.** "Top sponsors" is dominated by multi-author Assembly bills. A per-bill-normalized variant would tell a different story.

## Phase 4 readiness check

Phase 4 (CFIS scoping) needs the chain's `sponsor_lawmaker_id` to be join-keyable against WI Ethics Commission donor/recipient records. Today's chain provides `ocd-person/...` IDs from OpenStates plus `current_district` from `wi.csv`. The CFIS schema is unknown until Phase 4 investigates, but the chain's identifier richness (`ocd-person/...` + surname + chamber + party + district, with `legislators_csv` as the join table) should give Phase 4 enough handles to attempt name-based or district-based matching.

## Tests + commits

Phase 3 added 20 tests (13 legislature loader + 7 chain composer) across 5 commits:

| SHA | What |
|---|---|
| `4b71c03` | `phase 3.1: RED tests for WI legislature loader` |
| `f830230` | `phase 3.2: WI legislature loader GREEN` |
| `67f9c30` | `phase 3.3: RED tests for WI chain composer` |
| `cfc8342` | `phase 3.4: WI chain composer GREEN` |
| `a64f710` | `phase 3.5: WI chain materialize + CLI subcommand` |

Full suite: 1,630 passed + 3 baseline failures (plan §234), zero regressions.

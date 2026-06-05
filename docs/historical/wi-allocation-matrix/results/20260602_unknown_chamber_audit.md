# Unknown-chamber audit

**Date:** 2026-06-02
**Branch:** `wi-allocation-matrix`
**Prerequisite from:** [`20260602_phase_3_1_per_sponsor_normalization.md`](20260602_phase_3_1_per_sponsor_normalization.md) (refinement candidate: "name-match audit for 'unknown' chamber 1,288 hr")
**Forces revision of:** [`20260602_wi_chain_synthesis.md`](20260602_wi_chain_synthesis.md) chamber-rollup numbers (corrections below)
**Audit scripts:** `/tmp/audit_unknown_chamber.py`, `/tmp/audit_chamber_rollup_corrected.py` (one-off, not checked in)

## TL;DR

The 1,288 hr / 2.6% "unknown chamber" bucket reported in Phase 3.1 was **inflated by a fragile name-based join**. Using the structured `sponsor_lawmaker_id` (`ocd-person/...`) → `wi.csv.id` → `current_chamber` join instead:

- **True unknown bucket is 589.6 hr (1.2%)** — exactly half the Phase 3.1 number.
- **It is 100% Joint Legislative Council** — a single collective entity (170 rows, 22 bills). No other unresolved sponsors at all.
- **The "missing" 698 hr were three disambiguated legislators** (B. Jacobson, L. Johnson, J. Jacobson) whose `ocd-person/...` IDs resolve correctly but whose chain-side surnames carry initial prefixes that don't match the roster's bare `family_name`. The structured-ID join handles them; the name-based join didn't.
- **Law Revision Committee — hypothesized as part of the unknown bucket — has zero chain rows.** No principals filed effort on LRC-sponsored items in 2025.
- **Coverage of the Plural Policy legislator roster is complete.** Every individual-legislator `ocd-person/...` ID in the chain resolves to wi.csv (zero `unresolved_ocd_id` rows). No gap in the join surface.

## Audit table

| Chamber status | Rows | Hours (`modeled_hours_per_sponsor`) | % of total | Distinct sponsors |
|---|---:|---:|---:|---:|
| **matched** (resolved to individual legislator) | 115,059 | 48,199.7 | 98.79% | 132 |
| **collective_entity** (id is a name string, not `ocd-person/...`) | 170 | 589.6 | 1.21% | 1 (Joint Legislative Council) |
| **unresolved_ocd_id** (id starts `ocd-person/` but no roster row) | 0 | 0.0 | 0.00% | 0 |
| **chamber_missing_in_roster** | 0 | 0.0 | 0.00% | 0 |

Cross-check: 48,199.7 + 589.6 = 48,789.3 — matches synthesis grand total exactly.

## Corrected chamber rollup

Re-doing the chamber rollup with the ID-based join (instead of name-based) shifts ~700 hr from "unknown" into the correct chambers:

| Chamber | Phase 3.1 (name-based) | **Corrected (ID-based)** | Δ |
|---|---:|---:|---:|
| Lower (Assembly) | 25,892 | **26,543** | **+651** |
| Upper (Senate) | 21,610 | **21,657** | +47 |
| Unknown (JLC) | 1,288 | **590** | **−698** |
| **Total** | 48,789 | **48,789** | 0 |
| **Lower : upper ratio** | **1.20×** | **1.23×** | +0.03 |

The headline Phase 3.1 finding — chamber bias from the old metric reversed; 8 of top 10 are Senate; lower:upper now ~1.2× balanced after normalization — is **unchanged in substance**. The corrected ratio is 1.23× vs 1.20×; the conclusion that effort is roughly balanced between chambers after per-sponsor normalization holds.

## Where the missing 698 hr went

WI legislators with shared surnames use an initial-prefix disambiguation pattern in the chain TSV. The three affected legislators in this snapshot:

| Chain surname | Roster `family_name` | Chamber | Rows | Hours |
|---|---|---|---:|---:|
| B. Jacobson | Jacobson | lower | 1,541 | 429.2 |
| L. Johnson | Johnson | upper | 464 | 223.7 |
| J. Jacobson | Jacobson | lower | 345 | 45.2 |
| | | | **2,350** | **698.2** |

698.2 hr is the exact delta between Phase 3.1 (1,288) and corrected (590). The shift goes mostly to Assembly (+651) because two of the three are Assembly members.

## What this means going forward

1. **The chain TSV's `sponsor_lawmaker_id` is fully reliable for chamber assignment** — no coverage gap on the wi.csv roster. Any downstream chamber rollup, party rollup, district analysis, etc. should join on the structured ID.

2. **Any join on `sponsor_lawmaker_name` (surname) is fragile** when the underlying data uses disambiguation prefixes. The Phase 3.1 chamber rollup used name-based join and lost ~700 hrs to the unknown bucket; future analysis code should use the ID consistently.

3. **The Joint Legislative Council 590-hr residual is genuinely unknown by-design** — JLC is a collective entity, not a chamber-assigned legislator. The 22 bills it sponsored are LRB-issued legislative-council vehicles (often technical / interim-committee work). Treat as a separate "collective entities" bucket if a complete-coverage chamber view is needed; do not try to assign a chamber.

4. **Law Revision Committee has zero chain rows.** We hypothesized it would contribute to the unknown bucket; it doesn't, because no principals filed effort on LRC items. This is a useful data point — collective-entity sponsors only enter the chain when a principal actually filed effort on a bill they sponsored, and LRC sponsorships didn't draw any filed effort in 2025.

5. **The synthesis chamber rollup table will be amended** (see "Synthesis updates" below). The story doesn't change but the numbers should be corrected.

## Synthesis updates

Amendments to `20260602_wi_chain_synthesis.md`:

- "Chamber bias reversal" table: 25,892 → 26,543, 21,610 → 21,657, 3.44× → still 3.44× pre-norm but post-norm 1.20× → 1.23×.
- "What this can and can't answer" section: the "unknown bucket 1,288 hr / 2.6%" line corrected to 590 hr / 1.2%, attributed to Joint Legislative Council specifically.
- New note: the chain's chamber-rollup is complete (zero coverage gap on individual legislators) provided ID-based join is used.

## Suggested action on downstream code

The `legislature.py` / `materialize.py` modules should be reviewed to ensure any chamber-rollup or sponsor-resolution code joins on `sponsor_lawmaker_id` rather than `sponsor_lawmaker_name`. This isn't in scope for this audit (read-only), but it's a small follow-up commit worth doing if those modules currently use the name surface.

Quick code check (out of scope to fix here):
- `grep -n 'family_name\|sponsor_lawmaker_name' src/lobby_analysis/allocation/wi/*.py` would find any name-based joins.

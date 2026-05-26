<!-- Generated during: convos/20260526_wi_principal_side_scrape_implementation.md -->

# WI Principal-Side Authorization Scrape — Results

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Plan:** [`plans/wi_principal_side_scrape.md`](../plans/wi_principal_side_scrape.md)
**Originating convo:** [`convos/20260526_wi_principal_side_scrape_implementation.md`](../convos/20260526_wi_principal_side_scrape_implementation.md)
**Data source:** per-principal HTML detail pages at `lobbying.wi.gov`, captured 2026-05-26
**Output TSVs (gitignored):**
- Principal-side raw: `/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations_principal_side.tsv`
- Unified (with provenance): `/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations_unified.tsv`

## Headline numbers

| Metric | Value |
|---|---|
| Principal IDs in scrape universe | 944 (904 .xls ∪ 942 auth-graph; 902 ∩, 40 auth-only, 2 dir-only) |
| Per-principal pages fetched | 944 (934 fresh + 10 from sanity batch) |
| Hard 404s | 0 |
| Soft 404s on principal pages | **0** (vs 1 on lobbyist side; principal pages cleaner) |
| Principals yielding ≥1 lobbyist authorization | 944 (every principal in the universe) |
| Principals yielding 0 authorizations | 0 |
| Total principal-side `(lobbyist, principal)` authorization rows | **2,254** |
| Distinct lobbyists in principal-side scrape | **748** (vs 745 on lobbyist side, **+3**) |
| Wall time (full scrape, 1.0 s delay) | 1170.9 s ≈ 19 min 31 s |
| Per-fetch rate (HTTP + sleep) | ~1.25 s/req (slightly slower than lobbyist side's 1.11 s due to larger pages on avg) |

## Unified table (lobbyist-side ⇄ principal-side) headline

After unifying with `discovered_via` ∈ {lobbyist, principal, both} + `lobbyist_in_grid` provenance:

| Metric | Value |
|---|---|
| Total unified rows | 2,254 |
| Rows discovered on BOTH sides | 2,251 (99.87% of unified) |
| Rows discovered on LOBBYIST side only | **0** |
| Rows discovered on PRINCIPAL side only | **3** (0.13% of unified) |
| **Schlaak-class lobbyists** (`discovered_via='principal' AND lobbyist_in_grid=false`) | **2** |
| Soft-404 recoveries (`discovered_via='principal' AND lobbyist_in_grid=true`) | **1** |

**Lobbyist-side completeness gain from this scrape: +3 edges, +3 distinct lobbyists, +0.4% lobbyist-coverage.** The lobbyist-side scrape was already 99.87% complete on edges and 99.6% complete on lobbyists at the 2026-05-26 snapshot. The structural blind spot the gap investigation flagged is *small*, but it's not zero — and it's not just the original Schlaak case.

## The 3 principal-only edges

| `lobbyist_id` | `principal_id` | `authorized_on` | `withdrawn_on` | `lobbyist_in_grid` | Interpretation |
|---|---|---|---|---|---|
| 11513 | 11592 | 2025-01-03 | 2026-04-09 | false | **NEW Schlaak-class case** (Steinbruecker / ACLU of Wisconsin) |
| 12694 | 12997 | 2026-01-08 | — | false | Known Schlaak case (Schlaak / WCTA) |
| 12717 | 12900 | 2025-02-27 | — | true | Soft-404 recovery (Neumann-Ortiz / Voces) |

### Lobbyist 11513 — James Steinbruecker (NEW finding)

- **Organization:** American Civil Liberties Union of Wisconsin Inc
- **License Issue Date:** 1/3/2025
- **License Surrender Date:** 5/25/2026 (per his lobbyist detail page)
- **License Type:** Single (per `WI_directory_lobbyists.xls`)
- **Status in `WI_directory_lobbyists.xls`:** **PRESENT** (row 661); `Surrendered Date` cell is blank
- **Status in LobbyistList grid AJAX:** **ABSENT**

This is a NEW Schlaak-class case the gap-investigation didn't catch. Different shape from Schlaak: Steinbruecker IS in the directory `.xls` (the snapshot captured him pre-surrender) but NOT in the grid AJAX (which reflects the day-of-print surrender). The principal-side scrape surfaced his historical authorization (2025-01-03 to 2026-04-09 — note he was withdrawn from ACLU 6 weeks before surrendering his license).

### Lobbyist 12694 — Michael Schlaak (re-confirmed)

- **Organization:** Wisconsin Cable Telecommunications Association (via principal 12997)
- **License Issue Date:** 1/28/2025 (current, no surrender)
- **Status in `WI_directory_lobbyists.xls`:** **ABSENT**
- **Status in LobbyistList grid AJAX:** **ABSENT**

The original Schlaak case. License current, authorization current (16+ months tenure pre-scrape), filtered out of **both** rosters for an unknown reason. License Type column doesn't apply (he's not in the .xls to read it from). His exclusion remains structurally unexplained.

### Lobbyist 12717 — Christine Neumann-Ortiz (soft-404 recovery)

- **Organization:** Voces de la Frontera Action, Inc.
- **License Issue Date:** 1/31/2025
- **Status in `WI_directory_lobbyists.xls`:** **PRESENT** (row 486); `Surrendered Date` cell is blank
- **Status in LobbyistList grid AJAX:** **PRESENT**
- **Status of her lobbyist detail page:** soft-404 (HTTP 200 + "Page Not Found" body)

Not a Schlaak-class case — both rosters know about her. Her lobbyist detail page is just broken on the portal side (was also a soft-404 in the lobbyist-side scrape, flagged at the time as the only soft-404 in 774 fetches). The principal-side scrape bridged the gap: her authorization with Voces is reachable via the principal's back-link, even though her own detail page is unreachable.

## Filter-rule hypothesis update

Going into this scrape, the working hypothesis was that the `WI_directory_lobbyists.xls` filter was empirically `Surrendered Date IS NULL`. The Steinbruecker case **refutes that simple rule**:

| Hypothesis | Verdict |
|---|---|
| `.xls` filter = "license not surrendered" | **Refuted.** Steinbruecker is in the .xls with `Surrendered Date = NULL` despite his detail page showing License Surrender Date 5/25/2026 (same day as .xls print). The .xls is a *point-in-time snapshot*, not a "currently active" filtered query. |
| Grid AJAX = `.xls` minus surrendered | **Refuted.** Grid (774) and .xls (776) differ by 2 — but Schlaak is in neither, and Steinbruecker is in the .xls but not the grid. The filters aren't aligned. |
| Grid AJAX filter = "license not surrendered" | **Partly supported, not fully.** Steinbruecker (just-surrendered) is excluded from grid as expected. Schlaak (current license) is also excluded — inconsistent with this rule. |
| `License Type` column predicts grid membership | **Refuted.** Directory has 658 Single / 116 Multiple / 2 NaN. The grid omits a mix; no clean partition along this axis. (Schlaak is not in the .xls to read his License Type at all.) |

**Net:** the directory `.xls` is a point-in-time snapshot with snapshot lag; the grid AJAX likely applies a "currently displayable" filter that mostly correlates with non-surrender but has at least one mysterious exclusion (Schlaak). The Schlaak exclusion remains unexplained after this scrape — it's the residual structural finding.

## Authorization-date distribution (principal side)

| Year | Rows |
|---|---|
| 2024 (Dec only) | 716 |
| 2025 | 1,400 |
| 2026 (through May) | 134 |
| Pending (`authorized_on` empty) | 4 |
| **Total** | 2,254 |

Matches the lobbyist-side distribution closely (+2 rows in 2025, +1 in 2026 — accounted for by the 3 principal-only edges, which all have `authorized_on` in 2025-2026).

## Cross-validation against the lobbyist-side scrape

| Check | Result |
|---|---|
| Every lobbyist-side edge appears on principal side | ✓ (2,251 of 2,251 found `discovered_via='both'`) |
| Withdrawn dates agree where both sides report a date | ✓ (no warnings logged on the unify run) |
| Soft-404 lobbyist (12717) authorization is recovered | ✓ (Voces edge appears with `discovered_via='principal'`) |
| Schlaak case (12694 → 12997) is recovered | ✓ (lands in unified with `lobbyist_in_grid=false`) |
| Privacy-redacted principals (11530, etc.) contribute their auths | ✓ (parser handles suppressed principal-info section) |

The unification step's WARNING-on-disagreement instrumentation produced **zero warnings**, which means: every edge that appears on both sides has identical `withdrawn_on` values. The two scrapes agree perfectly on the rows they both see.

## Notable findings & implications

### Finding 1: The lobbyist-side scrape is ~99.9% complete on this snapshot

The headline number from the gap investigation was framed as a real completeness risk: "our auth graph has unknown lobbyist-side completeness; can't bound the Schlaak-class population from this side." The principal-side scrape *bounds* it: **2 Schlaak-class lobbyists out of 748 total = 0.27% lobbyist-coverage gap.** Whatever filter the grid AJAX applies, the lobbyists it excludes are a tiny minority for the 2025REG session at this snapshot.

This is **not zero** — and the Steinbruecker case shows the gap isn't just one weird lobbyist; the grid filter does drop multiple lobbyists per session. But the magnitude is small enough that the lobbyist-side scrape is a reasonable starting point for time-series analysis if Schlaak-class coverage isn't critical.

### Finding 2: The principal-side scrape gains 0 edges from the lobbyist-side perspective alone

**Zero `discovered_via='lobbyist'` rows.** Every edge the lobbyist-side scrape captured was also captured by the principal-side scrape. This is a stronger result than expected — it implies the principal pages list withdrawn authorizations within the current session (which we confirmed in the gap investigation's Apex Clean Energy case). If a lobbyist authorization was *ever* in effect during 2025REG, it shows up on both sides.

Operationally: for future sessions, **EITHER scrape is sufficient** as long as you don't care about Schlaak-class lobbyists. The principal-side is *also* sufficient by itself (and discovers Schlaak-class lobbyists for free).

### Finding 3: The Schlaak exclusion is real but Schlaak isn't unique

Steinbruecker is a second confirmed case, and the principal-side scrape exists *because* it's the only way to enumerate this class. We now know:

- The exclusion mechanism isn't License Type (Single/Multiple).
- It isn't "license surrendered" (Schlaak's license is current).
- It isn't a registration race (Schlaak: 16-month tenure; Steinbruecker: ~17-month tenure).
- It might be some administrative-status flag on the portal database that isn't exposed in the .xls or grid.

This is the residual unknown. Worth one more email to `lobbying@wi.gov` if Dan's first one bears fruit — they can presumably explain what their grid filter does.

### Finding 4: Principal pages are cleaner than lobbyist pages

**Zero soft-404s on the principal side**, vs 1 on the lobbyist side (Neumann-Ortiz). The principal-side endpoint at `/Who/PrincipalInformation/{session}/Information/{id}` appears to be more robust than `/Who/LobbyistInformation/{session}/Information/{id}` — or at least: no principal in the 944-ID universe has the per-page failure mode that 1 of 774 lobbyists does. Worth knowing for future scrapes.

### Finding 5: The directory `.xls` is a snapshot, not a query

Steinbruecker counterexample (in .xls, surrendered same day as print). This corrects the "filter rule" framing from the gap investigation. Practically: for time-series work, the .xls captures a point-in-time and the grid captures a different one, so cross-vintage comparisons need both vintages of both sources.

## Open questions surfaced

- **What is the grid AJAX's exclusion rule?** Schlaak is the unresolved structural case; Steinbruecker's exclusion explains itself by surrender date but the .xls disagreement reveals filter complexity. An email exchange with WI Ethics Commission is the cheapest path; alternatively, brute-forcing principal IDs in the 10000–13500 range (deferred per the plan's "What could change" notes) could surface more Schlaak-class lobbyists if any exist.
- **Are the 2 Schlaak-class lobbyists stable across sessions?** Schlaak was in the system 16+ months pre-scrape; Steinbruecker similar. If the exclusion is administrative, it might persist across the 2023REG → 2025REG transition. Cross-session enumeration would tell us.
- **What's the principal-side data-quality picture for older sessions?** 2025REG is the current session and presumably the freshest data. 2023REG (current at time of writing prior research) may have more soft-404s or different filter behavior. Cross-vintage principal-side scrape is a natural follow-up.
- **Should we use the principal-side scrape as the canonical edge source going forward?** It's a superset of the lobbyist-side scrape on this snapshot and discovers Schlaak-class lobbyists for free. The lobbyist-side scrape remains useful for fetching per-lobbyist metadata (license dates, surrenders) that the principal page doesn't expose. But for *edges*, the principal-side is strictly more complete.

## Data integrity

All checkpoints preserved under `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/` (gitignored, 944 JSON files). Resume contract verified twice (sanity-batch re-run + multi-day-friendly checkpoint dir structure parallel to the lobbyist-side scrape). Three new committed parser fixtures under `tests/fixtures/wi/principal_{12997,11348,11530}.html` for future regression coverage.

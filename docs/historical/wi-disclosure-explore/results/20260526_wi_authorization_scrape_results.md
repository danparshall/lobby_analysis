<!-- Generated during: convos/20260526_wi_authorization_scrape_implementation.md -->

# WI Lobbyist↔Principal Authorization Scrape — Results

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Plan:** [`plans/wi_authorization_scrape.md`](../plans/wi_authorization_scrape.md)
**Originating convo:** [`convos/20260526_wi_authorization_scrape_implementation.md`](../convos/20260526_wi_authorization_scrape_implementation.md)
**Data source:** per-lobbyist HTML detail pages at `lobbying.wi.gov`, captured 2026-05-26
**Output TSV (gitignored):** `/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv`

## Headline numbers

| Metric | Value |
|---|---|
| Lobbyist IDs in the LobbyistList grid (2025REG) | 774 |
| Per-lobbyist pages fetched | 774 (763 fresh + 10 from earlier small-batch + 1 re-fetch after soft-404 fix) |
| Hard 404s | 0 |
| Soft 404s (HTTP 200 + "Page Not Found" body) | 1 (lobbyist_id=12717) |
| Lobbyists yielding a real "Principals Represented" table | 773 |
| Lobbyists with ≥1 authorization | 745 |
| Lobbyists with 0 authorizations | 29 (incl. the 1 soft 404) |
| Total `(lobbyist, principal)` authorization rows | **2,251** |
| Distinct principals authorized by ≥1 lobbyist | 942 |
| Currently-withdrawn rows (`withdrawn_on` set) | 258 |
| Pending-authorization rows (`authorized_on` IS NULL) | 4 |
| Avg authorizations per active lobbyist | 3.02 |
| Wall time (full scrape, 1.0 s delay) | 851 s ≈ 14 min 11 s |
| Per-fetch rate (HTTP + sleep) | ~1.11 s/req |

## Authorization-date distribution

| Year | Rows |
|---|---|
| 2024 (Dec only) | 716 |
| 2025 | 1,398 |
| 2026 (through May) | 133 |
| **Pending (`authorized_on` IS NULL)** | 4 |
| **Total** | 2,251 |

Earliest: 2024-12-03. Latest: 2026-05-11.

## Top-10 most-represented principals

Highest `count(lobbyist_id)` per `principal_id` — proxy for influence concentration on the principal side.

| Rank | Principal ID | Principal name | # lobbyists |
|---|---|---|---|
| 1 (tied) | 11633 | Wisconsin Automobile and Truck Dealers Association, Inc. | 15 |
| 1 (tied) | 11319 | Wisconsin Hospital Association | 15 |
| 3 | 11107 | Wisconsin REALTORS Association | 12 |
| 4 | 11541 | ATC Management Inc. | 11 |
| 5 (tied) | 10936 | WEC Energy Group, Inc. | 10 |
| 5 (tied) | 11637 | Wisconsin Manufacturers & Commerce | 10 |
| 7 | 11110 | One City Schools, Inc. | 9 |
| 8 (tied) | 11599 | Secure Democracy USA and its Affiliates | 8 |
| 8 (tied) | 11138 | Milwaukee Public Schools | 8 |
| 8 (tied) | 12822 | AT&T Wisconsin | 8 |

## Top-10 most-active lobbyists

Highest `count(principal_id)` per `lobbyist_id` — lobbyists representing the most principals concurrently. Names extracted from each lobbyist's detail-page `<h1>` heading.

| Rank | Lobbyist ID | Lobbyist name | # principals |
|---|---|---|---|
| 1 | 11052 | Bryan Brooks | 41 |
| 2 (tied) | 11442 | Jeff Fitzgerald | 38 |
| 2 (tied) | 11524 | Buddy Julius | 38 |
| 4 (tied) | 11093 | Alicia Schweitzer | 37 |
| 4 (tied) | 11187 | Jeremey Shepherd | 37 |
| 6 (tied) | 11091 | RJ Lambert | 36 |
| 6 (tied) | 11177 | Joe Leibham | 36 |
| 6 (tied) | 11273 | Jamie Kuhn | 36 |
| 9 (tied) | 11107 | Daniel Romportl | 35 |
| 9 (tied) | 11182 | Annie Early | 35 |

## Notable findings & anomalies

### 40 principals in the auth graph aren't in the `WI_directory_principals.xls`

The principal directory `.xls` exported 5/25/2026 has 904 entries. The scraped authorization graph references 942 distinct principal IDs. The 40-entry gap means current 2025-2026-session lobbyists are authorized to represent 40 principals that the directory file doesn't list.

Hypotheses (untested):
- Principals that registered after the 5/25 directory print and before the 5/26 scrape
- Principals that ceased registration but whose ID still appears in unwithdrawn lobbyist authorizations
- Principal IDs from prior biennia that the portal still resolves (suggests `principal_id` is cross-session-stable)

Example IDs missing from the directory: `10949, 10973, 11017, 11048, 11227, 11248, 11250, 11251, 11271, 11320` (10 of 40). Each is reachable as a lobbyist-side href; spot-checking one against `/Who/PrincipalInformation/2025REG/Information/{id}` from the live portal would confirm the hypothesis.

### 2 directory principals have 0 lobbyists authorized

Conversely, 2 of the 904 directory principals are registered but have no lobbyist authorizations in the 2025-2026 session. (IDs not enumerated in this writeup — recoverable from the data.) Plausible: principals that registered but haven't engaged anyone yet, or whose lobbyist authorizations all withdrew.

### 4 pending-authorization rows

The parser was updated mid-session to handle `Authorized On = N/A` (initial design treated all dates as required). Persisted these as `authorized_on=None`. Mid-scrape audit identified the 4 rows:

| lobbyist_id | principal_id | principal name | withdrawn_on |
|---|---|---|---|
| 11112 | 11415 | Wisconsin Reading Corps | (N/A) |
| 12666 | 12818 | Union Pacific Railroad | 2025-07-31 |
| 12748 | 11252 | Superior Air-Ground Ambulance Service | (N/A) |
| 13865 | 11415 | Wisconsin Reading Corps | (N/A) |

Lobbyist 12666's row is the structurally weirdest — a withdrawal date on a never-authorized representation. Likely a data-entry issue at the WI Ethics Commission's side; preserved as-is.

### 1 soft-404 (lobbyist_id=12717)

The WI portal returns HTTP 200 with a "Page Not Found" body for nonexistent lobbyist IDs (rather than HTTP 404). The fetcher's first pass treated it as a real fetch; the materialize step's failure on a missing "Principals Represented" section surfaced the soft-404 pattern. Fetcher updated to detect the body marker, treats matches as `html=null, status_code=404`.

The original 12717 capture is preserved at `_authorization_scrape_checkpoints/12717.diagnostic_soft_404_capture.json` (gitignored, in the data store) — kept per the experiment-data-integrity rules even though the same body is re-fetchable.

### Other anomalies

- Lobbyists with 0 authorizations (excluding the soft-404): 28 (each appears in the LobbyistList grid but has an empty "Principals Represented" table). These are legitimately listed lobbyists with no current authorizations — a real state, not a bug.
- Authorization dates outside the nominal 2025-2026 session window: 716 rows in late 2024 (session begins Jan 2025 but registrations open 12/3/2024+). 133 rows in 2026 (in-session). No dates outside the plausible window.

## Validation

| Check | Result |
|---|---|
| Lobbyist 11042's 9 principals match the test fixture | ✓ Set equality: `{10937, 11004, 11102, 11110, 11158, 11300, 11590, 11678, 13214}` |
| Sanity batch (10 lobbyists, IDs 11040-11049) produces same edges as the full run | ✓ Yes (checkpoint-resume contract, no re-fetch needed) |
| Spot-check 5 random rows against live portal (manual) | _Not done in this session — held over_ |

## Reproducibility

Re-run is idempotent (resume contract via `{lobbyist_id}.json` checkpoints):

```
uv run python -m lobby_analysis.io.wi.scrape_authorizations
```

Defaults (production):
- `--delay 1.0` (politeness floor)
- `--checkpoint-dir /Users/dan/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints`
- `--session-id 2025REG`
- `--output /Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv`

Re-materialize from existing checkpoints (no HTTP): `--skip-fetch`.
Force re-discovery: delete `_lobbyist_grid_2025REG.html` from the checkpoint dir.
Force a single lobbyist re-fetch (e.g., to refresh a soft-404 case): delete `{id}.json` from the checkpoint dir and re-run.

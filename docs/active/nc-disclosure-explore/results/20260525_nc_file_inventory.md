<!-- Generated during: convos/20260525_nc_disclosure_initial_look.md -->

# NC Lobbying Disclosure Files — Inventory

**Source:** [NC SoS Lobbying Download](https://www.sosnc.gov/online_services/lobbying/download)
**Pulled:** 2026-05-24 (NC_2026.xlsx) and 2026-05-25 (4 directory files)
**Storage location:** `~/data/lobby_analysis/disclosures/NC/` (gitignored)

## Files

| File | Size | Rows | Cols | Source surface | Content |
|---|---:|---:|---:|---|---|
| `NC_2026.xlsx` | 226 KB | 2,964 | 25 | Term export ("2026(Excel)" link) | Lobbyist↔principal pairs for Term=2025 |
| `NC_directory_lobbyists.xlsx` | 127 KB | 3,198 | 12 | Real-time Directory | Lobbyist-principal pairs with email |
| `NC_directory_principals.xlsx` | 163 KB | 3,062 | 13 | Real-time Directory | Principal-lobbyist pairs with officer + email |
| `NC_directory_state_agency_liaisons.xlsx` | 7 KB | 100 | 8 | Real-time Directory | State agency liaisons (covered-official side) |
| `NC_directory_local_govt_liaisons.xlsx` | 2 KB | 6 | 8 | Real-time Directory | Local government liaisons |

All 4 directory files arrived as `daily_*.xls` from `~/Downloads/lobby/nc/`. Content was XLSX format despite `.xls` extension (verified via `file` command); renamed to `.xlsx` at move time.

## `NC_2026.xlsx` — full schema

| # | Column | Notes |
|---:|---|---|
| 0 | `Term` | Always `2025` in this file |
| 1 | `LobbyName` | Whole name, 678 unique |
| 2 | `LobbyPrefix` | 5 unique values; 98.5% null |
| 3 | `LobbyFirst` | 416 unique |
| 4 | `LobbyMid` | 165 unique; 49% null |
| 5 | `LobbyLast` | 562 unique |
| 6 | `LobbySuffix` | 9 unique; 92% null |
| 7 | `LobbyFirm` | 269 unique; 12% null (=in-house lobbyists) |
| 8 | `LobbyAddress` | 567 unique |
| 9 | `LobbyCity` | 128 unique |
| 10 | `LobbyState` | 30 unique; 93% NC |
| 11 | `LobbyZip` | 244 unique |
| 12 | `LobbyPhone` | 564 unique |
| 13 | `Principal` | 1,269 unique |
| 14 | `PrinOfficer` | 1,274 unique |
| 15 | `PrinTitle` | **100% null** |
| 16 | `PrinAddress` | 1,254 unique |
| 17 | `PrinCity` | 393 unique |
| 18 | `PrinState` | 42 unique; 58% NC |
| 19 | `PrinZip` | 749 unique |
| 20 | `PrinPhone` | 1,185 unique |
| 21 | `SqlLogUserId` | **100% null** (audit) |
| 22 | `SqlLogUserIp` | Literal string `'False'` everywhere (audit, misnamed) |
| 23 | `SqlLogUserName` | **100% null** (audit) |
| 24 | `ReadOnlySearch` | **100% null** (audit) |

## `NC_directory_lobbyists.xlsx` — full schema

`Lastname` · `Middlename` · `Firstname` · `Suffix` · `Address` · `City` · `State` · `ZipCode` · `Telephone` · **`Email`** · `Principal` · `PrincipalPhone`

12 columns. Includes email (term export does not). One row per (lobbyist, principal) pair.

## `NC_directory_principals.xlsx` — full schema

`Principal` · `Address` · `City` · `State` · `ZipCode` · `Telephone` · **`Email`** · `OfficerFirstName` · `OfficerMiddleName` · `OfficerLastName` · `OfficerSuffix` · `Lobbyist` · `LobbyistPhone`

13 columns. Principal-side denormalization (vs the lobbyist-side denormalization of `_lobbyists`). Officer name parts present (term export only had `PrinOfficer` whole-string).

## `NC_directory_state_agency_liaisons.xlsx` — full schema

`StateDepartment` · `Address` · `City` · `State` · `ZipCode` · `Telephone` · `Email` · `Liaison`

8 columns, 100 rows. Examples: NC Department of Commerce Division of Employment Security, NC Administrative Office of the Courts. The "covered-officials" side of the lobbying graph.

## `NC_directory_local_govt_liaisons.xlsx` — full schema

`GovernmentUnit` · `Address` · `City` · `State` · `ZipCode` · `Telephone` · `Email` · `Liaison`

8 columns, only 6 rows. Examples: Charlotte-Mecklenburg Board of Education, Chatham County. Very small registry.

## Entity-level counts (NC_2026.xlsx, term export only)

- Unique lobbyists: 678
- Unique firms: 269 (347 rows have no firm = in-house)
- Unique principals: 1,269
- Unique (lobbyist, principal) pairs: 2,905 (so 59 duplicate-pair rows)
- 53 duplicate-pair groups: 45 byte-identical (export artifacts; exact-dedupe safe), 8 with real differences (firm name typos, officer transitions, employment-status change)

## Top lobbyists by # principals (NC_2026.xlsx)

| Lobbyist | Principals |
|---|---:|
| Charles Franklin McDowell | 63 |
| Nelson Freeman | 50 |
| John A. Hardin | 43 |
| William Morgan | 43 |
| Hampton Michael Billips | 41 |

Heavy-tailed distribution: 464 lobbyists have just 1 principal; 70+ have 10+; one has 63.

## Not yet profiled (deferred to next session)

The 4 directory files have headers + sample rows characterized above but have NOT been run through the parallel count/unique/null/dup profiling that `NC_2026.xlsx` received. Specifically open:

- Lobbyist row counts in `_lobbyists` (3,198) vs term export (2,964) — why the difference?
- Are the 4 directory files internally consistent (e.g., does the lobbyist set in `_lobbyists` equal the lobbyist set referenced in `_principals`)?
- Email coverage — what fraction of lobbyists and principals have non-null email?
- Liaison registries: distribution of agencies, completeness of contact info

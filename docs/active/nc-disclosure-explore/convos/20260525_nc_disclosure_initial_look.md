# NC Disclosure — Initial Look

**Date:** 2026-05-25
**Branch:** nc-disclosure-explore

## Summary

First session on this branch. User dropped a single NC lobbying disclosure file (`NC_2026.xlsx`) and asked "let's see what it tells us." The session arc: (1) characterize that file, (2) trace its provenance to the NC Secretary of State Lobbying Download page, (3) survey what NC actually publishes as bulk data, (4) discover mid-session that the user had also pulled 4 *additional* NC files from a different surface (the SoS "real-time Directory"), (5) inspect and rename those, (6) consolidate into a per-state subdirectory.

The dominant finding is structural rather than empirical: **NC publishes only registration-side data as free bulk downloads** — no expenditure reports, no contact logs, no gifts, no bills, no dates — even though those filings legally exist and are publicly inspectable per-record. This is a concrete schema-vs-reality data point feeding the project's gather-first pivot toward v2.2 compendium design.

Branch is left in checkpoint state: file inventory complete, file profiles partial (NC_2026.xlsx profiled in detail; 4 directory files have headers + sample rows only). No commitment yet to compendium-walk work, ingestion-pipeline work, or schema work. Decision deferred to next session.

## Topics Explored

- Schema, row count, null/unique distributions, and duplicate-pair analysis of `NC_2026.xlsx`
- Out-of-state vs in-state distribution on both lobbyist side (93% NC) and principal side (58% NC)
- Source URL recovery: `https://www.sosnc.gov/online_services/lobbying/download`
- WebFetch of the SoS download page to inventory what NC publishes for bulk
- Web search to verify whether other NC agencies (Ethics Commission, Board of Elections) publish a different slice of lobbying data
- Inspection of the 4 `daily_*.xls` files from `~/Downloads/lobby/nc/` (turned out to be XLSX content despite `.xls` extension)
- Filename and directory-structure design for per-state data organization
- Implication for the compendium `practical_availability` axis given tiered NC access surface

## Provisional Findings

- **`NC_2026.xlsx` is the term-based registration export.** 2,964 rows, all `Term=2025`. 678 unique lobbyists, 1,269 unique principals, 269 firms (with 347 in-house lobbyist rows lacking a firm). 25 columns: lobbyist identity + principal identity + 4 SQL-export audit columns that can be dropped.
- **The 4 `daily_*.xls` files are the SoS "real-time Directory" exports**, a different surface from the term export:
  - `NC_directory_lobbyists.xlsx`: 3,198 lobbyist-principal rows, includes `Email`
  - `NC_directory_principals.xlsx`: 3,062 principal-lobbyist rows, includes officer name parts + email
  - `NC_directory_state_agency_liaisons.xlsx`: 100 rows of state-agency liaisons (covered-official side)
  - `NC_directory_local_govt_liaisons.xlsx`: 6 rows of local-government liaisons
- **The directory files include email addresses** which the term export does not — useful for entity disambiguation across states.
- **The directory files include the liaison-side registries** (state agency reps + local govt reps who are recipients of lobbying), a category not represented in the term export.
- **NC publishes nothing about lobbying *activity* in free bulk form.** No expenditure, no compensation, no bills lobbied, no officials contacted, no gifts, no within-term dates. The data legally exists (quarterly expense reports filed with SoS under Chapter 120C; monthly during session if covered-official spend) and is "open to public inspection," but the public access tiers are: (1) free + bulk + scriptable → registrations only; (2) free + per-record web search → all reports, JS-only, "scripted search forbidden"; (3) paid SoS Data Subscription Services → presumably bulk reports; (4) annual "Lobbying Compliance Report" PDF aggregate (latest 2022-23).
- **Schema-vs-reality observation for the compendium.** The `practical_availability` axis as currently written is likely a single yes/no per row. NC concretely shows that a single bit cannot distinguish "free bulk machine-readable" from "free per-record manual" from "paid bulk machine-readable" — each is a meaningfully different access posture. Worth surfacing as a v2.2 design candidate.
- **Data-quality notes on the term export:**
  - 53 duplicate `(lobbyist, principal)` groups: 45 are byte-identical (pure export artifacts; exact-match dedupe is safe); 8 have real differences (firm-name typos, principal-officer transitions, lobbyist-employment-status change). The 8 deserve a hand pass before any modeling.
  - `PrinTitle` column is 100% null across all 2,964 rows — schema field exists, NC isn't populating it.
  - `SqlLogUserIp` column is the literal string `'False'` on every row — almost certainly a misnamed boolean from the source DB.
  - Heavy-tailed lobbyist-to-principal distribution. Top 5: Charles Franklin McDowell (63 principals), Nelson Freeman (50), John A. Hardin (43), William Morgan (43), Hampton Michael Billips (41).
- **Geographic asymmetry.** Lobbyist side: 93% NC-based (2,753/2,964). Principal side: only 58% NC; DC/CA/VA/NY take meaningful share. Pattern: out-of-state corporate interests routing through NC-based lobbyists.

## Decisions Made

- **Branch created:** `nc-disclosure-explore` (worktree at `.worktrees/nc-disclosure-explore`, data symlink to `~/data/lobby_analysis/`).
- **Per-state data subdirectory introduced:** `~/data/lobby_analysis/disclosures/NC/` holds all NC files.
- **Naming convention for directory files:** `NC_directory_<type>.xlsx` (type = `lobbyists` | `principals` | `state_agency_liaisons` | `local_govt_liaisons`). Type-only names, no date suffix — sufficient for first pass; add date stamps if/when we start tracking vintages.
- **`.xls` extensions rewritten to `.xlsx`** since the content is XLSX format (verified via `file` command).
- **Goal for this branch (per user):** catalog NC's publication shape for the compendium practical-availability axis. NOT to build an ingestion pipeline.
- **Deferred / not committed:** schema-redesign work for tiered `practical_availability`; full 181-row compendium walk for NC; ingestion-pipeline prototype; multi-vintage analysis using "all previous terms" download.

## Results

- [results/20260525_nc_file_inventory.md](../results/20260525_nc_file_inventory.md) — file inventory + schema headers + row/col counts for all 5 NC files

## Open Questions

- **Term semantics.** `Term=2025` in NC_2026.xlsx — is this calendar 2025, the first year of a 2025-2026 biennium, or something else? Affects how we interpret cross-vintage downloads. The download page exposes "2026(Excel)" + "All previous terms(Excel)"; the file the user pulled labelled 2026 contains Term=2025. Worth one careful read of the page or NC statute.
- **Why row-count discrepancies between bulk surfaces?** Term export has 2,964 lobbyist-principal pairs; directory `_lobbyists` export has 3,198; directory `_principals` export has 3,062. Different snapshot dates? Different inclusion criteria (active vs pending vs terminated)? Different denormalization? Not yet investigated.
- **SoS Data Subscription Services price + terms.** This is almost certainly how OpenSecrets-style aggregators get NC expenditure data. Worth knowing for project strategy. Worth checking whether Corda Fellowship has any institutional access.
- **What's in the annual Lobbying Compliance Report (2022-23)?** PDF-only aggregate, but could give us validation totals (spend by year, top spenders) for sanity-checking any future extraction.
- **Should the tiered practical-availability finding become a v2.2 design item?** Concrete NC evidence that the current axis is under-specified. Worth raising in the next round of v2.2 design conversations, but not committed to as schema work on this branch.
- **Do other states have a similar "real-time Directory" vs "term export" split?** If so, the same dual-surface analysis is replicable across states. If unique to NC, less generalizable.
- **What does the "all previous terms" download contain?** Multi-term cumulative? Per-term files? Would enable longitudinal analysis if pulled.

## Provenance

Source URL for all NC files: [https://www.sosnc.gov/online_services/lobbying/download](https://www.sosnc.gov/online_services/lobbying/download).
NC files now consolidated at `~/data/lobby_analysis/disclosures/NC/` (gitignored).

<!-- Generated during: convos/20260527_2025_cohort_expansion_and_co_fix.md -->

# Statute Section-File Inventory — 2026-05-27

Per-state per-vintage file counts in `~/data/lobby_analysis/statutes/<STATE>/<VINTAGE>/sections/`.
Machine-local on Dans-MacBook-Pro; not under git.

| State | 2010 | 2015 | 2025 | Notes |
|-------|-----:|-----:|-----:|-------|
| AK    |   20 |   20 |   20 | |
| AR    |   16 |   16 |   15 | 2025 substituted to 2024 |
| CA    |    8 |   55 |   56 | |
| CO    |   11 |   11 |   11 | 2015 substituted to 2016; 2025 substituted to 2024; 2025 bundle rebuilt via mechanical /2016/→/2024/ URL swap after the 5/19 article-directory-URL bundle was found to fetch TOC pages, not statute bodies |
| FL    |    – |   14 |   18 | Both vintages added this session; 4 sections added between 2015 and 2025 (112.3121–112.3124, post-office lobbying prohibition, 2018 constitutional amendment); URL slug convention drifted (dot-separated at 2015, hyphen-separated at 2025) |
| IL    |    3 |   12 |    9 | 2025 URLs are article-level directory-leaves (TX 2015 pattern); Justia inlines section text on article pages so coverage is equivalent to the 12-URL 2015 bundle |
| MA    |   11 |   11 |   11 | |
| MI    |   23 |   23 |   23 | |
| NC    |    – |   32 |   30 | Both vintages added this session; 2 sections removed/recodified between 2015 and 2025 (120C-215 Other persons required to register; 120C-404 Solicitor's reports); same Chapter 120C, same 8 articles |
| NY    |    1 |    – |    – | Lossy 3 at 2015; nothing at 2025 |
| OH    |   39 |   52 |   30 | 2025 from `statute-retrieval` branch (predates this session); 52→30 delta vs 2015 not investigated here |
| PA    |   11 |   11 |   11 | |
| TX    |    1 |    1 |   35 | 2010/2015 are single directory-leaf URLs (Government Code Ch. 305 inlined); 2025 explodes to 35 section URLs |
| WA    |   17 |   19 |   42 | |
| WI    |   16 |   16 |   16 | |
| WV    |   24 |   24 |   34 | |
| WY    |    1 |    – |    – | Lossy 3 at 2015; nothing at 2025 |
| **#states** | **15** | **15** | **15** | |
| **#files**  | **202** | **317** | **361** | |

## Cross-vintage coverage

- **Paired 2015 + 2025:** 15 states (AK, AR, CA, CO, FL, IL, MA, MI, NC, OH, PA, TX, WA, WI, WV)
- **Triple 2010 + 2015 + 2025:** 13 states (paired set minus FL and NC, which had no 2010 work — PRI 2010 didn't ground-truth either)
- **2010 only:** NY, WY (1 file each, pre-TSV-capture era)

## Session deliverables

| Vintage | States added | Files added |
|---------|--------------|-------------|
| 2015    | +2 (NC, FL)  | +46 |
| 2025    | +12 (AK, AR, CA, CO, FL, IL, MA, NC, PA, TX, WA, WV) — was 3 (MI, OH, WI) | +328 (incl. CO rebuild) |

Method A dispatches: 4 (FL 2025, NC 2025, NC 2015 retry, FL 2015 from-scratch), all CF-clear.
Method B sections fetched: ~380 URLs across 14 state-vintage bundles, zero CF stubs.

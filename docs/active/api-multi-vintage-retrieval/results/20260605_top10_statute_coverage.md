<!-- Generated during: convos/20260605_top10_vintage_gapfill.md -->

# Top-10 Priority States — 3-Vintage Statute Coverage (2026-06-05)

**Trigger:** Priority-state list updated. New top-10 (NY, CO, WI, CA, TX, IL, WA, FL, NC, OH) chosen *because of* the `docs/reports/state_bulk_data_availability/` research (chain-closure tiers). Goal: confirm statute text for 3 vintages — **2010, 2015, 2025** — across all 10 states (30 cells).

**Vintages = statute-as-it-stood (legal text), not bulk filing records.** 2010/2015/2025 align with the rubric-validation vintages (PRI 2010, CPI/Sunlight 2015, current).

## Final coverage — section-file counts in `~/data/lobby_analysis/statutes/<STATE>/<VINTAGE>/sections/`

| State | 2010 | 2015 | 2025 | Notes |
|-------|-----:|-----:|-----:|-------|
| NY | 23\* | 22 | 22 | **Filled this session.** Legislative Law Art. 1-A §§1-A…1-V (22 leaves) at all 3 vintages. \*2010 = 22 new leaves + 1 pre-existing lossy stub left in place. |
| CO | 11 | 11 | 11 | Prior. All 3 date-substituted (2015→2016, 2025→2024; 2010 historically →2016 — validity flagged, see caveats). |
| WI | 16 | 16 | 16 | Prior. |
| CA | 8 | 55 | 56 | Prior. |
| TX | 1 | 1 | 35 | Prior. 2010/2015 = single inlined Gov. Code Ch.305 page (legit, not a stub); explodes to 35 sections by 2025. |
| IL | 3 | 12 | 9 | Prior. 2010 = inline single-page acts (legit). |
| WA | 17 | 19 | 42 | Prior. 2025 reflects the Title 42→29B reorg. |
| FL | 13 | 14 | 18 | **2010 filled this session** (Ch.11 legislative + Ch.112 executive). |
| NC | 32 | 32 | 30 | **2010 filled this session** (Chapter 120C, 8 articles). |
| OH | 39 | 52 | 30 | Prior. 52→30 delta 2015→2025 still uninvestigated. |

**30/30 cells have statute text.** Size sanity-check on the 5 newly-fetched cells: medians 2.7–4.3 KB, **zero files <500B** (no Cloudflare-stub or parse-miss contamination).

## Work done this session (the 5 gap cells)

Before this session: 25/30 present. Genuine gaps were **NY 2010 (lossy 1-file stub), NY 2015 (missing), NY 2025 (missing), FL 2010 (missing), NC 2010 (missing)** — 4 of the 5 in the two top-priority states (NY, CO… NY especially).

| Cell | Discovery | Fetch | Result |
|------|-----------|-------|--------|
| FL 2010 | Method-B subagent, CF-clear | 13 sections | Ch.11 §§11.045–062 + Ch.112 §§112.3215–3217 +3 support. = FL 2015 minus post-2010 §112.3261. |
| NC 2010 | Method-B subagent, CF-clear | 32 sections | Chapter 120C, all 8 articles. Structurally = NC 2015, incl. §120C-215 & §120C-404 (present 2010/2015, removed by 2025). Un-hyphenated 2010 slugs. |
| NY 2010 | Method-B subagent, CF-clear | 22 sections | Legislative Law Art. 1-A §§1-A…1-V via `leg/article-1-a/`. **Non-lossy** — supersedes the prior 1-file `rla/` stub the 5/15 pilot left. |
| NY 2015 | Method-B subagent, CF-clear | 22 sections | Same 22 leaves. Fixes the prior "lossy 3". |
| NY 2025 | Method-B subagent, CF-clear | 22 sections | Same 22 leaves; year-prefixed via the year-less-convention helper patch. |

Discovery bundles: `results/subagent_canaries/{FL_2010,NC_2010,NY_2010,NY_2015,NY_2025}/`.
Section-fetch driver: `scripts/fetch_gap_cells_sections.py` (rate_limit 2.5s, skips NY `rla/` monolith).

## Substantive findings

- **NY Lobbying Act is structurally stable 2010→2025.** §§1-A…1-V identical across all 3 vintages at leaf granularity. The 2022 JCOPE→COELIG transfer amended section *substance* (e.g. 1-D "Lobby-Related Powers of the Commission") but added/removed no sections.
- **NC 2010 = NC 2015** (same 32-section Ch.120C). The only 2010→2025 deltas are the two removed sections.
- **FL 2010 helper gap (Method-A).** FL 2010 uses a flat-sibling convention where Part-III sections live as siblings in `chapter112/` (e.g. `chapter112/112_3215.html`), not under a `PARTIII/` subdir. `_build_justia_link_tsv` returned an empty TSV on `PARTIII.html`; the subagent recovered the 37-section snapshot from saved HTML. **Method-A automation needs a 5th namespace pattern (flat-sibling Part page) for FL 2010.**

## Caveats on the "prior" (already-present) cells

- **CO** — all 3 vintages are Justia date-substitutions (2015→2016, 2025→2024; 2010 historically →2016, *outside* the ±5 window). CO 2010 substitution-validity flagged in the 2026-05-19 log as needing human review before use as a calibration anchor. Not re-examined this session.
- **OH** — 2015→2025 file drop (52→30) never investigated.
- **TX 2010/2015 = 1 file, IL 2010 = 3 files** are *legitimate* inline single-page codifications, not incomplete fetches.

## CF posture note

CF cleared on **Dans-MacBook-Pro** through all 5 discovery bundles (~110 TOC/section page fetches) **and** all 111 section-body fetches — zero challenges. This is a *clean-window* observation, consistent with 5/27's clear run on Pro; it does **not** resolve the open machine-vs-time-vs-URL-family question, and does **not** retire the stealth-Playwright recommendation. The window held; next session may not get one.

## Cross-machine sync

New section bodies are machine-local on Dans-MacBook-Pro under `~/data/lobby_analysis/statutes/{FL/2010,NC/2010,NY/2010,NY/2015,NY/2025}/`. **Needs sync to Air/tarragon** before downstream use there.

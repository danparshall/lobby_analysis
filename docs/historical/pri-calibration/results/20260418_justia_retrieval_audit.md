# Justia Retrieval Audit — 50 States, 2010 Vintage

**Date:** 2026-04-18
**Branch:** pri-calibration
**Method:** Phase 1 of `plans/20260417_pri_ground_truth_calibration.md` via `plans/20260417_statute_retrieval_module.md`
**Data:** [`20260418_justia_retrieval_audit.csv`](20260418_justia_retrieval_audit.csv)

## Executive summary

**49 of 50 states are eligible for 2010 calibration.** The single excluded state is Colorado (Justia's earliest CO year is 2016, which is 6 years out from 2010 — outside the ±2 year tolerance). All 50 states are eligible for 2026-vintage scoring (every state has a recent year on Justia, typically 2024 or 2025).

This is a much better outcome than the plan anticipated. The original Phase 1 decision gate was:

- ≥ 40 eligible → proceed
- 20–39 → proceed with partial coverage
- < 20 → re-scope entirely

We land at 49/50 without needing any Wayback or HeinOnline fallbacks — the Justia-unified retrieval architecture is validated.

## Vintage distribution

Of the 49 calibration-eligible states:

| Direction | States | Year used | Interpretation |
|-----------|--------|-----------|----------------|
| `exact` | 34 | 2010 | Directly matches PRI's scoring vintage |
| `pre` | 15 | 2009 (delta=-1) | Pre-PRI vintage; may miss late-2009 changes |
| `post` | 0 | — | No state forced us to use a post-2010 vintage |

All `pre` states are exactly one year prior. The ±2 tolerance is barely used — the nearest-year ladder converges to 2009 or 2010 for every eligible state. Using asymmetric pre-preferred tie-breaking never mattered because post-2010 years were never the closest option for any eligible state.

## Trust-weighted pool (PRI responder overlap)

PRI 2010 validated 34 of 50 states by emailing results to state officials for review. The 34 responders are higher-trust ground truth than the 16 non-responders.

| Audit outcome | Responders (of 34) | Non-responders (of 16) |
|---------------|--------------------|------------------------|
| Eligible for calibration | 33 | 16 |
| Ineligible | 1 (CO) | 0 |

The one ineligible state (CO) is a responder — we lose it from both eligibility buckets. **Net calibration pool: 33 responder states + 16 non-responder states = 49.**

The Phase 3 baseline should partition agreement metrics on responder status (already planned in the calibration-harness sub-plan).

## Historical coverage depth

Breakdown of each state's earliest available Justia year:

| Earliest year | # states | Notes |
|---------------|----------|-------|
| 1973 | 1 | Washington |
| 1993 | 1 | Alaska |
| 1997 | 2 |  |
| 2005 | 17 |  |
| 2006 | 18 |  |
| 2009 | 4 |  |
| 2010 | 6 | Just-barely eligible; no pre-2010 fallback available |
| 2016 | 1 | Colorado (excluded) |

Most states have 15+ years of Justia history. This matters for possible future calibration work (e.g., scoring multiple vintages to track reform trajectories).

## Colorado exclusion (detail)

| Field | Value |
|-------|-------|
| Earliest year | 2016 |
| Latest year | 2024 |
| PRI 2010 disclosure-law rank | 36 (19 of 37 = 51.4%, near-median) |
| PRI 2010 accessibility rank | 13 (11.2/22 = 50.9%, upper-median) |
| PRI responder | Yes |
| Eligible for 2026 scoring | Yes |

Losing CO is survivable. Calibration pool remains 49 states spanning the full PRI score distribution. CO will still be scored against 2026 statutes (no 2010 baseline comparison is possible) and flagged as such in the final deliverable.

## Method

Per `plans/20260417_statute_retrieval_module.md`, narrowed for Phase 1:

1. Fetch `https://law.justia.com/codes/<state>/` per state (Justia state-index page).
2. Parse the year list (`<a>` elements with `/codes/<state>/YYYY/` hrefs).
3. Apply the `pick_year_within_tolerance(target=2010, tolerance=2)` ladder with pre-preferred-on-tie.
4. Emit one CSV row per state.

Retrieval used `PlaywrightClient` (fresh browser per request, headless Chromium, realistic user agent). Cloudflare's JS challenge is the reason for Playwright — curl/WebFetch are blocked. Fresh browser per request was needed because a long-lived browser context gets progressively more-aggressively challenged after the first fetch and never clears.

Rate-limit: 2 seconds courtesy delay between states. 50 states × ~20 seconds per state (browser launch + navigate + challenge wait + close) ≈ 17 minutes of wall time.

## What this audit did NOT check

- **Chapter-level availability.** The audit confirms a state has a given year, not that the year contains the lobbying/ethics title we'll need to score. Some Justia years back-fill partial coverage. Chapter presence check belongs with Phase 2 retrieval (where we'd be fetching the title pages anyway).
- **Statute text retrieval.** No section-range pages fetched; no statute text bundles built. That is Phase 2 work.

Both will surface as TDD sub-plans in the next session.

## Next action

Pick the Phase 3 calibration subset — 5 states spanning the PRI 2010 score distribution, weighted toward responders for higher-trust comparison. Candidates worth considering:

- **Top:** Connecticut (rank 1 accessibility), Texas / Alaska (disclosure-law top)
- **Median:** Several responder states near rank 25
- **Bottom:** Wyoming / Oklahoma (bottom of distribution)

Pick from the eligible 49 per responder status and spread. Dan's call on the specific 5.

## CSV schema

| Column | Type | Notes |
|--------|------|-------|
| state_abbr | str | USPS code |
| target_year | int | 2010 in this audit |
| chosen_year | int \| empty | Best year within tolerance; empty if none |
| year_delta | int \| empty | Signed delta (negative=pre, positive=post) |
| direction | enum | `exact` / `pre` / `post` / `none` |
| current_year | int | Most recent year Justia hosts |
| eligible_for_calibration | bool | chosen_year is not null |
| eligible_for_2026_scoring | bool | current_year > 0 |
| pri_state_reviewed | bool | In PRI footnote 80's 34-state responder list |
| n_available_years | int | Count of years on Justia |
| min_available_year | int | Earliest year Justia hosts |
| max_available_year | int | Same as current_year |

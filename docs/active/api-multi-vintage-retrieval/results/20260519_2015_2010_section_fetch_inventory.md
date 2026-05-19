<!-- Generated during: convos/20260519_fetch_2015_2010_sections.md -->

# Section-fetch inventory: 2015 (13 states) + 2010 (10 newly fetched + 5 already on disk)

**Date:** 2026-05-19
**Branch:** `api-multi-vintage-retrieval`
**Machine:** Dans-MacBook-Pro

Output of the per-state inventory scripts (`/tmp/inventory_2015.py`, `/tmp/inventory_2010.py`) after the section-fetch runs completed. All files written to `~/data/lobby_analysis/statutes/<STATE>/<intended_vintage>/sections/` (via the `data/` → `~/data/lobby_analysis/` symlink).

## 2015 fetch — 13 states, 271 files

Driven by `/tmp/fetch_2015_sections.py` against the canary bundles committed in `104268e`. Started at 5s `rate_limit_seconds`; restarted at 2.5s after WI completed (state-boundary kill to cut wall time).

```
State  Files     Min     Med      Max
------------------------------------------
TX         1   69254   69254    69254
MA        11    2027    5574    13742
PA        11    1561    5484     9708
CO        11    1838    4802    17135   (vintage-substituted → 2016)
IL        12    3431   14414    52526
AR        16    1130    1878    10909
WI        16    1660    3884    11353
WA        19    1889    4213    27818
AK        20    1544    2678     7363
MI        23    1791    2754     9596
WV        24    1677    3874    20969
OH        52    1614    3715    27646
CA        55    1573    2339     4695
------------------------------------------
TOTAL: 271 files, ALL CLEAN
```

- All files ≥ 500 bytes, medians 1.8–14 KB, no Cloudflare stubs detected.
- TX is a single-file directory-leaf URL (Justia rendered the whole chapter as one 69 KB page).
- CO substituted to 2016 (Justia doesn't host CO before 2016).
- WA's 19 URLs reflect the "Defect 2" 2010-silent-empty resolution — the chapter is real, was a real miss in the earlier lossy canary.

**Cloudflare**: zero re-engagement across all 271 fetches.

## 2010 fetch — 10 newly fetched + 5 already on disk = 15 states, 202 files

Driven by `/tmp/fetch_2010_sections.py` against the 10 new canary bundles committed in `b588b7b`. Rate limit 2.5s throughout. 3 entries (WI/OH/CA) skipped via `dest.exists()` guard because the `statute-retrieval` branch had already populated them.

```
Newly fetched (this session):
State  Files     Min     Med      Max    actual_vintage_used
---------------------------------------------------------------
TX         1   65298   65298    65298    2009  (-1)
IL         3    1604    1692    32551    2010
MA        11    1996    7432    17686    2010
PA        11    1347    5239     9464    2010
CO        11    1838    4802    17135    2016  (+6, OUTSIDE ±5)
AR        16    1119    1709    10834    2010
WA        17    1653    4267     9612    2009  (-1, pre-42.17A reorg)
AK        20    1500    2611     7319    2010
MI        23    1667    2630     9554    2010
WV        24    1535    3703    20885    2010
                                          subtotal 137

Already on disk (statute-retrieval branch):
WI        16    1423    3852    10708    2010
OH        39     705    3571    50231    2010
CA         8     709    3570    44488    2010
NY         1   51917   51917    51917    2010
WY         1    8526    8526     8526    2010
                                          subtotal 65

GRAND TOTAL 2010: 202 files
```

- All newly-fetched bundles have median sizes 1.7–7.4 KB, no CF stubs.
- `actual_vintage_used` recorded in each canary bundle's `result.json`, not in the section-bundle manifest.

## Substitution / coverage-validity flags

Three states substituted away from the intended 2010 vintage:

| State | actual | gap | reason |
|---|---|---|---|
| TX | 2009 | −1 | Justia doesn't host TX/2010; curated path also uses 2009. Within ±5 window. |
| CO | 2016 | +6 | Justia hosts no CO before 2016 (verified by trying 2010, 2011, 2009, 2012, 2008). **Outside the ±5 window** the pass-1 prompt suggests; treated as the only-available record, flagged in the canary bundle's `notes`. Content identical to `data/statutes/CO/2015/`. |
| WA | 2009 | −1 | Justia hosts WA/2010 only as a 7.7 MB monolithic volume page with no per-section URLs. Substituted to 2009 (operatively pre-42.17A reorganization — the 42.17A reorg had a 2012 effective date, so RCW 42.17 was in force during calendar 2010). |

Additional coverage-validity flags:

- **WA 2010 coverage gap:** Justia's 2009 listing starts at 42.17.030. Missing the 2010 analogues of 42.17A.005 (definitions) and 42.17A.020 (statements/reports). The agent surfaced this as a `notes` line rather than papering over with the inoperative 42.17A side.
- **IL 2010 vs IL 2015 file-count delta:** 3 URLs at 2010 vs 12 at 2015. Same statutory coverage (25 ILCS 170 + 5 ILCS 420 + 5 ILCS 430); Justia rendered as inline single-page acts at 2010 and split into per-article TOCs at 2015. Section bodies are larger but fewer files at 2010.
- **Slug convention drift across vintages (MA, PA, IL, AR, AK, MI, WV):** several states show URL-template differences between 2010 and 2015 (hyphens vs no hyphens, dots vs hyphens in section numbers, presence/absence of `section-` prefix, etc.). Same statute body, different Justia slug. A downstream consumer comparing raw URLs across vintages would treat them as disjoint sets.

## Cloudflare summary across the 2026-05-19 session

| Operation | Justia hits | CF re-engagements |
|---|---|---|
| 2015 section fetch | 271 | 0 |
| 2010 URL discovery (pass-1/pass-2/pass-3 across 10 subagents) | ~40 | 0 |
| 2010 section fetch | 137 | 0 |
| **Total** | **~450** | **0** |

The previous day's CF re-engagement pattern (afternoon escalation from pass-3 → pass-1 blocks during URL discovery) did not recur on Dans-MacBook-Pro through this session.

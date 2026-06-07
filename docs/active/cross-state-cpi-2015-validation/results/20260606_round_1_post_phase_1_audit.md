<!-- Generated during: convos/20260606_phase_1_exec_and_de_jure_pivot.md -->

# Round 1 post-Phase-1 re-audit (2026-06-06)

**Companion to:**
- [`20260605_cross_state_cpi_2015_validation.md`](20260605_cross_state_cpi_2015_validation.md) — original Round 1 audit (pre-fix, 15/30 = 50%).
- [`20260606_failure_mode_trends_and_paths_forward.md`](20260606_failure_mode_trends_and_paths_forward.md) — failure-mode analysis predicting +4 cells under Phase 1's vocab fix.

**Originating plan:** [`../plans/20260606_pre_dispatch_hygiene.md`](../plans/20260606_pre_dispatch_hygiene.md) §Phase 1.
**Phase 1 commit:** `cbcd3e2` — `phase 1 vocab fix: IND_199 IntCell-months + IND_207 CPI-enum domains; round 1 re-audit 19/30 (was 15/30)`.

**Generation:** `uv run python scripts/cross_state_cpi_2015_audit.py` against stored Round 1 extractions, with the post-Phase-1 helper code in place (no re-dispatch — same stored YAML data, re-projected through fixed helpers).

---

## Headline

**Per-(state, indicator) match rate: 19/30 (63.3%)**, up from 15/30 (50%) pre-Phase-1. **+4 cells, matching the failure-mode doc Trend 1 prediction exactly.**

Per-indicator (across 5 states):

| Indicator | Pre-fix | Post-fix | Δ |
|---|:---:|:---:|:---:|
| IND_196 | 5/5 | 5/5 | 0 (untouched by fix) |
| IND_197 | 3/5 | 3/5 | 0 (DecimalCell pathway untouched) |
| IND_199 | 1/5 | **4/5** | **+3** (NY/WI/OH/CA flip from spurious-NO to MODERATE match) |
| IND_201 | 2/5 | 2/5 | 0 (compound-arity instability untouched) |
| IND_203 | 4/5 | 4/5 | 0 (untouched) |
| IND_207 | 0/5 | **1/5** | **+1** (NY's "YES" now matches; WI/OH/CA/TX still miss but for Trend 5 reasons, not vocab schism) |

Per-state:

| State | Pre-fix | Post-fix | Δ |
|---|:---:|:---:|:---:|
| NY | 4/6 | **6/6** | +2 |
| WI | 3/6 | **4/6** | +1 |
| OH | 1/6 | **2/6** | +1 |
| CA | 3/6 | 3/6 | 0 |
| TX | 4/6 | 3/6 | -1 (TX IND_199 flips from spurious-match to correct-mismatch per plan prediction) |

---

## Table A — per-cell comparison (post-fix)

| State | Indicator | Chunk | Oracle | Projected | Match | Notes |
|---|---|---|---|---|---|---|
| NY | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| NY | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| NY | IND_199 | registration_mechanics_and_exemptions | 50 | 50 | YES | match (IntCell 24mo → MODERATE post-fix) |
| NY | IND_201 | lobbyist_spending_report | 100 | 100 | YES | match |
| NY | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| NY | IND_207 | enforcement_and_audits | 100 | 100 | YES | match (CPI-enum "YES" → 100 post-fix) |
| WI | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| WI | IND_197 | registration_thresholds | 50 | 100 | no | oracle=50 projected=100; lobbyist_registration_threshold_compensation_dollars=0 |
| WI | IND_199 | registration_mechanics_and_exemptions | 50 | 50 | YES | match (IntCell 24mo → MODERATE post-fix) |
| WI | IND_201 | lobbyist_spending_report | 0 | 0 | YES | match |
| WI | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| WI | IND_207 | enforcement_and_audits | 100 | 50 | no | Trend 5: extracted "MODERATE" (compliance review), oracle YES. Helper correctly maps "MODERATE"→50; mismatch is CPI-generosity, not vocab schism. |
| OH | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| OH | IND_197 | registration_thresholds | 50 | 100 | no | oracle=50 projected=100; scor_unstable (value=0) |
| OH | IND_199 | registration_mechanics_and_exemptions | 50 | 50 | YES | match (IntCell 24mo → MODERATE post-fix) |
| OH | IND_201 | lobbyist_spending_report | 50 | 0 | no | oracle=50 projected=0; compound-arity instability |
| OH | IND_203 | principal_spending_report | 50 | 0 | no | oracle=50 projected=0; principal_spending_report_required=False; _includes_compensation_paid_to_lobbyists=False |
| OH | IND_207 | enforcement_and_audits | 100 | 50 | no | Trend 5 (same shape as WI): extracted MODERATE vs oracle YES |
| CA | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| CA | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| CA | IND_199 | registration_mechanics_and_exemptions | 50 | 50 | YES | match (IntCell 24mo → MODERATE post-fix) |
| CA | IND_201 | lobbyist_spending_report | 100 | 0 | no | oracle=100 projected=0; all 3 inputs value_unstable |
| CA | IND_203 | principal_spending_report | 100 | 100 | YES | match |
| CA | IND_207 | enforcement_and_audits | 100 | 0 | no | Trend 5: extracted "NO" vs oracle YES. Audit script's vocab-mismatch warning is stale (helper now accepts "NO" directly). |
| TX | IND_196 | lobbying_definitions | 100 | 100 | YES | match |
| TX | IND_197 | registration_thresholds | 50 | 50 | YES | match |
| TX | IND_199 | registration_mechanics_and_exemptions | 0 | 100 | no | post-fix: IntCell 12mo → YES (100); oracle = 0 (Excel "100" artifact normalized to NO). Pre-fix the helper accidentally returned 0 (string-mismatch fallback), masking the underlying disagreement. |
| TX | IND_201 | lobbyist_spending_report | 50 | 100 | no | oracle=50 projected=100; Trend 4 sparse-corpus over-projection |
| TX | IND_203 | principal_spending_report | 0 | 0 | YES | match |
| TX | IND_207 | enforcement_and_audits | 50 | 0 | no | Trend 5 variant: extracted "NO" vs oracle MODERATE |

---

## Table B — per-state summary (post-fix)

| State | Indicators matched | Dispatches | Instantiation errors | Total cost (USD) |
|---|---|---|---|---|
| NY | **6 / 6** | 36 | 2 | $2.8289 |
| WI | 4 / 6 | 36 | 6 | $2.4825 |
| OH | 2 / 6 | 36 | 0 | $3.7894 |
| CA | 3 / 6 | 36 | 1 | $2.8428 |
| TX | 3 / 6 | 36 | 3 | $2.4835 |

Total: **19 / 30**, Round 1 cost unchanged at $14.4271.

---

## Interpretation

**What the +4 confirms:**
- The failure-mode doc's Trend 1 (YAML extraction vocab ≠ projection helper vocab) was a precise, mechanical diagnosis. Predicted +4 cells; observed +4 cells.
- IntCell 24 months for `lobbyist_registration_renewal_cadence` IS the right Phase A extraction — the schism was helper-side.
- CPI's "YES"/"MODERATE"/"NO" vocabulary at YAML extraction time IS the right vocabulary — same conclusion.

**What the remaining 11 misses are (post-Trend-1):**
- **3 cells (IND_197 WI, OH; IND_207 TX MODERATE-vs-NO)** — Trend 5 (CPI more generous than extraction). The helper now correctly maps the extracted values; the disagreement is between the extracted statute-literal reading and CPI's interpretive convention.
- **2 cells (IND_201 OH, CA)** — Trend 2 (compound-cell instability). Unaffected by Phase 1.
- **1 cell (IND_203 OH)** — value_unstable on principal_spending_report_required=False vs oracle 50. Unaffected by Phase 1.
- **2 cells (IND_201 TX, IND_199 TX)** — Trend 4 (TX sparse-corpus over-projection / oracle-artifact). The TX IND_199 case is now correctly reported as a mismatch (was masking pre-fix).
- **3 cells (IND_207 WI, OH, CA YES/MODERATE/NO-vs-YES)** — Trend 5 again. The audit script's "vocab-mismatch" warning column is stale; the helper post-fix maps these correctly; the residual is CPI-interpretive disagreement.

**Reporter-side staleness:** the audit script (`scripts/cross_state_cpi_2015_audit.py`) prints "vocab-mismatch: extracted EnumCell='MODERATE' but helper expects {regular_third_party_audit_required, ...}" for the IND_207 cells. As of commit `cbcd3e2` the helper now ALSO accepts "MODERATE", so this warning is misleading. The mismatches are real (projected 50, oracle 100) but the diagnosis is Trend 5, not vocab schism. Reporter update flagged for a future audit-script tweak.

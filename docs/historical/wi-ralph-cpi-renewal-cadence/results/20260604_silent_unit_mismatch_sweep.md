<!-- Generated during: convos/20260604_phase_b_silent_unit_mismatch_sweep.md -->

# Silent Unit-Mismatch Sweep — WI 2025 wide-pass JSONs vs CPI 2015 oracle

**Plan:** [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md)  
**Convo:** [`../convos/20260604_phase_b_silent_unit_mismatch_sweep.md`](../convos/20260604_phase_b_silent_unit_mismatch_sweep.md)  
**Script:** [`../../../scripts/silent_unit_mismatch_sweep.py`](../../../../scripts/silent_unit_mismatch_sweep.py)  
**Follow-on iter 5 (Step 5 fix on the IND_197 MISMATCH):** [`20260604_compensation_threshold_iter5.md`](20260604_compensation_threshold_iter5.md) — confirmed silent-unit-mismatch fixed (GPT 2/3 → 0/3 emitting `'0.5'`; 6/6 converge on `'0'`); plus 3 chunk-mate spillover findings.  

## Summary

Sweep over 20 (compendium row × CPI indicator) pairs, derived from 21 CPI-2015-readable rows and 14 CPI indicators (IND_196..IND_209).

Classification counts (top-level):

- **MISMATCH** — 2
- **COMPOUND_ROLE** — 7
- **NOT_EMITTED** — 10
- **MATCH** — 1

Cell emission notation: each `Claude r1/r2/r3` cell shows the emitted value for each of the 3 runs; `∅` means not emitted, `FAIL:X` means instantiation failed with attempted value `X`.

## Full classification table

| Compendium row | Cell type | Axis | CPI IND | WI oracle | Claude r1/r2/r3 | GPT r1/r2/r3 | Classification | Notes |
|---|---|---|---|---|---|---|---|---|
| `lobbyist_registration_threshold_compensation_dollars` | typed Optional[Decimal] | legal | IND_197 | MODERATE | '0' / '0' / '0' | '0.5' / '0' / '0.5' | MISMATCH (4/6) | WI oracle = MODERATE; match=2/6 mismatch=4/6 failed=0/6 not_emitted=0/6 |
| `lobbying_disclosure_audit_required_in_law` | enum (legal) + typed int 0-100 step 25 (practical) | legal | IND_207 | YES | 'MODERATE' / 'MODERATE' / 'MODERATE' | 'MODERATE' / 'MODERATE' / 'MODERATE' | MISMATCH (6/6) | WI oracle = YES; match=0/6 mismatch=6/6 failed=0/6 not_emitted=0/6 |
| `def_target_governors_office` | binary | legal | IND_196 | YES | True / True / True | True / True / True | COMPOUND_ROLE | IND_196 is compound (reads 2 rows: def_target_legislative_branch, def_target_governors_office). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = YES. Composite projections per run: (claude-o/r1: YES — leg=True AND gov=True), (claude-o/r2: YES — leg=True AND gov=True), (claude-o/r3: YES — leg=True AND gov=True), (gpt-5.2-/r1: YES — leg=True AND gov=True), (gpt-5.2-/r2: YES — leg=True AND gov=True), (gpt-5.2-/r3: YES — leg=True AND gov=True) |
| `def_target_legislative_branch` | binary | legal | IND_196 | YES | True / True / True | True / True / True | COMPOUND_ROLE | IND_196 is compound (reads 2 rows: def_target_legislative_branch, def_target_governors_office). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = YES. Composite projections per run: (claude-o/r1: YES — leg=True AND gov=True), (claude-o/r2: YES — leg=True AND gov=True), (claude-o/r3: YES — leg=True AND gov=True), (gpt-5.2-/r1: YES — leg=True AND gov=True), (gpt-5.2-/r2: YES — leg=True AND gov=True), (gpt-5.2-/r3: YES — leg=True AND gov=True) |
| `lobbyist_spending_report_includes_itemized_expenses` | binary | legal | IND_201 | NO | False / False / False | False / False / False | COMPOUND_ROLE | IND_201 is compound (reads 3 rows: lobbyist_spending_report_required, lobbyist_spending_report_includes_itemized_expenses, lobbyist_spending_report_includes_total_compensation). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = NO. Composite projections per run: (claude-o/r1: NO — req=False → NO), (claude-o/r2: NO — req=False → NO), (claude-o/r3: NO — req=False → NO), (gpt-5.2-/r1: NO — req=False → NO), (gpt-5.2-/r2: NO — req=False → NO), (gpt-5.2-/r3: NO — req=False → NO) |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | IND_201 | NO | False / False / False | False / False / False | COMPOUND_ROLE | IND_201 is compound (reads 3 rows: lobbyist_spending_report_required, lobbyist_spending_report_includes_itemized_expenses, lobbyist_spending_report_includes_total_compensation). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = NO. Composite projections per run: (claude-o/r1: NO — req=False → NO), (claude-o/r2: NO — req=False → NO), (claude-o/r3: NO — req=False → NO), (gpt-5.2-/r1: NO — req=False → NO), (gpt-5.2-/r2: NO — req=False → NO), (gpt-5.2-/r3: NO — req=False → NO) |
| `lobbyist_spending_report_required` | binary | legal | IND_201 | NO | False / False / False | False / False / False | COMPOUND_ROLE | IND_201 is compound (reads 3 rows: lobbyist_spending_report_required, lobbyist_spending_report_includes_itemized_expenses, lobbyist_spending_report_includes_total_compensation). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = NO. Composite projections per run: (claude-o/r1: NO — req=False → NO), (claude-o/r2: NO — req=False → NO), (claude-o/r3: NO — req=False → NO), (gpt-5.2-/r1: NO — req=False → NO), (gpt-5.2-/r2: NO — req=False → NO), (gpt-5.2-/r3: NO — req=False → NO) |
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | binary | legal | IND_203 | YES | True / True / True | True / True / True | COMPOUND_ROLE | IND_203 is compound (reads 2 rows: principal_spending_report_required, principal_spending_report_includes_compensation_paid_to_lobbyists). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = YES. Composite projections per run: (claude-o/r1: YES — req AND comp → YES), (claude-o/r2: YES — req AND comp → YES), (claude-o/r3: YES — req AND comp → YES), (gpt-5.2-/r1: YES — req AND comp → YES), (gpt-5.2-/r2: YES — req AND comp → YES), (gpt-5.2-/r3: YES — req AND comp → YES) |
| `principal_spending_report_required` | binary | legal | IND_203 | YES | True / True / True | True / True / True | COMPOUND_ROLE | IND_203 is compound (reads 2 rows: principal_spending_report_required, principal_spending_report_includes_compensation_paid_to_lobbyists). composite: match=6/6 mismatch=0/6 unprojectable=0/6. WI oracle = YES. Composite projections per run: (claude-o/r1: YES — req AND comp → YES), (claude-o/r2: YES — req AND comp → YES), (claude-o/r3: YES — req AND comp → YES), (gpt-5.2-/r1: YES — req AND comp → YES), (gpt-5.2-/r2: YES — req AND comp → YES), (gpt-5.2-/r3: YES — req AND comp → YES) |
| `lobbyist_registration_required` | binary (legal) + typed int 0-100 step 25 (practical) | practical | IND_198 | 50 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_198 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbyist_registration_deadline_days_after_first_lobbying` | typed int (legal) + typed int 0-100 step 25 (practical) | practical | IND_200 | 50 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_200 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbyist_spending_report_filing_cadence` | enum (legal) + typed int 0-100 step 25 (practical) | practical | IND_202 | 0 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_202 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | binary | practical | IND_204 | 50 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_204 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_disclosure_documents_free_to_access` | binary | practical | IND_205 | 100 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_205 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_disclosure_documents_online` | binary | practical | IND_205 | 100 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_205 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_disclosure_offline_request_response_time_days` | typed int (practical) | practical | IND_205 | 100 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_205 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_data_open_data_quality` | typed int 0-100 step 25 (practical) | practical | IND_206 | 25 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_206 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_disclosure_audit_required_in_law` | enum (legal) + typed int 0-100 step 25 (practical) | practical | IND_208 | 25 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_208 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbying_violation_penalties_imposed_in_practice` | binary (legal) + typed int 0-100 step 25 (practical) | practical | IND_209 | 50 | ∅ / ∅ / ∅ | ∅ / ∅ / ∅ | NOT_EMITTED (axis=practical) | IND_209 reads only the practical axis. Legal-axis dispatch did not extract this cell; cannot compare. |
| `lobbyist_registration_renewal_cadence` | typed Optional[int_months] (or enum) | legal | IND_199 | MODERATE | 24 / 24 / 24 | 24 / 24 / 24 | MATCH | WI oracle = MODERATE; match=6/6 mismatch=0/6 failed=0/6 not_emitted=0/6 |

---

## Findings

Pre-execution prediction (iter 3+4 wrap-up): the sweep would surface 0–17 silent unit-mismatch instances on the CPI-readable rows the wide-pass audit cleared as "no problem." Empirical result: **the wide-pass JSONs are CPI-projection-clean on 8 of 10 projectable indicators**, with the 2 MISMATCH rows both admitting concrete diagnoses.

### 1. The sweep is mostly clean — wide-pass JSONs project to WI oracle on 8 of 10 projectable indicators.

Of the 14 CPI indicators (IND_196–IND_209):
- **8 are practical-axis-only and not extracted by the legal-axis dispatch** (IND_198, IND_200, IND_202, IND_204, IND_205, IND_206, IND_208, IND_209). These map to 10 of the 20 pairs in the table (some indicators read multiple rows) — all classified `NOT_EMITTED (axis=practical)`. Expected per the plan's edge-case 1.
- **3 are compound legal indicators with clean composite projections** (IND_196: 2 rows; IND_201: 3 rows; IND_203: 2 rows). Composite projection per (model, run) matches the WI oracle **6/6** for all three indicators. No hidden mismatches inside the compound reads.
- **1 is single-row legal MATCH** (IND_199 `renewal_cadence`): 6/6 emit `24` projecting to MODERATE = WI oracle. (Reflects the iter 2 fix; the original wide-pass had the GPT-emits-`2` pattern surfaced in iter 0 inspection.)
- **2 are single-row legal MISMATCH** (IND_197 + IND_207). Both diagnosed below.

### 2. IND_197 MISMATCH — `lobbyist_registration_threshold_compensation_dollars`: a silent-unit-mismatch on the model side AND a probable CPI-oracle issue.

**Model behavior:**
- **Claude 3/3 emit `'0'` (string "0") at high confidence**, citing §13.62(11). Reads correctly: "any individual employed by a principal or who contracts for or receives economic consideration… with no dollar threshold." Projects under our v2-convention rule (`threshold == 0 → YES`) to YES.
- **GPT mixed: 1/3 emit `'0'`, 2/3 emit `'0.5'`** at high confidence, same §13.62(11) citation, same substantive reading ("no minimum compensation"). The `'0.5'` emission is **a clear instance of the silent unit-mismatch class**: GPT is emitting a CPI tier score (50/100 → 0.5) into a DecimalCell typed `Optional[Decimal]` representing dollar amount. Justification text describes the substantive law correctly; the *numeric encoding* is on the wrong axis (CPI rubric tier rather than dollar value).

**WI oracle vs reading:**
- CPI 2015 WI oracle = MODERATE. Models' reading (Claude unanimously; GPT in justification) = threshold == 0 → YES.
- Per the projection mapping doc's scoring rule for IND_197 (*"A YES score is earned if anyone paid any amount to carry out lobbying activity is defined as a lobbyist… A MODERATE score is earned if only persons being paid more than a certain threshold are defined as a lobbyist"*), Claude's reading of §13.62(11) is unambiguously YES.
- CPI 2015 may have mis-coded WI by conflating the principal-side $500 expenditure de-minimis (§13.621) with a *lobbyist* compensation threshold. That is, CPI's source-doc reader saw "$500" near "lobbying" and rated it MODERATE. This is consistent with the projection-mapping doc's §"Open issues" footnote on 6 / 700 CPI cell-level data-quality glitches; IND_197 wasn't on the catalogued list, but the failure mode is the same shape.

**Two distinct findings packaged together:**
- *(a) Silent unit-mismatch confirmed in the broader sweep* — GPT emits CPI tier score `'0.5'` into a DecimalCell on this row in 2/3 runs. Matches the failure class the sweep was designed to find. Cell type is the row where the wide-pass Commit 3 audit was particularly anchored on instantiation-only failures; DecimalCell-non-negative didn't surface in the catalog.
- *(b) Probable CPI 2015 WI-oracle mis-code* — Claude's unanimous reading of WI §13.62(11) is substantively correct; CPI's MODERATE rating is plausibly an error. Same pattern as IND_207 (next finding) and as iter 3 convo's pre-flagged candidate.

### 3. IND_207 MISMATCH — `lobbying_disclosure_audit_required_in_law`: pure CPI-oracle-vs-statute-interpretation disagreement.

All 6 runs emit `'MODERATE'`. Claude cites §13.74(1) + §13.685(3); GPT cites §13.74(1)-(2). Both read the Ethics Commission's mandatory examination-of-all-filings as **compliance-review-by-the-regulator-itself**, NOT independent-third-party-audit. Per the projection mapping doc's enum: `audit_only_when_irregularities_suspected_or_compliance_review → MODERATE`. CPI WI = YES (requires regular third-party audit).

The Ethics Commission IS the regulator (not a third party), so the models' MODERATE reading is legally accurate. This is the *exact* candidate the iter 3 convo §"Open questions" pre-flagged ("WI's CPI 2015 oracle is YES — models cite §13.74(1) examination requirement and conclude MODERATE; plausibly models are right and CPI 2015 is stale/differently-interpreted").

**No silent unit-mismatch here.** The cell type (EnumCell) is right, the prompt is asking the right question, the models converge unanimously, and the projection rule applies cleanly. The MISMATCH is purely substantive: CPI's "YES" for WI on IND_207 is questionable.

### 4. GPT's `'0.5'` on IND_197 is the only confirmed silent-unit-mismatch beyond the iter 0 `renewal_cadence` GPT-emits-`2` case.

The sweep was motivated by the question: are there *other* CPI-readable rows where GPT (or Claude) emits a CPI-tier-score-as-cell-value? Empirical answer for WI 2025: **yes, exactly one — GPT's `'0.5'` on IND_197**. The instance is real, but the prevalence is much lower than feared (1 of 20 pairs, not 5+).

This bounds Phase A scope substantially: silent-mismatch is real but rare. The Phase A pre-flight audit can target the additive cell-type-aligned instruction on this single confirmed case, and the broader pattern (DecimalCell-non-negative still to be validated end-to-end) carries forward via candidate (a').

### 5. Compound-projection composite read confirms the 3 multi-row indicators are all 6/6 on WI oracle.

IND_196 (2-row AND): composite = YES, 6/6. WI oracle = YES. ✓
IND_201 (3-row compound): composite = NO, 6/6 (because `report_required=False` for all runs — WI requires *principal*, not lobbyist, to file). WI oracle = NO. ✓
IND_203 (2-row compound): composite = YES, 6/6 (req AND comp). WI oracle = YES. ✓

This is the answer to the plan's edge-case 2 ("CPI indicators reading multiple compendium rows… flag as AMBIGUOUS rather than force a single-row attribution"). Per-row attribution remains AMBIGUOUS as the plan said; but the composite projection is clean, so the multi-row indicators don't hide any silent issues either.

### 6. The wide-pass JSONs are trustworthy on the 17 cleared rows — Phase A focus is the 4 known wide-pass-failure rows, with `lobbyist_registration_threshold_compensation_dollars` joining as a 5th (newly surfaced by the sweep).

Of the 21 CPI-readable rows: 17 cleared the wide-pass audit; 4 were known failures (IntCell `renewal_cadence`, EnumCell `filing_cadence`, DecimalCell `de_minimis_threshold_dollars`, BinaryCell `penalties_imposed_in_practice`). The sweep's MISMATCH on IND_197 adds `lobbyist_registration_threshold_compensation_dollars` (DecimalCell-Optional) to the Phase A target list as a 5th confirmed-by-sweep candidate. The other 16 cleared rows hold up against CPI projection.

---

## Recommendations

1. **Phase A pre-flight YAML audit's target list now stands at 5 rows**, not 4:
   - `lobbyist_registration_renewal_cadence` (IntCell) — already fixed by iter 1+2.
   - `lobbyist_spending_report_filing_cadence` (EnumCell, split-axis with practical-only CPI source) — already fixed by iter 3+4.
   - `lobbyist_filing_itemization_de_minimis_threshold_dollars` (DecimalCell-non-negative) — wide-pass failure, candidate (a') target. **Not in the sweep's 21-row list because it's not CPI-readable** — but per the iter 3+4 convo it carries the `-1` sentinel pattern (Claude emitting a negative-as-sentinel into a non-negative DecimalCell).
   - `lobbying_violation_penalties_imposed_in_practice` (BinaryCell) — wide-pass failure, candidate (a') target. Also carries the known Pattern C v2.2 row-axis bug.
   - **`lobbyist_registration_threshold_compensation_dollars` (DecimalCell `Optional[Decimal]`)** — newly added by this sweep. GPT 2/3 emitted CPI tier value `'0.5'` rather than dollar amount. Pattern: append "Answer the dollar threshold; emit `0` if no threshold (anyone paid is a lobbyist); emit `null` if no statute defines a compensation standard."

2. **The DecimalCell additive fix is the natural next single-row test.** Combined with the candidate-(a') BinaryCell row, this gives ~$0.60-1.50 to close the 4-cell-type matrix AND validate the GPT-`0.5`-on-IND_197 fix in one chunk re-dispatch (`registration_thresholds` chunk for IND_197; `enforcement_and_audits` for BinaryCell; the de minimis row's home chunk needs lookup).

3. **Treat IND_197 and IND_207 CPI MISMATCHes as oracle-issues, not model-issues.** Document both in the projection-mapping doc's §"Open issues" data-quality-glitches footnote as 5th and 6th candidate WI-row CPI 2015 errata. The model reads of WI §13.62(11) and §13.74(1) are substantively defensible; CPI's 2015 ratings (MODERATE on IND_197 and YES on IND_207) appear to misclassify these.

4. **Sweep complete; Step 5 follow-on (re-dispatch) IS recommended, scoped to the new IND_197 finding.** A single re-dispatch of `registration_thresholds` chunk (~$0.74 by the iter 3+4 cost model on the comparable chunk size) with an additive DecimalCell-Optional-aligned actionable question would test the silent unit-mismatch fix on the IND_197 row. Combine with the candidate-(a') DecimalCell/BinaryCell rows for combined Phase A wave-1 dispatch. **Per-Dan budget approval needed before dispatch.** Cumulative wi-ralph after Step 5 would be ~$2.81–3.55 (still within the $3–5 ceiling).

5. **The sweep methodology validates two ways**: (a) reproduces the IND_199 MATCH cleanly on the iter-2-fixed JSONs (renewal_cadence now `24` → MODERATE matches WI = MODERATE); (b) catches the GPT-emits-`'0.5'` silent-mismatch on IND_197 that the wide-pass Commit 3 audit missed (the audit's instantiation-only frame was insufficient for the silent-unit-mismatch class, as predicted by the plan).

6. **A v2-convention-vs-CPI-semantic-projection distinction was NOT needed in this sweep.** The plan's edge case 6 worried about the GPT-emits-`2` case (where literal-value projection might mis-flag a CPI-tier-equivalent value as MISMATCH). In the current top-level JSONs (post-iter-2), all `renewal_cadence` emissions are `24` in months — no ambiguity. The edge case remains relevant for *future* sweeps if the iter-2 fix is rolled back or if the same pattern surfaces on other rows; the script's projection logic still applies v2-convention literally and surfaces such cases as MISMATCH-with-explanation in the notes.

---

## Spend ledger

This sweep cost **$0.00** (pure analysis over existing data). Cumulative wi-ralph unchanged at **$2.0720**. Step 5 follow-on (if approved) projected at ~$0.74 per affected chunk dispatched.

| Phase | Cost | Cumulative wi-ralph | Cumulative WI Phase 1/2 + Phase B |
|---|---|---|---|
| Sweep (this session, core) | $0.00 | $2.0720 | $9.3666 |
| Step 5 (Dan-gated) | ~$0.74 / chunk | TBD | TBD |

Budget: $3-5 wi-ralph ceiling; $0.93-$2.93 remaining; Step 5 + candidate-(a') combined ~$1.5–2.2 sits comfortably under the ceiling.


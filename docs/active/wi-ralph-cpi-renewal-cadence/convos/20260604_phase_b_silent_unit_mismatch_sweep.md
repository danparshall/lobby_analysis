# Phase B Ralph — silent unit-mismatch sweep on the 21 CPI-readable rows + iter 5 fix on IND_197

**Date:** 2026-06-04 (later evening, immediately after iter 3+4 on `filing_cadence`)
**Branch:** wi-ralph-cpi-renewal-cadence
**Plan:** [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md) (drafted in iter 1+2; this session executed it + the Step 5 follow-on)
**Sweep script:** [`../../../scripts/silent_unit_mismatch_sweep.py`](../../../../scripts/silent_unit_mismatch_sweep.py)
**Sweep results:** [`../results/20260604_silent_unit_mismatch_sweep.md`](../results/20260604_silent_unit_mismatch_sweep.md)
**Iter 5 results:** [`../results/20260604_compensation_threshold_iter5.md`](../results/20260604_compensation_threshold_iter5.md)
**Predecessor convo:** [`20260604_phase_b_iter_3_filing_cadence.md`](20260604_phase_b_iter_3_filing_cadence.md)

## Summary

Picked up the (a')/(b)/(c) decision from the iter 3+4 handoff and chose (b) — the silent unit-mismatch sweep against existing wide-pass JSONs. Wrote `scripts/silent_unit_mismatch_sweep.py` (~470 lines, stdlib-only Python) to enumerate 21 CPI-2015-readable compendium rows from the v2 TSV, load WI's CPI 2015 per-state oracle (700-cell archive), and classify each (compendium row × CPI indicator) pair as MATCH / MISMATCH / INSTANTIATION_FAILED / NOT_EMITTED / COMPOUND_ROLE / AMBIGUOUS. Sweep classifies 20 pairs total (3 indicators read multiple rows; 1 row read by 2 indicators). $0 API cost for the analysis.

**Sweep findings:** 10 NOT_EMITTED (practical-axis-only IND, expected); 7 COMPOUND_ROLE with all 6/6 composite MATCH on multi-row legal indicators (IND_196, IND_201, IND_203); 1 single-row MATCH (IND_199 `renewal_cadence` post-iter-2); **2 MISMATCH** (IND_197 `compensation_threshold` and IND_207 `audit_required_in_law`). Both MISMATCH cases admitted clean diagnoses — IND_197 is a both/and finding (GPT 2/3 silent-unit-mismatch `'0.5'` as decimal value AND probable CPI oracle errata on WI), IND_207 is pure CPI-oracle-vs-statute-interpretation disagreement (already pre-flagged in iter 3 convo).

After surfacing findings, Dan picked option 2 (run Step 5 dispatch on IND_197 only). Iter 5 added an additive DecimalCell-Optional actionable question to the YAML prompt, dispatched the 6-row `registration_thresholds` chunk ($0.2853). **Result: GPT shifted 2/3 → 0/3 emitting `'0.5'`; 6/6 converge on `'0'` at high confidence citing §13.62(11)** — silent-unit-mismatch fixed cleanly. **Three unexpected chunk-mate spillovers, all substantively positive:** Claude's `-1` sentinel pattern on the candidate-(a') `de_minimis_threshold` row eliminated; GPT's anomalous `'1'` outlier on `de_minimis_dollars` fixed (5/6 → 6/6 on `'500'`); Claude 3/3 swung `'0'` → `null` on `expenditure_threshold` (plausibly more correct — WI has no lobbyist-side expenditure standard).

The 4-cell-type matrix now reads: IntCell ✓ (iter 1+2), EnumCell ✓ (iter 3+4), DecimalCell `Optional[Decimal]` ✓ (iter 5), DecimalCell-non-negative partially ✓ via spillover (instantiation-failure mode fixed; value-stability not reached), BinaryCell still untested. Cumulative wi-ralph **$2.3573** of $3-5 budget; remaining $0.64-$2.64.

## Topics Explored

### 1. Sweep methodology design + script (~470 lines)

Pre-flight reads against the CPI 2015 C11 projection mapping doc, the CPI 700-cell per-state oracle CSV, the v2 compendium TSV, and a sample wide-pass JSON. Confirmed:
- 21 cpi_2015-readable rows in the TSV (`rubrics_reading` contains `cpi_2015`).
- WI rows in the oracle CSV cover all 14 IND_xxx indicators (IND_196..IND_209).
- JSON shape: `instantiated_cells[]` with `cell.cell_id = [row_id, axis]` + `cell.value`; `errors[]` with `reason: instantiation_failed` + `key: [row_id, axis]` + `arguments.value` (the attempted emission).
- Working-name → TSV-name mapping for 2 renames (`compensation_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_compensation_dollars`; `lobbyist_spending_report_includes_compensation` → `lobbyist_spending_report_includes_total_compensation`).

Script enumerates indicators, projects emitted values per indicator's hard-coded scoring rule (extracted from the projection mapping doc's §"Per-item mappings"), compares to WI oracle, classifies. Compound indicators (IND_196 2-row, IND_201 3-row, IND_203 2-row) get both a per-row `COMPOUND_ROLE` classification and a composite projection summary in the notes column. Practical-axis-only indicators (IND_198, IND_200, IND_202, IND_204, IND_205, IND_206, IND_208, IND_209) get `NOT_EMITTED (axis=practical)` since the legal-axis dispatch can't reach them.

Ruff clean. Output: `results/20260604_silent_unit_mismatch_sweep.md` (table + findings + recommendations).

### 2. Sweep results — clean on 8 of 10 projectable indicators

Wide-pass JSONs project to WI oracle cleanly on 8 of 10 indicators we can project (10 of 14 — minus the 4 IND that are exclusively practical-axis 5-tier). The 3 compound legal indicators (IND_196, IND_201, IND_203) all composite-project 6/6 to WI oracle. The single-row legal MATCH is IND_199 `renewal_cadence` (post-iter-2; GPT-emits-`2` fixed). The 2 MISMATCHes are IND_197 and IND_207.

### 3. Hand spot-check of MISMATCH source JSONs (`/tmp/inspect_mismatches.py`)

Confirmed iter 197's failure mode is dual: Claude reads correctly and emits `'0'`; GPT reads correctly per justification ("no minimum compensation," "no dollar minimum stated") but encodes the value as CPI tier score `'0.5'`. Confirmed iter 207's failure mode is uniform: 6/6 emit `'MODERATE'` citing §13.74(1) + §13.685(3) (Ethics Commission compliance review) — substantively correct per the statute; CPI's YES rating is the disagreement, not the model emission.

### 4. Surfaced findings + (a')/(b)/(c) re-decision to Dan

Presented sweep findings cleanly: 16/17 cleared CPI-readable rows trustworthy; IND_197 newly added to Phase A target list; IND_197 + IND_207 both candidate WI-row CPI 2015 errata. Asked: finish-convo here, run Step 5 on IND_197 only, run combined Step 5 + (a') wave, or pause to discuss.

Dan picked Step 5 on IND_197 only. Reading: keep scope tight; validate the additive DecimalCell-Optional pattern on the sweep-surfaced row; defer BinaryCell + DecimalCell-non-negative validation to a future session.

### 5. Iter 5 dispatch + audit

YAML prompt edited for `lobbyist_registration_threshold_compensation_dollars` — CPI source quote preserved at front; appended actionable DecimalCell-Optional question with concrete null-case parenthetical ("e.g., the statute defines a lobbyist as anyone receiving 'any economic consideration' to lobby"). 6 pre-iter5 JSONs archived to `_pre_iter5_compensation_threshold/`. Dispatched `python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --chunks registration_thresholds` via `/tmp/dispatch_iter5.py` Python wrapper (needed to load `.env.local` for API keys). $0.2853 cost.

Audit via `/tmp/audit_iter5.py` showed:
- **Target row:** 6/6 → `'0'` at high confidence. GPT 2/3 `'0.5'` → 0/3. Silent unit-mismatch fixed.
- **Chunk-mate spillover** on 3 other rows (de_minimis sentinel pattern fixed; GPT outlier fixed; expenditure threshold Claude `'0'` → `null` shift).
- **Pre-existing time_percent failure** persists (6/6 FAIL with compound `{magnitude: 5, unit: 'days_per_reporting_period'}` structure — different failure class).

### 6. Concrete null-case examples appear to carry interpretive weight

The iter 5 prompt's parenthetical example ("e.g., the statute defines a lobbyist as anyone receiving 'any economic consideration' to lobby") matched WI §13.62(11)'s exact phrasing. Both models reproduced this phrasing in their justifications. Suggests Phase A pre-flight scope should consider whether concrete null-case examples (not just abstract rule statements) improve convergence.

## Provisional Findings

- **The additive cell-type-aligned-instruction pattern is now confirmed across 3 cell types** (IntCell, EnumCell, DecimalCell-Optional), all on statute-derived oracle values. The fourth cell type (BinaryCell) remains untested; the candidate row carries an entangled Pattern C v2.2 row-axis bug.

- **DecimalCell-non-negative is partially confirmed via chunk-mate spillover.** Claude's `-1` sentinel pattern on `lobbyist_filing_itemization_de_minimis_threshold_dollars` (the dedicated (a') candidate row) eliminated as a side effect of the IND_197 prompt edit. Value-stability not reached; a dedicated prompt edit would close that half.

- **Chunk-mate spillover is bigger than the prior iterations made visible.** Three substantive shifts on chunk-mate rows from a single YAML edit. The additive instruction's effect propagates through in-context priming, not just the single-row prompt. Phase A's design needs to plan for this — could be a feature (one edit covers analogous chunk-mate rows) or a constraint (need to verify chunk-mate rows weren't dragged wrong).

- **The sweep methodology validates two ways**: (a) reproduces the iter-2-fixed `renewal_cadence` MATCH cleanly; (b) catches the GPT `'0.5'` silent-unit-mismatch on IND_197 that the wide-pass Commit 3 audit missed. Iter 5's fix confirms the MISMATCH classification was actionable, not an oracle artifact.

- **Two CPI 2015 WI-row errata candidates surface from this session.** IND_197 (CPI = MODERATE but model reading = YES per §13.62(11)) and IND_207 (CPI = YES but model reading = MODERATE per §13.74(1) + §13.685(3) being regulator self-review, not impartial third-party). Both join the projection mapping doc's existing §"Open issues" 4-6 cell data-quality glitches footnote as candidate additions.

- **The wide-pass JSONs are trustworthy on 15 of 17 cleared CPI-readable rows.** Sweep originally flagged IND_197 as the only new silent-mismatch; iter 5's spillover suggests `expenditure_threshold` may also have been silently mis-emitted (Claude `'0'` plausibly wrong, swung to `null` post-spillover). 15/17 still passes the bar; the sweep methodology continues to catch real issues without generating false alarms.

- **Per-iteration cost on the 6-cell `registration_thresholds` chunk: $0.2853** (~$0.05 per cell per model per run). Comparable to iter 1+2's $0.29 on the 8-cell `registration_mechanics_and_exemptions` chunk; both substantially cheaper than iter 3+4's $0.74 on the 30-cell `lobbyist_spending_report` chunk. Per-cell cost is the right unit for budgeting.

## Decisions Made

- **The additive cell-type-aligned-instruction pattern is the load-bearing Phase A fix shape** across 3 confirmed cell types. Documented in iter 5 results doc §Findings 1 and §Recommendations 5. Concrete templates per cell type:
  - IntCell → "Answer in [unit] as an integer (e.g., 12 for annual). If [absence case], return null." [iter 2]
  - EnumCell → "Answer with one of: [members]. Use '[null member]' if [absence case]." [iter 4]
  - DecimalCell `Optional[Decimal]` → "Answer with the [unit] as a non-negative decimal (e.g., 500 for $500). Use 0 if [zero case]. Use null if no statute defines [the standard]." [iter 5]

- **Production YAML for `lobbyist_registration_threshold_compensation_dollars` holds iter 5's prompt.** Same posture as iter 2 (renewal_cadence) and iter 4 (filing_cadence) — provenance preserved, actionable question appended.

- **No retroactive correction of the wide-pass Commit 3 audit's narrative.** Same posture as iters 1+2 and 3+4. The sweep results doc + iter 5 results doc preserve the refined reading; the original audit narrative stands as historical record.

- **Two new CPI 2015 WI-row errata candidates documented**, joining IND_207 from iter 3 convo:
  - IND_197 (compensation_threshold = MODERATE per CPI; YES per model + §13.62(11) reading).
  - IND_207 (audit_required = YES per CPI; MODERATE per model + §13.74(1) + §13.685(3) reading).
  Tracked in sweep results doc §Findings 2 + 3 and iter 5 results doc §Findings 6. Future projection mapping doc footnote update is a low-priority cleanup task.

- **STATUS.md, RESEARCH_LOG.md, sweep + iter 5 results + this convo will be committed in this session's finish-convo.**

- **Phase B continues.** Next-session candidates:
  - (i) Test BinaryCell additive pattern on `lobbying_violation_penalties_imposed_in_practice` (chunk = `enforcement_and_audits`, ~$0.30) — BUT this row carries Pattern C v2.2 row-axis bug; a row-axis fix may be a prerequisite. Worth a brainstorm to scope first.
  - (ii) Value-stability test on `lobbyist_filing_itemization_de_minimis_threshold_dollars` ($200 vs $500 ambiguity needs disambiguating prompt; sentinel pattern already fixed by spillover; ~$0.30).
  - (iii) Chunk-mate spillover investigation — how does prompt edit on one row propagate? Mechanism matters for Phase A design.
  - (iv) Phase A pre-flight YAML audit at scale (candidate (c)) — now well-defined: 3 cell-type templates + chunk-mate spillover as known design constraint + 5 known target rows + 16 sweep-cleared rows.

## Results

- **Sweep script:** [`../../../scripts/silent_unit_mismatch_sweep.py`](../../../../scripts/silent_unit_mismatch_sweep.py) (~470 lines, ruff clean)
- **Sweep results doc:** [`../results/20260604_silent_unit_mismatch_sweep.md`](../results/20260604_silent_unit_mismatch_sweep.md) — full classification table for 20 (row × indicator) pairs + 6 findings sections + 6 recommendations
- **Iter 5 results doc:** [`../results/20260604_compensation_threshold_iter5.md`](../results/20260604_compensation_threshold_iter5.md) — per (model, run) before/after table + 3 spillover findings + 6 recommendations + cell-type template summary
- **YAML edit:** `compendium/source_quotes.yaml` — `lobbyist_registration_threshold_compensation_dollars.prompt` updated to iter 5's additive DecimalCell-Optional pattern
- **JSONs (preserved):**
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter5_compensation_threshold/` — 6 pre-iter-5 wide-pass JSONs
  - `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*__registration_thresholds__run*.json` — 6 iter 5 JSONs (current)
- **Spend ledger:** Iter 5 $0.2853. wi-ralph cumulative **$2.3573** (against $3-5 ceiling). wi-tier1 unchanged at $7.2946. Grand total WI Phase 1/2 + Phase B: **$9.6519**.

## Open Questions

- **Does the additive pattern hold for BinaryCell?** Untested; candidate row carries Pattern C v2.2 row-axis bug entangling the test. Brainstorm scope first.

- **How does chunk-mate spillover propagate mechanistically?** Iter 5 surfaced 3 substantive chunk-mate shifts from a single YAML edit. Is it (a) in-context learning from the analogous appended-question structure, (b) general improvement of model-of-state from clearer one-row reading, (c) other? Mechanism informs whether Phase A can deliberately leverage spillover.

- **Should the candidate-(a') value-stability test on `lobbyist_filing_itemization_de_minimis_threshold_dollars` be combined with the BinaryCell test?** Both are remaining open-ended tests; one chunk per row; $0.30 each.

- **What's the formal write-up posture for CPI 2015 WI-row errata?** Currently tracked across multiple results docs; eventually a projection-mapping-doc footnote update could consolidate. Low priority but visible.

- **`expenditure_threshold` row's `'0'` → `null` shift — substantively correct or oracle-confused?** Plausibly correct per the §13.621 principal-vs-lobbyist axis distinction; a sanity-check pass would close it. Could be folded into a Phase A pre-flight chunk-mate audit.

## Session meta — option (b) was the right call

In retrospect, choosing the sweep over (a') cell-type completion was the right move. The sweep:
- Was free ($0 API).
- Surfaced 1 silent-unit-mismatch instance (IND_197) that the wide-pass audit had missed, and 2 CPI-oracle-questionable rows.
- Bounded Phase A scope dramatically (16/17 cleared rows trustworthy; only 1 new target row added).
- Triggered iter 5, which incidentally validated the additive pattern on 2 more cell types (DecimalCell-Optional explicit; DecimalCell-non-negative via spillover) for $0.2853 — close to half the cost of a single-row dispatch on the 30-cell chunk.

The decision to extend with Step 5 (over finish-convo here) bought a 4th cell-type confirmation for the cost of one chunk dispatch. Worth doing immediately because the sweep result was fresh and the YAML edit was a 1-paragraph append.

The Phase B house style ("first iteration tests the intervention, second iteration runs the ablation") was NOT reproduced this session — iter 5 is a single confirmation dispatch without a paired ablation. Defensible: the additive pattern is already heavily ablation-validated on IntCell + EnumCell (iters 1-4); iter 5's role was direct sweep-finding fix, not pattern re-testing. A future ablation iter (e.g., strip iter 5's additive instruction and verify GPT-`0.5` returns) would close the loop formally if needed.

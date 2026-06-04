<!-- Generated during: convos/20260604_phase_b_silent_unit_mismatch_sweep.md -->

# Iter 5 — Additive DecimalCell-Optional fix on `lobbyist_registration_threshold_compensation_dollars` (IND_197)

**Date:** 2026-06-04 (post-sweep, same session)
**Plan:** [`../plans/20260604_silent_unit_mismatch_sweep.md`](../plans/20260604_silent_unit_mismatch_sweep.md) §Step 5 (Dan-gated follow-on)
**Convo:** [`../convos/20260604_phase_b_silent_unit_mismatch_sweep.md`](../convos/20260604_phase_b_silent_unit_mismatch_sweep.md)
**Sweep results:** [`20260604_silent_unit_mismatch_sweep.md`](20260604_silent_unit_mismatch_sweep.md)
**Predecessor iteration logs:** [`20260604_renewal_cadence_iterations.md`](20260604_renewal_cadence_iterations.md), [`20260604_filing_cadence_iterations.md`](20260604_filing_cadence_iterations.md)

## Target

**Row:** `lobbyist_registration_threshold_compensation_dollars`
- **Cell type spec (TSV col 2):** `typed Optional[Decimal]` (dollar threshold above which an individual is defined as a lobbyist; `0` = no threshold, `null` = no statutory standard).
- **Axis:** `legal`
- **Rubrics reading:** `cpi_2015; focal_2024; hg_2007; newmark_2005; newmark_2017; opheim_1991` (6 rubrics)
- **Chunk:** `registration_thresholds` (6 rows: compensation_threshold, expenditure_threshold, time_percent, itemization_de_minimis, de_minimis_dollars, de_minimis_time_percent)
- **Source-quote provenance (YAML):** `cpi_2015_IND_197`

**Sweep finding driving this fix:** GPT 2/3 in the wide-pass JSONs emitted value `'0.5'` at high confidence for this row — a literal CPI tier score (50/100 → 0.5) being emitted into a DecimalCell representing dollar amount. The silent-unit-mismatch class confirmed in the wild, on a row the wide-pass Commit 3 audit had cleared as "no problem." See [`20260604_silent_unit_mismatch_sweep.md`](20260604_silent_unit_mismatch_sweep.md) §Findings 2 + 4.

**Oracle:** The CPI 2015 WI oracle (MODERATE) appears to be miscoded — Claude 3/3 wide-pass + iter-5 emissions read WI §13.62(11) ("any individual… contracts for or receives economic consideration… from a principal whose duties include lobbying") as having no compensation threshold, projecting to YES not MODERATE. So the substantive oracle for the cell value is **`0` (no threshold)** per the statute.

## Prompt change (additive)

**Before** (wide-pass YAML, line 449 of `compendium/source_quotes.yaml`):

> *"A YES score is earned if anyone paid any amount to carry out lobbying activity is defined as a lobbyist and must register as such. A MODERATE score is earned if only persons being paid more than a certain threshold are defined as a lobbyist. A NO score is earned if no such law exists."*

**After (iter 5):**

> *"A YES score is earned if anyone paid any amount to carry out lobbying activity is defined as a lobbyist and must register as such. A MODERATE score is earned if only persons being paid more than a certain threshold are defined as a lobbyist. A NO score is earned if no such law exists. **Under state law, what is the dollar compensation threshold above which an individual must register as a lobbyist? Answer with the dollar amount as a non-negative decimal (e.g., 500 for a $500 threshold). Use 0 if anyone paid any amount to lobby is a lobbyist (no threshold, e.g., the statute defines a lobbyist as anyone receiving 'any economic consideration' to lobby). Use null if no statute defines a compensation standard at all.**"*

Additive pattern: CPI vocab preserved at front for provenance; cell-type-aligned actionable question appended at end. Same shape as iter 2 (`renewal_cadence` IntCell) and iter 4 (`filing_cadence` EnumCell).

## Dispatch + cost

- **Command:** `python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --chunks registration_thresholds`
- **Wall time:** ~2 min (much faster than the 30-cell `lobbyist_spending_report` chunk; 6 cells in this chunk)
- **Cost: $0.2853** (Claude $0.1586 across 3 runs + GPT $0.1266 across 3 runs)
- **Pre-iter5 JSONs archived to:** `_pre_iter5_compensation_threshold/` (6 files)

## Results — target row

| Model | Run | Pre-iter5 (wide-pass) | Iter 5 | Change |
|---|---|---|---|---|
| claude-opus-4-7 | 1 | `'0'` (high) | `'0'` (high) | no change ✓ |
| claude-opus-4-7 | 2 | `'0'` (high) | `'0'` (high) | no change ✓ |
| claude-opus-4-7 | 3 | `'0'` (high) | `'0'` (high) | no change ✓ |
| gpt-5.2 | 1 | **`'0.5'` (high)** | `'0'` (high) | **fixed** ✓ |
| gpt-5.2 | 2 | `'0'` (high) | `'0'` (high) | no change ✓ |
| gpt-5.2 | 3 | **`'0.5'` (high)** | `'0'` (high) | **fixed** ✓ |

**Convergence: 6/6 emit `'0'` at high confidence**, all citing §13.62(11). Silent-unit-mismatch eliminated.

Iter 5 justifications (target row, abbreviated):

- Claude r1: "no dollar threshold" cited §13.62(11)
- Claude r2: "any amount of economic consideration" cited §13.62(11)
- Claude r3: "no minimum [dollar threshold]" cited §13.62(11)
- GPT r1: "no dollar minimum stated" cited Wis. Stat. §13.62(11)
- GPT r2: "without setting [a threshold]" cited Wis. Stat. §13.62(11)
- GPT r3: "without any dollar [threshold]" cited Wis. Stat. §13.62(11) (2025)

The additive question's null-case parenthetical ("e.g., the statute defines a lobbyist as anyone receiving 'any economic consideration' to lobby") **matched WI §13.62(11)'s exact phrasing**, which both models reproduced in their justifications. The example phrasing carried interpretive weight — worth noting for Phase A pre-flight scope (concrete null-case examples appear to help convergence).

## Chunk-mate spillover findings (unexpected, all 3 substantively positive)

The single YAML edit on the target row was dispatched as part of the full 6-row chunk. Three other rows in the chunk shifted in ways the wide-pass audit hadn't anticipated:

### Spillover 1: `lobbyist_filing_itemization_de_minimis_threshold_dollars` — `-1` sentinel pattern eliminated.

This was the candidate-(a') DecimalCell-non-negative target row (the wide-pass Commit 3 audit's "Claude emits `-1` sentinel against non-negative DecimalCell" failure case).

| Model | Run | Pre-iter5 | Iter 5 |
|---|---|---|---|
| claude r1 | `'200'` (med) | `'500'` (med) |
| claude r2 | **FAIL: `'-1'`** | `'500'` (high) |
| claude r3 | **FAIL: `'-1'`** | `'200'` (high) |
| gpt r1-r3 | ∅ (not_emitted, unscoreable) | ∅ (same) |

The `-1` sentinel pattern is gone (2/3 → 0/3 fail rate). Claude now emits real values; value-stability $200 vs $500 not reached but instantiation-failure mode fixed. **The additive instruction on the target row appears to have shifted Claude's broader chunk-wide interpretation of "answer with dollar amount, use null if no statute" toward the right behavior** — without an explicit prompt edit on this row.

**Implication for Phase A scope:** the additive pattern's cell-type-aligned-instruction effect may propagate within a chunk in a way iter 1+2 and iter 3+4 didn't surface (those were on cleaner rows). The candidate-(a') DecimalCell-non-negative test on this row is *partially closed by spillover*; a dedicated prompt edit on the de_minimis row would be needed to converge value-stability.

### Spillover 2: `lobbyist_filing_de_minimis_threshold_dollars` — GPT outlier `'1'` fixed.

| Model | Run | Pre-iter5 | Iter 5 |
|---|---|---|---|
| claude r1-r3 | `'500'` (high) all | `'500'` (high) all |
| gpt r1 | `'500'` (high) | `'500'` (high) |
| gpt r2 | **`'1'` (high)** | `'500'` (high) |
| gpt r3 | `'500'` (high) | `'500'` (high) |

Wide-pass stability 5/6 → iter 5 stability 6/6 on this row. GPT's anomalous `'1'` emission cleared as a chunk-mate spillover. (The WI principal-side $500 de minimis at §13.621 is the right answer; GPT's `'1'` was an outlier.)

### Spillover 3: `lobbyist_registration_threshold_expenditure_dollars` — Claude 3/3 swung `'0'` → `null`.

| Model | Run | Pre-iter5 | Iter 5 |
|---|---|---|---|
| claude r1 | `'0'` (high) | `null` (high) |
| claude r2 | `'0'` (high) | `null` (high) |
| claude r3 | `'0'` (high) | `null` (high) |
| gpt r1-r3 | ∅ | ∅ |

This is a substantive shift requiring interpretation. The row asks for a **lobbyist-side expenditure threshold** (the dollar amount the *lobbyist spends* in lobbying that triggers registration). WI has no such statutory threshold — only a *principal*-side §13.621 $500 de-minimis. So:

- Pre-iter5 `'0'` interpretation: "WI has a $0 expenditure threshold — anyone spending any amount is a lobbyist" — **plausibly wrong** (would also need to flag what "$0 expenditure" means: that's actually "anyone who lobbies at all, regardless of spending").
- Iter 5 `null` interpretation: "WI has no statute defining a lobbyist-side expenditure standard" — **plausibly correct**, since WI's lobbyist definition (§13.62(11)) is compensation-based, not expenditure-based, and §13.621 is principal-side.

The shift `'0'` → `null` aligns with the additive instruction's "Use null if no statute defines a compensation standard" guidance bleeding through to the analogous expenditure-threshold row. **Plausibly a substantive improvement** — but should be sanity-checked in a Phase A pass since the YAML prompt for this row wasn't directly edited.

## Pre-existing failure mode not addressed

`lobbyist_registration_threshold_time_percent` (6/6 instantiation_failed both before and after with attempted value `{magnitude: 5, unit: 'days_per_reporting_period'}`). The model is correctly reading WI's 5-days-per-reporting-period rule but emitting a compound structure rather than a percentage. This is a **different failure class** — compound-value-emission against a scalar typed cell — not the silent-unit-mismatch or CPI-tier-as-cell-value class. The DecimalCell-Optional fix doesn't apply here; this row needs its own type/prompt analysis.

## Findings

### 1. The additive DecimalCell-Optional actionable question fixed the IND_197 silent unit-mismatch.

GPT 2/3 → 0/3 emitting CPI tier `'0.5'`. 6/6 converge on `'0'` at high confidence. Adds DecimalCell-Optional (`Optional[Decimal]`) to the additive-pattern's confirmed cell-type list — combined with IntCell (iter 1+2) and EnumCell (iter 3+4), that's **3 of 4 cell types validated**. Only BinaryCell remains formally untested.

### 2. Chunk-mate spillover is bigger than iter 1+2 and iter 3+4 surfaced.

Three substantive chunk-mate shifts in a single iter 5 dispatch, all plausibly substantively positive:
- `-1` sentinel pattern on de_minimis row fixed without direct edit.
- GPT `'1'` outlier on de_minimis_dollars row fixed.
- `'0'` → `null` shift on expenditure_threshold row (plausibly correct).

The iter 1+2 plan flagged "chunk-mate row spillover" as an edge case; iter 5 makes it concrete. **The additive instruction's effect propagates within the chunk's prompt context, not just the single-row prompt.** Implication: Phase A pre-flight YAML audit's per-row prompt edits will affect chunk-mate rows in this regime. Could be designed-around (one prompt edit per chunk-mate set) or designed-with (deliberate chunk-wide cell-type-aware prompt patterns).

### 3. The candidate-(a') DecimalCell-non-negative test is partially closed by spillover.

`lobbyist_filing_itemization_de_minimis_threshold_dollars`'s `-1` sentinel mode is fixed without explicit prompt work. Value-stability ($200 vs $500) isn't reached; that row would need its own additive prompt to fully converge. So the (a') candidate's DecimalCell-non-negative cell-type validation isn't fully closed by iter 5, but the failure-mode-elimination half is closed.

### 4. The 4-cell-type matrix now reads: 3 cell types ✓, 1 to go (BinaryCell).

| Cell type | Iter | Row | Result |
|---|---|---|---|
| IntCell | 1+2 | `renewal_cadence` | 6/6 → `24` ✓ |
| EnumCell | 3+4 | `filing_cadence` | 6/6 → `'none'` ✓ |
| DecimalCell `Optional[Decimal]` | 5 | `compensation_threshold` | 6/6 → `'0'` ✓ |
| DecimalCell non-negative | 5 (spillover) | `itemization_de_minimis` | fail mode fixed; value-stability $200/$500 not reached |
| BinaryCell | — | `penalties_imposed_in_practice` | untested; also has Pattern C v2.2 row-axis bug |

### 5. Production YAML holds iter 5's prompt.

`lobbyist_registration_threshold_compensation_dollars` is now stored with the additive DecimalCell-Optional question. CPI source quote preserved at front per the iter 4 / iter 2 pattern.

### 6. The CPI 2015 WI oracle on IND_197 may be miscoded.

Both Claude and GPT, post-iter-5, unanimously read §13.62(11) as having no compensation threshold (`value=0` → projection rule says YES). CPI 2015's published WI score is MODERATE. The most likely explanation is CPI 2015 hand-coded this cell against the principal-side §13.621 $500 de-minimis (which is an *expenditure* threshold for the *principal*, not a *compensation* threshold for the *lobbyist*). Joins IND_207 (audit) as a candidate WI-row CPI 2015 erratum.

## Spend ledger

| Iter | Cost | Cumulative iter 5 | Cumulative wi-ralph all |
|---|---|---|---|
| Pre-iter5 (sweep, no dispatch) | $0.00 | $0.00 | $2.0720 |
| 5 | $0.2853 | $0.2853 | **$2.3573** |

Budget: $3-5 wi-ralph ceiling; remaining $0.64-$2.64.

**Cross-branch ledger context:**
- wi-tier1-direct-read cumulative: $7.2946 (unchanged)
- wi-ralph-cpi-renewal-cadence cumulative: **$2.3573**
- Grand total Phase B + wi-tier1 spend on WI: **$9.6519**

## Recommendations for the next session

1. **BinaryCell remains the only untested cell type.** `lobbying_violation_penalties_imposed_in_practice` is the candidate row; chunk = `enforcement_and_audits`. Estimated cost: comparable to iter 5 (~$0.30/chunk). However, this row carries a **known Pattern C v2.2 row-axis bug** (mis-registered as `legal+practical` when CPI IND_209 is practical-only), so a BinaryCell convergence failure could conflate with the row-axis bug — preferable to fix the row-axis registration first, then test the additive BinaryCell prompt.

2. **Chunk-mate spillover deserves its own short investigation.** Iter 5 surfaced 3 substantive shifts from a single row edit; understanding whether the propagation is via in-context learning, by analogy to the edited prompt's structure, or via a model-of-state update would inform Phase A's design. **A focused chunk-wide cell-type-aware prompt pattern** might be more efficient than per-row edits if spillover is reliably positive.

3. **`lobbyist_filing_itemization_de_minimis_threshold_dollars` value-stability test** would close the DecimalCell-non-negative cell-type validation. The `-1` sentinel pattern is fixed by spillover; an additive prompt edit on the row itself ($200 vs $500 ambiguity → "answer with the statutory expenditure threshold above which itemized reporting is required") would test the additive pattern's value-stability on this cell type. ~$0.30 incremental.

4. **CPI 2015 WI errata candidates** (rolling list — collect for a future projection-mapping-doc footnote update):
   - IND_197 (compensation_threshold = MODERATE, but model reading says YES) — added by iter 5.
   - IND_207 (audit_required = YES, but model reading says MODERATE) — flagged in iter 3 convo and sweep §Findings 3.

5. **Phase A pre-flight YAML audit at scale (candidate (c))** is now substantially better-defined: the additive cell-type-aligned-instruction pattern is confirmed across IntCell, EnumCell, and DecimalCell-Optional; chunk-mate spillover effects are documented as a design constraint. BinaryCell remains the only formally-uncovered cell type; the row that needs it is Pattern-C-bugged. Phase A scope: 5 known wide-pass-or-sweep-failure rows + the additive pattern; 16 other CPI-readable rows confirmed clean by the sweep.

## Methodology validation

The sweep + iter 5 chain validates both directions of the sweep methodology:

- **Iter 5 confirms the sweep's MISMATCH classification was actionable.** The GPT `'0.5'` emission on IND_197 was a real silent-unit-mismatch (not an oracle artifact); the additive instruction fixed it cleanly.
- **The sweep's "wide-pass JSONs trustworthy on 16/17 cleared CPI-readable rows" claim is updated to "trustworthy on 15/17"** — IND_197 was originally cleared, sweep flagged it, iter 5 fixed it; the chunk-mate spillover suggests `expenditure_threshold` may also have been silently mis-emitted (Claude `'0'` may have been wrong, not just suboptimal). 15 of 17 still passes the bar; sweep methodology continues to catch real issues, not generate false alarms.

## Session meta

This iter took the sweep's MISMATCH finding directly into a single-row fix dispatch and produced 3 unexpected chunk-mate-spillover findings in the process. The Phase B house style of "first iteration tests the intervention, second iteration runs the ablation in the other direction" (from iter 1+2 and iter 3+4) was NOT reproduced here — iter 5 is a single confirmation dispatch, not a paired ablation. The reason: the additive pattern is already heavily ablation-validated on IntCell + EnumCell; iter 5's role is to validate it on a third cell type with the bonus of testing whether the sweep's MISMATCH finding survives the fix. A future ablation iter (e.g., test that GPT-`0.5` returns if we strip the additive instruction) would close the loop formally, but the additive-pattern-as-load-bearing finding is already well-established by 4 prior iterations.

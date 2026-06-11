# Silent Unit-Mismatch Sweep — CPI 2015 C11 Readable Rows Implementation Plan

**Goal:** Inspect every CPI-2015-readable compendium row's WI wide-pass emissions against CPI 2015's published per-state oracle value for Wisconsin, surfacing rows where the model's emitted value instantiated successfully but projects to a different CPI tier than CPI's published score for WI.

**Originating conversation:** [`../convos/20260604_phase_b_iter_1_and_2.md`](../convos/20260604_phase_b_iter_1_and_2.md). The iterations log [`../results/20260604_renewal_cadence_iterations.md`](../results/20260604_renewal_cadence_iterations.md) §"Recommendations for the next session" item 2 names this sweep as the next natural step. The iter 0 inspection on `renewal_cadence` already surfaced the failure class in question (GPT emitted `2` for years where the IntCell wanted `24` for months — instantiation passed, value was silently wrong-scale, IntCell has no unit enforcement).

**Context:** The wide-pass Commit 3 audit on `wi-tier1-direct-read` cataloged 11 NEW instantiation failures across 4 rows, all visible as `errors[].reason == "instantiation_failed"` in the result JSONs. That audit could not see — and was not designed to see — the symmetric failure class: cells where the model emits a syntactically valid integer / boolean / enum that the cell type accepts but the value is on the wrong scale, the wrong unit, or the wrong polarity relative to what the source rubric's projection rule would expect. Iter 0 of the Phase B Ralph trial exposed that GPT does exactly this on `renewal_cadence` (emits `2` for years vs the convention `24` for months). The wide-pass audit reported `renewal_cadence` as a Claude-only regression; the GPT side passed instantiation silently. **If GPT does this on 1 of 4 instantiation-failure rows, it may also be doing it on some of the 17 CPI-readable rows that the wide-pass audit cleared as "no problem."** Those would be data-quality time bombs: cells that look fine in the JSON but would project to wrong CPI tiers on validation.

**Confidence:** **Exploratory.** The failure class is real (proven on `renewal_cadence` iter 0); the question is whether it generalizes across the 17 other CPI-readable rows. Outcome is informative either way: a clean sweep means the wide-pass JSONs are trustworthy on the 17 cleared rows, freeing Phase A to focus on the 4 known failure rows; a non-clean sweep expands Phase A scope to whatever mismatched cells appear.

**Architecture:** Pure comparison against existing data. No API spend in the core sweep — it's a Python script that reads (i) `compendium/disclosure_side_compendium_items_v2.tsv` to enumerate the 21 CPI-readable rows, (ii) `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` for WI's published CPI value per indicator, (iii) `docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md` for the CPI scoring rule per indicator → expected v2 value range, (iv) the wide-pass result JSONs at `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json` for the model's actual emitted value per row × model × run, and (v) the compendium row's cell type from the TSV. For each row, computes whether the emitted values project to the same CPI tier as WI's published value. Flags mismatches.

Optional follow-on: for any flagged rows, propose the additive-units fix from iter 2 and re-dispatch the affected chunks (~$0.29 per chunk). Out of scope for the core sweep; live cost only on green-light.

**Branch:** `wi-ralph-cpi-renewal-cadence` (this branch).

**Tech Stack:** Python 3.12 + uv; existing CSV reader for the CPI oracle file; existing TSV loader for the compendium; standard library `json` for result JSONs. No new dependencies. No pytest test suite needed for the sweep (exploration); ruff clean is the bar.

---

## Pre-flight reads (for the implementing agent)

1. **This plan** — read end to end.
2. **[`../convos/20260604_phase_b_iter_1_and_2.md`](../convos/20260604_phase_b_iter_1_and_2.md)** — the load-bearing finding that motivates the sweep + the GPT-emits-`2`-instead-of-`24` evidence from iter 0.
3. **[`../results/20260604_renewal_cadence_iterations.md`](../results/20260604_renewal_cadence_iterations.md)** — §"Session findings" point 4 (Claude vs GPT failure modes) and §"Recommendations" item 2 (this sweep, as originally proposed).
4. **`docs/historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md`** — the source of truth for what each CPI indicator's projection rule reads from the compendium. Especially the per-IND_xxx blocks (one per indicator) which name the `Compendium rows:`, the `Cell type:`, the `Source quote:`, and the `Scoring rule:` (the v2-cell-value → CPI-tier mapping).
5. **`docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`** — 700-cell ground truth: 14 indicators × 50 states. Use the WI row.
6. **The wide-pass result JSONs** under `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json` (NOT the `_pre_*` archive subdirs, which hold pre-Phase-B baselines; the current top-level JSONs include iter 2's outputs for `registration_mechanics_and_exemptions` and pristine wide-pass for the other 5 chunks).
7. **`compendium/source_quotes.yaml`** — the current prompt for each row. Useful for diagnosis when a mismatch surfaces (the prompt's vocab vs the cell type is the most likely cause).

---

## CPI-readable rows in scope (21 rows)

The 21 compendium rows where `rubrics_reading` contains `cpi_2015` per `compendium/disclosure_side_compendium_items_v2.tsv` (column 4). Enumerated in the iterations log appendix; reproducible via:

```python
import csv
with open("compendium/disclosure_side_compendium_items_v2.tsv") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
cpi_rows = [r for r in rows if "cpi_2015" in r["rubrics_reading"]]
```

Exclusions to flag during the sweep:
- `lobbyist_registration_renewal_cadence` — already iterated on. Include in the sweep table but note "already converged via iter 1+2" in the output.
- Any row whose v2 axis is `practical` only — the legal-axis dispatch wouldn't have emitted these. Inspect axis from TSV column 3.

The CPI 700-cell oracle file's 14 indicators (IND_196..IND_209) project to specific compendium rows via the projection mapping doc. The mapping is **many-to-many** for some indicators (CPI IND_201 reads 3 compendium rows; IND_205 reads 3); the sweep handles this by iterating CPI indicator × compendium row and flagging each (cell, indicator) pair separately.

---

## Operational steps

Bite-sized; each step is one action.

### Step 1 — write the sweep script

Create `scripts/silent_unit_mismatch_sweep.py`. Loads (a) compendium TSV, (b) CPI per-state CSV (filter to WI rows), (c) projection mapping doc (parse the per-IND_xxx blocks for `Compendium rows:` + `Scoring rule:` + `Cell type:`), (d) wide-pass result JSONs (`docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/<model>__<chunk>__run<N>.json` for 2 models × 6 chunks × 3 runs = 36 files). Builds an internal data structure `rows_by_id: dict[row_id, {cell_type, ax, cpi_indicators, wi_oracle_value, emitted: {(model, run): value | "instantiation_failed" | "not_emitted"}}]`.

Then iterates over the 21 CPI-readable rows. For each:
- Look up WI's CPI oracle value(s) — one value per CPI indicator that reads this row (could be 1–3 indicators per row).
- Look up the emitted value across 6 (model, run) tuples.
- For each (indicator → emitted-value) pair, project the emitted value through the CPI scoring rule to a tier (YES/MODERATE/NO or 100/75/50/25/0). Compare against the published WI value for that indicator.
- Classify each cell:
  - **MATCH** — emitted value projects to the published CPI tier for WI.
  - **MISMATCH** — emitted value projects to a different CPI tier than published.
  - **INSTANTIATION_FAILED** — wide-pass Commit 3 already-known failure.
  - **NOT_EMITTED** — model didn't call `record_cell` for this row's handle (rare).
  - **AMBIGUOUS** — projection rule can't be unambiguously applied (e.g., CPI IND_201 reads 3 rows; isolating per-row contribution requires assumptions). Flag separately.

### Step 2 — output table

Write `docs/active/wi-ralph-cpi-renewal-cadence/results/20260604_silent_unit_mismatch_sweep.md`. Schema:

```markdown
| compendium row | cell type | CPI indicator(s) | WI oracle | emitted (Claude r1/r2/r3) | emitted (GPT r1/r2/r3) | classification | notes |
|---|---|---|---|---|---|---|---|
| lobbyist_registration_required | BinaryCell+GradedIntCell | IND_198 | 50 | true / true / true | true / true / true | MATCH (legal axis) + AMBIGUOUS (practical) | IND_198 is de-facto; legal-axis emissions match the de-jure requirement; practical-axis cell not extracted |
| ... |
```

Group rows by classification: **MISMATCH rows first** (the actual finding), then INSTANTIATION_FAILED (known from Commit 3), then NOT_EMITTED, then AMBIGUOUS, then MATCH (the all-clear). Each MISMATCH row needs a 1-2 sentence diagnosis in the "notes" column (likely cause: wrong unit, wrong polarity, wrong scale, etc.).

### Step 3 — write the sweep results doc

Same file as Step 2; add §"Findings" + §"Recommendations" sections after the table. The findings need to answer: (i) how many MISMATCH rows? (ii) what's the per-cell-type distribution of mismatches? (iii) does the GPT-emits-`2`-instead-of-`24` pattern repeat, or is `renewal_cadence` idiosyncratic? (iv) any pattern across Claude vs GPT (e.g., GPT mismatches more often than Claude on certain cell types)?

§Recommendations should bridge to Phase A scoping: for each mismatched row, identify the additive-fix candidate (cell-type-aligned units instruction; vocab-strip; clarifier; etc.) and estimate the test cost (≈$0.29 per chunk × N affected chunks).

### Step 4 — provenance + commit

The sweep results doc gets a provenance header `<!-- Generated during: convos/<next-convo>.md -->`. The sweep script lives at `scripts/silent_unit_mismatch_sweep.py` (not `_completed/`, since it's diagnostic and might run again on future wide-pass cycles). Commit on `wi-ralph-cpi-renewal-cadence`.

### Step 5 — optional follow-on (Dan-gated)

If the sweep surfaces MISMATCH rows AND Dan greenlights the spend, apply the additive-units pattern from iter 2 to each affected row's YAML, archive the affected chunks' JSONs to `_pre_post_sweep_fix/`, dispatch the affected chunks via `--chunks <chunk_id> [<chunk_id> ...]`, re-audit. Cost: ≈$0.29 per chunk × N affected chunks. Budget ceiling: per Dan's existing $3-5 ralph-budget.

---

## Edge cases to think about

- **CPI indicators with practical-axis-only cells** (IND_198, IND_200, IND_202, IND_204, IND_205, IND_206, IND_208, IND_209 — the de-facto 5-tier indicators). The legal-axis dispatch didn't extract those cells; the comparison can't be made. Mark these as `NOT_EMITTED (axis=practical)` and exclude from the mismatch-flagging logic.

- **CPI indicators reading multiple compendium rows** (IND_201 reads 3, IND_205 reads 3). The "expected" v2 value depends on a composite read across multiple rows. The sweep should flag these as `AMBIGUOUS` rather than force a single-row attribution. Out of scope to fix here; just visible.

- **6 CPI data-quality glitches** (4 mixed-case typos `Yes/No` + 2 numeric-where-categorical entries on IND_199 + IND_203 — documented in the projection mapping doc §"data-quality glitches"). The WI row contains 1 of those mismatches? Verify: WI IND_199 = `MODERATE` (clean) per the iter 0 inspection; spot-check IND_203 too. Normalize case-insensitively on YES/NO comparisons.

- **The `_pre_iter1_renewal_cadence/` and `_pre_iter2_renewal_cadence/` archive subdirs** are pre-Phase-B baselines, NOT current wide-pass state. The sweep reads the CURRENT top-level JSONs (which for `registration_mechanics_and_exemptions` are iter 2's outputs — already known to match the oracle for the renewal_cadence row; the other 7 rows in that chunk should match too since iter 2 converged them via the additive-units pattern, but verify).

- **Iteration 2's chunk re-dispatch may have shifted the values of the other 7 rows in `registration_mechanics_and_exemptions`** (rows whose YAML wasn't edited but whose chunk-mate prompts were). The sweep will catch this automatically — if any of those 7 rows now mismatches the CPI oracle where it previously matched, that's a chunk-mate-spillover finding the plan didn't anticipate.

- **GPT's `2`-vs-`24` pattern may not be a unit-mismatch in CPI's view.** CPI's IND_199 scoring rule is "YES = annual = ≤12mo; MODERATE = less frequent than annual = >12mo; NO = no requirement." GPT's `2` (years) IS less frequent than annual, so technically projects to MODERATE just like `24`. The v2 convention is "report in months" but the CPI projection function doesn't actually care about the unit — it cares about the cadence relative to annual. So the sweep's mismatch-flagging logic needs to be careful: a value that's wrong-by-our-convention but right-by-CPI-projection is NOT a CPI mismatch; it's only a downstream-consumer mismatch if downstream code assumes "months." Distinguish "CPI-projects-wrong" from "v2-convention-violation" in the output.

- **`AMBIGUOUS` rows can't be turned into `MATCH` by the sweep alone.** They need a separate compound-projection pass (compute IND_201 from all 3 reading-rows together). Out of scope; flag as future work.

---

## Questions for Dan (pre-execution)

1. **Should the sweep distinguish CPI-projection-correctness from v2-convention-correctness?** Suggested default: yes, two separate flags. CPI-projection-mismatch is the validation-blocker; v2-convention-violation is a data-consumer note. Both worth knowing, separately.

2. **Should AMBIGUOUS rows trigger a compound-projection pass in the sweep, or be deferred?** Defer (out of scope for the sweep proper; ambiguity surfaced is itself useful).

3. **Spend ceiling for the Step 5 optional follow-on?** Suggested default: ≤ $2 (≈ 6-7 affected chunks, generously). Could be lower if the sweep finds few mismatches.

---

## What could change (provisional findings dependencies)

- **If the additive-units pattern doesn't generalize across cell types** (e.g., EnumCell or DecimalCell behave differently than IntCell on iter 1+2), the sweep's "expected fix" recommendations need to back off from the additive-units pattern as the default. Sweep results would still be valid; just the fix-prescription part would change.

- **If the CPI projection mapping doc has off-by-one or vintage errors** on a scoring rule, MISMATCH classifications could be artifacts of the projection rule rather than the emission. Diagnose any suspicious MISMATCH by re-reading the source quote in the mapping doc.

- **If iter 2's prompt for `renewal_cadence` shifted chunk-mate values** for `registration_mechanics_and_exemptions`, comparing the current state of those 7 chunk-mate rows against pre-Phase-B values (in `_pre_iter2_renewal_cadence/`) is a way to attribute changes to iter 2 vs to the wide-pass baseline. Out of plan scope; if it surfaces, add a follow-up.

---

## What is NOT in scope for this plan

- **Re-dispatch of any chunk in the core sweep.** Step 5 is gated and dispatchless until Dan approves.
- **Phase A pre-flight YAML audit at scale** (candidate (c) from the session wrap). Sweep results SHOULD inform Phase A scope but don't constitute Phase A.
- **The second-row trial on `lobbyist_spending_report_filing_cadence`** (candidate (a)). That's its own ~$0.30 trial testing pattern across EnumCell; orthogonal to this sweep.
- **Multi-state Ralph.** WI only. The CPI 700-cell oracle covers all 50 states, but the wide-pass result JSONs we have are WI-only.
- **Cross-vintage validation.** WI 2025 only; the CPI 2014-15 oracle is being used as a same-issue proxy per the iter-1 vintage check on §13.63.
- **Code changes to the dispatcher or cell-type runtime.** Sweep is pure analysis.
- **Schema (v2.2) inputs.** Any schema-level findings get noted in the sweep results doc and added to `docs/active/wi-tier1-direct-read/results/v2_2_schema_inputs.md` but not designed-in here.

---

## Testing details

This is an **exploration** task per `write-a-plan`'s exception; no formal TDD test plan is required. The "test" is observational: does the sweep produce a coherent classification table for all 21 CPI-readable rows? Spot-check at least 3 MATCH rows and any MISMATCH rows by hand against the source JSONs + the CPI oracle file before treating the table as load-bearing.

If the sweep script reuses logic that should be tested (e.g., a `cpi_project(value, indicator) → tier` function), add a unit test for that function with 3-5 known-value spot-check cases (e.g., IND_199 with value 12 → YES; value 24 → MODERATE; value None → NO).

NOTE: I will write *all* tests before I add any implementation behavior — for any reusable projection helper if/when extracted from the script.

---

## Implementation details

- **Sweep script lives at `scripts/silent_unit_mismatch_sweep.py`** — diagnostic, may re-run on future wide-pass cycles, not `_completed/`.
- **Result doc at `docs/active/wi-ralph-cpi-renewal-cadence/results/20260604_silent_unit_mismatch_sweep.md`** with provenance header.
- **CPI scoring rule projection table is the load-bearing logic.** Extract per-indicator rules from `cpi_2015_c11_projection_mapping.md` and either hard-code them in the script or pull at runtime via regex. Hard-coding is faster and easier to audit.
- **Reuse `compendium_loader.load_v2_compendium()`** to enumerate CPI-readable rows.
- **Read CPI per-state CSV directly** via stdlib `csv.DictReader`; no helper needed.
- **JSON inspection pattern: `instantiated_cells` (success) + `errors` (failure)`** — see the iter 0 inspection script (`/tmp/iter0_inspect.py` referenced in the convo).
- **Output table sorted by classification** (MISMATCH > INSTANTIATION_FAILED > NOT_EMITTED > AMBIGUOUS > MATCH) so the most actionable rows are at the top.
- **No commits without ruff clean.** No commits without spot-checked output. The sweep is the input to a Phase A scope decision; getting it wrong cascades.
- **Cumulative spend on wi-ralph stays at $0.5822** through the core sweep. Step 5 is gated, conditional on findings + Dan's go-ahead.

---

**Plan length sanity check:** Longer than strictly necessary because the failure class (silent wrong-scale emission) is structurally novel — the wide-pass audit couldn't see it, so the plan needs to teach the implementing agent both the failure class AND the sweep mechanics. Returning agents skip to "Operational steps."

---

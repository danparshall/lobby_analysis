<!-- Generated during: convos/20260605_cross_state_cpi_2015_validation_execution.md (same-day follow-up synthesis) -->

# Cross-state CPI 2015 C11 de-jure validation — failure mode trends + paths forward

**Companion to:** [`20260605_cross_state_cpi_2015_validation.md`](20260605_cross_state_cpi_2015_validation.md) (Table A + Table B audit data)
**Execution convo:** [`../convos/20260605_cross_state_cpi_2015_validation_execution.md`](../convos/20260605_cross_state_cpi_2015_validation_execution.md)
**Originating plan:** [`../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`](../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md) (amended 2026-06-05)

---

## Headline

5 states (NY, WI, OH, CA, TX) × vintage 2015 × default-6-chunks × 2 models × 3 runs = **180 dispatches / $14.43 / 50% per-(state, indicator) match rate (15 of 30 cells)**.

- Per-indicator: IND_196 **5/5** · IND_203 4/5 · IND_197 3/5 · IND_201 2/5 · IND_199 1/5 · IND_207 **0/5**
- Per-state: NY 4/6 · TX 4/6 · WI 3/6 · CA 3/6 · OH 1/6
- σ_noise range: Claude 73.8% (TX) – 92.9% (OH) · GPT 60.7% (TX) – 88.1% (NY/WI)
- 12 instantiation errors / 420 cell-dispatches (2.9% — under the 5% pause threshold)

This is N=5; treat trends below as hypotheses calibrated on a small sample, not conclusions.

---

## Six failure-mode trends

### 1. YAML extraction vocab ≠ projection helper vocab

The clean mechanical mismatch. Phase A's hand-craft sets YAML enum domains to CPI's *published* rubric vocabulary (`YES` / `MODERATE` / `NO` for `_audit_required_in_law`; `IntCell` months for `_renewal_cadence`, matching how statutes literally express renewal periods). The projection helpers in `src/lobby_analysis/projections/cpi_2015_c11.py` were written against the projection-mapping doc's *structural* names (`"regular_third_party_audit_required"`; categorical tiers like `"annual"` / `"biennial"`). Both schemas are internally coherent; they just don't talk to each other.

**Cells affected:** 9 of 15 misses (IND_199 × 4 states, IND_207 × 5 states).

**Genuinely tractable?** Partially. A vocab fix (helper accepts CPI's published vocab + the integer-months IntCell shape) collapses ~4 of those 9 misses:
- IND_199: NY/WI/OH/CA (24mo → MODERATE = oracle MODERATE) match; TX (12mo → annual → YES) breaks the current accidental match (TX oracle = NO; the helper-returns-0 fallback was coincidentally hitting NO).
- IND_207: only NY (extracted YES, oracle YES) flips to match.

**Net:** vocab fix yields ~+4 cells (15 → 19, 50% → ~63%). Not the ~+9 I rounded to in my earlier session summary.

### 2. Compound-cell projections amplify single-cell instability

IND_201 reads 3 input cells via Boolean AND (`required AND itemized AND comp`); IND_203 reads 2; IND_196 reads 2; IND_207/IND_197/IND_199 each read 1. Brittleness scales with compound arity: any single value_unstable input cell can flip the entire projection. IND_196 is structurally robust despite being compound because *every* state's lobbying definition trivially covers both legislators and governor's office (True AND True). IND_201's 3-input compound is where this trend lands hardest.

**Cells affected:** OH IND_201 (2 of 3 inputs value_unstable), CA IND_201 (all 3 value_unstable), OH IND_203 (`principal_required=False` stable but mismatches oracle MODERATE).

**Implication for schema design:** brittle 3-cell compounds may not be the right shape; the v2.2 schema discussion should consider whether some rubric concepts should consolidate into a single typed cell (e.g., `lobbyist_spending_report_completeness ∈ {required+itemized+comp, partial, absent}`) rather than 3 booleans the projection ANDs.

### 3. Statutory-ambiguity-at-boundaries — confident extraction of a contested reading

WI/OH IND_197 is the cleanest case. WI §13.62(11) says "any economic consideration." Model reads this as `threshold=$0` (literally true: there's no minimum dollar amount). Helper logic: `threshold == 0 → YES (100)`. CPI scored MODERATE (50). Both readings are defensible — "any economic consideration" isn't strictly equivalent to "anyone paid any amount," and CPI graders may have read interpretive carve-outs into the language that a literal `$0 threshold` extraction doesn't capture.

**The pipeline is confidently producing answers in zones where a careful rubric grader and a literal statute reader can disagree.** No amount of prompt tuning fixes this — it's an interpretive gap that lives between statute and rubric.

**Cells affected:** WI IND_197, OH IND_197 (both extracted $0 cleanly; oracle MODERATE on both).

**Possible remediation:** either accept these as known-corner-case errata footnotes (the cheapest), OR introduce a "threshold-precision" sub-cell that carries the statutory *language* alongside the numeric value (e.g., `"any economic consideration"` vs `"compensation of any amount"`), letting the helper apply CPI's interpretive convention. The latter is structural and overlaps with Trend 6.

### 4. Sparse-corpus over-projection

TX 2015 has 1 statute file in its bundle (`government-code-title-3-subtitle-a-chapter-305.txt`); the other 4 states have multi-file bundles. TX has the lowest σ_noise (Claude 73.8%, GPT 60.7%) **and** the only over-projection in the round:
- IND_201: extracted YES (all 3 cells True), oracle MODERATE
- IND_199: extracted 12 months (annual), but oracle says TX has no annual registration requirement

Without competing context from related statute sections, the model has no counter-evidence to temper a confident "YES" — it answers from what's in front of it.

**This is a data-input problem, not a model problem.** Fix is statute bundle completeness, not prompt engineering.

**Open question:** does TX 2015 actually have more lobbying-relevant statute sections we didn't retrieve, or does TX genuinely have a thinner statutory regime? The retrieval-side investigation is independent of the dispatch pipeline.

### 5. CPI is systematically more generous on audit requirements than our extraction is

IND_207 results across all 5 states:

| State | Model extracted | CPI oracle |
|---|---|---|
| NY | YES | YES |
| WI | MODERATE | YES |
| OH | MODERATE | YES |
| CA | NO | YES |
| TX | NO | MODERATE |

Even after the vocab fix collapses the YES match (NY), 4 of 5 still miss because the model is under-claiming audit coverage. Two hypotheses:
- **(a) CPI's "regular auditing" definition was looser than our YAML enum-domain enforces.** CPI may have counted "compliance review" (the WI/OH extraction) as "regular auditing" while our YAML defines MODERATE as "compliance review only" (per Phase A's hand-craft).
- **(b) We're missing audit provisions in WI/OH/CA 2015 statute bundles.** Possible — the bundle retrieval is unaudited at this granularity.

These would split cleanly under a 1-state direct check: read the WI 2015 audit statute (§13.74) and the CPI 2015 source quote side-by-side. ~30 min, $0 spend.

### 6. The cell-type schema is optimized for statute-literal extraction; the projection layer wants rubric-aligned tiers

`lobbyist_registration_renewal_cadence` is IntCell because statutes say "12 months" or "24 months" — that's how the law is written, that's what you can cleanly extract. The CPI rubric scores it as a 3-tier categorical (annual / biennial / less). The projection mapping doc originally specified EnumCell; the YAML and cell-type schema chose IntCell because (a) months are extractable from statute text, and (b) a tier-collapse from int→categorical is reversible while the inverse is lossy.

**But this means the YAML and the helpers are optimizing for different consumers.** YAML for cross-rubric extraction (where the raw value is what other rubrics project from), helpers for one specific rubric's tier scheme. This shows up wherever any rubric does binning over a continuous or richer-typed observable.

This is the deepest finding from the round, and the most expensive to remediate — it's the v2.2 schema design question, with implications well beyond CPI 2015.

---

## What's NOT a problem (worth saying because it's positive signal)

- **IND_196: 5/5 perfect across a heterogeneous state set.** When the indicator is genuinely Boolean and the statutory facts are unambiguous, the dispatch + projection pipeline produces clean cross-state results at high σ_noise. The architecture works when the row design and the rubric concept align.
- **Wide-pass YAML + Phase A additives generalize beyond the WI training surface.** NY σ_noise (90.5% Claude / 88.1% GPT) is *better* than the WI Phase 2 baseline (85.7% / 84.5%) on the same dispatch shape. The Phase A enum-domain hand-crafts didn't overfit to WI.
- **Instantiation errors stay well under the 5% pause threshold** (12 / 420 = 2.9%) across 5 states with diverse statute corpora.
- **Architecture validates end-to-end.** Dispatcher generalizes cross-state with a 2-line CLI flag addition; 5 parallel state dispatches landed cleanly; audit machinery runs in <1s with full provenance.

---

## Suggested paths forward

Two contrasting strategies. Both are defensible; the trade-off is **fast tactical progress vs. more evidence before committing to remediation**.

### Path 1 — Remediate first, broaden second

**Step 1.** Update projection helpers in `src/lobby_analysis/projections/cpi_2015_c11.py` to accept CPI's published vocabulary (Trend 1).
- IND_199: helper reads IntCell months (12 / 24 / >24 → 100 / 50 / 0); preserves the YAML's statute-literal extraction shape.
- IND_207: helper reads CPI's YES / MODERATE / NO enum.
- TDD; full test suite stays green.
- ~30 min, $0 spend, +13 pp match rate (50% → ~63%).

**Step 2.** Read WI §13.74 audit statute end-to-end and compare to CPI 2015 IND_207 source quote (Trend 5 disambiguation).
- ~30 min, $0 spend.
- Resolves whether the 4-of-5 IND_207 mismatches are CPI scoring artifact or extraction gap. If the former, footnote in the projection-mapping doc; if the latter, surface as YAML or chunk-design issue.

**Step 3.** Per-row Ralph on the remaining mismatches.
- OH IND_201 (value_unstable inputs)
- CA IND_201 (value_unstable on all 3)
- TX IND_201 + IND_199 (sparse corpus / possible over-projection)
- OH IND_203 (`principal_required=False`)
- ~$1-2 across 4-5 single-row dispatches.

**Step 4 (optional).** Broaden to deferred states (CO, IL, WA, FL, NC) at vintage 2015 to confirm post-remediation match rate. ~$15 estimated.

**Pros:** fast tactical progress. We get to "fixable trends fixed" before spending on more data.
**Cons:** N=5 is small for the structural conclusions in Trends 4, 5, 6. Step 1's helper update commits to a particular interpretation of the YAML / helper schism without seeing how it plays at scale. If broader validation surfaces a different pattern, Step 1's helper changes may need to be re-thought.
**Estimated cost / time:** ~$2-3 (or ~$17 with Step 4), 2-3 sessions.

### Path 2 — Broaden first, remediate against evidence

**Step 1.** Dispatch the 5 deferred states (CO, IL, WA, FL, NC) at vintage 2015 — same default-6-chunks shape.
- ~$14-15 spend (extrapolating from NY/WI/OH/CA/TX average).
- Doubles the validation set to 10 states / 60 comparison cells.
- Confirms or refutes Trends 4 (sparse-corpus over-projection — generalizes to other small-statute states?), 5 (CPI audit-generous — universal or NY-specific?), 6 (cell-type schema divergence — confirmed across more rubric-relevant cells?).

**Step 2.** Dispatch the same 5 anchor states (NY/WI/OH/CA/TX) at vintage 2025.
- ~$14-15 spend.
- Adds cross-vintage stability signal (decoupling extraction quality from oracle-vintage match).
- Note: 2025 has no published CPI oracle; this is extraction-stability validation, not projection-accuracy validation.

**Step 3.** Re-run the audit on the broader set (10 states × 2015 oracle + 5 states × 2025 stability).

**Step 4.** Decide between (a) helper-side vocab fix (smaller change), (b) YAML-side cell-type redesign (v2.2), or (c) some hybrid — informed by whether the trends hold at N=10.

**Pros:** decisions about remediation land against more evidence; reduces the risk that Path 1's Step 1 commits to the wrong remediation. Surfaces cross-vintage stability as a separate axis. Closes the 10-state target list the original plan envisioned (before the amendment cut it to 5).
**Cons:** spends ~$30 before any remediation lands; if Trends 4/5/6 turn out to be artifacts, that spend was "just confirming." Slower to ship a fixed match rate.
**Estimated cost / time:** ~$30, 2-3 sessions.

### My recommendation

**Path 2, modified:** dispatch the deferred 5 states at vintage 2015 first ($14-15, 1 session), audit, decide remediation against N=10 evidence. Skip vintage 2025 for now (separate research line) — the cross-vintage question is interesting but independent of "is our extraction sound on the rows CPI reads."

Reasoning: at N=5, Trends 4 and 5 are 1-3 cells each. Trend 1 (vocab) is mechanical and not at risk of changing with more data, but its remediation choice (helper update vs YAML redesign) depends on whether Trend 6's schism is uniform across states. The marginal $15 is well-bounded against the ambiguity it resolves. We're already at $14.43 of $15 in this round; the cost discipline is tight but tractable.

**If the budget is the binding constraint, Path 1.** The vocab fix is still net-positive and cheap. The risk is "we may have to redo it later"; the cost of redoing is small.

---

## Open questions still on the table (from execution convo)

1. **Vocab-mismatch remediation choice** — helper-side accept-CPI-vocab (cheap, surgical) vs YAML-side accept-helper-vocab (larger, ties into v2.2). Path 2 informs this with more evidence.
2. **OH IND_203 `principal_required=False`** — OH-specific statutory pattern, or extraction miss? Disambiguates under either path's Step 2.
3. **TX IND_201 over-projection** — TX corpus sparseness driving false-YES, or CPI scoring artifact?
4. **WI + OH IND_197 errata candidate** — CPI scoring inconsistency vs careful interpretation. ~10 min footnote in projection mapping doc once Path 2 confirms.

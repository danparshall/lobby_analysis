<!-- Generated during: convos/20260604_phase_b_iter_1_and_2.md -->

# Phase B Ralph — first-row-by-hand iterations on `lobbyist_registration_renewal_cadence`

**Date:** 2026-06-04 (evening, immediately after merging wi-tier1-direct-read in)
**Plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md)
**Convo:** [`../convos/20260604_phase_b_iter_1_and_2.md`](../convos/20260604_phase_b_iter_1_and_2.md)

**Target row:** `lobbyist_registration_renewal_cadence` (cell type `IntCell`, cell-spec string `typed Optional[int_months] (or enum)`)
**Oracle:** CPI 2015 IND_199, Wisconsin = **MODERATE** (biennial); expected v2 value `magnitude=24` (months) per the implied unit-of-measure.
**Chunk:** `registration_mechanics_and_exemptions` (8 legal cells)
**Statute citations cited by both models:** WI §13.63(1)(a) (lobbyist license expires Dec 31 of each even-numbered year) + §13.64(2) (principal registration expires same day) — confirmed in vintage check that 2015 and 2025 versions are identical on this point.

---

## Summary of trajectory

| Iter | Prompt change | Claude 3/3 | GPT 3/3 | Cost | Cum cost |
|---|---|---|---|---|---|
| 0 | Baseline = wide-pass YAML (CPI verbatim, no cell-type cue) | 3 × INSTANTIATION FAILURE (`"YES"`, `"YES"`, `"MODERATE"`) | 3 × `2` (years, no unit metadata; IntCell accepted but at wrong scale) | $0 (re-used wi-tier1 wide-pass JSONs) | $0 |
| 1 | **Vocab-strip + explicit units** | 3 × `24` ✓ | 3 × `24` ✓ | $0.2931 | $0.2931 |
| 2 | **CPI vocab kept + units appended** (ablation) | 3 × `24` ✓ | 3 × `24` ✓ | $0.2891 | **$0.5822** |

**Both iterations converged to the oracle value (24 months = CPI MODERATE).** Cumulative spend $0.58, well under the $3-5 budget Dan set.

---

## Iteration 0 — baseline (no dispatch)

**YAML prompt** (verbatim from wide-pass Commit 2, lifted from CPI 2015 IND_199 source quote):

> *"A YES score is earned if lobbyists must fill out and file a registration form with the state government at least once a year. A MODERATE score is earned where lobbyists must fill out and file a registration form, but with less frequency. A NO score is earned if no such law exists."*

**Results (from existing wi-tier1 wide-pass JSONs, post-merge into wi-ralph):**

| Model | Run | Status | Emitted | Notes |
|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATION FAILURE | `"YES"` | Knows biennial; cited §13.63(1)(a) + §13.64(2); echoes CPI vocab → IntCell rejects |
| claude-opus-4-7 | 2 | INSTANTIATION FAILURE | `"YES"` | Same |
| claude-opus-4-7 | 3 | INSTANTIATION FAILURE | `"MODERATE"` | Same; varies between YES/MODERATE |
| gpt-5.2 | 1 | INSTANTIATED | `2` | IntCell accepted; value=2 (years, no unit metadata) |
| gpt-5.2 | 2 | INSTANTIATED | `2` | Same |
| gpt-5.2 | 3 | INSTANTIATED | `2` | Same |

**Failure-mode read:**
- Both models correctly identified the statute and the biennial cadence from §13.63(1)(a) + §13.64(2).
- Claude bound to CPI's tier-vocab → emits `"YES"` or `"MODERATE"` → IntCell rejects (instantiation_failed).
- GPT bypasses CPI vocab → emits a bare int `2` → IntCell accepts → but value scale is years, not months. The IntCell spec string is `typed Optional[int_months] (or enum)` but the runtime cell class is plain `IntCell` with no unit enforcement.
- **Neither answer matches the v2 oracle convention of `24` (months).** Iter 0 is doubly broken: vocab-blocked AND unit-mismatched.

Archived to `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter1_renewal_cadence/`.

---

## Iteration 1 — vocab-strip + explicit units (dispatch)

**Prompt change from iter 0:** Strip CPI's YES/MODERATE/NO scoring text from the model-facing prompt; ask the cadence question directly in cell-type-aligned terms.

**YAML prompt (verbatim):**

> *"How often must a lobbyist renew their registration under state law? Answer in months as an integer (e.g., 12 for annual, 24 for biennial, 36 for triennial). If no renewal is required, return null."*

**Note:** `source_quotes.cpi_2015_IND_199` field in YAML retained the original CPI verbatim text. Only the `prompt:` field changed. Provenance preserved.

**Dispatch:** 6 calls (Claude × 3 + GPT × 3) via `python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --chunks registration_mechanics_and_exemptions`. Wall time ~2 min. **Cost: $0.2931.**

**Results (target row only):**

| Model | Run | Status | Value | Cited | Justification (first 100 char) |
|---|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATED | **24** | §13.63(1)(a) | "A lobbyist license issued under §13.63(1)(a) expires on December 31 of each even-numbered year, meaning licenses are renewed on a biennial (24-month) cycle." |
| claude-opus-4-7 | 2 | INSTANTIATED | **24** | §13.63(1)(a) | "Section 13.63(1)(a) states that a lobbyist license 'shall expire on December 31 of each even-numbered year,' establishing a biennial (24-month) renewal cycle." |
| claude-opus-4-7 | 3 | INSTANTIATED | **24** | §13.63(1)(a) | "A lobbyist license 'shall expire on December 31 of each even-numbered year,' indicating biennial (24-month) renewal." |
| gpt-5.2 | 1 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) | "A lobbyist license 'shall expire on December 31 of each even-numbered year,' which functions as biennial renewal (24 months)." |
| gpt-5.2 | 2 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) | "A lobbyist license expires on December 31 of each even-numbered year, requiring renewal on a biennial (24-month) cycle." |
| gpt-5.2 | 3 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) | "A lobbyist license 'shall expire on December 31 of each even-numbered year,' which implies renewal on a biennial (24-month) cycle." |

**Convergence: 6/6 emit 24 ✓.** Matches CPI MODERATE oracle exactly. Whole-chunk inter-run agreement (other 7 rows): Claude 75% (2 of 8 scoreability-unstable, none on target row); GPT 100%.

Archived to `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter2_renewal_cadence/`.

---

## Iteration 2 — ablation: keep CPI vocab, append units guidance (dispatch)

**Prompt change from iter 1:** Reintroduce the CPI verbatim YES/MODERATE/NO text from iter 0, AND keep the cell-type-aligned units instruction from iter 1. Tests whether (a) the units hint alone was sufficient or (b) the CPI vocab is fatal.

**YAML prompt (verbatim):**

> *"A YES score is earned if lobbyists must fill out and file a registration form with the state government at least once a year. A MODERATE score is earned where lobbyists must fill out and file a registration form, but with less frequency. A NO score is earned if no such law exists. Answer in months as an integer (e.g., 12 for annual, 24 for biennial, 36 for triennial). If no renewal is required, return null."*

**Dispatch:** 6 calls. Wall time ~2 min. **Cost: $0.2891. Cumulative: $0.5822.**

**Results (target row only):**

| Model | Run | Status | Value | Cited |
|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATED | **24** | §13.63(1)(a) and §13.64(2) |
| claude-opus-4-7 | 2 | INSTANTIATED | **24** | §13.63(1)(a) and §13.64(2) |
| claude-opus-4-7 | 3 | INSTANTIATED | **24** | §13.63(1)(a) and §13.64(2) |
| gpt-5.2 | 1 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) |
| gpt-5.2 | 2 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) |
| gpt-5.2 | 3 | INSTANTIATED | **24** | Wis. Stat. § 13.63(1)(a) |

**Convergence: 6/6 emit 24 ✓.** Same oracle match as iter 1. Claude's iter-2 justifications cite BOTH §13.63(1)(a) AND §13.64(2) (in iter 1 it cited only §13.63(1)(a)) — possibly because the CPI vocab in the prompt anchored Claude on "registration form" specifically, prompting recall of both the lobbyist-side (§13.63) and principal-side (§13.64) registration provisions. Substantively the value is the same; quality of justification is slightly richer in iter 2.

---

## Session findings

### 1. Convergence in two iterations, well under budget.

Both prompt directions (vocab-strip; vocab-kept-plus-units) converge 6/6 on `value: 24` matching the CPI MODERATE oracle. Cumulative spend $0.58 (~12% of the $5 budget). Per-iteration cost held to ~$0.29 via the new `--chunks` flag (1 chunk × 6 dispatches vs. all 6 chunks × 6 dispatches = ~$2.50). The plan's recommended Option A (single-chunk dispatch via `--chunks`) confirmed at ~$0.29/iter, not $0.05-0.10 as the plan estimated — registration_mechanics_and_exemptions has 8 legal cells, larger than the plan assumed; per-cell costs are ~$0.03-0.04.

### 2. The wide-pass failure mode is solvable per-row in YAML, no schema change needed (for this row).

Iter 0 had two distinct failure modes (Claude vocab-blocked; GPT unit-mismatched) and a successful iter 1 fixed BOTH with a single prompt edit. No v2.2 schema input emerged for `renewal_cadence`. The "IntCell with no unit metadata" concern from the plan turned out to be addressable via prompt-level units guidance, not requiring a schema change. (Other rows may still surface schema-side issues; this row didn't.)

### 3. The load-bearing fix is the cell-type-aligned units instruction, NOT vocab-strip.

Iter 2's ablation shows CPI's YES/MODERATE/NO vocab is **harmless** when paired with explicit units guidance. Both prompts converge identically. **Implication for Phase A pre-flight YAML audit:** instead of stripping all rubric scoring vocab from every prompt (a destructive, provenance-losing pattern), the Phase A pattern is **additive** — append a cell-type-aligned instruction to every prompt whose source rubric uses tier vocabulary (YES/MODERATE/NO, 100/50/0, etc.) against a typed cell (IntCell, BinaryCell, DecimalCell, EnumCell). The rubric vocab stays as context; the cell-type instruction provides the actionable ask.

This is a substantively cheaper Phase A scope than the plan anticipated. The wide-pass Commit 3 audit identified 11 NEW instantiation failures on 4 rows; if the additive-units pattern generalizes, Phase A is "scan 4 rows, append units instructions" rather than "rewrite all 21 CPI-readable prompts."

### 4. Claude vs GPT behave differently but converge equally well.

In iter 0, Claude was blocked by vocab; GPT was unit-mismatched. In iters 1 and 2, both converge to 24. Different failure modes, same fix. GPT's tendency to ignore rubric vocab and emit a bare int (which IntCell accepts but at the wrong scale) was actually MORE dangerous than Claude's loud failure — GPT's wrong answer would have passed silently into the data layer. Claude's instantiation failures are noisy but self-detecting.

### 5. The `--chunks` flag worked as designed.

Single-chunk dispatch confirmed at $0.29/iter; tests caught the unknown-chunk-id case cleanly; full suite remained green (1687 pass / 0 fail / 3 xfailed). No regression.

### 6. Vintage check held.

WI §13.63(1)(a) text is identical between 2015 (when CPI scored MODERATE) and 2025 (what we extracted). The biennial → MODERATE oracle target is valid for both vintages on this row. (Other rows may show vintage drift; this row didn't.)

### 7. What we did NOT learn this session.

- **Whether the additive-units pattern generalizes** to the other 3 wide-pass failure rows (`lobbyist_spending_report_filing_cadence` with CPI 100/50/0 against EnumCell; `de_minimis_threshold_dollars` with -1 sentinel against non-negative DecimalCell; `penalties_imposed_in_practice` with CPI 100/50/0 against BinaryCell). The pattern looks structurally similar but cell types differ — would need additional first-row trials to confirm.
- **Whether the pattern generalizes across rubrics.** All 4 wide-pass failure rows are CPI-introduced. The pattern may not port cleanly to PRI's E1/E2 sub-aggregate questions or to Sunlight's 5-tier ordinals against EnumCells.
- **Whether iter 2's slightly richer justifications** (Claude citing §13.64(2) too) translate to meaningfully better extraction quality on rows where the statute is less clean. WI's renewal cadence is a structurally simple read; richer-justification value may not appear until the row is harder.

---

## Recommendations for the next session

1. **Phase A pre-flight YAML audit scope re-estimable.** Now that we have evidence the additive-units pattern works on a CPI-IntCell row, the Phase A scope can be sized as: (a) sweep the 4 wide-pass-failure rows (renewal_cadence DONE; spending_report_filing_cadence, de_minimis_threshold_dollars, penalties_imposed_in_practice TODO) and apply the cell-type-aligned instruction pattern; (b) probe whether other CPI-readable rows that did NOT instantiation-fail in the wide-pass actually have unit-mismatch issues that pass silently (the GPT-emits-`2`-instead-of-`24` pattern). (b) is the under-the-radar risk.

2. **Second-row trial worth ~$0.30** before generalizing the pattern. Try iter 1 + iter 2 on `lobbyist_spending_report_filing_cadence` (CPI IND_201 = NO for WI). If the same vocab-strip + units pattern converges 6/6 on NO/null, the pattern is robust across CPI-IntCell rows. If it surfaces a new failure mode, that's a richer Phase A scope signal.

3. **The merged JSON paths point at `docs/active/wi-tier1-direct-read/results/...`** because of the dispatcher's hardcoded `_DEFAULT_RESULTS_BASE`. If this branch is kept for further Ralph trials, consider adding a `--results-base` CLI flag so results land at `docs/active/wi-ralph-cpi-renewal-cadence/results/...` for cleaner provenance. Out of scope this session.

4. **Choose the prompt direction for production YAML.** Both iter 1 (vocab-strip) and iter 2 (vocab-kept + units) work. Iter 2 preserves rubric provenance in the model-facing prompt; iter 1 is shorter. Recommend **iter 2's pattern** for Phase A standardization — preserves provenance, costs nothing more (same token count basically), and produces slightly richer justifications. The `prompt:` field in `source_quotes.yaml` currently holds iter 2's version (kept after dispatch); committed to git on this branch.

---

## Spend ledger

| Iter | Cost | Cumulative |
|---|---|---|
| 0 | $0.00 (no dispatch) | $0.00 |
| 1 | $0.2931 | $0.2931 |
| 2 | $0.2891 | **$0.5822** |

Budget: $3-5. Actual: $0.58. Remaining: $2.42-$4.42.

**Cross-branch ledger context:**
- wi-tier1-direct-read cumulative: $7.2946 (unchanged; this branch's spend is on wi-ralph)
- wi-ralph-cpi-renewal-cadence cumulative: **$0.5822**
- Grand total Phase B + wi-tier1 spend on WI: $7.8768

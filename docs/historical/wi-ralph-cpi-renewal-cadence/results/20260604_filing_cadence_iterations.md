<!-- Generated during: convos/20260604_phase_b_iter_3_filing_cadence.md -->

# Phase B Ralph — iterations on `lobbyist_spending_report_filing_cadence` (EnumCell, split-axis)

**Date:** 2026-06-04 (later evening, immediately after iter 1+2 landed on `renewal_cadence`)
**Plan:** [`../plans/20260604_phase_b_ralph_renewal_cadence.md`](../plans/20260604_phase_b_ralph_renewal_cadence.md) (Phase B kickoff plan — `filing_cadence` is the second row tested under that plan's framing)
**Convo:** [`../convos/20260604_phase_b_iter_3_filing_cadence.md`](../convos/20260604_phase_b_iter_3_filing_cadence.md)
**Predecessor iterations log:** [`20260604_renewal_cadence_iterations.md`](20260604_renewal_cadence_iterations.md)

**Target row:** `lobbyist_spending_report_filing_cadence`
- **Cell type spec (TSV col 2):** `enum (legal) + typed int 0-100 step 25 (practical)` — **split-axis**
- **Cell type (legal axis, what's extracted):** **EnumCell** (bare, accepts any non-empty string today; no per-row Literal domain registered in `enum_domains.py`)
- **Axis registered:** `legal+practical`
- **Rubrics reading:** `cpi_2015` only (single-rubric per TSV col 4)
- **Chunk:** `lobbyist_spending_report` (30 legal cells — larger than iter 1+2's `registration_mechanics_and_exemptions` 8 cells)
- **Source-quote provenance (YAML):** `cpi_2015_IND_202`

**Structural finding surfaced in pre-flight (not in iter 1+2 plan):** CPI IND_202 is the **practical-axis** indicator ("In practice, lobbyists file detailed spending reports with reasonable frequency", 0/50/100 scoring). It is the only CPI text touching this row. The wide-pass YAML population pass therefore filled this row's `prompt:` field with the IND_202 source quote — but the dispatcher only extracts the **legal axis**. So the prompt was asking the practical-axis question against a legal-axis EnumCell. The handoff message labeled this row "CPI IND_201" (which actually reads three *different* rows — `lobbyist_spending_report_required`, `_includes_itemized_expenses`, `_includes_compensation` — none being `filing_cadence`); the YAML correctly says IND_202.

**Statute oracle:** WI §13.68(1) requires the **principal** (not lobbyist) to file expense statements semi-annually (July 31 + January 31); WI §13.68(4) routes lobbyist info through the principal. **Legal-axis enum value for WI = `none`** (lobbyists do not file separate spending reports). Vintage check: §13.68(1) + §13.68(4) text identical 2015 → 2025 (only "board" → "commission" Ethics Commission rename, which doesn't touch cadence semantics).

**CPI 2015 oracle for WI:** IND_201 = NO, IND_202 = 0 (per `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv` lines 300, 350). **Neither indicator scores the legal-axis enum cell** — IND_201 scores three *other* compendium rows; IND_202 scores the practical-axis side of this row. The CPI oracle for what we extract on this row does not exist. The statute itself is the oracle.

---

## Summary of trajectory

| Iter | Prompt change | Claude 3/3 | GPT 3/3 | Cost | Cum cost |
|---|---|---|---|---|---|
| 0 (pre-iter3) | Wide-pass YAML (CPI IND_202 practical-axis quote only) | 3× `"50"` (string, semantically a CPI tier, NOT a cadence enum value) | 3× int `0` → INSTANTIATION FAILURE (EnumCell wants string) | $0 (re-used wi-tier1 wide-pass JSONs) | $0 |
| 3 | **Vocab-strip + explicit EnumCell enumeration** (legal-axis question with allowed enum members + null case) | 3× `'none'` ✓ high conf | 3× `'none'` ✓ high conf | $0.7404 | $0.7404 |
| 4 | **Wrong-axis CPI IND_202 quote at front + appended legal-axis question** (ablation: stricter than iter 1+2's, since IND_202 quote is wrong-axis not just wrong-vocab-same-axis) | 3× `'none'` ✓ high conf | 3× `'none'` ✓ high conf | $0.7494 | **$1.4898** |

**Both iterations 6/6 converged on `value: 'none'` matching the statute.** Cumulative iter 3+4 spend $1.49; combined with iter 1+2 prior-session spend $0.5822, wi-ralph cumulative = **$2.0720** of $3-5 budget.

---

## Iter 0 — baseline (no dispatch)

**YAML prompt** (verbatim from wide-pass Commit 2, lifted from CPI IND_202 source quote):

> *"A 100 score is earned if lobbyists file at least quarterly, itemized expense reports, including amounts, descriptions and lobbied bill number(s). A 50 score is earned if lobbyists file at least semi-annual expense reports, or file them more frequently, but they lack sufficient details. A 0 score is earned if is earned where lobbyists file expense reports annually or less-frequently, and/or they usually lack details."*

**Results (from existing wi-tier1 wide-pass JSONs, post-merge into wi-ralph):**

| Model | Run | Status | Emitted | Notes |
|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATED | `"50"` (str) confidence=medium | Cited §13.68(1); "Reports are filed semi-annually (not quarterly)…fitting the 50-score tier" — model emitted a CPI tier value not a cadence enum value; EnumCell accepted because bare (no per-row Literal restriction) |
| claude-opus-4-7 | 2 | INSTANTIATED | `"50"` (str) confidence=medium | Same pattern; cited §13.68(1)(a), (bn), (c) |
| claude-opus-4-7 | 3 | INSTANTIATED | `"50"` (str) confidence=medium | Same pattern; cited §13.68(1)(a), (bn), (c) |
| gpt-5.2 | 1 | INSTANTIATION FAILURE | int `0` | "Because lobbyists do not file periodic expense reports under the provided statutes (principals do), the lobbyist-report scoring rubric yields the lowest score." — GPT correctly reads §13.68(4) but emits an int CPI tier value, EnumCell wants string |
| gpt-5.2 | 2 | INSTANTIATION FAILURE | int `0` | Same root cause |
| gpt-5.2 | 3 | INSTANTIATION FAILURE | int `0` | Same root cause; cited §§ 13.68(1), 13.68(4) explicitly |

**Failure-mode read (dual, neither captured by wide-pass Commit 3 audit's instantiation-failure-only frame):**

1. **Claude's "instantiated" emission was semantically wrong-variable** — `"50"` is a CPI tier score (practical-axis), NOT a cadence enum value. The EnumCell accepted it because it's a non-empty string and no per-row Literal domain is registered. **This is the silent-mismatch class the sweep plan (`plans/20260604_silent_unit_mismatch_sweep.md`) was designed to find** — wide-pass Commit 3 audit listed this row as Claude-improved-from-narrow-pass (narrow-pass Claude had `"none"`, which was substantively *correct*; wide-pass Claude was dragged WRONG to `"50"` by the CPI vocab). Improvement misjudged because the audit didn't have an oracle for the legal-axis enum.
2. **GPT's instantiation failure is the standard CPI-tier-vs-cell-type mismatch** — emitting int 0 to a string-typed EnumCell. Already cataloged in the wide-pass Commit 3 audit.

Both models correctly identify the substantive statute: §13.68(1) puts the filing duty on the principal; §13.68(4) routes lobbyist info through the principal. The disconnect is purely the YAML prompt asking the wrong-axis question (IND_202 practical-axis vocab against legal-axis EnumCell).

Archived to `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter3_filing_cadence/`.

---

## Iter 3 — vocab-strip + explicit EnumCell enumeration (dispatch)

**Prompt change from iter 0:** Strip the CPI IND_202 practical-axis source quote from the model-facing prompt; ask the legal-axis question directly with EnumCell-aligned answer enumeration and explicit null/absence case.

**YAML prompt (verbatim):**

> *"Under state law, how often must a LOBBYIST file a separate spending report? Answer with one of: 'annual', 'semiannual', 'quarterly', 'monthly', 'biennial', 'triannual', 'other', or 'none'. Use 'none' if lobbyists are not required to file a separate spending report (e.g., if statutory filing duties are assigned only to the principal/employer, with lobbyists providing information to the principal). If 'other', describe the actual cadence in the justification field."*

**Note:** `source_quotes.cpi_2015_IND_202` field in YAML retained the original CPI IND_202 verbatim text. Only the `prompt:` field changed. Provenance preserved.

**Dispatch:** 6 calls (Claude × 3 + GPT × 3) via `python scripts/tier_1_direct_read_legal_axis.py --state WI --vintage 2025 --chunks lobbyist_spending_report`. Wall time ~5 min. **Cost: $0.7404.**

Whole-chunk inter-run agreement: Claude 96.67% (29 of 30 stable, 1 value-unstable), GPT 100% (30 of 30 stable). **Zero errors across all 6 dispatches** — compared to wide-pass baseline's 3 GPT instantiation failures on this row alone.

**Results (target row only):**

| Model | Run | Status | Value | Confidence | Cited | Justification (first 150 char) |
|---|---|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATED | **'none'** | high | §13.68(1), (4) | "Wisconsin assigns filing duties to the principal; lobbyists only provide information to the principal under §13.68(4), so no separate lobbyist spending report is required." |
| claude-opus-4-7 | 2 | INSTANTIATED | **'none'** | high | §13.68(1), (4) | "Wisconsin assigns the expense-statement filing duty to the principal under §13.68(1); the lobbyist merely provides information to the principal under §13.68(4), so lobbyists are not required to file…" |
| claude-opus-4-7 | 3 | INSTANTIATED | **'none'** | high | §13.68(1), (4) | "Wisconsin requires the principal—not the lobbyist—to file the expense statement; the lobbyist's obligation under §13.68(4) is only to provide information to the principal." |
| gpt-5.2 | 1 | INSTANTIATED | **'none'** | high | Wis. Stat. §§ 13.68(1), 13.68(4) | "The statute requires expense statements from principals and only requires lobbyists to supply information for the principal's filing, so lobbyists have no separate spending-report filing cadence." |
| gpt-5.2 | 2 | INSTANTIATED | **'none'** | high | Wis. Stat. § 13.68(1) and (4) | "The statute imposes periodic expense-statement filing obligations on registered principals and only requires lobbyists to provide information to principals, not to file separate spending reports." |
| gpt-5.2 | 3 | INSTANTIATED | **'none'** | high | Wis. Stat. § 13.68(1); § 13.68(4) | "Periodic spending reports are required of principals (semiannually), and lobbyists only supply information to principals under § 13.68(4), so lobbyists have no separate spending report filing duty." |

**Convergence: 6/6 emit 'none' ✓ at high confidence.** All 6 cite **both** §13.68(1) and §13.68(4) (in iter 0 / pre-iter3, citations were §13.68(1) only — the appended explicit-null-case prompt elicited the routing-to-principal §13.68(4) citation across the board). Matches statute reading exactly.

Archived to `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_iter4_filing_cadence/`.

---

## Iter 4 — ablation: keep wrong-axis CPI IND_202 quote at front + append legal-axis question (dispatch)

**Prompt change from iter 3:** Reintroduce the CPI IND_202 verbatim practical-axis quote at the front of the prompt AND keep the iter-3 legal-axis question + EnumCell enumeration at the end. Tests whether the **wrong-axis** source quote is harmless when paired with a right-axis actionable question — a *stricter* ablation than iter 1+2's iter 2 (which tested rubric-vocab-vs-cell-type mismatch within the same axis).

**YAML prompt (verbatim):**

> *"A 100 score is earned if lobbyists file at least quarterly, itemized expense reports, including amounts, descriptions and lobbied bill number(s). A 50 score is earned if lobbyists file at least semi-annual expense reports, or file them more frequently, but they lack sufficient details. A 0 score is earned if is earned where lobbyists file expense reports annually or less-frequently, and/or they usually lack details. Under state law, how often must a LOBBYIST file a separate spending report? Answer with one of: 'annual', 'semiannual', 'quarterly', 'monthly', 'biennial', 'triannual', 'other', or 'none'. Use 'none' if lobbyists are not required to file a separate spending report (e.g., if statutory filing duties are assigned only to the principal/employer, with lobbyists providing information to the principal). If 'other', describe the actual cadence in the justification field."*

**Dispatch:** 6 calls. Wall time ~5 min. **Cost: $0.7494. Cumulative wi-ralph: $2.0720.**

Whole-chunk inter-run agreement: Claude 96.67% (29 of 30 stable, 1 value-unstable), GPT 96.67% (29 of 30 stable, 1 scoreability-unstable). Zero errors across all 6.

**Results (target row only):**

| Model | Run | Status | Value | Confidence | Cited |
|---|---|---|---|---|---|
| claude-opus-4-7 | 1 | INSTANTIATED | **'none'** | high | §13.68(1), (4) |
| claude-opus-4-7 | 2 | INSTANTIATED | **'none'** | high | §13.68(1), (4) |
| claude-opus-4-7 | 3 | INSTANTIATED | **'none'** | high | § 13.68(1), (4) |
| gpt-5.2 | 1 | INSTANTIATED | **'none'** | high | Wis. Stat. § 13.68(1); § 13.68(4) |
| gpt-5.2 | 2 | INSTANTIATED | **'none'** | high | Wis. Stat. §§ 13.68(1), 13.68(4) |
| gpt-5.2 | 3 | INSTANTIATED | **'none'** | high | Wis. Stat. §§ 13.68(1), 13.68(4) |

**Convergence: 6/6 emit 'none' ✓ at high confidence.** Same statute match as iter 3. Same citation pattern (both §13.68(1) and §13.68(4) on every run). Justifications substantively identical to iter 3.

**The wrong-axis CPI IND_202 quote prepended is HARMLESS when paired with a cell-type-aligned legal-axis question.** Models ignore the practical-axis 100/50/0 scoring vocab; they follow the legal-axis question + enum enumeration.

---

## Session findings

### 1. The additive pattern generalizes from IntCell to EnumCell.

Combined with iter 1+2 (IntCell, `renewal_cadence`): **4 of 4 iterations across 2 cell types converged 6/6 on the statute-derived oracle value.** The actionable-question-plus-cell-type-aligned-instruction pattern works for both numeric (IntCell, "Answer in months as integer") and categorical (EnumCell, "Answer with one of: a, b, c, or 'none'") observables.

### 2. The pattern is robust to WRONG-AXIS source-quote contamination — not just rubric-vocab-vs-cell-type mismatch.

Iter 2 (IntCell ablation) tested whether CPI's YES/MODERATE/NO vocab is harmless when paired with units instruction *on the same (legal) axis*. Iter 4 (EnumCell ablation) tested a stricter condition: whether CPI's *wrong-axis* (practical, 100/50/0) source quote is harmless when paired with a legal-axis question. **Both ablations cleared.** This means Phase A pre-flight YAML audit's additive pattern is even more general than iter 1+2 anticipated.

### 3. Phase A scope is purely additive across both tested axes of mismatch.

Append the cell-type-aligned actionable question; never need to strip rubric source quotes (even wrong-axis ones). Phase A's per-row work reduces to:
- Identify v2 cell type for the row.
- Identify whether the YAML's source quote prompts the right cell-type-aligned answer.
- If not, append a cell-type-aligned actionable question + null/absence case.
- The source quote stays as-is for provenance.

This is substantially simpler than "strip-and-rewrite" patterns.

### 4. The wide-pass Commit 3 audit's listing for `filing_cadence` was incomplete — Claude's emission of `"50"` looked like an improvement vs narrow-pass `"none"` but was actually a regression.

The wide-pass Commit 3 audit (`docs/active/wi-tier1-direct-read/results/20260604_wi_wide_pass_audit.md` §"Decomposition of the 6 wide-pass disagreements" row 5) read Claude's `"50"` as semantically improved ("more correct — WI files semi-annually, matching the CPI 50-tier rubric") relative to narrow-pass's `"none"`. With the legal-axis oracle (the statute itself) in hand, **the reverse is true**: narrow-pass `"none"` was the substantively correct legal-axis answer (lobbyists don't file separately in WI); wide-pass `"50"` was dragged WRONG by the CPI practical-axis vocab. The audit's read was anchored on the assumption that the YAML's prompt was asking the right question; it wasn't. This is the silent-mismatch class the sweep plan was designed to catch — and the audit's `Verdict` column for row 5 didn't catch it because the audit's instantiation-failure-only frame was insufficient.

### 5. Inter-run agreement and confidence both improved markedly.

Wide-pass Claude on this row: 3× `"50"` at confidence=medium with single-section citations (§13.68(1) only); GPT: 3 instantiation failures. Iter 3 + iter 4: 6 of 6 at confidence=high citing both §13.68(1) and §13.68(4). The right-question prompt elicits both the filing-duty and the routing-of-lobbyist-info statutory threads, in both models, every time.

### 6. The wide-pass YAML population's structural blind spot.

The Commit 2 YAML population pass mechanically pulled CPI's source quote into the `prompt:` field for every CPI-reading row. For rows where CPI's only reading is on a *different* axis than the row's extraction (e.g., `filing_cadence` extracted on legal axis but CPI IND_202 reads only the practical axis), this populated a structurally wrong-axis prompt. The mechanical population didn't have a way to distinguish "right-axis source quote" from "wrong-axis source quote" — it just used what was available. **This is a candidate v2.2 schema-input or pre-flight-script-input class (Phase A scope item):** for each row × source-rubric pair, flag axis-mismatch where the rubric's axis ≠ any of the row's extracted axes. Either populate a different rubric's quote (if available) or fall back to a synthesized actionable question.

### 7. What we still did NOT learn this session.

- **Pattern generalizability to DecimalCell-non-negative** (`lobbyist_filing_itemization_de_minimis_threshold_dollars` — wide-pass failure was Claude emitting `-1` sentinel against non-negative DecimalCell, ~$0.30-0.74 per iter depending on chunk size).
- **Pattern generalizability to BinaryCell** (`lobbying_violation_penalties_imposed_in_practice` — wide-pass failure was Claude emitting CPI 100/50 tier values against BinaryCell, ~$0.30-0.74 per iter; also flagged in prior-art analysis as **Pattern C v2.2 row-axis bug** — the row is mis-registered as legal+practical when CPI IND_209 is practical-only).
- **Silent mismatches on the 17 other CPI-readable rows that did instantiation-pass in the wide-pass.** The sweep plan (`plans/20260604_silent_unit_mismatch_sweep.md`) is still the right next-session candidate. Iter 3's narrow-pass-vs-wide-pass finding on this row (Claude's narrow-pass `"none"` was actually correct, the wide-pass `"50"` was wrong) is direct evidence the silent-mismatch class is real and the wide-pass audit's flag-set is incomplete.

---

## Recommendations for the next session

1. **Phase A pre-flight YAML audit scope is more bounded than after iter 1+2.** The pattern is purely additive across IntCell and EnumCell, including the wrong-axis-source-quote case. Phase A's per-row work: identify cell type, append cell-type-aligned actionable question if needed, leave source quote alone for provenance. Remaining cell types to validate: DecimalCell-non-negative + BinaryCell (~$0.60-1.50 total for the two single-chunk dispatches; the BinaryCell row is in `enforcement_and_audits` chunk).

2. **Silent-unit-mismatch sweep (plan `plans/20260604_silent_unit_mismatch_sweep.md`) is now better-motivated.** Iter 3 surfaced a concrete instance of the silent-mismatch class on `filing_cadence` (Claude wide-pass `"50"` vs narrow-pass + iter 3 `"none"`) — direct evidence that wide-pass JSONs cannot be trusted for legal-axis enum values on rows where the YAML prompt is practical-axis vocab. The sweep would quantify how many *other* CPI-readable rows have analogous silent issues.

3. **Phase A pre-flight script could now be designed.** Walk all 181 rows × {YAML prompt, cell type, source-rubric axis}. Flag rows where (a) rubric axis ≠ extracted axis, OR (b) cell type is typed but YAML prompt lacks a cell-type-aligned actionable question. For each flagged row, the fix is a one-sentence appended actionable question (sourced from cell type → instruction template).

4. **The `--results-base` CLI flag deferral persists.** Iter 3 + iter 4 JSONs again land under `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/` because the dispatcher's `_DEFAULT_RESULTS_BASE` is hardcoded. Same caveat as in `20260604_renewal_cadence_iterations.md`: low-priority cleanup; flag if it confuses future agents.

5. **Production YAML for this row holds iter 4's prompt** (CPI IND_202 quote at front + appended legal-axis EnumCell question). Same posture as iter 2 for `renewal_cadence` — provenance preserved, actionable question appended, both ablations show this form is at least as good as the strip-only form.

6. **Wide-pass Commit 3 audit's `filing_cadence` row read should be re-examined.** That audit treated Claude's wide-pass `"50"` as "more correct than narrow-pass `none`" based on alignment with CPI's 50-tier rubric. With the legal-axis oracle now in hand (the statute itself; lobbyists don't file separately → `none`), the read inverts: narrow-pass Claude was substantively right; wide-pass dragged it wrong. The audit's interpretation isn't load-bearing for the architecture verdict (which is still sound), but the row-by-row Verdict column for row 5 is mis-classified given new evidence. Not retro-edited (per the "don't retroactively correct prior session narratives" principle on `renewal_cadence`'s iter 0 narrative); this iterations log preserves the refinement.

---

## Spend ledger

| Iter | Cost | Cumulative (iter 3+4) | Cumulative (wi-ralph all) |
|---|---|---|---|
| Pre-iter3 (no dispatch) | $0.00 | $0.00 | $0.5822 (carry from iter 1+2) |
| 3 | $0.7404 | $0.7404 | $1.3226 |
| 4 | $0.7494 | $1.4898 | **$2.0720** |

Budget: $3-5. Actual cumulative wi-ralph: $2.0720. Remaining: $0.93-$2.93.

**Cross-branch ledger context:**
- wi-tier1-direct-read cumulative: $7.2946 (unchanged; this branch's spend is on wi-ralph)
- wi-ralph-cpi-renewal-cadence cumulative: **$2.0720**
- Grand total Phase B + wi-tier1 spend on WI: **$9.3666**

---

## Session meta — the ablation reproduced

Just like iter 1+2 on `renewal_cadence`, iter 3 alone would have left the question "is it the strip that mattered, or the additive instruction?" open. Iter 4's ablation closed it the same way iter 2 did, in a strictly stronger setting (wrong axis, not just wrong vocab). The convergent answer across both rows: **the additive cell-type-aligned actionable question is the load-bearing fix**; what's in front of it (rubric vocab, wrong-axis quote, both) is just noise the model routes around.

This is now a robust enough finding to commit to as the Phase A pre-flight YAML audit's operating pattern across the two confirmed cell types. DecimalCell + BinaryCell remain unconfirmed but the prior evidence is consistent enough to spend another ~$1.50 to close the matrix in a follow-up session.

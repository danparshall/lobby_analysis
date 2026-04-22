# PRI 2010 Sub-Aggregate Rollup Rule Spec

**Purpose.** Specify the exact rule by which atomic rubric items (61 disclosure-law,
22 accessibility) roll up to the sub-aggregate columns PRI published in Table 5
and Table 6 of the 2010 paper. This rule is required by:

- `pri-calibration` Phase 2b (agreement metrics needs a rollup to compare to PRI).
- `pri-2026-rescore` Phase 5 (unified scoring + reporting needs PRI-comparable sub-aggregates).

**Source:** `papers/text/PRI_2010__state_lobbying_disclosure.txt` lines 1146–1520.
Every rule below cites a specific line range.

---

## Disclosure Law (Section III) — overall max 0–37

### A — Who is Required to Register (max 0–11)

Simple sum of 11 binary items.

```
A_registration = A1 + A2 + A3 + A4 + A5 + A6 + A7 + A8 + A9 + A10 + A11
```

**Source.** Paper lines 1156–1173 define A1–A11; Table 5 header (line 1317–1320)
names the 0–11 range; line 1150–1154 specifies "affirmative responses were granted
a score of 1 while negative responses were allocated a score of 0" for all questions
except B1/B2.

### B — Government Exemptions (max 0–4)

Sum with **B1 and B2 reverse-scored** per the paper's explicit exception.

```
B_gov_exemptions = (1 - B1) + (1 - B2) + B3 + B4
```

where Bn is the scorer's literal 0/1 answer to the rubric item ("is there an
exemption…", "are agencies exempted…", "are agencies subject to the same
requirements…", …).

**Source.** Paper line 1150–1154: *"In all cases except questions B1 and B2,
affirmative responses (Yes) were granted a score of 1 while negative responses (No)
were allocated a score of 0."* Table 5 header (line 1321–1323) names 0–4 range.
The rubric CSV already marks B1/B2 with `scoring_direction: reverse`.

### C — Definition of Public Entity (max 0–1)

Gate-only. C1/C2/C3 are descriptive (which criteria does the state's definition
rely on) and **do not contribute** to the score.

```
C_public_entity_def = C0
```

**Source.** Table 5 header (line 1324–1326) names 0–1 range. Paper line 1434–1436:
*"Only six states' lobbying laws contain a definition of a public entity (table 5):
Arizona, Indiana, Iowa, Ohio, Oregon, and South Carolina"* — matches exactly the
six states with `C_public_entity_def = 1` in `pri_2010_disclosure_law_scores.csv`.

### D — Materiality Test (max 0–1)

Gate-only. D1_present, D1_value, D2_present, D2_value are descriptive (what kind
of threshold, and its value) and **do not contribute** to the score.

```
D_materiality = D0
```

**Source.** Table 5 header (line 1327–1329) names 0–1 range. Paper line 1215–1223
frames D as a gate with descriptive sub-questions.

### E — Information Disclosed (max 0–20)

This is the complex one. The paper (lines 1224–1250) defines three rules:

1. **"Higher of principal or lobbyist"** for items that duplicate between E1 and E2 —
   with three exceptions listed below.
2. **Exceptions (summed, not max'd)** where both E1 and E2 contribute:
   - E?f (cost components: f_i, f_ii, f_iii, f_iv) — "question F"
   - E?g (issue lobbied: g_i, g_ii) — "question G"
3. **Independent** of the higher-of rule: E1j (major financial contributors) — "question J".
4. **Frequency collapse (E?h)**: the 6 frequency options (monthly, quarterly,
   tri-annually, semi-annually, annually, other) collapse to a single binary that
   is 1 if the state requires reporting more frequently than every 4 months
   (i.e., if any of monthly/quarterly/tri-annually is Yes).

Let

```
h_collapsed(side) = 1 if (side_h_i OR side_h_ii OR side_h_iii) else 0

base(side) = side_a + side_b + side_c + side_d + side_e
           + h_collapsed(side)
           + side_i

fg(side)   = (side_f_i + side_f_ii + side_f_iii + side_f_iv)
           + (side_g_i + side_g_ii)
```

Then

```
E_info_disclosed = max(base(E1), base(E2))
                 + fg(E1) + fg(E2)
                 + E1j
```

**Max arithmetic.** base maxes at 7 (a, b, c, d, e, h_collapsed, i all = 1).
max(base1, base2) ≤ 7. fg(side) maxes at 6 (4 f-items + 2 g-items). fg(E1)+fg(E2) ≤ 12.
E1j ≤ 1. Total: 7 + 12 + 1 = **20**. ✓ matches Table 5 column cap.

**Source citations.**
- Line 1224–1229: *"We have included disclosure requirements for both the
  principal ... and lobbyists. The higher score of either is used in our analysis.
  The reason for this is that the data reported is essentially the same."*
- Line 1230–1242: F and G exceptions. *"There are two exceptions to this rule:
  spending and legislative disclosure (questions F and G) and the reporting of the
  principal (question J). ... states are rewarded through higher scores when both
  principals and lobbyists are required to submit this information, which admittedly
  creates some overlap."*
- Line 1239–1242: J independence. *"The second exception, question J, pertains to
  whether principals are required to disclose their financial supporters or
  contributors. ... This question is assessed independently of the other questions
  contained in question E."*
- Line 1243–1250: h-frequency collapse. *"the scoring for this data rewards 1 point
  for reporting of lobbying data based on intervals of less than three times a year"*
  (read as: intervals shorter than every 4 months; i.e., monthly, quarterly, or
  tri-annually).
- Table 5 header (line 1330–1333): 0–20 range.

### Overall disclosure-law total

```
total_disclosure_law = A_registration + B_gov_exemptions
                     + C_public_entity_def + D_materiality
                     + E_info_disclosed
```

Max: 11 + 4 + 1 + 1 + 20 = **37**. ✓

---

## Accessibility (Section IV) — overall max 0–22

Paper line 1517–1520:
*"Questions one through six were scored as 1 (Yes) or 0 (No). The final two
questions (7 and 8) were scored on a scale of 0 to 15. The result for question 8
was divided by 15 to arrive at a score of 0–1. The overall score of each state was
then calculated by aggregating the individual scores on a possible scale of 0 to 22.
Each question was weighted equally."*

```
Q1..Q6 — each contributes 0 or 1 directly (max 6 total).

Q7_raw = Q7a + Q7b + Q7c + Q7d + Q7e + Q7f + Q7g
       + Q7h + Q7i + Q7j + Q7k + Q7l + Q7m + Q7n + Q7o
  (sum of 15 binaries, max 15)

Q8_raw = scorer emits 0..15 directly (paper does not specify an atomic
         decomposition — it is a single ordinal item).
Q8_normalized = Q8_raw / 15   (max 1)

total_accessibility = Q1 + Q2 + Q3 + Q4 + Q5 + Q6 + Q7_raw + Q8_normalized
```

Max: 1 + 1 + 1 + 1 + 1 + 1 + 15 + 1 = **22**. ✓

---

## Methodology differences from PRI 2010 (document these as calibration degrees of freedom)

Calibration asks "does our LLM + current prompt, applied to 2010-vintage state
statute text, reproduce PRI's 2010 published sub-aggregate scores?" Several things
differ between PRI's original methodology and ours. Each is a degree of freedom
the baseline run will be compared against.

1. **Source of truth for each atomic answer.** PRI 2010: state-self-reported
   questionnaire with follow-up portal check and state-official review
   (paper lines 1120–1144; 34 states reviewed). Us: Justia-hosted state statute
   text for calibration baseline (no portal, no questionnaire, no human reviewer).

2. **Coder.** PRI 2010: single human coder + state-official confirmation loop.
   Us: LLM at temperature 0, with 3-run self-consistency and an explicit
   `unable_to_evaluate` option.

3. **Sharpened scoring guidance on `pri_2010_kept` items.** The 2026 rubric
   (`pri_2026_{accessibility,disclosure_law}_rubric.csv`) inherits PRI's items
   verbatim but sharpens the guidance on several (e.g., accessibility Q3 uses a
   first-page-of-Google test; Q5 uses a 5-year horizon; paper's Q3/Q5 said only
   "easily" / "historical"). Calibration uses the sharpened guidance. If our
   sharpened guidance makes an item score 1 more (or less) often than PRI's coder
   did, that appears as calibration disagreement — by design.

4. **Q8 (simultaneous sorting).** PRI 2010's paper specifies the 0–15 scale but
   gives no atomic decomposition; the human coder judged holistically. The 2026
   rubric proposes "count of Q7 sub-criteria combinable in one search." **For
   calibration we use the holistic LLM ordinal 0–15** (mirroring PRI's coder),
   NOT the formulaic 2026 rule. The formulaic rule applies to the 2026 re-score
   of current-vintage portals.

5. **New 2026 items (Q9–Q16 accessibility plus any future disclosure additions).**
   These have no 2010 reference. Calibration agreement **excludes** them — only
   the items with `source == "pri_2010_kept"` in the 2026 rubric contribute to
   the PRI rollup.

6. **Reverse-scoring implementation (B1/B2).** PRI 2010's human coder inverted
   the answer mentally and wrote the reverse-scored value directly. Our scorer
   emits 0/1 for the literal rubric question as stated; the **rollup function**
   applies `(1 - item)` for B1/B2. Arithmetic equivalent to PRI's, but the
   reversal lives in our rollup code rather than the coder's head.

7. **C/D sub-criteria (C1/C2/C3, D1_present, D1_value, D2_present, D2_value).**
   PRI 2010 did not publish atomic answers to these; we don't know whether the
   coder recorded them. Our scorer answers all of them, but the rollup **only
   uses C0 and D0** (per Table 5's 0–1 cap). The other answers are captured
   descriptively and have no effect on the score. This is consistent with PRI's
   stated scoring but is an implementation difference (we have more atomic data
   than PRI published).

8. **E h-frequency interpretation.** The paper's exact wording — *"1 point for
   reporting of lobbying data based on intervals of less than three times a
   year"* — is ambiguous. We read it as "monthly / quarterly / tri-annually
   qualify" (see "Source citations" for E above). If PRI meant the literal
   reading (semi-annual and annual earn the point, because they are "less than
   three times a year" in the count-intervals-per-year sense), our rule
   systematically disagrees. A baseline run with near-universal E h-disagreement
   would be the signal to revisit this.

9. **Confidence / `unable_to_evaluate`.** PRI 2010 published every atomic
   answer as 0 or 1 — no concept of uncertainty. Our scorer can emit
   `unable_to_evaluate=True, score=null`; nulls propagate through the rollup;
   null sub-aggregates count as disagreement against PRI numeric. Calibration
   runs should report the null-rate per sub-component separately so we can
   distinguish "scorer disagreed with PRI" from "scorer refused to answer".

---

## Known limitations of this rule

1. **Q8_raw has no atomic decomposition.** PRI's paper never specifies how to arrive
   at a 0–15 score for Q8 ("simultaneous sorting"). The 2026 rubric (see
   `pri_2026_accessibility_rubric.csv` Q8 scoring_guidance) proposes "count of Q7
   sub-criteria combinable in one search" — but that's a 2026-era interpretation.
   For 2010-vintage calibration, Q8 will be scored by the LLM as a single ordinal
   judgment, same as PRI's human coder did. Divergence here is expected and
   informative.

2. **No atomic-level PRI ground truth exists** at the item level. The 2010 paper
   only publishes sub-aggregate sums. This rule therefore **cannot** be verified
   against per-item PRI scores — only against the structural invariants:
   (a) sub-component sum to total reconciles, (b) each sub-component's max under
   this rule matches Table 5/Table 6 column caps, (c) every observed sub-aggregate
   falls within [0, column_cap]. All three hold.

3. **The "exceptions" list in the paper (F, G, J)** is described in paragraph form
   rather than formula. Our interpretation — F/G items sum across E1+E2, J is a
   single E1-side binary — is the only reading consistent with a max of 20. If
   PRI actually intended something different (e.g., "higher of E1f or E2f per
   sub-item"), the effective max would be < 20 and a state scoring 18 or 20 would
   be unreachable. The data rules that out.

4. **B_gov_exemptions rule produces 0–4 max**, but no state in Table 5 scores 4.
   The paper does not claim all four B questions are answerable together — it is
   structurally possible but empirically unrealized. This is consistent with the
   rule, not evidence against it.

---

## Verification plan

Before merging this spec to `main`, add a regression test:

```python
def test_rollup_rule_consistent_with_pri_totals():
    """For every state in pri_2010_disclosure_law_scores.csv,
       A + B + C + D + E must equal total_2010."""
    # This is a reconciliation of PRI's published columns against PRI's published
    # total — already verified by the prior session. We re-assert it here so this
    # spec's arithmetic claim (max 37 = 11+4+1+1+20) stays coupled to the data.
```

This is a structural check only — it does not verify the atomic-to-sub-aggregate
rule (which requires atomic-level ground truth we don't have). The atomic rule's
correctness can only be demonstrated by running the scorer against statute text,
applying this rollup, and showing agreement with PRI's sub-aggregates under a
calibrated prompt.

---

## Implementation location

Proposed: `src/scoring/calibration.py` functions

- `rollup_disclosure_law(atomic_scores: dict[str, int | None]) -> DisclosureSubAggregates`
- `rollup_accessibility(atomic_scores: dict[str, int | float | None]) -> AccessibilitySubAggregates`

Where `DisclosureSubAggregates` is a pydantic model with fields
`A_registration, B_gov_exemptions, C_public_entity_def, D_materiality,
E_info_disclosed, total`. Same shape for accessibility.

Null handling: if any item needed for a sub-aggregate is None
(`unable_to_evaluate=True`), the sub-aggregate is None. The agreement metric
treats None as a disagreement against PRI numeric.

---

## Sign-off

| Aspect | Status |
|--------|--------|
| Rule derivation from paper text | Complete, every rule line-cited |
| Max arithmetic checks against Table 5 / Table 6 | ✓ |
| Structural reconciliation (A+B+C+D+E = total) | ✓ per prior-session transcription |
| Atomic-level verification | Not possible (no atomic ground truth) |
| Dan sign-off | Pending |

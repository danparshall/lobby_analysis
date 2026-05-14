# Newmark 2005 — Item Extraction

## 1. Paper

Newmark, Adam J. 2005. "Measuring State Legislative Lobbying Regulation, 1990–2003." *State Politics and Policy Quarterly* 5(2): 182–191.

In Newmark's own framing: "I construct a replicable measure of lobbying regulation that is based on factors that influence the relationship between lobbyists and legislators, rather than one that includes all available indicators of lobbying restrictions and reporting requirements" (lines 58–61). The index is built from *Book of the States* data covering six time periods (1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003) and is presented as the first "simple, replicable index of lobbying regulation that is comparable across states and over time" (lines 44–46). The aim is to enable scholars to assess "a variety of hypotheses about the legislative process" (line 14–15) where prior work had been "hindered by the lack of a measure of lobbying regulation that is comparable across states and over time" (lines 27–29).

## 2. Methodology

**Data source.** Endnote 1 (lines 833–834): "All data were obtained from *The Book of the States* for each time period with the exception of penalties, the source of which is described below." (BoS data is biennial except 2002 and 2003, which are annual — endnote 2.)

**Sample.** All 50 states (47 for the penalty add-on; data not available for Colorado, Tennessee, West Virginia per endnote 8).

**Time coverage.** Six panels: 1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003.

**Item selection logic.** Indicators are chosen because they bear on "the legislator–lobbyist relationship" (lines 49, 58–60). Lobbyist *compensation*, for example, is excluded as not relevant to that relationship (lines 62–64).

**Scoring rule (main 0–18 index).** Every component is binary: "Each of these components is coded 1 if the state considers a given behavior as lobbying and 0 otherwise" (lines 122–123) and, for the prohibited/disclosure components, "each of these categories was coded 1 or 0 depending on whether the state had such a requirement. The values for all of these potential regulations were summed in each state in each time period to create an index of lobbying regulation with a possible range of 0 to 18" (lines 148–151).

**Reliability/validity diagnostics (lines 156–163).** Correlation with Opheim (1991) at 1990–91 = 0.84 (p<0.01). Correlation between Newmark 1990–91 and 2003 = 0.46 (p<0.01). Cronbach's α = 0.71 on "the 17 components of my index that went into the 2003 measure" (line 160) — endnote 5 explains: "There were a total of 18 components but one of the deﬁnition components was removed because it was constant across states" (lines 847–848). Newmark does not say which definition component was constant.

**Penalty add-on (lines 740–765).** A separate ordinal 1–4 score, scored only for 2003, derived from direct reading of state codes (not BoS). Combined with the 2003 main score in Table 1's "2003 score (plus penalties)" column, but listed in parentheses — i.e., the 18-item index and the penalty score remain conceptually separate.

## 3. Organizing structure

Newmark's own grouping (verbatim from lines 110–113 and the body of the methodology section):

| Category (Newmark's wording) | Item count |
|---|---|
| Statutory definitions ("statutory deﬁnition" / "deﬁnitions component") | 7 |
| Frequency of registration and reporting ("frequency of reporting requirements") | 1 |
| Prohibited activities | 4 |
| Disclosure requirements | 6 |
| **Subtotal — main 0–18 index** | **18** |
| Penalties (separate add-on, 2003 only, ordinal 1–4) | 1 composite |

This is **four** categories in the main index, not three — FOCAL's secondary description ("Definitions; frequency of reporting requirements; prohibited activities; disclosure requirements") matches the paper exactly but FOCAL miscounted them as "3 categories." Frequency is its own category in the paper (only one item, but treated as a separate "additionally" addition at lines 123–127 — distinct from definitions).

## 4. Indicator count and atomization decisions

**Total in 0–18 index: 18 items.**

**Plus 1 penalty composite (ordinal 1–4):** treated as a separate item in the TSV with explicit `notes` flagging that it is *not* part of the 18-point sum. Total rows in TSV = 19.

**Atomization judgment calls:**

- **`freq_reporting_more_than_annual`** — Newmark frames this as one item. The paper's underlying language ("registration and reporting") could suggest two separate frequencies (registration cadence vs reporting cadence), but Newmark scores them as a single binary, so I left them as one item. Flagged in `notes`.
- **Prohibited campaign contributions** — the paper splits into two items ("at any time" vs "during the legislative session"). I preserved the split exactly as written.
- **Total vs categorical compensation, total vs categorical expenditures** — the paper enumerates these as four separate disclosure items (total expenditures, categories of expenditures, total compensation, compensation by employer). I preserved all four.
- **Penalty composite vs sub-components** — Newmark describes several factors that feed into the 1–4 penalty score (felony vs misdemeanor classification of gift-ban/prohibited-activity/disclosure violations; failure-to-file penalties; failure-to-register; false-statement penalties; size of fines; length of prison sentences). He never publishes a sub-rubric mapping these to 1/2/3/4. I represented the penalty score as a single ordinal item rather than fabricating sub-items. Flagged in `notes`.

**Endnote 5 anomaly.** One of the seven definition components was "constant across states" in 2003 and was removed for the Cronbach's α calculation (yielding 17 components). Paper does not identify which component. Index itself is still 18 components — the constant variable still contributes 0 to every state's score. I retained all seven definition items in the TSV with a note on `def_expenditure_standard` flagging the ambiguity (could equally be flagged on any of the seven).

## 5. Frameworks cited or reviewed

By name, in this paper:

- **Opheim (1991)** — predecessor index; correlation diagnostic uses it.
- **Brinig, Holcombe, and Schwartzstein (1993)** — "ad hoc measures."
- **Gray and Lowery (1998)** — "ad hoc measures."
- **Rosenson (2003)** — "ad hoc measures"; cited later for ethics-commission authorization.
- **Newmark (2003)** — Newmark's own dissertation; correlates 0.70 with the 2003 index per endnote 4.
- **National Conference of State Legislatures** (named in endnote 6 as a URL pointer to lobbying/ethics laws).
- **Center for Public Integrity** (endnote 6, URL pointer).

Other works cited but not as measurement frameworks: Hunter/Wilson/Brunk (1991), Lowery and Gray (1997), Rosenthal (2001), Goodman/Holp/Ludwig (1996), Ensign (1997), Grimm (2003), Augusta Chronicle (1997).

## 6. Data sources — paper-defined vs BoS-defined vs fallback

**Critical for this paper.** Newmark's own framing makes the dependency explicit (endnote 1, line 833): *all* main-index data comes from *Book of the States*. The paper supplies the **scoring rules** (1/0 binary, sum) but the **operational definitions** (what counts as "legislative lobbying" in state X, what threshold for "expenditure standard," whether state X "has" a prohibition on session-time contributions) live in BoS.

Breakdown of the 18 main-index items:

- **18/18 BoS-defined operationally.** Every item's substantive definition lives in BoS. Newmark names the variable, applies a binary scoring rule, and sums.
- **0/18 paper-defined operationally.** The paper does not enumerate any thresholds (no dollar amounts for the expenditure standard, no time-period for the time standard, no specific cadence cutoff beyond "more frequently than once per year").
- **Paper-defined elements:** the *scoring scheme* (binary, sum to 0–18), the *frequency cutoff* ("more frequently than once per year" vs "once per year or less" — line 125–127), and the *category structure* (which items belong to definitions vs disclosure vs prohibited).

The penalty add-on (1 item, 2003 only) is the **lone exception**: it is paper-coded from direct statute reading (lines 753–763, "I conducted a thorough examination of the state codes" / "after three examinations of their 2003 statutes"). However, Newmark provides no transparent sub-rubric — only general considerations (felony vs misdemeanor classification per endnote 7, fines, prison sentences, failure-to-file/register/false-statement penalties). So the penalty score is paper-sourced but not paper-rubricized.

**Bottom line: 18/18 = 100% of main-index items are BoS-defined operationally; 1 supplementary penalty composite is paper-sourced but underspecified.** This is the same dependency pattern Opheim (1991) showed — Newmark explicitly aligns with that approach ("Similar to Opheim's (1991) measure," line 117).

## 7. Notable quirks / open questions

- **Which definition component is "constant across states"?** Endnote 5 says one of the seven was constant in 2003 and removed for the α calc, but does not name it. Likely candidate: `def_legislative_lobbying` (every state arguably regulates this) — but unverifiable from this paper alone.
- **"Registration and reporting" conflated.** The frequency item bundles two different cadences. A state requiring annual registration but quarterly reporting (or vice versa) gets a single binary score; the paper does not say which dominates.
- **Penalty composite is opaque.** The 1–4 ordinal lacks a published sub-rubric. Newmark mentions felony/misdemeanor classifications, fine sizes, prison-sentence lengths, and several failure-to-X categories but never maps them to specific scores. Three states (CO, TN, WV) are missing.
- **Range claim vs observed.** The paper says possible range is 0–18 (line 151). Observed 1990–91 range is 1–14; observed 2003 range is 1–17 (lines 169, 172). No state hits 18, and no state hits 0. The "constant" definition component (endnote 5) is consistent with a guaranteed-positive score in every state.
- **Frequency item scoring asymmetry.** Reporting "once per year or less" and "more frequently than once per year" — a state with biennial reporting and a state with quarterly reporting differ on this axis but only the binary cut at "more than once per year" matters. Cadence sub-distinctions are lost.
- **No enforcement variable.** The conclusion (lines 822–824) explicitly notes: "the vigor of their enforcement also affects this, and my index does not take this into account." Penalty stringency is the closest the paper gets, and only for 2003.
- **Compensation logic asymmetry.** Lobbyist compensation is excluded from the prohibited-activities/definition logic ("how lobbyists themselves are compensated would not be" relevant — line 64), but compensation *disclosure* (total compensation, compensation by employer) is included as two of the six disclosure items. Whether this is internally consistent is a fair question — disclosure of compensation could plausibly affect the relationship via media scrutiny (which is the paper's stated mechanism for disclosure regs at lines 99–108).
- **FOCAL miscount.** FOCAL's secondary description says "18 items in 3 categories"; the paper has 18 items in **four** categories (definitions / frequency / prohibited / disclosure). The four-category count is unambiguous in the body text.

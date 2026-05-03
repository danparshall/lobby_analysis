# Newmark 2017 — Source Extract

Companion to `items_Newmark2017.tsv`. All line refs are to `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`.

## 1. Paper

**Citation.** Newmark, Adam J. 2017. "Lobbying regulation in the states revisited: What are we trying to measure, and how do we measure it?" *Interest Groups & Advocacy* 6(3): 215–230. doi:10.1057/s41309-017-0023-z. (Author at Appalachian State University.)

**Framing.** The paper is the explicit follow-up to Newmark (2005) — a "theoretically sound, valid, and replicable measure of lobbying regulation" (line 425) covering all 50 states as of 2015. Newmark argues that the field has accumulated "a multitude of measures that often assess very different constructs" (line 12), and that the abandoned-since-2005 *Book of the States* (BoS) categories remain the right theoretical scaffold but require independent re-coding from primary sources because BoS data were self-reports with documented errors. The headline contribution is the **2015 lobbying regulation index** built from 19 binary components in three categories — Definitions, Prohibited activities, Disclosure/Reporting — with state scores reported in Table 2 alongside the 2003 BoS scores from Newmark 2005 and a four-factor analysis in Table 3.

The paper is also a survey of competing measures (Sunlight Foundation, Center for Public Integrity, Pacific Research Institute) and reports cross-rubric correlations to argue that these measures are not interchangeable.

## 2. Methodology

**Item construction.** 19 binary (1/0) indicators chosen from BoS categories, plus statute review for verification. Newmark explicitly distrusts the BoS self-reports: "Based on my review of data provided in the 2005 BOS, I concluded that there were several errors in the self-reported state lobbying data" (line 544). The 2015 re-coding came from "an examination of state statutes, constitutional provisions where applicable, and review of materials from relevant departments or agencies responsible for lobbying oversight (e.g., Secretaries of State offices and Ethics Commissions)" (lines 433–435).

**Sample.** All 50 states. Year of data: 2015 (the article's data are labeled "2015 index" throughout Table 2). Author with research assistance from Sarah Smithers (line 1048).

**Scoring rule.** "each of the above 19 categories was given a 1 if the state included the provision and a 0 if it did not, and the categories were then summed to create an index assessing the level of lobbying regulation in each state." (lines 555–558).

**Composite rule.** Simple unweighted sum, range 0–19 in principle. Observed range: "ranges from 7 to 19, with a mean of 12.96 and standard deviation of 2.63. The Cronbach's alpha for the 19 components is a less than ideal 0.67." (lines 565–567). Top scorers: Kentucky (19), Colorado (18), California, Arizona, Maine, Massachusetts, Wisconsin (16). Bottom: Wyoming, North Dakota (7), Nevada (8), South Dakota, Florida (9).

**Factor structure.** Newmark explicitly rejects a clean three-category factor model. "Factor analysis reveals that there are likely multiple dimensions in state lobbying regulations, and there are between four and six factors depending on the factor model utilized and the eigenvalue cut-points" (lines 849–851). The Appendix Table 3 reports a four-factor varimax-rotated PCA solution; loadings ≥0.3 are recorded in `notes` for each item. Two items are excluded from factor analysis "because there is no variation in these categories" (line 1162) — `def.legislative_lobbying` and `disclosure.expenditures_benefiting_officials`.

**Cross-rubric correlations Newmark reports (verbatim, with line refs).** These are the empirical basis for treating the existing rubrics as measuring different constructs:

- *PRI disclosure ↔ PRI accessibility:* "the correlation between the two PRI rankings is only 0.25." [line 416–417]
- *CPI disclosure ↔ PRI disclosure:* "Surprisingly, even the disclosure measures constructed by CPI and PRI are unrelated (Pearson's r = 0.04). Despite some common components, these organizations actually measure disclosure in different ways." [lines 421–423]
- *Newmark 2015 ↔ Sunlight Foundation:* "The new measure correlates with the Sunlight Foundation score at 0.4." [line 945]
- *Newmark 2015 ↔ CPI:* "The new measure correlates with the CPI measure at 0.52, which is not surprising given some of the commonalities across the two measures." [lines 953–954]
- *Newmark 2015 ↔ PRI accessibility:* "the new index is only weakly correlated with the PRI accessibility index (r = 0.27)" [lines 954–955]
- *Newmark 2015 ↔ PRI disclosure:* "it is generally unrelated to the PRI disclosure index. Given that the PRI measure is unrelated to the new measure and the CPI measure, it is safe to say that it is measuring something different." [lines 955–958]
- *Newmark 2015 ↔ Newmark 2003 BoS:* "The relationship between the new measure and Newmark's (2005) data from 2003 derived from The Book of the States is moderate (r = 0.54), reflecting the fact that the measures are derived from most of the same categories, but some states have adjusted their lobbying laws more than others during the past 12 years." [lines 571–574]

These correlations are why Newmark concludes "scholars should not blindly incorporate measures of lobbying regulation without first considering the theoretical justification" (lines 1027–1028) — and they directly support the project's choice not to privilege any single predecessor (including PRI) as the calibration anchor.

## 3. Organizing structure

Newmark uses **three categories**, matching FOCAL's count exactly:

| Category | Items | Notes |
|---|---|---|
| Definitions of lobbyists and registration requirements | 7 | Reported as "2015 definitions" column in Table 2; per-state range 1–7 |
| Prohibited activities | 5 | Reported as "2015 prohibited activities" column; per-state range 0–5 |
| Registration and reporting/disclosure requirements | 7 | Reported as "2015 disclosure/reporting" column; per-state range 2–7 |
| **Total** | **19** | Matches Newmark's own count: "each of the above 19 categories" (line 555) |

FOCAL's claim of "19 items in 3 categories" is **exactly correct**. No discrepancy.

## 4. Indicator count and atomization decisions

**19 atomic items + 3 sub-aggregates + 1 overall index = 23 rows in TSV.** Atomic count matches FOCAL.

Atomization judgment calls:

1. **`def.compensation_standard` / `def.expenditure_standard` / `def.time_standard`** — Newmark groups these in a single sentence ("compensation, expenditure, and time standards") at line 524, but then says each "is coded 1 if the state includes the provision in its definition of a lobbyist and 0 otherwise" (lines 525–526). The Table 2 "2015 definitions" column reaches a maximum of 7, which is only achievable if these three are separate items. Confirmed by Table 3 factor analysis listing each on its own row with distinct factor loadings. Split into three.
2. **`def.elective_officials_as_lobbyists` vs. `def.public_employees_as_lobbyists`** — Newmark gives these as two separate items in his enumeration (line 517) and Table 3, even though the prose discussion (line 519–521) sometimes lumps them ("Some states require elected officials and public appointees to register"). Kept separate per the explicit enumeration.
3. **`prohib.contributions_anytime` vs. `prohib.contributions_during_session`** — Two distinct items in Newmark's enumeration (lines 529–531) and Table 3. The "during session" item is a stricter sub-case but coded independently. Kept separate.
4. **`disclosure.compensation_by_employer` vs. `disclosure.total_compensation`** — Two items in the enumeration (line 542–543) and Table 3. The first is itemized-by-employer, the second is the total. Kept separate.
5. **`disclosure.categories_of_expenditures` vs. `disclosure.total_expenditures`** — Same pattern as compensation. Kept separate.

**Items with no variation across states (excluded from factor analysis but still in the index):**
- `def.legislative_lobbying` — "All 50 states require registration for lobbying the legislature" (line 518). Constant 1 across states.
- `disclosure.expenditures_benefiting_officials` — Table 3 footnote: "excluded because there is no variation in these categories" (line 1162).

Both still count toward the 19-item index per Newmark's own scoring rule, but they contribute zero variance.

## 5. Frameworks cited or reviewed

Names only (project rule: do not cross-reference content from other papers):

- **Council of State Governments — *Book of the States* (BoS)** — last collected 2005; Newmark's primary scaffold for category selection.
- **National Conference of State Legislatures (NCSL)** — categories: definition of lobbying/lobbyists, reporting requirements, registration and identification, use of public funds, plus indirect-regulation categories (general ethics, financial disclosure, gift restrictions, conflict of interests, oversight).
- **Sunlight Foundation (SF)** — letter-grade scoring on lobbying activity, expenditure transparency, expenditure reporting thresholds, document accessibility, lobbyist compensation, state lobbying laws.
- **Center for Public Integrity (CPI)** — State Integrity Investigation, 13 categories including lobbying disclosure.
- **Pacific Research Institute (PRI)** — two indices: disclosure (registration requirements, government exemptions, public-entity materiality test, lobbying information disclosure) and accessibility (data availability, website score, website ID, current/historical data availability, data format, sorting data, simultaneous sorting score).
- **Newmark 2005** — direct predecessor; the 2003 BoS-based measure compared against the 2015 measure.
- **Opheim 1991** — cited as historical antecedent.
- Other works cited but not used as measurement rubrics: Brinig et al. 1993; Hunter et al. 1991; Lowery & Gray 1997; Gray & Lowery 1998; Rosenson 2005; Ozymy 2010, 2013; Strickland 2014; Flavin 2015; Holman & Luneburg 2012; Hogan et al. 2008; Mihut 2008; LaPira & Thomas 2014; Witko 2005, 2007; Vaughan & Newmark 2008.

## 6. Data sources (paper-defined vs BoS-defined vs fallback-defined)

**Newmark 2017 is BoS-lineage in its category structure but paper-coded for actual values.** From the paper itself: "the categories listed above are used in previous studies derived from the BOS" (line 551). The category and item set comes from BoS; the 2015 binary values come from Newmark's own statute review (lines 433–435). For dependent users of the index, the operational definition of each item is split:

| Layer | Source |
|---|---|
| Item *names* and *category structure* | **BoS** (Newmark 2005 lineage; reproduced from CSG *Book of the States* circa 2005) |
| Item *operational thresholds* (e.g., dollar values for compensation/expenditure standards, length of revolving-door wait) | **Not specified** by Newmark 2017. Paper records only presence/absence of "a" threshold; the dollar/time values themselves are not coded. |
| Item *2015 binary values* (per state) | **Paper-defined** — Newmark's review of state statutes and oversight-agency materials |
| Item *2003 binary values* (Table 2 last column) | **BoS-defined** — reproduced from Newmark 2005 / *Book of the States* 2005 edition |

So in TSV `notes`, every atomic item is flagged "BoS-derived" — meaning the *item itself* was lifted from the BoS taxonomy that Newmark 2005 had previously used. The 2015 *scoring* is paper-defined.

## 7. Notable quirks / open questions

- **Cronbach's alpha 0.67 is below the conventional 0.7 threshold for scale reliability.** Newmark calls this out himself ("a less than ideal 0.67", line 566). This is consistent with his factor-analytic finding that the index is multi-dimensional rather than a single coherent construct.
- **Factor analysis explicitly contradicts the three-category structure.** Newmark reports 4–6 factors depending on cut-point. The reported four-factor solution mixes definitional and disclosure items in factors 1 and 4, prohibited and disclosure items in factors 2 and 3. "the data do not organize neatly along a preconceived structure" (line 867). This is a substantive finding, not a measurement artifact.
- **Two items have no cross-state variation in 2015** (`def.legislative_lobbying` always 1; `disclosure.expenditures_benefiting_officials` constant). They contribute zero discrimination but still count toward the index sum. For replication, they can be dropped without changing state rankings.
- **No threshold values are coded.** The compensation/expenditure/time standards are scored 1 if "a" threshold exists, regardless of how strict. A state with a $1 threshold and a state with a $5,000 threshold both score 1. Same for revolving-door cooling-off period (Florida's 2-year and a hypothetical 1-day rule both score 1). For the lobby_analysis project, this is a key gap: any framework that wants to compare *strictness* (rather than presence) of these provisions cannot rely on Newmark 2017 alone.
- **`prohib.solicitation_by_officials` is a demand-side item in a supply-side category.** It restricts what officials can do (solicit), not what lobbyists can do. Newmark explicitly notes elsewhere "lobbyists can be constrained indirectly by disrupting the demand" (line 1015–1017). This item conceptually belongs to a separate "official conduct / ethics laws" axis rather than to lobbying regulation per se. Worth flagging for compendium framework design.
- **Spelling note in source quote:** the paper uses "benefitting" (double-t, line 541) and "compensations" (plural, line 543) for what Table 3 lists as "benefiting" and "total compensation". Same constructs.
- **Newmark 2017 ≠ Newmark 2005.** The 2017 paper uses 19 components; Newmark 2005 had a different (larger) component set per the Table 2 footnote ("not directly comparable, given that they are based on slightly different components", lines 562–564). When other papers cite "the Newmark measure," care is required to identify which vintage.

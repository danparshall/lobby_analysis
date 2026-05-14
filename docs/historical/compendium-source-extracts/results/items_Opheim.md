# Opheim 1991 — Indicator Extraction

## 1. Paper

Opheim, Cynthia. 1991. "Explaining the Differences in State Lobby Regulation." *Western Political Quarterly* 44(2): 405–421. (Received December 6, 1989; revision received March 28, 1990; accepted for publication April 3, 1990.)

**What Opheim claims to be measuring.** Opheim builds an "index of lobby regulation" as a dependent variable to "measure the stringency with which states regulate organized lobbies" (line 87–88). The index is meant to operationalize "the rigor of the state's formal regulation of lobbyists" as the "most straightforward measure of legislative independence from interest group pressure" (lines 6–8). The index "consisted of 22 separately scored items drawn from three different dimensions of lobby regulation requirements": (1) "statutory definition of a lobbyist (seven items)," (2) "frequency and quality of disclosure (eight items)," and (3) "oversight and enforcement of regulations (seven items)" (lines 89–94). Higher scores indicate more stringent regulation.

## 2. Methodology

- **Sample.** 47 states. "Data for Montana, South Dakota, and Virginia were unavailable" (Table 1 caption, line 176).
- **Year of data.** 1988–89 (per the Blue Book and Book of the States editions cited in footnote 1, lines 120–124).
- **Scoring rule.** "The sum of all 22 items indicated the state's index score" (line 151). Each item dichotomously coded except two (frequency of reporting; thoroughness of reviews) where, even though more granular distinctions are present in source data, Opheim collapsed to 0/1 — explicitly acknowledging "for two items — frequency of reporting and thoroughness of reviews — some finer distinction is lost in the simple 0/1 coding procedure" (lines 152–154). Justification given: "following Herzik's example, by sampling different items within general categories, the basic concepts embodied in each of the three categories are tapped by several specific variables. Dichotomous coding also eliminates much of the arbitrariness in attempting to create finer distinctions" (lines 154–159; cites Herzik 1985: 417).
- **Aggregation.** Simple unweighted sum across 22 items. Range therefore 0–22; observed range in Table 1 caption is "0 - weakest / 18 - strongest" (line 174).
- **No section weights, no factor analysis.** Sections are conceptual groupings, not separately weighted in the index.
- **No inter-coder reliability reported.** A single coder (the author) is implied; the only reliability check mentioned is for an *independent* variable (staff support measure correlated r=.63 with Simon 1979; lines 280–282).

## 3. Organizing structure

Opheim uses three categories, exactly as quoted in lines 92–94:

| Section (verbatim Opheim phrasing) | Item count |
|---|---|
| "statutory definition of a lobbyist" | 7 |
| "frequency and quality of disclosure" | 8 |
| "oversight and enforcement of regulations" | 7 |
| **Total** | **22** |

These three labels are Opheim's own (not borrowed from FOCAL or any later paraphrase); the parent task's named labels match Opheim's prose verbatim except for sentence-case adjustments.

## 4. Indicator count and atomization decisions

**Total atomic items: 22.** Plus 3 section composites and 1 overall index composite = **26 rows in the TSV**.

Atomization judgment calls:

- **Definition section, "compensation, expenditure, and time standards" (one sentence, lines 107–109).** Split into 3 separate items (`def.compensation_standard`, `def.expenditure_standard`, `def.time_standard`). Justification: Opheim says the section has 7 items, and the only way to reach 7 is by splitting these — there are 4 other inclusion criteria named in the same paragraph (legislative lobbying, administrative lobbying, elective officials, public employees), and 4 + 3 = 7.
- **Enforcement section, "impose administrative fines, impose administrative penalties" (one sentence, line 148).** Kept as 2 separate items (`enforce.impose_administrative_fines`, `enforce.impose_administrative_penalties`) per Opheim's own enumeration ("Six items measure the rigor of this authority"; the six items are listed and these appear as distinct entries). Distinction between "fines" and "penalties" is not explained in the paper. Flagged in TSV `notes`.
- **Enforcement section, item count.** Opheim says the section has 7 items (line 94) but the prose says "Six items measure the rigor of this authority" (line 145). The 7th item is the *thoroughness of reviews* item described in the preceding paragraph (lines 135–142), which sits in this section but is not part of the "prosecutorial authority" sub-cluster. Flagged in TSV `notes` for `enforce.section_total`.
- **Disclosure section, frequency item.** Treated as a single item even though it is *categorical* not *boolean* in source data (monthly / both in-out / quarterly / semi-annually / annually). Opheim collapses it 0/1; we keep it as one row but mark `indicator_type: categorical` with the collapse rule recorded in `scoring_rule`.
- **Disclosure, "expenditures benefitting public employees including gifts."** Treated as a single item, not split into "expenditures benefitting public employees" + "gifts." The "including gifts" appears to be a clarifying clause within one disclosure category in the source data, and Opheim uses singular grammar.
- **Composites.** Added 4 composite rows (`index.total`, `def.section_total`, `disclosure.section_total`, `enforce.section_total`) because the task instructions require composite rows alongside their sub-items, with aggregation rules in `notes`.

## 5. Frameworks cited or reviewed

Opheim is from 1991 — there are very few prior *rubrics* of state lobbying regulation to cite, and Opheim cites essentially none as direct predecessors of his index. The only methodologically analogous index Opheim explicitly leans on is **Herzik 1985** ("openness of government structures") — for the dichotomous-coding-within-categories approach, not for any item content (lines 154–159, citing Herzik 1985: 417).

**Substantive citations to prior lobbying-regulation work** (used for context, not for items):

- **Citizen Conference on State Legislatures (CCSL) 1971a, 1971b** — cited as the origin of the legislative-independence framing and reform agenda (lines 9–11, 17–21, 53–55, 202–206).
- **Rosenthal 1981** — descriptive baseline on registration / reporting / expenditures across states (line 30).
- **Allen and Clark 1981** — earlier-adopting wealthier states; lobbying-and-education state policy (lines 353, 526).
- **Huckshorn 1985** — enforcement of campaign finance laws in the states (line 45).

**Theoretical / methodological citations** (independent-variable construction, not the lobby index):

- **Elazar 1984** and **Sharkansky 1969** — political culture (Sharkansky's 9-point operationalization is used).
- **Grumm 1971; Carmines 1974; Morehouse 1981; Squire 1988; Bowman and Kearney 1988; LeLoup 1978; Roeder 1979** — legislative professionalism.
- **Simon 1979** — alternative staff measure used for reliability check (r=.63).
- **Council of State Governments Book of the States 1988–89** and **CSG Blue Book 1988–89** — primary data sources (see §6).
- **ACIR 1985** — tax capacity.
- **Ranney 1976** (per Bibby et al. update) — interparty competition index.
- **Karnig and Sigelman 1975; Fitzpatrick and Hero 1988; Joslyn 1980; Welch and Peters 1980; Lowery and Sigelman 1982; Ritt 1974; Peters and Welch 1978; Kincaid 1980; Nice 1983** — political-culture-and-policy evidence.
- **Dye 1966; DeLeon 1973; Walker 1969** — economic-resources-and-policy literature.

No earlier *rubric/index of lobbying disclosure regulation* is cited. Opheim's index appears to be a de novo construction.

## 6. Data sources

**Critical caveat: Opheim's index is almost entirely a re-coding of CSG-published reference tables, not a direct reading of state statutes.** Per footnote 1 (lines 120–124, verbatim):

> "All data, with the exception of frequency of reporting requirements, were coded from the Council of State Government's Blue Book 1988-89, Campaign Finance, Ethics and Lobby Law: Special Edition (Lexington, Ky.: Council of State Governments, 1988). Data indicating frequency of reporting requirements were taken from Council of State Governments, The Book of the States, 1988-89."

This means:

| Item set | Operational source |
|---|---|
| 7 definition items | CSG **Blue Book 1988–89** (Campaign Finance, Ethics and Lobby Law: Special Edition) |
| 1 disclosure-frequency item | CSG **Book of the States, 1988–89** |
| 7 disclosure-content items | CSG **Blue Book 1988–89** |
| 7 enforcement items (1 thoroughness + 6 prosecutorial-authority) | CSG **Blue Book 1988–89** |

**21 of 22 items are CSG Blue Book–defined; 1 of 22 is CSG Book of the States–defined.** Zero items are defined by Opheim's own statute reading. Every TSV row is flagged `BoS-defined` (or Blue Book–defined) in `notes`. The user should treat Opheim's "indicator definitions" as effectively the row/column structure of two 1988–89 CSG reference tables that are not reproduced in the paper. Without those CSG sources, the precise coding decisions for any given state cannot be reconstructed from Opheim alone.

Practical consequence for the compendium rebuild: Opheim's labels (e.g., "specific compensation standard," "spending by category," "other activities that might constitute influence peddling or conflict of interest") are *category names* from the CSG Blue Book that Opheim does not redefine. Threshold values (e.g., what dollar amount of compensation triggers a "yes"; what counts as a sufficient "category") are not in Opheim's text and presumably live in the CSG source.

## 7. Notable quirks / open questions

1. **Two items collapsed from finer source granularity.** `disclosure.frequency` and `enforce.thoroughness_of_reviews` are categorical/ordinal in the underlying CSG data but Opheim coded them dichotomously. The TSV preserves this by using `indicator_type: categorical` with the collapse rule in `scoring_rule`, and flags both in `notes`. Anyone re-using Opheim's items can choose either Opheim's 0/1 collapse or the underlying multi-category granularity (the latter requires the CSG source).
2. **"Six items" vs "seven items" in enforcement section.** Opheim says the enforcement *section* has 7 items (line 94) but later says "Six items measure the rigor of this authority" (line 145). Reconciliation: the 7th is the thoroughness-of-reviews item. Not a contradiction once you read carefully, but easy to mis-count.
3. **`enforce.impose_administrative_fines` vs `enforce.impose_administrative_penalties`.** Both appear as distinct items in Opheim's enumeration. The conceptual distinction is undefined in the paper and is presumably whatever the CSG Blue Book table distinguished. May or may not be meaningful — flag for review.
4. **`disclosure.other_influence_peddling_or_conflict_of_interest` is a catch-all.** No operational definition in the paper. This is the single most under-defined item in the index.
5. **No tabular item list in the paper.** Items are described in prose only. There is no Table that enumerates the 22 indicators — Table 1 shows state rankings; Tables 2 and 3 show regression results. A reader has to atomize from prose. (This is the source of all atomization judgment calls.)
6. **No threshold values for definition standards.** Opheim refers to "specific compensation, expenditure, and time standards" as inclusion criteria but does not record what threshold any state used (e.g., "$X compensation," "Y days lobbying"). For state-level reproduction, CSG Blue Book 1988–89 would be required.
7. **Sample is 47, not 50.** Montana, South Dakota, Virginia missing per Table 1 caption (line 176). Alaska and Hawaii also missing from Sharkansky's culture measure (footnote 4, line 363) — affects the regression but not the index construction itself.
8. **The index is computable from any state's statutes today,** but the *coding instructions* in Opheim are minimal — anyone re-applying the index to current statutes must either (a) infer Opheim's intent from CSG's 1988–89 framing or (b) define their own thresholds for compensation/expenditure/time standards, which would diverge from Opheim's actual coding.

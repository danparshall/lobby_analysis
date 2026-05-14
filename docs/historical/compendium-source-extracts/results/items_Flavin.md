# Flavin 2015 — Source Extract

Companion to `items_Flavin.tsv`. All line refs are to `papers/text/Flavin_2015__lobbying_regulations_political_equality.txt`.

## 1. Paper

**Citation.** Flavin, Patrick. 2015. "Lobbying Regulations and Political Equality in the American States." *American Politics Research* 43(2): 304–326. doi:10.1177/1532673X14545210. (Author at Baylor University; this draft January 28, 2014; line 16.)

**Framing.** The paper is an **empirical-use** study of whether stricter state lobbying regulations actually deliver their stated political-equality goal. Flavin's framing is normative-democratic — opening with the observation that "There is growing normative concern among social scientists, policymakers, and the general public about unequal political influence" (lines 54-60) and Dahl's claim that "The existence of political equality is a fundamental premise of democracy" (line 95). The paper's headline claim: "states with more stringent lobbying regulations tend to exhibit a weaker relationship between income and political influence" (lines 130-134) and "lobbying regulations can play an important role in promoting political equality" (lines 47-49, abstract).

The paper's contributions are (a) constructing a state-comparable Political Equality Index and (b) testing the regulation→equality link. It does **not** construct, re-code, or modify a lobbying-regulation rubric.

## 2. Methodology

**Empirical question.** "What effect, if any, does the strictness of lobbying regulations have on the content of actual policy decisions in the states?" (lines 239-242). Specifically: do states with stricter regulations exhibit a weaker income-to-opinion-policy-congruence relationship?

**State coverage.** 48 states. "Alaska and Hawaii were not surveyed, so all analyses in this paper report results from the remaining 48 states" (lines 390-392). N=48 in the regression (Table 4, line 1344).

**Time window.** Public-opinion / political-equality measure pools 2000, 2004, and 2008 NAES surveys (line 350). Lobbying-regulation measure is Newmark's 2000-2001 wave (lines 800-803). State policy liberalism measures are GLFM 2004 (using policy items from 1997-2001 era) and Sorens-Muedini-Ruger 2008 (lines 444-470). Income inequality is the 1999 Gini (line 819); electoral competition uses Holbrook-Van Dunk; for-profit interest-group share is the 1997 Gray-Lowery measure as updated by GLFM 2004 (lines 847-852). Effectively a 2000-2008 cross-section.

**Lobbying-regulation measure used.** **Newmark (2005) additive index, applied unchanged.** Verbatim:

> "The one important exception is Newmark's 2005 article in State Politics & Policy Quarterly that uses information on 'statutory definition, prohibited activities, and disclosure requirements (including the frequency of registration and reporting)' (184) to measure the strictness of state lobbying regulations. Specifically, Newmark creates an additive index for each state ranging from zero to eighteen (with higher numbers indicating more regulations) that catalogues the number of different groups required to register as lobbyists, the frequency of reporting requirements, the types of activities that are prohibited, and disclosure requirements. Data is collected on a biennial basis from the Book of States for 1990-2003. Because the data on the equality of opinion-policy representation in the states are from the 2000-2008 timeframe, I use Newmark's additive measure of lobbying regulations for 2000-2001 that has a mean of 10.34, a standard deviation of 3.17, and ranges from 1 (North Dakota) to 17 (South Carolina) across the states." (lines 781-805)

There is no re-coding, no item addition, no item subtraction, no re-weighting. The index enters the right-hand side of the regression as a single scalar.

**Political-equality dependent variable construction.** This is Flavin's own measurement contribution. The construction is:

1. **Opinion data.** Self-reported political ideology from pooled 2000+2004+2008 National Annenberg Election Surveys, NAES item: "Generally speaking, would you describe your political views as very conservative, conservative, moderate, liberal, or very liberal?" coded -2 (very conservative) to +2 (very liberal) (lines 376-381). N=177,043 respondents (line 386). Sample size justifies state-level analysis without MRP simulation (lines 358-371).

2. **State policy-liberalism data.** Two composite indices used in parallel:
   - **GLFM 2004** = Gray, Lowery, Fellowes & McAtee 2004's update of Erikson-Wright-McIver, built from 5 components: state gun laws; abortion-laws scorecard 2000; TANF welfare stringency 1997-99; right-to-work 2001; tax progressivity (top 5% / bottom 40% tax-burden ratio). Standardized and summed; Cronbach's alpha .63 (lines 444-456, footnote 7).
   - **SMR 2008** = Sorens, Muedini & Ruger 2008's factor score over 20 policy areas (lines 462-471). Available at www.statepolicyindex.com (footnote 8). The two policy-liberalism measures correlate at .79 (footnote 9, line 491).

3. **Proximity (opinion-policy distance).** "Policy representation is measured using a proximity technique that places public opinion and policy on the same linear scale and compares the distance between the two (Achen 1978)" (lines 297-299). Three rescaling techniques are applied to make opinion and policy comparable:
   - *Standardized* (mean 0, SD 1 for both opinion and policy; Wright 1978 style; lines 510-525).
   - *Same Scale* (policy rescaled to -2 to +2 to match the 5-point ideology item; Miller 1964 / Achen 1978 / Burden 2004 / Griffin-Newman 2008 style; lines 544-555).
   - *Restricted Scale* (policy rescaled to -1 to +1, tighter than ideology, on the rationale that policy outputs have narrower range than citizen ideology; Powell 1982/1989 style; lines 557-568).

   Three techniques × two policy measures = **six different distance measures per respondent** (lines 570-574).

4. **Income → distance relationship.** State-relative income is computed (respondent income − state mean income) to neutralize cross-state cost-of-living and income-distribution differences (lines 592-600). For each state, regress opinion-policy distance on state-relative income, using each of the six distance measures. The slope coefficient is the within-state income-influence gradient. "A more steeply negative slope coefficient indicates a stronger relationship between income and ideological distance and, accordingly, less political equality" (lines 660-663).

5. **Political Equality Index.** Six within-state slope coefficients per state are combined into a single factor score via principal-components analysis. "The eigenvalue for the lone retained factor is 5.15 and explains 86% of the total variance" (footnote 14, line 738). Cronbach's alpha across the six measures is .96 (lines 695-697). The factor scores are sign-flipped so that "a more positive factor score indicates greater political equality (i.e. a more equal weighting of citizens' opinions)" (lines 705-708). State scores are reported in Table 3 (lines 1287-1311), ranging from Mississippi at -8.44 (least equal) to Montana at 4.51 (most equal).

**Main regression specification (Table 4, lines 1321-1352).** OLS of the Political Equality Index on:
- Lobbying Regulations (Newmark 2000-2001 score)
- Income Inequality (1999 state Gini, U.S. Census)
- Electoral Competitiveness (Holbrook & Van Dunk 1993)
- % Interest Groups For-Profit (Gray-Lowery 1996, updated 1997 by GLFM 2004)

N=48; R²=.32. Lobbying coefficient = 0.213 (SE 0.092, p<.05); substantive effect = +0.60 SD of the Political Equality Index when moving from −1 SD to +1 SD on regulation strictness — "the largest substantive effect on the equality of political representation" of any covariate in the model (lines 893-901). Robust regression (Column 3) gives 0.220 (SE 0.068, p<.01).

## 3. Organizing structure

Flavin uses **none of his own** structural categories for lobbying regulation. He does not enumerate, group, or categorize the components of Newmark's index. He treats Newmark's index as a single scalar covariate. His framing of "what regulation does" — when describing the construct in prose — paraphrases Ozymy 2010: "Legislative lobbying regulations structure the relationship between lobbyists and state legislators by defining lobbyists for purposes of registration, mandating reporting requirements, and creating prohibitions or limitations on gifts, rules for campaign contributions, and statutory definitions for conflicts of interest" (lines 769-776, quoting Ozymy 2010, 398). But this prose is description, not a rubric.

His **own** organizing structure is on the dependent-variable side: 3 rescaling techniques × 2 policy-liberalism sources × 50-state regressions → 1 PCA factor score per state.

## 4. Indicator count and atomization decisions

**Lobbying-regulation indicators contributed by Flavin: 0.** He applies Newmark's index as-is.

The TSV therefore has a single row (`uses.newmark_2005`) documenting the empirical-use relationship rather than a per-item decomposition. Atomizing Newmark's components from this paper would be inappropriate — Flavin does not enumerate them, score them, or analyze them individually. The atomization belongs to Newmark 2005 itself (or to Newmark 2017's re-coding); pulling it back through Flavin would double-count.

For completeness, the **dependent-variable side** of the paper has its own atomization (Political Equality Index = PCA over 6 income-slope coefficients per state; each slope is itself estimated from 1 of 2 policy measures × 1 of 3 rescaling rules), but this is not a lobbying-regulation indicator and does not belong in the compendium. It is documented above for context.

## 5. Frameworks cited or reviewed

For lobbying-regulation measurement specifically, Flavin cites **only Newmark 2005** as a measurement source. He acknowledges adjacent prior work on lobbying-regulation effects without using their measures:

- **Newmark 2005** — used as the regulation measure.
- **Opheim 1991** — cited as documenting cross-state regulation variation (line 109).
- **Brinig, Holcombe & Schwartzstein 1993** — cited for effects on bill-passage rates (lines 218-220).
- **Hamm, Weber & Anderson 1994** — cited for effects on interest-group population size (line 213).
- **Lowery & Gray 1993, 1997, 1998 / Gray & Lowery 1996, 1998** — cited for effects on interest-group community size and diversity (lines 213-217).
- **Ozymy 2010, 2013** — cited as the closest analogue ("one notable exception"); Ozymy 2010 measures legislator perceptions of group influence as the outcome (lines 220-237). Ozymy 2010's prose definition of lobbying regulations is quoted (lines 769-776) but Ozymy's measure is not used.
- **Rosenthal 2001** — cited for the qualitative description of state lobbying (lines 187-191).
- **Rosenson 2003, 2005** — cited for ethics-commission scholarship (lines 200-203).

For the political-equality / opinion-policy-proximity dependent-variable side, Flavin cites a much longer list (Achen 1978; Miller-Stokes 1963; Erikson 1978; Powell 1982, 1989; Bartels 1991, 2008; Clinton 2006; Page-Shapiro 1983; Erikson-Wright-McIver 1993; Erikson-MacKuen-Stimson 2002; Wlezien 2004; Burden 2004; Blais-Bodet 2006; Gershtenson-Plane 2007; Griffin-Flavin 2007; Griffin-Newman 2007, 2008; Jessee 2009; Powell 2009; Golder-Stramski 2010; Giger-Rosset-Bernauer 2012; Ellis 2012, 2013; Gilens 2005, 2012; Gilens-Lax-Phillips 2011; Rigby-Wright 2011, 2013; Flavin 2012; Wright 1978; Klingman-Lammers 1984; Gray-Lowery-Fellowes-McAtee 2004; Sorens-Muedini-Ruger 2008; Gelman-Park-Shor-Bafumi-Cortina 2008; Lax-Phillips 2009a/b; Park-Gelman-Bafumi 2006; Carsey-Harden 2010; Holbrook-Van Dunk 1993; Squire 2007; Dahl 1971, 2006; Verba 2003; Eulau-Karps 1977; Schattschneider 1960; Schlozman-Tierney 1986; Thomas-Hrebenar 1990; Cigler-Loomis 2007; Nownes 2001; Jacobs-Skocpol 2005; Hacker-Pierson 2010; Kelly 2009; Kelly-Witko 2012; Soss-Schram-Vartanian-O'Brien 2001; Brace-Jewett 1995; Barrilleaux-Holbrook-Langer 2002; Key 1949; Knight 1985; Jennings 1992; Jacoby 1995; Ellis-Stimson 2009).

## 6. Data sources

- **Lobbying regulation:** Newmark (2005), 2000-2001 wave. Newmark's source was the *Book of the States* (lines 796-799).
- **Public opinion:** 2000, 2004, 2008 National Annenberg Election Surveys (NAES); pooled N=177,043 (lines 348-355, 386).
- **State policy liberalism #1:** Gray, Lowery, Fellowes & McAtee 2004 — built from 5 policy items (gun, abortion, TANF, right-to-work, tax progressivity) (lines 444-456).
- **State policy liberalism #2:** Sorens, Muedini & Ruger 2008 — composite factor over 20 policy areas (lines 462-471, www.statepolicyindex.com).
- **Income inequality:** U.S. Census Bureau, state Gini for 1999 (lines 817-819, footnote 15).
- **Electoral competitiveness:** Holbrook & Van Dunk 1993 index (lines 833-839).
- **Interest-group composition:** Gray & Lowery 1996, 1997 update by GLFM 2004 — % of organized groups that are for-profit (lines 846-852). Acknowledgment line: "Thank you to Virginia Gray for state interest group data" (line 22).

## 7. Notable quirks / open questions

**(a) The political-equality DV is itself a measurement contribution worth noting separately.** Flavin's *Political Equality Index* is a PCA-summarized within-state income-to-opinion-policy-distance gradient. Mississippi -8.44, Alabama -5.06, Georgia -3.56 at the bottom; Montana 4.51, Minnesota 3.23, Oregon 3.19 at the top (Table 3, lines 1287-1311). It correlates with GLFM policy liberalism at .47 and with SMR at .37 (lines 752-758) — Flavin emphasizes that this means the index "is not simply an alternative measure of the liberalism of state policy" (lines 749-752). For the compendium, this DV is **out of scope** (it measures political equality, not lobbying regulation), but it is the lens through which Flavin's results should be interpreted: when Flavin says regulations "promote political equality," he specifically means that stricter regulations are associated with a *weaker income-to-opinion-policy-distance gradient*, conditioning on income inequality, electoral competitiveness, and for-profit interest-group share.

**(b) Headline empirical findings (verbatim, with line refs).**

- "Across the states, more stringent lobbying regulations predict greater political equality." (lines 962-965)
- "states with more stringent lobbying regulations tend to exhibit a weaker relationship between income and political influence" (lines 130-134)
- "The coefficient for strictness of lobbying regulations is positive and statistically different from zero, indicating that states with stricter regulations on lobbyists tend to weigh citizens' opinions more equally in the policymaking process." (lines 859-866)
- "lobbying regulations have the largest substantive effect on the equality of political representation: moving one standard deviation below the mean to one standard deviation above leads to a .60 standard deviation increase in the Political Equality Index." (lines 894-900)
- Table 4: Lobbying-regulations coefficient = **0.213** (SE 0.092, p<.05) under OLS; **0.220** (SE 0.068, p<.01) under bi-weight robust regression. N=48, R²=.32. (Table 4, lines 1321-1352.)
- Co-variate signs as expected: states with higher Gini and higher for-profit share are *less* politically equal; states with more competitive elections are *more* politically equal (lines 866-885).

**(c) Limitations Flavin himself flags.**

- The measure of regulation strictness is "the number of different regulations a state has on its books (Newmark 2005)" — Flavin explicitly suggests future work should evaluate "other measures of regulation (for example, resources and vigilance devoted to prosecuting those who violate established regulations)" (lines 992-1001). I.e. **enforcement** is missing from his right-hand side.
- N=48 is small. Flavin runs a bi-weight robust regression to check that 1-2 high-leverage states are not driving the result (lines 905-921).
- Causal direction is not formally identified; Flavin reports a conditional correlation. The implicit assumption is that regulation choice is not endogenous to current political-equality conditions (an assumption he does not test).

**(d) For the compendium pipeline.** Because Flavin applies Newmark 2005 unchanged, his paper contributes **no own-rubric atomic indicators** to the compendium. The TSV reflects this with one external-measure-applied row. If at some point the project wants to record empirical-use evidence of the form "rubric X's outputs predict outcome Y in study Z" — i.e., a citation graph for rubrics — this paper is a clean datum: Newmark 2005 → Flavin's Political Equality Index, β = 0.213, p<.05 (Table 4 col 1), with state-relative income, Gini, electoral competition, and for-profit interest-group share controls.

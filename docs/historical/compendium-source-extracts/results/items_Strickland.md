# Strickland 2014 (published 2018) — Extraction Notes

## 1. Paper

Strickland, James. "A Paradox of Political Reform: Shadow Interests in the U.S. States." *American Politics Research* (2018), DOI 10.1177/1532673X18788049. Working paper version dated July 18, 2014; SSRN abstract 2467944. University of Michigan PhD candidate at time of writing.

**Framing.** Empirical study of whether US state lobbying laws suppress or promote interest-group registration rates. Frames itself against Gray and Lowery's Energy–Stability–Area model and the "shadow lobbying" literature (LaPira 2016; Thomas & LaPira 2017). The central thesis is a "paradox of political reform": campaign-finance restrictions on registered lobbyists drive interest groups underground (do not register), so reformers face a trade-off — they can have either broad registration or strict limits on registered lobbyists' political activity, but not both.

> "Reformers can either restrict the campaign finance activities of organized interests or disclose their lobbying activities more fully, but not both." (Abstract, L36–37)

## 2. Methodology

**Empirical question.** Do (a) registration criteria, (b) campaign-finance prohibitions, and (c) reporting requirements each affect the count of registered interest groups in a state-year, and how do they interact?

**Time window.** 1988–2013 (a temporal extension beyond Newmark's 1991–2003 coverage).

**State coverage.** All 50 US states. Some models (Models 1, 5) use all observed state-years (n=931, 50 states). "Complete-panel" models (Models 3, 7) use only the 12 years for which all 50 states had observations (n=600). Models 2, 4, 6, 8 drop Nebraska (49 states) because the Unicameral is nonpartisan and party-competition controls do not apply.

**What measure(s) Strickland uses + how he applies them.** Strickland uses **Newmark's (2005) 18-item index** as his measure of lobby-law stringency. Crucially, he does NOT construct an own rubric:

> "I employ a measure of lobby law stringency that spans multiple states and years. Newmark's (2005) measure assumes values from 0 to 18 depending on the presence or absence of specific lobby laws. In this index, lobby laws come in three categories: definitions of lobbyists, prohibitions on their conduct, and reporting requirements. I utilize the three categories of lobby laws in Newmark's index as separate explanatory variables. Table 1 lists all 18 laws included in Newmark's scale." (L415–422)

Table 1 of the paper reproduces Newmark's 18 items verbatim with the footer `Source. Newmark (2005).`

**Modifications.** None at the item level. Strickland's analytic adjustments are:
1. **Decomposition.** He splits Newmark's 0–18 composite into three component sub-scales (Definitions 0–7; Prohibitions 0–4; Reporting 0–7) and uses them as **three separate explanatory variables** in regression instead of as a single index.
2. **Interaction terms.** Adds Definitions × Prohibitions and Definitions × Reporting interactions in the regression specification, motivated by his costly-compliance theory. (This is an analytic choice, not an item-level change.)
3. **Temporal extension.** Newmark's data ran 1991–2003; Strickland extends to 1988–2013 by re-applying Newmark's coding scheme to additional source documents (see Section 6).
4. **No items added, removed, or modified.**

The TSV (`items_Strickland.tsv`) therefore contains 0 own-rubric rows and a single meta-row documenting the unchanged application.

## 3. Organizing structure

Strickland uses **Newmark's three categories** unchanged:
- **Definitions of lobbyists** (7 items)
- **Prohibited activities involving lobbyists** (4 items)
- **Reporting requirements for lobbyists** (7 items)

These are not Strickland's own categorization — they are the structure Newmark (2005) imposed and Strickland adopts wholesale.

## 4. Indicator count and atomization decisions

- **18 underlying indicators**, all from Newmark (2005). Strickland does not split, merge, or rename any.
- **Atomization decision.** Because Strickland makes no item-level changes, no atomization decisions on the rubric itself. His only atomization-adjacent choice is treating Newmark's 0–18 composite as three sub-scales rather than one index — a regression-specification choice, not an item-rewrite.
- **Boolean coding.** Each item is binary 0/1 (per Newmark's scheme that Strickland inherits); summed within category to yield the three sub-scales.

## 5. Frameworks cited or reviewed

Frameworks and predecessor measures named in the body of the paper:
- **Newmark (2005)** — the measure Strickland uses (see lit-review section "Explanatory Variables", L416–429).
- **Hunter, Wilson & Brunk (1991)** — first to test whether stringent lobbying regulations affect registrations; used binary indicators of frequent legal definitions of "lobbyist."
- **Hamm, Weber & Anderson (1994)** — found broadness of statutory definitions positively associated with registrations.
- **Brinig, Holcombe & Schwartzstein (1993)** — "economic model" using measures of regulations and violation penalties.
- **Lowery & Gray (1994, 1997)** — argued lobby regulations have little effect on registrations.
- **Brasher, Lowery & Gray (1999)** — Florida and Minnesota case study of changing lobbying definitions.
- **Gray & Lowery (1996, 1998)** — Energy–Stability–Area model of interest populations.
- **Opheim (1991)** — explanation of state-level differences in lobby regulation.
- **Ozymy (2010, 2013)** — total-lobby-laws measure used to study influence and scandal-driven adoption.
- **Chari, Hogan & Murphy (2010)** — global comparison of lobby regulation (mentioned for context).
- **LaPira (2016); Thomas & LaPira (2017)** — shadow-lobbying framing.
- **Newmark (2017)** — cited in the Discussion as a call for "more precise measurement of lobby laws" (L885–886), framing Strickland's use of the older Newmark 2005 index as provisional.

## 6. Data sources

**Lobby-law variables (Newmark index, 1988–2013):**
- **1988–2003:** Council on Governmental Ethics Laws (COGEL) *Campaign Finance, Ethics and Lobby Blue Book*, biennial editions, plus Council of State Governments (CSG) *Book of the States*, biennial editions. These are Newmark's original sources.
- **2004–2013:** State Capital Law Firm Group's *Lobbying, PACs, and Campaign Finance: 50 State Handbook*, annual editions. Used to extend Newmark's coding scheme; the 2003 Handbook was used as a calibration year against the 2003 Book of the States. Where Handbooks indicated changes in definitions, prohibitions, or reports, Strickland adjusted the measure; otherwise he extended 2003 values forward.
  > "If, according to post-2003 Handbooks, lobby laws did not change within a state before 2013, then 2003 values from the Books of the States were extended to subsequent years. If Handbooks did indicate changes in existing lobby laws after 2003, then I first determined whether there had been changes to definitions, prohibitions, or reports and then made the necessary adjustments in the lobby law measure. This method allowed me to employ a consistent coding scheme across sources." (L920–927)

**Counts of registered interest groups (response variable):**
- State documents and registration reports (online, state archives, libraries, on-request) — first priority.
- Counts from prior researchers' published lists: Wilson (1990) for 1989; Gray & Lowery (1996) for 1990; Lowery & Brasher (2004) for 1997; Lowery, Gray & Cluverius (2015) for 1998; Newmark (2008) for 1999.
- Jordan & Grossmann (2016) Correlates of State Policy Project — aggregator.
- **National Institute on Money in State Politics (NIMSP)** — for 2006–2013, lobbyist–client dyads cleaned of duplicates.
- Pennsylvania and New Jersey: lobbying firms included in group totals because firms must register.

**Statute readings.** Strickland does NOT read statutes himself. He extends Newmark's coding by reading prepared compilations (COGEL Blue Book, Book of the States, 50 State Handbook) — the same kind of secondary source Newmark used.

**Controls:**
- Real gross state product (Bureau of Economic Analysis, 1997 chained dollars; SIC pre-1998, NAICS post-1998).
- Squire (2007) legislative-professionalism index, with 2009 update from Squire.
- Modified Ranney party-competition index (Klarner 2010), 6-year folded average.
- Initiative/referendum dichotomous indicator (26 states).

## 7. Notable quirks / open questions

- **The "2014" working paper title is misleading.** The text file is the published 2018 version in *American Politics Research* with title "A Paradox of Political Reform: Shadow Interests in the U.S. States." The SSRN 2014 working paper (the one in the prompt) is presumably an earlier draft of the same study. Per the project's `paper_id` convention I have used `strickland_2014`, but the substantive content is the published 2018 version.
- **No own-rubric construction.** This paper is squarely in the "empirical use" bucket — Strickland makes the project's compendium-construction decisions easier by NOT introducing new items.
- **Decomposition matters for compendium use.** While the items are Newmark's, Strickland's evidence that the three sub-scales have *opposite-signed* effects on registration (prohibitions depress; reporting near-zero or mixed; definitions positive but moderated by prohibitions) is a finding worth reflecting in any composite scoring rubric: aggregating these into a single 0–18 index is masking heterogeneous effects.
- **Headline empirical findings.**
  > "States in which initiatives or referenda might occur also have more interest groups on average... With regard to lobby laws, model results are mixed but conclusively suggest that the number of campaign finance limits in a state affects rates of registration among interest groups. The effects of criteria are contingent on the presence of prohibitions. When interacted with registration criteria, prohibitions suppress the positive effect of more criteria on total registrations." (L707–716)
  > "At an aggregated level, 57,815 unique interest groups registered in the U.S. states in 2013 (the latest year for which I have data). By contrast, my model predicts that approximately 72,091 groups might have registered if there had been detailed registration criteria and no campaign finance restrictions or reporting requirements." (L791–796)
- **Newmark 2017 self-criticism is acknowledged.** Strickland flags in his Discussion that "the need for more precise measurement of lobby laws remains (see Newmark, 2017)" (L885–886) — i.e., he is aware the index he is using has known limitations but proceeds because nothing better exists for panel analysis.
- **Public Disclosure Commission as a positive case.** Strickland highlights Washington State's PDC as the example where a stringent reporting regime did NOT depress registration: "the number of clients who registered consistently approached the maximum potential. Such a set of laws provides promise for reformers." (L803–805)
- **Reporting-coefficient caveat.** Reporting-requirement coefficients sometimes failed conventional significance thresholds; the headline causal story is about prohibitions, not reporting (L723–725).
- **Open question for the compendium.** Whether to count Strickland in the "framework count" at all, or only as an empirical-use citation of Newmark 2005. He produces no own-rubric; he produces an extended panel of Newmark scores, which is a *data product*, not a *measurement instrument*.

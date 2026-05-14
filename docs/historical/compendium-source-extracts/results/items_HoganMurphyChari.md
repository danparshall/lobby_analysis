# Hogan, Murphy & Chari (2008) — extraction notes

`paper_id`: `hogan_murphy_chari_2008`

## 1. Paper

Hogan, John, Gary Murphy and Raj Chari. 2008. "'Next door they have regulation, but not here …': Assessing the opinions of actors in the opaque world of unregulated lobbying." *Canadian Political Science Review* 2(3): 125–151.

> "The lobbying of government by various interests is regarded as central to the democratic process. Deliberative democratic theorists tell us that the regulation of lobbying has a positive effect on political systems, and the behaviour of those within them. Yet, only a small number of democracies have implemented legislation regulating lobbyists' activities. Even within these countries, certain jurisdictions still have not enacted lobbying regulations. Here we examine the attitudes of actors in these unregulated provinces, states and institutions towards the idea of lobbying legislation." (Abstract, lines 16–25)

The paper is **not** a rubric-construction paper. It is an attitudinal survey of politicians, administrators and lobbyists in *unregulated* jurisdictions that border or share sovereignty with regulated ones. Its analytical scaffold borrows the three-tier (low/medium/high) typology that **Chari, Murphy & Hogan 2007** ("Regulating Lobbyists: A Comparative Analysis of the USA, Canada, Germany and the European Union," *The Political Quarterly* 78(3): 422–438) produced by applying CPI's Hired Guns index to all jurisdictions with lobbying legislation.

Central hypothesis (lines 243–245):
> "in jurisdictions without lobbying regulations, significant support exists for the transparency, and accountability, regulations offer."

## 2. Methodology

**Jurisdictions sampled** (all unregulated at the time of the 2005–2006 fieldwork):
- **United States**: Pennsylvania (the lone state without lobbying regulation).
- **Canada (provinces)**: Prince Edward Island, New Brunswick, Manitoba, Saskatchewan, Alberta. (Alberta enacted regulation in 2008, after the data collection.)
- **European Union**: the European Council and the European Commission (Commission instituted a voluntary register in July 2008, after fieldwork).

> "This selection fulfils a basic research requirement of having a range of 'most similar' and simultaneously 'most different' cases to examine." (lines 269–273)

**Instruments**:
- 460 hardcopy expert questionnaires posted September 2005 – January 2006. Overall response rate ~10% (politicians 8.3%, administrators 18.3%, lobbyists 5.3%).
- 18 in-depth, semi-structured interviews March–July 2006 with elected representatives, administrators, lobbyists and academics.

> "we employed a subcategory of purposive sampling – expert sampling. The sample was preselected due to their in‐depth knowledge in the area examined. … the expert sample size selected was 460. However, we recognise that by employing a non‐probability sampling technique we cannot infer from our findings to the larger population." (lines 282–286)

The questionnaire (Appendix A, lines 974–1090) contains **15 questions**: Q1–Q5 are demographic (which constituency / ministry / province / lobby-group type); **Q6–Q14** are the substantive items, with Q15 a free-text close. The substantive items are what we capture in the TSV.

## 3. Organizing structure

This paper does **not** produce its own per-item rubric for scoring statutes. Two structures are present:

(a) **Imported typology** (one structural anchor, three categories):
- low / medium / high regulatory environment, derived in Chari et al. 2007 by applying the CPI Hired Guns index across jurisdictions and presented here as an "ideal type" framework. The 2008 article *uses* this typology to contextualise where its surveyed jurisdictions sit (or would sit) but does not re-derive scores.

(b) **Survey instrument** (nine substantive items, Q6–Q14), grouped narratively by the article into the following thematic clusters:
- Reasons for absence of regulation (Q6) → Table 1
- Registration and the filing of spending reports (Q7, Q8, Q9, Q10) → Tables 2 and 3, plus narrative
- The impact of a register upon citizens (Q11) → Table 4
- The auditing and penalisation of lobbyists (Q12, Q13) → Tables 5 and 6
- Transparency, accountability and effectiveness (Q14) → Table 7

## 4. Indicator count and atomization decisions

**Total items in the TSV: 10.**

- **1** typology indicator (`typology.regulatory_environment`) representing the imported low/medium/high classification. Captured because it is the only "rubric-like" structure the paper places in front of the reader, even though its construction belongs to Chari et al. 2007.
- **9** survey items (`survey.q6` through `survey.q14`), one per substantive questionnaire question. These are not statute-coding items, but they probe the same regulatory dimensions that statute-coding rubrics measure (registration, disclosure frequency, contribution disclosure, public-list modality, audit authority, penalties), and are the closest things this paper offers to "items."

Demographic questions (Q1–Q5) and the free-text close (Q15) are excluded — they encode respondent metadata rather than regulatory content.

We did **not** decompose the multi-option questions (Q6, Q8, Q10, Q12) into per-option binaries. The paper itself treats each as a single multi-choice item and reports response distributions across the option set; splitting them would manufacture structure that the authors didn't intend.

## 5. Frameworks cited or reviewed

Names only (no scoring imported from any of these):

- **Center for Public Integrity (CPI) — Hired Guns index**: cited explicitly as the index applied in the antecedent Chari, Murphy & Hogan 2007 *Political Quarterly* paper. Methodology URL given in endnote 3: `http://www.publicintegrity.org/hiredguns/default.aspx?act=methodology` (line 908).
- **Opheim 1991** ("Explaining the Differences in State Lobby Regulations," *Western Political Quarterly* 44(2): 405–421): cited as a US-state lobby-regulation rigour measure (line 158, line 171).
- **Brinig, Holcombe & Schwartzstein 1993** ("The Regulation of Lobbyists," *Public Choice* 77(2): 377–384): cited alongside Opheim as a US-state rigour measure and again on the barrier-to-entry argument (line 158, line 211, line 645).
- **Newmark**: not cited.
- **Citizens Conference on State Legislatures (CCSL) 1971**: cited (line 173).
- **OECD / Bertók 2008** (*Lobbyists, Governments and Public Trust*): cited extensively as the deliberative-democracy / transparency frame.
- **Nolan Committee 1995** (UK): cited as the locus of the "barrier to entry" argument the authors test against (lines 211–215, 641–646).

## 6. Data sources

- **Direct statute reading**: not applicable — this article does not score statutes.
- **Country experts**: yes — purposive expert sampling (n=460) of politicians, administrators and lobbyists in the named jurisdictions; supplemented by 18 in-depth interviews.
- **Surveys**: yes — postal hardcopy questionnaires.
- The imported typology (low/medium/high) was constructed in Chari et al. 2007 from CPI's Hired Guns rubric; that earlier paper is the statute-reading exercise, not this one.

## 7. Notable quirks / open questions

**The big one — relationship to the Chari et al. 2020 book** (*Regulating Lobbying: A Global Comparison*, 2nd ed., Manchester UP):

The 2008 CPSR article does **not** reference any forthcoming book. It cites only the antecedent **Chari, Murphy & Hogan 2007** *Political Quarterly* paper (lines 1140–1141), which contains the original three-tier typology built by applying CPI Hired Guns across jurisdictions. The progression is therefore plausibly: **CPI Hired Guns rubric → Chari, Murphy & Hogan 2007 (PQ) applies it to a comparative sample and produces the low/medium/high typology → Hogan, Murphy & Chari 2008 (CPSR) deploys the typology in a survey of unregulated-jurisdiction attitudes → Chari, Hogan & Murphy 2010 1st-ed book (later 2020 2nd ed.) extends the comparative project**. The 2008 article alone does not let us verify the 2010/2020 books' rubric — the rubric they extend is the 2007 PQ paper's, not this one.

**Comparability to CPI Hired Guns**:
- The article *uses* CPI's index by reference (via Chari et al. 2007) and treats CPI's score categories as the implicit benchmark when discussing what counts as "low/medium/high" regulation.
- The article's own survey instrument is **attitudinal**, not a coding rubric. Q7 (registration), Q8 (filing frequency), Q9 (contribution disclosure), Q10 (public-list availability), Q12 (audit), and Q13 (penalties) cleanly map onto the dimensions that CPI Hired Guns scores, but they ask actors *what they think should be required*, not what the statute requires. Treating them as comparable rubric items would conflate "ought" with "is."

**Other quirks**:
- Pennsylvania's anomalous status: it had passed lobbying legislation in 1998, which the **Pennsylvanian Supreme Court struck down in 2000** (and reaffirmed in 2002) as illegal regulation on the practice of law (lines 360–364). For the purposes of this article it is treated as unregulated.
- "Most similar / most different" case-selection logic explicitly invoked (Collier 1997) — three substantively different polities (US state, Canadian provinces, supranational EU institutions) deliberately included.
- Response rate 10% — the authors are explicit that findings are illustrative, not representative.
- Australian regulation history (1983–1996, repealed; new code 2008) and Hungary 2006 / Poland 2005 are flagged as the rapidly-changing context the snapshot is taken against (line 877: "since the research presented here was conducted, Australia and Hungary have introduced lobbying regulations, while Alberta and the European Commission are in the process of doing so").

**Open question for the compendium**: if FOCAL ref'd this paper as a "validator" for CPI Hired Guns, that's a category error — Hogan/Murphy/Chari 2008 *uses* CPI Hired Guns (via Chari et al. 2007) rather than validating it independently. The independent validation, if any, would have to come from comparing CPI Hired Guns scores against external indicators in either the 2007 PQ paper or the 2010/2020 book.

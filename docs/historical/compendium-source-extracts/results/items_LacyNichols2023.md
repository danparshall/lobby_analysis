# Lacy-Nichols, Quinn & Cullerton 2023 — "Aiding empirical research on the commercial determinants of health"

## 1. Paper

**Citation.** Lacy-Nichols J, Quinn M, Cullerton K. Aiding empirical research on the commercial determinants of health: a scoping review of datasets and methods about lobbying. *Health Research Policy and Systems* 2023;21:56. doi:10.1186/s12961-023-01011-8.

**Framing.** This is a **methodological scoping review of datasets and methods**, not a measurement framework. Two practical questions guided the review (lines 92–94):

> "(1) Where can we find data about lobbying, and (2) How can we access and analyse this data?"

The audience is **commercial determinants of health (CDoH) researchers** — the authors are public health scholars borrowing from political science to enable empirical lobbying research. The paper does **not** construct a normative scorecard for evaluating disclosure regimes; rather, it inventories what political-science researchers have actually done with disclosure data and asks how CDoH researchers can repurpose those datasets and methods.

This matters because Lacy-Nichols 2023 is the **methodological precursor** to FOCAL (Lacy-Nichols et al. 2024). The 2023 paper points downstream — given the disclosure data that exists, what indicators and methods can researchers use? The 2024 paper points upstream — what should disclosure regimes require? Notably, Table 2's exclusion criteria explicitly **rule out** the kind of disclosure-regime evaluation studies that constitute FOCAL 2024's corpus: "Only examined mechanisms to address lobbying (e.g., disclosure requirements); only analysed the influence of lobbying (not the practice)" (lines 342–344). So the two papers are complementary, not redundant: 2023 catalogues research-method indicators; 2024 catalogues regulation-design indicators.

## 2. Methodology

**Scoping review** following Arksey & O'Malley's five-step framework (line 235). Conducted by an Australian/UK public health team.

**Search strategy:**
- **Database searches** (29 September 2021): six databases — Scopus, Medline (Ovid), Web of Science, Embase, CAB Direct, ProQuest — yielding 5,141 records, deduplicated to 4,533 (lines 248–263, 256–263).
- **Grey literature** (Godin et al. method): five Google Advanced searches limited to `filetype:pdf`, scanning first 100 results; plus website searches of 11 organisations (initial list of 28 from Mialon et al.'s "institutions working on the influence of corporations on public health policy"; lines 305–322). 308 records via websites + 12 via Google = 320, deduplicated to 285, of which 280 reports retrieved (lines 252–256).
- **Search terms** combined two conceptual categories — "lobbying" and "lobbying dataset" — using `lobby* OR "interest group*" OR "pressure group*" OR "outside group*" OR advoc*` (line 213) anded with terms for transparency registers, ministerial diaries, official records, etc. (lines 213–223).

**Screening pipeline:**
- Screened: 4,533 peer-reviewed + 280 grey literature reports against Table 2 inclusion criteria. MQ primary screener; JLN double-screened 10%.
- **Phase 1 included:** 149 peer-reviewed + 16 grey literature = **165 studies** (lines 290–293).
- **Phase 2 (deep-dive on meetings):** 12 peer-reviewed + 3 grey literature = **15 studies** (lines 296–300).

**Data extraction:** Two-stage process.
- **Stage 1** (all 165 studies): two pieces of information — data sources used and indicators used to measure lobbying. The six-indicator typology (Table 3) was inductively developed and iteratively refined as papers were screened (lines 322–328).
- **Stage 2** (15 meeting studies): nine extraction categories charted in Excel — article details, topic, location, government details, policy details, lobbyist details, data, lobbying purpose, challenges discussed (lines 383–391).

**Inclusion criteria (Table 2):** five inclusion gates that constrain the corpus to (a) English, (b) original research, (c) the *practice* of lobbying (not regulation of it, not influence outcomes alone), (d) publicly replicable data, (e) sufficient method detail. Exclusion criteria explicitly rule out studies that "only examined mechanisms to address lobbying (e.g., disclosure requirements)" (line 343) — this draws a hard line between this paper's scope and FOCAL 2024's scope.

## 3. Organizing structure

The review produces **six analytical structures**, of which the first three are the canonical "outputs":

| # | Structure | Items | Source | Role |
|---|---|---|---|---|
| 1 | **Table 3 — Lobbying activity indicators** | 6 | papers/text/...txt:358–367 | The core typology — what researchers measure when they study lobbying |
| 2 | **Table 6 — Actor classification categories** | 12 | papers/text/...txt:848–871 | Synthesis of the actor taxonomies used across the 15 meeting studies |
| 3 | **Table 4 — Data sources, classified into 3 classes** | 3 classes (Govt / Public / Commercial), ~80+ datasets | papers/text/...txt:439–497 | Inventory + accessibility classification of the corpus's data sources |
| 4 | Stage-2 extraction schema | 9 columns | papers/text/...txt:383–391 | The data-extraction template applied to the 15 meeting studies |
| 5 | Table 2 — Inclusion / exclusion criteria | 5 inclusion + 5 exclusion | papers/text/...txt:335–353 | Defines the boundary of the review |
| 6 | Table 1 — Definitions of lobbying | 6 illustrative definitions | papers/text/...txt:163–179 | Vocabulary survey, not a typology |

**Authoritative quote on Table 3 typology:**

> "We also sought to describe the different ways that lobbying was analysed in the literature. To do this, we developed a set of 'indicators' used to measure lobbying activity. These were inductively developed and iteratively refined as we screened the papers, with a final set of six categories (Table 3). These categories were applied to the 165 studies included in the first stage." (lines 322–326)

**Frequency distribution across the 165-study corpus** (lines 376–380):

| Indicator | n studies | % |
|---|---|---|
| Registration | 67 | 41% |
| Expenditure | 56 | 34% |
| Meetings | 15 | 9% |
| Comments | 14 | 8% |
| Bills | 9 | 5% |
| Committees | 4 | 2% |

Sums to 165 — consistent with the rule that each study was assigned a single primary indicator: "Some studies, especially those from the grey literature, used a combination of indicators (e.g., registrations and expenditure), in which case a primary indicator was selected for coding based on the overall focus of the study, as coding for multiple indicators was beyond the scope of the study. If meetings were one of the indicators, they were prioritised as our main interest." (lines 326–333).

**Geographic skew:** ~two-thirds of the 165 studies are USA-based (n=113; line 410). For lobbying expenditure specifically, 48 of 56 studies use the Open Secrets database (lines 414–417). All 15 meeting studies are from high-income contexts: EU (5), US (4), Canada (3), Australia (1), Ireland (1), UK (1) (lines 432–434).

## 4. Indicator count and atomization decisions

**TSV row total: 35 rows.** Composition:

- 6 rows for Table 3 indicators (`indicator.*`)
- 12 rows for Table 6 actor categories (`actor_cat.*`)
- 3 rows for Table 4 data-source classes (`data_class.*`)
- 9 rows for stage-2 extraction columns (`stage2.*`)
- 5 rows for Table 2 inclusion criteria (`inclusion.*`)

**Judgment calls:**

1. **No native numerical IDs.** None of the tables number their rows. I assigned semantic IDs (e.g., `indicator.registration`, `actor_cat.business`).
2. **Compound rows kept as one item, matching the paper.** Every Table 3 row enumerates multiple sub-criteria (e.g., Meetings = "face-to-face meetings…requests for meetings…reports of government branch(es) contacted…informal meetings"). Kept as single rows because (a) the paper presents them as one indicator and (b) the n-counts (67/56/15/14/9/4 = 165) require this grouping. Atomizing would inflate the count and destroy the n-distribution claim.
3. **Table 6 rows include synonym sets in `indicator_text`** rather than as separate items. This matches the paper's structure: each row is "Category | Other terms". Twelve rows (4 with no synonyms — Think tank, Law firm, Lobbying firms, Individuals; 8 with 1–8 synonyms each).
4. **Table 4 represented at the *class* level, not per-dataset.** Table 4 contains roughly 80+ named datasets in three columns. Capturing each dataset as a row would have produced a long list of named data sources rather than a description of the analytical structure the paper produces. The paper's structural contribution is the **3-way classification scheme** (government / publicly available / commercial) plus the rule for classifying — these are captured as 3 rows. Individual datasets named in Table 4 are referenced in the `notes` column.
5. **Table 1 (definitions of lobbying) excluded from TSV.** Six illustrative definitions from European Transparency Initiative, WHO, Sunlight Foundation, OECD, Transparency International, International Standards for Lobbying Regulation. These are *examples of definitional variation*, not items the paper itself constructs as a typology — the paper's point in citing them is to demonstrate that lobbying lacks a consistent definition, not to commit to any one. Excluding from the TSV avoids implying the paper endorses these as a normative list.
6. **Table 5 (15 meeting studies) excluded from TSV.** Table 5 is a study-level evidence chart, not an indicator list. Captured implicitly via the stage-2 extraction-schema rows.
7. **`scoring_rule` is "Not specified" for nearly all rows.** This is a methodological scoping review — its outputs are typologies and inventories, not weighted indicators. The only places with explicit rules are Table 2 (inclusion gates with exclusion-criterion text) and Table 4's "free of charge → publicly available; unsure → commercial" classification heuristic.
8. **`indicator_type` values used:** `count`, `amount`, `field`, `category`, `data_source_class`, `extraction_field`, `inclusion_criterion`. These are categorical inferences from the paper's structure, not paper-defined.

## 5. Frameworks cited or reviewed

The paper reviews 165 empirical studies; it does not "review frameworks" the way FOCAL 2024 does. However, in the introduction (lines 130–187) the authors situate their work against several **public-health conceptual frameworks** for thinking about lobbying:

| Framework | Citing line | Role in this paper |
|---|---|---|
| **Corporate Political Activity (CPA) Framework** (Savell, Gilmore, Fooks 2014) | 150–157 | Cited as one definition of lobbying — "Information strategy, defined as 'meetings and correspondence with legislatures/policymakers'" (line 154–156). Differentiates direct vs indirect lobbying. |
| **Policy Dystopia Framework** (Ulucanlar, Fooks, Gilmore 2016) | 151–158 | Cited as alternative definition — segments lobbying into "information management" and "direct involvement/influence", with techniques of access, incentives, threats, etc. |
| **Mialon, Swinburn, Sacks 2015** ("proposed approach to systematically identify and monitor the corporate political activity of the food industry") | 224–230 | Identified as the prior work that systematically documented data sources for measuring political practices. **The 2023 paper explicitly positions itself as building on this list:** "Here, we build on this list of data sources by documenting a fuller range of specific data sources to measure lobbying" (lines 226–228). |
| **Corporate Permeation Index** (Madureira Lima & Galea 2019) | 184–187 | Cited as an indicator-based approach to measuring CDoH influence; uses # of registered lobbyists + gaps in national lobbying regulation as proxy for CDoH risk exposure. |
| **Corporate Financial Influence Index** (Allen, Wigley, Holmer 2022) | 184, 195–199 | Cited; notably, the protocol authors reflect on "challenges of finding datasets measuring lobbying transparency with sufficient country coverage, ultimately excluding the lobbying indicator" (lines 194–199). |
| **Commercial Determinants of Health Index** (Lee et al. 2022) | 184–186 | Cited; includes "the number of registered lobbyist as well as gaps in national regulation of lobbyists as indicators for the level of CDoH risk exposure" (lines 185–187). |
| **Global Data Barometer — Political Integrity module** (Open Government Partnership / Transparency International, 2022) | 1040–1052 | Cited in discussion as an example of cross-domain alignment (public health ∪ corporate accountability). Five-dimension structure: party finance, interest declarations, lobbying registers, public consultation in rule-making, right-to-information. Differentiates "quality related features" (data content) from "open data related features" (usability). |
| **OECD Lobbying in the 21st Century (2021)** | 1115–1118 (page 17) | Cited; surveyed 41 countries, found only 23 had lobbying disclosure requirements. |

**Overlap with FOCAL 2024's 15-framework corpus.** None of the eight frameworks above appear in FOCAL 2024's 15-framework Table 2. The 2023 paper engages with **public-health/CDoH conceptual frameworks** (CPA, Policy Dystopia, CPI, CFII, CDoH Index, Mialon-Swinburn-Sacks), whereas FOCAL 2024 reviews **lobbying-disclosure-regime evaluation frameworks** (Opheim 1991, Newmark 2005, Center for Public Integrity Hired Guns 2007, PRI 2010, ALTER-EU 2013, Sunlight 2015, etc.). This is the cleanest evidence that the two reviews cover **disjoint methodological literatures** despite shared authorship — they sit on opposite sides of the disclosure-data pipeline.

The Sunlight Foundation 2013 lobbying disclosure guidelines do appear here (Table 1, line 169), but only as a definitional citation, not as a reviewed framework.

## 6. Data sources

**Search corpus:** Six academic databases (Scopus, Medline, Web of Science, Embase, CAB Direct, ProQuest) and structured grey literature search across 11 organisation websites + Google Advanced. Search date: 29 September 2021.

**Database yield by source** (lines 251–259):

| Database | Records |
|---|---|
| Scopus | 3,317 |
| ProQuest | 1,125 |
| Embase (Ovid) | 358 |
| Web of Science | 260 |
| Medline (Ovid) | 42 |
| CAB Direct | 39 |
| **Total (with duplicates)** | **5,141** |
| **Deduplicated** | **4,533** |

**Datasets reviewed (Table 4, lines 439–497):** organised into three columns. Approximate counts:

- **Government data** (~30 entries): US federal (FEC, LDA, FARA, IRS Form 990, SEC, Senate Finance Committee, US Congressional Hearings, SAM.gov, OIRA, OMB, Trade Advisory Committee Membership, U.S. Census Bureau, U.S. Department of Commerce); US states (CA Secretary of State, CA Office of Administrative Law, MN Campaign Finance Board, Eye on Lobbying [WI], FL Commission on Ethics, NC Secretary of State); EU (Transparency Register, Calendars of Commissioners, EUR-Lex, Eurobarometer, EP Public Register of Documents, EP door pass register, Lobby Transparency LobbyCal plugin); country-level (Ireland Register of Lobbying, electionsireland.org, Houses of the Oireachtas; German Lobby Register, OECKL Handbuch; France's Le conseil national de la vie associative; Chile Library of National Congress; UK Public Sector Transparency Board, All-Party Parliamentary Groups register, Conservative Party Lobbying Contact Reports; Canada Registry of Lobbyists, Health Canada Meetings and Correspondence; Australia Government Register of Lobbyists, Productivity Commission).
- **Publicly available data** (~25 entries): Comparative Agendas Project, Open Secrets, FollowTheMoney.org, lobbyfacts.eu, openinterests.eu, voteview.com, Sunlight Foundation, Public Citizen, Center for Progressive Reform, Environmental Working Group, GovTrack.us, LobbyView, Vote Smart, Voter Information Services, Interarena project, INTEREURO project, UN Accreditation database, European Patent Register, EU Policy Agendas Project codebook, Forbes Global 2000, Fortune 100, Fortune Global 500, FOI archives (e.g., corporateeurope.org), Italian Stock Exchange, ISIC scheme, IRRC, The European Election Studies, LinkedIn.
- **Commercially available data** (~25 entries): BoardEx, Compustat, Orbis, LexisNexis, Refinitiv Datastream, Thomson Reuters Business Classification, Thomson Reuters Stock Ownership, Thomson Financial Securities Data, SDC VentureXpert, Washington Representatives (formerly lobbyists.info), WestLaw Next, Russell 2000 Index, Encyclopedia of Associations, Directory of Corporate Affiliations, American Lobbyists Directory, Directory of British Associations, Nealon's Guide, Pyttersen Almanak, Guida Monaci sul Sistema Italia, The European Public Affairs Directory, Yearbook of International Organizations, First Street, Breach Level Index, Congressional Districts in the 1990s, International Accounting Standards Board.

**Classification heuristic:** "We have reviewed the websites of all non-government data sources to establish whether they were available free of charge. Where unsure, we have listed them as commercially available." (lines 419–422). Important caveat: "researchers often have free access to these sources through their university libraries. However, cost would present a significant barrier for other organisations, such as advocacy groups to access these data" (lines 422–426).

## 7. Notable quirks and open questions

**A. This is unambiguously a methodological precursor to FOCAL 2024 — but with disjoint scope.** Same lead author, overlapping co-author (Cullerton), one-year gap. Yet the two papers' scope conditions are designed to **exclude** each other:

- **2023:** "Focused on the practice of lobbying or the quantity of lobby firms and lobbyists" → studies of disclosure-regime *design* are excluded (Table 2: "Only examined mechanisms to address lobbying (e.g., disclosure requirements)" → exclude).
- **2024 (FOCAL):** Reviews 15 frameworks for *evaluating disclosure regimes* — exactly the literature 2023 excluded.

This is a deliberate division of labor. The 2023 paper inventories what researchers can do with disclosure data; FOCAL 2024 inventories what disclosure regimes should require. There is essentially zero overlap in cited frameworks (none of FOCAL 2024's 15 frameworks appear in the 2023 paper, and none of the 2023 paper's 8 conceptual frameworks appear in FOCAL 2024).

**B. The 2023 typology is descriptive of the literature, not prescriptive.** The 6-indicator typology in Table 3 is an **inductive** synthesis of what researchers have actually measured: "These were inductively developed and iteratively refined as we screened the papers, with a final set of six categories" (lines 323–326). The paper does **not** claim these six are the right things to measure — it claims these six are what the literature does measure. This contrasts sharply with FOCAL 2024's normative 50-indicator framework.

**C. "Meetings" prioritization injects bias.** The single-primary-indicator rule has a tiebreaker: "If meetings were one of the indicators, they were prioritised as our main interest" (lines 332–333). This biases the n=15 meeting count upward and the other counts downward (especially registration + expenditure, which are almost always co-measured with meetings in grey literature). The reported n-distribution should be read as **lower bounds** for indicators other than meetings.

**D. US/Open-Secrets bias propagates through the corpus.** Two-thirds US-based studies (n=113); 48 of 56 expenditure studies use Open Secrets; all 15 meeting studies are high-income (EU/US/Canada/Australia/Ireland/UK). The paper acknowledges this: "while many of the datasets documented here exist in the Global North, similar datasets may exist in other countries which we are not aware of" (lines 975–977).

**E. "Notably absent" finding on lobbying purpose.** Only 5 of 15 meeting studies measured the *purpose* of meetings, and even then in coarse terms (lines 877–887, 909–911). This is the paper's strongest empirical finding for disclosure-regime design: meeting registers tend to record who-met-whom-when but rarely what-was-discussed. This is directly actionable for state-level disclosure schema work — it says the *content* field of a meeting record is the lowest-hanging fruit for disclosure-regime improvement.

**F. Two-theme synthesis of data challenges:**
- Theme 1 — Deficiencies in the data: missing in-house lobbyists, missing low-level officials, voluntary fields treated as optional (lines 909–926).
- Theme 2 — Format and quality: non-downloadable data, lack of unique identifiers (preventing entity matching), PDFs in unstandardised formats (lines 927–933).

The unique-identifier discussion (lines 1002–1031) is particularly relevant for any state-level disclosure pipeline: "Requiring a unique identifier… would help to address this challenge and make the data more easily searchable" — though the authors acknowledge significant practical hurdles for cross-jurisdiction implementation.

**G. Open question — is "Comments" the same as "submissions" in FOCAL 2024's lexicon?** Table 3's Comments indicator subsumes "written letters, submissions, comments, responses to consultations" (line 365). FOCAL 2024 has indicators related to written submissions in its Contact log category. Without consulting FOCAL 2024 (per task constraints), the boundary cannot be drawn here, but this is the most likely point of indicator-level overlap between the two papers' typologies, given that both authors were thinking about the same construct.

**H. Open question — does Table 6's actor taxonomy align with anything in FOCAL 2024's "Descriptors" category?** FOCAL 2024 has a Descriptors category (6 indicators); Table 6 here lists 12 actor types. Per task constraints I have not cross-referenced. The fact that Table 6 has more synonyms than canonical labels (e.g., 8 alternative terms for "Public interest") suggests the actor-taxonomy literature is fragmented — useful background for any normative typology effort.

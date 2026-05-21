# PAPER_SUMMARIES

Key conclusions per paper, with numerical findings where applicable. This file is too long for every-session reads — get pointed here from `PAPER_INDEX.md`.

---

## Bacik 2025 — LobbyView network dynamics

**Citation:** Karol A. Bacik, Jan Ondras, Aaron Rudkin, Jörn Dunkel, In Song Kim. "Measuring the dynamical evolution of the United States lobbying network." arXiv:2503.11745v2 [physics.soc-ph], February 2026.
**File:** `papers/Bacik_2025__lobbyview_network_dynamics.pdf`
**Extracted text:** `papers/text/Bacik_2025__lobbyview_network_dynamics.txt`

### Key findings

- LobbyView integrates **1,277,411 LD-2 filings** (1999–2023) representing more than **$87 billion in disclosed lobbying expenditures**. Reports were biannual before 2008 and quarterly after, due to HLOGA 2007; the number of reports roughly doubles at the 2008 transition.
- The lobbying system is modeled as a five-layer multipartite network: clients → registrants → lobbyists → government entities → legislators. Edges between clients, registrants, and lobbyists come from LD-2 filings directly. Edges to legislators are inferred from disclosed past employment (the "revolving door"): in 2023, 20% of lobbyists had a disclosed connection to a covered government position, and in recent years 80% of Senators and 60% of Representatives had at least one lobbyist with a past-employment connection to them.
- Annual churn in K-Street registrants: 200–500 new firms enter and a comparable number exit each year.
- Long-term growth in client-registrant connections follows **linear preferential attachment** — firms with more existing clients accumulate new clients at a rate proportional to their size. This is the same mechanism found in other complex networks (Barabási-Albert type scale-free growth).
- Mid-term dynamics show **synchronization with the presidential election cycle**: the issue-portfolio matrix has a block-diagonal structure aligning with changes in government. Major rearrangements occurred after 9/11 and during COVID-19.
- Short-term perturbations track critical events: the 2007–2008 financial crisis and the early COVID-19 period both produced measurable network-structure shifts.
- SOPA case study: for the 67 publicly-traded firms that lobbied on the Stop Online Piracy Act in Q4 2011, the conditional probability P(client ∈ IT sector | lobbied SOPA) exceeds 0.4, compared to a much lower baseline of P(client ∈ IT sector).
- The paper introduces a probabilistic framework for analyzing lobbying behavior at the level of individual bills, issues, or firms, based on conditional probabilities over lobbying pathways.

### Method

**Entity disambiguation (the part most directly relevant to our project):**

- **Registrants** have unique identifiers in the Senate LDA database, used internally.
- **Clients** are identified only by textual representation and require disambiguation. LobbyView uses a search-engine-driven disambiguation method (queries external corporate identifiers — Compustat, Orbis — and agglomerates high-probability matches).
- **Lobbyists** require disambiguation because they are identified only by name. The paper uses a **score-based entity resolution approach**: block on characteristics (name, past covered-position history, registrants, years of operation), then agglomerate high-probability matches.
- **Government entities** use closed-set string-distance matching (simpler because the universe of federal agencies is bounded).
- **Bills** are extracted from unstructured issue text using **regular expressions** to identify specific bill IDs, which are then related to congressional data.

**Data pipeline:** Python for automation, PostgreSQL relational database for storage, indexed for query performance. Cross-linking identifiers are provided for Compustat, Orbis, BoardEx, and NOMINATE/VoteView.

**Monetary amounts:** Handled via an upper-bound convention for low-cost lobbying — if a filing is below the reporting threshold, the amount is set to the threshold value (treating it as an upper bound on actual unknown spending). Self-filers and external-registrant filers use different reporting lines (line 13 vs. line 12 of LD-2).

### Notes for our project

1. **LobbyView is the template for what this project is trying to build at the state level.** Their architecture (PostgreSQL relational, entity disambiguation across five actor layers, external ID linkage) is directly portable. What we have to add is (a) heterogeneous input formats across 5–8 states instead of one structured federal source, (b) position extraction (which Bacik 2025 does not do — see Kim 2025), and (c) a compliance layer. What we can reasonably *skip* in v1 is the network analysis and probabilistic pathway framework — those are downstream uses of a clean data layer.
2. **Their entity disambiguation methodology is a concrete answer to some of the open questions in our schema design.** The score-based blocked agglomeration approach for lobbyists, and the search-engine-driven approach for clients, are both worth benchmarking against fastLink / fuzzylink / Libgober-Jerzak on state lobbying data.
3. **The regex-only bill extraction is a viable baseline.** State lobbying filings are messier than LDA reports, so LLM extraction will probably do better — but it is important to build a regex-based baseline first and measure the delta rather than assuming LLMs help.
4. **The $87B / 1.6M record scale is an aspiration, not a benchmark.** At the state level, with 8 states, the pipeline will process far fewer filings but with more format heterogeneity.
5. **The "historical paper filings are digitized separately" problem we identified in Montana has an analog in LobbyView:** LDA filings from 1999–2007 are available but with filing-period code ambiguities (e.g., Q-codes appearing in biannual-reporting years). The paper handles this by "aggregating the periodic data into annualized data, thus discarding the exact filing code." Our pipeline will face similar annualization choices for pre-standardization state filings.

---

## Kim 2025 — AI-driven bill position classification

**Citation:** Jiseon Kim, Dongkwan Kim, Joohye Jeong, Alice Oh, In Song Kim. "Measuring Interest Group Positions on Legislation: An AI-Driven Analysis of Lobbying Reports." arXiv:2504.15333v1 [cs.CY], April 2025. (Targeted for PNAS.)
**File:** `papers/Kim_2025__ai_bill_positions_lobbying.pdf`
**Extracted text:** `papers/text/Kim_2025__ai_bill_positions_lobbying.txt`

### Key findings

- Pipeline produces a dataset of **279,104 bill positions** across **12,032 interest groups** on **42,475 bills** from the 111th to 117th Congresses. This is **5× more interest groups and 7× more bills than MapLight**, the prior human-curated gold standard.
- Of the 279k positions, **82,421 were generated by LLM annotation directly** and **196,683 were generated by the GNN refinement layer** on edges where textual information alone was insufficient.
- **LLM annotation accuracy: 96.93% and F1 97.19** vs. human labels on a validation set of 391 samples that two human annotators independently labeled with identical results (selected for clarity of the text signal).
- **MapLight agreement: 91.03%** on the 1,182 overlapping interest-group-bill pairs between the Kim dataset and MapLight. The 9% disagreement is not necessarily LLM error — it could reflect actual position shifts over time or MapLight coding choices.
- **GNN refinement accuracy: 78.51% overall, F1 74.65**, on a 70/10/20 train/val/test split. Per-class F1: Support 79.19, Oppose 64.06, Engage 80.70. The GNN is trained on the combined LLM + MapLight labeled data.
- The Amend and Monitor categories were merged into a single "Engage" category during training because classifying Amend separately produced unreliable accuracy. Final task is a 3-class problem: Support / Oppose / Engage.
- **Lobbying Position Scores (LPscores)** are derived via an item response theory (graded model, MIRT package in R) applied to Support/Oppose positions only, producing latent preference scores for 1,796 interest groups over 2,020 bills. EAP reliability is 0.95, standard errors range 0.03–0.30 (all below 0.32 threshold).
- Only **13.1% of MapLight's 194,479 interest-group-bill position pairs** can be mapped to corresponding lobbying reports. The authors interpret this as evidence that most MapLight-listed interest groups do not actively lobby, so MapLight alone gives limited insight into direct lobbying influence.

### Method

**Raw data source:** LD-2 lobbying reports, Section 16 ("Specific Lobbying Issues") free text. Filings are segmented line-by-line; lines are filtered to keep only those that (a) reference a bill ID (Senate or House bills only, no resolutions) and (b) contain one of a set of position-indicator keywords (`endorse`, `defeat`, `advocate`, `watch`, etc.). The keyword list is derived from state lobbying statutes and guidance documents. Approximately 1.4 million bill-line text pairs enter the pipeline before keyword filtering.

**LLM annotation:** Azure OpenAI, GPT-4 (model version `2023-09-01-preview`), temperature 0 for deterministic output. For each bill-line pair, the LLM receives the bill ID, bill title, and the lobbying description line, and is prompted to classify as Support / Oppose / Amend / Monitor. Cases where the text is insufficient are labeled "Mention" rather than being forced into a position class.

**GNN annotation:** A heterogeneous graph neural network operating on interest groups, bills, legislators, and lobbyists. Interest groups have attributes (state, industry code, government affiliation). Bills have attributes (subject, sponsoring party, legislative status). Lobbyists have attributes (ethnicity, gender, past party affiliation). Lobbying reports create interest-group ↔ bill edges; bill sponsorships create bill ↔ legislator edges; covered-position disclosures create lobbyist ↔ legislator edges. The GNN predicts the type of the interest-group ↔ bill edge (Support / Oppose / Engage). Training uses LLM-annotated labels combined with MapLight labels. Predictions with confidence > 0.9 are retained; lower-confidence predictions are discarded.

**LPscores:** MIRT graded model fit to Support/Oppose labels only. Filter: retain only interest groups lobbying on ≥10 bills and bills lobbied by ≥10 groups. Output: one-dimensional latent preference score per group, analogous to a roll-call ideal point.

### Notes for our project

1. **This is the single most directly applicable piece of prior art for the position-extraction component of the pipeline.** The 96.93% accuracy number is the ceiling we should measure against for the federal case, and the cross-jurisdictional comparison (state vs. federal) is the open question worth answering first.
2. **The federal-to-state gap matters.** Federal LD-2 Section 16 text is reasonably structured (the authors found about 1.4M bill-line pairs via line segmentation, then filtered by keywords). State filings vary from similarly structured to entirely unstructured PDFs. Before assuming 96.93% accuracy will hold, the pipeline should include a per-state validation set with ~200–400 hand-labeled samples and compute per-state accuracy.
3. **The keyword-filtering step is worth stealing.** Before sending text to an expensive model, filter to lines containing position-indicator keywords. The paper's keyword list is derived from state lobbying statutes (they cite the Colorado Secretary of State guidance manual and NCSL resources) — directly reusable for us.
4. **Temperature 0 and a fixed model version are critical for reproducibility.** The paper documents `gpt-4-2023-09-01-preview` explicitly. Our pipeline should do the same, and provenance records should store the model version so re-runs are auditable.
5. **The Engage / Mention distinction is subtler than it sounds.** The paper merges Amend and Monitor because the Amend class was unreliable. The Mention class is used for cases where text is insufficient. For state filings where the text signal is weaker overall, the Mention category may be much larger than in the federal case, which changes what downstream analysis can conclude.
6. **The GNN refinement layer is a v2 concern, not a v1.** The LLM-only labels cover 82k of the 279k bill positions (about 30%), with the rest coming from GNN inference. For a v1 pipeline, LLM-only extraction on the subset of filings where the text signal is sufficient is a defensible scope and ship-ready. GNN refinement is worth building only after the v1 baseline is measured.
7. **MapLight is not the benchmark we want.** The 13.1% overlap between MapLight and actual lobbying reports suggests MapLight is capturing something different from direct lobbying (revealed public positions rather than filed activity). For validation, we should hand-label state filings directly rather than relying on MapLight as ground truth.
## Entity Resolution & Record Linkage

### fuzzylink: Probabilistic Record Linkage Using Pretrained Text Embeddings

- Authors: Joseph T. Ornstein (University of Georgia, Department of Political Science)
- Date: 2025
- File: `papers/Ornstein_2025__fuzzylink.pdf`
- Extracted text: `papers/text/Ornstein_2025__fuzzylink.txt`
- Source: https://joeornstein.github.io/publications/fuzzylink.pdf

Summary: fuzzylink is an active-learning record linkage procedure that replaces lexical string similarity with cosine similarity over pretrained text embeddings (OpenAI, 256-dim), using GPT-4o zero-shot prompts to label uncertain record pairs instead of human coders. The method iteratively fits a logistic regression on labeled pairs (embedding + Jaro-Winkler similarity as predictors), selects the most uncertain remaining pairs for labeling via uncertainty sampling, and repeats until convergence. It handles nicknames, acronyms, former organization names, and cross-language matching — all cases where lexical similarity fails.

Key findings:
- Candidate-to-voter-file linking (9,025 CA candidates vs. 22M voter records): 95.8% precision and 95.8% recall, vs. fastLink's 93.3% precision and only 63.1% recall — a 32-point recall gain driven by nickname resolution.
- Misspelled city name linking (7,118 PPP city names vs. 28,889 Census places): 2,451 true matches at 98.0% precision; the AFSM baseline found only 705 matches at 65.6% precision.
- Interest group linking (1,388 amicus brief organizations vs. 2.9M DIME donors): recovered DIME scores for 437 organizations at 99.6% precision, vs. 376 recovered by original paper using exact + lexical fuzzy matching.
- Multilingual party name linking across 32 countries / 30 languages: 97.6% overall recall, 91.5% precision.
- All applications ran in a few hours on a personal computer and cost under $10 in API fees.

Relevance: Entity resolution across inconsistent state lobbying disclosure databases is exactly the problem fuzzylink targets — organizations listed under acronyms, abbreviations, former names, or variant spellings across 50 different state systems. The near-perfect precision on the interest group application (99.6%) is directly analogous to the lobbying use case. The R package is open-source and ready to use.

---

### Using a Probabilistic Model to Assist Merging of Large-Scale Administrative Records

- Authors: Ted Enamorado (Princeton), Benjamin Fifield (Princeton), Kosuke Imai (Harvard)
- Date: 2019
- File: `papers/Enamorado_2019__fastlink.pdf`
- Extracted text: `papers/text/Enamorado_2019__fastlink.txt`
- Source: https://imai.fas.harvard.edu/research/files/linkage.pdf

Summary: fastLink is a fast, scalable implementation of the canonical Fellegi-Sunter (1969) probabilistic record linkage model, addressing failures of deterministic and existing open-source probabilistic methods on large administrative datasets with missing data and measurement error. Also contributes methods for incorporating auxiliary information (name frequency, migration rates) and for post-merge regression analyses that propagate merge uncertainty.

Key findings:
- In simulations (100K records, 10% missingness): FNR below 5% and absolute estimation error below 1.5pp; exact match and ADGN produced much higher FNR and estimation errors above 7.5pp under MAR/MNAR conditions.
- Computational scaling: near-linear runtime vs. exponential for RecordLinkage (R/Python). At 150K records, fastLink takes under 6 hours (single core) vs. extrapolated ~900 days for RecordLinkage (Python).
- Merging two 160M+ nationwide voter files: 93%+ match rate at 0.85 threshold (FDR 0.10%, FNR 3.63%), vs. only 66.24% from exact matching — found 20x more across-state movers.
- Small overlap between datasets (20% vs. 50%/80%) is the primary driver of degraded performance; blocking by observed covariates substantially mitigates this.

Relevance: Cross-state and cross-year entity resolution in lobbying data involves inconsistent naming conventions, missing fields, and scale in the millions. fastLink provides the battle-tested probabilistic baseline — directly applicable to linking lobbying entities across state filings or against external reference datasets.

---

### Linking Datasets on Organizations Using Half a Billion Open-Collaborated Records

- Authors: Brian Libgober (Northwestern University, Political Science and Law), Connor T. Jerzak (University of Texas at Austin, Department of Government)
- Date: 2024 (to appear in Political Science Methods and Research)
- File: `papers/Libgober_2024__org_linking_open_collab.pdf`
- Extracted text: `papers/text/Libgober_2024__org_linking_open_collab.txt`
- Source: https://arxiv.org/pdf/2302.02533

Summary: Builds a linkage corpus from ~350 million public LinkedIn profiles, extracting 15.3 million unique organizational aliases, 6 million unique company URLs, and over 10^14 alias pairs. Trains three matching methods — a character-and-word-level neural network (ML), community detection over the alias-URL graph (bipartite/Markov clustering), and an ensemble — then validates on three tasks drawn from US lobbying data.

Key findings:
- On a lobbying-meetings-to-stock-tickers task (~700 orgs vs. ~7,000 companies), the Bipartite-ML ensemble achieves F2 scores above 0.6; the LinkedIn-trained ML model achieves KS = 0.87 (p < 10^-16) between match/non-match distributions vs. KS = 0.47–0.55 for fuzzy matching (Jaccard).
- On Fortune 1000 / OpenSecrets lobbying expenditure task, fuzzy matching recovers only about half the ground-truth coefficient; LinkedIn-based ensemble methods recover estimates within the 95% CI of ground truth.
- For out-of-sample organizations (YCombinator startups 2017–2024, not in LinkedIn scrape), the LinkedIn-trained ML model still outperforms fuzzy matching — corpus staleness limits the network component but not the embedding component.
- Runtime tradeoff: fuzzy matching under 1 minute, standalone ML ~5 minutes, Bipartite-ML ~4 hours for ~700x7,000; a 10,000x10,000 match would take ~2–3 days.
- Releases open-source R package (LinkOrgs) and full LinkedIn alias corpus on Dataverse.

Relevance: Entity resolution across inconsistent organizational names is central to the state lobbying pipeline. This paper provides directly applicable methods validated specifically on lobbying datasets, and the open-source LinkOrgs package and corpus may be usable as-is or as a training resource for a fine-tuned LLM approach.

---

## Lobbying Data Infrastructure

### LobbyView: Firm-level Lobbying & Congressional Bills Database

- Authors: In Song Kim (MIT, Department of Political Science)
- Date: 2018
- File: `papers/Kim_2018__lobbyview.pdf`
- Extracted text: `papers/text/Kim_2018__lobbyview.txt`
- Source: https://web.mit.edu/insong/www/pdf/lobbyview.pdf

Summary: LobbyView constructs a comprehensive database linking all lobbying reports filed under the LDA to specific congressional bills, standardized firm/industry identifiers, and bill sponsorship records. The core technical contribution is a multi-stage pipeline for extracting bill references from unstructured "specific issue" free text using regex-based bill number extraction with bag-of-words cosine similarity against CRS bill summaries to resolve the correct Congress session.

Key findings:
- Bill number extraction uses regex patterns for "H.R. 2577" / "S. 1207" formats from free text — no validation rate reported in this technical note.
- Congress disambiguation considers three preceding Congresses relative to filing year, selects best match by cosine similarity between issue text and CRS bill summaries.
- Congress propagation assumes one report almost always references bills from one Congress; majority vote propagation to ambiguous entries.
- Bill title search covers name-only references (e.g., "Safe Data Act") via tokenized full-text matching against bill title table.
- Bill range expansion handles "H.R. 4182-4186" patterns when numeric suffix difference is ≤10.

Relevance: This is the primary methodological baseline for bill extraction from federal lobbying disclosure text. State-level data lacks CRS summaries and uses inconsistent bill number formats across 50 jurisdictions, meaning the Congress-disambiguation step has no direct analog and the regex patterns will need to be replaced with LLM-based extraction for state data.

---

### The Lobbying Disclosure Act at 25: Challenges and Opportunities for Analysis

- Authors: Timothy M. LaPira (James Madison University), Herschel F. Thomas (West Virginia University)
- Date: 2020
- File: `papers/LaPira_Thomas_2020__lobbying_disclosure_act_at_25.pdf`
- Extracted text: `papers/text/LaPira_Thomas_2020__lobbying_disclosure_act_at_25.txt`
- Source: Interest Groups & Advocacy (2020) 9:257–271

Summary: Systematic accounting of the structural and analytical limitations in the federal LDA database (1998–2018), based on 1,000,336 verified LD-2 reports from 47,555 organizations. Diagnoses the nested, duplicative report format; documents artificial discontinuities from the 2007 HLOGA shift; and assesses how 85 peer-reviewed studies have exploited the data.

Key findings:
- HLOGA shift from semiannual to quarterly filings in 2008 nearly doubled annual report count overnight (38,739 → 79,203), a purely artifactual increase that distorts any time-series spanning that break.
- Total lobbying spending, unique clients, and multi-client contract firms all peaked in 2009 and declined rapidly through 2012, then held flat — attributed to more conservative compliance behavior triggered by HLOGA.
- 49.4% of 85 studies reviewed selected non-random client subsets (e.g., Fortune 500); only 20% analyzed the full population. Mean study spans just 6.7 years.
- Expenditures are not itemized by lobbyist or issue area — only available at the aggregate report level.
- Revolving-door "covered official" status is significantly undercounted because the LDA only requires disclosure on the initial LD-1, not subsequent LD-2 reports.
- US House and Senate together account for ~59% of all agency mentions, but the LDA treats both as generic "agencies," hiding which members, committees, or staff were contacted.
- Bill numbers in specific issue fields are unreliable before 2006 and remain high-risk for measurement error throughout.

Relevance: Understanding the federal LDA's structural gaps — non-itemized expenditures, revolving-door undercount, HLOGA break, opaque agency field — sets expectations for state-level disclosure regimes with similar or worse limitations. The taxonomy of analytical levels (client, lobbyist, firm, issue area, bill) and double-counting warnings are directly applicable to state pipeline design.

---

## Compliance & Disclosure Quality

### 2024 Lobbying Disclosure: Observations on Lobbyists' Compliance with Disclosure Requirements

- Authors: GAO (Government Accountability Office)
- Date: April 2025
- File: `papers/GAO_2025__lda_compliance_audit.pdf`
- Extracted text: `papers/text/GAO_2025__lda_compliance_audit.txt`
- Source: https://www.gao.gov/assets/gao-25-107523.pdf

Summary: GAO's 18th annual audit of LDA compliance, reviewing a stratified random sample of 100 quarterly LD-2 reports and 160 semiannual LD-203 contribution reports filed across Q3 2023–Q2 2024, drawn from 67,577 qualifying reports. Measures filing rates, documentation quality, covered-position disclosure, contribution reporting, and enforcement outcomes.

Key findings:
- 97% of lobbyists who filed new registrations also filed the required initial LD-2 report in the same quarter.
- 93% of LD-2 reports included documentation for lobbying income and expenses; 4% had figures differing from documentation by more than $10,000; 9% had rounding errors.
- 21% of LD-2 reports included lobbyists who had NOT properly disclosed prior covered positions — a persistent gap since 2015 with no statistically significant improvement.
- 5% of LD-203 contribution reports omitted one or more reportable political contributions; all 13 omitting reports in the 2024 sample were amended only after GAO contact.
- 23% of sampled LD-2 reports were amended after GAO contact — indicating corrections would not otherwise have occurred.
- Of 3,566 noncompliance referrals to the U.S. Attorney (DC) from 2015–2024, only 36% closed as compliant; 63% remain pending. The office has two full-time LDA enforcement staff. One civil action ($65,000 settlement) in 2024; no criminal actions.

Relevance: Federal compliance appears high on surface metrics (97% filing rate) but the 21% covered-position gap and the pattern of amendments triggered only by audit contact suggest systematic understatement. State systems are generally less resourced and less audited, so similar or worse data quality issues should be assumed in the pipeline.

---

### Lobbying in the Sunlight: A Scoping Review of Frameworks to Measure the Accessibility of Lobbying Disclosures

- Authors: Jennifer Lacy-Nichols, Hedeeyeh Baradar (University of Melbourne); Eric Crosbie (University of Nevada Reno); Katherine Cullerton (University of Queensland)
- Date: 2024
- File: `papers/Lacy_Nichols_2024__focal_scoping_review.pdf`
- Extracted text: `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt`
- Source: https://www.ijhpm.com/article_4651_43e3b5f9020f5754cb8e9fe5529287b8.pdf
- Supplementary: `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` (4 pages documenting the scoping review's search-term methodology; no text extraction — not research-relevant content)

Summary: Systematic scoping review of 1,911 records yielding 15 lobbying transparency frameworks (1991–2022). Thematically coded 248 items to synthesize FOCAL (Framework fOr Comprehensive and Accessible Lobbying) — an 8-category, 50-indicator rubric for evaluating what governments disclose about lobbying and how accessible those disclosures are. Designed to assess both lobbyist registers and open/ministerial diaries.

Key findings:
- Of 15 frameworks, financials appeared in 14/15; scope in 13/15; openness in 11/15 (open-data sub-theme specifically in 9/15); contact log in 13/15.
- Only 19 of 109 countries surveyed by the 2021 Global Data Barometer had a lobbyist register available online.
- Only 3 of the 15 frameworks applied weighted indicators; of those, the categories receiving highest weights were timeliness, online availability/format, financial disclosures, and enforcement/sanctions. FOCAL itself is unweighted by design and the authors flag this as a limitation.
- Scope and contact logs identified as the two highest-priority categories: narrow scope definitions (e.g., UK/Australia limiting to third-party lobbyists) exclude the bulk of in-house lobbyists; contact logs capture who was contacted, whose interests were represented, and the purpose of the meeting. Chile is cited as an exemplary model for contact log disclosure.
- FOCAL's 8 categories: Scope, Timeliness, Openness, Descriptors, Revolving Door, Relationships, Financials, Contact Log. First two assessed from legislation/regulations; remaining six from the register itself.
- Deliberate exclusions from FOCAL (present in 11/15 and 6/15 prior frameworks respectively): enforcement/accountability mechanisms and integrity/codes-of-conduct. FOCAL is explicitly disclosure-focused; enforcement and ethics belong in a separate compliance-layer rubric (e.g., GAO-25-107523).

Relevance: FOCAL provides the most directly applicable disclosure rubric for grading US state lobbying data quality: its 50 indicators map onto the fields an LLM extraction pipeline should populate (lobbyist names, client/employer, targets contacted, date, form of contact, topics, outcomes sought, financial amounts) and its Openness category directly informs how to score state-level data accessibility.

---

### Explaining the Differences in State Lobby Regulation

- Authors: Cynthia Opheim (Southwest Texas State University — now Texas State)
- Date: 1991 (Western Political Quarterly 44(2): 405–421)
- File: `papers/Opheim_1991__state_lobby_regulation.pdf`
- Extracted text: `papers/text/Opheim_1991__state_lobby_regulation.txt`
- Source: DOI 10.1177/106591299104400209 (SAGE)
- Cited by FOCAL (Lacy-Nichols 2024) as ref #30.

Summary: The foundational state-lobbying-regulation index. Constructs a 22-item, 0–18-point index across three dimensions — statutory definition of "lobbyist" (7 items), frequency and quality of disclosure (8 items), oversight and enforcement (7 items) — applied to 47 states (MT, SD, VA data unavailable). Uses OLS regression to test predictors of regulatory stringency: legislative professionalism (staff, pay, session length), political culture (Elazar/Sharkansky scale), tax capacity, urbanization, and Ranney party competition.

Key findings:
- Multivariate model explains 58% of variance in regulatory stringency (F=8.84, p<.0001).
- **Political culture** is the strongest predictor (t=4.85, p<.0001); moralistic states regulate most stringently, traditionalistic least.
- **Legislative staff support** is significant in the definitions and disclosure categories (p<.05) but not for oversight/enforcement.
- **Pay and session length** are tied to oversight/enforcement rigor but not to definitions or disclosure rigor.
- **Party competition** is *negatively* associated with regulation in the full model (counterintuitive; attributed to intra-party factional dynamics in one-party states).
- Lobbyist-definition components: 7 binary items covering whether a state defines legislative lobbying, administrative-agency lobbying, elected officials as lobbyists, public employees as lobbyists, and includes compensation / expenditure / time standards in the definition.
- Disclosure components (8 items, mostly binary except frequency of reporting): total spending, spending by category, expenditures benefitting public employees, gifts, legislation approved/opposed, sources of income, total income, and other influence-peddling activities.
- Oversight / enforcement components (7 items, binary): thoroughness of report review, plus six enforcement-authority items (subpoena witnesses, subpoena records, administrative hearings, administrative fines, administrative penalties, independent court actions).

Relevance: Opheim's 22-item index is the earliest item-level precursor to PRI 2010's 59-item rubric. The three-dimension structure (definitions / disclosure / enforcement) is the conceptual scaffolding that Newmark 2005/2017 and CPI Hired Guns both extended. For the rubric-unification work, Opheim's category-level architecture is useful context — but her items are subsumed by PRI 2010 (which carries more granular disclosure items) and FOCAL 2024 (which explicitly excludes enforcement for feasibility). Historically important; not a separate independent rubric source for the unification pass.

---

### Measuring State Legislative Lobbying Regulation, 1990–2003

- Authors: Adam J. Newmark (Appalachian State University)
- Date: 2005 (State Politics and Policy Quarterly 5(2): 182–191)
- File: `papers/Newmark_2005__state_lobbying_regulation_measure.pdf`
- Extracted text: `papers/text/Newmark_2005__state_lobbying_regulation_measure.txt`
- Source: DOI 10.1177/153244000500500205 (SAGE)
- Cited by FOCAL (Lacy-Nichols 2024) as ref #28.

Summary: Updates and extends Opheim 1991's approach into a time-series measure. Uses Council of State Governments' *The Book of the States* as the underlying data source (published biennially), constructing a replicable 17-binary-item, 0–18-point index covering six time periods: 1990–91, 1994–95, 1996–97, 2000–01, 2002, 2003. Supplements with a 1–4 penalty-severity score (based on direct statute review) for the 2003 cross-section. Does *not* include Opheim's oversight/enforcement items; focuses on statutory definition, prohibited activities, and disclosure requirements.

Key findings:
- **Validated against Opheim (1991)** at r=0.84 (p<.01) at the 1990–91 time point.
- Cross-time correlation: 1990–91 vs. 2003 r=0.46 (p<.01), reflecting meaningful change in state regulation over the decade.
- **Cronbach's alpha 0.71** for the 17-component 2003 measure — indicates acceptable internal reliability.
- **Mean state regulation rose from 6.54 (1990–91) to 10.34 (2003)**, standard deviation stable at ~3.1–3.6.
- **Largest gains:** South Carolina +750% (rose 42 spots, from 43rd to 1st); Georgia +700%; South Dakota +600%; Kentucky +367% (up 32 spots to 6th); Vermont and Ohio +267%.
- **Declines:** North Dakota −75%; Virginia −40% (dropped from 8th to 44th); Indiana −27% (5th to 37th).
- **Correlates with Newmark 2003** (a parallel NCSL+statute-based measure used in his dissertation) at r=0.70 (p<.01).
- **Index structure:** 7 definitional items (legislative / administrative / elected / employee lobbyist, compensation / expenditure / time standards), plus reporting-frequency item, plus prohibited-activities items (campaign contributions any time / during session / expenditures over threshold / solicitation), plus 6 disclosure-requirement items (seeking to influence legislation, expenditures benefitting officials, compensation by employer, total compensation, categories of expenditures, total expenditures). One definitional component was dropped due to zero variance.
- **Penalty supplement:** Separately coded felony-vs-misdemeanor classification, plus penalties for failure to file / register / filing false statement; scored 1–4 on severity. Data available for 47 of 50 states (CO, TN, WV excluded).

Relevance: Useful time-series validation of the *direction* of state regulatory change (states broadly got stricter 1990–2003), but **the index items are a proper subset of PRI 2010's** — PRI captures essentially all of Newmark's definitional and disclosure items and adds sub-aggregates on government exemptions, public-entity definition, materiality, and information-disclosed granularity. For rubric-unification purposes, Newmark 2005 contributes no item-level indicators that PRI does not already have. The validation-against-Opheim correlation (r=0.84) is evidence that PRI 2010 (which subsumes Opheim) should also correlate highly with Newmark's 2005 measure.

---

### Hired Guns Methodology (CPI)

- Author: Center for Public Integrity
- Date: December 2007 (web-only series)
- File: `papers/CPI_2007__hired_guns_methodology.pdf` (17-page PDF printed from the live web page on 2026-04-22; CPI never published a canonical PDF)
- Extracted text: `papers/text/CPI_2007__hired_guns_methodology.txt` (full 48-question text with point weights)
- Raw HTML backup: `papers/CPI_2007__hired_guns_methodology.html`
- Source: https://publicintegrity.org/politics/state-politics/influence/hired-guns/methodology-5/
- Cited by FOCAL (Lacy-Nichols 2024) as ref #33.

Summary: A 48-question, 100-point survey applied to all 50 states, designed to rank state lobby disclosure regimes. Researchers reviewed statutes and interviewed officials from each state's lobbying oversight agency. Scoring is weighted — the weights themselves encode CPI's view of what matters most in disclosure law.

Key findings:
- **Top state:** Washington at 87/100. No state scored 80 or above except Washington.
- **Score bands:** 70+ "relatively satisfactory"; 60–69 "marginal"; below 60 "failing."
- **8 category weights (summing to 100):**
  - Definition of Lobbyist — **7 pts** (executive-branch recognition, monetary thresholds)
  - Individual Registration — **19 pts** (filing mandates, timeframes, bill/subject specificity, frequency, photos, employer, compensated/non-compensated classification)
  - Individual Spending Disclosure — **29 pts** (largest weight; filing frequency, compensation, categorized summaries, itemization thresholds, recipient ID, dates, household-member spending, business associations, gifts, campaign contributions, no-activity reporting)
  - Employer Spending Disclosure — **5 pts**
  - Electronic Filing — **3 pts** (online registration, online report submission, training)
  - Public Access — **20 pts** (directory formats, report accessibility, copy costs, sample forms, aggregate totals, update frequency)
  - Enforcement — **15 pts** (auditing authority, mandatory review, late-filing penalties, incomplete-filing penalties, penalty history, delinquent-filer publication)
  - Revolving Door Provision — **2 pts** (cooling-off period only)

Relevance: **CPI Hired Guns is the only pre-FOCAL state framework that explicitly weights categories** — its weighting (Individual Spending Disclosure 29%, Public Access 20%, Individual Registration 19%, Enforcement 15%) is a useful reference for any future decision about weighting the unified rubric (which is currently unweighted, matching both PRI 2010 and FOCAL 2024). Its "Public Access" category is a proto-FOCAL-Openness; its "Individual Spending Disclosure" + "Employer Spending Disclosure" map onto PRI E-subsection and FOCAL Financials (cat 7). The **Enforcement category has no counterpart** in PRI 2010 or FOCAL 2024 — both explicitly exclude enforcement for feasibility/scope reasons — so Hired Guns is a reminder that the unified-rubric decision to exclude enforcement is a deliberate project choice, not a natural absence. Its web-only publication format is a cautionary note for data provenance: no canonical DOI, source only preserved via live URL + Wayback.

---

### How Transparent Is Your State's Lobbying Disclosure? (Sunlight Foundation)

- Author: Jonah Hahn
- Date: 2015-08-12 (updates 8/13/15 and 8/19/15 for Oregon and New Hampshire corrections)
- File: `papers/Sunlight_2015__state_lobbying_disclosure_scorecard.pdf` (web page printed as PDF — Sunlight never published a canonical PDF)
- Structured data: `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` (50 states × all 5 category scores + letter grade + total + links to state statutes and portals)
- Extracted text: `papers/text/Sunlight_2015__state_lobbying_disclosure_scorecard.txt`
- Source: https://sunlightfoundation.com/blog/2015/08/12/how-transparent-is-your-states-lobbying-disclosure/
- Status: Sunlight Foundation shut down September 2020; scorecard was never updated. Direct successor: OpenSecrets 2022 (see separate entry below).

Summary: A 5-category state lobbying disclosure scorecard, extending 2011 Sunlight work by Schuman, Buck, and Dunn. Every state graded on five criteria, with each category scored on a variable −2 to +2 scale. Scores summed to a raw total (can be negative), then mapped to A–F letter grades. Methodology is a blend of legal-statute review + actual state-website inspection. Explicit sibling project to State Integrity Investigation and National Institute on Money in State Politics, which supplied informational support.

Key findings:

**Methodology — 5 categories, variable point scales:**

1. **Lobbyist Activity** (−1 to +2): What level of legislative/action specificity is required in lobbyist reports?
   - +2: bill/action discussed AND position taken
   - +1: bill/action discussed
   - 0: general subjects only
   - −1: no activity reporting
2. **Expenditure Transparency** (−1 to +2): Granularity of expenditure reporting.
   - +2: itemized with dates and descriptions
   - +1: categorized totals (food/travel/etc.)
   - 0: lump total
   - −1: no reporting
3. **Expenditure Reporting Thresholds** (−1 to 0): Is all spending disclosed or only above a threshold?
   - 0: all expenditures disclosed
   - −1: threshold exemption applies
4. **Form Accessibility** (−2 to +2): Can the public access registration and expenditure forms?
   - +2: digital forms publicly available
   - +1: forms findable online
   - 0: blank forms accessible only
   - −1: one of the two forms inaccessible
   - −2: neither form accessible
5. **Lobbyist Compensation** (−1 to 0): Is lobbyist compensation disclosed?
   - 0: earnings disclosed
   - −1: no earnings disclosure

**Resulting score range per state:** −7 to +6 (sum of five category caps). Maps to A–F grades — exact cut points not stated in the blog post but embedded in the CSV.

**Empirical findings from the blog narrative:**
- **33 of 50 states** do not require full itemized expenditure disclosure (threshold exemptions apply).
- **24 of 50 states** do not require lobbyist compensation disclosure.
- **6 states** withhold the registration form from the public entirely.
- **18 states** only record the official met if expenditures exceed the threshold.
- Expenditure thresholds range from $2–$5 on the low end to $50 (Connecticut, Ohio, Virginia).
- Alabama's $500/quarter threshold makes most lobbyist-official interactions invisible.
- Notable transparency practices flagged: Missouri's direct-business-relationship disclosure; Alabama's similar requirement; New Jersey's disclosure of lobbyist board service on state authorities.

**Grade distribution (from the CSV):** All 50 states present. Top grade A: California, Massachusetts, New Jersey, New York, North Carolina, South Carolina, Wisconsin. Bottom grade F: Florida, Nevada, Oregon, West Virginia. Most states cluster B–D.

### Relevance for `lobby_analysis`:

1. **Explicit per-state category scores in machine-readable CSV — directly usable for calibration.** The CSV has each of the 5 scores per state plus state-statute and state-portal URLs. For our 2026 re-scoring work, these are a validation fixture: if a state ranked A in 2015 Sunlight and our pipeline scores it poorly in 2026, we should investigate whether (a) the state's laws degraded, (b) our rubric differs, or (c) the portal changed. The CSV is also the second per-state-per-category dataset we have (alongside PRI 2010), doubling the historical ground-truth surface.
2. **Rubric overlap with FOCAL.** Sunlight's 5 categories map cleanly onto FOCAL subsets: Lobbyist Activity ↔ FOCAL 8.9–8.11 (topics/bills); Expenditure Transparency ↔ FOCAL 7.1–7.10 (financials); Form Accessibility ↔ FOCAL Openness (cat 3); Lobbyist Compensation ↔ FOCAL 7.1. Sunlight's "Expenditure Reporting Thresholds" (reverse-scored threshold exemption) has no clean FOCAL equivalent and is a potential PRI_ONLY-style incompatible item for the unified rubric.
3. **Negative-scoring rubric is uncommon.** Most rubrics sum positive integers; Sunlight allows −2 on Form Accessibility. This creates a design question for the unified rubric: do we follow Sunlight and allow reverse-scored items (absence → penalty), or stick with PRI/FOCAL's non-negative convention? Newmark 2017's factor analysis already showed that mixing reverse-scored items into additive indices confuses the factor structure.
4. **Shut-down context reinforces the structural gap this project fills.** Sunlight, the highest-profile transparency NGO, couldn't maintain even this single scorecard as a living artifact. The scorecard was a one-off publication, never updated, then the organization closed. Living open infrastructure at the state level is genuinely unfilled — and this project's maintained `StateMasterRecord` is the correct response.

---

### Lobbying Regulation in the States Revisited

- Authors: Adam J. Newmark (Appalachian State University)
- Date: 2017 (Interest Groups & Advocacy 6(3): 215–230)
- File: `papers/Newmark_2017__lobbying_regulation_revisited.pdf`
- Extracted text: `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`
- Source: DOI 10.1057/s41309-017-0023-z (Springer)
- Cited by FOCAL (Lacy-Nichols 2024) as ref #29.

Summary: Updates Newmark 2005's measure to 2015 data. Because *The Book of the States* stopped publishing lobbying data after 2005, the author shifted methodology to direct review of state statutes, constitutional provisions, and information from Secretaries of State / Ethics Commissions — reviewing 50 states in 2015. Constructs a 19-item, 0–19-point index across three categories: definitions (7 items), prohibited activities (5 items), disclosure/reporting (7 items). Explicitly benchmarks the new measure against contemporaneous alternatives — Sunlight Foundation letter grades, Center for Public Integrity (CPI), and PRI 2010 (both accessibility and disclosure indices).

Key findings:
- **Index range 7–19**, mean 12.96, SD 2.63. Cronbach's alpha = 0.67 (lower than 2005's 0.71; author flags as "less than ideal").
- **Top states 2015:** Kentucky (19), Colorado (18), California (17), Arizona / Maine / Massachusetts / Wisconsin (16). **Bottom:** Wyoming (7), North Dakota (7), Nevada (8), South Dakota (9), Florida (9).
- **Correlations with other measures:**
  - New index ↔ Newmark 2003 (BOS data): **r=0.54** — 12-year drift plus methodological shift.
  - New index ↔ Sunlight Foundation: **r=0.40**
  - New index ↔ CPI: **r=0.52**
  - New index ↔ PRI accessibility: **r=0.27**
  - New index ↔ PRI disclosure: **essentially zero** (the paper says "it is generally unrelated to the PRI disclosure index")
  - **CPI ↔ PRI disclosure: r=0.04** — two disclosure indices that should theoretically measure overlapping constructs are in fact nearly orthogonal.
- **Factor analysis of the 19 items reveals 4–6 factors** (depending on eigenvalue cut), not 3 clean dimensions matching the category labels. Factors do not neatly align with "definitions / prohibitions / disclosure" — instead mix disclosure items with definition items, suggesting states make bundled design choices rather than independent decisions per category.
- **Substantive claim:** "Different measures, by design, measure different things. ... Scholars should not blindly incorporate measures of lobbying regulation without first considering the theoretical justification for a given restriction or set of restrictions."
- **Movers:** Arizona moved from low (6 in 2003) to high (16 in 2015) — but author notes Arizona's disclosure has gaps in recipient identification despite high item-level scores. Virginia, Illinois, North Carolina also moved up notably.

Relevance: **This paper is the single most important piece of evidence for the rubric-unification project's core decision.** The r=0.04 CPI-vs-PRI-disclosure correlation, and the r=0.27 Newmark-vs-PRI-accessibility correlation, are empirical proof that different scoring rubrics labeled "disclosure" or "accessibility" can measure near-orthogonal constructs. This directly supports the pri-calibration finding (0% exact-match agreement on PRI 2010 alone) and strengthens the case for a carefully-designed unified rubric over independent parallel scoring. The item list (7+5+7) is again a subset of PRI 2010's 61 disclosure-law items; Newmark 2017 contributes no new item-level indicators for unification but contributes the *validity warning* — rubrics that look similar can score states very differently. The author's own conclusion ("consider theoretical justification for each restriction") is the methodological posture this project should adopt going into Phase 2 of the unification plan.

---

### Lobbying in the Shadows: A Comparative Analysis of Government Lobbyist Registers

- Authors: Jennifer Lacy-Nichols, Hedeeyeh Baradar (University of Melbourne); Eric Crosbie (University of Nevada Reno); Katherine Cullerton (University of Queensland)
- Date: 2025 (Milbank Quarterly 103(3): 857–882)
- File: `papers/Lacy_Nichols_2025__lobbying_in_the_shadows.pdf`
- Extracted text: `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows.txt`
- Source: https://onlinelibrary.wiley.com/doi/10.1111/1468-0009.70033 (open access, CC-BY-NC)

Summary: The FOCAL application paper — companion to Lacy-Nichols 2024 (which built the framework). Identifies 28 countries with online lobbyist registers (from 128 surveyed via the Global Data Barometer, French HATVP 2020/2023, and OECD's *Lobbying in the 21st Century*), then scores each country against FOCAL's 50 indicators with a weighted 0/1/2 scheme (no/partly/yes), mapped to indicator-specific weights for a 182-point total. Includes a tobacco-industry-lobbying case study tracking Philip Morris International and British American Tobacco across all 28 registers. This is the first empirical application of FOCAL end-to-end.

Key findings:

**Benchmarking results (28 countries):**
- **No country fulfilled all 50 indicators.** Top performer (Canada) scored 49% / 89 of 182 points. The paper calls this "immensely telling."
- **Top 7:** Canada 49%, Chile 48%, United States 45%, Ireland 43%, France 43%, Scotland 40%, Finland 38%.
- **Bottom:** Netherlands 9%, Israel 11%, Georgia 12%, Poland 16%, Mexico 16%.
- **Category performance:** "Scope" scored highest across countries; **"Revolving door" and "Financials" scored lowest**. Contact logs are rare (only a small subset of the 28 provide them).
- **Ministerial-diary countries (4 of 28):** Chile, Estonia, Romania, United Kingdom.
- **Exemplars:** Canada (best-designed register, downloadable CSV with unique IDs, data-linkage friendly); Chile, Ireland, and Scotland (best contact logs with detailed topic/purpose disclosure).

**US-specific observations:**
- Scored as a **single country**, not state-by-state. US = federal LDA scope + House and Senate registers separately.
- US is the **only country imposing time AND money qualifiers** on lobbyist registration (20% of 3-month period + $3k individual / $13k org).
- US **excludes the executive branch** from disclosure requirements.
- US is one of only 2 countries (with France) providing detailed lobbying financial data.
- Multiple registers (House + Senate) create fragmentation — paper cites this as a design flaw.
- **Authors explicitly call out US-state application as future work:** *"researchers could apply the FOCAL to state governments in the United States, as many have more detailed disclosures than those required by the federal government."* (p. 875)

**Tobacco case study (Stage 2):**
- Evidence of PMI / BAT / subsidiary lobbying found in 14 of 28 countries with registers.
- 193 tobacco-industry meetings documented in the Chile / Scotland / Ireland contact logs alone.
- Striking strategic divergence by jurisdiction: Scotland's PMI/BAT lobbying focused on "reduced-risk tobacco products" (vapes); Chile's focused on "smuggling" — maps onto then-pending legislation in each country.
- Null result in Colombia (no tobacco industry entries in register) contradicted by independent document-based studies — demonstrates register under-reporting.

**Methodology details:**
- Weighted scoring: each indicator's 0/1/2 scale is multiplied by an indicator-specific weight (published as Supplementary File 1 Table 3) to produce the 182-point total. Three pre-existing weighted frameworks informed the weights (referenced to Supplementary File 1 Table 4).
- For registers in non-English languages, used Google Translate (with Spanish-native co-author reviewing Chilean registers).
- Sampled first 3 pages / 10 entries when reviewing variable-by-entry indicators.

### Relevance for `lobby_analysis`:

1. **Direct endorsement of this project's premise.** The paper explicitly frames applying FOCAL to US states as the obvious future-research follow-on. We are building what the FOCAL authors have publicly asked for.

2. **Published weights are a critical input to the rubric-unification decision.** The pri-calibration plan and the Phase-1 overlap-map plan currently assume an unweighted unified rubric (matching both PRI 2010 and the `focal_2026_scoring_rubric.csv`). This paper is the first to publish indicator-level weights for FOCAL, validated empirically against 28 countries. We should decide consciously whether to (a) adopt these weights, (b) use different weights (e.g., CPI Hired Guns', which are more US-state-disclosure-oriented), or (c) stay unweighted. **This should be surfaced in the Phase-1 open-questions list.**

3. **"Scope scores highest, revolving door + financials lowest" — calibration expectation for US states.** If our 50-state scoring comes back with a similar pattern (states broadly get definitions right but fail on revolving-door and financial disclosure), that's consistent with the international baseline. If it diverges sharply, we should understand why.

4. **Canada is the reference for register design.** Canada's combination of downloadable CSV, unique IDs enabling joins across lobbyist/client/meeting tables, and contact-log structure is what the `StateMasterRecord` + filing-model schema is heading toward. Canada's 49% score is the benchmark we should actually be able to beat for any state with a decent portal.

5. **The FOCAL weighting is category-level, not item-level equal.** Some indicators carry 2-point max, others 6-point max, reflecting the authors' view of relative importance. Cross-check when reading the methodology CSV: the scoring-direction column in `focal_2026_scoring_rubric.csv` currently treats all indicators as binary 0/1 — this diverges from Lacy-Nichols 2025's 0/1/2 with weights. Either the 2026 rubric needs updating to the published weights, or the project should document why it's deliberately using a simpler scheme.

6. **Contact-log category finding validates the FOCAL decision to decompose it into 11 indicators.** The paper shows how much richness exists in Chile / Ireland / Scotland's contact logs (topic, purpose, attendees, date, form, location, materials) and argues contact logs are "one of the most imperative features of disclosure." The unified rubric should preserve FOCAL's 11-indicator contact-log granularity rather than collapsing toward PRI's briefer E1i/E2i treatment.

---

### State Lobbying Disclosure: A Scorecard (OpenSecrets)

- Authors: Dan Auble, Brendan Glavin (OpenSecrets / Center for Responsive Politics)
- Date: 2022-06-28 (part of OpenSecrets' "Layers of Lobbying" series, funded in part by Omidyar Network)
- File: `papers/OpenSecrets_2022__state_lobbying_disclosure_scorecard.pdf` (web page printed as PDF)
- Extracted text: `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt`
- Source: https://www.opensecrets.org/news/reports/layers-of-lobbying/lobbying-scorecard
- Announcement: https://www.opensecrets.org/news/2022/06/opensecrets-releases-new-state-lobbying-disclosure-scorecard/

Summary: The direct successor to Sunlight Foundation's 2015 scorecard — Sunlight shut down 2020; OpenSecrets (Center for Responsive Politics) picked up the thread. Framework is redesigned, not inherited: 4 categories, each on a 5-point scale, 20-point max. Explicit design focus on making data ingestion feasible — "only 19 of the 50 states make meaningful data available" in OpenSecrets' own database, gated primarily on compensation disclosure. Context: OpenSecrets tracked $1.8B in state lobbying spending across the covered 19 states in 2021, vs. $3.8B federal.

Key findings:

**Methodology — 4 categories × 5-point scale = 20-point max:**

1. **Lobbyist/Client Disclosure Quality** (0–5): Are both lobbyist and client identified, and how?
   - Baseline 3: both identified
   - +1 (score 4): separate registrations for lobbyists and clients (cleaner data, fewer inconsistencies)
   - 0–3 below-baseline for less complete coverage
2. **Lobbyist Compensation** (0–5): Is compensation paid to lobbyists disclosed?
   - 0: not required (17 states)
   - 1–3: partial disclosure (e.g., reported in ranges, not linked to individual lobbyists — 7 states)
   - 4: full baseline disclosure (compensation required and linked to lobbyist)
   - 5: exceeding baseline (26 states total at 4+)
3. **Timely Disclosure** (0–5):
   - Baseline (4): monthly during legislative session + quarterly out of session (20 states meet this)
   - 5: more frequent than baseline
   - 0–3: below baseline (e.g., North and South Dakota: once a year)
4. **Public Availability** (0–5): Composite of three sub-factors
   - 1 pt: accessible lists of lobbyists and clients
   - 2 pts: user-friendly search (no click-through burden, no insider jargon, auto-populating lists)
   - 2 pts: downloadable data (bulk export, unique search URLs)

**Top-scoring states (≥16 points)** share four features: full compensation disclosure, accessible public display, perfect timely-disclosure score, user-friendly sites. Washington State cited as exemplar of public-availability UX.

**Bottom-scoring states (<10)** nearly all score 0 on compensation. North Dakota and South Dakota are the two lowest (once-a-year reporting only). Virginia is a notable exception — does require compensation disclosure but scores low overall due to a poor public-access site (the gap is partially filled by Virginia Public Access Project, an independent nonprofit).

**Key finding on compensation data:** Of the $1.8B OpenSecrets tracked in 2021 state lobbying, **84% was compensation**. States that don't disclose compensation are invisible to 84% of the tracked lobbying spend, which is why OpenSecrets treats compensation disclosure as the gating criterion for dataset inclusion.

**Per-state scores:** The PDF includes an interactive map (not a static table) plus descriptive top/bottom band discussion. The "complete list" is linked from the page as a separate artifact — not captured in the PDF. If the full 50-state per-category table is needed for calibration, it would require a separate fetch (possibly via OpenSecrets' data distribution or by Playwright-rendering the interactive map).

**What OpenSecrets explicitly flags as future work:**
- Targeted-legislation disclosure (bill references) — not addressed in this scorecard; "most states do not address it at all under the current rules."
- Common frameworks for definitions/requirements across jurisdictions — directly aligned with this project's `StateMasterRecord` aim.

### Relevance for `lobby_analysis`:

1. **Most recent peer scoring framework — critical Phase-1 overlap-mapping input.** This is the 2022 answer to "how does a transparency-data organization grade state lobbying disclosure in 2026-minus-4 years?" It is the freshest reference in the whole PRI/CPI/Sunlight/OpenSecrets lineage and the most operationally motivated (designed by people who ingest the data, not just score it). Its 4-category structure deserves explicit mapping in the Phase-1 unified-rubric overlap analysis.

2. **The compensation-disclosure gate is a strong empirical signal.** 84% of $1.8B tracked spending is compensation; 17 states require none. For our pipeline's `StateMasterRecord.RegistrationRequirement` / `ReportingPartyRequirement` fields, compensation disclosure is a high-leverage flag — states scoring low here have an extraction-ceiling regardless of how good our pipeline is. This should inform which states we prioritize for the 5–8 state target.

3. **Category-weighting insight: OpenSecrets gives equal weight (5 pts each) to 4 categories.** This is distinct from CPI Hired Guns 2007's heavily-skewed weighting (Individual Spending 29/100, Public Access 20/100, etc.) and Lacy-Nichols 2025's indicator-specific weights. Adds a third data point for the unified-rubric weighting question.

4. **"Virginia Public Access Project fills the gap where state site fails" is a pattern to note.** Some states have civic-tech nonprofits providing better data access than state government. For our pipeline, this raises the question of whether to ingest from such third-party sources where they exist, and how to credit them in provenance. Out of scope now but worth documenting.

5. **Top-state benchmarking.** Our pipeline pilot (pri-calibration) currently targets CA/TX/WY/NY/WI. Cross-referencing with OpenSecrets 2022: Wisconsin and NY are likely top-band here; CA / TX should be high; WY is a known bottom-band state (comparable to ND/SD). This is broadly consistent with the pilot's intent — covering range, not just clean cases.

6. **What they didn't publish in the article.** The full per-state per-category score table is an external linked artifact — not in the PDF. If we want a calibration fixture like the Sunlight CSV, we'd need to extract that list separately. Worth a note: unlike the Sunlight 2015 CSV which we successfully captured, OpenSecrets 2022 data is behind Cloudflare and will require either Playwright rendering or a direct data request to OpenSecrets.

---

### State-Level Lobbying and Taxpayers: How Much Do We Really Know? Assessing State Lobbying Disclosure Laws and Accessibility

- Authors: Jason Clemens, Julie Kaszton, Karrie Rufer, Laura Sucheski (Pacific Research Institute)
- Date: March 2010
- File: `papers/PRI_2010__state_lobbying_disclosure.pdf`
- Extracted text: `papers/text/PRI_2010__state_lobbying_disclosure.txt`
- Source: https://www.pacificresearch.org/wp-content/uploads/2017/06/TPFL_NoApp.pdf

Summary: A free-market think tank report that constructs two parallel scoring rubrics and applies them to all 50 states, producing ranked scores and a combined overall ranking. **Disclosure-law rubric:** 37-point composite across 5 sub-components (A: registration, 11 binary items; B: government exemptions, 4 binary items with B1/B2 reverse-scored per footnotes 85/86; C: public-entity definition, 0/1 gate with 3 described sub-criteria; D: materiality test, 0/1 gate with 2 described sub-criteria; E: information disclosed, 20-point aggregate using "higher of E1/E2 + F/G double-count when both principal and lobbyist report + separate J for financial contributors"). **Accessibility rubric:** 8 questions totaling 22 scorable points (Q1–Q6 binary, Q7 with 15 sort-criterion sub-items scored 0–15, Q8 simultaneous-sorting scored 0–15 then divided by 15 → 0–1). The report also uses California as a case study to estimate taxpayer-funded (government-to-government) lobbying as a share of total state lobbying. Note: the ideological framing (opposition to taxpayer-funded lobbying) does not undermine the scoring rubrics, which are the document's primary research contribution.

Key findings:

**Disclosure Law Scores (out of 37; 5 components):**
- Top: Montana 31/37 (83.8%), Arizona 30/37 (81.1%), South Carolina and Texas tied 29/37 (78.4%)
- Bottom: West Virginia and Nevada tied 11/37 (29.7%), New Hampshire 12/37 (32.4%), Maryland 13/37 (35.1%)
- Average: 21.9/37 (59.3%); 11 states scored below 50%
- 5 sub-components: (A) Registration (0–11): who must register — only 17 states require volunteer lobbyists, 24 require principals, 17 require lobbying firms, only 6 require government agencies to register. (B) Government exemptions (0–4): 44 states provide explicit exemptions for public agencies. (C) Definition of public entity (0–1): only 6 states define it. (D) Materiality test (0–1): 32 states include exemptions for small/incidental lobbying. (E) Information Disclosure (0–20): Alaska, Montana, NY, Texas tied at top with 18/20; Wyoming/Oklahoma worst at 5/20.

**Accessibility Scores (out of 22; 8 categories):**
- Top: Connecticut 17.3/22 (78.5%), North Carolina 14.3/22 (64.8%), Washington 14.3/22 (64.8%)
- Bottom: Vermont and Wyoming tied 5/22 (22.7%), New Hampshire 6/22 (27.3%)
- Average: 9.6/22 (43.6%); 32 states (64%) scored below 50%
- 8 categories: (1) Data availability, (2) Website existence, (3) Website identification, (4) Current data availability, (5) Historical data availability — 13 states lack it, (6) Data format — only 17/50 provide machine-readable downloads, (7) Sorting data — average 4.4/15 sort variables supported, (8) Simultaneous sorting — average 1.7/15 variables
- Notable discrepancy: South Carolina ranked 3rd on disclosure laws but 46th on accessibility. Connecticut ranked 18th on laws but 1st on accessibility.

**Combined Overall Rankings:**
- Top 6: Connecticut 71.7%, Indiana 68.0%, Texas 67.1%, Washington 66.2%, Maine 65.3%, Montana 65.2%
- Bottom 5: New Hampshire 29.9%, Wyoming 30.3%, West Virginia 30.8%, Nevada 35.3%, Maryland 38.5%

**California Case Study:** Total CA lobbying 2007–08 was $552.6M; government category was $92.6M (16.8%) officially, rising to $131.4M (23.8%) after reclassifying taxpayer-funded entities from Education, Public Employees, and Labor Unions.

Relevance: The 37 disclosure law criteria and 22 accessibility criteria are a directly usable framework for grading state data quality in a pipeline feasibility assessment. The accessibility rubric maps cleanly onto whether a state's data can be programmatically ingested (machine-readable format, sortability, historical availability). The 2010 rankings give a vintage baseline — Connecticut, Indiana, Texas, and Washington as better starting points; New Hampshire, Wyoming, and West Virginia as likely data dead-ends. Caveat: this is 16 years old; many states have overhauled their portals since, so rankings should be re-verified against current infrastructure before making pipeline decisions.

---

### CPI / Global Integrity — State Integrity Investigation (2015) *[stub-indexed 2026-05-13]*

- Authors: Nicholas Kusnetz / Center for Public Integrity (with Global Integrity)
- Date: November 2015
- File: `papers/CPI_2015__sii_only_three_states.pdf`
- Extracted text: `papers/text/CPI_2015__sii_only_three_states.txt`

Summary: Public-facing rollup article accompanying CPI/Global Integrity's 2015 State Integrity Investigation (SII), a second-round assessment using 245 questions across 13 governance categories scored by state-based journalists. Lobbying disclosure is the C11 category — the source of the C11 atomic items extracted independently on the `compendium-source-extracts` branch. Headline: no state earned A or B; Alaska earned the top grade (C); 11 states received F; New Jersey saw the largest drop from round 1.

Relevance: The C11 lobbying-disclosure subitems extracted from this SII feed the FOCAL-style framework comparison on this branch. **Stub-indexed; not factually audited** — the C11 atomic items themselves were extracted from the underlying `PublicI/state-integrity-data` GitHub repo (see 2026-05-07 RESEARCH_LOG entry), so this PDF is the *contextual citation* rather than the primary data source for that extraction.

---

## International / Comparative Lobbying Regulation

The entries below were all stub-indexed during the 2026-05-13 pre-merge audit of the `compendium-source-extracts` branch. Confidence: MEDIUM-HIGH from a single-pass survey by a research subagent. Full factual audit deferred. Reading order in `PAPER_INDEX.md` is roughly chronological within this category.

### Hogan, Murphy & Chari — Assessing the Opinions of Actors in the Opaque World of Unregulated Lobbying *[stub-indexed]*

- Authors: John Hogan (DIT), Gary Murphy (DCU), Raj Chari (TCD)
- Date: 2008 (September), in *Canadian Political Science Review* 2(3)
- File: `papers/Hogan_Murphy_Chari_2008__regulating_lobbying_globally.pdf`
- Extracted text: `papers/text/Hogan_Murphy_Chari_2008__regulating_lobbying_globally.txt`

Summary: Interview-based study of attitudes toward lobbying regulation among actors in unregulated jurisdictions. Builds on CPI's Hired Guns index, Opheim (1991), and Brinig et al. (1993) state-level indices to construct a three-tier (low/medium/high) classification applicable internationally. Tests predictions of deliberative-democratic theory about whether unregulated-jurisdiction actors favor regulation.

Relevance: Anchors the lineage from Opheim 1991 → CPI Hired Guns 2007 → international comparative use. The authors go on to write the *Regulating Lobbying* book series, which is widely cited in Lacy-Nichols 2024/2025. Useful context for understanding why CPI Hired Guns becomes the dominant international comparator. **Stub-indexed; not factually audited.**

---

### Mihuț — Lobbying in the United States and the European Union *[stub-indexed]*

- Authors: Liliana Mihuț (Babeș-Bolyai University)
- Date: 2008, in *Romanian Journal of European Affairs* 8(4)
- File: `papers/Mihut_2008__lobbying_us_eu.pdf`
- Extracted text: `papers/text/Mihut_2008__lobbying_us_eu.txt`

Summary: Comparative descriptive essay covering the 1946 Federal Regulation of Lobbying Act through the 2007 Honest Leadership and Open Government Act on the US side, and the European Transparency Initiative (2007) and 1996–97 EP Rules of Procedure on the EU side. Argues that the systems are converging despite differences along the pluralist/corporatist axis.

Relevance: Useful as a primary-source background on the EU-US definitional gap (LDA's "lobbying contact" vs. ETI's "activities to influence policy formulation"). Doesn't add a measurement framework not already covered by Holman & Luneburg 2012. **Stub-indexed; not factually audited.**

---

### Holman & Luneburg — Lobbying and Transparency: A Comparative Analysis of Regulatory Reform *[stub-indexed]*

- Authors: Craig Holman (Public Citizen) & William Luneburg (Univ. of Pittsburgh Law)
- Date: 2012, in *Interest Groups & Advocacy* 1(1)
- File: `papers/Holman_Luneburg_2012__lobbying_transparency.pdf`
- Extracted text: `papers/text/Holman_Luneburg_2012__lobbying_transparency.txt`

Summary: Comparative legal/policy article documenting the divergent origins of lobbying registries — US/Canada developed disclosure to combat corruption while early European registries (Germany 1951, EP 1996, Georgia mid-1990s) emphasized business access ("hall passes"). Catalogs registry adoption in Lithuania (2001), Poland (2005), Hungary (2006, repealed 2011), EC (2008), Macedonia (2008), France (2010), Slovenia (2010), Austria (2011).

Relevance: Categorical critique of disclosure scope (lobbyist identity, expenditure, issue, target) maps to the same atomic items we are extracting from US state regimes. Useful for understanding which disclosure-field axes are universal vs. regime-dependent. **Stub-indexed; not factually audited.**

---

### ALTER-EU — Recommendations for Transparency Register Review: Lobby Disclosure Requirements *[stub-indexed]*

- Authors / publisher: ALTER-EU (Alliance for Lobbying Transparency and Ethics Regulation in the EU)
- Date: 2013
- File: `papers/ALTER_EU_2013__transparency_register_review.pdf`
- Extracted text: `papers/text/ALTER_EU_2013__transparency_register_review.txt`

Summary: Short NGO advocacy brief building on ALTER-EU's June 2013 "Rescue the Register!" report. Concrete proposals include €10,000 financial-disclosure bandwidths, mandatory listing of all lobbyists' prior public offices, drop-down legislative-dossier selection for issue disclosure, twice-yearly registration updates on fixed dates, and obligatory reporting of which lobby firms assisted each registrant's lobbying.

Relevance: Marginal — identifies disclosure-field gaps that recur in many state registers; motivates extraction priorities (named lobbyists, prior offices, specific bills). **Stub-indexed; not factually audited.**

---

### AccessInfo / Open Knowledge / Sunlight / Transparency International — International Standards for Lobbying Regulation *[stub-indexed]*

- Authors / publisher: Access Info Europe, Open Knowledge, Sunlight Foundation, Transparency International (joint)
- Date: May 2015
- File: `papers/AccessInfo_2015__intl_lobbying_standards.pdf`
- Extracted text: `papers/text/AccessInfo_2015__intl_lobbying_standards.txt`

Summary: Four-NGO coalition consolidates lobbying-regulation best practice into 38 numbered standards organized into 7 areas (scope, transparency, integrity, participation, oversight, definitions, framework design). Headline factual claim: as of May 2015, only ~20 countries worldwide had national-level lobbying regulation.

Relevance: Normative benchmark catalog — the disclosure items it enumerates (lobbyist identity, subject matter, ultimate beneficiary, targeted institution, expenditure, funding sources, political contributions, revolving-door history) map directly onto the field-level extractions our LLM pipeline must support. **Stub-indexed; not factually audited.**

---

### SOMO — A Structural Problem in the Shadows: Lobbying by Banks in the Netherlands *[stub-indexed]*

- Authors / publisher: Myriam Vander Stichele / SOMO (Centre for Research on Multinational Corporations)
- Date: November 2016
- File: `papers/SOMO_2016__structural_problem.pdf`
- Extracted text: `papers/text/SOMO_2016__structural_problem.txt`

Summary: Investigative NGO report citing regulatory capture as a structural feature of Dutch financial-sector law-making post-2008 crisis. Documents that the Netherlands has no binding lobbying disclosure, with the only official requirement being that one person per organization may register for parliamentary access.

Relevance: Tangential. Sectoral case study rather than measurement framework; primary value is as a worked example of what's invisible without a real disclosure regime. **Stub-indexed; not factually audited.**

---

### Transparency International EU — Open Data to Fight Corruption — Case Study: The EU and Lobbying *[stub-indexed]*

- Authors / publisher: Daniel Freund & Yannik Bendel / Transparency International EU
- Date: 2016 (data current as of 21 December 2015)
- File: `papers/TI_2016__open_data_eu_lobbying.pdf`
- Extracted text: `papers/text/TI_2016__open_data_eu_lobbying.txt`

Summary: TI-EU walkthrough of the Integrity Watch (integritywatch.eu) project, launched October 2014 and expanded June 2015. Combines ~7,000 EC senior-official lobby meetings with Transparency Register profiles and MEP financial declarations, scraped daily via ParlTrack. Notes that across 19 EU countries assessed, the average lobbying-legislation quality score was 31% and 36% for the three EU institutions.

Relevance: Architectural exemplar — a public-facing portal built by linking three distinct disclosure sources (meeting data, register data, financial declarations) is the kind of downstream artifact our state-level pipeline could feed. Reinforces the design choice of treating each source as a separate but linkable entity. **Stub-indexed; not factually audited.**

---

### Council of Europe — Legal Regulation of Lobbying Activities: Recommendation CM/Rec(2017)2 *[stub-indexed]*

- Authors / publisher: Council of Europe, Committee of Ministers
- Date: March 2017 (adopted at 1282nd meeting; July publication)
- File: `papers/CouncilEurope_2017__lobbying_legal_regulation.pdf`
- Extracted text: `papers/text/CouncilEurope_2017__lobbying_legal_regulation.txt`

Summary: Intergovernmental soft-law instrument from the Council of Europe's Committee of Ministers, with detailed explanatory memorandum. Defines lobbying as "promoting specific interests by communication with a public official as part of a structured and organised action aimed at influencing public decision making" and prescribes that consultant, in-house, and sectoral-organization lobbyists all fall within scope. Organized into ten guiding-principle sections (objective, scope, freedom of expression, transparency, registers, ethics, sanctions, integrity, oversight, review).

Relevance: Authoritative European definitional anchor — its scope/definition section is widely cited downstream and offers a comparator for the US state-by-state definitional patchwork our pipeline must reconcile. **Stub-indexed; not factually audited.**

---

### Bednářová — Evaluation of the Government Draft Lobbying Act in the Czech Republic *[stub-indexed]*

- Authors: Pavla Bednářová (Technical University of Liberec)
- Date: June 2020, in *E&M Economics and Management* 23(2)
- File: `papers/Bednarova_2020__lobbying_regulation_quality.pdf`
- Extracted text: `papers/text/Bednarova_2020__lobbying_regulation_quality.txt`

Summary: Cost-benefit-flavored RIA assessment of the 2019 Czech draft Lobbying Act, applying CPI's Hired Guns scoring on the strength axis paired with Krsmanovic's CII on the burden axis (the "Ninefold theory"). Headline numbers: pre-act Czech regime scores CPI = 0 (lowly regulated) / CII = 0 (lowly burdensome); the draft act would move it to CPI = 34 / CII = 35 (both "medium"), comparable to Slovakia/Poland/Hungary/Slovenia/Austria.

Relevance: A downstream user of the CPI Hired Guns rubric — confirms which atomic items remain CPI-derived in non-US applications. **Stub-indexed; not factually audited.**

---

### Carnstone Partners / Meridian Institute — The Responsible Lobbying Framework *[stub-indexed]*

- Authors / publisher: Carnstone Partners (for the Meridian Institute)
- Date: June 2020
- File: `papers/Carnstone_2020__responsible_lobbying_framework.pdf`
- Extracted text: `papers/text/Carnstone_2020__responsible_lobbying_framework.txt`

Summary: Originator-facing voluntary framework (intended for companies and CSOs, not paid lobbyists) compiled from prior standards including TI, OECD, WHO, PRI, and Harvard. Defines five principles (legitimacy, transparency, consistency, opportunity, accountability) with cross-references; the Transparency principle prescribes disclosure of direct/indirect lobbyists, public-sector officials engaged, issues, outcomes sought, frequency, ultimate beneficiaries, monetary spend on direct lobbying, and third-party-association memberships.

Relevance: Prescribes disclosure-content schema from the lobbyist side rather than the regulator side; useful as a cross-check on which fields should be extractable from public filings. **Stub-indexed; not factually audited.**

---

### McKay & Wozniak — Opaque: An Empirical Evaluation of Lobbying Transparency in the UK *[stub-indexed]*

- Authors: Amy Melissa McKay (Exeter) & Antal Wozniak (Liverpool)
- Date: 2020 (online 2019), in *Interest Groups & Advocacy*
- File: `papers/McKay_Wozniak_2020__lobbying_transparency_uk.pdf`
- Extracted text: `papers/text/McKay_Wozniak_2020__lobbying_transparency_uk.txt`

Summary: Cross-source empirical disclosure-quality audit matching the UK Office of the Registrar of Consultant Lobbyists' register against ministerial-meeting publications for the same four quarters. Headline numbers: only ~29% of register clients appear in ministerial-meeting records, and less than 4% of groups in ministerial meetings appear in the register. UK scores 33 on the CPI Hired Guns rubric per Keeling et al. 2017 (placing it in CPI's "medium-robust" band), but the authors dispute this scoring on two specific coding points.

Relevance: A model for the kind of cross-source validation our pipeline should support (e.g., compare registry filings against meeting/disclosure outputs from the executive branch). Directly applicable methodology. **Stub-indexed; not factually audited.**

---

### Roth — Creating a Valid and Accessible Robustness Index (lobbymeter.eu) *[stub-indexed; web-source-only]*

- Authors: Aminata Sarah Roth
- Date: 2020 (project ongoing)
- File: **No local PDF** — Google Sites page is canonical source
- Extracted text: `papers/text/Roth_2020__lobbymeter_robustness_index.txt` (WebFetch summary captured 2026-05-03)
- Source: https://sites.google.com/view/regulating-lobbying/home/work-of-colleagues/creating-a-valid-and-accessible-robustness-index

Summary: Roth's research addresses shortcomings in existing lobbying-regulation measurement tools by developing a new 23-item, 6-subindex robustness index and an online platform (lobbymeter.eu). Identifies critical flaws in prior indices (international-applicability issues, validity/reliability imbalance, equal-weighting failures), applies differentiated item weights, and validates via convergent-validity comparison against Corruption Perceptions Index data (r=0.6807 across 13 jurisdictions).

Relevance: Sits in the same Opheim → CPI → comparative-international lineage as Hogan/Murphy/Chari 2008 and Bednářová 2020. The 23-item index is a candidate input to FOCAL-style cross-walks. **Web-source-only; no PDF audit possible.** The summary text is itself a WebFetch capture, not a paper extraction.

---

### Global Data Barometer — First Edition Report *[stub-indexed]*

- Authors / publisher: Tim Davies & Silvana Fumega (with Jonathan Gray) / Global Data Barometer / ILDA
- Date: 2022 (May 2019 - May 2021 data period)
- File: `papers/GlobalDataBarometer_2022__report.pdf`
- Extracted text: `papers/text/GlobalDataBarometer_2022__report.txt`

Summary: Cross-country survey-based index covering 109 countries, with thematic modules including political integrity and lobbying among others. Headline finding: no country scored over 70/100; mean country score was 34.38/100.

Relevance: Narrow but real — the lobbying sub-indicators within the political-integrity module sit alongside our framework as a comparator, and the Barometer is cited in Lacy-Nichols 2025 as one of three frameworks tracking lobbying-register existence across countries (alongside HATVP 2020/2023 and OECD 2021). **Stub-indexed; not factually audited.**

---

### IBAC — Special Report on Corruption Risks Associated with Donations and Lobbying *[stub-indexed]*

- Authors / publisher: Independent Broad-based Anti-corruption Commission (IBAC), Victoria, Australia
- Date: October 2022
- File: `papers/IBAC_2022__corruption_risks_donations_lobbying.pdf`
- Extracted text: `papers/text/IBAC_2022__corruption_risks_donations_lobbying.txt`

Summary: IBAC's section 162(1) special report to the Victorian Parliament. Identifies four areas of lobbying-regime weakness: too-narrow scope of regulation, privileged access enabled by lobbying, lack of transparency around access, and ineffective controls. Notes that Victoria is one of only three Australian states with no electoral campaign spending cap.

Relevance: Tangential to a US state focus, but the regulatory-gap taxonomy (scope/access/transparency/enforcement) is the same diagnostic axis used by FOCAL and CPI Hired Guns — useful as a non-US comparator point. **Stub-indexed; not factually audited.**

---

## Lobbying & Political Outcomes (empirical)

US state-level empirical studies using lobbying-regulation strength as a treatment or moderator. These *use* the measures rather than *constructing* them.

### Strickland — A Paradox of Political Reform: Shadow Interests in the U.S. States *[stub-indexed]*

- Authors: James Strickland (Univ. of Michigan)
- Date: 2018 (online publication; filename year refers to working paper; SAGE DOI 10.1177/1532673X18788049), in *American Politics Research*
- File: `papers/Strickland_2014__lobbying_laws_interest_groups.pdf`
- Extracted text: `papers/text/Strickland_2014__lobbying_laws_interest_groups.txt`

Summary: Panel-data analysis of all 50 states over three decades using an originally compiled dataset of state lobbyist registrations. Finds that campaign-finance restrictions (not reporting burdens) suppress registration — presenting reformers with a paradox: maximize registration or maximize regulation of the registered, but not both. Estimates that hundreds of unregistered "shadow" groups are lobbying in the US states.

Relevance: Empirical evidence that the registration-rate observable our pipeline measures is endogenous to the regulatory regime itself; should inform how we interpret cross-state registrant-count comparisons. The filename's 2014 date is from a working-paper version — actual publication is 2018. **Stub-indexed; not factually audited.**

---

### Flavin — Lobbying Regulations and Political Equality in the American States *[stub-indexed]*

- Authors: Patrick Flavin (Baylor University)
- Date: 2015 (draft dated January 2014), in *American Politics Research* 43(2)
- File: `papers/Flavin_2015__lobbying_regulations_political_equality.pdf`
- Extracted text: `papers/text/Flavin_2015__lobbying_regulations_political_equality.txt`

Summary: Cross-state observational analysis combining National Annenberg Election Survey income-stratified opinion data with state policy outputs to build a "political equality" index. Finds that states with more stringent lobbying regulations exhibit a weaker income-influence gradient — i.e., regulations are associated with more equal representation in policy outcomes.

Relevance: A downstream-use exemplar — shows what becomes empirically tractable once a credible cross-state regulation-strictness measure exists (the very kind of measure our pipeline aims to produce at higher temporal resolution). **Stub-indexed; not factually audited.**

---

## Compliance & Disclosure Quality (continued — 2026-05-13 additions)

Two additional entries in this category were stub-indexed during the 2026-05-13 audit. They are placed here rather than under "International / Comparative" because both use US OpenSecrets data and concern disclosure-quality measurement; the Lobbying Data Infrastructure addition (LaPira & Thomas 2014) is below.

### Lacy-Nichols, Quinn & Cullerton — Aiding Empirical Research on the Commercial Determinants of Health *[stub-indexed]*

- Authors: Jennifer Lacy-Nichols, Madalyn Quinn, Katherine Cullerton
- Date: 2023, in *Health Research Policy and Systems* 21:56
- File: `papers/Lacy-Nichols_2023__aiding_empirical_research_cdoh.pdf`
- Extracted text: `papers/text/Lacy-Nichols_2023__aiding_empirical_research_cdoh.txt`

Summary: Systematic scoping review of peer-reviewed (4,533 screened, 233 assessed) and grey-literature (285 screened, 280 assessed) studies analyzing lobbying. Catalogs indicators (lobbyist registrations, expenditure, meetings, written submissions, bills, committee participation), datasets (government, NGO, commercial), and methodological approaches used by political-science research, with the aim of importing these into public-health/CDoH research. Notes a 2021 OECD survey finding that only 23 of 41 jurisdictions provided lobbying-disclosure information, with widely varying quality.

Relevance: Maps the indicator taxonomy used in academic lobbying research to the data fields actually present in disclosure regimes — useful for normalizing our extracted-field schema against the indicators downstream researchers actually want. Authorship overlaps the Lacy-Nichols 2024 (FOCAL framework) team. **Stub-indexed; not factually audited.**

---

### Chung, Cullerton & Lacy-Nichols — Mapping the Lobbying Footprint of Harmful Industries *[stub-indexed]*

- Authors: Holly Chung, Katherine Cullerton, Jennifer Lacy-Nichols
- Date: 2024, in *The Milbank Quarterly*
- File: `papers/Chung_2024__mapping_lobbying_footprint.pdf`
- Extracted text: `papers/text/Chung_2024__mapping_lobbying_footprint.txt`

Summary: Power-BI-driven descriptive analysis of 23 years of US federal lobbying expenditures (1998–2020) across four harmful-industry sectors using OpenSecrets data. Headline findings: ultraprocessed food spent the most at $1.15B over the period, followed by gambling ($817M), tobacco ($755M), alcohol ($541M); spending was highly concentrated (two organizations = ~60% of tobacco; four = >50% of alcohol).

Relevance: Demonstrates that OpenSecrets-style sector taxonomies enable longitudinal cross-industry comparison and shows what becomes possible once disclosure data is normalized — a downstream-use exemplar for our pipeline at the state level. **Stub-indexed; not factually audited.**

---

## Lobbying Data Infrastructure (continued — 2026-05-13 additions)

### LaPira & Thomas — Revolving Door Lobbyists and Interest Representation *[stub-indexed]*

- Authors: Timothy M. LaPira (James Madison Univ.) & Herschel F. Thomas III (Univ. of Texas-Austin)
- Date: January 2014, in *Interest Groups & Advocacy* 3
- File: `papers/LaPira_Thomas_2014__revolving_door_lobbyists.pdf`
- Extracted text: `papers/text/LaPira_Thomas_2014__revolving_door_lobbyists.txt`

Summary: Original biographical-data construction + linkage exercise: hand-collected professional histories of ~1,600 registered federal lobbyists linked to ~50,000 quarterly LDA reports. Used to identify a major transparency loophole — the LDA does not require continuous disclosure of "covered official" status, so the revolving door is systematically under-reported in periodic filings. Empirically finds that former-Congress lobbyists tend to be contract (not in-house) and over-specialize in appropriations earmarks.

Relevance: A methodological exemplar of biographical-record linkage against periodic disclosure filings (essentially the same problem we solve at state level) — predates the LobbyView corpus by several years. The covered-official under-reporting finding bears directly on what state-level extraction should *expect* to find vs. what's actually filed. **Stub-indexed; not factually audited.**

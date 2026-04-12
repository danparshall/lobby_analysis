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

Summary: Systematic scoping review of 1,911 records yielding 15 lobbying transparency frameworks (1991–2022). Thematically coded 248 items to synthesize FOCAL (Framework fOr Comprehensive and Accessible Lobbying) — an 8-category, 50-indicator rubric for evaluating what governments disclose about lobbying and how accessible those disclosures are. Designed to assess both lobbyist registers and open/ministerial diaries.

Key findings:
- Of 15 frameworks, financials appeared in 14/15; scope in 13/15; contact log in 13/15; openness/data accessibility in 9/15.
- Only 19 of 109 countries surveyed by the 2021 Global Data Barometer had a lobbyist register available online.
- Weighted frameworks gave highest scores to timeliness, online availability/format, financial disclosures, and enforcement/sanctions.
- Scope and contact logs identified as the two highest-priority categories: narrow scope definitions (e.g., UK/Australia limiting to third-party lobbyists) exclude the bulk of in-house lobbyists; contact logs capture who was contacted, whose interests were represented, and the purpose of the meeting.
- FOCAL's 8 categories: Scope, Timeliness, Openness, Descriptors, Revolving Door, Relationships, Financials, Contact Log. First two assessed from legislation/regulations; remaining six from the register itself.

Relevance: FOCAL provides the most directly applicable disclosure rubric for grading US state lobbying data quality: its 50 indicators map onto the fields an LLM extraction pipeline should populate (lobbyist names, client/employer, targets contacted, date, form of contact, topics, outcomes sought, financial amounts) and its Openness category directly informs how to score state-level data accessibility.

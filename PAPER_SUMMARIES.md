# PAPER_SUMMARIES

Key conclusions per paper, with numerical findings where applicable. This file is too long for every-session reads — get pointed here from `PAPER_INDEX.md`.

---

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

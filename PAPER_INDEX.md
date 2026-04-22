# PAPER_INDEX

One-sentence summary of every paper in `papers/`. Use this as the entry point for literature lookup; once you've found the right paper, check `PAPER_SUMMARIES.md` for the key findings, and `papers/text/` for the full extracted text.

## Entity Resolution & Record Linkage

- **Ornstein (2025)** — fuzzylink integrates pretrained text embeddings into an active learning probabilistic record linkage procedure, using LLM zero-shot labeling to dramatically outperform lexical-similarity-based methods on name/organization matching tasks. File: `papers/Ornstein_2025__fuzzylink.pdf`
- **Enamorado, Fifield & Imai (2019)** — fastLink: a fast, scalable R implementation of the Fellegi-Sunter probabilistic record linkage model that outperforms deterministic methods in FNR and estimation accuracy, scales to 160M+ records, and provides principled post-merge uncertainty quantification. File: `papers/Enamorado_2019__fastlink.pdf`
- **Libgober & Jerzak (2024)** — Introduces a half-billion LinkedIn employment record corpus to train ML and network-based organization name-matching methods, substantially outperforming fuzzy string matching on lobbying and financial datasets with up to 60% gains in F2 score. File: `papers/Libgober_2024__org_linking_open_collab.pdf`

## Lobbying Data Infrastructure

- **Bacik et al. (2025)** — Presents LobbyView, a relational database integrating 1.6M+ federal LDA reports ($87B+ expenditures) with entity disambiguation across clients, registrants, lobbyists, government entities, and legislators, linked to Compustat/Orbis/BoardEx/VoteView; this is the federal gold standard the state-level pipeline aims to replicate. File: `papers/Bacik_2025__lobbyview_network_dynamics.pdf`
- **Kim et al. (2025)** — Uses GPT-4 (with a graph neural network refinement layer) to classify interest group positions on federal bills from LDA report text, validated at 96.93% accuracy vs. human labels on 391 dually-annotated samples, producing 279k bill positions across 12k interest groups — 5× more groups and 7× more bills than MapLight. File: `papers/Kim_2025__ai_bill_positions_lobbying.pdf`
- **Kim (2018)** — LobbyView introduces a federal lobbying database linking interest group reports to congressional bills, with a technical description of the regex + cosine-similarity pipeline used to extract and disambiguate bill IDs from LDA report free text. File: `papers/Kim_2018__lobbyview.pdf`
- **LaPira & Thomas (2020)** — Catalog of the structural quirks, artificial discontinuities, and systematic underuse of the federal LDA database across 25 years of filings, with guidance on correct levels of analysis, double-counting pitfalls, and the need for a lobbying data commons. File: `papers/LaPira_Thomas_2020__lobbying_disclosure_act_at_25.pdf`

## Compliance & Disclosure Quality

- **GAO (2025)** — 18th annual audit of federal lobbying disclosure compliance, finding 93–97% compliance on key filing metrics but a persistent 21% rate of improper covered-position disclosure and 63% of noncompliance referrals still pending as of December 2024. File: `papers/GAO_2025__lda_compliance_audit.pdf`
- **Lacy-Nichols et al. (2024)** — Systematic scoping review of 15 lobbying transparency frameworks synthesized into FOCAL — an 8-category, 50-indicator rubric for evaluating what governments disclose about lobbying and how accessible those disclosures are. File: `papers/Lacy_Nichols_2024__focal_scoping_review.pdf`
- **Lacy-Nichols et al. (2025)** — Follow-up to FOCAL: applies the 50-indicator framework with 0/1/2 weighted scoring (182 points total) to all 28 countries with online lobbyist registers; Canada leads at 49%, US scores 45% (federal scope only, not state-by-state — flagged as future work); scope category scores highest across countries, revolving door + financials lowest. File: `papers/Lacy_Nichols_2025__lobbying_in_the_shadows.pdf`

## State Lobbying Regulation Measurement (FOCAL source frameworks)

These four works are the US-state-focused frameworks cited by Lacy-Nichols et al. 2024 as direct inputs to FOCAL (FOCAL refs #28–30, 33, 35). Together with PRI 2010 (also a FOCAL source) they represent the full set of state-focused scoring-rubric precedents feeding this project's unification work.

- **Opheim (1991)** — First systematic index of state lobby regulation: 22 binary items across three dimensions (statutory definitions 7, disclosure 8, oversight/enforcement 7), tested via OLS on 47 states; finds political culture (moralistic > individualistic > traditionalistic), staff support, and legislative pay predict regulatory stringency (R²=0.58). File: `papers/Opheim_1991__state_lobby_regulation.pdf`
- **Newmark (2005)** — Replicable 0–18 index of state legislative lobbying regulation across six time points 1990–2003 (17 binary items: statutory definitions, prohibited activities, disclosure requirements; +1–4 penalty supplement), validated at r=0.84 against Opheim 1991; mean state regulation rose from 6.54 (1990–91) to 10.34 (2003). File: `papers/Newmark_2005__state_lobbying_regulation_measure.pdf`
- **CPI "Hired Guns" (2007)** — 48-question, 100-point state ranking across 8 categories (Definition of Lobbyist 7, Individual Registration 19, Individual Spending Disclosure 29, Employer Spending 5, Electronic Filing 3, Public Access 20, Enforcement 15, Revolving Door 2); Washington topped at 87 (only state above 80). Web-only source; PDF printed from live page 2026-04-22. File: `papers/CPI_2007__hired_guns_methodology.pdf`
- **Newmark (2017)** — Updated 19-item 0–19 state lobbying regulation index for 2015 (primary-source statute review after Book of the States data collection ended in 2005); explicit comparison against Sunlight Foundation, CPI, and PRI finds the four disclosure measures largely measure different constructs (CPI ↔ PRI-disclosure r=0.04; new index ↔ PRI-accessibility r=0.27). File: `papers/Newmark_2017__lobbying_regulation_revisited.pdf`
- **Clemens et al. / PRI (2010)** — Scores all 50 states on lobbying disclosure law quality (37 criteria) and data accessibility (22 criteria across 8 categories), producing state-by-state rankings; the accessibility rubric maps directly onto pipeline feasibility (machine-readable format, sortability, historical availability). File: `papers/PRI_2010__state_lobbying_disclosure.pdf`

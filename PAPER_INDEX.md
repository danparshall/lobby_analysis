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
- **Clemens et al. / PRI (2010)** — Scores all 50 states on lobbying disclosure law quality (37 criteria) and data accessibility (22 criteria across 8 categories), producing state-by-state rankings; the accessibility rubric maps directly onto pipeline feasibility (machine-readable format, sortability, historical availability). File: `papers/PRI_2010__state_lobbying_disclosure.pdf`

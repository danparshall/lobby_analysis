# PAPER_INDEX

One-sentence summary of every paper in `papers/`. Use this as the entry point for literature lookup; once you've found the right paper, check `PAPER_SUMMARIES.md` for the key findings, and `papers/text/` for the full extracted text.

## Entity Resolution & Record Linkage

- **Ornstein (2025)** — fuzzylink integrates pretrained text embeddings into an active learning probabilistic record linkage procedure, using LLM zero-shot labeling to dramatically outperform lexical-similarity-based methods on name/organization matching tasks. File: `papers/Ornstein_2025__fuzzylink.pdf`
- **Enamorado, Fifield & Imai (2019)** — fastLink: a fast, scalable R implementation of the Fellegi-Sunter probabilistic record linkage model that outperforms deterministic methods in FNR and estimation accuracy, scales to 160M+ records, and provides principled post-merge uncertainty quantification. File: `papers/Enamorado_2019__fastlink.pdf`
- **Libgober & Jerzak (2024)** — Introduces a half-billion LinkedIn employment record corpus to train ML and network-based organization name-matching methods, substantially outperforming fuzzy string matching on lobbying and financial datasets with up to 60% gains in F2 score. File: `papers/Libgober_2024__org_linking_open_collab.pdf`

## Lobbying Data Infrastructure

- **Kim (2018)** — LobbyView introduces a federal lobbying database linking interest group reports to congressional bills, with a technical description of the regex + cosine-similarity pipeline used to extract and disambiguate bill IDs from LDA report free text. File: `papers/Kim_2018__lobbyview.pdf`
- **LaPira & Thomas (2020)** — Catalog of the structural quirks, artificial discontinuities, and systematic underuse of the federal LDA database across 25 years of filings, with guidance on correct levels of analysis, double-counting pitfalls, and the need for a lobbying data commons. File: `papers/LaPira_Thomas_2020__lobbying_disclosure_act_at_25.pdf`

## Compliance & Disclosure Quality

- **GAO (2025)** — 18th annual audit of federal lobbying disclosure compliance, finding 93–97% compliance on key filing metrics but a persistent 21% rate of improper covered-position disclosure and 63% of noncompliance referrals still pending as of December 2024. File: `papers/GAO_2025__lda_compliance_audit.pdf`
- **Lacy-Nichols et al. (2024)** — Systematic scoping review of 15 lobbying transparency frameworks synthesized into FOCAL — an 8-category, 50-indicator rubric for evaluating what governments disclose about lobbying and how accessible those disclosures are. File: `papers/Lacy_Nichols_2024__focal_scoping_review.pdf`

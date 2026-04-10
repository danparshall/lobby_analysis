# Prior-Art Survey: US State Lobbying Data Normalization

**Provenance:** `docs/active/research-prior-art/convos/20260410_scoping-kickoff.md`
**Last updated:** 2026-04-10
**Branch:** `research-prior-art`

## Purpose

Verify the CORDA P7 brief's central claim that no open-source, academic, or commercial effort is systematically scraping, normalizing, and publishing itemized US state lobbying disclosure data across multiple states. This file consolidates the evidence from the scoping-kickoff session and corrects several errors in my earlier verbal survey.

## Headline Conclusion

**The gap is real.** No project in any of the three surveyed categories (civic-tech/open-source, academic, commercial) systematically normalizes state-level lobbying disclosures across multiple states with itemized (rather than aggregate) data and bill-level positions. Existing efforts are either (a) single-state, (b) aggregated-spending-only, (c) federal-only, or (d) paywalled and pitched at lobbyists rather than researchers.

## Civic Tech and Open Source

### OpenSecrets (Center for Responsive Politics)

**What it actually provides for state data:** Registration pairings (lobbyist × client) for all 50 states, and aggregate annual spending totals for roughly 19–20 states. No itemized filing data. No bill-level positions. No systematic free-text analysis.

**Current state of the project (as of this session):**
- State data last updated **December 4, 2023**.
- Public API discontinued **April 15, 2025**.
- Approximately one-third staff layoff in **November 2024**.

**Verdict on the brief's claim:** Directionally accurate with nuance. The brief's "only flat summary data" language is slightly too dismissive — the registration pairings have value — but the core assertion that OpenSecrets does not provide itemized state lobbying data with bill-level detail is correct. Their retreat from the space over the past 18 months also validates the project's urgency.

### FollowTheMoney / National Institute on Money in Politics

Primarily campaign finance. State lobbying coverage is partial and not itemized. Same category as OpenSecrets: useful as a reference source for who is registered, not a source for what they lobbied on or how much they spent per issue.

### LittleSis

Crowdsourced relationship graph connecting people, companies, government, and money. Relies on volunteer curation rather than systematic disclosure ingestion, and coverage is uneven across states. Not a disclosure-normalization project; the closest analog is a Wikipedia for power-mapping. Useful as a complement, not a substitute.

### California Civic Data Coalition

California-only. Probably the single best implementation of what we're trying to build, but it is explicitly scoped to California's CAL-ACCESS system and does not attempt generalization to other states. Worth studying as a reference architecture for one jurisdiction.

### OpenCorporates

Company entity reconciliation across jurisdictions, not lobbying-specific. Relevant to our entity-resolution layer (matching corporate clients in state lobbying filings to canonical company records), but does not ingest lobbying data itself.

### Open States (Plural Policy)

Covers bills, legislators, votes, committees for all 50 states using the Open Civic Data schema. Does not cover lobbying disclosures. We plan to **depend on** Open States via its API (pin version, plan scraper-only fallback). Analyzed separately in `results/opencivicdata-analysis.md`.

### Verdict on civic-tech

No existing civic-tech project fills the gap. The closest pieces are single-state (California Civic Data Coalition), aggregate-only (OpenSecrets, FollowTheMoney), or adjacent (Open States for bills, OpenCorporates for entities). Our project is unambiguously additive to this ecosystem.

## Academic Literature

### LaPira & Thomas 2020 — "The Lobbying Disclosure Act at 25"

**Correction:** I had previously cited this as "Drutman, Grossmann, LaPira" in earlier verbal notes. The actual authors are **Timothy M. LaPira & Herschel F. Thomas**, *Interest Groups & Advocacy* 9(3):257–271 (2020). Drutman and Grossmann are collaborators on related work (notably the "Interest Group Top Tier" chapter in *Can America Govern Itself?*, 2019) but are not authors on this paper.

The paper is the definitive data-quality assessment of federal LDA disclosures at the 25-year mark. Its observations about (a) nested data structures, (b) limits of what is actually reported, (c) definitional drift over time, and (d) the undercount of "revolving door" lobbyists due to the LDA's one-time-disclosure rule all translate directly to the state level, where the data-quality problems are worse. This is the template for our state-level compliance-tracking workstream.

**Access:** Springer (paywalled). DOI: 10.1057/s41309-020-00101-0. Open-access PDF was not located during the session.

### GAO-25-107523 (April 2025) — 2024 LDA Compliance Audit

Fresh evidence on federal compliance gaps that supersedes older numbers I was working from. Key findings:

- From 2015–2024, Congress referred 3,566 cases to the US Attorney's Office for failure to file quarterly reports.
- As of December 2024, approximately 63% of those referrals remained **unresolved**. Only about 36% had been closed as in compliance.
- 21% of quarterly LD-2 reports in GAO's sample listed lobbyists who had not properly disclosed covered positions.
- The USAO's enforcement process is "contact the lobbyist by email, phone, or letter" — not an adversarial process.

The federal regime is the best-resourced lobbying enforcement apparatus in the country and has this compliance gap. State-level compliance is almost certainly worse, and the project's data pipeline is a direct enabler of independent compliance monitoring.

**Access:** https://www.gao.gov/assets/gao-25-107523.pdf (open).

### Bacik, Ondras, Rudkin, Dunkel & Kim 2025 — LobbyView network dynamics

The current canonical LobbyView reference, published via arXiv (2503.11745). Supersedes the 2018 Kim working paper that had been the reference until now. Details in `PAPER_SUMMARIES.md`. Key facts for this survey: 1.6M+ LDA reports integrated, $87B+ in disclosed lobbying expenditures, entity disambiguation across clients / registrants / lobbyists / government entities / legislators, linked to Compustat / Orbis / BoardEx / VoteView. This is the federal gold standard we want to replicate at the state level.

### Kim, Kim, Jeong, Oh & Kim 2025 — GPT-4 bill-position classification

The most directly applicable validation for the LLM-extraction approach. Details in `PAPER_SUMMARIES.md`. Key facts: GPT-4 achieves **96.93% accuracy and 97.19 F1** vs. human labels on a validation set of 391 dually-annotated lobbying report lines, classifying positions as Support / Oppose / Engage / Mention. A graph neural network refinement layer achieves 78.51% accuracy on the harder cases where text alone is insufficient. The final dataset has 279k bill positions across 12k interest groups — 5× more groups and 7× more bills than MapLight.

**Caveat the paper does not discuss:** The 96.93% accuracy is on federal LDA reports. Federal filings are substantially more structured than most state filings. State-level performance is an open question and should be treated as such.

### Ornstein 2025 — fuzzylink (Probabilistic Record Linkage Using Pretrained Text Embeddings)

**Correction:** I had previously cited this as "Libgober & Rashin" in earlier verbal notes. The actual author is **Joe Ornstein** (2025), *Political Analysis*. Libgober has a different 2024 paper with Jerzak ("Linking Datasets on Organizations Using Half A Billion Open Collaborated Records," *PSRM*) that is arguably more relevant for our organization-linkage use case — worth prioritizing that one as a separate follow-up.

Ornstein's method uses pretrained text embeddings combined with zero-shot LLM prompting in an iterative Adaptive Fuzzy String Matching loop. In a voter file application it achieves 95.8% precision and recall versus fastLink's 93.3% / 63.1% (Ornstein's reported numbers). The recall gain is largely from handling nicknames and abbreviations (Trish↔Patricia, United States Telecom Association↔US Telephone Association). R package on CRAN; not a Python-native tool.

### Enamorado, Fifield & Imai 2019 — fastLink

Classical Fellegi-Sunter probabilistic record linkage with a scalable EM implementation. *APSR* 113(2):353–371. Handles missing data via an MAR assumption, estimates false discovery rate and false negative rate, scales to millions of records via hashing and sparse-matrix hash tables. R package on CRAN. This is the baseline to compare any LLM-based approach against for our entity-resolution layer.

### Open questions in the academic literature

- How well does LLM-based bill-position extraction generalize from federal LDA to heterogeneous state formats?
- Which entity-resolution approach (classical Fellegi-Sunter via fastLink, LLM-embedding via fuzzylink, or collaborative-records via Libgober-Jerzak) is best suited to corporate-name matching in lobbying data?
- No paper we found applies these methods to itemized state lobbying data specifically. The project's empirical contribution would be to answer these questions.

## Commercial Tools

### Quorum, FiscalNote, Bloomberg Government

All three serve lobbyists, advocates, and in-house government-affairs teams with bill tracking, legislator profiles, and some aggregated lobbying intelligence. None of them publishes normalized disclosure data as a public or research-accessible product. Subscription prices start in the thousands of dollars per seat per year, which places them structurally outside the research / journalism / civic use case.

### LegiScan, BillTrack50

Bill tracking across states. Analogous to Open States in scope. Do not cover lobbying disclosures.

### Verdict on commercial

The commercial tools serve a different customer (lobbyists needing situational awareness, not researchers needing normalized data) and have not filled the gap. Their existence is not a substitute for the project.

## Corrections Log

Errors in my earlier (unpublished) verbal prior-art survey that this file corrects:

1. **"Drutman, Grossmann, LaPira — The LDA at 25 (2020)"** — wrong authorship. Actual: **LaPira & Thomas 2020**.
2. **"Libgober & Rashin — fuzzylink"** — wrong author. Actual: **Joe Ornstein 2025**. Separate paper by Libgober & Jerzak 2024 (organization linkage, *PSRM*) is a different paper that is arguably more relevant for our use case.
3. **"Kim 2018 LobbyView working paper" as the canonical reference** — superseded. The current canonical LobbyView reference is **Bacik et al. 2025** (arXiv:2503.11745). The 2018 paper is still useful as a reference for the original bill-ID regex methodology.
4. **Federal LDA compliance numbers** — I had been working from older GAO audit numbers. **GAO-25-107523 (April 2025)** is the current reference: 3,566 referrals 2015–2024, ~63% unresolved as of December 2024.

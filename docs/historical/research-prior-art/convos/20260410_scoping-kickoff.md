# 20260410 — scoping-kickoff

**Date:** 2026-04-10
**Branch:** `research-prior-art`
**Participants:** Dan Parshall + Claude

## Summary

Opening session on the lobby_analysis project. We stepped back from the CORDA P7 brief, surveyed the prior art (civic-tech, academic, commercial) to verify the claimed gap, profiled the US state disclosure landscape, and did a deep dive into the Open Civic Data schema proposals to figure out whether to adopt/extend OCD or design a parallel schema. We also set up multi-committer repo infrastructure for Corda fellows and drafted a `COLLABORATOR_PROJECT_INSTRUCTIONS.md` template that non-git-literate fellows can drop into their Claude projects.

The central conclusion is that the gap the brief claims is real: no open-source project, commercial platform, or academic effort systematically scrapes, normalizes, and publishes itemized US state lobbying data across multiple states, and OpenSecrets is actively retreating from the space (API discontinued April 2025, state data stale since December 2023, one-third staff layoff November 2024). The architectural stance is to depend on Open States for bills/legislators (don't fork), adopt Popolo via OCDEP 5 for Person/Org/Post/Membership, and introduce new first-class entities for lobbying concepts rather than retrofitting into OCD Events — a path explicitly validated by examining the **withdrawn** OCD Disclosures proposal, which tried the retrofit approach and failed.

Two self-corrections surfaced during the session: the "LDA at 25" paper is **LaPira & Thomas 2020**, not "Drutman-Grossmann-LaPira" as I had originally cited, and the fuzzylink paper is **Joe Ornstein 2025**, not "Libgober & Rashin." Both corrections are flagged in the prior-art survey results file.

## Topics Explored

- OpenSecrets state-data verification against the brief's "flat summary data" claim
- State disclosure infrastructure tiers (CA/CO/WA/WI top tier; Montana as detailed counterexample)
- GAO-25-107523 (April 2025) as fresh evidence on federal LDA compliance: 3,566 referrals 2015–2024, ~63% unresolved
- Qui-tam/bounty mechanisms for lobbying disclosure — don't exist in any state; structural reason is the FCA frame
- Open Civic Data Enhancement Proposals: OCDEP 5 (People/Orgs/Posts/Memberships, accepted), OCDEP 6 (Bills, accepted), withdrawn Disclosures proposal (cautionary tale), draft Campaign Finance Filings proposal (pattern to adopt)
- Open States dependency vs. fork decision
- LobbyView (Bacik et al. 2025) as the federal gold standard and reference methodology
- GPT-4 bill-position classification at 96.93% accuracy (Kim et al. 2025) as validation for the LLM-extraction approach
- Collaborator onboarding: Claude Projects sharing (now available on Team/Enterprise) and the fellow-onboarding template

## Provisional Findings

See `RESEARCH_LOG.md` for the detailed findings list. Top-line:

1. The claimed gap is real and validated by multiple lines of evidence.
2. Priority-state shortlist: CA, CO, NY, WA, TX, WI, IL, FL (8 states).
3. Only 8 states statutorily require all of (compensation + bills lobbied + position taken): CO, IA, MA, MT, NE, NJ, RI, WI.
4. The Open Civic Data withdrawn Disclosures proposal is a cautionary tale — we should not retrofit lobbying into OCD Events.
5. GPT-4 position classification works at 96.93% accuracy on federal LDA text — state-level performance remains an open question since state filings are substantially less structured.

## Decisions Made

- Branch name: `research-prior-art`.
- Architectural stance: depend on Open States via its API, don't fork.
- Schema direction: adopt Popolo via OCDEP 5, introduce new first-class lobbying entities (LobbyingFiling, LobbyingPosition, LobbyingExpenditure, Gift, LobbyingEngagement), adopt Epton's Filing → Sections + `filing_actions` amendment pattern, add field-level provenance with confidence scores, add a compliance-tracking layer.
- Paper ingestion scope for this commit: only the 2 papers actually downloaded as clean PDFs this session (Bacik 2025, Kim 2025). Five more candidates deferred — see "Follow-ups" below.
- Collaborator onboarding: ship `COLLABORATOR_PROJECT_INSTRUCTIONS.md` as a drop-in template with variables at the top.

## Results Files

- `results/prior-art-survey.md` — corrected and consolidated prior-art survey
- `results/state-infrastructure-tiers.md` — Tier 1–4 breakdown, "three keys" analysis, F Minus 2024 caveat
- `results/opencivicdata-analysis.md` — OCDEP 5, OCDEP 6, withdrawn Disclosures, draft Campaign Finance Filings + lessons
- `results/schema-design-questions.md` — Epton-style questions to answer for a future lobbying schema OCDEP

## Papers Added

Only 2 out of 7 candidates were successfully downloaded this session due to proxy restrictions on the session's shell environment. See follow-ups below for manual retrieval instructions.

- Bacik et al. 2025 — "Measuring the dynamical evolution of the United States lobbying network" (arXiv:2503.11745). `papers/Bacik_2025__lobbyview_network_dynamics.pdf` + extracted text.
- Kim et al. 2025 — "Measuring Interest Group Positions on Legislation: An AI-Driven Analysis of Lobbying Reports" (arXiv:2504.15333). `papers/Kim_2025__ai_bill_positions_lobbying.pdf` + extracted text.

## Follow-ups

### Papers to fetch manually (proxy blocks shell download in this environment)

These are priority-ordered by relevance to the pipeline work. Use the `add-paper` skill once the PDFs are in `papers/`.

| Paper | URL | Why it matters |
|---|---|---|
| Libgober & Jerzak 2024 — "Linking Datasets on Organizations Using Half-a-Billion Open-Collaborated Records", *PSRM* | https://arxiv.org/pdf/2302.02533 (arXiv v5 = published PSRM version) | **Most directly applicable entity-resolution paper for our use case.** First empirical application in the paper is matching ~700 lobbying-record organizations to ~7,000 listed US companies — essentially our state-lobbying-client → SEC EDGAR matching problem. Training corpus is a half-billion LinkedIn alias scrape. Newly surfaced this session — bumps ahead of Ornstein. |
| Ornstein 2025 — fuzzylink (Probabilistic Record Linkage Using Pretrained Text Embeddings), *Political Analysis* | https://joeornstein.github.io/publications/fuzzylink.pdf | LLM-embedding record linkage; outperforms fastLink on nickname and abbreviation cases. The author's primary applications are person-name matching, but the technique generalizes |
| Enamorado, Fifield & Imai 2019 — fastLink, *APSR* 113(2):353–371 | https://imai.fas.harvard.edu/research/files/linkage.pdf | Classical Fellegi-Sunter probabilistic record linkage. Baseline to compare both Libgober-Jerzak and Ornstein against |
| LaPira & Thomas 2020 — "The Lobbying Disclosure Act at 25" | Springer paywall at https://link.springer.com/article/10.1057/s41309-020-00101-0 — may require institutional access | Definitive data-quality assessment of federal LDA disclosures; direct template for our state-level compliance-tracking workstream |
| Lacy-Nichols, Baradar, Crosbie & Cullerton 2024 — "Lobbying in the Sunlight: A Scoping Review of Frameworks" (FOCAL), *Int J Health Policy Manag* | https://www.ijhpm.com/article_4651_43e3b5f9020f5754cb8e9fe5529287b8.pdf | Synthesizes 15 existing lobbying transparency frameworks into FOCAL (8 categories, 50 indicators). Directly applicable as a scoring rubric for our state-by-state compliance layer |
| GAO-25-107523 (April 2025) — 2024 LDA Compliance Audit | https://www.gao.gov/assets/gao-25-107523.pdf | Fresh federal compliance evidence: 3,566 referrals 2015–2024, ~63% unresolved. Anchor for the compliance-gap section of any policy writeup |
| Kim 2018 — LobbyView original working paper | https://web.mit.edu/insong/www/pdf/lobbyview.pdf | Superseded by Bacik 2025 as the canonical LobbyView reference, but contains the original bill-ID regex extraction methodology |

**Note on the Libgober & Jerzak entry:** I had originally listed this as a "bonus" candidate without a clear URL or detailed rationale. After locating the open-access arXiv version and reading the abstract, the paper's first application turns out to be a regulator-meeting → stock-ticker matching problem that is structurally identical to our state-lobbying-client → SEC EDGAR problem. That moves it from "interesting adjacent work" to "directly applicable methodology paper" and bumps it to the top of the entity-resolution group. The training-corpus source is LinkedIn (a half-billion-record scrape of organization aliases and name-to-name links), not OpenCorporates as I had guessed in earlier verbal notes.

### Other follow-ups

- Verify F Minus 2024 methodology before weighting it in state selection.
- Check Montana PLORS post-October-2025 export formats once the all-electronic mandate has settled.
- Pull one real filing from each of CA, CO, TX to stress-test the draft schema against actual data before committing to it.
- Consider a standalone schema-design session that converts `schema-design-questions.md` into a draft OCDEP-style proposal.

## Open Questions

- **State-level LLM position-classification accuracy.** Kim et al. 2025 achieves 96.93% on federal LDA, but state filings vary wildly in structure — many are free-form PDFs or poorly-formed web forms. The pipeline should treat this as an empirical question to answer with per-state validation sets, not a solved problem.
- **Entity resolution across states.** fuzzylink (LLM embeddings) vs. fastLink (classical Fellegi-Sunter) vs. Libgober-Jerzak (LinkedIn-corpus organization linkage) is an unsettled methodological choice. Depends on how much lexical vs. semantic variation exists in corporate names across state filings — another empirical question.
- **Amendment handling semantics.** Epton's `filing_actions` pattern assumes an amendment supersedes or modifies a prior version via an explicit link. Several states don't track amendment lineage at all — filings just get overwritten or accumulated without linkage. Need a "provenance-only, no lineage" fallback mode in the schema.
- **Compliance-layer as first-class or as a view?** Unsure whether the compliance/enforcement signal should live as first-class entities in the schema (Violation, Referral, Penalty) or as a derived view over the filing and filer data. Leaning first-class because enforcement actions are the policy payload, but not decided.

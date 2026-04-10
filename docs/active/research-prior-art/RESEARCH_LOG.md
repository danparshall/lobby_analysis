# Research Log: research-prior-art

**Created:** 2026-04-10
**Purpose:** Scoping phase 1 for the US State Lobbying Data LLM Pipeline — prior-art survey, state infrastructure assessment, and Open Civic Data schema analysis before any code is written.

---

## Session: 2026-04-10 — scoping-kickoff

### Topics Explored

- Prior-art survey across three categories: civic-tech/open-source, academic literature, and commercial tools, with a focus on state-level lobbying disclosure normalization.
- Verification of the CORDA P7 brief's central premise that OpenSecrets/FollowTheMoney provides "only flat summary data" for state lobbying. Verdict: directionally accurate, with nuance (registration pairings for all 50 states + aggregate spending for 19–20 states, no itemization, no bill-level positions, data last updated December 2023).
- State infrastructure quality tiers for disclosure portals, with candidate priority-state shortlist for the initial 5–8.
- Montana as a detailed counterexample: dual paper+electronic filing regime with ~80% electronic, 2024 legislative audit exposing deep compliance gaps, October 2025 statutory shift to all-electronic via HB 804 that won't affect historical filings.
- Enforcement gap between statutory penalties and actual enforcement. GAO-25-107523 (April 2025) documents 3,566 LDA referrals 2015–2024 with ~63% still unresolved as of Dec 2024. Qui-tam/bounty mechanisms do not exist for lobbying disclosure in any state — only unrewarded citizen complaints. Structural reason: qui tam is a creature of the False Claims Act, which addresses fraud against government money, and lobbying non-disclosure is an informational harm that doesn't fit the FCA frame.
- Open Civic Data schema deep-dive: OCDEP 5 (People/Orgs/Posts/Memberships built on Popolo), OCDEP 6 (Bills), the **withdrawn** Disclosures proposal (Bob Lannon, tried to model lobbying via Event overloading — failed), and the **draft** Campaign Finance Filings proposal (Abraham Epton, Filing → Sections → Transactions pattern with amendment handling via `filing_actions`).
- Delta between Open States as it exists today (bills/legislators/votes, Open Civic Data schema, all 50 states) and a hypothetical lobbying extension. Conclusion: depend on Open States, don't fork it — the entity model, format heterogeneity, entity-resolution burden, and cross-state linkage requirements make this a separate pipeline that references Open States rather than extending it.
- Collaborator onboarding: Claude Projects now supports sharing on Team/Enterprise plans (as of 2026), but the drop-in `COLLABORATOR_PROJECT_INSTRUCTIONS.md` template is still useful for fellows on individual Pro accounts.

### Provisional Findings

Items that are currently supported but are not settled and may change:

1. **No open-source project systematically scrapes, normalizes, and publishes itemized US state-level lobbying disclosure data across multiple states.** This is the central gap the project addresses. Closest existing prior art: California Civic Data Coalition (California-only), LittleSis (crowdsourced relationship graph, not systematic disclosure ingestion), and OpenCorporates (entity reconciliation infrastructure, not lobbying-specific).
2. **The commercial legislative-intelligence market (Quorum, FiscalNote, Bloomberg Government) has not filled this gap either.** They serve lobbyists and advocates who need bill tracking, not researchers/journalists/public who need normalized disclosure data.
3. **Candidate priority states for the initial 5–8:** California, Colorado, New York, Washington, Texas, Wisconsin, Illinois, Florida. Selected for a combination of (a) Tier 1/2 data accessibility, (b) political and economic significance, and (c) diversity of disclosure architectures (to stress-test generalization).
4. **OpenSecrets is retreating from this space.** API discontinued April 2025; state data last updated December 2023; one-third staff layoff November 2024. Validates the project premise and increases urgency.
5. **LobbyView (Bacik et al. 2025) is the federal gold standard** we are trying to build a state-level analog of. They integrate 1.6M+ LDA reports, $87B+ in disclosed expenditures, with entity disambiguation linked to Compustat/Orbis/BoardEx/VoteView. Their methodology (regex bill extraction, blocked name disambiguation, PostgreSQL relational schema) is a direct template for our entity resolution and data model work — but only for the federal data they actually process.
6. **GPT-4 can classify bill positions (Support/Oppose/Engage) from lobbying report text at 96.93% accuracy vs. human labels** on 391 dually-coded samples (Kim et al. 2025). This validates the LLM-extraction approach for our pipeline. Caveat: their pipeline is applied to federal LDA reports, which are substantially more structured than most state filings — state-level performance is an open question.
7. **The LaPira & Thomas (2020) "LDA at 25" paper and the GAO annual LDA compliance audits document severe federal compliance gaps** even though the federal regime is the best-resourced lobbying enforcement apparatus in the country. State-level compliance is almost certainly worse.
8. **The Open Civic Data withdrawn Disclosures proposal is a cautionary tale.** It tried to retrofit lobbying into existing OCD primitives (Event + related_entities + role-note strings) rather than introducing first-class entities. The proposal was withdrawn, presumably because the approach is fundamentally insufficient — no itemized financial data, no typed bill linkage, no amendment handling, and all "participants" flattened into a single untyped list distinguished only by free-text notes. The project should not follow this pattern.

### Decisions Made

- **Branch name: `research-prior-art`** (not `research/prior-art-and-schema-scoping` or other candidates).
- **Convo file name: `20260410_scoping-kickoff.md`.**
- **Architectural stance: depend on Open States, don't fork.** Use Open States as the canonical source for bills and legislators; the lobbying pipeline is a separate project that references it. Pin API versions and plan for Open States scraper-only fallback if the hosted API becomes unusable.
- **Schema direction: adopt Popolo via OCDEP 5 for Person/Organization/Post/Membership. Introduce new first-class entities for lobbying concepts (LobbyingFiling, LobbyingPosition, LobbyingExpenditure, Gift, LobbyingEngagement). Adopt Epton's Filing → Sections pattern and `filing_actions` amendment handling.** Do not retrofit into OCD Events. Add two things OCD lacks: field-level extraction provenance and a compliance-tracking layer.
- **Paper ingestion: only the 2 papers downloaded cleanly this session are being added via add-paper (Bacik 2025 LobbyView, Kim 2025 AI bill positions).** The other 5 candidate papers are proxy-blocked for shell curl in this environment — listed as follow-ups with URLs for manual ingestion next session.

### Results

- `results/prior-art-survey.md` — corrected and consolidated prior-art survey (civic-tech, academic, commercial).
- `results/state-infrastructure-tiers.md` — state-by-state disclosure infrastructure tiers with the "three keys" analysis and the F Minus 2024 caveat.
- `results/opencivicdata-analysis.md` — OCDEP 5, OCDEP 6, withdrawn Disclosures, and draft Campaign Finance Filings analysis with design rationale.
- `results/schema-design-questions.md` — Epton-style "questions to answer" for a future lobbying schema OCDEP.

### Corrections to Earlier Work

Errors in my earlier verbal prior-art survey (not yet committed anywhere) that need to land in the results files:

1. **"Drutman, Grossmann, LaPira — The LDA at 25 (2020)" is incorrect.** The actual authors are **LaPira & Thomas (2020)**, *Interest Groups & Advocacy* 9:257–271. Drutman and Grossmann are collaborators on related work but not authors on this paper.
2. **"Libgober & Rashin — fuzzylink" is incorrect.** The actual author is **Joe Ornstein (2025)**, *Political Analysis*, "Probabilistic Record Linkage Using Pretrained Text Embeddings." Libgober has a different 2024 paper with Jerzak ("Linking Datasets on Organizations Using Half-a-Billion Open-Collaborated Records," *PSRM*; arXiv:2302.02533) that is more directly relevant since it (a) is specifically about organization linkage, and (b) has a first empirical application that is structurally identical to our state-lobbying-client → SEC EDGAR matching problem (~700 lobbying-record orgs matched to ~7,000 listed companies). Open PDF: https://arxiv.org/pdf/2302.02533. The training corpus is a LinkedIn alias scrape, not OpenCorporates.
3. **Newer evidence on federal LDA compliance gaps** than what I originally cited: GAO-25-107523 (April 2025) shows 3,566 referrals 2015–2024 with ~63% still unresolved as of Dec 2024. Worth citing alongside the LaPira-Thomas 2020 paper.
4. **Newer LobbyView reference:** Bacik, Ondras, Rudkin, Dunkel & Kim (2025/2026), *"Measuring the dynamical evolution of the United States lobbying network"*, arXiv:2503.11745 — this supersedes the 2018 Kim working paper as the canonical LobbyView reference.

### Next Steps

- **Ingest the 5 deferred papers via add-paper in a follow-up session** (LaPira-Thomas 2020, Ornstein 2025 fuzzylink, Enamorado-Fifield-Imai 2019 fastLink, Lacy-Nichols et al. 2024 FOCAL, GAO 2025 LDA compliance). URLs are in the convo summary.
- **Verify the F Minus 2024 methodology before weighting it in state selection.** The report's headline finding (27 states failing, Colorado alone receiving an A) should make any analyst want to look under the hood.
- **Check Montana PLORS post-October-2025 export formats** once the all-electronic mandate has had time to settle.
- **Pull one real filing from each of 3 priority states (California, Colorado, Texas)** to stress-test the draft schema against actual data before committing to it.
- **Consider a standalone schema-design session** that converts the "Questions to answer" in schema-design-questions.md into a draft OCDEP-style proposal.
- **Prioritize Libgober & Jerzak 2024 in the next paper-ingestion pass.** It's open-access on arXiv (https://arxiv.org/pdf/2302.02533, on the allowed-domains list so I can fetch it directly next session) and its first empirical application is the same matching problem we have (~700 lobbying-record orgs to ~7,000 listed companies). Should be ingested ahead of Ornstein's fuzzylink.

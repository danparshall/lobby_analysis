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

---

## Mid-session update: 2026-04-12 — paper retry + targeted searches

**Libgober & Jerzak 2024 fetched.** arXiv is on the allowed domains list, so `curl https://arxiv.org/pdf/2302.02533` worked directly. PDF (1.3MB) saved to `papers/LibgoberJerzak_2024__org_linkage_linkedin.pdf`; text extracted to `papers/text/` (2,640 lines, some font-encoding warnings from pdftotext but content readable). **Not yet summarized** — full read and PAPER_SUMMARIES entry deferred to next session, which is what the add-paper skill requires.

**Ornstein 2025 still unreachable.** Re-checked `joeornstein.github.io` (proxy-blocked) and tried raw.githubusercontent.com paths for both the `fuzzylink` code repo and the author's `github.io` source repo (all returned 000 — raw.githubusercontent.com is not on the allowlist either). The paper exists only at the author's github.io Pages site and via CRAN; no arXiv mirror. **Options for next session:** (a) fetch via `web_fetch` as text-only (no PDF binary), (b) Dan grabs it manually and drops it in `papers/`, (c) skip — Splink can serve as the Python-native alternative and the paper's ideas are well-summarized in the abstract + GitHub README we already have in context.

**Targeted searches for new-gap papers:**
- **State-level lobbying data papers:** one strong hit so far — **Lacy-Nichols et al. 2024 FOCAL** (already on the deferred list) explicitly notes in its introduction that lobbying data research faces "challenges accessing, extracting, cleaning, coding and analysing" that the authors have themselves faced. Worth ingesting sooner than I'd originally placed it.
- **Data extraction / heterogeneous government forms:** no single standout paper found yet. The most relevant adjacent literature is in the legal-informatics space (e.g., arXiv 2601.05609 "Data Augmented Pipeline for Legal Information Extraction") but the fit is indirect. More targeted searches needed in a future session — the right query terms are probably "document understanding government forms" or "semi-structured PDF extraction civic data" rather than "state lobbying NLP."
- **Commercial baseline discovered:** Dewey Data's "U.S. Lobbying Data" product applies proprietary entity resolution to federal LDA filings and **maps publicly traded entities to stock ticker symbols**. This is federal-only and commercial, but confirms the Libgober-Jerzak approach (lobbying-org → stock-ticker matching) is live in industry, not just academic.
- **Splink** (Python/DuckDB Fellegi-Sunter record linkage, from the UK Ministry of Justice) — confirmed to exist; worth benchmarking against fastLink and Libgober-Jerzak in the entity-resolution empirical pass. Not a paper, so not a candidate for add-paper, but should be noted in schema-design-questions.md as a candidate implementation.

**Updated "right size" for the working set:** 5 → 6 load-bearing papers. Add Libgober-Jerzak (ingested), keep the Ornstein/Enamorado pending for context on the ER decision, and promote Lacy-Nichols FOCAL from reference-useful to load-bearing because it's the closest thing to a state-level data-access paper in the set. State-level data papers and heterogeneous-form extraction papers remain genuine gaps — worth a dedicated follow-up search session with better query terms.

---

## Mid-session update: 2026-04-12 (continued) — reading notes on Libgober-Jerzak and Lacy-Nichols

Read the two highest-leverage papers from the newly-merged set (not the full seven). Deferring Enamorado, Ornstein, LaPira-Thomas, Kim 2018, and GAO 2025 to follow-up sessions — they don't change pending decisions, just confirm triangulations.

### Libgober & Jerzak 2024 — key findings from the reading

**Task 1 (our problem, literally):** Matching ~700 organization names from regulator meeting logs to ~7,000 US public companies, using Libgober 2020's hand-coded matches as ground truth. Best F2 score across all methods is just over 0.6 — the best performer is "Bipartite-ML" (bipartite network representation combined with ML distance measure). LinkedIn-assisted approaches beat fuzzy string matching across the full range of acceptance thresholds.

**Concrete failure case worth remembering:** Fuzzy matching fails to link "HSBC Holdings PLC" to "HSBC" because their string distance (0.57) is worse than the fuzzy match "HSBC Holdings PLC" → "AMC Entertainment Holdings, Inc." (0.13). LinkedIn's alias directory has an exact match and rescues the pair. This is exactly the corporate-hierarchy failure mode we'd see in state lobbying data at scale.

**Runtime numbers matter for our scale.** On 2024 hardware for the 700 × 7,000 task:
- Fuzzy matching: 0.27 min
- Machine learning (no network): 1.63 min
- Bipartite network only: 13.12 min
- **Bipartite-ML (best performer): 251.38 min (~4 hours)**
- Markov-ML: 113 min

Back-of-envelope: a 10,000 × 10,000 match with Bipartite-ML would take 2–3 days. A 100,000 × 100,000 would take ~255 days without optimization. The paper flags locality-sensitive hashing and parallelization as mitigations. For our project, a full federal LobbyView × state pipeline match would be in the 100k × 100k range — **we cannot just adopt Bipartite-ML uncritically; scaling is a real concern.**

**Task 2 (also substantively important):** Matching Fortune 1000 companies to OpenSecrets lobbying expenditures 2013–2018. The human-matched ground-truth coefficient for log(assets) → log(lobbying) is about 2.5. **Fuzzy matching underestimates this coefficient by about half** (attenuation bias from noise). LinkedIn-assisted methods recover a coefficient within the 95% CI of the ground truth; fuzzy and DeezyMatch do not. **This is direct evidence that ER quality materially changes substantive findings in lobbying research** — not just a methods-paper abstract concern.

**Training corpus note:** The LinkedIn data is from 2017. The paper flags this as a limitation for out-of-sample organizations (Task 3: matching YCombinator startups and PPP loan recipients, which didn't exist or weren't well-represented in the 2017 scrape). For state lobbying data where many regional entities (local trade associations, family-owned firms, state-specific LLCs) may not have LinkedIn pages, this is a real concern. **State-level performance remains empirically untested.**

### Lacy-Nichols et al. 2024 FOCAL — key findings from the reading

**FOCAL synthesizes 15 frameworks.** Of these, **four are specifically US-state-focused** and I had not previously identified them. This closes part of the "state-level lobbying data paper" gap I was searching for last session:

| Framework | Year | Items | US state-specific? |
|---|---|---|---|
| Opheim — Index of state lobbying regulation law | 1991 | 22 | Partly |
| Newmark — Index to measuring state lobbying regulation | 2005 | 18 | Partly |
| Center for Public Integrity — "Hired Guns" state rankings | 2007 | 48 | Partly |
| Pacific Research Institute — State disclosure law criteria | 2010 | 47 + 22 | Yes (fully) |

**Pacific Research Institute 2010 is the most directly applicable** — it has explicit separate "State disclosure law criteria" (47 items) and "State lobbying information accessibility criteria" (22 items, 8 categories: data availability, website existence, website identification, current data availability, historical data availability, data format, sorting data, simultaneous sorting). That "information accessibility" dimension is exactly our compliance-layer rubric.

**FOCAL's own 8 categories (50 indicators):** scope, timeliness, openness, descriptors, revolving door, relationships, financials, contact log. This is also directly usable as a compliance-layer rubric — arguably better than my earlier schema-design-questions.md Q2 thinking because it separates "what is disclosed" from "how accessible the disclosure is."

**Important scope caveat:** FOCAL *excludes* enforcement, sanctions, ethics, and whistleblower protections "for feasibility." So if we want a compliance layer that includes enforcement signal (referrals, penalties, violations), FOCAL gives us the disclosure-quality half of the rubric but not the enforcement half. The enforcement half has to come from GAO-25-107523 and state-level enforcement records directly.

### What this reading changes

1. **The "state-level lobbying data paper" gap is partially closed.** Opheim 1991, Newmark 2005, CPI 2007, and especially **Pacific Research Institute 2010** are prior art I should have found earlier. PRI 2010 in particular should be tracked down and ingested — it's the most direct methodological predecessor to what we're building. **New follow-up: find PRI 2010 (likely a policy report, not a peer-reviewed paper; PRI is a free-market think tank so this is a hypothesis-generator not a ground truth).**
2. **The entity-resolution decision has a more concrete answer.** Libgober-Jerzak's Bipartite-ML is the best performer on the most relevant benchmark, but runtime concerns make it non-trivial to adopt at our scale. **Practical direction: benchmark Bipartite-ML, fastLink, and Splink on a 500-row labeled subset of state lobbying clients vs. SEC EDGAR before committing.** The benchmark design matters more than the methodology choice.
3. **The compliance-layer rubric now has two candidate templates:** FOCAL (8 cat × 50 ind, disclosure-quality focus) and PRI 2010 (8 cat × 22 ind, accessibility focus). These should be reconciled with each other and with the GAO/enforcement-gap evidence into a single state-compliance scoring rubric. **New follow-up: draft a compliance-rubric synthesis document.**

### Not read this session (and why)

- **Enamorado (fastLink)** — I have the full text in context from last session's web_fetch; reading the committed PDF adds nothing.
- **Ornstein (fuzzylink)** — would confirm triangulation on ER methodology, but Libgober-Jerzak's Bipartite-ML already dominates the benchmark we care about.
- **LaPira & Thomas 2020** — historical context for federal compliance gaps; GAO-25-107523 covers the current state.
- **Kim 2018** — fully superseded by Bacik 2025.
- **GAO-25-107523** — key numbers already extracted last session (3,566 referrals, 63% unresolved).
- **Lacy-Nichols full paper** — read only the framework table and category summary; did not read the full methods section or the 50-indicator detail. Worth a fuller read when designing the compliance rubric.

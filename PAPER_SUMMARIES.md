# PAPER_SUMMARIES

Key conclusions per paper, with numerical findings where applicable. This file is too long for every-session reads — get pointed here from `PAPER_INDEX.md`.

## Papers

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

---

**Format for new entries:**

```
## [short_name] ([year])

**Citation:** [authors, title, venue]
**File:** `papers/[filename].pdf`
**Extracted text:** `papers/text/[filename].txt`

### Key findings

- [finding with numbers if applicable]
- [finding]

### Method

[brief description of method]

### Notes for our project

[why this paper matters for lobby_analysis]
```

# Compendium 2.0 Synthesis — Plan for next session

**Goal:** Move from 26 per-paper rubric extracts to a defensible **core item set** for compendium 2.0 (and, alongside it, schema v2.0). Two intermediate deliverables: (a) acquire the still-missing predecessor papers and CSG/COGEL reference works; (b) descriptive cross-rubric statistics (intersection / union / item-frequency-by-rubric) that inform a principled selection method.

**Originating conversation:** [`docs/active/compendium-source-extracts/convos/20260503_per_paper_extraction_execution.md`](../convos/20260503_per_paper_extraction_execution.md)

**Context:** The 2026-05-03 session extracted 26 source papers, of which **14 construct their own measurement rubric**. The 12 non-rubrics are still useful as evidence (empirical applications show which items researchers actually use; methodological reviews surface adjacent measurement universes; federal-data papers like Kim 2018 / Chung 2024 / LaPira & Thomas 2014 anchor the LobbyView-for-states framing). With 14 rubrics in hand, "PRI is one of N" is now empirically grounded — there is no single rubric to anchor on. Three audits this branch have caught the same structural pattern (compendium 1.x PRI-shaped, schema v1.1 Literals PRI-shaped); the next move is to derive the item set *from the cross-rubric data itself*, not from any single rubric's atomization.

**Confidence:** Procedural (acquisition + descriptive stats are mechanical) on the first two deliverables. Exploratory on the principled-subset method — the user has already cautioned against pure frequency-based filtering (universal-agreement items are likely the lowest-information ones), so part of this work is testing several selection approaches against each other.

**Architecture:** Pure analysis + acquisition session. No code changes to `src/lobby_analysis/models/` yet — schema v2.0 design comes after the item-set is settled. Outputs are: new papers in `papers/` + text in `papers/text/`; new TSV+MD per-paper extracts in `results/items_*.tsv|.md` for each newly-acquired rubric; a cross-rubric analysis doc in `results/`; a brainstorm doc on item-clustering and subset-selection methods.

**Branch:** Continues on `compendium-source-extracts` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts/`). No new branch.

**Tech Stack:** None new. Python (pandas) for the cross-rubric stats if useful; otherwise grep + manual review against the 26+ TSV files. Optional: an LLM-assisted clustering pass over the union of all paper-defined items.

---

## Why this plan exists

Three threads from the 2026-05-03 session converge on this work:

1. **The acquisition list grew substantially during extraction.** Each paper's lit review surfaced predecessors we hadn't seen; several papers operationalized rubrics whose source documents we don't have (CII methodology in Bednařová; TI-UK 4-criterion rubric in TI 2016; Piotrowski & Liao 2012 usability framework in McKay & Wozniak; the underlying statute-tradition reference works — CSG Blue Book, Book of States vintages, COGEL Blue Books, State Capital Law Firm Group handbook — for Opheim 1991 / Newmark 2005 / Newmark 2017 / Strickland 2014). Lacy-Nichols 2023 also surfaced an entire parallel CDoH measurement universe (7 frameworks) FOCAL didn't review. Until those papers are in hand, the rubric corpus is incomplete and any "core item set" derived from it is biased toward easy-to-retrieve sources.

2. **We have not yet measured cross-rubric overlap.** 14 rubrics × N items each is a small enough dataset to characterize directly: how many items appear in 1 rubric only, 2, 3, …, 14? Where does the median item sit? Is there a natural elbow? Is there a "core" of items that show up in ≥6 rubrics? Until we have these descriptives, any selection method is being designed in the dark.

3. **The selection method itself needs structured exploration**, not ad-hoc judgment. The user has already raised one principled concern: "most-commonly-used" filtering may over-index on the lowest-information items. The session needs to compare at least 2–3 selection approaches against each other before committing to one.

---

## In scope

1. **Acquire missing papers** per the consolidated acquisition list in Tasks #10 + #11.
2. **Extract additional rubric items** from any newly-acquired *measurement-framework* papers (skip empirical applications and surveys — same heuristic as the 2026-05-03 session).
3. **Descriptive cross-rubric statistics** — intersection / union / item-frequency-by-rubric / state-of-overlap visualizations.
4. **Brainstorm document** on item-clustering and principled-subset-selection methods, with at least 2–3 candidate approaches articulated.
5. **Defer:** writing compendium-2.0 itself, building schema v2.0 Literal types, dispatching state-statute-extraction agents. All of those are downstream of this plan's deliverables.

## Explicitly NOT in scope

- Compendium 2.0 design itself (separate plan, written after this plan ships).
- Schema v2.0 (Literal types, SMR field rebuild) — separate plan after compendium 2.0.
- Reading PRI 2010 in any form. PRI is still out of bounds; the ⛔ block in STATUS.md still applies.
- Federal-only extracts unless explicitly approved (LaPira 2020 LDA at 25, GAO 2025 — currently deferred).
- Non-acquired papers from the email-author wave if Task #10's email skill hasn't been run yet.

---

## Sequencing

### Step 1: Pre-flight (implementing agent)

Read in order:
- `CLAUDE.md` (worktree root).
- `STATUS.md` and `README.md` at repo root.
- `docs/active/compendium-source-extracts/RESEARCH_LOG.md` — the 2026-05-03 session entry is the immediate predecessor.
- `docs/active/compendium-source-extracts/convos/20260503_per_paper_extraction_execution.md` — the originating convo.
- This plan.
- The auto-memory `feedback_pri_not_privileged.md` (PRI fully out of bounds rule).

Do NOT read: `papers/text/PRI_2010__state_lobbying_disclosure.txt`, `compendium/disclosure_items.csv`, `compendium/framework_dedup_map.csv`, `docs/COMPENDIUM_AUDIT.md`. PRI is still out of bounds; the v1 compendium is still frozen.

### Step 2: Run the email-author skill (Task #10)

If the email-author skill exists by next session: run it against Task #10's still-missing post-2000 papers. If it doesn't yet exist: skip; proceed with what's already in `papers/`. Targets:

- **Witko 2005** + **Witko 2007** (Penn State, cwitko@psu.edu) — campaign-finance stringency indices
- **Ozymy 2010** + **Ozymy 2013** (verify current affiliation via ORCID) — Newmark-2005-using studies
- **Laboutková & Vymětal 2022/23** (Liberec + Prague Univ. of Economics) — *highest-priority*; 158-indicator framework, largest in FOCAL's reviewed corpus
- **Vaughan & Newmark 2008** (newmarka@appstate.edu) — easy ask; bundle with Newmark on CSG/COGEL questions
- **Roth 2020 thesis** (chari@tcd.ie supervised; thesis at d-nb.info/136695582X/34) — full operationalization of the 23-item Robustness Index
- **Chari, Murphy & Hogan 2007** *Political Quarterly* — the actual Hired-Guns-validation paper. Same TCD contact.

If the email-author skill doesn't exist yet, that's a separate skill-creation task — flag for the user, don't block on it.

### Step 3: Direct-fetch attempts on still-missing post-2000 papers

For each Task #10 candidate, also attempt direct retrieval (the 2026-05-03 download wave already exhausted obvious URL paths, but new approaches may work):
- **Roth 2020 thesis**: WebFetch `https://d-nb.info/136695582X/34` (German DNB)
- **Witko / Ozymy / Laboutková**: try ResearchGate full-text-by-author pages (different endpoint than the 2026-05-03 attempts)
- Any author-page hits the user has discovered since 2026-05-03

### Step 4: Acquire CSG / COGEL / State Capital reference works (Task #11)

Five priority targets, all hard:
1. **CSG, *Campaign Finance, Ethics and Lobby Law: Special Edition* (1988-89)** — the "Blue Book." Defines 21/22 of Opheim 1991's items. Try HathiTrust + Internet Archive + WorldCat + LoC + CSG.org back-issues. ILL fallback.
2. **CSG, *Book of the States* (1988-89)**. Same access paths.
3. **CSG, *Book of the States*, vintages 1990–2002** (covers Newmark 2005's 1990–2003 study window). 7+ volumes.
4. **COGEL Blue Books** — distinct from CSG's Blue Book. Try cogel.org back-issues + ILL.
5. **State Capital Law Firm Group, *Lobbying, PACs, and Campaign Finance: 50 State Handbook*** — used by Strickland 2014 post-2004. Likely commercial / paywalled; check library subscriptions.

If any are unretrievable: flag in the cross-rubric analysis doc that Opheim/Newmark/Strickland operational definitions remain inaccessible — this affects how those rubrics' items can be cross-walked into compendium 2.0.

### Step 5: Methodology source documents (Task #11)

Easier targets, mostly direct WebFetch:
- **GDB Research Handbook** at `https://handbook.globaldatabarometer.org/2021/` — has the full lobbying-module sub-questions GDB 2022 only stubbed. Try direct fetch.
- **TI-UK open-data rubric** — the 4-criterion (accessible/accurate/intelligible/meaningful) framework TI 2016 applies. Find the original TI-UK document.
- **Piotrowski & Liao 2012** — six-criterion usability framework McKay & Wozniak applied. Likely an academic paper; check author affiliations.
- **Keeling, Feeney & Hogan 2017** — original UK CPI Hired Guns scoring McKay & Wozniak corrected.
- **CII (Cost-Indicator Index) source methodology** — likely lives in Chari et al. 2010 or 2020 books (book-only); ask Chari directly.

### Step 6: CDoH-corpus expansion (Task #11) — Lacy-Nichols 2023's parallel measurement universe

Seven frameworks, all academic / NGO; mostly retrievable:
- Mialon, Swinburn & Sacks 2015
- Corporate Political Activity Framework (Savell 2014)
- Policy Dystopia Framework (Ulucanlar 2016)
- Corporate Permeation Index (Madureira Lima 2019)
- Corporate Financial Influence Index (Allen 2022)
- CDoH Index (Lee 2022)
- OECD Lobbying in the 21st Century (2021)

Try DOI / repository / author page for each. **These approach lobbying from the corporate-actor side rather than the regulatory-disclosure side** — different lens but overlapping territory; their inclusion in compendium 2.0 is an open question for user resolution after extraction.

### Step 7: Lit-review-surfaced predecessor candidates (Task #11)

Nine candidates surfaced from extraction lit reviews. Many older / paywalled; lower priority than the above categories. Triage and attempt:
- Pross 2007, Chari & Murphy 2006, Malone 2004 (typology references from Mihut 2008)
- Hamm/Weber/Anderson 1994, Brasher/Lowery/Gray 1999 (from Strickland 2014)
- Lowery & Gray 1993 + 1994, Gray & Lowery 1996 (older vintages)
- LaPira 2016 (different vintage from 2014 + 2020)
- Rosenthal 2001 (cited but not used)

### Step 8: Extract newly-acquired rubric papers

For each newly-acquired *measurement-framework* paper (skip empirical applications, surveys, scoping reviews unless they construct their own framework — same heuristic as 2026-05-03):

1. Run pdftotext into `papers/text/<stem>.txt`.
2. Dispatch a per-paper extraction agent with the same prompt template the 2026-05-03 session used (TSV columns: `paper_id`, `indicator_id`, `indicator_text`, `section_or_category`, `indicator_type`, `scoring_rule`, `source_quote` with line ref, `notes`; MD with 7 sections).
3. Surface results to user.

**Capacity guidance:** keep batch sizes ≤6 in parallel based on the 2026-05-03 session's experience. The first session never hit a rate-limit kill but the prior `scoring`-branch incident with 21-concurrent killed 20 of 21.

### Step 9: Cross-rubric descriptive statistics

Once the corpus is as complete as it's going to get for this session:

1. **Build a unified item table.** Concatenate all `items_*.tsv` files for *measurement-framework* papers (skip empirical applications). Should yield somewhere on the order of 300–600 rows depending on how many new rubrics land.
2. **Cluster items by semantic similarity.** Two methods to compare:
   - **Manual / spreadsheet clustering** — hand-group items by topic (registration / disclosure threshold / expenditure itemization / revolving door / gifts / electronic filing / public access / enforcement / etc.). Tedious but high quality. The user explicitly cares about *what items to include*; manual clustering keeps human judgment in the loop.
   - **LLM-assisted clustering** — dispatch an agent over the unified TSV to propose topic clusters; surface for user review. Faster but inherits the LLM's cluster-boundary biases.
3. **Compute frequency stats.** For each cluster: how many rubrics include at least one item? Median items-per-rubric in the cluster? Variance? This produces the "X rubrics have items in cluster Y" matrix.
4. **Visualize.** A heatmap or grouped bar chart of items-per-rubric by cluster makes the structure visible. The user has not requested figures specifically; do this only if the cluster count is in the dozens (small enough to see).
5. **Save to** `docs/active/compendium-source-extracts/results/20260504_cross_rubric_descriptive.md` with:
   - Total unique items pre-clustering
   - Cluster count + items-per-cluster distribution
   - Items-by-rubric-count histogram (1-rubric / 2-rubric / 3+-rubric breakdown)
   - Items appearing in ≥6 rubrics (the high-consensus core)
   - Items appearing in only 1 rubric (the long tail)
   - Per-rubric coverage (how many of the cluster centroids does each rubric hit?)

### Step 10: Brainstorm methods to create a principled subset

Save to `docs/active/compendium-source-extracts/results/20260504_subset_selection_methods.md`. Articulate at least three candidate approaches and their tradeoffs:

**Method A: Frequency threshold (with caveat).** Auto-include items appearing in ≥N rubrics. The user has already flagged that this over-indexes on registration / threshold / frequency / etc. — items every rubric asks because they're easy. This produces a small "core" that may be uninformative. Document the failure mode explicitly; the method is not wrong but should not be applied alone.

**Method B: FOCAL-anchored expansion.** Start from FOCAL 2024's 50 indicators (already a 15-rubric synthesis by overlapping authors) and ask, for each cluster: does FOCAL cover this? If not, expand by pulling the most-cited items from the older rubrics. The risk is that FOCAL's atomization choices become the project's atomization choices — exactly the PRI failure mode at a different center of gravity. Mitigate by running parallel anchoring from another rubric (Newmark 2017? CPI Hired Guns?) and comparing.

**Method C: Discriminative-strength filtering.** For each candidate item, the meta-question: does this item *vary* across states in ways that matter? Items every state addresses identically (e.g., "is there *any* lobbying registration") aren't useful for distinguishing states. Items where states diverge (threshold magnitudes, materiality tests, electronic-filing-with-bulk-export, revolving-door cooling-off length) carry the actual signal. The 2026-05-03 session's audits surfaced several such items (e.g., LaPira & Thomas: LDA self-reporting captures only 29.7% of true rate — disclosure is *systematically wrong* on revolving door). This is the user's earlier framing: "diagnostically-strong items often appear in only 2-3 rubrics." Documenting the method requires (i) a way to test discriminative strength without state-by-state coding (use FOCAL's 19/109 finding, OpenSecrets's 19-state gap, the cross-rubric correlation literature) or (ii) accepting that discriminative-strength scoring is post-hoc and the first compendium-2.0 will need revision after a state-coverage pilot.

**Method D: Hybrid (recommended).** Combine: A as a starting filter (≥3 rubrics); B as a structural anchor (FOCAL clusters); C as a tiebreaker on items A surfaces that would be cut. Make user-judgment-explicit step at each transition.

The brainstorm doc presents the methods + tradeoffs and ends with **questions for the user** rather than a final recommendation. The user picks the method (or a hybrid) at session 3.

### Step 11: Item-family clustering

Per the user's framing: "how to cluster items into families." This may collapse into Step 9's clustering work, or it may be a separate post-method-selection step. Document either way.

If the unified-item count is small enough (say, <300 unique items after dedup), a *flat* item set may be tractable — no clustering required. If it's larger, families are the way to make the set navigable.

Candidate clustering dimensions to consider:
- **Topic** (registration / disclosure / threshold / itemization / gift / revolving / enforcement / accessibility / contact log / electronic filing / etc.) — dominant axis in most rubrics.
- **Filer role** (lobbyist / client / firm / public official / government entity) — orthogonal to topic.
- **Type** (existence-of-rule / threshold-magnitude / itemization-granularity / open-data-quality / cadence) — orthogonal to both.
- **Statutory locus** (definition / registration / reporting-content / reporting-cadence / oversight / sanctions) — closer to FOCAL's organization.

The brainstorm doc should propose a clustering scheme + flag where existing rubrics' clusterings disagree (likely many places — Newmark uses 3 categories, CPI uses 8, FOCAL uses 8 with completely different labels, AccessInfo uses 7, SOMO uses 12; none of them are wrong, they're just orthogonal cuts).

### Step 12: User review + close-out

Surface the descriptive doc + brainstorm doc to the user. Wait for sign-off. End-of-session: write convo summary, update RESEARCH_LOG + STATUS row + Recent Sessions, commit, push.

---

## Edge cases and risks

- **Email-author skill doesn't exist.** Skip Step 2; the email-author flow becomes its own session. Direct-fetch attempts (Step 3) still proceed.
- **CSG/COGEL volumes are physically inaccessible** without ILL or library visit. Document the inaccessibility in the cross-rubric analysis; flag that Opheim/Newmark/Strickland items have unreachable operational definitions for now. This affects compendium-2.0 design but doesn't block this plan.
- **CDoH-corpus papers have substantively different framing.** They measure corporate-actor behavior, not regulatory-disclosure design. Inclusion in compendium 2.0 is an open question — the brainstorm doc should articulate the framing-mismatch question, not just assume CDoH items go in the same pool as the disclosure-rubric items.
- **Item counts may be too small to need clustering.** If the unified item count after dedup is <100, Method D + a flat list may be sufficient. Document and proceed.
- **Item counts may be too large to handle in one session.** If the unified count is >1000, the session may need to scope down to "rubric-only items" (skip CDoH expansion until next session). Flag and ask.
- **PRI items might appear in newly-acquired papers' citation lists.** Same rule as 2026-05-03: PRI may appear *as a name* in predecessor lists; nothing more. Do not extract from PRI; do not compare against PRI; do not let any item enter the unified table with `paper_id = pri_*`.
- **A rubric extracted before may need re-extraction** if a newly-acquired methodology source changes our understanding (e.g., if Roth 2020's full thesis lands and reveals 23 items operationalized differently than the Google-Sites summary suggested). Re-extract per the 2026-05-03 prompt template; flag in the convo summary.

---

## Open questions (for user resolution at plan review)

1. **Email-author skill state.** Has the user built it yet? If not, this plan skips Step 2 and direct-fetch only.
2. **CDoH-corpus inclusion.** Approach the 7 CDoH frameworks as: (a) include in extraction wave, treat their items same as disclosure-rubric items; (b) extract but flag separately as "different lens, possible secondary tier"; (c) acquire but defer extraction to a later session. Recommendation: (b).
3. **Federal-only papers** (LaPira 2020 LDA at 25; GAO 2025). Currently deferred. Reconsider for this session? Recommendation: continue deferring — they don't construct rubrics, they critique the federal LDA. Federal extraction is a separate downstream concern.
4. **Item-clustering method.** Manual-only / LLM-assisted-only / both compared? Recommendation: both, with manual as anchor and LLM-assisted as second opinion.
5. **Subset-selection method choice.** This plan presents A/B/C/D but doesn't pick. Will the user decide at the start of the session, after seeing the descriptive stats, or at session-3 after seeing the brainstorm doc? Recommendation: defer to session-3.
6. **Schema v2.0 design.** Out of scope for this plan, but should it be a separate plan written in parallel, or a follow-up that waits for compendium 2.0? Recommendation: follow-up. Schema v2.0 Literal types should be derived from compendium 2.0's atomization, not designed in advance.

---

## Carry-forward acquisitions (after this session)

- If anything from Task #10 / Task #11 is still pending after Step 8 (likely most CSG/COGEL volumes + some emails + some CDoH papers), keep them in the open tasks. Compendium 2.0 design (the next plan) should be written assuming the corpus available at that time, with a clearly-flagged "if X arrives later, revise Y" appendix.

---

## What could change

- **The email-author wave returns more papers than expected**, materially expanding the rubric corpus. Sequencing absorbs by extending Step 8's extraction wave.
- **CSG/COGEL volumes are retrieved.** This unlocks operational definitions for Opheim 1991 / Newmark 2005 / Newmark 2017 / Strickland 2014 — those rubrics' items become *much more useful* because their thresholds and category definitions become readable. Re-examine those four extractions' MDs and possibly re-extract.
- **The CDoH frameworks turn out to be on a fundamentally different axis** (corporate-actor measurement, not regulatory-disclosure measurement). Then they may belong in a *parallel* compendium rather than the main one. Brainstorm doc should articulate this possibility.
- **One of the methodology source documents** (TI-UK rubric / Piotrowski & Liao / Keeling et al.) turns out to be the actually-influential source for a rubric we already have. That rubric's items would need re-tagging.
- **The descriptive stats reveal an obvious "elbow"** in the items-by-rubric-count distribution — the natural cut point for the core item set. If the elbow is at ≥4 rubrics, Method A becomes more defensible than the user's prior framing suggested.

---

## Follow-up plans (informational, not gating)

- **Compendium 2.0 design** — written after this plan's deliverables (descriptive stats + brainstorm) ship. User picks the selection method; that plan operationalizes it.
- **Schema v2.0** — written after compendium 2.0. Rebuilds the SMR Literal types (registration roles, reporting frequency, framework IDs, de_minimis fields) on top of compendium 2.0's atomization.
- **State-coverage pilot** — written after schema v2.0. First N states (probably the 5–8 the project initially scopes to) get full compendium-2.0 coding.
- **CDoH compendium** (separate, optional) — if the brainstorm doc concludes the CDoH frameworks belong in a parallel compendium rather than the main one.

---

**Testing Details:** N/A — pure analysis + acquisition task. Per-paper extraction validation criteria same as the 2026-05-03 plan (TSV header has 8 columns, every row has a `source_quote` with line ref, MD has 7 sections). Cross-rubric descriptive doc validation: arithmetic must add up across the items-by-rubric-count histogram; cluster counts must reconcile with the unified-item count.

**Implementation Details:** No code changes. Artifact additions: this plan + (next session's) convo summary + new papers + new TSV/MD extracts + cross-rubric descriptive doc + brainstorm doc + RESEARCH_LOG entry + STATUS row update + final commit + push.

**What could change:** Documented under "What could change" above. Headline: email-author results, CSG/COGEL access, CDoH framing decision.

**Questions:** Six open at plan review (above). User to resolve before Step 2 begins.

---

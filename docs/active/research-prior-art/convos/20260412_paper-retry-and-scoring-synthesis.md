# 20260412 — paper-fetch retry and scoring-rubric synthesis

**Date:** 2026-04-12
**Branch:** `research-prior-art`
**Participants:** Dan Parshall + Claude

## Summary

Follow-up session to the 2026-04-10 scoping kickoff. Four distinct things happened, in roughly this order: (1) retried the paper fetches that had been blocked by the egress proxy last session, (2) merged `origin/main` into `research-prior-art` after another agent added seven papers to main, (3) read the two highest-leverage newly-available papers (Libgober-Jerzak 2024 and Lacy-Nichols et al. 2024 FOCAL) and wrote detailed notes on each, and (4) consolidated the state-lobbying-disclosure scoring-rubric landscape into a single reference document for the upcoming planning-agent session, after Dan flagged that there appear to be three (actually four) competing rubrics and asked for clarification on how they relate.

The session's central finding is that there are two usable rubrics (PRI 2010 for accessibility, FOCAL 2024 for content quality) that compose cleanly into a defensible composite scoring layer, one rubric (F Minus 2024) whose methodology is not yet trusted, and one non-rubric enforcement data source (GAO-25-107523) that belongs in its own dimension. The single highest-leverage next task is re-running PRI's 22-item accessibility rubric against current state portals to produce a 2026 State Lobbying Data Accessibility Index as a standalone deliverable, parallelizable with schema-design work.

A second meaningful finding is that the 8-state priority shortlist written on 2026-04-10 (CA/CO/NY/WA/TX/WI/IL/FL) is partially inconsistent with PRI 2010's rankings — Connecticut, Indiana, Maine, and Montana all appear in PRI's combined top 6 and were not in my shortlist, and Texas is in PRI's top 3 but I placed it Tier 2. This is flagged in the scoring-rubric-landscape results file and should be resolved by the 2026 re-scoring task rather than by revising the shortlist against PRI's stale numbers.

## Topics Explored

- Retry of the five proxy-blocked paper downloads from the previous session. Libgober-Jerzak succeeded via arXiv (which IS on the allowed-domains list — I had not tested this last session, which was a miss). Ornstein still unreachable via joeornstein.github.io or raw.githubusercontent.com.
- Targeted searches for (a) state-level lobbying data papers and (b) heterogeneous government-form document-extraction papers. Results were thin on both fronts — the state-level gap was partially closed by discovering that FOCAL's reference set contains four US-state-specific frameworks (Opheim 1991, Newmark 2005, CPI "Hired Guns" 2007, and especially PRI 2010), and the document-extraction gap remains genuinely unfilled. Splink confirmed as a real Python/DuckDB Fellegi-Sunter tool worth benchmarking.
- Merge of `origin/main` (which another agent had populated with seven papers: Enamorado, GAO-25-107523, Kim 2018, LaPira-Thomas, Lacy-Nichols, Libgober-Jerzak, Ornstein) into `research-prior-art`. Conflicts in PAPER_INDEX.md and PAPER_SUMMARIES.md resolved by unioning both sides and moving my Bacik 2025 / Kim 2025 entries into main's "Lobbying Data Infrastructure" section.
- Detailed reading of Libgober-Jerzak 2024 Tasks 1 and 2 (the two lobbying applications). Documented the F2 ~0.6 best-case performance, the runtime scaling concerns (Bipartite-ML at ~4h for 700×7000 rising to ~255 days for 100k×100k without optimization), the "HSBC Holdings PLC → HSBC" failure case for fuzzy matching, and the Task 2 evidence that fuzzy matching underestimates the log(assets)→log(lobbying) coefficient by roughly half.
- Detailed reading of the Lacy-Nichols FOCAL framework table, identifying the four US-state-specific frameworks inside FOCAL's reference set and noting that PRI 2010's accessibility rubric is the closest direct methodological predecessor to our compliance layer that exists anywhere in the literature.
- Four-rubric comparison (PRI, FOCAL, F Minus, GAO), including a cross-dimensional table and a recommendation for how they should (and should not) compose.
- **Out-of-session paper pull:** Dan confirmed that another agent with better network access is handling the remaining paper retrievals. The PRI 2010 summary was pasted into the conversation (not ingested as a file on this branch), with full scoring details for the 37 disclosure-law and 22 accessibility criteria, 2010 per-state rankings, and a California case study on taxpayer-funded lobbying.

## Provisional Findings

1. **PRI 2010's 22-item accessibility rubric is the best methodological predecessor we have for the project's compliance layer.** It is 16 years stale and needs re-running against current state portals, but the rubric structure itself is directly applicable.
2. **PRI and FOCAL compose cleanly as accessibility + content-quality halves of a composite scoring rubric** with peer-reviewed pedigree on both halves. The overlap at the edges (FOCAL's "openness" category has some accessibility elements; PRI's disclosure-law section has some content elements) is tractable because both rubrics enumerate their criteria explicitly.
3. **Libgober-Jerzak's Bipartite-ML is the best performer on the most relevant entity-resolution benchmark we have**, but runtime scaling is a real concern at project scale. Benchmark before committing, rather than adopting on reputation alone.
4. **Fuzzy string matching alone materially biases substantive lobbying findings**, not just methods-paper abstractions (Libgober-Jerzak Task 2: ~50% attenuation bias on log(assets)→log(lobbying) coefficient). This is concrete justification for investing in real entity resolution rather than shipping a v1 pipeline with fuzzy matching as a stopgap.
5. **F Minus 2024 is not yet trusted as scoring ground truth.** Its methodology is not clearly replicable from the public report, and its headline bimodal distribution is suspicious compared to other rankings. Use only as a hypothesis generator until verified.
6. **The document-extraction / heterogeneous government forms literature gap remains genuinely unfilled.** No standout paper surfaced in targeted searches this session. The right search terms are probably in the legal-informatics or civic-tech space, not the lobbying literature proper.

## Decisions Made

- **Scoring-rubric composition:** PRI 2010 (accessibility) + FOCAL 2024 (content) + GAO-style enforcement as a separate axis. Do not fold enforcement into the disclosure/accessibility score. Do not include F Minus 2024 until its methodology is verified.
- **Highest-leverage next task:** re-run PRI 2010's 22-item accessibility rubric against current (2026) state portals, producing a standalone *State Lobbying Data Accessibility Index, 2026* deliverable independent of any pipeline code. Parallelizable with schema-design work.
- **8-state priority shortlist stays unchanged for now.** Revising it against PRI 2010's stale numbers would trade one stale rubric for another. The shortlist should be revisited after the 2026 re-scoring task produces current evidence.
- **Ornstein fuzzylink deferred indefinitely as a proper paper ingestion.** The other agent may fetch it; if not, Splink is the Python-native alternative and Libgober-Jerzak's benchmark already answers the ER-methodology question Ornstein would inform.
- **Merge strategy: merge main into research-prior-art directly** rather than keeping them separate. The papers are additive and having them on the working branch enables immediate reading. Dan explicitly pushed back on me over-engineering this decision.

## Results Files

New this session:
- `docs/active/research-prior-art/results/scoring-rubric-landscape.md` — the single-document summary of the four rubrics and the composition recommendation, written as a handoff for the planning-agent session.

Updated this session:
- `docs/active/research-prior-art/RESEARCH_LOG.md` — two mid-session entries (paper retry results + reading notes on Libgober-Jerzak and Lacy-Nichols).

Merged in from main (not written by me but worth noting for the planning agent):
- Seven new papers in `papers/` and `papers/text/` (Enamorado, GAO-25-107523, Kim 2018, LaPira-Thomas, Lacy-Nichols, Libgober-Jerzak, Ornstein).
- Updated `PAPER_INDEX.md` and `PAPER_SUMMARIES.md` with main's three-section structure (Entity Resolution & Record Linkage, Lobbying Data Infrastructure, Compliance & Disclosure Quality). My Bacik 2025 and Kim 2025 entries moved into the Lobbying Data Infrastructure section.

## Papers Added / Touched

- **Libgober-Jerzak 2024** — ingested via arXiv (arxiv.org is on the allowed-domains list, which I had not tested last session). Full PDF + text extraction + read summary in RESEARCH_LOG. My original filename `LibgoberJerzak_2024__org_linkage_linkedin.pdf` was renamed during the main-merge to match main's convention `Libgober_2024__org_linking_open_collab.pdf` — git handled this as a rename automatically.
- **PRI 2010** — summary provided by Dan from an out-of-session paper pull. Cited in `scoring-rubric-landscape.md` and in `PAPER_SUMMARIES.md` (via Dan's append in the conversation). The PDF itself is pending ingestion into `papers/` when the other agent's pull completes.
- **All seven papers merged from main** — ingested with index entries and summaries but not read in depth this session except for Libgober-Jerzak (Tasks 1+2) and Lacy-Nichols (framework table and category summary only).

## Follow-ups

### For the planning-agent session (highest priority)

- **Design and scope the 2026 State Lobbying Data Accessibility Index re-scoring task.** Deliverable: per-state scores on PRI 2010's 22 accessibility criteria against current portal infrastructure, published as a standalone document before any pipeline code is written. Estimated scope: 1–2 weeks of per-state portal inspection work. Parallelizable with schema-design.
- **Design the composition of PRI's 22 accessibility criteria with FOCAL's 50 content indicators** into a unified state-level scoring rubric. Requires extracting FOCAL's 50 indicators into a machine-readable form first (a prerequisite sub-task).
- **Revisit the 8-state priority shortlist** after the 2026 re-scoring task produces current evidence. Candidates to consider adding: Connecticut, Indiana, Maine, Montana. Current shortlist members to re-evaluate: possibly Florida or Illinois.

### Paper-ingestion backlog

- **PRI 2010 PDF** — confirm it lands in `papers/PRI_2010__state_lobbying_disclosure.pdf` from the other agent's pull and update PAPER_INDEX / PAPER_SUMMARIES.
- **Ornstein 2025 fuzzylink** — still unreachable from this session's environment. Either fetch via web_fetch as text-only, get from the other agent, or accept that Libgober-Jerzak's benchmark makes Ornstein lower priority.
- **Full careful reads of Enamorado, LaPira-Thomas, Kim 2018, GAO-25-107523** — ingested with summaries but not read in depth this session. Each is a 30–60 minute read. Not urgent; none change pending decisions, but worth doing for cross-checking the summaries main's agent wrote.
- **F Minus 2024 methodology verification pass** — either confirm the rubric is trustworthy (and include it in the composition) or document why it's not (and exclude it explicitly). Either outcome is useful.

### Research-literature gaps still open

- **Document-extraction / heterogeneous government forms papers.** Genuine gap. Right search terms are probably in legal-informatics or civic-tech, not lobbying literature proper. Worth a dedicated search session with different query terms than I've used so far.
- **Libgober 2020's hand-coded regulator-meeting → stock-ticker ground-truth matches.** Not a paper per se, but the replication data for Libgober-Jerzak Task 1 would give us a direct drop-in benchmark dataset for our entity-resolution methodology choice. Arguably more valuable than reading more papers.

## Open Questions

- **Will PRI's 2010 rubric still be meaningful after the 2026 re-scoring, or will some criteria be obsolete?** "Website existence" is now trivially universal, for instance. The re-scoring task is also implicitly a rubric-modernization task, and the output should include notes on which criteria were dropped, added, or modified.
- **What's the right treatment of enforcement signal in the composite score?** The scoring-rubric-landscape file argues for keeping it as a separate axis (following FOCAL's scope choice), but there's a defensible alternative of including it as a weighted input to a unified score. This decision affects both the schema (whether Violation/Referral/Penalty are first-class entities or a derived view) and the downstream usability.
- **How should we handle the F Minus methodology verification?** Minimum-cost path is to email the authors and ask for the indicator list. That's a 5-minute task but requires Dan to do it, not me.

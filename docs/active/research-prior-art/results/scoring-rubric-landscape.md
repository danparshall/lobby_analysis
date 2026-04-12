# Scoring Rubric Landscape

**Provenance:** `docs/active/research-prior-art/convos/20260410_scoping-kickoff.md` plus the mid-session reading entries in `RESEARCH_LOG.md` dated 2026-04-12.
**Last updated:** 2026-04-12
**Branch:** `research-prior-art`
**Purpose:** Single-document summary of the four state-lobbying-disclosure scoring rubrics available to the project, their coverage, their methodological status, and how they should (and should not) be combined. Written as a reference for the planning-agent session that will design the scoring layer.

## The Four Rubrics

### 1. PRI 2010 — Pacific Research Institute, "State-Level Lobbying and Taxpayers"

- **37 disclosure-law criteria + 22 accessibility criteria**, applied to all 50 US states with published per-state scores.
- Split cleanly into *what the law requires* (disclosure laws, 5 sub-components) vs. *whether the data can be extracted from the portal* (accessibility, 8 categories: data availability, website existence, website identification, current data availability, historical data availability, data format, sorting data, simultaneous sorting).
- 2010 combined ranking top 6: Connecticut, Indiana, Texas, Washington, Maine, Montana. Bottom 5: New Hampshire, Wyoming, West Virginia, Nevada, Maryland.
- **Methodologically strong, chronologically stale.** The 16-year gap means any 2010 ranking must be re-verified against current portal infrastructure before being used for project decisions — but the *rubric itself* (the 37+22 criteria) is the most directly applicable methodological predecessor for our compliance layer that exists.
- Free-market think tank framing (opposition to taxpayer-funded lobbying) does not undermine the scoring rubric, which is the document's primary research contribution.
- Full summary in `PAPER_SUMMARIES.md` under the PRI 2010 heading.

### 2. FOCAL 2024 — Lacy-Nichols et al., "Lobbying in the Sunlight"

- **8 categories × 50 indicators**: scope, timeliness, openness, descriptors, revolving door, relationships, financials, contact log.
- Synthesized from 15 prior frameworks (including Opheim 1991, Newmark 2005, CPI "Hired Guns" 2007, and PRI 2010 itself).
- **Explicitly excludes enforcement, sanctions, ethics, and whistleblower protections** "for feasibility." This is a deliberate scope choice, not an oversight, but it means FOCAL cannot be used as the sole rubric for a project that cares about enforcement gaps.
- Applied primarily at the country level. A 2025 follow-up ("Lobbying in the Shadows," Milbank Quarterly) applied FOCAL to 28 countries but **not to US states individually**.
- Peer-reviewed (*International Journal of Health Policy and Management*), current vintage, reproducible methodology.
- Full summary in `PAPER_SUMMARIES.md`.

### 3. F Minus 2024 — state-lobbying-transparency letter grades

- Assigns letter grades to all 50 states. Headline finding: 27 states failing, Colorado alone receiving an A.
- **Methodology not clearly replicable from the public report.** The indicator list and scoring weights are not enumerated in a way that allows external verification, and the headline bimodal distribution is more extreme than any other state-transparency ranking I've seen.
- **Recommendation: treat as a hypothesis generator only.** Use it to flag states for closer examination, never as a ground truth for scoring. If the underlying methodology turns out to be defensible after a verification pass, this recommendation can be revised.

### 4. GAO-25-107523 (April 2025) — 2024 LDA Compliance Audit

- **Not a state-level rubric.** Measures federal LDA compliance by sampling reports, checking for supporting documentation, and counting referrals to the US Attorney's Office for DC.
- Key findings: 3,566 referrals accumulated 2015–2024, ~63% unresolved as of December 2024; 21% of quarterly LD-2 reports list lobbyists who did not properly disclose covered positions.
- Belongs in a separate dimension from PRI/FOCAL/F Minus: those measure *what the law and portal provide*, while GAO measures *whether the disclosure requirements are actually enforced*.
- Our pipeline's compliance layer should reference GAO's methodology for the enforcement dimension but not conflate enforcement scoring with disclosure/accessibility scoring.

## Cross-Rubric Comparison

| Dimension | PRI 2010 | FOCAL 2024 | F Minus 2024 | GAO 2025 |
|---|---|---|---|---|
| Statutory requirements | Yes (37 items) | Yes (most of 50) | Implicit | No |
| Programmatic data accessibility | Yes (22 items) | Partial (openness cat) | Unclear | No |
| Enforcement / actual compliance | No | Explicitly excluded | Unclear | Yes (federal only) |
| US states specifically | Yes (all 50) | No (country-level) | Yes | No (federal only) |
| Methodology replicable? | Yes (published criteria) | Yes (50 indicators listed) | Not clearly | Yes (sampling protocol) |
| Current (2024+)? | No (16 years old) | Yes | Yes | Yes |

**The practical consequence:** no single rubric answers the question the project actually has, which is *"how well can we build a pipeline against state X's disclosure portal right now?"* PRI has the right dimensions but is stale. FOCAL has the right vintage and more categories but isn't applied to US states. F Minus is applied to states and current but methodologically opaque. GAO measures the thing that matters most for policy accountability but only federally.

## Recommended Composition

### Use PRI and FOCAL as complementary halves of a composite rubric

PRI and FOCAL are not competing — they measure different things, and a synthesis that takes **PRI's 22 accessibility items and FOCAL's 8 content categories** gives us a defensible scoring layer with peer-reviewed pedigree on both halves. Rough division of labor:

- **PRI 22-item accessibility rubric** answers *can I get the data out of the portal?* — bulk downloads, machine-readable formats, historical coverage, sortability, current data availability. This is the most pipeline-relevant dimension because it determines whether a state is programmatically ingestable at all.
- **FOCAL 50-indicator content rubric** answers *what's in the data once I have it?* — scope of disclosure, timeliness of filings, revolving-door provisions, relationships between lobbyists and officials, financial itemization, contact logging. This determines whether the data, once ingested, is rich enough to support the research and journalism use cases.

The two rubrics overlap at the edges (FOCAL's "openness" category has some accessibility elements; PRI's disclosure-law section has some content elements), and the synthesis work is not trivial. But the overlap is tractable because both rubrics enumerate their criteria explicitly, so a reconciliation pass can produce a unified rubric with explicit lineage back to each source criterion.

### Do not fold enforcement into the composite

GAO-style enforcement evidence should live as a separate axis of the compliance layer, not be merged into the disclosure/accessibility score. Conflating *"the portal works and the data is rich"* with *"violations get prosecuted"* is a category error that FOCAL's authors explicitly avoided, and for good reason — a state can have excellent portal infrastructure with zero enforcement (arguably Connecticut), or weak infrastructure with aggressive enforcement (arguably New Jersey via ELEC). The dimensions are independent and should be scored independently.

### Set F Minus aside until its methodology can be verified

F Minus should be used *only* as a hypothesis generator for "states worth looking at harder" until somebody recovers and validates its indicator list and scoring weights. If the methodology turns out to be defensible after a verification pass, it can be promoted; until then, it should not enter the scoring composition.

## The Single Highest-Leverage Validation Task

**Re-run PRI 2010's 22-item accessibility rubric against current state portals.** This is a mechanical per-state exercise — for each of PRI's 22 accessibility criteria, check whether the state's 2026 portal satisfies it — and it produces a direct project output: an updated *State Lobbying Data Accessibility Index, 2026* that could be published as a standalone deliverable before any pipeline code is written.

Why this is the highest-leverage next move:

1. **It answers the shortlist question directly with real evidence** instead of tier-based guesses from the earlier `state-infrastructure-tiers.md` pass. Several of PRI's 2010 rankings contradict the tier assignments I wrote earlier in this branch (see the reconciliation note in `state-infrastructure-tiers.md` once that update lands), and a current-vintage re-scoring resolves the contradictions empirically.
2. **It creates a publishable deliverable independent of the pipeline.** An updated PRI-style index is useful to journalists, researchers, and policymakers even if no pipeline code is ever written. That de-risks the project's external value.
3. **It stress-tests the rubric itself.** Running the 22 criteria against 50 portals in 2026 will reveal which criteria are still meaningful, which are obsolete (e.g., "website existence" is now trivially universal), and which need modernization (e.g., adding API-access criteria that didn't exist in 2010). The modernized rubric is a better composition input than the raw 2010 one.
4. **It's parallelizable to the schema-design work.** The schema design is not blocked on accessibility scoring; both workstreams can proceed simultaneously.

The planning agent should probably scope this as a 1–2 week task with a clear deliverable (the 2026 index plus a short methodology note documenting the rubric modernization), separate from any pipeline implementation work.

## Handoff Notes for the Planning Agent

1. Read this file, `state-infrastructure-tiers.md`, and the PRI 2010 entry in `PAPER_SUMMARIES.md`.
2. The 8-state priority shortlist in `state-infrastructure-tiers.md` (CA/CO/NY/WA/TX/WI/IL/FL) was written before the PRI summary landed and is partially inconsistent with PRI's 2010 rankings. Connecticut, Indiana, Maine, and Montana all appear in PRI's combined top 6 and are not in the shortlist; Texas is in PRI's top 3 but was placed in Tier 2 in the earlier pass. **The shortlist should be revisited after the 2026 re-scoring task produces current evidence, not before** — revising it based on 2010 scores alone would trade one stale rubric for another.
3. FOCAL's 50 indicators are not yet in a machine-readable form in the repo. Extracting them into a table (or referencing a published table if one exists in the FOCAL paper's supplementary materials) is a prerequisite for the composition work.
4. The PRI PDF is ingested (`papers/PRI_2010__state_lobbying_disclosure.pdf`) and text-extracted. The full per-state score tables should be transcribed into a CSV or similar machine-readable format before the re-scoring task begins, so the 2026 numbers can be compared directly against the 2010 baseline.

# STATUS — lobby_analysis

Last updated: 2026-04-13

## Current Focus

Transitioning from scoping to implementation. The `research-prior-art` branch has produced the scoring-rubric landscape, schema-design questions, state-infrastructure tiers, and two implementation plans (PRI 2026 accessibility re-score; FOCAL indicator extraction). Merging to main and archiving. Next branches: `pri-2026-rescore` (starting now) and `focal-extraction` (to follow).

## Active Research Lines

| Branch | Started | Focus | Status |
|--------|---------|-------|--------|
| pri-2026-rescore | 2026-04-12 | Re-score all 50 state lobbying portals against PRI's 22 accessibility + 37 disclosure-law criteria (2026 vintage) using a Sonnet-subagent scoring pipeline | Phases 1–3 complete: 2010 rubrics and scores transcribed and reconciled, 2026 rubrics drafted and user-approved (accessibility: 22 retained + 37 new; disclosure-law: 61 retained + reverse-scoring documented). Next: Phase 4 scoring pipeline build. |

## Archived Research Lines

Lines moved to `docs/historical/` — not currently active, but available for reference.

| Branch | Summary | Archived | Material |
|--------|---------|----------|----------|
| research-prior-art | Scoping phase 1 — prior-art survey, state infrastructure tiers, OCD schema analysis, scoring-rubric landscape (PRI + FOCAL + F Minus + GAO), PRI and FOCAL implementation plans. Decision: depend on Open States (don't fork); adopt Popolo via OCDEP 5; score all 50 states on both PRI rubrics in a follow-up branch. | 2026-04-12 | `docs/historical/research-prior-art/` |

## Recent Sessions

(One-line session summaries, newest first)

- **2026-04-13 (pm)** — [pri-2026-rescore] Phase 3: drafted 2026 accessibility rubric (59 items = 22 retained + 37 new) and 2026 disclosure-law rubric (61 items retained, B1/B2 reverse-scoring made explicit). Added Q9 downloadable-sort-results (15 sub-items), Q10 bulk download, Q11 open API, Q12 no-auth-barrier (reverse), Q13 data dictionary (15 sub-items over PRI E-union), Q14 persistent URLs, Q15 raw filings, Q16a/b timestamp-and-freshness. User approved; Phase 3 gate passed.
- **2026-04-13** — [pri-2026-rescore] Phase 1+2: transcribed PRI 2010 accessibility rubric (22 atomic items) and disclosure-law rubric (61 atomic items) to CSVs with deferred scoring; transcribed 2010 per-state scores (50 states × sub-component breakdown) for both rubrics; programmatic reconciliation of sub-component sums vs published totals passes on all 50 states both rubrics. Flagged: PRI's E-component lacks item-level scoring detail in the paper — Phase 3 will re-specify E aggregation.
- **2026-04-12 (pm)** — [research-prior-art] Planning-agent session: reviewed prior session's blindspots, authored PRI 2026 re-score plan (7 phases, all 50 states, both accessibility + disclosure-law rubrics, Sonnet-subagent scoring) and FOCAL extraction plan (3 phases, scoring deferred). Reframed PRI quality gate after user pushback — rubric is source of truth, not human scorer. Merged branch to main; cut `pri-2026-rescore`.
- **2026-04-12** — [research-prior-art] Paper-fetch retry (Libgober-Jerzak ingested via arXiv; Ornstein still unreachable), merged main into branch (brought in 7 papers from other agent's pull), read Libgober-Jerzak Tasks 1+2 and Lacy-Nichols FOCAL framework table, consolidated four-rubric landscape (PRI 2010 + FOCAL 2024 + F Minus + GAO-25-107523) into scoring-rubric-landscape.md as planning-agent handoff. Key finding: PRI + FOCAL compose cleanly, F Minus not yet trusted, highest-leverage next task is 2026 re-scoring of PRI's 22 accessibility criteria.
- **2026-04-10** — [research-prior-art] Scoping kickoff: verified the prior-art gap, profiled state infrastructure tiers (8-state shortlist: CA/CO/NY/WA/TX/WI/IL/FL), analyzed OCDEP 5/6 + withdrawn Disclosures + draft Campaign Finance Filings proposals, decided to depend on Open States, drafted schema-design questions, ingested Bacik 2025 + Kim 2025 as the first two papers, deferred 5 more papers to follow-up. Added `COLLABORATOR_PROJECT_INSTRUCTIONS.md` for fellow onboarding.
- **2026-04-09** — Repo initialized with research-first scaffolding (CLAUDE.md, STATUS.md, PAPER_INDEX.md, PAPER_SUMMARIES.md, papers/, docs/active/, docs/historical/).

# STATUS — lobby_analysis

Last updated: 2026-04-12

## Current Focus

Transitioning from scoping to implementation. The `research-prior-art` branch has produced the scoring-rubric landscape, schema-design questions, state-infrastructure tiers, and two implementation plans (PRI 2026 accessibility re-score; FOCAL indicator extraction). Merging to main and archiving. Next branches: `pri-2026-rescore` (starting now) and `focal-extraction` (to follow).

## Active Research Lines

| Branch | Started | Focus | Status |
|--------|---------|-------|--------|
| pri-2026-rescore | 2026-04-12 | Re-score all 50 state lobbying portals against PRI's 22 accessibility + 37 disclosure-law criteria (2026 vintage) using a Sonnet-subagent scoring pipeline | Kicking off — plan at `docs/historical/research-prior-art/plans/20260412_pri_2026_accessibility_rescore.md` |

## Archived Research Lines

Lines moved to `docs/historical/` — not currently active, but available for reference.

| Branch | Summary | Archived | Material |
|--------|---------|----------|----------|
| research-prior-art | Scoping phase 1 — prior-art survey, state infrastructure tiers, OCD schema analysis, scoring-rubric landscape (PRI + FOCAL + F Minus + GAO), PRI and FOCAL implementation plans. Decision: depend on Open States (don't fork); adopt Popolo via OCDEP 5; score all 50 states on both PRI rubrics in a follow-up branch. | 2026-04-12 | `docs/historical/research-prior-art/` |

## Recent Sessions

(One-line session summaries, newest first)

- **2026-04-12 (pm)** — [research-prior-art] Planning-agent session: reviewed prior session's blindspots, authored PRI 2026 re-score plan (7 phases, all 50 states, both accessibility + disclosure-law rubrics, Sonnet-subagent scoring) and FOCAL extraction plan (3 phases, scoring deferred). Reframed PRI quality gate after user pushback — rubric is source of truth, not human scorer. Merged branch to main; cut `pri-2026-rescore`.
- **2026-04-12** — [research-prior-art] Paper-fetch retry (Libgober-Jerzak ingested via arXiv; Ornstein still unreachable), merged main into branch (brought in 7 papers from other agent's pull), read Libgober-Jerzak Tasks 1+2 and Lacy-Nichols FOCAL framework table, consolidated four-rubric landscape (PRI 2010 + FOCAL 2024 + F Minus + GAO-25-107523) into scoring-rubric-landscape.md as planning-agent handoff. Key finding: PRI + FOCAL compose cleanly, F Minus not yet trusted, highest-leverage next task is 2026 re-scoring of PRI's 22 accessibility criteria.
- **2026-04-10** — [research-prior-art] Scoping kickoff: verified the prior-art gap, profiled state infrastructure tiers (8-state shortlist: CA/CO/NY/WA/TX/WI/IL/FL), analyzed OCDEP 5/6 + withdrawn Disclosures + draft Campaign Finance Filings proposals, decided to depend on Open States, drafted schema-design questions, ingested Bacik 2025 + Kim 2025 as the first two papers, deferred 5 more papers to follow-up. Added `COLLABORATOR_PROJECT_INSTRUCTIONS.md` for fellow onboarding.
- **2026-04-09** — Repo initialized with research-first scaffolding (CLAUDE.md, STATUS.md, PAPER_INDEX.md, PAPER_SUMMARIES.md, papers/, docs/active/, docs/historical/).

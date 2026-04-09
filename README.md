# lobby_analysis

**US State Lobbying Data LLM Pipeline** — open-source infrastructure to make state-level lobbying disclosure data usable as a real-time input for democracy measurement.

Group project of the **Corda Democracy Fellowship**. Project lead: Suhan Kacholia (Co-Founder, Analogy Group). Multiple fellows contribute to this repo.

## Why this exists

Policy capture — when private interests systematically shape government decisions at the expense of the public — is one of the clearest indicators of democratic backsliding. At the US state level, lobbying disclosure data is the most direct signal of who is trying to influence policy and how much they're spending to do it.

This data is hard to use for real-time monitoring. State portals bury it in inconsistent formats, PDFs, and clunky search interfaces. The best existing aggregator (OpenSecrets / FollowTheMoney) provides only flat summary data — without the enrichment that makes it actionable: which specific bills were lobbied on, what positions were taken, which officials received gifts, and how the same entities are operating across states and at the federal level.

## Scope

This project will build open-source infrastructure that makes state lobbying data usable as a real-time input for democracy measurement. We will focus on **5–8 priority states** selected for data quality and political significance.

## Repo layout

This repo follows the research-first documentation workflow. See `CLAUDE.md` for the full description.

- `STATUS.md` — current focus, branch inventory, recent sessions
- `PAPER_INDEX.md` / `PAPER_SUMMARIES.md` — literature index and key findings
- `papers/` — source PDFs; `papers/text/` — extracted text for search
- `docs/active/<branch>/` — active research lines (convos, plans, results, RESEARCH_LOG)
- `docs/historical/<branch>/` — archived research lines (see STATUS.md table)

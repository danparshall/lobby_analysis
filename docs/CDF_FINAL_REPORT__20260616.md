# State-Level Lobbying Disclosure Infrastructure

*Final Report — Corda Democracy Fellowship, April–June 2026*

**The goal:** build open-source infrastructure that makes U.S. state lobbying disclosure data usable for democracy measurement — filling a gap left by existing tools, which cover only federal data or surface-level state scorecards.

**The work — three pillars:**

**1. A common reference layer.** A structured catalog of what each state's lobbying-disclosure law actually requires, built from nine published research frameworks treated on equal footing. This is the rubric-neutral foundation: researchers, journalists, and activists can apply their own definitions on top, rather than inheriting any single existing ranking.

**2. Per-state disclosure extraction.** Actual lobbying activity, structured and joined into queryable "influence chains" linking principals → lobbyists → bills → lawmakers. We shipped **three state releases** during the fellowship — Wisconsin, New York, and Ohio — each requiring its own bespoke extraction approach, confirming that scale comes from a shared output format, not a one-size-fits-all pipeline.

**3. A backend prototype.** A working API and web interface serving the released data, demonstrating end-to-end queryability for downstream consumers.

**How it's teed up.** Everything is open-source, reproducible from source data, and archived with full research provenance at [github.com/danparshall/lobby_analysis](https://github.com/danparshall/lobby_analysis). A queue of roughly twenty scoped follow-on tasks documents what would extend the work to additional states, multi-year time coverage, and campaign-finance integration — leaving the project in a position to be resumed by the team, a future fellowship cohort, or any other group building on a rubric-neutral state lobbying data substrate.

---

## Dig deeper

**For the full story:**
- [`PROJECT_REPORT__20260616.md`](../PROJECT_REPORT__20260616.md) — the long-form project report, drawing on the research arc and weekly updates
- [`README.md`](../README.md) — project mission and positioning vs LobbyView / OpenSecrets / Sunlight / FOCAL
- [`docs/RESEARCH_ARC.md`](RESEARCH_ARC.md) — the three-pillar architecture, the Prong 1 extraction internals, and the empirical findings underneath

**For picking the work up (the tee-up):**
- [`STATUS.md`](../STATUS.md) — current branch state and "where everything is"
- [`docs/STATE_COVERAGE.md`](STATE_COVERAGE.md) — per-state coverage matrix (the Prong 2 scoreboard)
- [Open task issues](https://github.com/danparshall/lobby_analysis/issues?q=is%3Aopen+label%3Atask) — the scoped pickup queue (~20 items)
- [`docs/historical/`](historical/) — 22 archived research lines, each with intact convo / plan / results trail
- [`docs/weekly_updates/2026-06-16.md`](weekly_updates/2026-06-16.md) — end-of-fellowship narrative with "What carries forward" + "What didn't ship"

**The three released chains:**
- [`releases/wi/`](../releases/wi/) — Wisconsin (115,229-row chain, IPF-based)
- [`releases/ny/`](../releases/ny/) — New York (83,786-row chain, JOIN-based; $153M conserved exactly)
- [`releases/oh/`](../releases/oh/) — Ohio (1,589-row chain preview; full-corpus extraction scoped at issue #35)

**Weekly progress reports across the fellowship:**
- [`docs/weekly_updates/`](weekly_updates/) — full series, April through June 2026

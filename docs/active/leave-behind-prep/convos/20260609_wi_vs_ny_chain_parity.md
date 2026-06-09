# WI vs NY chain parity

**Date:** 2026-06-09
**Branch:** leave-behind-prep
**Surface:** claude.ai

## Summary

Cross-state state-of-the-world audit comparing the WI and NY chain artifacts as part of pre-wrap leave-behind work. Session opened with Dan asking whether WI had reached parity with NY's chain — referencing the 2026-06-08 `20260608_ny_egress_check_and_chain_completion` session that landed the `parties_lobbied` integration on `ny-disclosure-explore`.

The comparison surfaced three categories of difference: (1) **structural** — NY discloses `parties_lobbied` (who the filer reported lobbying), WI doesn't; (2) **modeling-architecture** — NY is a clean JOIN, WI requires IPF because WI lobbyists report only aggregate hours; (3) what I initially mis-framed as a **fixable $-attribution gap** — proposing a `comp_per_cell` column for the WI chain. Dan's pushback walked the third back: under WI's data shape, any per-cell dollar attribution either collapses to hours × per-principal $/hr (no new signal) or requires external lobbyist-revenue data that doesn't exist in WI's disclosure regime.

Dan then proposed running IPF on dollars in WI (symmetric with the hours IPF that's already there). That doesn't work either — WI lobbyists file Time Reports (no compensation-received field), so we have row marginals (principal aggregate spend) but no column marginals. IPF needs both. Honest verdict: **WI is structurally complete relative to its data; NY ditto; differences are data-shape, not pipeline-completeness.**

Architectural finding that surfaced from the CFIS/FTM/Plural Policy clarification: the **campaign-finance leg can be a 50-state shared-infrastructure layer via FTM** — parallel architectural axis to Plural Policy/OpenStates for bill-sponsorship. Lobbying disclosure stays per-state Anna Karenina, but two of three chain legs are now confirmed-shareable. Outcome: two captured tasks (#42 Plural Policy refactor, #43 FTM new build) to externalize the shared-infrastructure work as successor-Fellow handoff. A third outcome surfaced later in the session: an architectural agreement on **per-state Suhan-droppable release docs** (3-doc pattern — per-state release README + per-state chain README + cross-state STATE_COVERAGE.md as index), captured as an executable plan at [`docs/active/leave-behind-prep/plans/release_doc_pattern.md`](../plans/release_doc_pattern.md) for fresh-agent execution. Plus one more captured task (#44, FTM NY sample query, fires 2026-06-10) externalizing the WI-vs-NY FTM-validation asymmetry.

## Topics Explored

- WI vs NY chain artifact comparison: 115K-row WI vs 83.8K-row NY; column schemas; conservation invariants
- The three categories of difference (structural / modeling-architecture / mis-framed gap)
- NY's data shape: does it have hours? (No — only `total_compensation` in `client_semiannual`; the `lobbyist_bimonthly` sibling adds itemized expenses + individual-lobbyist resolution but is still dollar-grain, no hours field disclosed)
- The hours ∝ spending rule of thumb's untestability across all 10 priority states (NY has $ but no hours; WI has hours but no per-bill $; OH has neither — no compensation disclosure on AER)
- Dan's IPF-on-dollars idea: row marginals yes (principal aggregate spend in `WI_principal_filings.tsv`), column marginals no (WI lobbyist filings are explicitly "Time Reports") → IPF mechanism can't run without a lobbyist-side dollar marginal
- CFIS as the WI-specific name (Wisconsin Ethics Commission's Campaign Finance Information System, now rebranded "Sunshine" / Civera-hosted) vs FTM as 50-state aggregator
- FTM access mechanism: API-only, single PHP-style endpoint at `api.followthemoney.org`, basic-tier quota ~15 queries pending Institute review
- FTM-in-OpenSecrets-integration sunset mode (banner observation, post-dates the wi-cfis-scoping work)
- Architectural axis count: lobbying disclosure (per-state, bespoke), bill sponsorship (shared via Plural Policy/OpenStates), campaign finance (shareable via FTM — not yet built)
- WI vs NY chain README comparison: WI has consumer-front-door polish (TL;DR, audience, 30-sec tour, headline finding); NY has reference-doc rigor (conservation rules, disclosed-vs-inferred semantic warning, measured-impact methodology). Each state's README needs a back-port from the other.
- Suhan-droppable release-doc workflow: per-state release dir must be self-contained for upload to an isolated claude.ai Project (no repo-wide context). Triggers a 3-doc architecture: per-state release README (framework + matrix + gotchas), per-state chain README (schema + conservation rules + sample analyses), cross-state STATE_COVERAGE.md (matrix index, unchanged).
- Recognition that the cross-state "basics" doc Dan described already exists as `docs/STATE_COVERAGE.md` (drafted 2026-06-06) — 4-node × 6-edge × 3-attribute framework, 6-symbol quality conventions, per-state matrices with footnoted gotchas, Anna Karenina principle
- Third attribute axis identified as **Stance** (support/oppose/monitor) — structurally absent in all three priority states' lobbying disclosure

## Provisional Findings

- WI chain is structurally complete given WI's disclosure shape. The `comp_per_cell` column I initially proposed adding would have been hours × per-principal $/hr — no new signal within a principal, only the per-principal $/hr rate across principals (which is already derivable from `WI_principal_filings.tsv` directly).
- The hours-proportional-to-spending assumption is structurally untestable against any of the 10 priority states' disclosed data. No oracle to validate against.
- WI vs NY are at parity *relative to their respective data sources*. Differences are not "gaps" in either direction; they're properties of different states' disclosure regimes.
- FTM API base tier hits a quota after ~15 queries; Institute review on quota-exceed (~2 business days) for expanded access. The wi-cfis-scoping `lobbying@opensecrets.org` outreach (2026-06-03) is the pending item for WI.
- FTM is in sunset/integration mode pending OpenSecrets merger. Banner reads: *"The National Institute on Money in Politics and the Center for Responsive Politics joined forces to become OpenSecrets... isn't maintained as we integrate with OpenSecrets."* Long-term API contract may not survive intact. Worth confirming before #43 implementation starts.
- Cross-state shareable infrastructure axes confirmed: Plural Policy (already in active use on both `wi-allocation-matrix` and `ny-disclosure-explore`), FTM (not yet built, 50-state aggregator). Lobbying disclosure remains per-state Anna Karenina by data-acquisition shape.
- The third attribute axis in the 4×6×3 framework is **Stance** (not Counts/Frequency) — confirmed by re-reading STATE_COVERAGE.md. Mostly absent across states (WI/NY/OH all structurally lack it), which is itself a load-bearing observation: the chain detects activity, not composition.
- The Suhan-droppable use case requires self-contained per-state release dirs. Acceptable approach: duplicate the ~15-line framework into each state's release README rather than have it defer to STATE_COVERAGE.md (which won't be in an isolated Project upload). Cost (N+1 sources of truth) is acceptable at N=3, revisit at N≥10.
- Per-state release-doc architecture decided (3-doc pattern: per-state release README, per-state chain README, cross-state STATE_COVERAGE.md as index). Each per-state release README to be enriched with framework + this-state matrix (adapted from STATE_COVERAGE) + use-instructions; each chain README back-ported with the polish/rigor it lacks; STATE_COVERAGE gets only a See-also touch.

## Decisions Made

- **No WI chain `comp_per_cell` work.** Explicitly rejected as surface-parity dressing that would stack 4 modeling layers (IPF + proportional bill attribution + per-sponsor split + per-principal $/hr rescaling) under a number that reads as disclosed.
- **Two tasks captured to GH issues** — externalized as successor-Fellow handoff work rather than absorbed into Day 4/5 leave-behind scope:
  - [#42: Extract Plural Policy bulk-CSV ingest into shared cross-state library](https://github.com/danparshall/lobby_analysis/issues/42)
  - [#43: Build reusable FollowTheMoney ingest for cross-state campaign-finance leg](https://github.com/danparshall/lobby_analysis/issues/43)
- Both tasks point at `docs/STATE_COVERAGE.md` as the principle reference. Both bodies updated with proper GitHub blob URLs (the initial drafts had path mentions in backticks, not clickable links — caught by Dan).
- **Per-state release-doc architecture decided** — 3-doc pattern, all docs already exist, all to be enriched (not replaced). Execution externalized to fresh agent via plan at `docs/active/leave-behind-prep/plans/release_doc_pattern.md` rather than performed inline this session.
- **Task #44 dated 2026-06-10** to validate FTM 50-state portability against NY data (parallel to the WI LeMahieu sample query). FTM site flagged as down at session time; retry tomorrow.

## Results

- GH issue #42 (Plural Policy refactor): https://github.com/danparshall/lobby_analysis/issues/42
- GH issue #43 (FTM new build): https://github.com/danparshall/lobby_analysis/issues/43
- GH issue #44 (FTM NY sample query, fires 2026-06-10): https://github.com/danparshall/lobby_analysis/issues/44
- Plan: [`docs/active/leave-behind-prep/plans/release_doc_pattern.md`](../plans/release_doc_pattern.md) — 22.3KB, 314 lines, 6-step execution spec for fresh-agent pickup, est. 2:20-3:30 depending on rigor

## Plans Authored

- [`docs/active/leave-behind-prep/plans/release_doc_pattern.md`](../plans/release_doc_pattern.md) — Per-state Suhan-droppable release-doc pattern. 6-step execution plan: extend `releases/wi/README.md` (framework + matrix + use-instructions), extend `releases/wi/chain/README.md` (back-port conservation rules + sample analyses), parallel work for NY on `ny-disclosure-explore`, touch STATE_COVERAGE.md See-also header, RESEARCH_LOG completion entry. For fresh-agent execution; original author won't be in-session.

## Open Questions

- Does FTM data and API surface migrate to `opensecrets.org` URLs/endpoints after the integration completes? (Worth confirming before #43 implementation starts. If yes, the schema specimens in the LeMahieu sample-query writeup may need re-validation.)
- Is the principal-side WI Tier-3 data (per-(lobbyist, principal, semester) detailed time reports — held over from Tier-2 parser work) something that could close the WI hours/dollars gap via finer hour granularity? Not investigated this session; speculation only.
- Does FTM's "Lobbyist Link" feature (`d-llink` flag in the LeMahieu sample query, ~5% coverage there) have any role to play in lobbyist-side personal-contribution disambiguation beyond what the WI campaign-finance plan already sketched?

## Captured Tasks

- [#42: Extract Plural Policy bulk-CSV ingest into shared cross-state library](https://github.com/danparshall/lobby_analysis/issues/42) — captured 2026-06-09
- [#43: Build reusable FollowTheMoney ingest for cross-state campaign-finance leg](https://github.com/danparshall/lobby_analysis/issues/43) — captured 2026-06-09
- [#44: Pull FTM NY sample query to validate 50-state portability](https://github.com/danparshall/lobby_analysis/issues/44) — captured 2026-06-09, dated 2026-06-10

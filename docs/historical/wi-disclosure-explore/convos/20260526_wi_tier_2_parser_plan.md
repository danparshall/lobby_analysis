# wi_tier_2_parser_plan

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore

## Summary

After the principal-side scrape landed earlier today, Dan asked what data beyond the (lobbyist, principal, dates) authorization edges is captured in the already-fetched HTML. Inspection of the four committed fixtures (12997 WCTA, 11348 Lexia, 11530 redacted, and lobbyist 11042) surfaced a substantial **Tier 2** layer of per-(entity, semester) data sitting inside the same HTML that was already fetched: per-principal lobbying-interest prose, total expenditures + total communication/other hours per semester, activity-allocation percentages across six WI-specific buckets (Legislative Bills/Resolutions, Budget Bill Subjects, Administrative Rulemaking, Topics-Not-Yet-Assigned, Minor Efforts, Other Matters), and per-lobbyist time-report summaries.

The current parsers (`authorization_parser.py`, `principal_parser.py`) extract only the authorization edges and discard everything else. The 944 principal HTMLs and 774 lobbyist HTMLs in the gitignored data store already contain Tier 2 data — no new fetches needed.

We walked the v1.1 model layer at `src/lobby_analysis/models/` to see whether Tier 2 data lands cleanly in existing types. It mostly does: `LobbyingFiling` is the right home (`filing_type="expenditure_report"` for per-(principal, semester) SLAE summaries, `filing_type="activity_report"` for per-(lobbyist, semester) time reports). Two genuine gaps surfaced: (a) `LobbyingFiling` has no fields for hours-on-lobbying — Dan's call is to bump to **v1.2** with `total_hours_communicating` + `total_hours_other`; (b) the current scrapers never instantiate `Organization` records for principals, so per-principal static metadata (lobbying interests, CEO, contact info) has no place to land without filling that gap as part of this work.

A schema-clarification reminder Dan surfaced and that the plan needs to carry: `LobbyingFiling` in `src/lobby_analysis/models/filings.py` is the contract for **actual disclosure data** (what filers submit). The `models_v2/` cell layer in `src/lobby_analysis/models_v2/cells.py` is the contract for **statute-metadata** (what the law requires — Prong 1 territory). They're related (a statute saying "filings must include X" implies `LobbyingFiling.X` must be populatable) but they version independently. This plan touches only the disclosure-data layer; the v1.1 → v1.2 bump applies to that side, not to the cell layer.

Two side-finds during inspection: (1) the Schlaak case "WCTA" turned out to be **Wisconsin County Treasurers Association** (a public-officials professional association, with Schlaak serving as Calumet County Treasurer / Legislative Chair) — not Cable Telecommunications as one of the two same-day session writeups stated. That reframes the Schlaak-class Mechanism A from "unknown filter" to "likely a public-sector-self-advocacy filter on the grid AJAX." (2) The hyphen-encoding hypothesis for Neumann-Ortiz is dead: 9 other hyphenated lobbyist surnames in the grid AJAX fetched cleanly, and the URL is keyed by ID anyway.

Also surfaced: no `nc-disclosure-explore` branch actually exists in the repo, despite the WI RESEARCH_LOG's branch-purpose statement claiming WI is "parallel to" it. WI is the first state-extraction line in the actual branch history, which means WI is setting the conventions (ID scheme, parser architecture, materialization shape) for downstream states. The plan picks `WI-principal-{id}` / `WI-lobbyist-{id}` to match the two-letter-uppercase `source_state` field already established in `Person` and `Organization`.

## Topics Explored

- What data the per-principal and per-lobbyist HTML pages expose beyond authorization edges (the three-tier framing: edges / per-period summaries / per-(lobbyist, principal, period) itemizations)
- Whether the Schlaak case "WCTA" is the Cable Telecommunications Assn or the County Treasurers Assn (the two principal-side scrape results docs disagreed; web-search resolution + fixture body)
- Whether Neumann-Ortiz's soft-404 could be a hyphen-encoding issue (refuted)
- The fit of Tier 2 data into the existing v1.1 `LobbyingFiling` schema
- Whether `LobbyingFiling` supports hours-on-lobbying (it does not at v1.1; single compendium row for it exists at `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying`, FOCAL 2024)
- The model-versioning convention (no code-level `__version__`; versioning lives in plan/RESEARCH_LOG docs; the v1.1 TDD pattern at `tests/test_models_v1_1.py` is the template)
- ID-scheme convention for downstream cross-state joins
- Whether tier 3 (per-(lobbyist, principal, semester) detailed time reports + per-principal SLAE itemizations) is in scope (it is not; explicitly held over)

## Provisional Findings

- **The 3 committed principal fixtures are not a representative sample for parser TDD.** 12997 (WCTA) is low-spend-pledge-exempt ($0.00 everywhere); 11530 is privacy-redacted; 11348 (Lexia) has 4 lobbyists and uses only the "Topics Not Yet Assigned" allocation bucket at 100%. None populate the Legislative Bills/Resolutions, Budget Bill Subjects, or Rulemaking sections with non-empty content. Any tier-2 parser needs new fixtures from high-volume principals (Wisconsin Hospital Association, Wisconsin Manufacturers & Commerce, the top-15-lobbyist principals identified by the prior scrape).
- **The 944 principal HTMLs are already on disk.** Implementing agent should grep the data store for principals with populated `<h4>Legislative Bills/Resolutions</h4>` sections and pick 2-3 of the richest as fixtures. Zero new HTTP fetches needed.
- **Tier 2 maps onto `LobbyingFiling` after a v1.2 bump.** Two new optional fields: `total_hours_communicating: float | None`, `total_hours_other: float | None`. Non-breaking additive change. The bump is documentary (in docs/plans), not a code-level version constant.
- **`Organization` records for principals are missing from the current scrape output entirely.** Adding them as part of this work is the cheapest moment.
- **Documentation drift in the principal-side scrape results doc:** principal 12997 is the Wisconsin County Treasurers Association per the fixture HTML, but `results/20260526_wi_principal_side_scrape_results.md:65` calls it "Wisconsin Cable Telecommunications Association." In-scope fix.
- **Tier 3 is a separate plan.** Per-(lobbyist, principal, semester) time reports + per-principal SLAE itemizations would require ~1500-3000 new fetches and we haven't yet inspected even one tier-3 page to know what it contains.

## Decisions Made

- **Scope:** Tier 2 only. Parse what's already on disk. No new fetches.
- **Sequencing:** Principal-side parser first, lobbyist-side mirrors after. Symmetric coverage; staged execution.
- **Schema target:** existing v1.1 `LobbyingFiling` + `Organization` types, bumped to v1.2 with two new optional hours fields on `LobbyingFiling`. Phase 1 of the plan, mandatory.
- **Schema layer scope reminder:** This bump is to `src/lobby_analysis/models/filings.py` (the disclosure-data contract). The `models_v2/` cell layer (statute-metadata contract for Prong 1) is untouched.
- **ID scheme:** `WI-principal-{id}` / `WI-lobbyist-{id}`. Matches the two-letter-uppercase pattern of `source_state` field already established in `Person` and `Organization`.
- **Documentation-drift fix** on principal 12997 in scope as a Phase 7 step.
- **Plan deliverable:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md)

## Results

No analytical results files this session. The plan is the deliverable.

## Open Questions

- **Tier 3.** What does a per-(lobbyist, principal, semester) time-report page actually contain? Single reconnaissance fetch needed before any tier-3 plan is written. Deferred.
- **Cross-state generalizability.** The activity-allocation bucket structure (6 categories) is empirically WI-specific. Other states publish different structures. The parser will need to be WI-flavored; the schema (`LobbyingFiling`) is reusable.
- **Schlaak-class enumeration.** Held over to Dan's `lobbying@wi.gov` email thread; orthogonal to this plan.
- **Whether the `provenance` field on `LobbyingFiling` should be populated** by this parser (recommendation: yes, source_url + retrieved_at, since we have the data — but this is a precedent-setting choice for downstream extraction work).

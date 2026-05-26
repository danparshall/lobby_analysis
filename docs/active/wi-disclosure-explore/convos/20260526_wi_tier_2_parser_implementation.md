# wi_tier_2_parser_implementation

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Originating plan:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md)
**Originating convo:** [`convos/20260526_wi_tier_2_parser_plan.md`](20260526_wi_tier_2_parser_plan.md)

## Summary

Picked up at Phase 0 of [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md) per the prior session's handoff. Shipped Phase 0 (fixture capture for high-volume principals + lobbyist) and Phase 1 (v1.1 → v1.2 disclosure-data schema bump on `LobbyingFiling` for hours fields). Paused before Phase 2 (principal-side parser TDD) after structural reconnaissance revealed the Percent Allocation HTML is **item-itemized** (one row per bill / topic / rule with its own per-period %) rather than bucket-totaled — Phase 2 needs ~60-90 min of careful BeautifulSoup work to walk the bucket cards and sum per-period item %s into the plan's "6-bucket activity allocation per semester" output shape. Dan locked the two plan-footer questions before the pause: `LobbyingFiling.provenance` is YES (populate `source_url` + `extracted_at`); no in-scope add-ins beyond the principal-12997 WCTA name fix.

## Session-start context

Branch state at session start: `aebe8e2` (matches handoff SHA). Pre-flight verified:

- Local `main` is in sync with `origin/main` at `94dc75d`.
- No other branch has touched `src/lobby_analysis/models/filings.py` since the original `lobbying-data-model` branch — the planned v1.2 schema bump (Phase 1) is collision-free vs. the multi-committer constraint.
- 944 principal-checkpoint JSONs + 776 lobbyist-checkpoint JSONs available under `~/data/lobby_analysis/disclosures/WI/` via the worktree's `data/` symlink.
- Schema-layer scope reminder absorbed: this plan touches `src/lobby_analysis/models/` (disclosure-data contract), NOT `src/lobby_analysis/models_v2/` (statute-metadata contract for Prong 1).

Session-start cleanup committed at `3ccc042`: two `cp_perm_diag*.html` stubs from a prior dotfiles cp-permission diagnostic were sitting in `tests/fixtures/wi/`; moved to `notes/cp_perm_diag/` so the fixture dir is clean for the Tier-2 work.

## Topics Explored

- Phase 0 fixture capture — grep checkpoint JSONs to find populated-bucket principals (HTML embedded in `cp["html"]` string per checkpoint)
- Phase 0 structural surprise — `<h4 class="card-title">Legislative Bills/Resolutions</h4>` appears TWICE per principal page (once in the "Lobbying Interests" h3 section, once in the "Percent Allocation of Lobbying Effort" h3 section)
- Phase 0 snapshot-timing finding — only 3 of 770 lobbyists have all 4 Time Report Summary periods populated; 420 match the 2-populated/2-zero norm because P3 (Jan-Jun 2026) is in progress and P4 (Jul-Dec 2026) hasn't started
- Phase 1 TDD on v1.2 schema bump — write 7 RED tests, add 2 fields (`total_hours_communicating` + `total_hours_other` on `LobbyingFiling`), verify GREEN
- Phase 1 noridoc update at `src/lobby_analysis/models/docs.md`
- Phase 2 reconnaissance — Total Lobbying Effort table is a 3-row × N-period table (Expenditures, Hours Communicating, Hours Other); Percent Allocation is a 6-bucket nested-card structure with per-item per-period %s

## Provisional Findings

- **Phase 0 ranking heuristic for principal fixtures:** Sort all 944 checkpoint JSONs by `no_results_count` (count of `<div class="no-results">` divs anywhere on the page) ascending, then by HTML byte size descending. The unique top candidate at `no_results=0` is **Dairy Business Association (11590)** — all 6 Percent Allocation buckets populated, 3 lobbyists, $88,568.50 spend. Second-pick by content-size is **Wisconsin Manufacturers & Commerce (11637)** — 2.1 MB HTML, 10 lobbyists, $911,593.49 spend, but `no_results=4` (only Topics Not Yet Assigned + 1 other bucket populated in the Percent Allocation despite a heavily-populated Lobbying Interests section). Third place by structural variation is **League of Wisconsin Municipalities (11588)** (`no_results=1`, 6 lobbyists, $141K), held back as a candidate not yet committed.

- **Same-h4-text-different-section pattern:** The string `<h4 class="card-title">Legislative Bills/Resolutions</h4>` appears under TWO different `<h3>` parents on a principal page:
  1. `<h3>Lobbying Interests</h3>` — the bill-by-bill list of what the principal is registered to lobby on (no $ or %, just bills + descriptions + topics, with detailed expandable cards)
  2. `<h3>Percent Allocation of Lobbying Effort</h3>` — the per-bill per-period % effort allocation table
  
  My initial coarse heuristic (search for "No legislative bills/resolutions found." anywhere on the page) confused these two sections. Refined heuristic: only count `no-results` divs INSIDE the Percent Allocation `<h3>` section. The parser must distinguish the two sections by their parent `<h3>` ancestor.

- **Top Lobbyist confirmed as Bryan Brooks (11052) at 41 principals.** Matches the prior session's headline. HTML is 63 KB. Time Report Summary at line 423 has 4 columns (Jan-Jun 2025 / Jul-Dec 2025 / Jan-Jun 2026 / Jul-Dec 2026) but only the first 2 are populated: Communication = [102.50, 195.00, 0, 0] and Other = [566.00, 673.90, 0, 0].

- **"All 4 periods populated" structurally unachievable on 2026-05-26 snapshot.** Histogram across all 770 lobbyists with Time Report Summaries: 146 lobbyists have 0 periods populated; 128 have 1; **420 have 2** (this is the norm — P1 + P2 only); 76 have 3; **3 have all 4**. The 3 four-period cases are 11119 William McCoshen (high), 11191 (small numbers, possibly an outlier), and 11637 WMC (also a principal ID). The plan's fixture-selection criterion "all 4 periods showing non-zero hours" was unachievable; Brooks's 2-populated/2-zero pattern is the realistic norm. The plan's test spec (which explicitly covers "zero-hours periods should still emit a filing with zeros") works fine with Brooks's data, so no test-design adjustment is needed — only the fixture-selection rationale shifts.

- **Total Lobbying Effort table is 3 rows × N period columns** (verified on 11590 + 11348):
  - Row 1: `Total Lobbying Expenditures` — `$X` per period
  - Row 2: `Total Hours Communicating` — `X.XX` per period (no `$`)
  - Row 3: `Total Hours Other` — `X.XX` per period
  
  Period columns are 2025 Jan-Jun + 2025 Jul-Dec + Total in both 11590 and 11348 — i.e., **the principal-side Total Lobbying Effort table only shows COMPLETED semesters**, while the Percent Allocation section shows all 4 (with empty cells for in-progress 2026 periods). This means the parser's emitted `LobbyingFiling` records have:
  - One filing per completed semester from Total Lobbying Effort (P1 2025 H1, P2 2025 H2)
  - Plus a `total_expenditure_lifetime_to_date` if the parser tracks the Total column (TBD whether to bother)
  - The 2026 periods don't appear in Total Lobbying Effort, so they don't get LobbyingFiling records at all.

- **Percent Allocation section is bill-itemized, not bucket-totaled.** Verified on 11348 Lexia (Topics Not Yet Assigned card has ONE topic at 100% each completed period) and 11590 Dairy (Legislative Bills/Resolutions card has Assembly Bills 30, 93, 219... each at 1% per period). The 6 bucket h4 cards are headers; under each bucket header is either `<div class="no-results">No X found.</div>` (empty bucket) or a `<div class="component-list">` containing per-item cards each with their own 5-column `<table>` (the per-period %s for that item). To produce "bucket-level % per semester" per the plan, the parser must:
  1. Locate the Percent Allocation `<h3>` section
  2. For each of 6 bucket `<h4 class="card-title">` cards inside that section, walk its descendant per-item cards
  3. For each item, parse the per-period % values (1% / 0.5% / empty / etc.)
  4. Sum the per-period %s across items within each bucket → bucket-level per-period totals

- **CEO Name extraction is simple:** `<strong>CEO Name:</strong><br />\n{name} <br /><br />`. Tim Trotter on 11590 Dairy. May be absent on smaller principals.

- **Contact section structure** at L136+ in 11590: `<strong>Contact</strong>` followed by address / phone / email / website tagged with their own `<strong>` labels.

## Decisions Made

- **Convo name:** `20260526_wi_tier_2_parser_implementation.md` (this file). Parallels the existing `20260526_wi_principal_side_scrape_implementation.md` naming.

- **Diagnostic cleanup:** Moved `cp_perm_diag.html` + `cp_perm_diag_dest2.html` (56-byte dotfiles cp-permission stubs) from `tests/fixtures/wi/` to `notes/cp_perm_diag/`. Committed at `3ccc042` per "prefer mv over rm" default.

- **Phase 0 principal fixture picks:** 11590 (Dairy Business Association, 698 KB, fully populated allocation buckets) + 11637 (Wisconsin Manufacturers & Commerce, 2.1 MB, sparse-allocation variant with heavy Lobbying Interests). Third-place 11588 League of WI Municipalities held back to keep fixture footprint at 2.8 MB total.

- **Phase 0 lobbyist fixture pick:** 11052 Bryan Brooks (top lobbyist at 41 principals, 63 KB, 2-populated/2-zero Time Report Summary pattern — the realistic norm on this snapshot).

- **Plan Q1 (provenance population) → YES:** Phase 2/3 parsers emit `LobbyingFiling.provenance` with `source_url` (reconstructable from `principal_id`/`lobbyist_id` + the `2025REG` session) and `extracted_at` (use the checkpoint JSON's fetch timestamp if available, else parse time). Sets a precedent for downstream extraction work.

- **Plan Q2 (cheap add-ins) → NO additions:** Only the principal-12997 WCTA name fix in Phase 7. State Agency Liaisons table parser and cross-session principal_id stability remain held over.

## Results

### Commits this session

All pushed to `origin/wi-disclosure-explore`:

- `3ccc042` chore: move cp_perm_diag stubs out of tests/fixtures/wi/
- `01388e6` wi: tier-2 parser fixtures (populated principals + lobbyist)
- `0debed0` models v1.2: tier-2 hours field tests (red)
- `f50c7e7` models v1.2: add hours fields to LobbyingFiling (green)
- `698897b` models v1.2: noridoc update

### Test deltas

- New: `tests/test_models_v1_2.py` — 7 tests, all GREEN after Phase 1
- Combined `test_models.py` + `test_models_v1_1.py` + `test_models_v1_2.py`: 126 pass
- Combined `tests/test_wi_*.py`: 49 pass
- Full suite: 1462 pass, same 3 pre-existing `test_pipeline.py` baseline failures (`test_ca_snapshot_loads_and_flags_incapsula_stubs`, `test_brief_contains_all_rubric_items_and_instructs_subagent`, `test_stamp_rows_adds_provenance` — owned by archived `pri-2026-rescore`; root cause is hardcoded `data/portal_snapshots/CA/2026-04-13/manifest.json` path while on-disk data is now under `2026-05-01/`; orthogonal to Tier-2)

### Fixtures captured

In `tests/fixtures/wi/`:

- `principal_11590_populated.html` (Dairy Business Association, 698,805 bytes) — `no_results=0`, 3 lobbyists, $37,840.00 / $50,728.50 / $88,568.50 spend; Total Hours Communicating = 158.50 / 100.50 / 259.00; Total Hours Other = 307.00 / 254.00 / 561.00. CEO Tim Trotter. Fully populated all 6 allocation buckets.

- `principal_11637_populated.html` (Wisconsin Manufacturers & Commerce, 2,101,475 bytes) — 10 lobbyists, $496,501.03 / $415,092.46 / $911,593.49 spend; Total Hours Communicating = 543.50 / 547.50 / 1091.00; Total Hours Other = 1971.45 / 1777.75 / 3749.20. Heavy Lobbying Interests (~2 MB of bill-by-bill detail) but Percent Allocation Legislative Bills card reads "No legislative bills/resolutions found." (effort allocated elsewhere — Budget Bills + Topics Not Yet Assigned). Tests the "populated Lobbying Interests, sparse Percent Allocation" variant.

- `lobbyist_11052_populated.html` (Bryan Brooks, 64,732 bytes) — 41 principals; Communication hours = [102.50, 195.00, 0, 0]; Other hours = [566.00, 673.90, 0, 0].

## Open Questions

Plan-footer questions resolved this session (kept here as a record):

- **Q1 — `LobbyingFiling.provenance` population.** → YES, populate `source_url` + `extracted_at`.
- **Q2 — Other cheap add-ins beyond the doc-drift fix?** → NO additions.

New open question raised this session for the next agent:

- **Q3 — Percent Allocation bucket-totaling strategy.** The plan's expected output is "activity-allocation percentages across the 6 buckets per semester," but the HTML provides per-item per-period %s, not bucket totals. Two strategies for Phase 2:
  - **(a) Sum at parse time** — for each bucket card, sum the per-period %s across the items inside. Output is the plan-expected "bucket × period" matrix. Loses per-item detail (which would be tier-3 anyway).
  - **(b) Emit per-item rows, defer aggregation** — parser returns one row per (bucket, item, period) triple. Materializer (Phase 4) aggregates to bucket level. Cleaner separation but expands the parser's return type significantly.
  
  Recommendation: **(a)** — keeps the parser's `LobbyingFiling` contract tight (bucket totals only; tier-3 detail explicitly out of scope per the plan). Items-as-row would push into tier-3 territory.

## Next Steps

Hand off to the next session for Phase 2 (principal-side parser TDD) and onward. Key context the next agent needs:

- Fixtures are in place: 11590 + 11637 (populated) + existing 11348 / 11530 / 12997 / 10949 / 10973 / 11017 (various edge cases) + 11042 / 11052 (lobbyist side).
- v1.2 schema is GREEN — `LobbyingFiling.total_hours_communicating` + `total_hours_other` accept floats including 0.0.
- Provenance shape: `source_url` (e.g., `https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/{id}`) + `extracted_at` (use checkpoint fetch timestamp).
- Q3 above needs resolution before writing Percent Allocation tests; recommend strategy (a).
- The Total Lobbying Effort table is the easier parse — 3 rows × N period columns, regex on the dollar / hour values. Start here.
- The Percent Allocation section is the harder parse — nested bucket / item / period table walk via BeautifulSoup.
- Remaining phases per the plan:
  - Phase 2: principal_meta_parser (TDD, RED → GREEN)
  - Phase 3: lobbyist_time_report_parser (TDD, RED → GREEN; Brooks 11052 fixture)
  - Phase 4: tier_2_materialize (TDD, integration over checkpoint dirs)
  - Phase 5: tier_2_materialize_cli (thin wrapper)
  - Phase 6: run + spot-check on Dan's machine (against `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/`)
  - Phase 7: doc-drift fix (principal 12997 WCTA name correction) + results writeup + RESEARCH_LOG / STATUS updates

Held over from prior sessions (orthogonal to Tier-2):

- `lobbying@wi.gov` reply on the Schlaak grid-AJAX filter
- SAL table parser/ingest (data captured as `WI_directory_state_agency_liaisons.xls`)
- Cross-session principal_id stability investigation
- Possible PR + merge of `wi-disclosure-explore` — Dan's call after Tier-2 lands

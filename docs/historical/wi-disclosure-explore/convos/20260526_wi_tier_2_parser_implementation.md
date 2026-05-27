# wi_tier_2_parser_implementation

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Originating plan:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md)
**Originating convo:** [`convos/20260526_wi_tier_2_parser_plan.md`](20260526_wi_tier_2_parser_plan.md)

## Summary

Picked up at Phase 0 of [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md) per the prior session's handoff. Shipped Phase 0 (high-volume fixture capture) and Phase 1 (v1.1 → v1.2 disclosure-data schema bump under TDD), then wrote Phase 2 RED tests for the principal-meta parser. Paused before Phase 2 GREEN (parser implementation) to keep the implementation work on a fresh context window. Two design questions surfaced during the session that Dan locked: (a) Percent Allocation rows emit at per-item level (not bucket-totaled), and (b) free-text fields the v1.1 Organization model has no home for (CEO Name / Business Or Interest / Lobbying Interests prose) flow through a side-channel dict alongside the typed Organization record. Both are "ship the data shape first, design the schema once we've seen it" calls aimed at a future v1.3 typed sub-entity bump.

## Session-start context

Branch state at session start: `aebe8e2` (matches handoff SHA). Pre-flight verified:

- Local `main` is in sync with `origin/main` at `94dc75d`.
- No other branch has touched `src/lobby_analysis/models/filings.py` since the original `lobbying-data-model` branch — the planned v1.2 schema bump (Phase 1) is collision-free vs. the multi-committer constraint.
- 944 principal-checkpoint JSONs + 776 lobbyist-checkpoint JSONs available under `~/data/lobby_analysis/disclosures/WI/` via the worktree's `data/` symlink.
- Schema-layer scope reminder absorbed: this plan touches `src/lobby_analysis/models/` (disclosure-data contract), NOT `src/lobby_analysis/models_v2/` (statute-metadata contract for Prong 1).

Session-start cleanup committed at `3ccc042`: two `cp_perm_diag*.html` stubs from a prior dotfiles cp-permission diagnostic were sitting in `tests/fixtures/wi/`; moved to `notes/cp_perm_diag/` so the fixture dir is clean for the Tier-2 work.

## Topics Explored

- Phase 0 fixture capture — checkpoint JSON shape (`{"principal_id": int, "html": "...", ...}`), grep heuristic for populated allocation buckets, top-30 by HTML size with `no_results=0` filter
- Phase 0 structural surprise — `<h4 class="card-title">Legislative Bills/Resolutions</h4>` appears TWICE per principal page (once under `<h3>Lobbying Interests</h3>`, once under `<h3>Percent Allocation of Lobbying Effort</h3>`)
- Phase 0 snapshot-timing finding — only 3 of 770 lobbyists have all 4 Time Report Summary periods populated; 420 match the 2-populated/2-zero norm because P3 (Jan-Jun 2026) is in progress and P4 (Jul-Dec 2026) hasn't started
- Phase 1 TDD on v1.2 schema bump — 7 RED tests, 2 fields added (`total_hours_communicating` + `total_hours_other` on `LobbyingFiling`), 7 GREEN, noridoc updated
- Phase 2 reconnaissance — Total Lobbying Effort is a 3-row × N-period table (Expenditures, Hours Communicating, Hours Other); Percent Allocation is a 6-bucket nested-card structure with per-item per-period %s
- Whether to roll up Percent Allocation %s to bucket totals at parse time (decision: no — keep at per-item level)
- Whether `Organization` has a home for CEO Name + Business Or Interest + Lobbying Interests prose (decision: no — emit through side-channel dict)

## Provisional Findings

- **Phase 0 ranking heuristic for principal fixtures:** Sort all 944 checkpoint JSONs by `no_results_count` (count of `<div class="no-results">` divs anywhere on the page) ascending, then by HTML byte size descending. The unique top candidate at `no_results=0` is **Dairy Business Association (11590)** — all 6 Percent Allocation buckets populated, 3 lobbyists, $88,568.50 spend. Second-pick by content-size is **Wisconsin Manufacturers & Commerce (11637)** — 2.1 MB HTML, 10 lobbyists, $911,593.49 spend, but `no_results=4`.

- **Same-h4-text-different-section pattern:** The string `<h4 class="card-title">Legislative Bills/Resolutions</h4>` appears under TWO different `<h3>` parents on a principal page:
  1. `<h3>Lobbying Interests</h3>` — the bill-by-bill list of what the principal is registered to lobby on (no $ or %, just bills + descriptions + topics)
  2. `<h3>Percent Allocation of Lobbying Effort</h3>` — the per-bill per-period % effort allocation table

  The parser must distinguish the two sections by their parent `<h3>` ancestor.

- **Top Lobbyist confirmed as Bryan Brooks (11052) at 41 principals.** HTML is 63 KB. Time Report Summary has 4 columns (Jan-Jun 2025 / Jul-Dec 2025 / Jan-Jun 2026 / Jul-Dec 2026) but only the first 2 are populated: Communication = [102.50, 195.00, 0, 0] and Other = [566.00, 673.90, 0, 0].

- **"All 4 periods populated" structurally unachievable on the 2026-05-26 snapshot.** Histogram across 770 lobbyists with Time Report Summaries: 146 / 128 / 420 / 76 / 3 (zero through four periods). Brooks's 2-populated/2-zero pattern is the realistic norm.

- **Total Lobbying Effort table is 3 rows × N period columns** (verified on 11590 + 11348):
  - Row 1: `Total Lobbying Expenditures` — `$X.XX` per period
  - Row 2: `Total Hours Communicating` — `X.XX` per period
  - Row 3: `Total Hours Other` — `X.XX` per period

  Period columns on the 2026-05-26 snapshot are 2025 Jan-Jun + 2025 Jul-Dec + Total. The principal-side Total Lobbying Effort table only shows COMPLETED semesters, while the Percent Allocation section shows all 4 with empty cells for in-progress 2026 periods.

- **Percent Allocation section is bill-itemized, not bucket-totaled.** Each of the 6 bucket `<h4 class="card-title">` cards either has `<div class="no-results">No X found.</div>` (empty bucket) or contains a list of item cards each carrying its own 5-column table of per-period %s. Computing bucket-level totals would require summing per-item %s within each bucket card — but Dan's call was to skip the rollup and ship the per-item rows directly.

- **CEO Name extraction is simple:** `<strong>CEO Name:</strong><br />\n{name} <br /><br />`. Tim Trotter on 11590. Pattern is also present for `Business Or Interest:` and `Lobbying Interests:` (free-text prose). Absent on privacy-redacted principals (11530-class).

- **v1.1 `Organization` has no free-text catch-all.** Fields are `id`, `name`, `classification`, `contact_details`, `identifiers`, `sector`, `legal_form`, `source_state`. CEO / Business / Lobbying-Interests prose don't fit any of those cleanly. Dan picked the side-channel dict pattern over either a schema bump or deferral.

- **`ContactDetail.type` v1.1 Literal is `{"address", "phone", "email", "website"}`** — NOT `"url"`. Caught in test design.

## Decisions Made

- **Convo name:** `20260526_wi_tier_2_parser_implementation.md` (this file).

- **Diagnostic cleanup:** Moved `cp_perm_diag.html` + `cp_perm_diag_dest2.html` (56-byte dotfiles cp-permission stubs) from `tests/fixtures/wi/` to `notes/cp_perm_diag/`. Committed at `3ccc042`.

- **Phase 0 principal fixture picks:** 11590 (Dairy Business Association, 698 KB, fully populated allocation buckets) + 11637 (Wisconsin Manufacturers & Commerce, 2.1 MB, sparse-allocation variant with heavy Lobbying Interests).

- **Phase 0 lobbyist fixture pick:** 11052 Bryan Brooks (top lobbyist at 41 principals, 63 KB, 2-populated/2-zero Time Report Summary pattern).

- **Plan Q1 (provenance population) → YES:** Phase 2/3 parsers populate `LobbyingFiling.provenance` with `source_url` and `extracted_at`. Sets a precedent for downstream extraction work.

- **Plan Q2 (cheap add-ins) → NO additions:** Only the principal-12997 WCTA name fix in Phase 7. State Agency Liaisons table parser and cross-session principal_id stability stay held over.

- **Q3 (Percent Allocation aggregation) → per-item-level rows, NOT bucket-totaled.** Dan: "long term I think we'll go B [typed sub-entity], but let's try A just to see what the data look like." Parser's fourth tuple element is a list of dicts, one per (principal_id, bucket, item_id, item_name, item_description, period_label, percent) entry. Empty period cells are skipped, not emitted with percent=None.

- **Q4 (CEO/Business/Lobbying-Interests prose location) → side-channel dict, NOT schema bump.** Parser's second tuple element is a dict with keys `ceo_name`, `business_or_interest`, `lobbying_interests_prose` (all `str | None`). Long-term v1.3 lifts the dict into typed `Organization` fields alongside the planned `LobbyingEffortAllocation` sub-entity.

- **Phase 2 parser contract locked:**
  ```python
  def parse_principal_meta(
      html: str, principal_id: int
  ) -> tuple[
      Organization,                # typed (v1.1 + v1.2 schema)
      dict,                        # principal-extras side-channel
      list[LobbyingFiling],        # typed (v1.2 schema)
      list[dict],                  # bill-effort items, schemaless prototype
  ]
  ```

- **`REDACTED_PRINCIPAL_IDS = {11530, 13137}`** module constant in the parser. Empty `<h2>` is a `ParseError` for any principal NOT in this set; for the redacted set, the parser emits `Organization(name=f"[redacted principal {id}]", ...)`.

## Results

### Commits this session

All pushed to `origin/wi-disclosure-explore`:

- `3ccc042` chore: move cp_perm_diag stubs out of tests/fixtures/wi/
- `01388e6` wi: tier-2 parser fixtures (populated principals + lobbyist)
- `0debed0` models v1.2: tier-2 hours field tests (red)
- `f50c7e7` models v1.2: add hours fields to LobbyingFiling (green)
- `698897b` models v1.2: noridoc update
- `a5dae17` convo: wi_tier_2_parser_implementation — Phase 0 + Phase 1 shipped (mid-session checkpoint, superseded by the end-of-session commit)
- `0481559` wi: tier-2 principal-meta parser tests (red)

### Test deltas

- New `tests/test_models_v1_2.py` — 7 tests, all GREEN after Phase 1
- New `tests/test_wi_principal_meta_parser.py` — 21 tests, RED at collection (ImportError) per the plan; will turn GREEN once Phase 2 implementation lands
- Combined `test_models.py` + `test_models_v1_1.py` + `test_models_v1_2.py`: 126 pass
- Combined `tests/test_wi_*.py` (existing modules): 49 pass
- Full suite: 1462 pass, 3 pre-existing `test_pipeline.py` baseline failures (`test_ca_snapshot_loads_and_flags_incapsula_stubs`, `test_brief_contains_all_rubric_items_and_instructs_subagent`, `test_stamp_rows_adds_provenance` — owned by archived `pri-2026-rescore`; hardcoded `2026-04-13` data path; orthogonal to Tier-2; unchanged by this session)

### Fixtures captured

In `tests/fixtures/wi/`:

- `principal_11590_populated.html` (Dairy Business Association, 698,805 bytes) — `no_results=0`, 3 lobbyists, $37,840.00 / $50,728.50 / $88,568.50 spend; Total Hours Communicating = 158.50 / 100.50 / 259.00; Total Hours Other = 307.00 / 254.00 / 561.00. CEO Tim Trotter.

- `principal_11637_populated.html` (Wisconsin Manufacturers & Commerce, 2,101,475 bytes) — 10 lobbyists, $496,501.03 / $415,092.46 / $911,593.49 spend; Total Hours Communicating = 543.50 / 547.50 / 1091.00; Total Hours Other = 1971.45 / 1777.75 / 3749.20. Heavy Lobbying Interests, sparse Percent Allocation.

- `lobbyist_11052_populated.html` (Bryan Brooks, 64,732 bytes) — 41 principals; Communication hours = [102.50, 195.00, 0, 0]; Other hours = [566.00, 673.90, 0, 0].

## Open Questions

None blocking the next session. All design questions resolved this session.

Held over from prior sessions (orthogonal to Tier-2):

- `lobbying@wi.gov` reply on the Schlaak grid-AJAX filter
- SAL table parser/ingest (data captured as `WI_directory_state_agency_liaisons.xls`)
- Cross-session principal_id stability investigation
- Possible PR + merge of `wi-disclosure-explore` — Dan's call after Tier-2 lands

## Next Steps

**Next agent starts at Phase 2 GREEN.** Implement `src/lobby_analysis/io/wi/principal_meta_parser.py` with:

```python
def parse_principal_meta(
    html: str, principal_id: int
) -> tuple[Organization, dict, list[LobbyingFiling], list[dict]]
```

Key implementation guidance:

- BeautifulSoup + lxml (matches existing parsers like `principal_parser.py`).
- Module constant: `REDACTED_PRINCIPAL_IDS = {11530, 13137}`.
- Custom `ParseError` class (or reuse the one from `authorization_parser`).
- Org name: extract from `<h2 class="display-4">`. Empty + non-redacted ID → `ParseError`. Empty + redacted ID → name = `f"[redacted principal {id}]"`.
- Extras dict: parse the three `<strong>X:</strong><br />\n{value}<br /><br />` patterns under the Principal Information area for `Business Or Interest`, `Lobbying Interests`, `CEO Name`. All keys present in the returned dict; values None when the corresponding strong is absent (e.g., redacted case).
- Contact details: parse the Contact card — extract `address` (multi-line; combine person-info `<br />` lines), `phone` (after `<i class="fa fa-phone"></i>`), `email` (`<a href="mailto:...">`), `website` (`<a href="http://..."><i class="fa fa-globe"></i>`).
- Total Lobbying Effort table: find `<h3>Total Lobbying Effort</h3>`, walk the 3-row × N-column table, emit one `LobbyingFiling(filing_type="expenditure_report", filer_organization=org, filer_role="client", reporting_period_start=..., reporting_period_end=..., total_expenditure=..., total_hours_communicating=..., total_hours_other=..., provenance=...)` per non-summary column (skip the `Total` column).
- Provenance: `source_url=f"https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/{principal_id}"`, `extracted_at=datetime.now(timezone.utc)`, `extraction_method="direct_copy"`.
- Percent Allocation items: find `<h3>Percent Allocation of Lobbying Effort</h3>`, walk each of the 6 bucket `<h4 class="card-title">` cards in DOM order, then for each item card inside extract `(bucket, item_id, item_name, item_description, period_label, percent)`. Item ID is the integer at the end of `panel-bill-{id}` / `panel-billeffort-{id}` / `panel-budgetbillsubjecteffort-{id}` HTML IDs (the prefix varies by bucket). Period labels match the table headers exactly: `2025 January - June`, `2025 July - December`, `2026 January - June`, `2026 July - December`. Skip empty cells (no `%` value); do not emit rows with percent=None.

Remaining phases after Phase 2 GREEN:
- Phase 3: lobbyist_time_report_parser (TDD; Brooks 11052 fixture; 2-populated/2-zero realistic norm)
- Phase 4: tier_2_materialize (TDD, integration over checkpoint dirs; emits 4 TSVs: `WI_principals`, `WI_lobbyists`, `WI_principal_filings`, `WI_lobbyist_filings`, plus the new bill-effort items TSV `WI_principal_bill_efforts.tsv` and presumably an analogous lobbyist-side artifact if the lobbyist parser also emits item-level rows)
- Phase 5: tier_2_materialize_cli (thin wrapper)
- Phase 6: run + spot-check on `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/`
- Phase 7: doc-drift fix (principal 12997 WCTA name correction) + results writeup + RESEARCH_LOG / STATUS updates

**One-sentence handoff for the next agent:** Phase 2 RED tests for the principal-meta parser are committed at `0481559` against `tests/test_wi_principal_meta_parser.py`; pick up at Phase 2 GREEN by implementing `src/lobby_analysis/io/wi/principal_meta_parser.py` per the contract locked in this convo's "Decisions Made" section, watch the 21 tests go green, then proceed to Phase 3 against `lobbyist_11052_populated.html`.

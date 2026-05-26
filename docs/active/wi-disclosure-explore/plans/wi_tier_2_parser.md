# WI Tier-2 Parser Implementation Plan

**Goal:** Parse per-period topic, dollar, hours, and activity-allocation data already present in the 944 principal HTMLs and 774 lobbyist HTMLs on disk into `LobbyingFiling` and `Organization` records — without any new HTTP fetches. Bump the disclosure-data model layer from v1.1 to v1.2 to add hours fields.

**Originating conversation:** [`convos/20260526_wi_tier_2_parser_plan.md`](../convos/20260526_wi_tier_2_parser_plan.md)

**Context:** The 2026-05-26 scrape sessions captured 944 principal-page HTMLs and 774 lobbyist-page HTMLs but only parsed the authorization-edge tables from them. The remaining sections — Lobbying Interests, Total Lobbying Effort (per-semester $ and hours), Percent Allocation of Lobbying Effort, plus the lobbyist-side Time Report Summary — contain the per-period dollar totals, communication hours, and activity-area distribution that downstream Compendium 2.0 projections (FOCAL 7.x financials; FOCAL 8.x activity; PRI E1/E2 expenditure) consume. Parsing what's already on disk is the highest-leverage next step.

**Schema-layer scope (load-bearing — read carefully):** This plan touches `src/lobby_analysis/models/` (the disclosure-data contract: `LobbyingFiling`, `LobbyistRegistration`, `Organization`, `Person`, etc.). It does NOT touch `src/lobby_analysis/models_v2/` (the statute-metadata cell contract for Prong 1). The two layers are related but version independently. When this plan says "bump to v1.2," it means the disclosure-data layer only; the cell layer's versioning is unaffected.

**Confidence:** High on the data being there — verified by direct inspection of 4 committed fixtures plus 3 web-search-confirmed cross-references for entity identity. Medium on the parser shape — 3 of 4 fixtures lack populated activity sections, so the implementing agent must capture 2-3 new fixtures from high-volume principals before writing tests.

**Architecture:** Two new parsers paralleling the existing `principal_parser.py` / `authorization_parser.py` pattern. Output emits `Organization` records (one per principal, with lobbying-interests prose + contact details) plus `LobbyingFiling` records (one per (principal, semester) for expenditure_reports, one per (lobbyist, semester) for activity_reports). Tier-2 only; tier-3 (per-(lobbyist, principal, semester) detailed time reports + per-principal SLAE itemizations) is out of scope.

**Branch:** `wi-disclosure-explore`. No new top-level branch.

**Tech Stack:** BeautifulSoup + lxml (matches existing parsers), pytest, pydantic v2 via `lobby_analysis.models`. No new dependencies.

---

## Locked Decisions (from originating conversation)

- **Scope:** Tier 2 only. No new HTTP fetches.
- **Sequencing:** Principal-side first, lobbyist-side mirrors after.
- **Schema:** v1.1 → v1.2 bump on `src/lobby_analysis/models/filings.py`. Add `total_hours_communicating: float | None` and `total_hours_other: float | None` to `LobbyingFiling`. Mandatory Phase 1.
- **ID scheme:** `WI-principal-{id}` for `Organization.id`; `WI-lobbyist-{id}` for `Person.id`. Matches uppercase-two-letter `source_state` convention.
- **Source of truth for materialization:** rebuild from checkpoint JSONs at `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/` and `_authorization_scrape_checkpoints/`, not from the derived TSVs.

---

## Out of Scope (Explicitly)

- **No new HTTP fetches.** All data comes from existing checkpoint JSONs on disk.
- **No tier-3 work.** Per-(lobbyist, principal, semester) detailed time reports and per-principal SLAE itemizations are a separate plan. They require both new fetches and a reconnaissance step on at least one page first.
- **No `LobbyingPosition` / `LobbyingExpenditure` / `LobbyingEngagement` / `Gift` sub-entities.** Those need tier-3 data to populate meaningfully (the Tier-2 summary fields are aggregate totals, not itemized lines).
- **No `models_v2/` cell-layer changes.** Statute-metadata is a separate contract.
- **No fixing the Schlaak / grid-AJAX filter mystery.** Held over to Dan's `lobbying@wi.gov` thread.

## In Scope (Cheap Add-Ins)

- **Fix the documentation drift** on principal 12997's organization name in `results/20260526_wi_principal_side_scrape_results.md` line 65 — change "Wisconsin Cable Telecommunications Association" to "Wisconsin County Treasurers Association". The fixture body is unambiguous; the scrape writeup got the acronym expansion wrong from context. Single-line edit.
- **Add a process note** to that same results doc explaining the acronym-expansion drift and the principle that future writeups should verify entity names from page body, not infer from context.

---

## Testing Plan

I will write 4 new test files, all under `tests/` matching existing naming conventions.

- `tests/test_models_v1_2.py` — TDD tests for the v1.2 schema bump (paralleling `test_models_v1_1.py`'s structure). Tests assert that `LobbyingFiling` accepts the two new optional hours fields, that omitting them still validates (non-breaking), that they round-trip through `model_dump()` + `model_validate()`, and that an empty filing serializes without the fields when they're None (matching pydantic v2 default behavior with the existing fields).

- `tests/test_principal_meta_parser.py` — unit tests for parsing the principal-page non-edge sections into `Organization` + `LobbyingFiling` records. Tests cover: lobbying-interests prose extraction; contact-details extraction (address, phone, email, website); CEO name extraction (when present, may be absent); total-expenditures parsing across multiple semesters; hours parsing for both communicating + other; activity-allocation percentages across the 6 buckets; the populated-bills case using the new high-volume fixture; the empty-bills case using the Lexia 11348 fixture (which reads "No legislative bills/resolutions found." across all sections); the privacy-redacted case using fixture 11530 (Organization gets minimal fields, `LobbyingFiling` still emits if amounts are present); the low-spend-exempt case using 12997 (emits `is_itemized=False` plus zero totals, the lobbying-interests prose still parses).

- `tests/test_lobbyist_time_report_parser.py` — unit tests for parsing the lobbyist-page Time Report Summary section into `LobbyingFiling(filing_type="activity_report")` records. Tests cover: per-semester hours-communicating + hours-other extraction; the 4-period table layout (Jan-Jun 2025 / Jul-Dec 2025 / Jan-Jun 2026 / Jul-Dec 2026); zero-hours periods (should still emit a filing with zeros, not silently skip); the soft-404 case (no Time Report Summary present → parser raises `ParseError`, not silent empty); a populated multi-principal case using the new lobbyist fixture.

- `tests/test_tier_2_materialize.py` — integration tests for the materialization step that reads checkpoint JSONs from disk, runs parsers, and emits TSV output. Tests cover: deterministic ordering (sorted by ID); idempotent re-run (running twice produces byte-identical output); failed checkpoints (e.g., the Neumann-Ortiz soft-404) surface in `_tier_2_parse_failures.tsv` as warnings, not silent drops; the materialize output joins cleanly with the existing authorizations TSV on `principal_id` and `lobbyist_id`; the `Organization.id` and `Person.id` follow the locked `WI-principal-{id}` / `WI-lobbyist-{id}` scheme.

NOTE: I will write *all* tests before I add any implementation behavior.

These tests do NOT cover (a) Pydantic model field shape for its own sake — that's tested via behavioral round-trip in `test_models_v1_2.py`, not by asserting on class attributes; (b) HTTP fetching — we are not fetching; (c) the Schlaak case or any of the authorization-edge logic — that's already covered by the existing test suite.

---

## Implementation Steps

### Phase 0 — Fixture Capture (no code changes)

1. From the data store on Dan's machine, grep `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/*.json` for principals whose HTML contains `<h4>Legislative Bills/Resolutions</h4>` followed by non-"No legislative bills/resolutions found." content. Pick 2-3 principals with the richest combination of populated buckets. The top-15-lobbyist principals (Wisconsin Hospital Association, Wisconsin Automobile and Truck Dealers Association, etc.) are good candidates per the 2026-05-26 scrape's headline.
2. Copy the chosen HTMLs to `tests/fixtures/wi/` as `principal_{id}_populated.html`.
3. Also grep `_authorization_scrape_checkpoints/*.json` for one lobbyist with a fully-populated Time Report Summary (all 4 periods showing non-zero hours, ≥3 principals authorized). The top-spend lobbyist (Bryan Brooks, 41 principals) is a good candidate.
4. Copy the chosen HTML to `tests/fixtures/wi/` as `lobbyist_{id}_populated.html`.
5. Commit fixtures only: `wi: tier-2 parser fixtures (populated principals + lobbyist)`.

### Phase 1 — Schema Bump v1.1 → v1.2 (mandatory)

6. Write `tests/test_models_v1_2.py` with the four behavior tests listed in the Testing Plan (round-trip + field-presence + non-breaking-default + serialize-omit-when-None). Reference the v1.1 test file's `_make_*` factory pattern.
7. Run the new test file. Confirm all tests fail with `AttributeError` / `ValidationError` because the fields don't exist yet.
8. Commit: `models v1.2: tier-2 hours field tests (red)`.
9. Add to `LobbyingFiling` in `src/lobby_analysis/models/filings.py`:
   ```
   total_hours_communicating: float | None = Field(
       default=None,
       description="Total hours spent communicating with officials (WI / FOCAL 7.x time-spent)",
   )
   total_hours_other: float | None = Field(
       default=None,
       description="Total non-communication lobbying hours (preparation, research, monitoring)",
   )
   ```
10. Run the entire existing model test suite to confirm no breakage: `uv run pytest tests/test_models.py tests/test_models_v1_1.py tests/test_models_v1_2.py`.
11. Commit: `models v1.2: add hours fields to LobbyingFiling (green)`.
12. Update `src/lobby_analysis/models/docs.md` (the Noridoc file) to mention v1.2's hours additions in the "Things to Know" section.
13. Commit: `models v1.2: noridoc update`.

### Phase 2 — Principal-Side Tier-2 Parser (TDD, RED first)

14. Write `tests/test_principal_meta_parser.py` with all behavior tests listed in the Testing Plan above. Tests reference the new populated fixture, the existing 12997 / 11348 / 11530 fixtures, and assert against expected `Organization` + `LobbyingFiling` shapes including specific dollar amounts and hours visible in the fixtures.
15. Run the test file. Confirm all tests fail with `ImportError` (no parser module yet).
16. Commit: `wi: tier-2 principal-meta parser tests (red)`.
17. Implement `src/lobby_analysis/io/wi/principal_meta_parser.py` with public function `parse_principal_meta(html: str, principal_id: int) -> tuple[Organization, list[LobbyingFiling]]`. Parse: page title (organization name; raises `ParseError` if missing AND principal isn't in the privacy-redacted whitelist {11530, 13137}); lobbying-interests prose; CEO name; contact rows (address + phone + email + website); 6 activity-allocation buckets per semester; total expenditures + hours per semester. Emit one `Organization(id=f"WI-principal-{principal_id}", ...)` (per principal) and one `LobbyingFiling(filing_type="expenditure_report", filer_organization=..., filer_role="client", reporting_period_start/end set, total_expenditure, total_hours_communicating, total_hours_other, ...)` per non-empty semester.
18. Run tests, watch them go green. If any test fails, fix the parser (NOT the test). Stop and ask Dan if a test reveals a finding that should be a research question instead of a code bug — the existing scraper code has a precedent of pausing-and-surfacing rather than silently patching (e.g., the soft-404 detection on lobbyist 12717).
19. Commit: `wi: tier-2 principal-meta parser (green)`.

### Phase 3 — Lobbyist-Side Tier-2 Parser (TDD, RED first)

20. Write `tests/test_lobbyist_time_report_parser.py` with tests covering Time Report Summary extraction. Reference the new populated lobbyist fixture + the existing 11042 fixture.
21. Run tests. Confirm failure.
22. Commit: `wi: tier-2 lobbyist time-report parser tests (red)`.
23. Implement `src/lobby_analysis/io/wi/lobbyist_time_report_parser.py` with `parse_lobbyist_time_reports(html: str, lobbyist_id: int) -> tuple[Person, list[LobbyingFiling]]`. Emit one `Person(id=f"WI-lobbyist-{lobbyist_id}", ...)` (per lobbyist; extract name + contact details from the lobbyist page) and one `LobbyingFiling(filing_type="activity_report", filer_person=..., filer_role="lobbyist", reporting_period_start/end set, total_hours_communicating, total_hours_other)` per non-empty semester.
24. Run tests, watch them go green.
25. Commit: `wi: tier-2 lobbyist time-report parser (green)`.

### Phase 4 — Materializer (TDD, RED first)

26. Write `tests/test_tier_2_materialize.py` with idempotency + deterministic-ordering + join + ID-scheme tests.
27. Run tests. Confirm failure.
28. Commit: `wi: tier-2 materializer tests (red)`.
29. Implement `src/lobby_analysis/io/wi/tier_2_materialize.py` with `materialize_tier_2(principal_checkpoints_dir: Path, lobbyist_checkpoints_dir: Path, output_dir: Path) -> None`. Walks both checkpoint dirs, runs the two parsers, emits 4 TSVs to `output_dir`:
   - `WI_principals.tsv` — Organization records flattened (one row per principal: id, name, classification, legal_form, sector, contact_details serialized, lobbying_interests_prose, ceo_name)
   - `WI_lobbyists.tsv` — Person records flattened (one row per lobbyist: id, name, contact_details serialized, license dates)
   - `WI_principal_filings.tsv` — LobbyingFiling expenditure_reports (one row per (principal_id, semester): total_expenditure, total_hours_communicating, total_hours_other, allocation_bucket_percentages_json)
   - `WI_lobbyist_filings.tsv` — LobbyingFiling activity_reports (one row per (lobbyist_id, semester): total_hours_communicating, total_hours_other)

   Each row carries `provenance.source_url`. Records that fail to parse (soft-404, etc.) emit a warning row to `_tier_2_parse_failures.tsv` rather than crashing the whole run. Materializer is idempotent: same inputs → byte-identical TSVs.
30. Run tests, watch them go green.
31. Commit: `wi: tier-2 materializer (green)`.

### Phase 5 — CLI Wrapper

32. Add `src/lobby_analysis/io/wi/tier_2_materialize_cli.py` mirroring the existing `unify_authorizations_cli.py` shape — argparse for `--principal-checkpoints`, `--lobbyist-checkpoints`, `--output-dir`. No new tests; the CLI is a thin pass-through covered by the materializer's tests.
33. Commit: `wi: tier-2 materialize CLI`.

### Phase 6 — Run + Spot Check

34. On Dan's machine: `uv run python -m lobby_analysis.io.wi.tier_2_materialize_cli --principal-checkpoints ~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/ --lobbyist-checkpoints ~/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints/ --output-dir ~/data/lobby_analysis/disclosures/WI/`.
35. Spot-check the output: pick 3 principals with known data (Lexia 11348 should show $65,225.58 YTD; the new populated fixture should show its known totals; 12997 should show $0.00 + low-spend-exempt flag).
36. Inspect `_tier_2_parse_failures.tsv` — there should be exactly 1 row (the Neumann-Ortiz soft-404 on the lobbyist side). Any other failure is a real parser bug to investigate, NOT to patch silently.

### Phase 7 — Doc Updates + Drift Fix

37. Fix the documentation drift in `results/20260526_wi_principal_side_scrape_results.md` line 65 — change "Wisconsin Cable Telecommunications Association" to "Wisconsin County Treasurers Association".
38. Add a brief note to that same results doc explaining the acronym-expansion drift and the principle that future writeups should verify entity names from page body, not infer from context.
39. Write results doc at `results/YYYYMMDD_wi_tier_2_parser_results.md` summarizing: total principals with non-empty Tier-2 data, total dollars across all principals, total hours, top-10 principals by spend, distribution of activity-allocation across the 6 buckets.
40. Update `RESEARCH_LOG.md` per `update-docs/SKILL.md` conventions.
41. Run `skills/finish-convo/SKILL.md` to checkpoint, push, and update STATUS.md.

---

**Testing Details:** Tests exercise observed-behavior contracts on real WI portal HTML — what specific dollar amounts the parser extracts from the Lexia fixture (which the parser author can verify by eye from the fixture file), what happens when a section reads "No X found" vs is fully populated, what happens on the privacy-redacted case, what happens on the soft-404 case. Tests do NOT assert on pydantic model field types (covered behaviorally via round-trip), do NOT mock HTTP (we don't fetch), do NOT just test that parsers return lists of the right length (they assert on specific values from the fixtures).

**Implementation Details:**
- All 4 parser/materializer modules live under `src/lobby_analysis/io/wi/`, paralleling the existing `principal_parser.py` / `authorization_parser.py` shape.
- `ParseError` discipline: raise loudly on page-shape changes, never return silent empty results. The existing parsers set this precedent.
- The 6 activity-allocation buckets are observably WI-specific; the parser should hard-code them as a `_BUCKET_HEADERS` tuple at module top so future cross-state work can grep for it as a known state-specific dependency.
- Dollar parsing: handle the `$0.00`, `$32,537.58`, and `Total $X` formats observed in the Lexia + WCTA fixtures. Comma as thousands separator; no parens for negatives.
- Hours parsing: handle `48.00`, `0`, and `0.00` forms. Hours can be zero for valid filings (low-activity periods). Empty cells (no entry for a future period) map to `None`, not `0.0`.
- `Organization` records emit `source_state="WI"`, `classification` left null (would need separate inference); `contact_details` typed-tagged with `type` ∈ {address, phone, email, website}.
- Privacy-redacted principals (11530, 13137): emit Organization with `name=f"[redacted principal {id}]"`, the lobbying-interests prose if present, and minimal contact_details. Emit LobbyingFilings with their actual amounts if listed.
- The `provenance` field on `LobbyingFiling`: populate with `source_url` + `retrieved_at` (the checkpoint JSON has a fetch timestamp). Sets a precedent for downstream extraction work; cheap and correct.
- `Person.id` extraction needs name parsing — the lobbyist page title gives "Shawn Pfaff - Lobbying in Wisconsin" or similar. Use the prefix before the dash.

**What could change:**
- If Phase 0 surfaces a high-volume fixture with section structure the existing fixtures don't have (e.g., a "Legislative Bills/Resolutions" table with linked bill numbers), the parser may need an additional sub-parser to handle the extra structure. Surface this to Dan rather than expanding scope — could justify a tier-2.5 follow-up plan.
- The activity-allocation table layout (4-period × 6-bucket cross-tab) is empirically WI-only — other states will publish entirely different structures, so the parser shouldn't try to be cross-state-clever. The `LobbyingFiling` model is reusable; the WI-specific parser is not.
- If Phase 6 spot-check turns up parse failures concentrated in a particular sub-class of principal (e.g., all ceased principals, or all redacted ones), that's a research finding, not a parser bug — stop and document before patching.
- Tier 3 (per-(lobbyist, principal, semester) time-report and SLAE itemization pages) becomes the natural follow-up. The model layer doesn't yet have the right shape for itemized expenditures-per-lobbyist; the `LobbyingExpenditure` sub-entity exists but its `recipient_role` / `recipient_name` fields would need to point to lobbyist `Person` records. Plan that later.
- Cross-state generalization: when the second state's extraction starts, the v1.2 hours fields will either fit cleanly or surface a new schema gap. If they fit, the v1.2 bump pays off across states; if not, this is one piece of evidence informing the next bump.

**Questions:**
- Provenance population on `LobbyingFiling`: recommended yes (source_url + retrieved_at), but this is a precedent-setting choice — confirm before Phase 4.
- Are there other in-scope cheap add-ins beyond the doc drift fix? (Currently only that one is listed; the implementing agent should not expand scope without surfacing.)

---

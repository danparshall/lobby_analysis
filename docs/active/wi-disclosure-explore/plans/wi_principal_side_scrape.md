# WI Principal-Side Completeness Scrape Implementation Plan

**Goal:** Scrape every principal detail page on `lobbying.wi.gov` for the 2025-2026 session to (a) build a principal-side authorization table that mirrors the existing lobbyist-side one and (b) enumerate the set of lobbyists reachable only via principal back-links — i.e., "Schlaak-class" lobbyists that the LobbyistList grid AJAX and the `WI_directory_lobbyists.xls` both silently omit.

**Originating conversation:** [`../convos/20260526_wi_principal_side_scrape_plan.md`](../convos/20260526_wi_principal_side_scrape_plan.md). Reframes load-bearing context first established in [`../convos/20260526_wi_principal_gap_investigation.md`](../convos/20260526_wi_principal_gap_investigation.md).

**Context:** The kickoff session built the lobbyist-side scrape (774 lobbyists → 2,251 `(lobbyist, principal)` authorization rows / 942 distinct principals); a follow-up gap investigation reconciled the 942-vs-904 principal-side discrepancy with the directory `.xls` cleanly (38 ceased + 2 privacy-redacted low-spend-pledge entities) AND surfaced a separate structural finding: at least one currently-active, currently-authorized, licensed Wisconsin lobbyist (Michael Schlaak, ID 12694) is silently omitted from both the grid AJAX (774 IDs) and the directory `.xls` (776 rows), but reachable cleanly by direct URL and by back-link from his principal's page (WCTA, ID 12997). The omission isn't a registration race condition (16-month tenure pre-scrape) and a 5-hour re-fetch this session confirmed both sides are byte-identical to the prior capture. The principal-side scrape is the only mechanism to bound the Schlaak-class population — neither published roster source is exhaustive.

**Confidence:** Moderate-to-high on the architectural shape (it mirrors the lobbyist-side scrape that shipped this morning, parser target verified on the WCTA capture). Lower on (a) whether large active principal pages stay within the empirical size distribution observed in the 42 ceased/low-volume captures and (b) how many Schlaak-class lobbyists actually exist — the latter being the question the scrape exists to answer.

**Architecture:** Three new modules + one CLI, mirroring the lobbyist-side layout under `src/lobby_analysis/io/wi/`:

1. **`principal_parser.py`** — pure function `parse_principal_authorizations(html: str, principal_id: int) -> list[Authorization]`. Extracts every `(lobbyist_id, principal_id, authorized_on, withdrawn_on)` edge from the principal page's "Authorized Lobbyists" section by walking `/Who/LobbyistInformation/2025REG/Information/(\d+)` href back-links.
2. **`principal_id_discovery.py`** — `discover_principal_ids() -> set[int]`. Composes the principal universe as the union of `WI_directory_principals.xls` IDs (904) and the existing auth-graph TSV's `principal_id` column (942 distinct) = 944 IDs.
3. **`principal_materialize.py`** — `build_principal_side_table(checkpoint_dir) -> list[dict]`. Reads all `{principal_id}.json` checkpoints, materializes the principal-side authorization table.

Plus a **fetcher refactor** (recommended, see Step 1 below): extract a generic `fetch_entity_page` / `fetch_or_load_entity` core in a new `entity_fetcher.py`, then have the existing `authorization_fetcher.py` and the new principal fetcher both thin-wrap it. This is the DRY win the existing code structure invites. If Dan prefers a safer option to keep the lobbyist code path untouched, the plan can fall back to duplicating the fetcher as `principal_fetcher.py` — same behavior, ~200 lines duplicated.

Then a **unification step** as a separate module: `unify_authorizations.py` produces `WI_lobbyist_principal_authorizations_unified.tsv` with a `discovered_via ∈ {lobbyist, principal, both}` column. This is the deliverable that answers "how many Schlaak-class lobbyists are there?" — count the rows where `discovered_via == 'principal'` and look at the distinct lobbyists therein.

CLI orchestrator: `scrape_principals.py` — mirrors `scrape_authorizations.py` (discovery → polite fetch with checkpoint/resume → materialize).

**Branch:** `wi-disclosure-explore` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-disclosure-explore/`).

**Tech Stack:** Same as lobbyist-side — `requests`, `beautifulsoup4`, `lxml`, `pytest`, `pandas` (only for the `.xls` read in ID discovery; materialize stays on `csv.DictWriter`).

---

## Pre-flight Checks (5 min)

1. **Verify worktree.** `git -C /Users/dan/code/lobby_analysis/.worktrees/wi-disclosure-explore branch --show-current` should be `wi-disclosure-explore`.
2. **Verify the lobbyist-side scrape outputs exist** (the plan depends on them). `ls ~/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv` should resolve.
3. **Verify the directory `.xls` is in place.** `ls ~/data/lobby_analysis/disclosures/WI/WI_directory_principals.xls` should resolve.
4. **Verify the gap-investigation captures are reachable** (for fixture provenance + the WCTA / Voces / Schlaak cases). `ls ~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/principal_12997.html` (WCTA, 1 lobbyist; will become a parser fixture) and `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/principal_11348.html` (4 lobbyists, biggest in the gap-investigation sample) should both resolve.
5. **Verify portal is up.** Single `GET https://lobbying.wi.gov/Home/Welcome` should return 200. If not, stop.
6. **Sample one moderate-to-large active principal page to bound the size distribution.** Pick a known-high-volume principal from the lobbyist-side TSV (e.g., the Wisconsin Hospital Association or Wisconsin Automobile and Truck Dealers Association — top-tied at 15 lobbyists per the prior session). Fetch its page and check size. If it's significantly over the 157 KB max in the 42-page sample (say >500 KB), update the plan's cost estimate before kicking off the full scrape.
7. **Check for a `lobbying@wi.gov` reply on Dan's end.** If a CSV came back, this plan may be moot — surface and ask.

If any check fails, stop and surface — do not work around silently.

---

## Testing Plan

The parser (`principal_parser.py`) is pure-function and gets full TDD coverage against real-portal HTML fixtures captured during the gap investigation. The fetcher refactor (Step 1) is covered by the existing test suite plus new tests against the generic core. The scrape itself is data collection and is exempt from TDD per the write-a-plan skill's analysis/exploration exception. The materialize step gets a TDD unit test against hand-built checkpoint files.

**Parser unit tests (TDD)** — `tests/test_wi_principal_parser.py`:

- `test_parses_single_lobbyist_principal` — feed `principal_12997.html` (WCTA), assert one `Authorization` record with `(lobbyist_id=12694, principal_id=12997, authorized_on=date(2026,1,8), withdrawn_on=None)`. This is the load-bearing Schlaak case.
- `test_parses_multi_lobbyist_principal` — feed `principal_11348.html` (4 lobbyists in gap-investigation sample), assert four `Authorization` records, all with `principal_id=11348`, distinct `lobbyist_id` values.
- `test_parses_privacy_redacted_principal` — feed `principal_11530.html` (low-spend-pledge redacted; principal-info suppressed but authorized-lobbyists section IS populated, per the gap investigation), assert the lobbyists are still extracted. This is the "redacted-but-graph-published" subcase.
- `test_parses_ceased_principal_with_historical_authorizations` — feed `principal_10949.html` (Apex Clean Energy, ceased 1/22/2025), assert the historical authorizations are still extracted, with `withdrawn_on` populated where the page shows it.
- `test_unparseable_authorized_lobbyists_section_raises_parse_error` — corrupt the WCTA fixture by mangling the section heading, assert `ParseError` (noisy fail; the parser must not silently swallow DOM changes).
- `test_empty_authorized_lobbyists_section_returns_empty_list` — minimal hand-built fixture with a real Authorized Lobbyists heading but no rows; assert `[]`. (Probably won't appear in the wild but the parser must handle it.)

NOTE: Some of these fixtures should be committed under `tests/fixtures/wi/principal_*.html`. The gap-investigation captures live under `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/` (gitignored); copy the ones used as fixtures into the test tree.

**Fetcher refactor tests** — `tests/test_wi_entity_fetcher.py` (new):

- `test_fetch_entity_page_lobbyist_url_template` — verify the lobbyist URL template binding behaves identically to the existing `fetch_lobbyist_page`. (Regression guard for the refactor.)
- `test_fetch_entity_page_principal_url_template` — verify the principal URL template produces the right URL.
- All existing `test_wi_authorization_fetcher.py` tests must continue to pass — those become the regression suite for the refactor.

**Materialize unit test** — `tests/test_wi_principal_materialize.py`:

- `test_build_principal_side_table_from_checkpoints` — write 3 hand-built `{principal_id}.json` files to a `tmp_path`, run `build_principal_side_table`, assert the row count + schema + per-principal lobbyist counts match.

**Unification test** — `tests/test_wi_unify_authorizations.py`:

- `test_unify_produces_three_provenance_classes` — small hand-built lobbyist-side + principal-side input tables that overlap partially; assert the unified output has exactly the right rows in each `discovered_via ∈ {lobbyist, principal, both}` class.
- `test_unify_surfaces_principal_only_lobbyists` — input where one lobbyist appears only in the principal-side table (the Schlaak case), assert it appears in the unified output with `discovered_via='principal'`.

**Integration check (not in pytest):** after the scrape runs and unification produces the unified table, manually verify:
- The Schlaak case (lobbyist 12694, principal 12997, authorized 2026-01-08) is exactly one row with `discovered_via='principal'`.
- The Neumann-Ortiz / Voces case (lobbyist 12717, principal 12900) — previously orphaned due to the lobbyist-side soft-404 — appears with `discovered_via='principal'` and the prior-session-known dates.
- The 902 intersection principals should produce rows where most are `discovered_via='both'` (lobbyist-side scrape saw the same edges) and a small number are `discovered_via='principal'` only (any new Schlaak-class lobbyists).

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Implementation Steps

### Step 1 — Decide and execute the fetcher refactor (15 min, or skip)

**First, ask Dan:** refactor to a generic `entity_fetcher.py` (DRY win, touches tested code) OR duplicate as `principal_fetcher.py` (safer, ~200 lines duplicated)?

**If refactor (recommended):**

1. Create `src/lobby_analysis/io/wi/entity_fetcher.py` with generic `fetch_entity_page(entity_id, url_template, session, ...)` and `fetch_or_load_entity(entity_id, checkpoint_dir, url_template, session, ..., id_field_name)` — the latter parameterizes the checkpoint key field so the lobbyist payload still says `"lobbyist_id"` and the principal payload says `"principal_id"`.
2. Rewrite `authorization_fetcher.py`'s `fetch_lobbyist_page` and `fetch_or_load` as thin wrappers binding `LOBBYIST_PAGE_URL_TEMPLATE` and `id_field_name="lobbyist_id"`. Public API stays identical.
3. Move the `_is_soft_404` helper into `entity_fetcher.py` since the same body marker is expected to apply to all WI portal pages.
4. Run `uv run pytest tests/test_wi_authorization_fetcher.py` — all existing tests must pass unchanged. If they fail, the refactor is wrong; revert and either re-attempt or fall back to duplication.
5. Commit as `wi-scrape: extract generic entity_fetcher; lobbyist fetcher becomes thin wrapper`.

**If duplicate:**

1. Copy `authorization_fetcher.py` to `principal_fetcher.py`, replace `LOBBYIST_PAGE_URL_TEMPLATE` with `PRINCIPAL_PAGE_URL_TEMPLATE = "https://lobbying.wi.gov/Who/PrincipalInformation/{session_id}/Information/{principal_id}"`, rename `lobbyist_id` → `principal_id` throughout.
2. Commit as `wi-scrape: principal-side fetcher (copy of lobbyist fetcher with principal URL)`.

### Step 2 — Commit principal-page test fixtures (5 min)

Copy from gap-investigation captures into the test tree:
- `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/principal_12997.html` → `tests/fixtures/wi/principal_12997.html` (WCTA, 1 lobbyist, the Schlaak case)
- `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/principal_11348.html` → `tests/fixtures/wi/principal_11348.html` (4 lobbyists, multi-row case)
- `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/principal_11530.html` → `tests/fixtures/wi/principal_11530.html` (privacy-redacted; auth section still populated)

Use the Read/Write tools (not `cp` — `cp` across directories is in the ASK list per the bash permission rules).

The 3 ceased-principal fixtures committed by the prior session (`principal_10949.html`, `principal_10973.html`, `principal_11017.html`) are already in `tests/fixtures/wi/` — reuse one of them for `test_parses_ceased_principal_with_historical_authorizations` rather than copying another.

Commit as `wi-scrape: principal-side parser test fixtures (WCTA + 4-lobbyist + redacted)`.

### Step 3 — Write parser tests (RED phase) (15 min)

Create `tests/test_wi_principal_parser.py` with the 6 tests from the Testing Plan. Run `uv run pytest tests/test_wi_principal_parser.py` and verify all 6 fail with `ImportError` (module doesn't exist yet). **Do not proceed until you've seen them fail.**

### Step 4 — Implement parser (GREEN phase) (25 min)

Create `src/lobby_analysis/io/wi/principal_parser.py`:

- Reuse the existing `Authorization` and `ParseError` types from `authorization_parser.py` — import them. This is the same edge data shape; only the page that exposes the edge differs.
- `def parse_principal_authorizations(html: str, principal_id: int) -> list[Authorization]` — find the "Authorized Lobbyists" section (BeautifulSoup, locate by heading text), iterate rows, extract `/Who/LobbyistInformation/2025REG/Information/(\d+)` hrefs + the per-row `Authorized On` and `Withdrawn` date columns.

Be careful about the privacy-redacted case (Step 5 of tests above): the page title is generic and the principal-info fields are suppressed, but the "Authorized Lobbyists" heading IS present and the lobbyist rows ARE populated. The parser shouldn't gate extraction on the principal-info section being present.

Run tests: all 6 should pass. Commit as `wi-scrape: principal-side authorization parser`.

### Step 5 — Implement principal ID discovery (15 min)

`src/lobby_analysis/io/wi/principal_id_discovery.py`:

```
def discover_principal_ids(
    directory_xls_path: Path,
    auth_graph_tsv_path: Path,
) -> set[int]:
    """Union of directory `.xls` principal IDs and existing auth-graph principal IDs."""
```

- Read `WI_directory_principals.xls` with pandas (the file has 3 header rows that need skipping, per the kickoff convo); extract the `Principal ID` integer column → 904 IDs.
- Read `WI_lobbyist_principal_authorizations.tsv` with `csv.DictReader`; extract distinct `principal_id` → 942 IDs.
- Return the union → expected 944 IDs.
- Print a one-line summary (`944 IDs total: 904 dir + 942 auth, 902 intersection, 40 auth-only, 2 dir-only`).

**Unit test** — `tests/test_wi_principal_id_discovery.py` — `test_union_of_two_id_sources` against hand-built tiny `.xls` and TSV fixtures (not the real files; we don't want the test depending on data shape that may shift between branches). Verify the function correctly unions two int sets read from these formats.

Commit as `wi-scrape: principal ID discovery (union of directory .xls + existing auth graph)`.

### Step 6 — Implement principal-side materialize (15 min)

`src/lobby_analysis/io/wi/principal_materialize.py`:

```
def build_principal_side_table(
    checkpoint_dir: Path,
) -> list[dict]:
    """Walk {principal_id}.json checkpoints; produce list-of-dicts in the
    same schema as the lobbyist-side table (lobbyist_id, principal_id,
    authorized_on, withdrawn_on)."""
```

Same shape as `authorization_materialize.py` — copy it as a starting point, swap "lobbyist" ↔ "principal" in the loading direction. The output schema is identical because the edge data is identical; only the discovery path differs.

Unit test per Testing Plan section. Commit as `wi-scrape: principal-side table materialize`.

### Step 7 — Implement unification (20 min)

`src/lobby_analysis/io/wi/unify_authorizations.py`:

```
def unify_authorization_tables(
    lobbyist_side_rows: Iterable[dict],
    principal_side_rows: Iterable[dict],
) -> list[dict]:
    """Compute the union of the two edge tables, with a 'discovered_via'
    column indicating provenance: 'lobbyist', 'principal', or 'both'."""
```

Edge identity = `(lobbyist_id, principal_id, authorized_on)` — withdrawn dates may differ between the two views if one side hasn't refreshed (we expect them to agree, but the unification step is the right place to surface disagreement).

Edge cases worth handling explicitly (per write-a-plan skill):
- Same edge present on both sides with **disagreeing `withdrawn_on`** → emit one row with `discovered_via='both'`, take the more recent of the two `withdrawn_on` values, log a warning.
- Same `(lobbyist_id, principal_id)` present on both sides with **different `authorized_on`** dates → this would mean a re-authorization. Emit both rows (different `(lobbyist_id, principal_id, authorized_on)` keys), tag each with whichever side(s) saw it.
- Principal-side-only rows where the lobbyist_id is NOT in our known lobbyist set (from the grid AJAX): these are the Schlaak-class additions. Tag them in the output with `lobbyist_in_grid=False` for easy filtering.

Unit tests per Testing Plan section. Commit as `wi-scrape: authorization-table unification with provenance + lobbyist-in-grid flag`.

### Step 8 — Build the principal-side CLI (10 min)

`src/lobby_analysis/io/wi/scrape_principals.py` — copy `scrape_authorizations.py` as a template, swap discovery / fetcher / materialize calls. Defaults:

- Checkpoint dir: `~/data/lobby_analysis/disclosures/WI/_principal_scrape_checkpoints/`
- Output TSV: `~/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations_principal_side.tsv`
- Delay: 1.0 s
- `--limit N` for sanity-check runs

Add a `unify` subcommand (or a separate `unify_authorizations_cli.py`) that reads both TSVs and writes `WI_lobbyist_principal_authorizations_unified.tsv` with the provenance column.

Commit as `wi-scrape: principal-side CLI runner + unification CLI`.

### Step 9 — Sanity-check scrape (10 principals) (5 min wall, 10 min observation)

Run with `--limit 10`. Eyeball:
- All 10 checkpoint JSONs exist.
- Each has non-empty parsed authorizations.
- Spot-check 2-3 against principal pages in a browser.
- **Specifically verify**: scrape principal 12997 (WCTA) in the small batch; confirm the materialized row includes lobbyist 12694 (Schlaak) with `authorized_on=2026-01-08`. This is the load-bearing case for the whole plan.

If anything looks off, stop and surface.

### Step 10 — Full scrape (~17 min wall) (background)

Remove `--limit`. Run the full 944-principal scrape. Background-friendly; checkpoint/resume means a crash mid-run is recoverable.

### Step 11 — Materialize + unify + results writeup (20 min)

1. Run `build_principal_side_table` against the full checkpoint dir → `WI_lobbyist_principal_authorizations_principal_side.tsv`.
2. Run `unify_authorization_tables` against both TSVs → `WI_lobbyist_principal_authorizations_unified.tsv`.
3. Compute the load-bearing numbers:
   - Row count of unified table.
   - Distinct lobbyist count in unified table vs. 745 from the lobbyist-side scrape. The **delta** is the Schlaak-class population.
   - Per-`discovered_via` row counts (lobbyist / principal / both).
   - List of all `lobbyist_id` values appearing in `discovered_via ∈ {principal}` — these are the Schlaak-class lobbyists. For each, fetch their lobbyist detail page (cheap; ~N IDs × 1 sec) and capture license issued date, principal count, and `License Type` field. Look for any pattern that explains the directory `.xls` filter rule.
   - Per-`discovered_via` distinct principal counts.
4. Write `docs/active/wi-disclosure-explore/results/20260527_wi_principal_side_scrape_results.md` (or whatever date the implementing agent runs this). Include:
   - Provenance header.
   - All the load-bearing numbers above.
   - The Schlaak-class lobbyist list with their detail-page metadata.
   - Whether the `License Type` field gives us a clean predicate for what the directory `.xls` filters on.
   - Any soft-404 cases the principal-side fetch surfaced.

### Step 12 — Update RESEARCH_LOG + STATUS + finish-convo (10 min)

Append the session entry to `docs/active/wi-disclosure-explore/RESEARCH_LOG.md` (top of file).
Update `STATUS.md` "Active Research Lines" → `wi-disclosure-explore` row, and append a "Recent Sessions" one-liner.
Run finish-convo to push.

---

**Testing Details**

The parser tests verify behavior against real-portal HTML snapshots (committed fixtures) — they check that specific known authorizations from a specific known page are correctly extracted. They are NOT mock-the-mock tests; they exercise the actual BeautifulSoup → list-of-`Authorization` transformation against fixtures whose content is independently verifiable on the live portal. The unification tests verify behavior on hand-built input rows because the unification logic is pure data shuffling with no external dependencies. The fetcher-refactor tests are regression-guards: existing tests must continue to pass after the refactor.

**Implementation Details**

- Page sizes: empirical mean 47 KB across 42 ceased/low-volume captures; max 157 KB. Sample is biased low; active-high-volume principals may be 2-3× larger. Pre-flight Step 6 samples one to bound the upward end before kicking off the full run.
- Wall time: ~17 min at delay=1.0 for 944 principals (parallel to the lobbyist scrape's 14 min for 774). Data volume in checkpoints: ~43 MB at mean, ~140 MB at the 3× upper bound.
- Reuse strategy: refactor recommended (extract generic `entity_fetcher.py` core); fallback to duplicate-as-sibling if Dan wants the lobbyist code path frozen.
- The principal-side scrape will surface ANY soft-404s on principal pages (the prior session only saw lobbyist-side soft-404s; we don't know if the principal endpoint has the same failure mode). Use the same body-marker detection (`"Page Not Found"` in body). All principal soft-404s should be logged to the results doc.
- Privacy-redacted principals (2 known: 11530, 13137): the parser must handle pages where the principal-info section is suppressed but the authorized-lobbyists section is populated. The principal page heading text "Authorized Lobbyists" is what the parser keys on, not the principal name.
- Output is consumer-ready TSV in the same shape as the lobbyist-side table, plus the unified table with provenance. Suhan / Dan may want a different downstream consumer shape; the unification module is the right place to extend if so.
- Checkpoint files are written even for soft-404s and HTTP 404s (per the existing fetcher's contract — `html: null` + `status_code: 404`). The materialize step needs to skip null-HTML payloads, not crash on them.

**What could change**

- If `lobbying@wi.gov` replies with a CSV that contains the full authorization table (and includes lobbyist IDs not in either of our roster sources), the unification step changes shape — it would be a 3-way merge across `{ethics-CSV, lobbyist-side, principal-side}`. Plan can be extended; reuse the unification module.
- If active-high-volume principal pages turn out to be much larger than the 157 KB upper bound from the gap-investigation sample (Pre-flight Step 6), data volume estimates go up but wall time stays bounded by the 1.0 s polite delay. Plan doesn't change architecturally.
- If the scrape surfaces zero Schlaak-class additions (i.e., the union exactly equals the grid-discovered set), the result is still load-bearing: it bounds the lobbyist-side completeness gap at "≤ what one Schlaak case represents," empirically demonstrates the grid is exhaustive in this session, and we get the principal-side authorization view as a cross-validation byproduct.
- If the scrape surfaces a large Schlaak-class population (say >20), there's a real question about whether the grid AJAX is filtering on a knowable predicate (license type? administrative state?) — that follow-up investigation belongs in the results doc, not the plan.
- If `License Type` in `WI_directory_lobbyists.xls` turns out to perfectly predict grid membership (e.g., "Single" → present, "Pro Bono" → absent), the directory filter rule is solved as a byproduct.

**Questions**

- **Refactor or duplicate the fetcher?** Plan recommends refactor (DRY). Lower-risk alternative is duplicate. Decision belongs to Dan, not the implementing agent.
- **Should the principal scrape wait on a `lobbying@wi.gov` reply?** If Dan has emailed and is waiting, executing this plan first is wasted work if the CSV arrives. If the email hasn't gone out, the plan is unblocked.
- **What's the output shape Suhan / Dan want?** The plan produces three TSVs (lobbyist-side existing, principal-side new, unified new). A different shape (e.g., one TSV with provenance columns and no separate per-side files) is fine — the unification module is the right place to extend.
- **Should we fetch the State Agency Liaisons table while we're at the portal?** Still held over from the prior session. One extra `curl` and adds the third entity table for free. Probably worth grabbing — independent of this plan, but plan-adjacent if the implementing agent has cycles.
- **What discovery-completeness check do we want for principal IDs?** The plan currently uses `{dir .xls} ∪ {auth graph}`. A more aggressive check would enumerate principal IDs in the 10000-13500 range and see if any "Schlaak-class principals" exist (principals reachable by direct URL but absent from both sources). That's ~3500 extra requests, ~1 hr wall. Probably not worth it for this plan, but worth flagging.

---

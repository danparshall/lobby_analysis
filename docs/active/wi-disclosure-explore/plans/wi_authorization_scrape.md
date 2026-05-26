# WI Lobbyist–Principal Authorization Scrape Implementation Plan

**Goal:** Build the complete lobbyist↔principal authorization join table for the WI 2025-2026 session by scraping per-lobbyist detail pages from `lobbying.wi.gov`, producing a TSV that joins cleanly with the two `.xls` directory exports already in `data/disclosures/WI/`.

**Originating conversation:** [`convos/20260526_wi_data_ingest_and_join_key_investigation.md`](../convos/20260526_wi_data_ingest_and_join_key_investigation.md)

**Context:** Dan dropped two WI Ethics Commission `.xls` exports (`WI_directory_lobbyists.xls` for 776 lobbyists, `WI_directory_principals.xls` for ~905 principals) into the data store. They don't carry a foreign-key relationship to each other — the lobbyist table references an employer by *Organization Name* (string), not by *Principal ID*. Portal investigation in the originating convo found that the authorization relationship IS publicly visible — but only embedded in per-entity HTML detail pages, not as a bulk export. The cheapest source side is the lobbyist detail page (34 KB each × 776 ≈ 26 MB total), where each page has a `Principals Represented` section with stable `/Who/PrincipalInformation/.../Information/{principal_id}` hrefs.

**Confidence:** Exploratory — the structural finding (where the data is reachable) is firm, but the scrape itself hasn't been validated at scale. The single spot-check (lobbyist 11042 → 9 principals) demonstrates the DOM shape is parseable; nothing yet confirms (a) the DOM is identical for all 776 lobbyists, (b) `lobbying.wi.gov` will tolerate 776 sequential requests, or (c) the "Principals Represented" section captures withdrawn authorizations in addition to active ones.

**Architecture:** Three pure-Python modules behind a thin CLI:
1. **`fetch_lobbyist_page(lobbyist_id, session) → str`** — polite HTTP GET with browser UA, session-cookie reuse, ≥1 s sleep between requests, retry on 5xx.
2. **`parse_lobbyist_authorizations(html, lobbyist_id) → list[Authorization]`** — extract every `(lobbyist_id, principal_id, authorized_on, withdrawn_on)` edge from the HTML.
3. **`build_join_table(checkpoint_dir) → pd.DataFrame`** — read all checkpoint files, materialize the bipartite edge table, write `WI_lobbyist_principal_authorizations.tsv`.

Checkpointing: one JSON file per lobbyist (`{lobbyist_id}.json`) holding the raw HTML plus parsed authorizations plus fetch timestamp. Resume = "if `{lobbyist_id}.json` exists, skip the fetch." This matches Dan's data-integrity rules (see CLAUDE.md "Experiment Data Integrity").

**Branch:** `wi-disclosure-explore` (already created this session at `/Users/dan/code/lobby_analysis/.worktrees/wi-disclosure-explore/`).

**Tech Stack:**
- `requests` — HTTP client. Already in many `lobby_analysis` deps via transitive; add to `[project]` if not already there.
- `beautifulsoup4` + `lxml` — HTML parsing. Need to add to `pyproject.toml`.
- `pandas` — table materialization and TSV write. Not currently a project dep; consider `--with` rather than adding (this code may move to a one-off script).
- `pytest` — test runner. Already in `[dev]`.

The `uv add` calls go in Step 1 — ask Dan before installing new project deps if unsure.

---

## Pre-flight Checks (5 min)

These ensure the next agent isn't starting from a broken assumption.

1. **Verify you're in the right worktree.** `pwd` should show `.worktrees/wi-disclosure-explore`; `git branch --show-current` should be `wi-disclosure-explore`. If not, `cd /Users/dan/code/lobby_analysis/.worktrees/wi-disclosure-explore` first.
2. **Verify the data files moved this session are still in place.** `ls /Users/dan/data/lobby_analysis/disclosures/WI/` should show `WI_directory_lobbyists.xls` (242 KB) and `WI_directory_principals.xls` (692 KB).
3. **Verify the `data/` symlink resolves.** `ls data/disclosures/WI/` from the worktree root should produce the same files.
4. **Verify portal is up.** `curl -sS -o /dev/null -w 'HTTP %{http_code}\n' -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15' https://lobbying.wi.gov/Home/Welcome` should be 200. If not, stop and surface to user.
5. **Pull the canonical spot-check fixture.** `curl -sS -A '<browser UA>' 'https://lobbying.wi.gov/Who/LobbyistInformation/2025REG/Information/11042?tab=Profile' -o tests/fixtures/wi/lobbyist_11042.html`. We'll use this as the parser unit-test fixture. ~34 KB. The originating convo verified this lobbyist has 9 principals represented.

If any check fails, stop and report — do not work around silently.

---

## Testing Plan

The scrape itself is a data-collection task and is exempt from TDD per the write-a-plan skill (analysis/exploration exception). **The parser is not** — `parse_lobbyist_authorizations(html, lobbyist_id)` is pure-function, deterministic, and the spec for what counts as a successful scrape lives entirely in it. So:

- **Parser unit tests (TDD):** I will add behavior tests against a real `lobbying.wi.gov` lobbyist page snapshot (`tests/fixtures/wi/lobbyist_11042.html`) that verify:
  - The parser extracts 9 `Authorization` records from lobbyist 11042's page (the spot-check count from the convo).
  - Each record has a non-None `principal_id` (integer) and `authorized_on` (date).
  - The 9 `principal_id` values match the convo's observed set: `{10937, 11004, 11102, 11110, 11158, 11300, 11590, 11678, 13214}`.
  - A page with zero "Principals Represented" entries returns `[]` cleanly (not an exception). To force this, write a minimal fixture by hand or find a lobbyist with no authorizations.
  - A page whose HTML structure changes (e.g., the `Principals Represented` heading text is altered) raises `ParseError`, not silently returns `[]` — this is the "noisy fail" property.
- **Fetcher unit tests:** mocked. Verify the polite-sleep is at least 1.0 s, the UA header is set to a browser string, 5xx triggers retry with exponential backoff up to 3 attempts, 404 is logged but doesn't raise (some lobbyist IDs may not have detail pages).
- **Resume-logic unit tests:** verify `fetch_or_load(lobbyist_id, checkpoint_dir)` reads from disk if `{lobbyist_id}.json` exists, calls `fetch_lobbyist_page` only otherwise. Mock the fetcher.
- **Materialize unit test:** given a checkpoint dir with 3 hand-built JSON files containing fixture data, verify `build_join_table` produces the expected DataFrame shape and content.

I will NOT test integration against the live portal in pytest — that requires network, slows down test runs, and isn't the job of unit tests. Instead, after the test suite passes, run the actual scrape (Step 4) on a small subset (10 lobbyists) and visually check the output before proceeding to the full 776.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Implementation Steps

### Step 1 — Add HTML parsing deps to `pyproject.toml` (5 min)

Ask Dan first whether to add `beautifulsoup4` + `lxml` as project deps or use `uv run --with` (the latter keeps `pyproject.toml` untouched but means each run rebuilds the env). For a 776-page scrape that may run several times during dev, project-dep is probably cleaner.

If approved: `uv add beautifulsoup4 lxml`. Commit as `deps: add beautifulsoup4 + lxml for WI authorization scrape`.

### Step 2 — Create test fixture (5 min)

Fetch lobbyist 11042's page (Pre-flight Step 5) and commit it to `tests/fixtures/wi/lobbyist_11042.html`. ~34 KB committed; this is fine for git. Add `tests/fixtures/wi/.gitkeep` if the dir is new.

### Step 3 — Write parser tests (RED phase) (15 min)

Create `tests/test_wi_authorization_parser.py`. Write the 4 parser tests in the Testing Plan section above. Run `uv run pytest tests/test_wi_authorization_parser.py` and verify all 4 fail with `ImportError` or `NameError` (the module doesn't exist yet). Do NOT proceed until you've seen them fail.

### Step 4 — Implement parser (GREEN phase) (20 min)

Create `src/lobby_analysis/io/wi/authorization_parser.py` with:
- `@dataclass(frozen=True) class Authorization` — fields: `lobbyist_id: int`, `principal_id: int`, `authorized_on: date`, `withdrawn_on: date | None`.
- `class ParseError(ValueError)` — raised when DOM structure doesn't match expectations.
- `def parse_lobbyist_authorizations(html: str, lobbyist_id: int) -> list[Authorization]`.

Inspect `tests/fixtures/wi/lobbyist_11042.html` to find the `Principals Represented` section's HTML structure (BeautifulSoup, look for the section heading text, then iterate sibling/child links matching `/Who/PrincipalInformation/2025REG/Information/{id}`). Authorization date is on the same row as the principal link, labeled `Authorized On`.

Run tests: all 4 should now pass.

Commit as `wi-scrape: authorization parser + lobbyist 11042 fixture`.

### Step 5 — Write fetcher + resume-logic tests (RED) (10 min)

`tests/test_wi_authorization_fetcher.py`:
- `test_fetcher_sets_browser_ua`
- `test_fetcher_polite_sleep_at_least_one_second`
- `test_fetcher_retries_on_5xx_up_to_three_times`
- `test_fetcher_logs_but_does_not_raise_on_404`
- `test_fetch_or_load_skips_fetch_if_checkpoint_exists`

Use `requests_mock` (or `responses` if Dan prefers — check what's already in dev deps).

### Step 6 — Implement fetcher + resume (GREEN) (20 min)

`src/lobby_analysis/io/wi/authorization_fetcher.py`:
- `def fetch_lobbyist_page(lobbyist_id: int, session: requests.Session) -> str`
- `def fetch_or_load(lobbyist_id: int, checkpoint_dir: Path, session: requests.Session) -> dict` — returns `{"html": str, "authorizations": list[dict], "fetched_at": str}`, writing the checkpoint file as a side effect.

Tests pass. Commit as `wi-scrape: polite fetcher with checkpoint/resume`.

### Step 7 — Write materialize test (RED) → implement (GREEN) (15 min)

`tests/test_wi_authorization_materialize.py` — one test that given a hand-built temp checkpoint dir with 3 JSON files, `build_join_table(checkpoint_dir)` returns a DataFrame with the expected row count and the expected schema (`lobbyist_id`, `principal_id`, `authorized_on`, `withdrawn_on`).

`src/lobby_analysis/io/wi/authorization_materialize.py` — implement. Commit as `wi-scrape: materialize join table from checkpoints`.

### Step 8 — Build the CLI / runner (15 min)

`src/lobby_analysis/io/wi/scrape_authorizations.py` (or `scripts/wi_scrape_authorizations.py` if Dan prefers scripts-not-src for one-offs):

```
usage: uv run python -m lobby_analysis.io.wi.scrape_authorizations [--limit N] [--checkpoint-dir DIR]
```

- Loads `WI_directory_lobbyists.xls`, extracts the lobbyist ID column. NOTE: the .xls doesn't have an explicit Lobbyist ID column in the export Dan moved this session — the per-lobbyist detail page URLs use a numeric ID that isn't in the spreadsheet. **This is a known unknown for this plan.** First-pass mitigation: discover lobbyist IDs by scraping `/Who/Lobbyists/2025REG/SearchNames` for the linked detail-page URLs, then iterate from there. Surface to Dan if this changes the plan shape.
- For each lobbyist ID, call `fetch_or_load`.
- Default checkpoint dir: `/Users/dan/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints/`.
- `--limit N` for the small-batch sanity check.
- Default delay 1.0 s; configurable via `--delay`.

### Step 9 — Sanity-check scrape (10 lobbyists) (5 min wall, 10 min observation)

Run with `--limit 10`. Eyeball the checkpoint JSONs. Verify:
- All 10 files exist
- Each has non-empty `authorizations`
- Principal IDs in each match what you'd expect by spot-checking 2–3 lobbyists in a browser

If anything looks off, stop and surface. Don't proceed to the full run on bad data.

### Step 10 — Full scrape (13 min wall) (background)

Remove `--limit`. Run the full 776 scrape. Background with `run_in_background=true` if your harness supports it; otherwise live tail.

If using `/loop`: structure the script as "fetch one lobbyist, write checkpoint, exit." Then `/loop 2s wi-scrape-once` will hit the rate limit comfortably and the loop handles restart-on-crash. Probably overkill for 13 min wall, but Dan flagged it as an option.

### Step 11 — Materialize + spot-check (10 min)

Run `build_join_table` against the full checkpoint dir. Write `/Users/dan/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv`.

Spot-checks:
- Row count: each (lobbyist, principal) authorization is one row. Expected ≈ 776 × 2-3 avg = ~1,500–2,500 rows. Sanity-check against the principal page for 11158 (3 lobbyists shown in the convo): the materialized table should contain exactly 3 rows where `principal_id=11158`.
- Lobbyist 11042 should appear in 9 rows (one per principal represented).
- Spot-check 5 random rows by visiting the corresponding portal URL.

### Step 12 — Add results doc + finish-convo (10 min)

`docs/active/wi-disclosure-explore/results/20260527_wi_authorization_scrape_results.md` (or whatever date the implementing agent runs this) with:
- Provenance header
- Row count, lobbyist count, principal count, distinct authorization-date count
- Top-10 most-represented principals (highest `count(lobbyist_id)` per principal — proxy for influence concentration)
- Top-10 most-active lobbyists (highest `count(principal_id)` per lobbyist)
- Any anomalies (lobbyists with no principals, principals with no lobbyists, dates outside the session window)

Then run finish-convo to push.

---

**Testing Details**

The parser tests test behavior (extracted records match a known ground truth from a real portal page snapshot) — not types, not mocks. The fetcher tests cover the polite-behavior contract (UA, sleep, retry, 404-tolerance) since that's the part that talks to the live portal; they use `requests_mock` because hitting the real portal in pytest would be slow and flaky. The resume-logic test verifies the actual filesystem behavior (does a real file on disk cause the fetcher to be skipped?) by using a `tmp_path` fixture. None of the tests check that "the mock was called" — they check that the right output was produced for the right input.

**Implementation Details**

- Pages return ~34 KB each; 776 pages × 34 KB = ~26 MB total HTML. Checkpoint dir will be ~50 MB after JSON wrapping. Goes in `disclosures/WI/_authorization_scrape_checkpoints/` (data store, gitignored).
- `Authorized On` dates may be stored as `M/D/YYYY` strings in the HTML; convert to `date` in the parser.
- `Withdrawn` status — if a lobbyist's representation of a principal was withdrawn during the session, the row likely shows a `Withdrawn` date. Confirm by inspecting fixture; if present, capture in `Authorization.withdrawn_on`. If not present in the lobbyist-side view (the convo verified withdrawal status is on principal pages), this becomes a known-incomplete: cross-validate against the principal-side scrape later.
- `requests.Session` for connection pooling and cookie persistence (one warmup GET to `/Home/Welcome` at the top of the run to seed cookies, then session-cookied request to each detail page).
- Browser UA: `Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15` (verified working in the originating convo's `curl` probes).
- No `robots.txt` was checked this session — please check before the full run. If it forbids `/Who/LobbyistInformation/`, stop and surface to Dan rather than scraping anyway.

**What could change:**

- If Dan emails `ETHLobbying@wi.gov` and they provide a CSV directly, this whole plan becomes moot. Check with Dan before starting work — if an email went out, give it a week for a reply before scraping.
- If the portal blocks the scraper (rate-limit, IP block, captcha), the plan needs to switch to Playwright with browser-realistic delays. Adds complexity but doesn't change the architecture.
- If the lobbyist directory exports include withdrawn lobbyists, the 776 number is wrong — it's actually the 714 active lobbyists we need to scrape (62 had surrender dates). Worth checking before kicking off.
- The `Principal ID` ↔ `Principal Name` mapping in the principals file is presumed stable through the scrape. If the WI Ethics Commission re-runs the principal directory export between this scrape's start and finish, IDs *should* still be stable (this is a 2025-2026 session-bound export) but verify by re-pulling the principals file at scrape end and diffing.

**Questions**

- **Should we email `ETHLobbying@wi.gov` first?** Cost = one email; benefit = possibly skip the entire scrape if they share the SSRS-internal authorizations table. Decision belongs to Dan, not the implementing agent.
- **Add `beautifulsoup4`+`lxml` to project deps, or keep them ephemeral via `uv run --with`?** If this code lives long-term in `src/lobby_analysis/io/wi/`, add to deps. If it's a one-off script in `scripts/`, ephemeral is fine.
- **Where do the new modules live — `src/lobby_analysis/io/wi/` or `scripts/`?** `src/io/wi/` is the cleaner home (parallel to whatever `nc-disclosure-explore` lands), but adds the obligation to maintain it. `scripts/` is fine for one-shot data ingest.
- **Capture withdrawn authorizations?** Whether the lobbyist-side page exposes withdrawal dates is unconfirmed (the convo only verified it for the principal-side view). If not, the table is incomplete-by-design — flag in results doc and consider a follow-up plan to also scrape principal pages.
- **State agency liaisons** — pull `/Who/StateAgencies/.../ReportExport?outRpt=Excel` while you're at the portal, or leave as separate work? Probably worth grabbing — it's one extra `curl` and adds the third entity table for free.

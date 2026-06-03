# Michigan Lobbying Data Acquisition — Implementation Plan (chunked)

**Goal:** Acquire a structured Michigan lobbying-disclosure dataset (registrants, the
employer/"Employed By" graph, and expenditure filings) plus the MI lobbying statutes,
mirroring the Wisconsin data-grab where Michigan's data model allows.

**Originating conversation:** [`../convos/20260603_mi_data_grab_planning_and_kickoff.md`](../convos/20260603_mi_data_grab_planning_and_kickoff.md)

**Context:** WI shipped a 6-TSV MVP (`releases/wi/`) from a two-tier scrape of
`lobbying.wi.gov`. Dan wants "the same thing for MI." Recon shows the *shape* (entities →
employer edges → filings) transfers, but Michigan's regime is **expenditure-centric, not
bill-centric** — so the WI bill-effort table and the principal→lobbyist→bill→sponsor chain
have **no Michigan analog** and are out of scope. Analysis is deferred until data exists.

**Confidence:** Exploratory on *mechanics* (the MiTN/entellitrak portal has not been
probed yet — Phase 0 is a hard gate). High on *data model* (MI collects no bill-level
lobbying data — this is well-established about Michigan's Lobby Registration Act).

**Locked decisions (Dan, 2026-06-03):** (a1) entity + expenditure is the accepted MI MVP —
no chain. (a2) **Single 2025 vintage only** — drop the multi-vintage optionality below.
(a3) Proceed to Phase 0 recon immediately.

**Architecture:** Reuse the WI pattern — polite fetcher + immutable full-HTML/JSON
checkpoints + pure parsers + deterministic TSV materializers + committed HTML fixtures for
TDD — under a new `src/lobby_analysis/io/mi/` package. **But the acquisition primitive
(scrape vs. bulk download vs. per-filing export) is undetermined until Phase 0.** If MiTN
exposes a bulk/dataset export, most of the WI scraping machinery collapses into a
download + parse, and Phases 1–3 shrink dramatically.

**Branch:** `mi-disclosure-explore` (worktree at
`/Users/dan/code/lobby_analysis/.worktrees/mi-disclosure-explore`).

**Tech stack:** Python 3.12, `uv`, `httpx` (or `requests`) for fetch, `lxml`/`beautifulsoup4`
for HTML, `openpyxl`/`pandas` for any XLS/CSV exports, `pytest` + `ruff`. Mirror whatever
the WI `io/wi/` package already depends on.

---

## How to use this plan (chunking)

This is sized for `handle-large-tasks`: each **Phase** below is one subagent-sized chunk
with a clear input, output artifact, and test. **Phase 0 is a hard gate** — its findings
parameterize the `TBD(Phase 0)` markers in every later phase. Do **not** start Phases 1–4
in parallel before Phase 0 resolves the acquisition primitive; the implementation shape of
1–3 depends on the answer.

Data lands under the worktree-relative `data/` symlink (→ `~/data/lobby_analysis`).
Target dir for this state: **`data/disclosures/MI/`** and **`data/statutes/mi/<year>/`**.
Mirror the WI on-disk layout (checkpoints in `_*_checkpoints/` subdirs, gitignored;
output TSVs at the top level).

---

## Phase 0 — Portal reconnaissance (HARD GATE, no TDD; it's exploration)

**Input:** the two entry points found in recon:
- MiTN public lobby search: `https://mi-boe.entellitrak.com/etk-mi-boe-prod/page.request.do?page=page.miboeLobbyPublicSearch`
- Legacy NIC itemized-expenditure analysis: `https://miboecfr.nicusa.com/cgi-bin/cfr/lobby_exp_anls.cgi`
- SoS landing: `https://www.michigan.gov/sos/elections/disclosure/lobby` (note: blocks
  automated fetch — use a real browser / `webapp-testing` skill).

**Questions this phase MUST answer** (each becomes a `TBD(Phase 0)` resolution downstream):
1. **Bulk vs. per-filing export.** Does MiTN expose a whole-dataset export (all registrants
   / all filings as one CSV/XLS), or only per-filing PDFs/spreadsheets? Does the legacy NIC
   CGI offer a downloadable dataset? **This decides scrape vs. download.**
2. **Registrant ID discovery.** Is there a list endpoint (analog of WI's
   `ShowLobbyistList?pageSize=1000`)? What's the entellitrak request shape
   (`page.request.do` + AJAX? form POST? query params)? Capture an actual request/response.
3. **Detail-page URL template** for a lobbyist/agent and for an employer, with a real ID.
4. **The "Employed By" relationship** — where is it exposed (search facet result, detail
   page back-link)? Confirm it gives agent→employer edges with dates.
5. **Filing structure** — locate a real Financial Report Summary + its Itemized Expenditure
   schedule; record the fields actually present (total expenditure, period, itemized rows
   {date, purpose, recipient, amount, category}).
6. **2025 availability** — confirm the full 2025 filing year (both semi-annual periods,
   Jan 31 + Aug 31 deadlines) is present and retrievable in MiTN. (Vintage locked to 2025
   only per a2 — no multi-year retrieval.)
7. **Politeness / robots** — check `robots.txt`, rate limits, terms; set a conservative
   delay (WI used 1.0 s). Note any session/CSRF tokens entellitrak requires.
8. **Volume estimate** — rough count of registrants and filings → wall-time estimate.

**Output artifact:** `results/20260603_mi_portal_recon.md` documenting answers 1–8 with
captured request/response samples (save raw HTML/JSON samples under
`data/disclosures/MI/_recon_samples/`). **Plus a go/no-go recommendation on acquisition
primitive** (bulk download | per-filing export | full scrape).

**Test:** none (exploration). Done-criteria = all 8 questions answered with at least one
concrete captured artifact each, and a stated primitive choice.

---

## Phase 1 — Registrant entities (lobbyists / agents / employers)

> Shape depends on Phase 0. **If bulk export exists:** this phase is "download + parse the
> registrant export → TSV." **If scrape:** this phase mirrors WI Tier-1 discovery + fetch.

**Files (new), under `src/lobby_analysis/io/mi/`:**
- `registrant_id_discovery.py` — `TBD(Phase 0)`: list endpoint or export parse → IDs.
- `entity_fetcher.py` — polite fetcher + JSON checkpoint layer (port `io/wi/entity_fetcher.py`;
  it's already the generic version). Stores full response bytes in checkpoint JSON.
- `registrant_parser.py` — pure function: detail HTML / export row → `Person` / `Organization`
  (Popolo-style, matching `src/lobby_analysis/models/`). Lobbyist vs. agent vs. employer
  classification.
- `registrant_materialize.py` — deterministic TSV writer.
- `scrape_registrants.py` (or `load_registrants.py` if download) — CLI entry point.

**Output TSVs** (under `data/disclosures/MI/`):
- `MI_lobbyists.tsv` and/or `MI_agents.tsv` — person entities (columns mirror
  `WI_lobbyists.tsv`: `id`, `name`, `source_state`, `contact_details_json`, role).
- `MI_employers.tsv` — employer/principal-analog organization entities (mirror
  `WI_principals.tsv` columns where present).

**Testing plan:**
I will add unit tests for `registrant_parser.py` against **committed HTML/export fixtures**
(`tests/fixtures/mi/`) captured in Phase 0 — assert that a known registrant parses to the
expected name/role/contact-detail values (real values, not mocks). I will add a
materializer test asserting deterministic row order and idempotent re-write (running twice
yields byte-identical output). I will NOT test the fetcher's network behavior beyond a
checkpoint-hit/miss unit test against a temp dir.
NOTE: I will write *all* tests before I add any implementation behavior.

**Done-criteria:** `MI_lobbyists`/`MI_agents` + `MI_employers` TSVs materialize from
checkpoints with 0 parse failures; spot-check ≥3 registrants against the live portal.

---

## Phase 2 — Employer ("Employed By") relationship graph

> WI analog: the lobbyist↔principal authorization graph. MI analog: agent↔employer via the
> "Employed By" facet. **This is the structural backbone and ports conceptually.**

**Files (new):**
- `employment_parser.py` — detail HTML / export row → `(agent_id, employer_id,
  start/registration_date, end_date)` edges.
- `employment_materialize.py` — TSV writer with provenance (`discovered_via` if both an
  agent-side and employer-side view exist, mirroring WI's unified-edge pattern).
- extend the Phase-1 CLI or add `scrape_employment.py`.

**Output TSV:** `MI_agent_employer_relationships.tsv` — columns:
`agent_id`, `employer_id`, `registered_on`, `terminated_on`, `discovered_via`
(mirror `WI_lobbyist_principal_authorizations_unified.tsv` semantics).

**Edge cases to handle:**
- An agent employed by multiple employers (multiple edges).
- Employer that is itself a registrant vs. employer-only entity (reconcile IDs with Phase 1).
- Terminated/withdrawn relationships — keep them with an end date, don't drop (WI kept
  `withdrawn_on`).
- ID-space reconciliation: does MI use one ID space for all registrants, or separate spaces
  for agents vs. employers? `TBD(Phase 0)`.

**Testing plan:**
Unit tests for `employment_parser.py` on committed fixtures: a known agent with ≥2 employers
parses to the right edge set with dates. Materializer determinism/idempotency test. A
reconciliation test asserting every `agent_id`/`employer_id` in the edge file appears in the
Phase-1 entity TSVs (referential integrity), allowing a documented exception list for
redacted/ceased entities (WI had a 40-principal gap class — expect an MI analog).
NOTE: I will write *all* tests before I add any implementation behavior.

**Done-criteria:** edge TSV materializes; referential integrity holds modulo a documented
exception list; spot-check ≥3 agents' employer sets against the portal.

---

## Phase 3 — Expenditure filings (Financial Report Summary + Itemized schedule)

> WI analog: `WI_principal_filings.tsv` + `WI_lobbyist_filings.tsv`. **MI has NO bill-effort
> analog** — do not build a `bill_efforts` table. Instead MI has an **itemized-expenditure**
> table keyed to public-official recipients, which WI did *not* have. Model it on its own terms.

**Files (new):**
- `filing_parser.py` — detail HTML / export → (a) summary record per registrant per
  semester (total expenditure, period, hours if present), and (b) itemized-expenditure rows.
- `filing_materialize.py` — writes both tables.
- CLI entry / extend orchestrator.

**Output TSVs:**
- `MI_filings.tsv` — one row per (registrant, reporting period). Columns (mirror WI filing
  schema where shared): `filing_id`, `registrant_id`, `state`, `filing_type`
  (= `financial_report_summary`), `filer_role`, `reporting_period_start`,
  `reporting_period_end`, `total_expenditure`, `source_url`. Period = semi-annual
  (Jan 31 / Aug 31 deadlines → H1/H2).
- `MI_itemized_expenditures.tsv` — **new table with no WI analog.** One row per itemized
  expenditure > $100. Columns (confirm against Phase 0): `filing_id`, `registrant_id`,
  `category` ∈ {financial_transaction, travel_lodging, food_beverage}, `expenditure_date`,
  `amount`, `purpose`, `recipient_name`, `recipient_address`, `official_benefitted`,
  `ytd_amount`.

**Edge cases:**
- Semi-annual, not quarterly (WI lobbyists were quarterly) — period modeling differs.
- Zero/exempt filers (WI had low-spend-exempt principals filing $0 in one period). Expect MI
  analog; preserve, don't synthesize.
- Threshold-gated itemization: only expenditures over statutory thresholds appear itemized;
  a registrant can have a positive `total_expenditure` with zero itemized rows. That's valid.
- Amount parsing: currency strings → cents-safe decimals (WI used exact `$911,593.49` match
  in spot-checks; do the same).

**Testing plan:**
Unit tests for `filing_parser.py` on committed fixtures: a known registrant's summary parses
to the exact total expenditure (real value spot-checked against the portal), and its itemized
rows parse to the right count + a known row's {date, amount, recipient}. Materializer
determinism/idempotency tests. A referential-integrity test: every `registrant_id` in the
filing tables exists in Phase-1 entities.
NOTE: I will write *all* tests before I add any implementation behavior.

**Done-criteria:** both TSVs materialize with 0 parse failures; ≥3 registrants'
totals match the portal exactly; itemized-row counts match for ≥2 registrants.

---

## Phase 4 — Statute retrieval (independent; can run any time)

> WI analog: `data/statutes/wi/<year>/` via the `statute-retrieval` harness (Justia source,
> manifest.json + per-section .txt with sha256). MI's lobbying law = **Michigan Lobby
> Registration Act, Act 472 of 1978** (MCL 4.411–4.430).

**Steps:**
1. Reuse the existing statute-retrieval harness (see `docs/historical/statute-retrieval/`
   and `src/` statute code). Identify MI sections: MCL §4.411 through §4.430 (the Lobby
   Registration Act). Source: Michigan Legislature (`legislature.mi.gov`) and/or Justia
   (`law.justia.com/codes/michigan/`). Prefer the same source WI used (Justia) for
   consistency; cross-check against the official legislature site.
2. Configure the harness with the section URL list; run the retriever.
3. Output: `data/statutes/mi/2025/manifest.json` (URLs, sha256, retrieved_at, role labels)
   + `data/statutes/mi/2025/sections/*.txt`.
4. ~~Optional multi-vintage~~ — **dropped per a2. 2025 vintage only.**

**Test:** manifest validates (every section has url + sha256 + non-empty local file);
section count matches the configured list; no hallucinated/empty sections. (This mirrors the
WI statute manifest contract — provenance integrity, not behavioral TDD.)

**Done-criteria:** manifest + section .txt files present for at least the 2025 vintage,
sha256-verified.

---

## Phase 5 (optional, post-data) — Release packaging

Mirror `releases/wi/`: a `releases/mi/` dir with the TSVs + a `README.md` documenting
source (MiTN/entellitrak), coverage, pipeline, generating commit, reproducer command,
headline aggregates, and **caveats** — including, prominently, the **no-bill-attribution**
limitation so downstream users don't expect a WI-style chain. **No `chain/` subdir** (no
bill data to chain). Only do this once Dan signs off that entity+expenditure is the accepted
MI MVP.

---

**Testing Details:** Each code phase (1–3) is test-first against **committed real HTML/export
fixtures** captured in Phase 0 — parsers are asserted to produce exact real values (names,
amounts, edge sets), not mock returns. Materializers are tested for deterministic ordering
and idempotent re-write. Referential integrity is tested across phases (edges/filings
reference real entities). Phases 0 and 4 are provenance/exploration, not TDD. No tests for
datastructures/types; all tests exercise behavior on real data.

**Implementation Details:**
- New package `src/lobby_analysis/io/mi/` mirroring `io/wi/` structure.
- Immutable full-response JSON checkpoints; parsers re-run from checkpoints, never re-fetch.
- Polite fetcher, conservative delay (≥1.0 s), browser UA; honor entellitrak session/CSRF
  tokens if Phase 0 finds them.
- Deterministic TSV sort; omit volatile `extracted_at` for idempotency (WI convention).
- Reuse `src/lobby_analysis/models/` Pydantic entities (Person/Organization/contact details).
- Add a new model only for `MI_itemized_expenditures` (no WI equivalent).
- `data/disclosures/MI/` for outputs; `_*_checkpoints/` gitignored.

**What could change (provisional):**
- **The single biggest unknown is Phase 0's acquisition-primitive answer.** If MiTN/NIC offers
  a bulk export, Phases 1–3 collapse into download-and-parse and the fetcher/checkpoint/ID-
  discovery machinery is largely unneeded. The plan is written scrape-shaped to be safe; bias
  toward the cheapest primitive Phase 0 permits.
- Exact column sets in Phases 1–3 are `TBD(Phase 0)` against real MI filings.
- Vintage strategy (single 2025 snapshot vs. multi-year) pending Dan + migration depth.

**Questions (for Dan, before/at execution):**
1. Is an **entity + expenditure** dataset (no bill chain) an acceptable MI MVP? (My read: yes,
   and worth being explicit that MI's regime simply doesn't support the chain.)
2. Single 2025 snapshot, or multi-vintage like WI?
3. Should we cross-check against The Accountability Project's MI dataset (~2023) as a
   historical sanity check?
4. Statute source: match WI (Justia) or prefer the official `legislature.mi.gov`?

---

# NY `parties_lobbied` disclosed-lawmaker edge — MVP Implementation Plan

**Goal:** Ingest NY's disclosed `parties_lobbied` field and ship a `releases/ny/NY_filing_parties_lobbied.tsv` edge that resolves the ~83% of values naming an individual legislator to an Open States `ocd-person` id, flagging the ~17% non-individuals as unresolved (raw preserved).

**Originating conversation:** [`convos/20260605_ny_v1_1_amp_decode_and_parties_recon.md`](../convos/20260605_ny_v1_1_amp_decode_and_parties_recon.md) (+ its 2026-06-06 addendum)

**Context:** The current chain's lawmaker edge is the bill *primary sponsor*, **inferred** via Open States — not a disclosed contact. `parties_lobbied` is the genuinely **disclosed** "who was lobbied" field (populated on 99.9% of 2025 rows). Reconnaissance ([`results/20260605_ny_parties_lobbied_recon.md`](../results/20260605_ny_parties_lobbied_recon.md)) showed ~83% are named legislators (resolvable), ~17% are executive offices / agencies / committee-staff / "entire-legislature" broadcasts (no `ocd-person`).

**Confidence:** Medium. The field shape is well-characterized from a representative whole-year `GROUP BY`. The two genuine unknowns are (1) the *grain* of `parties_lobbied` within a filing and (2) the name-format reconciliation between the disclosure text and the OS roster — both resolved in Phase 0 before any schema is frozen.

**Architecture:** A separate filing-grain extraction (parallel to the existing bill-link extraction — same raw CSV, different explosion), a free-text → `ocd-person` resolver reusing the OS sponsorship roster, and a new release TSV. The edge is **unweighted** (a contact edge, not a dollar allocation) — no conservation invariant, just a resolution-coverage metric. Chain integration is a stretch goal, not MVP.

**Branch:** `ny-disclosure-explore` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/ny-disclosure-explore`)

**Tech Stack:** Python 3.12, pandas, pydantic, pytest, ruff. SODA/Socrata pull via `io/ny/acquire.download_resource_csv`. Open States NY 2025-2026 CSV bundle (gitignored at `data/bills/NY/2025/`).

---

## MVP scope (explicit)

Resolve the **named legislators** (~83%). For the **~17% non-individual** rows, keep the raw string + a single `resolved=False` flag — do **not** build the typed `target_kind ∈ {executive, agency, committee_staff, chamber_broadcast}` taxonomy (post-MVP, per Dan 2026-06-05). All rows preserved, none dropped, so the taxonomy can be added later without a re-pull. **Do not overclaim to policymakers:** "disclosed contact" — and only where `resolved=True` is it a specific named legislator.

---

## Phase 0 — probe the grain + name formats (GATING, no schema yet)

Two facts gate the table design; resolve them against real data before writing any parser.

- **Step 0.1** — Extend `scripts/ny_probe_parties_lobbied.py` (or a sibling) to pull a bounded sample with `form_submission_id`, `reporting_period`, `focus_identifying_number`, `type_of_lobbying_focus`, **and** `parties_lobbied` for a handful of *specific* `form_submission_id`s (use `$where form_submission_id IN (...)` on the worst-case multi-row filings). Save raw under `results/`.
- **Step 0.2** — Determine: **does `parties_lobbied` vary within one `form_submission_id`+firm+client filing?** And **does it correlate with `focus_identifying_number`** (i.e. is the party reported *per bill/focus*, or once for the whole filing)?
  - If **per-filing** (constant across the filing's rows): the edge is `filing → {parties}`. Simplest; this is the MVP assumption.
  - If **per-focus** (varies with the bill): the edge *could* be `(filing, bill) → party`, but **MVP still collapses to `filing → {parties}`** (dedup per filing); the per-bill association is a post-MVP refinement.
- **Step 0.3** — Inspect the OS sponsorship **name format**. `git -C` not needed — read a few rows of `data/bills/NY/2025/NY_2025-2026_bill_sponsorships.csv`: confirm whether `name` is `"Amy Paulin"` vs `"Paulin, Amy"` vs `"Amy R. Paulin"`, and that `person_id` (`ocd-person/...`) is populated for individuals. The disclosure text is `"Assembly member Amy R. Paulin"` (title + First [Middle] Last). The resolver must bridge whatever gap Phase 0 reveals.
- **Step 0.4** — Write `results/YYYYMMDD_ny_parties_lobbied_grain.md` recording both verdicts. **Everything below is provisional on this doc.**

**This is a pure-analysis step — no TDD.** Surprising result = `parties_lobbied` varies per row in a way that doesn't dedup cleanly to a small per-filing set, or the OS name format can't be reconciled without fuzzy matching (which would expand MVP scope — stop and surface to Dan).

---

## Phase 1 — re-pull `client_semiannual` 2025 with `parties_lobbied`

- **Step 1.1** — In `scripts/ny_pull_2025.py`, add `"parties_lobbied"` to the `COLS` list (the `$select`). No other change.
- **Step 1.2** — Run `uv run --active python scripts/ny_pull_2025.py`. This overwrites `data/raw/ny/2025/client_semiannual.csv` (gitignored). Expect a larger file than the current ~1.9 GB (free-text column added) and a multi-minute streamed pull. The script already verifies the row count against the live `count(*)`.
- **Step 1.3** — Spot-check: `head` the new CSV, confirm the `parties_lobbied` column header is present with field-name (not display-name) headers.

**No TDD** (acquisition is a one-line `$select` change to an already-tested fetcher; `io/ny/acquire` has its own suite).

---

## Phase 2 — extract + resolve (TDD)

The party edge is a *separate explosion* of the raw rows from the bill-link edge, so it gets its own extraction function rather than riding the bill-grain collapse.

**Testing Plan**

I will write unit tests (in a new `tests/test_ny_parties_lobbied.py`) for the resolver's *behavior* against a small hand-built OS roster fixture (`{"ocd-person/aaa": "Amy R. Paulin", ...}`) and the real free-text examples from the recon doc:
- `"Assembly member Amy R. Paulin"` → `resolved=True`, `person_id="ocd-person/aaa"`.
- `"Assembly member Karl A. Brabenec, staff member"` → `resolved=True` (the `, staff member` suffix is stripped, still the legislator).
- `"Senator Shelley B. Mayer, staff member"` → `resolved=True`.
- `"Executive Chamber/Office of the Governor"` → `resolved=False`, `person_id=""`, raw preserved.
- `"A communication sent to entire NYS Legislature"` → `resolved=False`.
- `"Department of Education (NYSED)"` → `resolved=False`.
- An entity-bearing edge case (`"Senator … &amp; …"` if any) → decoded via the existing `html.unescape` path (reuse `_clean_name`, do not re-implement).

I will write an extraction test that, given a small set of raw rows sharing one `FILING_KEY` with differing `parties_lobbied`, yields one deduped party row per distinct resolved party for that filing (grain per Phase 0).

I will write a materializer test (mirroring `test_ny_materialize.py`) asserting: the TSV has one row per (filing, distinct party); the `resolved` flag round-trips; byte-identical re-run; empty input → header-only; no party dropped.

NOTE: I will write *all* tests before I add any implementation behavior.

- **Step 2.1** — Write the failing resolver tests above.
- **Step 2.2** — Run them; confirm RED (`ModuleNotFoundError` / missing function).
- **Step 2.3** — Implement in `io/ny/parse.py` (or a new `io/ny/parties.py` if it keeps `parse.py` focused — decide during impl, DRY):
  - `build_legislator_roster(csv_dir) -> dict[normalized_name, ocd_person_id]` — read `NY_*_bill_sponsorships.csv` (ALL rows, not just `classification=='primary'`, to capture the full roster), keep rows with a non-empty `person_id`, key by a normalized name. Reuse the chamber/file-glob discipline from `chain._os_sponsorships_csv` (shortest-match). (Consider relocating that helper so both call sites share it.)
  - `resolve_party_lobbied(raw, roster) -> (name, person_id|None, resolved: bool)` — `html.unescape` + `_clean_name`; strip a leading legislator title (`Senator`, `Assembly member`, `Assemblyman`, `Assemblywoman`, `Governor`, `Lieutenant Governor`, `Comptroller`, `Attorney General`, …); strip a trailing `, staff member` and parentheticals (`(effective …)`, `(NYSED)`); normalize the residual `First [Middle] Last` the SAME way the roster is normalized; look up. Miss → `resolved=False`, raw name preserved.
  - `extract_filing_parties(df) -> DataFrame` — group the normalized raw frame by `FILING_KEY` (reuse `grain.FILING_KEY` — do **not** redefine it), collect distinct `parties_lobbied`, resolve each. One output row per (filing, distinct resolved party).
- **Step 2.4** — Run resolver + extraction tests; GREEN.
- **Step 2.5** — Write the failing materializer test; implement `materialize_parties_lobbied(...)` (mirror `io/ny/materialize.py` conventions: `csv.DictWriter`, `\t`, `\n`, `None→""`, deterministic sort, byte-identical re-run, returns a row-count dict). Columns: `reporting_year, reporting_period, filing_id, lobbyist_id, client_id, party_lobbied_raw, party_lobbied_name, party_lobbied_person_id, resolved`.
- **Step 2.6** — GREEN. `ruff check` + `ruff format` the touched files.
- **Step 2.7** — Commit.

---

## Phase 3 — wire the CLI + ship the release (TDD-light)

- **Step 3.1** — Add a `parties` step to `io/ny/materialize_cli.py` (or a sibling CLI) that runs `read_csv → normalize_columns → extract_filing_parties → materialize_parties_lobbied` over the re-pulled CSV + the OS roster, writing `releases/ny/NY_filing_parties_lobbied.tsv`. Mirror the existing CLI; no new behavior tests (the steps' suites cover it — same precedent as `materialize_cli`).
- **Step 3.2** — Run it. Record real aggregates: total party rows, distinct resolved `ocd-person` count (sanity: ≤ ~213 legislators), **resolution rate** (% rows `resolved=True` — expect ~83% per recon), and the top unresolved values (sanity that they're the offices/broadcasts, not mis-parsed legislators).
- **Step 3.3** — Write `results/YYYYMMDD_ny_parties_lobbied_release.md` (provenance header) with those aggregates.
- **Step 3.4** — Write `releases/ny/NY_filing_parties_lobbied.tsv` is **gitignored** under the `releases/ny/**/*.tsv` rule (2026-06-06 decision) — it is regenerated during dev, `git add -f` only at merge. Add a short section to `releases/ny/README.md` documenting the new table + the "disclosed vs inferred" distinction + the resolution-rate caveat.
- **Step 3.5** — Update `RESEARCH_LOG.md` + `STATUS.md`; commit; push (no merge).

---

## Stretch (NOT MVP) — chain integration

Once the table is proven, optionally surface the disclosed edge alongside the inferred sponsor edge in the chain (a `disclosed_party_person_id` column or a sibling chain). Defer until the standalone table's resolution rate is validated. The `target_kind` taxonomy for the ~17% is also post-MVP.

---

**Testing Details:** Tests assert resolver *behavior* on real free-text examples (title/suffix stripping, legislator match, non-individual → unresolved) against a small roster fixture — never mocks-of-mocks, never type-shape tests. Extraction tests assert the per-filing dedup grain on hand-built multi-row filings. Materializer tests assert the on-disk TSV shape + byte-identical re-runs (the project's determinism invariant). No conservation test — this edge carries no dollars.

**Implementation Details:**
- The party edge is **unweighted** — it does not split or carry compensation. Do not invent a dollar weight.
- Reuse `grain.FILING_KEY`, `parse._clean_name` (HTML-decode), and the OS file-glob shortest-match discipline — do not duplicate.
- Build the roster from **all** sponsorship rows (primary + cosponsor) to get the full legislator name set, but only the `name`+`person_id` pair is used (not the bill linkage).
- `parties_lobbied` is already canonically named — no `COLUMN_MAPS` entry needed; it only needs adding to the pull `$select` and being carried into the extraction frame.
- One output row per (filing, distinct resolved party); no party dropped; non-individuals kept with `resolved=False`.
- Resolution is exact-normalized-match only for MVP; fuzzy matching is explicitly out of scope (flag if Phase 0 shows it's needed).

**What could change:** If Phase 0 shows `parties_lobbied` is reliably **per-focus**, a richer `(filing, bill) → party` edge becomes possible (post-MVP). If the OS name format needs fuzzy matching to hit ~83%, MVP scope expands — stop and consult Dan. If the re-pull reveals `parties_lobbied` is itself a semicolon/comma-delimited multi-party field (a single cell naming several people), the extraction must split it first (same `;`-delimiter hazard as the coalition split — reuse the decode-before-split discipline).

**Questions:**
1. **Multi-party cells:** does one `parties_lobbied` cell ever list multiple people (delimiter)? Phase 0 must check; if yes, split before resolve (decode first, per the `&amp;` lesson).
2. **Roster completeness:** are all ~213 legislators present in the 2025-2026 sponsorship file's `person_id` set, or do some never sponsor anything (and so are missing from the roster)? If gaps exist, a lobbied-but-never-sponsored legislator would fail to resolve — may need a fuller OS people source. Phase 0 sanity-checks roster size.
3. **Chamber disambiguation:** could two legislators share a normalized name across chambers? If so, the title prefix (`Senator` vs `Assembly member`) is the disambiguator and must be retained through normalization.

---

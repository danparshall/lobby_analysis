# Research Log: oh-portal-extraction

Created: 2026-04-30
Owner: Amina Rakhimbergenova
Track: B (portal scraping → `LobbyingFiling`)
Test state: Ohio

## Purpose

Extract actual lobbying disclosures from the Ohio state portal into the `LobbyingFiling` model (`src/lobby_analysis/models/filings.py`). Ohio is the team-wide test state for shaking out the end-to-end pipeline before broadening to other priority states.

This is the data-acquisition counterpart to Dan's Track A work (`statute-retrieval` archived 2026-04-30, succeeded by `statute-extraction`). The two tracks share a target schema (currently data model v1.3) and the locked 141-row compendium contract, but operate independently.

## Sessions

(Newest entries first.)

### 2026-06-14 (later) — Phases 3 + 3.5 + 4 + 5 + 6 shipped end-to-end: PREVIEW release materialized at `releases/oh/`; full OH suite 139/139 green

Six commits in earlier-in-this-session (Phase 0, 1, 2) shipped audit + loaders + chain. This entry covers the remaining five phases — gifts composer, filings composer, CLI materializer, four release READMEs, and the actual preview-release run.

**Phase 3 — gifts composer.** `src/lobby_analysis/allocation/oh/gifts.py` (~170 lines) ships `compose_gifts(extractions_dir, oh_csv_path=None) -> DataFrame`. Schema is the 10-column `GIFTS_COLUMNS` tuple per plan §4. Event-type derivation: `gift_type == "meal"` → `event_type="meal"` (Section II.B); anything else → `event_type="gift"` (Section II.A). Lawmaker resolver: prefix-strips `Sen.`/`Rep.`/`Senator`/`Representative`, looks up the result in a full-name index (case-folded `oh.csv.name`), falls back to surname-only when the recipient is a single token, **declines on ambiguous surnames** (two Smiths in oh.csv + recipient = "Sen. Smith" → null, not arbitrary pick). 14 tests cover schema, row shape, event-type derivation, all four resolver paths (full-name hit / surname-only hit / unknown / ambiguous).

**Phase 3.5 — filings composer (Q6 → include).** `src/lobby_analysis/allocation/oh/filings.py` (~110 lines) ships `compose_filings(extractions_dir) -> DataFrame`. Schema is the 14-column `FILINGS_COLUMNS` tuple. Two findings-doc normalizations applied with strict guards: (1) **stated-zero** — `(total_expenditure is None AND len(expenditures) == 0) → 0.0`; `(None, non-empty)` stays null so upstream defects surface. (2) **is_current forcing** — `(filing_action == 'original' AND supersedes is None) → True`; both conjuncts required. 14 tests cover both normalizations + the strict-guard cases + summary stats.

**Phase 4 — CLI materializer.** `src/lobby_analysis/allocation/oh/cli.py` (~95 lines) ships one subcommand: `materialize --extractions ... --bills ... [--oh-csv ...] --out ...`. Writes the three TSVs with `_preview` suffix (Q1-locked). 5 integration tests cover end-to-end CLI invocation, schema, row counts, normalization application, and the `--oh-csv` optional path.

**Phase 5 — release READMEs.** Four READMEs at `releases/oh/README.md` + `releases/oh/{chain,gifts,filings}/README.md`. Top-level documents the three-edge framework (compared to WI/NY), the preview caveat, and the six caveats analysts must read before quantitative use. Per-artifact READMEs document schema + conservation rules + provenance per the WI release-doc pattern.

**Phase 6 — preview materialize run.** `uv run python -m lobby_analysis.allocation.oh.cli materialize` against the 316-filing cache + Plural Policy bundle + oh.csv produced the three preview TSVs in-tree at `releases/oh/`:

- `chain/OH_chain_2025_2026_preview.tsv` — **1,589 rows × 18 cols, ~600 KB** (1,299 bill + 150 subject + 88 jcarr + 34 oac_rule + 18 unmatched; top bill HB 96 budget at 73 rows)
- `gifts/OH_gifts_2025_2026_preview.tsv` — **0 rows, 131 bytes (header only)** — empty per Phase 1 Finding 2 (likely sampling artifact; secondary hypothesis is extraction-prompt scope). Honestly documented in the gifts README.
- `filings/OH_filings_2025_2026_preview.tsv` — **305 rows × 14 cols, ~220 KB** (97 stated-zero normalizations applied; 0 is_current forcings needed in this slice — all already True).

Full OH suite at session end: **139/139 green** (48 classifier + 32 loaders + 5 dedup + 21 chain + 14 gifts + 14 filings + 5 CLI). All pure-logic; no DB, network, or real-data dependency.

**End-of-phase posture.** The composer code is complete and the preview release is shipped in-tree. The remaining open follow-ups are documented in the phase-2 findings doc + the release READMEs: (a) extraction-prompt verification for II.A/II.B gifts (likely separate PR); (b) `bill_number` over `original_text` for join key (low-impact in current slice); (c) OAC regex widening for v0.1 (colon-subdivided rules, multi-rule strings). Branch is ready for PR per Q1's preview-release scope.

### 2026-06-14 — Phase 2 (chain composer) shipped: `compose_bill_chain` + 21 tests; full OH suite 106/106 green; real-data smoke = 1,589 chain rows

`src/lobby_analysis/allocation/oh/chain.py` (~250 lines) ships `compose_bill_chain(extractions_dir, plural_dir) -> DataFrame` per plan §4/§4a/§6. Schema is the 18-column `CHAIN_COLUMNS` tuple matching the plan §4 sketch. 21 chain tests + the existing 85 = **106/106 OH tests green**. Per-class behavior locked:

- `bill` (joins Plural) → cross-product over primary sponsorships → N rows with populated sponsor fields, `confidence='direct'`.
- `bill` (no Plural match, defensive 0-primary, or fuzzy label) → 1 row, null sponsor, `confidence` reflects the route.
- `jcarr` / `oac_rule` → 1 row, null sponsor, `confidence='oac_dropped'`.
- `subject` (both subject kinds) → 1 row, null sponsor, `confidence='subject_only'`.
- Empty position (classifier raises) → 1 sentinel row, `confidence='null_extraction'`. One bad position cannot kill the composer run.

Composer calls `select_canonical_extraction(load_filings(...))` to dedupe the 11 cached duplicates surfaced in Phase 1.

**Real-data smoke against the 316-filing cache** (full writeup at `results/20260614_phase2_chain_findings.md`): **1,589 chain rows** with conservation arithmetic clean. 1,299 `bill` + 150 `subject` + 88 `jcarr` + 34 `oac_rule` + 18 `unmatched`. Cross-product: 411 (1-primary) + 444 (2-primary) = 855 unique bill-position joins → 1,299 bill chain rows. Deduped input position count = 855 + 290 = 1,145 (32 lower than Phase 1's 1,177 because dedup dropped non-canonical extractions of 5 dupe-cached filings — confirming `select_canonical_extraction` is working).

Top-5 lobbied bills: HB 96 (FY 2026-27 budget, 73 rows), HB 1 (Property Protection Act, 22), HB 276 (340B reimbursement, 14), HB 105 (litigation funding, 14), HB 227 (excavation, 12). 140 of 305 canonical filings contribute chain rows (54% are position-empty in this slice — matches the 53% nil rate from the 06-11 data-landed doc).

**Two open follow-ups** flagged in the findings doc:
1. `extract_position_label` returns `original_text` not `bill_number`. In this slice no extra-text labels surface, so practical impact is zero — but the 06-11 smoke-test script used `bill_number` as preferred join key. Worth swapping when the full-corpus run lands.
2. No `confidence='direct_no_primary'` distinction for the defensive 0-primary case; analysts filter via `num_primary_sponsors==0 AND bill_class=='bill'` if needed. Could split for v0.1.

Phase 3 (gifts composer) is unblocked next.

### 2026-06-14 — Phase 1 (loaders) shipped: 5 typed loaders + dedup helper; 85/85 OH tests green

Phase 1 Step C complete (classifier Steps A+B were already in at `f59a7f9`). `src/lobby_analysis/allocation/oh/load.py` (240 lines) ships five typed loaders plus `select_canonical_extraction` (helper). Test count for OH allocation: 48 (classifier) + 32 (loaders) + 5 (dedup) = **85**, all green via `python -m pytest tests/allocation/oh/`.

**Loader contracts:**

- `load_filings` / `load_positions` / `load_gifts` walk `data/oh_portal/extracted/*/*/filing.json` and project to (filing | position | gift) grain. Each carries the typed Pydantic model in an `*_obj` column (preserves the classifier-callable contract).
- `load_plural_bills` / `load_plural_sponsorships` read the 16 Plural Policy 136th GA CSVs. Bills loader adds `identifier_norm` (uppercase + dot-stripped + whitespace-collapsed) for direct join with extraction labels; sponsorships loader filters to `classification == "primary"` by default per Q2.
- Loaders do NOT pre-filter empty positions or duplicate extractions — they surface upstream defects at the composition seam, not silently.

**Three structural findings from the real-data smoke test on the 316-filing cache** (full writeup at `results/20260614_phase1_loaders_findings.md`):

1. **Cache has 11 duplicate extractions for 5 filing_ids** (one filing has 8 hash-subdir-distinct extractions). `select_canonical_extraction` picks most-recent by mtime, lex `source_path` tiebreaker. Phase 2 chain composer must invoke it before composing.
2. **0 gifts across the 316 cached filings.** Possible causes (sampling artifact / 53% nil rate / extraction-prompt scope). Phase 3 composer ships either way; preview release's `releases/oh/gifts/` artifact will be empty until extraction-side investigation resolves this. Flag in gifts README.
3. **18 unmatched bill_referenced positions are extraction-side defects**, not classifier bugs (subject text mis-placed in `bill_reference`, OAC variants with colons/Chapter prefix not in the regex, two malformed `CB ...` identifiers). The classifier correctly flags them; the chain composer emits them with `bill_class="unmatched"`, `bill_id=null` as a quality canary.

**Conservation sanity-check.** Across 1,177 positions: 887 `bill` + 150 `subject` + 88 `jcarr` + 34 `oac_rule` + 18 `unmatched` = 1,177. Every position routes to exactly one class. The 887 `bill` count matches the 06-11 smoke-test 86.4% row-weighted match against `OH_136_bills.csv` — the classifier-loader integration is consistent with the data-landed finding.

Smoke + diagnostic scripts saved at `results/20260614_phase1_loaders_smoke.py` and `results/20260614_phase1_loaders_diags.py` for re-run after #35 lands the full corpus.

Phase 2 (chain composer) is unblocked next.

### 2026-06-14 — Branch `oh-chain-composer` cut + Phase 1 classifier shipped + Phase 0 pre-flight audit clean

This entry back-fills the morning Phase 1 classifier session (was captured in the handoff brief but not in this log) and adds the evening Phase 0 audit findings.

**Morning session (commit `f59a7f9` by Claude-via-Dan):** branch `oh-chain-composer` cut off `bfe9f8f`. Phase 1 *classifier* (Steps A + B per plan §5) shipped at `src/lobby_analysis/allocation/oh/classify.py` (165 lines) + `tests/allocation/oh/test_classify.py` (290 lines, **48 tests all passing** — `python -m pytest tests/allocation/oh/ -v` runs in ~0.03s with no data/network/DB dependencies). Local conftest at `tests/allocation/oh/conftest.py` overrides the repo's autouse Postgres-dependent `_truncate_filings` fixture to a no-op, scoped to OH allocation tests only. Phase 1 *loader* (Step C) still open — that's Phase 1's remaining piece. Handoff brief shipped at `docs/active/oh-portal-extraction/HANDOFF_oh_chain_composer.md` for the next agent.

**This session (Phase 0 pre-flight audit, Q1–Q6 resolution):** picked up the handoff. Surfaced Q1–Q6 to Dan; all six resolved at the plan's recommendations (Q1 = preview slice, Q2 = primary-only v1, Q3 = download `oh.csv`, Q4 = defer expenditures, Q5 = branch already cut, Q6 = include minimal filings TSV). Phase 0 audit findings doc at `results/20260614_phase0_preflight_audit.md` + script at `results/20260614_phase0_preflight_audit.py`. Five Phase 0 checks all green:

- **(a) Schemas:** 16/16 Plural Policy CSVs row-count-stable vs the 2026-06-11 data-landed doc; columns inventoried.
- **(b) Smoke test:** 86.4% row-weighted match identical to 06-11 (cache has not grown — #35 has not run).
- **(c) Multi-primary:** CONFIRMED structural for OH (946 of 2,317 bills = **40.8%** have ≥2 primaries on substantive HBs/SBs, not just resolutions). High-primary tail (≥10) is exclusively ceremonial HRs (99 = whole-House signing on to memorial/honor resolutions); document as artifact in the chain README.
- **(d) `bill_actions.description` cosponsor names:** 0 hits over 5,525 rows — **WI lesson does NOT apply to OH**. Cosponsors live cleanly in `bill_sponsorships.classification == "cosponsor"`; v1.1 cosponsor extension is a config flip.
- **(e) `oh.csv` legislator roster:** downloaded from `https://data.openstates.org/people/current/oh.csv` (88,210 bytes, 132 legislators = 99 House + 33 Senate). Landed at `data/bills/OH/oh.csv` via the worktree's `data/` symlink to `~/data/lobby_analysis/`. Closes the second half of `STATE_COVERAGE.md` OH footnote 7.

**Worktree setup note:** new agents picking this up should `readlink` an existing recent worktree's `data/` (e.g., `leave-behind-prep`, `backend-prototype`, `ny-disclosure-explore`) before assuming "no data on this machine" — the convention is `data → /Users/dan/data/lobby_analysis` symlink + `.env.local → ../../.env.local` symlink. Main worktree does not carry a `data/` dir, so a "missing data" first impression is a false negative.

Phase 1 (loader Step C) is unblocked next. Plan reference: `plans/20260611_oh_chain_composer_design.md` §5; handoff: `HANDOFF_oh_chain_composer.md`.

### 2026-06-11 — Plural Policy 136th GA data drop + chain composer v0 design plan

- **Plural Policy bundle landed** (data drop by Dan into `data/` + this session's mechanical move/extract). 136th GA session bundle now at `data/bills/OH/136/` (16 CSVs; 2,325 bills, 11,559 sponsorship rows, 36,023 vote-people rows). Layout mirrors `data/bills/WI/2025/`. Zip preserved at `data/bills/OH/PluralPolicy_OH_136_csv.zip`.
- **Structural join smoke-test passed.** Joining 316 cached AER extractions' `positions[].bill_reference.bill_number` against `OH_136_bills.csv.identifier`: **86.4% row-weighted match** (887/1,027). Top match HB 96 (state biennial budget, 81 references). Unmatched 13.6% are exclusively OAC / JCARR admin-rule citations (e.g., `5160-32-02`, `JC 4731-9-01`) — not bills, expected miss. Reusable script at `results/20260611_plural_policy_join_smoke.py`.
- **Chain composer v0 design plan authored** at `plans/20260611_oh_chain_composer_design.md` (Dan-requested follow-up after surfacing that no chain code or plan was pre-written). Captures: edge-inventory delta vs WI/NY (OH chain is a *third* structural form — no IPF needed since no $ or time marginals; gifts edge is native to OH and gets sibling artifact); proposed schemas for `releases/oh/chain/OH_chain_2025_2026.tsv` + `releases/oh/gifts/OH_gifts_2025_2026.tsv`; 7-phase TDD scaffold (Phases 0-5 = $0; Phase 6 dependent on #35); 5 open questions with recommendations for execution-session resolution.
- **STATUS.md row 64**: pending item (b) Plural Policy download flipped to landed; pending item (c) `releases/oh/` materialization now points at the design plan with `oh-chain-composer` recommended branch name. STATE_COVERAGE.md OH Status line + footnote 7 updated to match.
- **Honest scope read**: the data drop was the prerequisite, not a blocked script waiting to fire. The chain composer is now *designed*, not *built*. `oh.csv` legislator roster (footnote 7 second half) still pending — separate Plural Policy fetch.
- Doc-only on main (per Dan's `feedback_weekly_updates_to_main` memory). Two commits this session: `551411b` (data drop + smoke test), `e8ad72c` (chain composer plan). Both pushed.
- Convo: [`convos/20260611_oh_plural_policy_data_drop_and_chain_composer_plan.md`](convos/20260611_oh_plural_policy_data_drop_and_chain_composer_plan.md). Plan: [`plans/20260611_oh_chain_composer_design.md`](plans/20260611_oh_chain_composer_design.md). Result + smoke-test script: [`results/20260611_plural_policy_data_landed.md`](results/20260611_plural_policy_data_landed.md), [`results/20260611_plural_policy_join_smoke.py`](results/20260611_plural_policy_join_smoke.py).

### 2026-06-05 (later) — provenance fixes implemented (TDD): code-populated `raw_text` + true regime

- **Part 1 — `raw_text` code-populated (commit `9b0fd7d`).** `extract.py`:
  `build_tool_schema()` drops `raw_text` from the model-visible tool schema;
  `assemble_filing()` sets `raw_text = aer_text` after validation, so the audit
  field is source-of-truth regardless of (and overriding) any model value. Also
  trims output tokens per call.
- **Part 2 — true OLAC regime captured (commit `629ce28`).** `discover.py`:
  `category` on `FiledForm`, `category_to_regime()` (L/E/R →
  legislative/executive/retirement_system, unknown → None — never a silent
  legislative default), `regime` column in the TSV. `batch.py`:
  `read_url_regimes` (header-based DictReader, back-compatible with plain URL
  lists / pre-regime TSVs) + `select_legislative` (skip non-legislative/unknown
  by default; `--include-nonlegislative` override). `pipeline.py`:
  `extract_one_filing(regime=...)` stamps the regime into `extraction_run.json`
  and warns when a non-legislative/unknown filing is run through the legislative
  brief.
- **Regime mapping confirmed empirically.** Scanned all 2,684 cached agent pages
  (364,351 AER rows): Category is exactly `L`/`E`/`R`, no blanks — resolving the
  plan's Medium-confidence flag on `R`. (`L` 52.3% / `E` 46.9% / `R` 0.8%,
  all-years.) Result: `results/20260605_olac_category_regime_distribution.md`.
- **Code review caught a real defect.** The non-legislative warning keyed on
  `DEFAULT_REGIME` rather than the brief regime, so an unknown-regime (`None`)
  filing under `--include-nonlegislative` emitted "None brief not yet
  implemented." Fixed at root + added the missing `regime=None` test.
- **Verification:** 37/37 oh_portal tests green (16 new, TDD); `ruff check`
  clean. Repo has no CI and isn't maintained under `ruff format` (left format
  alone). The 3 `test_pipeline.py` failures are local-data-only (untracked CA
  snapshot), not a regression. Branch `MERGEABLE`, pushed to PR #33.
- **Deferred:** step 21 (doubled `_discover_dir` cache path) → issue
  [#36](https://github.com/danparshall/lobby_analysis/issues/36); do post-merge
  so stale-code worktrees can't re-double the path. Includes cache migration.
- Convo: `convos/20260605_provenance_fixes_implementation.md`.

### 2026-06-05 — OH `discover --all` bulk grab (45,605 AERs) + 300-filing slice validation

- **ToS gate (handoff blocker) cleared.** `www2.jlec-olig.state.oh.us/robots.txt` → 404
  (no policy); no Terms of Use on OLAC; data is Ohio statutory public record (ORC §§101.70+).
- **Crawler etiquette fixed before crawling (commit `4ebd2e3`).** The runbook claimed
  "polite spacing is built in" — it wasn't (`discover_all` had no inter-request sleep), and
  the crawler spoofed a Chrome UA. Renamed `CHROME_UA` → honest `USER_AGENT`; added
  `REQUEST_DELAY_SECONDS=0.5` throttle at live-network entry points (cache hits unthrottled);
  TDD'd a UA-honesty contract test; corrected the runbook. Suite 372 pass / 3 pre-existing.
- **`discover --all` ran:** **45,605 AER filings** (2025=34,080 / 2026=11,525), 2,684 agents,
  2,741 employers, **100% employer-populated, 0 dup report_ids**. Index → `recent.tsv`
  (gitignored, regenerable). The employer-misfile fix holds at scale.
- **300-filing slice validation (sonnet-4-6):** 299 extracted first-pass + 1 transient 529
  (1396214) **recovered on one retry** → effectively **300/300 extractable, 0 genuine
  failures**. Measured **15.6 s/filing**, ~$0.035/filing.
- **Two gaps surfaced (pre-existing):** (1) no retry on transient API errors → silent drops
  at scale; (2) serial `batch.py` = ~8 days for the full 45K. Also a doubled discover
  cache-path bug (`_discover_dir` re-appends `oh_portal`).
- **Decision:** full-universe extraction deferred to a dedicated build (Message Batches API
  + prompt caching + transient retry ≈ $800 async) — issue
  [#35](https://github.com/danparshall/lobby_analysis/issues/35).
- **Content analysis of the 300 (post-checkpoint).** Of 305 distinct extracted filings:
  **53% fully nil** ("No Activity / No expenditures"), 45% list bills lobbied (mean 3.8,
  max 108 bills; 1,145 bill-rows total), only **5% report any expenditure**. No
  support/oppose stance (same gap as WI). **Regime mix:** among the 109 with raw_text,
  ~86% legislative / ~13% executive / ~1% retirement — the crawl spans all 3 OH regimes,
  but `pipeline.py` runs every filing through the *legislative* brief and stamps
  `regime="legislative"`. Empirical confirmation of the v2.2 regime gap that main's
  `STATE_REGIME_SPLITTING.md` predicted from statute.
- **`raw_text` root-caused.** Missing on ~64% of filings because it's an *optional
  model-emitted* field (omitted even on 71% of nil filings → not truncation); when present
  it's byte-identical to `html_to_aer_text(raw.html)` (EXACT match verified on 1509340).
  Fix = code-populate from source + drop from the tool schema.
- **Plan created:** `plans/20260605_extraction_provenance_fixes.md` (TDD; raw_text + true
  regime; do before #35). Doubled discover cache-path bug (`_discover_dir`) folded in as
  optional step 21.
- Results: `results/20260605_slice_validation_300.md`. Convo:
  `convos/20260605_oh_discover_all_and_slice_validation.md`.

### 2026-06-04 (later) — sonnet validated → employer/warnings schema fix → statute-extraction archived

- **Sonnet validation.** `claude-sonnet-4-7` doesn't exist (404); sonnet is on `4-6`,
  opus on `4-7`. Validated sonnet-4-6 vs the opus baseline on AER 1427844 (same cached
  HTML, 3 runs). Sonnet **consistent** and on row-accuracy ≥ opus (fixes `is_itemized`),
  but it put the employer into `filer_organization` where opus dropped it. Traced to the
  **brief**, not the model: rule 6 said "populate employer name" with no schema slot →
  contradictory spec → models cope differently, both silently.
- **Fix (TDD):** added `LobbyingFiling.employer: Organization|None` +
  `extraction_warnings: list[str]` (additive, backward-compat); rewrote the brief
  (employer→`employer`, not `filer_organization`; new warnings rule; deleted the phantom
  `regime=` instruction; cut `(A')` jargon); stamped `regime="legislative"` in run
  metadata. 6 new tests; full suite **371 pass / 3 pre-existing** data-fixture fails;
  ruff clean. **Both opus and sonnet now converge** (employer routed correctly,
  `filer_organization` null, warnings flag the II.D gap). Switched `MODEL_ID` → sonnet-4-6
  for bulk. Commit `e5d2da3`.
- **regime decision:** not added to `LobbyingFiling`. The statute-side `regime` axis is a
  v2.2 design gap (the branch/level axis was re-encoded as v2 `actor_*`/`def_target_*`
  row IDs, but regime-as-multiplier was dropped in the v2 rebuild; see untracked
  `state_regime_splitting.md`). Deferred to the gather-first v2.2 schema pass; meanwhile
  it's caller-stamped in `extraction_run.json`.
- **Archived `statute-extraction`** on main (`20ee37a`): harness superseded by
  compendium-2.0; marked DO-NOT-USE; stranded-schema findings recorded. Not merged, not
  deleted.
- **Not run:** the bulk OH discover→batch grab (still gated on go + robots.txt/ToS).
- Convo: [`convos/20260604_sonnet_validation_employer_warnings_schema.md`](convos/20260604_sonnet_validation_employer_warnings_schema.md).
  Result: [`results/20260604_sonnet_opus_validation.md`](results/20260604_sonnet_opus_validation.md).

### 2026-06-04 — schema retargeted to current main + (B') discovery built; full pipeline reproducible

- **Schema scare resolved (no v1.4 needed).** Investigated the belief that Amina's `LobbyingFiling`
  was "ancient v1." Git says otherwise: her branch base (2026-05-18) postdates Compendium 2.0/v2,
  and the only delta on main since was **two optional fields** (`total_hours_communicating`,
  `total_hours_other`). Pulled them in surgically; the parser now targets current `LobbyingFiling`.
  The v1→v2 transition was the **SMR/compendium** (Prong 1), a different schema from the
  disclosure-record `LobbyingFiling` (Prong 2) the OH parser targets. Dropped the v1.4/Gowrav
  ceremony. Re-extraction confirmed the employer can live in `filer_organization` (stochastic
  run-to-run) — no schema gap, brief-consistency only.
- **(B') filing-ID enumeration solved (the gating item).** Probed OLAC read-only and mapped the
  agent-axis chain: `Agents/List` (CSV roster, 1,502 agents) → `FormsFiledSearch?LastName=` (agent
  IDs) → `Agents/{id}/FormsFiled` (every form, with Year/Employer/Type/Period columns) → filter
  `Type==AER` & recent years. Verified against ground truth (agent 5272 = Nathan Aichele; all 3
  seeds present with correct employers). Built `discover.py` (TDD parsers/filter + live-validated
  fetch, raw-artifact caching). Live: 139 recent AERs of 2,213 forms for Aichele.
- **The index carries the employer per filing** — captures the (agent, employer) tuple structurally,
  independent of the (stochastic) detail-page extraction.
- **Full pipeline now reproducible end-to-end, no wrappers.** `discover --out x.tsv` → `batch --file
  x.tsv` (batch reads the TSV's `aer_url` column directly); `env_local.load_env_local()` self-loads
  the API key from `.env.local`. Proven: `batch --file <tsv>` with no key in the shell extracted 2
  new filings end-to-end. Runbook: [`results/20260604_pipeline_runbook.md`](results/20260604_pipeline_runbook.md).
- **Not run:** the full `discover --all` crawl (thousands of AERs → thousands of LLM calls) — pending
  Dan's go + a robots.txt/ToS check. discover+batch tests 17 pass; full suite 365 / 3 pre-existing.
- Convo: [`convos/20260604_oh_schema_retarget_discovery_pipeline.md`](convos/20260604_oh_schema_retarget_discovery_pipeline.md).

### 2026-06-03 (later) — (A') first real run GRADUATED + (B') batch runner built

- **Branch:** `oh-portal-aprime-batch`, forked off `oh-portal-extraction` (run-and-PR per Dan).
- **First real extracted data.** The (A') LLM call fired for the first time (quota reset 2026-06-01).
  Report 1427844 (Aichele/ARC Gaming), run `bd540187`, `claude-opus-4-7`, 8.06s →
  **29/31 rows CORRECT (93.5%), 0 WRONG → graduated to (B').** Validation table filled in
  [`results/20260507_oh_a_prime_validation.md`](results/20260507_oh_a_prime_validation.md).
- **The OLAC blocker was outside-US connectivity, not a portal defense.** From a US network the
  live `requests.get` fetch worked first try — no VPN/browser-save needed. Browser-save is only
  required when running from abroad. (B') from a US machine/CI is directly scrapable.
- **Two schema gaps confirmed at extraction (both pre-flagged, neither a model error):**
  (1) **employer dropped** — `filer_organization=null`, ARC Gaming preserved nowhere; the
  (agent, employer) tuple has no slot. **Systematic** — HART + LKQ batch filings dropped their
  employers too. Leading v1.4 candidate. (2) `is_itemized=null` (true `false`) — one-sentence
  brief fix. No new gaps surfaced.
- **(B') batch runner, built test-first:** new `pipeline.py` (`extract_one_filing`, factored out
  of `__main__` which now delegates to it) + `batch.py` (`find_existing_extraction` resume guard,
  `run_batch` skip+failure-isolation, `cli_main`) + `tests/test_oh_portal_batch.py` (4 tests, real
  fs + injected worker, no network/LLM mocks). Ran the batch over the 3 seeds:
  1427844 **skipped** (resume), 1459616/HART + 1405684/LKQ **extracted**, 0 failed. 3 OH filings
  now extracted total. All 3 seeds turned out to be the same agent (Aichele), different employers.
- **Gating open item for (B'):** **filing-ID enumeration** — the runner consumes a supplied URL
  list; we have no way yet to discover the OLAC `report_id` universe. Flagged, not built.
- **Tests:** oh_portal+batch 15/15; full suite 358 pass / 3 fail. The 3 fails are pre-existing
  data-only (Track A `test_pipeline.py` wants CA snapshot `2026-04-13`; only `2026-05-01` synced
  here; gitignored data). Inherited from branch point, not this session's code. ruff clean.
- Convo: [`convos/20260603_oh_aprime_run_and_batch.md`](convos/20260603_oh_aprime_run_and_batch.md).

### 2026-06-03 — HANDOFF prepared; Dan taking branch over from Amina

- **Ownership change:** Dan is taking this branch over from Amina (decided 2026-06-03 while
  scoping the MI/NC/OH state pulls). Coordinate with Amina on the in-flight LLM run.
- **Resume here:** [`convos/20260603_oh_resume_handoff.md`](convos/20260603_oh_resume_handoff.md)
  — a zero-context handoff for finishing the (A') round-trip.
- **State unchanged since 2026-05-22:** (A') code shipped + round-trip validated against saved
  HTML; only the LLM extraction run + validation-table fill remain. The API quota cap that
  blocked the run **reset 2026-06-01**.
- **Practical first blocker:** the raw HTML (report_id `1427844`, Aichele/ARC Gaming) is **not
  on this machine** — it was browser-saved on Amina's VPN'd machine and never synced. Get it
  from Amina, re-fetch from a US network, or browser-save again. See the handoff.
- No code or data changed this session — handoff documentation only.

### 2026-05-22 — VPN workaround landed + handoff for LLM run

- VPN reachability to OLAC has been the long-running blocker on (A') execution. Workaround landed this session: browser-saved the AER HTML at `data/oh_portal/html_test/`, then mirrored into the canonical layout at `data/oh_portal/raw/1427844/2026-05-21T18-52-26+00-00/raw.html` with a real `meta.json` (sha256, `fetch_method="browser-save-via-vpn-then-local-copy"`). Downstream tooling sees the same shape as a live fetch.
- Wrote a one-off invocation that imports the shipped `extraction_brief` / `provenance` / `extract` modules and runs them against the local HTML — skips fetch only. Content verified to match the expected sample (Aichele/ARC Gaming, 4 bills, $20 Section II.D).
- Closed [open question (c) from 2026-05-07](#open-questions): canonical `regime` literal is `"legislative"` (verified `git grep "regime=" origin/statute-extraction`); matches `extraction_brief.py:14`. No code change.
- Pre-filled the validation results doc at [`results/20260507_oh_a_prime_validation.md`](results/20260507_oh_a_prime_validation.md) with source-derived ground truth (bills, expenditure totals, expected null patterns, pre-flagged schema gaps). Reduces the LLM-run step to tag-filling.
- LLM call hit a workspace API quota cap (resets 2026-06-01). Handing off the actual extraction to a US-based colleague with their own key.
- Side-note infra: worktree venv editable install is duplicated 4×; `PYTHONPATH=src .venv/bin/python -m ...` is the workaround. Not blocking.
- Convo: [`convos/20260522_phase_3_handoff_prep.md`](convos/20260522_phase_3_handoff_prep.md).

### 2026-05-07 — (A') brainstorm + implementation plan

- Pre-flight: caught up on a week of upstream work (compendium locked at 141 rows, schema bumped v1.1 → v1.2 → v1.3 with new `regime`/`registrant_role`/`condition_text` fields, `statute-retrieval` merged + archived, `statute-extraction` is Track A's active branch with iter-1 hitting 14/15 inter-run agreement on OH `definitions` chunk).
- Merged `origin/main` (39 commits) into `oh-portal-extraction`. One conflict on `STATUS.md`'s Active Research Lines table — resolved by keeping our row and Dan's `filing-schema-extraction` row, dropping his stale "(other fellow's branch — not investigated)" placeholder. Tests post-merge: 303 pass / 5 skipped / 3 pre-existing data-fixture failures unrelated to this branch.
- Ran the `brainstorming` skill end-to-end on "what does done-for-OH look like for the next ~2 weeks." Converged on a phased path: (A') smallest-viable single-filing round-trip → (B') single-regime MVP across all current filers → (C') graduate. Validation strategy for (A') is model-anchored hand-spot-check; SMR-anchored validation deferred to (B'). Regime choice for (A') = OH legislative agent (ORC §§101.70–101.79) — largest filer population, Track A's iter-1 already converged on its `definitions` chunk, statute structurally unchanged 2010 → 2025 per OH SMR diff.
- Brainstorm output (4 confirmed sections): (1) round-trip architecture; (2) source acquisition + sample selection; (3) extraction + validation; (4) failure handling + testing scope + definition of done.
- Switched to `write-a-plan` skill: drafted [`plans/20260507_oh_a_prime_implementation.md`](plans/20260507_oh_a_prime_implementation.md) with TDD-shaped tasks, explicit edge cases, two unit tests planned (extraction-brief substring assertions; provenance round-trip), one real LLM call against one real OLAC PDF as the end-to-end behavioral check.
- Open coordination items flagged for next weekly sync: (a) Anthropic SDK vs Dan's subagent-dispatch pattern preference; (b) v1.4 schema-gap handling protocol if (A') surfaces gaps; (c) canonical `regime` enum value for OH legislative agent — read from `origin/statute-extraction` before Phase 2.

### 2026-04-30 — Branch kickoff

- Cut `oh-portal-extraction` worktree off `main` (eb849ca).
- Seeded `docs/active/oh-portal-extraction/{convos,plans,results}/` and this log.
- Baseline check: tests passing, environment clean.
- Next: brainstorming session on what the OH portal looks like (existing snapshot in `docs/historical/pri-2026-rescore/` is the starting artifact). Decide scrape strategy before writing any extraction code.

## Plans

(Plans are added under `plans/` and listed here once written.)

- [`20260507_oh_a_prime_implementation.md`](plans/20260507_oh_a_prime_implementation.md) — single-filing round-trip on OH legislative agent A&E report; TDD-shaped, ~25 bite-sized tasks across 4 phases.

## Convos

(Convo summaries land under `convos/YYYYMMDD_topic.md` and are listed here.)

- [`20260507_oh_a_prime_brainstorm.md`](convos/20260507_oh_a_prime_brainstorm.md) — scope tier choice (A'/B'/C'), validation-strategy comparison (model-anchored / SMR-anchored / form-as-schema), regime selection (legislative), and 4-section design walk-through.
- [`20260522_phase_3_handoff_prep.md`](convos/20260522_phase_3_handoff_prep.md) — VPN workaround landed (browser-save + canonical-layout mirror), regime literal verified, validation skeleton pre-filled with ground truth, LLM run handed off after workspace API cap surfaced.

## Open questions

- **Resolved 2026-05-07:** OH snapshot tier under `docs/historical/pri-2026-rescore/` is *clean capture* (11 MB, 26 artifacts, no WAF/SPA blocker) — but the actual artifact bytes live only on Dan's laptop, so (A') fetches fresh from OLAC rather than reusing.
- Does OLAC require auth/CAPTCHA for individual report PDFs? Dan's 2026-04-13 snapshot didn't flag it, but he scraped discovery pages, not per-report PDFs. First execution of the (A') plan will surface this.
- Are OLAC report PDF URLs stable, or session-bound? Affects how we record the "stable identifier" for samples.
- Is `LobbyingFiling.model_json_schema()` clean enough for Anthropic SDK tool-use, or do its nested optionals/discriminated unions need flattening?
- What's the team's preferred protocol for handling v1.4 schema-gap proposals if (A') surfaces them — ad-hoc convo doc + Dan/Gowrav review, or a more formal RFC pattern?
- What's the right `ExtractionCapability` (`src/lobby_analysis/models/pipeline.py`) shape for OH — populated as a side-effect of the pipeline, or curated up-front? Deferred to (B').

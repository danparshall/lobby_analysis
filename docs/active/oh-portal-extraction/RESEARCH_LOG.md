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

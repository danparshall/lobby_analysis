# wi-campaign-finance Implementation Plan

**Goal:** Close the structurally missing $-flow leg of the WI 2025-2026 lobbying chain by ingesting WI candidate-committee receipts via the FollowTheMoney.org API, joining principal-side / lobbyist-side / lawmaker-side anchors, and materializing `releases/wi/campaign_finance/` TSVs that consumers can compose with the existing `releases/wi/chain/WI_chain_2025.tsv`.

**Originating conversation:** [`../convos/20260603_wi_cfis_access_surface_scoping.md`](../convos/20260603_wi_cfis_access_surface_scoping.md)

**Originating scoping doc:** [`../results/20260603_phase_4_cfis_scoping.md`](../results/20260603_phase_4_cfis_scoping.md)

**Originating sample-query writeup:** [`../results/20260603_ftm_sample_query_lemahieu.md`](../results/20260603_ftm_sample_query_lemahieu.md)

**Context:** Phase 4 of the archived `wi-allocation-matrix` plan recommended scoping WI Ethics Commission's CFIS as a separate branch. Scoping landed 2026-06-03: WI Ethics Commission's portal (Sunshine, ex-CFIS) is a Civera-hosted Next.js SPA with no documented public API and a 65K-row UI-export cap — not viable as the primary source. FollowTheMoney.org has 50-state coverage current through 2024, a free non-commercial-research API, **and has already done the donor-entity canonicalization + 3-level industry classification** we'd otherwise have to build. A sample query against LeMahieu's 2022 cycle (2,803 transactions / $609K / 1,822 contributors) cross-validated the chain — Xcel Energy at #21 in his top-25 donors and WEC Energy Group PAC in transaction page 0 both match their chain SB 28 positions.

**Confidence:** High on path (FTM-first with Selenium-Sunshine as coverage-gap fallback), Medium on principal-side / lawmaker-side crosswalk completeness (needs empirical confirmation across the full ~165 sitting WI legislator × ~525 chain-active principal universe), Lower on lobbyist personal-contribution slice (`d-llink` flag is partial ~5% coverage; relies on name-string match against `WI_lobbyists.tsv`).

**Architecture:** Three-phase. **Phase 0** = calendar wait for FTM Institute's automatic expanded-access review (already triggered by basic-tier quota exhaustion during scoping). **Phase 1** = FTM ingest + three crosswalks (principal → FTM `d-eid`, lawmaker → FTM `c-t-eid`, lobbyist → FTM `Contributor` for individuals) + materialize TSVs. **Phase 2 (conditional)** = Selenium-driven Sunshine port for specific gaps Phase 1 surfaces (only if `Conduit` / `Comment` / `EmployerAddress` etc. turn out to be load-bearing for downstream consumers; not a full duplicate ingest).

**Branch:** `wi-campaign-finance` — to be cut off post-merge main after `wi-cfis-scoping` lands. Worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-campaign-finance/` (does not exist yet; create via `using-git-worktrees` skill).

**Tech Stack:** Python 3.13, uv-managed; `httpx` for FTM HTTP client (sync, since query rates are low); `pydantic` for typed FTM response models; `pandas` for join + materialize; `pytest` + recorded HTTP cassettes (via `vcrpy` or hand-curated JSON fixtures) for offline tests. **No Selenium dependency in Phase 1** — Sunshine fallback (Phase 2) would add `playwright` only if needed.

---

## Worktree paths (CRITICAL — all paths are within the worktree once cut)

- **Worktree root:** `/Users/dan/code/lobby_analysis/.worktrees/wi-campaign-finance/`
- **Branch docs:** `docs/active/wi-campaign-finance/` (seed with `RESEARCH_LOG.md` + `convos/` + `plans/` + `results/`)
- **Source upstream (read-only):** `releases/wi/` (6 lobbying TSVs + chain release) — input contract
- **Scoping reference (read-only):** `docs/historical/wi-cfis-scoping/` after this branch merges; or `docs/active/wi-cfis-scoping/` before merge — read the scoping doc + sample-query writeup before any code
- **New code lives at:** `src/lobby_analysis/campaign_finance/wi/` (new module — does not exist yet)
- **Tests live at:** `tests/test_wi_campaign_finance_*.py`
- **HTTP cassettes / fixtures:** `tests/fixtures/wi_campaign_finance/` (committed)
- **Outputs:** `releases/wi/campaign_finance/` (committed TSVs + README); per-query JSON cache lives under `data/campaign_finance/WI/` (gitignored, symlinked to `~/data/lobby_analysis/campaign_finance/WI/`)
- **Plan reference:** `docs/active/wi-cfis-scoping/plans/wi_campaign_finance.md` (this file)

---

## Phase 0 — Wait for FTM Institute expanded-access review

**Goal:** Stay quiet on the API until the Institute's automatic review clears Dan's account for expanded access. The quota was tripped during scoping; the response said review is automatic with a 2-business-day SLA.

1. **Do NOT run any FTM API queries** until expanded access is confirmed. Additional traffic against the throttled account risks deprioritization.
2. **Watch the inbox** at the account email (Dan's Canary email) for the Institute's review message.
3. **When it arrives**, reply with the context drafted in [`../results/20260603_ftm_sample_query_lemahieu.md`](../results/20260603_ftm_sample_query_lemahieu.md) §6 — Corda Democracy Fellowship + open-source + non-commercial + planned use across 5-8 priority states over the next few weeks + attribution per CC BY-NC-SA 3.0 US.
4. **If no contact arrives by end-of-business-day 3-5**, send a proactive status-check email to `info@opensecrets.org`. Dan has the draft (also in the sample-query writeup §6).
5. **Confirm expanded access** with one small probe query against the WI 2024 candidate list before starting Phase 1.

**Deliverable:** zero code. Just the green light on the API key.

---

## Phase 1 — FTM ingest + crosswalks + materialize

**Goal:** Pull WI 2024 + 2025-2026 cycle contributions for all sitting WI state legislators (~165 entities × 2 cycles, ~few hundred K transactions estimated); build the three crosswalks back to the chain; ship `releases/wi/campaign_finance/`.

### 1.1 — Setup

6. **Cut the worktree.** `git worktree add .worktrees/wi-campaign-finance -b wi-campaign-finance main`. Add `data/` symlink (`ln -s ~/data/lobby_analysis data`) and `.env.local` symlink per the `using-git-worktrees` skill.
7. **Seed branch docs.** `docs/active/wi-campaign-finance/` with `RESEARCH_LOG.md`, `convos/`, `plans/`, `results/`. Copy this plan as the originating reference; the wi-cfis-scoping convo is the originating conversation.
8. **`uv add httpx pydantic`** (FTM client deps). Confirm `pandas` already in the project.

### 1.2 — Build the FTM client (TDD)

9. **Write failing tests** in `tests/test_ftm_client.py`:
   - `test_client_builds_canonical_query_url` — given filter kwargs `(state="WI", year=2024, c_t_eid=3073941, gro="d-id")`, returns the URL with params in deterministic order and `APIKey=` masked from logs.
   - `test_client_parses_known_response_shape` — given a hand-saved JSON fixture (LeMahieu 2022 cycle, page 0, recorded during scoping at `/tmp/ftm_lemahieu_txns_p0.json` — copy into `tests/fixtures/wi_campaign_finance/`), parses into typed `FTMTransaction` records with the 15 fields documented in scoping §3.
   - `test_client_raises_on_quota_error` — given a fixture with the `{"error":"This account has reached its free API call limit..."}` shape, raises a typed `FTMQuotaExceeded` exception (distinct from `FTMInvalidKey` etc.).
   - `test_client_iterates_pages` — given a multi-page fixture sequence, iterates correctly using the `paging.totalPages` field.
10. **Run tests, confirm RED, commit RED.**
11. **Implement `src/lobby_analysis/campaign_finance/wi/ftm_client.py`** with `FTMClient` class (sync `httpx`, hand-built URL, typed pydantic models for response shapes). Minimal implementation to GREEN the tests. Commit GREEN.

### 1.3 — Pull WI 2024 + 2025-2026 cycle candidate lists

12. **Write failing tests** in `tests/test_ftm_wi_candidates.py`:
   - `test_candidate_list_contains_known_legislator` — given a recorded fixture for `?s=WI&y=2022&gro=c-t-id`, returns at least one record with `Candidate: "LEMAHIEU, DEVIN"` / `c-t-eid: "3073941"` / `Office_Sought: "SENATE DISTRICT 009"`.
   - `test_candidate_list_filters_to_state_offices` — excludes federal / local offices; only state Senate + Assembly candidates.
13. **Run, RED, commit.**
14. **Implement `fetch_wi_candidates(client, year)`** that pages through `?s=WI&y=<year>&gro=c-t-id` and returns a list of typed `FTMCandidate` records. Cache JSON pages under `data/campaign_finance/WI/raw_candidates_<year>/page_<N>.json` for resume-safety (per the experiment-data-integrity policy).
15. **Run, GREEN, commit.**
16. **Execute** for `y in {2022, 2024, 2026}` (covers WI's 4-year senate terms + 2-year assembly terms across the chain's 2025-2026 biennium). Materialize `data/campaign_finance/WI/candidate_directory.tsv` as the union with stable `c-t-eid` as the primary key. Write `results/<DATE>_wi_candidate_directory.md` documenting row counts per cycle, party breakdown, chamber breakdown.

### 1.4 — Build the lawmaker-side crosswalk (FTM `c-t-eid` ↔ `ocd-person/...`)

17. **Read the chain.** `releases/wi/chain/WI_chain_2025.tsv` has 132 unique `sponsor_lawmaker_id` values (`ocd-person/<uuid>`) with `sponsor_lawmaker_name` strings.
18. **Read the Plural Policy lawmaker roster.** The chain release's README points at the Plural Policy bulk CSV the chain used; that dump has additional metadata (party, chamber, district, possibly external identifiers).
19. **Probe OpenStates first.** `pyopenstates` or the OpenStates API's `Person.identifiers[]` field may already contain a `ftm_c-t-eid` or `nimsp_id` identifier per legislator. If yes, the crosswalk is one query.
20. **If OpenStates is silent**, build the crosswalk manually:
    - Match by `(family_name, chamber, district)` against the FTM candidate directory built in §1.3.
    - Use the chain's `sponsor_lawmaker_name` surname-disambiguation work done in `docs/historical/wi-allocation-matrix/results/20260602_unknown_chamber_audit.md` (the 3 prefix-disambiguated B./L./J. cases).
    - Hand-resolve any residual ambiguity against ballotpedia.org candidate pages.
21. **Write failing tests** in `tests/test_lawmaker_crosswalk.py`:
   - `test_lemahieu_resolves` — `ocd-person/be7a6f06-6d2c-49d1-908d-451adef564eb` ↔ FTM `c-t-eid=3073941`.
   - `test_all_chain_sponsors_resolved` — every distinct `sponsor_lawmaker_id` in the chain TSV resolves to an `c-t-eid` OR is explicitly listed in a `lawmaker_unresolved.tsv` exclusion file with a reason. **165-legislator coverage target.**
22. **Materialize** `releases/wi/campaign_finance/wi_lawmaker_crosswalk.tsv` with columns `(ocd_person_id, family_name, given_name, chamber, district, party, ftm_c_t_eid, source_method, last_verified_date)`.

### 1.5 — Pull contributions per lawmaker per cycle

23. **Write failing tests** in `tests/test_ftm_wi_contributions.py`:
   - `test_contributions_for_lemahieu_2022_match_known_aggregates` — sum of all contribution amounts matches the cycle aggregate (2,803 records / $609,272 from the scoping sample).
   - `test_contributions_have_canonical_donor_entity` — every row has both `Original_Name` (raw filer) and `Contributor` (FTM canonical entity with `d-eid`).
   - `test_resume_skips_already_pulled` — re-running against an already-populated cache directory is a no-op (per experiment-data-integrity policy).
24. **Implement `fetch_wi_contributions(client, c_t_eid, year)`** that pages through `?c-t-eid=<eid>&y=<year>&gro=d-id` and returns the full transaction list. Cache JSON pages under `data/campaign_finance/WI/raw_contributions/<c_t_eid>/<year>/page_<N>.json`. Each cache file includes the exact request URL (with `APIKey` masked) + timestamp in a metadata wrapper.
25. **Execute for the priority set:**
   - `c-t-eid` ∈ {all 165 sitting WI legislators from §1.3}
   - `year` ∈ {2022, 2024, 2026}
   - This is the volume burst that consumes the expanded API quota. Confirm Phase 0 cleared before starting.
26. **Materialize** `releases/wi/campaign_finance/WI_contributions_2022_2026.tsv` with the 15-field FTM transactional schema (see scoping §3). Sort deterministically; include a per-row `pulled_at` timestamp for provenance.

### 1.6 — Build the principal-side crosswalk (chain `principal_id` ↔ FTM `d-eid`)

27. **Aggregate distinct donors** from `WI_contributions_2022_2026.tsv` grouping by `(Contributor, d-eid)`. This is the universe of FTM-known donor entities that gave to WI state legislators.
28. **Match against `releases/wi/WI_principals.tsv` (1,108 entries, 525 chain-active).** Strategy:
    - **Exact-string match** on canonicalized names (lowercase, strip punctuation, strip suffixes like "Inc."/"LLC"/"Group").
    - **Manual review** of the residual unmatched principals against FTM's `Contributor` field. The scoping doc's principal-side join section sized this as ~525-row review; FTM's canonicalization makes most matches obvious (e.g., "WEC Energy Group, Inc." ↔ "WISCONSIN ENERGY CORP" via FTM eid=9524).
29. **Write failing tests** in `tests/test_principal_crosswalk.py`:
   - `test_wec_resolves` — `WI_principals.tsv.principal_id` for WEC Energy Group ↔ FTM `d-eid=9524`.
   - `test_all_sb28_coalition_resolved` — the 29 SB 28 principals from `docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md` all resolve to either an FTM `d-eid` OR are explicitly listed in an exclusion file with a reason (e.g., ATC Management's likely absence from candidate-side contributions).
30. **Materialize** `releases/wi/campaign_finance/wi_principal_crosswalk.tsv` with columns `(principal_id, principal_name, ftm_d_eid, ftm_canonical_name, match_method, ambiguity_notes, last_verified_date)`.

### 1.7 — Build the lobbyist personal-contribution slice (FTM `Contributor` name-match for individuals)

31. **Filter `WI_contributions_2022_2026.tsv` to `Type_of_Contributor = "Individual"`.** This is the donor universe for the lobbyist personal-contribution leg.
32. **Match against `releases/wi/WI_lobbyists.tsv` (773 entries)** by canonicalized name (`(family_name, given_name)` after stripping middle initials and suffixes). Use FTM's `Occupation` and `EmployerName` fields (where populated for > $200 contributions) as disambiguators.
33. **Cross-check timing** against §13.625 windows. A contribution by a registered lobbyist outside the legal window is either (a) misclassified, (b) made to a candidate not subject to the restriction (local/non-partisan/national), or (c) a §13.625 violation. Default v1 behavior: emit the row + a `wi_window_status` column with values `{within_window, outside_window, n/a_unrestricted_office}`.
34. **Materialize** `releases/wi/campaign_finance/wi_lobbyist_contributions.tsv` with columns `(lobbyist_id, lobbyist_name, ftm_contributor_d_eid, recipient_c_t_eid, recipient_name, amount, date, wi_window_status, source_contribution_row_id)`.

### 1.8 — Materialize chain-v2 (chain + $-flow)

35. **Compose** `WI_chain_2025.tsv` × `wi_principal_crosswalk` × `WI_contributions_2022_2026.tsv` to produce, per `(semester, principal, lobbyist, bill, sponsor)` chain row, a companion view of donations from that principal to that sponsor.
36. **Decision point** for the join shape: per-chain-row appending or a separate sidecar TSV. Default v1: separate sidecar `releases/wi/campaign_finance/WI_chain_dollar_flow_2025.tsv` keyed on `(principal_id, sponsor_lawmaker_id)` with aggregate `(total_$, n_contributions, first_date, last_date)`. Consumers join to the chain TSV on the principal-sponsor pair.
37. **Spot-check** the WEC → LeMahieu cell against the scoping evidence: should show WEC Energy Group PAC's $2K contributions to LeMahieu across cycles.

### 1.9 — README + attribution

38. **Write** `releases/wi/campaign_finance/README.md` documenting: source = FTM API; license = CC BY-NC-SA 3.0 US; mandatory attribution to "National Institute on Money in State Politics"; coverage years; row counts per TSV; the schema for each TSV; the three crosswalks; known limitations (no `Conduit` / no `Comment` / FTM-cycle date convention != calendar year).
39. **Update the repo-level `README.md` acknowledgments section** to credit FTM alongside Plural Policy + IRW Accountability Project.

### 1.10 — Phase 1 writeup

40. **Write** `docs/active/wi-campaign-finance/results/<DATE>_phase_1_ingest_and_chain_join.md` summarizing: API queries executed + quota cost; row counts per TSV; crosswalk coverage (% of chain principals / sponsors / lobbyists resolved); the SB 28 coalition's full $-flow spot-check against LeMahieu; known FTM gaps + their downstream impact (if any).

---

## Phase 2 — Selenium-Sunshine gap-fill (CONDITIONAL)

**Goal:** Fill ONLY specific gaps Phase 1 surfaces — not duplicate the FTM ingest. Triggered only if downstream consumers ask for `Conduit`, `Comment`, `SegregatedFundFlag`, `EmployerAddress`, or any other CFIS field FTM drops.

**Defer entry decision to post-Phase 1.** If Phase 1's writeup shows full coverage of the chain's $-flow needs, skip Phase 2 entirely.

If triggered:
41. **Port IRW's `scrape_wi_contribs.R`** (R + Selenium, against old CFIS) to Python + Playwright against the new Sunshine UI at `https://wi.sunshine.civera.com/`. The export-icon path (Transaction Search → CSV) is documented; the 65K-row cap requires batched iteration.
42. **Pull ONLY the specific committees + fields** Phase 1 needs gap-fills for. Do NOT duplicate the FTM-already-covered transaction set.
43. **Cross-validate** against the FTM Phase 1 results on overlap rows. Document any drift in a results writeup.

---

## Phase 3 — Finish branch and PR

44. **Run full pytest suite.** Confirm new tests pass + zero regressions on the existing baseline (1,636 pass + 3 pre-existing failures from wi-allocation-matrix merge).
45. **Run `ruff check`.** Fix any F-class violations.
46. **Run `finish-convo` skill** for the final session — convo summary + RESEARCH_LOG entry + STATUS.md one-liner + commit + push.
47. **Run `finishing-a-development-branch` skill** — pre-merge code review via `nori-code-reviewer`, address blockers, open PR. The chain's $-flow leg becomes part of the permanent record on main.

---

## Testing Plan

I will write tests that exercise observable behavior, not implementation details:

- **FTM client tests** use recorded JSON fixtures (saved during scoping at `/tmp/ftm_lemahieu_*.json`; copy into `tests/fixtures/wi_campaign_finance/`) to confirm the client parses the documented 15-field schema and surfaces typed errors for the known error responses (quota-exceeded, invalid-key).
- **Candidate-list tests** confirm we can find LeMahieu's `c-t-eid=3073941` in the WI 2022 cycle list, against a recorded fixture page.
- **Crosswalk tests** confirm specific known mappings (LeMahieu → 3073941, WEC Energy → 9524) and confirm 100% chain-sponsor coverage with explicit exclusion lists for residuals.
- **Contribution-ingest tests** confirm aggregate sums match known cycle totals from the scoping evidence (LeMahieu 2022 = 2,803 records / $609,272), and confirm resume-from-checkpoint is safe (per experiment-data-integrity policy — re-running an interrupted pull is a no-op against an already-cached cell).
- **Lobbyist-slice tests** confirm a known lobbyist's name resolves and that the §13.625 window classification produces the right `wi_window_status` value for a fixture contribution with known date + recipient office type.
- **Chain-join sidecar tests** confirm that the WEC → LeMahieu cell shows up with the expected aggregate from Phase 1.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Edge cases the implementing agent must handle

- **FTM cycle convention.** FTM groups contributions into election cycles, so a `y=2022` query returns contributions dated from the previous cycle's end through 2022's general election (e.g., the WEC PAC contribution to LeMahieu dated 2019-05-04 is counted in his 2022 cycle). Document this in the README; do not assume `y=` is calendar year.
- **Multi-cycle legislators.** Sitting senators serve 4-year terms across multiple cycles. LeMahieu is in the 2022 cycle list but not the 2024 list. Iterate `y` to cover all elections the sitting cohort was on.
- **Withdrawn / lost candidates appearing in the candidate list.** `?gro=c-t-id` returns everyone who FILED, not just winners. Filter on `Election_Status: "Won-General"` to limit to sitting legislators if that's the chain's lawmaker set.
- **FTM canonicalization that the implementing agent may dislike.** "WEC ENERGY GROUP PAC (WEC PAC)" maps to canonical entity "WISCONSIN ENERGY CORP" (`d-eid=9524`) — FTM's choice, not ours. The `wi_principal_crosswalk.tsv` should record both FTM's canonical name and our chain's preferred name (`WI_principals.tsv.name`) so consumers can choose.
- **`d-llink` is partial (~5%).** Do NOT rely on it as the primary lobbying-flag. The lobbyist-side slice uses `WI_lobbyists.tsv` name-match as the primary signal; `d-llink` is a confirming secondary signal at best.
- **WI conduit PACs that lobbying principals control.** WEC's flow goes through WEC PAC; ATC Management may flow through an industry association. The principal-side crosswalk should record both direct-entity matches and known-conduit matches with a `match_via` column (`{direct, conduit, parent_org}`).
- **Negative contribution amounts.** LeMahieu's top-25-ascending sample showed his own committee refunding -$5,800 to himself. The schema permits negatives; aggregation must respect them.
- **WI §11.1101 corporate-contribution restrictions post-2015.** Direct corporate contributions to candidate committees are restricted; most corporate flow is via PACs/conduits. Expect very few `Type_of_Contributor: "Non-Individual"` rows that are NOT PAC-shaped.
- **Quota-exceeded retries.** Even with expanded access, FTM may rate-limit at higher volumes. The client should detect the `FTMQuotaExceeded` shape, log clearly, and stop — do NOT retry into a hard fail.

---

## Validation / what success looks like

- All ~165 sitting WI legislators resolve to an FTM `c-t-eid`.
- All 525 chain-active principals resolve to an FTM `d-eid` OR are listed in `wi_principal_unresolved.tsv` with a reason (the exclusion list is short and explanatory).
- WEC → LeMahieu cell shows up in `WI_chain_dollar_flow_2025.tsv` with the $2K contributions from the scoping evidence visible.
- A spot-check on a different chain row (say, Wisconsin Realtors Association → some Assembly sponsor) shows a non-zero $-flow if any was reported in CFIS for the same cycle window.
- Full pytest suite passes, zero regressions on baseline, attribution lives in the right surfaces per the FTM TOS.

---

**Testing Details:** Tests assert observable behavior — aggregate sums match known totals, specific known IDs resolve to specific known canonical entities, resume-from-checkpoint is idempotent. No tests on pydantic class structure or type signatures; no tests that only verify mocks. Each phase's GREEN bar requires unit-test pass AND a manual spot-check of 2-3 cells against the chain's known signal (WEC → LeMahieu, Xcel → LeMahieu, AT&T → LeMahieu).

**Implementation Details:**
- New module: `src/lobby_analysis/campaign_finance/wi/` (`ftm_client.py`, `candidates.py`, `contributions.py`, `lawmaker_crosswalk.py`, `principal_crosswalk.py`, `lobbyist_slice.py`, `chain_dollar_flow.py`, `cli.py`).
- FTM client: sync `httpx`; never log the `APIKey` parameter; raise typed exceptions for the known error shapes.
- Output schemas pinned in this plan; column order is part of the contract.
- Per-query JSON caching under `data/campaign_finance/WI/` (gitignored, symlinked) enables resume-safe re-runs without re-spending API quota.
- All raw + processed output TSVs go to `releases/wi/campaign_finance/` (committed); the `data/` cache is a build artifact.
- FTM attribution propagates to: `releases/wi/campaign_finance/README.md`, repo-level README acknowledgments, per-TSV header comment block, any results doc that quotes dollar figures.
- Phase 2 (Selenium-Sunshine) stays out of `pyproject.toml` deps unless Phase 1 surfaces a gap that triggers it.

**What could change:**
- **FTM expanded-access review may impose tighter limits than expected.** If the Institute grants only an incremental quota bump (not unrestricted), Phase 1 may need to be reshaped into smaller batches with multi-day pauses. Worth confirming Phase 0 ends with a clear quota number.
- **OpenStates `Person.identifiers[]` may not have FTM eids.** Manual lawmaker crosswalk is the fallback; ~165 rows is tractable but not zero work.
- **The Plural Policy lawmaker roster may have changed** between the chain's 2026-05-30 pull and this branch's start. Re-pull if drift is suspected.
- **WI may introduce new statutory restrictions** on lobbyist contributions during the project window (unlikely but possible — the §13.625 windows are politically contested).
- **Cosponsor parsing** (parent plan's Refinement #2) may land on a sister branch in parallel. The lawmaker-side crosswalk is sized for "all sitting WI legislators" (~165), not just primary sponsors (132), so cosponsor parsing later does not trigger rework here.

**Questions:**
- **Q1 (Phase 0):** what does FTM's expanded-access grant look like operationally — unlimited, daily cap, monthly cap? Confirm at Phase 0 end before sizing Phase 1 batches.
- **Q2 (Phase 1 §1.4):** does OpenStates' `Person.identifiers[]` already contain FTM eids for WI legislators? Worth a 5-min probe before committing to manual crosswalk.
- **Q3 (Phase 1 §1.7):** how should `wi_window_status = "outside_window"` rows be presented to downstream consumers — emit with a flag, or filter out by default? Default plan = emit + flag; consumer decides.
- **Q4 (Phase 1 §1.8):** sidecar TSV vs in-place chain TSV append? Default plan = sidecar (keyed on `(principal_id, sponsor_lawmaker_id)` aggregate); chain TSV stays untouched.
- **Q5 (out of scope, flag-only):** cross-state generalization. The FTM API is 50-state; the chain ingest is currently WI-specific. When the next priority state lands, design the module path as `src/lobby_analysis/campaign_finance/<state>/` (parallel to WI) vs a generic shared core. YAGNI for v1, but worth flagging for the v2 conversation.

---

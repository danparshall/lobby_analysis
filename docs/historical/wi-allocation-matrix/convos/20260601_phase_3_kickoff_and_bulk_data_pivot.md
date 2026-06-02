# Phase 3 kickoff + bulk-data pivot

**Date:** 2026-06-01
**Branch:** `wi-allocation-matrix`
**Plan executed:** [`plans/wi_allocation_matrix.md`](../plans/wi_allocation_matrix.md) steps 32–42 (Phase 3 complete)
**Originating handoff:** [`convos/20260531_phase_2_ipf_design_and_execution.md`](20260531_phase_2_ipf_design_and_execution.md) (Phase 2 wrapped at step 31, handoff said "pause immediately at step 32 to ask Dan Q1")
**Results doc:** [`results/20260601_phase_3_chain.md`](../results/20260601_phase_3_chain.md)

## Summary

Phase 3 — bill sponsorship loader + end-to-end chain composer — landed in a single session with 20 new tests (13 + 7), 5 commits, zero regressions, and a materialized 115,229-row chain TSV. The bigger story is the bulk-data pivot. The plan literal at step 33 named `pyopenstates` as the default bill-sponsorship data source; three findings from probing the API path before writing tests argued for abandoning it:

1. OpenStates v3 enforces an API key server-side (no anonymous probe possible).
2. The free tier's rate limit is 10 req/min + 500 records/day, not the "1 rps" Dan initially remembered — tighter than the ~1,000-bill workload required.
3. `pyopenstates` swallows HTTP status + headers (`raise APIError(response.text)` only), making rate-limit telemetry invisible.

Dan then pointed at Plural Policy's bulk session-data downloads, which proved decisive: 15 normalized CSV tables for WI 2025 plus a separate legislators dataset (`wi.csv`) with `ocd-person/...` IDs. That's a structural upgrade over the JSON dump even setting aside the rate-limit issue — the structured `bill_sponsorships.csv` includes `person_id` for 99.8% of sponsorship rows, whereas the JSON's `sponsors` field is bare name strings only.

The pivot landed Q1, Q3, and the `sponsor_lawmaker_id` resolution question (asked separately) all together: bulk CSV instead of API, primary-sponsors-only (cosponsors deferred — confirmed structurally absent from both JSON and CSV), and `sponsor_lawmaker_id = ocd-person/...` instead of name strings. The 60 collective-entity sponsors (Joint Legislative Council × 26, Law Revision Committee × 34) round-trip via `is_collective=True` + name-as-id.

## Topics Explored

### Plan step 32 — Q1 boundary

- Read plan + Phase 2 convo for trajectory before asking.
- Surfaced Q1 (OpenStates vs direct scrape) as three options. Dan picked (c): OpenStates first, fall back if coverage <50%. Default recommendation.

### OpenStates API probing (path-not-taken)

- `pyopenstates` 2.0.0 installed via `uv add pyopenstates`.
- First call without `OPENSTATES_API_KEY` set: server returns 401-equivalent JSON error. So "defer auth" option from a follow-up question doesn't work — OpenStates v3 enforces the key.
- Dan registered + dropped key in `.env.corporate`. Initial typo `OPENSTATES_API_KEEY` (three E's) caught + flagged before fix.
- First authenticated call: `APIError: exceeded limit of 10/min: 11`. Translation: the key was at 11 requests in the current minute when I called, against a cap of 10. Dan said he hadn't used the key, leaving the 11 unexplained — possibly a shared `.env.corporate` key.
- Inspected `pyopenstates` source: line 88 throws away HTTP status code and headers, only re-raising `response.text`. Library opacity = no rate-limit telemetry visible.

### Pivot: bulk CSV via Plural Policy

- Dan pointed at `data/bills/WI/2025/`: `WI_2025_json_*.zip` (38 MB) already downloaded.
- Probed JSON: 100% bill-identifier coverage (all 1,000 unique `Senate Bill X` / `Assembly Bill X` strings in `WI_principal_bill_efforts.tsv` resolve cleanly to OpenStates short form `SB X` / `AB X`).
- JSON's structured `sponsors` field: only `classification='primary'` rows across all 28,047 entries — **cosponsors are NOT in the structured field**. They appear exclusively in `bill_actions[*].description` text ("Introduced by Senators X, Y, Z; cosponsored by Representatives A, B, C").
- JSON's `sponsors` field has bare name strings only — no `ocd-person/...` IDs. Surfaced to Dan as a chain-schema decision (name-as-id vs pull legislators dataset).
- Dan then dropped a CSV version: `WI_2025_csv_*.zip` (24 MB) plus the legislator-csv `wi.csv` (148 KB). CSV bundle has 15 normalized tables.
- Re-probed CSV: same primary-only-classification finding, but `bill_sponsorships.csv` includes `person_id` (`ocd-person/...`) for 27,987 of 28,047 rows. The 60 unlinked rows are organizational entities (Joint Legislative Council × 26, Law Revision Committee × 34).
- `wi.csv` ships 132 WI legislators (99 Assembly + 33 Senate; 72 Republican + 60 Democratic) with party / chamber / district. Joined on `person_id` to enrich sponsor rows.
- Committee assignment: `bill_actions.csv` has structural linkage to `organizations.csv` via `organization_id`, but on referral-committee rows the linked org is the **chamber**, not the specific committee. Committee name itself is only in `description` text — regex-parseable.

### Phase 3 v1 scope decisions

Asked + answered with Dan, in order:

1. **Q1 (OpenStates vs scrape):** (c) OpenStates first, fall back if needed → resolved by bulk-data pivot.
2. **Library:** `uv add pyopenstates` → reverted via `uv remove` once bulk path won. Briefly side-affected dev deps (pytest/ruff) being removed too; restored via `uv sync --extra dev`.
3. **API key location:** Defer auth → didn't work; key ended up in `.env.corporate` (typo fixed).
4. **`sponsor_lawmaker_id`** (added when probe revealed JSON had no person IDs): A (name-as-id for v1) → upgraded to (B, real ID) once CSV bundle's `person_id` field was found.
5. **Cosponsor scope:** A (primary-only) → confirmed for v1. Cosponsor parsing is Phase 3+ refinement (text regex over action descriptions).
6. **JSON vs CSV format:** CSV won on structural grounds (person_id, normalized tables, separate legislators file).
7. **Bucket filter (implicit Q3 default):** Legislative Bills/Resolutions only for v1; Topics Not Yet Assigned (2,327 effort rows) deferred. Surfaced in results doc.

### Implementation

- **Phase 3.1 (RED):** 13 tests for legislature loader — bill ID normalization (5), session bill count (2), SB 3 metadata spot-check (5), collective sponsor flagging (1).
- **Phase 3.2 (GREEN):** `legislature.py` — `normalize_bill_id` + `load_bill_sponsorships`. 13/13 pass; hand-spot-checked AB 156, AB 112 (collective), AJR 22 against raw CSVs.
- **Phase 3.3 (RED):** 7 tests for chain composer — plan-required trio (DoorDash nonempty + row count = 78 + confidence dist) plus 4 supporting assertions.
- **Phase 3.4 (GREEN):** `chain.py` — `compose_chain` joins allocation matrix × bill_efforts × bill_metadata into one row per (semester, principal, lobbyist, bill, sponsor). 7/7 pass; one test had a numpy-int-vs-Python-int mistake (test-code bug, not impl bug) — fixed.
- **Phase 3.5:** `materialize_chain` + CLI subcommands (`allocation`, `chain`). Refactored single-command CLI to subcommands without breaking existing invocations. Output: `WI_chain_2025.tsv`, 115,229 rows.

### Verification

- **Coverage check (plan §217 bar ≥80%):** 97.9% — 3,947 of 4,030 unique legislative effort rows produce ≥1 chain row.
- **DoorDash worked example:** 78 rows exact (3 lob × 4+9 sponsors × 2 semesters). Arithmetic spot-checked: hours_comm 37.81 + hours_other 9.21 = 47.01; × 0.21 = 9.87 = `modeled_hours` field. ✓
- **Full suite:** 1,630 passed, 0 regressions, same 3 baseline `test_pipeline.py` failures listed in plan §234.

## Provisional Findings

- **The bulk CSV path is strictly better than the API path for this workload.** Same data (Plural Policy = OpenStates), structured `person_id` join key, no rate limit, no auth. The plan's API default was written before the bulk-download path was discovered.
- **Cosponsors are not in any structured data anywhere (JSON or CSV).** They live only in `bill_actions.description` strings. Cosponsor support requires text parsing — manageable but real work, deferred to Phase 3+.
- **Pettack (lobbyist 11072) produces zero chain rows.** Her 6 SAA-family principals didn't file legislative-bucket bill efforts. The `aggregation_flagged` confidence label propagated through Phase 2's allocation matrix correctly but is invisible in the v1 chain (legislative-only). Different axes — labeling lives on lobbyist, attribution lives on principal.
- **Top sponsors are all Assembly Republicans.** Mursau, O'Connor, Dittrich, Kreibich, Behnke, Knodl, Gundrum, Murphy, Wichgers, Melotik. Likely confound from per-bill primary sponsor counts (Assembly bills have more named primaries on average), not a clean "most-lobbied" signal. Per-bill-normalization would tell a different story.

## Decisions Made

- **Bulk CSV path** instead of `pyopenstates` / OpenStates API. `pyopenstates` removed from dependencies.
- **`sponsor_lawmaker_id` = `ocd-person/...`** for individual sponsors; **= name string** for collective entities (`is_collective=True`).
- **Primary sponsors only for Phase 3 v1.** Cosponsor parsing deferred.
- **Legislative Bills/Resolutions bucket only for Phase 3 v1.** Topics Not Yet Assigned (2,327 effort rows), Budget Bill Subjects (856), Administrative Rulemaking (127) deferred.
- **Semester added** to chain row schema (beyond plan literal) — same tuple appears in both H1 and H2 with different hours and percents.
- **`modeled_hours` is the single value** `(hours_comm + hours_other) × (filed_percent / 100)`. Plan literal said "modeled_hours" singular.
- **Chain emits 0 rows for 16 bills with zero structured sponsors.** Skipped, not emitted with null sponsor; diagnostic candidate for Phase 3+.

## Commits this session (on `wi-allocation-matrix`)

| SHA | What |
|---|---|
| `4b71c03` | `phase 3.1: RED tests for WI legislature loader` |
| `f830230` | `phase 3.2: WI legislature loader GREEN` |
| `67f9c30` | `phase 3.3: RED tests for WI chain composer` |
| `cfc8342` | `phase 3.4: WI chain composer GREEN` |
| `a64f710` | `phase 3.5: WI chain materialize + CLI subcommand` |

(Docs commit pending.)

## Open Questions

- **Q3 (Phase 3+ candidate):** Topics-Not-Yet-Assigned bucket (2,327 effort rows, 31.7% of total) — emit with `topic_no_bill_yet` flag, or leave out as v1 does?
- **Cosponsor parsing (Phase 3+ candidate):** Half-day of regex work over `bill_actions.description`; doubles/triples chain rowcount; adds attribution to cross-chamber cosigners.
- **Per-cell row-residual exposure (Phase 2 carryover):** Would let downstream consumers distinguish tightly-pinned `ipf_fit` rows from over-attribution-absorbing ones.
- **Per-bill-normalization for "top sponsors":** Current top-10 is dominated by multi-author Assembly bills. A normalized variant would tell a different story about real lobbyist→legislator attribution.
- **Q4 (Phase 4 boundary):** CFIS investigation scope — 0.5-day timebox or open-ended? Unchanged from Phase 2.

## Handoff for next session

Phase 3 lands the chain. Phase 4 (CFIS scoping) and Phase 5 (PR) remain.

- **If continuing to Phase 4:** read this convo + `results/20260601_phase_3_chain.md` for the chain shape. Phase 4 is investigation-only (no scrape this branch) — characterize WI CFIS schema, determine join keys back to the chain's `sponsor_lawmaker_id` space, write `results/YYYYMMDD_phase_4_cfis_scoping.md` with recommendation for a follow-up `wi-campaign-finance` branch.
- **If continuing to Phase 5:** read the plan's §234 baseline failures list. Run `ruff check`. Open PR.
- **If Dan decides Phase 3+ refinements come first:** Q3 (TNYB bucket) is the most concretely-defined refinement and would fill out the chain's coverage of the 31.7% of effort rows currently unaccounted for.

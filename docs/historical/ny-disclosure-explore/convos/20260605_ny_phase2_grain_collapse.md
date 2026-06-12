# NY Phase 2 — grain-collapse + column map

**Date:** 2026-06-05
**Branch:** `ny-disclosure-explore`

## Summary

Picked up the Phase-1 handoff and built the first (load-bearing) pieces of Phase 2: the grain-collapse dollar-conservation guard and the per-dataset column map. Before writing the guard, I verified the plan's amendment-dedup assumption against live data — and found it wrong. The plan said *"keep latest `filing_type` per `form_submission_id`"*; probes showed that's a no-op (no `form_submission_id` carries both Original and Amendment) and that an amendment is a *separate* submission with its own id that supersedes the prior one. Summing compensation over distinct `form_submission_id` therefore double-counts every superseded version — a 4.1× overcount on the worst real example — and the plan's conservation test (sum over distinct `form_submission_id` on both sides) would have passed while still wrong.

A second probe confirmed `form_submission_id` is monotonic with submission order (amendment ids strictly exceed their superseded original's), so `max(form_submission_id)` per business key is the latest version — no filed-date column needed. The verified dedup rule is: per business key `(reporting_year, reporting_period, principal_lobbyist, beneficial_client, contractual_client_name)`, keep only `max(form_submission_id)`; drop superseded submissions *before* collapsing to bill grain.

Built `io/ny/grain.py` (`collapse_to_filing_grain`) and `io/ny/columns.py` (`normalize_columns`) test-first (TDD). A code review caught a real reachable bug — a NaN in any business-key column made pandas `groupby` drop that group and silently lose the filing's dollars (the exact non-conservation the module prevents); fixed with `dropna=False` and a regression test. Full suite green (1659 passed; only the 3 pre-existing #38 `scoring` reds remain).

## Topics Explored

- Phase-1 handoff, plan, and Phase-0 schema-verification findings.
- Amendment-dedup semantics (`form_submission_id` vs business key) via two live read-only probes.
- TDD build of the grain-collapse step and the per-dataset column map.
- Adversarial code review of the conservation guard.

## Provisional Findings

- Plan's per-`form_submission_id` dedup is a no-op; amendments are separate, superseding submissions. Within-dataset double-count is severe (4.1× on `RIDDETT ASSOCIATES` / `TRIAL LAWYERS ASSN`). Details + evidence: [`../results/20260605_ny_amendment_double_count.md`](../results/20260605_ny_amendment_double_count.md).
- `form_submission_id` is monotonic with submission order (verified on 5 worst-case keys), so `max(form_submission_id)` = latest version.
- Business key with `contractual_client_name` yields exactly one Original per key (no evidence it's too coarse).
- NaN in a business-key column was a silent dollar-loss path in the first implementation (found in review, fixed).

## Decisions Made

- **Dedup key = business key, keep `max(form_submission_id)`** (supersedes the plan's `form_submission_id` rule). Verified ordering first per Dan's call.
- **Tracked on GH #37** (not a new issue), per Dan's call — within-dataset amendment double-count documented as a comment alongside the cross-dataset concern.
- **`bill_id` derivation deferred to the parser step** — the column map does name-normalization only. Grain-collapse consumes a `bill_id` the parser will add.
- **Column map scoped to the two core datasets** (`client_semiannual`, `lobbyist_bimonthly`) the 2025 build uses; other 4 deferred.

## Results

- [`../results/20260605_ny_amendment_double_count.md`](../results/20260605_ny_amendment_double_count.md) — finding + verified rule.
- `../results/ny_amendment_probe_2025.json`, `../results/ny_amendment_ordering_probe_2025.json` — raw probe evidence.
- Code: `src/lobby_analysis/io/ny/grain.py`, `src/lobby_analysis/io/ny/columns.py`; tests `tests/test_ny_grain.py` (9), `tests/test_ny_columns.py` (4); probe scripts `scripts/ny_probe_amendments.py`, `scripts/ny_probe_amendment_ordering.py`.

## Open Questions

- **`bill_id` State-Bill scoping (for the parser step).** Phase-0's `starts_with(level_of_government, 'State')` filter would wrongly drop a `State Bill` row filed at `Both (State and Municipal)` level — the committed fixture shows exactly this (`S550-A` at `Both`). Likely the correct discriminator is `focus_type == 'State Bill'` alone (the focus type already says it's a state bill); verify when building the parser.
- **Comp-replication assumption.** Grain-collapse assumes `filing_compensation` is identical across a filing's rows (takes first on dedup). True for the verified shape; not runtime-asserted.
- **Other 4 datasets' column maps** (registration, disbursement, public_corp ×2) — public-corp universe has no contractual/beneficial-client triad; needs its own modeling decision before folding into the canonical schema.

## Next Steps

- Parser step: derive `bill_id` (resolve the State-Bill/level question), parse entity + filing/linkage datasets to Pydantic models against Phase-0 fixtures, then `materialize_ny` + CLI (Phase 2 remainder).
- Then Phase 3 (real 2025 pull + `releases/ny/`) and Phase 4 (chain + Open States join, where `comp_per_bill` even-split + its conservation test #5b live).

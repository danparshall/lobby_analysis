# NY Phase 2 — parser step (bill_id derivation + entity/filing parsers)

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Picked up the Phase-2 parser step from the prior session's handoff. The session's
substantive decision was the **State-Bill scoping question** the handoff flagged:
Phase-0's first-pass filter scoped bill rows on `focus_type == 'State Bill'` **AND**
`level_of_government` starts-with `'State'`, and the `level` clause was suspected of
wrongly dropping `State Bill` rows filed at `Both` level. We resolved it against the
real data rather than by reasoning alone: the committed fixture row `S550-A` is a
genuine NY state bill filed at `level_of_government = 'Both (State and Municipal)'`,
and the focus-breakdown aggregates show the `level` clause drops **2.45M of 9.82M**
State-Bill rows for 2025 (25%). Decision: **scope on `focus_type == 'State Bill'`
alone.** `level` describes the engagement's jurisdictional scope, not the bill's
identity; `Municipal Bill` is a distinct `focus_type` value, excluded by the
focus-type test without consulting `level`.

Implemented `src/lobby_analysis/io/ny/parse.py` under the Nori TDD workflow (22 tests
RED → GREEN → one REFACTOR correction with its own RED→GREEN). The module is the
parser step that interposes between `columns.normalize_columns` (raw→canonical names)
and `grain.collapse_to_filing_grain` (which requires a canonical `bill_id` column to
already exist). It covers `bill_id` derivation, name-keyed entity parsing, dirty-money
coercion, and grain-row→`LobbyingFiling` mapping. Verified end-to-end that
`normalize_columns → add_bill_id_column → collapse_to_filing_grain` composes on the
real fixture; the `S550-A` `Both`-level row survives with a real `bill_id` — the exact
row the old `level` filter would have dropped.

A process note also came up: the first two commit attempts had a bad message (a
`read -d` bashism under dash produced an empty message; then shell interpolation
collapsed the JSON newlines). Fixed by building the commit payload in Python and
POSTing it from a file (`curl -d @file.json`), which keeps message/content out of
shell quoting entirely. Dan and I discussed whether to codify this; see Decisions.

## Topics Explored

- The State-Bill / `level_of_government` scoping question (resolved against fixture +
  aggregates, not by reasoning).
- The existing `grain.py` / `columns.py` contract — what the parser must produce
  (`bill_id` as an object-dtype column; canonical names) to slot in cleanly.
- WI conventions to mirror: `NY-{role}-{slug}` entity ids (WI used `WI-principal-{id}`),
  `expenditure_report` vs `activity_report` filing_type (WI: spend report =
  `expenditure_report`), money coercion, trailing-`;` / semicolon-list name cleaning.
- Whether the shell-quoting commit failure warrants a skill/project-instructions change.

## Provisional Findings

- The `level_of_government` clause in the Phase-0 bill filter is wrong; `focus_type`
  alone is the correct bill scope. (Verified on 2025 client_semiannual aggregates +
  the committed fixture; should still be re-confirmed against a live parse-rate probe —
  see Open Questions.)
- `normalize_columns → add_bill_id_column → collapse_to_filing_grain` composes on the
  real fixture rows with the expected grain and `n_bills_in_filing`.

## Decisions Made

- **State-Bill scoping:** scope on `focus_type == 'State Bill'` alone; do not filter on
  `level_of_government`. `derive_bill_id` takes no `level` argument, so `level` cannot
  affect bill identity structurally.
- **Amendment suffix:** `bill_id` preserves the print suffix (`S550-A`); stripping it to
  hit the Open States key stays the separate Phase-4 chain normalizer's job (per plan).
- **filing_type:** NY `client_semiannual` is a compensation report → `expenditure_report`
  (matches WI's spend-report convention).
- **Scope of this session:** stopped at the parser layer (`bill_id` + entity + filing
  parsers). `materialize_ny` + CLI is the next Phase-2 pickup, not done here.
- **Commit-transport lesson:** build GitHub Git-Data-API payloads in Python and POST
  from a file (`curl -d @file.json`); never route a multi-line message or file content
  through shell string interpolation. Dan and I agreed a *Git Data API multi-file commit
  recipe* is worth adding to the project instructions (recurring need across state
  pipelines); we did **not** add a defensive one-line caveat. Recipe addition not yet
  written — flagged for whoever edits the project-instructions doc.

## Results

- No analysis tables/figures this session (code + decision). The decisive evidence was
  already on the branch: `results/ny_focus_breakdown_2025.json` (focus-type counts) and
  `results/ny_grain_2025.json` (filing/bill counts), both from Phase 0.

## Open Questions

- **Parse-rate verification (carried, NOT done):** confirm that `State Bill` rows at
  `Both` level carry well-formed bill identifiers (`S###`/`A###` ± suffix), not free
  text the `level` filter was incidentally screening out. `derive_bill_id` safely yields
  `None` for non-bill text (so junk degrades to "not chain-eligible", never corrupts the
  chain), but we won't *know* the re-included 2.45M rows are mostly well-formed until a
  live aggregate probe runs. This environment's egress proxy doesn't allow `data.ny.gov`,
  so it couldn't run here — belongs at the start of Phase 3, or as a quick probe on a
  networked machine.
- `materialize_ny` design: which TSVs to emit and their exact headers (mirror
  `releases/wi/` shapes), and how the firm/client/individual-lobbyist entities + the
  per-(filing, bill) linkage rows split across files.

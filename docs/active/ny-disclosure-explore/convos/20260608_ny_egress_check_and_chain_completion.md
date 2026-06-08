# NY egress check → chain completion (Phases 0+1+2 shipped, CONSUMER_README)

**Date:** 2026-06-08
**Branch:** `ny-disclosure-explore`

## Summary

Session opened as a generic "can this sandbox reach the data sources we need?"
egress check. Dan corrected me when I said I didn't see an `ny-disclosure-explore`
branch — I'd been trusting STATUS.md (which doesn't yet list any of the
`*-disclosure-explore` branches) instead of querying the branches API. After
fixing that and reading the prior handoffs + `plans/ny_chain_completion_sketch.md`,
the session converted from "egress test" into actually executing the chain-
completion plan end-to-end: Phase 0 (gating grain-join check), Phases 1+2
(TDD column adds), and a follow-on CONSUMER_README aimed at letting Dan share
the chain with Suhan without project-internal jargon getting in the way.

Phase 0 ran on Dan's machine and returned **GREEN at 97.63%** join coverage
under the plan's default key `(filing_id, lobbyist_id)`, with key B (+`client_id`)
identical (zero `(filing, lobbyist)` groups spanning multiple `client_id`s —
client_id is redundant for this join). Phases 1+2 shipped as a hermetic TDD
addition to `compose_chain`: three new columns (`disclosed_lawmakers`,
`sponsor_in_disclosed_set`, `disclosed_only_lawmaker_count`), 12 new tests,
138 NY tests green, ruff clean. Dan ran Phase 3 (live regen) locally and
verified: 83,786 rows unchanged, **$153,064,191.00 conservation exact ($0 delta)**,
new column coverage matches Phase 0 to the digit (97.63%).

The post-build aggregates surfaced something I'd under-called in the README's
caveat-draft: `sponsor_in_disclosed_set=True` rate is **56.07%** on matched
rows — well short of the saturation I'd implied "base-rate fan-out" would
produce. So the column carries more signal than I gave it credit for; 44% of
matched rows are sponsors the filer did not (resolvedly) disclose contacting.
Walked back the "True largely by base rate" language in both the README and
the docstring; replaced with the actual measurement.

The CONSUMER_README closes the loop: Dan said the chain README is fine for
project-internal readers but won't survive Suhan dumping it to an agent and
saying "tell me what you think" — too much Phase-N / Decision-N / conservation
vocabulary, no provenance section, no plain-English row example, no sample
data, no consumer-facing aggregation snippets. We agreed on a sibling
`CONSUMER_README.md` rather than a rewrite, so the internal doc keeps its
density.

## Topics Explored

- **Session-start correction.** I missed `ny-disclosure-explore` (and
  `mi-disclosure-explore`, `nc-disclosure-explore`) by reading STATUS.md only;
  Dan caught it, I verified via the branches API. STATUS later updated on
  `main` via `leave-behind-prep`'s 2026-06-08 push (commit
  `f97c73d..6cc5bf0` on `main` included a new `docs/STATE_COVERAGE.md` and
  STATUS additions), which may already cover the gap — not re-checked.
- **Data-sizing question.** Dan asked how much raw data we need committed.
  Probed `data.ny.gov` live: full `qym9-xzj6` is 66.9M rows / ~20 GB
  projected; 2025-only 11.2M / 3.3 GB; 2024-only 17.8M / 5.2 GB. Definitively
  too big to commit. Discussed Git LFS — talked Dan out of it for this case
  (quota cost, slow clones, doesn't fit a "frequently-refreshed open data"
  pattern). Settled on the existing `data/raw/` gitignored + tiny committed
  sample pattern.
- **Real-data sample.** Pulled a 10k-row 2025 `client_semiannual` slice
  (projected to the 10 columns the pipeline reads), 2.7 MB, committed at
  `docs/active/ny-disclosure-explore/results/20260608_client_semiannual_sample_10k.{csv,md}`
  with sha256 + sampling-bias notes. Sampling caveat surfaced and recorded:
  Socrata's default order is biased toward large filings, so the 10k slice
  spans only 133 of 8,613 distinct `form_submission_id`s; fine for schema
  fixtures, NOT representative for grain analysis.
- **Per-filing row-count distribution.** Aggregate group-by surfaced the
  shape: median 6 rows per filing, p90 = 216, max = 2,219,319. This is
  consistent with the prior handoff's "the 2.22M mega-id streamed fine" note
  and helps explain why bucketing by id-range is the right pagination
  strategy.
- **Scope-creep self-check.** Caught myself designing a stratified-by-grain
  sampling strategy that neither active plan actually requires (acquisition-
  hardening uses mocked bytes; chain-completion uses 3–5 hand-known
  fixtures). Surfaced + redirected with Dan rather than continuing.
- **Plan-gating decision.** The chain-completion plan explicitly gates Phase
  1 behind Phase 0 with a hard STOP threshold at <90% join coverage. Talked
  through Path A (write Phase 0 script for Dan to run locally, wait for the
  verdict) vs Path B (jump the gate, write Phases 1+2 speculatively). Went
  with Path A — the plan author chose to gate this for a reason, and the
  Phase 0 script was a small contained win regardless.
- **Phase 0 verdict.** GREEN at 97.63% under key A; key B identical
  (`client_id` redundant). Fan-out distribution: median 36 distinct
  legislators per `(filing, lobbyist)` group, p99 = 158, max = 209
  (≈ full 213-member legislature). This number is what drove my caveat
  about `sponsor_in_disclosed_set` being unreliable at the row level.
- **Phases 1+2 implementation.** Added `_load_disclosed_contacts` (loads
  `NY_filing_parties_lobbied.tsv`, keeps only `resolved=True` with non-
  empty `party_lobbied_person_id`, returns `{}` if file absent for back-
  compat). Extended `compose_chain` with three columns: per-row inline
  computation of `disclosed_lawmakers` (sorted, `;`-joined) + per-row
  `sponsor_in_disclosed_set` (set membership), and a second pass for
  `disclosed_only_lawmaker_count` (needs the union of sponsor IDs across
  all chain rows for a group, only knowable post-build). All hermetic
  tests, `_write_parties` helper mirrors the materializer's `_FIELDS`
  exactly.
- **Open question 1+2 from the plan, ratified silently.** Column name
  defaulted to `disclosed_lawmakers` (vs `parties_lobbied_resolved`); sort
  order alphabetical on `ocd-person` ID. Flagged the defaults before
  writing, Dan ratified ("LGTM").
- **Post-data measurement correction.** Sample-row inspection (8 random rows
  Dan pasted) revealed concrete patterns I hadn't pre-anticipated — most
  notably row 5's $0 cell, row 6's `Budget Committee` collective sponsor
  forcing `sponsor_in_disclosed_set=False`, and row 8's `os_matched=True`
  with an empty `disclosed_lawmakers` set (the 2.37% Phase-0 miss in the
  wild). Used these as the sample table in CONSUMER_README rather than
  synthesizing.

## Provisional Findings

- **`(filing_id, lobbyist_id)` is the right join key for chain ↔ parties.**
  Key B (+`client_id`) gives identical coverage; zero groups span multiple
  client_ids. Phase 0 settled this; the plan's default is correct as written.
- **97.63% chain-rows-with-at-least-one-resolved-disclosed-lawmaker** —
  matches the regenerated chain to the digit.
- **`sponsor_in_disclosed_set=True` rate is 56.07% on matched chain rows
  (46,937 / 83,704).** Well short of the saturation a high-fan-out base-rate
  hypothesis would predict. So the column carries real signal at aggregate
  scale, but is NOT reliable as a per-row "did this firm meet this sponsor
  about this bill" indicator (grain caveat from Phase 0 still binding). The
  44% negative case is split between: filer working through cosponsors/
  staff/leadership/broadcasts (real off-sponsor lobbying) and resolver
  coverage gaps (unresolved-leg titles, committee staff, broadcasts that
  would resolve under a future `target_kind` taxonomy).
- **`disclosed_only_lawmaker_count` distribution.** Median 24, mean 35, p75
  69, max 200 per `(filing, lobbyist)`. This is the leadership / committee-
  chair / off-bill-contact signal the plan anticipated; it's substantial.
- **Sample inspection.** Concrete instances of every interesting row shape
  (large coalition, $0 cell, committee sponsor → empty `sponsor_lawmaker_id`,
  sponsor-not-disclosed, empty disclosed set despite os_matched). Used in
  CONSUMER_README's sample table.

## Decisions Made

- **Defaults from the plan's "open questions" ratified.** Column names
  `disclosed_lawmakers` / `sponsor_in_disclosed_set` /
  `disclosed_only_lawmaker_count`; sort order alphabetical on `ocd-person`
  ID. Flagged before writing, Dan said go.
- **`_load_disclosed_contacts` opts in by file presence.** Returns `{}` if
  `NY_filing_parties_lobbied.tsv` is absent; all three new columns default
  to empty / False / 0. Preserves backward compat with every existing test
  and any caller that doesn't have parties materialized.
- **Conservation invariant preserved by construction.** New columns added
  to `base` dict before sponsor fan-out replication; `comp_per_cell`
  arithmetic untouched. Verified: $0 delta on the regenerated chain.
- **Phase 3 (live regen) ran on Dan's machine, not in the sandbox.** Sandbox
  can't see the gitignored release TSVs or the OS Plural Policy bundle.
  Test discipline kept everything hermetic so Phase 3 was a pure CLI
  invocation on Dan's side.
- **README "base rate" framing softened post-data.** Pre-data, I'd written
  "True largely by base rate" — the 56.07% measurement doesn't support
  "largely." Both the chain README and the `compose_chain` docstring
  updated to reflect the actual measurement and the dual reading (True is
  not bill-specific evidence, but False isn't pure noise either).
- **`CONSUMER_README.md` instead of rewriting README.md.** Dan agreed —
  preserves the internal doc's density for project-internal readers; gives
  Suhan a standalone consumer-facing document that survives being dumped
  to an agent with the file. Structure: what-it-is plain English, provenance,
  example questions with pandas snippets, schema, dollars discipline, two-
  lawmaker-signals caveat, sample rows table, companion files, 8 limitations.

## Results

Five commits on `ny-disclosure-explore`:

- `3b5235c` — 10k client_semiannual sample (real-shape fixture) at
  `docs/active/ny-disclosure-explore/results/20260608_client_semiannual_sample_10k.{csv,md}`.
- `0a9da2e` — Phase 0 grain-check script: `scripts/ny_chain_pl_grain_check.py`.
- `3f60e05` — Phases 1+2 chain enrichment:
  `src/lobby_analysis/allocation/ny/chain.py` (+ `_load_disclosed_contacts`,
  three new columns, docstring update), `tests/test_ny_chain.py` (+ 12 new
  tests, `_write_parties` helper), `releases/ny/chain/README.md` (extended
  schema, new "Disclosed vs inferred" section). 138 NY tests green.
- `f3d9770` — README aggregates table + "base rate" softening, in both the
  release README and the `compose_chain` docstring.
- `315454d` — `releases/ny/chain/CONSUMER_README.md`, the consumer-facing
  companion (337 lines).

Phase 0 results written locally to
`docs/active/ny-disclosure-explore/results/20260608_ny_chain_pl_grain_check.md`
(not committed by Dan yet — fine, the script regenerates it deterministically).

## Open Questions

- **STATUS.md updates from `leave-behind-prep`.** Dan's pull surfaced that
  STATUS got an update on `main` (`f97c73d..6cc5bf0`) plus a new
  `docs/STATE_COVERAGE.md`. May already record `ny-disclosure-explore` and
  the sibling `*-disclosure-explore` branches — I noted the addition but
  didn't read it. Worth a check next session.
- **Phase 0 results doc not yet committed.** The deterministic markdown
  output of `scripts/ny_chain_pl_grain_check.py` ran successfully on Dan's
  worktree but isn't tracked. Cheap to add next session if the numbers are
  worth keeping in branch history (they are — they're the gating evidence
  for the GREEN verdict).
- **README's `parties_lobbied` resolution figure (57.6%) was cited verbatim
  from `releases/ny/README.md` — should be re-verified.** The CONSUMER_README
  references it; if it has drifted since the README was written, the
  consumer doc would inherit the drift. Low priority, but a one-line check.
- **The "stale framing" I caught in the chain README — is it the only
  stale spot?** I fixed the "Honest limitations" first bullet and the v1.1
  follow-ups section; didn't audit the rest. The aggregates table is
  current. The conservation discussion is current. But there may be other
  small drifts post-2026-06-05.
- **Phase 4 remains deferred.** The `target_kind` taxonomy for the ~42%
  non-individual `parties_lobbied` rows (NYC officials, agencies,
  broadcasts) would let those contribute to a disclosed-lawmaker signal too
  — currently they're `resolved=False` and excluded from
  `disclosed_lawmakers`. Real follow-on, not started.
- **Suhan feedback loop.** Once Suhan (or her agent) actually reads the
  CONSUMER_README, the most useful next iteration is whatever questions
  they ask — they'll surface the gaps better than I can guess.

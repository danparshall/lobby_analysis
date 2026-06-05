# wi_tier_2_phase_4_materialize

**Date:** 2026-05-26
**Branch:** wi-disclosure-explore
**Originating plan:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md)
**Prior convo (handoff source):** [`convos/20260526_wi_tier_2_phases_2_3_green.md`](20260526_wi_tier_2_phases_2_3_green.md)

## Summary

Picked up the prior session's Phase 4 handoff. Wrote 36 RED tests at
`tests/test_wi_tier_2_materialize.py` covering the materializer's full
public surface — ParseFailure value object, two checkpoint iterators
(parsed-tuple yield vs `ParseFailure` routing, null-html silent skip,
sorted iteration, non-numeric filename skip), 5 TSV writers + 1
warnings writer (schema fieldnames, sort orders, None→empty-cell vs
zero→"0.0" distinction, JSON-serialization of contact_details),
end-to-end orchestrator (6 output files, known-value round-trip on the
Dairy P1 anchor, ParseError doesn't crash the run, `WI-{role}-{id}`
convention, principal_id/lobbyist_id join compatibility with
`WI_lobbyist_principal_authorizations.tsv`), and idempotency
(byte-identical re-runs). Implemented
`src/lobby_analysis/io/wi/tier_2_materialize.py` against the contract;
all 36 turn green on the first implementation pass — no iteration
needed.

Then ran the materializer against the real on-disk corpus (944
principal + 776 lobbyist checkpoints under
`~/data/lobby_analysis/disclosures/WI/`) as a smoke check: **19.2 s
wall, 6 output files emit clean, 0 parse failures**. Spot-checks of
Dairy 11590 (P1 `$37,840 / 158.5 / 307.0`, P2 `$50,728.5 / 100.5 /
254.0`), WCTA 12997 (`$0.0 / 0.0 / 0.0`), Brooks 11052 (P1 `102.5 /
566.0`, P2 `195.0 / 673.9`, 2026 zeros) match the parser tests'
fixture-derived anchor values exactly.

Per Dan's call via in-session AskUserQuestion ("Phase 5 only, then
finish-convo"), also shipped the Phase 5 CLI wrapper —
`src/lobby_analysis/io/wi/tier_2_materialize_cli.py`, a thin argparse
pass-through over `materialize_tier_2()` mirroring
`unify_authorizations_cli.py` in shape. No new tests per the plan
(the materializer's 36-test suite covers everything the CLI does).
Verified end-to-end against the real corpus.

Two findings worth surfacing for the Phase 7 results writeup:

1. **0 parse failures, not the 1 the plan + prior convos
   anticipated.** The Neumann-Ortiz 12717 soft-404 is already stored
   as `html=null` by the fetcher's body-marker detection from the
   auth-scrape session, so the materializer's iterator silently skips
   it via the null-html branch — it never reaches the ParseError →
   ParseFailure path. The soft-404 IS handled correctly, just via a
   different path than the plan's framing implied. Worth documenting
   in Phase 7 so future readers don't go hunting for the "missing"
   failure row.

2. **WCTA 12997 emits 1 filing (2025-H2 at $0/0/0), not 2.** The
   2025-H1 column on its page is empty rather than populated-with-zero.
   Low-spend-exempt principals file in some periods but not necessarily
   all of them; the plan's "zeros across all periods" framing turns
   out to be "zeros in whichever periods the page populates; absent in
   others." Not a bug — a refinement of expectations.

## Topics Explored

- Phase 4 materializer design: module structure, iterators, TSV
  writers, orchestrator
- Idempotency vs `extracted_at`: parsers stamp `datetime.now()` into
  provenance; TSV omits that field by design so byte-identical re-runs
  are possible
- Tagged-union iterator yield (parsed tuple OR `ParseFailure`) for
  testability + clean dispatch in the orchestrator
- TSV row schemas — 5 output TSVs + 1 warnings TSV, sort orders,
  JSON-serialization of contact_details with stable separators
- Smoke-test against real on-disk corpus + spot-check of plan anchors
- Phase 5 CLI wrapper — mirrors `unify_authorizations_cli.py` shape

## Provisional Findings

- **Materializer is structurally clean.** 36 of 36 driving tests
  GREEN on first implementation. No iteration needed on iterator
  behavior, TSV schemas, or the orchestrator's row-count return.

- **Idempotency contract holds on real data.** Two consecutive smoke
  runs against the 944+776 corpus produced identical row counts in
  the same wall time. The `test_repeated_runs_produce_byte_identical_output`
  test covers the byte-identity proof at the synthetic-input level.

- **Soft-404 filtering happens earlier than expected.** The fetcher's
  body-marker detection (shipped in the auth-scrape session) sets
  `html=null` on soft-404s, so the iterator silently skips them. The
  ParseError → ParseFailure path is for *truly unparseable* pages —
  not the documented Neumann-Ortiz case. The auth-scrape session
  caught 1 soft-404 (12717); the principal-side scrape session caught
  0. The materializer reads both at 0 parse failures, consistent with
  that history.

- **WCTA 12997 has only 1 emitted filing, not 2.** The 2025-H1 column
  on its page is empty. Low-spend-exempt principals don't necessarily
  file zero-rows across all periods — they file in whichever periods
  the portal records something for, and the others are absent. Worth
  documenting in Phase 7's results writeup.

- **Output volume profile** (944 principal + 776 lobbyist
  checkpoints, gitignored):
  - 944 Organization rows in `WI_principals.tsv` (matches scrape headline)
  - 773 Person rows in `WI_lobbyists.tsv` (3 silently skipped via
    null-html; consistent with the 1 soft-404 + 2 other captured-as-null
    cases noted in prior scrape sessions)
  - 1,706 expenditure-report rows in `WI_principal_filings.tsv`
    (≈1.8 emitted filings/principal on average)
  - 3,092 activity-report rows in `WI_lobbyist_filings.tsv` (exactly
    773 × 4 — matches the lobbyist parser's "always 4 filings per
    page" contract)
  - 7,345 per-item bill-effort rows in `WI_principal_bill_efforts.tsv`

## Decisions Made

- **Convo name (this file):** `20260526_wi_tier_2_phase_4_materialize.md`.
  Sequential continuation of the Phase 2/3 convo from earlier today.

- **TSV idempotency strategy:** omit `extracted_at` from row schemas
  (parsers' `datetime.now()` would defeat byte-identity); include
  `source_url` (stable from URL template). The provenance object
  stays correct in-memory; only the TSV row schemas are trimmed for
  idempotency.

- **Iterator yield shape:** tagged-union (parsed tuple OR
  `ParseFailure`), with `isinstance(rec, ParseFailure)` dispatching
  in the orchestrator. Cleaner than mixed-type returns or
  side-channel failure lists.

- **TSV writer factorization:** 6 public writer functions (one per
  output file) + one orchestrator. Each writer takes a `Sequence`,
  sorts deterministically, returns the row count. Composable and
  individually testable.

- **Phase 5 ship strategy:** thin argparse CLI pass-through, no new
  tests (plan-locked). Verified end-to-end against the real corpus.

- **Pause point:** Dan picked "Phase 5 only, then finish-convo" via
  in-session AskUserQuestion. Phases 6 (run/spot-check writeup) and 7
  (WCTA doc-drift fix + results writeup) deferred to a follow-up
  session.

## Results

### Commits this session

All pushed to `origin/wi-disclosure-explore`:

- `1132529` wi: tier-2 materializer tests (red; 36/0)
- `69a268b` wi: tier-2 materializer (green; 36/36)
- `eff2cda` wi: tier-2 materialize CLI

(Plus this finish-convo commit + RESEARCH_LOG + STATUS updates below.)

### Test deltas

- `tests/test_wi_tier_2_materialize.py`: 36 RED → 36 GREEN on first
  implementation pass. 11 test classes covering ParseFailure value
  object, two iterators, 5 TSV writers + 1 warnings writer, the
  end-to-end orchestrator, and idempotency.
- Full suite: **1537 passed** (+36 from prior session's 1501), 3
  pre-existing `test_pipeline.py` baseline failures (archived-line
  owned, same as prior session), 3 skipped, 3 xfailed. No
  regressions.

### Code shipped

- `src/lobby_analysis/io/wi/tier_2_materialize.py` (~440 lines
  including docstring)
- `src/lobby_analysis/io/wi/tier_2_materialize_cli.py` (~95 lines)
- `tests/test_wi_tier_2_materialize.py` (~1100 lines, 36 tests)

### Smoke run on real corpus (gitignored; for context only)

19.2 s wall against 944 principals + 776 lobbyist checkpoints:

| Output | Rows | Size |
|---|---|---|
| `WI_principals.tsv` | 944 | 608 KB |
| `WI_lobbyists.tsv` | 773 | 244 KB |
| `WI_principal_filings.tsv` | 1,706 | 314 KB |
| `WI_lobbyist_filings.tsv` | 3,092 | 525 KB |
| `WI_principal_bill_efforts.tsv` | 7,345 | 1.2 MB |
| `_tier_2_parse_failures.tsv` | 0 | 0 KB (header-only) |

Output landed at `~/data/lobby_analysis/disclosures/WI/_tier_2_smoke/`
— a subdir, intentionally NOT the documented Phase 6 path
(`~/data/lobby_analysis/disclosures/WI/`), so this smoke run didn't
overwrite anything Dan might want to inspect under that path in the
proper Phase 6 session.

## Open Questions

- **Phase 6 results writeup.** A proper Phase 6 spot-check writeup
  would document (a) the 0-vs-1 parse-failures finding above; (b) the
  WCTA single-filing finding; (c) any other surprises from inspecting
  the materialized TSVs at scale. Deferred to a follow-up session.

- **Phase 7 doc-drift fix.** The WCTA 12997 name correction in
  `results/20260526_wi_principal_side_scrape_results.md` line 65
  ("Wisconsin Cable Telecommunications Association" → "Wisconsin
  County Treasurers Association") is still pending. Single-line edit
  + a brief process note. Easy to ship alongside Phase 6's writeup.

- **Address ContactDetail quality (still open from Phase 3 convo).**
  Best-effort heuristic on lobbyist `Person.contact_details` likely
  conflates firm name + phone digits into the `address` value. Worth
  eyeballing the materialized `WI_lobbyists.tsv`'s `contact_details_json`
  column on a few rows in Phase 6 to decide whether a small refactor
  is warranted.

Held over from prior sessions (orthogonal to Tier-2):

- `lobbying@wi.gov` reply on the Schlaak grid-AJAX filter
- State Agency Liaisons table parser/ingest
  (`WI_directory_state_agency_liaisons.xls` already captured at 2,599
  rows × 13 cols; not yet wired)
- Cross-session principal_id stability investigation

## Next Steps

Top of the list for the next agent (or the next session of this
branch):

1. **Phase 6 + Phase 7 in one session.** Re-run the CLI to the proper
   output dir (`~/data/lobby_analysis/disclosures/WI/`), inspect the
   materialized TSVs at scale, write
   `results/20260526_wi_tier_2_parser_results.md` documenting the two
   findings above plus top-10 principals by spend, bucket
   distribution across the 7,345 bill-effort rows, lobbyist hours
   distribution. Apply the WCTA doc-drift fix in the same session.

2. **Alternative path: PR + merge `wi-disclosure-explore` now.** Phase 4
   (materializer) + Phase 5 (CLI) are the load-bearing pieces; Phases
   6/7 are mostly writeup + a one-line doc-drift fix. If Dan calls
   the branch done at the parser+materializer layer, PR + merge is
   reasonable. Phase 6/7 could land later via a separate small
   branch.

**One-sentence handoff for the next agent:** Phase 4 + 5 are
committed at `1132529` / `69a268b` / `eff2cda` and the full suite is
at 1537 passed; the materializer runs cleanly against the real
944+776 corpus in 19.2 s; pick up at Phase 6 by running
`uv run python -m lobby_analysis.io.wi.tier_2_materialize_cli` and
writing the results doc, or open a PR if Dan calls the
parser+materializer the Tier-2 finish line.

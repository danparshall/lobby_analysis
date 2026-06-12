# NY Phase 2 — materialize_ny + materialize_cli

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Picked up at the prior session's explicit handoff: build `materialize_ny` + a
thin `io/ny/materialize_cli.py`, the remaining Phase 2 work after the grain and
parser steps. Followed the handoff's "do not re-litigate the settled decisions"
instruction — the State-Bill scoping (`focus_type == 'State Bill'` alone) and
the layer composition were already resolved against data, so this session built
on top of them rather than re-checking them.

`materialize_ny` projects the collapsed filing grain into four `releases/ny/`
TSVs, shape-compatible with `releases/wi/`: `NY_clients.tsv` (beneficial clients
as `Organization`), `NY_lobbyists.tsv` (principal-lobbyist firms), `NY_filings.tsv`
(one row per (submission, client) at filing grain, comp carried once), and
`NY_filing_bill_links.tsv` (one row per (filing, real bill) with the even-split
`comp_per_bill`). The CLI wires the full Phase-2 pipeline over a raw Open NY bulk
CSV (`normalize_columns → add_bill_id_column → collapse_to_filing_grain →
materialize_ny`), mirroring `io/wi/tier_2_materialize_cli.py` but adapted to NY's
raw-CSV input (WI's reads pre-parsed checkpoints).

Work was done test-first per repo norms. Because git push is blocked in this
session's environment (worked via the GitHub REST API), the full repo
`pytest`/`ruff` could not be run here — verification was done locally against the
real Pydantic models and the Phase-0 fixture, and a networked run is still owed
before fully trusting the green claim. The implementation landed as commit
`f1098b6b27`.

## Topics Explored

- The `materialize_ny` output shape: how to split NY's denormalized
  client_semiannual into entity + filing + per-bill-link TSVs that stay
  shape-compatible with `releases/wi/` and feed the Phase-4 chain join.
- The WI materializer conventions to mirror (`csv.DictWriter`, `\t` delimiter,
  `\n` lineterminator for byte-identical re-runs, `None → ""`, compact JSON
  columns, deterministic sort, return-counts contract).
- Even-split dollar attribution and its conservation invariant under odd
  division.
- The CLI shape: NY needs the full Phase-2 pipeline wired (raw CSV in), unlike
  WI's checkpoint-reading CLI.

## Provisional Findings

- The existing `normalize_columns → add_bill_id_column → collapse_to_filing_grain`
  chain composes correctly on the real Phase-0 fixture (independently re-verified
  this session): `S550-A` survives with a real `bill_id`; the `State Funding` /
  `Discretionary Funding` focus rows correctly get `None`; compensation is carried
  once, not summed.
- The even-split conserves dollars exactly even under odd division — integer-cent
  arithmetic distributes the remainder so `100/3 → 33.34 + 33.33 + 33.33 = 100.00`.
  This is the NY analog of WI's `modeled_hours_per_sponsor` conservation test.
- A filing with no real bills (only a non-bill focus, `n_bills_in_filing = 0`)
  appears in `NY_filings.tsv` (its dollars are preserved) but contributes zero
  rows to `NY_filing_bill_links.tsv` — not chain-eligible, but not lost from the
  filings table.
- Observed (not fixed): `parse_filing` feeds a `Decimal` into
  `LobbyingFiling.total_compensation`, which is typed `float`; Pydantic silently
  coerces. The materializer deliberately writes the `Decimal` straight from the
  grain (bypassing the model) so the TSVs stay exact — but the model's float
  field and the TSV can disagree at the last digit. A `Decimal`-typing pass on
  the filings model is a candidate follow-up, out of scope here.

## Decisions Made

- **Filing output is split into two TSVs** (`NY_filings.tsv` at filing grain +
  `NY_filing_bill_links.tsv` per-bill), mirroring WI shipping both the aggregate
  and the split, and setting up the Phase-4 chain join. (Flagged to Dan as a
  design choice, not silently assumed.)
- **No new CLI tests** — per the WI `tier_2_materialize_cli` precedent: the
  materializer's suite + the upstream steps' suites cover the behavior the CLI
  invokes. The CLI was still verified end-to-end by hand against a CSV built from
  the real fixture rows.
- Entity ids follow the established `NY-{role}-{slug}` convention; entities are
  de-duplicated by id.

## Results

- No standalone results files this session — the deliverable is code
  (`io/ny/materialize.py`, `io/ny/materialize_cli.py`) + tests
  (`tests/test_ny_materialize.py`), committed at `f1098b6b27`.

## Open Questions

- **Owed verification:** a networked machine should run
  `uv run pytest tests/test_ny_materialize.py` (and the full suite) to confirm
  the green claim — this session could not run the repo harness.
- `releases/ny/README.md` is intentionally deferred until after the first real
  Phase-3 run, so its headline-aggregates section isn't a placeholder (the plan
  says exactly this).
- Whether the consumer wants the two-TSV filing split or a single denormalized
  filing-bill table — the split is the current choice but is reversible.
- The `Decimal`-vs-`float` typing of `LobbyingFiling.total_compensation` —
  worth a model-side pass eventually.

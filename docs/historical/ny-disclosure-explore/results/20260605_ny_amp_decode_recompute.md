<!-- Generated during: convos/20260605_ny_v1_1_amp_decode_and_parties_recon.md -->

# NY v1.1 — `&amp;` HTML-entity decode: bug, fix, and recomputed aggregates (2025)

## The bug (correctness, not cosmetics)

The Open NY `beneficial_client` field is HTML-encoded: an ampersand arrives as
`&amp;` (e.g. `A&amp;E Real Estate Management LLC`, `AT&amp;T`). The Phase-3
parser (`io/ny/parse.py::_clean_name`) did **not** decode entities, so
`NY_clients.tsv` shipped encoded names and `-amp-` slugged ids.

The chain composer's coalition splitter (`allocation/ny/chain.py::split_beneficiaries`)
splits `beneficial_client` on `;`. **The encoded ampersand `&amp;` ends in a
`;`** — the same delimiter. So an undecoded `AT&amp;T` was split into two
phantom beneficiaries, `AT&amp` and `T`:

- fabricated beneficiaries (phantom fragments in `beneficiary_name` / `beneficiary_id`);
- inflated the coalition member count `M`, so `even_split(C, M·N)` divided each
  real beneficiary's `comp_per_cell` by too large a denominator (the per-filing
  total stayed conserved — the dollars were just misallocated *within* the cell);
- inflated the published "coalition filings (M>1)" metric, because standalone
  names containing one `&amp;` looked like 2-member coalitions.

**Scale in the shipped (pre-fix) chain:** 3,748 of 87,534 rows (4.3%) carried an
`&amp` fragment in `beneficiary_name`.

## The fix (root cause, TDD)

Decode HTML entities at the earliest parse point so releases *and* chain get
clean names + ids:

- `_clean_name`: `html.unescape(...)` **before** the trailing-`;` strip (order
  matters — stripping first would truncate an entity sitting before a delimiter
  artifact like `A&amp;H ...;`).
- `parse_individual_lobbyists`: unescape the whole field **before** the `;`
  split (it splits raw, bypassing `_clean_name`), so an entity-bearing name
  can't fracture the person list either.

The chain's `split_beneficiaries` needs no change: it reads the now-decoded
`NY_clients.tsv`, so the `;` it splits on is only ever a real coalition
delimiter. 5 new tests in `tests/test_ny_entities.py`; NY suite 89 → **94 green**,
ruff clean.

## Recomputed chain aggregates (after regeneration)

Regenerated end-to-end: `materialize_cli` over the raw 2025 `client_semiannual.csv`
(11.2M rows) → `releases/ny/`, then `cli chain` → `releases/ny/chain/NY_chain_2025.tsv`.

| metric | pre-fix | post-fix | note |
|---|---|---|---|
| chain rows | 87,534 | **83,786** | −3,748 = exactly the phantom-fragment rows |
| distinct beneficiaries | 1,892 | **1,812** | 80 phantom beneficiaries removed |
| coalition filings (M>1) | 476 | **276** | old count inflated ~42% by mis-split standalones |
| rows `os_matched=True` | 87,446 (99.9%) | **83,704 (99.9%)** | bill-match unaffected |
| distinct unmatched bills | 30 | **30** | unchanged |
| distinct lobbying firms | 927 | **927** | firms used literal `&`, never encoded |
| distinct source bills | 6,352 | **6,352** | unchanged |
| distinct sponsors | 213 | **213** | full NY legislature |
| **total over distinct cells** | **$153,064,191.00** | **$153,064,191.00** | **$0 delta — conservation holds** |

The row drop equals the fragment-row count exactly, by construction: each
`&amp;` split created one extra (left-fragment) beneficiary, contributing one
extra set of `N×sponsors` rows; the fix merges the fragments back, removing
precisely those rows. The Phase-3 release entity counts (4,373 clients / 1,333
lobbyists / 10,870 filings / 47,204 links) are unchanged — decoding renames
entities without merging distinct ones.

## Validation

- Conservation: distinct-cell total = **$153,064,191.00**, identical to the
  pre-fix total and to the Phase-3 bill-linked release total ($0 delta).
- Residual entities: `grep` finds **0** `&amp;` in any `releases/ny/*.tsv` after
  regeneration (remaining hits are in README prose, since updated).
- Bill-id match rate (99.9% rows, 30 unmatched bills) unchanged — the decode is
  orthogonal to bill normalization.

Probe scripts (committed): `scripts/ny_chain_metrics.py`,
`scripts/ny_chain_aggregates.py`.

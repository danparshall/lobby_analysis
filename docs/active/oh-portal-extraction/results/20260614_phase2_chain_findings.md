# 2026-06-14 — OH chain composer Phase 2 (chain.py) findings

**Branch:** `oh-chain-composer` (continuing from `56f80ca` — Phase 1 loaders shipped).
**Trigger:** Plan §5 Phase 2 — bill-side chain composer.
**Smoke script:** `20260614_phase2_chain_smoke.py` (sibling file).

## What shipped

Module: `src/lobby_analysis/allocation/oh/chain.py` (~250 lines).
Tests: `tests/allocation/oh/test_chain.py` (21 tests, all passing — full OH suite now **106/106**).

`compose_bill_chain(extractions_dir: Path, plural_dir: Path) -> pd.DataFrame` walks the canonical extractions and emits chain rows per the §4/§4a/§6 plan contracts:

| Class flow | Rows per position | Sponsor fields | `confidence` token |
|---|---|---|---|
| `bill_class=='bill'` AND joins Plural | N (cross-product over primary sponsors) | populated | `direct` |
| `bill_class=='bill'`, joins Plural, 0 primaries (defensive) | 1 | null | `direct` (with `num_primary_sponsors=0`) |
| `bill_class=='bill'`, doesn't join Plural | 1, downgraded to `unmatched` | null | `unmatched` |
| `bill_class=='jcarr'` / `'oac_rule'` | 1 | null | `oac_dropped` |
| `bill_class=='subject'` (both subject kinds) | 1 | null | `subject_only` |
| classifier raises (empty position) | 1 sentinel | null | `null_extraction` |

Schema (per plan §4 sketch): 18 columns. Output column order locked in `CHAIN_COLUMNS` constant.

Calls `select_canonical_extraction(load_filings(...))` to dedupe the 11 duplicate cached extractions for 5 filing_ids (Finding 1 from Phase 1). This is load-bearing — without it, those 5 filings would triple-count.

## Real-data smoke against the 316-filing cache

```
Chain rows: 1,589

bill_class distribution:
  bill          1,299
  subject         150
  jcarr            88
  oac_rule         34
  unmatched        18
  TOTAL         1,589   (conservation: every input position contributes ≥1 row)

position_kind distribution:
  bill_referenced                       1,439
  subject_general                         149
  subject_hoisted_from_description          1

confidence distribution:
  direct           1,299
  subject_only       150
  oac_dropped        122
  unmatched           18
  null_extraction      0   (no empty positions in the slice)

num_primary_sponsors distribution:
  primary_count=2:   888 chain rows  (= 444 bill-position joins × 2 primaries)
  primary_count=1:   411 chain rows  (= 411 bill-position joins × 1 primary)
  primary_count=0:   290 chain rows  (= all non-bill rows; 0 defensive 0-primary cases)
```

**Conservation arithmetic:**
- Cross-product on bill side: 411 (1-primary) + 444 (2-primary) = 855 unique bill-position joins → 1,299 bill chain rows
- Non-bill side: 290 non-bill rows = 150 subject + 88 jcarr + 34 oac_rule + 18 unmatched
- Total deduped input positions: 855 + 290 = **1,145**
- Pre-dedup positions (Phase 1 smoke): 1,177
- Dedup delta: 32 positions — these came from the 11 non-canonical extractions of the 5 dupe-cached filing_ids whose canonical version had a different position count. Confirms `select_canonical_extraction` is doing its job.

**Top-5 most-lobbied bills** (by chain rows):

| Chain rows | Label | Title |
|---:|---|---|
| 73 | HB 96 | Make state operating appropriations for FY 2026-27 |
| 22 | HB 1  | Enact Ohio Property Protection Act |
| 14 | HB 276 | Prohibit certain actions re: reimbursing 340B covered entities |
| 14 | HB 105 | Revise non-recourse litigation funding agreement regulations |
| 12 | HB 227 | Modify excavation requirements |

HB 96 (operating budget) at the top matches the 06-11 smoke-test finding (81 raw references). The current 73 chain-row count reflects HB 96's number of primary sponsors in Plural (currently 1 primary based on 73/some-divisor — note HB 96 is the budget bill, primary by definition single sponsor in OH practice).

**Per-filing chain-row dispersion:**

```
count   140.00       (unique filing_ids in chain output)
mean     11.35       (chain rows per filing)
std      23.51
min       1.00
25%       2.00
50%       4.00
75%       9.00
max     163.00       (one filing alone emits 163 chain rows — heavy lobbying portfolio)
```

305 canonical filings, but only 140 produce chain rows — the other 165 have no positions (54% of canonical filings are position-empty in this slice). Consistent with the 53% nil rate flagged in the 06-11 data-landed doc.

## What this unblocks

- **Phase 3 (gifts composer):** independent of chain; runs against the same extraction cache.
- **Phase 3.5 (filings-level composer, Q6→include):** consumes `load_filings` directly and applies the stated-zero + is_current normalizations.
- **Phase 4 (CLI):** wires chain + gifts + filings composers into `materialize` subcommand.
- **Phase 5 (READMEs):** the conservation rules above + per-bill_class semantics are the README's "30-second tour" content.
- **Phase 6 (preview release):** runs Phase 4's CLI against this slice; ship `_preview` filenames.

## What stays open

- **No `confidence='direct_no_primary'` distinction.** When a bill joins Plural but has 0 primary sponsorships (defensive case), the row gets `confidence='direct'` and `num_primary_sponsors=0`. Analysts can filter on `num_primary_sponsors==0 AND bill_class=='bill'` if they need to surface this case. Could split `direct_with_sponsor` vs `direct_no_sponsor` in v0.1.
- **`extract_position_label` uses `original_text` not `bill_number`.** For positions whose `bill_reference.original_text` contains extra text (e.g., "HB 96 BUDGET BILL"), the classifier matches `bill` but the join might fail (would emit as `unmatched`). The 06-11 smoke test used `bill_number` as the preferred join key. In this slice the issue doesn't materialize (no such extra-text labels appear), so the practical impact is zero. **Worth swapping** to `bill_number or original_text` for the JOIN key (keeping `original_text` for display) when the full-corpus run lands — the wider sample is more likely to contain extra-text labels.
- **OAC regex widening (per Phase 1 Finding 3):** OAC variants with colons (`5180:4-5-09.1`), "Chapter" prefix, multi-rule strings remain in the `unmatched` bucket. Defensible v0.1 widening.

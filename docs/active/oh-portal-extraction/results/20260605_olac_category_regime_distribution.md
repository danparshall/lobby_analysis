<!-- Generated during: convos/20260605_provenance_fixes_implementation.md -->

# OLAC Category → regime distribution (cached agent pages)

**What this is:** an empirical tabulation of the OLAC FormsFiled "Category"
column (table index 5) across every cached agent page, to confirm the
`category → regime` mapping the provenance-fixes plan flagged as
Medium-confidence (especially the `R` → retirement case, which the L/E test
fixture didn't cover).

**How it was generated:** a one-off scan of all cached
`data/oh_portal/oh_portal/discover/agents/*.html` pages (the doubled-path cache
from the 2026-06-05 `discover --all` crawl), parsing each row with a /View link,
reading `cells[5]` as Category and `cells[2]` as form type. 2,684 pages scanned;
every row that had a /View link had exactly 8 cells (consistent structure).

## AER rows by Category

| Category | AER rows | share | → regime |
|----------|---------:|------:|----------|
| `L` | 190,538 | 52.30% | legislative |
| `E` | 170,907 | 46.91% | executive |
| `R` | 2,906 | 0.80% | retirement_system |
| **total** | **364,351** | | |

No blank or unknown Category values appeared in the AER set.

## Interpretation

- The mapping `L→legislative`, `E→executive`, `R→retirement_system` is confirmed
  on real data, including the `R` case the fixture lacked — the plan's
  Medium-confidence flag is resolved without a live page fetch.
- These counts are **all years** (the full cache), not the 2025–26 universe. The
  prior session's raw-text subsample of the 2025–26 slice was ~86% legislative /
  ~13% executive / ~1% retirement. Different denominators; not a conflict. The
  ~14% non-legislative share of the 45,605-filing 2025–26 universe is what the
  new `select_legislative` skip-by-default removes.
- Caveat: the high executive share here is dominated by older filings; do not
  read 46.9% as the executive share of the current-vintage extraction target.

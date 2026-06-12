<!-- Generated during: convos/20260606_ny_accent_fold_match_key.md -->

# NY `parties_lobbied` — accent-folding the first+last match key

**What changed.** The first+last match key (`io/ny/parties._first_last_key`) now
folds diacritics via NFKD decomposition (drop combining marks) before casefolding.
Because the *same* key function builds both the OS roster keys and the disclosure
lookup keys, folding it once makes both sides symmetric — the disclosure's plain
`Jose Serrano` and the OS roster's accented `José Serrano` now produce the same
key (`jose serrano`). The displayed `party_lobbied_name` keeps its accents; only
the match **key** is folded.

This is a deterministic canonicalization, not similarity-fuzzing — the same class
of move as dropping the middle initial (which Dan ratified 2026-06-06).

## Before / after (full 2025 release, regenerated from the 2.32 GB pull)

| metric | baseline (pre-fold) | accent-folded | delta |
|---|---:|---:|---:|
| total edge rows | 170,328 | 169,813 | −515 |
| resolved rows | 90,612 | 92,342 | **+1,730** |
| resolution rate (all edges) | 53.20% | 54.38% | +1.18 pp |
| **state-legislator edges** | 100,250 | 99,735 | −515 |
| **resolved (of state-legislator edges)** | **90.39%** | **92.59%** | **+2.20 pp** |
| distinct resolved legislators | 195 | 198 | **+3** |

The baseline figures reproduce the prior session's release exactly (100,250
state-legislator edges, 90.4%), which validates the denominator method.

## The +3 newly-resolved legislators are exactly the accented names

| `ocd-person` | example disclosure raw |
|---|---|
| `…1e5af6bc…` | `Senator Luis R. Sepulveda` |
| `…31d058e9…` | `Senator Jose M. Serrano` |
| `…4af19dc2…` | `Assembly member Emérita Torres, staff member` |

Serrano and Torres are the two names the handoff named; Sepúlveda (Sepulveda in
the disclosure, accented in the OS roster) is a bonus recovery of the same class.

## Why total rows DROP by 515 (this is correct, not data loss)

The edge grain is `FILING_KEY → {distinct resolved parties}`. Resolved parties
dedupe by `person_id`; unresolved parties dedupe by the cleaned raw string. When
a name becomes resolvable, multiple raw spellings of that legislator within one
filing (e.g. `Senator Jose M. Serrano` and a middle-initial-free variant) collapse
from N distinct unresolved rows to ONE resolved person-edge. That accounts for the
−515.

Accounting (internally consistent): unresolved rows fell by 2,245; of those, 1,730
became net-new resolved edges and 515 collapsed onto person-edges already counted.
The state-legislator denominator fell by exactly the same 515 — confirming every
collapsed row was a now-recognized legislator, not a lost office/agency. The
unresolved-dedup path (raw casefold) is untouched by the change, so no executive
office, agency, or broadcast edge can be merged or lost. The edge is unweighted
(no conservation invariant), so the row count is not a conserved quantity.

## Reproduction

```
PYTHONPATH=src python -m lobby_analysis.io.ny.parties_cli \
    --input data/raw/ny/2025/client_semiannual.csv \
    --os-dir data/bills/NY/2025 \
    --output-dir releases/ny
```

Tests: `tests/test_ny_parties_lobbied.py::test_resolve_accent_folded_disclosure_matches_plain_roster`
and `::test_build_roster_folds_accents_so_plain_disclosure_matches` (both
directions of the accent disagreement). NY suite green; ruff clean.

# `compendium/_deprecated/v1/` — Compendium 1 (deprecated 2026-05-14)

These files are **deprecated**. Use [`../disclosure_side_compendium_items_v2.tsv`](../disclosure_side_compendium_items_v2.tsv) instead.

| File | Origin |
|------|--------|
| `disclosure_items.csv` | 141-row Compendium 1 (post-v1.2 schema bump, 2026-04-30 → 2026-05-01). Structurally PRI-shaped despite Decision Log D9's rubric-neutral row_id renaming. |
| `framework_dedup_map.csv` | Audit trail mapping each `disclosure_items.csv` row back to the source rubrics that introduced it (PRI / FOCAL / Sunlight / etc.). |

## Why v1 was deprecated rather than patched

The 2026-05-02 v3 audit on `statute-extraction` (the predecessor of `compendium-source-extracts`) ran two parallel auditors with reconciliation against the 141-row v1.2 compendium. Results:

- **186 concerns raised**
- **109 of 141 rows flagged**
- **24.2% inter-auditor agreement**

The audit became evidence the compendium needed **rebuilding from sources**, not patching. The structural finding:

> The compendium's seed was PRI's rubric structure; later rubrics (FOCAL, Newmark, Opheim, Sunlight, CPI Hired Guns, OpenSecrets) got integrated by mapping their items onto PRI-shaped rows. D9 renamed the IDs to be rubric-neutral; the row *shape* never got renamed.

Empirical reason to suspect the bias was load-bearing: Newmark 2017's published r = 0.04 CPI↔PRI-disclosure correlation. Two of the most-cited disclosure measures correlate at essentially zero — meaning any single rubric's atomization is likely to mask frame-overfitting.

## What replaces v1

Compendium 2.0, built on the `compendium-source-extracts` branch (2026-05-02 → 2026-05-14, merged to main as `cac1469`):

- **181 rows** (180 firm + 1 path-b unvalidated; down from v1's 141 rows but with a **completely different shape** — cell-typed observables across `legal` and `practical` axes rather than yes/no diagnostic items).
- Each row backed by **one or more** of 9 source rubrics treated on even footing (PRI 2010, CPI Hired Guns 2007, CPI 2015, Sunlight 2015, Newmark 2005, Newmark 2017, Opheim 1991, FOCAL 2024, OpenSecrets 2022 [tabled], LobbyView 2018/2025 [schema-coverage]).
- Most-validated row: `lobbyist_spending_report_includes_total_compensation` (read by all 8 score-projection rubrics).
- 30-decision freeze log at [`docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md`](../../docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md).
- Pre-merge factual audit on the 3 load-bearing source-rubric summaries (Newmark 2017 / FOCAL / PRI 2010) confirmed accuracy: 1 real FOCAL correction (contact-log 13/15 restored), 1 FOCAL clarity tightening (openness 11/15 vs open-data sub-theme 9/15), 1 Newmark 2017→2005 sourcing nit.

## Retention rationale

These files are **not deleted** because:

1. They are the *evidence* for why the rebuild was needed (rule: never delete experiment data without explicit permission; analytical artifacts get archived, not removed).
2. The `framework_dedup_map.csv` records which source rubrics each v1 row claimed to draw from — useful historical lookup if anyone wants to compare v1's claimed cross-rubric coverage against v2's actual coverage.
3. The v1 loader (`load_v1_compendium_deprecated()` in `src/lobby_analysis/compendium_loader.py`) still exists so PRI-projection-MVP code (`cmd_build_smr` subcommand, `smr_projection` module) keeps working until `phase-c-projection-tdd` retires it.

If you encounter code or docs still referencing v1, surface the gap and migrate to v2 — do not silently rewrite v1 data.

# 20260514_naming_taxonomy_kickoff

**Date:** 2026-05-14
**Branch:** compendium-naming-docs

## Summary

Kickoff session for the `compendium-naming-docs` branch, addressing GH issue [#9](https://github.com/danparshall/lobby_analysis/issues/9): document the Compendium 2.0 row-naming taxonomy and trace every name to its origin. The issue had been opened earlier the same day, carried out of sub-1 of the `phase-c-projection-tdd` rubric-plans-drafting convo.

Scope was locked at kickoff to **audit + flag, defer renames** (Option A of two presented) to keep merges clean on the parallel-running sister branches (`phase-c-projection-tdd`, `extraction-harness-brainstorm`, `oh-statute-retrieval`). The argument for deferral: any rename of a row that appears in a projection-mapping doc, a (future) v2 Pydantic model, or a prompt string forces a multi-branch update. The audit can surface candidates without absorbing that cost; a future rename-execution branch can batch the actual renames timed against sister-branch lifecycles.

Three artifacts produced and committed (`0e94f37`):

1. **`compendium/NAMING_CONVENTIONS.md`** (362 lines) — the deliverable for issue #9. 13 sections covering: row-ID shape; top-level prefix families (20 distinct 1-token prefixes covering 181 rows); strong 3-token families (19 families with ≥2 members covering 147 of 181 rows); the `def_target_*` / `def_actor_class_*` / `actor_*` triangle (D25); the α form-type split (D3); joint-actor rows (D7); the three-threshold framework (D4); axis conventions; cell-type suffix hints; **8 rename candidates in §10**; prefix-choice decision tree (§11); per-row provenance pointer; maintenance.
2. **`results/20260514_prefix_survey.{py,md}`** (175 + 406 lines) — empirical prefix histogram at 1/2/3-token granularity, family membership listing, cross-tabs (prefix × cell_type / axis / `first_introduced_by`).
3. **`results/20260514_provenance_table.{py,md}`** (216 + 319 lines) — per-row provenance generator + table. Programmatically credits each of 181 rows to its `first_introduced_by` projection-mapping doc and any of D1–D30 that name it explicitly. 60 of 181 rows have D-decision refs; the remaining 121 survived the freeze unchanged with provenance fully in their projection-mapping doc.

## Topics Explored

- Whether to handle renames on this branch (Option A audit-only) vs. execute them in-band (Option B). Locked Option A.
- Whether to check `extraction-harness-brainstorm`'s compendium delta before cutting (the issue had flagged this as a TODO). User said skip and proceed.
- Empirical prefix structure of the 181 v2 row IDs — 1-token, 2-token, 3-token granularities; cross-tabs against `cell_type`, `axis`, `first_introduced_by`.
- The naming-decision history encoded in D1–D30 of the row-freeze log (8 of 30 decisions are explicit naming canonicalizations: D1–D8). Mapped each D-decision to the rows it names by string match.
- Where the v2 row-naming conventions are **systematically inconsistent** (vs. minor cosmetic drift) — produced the list of 8 rename candidates in §10 of NAMING_CONVENTIONS.md.
- How to make per-row provenance machine-readable rather than 181 hand-written entries (programmatic generator over TSV + freeze-decisions doc).

## Provisional Findings

- The compendium's row-naming conventions are **mostly consistent**, with the structural anchors (3-token families like `lobbyist_spending_report_*`, `principal_spending_report_*`, `lobbying_search_filter_*`, `lobbyist_reg_form_*`, `lobbying_contact_log_*`) holding cleanly across 147 of 181 rows.
- The inconsistencies that survived the freeze are concentrated in **two patterns**: (a) D3's rename rule was scoped to PRI E1/E2 atomic-items, so FOCAL/Newmark/LobbyView-introduced rows with the same `_report_includes_*` shape were skipped (5–6 rows); (b) the three-threshold framework (D4) didn't fully back-rename the lobbyist-status threshold trio (`compensation_/expenditure_/time_threshold_for_lobbyist_registration` — 3 high-traffic rows that don't share a prefix with each other or with `lobbyist_registration_*`).
- The `actor_*` family (11 rows) is structurally flat at the 1-token level — every member has a singleton 2-token prefix (`actor_executive_*`, `actor_governors_*`, etc.). This matters for any tooling that groups by 2-token prefix: the family identity must be read at the 1-token level. Fixed mid-session in the provenance-table generator.
- **The TSV's `first_introduced_by` + `notes` columns already carry most of the per-row provenance** — issue #9's "per-row provenance" deliverable is largely a matter of making that machine-readable, not hand-curating 181 entries.
- An incidental docs-drift finding: `compendium/README.md` lists `cpi_2015_projection_mapping.md` but the actual file is `cpi_2015_c11_projection_mapping.md`. Logged as issue #8 in NAMING_CONVENTIONS.md §10.

## Decisions Made

- **Audit + flag, defer renames** — locked at kickoff. Executable renames stay out of scope for this branch.
- **Skip sister-branch compendium-delta check** before cut (the issue's pre-launch TODO). Deal with coordination cost at merge time.
- **Programmatic per-row provenance** rather than hand-curated. Generator at `results/20260514_provenance_table.py` is re-runnable against the TSV's authoritative `first_introduced_by` + `notes`.
- **Land everything in one commit** (`0e94f37`) rather than per-artifact, since the artifacts cross-reference each other.
- **No PR opened, no GH issue #9 comment, no test run** — per user's discretion at the audit-v1 review point. Branch pushed to `origin/compendium-naming-docs` for backup and visibility.

## Results

- [`results/20260514_prefix_survey.py`](../results/20260514_prefix_survey.py) — reproducible prefix-survey generator
- [`results/20260514_prefix_survey.md`](../results/20260514_prefix_survey.md) — survey output (1/2/3-token histograms + cross-tabs + full family membership listing + 34-row singleton-prefix list)
- [`results/20260514_provenance_table.py`](../results/20260514_provenance_table.py) — per-row provenance generator
- [`results/20260514_provenance_table.md`](../results/20260514_provenance_table.md) — provenance table (181 rows × {row_id, 2-tok family, first_introduced_by, D-refs, notes excerpt}) + family-grouped summary with 1-tok→2-tok nesting
- [`../../../compendium/NAMING_CONVENTIONS.md`](../../../../compendium/NAMING_CONVENTIONS.md) — the deliverable (committed to repo-root `compendium/` as a sibling of `README.md`)

## Open Questions

- **Which of the 8 rename candidates should actually execute** (vs. defer indefinitely vs. reject)? Each has different coordination cost — Issue 1 is trivial (1 single-rubric row); Issue 2 spans 5–6 rows including the FOCAL-introduced joint-actor trio; Issue 3 is the heaviest (3 high-traffic rows, one 6-rubric and two 4-rubric, load-bearing for HG Q2's D22 projection). Next-session work.
- **Should `tools/freeze_canonicalize_rows.py` be extended with a D31+ rename-execution batch** as the mechanism for rename execution (preserving idempotent regen), or should the rename branch directly edit the v2 TSV and accept that the script becomes lossy until backfilled? Pending the rename-execution session.
- **Will any of the rename candidates collide with extraction-harness-brainstorm's v2 Pydantic model design** (which is the other planned consumer of the row names)? Not investigated this session.

## Next Steps (handoff)

Walk Dan through the 8 rename candidates in §10 of `compendium/NAMING_CONVENTIONS.md` one at a time (accept / defer / reject for each), then draft a rename-execution plan at `plans/20260515_rename_execution_plan.md` enumerating the accepted set plus each rename's downstream-consumer fan-out (TSV regen path, projection-mapping doc cross-refs, future `extraction-harness-brainstorm` Pydantic models, prompt strings).

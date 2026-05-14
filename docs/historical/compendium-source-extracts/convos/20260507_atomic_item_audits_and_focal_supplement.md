# Atomic-item audits (Phase A1-A4) + Lacy-Nichols 2025 supplementary extraction

**Date:** 2026-05-07 (pm)
**Branch:** compendium-source-extracts
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) — Phase A only.

## Summary

Executed Phase A of the atomic-items + projections plan: parallel atomic-item audits of OpenSecrets 2022, LobbyView (Kim 2018/2025), Sunlight 2015, and the Lacy-Nichols 2025 supplementary file extraction. Mid-session: the file at `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` turned out to be the *2024* IJHPM paper's database-search supplementary, not the 2025 Milbank paper's Tables 3/4/5 — agent error from session prep, surfaced when the A4 agent reported. First A4 pass populated FOCAL scoring rules using main-paper Figure 3 max-observed inference (US row sanity check passed at 81/182 = 45%); second pass tried Wiley web-fetch (blocked: 403 / timeout / archive.org refused / PMC embargoed); third pass executed after user manually downloaded the actual supplementary file as two .docx files which I pandoc-converted to text.

The OpenSecrets verdict was overturned mid-session after user pushback — the first audit framed "drop, methodology is analyst-judgment-only", but a re-audit found the article's Rankings narrative includes 5 worked-example states + population-level statistical anchors that pin the ordinal at multiple points. New verdict: keep, with 75% of score mass projectable.

The Sunlight verdict was a per-item judgment call after user supplied the rule "if we can cleanly map our compendium items onto the rubric, then fine. Drop anything we can't" — items 1, 2, 3, 5 are clean (binaries / single enum), item 4 (Document Accessibility) is excluded because its 5-tier ordinal conflates 3-4 sub-features and tier -1/-2 is a documented near-typo.

Phase A is now locked. Phase B (per-rubric projection mappings) handoff written.

## Topics Explored

- Phase A dispatch architecture: 4 parallel `general-purpose` subagents (A1 OpenSecrets / A2 LobbyView / A3 Sunlight / A4 Lacy-Nichols supplementary), each with self-contained briefs covering scope, working files, expected artifacts, drop-rule reminders, and hard constraints (no PRI 2010, no git commit, no out-of-scope writes).
- A1 OpenSecrets — first audit found "no atomic items, drop". User pushback led to recheck specifically asking whether tier definitions or worked examples exist anywhere in the article. Recheck found 5 named worked-example states + statistical anchors; verdict overturned.
- A2 LobbyView — agent walked Kim 2018 paper + Kim 2025 paper + LobbyView Python package GitHub source. 46 schema fields written; superset of existing items_Kim2018.tsv. Three ambiguities flagged (lobbyist_id public-API gap, Kim 2018 bill-detection has no published P/R, bill_position is Wisconsin-only).
- A3 Sunlight — agent confirmed the 5 items are simultaneously headline categories AND atomic scoring units (Sunlight does not score below this granularity). Per-item judgment surfaced item 4's near-typo + dimensional conflation; user applied "drop what we can't cleanly map" rule.
- A4 Lacy-Nichols — three-pass execution. First pass: main-paper Figure 3 inference, US row exact match (45%). Second pass: Wiley web-fetch blocked on every route. Third pass: user manual download → pandoc docx→txt → second extraction agent populated all 50 indicators with verbatim weights, closed all 8 weight-UNKNOWNs, caught 2 weight-decomposition conflicts, populated 50-row prior-framework mapping CSV, reconciled 1,372-cell per-country matrix.
- Internal supplement-vs-Figure-3 discrepancy: Suppl Table 5's "TOTAL out of 100pts" row doesn't match Figure 3 (US Table 5 says 42, Figure 3 says 45). Computing Table 5 raw × Table 4 weights reproduces Figure 3 exactly for all 28 countries → Figure 3 is authoritative; Table 5 TOTAL row is wrong. Documented in audit.

## Provisional Findings

- **OpenSecrets's article narrative is structurally informative beyond the methodology block.** First audit looked at lines 196-216 (methodology) and treated "depending on the individual circumstances" as terminal. Lines 221-245 (Rankings narrative) are where the ordinal gets pinned via worked examples — agent missed this on first pass. Lesson: methodology blocks can be misleading on shallow rubrics; the rest of the article often constrains the ordinal.
- **Sunlight's 5-criterion structure is intentionally shallow** — not "headline categories with atomic items waiting to be found" but a designed-flat rubric. The compendium-mapping question is per-item: can the rubric tier be a deterministic function of compendium cells? Yes for 4 of 5; no for item 4.
- **L-N 2025 Suppl File 1 is dramatically richer than the plan anticipated** — contains all three target tables (verbatim per-indicator scoring rules with P/N criteria, cross-rubric weight mapping, 28×50 per-country score matrix). Phase A4's "may need to fall back to Option C" was overkill; the supplementary closes everything cleanly.
- **The Wiley web-fetch route is solidly blocked** (403 on all DOI variants, timeout on Milbank, archive.org refused, PMC embargoed until 2026-09-01). For future Wiley supplementaries, plan for manual user download, not web-fetch.
- **Pandoc handles Wiley supplementary docx cleanly** — the docx→txt conversion preserved table structure well enough that a downstream agent extracted verbatim cell content without round-trips.
- **The first A4 pass's Figure-3-inferred weights were 40/42 correct** against the verbatim Suppl Table 4 weights. The 2 conflicts (`financials.3`, `financials.8`, both 1→2) didn't change Figure 3 cell values; only the (weight × raw) decomposition was off.
- **Finland's published total drops 70 → 46 weighted** after Suppl Table 5 reconciliation — 13 cells previously read as 0 in Figure 3 are actually "/" (unassessable) per the verbatim source. This is Figure-3-visual-reading error, not a meta-finding about the rubric.

## Decisions Made

| Topic | Decision |
|---|---|
| **OpenSecrets** | KEEP — partial (75% score-mass projectable). Cat 1 binary, Cats 2/3 few-shot anchored, Cat 4 decomposed. |
| **LobbyView** | KEEP — schema-coverage rubric (different shape from score-projection rubrics). 46 fields. items_Kim2018 retained alongside as per-paper extract. |
| **Sunlight** | KEEP items 1, 2, 3, 5; DROP item 4 from projection layer (left in source-extract TSV). Per-item rule: clean-map ⇒ keep. |
| **FOCAL** | KEEP — fully populated from verbatim Suppl File 1 weights. US row anchor = 81/182 = 45%. Federal LDA validation jurisdiction. |
| **Phase C order** | CPI 2015 C11 first (smallest concrete target, 14 items), then PRI 2010 (largest, hardest aggregation). Other rubrics in plan order. |
| **Phase C scaffolding** | `tests/fixtures/projection_inputs/<rubric>_<state>_<vintage>.json` for hand-population; `src/lobby_analysis/projections/<rubric>.py` for code modules. |
| **Phase B handoff** | Written at `plans/_handoffs/20260507_phase_b_handoff.md` — supplements plan with what's locked since Phase A. |

## Results

- `results/items_LobbyView.tsv` — 46 LobbyView federal LDA schema fields (Phase A2)
- `results/items_LobbyView.md` — methodology note for items_LobbyView.tsv
- `results/items_FOCAL.tsv` — updated: 50/50 indicators with verbatim weights from Suppl File 1
- `results/items_FOCAL.md` — updated with verbatim-source methodology section
- `results/focal_2025_lacy_nichols_per_country_scores.csv` — 1,372 (country, indicator) cells with raw + weighted scores (verbatim from Suppl Table 5)
- `results/focal_2025_lacy_nichols_prior_framework_mapping.csv` — 50 rows mapping FOCAL indicators to Bednarova/CPI/Roth weights (verbatim from Suppl Table 4)
- `results/opensecrets_worked_examples_2022.csv` — 18 rows of state-level worked examples + verbatim quotes + line refs (Phase A1-recheck)
- `results/20260507_opensecrets_atomic_audit.md` — original drop audit (kept as appendix)
- `results/20260507_opensecrets_recheck.md` — supersedes drop verdict; per-cat projectability documented
- `results/20260507_sunlight_atomic_audit.md` — Phase A3 audit + user decision section locking 4-of-5 scope
- `results/20260507_focal_a4_audit.md` — Phase A4 audit covering all three passes + Table-5-vs-Figure-3 discrepancy
- `papers/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_001.docx` — Suppl File 1 (containing Tables 3/4/5)
- `papers/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_002.docx` — Suppl File 2 (tobacco case study, out of scope)
- `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_001.txt` — pandoc text extract (738 lines)
- `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_002.txt` — pandoc text extract (1,327 lines)
- `plans/_handoffs/20260507_phase_b_handoff.md` — Phase B handoff for the next implementing agent

## Mistakes recorded

1. **Pre-flight misidentification of the Lacy-Nichols supplementary file.** Asserted "the file is already on disk" based on filename `Lacy-Nichols-Supple-File-1-IJHPM.pdf` without checking it was the right paper. The IJHPM token in the filename was a giveaway it was the 2024 paper, not the 2025 Milbank paper. Caught when the A4 agent reported the file was the 2024 search-strategies supplementary, not Tables 3/4/5. Cost: one wasted agent dispatch + one Wiley web-fetch attempt that was destined to fail. Mitigation for future: read the first page of any "already-on-disk" supplementary file before asserting it's the right one.
2. **Used cd+git compound (`cd <worktree> && git status`) early in session despite CLAUDE.md explicitly calling out the heuristic that blocks it.** User pushback led to memory entry `feedback_use_preapproved_bash_patterns.md` and switched to `git -C <path>` for all subsequent git ops.
3. **First A1 OpenSecrets audit was incomplete** — only walked the methodology block, not the Rankings narrative. User pushback forced a recheck that overturned the drop verdict. Useful precedent: when a published methodology says "depending on circumstances", the rest of the article narrative often pins the ordinal via worked examples — check there before declaring rubric unprojectable.

## Next Steps

1. **Phase B starts here.** Read `plans/_handoffs/20260507_phase_b_handoff.md` first, then the plan. Build per-rubric `<rubric>_projection_mapping.md` docs starting with CPI 2015 C11. Union of all `compendium_rows` across mappings is saved as `results/projections/disclosure_side_compendium_items_v1.tsv`.
2. After Phase B is complete, Phase C implements projection functions in code (`src/lobby_analysis/projections/<rubric>.py`) under TDD.
3. **Open option (Phase A leftover):** OpenSecrets state-map widget JS pull would close Cat 1 projectability. Currently Cat 1 is "binary baseline-3-vs-4" — sufficient for Phase B mapping; revisit only if Phase C validation shows the binary doesn't reach published per-state Cat-1 scores.

## Open Questions

- LobbyView's projection shape is "schema-coverage check, not score computation" — the existing `f_rubric(compendium_cells, vintage) → rubric_score` shape doesn't fit. Phase B will need to define a separate output shape for LobbyView (`coverage_map: {field → has_compendium_row?}`). Resolved at the level of "tackle LobbyView last and adapt" but the data structure isn't designed yet.
- The internal Suppl Table 5 vs Figure 3 TOTAL row discrepancy is documented but the cause isn't fully diagnosed — it could be a published-table arithmetic error in L-N 2025, or it could be a different aggregation rule (e.g., normalization that I haven't reverse-engineered). Figure 3 is authoritative for project use, but the discrepancy is worth noting if anyone cites L-N 2025's Suppl Table 5 totals directly.
- Whether to do the OpenSecrets map-widget JS pull in Phase B (as input prep) vs Phase C (as remediation if validation fails) is a sequencing choice; punted as "do it lazily" for now.

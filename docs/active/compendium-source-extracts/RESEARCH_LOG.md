# Research Log: compendium-source-extracts

Created: 2026-05-02
Purpose: Rebuild the project's compendium of disclosure-law indicators by extracting items independently from each non-PRI source-framework paper, with PRI 2010 fully excluded. The compendium-as-shipped (141 rows) is structurally PRI-shaped: row count, atomization decisions, and verbatim descriptions all derive from PRI's question hierarchy because PRI was the seed rubric and later rubrics were tucked in as `framework_references` on PRI-shaped rows. The 2026-05-02 v3 audit on `statute-extraction` (186 concerns / 24.2% inter-auditor agreement) made this concrete and the user pivoted from "audit + patch" to "rebuild from sources."

> **⛔ AGENT-CRITICAL: PRI 2010 is out of bounds for this branch.** Do not read `papers/text/PRI_2010__state_lobbying_disclosure.txt`, do not open `compendium/disclosure_items.csv` or `framework_dedup_map.csv`, do not "calibrate against PRI" anywhere. PRI may appear as a name in predecessor-citation lists in extracts; that is the only context. The user has explicitly registered strong frustration about repeated agent-side defaulting to PRI as the structural foundation. See the top-of-file `⛔ AGENT-CRITICAL` block in `STATUS.md` for the full posture. This rule is non-negotiable until compendium-2.0 lands and the user explicitly clears it.

Carry-forward signals (informational, not gates):
- The Phase 0 audit deliverable on `statute-extraction` (`docs/active/statute-extraction/results/20260502_compendium_audit_*`) is **historical evidence the rebuild was needed, not a fix-list**. Do not read it for guidance; it is PRI-shape-aware in ways that bias the rebuild.
- The harness work on `statute-extraction` (iter-2 onward) is paused until compendium-2.0 lands. Iter-2's tightened `definitions` row descriptions would need redoing post-2.0.
- The `papers/text/` corpus contains both the 7 originally-scoped framework papers and (as of 2026-05-02) ~16 additional candidate framework/review papers that were added to the worktree by a parallel process. Their inclusion in the rebuild scope is an open question for user resolution; see the locked plan's Open Question 1.

---

## Sessions

(Newest first.)

### 2026-05-02 (pm) — Branch creation + per-paper extraction plan

**Convo:** [`convos/20260502_pm_compendium_rebuild_pivot.md`](convos/20260502_pm_compendium_rebuild_pivot.md)
**Plan produced:** [`plans/20260502_per_paper_source_extraction.md`](plans/20260502_per_paper_source_extraction.md)
**Spawning artifact:** the v3 audit on `statute-extraction` (`docs/active/statute-extraction/results/20260502_compendium_audit_concerns.md`) — but the audit is **not a fix-list**; it is evidence-of-need.

#### Topics Explored

- Walk-through of the v3 Phase 0 audit's tag-disagreements (NON_COMPENSATION broader-vs-narrower, DEF_PUBLIC_ENTITY axis-ambiguous-vs-misleading, DEF_ADMIN_AGENCY rubric-ambiguous-vs-broader). Recognition that surface tag-disagreements were symptoms of two assumption-breaks in the audit's C1/C2 taxonomy: rows aren't all axis-typed, and `framework_references` clusters aren't all homogeneous.
- Recognition of structural PRI privilege in the compendium: 4-row DEF_PUBLIC_ENTITY family (PRI Q-C parent + 3 sub-criteria), 12-row FREQ_* (PRI E1h/E2h enumeration), 11-row REG_*-A-series (PRI A1–A11), 8-row RPT_*_NON_COMPENSATION/OTHER_COSTS/etc. (PRI E1f i/ii/iii/iv split × 2 sides), and a literal `?.` formatting artifact on ~24 rows (mechanical evidence of script-translated PRI text). Vocabulary fix in D9 was insufficient; structural rebuild required.
- Pivot decision: rebuild from non-PRI source papers, in each paper's own structure, with no carry-over from the existing compendium or any prior PRI-derived CSVs.
- Per-paper artifact spec: TSV (machine-readable) + MD (human-readable methodology summary). Output path `docs/active/compendium-source-extracts/results/items_<Paper>.{tsv,md}`. Rubric-native vocabulary; no domain assignment, no axis-tagging, no cross-paper mapping.
- Sequencing: template-first (one paper foreground, user format review) → parallel-dispatch remaining papers → per-paper user review → stop. Compendium-2.0 design is a separate plan written after all reviews are in. Predecessor-framework chase is a separate plan written after extracts ship.

#### Provisional Findings

- The compendium 1.x is unsalvageable as a foundation for compendium-2.0 design. Patches to row names, descriptions, or domain assignments leave the structural PRI-shape intact.
- D9's vocabulary de-PRI-ing was necessary but not sufficient — the row *atomization* itself is PRI's, and that requires source-paper rebuild.
- The ~16 additional papers (international/EU lobbying-regulation frameworks + review pieces) discovered untracked on the worktree at session-end materially expand the candidate source-paper universe beyond the 7 originally scoped. User triage needed before extraction dispatches.

#### Decisions

| topic | decision |
|---|---|
| Compendium 1.x posture | Frozen; soft-deprecated by compendium-2.0 work on this branch |
| PRI 2010 status | Fully excluded. Not "de-privileged"; ignored. No PRI text in any extract; PRI only appears as a citation name in predecessor lists |
| Source extraction posture | Re-extract every paper from scratch. Ignore prior CSVs (`focal_2024_indicators.csv`, Sunlight data CSV, pri-rubric CSVs). Compendium itself is off-limits as a seed |
| Format | TSV + MD per paper. `items_<Paper>.tsv` + `items_<Paper>.md` |
| Output location | `docs/active/compendium-source-extracts/results/` |
| Sequencing | Template-first, then parallel; user reviews each |
| Compendium-2.0 design | Separate plan, written after all per-paper reviews are in |
| Predecessor-framework chase | Enumerate-only in per-paper MDs; chase decision deferred |
| `statute-extraction` iter-2 of harness | Paused until 2.0 |
| Phase 0 audit doc on `statute-extraction` | Retained as historical evidence; supersession marker added on plan; canonical concerns doc + reconciliation note unchanged |
| STATUS.md PRI bar | Added top-of-file on this branch's STATUS.md; cherry-picked to `statute-extraction`'s STATUS.md |
| Auto-memory | `feedback_pri_not_privileged.md` updated to extend the rule from vocabulary to structure |

#### Mistakes recorded

For honesty + future-session protection:

1. **Missed structural PRI privilege repeatedly.** When user asked about the D11 concern, assistant framed it as PRI-neutral on the basis that row IDs were rubric-neutral. Failed to recognize that the row *atomization* itself was PRI's. Memory `feedback_pri_not_privileged.md` had the vocabulary lesson but assistant didn't generalize. The auto-memory has been updated to make the structural lesson explicit.
2. **Dispatched template extraction agent at wrong path/format** before the user clarified `results/items_<Paper>.tsv`. Agent wrote to `papers/extracts/Opheim_1991.{csv,md}` (wrong dir, wrong extension). Files have been deleted as part of session-end cleanup.
3. **Tried to redirect the in-flight agent** via `SendMessage`, but the tool was not in the assistant's surface; ToolSearch returned no match. User stopped execution.
4. **Conversation context too saturated** by end-of-session for clean execution. User explicitly: "you aren't capable of doing the work with your context as-is. Your job is to write the plan."

#### Next Steps

- User reviews the locked plan at `plans/20260502_per_paper_source_extraction.md` and resolves its 7 open questions, especially Open Question 1 (the universe of source papers — now potentially much larger than 7 given the ~16 untracked additions).
- After plan acceptance, fresh-context implementing agent executes per the plan: dispatches one template paper, surfaces for user format review, then dispatches the remaining papers in parallel.
- After all per-paper reviews are in, a follow-up plan is written for compendium-2.0 design (not part of this plan).

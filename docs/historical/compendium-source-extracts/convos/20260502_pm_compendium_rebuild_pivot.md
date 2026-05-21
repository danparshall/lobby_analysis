# 2026-05-02 (pm) — Compendium audit walkthrough → rebuild pivot

**Branch (during):** `statute-extraction`
**Branch (after pivot):** `compendium-source-extracts` (new, off origin/main)
**Status:** Closed; conversation pivoted from "audit + patch" to "rebuild from sources"
**Spawning artifact:** [`docs/active/statute-extraction/plans/20260502_compendium_item_audit_v3_phase0.md`](../../statute-extraction/plans/20260502_compendium_item_audit_v3_phase0.md) (now superseded for compendium-design purposes)

## Summary

Session opened on `statute-extraction` to execute the v3 Phase 0 compendium audit per the plan written earlier the same day. Two parallel auditor subagents + a reconciliation pass produced the canonical concerns doc (186 concerns / 109 of 141 rows flagged / 24.2% inter-run agreement). User and assistant walked through the tag-disagreements concretely. The walkthrough surfaced — through the assistant repeatedly missing it, until the user said it directly — that the compendium is **structurally** PRI-shaped, not just lexically PRI-flavored. D9's vocabulary de-PRI-ing (rubric-neutral threshold-row IDs) was necessary but not sufficient: the row *count*, *atomization*, and *descriptions* still derive from PRI's question hierarchy because PRI was the seed rubric and later rubrics got tucked in as `framework_references` on PRI-shaped rows.

User declared the patch path the wrong shape of work and pivoted: rebuild from each source paper independently, ignore PRI entirely, no carry-over from the existing compendium. Conversation context exhausted by accumulated mistakes; user stopped execution and asked for a plan referencing this conversation. The implementing agent works from a fresh context.

## Topics Explored

- **Phase 0 audit execution.** Two parallel auditors ran the full 141-row sweep against C1–C5 criteria; reconciliation produced 45 strict-agreement concerns, 9 tag-disagree (row_id, criterion) keys, 46 run1-only, 77 run2-only.
- **Tag-disagreement walkthrough.** Three clusters examined:
  - `RPT_*_NON_COMPENSATION × C2` (run1=description-broader-than-rubric / run2=description-narrower-than-rubric, opposite directions): description matches PRI E1f.ii / E2f.ii verbatim. Disagreement is artifact of cluster heterogeneity (PRI says one sub-component; FOCAL 7.6 = total expenditure; Sunlight = 4-tier rollup). Right tag is C3 `cluster-asks-two-questions`, not either C2 sub-tag. Diagnostic: when both broader and narrower are arguable, the underlying issue is heterogeneous refs not boundary fuzziness.
  - `DEF_PUBLIC_ENTITY` family + `EXEMPT_GOVT_OFFICIAL_CAPACITY × C1` (run1=axis-ambiguous-name / run2=name-misleading): C1's axis taxonomy doesn't apply — these rows aren't axis-typed. The DEF_PUBLIC_ENTITY family's real concern is C5 wrong-domain (`DEF_*` prefix in `domain="registration"`); EXEMPT_GOVT_OFFICIAL_CAPACITY was over-flagged. Diagnostic: C1 needs an "is this row axis-typed at all" gate.
  - `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × C2` (run1=rubric-source-ambiguous / run2=description-broader-than-rubric): both are correct, capturing different concerns about the same row. Reconcile by retaining both tags, not picking one.
- **Structural PRI privilege.** Concrete evidence:
  - `DEF_PUBLIC_ENTITY` family is *4 rows* (parent + 3 sub-criteria) because PRI Q-C had parent + 3 sub-items. No other rubric demands this 4-row split.
  - 12 `FREQ_*` rows (6 cadences × 2 sides) is PRI E1h/E2h's enumerated list. Newmark uses `freq_binary` (one categorical). FOCAL doesn't atomize at this granularity.
  - 11 `REG_*-A-series` rows are PRI A1–A11. FOCAL 1.1 covers the same conceptual ground via *one* AND-disjunction.
  - PRI's E1f i/ii/iii/iv split → 4 rows × 2 sides = 8 RPT_* rows.
  - ~24 rows have the literal `?.` formatting artifact: a script appended `.` to PRI item_text without stripping the trailing `?`. Mechanical evidence the compendium was bootstrapped from PRI's rubric.
  - The `*_NON_COMPENSATION` C2 disagreement is itself a symptom: row was built from PRI's E1f.ii; FOCAL/Sunlight got tucked in as cross-refs but didn't fit the PRI-shape.
- **D11 explanation + scope question.** User asked what D11 was; assistant explained the v1.2 schema bump (added `domain="definitions"`, split BOOLEAN threshold rows along inclusion/exemption with `DEF_*_STANDARD` ↔ `THRESHOLD_LOBBYING_*_PRESENT`, asymmetric on the `_VALUE` rows + missing compensation `_VALUE`/exemption rows). Assistant initially framed the D11 NUMERIC-asymmetry concern as PRI-neutral ("auditors are exposing residual asymmetry, not match-PRI"). User pushed back: this is still PRI-privileging. The compendium's *atomization* is PRI's; the inclusion/exemption asymmetry exists because PRI's BOOLEAN/NUMERIC bundling shaped the v1.x schema and v1.2's fix was incomplete.
- **Pivot scope.** User decision: ignore the existing compendium and PRI entirely; extract from each non-PRI source paper independently from the paper text alone; user reviews each extract personally; only after all reviews are in does data-object-2.0 design begin.
- **Branch + scaffolding.** New branch `compendium-source-extracts` off origin/main; worktree at `.worktrees/compendium-source-extracts/`. Phase 0 audit deliverable on `statute-extraction` becomes evidence-of-need, not fix-list.

## Provisional findings

- The 24.2% inter-run agreement on the audit was largely artifact of two assumption-breaks in the C1/C2 taxonomy (rows aren't axis-typed; `framework_references` clusters aren't homogeneous). Phase 1's taxonomy-refinement step would have collapsed many of the tag-disagrees — but that line of work is now superseded.
- Compendium 1.x is unsalvageable as a foundation. Patches to row names, descriptions, or domain assignments leave the structural PRI-shape intact.
- Vocabulary de-PRI-ing (D9) ≠ structural de-PRI-ing. The latter requires re-examining row count + atomization decisions per topic, not just renaming.
- The 186-concern canonical doc + reconciliation note remain as historical evidence; they should not be deleted but should be marked superseded once compendium-2.0 lands.

## Decisions

| topic | decision |
|---|---|
| Compendium 1.x posture | Frozen; soft-deprecated by compendium-2.0 work on a new branch |
| New branch | `compendium-source-extracts` off `origin/main` (already created) |
| PRI 2010 | **Fully excluded** from compendium-2.0 work. Not "de-privileged"; ignored. No reading PRI text, no comparison, no PRI item-IDs in extracts (predecessor citations may name PRI; nothing more) |
| Source extraction posture | Re-extract every paper from scratch from `papers/text/` only. Ignore all prior CSVs (`focal_2024_indicators.csv`, Sunlight data CSV, any pri-rubric CSVs). The compendium itself is off-limits as a seed |
| Format | TSV + MD per paper; rubric-native vocabulary (no domain assignments, no axis tags, no cross-paper mapping) |
| Output location | `docs/active/compendium-source-extracts/results/items_<Paper>.{tsv,md}` |
| Filename | `items_<Paper>.tsv` and `items_<Paper>.md` (e.g., `items_Opheim_1991.tsv`) |
| Sequencing | Template-first: one paper foreground, user reviews format, then 6 parallel; user reviews each extract |
| Predecessor-framework chase | Enumerate-only in per-paper MDs; chase decision deferred to a follow-up audit after all 7 ship |
| Compendium-2.0 design | Separate plan, written *after* all 7 paper reviews are in. Not part of this plan |
| `statute-extraction` iter-2 of harness | Pause until 2.0 lands |
| Phase 0 audit doc + reconciliation | Retained as historical evidence; mark superseded after 2.0 ships |

## Mistakes recorded

For honesty + future-session context:

1. **Missed structural PRI privilege repeatedly.** When user asked about the D11 concern, assistant framed it as PRI-neutral on the basis that row IDs were rubric-neutral. Failed to recognize that the row *atomization* itself was PRI's. Memory `feedback_pri_not_privileged.md` had the vocabulary lesson but assistant didn't generalize to structure. User had to spell it out.
2. **Dispatched template extraction agent at wrong path/format** before the user clarified `results/items_<Paper>.tsv`. Agent wrote to `papers/extracts/Opheim_1991.{csv,md}` (wrong dir, wrong extension). Files exist on the new worktree but are stale; implementing agent should ignore and re-extract per the locked spec.
3. **Tried to redirect the in-flight agent** via `SendMessage`, but `SendMessage` was not in the assistant's current tool surface; ToolSearch returned no match. User stopped execution.
4. **Conversation context too saturated** for clean execution by end-of-session. User explicitly: "you aren't capable of doing the work with your context as-is. Your job is to write the plan."

## Goal of this session

Audit the compendium per the v3 Phase 0 plan. Walk through findings. Decide whether to patch or rebuild.

Outcome: rebuild. Plan written for fresh-context implementing agent.

## Next steps

- User reviews the plan at `plans/20260502_per_paper_source_extraction.md`.
- After plan acceptance, fresh-context implementing agent executes per the plan: dispatches one template paper, surfaces for user review, then dispatches the remaining 6 in parallel.
- After all 7 reviews are in, a follow-up plan is written for compendium-2.0 design (not part of this plan).
- A second follow-up plan (after the compendium-2.0 work begins or completes) handles the predecessor-framework chase decision.

## Plan produced

[`plans/20260502_per_paper_source_extraction.md`](../plans/20260502_per_paper_source_extraction.md)

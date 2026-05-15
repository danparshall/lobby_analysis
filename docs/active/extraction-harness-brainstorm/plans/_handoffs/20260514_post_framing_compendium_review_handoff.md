# Handoff: Compendium 2.0 post-framing review

**Date written:** 2026-05-14
**Originating convo:** [`../../convos/20260514_research_arc_doc.md`](../../convos/20260514_research_arc_doc.md) on `extraction-harness-brainstorm`
**Parallel review:** [`20260514_post_framing_harness_review_handoff.md`](20260514_post_framing_harness_review_handoff.md) — audits `extraction-harness-brainstorm` against the same framing. Reviewers stay in lane; cross-branch reading not required.
**Framing reference:** [`docs/RESEARCH_ARC.md`](../../../../RESEARCH_ARC.md) on main (commit `86dc02e`).

## Context for the spawn

The 2026-05-14 research-arc review session (originating convo above) clarified the project framing in ways the Compendium 2.0 work pre-dates. Compendium 2.0 was frozen 2026-05-13 with 181 cell-typed rows; it was promoted to repo-level `compendium/` on 2026-05-14 (`compendium-v2-promote` merge `0a6804f`); and naming conventions landed on main via PR #10 (`compendium-naming-docs`) the same day. The full body of v2 compendium work — Phase A categorization, Phase B per-rubric projection mappings, row freeze, factual audit, naming conventions — was executed under a less-explicit framing than the one now in `docs/RESEARCH_ARC.md`.

The purpose of this review is **not** to re-open frozen decisions. It is to surface findings that, under the corrected framing, should change what we work on next on the **active downstream branches** (`extraction-harness-brainstorm`, `phase-c-projection-tdd`, `oh-statute-retrieval`). Read-only; report-only; commit one file on the branch you are spawned in.

---

## Prompt (self-contained — execute below as if no other context exists)

You are auditing the Compendium 2.0 work in this repo against a recently-clarified framing of what the project is for. You have zero prior session context; this prompt is self-contained.

### What the project is (clarified 2026-05-14)

Read `docs/RESEARCH_ARC.md` on main first. Two load-bearing claims:

1. **Prong 2 + Prong 3 is the product** (portal extraction → display via GraphQL/MCP). Prong 1 (statute → SMR) is *upstream scaffolding* — produces a typed-cell schema reference that makes Prong 2 cheaper, plus the legal-vs-practical gap is itself a research artifact.

2. **The Ralph loop is Phase C–driven.** Prong 1 has no 50-state ground truth at the typed-cell level. Phase C projects extracted cells back into each rubric's published scoring rule (`f_rubric(SMR_cells) → projected_score`) and compares to the published per-state score. That score-distance is the prompt-iteration gradient.

Compendium 2.0 was built **before** that framing was articulated. The row contract was frozen 2026-05-13 (181 rows × 8 columns). Your job is to check whether what we built actually supports the framing we now have.

### What to read (in this order, calibrated for signal — 1-2 hours total)

1. `docs/RESEARCH_ARC.md` (~213 lines) — authoritative framing.
2. `compendium/README.md` + `compendium/NAMING_CONVENTIONS.md` + the v2 TSV `compendium/disclosure_side_compendium_items_v2.tsv` (header + a sample of rows; don't try to read all 181 rows linearly).
3. `docs/historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md` — the 30 numbered freeze decisions (D1-D30).
4. The 9 per-rubric projection mappings at `docs/historical/compendium-source-extracts/results/projections/*_projection_mapping.md` — skim each, deep-read any that pull a concern.
5. `STATUS.md` for operational context.
6. `docs/active/compendium-naming-docs/RESEARCH_LOG.md` — most recent merge (PR #10), naming-conventions work.

You can read more if a specific question demands it, but don't read the brainstorm convos in full.

### Questions to answer

Answer each. Don't generate generic findings; only flag things outside these questions if they are load-bearing for the framing.

**Q1.** Does the 181-row set support the Ralph loop objective for all 8 Phase C rubrics? For each rubric (CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991, HG 2007, FOCAL 2024), are there enough cells in v2 to compute `f_rubric(SMR) → projected_score`? Missing cells = blocker.

**Q2.** Is the Prong-1 / Prong-2 axis seam clean? The 50 practical-only rows + practical halves of 5 dual-axis rows are supposed to be Prong-2-populated (portal observation). Walk through them. Any actually statute-reading work mislabeled as practical-axis? Vice versa?

**Q3.** Are there cells missing for the legal-vs-practical-gap research artifact? For the gap to be queryable, every row where the legal axis says "X is required" needs a corresponding practical-axis cell answering "does the portal expose X?" Audit asymmetries.

**Q4.** Did the naming-conventions merge (PR #10) introduce inconsistencies vs. the pre-merge projection mappings? The mappings reference rows by name. Spot-check, not exhaustive.

**Q5.** Are there cells in v2 that exist only because Prong 1 was implicitly framed as the product? i.e., cells that wouldn't be in the schema under the "P1 is scaffolding" framing. Flag them; do not propose removal.

### Output

Save your report to:
`docs/historical/compendium-source-extracts/results/20260514_post_framing_review.md`

Structure:

```markdown
# Compendium 2.0 post-framing review

**Date:** 2026-05-14
**Framing reference:** `docs/RESEARCH_ARC.md`
**Originating handoff:** `docs/active/extraction-harness-brainstorm/plans/_handoffs/20260514_post_framing_compendium_review_handoff.md`

## Top 3-5 findings that should change what we work on next

(Severity-tagged: BLOCKER / SHOULD-FIX / OBSERVATION. Rank by load-bearing-ness.
If fewer than 3 meaningful findings, say so — don't pad.)

## Q1. Row coverage of Phase C rubrics
## Q2. Prong-1 / Prong-2 axis seam
## Q3. Legal-vs-practical gap completeness
## Q4. Naming-merge consistency
## Q5. P1-product-framing residue

## Out of scope / not checked
```

### Constraints

- **Read-only.** No code or doc edits beyond writing your report.
- **Commit your report on whatever branch you are spawned in.** Do not push. Do not open PRs. Do not modify STATUS.md or any other doc.
- **Multi-committer awareness:** other fellows may be active on other branches; do not touch them.
- **No decoration.** Severity tags only. No emoji. No "overall the work appears solid" preamble.
- **If a question has no meaningful finding, say so** — don't manufacture material.

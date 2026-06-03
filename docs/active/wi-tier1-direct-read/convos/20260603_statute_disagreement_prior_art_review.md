# Statute disagreement — prior-art adjudication of the WI 18

**Date:** 2026-06-03
**Branch:** `wi-tier1-direct-read`
**Originating handoff:** the previous session's RESEARCH_LOG / convo entries closed items 1, 5, 6 + bonus 2; Item 3 (Citations API direction) was the open gate, blocked on Dan's review of the 18 inter-model disagreement cells in [`../results/20260601_wi_statute_vs_portal_spending.md`](../results/20260601_wi_statute_vs_portal_spending.md).
**Originating plan item:** [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 3.
**Predecessor convo:** [`20260601_phase3_followups_execution.md`](20260601_phase3_followups_execution.md).

## Summary

Picked up the wi-tier1-direct-read branch to walk through the 18 inter-model disagreement cells before deciding whether to fund the Citations API integration (post-Phase-3 followups, Item 3). Enumerated the 18 cells programmatically (re-deriving the 27.7% disagreement number from the 36 result JSONs); classified them into three structural patterns (A: 14 cells, B: 3 cells, C: 1 cell); then — at Dan's redirect — adjudicated each pattern against the source-rubric prior art (CPI 2015 IND_201, PRI 2010 §III.E2, Newmark 2017, others) rather than treating the row interpretations as design choices for us to make in 2026.

The audit landed two interlocking conclusions. First, on the question Item 3 was asking: **all 17 model-disagreement cells (Patterns A + B) trace to row-label ambiguity that the source rubrics adjudicate cleanly** — the rubric authors specifically asked about the lobbyist *as filer*, and GPT was reading source intent while Claude was over-projecting §13.68(4)'s "info flows through the lobbyist" onto a row asking who-the-filer-is. Item 3 (Citations API) is therefore closed: span-level statute citations don't help when both models already cite the right sections and the disagreement is about row meaning, not statute meaning. Second — surfaced during the prompt-rubric-update scoping check at session end — **the dispatch prompt currently sends only row IDs, no question text**. The verbatim source-rubric questions exist in the projection-mapping docs but never reach the model. The right fix is a `prompt_text` column on the compendium TSV populated from those source quotes.

This was an analysis-and-design session. No API spend. Three docs landed: a detailed results writeup adjudicating the 18 cells, three new v2.2 ledger entries, and back-link banners on the predecessor cross-validation doc and the Item-3 plan entry to keep the link graph self-consistent.

## Topics Explored

- **Enumeration of the 18 disagreement cells.** Wrote `wi_intermodel_disagreement.py` to walk all 36 result JSONs, find cells where each model is internally stable across 3 runs but the two models disagree. Replicated the predecessor doc's 65-jointly-stable / 18-disagree numbers exactly; refined the predecessor doc's "13 explicit + ~5 other" estimate to 14 + 4.
- **Three-pattern typology.**
  - Pattern A (14): every cell Claude TRUE × 3 / GPT FALSE × 3 in the `lobbyist_spending_report` chunk; both models cite overlapping §13.68 sections.
  - Pattern B (3): Claude scores by projecting principal-side / time-exemption rules onto lobbyist-labeled rows; GPT abstains because WI has no lobbyist-side analog.
  - Pattern C (1): `lobbying_violation_penalties_imposed_in_practice` — Claude scores from statute, GPT refuses because the row name embeds "in practice."
- **First-pass synthesis (later revised after Dan's pushback).** Initial framing was "all 18 are row-design ambiguities → drop Item 3, add v2.2 ledger entries for the row-design patterns." Dan pushed back: the compendium *unions prior art*; the right adjudicator is what the source-rubric authors actually meant, not what we think a good interpretation today would be.
- **Source-rubric provenance lookup.** Confirmed the compendium TSV carries `rubrics_reading`, `n_rubrics`, `first_introduced_by` columns. Wrote `wi_disagreement_provenance.py` to join the 18 cells against the TSV. Pattern A is PRI 2010-dominated (8 of 14 first-introduced by PRI; 13 of 14 list PRI in `rubrics_reading`) with sunlight_2015, newmark_2017, hiredguns_2007, cpi_2015 as the other introducers.
- **Verbatim source-quote audit.** Read `cpi_2015_c11_projection_mapping.md` lines 122–204, `pri_2010_projection_mapping.md` lines 600–710, `newmark_2017_projection_mapping.md` line 150 to recover the original question text for representative Pattern A + B rows.
- **Two compendium row-ID renames discovered.** PRI's `lobbyist_report_*` → v2.1 `lobbyist_spending_report_*`; Newmark's `expenditure_threshold_for_lobbyist_registration` → v2.1 `lobbyist_registration_threshold_expenditure_dollars`. Both source-intent-preserving but obscure the audit trail.
- **Structural prompt finding.** When scoping the "update the prompt-rubric text" task per Dan's a1 priority, discovered `render_legal_roster` (`scripts/tier_1_direct_read_legal_axis.py` lines 205–223) sends only `row_id` + `axis` + `expected_cell_class` to the model — no question text at all. The verbatim source-rubric questions are sitting unused in the projection-mapping docs.

## Provisional Findings

- **Pattern A: source intent unambiguously favors GPT.** CPI 2015 IND_201's source quote ("A YES score is earned if **lobbyists are required to file** itemized spending reports…") and the structural fact that CPI maintains `lobbyist_spending_report_required` AND `principal_spending_report_required` as separate rows (IND_201 vs IND_203) together establish that the row asks who-the-filer-is, not whether the info is disclosed anywhere. PRI 2010 §III.E2 ("Are lobbyists required to disclose?") corroborates with the same lobbyist-as-filer framing. All 14 Pattern A cells on WI should be FALSE (or unscoreable). Claude was answering a different question than the row was authored to ask.
- **Pattern B: source intent also unambiguously favors GPT.** Newmark's `expenditure_threshold_for_lobbyist_registration` is defined as "the expenditure dollar threshold above which the **lobbyist-definition** triggers." WI has no such threshold (the $500 is a *principal* threshold; the qualitative "main purpose" test in §13.62(11) is the lobbyist definition). Same shape for the de minimis and registration-deadline rows. All 3 Pattern B cells should be unscoreable. Claude was projecting principal-side rules onto lobbyist-side rows.
- **Pattern C: neither model wrong; row is mis-axed.** CPI 2015 IND_209's source quote is unambiguously about empirical imposition ("offenders are always sanctioned"); CPI explicitly assigns the row to the practical-availability axis. The v2.1 TSV registers it as `legal+practical`, which is the bug. Until the v2.2 split lands, this cell's legal-axis read should be excluded from σ_noise / inter-model alignment.
- **Item 3 (Citations API) is closed.** Span-level statute citations don't help when both models already cite the right sections; the disagreement is row-meaning, not statute-meaning.
- **Structural blocker on `prompt_text`.** The dispatch prompt has no row-question text at all. Adding a `prompt_text` column to the TSV (populated from the source-rubric quotes already verbatim in the projection-mapping docs) and updating `render_legal_roster` is the minimum intervention with the highest-confidence payoff for the WI 17 cells, and is v2.2-prerequisite for the MI session.
- **Portal cross-validation isn't an independent yardstick on Pattern A.** The 13/13 portal-data wins for GPT in the predecessor doc are restatements of the same finding — the portal exposes what the lobbyist actually files (zero spending columns), exactly what the source-intent reading predicts.

## Decisions Made

- **Close Item 3 (Citations API).** No integration in response to the WI 18. A future state could surface a different class of disagreement (genuinely non-overlapping cited spans) where Citations API earns its keep, but the WI batch is not that regime.
- **Don't unilaterally redesign the row labels.** Don't propose "add precondition cells" / "rename rows" / "sharpen prompts" as v2.2 design moves *without* first checking whether the source rubrics adjudicate. They do, in this case.
- **Stage the prompt_text fix narrow-first.** Populate `prompt_text` for the 17 confirmed-disagreement rows only, re-dispatch the 3 affected chunks on WI (~$1, ~10 min), validate Claude collapses onto GPT before committing to the full 181-row population pass. Re-dispatch happens with the fresh agent (post-finish-convo); needs Dan's explicit sign-off on the ~$1 spend at that point.
- **Three v2.2 ledger entries land this session.** Pattern C axis split; `prompt_text` column gap; source-quote provenance gap (row-ID renames). All three are observation-only entries per the ledger's design.
- **Bake the prompt_text fix into MI sequencing.** If it doesn't land before MI dispatch, the MI run repeats the WI Pattern A/B failure class on whatever rows are sensitive to filer-vs-subject ambiguity in MI's statute. MI can still proceed but interpret-with-caveats.

## Results

- [`../results/20260603_prior_art_adjudication_of_18_disagreements.md`](../results/20260603_prior_art_adjudication_of_18_disagreements.md) — full writeup with verbatim source quotes, per-row provenance, three-pattern typology, and the structural `render_legal_roster` finding.
- [`../results/disagreement_audit/wi_intermodel_disagreement.py`](../results/disagreement_audit/wi_intermodel_disagreement.py) — enumeration script (walks 36 JSONs, prints the 18-cell list with full per-model justifications).
- [`../results/disagreement_audit/wi_intermodel_disagreement_output.txt`](../results/disagreement_audit/wi_intermodel_disagreement_output.txt) — saved output of the enumeration script.
- [`../results/disagreement_audit/wi_disagreement_provenance.py`](../results/disagreement_audit/wi_disagreement_provenance.py) — provenance-lookup script (joins the 18 cells against the v2.1 TSV).
- [`../results/disagreement_audit/wi_disagreement_provenance_output.txt`](../results/disagreement_audit/wi_disagreement_provenance_output.txt) — saved output.
- [`../results/v2_2_schema_inputs.md`](../results/v2_2_schema_inputs.md) — three new entries (2, 3, 4).

Doc updates:

- [`../results/20260601_wi_statute_vs_portal_spending.md`](../results/20260601_wi_statute_vs_portal_spending.md) — added 2026-06-03 update banner at the top noting the resolution of the 18-cell question.
- [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) — added "Status: CLOSED 2026-06-03" banner to Item 3 with back-link to this session's writeup.

## Open Questions

- **Will Claude actually collapse onto GPT's reading with `prompt_text` added?** This is the falsifiable claim the narrow re-dispatch validates. If it does, the fix is portable to MI and the broader 181-row pass. If it doesn't, the row labels are ambiguous in a deeper way and v2.2 needs schema work.
- **Does the OH Tier-1 run have a similar inter-model disagreement pattern we haven't measured?** The OH Phase 3 writeup reported per-model σ_noise but not inter-model alignment. The optional OH re-dispatch flagged earlier (clean post-fix baseline for cross-state σ_noise) could double as an inter-model audit, but only after the prompt_text fix lands — otherwise we'd just measure WI's row-label ambiguity at OH.
- **Wide-pass scope for `prompt_text`.** Populating for 181 rows requires walking through ~6 projection-mapping docs and picking the right rubric per row. Mostly mechanical but substantive (likely most of a session). Should be its own branch or stay on wi-tier1?
- **Rename history capture.** v2.2 ledger Entry 4 proposes either `source_row_id_history` or `source_quote_verbatim` (or both) as TSV columns. Decision deferred to the v2.2 design pass.

## Sycophancy check

The session-start framing recommended "drop Item 3 / write v2.2 schema entries." Dan pushed back: the compendium unions prior art; the right adjudicator is the source-rubric author. I updated and the next reasoning used the update — went from "design unilaterally" to "look up source intent first" — and the resulting prior-art audit is what produced the load-bearing structural finding (the prompt sends no question text). The update wasn't performative; it changed the action and the action changed the finding. The recommendation against Item 3 *strengthened* under the new framing (now backed by source-rubric evidence, not just a design-process intuition) rather than weakened — that's the right shape of holding ground while absorbing the correction.

The "no prompt text" finding is uncomfortable for the WI Tier-1 work because it implies σ_noise + inter-model alignment numbers from the existing dispatches are partly artifacts of prompt under-specification. Surfaced it directly to Dan rather than couching it as a v2.2 future improvement.

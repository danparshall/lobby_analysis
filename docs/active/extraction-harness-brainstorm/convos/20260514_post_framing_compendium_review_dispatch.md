# Post-framing compendium review (dispatcher session)

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Originating handoff:** [`plans/_handoffs/20260514_post_framing_compendium_review_handoff.md`](../plans/_handoffs/20260514_post_framing_compendium_review_handoff.md)
**Output report (committed by the spawned reviewer):** [`docs/historical/compendium-source-extracts/results/20260514_post_framing_review.md`](../../../historical/compendium-source-extracts/results/20260514_post_framing_review.md) (commit `770f866`)

## Summary

Dispatcher session: the user asked this session to "spawn a compendium reviewer with prompt 'Execute …compendium_review_handoff.md'". The substantive review was done by the spawned subagent, which read the handoff, the 9 per-rubric projection mappings, the freeze-decisions log, naming conventions, and `docs/RESEARCH_ARC.md`, then committed a 98-line report at the handoff-specified path. This convo file records the dispatch + the reviewer's findings summary so future agents can find them without re-running the review.

The reviewer worked under the "report-only, read-only outside the report file, commit-but-don't-push, no STATUS.md edits" constraints from the handoff. Tree was clean on entry and clean on exit; the only change is the new report file under `docs/historical/`.

A **parallel review** spawned from the sibling handoff (`20260514_post_framing_harness_review_handoff.md`) had landed ~1 minute before this session's reviewer finished — commit `0ccbb86`, report at `docs/active/extraction-harness-brainstorm/results/20260514_post_framing_review.md`. Different review (harness internals, not Compendium 2.0), different path, no collision. Both reports are local-only on this branch until this session's finish-convo push.

## Topics Explored

- Termination ceremony for `claude-exit` (PID spawn/kill verified end-to-end; flagged that the parent-claude command line shows `--model opus[1m]` and `--system-prompt .` — looks like an ANSI bold escape leaking into displayed argv).
- Pre-flight reads (RESEARCH_LOG, handoff doc, git state) sized for a dispatcher session — STATUS.md was deferred to the subagent since the handoff already names it in the reviewer's required-read list.
- Dispatch of the compendium reviewer via the `general-purpose` agent type with a self-contained brief (worktree path, read-only constraints, `git -C` enforcement, output path, commit-don't-push, return format under 250 words).
- Spot-check of the resulting commit to verify the report landed at the handoff-specified path.

## Provisional Findings

The 4 findings the reviewer surfaced (severity tags per handoff: **BLOCKER / SHOULD-FIX / OBSERVATION**):

1. **BLOCKER for Phase C — uneven Ralph-loop ground-truth granularity across the 8 rubrics.** Only CPI 2015 (700 cells) and Sunlight 2015 (200 cells) give per-state per-atomic-item ground truth. PRI 2010 archive provenance needs verification before Phase C consumes; Newmark 2017 is sub-aggregate-only; Newmark 2005 / Opheim 1991 are total-only weak-inequality; HG 2007 needs re-retrieval from the CPI site or degrades to weak-inequality on its 83/100 disclosure partial; FOCAL 2024 has zero US-state ground truth (only Federal LDA 81/180 + 27 non-US countries). RESEARCH_ARC's `loss(prompt) = Σ |diff|` will silently weight whichever rubric has the most projectable summands unless `phase-c-projection-tdd` picks an explicit per-rubric normalization at kickoff. RESEARCH_ARC §"Three risks worth naming up front" risk #1 names the weighting issue abstractly; this is the concrete version that drops out of what each rubric can actually contribute.
2. **SHOULD-FIX — doc-vs-data drift on OS-1 firm count.** TSV: all 181 rows `status=firm`. `compendium/README.md` + `compendium/NAMING_CONVENTIONS.md`: "180 firm + 1 path_b_unvalidated". OS-1's unvalidated status is only encoded via `n_rubrics=0` and the literal string `(unvalidated; path-b)` in the `rubrics_reading` column. Cheap to fix on either side (regenerate TSV via `tools/freeze_canonicalize_rows.py` or update the two docs to describe how unvalidated status is actually encoded).
3. **SHOULD-FIX — legal-vs-practical gap is queryable for artifact existence, not for content-field surfacing.** 35 `lobbyist_spending_report_includes_*` + 13 `lobbyist_reg_form_includes_*` + 9 `lobbying_contact_log_includes_*` rows are legal-only with no practical sibling asking "does the portal expose this field?" The 5 dual-axis rows handle artifact-existence but not field-level content asymmetry. Under the corrected framing this is a real research-artifact gap. Two routes flagged: per-content-field practical cells (~50+ new rows, expensive) vs. a single `practical_axis_observed_fields: Set[row_id]` cell on a portal-observation envelope outside the 181-row TSV (cheaper, consistent with cell-typed-schema posture). Decision belongs to Prong-2 brief-writer at spin-up, not v2 re-opening.
4. **OBSERVATION — projection mapping docs use pre-rename row IDs throughout.** 247 old-name occurrences across the 9 mapping docs, by §10.1 design. When `phase-c-projection-tdd` writes projection functions reading from these docs, every row_id lookup must route through §10.1's resolver or `src/lobby_analysis/row_id_renamer.py:RENAMES`. Easy to skip and produce silent miscoding. Cheap mitigation: a one-off `tools/check_mapping_doc_row_ids.py` as a pre-merge check on projection PRs.

**Q2 (axis seam) is clean — no finding.** The 50 practical-only rows are all portal-observable, the 5 dual-axis rows have clean legal + practical readings, no mislabeling either direction.

**Q5 (P1-product residue):** lone candidate is **OS-1 (`separate_registrations_for_lobbyists_and_clients`)** — its D16 rationale explicitly invokes the "P1 as product" framing ("a real distinguishing statutory observable"). Flagged per handoff, not proposed for removal. D16 already names the watchpoint that would reverse its tabling.

## Decisions Made

- No decisions in this session. The reviewer's findings are advisory; the user reads the report and decides which to act on.
- Finding 1 will likely surface as a kickoff decision on `phase-c-projection-tdd` (per-rubric normalization) — but that's the user's call, not this session's.
- Finding 4's `tools/check_mapping_doc_row_ids.py` is a discrete pre-merge guard that could land on this branch or on `phase-c-projection-tdd`; deferred for user direction.

## Results

- [`../../../historical/compendium-source-extracts/results/20260514_post_framing_review.md`](../../../historical/compendium-source-extracts/results/20260514_post_framing_review.md) — committed by the spawned reviewer as `770f866`.
- (Adjacent: the sibling harness review at `../results/20260514_post_framing_review.md` from commit `0ccbb86` — different session, different scope.)

## Open Questions

- Which side resolves the OS-1 doc-vs-data drift (Finding 2): regenerate the TSV `status` column to encode `path_b_unvalidated` as a real value, or update README + NAMING_CONVENTIONS to describe how unvalidated status is actually encoded?
- Does `extraction-harness-brainstorm`'s upcoming practical-axis-brief-writer sibling brainstorm pick up Finding 3's design decision (per-content-field rows vs. portal-observation envelope), or does it surface elsewhere?
- Does the user want the Finding-4 row-ID consistency check landed now (on which branch?) or punted to `phase-c-projection-tdd` kickoff?
- Reviewer punted on PRI 2010 mapping deep-read (919 lines; spot-check only) and on whether `compendium-v2-promote`'s deprecation broke any caller. Worth a separate sweep if the user wants either.

## Process notes

- **Head-fake mid-verification:** when post-spawn git log showed two new commits, I jumped to "the reviewer clobbered the parallel review at the same path" without checking dirnames. They were different paths (`docs/historical/...` vs `docs/active/...`). Corrected within the same turn but worth noting: identical basenames across different parent dirs is exactly the failure shape that "check the full path before claiming collision" guards against. The lesson generalizes — git operations always look at full paths; my mental shortcut from basenames was the lossy step.
- The reviewer's commit message uses `review:` prefix (not the `convo:` prefix this repo's finish-convo uses). That's appropriate — the report is a results artifact, not a convo summary. This file uses the `convo:` prefix and is what closes the link graph for the dispatcher session.
- `--system-prompt .` and `--model opus[1m]` in the parent-claude command line (visible during the termination ceremony) look like display artifacts of the harness, not real flags. Not blocking; recorded so the next agent doesn't chase a phantom.

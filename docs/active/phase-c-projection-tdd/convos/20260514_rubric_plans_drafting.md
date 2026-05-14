# Rubric plans drafting — meta-session for the 6 remaining Phase C rubrics

**Date:** 2026-05-14
**Branch:** phase-c-projection-tdd
**Predecessor convos:** [`20260514_pri_2010_tdd.md`](20260514_pri_2010_tdd.md) (rubric #2, last implementation session) → this convo (meta-planning for #3–#8)
**Playbook under audit:** [`../plans/20260514_rubric_implementation_playbook.md`](../plans/20260514_rubric_implementation_playbook.md)
**Sub-session 0 results:** [`../results/20260514_playbook_gap_audit.md`](../results/20260514_playbook_gap_audit.md)

## Status

Sub-session 0 of 5 complete. Gap audit landed; structural decisions made (Stream B = 5 sub-sessions; FOCAL split into 3-4 sub-plans; HG launch gated on scorecard retrieval; strict reading of disclosure-only Phase B scope). Sub-sessions 1–4 (Stream 1 plans → Stream 2 plans → Stream 3 + HG plans → launch infrastructure + Sunlight canary) are pending; each will run in its own fresh-context Claude Code session. The user's motivation for batching is **API-key billing** (work-project budget) instead of personal Claude Code subscription tokens — so headless `claude -p` is the eventual execution path for plan-driven implementation, not the Agent tool from this session.

## Originating context

User opened the session: *"I believe we have 6 more rubrics to analyze; seems like a good candidate for doing in parallel, using the API. How feasible is that?"* The framing question (parallelism via API) prompted a chain of reframes:

1. **First reframe (mine):** Pure parallelism over 6 rubrics fights inter-rubric dependencies — Sunlight 2015 → Opheim 1991 (β AND-projection), Newmark 2017 → Newmark 2005 (shared helper extraction), HG 2007 (gated on `oh-statute-retrieval` Track A). Counter-proposal: 3 streams (Sunlight→Opheim; Newmark 2017→2005; FOCAL), with HG held.
2. **Second reframe (user):** The motivation isn't parallelism per se — it's *bill the API key, not the subscription*. Parallelism is a happy byproduct.
3. **Third reframe (user, by question):** "I'm even fine with doing one big planning session here with you, and then having you write 6 plans, and we launch those with the API key." This is the structure the session adopted, with the caveat that "one big planning session" was rebudgeted into 5 sub-sessions to keep each within a manageable context window.

## Pre-flight investigation

Standard pre-flight reads (STATUS.md, README.md, RESEARCH_LOG.md, the playbook itself). Then: read Sunlight 2015 spec doc in full as a sanity check on whether the playbook's per-rubric notes are faithful to reality.

**Sunlight finding (forecast for the broader audit):** The playbook's per-rubric notes are too compressed. For Sunlight 2015, the load-bearing fact a plan-drafter needs is **item 4 is excluded** (audit decision 2026-05-07; 5-tier ordinal conflates 3-4 sub-features with documented near-typos). The playbook does not mention this. Projecting all 5 items would produce a wrong projection function.

This finding motivated sub-session 0: do the same spot-check for the other 5 remaining rubrics before sinking effort into per-rubric plan drafting.

## Decisions (user-approved, top of session)

- **Convo name:** `20260514_rubric_plans_drafting`.
- **Structure:** B — 5 sub-sessions (gap audit → 3 stream-plan drafting sessions → launch infrastructure + canary). Each sub-session in its own fresh-context Claude Code session.
- **Sub-session 0 = playbook gap audit:** read intro + scope + aggregation + validation + Open Issues of each of the 5 remaining spec docs (Newmark 2017, Newmark 2005, Opheim 1991, HG 2007, FOCAL 2024). Output: results doc capturing per-rubric gaps. ~75 min budget.

## Sub-session 0 work performed

Read 5 spec docs (Newmark 2017 in full at 303 lines; Newmark 2005 in full at 383; Opheim 1991 in full at 424; HG 2007 first 170 + last 220 of 815; FOCAL 2024 first 170 + last 200 of 938). Cross-referenced against the playbook's per-rubric notes. Produced [`../results/20260514_playbook_gap_audit.md`](../results/20260514_playbook_gap_audit.md) — 5 cross-cutting meta-patterns the playbook missed + per-rubric gaps for all 6 + implementation implications + 7 convention proposals to bake into all plans + decisions surfaced for user review.

## Provisional findings — 5 cross-cutting meta-patterns the playbook missed

1. **"Disclosure-only Phase B" scope qualifier applies to every remaining rubric.** Newmark 2017 drops 5 of 19 (`prohib.*`); Newmark 2005 drops 5 of 18 (`prohib.*` × 4 + `penalty_stringency_2003`); Opheim 1991 drops 8 of 22 (`enforce.*` × 7 + 1 catch-all); HG 2007 drops 10 of 48 (Q39-Q47 enforcement + Q48 cooling-off); FOCAL 2024 drops 1 of 50 (`revolving_door.2`) after FOCAL-1 resolution. **None can reproduce their published index total.** The playbook does not mention this qualifier at all.

2. **Validation regime tiers split 3 ways, not the playbook's 3 regimes.** Strong (CPI/HG/FOCAL: per-state per-atomic-item ground truth). Medium (PRI/Newmark 2017: per-state sub-aggregate only). **Weak-inequality only (Newmark 2005, Opheim 1991): `our_partial ≤ paper_total` is the only check** — no sub-aggregate breakdown published.

3. **`unable_to_evaluate` convention is broader than playbook implied.** Applies to every OOS item, every operationally-undefined item, every portal-observation-required cell when only statute data is available. Critically: **not zeroed** (so weak-inequality holds).

4. **"Same-row-different-binary-cut" is a recurring per-item helper pattern.** PRI cadence row family (8 binary cells) read by Newmark 2005 (OR over all 8) and Opheim 1991 (OR over 2 cells — monthly only) at different binary cuts. The playbook's cheat sheet missed this pattern.

5. **Row-promotion meta-pattern (`X-rubric-confirmed`)** is the seed of Phase 4 cross-rubric audit. `lobbyist_spending_report_includes_total_compensation` is now 7-rubric-confirmed (the most-validated row in the compendium). Each plan should produce a "row-promotion delta" in its results doc.

## Provisional findings — biggest per-rubric surprises

- **FOCAL 2024 has NO per-state US ground truth.** Only federal LDA + 27 other countries. Cross-rubric is the *only* check for state FOCAL projections. Opposite regime from HG/CPI/Newmark.
- **Newmark 2005 is NOT a near-clone of Newmark 2017.** Different aggregation (4 sections vs 3), different validation regime (weak-inequality vs sub-aggregate), 6 panels vs 1. Shared helper is at row-family level, not module level.
- **HG 2007 has TWO retrieval blockers, not one.** Playbook said "depends on Track A `oh-statute-retrieval`." Actually: (a) HG per-state scorecard retrieval (CPI's 2007 archived pages — current availability uncertain; **NOT a Track A task**); (b) OH statute extraction (Track A) for the OH-specific HG sub-task only.
- **HG's 22 NEW rows include 13 practical-availability cells** that need portal observation, not statute extraction. Phase C can validate the 22 legal-axis items; the 13+ practical cells are Phase D targets.
- **FOCAL is substantially heavier than playbook suggests.** 11 Open Issues in spec doc; scorer-judgment cutoff for scope.2; 2024-numbering-with-2025-projection-logic asymmetry; set-typed cells and structured value types; weighted aggregation with weights 20×W1 + 19×W2 + 11×W3 = 182 max.

## Decisions made (top-of-session + post-audit)

- **Structure B confirmed:** 5 sub-sessions.
- **FOCAL plan shape:** **split into 3-4 sub-plans** per scope (legal-side core, contact_log battery, openness battery, aggregation + US LDA validation). Decision rationale: 49 indicators × 36 new rows × scorer-judgment items × 2024-vs-2025 asymmetry exceeds single-plan-context-window budget.
- **HG plan launch:** **gated on Phase 0 scorecard retrieval** (separate task). Plan drafted in Sub-3 with both paths specified (per-state if scorecard recoverable; weak-inequality if not). Launch waits on retrieval result.
- **Strict reading of disclosure-only Phase B scope:** keep all current OOS items OUT. FOCAL-1 precedent (user pulling `revolving_door.1` IN as a registration-form disclosure observable) does not retroactively apply to Newmark / Opheim / HG enforcement items. STOP clause in each plan: if a borderline item surfaces during drafting, ask user before pulling in.

## Convention proposals from the gap audit (to bake into all 6 plans)

1. **Scope qualifier** — every plan opens with a "Scope qualifier" section naming excluded items + reason + max-reproducible total.
2. **`unable_to_evaluate` convention** — OOS items, un-projectable items, and Phase D portal-observation cells produce `unable_to_evaluate` (not zeroed).
3. **Validation regime declaration** — every plan declares Strong / Medium / Weak validation regime up front.
4. **Row-promotion delta** — every plan's results doc has a "Row-promotion delta" section listing rows shifted N → N+1 confirmation.
5. **Spec-doc-vs-v2 cross-check** — load-bearing per the existing playbook; STOP clause if drift exceeds 10% of expected rows.
6. **Per-item helper return signature** — `int` in rubric-specific range OR `Literal["unable_to_evaluate"]`. Reverse-scoring in rollup, not per-item helper.
7. **Function-per-item vs declarative table** decision per rubric (see gap audit doc for per-rubric recommendation).

## Sub-session 0 results

- **Gap audit doc:** [`../results/20260514_playbook_gap_audit.md`](../results/20260514_playbook_gap_audit.md). 5 cross-cutting meta-patterns + per-rubric gaps for all 6 + implementation implications + 7 convention proposals + decisions for user.
- **Rubric data years doc:** [`../results/20260514_rubric_data_years.md`](../results/20260514_rubric_data_years.md). User mid-session interjection: "I'd like to know the 'data year' of each rubric. e.g. 'Sunlight 2015' wasn't actually checking the 2015 statutes, it was probably checking 2014 or something; this is important to make sure we grab the right vintage from Justia." Produced a table mapping publication-year vs data-year for all 8 rubrics, with confidence levels and paper-line citations where available. 12 distinct statute vintages span 1988-89 → 2025. HG 2007 has a *per-item* vintage split (Q35-Q37 = 2002; rest = 2006-2007). FOCAL state projections are vintage-flexible (no US-state ground truth); recommend aligning to L-N 2025's 2019-2023 collection window. 4 rubrics (Sunlight, CPI 2015, PRI 2010, Newmark 2017) have MEDIUM-or-lower confidence on data year — flagged for follow-up reads during Sub-1/Sub-2/Sub-3 plan drafting.

## Findings from data-year audit (added mid-session per user interjection)

Six headline points:

1. **Opheim 1991 and Newmark 2005 are HIGH-confidence**: data years explicitly stated in papers (Opheim = 1988-89 from CSG Blue Book; Newmark 2005 = 6 panels from BoS biennial editions, 1990-91 through 2003).
2. **L-N 2025 (FOCAL applied) is HIGH-confidence**: data collection between 2019 and 2023 per paper line 180-181 (Israel outlier 2025).
3. **Sunlight 2015 is MEDIUM-LOW**: blog post dated Aug 12 2015 per Newmark 2017 citation; the user's framing "wasn't actually checking the 2015 statutes" is correct — it was mid-2015 statutes at best, not end-of-year 2015.
4. **CPI 2015 C11 and PRI 2010 are MEDIUM**: implicit from publication date + context-events cited in papers. Already-shipped rubrics so this is informational, not blocking.
5. **HG 2007 has a per-item vintage split**: Q35-Q37 reference year is 2002 per `items_HiredGuns.md` §6; main items ~2006-2007. **Plan must specify per-item statute-year, not per-rubric.**
6. **`oh-statute-retrieval` (Track A) currently fetches 4 vintages** (2007/2010/2015/2025); validation across all 8 rubrics needs 12 distinct vintages. The OH bundle is a subset; expansion is a Track A scope question.

## Open questions / parked items

- **Newmark 2017 `TimeThreshold` structured-value support in v2 compendium loader.** The current `load_v2_compendium()` returns `list[dict[str, str]]` — raw strings. Newmark 2017's `time_threshold_for_lobbyist_registration` cell carries a structured `{magnitude, unit}` value that won't survive a string round-trip. Either the projection module parses the string at read-time (likely YAGNI option) OR `extraction-harness-brainstorm` (Track B) ships v2 Pydantic models with typed cell support before Newmark 2017 implements (currently no schedule). Flag for Stream 2 plan-drafting: plan should explicitly state how `TimeThreshold` is handled (parser in projection module, or wait for typed models).
- **FOCAL `LOW_DOLLAR_CUTOFF` / `LOW_TIME_CUTOFF` calibration.** FOCAL scope.2's projection requires a calibrated cutoff (paper acknowledges scorer-judgment). Candidate values: $1000 / 8 hours / 5% time. Decision deferred to Sub-3 (FOCAL plan-set drafting). May need a small empirical-fit script analogous to the CPI aggregation-rule fit.
- **Cross-rubric audit prototype timing.** Phase 4 cross-rubric agreement audit is deferred until ≥3 projection modules exist. With CPI + PRI shipped, even one more module unlocks the prototype. Could be a small parallel task while Stream 1 plans are drafted.

## Next steps

Sub-session 1 (next): **Stream 1 plans — Sunlight 2015 + Opheim 1991.** Run in a fresh Claude Code session. Inputs the next-session agent needs:

1. This convo file (decisions + conventions).
2. The gap audit results doc (per-rubric gaps for Sunlight + Opheim specifically).
3. The playbook (for shared conventions that ARE faithful).
4. The Sunlight 2015 spec doc + Opheim 1991 spec doc (already read here; agent will re-read for plan-drafting depth).
5. The CPI + PRI projection modules + tests (as reference implementations).

Sub-session 1 should:
- Open Sunlight 2015 plan first; lead with item-4 exclusion + validation regime + α/β conventions.
- After Sunlight plan lands, open Opheim plan; inherit β AND-projection convention; document weak-inequality validation regime + un-projectable catch-all.
- Both plans self-contained per write-a-plan skill, with STOP clauses for spec-doc-vs-v2 drift discovery.

After Sub-1, the chain continues: Sub-2 (Newmark 2017 → 2005), Sub-3 (FOCAL plan-set + HG plan with gate), Sub-4 (prompt template + headless launch script + Sunlight canary). HG launch and the other rubric launches don't happen until Sub-4's canary proves the headless workflow viable.

## Session token cost

This sub-session ran on Claude Code subscription. Sub-1 onward expected to run on user's API key via headless `claude -p` (or new Claude Code sessions with `ANTHROPIC_API_KEY` set), per the user's billing motivation.

## Captured Tasks

- [#9: Document compendium row-naming taxonomy; trace every name to source](https://github.com/danparshall/lobby_analysis/issues/9) — captured 2026-05-14 (surfaced during Sub-1 plan-drafting when the `*_report_*` → `*_spending_report_*` rename pattern revealed that broader naming conventions live across scattered docs without a canonical taxonomy reference)

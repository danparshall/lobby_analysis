# 2026-05-01 (pm) — Phases 0–3 implemented + iter-1 dispatched + iter-2 prep

**Date:** 2026-05-01
**Branch:** statute-extraction
**Predecessor convo:** [`20260501_harness_brainstorm_kickoff.md`](20260501_harness_brainstorm_kickoff.md)
**Plan executed:** [`plans/20260501_statute_extraction_harness.md`](../plans/20260501_statute_extraction_harness.md)

## Summary

End-to-end implementation session for the iter-1 statute-extraction harness. Phases 0–3 of the kickoff plan landed under TDD discipline (red → green → refactor): v1.3 schema bump, v2 scorer prompt + extraction_brief module, ExtractionRunMetadata + sha helpers in provenance, and orchestrator extract-prepare-run / extract-finalize-run subcommands. Phase 4 (iter-1 dispatch) ran in two halves — single-run sanity check first, then 2 more runs after user greenlight — producing the first three real `field_requirements.json` artifacts at `data/extractions/OH/2025/definitions/`.

The dispatch surfaced two genuine findings: (1) a prompt/validation tension on `not_addressed` rows where Rule 1 ("citation mandatory") and Rule 3 ("honest not_addressed") conflicted, resolved by tightening Rule 1's exception clause and loosening the finalize check; (2) a curation gap on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` where the row name is direction-ambiguous (target vs actor axis) and the description's single disambiguating preposition is the only thing that pins the axis. The harness happened to read it right (3-of-3 runs went target-axis), but that was lucky — the framework_references that anchor the cluster on target-axis (Hired Guns Q1: "executive branch lobbyists") were never visible to the agent.

The session produced iter-2 prep in response: tightened all 7 `definitions` row descriptions to lead with explicit axis labels (TARGET / ACTOR / THRESHOLD), wrote a per-chunk preamble at `src/scoring/chunk_frames/definitions.md` that names the three axes the rows decompose, and wired the preamble into `extraction_brief._render_suffix()`. Also drafted a handoff brief for a future agent to develop a v3 audit plan covering all 141 compendium rows for axis explicitness and curation fidelity.

## Topics Explored

- TDD-driven implementation of all four phases of the kickoff plan, all on the worktree branch.
- A worktree-pytest gotcha on `uv run pytest` resolving to main's editable install — surfaced, paper-trailed in CLAUDE.md, then user verified the gotcha appears resolved in current uv (left the section in as documentation in case it recurs).
- Three temp-0 claude-opus-4-7 subagent dispatches via the new harness, all against the OH 2025 `definitions` chunk (7 rows × 3-regime expansion = 15 emitted tuples per run).
- Cross-run agreement analysis: 14/15 = 93.3% status agreement; the single disagreement (`DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system`) probed in detail.
- Multiple cycles of pushback on which interpretation was "right" — the data in framework_references settled it (Hired Guns Q1 anchors the cluster on target-axis; r1's `not_required` is correct).
- The user's recall that PRI 2010 cared about *agency-as-actor* lobbying confirmed that the actor-axis question lives in `REG_GOVT_LOBBYING_GOVT` etc. in the `registration` chunk — the compendium's curation actually splits the axes correctly across domains.
- Per-chunk preamble design: name the conceptual axes the chunk decomposes (target / actor / threshold for `definitions`); have the agent map each row to an axis; provide prepositional disambiguation cues from the description text.

## Provisional Findings

- **Bundle inlining eliminated dispatch variance** as predicted in the kickoff plan. No tool-call variance was observed; the prior architecture's 4–43 tool-call dispatch noise is structurally gone.
- **Regime-aware-from-day-one (Q4) was correct.** All 3 runs identified OH's three regimes (legislative / executive / retirement_system) and emitted identical regime-specific tuple sets. No prompting was required.
- **The materiality-gate canary works across all three regimes.** §101.70(F)'s "main purposes" gate, §121.60(H)'s "regular and substantial basis" version, and §101.90(H)'s parallel — all captured as `required_conditional` with verbatim `condition_text`. The harness even detected a textual variation between legislative ("during at least a portion of the individual's time...") and executive/retirement ("on a regular and substantial basis") — fidelity the v1 PRI projection didn't have.
- **OH has no quantitative inclusion thresholds.** Unanimous `not_addressed` on `DEF_COMPENSATION_STANDARD` / `DEF_EXPENDITURE_STANDARD` / `DEF_TIME_STANDARD`, with detailed search-trail evidence_notes. Confirms prior project's qualitative-gate-only finding for OH.
- **The single inter-run disagreement is interpretive, not noise.** All 3 runs cite §101.90(H) and read the same statutory language; they disagree on whether the retirement-system definition's "retirement system decisions" axis subsumes "administrative-agency lobbying" (target-axis) categorically. r1's `not_required` is the literal reading; r2 punted to `not_addressed`; r3 over-functionalized to `required`. The compendium description's "contact with administrative agencies" pins the right answer — but only if read carefully.
- **Row names alone don't carry axis.** `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` reads as actor-axis to a careful human; only the description disambiguates, and it does so with a single preposition. The framework_references (Hired Guns Q1's "executive branch lobbyists" phrasing) are the strongest disambiguating evidence and weren't visible to the agent.
- **The compendium's domain split (definitions vs registration) actually does the right thing.** Target-axis rows live in `definitions`; actor-axis rows about institutional actors live in `registration` (PRI A5–A11). The curation honored the rubrics' implicit axis split; the row *names* just don't preserve it.

## Decisions Made

- **Validation rule (codified):** `legal_citation` is required for `required` / `not_required` / `required_conditional`; null is permitted for `not_addressed` provided `evidence_notes` is non-empty. Commit `0ac7800`.
- **Q6 settles to ≥3 temp-0 runs at iter-1 evidence.** Bumping to 5 wouldn't resolve interpretive disagreement; the 3-model consensus oracle (or per-row scope tightening) is the right escalation path for interpretive cases, not more same-model runs.
- **Iter-2 fix is structural, not row-specific.** Adding a per-chunk preamble that names the chunks axes (target/actor/threshold for `definitions`) is more general than tightening individual row names one at a time. Wired into the brief renderer.
- **Audit of all 141 rows is a separate effort, deferred via handoff brief.** The receiving agent will write a v3 audit plan; this session produced the brief, not the plan.
- **No row-name renames this session.** Renames are stable-contract changes that need migration of references in tests/fixtures/run dirs; deferred to the v3 audit's planned sequencing.

Plan docs referenced this session:
- [`plans/20260501_statute_extraction_harness.md`](../plans/20260501_statute_extraction_harness.md) — the kickoff plan (Phases 0–4) executed end-to-end.
- [`plans/_handoffs/20260501_compendium_item_audit_handoff.md`](../plans/_handoffs/20260501_compendium_item_audit_handoff.md) — handoff brief produced this session for a future agent.

## Results

- [`results/iter-1_analysis.md`](../results/iter-1_analysis.md) — full iter-1 analysis (per-row results × 3 runs, weak-row write-up, decisions validated/open, next-iteration recommendation).
- Live run dirs (under `data/extractions/OH/2025/definitions/`, gitignored): `cc24d8920949`, `dea6828ac0bc`, `4ad20debaf31`. Each contains `brief_suffix.md`, `full_brief.md`, `meta.json`, `raw_output.json`, `field_requirements.json`.

## Open Questions

- **Will iter-2's preamble + tightened descriptions collapse the `× retirement_system` disagreement to unanimous `not_required`?** That's the iter-2 hypothesis. If yes, the per-chunk preamble approach is validated and we apply it to the other chunks. If no, the disagreement is deeper than name/description ambiguity (possibly genuine cross-regime definitional ambiguity in OH statute itself, in which case iter-2 escalates to the 3-model consensus oracle).
- **Should `CompendiumItem` gain an explicit `axis` field for v1.4?** The chunk-frame preamble can carry the axis vocabulary in prose; an explicit field would make it data, queryable downstream. The audit handoff defers this decision to the v3 audit plan.
- **Are there other rows with the same direction-ambiguity issue?** Iter-1 only ran on the 7-row `definitions` chunk. The audit handoff covers the 134 rows in the other domains.

## Captured Tasks

None new this session. (Issue #6 — Justia statute pull + portal snapshots restoration after laptop data-loss — was captured at session start and remains open.)

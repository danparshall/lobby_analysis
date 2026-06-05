# 20260520 — Tier-0 direct-read plan: Steps 5–7 executed (the smoke run + writeup)

**Date:** 2026-05-20
**Branch:** extraction-harness-brainstorm
**Machine:** Dans-MacBook-Air (API keys supplied this session via a local `.env.corporate` file — see Session mechanics below)
**Predecessor convo:** [`20260519_session_end_steps_1_to_4.md`](20260519_session_end_steps_1_to_4.md)
**Plan executed:** [`../plans/20260518_tier_0_direct_read_smoke_test.md`](../plans/20260518_tier_0_direct_read_smoke_test.md) — Steps 5–7 of 7 (Steps 1–4 shipped 2026-05-19)

## Summary

Picked up the Tier-0 direct-read plan with Steps 1–4 (the pure-code wiring) already shipped and pushed. This session ran the remaining three steps: the live dual-model smoke dispatch (Step 5), the hand-eyeball + writeup (Step 6), and this finish-convo (Step 7). No code was changed — Steps 5–7 are execution and analysis only. Per the plan, success criterion 5 failed (a value type-check error on Claude's side); per the plan that is **reported, not patched** — the failure mode is the deliverable.

The smoke ran end-to-end on the first attempt (after a key-loading false start, see mechanics). Both models dispatched against the OH 2025 `enforcement_and_audits` chunk (2 rows × 2 axes = 4 cells), parsed cleanly, and wrote all four raw/parsed JSON files. Total dispatch cost ≈ $0.10, far under the $5 ceiling. The empirical signal is clear and a little more interesting than a binary "direct-read works / doesn't": direct-read is viable for the **legal axis** and structurally cannot serve the **practical axis** from a statute-only bundle — and that practical-axis gap is *not* something the Citations+retrieval escape hatch would fix, because it is a data-*source* gap, not a retrieval gap.

The two models also diverged sharply in behavior on identical input, which is itself a finding for the Phase-2 verifier design.

## Topics Explored

- Step 5: live dispatch of Claude Opus 4.7 + GPT-5.2 against OH 2025 `enforcement_and_audits`.
- Step 6: hand-verification of every cited statute section against the bundle text; cell-by-cell cross-model comparison.
- Whether Tier-0's result selects the plan's "direct-read viable" branch or the "escape hatch" branch.

## Provisional Findings

- **The wiring works.** Both models dispatched, parsed, and saved without uncaught exceptions. Success criteria 1–4 and 7 met.
- **Criterion 5 failed (Claude).** Claude emitted `record_cell` for both `practical`-axis `GradedIntCell`s with `value="2"` / `value="1"` — JSON **strings**, not ints. Pydantic rejected both. Root cause: the shared `RECORD_CELL_INPUT_SCHEMA` `value` field is a loose `oneOf` that includes `{"type":"string"}`. This is an encoding mismatch, not a reasoning error (the values are stringified integers). The plan's "What could change" item 3 predicted exactly this. **Left unpatched per the plan** — Tier-1's job (tighten schema per cell-class, or coerce `str→int` in `_instantiate_cell`).
- **The practical axis is unanswerable from a statute-only bundle.** Both practical-axis cells ask about real-world behavior (penalties *imposed*, audits *conducted*). GPT correctly emitted `record_unscoreable_cell` for both. Claude scored them anyway, while its own justifications conceded the bundle lacks enforcement data. GPT's calibration was better here.
- **GPT's 0 type-errors is an artifact, not a virtue.** It abstained on exactly the two cells that trigger the string/int bug; it never reached the buggy path. If it had scored them it would likely have hit the same error.
- **Legal axis is viable.** `penalties_imposed_in_practice, legal`: both models scored `True`, both correct, both well-cited (§101.99 verified verbatim — 4th/1st-degree misdemeanors). `audit_required_in_law, legal`: Claude scored `review_only` (substantively correct — §101.72(G) review + §101.79 AG investigation, no audit mandate; all three sections verified verbatim); GPT abstained, which here was **over-conservative** — for a "required in law?" question over a complete 30-section chapter, the requirement being absent *is* a determinate answer.
- **Sharp model divergence on identical input.** Claude scores aggressively (4/4 attempted); GPT abstains readily (3/4 unscoreable). They agree on statute *facts* (cite the same sections) but disagree on *scoreability*.

## Decisions Made

- Tier-0's verdict selects neither plan branch cleanly. It selects a **third path**: (1) fix the value-typing bug in Tier-1; (2) the user decides whether the `practical` axis is in scope for a statute-fed pipeline or needs a separate evidence corpus; (3) proceed to Tier-1 direct-read on the **legal axis** across the 6 CPI-2015 de-jure chunks; (4) the Phase-2 verifier needs an explicit abstention-calibration policy because the two models disagree on when a cell is scoreable. Full reasoning in the writeup.
- The escape hatch (Citations + retrieval + bundle expansion) is **not indicated** by this run — the failure that occurred would not be cured by retrieval over the same statute corpus.
- Script left unmodified; criterion-5 failure documented, not patched (plan directive).

## Results

- [`../results/20260518_tier_0_direct_read_writeup.md`](../results/20260518_tier_0_direct_read_writeup.md) — full writeup + architecture verdict (Step 6 deliverable).
- Raw + parsed JSON (4 files): `../results/20260518_tier_0_{raw,parsed}_{anthropic,openai}_enforcement_and_audits.json`.

## Open Questions

- **Practical-axis scope** — exclude practical cells from a statute-fed pipeline, or source a separate practical-evidence corpus (enforcement records / FOIA / news)? Research decision for the user.
- **Abstention calibration** — Claude over-scores, GPT over-abstains. The verifier agent (Phase 2) needs an explicit policy. What is "correct" abstention?
- `review_only` was not cross-checked against `EnumCell`'s allowed value set — a Tier-1 verification.
- Carried from the plan: Q2 (adversarial-framing wording) and Q4 (cost ceiling — $0.10 actual vs $5 ceiling; tighten?).
- Pricing caveat from Steps 1–4 still stands: Claude cost estimate uses placeholder opus-4-6 rates.

## Next Steps

1. Execute [`../plans/20260520_tier_1_direct_read_legal_axis.md`](../plans/20260520_tier_1_direct_read_legal_axis.md) — Tier-1 legal-axis run (typing fix + legal roster filter + 6 CPI de-jure chunks + σ_noise).
2. Phase-2 verifier plan should treat abstention calibration as a first-class design problem.
3. Practical/de facto axis is Prong 2's territory — not this branch.

## Session mechanics / caveats for the next agent

- **API keys came from `/Users/dan/code/lobby_analysis/.env.corporate`** (copied to the main worktree this session). That file is **not a clean env file** — lines 1–3 are `KEY=value`, but the rest is freeform scratch notes. `source`-ing the whole file runs the prose as shell commands. Load only the key lines: `. <(grep -E '^[A-Za-z_]+=' .env.corporate)`. The file is gitignored (`.env*`).
- The keys are **live** (the dispatch authenticated and billed). They appeared in this session's transcript — worth rotating.
- Dans-MacBook-Air now has working keys, contradicting the Steps 1–4 convo's "laptop is keyless" assumption.

## Addendum (same session) — de jure/de facto clarification, writeup amended, Tier-1 plan written

After the writeup landed, the user corrected a misframing in it. The `practical` axis **is** the **de facto** axis, and de facto measurement is **Prong 2's** job — scored against the *same* compendium items (the SMR). This prong (Prong 1) is **de jure only**. The writeup had framed the practical-axis cells coming back unscoreable as an open "which data source?" decision; that was never an open decision. GPT abstaining on the practical cells was *correct*; Claude scoring them was a *genuine error* (a de facto answer from de jure evidence). The fix is a one-line roster filter (`axis == "legal"`) — which the brief-writer brainstorm had already locked.

- **Writeup amended** — [`../results/20260518_tier_0_direct_read_writeup.md`](../results/20260518_tier_0_direct_read_writeup.md): two sections corrected and marked `[Amended 2026-05-20.]`, plus a header note.
- **SMR-status assessment.** A full *de jure* SMR for one state-vintage = **131 legal-axis cells across 15 chunks** (registry is 186 cells: 131 legal + 55 practical). Tier-0 scored 2 of those 131. Mechanically populating all 131 for OH 2025 is ~days away; a *trusted* SMR is not — the typing fix, Tier-1, the verifier agent (unbuilt), the Ralph loop/orchestrator (unowned per STATUS), and projection validation (`phase-c-projection-tdd`, not started) all sit in between. "Populating" and "trusting" the SMR are very different milestones.
- **Tier-1 plan written** — [`../plans/20260520_tier_1_direct_read_legal_axis.md`](../plans/20260520_tier_1_direct_read_legal_axis.md): legal-axis-only run over the 6 CPI-2015 C11 de-jure chunks (items IND_196/197/199/201/203/207), with the value-typing fix, per-dispatch checkpointing, and σ_noise from N=3 re-runs. CPI published-score comparison deferred to when `phase-c-projection-tdd`'s projection functions land.

# Phase 3 baseline dispatch + H1 confirmation via TX statute walkthrough

**Date:** 2026-04-20 / 2026-04-21 (single conversation spanning a day boundary)
**Branch:** pri-calibration
**Plan driving this session:** [`plans/20260418_phase2_statute_retrieval_and_baseline.md`](../plans/20260418_phase2_statute_retrieval_and_baseline.md) — Phase 3 execution block.

## Summary

This session executed the Phase 3 live-dispatch plan end-to-end: preparing 15 run directories × 2 rubrics (30 briefs), dispatching 30 Claude Code general-purpose subagents in batches of 4 to score the 5-state calibration subset (CA/TX/WY/NY/WI) against their respective-vintage statute bundles, finalizing runs, and producing inter-run consistency + agreement-vs-PRI reports. Baseline agreement came out at **0% exact-match on disclosure-law total scores** across all 5 states — triggering the plan's "< 40% agreement → something bigger is wrong, debug before iterating" stopping condition.

A post-dispatch investigation session with Dan then walked through TX Gov Code ch. 305 statute text item-by-item against A_registration, and independently retrieved §311.005(2) (Code Construction Act) — establishing decisively that TX's "person" statutorily includes governmental entities. This resolves the A-score gap via **H1 (bundle scope too narrow)** rather than **H2 (scorer interpretation wrong)**. The scorer gave TX A=1 because ch. 305 alone doesn't tell it "person includes agencies" — with §311.005 in scope the reading supports 8–10 A-items (PRI's 7 is middle-of-range, defensible).

The conversation then shifted to architecture: Dan proposed a per-state meta-dictionary to capture cross-chapter interpretive context. Agreed hybrid shape: `LOBBYING_STATUTE_URLS` extends to include `support_chapters` (additional statute text the scorer should read) and `interpretive_notes` (static protocol facts with citations). Lean toward retrieval-guide over metadata where statute text would do the job — encode legal facts as data only when statute reading can't substitute. Agreed strategy: finalize 5-state pilot with bundle expansion before scaling to 3-fellow × 17-state rollout, to lock the schema.

## Topics Explored

- Dispatched 30 scoring subagents in batches of 4 (5 states × 3 run-ids × 2 rubrics); all returned `DONE <n>` with correct item counts (59 for accessibility, 61 for disclosure law).
- Mid-session discovery of a load-bearing bug in `build_statute_subagent_brief`: brief instructed subagents to prepend `repo_root` to each artifact's `local_path`, but `StatuteArtifact.local_path` was stored as `sections/<name>.txt` — relative to the bundle directory, not repo root. Fixed by normalizing `StatuteArtifact.local_path` to repo-root-relative in `load_statute_bundle(bundle_dir, repo_root)`; added a dispatch-contract test that would have caught the original bug.
- Ran `calibrate-analyze-consistency` per state; disclosure-law inter-run disagreement: CA 24.6%, TX 27.9%, NY 19.7%, WI 9.8%, WY 11.5%. Compare to 2026-portal pilot CA disclosure ≈37% — statute-based scoring shows improvement but stays above the 10% flag threshold on 4/5 states.
- Ran `calibrate` against PRI 2010 references; total exact-match agreement = 0% on all 10 (state, rubric) pairs. Accessibility was almost all `null / X ✗` as expected — portal-feature rubric doesn't fit statute text.
- Diagnosed A_registration as the dominant error driver (4/5 states had ours < PRI; WY and TX each off by 6 points).
- Walked TX Gov Code §305.003 with Dan: identified the two independent registration triggers (a)(1) expenditure path + (a)(2) compensation path; confirmed (b-1) exemption applies only to (a)(2); §305.004(3)-(5) adds narrow procurement/internal-solicitation/event-attendance carve-outs.
- Retrieved TX Gov Code §311.005(2) externally (text pasted by Dan): "Person" includes "government or governmental subdivision or agency, business trust, estate, trust, partnership, association, and any other legal entity." This is the decisive definition for H1.
- Discussed meta-dictionary shape: retrieval-guide (B) vs. static-facts (A). Agreed hybrid, lean B.

## Provisional Findings

- **H1 confirmed for TX.** `LOBBYING_STATUTE_URLS` was scoped to the *lobbying* chapter per state; the scorer needs cross-chapter definitions (code construction acts, general definitions) to resolve A_registration item-type questions. Expected to generalize to CA/NY/WI/WY — each has its own code-construction statute.
- **H2 (rubric-interpretation drift) deprioritized** but not falsified. If residual agreement gap remains after H1 fix, H2 may still be relevant — particularly for items A5-A11 if the "person = entity" reading doesn't capture whatever PRI actually did.
- **Accessibility rubric against statute text is structurally wrong.** TX/WY 96-98% "unable-disagree" confirms the scorer can't evaluate portal-feature items from statute text. Accessibility should be scoped out of calibration branch.
- **Disclosure-law inter-run disagreement improved vs. portal baseline** — CA came down from ~37% (portal) to 24.6% (statute). Statute text is clearer than portal guidance. This validates the calibration pivot's premise partially but with residual 10-28% ambiguity that bundle expansion may narrow further.
- **WI bundle (17 sections, 78 KB of text)** shows the lowest inter-run disagreement (9.84% on disclosure_law, below the 10% flag). Suggests granular per-section retrieval helps consistency.
- The single biggest confidence-weighted strategic call: pilot-first before 3-fellow scale-out. Premature scaling would fork the meta-dictionary schema into 3 incompatible shapes.

## Decisions Made

- **Phase 4 prompt iteration is NOT the immediate next step.** Debug the baseline (bundle expansion) first.
- **Next session:** hand-curate `support_chapters` for all 5 pilot states, re-retrieve statutes, re-run prepare → dispatch → finalize → calibrate. Compare to today's numbers.
- **Success criterion for pilot:** set concretely after re-score numbers are in; target somewhere in the 50-70% exact-match disclosure-law range (placeholder — to be locked before Phase 4 starts).
- **Fellow scale-out blocked on pilot.** Only after pilot's schema is validated do the other 2 fellows start on their 15-17 states each.
- **Accessibility rubric descoped from calibration branch.** Will be addressed separately — either on `scoring` branch or a future portal-based calibration line.
- **Bundle-path normalization bug fixed and committed** (`6df631a`).

## Results

- [`results/20260420_calibration_baseline.md`](../results/20260420_calibration_baseline.md) — consolidated baseline writeup with hypothesis table, per-state error decomposition, next-steps decisions (updated 2026-04-21 with TX H1 confirmation).
- [`results/20260420_consistency_CA.md`](../results/20260420_consistency_CA.md), `_TX.md`, `_NY.md`, `_WI.md`, `_WY.md` — per-state inter-run consistency reports across 3 temp-0 runs.
- [`results/20260420_baseline_disclosure_law_4states.md`](../results/20260420_baseline_disclosure_law_4states.md), `_TX.md` — multi-run agreement-vs-PRI for disclosure law.
- [`results/20260420_baseline_accessibility_4states.md`](../results/20260420_baseline_accessibility_4states.md), `_TX.md` — multi-run agreement-vs-PRI for accessibility (mostly `null`, as expected).
- `data/scores/<STATE>/statute/<vintage>/<r1,r2,r3>/` — 15 statute-path scored CSVs + StatuteRunMetadata (gitignored; referenced via committed manifests).

## Open Questions

- **What's the right `support_chapters` list per state?** TX ch. 311 is confirmed necessary; other states' code-construction / definitions statutes are likely analogs (CA Gov Code §18, NY Gen Constr Law §37, WI Stats ch. 990, WY Stats title 8) but need verification by reading each state's lobbying chapter for cross-references and hitting the definitions chapter directly.
- **Does `build_statute_subagent_brief` need a prompt-level update to flag "read the lobbying chapter AND the support chapters; the support chapters give cross-referenced definitions"?** Probably yes — currently the brief labels artifacts only as "statute text (not portal content)" without differentiating primary/secondary source roles.
- **What's PRI's coding protocol for items that require cross-chapter reading?** Re-read PRI 2010 §III.A footnotes — did PRI systematically pull from code-construction acts, or only the lobbying chapter? If PRI was consistent with what we're about to do, agreement should be strong. If PRI was inconsistent, agreement will cap below what bundle-expansion alone can achieve.
- **What ROI does the bundle expansion give on E_info_disclosed items?** We only validated H1 via A_registration. E_info_disclosed items (E1b-E2i) asking about disclosure-report content might also turn on definitions from other chapters (e.g., "principal" definition, itemization rules) — but could just as likely be fine. TBD.
- **How does meta-dictionary schema generalize to the full 50 states?** The 3-fellow rollout needs a discovery checklist. "For each state: (1) identify lobbying chapter; (2) identify code-construction act; (3) identify separate definitions chapter; (4) identify ethics-code cross-references" is the skeleton — but state-specific quirks (e.g., California's Political Reform Act having its own definitions baked in) need to be handled.
- **Non-responder states may behave systematically differently.** 16 of 50 states are non-responders; their PRI ground truth is weaker. Will responder/non-responder split show a consistent pattern or random variance?

## Addendum (end-of-session, 2026-04-21)

Late in the session, Dan and I widened the lens from "finish pri-calibration pilot" to "what does the unified rubric look like across PRI + FOCAL?" Two distinct threads landed:

**1. Multi-branch housekeeping.** Merged `scoring` and `lobbying-data-model` into main, reconciling the pyproject.toml conflict by combining both packages under the umbrella name `lobby-analysis` with `packages = ["src/lobby_analysis", "src/scoring"]`. Preserved pri-calibration's 3 extra deps (beautifulsoup4, playwright, requests) in the back-merge. 156 tests green after the merge train. Also broadened `.gitignore` to `.env*` per Dan's request. Pushed main and pri-calibration. Branches listed as merged on origin: focal-extraction, pri-2026-rescore, research-prior-art (all archived), and now scoring + lobbying-data-model. Unmerged: pri-calibration (active), lobbying-data-model was locally unchecked-out.

**2. Data model v1.0 accepted + archived.** The `lobbying-data-model` branch had been sitting in "Draft — circulate for feedback" status for 4 days with no change requests. Accepted as v1.0; spec doc updated; docs moved `docs/active/lobbying-data-model/` → `docs/historical/`; STATUS.md updated with Archived row. Pydantic models remain in `src/lobby_analysis/models/` as the extraction-pipeline contract. The model is Popolo-compatible at the reference-entity layer (Person/Organization/Identifier/ContactDetail) — the user initially called this "Pomodoro" (likely thinking of Popolo, which is the actual open-data standard used by Open Civic Data). The schema's `StateMasterRecord` with requirement sub-models is the reconciliation surface between "what the state's law requires in principle" (populated by legal review) and "what filers actually report" (populated by portal extraction).

**3. Rubric unification scoped as the next major work.** Dan asked "what's up with FOCAL vs PRI — we use both to define the standard, but maybe we should do the effort to first think about what does/n't overlap." The earlier `scoring-rubric-landscape.md` proposed composing "PRI 22 accessibility + FOCAL 50 content" but only at the conceptual level — no item-level mapping. Before fellows scale to 50 states, the unified rubric needs to be nailed down so everyone scores the same thing. I read the three source CSVs (PRI disclosure-law 61 items, PRI accessibility 22 items, FOCAL 50 indicators) and sketched the landmarks — PRI A1–A11 vs FOCAL 1.x (related); FOCAL 5 (revolving door) + 6 (relationships) have no PRI analog; FOCAL 3 (openness) is the portal-accessibility axis which should stay out of the unified legal-review rubric; PRI B/C/D structural exemption/definition items are PRI-only.

**Decision:** capture this as a handoff plan for another agent with fresh context (context in this session is full enough that starting the actual rubric unification here would risk compression losing nuance).

**Handoff plan written:** [`plans/20260421_rubric_unification_and_handoff.md`](../plans/20260421_rubric_unification_and_handoff.md) — 4 phases (item-level overlap mapping → unified rubric synthesis → rubric-to-schema mapping → fellow playbook), pre-flight reads, edge cases, 5 open questions for Dan, explicit coordination notes with pri-calibration pilot to avoid rubric-identity collision mid-calibration.

**Sequencing landed at end of session:**

1. **Next pri-calibration session:** finish the pilot — expand bundles per the H1 fix, re-retrieve, re-score against *existing PRI 2010 rubric* (NOT the unified rubric — changing rubric mid-calibration breaks apples-to-apples). Measure agreement uplift.
2. **Parallel (another agent, fresh context):** execute `plans/20260421_rubric_unification_and_handoff.md` — produce the unified rubric as a committed CSV + methodology + schema mapping. Downstream consumer is the fellow rollout, not the pri-calibration pilot.
3. **Fellow scale:** only after both (1) and (2) land. 3 fellows × ~17 states each, armed with (a) expanded-bundle meta-dictionary shape, (b) unified rubric, (c) data model v1.0.

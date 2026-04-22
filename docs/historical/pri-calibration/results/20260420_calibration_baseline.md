<!-- Generated during: convos/20260420_phase3_baseline_dispatch.md -->

# Phase 3 Calibration Baseline — 5-state statute-text scoring run

**Date:** 2026-04-20
**Subset:** CA/2010, NY/2010, WI/2010, WY/2010, TX/2009 (all PRI 2010 responders)
**Runs:** 3 temp-0 runs per (state, rubric) via Claude Code general-purpose subagents. Scorer prompt is unchanged from the locked `src/scoring/scorer_prompt.md`. 30 subagent dispatches total.
**Inputs:** Statute text bundles from Justia (vintage-matched, sha256-verified). No portal snapshots — this is the statute-based baseline that the calibration pivot was designed to produce.
**Originating plan:** [`plans/20260418_phase2_statute_retrieval_and_baseline.md`](../plans/20260418_phase2_statute_retrieval_and_baseline.md)

## TL;DR — the plan's `< 40% agreement` stopping condition is triggered

Disclosure-law total agreement against PRI 2010 is **0% exact-match** across all 5 states, meaning no state's rolled-up total score equals PRI's 2010 value. Per-state gaps vary from 2 points (close) to 14 points (TX). Accessibility total agreement is **0% across the board and largely `null`** — expected: the accessibility rubric is about portal features and statute text doesn't describe portals.

The plan's Phase 3 write-up criteria:
- ≥ 90% → surface as surprisingly good. **Not triggered.**
- < 40% → something bigger is wrong; debug before iterating. **Triggered.**
- Inter-run disagreement ≥ the 2026-portal pilot's rate → calibration pivot premise is weak. **Partially triggered** (see below).

**Recommendation: pause before Phase 4 prompt iteration.** Prompt tweaks on top of this baseline will overfit to symptoms rather than root causes. The underlying issues are bundle-scope, rubric-match, and item-level interpretation — not prompt phrasing.

## Headline numbers

### Inter-run consistency (% of items where 3 runs disagree)

| State | Accessibility | Disclosure Law |
|-------|---------------|----------------|
| CA    | 0.00%         | 24.59% FLAGGED |
| NY    | 1.69%         | 19.67% FLAGGED |
| WI    | 1.69%         | 9.84% ok       |
| WY    | 98.31% FLAGGED| 11.48% FLAGGED |
| TX    | 96.61% FLAGGED| 27.87% FLAGGED |

Portal pilot on CA disclosure law (`scoring` branch, 2026-04-17): ~37%.

Reading:
- **Accessibility against statute text is broken by design.** TX and WY show 57/59 and 58/59 items in "unable-disagree" — the scorer can't decide whether a statute that doesn't mention portals is evidence of "no such feature exists" (score 0) or "the source can't tell me" (unable). CA/NY/WI accessibility looks clean only because those states' statutes happen to contain text mentioning an electronic database or online filing, giving the scorer a stable anchor on ~2-3 items and letting the rest fall to consistent 0/unable. Do not interpret the low CA/NY/WI accessibility rates as a success signal.
- **Disclosure-law inter-run disagreement improved vs portal baseline but remains above 10% on 4/5 states.** CA came down from ~37% (portal) to 24.59% (statute) — statute text is clearer than portal guidance, but the remaining 24.59% says the scorer is still hitting genuinely ambiguous items even with the actual law in front of it.

### Agreement vs PRI 2010 — disclosure-law sub-aggregate totals

Per-state total, all 3 runs combined (the `calibrate` reporter shows per-run detail; here showing the first run):

| State | A_registration (ours / PRI) | B_gov_exemptions | C_public_entity_def | D_materiality | E_info_disclosed | Total (ours / PRI) | Δ |
|-------|-----------------------------|-------------------|---------------------|---------------|------------------|--------------------|---|
| CA    | 3 / 6                        | 1 / 2             | 0 / 0 ✓             | 1 / 1 ✓       | 15 / 14          | 20 / 23            | –3 |
| NY    | 5 / 3                        | 2 / 0             | 1 / 0               | 1 / 1 ✓       | 15 / 18          | 24 / 22            | +2 |
| WI    | 4 / 6                        | 2 / 1             | 0 / 0 ✓             | 1 / 1 ✓       | 13 / 10          | 20 / 18            | +2 |
| WY    | 1 / 7                        | 2 / 2 ✓           | 0 / 0 ✓             | 1 / 0         | 7 / 5            | 11 / 14            | –3 |
| TX    | 1 / 7                        | 2 / 3             | 0 / 0 ✓             | 1 / 1 ✓       | 11 / 18          | 15 / 29            | –14 |

Observations:
- **C and D sub-aggregates are mostly exact** (C_public_entity_def is often 0/0 because most of our subset states don't define "public entity"). These are gate-question sub-aggregates and the scorer handles them well.
- **A_registration is the dominant error driver.** 4/5 states have our A < PRI's A. On WY and TX the gap is 6 points each — that's most of the total disagreement.
- **E_info_disclosed is within ±3 of PRI on CA/WI/WY but 7 points short on TX.**

### Accessibility — summary

All non-WY rows are `null / X ✗` for nearly every sub-aggregate across all runs. I.e., the scorer refused to score (`unable_to_evaluate`) most accessibility items against statute text. This is the expected-and-correct behavior: statute text does not describe portals. Accessibility scoring requires portal snapshots.

## Hypotheses for the agreement gap — **H1 confirmed for TX (2026-04-21)**

A post-dispatch statute-reading session with Dan walked §305.003 of TX Gov Code and its carve-outs, then §311.005(2) (Code Construction Act). Finding: TX §311.005(2) defines "person" to include "government or governmental subdivision or agency, business trust, estate, trust, partnership, association, and any other legal entity." Since §305.003 reads "a person must register if..." and uses the two independent (a)(1) expenditure / (a)(2) compensation triggers, the agency-as-entity reading walks out to 8–10 supportable A-items — PRI's 7 lands in the middle (likely dropping A3 under §305.004(4) and A7 as self-lobbying).

The scorer gave TX A=1 because it only had ch. 305 — no way to know "person" statutorily includes agencies. With §311.005 in the bundle the gap closes by ~6 points on A alone. **H1 (bundle scope) confirmed for TX;** expect the same pattern on the other 4 states (CA, NY, WI, WY) — each has its own code-construction / general-definitions statute that defines "person" to include entities.

Hypotheses retained for completeness, now ordered by remaining explanatory power after H1 resolution.

### H1 — statute bundle scope is too narrow for some states

- **WY** bundle is one 8.5 KB chapter file. PRI's A_registration=7 means PRI coded 7 of 11 entity types as required to register. To score A5–A11, the scorer needs statute coverage of which branches of Wyoming government are covered — this is usually in separate definitional titles or in a lobbying-act preamble. If the chapter we retrieved doesn't cite them, A5–A11 default to 0/unable.
- **TX** bundle is a single 65 KB chapter (Gov Code ch. 305), which is the lobbyist-registration statute. The PRI 2010 coding likely referenced definitions that live elsewhere in the Texas Government Code (e.g., Gov Code §305.002 definitions, §572 ethics statute cross-references). Our bundle is substantial but may be scoped too narrowly.
- **CA** bundle is two Political Reform Act sections (§§86100–86118, §§86201–86206) = 30 KB. The PRA is the right statute — but "state agency", "local agency", "public official" definitions live in §82000–§82056 (Definitions), which we did not bundle. This is likely why A5–A11 oscillates between 0 and `unable`.

Root cause: `LOBBYING_STATUTE_URLS` was curated to the *registration-and-reporting* chapter per state. The A_registration sub-aggregate questions ask about entity-type coverage, which typically lives in the *definitions* chapter. Those two chapters diverge across states.

**Test:** Manually inspect one state where we have low A agreement (e.g., CA A=3 vs PRI 6). Read CA Gov Code §82000–82056 (definitions of "state agency," "local government agency," "public official") and see whether those sections would move A5, A7, A9 from 0/unable to 1. If yes, expand `LOBBYING_STATUTE_URLS` to include definitions chapters per state.

### H2 — rubric-interpretation drift on A5–A11

The A5–A11 items ask about specific entity types (Governor's office, legislative branch, etc.). PRI appears to have coded these based on what the statute *applies to* — i.e., if the lobbying act regulates "any officer or employee of the executive branch," A6 = 1 regardless of whether the statute enumerates "executive branch agencies" as a registration class.

Our scorer may be reading A5–A11 more literally — it wants statute text naming "Governor's office" as a registration class. PRI was more liberal. Neither interpretation is wrong; they diverge.

**Test:** Read the PRI 2010 paper's §III.A footnotes carefully — do they document the coding rule? If the footnote clarifies PRI's interpretation, the scorer prompt's A-section guidance can be updated to match (this is Phase 4 work, but the scope of the prompt change depends on whether H1 or H2 dominates).

### H3 — rollup rule bug

Unlikely but possible. The rollup rule was locked 2026-04-19 in `results/20260419_pri_rollup_rule_spec.md` with 130/130 tests green. But the spec called out 9 places where our rollup diverges from PRI's 2010 protocol by necessity (reverse-scoring, gate-questions, h-frequency collapsing, etc.). A systematic bug in one of those would show as a consistent state-by-state offset, not the varied pattern we see.

**Test:** Manually compute one state's sub-aggregates from its raw JSON using the spec rules and compare to the `calibrate` report's numbers. If they match, H3 is ruled out.

### H4 — TX vintage drift

TX was scored against 2009 statute text (Justia doesn't host TX 2010). TX Gov Code ch. 305 was amended in 2010 (HB 2519 added some provisions). If PRI scored TX against the post-HB-2519 law, a 2009 retrieval will systematically under-score TX. The -14 TX gap is consistent with this but is probably not the full explanation — 14 points over A+B+E is more than typical 1-year legislative drift.

**Test:** Check TX legislative history for HB 2519 (2011 session) and any 2010-specific amendments to ch. 305. If the amendments affect A_registration or E_info_disclosed items, document the vintage-drift size and either (a) live with it or (b) bundle the 2010 TX statute from Wayback.

## Inter-run diagnostic — item-level

Flagged disclosure-law items where all 3 runs disagreed (not just majority-1-vs-2) reveal the scorer's ambiguity pattern. Sample from CA:

- `A5–A11` — scorer alternates between 0 and `unable_to_evaluate` — reflects H1 (bundle missing definitions) and H2 (no explicit enumeration in retrieved text).
- `B1, B2` (government exemptions, reverse-scored) — scorer is inconsistent about reverse-scoring direction across runs despite explicit guidance in the rubric item. This is a prompt-fidelity issue worth a separate look.
- `D2_present`, `D2_value` (time-threshold materiality exemption) — scorer sometimes reports present, sometimes not — likely genuine rubric interpretation ambiguity on whether "percent of work time" language in the statute counts as a threshold.

## What NOT to do next

- **Don't start Phase 4 prompt iteration.** The baseline's problems are upstream of prompt phrasing: bundle scope (H1) and rubric interpretation (H2) dominate. Iterating the prompt against a bad input space is overfitting.
- **Don't treat accessibility as in-scope for statute-based calibration.** Confirmed — accessibility needs portal snapshots or a different rubric mapping. The plan already scoped only PRI disclosure_law + accessibility for calibration; the accessibility leg of that should now be formally descoped from this branch and left for the `scoring` branch or a future accessibility-specific line.

## Next steps — decided 2026-04-21

Strategic direction (agreed with Dan in the 2026-04-21 post-dispatch session):

1. **Pilot-first, then scale.** The 3-fellow × ~17-state rollout should NOT start until the 5-state pilot's bundle-scope fix is validated. Reason: meta-dictionary schema isn't designed yet; parallel work before schema lockdown would fork into three incompatible schemas.
2. **Expand `LOBBYING_STATUTE_URLS` to a richer per-state shape.** Current: `{(state, year): [url, ...]}`. Proposed: `{(state, year): {"lobbying_chapters": [...], "support_chapters": [(url, note), ...], "interpretive_notes": [...]}}`. `support_chapters` holds cross-referenced definitions / code-construction acts (TX: ch. 311; CA: Gov Code §18 + §§82000-82056; NY: Gen Constr Law §37; WI: Stats ch. 990; WY: Stats title 8). `interpretive_notes` captures static rubric-protocol facts with citations.
3. **Hybrid retrieval-guide + metadata.** Lean toward bundle expansion (retrieval-guide B) so the scorer sees source text; use `interpretive_notes` (metadata A) only for facts not obvious from statute text (e.g., "PRI coded 'volunteer lobbyists' per paper §III.A based on threshold presence"). Don't encode legal interpretation as static data where statute text would do the same job more robustly.
4. **Success criterion for the re-score:** disclosure-law exact-match agreement crosses a threshold (specific value set after the numbers come in — premature to fix now); inter-run disagreement < 15% on disclosure_law. If pilot hits this, extract the schema as the fellow handoff deliverable.
5. **Accessibility: out of scope for statute calibration.** Confirmed — portal-feature rubric fundamentally doesn't fit statute text. Leave accessibility work to `scoring` branch or a future portal-based line.
6. **Non-responder caveat for fellow rollout.** The 5-state pilot is all PRI responders. Fellows' 15-17 states each will include non-responders (16 of 50 total). Non-responder agreement rates will almost certainly be lower — ground-truth-quality reason, not a pipeline problem. Plan to report responder/non-responder agreement separately from the start (`calibrate` already supports this via `out_of_partition`).

Hypotheses retained for completeness (H1 confirmed; others deprioritized):

- **H1 (bundle scope)** — confirmed via TX walkthrough. Action: expand bundles.
- **H2 (rubric-interpretation drift)** — still possible but less likely dominant. Re-score after H1 fix; if residual gap remains, re-open H2.
- **H3 (rollup bug)** — low probability; 130/130 tests green, bug pattern would be systematic, not state-specific as observed.
- **H4 (TX 2009 vintage drift)** — probably a small contributor; -14 TX gap is better-explained by H1 (TX ch. 305's exemption structure + missing ch. 311).

## Artifacts

- `results/20260420_consistency_{CA,TX,NY,WI,WY}.md` — per-state inter-run consistency
- `results/20260420_baseline_disclosure_law_4states.md` — agreement report, CA/NY/WI/WY
- `results/20260420_baseline_disclosure_law_TX.md` — agreement report, TX (2009 vintage)
- `results/20260420_baseline_accessibility_4states.md` — agreement report, CA/NY/WI/WY accessibility (mostly null)
- `results/20260420_baseline_accessibility_TX.md` — agreement report, TX accessibility (mostly null)
- `data/scores/{STATE}/statute/{VINTAGE}/{r1,r2,r3}/` — 15 run directories with raw JSON + scored CSVs + StatuteRunMetadata

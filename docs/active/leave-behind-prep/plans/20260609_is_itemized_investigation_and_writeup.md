# Plan: is_itemized investigation + Suhan writeup

**Date:** 2026-06-09 (filed at session-end of `20260609_gpt5mini_reasoning_effort_three_arm_dispatch`)
**Predecessor convo:** [`convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md`](../convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md)
**Status:** TODO. Investigation step + writeup are gated on this plan's first decision; everything downstream is conditional.

## What's already decided (don't relitigate)

- **Ship medium with brief-v3** as the production-shipping baseline, modulo the open `is_itemized` question.
- `ReasonableDate` validator stays regardless (defense-in-depth; commit `5a87c79`).
- Minimal arm is dropped from the writeup (quality floor failure on reporting_period).
- Low arm is dropped from the writeup unless someone explicitly re-tests it at brief-v3 (~$0.40, ~5min); not blocking.
- Filing `1423176` is logged as issue [#54](https://github.com/danparshall/lobby_analysis/issues/54) and removed from any future-arm dispatches via TBD denylist mechanism (denylist not yet implemented; out of scope for this plan).

## The open question this plan resolves

The brief-v3 cross-arm agreement run ([`results/20260609_cross_arm_agreement_briefv3.md`](../results/20260609_cross_arm_agreement_briefv3.md)) showed brief-v3 fixed `is_current` cleanly (94%→100%, no leak) but **introduced a new side effect on `is_itemized`**:

- briefv2 emitted is_itemized on 5/100 filings (all 5 agreeing with sonnet)
- briefv3 emits is_itemized on **0/100** filings — full abstention
- medium_briefv2 vs medium_briefv3 panel confirms: 95 both-null + 5 one-null + 0 both-emit

Brief-v3's step 8 ("default is_current=True for originals") apparently nudged mini toward more abstention on adjacent optional fields. **We don't yet know whether is_itemized's abstention is correct or a regression.**

This matters because we're now three brief revisions deep and each one fixes one field while perturbing another (v2: fixed period, broke is_current; v3: fixed is_current, broke is_itemized). If we keep iterating, we may never converge. Before considering brief-v4, we need to know whether **sonnet's `is_itemized` emissions are ground truth or guesswork.**

## Investigation procedure (next session)

### Step 1 — Identify the 5 rids where briefv2 emits is_itemized but briefv3 doesn't

The cleanest path: write a small `is_itemized_spotcheck.py` modeled on `is_current_spotcheck.py`. It walks `medium_briefv2` vs `medium_briefv3` on the 100-filing intersection and prints the 5 rids where briefv2 emits non-null and briefv3 emits null, along with their sonnet values for comparison.

Script outline (~50 lines, follows the existing spotcheck-script pattern):
- Load each arm's filing.json for each rid in `find_briefv2_rids(data_dir)`
- Filter to rids where `briefv2.is_itemized is not None and briefv3.is_itemized is None`
- For each, print `(rid, sonnet_value, briefv2_value, briefv3_value)`
- Should yield exactly 5 rids

Save as `scripts/gpt5mini_oh_300slice_is_itemized_spotcheck.py` per the existing naming convention. ~5 minutes to write.

### Step 2 — Read raw HTML for each of the 5 rids

For each rid, check `data/oh_portal/raw/<rid>/*/raw.html` and look at Section II (or wherever expenditure itemization would show up in the OH AER form). Three questions per filing:

1. **Does Section II contain any expenditure rows at all?** (Most OH AERs have empty Section II — ~95% per Day-1 finding. is_itemized may be undefined when Section II is empty.)
2. **If populated, are the rows individually itemized (separate line per expenditure) or summarized (totals only)?**
3. **Does the form have any explicit "itemized: yes/no" UI element?** (Probably not — the OH form likely doesn't expose this directly; it's a derived field.)

### Step 3 — Categorize each of the 5 by what the source actually supports

For each rid, the answer is one of:

- **GROUND_TRUTH_EMITS:** Source clearly shows itemized vs non-itemized; sonnet's value is correct; briefv3 lost real signal.
- **GROUND_TRUTH_ABSTAINS:** Source is empty/silent on itemization; sonnet was defaulting `False` (or guessing); briefv2 matched the guess; **briefv3's abstention is the correct behavior.**
- **AMBIGUOUS:** Source has some signal but not unambiguous; reasonable extractors could go either way.

### Step 4 — Decide based on the categorization

| 5/5 GROUND_TRUTH_EMITS | brief-v4 with explicit is_itemized guidance. Worth iterating. |
| 5/5 GROUND_TRUTH_ABSTAINS | **Ship brief-v3 unchanged.** Writeup frames briefv3 as "more honest about ambiguous fields than Sonnet." |
| 5/5 AMBIGUOUS | Ship brief-v3 unchanged. Writeup notes is_itemized as a known-low-coverage derived field; downstream consumers should treat as advisory. |
| Mixed | Document the mix in the writeup. Decision depends on the mix — if mostly ABSTAINS, ship v3; if mostly EMITS, consider v4. |

**Strong prior (mine, not Dan's):** the answer will be 4-5 GROUND_TRUTH_ABSTAINS. Most OH AERs have empty Section II, and is_itemized on empty Section II is semantically undefined. Sonnet probably defaults `False`; mini-briefv2 mirrored that default; mini-briefv3 correctly abstains. This would mean **brief-v3 is the final brief**, no v4 needed.

But I genuinely don't know. The investigation resolves it cheaply.

## Other open follow-ups (lower priority)

### Re-evaluate the extraction_warnings 30%→13% drop framing

Disagreement on this thread is unresolved:

- **Desktop agent's framing:** "brief-v2/v3 stopped narrating procedural moves; for an end-user report it's noise, for an auditor it's signal."
- **Web agent's (my) framing:** lost audit-trail signal is a small quality-floor concern, not neutral churn. For Suhan-as-auditor specifically, the loss matters more than for a steady-state production run.

This isn't blocking the writeup, but the writeup's "honest limitations" section should land on one framing. Worth a 30-second decision before writing.

### Brief change → unintended-side-effect pattern

Three brief revisions, three rounds of "fixed one field, perturbed another." If brief-v4 is needed (only if the investigation says GROUND_TRUTH_EMITS), there's structural risk it'll do the same. **Recommend adopting a "check the full cross-arm before committing" discipline going forward** — every brief revision requires a $0.66 full-medium re-extraction + full cross-arm agreement scan to confirm no new side effects. This is part of the brief-iteration cost and should be budgeted.

### Filing 1423176 denylist mechanism (issue #54)

Not in scope for this plan. Separate follow-up. Should be designed at the `dispatch.py` level so all harnesses honor it.

## The Suhan writeup

After the is_itemized investigation resolves, the writeup becomes the actual leave-behind artifact. Provisional shape:

- **Headline:** Mini at medium with brief-v3 is shippable for OH AER extraction. ~$0.0066/filing vs Sonnet's $0.0175, ~$300 full-corpus vs Sonnet's $800.
- **Quality:** 100% reporting_period agreement, ≥99% on identity/dollar/list-count fields when both emit, sonnet-matching behavior on every committed field. One known low-coverage derived field (`is_itemized`) where mini abstains — [resolution depends on investigation].
- **Methodology:** 3-arm reasoning_effort dispatch (medium/low/minimal × 100), cross-arm field-agreement analyzer, brief surgery in two passes (period-shorthand expansion + is_current default).
- **Honest limitations:**
  - Low and minimal arms not re-tested at brief-v3 (optional)
  - One pathological filing (#54, 1423176) burns 5-10× median cost across every configuration — long-tail risk on full-corpus extrapolation
  - extraction_warnings: brief-v3 emits fewer audit-trail confirmations than original brief [framing to decide]
- **Schema-side:** `ReasonableDate` validator (year ∈ [1990, current+1]) on all date fields catches malformed extractor output structurally, independent of brief.
- **Cost stack:** $1.89 total for the validation work; $0.66 per future brief iteration.

Target audience: Suhan as the technical evaluator. Should be skim-able in 3 minutes, defensible under detailed questioning. Probably 1-2 pages of markdown plus the cross-arm agreement tables as appendices.

## Estimated effort for next session

| step | effort | cost |
|---|---|---|
| Write `is_itemized_spotcheck.py` | 5 min | $0 |
| Run it, identify 5 rids | 30 sec | $0 |
| Read 5 raw HTMLs, categorize | 5-10 min | $0 |
| Decide (ship v3 / brief-v4) | based on step 3 |
| (Conditional) Brief-v4 + full retest + cross-arm | 30 min | ~$0.66 |
| Write Suhan writeup | 30-45 min | $0 |
| Finish-convo + STATUS | 10 min | $0 |
| **Total** | **~1-2 hours** | **$0-0.66** |

## Files to read first (in order)

1. This plan
2. [`convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md`](../convos/20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md) — full session narrative
3. [`results/20260609_cross_arm_agreement_briefv3.md`](../results/20260609_cross_arm_agreement_briefv3.md) — the latest cross-arm output that surfaced this question
4. [`results/20260609_cross_arm_agreement_briefv2.md`](../results/20260609_cross_arm_agreement_briefv2.md) — for the briefv2 vs briefv3 comparison
5. `src/lobby_analysis/oh_portal/extraction_brief.py` — brief-v3 (current state, sha `57ac0b6c`)
6. `src/lobby_analysis/models/filings.py` — to read the `is_itemized` field's docstring and any validator behavior
7. [Issue #54](https://github.com/danparshall/lobby_analysis/issues/54) — for context on the 1423176 long-tail, since the writeup will reference it

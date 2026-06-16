# Mini-swap chain-level experiment + composer-side normalizations plan

**Date:** 2026-06-15
**Branch:** leave-behind-prep

## Summary

Session opened as a leave-behind-prep audit ("what's left on this
branch") and pivoted twice: first to confirming what's already done
(user noted #52 OH chain composer + `releases/oh/` had just merged via
PR #59), then to the user's question "have we actually tried the
mini-swap?" That question prompted a $0 end-to-end experiment using
existing briefv2 mini outputs on disk: stage them in a parallel
directory, run the freshly-shipped OH chain composer on them, and diff
against the shipped sonnet chain on the same 100 rids.

The experiment surfaced a *much* more decisive result than the
2026-06-13 provisional findings doc had framed: on LUPA AERs (the form
type the brief targets), briefv2 mini produces chain output that is
structurally equivalent to sonnet — same position count (236=236),
same per-filing median, same bill resolution (zero disagreement on
bill_id, sponsor IDs, etc.). The residual diff is two composer-side
conventions that are deterministically closable without any brief
change or new API spend.

A mid-experiment correction: my initial findings draft had the
"positions slot mismatch" issue (Q1 of the 2026-06-13 doc) framed as
"hoist description into general_issue_area." Reading the composer code
revealed that hoist is already implemented (`POSITION_KIND_SUBJECT_HOISTED`,
PR #59) and accounts for only 2 of 426 mini chain rows. The actual
residual issue is the *opposite* direction: mini routes subject content
into the `bill_reference` slot, producing 59 `bill_referenced +
unmatched` chain rows that have no analog in sonnet (whose unmatched
rate is 1.2% vs mini's 14.2%). The proposed composer-side fix is a
digit-check demotion: unmatched bill_referenced rows with no digits in
the label get demoted to subject_general, preserving sonnet's
malformed-bill audit signal while closing mini's order-of-magnitude diff.

Session closed with two deliverables (findings doc + plan doc) written
for fresh-agent pickup. No code changes this session; implementation
is delegated per Dan's plan-then-fresh-session memory.

## Topics Explored

- Branch state audit (#52 closed via PR #59 mid-session;
  `oh-chain-composer` now archived; recursive read of RESEARCH_LOG /
  STATUS / open issues)
- "Have we tried the mini-swap?" — distinguishing validation (extensive)
  from production swap (zero) from external writeup (zero)
- End-to-end chain-level experiment: stage briefv2 mini outputs → run
  composer → diff against shipped sonnet chain
- Per-section position-count comparison (LUPA vs EUPA) → mini matches
  sonnet on LUPA, both abstain heavily on EUPA (mini slightly less)
- `principal_id` / `lobbyist_id` disagreement root-cause: model-emitted
  schema fields, no consistent convention from mini
- Row-set diff position-kind × bill_class breakdown — revealed the
  subject-content-in-bill_reference pattern; 92% concentrated on 3
  EUPA filings
- Mid-flight correction of the slot-mismatch story (description-hoist
  already shipped; real issue is the opposite direction)
- Plan structure for fresh-agent pickup (TDD-ready, self-contained,
  branch-state-explicit)

## Provisional Findings

- **On LUPA AERs:** briefv2 mini is operationally equivalent to sonnet
  at chain-row level. Same position count, same emit rate, perfect
  bill resolution.
- **On EUPA AERs:** both models abstain at high rates (sonnet 78%, mini
  70%). Position-content sparsity is a form-type property, not a model
  failure. Earlier hypothesis (mini follows the Legislative-AER brief
  literally and over-abstains on Executive AERs) is *not* supported —
  mini actually emits *more* EUPA positions than sonnet in this slice.
- **Two residual chain-level gaps** are composer-side conventions, both
  deterministically closable:
  1. Entity-ID derivation: 98% of `principal_id` / `lobbyist_id`
     disagreement comes from sonnet using a kebab-case convention
     (`org-cleveland-browns-oh`) while mini uses inconsistent formats
     (`org:Cleveland_Browns`, raw name, or empty). Names agree in every
     case.
  2. Unmatched bill_referenced demotion: 59 of mini's 61 row-set-diff
     rows are subject content placed in `bill_reference` slot; composer
     correctly flags `unmatched` but pollutes the chain. Digit-check
     demotion rule closes ~all of this while preserving the 18-row
     malformed-bill audit signal sonnet exercises.
- **The is_itemized regression that gated the 2026-06-13 lock decision
  is moot for the chain artifact** — `is_itemized` is a filing-level
  field, not a chain-row field. Open for the filings TSV, irrelevant
  for the chain.
- **briefv2 mini is materially closer to ship-ready than the 2026-06-13
  provisional framing implied** for the chain artifact.

## Decisions Made

- **Recommendation captured in findings doc as "provisional
  ship-with-normalization."** Briefv2 mini as production OH extractor;
  composer takes responsibility for entity-ID derivation +
  bill_referenced-unmatched demotion. ~half-day implementation, $0
  spend.
- **No execution this session.** Per Dan's "plan-then-fresh-session"
  memory, stopped at plan-finalize + finish-convo. Implementation by
  fresh agent.
- **Implementation branch should be cut off main**, NOT off
  leave-behind-prep — the OH chain composer code lives on main and
  leave-behind-prep is ~90 commits behind.
- **Plan doc:**
  [`plans/20260615_composer_side_mini_swap_normalizations.md`](../plans/20260615_composer_side_mini_swap_normalizations.md).

## Results

- [`results/20260615_mini_swap_chain_level_evidence.md`](../results/20260615_mini_swap_chain_level_evidence.md)
  — full findings doc: experiment setup, quantitative results,
  position-kind breakdown, concentration analysis, what supersedes
  the 2026-06-13 provisional doc, honest limitations, decision
  recommendation.

## Open Questions

- **Cost-identity reconciliation** (which model id = the $0.0066/filing
  measurement?). Required before any external dollar figure; not
  required for composer changes. Dan's `personal_info.md` references
  the Aug-2025 mini at $0.25/$2.00; current cost-optimized mini is
  GPT-5.4 at $0.75/$4.50 (3× input). Anchor: `MODEL_ID_DATED` in
  `src/lobby_analysis/oh_portal/extract_openai.py`.
- **Q4: is_itemized generalization beyond JLEC forms** (39-rid
  follow-up, $0, data on disk). Useful for a filings-TSV writeup; not
  required for chain ship-readiness.
- **Q5: OAC granularity decision** — does the composer want rule-level
  granularity for the OAC/JCARR edge or rolled-up subjects? Mini's 2
  oac_rule emissions vs sonnet's rolled-up subject for the same filing
  reflect this. Dan's call.
- **Filings TSV is_itemized / total_expenditure conventions** — separate
  from chain; briefv2 vs briefv3 vs sonnet still divergent. Filings TSV
  story is owed independently.
- **Amendment-path / `is_current` corpus sweep** — live slice has zero
  amendments; validation deferred until a slice with amendments exists.
- **Should the regenerated chain artifact** (post-Step-1 normalization)
  go to main as a sonnet-baseline re-ship before the mini swap, or
  alongside the mini-sourced version? Dan's call at acceptance time.

## Process notes

- The "have we actually tried it" question reframed the work
  productively. Previous framing was "what does the 2026-06-13 doc say
  is still owed?" — that anchored on incomplete validation steps.
  Reframing to "what does mini-as-extractor produce as the released
  chain artifact?" cut directly to the question that matters.
- Mid-experiment correction (description-hoist is already in; real
  issue is the opposite direction) reinforces the importance of
  reading existing code before writing a "needs implementation" plan.
  Saved the next agent from chasing a phantom fix.
- The chain composer already cites the 2026-06-13 findings doc in its
  classifier docstring (`POSITION_KIND_SUBJECT_HOISTED` comment) — the
  PR #59 implementer did read it; my misreading was on my end.

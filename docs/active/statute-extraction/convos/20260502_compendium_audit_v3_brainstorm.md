# 2026-05-02 — Compendium Audit v3 Brainstorm

**Branch:** `statute-extraction` (worktree: `.worktrees/statute-extraction/`)
**Status:** closed; brainstorm complete; Phase 0 plan written
**Spawning artifact:** [`plans/_handoffs/20260501_compendium_item_audit_handoff.md`](../plans/_handoffs/20260501_compendium_item_audit_handoff.md)

## Summary

Brainstorm to design the v3 compendium audit — the response to iter-1's surfaced curation gap that `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is target-axis (lobbying *directed at* admin agencies) but its name is direction-ambiguous, and the harness only avoided a wrong reading by accident (single-preposition cue in the description). On rows where the model picks consistently-but-wrong, the inter-run-disagreement signal that caught this would be silent.

The brainstorm landed on a **descriptions + axis-in-ID** strategy (no schema bump), executed as a **three-phase audit** (concerns sweep → solution design → fixes), with **Phase 0 sweeping the full 141 rows up front** so cross-domain patterns inform per-domain axis vocabulary harmonization. This session ships the **Phase 0 plan only**; Phase 1's plan gets written *after* the concerns doc exists, since its solution-design shape depends on what Phase 0 finds.

## Topics Explored

- **Whether v3 is the right next move.** Iter-2 already added a per-chunk preamble for `definitions` axes; that's a prompt-side band-aid. The handoff thesis is that compendium-side disambiguation must be authoritative because consistent-but-wrong rows give no inter-run signal. Accepted, with the qualifier that Phase 0's full sweep is itself the test of how widespread the latent rate is.
- **Schema-axis-field tradeoff (Option 1 vs 2 vs 3).** Considered v1.4 schema bump adding `axis: Axis | None`; rejected because (a) the axis taxonomy is per-domain not global, so a single enum is lossy or incoherent; (b) iter-1 evidence is N=1, not enough to drive a schema bump; (c) descriptions + ID renames cover the audit's job; (d) YAGNI. Option 3 (free-form `tags` field) rejected as deferring the taxonomy decision rather than making it.
- **Axis-in-ID convention.** User-proposed `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` pattern (e.g., `DEF_LOBBYING_TARGET_ADMIN_AGENCIES`, `DEF_LOBBYING_ACTOR_PUBLIC_EMPLOYEE`). Gives most of Option 1's machine-readability (axis greppable from ID) without the schema bump. Axis-less rows (enforcement, penalties) permit the pattern's absence — convention is opt-in where the axis applies.
- **Sequencing: per-domain vs full-sweep first.** Initial leaning was per-domain (smallest-first, `definitions` as canary). User pushed back: full-sweep first lets cross-domain patterns inform per-domain vocabulary harmonization, instead of locking `definitions`'s axes before seeing how `reporting`'s axes interact. Accepted; v3's flow is now sweep → design → fix.
- **Three-phase decoupling.** Decided to separate concern-finding from solution-design as distinct cognitive tasks. Phase 0 = classify, don't fix. Phase 1 = group concerns by pattern, propose fixes, lock per-domain axis vocabularies. Phase 2 = apply fixes in cascade-cohesion batches.
- **Concerns-doc tag taxonomy.** Strawman of 7 tags (`axis-ambiguous-name`, `name-misleading`, `description-rubric-drift`, `cluster-asks-two-questions`, `cross-row-overlap`, `wrong-domain`, `multi-concern`); user added `other-issue` as a free-text escape hatch. Locked as starting-point posture (Phase 0 may surface tags that Phase 1 splits or merges).
- **Severity field on concerns.** Considered then dropped. Per-row severity is row-level guesswork; Phase 1's grouping pass produces cluster-level prioritization signal naturally (e.g., "12 axis-ambiguous rows in `definitions`" is its own high-priority cluster, no per-row tag needed). Adds cognitive cost to Phase 0 for output Phase 1 reproduces better.
- **One-plan vs staged-plan flow.** Chose staged: ship Phase 0 plan only, write Phase 1's plan *after* concerns doc lands. Rationale: Phase 1's solution-design shape depends on Phase 0's findings (e.g., 80% description-fidelity vs 80% axis-ambiguous concerns produce very different Phase 1 plans). Mitigation against losing the thread: Phase 0 plan ends with a "Follow-up stages" footer naming Phase 1 + Phase 2 informationally.

## Provisional Findings

- The latent-axis-bug rate is unknown. Iter-1's evidence is N=1 by accident. Phase 0's full sweep is itself the population estimate.
- Axis vocabulary is genuinely per-domain. `definitions` uses {target, actor, threshold (quant + qual)}; `reporting` will use something like {cadence, scope, granularity}; `contact_log` will use a different set. A global axis enum would be lossy; per-domain natural-language vocabularies (in chunk-frame preambles + IDs) are the right structure.
- Rename cascade per fix is non-trivial: tests (24 compendium tests + ID references), `compendium/framework_dedup_map.csv` (254 entries), `data/extractions/<STATE>/<VINTAGE>/<DOMAIN>/<run_id>/{raw_output.json, field_requirements.json}` (3 OH `definitions` run dirs reference 7 IDs each), chunk-frame preambles, any `.py` source. Phase 1 must include cascade-cost methodology so Phase 2's batching is informed.
- The v2 audit's Decision Log (D1–D11 in `docs/COMPENDIUM_AUDIT.md`) is the procedural template. v3 continues numbering at D12+.

## Decisions Made

| topic | decision |
|---|---|
| Strategy | Option 2: descriptions + axis-in-ID renames; **no schema-axis-field**. Future evidence may reopen as v1.5 if needed |
| ID convention | `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` where axis applies; absence permitted for axis-less rows (enforcement, penalties) |
| Audit flow | Three phases: P0 concerns sweep (full 141 rows) → P1 solution design → P2 apply fixes in batches |
| Sweep scope | Full 141 rows up front; cross-domain patterns inform per-domain axis vocabulary harmonization |
| Plan staging | Ship P0 plan only this session; P1 plan written after concerns doc exists; P0 plan has "Follow-up stages" footer to keep the thread |
| Concerns-doc tags | 8 starting-point tags including `other-issue` escape hatch; severity field dropped |
| Spot-check | Folded into P0 (full sweep is the spot-check at scale); no separate 5–10-row deliverable |
| Schema recommendation | Standing answer: Option 2 stands; v3 doesn't reopen unless P0 surfaces evidence-of-need |
| Decision Log | v3 continues `docs/COMPENDIUM_AUDIT.md` numbering at D12+ |

**Plan produced:** [`plans/20260502_compendium_item_audit_v3_phase0.md`](../plans/20260502_compendium_item_audit_v3_phase0.md)

## Open Questions

These don't block Phase 0 plan acceptance; surface during Phase 0 execution or in Phase 1's planning:

- Per-domain axis vocabularies for `reporting`, `contact_log`, `financial`, `relationship`, `revolving_door`, `accessibility`, `enforcement`, `other`. Phase 0 will reveal the candidate vocabularies; Phase 1 locks them.
- Whether some `definitions` rows are legitimately multi-axis (e.g., `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` is actor-axis but threshold-flavored). Convention currently forces a single primary axis; Phase 1 decides whether to allow secondary-axis annotation in description or split into multiple rows.
- Whether axis-in-ID renames cascade to chunk-frame preambles (`src/scoring/chunk_frames/definitions.md`) or whether preambles can stay axis-vocabulary-only. Phase 1 decides.
- Whether the v1.2 `CompendiumDomain` Literal needs additional values (e.g., a `lifecycle` or `process` domain) revealed by P0 — currently we have 10 domains.

## Goal of this session

Design the v3 compendium audit's procedural shape, deliver the Phase 0 plan, and preserve the thread to Phases 1 + 2 without locking their design prematurely.

## Pre-work done before brainstorm

- Pre-flight reads: STATUS.md (current focus + active branch row), README.md, this branch's RESEARCH_LOG.md (iter-1 dispatch context), the handoff doc, the iter-1 analysis doc, the iter-1 plan (for style reference).
- Confirmed worktree at `.worktrees/statute-extraction/` is the correct workspace.
- Read brainstorming + write-a-plan skills.
- Verified PR #5 v2 audit landed (compendium = 141 rows; `docs/COMPENDIUM_AUDIT.md` exists at repo root with D1–D11).

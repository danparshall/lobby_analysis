<!-- Generated during: convos/20260514_post_framing_compendium_review_dispatch.md -->

# Post-framing review synopsis

**Date:** 2026-05-16
**Branch:** `extraction-harness-brainstorm`
**Purpose:** Speed-readable walkthrough of the two 2026-05-14 post-framing reviews — what they say together, what's blocking what, what decisions need user input.

**Source reports:**
- Compendium-side: [`docs/historical/compendium-source-extracts/results/20260514_post_framing_review.md`](../../../historical/compendium-source-extracts/results/20260514_post_framing_review.md) (commit `770f866`)
- Harness-side: [`results/20260514_post_framing_review.md`](20260514_post_framing_review.md) (commit `0ccbb86`)

**Originating dispatcher convos:**
- [`convos/20260514_post_framing_compendium_review_dispatch.md`](../convos/20260514_post_framing_compendium_review_dispatch.md) (compendium review parent, ran on this branch)
- [`convos/20260514_post_framing_harness_review.md`](../convos/20260514_post_framing_harness_review.md) (harness review parent, ran on main worktree)

**Downstream plan:** [`plans/20260515_apply_post_framing_review_recommendations_plan.md`](../plans/20260515_apply_post_framing_review_recommendations_plan.md)

---

## The 30,000-foot view

Two reviewers hit the same load-bearing concern from different sides: **the Ralph loop isn't actually supported yet.** Everything else in the two reports is either downstream of that or unrelated cleanup.

## What "Ralph loop isn't supported" actually means

The loop is written in `docs/RESEARCH_ARC.md` as `loss(prompt) = Σ over (state, vintage, rubric) |f_rubric(SMR) − published_score|`, with σ_noise estimated from N independent re-runs. The reviewers say this has two holes:

### Hole 1 — the math is uneven (C-F1, BLOCKER)

The `Σ` treats every `(state, vintage, rubric)` summand uniformly. But ground truth at the per-state per-atomic-item level only exists for two rubrics:
- **CPI 2015 C11** — 700 cells (50 states × 14 items).
- **Sunlight 2015** — 200 cells (50 states × 4 items).

The other six rubrics validate at sub-aggregate, weak-inequality, or zero-US-state granularity:
- **PRI 2010** — per-state per-item only via `docs/historical/pri-2026-rescore/` (provenance check needed before Phase C consumes).
- **Newmark 2017** — sub-aggregate only (50 × 2 cells = 100 anchors).
- **Newmark 2005**, **Opheim 1991** — total-only, weak-inequality (`our_partial ≤ published_total`; per-section sub-aggregates not published).
- **HG 2007** — strong validation requires re-retrieval from the CPI site (not in the archive); without that, weak-inequality on the 83/100 disclosure partial.
- **FOCAL 2024** — zero per-state US ground truth; only Federal LDA (81/180 raw points, exact match) plus 27 non-US country anchors.

`loss(prompt)` will silently overweight whichever rubric has the most projectable summands. RESEARCH_ARC §"Three risks worth naming up front" risk #1 names this abstractly; the compendium reviewer made it concrete. **This needs an explicit per-rubric normalization decision before `phase-c-projection-tdd` writes any projection code.**

### Hole 2 — the plumbing isn't there (H-F2, SHOULD-FIX)

None of the four planned modules (`models_v2`, `chunks_v2`, `retrieval_v2`, `scoring_v2`) is positioned to drive the loop at all:
- No `n_runs` primitive for σ_noise estimation at fixed prompt-sha.
- No batch invocation across `(state, vintage, rubric)`.
- No per-rubric loss aggregator.
- No prompt-version diff.

"The orchestrator" is named as out-of-scope in every brainstorm convo (chunks line 147; retrieval line 130; brief-writer lines 86, 185). It's the thing the Ralph loop actually requires. **The four-component harness ships extraction-complete, not Ralph-loop-ready.** There's a 5th component to name and schedule.

### The compound problem

These holes compound. Even if `phase-c-projection-tdd` picks a perfect per-rubric normalization, no component in the queue actually runs the loop. The first end-to-end Ralph iteration end-to-end needs `scoring_v2` + a CPI 2015 C11 projection + an OH 2015 statute bundle + a not-yet-named orchestrator converging across four branches.

---

## Two design forks that block `scoring_v2`

Outside the Ralph-loop theme, the harness reviewer surfaced two concrete code-shape issues that the `scoring_v2` impl plan can't ignore.

### Fork 1 — Which `EvidenceSpan` does `CompendiumCell.provenance` hold? (H-F1, SHOULD-FIX)

There are currently two `EvidenceSpan` Pydantic classes, both exported as public names of their packages:

| Class | Fields | Semantics |
|---|---|---|
| `models_v2.EvidenceSpan` | `section_reference`, `quoted_span` (≤200 chars), `artifact_path`, `url` | Statute-axis semantic provenance — what Phase C reads |
| `retrieval_v2.EvidenceSpan` | `citation_type`, `document_index`, `cited_text`, `start_char_index`, `end_char_index` | Citations-API machine-level provenance |

The `scoring_v2` brainstorm Q8 locked `CompendiumCell.provenance: tuple[EvidenceSpan, ...]` and didn't pick which class. The reviewer's point: these aren't aliasable — they're genuinely different shapes for genuinely different purposes.

**Three options:**
- **A. Pick semantic.** `scoring_v2` derives a `models_v2.EvidenceSpan` from each Citations span at brief-write time. Loses raw char indices unless preserved elsewhere. Phase C reads semantic directly.
- **B. Pick machine.** Phase C does its own section-reference + quoted-text parsing in 8 different projection modules.
- **C. Wrap both.** Define `CompendiumCellProvenance` with `(machine_span, semantic_span)`; `CompendiumCell.provenance` holds those. Richer; doubles the field count.

**Recommendation (not pre-locked):** lean A — Phase C reads statute *sections*, not char indices. C is the richer alternative if the legal-vs-practical gap as a research artifact wants the machine span available for cross-state replicability checks. B is the path of most Phase C work and least scoring_v2 work — usually the wrong tradeoff.

This is the one fork actively blocking the planned next-work-item (`scoring_v2` impl plan).

### Fork 2 — How does `StateVintageExtraction` say "I'm only half-populated"? (H-F3, OBSERVATION)

`StateVintageExtraction.cells` is a flat 186-cell dict. This branch's scope is legal-only — extraction produces 131 legal cells + 5 dual-axis legal halves = **136 cells**. The remaining **50 practical-only + 5 dual-axis practical halves = 55 cells** come from the future Prong-2 sibling.

Today, a half-filled SMR is indistinguishable from a complete one. A Phase C projection that reads practical cells will silently miscompute when fed a legal-only extraction.

**Two options:**
- **A. `axis_coverage: frozenset[Literal["legal", "practical"]]` field on `StateVintageExtraction`.** Validator enforces every cell's axis is in the set. Phase C consumers branch on coverage before projecting.
- **B. Type split.** `LegalAxisExtraction` and `PracticalAxisExtraction` merge into `StateVintageExtraction`. More wiring, more explicit.

**Recommendation (not pre-locked):** lean A — it's a coverage property, not a type property; the cells themselves are typed correctly. B forces a wrapper either way once you have to merge legal + practical.

---

## Cleanup tier (independent, cheap)

### C-F2 — TSV-vs-docs status drift (SHOULD-FIX)

- TSV column 7 (`status`): 181/181 rows = `firm` (verified by `awk` this session).
- `compendium/README.md` line 47: "180 firm + 1 path_b_unvalidated".
- `compendium/NAMING_CONVENTIONS.md`: same claim.
- OS-1's unvalidated status is encoded *implicitly* via `n_rubrics=0` + the literal string `(unvalidated; path-b)` in `rubrics_reading`.

**Decision:** which side moves?
- **A.** Regenerate the TSV to make `path_b_unvalidated` a real status value (more discoverable; consumers reading `status` get a real value to branch on).
- **B.** Rewrite the README + NAMING_CONVENTIONS to describe the actual encoding (cheaper; no TSV regen).

### C-F4 — Pre-rename row IDs in projection mapping docs (OBSERVATION)

- 9 per-rubric projection mapping docs at `docs/historical/compendium-source-extracts/results/projections/*_projection_mapping.md` use **pre-rename** row IDs throughout — 247 occurrences total — by `§10.1` design (archived material isn't rewritten).
- When `phase-c-projection-tdd` writes projection functions reading these docs, every row_id lookup must route through `§10.1`'s resolver table or `src/lobby_analysis/row_id_renamer.py:RENAMES`. Easy to skip and produce silent miscoding.

**Mitigation:** a small TDD-built script `tools/check_mapping_doc_row_ids.py` that asserts every row_id mentioned in a mapping doc is either in the v2 TSV or in `RENAMES`. Run as a pre-merge guard on projection PRs.

---

## Far-future-but-named

### C-F3 — Legal-vs-practical content-field gap (SHOULD-FIX)

Under the new framing (RESEARCH_ARC §"Three prongs": "the gap between what the statute *requires* and what the portal *actually exposes* is itself observable and queryable"), every legal-axis row asserting a content requirement on a disclosure artifact ought to have a practical-axis counterpart.

**Empirically asymmetric:**
- 35 `lobbyist_spending_report_includes_*` rows — legal-only.
- 13 `lobbyist_reg_form_includes_*` rows — legal-only.
- 9 `lobbying_contact_log_includes_*` rows — legal-only.

No practical-axis row asks "does the portal expose `<field>`?" for any of these. The 5 dual-axis rows handle *artifact existence* (does the portal expose the report at all) but not *content-field surfacing on the artifact*.

**Two routes — neither is "re-open v2":**
- Per-content-field practical cells (~50+ new rows, expensive).
- A single `practical_axis_observed_fields: Set[row_id]` cell on a portal-observation envelope that lives outside the 181-row TSV (cheaper, consistent with cell-typed-schema posture).

**Decision point:** when the practical-axis sibling brainstorm spins up — not before.

### Q5 — OS-1 as P1-product-framing residue

`separate_registrations_for_lobbyists_and_clients` (legal, n_rubrics=0, status=firm-but-actually-unvalidated, path-b) is the lone candidate row that exists because Prong 1 was framed as the product. D16's rationale ("a real distinguishing statutory observable") is the "P1 as product" justification verbatim. Under "P1 as scaffolding," it earns its keep only if either (i) the legal-vs-practical gap surfaces as observable on portals, or (ii) a future rubric reads it.

D16 already named the watchpoint: if extraction reveals OS scoring would benefit from inclusion, OS-tabling reverses. **Flag, don't remove.**

---

## Where they actually concur vs. where they're complementary

| Surface | Compendium review | Harness review | Pattern |
|---|---|---|---|
| Ralph loop | C-F1: uneven `Σ` across rubrics | H-F2: no orchestrator drives the loop | **Concur** (two halves of the same problem) |
| Schema / docs | C-F2 status drift; C-F4 row-ID drift; C-F3 content-field gap | — | Compendium-only |
| Code shapes | — | H-F1 EvidenceSpan duplication; H-F3 partial-SMR sentinel | Harness-only |
| P1-product residue | Q5 OS-1 | — | Compendium-only |

The concur is real and thematic on the Ralph-loop theme. The other findings are complementary across surfaces (compendium = schema/docs/projection-mappings; harness = code-module shapes), not duplicative.

---

## Priority order, by what blocks what

1. **H-F1 EvidenceSpan fork.** Blocks `scoring_v2` impl plan — the actively planned next-work-item on this branch. Either 5 minutes of brainstorm or its own session.
2. **H-F3 SMR partiality.** Blocks Phase C correctness against this branch's output; small addition to `models_v2`.
3. **H-F2 orchestrator naming + scheduling.** Doesn't need to be built now, but should be in STATUS + RESEARCH_ARC so it doesn't get rediscovered 2 months from now.
4. **C-F1 per-rubric normalization handoff to `phase-c-projection-tdd`.** Don't let them write projection code without picking this.
5. **C-F2 + C-F4.** Independent cheap wins; ~3 hours combined.
6. **C-F3.** Sits in futures-file until practical-axis spin-up.

---

## Plan structure recommendation (re-thought)

The plan as written ([`plans/20260515_apply_post_framing_review_recommendations_plan.md`](../plans/20260515_apply_post_framing_review_recommendations_plan.md)) bundles 1–6 onto this branch in 6 phases, with brainstorm gates on items 1 and 2. **What I'd do differently:** split into three smaller plans.

- **Plan A (quick wins, autonomous).** C-F2 status fix + C-F4 row-ID tool + H-F2 doc-naming. No design decisions; fire-and-forget on a fresh agent. ~3-4 hours.
- **Plan B (design forks, user-in-loop).** H-F1 EvidenceSpan + H-F3 partiality marker. Brainstorm gates → TDD impl. Lands the design forks before `scoring_v2` impl plan picks them up downstream.
- **Plan C (handoff notes, pure doc).** C-F1 + C-F3 + Q5 OS-1 watchpoint. ~30 min on whichever branches.

Reasons to split: parallel execution (Plan A can fire while you decide Plan B's forks); cleaner provenance per finding; easier to roll back if any one piece goes sideways. Reasons to keep unified: one coherent provenance line, one finish-convo, the framing-link stays intact.

---

## Open decisions waiting on user

1. **Fork 1 (EvidenceSpan):** A / B / C? Plan leans A.
2. **Fork 2 (SMR partiality):** A (`axis_coverage` field) / B (type split)? Plan leans A.
3. **C-F2 (status drift):** TSV regen / doc rewrite? Either is cheap; TSV regen is more discoverable.
4. **Plan structure:** single 6-phase plan / split into Plans A/B/C?
5. **Brainstorm timing for Forks 1 & 2:** in-session before launching fresh agent / surfaced as gates the fresh agent surfaces?

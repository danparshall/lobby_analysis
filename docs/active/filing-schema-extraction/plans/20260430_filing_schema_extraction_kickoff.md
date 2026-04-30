# Filing-Schema-First Extraction Harness — Kickoff Plan

**Status:** Brainstorm-needed (design questions open). This is a kickoff brief, not an implementation-ready TDD spec. The first session on this branch should resolve the open design questions via brainstorming before any code lands.

**Originating conversation:** `docs/historical/statute-retrieval/convos/20260430_oh_2025_baseline_smr.md` — second mid-session reframe ("the WHOLE POINT of this tool is to ACTUALLY EXTRACT the disclosure filings, so we need to know what's required, right?").

**Branch:** `filing-schema-extraction` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/filing-schema-extraction`).

**Calibration anchor:** OH 2025 PRI-projection SMR (`data/state_master_records/OH/2025/e7846593ebb5.json` — gitignored, regenerable from committed score CSV). Diff doc with structural findings: `docs/historical/statute-retrieval/results/20260430_oh_2025_vs_2010_diff.md`.

---

## The gap this plan closes

The OH 2025 PRI-projection SMR has 22 `field_requirements` rows. The compendium has 118 rows total. Of those 118 rows, **57 have no 2025 score data at all** (PRI accessibility + FOCAL-only + Sunlight-only items not separately scored); **another 39 are scored but not projected** (compendium rows where `maps_to_state_master_field` was only populated for the E-series during Stage B.6.1, leaving most of the 61 PRI disclosure-law items projected nowhere). The SMR is genuinely thin.

But that's only the *quantitative* gap. The *qualitative* gap is bigger:

1. **PRI's diagnostic yes/no shape isn't the right product shape for downstream filing extraction.** "Are principals required to disclose their address and phone number?" → 0 or 1 doesn't tell a downstream extractor whether to expect `principal.address` and `principal.phone` columns on the filing, or what types they are, or whether they're required-conditional-on-something.
2. **Qualitative legal gates are invisible** to the rubric structure. §101.70(F)'s "as one of the individual's main purposes" *is* a materiality test; PRI looks for quantitative thresholds and finds nothing, so D0-D2 read as "no materiality test." A real extractor must capture this.
3. **Multi-regime parallel chapters get flattened.** OH has three parallel lobbying regimes (legislative agents in §101.70-79; retirement system in §101.90-99; executive agency in §121.60-69). Each has its own filings, definitions, and exemptions. PRI's rubric doesn't have shape for this — every cell answers "yes for some regime" or "no for all." The SMR must represent each regime's filing schedule separately.
4. **Conjunctive vs disjunctive rubric items get scored disjunctively under prompt drift.** r1 read "address AND phone required" as 1 when only address is required (statute-retrieval session, scorer drift). A field-by-field schema makes the distinction structural, not prompt-engineered.

The **product** for this branch is: each compendium-keyed `field_requirements` row in the SMR is populated with `status`, `legal_availability`, `legal_citation`, `evidence_source`, and `notes` derived **directly from statute text** — for every compendium row that's legally applicable to the state.

---

## What "full compendium-SMR" means

For OH (the MVP target), the compendium has 118 rows. Of those:
- **28 PRI-disclosure-only rows** — must be populated from OH §101.70-79 + §101.90-99 + §121.60-69 directly.
- **21 PRI-disclosure ∪ FOCAL rows** — same, but with FOCAL refs riding along.
- **8 PRI-disclosure ∪ Sunlight rows** — same, with Sunlight refs riding along.
- **4 triple-overlap rows** — same.
- **17 PRI-accessibility rows** — populated from portal-side observation, not statute. **Out of scope for this plan** (accessibility is portal evidence, not statute evidence).
- **32 FOCAL-only rows** — assess: do these correspond to OH disclosure requirements? Some do (OH may require disclosure of items FOCAL covers but PRI doesn't); some don't (OH has no parallel requirement).
- **3 FOCAL ∪ accessibility rows** — accessibility-side, deferred.
- **3 Sunlight-only rows** — atomic facts from Sunlight 2015 methodology paragraph; assess applicability to OH.
- **2 PRI-accessibility ∪ FOCAL rows** — accessibility-side, deferred.

**MVP target for OH (statute-side rows only):** 61 + 32 + 3 = **~96 compendium rows** to assess. Each row resolves to one of:
- **`required` + legal citation + status="known"** — OH law explicitly requires this.
- **`not_required` + status="known"** — OH law explicitly does NOT require this (negative finding, equally valuable).
- **`not_addressed` + status="unknown"** — OH law is silent; we can't infer from statute alone.
- **`required_conditional` + condition + citation** — required when X (e.g., "required when expenditure > aggregate $50/year per member").

**Compare to current PRI-projection SMR for OH (22 rows populated):** the new harness should produce ≥22 populated rows that *match* the PRI-projection result on items where PRI is correct, AND populate the other ~74 statute-side compendium rows with proper findings, AND fix the known PRI-projection errors (D0=1 not 0; conjunctive E-series read correctly).

---

## Design questions (resolve via brainstorming first)

1. **Subagent architecture.** One agent reads the whole bundle and emits the full schema in one pass? Or per-section agents that each emit the obligations from one section, then a unifier? The Stage B harness used one-agent-per-rubric (one agent scored all 61 PRI items at once); the agent had to hold the whole 30-section bundle + all 61 questions + the locked prompt in context. For full schema extraction with ~96 compendium rows, that's much heavier. Per-section is more scalable but loses cross-reference context (e.g., §101.74's expenditure rules reference §101.70's definitions).
2. **Prompt shape.** What does the agent's brief look like? It needs: (a) the compendium rows to populate (with `field_path`, `data_type`, `description` for each row); (b) the bundled statute text; (c) instructions to emit each row's `status`, `legal_availability`, `legal_citation`, `evidence_source`, `notes`. The PRI scorer prompt's three-tier exemption boundary, files-read enforcement, and locked rules are reusable scaffolding.
3. **Multi-regime representation in the SMR.** OH has three parallel lobbying regimes. The current SMR has 11 `registration_requirements` rows and 2 `reporting_parties` rows (lobbyist + client). Does the new schema represent each regime separately (3 × 2 = 6 reporting-party rows) or unified (the existing flat shape, with regime as a `notes` qualifier)? **Strong opinion: keep flat shape for now; document multi-regime in `notes` per row;** revisit if Track B's extraction pipeline needs structural multi-regime.
4. **What is "evidence" for a `not_required` finding?** Negative findings are harder than positive ones — the agent must show it considered whether OH law requires X and didn't find it, vs missing the requirement entirely. Possible approach: require the agent to cite the *most relevant* statute section even for `not_required`, with `evidence_source.evidence_type="statute_silence"` and `evidence_notes="searched §101.72 (registration content), §101.73 (expenditure statement), §101.74 (financial transaction statement); none require X."`
5. **How do we calibrate?** The OH 2025 PRI-projection SMR is the *floor* — the new harness must match its 22 populated rows on agreement items. But it must also *correct* the known errors (D0=1 not 0; conjunctive items). Calibration approach: produce the new SMR; diff against PRI-projection SMR; for each diff, classify as "harness right, PRI wrong" / "harness wrong, PRI right" / "judgment call." Report agreement rate + categorized differences.
6. **What about FOCAL-only and Sunlight-only compendium rows?** PRI didn't ask about these, so the PRI-projection SMR is silent on them. The new harness must reach a finding on each. Some will be `not_addressed` (OH statute silent); others will be real obligations PRI's rubric just didn't cover.
7. **Data source for `MatrixCell`.** The N×50×2 matrix (Required × Legally Available × Practically Available) is downstream of populated SMRs. This plan doesn't build the MatrixCell projection layer — that's separate. But the SMR shape this plan produces is the input to that layer. **Make sure `legal_availability` is set on every populated row** so the matrix layer has data to project.

---

## Out of scope (deliberate)

- **Accessibility-side compendium rows** (PRI accessibility + FOCAL/Sunlight accessibility-tagged items). Those depend on portal observation, not statute reading; defer to a portal-evidence harness on a separate branch.
- **The N×50×2 `MatrixCell` projection layer.** Stage C of the parent compendium plan. Defer.
- **CA / TX / other states.** OH first. After OH passes calibration, template to other priority states as separate sessions on this branch.
- **All 50 states.** The README scopes to 5–8 priority states. Don't try to scale to 50 here.
- **Multi-vintage scoring.** OH 2025 first. OH 2010 already exists as comparison anchor. Other vintages later.
- **Replacing the data-model-v1.1 schema.** The compendium-keyed `field_requirements` shape is correct; this plan populates it from a new data source, not redesigns it.
- **Disclosure-data pulling.** Other fellow's branch (`oh-portal-extraction` per origin/2026-04-30 sighting). This branch is statute-side only; the SMR this branch produces is a contract for that branch.

---

## Suggested first-session work

A brainstorming session that resolves design questions 1, 2, 3, 4 above. Don't write any code in the first session — the design choices are load-bearing and a wrong subagent architecture or prompt shape will cost weeks. The brainstorming skill is the right framework. Specific questions to land before any implementation:

- One agent vs per-section agents?
- Brief shape: how do we present 96 compendium rows + 30-section bundle + extraction instructions in one prompt without the agent dropping rows?
- What's the minimum viable schema for a compendium row's "filled" state? `status` + `legal_citation` is the floor. Are `evidence_source` + `data_type` overrides necessary at MVP?
- How do we handle compendium rows where the *concept* doesn't fit OH's statute structure (e.g., a FOCAL indicator about a database feature that's portal-side, not statute-side)?

Once design questions are resolved, the second session writes a TDD-ready implementation plan and begins.

---

## Confidence

- **High** that the compendium-keyed SMR shape is the right long-term target. (User-confirmed twice on the parent branch.)
- **High** that the OH 2025 PRI-projection SMR is the right calibration anchor. (Built end-to-end; diff doc shipped.)
- **Medium** on whether one-pass extraction will scale to ~96 rows × 30 sections in a single agent context. May need to chunk.
- **Medium** on whether negative findings (`not_required` + `statute_silence` evidence) are reliably distinguishable from missed positives. The brainstorming session must address this.
- **Lower** on whether FOCAL-only compendium rows can all be resolved against OH statute alone. Some FOCAL indicators are about portal features that have no statutory mandate — those will resolve to `not_addressed` from a statute-only harness, even if the disclosure feature exists in practice.

---

## Pre-flight reads for the implementing agent

1. `STATUS.md` — current focus and active branches.
2. `README.md` — what this repo is.
3. `docs/historical/statute-retrieval/RESEARCH_LOG.md` — full trajectory of the parent branch; especially the 2026-04-30 entry on the PRI-projection MVP.
4. `docs/historical/statute-retrieval/convos/20260430_oh_2025_baseline_smr.md` — originating convo for this plan; both reframes.
5. `docs/historical/statute-retrieval/results/20260430_oh_2025_vs_2010_diff.md` — calibration anchor + scorer-drift signals + statute-text change summary.
6. `docs/historical/statute-retrieval/plans/20260429_multi_rubric_extraction_harness.md` — the parent harness plan; this branch is its Phase 3 ("extraction-first refactor — brainstorm-needed") materialized.
7. `src/lobby_analysis/models/compendium.py` — `CompendiumItem` schema.
8. `src/lobby_analysis/models/state_master.py` — `StateMasterRecord` + `FieldRequirement` schema.
9. `src/scoring/scorer_prompt.md` — current locked PRI scorer prompt (reusable scaffolding for the new harness).
10. `data/compendium/disclosure_items.csv` — the 118-row populated compendium.
11. `data/statutes/OH/2025/sections/` — the 30-section OH 2025 bundle (gitignored; regenerable via `retrieve-statutes --state OH --vintage 2025`).

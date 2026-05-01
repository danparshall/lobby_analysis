# Research Log: statute-extraction

Created: 2026-05-01
Purpose: Build the filing-schema extraction harness that reads state statute text directly into compendium-keyed `field_requirements` rows on the `StateMasterRecord`. The compendium is the universe; the SMR is keyed to the compendium; framework rubrics (PRI, FOCAL, Sunlight, Newmark, Opheim, CPI, OpenSecrets) are projections from a populated SMR, not data sources for it.

Successor to the just-merged `filing-schema-extraction` branch (v2 audit + v1.2 schema bump landed in PR #5). This branch turns the locked 108-row statute-side compendium into a populated SMR for OH 2025 first, then templates to other priority states.

Carry-forward signals from prior branches (informational, not gates):
- Two scorer blind spots flagged at the end of `statute-retrieval`: qualitative materiality (e.g., OH §101.70(F) "main purposes" test) was structurally invisible to a quantitative-threshold rubric scorer; conjunctive multi-field rubric items got collapsed to disjunctive under prompt drift. The harness must capture both correctly.
- A prior MVP shipped at `docs/historical/statute-retrieval/results/20260430_oh_2025_vs_2010_diff.md` produced 22 populated rows in a 22-row PRI-shape; that artifact exists for diff comparison but is not a target.

---

## Sessions

(Newest first.)

### 2026-05-01 (pm) — Phases 0–3 implemented + iter-1 dispatched (3 runs) + iter-2 prep

**Convo:** [`convos/20260501_pm_phases_0_3_iter1_dispatch.md`](convos/20260501_pm_phases_0_3_iter1_dispatch.md)
**Plan executed:** [`plans/20260501_statute_extraction_harness.md`](plans/20260501_statute_extraction_harness.md)
**Iter-1 analysis doc:** [`results/iter-1_analysis.md`](results/iter-1_analysis.md)
**Audit handoff brief:** [`plans/_handoffs/20260501_compendium_item_audit_handoff.md`](plans/_handoffs/20260501_compendium_item_audit_handoff.md)

#### Topics Explored
- TDD-driven build of all four phases of the kickoff plan: v1.3 schema bump, v2 scorer prompt + extraction_brief module, ExtractionRunMetadata + sha helpers, orchestrator extract-prepare/finalize subcommands.
- Iter-1 dispatch: 3 temp-0 claude-opus-4-7 subagent runs against OH 2025 `definitions` chunk via the new harness.
- Mid-run scaffolding fix: prompt/validation tension on `not_addressed` rows surfaced by r1 was resolved by tightening v2 Rule 1 (explicit not_addressed exception) and loosening finalize (permits null citation when status is not_addressed and evidence_notes non-empty).

#### Provisional Findings
- **14/15 = 93.3% inter-run status agreement** at temp-0 across the 15 emitted tuples (3 regimes × 4 regime-specific rows + 3 regime-uniform rows). The single disagreement is on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system` and is interpretive (definitional cross-application of "administrative agency" to the retirement-system regime), not a noise-driven scoring flip.
- **Regime expansion is unanimous and correct.** All 3 runs identified OH's three lobbying regimes (`legislative` / `executive` / `retirement_system`) and produced identical (compendium_row_id, regime, role) tuples. The Q4 "regime-aware-from-day-one" decision is empirically validated.
- **Bundle inlining eliminated dispatch variance** as predicted. No tool-call variance was observed; the prior architecture's 4–43 tool-call dispatch noise is structurally gone.
- **Atomic per-row holds.** No conjunctive→disjunctive collapse observed; 7 distinct rows produced 15 distinct records without merging.
- **Materiality-gate canary works.** All 3 runs correctly captured §101.70(F) etc. as `required_conditional` with `condition_text` populated across all three regimes, and detected textual variation between legislative ("during at least a portion of the individual's time...") and executive/retirement ("on a regular and substantial basis") — fidelity prior PRI projection couldn't see.
- **OH has no quantitative inclusion thresholds** (compensation/expenditure/time standards all `not_addressed` unanimously) — confirms prior project's qualitative-gate-only finding.

#### Decisions
- **Q6 (multi-run agreement) settles to ≥3 temp-0 runs** at iter-1 evidence; bumping to 5 wouldn't resolve interpretive disagreement. The 3-model consensus oracle (or per-row scope tightening) is the right escalation path for interpretive cases, not more same-model runs.
- **Validation: legal_citation is required for required/not_required/required_conditional, optional+evidence_notes-required for not_addressed.** Codified in commit `0ac7800` after r1 surfaced the prompt/validation tension.

#### Iter-2 prep (later in same session)

After cross-examining the `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system` disagreement: the row name reads as actor-axis to a careful human even though the description is target-axis (anchored on Hired Guns Q1's "executive branch lobbyists"). The framework_references that pin the axis weren't visible to the agent. Three iter-2 prep artifacts shipped:

- **Tightened 7 `definitions` row descriptions** to lead with explicit axis labels (`TARGET axis.` / `ACTOR axis.` / `THRESHOLD axis (quantitative, inclusion-framed).` / `THRESHOLD axis (qualitative).`) plus cross-references to adjacent rows on different axes.
- **`src/scoring/chunk_frames/definitions.md`** — per-chunk preamble naming the three axes the rows decompose, mapping each to its rows, calling out the FDA-as-actor case as out-of-chunk (lives in `REG_GOVT_LOBBYING_GOVT` / `REG_EXECUTIVE_AGENCY` in the registration domain). Wired into `extraction_brief._render_suffix()` as auto-inlined `chunk_frames/<chunk>.md`; absent files are no-ops, so the wiring is generic for future chunks.
- **Audit handoff brief** at `plans/_handoffs/20260501_compendium_item_audit_handoff.md`. Defines the work for a future agent that will write the v3 compendium-curation audit plan (axis explicitness + name clarity + description fidelity + framework-reference cohesion across all 141 rows; possible v1.4 schema bump for an explicit `axis` field).

Tests: 1 new (`test_extraction_brief_includes_chunk_frame_when_present`); full suite 337/337 green.

#### Commits (this session)
- `44fc762` — v1.3 FieldRequirement schema bump (Phase 0).
- `d8e5187` — v2 scorer prompt + extraction_brief module (Phase 1).
- `c398020` — CLAUDE.md: worktree pytest gotcha (paper-trail; user later verified the gotcha appears resolved in current uv).
- `878133a` — provenance v1.3: ExtractionRunMetadata + sha helpers (Phase 2).
- `a703566` — orchestrator: extract-prepare-run + extract-finalize-run (Phase 3).
- `0ac7800` — extract-finalize: allow null legal_citation for not_addressed rows.
- `67ccb4b` — iter-1 dispatch (3 runs) + analysis doc.
- `2d32c39` — iter-2 prep: definitions chunk frame + tightened row descriptions + audit handoff.

#### Next Steps
**Iter-2 dispatch** — re-run 3 temp-0 subagents on OH 2025 `definitions` with the new chunk frame + tightened descriptions in the brief. Hypothesis: the disagreement on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system` collapses to 3-way `not_required` consensus (r1's reading was right; the preamble + tightened description should pull r2 and r3 toward it). If yes, the per-chunk-preamble approach is validated and gets applied to other chunks. If no, the disagreement is deeper than name/description ambiguity (possibly genuine cross-regime definitional ambiguity in OH statute itself), and iter-3 escalates to a 3-model consensus oracle.

**v3 compendium audit** — the audit handoff brief is ready for a fresh-context agent to develop into a plan. Independent of iter-2; can run in parallel.

### 2026-05-01 — kickoff: harness brainstorming (closed)

**Convo:** [`convos/20260501_harness_brainstorm_kickoff.md`](convos/20260501_harness_brainstorm_kickoff.md)
**Plan produced:** [`plans/20260501_statute_extraction_harness.md`](plans/20260501_statute_extraction_harness.md)

#### Topics Explored
- 7 design questions from the predecessor's kickoff plan (architecture / qualitative materiality / disjunctive drift / multi-regime / MVP gate / multi-run / scaling).
- Single-prompt vs chunked extraction; measured token costs; bundle-as-system-prompt inlining vs Read-tool fetching.
- Existing harness review (`src/scoring/`) — what carries forward, what needs v2 rewrites, what's new.
- Provenance / reproducibility as a first-class requirement.
- Per-iteration analysis-doc template.
- Two reframings: PRI-de-privileging (forward-looking framings rewritten); compendium relocated to repo root.

#### Provisional Findings
- Prior MVP failure modes (dispatch variance, exemption-layer under-reading, conjunctive collapse, qualitative-materiality drops, 21.3% inter-run disagreement) all trace to model-chosen reading. Bundle inlining should remove the dispatch source structurally — verify in iter-1.
- 8 of 50 states have unambiguous statutory multi-regime structures (OH/FL/CA/NY/NJ/IL/NC/MA); regime-aware schema is warranted from day one.
- Compendium curation is mature (141 rows, 9-rubric union, locked Decision Log D1–D11) — stable contract for the harness.

#### Results
- [`results/state_regime_splitting.md`](results/state_regime_splitting.md) — regime survey from an external web-UX research agent; drove the Q4 flip.

#### Decisions
- 4 chunks by domain (reporting / registration / contact_log / other) with bundle inlined as cached prefix.
- v1.3 `FieldRequirement` adds `condition_text` + `regime` + `registrant_role` (all `str | None`, additive).
- Iter-1 = `definitions` chunk only on OH 2025; iteration loop with user OK as the gate.
- 3 temp-0 runs per chunk; measure variance; 3-model consensus oracle as fallback.
- Provenance: per-run `brief_suffix.md` + `meta.json` with shas + iteration_label + prior_run_id + changes_from_prior.
- Skeleton refactor: `data/compendium/` → `compendium/` (commit `5537c92`).
- All PRI-as-anchor framings removed from forward-looking docs; predecessor branch archived.

#### Commits
- `5537c92` — relocate `compendium/` to repo root (skeleton refactor).
- `453c7fb` — reframe STATUS + seed branch docs.
- `b223048` — log brainstorm Q1–Q7 + bundle-inlining + provenance decisions.
- `2911dcd` — import regime-survey result + lock Q4 regime-aware schema.
- `96b341e` — log per-iteration analysis-doc template.

#### Next Steps
Implement the iter-1 plan. Order: v1.3 schema bump → v2 scorer prompt + brief builder → provenance extension → orchestrator subcommands → 3 manual dispatches on OH 2025 `definitions` chunk → first analysis doc. Implementing agent follows the Nori workflow with TDD discipline.

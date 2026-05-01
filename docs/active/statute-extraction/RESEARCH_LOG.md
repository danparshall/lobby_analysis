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

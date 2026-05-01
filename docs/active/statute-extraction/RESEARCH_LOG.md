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

### 2026-05-01 — kickoff: harness brainstorming
- **Convo:** [`convos/20260501_harness_brainstorm_kickoff.md`](convos/20260501_harness_brainstorm_kickoff.md) (in progress)
- **Plan produced:** TBD (pending brainstorm outcome)
- **First commit on branch:** `5537c92` — relocate `compendium/` from `data/compendium/` to repo root (skeleton refactor). Locked curation data belongs alongside `papers/` as top-level reference data, not under gitignored `data/`.
- **Result imported:** [`results/state_regime_splitting.md`](results/state_regime_splitting.md) — survey of which states have multiple statutory disclosure regimes (legislative / executive / retirement / procurement / placement-agent / liaison / pay-to-play). Produced by a web-UX research agent. **Headline:** 8 states with unambiguous statutory regime splits (OH, FL, CA, NY, NJ, IL, NC, MA) + 2–4 borderline. Drove Q4 lock to regime-aware-from-day-one and the v1.3 schema additions (`regime`, `registrant_role`, `condition_text` on `FieldRequirement`).

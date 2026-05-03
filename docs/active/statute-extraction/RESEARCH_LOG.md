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

### 2026-05-02 (pm) — Phase 0 audit executed → rebuild pivot, harness paused

**Convo:** captured on the new `compendium-source-extracts` branch at [`docs/active/compendium-source-extracts/convos/20260502_pm_compendium_rebuild_pivot.md`](../../compendium-source-extracts/convos/20260502_pm_compendium_rebuild_pivot.md).
**Audit results (this branch):** [`results/20260502_compendium_audit_concerns.md`](results/20260502_compendium_audit_concerns.md) (canonical) + [`.csv`](results/20260502_compendium_audit_concerns.csv), [`results/20260502_compendium_audit_concerns_run1.{md,csv}`](results/), [`_run2.{md,csv}`](results/), [`results/20260502_compendium_audit_reconciliation.md`](results/20260502_compendium_audit_reconciliation.md).
**Plan superseded:** [`plans/20260502_compendium_item_audit_v3_phase0.md`](plans/20260502_compendium_item_audit_v3_phase0.md) — Phase 0 deliverable shipped; Phase 1/2 superseded by `compendium-source-extracts`.

#### Topics Explored

- Phase 0 audit execution: dispatched two parallel general-purpose auditor subagents against the locked plan. Each ran the per-run 8-step sequence (pre-flight reads → load source data → C1+C5 first pass → C2+C3 second pass → C4 third pass → aggregate → notable patterns → output). Reconciliation step (third subagent) produced the canonical concerns doc + reconciliation note.
- Walk-through of tag-disagreements with the user. Three clusters examined: `RPT_*_NON_COMPENSATION × C2` (broader vs narrower opposite-direction calls — symptom of cluster heterogeneity, real tag is C3); `DEF_PUBLIC_ENTITY` family + `EXEMPT_GOVT_OFFICIAL_CAPACITY × C1` (axis-ambiguous-name vs name-misleading — both wrong tag, rows aren't axis-typed; real concern is C5 wrong-domain on the DEF family, no flag warranted on EXEMPT_GOVT); `DEF_ADMIN_AGENCY × C2` (rubric-source-ambiguous vs description-broader-than-rubric — both correct, capturing different concerns; retain both).
- Recognition of structural PRI privilege: 4-row `DEF_PUBLIC_ENTITY` family (PRI Q-C parent + 3 sub-criteria), 12-row `FREQ_*` (PRI E1h/E2h enumeration), 11-row `REG_*-A-series` (PRI A1–A11), 8-row `RPT_*_NON_COMPENSATION/OTHER_COSTS/etc.` (PRI E1f i/ii/iii/iv split × 2 sides), and a literal `?.` formatting artifact on ~24 rows (mechanical evidence of script-translated PRI rubric text). The compendium's *atomization* is PRI's, not just its vocabulary.
- Pivot: rebuild the compendium from non-PRI source papers on a new branch.

#### Provisional Findings

- **Phase 0 audit results:** 186 canonical concerns / 109 of 141 rows flagged / 24.2% inter-auditor agreement. Three "surprising-result" thresholds tripped: structural drift (>35%), fuzzy tag boundaries (<60% agreement), cross-row-overlap clusters of 3+ rows. Headline pattern: PRI-verbatim descriptions are the dominant C2 driver (~40% of concerns).
- **Audit's role inverted mid-session:** from "input to Phase 1 fix-design" to "evidence the compendium needs structural rebuilding." Phase 1 and Phase 2 of the v3 audit are superseded; the canonical concerns doc + reconciliation note remain as historical artifacts only.
- **Compendium 1.x is unsalvageable as a foundation.** Patches to row names, descriptions, or domain assignments leave the structural PRI-shape intact. D9's vocabulary fix was necessary but not sufficient.

#### Decisions

| topic | decision |
|---|---|
| Phase 1/2 of v3 audit | **Superseded.** Plan footer added pointing at `compendium-source-extracts` |
| Phase 0 audit results | **Retained as historical evidence**, not a fix-list |
| Harness work on this branch (iter-2 onward) | **Paused** until compendium-2.0 lands |
| New branch | `compendium-source-extracts` off `origin/main` (already created and pushed) |
| PRI 2010 status | **Fully excluded** project-wide. Top-of-file `⛔ AGENT-CRITICAL` block added to STATUS.md on this branch as well as on `compendium-source-extracts` |
| Auto-memory `feedback_pri_not_privileged.md` | Updated to extend the rule from vocabulary to structure (handled in this session) |

#### Commits this session

- `0f33d34` (compendium-source-extracts) — Branch creation: per-paper rebuild, no PRI
- This branch's commit — Phase 0 audit results + RESEARCH_LOG + Phase 0 plan supersession + STATUS.md PRI bar

#### Next Steps

- All harness work on this branch is paused. Do not iterate iter-2 / iter-3 / etc.
- Future work resumes only after compendium-2.0 lands on `compendium-source-extracts` and the user explicitly clears the PRI bar.

### 2026-05-02 — Compendium Audit v3 brainstorm + Phase 0 plan

**Convo:** [`convos/20260502_compendium_audit_v3_brainstorm.md`](convos/20260502_compendium_audit_v3_brainstorm.md)
**Plan produced:** [`plans/20260502_compendium_item_audit_v3_phase0.md`](plans/20260502_compendium_item_audit_v3_phase0.md)
**Spawning artifact:** [`plans/_handoffs/20260501_compendium_item_audit_handoff.md`](plans/_handoffs/20260501_compendium_item_audit_handoff.md)

#### Topics Explored

- Whether the iter-1-surfaced curation gap (`DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` axis ambiguity) justifies a 141-row sweep — pressure-tested the handoff thesis that compendium-side disambiguation must be authoritative because consistent-but-wrong rows give no inter-run-disagreement signal.
- Schema-axis-field tradeoff (Option 1 v1.4 schema bump vs Option 2 descriptions+rename vs Option 3 free-form `tags` field). Rejected Option 1 because axis taxonomy is per-domain not global; Option 3 defers the decision rather than makes it.
- Axis-in-ID convention: `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` (e.g., `DEF_LOBBYING_TARGET_ADMIN_AGENCIES`) as user-proposed refinement of Option 2 — gives most of Option 1's machine-readability without the schema bump.
- Audit sequencing: per-domain (smallest first, `definitions` as canary) vs full-sweep first. Chose full-sweep so cross-domain patterns inform per-domain axis vocabulary harmonization rather than locking `definitions`'s axes prematurely.
- Three-phase decoupling (P0 concerns sweep → P1 solution design → P2 apply fixes in batches). Separates concern-finding from solution-design as distinct cognitive tasks.
- Concerns-doc tag taxonomy: 8 starting-point tags including `other-issue` escape hatch. Severity field considered then dropped — Phase 1's grouping pass produces cluster-level prioritization signal naturally.
- One-plan vs staged-plan flow. Chose staged: ship Phase 0 plan only this session; Phase 1's plan written *after* concerns doc lands so its design is informed by Phase 0's findings.

#### Provisional Findings

- The latent-axis-bug rate is unknown (iter-1 evidence is N=1 by accident). Phase 0's full sweep is itself the population estimate; the audit is cheap enough that doing it tells us more than guessing.
- Axis vocabulary is genuinely per-domain — `definitions` uses {target, actor, threshold (quant + qual)}; `reporting`, `contact_log`, etc. will use different sets. A global axis enum would be lossy or incoherent; per-domain natural-language vocabularies (in chunk-frame preambles + IDs) are the right structure.
- Rename cascade per fix is non-trivial (tests + dedup-map + prior run dirs + chunk-frame preambles + `.py` source). Phase 1 must include cascade-cost methodology so Phase 2's batching is informed.
- The v2 audit's Decision Log (D1–D11 in `docs/COMPENDIUM_AUDIT.md`) is the procedural template — v3 continues numbering at D12+ (in Phase 1, not Phase 0).

#### Decisions

| topic | decision |
|---|---|
| Strategy | Option 2: descriptions + axis-in-ID renames; **no schema-axis-field**. Future evidence may reopen as v1.5 if needed |
| ID convention | `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` where axis applies; absence permitted for axis-less rows |
| Audit flow | Three phases: P0 concerns sweep (full 141 rows) → P1 solution design → P2 apply fixes in batches |
| Sweep scope | Full 141 rows up front; cross-domain patterns inform per-domain axis vocabulary harmonization |
| Plan staging | Ship P0 plan only this session; P1 plan written after concerns doc exists; P0 plan has "Follow-up stages" footer |
| Concerns-doc tags | 8 starting-point tags including `other-issue` escape hatch; severity field dropped |
| Confidence field | Concerns table includes `confidence: high\|medium\|low` per concern (resolved at plan-acceptance) |
| Spot-check | Folded into P0 (full sweep is the spot-check at scale); no separate 5–10-row deliverable |
| Schema recommendation | Standing answer: Option 2 stands; v3 doesn't reopen unless P0 surfaces evidence-of-need |
| Phase 0 execution | Hand off to a fresh agent for context-budget + plan-as-contract + independence reasons |

#### Next Steps

Spawn a fresh general-purpose agent against the Phase 0 plan to execute the 141-row concerns sweep. Output: `results/20260502_compendium_audit_concerns.md` (or sweep-date filename if execution slips). Once that lands, write the Phase 1 plan (solution design) informed by what the concerns doc actually shows. Phase 0 execution is independent of the iter-2/iter-3 harness work — both can proceed in parallel, since Phase 0 only reads the compendium.

### 2026-05-01 (eve → 05-02) — Issue #6: post-laptop-crash data restoration

**Convo:** [`convos/20260501_eve_issue6_data_restoration.md`](convos/20260501_eve_issue6_data_restoration.md)
**Issue:** [#6](https://github.com/danparshall/lobby_analysis/issues/6) — Rerun Justia statute pull + portal snapshots after laptop data loss
**Result doc:** [`results/20260501_state_portal_drift.md`](results/20260501_state_portal_drift.md)

#### Topics Explored
- Inventory of what survived the pre-2026-04-30 laptop drive crash: `data/statutes/{CA/2010, TX/2009, OH/2010, OH/2025}` intact; `data/portal_snapshots/`, `data/portal_urls/`, NY/WI/WY statutes lost.
- Stage 1 vs Stage 2 design: keep URL discovery as one-shot subagent work, replace the historical 50-parallel `curl` subagents (which produced a permissions storm) with a single deterministic Python script.
- Permission patterns: empirically verified that `unset VIRTUAL_ENV` is no longer needed in the worktree — uv warns and ignores mismatched VIRTUAL_ENV; updated CLAUDE.md gotcha section accordingly.
- Statute SSOT framing correction: my initial framing claimed "Justia is the statute SSOT" — pushback established that Justia is the project's *operational* SSOT (stable per-vintage URLs, programmatic), not the canonical authority (each state's own legislative codification).

#### Provisional Findings
- 3 missing statutes (NY/WI/WY) fetched cleanly via the existing `retrieve-statutes` orchestrator — no infra changes needed.
- 8 of 50 states cover the README's "5–8 priority" scope (CA + CO/NY/WA/TX/WI/IL/FL); all 8 captured at 2026-05-01, ~144 MB total disk.
- 18-day Stage 1 re-discovery surfaced substantive drift in 5 of 8 portals (CA: CARS rollout date; CO: hostname shift; NY: JCOPE → COELIG transition; WA: RCW recodification to Title 29B; TX: bulk ZIP migration). See `results/20260501_state_portal_drift.md`.
- IL's WAF posture (every `ilsos.gov` host blocks WebFetch) appears unchanged from the historical pass — Stage 2 reproduces the partial-capture state without Playwright.
- The `compendium/portal_urls/<ABBR>.json` files are now committed at the repo-root locked-contract location (alongside the compendium CSVs), not the gitignored `data/portal_urls/` location of the original — so the next laptop crash can't take them out.

#### Decisions
- Stage 2 implementation: deterministic Python script (`src/scoring/portal_snapshot.py`) + `cmd_capture_snapshots` orchestrator subcommand.
- Stage 1 dispatch: one foreground subagent at a time (sequential), not parallel.
- Body cap: 100 MB streaming cap per artifact (matches historical pragmatic behavior on CA's 650 MB CalAccess ZIP).
- `statute`-role URLs: record metadata, skip body fetch — Justia is the operational SSOT for content; the state's own statute hosting is portal-accessibility metadata, not content.
- `SNAPSHOT_DATE_DEFAULT` bumped 2026-04-13 → 2026-05-01.
- Scope cap: 8 priority states this session; remaining 42 are deferred (script + orchestrator handle scale-out without further architectural work).

#### Commits (this session)
- `6673d99` — portal-snapshot Stage 2 script + CA capture (initial CA Stage 1 + manifest, `SNAPSHOT_DATE_DEFAULT` bump, worktree gotcha doc fix, 8 unit tests).
- `d9be039` — Stage 1 JSONs for 7 priority states (CO/NY/WA/TX/WI/IL/FL) + statute-role body skip + framing docstring on `lobbying_statute_urls.py`.

Tests: 337/337 green throughout. The 3 previously failing `tests/test_pipeline.py` tests are unblocked by the fresh CA snapshot.

#### Next Steps
- **GH issue #6 status:** infrastructure restored; 8 of 50 states captured. Open question: close the issue (priority-state coverage achieved) or leave open with a comment noting the remaining 42 states as deferred work.
- The other 42 states are "more of the same" — script and dispatch loop work, no architectural blockers.
- WI's SSRS endpoints, FL's SPA-shell stubs, IL's WAF-blocked apps remain structural gaps that would need a Playwright Stage 3 pass (out of scope for this session).
- FL's `dl_data.cfm` timestamps frozen at 12/31/2014 needs a HEAD-check follow-up (flagged in FL.json observations).

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

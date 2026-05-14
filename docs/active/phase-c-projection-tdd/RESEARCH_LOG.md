# Research Log: phase-c-projection-tdd

Created: 2026-05-14
Purpose: Phase C successor branch (per Option B locked 2026-05-13). TDD-implements per-rubric projection functions `f_rubric(compendium_cells_for_state_year) → rubric_score` in the **locked rubric order**:

1. **CPI 2015 C11** (smallest concrete target; 21 rows in v2 mapping; 14 atomic items from `PublicI/state-integrity-data/2015/criteria.xlsx`)
2. **PRI 2010** (69 rows in v2 mapping; ~52 NEW vs v1.2; sub-aggregate rollup rule already paper-derived in archived `pri-calibration`)
3. **Sunlight 2015** (13 rows in v2 mapping; 11 cross-rubric; three locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation)
4. **Newmark 2017** (14 rows; 8 reused, 6 new; load-bearing r=0.04 CPI↔PRI-disclosure correlation factually-audited 2026-05-13)
5. **Newmark 2005** (14 rows; **100% reuse** of Newmark 2017 mappings; 2005 mapping falsified the 2017 mapping's `contributions_from_others` parallel speculation)
6. **Opheim 1991** (14 row families / 15 in-scope items; **100% reuse**; β AND-projection 2nd concrete use; 1 catch-all un-projectable)
7. **HG 2007** (38 rows; 16 reused, 22 new; 42% reuse; ground-truth retrieval is a `oh-statute-retrieval` sub-task — depend on its output)
8. **FOCAL 2024** (58 rows post-FOCAL-1 / 22 reused, 36 new; 37.9% reuse — lowest single-mapping rate; **L-N 2025 Suppl File 1 weights** — 1,372-cell ground truth; US LDA 81/182 = 45%)

**LobbyView 2018/2025 is NOT in scope for Phase C** — it's a schema-coverage check (Federal_US LDA disclosure-observable coverage 14/18 = 78%), not a score-projection. Already documented as Phase B mapping #9; no projection function to implement.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows. Promoted from `docs/historical/...` to repo-level `compendium/` on 2026-05-14 by the `compendium-v2-promote` branch (live contract for the two parallel-running successors; v1 artifacts retained at `compendium/_deprecated/v1/`). Load via `from lobby_analysis.compendium_loader import load_v2_compendium` (returns raw `list[dict[str, str]]`). Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). (Path is live on main after `compendium-v2-promote` merges; until then read via the worktree-local view.)
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #4 (per-rubric projections as sanity checks on extraction accuracy).
>
> **Per-rubric projection mapping docs (Phase B output):** [`docs/historical/compendium-source-extracts/results/projections/`](../../historical/compendium-source-extracts/results/projections/) — one `<rubric>_projection_mapping.md` per rubric documents the column-by-column projection logic. Each TDD session can use the matching projection-mapping doc as its spec.
>
> **Factual-audit verdict (2026-05-13, pre-merge):** Newmark 2017's r=0.04 CPI↔PRI-disclosure correlation (load-bearing for unification rationale) verified exactly at paper p.421-422. PRI 2010's dense numerical claims (sub-component max counts A:11 + B:4 + C:1 + D:1 + E:20 = 37; B1/B2 reverse-scoring per footnotes 85/86; E rubric "higher of E1/E2 + F/G double-count + separate J") all confirmed exactly. FOCAL had 1 correction landed (contact-log 13/15 restored) + 1 clarity tightening (openness 11/15 vs open-data sub-theme 9/15). **Phase C agents can trust the projection-arithmetic values in these summaries.** One outstanding sourcing nit on Newmark 2017's parenthetical "0.71" comparator: it's sourced from Newmark 2005 (separate paper), not the 2017 PDF — extract from `papers/text/Newmark_2005__lobbying_regulation_in_the_states.txt` if needed.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A; Phase C HG 2007 projection depends on Track A's ground-truth retrieval sub-task).
- Designing the extraction harness — that lives on `extraction-harness-brainstorm` (Track B). Phase C projections operate on hypothetically-correct `compendium_cells`; the extraction pipeline that populates those cells is Track B's concern.
- LobbyView score-projection — LobbyView is schema-coverage only.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. Projection functions are pure code over compendium-keyed cells + tracked rubric ground-truth CSVs — likely no gitignored data needed at all for this branch.

---

## Sessions

(Newest first.)

### 2026-05-14 — Rubric plans drafting (meta-session, sub-0 of 5): playbook gap audit + data-year audit

Convo: [`convos/20260514_rubric_plans_drafting.md`](convos/20260514_rubric_plans_drafting.md)
Results:
- [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) — playbook vs reality for the 6 remaining rubrics
- [`results/20260514_rubric_data_years.md`](results/20260514_rubric_data_years.md) — publication-year vs data-year per rubric (12 distinct vintages across the 8 rubrics)

**Topics explored**

- **Meta-question:** can the 6 remaining rubrics (Sunlight, Newmark 2017/2005, Opheim, HG 2007, FOCAL 2024) be parallelized for headless API-key-billed implementation? Motivation: user wants to bill API key (work-project budget) instead of Claude Code subscription. Original framing was "pure parallelism via API."
- **Reframe chain:** Pure parallelism fights inter-rubric dependencies. Counter: 3 streams (Sunlight→Opheim; Newmark 2017→2005; FOCAL), HG held on `oh-statute-retrieval` Track A. Counter to counter: 2 retrieval blockers for HG, not 1 (CPI scorecard + Track A). Settled: 5 sub-sessions structure with plans drafted in this branch's worktree, headless launches via `claude -p` with API-key auth in later sub-sessions.
- **Playbook gap audit (sub-0 main work).** Read intro + scope + aggregation + validation + Open Issues of all 5 remaining spec docs (Newmark 2017, Newmark 2005, Opheim 1991, HG 2007, FOCAL 2024); also re-read Sunlight 2015 in full as sanity-check on whether playbook is faithful.
- **Data-year audit (user interjection mid-session).** Grepped `papers/text/` for each rubric to identify publication-year vs data-year — critical because extraction needs to fetch correct statute vintage from Justia. Found 12 distinct statute vintages spanning 1988-89 → 2025.

**Provisional findings — 5 cross-cutting meta-patterns the playbook missed**

1. **"Disclosure-only Phase B" scope qualifier applies to every remaining rubric** (5 prohib in Newmark 2017; 5 prohib+penalty in Newmark 2005; 8 enforce+catch-all in Opheim; 10 enforce+cooling-off in HG; 1 revolving_door.2 in FOCAL post-FOCAL-1). None can reproduce their published index total.
2. **Validation regime tiers split 3 ways** — Strong (CPI/HG/FOCAL: per-state per-item); Medium (PRI/Newmark 2017: per-state sub-aggregate); **Weak-inequality only (Newmark 2005, Opheim 1991)**: `our_partial ≤ paper_total` is the only check.
3. **`unable_to_evaluate` convention applies across the board** (not just Opheim's catch-all): OOS items, un-projectable items, and Phase D portal-cells when only statute data is available. Critically: **not zeroed** (so weak-inequality holds).
4. **"Same-row-different-binary-cut" is a recurring per-item helper pattern** (PRI cadence family read by Newmark 2005 at 8-cell-OR and Opheim at 2-cell-OR).
5. **Row-promotion meta-pattern (`X-rubric-confirmed`)** is the seed of Phase 4 cross-rubric audit. `lobbyist_spending_report_includes_total_compensation` is now 7-rubric-confirmed.

**Provisional findings — biggest per-rubric surprises**

- **FOCAL 2024 has NO per-state US ground truth** — only federal LDA + 27 other countries. Cross-rubric is the *only* check for state FOCAL projections.
- **Newmark 2005 is NOT a near-clone of Newmark 2017** — different aggregation (4 sections vs 3), different validation regime (weak-inequality vs sub-aggregate), 6 panels vs 1.
- **HG 2007 has TWO retrieval blockers, not one**: (a) CPI's 2007 per-state scorecard (NOT Track A), (b) Track A `oh-statute-retrieval` for OH-specific sub-task.
- **HG's 22 NEW rows include 13 practical-availability cells** requiring portal observation, not statute extraction. Phase D targets.
- **FOCAL is substantially heavier than playbook suggests** — 11 Open Issues, scorer-judgment cutoff for scope.2, 2024→2025 numbering asymmetry, set-typed cells, weighted aggregation.

**Provisional findings — data-year audit (user-interjected)**

- 12 distinct statute vintages across the 8 rubrics, 1988-89 → 2025.
- **HG 2007 has per-item vintage split**: Q35-Q37 at 2002, rest at 2006-2007.
- **FOCAL state projections are vintage-flexible**: align to L-N 2025's 2019-2023 collection window.
- 4 rubrics have MEDIUM-or-lower data-year confidence (Sunlight, CPI 2015, PRI 2010, Newmark 2017); papers should be re-read during plan drafting to firm up.
- `oh-statute-retrieval` (Track A) currently fetches 4 vintages (2007/2010/2015/2025); full Phase C validation needs 12. Track A scope expansion is a separate conversation.

**Decisions carried forward**

- **Structure B**: 5 sub-sessions (sub-0 gap audit now complete; sub-1 Stream 1 plans → sub-2 Stream 2 plans → sub-3 FOCAL plan-set + HG plan → sub-4 launch infra + Sunlight canary).
- **FOCAL plan shape**: split into 3-4 sub-plans per scope (legal-side core, contact_log battery, openness battery, aggregation + US LDA validation).
- **HG plan launch gated** on Phase 0 scorecard retrieval; plan drafted with both paths (per-state if retrievable, weak-inequality if not).
- **Strict reading of disclosure-only Phase B scope** — keep current OOS items OUT; FOCAL-1 precedent does not retroactively apply.
- **7 convention proposals** from the gap audit to bake into all 6 plans (see [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) for the full list).

**Results**

- [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) — gap audit (5 cross-cutting meta-patterns + per-rubric gaps + implementation implications + convention proposals + decisions).
- [`results/20260514_rubric_data_years.md`](results/20260514_rubric_data_years.md) — publication-year vs data-year lookup table for all 8 rubrics, with confidence levels and paper-line citations.

**Next steps**

Sub-session 1 (next; separate Claude Code session with API-key auth): Stream 1 plans — Sunlight 2015 + Opheim 1991 in a single sub-session. Sunlight first (function-per-item; item 4 exclusion; per-item validation regime); Opheim second (declarative table; weak-inequality regime; un-projectable catch-all; β AND-projection reuse from Sunlight). Both plans self-contained per write-a-plan skill, with STOP clauses for spec-doc-vs-v2 drift. Each plan opens with a "Scope qualifier" + "Validation regime" + "Data year" section per the conventions established by sub-0.

After Sub-1: Sub-2 (Newmark 2017 → 2005), Sub-3 (FOCAL plan-set + HG plan with retrieval gate), Sub-4 (prompt template + headless launch script + Sunlight canary). HG launch waits on scorecard retrieval task (#6).

---

### 2026-05-14 — PRI 2010 projection: rubric #2 + PRI-MVP retirement

Convo: [`convos/20260514_pri_2010_tdd.md`](convos/20260514_pri_2010_tdd.md)
Results: [`results/20260514_pri_2010_projection.md`](results/20260514_pri_2010_projection.md)
Spec doc: [`../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md`](../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md)
Rollup spec: [`../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md`](../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md)

**Topics explored**

- Per-atomic-item projection logic for 76 PRI 2010 rubric items (54 disclosure-law + 22 accessibility). 75 are pure binary cell -> 0/1 passthroughs; Q8 is a typed 0..15 passthrough.
- Reuse of the paper-derived rollup helpers at `src/scoring/calibration.py` (handoff's "port if survived, rebuild from spec doc if not" resolved to **port** — the rollup is intact and unit-tested by 114 rule-level tests).
- Spec-doc / v2-TSV naming drift. Spec's `principal_report_*` and `lobbyist_report_*` resolve to v2's `principal_spending_report_*` and `lobbyist_spending_report_*`. E1f_i and E2f_i resolve to multi-rubric shared rows.
- End-to-end validation strategy given PRI publishes only sub-aggregate ground truth. User picked rule-based: existing calibration rollup tests + fixture per-item tests + accessibility 50-state round-trip + disclosure-law wiring tests.
- Architectural decision: declarative spec table for per-item layer (vs CPI's function-per-item pattern). Resolves CPI's deferred Open Question on cross-rubric template.
- Phase 3 PRI-MVP retirement (same session): move `smr_projection.py` and `test_smr_projection.py` to `_deprecated/` subdirs with SUPERSEDED banners; remove `cmd_build_smr` from `orchestrator.py`.

**Provisional findings**

- **Two projection axes, separate functions.** PRI 2010 publishes disclosure-law (max 37) and accessibility (max 22) as independent scores. Top-level API: `project_pri_2010_disclosure_law` + `project_pri_2010_accessibility`, each returning a typed score model carrying atomic_scores + sub-aggregates + total + percent.
- **Accessibility 50-state round-trip passes within tolerance.** Max residual ~0.05 across all 50 states (1-dp rounding artifact of PRI's published total_2010 column). Q8_normalized's 1-dp publication is the dominant error source (recovering Q8_raw introduces at most 0.033 per state); well inside ±1 spec.
- **No letter grade for PRI 2010.** Same as CPI 2015. The handoff's "confirm rubric-by-rubric" question for letter grades resolved negatively for rubric #2 as well.
- **`lobbyist_spending_report_includes_total_compensation` reaches 8 rubrics.** Once two projection modules read it, cross-rubric agreement audit on that row becomes well-defined — this is the kind of redundant validation Compendium 2.0's success criterion #4 was built for.
- **PRI-MVP cleanly retires.** 10 deprecated tests still pass when targeted directly (`uv run pytest tests/_deprecated/test_smr_projection.py`); excluded from default pytest collection.

**Results**

- Module: `src/lobby_analysis/projections/pri_2010.py` (388 LOC; declarative `_ATOMIC_SPEC` table + two Pydantic score models + 2 top-level projections + competition rank + ground-truth loaders).
- Tests: `tests/projections/test_pri_2010_per_item.py` (247 tests), `test_pri_2010_ground_truth.py` (6 tests), `test_pri_2010_aggregation.py` (13 tests) — 266 new tests, all passing.
- Phase 3 retirement: `src/scoring/smr_projection.py` -> `src/scoring/_deprecated/smr_projection.py`, `tests/test_smr_projection.py` -> `tests/_deprecated/test_smr_projection.py`, `cmd_build_smr` + helpers removed from `orchestrator.py`, `norecursedirs = ["_deprecated"]` added to pyproject.
- Full test suite: 640 passing + 5 skipped + 3 pre-existing failures (same `tests/test_pipeline.py::test_ca_snapshot_*` failures CPI 2015 flagged; missing gitignored data file).

**Decisions carried forward**

- **Declarative `_ATOMIC_SPEC` table** is the right pattern for rubrics with many near-identical per-item helpers. CPI's function-per-item pattern still fits rubrics with bespoke compound reads.
- **Cross-check spec-doc row names against v2 TSV early** — Phase B projection mappings written pre-`compendium-v2-promote` may have similar `*_spending_report_*` rename drift.
- **Per-rubric module + sibling tests pattern** carries forward unchanged from CPI: `src/lobby_analysis/projections/<rubric>.py` + `tests/projections/test_<rubric>_*.py`.
- **End-to-end validation tolerance is per rubric.** PRI accessibility supports 50-state round-trip; PRI disclosure-law is rule-level only (per-atomic-item ground truth never published). Future rubrics need a per-rubric validation strategy decision.

**Next steps**

Either:
- (a) Rubric #3: Sunlight 2015 (13 rows; 11 cross-rubric). Locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation.
- (b) Phase 4 cross-rubric agreement audit prototype, using CPI + PRI's two-module overlap.
- (c) Backport CPI 2015 to declarative table format (probably premature — CPI's compound reads don't compress cleanly into a 2-tuple spec).

Recommendation: (a). Cross-rubric audit (b) is more useful with 3 modules.

**Rubric-implementation playbook landed same session:** [`plans/20260514_rubric_implementation_playbook.md`](plans/20260514_rubric_implementation_playbook.md) generalizes the CPI + PRI patterns into a reusable kickoff brief for the remaining 6 rubrics (Sunlight, Newmark 2017/2005, Opheim, HG, FOCAL). Future rubric sessions should read the playbook instead of the original kickoff plan sketch — the playbook covers pre-flight (spec doc + v2-row-name cross-check + ground-truth location + rollup-helper survival check), architectural decision (declarative table vs function-per-item), validation regime selection, standard module structure, common rubric patterns (binary / tier / compound / typed / reverse-scoring / AND-projection / form-type-split / collect-once-map-many / catch-all), per-rubric notes for the 6 remaining rubrics, Phase 3 retirement protocol, and Phase 4 cross-rubric audit shape.

---

### 2026-05-14 — CPI 2015 C11 projection: first TDD session

Convo: [`convos/20260514_cpi_2015_c11_tdd.md`](convos/20260514_cpi_2015_c11_tdd.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md) (Phase 0 + Phase 1)
Results: [`results/20260514_cpi_2015_c11_aggregation_fit.md`](results/20260514_cpi_2015_c11_aggregation_fit.md)

**Topics explored**

- Per-item projection logic for the 14 CPI 2015 C11 indicators (6 de jure
  Boolean / threshold / enum reads + 8 de facto 5-tier passthroughs +
  1 compound passthrough on IND_205).
- Empirical fit of the aggregation rule against the published 50-state
  per-state aggregate. Four candidates evaluated; only one fits within
  tolerance.
- Data-quality normalization for 8 known glitch cells in the 700-cell
  ground-truth CSV (6 mixed-case Colorado cells + 2 numeric-where-
  categorical cells in Texas / Massachusetts).
- Rank tie-break convention used by CPI's published per-category rank.

**Provisional findings**

- **Aggregation rule:** unweighted mean of the 5 sub-category means
  (sub-cats 11.1-11.5 extracted from `papers/CPI_2015__sii_criteria.xlsx`,
  item counts 2/4/3/2/3). Max abs residual across 50 states is 0.05,
  i.e. a one-decimal rounding artifact of the published score. The
  other 3 candidates (simple mean, de-jure/de-facto halves, sequential
  sub-cats) miss the +/-1 tolerance on 18-38 of 50 states.
- **Normalization for invalid de jure cells:** the 2 numeric-string
  cells (Texas IND_199 "100", Massachusetts IND_203 "100") are
  consistent with CPI's aggregator treating them as NO (0), not YES
  (100). Setting them to NO produces exact fit; setting them to YES
  over-estimates by ~6.7 per state. Codified as a 0-default fallback
  for any de jure cell not in the YES/MODERATE/NO set after
  case-insensitive match.
- **Rank tie-break:** CPI uses competition ranking (1224 style; ties
  share a rank, next rank skips). Sequential ranking with alphabetical
  tie-break (a-priori guess) was off-by-1 to off-by-2 on 11 states.
- **No per-category letter grades.** CPI 2015 publishes letter grades
  at the overall-state level only. The kickoff plan implied
  per-category grades; that was incorrect for C11. Letter-grade
  projection dropped from this rubric's deliverable; rubrics #2-#8
  likely the same — confirm rubric-by-rubric.

**Results**

- Module: `src/lobby_analysis/projections/cpi_2015_c11.py` (per-item
  helpers IND_196-IND_209, ground-truth loader, sub-cat aggregator,
  rank, top-level `project_cpi_2015_c11`, `CPI2015C11Score` Pydantic
  model).
- Tests: `tests/projections/test_cpi_2015_c11_per_item.py`,
  `test_cpi_2015_c11_ground_truth.py`,
  `test_cpi_2015_c11_aggregation.py` (78 tests, all passing; full
  suite 384 pass + 3 pre-existing failures from
  `tests/test_pipeline.py` unrelated to this branch).
- Fit script: `scripts/fit_cpi_2015_c11_aggregation.py` (reproduces
  the empirical-fit decision; evaluates 4 candidate aggregators).
- Fit result: `results/20260514_cpi_2015_c11_aggregation_fit.md`.

**Decisions carried forward**

- Per-rubric module layout: `src/lobby_analysis/projections/<rubric>.py`
  + `tests/projections/test_<rubric>_*.py`.
- Cell input shape: `cells[row_id][axis] = value` nested dict,
  harness-independent.
- Per-item helper return type: plain `int` in {0, 25, 50, 75, 100}.
- Score type: frozen Pydantic model with `state` + `per_item_scores`
  dict + `category_score` float (no per-category letter grade — not
  published).
- Aggregation-fit pattern: try 3-4 closed-form candidates (simple mean,
  de-jure/de-facto halves, sub-cat means from published methodology
  doc when available, etc.), pick the one with the smallest max
  residual against published per-state aggregate.

**Next steps**

Either (a) start rubric #2 (PRI 2010, 69 rows; sub-aggregate rollup
rule already paper-derived in archived `pri-calibration` — port if
recoverable, rebuild from spec doc if not) or (b) refactor CPI
projection toward a declarative table format before more rubrics land.
Recommendation: (a). Refactor only if PRI 2010 makes duplication
painful.

**Pre-existing test failures flagged.** 3 tests in
`tests/test_pipeline.py` (test_ca_snapshot_*, test_brief_contains_*,
test_stamp_rows_*) fail on this branch *and* on main because
`data/portal_snapshots/CA/2026-04-13/manifest.json` doesn't exist
(`data/` is gitignored, no symlink set up for this branch). Not caused
by this session; flagged for the next person who looks at the test
suite — likely needs a `pytest.skipif` on missing data path or a
documented data-symlink step.

---

### 2026-05-14 — Kickoff orientation + plan sketch (NOT the first TDD session)

Convo: [`convos/20260514_kickoff_orientation.md`](convos/20260514_kickoff_orientation.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**Originating context.** This branch was assigned plan-sketch work as a side-effect of the 2026-05-14 coordination session on `compendium-v2-promote` (see [`../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available post-merge). User wanted a "solidly sketched" plan in `plans/` so the kickoff agent isn't reading skeleton stubs cold.

**Locked decisions carried forward.** v2 row contract now lives at `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows). `extraction-harness-brainstorm` owns v2 Pydantic models; this branch operates on raw `dict[str, Any]` keyed by `compendium_row_id` until those models exist. The ⛔ PRI-out-of-bounds banner is gone — PRI is rubric #2 in this branch's locked order.

**Sketch contents.** Concrete TDD agenda starting with CPI 2015 C11 (most-ready first rubric):
- Phase 0: env setup + projections module skeleton (`src/lobby_analysis/projections/`)
- Phase 1: per-item TDD cycles for 14 CPI items (6 de jure 2/3-tier + 8 de facto 5-tier per spec doc); aggregation rule fitted empirically against 50-state ground truth (700 cells per-item + 50 cells category-aggregate); letter grade + rank as derivations
- Phase 2: carry pattern through remaining 7 rubrics in locked order, with per-rubric notes (PRI 2010 rollup recoverable from `pri-calibration` archive; Newmark 2005 = 100% reuse of 2017; Opheim 100% reuse + weak-inequality tolerance; HG 2007 blocked on `oh-statute-retrieval`; FOCAL 2024 lowest reuse at 37.9%)
- Phase 3: PRI-MVP retirement after rubric #2 (move `cmd_build_smr` + `smr_projection` to `_deprecated/`)
- Phase 4: cross-rubric agreement audit after all 8 rubrics ship

**Recommended first session deliverable:** CPI 2015 C11 projection function (per-item + aggregation) passing against the 700-cell per-state-per-item + 50-cell category-aggregate ground truth.

**Open questions flagged for the first TDD session.** scipy/numpy availability for aggregation-rule fitting (current `pyproject.toml` has neither); PRI rollup helper recoverability from `pri-calibration` archive; letter grade boundaries (published vs back-fit); OH SMR equivalence tolerance for PRI-MVP retirement validation.

**Not implementation work.** No code, no tests written; only docs (the convo + plan sketch + this RESEARCH_LOG update + the Row-freeze contract path migration).


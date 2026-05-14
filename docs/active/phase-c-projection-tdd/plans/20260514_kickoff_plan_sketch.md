# Phase C Projection-TDD Kickoff Plan Sketch

> **Note added 2026-05-14 (post-PRI-2010 session):** Phases 0-3 of this plan are complete (env + CPI 2015 C11 + PRI 2010 + PRI-MVP retirement). Phase 2.2 onward (rubrics #3-#8) is now better served by the generalized playbook at [`20260514_rubric_implementation_playbook.md`](20260514_rubric_implementation_playbook.md), which captures the patterns established by CPI and PRI (declarative table vs function-per-item, validation-regime decision, spec-doc-to-v2 row-name drift check, common rubric patterns, per-rubric notes). Future rubric sessions should read the playbook instead of this sketch's Phase 2 paragraph. This sketch is preserved for traceability of the original Phase C kickoff decisions.

**Goal:** Get this branch from "skeleton seeded" to "first TDD'd projection function (CPI 2015 C11) passing against published ground truth" within one kickoff session. The pattern established for CPI 2015 C11 then carries through the remaining 7 rubrics in the locked order.

**Originating conversation:** [`../convos/20260514_kickoff_orientation.md`](../convos/20260514_kickoff_orientation.md) (which itself is a thin handoff from [`../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available on main post-`compendium-v2-promote` merge).

**Context:** Compendium 2.0 landed 2026-05-14 with 181 cell-typed rows; the v2 TSV is at `compendium/disclosure_side_compendium_items_v2.tsv` (live contract post-`compendium-v2-promote` merge). Per the ⭐ Compendium 2.0 success criterion #4, per-rubric projection functions are **sanity checks on extraction accuracy**, not the goal — each function takes hypothetically-correct compendium cells and projects to a per-state rubric score, validated against published ground truth. The 8 projections together give redundant per-row validation: each compendium row is read by 1–8 projections, so multi-rubric agreement at a row means high confidence in that row's extraction.

**Confidence:** High for the overall direction (projection-as-sanity-check is the load-bearing architecture of the Compendium 2.0 success criterion, articulated 2026-05-07 and locked through the row-freeze on 2026-05-13). Medium for CPI 2015 C11 aggregation specifics — aggregation rule is empirical and will be fitted in this session.

**Architecture:** Per-rubric projection functions live at `src/lobby_analysis/projections/<rubric>.py`. Each function takes `cells: dict[str, Any]` keyed by `compendium_row_id` (raw-dict shape until harness ships Pydantic models) plus a `state: str` argument, and returns a rubric score (numeric or `RubricScore` typed wrapper). Per-item logic lives in the function; aggregation logic on top. Tested against the matching per-state ground-truth CSV.

**Branch:** `phase-c-projection-tdd` (worktree at `.worktrees/phase-c-projection-tdd/`).

**Tech Stack:** Python 3.12, `uv`, Pydantic 2.x (for any typed wrappers), `pytest` for tests, `ruff` for lint. No LLM calls in this branch — projections are pure data transformations.

---

## Phase 0 — Setup (~15 min)

1. **Set up the worktree's Python env.** This worktree has no `.venv` yet. From the worktree root: `uv venv && uv sync --extra dev`. Confirm `uv run pytest --collect-only` shows the existing test suite (300 tests pass post-`compendium-v2-promote` once that branch merges).
2. **Confirm v2 TSV access.** Run `uv run python -c "from lobby_analysis.compendium_loader import load_v2_compendium; rows = load_v2_compendium(); print(len(rows))"`. Expect `181`. If `load_v2_compendium` is unimportable, this branch hasn't picked up `compendium-v2-promote` yet — rebase against main first (`git pull --rebase origin main`).
3. **Create the projections module skeleton.** `mkdir -p src/lobby_analysis/projections tests/projections && touch src/lobby_analysis/projections/__init__.py tests/projections/__init__.py`. Add to `pyproject.toml` if the package layout requires it (existing src-layout should auto-discover).

## Phase 1 — TDD the CPI 2015 C11 per-item projections (~2-3 hours)

### Read the spec first

Read [`../../historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md`](../../historical/compendium-source-extracts/results/projections/cpi_2015_c11_projection_mapping.md) end-to-end. Critical info from that doc:

- 14 atomic items (6 de jure + 8 de facto).
- De jure: 2-tier or 3-tier scoring → 100/50/0.
- De facto: **5-tier** scoring (0/25/50/75/100) — graders awarded 25/75 as partial-credit; published xlsx only documents 100/50/0 anchors.
- Per-state per-item ground truth at [`../../historical/compendium-source-extracts/results/projections/cpi_2015_c11_per_state_scores.csv`](../../historical/compendium-source-extracts/results/projections/cpi_2015_c11_per_state_scores.csv) (700 cells; 50 states × 14 items).
- Category-aggregate ground truth at `papers/CPI_2015__sii_scores.csv` (50 states; 0-100 numeric + letter grade + rank).
- 4 cell-level glitches in 700 cells (~99.4% clean): 4 mixed-case YES/NO typos + 2 numeric-where-categorical (IND_199, IND_203). Normalize before consumption.

### Architecture decisions to land before writing tests

These are short — pick a default and proceed. Capture choices in `convos/` if non-obvious.

1. **Cell input shape.** Use raw `dict[str, Any]` keyed by `compendium_row_id`. The 21 v2 rows CPI 2015 C11 reads are the keys. Coordinate with `extraction-harness-brainstorm` later for typed migration.
2. **Score type.** Pydantic `CPI2015C11Score` wrapping per-item raw scores + the aggregated category score + the letter grade + rank. Keep flat for now; can be elaborated later.
3. **Test fixture format.** Hand-coded fixtures for 5 representative states sampled across the score distribution (one top-3, one bottom-3, three middle). Each fixture is a `dict[str, Any]` literal. Plus a data-driven test that loads the full 50-state CSV and runs all of them.
4. **Tolerance.** For per-item: exact match (the ground truth is discrete tiers). For category aggregate: ±1 point of published score (allows for empirical-fit residual).

### Per-item TDD cycles (14 items)

For each item IND_196 through IND_209, run the TDD cycle:

1. **Read the item's section in the spec doc.** Identifies which v2 row(s) it reads and the projection logic (e.g., `threshold == 0 → YES; threshold > 0 → MOD; cell absent → NO`).
2. **Write the failing test.** In `tests/projections/test_cpi_2015_c11.py`:
   - Test name: `test_<item_id>_projects_<value_pattern>_to_<expected_tier>`.
   - Construct a `cells` dict literal with the items the projection reads.
   - Call the per-item projection helper (doesn't exist yet → ImportError).
   - Assert the returned score matches the expected tier.
3. **Run the test — confirm it fails** with ImportError or AttributeError on the missing function.
4. **Write the minimal helper in `src/lobby_analysis/projections/cpi_2015_c11.py`**.
5. **Run the test — confirm it passes.**
6. **Run all 50 states from the ground truth CSV through this item's helper** as a follow-up data-driven test in the same file. Should pass for all 50 (modulo the 4 documented data-quality glitches — handle via a normalization pass before consumption).
7. **Commit each item's red→green→data-driven cycle as one commit.** Commit message: `cpi_2015_c11: TDD IND_<NNN> per-item projection`.

Order the items by simplest spec first (likely IND_196 — clean 2-tier de jure) so early commits build confidence before tackling the 5-tier de facto items.

### Aggregation TDD cycle

After all 14 per-item helpers pass against 50 states each:

1. **Write the failing test** asserting `project_cpi_2015_c11(cells, state="NY").category_score` matches the published NY score within ±1.
2. **Fit the aggregation rule.** With 50 states × 14 per-item scores and 50 category-aggregate ground truths, linear regression (or simple mean / sub-category mean candidates from the spec doc) determines the formula. Use `numpy` / `scipy` if needed; ask before adding `scipy` if not already in `pyproject.toml`.
3. **Implement the aggregation formula** in `project_cpi_2015_c11`.
4. **Run all 50 states through the full aggregation.** Should pass within ±1 for all 50. If residual exceeds tolerance on >2 states, the aggregation rule is wrong — try a different candidate from the spec doc's list, or surface to user.

### Letter grade + rank projections

CPI publishes letter grades (F to A) and ranks (1-50) in addition to the numeric category score. These are derivations of the numeric score:

- Letter grade is a numeric → letter map; the boundaries can be back-fitted from the 50-state distribution.
- Rank is `argsort(-category_score)` with stable tie-handling.

Each gets its own TDD cycle (one test, one helper, run against 50 states).

## Phase 2 — Carry the pattern through the remaining 7 rubrics

Once CPI 2015 C11 is shipped, the pattern is established. Each rubric in the locked order gets its own session (this is multi-session work — not all in one go).

### Per-rubric session structure

- Read the matching `<rubric>_projection_mapping.md` spec.
- Set up `tests/projections/test_<rubric>.py` and `src/lobby_analysis/projections/<rubric>.py`.
- Per-item TDD cycles.
- Aggregation TDD cycle (if the rubric has one).
- Validate against published ground truth.

### Rubric-specific notes (gathered from this branch's RESEARCH_LOG + spec docs)

- **PRI 2010 (rubric #2; 69 rows):** Sub-aggregate rollup rule already paper-derived (in archived `pri-calibration` branch). Worth porting that rollup helper if it survived the archive. PRI methodology rules (B1/B2 reverse-scored per footnotes 85/86; E "higher of E1/E2 + F/G double-count + separate J") confirmed in factual audit pre-merge — trust the spec.
- **Sunlight 2015 (rubric #3; 13 rows):** 11 cross-rubric. Three locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation. These conventions matter for clean projection code.
- **Newmark 2017 (rubric #4; 14 rows):** 8 reused, 6 new. Load-bearing r=0.04 CPI↔PRI-disclosure correlation factually audited 2026-05-13 — projection arithmetic in the spec is trusted. **Caveat:** Newmark 2017's "0.71 comparator" in the summary is sourced from Newmark 2005, not the 2017 paper — flagged in PAPER_INDEX Audit Notes; extract from `papers/text/Newmark_2005__lobbying_regulation_in_the_states.txt` if needed.
- **Newmark 2005 (rubric #5; 14 rows):** **100% reuse of Newmark 2017 mappings.** 2005 mapping falsified the 2017 mapping's `contributions_from_others` parallel speculation. Easier projection — just port from #4 with the falsification noted.
- **Opheim 1991 (rubric #6; 14 row families):** **100% reuse.** β AND-projection is the 2nd concrete use after Sunlight. 1 catch-all un-projectable item (`disclosure.other_influence_peddling_or_conflict_of_interest`) — first contributing-rubric item with `unable_to_evaluate` projection (excluded from partial, not zeroed). Tolerance check is weak inequality (`projected_partial ≤ paper_total`) — paper publishes per-state index totals only, no per-item.
- **HG 2007 (rubric #7; 38 rows):** 16 reused, 22 new. **Blocked on `oh-statute-retrieval`** for ground-truth retrieval. Don't start this rubric's TDD until Track A's HG 2007 sub-task ships.
- **FOCAL 2024 (rubric #8; 58 rows post-FOCAL-1):** 22 reused, 36 new. 37.9% reuse — lowest single-mapping rate. Verbatim L-N 2025 Suppl File 1 weights (1,372-cell ground truth). US LDA tolerance 81/182 = 45% baseline.

## Phase 3 — PRI-MVP retirement (after rubric #2)

After PRI 2010 projection (rubric #2) passes against ground truth:

- `cmd_build_smr` orchestrator subcommand and `src/scoring/smr_projection.py` are empirically superseded.
- Move to `src/scoring/_deprecated/` (preserving git history via `git mv`) per the "mv over rm for research artifacts" convention.
- Drop the `load_v1_compendium_deprecated` import alias from `tests/test_compendium_loader.py` and `tests/test_smr_projection.py` if those tests are removed alongside. Otherwise keep functional (the v1 loader supports those tests, not new work).
- Update `STATUS.md` to note PRI-MVP retirement landed.

## Phase 4 — Cross-rubric agreement audit (after all 8 rubrics)

After all 8 projections pass against their respective ground truths:

- For each compendium row read by 2+ rubrics, audit: do all rubrics agree on the row's cell value for a sample of states? Disagreement signals either an extraction-pipeline issue (which `extraction-harness-brainstorm` would address) or a projection-mapping bug (which this branch would address).
- The most-validated row `lobbyist_spending_report_includes_total_compensation` is the natural starting point — 8 projections agreeing on its value across a sample of states is strong validation of the row design.

---

## Testing Plan

This branch is pure data transformations — no LLM calls, no network, no fixtures larger than CSV. TDD is straightforward.

For each per-item projection in each rubric:

- I will add unit tests that construct a `cells` dict literal with the row IDs that item reads, call the per-item helper, and assert the returned tier matches the expected value. The test boundary is the per-item helper function (boundary input: `cells: dict[str, Any]` + `state: str`; boundary output: tier value). Tests do NOT inspect helper internals.
- I will add a data-driven follow-up test per item that loads the rubric's per-state ground-truth CSV (where available) and iterates all states, asserting each state's projected tier matches the published tier. This validates the per-item helper against real data, not just hand-coded fixtures.
- I will NOT write tests that assert the `cells` dict has certain keys or that types are typed — those are testing-anti-patterns. Tests must exercise projection behavior.

For each rubric's aggregation:

- I will add a test asserting `project_<rubric>(cells, state).category_score == published_score(state) ± tolerance` for a representative sample of 5 states. Then a data-driven follow-up across all states.
- The aggregation formula itself is fitted from the 50-state ground truth (where available) — but I will NOT add a test that asserts the formula's coefficients. The behavior is "the formula reproduces published scores"; the coefficients are implementation detail.

For PRI-MVP retirement:

- I will add a test asserting `phase-c PRI 2010 projection` reproduces the same OH 2010 + OH 2025 SMR scores that `cmd_build_smr` did, within tolerance. This is the empirical superseding step. Existing `tests/test_smr_projection.py` tests stay green throughout (v1 path preserved); the new Phase C path adds an equivalent test against the same OH SMRs.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## What could change

- **Aggregation rule for CPI 2015 C11.** Spec doc lists candidate formulas (simple mean, sub-category mean, de jure/de facto half, weighted variants). Empirical fit on the 50-state data picks the winner; if no candidate fits within ±1 on >48 of 50 states, surface to user — may indicate the per-item projections are wrong, not the aggregation.
- **Projection function input shape.** Currently `dict[str, Any]` keyed by `compendium_row_id`. Will migrate to harness branch's Pydantic models once those exist. Plan accommodates this by keeping the projection signature simple and the type explicit.
- **HG 2007 blocking dependency.** If `oh-statute-retrieval` hasn't shipped HG 2007 ground truth by the time Phase C reaches rubric #7, that rubric gets deferred or stubbed.
- **Spec docs flagged open issues.** Each `<rubric>_projection_mapping.md` has its own Open Issues section. Most are deferred to "compendium 2.0 freeze planning" but a few may surface during TDD (e.g., HG-1 def_target_executive_agency carve-out split, FOCAL Open Issues 2-11). Handle case-by-case; defer if not blocking.

---

## Open Questions

- **PRI rollup helper from `pri-calibration`** — did it survive the archive? Check `docs/historical/pri-calibration/results/` and the orchestrator subcommands list. If yes, port; if no, rebuild from `pri_2010_projection_mapping.md` spec.
- **scipy / numpy availability** for aggregation-rule fitting. Currently `pyproject.toml` has `pydantic`, `requests`, `playwright`, `pytest`, `ruff`. If aggregation needs linear regression, request user permission to add `numpy` or `scipy`.
- **Letter grade boundaries for CPI.** Are they published, or do we back-fit from the 50-state distribution? Check `papers/CPI_2015__sii_scores.csv` first.
- **OH SMR equivalence tolerance for PRI-MVP retirement.** The v1 `cmd_build_smr` produced OH 2010 + OH 2025 SMRs with 21.3% inter-run disagreement (per archived `statute-retrieval` results). What's the appropriate tolerance for the Phase C PRI projection to "match" those? Likely the existing inter-run disagreement bound (exact equivalence would over-constrain).

---

**Testing Details.** Per-item TDD cycles use hand-coded `cells` dict fixtures (small, deterministic) + data-driven follow-ups over the rubric's ground-truth CSV. Aggregation TDD cycles validate `category_score` within a tolerance bound against published scores. No mocking — all tests exercise real projection behavior over real or hand-coded data.

**Implementation Details.**

- Branch is in worktree `.worktrees/phase-c-projection-tdd/`. The v2 row contract is at `compendium/disclosure_side_compendium_items_v2.tsv` (live post-`compendium-v2-promote` merge; rebase if not yet visible).
- Module layout: `src/lobby_analysis/projections/<rubric>.py` + `tests/projections/test_<rubric>.py`. New package.
- Projection function signature: `def project_<rubric>(cells: dict[str, Any], state: str) -> <Rubric>Score`. Cell input is harness-independent.
- PRI-MVP code at `src/scoring/orchestrator.py::cmd_build_smr` + `src/scoring/smr_projection.py` retires after rubric #2 lands. Move to `_deprecated/` not delete.
- Spec docs at `docs/historical/compendium-source-extracts/results/projections/<rubric>_projection_mapping.md` are the implementation spec; trust them (factual-audited pre-merge for the 3 load-bearing summaries).
- HG 2007 ground-truth retrieval depends on `oh-statute-retrieval` branch — sequence accordingly.

**What could change:** See "What could change" section. Headline: CPI aggregation rule is empirical; harness Pydantic models will eventually replace raw-dict input shape; HG 2007 ground truth gated on Track A.

**Questions:** See "Open Questions" section. Headline: scipy/numpy availability for fitting; PRI rollup helper recoverability from `pri-calibration` archive.

---

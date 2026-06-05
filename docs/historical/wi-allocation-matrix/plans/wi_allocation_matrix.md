# WI Allocation Matrix Implementation Plan

**Goal:** Build the {principal, lobbyist, lawmaker, bill} influence graph for WI 2025-2026 by (a) inferring a per-(lobbyist, principal) hours matrix from the WI lobbying release via bipartite matrix completion, (b) joining external WI Legislature bill-sponsorship data for the lawmaker→bill edge, and (c) scoping WI CFIS campaign-finance data as a third leg closing the principal→lawmaker $-flow edge.

**Originating conversation:** [`convos/20260530_wi_allocation_matrix_kickoff.md`](../convos/20260530_wi_allocation_matrix_kickoff.md)

**Context:** Suhan (Corda lead) asked for a "company → lobbyist → lawmaker → bill" chain across states. Walking the merged WI 2025-2026 release (`releases/wi/`) showed 3 of 6 pairwise relations are direct disclosures, 1 is bipartite-matrix-inferable, 1 is freely scrapable from the WI Legislature site, and 2 require WI CFIS to close. This branch executes all three legs.

**Confidence:** Mixed. Leg 1 (matrix completion) is High — IPF is a standard textbook method for exactly this shape of problem; the supporting WI data is already on disk and audited. Leg 2 (bill sponsorship) is High — endpoints are public and well-known. Leg 3 (CFIS investigation) is Exploratory — we don't yet know the access surface or schema; Phase 4 is a scoping/discovery exercise, not an implementation commitment.

**Architecture:** Four phases plus a Phase 0 setup. Phase 1 loads + audits the WI release, builds the bipartite graph, runs connected-component analysis, and surfaces the data-quality issues (Pettack outlier, percent-rounding discrepancies, partial-semester edges) that the IPF fit needs to handle. Phase 2 runs the IPF fit per connected component per semester per hours-type, producing the `h_{Y,P}` matrix with per-cell confidence (exactly-pinned vs free). Phase 3 scrapes WI Legislature for bill metadata + sponsorship and composes the end-to-end chain. Phase 4 is a CFIS scoping subtask that ends in a written assessment, not code.

**Branch:** `wi-allocation-matrix` (already cut; worktree at `/Users/dan/code/lobby_analysis/.worktrees/wi-allocation-matrix/`, baseline 1541 pass + 3 pre-existing `test_pipeline.py` baseline failures)

**Tech Stack:** Python 3.13, uv-managed; pandas, numpy, scipy (for `scipy.optimize.linprog` if needed); `ipfn` package for IPF (or hand-rolled, it's ~30 lines); httpx + BeautifulSoup for WI Legislature scrape (OR check OpenStates / `pyopenstates` first); pytest for TDD.

---

## Worktree paths (CRITICAL — all paths are within the worktree)

- **Worktree root:** `/Users/dan/code/lobby_analysis/.worktrees/wi-allocation-matrix/`
- **Branch docs:** `docs/active/wi-allocation-matrix/`
- **Source release (read-only input):** `releases/wi/` (6 TSVs)
- **Existing WI scrape code (read-only reference, do not modify):** `src/lobby_analysis/io/wi/`
- **New code lives at:** `src/lobby_analysis/allocation/wi/` (new module — does not exist yet)
- **Tests live at:** `tests/test_wi_allocation_*.py`
- **Outputs:** `data/allocations/WI/` (gitignored, symlinks to `/Users/dan/data/lobby_analysis/allocations/WI/`)
- **Results writeups:** `docs/active/wi-allocation-matrix/results/`

---

## Testing Plan

**Behavior under test, not implementation:**

- **Loader behavior:** loading `releases/wi/WI_principal_filings.tsv` for semester H1 returns a per-principal row-sum dict whose total equals the documented $47.5M aggregate (within rounding); loading `WI_lobbyist_filings.tsv` quarterly and aggregating to semester returns column-sums that sum to the same number of total hours as the principal-side independently computes (within data-quality tolerance — `Pettack` outlier is expected to inflate the lobbyist side).
- **Bipartite graph construction:** authorization edges active in H1 2025 (filtered by `authorized_on` ≤ 2025-06-30 AND (`withdrawn_on` is null OR `withdrawn_on` ≥ 2025-01-01)) produce an edge set whose distinct lobbyist count + principal count + edge count match externally-verified spot values.
- **Connected-component decomposition:** running CC analysis on the bipartite graph yields a documented number of components; the largest component's size is reported as a fixture-pinned scalar; isolated singleton components (one lobbyist, one principal, one edge) are correctly classified as "exactly pinned, no IPF needed."
- **IPF convergence:** on a hand-constructed 3×3 toy graph with known marginals, the IPF implementation converges to the known correct solution within `< 1e-6` row+column residual.
- **IPF on real component:** on the largest WI 2025 H1 connected component, IPF converges (row + column residual under tolerance) within bounded iterations; output cells are nonnegative.
- **Attribution chain:** for principal P with two bills b1, b2 at 60% / 40% and a single lobbyist Y with 100 H1 hours, the modeled `hours_{Y, b1}` = 60 and `hours_{Y, b2}` = 40.
- **End-to-end chain composition:** given the inferred `h_{Y,P}` matrix + scraped bill sponsorship, the composed table has the schema columns `(principal_id, lobbyist_id, bill_id, modeled_hours, sponsor_lawmaker_id, attribution_confidence)`, contains at least one row for DoorDash (known to lobby on bills with named sponsors), and the row count for DoorDash equals (# DoorDash bills × # DoorDash lobbyists × 2 hours-types × 2 semesters) after the modeling rolls through.

**Validation behavior (separate from unit tests):**

- For each connected component, the post-fit row-sum residual and column-sum residual are both `< 0.01` of total marginal (relative).
- For each principal P, the sum of `Σ_Y h_{Y,P}` matches the principal's filed total hours (within IPF residual tolerance).
- For each lobbyist Y, the sum of `Σ_P h_{Y,P}` matches the lobbyist's filed total hours (within IPF residual tolerance + after explicit outlier handling for Pettack-class principals).
- Spot-check 3 DoorDash-bill-effort rows against the source release and confirm the modeled attribution is internally consistent with the principal's filed %.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Phase 0 — Setup, audit, and design

**Goal:** Walk into the WI release with fresh eyes. Confirm data shapes match the plan's assumptions before any code is written.

1. **Read** `releases/wi/README.md` end-to-end. Note the 7 documented caveats — Pettack outlier (#1), low-spend-exempt principals (#2), the 56 zero-filing principals (#3), Neumann-Ortiz silent absence (#4), address sub-field (#5), Madison/WI duplicate (#6), WCTA acronym (#7).
2. **Inspect** all 6 TSVs by reading the first 3-5 lines of each: confirm column names, dtypes, and one-line-per-record assumptions.
3. **Confirm percent format:** read 20 rows from `WI_principal_bill_efforts.tsv` to confirm `percent` column format (string like `"1%"` or `"54.9%"`). Convert to float in the loader.
4. **Confirm period-label format:** read 10 distinct `period_label` values from the bill-efforts file. Map to `(year, H1|H2)`.
5. **Confirm authorization date coverage:** confirm `authorized_on` and `withdrawn_on` exist for all rows; spot null fraction.
6. **Confirm semester → quarter mapping** on the lobbyist side: lobbyist activity filings are quarterly (4 per lobbyist per year per Notes in the release README); confirm by reading distinct `(reporting_period_start, reporting_period_end)` values in `WI_lobbyist_filings.tsv`.
7. **Read** `src/lobby_analysis/io/wi/tier_2_materialize.py` to understand how the TSVs were generated. **Do not modify** — this is read-only reference.
8. **Read** `src/lobby_analysis/models/filings.py` to understand the `LobbyingFiling` schema. The IPF output will compose with this schema downstream.
9. **Read** the archived branch's results writeup at `docs/historical/wi-disclosure-explore/results/20260526_wi_tier_2_parser_results.md` for context on the data-quality observations.
10. **Write a Phase 0 results doc** at `docs/active/wi-allocation-matrix/results/YYYYMMDD_phase_0_data_audit.md` summarizing: row counts, percent-rounding discrepancy distribution per (principal, semester), zero-filing principal count, partial-semester edge count, decision on Pettack-outlier handling. Commit.

**Deliverable:** Phase 0 results doc + 0 new code.

---

## Phase 1 — Bipartite graph construction + connected-component analysis

**Goal:** Build the bipartite graph data structure, run CC decomposition, identify which cells are exactly pinned vs free, and produce a per-component summary for the IPF step.

### 1.1 Write the failing tests first

11. Write `tests/test_wi_allocation_load.py` with these tests:
    - `test_load_principal_totals_for_h1_2025` — returns dict {principal_id: (total_hours_comm, total_hours_other)}; aggregate sum matches release README's documented H1 totals.
    - `test_load_lobbyist_totals_for_h1_2025` — quarterly → semester aggregation; result dict {lobbyist_id: (total_hours_comm, total_hours_other)}.
    - `test_active_edges_for_h1_2025` — given the authorizations TSV, returns the set of `(lobbyist_id, principal_id)` pairs active in H1 2025. Test against a known authorization fixture row.
    - `test_bill_effort_percent_parsing` — `"54.9%"` → `0.549`; `"1%"` → `0.01`; verify `(principal_id, semester) → list[(item_id, item_name, percent_float)]`.
12. Run these tests with `uv run --with pytest pytest tests/test_wi_allocation_load.py -v` and confirm they all RED (import errors / functions missing). Commit RED.
13. Write `tests/test_wi_allocation_graph.py` with these tests:
    - `test_bipartite_graph_node_counts_h1_2025` — graph has the expected lobbyist count + principal count + edge count for H1 2025.
    - `test_connected_components_decomposition` — graph decomposes into `>1` components; total node count across components equals overall node count.
    - `test_exactly_pinned_cells` — singleton components (one principal, one lobbyist, one edge) classified as "exactly pinned" and the pinned value equals the lobbyist's total hours and the principal's total hours simultaneously.
    - `test_pettack_outlier_flagged` — lobbyist 11072 (Pettack) has hours `> 2× sum of any plausibly-attributable principal hours` and is flagged for the outlier-handling list.
14. Run these tests, confirm RED, commit RED.

### 1.2 Implement the loader

15. Create `src/lobby_analysis/allocation/wi/__init__.py` (empty package marker).
16. Implement `src/lobby_analysis/allocation/wi/load.py` with: `load_principal_totals(release_dir, semester) -> dict[int, tuple[float, float]]`, `load_lobbyist_totals(release_dir, semester) -> dict[int, tuple[float, float]]`, `load_active_edges(release_dir, semester) -> set[tuple[int, int]]`, `load_bill_effort_percents(release_dir, semester) -> dict[int, list[tuple[int, str, float]]]`. Minimal implementations to pass the load tests.
17. Run `tests/test_wi_allocation_load.py`; confirm GREEN. Commit GREEN.

### 1.3 Implement the graph + CC decomposition

18. Implement `src/lobby_analysis/allocation/wi/graph.py` with: `build_bipartite_graph(edges, principal_totals, lobbyist_totals) -> BipartiteGraph` (dataclass), `connected_components(graph) -> list[Component]`, `classify_components(components) -> tuple[list[ExactlyPinned], list[FreeComponent]]`, `flag_outliers(graph) -> list[OutlierFlag]`. Minimal implementations to pass the graph tests.
19. Run `tests/test_wi_allocation_graph.py`; confirm GREEN. Commit GREEN.

### 1.4 Phase 1 writeup

20. Write `docs/active/wi-allocation-matrix/results/YYYYMMDD_phase_1_graph_structure.md` summarizing: total nodes + edges, component count, largest-component size, exactly-pinned-cell count, free-cell count (= the size of the IPF problem to be solved in Phase 2), flagged outliers. Commit.

---

## Phase 2 — IPF fit

**Goal:** Run iterative proportional fitting on each non-trivial connected component, per semester, per hours-type. Produce the `h_{Y, P, semester, hours_type}` 4-D matrix.

### 2.1 Write the failing tests first

21. Write `tests/test_wi_allocation_ipf.py`:
    - `test_ipf_converges_on_toy_3x3` — hand-constructed 3×3 with row sums `[10, 20, 30]`, column sums `[15, 25, 20]`, full support → IPF converges to within `1e-6` residual; row + column sums match.
    - `test_ipf_converges_on_sparse_toy` — 3×3 with one zero-edge → IPF respects the sparsity pattern (zero stays zero).
    - `test_ipf_max_entropy_for_underdetermined` — toy where multiple solutions exist with same marginals; IPF returns the max-entropy one (verify against known closed-form for the 2×2 unrestricted case).
    - `test_ipf_on_largest_wi_h1_component` — IPF converges; residuals `< 0.01` relative; all cells nonnegative.
    - `test_ipf_handles_outlier_lobbyist` — Pettack 11072's marginal is replaced by an "uncertain — flagged" placeholder OR the fit explicitly downweights her contribution; component fits do not blow up.
22. Run, confirm RED, commit RED.

### 2.2 Implement IPF

23. Use the `ipfn` package from PyPI (verified working 2026-05-30: installs in ~5 packages, sub-second; `from ipfn import ipfn; ipfn.ipfn(m, aggregates, dimensions, convergence_rate=1e-6, max_iteration=500).iteration()` returned correct 3×3 toy fit with exact row + column marginals). Add as a project dep via `uv add ipfn`.
24. Implement `src/lobby_analysis/allocation/wi/ipf.py` with: `fit_component(component, hours_type) -> ComponentFit` (returns the cell matrix + residuals + iteration count). Wraps `ipfn.ipfn`. Minimal to pass the toy tests.
25. Run toy tests; GREEN. Commit.
26. Implement `fit_all(graph, semester) -> AllocationMatrix` that orchestrates over components × hours-types.
27. Run the real-component tests; GREEN. Commit.

### 2.3 Phase 2 writeup + materialize

28. Implement `src/lobby_analysis/allocation/wi/materialize.py`: `materialize_allocation_matrix(release_dir, output_dir)` produces `WI_lobbyist_principal_hours_h1_2025.tsv` and `WI_lobbyist_principal_hours_h2_2025.tsv` with columns `(lobbyist_id, principal_id, hours_comm, hours_other, confidence)` where `confidence ∈ {exact, ipf_fit, outlier_flagged}`.
29. Write `tests/test_wi_allocation_materialize.py` with end-to-end behavior tests (file produced, schema correct, row count matches edge count, exactly-pinned cells round-trip correctly).
30. Run via a CLI module `src/lobby_analysis/allocation/wi/cli.py`; output to `data/allocations/WI/`. Verify by hand-spot-checking 3 cells.
31. Write `docs/active/wi-allocation-matrix/results/YYYYMMDD_phase_2_ipf_fit.md` summarizing: components fit, iterations needed, residuals achieved, % of cells exactly-pinned vs IPF-fit, outlier flag count. Commit.

---

## Phase 3 — Bill sponsorship scrape + end-to-end chain

**Goal:** Get `lawmaker → bill` edges for WI 2025-2026, then compose `principal → lobbyist (inferred) → bill → lawmaker` into a single end-to-end table.

### 3.1 Investigate OpenStates first

32. **Stop and ask** Dan: "OpenStates already aggregates state legislative data; check there before writing a WI scraper. Should I (a) use OpenStates Python client, (b) scrape `docs.legis.wisconsin.gov` directly, or (c) try OpenStates first and fall back?"
33. If OpenStates: use `pyopenstates` or the JSON API to get all WI 2025-2026 bills with sponsors. If direct scrape: identify the WI Legislature endpoint (likely `docs.legis.wisconsin.gov/2025/proposals/...` or similar — Phase 3 discovery task).

### 3.2 Write the failing tests first

34. Write `tests/test_wi_legislature_load.py`:
    - `test_bill_metadata_for_known_bill` — given bill ID "Senate Bill 3" (Wisconsin 2025-2026), load returns expected sponsor + cosponsors + committee. Use OpenStates spot-check OR a captured fixture HTML/JSON.
    - `test_bill_id_normalization` — "Senate Bill 3" / "SB 3" / "2025 SB 3" all resolve to the same canonical bill key.
35. Run, confirm RED, commit RED.

### 3.3 Implement loader

36. Implement `src/lobby_analysis/allocation/wi/legislature.py` with `load_bill_sponsorships(session="2025") -> dict[bill_key, BillMetadata]` and `normalize_bill_id(raw: str) -> bill_key`.
37. Run tests; GREEN. Commit.

### 3.4 Compose end-to-end chain

38. Implement `src/lobby_analysis/allocation/wi/chain.py`: `compose_chain(allocation_matrix, bill_efforts, bill_metadata) -> ChainTable` producing rows `(principal_id, principal_name, lobbyist_id, lobbyist_name, bill_id, bill_title, modeled_hours, principal_filed_percent, sponsor_lawmaker_id, sponsor_lawmaker_name, attribution_confidence)`.
39. Write `tests/test_wi_allocation_chain.py`:
    - `test_doordash_chain_nonempty` — DoorDash (principal 11091) produces at least one row with a real lobbyist and a real bill with a named sponsor.
    - `test_chain_row_count_matches_join_arithmetic` — total chain rows = expected from join arithmetic (principal × lobbyist × bill cardinalities per principal).
    - `test_chain_confidence_distribution` — confidence column populated with one of the three documented values for every row.
40. Run, GREEN, commit.

### 3.5 Phase 3 writeup + materialize

41. Materialize to `data/allocations/WI/WI_chain_2025.tsv` via the CLI.
42. Write `docs/active/wi-allocation-matrix/results/YYYYMMDD_phase_3_chain.md` summarizing: chain row count, % rows with a named sponsor, % rows with bill metadata, DoorDash worked example end-to-end, top-10 (lobbyist, lawmaker) pairs by modeled hours. Commit.

---

## Phase 4 — CFIS scoping (write-only, no scrape)

**Goal:** Characterize what WI CFIS exposes well enough to scope a follow-up branch. **No CFIS scrape this branch** — just the investigation + writeup.

43. Investigate the WI Ethics Commission's Campaign Finance Information System. Find: bulk download? API? scrape only? What's the principal identifier (employer name string? FEIN? something else)? Lobbyist personal-donation disclosure path?
44. Identify the public access surface. Try one sample query end-to-end (e.g., fetch a single contribution record for a known WI lawmaker) to confirm the access pattern.
45. Document join keys: how does a CFIS donor record map back to a WI lobbying principal (string match? canonicalization? lookup table?)? How does a CFIS recipient map to a WI legislator (typically by name + chamber + district)?
46. Write `docs/active/wi-allocation-matrix/results/YYYYMMDD_phase_4_cfis_scoping.md` with: data availability assessment, recommended access path, schema sketch, join-key analysis, identified risks, **explicit recommendation** for whether a separate `wi-campaign-finance` branch should be cut and what its first phase should be.

**Deliverable:** Phase 4 writeup. Zero new code.

---

## Phase 5 — Finish and PR

47. Run full pytest suite: `uv run --with pytest pytest --tb=no -q`. Confirm 1541 + (new tests) pass + same 3 pre-existing baseline failures, zero regressions.
48. Run `ruff check`. Fix any F-class violations.
49. Run `finish-convo` (skill) — convo summary + RESEARCH_LOG entry + STATUS.md one-liner, commit + push.
50. Run `finishing-a-development-branch` (skill) — pre-merge code review via `nori-code-reviewer`, address blockers, open PR. Suhan + other fellows can see the chain Suhan asked for.

---

## Edge cases the implementing agent must handle

- **Empty-period principals.** Some principals file `$0.00` for one semester only (low-spend-exempt). For those semesters, principal_total_hours is 0; their lobbyists in that semester contribute 0 hours through them. Test this case in Phase 1.
- **Soft-404 lobbyist 12717 (Neumann-Ortiz).** She's not in the lobbyist roster but might be referenced from authorization edges (verify). If she IS referenced, exclude the edge from the graph (no column-sum constraint available for her).
- **Privacy-redacted principals (11530, 13137).** They have no filings; if they appear in the authorization edges, exclude.
- **Pettack outlier (11072).** Her marginal is implausible (7,611 hours, ≈32 hrs/day). Two options to discuss with Dan in Phase 2: (a) replace her marginal with `min(her_marginal, sum_of_her_principals'_marginals)`, or (b) flag her cells as `confidence=outlier_flagged` and skip the constraint. Default: (b).
- **Percent-rounding.** Per-(principal, semester) bill-effort percentages may not sum to exactly 100% (string-format rounding to 1%). Treat as advisory rather than exact; in the chain composition, normalize.
- **Partial-semester authorizations.** A lobbyist authorized on 2025-04-01 contributes at most 3 of 6 months of the H1 semester. Either time-weight the column-sum (e.g., scale lobbyist Y's H1 column-sum constraint by their active fraction within H1) OR ignore and accept the slack as IPF residual. Default: ignore in v1, document, possibly add in v2.
- **Quarterly→semester aggregation.** Lobbyist Q1 + Q2 hours sum to lobbyist H1 hours; verify this identity in a Phase 0 audit step.
- **Bill ID format mismatch.** Source release stores `item_name` as `"Senate Bill 3"`, WI Legislature may use `"SB 3"` or `"2025 Senate Bill 3"`. Normalize at the join, not at load.
- **Bills the principal lobbied that have no Legislature record.** "Topics Not Yet Assigned A Bill Or Rule Number" bucket rows (31.7% of bill-effort rows) — these have no `item_id` in the legislature. Chain composition emits them with `sponsor_lawmaker_id = null` and `attribution_confidence = "topic_no_bill_yet"`.

---

## Validation / what success looks like

- Phase 2 fit: row + column residuals `< 0.01` relative for all components.
- Phase 3 chain: ≥80% of `Legislative Bills/Resolutions`-bucket bill-effort rows successfully matched to a WI Legislature bill with a named sponsor.
- End-to-end: a "DoorDash worked example" table for Suhan showing the full chain on one principal — what bills they lobbied, what % effort, which lobbyists worked for them, how the hours allocate, who sponsored the bills they targeted.

---

**Testing Details:** Tests assert observable behavior — file row counts, marginal sums, residual tolerances after IPF convergence, end-to-end chain row counts vs join arithmetic, presence of expected entities (DoorDash, Pettack, the WCTA acronym ambiguity). No tests on data-class structure or type signatures; no tests that only verify mocks. Each phase's GREEN bar requires both unit-test pass AND a manual spot-check of 2-3 cells against the source release.

**Implementation Details:**
- New module: `src/lobby_analysis/allocation/wi/` (load, graph, ipf, materialize, legislature, chain, cli).
- IPF library: ask Dan in Phase 2 whether to use `ipfn` from PyPI or hand-roll.
- WI Legislature data source: ask Dan in Phase 3 whether to use OpenStates / `pyopenstates` or direct scrape; OpenStates almost certainly preferred (uses existing infrastructure the project has already adopted per the `data-model-v1.1` archived branch).
- Output schema for the inferred hours: `(lobbyist_id, principal_id, hours_comm, hours_other, confidence ∈ {exact, ipf_fit, outlier_flagged})`.
- Output schema for the full chain: `(principal_id, principal_name, lobbyist_id, lobbyist_name, bill_id, bill_title, modeled_hours, principal_filed_percent, sponsor_lawmaker_id, sponsor_lawmaker_name, attribution_confidence)`.
- Per-cell confidence distinguishes exactly-pinned cells (singleton components, known with zero modeling error) from IPF-fit cells (modeled, with the proportional-attribution assumption) from outlier-flagged cells (excluded from fit).
- All data outputs to `data/allocations/WI/` (gitignored, symlinks to user's `~/data/lobby_analysis/allocations/WI/`).
- Phase 4 (CFIS) ends in a written assessment, not code — explicitly scoped that way to keep this branch focused.
- The `wi-allocation-matrix` branch does not modify `releases/wi/` — that release is the upstream contract; any data fixes belong on a different branch.
- Pre-existing baseline failures on `test_pipeline.py` (3 tests, archived-line-owned) are not in scope; do not attempt to fix them on this branch.

**What could change:**
- **Phase 4 might surface that CFIS is harder than expected** (e.g., behind an interactive query form, no bulk export). In that case Phase 4's recommendation may be "scrape via headless browser" and that subbranch becomes much larger; the chain Suhan asked for stays incomplete until CFIS is in.
- **OpenStates coverage of WI 2025-2026 might be partial.** If sponsor data is missing for ≥50% of WI bills, Phase 3 may need to fall back to direct scrape, adding ~1 day.
- **Pettack-class outliers may be more common than expected.** If Phase 0 surfaces 10+ similar lobbyists with implausible hour aggregates, the "flag and exclude" strategy needs to scale to a more systematic outlier-detection step (e.g., flag any lobbyist whose hours exceed `2× sum of plausibly-attributable principals'`).
- **The proportional-attribution assumption (lobbyist Y attacks principal P's bill mix in proportion to P's filed %) might be challengeable.** Without per-lobbyist-per-bill ground truth in any WI snapshot, it cannot be validated against WI alone. If a state with contact-log disclosure (per the compendium: a handful exist) is in scope later, cross-state calibration becomes possible.
- **The bipartite graph might have one giant connected component** dominating the structure, leaving almost no exactly-pinned cells. If so, the entire matrix is IPF-modeled rather than partially exact, and the confidence column has only one value for most rows.

**Questions:**
- Q1 (Phase 3): OpenStates first, or direct scrape first? Default recommendation: OpenStates first.
- Q2 (Phase 2): Pettack-outlier handling — flag-and-exclude (default) or replace-marginal-with-min?
- Q3 (Phase 3): Should the chain composition emit rows for the "Topics Not Yet Assigned" bucket (31.7% of bill-efforts have no bill ID), or filter them out? Default: emit with `attribution_confidence = "topic_no_bill_yet"` to preserve the principal-level signal.
- Q4 (Phase 4): What's the user-acceptable scope for CFIS investigation — 0.5 day timeboxed, or open-ended until we get a clean schema characterization?
- Q5 (out of scope, but worth flagging): cross-state replication of this analysis will need a generic version of the IPF + chain code, parameterized by state. Should we design for that now, or strictly YAGNI to WI?

**Resolved (locked at plan-writing time, do not re-ask):**
- IPF library: `ipfn` from PyPI. Verified working 2026-05-30 on a 3×3 toy. Phase 2 uses it directly.

---

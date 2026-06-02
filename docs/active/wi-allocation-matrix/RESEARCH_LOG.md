# RESEARCH_LOG — wi-allocation-matrix

Branch index. Newest entries first.

---

## Branch charter

Take the merged WI 2025-2026 lobbying-disclosure release (`releases/wi/`, 6 TSVs, ~2.9 MB, $47.5M total spend across 944 principals) and build the **{principal, lobbyist, lawmaker, bill}** influence graph that Suhan asked for. The WI lobbying data gives us **3 of 6 pairwise relations directly** (principal↔lobbyist, principal↔bill with effort %, lobbyist↔hours-aggregated-marginal); the remaining 3 are either inferable from constraints, scrapable from a free external source, or structurally absent without a separate dataset.

Three legs to the stool:

1. **Bipartite matrix completion** (within WI lobbying data): infer per-(lobbyist, principal) hours from the principal-side row sums + lobbyist-side column sums, using the authorization edges as the support pattern. Then attribute through principals' per-bill effort %s to get a modeled **lobbyist → bill** matrix.

2. **WI Legislature bill-sponsorship scrape** (`docs.legis.wisconsin.gov`): direct **lawmaker → bill** edges (sponsor, cosponsors, committee membership). Free, structured, in-scope.

3. **WI CFIS campaign finance** (Wisconsin Ethics Commission, separate database): direct **principal → lawmaker** $-flow edges via PAC + corporate-contribution disclosures, and **lobbyist → lawmaker** personal-donation edges. Closes the two relations the lobbying data structurally cannot.

With all three legs, the chain Suhan asked for — "company W spends X via lobbyist Y on bill Z sponsored by lawmaker A who received $B from W" — is **fully populated** for WI 2025-2026 from public-record disclosure data.

## Convos

- [`convos/20260530_wi_allocation_matrix_kickoff.md`](convos/20260530_wi_allocation_matrix_kickoff.md) — kickoff: 6-relation classification, IPF framing, 3-leg architecture, plan-only decision.
- [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md) — Phase 0 (audit, no code) + Phase 1 (TDD: loaders + bipartite graph + CC decomposition + outlier flagging); landed Phase 1 with 32 new tests + zero regressions.
- [`convos/20260531_phase_2_ipf_design_and_execution.md`](convos/20260531_phase_2_ipf_design_and_execution.md) — Phase 2 design + execution (TDD: IPF fit + materialize + CLI); 27 new tests + zero regressions. Empirical ipfn probe at giant-CC scale; Pettack-not-in-giant discovery; confidence-label schema (`exact` / `ipf_fit` / `zero_filed` / `aggregation_flagged`); small-CC over-attribution pattern flagged as Phase 3+ candidate.
- [`convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md`](convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md) — Phase 3 (TDD: legislature loader + chain composer + materialize). Pivot from `pyopenstates` / OpenStates API to Plural Policy bulk CSV after probing surfaced rate-limit constraints (10/min + 500/day) and structural advantages (CSV has `person_id` on sponsorships, JSON only has names). 20 new tests + 5 commits + zero regressions; 115,229-row chain TSV materialized.
- [`convos/20260602_phase_3_per_sponsor_normalization.md`](convos/20260602_phase_3_per_sponsor_normalization.md) — Phase 3.1 refinement (TDD: 6 new tests). Two new columns (`num_sponsors_on_bill`, `modeled_hours_per_sponsor`) implement uniform-share normalization so `SUM GROUP BY sponsor` stops inflating by sponsor count. Mid-session: WI bill-id collisions discovered (e.g. principal 11473 filed effort on multiple distinct "AB 1"s); `item_id` added to chain TSV to disambiguate. Headline finding: chamber-bias artifact in top-sponsor table reverses (10/10 Assembly → 8/10 Senate); lower:upper ratio 3.4× → 1.2×.

## Plans

- [`plans/wi_allocation_matrix.md`](plans/wi_allocation_matrix.md) — implementation plan for a fresh session (5 phases + Phase 0 setup; charter is "do all 3 legs"; CFIS leg ends in scoping writeup, not code).

## Results

- [`results/20260530_phase_0_data_audit.md`](results/20260530_phase_0_data_audit.md) — Phase 0 audit. Four findings reshape the plan: lobbyist filings are semester (not quarterly) → IPF marginals align natively; percent-rounding is structural (only 41% of (principal, period) groups sum to 100%, max 100%) → Phase 3 attribution math needs a decision; active edges per semester ~1,912 (H1) / ~2,055 (H2), not the biennium-union 2,254; one giant 835-node CC dominates the H1 graph (only ~6.4% exactly-pinned cells).
- [`results/20260530_phase_1_graph_structure.md`](results/20260530_phase_1_graph_structure.md) — Phase 1 graph + CC writeup. H1 / H2 both dominated by one giant CC (835 / 900 nodes); 122 / 140 exactly-pinned singletons; 70 / 71 free components for Phase 2 IPF. Pettack catchable only via per-day arithmetic (the plan's marginal-ratio heuristic alone is silent — her 6 SAA-family principals' combined 4,197 hr marginal "explains" her 4,007.5 hrs). 4 low-hours ratio-trips against zero-marginal principals — candidate for `min_hours_for_ratio_flag` suppression in Phase 2.
- [`results/20260531_phase_2_ipf_fit.md`](results/20260531_phase_2_ipf_fit.md) — Phase 2 writeup. 27 new tests + 5 commits land IPF + materialize + CLI. Three findings revise the plan: (1) Pettack is in her own 6×6 CC with balanced marginals; no exclusion mechanism needed — labeling-only. (2) Bipartite support via seed=1 on edges / 0 elsewhere is the right primitive; ipfn preserves zeros at machine precision. (3) `zero_filed` cells preserved deliberately so consumers can spot filing gaps. Small-CC over-attribution pattern (8 H1 CCs with `agg_res` 4-42%) flagged as Phase 3+ refinement candidate.
- [`results/20260601_phase_3_chain.md`](results/20260601_phase_3_chain.md) — Phase 3 chain composer writeup. 115,229 chain rows in `data/allocations/WI/WI_chain_2025.tsv`; 97.9% legislative effort-row coverage (plan §217 bar ≥80%); DoorDash worked example end-to-end (78 rows, arithmetic spot-checked). Bulk CSV pivot from `pyopenstates` rationalized; 4 Phase 3+ refinement candidates flagged (TNYB bucket inclusion, cosponsor parsing, per-cell row-residual exposure, per-bill-normalized top-sponsor metric). Pettack-not-in-chain finding: `aggregation_flagged` lives on lobbyist axis, legislative attribution lives on principal axis; the two are decoupled by design.
- [`results/20260602_phase_3_1_per_sponsor_normalization.md`](results/20260602_phase_3_1_per_sponsor_normalization.md) — Phase 3.1 writeup. Adds `num_sponsors_on_bill` + `modeled_hours_per_sponsor` + `item_id` to the chain TSV (additive, non-breaking). Old top-10 (10/10 Assembly) → new top-20 (8/10 Senate); LeMahieu at #8 on only 4 bills surfaces as structurally interesting outlier. Chamber lower:upper ratio drops 3.4× → 1.2×. Bill-id-collision finding: 3 cases of distinct WI bills sharing canonical `bill_id` (principal 11473's "AB 1" voter-ID vs education-assessment, etc.); `item_id` resolves. 1,288 hr (2.6%) of "unknown" chamber bucket flagged for future name-match audit.
- [`results/20260602_wi_chain_synthesis.md`](results/20260602_wi_chain_synthesis.md) — **Suhan-facing standalone synthesis** integrating Phases 0 → 3.1. Leads with the LeMahieu/SB 28 and chamber-reversal findings; covers the 6-relation framing, chain construction at a non-statistical-audience level (bipartite graph + IPF + per-sponsor normalization with confidence labels), the modeling assumptions consumers are trusting (proportional attribution, uniform-share sponsor split), what the chain can / cannot answer, and dependency structure for next-step ordering (A: unknown-chamber audit cheap+orthogonal; B → C: cosponsor parsing before CFIS scoping). No new code or analysis — pure synthesis of the existing five phase docs. **Revised same day** after the LeMahieu inspection below: the original "leadership-vehicle hypothesis" was retracted and replaced with the single-bill SB 28 finding.
- [`results/20260602_lemahieu_bill_inspection.md`](results/20260602_lemahieu_bill_inspection.md) — **Bill-level inspection of LeMahieu's 4 bills**, written as the prerequisite check the synthesis flagged as needed before any external claim. Headline: the #8 ranking is 98.8% one bill (SB 28, electric transmission ROFR). LeMahieu is sole primary sponsor; 29 principals filed effort, with electric-utility industry concentration (ATC Management 331 hrs, WEC 134, WIEG 124, AFP 86, plus the major IOUs). AFP outlier surfaces the position-direction gap as a project-wide finding (the chain detects coalition *activity*, not *composition*). Method-level lesson logged: per-sponsor metrics can compress single-bill signals into apparent broad patterns — do per-bill inspection before claiming sponsor-level patterns externally.

---

## Session: 2026-06-02 — phase_3_per_sponsor_normalization

**Convo:** [`convos/20260602_phase_3_per_sponsor_normalization.md`](convos/20260602_phase_3_per_sponsor_normalization.md)

### Topics Explored
- Phase 3 v1 chain inspection (DoorDash slice, arithmetic verification, edge-confidence ladder)
- 4 initial RED tests for `num_sponsors_on_bill` + `modeled_hours_per_sponsor` + conservation invariant
- Discovery mid-implementation: 3 of 10,290 conservation groups failed → WI bill-id collisions (multiple distinct `item_id`s share canonical `bill_id` like "AB 1")
- Decision: add `item_id` to chain TSV (Dan's pick); 2 additional RED tests; conservation test rewritten to group by `item_id` (the unique source-row identifier)
- Recomputed top-sponsor + chamber rollup tables old-metric-vs-new-metric

### Provisional Findings
- Per-sponsor normalization conserves total bill-allocated effort: 48,789 hr (vs 561k inflated by sponsor count)
- Chamber bias in top-sponsor table reverses: old 10/10 Assembly → new 8/10 Senate; lower:upper ratio 3.4× → 1.2×
- Two distinct lobbying-target profiles emerge: concentrated Senate primaries (65-123 bills, high per-sponsor weight) vs broad-named Assembly co-authors (198-234 bills, low per-sponsor weight)
- LeMahieu (Senate Majority Leader) at #8 on only 4 bills — high concentration per bill, structurally interesting signal that was buried in the old metric
- WI bill-id collisions are a real biennium-internal phenomenon (3 cases in this snapshot, all under principal 11473); `item_id` in the chain TSV is the disambiguator going forward
- 1,288 hr (2.6%) of `modeled_hours_per_sponsor` lands in an "unknown" chamber bucket — likely 60 collective entities (Joint Legislative Council / Law Revision Committee) plus possible name-normalization gaps

### Results
- [`results/20260602_phase_3_1_per_sponsor_normalization.md`](results/20260602_phase_3_1_per_sponsor_normalization.md)
- [`results/20260602_wi_chain_synthesis.md`](results/20260602_wi_chain_synthesis.md) — added later same day, mid-discussion: Suhan-facing standalone synthesis of Phases 0 → 3.1, written so a project-lead audience can read the chain's findings and limitations without walking the per-phase docs (revised post-LeMahieu-inspection — see next line)
- [`results/20260602_lemahieu_bill_inspection.md`](results/20260602_lemahieu_bill_inspection.md) — bill-level inspection prerequisite the synthesis flagged. LeMahieu's #8 ranking is 98.8% one bill (SB 28, electric transmission ROFR, sole primary). Forced revision of the synthesis's leadership-vehicle hypothesis. Surfaces position-direction gap (no support/oppose field) as a project-wide finding worth flagging on the compendium side.

### Next Steps
- Pause for Dan review of the new top-sponsor profile
- Phase 4 (CFIS scoping) — write-only investigation; per-sponsor honesty sharpens the join target
- Cosponsor parsing (refinement #2) — next natural in-chain refinement
- "Unknown" chamber name-match audit (~30 min diagnostic)
- Position-weighted sponsor attribution as a possible v1.2 if uniform-share turns out to be too crude

---

## Session: 2026-06-01 — phase_3_kickoff_and_bulk_data_pivot

**Convo:** [`convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md`](convos/20260601_phase_3_kickoff_and_bulk_data_pivot.md)

### Topics Explored
- Plan step 32 Q1 boundary: OpenStates vs direct scrape (Dan: c, OpenStates first w/ fallback)
- OpenStates API probing: key required server-side, 10 req/min + 500 records/day rate limit, `pyopenstates` library swallows HTTP status + headers
- Pivot to Plural Policy bulk CSV: 15 normalized tables + separate legislator-csv (`wi.csv`), `person_id` (`ocd-person/...`) on 99.8% of sponsorship rows
- Structural finding: cosponsors are NOT in any structured data (JSON or CSV) — only in `bill_actions.description` text; primary-only scope locked for v1
- Sponsor `lawmaker_id` resolution: bulk CSV's `person_id` field enables real-ID joins instead of the original name-string-as-ID Option A
- 60 collective-entity sponsors (Joint Legislative Council × 26, Law Revision Committee × 34) flagged via `is_collective=True`
- Committee assignment: structural via `bill_actions.organization_id` only identifies chamber, not specific committee → committee name parsed from `description` text regex
- TDD: legislature loader (13 tests) + chain composer (7 tests); 20 total; 5 commits

### Provisional Findings
- Bulk CSV path is strictly better than the OpenStates API path for this workload — same data (Plural Policy = OpenStates), structured `person_id` join key, no rate limit, no auth, free
- 100% bill-identifier coverage from bulk: all 1,000 unique legislative effort `Senate Bill X` / `Assembly Bill X` strings resolve to OpenStates short form `SB X` / `AB X`
- 97.9% chain coverage of unique legislative effort rows (3,947 of 4,030); clears plan §217 ≥80% bar by wide margin
- DoorDash worked example: 78 chain rows (3 lobbyists × 4+9 sponsors × 2 semesters); arithmetic verified
- Pettack (lobbyist 11072): 0 chain rows. Her 6 SAA-family principals don't file legislative-bucket bill efforts. `aggregation_flagged` lives on lobbyist axis, legislative attribution on principal axis — decoupled by design.
- Top 10 sponsors are all Assembly (lower chamber) — likely confound from per-bill primary sponsor counts on Assembly-originated bills, not a clean "most-lobbied" signal

### Results
- [`results/20260601_phase_3_chain.md`](results/20260601_phase_3_chain.md)

### Next Steps
- **Pause for Dan review** — Phase 3 v1 delivered; 4 Phase 3+ refinement candidates flagged (TNYB bucket, cosponsor parsing, per-cell row-residual, per-bill-normalized top-sponsor)
- Phase 4 (CFIS scoping): write-only investigation, no scrape; characterize WI Ethics Commission schema, determine join keys
- Phase 5 (PR): only when Dan says ready

---

## Session: 2026-05-31 — phase_2_ipf_design_and_execution

**Convo:** [`convos/20260531_phase_2_ipf_design_and_execution.md`](convos/20260531_phase_2_ipf_design_and_execution.md)

### Topics Explored
- Empirical ipfn probe before tests: 3×3 toy, bipartite support via zero-seed, Pettack-style marginal exclusion via implied row marginal, scale on 312×523 / 1,441-edge giant CC
- **Pettack-not-in-giant discovery:** she's in her own 6L × 6P × 11E CC where marginals balance natively (730.2 comm both sides; 3,454.5 vs 3,466.8 other). Plan/Phase 1 assumed exclusion from the giant CC; the actual data needs no marginal surgery at all
- Pushback exchange with Dan on Pettack labeling: avoid "illegal" framing without WI §13.62 evidence; settle on descriptive `aggregation_flagged` label
- Phase 2 test design: aggregate row residual < 5% per CC (not per-row); per-row distribution reported in writeup; small-CC over-attribution flagged but not asserted-against
- 5-commit Phase 2 build: `min_hours_for_ratio_flag` param → IPF RED → IPF GREEN → materialize → CLI + stdout cleanup
- Hand-spot-check 4 cells: exact round-trip, Pettack row total within 0.4%, zero_filed (0, 0), DoorDash col-sum EXACT match (83.90 == 83.9, 87.50 == 87.5)

### Provisional Findings
- IPF on per-CC basis converges sub-second total across all 70 free CCs; giant CC alone ~340 ms (comm) + ~80 ms (other)
- Bipartite support pattern via zero seed is rigorous (max leak in non-support cells = 0.0 machine precision)
- Giant CC aggregate row residual: 1.3% comm / 2.8% other; median per-row residual 0.78% comm / 2.33% other
- Materialized output: 1,912 rows H1 / 2,055 rows H2; confidence dist (H1): 6.4% `exact` / 90.8% `ipf_fit` / 2.5% `zero_filed` / 0.3% `aggregation_flagged`
- 8 small CCs (H1) have over-attribution pattern (principal-side > sum of authorized lobbyists' filed hours, with zero-marginal co-lobbyists in same CC); same mechanism as giant CC but more concentrated; currently invisible in `ipf_fit` label
- `min_hours_for_ratio_flag=10` (live default in `fit_all`) suppresses the 4 H1/H2 ratio-flag false positives from Phase 1; only Pettack still flagged (via the per-semester absolute axis)

### Results
- [`results/20260531_phase_2_ipf_fit.md`](results/20260531_phase_2_ipf_fit.md)

### Next Steps
- Phase 3 (bill sponsorship scrape + chain composition) — pause immediately at plan step 32 to ask Dan Q1 (OpenStates vs direct WI Legislature scrape)
- Phase 3 Q3 boundary will surface decisions on "Topics Not Yet Assigned" bucket emission and `zero_filed` / `aggregation_flagged` row propagation through the chain composition
- Per-cell row-residual exposure (Phase 2-raised) is a deferred refinement candidate, not blocking
- Pettack-legality WI §13.62 question is a compendium-side investigation that belongs on a different branch entirely

---

## Session: 2026-05-30 (evening) — phase_1_loaders_and_graph

**Convo:** [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md)

### Topics Explored
- TDD cycle: RED tests for loaders (4 fns) + graph (4 fns + 5 dataclasses); confirmed RED via ModuleNotFoundError
- Loader: 4 entry points, semester-string ("2025-H1") input form; active-edge filter `auth <= period_end AND (wd null OR wd >= period_start)`; null-`authorized_on` exclusion (4 edges)
- Graph: NetworkX-backed CC decomp; BipartiteGraph/Component/ExactlyPinned/FreeComponent/OutlierFlag dataclasses
- Outlier-flag heuristic adjustment mid-implementation: marginal-ratio check ALONE doesn't catch Pettack (the SAA-family 6 principals "explain" her hours at the marginal level); added per-semester absolute check (>2000 hr, ~16 hrs/day)

### Provisional Findings
- Orphan lobbyists (11513, 12717) in authorizations but not in roster — loader surfaces faithfully; graph layer falls back to principal marginal in singleton classify
- Per-semester structure stable: H2 slightly larger than H1 across the board (more auths accumulate by mid-year); same "one giant CC" pattern
- 93% of edges live in free components (need IPF); 6.5% are exactly-pinned singletons; outliers ~ 2-4 per semester

### Results
- [`results/20260530_phase_1_graph_structure.md`](results/20260530_phase_1_graph_structure.md)

### Next Steps
- Phase 2: IPF on free components (toy 3×3 + sparse + max-entropy verification + real giant CC); use `ipfn` package per plan
- Phase 3 boundary will surface Q1 (OpenStates vs scrape) to Dan; Phase 4 boundary will surface Q4 (CFIS timebox)
- Optional Phase 2 refinements: `min_hours_for_ratio_flag` to suppress the 4 low-hours false positives

---

## Session: 2026-05-30 (afternoon) — phase_0_data_audit

**Convo:** [`convos/20260530_phase_0_and_1_execution.md`](convos/20260530_phase_0_and_1_execution.md)

### Topics Explored
- Walked all 6 TSVs of `releases/wi/` against plan Phase 0 steps 1–10
- Confirmed `WI_principal_bill_efforts.tsv` has embedded newlines in `item_description` — pandas-correct, `wc -l` undercounts by 4
- Audited percent-rounding distribution across all 1,428 (principal, period) groups
- Verified Pettack 11072 outlier (7,611 hrs = 1,216.5 comm + 6,394.5 other; 2.84× next-highest lobbyist)
- Computed H1 2025 connected-component decomposition (preview of Phase 1)
- Diagnosed lobbyist-filings-are-semester (release README is wrong; source code at `tier_2_materialize.py:12` is correct)

### Provisional Findings
- See Results doc TL;DR: 4 findings reshape the plan. Key: percent-rounding is asymmetric (max 100%, median 95%, 5th-pctl 35.7%) → structural undercounting, not noise.
- Confidence column in Phase 2 output will be ~6.4% `exact` / ~93.6% `ipf_fit` / small `outlier_flagged` tail — dominated by the giant CC.

### Results
- [`results/20260530_phase_0_data_audit.md`](results/20260530_phase_0_data_audit.md)

### Next Steps
- Phase 1 (graph construction + CC analysis) — TDD: write failing tests RED → loader + graph → GREEN → CC writeup
- Q6 (percent-rounding interpretation) remains open until Phase 3 boundary
- Release-README mislabel ("quarterly") flagged but not fixed on this branch — separate small commit on release-maintenance line

---

## Session: 2026-05-30 — wi_allocation_matrix_kickoff

### Topics Explored
- Walked WI 2025-2026 release against Suhan's "company → lobbyist → lawmaker → bill" ask
- Clarified principal-files-bill-efforts (direct disclosure, not attribution)
- Enumerated 6 pairwise relations: 3 direct in WI lobbying, 1 IPF-inferable, 1 free external scrape, 2 need CFIS
- Bipartite matrix completion math: ~2,254 cells / semester, ~3,432 constraints with both hours-types; decomposes into components with many exactly-pinned cells
- Three legs of the stool: matrix completion (WI lobbying), bill sponsorship (WI Legislature / OpenStates), CFIS (Wisconsin campaign finance — scoping only this branch)

### Provisional Findings
- Company → bill is **direct sworn disclosure** in WI, not modeling — corrects earlier framing
- Matrix completion is genuinely tractable (standard IPF / RAS), with a non-trivial fraction of cells exactly pinned in singleton CC components
- The "lobbyist X targeted bills sponsored by lawmaker Y" derived edge is a defensible proxy for influence target but NOT for direct contact; flag clearly in any Suhan-facing output
- CFIS is the structural completion of Suhan's chain — without it the chain is incomplete for the (principal → lawmaker) $-edge

### Results
(none — plan-only session)

### Next Steps
- Fresh-context session executes `plans/wi_allocation_matrix.md` starting at Phase 0
- Implementing agent must read `convos/20260530_wi_allocation_matrix_kickoff.md` first for the reasoning trajectory

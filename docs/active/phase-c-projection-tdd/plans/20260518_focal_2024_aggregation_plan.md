# FOCAL 2024 — Aggregation + Federal US LDA Validation Harness Implementation Plan

**Goal:** Ship the top-level `project_focal_2024(cells, jurisdiction, vintage)` function + weighted-sum aggregation + Federal US LDA validation harness + ranking. This plan lands **last** in the 4-plan FOCAL set; it consumes the `_ATOMIC_SPEC` dispatcher and per-item helpers built by the legal-core / contact-log / openness-timeliness plans and wires them into the end-to-end projection. **The Federal US LDA validation is the primary deliverable** — it is the project's only cross-rubric calibration anchor for FOCAL at the per-rubric layer (FOCAL has no per-state US ground truth; US LDA is the load-bearing 49-indicator + 81-raw-points exact match check).

**Originating conversation:** [`../convos/20260518_focal_hg_plans_drafting.md`](../convos/20260518_focal_hg_plans_drafting.md) (Sub-3 of Phase C — FOCAL plan-set + HG plan with retrieval gate). Final companion plan in the 4-plan FOCAL set:

- [`20260518_focal_2024_legal_core_plan.md`](20260518_focal_2024_legal_core_plan.md) — module skeleton (must land first).
- [`20260518_focal_2024_contact_log_plan.md`](20260518_focal_2024_contact_log_plan.md) — contact log battery (must land second).
- [`20260518_focal_2024_openness_timeliness_plan.md`](20260518_focal_2024_openness_timeliness_plan.md) — openness + timeliness batteries (must land third).
- **This plan** — aggregation + Federal US LDA harness (lands last).

**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md) — aggregation rule (lines 54-78); Federal US LDA scoring (line 84-100); Phase C validation (line 103-108). The plan below is **derivative**; read the spec for the published US LDA per-battery breakdown.

**Context:** Rubric #8 in Phase C's locked rubric order. FOCAL's published aggregation rule per Lacy-Nichols 2025 Suppl File 1 Tables 3, 4, 5:

```
per_indicator_score(i) = base(i) × weight(i)
  base(i)   ∈ {0=no, 1=partly, 2=yes}
  weight(i) ∈ {1, 2, 3}  (verbatim per Suppl File 1 Table 4 "Our weights")

per_jurisdiction_score = Σ per_indicator_score(i) over all 50 indicators
                       ∈ [0, 182]
per_jurisdiction_pct   = per_jurisdiction_score / 182
```

Weight distribution: 20 × weight-1 + 19 × weight-2 + 11 × weight-3 = 91, × 2 = **182 max** (full 50-indicator scoring).

For Phase C with FOCAL-1 resolution (revolving_door.2 OUT): max projects to **180** (revolving_door.2 weight 1 × max 2 = 2 excluded). For 2025 vintage with "Lobbyist list" addition: max projects to **186** (180 + 6 from the new weight-3 indicator). Per-vintage max is dispatcher-dependent.

**Confidence:** High. The aggregation rule is paper-explicit; weights are verbatim from Suppl File 1 Table 4; the audit doc has confirmed the US LDA published total of 81 raw points exactly. Per-indicator US LDA values are documented in the spec doc; cross-rubric harness reuses the existing test infrastructure in `tests/projections/test_cross_rubric_overlap.py`.

**Architecture:** Adds the top-level `project_focal_2024` function + `aggregate` helper + Federal US LDA validation tests + cross-rubric overlap tests + ranking function. **Does not add new `_ATOMIC_SPEC` entries** — relies on the 49 (2024) or 50 (2025) entries already added by the 3 companion plans.

**Branch:** `phase-c-projection-tdd` (worktree at `.worktrees/phase-c-projection-tdd`).

**Tech Stack:** Python 3.12, Pydantic v2, pytest, `uv` for env management.

---

## Cross-plan ordering — landed fourth (last in FOCAL set)

Sequence within FOCAL plan-set:

1. Legal core (skeleton)
2. Contact log
3. Openness + timeliness
4. **Aggregation + Federal US LDA harness (this plan)** — wires everything together

**Sub-4 headless launcher must enforce the full 4-step sequence.** This plan's tests will fail if any companion plan hasn't shipped — the per-item dispatcher for the missing battery returns 0 for all items, which produces a Federal US LDA total well below the 81 target.

---

## Scope qualifier — same as legal-core plan

Inherits 1 item OUT (`revolving_door.2`); 49 in scope for 2024 vintage, 50 in scope for 2025 vintage (49 + `relationships.lobbyist_list_2025`).

---

## Validation regime — Strong (Federal US LDA); Cross-rubric only (US states)

### Federal US LDA — load-bearing exact-match test

Federal US LDA per the audit doc + L-N 2025 Suppl File 1 Table 5:

```
Scope:          4 + 0 + 0 + 2  =  6
Timeliness:     0 + 0          =  0   (2024 numbering: .1 + .2 separately; both 0)
Openness:       4 + 0 + 6 + 3 + 6 + 2 + 2 + 2 + 2  =  27
Descriptors:    4 + 2 + 0 + 0 + 2 + 0  =  8
Revolving_door: 6 + 0          =  6   (revolving_door.1 IN by FOCAL-1; revolving_door.2 OUT)
Relationships:  6 + 2 + 0 + 0 + 0  =  8   (5 entries; ordering ambiguous per FOCAL-5)
Financials:     4 + 4 + 0 + 0 + 0 + 4 + 0 + 0 + 0 + 0 + 4  =  16
Contact_log:    2 + 0 + 2 + 0 + 0 + 0 + 0 + 0 + 3 + 0 + 3  =  10
TOTAL:          81 / 182 = 45%        (projected: 81 / 180 = 45% after revolving_door.2 deferral)
```

**Primary Federal US LDA test:**

```python
def test_federal_us_lda_aggregate_2024_vintage(federal_us_lda_cells):
    score = project_focal_2024(federal_us_lda_cells, jurisdiction="Federal_US", vintage=2024)
    assert score.total_raw == 81, f"Expected 81 raw points; got {score.total_raw}"
    assert abs(score.pct - 0.45) <= 0.01  # 81/180 = 0.45 vs published 81/182 = 0.445 → ≤1pp residual
```

**Per-battery subtotal tolerance** (acknowledging the partly-tier collapses documented in companion plans):

```python
# Tolerances reflect known projection-vs-published deltas from partly-tier collapses:
_FEDERAL_US_LDA_SUBTOTAL_TOLERANCE = {
    "scope": 0,           # exact match expected (no partly-tier collapse)
    "timeliness": 0,      # exact (all binary)
    "openness": 4,        # ~+3 over-scoring from openness.4 partly tier collapse
    "descriptors": 4,     # ~+4 over-scoring from descriptors.* partly tier collapses
    "revolving_door": 0,  # exact (revolving_door.1 IN; binary)
    "relationships": 6,   # ~+4 over-scoring from relationships.* partly tier; +2 from FOCAL-5 ordering
    "financials": 4,      # ~+2 over-scoring from financials.3 / .4 partly tier
    "contact_log": 12,    # ~+10 over-scoring from .1, .3, .9, .11 partly tier collapses
}
```

**Total tolerance** ≤ sum of subtotal tolerances = ~30 raw points if all worst-case. In practice, partly-tier collapses both over-score and under-score depending on cell content — net deviation should be much smaller. **For the total-raw test, use `abs(projected - 81) ≤ 15` as a starting tolerance**; tighten as the implementing agent observes actual projection-vs-published deltas during the validation run.

**STOP clause:** if the total-raw projection lands outside `[66, 96]`, something is wrong — either a wrong rename, a missing battery, or a dispatcher bug. Investigate before relaxing the tolerance.

### Other countries (informational)

27 jurisdictions × 49 indicators × 1 vintage = 1,323 cells. Tests are `pytest.mark.xfail` with reason="non-US jurisdiction; informational only".

### US states — cross-rubric only

50 states × 49 in-scope 2024 indicators × 1 vintage = 2,450 projected cells, **none with FOCAL-published ground truth**. The cross-rubric harness (next section) validates shared-row projections.

### Cross-rubric overlap harness

For each row FOCAL shares with another Phase C-shipped module, project a sample of states through both modules; assert per-item agreement at the binary contributing-value layer. Existing test infrastructure: `tests/projections/test_cross_rubric_overlap.py`.

**Shared rows (count of cross-rubric readers per row, post-FOCAL):**

| Row | Readers | Reading rubrics |
|---|---|---|
| `lobbyist_spending_report_includes_total_compensation` | 8 | CPI + PRI + Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG + FOCAL |
| `lobbyist_spending_report_includes_compensation_broken_down_by_payer` | 6 | Sunlight + Newmark 2017 + Newmark 2005 + HG (footnote) + CPI + FOCAL |
| `lobbyist_spending_report_includes_gifts_entertainment_transport_lodging` + principal-side | 6 | PRI + Newmark 2017 + Newmark 2005 + Opheim + HG + FOCAL (bundle) |
| `lobbyist_spending_report_includes_bill_or_action_identifier` + reg-form-side | 5 | Sunlight + HG + PRI + Opheim + FOCAL contact_log.11 |
| `lobbyist_registration_threshold_compensation_dollars` | 5 | CPI (3-tier) + HG (5-tier) + Newmark 2017 / 2005 / Opheim (IS NOT NULL) + FOCAL (calibrated 3-tier) |
| `def_target_executive_agency` / `_legislative_branch` / `_governors_office` | 4-5 | CPI + Newmark 2017/2005 + Opheim + HG + FOCAL |
| `lobbyist_spending_report_includes_position_on_bill` | 3 | Sunlight + Opheim + FOCAL |
| `lobbyist_reg_form_includes_employment_type` | 2 | HG + FOCAL |
| `lobbyist_reg_form_includes_business_associations_with_officials` | 2 | HG + FOCAL |
| `lobbyist_directory_update_cadence` | 2 | HG + FOCAL |

Cross-rubric tests for FOCAL primarily validate that FOCAL reads these cells consistently with other rubrics' readings at the same axis. Vintage drift is tolerated at the per-item layer (different rubrics, different vintages, may agree on most state cells even when statutes change between vintages).

---

## Data year — same as legal-core plan

2019-2023 data window for Federal US LDA validation; US states inherit Phase D extraction vintage.

---

## Per-item mappings — N/A

This plan adds no `_ATOMIC_SPEC` entries. All 49 (2024) or 50 (2025) per-item mappings are in the 3 companion plans.

## Top-level projection function

```python
def project_focal_2024(
    cells: dict[str, dict[str, Any]],
    jurisdiction: str,
    vintage: int = 2024,
    *,
    calibration: ScopeCalibration | None = None,
) -> Focal2024Score:
    """Project FOCAL 2024 score for a jurisdiction × vintage.

    Args:
        cells: v2 compendium cells for the jurisdiction (output of compendium loader filtered to state/Federal_US).
        jurisdiction: USPS state code or "Federal_US".
        vintage: 2024 (default; original Lacy-Nichols 2024 framework) or 2025 (Lacy-Nichols 2025 application
            with timeliness.1+.2 merged + "Lobbyist list" added to relationships).
        calibration: scope.2 cutoff calibration (defaults to LOW_DOLLAR_CUTOFF=1000, LOW_TIME_CUTOFF=5).

    Returns:
        Focal2024Score with atomic_scores, per_battery_subtotals (informational), total_raw, pct.
    """
    if calibration is None:
        calibration = DEFAULT_CALIBRATION  # LOW_DOLLAR_CUTOFF=1000, LOW_TIME_CUTOFF=5

    atomic_scores: dict[str, int] = {}
    per_battery_raw: dict[str, int] = defaultdict(int)
    max_total = 0

    for item_id, spec in _ATOMIC_SPEC.items():
        # vintage filtering
        if spec.min_vintage is not None and vintage < spec.min_vintage:
            continue
        if spec.max_vintage is not None and vintage > spec.max_vintage:
            continue
        # OOS skip
        if item_id in _OOS_ITEMS:
            continue
        raw = _project_atomic(item_id, cells, spec, calibration)
        weighted = raw * spec.weight
        atomic_scores[item_id] = raw
        battery = item_id.split(".")[0]  # e.g. "scope", "openness", etc.
        per_battery_raw[battery] += weighted
        max_total += 2 * spec.weight  # max raw per item is 2 (yes)

    total_raw = sum(per_battery_raw.values())
    pct = total_raw / max_total if max_total > 0 else 0.0

    return Focal2024Score(
        jurisdiction=jurisdiction,
        vintage=vintage,
        atomic_scores=atomic_scores,
        per_battery_subtotals=dict(per_battery_raw),
        total_raw=total_raw,
        pct=pct,
        max_total=max_total,  # informational; varies per vintage (180 for 2024 / 186 for 2025)
    )
```

## Ranking function

```python
def rank_focal_2024_jurisdictions(scores: list[Focal2024Score]) -> list[tuple[str, int]]:
    """Competition (1224) ranking by total_raw descending; tie-break on jurisdiction USPS code alphabetic."""
    sorted_scores = sorted(scores, key=lambda s: (-s.total_raw, s.jurisdiction))
    ranked: list[tuple[str, int]] = []
    prev_score: int | None = None
    rank = 0
    for i, s in enumerate(sorted_scores, start=1):
        if prev_score is None or s.total_raw != prev_score:
            rank = i
        ranked.append((s.jurisdiction, rank))
        prev_score = s.total_raw
    return ranked
```

**Cross-jurisdictional ranking:** FOCAL is the first Phase C rubric with multi-country ranking applicability (28 countries). The aggregation plan can rank the 28 countries from the L-N 2025 application + 50 US states + Federal_US = 79 jurisdictions total once US extraction lands.

---

## Standard module structure

```
src/lobby_analysis/projections/focal_2024.py        # extended with top-level + aggregation (this plan)
tests/projections/test_focal_2024_aggregation.py    # aggregation + Federal US LDA harness + ranking (this plan)
tests/projections/test_cross_rubric_overlap.py      # FOCAL cross-rubric reads extended (this plan; existing file)
```

Module additions:

- `Focal2024Score` Pydantic model is finalized here (legal-core plan introduced; this plan adds `max_total: int` field for vintage-aware accounting + ensures `total_raw` and `pct` are `Field(default=0)`-initialized).
- `DEFAULT_CALIBRATION = ScopeCalibration(low_dollar=Decimal("1000"), low_time=Decimal("5"))` module constant.
- `_project_atomic(item_id, cells, spec, calibration) -> int` dispatcher — implemented in legal-core; this plan verifies it handles all spec entries including the vintage-conditional ones.
- `project_focal_2024(cells, jurisdiction, vintage=2024, *, calibration=None) -> Focal2024Score` top-level.
- `rank_focal_2024_jurisdictions(scores)` ranking.

---

## Test structure

Per the test-driven-development skill: write all tests first, watch them fail (since none of the dispatcher entries exist yet without the companion plans), implement.

### Aggregation tests (`test_focal_2024_aggregation.py` — load-bearing for this plan)

**Federal US LDA primary test (2024 vintage):**

```python
def test_federal_us_lda_2024_aggregate_exact():
    cells = load_focal_2024_federal_us_lda_cells(VINTAGE_2024)
    score = project_focal_2024(cells, jurisdiction="Federal_US", vintage=2024)
    # Tolerance: ≤15 raw points from partly-tier collapses (see plan for breakdown)
    assert abs(score.total_raw - 81) <= 15, f"Expected ~81 raw points; got {score.total_raw}"
    # Ideal target: exact match. If achieved, tighten the tolerance in a follow-up.
    assert score.max_total == 180  # 49 in-scope 2024 indicators (50 - revolving_door.2)
    assert abs(score.pct - (81/180)) <= 0.01
```

**Federal US LDA 2025 vintage test:**

```python
def test_federal_us_lda_2025_aggregate_exact():
    cells = load_focal_2024_federal_us_lda_cells(VINTAGE_2025)
    score = project_focal_2024(cells, jurisdiction="Federal_US", vintage=2025)
    assert score.max_total == 186  # 50 in-scope 2025 indicators (49 + lobbyist_list_2025)
    # 2025 vintage gives ~87 (81 + 6 from lobbyist_list_2025 if LDA scores yes) or ~81 (if LDA scores 0)
    # User: verify which from L-N 2025 Suppl Table 5 lobbyist_list row for US
    assert abs(score.total_raw - <PUBLISHED_2025_TOTAL>) <= 15
```

**Per-battery subtotal tests** (informational, per Open Q-5 in legal-core):

```python
@pytest.mark.parametrize("battery,expected,tolerance", [
    ("scope", 6, 0),
    ("timeliness", 0, 0),
    ("openness", 27, 4),
    ("descriptors", 8, 4),
    ("revolving_door", 6, 0),
    ("relationships", 8, 6),  # FOCAL-5 ordering ambiguity
    ("financials", 16, 4),
    ("contact_log", 10, 12),  # heavy partly-tier collapse
])
def test_federal_us_lda_per_battery_subtotal(battery, expected, tolerance):
    cells = load_focal_2024_federal_us_lda_cells(VINTAGE_2024)
    score = project_focal_2024(cells, jurisdiction="Federal_US", vintage=2024)
    assert abs(score.per_battery_subtotals[battery] - expected) <= tolerance, (
        f"Battery {battery}: expected {expected} ± {tolerance}, got {score.per_battery_subtotals[battery]}"
    )
```

**Aggregation invariants:**

```python
def test_aggregation_invariants_2024(federal_us_lda_cells):
    score = project_focal_2024(federal_us_lda_cells, "Federal_US", vintage=2024)
    # total_raw = sum of per_battery_subtotals
    assert score.total_raw == sum(score.per_battery_subtotals.values())
    # atomic_scores keys cover all in-scope 2024 items (49)
    assert len(score.atomic_scores) == 49
    # All atomic scores ∈ {0, 1, 2}
    assert all(v in {0, 1, 2} for v in score.atomic_scores.values())
    # max_total = 2 × Σ weights over in-scope items = 180 for 2024
    assert score.max_total == 180


def test_aggregation_invariants_2025(federal_us_lda_cells_2025):
    score = project_focal_2024(federal_us_lda_cells_2025, "Federal_US", vintage=2025)
    assert len(score.atomic_scores) == 50  # 49 + lobbyist_list_2025
    assert score.max_total == 186  # 180 + 6 from lobbyist_list_2025 weight 3
```

**OOS skip test:**

```python
def test_oos_revolving_door_2_not_projected(federal_us_lda_cells):
    score = project_focal_2024(federal_us_lda_cells, "Federal_US", vintage=2024)
    assert "revolving_door.2" not in score.atomic_scores
```

**Ranking test:**

```python
def test_rank_28_countries():
    """Use L-N 2025 published scores; verify rank() produces the same order."""
    countries = load_all_28_countries_published_scores()  # dict[country, raw_score]
    fake_scores = [Focal2024Score(jurisdiction=c, vintage=2025, atomic_scores={}, ..., total_raw=s, ...) for c, s in countries.items()]
    ranking = rank_focal_2024_jurisdictions(fake_scores)
    # Top should be Canada (49%); bottom Netherlands (9%)
    assert ranking[0][0] in {"Canada", "Chile"}  # 49%/48%; tie-break on alphabet
    assert ranking[-1][0] == "Netherlands"
```

**Cross-rubric overlap tests (extension of `tests/projections/test_cross_rubric_overlap.py`):**

For each shared row, project a synthetic state's cell through FOCAL and through the other reading rubric(s); assert per-item agreement:

```python
@pytest.mark.parametrize("row_id,cell_value,focal_item,other_module,other_helper", [
    ("lobbyist_spending_report_includes_total_compensation", True, "financials.1", "cpi_2015_c11", "project_ind_201"),
    # ... 10 shared rows × multiple consumers each
])
def test_cross_rubric_agreement_focal_vs_other(row_id, cell_value, focal_item, other_module, other_helper):
    cells = {row_id: {"legal_availability": cell_value}}
    focal_raw = _project_atomic(focal_item, cells, _ATOMIC_SPEC[focal_item], DEFAULT_CALIBRATION)
    other_raw = getattr(import_module(f"lobby_analysis.projections.{other_module}"), other_helper)(cells)
    # Both should agree at the binary contributing-value layer (different scales OK)
    assert (focal_raw > 0) == (other_raw > 0), f"{focal_item} vs {other_module}.{other_helper}: disagree on TRUE/FALSE"
```

### Ground-truth loader tests (`test_focal_2024_ground_truth.py` — finalization)

- `load_focal_2024_per_country_reference(repo_root)` returns the full 28-country × 49-2024-indicator dict (or 50-2025-indicator dict).
- Federal US LDA row complete (49 indicators populated).
- Per-country totals match the L-N 2025 Suppl Table 5 published values for 5 spot-checked countries.
- 2025-only indicator (`relationships.lobbyist_list_2025`) maps to the per-country CSV's 2025-numbering `lobbyist_list` column.

---

## Open questions for the implementing agent

3 questions surfaced; confirm before launch:

1. **Federal US LDA aggregate tolerance — exact match or ±15?**
   - Partly-tier collapses produce systematic over-scoring (~+10 from contact_log, +3 from openness, +4 from descriptors, +2 from financials, +6 from relationships = ~+25 worst case). But not all states/jurisdictions trigger every partly tier — actual deltas may be smaller.
   - **Recommendation:** ship with `abs(projected - 81) ≤ 15` tolerance; record actual projected value in the validation results doc; tighten in a follow-up if the actual delta is consistently smaller.
   - **STOP clause:** if projection lands at exactly 81 (best case) or outside [66, 96] (worst case + dispatcher bug), surface to user.

2. **Cross-rubric harness scope — full pairwise or sampled?**
   - 10 shared rows × ~3-5 readers each = ~30-50 pairwise FOCAL-vs-other checks. Each check is fast (< 1ms per cell) but doubles the test count.
   - **Recommendation:** ship the full pairwise harness — Phase 4's cross-rubric audit benefits from comprehensive coverage. If test runtime balloons, parameterize at the row level (one test per row, all reader-pairs as sub-asserts).

3. **2025 vintage US LDA verification — does the per-country CSV include `lobbyist_list` for US?**
   - L-N 2025 documents the 2025-only "Lobbyist list" indicator as part of the relationships battery; the per-country CSV should have a column for it. Verify before coding the 2025 test.
   - **Recommendation:** open the CSV header and confirm. If present, populate the expected 2025 US LDA total accordingly (81 + LDA's `lobbyist_list` raw × 3; expect raw 1 partly = +3 → total 84 if LDA partially lists employed lobbyists per LD-1 employee section; otherwise 81 unchanged). If absent, mark the 2025 test as `pytest.mark.xfail`.

---

## Phase 3 retirements

No prior FOCAL implementation exists. Skip Phase 3.

---

## Phase 4 cross-rubric agreement audit feed

After FOCAL (all 4 plans) lands, Phase 4 cross-rubric audit becomes substantially more powerful:

- **8 of 9 Phase C projection modules shipped** (CPI + PRI + Sunlight + Newmark 2017 + Newmark 2005 + Opheim [blocked] + HG + FOCAL = 7 active + 1 blocked + 0 remaining for score-projection).
- **`lobbyist_spending_report_includes_total_compensation` reaches 7-module-confirmed** at the projection layer (Opheim blocked; if Opheim ships later, → 8-module).
- LobbyView schema-coverage check (the 9th Phase B mapping, not a score-projection) is the remaining Phase B + Phase C work after FOCAL lands.

Phase 4 prototype shape: per shared row, per state, build a per-state per-row "agreement matrix" — does every reading module score the same (0 or non-0) on the row? Disagreements surface as cells worth manual review (extraction issue vs projection-rule issue).

---

## Sequencing notes for Sub-4

- This plan **must launch fourth (last)** in the FOCAL sequence.
- Estimated implementation time: medium — ~10 test methods + aggregation function + ranking + cross-rubric harness extension. ~200-250 LOC. Likely 1 session.
- **No new helpers shared back to other modules.**

---

## Closing the loop (Phase C completion)

This is the **final plan in Phase C's score-projection work** (Opheim blocked is a separate question; HG ships in parallel). After all 4 FOCAL plans + HG plan ship:

- **Phase C is 7 of 8 score-projection rubrics complete** (CPI + PRI + Sunlight + Newmark 2017 + Newmark 2005 + HG + FOCAL = 7; Opheim still blocked on 1988-89 statute data).
- **Phase 4 cross-rubric agreement audit** is the natural next research line.
- **The `phase-c-projection-tdd` branch's primary deliverables are complete** at FOCAL landing; merge to main per user direction.

End-of-Phase-C checklist:

1. Convo file at `convos/YYYYMMDD_focal_2024_tdd.md` — covers all 4 FOCAL plans' implementation sessions OR each plan has its own convo (implementing agent's choice; recommend per-plan for finer history).
2. Results doc at `results/YYYYMMDD_focal_2024_projection.md` — Federal US LDA validation outcome (raw points + per-battery subtotals + tolerance results), cross-rubric audit prototype outputs, items skipped per YAGNI.
3. RESEARCH_LOG.md entry — links to convos + results, topics, findings, decisions, **branch-closure note** ("Phase C 7-of-8 complete; Opheim blocked").
4. STATUS.md — update `phase-c-projection-tdd` row to `7 of 8 rubrics shipped (Opheim blocked); ready for Phase 4 audit research line or merge`.
5. README.md — update if the rubric landings retire any code visible at the README level.
6. Commit + push per plan. Final commit message: `convo: <convo-name> — focal_2024: aggregation + Federal US LDA harness shipped; Phase C 7-of-8 complete`.

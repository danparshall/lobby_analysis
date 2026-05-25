# FOCAL 2024 — Openness + Timeliness Batteries Projection Implementation Plan

**Goal:** Extend the `focal_2024` module skeleton (created in [`20260518_focal_2024_legal_core_plan.md`](20260518_focal_2024_legal_core_plan.md)) with the openness battery (9 items) + timeliness battery (3 items → 2 effective after 2025 merge) = **12 items**. Openness is FOCAL's **practical-availability backbone** (portal observables), strong overlap with PRI accessibility / CPI #205-206 / HG Q28-Q38. Timeliness has 1 merged-in-2025 indicator + 1 parliamentary-N/A item for US jurisdictions. All 12 items land in the same `focal_2024.py` module via additions to `_ATOMIC_SPEC`.

**Originating conversation:** [`../convos/20260518_focal_hg_plans_drafting.md`](../convos/20260518_focal_hg_plans_drafting.md) (Sub-3 of Phase C — FOCAL plan-set + HG plan with retrieval gate). Companion plan in the 4-plan FOCAL set:

- [`20260518_focal_2024_legal_core_plan.md`](20260518_focal_2024_legal_core_plan.md) — **must land first** (introduces module skeleton).
- [`20260518_focal_2024_contact_log_plan.md`](20260518_focal_2024_contact_log_plan.md) — same session, contact_log battery.
- [`20260518_focal_2024_aggregation_plan.md`](20260518_focal_2024_aggregation_plan.md) — same session, weighted aggregation + Federal US LDA validation harness.

**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md) — openness section (lines 237-369), timeliness section (lines 202-234). The plan below is **derivative**; read the spec for source quotes and per-item Suppl Table 3 P/N notes.

**Context:** This plan covers FOCAL's practical-axis backbone (openness) and the small timeliness battery. Openness has the most cross-rubric overlap of any FOCAL battery (5 of 9 items reuse pre-existing v2 rows from PRI / CPI / HG); timeliness has 1 cross-rubric reuse (HG Q38) and 2 parliamentary-N/A items.

**Confidence:** High on openness — paper-explicit, 5 reused rows with confirmed v2 names. Medium on timeliness — 2 of 3 items are parliamentary-system observables (ministerial diaries) that score 0 for US jurisdictions; the data signal is structural-zero, not informative variation. The merged 2025 timeliness.1+.2 indicator is straightforward (reads HG Q38's cadence cell).

**Architecture:** Adds 12 entries to `_ATOMIC_SPEC` (with 1 timeliness merge collapsing 2 spec items into 1 dispatcher entry). 2 named helpers for the openness partly-tier conditional reads (openness.3 4-AND + openness.8 historical-archive-AND-downloadable). Introduces the **`practical_availability` axis** for FOCAL — first FOCAL battery to read non-legal-axis cells. The aggregation plan (Plan 4) handles the axis-distinction in the per-battery subtotal accounting.

**Branch:** `phase-c-projection-tdd` (worktree at `.worktrees/phase-c-projection-tdd`).

**Tech Stack:** Python 3.12, Pydantic v2, pytest, `uv` for env management.

---

## Cross-plan ordering — landed third (after legal core + contact log)

Sequence within FOCAL plan-set:

1. Legal core (creates module skeleton)
2. Contact log (extends dispatcher)
3. **Openness + timeliness (this plan)** — extends dispatcher, adds practical-axis convention
4. Aggregation — wires top-level + Federal US LDA harness

This plan modifies `focal_2024.py` by extending `_ATOMIC_ITEMS_OPENNESS_TIMELINESS` (placeholder defined in legal-core plan) and appending 11 entries to `_ATOMIC_SPEC` (3 timeliness items collapse to 2 dispatcher entries via the 2025 merge). **Does not redefine the score model or top-level function.**

---

## Scope qualifier — 0 items OUT

All 9 openness items + all 3 timeliness items are in scope.

**Timeliness 2025 merge:** L-N 2025 merged `timeliness.1` + `timeliness.2` (both 2024 numbering) into one 2025 indicator. Both 2024 indicators read the **same compendium cell** (`lobbyist_directory_update_cadence`), so the merge is at the projection layer: produce a single `timeliness_1_2_merged` score for 2025 vintage, two separate scores for 2024 vintage. **Both vintages use the same per-item helper** (4-tier cadence read); the merge changes only the aggregation accounting.

---

## Validation regime — Cross-rubric only (US states); Strong (US LDA federal)

Inherits from the FOCAL legal-core plan. Battery-specifics:

- **US LDA Federal validation** (load-bearing): per the audit doc breakdown, US LDA per-battery subtotals are:
  - Timeliness: 0+0 = **0** (US LDA scored 0 on both 2024 items; merged 2025 indicator also scores 0)
  - Openness: 4+0+6+3+6+2+2+2+2 = **27** (LDA's portal infrastructure is well-developed)

  Per-indicator targets:
  - openness.1 (register online) = 4 (raw 2 × weight 2)
  - openness.2 (diaries online) = 0 (US has no ministerial diaries)
  - openness.3 (no registration / free / open license / non-proprietary / machine readable bundle) = 6 (raw 2 × weight 3)
  - openness.4 (downloadable) = 3 (raw 1 × weight 3 = partly; LDA "some data not captured")
  - openness.5 (searchable multi-criteria) = 6 (raw 2 × weight 3)
  - openness.6 (unique identifiers) = 2 (raw 2 × weight 1)
  - openness.7 (linked/interconnected data) = 2 (raw 2 × weight 1)
  - openness.8 (historical archive downloadable) = 2 (raw 2 × weight 1)
  - openness.9 (changes flagged with versioning) = 2 (raw 2 × weight 1)
  - timeliness.1 (changes near-real-time) = 0
  - timeliness.2 (lobbying activities near-real-time) = 0
  - timeliness.3 (ministerial diaries monthly) = 0

- **US states validation:** no per-state US ground truth. Cross-rubric is the only check; 5 of 9 openness items reuse existing rows (cross-validatable against PRI/CPI/HG); the other 4 openness items + 2 timeliness items are FOCAL-distinctive or parliamentary-N/A.

**Validation tolerance:**

- **Federal US LDA per-indicator:** `==` exact match for binary projections (openness.1, .2, .5, .6, .7, .9; timeliness.1, .2, .3). 
- **Partly-tier indicators** (openness.3, .4, .8 + relationships.* + descriptors.*): **deviation expected**.
  - openness.4 partly tier ("some data not captured") not extractable from v2; binary projection gives 6 (raw 2 × weight 3 = yes) vs published 3 (partly). Over-scoring +3 raw points.
  - openness.3 partly tier ("proprietary format e.g. excel") needs `lobbying_data_proprietary_format_flag` cell — not in v2; binary AND-projection over 4 cells gives 6 if all TRUE; matches published 6 for US LDA where all 4 conditions hold. Likely no over-scoring for US.
  - openness.8 partly tier ("not downloadable at once") needs to read the historical-archive + downloadable cells AND; binary projection gives 2 if both TRUE; matches published 2 for US LDA. Likely no over-scoring for US.
- **Federal US LDA per-battery subtotal:** Openness projects to ~30 vs published 27 (~+3 from openness.4 over-scoring); Timeliness projects to 0 vs published 0 (exact). Plan 4's Federal US LDA test uses `abs(projected_openness_subtotal - published) ≤ 4` tolerance.

### Practical-availability axis introduction

This plan is the first FOCAL battery to read practical-availability cells (openness.1-.9 all practical; timeliness.1-.3 all practical). The score model and `_ATOMIC_SPEC` infrastructure introduced in legal-core already support the axis split via the per-spec-entry axis field. **No new axis machinery required.**

The legal-core plan's `_LEGAL = "legal_availability"` and `_PRACTICAL = "practical_availability"` constants are used by this plan's spec entries. **Per-battery subtotal accounting** (in Plan 4) sums per-axis raw scores separately for diagnostics but the FOCAL published total is a single weighted sum across both axes.

---

## Data year — 2024 framework, 2019-2023 data window for US LDA validation (HIGH confidence)

Same as legal-core plan. Practical-availability cells in this plan reflect portal state at extraction time, not statute snapshot — vintage discipline differs slightly: for openness/timeliness, the "extraction window" is when the portal was last observed, which for L-N 2025 was 2019-2023. **Phase D extraction must record the portal-observation timestamp** for each openness/timeliness cell.

---

## Per-item mappings

### Spec-doc → v2 row-name rename mapping

Phase 0 cross-check surfaced **1 rename** affecting this battery:

| Spec doc working name | v2 compendium row id | Rename family |
|---|---|---|
| `ministerial_diaries_available_online` | `ministerial_diary_available_online` | singular `diary` in v2 (parallel to `ministerial_diary_disclosure_cadence` from timeliness.3) |

The other 11 v2 rows match the spec-doc working names exactly. Carry this rename in the module-level rename comment block.

### Openness battery (9 items, all in scope; weights 2+1+3+3+3+1+1+1+1)

| FOCAL item | Wt | v2 row(s) | Read shape | Notes |
|---|---|---|---|---|
| openness.1 (register online) | 2 | `state_has_dedicated_lobbying_website` | binary → 2 | partly tier collapsed (Open Q-1); reused PRI row |
| openness.2 (diaries online) | 1 | `ministerial_diary_available_online` | binary → 2 | parliamentary-N/A for US; structural-zero |
| openness.3 (no-reg + free + open license + non-prop + machine-readable bundle) | 3 | 4 binary cells: `lobbying_data_no_user_registration_required` AND `lobbying_disclosure_documents_free_to_access` AND `lobbying_data_open_license` AND `lobbying_data_downloadable_in_analytical_format` | named helper — 4-AND 3-tier (partly tier collapsed) |
| openness.4 (downloadable) | 3 | `lobbying_data_downloadable_in_analytical_format` | binary → 2 (partly tier collapsed; reuses openness.3's downloadable cell) | reused PRI row |
| openness.5 (searchable multi-criteria) | 3 | `lobbying_search_simultaneous_multicriteria_capability` (typed int 0-15) | typed 3-tier (`>= 4 → 2; 1..3 → 1; 0 → 0`) | reused PRI row |
| openness.6 (unique identifiers) | 1 | `lobbying_disclosure_data_includes_unique_identifiers` (typed Set[enum]) | typed `IS NOT NULL → 2` (partly tier collapsed) | NEW row |
| openness.7 (linked/interconnected data) | 1 | `lobbying_disclosure_data_linked_to_other_datasets` (typed Set[enum]) | typed `IS NOT NULL → 2` | NEW row |
| openness.8 (historical archive downloadable) | 1 | `lobbying_data_historical_archive_present` AND `lobbying_data_downloadable_in_analytical_format` | named helper — 2-AND 3-tier | reused PRI row |
| openness.9 (versioning) | 1 | `lobbying_data_changes_flagged_with_versioning` | binary → 2 | NEW row |

**Named helpers** for openness.3 (4-AND) and openness.8 (2-AND):

```python
def _project_focal_openness_3(cells) -> int:
    """4-criteria AND on practical-axis cells; partly tier collapsed to binary."""
    no_reg = bool(cells.get("lobbying_data_no_user_registration_required", {}).get("practical_availability"))
    free = bool(cells.get("lobbying_disclosure_documents_free_to_access", {}).get("practical_availability"))
    open_lic = bool(cells.get("lobbying_data_open_license", {}).get("practical_availability"))
    machine = bool(cells.get("lobbying_data_downloadable_in_analytical_format", {}).get("practical_availability"))
    # FOCAL's "partly = proprietary format (e.g. excel)" tier is not extractable from v2; collapse to binary AND
    if no_reg and free and open_lic and machine:
        return 2
    return 0


def _project_focal_openness_8(cells) -> int:
    """Historical archive AND downloadable; partly tier collapsed to binary."""
    archive = bool(cells.get("lobbying_data_historical_archive_present", {}).get("practical_availability"))
    downloadable = bool(cells.get("lobbying_data_downloadable_in_analytical_format", {}).get("practical_availability"))
    if archive and downloadable:
        return 2
    if archive and not downloadable:
        return 1  # partly: "not downloadable at once"
    return 0
```

**Note on openness.8 partly tier:** unlike most partly tiers in FOCAL, this one IS operationally readable — it reads the AND/AND-NOT pattern over two existing cells. Keep the 3-tier projection.

**Named helper for openness.5** (typed int 3-tier):

```python
def _project_focal_openness_5(cells) -> int:
    cap = cells.get("lobbying_search_simultaneous_multicriteria_capability", {}).get("practical_availability")
    if cap is None:
        return 0
    cap_int = int(cap)
    if cap_int >= 4:
        return 2
    if cap_int >= 1:
        return 1
    return 0
```

### Timeliness battery (3 items → 2 effective after 2025 merge; weights 3+3+1)

| FOCAL item | Wt | v2 row | Read shape | Notes |
|---|---|---|---|---|
| timeliness.1 (changes near-real-time) | 3 | `lobbyist_directory_update_cadence` (typed enum) | named helper — cadence 3-tier | reused HG Q38 row; merged with timeliness.2 in 2025 |
| timeliness.2 (activities near-real-time) | 3 | `lobbyist_directory_update_cadence` (same cell) | named helper — same as timeliness.1 | merged with timeliness.1 in 2025 |
| timeliness.3 (ministerial diaries monthly) | 1 | `ministerial_diary_disclosure_cadence` (typed enum) | named helper — cadence 3-tier | parliamentary-N/A for US |

**Named helper for cadence 3-tier reads** (shared by timeliness.1, .2, .3):

```python
def _project_focal_cadence_3tier(cells, row_id: str) -> int:
    """3-tier cadence: daily → 2; weekly|monthly → 1; semiannual_or_less|none → 0."""
    cad = cells.get(row_id, {}).get("practical_availability")
    if cad is None or cad in ("none", "semiannual_or_less_often", "less_than_quarterly", "no_diary_published", "none_required"):
        return 0
    if cad in ("weekly", "monthly", "monthly_or_more", "quarterly"):
        return 1
    if cad == "daily":
        return 2
    return 0  # unknown enum value defaults to 0
```

**2024-vs-2025 vintage handling:** the dispatcher applies a `min_vintage` / `max_vintage` per spec entry:

```python
_ATOMIC_SPEC.update({
    "timeliness.1": Spec(("lobbyist_directory_update_cadence",), _PRACTICAL, weight=3, helper="cadence_3tier", min_vintage=None, max_vintage=2024),
    "timeliness.2": Spec(("lobbyist_directory_update_cadence",), _PRACTICAL, weight=3, helper="cadence_3tier", min_vintage=None, max_vintage=2024),
    "timeliness.1_2_merged_2025": Spec(("lobbyist_directory_update_cadence",), _PRACTICAL, weight=3, helper="cadence_3tier", min_vintage=2025, max_vintage=None),
    "timeliness.3": Spec(("ministerial_diary_disclosure_cadence",), _PRACTICAL, weight=1, helper="cadence_3tier", min_vintage=None, max_vintage=None),
})
```

The dispatcher's vintage filter (introduced in legal-core for `relationships.lobbyist_list_2025`) skips items where `current_vintage` is outside `[min_vintage, max_vintage]`. For 2024 vintage: timeliness.1 + .2 scored separately (max raw = 6 + 6 = 12 with weight); for 2025: timeliness.1_2_merged_2025 scored once (max raw = 6 with weight 3). The merged 2025 weight stays 3 per L-N 2025 paper.

**Total weighted-max contribution per vintage:**
- 2024: 2×(2+1+3+3+3+1+1+1+1+3+3+1) = 2×23 = 46 raw points from this plan's 12 items
- 2025: 2×(2+1+3+3+3+1+1+1+1+3+1) = 2×20 = 40 raw points (1 fewer indicator due to merge)

---

## Standard module structure

This plan only **extends** `focal_2024.py`. Test additions:

```
tests/projections/test_focal_2024_per_item.py       # extends with openness + timeliness subset (this plan)
tests/projections/test_focal_2024_ground_truth.py   # extends with openness + timeliness indicator reads (this plan)
```

Module additions:

- `_ATOMIC_ITEMS_OPENNESS_TIMELINESS: tuple[str, ...] = ("openness.1", ..., "openness.9", "timeliness.1", "timeliness.2", "timeliness.1_2_merged_2025", "timeliness.3")` (12 IDs, +1 vintage-conditional).
- 12 entries appended to `_ATOMIC_SPEC` (with the 2024 / 2025 vintage gating).
- 3 named helpers: `_project_focal_openness_3`, `_project_focal_openness_8`, `_project_focal_openness_5`, `_project_focal_cadence_3tier` (4 helpers total; openness.5 is also a helper).
- Helper-name handlers `"cadence_3tier"` added to the dispatcher's `_project_atomic`.

---

## Test structure

### Per-item tests (`test_focal_2024_per_item.py` — openness + timeliness extension)

- **openness.1, .2, .4, .9** (binary reads): parameterize each over `{TRUE, FALSE, missing}` → expected `{2, 0, 0}`. 4 × 3 = 12 cells.
- **openness.3** (4-AND): parameterize over `2^4 = 16` truth-table cases; expected `{2 if all True else 0}`. 16 cells.
- **openness.5** (typed int 3-tier): parameterize over `{None, 0, 1, 3, 4, 10, 15}` → expected `{0, 0, 1, 1, 2, 2, 2}`. 7 cells.
- **openness.6, .7** (typed `IS NOT NULL`): parameterize each over `{set, empty_set, None}` → expected `{2, 0, 0}`. 6 cells.
- **openness.8** (2-AND with partly): parameterize over `2^2 = 4` cases; expected `{2 if both, 1 if archive only, 0 otherwise}`. 4 cells.
- **timeliness.1, .2, .3** (cadence 3-tier): parameterize over `{"daily", "weekly", "monthly", "semiannual_or_less_often", "none", None}` → expected `{2, 1, 1, 0, 0, 0}`. 3 × 6 = 18 cells.
- **timeliness 2024-vs-2025 vintage filter:** 4 cases — (vintage=2024, item=.1) → scored; (vintage=2024, item=.1_2_merged_2025) → NOT scored; (vintage=2025, item=.1) → NOT scored; (vintage=2025, item=.1_2_merged_2025) → scored. 4 cells.

**Estimated cells:** 12 + 16 + 7 + 6 + 4 + 18 + 4 = **67 per-item truth-table cells for openness + timeliness.**

### Ground-truth loader tests (`test_focal_2024_ground_truth.py` — openness + timeliness extension)

- Federal US LDA row contains 12 indicators with values per the spec-doc breakdown.
- Per-indicator value-range bounds (each indicator ∈ {0, 1, 2}).
- Spot-check non-US: Netherlands (low openness — 9% total includes near-zero openness subtotal) and Canada (high openness — 49% total includes near-max openness subtotal).
- **2025-vintage merged indicator** read from per-country CSV: confirm the per-country CSV uses `timeliness.1` as the 2025 numbering merged column (timeliness.2 is null/merged per spec doc line 115-116).

### Cross-rubric overlap tests (extension)

5 of 9 openness items reuse existing v2 rows:

- `state_has_dedicated_lobbying_website` (openness.1) — reused PRI Q2 row.
- `lobbying_data_downloadable_in_analytical_format` (openness.3 + .4) — reused PRI Q6 row.
- `lobbying_disclosure_documents_free_to_access` (openness.3) — reused CPI #205 derivative row.
- `lobbying_search_simultaneous_multicriteria_capability` (openness.5) — reused PRI Q8 row.
- `lobbying_data_historical_archive_present` (openness.8) — reused PRI Q5 row.

Plus 1 of 3 timeliness items:

- `lobbyist_directory_update_cadence` (timeliness.1 + .2 / merged) — reused HG Q38 row (once HG ships).

Cross-rubric agreement tests: for each shared row, project a synthetic state through both FOCAL and the other module(s) reading the same cell; assert per-item agreement at the binary (or appropriate tier) layer.

---

## Open questions for the implementing agent

3 questions surfaced; confirm before launch:

1. **openness.1 partly tier ("optional registration or separate websites").** FOCAL spec doc Open Issue FOCAL-3 — partly tier reads a derived condition over additional cells not in v2 (`lobbyist_registration_optional_for_some_actor_types`, `lobbyist_registration_split_across_websites_by_actor_type`).
   - **Recommendation:** YAGNI — project at binary granularity. Federal US LDA scored 4 (yes) per binary projection, matches published. State-level over-scoring may occur for states with optional / split registration; Phase D extraction may surface these. **STOP clause:** if Phase D extraction surfaces meaningful state variation on this partly tier and projection over-scoring is material (>2 raw points per state on average), propose adding the 2 partly-tier cells to compendium 2.0 freeze.

2. **openness.6 partly tier ("only business IDs").** FOCAL spec doc partly tier reads `cell == {business_registration_id} ONLY → 1`. The v2 cell is typed `Set[enum]` so this read IS operationally possible.
   - **Recommendation:** ship the 3-tier projection (not collapsed to binary):

   ```python
   def _project_focal_openness_6(cells) -> int:
       ids = cells.get("lobbying_disclosure_data_includes_unique_identifiers", {}).get("practical_availability")
       if ids is None or len(ids) == 0:
           return 0
       if set(ids) == {"business_registration_id"}:
           return 1
       # presence of any lobbyist_id / individual_id / organization_id beyond bare business_id → yes
       if {"lobbyist_id", "organization_id"} & set(ids):
           return 2
       return 1  # other partial sets
   ```

   - This is the only FOCAL partly tier in this plan that's operationally readable from v2 directly; ship the finer projection.

3. **timeliness merge 2025 indicator handling — CSV column naming.** Per spec doc line 116, the merged 2025 ground-truth cell in the per-country CSV is named `timeliness.1` (2025 numbering); `timeliness.2` (2024 numbering) is null in 2025.
   - **Recommendation:** ground-truth loader maps the CSV's `timeliness.1` column to the dispatcher's `timeliness.1_2_merged_2025` item ID for 2025-vintage projections, OR to `timeliness.1` item ID for 2024-vintage projections. Vintage-aware loader logic; document with a docstring example.
   - **Verification task:** open the per-country CSV header and confirm the column naming before coding the loader. If the CSV uses a different convention (e.g., `timeliness.1_2_merged`), adjust the dispatcher's item ID accordingly.

---

## Phase 4 cross-rubric agreement audit feed

After openness + timeliness lands (alongside the other 3 FOCAL plans):

- `state_has_dedicated_lobbying_website` → **3-rubric-confirmed** (PRI + HG Q31 + FOCAL openness.1; HG Q31 reads the binary indirectly via the `_directory_available_as_*` family).
- `lobbying_data_downloadable_in_analytical_format` → **4-rubric-confirmed** (PRI Q6 + CPI #206 + HG Q31/Q32 tier-4 + FOCAL openness.3+.4). Most cross-rubric-confirmed practical-axis row.
- `lobbying_data_historical_archive_present` → **2-rubric-confirmed** (PRI Q5 + FOCAL openness.8).
- `lobbyist_directory_update_cadence` → **2-rubric-confirmed** (HG Q38 + FOCAL timeliness.1+.2-merged) once HG ships.
- 5 NEW FOCAL practical-axis rows become single-rubric-confirmed (FOCAL-distinctive).

---

## Sequencing notes for Sub-4

- This plan **must launch third** in the FOCAL sequence (after legal core + contact log).
- No cross-rubric helper imports; helpers introduced here are FOCAL-specific.
- Estimated implementation time: medium — 67 truth-table cells + 12 dispatcher entries + 4 named helpers + extended ground-truth loader. ~250-300 LOC. Likely 1 session.

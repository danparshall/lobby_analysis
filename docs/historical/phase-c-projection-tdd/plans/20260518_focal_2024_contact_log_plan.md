# FOCAL 2024 — Contact Log Battery Projection Implementation Plan

**Goal:** Extend the `focal_2024` module skeleton (created in [`20260518_focal_2024_legal_core_plan.md`](20260518_focal_2024_legal_core_plan.md)) with the 11 contact_log atomic items. Contact log is FOCAL's **most-distinctive battery** — 9 of 11 items introduce NEW v2 rows that no other contributing rubric reads at per-meeting granularity. All 11 items land in the same `focal_2024.py` module via additions to `_ATOMIC_SPEC`.

**Originating conversation:** [`../convos/20260518_focal_hg_plans_drafting.md`](../convos/20260518_focal_hg_plans_drafting.md) (Sub-3 of Phase C — FOCAL plan-set + HG plan with retrieval gate). Companion plan in the 4-plan FOCAL set:

- [`20260518_focal_2024_legal_core_plan.md`](20260518_focal_2024_legal_core_plan.md) — **must land first** (introduces module skeleton, score model, dispatcher dict).
- [`20260518_focal_2024_openness_timeliness_plan.md`](20260518_focal_2024_openness_timeliness_plan.md) — same session, openness + timeliness batteries.
- [`20260518_focal_2024_aggregation_plan.md`](20260518_focal_2024_aggregation_plan.md) — same session, weighted aggregation + Federal US LDA validation harness + ranking.

**Spec doc:** [`../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md`](../../../historical/compendium-source-extracts/results/projections/focal_2024_projection_mapping.md) — contact_log section (lines 653-764). The plan below is **derivative**; read the spec for source quotes and per-item Suppl Table 3 P/N notes.

**Context:** Rubric #8 in Phase C's locked rubric order; this plan covers the contact_log battery only. The legal-core plan covers scope/descriptors/relationships/revolving_door/financials; the openness+timeliness plan covers practical-axis observables; the aggregation plan covers the weighted sum + Federal US LDA validation harness.

**Confidence:** High. Contact log items are all read at near-uniform binary granularity (10 of 11 are binary; 1 is typed enum with `IS NOT NULL` read). 9 of 11 v2 rows are NEW — confirmed present in v2 via Phase 0 cross-check (no renames; all matched exactly under the spec-doc working names). The FOCAL "partly" tier ("P=some entries incomplete") is the same data-quality observable as descriptors; YAGNI-collapse to binary per the legal-core plan's Open Q-3 convention.

**Architecture:** Adds 11 entries to the `_ATOMIC_SPEC` dispatcher dict introduced by the legal-core plan. No new helpers; the standard binary-read default (`bool(cells.get(row, {}).get(axis)) → 2 if TRUE else 0`) handles 10 of 11 items. One typed `IS NOT NULL` read for contact_log.6 (communication form enum). **Adds the practical-vs-legal axis split note** — contact log items are all `legal_availability` (statute-readable: does the state require these disclosures on lobbying activity reports?).

**Branch:** `phase-c-projection-tdd` (worktree at `.worktrees/phase-c-projection-tdd`).

**Tech Stack:** Python 3.12, Pydantic v2, pytest, `uv` for env management.

---

## Cross-plan ordering — landed second (after legal core)

Sequence within FOCAL plan-set:

1. Legal core (creates module skeleton)
2. **Contact log (this plan)** — adds 11 items to `_ATOMIC_SPEC`
3. Openness + timeliness — adds 12 items
4. Aggregation — wires top-level + Federal US LDA harness

This plan modifies `focal_2024.py` by extending `_ATOMIC_ITEMS_CONTACT_LOG` (defined as empty placeholder in legal-core plan) and appending 11 entries to `_ATOMIC_SPEC`. **Does not redefine the score model or top-level function.**

---

## Scope qualifier — 0 items OUT

All 11 contact_log items are in scope. No scope-qualifier exclusions in this battery.

---

## Validation regime — Cross-rubric only (US states); Strong (US LDA federal)

Inherits from the FOCAL legal-core plan's regime. Contact log specifics:

- **US LDA Federal validation** (load-bearing): 11 indicator-level reads from L-N 2025 per-country CSV. Per the audit doc breakdown, US LDA Contact_log subtotal = **10** (raw points contributing to the 81 total); per-indicator values per the spec doc:
  - contact_log.1 (organisation/interest represented) = 2 (raw 1 × weight 2 = partly)
  - contact_log.2 (names of persons contacted) = 0 (LDA doesn't list specific officials)
  - contact_log.3 (institution/department) = 2 (partly — chambers + agencies but not departments)
  - contact_log.4 (meeting attendees) = 0 (not per-meeting)
  - contact_log.5 (date) = 0 (not per-meeting)
  - contact_log.6 (form) = 0
  - contact_log.7 (location) = 0
  - contact_log.8 (materials shared) = 0
  - contact_log.9 (topics discussed) = 3 (raw 1 × weight 3 = partly; LDA "Specific lobbying issues" at quarterly granularity)
  - contact_log.10 (outcomes/position on bill) = 0 (LDA doesn't require position)
  - contact_log.11 (bill numbers) = 3 (raw 1 × weight 3 = partly; LDA "Specific bills" at quarterly granularity)
  - **Total: 0+0+2+2+0+0+0+0+3+0+3 = 10** ✓ matches audit doc.

- **US states validation:** no per-state US ground truth. Cross-rubric is the only check, but contact_log has minimal cross-rubric overlap — only 2 of 11 items reuse existing v2 rows. The 9 NEW contact_log rows are FOCAL-distinctive in the contributing-rubric set at per-meeting granularity. **Empirical expectation:** US states will populate the 9 contact_log NEW rows as FALSE near-universally (US states largely don't require per-meeting disclosure), producing 0 per-indicator scores — a near-constant projection.

**Validation tolerance:**

- **Federal US LDA per-indicator:** `==` exact match for contact_log.1, .2, .3, .4, .5, .6, .7, .8, .10 (all binary projections; LDA is exact 0 or 2).
- **Federal US LDA partly-tier indicators (.9, .11):** **deviation expected.** FOCAL's "partly" tier (`TRUE AND vague_or_unclear → 1` for .9; `TRUE AND general_list_not_specific → 1` for .11) is not operationally readable from v2 binary cells. v2 row `lobbyist_spending_report_includes_topics_discussed` returns TRUE for LDA → binary projection gives 2; published is 1 (partly). Same for `lobbyist_spending_report_includes_bill_or_action_identifier`. **Quantified: 2 raw points over-scored vs published (1+1) → ~1.1pp percentage error.** Document in module docstring as a known partly-tier collapse.
- **Federal US LDA total:** likely projects 12 raw points vs published 10 (+2 from partly-tier over-scoring on .9 and .11). Aggregation plan's Federal US LDA test must tolerate this 2-point delta.

### Vintage discipline

Same as legal-core plan: 2019-2023 data collection window for Federal US LDA; US states inherit Phase D extraction vintage.

---

## Data year — 2024 framework, 2019-2023 data window for US LDA validation (HIGH confidence)

Same as legal-core plan. No per-battery vintage variation within FOCAL.

---

## Per-item mappings

### Spec-doc → v2 row-name rename mapping

Phase 0 cross-check confirmed **0 renames needed** for the contact_log battery; all 11 v2 rows match the spec-doc working names exactly:

| FOCAL item | Spec doc & v2 row name (no rename) |
|---|---|
| contact_log.1 | `lobbying_contact_log_includes_beneficiary_organization` |
| contact_log.2 | `lobbying_contact_log_includes_official_contacted_name` |
| contact_log.3 | `lobbying_contact_log_includes_institution_or_department` |
| contact_log.4 | `lobbying_contact_log_includes_meeting_attendees` |
| contact_log.5 | `lobbying_contact_log_includes_date` |
| contact_log.6 | `lobbying_contact_log_includes_communication_form` |
| contact_log.7 | `lobbying_contact_log_includes_location` |
| contact_log.8 | `lobbying_contact_log_includes_materials_shared` |
| contact_log.9 | `lobbying_contact_log_includes_topics_discussed` |
| contact_log.10 | `lobbyist_spending_report_includes_position_on_bill` (existing Sunlight row) |
| contact_log.11 | `lobbyist_spending_report_includes_bill_or_action_identifier` (existing Sunlight row) |

### Contact log battery spec entries (11 items, all in scope; weights mixed)

| FOCAL item | Wt | v2 row | Read shape | Notes |
|---|---|---|---|---|
| contact_log.1 (org/interest represented) | 2 | `lobbying_contact_log_includes_beneficiary_organization` | binary → 2 | NEW row |
| contact_log.2 (names of persons contacted) | 2 | `lobbying_contact_log_includes_official_contacted_name` | binary → 2 | NEW row |
| contact_log.3 (institution/dept) | 2 | `lobbying_contact_log_includes_institution_or_department` | binary → 2 | NEW row |
| contact_log.4 (meeting attendees) | 1 | `lobbying_contact_log_includes_meeting_attendees` | binary → 2 | NEW row |
| contact_log.5 (date) | 2 | `lobbying_contact_log_includes_date` | binary → 2 | NEW row |
| contact_log.6 (form: in-person/video/phone) | 2 | `lobbying_contact_log_includes_communication_form` (typed enum) | typed `IS NOT NULL → 2` | NEW row |
| contact_log.7 (location) | 1 | `lobbying_contact_log_includes_location` | binary → 2 | NEW row |
| contact_log.8 (materials shared) | 1 | `lobbying_contact_log_includes_materials_shared` | binary → 2 | NEW row |
| contact_log.9 (topics discussed) | 3 | `lobbying_contact_log_includes_topics_discussed` | binary → 2 (partly tier collapsed) | NEW row; Open Q-1 |
| contact_log.10 (outcomes/position on bill) | 3 | `lobbyist_spending_report_includes_position_on_bill` | binary → 2 (partly tier collapsed) | reused Sunlight row |
| contact_log.11 (bill numbers/legislation) | 3 | `lobbyist_spending_report_includes_bill_or_action_identifier` OR `lobbyist_reg_form_includes_bill_or_action_identifier` | OR binary → 2 (partly tier collapsed) | reused Sunlight α-split family; Open Q-2 |

**No named helpers required** — 10 of 11 items use the default binary-read; 1 uses the default typed `IS NOT NULL`. The spec entries:

```python
_ATOMIC_SPEC.update({
    "contact_log.1": Spec(("lobbying_contact_log_includes_beneficiary_organization",), _LEGAL, weight=2, helper=None, min_vintage=None),
    "contact_log.2": Spec(("lobbying_contact_log_includes_official_contacted_name",), _LEGAL, weight=2, helper=None, min_vintage=None),
    "contact_log.3": Spec(("lobbying_contact_log_includes_institution_or_department",), _LEGAL, weight=2, helper=None, min_vintage=None),
    "contact_log.4": Spec(("lobbying_contact_log_includes_meeting_attendees",), _LEGAL, weight=1, helper=None, min_vintage=None),
    "contact_log.5": Spec(("lobbying_contact_log_includes_date",), _LEGAL, weight=2, helper=None, min_vintage=None),
    "contact_log.6": Spec(("lobbying_contact_log_includes_communication_form",), _LEGAL, weight=2, helper="is_not_null", min_vintage=None),
    "contact_log.7": Spec(("lobbying_contact_log_includes_location",), _LEGAL, weight=1, helper=None, min_vintage=None),
    "contact_log.8": Spec(("lobbying_contact_log_includes_materials_shared",), _LEGAL, weight=1, helper=None, min_vintage=None),
    "contact_log.9": Spec(("lobbying_contact_log_includes_topics_discussed",), _LEGAL, weight=3, helper=None, min_vintage=None),
    "contact_log.10": Spec(("lobbyist_spending_report_includes_position_on_bill",), _LEGAL, weight=3, helper=None, min_vintage=None),
    "contact_log.11": Spec(("lobbyist_spending_report_includes_bill_or_action_identifier", "lobbyist_reg_form_includes_bill_or_action_identifier"), _LEGAL, weight=3, helper="or_any", min_vintage=None),
})
```

**Two-helper convention** that the dispatcher must support (these are the only two non-default read shapes used in contact_log):

- `"is_not_null"` — returns 2 if cell value is non-null (typed cells); 0 if null. Default-reads convert binary `True/False/missing` to `2/0/0`.
- `"or_any"` — returns 2 if ANY of the row IDs in the tuple have a TRUE binary cell value; 0 if all FALSE/missing.

These two are generic enough to live in the module-level helper namespace (used by contact_log.6, .11 and by relationships.1, financials.10 in legal-core).

### Weighted-sum contribution for contact_log

If all 11 contact_log items projected 2 (yes), the battery contributes: `2×(2+2+2+1+2+2+1+1+3+3+3) = 2×22 = 44 raw points` to the FOCAL total. US LDA published is 10 (out of 44 max); projection target is 10+2=12 (partly-tier over-scoring on .9 and .11).

### "Partly" tier collapse (contact_log.9 and contact_log.11)

FOCAL Suppl Table 3 defines partly tiers as:

- contact_log.9: `TRUE AND specific → 2; vague_or_unclear → 1; FALSE → 0`
- contact_log.11: `(reg_form OR spending_report) AND specific_to_communication → 2; general_list → 1; FALSE → 0`

Neither sub-criterion ("specific" vs "vague_or_unclear"; "specific to communication" vs "general list") is operationally readable from v2 binary cells. **YAGNI: project at binary granularity (TRUE → 2; FALSE → 0).** Documented in module docstring; Federal US LDA validation tolerance accommodates the 2-point over-scoring (see Open Q-1).

The contact_log.1, .2, .3, .4, .5 Suppl Table 3 P/N notes ("P=some entries incomplete") are also data-quality observables not extractable from v2. Same YAGNI-collapse: binary read. For US LDA the binary projection happens to match published exactly (.1, .3 cells extract as TRUE; produce 2; published is 1+1=2 per the audit doc — wait, that's 1 partly each at weight 2 = 2 each; binary projection at TRUE→2×weight 2 = 4 each; **delta would be 2 raw points per item, +4 total over-scoring**). Re-check after Federal US LDA validation runs.

**Cumulative partly-tier over-scoring on Federal US LDA contact_log:** if .1, .3, .9, .11 all over-score by 1 raw point each (weight × 1 partly delta), the over-scoring is 2+2+3+3 = 10 raw points. **This would project Contact_log subtotal as 20 vs published 10.** That's larger than acceptable. **Phase C decision needed before launch:** either (a) accept the over-scoring and validate against `≤ published + tolerance` instead of `==`, OR (b) extract typed cells for the partly-tier sub-criteria (compendium 2.0 freeze question). **Recommendation:** ship with binary read + document over-scoring; defer typed extraction to compendium 2.0 freeze. Plan 4's Federal US LDA test uses `abs(projected - published) ≤ 12` tolerance for contact_log subtotal.

---

## Standard module structure

This plan only **extends** `focal_2024.py`; it does not introduce new files. Test additions:

```
tests/projections/test_focal_2024_per_item.py       # extends with contact_log subset (this plan)
tests/projections/test_focal_2024_ground_truth.py   # extends with contact_log indicator reads (this plan)
```

Module additions:

- `_ATOMIC_ITEMS_CONTACT_LOG: tuple[str, ...] = ("contact_log.1", ..., "contact_log.11")` (11 IDs).
- 11 entries appended to `_ATOMIC_SPEC` dict.
- `"is_not_null"` and `"or_any"` helper-name handlers in the dispatcher's `_project_atomic` function (if not already added by legal-core for relationships.1 / financials.10).
- Ground-truth loader extension: `load_focal_2024_per_country_reference(repo_root)` returns the 11 contact_log indicators alongside the 26 legal-core indicators.

---

## Test structure

### Per-item tests (`test_focal_2024_per_item.py` — contact_log extension)

- **Binary-read items** (.1, .2, .3, .4, .5, .7, .8, .9, .10): each parameterized over `{TRUE, FALSE, missing}` cell → expected `{2, 0, 0}`. 9 items × 3 cases = 27 cells.
- **Typed `IS NOT NULL` read** (.6 communication_form): parameterize over `{"in_person", "video", "phone", None, "missing"}` → expected `{2, 2, 2, 0, 0}`. 5 cases.
- **OR projection** (.11 bill_or_action_identifier α split): 4 truth-table cases over (spending_report ∈ {T, F}) × (reg_form ∈ {T, F}) → expected {2, 2, 2, 0}.

**Estimated cells:** 27 + 5 + 4 = **36 per-item truth-table cells for contact_log.**

### Ground-truth loader tests (`test_focal_2024_ground_truth.py` — contact_log extension)

- Federal US LDA row contains the 11 contact_log indicators with values matching the spec-doc audit breakdown ([0, 0, 2, 0, 0, 0, 0, 0, 3, 0, 3] for [.1, .2, .3, .4, .5, .6, .7, .8, .9, .10, .11]; sum 8 — wait, earlier breakdown says 0+0+2+2+0+0+0+0+3+0+3 = 10; discrepancy from contact_log.1 between 0 and 2). **Implementing agent task:** verify against the per-country CSV directly per spec doc Open Issue FOCAL-5 (audit-doc ordering ambiguity).
- Per-indicator value-range bounds (each contact_log indicator ∈ {0, 1, 2}).
- Spot-check a non-US high-scoring country (Canada or Chile) for contact_log per-indicator depth — these countries have meaningful contact-log requirements (Canada's Lobby Commissioner publishes per-meeting registries).

### Cross-rubric overlap tests (extension)

Only 2 of 11 contact_log items reuse existing v2 rows:

- `lobbyist_spending_report_includes_position_on_bill` (contact_log.10) — read by Sunlight #1 + Opheim (β AND pair). Cross-rubric test: assert FOCAL contact_log.10 projection agrees with Sunlight's projection on a sample state's cell.
- `lobbyist_spending_report_includes_bill_or_action_identifier` + `lobbyist_reg_form_includes_bill_or_action_identifier` (contact_log.11 α-split pair) — read by Sunlight #1, HG Q5/Q20 (when shipped), PRI E2g_ii. 4-rubric cross-check pre-FOCAL; 5-rubric post-FOCAL.

The 9 NEW contact_log rows are single-rubric-confirmed (FOCAL-distinctive) at landing; no cross-rubric tests for those at this round.

---

## Open questions for the implementing agent

3 questions surfaced; confirm before launch:

1. **Partly-tier over-scoring vs published L-N 2025 for Federal US LDA — accept or fix?**
   - Spec doc 7 of 11 contact_log items have Suppl Table 3 "partly" sub-tiers (data-quality observables) that v2 binary cells cannot read.
   - **Recommendation:** accept binary over-scoring for Federal US LDA (~10 raw points / ~5.5pp), document in module docstring, set Plan 4's Federal US LDA test tolerance to `abs(projected_contact_log_subtotal - published) ≤ 12`. **Defer typed extraction to compendium 2.0 freeze.**
   - **STOP clause:** if user wants to invest in partly-tier extraction to close the over-scoring, propose 2-3 new compendium cells (e.g., `lobbying_contact_log_topic_specificity_level: enum{vague, specific}`) for compendium 2.0 freeze. Not in Phase C scope without user direction.

2. **contact_log.11 OR over reg_form + spending_report sides.**
   - FOCAL's spec text: "Targeted areas of public policy or legislation, including a list of official legislative references/bill numbers/measures" — does NOT explicitly say "on which form." Sunlight's α form-type split has both cells; HG Q5/Q20 reads them separately (3 pts each).
   - **Recommendation:** OR over the two cells per the spec doc's per-item entry which states `(reg_form OR spending_report) AND specific_to_communication → 2`. The OR matches FOCAL's framing (the disclosure exists somewhere in the lobbyist's filing infrastructure).
   - **Validation check:** Federal US LDA — LDA requires bill numbers on LD-2 (spending report) only, not LD-1 (reg form). Binary projection of `lobbyist_spending_report_includes_bill_or_action_identifier == TRUE` → 2. Published is 3 (raw 1 × weight 3 = partly). Over-scoring +3 raw points.

3. **`is_not_null` helper for typed-cell reads — module-level or per-item lambda?**
   - The contact_log.6 read needs to test whether `lobbying_contact_log_includes_communication_form` (a typed `Optional[enum]`) is non-null. This is the same pattern as Newmark 2017's typed-threshold `IS NOT NULL` reads (3 items there) and FOCAL's descriptors typed-enum reads (.3, .5 in legal-core).
   - **Recommendation:** ship a single `_is_not_null_read(cells, row_id, axis) -> int` helper in `focal_2024.py` that returns 2 if cell value is non-null, 0 otherwise. The dispatcher checks `helper == "is_not_null"` and calls it. **If Newmark 2017 has shipped with a similar helper**, import from there for shared signature; otherwise inline. Module docstring notes the reuse.

---

## Phase 4 cross-rubric agreement audit feed

After contact_log lands (alongside the other 3 FOCAL plans), the following cross-rubric promotions:

- `lobbyist_spending_report_includes_position_on_bill` → **3-rubric-confirmed** (Sunlight + Opheim + FOCAL contact_log.10). β AND-projection family's first 3-rubric row.
- `lobbyist_spending_report_includes_bill_or_action_identifier` + `lobbyist_reg_form_includes_bill_or_action_identifier` → **5-rubric-confirmed** (Sunlight + HG Q5/Q20 + PRI + Opheim + FOCAL contact_log.11). Confirms α form-type split convention's empirical necessity.
- 9 NEW contact_log rows become single-rubric-confirmed (FOCAL-distinctive). No promotion paths from LobbyView (federal LDA schema-coverage check) on these rows — LDA does not require per-meeting contact disclosure.

---

## Sequencing notes for Sub-4

- This plan **must launch second** in the FOCAL sequence (after legal core).
- No cross-rubric helper imports; FOCAL contact_log is standalone within the FOCAL plan-set.
- Estimated implementation time: small — 36 truth-table cells + 11 dispatcher entries + extension of ground-truth loader. ~150-200 LOC. Likely 1 session.

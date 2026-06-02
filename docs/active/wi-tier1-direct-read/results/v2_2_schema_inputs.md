# v2.2 schema design inputs — rows where the model agrees but v2.1 can't represent the answer

**Purpose:** Structured record of cases where, on real statute extraction runs, the model(s) agree on what the statute says, but the v2.1 typed-cell schema cannot faithfully represent the answer. This is the corpus for the v2.2 schema redesign — see the 2026-05-24 gather-first pivot in repo-root `STATUS.md`.

**Scope:** This ledger is **observation-only**, not patch-driven. Each entry captures: the cell, the current v2.1 constraint, the observed model emission(s), the proposed v2.2 widening, and the source evidence. v2.1 stays locked; entries here become the design inputs when the v2.2 design pass runs.

**Cross-reference (naming):** [`compendium/NAMING_CONVENTIONS.md`](../../../../compendium/NAMING_CONVENTIONS.md) §7 (three-threshold framework, `_threshold_<measure>_<unit>` suffix). The row-ID `<unit>` suffix and the cell-class `unit` enum **content** are distinct surfaces: §7 governs the row-ID; this ledger records gaps in the enum content surface (`models_v2/cells.py`'s `TimeUnitLiteral`, etc.).

---

## Entry 1 — `TimeThresholdCell.unit` literal-enum gap (WI §13.62(11))

### Cell

| Field | Value |
|---|---|
| Cell class | `TimeThresholdCell` |
| Field | `unit: TimeUnitLiteral \| None` |
| Source: | `src/lobby_analysis/models_v2/cells.py` (line 186) |
| Reachable from row | `lobbyist_registration_threshold_time_percent` (legal axis) |

### Current v2.1 allowed values

```python
TimeUnitLiteral = Literal[
    "hours_per_quarter", "hours_per_year", "days_per_year", "percent_of_work_time"
]
```

(`src/lobby_analysis/models_v2/cells.py` line 171–173.)

### Observed model emissions

Both Claude opus-4-7 and GPT-5.2, **all 6/6 runs** on the WI 2025 statute bundle (Phase 2, 2026-06-01), emitted `unit="days_per_reporting_period"` for `lobbyist_registration_threshold_time_percent`, citing WI Stat. §13.62(11):

> An individual whose duties are not limited exclusively to lobbying is a lobbyist only if he or she makes lobbying communications on each of at least **5 days within a reporting period**.

Pydantic literal validation rejects with `literal_error`: `Input should be 'hours_per_quarter', 'hours_per_year', 'days_per_year' or 'percent_of_work_time' [type=literal_error, input_value='days_per_reporting_period', input_type=str]`.

### Proposed v2.2 additions (minimum)

- `days_per_reporting_period` — WI's structure (5 days per principal's 6-month reporting period). Generalizes to any state whose lobbyist-status definition counts qualifying days within the filing cadence.
- `days_per_6_month_reporting_period` — if a stricter encoding is wanted (when the reporting period itself is specified by statute as 6-monthly, this preserves the period length).

### Candidate additions (need more evidence before pinning)

- `days_per_quarter` — parallel to `hours_per_quarter`.
- `days_per_session` — for legislative-session-bounded thresholds (some states key on biennial session days).
- `days_unspecified_period` — escape hatch for statutes that say "N days" without naming the period; better than forcing one of the above.

### Source statute citation

WI Stat. §13.62(11) "Lobbyist" definition, paragraph beginning "If an individual's duties are not limited exclusively to lobbying…"

### Source evidence files

6 JSONs, all errored on this cell with identical mechanism:

- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/claude-opus-4-7__registration_thresholds__run{1,2,3}.json`
- `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/gpt-5.2-2025-12-11__registration_thresholds__run{1,2,3}.json`

The `errors[0].arguments` dict in each contains the full `record_cell` arguments the model emitted, including the exact `value={"magnitude": 5, "unit": "days_per_reporting_period"}` shape.

### Open design question — single source of truth or per-cell?

`TimeUnitLiteral` is reused on both `TimeThresholdCell` and `TimeSpentCell` (same `cells.py` line 200). When v2.2 lands, the question is whether unit enums should consolidate to a single canonical enum source (e.g., a shared `UnitsRegistry` typed module) or stay per-cell. **The gather-first phase doesn't need to decide this**; record it here so the v2.2 design pass has the question pre-loaded.

### Cross-row coordination note

The row `lobbyist_registration_threshold_time_percent` has `_time_percent` in its row-ID suffix per §7 of NAMING_CONVENTIONS.md — but the WI evidence shows the actual unit isn't a percent at all; it's day-count-per-period. If v2.2 adds `days_per_reporting_period`, the row-ID's `_time_percent` suffix is misleading for statutes (like WI) that use day-count thresholds. Two options for the v2.2 design pass to weigh:

- (a) Keep the row-ID `_time_percent` and accept that the suffix names the *family of measure* (time-based threshold), with `unit` field carrying the actual unit.
- (b) Split into two rows: `_time_percent` (for percent-of-work-time states) and `_time_days_per_period` (for day-count states), with each row's `unit` enum constrained to the matching shape.

(a) is simpler; (b) is more honest. **No decision needed now** — flagging for v2.2.

### How this entry was opened

Predecessor plan: [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md) Item 2.
Session that opened it: [`../convos/20260601_phase3_followups_execution.md`](../convos/20260601_phase3_followups_execution.md).
Companion: Item 1 (Fix A dict-shape coverage) cleared the magnitude-coercion side of this same cell's two-error stack; the enum gap is the residual.

---

## Future entries

Add new entries below as concrete v2.1 representation gaps surface across states. Each entry should carry: the cell + field, the v2.1 constraint, the observed emission, the proposed widening, the source statute citation, the source evidence files, and any cross-row coordination notes.

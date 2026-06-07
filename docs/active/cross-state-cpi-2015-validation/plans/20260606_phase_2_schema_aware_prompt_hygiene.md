# Plan — Phase 2 schema-aware prompt hygiene (supersedes Phase 2 of the pre-dispatch plan)

> ## ⚠️ SEQUENCING UPDATE (2026-06-06, post-finish-convo) — READ FIRST
>
> The original Phase 2 plan conflates three workstreams under one phase number. The correct execution order — clarified at the end of the finish-convo session, after the audit plan also landed — is:
>
> 1. **Execute Phase 2A (schema change) FIRST**, before the audit runs. Phase 2A promotes row #5 from FloatCell to TimeThresholdCell + adds the `other_specification` escape hatch. If the audit hits row #5 against the current FloatCell schema, it has to escalate as SCHEMA-BLOCKED. Landing 2A first lets the audit do a normal lean-prompt review of row #5 alongside the other 130 prompts.
>
> 2. **Then defer Phase 2B (the 7 YAML prompt rewrites) to the audit + execution agents.** The 7 prompts here are now "manually-curated reference drafts" — kept in this doc as worked examples of the lean-prompt principle for the audit agent to compare its drafts against, but the audit covers all ~131 legal-axis prompts and produces unified findings. Execution agents apply audit findings; do NOT separately apply Phase 2B as written.
>
> 3. **Then execute Phase 2C (legal-axis format-hint regression test) LAST**, after all prompt edits land from the audit-driven execution. The regression test gates future drift; it should be authored against the final post-edit state of the YAML, not the pre-audit state.
>
> So: 2A → audit → execute (separate plans, per audit findings) → 2C. The 7 prompt drafts in §Phase B below remain useful as the audit agent's reference drafts and as a sanity check on what the audit produces.

**Originating analysis:**
- [`./20260606_pre_dispatch_hygiene.md`](./20260606_pre_dispatch_hygiene.md) — the prior hygiene plan. Phase 1 of that plan landed in commit `cbcd3e2` (helper vocab fix; Round 1 re-audit 19/30). This plan **replaces Phase 2** of that plan with a schema-aware version, and renumbers everything downstream.
- Originating convo: [`../convos/20260606_phase_1_exec_and_de_jure_pivot.md`](../convos/20260606_phase_1_exec_and_de_jure_pivot.md). The design discussion produced three corrections to the prior Phase 2:
  1. **Extraction-vs-projection separation.** Prompts should ask the *actual question*, lean and granular. Cross-rubric synthesis (e.g., HG Q13's OR-projection across registration-form-comp ∨ spending-report-comp) lives in projection helpers, not in the prompt. Don't bake historical rubric framing into the model-facing question.
  2. **Test scope = dispatch scope.** The dispatcher (`scripts/tier_1_direct_read_legal_axis.py`) filters to `axis == 'legal'`. The format-hint regression test should iterate the same scope. The 4 practical-axis underspecified prompts (`_required` P, `_deadline_days` P, `_imposed_in_practice` P, `_audit_required_in_practice` P) aren't dispatched in this pipeline and shouldn't be flagged.
  3. **Row #5 schema asymmetry.** `lobbyist_filing_de_minimis_threshold_time_percent` is `FloatCell` but its sibling `lobbyist_registration_threshold_time_percent` is `TimeThresholdCell`. Same observable family, different cell types — Phase A oversight. Promote #5 to `TimeThresholdCell` for symmetry, and add a `other_specification` free-text escape hatch to `TimeThresholdCell` so non-enumerated unit shapes (e.g., "5 hours per week") aren't lost at extraction time.

- Reframing of risk: Dan's note — "the whole point of doing a handful at a time is to stress-test our model against reality; we can make adjustments until we're properly capturing what's out there." The original Phase 2 plan's Risk #1 (changes input mid-experiment / disturbs σ_noise comparability) is overcalibrated. Iterative model-vs-reality calibration is the design.

**Cross-branch context:**
- [`../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md`](../../leave-behind-prep/convos/20260606_take_stock_and_day1_hygiene.md) — 5-day Fellowship-end plan.
- [`../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md`](../../../historical/wi-ralph-cpi-renewal-cadence/plans/20260605_cross_state_cpi_2015_validation.md) — originating cross-state plan.

**Branch:** `cross-state-cpi-2015-validation`
**Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/cross-state-cpi-2015-validation`
**Estimated total cost:** $0 (no model dispatches; all source-code + YAML + test changes)
**Estimated total time:** ~90 min execution + Dan review gate

---

## Why this plan exists (the question it's answering)

After Phase 1 (helper vocab fix, commit `cbcd3e2`) Round 1 re-audited at 19/30 (63.3%). Phase 2 of the prior plan was to add format-hint clarifications to 11 underspecified prompts. Reviewing the underspecified-11 surfaced three corrections (above) that move Phase 2 from "append a format-hint sentence to 11 prompts" to a small structural change:

- 7 of the 11 are the operational scope (legal-axis = dispatched). The other 4 are practical-axis and not dispatched in this pipeline.
- 6 of the 7 need lean prompt rewrites following the extraction-vs-projection principle.
- 1 of the 7 (row #5) needs both a prompt rewrite AND a cell-type promotion (FloatCell → TimeThresholdCell), and TimeThresholdCell itself needs a `other_specification` field for non-enumerated units.

The implementing agent should already have re-read the failure-mode doc, the chunk inventory, and the schema-design convo before starting. The §Pre-execution checklist at the bottom gates that.

---

## The 7 operational underspecified prompts (legal-axis, dispatched)

| # | row_id | cell_type today | cell_type after | current prompt (truncated) |
|---|---|---|---|---|
| 1 | `lobbyist_registration_required` | BinaryCell | unchanged | CPI rubric only ("A 100 score is earned if all who are paid to lobby register as such...") |
| 2 | `lobbyist_registration_deadline_days_after_first_lobbying` | IntCell | unchanged | CPI rubric + scope note |
| 3 | `lobbyist_registration_amendment_deadline_days` | IntCell | unchanged | "7. Within how many days must a lobbyist notify the oversight agency of changes in registration?" |
| 4 | `lobbyist_registration_threshold_time_percent` | TimeThresholdCell | unchanged | newmark fragment, no return-shape |
| 5 | `lobbyist_filing_de_minimis_threshold_time_percent` | **FloatCell** | **TimeThresholdCell** (this plan) | pri_2010 fragment + scope note, no return-shape |
| 6 | `lobbyist_spending_report_cadence_other_specification` | FreeTextCell | unchanged | "Reporting frequency option: Other (free-text)." |
| 7 | `principal_spending_report_cadence_other_specification` | FreeTextCell | unchanged | "Reporting frequency option: Other (free-text)." |

The 4 practical-axis cells deferred from this plan:
- `lobbyist_registration_required` P (GradedIntCell) — shares YAML prompt entry with #1 (combined-axis row).
- `lobbyist_registration_deadline_days_after_first_lobbying` P (GradedIntCell) — shares YAML prompt entry with #2.
- `lobbying_violation_penalties_imposed_in_practice` P (GradedIntCell) — own YAML entry.
- `lobbying_disclosure_audit_required_in_practice` P (GradedIntCell) — own YAML entry.

These get clarified in a future plan when a practical-axis dispatch (Prong 2) actually exercises them. They are **not** Round 2 blockers.

---

## Phase A — Schema change (TimeThresholdCell + row #5 promotion)

**Goal:** add `other_specification` field to `TimeThresholdCell`; promote row #5 from FloatCell to TimeThresholdCell. Symmetric design with row #4 + escape hatch for non-enumerated units.

**Files touched:**
- `src/lobby_analysis/models_v2/cells.py` — `TimeThresholdCell` field addition.
- `compendium/disclosure_side_compendium_items_v2.1.tsv` — row #5's `cell_type` column.
- `tests/test_models_v2_cells.py` — new tests for `other_specification` field behavior.
- `tests/test_tier_1_legal_axis.py` — refactor `test_coerce_string_to_float_for_floatcell` to a synthetic FloatCell spec (since row #5 was the only FloatCell row in the compendium; FloatCell class itself remains as schema affordance).

### TDD sequence

1. **RED — TimeThresholdCell.other_specification field tests:**
   ```python
   def test_time_threshold_cell_accepts_other_specification_string():
       cell = TimeThresholdCell(
           cell_id=("lobbyist_registration_threshold_time_percent", "legal"),
           magnitude=None, unit=None,
           other_specification="5 hours per week",
       )
       assert cell.other_specification == "5 hours per week"

   def test_time_threshold_cell_other_specification_defaults_to_none():
       cell = TimeThresholdCell(
           cell_id=("lobbyist_registration_threshold_time_percent", "legal"),
           magnitude=Decimal("20"), unit="percent_of_work_time",
       )
       assert cell.other_specification is None

   def test_time_threshold_cell_other_specification_rejects_over_500_chars():
       with pytest.raises(ValidationError):
           TimeThresholdCell(
               cell_id=("lobbyist_registration_threshold_time_percent", "legal"),
               magnitude=None, unit=None,
               other_specification="x" * 501,
           )
   ```
   Plus retain the existing 3 TimeThresholdCell tests unchanged.

2. **RED — row #5 cell-spec class:**
   ```python
   def test_row_5_is_time_threshold_cell_in_registry():
       spec = _spec("lobbyist_filing_de_minimis_threshold_time_percent", "legal")
       assert spec.expected_cell_class.__name__ == "TimeThresholdCell"
   ```
   Place in `tests/test_models_v2_cells.py` or wherever the registry tests live.

3. **GREEN — schema change:**
   ```python
   class TimeThresholdCell(CompendiumCell):
       """The time-based threshold in a state's lobbyist registration definition
       or filing-exemption (e.g. the federal LDA's 20% of work time rule, or a
       state's "5 hours per week" threshold).

       Cell type: `typed Optional[TimeThreshold]` (2 rows, post-2026-06-06:
       `lobbyist_registration_threshold_time_percent` (registration trigger) and
       `lobbyist_filing_de_minimis_threshold_time_percent` (filing exemption)).

       Source: Newmark 2005/2017 projection mappings (registration row);
       PRI 2010 §III.D D2 (filing-exemption row).

       Fields:
       - magnitude: Decimal threshold value, or None if no threshold.
       - unit: one of TimeUnitLiteral, or None if the statute's unit doesn't
         fit any enumerated bucket OR no threshold exists.
       - other_specification: short verbatim description of the statute's
         unit framing when it doesn't fit TimeUnitLiteral (e.g., "5 hours per
         week", "20 hours per legislative session"). None when unit is set
         or when no threshold exists.
       """
       magnitude: Decimal | None
       unit: TimeUnitLiteral | None
       other_specification: Annotated[str, Field(max_length=500)] | None = None
   ```

4. **GREEN — TSV row #5:** change `cell_type` column from `typed Optional[float]` to `typed Optional[TimeThreshold]`. The parser table already maps that string to `TimeThresholdCell`; no parser change needed.

5. **GREEN — refactor FloatCell coercion test:**
   ```python
   def test_coerce_string_to_float_for_floatcell():
       """A JSON-string '3.5' for a FloatCell coerces to float 3.5.

       Uses a synthetic FloatCell spec rather than a real row: as of the
       2026-06-06 Phase A schema fix, no compendium row uses FloatCell —
       the class is retained as a schema affordance for future rows.
       """
       from lobby_analysis.models_v2 import CompendiumCellSpec, FloatCell
       spec = CompendiumCellSpec(
           row_id="__synthetic_floatcell__",
           axis="legal",
           expected_cell_class=FloatCell,
           prompt=None,
       )
       assert spec.expected_cell_class.__name__ == "FloatCell"
       result = tier0._instantiate_cell(spec, _record_cell_args("3.5"))
       assert result["cell"]["value"] == 3.5
       assert isinstance(result["cell"]["value"], float)
   ```

6. **Re-run pytest.** Full suite green (~1901 tests + the new ones).

### Acceptance gate

- Pytest fully green.
- `TimeThresholdCell.other_specification` accepts a string, defaults to None, rejects >500 chars.
- Row #5 in registry has `expected_cell_class == TimeThresholdCell`.
- FloatCell coercion path still tested (via synthetic spec).
- Suggested commit message: `phase 2A schema: TimeThresholdCell.other_specification escape hatch; promote row 5 (de minimis filing threshold) to TimeThresholdCell for symmetry with row 4`

---

## Phase B — YAML prompt updates (the 7 operational prompts)

**Goal:** lean prompts that ask the actual question, with return-shape spec. Strip rubric-language preamble where the question is clear without it.

**Files touched:**
- `compendium/source_quotes.yaml` — 7 prompt entries.

### The 7 revised prompts

**#1 — `lobbyist_registration_required` (BinaryCell):**
> *"Under state law, must paid lobbyists register with the state? (True or False)"*

Drops the CPI rubric language ("A 100 score is earned if all who are paid to lobby register as such...") entirely — the model has no use for it when the legal-axis observable is binary.

**#2 — `lobbyist_registration_deadline_days_after_first_lobbying` (IntCell):**
> *"Under state law, within how many days of first lobbying activity must a lobbyist register? Answer as a non-negative integer number of days. Use null if no such deadline exists in statute."*

**#3 — `lobbyist_registration_amendment_deadline_days` (IntCell):**
> *"Under state law, within how many days must a lobbyist notify the oversight agency of changes to their registration? Answer as a non-negative integer number of days. Use null if no such deadline exists in statute."*

**#4 — `lobbyist_registration_threshold_time_percent` (TimeThresholdCell):**
> *"Under state law, does the lobbyist-registration definition include a threshold based on time spent lobbying? If yes, extract the threshold's magnitude (non-negative number) and unit. Unit must be one of: `hours_per_quarter`, `hours_per_year`, `days_per_year`, or `percent_of_work_time`. If the statute uses a different unit (e.g., hours per week, hours per legislative session), leave `unit` null and put a short verbatim description in `other_specification`. Use null for `magnitude` and `unit` if no time-based threshold exists in the lobbyist definition."*

**#5 — `lobbyist_filing_de_minimis_threshold_time_percent` (TimeThresholdCell, post-promotion):**
> *"Under state law, is a person exempt from filing lobbying disclosure if their lobbying activity is below a time threshold? If yes, extract the threshold's magnitude (non-negative number) and unit. Unit must be one of: `hours_per_quarter`, `hours_per_year`, `days_per_year`, or `percent_of_work_time`. If the statute uses a different unit, leave `unit` null and put a short verbatim description in `other_specification`. Use null for `magnitude` and `unit` if no time-based filing-exemption threshold exists."*

**#6 — `lobbyist_spending_report_cadence_other_specification` (FreeTextCell):**
> *"If state law requires lobbyist spending reports on a non-standard cadence (i.e., not annual / semiannual / quarterly / monthly / biennial / triannual), describe that cadence. Answer with a short free-text description. Use null if the cadence is one of the standard buckets or if no spending report is required."*

**#7 — `principal_spending_report_cadence_other_specification` (FreeTextCell):**
> *"If state law requires principal/employer spending reports on a non-standard cadence (i.e., not annual / semiannual / quarterly / monthly / biennial / triannual), describe that cadence. Answer with a short free-text description. Use null if the cadence is one of the standard buckets or if no spending report is required."*

### Sequence

1. Apply the 7 prompt edits to `compendium/source_quotes.yaml`.
2. **Surface diff to Dan for semantic review BEFORE commit.** Per the originating convo's discipline check: confirm each prompt asks the same *underlying question* the prior prompt was trying to ask, and that the extraction-vs-projection separation is honored. Any contested prompt skipped + documented.
3. Run full pytest.

### Acceptance gate

- Pytest fully green.
- Dan signed off on the 7 prompt diffs.
- Suggested commit message: `phase 2B prompts: lean rewrites for 7 underspecified legal-axis prompts; #4/#5 reflect TimeThresholdCell.other_specification escape hatch`

---

## Phase C — Format-hint regression test (legal-axis scope)

**Goal:** prevent regression of the underspecified-prompt issue. Iterate the same scope the dispatcher actually uses (`axis == 'legal'` cells in the 6 default chunks).

**Files touched:**
- `tests/test_default_chunk_prompts_have_format_hints.py` (new).

### TDD sequence

1. **RED** — write the test:
   ```python
   """Regression guard: every legal-axis cell in the 6 CPI-2015 C11 default
   chunks must have a prompt that explicitly states the response format.

   Scope matches the dispatcher's filter (`tier_1_direct_read_legal_axis.py`):
   axis=='legal' cells only. Practical-axis cells get their own hygiene pass
   when a practical-axis dispatch is added.
   """
   from __future__ import annotations

   from lobby_analysis.chunks_v2 import build_chunks

   _DEFAULT_CHUNKS = (
       "lobbying_definitions",
       "registration_thresholds",
       "registration_mechanics_and_exemptions",
       "lobbyist_spending_report",
       "principal_spending_report",
       "enforcement_and_audits",
   )

   # Keywords that signal the prompt explicitly states a return shape.
   # Empirical: every well-specified prompt in the YAML as of 2026-06-06
   # contains at least one of these (case-insensitive substring match).
   _FORMAT_KEYWORDS = (
       "true or false",
       "boolean",
       "non-negative integer",
       "non-negative float",
       "non-negative decimal",
       "answer with one of",
       "answer with the dollar",
       "answer with the time-percent",
       "answer as a non-negative",
       "answer with a short free-text",
       "answer with the set",
       "answer with a magnitude",
       "use null",
       # additional return-shape signals as the YAML evolves; extend with care.
   )

   def test_default_chunk_legal_axis_prompts_have_format_hints():
       chunks = {c.chunk_id: c for c in build_chunks()}
       offenders = []
       for cid in _DEFAULT_CHUNKS:
           for cs in chunks[cid].cell_specs:
               if cs.axis != "legal":
                   continue
               prompt = (cs.prompt or "").lower()
               if not any(kw in prompt for kw in _FORMAT_KEYWORDS):
                   offenders.append((cs.row_id, cs.axis))
       assert not offenders, (
           f"{len(offenders)} legal-axis prompts in default chunks lack a "
           f"format hint: {offenders}"
       )
   ```

2. Before Phase B's prompt edits: test fails with 7 offenders (the operational underspecified set).
3. After Phase B's prompt edits: test passes.

### Acceptance gate

- Test fails with exactly 7 offenders before Phase B; passes after.
- Full pytest green.
- Suggested commit message: `phase 2C test: legal-axis prompt format-hint regression guard for 6 default chunks`

---

## Risks & open caveats (read before committing)

1. **TimeUnitLiteral domain still lacks `hours_per_week`.** Dan's escape hatch (`other_specification`) covers it, but projection-side arithmetic over `hours_per_week` statutes will land in free-text rather than a structured magnitude+unit. If Round 2 surfaces many `hours_per_week` statutes, expanding the literal becomes a follow-up. Tracked as deferred (§NOT in this plan).

2. **TimeSpentCell has the same shape** (`magnitude: Decimal | None, unit: TimeUnitLiteral | None`) as TimeThresholdCell pre-fix. Same escape-hatch gap. But TimeSpentCell isn't in the 6 default chunks (it's on `lobbyist_or_principal_spending_report_includes_time_spent_on_lobbying`, a FOCAL 2024 row), so it's not Round-2-blocking. Mirror the fix when that row goes into rotation.

3. **The Phase A pedigree-completeness gap is acknowledged but not addressed here.** 50 multi-rubric rows in the TSV have dropped source quotes in the YAML (only 1 of the 49 carried >1 source_quotes entry). For Round 2 this doesn't matter — Dan's extraction-vs-projection principle means the model only needs the actual question, not the rubric chronology. Pedigree review work is review-side, not dispatch-side. Defer to a separate plan.

4. **Round 2 is no longer treated as a "controlled experiment" requiring σ_noise comparability with Round 1.** Per Dan's reframing, the design is iterative model-vs-reality calibration. If Round 2 dispatches with these 7 revised prompts and surfaces new failure modes, that's the signal we're looking for, not a confound.

5. **Schema migration risk for row #5 is bounded.** No projection helper reads row #5 today; the existing FloatCell coercion test gets refactored to a synthetic spec; the only behavior change is at dispatch time (the model returns a TimeThresholdCell-shaped dict instead of a FloatCell-shaped one). Dispatch test coverage (`test_tier_1_legal_axis.py`) exercises the TimeThresholdCell shape; row #4's tests carry forward.

---

## Pre-execution checklist (gating Phase A start)

The implementing agent (next session) should confirm before writing the first test:

- [ ] Read this plan end-to-end.
- [ ] Read the originating convo (`../convos/20260606_phase_2_schema_design.md`) end-to-end.
- [ ] Read [`./20260606_pre_dispatch_hygiene.md`](./20260606_pre_dispatch_hygiene.md) end-to-end (the prior plan; Phase 1 of that landed in commit `cbcd3e2`).
- [ ] Read `src/lobby_analysis/models_v2/cells.py` end-to-end (TimeThresholdCell area).
- [ ] Read `tests/test_models_v2_cells.py` (existing TimeThresholdCell tests).
- [ ] Read `tests/test_tier_1_legal_axis.py` lines ~99-105 (the FloatCell coercion test that needs refactoring) and lines ~340-400 (TimeThresholdCell dispatch shape tests).
- [ ] Run `uv run pytest` baseline — confirm current suite is green (1901 passed) before any changes.
- [ ] Confirm worktree is clean + on `cross-state-cpi-2015-validation` at HEAD `cbcd3e2` or later.
- [ ] Phase B is gated by a Dan-review checkpoint. After applying YAML edits, surface the 7 diffs to Dan; do NOT commit until sign-off.

---

## What's explicitly NOT in this plan (deferred)

- **TimeUnitLiteral expansion to add `hours_per_week`.** Escape hatch (`other_specification`) covers the gap for this round. Revisit if Round 2 surfaces many hours_per_week statutes that would be cleaner as structured magnitude+unit.
- **TimeSpentCell parallel cleanup** (add `other_specification` field to TimeSpentCell). Not in the 6 default chunks; mirror the fix when that row goes into dispatch rotation.
- **Practical-axis prompt hygiene** (the 4 deferred cells). Out of operational scope — practical axis isn't dispatched.
- **YAML pedigree-completeness pass** (recover dropped source quotes for the 49 multi-rubric rows). Review-side work, not Round-2-blocking. Separate plan.
- **The other ~75 already-well-specified legal-axis prompts.** They follow `[rubric quote] + [clarification] + [format spec]` — bloated by Dan's lean-prompt principle, but rewriting them would be a much larger scope and not Round-2-blocking. Surface as a deferred clean-sweep candidate.
- **Projection helper updates for row #5.** No projection helper reads row #5 today, so the cell-type promotion is dispatch-side only. If a future helper consumes row #5, it should respect the new schema (magnitude + unit + other_specification).

---

## Cost summary

| phase | cost | time | scope |
|---|---:|---:|---|
| A — schema change (TimeThresholdCell + row #5 promotion) | $0 | ~30 min | cells.py, TSV, tests |
| B — YAML prompt updates (7 prompts) | $0 | ~30 min + Dan review | source_quotes.yaml |
| C — format-hint regression test | $0 | ~15 min | new test file |
| **total** | **$0** | **~75 min + Dan review gate** | one execution session |

After Phases A–C land, the originating plan's Phase 3 (Round 1 re-audit checkpoint capture) and Phase 4 (Round 2 dispatch) remain as written.

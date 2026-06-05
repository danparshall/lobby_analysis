# 2026-06-05 (even later) — Phase A execution: 163 YAML additives landed under TDD, A2.b dispatch confirms BinaryCell+EnumCell templates at scale on WI

**Plan:** [`../plans/20260605_phase_a_yaml_audit_at_scale.md`](../plans/20260605_phase_a_yaml_audit_at_scale.md)
**Originating convo:** [`20260605_phase_a_kickoff.md`](20260605_phase_a_kickoff.md) (plan landed; Dan dropped A0, picked A2.b)
**Audit script:** `/tmp/audit_phase_a_a2b.py` (session artifact)
**Bulk-edit script:** `/tmp/apply_phase_a_yaml_additives.py` (session artifact)

## Pre-flight

Re-read kickoff convo + plan end-to-end (especially §Pre-execution checklist). Re-ran `/tmp/phase_a_characterize.py` and `/tmp/phase_a_list_targets.py` (both already preserved as session artifacts) — characterization numbers held: 183 rows total, 22 already-additive, 161 raw rubric-vocab. Breakdown for Phase A: 135 raw BinaryCell + 3 raw DecimalCell-Optional + 9 raw enum-family + 11 long-tail-defer + 3 practical-skip. Vocabulary across the additive markers and the existing wide-pass additives confirmed; cell-class routing verified via `src/lobby_analysis/models_v2/cell_spec.py` (`_CELL_TYPE_PARSER`).

`enum_domains.py` registry **does not exist** — only `cells.py` has 3 Literals (`UpdateCadenceLiteral`, `TimeUnitLiteral`, `IncomeSourceTypeLiteral`). For the 9 enum-family rows, per-row domains were hand-designed from the FOCAL/CPI/HG source quotes (e.g., the YES/MODERATE/NO domain for `_audit_required_in_law`, the 5-type IncomeSourceTypeLiteral domain for `consultant_lobbyist_report_includes_income_by_source_type`).

## Decisions confirmed with Dan mid-session

1. **Dispatcher constraint surfaced.** The Tier-1 dispatcher hardcoded `_RESOLVED_CHUNKS` to the 6 CPI-2015 C11 chunks; the plan + handoff's chosen BinaryCell verification chunk (`actor_registration_required`) was NOT in that list. Per plan §"Out of scope" ("If A0 surfaces a code-side surprise, surface to Dan, don't autonomously change code") I asked Dan with 3 concrete options: (a) extend `_RESOLVED_CHUNKS` via TDD, (b) substitute default-only chunks, (c) defer A2.b entirely. **Dan picked (a)** — small TDD change.
2. **`_DEFAULT_CHUNKS` vs `_RESOLVED_CHUNKS` split landed.** To preserve the 6-chunk default-dispatch invariant (test `test_omitting_chunks_resolves_to_all_six` would otherwise have to flip semantics), refactored into two tuples: `_DEFAULT_CHUNKS` (6 — used when `--chunks` omitted) and `_RESOLVED_CHUNKS` = `_DEFAULT_CHUNKS + _PHASE_A_EXTRA_CHUNKS` (used for validation). Allows `--chunks actor_registration_required` while leaving multi-state expansion's default dispatch surface unchanged.

## What happened (chronological)

1. **Pre-flight reads + characterization re-run** — same numbers as plan.
2. **RED batch (TDD per `skills/test-driven-development/SKILL.md`).** Wrote `tests/test_phase_a_yaml_additives.py` (167 tests total) with 3 parametrized contracts:
   - Every `cell_type == "binary"` row's prompt contains `"Answer with the boolean value true or false."` (151 rows × 1 marker)
   - Every `cell_type == "typed Optional[Decimal]"` row's prompt contains `"non-negative decimal"` (5 rows × 1 marker)
   - Each of 9 hand-curated enum-family target rows' prompt contains `"Answer with one of:"` or `"Answer with one or more of:"`
   Plus 2 sanity tests (row-count anchors against plan-documented totals).
   **RED confirmed: 163 failures (150 binary + 4 decimal + 9 enum), each for the right reason** (prompt missing additive marker). Filter design verified by inspecting first failure (`actor_executive_agency_registration_required: 'Executive branch agencies.'` — clean signal).
3. **GREEN batch — single Python script `/tmp/apply_phase_a_yaml_additives.py`** doing all 163 edits in one pass using line-level text editing (preserves YAML double-quoted-key style; PyYAML round-trip would not). Script:
   - Replaces 13 hand-craft prompts wholesale (4 decimal + 9 enum, each with a hand-designed cell-type-aligned full prompt)
   - For 151 binary rows: skip if `"Answer with the boolean value true or false."` already in prompt; else append. Skipped 1 (`_defined_in_law` from predecessor session), added on 150.
   Result: 163 prompt lines modified, file diff exactly 163 insertions + 163 deletions.
4. **Phase A test suite GREEN at 167/167.** Full pytest suite GREEN at 1850 passed (+0 failures vs pre-Phase-A baseline).
5. **Dan-question about dispatcher extension** (between RED→GREEN of Stage A1 and Stage A2). Surfaced 3 options; Dan picked (a) Extend `_RESOLVED_CHUNKS` via TDD. RED+GREEN for the dispatcher extension landed (1 new test + 1-line addition + the `_DEFAULT_CHUNKS`/`_RESOLVED_CHUNKS` refactor). Test suite 1851 passed.
6. **Archived prior JSONs for `registration_thresholds` + `enforcement_and_audits`** to `_pre_phase_a_<chunk>/` with SUPERSEDED.md banners (per "prefer mv over rm" memory). `actor_registration_required` has no priors (new chunk in dispatch). 12 JSONs archived.
7. **A2.b dispatch — 3 chunks, $0.8290 total.** Wall time ~5 min. Headline: 18/18 dispatched, 0 skipped.
8. **Audit via `/tmp/audit_phase_a_a2b.py`** — per-row table + before/after spillover compare.

## Findings (load-bearing)

### 1. BinaryCell bulk additive at scale: 0 errors, 85+% stability

`actor_registration_required` (11 binary cells × 2 models × 3 runs = 66 cell-instantiations) **passed 66/66 with zero instantiation errors.** The bulk additive (`Answer with the boolean value true or false.`) extends the `_defined_in_law` Pattern C iteration cleanly.

Per-row value-stability:
- 9 of 11 rows: 6/6 model-run convergence at high confidence
- `actor_lobbying_firm_registration_required`: Claude 2/3 True / 1/3 False (medium confidence; run3 drift), GPT 3/3 True → **5/6 majority True**, substantive disagreement on the run3 outlier
- `actor_local_government_registration_required` + `actor_public_entity_other_registration_required`: medium-confidence 6/6 True (consistent, less assertive)

**Conclusion:** the BinaryCell template generalizes from `_defined_in_law` (1 row, predecessor session) to the 11-row representative chunk. Multi-state expansion is unblocked on BinaryCell, modulo per-state statute quirks.

### 2. EnumCell hand-craft: value-stability flag RESOLVED on `_audit_required_in_law`

`lobbying_disclosure_audit_required_in_law` was flagged in the predecessor session as Claude-run3-drift-to-YES (5/6 'MODERATE' + 1 drift). The Phase A EnumCell additive (`Answer with one of: 'YES', 'MODERATE', or 'NO'. Use 'YES' if... Use 'MODERATE' if... Use 'NO' if...`) **converged 6/6 on 'MODERATE'.** The plan's prediction "additive may incidentally resolve the iter-5 value-stability flag" LANDED.

The CPI 2015 IND_207 errata candidate stands: 6/6 'MODERATE' (impartial-third-party = NO + compliance-review = MODERATE per the YES/MODERATE/NO domain definition); CPI 2015 oracle says YES. Models cite §13.74(1) Ethics Commission compliance review.

### 3. DecimalCell-Optional hand-craft: 2 of 4 rows value-stable; 2 need more iteration

**Value-stable post-Phase-A:**
- `lobbyist_filing_de_minimis_threshold_dollars`: **6/6 '500' at high confidence** (matches pre-Phase-A baseline; the new explicit additive ratified the iter-5 chunk-mate-spillover value). WI §13.621.
- `lobbyist_registration_threshold_expenditure_dollars`: **6/6 None at high confidence** (GPT cleared UNSCOREABLE×3 → None; Claude held None×3). Both models agree: no lobbyist-side expenditure standard in WI statute.

**Not yet stable:**
- `lobbyist_filing_itemization_de_minimis_threshold_dollars`: Claude 2/3 '200', 1/3 None (medium); GPT 3/3 None (high). Pre-Phase-A: Claude '500'/'500'/'200', GPT UNSCO×3. **GPT cleared UNSCOREABLE; Claude shifted '500' → '200'**, disagreement remains. The Sunlight Tier-0/-1 itemization-reporting question is semantically ambiguous: $200 (§13.625 expenditure breakdown threshold for itemized line items?) vs None (no statute defines a per-item de minimis exemption — they say "all" or "lump aggregate"). Phase B candidate.
- `lobbyist_registration_threshold_compensation_dollars` (already-additive iter 5 winner): Claude 3/3 '0' (held); GPT 1/3 '0', 2/3 None. Pre-Phase-A GPT was 3/3 '0'. **Minor regression on GPT** (3/3 → 1/3 + 2/3 None). Both interpretations are consistent with §13.62(11) ("any economic consideration") — None = "no statute defines a threshold;" '0' = "threshold is zero" — chunk-mate spillover from the bulk additives may be the cause.

### 4. Long-tail TimeThresholdCell confirms plan's DEFER decision

`lobbyist_registration_threshold_time_percent` (cell_type `typed Optional[TimeThreshold]`, DEFER per plan): **6/6 instantiation errors.** Both models emit valid `{magnitude, unit}` shape (e.g. `{"magnitude": 5, "unit": "days"}`) but `unit='days'` / `unit='days_per_reporting_period'` are not in `TimeUnitLiteral` domain (`hours_per_quarter, hours_per_year, days_per_year, percent_of_work_time`).

**Confirms plan's prediction:** long-tail typed singletons need per-cell-type Phase-B-style template design before they instantiate cleanly. The model's statute reading (5 days per reporting period; WI uses an absolute hours threshold under §13.68(1)(a)) is substantively coherent; the cell-shape additive is the missing piece.

### 5. Chunk-mate spillover characterization

`registration_thresholds` chunk shows non-trivial spillover from the bulk additives:
- GPT cleared UNSCOREABLE on 2 rows (`itemization_threshold_dollars`, `_threshold_expenditure_dollars`, `_de_minimis_threshold_time_percent`) — POSITIVE spillover (the explicit cell-type vocabulary reduced GPT's hesitancy).
- GPT shifted '0' → None on `_threshold_compensation_dollars` (2/3) — AMBIGUOUS spillover (still convergent interpretation; sentinel value flip is a known DecimalCell-Optional sub-pattern).
- Claude regressed slightly on `_filing_de_minimis_threshold_time_percent` (1 None + 2 UNSCOREABLE vs PRE 3 None) — MINOR regression.

The plan's iter 5 finding "chunk-mate spillover is real and bigger than prior iterations made visible" generalizes to Phase A: bulk per-row prompt edits affect chunk-mate rows through the chunk-wide prompt context. The post-Phase-A picture is overall positive (2 stable wins, 2 still-unresolved, 1 minor regression).

### 6. The Nori-flow plan-then-fresh-session boundary held

This was a fresh session, executed cleanly under TDD per the plan's §Pre-execution checklist. RED batch first (all 167 tests written before any GREEN), then GREEN, then dispatch. The "8. Confirm with Dan: chunk picks" step caught the dispatcher constraint and surfaced cleanly. The plan-then-execute pattern saved a meaningful amount of mid-session redesign — the planning session had already done the per-row enum-domain reasoning prep, so execution-session enum-domain design was just "write down the answer" not "decide it from scratch."

## Cost ledger

| Item | Cost |
|---|---|
| Pre-flight + characterization re-run | $0 |
| RED batch (167 tests written) | $0 |
| GREEN batch (163 YAML edits via bulk script) | $0 |
| Dispatcher TDD extension (1 test + 1-line refactor) | $0 |
| A2.b dispatch (3 chunks, 18 dispatches) | **$0.8290** |
| Audit | $0 |
| **This session subtotal** | **$0.8290** |
| **wi-ralph cumulative** | **$3.5127** (was $2.6837; against $3-5 ceiling; $1.49 remaining) |
| wi-tier1-direct-read cumulative | $7.2946 (unchanged) |
| **Grand total WI Phase 1/2 + Phase B** | **$10.8073** |

## Artifacts produced

- **YAML edits (163 prompts modified):** `compendium/source_quotes.yaml` — 4 hand-craft DecimalCell-Optional + 9 hand-craft EnumCell-family + 150 bulk BinaryCell additives.
- **Tests (167):** `tests/test_phase_a_yaml_additives.py` — 3 parametrized cell-type-bucket contracts + 2 plan-anchor sanity tests.
- **Dispatcher extension:** `scripts/tier_1_direct_read_legal_axis.py` (`_DEFAULT_CHUNKS` / `_RESOLVED_CHUNKS` refactor + `actor_registration_required` added). `tests/test_tier_1_chunks_filter.py` updated (1 new test + 1 existing test text update).
- **Archived JSONs:** `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_phase_a_registration_thresholds/` + `_pre_phase_a_enforcement_and_audits/`, both with SUPERSEDED.md banners.
- **Fresh A2.b dispatch JSONs:** 18 (`actor_registration_required` ×6, `registration_thresholds` ×6, `enforcement_and_audits` ×6).
- **Session scripts (preserved in /tmp):** `apply_phase_a_yaml_additives.py`, `audit_phase_a_a2b.py`.

## Next-session candidates

Dan's call. Recommended order:

1. **(Most natural continuation) Cross-state expansion design.** Phase A's done-criteria #1-#6 met for WI; the BinaryCell + EnumCell templates are confirmed at scale on WI's `actor_registration_required` chunk + `enforcement_and_audits` chunk. Per Dan's earlier framing: "batch-dispatch-per-loop, we want the *overall* effect." 15-state matrix (AK/AR/CA/CO/FL/IL/MA/MI/NC/OH/PA/TX/WA/WI/WV × 2015 + 2025 = 30 dispatches per chunk per round; NY+WY only 2010). Need to design: which chunks to dispatch (default 6? all 7 including actor_registration_required? smaller subset on a Phase-A-validation focus?), how to roll up cell-instantiation success rates per state-vintage, and whether to fold v2.1 promotion to main into the cross-state task.
2. **DecimalCell-Optional follow-up Ralph on `lobbyist_filing_itemization_de_minimis_threshold_dollars`.** Claude=$200 / GPT=None disagreement needs disambiguating prompt edit. ~$0.30.
3. **Long-tail typed singletons template design** (11 distinct cell types deferred from Phase A; ~$0.30-0.50 per cell-type design iteration). TimeThresholdCell is the most concrete target — both models emit valid magnitude+unit but the unit domain doesn't match what statutes actually use (e.g. WI §13.68(1)(a) "10 hours per reporting period"). Either extend `TimeUnitLiteral` or accept `unit=None` as a sentinel.
4. **v2.1 propagation to main** (Decision 3 of the plan — still deferred). Templates are confirmed at scale; safe to merge to main now. ~5 min + PR.

## Open questions surfaced this session

- **6-vs-15 chunk-count discrepancy resolved.** Dispatcher's `_RESOLVED_CHUNKS` was hardcoded to 6; chunks_v2 manifest has 15. Phase A extended to 7 (defaults + `actor_registration_required`). Multi-state expansion may want to consider further extensions.
- **CPI 2015 IND_207 errata candidate stands** (6/6 'MODERATE' vs CPI YES). Plus IND_197 (compensation threshold) from iter 5. Two CPI WI-row errata documented in this branch's results; projection-mapping-doc footnote update is a clean-up task.
- **Itemization-threshold ambiguity** (Claude $200 / GPT None on `lobbyist_filing_itemization_de_minimis_threshold_dollars`) — Sunlight Tier-0/-1 reporting-itemization-vs-aggregate question doesn't have a clean WI-statute reading. Phase B candidate.
- **Chunk-mate spillover both helps and hurts.** GPT cleared 2 UNSCOREABLE → None (positive); Claude regressed 1 None → UNSCOREABLE (negative). Net positive. The mechanism deserves a brainstorm — the bulk per-row additives change chunk-wide prompt context, which affects unrelated rows.

## Session meta

Fresh-session TDD discipline held cleanly:
- All RED tests written before any GREEN (Skill requirement).
- Per-row prompt design happened in planning session; execution session just applied them.
- The dispatcher mismatch (plan vs reality) was caught early and surfaced to Dan with concrete options rather than autonomously resolved.
- Doc graph walked at finish-convo (this convo + RESEARCH_LOG + STATUS update + commit).

## Next-session handoff sentence

*"Pick up branch `wi-ralph-cpi-renewal-cadence`. Phase A is structurally complete: 163 YAML additives landed (150 binary + 4 decimal-opt + 9 enum), tested under TDD (167 Phase A tests + dispatcher extension test), and verified on WI via A2.b dispatch ($0.8290; cumulative wi-ralph $3.5127 of $5 ceiling, $1.49 remaining). BinaryCell + EnumCell templates confirmed at scale; DecimalCell-Optional 2 of 4 stable / 2 need follow-up; long-tail TimeThresholdCell DEFER confirmed (6/6 instantiation errors as expected). Best next moves: (1) cross-state expansion design, (2) DecimalCell-Optional follow-up Ralph on `_filing_itemization_threshold_dollars`, (3) v2.1 propagation to main (templates confirmed; safe to merge). Read `convos/20260605_phase_a_execution.md` end-to-end + `convos/20260605_phase_a_kickoff.md` + the plan for context."*

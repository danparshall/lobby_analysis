# Phase 3 followups execution — items 1, 5, 6 (+ bonus item 2 capture)

**Date:** 2026-06-01
**Branch:** `wi-tier1-direct-read`
**Originating plan:** [`../plans/20260601_post_phase3_followups.md`](../plans/20260601_post_phase3_followups.md)
**Predecessor convo:** [`20260601_wi_tier1_phase2_run.md`](20260601_wi_tier1_phase2_run.md)

## Summary

Picked up the post-Phase-3 followups handoff. Of the 7 items in the plan:
- **Item 1 (Fix A int→Decimal regression)** — investigated, root-caused as hypothesis (b), fixed with TDD, full test suite stays at 1553 passing.
- **Item 5 (principal-filings aggregation source)** — investigated, conclusion is "neither A nor B cleanly; it's a deliberate Tier-2/Tier-3 scope decision tracked at GH #28."
- **Item 6 (σ_noise WI-vs-OH composition)** — decomposed the metric, surfaced an issue with the Phase 2 convo's cross-state baseline (uses pre-fix OH; no clean post-fix OH baseline exists), and surfaced the within-state cross-model finding as the load-bearing one.
- **Bonus: Item 2 capture (v2.2 `TimeThresholdCell.unit` enum gap)** — since Item 1 work already produced the exact evidence, opened the v2.2 design ledger here rather than ship-then-patch-each-gap.
- **Skipped:** Item 3 (Citations API, gated on Dan's review of 18 disagreement cells), Item 4 (MI-session standing instruction), Item 7 (GH #31, independent track).

This was an analysis-and-cleanup session — no API spend, no new statute runs, no Phase 2 convo edits per Dan's call on the baseline-issue framing.

## Topics Explored

### Item 1 — Fix A regression on dict-shape value path

Investigation confirmed **hypothesis (b)** from the plan: Fix A (`scripts/tier_0_direct_read_smoke.py::_coerce_scalar_value`, commit `0403218`) is present on main and operates correctly for the scalar `DecimalCell` path. The dict-shape branch of `_instantiate_cell` (lines 542–561 in the same file, covering `TimeThresholdCell`, `TimeSpentCell`, `CountWithFTECell`, `EnumSetWithAmountsCell`) unpacks `raw_value` directly into the cell constructor without per-field coercion, so a bare `int` `magnitude` for `TimeThresholdCell` reaches Pydantic strict mode unchanged.

**Fix shape:** added `_coerce_dict_shape_inner_decimals(cls, kwargs)` helper that walks `cls.model_fields`, finds fields whose annotation contains `Decimal`, and coerces `int`/`float` values to `Decimal` (excluding `bool` per parallel to scalar bool-uncoerced precedent). Called from the dict-shape branch immediately before the constructor.

**Tests:** 3 new tests in `tests/test_tier_1_legal_axis.py`:
- `test_coerce_int_magnitude_to_decimal_for_timethresholdcell` — RED before fix, GREEN after.
- `test_coerce_float_magnitude_to_decimal_for_timethresholdcell` — RED before fix, GREEN after.
- `test_bool_magnitude_not_coerced_to_decimal_for_timethresholdcell` — passes both before and after (strict-mode Pydantic correctly rejects bool→Decimal even without coercion); included for parallel coverage with the scalar bool-uncoerced test.

Tests use `unit="days_per_year"` (a valid `TimeUnitLiteral`) to isolate the magnitude coercion from item 2's separate enum-gap on `"days_per_reporting_period"`.

**Verification:** Full test suite 1553 passed / 3 skipped / 3 xfailed (matches the Phase-1 baseline). Ruff lint on touched files: 6 errors, all pre-existing E402 on unrelated imports — verified by stashing my changes and re-running ruff (same 6 errors).

### Item 5 — Principal-filings aggregation: where does the itemized data live?

Read the WI Tier-2 parsers (`src/lobby_analysis/io/wi/principal_meta_parser.py`, `principal_parser.py`, `principal_materialize.py`, `principal_fetcher.py`). The current scrape hits 4 URL families, all routed to per-entity *summary* pages. The principal summary page's "Total Lobbying Effort" table has **exactly 3 labeled rows** (`Total Lobbying Expenditures`, `Total Hours Communicating`, `Total Hours Other`) — the parser reads all 3, drops nothing. The 4 gaps Dan surfaced (compensation per lobbyist, gifts, indirect costs, itemized format) are not in this page's DOM at all.

The archived `wi-disclosure-explore` plan ([`docs/historical/wi-disclosure-explore/plans/wi_tier_2_parser.md`](../../../historical/wi-disclosure-explore/plans/wi_tier_2_parser.md)) explicitly scoped out "tier-3 (per-(lobbyist, principal, semester) detailed time reports + per-principal SLAE itemizations)" as out of scope, and tracked the deferred work at [GH #28](https://github.com/danparshall/lobby_analysis/issues/28) ("Pull WI expenditure data — 15-day reports + 6-month SLAEs"). GH #28's body confirms the WI portal does publish two report families (15-day notifications + 6-month SLAEs) and a per-bill/topic aggregate endpoint that aren't currently fetched.

**Verdict:** not scrape loss in the parser, not portal-publication absence; it's a deliberately deferred Tier-3 fetch family. The 4 gaps likely close when GH #28 lands — but **no one has inspected a Tier-3 SLAE page yet**, so a single page reconnaissance fetch is the natural Phase-1 of #28 before bulk work.

### Item 6 — σ_noise composition: WI vs OH

Decomposed `pct_stable` into its four mutually exclusive stability classes (stable / value-unstable / scoreability-unstable / incomplete). Replication of the Step D writeup numbers (Claude 85.71 %, GPT 79.76 %) is the consistency check on the script.

**Three findings:**

1. **The Phase 2 convo's cross-state Δ is computed against a stale OH baseline.** Phase 2 cites GPT OH = 73.8 %, which is the *pre-Step-D* number from the original Tier-1 OH writeup. The post-Step-D OH GPT is 79.76 % — but the Step D writeup itself warned its number "is a mix of 3 original-Tier-1 chunks and 3 post-fix chunks — it is not a clean re-measurement." No clean post-fix OH baseline exists (Prong 1 was paused before a full re-dispatch). The +10.7 pts cross-state Δ in the Phase 2 convo should be read with this caveat.

2. **Within-state cross-model, the failure-mode mix is very different.** WI: Claude has 2 scoreability-unstable + 9 value-unstable; GPT has 7 scoreability-unstable + 5 value-unstable. **GPT's WI scoreability instability concentrates in `lobbying_definitions` (4 of 7)** — the chunk that asks "what counts as lobbying / who counts as a lobbyist," exactly where the WI §13.62(11) qualitative trigger sits. GPT abstains inconsistently across runs on the definitional questions.

3. **Claude is state-invariant at the headline (85.71 % both states), but composition shifted.** OH Claude scor_un=4 was entirely in `registration_thresholds`; that chunk's scor_un dropped to 0 on WI (after a single `incomplete` from the `TimeThresholdCell` failure in item 1). The 2 WI Claude scor_un cells live in `lobbying_definitions` and `registration_mechanics_and_exemptions`.

**Implication for v2.2 metrics:** the headline `pct_stable` masks two qualitatively distinct failure modes (value-unstable = "which number is right?", scoreability-unstable = "should this even be scored?"). v2.2 should surface the 4-component breakdown alongside the headline, and per-chunk cuts — the chunk-level signal is stronger than the aggregate (e.g., GPT's 4-of-15 = 26.7% scor_un rate in `lobbying_definitions` reads very differently from the 8.3% aggregate rate).

### Bonus — Item 2 capture (v2.2 enum gap ledger opened)

Plan said item 2 was "capture/standing-instruction work for whenever they get touched." Item 1's investigation already established the exact evidence (6/6 runs emitting `unit="days_per_reporting_period"` for `lobbyist_registration_threshold_time_percent`), so the natural moment to capture is now. Opened [`../results/v2_2_schema_inputs.md`](../results/v2_2_schema_inputs.md) with the first entry: `TimeThresholdCell.unit` needs at minimum `days_per_reporting_period`, possibly also `days_per_6_month_reporting_period`, with candidate additions (`days_per_quarter`, `days_per_session`, `days_unspecified_period`) flagged for the v2.2 design pass. The ledger also raises a v2.2 design question (single source of truth for unit enums vs per-cell) and a cross-row coordination question (the row-ID `_time_percent` suffix is misleading once non-percent units are allowed — keep the suffix as family-of-measure or split the row?).

## Provisional Findings

- **Item 1 root cause is hypothesis (b)**: the original Fix A was scoped to scalar `DecimalCell.value`; dict-shape cell inner `Decimal` fields are reached only through a code path that doesn't run any per-field coercion.
- **The 4 WI principal-side gaps are not parser bugs.** They reflect the deliberate Tier-2/Tier-3 scope decision in `wi-disclosure-explore`, tracked at GH #28.
- **σ_noise composition reveals different failure modes between models.** Claude's instability is dominated by value disagreement, GPT's by scoreability disagreement; the right metric design should surface both.
- **No clean cross-state σ_noise baseline currently exists.** The Phase 2 convo's +10.7 pts uses the pre-fix OH GPT 73.8 %; the post-Step-D OH GPT is 79.76 % but is a mixed-state number; the only honest cross-state measurement would be a full OH re-dispatch with current fixes applied.

## Decisions Made

- **Item 1 fix landed under TDD.** Added `_coerce_dict_shape_inner_decimals` helper; 3 new tests; full suite green.
- **Don't amend the Phase 2 convo.** Dan: prefer this session's convo + results doc carries the baseline-issue context; the Phase 2 convo stays as the historical record of what was known then.
- **Don't run an OH re-dispatch this session.** Out of handoff scope; capture as a potential followup if Dan decides it's worth the spend later.
- **Captured Item 2 in this session** rather than deferring. The evidence is already in hand from Item 1 investigation; deferring would be ship-then-patch-each-gap.

## Results

- [`../results/20260601_principal_filings_aggregation_source.md`](../results/20260601_principal_filings_aggregation_source.md) — Item 5 writeup. Verdict: deliberate Tier-2/Tier-3 scope decision, tracked at GH #28. Back-linked from the cross-validation doc.
- [`../results/20260601_sigma_noise_composition_oh_wi.md`](../results/20260601_sigma_noise_composition_oh_wi.md) — Item 6 writeup with full per-(state, model, chunk) breakdown.
- [`../results/sigma_noise_composition/sigma_noise_composition_oh_wi.py`](../results/sigma_noise_composition/sigma_noise_composition_oh_wi.py) — reproducibility script for Item 6.
- [`../results/sigma_noise_composition/output.txt`](../results/sigma_noise_composition/output.txt) — saved script output.
- [`../results/v2_2_schema_inputs.md`](../results/v2_2_schema_inputs.md) — v2.2 design ledger; first entry is the `TimeThresholdCell.unit` enum gap.

Code changes (Item 1):
- `scripts/tier_0_direct_read_smoke.py` — added `_coerce_dict_shape_inner_decimals` helper + call site in the dict-shape branch of `_instantiate_cell`. Added `import typing` at the top of the module.
- `tests/test_tier_1_legal_axis.py` — 3 new tests in the Group 5 Fix A section.

Doc updates:
- `docs/active/wi-tier1-direct-read/results/20260601_wi_statute_vs_portal_spending.md` — added a 2026-06-01 update banner where the original doc posed the scrape-loss-vs-portal-choice question, back-linking to the Item 5 writeup.

## Open Questions

- **Tier-3 SLAE reconnaissance.** No one has yet inspected a single WI Tier-3 SLAE itemization page. A 1-page fetch + DOM inspection would confirm whether all 4 gaps Dan surfaced are actually addressable from those pages or whether some still need a different source. Natural Phase-1 of GH #28 work.
- **Should an OH re-dispatch be funded?** Item 6 surfaces that the only honest cross-state σ_noise comparison requires a clean post-fix OH baseline. ~$2.50, ~20 min. Decision deferred — capture as a potential followup if Dan wants it.
- **v2.2 unit-enum source-of-truth.** Per-cell enum literals vs a shared `UnitsRegistry`. Recorded in the v2.2 ledger, not for resolution now.
- **v2.2 row-ID `_time_percent` suffix** for `lobbyist_registration_threshold_time_percent` becomes misleading once non-percent units are allowed. Two options surfaced in the v2.2 ledger (keep as family-of-measure vs split into two rows). For the v2.2 design pass.

## Carry-overs from the plan that remain open

- **Item 3 (Citations API for adjudication)** — still gated on Dan's closer review of the 18 disagreement cells in `results/20260601_wi_statute_vs_portal_spending.md`. No movement this session.
- **Item 4 (bake portal cross-validation into the MI session)** — standing instruction for the next-state run; nothing to ship this session.
- **Item 7 (GH #31, parallelize dispatch loop)** — independent track; not touched this session.

## Sycophancy check

Reviewed: did I push back where evidence warranted? The Item 6 finding that the Phase 2 convo's cross-state Δ is computed against a stale baseline is a real correction to a prior session's analysis — I didn't soften it, and surfaced it to Dan before the writeup landed. The Item 5 verdict ("not parser bugs, deliberate scope decision") is more favorable to the prior `wi-disclosure-explore` work than a "scrape loss" verdict would have been, but the evidence (archived plan explicitly excludes Tier-3, GH #28 already tracking) supports that reading on its own merits, not because it's flattering.

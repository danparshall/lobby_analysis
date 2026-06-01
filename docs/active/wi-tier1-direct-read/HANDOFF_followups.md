# HANDOFF — wi-tier1-direct-read followups (post-Phase 3)

**For:** the next agent/session, picking up after the 2026-06-01 Phase 2 + 3 close.
**Predecessor:** `HANDOFF.md` (the Phase 2 runbook — phase done, kept as historical record).
**Convo that produced these followups:** `convos/20260601_wi_tier1_phase2_run.md` (especially the Phase 3 + Next sections).

This file lists the two concrete investigations to run **before** extending the Tier-1 harness to a third state. (NC is no longer the planned third state — see "Decision: MI substitutes for NC" below.) Issue [#31](https://github.com/danparshall/lobby_analysis/issues/31) — dispatch loop parallelization — is also pending but is independent: it can be done in parallel with these followups or saved for the next-state run.

---

## Item 1 — Fix A regression investigation (`magnitude: int → Decimal` on dict-shape value path)

### What we saw

All 6 runs (Claude × 3, GPT × 3) on the `registration_thresholds` chunk failed instantiation of `lobbyist_registration_threshold_time_percent` with **identical** error class:

```
key=['lobbyist_registration_threshold_time_percent', 'legal']
reason='instantiation_failed'
arguments: {
  'value': {'magnitude': 5, 'unit': 'days_per_reporting_period'},
  'cited_section': '§13.62(11)',
  'confidence': 'high',
  ...
}
error: 2 validation errors for TimeThresholdCell
  magnitude: Input should be an instance of Decimal [type=is_instance_of, input_value=5, input_type=int]
  unit:      Input should be 'hours_per_quarter', 'hours_per_year', 'days_pe…' [literal]
```

The `magnitude: int=5` rejection is the load-bearing part of this item. (The `unit` literal-enum gap is item 2.)

### Why this is a *regression*, not a new bug

The archived `extraction-harness-brainstorm` branch (Tier-2 Step D, merged + archived 2026-05-24 as part of the Prong 1 pause) explicitly shipped **"Fix A: int→Decimal coercion"** under TDD, with the writeup claiming verification against real API output:

> Tier-2 (2026-05-21): Fixes A (int→Decimal coercion), B (dict-shape value roster hint), C (null FreeTextCell → abstention) shipped under TDD; Step D re-dispatch verified A and C against real API output, original class-B `TypeError` cleared.

So Fix A *should* be handling exactly this. The fact that 6/6 runs on a fully fresh statute still fail with `Input should be an instance of Decimal` on an `int` input means Fix A is either:

- (a) Not present on the current `wi-tier1-direct-read` HEAD (lost in a merge / wasn't actually merged from `extraction-harness-brainstorm` to main),
- (b) Present but doesn't operate on the *roster-driven dict-shape value path* — i.e., when the model emits `{"magnitude": 5, "unit": "..."}` as a nested-dict `value` argument (vs a scalar value passed positionally to the cell constructor),
- (c) Present and correct but bypassed by a different code path that constructs cells directly from `record_cell` arguments without going through the fixed coercion.

Hypothesis (b) is the strongest prior — dict-shape values are exactly what `TimeThresholdCell` accepts (`{magnitude, unit}` are its fields), and the OH Tier-2 work might have only addressed scalar cell types.

### How to investigate

1. **Find Fix A on disk.** Search the archived `docs/historical/extraction-harness-brainstorm/` for the commit/convo where Fix A landed (likely a 2026-05-21 entry in that RESEARCH_LOG). Confirm the file + function it touched.
2. **Verify Fix A merged forward to main.** `git log --all --oneline -- <fixed_file>` should show Fix A's commit reachable from main. If not, that's hypothesis (a) — and the fix needs porting.
3. **If Fix A is present on main**, trace the cell-instantiation code path in `scripts/tier_1_direct_read_legal_axis.py` (`_parse_and_instantiate` around lines 455+) and follow into `lobby_analysis.models_v2`. Pay attention to how `record_cell` arguments are unpacked — does the coercion run before pydantic validation, or only on a path that's bypassed for dict-shape values?
4. **Reproduce locally** by replaying the failing arguments from any one of the 6 WI registration_thresholds JSONs:
   - Example: `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/claude-opus-4-7__registration_thresholds__run1.json` → `errors[0].arguments`
   - The arguments dict has the exact `value` + `axis` + `row_id` that triggers the failure.
   - Add a regression test under `tests/test_tier_1_legal_axis.py` (or a new `tests/test_cell_coercion_regression.py`) that reproduces the failure, watch RED, then fix it.

### Acceptance for "Fix A regression cleared"

- A test exists that, given the exact failing arguments from one of the WI registration_thresholds JSONs, currently RED, then GREEN after fix.
- Re-running the WI Tier-1 dispatch (resume-only, no new spend — the 36 files already exist) wouldn't re-encounter this class. Note: the *cell value* is still un-encodable because of item 2's enum gap; this item is about the type-coercion, not the enum.
- A short writeup in the convo doc notes which of (a)/(b)/(c) was correct, so the architectural lesson lands.

### Cost

Zero API spend. Pure code investigation against existing JSON artifacts.

---

## Item 2 — `TimeThresholdCell.unit` literal-enum gap (v2.2 design input)

### What we saw

Even if Fix A is applied to the value-coercion side, the same `lobbyist_registration_threshold_time_percent` cell would *still* fail instantiation because the `unit` field has a literal-enum constraint and neither `days_per_reporting_period` nor `days_per_6_month_reporting_period` is in the allowed set:

```
unit: Input should be 'hours_per_quarter', 'hours_per_year', 'days_pe…'
```

(The error message truncates after "days_pe…" — pull the full Literal type from `src/lobby_analysis/models_v2/` to see exactly what's allowed.)

This is *not* a code bug. It's a v2.1 schema design choice that doesn't cover WI's structure. Both models, on every run, correctly identify the WI structure (5 days per reporting period); the schema can't represent it.

### Why this is the load-bearing finding from this run

This is the exact shape of evidence the *gather-first* pivot (2026-05-24) was paused to collect:

> **Pivot: gather-first.** Collect per-(state, vintage, question) answers in a flexible intermediate JSON (freeform answer + statute citation + confidence) across all priority states, then design the v2.2 typed schema from observed reality.

WI gave us the first concrete v2.2 schema input: `TimeThresholdCell` needs more `unit` values. The right move is **not** to patch v2.1 (the schema is locked); it's to **capture this finding in a v2.2 design ledger** so when the v2.2 design pass runs, it has the corpus to design against.

### How to capture

1. **Open or create the v2.2 design ledger** — there isn't one yet on this branch. Suggested location: `docs/active/wi-tier1-direct-read/results/v2_2_schema_inputs.md` (or a similar repo-level path if the gather-first effort gets its own branch). Either way, the file is a structured record of "rows where the model agrees on what the statute says but the v2.1 cell shape can't represent it."
2. **First entry:** `TimeThresholdCell.unit` — needs at minimum `days_per_reporting_period` and `days_per_6_month_reporting_period`. Possibly also `days_per_year`, `days_per_quarter`, and an "unspecified-period days" variant.
3. **Cross-reference with `compendium/NAMING_CONVENTIONS.md` §7** (the C3 unit-suffix rule). §7 specifies `_threshold_<measure>_<unit>` naming; the *unit-enum content* is currently scattered across cell-type definitions in `models_v2/`. The v2.2 design ledger should also note whether unit enums should consolidate to a single source of truth or stay per-cell.

### Acceptance for "v2.2 enum gap captured"

- A markdown file at the chosen path exists with at least one entry (`TimeThresholdCell.unit`), cross-referencing the source evidence (the 6 WI registration_thresholds JSONs).
- The entry includes: cell type, current allowed values, observed model-emitted value(s), proposed addition(s), source statute citation.

### Cost

Zero API spend. Pure design-doc capture.

---

## Decision: MI substitutes for NC as the next-state target

The Phase 3 writeup proposed NC as the next state for multi-state-reliability validation (NC has the flat data layout already established by the `wi-disclosure-explore` Tier-2 convention). Dan superseded that 2026-06-01: **the next state will be MI**, not NC. No reasons logged in the convo — assume MI was chosen for either data-quality or political-significance reasons per the README's "5–8 priority states" framing.

This affects the followups in one way only: the next-state branch should be `mi-tier1-direct-read` (or similar) and the test fixtures should use MI's bundle path. Item 1's investigation is state-independent; item 2's `v2_2_schema_inputs.md` will gain MI's entries when MI runs.

---

## Item 3 — Citations API for inter-model adjudication (CANDIDATE, not yet decided)

**Source:** Dan, 2026-06-01 afternoon, while reviewing the statute-vs-portal cross-validation (`results/20260601_wi_statute_vs_portal_spending.md`).
**Status:** OPEN CANDIDATE. Dan said: *"I'll look, but sounds like the disagreement is large enough to be worth using the Citations API."* The "I'll look" part is load-bearing — Dan wants to do a more detailed read of the 18 disagreeing cells before committing to the integration.

### What we found that prompted this

The WI cross-validation surfaced **18 of 65 jointly-stable cells (27.7%)** where Claude and GPT deterministically disagree at high confidence on the same legal question. The σ_noise metric (per-model) is correct as designed but doesn't capture this — there's no current report of inter-model alignment.

Concentrated in the `lobbyist_spending_report` chunk (~13 of 18): Claude reads "is this info required to flow through the lobbyist?" → TRUE, citing §13.68(1)(*). GPT reads "is the *lobbyist* the filer?" → FALSE, citing the same §13.68(1) but characterizing it as principal-filed. Portal data (`WI_lobbyist_filings.tsv` has zero expenditure columns) settles 13/13 in GPT's favor.

### What to evaluate

Before integrating the Citations API:

1. **Read the 18 disagreeing cells closely.** They're enumerated in `results/20260601_wi_statute_vs_portal_spending.md` (13 explicitly in the headline table; the other ~5 are in `lobbying_definitions` / `registration_*` / `enforcement_and_audits` chunks — re-run `/tmp/wi_within_model_sigma.py` to enumerate).
2. **Categorize the disagreements.** Are they all the same shape (one model over-includes, one reads literally)? Or are there qualitatively different failure modes? The integration is more valuable if the disagreements span shapes.
3. **Confirm Citations API is the right mechanism.** The `extraction-harness-brainstorm` archive already has a `retrieval_v2/` module that uses Citations API (per STATUS.md). Check if extending that to Tier-1 dispatch is a small lift or a rewrite. The two questions:
   - (a) Does Citations API on the model's output expose the substring(s) of the source it was citing — i.e., can we recover "Claude was looking at §13.68(1) sentence A" vs "GPT was looking at §13.68(1) sentence B"?
   - (b) If yes, what's the wrapper code to capture the citation spans alongside each `record_cell` tool call?

### What this would actually buy us

Adjudication. For each of the 18 cells:
- If both models cited the **same span** → disagreement is about *interpretation* of the same statute text. That's the case where downstream reconciliation (a Tier-2 pass, or a v2.2 schema decision) makes the call.
- If they cited **different spans** → at least one model was looking at the wrong text. That's a *retrieval / context-window* issue, solvable by extracting better statute slices.

Without Citations API, we can't distinguish these. With it, the inter-model disagreement rate becomes a structured signal rather than a flat number.

### Cost

API spend dominated by the re-dispatch (probably ~$3 to re-run the lobbyist_spending_report chunk against both models if we just want to validate the integration on the disagreement cells). Plus engineering time to wire up the Citations API wrapper.

### Decision gate

This item should NOT be implemented until Dan has done the closer review of the 18 cells. If after review he says "yes, integrate" — then this item becomes a concrete code task. If he says "no, this isn't worth it" — drop the item and stop here.

---

## Item 4 — Bake portal cross-validation into the MI session

**Source:** Generalized from this WI session.

When MI Tier-1 runs, **don't separate the legal-axis extraction from the portal-comparison analysis.** Do them in the same session, using the same comparison structure as `results/20260601_wi_statute_vs_portal_spending.md`. The pattern that worked here:

1. Run Tier-1 on MI 2025 statute bundle → 36 result JSONs.
2. Load `releases/mi/` TSVs (assuming an MI scrape lands before the Tier-1 run; if not, that's an upstream dependency to flag).
3. For each spending-report cell (chunks `lobbyist_spending_report` + `principal_spending_report`), build the cell-to-column mapping by hand. Catalog cell-vs-portal status as MATCH / CROSS-FILE MATCH / GAP / UNRESOLVED.
4. Surface the inter-model disagreements separately; treat them as candidates for item 3 (Citations API) if that lands.

Expected payoff: identifies MI-specific compendium-taxonomy gaps + cross-validates per-cell model disagreements + grows the cross-state portal-coverage matrix the README's "Required × {Legal, Practical}" framing has been waiting for.

### Cost

The legal-axis run is ~$2-4 per state. The portal-comparison analysis is ~30 min of focused work per state.

---

## Item 5 — Investigate principal-filings aggregation (portal design vs scrape loss?)

**Source:** The 4 transparency gaps surfaced in this session's principal-side mapping.

All 4 WI principal-side gaps reduce to: **statute requires itemized reporting (compensation paid to each lobbyist, gifts/entertainment as a separate category, indirect costs, itemized format generally), but `WI_principal_filings.tsv` exposes only a single `total_expenditure` scalar.** Two hypotheses:

- **(A) Portal-publication choice.** The underlying expense statements are itemized in the source filings, but the WI Ethics Commission publishes only the top-line aggregate to the public-facing portal. The itemized data exists but is not surfaced.
- **(B) Scrape loss.** The `wi-disclosure-explore` Tier-2 parser dropped the itemized fields during materialization. The data is in the source PDFs/portal pages but didn't make it into the TSVs.

Investigation:

1. Read the Tier-2 parser modules at `src/lobby_analysis/io/wi/` (per the archived `wi-disclosure-explore` summary in STATUS.md). Specifically look at whether `principal_meta` or `lobbyist_time_report` parsers see itemized fields and intentionally drop them, or whether they only encounter aggregates.
2. If parsers see and drop itemized fields → it's a scrape loss; the fix is to re-run the scrape capturing those fields, no portal-side change needed.
3. If parsers only encounter aggregates → it's a portal-design choice; the gap is real and either un-fixable (only aggregates published) or would require an XLS/PDF source separate from the live portal.

Note for sequencing: this investigation is also an answer for **what the practical-side data layer can ever look like for WI**, so it's worth doing before MI commits to a parallel `releases/mi/` shape.

### Cost

Pure code reading + maybe a small re-scrape probe; no significant API spend.

---

## Item 6 — σ_noise WI-vs-OH composition study

**Source:** Phase 3 writeup noted GPT's `n_scoreability_unstable` jump 2 → 7 between OH and WI.

The aggregate σ_noise = pct_stable conflates "wrong value drift" with "wrong scoreability decision drift." These have different epistemic status (a model flipping a value is different from a model flipping between "yes it's required" and "the statute is silent on this"). For both OH and WI we have run-level data — decomposing pct_stable into its components and comparing across states is a metric-design exercise, no API spend.

### Cost

Pure analysis of existing artifacts. Could be done as a small results doc.

---

## Item 7 — already tracked

GH issue [#31](https://github.com/danparshall/lobby_analysis/issues/31) — parallelize the Tier-1 dispatch loop. Independent of all other items here; no further capture needed.

---

## Suggested order of work

The branch is in a state where the next agent could pick up multiple of these in parallel. Suggested:

1. **Item 1 (Fix A regression) first.** Until Fix A is understood, every state with a similar `magnitude: int` emission will hit the same error class — and we won't know whether it's a coercion bug or a model bug. Cheap investigation, no API spend.
2. **Item 5 (principal-filings aggregation) in parallel with item 1.** Different code surfaces; doesn't conflict. Important to know before MI.
3. **Item 2 (TimeThresholdCell enum gap) after item 1** so the v2.2 entry can correctly distinguish the coercion gap from the enum gap.
4. **Item 3 (Citations API evaluation) — wait for Dan's review.** Don't start until Dan has read the 18 disagreement cells closely and made the call.
5. **Item 6 (σ_noise decomposition) anytime** — cheap, orthogonal.
6. **Item 4 (portal cross-validation) when MI Tier-1 runs** — that's the natural slot.
7. **#31 (parallelization) anytime, but doesn't gate anything.**

---

## Open / flagged items (carry-overs)

- **`HANDOFF.md`** (Phase 2 runbook) is now stale but retained as a historical record of how Phase 2 was set up. Do not delete; do not edit.
- **`_ORIGINATING_CONVO`** constant in `scripts/tier_1_direct_read_legal_axis.py` still points at the OH Tier-0 convo (`convos/20260520_tier_0_direct_read_execution.md`) — documents method lineage, stamped into provenance alongside correct `state_abbr`/`vintage_year`. Left as-is per the Phase 1 convo's "Known minor item" note. Update post-hoc if a more recent provenance pointer is wanted.
- **The intermediate symlink** `.worktrees/wi-tier1-direct-read/.env.local → .worktrees/compendium-source-extracts/.env.local → main/.env.local` is weird-but-functional. The middle hop points into an archived worktree dir that still exists on disk (not registered to git worktree list but the directory persists). The clean fix: `ln -sf ../../.env.local .worktrees/wi-tier1-direct-read/.env.local`. Not blocking.

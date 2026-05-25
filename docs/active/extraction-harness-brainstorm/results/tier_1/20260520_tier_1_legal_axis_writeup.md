<!--
Generated during: convos/20260521_tier_1_legal_axis_execution.md (execution session)
Plan: plans/20260520_tier_1_direct_read_legal_axis.md
Originating convo: convos/20260520_tier_0_direct_read_execution.md
-->

# Tier 1 — Direct-read legal-axis run: writeup + σ_noise

**Run date:** 2026-05-21 (UTC) · **Machine:** Dans-MacBook-Air · **State-vintage:** OH 2025
**Scope:** legal (de jure) axis only, 6 chunks, 84 cells, `[claude-opus-4-7, gpt-5.2] × 6 chunks × 3 runs` = 36 dispatches.

## What the run does

`scripts/tier_1_direct_read_legal_axis.py` scales the Tier-0 direct-read smoke
to a legal-axis-only run over the 6 chunks that carry the CPI-2015 C11 **de
jure** items. The OH 2025 statute bundle (30 sections, ≈36K tokens) ships once
in a cache-controlled system prompt; each chunk's legal-only cell roster is a
per-chunk user message. Each `(model, chunk, run)` triple is dispatched
independently, parsed into typed `CompendiumCell`s, and checkpointed to its own
JSON. It reuses Tier-0's schemas / tools / parser / `_instantiate_cell` /
statute loader; it owns its dispatch wrappers and system prompt (see Deviations).

## Step 1 — CPI-2015 C11 de-jure items → live v2 rows → chunks

The 6 CPI de-jure items resolve to **exactly 6 chunks** (the plan's expectation):

| CPI item | de-jure compendium row(s) | chunk |
|---|---|---|
| IND_196 | `def_target_legislative_branch`, `def_target_governors_office`, `def_target_executive_agency`, `def_target_independent_agency`, `def_target_legislative_staff` | `lobbying_definitions` |
| IND_197 | `lobbyist_registration_threshold_compensation_dollars` *(renamed from `compensation_threshold_for_lobbyist_registration` — NAMING_CONVENTIONS §10.1)* | `registration_thresholds` |
| IND_199 | `lobbyist_registration_renewal_cadence` | `registration_mechanics_and_exemptions` |
| IND_201 | `lobbyist_spending_report_required`, `lobbyist_spending_report_includes_itemized_expenses`, `lobbyist_spending_report_includes_total_compensation` | `lobbyist_spending_report` |
| IND_203 | `principal_spending_report_required`, `principal_spending_report_includes_compensation_paid_to_lobbyists` | `principal_spending_report` |
| IND_207 | `lobbying_disclosure_audit_required_in_law` | `enforcement_and_audits` |

**Row-ID drift (minor, immaterial to dispatch):** the projection-mapping doc's
working name for IND_201's third row, `lobbyist_spending_report_includes_compensation`,
is not a literal v2 row ID and is not in the §10.1 resolver table (which only
records the 15 renames). The live row is `lobbyist_spending_report_includes_total_compensation`,
in the same `lobbyist_spending_report` chunk. Because the runner dispatches each
chunk's **full legal roster** (not individual CPI rows), the chunk set is
unaffected.

The 6 chunks carry **84 legal cells** (the `axis=='legal'` filter drops 9
practical cells from the 3 mixed chunks — `registration_mechanics_and_exemptions`,
`lobbyist_spending_report`, `enforcement_and_audits`).

## Run facts

| Model | Calls | Wall-clock | Cost (est.) | Cells scored (of 84) | Unscoreable | Errored |
|---|---|---|---|---|---|---|
| claude-opus-4-7 | 18 | 635 s | $1.61 | 81 | 0 | 3 |
| gpt-5.2-2025-12-11 | 18 | 349 s | $1.33 | ~75 (varies 73–76) | ~6 (varies 6–7) | 3 |

Session cost **$2.94** — within the plan's $2–4 estimate, well under the $10
ceiling. No per-call cost exceeded $0.19. Resume was not exercised (the run
completed in one pass) but the checkpoint files are all present.

### Per-(model, chunk) cell counts — scored / unscoreable / errored

| Chunk (legal cells) | claude (per run) | gpt (per run) |
|---|---|---|
| `lobbying_definitions` (15) | 15 / 0 / 0 | 15 / 0 / 0 |
| `registration_thresholds` (6) | 5 / 0 / 1 | 0 / 5 / 1 |
| `registration_mechanics_and_exemptions` (8) | 8 / 0 / 0 | 8 / 0 / 0 *(run2: 7 / 1 / 0)* |
| `lobbyist_spending_report` (30) | 29 / 0 / 1 | 27–29 / 0–1 / 1 |
| `principal_spending_report` (23) | 22 / 0 / 1 | 22 / 0 / 1 |
| `enforcement_and_audits` (2) | 2 / 0 / 0 | 1–2 / 0–1 / 0 |

## σ_noise — inter-run agreement across N=3

`stable` = all 3 runs scored the same value, or all 3 abstained.

| Model | cells | stable | value-unstable | scoreability-unstable | incomplete | **% stable (σ_noise proxy)** |
|---|---|---|---|---|---|---|
| claude-opus-4-7 | 84 | 72 | 9 | 0 | 3 | **85.7 %** |
| gpt-5.2-2025-12-11 | 84 | 62 | 13 | 3 | 6 | **73.8 %** |

**Read the raw figure with two deflators in mind** — the true model-reasoning
noise floor is meaningfully *higher* than 85.7 % / 73.8 %:

1. **Unpinned-enum label churn inflates "value-unstable."** `EnumSetCell` /
   `EnumCell` rows whose domains aren't yet pinned in `enum_domains.py`
   (`def_lobbying_activity_types`, `def_lobbyist_actor_types`,
   `lobbying_disclosure_audit_required_in_law`) come back with *different label
   strings for the same underlying meaning* run to run — Claude:
   `retirement_system` vs `retirement_system_lobbying`; GPT cycles through
   `attempting_to_influence_legislation` /
   `direct_communication_with_officials_to_influence_legislation` / etc. The
   exact-match agreement metric scores these as unstable even though the set
   *membership* is consistent. This is downstream of an unfinished schema task,
   not model noise.
2. **The 3 error classes (below) account for all `incomplete` cells.** Those
   cells can't be classified as stable/unstable at all — they're a wiring/schema
   problem, not a noise measurement.

**Noise is correlated within a (chunk, run), not IID per cell.** In
`principal_spending_report`, a *block* of ~5–6 cells (`includes_general_issues`,
`includes_lobbyist_contact_info`, `includes_lobbyist_names`,
`includes_principal_contact_info`, `lists_lobbyists_employed`) flips together —
Claude's run 2 reads the principal-report section differently from runs 1 & 3
and the whole block moves with it (`[True, False, True]`). A re-run is not 84
independent coin-flips; it is ~6 chunk-reads. This matters for how the Ralph
loop should treat σ_noise — the effective sample size is closer to
chunks × runs than cells × runs.

## Errors — 3 new classes, zero of the Tier-0 string/int class

**Criterion 3 is met:** the Tier-0 `value="2"`-string-vs-int failure does **not**
recur. Claude scored all 4 `DecimalCell`s in `registration_thresholds` cleanly —
it emitted them as JSON strings, which the new `_coerce_scalar_value` adapter
converts `str → Decimal`. The fix works.

The 18 error entries are **3 genuinely new classes** (per the plan: reported,
**not patched**):

| Class | Rows | Mechanism | Occurrences |
|---|---|---|---|
| **A — `int → Decimal` strict rejection** | `lobbyist_filing_de_minimis_threshold_dollars`, `lobbyist_filing_itemization_de_minimis_threshold_dollars` (`DecimalCell`) | Model emits a bare JSON number `50`; `CompendiumCell` strict mode requires a `Decimal` *instance* and rejects `int`. The Step-2 coercion covers `str → Decimal` but not `int → Decimal`. | 3 (GPT only) |
| **B — dict-shape cell fed a scalar** | `lobbyist_registration_threshold_time_percent` (`TimeThresholdCell`) | Claude emitted a string for a `{magnitude, unit}` dict-shape cell. The plan explicitly anticipated this for IND_197. | 3 (Claude only) |
| **C — non-optional `FreeTextCell` fed `null`** | `lobbyist_spending_report_cadence_other_specification`, `principal_spending_report_cadence_other_specification` | Both models, all 3 runs, emit `value: null` — correctly reasoning "no *other* specification applies, the cadence isn't 'other'." But `FreeTextCell.value` is non-optional `str`. | 12 (both models, 100 % of runs) |

Notes:
- **Class A is an irony of the Step-2 prompt nudge.** The nudge ("emit numeric
  answers as JSON numbers, not quoted strings") worked — GPT obeyed and emitted
  `50` instead of `"50"` — and that is the exact input strict-`Decimal`
  rejects. The fix is a one-line extension of `_coerce_scalar_value`
  (`int → Decimal`), but per the plan that is a Tier-2 finding, not a mid-run
  patch.
- **Class C is not a model error — it is a schema gap.** Both models did the
  *right* thing. `FreeTextCell` simply cannot represent "not applicable."
  Conditional `_other_specification` rows need an optional value field (or the
  models should emit `record_unscoreable_cell` / a sentinel — a design call).
- **Class B is the anticipated dict-shape failure.** It is the *only* dict-shape
  cell in the 84-cell legal roster, and it failed every Claude run. The
  `_instantiate_cell` dict-shape path is still untested by real API output —
  the model needs an explicit nudge toward the `{magnitude, unit}` shape, or
  the tool schema needs a per-cell-class `value` shape.

## Cross-model agreement

Of the 74 cells both models scored in run 1, **63 agree (85 %)**, 11 disagree.
The disagreements split into two kinds:

- **Label-format only (not substantive)** — `def_lobbying_activity_types`,
  `def_lobbyist_actor_types`, `lobbying_disclosure_audit_required_in_law`. Same
  meaning, different unpinned-enum strings. Resolves when enum domains are
  pinned.
- **Substantive disagreements** worth a verifier's attention:
  - `lobbyist_registration_renewal_cadence`: Claude `2`, GPT `24`. **Both look
    wrong.** OH §101.72(B) requires updated statements "not later than the last
    day of January, May, and September of each year" — 3×/year, ≈ every 4
    months. The `IntCell` "months" encoding has no clean value for an
    enumerated-dates cadence. *This is a compendium-schema finding:* the row's
    int-months type is a poor fit for real statutory cadences. GPT's own runs
    `[24, 2, 3]` are maximally unstable on this cell.
  - `def_actor_class_elected_officials`, `principal_spending_report_includes_business_nature`,
    `lobbyist_spending_report_categorizes_expenses_by_type`,
    `..._includes_expenditure_per_issue`, `lobbying_violation_penalties_imposed_in_practice` —
    genuine `True`/`False` reads of the same statute that differ. These are the
    verifier agent's core workload.

## The registration_thresholds divergence — the headline finding

On `registration_thresholds`, **Claude scored 5/6 cells; GPT abstained on all
5 scalar cells.** This is not random — GPT's abstention reasons are substantive
and consistent across all 3 runs: *"the bundled Ohio sections define
'legislative agent' qualitatively (main purpose) … not a dollar threshold."*

OH triggers lobbyist status with a **qualitative** test ("main purpose,"
"during at least a portion of the registration period"), not a dollar/time
threshold. The two models encode that fact differently:

- **Claude** writes `compensation_threshold = 0` — reading the
  mapping doc's intended semantics (`0` / `None` = "no threshold, anyone paid
  is a lobbyist").
- **GPT** abstains — "there is no dollar threshold *to report*."

Both readings are defensible; the mapping doc favors Claude's `0` encoding. But
this is the **abstention-calibration problem from Tier-0, now reproduced at
chunk scale**: a de-jure scorer hitting a qualitative-trigger statute must know
whether the compendium wants `0` or an abstention. The Phase-2 verifier needs
an explicit policy on this — it is the single largest source of Claude/GPT
divergence in the run (it alone is 5 of GPT's per-run abstentions).

## Hand-eyeball

Cited sections were spot-checked against the OH 2025 bundle:

- All sampled `cited_section` values are real, in-bundle OH Chapter 101 sections
  (`§101.70`, `§101.72`, `§101.73`, `§101.79`, `§101.99`). No hallucinated
  citations found in the sample.
- `enforcement_and_audits`: Claude's `penalties_imposed_in_practice = True`
  (§101.99) and `audit_required_in_law` (§101.72(G); §101.79) are consistent
  with Tier-0's verbatim verification of those exact sections — §101.99 sets
  misdemeanor penalties, §101.72(G) is a completeness review, §101.79 is a
  discretionary AG investigation, no audit mandate. (The enum *value* churns
  `no_audit_required` / `review_only` / `none` across runs — same finding,
  three unpinned labels.)
- `registration_thresholds`: Claude's `compensation = 0`, `expenditure = 0`,
  `itemization_de_minimis = 50` (§101.73(B)(3)) are plausible against the
  statute; not exhaustively verified cell-by-cell (84 cells; the plan asked for
  a sample).

## Deviations from the plan (documented)

- **Tier-1 owns its dispatch wrappers.** Tier-0's `dispatch_anthropic` hardcodes
  `max_tokens=4096`, sized for a 4-cell chunk. `lobbyist_spending_report` has 30
  legal cells; at Tier-0's observed Claude rate (~335 tok/cell) that needs
  ~10K output tokens. Tier-1's wrappers raise the cap to 16384. Tools/model
  constants are still reused from Tier-0.
- **Tier-1 owns its system prompt** — adds the de-jure-only framing and the
  "numeric answers as JSON numbers" nudge (plan Step 2's belt-and-suspenders).
  Tier-0's prompt template is left unchanged (its results are committed).
- **Coercion target for `DecimalCell` is `Decimal`, not `float`** (the plan's
  prose said `float`). Under strict mode a `float` fails a `Decimal | None`
  field; `Decimal` is the correct target.
- **GradedIntCell coercion tested with on-grid `"50"`**, not the plan's `"2"` —
  `GradedIntCell`'s grid validator rejects `2` regardless of coercion. A plain
  `IntCell` covers the `"2" → int` case.
- **Commit granularity** — Steps 2/3/5 landed as 3 commits (coercion; runner;
  tests) rather than the plan's per-step commits, so each commit leaves the
  suite green. TDD order (tests written first, watched fail, watched pass) was
  honored.

## Success criteria

| # | Criterion | Result |
|---|---|---|
| 1 | Step 2/3/5 tests green; no new suite failures beyond the 3 `test_pipeline.py` baseline | ✅ 515 passed, 3 baseline failures, 8 skipped |
| 2 | 36-dispatch run completes with all reachable result files written | ✅ 36/36 |
| 3 | Zero `instantiation_failed` errors of the string/int class; new classes stop-and-reported | ✅ zero string/int; 3 new classes reported, not patched |
| 4 | No `practical`-axis cell ever dispatched (verified in saved rosters) | ✅ 0 practical cells in all 36 saved rosters |
| 5 | A σ_noise figure per model | ✅ Claude 85.7 %, GPT 73.8 % |

## Surprises

- **The Step-2 prompt nudge created error Class A.** Telling the model to emit
  JSON numbers fixed the `str` problem and walked GPT straight into the
  `int → Decimal` strict-mode rejection. The schema's `value` typing needs to
  be solved at the schema/adapter level, not by prompt engineering.
- **GPT abstains on a whole chunk for a defensible reason.** It is not flaky on
  `registration_thresholds` — it consistently reads OH's qualitative trigger as
  "no dollar threshold." Abstention here is a *philosophy*, not noise.
- **Error Class C is the models being correct and the schema being wrong.**
  100 % of runs, both models, emit `null` for a not-applicable conditional
  cell. The cleanest failure in the run is a schema gap.
- **Noise is chunk-correlated.** The `principal_spending_report` block-flip
  shows a single run-level misread moving 5–6 cells at once.

## Verdict — is legal-axis direct-read ready to scale?

**Qualified yes, with three blockers to clear first.**

The architecture holds at 6-chunk / 84-cell scale: the run completed, cost was
trivial ($2.94), no practical cells leaked, and the string/int bug is gone.
Claude's 85.7 % raw stability (higher once enum-label artifact is removed) is a
usable noise floor.

Three things must be fixed before scaling to all 15 chunks / multi-vintage:

1. **Schema/adapter typing** — extend `_coerce_scalar_value` to `int → Decimal`
   (Class A); make conditional `FreeTextCell` rows optional or give them a
   defined N/A encoding (Class C); give the dict-shape `value` an explicit
   per-cell-class schema or prompt shape (Class B). These are ~3 small,
   well-understood fixes — none architectural.
2. **Pin enum domains** for the unpinned `EnumCell` / `EnumSetCell` rows, or the
   σ_noise metric and cross-model agreement will keep undercounting agreement on
   semantically-identical answers.
3. **Abstention-calibration policy** — the `registration_thresholds`
   qualitative-trigger divergence (Claude `0` vs GPT abstain) is the dominant
   cross-model disagreement and Tier-0's open question reproduced at scale. The
   Phase-2 verifier cannot be designed without it.

Tier-1 stops here, at σ_noise + hand-eyeball, per the plan. Projecting these
cells onto CPI's published OH scores waits on the `phase-c-projection-tdd`
projection functions.

## Files produced

`docs/active/extraction-harness-brainstorm/results/tier_1/` — 36 JSON files,
one per `(model, chunk, run)` triple, each with a provenance block, the legal
roster dispatched, raw response, parsed cells, unscoreable emissions, and
errors. Plus this writeup.

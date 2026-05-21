# Tier-2 — Three schema/adapter fixes from the Tier-1 run Implementation Plan

**Goal:** Clear the 3 instantiation-error classes the Tier-1 legal-axis run surfaced (`int→Decimal` strict rejection; dict-shape cell fed a scalar; non-optional `FreeTextCell` fed `null`), so a Tier-1 re-run produces zero `instantiation_failed` errors of any known class.

**Originating conversation:** [`../convos/20260521_tier_1_legal_axis_execution.md`](../convos/20260521_tier_1_legal_axis_execution.md)

**Context:** Tier-1 ([writeup](../results/tier_1/20260520_tier_1_legal_axis_writeup.md)) confirmed the Tier-0 string/int bug is fixed but surfaced 18 errors in 3 genuinely new classes. Per the Tier-1 plan's stop-and-report discipline they were documented, not patched. They are the named blocker (item 1 of 3) on the Tier-1 verdict's "qualified yes" for scaling legal-axis direct-read to all 15 chunks / multi-vintage. All three are small, well-understood, and non-architectural.

**Confidence:** High for A and B (mechanism fully understood from the saved error payloads). Moderate for C — the fix is small but involves a design choice (touch a shared `models_v2` model, or change scorer behavior); the choice is Step C0 of this plan and a Question below.

**Architecture:** Two of the three fixes land in the shared instantiation adapter `_instantiate_cell` / its helper `_coerce_scalar_value` in `scripts/tier_0_direct_read_smoke.py` (A) and in the Tier-1 runner's roster rendering (B). C is either a one-field change to `models_v2/cells.py` or a scorer-behavior change — resolved in Step C0. No new modules.

**Branch:** `extraction-harness-brainstorm` (worktree at `/Users/dan/code/lobby_analysis/.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, `uv`, Pydantic v2 (strict mode), Anthropic SDK, OpenAI SDK.

---

## Pre-flight reads (mandatory before touching code)

1. [`../results/tier_1/20260520_tier_1_legal_axis_writeup.md`](../results/tier_1/20260520_tier_1_legal_axis_writeup.md) — the "Errors — 3 new classes" section is the spec for this plan.
2. [`../convos/20260521_tier_1_legal_axis_execution.md`](../convos/20260521_tier_1_legal_axis_execution.md) — the originating session.
3. `scripts/tier_0_direct_read_smoke.py` — `_coerce_scalar_value` + `_instantiate_cell` (Fix A lands here).
4. `scripts/tier_1_direct_read_legal_axis.py` — `render_legal_roster` (Fix B lands here).
5. `src/lobby_analysis/models_v2/cells.py` — the cell classes; note `model_config = ConfigDict(frozen=True, strict=True)` on `CompendiumCell`, and `FreeTextCell.value: Annotated[str, Field(max_length=500)]` (non-optional).
6. `tests/test_tier_1_legal_axis.py` — the existing 18-test file; new tests append here.

## Prerequisites — verify BEFORE writing code

`ls` / `grep` each; trust the filesystem.

1. **Tier-1 tests green:** `uv run pytest tests/test_tier_1_legal_axis.py tests/test_tier_0_smoke_parser.py` → 35 passed.
2. **Saved Tier-1 error payloads present:** `ls docs/active/extraction-harness-brainstorm/results/tier_1/*.json | wc -l` → 36. These carry the exact failing `arguments` dicts — use them as fixture ground truth, do not invent inputs.
3. **Both API keys** only needed for the optional Step D re-dispatch verification, not for A/B/C unit work. If absent, A/B/C still complete; Step D stops and asks.

---

## Fix A — `int` / `float` → `Decimal` coercion (TDD)

**Root cause:** `_coerce_scalar_value` coerces JSON-*string* scalars only. The Tier-1 prompt nudge ("emit numeric answers as JSON numbers") made GPT emit a bare JSON `50` (Python `int`) for a `DecimalCell`. `CompendiumCell` runs Pydantic strict mode; a strict `Decimal | None` field rejects `int` (and `float`). The coercion never fired because the input was not a `str`.

**Fix:** In `_coerce_scalar_value`, for `DecimalCell`, also coerce a non-string numeric: `int → Decimal(value)`, `float → Decimal(str(value))` (via `str()` to avoid binary-float artifacts — `Decimal(0.1)` is wrong, `Decimal("0.1")` is right). A `bool` must NOT be coerced (it is an `int` subclass but never a valid threshold) — leave it to fail. The existing `str → Decimal` path stays. Uncoercible inputs still raise `ValueError` (caller records the error).

- Steps: (1) write the failing unit tests (Step E); (2) run, watch fail; (3) implement; (4) run, watch pass; (5) commit `tier-2: coerce int/float to Decimal in _coerce_scalar_value`.

## Fix B — dict-shape `value` prompt hint (prompt fix + re-dispatch verification)

**Root cause:** the legal roster has exactly one dict-shape cell — `lobbyist_registration_threshold_time_percent` (`TimeThresholdCell`, fields `{magnitude, unit}`). The shared `record_cell` tool schema's `value` is a loose scalar `oneOf`; the roster line names only `expected_cell_class=TimeThresholdCell`. Claude emitted a bare string for it, all 3 runs → `TypeError('TimeThresholdCell expects dict-shaped value, got str')`.

**Fix:** in `render_legal_roster` (`scripts/tier_1_direct_read_legal_axis.py`), when a roster cell's `expected_cell_class` is a dict-shape class, append the expected dict keys to that cell's roster line, e.g.
`… expected_cell_class=TimeThresholdCell — emit value as a JSON object {"magnitude": <number|null>, "unit": <one of: hours_per_quarter|hours_per_year|days_per_year|percent_of_work_time>}`.
Derive the dict keys from `cls.model_fields` minus the common `CompendiumCell` fields (`cell_id`, `conditional`, `condition_text`, `confidence`, `provenance`) — do not hardcode per class. The 4 dict-shape classes are `TimeThresholdCell`, `TimeSpentCell`, `CountWithFTECell`, `EnumSetWithAmountsCell`; only `TimeThresholdCell` is in the 6-chunk legal roster, but the helper must be general.

- This is a prompt-engineering fix. Its unit test asserts the *roster-rendering behavior* (the line for a dict-shape cell names the expected keys); its real verification is the Step-D re-dispatch.
- `_instantiate_cell`'s existing `TypeError` on a non-dict `value` is correct and stays — keep it as the loud failure if the hint doesn't take.
- Steps: (1) write the failing roster-rendering test (Step E); (2) run, watch fail; (3) implement; (4) run, watch pass; (5) commit `tier-2: dict-shape value shape hint in render_legal_roster`.

## Fix C — non-optional `FreeTextCell` fed `null`

**Root cause:** `lobbyist_spending_report_cadence_other_specification` and `principal_spending_report_cadence_other_specification` are *conditional* "other-specification" rows — only meaningful when the cadence enum is `other`. Both models, 100 % of runs, correctly emitted `record_cell` with `value: null`. But `FreeTextCell.value: Annotated[str, Field(max_length=500)]` is non-optional → `string_type` validation error. **The models did the right thing; the schema cannot represent "not applicable."**

### Step C0 — resolve the design choice (do this FIRST, with the user)

Three options (see Questions Q1):

- **(a) `FreeTextCell.value: str | None`** in `models_v2/cells.py`. Smallest code change, most semantically honest. **But `models_v2` is shared infrastructure** — `phase-c-projection-tdd` and `oh-statute-retrieval` consume it. Per the repo's multi-committer rule this needs user sign-off and a check that no consumer assumes `FreeTextCell.value` is always a `str`.
- **(b) Scorer behavior change.** Instruct the scorer (system prompt) to emit `record_unscoreable_cell` for a conditional cell whose condition does not hold, instead of `record_cell` with `null`. No schema change; no sister-branch impact. But it overloads `record_unscoreable_cell` (whose `reason` field is framed as "missing evidence," not "not applicable").
- **(c) Sentinel in `_instantiate_cell`.** Treat a `record_cell` with `value: null` for a `FreeTextCell` as an abstention (route it to the `unscoreable_emissions` list, not `errors`). No schema change, no sister-branch impact, no scorer change — purely a Tier-1-side adapter rule. Loses the "value-was-explicitly-null" nuance only if some FreeTextCell legitimately wants empty string (it would emit `""`, not `null`).

**Recommendation: (c)** for this plan — it is the only option that touches neither shared `models_v2` nor the scorer's semantics, and `null` for a non-optional text field is unambiguously "not applicable." If the user prefers the schema to be honest, (a) is the right longer-term answer but should be a coordinated `models_v2` change, not bundled here.

### Step C-impl — implement the chosen option (TDD)

- For (c): in `_instantiate_cell` (or the Tier-1 runner's `_parse_and_instantiate`), before instantiation, if `expected_cell_class is FreeTextCell and arguments["value"] is None`, record it as an abstention with `reason="conditional cell not applicable (value null)"` rather than attempting instantiation. Write the failing test first, implement, commit `tier-2: treat null-valued FreeTextCell record_cell as an abstention`.
- For (a) or (b): the implementing agent re-scopes Step C-impl per the user's choice and surfaces the changed test list before writing code.

## Step D — re-dispatch verification (exploration, not TDD)

After A/B/C are green, re-run the 2 chunks that carried the errors to confirm the fixes hold against real API output:

- Delete (move, per "prefer mv over rm for research artifacts" — to a `_superseded/` subdir) the 6 result files for `registration_thresholds` + the 6 for `lobbyist_spending_report` + `principal_spending_report`, OR run into a fresh `results/tier_1_v2/` directory. **Do not overwrite the Tier-1 results in place** — they are the evidence behind the committed writeup.
- Re-run `scripts/tier_1_direct_read_legal_axis.py` (resume logic dispatches only the missing triples). Both API keys required — if absent, stop and ask.
- **Pass criterion:** zero `instantiation_failed` errors across the re-dispatched chunks. Any remaining error is a new finding — stop and report, do not patch.
- Cost: ~12 re-dispatches ≈ $1; keep the $1/call + $10 session ceilings.
- This step is optional-but-recommended; A/B/C can be committed without it. If skipped, say so in the writeup.

## Step E — Tests (write ALL of these before any A/B/C implementation)

**Testing Plan**

Behavior tests, appended to `tests/test_tier_1_legal_axis.py`, against real `models_v2` classes (no mocks):

- **Fix A:** `_instantiate_cell` with a real `DecimalCell` spec and `value=50` (Python `int`) instantiates to a cell whose value round-trips to `"50"`; `value=50.5` (float) → `"50.5"` (exact, via `Decimal(str(...))`); `value=True` (bool) raises (not coerced); the existing `value="500"` (str) path still passes. Test `_coerce_scalar_value` directly for the numeric cases too.
- **Fix B:** `render_legal_roster` for a roster containing a `TimeThresholdCell` spec produces a line that names both `magnitude` and `unit`; for a scalar-cell roster the lines are unchanged (no spurious shape hints).
- **Fix C (option c):** a `record_cell`-shaped arguments dict with `value=None` for a real `FreeTextCell` spec is routed to abstention, not to the errors list — test the routing predicate / `_parse_and_instantiate` behavior directly, no API call. (If the user picks (a)/(b), the implementing agent rewrites this test accordingly and surfaces it.)

The re-dispatch (Step D) is the integration test for the whole plan — exploratory, with the explicit pass criterion above.

NOTE: I will write *all* tests before I add any implementation behavior.

## Edge cases to anticipate

- **`Decimal(str(float))` vs `Decimal(float)`** — always go through `str()`; `Decimal(0.1)` carries binary-float noise.
- **`bool` is an `int` subclass** — Fix A must exclude `bool` explicitly or a `True`/`False` slips into a `Decimal`.
- **A dict-shape cell legitimately not in the bundle** — the model should still be able to `record_unscoreable_cell`; the Fix-B hint must not push it to fabricate a `{magnitude, unit}`.
- **Fix C option (c) and a real empty-string answer** — a FreeTextCell that genuinely has an empty value should emit `""`, not `null`; (c) only intercepts `null`. Confirm no legal FreeTextCell wants `null` as a real value (the 2 rows are both `_other_specification`, so this holds).
- **Sister-branch blast radius (option a only)** — if C resolves to (a), grep `phase-c-projection-tdd` and `oh-statute-retrieval` worktrees for `FreeTextCell` consumers before changing the field.

---

**Testing Details:** Three behavior-focused unit-test groups appended to `tests/test_tier_1_legal_axis.py` — numeric→Decimal coercion against the real `DecimalCell` class; dict-shape roster-line rendering; null-FreeTextCell abstention routing. None test datastructures or mocks. The 12-dispatch re-run (Step D) is the integration test, exploratory, with an explicit zero-error pass criterion.

**Implementation Details:**
- Fix A: extend `_coerce_scalar_value` in `scripts/tier_0_direct_read_smoke.py` — `int`/`float` → `Decimal` for `DecimalCell`, excluding `bool`.
- Fix B: a roster-line shape hint in `render_legal_roster`, keys derived from `cls.model_fields` minus the 5 common `CompendiumCell` fields.
- Fix C: Step C0 picks the option; recommended (c) = treat `null`-valued `FreeTextCell` `record_cell` as an abstention in the Tier-1 adapter; no shared-schema change.
- Step D re-dispatches into a fresh directory; never overwrites the committed Tier-1 results.
- Commits: one per fix (A, B, C), plus a writeup commit if Step D runs.

**What could change:**
- If Step D surfaces a *new* error class, it is a finding to surface, not a patch — same discipline as Tier-1.
- If the user picks Fix C option (a), the change widens into a coordinated `models_v2` edit with sister-branch verification, and this plan's Step C is re-scoped.
- `IntCell`/`BoundedIntCell`/`GradedIntCell` fed a JSON `float` (e.g. `50.0`) would hit the same strict-mode wall as Class A; not observed in Tier-1, so out of scope here — flag if Step D surfaces it.

**Questions:**
1. **Fix C design choice** — (a) make `FreeTextCell.value` optional in shared `models_v2` (honest, but touches sister branches); (b) scorer emits `record_unscoreable_cell` for inapplicable conditional cells (overloads "unscoreable"); (c) Tier-1 adapter treats a `null`-valued `FreeTextCell` as an abstention (no shared-schema or scorer change). Plan recommends (c); confirm before Step C-impl.
2. **Run Step D this session, or defer?** It needs both API keys and ~$1. If deferred, A/B/C still ship; the re-dispatch becomes a follow-up.
3. **Enum-domain pinning and the verifier abstention-calibration policy** (Tier-1 writeup blockers 2 and 3) are deliberately *not* in this plan — confirm they stay as separate future work.

---

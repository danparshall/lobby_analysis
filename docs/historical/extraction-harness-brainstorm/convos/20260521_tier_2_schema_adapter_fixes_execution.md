# Tier-2 schema/adapter fixes — execution

**Date:** 2026-05-21
**Branch:** extraction-harness-brainstorm

## Summary

Executed [`plans/20260521_tier_2_schema_adapter_fixes.md`](../plans/20260521_tier_2_schema_adapter_fixes.md)
end-to-end under strict TDD. The plan clears the 3 `instantiation_failed`
error classes the Tier-1 legal-axis run surfaced (and reported, not patched,
per Tier-1's stop-and-report discipline). All three fixes are small,
non-architectural, and were well-understood from the saved Tier-1 error
payloads — confidence held through implementation with no surprises.

The session opened by settling the plan's three Questions with the user.
Q1 (the Fix C design choice) resolved to option **(c)** — the adapter-side
sentinel — keeping the fix entirely Tier-1-side, with no change to shared
`models_v2` (option a) and no scorer-semantics change (option b). Q2: Step D
(the ~$1 / ~12-call re-dispatch verification) **deferred** — it needs both
API keys, currently unset; A/B/C ship without it and the re-dispatch becomes
a follow-up. Q3: enum-domain pinning and the Phase-2 verifier's
abstention-calibration policy (Tier-1 writeup blockers 2 and 3) confirmed to
stay **out of scope** as separate future work.

All Step-E tests (A/B/C) were written first as one batch, watched fail
correctly (5 driving tests RED, 5 guard tests green-before-and-after), then
the three fixes were implemented in sequence — each turning its tests green.
Full suite: **525 passed**, 8 skipped, 3 pre-existing `test_pipeline.py`
failures (the documented `data/portal_snapshots/` baseline, unrelated, not
on this machine). Four commits on top of `99de3cd`.

## Topics Explored

- The 3 Tier-1 error classes, traced from the writeup's "Errors" section and
  the saved error payloads to the exact code paths.
- Fix A — `_coerce_scalar_value` only coerced JSON-*string* scalars; the
  Tier-1 "emit numbers as JSON numbers" nudge made GPT emit a bare `int`,
  which Pydantic strict mode rejects for a `Decimal` field.
- Fix B — `render_legal_roster` named only the cell class; the shared
  `record_cell` tool schema's `value` is a loose scalar `oneOf`, so a model
  emitted a bare string for the one dict-shape cell (`TimeThresholdCell`).
- Fix C — the conditional `*_other_specification` rows correctly emit
  `value: null`, but `FreeTextCell.value` is a non-optional `str`. The models
  were right; the schema cannot represent "not applicable."

## Provisional Findings

- All three fixes behaved exactly as the plan's mechanism analysis predicted.
  The RED phase failed precisely where expected (the Fix C failure showed the
  `string_type` validation error — the Class C mechanism — confirming the
  diagnosis before any code changed).
- No new error classes surfaced *in unit-test scope*. Whether the fixes hold
  against real API output is unverified — that is exactly what the deferred
  Step D would check.

## Decisions Made

- **Plan Q1 → option (c)** (adapter sentinel). `_parse_and_instantiate` now
  routes a `record_cell` with `value: null` for a `FreeTextCell` to the
  `unscoreable` list as an abstention (`reason: "conditional cell not
  applicable (value null)"`), keeping the call's `row_id`/`axis` so
  `extract_cell_outcome` classifies it as `abstained`.
- **Plan Q2 → defer Step D.** A/B/C shipped without the re-dispatch.
- **Plan Q3 → keep separate.** Enum-pinning and the abstention-calibration
  policy remain future work.
- **Fix B scope call (flagged to the user):** implemented the **keys-only**
  hint — the roster line for a dict-shape cell now names its expected
  JSON-object keys. The plan's line-51 example *also* expands the `unit`
  `Literal` domain, but the plan's Step-E test spec (line 94) and
  Implementation Details (line 115) both specify keys only. With Step D
  deferred, a general enum-domain renderer would ship unverified, so it was
  left out as scope creep. If Step D later shows the model fumbles the `unit`
  enum, that is a precise, evidence-driven follow-up.
- Left the pre-existing `ruff format` / E402 drift in `scripts/` (prior-session
  code in the parsers and metric functions) untouched — not this session's
  code, no CI gates it, and reformatting it would be unrelated churn. My own
  additions are `ruff check`- and `ruff format`-clean.

## Results

No analysis outputs this session — pure code. No Tier-1 results were
overwritten. (A writeup commit was only planned for the case where Step D
ran; Step D was deferred.)

## Commits

On top of `1be98a5` (the Tier-2 plan commit; worktree at
`.worktrees/extraction-harness-brainstorm/`):

- `0403218` — `tier-2: coerce int/float to Decimal in _coerce_scalar_value`
  (Fix A). Also lands all Group-5 behavior tests in
  `tests/test_tier_1_legal_axis.py` (Step E writes all tests up front; the
  B/C tests are not yet green at this commit).
- `76c77e6` — `tier-2: dict-shape value shape hint in render_legal_roster`
  (Fix B, keys-only hint).
- `fd8b656` — `tier-2: treat null-valued FreeTextCell record_cell as an
  abstention` (Fix C, option c).
- `00e7257` — `tier-2: ruff-format the Tier-2 test additions` (format-only).

## Open Questions / Next Steps

- **Step D — re-dispatch verification** (the integration test for the whole
  plan). Deferred this session. Needs `ANTHROPIC_API_KEY` + `OPENAI_API_KEY`
  and ~$1 / ~12 calls. Re-run the 2 error-bearing chunk groups into a fresh
  `results/` directory (never overwrite the committed Tier-1 results); pass
  criterion = zero `instantiation_failed` errors. Any remaining error is a
  new finding — stop and report, do not patch.
- **Enum-domain pinning** (Tier-1 writeup blocker 2) — still future work.
- **Phase-2 verifier abstention-calibration policy** (Tier-1 writeup blocker
  3) — still future work.
- **Fix B effectiveness** — the keys-only hint's real-world effect on the
  `unit` enum is unverified until Step D runs.

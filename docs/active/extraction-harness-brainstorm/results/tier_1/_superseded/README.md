# SUPERSEDED — Tier-1 result JSONs for the 3 error-bearing chunks

These 18 files (`registration_thresholds`, `lobbyist_spending_report`,
`principal_spending_report` × `[claude-opus-4-7, gpt-5.2]` × 3 runs) are the
original Tier-1 legal-axis dispatches from the 2026-05-20 run. Every one of
them carried exactly one `instantiation_failed` error — the 3 error classes
the Tier-2 plan
([`../../../plans/20260521_tier_2_schema_adapter_fixes.md`](../../../plans/20260521_tier_2_schema_adapter_fixes.md))
fixed:

- `registration_thresholds` — claude ×3: error class B (`TimeThresholdCell`
  fed a bare string); gpt ×3: error class A (`DecimalCell` fed a bare `int`).
- `lobbyist_spending_report` / `principal_spending_report` — all 12: error
  class C (non-optional `FreeTextCell` fed `null`).

They were **moved here, not deleted**, by the Step-D re-dispatch verification
(2026-05-21) so the re-run could regenerate these triples in
`../` against the now-committed A/B/C fixes without overwriting the evidence
behind the committed Tier-1 writeup
([`../20260520_tier_1_legal_axis_writeup.md`](../20260520_tier_1_legal_axis_writeup.md)).

The replacement post-fix dispatches live one directory up, in `../`.

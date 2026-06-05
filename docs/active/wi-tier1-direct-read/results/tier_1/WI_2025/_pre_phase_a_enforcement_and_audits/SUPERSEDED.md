# SUPERSEDED — `enforcement_and_audits` JSONs pre-Phase-A

**Archived:** 2026-06-05
**Branch:** `wi-ralph-cpi-renewal-cadence`
**Originating plan:** [`plans/20260605_phase_a_yaml_audit_at_scale.md`](../../../../../../../docs/active/wi-ralph-cpi-renewal-cadence/plans/20260605_phase_a_yaml_audit_at_scale.md)
**Why archived:** Phase A Stage A2.b verification dispatch. The 6 `enforcement_and_audits` chunk JSONs preserved here predate the Stage A1 YAML additives applied to:

- `lobbying_disclosure_audit_required_in_law` (EnumCell hand-craft, this session — YES/MODERATE/NO domain)
- `lobbying_violation_penalties_defined_in_law` (BinaryCell, already-additive from predecessor session)

After Stage A1 these prompts changed; the dispatcher would resume-skip these checkpoints. Preserved per the "prefer mv over rm for research artifacts" memory.

These are the post-`v2.1_pattern_c_enforcement` JSONs (the 6/6 SUCCESS dispatch following the buggy-prompt BinaryCell-vocab-mismatch session; per
[`convos/20260605_pattern_c_v2_1_execution.md`](../../../../../../../docs/active/wi-ralph-cpi-renewal-cadence/convos/20260605_pattern_c_v2_1_execution.md)).
The current Phase A re-dispatch should:
- Confirm `_defined_in_law` value stability under the bulk-applied BinaryCell additive (the additive marker was added on top of the existing prompt; should be a no-op).
- Verify `_audit_required_in_law` resolves under the new YES/MODERATE/NO EnumCell additive — predecessor session flagged Claude run3 drift to YES from 6/6 MODERATE baseline.

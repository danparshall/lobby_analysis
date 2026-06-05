# SUPERSEDED — `registration_thresholds` JSONs pre-Phase-A

**Archived:** 2026-06-05
**Branch:** `wi-ralph-cpi-renewal-cadence`
**Originating plan:** [`plans/20260605_phase_a_yaml_audit_at_scale.md`](../../../../../../../docs/active/wi-ralph-cpi-renewal-cadence/plans/20260605_phase_a_yaml_audit_at_scale.md)
**Why archived:** Phase A Stage A2.b verification dispatch. The 6 `registration_thresholds` chunk JSONs preserved here predate the Stage A1 YAML additives applied to:

- `lobbyist_filing_itemization_de_minimis_threshold_dollars` (DecimalCell-Optional hand-craft)
- `lobbyist_filing_de_minimis_threshold_dollars` (DecimalCell-Optional hand-craft)
- `lobbyist_registration_threshold_expenditure_dollars` (DecimalCell-Optional hand-craft)
- `lobbyist_registration_threshold_compensation_dollars` (already-additive iter 5)
- `lobbyist_filing_de_minimis_threshold_time_percent` (already-additive Pattern B)
- `lobbyist_registration_threshold_time_percent` (DEFER — long-tail TimeThresholdCell, NOT touched)

After Stage A1 these prompts changed; the dispatcher would resume-skip these checkpoints and emit pre-additive answers without an archive. Preserved as negative-result evidence per the "prefer mv over rm for research artifacts" memory.

These are the iter-5 chunk-mate-spillover JSONs (per
[`convos/20260604_phase_b_silent_unit_mismatch_sweep.md`](../../../../../../../docs/active/wi-ralph-cpi-renewal-cadence/convos/20260604_phase_b_silent_unit_mismatch_sweep.md)).

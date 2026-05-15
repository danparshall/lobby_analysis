# Rename-candidate review and plan drafting

**Date:** 2026-05-14
**Branch:** compendium-naming-docs

## Summary

Sub-session 2 on `compendium-naming-docs`. Sub-session 1 (kickoff, convo `20260514_naming_taxonomy_kickoff.md`) audited the 181-row v2 compendium and surfaced 8 rename candidates in §10 of `compendium/NAMING_CONVENTIONS.md`. This session walked Dan through each of the 8 candidates one at a time (accept / defer / reject) with a pre-scanned downstream-consumer fan-out, then drafted the rename-execution plan referenced by the kickoff handoff.

All 8 candidates were accepted, yielding 15 row renames + 1 README typo fix. The plan stays in this branch as a planning artifact; the actual rename execution is timed for a future branch once `phase-c-projection-tdd` and `extraction-harness-brainstorm` lifecycles settle (per the kickoff scope decision).

Downstream-consumer pre-scan resolved one important question: the v1.1 Pydantic models in `src/lobby_analysis/models/` are **row-ID-agnostic** (no candidate row IDs appear in `compendium.py`, `state_master.py`, or `compendium_loader.py`). The merge-cost consumer is the **future** v2 Pydantic work on `extraction-harness-brainstorm` (where `chunks_v2` and downstream models are likely to enumerate row IDs).

## Topics Explored

- §10 of `compendium/NAMING_CONVENTIONS.md` — 8 rename candidates, in rough order of justification-clarity
- Downstream-consumer pre-scan via grep across the worktree:
  - `tools/freeze_canonicalize_rows.py` — already encodes v1→v2 renames in `RENAMES` / per-row dicts; the right place to extend
  - `docs/historical/compendium-source-extracts/results/projections/*.md` — references appear but historical docs are immutable archives
  - `src/lobby_analysis/` v1.1 Pydantic models — row-ID-agnostic, no fan-out cost
  - Sister branches (`extraction-harness-brainstorm`, `oh-statute-retrieval`, `phase-c-projection-tdd`) — the kickoff already flagged these as coordination-cost surfaces
- Candidate 2 LV-1 sub-choice: `_filing_*` (semantic faithfulness) vs `_spending_report_*` (cluster uniformity) — Dan picked `_filing_*` after the pushback on cluster-uniformity-as-consistency framing
- Doc inconsistency surfaced: §10 Issue 2 header says "5 rows" but the body table lists 6 rows (1 Newmark + 4 FOCAL + 1 LV-1). To fix in the rename-execution branch alongside the renames themselves.

## Provisional Findings

- All 8 candidates have strong-enough justification to land. The expected-resistant ones were Candidate 3 (high-traffic threshold trio) and Candidate 7 (defensible-to-leave-alone definitional rows); Dan accepted both.
- Candidate 2's LV-1 row is the only case where rename target was non-obvious; the decision (`lobbyist_filing_*` over `_spending_report_*`) treats LobbyView schema-coverage observables as a categorically different kind of row than report-contents observables.
- The implementing agent's main coordination headache is the timing — not the renames themselves. The renames are mechanical (extend `tools/freeze_canonicalize_rows.py` with a `V2_TO_V3_RENAMES` dict; regen TSV; update NAMING_CONVENTIONS body). The hard part is picking a moment when sister branches can absorb the change cleanly.

## Decisions Made

- **All 8 rename candidates accepted.** Full mapping table is in the plan.
- **Candidate 2 LV-1 → `lobbyist_filing_distinguishes_in_house_vs_contract_filer`** (the `_filing_*` family, not the cluster-uniform `_spending_report_*`).
- **Candidate 8 (README typo)** lands in the same execution branch as the row renames (not separately).
- **Historical projection-mapping docs in `docs/historical/compendium-source-extracts/results/projections/` stay immutable.** The plan does NOT rewrite them; the old→new rename table in the plan itself is the resolver for archive readers.
- **Doc inconsistency in §10 Issue 2 header (5 rows vs 6 in body) is fixed in the rename-execution branch**, not retroactively in this audit branch.
- **Plan filename: `plans/20260515_rename_execution_plan.md`** (as named in the kickoff handoff; one day forward of today, consistent with the handoff convention).
- **Execution timing: deferred.** The plan is the deliverable from this branch; execution waits on sister-branch lifecycles.

Links: [`plans/20260515_rename_execution_plan.md`](../plans/20260515_rename_execution_plan.md)

## Results

No results files produced this session — the plan IS the deliverable.

## Open Questions

- Final timing for the rename-execution branch: blocked on `extraction-harness-brainstorm` Pydantic-model work and `phase-c-projection-tdd` projection-function rollout. Revisit when both branches have either merged or paused.
- For Candidate 2 LV-1: confirm during execution that no `extraction-harness-brainstorm` Pydantic enum has already absorbed the old name `lobbyist_report_distinguishes_in_house_vs_contract_filer`. If yes, that branch will need a coordinated update.
- For Candidate 3 (high-traffic threshold trio): the new shape `lobbyist_registration_threshold_<measure>_<unit>` introduces a `_<unit>` suffix convention (`_dollars`, `_percent`) that doesn't appear elsewhere in the `lobbyist_registration_*` family. Is this drift acceptable, or should the suffix shape be revisited at execution time? (Probably acceptable — it mirrors `lobbyist_filing_de_minimis_threshold_*` precedent.)

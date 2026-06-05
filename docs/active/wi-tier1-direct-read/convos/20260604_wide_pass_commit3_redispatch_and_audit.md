# Wide-pass Commit 3 — WI re-dispatch + diagnosis; Ralph-loop brainstorm seeded

**Date:** 2026-06-04 (afternoon → evening, immediately after Commit 2)
**Branch:** wi-tier1-direct-read
**Predecessor convo:** [`20260604_wide_pass_commit2_yaml_population.md`](20260604_wide_pass_commit2_yaml_population.md)
**Plan executed:** [`../plans/20260604_wide_prompt_text_pass.md`](../plans/20260604_wide_prompt_text_pass.md) (Commit 3, steps 24-30)
**Audit deliverable:** [`../results/20260604_wi_wide_pass_audit.md`](../results/20260604_wi_wide_pass_audit.md)

## Summary

Executed Commit 3 of the wide-pass plan — WI Tier-1 re-dispatch as a sanity check on the YAML SSOT + opaque-handle renderer landed in Commits 1 + 2. Got Dan's explicit spend sign-off, archived prior JSONs to `_pre_wide_pass/`, dispatched 36 calls (Claude Opus 4.7 + GPT-5.2, 6 chunks × 3 runs), audited results against the narrow-pass baseline.

Headline: **inter-model agreement dropped 98.5% → 90.8%** (jointly-stable cells: 66 → 65, agree: 65 → 59, disagree: 1 → 6). Claude σ_noise dropped 86.90 → 82.14; GPT held at 82.14. Total spend $2.5442 (predicted ~$2.50 ✓); cumulative WI Tier-1 ledger $4.7504 → $7.2946.

Initial read suggested a real architectural regression. Diagnosis (Dan's prompt: "diagnose the n_incomplete jump before deciding") flipped the read entirely: **the opaque-handle renderer is architecturally sound** — Claude emitted clean tool_use blocks with valid handles for every chunk; parser routed correctly; zero leakage. The regression is content-level: **the wide-pass YAML population was too mechanical, copying source-rubric scoring vocabulary verbatim into `prompt:` fields without reconciling rubric vocabulary with the v2 cell type for that row.** YES/MODERATE/NO landed for IntCell; 100/50/0 scoring tiers landed for BinaryCell; both make Pydantic reject the model's faithfully-echoed values.

Decomposed: of the 6 wide-pass disagreements, 3 are newly-stabilized-into-disagree (philosophical "absence = 0 vs unscoreable" disagreements where wide-pass prompts anchored both models into opposing positions — Ralph-tractable); 1 is the real `renewal_cadence` regression (caused by the YES/MODERATE/NO ↔ IntCell mismatch); 2 involve degraded instantiation on previously-unstable or known-mis-axed rows. Across all 36 JSONs: 17 instantiation failures total (vs 7 baseline). 6 are the persisting TimeThresholdCell.unit gap (v2.2 ledger Entry 1); 11 are NEW prompt-vocab/cell-type mismatches affecting 4 specific rows.

Brainstorm seeded the Ralph-loop design with Dan. Key shape: **per-row iteration, anchored to prior-art rubric authors' published scores as the external oracle** (rather than inter-model agreement). Most rubric ground truth turns out to be aggregate per-state, not per-item — so Ralph at row-level can directly use only rubrics with per-item data (PRI 2010 transcribed per-item × 50 states; possibly FOCAL 2024 L-N 2025 Supp File 1; Sunlight 2015 5-tier categorical). Two-layer iteration: layer 1 = "does the prompt let the model emit a value the cell type accepts?" (pre-flight YAML audit, mechanical), layer 2 = "does the value match the oracle?" (Ralph iteration, per-row).

NOT implemented in this session: Phase A pre-flight prompt audit + Phase B Ralph implementation. Both deferred pending Dan's decisions on the brainstorm questions answered + the 9-rubric oracle-granularity audit (separate next session).

## Topics Explored

- **Commit 3 execution.** Got Dan's explicit spend sign-off; pre-flight check (disk 70% used, 59 GiB free; env keys via `uv run --env-file .env.local`; bundle 16 sections; 68 tests pass on `test_tier_1_state_keying.py` + `test_tier_1_legal_axis.py` + `test_source_quotes_yaml.py`); archived 36 prior JSONs to `_pre_wide_pass/`; dispatched cleanly; integrity check confirmed 36 files / `corrupt: []` / per-file `cost_usd_estimate` sum matches log session_cost ($2.5442).

- **Inter-model agreement audit.** Re-ran `wi_intermodel_disagreement.py` against both `_pre_wide_pass/` (to confirm 65/66 narrow-pass baseline) and the new wide-pass JSONs. Confirmed: narrow-pass = 66 stable / 65 agree / 1 disagree (the known Pattern C `lobbying_violation_penalties_imposed_in_practice`); wide-pass = 65 / 59 / 6.

- **Per-row narrow-vs-wide comparison.** Wrote `/tmp/compare_disagreements_narrow_vs_wide.py` to trace each wide-pass disagreement to its narrow-pass status. Surfaced that 3 of 6 disagreements (rows 1-3 in audit doc table) were within-model UNSTABLE in narrow-pass — the wide-pass substantive prompts **stabilized** both models into opposing positions. Not a regression; a higher-resolution exposure of philosophical disagreement.

- **Claude n_incomplete forensics.** Wrote `/tmp/diagnose_claude_incomplete.py` to inspect raw tool_use blocks per failing chunk. Confirmed every failing run emitted clean `record_cell` blocks with valid `handle: 'row_NNN'` fields, correctly routed by the parser. **No renderer/parser/handle-map bug.** Failures all live in `errors[0].reason == "instantiation_failed"` — model emitted a value that the cell type rejected.

- **Instantiation-failure survey.** Wrote `/tmp/instantiation_failure_survey.py` to classify all `instantiation_failed` errors by cell type + error class. Wide-pass: 17 total, on 5 (row, error_class) combos: 6 × TimeThresholdCell.unit (known), 3 × BinaryCell coerce, 3 × IntCell coerce, 3 × EnumCell string-vs-int, 2 × DecimalCell non-negative. Narrow-pass: 7 total, 6 × same TimeThresholdCell.unit + 1 × GPT None→EnumCell. So 11 of the 17 wide-pass failures are NEW, all attributable to prompt-vocab/cell-type mismatches in the YAML.

- **Architecture verdict.** Combining the inter-model audit + the Claude forensics + the instantiation-failure survey: opaque-handle renderer is sound; YAML SSOT loader works; parser works. Wide-pass "regression" is content-level (YAML population was mechanical). Wide-pass also positively validated the design — by anchoring both models into consistent readings, it exposed real philosophical disagreements that the narrow-pass row_id-only renderer was masking via per-row instability.

- **Ralph-loop brainstorm.** Surfaced architectural shape to Dan; Dan reframed convergence criterion from inter-model agreement to **prior-art oracle** (each row's introducing rubric provides the ground truth). Dan's framing: "every row came from prior-art, and so there's at least ONE previously researcher-validated result, for SOME vintage." Asked structural questions; Dan's answers:
  - **Oracle source:** ANY rubric that reads the row (not just `first_introduced_by`). Multi-oracle.
  - **Schema-fit layer:** pre-flight prompt audit BEFORE Ralph (Phase A); Ralph (Phase B) is layer-2 only.
  - **Convergence criterion (Q3 — important):** **most prior art published aggregate per-state scores, NOT per-item.** Ralph at row level can't directly use most rubrics. Only rubrics with per-item ground truth are tractable as row-level oracles.
  - **Human role:** decide automation level AFTER doing the first row by hand.

- **9-rubric oracle-granularity audit (deferred).** Before picking the first Phase B row, walk all 9 rubrics' archived data to document per-item availability. Confirms / disconfirms my recollection that PRI 2010 has per-item × per-state from `pri-2026-rescore` transcription, FOCAL 2024 has per-(state, item) from L-N 2025 Supp File 1, Sunlight 2015 has 5-tier categorical per-state per-category. CPI/Newmark/Opheim/HG/OpenSecrets are likely aggregate-only. Deferred to next session.

- **Phase A scope decision.** Pre-flight prompt audit lives on THIS branch as Commit 4 (promoting the previously-optional/stylistic commit to substantive YAML-quality work). Keeps the wide-pass story unified: wide-pass exposed the issue, same branch fixed it. Then Ralph (Phase B) gets its own branch / session.

## Provisional Findings

- **The opaque-handle renderer + YAML SSOT design is architecturally sound.** Every diagnostic check (clean tool_use emissions, handle map correctness, parser routing, smoke probe) confirmed this. The wide-pass result didn't validate the *prompts*, but did validate the *infrastructure*.

- **The wide-pass populated prompts at the granularity rubric authors did, not at the granularity the v2 cell types require.** This was a foreseeable gap once you state it; the Commit 2 plan focused on lifting source quotes mechanically and didn't address vocabulary-vs-type reconciliation. Fixable per-row in YAML.

- **3 of the 6 wide-pass disagreements are positive signal**, not regression — they're philosophical disagreements about "absence-of-statutory-rule = 0 (Claude) vs unscoreable (GPT)" that the wide-pass prompts anchored both models into consistent positions on. The narrow-pass row_id-only renderer masked these via per-row instability. Ralph-tractable with clarifiers like the narrow-pass Pattern A pattern.

- **1 real regression** — `lobbyist_registration_renewal_cadence` went from agreed (Claude=24, GPT=24) to Claude-incomplete (instantiation failure on YES/MODERATE/NO emission) + GPT changed unit (24 months → 2 years; same biennial reality, different encoding). Cause: wide-pass YAML prompt for this row is CPI's verbatim "A YES score is earned if lobbyists must fill out and file a registration form at least once a year. A MODERATE score is earned where lobbyists must fill out and file a registration form, but with less frequency. A NO score is earned if no such law exists." Cell type is IntCell. Claude faithfully echoed YES/MODERATE; rejected.

- **Sunlight 2015 5-tier scoring** appears to behave better than CPI's YES/MODERATE/NO when landed verbatim in YAML for typed cells: the `lobbyist_spending_report_filing_cadence` row's CPI-100/50/0 prompt has Claude emitting "50" (a string number that EnumCell accepts), while the YES/MODERATE/NO prompt for `renewal_cadence` has Claude emitting "YES" (which IntCell rejects). The cell-type-mismatch failure mode is rubric-dependent, not just cell-type-dependent.

- **The 6 TimeThresholdCell.unit failures persist unchanged** across narrow-pass and wide-pass. v2.2 ledger Entry 1 remains the right disposition — schema-level fix, not prompt-level.

- **Ralph's first move should be Phase A (prompt-vocab audit) followed by an end-to-end-by-hand single-row Phase B iteration** before any infrastructure design. The Phase B candidate row will likely come from PRI 2010 (highest oracle-granularity per recollection — pending audit).

## Decisions Made

- **Commit 3 audit doc landed** at [`../results/20260604_wi_wide_pass_audit.md`](../results/20260604_wi_wide_pass_audit.md).
- **Commit 4 promoted from "optional/stylistic" to substantive Phase A pre-flight YAML audit.** Stays on this branch.
- **Phase B (Ralph) deferred to its own branch / session.** No implementation this session. Brainstorm seeded but not closed.
- **9-rubric oracle granularity audit precedes Phase B row pick.** Standalone session ahead.
- **No retroactive edit of `convos/20260604_wide_pass_commit2_yaml_population.md`.** Its "Open Questions" section flags Commit 3 + Ralph-loop prompt evolution as future work; the wide-pass-introduced quality issues weren't anticipated and shouldn't be backfilled there. Captured here instead.

## Results

- 36 new WI Tier-1 result JSONs at `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/*.json`
- 36 prior JSONs archived at `docs/active/wi-tier1-direct-read/results/tier_1/WI_2025/_pre_wide_pass/*.json` (preserved per Experiment Data Integrity)
- Audit doc: `docs/active/wi-tier1-direct-read/results/20260604_wi_wide_pass_audit.md`
- Cumulative WI Tier-1 spend ledger: **$7.2946** ($4.7504 prior + $2.5442 this session)

## Open Questions

- **Phase B row pick.** Pending 9-rubric oracle-granularity audit. Tentative candidates (subject to confirmation): rows read by PRI 2010 where the wide-pass exposed either an instantiation failure or a "newly-stabilized-into-disagree" pattern. E.g., `lobbyist_registration_renewal_cadence` (PRI E1c? CPI IND_199 — multi-rubric; instantiation failure; clear oracle anchor in PRI 2010 per-item data).
- **Phase A audit scope.** Sweep all 181 rows × YAML prompt × cell type → flag mismatches → patch in YAML. Open: does this also re-derive prompts from the projection-mapping docs differently (e.g., synthesizing instead of lifting verbatim where vocabulary mismatch is unavoidable)? Or just minimal vocabulary patches?
- **Cheap WI re-dispatch after Phase A?** Optional cost-confirm that the patches eliminate the 11 NEW instantiation failures. ~$2.50 again. Worth budgeting?
- **Ralph cost model.** Per-chunk dispatch = $0.05-0.07 × 2 models × 3 runs = ~$0.30-0.40 per iteration of a single row. Tractable for ~50-100 iterations before the cost gets meaningful. But across 181 rows × N iterations, total could climb. Worth thinking about Ralph's per-row stopping rule.
- **Cross-vintage Ralph.** PRI 2010 wants 2010-era statutes; we have OH 2010, OH 2015, OH 2025, WI 2025 on disk. Cross-vintage validation per ⭐ success criterion #3 needs more bundles. Defer to "after first PRI 2010 by-hand row converges."

## Session meta — diagnosis → reframe → defer

The user-initiated diagnosis pivot was load-bearing. My initial read of the wide-pass results was "real architectural regression — Claude's n_incomplete=4 is the new failure mode." That framing would have led to either (a) reverting the wide-pass or (b) chasing a non-existent renderer bug. The actual finding (mechanical YAML population mismatched rubric vocab with cell types) is a much cheaper fix and doesn't touch the renderer at all.

Two specific moments where Dan's pushback shaped the outcome:
1. **"diagnose the n_incomplete=4 jump before deciding"** — forced the forensic check that proved the renderer is fine.
2. **"actually once you diagnose, we will brainstorm Ralph. Do NOT implement Ralph without discussion!"** — pulled me back from a structurally elaborate Ralph design before we'd actually nailed down what the oracle is. The Q3 answer ("most prior art just provided their mapped scores") would have invalidated half of any premature Ralph design.

Pattern echoes Commit 1 + Commit 2's pre-implementation brainstorms: each had a step where I proposed a structurally elaborate solution and Dan pulled back to a simpler form. This session's variant was the same shape, but at the planning level rather than the code level.

No API spend beyond the Commit 3 dispatch.

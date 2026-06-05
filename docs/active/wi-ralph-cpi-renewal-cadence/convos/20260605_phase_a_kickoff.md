# 2026-06-05 (later) — Phase A kickoff: plan written, A0 dropped after Dan's push-back; ready for fresh-session TDD execution

**Plan:** [`../plans/20260605_phase_a_yaml_audit_at_scale.md`](../plans/20260605_phase_a_yaml_audit_at_scale.md)
**Originating convo:** [`20260605_pattern_c_v2_1_execution.md`](20260605_pattern_c_v2_1_execution.md) §"Open questions / next-session candidates" item (i) "Phase A pre-flight YAML audit at scale"

## Pre-flight

Read the handoff's enumerated pre-flight set end-to-end: 4 prior wi-ralph convos (Pattern C v2.1 execution, silent unit-mismatch sweep, iters 1+2, iters 3+4) + sweep results doc + NAMING_CONVENTIONS.md (full doc, including §9 suffix → cell_type hints) + `source_quotes.yaml` end-to-end (755 lines, all 183 entries) + v2.1 TSV header. Clean pre-flight: trajectory matches what handoff promised.

Dan's framing check: confirmed that this session = Phase A planning, multi-state cross-vintage expansion = session-after-Phase-A (batch-dispatch-per-loop, per Dan's clarification; we want the *overall* effect, not per-state optimization). Also confirmed the state-vintage matrix: 15 states have both 2015 + 2025 statutes (AK, AR, CA, CO, FL, IL, MA, MI, NC, OH, PA, TX, WA, WI, WV); NY + WY have only 2010. CO is in (Dan asked specifically).

## Decisions confirmed with Dan

1. **A0 diagnostic dispatch dropped.** My original plan had a Stage A0 (~$0.40) to test whether 135 raw-binary rows currently trip BinaryCell coercion error. Dan's push-back: *"why not just apply the template preemptively, it's free?"* Correct — the additive pattern is purely additive (iter 4 ablation), so we apply it in both branches anyway. A0's information value is near zero relative to its cost, and defensive immunization beats post-hoc diagnosis since multi-state expansion is next (state-specific statute quirks could elicit "Yes" vs "true" inconsistently across new states even if WI is currently clean).
2. **Verification strategy: A2.b — one chunk per touched cell type (~$1.00-1.20).** Dan's call: *"after you make the edits, then we'll test."* Catching a template bug on one WI chunk is cheaper than catching it after dispatching across N states × M vintages. Fits ceiling cleanly (cumulative ~$3.88 worst case, against $5 max).
3. **Stage A0 → Stage A1 chunk pick for BinaryCell verification:** `actor_registration_required` (11 PRI rows, smallest binary-heavy chunk, ~$0.40). Implementing agent confirms at execution time.
4. **v2.1 propagation to main: still deferred.** Branch-local for now. Decision waits until post-A2 verification confirms templates work. Surface to Dan after A2 lands.
5. **Nori flow protocol catch (second-in-two-sessions).** Mid-session Dan asked: *"you're going to follow Nori flow, right? first make the updated plan, and then I'll start a fresh session to TDD?"* — caught me mid-investigation of `enum_domains` (execution prep, not planning). Walked back. **This session = planning + finish-convo only. Fresh session = TDD execution.** Saved as memory entry [[nori-flow-plan-then-fresh-session]].

## What happened (chronological)

1. **Pre-flight reads** — 4 convos + sweep results + NAMING_CONVENTIONS + source_quotes.yaml + v2.1 TSV header.
2. **Wrote /tmp/phase_a_characterize.py** to get precise per-cell-type counts (not just the handoff's "~22 / ~161" approximation). **Result: 183 rows total; 22 already additive (mix of cell-type-vocabulary fixes from Phase B + axis-clarification caveats from wi-tier1 wide-pass); 161 raw rubric-vocab. Of the 161, the breakdown by cell type was the key surprise: 135 are BinaryCell.**
3. **Surfaced Phase A scope characterization to Dan** with 3 decisions: verification strategy, chunk picks, v2.1 propagation.
4. **Dan's "why are we even running A0?" push-back** — load-bearing course correction. Defensive immunization > post-hoc diagnosis. A0 dropped, plan simplifies from 4 stages to 3.
5. **Plan revised in-place** with REVISED 2026-06-05 banner explaining what changed and why. Per-cell-type targets enumerated. Cost projection updated (Total ~$1.00-1.20, comfortably under ceiling).
6. **Started /tmp/phase_a_list_targets.py** to enumerate exact target rows by cell-type bucket with their current prompts (so hand-crafted typed-cell edits could be queued). **Result:**
   - BinaryCell raw (bulk-script): 135
   - DecimalCell-Optional raw (hand-craft): 3 — `lobbyist_filing_itemization_de_minimis_threshold_dollars`, `lobbying_records_copy_cost_per_page_dollars`, `lobbyist_filing_de_minimis_threshold_dollars`
   - Enum-family raw (hand-craft with per-row enum-domain lookup): 9 — including the iter-5 errata-candidate `lobbying_disclosure_audit_required_in_law`
   - Long-tail typed singletons (defer): 11 — distinct cell types like `typed UpdateCadence`, `typed Optional[count_with_FTE]`, `typed Optional[TimeSpent]`, `typed Optional[SectorClassification]`, `typed Optional[TimeThreshold]`, etc. Each needs Phase-B-style template design.
   - Practical-axis-only typed-int (skip): 3 — `lobbying_data_open_data_quality`, `lobbying_disclosure_audit_required_in_practice`, `lobbying_violation_penalties_imposed_in_practice`.
7. **Started investigating `enum_domains.py`** — search came up empty in `src/lobby_analysis/`. Some enum literal definitions live in `models_v2/cells.py` (UpdateCadenceLiteral, IncomeSourceTypeLiteral). Per-row enum-domain registry may be elsewhere or not yet exist.
8. **Dan's Nori-flow catch landed mid-investigation.** Walked back. Finalized plan with explicit "fresh-session-TDD" framing in pre-execution checklist + an enum-domain-lookup note for the implementing agent + linked-artifacts references to the /tmp scripts. Wrote memory entry, this convo, and the doc updates below.

## Findings (load-bearing)

### 1. Phase A scope was bigger than I initially modeled, in one specific way

The handoff said "~161 raw rubric-vocab prompts" without breaking down by cell type. Characterization revealed **135 of those 161 are BinaryCell** — i.e., the cell-type-vocabulary fix has the most surface area where Phase B never iterated (Phase B only confirmed BinaryCell on 1 row, the `_defined_in_law` Pattern C session). The implication: most of Phase A is mechanically extending the BinaryCell template to 135 rows, which is bulk-script-tractable.

### 2. Dan's "skip A0" instinct shrank the plan elegantly

A0 was protecting against the wrong risk. The additive pattern is purely additive (iter 4 ablation), so the action is the same in both branches: apply the template. Defensive immunization beats diagnosis, especially before multi-state expansion where state-specific statute quirks introduce orthogonal risk.

### 3. The 4-cell-type matrix templates carry well — but long-tail typed singletons need per-cell-type design work

11 long-tail typed singletons (UpdateCadence, count_with_FTE, TimeSpent, SectorClassification, TimeThreshold, Optional[int], free-text × 2, etc.) don't fit the 4 confirmed templates. Each needs Phase-B-style hand iteration to design the right additive instruction. Plan defers these explicitly — they're follow-up Phase B candidates, not Phase A.

### 4. The Nori-flow plan-then-fresh-session boundary is load-bearing — and easy to miss

Second time in two sessions this pattern caught me. I sliding-into-execution behavior is "let me just check enum_domains so the plan is more concrete" — and that's execution dressed as planning prep. Saved as memory entry [[nori-flow-plan-then-fresh-session]] sibling to [[doc-system-is-persistent-memory-not-patchwork]].

## Cost ledger

| Item | Cost |
|---|---|
| Pre-flight reads + characterization scripts (/tmp/phase_a_characterize.py, /tmp/phase_a_list_targets.py) | $0 |
| Plan write + 2 revisions (A0-drop + Nori-flow-catch) | $0 |
| **This session subtotal** | **$0** |
| **wi-ralph cumulative** | **$2.6837** (unchanged; against $3-5 ceiling; $0.32-$2.32 remaining) |
| wi-tier1-direct-read cumulative | $7.2946 (unchanged) |
| **Grand total WI Phase 1/2 + Phase B** | **$9.9783** (unchanged) |

## Artifacts produced

- **Plan:** [`../plans/20260605_phase_a_yaml_audit_at_scale.md`](../plans/20260605_phase_a_yaml_audit_at_scale.md) (self-contained for cold pickup; reflects all Dan decisions; explicit fresh-session-TDD framing in pre-execution checklist)
- **Characterization scripts (preserved as session artifacts in /tmp):**
  - `/tmp/phase_a_characterize.py` (~80 lines, ruff-OK, re-runnable; produces per-cell-type additive vs raw counts)
  - `/tmp/phase_a_list_targets.py` (~70 lines, ruff-OK, re-runnable; lists exact target row IDs + current prompts by bucket)
- **Memory entries:**
  - `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_nori_flow_plan_then_fresh_session.md` (new)
  - `MEMORY.md` index updated to reference it
- **No code, no YAML, no API spend.**

## Next-session handoff sentence

*"Pick up branch `wi-ralph-cpi-renewal-cadence`. This is a fresh-session-TDD task. Read `convos/20260605_phase_a_kickoff.md` end-to-end + `plans/20260605_phase_a_yaml_audit_at_scale.md` end-to-end (especially §Pre-execution checklist). Phase A is YAML-only: bulk-apply BinaryCell template to 135 raw-binary rows (mechanical script), hand-craft DecimalCell-Optional additives on 3 rows + EnumCell additives on 9 rows (locate enum_domains registry first; for the `lobbying_disclosure_audit_required_in_law` row, enum is YES/MODERATE/NO and additive may incidentally resolve the iter-5 value-stability flag). Then A2.b verification: dispatch `actor_registration_required` (BinaryCell, ~$0.40) + `registration_thresholds` (DecimalCell-Optional, ~$0.30) + one EnumCell-bearing chunk (~$0.30-0.50). TDD discipline: RED batch first (tests asserting template substrings present), then GREEN. Cumulative wi-ralph $2.6837; budget $0.32-$2.32 remaining of $3-5 ceiling. Per-cell-type target counts: 135 binary, 3 decimal-optional, 9 enum-family, 11 long-tail singletons DEFER, 3 practical-axis-only SKIP."*

## Open questions surfaced this session

- **enum_domains registry location.** Search came up empty. Implementing agent may need to find it elsewhere (e.g., `src/lobby_analysis/models_v2/cells.py` has some Literals; maybe a `compendium/enum_domains.py` or `src/lobby_analysis/compendium/enum_domains.py` was added later) or design per-row enum domains from source quotes if no central registry exists.
- **6-vs-15 chunk count.** Some prior convos say "full-6-chunk re-dispatch ~$2.50" but current manifest has 15 chunks. Either the dispatcher Tier-1-selects 6 of 15 by default or the prior number is outdated. Cost projection should be verified empirically at execution, not assumed from the plan number.
- **The 14 axis-clarification ("Asks whether the LOBBYIST is the named filer") caveats** — these coexist with the cell-type-vocabulary additives this plan adds. Worth a quick review during Stage A1 of whether combining additives might be redundant or contradict on any of those ~14 rows.
- **`_audit_required_in_law` value-stability** (predecessor session flagged Claude run3 drift to YES). EnumCell additive applied this session may incidentally resolve; A2.b dispatch of the chunk hosting this row will surface whether it does.

## Session meta — the Nori flow catch

Dan caught the same slide-into-execution pattern as the predecessor session ("you ARE writing a plan and using Nori / TDD right?"). Acknowledged immediately, saved as memory, walked back the enum_domains investigation (which was execution prep, not planning). Pattern characterization: it shows up as "let me just check X so the plan is more concrete" — and that's execution dressed as planning prep. Plan-finalize + finish-convo is the hard stop; fresh session executes.

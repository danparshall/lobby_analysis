# Phase A — pre-flight YAML audit at scale on v2.1 (183 rows)

**Date:** 2026-06-05
**Branch:** `wi-ralph-cpi-renewal-cadence`
**Originating convo:** `convos/20260605_phase_a_kickoff.md` (this session — to be written at finish-convo)
**Predecessor:** [`convos/20260605_pattern_c_v2_1_execution.md`](../convos/20260605_pattern_c_v2_1_execution.md) — 4-cell-type matrix structurally closed (IntCell ✓ EnumCell ✓ DecimalCell-Optional ✓ BinaryCell ✓)
**Status:** APPROVED 2026-06-05 — Dan endorsed skipping A0 (instinct: "why not just append the template preemptively, it's free?") + A2.b verification ("after you make the edits, then we'll test"). v2.1 propagation to main remains deferred. Stages below are revised accordingly.

## Plan revision 2026-06-05 (post-Dan-discussion)

Original plan had Stage A0 (diagnostic dispatch, ~$0.40) to determine whether raw-binary rows need the BinaryCell template. **Dan correctly observed A0 has near-zero decision value:** the additive pattern is purely additive (iter 4 ablation), so we apply it in both branches anyway. Defensive immunization beats post-hoc diagnosis, especially with multi-state expansion next (13+ states × 2 vintages). **A0 is dropped.** Stages renumbered.

---

## Why this plan exists

Phase B Ralph on WI ran 5 iterations (iters 1–5) plus the Pattern C BinaryCell session, surfacing a 4-cell-type **additive cell-type-aligned vocabulary template set**. Each iteration converged 6/6 on a statute-derived oracle once the right template was applied to the row's YAML prompt. The templates are documented but currently live on only **~5 rows** out of the 183-row v2.1 compendium. **Phase A is the systematic pass that applies the templates to every row that needs one**, so the next multi-state cross-vintage expansion (CO/AK/AR/FL/IL/MA/MI/NC/OH/PA/TX/WA/WI/WV across 2015 + 2025) starts from a YAML where the prompts match the cell-type instantiation table.

Cross-state expansion design is **downstream of Phase A** and is **not** in scope here (per Dan: it will be batch-dispatch-per-loop so we get the overall effect, not per-state optimization). Flag forward, do not conflate.

---

## Current YAML state (characterized, not estimated)

Numbers from `/tmp/phase_a_characterize.py` against v2.1 TSV + `source_quotes.yaml`:

| Cell-type group                                              | Total | Already additive | Raw rubric-vocab |
| ------------------------------------------------------------ | ----: | ---------------: | ---------------: |
| binary                                                       |   151 |               16 |              135 |
| typed Optional[Decimal]                                      |     5 |                2 |                3 |
| typed int 0-100 step 25 (practical-axis-only — not extracted) |     3 |                0 |                3 |
| typed Optional[enum] / typed Set[enum] / typed enum          |     6 |                0 |                6 |
| typed Optional[int_months] (or enum)                         |     1 |                1 |                0 |
| typed Optional[float]                                        |     1 |                1 |                0 |
| enum (legal) + typed int 0-100 (split-axis)                  |     1 |                1 |                0 |
| typed int (legal) + typed int 0-100 (split-axis)             |     1 |                1 |                0 |
| binary (legal) + typed int 0-100 (split-axis)                |     1 |                0 |                1 |
| Other typed singletons (10 distinct cell types)              |    13 |                0 |               13 |
| **TOTAL**                                                    | **183** |          **22** |          **161** |

**Composition of the 22 already-additive rows:**

- **5 cell-type-vocabulary fixes from Phase B Ralph (the templates we want to scale):**
  - `lobbyist_registration_renewal_cadence` — IntCell
  - `lobbyist_registration_threshold_compensation_dollars` — DecimalCell-Optional
  - `lobbyist_registration_threshold_expenditure_dollars` — DecimalCell-Optional (recently)
  - `lobbyist_spending_report_filing_cadence` — EnumCell (split-axis)
  - `lobbying_violation_penalties_defined_in_law` — BinaryCell
- **~14 axis-clarification caveats** from wi-tier1 wide-pass population ("Asks whether the LOBBYIST is the named filer..."). These are a different additive class — principal-vs-lobbyist disambiguation, not cell-type vocabulary. They don't conflict with cell-type-vocabulary additives; both can coexist on a row.
- **~3 standalone-rewrites** where the wide-pass populator wrote a fresh question.

---

## Why no diagnostic dispatch (original A0, dropped)

The additive pattern is **purely additive** — iter 4 ablation confirmed it doesn't degrade rows that were already working. So whether the 135 raw-binary rows currently pass or fail BinaryCell coercion, **the action is the same in both branches: apply the template**. A diagnostic dispatch's information value is near zero relative to its cost.

Defensive context: we're about to expand to 13+ states × 2 vintages. Even if WI's wide-pass currently clears raw-binary rows on the small sample the sweep tested, state-specific statute quirks elsewhere could elicit "Yes" vs "true" inconsistently. Preemptive immunization beats post-hoc diagnosis.

The original failure-mode reminder, for the cold reader: BinaryCell coercion accepts only `'true'`/`'false'`, not `'yes'`/`'no'`. The `_defined_in_law` session showed a natural-English prompt → model emits `'yes'` → 6/6 ValueError on coercion. Most of the 135 raw-binary rows have natural-English prompts (e.g., "Are lobbyists required to disclose contacts?") — same shape as `_defined_in_law` was.

---

## Stages

### Stage A1 — Bulk YAML edits (~30 min, $0)

| Cell type                          | Template                                                                                                                                              | Action                                                         | Rows |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---: |
| BinaryCell                         | Append: `Answer with the boolean value true or false.`                                                                                                | **Mechanical bulk script** (`/tmp/apply_phase_a_binary.py`)    |  135 |
| DecimalCell-Optional               | Append: `Answer as a non-negative decimal (e.g., 500 for $500). Use 0 if [row-specific zero case]. Use null if [row-specific null case].`              | **Hand-crafted per row** (~10 min)                             |    3 |
| EnumCell / Set[enum] / Optional[enum] | Append: `Answer with one of: a, b, c, ..., or null. [row-specific absence-case guidance]`                                                          | **Hand-crafted per row with `enum_domains.py` lookup** (~20 min) |    6 |
| Long-tail typed singletons         | Per-cell-type template not yet designed                                                                                                                | **DEFER to Phase B follow-up** (handoff at end of session)     |  ~13 |
| Practical-axis-only typed-int (3)  | n/a                                                                                                                                                    | **SKIP** — dispatcher does not extract                          |    0 |

**Pure additive: no destructive edits.** Append the cell-type-aligned vocabulary instruction to the existing `prompt:` field. Preserve source quote as front matter (provenance). Same pattern as iters 1-5.

**Edit ordering:** hand-crafted typed cells first (~30 min, ~9 rows), then bulk-script binary (~5 min, 135 rows). Bulk-script approach minimizes risk of accidentally clobbering an existing additive — script reads existing prompt, skips if "true or false" substring present, appends if absent.

**Total rows touched: ~144 in YAML.** Full pytest suite must stay green after edits (no structural changes; should be no-op for tests, but verify).

### Stage A2 — Verification dispatch (A2.b: one chunk per touched cell type, ~$0.50-$1.20)

Picked: **A2.b — verify on WI before multi-state expansion runs blind.** Catching a template bug on one WI chunk is cheaper than catching it after dispatching across N states × M vintages.

Per cell type, dispatch ONE representative chunk. Suggested picks (implementing agent confirms at execution):

| Cell type touched      | Representative chunk                            | Why                                                                                    | Approx cost |
| ---------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------- | ----------: |
| BinaryCell             | `actor_registration_required` (11 PRI rows)     | Pure-binary, all raw → all touched. Confirms the most common cell type in one dispatch | ~$0.40      |
| DecimalCell-Optional   | `registration_thresholds` (6 rows; iter-5 home) | 3 raw DecimalCell-Optional rows live here; before-state JSONs already archived         | ~$0.30      |
| EnumCell               | TBD at execution — pick chunk with touched enum row | Need to identify which chunk(s) host the 6 enum rows                                | ~$0.30-0.50 |
| **TOTAL**              |                                                 |                                                                                        | **~$1.00-1.20** |

**For each chunk:** archive existing JSONs to `_pre_phase_a_<chunk>/` with SUPERSEDED.md banner (per "prefer mv over rm for research artifacts" memory). Dispatch fresh. Audit:

1. **Instantiation:** zero `errors[]` entries (no BinaryCell coercion failures).
2. **Per-row stability:** for each touched row, value at high confidence; same value across at least 2 of 3 runs per model.
3. **Chunk-mate spillover:** non-touched rows in the chunk — values stable or substantively shifted? Iter 5 surfaced 3 positive spillover shifts; this round may surface more. Document per-chunk.

**Pass criteria:** all 3 chunks dispatch with 0 errors and converge on cell-type-coherent values. If any chunk errors or surfaces a regression, **pause and surface to Dan** before continuing.

### Stage A3 — Documentation + commit (no API)

- Update RESEARCH_LOG.md (this branch), STATUS.md (this branch's row only — multi-committer norm), write convo summary at `convos/20260605_phase_a_execution.md`
- If long-tail typed singletons remain unaddressed: write next-session handoff sentence flagging them as Phase B candidates with per-cell-type design effort estimate
- v2.1 propagation to main: flag for Dan post-verification (Decision 3 below — still deferred)
- Walk doc link graph (per persistent-memory feedback memo): convos back-reference plan, plan back-references convo, RESEARCH_LOG indexes both, STATUS.md branch row updated
- Commit + push

- Update RESEARCH_LOG.md, STATUS.md (branch's row only — multi-committer repo norm), write convo summary
- Surface follow-up Phase B candidates (long-tail typed singletons; any A2 spillover anomalies)
- Walk the doc link graph (per the persistent-memory feedback memo) before commit — convos/plans/results all back-reference

---

## Cost projection (revised, post-A0-drop)

| Stage | Cost | Cumulative wi-ralph |
|---|---:|---:|
| Stage A1 (YAML edits) | $0 | $2.6837 |
| Stage A2 (verification, A2.b on ~3 chunks) | ~$1.00-1.20 | $3.68-3.88 |
| **Total this session** | **~$1.20 (max)** | **~$3.88 (worst case)** |

Ceiling fit: comfortably under $5 ($1.12 headroom at worst case). Better budget posture than A2.a / A2.d would have provided. A0 drop frees ~$0.40 of headroom.

---

## Done criteria (for "Phase A is complete on this branch")

A Phase A landing checks all of:

1. **Zero remaining rubric-vocab-vs-cell-type mismatches** on rows whose cell_type matches one of the 4 confirmed templates AND that aren't practical-axis-only (and not in the long-tail-singleton defer list).
2. **Long-tail singleton cell types** explicitly flagged in a follow-up handoff as Phase B candidates (template design, not "audit at scale").
3. **Chunk-mate spillover characterized per touched cell type** — for each chunk dispatched in A2, a before/after per-row comparison surfaces whether spillover dragged neighboring rows substantively.
4. **A clean re-dispatch (no `instantiation_failed` errors)** on each verified chunk.
5. **v2.1 propagation decision flagged for Dan** — branch-local right now; merge to main is a downstream separate decision (Decision 3 below).
6. **Doc graph self-consistent** at commit — convo back-references plan, plan back-references convo, RESEARCH_LOG indexes both, STATUS.md branch row updated.

If A2.c is picked, criterion (3) and (4) are deferred to the follow-up verification branch — landing this branch ships "structural YAML edits, verification queued."

---

## Decisions

### Decision 1 — Verification strategy: **A2.b (RESOLVED 2026-06-05)**

Dan's call: "after you make the edits, then we'll test." A2.b — one chunk per touched cell type, ~$1.00-1.20.

### Decision 2 — A2.b chunk picks: implementing-agent picks at execution

BinaryCell: `actor_registration_required` (11 PRI rows). DecimalCell-Optional: `registration_thresholds`. EnumCell: TBD at execution (need to identify chunk(s) hosting the 6 enum rows).

### Decision 3 — v2.1 propagation to main: **DEFERRED (still open)**

v2.1 (183-row TSV) is currently branch-local. Phase A's YAML edits land on this branch's v2.1 only. Decision to propagate to main waits until post-A2 verification confirms templates work. Surface to Dan after A2 lands.

---

## Out of scope (explicitly)

- **Cross-state expansion design.** Downstream of Phase A. Per Dan: batch-dispatch-per-loop. Plan flags this for the next-session handoff but does not design it here.
- **Long-tail singleton cell-type templates** (count_with_FTE, TimeSpent, SectorClassification, TimeThreshold, UpdateCadence, Optional[int], typed Set[enum] (8/9 types), free-text). Each needs Phase-B-style hand iteration to design the right vocabulary template. ~10-13 rows worth, ~$0.30-0.50 per cell-type design iteration.
- **`_audit_required_in_law` value-stability test** with additive EnumCell template (Claude run3 drift to YES from last session's results — flagged in §Open of `convos/20260605_pattern_c_v2_1_execution.md`). Not Phase A — it's row-level Ralph follow-up.
- **CPI 2015 WI-row errata documentation** (IND_197 + IND_207 candidates). Low priority cleanup; lives in projection-mapping-doc footnote update.
- **Production code changes** (dispatcher, registry, projections). Phase A is YAML-only. If A0 surfaces a code-side surprise (e.g., dispatcher behavior we hadn't characterized), surface to Dan, don't autonomously change code.

---

## Pre-execution checklist (implementing agent, post-Dan-sign-off)

**This is a fresh-session-TDD task.** This plan was written one session, executed the next.

1. Re-read this plan end-to-end.
2. Re-read [`convos/20260605_pattern_c_v2_1_execution.md`](../convos/20260605_pattern_c_v2_1_execution.md) (immediate predecessor — TDD discipline, plan-then-execute pattern, "Dan caught me about to edit code before updating the plan" lesson).
3. Re-read [`convos/20260605_phase_a_kickoff.md`](../convos/20260605_phase_a_kickoff.md) (this plan's originating convo — captures Dan's A0-drop reasoning).
4. Re-read `compendium/source_quotes.yaml` end-to-end — YAML may have shifted between plan-write and plan-execute (multi-committer repo).
5. **Re-run the characterization scripts:**
   - `/tmp/phase_a_characterize.py` (per-cell-type additive vs raw counts; preserved as session artifact)
   - `/tmp/phase_a_list_targets.py` (lists exact target row IDs + their current prompts, by cell type bucket)
   - If `/tmp/` lost the files, regenerate from this plan's logic. (Numbers in this plan: 135 raw binary, 3 raw decimal-optional, 9 raw enum-family, 11 long-tail typed singletons defer, 3 practical-axis-only skip.)
6. **Look up enum domains per row.** Plan didn't pin the per-row enum vocabularies (planning-session investigation got interrupted at this step). Two options:
   - Find an `enum_domains.py` or equivalent registry in `src/lobby_analysis/models_v2/`
   - If no such registry, infer from the source quote + projection mapping doc per row
   - For `lobbying_disclosure_audit_required_in_law` specifically: enum is YES/MODERATE/NO (the CPI tier vocab is the actual enum domain). This row also has a value-stability flag from predecessor session (Claude run3 → YES). Apply additive EnumCell template AND note the additive may resolve the value-stability question incidentally.
7. **Begin TDD per `skills/test-driven-development/SKILL.md`:**
   - RED batch: write tests asserting Phase A template substrings present in YAML for each target cell type's rows. Run pytest, verify failures land for the right reasons.
   - GREEN batch: apply YAML edits (hand-craft typed cells first, then bulk-script binary). Verify pytest green.
   - Run full pytest suite (not just targeted). The predecessor session's 7th-touchpoint discovery (`test_load_v2_compendium_returns_181_rows`) was caught by full-suite; same risk here for any test that asserts something about YAML prompt content.
8. Confirm with Dan: A0 chunk picks (BinaryCell candidate: `actor_registration_required`, 11 rows, ~$0.40), then dispatch A2.b sequentially.
9. After A2 lands: audit per-row before/after on each chunk + chunk-mate spillover; finish-convo; surface v2.1-to-main propagation question (Decision 3) to Dan.

---

## Linked artifacts

- v2.1 compendium: [`compendium/disclosure_side_compendium_items_v2.1.tsv`](../../../../compendium/disclosure_side_compendium_items_v2.1.tsv)
- YAML SSOT: [`compendium/source_quotes.yaml`](../../../../compendium/source_quotes.yaml)
- Naming conventions: [`compendium/NAMING_CONVENTIONS.md`](../../../../compendium/NAMING_CONVENTIONS.md) §9 (suffix → cell_type hints)
- Predecessor Pattern C session: [`convos/20260605_pattern_c_v2_1_execution.md`](../convos/20260605_pattern_c_v2_1_execution.md)
- This plan's originating convo: [`convos/20260605_phase_a_kickoff.md`](../convos/20260605_phase_a_kickoff.md)
- Sweep results doc: [`results/20260604_silent_unit_mismatch_sweep.md`](../results/20260604_silent_unit_mismatch_sweep.md) (16/17 CPI-readable rows cleared)
- Characterization scripts (session artifacts, preserved):
  - `/tmp/phase_a_characterize.py` (per-cell-type additive vs raw counts)
  - `/tmp/phase_a_list_targets.py` (exact target row IDs + current prompts, by cell type)
- Chunks manifest: `src/lobby_analysis/chunks_v2/manifest.py` (15 chunks total)
- Cells / enum domain definitions: `src/lobby_analysis/models_v2/cells.py` (UpdateCadenceLiteral, IncomeSourceTypeLiteral, etc.); per-row enum domain registry may be elsewhere — implementing agent to locate

---

## Open questions surfaced by plan-writing (for Dan to consider, not blocking)

- **The 6-vs-15 chunk-count discrepancy** — earlier convos reference "full-6-chunk re-dispatch ~$2.50"; current manifest has 15 chunks. Either the dispatcher Tier-1-selects 6 of 15 by default, or the earlier number was wrong. Implementing agent should verify cost projection from a clean dispatch test, not assume the projection.
- **The 14 axis-clarification ("Asks whether the LOBBYIST is the named filer") caveats** — should Phase A check whether these are still correct on rows whose cell type also wants a cell-type-vocabulary additive? Combining additives might be redundant or contradict. Worth a quick review of those ~14 rows during A1 if A0 returns hypothesis-A.

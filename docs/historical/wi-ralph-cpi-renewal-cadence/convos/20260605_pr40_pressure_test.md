# 2026-06-05 (PR 40 review) — Pressure-test of v2.1 + Phase A inheritance story; plan amendment lands

**Plan amended:** [`../plans/20260605_cross_state_cpi_2015_validation.md`](../plans/20260605_cross_state_cpi_2015_validation.md) (§Amendment 2026-06-05 banner + D1/D3/D4 marked SUPERSEDED inline + D7/D8/D9 added + downstream sections updated)
**Predecessor:** [`20260605_cross_state_planning.md`](20260605_cross_state_planning.md) (original plan write — 10 states × 3 chunks × "CPI projection accuracy per state" continuous tolerance)
**PR under review:** [#40 — `wi-ralph-cpi-renewal-cadence` → `main`](https://github.com/danparshall/lobby_analysis/pull/40)
**Session shape:** Discussion + plan-amendment commit. No API spend, no code edits, no test changes — only the plan document. Convo + RESEARCH_LOG entry + plan amendment commit together as one logical PR-prep change.

---

## Why this session existed

Dan opened with *"Hi Claude, let's discuss PR 40"*. PR 40 bundles three streams (`wi-tier1-direct-read` absorbed via earlier merge + v2.1 schema bump + Phase A YAML audit at scale) and is the propagation-to-main blocker for Phase A done-criterion 6. The session moved from PR overview → "pressure-test the v2.1 + Phase A inheritance story" → de-jure success-metric refinement → state-list amendment → plan amendment commit.

## What got pressure-tested

The inheritance story is: PR 40 lands v2.1 TSV + 163 Phase A YAML additives + dispatcher `_RESOLVED_CHUNKS` extension + the projection-helper updates for v2.1's Pattern C row split on main. A successor branch cut off main inherits all of this for the cross-state CPI 2015 validation execution. Question: does the inheritance hold up structurally, or are there gaps that will bite the next agent?

## Findings

### 1. Inheritance story is structurally clean (mostly)

- `DEFAULT_COMPENDIUM_V2_TSV` in `src/lobby_analysis/compendium_loader.py:32` points at v2.1 — the successor branch inherits v2.1 as the default by construction.
- All 4 Pattern C split row IDs present in v2.1 TSV (rows 49/50/73/74: `_audit_required_in_law`, `_audit_required_in_practice`, `_penalties_defined_in_law`, `_penalties_imposed_in_practice`) and in `source_quotes.yaml` with Phase A vocabulary additives applied where appropriate (cell-type-aligned).
- `enforcement_and_audits` ChunkDef in `chunks_v2/manifest.py:243-249` lists all 4 new split rows — `--chunks enforcement_and_audits` (or default dispatch) will actually dispatch them.
- Projection helpers in `projections/cpi_2015_c11.py` key by row ID, not row index — v2.1's row-count shift (181 → 183) doesn't break the projection.
- Dispatcher is state/vintage-agnostic: `--state`/`--vintage` parsed args; `resolve_bundle_dir`/`resolve_results_dir` are pure path-builders. Phase A test suite (167 tests) is state-agnostic too — reads YAML invariants only.

### 2. Stale prose in 5 places — not breaking, but misleading for a new-to-the-branch agent

Not in the PR body's "what changed/didn't" list, not in the 4 nori-code-reviewer findings:

- `src/lobby_analysis/chunks_v2/__init__.py:3` — "186-cell" (correct count, but ambient context says v2)
- `src/lobby_analysis/chunks_v2/chunks.py:98` — comment says "v2 TSV"
- `src/lobby_analysis/chunks_v2/docs.md:14,36` — "181 v2 TSV rows = 186 cells" and "5 combined-axis rows" (should be 183 rows + 3 combined-axis post-Pattern-C)
- `src/lobby_analysis/chunks_v2/manifest.py:4` — "Verified ... against `disclosure_side_compendium_items_v2.tsv`"
- `scripts/silent_unit_mismatch_sweep.py:29` — hardcodes `v2.tsv`; not under `_completed/`, so still live. Phase B diagnostic sweep; if a cross-state agent reaches for it to debug an outlier state, they'll be on frozen v2.

Surfaced to Dan; not blocked on for the PR merge but worth tracking as cleanup.

### 3. The structural-bug concern I raised was a category error

I read the dispatcher (legal-axis only per system prompt: *"never what the state does in practice"*) and the CPI 2015 projection helpers (8 of 14 read `_practical()`) and concluded the cross-state plan was structurally broken — projected scores capped at ~46.7, every state above-median failing tolerance for non-extraction reasons. **Dan corrected:** *"Practical is something we learn via research agents, not by parsing statutes."* Tier-1 legal-axis-only is *supposed* to be legal-axis-only; practical-axis cells come from a separate research-agent pipeline that the cross-state validation isn't running this round. So the projection function's `_practical()` calls returning None is expected, not a bug — the *validation* needs to slice to de-jure only.

This was a discourse-register Exchange 3 — partial concession on the structural-bug claim (wrong), holding ground on the empirical/structural conflation + stale prose findings (still valid), with a refined observation that the cross-state plan's X2 was under-specified on how the projection-function call actually runs end-to-end given practical axis is out-of-scope this round.

### 4. The de-jure framing surfaced a clean 1:1 chunk↔indicator structure

Dan: *"comparison on dejure only... part of why we're doing CPI is because it (uniquely!) records state-by-row data, so we CAN just check that."* CPI 2015 publishes per-(state, indicator) ground truth in a 700-cell CSV — so the comparison is per-cell exact-match on the 3-tier {0, 50, 100} de-jure scale, not category-aggregate within ±10 points.

Following that thread, I mapped the 6 de-jure CPI indicators to chunks and found a clean **1:1 correspondence**:

| Default chunk | De-jure CPI indicator |
|---|---|
| `lobbying_definitions` | IND_196 |
| `registration_thresholds` | IND_197 |
| `registration_mechanics_and_exemptions` | IND_199 |
| `lobbyist_spending_report` | IND_201 |
| `principal_spending_report` | IND_203 |
| `enforcement_and_audits` | IND_207 |

Almost certainly by design — the chunk decomposition was informed by the CPI indicator structure when originally cut. Diagnostic payoff: each chunk's extraction-quality lands a single de-jure indicator's match rate. No further triangulation needed when a (state, indicator) mismatches.

### 5. Tension surfaced: full de-jure coverage overruns the $10 envelope at 10 states

Phase A's 21-cell 3-chunk dispatch was $0.83/state. Default 6-chunk dispatch is ~90 rows (`lobbying_definitions` 15 + `registration_thresholds` 6 + `registration_mechanics_and_exemptions` 8 + `lobbyist_spending_report` 34 + `principal_spending_report` 23 + `enforcement_and_audits` 4). Cost extrapolation: ~$1.6/state × 10 states = ~$16, busts the $10 envelope by ~$6.

Trade-off Dan considered: stay narrow on chunk set (preserves 10-state breadth, but de-jure coverage is only 2-of-6 or 3-of-6) vs cut states (full 6-of-6 de-jure coverage, but breadth shrinks).

## Decisions Dan locked this session

Via direct message (no AskUserQuestion round — Dan's response *"drop --chunks, cut states to 5: NY WI OH CA TX"* was unambiguous):

- **State list amendment (D7).** 10 → 5. **NY, WI, OH, CA, TX** in dispatch order. Drops CO, IL, WA, FL, NC — deferred to a follow-up round, not retired. NY is the cost-calibration anchor (first dispatch, pause-and-surface threshold at NY > $2.50); WI is the Phase A known-good baseline.
- **Chunk set amendment (D8).** Phase A 3-chunk validation subset → default 6 chunks (drop `--chunks` flag entirely). Covers all 6 de-jure CPI 2015 C11 indicators 1:1. Drops `actor_registration_required` from this round — Phase A's WI BinaryCell verification (11/11 stable) is taken as sufficient template-at-scale evidence for now; cross-state BinaryCell template test deferred to a follow-up.
- **Success metric amendment (D9).** "CPI 2015 C11 projection accuracy per state" (continuous tolerance, ±10 points) → **per-(state, indicator) exact-match on the 6 de-jure CPI 2015 C11 indicators**, 3-tier {0, 50, 100} categorical comparison, 30 comparison cells total (5 states × 6 indicators).

D1, D3, D4 left in the plan with SUPERSEDED markers + cross-reference to D7/D8/D9 (preserves trajectory per the doc-as-persistent-memory feedback memo).

## Findings (load-bearing)

### 1. The plan-amendment-as-in-place-supersession pattern preserved trajectory cleanly

The original D1/D3/D4 are kept inline with `~~strikethrough~~` + SUPERSEDED-by-Dx markers + a one-sentence "what changed" note. New D7/D8/D9 follow. The §Amendment 2026-06-05 banner at top summarizes the delta. An agent reading the plan post-merge sees both the prior framing and the current one without having to git-archeology the convo.

This matches the doc-as-persistent-memory feedback memo: trajectory stays visible, the doc is internally coherent as the operational brief, and ship-then-patch-each-gap is avoided.

### 2. The 1:1 chunk↔indicator structure is the diagnostic payoff that makes this validation tractable

If a state mismatches on IND_201, the failing chunk is `lobbyist_spending_report` — period. No need to disambiguate which chunk's prompts to scrutinize. This is the structural property that justifies the budget trade-off: each chunk's extraction-quality maps to exactly one diagnostic signal.

### 3. Dispatch-order-as-cost-anchor is a small but real prudence

NY-first is not just arbitrary ordering — NY's statute corpus may differ substantially in volume from WI's (Phase A baseline), and 6 chunks is 2× the chunks Phase A dispatched. A $2.50 NY threshold before continuing to OH/CA/TX gives a fail-fast on the envelope without committing $8 up front.

### 4. The PR 40 inheritance story ships clean

No PR-blocker findings. The 5 stale-prose items are tracked as cleanup, not gates. The deferred BinaryCell prompt-grammar (reviewer finding #2) remains the only known deferral and is bounded by the cross-state instantiation-error pause threshold.

## What didn't happen (explicitly out of scope this session)

- **PR 40 merge.** This session was plan-amendment + commit-to-PR-40 only. The merge itself is a separate Dan decision after the plan amendment lands and any other review surfaces.
- **Convo for the original cross-state planning session.** Already exists (`20260605_cross_state_planning.md`), referenced as predecessor.
- **Code edits or test changes.** The 5 stale-prose items are docs/comments only; no functional impact. Tracked for cleanup but not blocked-on.

## Cost ledger

This session: **$0**. No API spend.
wi-ralph cumulative: **$3.5127** (unchanged).
Cross-state envelope: **$0 of $10** (unchanged; allocated to successor branch).
Grand total: **$10.8073** (unchanged).

## Next-session shape

- If Dan wants to merge PR 40: standard merge → `wi-ralph-cpi-renewal-cadence` moves to `docs/historical/` per the active → historical lifecycle (per skill `finishing-a-research-branch`).
- Then: successor branch (`cross-state-cpi-2015-validation` or similar) cut off main; reads the amended plan (now at `docs/historical/wi-ralph-cpi-renewal-cadence/plans/...`); fresh-session TDD execution per the §Pre-execution checklist.
- No remaining pre-dispatch blocking open questions — the original Open Q #1 (chunk-set swap) and #2 (tolerance) were resolved by this session's amendment.

---

## Appendix 2026-06-05 (later) — `finishing-a-research-branch` skill walk-through

Same-day continuation: Dan asked to run the finish-branch skill before merging PR 40. Skill steps executed in order; no substantive findings, just the archive + merge mechanics.

### Pre-flight (Step 1)

- `git fetch origin` clean.
- Local `main` 35 commits behind `origin/main` — left untouched (other worktrees / fellows have unstaged work in main; will pull main only after the merge step, in the worktree we land on).
- Branch handling: switched into existing worktree `.worktrees/wi-ralph-cpi-renewal-cadence/` (clean; up to date with `origin/wi-ralph-cpi-renewal-cadence` at `6914704`).
- `docs/active/wi-ralph-cpi-renewal-cadence/` present with `RESEARCH_LOG.md` + `convos/` + `plans/` + `results/` — branch is tracked as a research line and is eligible to archive.

### Test suite (Step 2)

- `uv run pytest -q` (via `--project` to point at the worktree): **1890 passed / 3 skipped / 3 xfailed in 46.76 s**. Baseline holds — no test regression introduced by the PR 40 pressure-test commit.

### finish-convo (Step 3)

- This appendix + RESEARCH_LOG entry + STATUS.md one-liner together checkpoint the finish-branch session.

### audit-docs (Step 4)

- Pending — runs next. Any flagged structural issues fix before archive.

### maintaining-decision-docs (Step 5)

- `docs/DOCS_INDEX.md` does not exist in this repo — skill skips silently.

### Archive + PR (Steps 6-10)

- `git mv docs/active/wi-ralph-cpi-renewal-cadence docs/historical/wi-ralph-cpi-renewal-cadence` after this convo + audit fixes land.
- STATUS.md: move the wi-ralph row from Active Research Lines to Archived Research Lines table with archived-date `2026-06-05` and material pointer `docs/historical/wi-ralph-cpi-renewal-cadence/`.
- Commit the archive; push the branch.
- PR 40 already open at https://github.com/danparshall/lobby_analysis/pull/40 with `mergeable: MERGEABLE`. Confirm description matches finished-branch template (Summary + Key Findings + Documentation links) — edit if needed.

### Merge gate (Steps 11-13)

- `gh pr checks` polled in foreground for CI green-light.
- User asked explicitly before merge (research-branch merge becomes permanent main history).

### What this appendix is NOT

- Not a substantive research finding. Findings of this branch are already captured in the 10 prior convos + the RESEARCH_LOG body. This appendix exists only to make the finish-branch mechanical work visible inside the link graph (per the `doc-system-is-persistent-memory-not-patchwork` feedback memo: end-of-session commits should land graph self-consistent).

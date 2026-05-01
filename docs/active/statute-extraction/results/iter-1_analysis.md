# OH Iteration 1 — Analysis (`definitions` chunk)

**Iteration:** iter-1 (prior: none — first iteration baseline)
**Date:** 2026-05-01
**Chunk:** `definitions` (7 compendium rows)
**Bundle:** OH 2025 (30 sections, ~36K tokens, retrieved 2026-04-30 from Justia)
**Compendium:** 141 rows; the 7 `definitions`-domain rows (locked at PR #5 merge)

**Provenance (3 temp-0 runs, claude-opus-4-7):**

| run_id | timestamp | bundle_manifest_sha (prefix) | compendium_csv_sha (prefix) | prompt_sha (prefix) | tokens |
|---|---|---|---|---|---|
| `cc24d8920949` (r1) | 2026-05-01T19:06:59+00:00 | shared | shared | scorer_prompt_v2 pre-Rule-1-tightening | 105K |
| `dea6828ac0bc` (r2) | 2026-05-01T19:13:25+00:00 | shared | shared | scorer_prompt_v2 post-Rule-1-tightening | 104K |
| `4ad20debaf31` (r3) | 2026-05-01T19:13:25+00:00 | shared | shared | scorer_prompt_v2 post-Rule-1-tightening | 104K |

The bundle manifest sha and compendium sha are identical across all three runs (verified by orchestrator's drift guard). The prompt sha differs between r1 and r2/r3 because the v2 prompt's Rule 1 was tightened mid-iteration to make the `not_addressed` exception explicit (see "What changed vs prior" below). The behavioral effect of that prompt change should be zero — r1's not_addressed records already had the right structural shape (null citation, search trail in evidence_notes); only the validation guard was wrong, and was fixed at finalize-layer too.

**What changed vs prior:** First iteration baseline. No prior. One mid-run scaffolding change: after r1 surfaced a prompt/validation tension on `not_addressed` rows (validation required `legal_citation` for every record; v2 Rule 3 says set null + put search trail in evidence_notes), the v2 prompt's Rule 1 was updated to make the `not_addressed` exception explicit, and the finalize check was loosened to permit null citation when status is `not_addressed` and evidence_notes is non-empty (commit `0ac7800`). All three runs' substantive output is comparable; r1 was re-finalized under the new rules.

---

## Per-row results

3 runs × 15 emitted tuples = 45 records. The 15 emitted tuples are identical across runs (regime-expansion decisions are unanimous). Status agreement is **14/15 = 93.3%**. The single disagreement is on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system` (see weak rows).

| compendium_row_id | regime | r1.status | r2.status | r3.status | run-agree | flag |
|---|---|---|---|---|---|---|
| `THRESHOLD_LOBBYING_MATERIALITY_GATE` | legislative | required_conditional | required_conditional | required_conditional | ✓ | quote-length variance |
| `THRESHOLD_LOBBYING_MATERIALITY_GATE` | executive | required_conditional | required_conditional | required_conditional | ✓ | — |
| `THRESHOLD_LOBBYING_MATERIALITY_GATE` | retirement_system | required_conditional | required_conditional | required_conditional | ✓ | — |
| `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` | legislative | not_required | not_required | not_required | ✓ | — |
| `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` | executive | required | required | required | ✓ | citation-subsection variance |
| `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` | retirement_system | not_required | not_addressed | required | **✗** | **interpretive disagreement** |
| `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` | legislative | not_required | not_required | not_required | ✓ | — |
| `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` | executive | not_required | not_required | not_required | ✓ | — |
| `DEF_ELECTED_OFFICIAL_AS_LOBBYIST` | retirement_system | not_required | not_required | not_required | ✓ | — |
| `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` | legislative | required | required | required | ✓ | — |
| `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` | executive | not_required | not_required | not_required | ✓ | — |
| `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` | retirement_system | not_required | not_required | not_required | ✓ | — |
| `DEF_COMPENSATION_STANDARD` | (uniform) | not_addressed | not_addressed | not_addressed | ✓ | — |
| `DEF_EXPENDITURE_STANDARD` | (uniform) | not_addressed | not_addressed | not_addressed | ✓ | — |
| `DEF_TIME_STANDARD` | (uniform) | not_addressed | not_addressed | not_addressed | ✓ | — |

**Multi-rubric agreement:** deferred to the validation-tool plan. Iter-1 has no automated rubric-projection; manual annotation against PRI 2010 / Newmark 2017 / CPI 2007 historical OH scoring is feasible but not yet done — those rubrics scored at coarser granularity than the per-regime breakdown produced here, and the projection mapping is a Phase 5 concern.

### Headline observations

1. **Regime expansion was unanimous and correct.** All 3 runs identified OH's three lobbying regimes (`legislative` / `executive` / `retirement_system`) and emitted the same per-regime tuple set. Four compendium rows split per-regime; three (the quantitative-threshold standards) emitted as regime-uniform. No run produced a "general" or other catch-all regime string. **The regime-aware-from-day-one Q4 decision is validated** — the harness uses the regime axis without prompting.

2. **The canary case (qualitative materiality gate) worked.** All 3 runs caught §101.70(F)'s "main purposes" gate as `required_conditional` across all 3 regimes, populating `condition_text` with verbatim qualifying clauses. r1 and r2 produced byte-identical condition_text per regime; r3 produced a shorter quote substring for legislative ("as one of the individual's main purposes" vs. r1/r2's "engaged during at least a portion of the individual's time to actively advocate as one of the individual's main purposes") — same statutory clause, different excerpt length. Status, regime, citation all match. The longer r1/r2 quote is more diagnostic, but r3's shorter quote is also structurally correct. **Quote-length is not a flag at iter-1; revisit if it persists at iter-2.**

3. **`DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST × legislative = required` is the substantively interesting unanimous finding.** All 3 runs cite `ORC §101.72(E)` — the public-employee disclosure clause inside the legislative-regime registration chapter. This means the harness correctly detected that OH's legislative regime affirmatively *includes* public employees in the lobbyist universe (via §101.72(E)'s registration requirement) — a substantive finding that prior PRI projection would not have surfaced because PRI 2010's A-series doesn't ask the question at this granularity.

4. **No quantitative inclusion thresholds in OH.** All 3 runs unanimously rule `DEF_COMPENSATION_STANDARD` / `DEF_EXPENDITURE_STANDARD` / `DEF_TIME_STANDARD` as `not_addressed`, with detailed search-trail evidence_notes ("Searched §§101.70, 101.90, 121.60 ... no $-per-period gate"). This **confirms the prior PRI-projection finding** that OH 2025 ≈ OH 2010 structurally, viewed through the inclusion-threshold lens. **Important downstream signal:** the *qualitative* materiality gate is captured at `THRESHOLD_LOBBYING_MATERIALITY_GATE`, so the not_addressed verdict on the three quantitative-standard rows is a substantive descriptive fact, not a harness blind spot.

5. **No leakage of legacy v1 status values** (`optional` / `not_applicable` / `unknown`). Every record uses one of the four v2 values. Validation enum extension worked as designed.

---

## Weak rows (flagged for review)

### `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system`

**Harness output:**

| run | status | citation | gist of evidence_notes |
|---|---|---|---|
| r1 | `not_required` | `ORC §101.90(H), (I)` | "Retirement-system regime trigger is influence on retirement-system investment decisions, not administrative-agency lobbying generally." |
| r2 | `not_addressed` | (null) | "searched §§101.90–101.98; retirement-system regime triggers on retirement-system decisions ... not at administrative/executive agencies generally." |
| r3 | `required` | `ORC §101.90(H)` | "Retirement systems are state administrative agencies; contacts with retirement-system boards/officials trigger registration in this regime." |

**Statute says** (§101.90(H)): `'Retirement system lobbyist' means any person engaged to influence retirement system decisions or to conduct retirement system lobbying activity as one of the person's main purposes on a regular and substantial basis.`

**Likely cause:** Genuinely interpretive ambiguity at the **definitional cross-application** boundary. The compendium row asks "does administrative-agency lobbying trigger registration (definitionally)?" The retirement-system regime in OH's statute is a *parallel* regime with its own definitions — not an instantiation of "administrative-agency lobbying" generally. Three coherent legal readings:

- r1 reads the row literally — admin-agency lobbying as a *category* — and rules `not_required` because the retirement-system regime is a separate definitional axis.
- r2 reads the row as inapplicable to the retirement-system regime — `not_addressed` (the statute neither affirms nor denies this; it just defines a parallel regime).
- r3 reads "retirement system" as a *species* of "state administrative agency" and rules `required` on functional grounds.

This is **inter-rater disagreement on a definitional question**, not a scaffolding bug. The brief gives no guidance on cross-regime row applicability — which is the prompt-side weakness.

**Proposed change for iter-2:** Add a per-domain extraction note to `definitions` clarifying how to handle compendium rows that cross-cut regimes. Specifically: when a compendium row asks about a category (e.g., "administrative-agency lobbying") and the state has a parallel regime that *partially* maps (e.g., retirement-system is one species of admin agency), the harness should emit `not_addressed` with `evidence_notes` enumerating the parallel-regime mapping. This converts a 3-way disagreement into a 1-way `not_addressed` consensus. Alternative: tighten the compendium row's `description` field to disambiguate scope (this would be a compendium-curation change, not a prompt change).

### Quote-length variance on `THRESHOLD_LOBBYING_MATERIALITY_GATE × legislative`

Not flagged as a weak row (status agreement is unanimous), but tracking for cross-iteration trend: r1 and r2 emit a 22-word `condition_text`; r3 emits a 7-word truncation that is also a verbatim substring of the statute. Both are valid per Rule 1's ≤30-word constraint. If iter-2 reveals the model preferring shorter quotes systematically, the prompt should specify a *minimum* quote length for materiality gates so the qualifying clause is fully captured (downstream code that pattern-matches the condition will benefit from the longer form).

### Citation-subsection variance on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × executive`

Not flagged (status agreement is unanimous). r1 cites §121.60(H), (I); r2 cites §121.60(I); r3 cites §121.60(H). All point at the same chapter-section. Minor noise.

---

## Decisions that this iteration validates

These can move from "open question" to "settled" given iter-1's evidence:

- **Bundle inlining works.** No retrieval/Read variance was observed. All 3 runs ingested the full 30-section bundle as required. The prior architecture's 4–43 tool-call dispatch variance is structurally eliminated.
- **Atomic per-row holds.** No conjunctive→disjunctive collapse observed. The 7 distinct definitions rows produced 15 distinct records without merging.
- **Regime-aware-from-day-one (Q4) was correct.** The 3-regime split is consistent across runs and substantively meaningful (e.g., the public-employee distinction). Building flat-and-refactoring would have lost this.
- **3 temp-0 runs is sufficient at iter-1.** 14/15 = 93.3% inter-run status agreement; the one disagreement is interpretive, not noise. Bumping to 5 runs would not resolve interpretive disagreement; the 3-model consensus oracle (or compendium-row scope tightening) is the right escalation path. **Q6 settles to 3 runs minimum** for the harness; escalate per-row when interpretive ambiguity is suspected.

## Decisions still open after iter-1

- **Cross-regime row applicability**, per the weak-row analysis above. Two valid responses: prompt-side (per-domain extraction note) or compendium-side (description tightening). Lean prompt-side for iter-2; compendium-side requires Decision Log update + per-rubric audit re-walk.
- **Multi-rubric agreement projection**. Deferred to the validation-tool plan; iter-1 cannot self-validate against historical PRI 2010 / Newmark / CPI scoring without it.
- **Whether to expand the chunk vocabulary (e.g., split `definitions` further by regime)**. Iter-1 evidence says no — 7 rows × 3 regimes is well within attention budget; no dilution observed.

---

## Next iteration

**Recommendation: proceed to iter-2 on the same chunk.** Add a `definitions`-specific per-domain note to the v2 prompt instructing the harness on cross-regime row applicability (when a compendium row's category partially maps to a parallel regime, prefer `not_addressed` with parallel-regime mapping in evidence_notes; reserve `required` / `not_required` for cases where the statute affirmatively addresses the category as named). Re-run the same 3-temp-0 dispatch on `definitions` and confirm the disagreement on `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER × retirement_system` collapses to 3-way `not_addressed` consensus (or measure the new disagreement signal if not).

If iter-2 produces ≥14/15 unanimous status agreement again with the disagreement resolved (or stably explained), expand to a second chunk for iter-3. The natural next chunk is `contact_log` (14 rows, smallest after `definitions`) — it's a structurally distinct extraction shape (per-engagement disclosure obligations) and tests whether the architecture generalizes off the qualitative-materiality-heavy `definitions` cases.

**Cost of iter-1 (3 runs):** ~$1.50 total token spend, ~10 min wall time end-to-end (after scaffolding was in place). Phases 0–3 plus this iteration: ~6 hours total work, 4 commits + 2 fix-up commits on `statute-extraction` branch.

---

## Appendix: artifacts

- Run dirs: `data/extractions/OH/2025/definitions/{cc24d8920949, dea6828ac0bc, 4ad20debaf31}/`
- Each contains: `brief_suffix.md`, `full_brief.md`, `meta.json`, `raw_output.json`, `field_requirements.json`
- Plan: `docs/active/statute-extraction/plans/20260501_statute_extraction_harness.md`
- Originating convo: `docs/active/statute-extraction/convos/20260501_harness_brainstorm_kickoff.md`

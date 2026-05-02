# Compendium Item Audit v3 — Phase 0 (Concerns Sweep) Implementation Plan

**Goal:** Walk all 141 compendium rows against five curation-fidelity criteria and produce a flat, classified concerns doc — without proposing or applying any fixes — so that Phase 1's solution design (a separate plan) sees the full cross-domain pattern of issues before it locks per-domain axis vocabularies.

**Originating conversation:** [`docs/active/statute-extraction/convos/20260502_compendium_audit_v3_brainstorm.md`](../convos/20260502_compendium_audit_v3_brainstorm.md)

**Spawning artifact:** [`docs/active/statute-extraction/plans/_handoffs/20260501_compendium_item_audit_handoff.md`](_handoffs/20260501_compendium_item_audit_handoff.md)

**Context:** Iter-1 of the statute-extraction harness (run on OH 2025 `definitions` chunk, 2026-05-01) surfaced that `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is target-axis but its name is direction-ambiguous; the harness only avoided a wrong reading by accident (single-preposition cue in the description). On rows where the model picks consistently-but-wrong, the inter-run-disagreement signal that caught this would be silent. v3 audits the compendium as a contract — not at extraction time via inter-run disagreement, but at curation time. Phase 0 is the data-gathering step; it is deliberately decoupled from solution-design (Phase 1) so cross-domain patterns can inform per-domain axis vocabulary harmonization.

**Confidence:** Exploratory. The latent-axis-bug rate is N=1 by accident. Phase 0 *is* the population estimate. The 8-tag taxonomy locked in this plan is starting-point posture; Phase 1 may split, merge, or rename tags after seeing the distribution.

**Architecture:** Pure analysis task. No code changes, no schema changes. Auditor reads source rubrics in `papers/text/` per the row's `framework_references` (resolved via `compendium/framework_dedup_map.csv`), evaluates each row against five criteria, and writes a structured Markdown concerns doc to `results/`. The concerns doc is the sole Phase 0 deliverable.

**Branch:** `statute-extraction` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/statute-extraction/`).

**Tech Stack:** None — analysis only. Optional: `pandas` or `csv` standard library for parsing `disclosure_items.csv` and `framework_dedup_map.csv`; `grep` for cross-row scope scans. No new code modules. No new tests.

**Execution model:** Implementing agent follows the Nori workflow (per `CLAUDE.md`). Pre-flight reads `STATUS.md`, `README.md`, this branch's `RESEARCH_LOG.md`, the spawning convo above, the v2 audit doc `docs/COMPENDIUM_AUDIT.md` (Decision Log D1–D11 is procedural template), and the iter-1 analysis (`results/iter-1_analysis.md`) so the seed example `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is concrete.

---

## What's in scope for Phase 0

1. Walk all 141 rows of `compendium/disclosure_items.csv`.
2. For each row, evaluate five criteria (C1–C5 below) and record concerns with tag + evidence.
3. Aggregate by tag, by domain, by concern-count-per-row.
4. Write the concerns doc at `docs/active/statute-extraction/results/20260502_compendium_audit_concerns.md` (date in filename = sweep date, may differ from this plan's date).
5. Surface 5–10 highest-confidence concerns to the user as a checkpoint before Phase 1's plan is written. (User can validate the audit's output shape early; Phase 0 doesn't need user approval to *complete* — only to hand off to Phase 1.)

## What's explicitly NOT in scope for Phase 0

- **Solution design.** No fix proposals, no rename suggestions, no description rewrites. Phase 1's job.
- **Per-domain axis vocabulary lock.** Phase 0 may *observe* candidate vocabularies (e.g., `definitions` uses target/actor/threshold) but does not lock them. Phase 1's job.
- **Schema changes.** v1.2 schema stands; v3 does not reopen the schema-axis-field decision unless Phase 0 surfaces evidence-of-need (which goes into the concerns doc as `other-issue` with explicit rationale).
- **Decision Log D12+ entries in `docs/COMPENDIUM_AUDIT.md`.** Phase 1's job.
- **Cascade-cost counting per fix.** Phase 1 (since fixes don't exist yet).
- **Cross-rubric coverage expansion.** v3 is curation cleanup, not coverage expansion. New rubrics or new rubric items are explicitly out of scope. (If Phase 0 finds rubric items in `papers/text/` that aren't in `framework_dedup_map.csv`, that's a `other-issue` flag with note "coverage gap, defer to v3+ scope decision" — not action.)

---

## Per-row evaluation criteria (C1–C5)

For each row, the auditor records every concern that applies. A row may have zero, one, or multiple concerns. A concern is a *flag* — not a fix proposal. Multi-concern rows get one row in the concerns table per concern, plus one summary entry in the per-row coverage table.

### C1 — Name clarity (axis-explicitness)

**Question:** Does the row ID communicate the row's intent unambiguously, particularly w.r.t. axis (target / actor / threshold / process / cadence / scope / granularity / etc.)?

**Procedure:**
1. Read the row ID without looking at the description.
2. Predict what the row is asking.
3. Compare to the description.
4. If a careful fellow could plausibly map the ID to a different axis than the description intends, flag.

**Tags:**
- `axis-ambiguous-name` — ID doesn't disambiguate axis (description does, but ID alone doesn't).
- `name-misleading` — ID actively suggests the wrong axis or scope (stronger than ambiguous; description says X, ID implies Y).

**Reference example:** `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` — ID could mean "lobbying *by* admin agencies" (actor-axis) or "lobbying *directed at* admin agencies" (target-axis); description clarifies target. Tag: `axis-ambiguous-name`.

**Edge case — axis-less rows.** Some rows are legitimately not axis-typed (e.g., enforcement penalty existence checks). Mark as `no-axis-applies` in the per-row coverage table; do not flag as a concern.

### C2 — Description fidelity (vs source rubric items)

**Question:** Does the row's description faithfully express what the source rubric items in `framework_references` were asking?

**Procedure:**
1. Read the description.
2. For each `framework_reference` on the row, look up the rubric item in `compendium/framework_dedup_map.csv` (per-rubric audit trail), then in the source paper text under `papers/text/<paper>.txt`.
3. Compare: does the description capture the rubric items' question, or has it drifted (broader, narrower, or differently-scoped)?

**Tags:**
- `description-rubric-drift` — description says X, source rubric items asked Y; X ≠ Y in a way that affects extraction.

**Edge case — source rubric ambiguity.** If the rubric item *itself* is ambiguous (the paper's wording is unclear), flag as `description-rubric-drift` with evidence noting "rubric-side ambiguity, not curation error" — defer the resolution to Phase 1, but record the observation. Don't try to reinterpret the paper.

**Edge case — empty `framework_references`.** A row with no source rubric items can't be C2-evaluated. Tag as `other-issue` with note "missing framework_references — curation gap from v2 audit".

### C3 — Framework-reference cohesion

**Question:** Do all `framework_references` clustered under one row actually ask the same question?

**Procedure:**
1. List each `framework_reference` for the row.
2. For each, read the source rubric item in `papers/text/`.
3. Check: are these items asking *one* substantive question, or *multiple* axis-divergent questions that v2's topic-similarity grouping happened to cluster?

**Tag:**
- `cluster-asks-two-questions` — `framework_references` cluster contains items that ask structurally different questions and should be split.

**Reference for v2 grouping rules:** `docs/COMPENDIUM_AUDIT.md` Decision Log D1–D11 — v2 grouped by topic similarity; v3's job is checking whether topic-similarity inadvertently bundled axis-divergent items.

### C4 — Cross-row scope clarity

**Question:** Are adjacent rows' axes explicit and non-overlapping? Do any pair of rows have scope overlap such that two rows could plausibly catch the same statutory provision?

**Procedure:**
1. After C1–C3 pass on a row, scan the rest of the same domain (and the whole compendium for cross-domain pairs that share a topic-keyword).
2. For each candidate-conflict pair, check: would the harness have a clear rule for which row "owns" a given statutory provision, or could both plausibly fire?

**Tag:**
- `cross-row-overlap` — two (or more) rows could plausibly extract the same statutory provision; readers/harness will confuse them.

**Reference example:** the handoff cites `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (target-axis, definitional) vs. `REG_EXECUTIVE_AGENCY` (actor-axis, registration domain) — intentional separation, but names don't make that obvious. Tag whichever row's *name* is the cause.

### C5 — Domain assignment

**Question:** Is each row in the right `CompendiumDomain` per the v1.2 enum (`definitions` / `registration` / `reporting` / `contact_log` / `financial` / `relationship` / `revolving_door` / `accessibility` / `enforcement` / `other`)?

**Procedure:**
1. Read the description.
2. Read the v1.2 `CompendiumDomain` Literal definition in `src/lobby_analysis/models/compendium.py`.
3. Decide: is this row's substance better fit by a different domain?

**Tag:**
- `wrong-domain` — row would be better-placed in a different `CompendiumDomain`.

**Edge case — `other` overuse.** If a row sits in `other` and Phase 0 finds it has a clear better home, flag `wrong-domain`. If `other` truly fits, no flag.

---

## Concerns-doc format

Output: `docs/active/statute-extraction/results/<SWEEP_DATE>_compendium_audit_concerns.md` (Markdown).

```markdown
# Compendium Audit v3 — Phase 0 Concerns

**Branch:** statute-extraction
**Sweep date:** YYYY-MM-DD
**Compendium snapshot:** sha (compendium/disclosure_items.csv) + sha (compendium/framework_dedup_map.csv)
**Rows audited:** 141
**Auditor:** [agent name + run note]

## 1. Concerns

| # | row_id | criterion | tag | confidence | evidence | note |
|---|---|---|---|---|---|---|
| 1 | DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C1 | axis-ambiguous-name | high | name says "trigger"; description says "contact with administrative... agencies as a registration trigger" — target-axis. ID could read as actor-axis. | reference example from iter-1 |
| 2 | ... | ... | ... | ... | ... | ... |

(One row per concern. A row with N concerns appears N times here.)

## 2. Per-row coverage

| row_id | C1 | C2 | C3 | C4 | C5 | concern_count | notes |
|---|---|---|---|---|---|---|---|
| DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | flag | ok | ok | flag | ok | 2 | — |
| DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST | ok | ok | ok | ok | ok | 0 | — |
| ... | | | | | | | |

(One row per compendium row. `flag` / `ok` / `n/a` per criterion. "n/a" means the criterion doesn't apply — e.g., C1 on an axis-less enforcement row.)

## 3. Aggregate counts

### By tag
| tag | count |
|---|---|
| axis-ambiguous-name | N |
| name-misleading | N |
| description-rubric-drift | N |
| cluster-asks-two-questions | N |
| cross-row-overlap | N |
| wrong-domain | N |
| other-issue | N |

### By domain
| domain | rows | concerns | concerns_per_row |
|---|---|---|---|
| definitions | 7 | N | N/7 |
| registration | ... | ... | ... |
| ... | | | |

### By concern-count-per-row
| count | num_rows |
|---|---|
| 0 | M |
| 1 | M |
| 2 | M |
| 3+ | M |

## 4. Observed candidate axis vocabularies (informational, not locked)

For each domain, list the axes that appeared in C1 flags. Phase 1 uses this as input to the per-domain vocabulary lock; Phase 0 does not lock.

## 5. Notable patterns flagged for Phase 1

5–10 free-text observations the auditor wants Phase 1 to engage with first. E.g., "All 7 `definitions` rows whose description mentions 'lobbying' need axis-in-ID encoding"; "3 rows reference rubric items that don't appear in `papers/text/<paper>.txt` — cross-check needed".
```

The "5 notable patterns" section satisfies the spawning handoff's "first 5–10 highest-confidence issues" deliverable, surfaced inside the same concerns doc rather than as a separate artifact.

---

## Sequencing within Phase 0

A single agent can run Phase 0 end-to-end in one session (target ≤4 hours wall time given 141 rows × five criteria + paper lookups). Suggested order:

1. **Pre-flight reads** (per Nori workflow): `CLAUDE.md`, `STATUS.md`, `README.md`, this branch's `RESEARCH_LOG.md`, the spawning convo, this plan, `docs/COMPENDIUM_AUDIT.md`, `results/iter-1_analysis.md`.
2. **Load source data**: `compendium/disclosure_items.csv`, `compendium/framework_dedup_map.csv`, `src/lobby_analysis/models/compendium.py` (for the `CompendiumDomain` Literal), `src/scoring/chunk_frames/definitions.md` (for the iter-2 axis vocabulary precedent).
3. **First pass — C1 + C5 (cheap, ID-only + description-only)**: walk all 141 rows; record `axis-ambiguous-name` / `name-misleading` / `wrong-domain` flags. No paper lookups yet. Aim ~1 minute per row.
4. **Second pass — C2 + C3 (expensive, paper lookups)**: walk all 141 rows; for each, resolve `framework_references` to source rubric items and check fidelity + cohesion. Aim ~2 minutes per row.
5. **Third pass — C4 (cross-row scans)**: scan within each domain for scope overlaps; cross-domain only where topic keywords match. Aim ~30 minutes total.
6. **Aggregate**: build the three count tables and the candidate-axis-vocabulary section.
7. **Notable patterns**: write the 5–10 "highest-confidence concerns" section last, after seeing the full distribution.
8. **Surface to user**: post a summary to the user (paste the aggregate tables + the notable patterns section). Phase 0 deliverable is shipped.

If iter-2 of the statute-extraction harness is dispatched in parallel during Phase 0 execution, that's fine — Phase 0 reads the compendium, doesn't write to it. No conflict.

---

## Edge cases and risks

- **Rows with empty `framework_references`.** Cannot be C2/C3 evaluated. Flag as `other-issue` with note. May represent v2 curation gaps.
- **Source rubric items missing from `papers/text/`.** Some papers may have OCR or extraction gaps. If the dedup-map references a rubric item the auditor can't locate in the text, flag as `other-issue` with note "rubric-text gap — defer to paper-audit". Don't reinterpret.
- **Multi-axis rows.** Some rows are legitimately multi-axis (e.g., a row that's both actor-axis and threshold-axis). Phase 0 records both observations under C1 with notes; Phase 1 decides whether to split or accept multi-axis.
- **The 7 `definitions` rows already have iter-2 chunk-frame preamble disambiguating axes.** Phase 0 should still flag axis-ambiguous IDs/descriptions for these rows — the ID and description are the load-bearing layer; the preamble is a parallel concern. Note in the per-row notes that the chunk-frame preamble exists.
- **`docs/COMPENDIUM_AUDIT.md` (v2) D1–D11 represent prior decisions.** Phase 0 may surface concerns that *contradict* prior decisions; record them honestly with note "appears to revisit Dn" — Phase 1 decides whether to override.
- **Auditor scope creep into solution design.** Discipline reminder: Phase 0 classifies, doesn't fix. If the auditor finds themselves writing "rename to X" — stop, write only the concern, defer the rename to Phase 1.
- **Concerns-doc churn.** If the auditor revises tag taxonomy mid-sweep (e.g., a new pattern emerges that doesn't fit the 8 starting tags), record under `other-issue` with detailed evidence; do not retroactively re-tag prior rows. Phase 1 reconciles.
- **Cascade-blind concerns.** Phase 0 doesn't know cascade cost yet (no fix proposed). It's possible Phase 0 flags rows whose fix would be prohibitively expensive; Phase 1's job is the cost/benefit weighing.

---

## Testing plan (analysis-task exception per write-a-plan skill)

This is a **pure analysis task**. No TDD applies. Per the `write-a-plan` skill's exception clause: "Pure analysis or exploration tasks ... need a clear description of what to run, what outputs to check, and what constitutes a surprising result."

**What to run:**
- The 8-step sequence above.

**What outputs to check:**
- The concerns doc exists at the planned path.
- The Concerns table is non-empty (we already know `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` should produce at least one C1 concern).
- The Per-row coverage table has exactly 141 rows, one per compendium row.
- The aggregate counts sum correctly (concerns count by tag = total rows in Concerns table).
- The candidate axis vocabularies section names at least 1 axis for `definitions`.
- The 5–10 notable patterns section exists.

**What constitutes a surprising result:**
- **Concern rate < 5/141 (~3%).** Means iter-1's surfaced bug was a true outlier and v3's full-sweep posture was over-scoped. Phase 1 plan should reflect a much narrower remediation.
- **Concern rate > 50/141 (~35%).** Means curation has structural drift that Phase 1's solution design needs to triage aggressively (not all 50 fixes can land at once).
- **Tag distribution heavily skewed.** If 80%+ of concerns are `description-rubric-drift` (not axis), the v3 strategy refocuses away from axis-in-ID and toward description rewrites. Phase 1 plan changes shape.
- **Domain skew.** If concerns concentrate in 1–2 domains, Phase 2's batching simplifies massively.
- **Cross-row-overlap clusters of 3+ rows.** Suggests deeper scope-design issue beyond per-row rename.

The "surprising result" categories above are flags for the Phase 0 → Phase 1 handoff, not blockers for Phase 0 completion.

---

## Implementation Details

- **Auditor agent type:** general-purpose or a fresh Claude Code session works. The task is reading-heavy (CSV + papers), not code-heavy.
- **Paper text access:** `papers/text/<paper>.txt` files are pre-extracted; `grep` works directly.
- **Dedup map structure:** each row in `framework_dedup_map.csv` maps a (rubric, rubric_item_id) to a (compendium_row_id, decision); use it as the audit trail for C2/C3.
- **No commits during Phase 0 except the concerns doc + this plan + the convo file.** No fixes, no schema changes, no chunk-frame edits.
- **The concerns doc is checkpointable.** Auditor can save partial drafts mid-sweep (e.g., after pass 1 of 3) and commit; subsequent passes amend the doc.
- **Multiple sessions are fine.** Phase 0 doesn't have to land in one session; if it splits across sessions, the second session re-reads the partial concerns doc and continues.
- **No new code modules.** No `tests/` additions. No `src/` additions. No model changes.

---

## What could change

If Phase 0's findings shift the framing, downstream plans adjust:

- **If concern rate is low (<5%)**: Phase 1's plan downgrades to a narrow remediation pass (just `definitions` + the obvious cross-domain neighbors). Phase 2 may be a single PR.
- **If concern rate is high (>35%)**: Phase 1's plan adds a triage step (not all fixes land at once); Phase 2 batches by severity *and* cascade cohesion.
- **If tag distribution is dominated by `description-rubric-drift`** (not axis): the v3 strategy emphasis shifts to description rewrites; axis-in-ID renames become a smaller piece. The user-proposed `<DOMAIN>_<SUBJECT>_<AXIS>_<SPECIFIER>` convention may apply to fewer rows than the brainstorm assumed.
- **If `cluster-asks-two-questions` shows up frequently**: row splits become a major Phase 2 workstream, with its own cascade cost (one source row → two compendium rows + redistributed `framework_references`).
- **If Phase 0 surfaces evidence that schema-axis-field is needed after all** (e.g., per-domain natural-language axis vocabularies turn out to be unwieldy at scale): Phase 1 reopens the Option 1 vs 2 decision with new evidence. The brainstorm's Option 2 leaning was conditional on iter-1's N=1; Phase 0 supplies the population estimate.

---

## Resolved decisions (locked at plan-acceptance, 2026-05-02)

1. **Orphan dedup-map auditing is out of scope.** Dedup-map integrity is v2's responsibility. If a missing/orphaned dedup-map entry blocks C2/C3 evaluation on a row, flag the row as `other-issue` with note "dedup-map gap blocks C2/C3"; do not chase the orphan further.
2. **Concerns table includes a `confidence: high | medium | low` column** per concern. Confidence ≠ severity; it captures the auditor's certainty in the flag itself (useful when distinguishing "ambiguous" from "terse"). Phase 1 uses it as a secondary sort within concern groups.
3. **All 141 rows are audited at the same depth** — including the 33 `accessibility`-domain rows. Concerns are recorded only, not acted on; no churn risk to `oh-portal-extraction` or other accessibility-side work. The Phase 0 → Phase 1 handoff should explicitly note any accessibility-domain concerns so other fellows have visibility before Phase 1's plan engages them.

---

## Follow-up stages (informational, not gating)

This Phase 0 plan does **not** include Phase 1 or Phase 2 — those get their own plans, written *after* the Phase 0 concerns doc exists. Stages are documented here to keep the thread:

### Phase 1 — Solution design (separate plan, written after Phase 0 ships concerns doc)

- Group concerns by pattern (e.g., all `axis-ambiguous-name` rows in `definitions`).
- Lock per-domain axis vocabularies based on what concerns surfaced.
- Propose fixes per concern (rename / tighten description / split / merge / move-domain / no-action).
- Compute cascade cost per fix (touchpoint count: tests, dedup-map, prior run dirs, chunk-frame preambles, `.py` source).
- Output: Decision Log D12+ in `docs/COMPENDIUM_AUDIT.md` + per-batch fix manifest.
- User-review gate before any fix lands.

### Phase 2 — Apply fixes in cascade-cohesion batches (separate plan)

- Batch sizing by blast-radius cohesion (fixes that touch overlapping test files / fixture run dirs cluster), not necessarily by domain.
- Each batch = one PR or commit set; tests green throughout; dedup map + fixture references migrated alongside.
- Per-batch user-review gate.

The branch lifecycle (active → historical) for `statute-extraction` does not depend on v3 audit completion; v3 can land mid-branch (likely will, before iter-3+ on `contact_log`) and the branch closes when the harness reaches OH MVP plus templates to one additional state.

---

**Testing Details:** N/A — pure analysis task. Output validation criteria documented under "What outputs to check" above.

**Implementation Details:** No code changes. Three artifact additions: this plan + the convo file (already shipped this session) + the concerns doc (Phase 0 deliverable). Single-session execution feasible; multi-session checkpointing supported by writing partial-draft concerns doc and committing.

**What could change:** Documented in detail under "What could change" above. Headline: tag distribution + concern rate determine Phase 1's plan shape.

**Questions:** None open. Three plan-time questions resolved under "Resolved decisions" above.

---

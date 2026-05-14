# Factual-accuracy audit + merge — handoff

**Originating session:** [`../../convos/20260513_paper_summaries_audit_premerge.md`](../../convos/20260513_paper_summaries_audit_premerge.md) (paper-audit pre-merge; stub-indexed 20 branch-added papers; explicitly deferred Stop condition #4 — factual spot-checks — to a fresh agent)
**Predecessor handoff (now closed):** [`20260514_paper_summaries_audit_premerge.md`](20260514_paper_summaries_audit_premerge.md) (8 of 9 Stop conditions checked off in commit `31ba9ce`; #4 deferred → this handoff)
**Date drafted:** 2026-05-13 (paper-audit pre-merge session)
**Audience:** the next-session agent. **Fresh-context-safe.**

---

## Why this handoff exists

The paper-audit pre-merge session (`31ba9ce`) closed 8 of the 9 Stop/done conditions on the `20260514_paper_summaries_audit_premerge` handoff. **Stop #4 — "at least 3 summaries factually accurate against the source PDF" — was deferred** because the prior agent assumed the factual audit would be picked up by the Phase C projection TDD successor branch.

**User redirect 2026-05-13:** do the factual audit BEFORE merge, by a fresh agent. Then complete the merge. This handoff scopes both.

The rationale: the three load-bearing source-rubric summaries (Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010) feed projection logic on a successor branch. A factually wrong summary would propagate into projection code, where it's much more expensive to catch and fix than at the docs gate.

## What the prior session left

Branch state at commit `31ba9ce`:

- 37 PDFs in `papers/` (was 18 at handoff drafting time; 20 paper-additions to the branch had been missed in the handoff's count).
- 37 PAPER_INDEX entries — 17 pre-existing + 20 new stub-indexed (annotated `*[stub-indexed]*` in the index).
- 37 PAPER_SUMMARIES entries — same 17 pre-existing + 20 new stub-indexed (annotated `**Stub-indexed; not factually audited.**`).
- 1 web-only entry (Roth 2020 / lobbymeter.eu).
- 1 supplementary file mapping documented (Lacy-Nichols 2025 suppl).
- v2 row-set TSV (181 rows) is the compendium 2.0 contract — frozen in commit `9765e33` (see `results/projections/disclosure_side_compendium_items_v2.tsv` + `results/projections/20260513_row_freeze_decisions.md`).

Branch is **merge-ready in every other respect** — the only remaining work is the factual audit + the merge itself.

## Read order for the next-session agent

1. **This handoff** (full read).
2. **Predecessor convo:** [`../../convos/20260513_paper_summaries_audit_premerge.md`](../../convos/20260513_paper_summaries_audit_premerge.md) — what was done, what was deferred, why.
3. **Predecessor handoff (closed):** [`20260514_paper_summaries_audit_premerge.md`](20260514_paper_summaries_audit_premerge.md) — see the check-off list at the top of "Stop / done conditions" for context.
4. **The `auditing-paper-summaries` skill** at `/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md` (also bundled at `skills/auditing-paper-summaries/SKILL.md`) — specifically Step 3 ("Verify Each Entry Against Source Paper") and Step 4 ("Fix Errors").
5. **The 3 target summaries** in `PAPER_SUMMARIES.md`:
   - **PRI 2010** — last entry in the file, ~line 527 onward. Look for `### State-Level Lobbying and Taxpayers...`
   - **Lacy-Nichols 2024 / FOCAL** — `### Lobbying in the Sunlight: A Scoping Review...` around line 218.
   - **Newmark 2017** — `### Lobbying Regulation in the States Revisited` around line 382.
6. **The 3 source PDFs / text extractions** under `papers/text/`:
   - `papers/text/PRI_2010__state_lobbying_disclosure.txt`
   - `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt`
   - `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`
7. **`STATUS.md`** + **`docs/active/compendium-source-extracts/RESEARCH_LOG.md`** for branch context. STATUS lists the row-set freeze; RESEARCH_LOG has the trajectory.
8. **`CLAUDE.md`** for the active → historical lifecycle protocol (used post-merge).

## Stop / done conditions

The session is done when:

- [ ] **Factual audit complete on PRI 2010 summary:** verify the numerical claims against `papers/text/PRI_2010__state_lobbying_disclosure.txt`. At minimum, verify: (a) the 37-point disclosure-law max + 22-point accessibility max; (b) the top/bottom state lists for each rubric; (c) the average scores (21.9/37 for disclosure-law; 9.6/22 for accessibility); (d) the 5 sub-component A/B/C/D/E max-point counts (11/4/1/1/20); (e) the California case-study dollar figures ($552.6M total, $92.6M government, $131.4M after reclassification). Note any discrepancies in the convo + decide with user whether to correct inline or note via PAPER_INDEX Audit Notes.
- [ ] **Factual audit complete on Lacy-Nichols 2024 (FOCAL) summary:** verify against `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt`. At minimum: (a) "8-category, 50-indicator" framework count; (b) "15 lobbying transparency frameworks synthesized"; (c) any category-level claims; (d) the FOCAL-1 weight tables if cited (this is load-bearing for the Phase C TDD branch's projection arithmetic). Note discrepancies.
- [ ] **Factual audit complete on Newmark 2017 summary:** verify against `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`. At minimum: (a) the 19-item index structure; (b) the CPI↔PRI-disclosure r=0.04 correlation (the load-bearing finding for the rubric-unification rationale); (c) the new-index↔PRI-accessibility r=0.27 correlation; (d) the factor-analysis claim (4-6 factors, not 3 clean dimensions); (e) the "movers" state list (Arizona 6→16, etc.). Note discrepancies.
- [ ] **Any factual errors found are surfaced + decided** with the user: correct inline, note via PAPER_INDEX Audit Notes, or escalate as a finding worth a follow-up branch. Default for minor errors is correct inline.
- [ ] **PAPER_INDEX.md Audit Notes "Pending factual-accuracy audits" line updated** to reflect: the 3 spot-checks happened; what was verified; what was corrected; outstanding gaps.
- [ ] **Convo summary written** at `docs/active/compendium-source-extracts/convos/20260514_factual_audit_and_merge.md` (or whatever date the next agent's session falls on).
- [ ] **RESEARCH_LOG entry** for this session (newest first).
- [ ] **STATUS.md branch row updated** noting factual audit landed; Recent Sessions section gains a new top entry.
- [ ] **Audit commit + push** before proceeding to merge.
- [ ] **Merge `compendium-source-extracts` → `main`.** Standard merge (no squash; this branch's commit history is the permanent record per the user's CLAUDE.md). Push main.
- [ ] **Archive `docs/active/compendium-source-extracts/` → `docs/historical/compendium-source-extracts/`** via `git mv` (the lifecycle per CLAUDE.md). Update STATUS.md "Archived Research Lines" table with a row summarizing what was learned.
- [ ] **Cut 3 successor branches in parallel** (per Option B locked 2026-05-13):
  - `oh-statute-retrieval` (Track A; adds OH 2007 + OH 2015 to OH 2010 + OH 2025 bundles; HG 2007 ground-truth retrieval sub-task)
  - `extraction-harness-brainstorm` (Track B; brainstorm-then-plan; inherits prompt-architecture from archived `statute-extraction` iter-2; references v2 row set)
  - `phase-c-projection-tdd` (locked rubric order: CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024 — 8 rubrics; LobbyView is schema-coverage, not score-projection)
- [ ] **Final commit + push** of merge + archive state.

## Workflow

### Phase 1: Factual audit (3 papers, ~45-60 min)

For each of Newmark 2017, Lacy-Nichols 2024, PRI 2010 (parallelizable via subagent if you want to keep main-context clean, but a direct read is also fine since each .txt is short):

1. **Open the .txt** under `papers/text/`.
2. **Open the corresponding `PAPER_SUMMARIES.md` entry** (anchor section, ~30-50 lines).
3. **Check each numerical claim** against the source. The checklists under each Stop condition above are the minimum; if you encounter additional load-bearing numbers, verify them too.
4. **Note discrepancies in a scratch list.** For each: (a) summary claim; (b) source claim; (c) magnitude (typo / decimal place / wrong sign / fabricated entirely); (d) suggested fix.
5. **Surface findings to the user** before applying corrections. The user may want some fixed inline, some noted via Audit Notes, and some escalated.
6. **Apply approved corrections.** For factual errors: edit `PAPER_SUMMARIES.md` inline. For corrections of category-level magnitude: also update `PAPER_INDEX.md` one-liner if the inaccuracy bleeds through.

**Watchpoint:** the existing PRI 2010 summary cites very specific numbers (e.g., "South Carolina ranked 3rd on disclosure laws but 46th on accessibility"; "Connecticut 17.3/22") — these are the most likely to have transcription errors. Don't trust the precision; verify it. Similarly the Newmark 2017 r=0.04 / r=0.27 correlations are load-bearing for the unification rationale — exact values matter.

**Honesty note:** if any of these summaries turns out to be substantively wrong (not just transcription typos), that's a signal worth surfacing as a top-line finding in the convo summary. The user (per CLAUDE.md tone guidance) wants the concern at full strength, not softened.

### Phase 2: Audit commit + push (~5 min)

Single commit with: `PAPER_SUMMARIES.md` (corrections), `PAPER_INDEX.md` (Audit Notes update), `STATUS.md` (row update + Recent Sessions entry), `RESEARCH_LOG.md` (session entry), new convo, this handoff's Stop conditions checked off.

Push.

### Phase 3: Merge (~10-15 min)

```bash
git -C /Users/dan/code/lobby_analysis fetch origin
git -C /Users/dan/code/lobby_analysis checkout main
git -C /Users/dan/code/lobby_analysis pull --ff-only origin main
git -C /Users/dan/code/lobby_analysis merge --no-ff compendium-source-extracts -m "Merge compendium-source-extracts: compendium 2.0 row freeze (181 rows) + 9 projection mappings"
git -C /Users/dan/code/lobby_analysis push origin main
```

**No squash.** This branch's commits are the permanent record (per the CLAUDE.md branch-history note: "Research branches get merged to main — their git history becomes the permanent record.").

**Multi-committer hygiene:** before pushing main, `git fetch` to verify no one else pushed since you started. If there's divergence, **stop and surface to user** — don't auto-rebase someone else's work.

### Phase 4: Archive (~5 min)

```bash
git -C /Users/dan/code/lobby_analysis mv docs/active/compendium-source-extracts docs/historical/compendium-source-extracts
```

Then update `STATUS.md`:
- Remove the `compendium-source-extracts` row from Active Research Lines table.
- Add a row to Archived Research Lines table summarizing what was learned. Suggested entry (refine based on what the audit phase surfaced):

  > | compendium-source-extracts | Rebuilt the compendium from non-PRI sources (~26 papers extracted; 9 projection mappings to score-projection rubrics + LobbyView schema coverage). Phase A atomic-item extraction; Phase B per-rubric projection mapping; row-freeze brainstorm landed 181-row compendium 2.0 (8-rubric peak on `lobbyist_spending_report_includes_total_compensation`). Pre-merge factual audit of 3 load-bearing source-rubric summaries (Newmark 2017, FOCAL, PRI 2010) confirmed accuracy / [or: corrected N items]. | 2026-05-14 [or your date] | `docs/historical/compendium-source-extracts/` |

Commit + push the archive move.

### Phase 5: Cut 3 successor branches in parallel (~10 min)

Per Option B locked 2026-05-13, each successor branch gets its own kickoff session with its own plan doc. **This handoff does not write those plans** — they are post-merge work on each successor branch. But this handoff *does* create the empty branches so the next agents have somewhere to start.

For each of the three branches:

```bash
git -C /Users/dan/code/lobby_analysis checkout main
git -C /Users/dan/code/lobby_analysis pull --ff-only origin main
git -C /Users/dan/code/lobby_analysis worktree add -b <branch-name> .worktrees/<branch-name>
ln -s /Users/dan/code/lobby_analysis/data /Users/dan/code/lobby_analysis/.worktrees/<branch-name>/data
git -C /Users/dan/code/lobby_analysis/.worktrees/<branch-name> push -u origin <branch-name>
```

Replace `<branch-name>` with each of: `oh-statute-retrieval`, `extraction-harness-brainstorm`, `phase-c-projection-tdd`.

For each branch, **seed** `docs/active/<branch-name>/` with: `RESEARCH_LOG.md` (stub), `convos/`, `plans/`, `results/` directories. Stub the RESEARCH_LOG.md with a Purpose section pointing back to the compendium-source-extracts archive and Option B sequencing. Do NOT write the kickoff plan for each branch — that's the kickoff session's work.

Then update `STATUS.md` Active Research Lines table with 3 new rows (one per successor branch), each pointing at the row-freeze contract and noting the Option B parentage.

Commit + push the seed state per branch.

**Stop here.** Don't do the kickoff work on any of the 3 successor branches — that's their respective kickoff sessions' work, with whatever fellow gets assigned to each track.

## Watchpoints (carry forward)

1. **The 3 target summaries are pre-existing (pre-branch).** They've been in PAPER_SUMMARIES.md since the early branches. Any errors found are inherited, not introduced by `compendium-source-extracts`. Don't conflate fixing them with "branch cleanup" — they predate this branch.
2. **Lacy-Nichols 2024 vs 2025.** The summary at line ~218 is for the 2024 paper (FOCAL framework construction). The 2025 paper (FOCAL application + 28-country scoring) is a separate entry at line ~411 and was NOT in the deferred audit scope. Don't conflate them.
3. **PRI 2010 has 50 numerical claims.** Don't try to verify all of them; the Stop condition lists the highest-leverage subset. If you find one wrong number in that subset, expand scope; if the subset is clean, declare the spot-check done and move on.
4. **The Newmark 2017 r=0.04 correlation is *the* load-bearing finding** for why this project unifies multiple rubrics rather than picking one. If this number is wrong, surface it as a top-line finding — it changes how the project frames its calibration approach. (Almost certainly correct, but worth checking.)
5. **Bidirectional link graph hygiene.** Per the prior session's mistake recorded in MEMORY: "Walk the link graph when writing new docs." When you create the new convo, the new handoff (if any), and the new RESEARCH_LOG entry, make sure each has back-references to its predecessor and forward-references to its successor. Don't ship a half-linked graph.
6. **Multi-committer hygiene.** Other fellows may push to `main` while you're working. Before the final merge push, `git fetch` and verify `main` hasn't moved. Per CLAUDE.md: "If there are conflicts on someone else's work, **stop and surface them** rather than auto-resolving."
7. **`AGENTS.md` untracked.** The repo has an untracked `AGENTS.md` at root that wasn't created by the `compendium-source-extracts` branch — it appears across multiple worktrees. Leave it alone unless the user explicitly asks; don't include in any commit.

## Out of scope for this session

- Auditing the 20 stub-indexed papers added during the `compendium-source-extracts` branch (LaPira & Thomas 2014, McKay & Wozniak 2020, etc.). Those stay stub-indexed; full-read pass is a future-audit candidate.
- Reformatting `PAPER_SUMMARIES.md` to a uniform heading convention. The pre-existing inconsistency (Bacik 2025 + Kim 2025 use `## Paper` H2s; others use `### Paper` H3s under `## Category` H2s) is documented as a known issue in PAPER_INDEX.md Audit Notes.
- The CPI 2015 SII placement inconsistency (PAPER_INDEX puts it under State Lobbying Regulation Measurement, PAPER_SUMMARIES puts it under Compliance & Disclosure Quality). Documented, not fixed.
- Writing kickoff plans for the 3 successor branches. Those are post-merge work on each respective branch.
- Drafting any of the 3 successor branches' first convo. Same reason.

## Files this handoff references

- [`../../convos/20260513_paper_summaries_audit_premerge.md`](../../convos/20260513_paper_summaries_audit_premerge.md) — predecessor convo
- [`20260514_paper_summaries_audit_premerge.md`](20260514_paper_summaries_audit_premerge.md) — predecessor handoff (now closed)
- [`/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`](/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md) — also at `skills/auditing-paper-summaries/SKILL.md`
- `PAPER_INDEX.md` + `PAPER_SUMMARIES.md` (repo root) — to audit + correct
- `papers/text/Newmark_2017__lobbying_regulation_revisited.txt` — source for spot-check
- `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt` — source for spot-check
- `papers/text/PRI_2010__state_lobbying_disclosure.txt` — source for spot-check
- `STATUS.md` + `docs/active/compendium-source-extracts/RESEARCH_LOG.md` — to update
- `CLAUDE.md` — for the active → historical lifecycle protocol
- `results/projections/disclosure_side_compendium_items_v2.tsv` — the row-freeze contract; reference when seeding successor branches' RESEARCH_LOG stubs
- `results/projections/20260513_row_freeze_decisions.md` — the decision log; same reason

## Open the next session with

> "working on compendium-source-extracts branch; pick up from docs/active/compendium-source-extracts/plans/_handoffs/20260514_factual_audit_and_merge.md"

Same pattern the prior session used to start.

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

- [x] **Factual audit complete on PRI 2010 summary** (2026-05-13): All checked claims confirmed exactly against `papers/text/PRI_2010__state_lobbying_disclosure.txt`. (a) 37-pt disclosure-law max + 22-pt accessibility max ✓; (b) top/bottom states for both rubrics ✓ (MT/AZ/SC+TX top disclosure; WV+NV/NH/MD bottom; CT/NC+WA top accessibility; VT+WY/NH bottom); (c) averages 21.9/37 + 9.6/22 ✓; (d) sub-component max-point counts A:11 + B:4 + C:1 + D:1 + E:20 = 37 ✓; (e) CA $ figures $552.6M / $92.6M (16.8%) / $131.4M (23.8%) ✓. Plus methodology rules: B1/B2 reverse-scored per footnotes 85/86 ✓; E "higher of E1/E2 + F/G double-count + separate J" ✓; cross-rubric ranks SC 3rd-on-disclosure / 46th-on-accessibility ✓ and CT 18th-on-laws / 1st-on-accessibility ✓. **No corrections needed.** One paper-side counting curiosity at "11 states below 50%" (vs 12 from Table 5) documented but not actioned — paper-side issue, summary faithful.
- [x] **Factual audit complete on Lacy-Nichols 2024 (FOCAL) summary** (2026-05-13): 14/16 verifiable claims confirmed exactly against `papers/text/Lacy_Nichols_2024__focal_scoping_review.txt`. 1,911 records ✓; 15 frameworks (1991-2022) ✓; 248 items coded ✓; 8-category × 50-indicator ✓; 19/109 GDB countries ✓; financials 14/15 ✓; scope 13/15 ✓; 3 weighted frameworks ✓; FOCAL unweighted limitation ✓; scope+contact-log priority ✓; Chile contact-log exemplar ✓; UK/Australia third-party-only example ✓; enforcement excluded but in 11/15 ✓; integrity/codes excluded but in 6/15 ✓. **2 corrections applied:** (a) restored "contact log in 13/15" + deleted false parenthetical claiming the paper doesn't state it (paper p.1077-1079 explicitly does); (b) tightened "openness/data accessibility in 9/15" → "openness in 11/15 (open-data sub-theme specifically in 9/15)" per paper p.886-887 (FOCAL Openness category) vs p.809 (open-data sub-theme).
- [x] **Factual audit complete on Newmark 2017 summary** (2026-05-13): All 11 verifiable numerical claims confirmed exactly against `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`. (a) 19-item index 7+5+7 ✓; (b) **CPI↔PRI-disclosure r=0.04 (load-bearing finding) confirmed exactly at paper p.421-422** ✓; (c) new-index↔PRI-accessibility r=0.27 ✓; (d) factor analysis 4-6 factors not 3 clean dimensions ✓; (e) Arizona 6→16 mover with recipient-id-gap caveat ✓ + VA/IL/NC also moved up ✓. Plus: range 7-19, mean 12.96, SD 2.63, alpha 0.67, top/bottom-7 state lists, all other r values (0.40 Sunlight, 0.52 CPI, 0.54 BOS-2003). **No summary corrections needed.** **One sourcing nit noted in PAPER_INDEX Audit Notes:** the parenthetical "(lower than 2005's 0.71...)" — the 0.71 comparator is sourced from Newmark 2005 (separate paper, also in collection), not the 2017 PDF; flag for Phase C agents.
- [x] **Any factual errors found are surfaced + decided** with the user (2026-05-13): All 4 questions surfaced via AskUserQuestion. User selected: restore-and-delete-parenthetical for FOCAL contact log; tighten-to-show-both-numbers for FOCAL openness; note-in-Audit-Notes-only for Newmark 0.71 nit; convo named `20260513_factual_audit_and_merge.md`.
- [x] **PAPER_INDEX.md Audit Notes "Pending factual-accuracy audits" line updated** (2026-05-13): replaced with "Factual-accuracy audits landed (2026-05-13)" header and full per-summary verdict block (Newmark 2017, FOCAL, PRI 2010 each with their own paragraph documenting what was verified, what was corrected, outstanding sourcing nits).
- [x] **Convo summary written** at `docs/active/compendium-source-extracts/convos/20260513_factual_audit_and_merge.md` (2026-05-13; execution-date naming per the handoff's allowance).
- [x] **RESEARCH_LOG entry** for this session, newest first (2026-05-13).
- [x] **STATUS.md branch row updated** (2026-05-13): "Branch is one factual-audit session away from merge-ready" → "Factual-accuracy audit LANDED 2026-05-13... Branch is now MERGE-READY post-audit-commit." Recent Sessions section gained new top entry.
- [x] **Audit commit + push** (2026-05-13): commit `359e3b1` "FACTUAL AUDIT LANDED..." pushed to `origin/compendium-source-extracts`.
- [x] **Merge `compendium-source-extracts` → `main`** (2026-05-14): merge commit `cac1469` on `origin/main`. Standard `--no-ff` merge (no squash) executed via temp worktree at `/tmp/lobby_analysis_merge` to avoid disturbing the nori-init-docs worktree. **3 files had merge conflicts**, all resolved: (a) **README.md** — took branch (more comprehensive: includes "What we deliver" + "Project state" sections); (b) **PAPER_INDEX.md** — took branch (2 new categories + ~14 stub-indexed papers + Lacy-Nichols suppl mapping + audit-notes block); (c) **STATUS.md** — union resolution: branch base + integrated main's "## Compendium 2.0 success criterion" load-bearing section (positioned after the AGENT-CRITICAL banner, before Current Focus) + integrated main's 2026-05-07 (am) Recent Sessions entry (3-way consensus + CPI extract, authored on main directly while branch ran parallel; relabeled "(am)" for chronological clarity vs the branch's pm/eve/late-eve same-day entries) + bumped Last-updated to 2026-05-14. **AGENT-CRITICAL PRI 2010 banner kept as-is per user direction** (per-banner removal authorization deferred; PRI is back in scope as one of N projection rubrics, but the banner stays until the user explicitly clears it). Conflict resolution rationale captured in the merge commit message.
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

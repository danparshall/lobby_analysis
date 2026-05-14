# Pre-merge paper-summaries audit — handoff

**Originating plan:** [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md) (Phase B done condition; this audit is the LAST pre-merge gate)
**Predecessor convo:** [`../../convos/20260513_row_freeze_brainstorm.md`](../../convos/20260513_row_freeze_brainstorm.md) (row freeze landed; v2 TSV is the row-set contract)
**Predecessor handoff (now closed):** [`20260513_row_freeze_brainstorm.md`](20260513_row_freeze_brainstorm.md) (all 9 Stop/done conditions checked off in commit `9459c70`)
**Date drafted:** 2026-05-13 (late-late-late-late-late eve; immediately after row-freeze closed)
**Audience:** the next-session agent. Fresh-context-safe.

---

## Why this handoff exists

The row freeze landed (181-row v2 TSV at `results/projections/disclosure_side_compendium_items_v2.tsv`; decision log at `results/projections/20260513_row_freeze_decisions.md`). **Only one pre-merge audit remains: `auditing-paper-summaries`.** This handoff scopes that audit, then sets up the merge.

Two flags from the 2026-05-13 (late-late-late eve) union session that are this audit's input:

1. **PAPER_INDEX has 17 entries but there are 18 PDFs in `papers/`.** One PDF is unindexed.
2. **~16+ papers were added to the branch's `papers/` directory** by parallel processes during the branch's life. Not all of these are necessarily in `PAPER_INDEX.md` + `PAPER_SUMMARIES.md`.

## What freeze-vs-audit means

- **Freeze (done last session):** locks the compendium 2.0 row set (181 rows). Successor branches reference v2 as their contract.
- **This audit (now):** verifies the `papers/` infrastructure is consistent (every PDF extracted to `papers/text/`, every paper indexed + summarized, summaries factually accurate). Doesn't change the compendium row set; it's about the literature trail behind the rubric extracts.

The audit is a separate concern from the freeze and runs against a separate set of files.

## Stop / done conditions

**EXECUTED 2026-05-13 (paper-audit pre-merge session).** Convo: [`../../convos/20260513_paper_summaries_audit_premerge.md`](../../convos/20260513_paper_summaries_audit_premerge.md). RESEARCH_LOG entry above the row-freeze entry.

**Successor handoff (for the deferred Stop condition #4 + merge):** [`20260514_factual_audit_and_merge.md`](20260514_factual_audit_and_merge.md) — drafted 2026-05-13 after user redirect (factual audits move out of Phase C and back to a pre-merge gate; new agent picks up the audit + merge + archive + cut-3-successor-branches mechanics).

- [x] Every PDF in `papers/` has a corresponding extracted text file in `papers/text/` — 37 PDFs, 39 .txt files (37 main + 2 Lacy-Nichols 2025 suppl from `Lacy-Nichols-Supple-File-1-IJHPM.pdf` split into `__suppl_001/__002.txt`; Roth 2020 .txt is a WebFetch capture, no PDF — both mappings documented in PAPER_INDEX Audit Notes).
- [x] Every paper in `papers/` is indexed in `PAPER_INDEX.md` with a one-sentence summary — 17 pre-existing + 20 new stub entries (annotated `*[stub-indexed]*`).
- [x] Every paper in `papers/` has a key-conclusions entry in `PAPER_SUMMARIES.md` — 17 pre-existing + 20 new stub entries (annotated `**Stub-indexed; not factually audited.**`). Note: most stubs have at least one numerical finding from the survey subagent's read; those without explicit numbers reflect papers where the source is qualitative (e.g., AccessInfo standards, Council of Europe recommendation).
- [ ] Spot-check: at least 3 summaries factually accurate against the source PDF — **DEFERRED** with explicit followup recorded in `PAPER_INDEX.md` Audit Notes section. Targets when revisited: Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010 (the three load-bearing source rubrics for Phase C projection TDD). Owner: Phase C projection TDD successor branch.
- [x] PAPER_INDEX entry count == PDF count — **37 PAPER_INDEX entries = 37 PDFs** + 1 web-only (Roth 2020); the handoff's "17 vs 18" estimate was stale (actual was 17 vs 37 with 20 unindexed). Reality reflected in this audit; entry count now matches PDF count exactly.
- [x] STATUS.md branch row updated noting audit landed — `compendium-source-extracts` row's Status column appended; Recent Sessions section gained a new top entry; "Last updated" bumped to 2026-05-13.
- [x] RESEARCH_LOG entry for this session — new top session entry in `docs/active/compendium-source-extracts/RESEARCH_LOG.md` above the row-freeze entry.
- [x] Convo summary written + commit + push — convo at `docs/active/compendium-source-extracts/convos/20260513_paper_summaries_audit_premerge.md`; commit + push completes this session.
- [x] Updated handoff describing merge readiness — this file (these check-offs); branch is merge-ready.

**Merge sequencing reminder (for the next session):** merge `compendium-source-extracts` → `main`, archive `docs/active/compendium-source-extracts/` → `docs/historical/compendium-source-extracts/` per the lifecycle in `CLAUDE.md`, then cut 3 successor branches in parallel per Option B (OH statute retrieval; extraction harness brainstorm; Phase C projection TDD).

## Read order for the next-session agent

1. **This handoff** (full read)
2. The **`auditing-paper-summaries` skill**: `/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`
3. **`PAPER_INDEX.md`** + **`PAPER_SUMMARIES.md`** at repo root
4. List `papers/` and `papers/text/` to inventory current state
5. The predecessor convo (skim) for context on what the freeze landed: [`../../convos/20260513_row_freeze_brainstorm.md`](../../convos/20260513_row_freeze_brainstorm.md)

## Inputs

- `papers/` — raw PDFs (18+ files; exact count to verify)
- `papers/text/` — extracted text files (should be 1:1 with PDFs)
- `PAPER_INDEX.md` — one-sentence-per-paper index (currently 17 entries; needs to grow)
- `PAPER_SUMMARIES.md` — key-conclusions per paper

## Workflow (per the skill)

The `auditing-paper-summaries` skill walks each paper, checks the 3 invariants (extraction exists; indexed; summarized), and prompts the user when discrepancies surface. Don't auto-fix — surface and let the user decide. For new papers added during this branch's life, the user may direct adding via the `add-paper` skill.

## After this audit

**Then merge** `compendium-source-extracts` → `main`. The merge is a separate session per branch hygiene. Once merged:

**Cut 3 successor branches in parallel** (per Option B locked 2026-05-13):

1. **OH statute retrieval** (Track A; adds OH 2007 + OH 2015 to existing OH 2010 + OH 2025 bundles; HG 2007 ground-truth retrieval sub-task)
2. **Extraction harness brainstorm** (Track B; brainstorm-then-plan; inherits prompt-architecture from archived `statute-extraction` iter-2; references v2 row set)
3. **Phase C projection TDD** — locked rubric order: CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024 (8 rubrics; LobbyView is schema-coverage, not score-projection)

Each successor branch gets its own kickoff session with its own plan doc on its own branch.

## Watchpoints (carry forward)

1. **The decision log is the durable freeze artifact.** If anything in the audit surfaces a need to reconsider a row decision, it should NOT be quietly altered in v2 — instead, document the new finding and propose a follow-on freeze pass on a new branch. The current freeze is the contract; revisions are a fresh decision.
2. **The 16+ branch-added papers may include duplicates of existing entries** (same paper added via different filename conventions). Spot-check for duplicates before adding new index entries.
3. **Papers/text/ should be 1:1 with papers/.** A missing text file is an extraction gap that should be filled (use the `add-paper` skill for the extraction step) — but if the source PDF is image-only/scanned, the user may have a different intent.
4. **The `papers/` directory is not the same as the compendium `results/` directory.** The audit walks `papers/` only.

## Out of scope for this session

- Compendium row-set changes (those are frozen; new row decisions need a fresh branch)
- Phase C projection logic (downstream)
- OH statute retrieval (downstream)
- Harness brainstorm (downstream)
- Merging (separate session after this audit)
- Drafting the 3 successor plan docs (post-merge work, on each successor branch)

## Files this handoff references

- [`disclosure_side_compendium_items_v2.tsv`](../../results/projections/disclosure_side_compendium_items_v2.tsv) — the locked row set
- [`20260513_row_freeze_decisions.md`](../../results/projections/20260513_row_freeze_decisions.md) — decision log (D1-D30 + appendix)
- [`20260513_row_freeze_brainstorm.md`](20260513_row_freeze_brainstorm.md) — predecessor handoff (all done conditions checked off)
- [`/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`](/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md) — the skill to run
- `papers/` + `papers/text/` + `PAPER_INDEX.md` + `PAPER_SUMMARIES.md` (repo root) — the audit's inputs/outputs

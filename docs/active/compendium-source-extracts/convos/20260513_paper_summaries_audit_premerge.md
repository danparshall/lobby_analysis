# Paper-summaries audit pre-merge — convo

**Date:** 2026-05-13 (paper-audit pre-merge session)
**Branch:** `compendium-source-extracts`
**Originating handoff:** [`../plans/_handoffs/20260514_paper_summaries_audit_premerge.md`](../plans/_handoffs/20260514_paper_summaries_audit_premerge.md) — drafted 2026-05-13 late-late-late-late-late eve (anticipating next-day execution, hence the 14 in the filename); executed 2026-05-13 (same UTC day)
**Predecessor convo:** [`20260513_row_freeze_brainstorm.md`](20260513_row_freeze_brainstorm.md) — the compendium 2.0 row freeze that this audit follows
**Skill executed:** [`/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`](/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md) (also at `skills/auditing-paper-summaries/SKILL.md` in the repo)
**RESEARCH_LOG entry:** [`../RESEARCH_LOG.md`](../RESEARCH_LOG.md) §`2026-05-13 (paper-audit pre-merge)`
**STATUS row update:** `STATUS.md` `compendium-source-extracts` row — added "Pre-merge `auditing-paper-summaries` LANDED" segment; Recent Sessions section gained a new top entry

## Purpose

Run the `auditing-paper-summaries` skill as the LAST pre-merge gate per the 2026-05-13 row-freeze handoff. Verify `papers/` infrastructure is internally consistent (every PDF has a text extraction, every paper is indexed in PAPER_INDEX + PAPER_SUMMARIES) before merging `compendium-source-extracts` → `main` and cutting the 3 successor branches per Option B.

## Inventory delta vs. the handoff

The handoff said:
- 17 PAPER_INDEX entries
- 18 PDFs
- ~16+ branch-added papers

Actual at execution:
- **17 PAPER_INDEX entries** (matches)
- **37 PDFs in `papers/`** (handoff was stale by ~20)
- **39 .txt files in `papers/text/`** (37 main + 2 Lacy-Nichols 2025 suppl files split into __001/__002 from a single PDF + 1 Roth 2020 orphan; nets to 37 sources)
- **20 PDFs not in PAPER_INDEX** before this audit (handoff said ~16+)

The handoff's numbers reflected an earlier branch state. ~20 papers were added during the 3-week branch life (mostly during Phase A/B cross-rubric work that pulled in international/comparative-regulation literature). Not a bug in the handoff — just stale.

## What got done

### 1. Inventoried structurally

Discrepancies surfaced to the user:
1. **20 PDFs not in PAPER_INDEX / PAPER_SUMMARIES** — listed explicitly.
2. **Orphan text extraction without source PDF:** `papers/text/Roth_2020__lobbymeter_robustness_index.txt`.
3. **PDF / text naming mismatch:** `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` ↔ `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_{001,002}.txt`.
4. **PAPER_SUMMARIES uses two heading conventions** — pre-existing inconsistency that breaks the format-audit script.

### 2. Decisions per discrepancy

User direction (via AskUserQuestion):

| Discrepancy | User's decision |
|---|---|
| 20 unindexed PDFs | Stub-index all 20 (one-line PAPER_INDEX + short PAPER_SUMMARIES stub each; "not fully read" annotation). |
| Roth 2020 orphan | Investigate first → confirmed web-source-only WebFetch capture from 2026-05-03 of lobbymeter.eu Google Sites page. Keep as-is. |
| Lacy-Nichols suppl naming | Document mapping in PAPER_INDEX.md (durable) NOT in convo (session-scoped). Reason: convos are for retracing logic, PAPER_INDEX is load-bearing reference. |
| Factual spot-checks (handoff Stop #4) | Defer **with an explicit followup note** so it doesn't get forgotten. User explicit: "if we're skipping, then we need a task or note to be sure we don't forget at the end of this session." |

### 3. Roth 2020 investigated

Read `papers/text/Roth_2020__lobbymeter_robustness_index.txt`. Content: a 59-line WebFetch summary header noting:
> Source: https://sites.google.com/view/regulating-lobbying/home/work-of-colleagues/creating-a-valid-and-accessible-robustness-index
> Captured: 2026-05-03 (via WebFetch summary; Google Sites page does not host a directly linkable PDF)

Decision: keep the .txt; add Roth 2020 to PAPER_INDEX under International / Comparative Lobbying Regulation with "(web-source-only; no local PDF)" annotation. The .txt is both the source-of-record and the "extracted text" in this case.

### 4. 20-paper survey via subagent

Dispatched one `general-purpose` subagent with the 20 file paths, asking for: paper title, authors/publisher, date, ≤35-word PAPER_INDEX summary, suggested category, 2-3-sentence PAPER_SUMMARIES stub, confidence rating. Depth cap: ~500 lines per paper. Returned a clean markdown report covering all 20 with honest confidence calls (most HIGH, two MEDIUM where extraction was sparse — Global Data Barometer 2022 and SOMO 2016).

Subagent's category recommendations (which I largely adopted):
- 11 papers fit a new **International / Comparative Lobbying Regulation** category (added Roth 2020 to bring this to 14)
- 2 papers fit a new **Lobbying & Political Outcomes (empirical)** category (Flavin 2015, Strickland 2014/2018)
- 4 papers fit existing categories: LaPira & Thomas 2014 → Lobbying Data Infrastructure; Chung 2024 + Lacy-Nichols 2023 → Compliance & Disclosure Quality; CPI 2015 SII → State Lobbying Regulation Measurement (the C11 atomic items source already cited in 2026-05-07 RESEARCH_LOG entry)
- 1 was supplementary material (Lacy-Nichols suppl): folded under existing Lacy-Nichols 2025 entry as a note, not a separate row

Strickland filename year discrepancy flagged: filename says 2014 but SAGE DOI (10.1177/1532673X18788049) indicates 2018 publication. Decision: keep filename, note actual date in entries.

### 5. Stub entries written

PAPER_INDEX.md restructured into a single Write call:
- Same intro
- Added `## Audit notes` section at top with 5 durable annotations: stub-indexed convention; Lacy-Nichols suppl mapping; Roth 2020 web-source-only; deferred factual-accuracy audits (Newmark 2017 + FOCAL + PRI 2010 for Phase C); format-script known issue
- 6 categories total (4 existing + 2 new)
- All 20 new entries marked `*[stub-indexed]*`
- Lacy-Nichols 2025 entry got "Supplementary:" annotation pointing to the 3 files involved

PAPER_SUMMARIES.md appended (existing structure preserved):
- New `## International / Comparative Lobbying Regulation` H2 + 14 stub entries (Hogan/Murphy/Chari 2008 through IBAC 2022, chronological)
- New `## Lobbying & Political Outcomes (empirical)` H2 + 2 stub entries (Strickland, Flavin)
- `## Compliance & Disclosure Quality (continued — 2026-05-13 additions)` with Lacy-Nichols 2023 + Chung 2024
- `## Lobbying Data Infrastructure (continued — 2026-05-13 additions)` with LaPira & Thomas 2014
- CPI 2015 SII entry inserted at end of pre-existing Compliance & Disclosure Quality section (functional placement; the PAPER_INDEX puts it under State Lobbying Regulation Measurement, but PAPER_SUMMARIES.md historically uses Compliance & Disclosure Quality as the umbrella H2 for state-measurement papers — pre-existing inconsistency documented in Audit Notes)
- Every new entry marked `*[stub-indexed]*` and includes `**Stub-indexed; not factually audited.**`

### 6. STATUS + RESEARCH_LOG updated

- `STATUS.md` Last updated → 2026-05-13
- `STATUS.md` compendium-source-extracts row's Status column: appended "Pre-merge `auditing-paper-summaries` LANDED 2026-05-13 (this session): 20 branch-added papers stub-indexed..." + "Branch is merge-ready."
- `STATUS.md` Recent Sessions: new top entry summarizing this session
- `RESEARCH_LOG.md`: new top session entry (above the row-freeze entry) with Topics / Findings / Decisions / Mistakes / Results / Next Steps subsections

## Decisions (durable summary)

| topic | decision |
|---|---|
| 20 branch-added papers | Stub-indexed (one-line PAPER_INDEX + short PAPER_SUMMARIES stub each). Full-read pass deferred to a future audit. |
| Roth 2020 (orphan .txt) | Confirmed web-source-only; kept .txt as both source and extraction; documented "no PDF" in PAPER_INDEX. |
| Lacy-Nichols suppl naming | Mapping documented in `PAPER_INDEX.md` Audit Notes (durable, repo-level) — NOT in this convo alone. Per user: convos are for retracing logic, PAPER_INDEX is for load-bearing reference. |
| Factual spot-checks (Stop #4) | Deferred to **Phase C projection TDD successor branch**. Followup note placed in PAPER_INDEX.md Audit Notes. Targets: Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010. |
| 2 new PAPER_INDEX categories | Added: International / Comparative Lobbying Regulation (14 entries); Lobbying & Political Outcomes (empirical) (2 entries). |
| Strickland 2014/2018 filename | Filename kept as-is (working-paper year); actual publication year (2018, per SAGE DOI 10.1177/1532673X18788049) noted in entries. |
| Format-audit script over-counting | Documented as known issue (mixed heading convention in PAPER_SUMMARIES.md). Not blocking merge; reconciliation deferred. |
| Merge-readiness | **Branch is merge-ready** after this commit lands. |

## Mistakes recorded

- Initial TaskUpdate calls used `id` parameter (TodoWrite-style) instead of `taskId` (FleetView Task tool API); the four early calls failed silently leaving 4 tasks at `pending`. Fixed when the user asked about TodoWrite availability and I loaded the TaskUpdate schema. Not a research mistake; surface-level harness quirk worth recording so future Nori sessions in FleetView don't trip over the same thing.
- Convo filename uses 2026-05-13 (actual execution date) while the handoff filename uses 2026-05-14 (anticipatory). The asymmetry is intentional but worth noting for future readers walking the link graph: the handoff was drafted on 2026-05-13 late-late-late-late-late eve, hence the next-day filename, but execution happened later the same UTC day.

## Loose ends / future audits

1. **Deep factual audit of Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010** — the load-bearing source rubrics for Phase C projection TDD. **Owner: Phase C projection TDD successor branch.** Note recorded in PAPER_INDEX.md Audit Notes.
2. **Deep factual audit of the 20 stub-indexed papers** — particularly the high-relevance ones: LaPira & Thomas 2014 (biographical-record linkage methodology); McKay & Wozniak 2020 (cross-source disclosure validation); Strickland 2014/2018 (registration-rate endogeneity); AccessInfo 2015 (normative disclosure-field schema); Lacy-Nichols 2023 (academic indicator taxonomy). **Owner: a future audit branch; not blocking any specific downstream work.**
3. **PAPER_SUMMARIES.md heading-convention reconciliation** — Bacik 2025 + Kim 2025 use one format, other papers use another. The format-audit script breaks on this. Either update the script or reformat PAPER_SUMMARIES. **Owner: a future docs-hygiene pass; not blocking merge.**
4. **CPI 2015 SII placement inconsistency** — PAPER_INDEX puts CPI 2015 SII under State Lobbying Regulation Measurement (Category 4); PAPER_SUMMARIES has it under Compliance & Disclosure Quality (the umbrella for state-measurement papers in PAPER_SUMMARIES historically). Pre-existing pattern, documented but not fixed here.

## Cross-references

- **Predecessor convo:** [`20260513_row_freeze_brainstorm.md`](20260513_row_freeze_brainstorm.md) — compendium 2.0 row freeze landed v2 TSV
- **Handoff this session executed:** [`../plans/_handoffs/20260514_paper_summaries_audit_premerge.md`](../plans/_handoffs/20260514_paper_summaries_audit_premerge.md)
- **Skill used:** [`/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md`](/Users/dan/.claude/skills/auditing-paper-summaries/SKILL.md) — also bundled in repo at `skills/auditing-paper-summaries/SKILL.md`
- **Modified durable docs:** `PAPER_INDEX.md`, `PAPER_SUMMARIES.md`, `STATUS.md`, `docs/active/compendium-source-extracts/RESEARCH_LOG.md`
- **Source data files:** `papers/` (37 PDFs), `papers/text/` (39 .txt files), `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` (supplementary file with renamed extraction)

## Next session

**Merge `compendium-source-extracts` → `main`** (separate session per branch hygiene). Then archive `docs/active/compendium-source-extracts/` → `docs/historical/compendium-source-extracts/` and cut 3 successor branches in parallel per Option B (OH statute retrieval; extraction harness brainstorm; Phase C projection TDD with locked rubric order CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024).

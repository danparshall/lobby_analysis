# Kickoff + Branch Setup

**Date:** 2026-04-30
**Branch:** filing-schema-extraction

## Summary

End-of-session continuation of the OH-2025-baseline-SMR session on `statute-retrieval`. After shipping the OH 2025 PRI-projection MVP, the user directed: PR + merge of `statute-retrieval`, then create a plan to expand to the "full" compendium-SMR. This convo records the branch-creation and plan-writing work; the substantive design work is deferred to a brainstorming session per the parent multi-rubric harness plan's "Phase 3: extraction-first refactor (brainstorm-needed)" framing.

The kickoff plan is intentionally a brainstorming brief, not a TDD-ready implementation spec. Subagent architecture / prompt shape / multi-regime representation / negative-finding evidence are all open design questions the next session must resolve before any code lands.

## Topics Explored

- PR #4 created and merged with merge commit (preserve research-branch history): `0e5c19f`.
- Archived `docs/active/statute-retrieval/` → `docs/historical/statute-retrieval/`. Updated STATUS.md: removed Track A/B framing (those tracks merged into the archived branch's results); rewrote Current Focus around the PRI-projection MVP shipping; added statute-retrieval to Archived Research Lines table with full session summary; noted `oh-portal-extraction` as another fellow's active branch (not investigated this session).
- Created new worktree at `.worktrees/filing-schema-extraction/` with `data/scores` and `data/statutes` symlinks (same pattern as the parent branch's worktree). Seeded `docs/active/filing-schema-extraction/{RESEARCH_LOG, convos, plans, results}/`.
- Wrote `plans/20260430_filing_schema_extraction_kickoff.md` — kickoff brief naming the gap (96 statute-side compendium rows for OH; current PRI-projection fills 22), four scorer blind spots to fix (qualitative materiality, conjunctive E-series, multi-regime flattening, negative-finding evidence), seven open design questions, OH-first MVP path, OH 2025 PRI-projection SMR as calibration floor.

## Provisional Findings

(no substantive analysis this session — pure ops + brief writing)

## Decisions Made

- **PR + merge approach:** merge commit (not squash) to preserve the 21-commit research history of statute-retrieval; matches existing repo pattern.
- **Branch lifecycle:** statute-retrieval archived to `docs/historical/` per CLAUDE.md lifecycle. New successor branch `filing-schema-extraction` rather than continuing on the merged branch.
- **Plan shape:** brainstorming brief, not TDD spec. Justification: parent multi-rubric plan flagged this work as "brainstorm-needed"; getting subagent architecture + prompt shape wrong here costs weeks.
- **MVP scope = OH only.** CA / TX / other priority states templated after OH passes calibration.
- **Out of scope (explicit):** accessibility-side compendium rows (portal evidence, separate branch); MatrixCell projection layer; replacing data-model-v1.1 schema; disclosure-data pulling (other fellow's `oh-portal-extraction` branch).

## Results

(none — this session was ops + plan writing)

## Open Questions

The seven design questions in `plans/20260430_filing_schema_extraction_kickoff.md` § "Design questions" — all deferred to a brainstorming session.

Branch-level open question surfaced after this session: a parallel session on this branch (not investigated by me) is writing a `compendium_expansion_v2` plan that audits 5 unwalked rubrics (Opheim, Newmark 2005/2017, CPI Hired Guns, OpenSecrets) against the existing 118-row compendium. **Dependency:** if v2 expands the compendium beyond 118 rows, the kickoff's "MVP target ~96 rows" estimate needs re-scoping before the harness brainstorm runs. The other session's RESEARCH_LOG entry already flags this dependency.

## Commits

- `0e5c19f` (on main, merge commit) — PR #4 merging statute-retrieval to main
- `79c22b0` (on main) — Archive statute-retrieval (active → historical) + STATUS update
- `c862327` (on main) — Add provenance header to OH 2025 vs 2010 diff doc
- `c3c00d0` (on filing-schema-extraction) — Plan: filing-schema-first extraction harness (kickoff brief)

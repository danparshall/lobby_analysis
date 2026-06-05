# Scope correction: this branch ships deterministic Python, nothing more

**Date:** 2026-05-18
**Branch:** phase-c-projection-tdd
**Predecessor convos:** [`20260518_focal_hg_plans_drafting.md`](20260518_focal_hg_plans_drafting.md) (Sub-3), [`20260518_newmark_plans_drafting.md`](20260518_newmark_plans_drafting.md) (Sub-2), [`20260514_sub_1_sunlight_opheim_plans.md`](20260514_sub_1_sunlight_opheim_plans.md) (Sub-1), [`20260514_rubric_plans_drafting.md`](20260514_rubric_plans_drafting.md) (Sub-0)

## TL;DR

The only thing left to do on this branch is **ship deterministic Python that turns a populated SMR into a rubric score**. There are 4 modules to write (Newmark 2017, Newmark 2005, HG 2007, FOCAL 2024). Opheim 1991 is blocked. There is no LLM in the loop, no API key needed, no "headless launcher" to build, no canary to run.

## What this branch is

`f_rubric(compendium_cells_for_state_year) → rubric_score`. Pure dict-reading and arithmetic.

The hard upstream LLM work is **reading the statute and populating the SMR** — that lives on `extraction-harness-brainstorm` (Track B) and `oh-statute-retrieval` (Track A). Downstream of a populated SMR, the projection is mechanical.

The 3 shipped modules confirm the shape:

| Module | Lines | LLM imports |
|---|---|---|
| `cpi_2015_c11.py` | 389 | 0 |
| `pri_2010.py` | 416 | 0 |
| `sunlight_2015.py` | 452 | 0 |

Imports across all three: `csv`, `re`, `pathlib`, `typing`, `pydantic`, plus internal compendium-loader. That's it.

## What got fucked up

Two structural mistakes compounded across Sub-0 → Sub-3:

1. **Sub-0 (May 14) framed the remaining work as "5 implementations to delegate to LLM subprocesses to save subscription tokens."** That framing presupposed LLM agents were the right tool. They aren't — the work is deterministic Python, hand-writable in 1-2 focused sessions per module. The token-cost frame swallowed the actual-work frame.

2. **Sub-1/2/3 (May 18) drafted 5 plans totaling ~2,190 lines of structured English** describing how to write code totaling maybe ~1,500-2,000 lines once shipped. Plan-to-code ratio over 1.0 for purely mechanical work. The plans introduced 7 conventions, STOP clauses, Phase-0 cross-checks, 19 Open Questions — for code that's "read cell, apply tier, return score."

Plus a vocabulary bug: Sub-3 wrote "Sub-2 Newmark plans shipped + pushed" meaning the plan *documents* are committed and pushed. Read on a phone or compressed into a cross-machine status summary, "Newmark plans shipped" collapsed to "Newmark shipped." That compression made it look like there was less work left than there actually is, and produced a 4th conversation about scope.

## What's actually shipped vs. not

| Rubric | Code | Plan | Mapping doc |
|---|---|---|---|
| CPI 2015 C11 | ✅ shipped | n/a | ✅ |
| PRI 2010 | ✅ shipped | n/a | ✅ |
| Sunlight 2015 | ✅ shipped | n/a | ✅ |
| Newmark 2017 | ❌ | drafted | ✅ |
| Newmark 2005 | ❌ | drafted | ✅ |
| Opheim 1991 | ❌ blocked* | drafted | ✅ |
| HG 2007 | ❌ | drafted | ✅ |
| FOCAL 2024 | ❌ | drafted (4 sub-plans) | ✅ |

\* Blocked on 1988-89 statute data Track A doesn't currently retrieve. Comes off the blocked list when Track A expands vintage scope.

Filesystem + git history both confirm: no `newmark*.py`, `opheim*.py`, `hg*.py`, `hired*.py`, or `focal*.py` projection module has ever existed on any branch, local or remote. Only the 3 modules listed above have shipped.

## Retired

The following framings/artifacts are **retired** as scope on this branch:

- **`plans/20260514_headless_api_key_handoff.md`** — the headless `claude -p` launcher idea. Don't build a launcher. Don't run a canary. Don't worry about ordering enforcement between modules. Just write the code. (The API-key-on-`.env.local` documentation in that file is fine general background but doesn't belong in this branch's scope.)
- **The "Sub-0 / Sub-1 / Sub-2 / Sub-3 / Sub-4" multi-sub-session orchestration structure.** It was useful artifact when imagined; dead weight now. The remaining work is "write Newmark, write HG, write FOCAL" — call those sessions whatever the next agent likes.
- **The 7 Sub-0 conventions wrapped as ceremony.** Some of the underlying ideas are reasonable (use `unable_to_evaluate` sentinel; declare validation regime; record statute vintage). But the framing of "Phase 0 cross-check" as a separate ritual, STOP clauses for >10% spec-doc-vs-v2 drift, per-helper RED-then-GREEN documentation, is overhead. CPI/PRI/Sunlight shipped without any of that overhead. Match their shape, write tests as you go.
- **The 5 Sub-1/2/3 plans (`plans/20260518_*` + `plans/20260514_sunlight_2015_plan.md` + `plans/20260514_opheim_1991_plan.md`)** — **not deleted**, but use them only as *cell-mapping reference* (which v2 rows feed which item; what the spec-doc-vs-v2 rename table is; where the ground-truth CSV lives). Ignore the process framing wrapped around the mapping content.

## What the next agent does

1. Open `src/lobby_analysis/projections/sunlight_2015.py` and one of its test files (`tests/projections/test_sunlight_2015_*.py`). That's the template.
2. Open the relevant **mapping doc** in `docs/historical/compendium-source-extracts/results/projections/` (e.g., `newmark_2017_projection_mapping.md`). That's the spec.
3. Optionally skim the matching plan in `plans/20260518_*` for the cell-mapping table and rename list. **Stop reading at the cell mappings.** Ignore the TDD/STOP/Phase-0 process framing.
4. Write the module + tests. Run `uv run pytest tests/projections/`. Commit. Move on.

Suggested sessioning (one focused session each, possibly two together):

- **Session A:** Newmark 2017 + Newmark 2005. Newmark 2005 is ~100% reuse of 2017 mappings per the Phase B mapping commit message; it should be a near-twin with weak-inequality aggregation and a few imports from `newmark_2017`.
- **Session B:** HG 2007 (38 items, declarative `_ATOMIC_SPEC` per the mapping doc).
- **Session C:** FOCAL 2024 (50 indicators × weighted aggregation; richest validation thanks to L-N 2025 Suppl File 1).
- **Later / blocked:** Opheim 1991 (needs Track A's 1988-89 statute support; not this branch's concern until then).

After all 4 land + tests pass, this branch is ready to merge. The 8-rubric-confirmed promotion on `lobbyist_spending_report_includes_total_compensation` (at FOCAL landing) is the last "interesting" milestone.

## Vocabulary fix going forward

Reserve **"shipped"** for code + tests merged. Use **"drafted"** or **"landed"** for plan documents. The current ambiguous usage in convos and RESEARCH_LOG was the proximate cause of this scope-correction session.

## What did NOT change

- The 3 shipped modules (CPI, PRI, Sunlight) and their tests are untouched.
- The v2 row-freeze contract (`compendium/disclosure_side_compendium_items_v2.tsv`) is unchanged.
- The Phase B mapping docs in `docs/historical/compendium-source-extracts/results/projections/` are unchanged — those carry the substantive spec content.
- The 5 plans on this branch are not deleted; they remain as reference material.
- Nothing on main, nothing on sister branches.

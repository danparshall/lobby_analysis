# 2026-04-29: Retrieval Pipeline Design

## Session goal
Design a scalable two-pass statute retrieval pipeline that can run annually on all 50 states without manual per-state URL curation.

## Key decisions

1. **Calibration subset changed:** Dropped WY (too simple), kept WI (16 sections, good stress test), added OH (three separate lobbying statute bodies across two chapters). Final active subset: CA, TX, OH. NY/WI/WY URLs remain in `LOBBYING_STATUTE_URLS` but removed from `CALIBRATION_SUBSET`.

2. **Two-pass architecture adopted:**
   - Pass 1 (retrieval agent): starts from core lobbying chapter, identifies cross-references, retrieves support chapters (2-hop limit)
   - Pass 2 (scoring agent): scores expanded bundle against PRI rubric items
   - Checkpoint between passes: enriched manifest is the inspectable intermediate artifact

3. **Cross-reference discovery: approach C (LLM-driven with structured output).** No regex/heuristic layer. The retrieval agent gets state-specific citation examples in its prompt and outputs structured cross-reference data. Rationale: scales better than regex as models improve; the enriched manifest provides the safety net for auditing today's less-capable models.

4. **Enriched manifest format:** Each artifact gets `role` (core_chapter | support_chapter), `retrieved_because` (agent's reasoning), `hop` (0 for core, 1-2 for cross-refs), `referenced_from` (which file triggered retrieval). This is the audit trail for diagnosing scoring errors.

5. **PRI 2010 scores as TDD-equivalent test suite:**
   - PRI ground-truth scores = expected values (test assertions)
   - Pipeline output = actual values (code under test)
   - `calibrate` subcommand = test runner
   - Iterate: run pipeline → compare to PRI → diagnose failures → fix harness → re-run
   - Caveat: PRI had no published inter-rater reliability (single coder), so some disagreements may reflect PRI errors, not pipeline errors. Manifest audit trail helps distinguish.

6. **OH as first test case:** Three lobbying bodies (§§101.70-79, §§101.90-99, §§121.60-69) that cross-reference each other. If the retrieval agent can navigate OH's structure autonomously, it can handle most states. All 30 section URLs retrieved successfully; content verified.

## Context: prior work

- `pri-calibration` branch (now archived) ran a 5-state baseline: 0% exact match on disclosure-law. Root cause confirmed as H1 (bundle scope too narrow — missing cross-referenced support chapters like TX §311.005(2) "person" definition).
- The old approach (hand-curate URLs per state) doesn't scale to 50 states annually. This session reframes the problem: make the *agent* capable of following cross-references, rather than requiring human curation.

## Artifacts produced
- Branch `statute-retrieval` created with worktree
- OH URLs added to `LOBBYING_STATUTE_URLS` (30 URLs across 3 statute bodies)
- `CALIBRATION_SUBSET` updated to CA/TX/OH
- Statute text retrieved for all 3 states (data/statutes/)
- Tests updated and passing (248 pass, 3 pre-existing data-dependent failures)

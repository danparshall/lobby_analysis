# chunks_v2 implementation — Phases 0-7 under strict TDD

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Plan executed:** [`../plans/20260514_chunks_implementation_plan.md`](../plans/20260514_chunks_implementation_plan.md)
**Originating brainstorm:** [`20260514_chunks_brainstorm.md`](20260514_chunks_brainstorm.md) (Q1–Q7 architectural decisions)
**Handoff consumed:** [`../plans/_handoffs/20260514_chunks_implementation_handoff.md`](../plans/_handoffs/20260514_chunks_implementation_handoff.md)

## Summary

Executed all 7 phases of the chunks implementation plan under strict TDD on a single session. Wrote all 24 tests RED first (commit `8450bd6`); each subsequent phase commit turned its slice green in sequence. Full repo suite: 374 → **400 pass** (+26 new chunks tests; 5 skip and 3 pre-existing `test_pipeline.py` `FileNotFoundError`s unchanged from baseline, per user approval carried forward from the cell-models session).

The deliverable, `src/lobby_analysis/chunks_v2/`, partitions the 186-cell `CompendiumCellSpec` registry into 15 topic-coherent chunks via a hand-curated manifest. Two anchor chunks carry continuity from prior work: `lobbying_definitions` (15 rows; spiritual successor to iter-1's 7-row `definitions` chunk) and `lobbyist_spending_report` (34 rows; user-approved single-chunk-for-the-cluster decision). Five combined-axis rows co-locate per Q3 of the chunks brainstorm. `build_chunks()` enforces the partition as a coverage invariant — adding TSV rows without updating the manifest raises `ValueError`; removing TSV rows without updating the manifest raises `KeyError`.

This unblocks the retrieval implementation sub-branch: `tools.py`, `brief_writer.py`, and the coupling test all import from `lobby_analysis.chunks_v2`, and `CROSS_REFERENCE_TOOL`'s `chunk_ids_affected.enum` will source from `build_chunks()` directly.

## Topics Explored

- **Pre-flight + handoff trust.** The handoff was unusually detailed (state-of-play, what-not-to-touch, downstream consumer references), and verification confirmed its claims: working tree clean, `4c49888 retrieval_v2: scaffolding` already on `extraction-harness-brainstorm` HEAD, `src/lobby_analysis/chunks_v2/` non-existent on any branch (`git log --all -- src/lobby_analysis/chunks_v2/` returned nothing). Baseline pytest matched the cell-models session: 374 pass / 5 skip / 3 pre-existing.
- **Phase 0 coverage verification.** Wrote `/tmp/verify_chunks_coverage.py` to replay the plan's 15-chunk manifest as plain data and check it against `build_cell_spec_registry()` at branch HEAD. Result: **186/186 cells covered, no duplicates, no unknowns** — the plan author's 2026-05-14 claim still holds against the TSV at session start (no TSV drift).
- **Manifest layout decision (plan inconsistency resolution).** The plan's architecture diagram and `manifest.py` code snippet placed `ChunkDef` in `manifest.py`, but the Phase 2 wording said to implement both `Chunk` and `ChunkDef` in `chunks.py`. Going with the Phase 2 wording was the cleaner choice — it (a) avoids a circular import once `build_chunks()` lands in Phase 4 (chunks.py would need `from .manifest import CHUNKS_V2` while manifest.py would need `from .chunks import ChunkDef`), and (b) means the Phase 2 commit can turn the *entire* `test_chunks_dataclass.py` file green rather than splitting Chunk/ChunkDef across two phases. `manifest.py` ended up containing only the `CHUNKS_V2` constant and its `ChunkDef` import.
- **Default-argument circular import.** The plan's `build_chunks(registry=None, manifest: tuple[ChunkDef, ...] = CHUNKS_V2)` signature would have created a module-load-time cycle (chunks.py needs CHUNKS_V2; manifest.py needs ChunkDef). Rewrote the default as `manifest: tuple[ChunkDef, ...] | None = None` with a lazy `from .manifest import CHUNKS_V2` inside the function body. Behaviorally equivalent for callers; eliminates the cycle.
- **Validation regex pitfall.** The plan's draft `ChunkDef.__post_init__` used `not self.chunk_id.replace("_", "").isalnum() or not self.chunk_id[0].isalpha()` for the snake_case check, which lets `"BadCaps"` through (capital ASCII letters are alphanumeric). Used `re.fullmatch(r"^[a-z][a-z0-9_]*$", chunk_id)` instead — strictly lowercase ASCII as the plan's test #4 specifies.
- **__init__.py wiring grew across phases rather than being a one-shot Phase 5 commit.** Tests import from the package root (`from lobby_analysis.chunks_v2 import Chunk, ChunkDef, build_chunks, CHUNKS_V2`), so `__init__.py` had to expose Chunk + ChunkDef in Phase 2, then CHUNKS_V2 in Phase 3, then build_chunks in Phase 4. Phase 5 added the explicit `__all__` declaration + the package-root smoke test. This deviated slightly from the plan's "Phase 5 adds all exports at once" framing but matched the TDD discipline of one-test-file-green-per-phase.

## Provisional Findings

- **TDD discipline yielded clean per-phase signals** (mirrors cell-models). RED commit shows all 24 tests failing with `ImportError`; each implementation commit then turns exactly its target test file green. Phase 6 lint commit changed only whitespace/line-length cosmetics — 26/26 chunks tests stayed green post-format.
- **The plan's 181/181 row coverage assertion held empirically.** Phase 0's one-off coverage script verified the manifest covers all 186 cells against the real registry. The plan's manifest tests guard this going forward.
- **Combined-axis Q3 lock works end-to-end.** All 5 combined-axis rows (lobbyist_registration_required, lobbyist_spending_report_filing_cadence, lobbying_disclosure_audit_required_in_law, lobbying_violation_penalties_imposed_in_practice, registration_deadline_days_after_first_lobbying) have both their legal and practical cells in a single chunk per `test_combined_axis_rows_land_in_same_chunk`. `enforcement_and_audits` is the most concentrated case: just 2 rows in the chunk, both of them combined-axis → 4 cells, `axis_summary="mixed"`.
- **No manifest refinements were spotted during TDD.** The plan flagged 3 potential refinement targets: `enforcement_and_audits` 2-row chunk granularity, the `other_lobbyist_filings` catch-all assignment of `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying`, and the legal/practical mix in `oversight_and_government_subjects`. None warranted a change at this scope — the topic-coherence calls in the plan-author's draft hold. If the brief-writer brainstorm reveals a need for splitting/merging chunks, the test surface (manifest tests + the partition invariant in `build_chunks`) supports refinement without API breakage.
- **`axis_summary` derivation is robust to all 5 combined-axis cases.** `registration_mechanics_and_exemptions` (2 combined-axis rows in a chunk with 6 other legal-only rows) and `lobbyist_spending_report` (1 combined-axis row in a chunk with 33 other rows) both correctly resolve to `"mixed"`. `enforcement_and_audits` (2 combined-axis rows, no other members) is also `"mixed"` because the axes set is `{"legal", "practical"}` regardless of how many rows contributed it. The 12 single-axis chunks resolve cleanly to `"legal"` or `"practical"`.

## Decisions Made

- **`Chunk` + `ChunkDef` both live in `chunks.py`**, not split across `chunks.py` + `manifest.py` as the architecture diagram in the plan suggested. Avoids circular import; lets Phase 2 commit turn its tests green in one shot.
- **`build_chunks` has `manifest: tuple[ChunkDef, ...] | None = None`**, not the plan's `manifest: tuple[ChunkDef, ...] = CHUNKS_V2`. Resolved lazily inside the function. Same caller behavior; eliminates the module-load-time circular import.
- **`__init__.py` wired up incrementally per phase** (Chunk+ChunkDef in Phase 2; CHUNKS_V2 in Phase 3; build_chunks + `__all__` in Phase 5). The plan's intent — only Phase 5 wires exports — would have meant tests had to import from `lobby_analysis.chunks_v2.chunks` and `.manifest` until Phase 5, breaking the package-root import idiom the test files were designed around. Wired incrementally is cleaner and didn't compromise TDD.
- **`chunk_id` snake_case validation uses `re.fullmatch(r"^[a-z][a-z0-9_]*$", ...)`** rather than the plan's draft `isalnum()`+`isalpha()` check. Strictly lowercase per the plan's test #4 spec.
- **No manifest refinements applied this session.** The 15-chunk hand-curated manifest landed verbatim from the plan; topic-coherence judgment calls flagged in the plan's `notes` fields can be revisited during brief-writer brainstorm if a real reason surfaces.
- **No `data/` symlink added.** Chunks is pure-data; no gitignored outputs generated this session. Decision deferred to whichever component first writes gitignored data (likely retrieval impl when it runs the integration test).

## Results

Code-only session — no analytical outputs in `results/`. The deliverable is the `chunks_v2/` module surface itself; its contract is the four-symbol public API in `src/lobby_analysis/chunks_v2/__init__.py` and the 15-Chunk partition returned by `build_chunks()` against the 186-cell registry.

## Commits this session (oldest first)

| SHA | Message |
|-----|---------|
| `087edb6` | scaffolding: empty chunks_v2 module |
| `8450bd6` | tests (RED): full test suite for chunks_v2 layer |
| `487e713` | chunks_v2: Chunk and ChunkDef dataclasses |
| `b9731ee` | chunks_v2: CHUNKS_V2 manifest (15 chunks, 186 cells) |
| `c98ebd0` | chunks_v2: build_chunks() with full registry coverage validation |
| `54949c4` | chunks_v2: __init__ exports |
| `65fa872` | chunks_v2: lint + format pass |

## Open Questions

- **Whether `Chunk.cell_specs` should preserve manifest order or sort by `(row_id, axis)`.** Plan flagged this; chose preserve-manifest-order (matches how a brief-writer would emit the preamble + per-row instructions). Revisit if downstream wants sorted.
- **Whether `enforcement_and_audits` should merge into `oversight_and_government_subjects`.** Plan flagged this as a coherence call; left separate (topic distinct). The 2-row chunk doesn't violate any invariant; the brief-writer's preamble will likely cover the chunk effectively because both rows are combined-axis penalty/audit observables.
- **`other_lobbyist_filings`' assignment of `lobbyist_or_principal_spending_report_includes_contributions_received_for_lobbying`** (Newmark-distinctive observable) might fit better in `principal_spending_report` or `lobbyist_spending_report`. Plan flagged it as a coherence call; left in catch-all per plan author's judgment.
- **What `axis_summary` means downstream for brief-writer preamble selection.** Currently `"mixed"` chunks lump combined-axis rows + chunks-spanning-both-axes-of-different-rows under one bucket. If the brief-writer needs to distinguish "rows that are both legal AND practical" from "chunks containing some legal-only and some practical-only rows," extend the value space.
- **TSV drift detection cadence.** The manifest tests catch drift at `pytest` time, but no CI/cron alerts on TSV-vs-manifest mismatch in a way that would surface to a fellow editing the TSV directly. May want a pre-commit hook on the TSV in a future session.

## Next session

The chunks impl shipping unblocks the **retrieval implementation sub-branch**: Phase 1 onward of [`../plans/20260514_retrieval_implementation_plan.md`](../plans/20260514_retrieval_implementation_plan.md) can now run (Phase 0 already landed via the killed parallel session at commit `4c49888`; this session deliberately left `retrieval_v2/` untouched per handoff). The retrieval session's pickup verifies chunks shipped, then resumes from Phase 1 (`tools.py` + the chunks-coupling test).

After retrieval lands, the user's session strategy calls for two more brainstorm-then-impl cycles in this branch: **brief-writer** (orthogonal to retrieval; depends on cells + chunks, both done) and **scorer-prompt rewrite** (anchored on retrieval's bundle shape, so do after retrieval lands). Brief-writer is the cleaner next pick because chunks now exists as its primary input.

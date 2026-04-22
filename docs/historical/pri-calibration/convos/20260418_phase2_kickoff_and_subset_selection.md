# 2026-04-18 — Phase 2 kickoff + subset selection

Plan being executed: [`plans/20260418_phase2_statute_retrieval_and_baseline.md`](../plans/20260418_phase2_statute_retrieval_and_baseline.md)

## Session goal

Lock the four user-facing decisions the Phase 2 plan flags, then begin Phase 2a (statute retrieval pipeline, TDD).

## Decisions

### Q1 — Calibration subset (APPROVED)

**CA, TX, WY, NY, WI.**

- CA — team familiarity, carries the apples-to-apples comparison against the `scoring` branch portal pilot.
- TX — responder, large-state stress test, differently-named title from CA (Government Code, no standalone "Political Reform Act" container).
- WY — responder, bottom of PRI 2010 disclosure-law rank, minimal-statute stress test.
- NY — responder, upper-quartile, different title organization again (Legislative Law rather than Government Code).
- WI — responder, near-median.

All 5 are PRI responders. All 5 are `eligible_2010 == True` in `results/20260418_justia_retrieval_audit.csv`.

### Q2 — Statute-bundle commit policy (APPROVED)

Commit `manifest.json` files under `data/statutes/<STATE>/<YEAR>/` for provenance. Bulk `sections/*.txt` stays gitignored. Matches the pattern for `data/portal_snapshots/`.

### Q3 — Scorer-prompt source flag (APPROVED)

Add `role=statute` artifact support to `build_subagent_brief` and a one-sentence brief-header line: *"The artifacts below are state statute text (not portal content)."* The 22/61 rubric-item prompts stay unchanged.

Commit this as its own atomic commit separate from any later Phase-4 prompt-iteration changes, so future work can cleanly diff against "original scorer + one-line brief-header change only." Strictly speaking this is a prompt change, not an unchanged-prompt baseline — but the alternative (feeding statute text through a brief that says "portal snapshot") would confuse the scorer worse than the one-line header does. Dan's read: "still the crude assembly stage" — mitigation is adequate.

### Q4 — Rate limits (CLARIFIED, SPLIT)

Two different concurrency layers:

- **Justia retrieval** (Python + Playwright): courtesy delay drops from 5s to 2s. Concurrency can fan out (~5 browsers parallel); stay polite and fall back if Cloudflare re-challenges. Applies to `PlaywrightClient.__init__` default and the `retrieve-statutes` `--rate-limit-seconds` arg.
- **Scoring subagent dispatch** (Phase 3): stick with Claude Code subagents. ~4-10 concurrent, `asyncio.gather` + semaphore, back off on rate-limit hits. **No SDK switch for this phase.** Dan doesn't have API keys right now; if Phase 4 prompt iteration scales call count up, we'll revisit and budget the 1-2 days for an SDK rewrite. Logged design factor: **SDK would be materially more reproducible than subagents** — determinism at temp=0, explicit cost accounting, prompt caching, structured-output reliability. That's a real reason for the switch if it happens, not just throughput.

### R1–R3 — Risk acknowledgments

- **R1** (parser generalization is the real unknown — first non-CA state will likely break an assumption): noted. Plan's 1-2 additional fixtures before writing parser tests is the mitigation; don't skip.
- **R2** (20-40 min live-run estimate is optimistic; realistic is "half a day if one state surprises us"): acceptable.
- **R3** (the one-line brief header is technically a prompt change — calling this an "unchanged prompt baseline" obscures a degree of freedom): acceptable; the separate commit is the log.

## Next actions (Phase 2a)

1. Capture a non-CA fixture — TX (Government Code, Chapter 305 is the lobbying chapter IIRC). Use `tests/fixtures/justia/_capture.py`; add TX year-index + TX 2010 title-index first (to confirm URL structure), then add the Chapter 305 section-range leaf and re-run.
2. RED on parser tests (`parse_title_page`, `parse_section_range`) against both CA and TX fixtures.
3. Continue through Phase 2a per plan.

## Session log

- Pre-flight reads done (STATUS, README, pri-calibration RESEARCH_LOG, Phase 2 plan, Phase 1 convo).
- Four decisions locked + 3 risks acknowledged above.
- Proceeding to Phase 2a step 1 (TX fixture capture).

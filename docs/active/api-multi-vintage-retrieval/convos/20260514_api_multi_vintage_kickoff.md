# API-Driven Multi-Vintage Statute Retrieval — Kickoff

**Date:** 2026-05-14
**Machine:** Dans-MacBook-Pro
**Branch:** `api-multi-vintage-retrieval` (created this session, off `main` at `0a6804f`)

## Summary

User opened with a memory-check ("did we have a Justia pipeline?") that surfaced a recoverable data-loss story: their laptop crashed, but the desktop's `~/data/lobby_analysis/` (the canonical cross-machine data root via the `data/` symlink) held the pilot-state statute bundles intact. After verifying that, we scoped a new research line to extend the retrieval pipeline from single-vintage / 5-state to multi-vintage / 50-state, driven by direct Anthropic API calls rather than Claude Code subagents (token-budget pressure + embarrassing parallelism).

## What happened

1. **Memory recall.** Justia retrieval pipeline exists on `main`: `src/scoring/justia_client.py` (Playwright + fresh-browser-per-request to defeat Cloudflare), `src/scoring/lobbying_statute_urls.py` (curated per-`(state, vintage)` URL table), `cmd_retrieve_statutes` orchestrator subcommand. Built originally on `pri-calibration` (archived) and extended on `statute-retrieval` (archived).
2. **Pilot-state list reconciliation.** The user remembered "OH + CA + TX + ...?"; I surfaced the mismatch between (a) original 5-state pilot `CA/TX/NY/WI/WY` and (b) current code-level `CALIBRATION_SUBSET` of `CA/TX/OH` (reduced from the pilot to focus on difficult/informative states). User confirmed OH was a later decision and the pilot list is now 6 states.
3. **Data-loss check (the productive surprise).** User said "laptop crashed, lost the data." I checked `data/statutes/` anyway — fully populated for all 6 states. The `data/` directory in the repo is a symlink to `~/data/lobby_analysis/`, which is the cross-machine sync root; the laptop crash didn't touch the desktop copy. Wrote `/tmp/verify_statute_bundles.py` to integrity-check all bundles against their manifests (file presence + byte sizes + sha256 + Cloudflare-challenge-stub detection + orphan files). **Result:** 100 artifacts across 7 (state, vintage) bundles totalling 1.35 MB, every hash matched, no challenge stubs. Three orphan files in `CA/2010/sections/` (`gov-91000-91015.txt`, `gov-82030-82048.5.txt`, `gov-82000-82015.txt`) flagged but not touched (experiment-data-integrity rule).
4. **Scope reframe via `phase-c-projection-tdd`.** User pointed at `docs/active/phase-c-projection-tdd/results/20260514_rubric_data_years.md` (initially absent from my view because origin was stale; resolved with `git fetch`). That file documents 12 distinct vintages spanning 1988–2025 across 8 rubrics. **Key correction to my initial scope estimate (3 vintages):** Opheim 1991 + all 6 Newmark 2005 panels were scored off the Council of State Governments' "Book of the States," not off original statutes. Justia is the wrong substrate for those. The Justia-feasible vintage set is 6–7, not 12.
5. **Architectural decisions locked.**
   - **Branch name:** `api-multi-vintage-retrieval` (confirmed).
   - **HG 2007 split-vintage handling:** option (a) — two bundles per state, `data/statutes/<STATE>/2002/` and `data/statutes/<STATE>/2007/`, with a per-rubric mapping of which items consume which vintage. Cleaner data model than a single bundle with mixed-vintage sections.
   - **Pre-2005 rubrics (Opheim 1991, Newmark 2005 ×6 panels):** out of scope here. Parked for a successor branch (working name: `bos-archival-retrieval`) — different retrieval substrate (Internet Archive / HathiTrust / scanned BoS editions), not Justia.

## Key technical findings

- The `data/` symlink chain saved this work: worktree `data/` → main `data/` → `~/data/lobby_analysis/`. The laptop crash dropped the laptop's checkout but the desktop-side data root is canonical.
- All existing bundle manifests are byte-and-hash-verified against their disk artifacts. Reproducibility is intact.
- Greenfield on Anthropic SDK: no existing `import anthropic` anywhere in `src/`. This branch is the first direct-API usage.
- Existing prompt asset `src/scoring/retrieval_agent_prompt.md` (96 lines) is **cross-reference-expansion-shaped** (hop1: seed bundle in, support chapters out). It is **not** seed-discovery-shaped (no seed bundle yet, figure out the URLs for a state-vintage pair from scratch). The plan needs a new sibling prompt for seed discovery — or a generalisation of the existing one.

## Justia-feasible vintage targets (per `20260514_rubric_data_years.md`)

| Vintage | Rubric(s) | Notes |
|---|---|---|
| 2002 | HG 2007 Q35-Q37 only | Borderline Justia coverage; expect partial failure |
| 2006-07 | HG 2007 main (Q1-Q34, Q38) | |
| 2009-10 | PRI 2010 | Pilot states already done; need other 44 |
| 2014-15 | CPI 2015 C11 + Sunlight 2015 | Two rubrics, one fetch per state |
| 2015-16 | Newmark 2017 | Possibly merge with 2014-15 if statutes were stable |
| ~2021 | L-N 2025 (optional — calibration-free for states) | Decide at plan time |
| 2025 | "Today" baseline | OH already done |

Approximate scale: **50 states × ~6 vintages ≈ 300 (state, vintage) pairs** for URL discovery. Of those, the 6 pilot-state PRI 2010 bundles already exist and should be skipped via resume logic.

## Decisions made

1. **API key replaces subagents** for URL discovery and cross-reference expansion. Playwright fetch step is unchanged — it doesn't need an API key (already local).
2. **Six (or seven) Justia-feasible vintages in scope.** Anything Book-of-the-States-derived is out.
3. **HG 2007 → two bundles per state** (option `a`).
4. **HEAD-request verification between discovery and Playwright fetch** — catches hallucinated URLs before they waste bandwidth. STATUS.md previously flagged "15 states with flagged seeds" from prior subagent-based discovery; same failure mode applies to API discovery, same mitigation.
5. **Checkpoint everything per `(state, vintage)`**, including the exact prompt used. Resume idempotently. Experiment-data-integrity rule.
6. **Branch is new** (not slotted into an existing active branch). Substrate change, not a continuation.
7. **Direct Anthropic SDK, not headless `claude -p`.** Sister-branch `phase-c-projection-tdd` is moving its rubric-planning work onto `claude -p` (see `docs/active/phase-c-projection-tdd/plans/20260514_headless_api_key_handoff.md`). For URL discovery, full Claude Code session overhead per call is wasted on a narrow structured-output task. Both approaches bill the same `ANTHROPIC_API_KEY`; only the runtime differs.
8. **Default model: `claude-sonnet-4-7`**, not opus. User pushback (correct): URL discovery is pattern-matching + recall, not deep reasoning. Earlier scoring branches used opus because rubric interpretation against statute text is fundamentally harder; that doesn't transfer to discovery. Reserve opus as an escalation knob if canary quality is poor.
9. **API key source: `.env.local`** at the repo root. Already exists on main (473 bytes, gitignored via `.env*`). Symlinked into this worktree per `use-worktree` skill (had to retrofit — initial worktree setup symlinked only `data/`, not `.env.local`; corrected). Module-load helper parses the file manually — no `python-dotenv` dep for a single key.

## Mid-session corrections

- **`use-worktree` skill compliance:** initial worktree creation symlinked `data/` but missed `.env.local`. Skill explicitly calls for both. Corrected after user pointed at `.env.local` as the key source. Worth noting for future worktree creations.
- **Initial scope estimate was wrong.** I sized this as "3 vintages × 50 states = 150 calls." The actual answer (after reading the `phase-c-projection-tdd` rubric-data-years file) is 6–7 Justia-feasible vintages, with another 6 vintages requiring a different substrate (BoS) entirely. User correctly pointed me at that file before I committed the wrong scope to a plan.
- **Initial model recommendation was wrong** — defaulted to opus by reflex from prior scoring work. User correctly pushed back. Sonnet is the right tool here.

## Open questions (for the plan and subsequent sessions)

- **Seed-discovery prompt shape:** generalise `retrieval_agent_prompt.md` or write a new sibling prompt. The hop-1 version assumes a seed bundle exists; for greenfield states-vintage pairs there is no seed. Likely a two-step prompt: (a) given `(state, vintage)`, identify the relevant statute body and propose canonical Justia URLs; (b) optional follow-up cross-ref expansion once a seed exists.
- **L-N 2025 vintage:** include or exclude? The rubric has no state-level ground truth, so the "year" is a user choice. Cheap to include if we're already running 50 × N anyway.
- **Per-vintage audit cadence:** run `audit-statutes` once per vintage before discovery? Or fold it into the discovery step itself (the LLM probes Justia year-availability as part of URL identification)? Plan should pick one.
- **The 3 CA orphan files** — leave / re-index / move. Not in scope for this branch; flagged for user decision later.

## Next session

Implement per the plan: TDD scaffold the API discovery module, mock at the Anthropic SDK boundary, then run the per-state-vintage discovery for one canary state (probably CA 2015 — known vintage, known state, easy to verify against published rubric scores). Expand from there.

# Research Log: oh-portal-extraction

Created: 2026-04-30
Owner: Amina Rakhimbergenova
Track: B (portal scraping → `LobbyingFiling`)
Test state: Ohio

## Purpose

Extract actual lobbying disclosures from the Ohio state portal into the `LobbyingFiling` model (`src/lobby_analysis/models/filings.py`). Ohio is the team-wide test state for shaking out the end-to-end pipeline before broadening to other priority states.

This is the data-acquisition counterpart to Dan's Track A work (`statute-retrieval` archived 2026-04-30, succeeded by `statute-extraction`). The two tracks share a target schema (currently data model v1.3) and the locked 141-row compendium contract, but operate independently.

## Sessions

(Newest entries first.)

### 2026-05-07 — (A') brainstorm + implementation plan

- Pre-flight: caught up on a week of upstream work (compendium locked at 141 rows, schema bumped v1.1 → v1.2 → v1.3 with new `regime`/`registrant_role`/`condition_text` fields, `statute-retrieval` merged + archived, `statute-extraction` is Track A's active branch with iter-1 hitting 14/15 inter-run agreement on OH `definitions` chunk).
- Merged `origin/main` (39 commits) into `oh-portal-extraction`. One conflict on `STATUS.md`'s Active Research Lines table — resolved by keeping our row and Dan's `filing-schema-extraction` row, dropping his stale "(other fellow's branch — not investigated)" placeholder. Tests post-merge: 303 pass / 5 skipped / 3 pre-existing data-fixture failures unrelated to this branch.
- Ran the `brainstorming` skill end-to-end on "what does done-for-OH look like for the next ~2 weeks." Converged on a phased path: (A') smallest-viable single-filing round-trip → (B') single-regime MVP across all current filers → (C') graduate. Validation strategy for (A') is model-anchored hand-spot-check; SMR-anchored validation deferred to (B'). Regime choice for (A') = OH legislative agent (ORC §§101.70–101.79) — largest filer population, Track A's iter-1 already converged on its `definitions` chunk, statute structurally unchanged 2010 → 2025 per OH SMR diff.
- Brainstorm output (4 confirmed sections): (1) round-trip architecture; (2) source acquisition + sample selection; (3) extraction + validation; (4) failure handling + testing scope + definition of done.
- Switched to `write-a-plan` skill: drafted [`plans/20260507_oh_a_prime_implementation.md`](plans/20260507_oh_a_prime_implementation.md) with TDD-shaped tasks, explicit edge cases, two unit tests planned (extraction-brief substring assertions; provenance round-trip), one real LLM call against one real OLAC PDF as the end-to-end behavioral check.
- Open coordination items flagged for next weekly sync: (a) Anthropic SDK vs Dan's subagent-dispatch pattern preference; (b) v1.4 schema-gap handling protocol if (A') surfaces gaps; (c) canonical `regime` enum value for OH legislative agent — read from `origin/statute-extraction` before Phase 2.

### 2026-04-30 — Branch kickoff

- Cut `oh-portal-extraction` worktree off `main` (eb849ca).
- Seeded `docs/active/oh-portal-extraction/{convos,plans,results}/` and this log.
- Baseline check: tests passing, environment clean.
- Next: brainstorming session on what the OH portal looks like (existing snapshot in `docs/historical/pri-2026-rescore/` is the starting artifact). Decide scrape strategy before writing any extraction code.

## Plans

(Plans are added under `plans/` and listed here once written.)

- [`20260507_oh_a_prime_implementation.md`](plans/20260507_oh_a_prime_implementation.md) — single-filing round-trip on OH legislative agent A&E report; TDD-shaped, ~25 bite-sized tasks across 4 phases.

## Convos

(Convo summaries land under `convos/YYYYMMDD_topic.md` and are listed here.)

- [`20260507_oh_a_prime_brainstorm.md`](convos/20260507_oh_a_prime_brainstorm.md) — scope tier choice (A'/B'/C'), validation-strategy comparison (model-anchored / SMR-anchored / form-as-schema), regime selection (legislative), and 4-section design walk-through.

## Open questions

- **Resolved 2026-05-07:** OH snapshot tier under `docs/historical/pri-2026-rescore/` is *clean capture* (11 MB, 26 artifacts, no WAF/SPA blocker) — but the actual artifact bytes live only on Dan's laptop, so (A') fetches fresh from OLAC rather than reusing.
- Does OLAC require auth/CAPTCHA for individual report PDFs? Dan's 2026-04-13 snapshot didn't flag it, but he scraped discovery pages, not per-report PDFs. First execution of the (A') plan will surface this.
- Are OLAC report PDF URLs stable, or session-bound? Affects how we record the "stable identifier" for samples.
- Is `LobbyingFiling.model_json_schema()` clean enough for Anthropic SDK tool-use, or do its nested optionals/discriminated unions need flattening?
- What's the team's preferred protocol for handling v1.4 schema-gap proposals if (A') surfaces them — ad-hoc convo doc + Dan/Gowrav review, or a more formal RFC pattern?
- What's the right `ExtractionCapability` (`src/lobby_analysis/models/pipeline.py`) shape for OH — populated as a side-effect of the pipeline, or curated up-front? Deferred to (B').

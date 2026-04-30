# OH 2026 Baseline SMR — Implementation Plan

**Goal:** Produce a `StateMasterRecord` JSON for Ohio against the **2026-vintage** OH lobbying statutes, equivalent in shape to the existing OH 2010 baseline but reflecting current law. Output: `data/state_master_records/OH/2026/<run_id>.json`.

**Originating conversation:** end of session continuing `docs/active/statute-retrieval/convos/20260429_sunlight_pri_item_level_calibration.md`. The OH 2010 baseline was just produced via Stage B of `plans/20260430_compendium_population_and_smr_fill.md`; this plan re-runs the same pipeline for the 2026 vintage.

**Pre-flight reads (before doing anything):**

1. `STATUS.md` — current branch state, branch inventory.
2. `README.md` — what this repo is.
3. `docs/active/statute-retrieval/RESEARCH_LOG.md` — trajectory of thinking on this branch.
4. `docs/active/statute-retrieval/plans/20260430_compendium_population_and_smr_fill.md` — the parent plan whose Stage B you're re-running with a different vintage.
5. `docs/historical/pri-calibration/` — Justia retrieval architecture, statute bundle pattern, calibration harness. Most of the infrastructure you need was built there and is already on this branch.

**Current state on the `statute-retrieval` branch (as of last commit):**

- ✓ Compendium populated and committed at `data/compendium/disclosure_items.csv` (118 rows, framework-agnostic). Reuse for every vintage; nothing to rebuild.
- ✓ `compendium_loader`, `smr_projection`, and `cmd_build_smr` orchestrator subcommand all in place.
- ✓ OH 2010 SMR exists at `data/state_master_records/OH/2010/38803d49e32f.json` (gitignored, local to the worktree).
- ✓ `LOBBYING_STATUTE_URLS` in `src/scoring/lobbying_statute_urls.py` has an `("OH", 2010)` entry covering 30 sections across ORC Ch. 101 §§ 101.70-79 + 101.90-99 and ORC Ch. 121 §§ 121.60-69. **No `("OH", 2026)` entry exists yet — adding it is Phase 1, step 1.**
- ✓ Justia client (`src/scoring/justia_client.py`) handles the Cloudflare JS challenge via fresh-browser-per-request.
- ✓ Three pre-existing `test_pipeline.py` failures depend on `data/portal_snapshots/CA/2026-04-13/` which was lost when Dan's laptop was wiped. Out of scope for this plan; do not try to fix them.

**Confidence:** High that the pipeline reproduces; the OH 2010 path was just exercised end-to-end (compendium → calibration → projection → JSON). Medium on the URL pattern: Justia's URL convention may differ between 2010 and 2026 (saw 5 distinct conventions across 5 states during the original `pri-calibration` work). Low on whether OH's ORC chapter / section numbering has changed materially since 2010 — verify before assuming the same section list.

**Branch:** stay on `statute-retrieval` (worktree: `/Users/dan/code/lobby_analysis/.worktrees/statute-retrieval`). Do not branch off; this is a continuation of the same research line.

---

## Phase 1 — Retrieve the 2026 OH statute bundle

### 1.1 Add `("OH", 2026)` to `LOBBYING_STATUTE_URLS`

Open `src/scoring/lobbying_statute_urls.py`. The 2010 entry hard-codes the URL pattern:

```
https://law.justia.com/codes/ohio/2010/title1/chapter101/101_{n}.html
https://law.justia.com/codes/ohio/2010/title1/chapter121/121_{n}.html
```

For 2026, **start by hand-checking** the URL convention. Open `https://law.justia.com/codes/ohio/` in a browser and look at the most recent year Justia hosts. The URL pattern may be:
- `/codes/ohio/2026/title-1/chapter-101/section-101.70/` (newer slug-based)
- `/codes/ohio/2025/title1/chapter101/101_70.html` (legacy underscore)
- Some hybrid

**Do not guess.** Use the live Justia page to confirm the pattern, then template the section list. The 2010 entry is your starting reference for which sections to include. **Verify** the section numbering — ORC chapters 101 §§ 70-79 / 90-99 and 121 §§ 60-69 are the 2010 lobbying statute. If Ohio renumbered or moved any of these between 2010 and 2026, surface to the user before encoding the URLs.

Add the new entry alongside the 2010 one. Do not remove or alter the 2010 entry.

### 1.2 Audit URL reachability

Run:

```
uv run python -m scoring.orchestrator audit-statutes --state OH --vintage 2026
```

Expected output: every URL in the new entry returns a non-error response. If any 404 or look like Cloudflare-stub responses, fix the URL list before proceeding. **Don't** continue to retrieval until the audit is clean — you'll waste API budget on broken fetches.

### 1.3 Retrieve

```
uv run python -m scoring.orchestrator retrieve-statutes --state OH --vintage 2026
```

This populates `data/statutes/OH/2026/sections/` with one `.txt` per section plus a `manifest.json`. Confirm the manifest shows expected coverage (count ≈ 30 sections, similar to OH 2010 which had 30 sections at ~260 KB total). If short by a lot, **stop and surface** — Ohio may have moved a chapter and the URL list is incomplete.

### 1.4 Optional: cross-reference expansion

If the OH 2026 statute reads light or you suspect cross-referenced support chapters were missed (recall TX §311.005(2) "person" definition was missed in the original calibration — the H1 bundle-scope bug), run:

```
uv run python -m scoring.orchestrator expand-bundle --state OH --vintage 2026 --hop 1
uv run python -m scoring.orchestrator ingest-crossrefs --state OH --vintage 2026 --hop 1
```

This is judgment-call work; only do it if there's evidence (post-scoring) that the harness needed unreachable cross-references. Skip on the first pass.

---

## Phase 2 — Score OH 2026 against the PRI rubric

### 2.1 Prepare the run

```
uv run python -m scoring.orchestrator calibrate-prepare-run --state OH --vintage 2026
```

This writes a subagent brief at `data/scores/OH/statute/2026/<run_id>/briefs/pri_disclosure_law.brief.md`. Capture the printed `<run_id>` — you'll need it for Phase 3.

### 2.2 Dispatch the scorer subagent

Use the Claude Code Agent tool (subagent-only — there is no anthropic SDK in this repo). Read the brief at the path printed by `calibrate-prepare-run`. Dispatch with the following constraints:

- Read-only file access.
- `claude-opus-4-7` model (matches the 2010 baseline run for vintage-comparable scoring).
- The brief instructs the subagent to write a JSON output to a specific path. **Don't deviate** — the finalize step expects that exact path.
- Single run is sufficient for an MVP baseline; if you want a 3-run consistency check (recommended for any state we publish), dispatch three concurrent runs with different `run_id`s. The original PRI calibration showed safe concurrent batch ≈ 4 subagents (org-level Anthropic API rate-limit kicks in beyond that).

### 2.3 Finalize

```
uv run python -m scoring.orchestrator calibrate-finalize-run --state OH --vintage 2026 --run-id <run_id>
```

Validates the subagent JSON, stamps provenance, writes `data/scores/OH/statute/2026/<run_id>/pri_disclosure_law.csv`. If validation fails, **stop and read the JSON** — don't paper over — likely the subagent missed an item or emitted invalid scores.

### 2.4 (If 3 runs) Consistency check

```
uv run python -m scoring.orchestrator calibrate-analyze-consistency --state OH --vintage 2026 --run-ids <id1> <id2> <id3>
```

Inter-run flag threshold from prior Phase 3 work was 11.5%. If higher, the 2026 statute reading is unstable; investigate which items are flapping before proceeding to SMR projection.

---

## Phase 3 — Project to SMR

### 3.1 Run `build-smr`

```
uv run python -m scoring.orchestrator build-smr --state OH --vintage 2026 --run-id <run_id>
```

Reads the score CSV from Phase 2, loads `data/compendium/disclosure_items.csv`, calls `project_pri_scores_to_smr`, writes `data/state_master_records/OH/2026/<run_id>.json`. Output is gitignored.

**STOP-AND-NOTIFY guard:** if the OH 2026 PRI scores have multiple `E1h_*` or `E2h_*` set true on the same side (the situation that fired for TX 2009), the subcommand will refuse to write and print a JSON error with the conflicting items. **Do not silently override with `--allow-multi-frequency`.** Surface to the user, who may want to reason about the multi-cadence reporting before deciding. (Issue #3 tracks the schema fix that will eventually let multi-frequency states be represented structurally.)

### 3.2 Sanity-check the output

Spot-check the OH 2026 SMR JSON:

- 11 `registration_requirements` entries, one per A1-A11 role.
- `reporting_parties` has both `client` and `lobbyist` rows. Compare the `reporting_frequency` to OH 2010 (`tri_annually`) — if it changed, that's a real legal-change finding worth a note. If it became multi-set, see the STOP-AND-NOTIFY behavior above.
- `field_requirements` has 22 rows. The `lobbyist`-side `total_compensation` row should carry PRI + FOCAL + Sunlight refs in `framework_references` (the compendium union is preserved automatically; no curation needed here).
- `de_minimis_financial_threshold` and `de_minimis_time_threshold` should reflect 2026-vintage thresholds. OH 2010 had both null (no materiality test in the law as scored). If OH added a threshold between 2010 and 2026, it shows up here.
- `notes` carries the B-series govt exemptions and C-series public-entity-definition paragraphs.

---

## Phase 4 — Diff vs OH 2010 baseline

A short comparison report — not a deliverable, but worth doing for sanity:

1. Diff the two SMRs JSON-deep. Note which `registration_requirements[].required` flags flipped, which `field_requirements[].status` changed, whether de_minimis thresholds were introduced or modified, whether reporting frequencies shifted.
2. For each flipped item, find the supporting `legal_citation` in both SMRs. If the citation in 2026 references a different section than 2010, that's a real statute change. If the citation is identical but the score flipped, that's a scorer judgment-call divergence — flag it.
3. Capture the diff in `docs/active/statute-retrieval/results/20260430_oh_2026_vs_2010_diff.md` (or a session-dated equivalent).

This is the first multi-vintage-same-state comparison the project has produced. It's the kind of artifact that demonstrates the SMR's value as up-to-date democracy infrastructure: "these are the OH disclosure-law changes between 2010 and 2026, with statute-level evidence." Worth a short writeup.

---

## What could change

- **Justia URL convention.** May have moved between 2010 and 2026. Phase 1.1 is the highest-risk step; budget time for it.
- **OH may have renumbered.** ORC §§ 101.70-79 / 101.90-99 / 121.60-69 are stable across many states' typical revision cycle, but Ohio could have consolidated or split chapters. Verify in Phase 1.1 by spot-checking the section list against the 2026 codes index.
- **PRI 2026 rubric vs PRI 2010 rubric.** The repo has both (see `docs/historical/pri-2026-rescore/results/`). Both have the same 61 disclosure-law item IDs. The calibration harness scores against `pri_disclosure_law` (whichever rubric_loader resolves it to — default is the 2010 rubric per `src/scoring/rubric_loader.py`). Either is fine for SMR projection because the projection helper is keyed on item IDs, which are stable. Don't switch rubrics without thinking through implications.
- **Multi-frequency edge case.** OH 2010 had `tri_annually` (clean single value). If OH 2026 added an annual reconciliation requirement on top of the tri-annual session reports, you'll hit the TX-style multi-set case. See issue #3 for the long-term fix.
- **Multi-rubric calibration is descoped.** This plan uses only PRI as the scoring data source — same as Stage B of the parent plan. Sunlight and FOCAL refs already ride along on the compendium-keyed FieldRequirement rows; no separate Sunlight/FOCAL scoring is run.

## Pre-flight checks before starting

- `data/compendium/disclosure_items.csv` exists (it's committed; should be there on a clean clone).
- `data/state_master_records/OH/2010/<run_id>.json` exists or can be regenerated via `build-smr` against the existing OH 2010 score CSV at `data/scores/OH/statute/2010/38803d49e32f/`. (If not present after Dan's laptop wipe, regenerate first — it's the comparison anchor for Phase 4.)
- `data/scores/OH/statute/2010/38803d49e32f/pri_disclosure_law.csv` exists (the 2010 baseline scores). If missing, you cannot do Phase 4 diff; surface to the user.
- `LOBBYING_STATUTE_URLS` has the existing OH 2010 entry at `src/scoring/lobbying_statute_urls.py:55`. Confirm before adding 2026.

## Estimate

Half-day if the URL pattern is straightforward and Justia hosts 2026 OH codes cleanly. Full day if the URL convention is novel or any chapters have moved (Phase 1.1 expands). Phase 2.2 (subagent dispatch) takes ~5-10 minutes wall-clock for a single run, ~15 minutes for three concurrent runs at safe batch size.

## Out of scope (deliberate)

- **CA / TX 2026 baselines.** Do OH first; we'll repeat the pattern for CA and TX as separate sessions.
- **Sunlight / FOCAL as additional scoring data sources.** Same as parent plan B — those rubric refs ride along on compendium-keyed rows already.
- **Stage C.1 `MatrixCell` projection.** The N×50×2 matrix consumer doesn't exist yet.
- **Stage C.2 statute-extraction harness.** That's the long-term replacement for the PRI-data SMR fill. Don't try to design it here.
- **Issue #3 schema change** for multi-frequency. Land that on a separate branch before the harness ships.
- **Fixing the 3 `test_pipeline.py` failures** (missing `data/portal_snapshots/`). They predate this work and depend on data not currently present on the host.

## Commit hygiene

- Commit the `LOBBYING_STATUTE_URLS` change as its own commit (Phase 1.1).
- Statute bundle (`data/statutes/OH/2026/`) is gitignored — don't try to commit.
- Score CSVs are gitignored — don't try to commit.
- SMR JSON is gitignored — don't try to commit.
- The diff writeup in `docs/active/statute-retrieval/results/` is committed.
- Do NOT merge to main without explicit user request. This plan ends with a working OH 2026 SMR JSON locally + a commit on `statute-retrieval` for the URL list change + a diff results doc.

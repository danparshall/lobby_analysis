# Session: 2026-04-30 — OH 2025 baseline SMR (PRI-projection MVP)

**Originating plan:** `docs/active/statute-retrieval/plans/20260430_oh_2026_baseline_smr.md` (handoff to fresh agent; executed end-to-end this session)
**Branch:** `statute-retrieval` (worktree at `.worktrees/statute-retrieval`)

## What we did

Executed the OH 2026 baseline SMR plan end-to-end, diverging once when the live Justia probe surfaced that no 2026 OH vintage exists (Justia tops out at 2025). User confirmed `(OH, 2025)` was fine for an April-2026 calibration baseline.

- **Phase 1.1:** Confirmed Justia URL convention via `PlaywrightClient` probe — boundary sections (§101.70, §101.79, §101.99, §121.60, §121.69) all resolve at 2025; URL pattern identical to 2010 with year swapped (Justia redirects newer slug-based forms to legacy underscore form). Section list intact 2010 → 2025.
- **Phase 1.1 commit:** `ee4ffdd` — added `("OH", 2025)` to `LOBBYING_STATUTE_URLS` (30 URLs across ORC Ch. 101 §§ 70-79 / 90-99 + Ch. 121 §§ 60-69).
- **Phase 1.2:** Skipped redundant `audit-statutes` step — that subcommand is for cross-state Justia year-availability, not single-state URL verification. Reachability was implicitly verified by retrieve-statutes.
- **Phase 1.3:** `retrieve-statutes` produced 30 sections (~143 KB total). Apples-to-apples vs OH 2010 core 30 sections (140,828 B vs 143,408 B = +1.8%) — essentially identical corpus size. The plan's "~260 KB" reference was OH 2010 *with cross-refs expanded* (39 files); the curated core is much smaller.
- **Phase 2:** Prepared 3 run_ids (`26b1ab90b0eb`, `e7846593ebb5`, `736087384f85`) and dispatched 3 concurrent opus-4-7 scorer subagents per user request ("3 times for debugging"). All three returned `DONE 61` with all 30 statute files read in their `files_read.json` manifests. Finalized all three with `--skip-missing` (accessibility was deliberately not scored, matching the OH 2010 baseline pattern).
- **Inter-run consistency analysis:** 13 of 61 items disputed (21.3%, flagged at 11.5% threshold).
- **Phase 3:** Built SMR from r2 (`e7846593ebb5`) — selected because it best matches the 2010 baseline's scoring conventions on disputed binary items (8/9 agreement, vs 2/9 for r1 and 5/9 for r3). SMR shape: 11 registration_requirements / 2 reporting_parties / 22 field_requirements / both de_minimis null.
- **Phase 4:** Diff vs OH 2010 SMR. **Almost zero structural change** — one `governors_office.required: False → True` flip, plus version anchors. All field_requirements and reporting_parties identical. Notes paragraph reordered but same exemption set + C-series scoring.
- **Diff doc:** `results/20260430_oh_2025_vs_2010_diff.md` (committed `ce10674`).

## Mid-session reframes

### Reframe 1 (mid-Phase-2): "no single 2025 run is the correct legal reading"

After consistency analysis flagged 13 disputes, the user asked **"which interpretation of the laws is correct?"** Reading §101.72 (registration content) and §101.70(F) (legislative agent definition) directly:

- **E1b/E1d/E2b/E2d (address+phone):** §101.72(A) requires *business address* only. Phone not required. The PRI rubric is conjunctive ("address AND phone"). Correct answer = 0. **r1 wrong (scored 1, treating partial = full); r2/r3/2010 right.**
- **A7 (legislative branch register):** §101.70(F) **explicitly excludes** legislators and legislative staff from "legislative agent". Correct = 0. **r3 wrong; r1/r2/2010 right.**
- **D0 (materiality test exists):** §101.70(F)'s "as one of the individual's main purposes" IS a materiality test, just qualitative not quantitative. Correct = 1. **r2/r3 wrong; r1/2010 right.**
- **D1_value/D2_value:** No quantitative threshold exists in OH law. Correct = null. **r2/r3 likely hallucinated values; r1's "unable" is more honest.**

So r2 (the run we picked for SMR projection) is best for 2010-convention continuity but isn't the legally correct reading. **r1 reads the qualitative materiality test correctly but over-scores E-series; r2/r3 read E-series correctly but miss qualitative materiality.** No run is fully correct.

### Reframe 2 (deeper): "the rubric isn't the right product anyway"

Toward end of session: **"the WHOLE POINT of this tool is to ACTUALLY EXTRACT the disclosure filings, so we need to know what's required, right?"**

Right. PRI's rubric asks diagnostic yes/no questions for cross-state comparison. Those answers don't tell a downstream extraction pipeline what fields to expect on a filing. The right shape of the per-state artifact is a **filing schema** — required filing types × fields per filing × cadences × triggering thresholds × cross-references — that an extraction pipeline can consume directly. PRI/FOCAL/Sunlight then become diagnostic *projections* of that schema, not data sources for it.

The compendium-keyed `field_requirements` row IS the right shape (`field_path`, `reporting_party`, `legal_availability`, `legal_citation`, `status`); it's just that the 22 fields populated by PRI projection are a thin slice of what OH's statute actually requires (real_party_in_interest disclosure, itemized expenditure schedules, financial-transaction disclosures, registration card validity through Dec 31 of next even-numbered year, tax-exempt-org member-listing exemption, etc.).

User decision: **don't pivot in this session.** Push the OH 2025 PRI-projection SMR through as a parking-orbit baseline. Future work: one branch on improved extraction (filing-schema-first harness), parallel branch unblocked to start pulling actual disclosures.

## Findings

- **OH disclosure law is structurally near-unchanged 2010 → 2025** as the PRI projection sees it. Real text-level changes exist (casino-control commission added to "person"/"legislative agent" definitions in §101.70; 8 procedural sections grew 15–60%) but they don't move the PRI rubric needle.
- **Inter-run noise is concentrated in known-broken zones** (qualitative materiality, conjunctive E-series questions, C-series public-entity boundary). The 21.3% inter-run rate is high *for OH*, which was "the cleanest" state in the original 5-state calibration.
- **The §101.70 / §121.60 apparent shrinkage was a measurement artifact.** The 2010 Justia page contained both pre-9/10/2010 and post-9/10/2010 versions of those definitions sections inline (~2000 words double-counted across two sections). Real shrinkage is much smaller.
- **The MVP shape works.** End-to-end pipeline (URL list → retrieval → 3-run concurrent dispatch → finalize → consistency → projection → diff doc) executed cleanly in one session, with one orchestrator-args paper-cut (audit-statutes is for cross-state year-availability, not single-state verification — plan's described interface didn't match).

## Decisions

- **Source vintage = 2025**, not 2026 (Justia constraint). Artifact path mirrors source-vintage convention from `("OH", 2010)`.
- **3 concurrent runs**, not 1. Wall-clock 5 min per run; well within safe-batch-size of 4.
- **r2 (`e7846593ebb5`) selected for SMR projection** for 2010-convention continuity, NOT for legal correctness. Diff doc explicitly flags this.
- **No further polishing on this branch.** Future work split into two parallel branches: (1) extraction-harness work (filing-schema-first), (2) actual disclosure-data pulling (unblocked by this MVP SMR existing as a downstream contract).

## Forward signals (not acted on)

- The `governors_office.required: False → True` flip is the only real structural diff and has unclear cause (Ch. 121 legal change vs scorer judgment drift). Worth a 30-min look on the extraction-harness branch.
- The qualitative materiality test (§101.70(F)) is a known scorer blind spot. Filing-schema harness must handle qualitative gates.
- **CA 2025 / TX 2025 baselines** would extend this pattern. Same plan template, same source-vintage labeling. Out of scope here per user — the PRI-projection MVP is parking-orbit, not the production artifact.

## Artifacts

**Committed (this session):**
- `02887ab` — checkpoint: prior session's STATUS/RESEARCH_LOG entries + convo + results doc
- `ee4ffdd` — Add `("OH", 2025)` to LOBBYING_STATUTE_URLS
- `ce10674` — diff doc

**Gitignored (local to worktree):**
- `data/statutes/OH/2025/` — 30-section bundle, ~143 KB
- `data/scores/OH/statute/2025/{26b1ab90b0eb,e7846593ebb5,736087384f85}/` — 3 runs raw + CSV
- `data/state_master_records/OH/2025/e7846593ebb5.json` — final SMR

# Compendium Expansion v2 — Per-Rubric Audit

**Status:** Plan ready. Curation work, not implementation. Output is a durable repo-level audit report that future sessions read instead of re-deriving.

**Originating discussion:** This conversation (2026-04-30). User reframe: "we'll be extracting the data for our consumers, but clearly we can only extract data which is required to be disclosed" — which scopes compendium expansion to *disclosure-side* rubric items only. Prohibitions / penalties / enforcement / cooling-off are out of scope (no filing carries them as data).

**Why this exists as a separate plan from the kickoff:** The current 118-row compendium was unioned from PRI 2010 (disclosure + accessibility), FOCAL 2024, and Sunlight 2015 only. Other consumer-facing rubrics — Opheim 1991, Newmark 2005/2017, CPI Hired Guns 2007, OpenSecrets 2022 — are in `papers/` but were never walked into the compendium. The filing-schema-extraction harness will extract against whatever the compendium defines as the universe; if rows are missing, they'll never be extracted.

**Branch:** `filing-schema-extraction` (this worktree). Audit lands on this branch; final report is intended to migrate to repo-level on merge to main (see "Lifecycle" below).

**Calibration anchor:** None needed — this is curation work over published rubrics, not statute extraction.

---

## The gap this plan closes

Two distinct gaps:

1. **Source-rubric coverage.** The current compendium represents the union of 4 rubrics. Five additional rubrics are in `papers/` with extracted text but not yet walked. Each one may surface compendium rows we haven't enumerated.

2. **Audit durability.** The dedup decisions made during the original Stage A walkthrough (statute-retrieval branch, 2026-04-30 morning) live only in the dedup-map CSV's `notes` column and the convo summaries. Future sessions re-derive these decisions because the rationale isn't discoverable. **Stated user concern: laptop drive crashed; data + context lost; we keep looping on the same questions.** The fix is a repo-level audit report that future sessions read during pre-flight.

---

## Rubrics in scope

All nine are already in `papers/` with extracted text in `papers/text/`. No new paper acquisition needed for this audit.

| # | Rubric | Vintage | File | Already in compendium? |
|---|---|---|---|---|
| 1 | PRI 2010 disclosure | 2010 | `papers/PRI_2010__state_lobbying_disclosure.pdf` | yes (61 rows) |
| 2 | PRI 2010 accessibility | 2010 | (same paper) | yes (22 rows) — **flagged: portal-side, see scope note** |
| 3 | FOCAL 2024 (Lacy-Nichols) | 2024 | `papers/Lacy_Nichols_2024__focal_scoping_review.pdf` | yes (50 indicators) |
| 4 | Sunlight 2015 | 2015 | `papers/Sunlight_2015__state_lobbying_disclosure_scorecard.pdf` + CSV | yes (~8 unique rows) |
| 5 | **Opheim 1991** | 1991 | `papers/Opheim_1991__state_lobby_regulation.pdf` | no |
| 6 | **Newmark 2005** | 2005 | `papers/Newmark_2005__state_lobbying_regulation_measure.pdf` | no |
| 7 | **Newmark 2017** | 2017 | `papers/Newmark_2017__lobbying_regulation_revisited.pdf` | no |
| 8 | **CPI Hired Guns** | 2007 | `papers/CPI_2007__hired_guns_methodology.pdf` | no |
| 9 | **OpenSecrets 2022** | 2022 | `papers/OpenSecrets_2022__state_lobbying_disclosure_scorecard.pdf` | no |

**Rubrics deliberately excluded from this audit:**

- **F Minus** — methodology not in repo; only mentioned in `docs/LANDSCAPE.md`. Add via `add-paper` skill in a follow-up if methodology is published.
- **Common Cause / League of Women Voters / state-level reform-org ratings** — not in repo; methodology heterogeneous. Add later if requested.
- **GAO 2025** — federal LDA compliance audit, not a state-disclosure rubric. Out of scope for the compendium (state-only).
- **Lacy-Nichols 2025** — application of FOCAL 2024 to 28 countries, no new indicators. Subsumed by FOCAL 2024 (already in compendium).
- **LobbyView / Bacik 2025 / Kim 2018, 2025 / LaPira & Thomas 2020** — federal infrastructure papers; not state-disclosure rubrics. Out of scope.
- **Ornstein 2025 / Enamorado 2019 / Libgober 2024** — entity-resolution methodology; not rubrics. Out of scope.

**Accessibility / portal-side note:** PRI 2010 accessibility (22 rows already in compendium) is portal-evidence not statute-evidence; it's in the compendium for completeness but is NOT extracted by the filing-schema harness. The audit walks any accessibility-flagged rubric items into the compendium with `domain="accessibility"` (existing convention) and tags them out-of-scope for the harness. Sunlight's "Form Accessibility" + OpenSecrets's "Public Accessibility" + CPI's "Public Access" + FOCAL's "transparency" indicators all fall into this bucket.

---

## What "out of scope" means concretely

Per the conversation reframe: the compendium catalogs items the project will *extract from disclosure filings*. An item is **in scope** if a state law could plausibly require it to be disclosed and a downstream filing could carry it as a data field. An item is **out of scope** if:

- It's a **prohibition** (e.g., "campaign contributions during session banned") — no filing carries this; statutory rule, not disclosure data.
- It's a **penalty** (e.g., "felony class B" / "max fine $10k") — no filing.
- It's an **enforcement metric** (e.g., "agency conducts audits") — no filing of audit-events as data.
- It's a **revolving-door restriction** (e.g., "2-year cooling-off period") — *unless* the state requires post-employment disclosure filings, in which case those filings' fields are in scope.
- It's a **statute structural feature** (e.g., "lobbying definition includes administrative agency lobbying") — this determines *who must file*, not *what they file*. Borderline; see below.

**Borderline: definition-trigger criteria.** Newmark/Opheim's "is there a compensation standard / expenditure standard / time standard *in the definition* of lobbying" is a structural feature of the statute, not a disclosure field. BUT it determines which filings exist and who has to file, which is structurally relevant to the harness. **Decision: include these as compendium rows with `domain="definitions"` (new domain value)**, marked as harness-relevant context. They populate the SMR with `status` indicating whether the state's statutory definition includes that trigger; they don't populate downstream filing field schemas.

This is the only `domain` expansion in scope for this plan. Prohibitions / penalties / enforcement / revolving-door domains are NOT added.

---

## Audit procedure

For each of the 5 unwalked rubrics (Opheim, Newmark 2005, Newmark 2017, CPI Hired Guns, OpenSecrets 2022):

1. **Read the paper text** at `papers/text/<paper>.txt`. Identify the rubric's atomic items — the smallest yes/no or scored unit (e.g., Newmark 2005's 17 binary items).
2. **Walk each item** and tag with one of:
   - `EXISTS` — already covered by an existing compendium row. Action: add a new `FrameworkReference` to that row in `framework_references_json`. Record the dedup decision in `framework_dedup_map.csv`.
   - `NEW` — disclosure-side concept not in compendium. Action: add a new compendium row. Decide `domain` (registration/reporting/accessibility/definitions/financial), `data_type`, `description`, `framework_references_json`. Record in dedup map with `target_expression="NEW"`.
   - `OUT_OF_SCOPE` — prohibition, penalty, enforcement, revolving-door restriction, etc. Action: do NOT add to compendium. Record in dedup map with `target_expression="OUT_OF_SCOPE"` and `notes` giving the reason.
   - `MERGE` — the rubric item subsumes 2+ existing compendium rows (rubric is coarser than compendium). Action: add `FrameworkReference` to each underlying compendium row. Record dedup decision as a boolean expression (e.g., `"PRI:E1g_i | PRI:E1g_ii"`).
3. **Write the rubric's audit section** in the final report (see "Final report" below). Each item gets one row in a table.

PRI 2010 (disclosure + accessibility), FOCAL 2024, Sunlight 2015 don't need re-walking — their dedup-map entries already exist. The audit verifies the existing entries pass tests and writes their summary sections of the final report from existing data.

**Order of walkthrough:** Newmark 2017 → Newmark 2005 → Opheim 1991 → CPI Hired Guns → OpenSecrets 2022. Newmark 2017 first because it's the most recent + most-cited and was built from primary-source statute review (most likely to surface real new rows). Opheim 1991 last because it's the oldest + smallest; most items will likely fold into existing rows.

---

## Deliverables

1. **Updated `data/compendium/disclosure_items.csv`** — current 118 rows, plus N new rows from the audit (estimated 10–30 new rows; mostly Newmark 2017 + CPI Hired Guns; OpenSecrets is mostly accessibility-side which folds into existing rows).
2. **Updated `data/compendium/framework_dedup_map.csv`** — current 141 entries, plus one new entry per rubric item walked (estimated +60–100 entries: Opheim 22, Newmark 2005 17, Newmark 2017 19, CPI 48, OpenSecrets ~20). Each new entry has `source_framework`, `source_item_id`, `target_expression` (compendium row id, boolean expression, `NEW`, or `OUT_OF_SCOPE`), and `notes` (the curation rationale).
3. **Final report: `docs/COMPENDIUM_AUDIT.md`** at repo root level (lifecycle: born on this branch in `docs/active/filing-schema-extraction/results/20260430_compendium_audit.md`; on branch merge moves to `docs/COMPENDIUM_AUDIT.md` so it's discoverable as repo-level documentation, not buried in branch history).
4. **Test additions in `tests/test_compendium.py`** — `test_loaded_real_compendium_includes_all_<rubric>_items` for each newly walked rubric (catches future curation drops).
5. **STATUS.md update** — add a one-liner pointing to `docs/COMPENDIUM_AUDIT.md` so future pre-flight reads surface this without re-deriving.

---

## Final report structure (`docs/COMPENDIUM_AUDIT.md`)

This is the load-bearing artifact. **Goal: any future agent or fellow can read this once and understand what the compendium contains, why each item is or isn't there, and what was deliberately excluded.** Designed to be the answer to "wait, why isn't X in the compendium?" without rerunning the audit.

Structure:

```markdown
# Compendium Audit Report

**Compendium version:** v<N> (commit <sha>)
**Audit date:** 2026-04-30
**Audit scope:** <state of compendium pre-audit> → <state post-audit>

## Summary
- <X> compendium rows, deduped from <Y> source-rubric items across <Z> rubrics
- <N> rows added in this audit
- <M> rubric items walked and excluded with reason

## Rubrics walked (in order)

### <rubric name> (<vintage>)
**Source:** `papers/<file>`
**Item count:** <N>
**Items added as new rows:** <M>
**Items folded into existing rows:** <K>
**Items excluded:** <L> (see "Excluded items" below)

| Rubric item id | Description | Disposition | Compendium row(s) | Rationale |
|---|---|---|---|---|
| <id> | <one-liner> | EXISTS / NEW / OUT_OF_SCOPE / MERGE | <row id or expression> | <why> |
| ... | | | | |

### <next rubric>
...

## Excluded items (cumulative across all rubrics)

| Rubric | Item | Exclusion reason | Notes |
|---|---|---|---|
| Newmark 2005 | "campaign contribs banned during session" | prohibition | Not a disclosure field; statutory rule. |
| ... | | | |

## Rubrics deliberately not walked

- **F Minus** — methodology not in repo. Add via `add-paper` if/when methodology is published.
- **Common Cause** — not in repo. Add later if requested.
- ... (full list with reason for each)

## Coverage matrix

(Compendium row × rubric — which rubrics flag each row. Generated programmatically from `framework_dedup_map.csv`. Useful for "which rubrics has anyone ever cared about field X?" lookups.)

## Decision log

For non-obvious dedup judgments, record the decision and rationale here so future sessions don't re-litigate:

- **Decision:** Newmark 2005 "expenditure standard in definition" → MERGE into PRI D1 (registration threshold). **Rationale:** Both refer to the dollar-value trigger for triggering registration as a lobbyist. **Alternative considered:** NEW row for "definition-side trigger" separate from "registration threshold." **Why rejected:** Same statutory mechanism; splitting would force every state to populate both rows identically.
- ... (one entry per non-obvious call)

## Lifecycle

- Born on branch `filing-schema-extraction` in `docs/active/filing-schema-extraction/results/20260430_compendium_audit.md`.
- On branch merge: moved to repo-level `docs/COMPENDIUM_AUDIT.md`.
- Updated whenever the compendium is changed (new rubric walked, row added, dedup decision revised). Bump the version line at top.
```

The Decision Log section is the explicit anti-loop mechanism: every contested call from this audit becomes a stable record so we don't re-debate it next time.

---

## Out of scope (deliberate, this plan)

- **Schema changes (data-model-v1.2).** Plan is curation against existing schema. The only schema-adjacent change is potentially a new `domain="definitions"` enum value on `CompendiumItem.domain` if that field has fixed values (verify during audit). If fixed, propose v1.2 in a separate plan.
- **Filing-schema extraction harness design.** That's the kickoff plan (`20260430_filing_schema_extraction_kickoff.md`). This plan is upstream of it: define the universe, then design the harness that extracts against it.
- **State-by-state SMR population.** OH-first comes after the harness design.
- **Adding F Minus / Common Cause / OpenSecrets-state-pages methodology.** Possible follow-up audit; not this one.
- **Re-walking PRI 2010 / FOCAL 2024 / Sunlight 2015.** Their dedup decisions stand. Audit verifies them (test-coverage check) but does not re-curate.
- **Verifying dedup-map source-frame counts** — separate verification (deferred): does `framework_dedup_map.csv` have exactly the right number of entries per rubric (PRI 61+22, FOCAL 50, Sunlight ~8)? A test in `tests/test_compendium.py` would catch this; add as part of test additions.

---

## Estimated effort

- **Reading + walking 5 rubrics:** half-day to full day. Newmark 2017 + CPI are the heavy ones (~50–70 atomic items combined); the others are 17–22 each.
- **Curation: writing the dedup-map entries + new compendium rows:** half-day. Most items fold into existing rows; new rows are fewer than the item count.
- **Final report draft:** half-day. The decision log section grows with the audit; tabular sections come from the dedup-map CSV.
- **Tests + STATUS update + commits:** quarter-day.

**Total: 1.5–2 days.** Committable in a single session if focused.

---

## Pre-flight reads for the implementing agent

1. This plan.
2. `data/compendium/disclosure_items.csv` — the current 118-row compendium.
3. `data/compendium/framework_dedup_map.csv` — current 141-row dedup audit trail.
4. `src/lobby_analysis/models/compendium.py` — `CompendiumItem` schema (especially `domain` field's allowed values).
5. `papers/text/Opheim_1991__state_lobby_regulation.txt`
6. `papers/text/Newmark_2005__state_lobbying_regulation_measure.txt`
7. `papers/text/Newmark_2017__lobbying_regulation_revisited.txt`
8. `papers/text/CPI_2007__hired_guns_methodology.txt`
9. `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt`
10. `docs/historical/statute-retrieval/plans/20260430_compendium_population_and_smr_fill.md` — original Stage A plan for context on dedup conventions.
11. `docs/historical/statute-retrieval/convos/20260429_sunlight_pri_item_level_calibration.md` — convo where the compendium-as-universe framing landed.

---

## Confidence

- **High** that the audit closes a real gap. (The 5 rubrics are in `papers/` and have never been walked into the compendium; this is verified, not assumed.)
- **High** that disclosure-only scoping is correct per the originating reframe. Prohibitions/penalties have no filing field shape; including them wastes harness budget.
- **High** that the final report design reduces re-litigation. Decision log + excluded-items table + coverage matrix together answer the "wait, why?" questions that surface in every cross-session re-discovery.
- **Medium** on row-count estimate (10–30 new rows). Could be lower if rubrics overlap heavily; could be higher if CPI's 48 items surface unexpected fields.
- **Medium** on the "definitions" domain decision. Borderline-in-scope; could argue for fully out-of-scope and folding into `notes` on existing rows. Decide during walkthrough; document the call in the report.
- **Lower** on whether the OpenSecrets-state-page-by-state methodology (per-state evaluations underlying the 2022 scorecard) is in `papers/OpenSecrets_2022__state_lobbying_disclosure_scorecard.pdf` or only in their live web app. If only on the web app, the rubric items are abstracted; the actual evaluations are not. Flag during reading.

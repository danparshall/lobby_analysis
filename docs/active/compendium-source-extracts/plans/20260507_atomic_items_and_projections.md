# Atomic-item audit + projection mappings (disclosure-first prototype) — Implementation Plan

**Goal:** For the working set of source rubrics, (a) confirm every rubric has atomic-level items we can extract — drop any rubric that doesn't — and (b) build per-rubric projection functions `f_rubric(compendium_cells, vintage) → rubric_score` for the disclosure-side items, validated against existing published prior data. This unlocks the Ralph-loop extraction-prompt iteration that comes after.

**Originating conversation:** [`docs/active/compendium-source-extracts/convos/20260507_3way_consensus_execution_and_cpi_addition.md`](../convos/20260507_3way_consensus_execution_and_cpi_addition.md)

**Context:** The 2026-05-07 session produced two load-bearing artifacts: the 3-way × 3-run consensus output (24 strict / 39 loose / 468 human-review pairs over 252 USA-tradition items) and the CPI 2015 C11 fold-in showing that the v1.1 schema's two-axis design accommodates de jure / de facto rubric items natively. From that came the **compendium 2.0 success criterion** (see top of `STATUS.md`): ONE compendium + ONE extraction pipeline + multi-year reliability + source rubrics as SANITY CHECKS on extraction accuracy via per-rubric projection functions validated against published prior data. This plan operationalizes the next concrete steps under that criterion.

**Confidence:** High on the success criterion itself ("feels right and unlikely to change", per user 2026-05-07). Medium on the rubric-set membership (Phase A may drop 1-3 rubrics if atomic items don't exist; that's expected behavior, not failure). Medium on projection mappings being correctly chosen (Phase B will surface ambiguities; iterate before locking).

**Architecture:** Top-down — work backward from each rubric's atomic-item scoring rules to derive (a) what cells the projection needs to read and (b) what the rubric's score-aggregation logic is. The compendium row set falls out as a byproduct; we don't pre-commit to row structure. Disclosure-only for this round; prohibitions / enforcement / personnel rows deferred. After Phase C validates projections against published prior data, the extraction prompt design (separate plan) iterates against well-defined targets.

**Branch:** `compendium-source-extracts` (existing worktree at `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts`).

**Tech Stack:** Python 3.12, pandas. No new dependencies expected. Worktree-local venv (`unset VIRTUAL_ENV && uv run …` per `feedback_pytest_in_worktree.md` memory).

---

## Working rubric set for this round

Not the absolute final set; this is the round-N set. New rubrics can join later without invalidating prior projection work.

**Currently in our extracted corpus** (for reference; Phase A audits the thin three):

| rubric | items | published per-state ground truth | atomic-item status |
|---|---:|---|---|
| HiredGuns 2007 | 47 | yes — CPI's predecessor scoring, 50 states | atomic, OK |
| FOCAL 2024 | 50 | no per-state scores (rubric is a checklist; not yet scored at scale) | atomic, OK |
| Newmark 2017 | 19 | yes — 50 states | atomic, OK |
| Newmark 2005 | 18 | yes — 50 states | atomic, OK |
| Opheim 1991 | 22 | yes — limited states (BoS Tables 28-32 for the 1990 vintage) | atomic, OK |
| PRI 2010 | 83 | yes — 50 states, transcribed in `docs/historical/pri-2026-rescore/` | atomic, OK |
| CPI 2015 C11 | 14 | yes — 50 states, `papers/CPI_2015__sii_scores.csv` | atomic, OK (added 2026-05-07) |
| OpenSecrets 2022 | 7 | partial — scorecard published but coverage uneven | **THIN — Phase A audit needed** |
| Sunlight 2015 | 5 | yes — `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` (50 states) | **THIN — Phase A audit needed** |
| **LobbyView (Kim 2018/2025)** | unknown | n/a (LobbyView is federal-only data infrastructure, not state-scored; treated as "rubric" in the sense that LobbyView's schema fields are questions a state-level data layer should also answer) | **NEW — Phase A audit needed** |

The "drop rule" per user direction: any rubric where atomic items don't exist after a reasonable effort is **excluded from the contributing-rubric set** — by definition, you can't use a rubric for compendium construction if you can't read its atomic questions.

## Scope qualifier (disclosure-first)

For this round, **only disclosure-side items** are processed in Phase B and Phase C. This roughly halves the work and matches Track B fellows' immediate downstream need (the data they're pulling out of state portals is disclosure data; rubric items asking about prohibitions, gift bans, contingent-fee bans, revolving-door rules, enforcement penalty schedules, etc. are deferred).

Disclosure-side items (rough scope, by rubric):

- HiredGuns Q1-Q38 + accessibility-related Q49-Q56 (Q39-Q47 enforcement = deferred; Q48 cooling-off = deferred)
- FOCAL all `financials.*` / `descriptors.*` / `contact_log.*` / `openness.*` / `relationships.*` / `scope.*` / `timeliness.*` (some `personnel.*` deferred per item)
- Newmark all `def_*_lobbying`, `def_*_standard`, `disc_*` (the `prohib_*` battery deferred)
- Opheim all `def.*` / `disclosure.*` (the `enforce.*` battery deferred)
- PRI 2010 all `disclosure.A*`, `disclosure.E1*`, `disclosure.E2*`, `accessibility.Q*`
- CPI 2015 C11 all 14 (entirely disclosure / monitoring of disclosure)
- OpenSecrets all 7 (currently entirely disclosure-framed, pending audit)
- Sunlight all 5 (currently entirely disclosure-framed, pending audit)
- LobbyView all schema fields (federal LDA fields are entirely disclosure / filing-content)

Final disclosure-side scope solidifies during Phase B.

---

## Phases

### Phase A — Atomic-item audit (3 rubrics)

For each of OpenSecrets, LobbyView, Sunlight 2015, the test is: do atomic-level items exist in the source publication? If yes, extract them in standard schema. If no, document and drop the rubric.

#### Phase A1 — OpenSecrets atomic-item audit

**What it is:** OpenSecrets's 2022 state-lobbying scorecard (the report acknowledging the 19-state data gap). Currently 7 items in `results/items_OpenSecrets.tsv` that look like headline categories.

**Where the data lives:** OpenSecrets's website, possibly the published 2022 scorecard PDF/article. URL hint: `opensecrets.org/state-lobbying` or similar. Scorecard methodology may be on a separate methodology page.

**Steps:**
1. Read the existing `results/items_OpenSecrets.tsv` and `results/items_OpenSecrets.md`. Note the 7 items currently captured.
2. Web search for "OpenSecrets state lobbying scorecard 2022 methodology" + "OpenSecrets state lobbying scorecard atomic indicators". Locate the scorecard methodology document.
3. If a methodology document exists with sub-questions per category: extract atomic items. Update `items_OpenSecrets.tsv` (or create `items_OpenSecrets_atomic.tsv` if there's a meaningful structural distinction).
4. If the methodology only has the 7 headline categories with no atomic decomposition: **drop OpenSecrets** from the contributing-rubric set. Document in a `results/20260507_opensecrets_atomic_audit.md` note explaining why.

**Stop condition:** Atomic items captured OR rubric documented as dropped. The user expects atomic items to exist; would be surprised by the drop case.

#### Phase A2 — LobbyView schema audit (Kim 2018 / 2025)

**What it is:** LobbyView is federal LDA-filing infrastructure (Kim 2018 introducing the database; Kim 2025 update). Treated as a "rubric" by virtue of the project framing ("LobbyView for 50 states") — the schema fields LobbyView captures define questions our state-level compendium should also answer. We don't have to literally adopt their schema, but the elements very probably belong in compendium.

**Where the data lives:** `papers/Kim_2018__lobbyview.pdf`, possibly `papers/Kim_2025__lobbyview_*` if present. LobbyView website (`lobbyview.org`) likely has schema documentation. The Kim 2018 paper Table 1-2 should describe schema.

**Steps:**
1. Read `papers/text/Kim_2018*.txt` (if extracted) or open the PDF. Find Table 1 / Table 2 / methodology section listing the schema fields.
2. Check for `papers/Kim_2025*` — if present, read for schema updates.
3. (Optional, if paper schema is incomplete) Web fetch `lobbyview.org` documentation page — verify schema fields enumerate consistently.
4. Build `results/items_LobbyView.tsv` with schema fields as atomic items. Use field name as `indicator_id`, field description as `indicator_text`, type/format as `scoring_rule`. Source quote = the table caption or paper section reference.
5. Companion `results/items_LobbyView.md` explaining how LobbyView's federal schema is being mapped to "rubric items" for state compendium construction (i.e., these aren't questions LobbyView asks; they're fields LobbyView captures, treated as questions about whether state-level disclosure data captures the same fields).

**Stop condition:** Schema fields captured (likely 20-50 fields). Drop case unlikely — LobbyView is well-documented infrastructure; if for some reason the schema can't be enumerated cleanly, document and drop.

#### Phase A3 — Sunlight Foundation 2015 atomic-item audit

**What it is:** Sunlight's "How transparent is your state's lobbying disclosure?" 2015 scorecard. Currently 5 items in `results/items_Sunlight.tsv` that are headline categories with mixed scoring scales (4-tier on some, 5-tier on others, 2-tier on others).

**Where the data lives:** Sunlight's article (`sunlightfoundation.com/2015/08/12/how-transparent-is-your-states-lobbying-disclosure/` — search result from session). Per-state data CSV at `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`.

**Steps:**
1. Read existing `results/items_Sunlight.tsv` and `.md`. Note the 5 categories and their per-state scores in the CSV.
2. Read `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv` — does it have per-category sub-questions, or only the 5 top-level scores per state?
3. If the CSV columns expose sub-questions: extract atomic items from those columns. The 4-tier / 5-tier / 2-tier scoring is exactly the per-item-scoring-rule we need.
4. If the article + CSV only expose the 5 headline categories: **drop Sunlight 2015** from the contributing-rubric set. Document in `results/20260507_sunlight_atomic_audit.md`.

**Stop condition:** Atomic items captured OR rubric dropped.

#### Phase A — done condition

Three rubrics audited. For each: either (a) atomic items captured in `items_<Rubric>.tsv` (or `_atomic.tsv` if structurally distinct) + companion `.md`, or (b) drop reason documented in `results/20260507_<rubric>_atomic_audit.md`.

After Phase A, the contributing-rubric set for Phase B is the survivors.

### Phase B — Projection mappings (disclosure-first)

For each surviving rubric, walk every disclosure-side atomic item. For each item, write down:

- `compendium_row(s)` — which canonical row(s) in compendium 2.0 the projection needs to read. Reference 3-way consensus output (`results/3way_consensus/consensus_clusters_strict.csv` + `consensus_clusters_loose.csv`) by `cluster_id` where applicable; for items not in consensus output, propose a candidate row name.
- `cell_type` — binary (yes/no), enum (e.g., {monthly, quarterly, semi-annual, annual}), typed value (dollar amount, day-count, list of role-names, etc.). If any rubric reads a value, the cell carries the value.
- `axis` — `legal_availability` or `practical_availability` (per v1.1 schema).
- `scoring_rule` — the function from cell value to per-item rubric score, taken from the rubric's scoring rule (already in `scoring_rule` column of `items_<Rubric>.tsv`).
- `aggregation_rule` — how per-item scores roll up to per-state rubric score (often the rubric paper specifies; PRI's is in the paper §III-IV, CPI's is "1-100 per question, aggregated to category letter grade", etc.).

#### Phase B per-rubric output

One file per rubric: `results/projections/<rubric>_projection_mapping.md`. Long-format markdown with sections per atomic item.

Suggested per-item structure:

```markdown
### <rubric_item_id>: <indicator_text>

- **Compendium rows:** `<row_id_1>`, `<row_id_2>` (or "NEW: <proposed name>" if not in consensus output)
- **Cell type:** binary | enum {a,b,c} | typed: <type>
- **Axis:** legal_availability | practical_availability
- **Scoring rule:** <function from cell value(s) to per-item score, paraphrased from rubric>
- **Source quote:** <copied verbatim from items_<Rubric>.tsv source_quote column>
```

#### Phase B — done condition

Per-rubric projection-mapping docs exist for each surviving rubric. The disclosure-side compendium ITEM set falls out as the union of `compendium_rows` across all mappings (de-duplicated). Save that as `results/projections/disclosure_side_compendium_items_v1.tsv`.

### Phase C — Projection function implementation + validation

For each rubric with a Phase-B mapping doc, implement the projection function in code:

```
src/lobby_analysis/projections/<rubric>.py  (or similar)

def project_<rubric>(compendium_cells: dict, vintage: int) -> RubricScore:
    """Map populated compendium cells to <rubric>'s per-state-vintage score."""
    ...
```

Where `compendium_cells` is a dict-like keyed by `(canonical_row_id, axis)` → cell value (typed appropriately).

#### Phase C steps per rubric

1. Implement `project_<rubric>` from the Phase-B mapping doc.
2. Write **unit tests** with synthetic cell values that exercise each per-item scoring branch + the aggregation rule. Tests verify projection LOGIC, not extraction. (See Testing Plan below.)
3. Build a small **integration test fixture**: hand-populate compendium cells for ONE state in the rubric's vintage. Hand-population is acceptable here; this is debug scaffolding for the projection, not the operational pipeline. For OH 2010, populate cells from PRI 2010's published per-item answers for OH (which give us cell-equivalent values directly); for OH 2015, populate from CPI 2015's published per-item answers. The hand-populated cells are correct-by-construction relative to the source rubric being tested.
4. Run the projection on hand-populated cells. Compare output to the rubric's published per-state aggregate score for that state-vintage. Match within tolerance ⇒ projection is sound.
5. Add **cross-rubric validation**: same hand-populated cells, run a different rubric's projection, compare to that rubric's published score. Cross-validates that the cells are consistent across rubrics' interpretations. This is the "redundant per-row ground truth" check.

#### Phase C suggested order

Smallest validation set first:

1. **CPI 2015 C11** (14 items × 50 published per-state scores × 1 vintage) — simplest projection logic (5 sub-categories with 100/50/0 scoring rules), tightest published ground truth.
2. **Sunlight 2015** (5 items × 50 states × 1 vintage) — IF Phase A1 found atomic items.
3. **OpenSecrets 2022** — IF Phase A1 found atomic items.
4. **Newmark 2017** (19 items × 50 states × 1 vintage).
5. **Newmark 2005** (18 items × 50 states × 1 vintage).
6. **Opheim 1991** (22 items × limited states × 1991 vintage).
7. **HiredGuns 2007** (47 items × 50 states × 1 vintage).
8. **PRI 2010** (83 items × 50 states × 1 vintage) — most items, hardest aggregation rule.
9. **FOCAL 2024** — checklist, not scored at scale; projection produces an indicator-coverage summary, not a single score. May not have published ground truth at the per-state level; deprioritized.
10. **LobbyView** — schema-coverage check rather than score projection. Different shape; tackled separately.

#### Phase C — done condition

Per-rubric projection function implemented + unit-tested + integration-tested for one (state, vintage) sample. Cross-rubric validation passes for at least one shared row.

---

## Testing Plan

I will write unit tests in `tests/test_projections.py` (or per-rubric files like `tests/test_projection_cpi_2015.py`).

**Per-rubric unit tests** verify projection LOGIC:
- For each rubric atomic item, a test case feeding synthetic cell values and asserting the per-item score the projection computes matches the rubric's scoring rule.
- For each rubric's aggregation, a test case computing per-state aggregate from synthetic per-item scores and asserting it matches the rubric's published aggregation rule.

**Per-rubric integration tests** verify projection AGAINST PUBLISHED PRIOR DATA:
- One test per rubric per available (state, vintage). Hand-populates compendium cells from the rubric's published per-item answers (which are correct-by-construction for that rubric). Runs the projection. Asserts the projection output equals the rubric's published per-state aggregate score for that (state, vintage), within rubric-specific tolerance.

**Cross-rubric integration tests** verify per-row ground truth REDUNDANCY:
- For shared rows (e.g., "expenditures benefitting officials" is in Newmark2005 + Newmark2017 + Opheim + FOCAL.financials.10), populate the cell once and verify all four rubric projections produce their respective correct outputs. Inconsistency surfaces row-design or projection-logic bugs.

NOTE: I will write *all* tests before I add any implementation behavior.

The tests test BEHAVIOR (does the projection produce the right rubric score given the right cells) — not implementation, not mocks, not data structures.

---

## Edge cases / known gotchas

- **Hand-population vs operational pipeline.** Phase C uses hand-populated cells only as test scaffolding for projection-logic validation. The operational pipeline (Phase D, separate plan) populates cells via extraction. Hand-population is one-off; do not let it leak into operational code.
- **Published per-state data is sometimes per-state aggregate only (not per-item).** PRI 2010 gives us per-item per-state (transcribed in `docs/historical/pri-2026-rescore/`). CPI 2015 gives us per-state aggregate + the 14 atomic indicators; per-item per-state may need to be back-derived. Sunlight 2015's CSV may or may not expose per-item; Phase A3 surfaces this.
- **FOCAL 2024 has no published per-state scoring.** It's a checklist for transparency assessment, not a scorecard. Projection may produce an "indicator coverage map" rather than a single score. Deprioritized in Phase C order.
- **LobbyView is shaped differently.** It's a database schema, not a yes/no rubric. The "projection" for LobbyView is more like "does our compendium have rows covering each LobbyView field?" — a schema-coverage check, not a score computation. Worth implementing but as a separate shape.
- **Rubric atomic items may use different units across rubrics.** Newmark expects a binary, PRI expects a yes/no with paper-derived rollup, CPI expects 100/50/0. Compendium cells must capture enough information for ALL projections to compute. Where rubrics disagree on granularity, the compendium cell should carry the finer-grained value; coarser projections aggregate.
- **3-way consensus output is a starting point, not a contract.** Rows that show up in projection mappings but not in consensus output should be ADDED to compendium 2.0; rows that show up in consensus but no projection reads should be flagged "keep / delete?" for separate decision (per the success criterion's minimum-compendium goal).
- **Drop decisions are reversible.** If Phase A drops a rubric (e.g., OpenSecrets if no atomic items), and a future paper or methodology page surfaces atomic items, the rubric can be re-added.

---

## Implementation Details (≤10 bullets)

- Phase A artifacts go in `results/` at the worktree root: `items_<Rubric>_atomic.tsv` (or update existing `items_<Rubric>.tsv`), companion `.md`, audit notes at `results/20260507_<rubric>_atomic_audit.md`.
- Phase B artifacts go in `results/projections/`: per-rubric `<rubric>_projection_mapping.md` + the union `disclosure_side_compendium_items_v1.tsv`.
- Phase C code goes in `src/lobby_analysis/projections/<rubric>.py` (or whatever fits the existing src layout — verify). Tests in `tests/`.
- Worktree-local venv: `unset VIRTUAL_ENV && uv sync` if not already.
- `git add` specific files; never `git add .` or `-A` (per CLAUDE.md).
- Don't merge to main; don't open a PR; don't write to other branches' STATUS.md rows.
- Phase A is exploratory (web fetch + manual judgment), no TDD needed. Phase B is also analytical, no TDD. Phase C is code; full TDD per `test-driven-development` skill.
- Existing PRI projection in `cmd_build_smr` (statute-retrieval branch, archived) is a structurally different shape (compendium 1.x PRI-shaped) — do NOT use as a template; it's the architecture we're moving away from.

---

## What could change

- **The rubric set** — current 9 + CPI 2015 + LobbyView is a working set, not the absolute final set. Adding rubrics (e.g., the 16 untracked international/EU papers, TI-UK, CII methodology, Roth thesis, Chari et al. books, CDoH 7-framework corpus) doesn't invalidate prior projection work; new rubrics get their own projections layered on.
- **The disclosure-only scope** — confirmed for this round per user direction. Once disclosure-side prototype is solid, expand to prohibitions / enforcement / personnel / itemization-granularity.
- **The cell-type schema** — Phase B will surface places where binary cells are insufficient and typed values are required. The schema may need a v1.6 or v2.0 bump to support new typed-value cell types. Coordinate with the v1.1 / v1.2 / v1.3 history (live in `src/lobby_analysis/models/`).
- **The integration-test scaffolding** (hand-population for projection validation) is a stop-gap. Once Phase D extraction pipeline (separate plan) lands, integration tests run end-to-end from extraction → projection → published-data comparison.
- **OpenSecrets / Sunlight may drop.** If atomic items don't exist, the contributing-rubric set shrinks. Plan adjusts in Phase B accordingly.

---

## Questions

1. **Phase C order — is CPI 2015 C11 first the right call?** It's the smallest concrete target with cleanest published ground truth (50-state × 14-item), but it's also the most recent rubric — projecting it well doesn't necessarily generalize to older rubrics with different scoring conventions. Alternative: start with PRI 2010 (largest, most-studied, per-item per-state ground truth available) to stress-test the projection architecture earlier.
2. **Hand-population scaffolding — where does it live in code?** Suggest `tests/fixtures/projection_inputs/<rubric>_<state>_<vintage>.json` so it's discoverable and re-usable. Confirm or override.
3. **`src/lobby_analysis/projections/` directory creation** — confirm this layout, or use a different module path. Verify against the existing `src/lobby_analysis/models/` structure when implementing.
4. **FOCAL 2024 — projection or schema-coverage check?** Treating FOCAL as a checklist (no per-state score, just an indicator-coverage map) is one option; treating it as score-able by counting "yes" indicators per state is another. User decision needed before Phase C9.
5. **LobbyView scope — federal schema only, or include state lobbying databases like LobbyView's public profiles?** Plan currently scopes to federal LDA schema (Kim 2018). State-level extensions (where LobbyView aggregates state portals) might also be relevant. Confirm Phase A2 scope.

---

## Out of scope for this plan

- Extraction prompt design / Ralph-loop iteration (separate plan after this one lands).
- Practical_availability portal-extraction work (other fellow's Track B).
- Compendium minimization (deletion of rubric-uncovered rows) — runs after all projections exist.
- Schema migration to v1.6 / v2.0 if needed (separate plan).
- Multi-state / 50-state scaling (after single-state validation passes).

---

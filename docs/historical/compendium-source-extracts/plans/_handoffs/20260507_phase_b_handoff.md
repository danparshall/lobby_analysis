# Phase B handoff — what changed during Phase A

**Originating plan:** [`../20260507_atomic_items_and_projections.md`](../20260507_atomic_items_and_projections.md)
**Originating convo (Phase A execution):** [`../../convos/20260507_atomic_item_audits_and_focal_supplement.md`](../../convos/20260507_atomic_item_audits_and_focal_supplement.md) (this is the convo that produced this handoff; you are reading its end-state)
**Date:** 2026-05-07 (pm)
**Audience:** the Phase B implementing agent — who has zero memory of the Phase A session.

---

## Why this handoff exists

The plan was written before Phase A executed. Phase A (atomic-item audits A1-A4 + the L-N 2025 supplementary file extraction) shifted multiple inputs and locked several decisions the plan left open. Reading the plan alone, you would re-discover all of these from the audit notes — that's a 30-60 min tax. This doc captures the shifts upfront so you start Phase B with the locked state in hand.

**Read this first, then the plan**, not the other way around. The plan's substance (per-rubric mapping methodology, per-item structure, Phase B done condition) is unchanged; only the *inputs* and *scope* shifted.

---

## What's locked

### Contributing-rubric set (post-Phase A)

| Rubric | Items in scope | Source TSV | Notes |
|---|---:|---|---|
| HiredGuns 2007 | 47 | `results/items_HiredGuns.tsv` | All disclosure-side per plan |
| FOCAL 2024 | 50 | `results/items_FOCAL.tsv` | Verbatim weights from L-N 2025 Suppl File 1 |
| Newmark 2017 | 19 | `results/items_Newmark2017.tsv` | Disclosure-side |
| Newmark 2005 | 18 | `results/items_Newmark2005.tsv` | Disclosure-side |
| Opheim 1991 | 22 | `results/items_Opheim.tsv` | Disclosure-side |
| PRI 2010 | 83 | `results/items_PRI_2010.tsv` | All disclosure + accessibility |
| CPI 2015 C11 | 14 | `results/items_CPI_2015_lobbying.tsv` | 6 de jure + 8 de facto |
| OpenSecrets 2022 | 4 cats | `results/items_OpenSecrets.tsv` | Cat 1 binary, Cats 2/3 few-shot, Cat 4 decomposed |
| **Sunlight 2015** | **4 of 5** | `results/items_Sunlight.tsv` | Item 4 (Doc Accessibility) excluded — see audit |
| LobbyView | 46 schema fields | `results/items_LobbyView.tsv` | **Different shape** — schema-coverage rubric, not score-projection. See per-rubric notes. |

Total: 9 score-projection rubrics + 1 schema-coverage rubric.

### Phase C order (locked 2026-05-07)

1. **CPI 2015 C11** first — smallest concrete target (14 items × 50 states), tightest published ground truth.
2. **PRI 2010** second — largest, hardest aggregation, stress-tests the projection architecture early enough to catch shape issues.
3. The plan's remaining order (Sunlight, OpenSecrets, Newmark 2017/2005, Opheim, HiredGuns, FOCAL, LobbyView) is unchanged. Phase B mapping order should mirror this.

### Phase C scaffolding paths (locked)

- Hand-population fixtures: `tests/fixtures/projection_inputs/<rubric>_<state>_<vintage>.json`
- Code modules: `src/lobby_analysis/projections/<rubric>.py`
- Tests: `tests/test_projection_<rubric>.py` (or `tests/test_projections.py` if shared)

Verify these against the existing `src/lobby_analysis/models/` layout when you land Phase C; this is the directionally-confirmed plan, not yet a code-confirmed layout.

---

## Per-rubric scope adjustments since the plan

### Sunlight 2015 — item 4 excluded at projection layer

The plan asked Phase A3 to decide drop-or-keep for the whole rubric. Outcome: **keep, minus item 4**.

- Items 1, 2, 3, 5 enter Phase B. Each cleanly decomposes into 1-2 underlying compendium cells; tier-from-cells function is deterministic.
- Item 4 (Document Accessibility, 5-tier -2..2) is **excluded from projection mapping** because its 5-tier ordinal conflates 3-4 sub-features (digital filing, registration form online, expenditure form online, blank forms online) and the -1/-2 distinction is documented as a near-typo in the source. The function from cells to tier is not well-defined.
- **`items_Sunlight.tsv` is left intact** — item 4 is still in the verbatim per-paper extract because that file is a source-extract, not a projection-input. The exclusion is at the projection layer only. Phase B's `sunlight_projection_mapping.md` should document item 4 as excluded with a pointer to `results/20260507_sunlight_atomic_audit.md` "User decision (2026-05-07 pm)" section as the reason.

### OpenSecrets 2022 — recovered from drop, with few-shot anchoring

The plan's Phase A1 had a binary outcome (atomic items found / drop). Phase A1's first pass concluded "drop — methodology says scores 0-3 depend on individual circumstances." A re-audit (the user pushed back) found:

- **Cat 4 (Search/access)** — explicitly decomposed in methodology: search=2pts, downloads=2pts, lists=1pt → 3 binary cells. Deterministic projection.
- **Cat 1 (Registration)** — baseline=3 plus 1-point bonus for "separate registrations exist". Single binary cell. Deterministic projection.
- **Cats 2, 3** — published methodology says "depending on the individual circumstances", but the article's Rankings narrative names 5 states with category-level reasoning (WA, ND, SD, VA, OK) plus population-level statistical anchors. Few-shot projection is implementable: cells extract deterministically, function from cells to score is calibrated by worked examples + statistical anchors.

**Phase B inputs for OpenSecrets:**
- `results/items_OpenSecrets.tsv` — 7-row atomic-item extract (kept from per-paper wave)
- `results/opensecrets_worked_examples_2022.csv` — 18 rows of state-level worked examples + verbatim quotes + line refs (Phase A1-recheck output; not in plan)
- `results/20260507_opensecrets_recheck.md` — supersedes the original drop verdict; documents Cat 1-4 projectability per category
- `results/20260507_opensecrets_atomic_audit.md` — original drop audit; kept as appendix, do NOT delete

**Open option:** the OpenSecrets state-map widget at opensecrets.org/state-lobbying likely renders per-state per-category numerics behind JS. If Phase B finds Cat 1 projectability is load-bearing and the binary baseline-3-vs-4 isn't enough, this is the next unlock. Not done yet; flagged in the recheck note.

### FOCAL 2024 — fully populated from Suppl File 1 (verbatim, not inferred)

The plan's Phase A4 anticipated needing a Wiley web-fetch to retrieve Suppl File 1 with Tables 3 + 4 + 5. Two passes happened:

1. **First pass** populated `items_FOCAL.tsv` scoring rules using main-paper Figure 3 max-observed weight inference. 8 indicators ended up weight=UNKNOWN (all 28 countries scored 0 in Figure 3 → max-observed couldn't reveal the weight). Per-country score CSV (`focal_2025_lacy_nichols_per_country_scores.csv`, 1,400 rows) built from Figure 3 visual reading.
2. **Wiley web-fetch attempt** failed (403 / timeout / archive.org refused / PMC embargoed). Documented in audit; no fabrication.
3. **Manual user download** of supplements from Wiley landing page → two .docx files: milq70033-sup-0001 and -0002. Sup-0001 contains all three tables in one file; sup-0002 is the tobacco case study (out of scope). Pandoc-converted to text in `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_001.txt` (738 lines).
4. **Second extraction pass** read the .txt and:
   - Closed all 8 weight-UNKNOWNs with verbatim values
   - Verified 40 of 42 prior Figure-3-inferred weights matched verbatim Suppl Table 4
   - Caught **2 conflicts** (`financials.3` 1→2, `financials.8` 1→2) — published *weighted* cell values were correct, only the (weight × raw) decomposition was off; raw scores updated for Canada/financials.3, Germany/financials.3, France/financials.8
   - Populated 50 rows of `focal_2025_lacy_nichols_prior_framework_mapping.csv` (Bednarova/CPI/Roth/Total/Our weights — the cross-rubric weighting comparison)
   - Reconciled the per-country matrix (1,372 cells matched, 45 changed: 27 NA-handling for unassessable Ministerial-diary cells, 13 Finland descriptors/contact-log corrections that drop Finland's weighted total 70→46, 3 weight-decomposition fixes, 2 Georgia financials blank-as-0)
   - **US row sanity check passes: 81/182 = 44.5% ≈ 45%** — confirmed against published value
   - Weight distribution: 20×weight-1, 19×weight-2, 11×weight-3 → max 182 (matches paper denominator)

**One internal-supplement discrepancy worth knowing about:** Suppl Table 5's "TOTAL (out of 100pts)" row does NOT match Figure 3 percentages (US Table 5 says 42, Figure 3 says 45). Computing Table 5 raw × Table 4 weights reproduces Figure 3 exactly for all 28 countries. **Figure 3 is authoritative; Table 5's TOTAL row is wrong.** Documented in `results/20260507_focal_a4_audit.md`.

**Phase B inputs for FOCAL:**
- `results/items_FOCAL.tsv` — 50 indicators, all with verbatim scoring rules + weights
- `results/focal_2025_lacy_nichols_per_country_scores.csv` — 1,372 (country, indicator) cells with raw + weighted scores. **Per-row ground truth for FOCAL projection validation.**
- `results/focal_2025_lacy_nichols_prior_framework_mapping.csv` — 50 rows mapping FOCAL indicators to Bednarova / CPI / Roth weights. Useful for Phase C cross-rubric validation across the L-N 2025 weighting scheme.
- `results/20260507_focal_a4_audit.md` — audit history including the two conflicts caught, Finland correction, Table 5 vs Figure 3 reconciliation
- `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_001.txt` — source-of-truth for any verbatim quotes

**Validation jurisdiction = US federal LDA** (target: 81/182 = 45%). State-level FOCAL projection runs the same logic on state cells but has no published state-level ground truth.

### LobbyView — schema-coverage rubric, distinct shape

The plan's Phase A2 confirmed LobbyView is federal-LDA-only (Kim 2018 / 2025). 46 schema fields written to `results/items_LobbyView.tsv` (superset of `items_Kim2018.tsv` — both retained; the latter is a per-paper extract, the former is the schema-coverage rubric).

**LobbyView's projection is shape-different from the others:**

- Other rubrics: `f_rubric(compendium_cells, vintage) → rubric_score`
- LobbyView: `coverage_check(compendium_rows, lobbyview_schema_fields) → coverage_map` — i.e., for each LobbyView field, does the compendium have a row that captures the same data? It's a schema-completeness check, not a numerical score. Validation is "for federal LDA, which LobbyView fields can the compendium populate from the LDA filing data?" → answer should be ~100%.

Tackle LobbyView last; the schema-coverage shape may inform what compendium rows need to be added based on LobbyView fields the rest of the rubric set doesn't cover (e.g., `bill_position` is Wisconsin-only at the state level — flag it but include the compendium row).

**Three ambiguities flagged for awareness** (not blockers):
1. `lobbyist_id` / `lobbyist_demographics` are central to Kim 2025's GNN but **not exposed in the public API** — published-data ≠ public-API surface
2. Kim 2018's bill-detection pipeline has **no published precision/recall** — `bill_client_link` users work with undocumented error
3. `bill_position` (Wisconsin only) and `firm_financials` (Compustat coverage gap for non-public state clients) are state-level analog cliffs likely to bite Phase B mapping

### Other rubrics (no scope changes)

HiredGuns 2007, Newmark 2017, Newmark 2005, Opheim 1991, CPI 2015 C11, PRI 2010 — all scope unchanged from plan. Use the existing `items_*.tsv` files as inputs.

---

## Phase B per-rubric output (unchanged from plan, repeated for convenience)

For each contributing rubric, produce `results/projections/<rubric>_projection_mapping.md`. Per-item structure (from plan §Phase B):

```markdown
### <rubric_item_id>: <indicator_text>

- **Compendium rows:** `<row_id_1>`, `<row_id_2>` (or "NEW: <proposed name>" if not in consensus output)
- **Cell type:** binary | enum {a,b,c} | typed: <type>
- **Axis:** legal_availability | practical_availability
- **Scoring rule:** <function from cell value(s) to per-item score, paraphrased from rubric>
- **Source quote:** <copied verbatim from items_<Rubric>.tsv source_quote column>
```

**Done condition:** per-rubric mapping docs exist for all 9 score-projection rubrics + 1 schema-coverage doc for LobbyView. Union of `compendium_rows` saved as `results/projections/disclosure_side_compendium_items_v1.tsv`.

The 3-way consensus output (`results/3way_consensus/consensus_clusters_strict.csv` + `consensus_clusters_loose.csv`) is the **starting point** for compendium-row reference, not a contract — rows that show up in projection mappings but not in consensus should be ADDED to compendium 2.0; rows that show up in consensus but no projection reads should be flagged "keep / delete?" for separate decision.

---

## What's still open after Phase A

Two items deliberately punted (not blockers for Phase B):

1. **OpenSecrets state-map widget JS pull** — would close Cat 1 projectability if needed. Currently Cat 1 is at "binary baseline-3-vs-4" — sufficient for Phase B mapping; only revisit if Phase C validation shows the binary doesn't reach the published per-state Cat-1 scores.
2. **Sunlight 2011 predecessor data** — possibly more granular than 2015's 5-criterion structure. Audit note flagged as "would re-open the Sunlight verdict if surfaced." Not a blocker — Sunlight 2015 stands on its own atomic-item set.

---

## Quick orientation for the implementing agent

When you start Phase B:

1. Read the plan: `../20260507_atomic_items_and_projections.md`
2. Read this handoff (you're doing it now)
3. Read RESEARCH_LOG.md's most recent session entry for the broader context
4. Confirm worktree environment: `git -C /Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts status`
5. **Start with CPI 2015 C11.** It has the smallest item count (14) and the most direct path from rubric items to compendium rows. Build `results/projections/cpi_2015_c11_projection_mapping.md` first; surface design issues before scaling to the other 8 rubrics.
6. Phase B is mapping work, not code. No TDD; analytical judgment + verbatim source quotes.

The compendium 2.0 row set falls out as the union of `compendium_rows` across all mappings — don't pre-commit to row structure. The projections drive the row design, not the other way around.

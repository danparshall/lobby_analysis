# 9-Rubric Oracle-Granularity Audit — Phase B Row-Pick Anchor

**Date:** 2026-06-04
**Branch:** wi-tier1-direct-read
**Originating convo:** [`../convos/20260604_wide_pass_commit3_redispatch_and_audit.md`](../convos/20260604_wide_pass_commit3_redispatch_and_audit.md) (§"9-rubric oracle-granularity audit (deferred)")
**Purpose:** Document, per source rubric, what per-state ground-truth granularity is actually available in the project archive — to anchor the Phase B Ralph-loop first-row pick. The Commit 3 brainstorm tentatively assumed PRI 2010 had per-item × per-state data from `pri-2026-rescore` transcription; this audit checks all 9 rubrics against archived data.

**Scope:** Read-only audit. No API spend. No Ralph implementation. No compendium edits.

**Headline finding:** **PRI 2010's published per-state data is per-CATEGORY × per-state for the disclosure-law rubric** (the one feeding the legal axis we're working on), **not per-item × per-state.** The Commit 3 convo's tentative Phase B first-row candidate `lobbyist_registration_renewal_cadence` is still good, but **the oracle source for it is CPI 2015 C11 (IND_199), not PRI 2010.** CPI 2015 C11 is the cleanest per-item × per-state ground-truth set in the archive (700 cells), and 21 of the 181 compendium rows are read by CPI 2015.

---

## Methodology

Walked the following archived data sources:

1. **`docs/historical/pri-2026-rescore/results/`** — PRI 2010 transcribed rubric + per-state score CSVs.
2. **`docs/historical/compendium-source-extracts/results/`** — Per-rubric projection mappings (`projections/<rubric>_projection_mapping.md`), per-paper atomic-item TSVs (`items_<Rubric>.tsv`), and extracted per-state ground-truth CSVs.
3. **`docs/historical/compendium-source-extracts/results/_tabled/`** — OpenSecrets 2022 tabling rationale.
4. **`docs/historical/phase-c-projection-tdd/`** — Per-rubric implementation plans (which name the validation-regime tier for each rubric explicitly).
5. **`papers/`** — Source rubric papers + machine-readable companion files (`Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`, `CPI_2015__sii_scores.csv`, `CPI_2015__sii_criteria.xlsx`, `Lacy-Nichols-Supple-File-1-IJHPM.pdf`).

The phase-c-projection-tdd branch already classified the validation regimes explicitly (RESEARCH_LOG line 505):

> **Validation regime tiers split 3 ways** — Strong (CPI/HG/FOCAL: per-state per-item); Medium (PRI/Newmark 2017: per-state sub-aggregate); Weak-inequality only (Newmark 2005, Opheim 1991): `our_partial ≤ paper_total` is the only check.

This audit uses that classification, qualifies it where archive completeness differs from published-paper completeness, and adds the granularity-axis the convo brainstorm was operating on (per-item × per-state vs per-category × per-state vs per-state rollup only).

---

## Per-rubric availability table

| # | Rubric | Vintage (statute year) | Published granularity | Cells in archive (US states) | Ralph row-level oracle? |
|---|---|---|---|---|---|
| 1 | **PRI 2010 — Accessibility** | 2009-10 | Per-item × per-state for **Q1–Q6 only** (6 binary); aggregate-only for Q7 (15 sub-criteria → `Q7_raw` int 0–15) and Q8 (`Q8_normalized` float 0–1) | 50 × 8 = **400** (6 per-item + 2 aggregate) | **Yes for Q1–Q6** (300 cells); **No for Q7a–Q7o, Q8** |
| 2 | **PRI 2010 — Disclosure-law** | 2009-10 | Per-CATEGORY × per-state (5 sub-aggregates: A_registration, B_gov_exemptions, C_public_entity_def, D_materiality, E_info_disclosed); item-level NOT published | 50 × 5 = **250** sub-aggregate cells | **No** — per-state per-item not available; the 60-item rubric structure exists in `pri_2010_disclosure_law_rubric.csv` but not as a per-state matrix |
| 3 | **CPI 2015 C11 (Lobbying Disclosure)** | 2014-15 | Per-INDICATOR × per-state (14 indicators IND_196–IND_209) | 50 × 14 = **700** | **Yes** (gold standard; the only per-item × per-state legal-axis oracle currently in archive) |
| 4 | **CPI 2015 main scorecard (12 other categories)** | 2014-15 | Per-CATEGORY × per-state (13 categories × 50 states); only category 11 is lobbying-relevant and is already covered in row #3 | 50 cells for "Lobbying Disclosure" column (aggregate only) | **No** — the cell-level data lives in #3, not this published scorecard |
| 5 | **FOCAL 2024 framework** (Lacy-Nichols 2024 IJHPM) | n/a — framework synthesis | No jurisdictions scored | 0 | **No** (framework paper has no data) |
| 5b | **FOCAL applied = L-N 2025** (Milbank Quarterly) | 2019-23 (Israel 2025) | Per-INDICATOR × per-COUNTRY (28 countries × 49 merged-2025 indicators) | 1,372 cells global; "United States" row = **Federal LDA only, 1 jurisdiction × 49 indicators = 49 cells** | **Yes for Federal LDA** (49 cells); **No for any US state** — FOCAL has never been applied to US states |
| 6 | **Sunlight 2015** | early-to-mid 2015 | Per-CATEGORY × per-state (5 ordinal categories, 5-tier scale −2..+2); category 4 unusable per project audit (5-tier conflates 3-4 sub-features, documented near-typo) | 50 × 5 = 250 published; **200 usable** (categories 1, 2, 3, 5) | **Partial** — per-category, not per-item; ordinal not binary. Cells usable as a category-level coarser oracle, not a strict per-row oracle |
| 7 | **Newmark 2017** | 2015-16 (BoS edition) | Per-SUB-AGGREGATE × per-state (Table 2: `def.section_total`, `prohib.section_total`, `disclosure.section_total`, `index.total`); `prohib.*` excluded under disclosure-only Phase B scope | 50 × 2 sub-aggregates in scope = **100** | **No** at row level (sub-aggregate only; per-atomic-item NOT published) |
| 8 | **Newmark 2005** | 6 panels: 1990-91, 1994-95, 1996-97, 2000-01, 2002, 2003 | Per-state INDEX TOTAL only (Table 1); no sub-aggregate breakdown published | 50 × 6 panels = **300 weak-inequality cells** (`our_partial ≤ paper_total`) | **No** — only total available |
| 9 | **Opheim 1991** | 1988-89 | Per-state INDEX TOTAL only (Table 1); 3 states (MT/SD/VA) excluded by paper as data-unavailable | 47 × 1 = **47 weak-inequality cells**. **1988-89 statute data not found online** — end-to-end validation currently not executable per `phase-c-projection-tdd/results/20260514_rubric_data_years.md` | **No** — only total; and statute vintage unretrievable for the projection input side |
| 10 | **HG 2007 (= CPI Hired Guns, actually 2003 data)** | **2003** (NOT 2007 — see `phase-c-projection-tdd/results/20260521_hg_vintage_correction.md`) | Per-state per-question scorecard exists at CPI archives (`publicintegrity.org/.../nationwide.aspx?st=XX`) but **NOT retrieved into project**; methodology TSV only (48 atomic items in `items_HiredGuns.tsv`) | **0 retrieved**; **potential 1,900** (50 × 38 in-scope items) if Path A retrieval ever runs | **Conditional yes** — requires retrieval first; HG implementation deferred per same doc (Path A needs 2003-vintage statute data, mostly unavailable) |
| 11 | **OpenSecrets 2022** | 2022 | Per-state 0–20 totals in article text (50 cells); per-category 0–5 breakdowns (4 categories × 50 states = 200 cells) behind JS-rendered state-map widget at opensecrets.org/state-lobbying — **NOT webfetch-accessible, NOT retrieved** | **Text: 50 aggregate cells**; **widget: 200 unretrieved**; project archive has only the 18-row `opensecrets_worked_examples_2022.csv` (qualitative examples, not per-state-per-category numerics) | **No currently** — TABLED 2026-05-13 from compendium-source-extracts (`_tabled/opensecrets_2022_tabled.md`). Reinstatement requires per-category numeric retrieval |
| 12 | **LobbyView 2018 / 2025** (Kim 2018; Kim 2025) | Federal LDA, ongoing | Schema definition only — no per-state per-item scoring data; treated as **schema-coverage check, not score projection** per `lobbyview_schema_coverage.md` | 0 score cells | **No** — wrong validation shape (schema field coverage, not value-projection) |

---

## What changed from the Commit 3 convo's recollection

The wide-pass-Commit-3 convo (§"9-rubric oracle-granularity audit (deferred)") said:

> *"PRI 2010 has per-item × per-state from `pri-2026-rescore` transcription, FOCAL 2024 has per-(state, item) from L-N 2025 Supp File 1, Sunlight 2015 has 5-tier categorical per-state per-category. CPI/Newmark/Opheim/HG/OpenSecrets are likely aggregate-only."*

After walking the archive, the correct read is:

| Recollection | Reality |
|---|---|
| PRI 2010 has per-item × per-state | **PARTIALLY WRONG.** PRI 2010 Accessibility has per-item × per-state for only Q1–Q6 (6 binary items). PRI 2010 Disclosure-law (the legal-axis-relevant half) is **per-CATEGORY × per-state** (5 sub-aggregates). Per-atomic-item per-state NOT published. |
| FOCAL has per-(state, item) from L-N 2025 Supp File 1 | **WRONG for US states.** L-N 2025 published per-COUNTRY × per-indicator for 28 countries — only "United States" appears, and it's the federal LDA, not 50 states. **Zero US-state per-item cells from FOCAL.** |
| Sunlight 5-tier per-state per-category | **CORRECT** — and the project audit confirms category 4 is unusable, leaving 4 categories × 50 states = 200 usable cells. |
| CPI aggregate-only | **WRONG.** CPI 2015 C11 has **per-INDICATOR × per-state, 700 cells**, extracted by the `compendium-source-extracts` branch from `papers/CPI_2015__sii_criteria.xlsx` to `results/cpi_2015_c11_per_state_scores.csv` on 2026-05-07. This is the strongest per-item × per-state oracle in the archive. |
| Newmark/Opheim aggregate-only | **CORRECT** — Newmark 2017 per-sub-aggregate, Newmark 2005 + Opheim per-total only. |
| HG aggregate-only | **PARTIALLY CORRECT** — HG per-state per-question DOES exist at CPI archives but is **NOT retrieved** into the project. Also: HG vintage is 2003, not 2007 (corrected 2026-05-21). |
| OpenSecrets aggregate-only | **CORRECT** for what's retrieved (per-state 0–20 totals); per-category breakdowns exist behind a JS widget but are unretrieved and the rubric is TABLED. |

**Net implication for Phase B row pick:** The Commit 3 candidate `lobbyist_registration_renewal_cadence` is still valid — but **the row's per-state oracle is CPI 2015 C11 IND_199** (per-state YES/MODERATE/NO across all 50 states), **not PRI 2010**. PRI does not read `renewal_cadence` directly, and even where PRI does read a row, PRI provides only sub-aggregate-level ground truth.

---

## Ralph-tractability classification

A rubric is **row-level Ralph-tractable** if its archived per-state ground truth is per-item-granular (so a single compendium row can be checked against a single published score for a single state). Tiered:

### Tier 1 — Row-level Ralph-tractable, available now

| Rubric | Cell scope | Cells × states | Compendium rows reached |
|---|---|---|---|
| **CPI 2015 C11** | 14 indicators (IND_196–IND_209) | 14 × 50 = **700 cells** | **21 compendium rows** read by `cpi_2015` per `compendium/disclosure_side_compendium_items_v2.tsv` (rubrics_reading column) — covers registration, spending reports, audit, penalties, document access |
| **PRI 2010 Accessibility Q1–Q6** | 6 binary items × 50 states | 6 × 50 = **300 cells** | Maps to compendium accessibility/portal-side rows (limited overlap with legal axis we're currently working on) |

### Tier 1.5 — Row-level oracle but coarser (categorical, not binary)

| Rubric | Cell scope | Cells × states | Notes |
|---|---|---|---|
| **Sunlight 2015** | 4 of 5 categories (5-tier ordinal −2..+2) | 4 × 50 = **200 cells** | Per-CATEGORY, not per-row. A compendium row is one of N rows feeding a category's tier — projection function is needed before the category score can validate against any single row. Useful as a category-level sanity check; not a single-row oracle |

### Tier 2 — Sub-aggregate oracle only (not single-row)

| Rubric | Cell scope | Cells × states | Notes |
|---|---|---|---|
| **PRI 2010 Disclosure-law** | 5 sub-aggregates (A/B/C/D/E) × 50 states | 5 × 50 = **250 cells** | Single compendium row → falls into one of 5 buckets, but Pat C says PRI's E-rollup rule is "not specified at atomic granularity"; per-row check impossible without resolving the within-bucket weights |
| **Newmark 2017** | 2 in-scope sub-aggregates (def + disclosure) × 50 states | 2 × 50 = **100 cells** | Same shape as PRI: row-to-sub-aggregate is many-to-one, with rollup rule un-derivable from sub-aggregate-only data |

### Tier 3 — State-total weak-inequality only

| Rubric | Cell scope | Cells | Notes |
|---|---|---|---|
| **Newmark 2005** | 50 states × 6 panels (totals) | **300 weak-inequality cells** | `our_partial ≤ paper_total` |
| **Opheim 1991** | 47 states × 1 panel (totals) | **47 weak-inequality cells** | 1988-89 statute snapshots not currently retrievable → calibration step blocked |
| **OpenSecrets 2022 (text totals)** | 50 states × 0-20 totals | **50 weak-inequality cells** | Rubric tabled from compendium-source-extracts |

### Tier 4 — Not available / wrong shape

| Rubric | Status |
|---|---|
| **FOCAL 2024 framework** | No data published |
| **L-N 2025 applied (per-country)** | Federal LDA only (1 × 49 = 49 cells); zero US-state cells |
| **HG 2007 (per-state-per-question)** | Per-state per-question exists at CPI but unretrieved; vintage = 2003; statute-side retrieval also blocked |
| **OpenSecrets 2022 (per-category breakdowns)** | Behind JS-rendered widget; unretrieved; rubric tabled |
| **LobbyView 2018/2025** | Schema-coverage check, not score-projection |

---

## Implication for Phase B Ralph first-row pick

**The single highest-leverage oracle source for a row-level Ralph loop on the legal axis is CPI 2015 C11.** The 21 compendium rows read by `cpi_2015` are:

```
def_target_executive_agency
def_target_governors_office
def_target_independent_agency
def_target_legislative_branch
def_target_legislative_staff
lobbying_data_open_data_quality
lobbying_disclosure_audit_required_in_law
lobbying_disclosure_documents_free_to_access
lobbying_disclosure_documents_online
lobbying_disclosure_offline_request_response_time_days
lobbying_violation_penalties_imposed_in_practice
lobbyist_registration_deadline_days_after_first_lobbying
lobbyist_registration_renewal_cadence
lobbyist_registration_required
lobbyist_registration_threshold_compensation_dollars
lobbyist_spending_report_filing_cadence
lobbyist_spending_report_includes_itemized_expenses
lobbyist_spending_report_includes_total_compensation
lobbyist_spending_report_required
principal_spending_report_includes_compensation_paid_to_lobbyists
principal_spending_report_required
```

For Wisconsin specifically, all 14 IND_196–IND_209 cells have CPI-published values (verified — see appendix). So Phase B for WI on any of the 21 CPI-readable rows has:

- **A single published score** (Wisconsin's IND_XXX value) as the per-state oracle
- **49 other state values** as cross-state consistency context (e.g., the IND_199 column for `renewal_cadence` is 50 YES/MODERATE/NO values)
- **The published scoring rule** in `papers/CPI_2015__sii_criteria.xlsx` extracted to the projection mapping — what the YES/MODERATE/NO anchors mean

### Intersection with wide-pass disagreements and instantiation failures

The Commit 3 wide-pass audit flagged 6 disagreements + 11 NEW instantiation failures (on 4 specific rows). Cross-tabulating which of those are CPI-readable (= have a per-state oracle in the 700-cell table):

| Wide-pass affected row | Type of issue | CPI-readable? | CPI indicator | WI's CPI value |
|---|---|---|---|---|
| `lobbyist_registration_renewal_cadence` | Real regression (YES/MODERATE/NO → IntCell mismatch; Claude 3/3 fail) | **Yes** | IND_199 | **MODERATE** |
| `lobbying_violation_penalties_imposed_in_practice` | Pattern C mis-axed (narrow-pass disagreement) | **Yes** | IND_209 | **50** (per-state 0-100 step 25 practical) |
| `lobbyist_spending_report_filing_cadence` | GPT 0 → EnumCell mismatch (3/3 fail) | **Yes** | IND_201 (related) | **NO** (note: IND_201 reads spending-report cadence + itemization jointly) |
| `lobbyist_registration_threshold_expenditure_dollars` | Newly-stabilized-into-disagree | **Partial** (CPI IND_198 is "all paid lobbyists actually register" — practical, not exact dollar threshold) | IND_198 (proxy) | 50 |
| `lobbyist_registration_amendment_deadline_days` | Newly-stabilized-into-disagree | No direct CPI indicator | n/a | n/a |
| `lobbyist_registration_deadline_days_after_first_lobbying` | Newly-stabilized-into-disagree | **Yes** | IND_200 ("In practice... within a few days...") | **50** |
| `de_minimis_threshold_dollars` | -1 sentinel → DecimalCell non-negative fail | Unclear (HG-introduced) | n/a directly | n/a |

The clean Phase B first-row picks (real regression + clean CPI oracle):

1. **`lobbyist_registration_renewal_cadence`** — CPI IND_199, WI=MODERATE. Already the convo's top candidate. The CPI scoring rule defines MODERATE = "lobbyists must fill out and file a registration form, but with less frequency [than annual]." WI requires biennial renewal per §13.62 → CPI's MODERATE → in the v2 IntCell formulation, value should be 24 (months) or {24, biennial}. The wide-pass failure was that CPI's YES/MODERATE/NO prompt vocab landed in YAML against an IntCell row — exactly what Phase A pre-flight is meant to fix.
2. **`lobbyist_spending_report_filing_cadence`** — CPI IND_201, WI=NO. Failure: GPT submitted int `0` to EnumCell. Same prompt-vocab/cell-type mismatch shape.
3. **`lobbying_violation_penalties_imposed_in_practice`** — CPI IND_209, WI=50 (practical). The known Pattern C mis-axed row from `_pre_wide_pass` baseline. v2.2 ledger Entry 2 is the row-design fix; CPI provides the per-state oracle for the practical axis.

### Why CPI 2015 C11 is the right Phase B anchor, not PRI

- **Granularity match.** CPI publishes per-INDICATOR × per-state; PRI publishes per-CATEGORY × per-state (disclosure-law) or per-item only for accessibility Q1-Q6.
- **Vintage proximity.** CPI 2015 (2014-15 statutes) is closer to WI 2025 than PRI 2010 (2009-10 statutes). Cross-vintage drift is smaller on most rows over 10 years than over 15.
- **Larger overlap with WI Tier-1 issues.** 3 of 6 wide-pass disagreements + 2 of 4 instantiation-failure rows are CPI-readable; PRI-only rows are largely unaffected by wide-pass changes.
- **Scoring rules published verbatim** in `CPI_2015__sii_criteria.xlsx`, lifted into the per-CPI-IND projection mapping. The YES/MODERATE/NO and 100/50/0 anchors are the same vocabulary that's currently mis-landed in YAML — Phase A audit will reconcile them with cell types; Phase B Ralph then checks that the model's emission matches WI's published cell.

---

## Caveats and known unknowns

1. **CPI 2015 has 6 data-quality glitches** in its per-state extract (4 mixed-case typos + 2 numeric-where-categorical entries). Out of 700 cells, ≈0.9% noise; Phase B should normalize case-insensitively and flag the 2 numeric cells for caveat.

2. **PRI 2010 accessibility Q1–Q6 is per-item × per-state, but those items are accessibility (portal-side), not legal-axis.** wi-tier1-direct-read is legal-axis only, so Q1–Q6 don't help the current Phase B work. They will become relevant when Tier-3 portal extraction lands and we have an accessibility-axis Ralph loop.

3. **HG 2007's Path A 1,900-cell ground truth is retrievable** (per `phase-c-projection-tdd/results/20260521_hg_vintage_correction.md` §3 — CPI's per-state pages at `nationwide.aspx?st=XX&display=DRStateNumbers` are scrapable from Wayback). A retrieval pass would more than double the row-level oracle pool (CPI 700 + HG 1,900 = 2,600 cells over the 50 states). The 2003 vintage is older than CPI 2015's 2014-15, so cross-vintage drift would be a larger concern.

4. **OpenSecrets 2022's 200 per-category cells are behind a JS widget** and would require browser-based retrieval. If retrieved, the rubric could re-enter compendium contribution (per `_tabled/opensecrets_2022_tabled.md` reinstatement trigger 2). Out-of-scope for Phase B's first row but worth noting.

5. **FOCAL has NO US-state per-item ground truth.** This audit confirms the validation gap that the FOCAL projection mapping already calls out ("US states: 50 jurisdictions × 49 in-scope indicators = 2,450 projected cells, **NONE with FOCAL-published ground truth**"). FOCAL projections on US states can only be cross-rubric-validated, never paper-validated directly.

6. **L-N 2025's per-country data IS useful but only for Federal LDA**, the 1 of 28 jurisdictions that's a US polity. 49 cells × 1 jurisdiction is enough for a federal-LDA Ralph loop but not state-level. If/when we build a federal-LDA branch, L-N 2025 + the 49 FOCAL indicators is the natural anchor.

7. **The 6 TimeThresholdCell.unit failures** (v2.2 ledger Entry 1) persist across narrow-pass and wide-pass. They're schema-side, not prompt-side, and not addressable by Ralph at any granularity — schema fix required first.

---

## Recommendation for next session

**Phase B first row: `lobbyist_registration_renewal_cadence`** (the Commit 3 convo's tentative pick, now confirmed with the right oracle source identified).

- **Oracle:** CPI 2015 IND_199, all 50 states (700-cell table at `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`).
- **WI's published value:** MODERATE.
- **Compendium row's cell type:** `typed: Optional[int_months]` (or enum) — per the projection mapping.
- **Wide-pass failure mode:** YES/MODERATE/NO prompt landed for IntCell row; Claude 3/3 instantiation failures; GPT changed unit (24 months → 2 years).
- **Phase A pre-flight fix:** the YAML prompt for this row should not echo CPI's YES/MODERATE/NO scoring vocabulary verbatim — should instead ask for the cadence value (e.g., "How often must lobbyists renew their registration? Answer in months. Use 12 for annual, 24 for biennial, etc.").
- **Phase B Ralph criterion:** after Phase A patch, do WI's three runs converge on `magnitude=24, unit=months` (which projects to CPI MODERATE)? If yes, row passes. If no, iterate on prompt clarification.
- **Dan's "first row by hand" framing applies** — do the iteration manually with the human in the loop, decide automation level afterward.

**Phase B candidate row #2 (parallel sanity check on Phase A): `lobbyist_spending_report_filing_cadence`** — same cell-type-mismatch failure shape, CPI IND_201 oracle, WI=NO.

**Out of Phase B's initial scope but worth noting:** rows introduced by PRI/Newmark/Opheim/HG where no per-item × per-state oracle exists. These rows can use **cross-rubric overlap** as the validation check (a row read by both PRI and CPI, validated against the CPI per-state value, is correct-by-construction for the PRI projection too since both rubrics are reading the same upstream statute). The phase-c-projection-tdd Newmark plans already document this pattern.

---

## Appendix: Wisconsin's full CPI 2015 C11 row (per-state oracle, 14 indicators)

From `docs/historical/compendium-source-extracts/results/cpi_2015_c11_per_state_scores.csv`:

| CPI indicator | WI value | Note |
|---|---|---|
| IND_196 | YES | In law, there is a clear definition of lobbyist |
| IND_197 | MODERATE | In law, the lobbyist definition includes broader actors |
| IND_198 | 50 | In practice, all paid lobbyists actually register (5-tier) |
| IND_199 | MODERATE | In law, lobbyists must file registration form annually |
| IND_200 | 50 | In practice, lobbyists file detailed registration within days (5-tier) |
| IND_201 | NO | In law, lobbyists file at least quarterly detailed reports |
| IND_202 | 0 | In practice, lobbyists submit detailed expense reports (5-tier) |
| IND_203 | YES | In law, principals required to file detailed reports |
| IND_204 | 50 | In practice, principals file detailed expense reports (5-tier) |
| IND_205 | 100 | In practice, citizens can access disclosure information (5-tier) |
| IND_206 | 25 | In practice, the entity in charge of disclosure conducts effective oversight (5-tier) |
| IND_207 | YES | In law, the lobbying disclosure agency conducts independent audits |
| IND_208 | 25 | In practice, lobbying disclosure regulations are enforced (5-tier) |
| IND_209 | 50 | In practice, sanctions and remediation are applied (5-tier) |

These 14 cells are the row-level oracle pool for Wisconsin's Phase B work. A Ralph loop on any row reading any of these indicators has a single published target value to converge toward.

# OpenSecrets 2022 — projection mapping (SUPERSEDED — kept as research artifact)

> ## ⚠️ SUPERSEDED 2026-05-13 by [`opensecrets_2022_tabled.md`](opensecrets_2022_tabled.md).
>
> This document was the Phase B projection-mapping draft for OpenSecrets 2022, written 2026-05-12. The drafting process surfaced (and the user check-in confirmed) that OpenSecrets does not meet the branch's projection-vs-published-data success criterion: no published per-tier scoring definition for scores 0–3 in Cats 1/2/3, no Cat 1 score-5 anchor, no per-state per-category numerical data accessible without JS-widget scraping, no inter-coder reliability. Per the 2026-05-13 review, OpenSecrets is **tabled** (not permanently dropped); the 3 OS-distinctive row candidates are tabled alongside. Path forward: see [`opensecrets_2022_tabled.md`](opensecrets_2022_tabled.md) for the tabling rationale, reinstatement triggers, and per-row pickup possibilities. The original location of this file was `results/projections/opensecrets_2022_projection_mapping.md`; moved here to make the supersession explicit (the `results/projections/` directory holds active projection mappings; this is no longer one).
>
> **What's preserved:** the per-category projection reasoning (Cat 1/2 fixed-prior + 4-corner Cat 2 binary decomposition + Cat 3 cadence-pair scoring rule + Cat 4 sub-facet weights). Useful if a reinstatement trigger fires — the analysis doesn't need to be redone.
>
> **What changed in the tabling doc:** the framing. The tabling doc is shorter and explicit about why the rubric isn't a projection target; this superseded doc is the longer mapping-attempt narrative that informed the tabling decision.

---

**Plan:** [`../../plans/20260507_atomic_items_and_projections.md`](../../plans/20260507_atomic_items_and_projections.md) Phase B (fourth rubric, after CPI 2015 C11, PRI 2010, Sunlight 2015).
**Handoff:** [`../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../../plans/_handoffs/20260511_phase_b_continued_remaining_7.md).
**Atomic items source:** [`../items_OpenSecrets.tsv`](../items_OpenSecrets.tsv) (7 rows = 4 top-level categories + 3 named sub-facets of Cat 4).
**Companion methodology note:** [`../items_OpenSecrets.md`](../items_OpenSecrets.md).
**Audit history:** [`../20260507_opensecrets_atomic_audit.md`](../20260507_opensecrets_atomic_audit.md) (original DROP verdict) → [`../20260507_opensecrets_recheck.md`](../20260507_opensecrets_recheck.md) (overturned for Cats 2/3/4; Cat 1 partial). Per user direction 2026-05-12: **all 4 categories are in scope** for this projection mapping; Cat 1 stays in even though its projection is partly degenerate.
**Few-shot calibration set:** [`../opensecrets_worked_examples_2022.csv`](../opensecrets_worked_examples_2022.csv) — 18 worked examples + statistical anchors. Phase-C calibration input, not extraction input.
**Predecessor mappings (for conventions):** [`cpi_2015_c11_projection_mapping.md`](cpi_2015_c11_projection_mapping.md), [`pri_2010_projection_mapping.md`](pri_2010_projection_mapping.md), [`sunlight_2015_projection_mapping.md`](sunlight_2015_projection_mapping.md).

---

## Doc conventions

Inherited verbatim from the CPI / PRI / Sunlight mappings:

- Compendium row IDs are working names chosen to be projection-meaningful (cluster IDs are provenance hints, not authoritative).
- Typed cells live on `MatrixCell.value` (v2.0 schema bump dependency).
- Axis: `legal_availability` for de jure / `practical_availability` for de facto. OpenSecrets Cats 1/2/3 are de jure (statute-readable); Cat 4 is de facto (portal-observable).
- Granularity bias: split on every distinguishing case.
- **Collect once, map to many.** Every row carries a `[cross-rubric: …]` annotation listing other readers. OpenSecrets is a shallow ordinal rubric whose value is cross-rubric redundancy at higher ordinal granularity than the binary rubrics; almost every row OpenSecrets reads is also read by ≥1 other rubric.

New convention surfaced by this mapping:

- **Few-shot calibration vs cell extraction are separate.** OpenSecrets's Cat 1/2/3 ordinals at scores 0–3 are not described by per-tier anchors in the methodology — they're scored by analyst judgment in the rubric. The projection function compensates by reading **finer-grained binary/typed cells than the ordinal alone exposes** and applying a deterministic mapping from cell combinations to the ordinal. Where the cell combination doesn't pin down the ordinal (e.g. Cat 1 score-5 is undefined; Cat 2 scores 1/2/3 distinguish "ranges" vs "unlinked to individuals" but only two binary cells exist for those), the projection returns the best deterministic estimate plus a documented uncertainty band — and the worked-examples CSV is the calibration set Phase C uses to set partial-credit boundaries.

## Aggregation rule

OpenSecrets publishes per-state totals only (article narrative; "complete list" is behind a state-map widget the recheck notes is JS-rendered and not webfetch-accessible). Per-category 0–5 numerics per state are NOT in the article text — only descriptive bands ("top-scoring states (16 and up)" / "poorest scoring states (<10)").

- `score_total = score_cat1 + score_cat2 + score_cat3 + score_cat4`
- `score_cat4 = score_search + score_downloads + score_lists` (with explicit weights 2/2/1, partial points allowed per sub-facet)
- Max = 5 + 5 + 5 + 5 = 20.

**Phase C validation strategy:**

- The per-state 0–20 total is the only deterministic cross-validation target without manual map-widget scraping.
- The 18-row worked-examples CSV provides anchored per-category subsets (WA cat4=5; ND/SD cat2=0 + cat3=very-low + cat4=low; VA cat2≥4; OK cat1≈3). These are calibration anchors *for the projection function*, not ground truth across all 50 states.
- Population-level statistical anchors (17 states cat2=0; 7 states cat2=1-3; 26 states cat2=4-5; 20 states cat3≥4; 16 states cat3=5) give distribution-shape checks the projection's per-state outputs should reproduce in aggregate.
- **Open option from the recheck note:** if Phase C needs tighter validation, the OpenSecrets state-map widget JS pull is the unblocking step. Not done this session.

## Validation jurisdictions

50 US states × 2022 vintage. Federal LDA out of scope (OpenSecrets's federal-comparison section uses LDA descriptively, not as a scoring target).

Per-state ground truth granularity: **state aggregate only** (1 cell per state) + **5 named-state per-category anchors** (WA cat4, ND/SD cat2+cat3+cat4, VA cat2+cat4, OK cat1) + **5 population-level distribution anchors**.

---

## Per-item mappings

### opensecrets_2022.lobbyist_client_disclosure (Cat 1, 0–5 ordinal)

**Score anchors:** 3 = baseline (lobbyist AND client both identified in registration); 4 = state requires separate registrations for lobbyists and clients (not just "lobbyist registers and lists their clients"); 5 undefined in source text; 0–2 = "depending on individual circumstances" with no anchors. OK is named as a negative anchor (3, not 4) because of the "lobbyists communicate amongst themselves" practice.

- **Compendium rows:**
  - `lobbyist_identified_in_registration` (binary; legal)
    [cross-rubric: HG Q3 ("lobbyist required to file a registration form" — implies identification); CPI #196 reads target-side of definition; PRI A1-A11 actor-side; LobbyView `registrant_name` schema field]
    *Near-universal True across 50 states; baseline-3-floor cell.*
  - `client_identified_in_registration` (binary; legal)
    [cross-rubric: HG Q9 ("lobbyist required to identify by name each employer on the registration form"); LobbyView `client_name` schema field]
    *Near-universal True across 50 states; baseline-3-floor cell.*
  - `separate_registrations_for_lobbyists_and_clients` (binary; legal) — **NEW row, OpenSecrets-distinctive**
    [cross-rubric: weakly LobbyView (registrant_uuid + client_uuid are separate identifiers at federal level → state analog if separate registrations); no other rubric reads this directly]
    *The 4-point uplift cell. T = state requires both lobbyists AND clients/principals to register independently; F = single registration where lobbyist registers and includes client names within.*
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule (deterministic from cells where possible; degenerate otherwise):**
  ```
  if NOT (lobbyist_identified AND client_identified):
      # Below baseline — no per-tier anchors in source
      score = 0  # conservative default (rare; no state should hit this)
  elif separate_registrations_for_lobbyists_and_clients:
      score = 4
  else:
      score = 3  # baseline
  # score = 5 unreachable from cells (no published anchor for what 5 means)
  ```
  **Degeneracy:** scores 0/1/2/5 are not projectable from cells alone. Per-state observed scores in OpenSecrets's article are concentrated at 3–4 (article describes OK as baseline=3, no specific state named at 0/1/2/5). Phase C validation: the projection should hit 3 or 4 for the vast majority of states; states scoring 0/1/2/5 in OpenSecrets's per-state widget (if pulled) would surface as projection misses and trigger a row addition or rule refinement.
- **Source quote:** "For lobbying/client disclosure, the baseline score was three and states that require separate registrations for the lobbyists and clients were assigned a four... the baseline practice is identification of both lobbyist and client. States that separate registrations for lobbyists and clients, as opposed to the practice of lobbyists registering and including the names of their clients within, are scored higher." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:49-55, 197-199)
- **Note:** This is the "Cat 1 is partial" row family. OpenSecrets's recheck note flagged this as **NO — projectable for Cat 1**; we keep all three cells in compendium 2.0 anyway (per user direction "all items by default should be in the compendium"). The projection acknowledges the degeneracy — Phase C MAY validate at the per-state 0–20 aggregate level without Cat 1 contributing usable signal beyond the 3/4 split.

### opensecrets_2022.lobbyist_compensation_disclosure (Cat 2, 0–5 ordinal)

**Score anchors:** 0 = no compensation disclosure required; 4 = baseline (full compensation disclosure linked to individual lobbyists); 5 = exceeds baseline (undefined what additional disclosure earns the 5); 1–3 = partial, distinguished by "ranges" vs "unlinked to individual lobbyists" but the per-tier mapping isn't explicit. Population: 17 states = 0; 7 states = 1–3; 26 states = 4–5.

- **Compendium rows:**
  - `lobbyist_spending_report_includes_total_compensation` (binary; legal) — **existing (Sunlight #5, CPI mapping)**
    [cross-rubric: Newmark 2017 `disclosure.total_compensation`; Newmark 2005 `disc_total_compensation`; HG Q13 (binary, spending-report variant); CPI #201 (compound, this is one read); PRI E2f_i; Sunlight #5 lobbyist_compensation]
  - `lobbyist_spending_report_includes_compensation_broken_down_by_client` (binary; legal) — **existing (Sunlight #5)**
    [cross-rubric: Newmark 2017 `disclosure.compensation_by_employer`; Newmark 2005 `disc_compensation_by_employer`; HG Q13 footnote; Sunlight #5]
  - `lobbyist_reg_form_includes_compensation` (binary; legal) — **existing (Sunlight #5)**
    [cross-rubric: HG Q13 footnote ("Full points if information is on registration form instead"); Sunlight #5]
  - `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges` (binary; legal) — **NEW row, OpenSecrets-distinctive**
    [cross-rubric: HG Q13 reads compensation existence but not exact-vs-ranges granularity; no other rubric reads this binary directly]
    *T = exact dollar amount required; F = disclosed in ranges only.*
  - `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate` (binary; legal) — **NEW row, OpenSecrets-distinctive**
    [cross-rubric: implied by the `*_broken_down_by_client` row but not identical (per-lobbyist vs per-client are distinct; a multi-lobbyist firm could disclose aggregate per-client without per-lobbyist split); no clean cross-rubric peer]
    *T = each lobbyist's compensation reported separately; F = aggregate across all lobbyists at a firm.*
  - `principal_spending_report_includes_compensation_paid_to_lobbyists` (binary; legal) — **existing (CPI mapping)**
    [cross-rubric: CPI #203/#204; HG Q27]
- **Cell type:** binary per row.
- **Axis:** `legal_availability`.
- **Scoring rule (deterministic 4-corner mapping; 5 not projectable from cells):**
  ```
  compensation_disclosed_at_all = (
      lobbyist_spending_report_includes_total_compensation
      OR lobbyist_spending_report_includes_compensation_broken_down_by_client
      OR lobbyist_reg_form_includes_compensation
      OR principal_spending_report_includes_compensation_paid_to_lobbyists
  )
  if NOT compensation_disclosed_at_all:
      score = 0
  elif (exact_amount AND per_individual):
      score = 4  # baseline (full disclosure linked to individual lobbyists)
      # score = 5 (exceeds baseline) unreachable from cells; undefined source
  elif (exact_amount AND NOT per_individual):
      score = 2  # exact ranges aggregated across lobbyists
  elif (NOT exact_amount AND per_individual):
      score = 3  # per-lobbyist ranges (better than aggregate-exact per article framing)
  else:  # ranges AND aggregate
      score = 1  # weakest partial form
  ```
  **Calibration anchors (from worked-examples CSV):** ND/SD = 0 (cells: NOT disclosed_at_all). VA = ≥4 (cells: exact AND per-individual). Population: 17 = 0, 7 = 1-3, 26 = 4-5 — projection should reproduce within ±2 states per band.
  **Score-5 caveat:** the recheck note flags this; no published anchor distinguishes 5 from 4. Reasonable Phase C posture: cap projection at 4 and accept the 5 → 4 mapping as a known compression. Could re-open with state-map widget pull.
- **Source quote:** "For compensation and timely reporting, a score of four was assigned to those states that are at least requiring the baseline practices discussed above and a score of five for those that are exceeding the baseline... states that do not require disclosure of compensation received a score of zero for that category. As detailed earlier, several states have partial compensation disclosure. Those received scores of between one and three in relation to the level of compensation disclosed." + "Seventeen states do not require compensation paid to lobbyists be disclosed at all. Seven more states only require partial reporting with compensation either reported in ranges or not linked to individual lobbyists." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:78-81, 199-209, 266-267)
- **Note on cross-rubric reuse:** 4 of 6 rows are already in compendium 2.0 from CPI / Sunlight / PRI mappings — OpenSecrets adds only the 2 finer-grained binaries (`exact_amount_vs_ranges`, `per_individual_vs_aggregate`). These two rows are read at finer granularity than any other rubric reads. Cross-rubric annotation will flag them as "potential OpenSecrets-unique" — the dedup-validity pass for compendium 2.0 should check whether HiredGuns or PRI or CPI implicitly read them.

### opensecrets_2022.timely_disclosure (Cat 3, 0–5 ordinal)

**Score anchors:** 4 = baseline (monthly when legislature in session, quarterly otherwise); 5 = monthly year-round; 0 ≈ once-yearly (ND, SD); 1–3 = below baseline ("depending on individual circumstances"). Population: 20 states ≥ 4; 16 states = 5.

- **Compendium rows:**
  - `lobbyist_spending_report_filing_cadence_in_session` (enum; legal) — **NEW** (or atomic-binary form per PRI mapping)
    [cross-rubric: PRI E1h_i-vi / E2h_i-vi (atomic binaries per cadence option); CPI #199/#202; Opheim `disclosure.frequency` (binary monthly-during-session vs less); Newmark 2005 `freq_reporting_more_than_annual` (binary >annual); HG Q6 (3-tier registration renewal — distinct concept); FOCAL `timeliness.1` (real-time updates — distinct concept)]
    *Enum values: `{monthly, bi_weekly, weekly, quarterly, semi_annual, annual, less_than_annual, not_required}`. Per PRI mapping locked convention: actual storage may be atomic binaries (`cadence_monthly_in_session: bool`, etc.); projection reads the equivalent enum.*
  - `lobbyist_spending_report_filing_cadence_out_of_session` (enum; legal) — **NEW**
    [cross-rubric: same readers — but only OpenSecrets and Opheim distinguish in-session vs out-of-session. PRI's E1h/E2h doesn't make this split explicit (treats cadence as a single option list); the in-session/out-of-session distinction is OpenSecrets-and-Opheim-introduced]
    *Same enum as in-session; for states with year-round single cadence, in-session and out-of-session take the same value.*
- **Cell type:** enum per row (or atomic binaries — see above).
- **Axis:** `legal_availability`.
- **Scoring rule (deterministic ordinal from enum pair):**
  ```
  in_sess = lobbyist_spending_report_filing_cadence_in_session
  out_sess = lobbyist_spending_report_filing_cadence_out_of_session
  if in_sess == 'monthly' AND out_sess == 'monthly':
      score = 5  # monthly year-round
  elif in_sess == 'monthly' AND out_sess in {'quarterly', 'semi_annual'}:
      score = 4  # baseline
  elif in_sess in {'monthly', 'bi_weekly', 'weekly'} AND out_sess in {'annual', 'less_than_annual', 'not_required'}:
      score = 3  # better in-session than baseline but very weak out-of-session
  elif in_sess in {'quarterly', 'semi_annual'} AND out_sess in {'quarterly', 'semi_annual', 'annual'}:
      score = 2  # less than monthly even in-session
  elif in_sess == 'annual' AND out_sess == 'annual':
      score = 1  # consistently sub-baseline
  elif (in_sess in {'less_than_annual', 'not_required'}) OR (out_sess in {'less_than_annual', 'not_required'} AND in_sess in {'annual', 'less_than_annual'}):
      score = 0  # once-yearly or less (ND, SD anchor)
  else:
      score = 2  # mid-band fallback
  ```
  **Calibration anchors:** ND/SD = ≈0 (cells: in_sess=annual, out_sess=annual). Top-tier subset (16 states) = 5 (cells: in_sess=monthly, out_sess=monthly). Baseline of 20 states ≥ 4 (cells: in_sess ∈ {monthly}, out_sess ∈ {monthly, quarterly}). Phase C validates the projection's per-band counts against these.
- **Source quote:** "In our scoring system, the baseline for timely disclosure is set to monthly reporting when the legislature is in session, and quarterly otherwise. This is a standard that 20 states are already using some variation of." + "16 states do require some form of monthly reporting, often tied to the legislative session." + "The bottom two states, North and South Dakota, only require reporting once a year." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:98-101, 234-236, 279-280)
- **Note on cadence row design:** The in-session / out-of-session split is consequential — many state regimes have asymmetric cadence (e.g., monthly during legislative session, then quarterly or semi-annual otherwise). Opheim 1991 read this asymmetry as a single binary ("monthly during the session or both in and out of session"); OpenSecrets reads it as the 4 vs 5 distinction. The two-row split preserves the asymmetry; coarser rubrics' projections roll up via OR or AND as needed. **This row family superseded the CPI mapping's `lobbyist_spending_report_filing_cadence` single-row entry; CPI's open issue 4 (PRI's atomic binaries vs CPI's enum) escalates to a 2-row enum here.** Design-team note: keep the row family flexible enough that PRI's atomic binary representation (E1h_i, E1h_ii, …) can be derived from the enum pair without loss.

### opensecrets_2022.public_avail_search (Cat 4 sub-facet, 0–2 points)

**Sub-facet of Cat 4. Anchors:** 2 = user-friendly search (WA exemplar — easy navigation, auto-populated filters); partial points = search exists but with frictions (jargon, buried behind menus, requires prior knowledge); 0 = no functional search.

- **Compendium rows:**
  - `portal_lobbyist_disclosure_search_quality` (typed `int` ∈ {0, 1, 2}; practical) — **NEW** (or could decompose into 2-3 binaries)
    [cross-rubric: HG Q31 (lobbyist directory format ordinal — "searchable database on the Web" is one tier); HG Q32 (spending report format ordinal — same); FOCAL `openness.5` ("Searchable, simultaneous sorting with multiple criteria"); CPI #205 (compound — searchability is one read); CPI #206 (open data format — searchability one component)]
    *3-tier ordinal: 0 = no functional search; 1 = search exists but limited (single-field, requires exact match, jargon-laden); 2 = multi-criteria search with auto-populating filters (WA exemplar).*
- **Cell type:** typed `int` ∈ {0, 1, 2}. (Alternative: 2 binaries — `portal_search_exists` and `portal_search_user_friendly` — but the 3-tier ordinal matches OpenSecrets's partial-credit framing more cleanly and is consistent with HG Q31/Q32's 4-level ordinal style.)
- **Axis:** `practical_availability`.
- **Scoring rule:** `score = portal_lobbyist_disclosure_search_quality` (direct passthrough, 0–2).
- **Source quote:** "Two points each were assigned to user-friendly search and availability of downloadable data... A search is not particularly helpful if it is buried behind several click throughs, filled with jargon that only makes sense to insiders or requires prior knowledge to perform the search." + "Washington state's site allows easy navigation between categories, auto-populates lists which can be filtered and has a clear link to download results at any time." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:117-119, 215-216, 228-230)
- **Note:** This row is a practical-availability cell on a portal-level observable; not statute-readable. Extraction relies on portal inspection (Track B fellows' territory). The 3-tier ordinal collapses HG Q31's 4-tier (photocopies / PDF / searchable / downloadable) by treating only the "searchable database" component, leaving "downloadable" to the next sub-facet.

### opensecrets_2022.public_avail_downloads (Cat 4 sub-facet, 0–2 points)

**Sub-facet of Cat 4. Anchors:** 2 = downloadable data (WA exemplar); partial = data available but downloads limited (search results without unique URLs, paginated across many pages); 0 = no downloads.

- **Compendium rows:**
  - `portal_lobbyist_disclosure_downloadable` (typed `int` ∈ {0, 1, 2}; practical) — **NEW** (close to existing CPI #206)
    [cross-rubric: CPI #206 (`lobbying_data_open_data_quality` — 5-tier 0/25/50/75/100, reads same observable at finer granularity); HG Q31/Q32 (4-level ordinal, "Downloadable files/database" is top tier); FOCAL `openness.4` ("Downloadable (eg, as files, database)") + `openness.3` (bundles machine-readable / non-proprietary / open-license); CPI #205 (compound — downloadability one component); LobbyView `api_bulk_download` schema field]
    *3-tier ordinal: 0 = no downloads / data not extractable; 1 = data available but extraction is friction-heavy (no bulk download, paginated results, no unique URLs); 2 = bulk download in standard formats.*
- **Cell type:** typed `int` ∈ {0, 1, 2}. (Could alternately reuse CPI #206's 5-tier cell and project OpenSecrets's 3-tier as a coarsening.)
- **Axis:** `practical_availability`.
- **Scoring rule:** `score = portal_lobbyist_disclosure_downloadable` (direct passthrough, 0–2).
- **Source quote:** "Two points each were assigned to user-friendly search and availability of downloadable data... downloadable data is not just a tool for data geeks, but a valuable asset that allows anyone searching for lobbyist data to capture that information... [bad patterns include] searches without unique URLs, results paginated across many pages." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:127-134, 215-216)
- **Note on overlap with CPI #206:** Same underlying observable, different ordinal granularity. Design choice for compendium 2.0: store the **CPI 5-tier value** (`{0, 25, 50, 75, 100}`) as canonical; OpenSecrets's 3-tier is a deterministic projection (`0 → 0`, `25/50 → 1`, `75/100 → 2`, or some similar boundary). This avoids a duplicate cell and preserves the finer-granularity rubric's signal. **Open issue 1** below documents this dedup recommendation.

### opensecrets_2022.public_avail_lists (Cat 4 sub-facet, 0–1 point)

**Sub-facet of Cat 4. Anchors:** 1 = lists available and easily accessed; partial points (e.g., 0.5) = lists available but not easily accessed; 0 = no lists.

- **Compendium rows:**
  - `portal_lobbyist_client_lists_accessibility` (typed `int` ∈ {0, 1, 2}; practical) — **NEW** (3-tier even though OpenSecrets allows 0/0.5/1 because partial-credit is a continuous extension of the same cell-from-portal observable)
    [cross-rubric: FOCAL `openness.1` ("Lobbyist register is online" — close); HG Q35-Q37 (overall spending totals by year / deadline / industry — different shape but related "is the portal making aggregate data discoverable"); no rubric reads partial-list-accessibility directly]
    *3-tier ordinal: 0 = no public list of registered lobbyists/clients exists; 1 = list exists but requires search query (you must know names to find them); 2 = browsable directory exposed prominently on the portal (e.g., A-Z index or auto-populating dropdown).*
- **Cell type:** typed `int` ∈ {0, 1, 2}. Projection maps `0 → 0`, `1 → 0.5`, `2 → 1` to match OpenSecrets's 0/0.5/1 grading.
- **Axis:** `practical_availability`.
- **Scoring rule:**
  ```
  if portal_lobbyist_client_lists_accessibility == 0:
      score = 0
  elif portal_lobbyist_client_lists_accessibility == 1:
      score = 0.5  # partial — list exists but not easily accessed
  else:  # == 2
      score = 1.0  # fully accessible
  ```
- **Source quote:** "Within the five points allocated to this category, one point is dedicated to the availability of lobbyist and client lists. Partial points were assigned based on lists that are available, but not as easily accessed... many of the search systems require users to know the name of a lobbyist or client, easily accessible lists of lobbyists and clients are often a necessity to a functional lobbying transparency site." (papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt:120-126, 212-214)
- **Note:** This is the only sub-facet with a 0–1 point weight (search and downloads carry 2 each). The 3-tier internal representation gives the projection a discoverability dimension distinct from search and downloads — a portal can have great search but no browsable list, or vice versa. The projection's `0.5` for partial is OpenSecrets-specific; other rubrics reading this cell get binary (any non-zero = accessible).

---

## Cat 4 aggregation

`score_cat4 = score_search + score_downloads + score_lists` per the published 2/2/1 weights. The published cap is 5 (the three sub-facets sum to ≤ 5). Range: 0 to 5.

Composite ordinal — but additive, not nested, so the composite cell `public_availability_total` from `items_OpenSecrets.tsv` does NOT need its own compendium row; it's a derived view of the 3 sub-facet cells.

## Summary of compendium rows touched

| Row id (working name) | Cell type | Axis | OpenSecrets cats/sub-facets | Cross-rubric readers (dedup candidates) | Status |
|---|---|---|---|---|---|
| `lobbyist_identified_in_registration` | binary | legal | Cat 1 | HG Q3 (implied); CPI #196 (target-side); LobbyView `registrant_name` | **NEW (baseline-floor)** |
| `client_identified_in_registration` | binary | legal | Cat 1 | HG Q9; LobbyView `client_name` | **NEW (baseline-floor)** |
| `separate_registrations_for_lobbyists_and_clients` | binary | legal | Cat 1 | LobbyView analog (separate UUIDs) | **NEW (OpenSecrets-distinctive)** |
| `lobbyist_spending_report_includes_total_compensation` | binary | legal | Cat 2 | Newmark 17/05 total_compensation; HG Q13; CPI #201; PRI E2f_i; Sunlight #5 | existing (Sunlight + CPI) |
| `lobbyist_spending_report_includes_compensation_broken_down_by_client` | binary | legal | Cat 2 | Newmark 17/05 compensation_by_employer; Sunlight #5 | existing (Sunlight) |
| `lobbyist_reg_form_includes_compensation` | binary | legal | Cat 2 | HG Q13 footnote; Sunlight #5 | existing (Sunlight) |
| `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges` | binary | legal | Cat 2 | (none direct — OpenSecrets-distinctive) | **NEW (OpenSecrets-distinctive)** |
| `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate` | binary | legal | Cat 2 | (none direct — related to `*_broken_down_by_client` but at lobbyist-not-client level) | **NEW (OpenSecrets-distinctive)** |
| `principal_spending_report_includes_compensation_paid_to_lobbyists` | binary | legal | Cat 2 | CPI #203/#204; HG Q27 | existing (CPI) |
| `lobbyist_spending_report_filing_cadence_in_session` | enum | legal | Cat 3 | PRI E1h/E2h (atomic binaries); CPI #199/#202; Opheim disclosure.frequency; Newmark 2005 freq_reporting; HG Q6 | **NEW (or existing PRI atomic family with in-session split)** |
| `lobbyist_spending_report_filing_cadence_out_of_session` | enum | legal | Cat 3 | Opheim disclosure.frequency (binary); no other rubric splits | **NEW (OpenSecrets + Opheim split)** |
| `portal_lobbyist_disclosure_search_quality` | typed int 0-2 | practical | Cat 4-search | HG Q31/Q32 (4-tier); FOCAL openness.5; CPI #205/#206 | **NEW (could fold into CPI #206-derived row)** |
| `portal_lobbyist_disclosure_downloadable` | typed int 0-2 | practical | Cat 4-downloads | CPI #206 (5-tier); HG Q31/Q32; FOCAL openness.3/4; LobbyView api_bulk_download | **NEW (likely fold into CPI #206)** |
| `portal_lobbyist_client_lists_accessibility` | typed int 0-2 | practical | Cat 4-lists | FOCAL openness.1; HG Q35-37 (different shape) | **NEW (OpenSecrets-distinctive)** |

**14 distinct compendium rows touched by 4 categories + 3 sub-facets.** 8 of 14 are either existing (4) or have strong overlap with finer-granularity rubric cells already in compendium 2.0 (4). 6 are net-new from OpenSecrets:
- 3 Cat 1 rows (lobbyist_identified, client_identified, separate_registrations) — only `separate_registrations` is OpenSecrets-distinctive; the other two are baseline-floor cells that other rubrics' projections imply but don't read directly.
- 2 Cat 2 sub-granular binaries (exact_vs_ranges, per_individual_vs_aggregate) — OpenSecrets-distinctive at the partial-credit granularity it reads.
- 1 Cat 4 sub-facet row (lists_accessibility) — partial overlap with FOCAL openness.1 but accessibility-tiered.

OpenSecrets's role: **a higher-ordinal-granularity rubric that exposes 6 candidate finer-granularity cells the binary-tradition rubrics didn't surface.** Compatibility with the other 4 rubric mappings: 100% (no contradictions).

## Open issues surfaced by OpenSecrets

1. **Cat 4 sub-facet rows likely fold into CPI #205/#206 + FOCAL openness.* during compendium-2.0 dedup.** OpenSecrets reads search + downloads at 3-tier granularity; CPI reads them at 5-tier; FOCAL reads them as binaries with partly/yes/no. Compendium 2.0 should store the **finest granularity available** (CPI 5-tier for download quality; combined 3-5 binary cells for search facets) and project each rubric's coarser ordinal from the finer cell via deterministic mapping. The mapping rows in this doc are NEW only as a temporary working name — the dedup pass will likely retire `portal_lobbyist_disclosure_search_quality` and `portal_lobbyist_disclosure_downloadable` in favor of the CPI 5-tier rows + FOCAL openness.5/openness.3 sub-facet decomposition.

2. **Cat 3 cadence row family supersedes the CPI mapping's single-row entry.** The in-session / out-of-session asymmetry is real and load-bearing for OpenSecrets's 4 vs 5 distinction. CPI mapping's Open Issue 4 already flagged the cadence-row design as unresolved; this mapping forces a two-row representation. Retroactive change recommendation: CPI mapping's `lobbyist_spending_report_filing_cadence` entry should reference this in-session/out-of-session pair and read whichever applies (CPI's prose doesn't distinguish; OpenSecrets's does).

3. **Cat 1 score-5 anchor missing.** OpenSecrets's article never defines what earns a 5 in lobbyist/client disclosure. The projection caps at 4. If the state-map widget pull (recheck note open option) ever happens and per-state Cat 1 scores include 5s, those would surface as projection misses and trigger row addition. **Until then, the projection is degenerate at the top of Cat 1's range.**

4. **Cat 2 score-5 also undefined.** Same pattern — "exceeds baseline" is undefined. Projection caps at 4. The 26 states with cat2 ∈ {4, 5} per the population anchor can't be split between 4 and 5 from cells. Phase C's cross-validation against the per-state 0–20 total will absorb this as up-to-±2-state-per-band noise.

5. **Score 0/1/2 anchors for Cat 1 don't exist.** The projection returns 0 only if NOT (lobbyist_identified AND client_identified) — which is rare-to-nonexistent across the 50 states. The article describes no per-state score-0/1/2 examples for Cat 1. **Effectively: Cat 1's score range as projected from cells is {3, 4}**, contributing ≤ 1 point of variation to the per-state total. This is the irreducible OpenSecrets-judgment portion the recheck note flagged.

6. **Partial points on Cat 4 sub-facets.** OpenSecrets allows partial points on each sub-facet but doesn't quantize. The 3-tier internal representation (0 / 1 = partial / 2 = full) projects to OpenSecrets's 0 / 0.5 / 1 (for lists) or 0 / 1 / 2 (for search and downloads). Phase C may need to calibrate whether OpenSecrets's "partial" actually corresponds to "1" (e.g., a portal with PDF-only spending reports might get partial credit for downloads, projecting to 1, but the OpenSecrets coder might have awarded 0.5 or 1.5 in practice). The worked-examples CSV has no per-sub-facet partial-point examples; this is calibration-by-distribution.

7. **The OpenSecrets state-map widget JS pull (recheck note open option) is the next unlock if Phase C validation falls short.** Pulling per-state per-category numerical scores from the widget would convert from "validate per-state 0–20 total only" to "validate per-state per-category 4 × 0–5 cells = 200 ground-truth values." That would let us partial-credit the projection per-category and identify which categories the projection systematically over- or under-shoots. Flagged here for future activation; not done this session.

## What OpenSecrets doesn't ask that other rubrics will

OpenSecrets is a 4-category surface rubric. It does not read: per-target-type lobbying definitions (CPI #196 / PRI A-family), itemization granularity (Sunlight #2 / PRI E1f / HG Q11-15), bill-or-action identifier disclosure (Sunlight #1 / HG Q5/Q20 / FOCAL contact_log.11), threshold values (any of the three threshold types), enforcement/audit (CPI #207-209), prohibitions / revolving door / cooling-off (Newmark prohib.* / HG Q41-48), per-meeting contact log (FOCAL contact_log.*), open-data-format granularity beyond binary downloadable (FOCAL openness.3 fine-grained), historical-data archival (FOCAL openness.8), unique identifiers (FOCAL openness.6 / LobbyView UUIDs).

These rows enter compendium 2.0 from the other rubrics' projection mappings, not OpenSecrets's. OpenSecrets's contribution is **finer ordinal granularity on Cats 2 and 4 — and the in-session/out-of-session cadence split** — relative to the binary-tradition rubrics.

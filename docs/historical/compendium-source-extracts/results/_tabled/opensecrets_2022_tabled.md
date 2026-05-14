# OpenSecrets 2022 — TABLED (not currently validating)

## Status

**TABLED 2026-05-13.** Not dropped permanently. This is research — decisions stay reversible. The OpenSecrets 2022 scorecard is set aside from the contributing-rubric set for the `compendium-source-extracts` branch pending the conditions listed under [Reinstatement triggers](#reinstatement-triggers) below.

## Why tabled

**Reason: we do not have a published scoring definition that lets us project from compendium cells to OpenSecrets's per-category scores deterministically.**

The branch's success criterion (`STATUS.md` ⭐ block) is that source rubrics serve as **sanity checks** on extraction accuracy via projection functions `f_rubric(compendium_cells_for_state_year) → rubric_score`, validated against published prior data. For this to work, the per-category scoring rule must be reproducible from extracted cells. OpenSecrets 2022 doesn't meet that bar:

- **Cat 1 (lobbyist/client disclosure, 0–5):** Anchors only at score 3 (baseline = both identified) and score 4 (separate registrations). Scores 0, 1, 2, 5 have no published anchor. The article describes scores below baseline as "depending on individual circumstances."
- **Cat 2 (compensation, 0–5):** Anchors at 0 (no disclosure), 4 (baseline = full + linked to individual lobbyists), 5 ("exceeds baseline" — what counts as exceeding is undefined). Scores 1–3 are "depending on the level of compensation disclosed" with two mentioned deficiency modes (ranges; unlinked to individuals) but no per-tier mapping.
- **Cat 3 (timely disclosure, 0–5):** Anchors at 4 (monthly-in-session / quarterly-otherwise) and 5 (monthly year-round). Scores 0–3 are "depending on individual circumstances."
- **Cat 4 (public availability, 0–5):** Sub-facet weights are explicit (search=2, downloads=2, lists=1) but partial-credit boundaries are not quantized; OpenSecrets explicitly acknowledges this category is "more subjective."

Also: no inter-coder reliability reported; no per-state per-category numerical scores in the published article text (only per-state 0–20 totals + descriptive bands like "16+" = top tier, "<10" = bottom tier; per-category numerics are behind a JS-rendered state-map widget on opensecrets.org/state-lobbying that is not webfetch-accessible).

### Decision history

1. **2026-05-07 (Phase A1 original audit)** — DROP verdict. Documented at [`../20260507_opensecrets_atomic_audit.md`](../20260507_opensecrets_atomic_audit.md). The audit correctly identified that OpenSecrets's atomic items can't be deterministically computed from atomic compendium-cell values via a documented scoring rule.
2. **2026-05-07 (recheck)** — Overturn. Documented at [`../20260507_opensecrets_recheck.md`](../20260507_opensecrets_recheck.md). The recheck applied a weaker criterion: "few-shot calibratable from worked examples + statistical anchors" instead of "deterministic projection from cells." Worked examples were extracted into [`../opensecrets_worked_examples_2022.csv`](../opensecrets_worked_examples_2022.csv).
3. **2026-05-12 (Phase B mapping attempt)** — Mapping doc drafted; preserved as [`opensecrets_2022_projection_mapping_superseded.md`](opensecrets_2022_projection_mapping_superseded.md) (sibling file in this `_tabled/` directory). The mapping surfaced that Cat 1's projection emits only {3, 4} from cells, and Cats 2/3's partial-credit (scores 1–3) requires calibration-by-distribution rather than deterministic projection — both consistent with the original Phase A1 audit's structural finding.
4. **2026-05-13 (reversal)** — Original Phase A1 verdict re-established. The recheck's "few-shot calibratable" criterion is softer than the branch's projection-vs-published bar; meeting the softer bar doesn't actually serve the branch's stated success criterion. Tabled rather than permanently dropped because the rubric may become projectable later (see reinstatement triggers).

## Reinstatement triggers

Any of these would re-qualify OpenSecrets 2022 as a contributing rubric. Drop is reversible.

1. **OpenSecrets publishes a v2 scorecard with explicit per-category sub-anchors.** E.g., for Cat 2: "score 1 = compensation in ranges aggregated across lobbyists; score 2 = ranges per-lobbyist; score 3 = exact dollar but aggregated; score 4 = exact per-lobbyist (baseline); score 5 = exact per-lobbyist + direction-of-lobbying flag (exceeds)." With anchors like that, deterministic projection becomes writable.
2. **Per-state per-category numerical data is released.** OpenSecrets references a "complete list" at line 195 of the article but only the 0–20 total per state is in the text. The per-category 0–5 breakdowns are behind a JS-rendered state-map widget that is not webfetch-accessible. **A manual browser pull of the widget would supply 50 states × 4 categories = 200 ground-truth cells** — that alone would convert the rubric to a validation target (calibration by distribution becomes calibration by per-cell ground truth).
3. **A third party reverse-engineers OpenSecrets's scoring into explicit per-tier rules and publishes it.** This would be a derived rubric, not OpenSecrets, but would cover the same conceptual ground.
4. **A different framing of OpenSecrets's contribution justifies inclusion.** E.g., if the project later finds value in cross-state aggregate-rank-order validation (Spearman correlation between projection-rank-order and OS-rank-order at per-state 0–20 totals), OpenSecrets could re-enter at that weaker level of contribution — but this is **not** what the branch's stated success criterion currently rewards.

## OS-distinctive row candidates (TABLED, not dropped)

The Phase B mapping attempt surfaced three statutory observables that OpenSecrets's scoring rule would have read but **no other rubric in our current contributing set reads at the same granularity**. Per user direction 2026-05-13: these are tabled here, not removed from consideration. Two paths to reinstatement:

- **(a) Organic pickup.** If another rubric mapping (Newmark 2017 / 2005, Opheim, HiredGuns, FOCAL, LobbyView, or a future addition) reads any of these observables, that rubric's mapping introduces the row to compendium 2.0 cleanly. No special handling needed.
- **(b) Project-internal need.** If the compendium-2.0 design pass concludes a row captures a real statutory distinguishing case that we want in the data infrastructure regardless of whether any current rubric validates it, the row enters as **unvalidated** (no projection-vs-published anchor). The success-criterion's "minimum compendium" framing penalizes unvalidated rows — so this path is the exception, not the default.

If neither path fires, the row stays tabled. We **revisit** during compendium 2.0 row-set freeze; we don't permanently drop.

### Candidate 1: `separate_registrations_for_lobbyists_and_clients`

- **Statutory observable:** Does the state require lobbyists AND their clients (principals) to file independent registration forms, vs a single registration form where the lobbyist names their clients within?
- **Where OpenSecrets read this:** Cat 1, the score-4 bonus over score-3 baseline. Article line 197-199: "the baseline score was three and states that require separate registrations for the lobbyists and clients were assigned a four."
- **Cross-rubric pickup possibilities:**
  - **LobbyView** has separate `registrant_uuid` and `client_uuid` schema fields at the federal level. The Phase B LobbyView mapping (schema-coverage rubric, tackled last) may justify this row as a state analog of LDA's lobbyist/client distinction.
  - **Newmark / HG / PRI** don't directly read this — they read registration existence but not the bookkeeping split.
- **Project-internal justification (if path (b) fires):** real distinguishing case in state statutes (some states do require both; OpenSecrets's worked example for OK = single-registration baseline). Worth tracking for data infrastructure even without validation.

### Candidate 2: `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges`

- **Statutory observable:** When compensation is disclosed, is the disclosed value an exact dollar amount, or a range (e.g., "$10,000–$25,000")?
- **Where OpenSecrets read this:** Cat 2, partial-credit (scores 1–3). Article line 78–81: "Seven more states only require partial reporting with compensation either reported in ranges or not linked to individual lobbyists."
- **Cross-rubric pickup possibilities:**
  - **HG Q13** reads compensation existence (binary), not exact-vs-ranges granularity.
  - **Newmark 2017 / 2005, PRI, CPI, Sunlight, FOCAL** read compensation existence and/or per-employer breakdown but not exact-vs-ranges.
  - **LobbyView** has an `amount` field rounded to nearest $10,000 at the federal level — a federal-statute-level "ranges" answer to this question.
- **Project-internal justification (if path (b) fires):** real distinguishing case; some states require exact dollar amounts, others require ranges. The distinction matters for data-quality downstream (range data degrades aggregate spending estimates).

### Candidate 3: `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate`

- **Statutory observable:** When compensation is disclosed, is it disclosed per-individual-lobbyist (one figure per lobbyist), or aggregated across all lobbyists at a firm/principal (one figure per firm)?
- **Where OpenSecrets read this:** Cat 2, partial-credit (scores 1–3). Article line 80–81: "...not linked to individual lobbyists."
- **Cross-rubric pickup possibilities:**
  - **Newmark 2017's `disclosure.compensation_by_employer`** reads per-employer breakdown — distinct concept (per-CLIENT split, not per-LOBBYIST split). A multi-lobbyist firm could disclose per-client without per-lobbyist split.
  - **HG Q13 / Q27 / PRI E2f_i / Sunlight #5** read compensation existence at the firm level.
  - **LobbyView** at the federal level reports per-LDA-registrant (firm), not per-lobbyist — so this row is a state-level finer granularity than LDA itself.
- **Project-internal justification (if path (b) fires):** real distinguishing case; the per-lobbyist split is what enables individual-lobbyist-level analysis (which lobbyists are most paid; which lobbyists work on which issues). Without this row, the compendium can't represent a real and consequential statutory distinction.

## Cadence in-session/out-of-session split — NOT TABLED, will be handled by Opheim

The Phase B mapping attempt also proposed a 2-row enum split for reporting cadence (`lobbyist_spending_report_filing_cadence_in_session` / `_out_of_session`). This was framed as OpenSecrets-distinctive but **Opheim 1991 also reads this split** (as a binary: monthly-during-session OR both-in-and-out vs less). When the Opheim projection mapping is written, this row family enters compendium 2.0 through Opheim's mapping. No tabling needed.

The CPI mapping's [Open Issue 4](../projections/cpi_2015_c11_projection_mapping.md) (PRI's atomic-binary cadence representation vs CPI's enum representation) is still open and will be resolved during compendium 2.0 row-set freeze; the OpenSecrets attempt added the in-session/out-of-session axis to that open issue but didn't resolve it.

## Cat 4 sub-facet rows — not tabled; fold into CPI / FOCAL / HG

The Phase B mapping attempt also identified Cat 4 sub-facets (search, downloads, lists) as candidate rows. On review these fold into existing rows from other rubrics' mappings:
- Search granularity → CPI #205 (compound), FOCAL `openness.5`, HG Q31/Q32 (4-tier ordinal).
- Download granularity → CPI #206 (5-tier `lobbying_data_open_data_quality`), FOCAL `openness.3`/`openness.4`, HG Q31/Q32.
- Lobbyist/client list discoverability → FOCAL `openness.1`, HG Q35-Q37 (different shape).

No new compendium rows needed for these. The Cat 4 portal observables are already covered by the existing CPI / FOCAL / HG mappings.

## Files preserved as evidence

- [`../20260507_opensecrets_atomic_audit.md`](../20260507_opensecrets_atomic_audit.md) — original Phase A1 DROP audit. Structurally correct; re-validated by 2026-05-13 reversal.
- [`../20260507_opensecrets_recheck.md`](../20260507_opensecrets_recheck.md) — overturn under weaker criterion (now amended with reversal note).
- [`../items_OpenSecrets.tsv`](../items_OpenSecrets.tsv) — 7-row atomic-item extract. Kept per Phase A1 instruction (do not delete); the rows are valid per-paper extracts even though the rubric is tabled as a contributor.
- [`../items_OpenSecrets.md`](../items_OpenSecrets.md) — companion methodology note. Kept.
- [`../opensecrets_worked_examples_2022.csv`](../opensecrets_worked_examples_2022.csv) — 18-row worked-examples calibration set. Kept; could become directly relevant under reinstatement trigger 2 (state-map widget pull supplements the worked examples to per-cell-ground-truth).
- `papers/text/OpenSecrets_2022__state_lobbying_disclosure_scorecard.txt` — source article. Kept (untouched).

## Implications for Phase B order

Phase B remaining count: **6 rubrics** (was 7).

Locked Phase C order (which Phase B mirrors), with OpenSecrets removed:

1. ~~OpenSecrets 2022~~ — **TABLED**, this doc.
2. **Newmark 2017** (19 items) — next.
3. Newmark 2005 (18 items).
4. Opheim 1991 (22 items, disclosure-side only) — will introduce the in-session/out-of-session cadence row family.
5. HiredGuns 2007 (47 items, disclosure-side only).
6. FOCAL 2024 (50 items, weighted aggregation).
7. LobbyView (46 schema fields — schema-coverage rubric, different shape). May introduce candidate 1 (`separate_registrations_for_lobbyists_and_clients`) via the LDA registrant/client UUID analog.

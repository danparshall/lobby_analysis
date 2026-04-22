# Snapshot Sufficiency Audit — 2026-04-13

**Question:** Are the portal snapshots produced by the PRI Stage-1/Stage-2 collection (documented at `docs/active/pri-2026-rescore/results/20260413_stage1_stage2_collection_summary.md`, 50/50 states, ~350 MB, 981 artifacts) sufficient to begin scoring all 50 states against both the PRI 2026 rubric (22 accessibility + 37 disclosure-law = 59 items) and the FOCAL 2024 rubric (50 indicators), or do we need additional fetches before pipeline work starts?

**Short answer:** Sufficient to begin scoring the ~25 "clean-capture" states against both rubrics. Insufficient for ~13 SPA/partial-WAF states (portal-UX items can't be scored from curl snapshots of SPA shells). Insufficient for AZ and VT (WAF blocks everything). **Recommended path: begin pipeline build and pilot on clean-capture states immediately; run Playwright supplementation as a parallel workstream for SPA/WAF states.**

## Method

Read the PRI Stage-1/Stage-2 collection summary and cross-referenced it against:

1. PRI 2026 accessibility rubric items Q1–Q22 + Q9 sub-items Q9.1–Q9.15 + Q13 sub-items + Q15, Q16a/b (snapshot URL-level items).
2. PRI 2026 disclosure-law rubric (schema-view items: satisfiable from statute text + form PDFs + registration HTML).
3. FOCAL's 8 categories, particularly Openness (9 indicators) which requires portal UX, vs. the other 7 categories (41 indicators) which can be satisfied from schema-view evidence.

Spot-checked per-state manifests for AZ (near-empty), KY (richest, 42 files), and the collection summary's own per-state tier labels.

## Coverage tiers (from PRI collection summary)

| Tier | States | Count | Usable evidence |
|---|---|---|---|
| Clean static capture | NY, TX, PA, MN, KY, VA, OH, AR, ME, SC, AK, AL, CO, GA, HI, IA, IN, LA, MD, MO, MS, MT, NE, NJ, OR, RI, TN, UT, WI, WV, WY (approx) | ~25–30 | Rich HTML + PDFs, often actual bulk data dumps. NY 40 MB, TX 35 MB, PA 64 MB. Form PDFs captured incidentally in many cases. |
| SPA-shell only (curl returned bootstrap, not UI) | ID, ND, SC, GA, NM, ME, MI, AR, IN, PA (approx — some overlap with clean tier, see note below) | ~10 | Bootstrap HTML (useless for UX scoring), but statutes/FAQ/guides/data dictionaries from sibling captures often usable. |
| Partial WAF blocks | MA, NH, MI, CT, DE, KS, CA, NC, IL | ~9 | Some seeds skipped, but documentation/statute content captured on companion hosts. |
| Near-empty | AZ (0/12 seeds), VT (1/9 seeds) | 2 | Nothing portal-derived. Must score from statute text or records requests. |

**Note on SPA/clean overlap:** ME and PA appear in both the clean-capture and SPA lists. What's captured statically (manuals, FAQ, bulk files) is rich, but the filer/search UI is SPA-rendered and invisible to curl. Implication: these states are *partially scoreable from what we have* — schema-view items yes, portal-UX items no.

## Sufficiency by rubric item family

### Well-served by current snapshots (score now on clean tier)

- **Statute / legal-text items** (PRI A-series, PRI B1/B2, FOCAL Scope 1.1–1.4). Answered from captured legal-text pages, FAQs, and official guides.
- **Registration-schema items** (PRI C-series, FOCAL Descriptors 4.1–4.6, Revolving door 5.1, Relationships 6.1–6.4). Answered from captured registration HTML + form PDFs (where present).
- **Expenditure-schema items** (PRI D-series, FOCAL Financials 7.1–7.11). Answered from captured expenditures HTML + form PDFs.
- **Bulk-download presence** (PRI Q10, FOCAL Openness 3.4). Answered from bulk_download role captures; rich states have actual data files.
- **Data-dictionary presence** (PRI Q13 and sub-items, FOCAL implicit). Answered from data_dictionary role captures.
- **Statute-timeline items** (PRI Q16 timestamp/freshness, FOCAL Timeliness 2.1–2.3). Schema-view — answered from statute or regulation text.

### Under-served without Playwright supplementation

- **Portal-UX items** (PRI Q2, Q3, Q4, Q9 sub-items that test actual search/filter/sort UI; FOCAL Openness 3.5 "searchable, simultaneous sorting with multiple criteria", 3.6 unique identifiers, 3.7 linked data).
- **Actual record inspection** (confirming that fields in the schema are populated in practice). Distinct from schema-view scoring — useful for verification layer, not required to apply either rubric first-pass.
- **Portal-behavior items** (PRI Q12 no-auth-barrier, Q11 open API presence). Partially answered from captured pages, but confirming absence of a hidden API surface requires browser-level inspection.

### Not served at all (AZ, VT)

Score these from statute text + any out-of-band evidence (legal records requests, third-party databases) or accept nulls with `notes="portal inaccessible; see AZ/VT snapshot manifest"`.

## FOCAL-specific gaps beyond PRI's scope

- **Form PDFs.** Incidental capture in some states' link sweeps (KY has `page_14.pdf`, `page_15.pdf`, `faq_02.pdf`; several other clean-tier states similar). No state has deliberate, consistent form-PDF capture. Impact: FOCAL Descriptors / Revolving door / Relationships / Financials score some states well (where form PDFs happened to get caught) and others poorly (where they didn't). **Recommendation: spot-check form-PDF coverage per state during the FOCAL pilot (Phase 4 of the FOCAL scoring plan). If patchy, add a small targeted re-fetch rather than a blanket extension pass.**
- **Contact-log landings.** Also incidental. Most US states don't have contact logs (automatic 0 for FOCAL category 8), so the absence is informative in itself. No action needed.
- **Sample data files / actual filings.** The heavy-MB clean states (NY, TX, PA, MN, KY) already captured bulk ZIPs/PDFs. Others did not. Impact: verification-layer scoring (does field X actually get populated?) is state-dependent, but first-pass schema-view scoring doesn't require this.

## Cross-rubric implication

The evidence surfaces are **largely shared between PRI and FOCAL** because the two rubrics overlap two-dimensionally (PRI 37 disclosure-law ↔ FOCAL 41 statutory-content; PRI 22 accessibility ↔ FOCAL 9 Openness). A single pass over a state's snapshot produces evidence usable by both rubrics' scorers. This validates the architectural decision in `plans/20260413_focal_50_state_scoring.md` to reuse PRI's snapshot infrastructure rather than running parallel snapshot protocols.

## Recommendation

**Treat the snapshot as sufficient-for-now.** Proceed with pipeline build immediately rather than delaying for Playwright supplementation. Concretely:

1. Build the rubric-agnostic scoring pipeline once (PRI Phase 4 / FOCAL Phase 3 are the same codebase, different rubric CSVs as input).
2. Pilot on CA + CO + WY (all in clean-capture tier — CA's partial-WAF situation is a feature, not a bug: it stress-tests how the pipeline handles auth-walled evidence).
3. Run the full set of clean-capture states on both rubrics.
4. In parallel, run a Playwright supplementation workstream to catch the ~13 SPA/WAF states. As each state's Playwright snapshot lands, re-score it with the existing pipeline (adding, not replacing, the curl-era snapshot).
5. Score AZ and VT from statute text with `evidence=legal_text_only` and expect those to carry more nulls than scored items.

**Risks of this path:**

- Collaborators reviewing partial scoring output may mis-interpret "not yet scored due to Playwright gap" as "scored 0 / weak portal." Mitigation: explicit `coverage_tier` column in the output CSV per state (clean / spa_pending_playwright / waf_partial / inaccessible), surfaced prominently in the summary deliverable.
- The ~10% self-consistency threshold from the PRI plan may fire spuriously if SPA states get pipeline-fed with empty shells. Mitigation: gate Playwright-pending states out of the self-consistency check at the orchestrator level; run them only after their snapshot is adequate.

**Risks of the alternative (Playwright-first):**

- 1–2 weeks of wall-clock delay before any scored output. Collaborators can't begin methodology review until every state is in.
- Playwright stealth engineering is itself a research task for some of these portals (Incapsula, Cloudflare, Akamai are actively adversarial); sinking that time before first pilot is front-loading risk.

## What this audit does not do

- Does not score any item. Sufficiency is assessed in the abstract from evidence-surface coverage, not by attempting a real scoring pass.
- Does not validate the PRI agent's per-state tier assignments. Those are taken at face value from the Stage-2 collection summary; spot-checks of AZ (near-empty) and KY (rich) confirmed the extremes, but middle-tier tier assignments were not re-audited.
- Does not resolve whether form PDFs captured incidentally are the *correct* form PDFs (e.g., registration vs. expenditure vs. amendment). The FOCAL pilot (3 states) will surface this; if a problem appears, a targeted form-PDF re-fetch lands before the full run.

## Next step

Per this audit and the 2026-04-13 decision: proceed with **option (1) — treat snapshots as sufficient-for-now, build the pipeline, pilot on clean states, Playwright-supplement in parallel.** The immediate next task is to kick off PRI Phase 4 / FOCAL Phase 3 pipeline build on the `pri-2026-rescore` branch (or a jointly-scoped pipeline branch if both rubrics share code).

# 2026-05-06 — Compendium assembly via embeddings (te3-large) + first candidate item set

**Branch:** `compendium-source-extracts`
**Status:** In flight; closing this convo to hand off to a parallel `comp_assembly_via_regex` session
**Originating convo:** [`convos/20260503_pm_acquisition_and_descriptives.md`](20260503_pm_acquisition_and_descriptives.md) (specifically its 2026-05-06 post-session continuation block, which committed `tools/embed_cross_rubric.py` for desktop execution)
**Originating plan:** [`plans/20260504_compendium_2_0_synthesis.md`](../plans/20260504_compendium_2_0_synthesis.md) — this session executed the embedding pass that the synthesis plan flagged as the next experiment to run, and produced the first candidate item set as input to the (still-deferred) compendium-2.0 design plan.

## Summary

Resumed the cross-rubric clustering work that the 2026-05-03 (pm) session had blocked on (sandboxed env couldn't reach HuggingFace). Switched embedding provider to OpenAI `text-embedding-3-large` (3072-dim, ~$0.002 for 509 items). Extended `tools/embed_cross_rubric.py` with a `--provider {openai, sentence-transformers}` flag and saved both the similarity matrix and the raw vectors so downstream analysis can re-cluster, project, or visualize without re-calling the API.

Used the embeddings to produce the first candidate item set for compendium 2.0 — `comp_assembly_embed_v1.tsv` (126 items: HG + FOCAL + Newmark2017 + 10 Opheim coverage extensions) and then `comp_assembly_embed_v2.tsv` (209 items: v1 + all 83 PRI 2010 atomic items, added per explicit user clearance to use PRI as a non-default coverage source). The TSV preserves full provenance (paper_id + indicator_id) and tags each non-core extension with `compendium_role` + `extension_rationale` + `best_core_match_*` so a reviewer can see why each item was pulled in.

Late-session correction from the user: artifact names should describe the **assembly method**, not the desired conclusion ("comprehensive_set" → "comp_assembly_embed"). Renamed all relevant files and saved the lesson to memory. The next session will produce a parallel `comp_assembly_via_regex` candidate set; the actual compendium 2.0 is whatever falls out of comparing/reconciling those candidates, not what any single method produces.

## Topics Explored

- **OpenAI te3-large embedding run** over the 509 rubric atomic items from `cross_rubric_items_clustered.csv`. Saved vectors (`embed_vectors__openai__text-embedding-3-large.npy`, 6.25 MB), index (`.csv`, 95 KB), similarity matrix (`.npy`, 1 MB), and threshold-cluster artifacts. Reproducibility caveat: OpenAI embeddings are not bit-deterministic across runs; cluster counts can shift by ~1 at the same threshold.
- **Threshold tuning.** Single-link clustering produces a giant 254-item mega-cluster below sim=0.62 (chaining via the European-tradition mega-cluster). Sweet spot at sim ≥ 0.68 (28 clusters / 106 items / 10 spanning ≥3 rubrics / 3 spanning ≥5 rubrics). At sim ≥ 0.66 the structure is similar but with slightly more bridging. Above 0.70 signal degrades.
- **Tradition-tagged cluster analysis.** Each rubric tagged state (US-state-tradition: Opheim, Newmark2005/2017, HiredGuns, Sunlight, OpenSecrets, CPI_2015) / cross (FOCAL, Lacy-Nichols 2024) / euro (everything else: AccessInfo, CouncilEurope, ALTER_EU, IBAC, McKayWozniak, SOMO, TI_2016, GDB, Carnstone). Categorized each cluster as STATE-only / EURO-only / CROSS / mixed-with-FOCAL.
- **Coverage analysis: how well does HG + FOCAL + Newmark2017 cover the rest of the state-tradition rubrics?** For each non-core atomic item, computed cosine sim to argmax core item; binned by sim to identify covered / partial / uncovered.
- **Normalization side-experiment.** Built `tools/normalize_state_items.py` to strip per-rubric framing prefixes (e.g. HG "Is X required?" → "X required"; Newmark2017 "Disclosure required: X" → "X (disclosure)"). Re-embedded the 134 normalized state items and re-clustered. Modest tightening of within-tradition clusters; not load-bearing for the v1/v2 assembly which uses raw embeddings.
- **PRI 2010 inclusion.** User explicitly cleared PRI for inclusion as a non-default coverage source: *"first let's go ahead and include all PRI items, now that we aren't locked onto them."* Pulled all 83 PRI atomic items (22 accessibility + 61 disclosure-law) from the historical pri-2026-rescore transcriptions (not re-extracted from paper text). Tagged `ext_pri_2010_*` to make the non-default status durable in the data.
- **Naming reframe.** Files initially named `comprehensive_set.tsv` / `_v2`. User pushed back: that pre-claims an answer the artifact doesn't have, and there will be parallel assemblies via other methods. Renamed to `comp_assembly_embed_v{1,2}.{tsv,md}`. Saved lesson to memory.

## Provisional Findings

- **Within-tradition consolidation works well.** At sim ≥ 0.68: state-tradition produces 10 internal clusters (notably: HG + Newmark2017 + Opheim + Sunlight on lobbyist-qualification thresholds, 8 items × 4 rubrics; 5 separate Newmark2005↔Newmark2017↔Opheim 3-rubric consolidations on definition triggers + expenditures-benefiting officials). European-tradition produces 14 internal clusters (notably: AccessInfo + CouncilEurope + Carnstone + IBAC + TI_2016 on "what to register," 12 items × 5 rubrics; AccessInfo + CouncilEurope + FOCAL + GDB + TI_2016 on "open-data accessibility," 11 items × 5 rubrics). Substantial improvement over the 2026-05-03 TF-IDF baseline (which produced only 1 cluster spanning ≥3 rubrics, "lobbyist definition," and only because the literal word "lobbyist" appeared in all five).
- **Cross-tradition (state↔euro) bridging is sparse even at frontier embedding quality.** Only 1 cross-tradition cluster forms at sim ≥ 0.68: AccessInfo + FOCAL + HiredGuns + OpenSecrets + Opheim on "timely disclosure / reporting frequency" (8 items × 5 rubrics). One additional state↔euro pair at sim 0.69-0.70 (Newmark2017 contingent compensation ↔ IBAC success fees). Many additional state↔euro pairs cluster at sim 0.60-0.66 (e.g. HG cooling-off ↔ CouncilEurope cooling-off at 0.652) but are blocked from the 0.68 cluster cut by single-link chaining considerations.
- **The European↔state vocabulary divide is structural, not just lexical.** Items don't bridge cross-tradition because each rubric organizes its items around a different conceptual frame: declarative-disclosure-inventory (Newmark), spending-report-itemization-audit (HG), normative-completeness (FOCAL), meeting-record-schema (TI_2016), public-official-duty (AccessInfo). The framing language is systematically different (every Newmark item is "Disclosure required: X"; every HG item is "Is X required?"), AND the organizing axis is different. Stripping framing helps within-tradition but not cross-tradition.
- **HG + FOCAL + Newmark2017 cover the state-tradition well.** Over 184 state+cross atomic items, the 126-item set (which is HG + FOCAL + Newmark + 10 Opheim) covers 79% at sim ≥ 0.70, 84% at sim ≥ 0.65, 89% at sim ≥ 0.55. Real gaps are: (1) Opheim's 6-item enforcement battery + 2-item income-disclosure pair + 2 borderline items — pulled into the 126-item set as `ext_opheim_*`. (2) Newmark2005 and Sunlight short-label artifacts (e.g. "time standard", "Document Accessibility") — these are concepts already in the set but the embedding mismatches due to short text. Normalization would close these.
- **CPI_2015 is mostly out of scope.** The CPI 2015 SII is a multi-domain integrity scorecard. 15 of 16 items are non-lobbying domains (Procurement, State pension fund management, Internal auditing, Judicial accountability, etc.). Only "Lobbying disclosure" is lobbying-specific, and that one bridges to AccessInfo's "Lobbyist identity" at sim 0.622.
- **European-tradition rubrics are largely out of US-state-lobbying-disclosure scope.** Most uncovered items are genuinely outside what US states require to be disclosed: AccessInfo's right-to-participate / complaint-mechanism items, SOMO's Dutch-specific consultation reform items, TI_2016's EU MEP declaration items, ALTER_EU's EU-specific operational details (€10K bandwidths, FTE calculation guidelines), Carnstone's corporate-side internal whistleblowing. A small subset (e.g. IBAC's MP-meeting-disclosure cluster, Carnstone's lobbyist-control items) might be worth flagging as `cmp_*` coverage-comparison reference in a future pass; not in this round.
- **Methodological: artifact names should describe method, not conclusion.** Naming a candidate output `comprehensive_set.tsv` pre-claims a finality the artifact doesn't have. The right name pattern is `comp_assembly_<method>_v{n}.{tsv,md}`. The comprehensive set is whatever falls out of reconciling multiple methods' candidates, not what any single method produces.

## Decisions

| topic | decision |
|---|---|
| Embedding provider | OpenAI `text-embedding-3-large` for the production run; sentence-transformers MiniLM kept as offline fallback in the same script. |
| Embedding artifact preservation | Save the raw vectors + index alongside the similarity matrix, so downstream re-clustering / UMAP / centroid work doesn't require API re-calls. |
| Threshold for cluster reporting | sim ≥ 0.68 as the primary read; lower thresholds (0.65, 0.66) shown for cross-tradition near-bridges that fall just below 0.68. |
| `comp_assembly_embed_v1` content | HG (47) + FOCAL (50) + Newmark2017 (19) + 10 Opheim items (6 enforcement + 2 income + 1 oversight + 1 catch-all). 126 items total. |
| `comp_assembly_embed_v2` content | v1 + all 83 PRI atomic items (22 accessibility + 61 disclosure-law). 209 items total. PRI sourced from historical pri-2026-rescore transcriptions, NOT re-extracted from paper text. |
| PRI status update | Partial clearance recorded 2026-05-06: PRI may be ADDED to compendium-2.0 candidate sets as `ext_pri_2010_*` coverage extension. Still blocked: structural anchoring, "match PRI" calibration, PRI-shaped row-frame seeding. The STATUS.md ⛔ block remains in force for everything else. |
| File naming | `comp_assembly_<method>_v{n}.{tsv,md}` — names by method, not by conclusion. Saves the slot for parallel assemblies (`comp_assembly_via_regex` next). |
| Old (141-row PRI-shaped) compendium | Not a target / baseline / benchmark for compendium-2.0 work. Memory entry added. |

## Mistakes recorded

1. **Volunteered comparison against the old compendium when user asked a sizing question.** User asked "how large is the compendium" referring to the 126-item v1; assistant proactively included a comparison to the old 141-row compendium. User redirected. Memory `feedback_dont_volunteer_comparisons.md` added.
2. **Named files `comprehensive_set.tsv` / `_v2.tsv`** when assembling candidates via one specific method. User pushed back: that pre-claims THE answer when it's one method of several. Memory `feedback_name_by_method_not_conclusion.md` added; files renamed to `comp_assembly_embed_v{1,2}.{tsv,md}`.
3. **Initial coverage analysis missed that the user wanted "% of each parent rubric covered by the set"** — assistant first reported within-set dedup statistics. User redirected to the right framing. Recovered same turn.
4. **Worktree-venv mismatch** caused initial `uv run` calls to load the main worktree's venv (which lacked openai/pandas/numpy). The pre-existing memory `feedback_pytest_in_worktree.md` had flagged this; assistant fixed by `unset VIRTUAL_ENV && uv sync && uv pip install` against the worktree's local venv.
5. **`.env.local` parsing** — file uses `KEY = value` format with spaces around `=`, which `set -a; source` rejects. Fixed by extracting the key with a Python regex one-liner. Worth noting for future sessions.

## Results

- Embedding artifacts (full corpus, raw):
  - [`results/embed_vectors__openai__text-embedding-3-large.npy`](../results/embed_vectors__openai__text-embedding-3-large.npy) — 509×3072 float32, L2-normalized
  - [`results/embed_index__openai__text-embedding-3-large.csv`](../results/embed_index__openai__text-embedding-3-large.csv) — row-aligned with `.npy`
  - [`results/embed_similarity_matrix__openai__text-embedding-3-large.npy`](../results/embed_similarity_matrix__openai__text-embedding-3-large.npy) — 509×509 cosine sim
  - [`results/embed_clusters_full__openai__text-embedding-3-large.txt`](../results/embed_clusters_full__openai__text-embedding-3-large.txt) — human-readable cluster dump per threshold
  - [`results/embed_clusters_at_thresholds__openai__text-embedding-3-large.csv`](../results/embed_clusters_at_thresholds__openai__text-embedding-3-large.csv) — per-threshold summary stats
- Embedding artifacts (state-only, normalized — side experiment):
  - [`results/cross_rubric_items_state_normalized.csv`](../results/cross_rubric_items_state_normalized.csv) — 134 items with raw + normalized text
  - [`results/state_normalized/embed_*__openai__text-embedding-3-large.{npy,csv,txt}`](../results/state_normalized/) — 134-item embedding artifacts
- PRI items in the standard schema:
  - [`results/items_PRI_2010.tsv`](../results/items_PRI_2010.tsv) — 83 items (22 accessibility + 61 disclosure-law) sourced from `docs/historical/pri-2026-rescore/results/pri_2010_*_rubric.csv`
- Candidate item sets:
  - [`results/20260506_comp_assembly_embed_v1.tsv`](../results/20260506_comp_assembly_embed_v1.tsv) — 126 items × 13 cols
  - [`results/20260506_comp_assembly_embed_v1.md`](../results/20260506_comp_assembly_embed_v1.md) — assembly note
  - [`results/20260506_comp_assembly_embed_v2.tsv`](../results/20260506_comp_assembly_embed_v2.tsv) — 209 items × 13 cols
  - [`results/20260506_comp_assembly_embed_v2.md`](../results/20260506_comp_assembly_embed_v2.md) — assembly note (with PRI clearance recorded)
- Tools:
  - [`tools/embed_cross_rubric.py`](../../../../tools/embed_cross_rubric.py) — extended with `--provider {openai, sentence-transformers}` and tag-based output filenames
  - [`tools/normalize_state_items.py`](../../../../tools/normalize_state_items.py) — per-rubric regex framing-strip
  - [`tools/assemble_comp_embed.py`](../../../../tools/assemble_comp_embed.py) — assembler that produces `comp_assembly_embed_v*` from the source extracts + similarity matrix

## Plan produced

[`plans/20260506_comp_assembly_via_regex.md`](../plans/20260506_comp_assembly_via_regex.md) — handoff to next agent for the parallel regex/python assembly approach, scoped to USA-tradition rubrics only.

## Open Questions

1. The `ext_opheim_catchall` item (`disclosure.other_influence_peddling_or_conflict_of_interest`) is genuinely vague. Worth a second look on whether to keep it in the v2 candidate set.
2. Opheim `disclosure.legislation_supported_or_opposed_by_lobbyist` was skipped (best-match was lexical noise, but a true conceptual match exists in HG `Q5` subject-matter item). Worth a second look on whether HG's "subject matter on registration form" actually captures Opheim's "legislation approved or opposed in the reporting period."
3. The European-tradition rubrics produced two large within-tradition mega-clusters (12-item "what to register" + 11-item "open-data accessibility") that no US-state rubric bridges into. Not in compendium 2.0 scope, but: worth flagging which European-tradition concepts are systematically absent from US-state-tradition for the LANDSCAPE doc / future advocacy framing.
4. Coverage analysis used raw (un-normalized) embeddings throughout. Newmark2005 and Sunlight short-label gaps would close substantially under normalization. Worth re-running coverage after the regex assembly produces a normalized item corpus, to see if any additional Opheim items can be dropped from the v1 extension list.
5. PRI items are not in the embedding space (PRI was excluded from the 26-paper extraction round). A v3 of the embedding-based candidate set could embed the 83 PRI items and identify which are conceptually redundant with non-PRI rows, supporting a dedup decision. Cost: ~$0.001.

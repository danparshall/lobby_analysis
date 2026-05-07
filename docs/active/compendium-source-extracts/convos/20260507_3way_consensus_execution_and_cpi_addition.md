# 2026-05-07 — 3-way × 3-run consensus execution + CPI 2015 addition + projection-success criterion

**Plans executed:** [`plans/20260506_comp_assembly_3way_consensus.md`](../plans/20260506_comp_assembly_3way_consensus.md)
**Spawning artifact:** locked plan from 2026-05-06 evening, written for the implementing agent (possibly user-from-the-road) to execute the 9-subagent dispatch.

## Topics explored

- **Pre-flight check on plan ambiguities.** Three issues flagged before dispatch: CPI in-scope filter (TODO in step 1's script), M1 cluster file scope (was built over the full 509-item corpus including European-tradition rubrics), method-instability metric in step 5 (formula in plan reads as cross-method spread, not within-method instability). User accepted the M1 USA-only filter and asked for both stability metrics distinct.
- **CPI in-scope filter resolution.** Inspected the 16 CPI rows in `cross_rubric_items_clustered.csv` and per-paper `items_CPI_2015.tsv`. Only C11 ("Lobbying disclosure") is lobbying-specific; the other 12 categories + 3 illustrative sub-questions are different domains (FOIA, political financing, judicial accountability, etc.). Filter: `in_scope_cpi_ids = ['C11']`. 1 row survives, matches plan's expectation.
- **9-subagent parallel dispatch via Claude Code Task tool.** Sent 9 calls in one message: M1 cluster-anchored × 3, M2 blind × 3, M3 FOCAL-anchored × 3. Each subagent ran ~3-7 min, total wall clock ~9 min (well under the 15-30 min plan estimate).
- **Validation pass.** All 9 outputs valid: 252 rows lossless, no duplicate keys, group_id 1-to-1 with labels, no empty labels.
- **Consensus tool execution.** `tools/consensus_grouping.py` produced per-pair agreement counts over 1,034 co-grouped pairs, transitively-closed strict (≥8/9) and loose (≥6/9) clusters, human-review pile (3-5/9), and a method-instability report distinguishing within-method instability (per-method, across the 3 runs) from between-method disagreement (cross-method spread).
- **CPI 2015 C11 atomic items extracted.** User realized that the "CPI is 1 in-scope row" finding was actually an artifact of CPI's atomic items not being in our local archive — they live on CPI's methodology pages. Web search located CPI's official `PublicI/state-integrity-data` GitHub repo. `2015/criteria.xlsx` sheet ` Lobbying Disclosure` has 14 atomic indicators (#196-#209) organized into 5 sub-categories, with explicit de jure / de facto labels. Saved xlsx + scores.csv to `papers/`. Extracted 14 items into `results/items_CPI_2015_lobbying.tsv` in standard schema.
- **Compare/contrast against consensus output.** Per-item fold-in mapping for all 14 CPI items against the 24 strict + 21 loose-only consensus clusters. Result: 6 de jure items mostly fold into existing clusters; 8 de facto items map onto the v1.1 schema's `practical_availability` axis rather than creating new compendium rows.
- **Projection-success criterion landed (user direction).** A populated compendium 2.0 must be **sufficient input** to populate every source rubric's per-state score. This is a falsifiable round-trip test on real data: populate compendium → apply each rubric's projection logic → compare to published score. Match within tolerance ⇒ that rubric is covered. Failure ⇒ either compendium is missing a row, or projection logic is wrong. **Goal: minimize compendium size while keeping the floor (all 9 rubrics still project) intact.**

## Provisional findings

### From the 3-way consensus run

- **24 strict consensus clusters covering 63 items** (25% of the 252-item corpus). Mostly the within-tradition Newmark2005/2017/Opheim battery, predicted by the plan.
- **39 loose consensus clusters covering 106 items** (42%).
- **146 of 252 items (58%) appear in NO loose cluster.** 40 items were never co-grouped by any of the 9 runs.
- **468 pairs in the 3-5/9 human-review band** — the actual disagreement signal.
- **Per-method group counts and within-method spread:**
  - M1 cluster-anchored: 153 / 189 / 201 (spread 48; 19.1% within-method instability)
  - M2 blind: 159 / 180 / 195 (spread 36; 14.4% — most stable)
  - M3 FOCAL-anchored: 92 / 110 / 120 (spread 28 in counts, but 45.6% within-method instability — driven by big groups, where one item moving ripples across many pair-decisions)
- **Methodology surprise:** M1 (the cluster-anchored method) was supposed to be the most stable thanks to its shared embedding-cluster prior. It wasn't. Different runs treated the prior with very different weight (some used it as load-bearing, others ignored it). M2 blind was the most stable.
- **Per-paper consensus coverage is asymmetric:**
  - Newmark2005 (17/18) and Newmark2017 (17/19) are almost entirely in strict clusters — same author, near-identical wording, all methods agree.
  - PRI 2010 (3/83) is sparse — its atomic items are too fine-grained to find consensus matches across rubrics that don't enumerate at that resolution.
- **Top disagreement pairs are FOCAL ↔ PRI semantic mismatches** — filer-direction-and-granularity tradeoffs (e.g., per-meeting contact log vs. per-period reporting). M3 (FOCAL-anchored) merges by canonical fact; M1 (cluster-anchored, conservative) splits by filer/granularity. Both defensible; this is a compendium-2.0 design call.

### From the CPI 2015 C11 fold-in

- **14 atomic items in C11**, organized into 5 sub-categories (11.1-11.5). 6 de jure + 8 de facto.
- **CPI 2015 is far smaller and higher-abstraction than HG 2007** (14 vs 47 items). Confirms the per-paper-extract framing: CPI 2015 = HG 2007's successor at higher abstraction.
- **The de jure / de facto pairing is CPI 2015's distinctive contribution.** No other rubric in the corpus does this explicitly at item level. PRI 2010 has accessibility items that are partly de facto, but doesn't pair them with statutory counterparts.
- **All 6 de jure CPI items fold into existing or near-existing strict/loose clusters** — modulo IND_199 (annual registration form, candidate new row) and IND_203 (principal-side spending reports, currently a consensus singleton).
- **All 8 de facto CPI items map onto the v1.1 schema's `practical_availability` axis** of existing canonical questions, not onto new compendium rows. CPI 2015 is direct empirical validation that the two-axis schema design is the right architecture.
- **CPI 2015 per-state scores (50 states × 14 items)** are a usable ground-truth dataset for cross-validating any practical-availability pipeline we build downstream — with the caveat that 2015 conditions vs. 2026 means it's a noisy anchor, not gospel.

### Projection-success criterion (load-bearing)

- The compendium 2.0 is judged by whether each source rubric is **fully reconstructible** from compendium cells. This is a falsifiable round-trip test on per-state data.
- Architectural framing (consistent with 2026-04-29 reframe): compendium = universe of canonical questions; rubrics = projections. Each rubric has its own scoring layer that reads compendium cells and computes the rubric's score format.
- For projection to work, the compendium needs:
  1. **Both axes populated** (legal_availability + practical_availability) per state per row.
  2. **Cell values, not just row presence** — specifically, threshold dollar amounts (CPI #197) and cadence enumerations (CPI #199). Other rubrics likely have similar value-capture requirements.
  3. **All projection-load-bearing rows kept**, even if they're consensus singletons. CPI #203's principal-side spending-report row is the immediate example.
- Minimum-compendium goal: the smallest set of canonical rows where all 9 rubrics still project correctly. After projections are implemented, run a coverage analysis (which rubrics use which rows); rows used by 0 rubrics are deletion candidates.

## Decisions

| topic | decision |
|---|---|
| 3-way consensus execution | Done. 9 subagents dispatched, all valid, consensus tool run, report written. |
| CPI in-scope filter for consensus run | `C11` only. 15/16 CPI rows are non-lobbying-domain. |
| M1 cluster-file scope | M1 brief explicitly tells subagents to disregard non-USA cluster members. |
| Stability metric | Two metrics computed and reported separately: within-method instability (per method, across 3 runs) and between-method disagreement (cross-method spread). |
| CPI 2015 atomic-item extraction | Pulled from official `PublicI/state-integrity-data` GitHub repo, sheet ` Lobbying Disclosure`. Saved xlsx + scores.csv to `papers/`. Extracted 14 items to `results/items_CPI_2015_lobbying.tsv`. |
| CPI 2015 fold-in vs re-dispatch | Manual fold-in (cheaper). 9-subagent re-dispatch with CPI items added is not warranted. |
| **Projection-success criterion (sharpened)** | **Four commitments: (1) ONE compendium (single canonical row set), (2) ONE extraction pipeline (single methodology applied uniformly across rows / states / years), (3) multi-year reliability (vintages, not single-year), (4) source rubrics as SANITY CHECKS on extraction accuracy, not goals. Multi-rubric × multi-year coverage gives redundant per-row ground truth. Goal: minimum compendium size where all rubrics still project correctly across all vintages.** |
| Compendium 2.0 design plan | Still deferred. Per-rubric projection logic for each of the 9 rubrics is the natural follow-on; CPI 2015 C11 is a small concrete first target (14 items × 50 states). |

## Mistakes recorded

1. **Initial CPI filter framing missed the bigger picture.** Filtered to C11 = 1 placeholder row per the plan, then mid-session realized the actual atomic items live elsewhere and we should extract them. The plan was right within its scope; the scope itself was incomplete. Recovery: extracted from CPI's GitHub repo, integrated cleanly.
2. **Subagents left scratch files in the worktree.** Three of the 9 (M1 run 1, M1 run 3, M3 run 1) wrote helper Python scripts to `build_groups.py`, `.tmpwork/`, `.scratch/` outside their designated output paths. Cleaned up post-hoc. For future runs, the brief should explicitly say "do not write any files outside the specified output CSV path" — current brief allows it implicitly.
3. **M3 within-method instability metric is misleading at face value.** 45.6% looks alarming until you decompose: M3's huge groups (top groups have 17-18 members) amplify pair-level variance because moving one item flips ~17 pair decisions. Should report alongside group-size statistics; the report.md does this but the headline number is potentially misread.

## Results

**Code:**
- `tools/build_usa_tradition_input.py` — pre-stages the 252-item input CSV
- `tools/consensus_grouping.py` — computes per-pair agreement, strict/loose/human-review views, and both stability metrics

**Run artifacts** (all in `docs/active/compendium-source-extracts/results/3way_consensus/`):
- `usa_tradition_items.csv` — 252-item input
- `m{1,2,3}_*_run{1,2,3}.csv` — 9 grouping outputs
- `consensus_summary.csv` — 1,034 co-grouped pairs with agreement counts
- `consensus_clusters_strict.csv` — 24 clusters at ≥8/9
- `consensus_clusters_loose.csv` — 39 clusters at ≥6/9
- `consensus_human_review.csv` — 468 pairs at 3-5/9
- `method_instability_report.md` — both stability metrics with definitions
- `report.md` — headline + analysis
- `briefs/` — common_header + m1/m2/m3 method briefs

**CPI 2015 addition:**
- `papers/CPI_2015__sii_criteria.xlsx` — full 13-sheet codebook (7.6 MB)
- `papers/CPI_2015__sii_scores.csv` — per-state scores
- `results/items_CPI_2015_lobbying.tsv` — 14 atomic items in standard schema

**Compare/contrast doc:**
- `results/20260507_cpi_2015_c11_vs_consensus.md` — per-item fold-in, projection-success criterion as load-bearing principle, recommendations, open work

## Next steps

1. **Per-rubric projection logic** for each of the 9 source rubrics. CPI 2015 C11 (14 items × 50 states) is the smallest concrete target and should be implemented first as a proof-of-concept. After that, the others in increasing complexity (Sunlight 5 items, then OpenSecrets 7, then HiredGuns 47, etc., then PRI 83 last).
2. **Round-trip validation harness.** Once a projection exists for some rubric, run it on N states' populated compendium cells and compare to published rubric scores. Use CPI 2015's 50-state scores as the first ground-truth check.
3. **Cell-value schema decisions for compendium 2.0.** Which rows carry binary cells, which carry typed values (dollars, days, enumerated cadences). The projection-test makes this concrete and testable.
4. **Compendium 2.0 design plan.** Still deferred. The projection-success criterion gives that plan a clear acceptance test that did not exist before today.
5. **Optional: re-run the 9-subagent dispatch with CPI 2015's 14 items added** (would tighten the consensus picture marginally but doesn't change the architecture).

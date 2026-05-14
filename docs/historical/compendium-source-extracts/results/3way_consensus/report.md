# 3-method × 3-run consensus grouping — Report

**Plan:** [`plans/20260506_comp_assembly_3way_consensus.md`](../../plans/20260506_comp_assembly_3way_consensus.md)
**Run:** 2026-05-07; orchestrator dispatched 9 parallel `general-purpose` Task subagents (~9 min wall clock).

## Headlines

- **9/9 outputs valid** (252 rows each, lossless, no duplicate keys, no empty labels).
- **Per-method group counts:**
  - M1 cluster-anchored: 153 / 189 / 201 — within-method spread = **48 groups**
  - M2 blind:            159 / 180 / 195 — within-method spread = **36 groups**
  - M3 FOCAL-anchored:    92 / 110 / 120 — within-method spread = **28 groups**
- **Pair-level consensus (over the 1,034 pairs that any of the 9 runs co-grouped):**
  - 24 strict consensus clusters (≥ 8/9), covering **63 items** = 25.0% of corpus
  - 39 loose consensus clusters (≥ 6/9), covering **106 items** = 42.1%
  - **146 items (57.9%) appear in no loose cluster.** 40 items were never co-grouped by any of the 9 runs.
  - 468 pairs sit in the human-review band (3-5/9).
- **Stability metrics** (see [`method_instability_report.md`](method_instability_report.md) for definitions):
  - Within-method instability: M1 19.1%, M2 14.4%, **M3 45.6%**
  - Between-method disagreement: 67.2% of co-grouped pairs have cross-method spread ≥ 2; 38.0% have spread ≥ 3.

## Headline call

The 24 strict clusters are real and clean, but they are **dominated by the Newmark2005 / Newmark2017 / Opheim within-tradition battery** — i.e. predictable, mostly already-known consolidations. Cross-tradition strict consensus is rare. **The methods agree on the easy cases and disagree on most of the rest.** This run does what it was designed to do: separate the high-confidence merges from the genuine disagreement, and the disagreement pile is large.

## Stability — what the method spread is telling us

| method | within-method instability | n_groups (3 runs) |
|---|---:|---|
| M1 cluster-anchored | 19.1% | 153 / 189 / 201 |
| M2 blind | 14.4% | 159 / 180 / 195 |
| M3 FOCAL-anchored | **45.6%** | 92 / 110 / 120 |

**M3's high within-method instability is a metric artifact, not pure noise.** M3's groups are much larger (top groups have 17-18 members because the FOCAL backbone forces consolidation). One item moving in/out of a 17-member group flips 16 pair-decisions; M1/M2 with their many singletons don't have this amplification. Read M3 instability as "FOCAL-backbone runs disagree on which items belong in each backbone group" — which is the right thing to learn.

**M1 was supposed to be the most stable** (3 runs sharing the same embedding-cluster prior). It isn't. Run 2 produced 153 groups (53 multi-member), run 1 produced 201 (27 multi-member). The cluster prior is being interpreted very differently across runs — some runs treat it as a strong prior, some treat it as one signal among many. Worth flagging if we run this again.

**M2 (blind) is the most stable.** Same task, no priors, three independent passes, lowest within-method instability. That's a positive signal that the canonical-question concept is meaningful at all — different runs without anchors converge enough that within-method disagreement is small.

## Per-paper coverage in strict clusters

| paper | total items | in strict | in loose |
|---|---:|---:|---:|
| Newmark2005 | 18 | **17** | 17 |
| Newmark2017 | 19 | **17** | 17 |
| Opheim | 22 | **12** | 15 |
| FOCAL | 50 | 6 | 14 |
| HiredGuns | 47 | 5 | 8 |
| pri_2010 | 83 | **3** | 31 |
| OpenSecrets | 7 | 2 | 3 |
| Sunlight | 5 | 1 | 1 |
| CPI_2015 | 1 | 0 | 0 |

The asymmetry is the story:

- **Newmark2005/2017 + Opheim**: 46/59 items (78%) in strict clusters. Same-author, near-identical wording across 3 rubrics → all methods agree they're the same questions. This is mostly the BoS-tradition battery (`def_*_lobbying`, `def_*_standard`, `disc_*_expenditures`, `disc_*_compensation`, `prohib_*`).
- **PRI 2010**: 3/83 items (3.6%) in strict clusters. PRI's atomic items are too fine-grained — Q7a-Q7o (15 search-by-field facets), E1h_i-vi / E2h_i-vi (12 frequency-option × principal/lobbyist twins), A1-A11 (11 registrant categories) — to find consensus matches across rubrics that don't enumerate at that resolution.
- **CPI_2015 C11** is the lone in-scope row of CPI; agents universally treated it as a singleton composite. Confirms the plan's assumption that CPI provides a category placeholder, not a question.

## The 24 strict consensus clusters (all in `consensus_clusters_strict.csv`)

The biggest groups are 4-member clusters bridging 4 rubrics:

1. **Expenditures benefiting public officials/employees** (FOCAL financials.10, Newmark2005, Newmark2017, Opheim)
2. **Spending classified by category type** (HiredGuns Q14, Newmark2005, Newmark2017, Opheim)

Then 3-member same-tradition consolidations (Newmark2005 ↔ Newmark2017 ↔ Opheim) for: legislative-lobbying definition, administrative-agency definition, elective-officials-as-lobbyists, public-employees-as-lobbyists, compensation/expenditure/time standards, total compensation, total expenditures, frequency of reporting (with HiredGuns Q12 included), multi-criteria search (FOCAL openness.5 + OpenSecrets + PRI Q8 — one of the few cross-tradition clusters).

Plus pairwise cross-rubric: FOCAL openness.4 + OpenSecrets downloads, FOCAL openness.8 + PRI Q5 (historical archive), FOCAL relationships.1 + PRI E2c (client list), FOCAL relationships.4 + HiredGuns Q22 (business ties), HiredGuns Q13 + Sunlight lobbyist_compensation, HiredGuns Q48 + Newmark2017 revolving-door, plus Newmark2005/2017 prohibitions pairs.

## Where methods disagree most

393 pairs have a cross-method spread of 3 (one method's 3 runs unanimously YES, another's unanimously NO). Pattern: **FOCAL ↔ PRI semantic mismatches**, where M3 (FOCAL-anchored) merges via the FOCAL backbone while M1 (cluster-anchored, more conservative) keeps them separate.

Examples (M1=0, M2=0-1, M3=3 — only M3 merges):

- FOCAL `contact_log.11` (per-meeting bill numbers) ↔ PRI E1g_ii / E2g_ii (per-period bill disclosure). FOCAL frames per-meeting; PRI frames per-reporting-period. Same conceptual content, different filing frame.
- FOCAL `descriptors.2` (contact details) ↔ PRI E1d / E2d (address+phone of principal vs lobbyist). PRI splits filer-side; FOCAL doesn't.
- FOCAL `relationships.1` (client list) ↔ PRI E1c (principals disclose lobbyists). Mirror question; same canonical fact, opposite filer.
- FOCAL `scope.1` (lobbyist types in register) ↔ PRI A4 (lobbying firms). PRI enumerates A1-A11; FOCAL bundles them.

These are the **filer-direction-and-granularity tradeoffs** that compendium 2.0 design has to make a call on. M3's "merge by canonical fact" and M1's "split by filer/granularity" are both defensible; it's a design choice.

Other notable disagreement pairs:

- FOCAL `openness.4` (downloadable) ↔ PRI Q6 (downloadability) — M1=3, M2=3, M3=0. M3 ran 1 placed PRI Q6 in a different FOCAL bucket; surprising.
- FOCAL `revolving_door.2` (database of officials under ban) ↔ HiredGuns Q48 (cooling-off period). M3 unanimous yes, M1 unanimous no. M1 reads them as different concepts (database vs rule), M3 collapses them.

## Singletons across all 9 runs (40 items)

Items no run ever co-grouped with another item — true cross-method-and-cross-run singletons. These are the corpus's unique-question floor; high signal for "things only one rubric thought to ask." Available in `consensus_summary.csv` by inverting the join against `usa_tradition_items.csv`. Notable categories:

- PRI search-by-field battery (Q7a-Q7o)
- HiredGuns enforcement granular items (Q39-Q47: audits, penalties, levy dates, delinquent-filer publication)
- Sunlight composite headers (`expenditure_transparency`, `expenditure_reporting_thresholds`, `document_accessibility`, `lobbyist_activity`)
- FOCAL contact_log subfacets that no rubric matches at the per-meeting frame (contact_log.1-9)
- Opheim enforcement battery (`enforce.subpoena`, `enforce.statutory_authority_to_audit`, etc.)
- CPI_2015 C11

The singleton population is signal, not noise. The plan flagged that diagnostic-strength items (rare-frequency, high-discrimination) are exactly what the compendium-2.0 question set should preserve. These 40 are candidates.

## Coverage check — what's missing from consensus

- **146 of 252 items (58%) appear in no loose cluster.** Most are in the human-review pile: 468 pairs in the 3-5/9 band involve items that some methods merged and others didn't. These are the items the user has to read and call.
- **PRI is the corpus segment with the lowest consensus rate** (3/83 in strict, 31/83 in loose). The PRI granularity vs. other rubrics' coarser framings is the dominant unresolved tension.

## What I'd surface to the user for review

1. **Strict clusters (24, 63 items):** likely safe to accept as compendium-2.0 rows with minor copy-editing on the canonical labels. The Newmark/Opheim battery is the bulk; cross-tradition merges are smaller but cleanly justified.
2. **Loose-only clusters (15 additional clusters / 43 additional items):** read per-cluster — these are 6-7/9 agreement, mostly real but worth a quick sanity check.
3. **The filer-direction question for PRI E1*/E2* twins:** does compendium 2.0 want one canonical question per "fact disclosed" (M3's call) or per "(fact × filer side)" (M1's call)? This single decision moves ~30 PRI rows.
4. **The granularity question for PRI A1-A11 (registrants) and Q7a-Q7o (search facets):** keep as 11+15 separate rows, or fold into 2-3 broader rows? Methods split on this.
5. **The 40 cross-run singletons:** the plan said these are "candidates for the question set" — confirm whether to carry forward.

## Files

- `usa_tradition_items.csv` — input (252 items)
- `m{1,2,3}_*_run{1,2,3}.csv` — 9 grouping outputs (one per subagent)
- `consensus_summary.csv` — per-pair agreement (1,034 pairs, sortable on `pair_strength` and `cross_method_spread`)
- `consensus_clusters_strict.csv` — 24 transitively-closed clusters at ≥ 8/9
- `consensus_clusters_loose.csv` — 39 transitively-closed clusters at ≥ 6/9
- `consensus_human_review.csv` — 468 pairs in the 3-5/9 disagreement band
- `method_instability_report.md` — formal definitions of the two stability metrics + headline numbers
- `briefs/` — the three method briefs (common_header, m1, m2, m3) used in dispatch

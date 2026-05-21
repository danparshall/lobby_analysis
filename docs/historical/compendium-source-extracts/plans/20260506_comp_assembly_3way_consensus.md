# Compendium assembly via 3-method × 3-run consensus — Implementation Plan

**Status:** Active. Supersedes [`plans/20260506_comp_assembly_via_regex.md`](20260506_comp_assembly_via_regex.md) (which proposed a single regex/string method; the user pivoted to a 3-way triangulation design that is methodologically stronger).

**Originating conversation:** [`docs/active/compendium-source-extracts/convos/20260506_3way_consensus_design.md`](../convos/20260506_3way_consensus_design.md)

---

## Why this matters (project context)

This repo is **"LobbyView, for all 50 states"** (`README.md` line 3) — a rubric-agnostic *data layer* where every state's record answers the same fixed set of disclosure questions, so researchers, activists, and journalists can apply their own weights and rankings on top of it.

**The compendium IS that fixed question set.** Each canonical row in compendium 2.0 = one disclosure question we will ask of every state's regime, with answers along two axes: "does the statute require it?" (legal availability) and "does the portal expose it?" (practical availability). Every rubric in `papers/text/` is a different prior attempt at this same question set, with author-specific framing scaffolds wrapped around the same underlying concepts:

- Newmark phrases items as `"Disclosure required: lobbyist principal"`.
- HiredGuns phrases the same item as `"Is the lobbyist principal required to be reported?"`.
- Opheim writes `"lobbyist principal"` bare.
- PRI writes `"Is the lobbyist required to disclose the principal?"`.

These are **one question**. The compendium has to recognize that — otherwise the per-state matrix asks every state the same question N times under different rubric names, which inflates the evaluation cost and corrupts the availability matrix that downstream consumers will derive their rankings from.

## Goal

Produce a **consensus canonical-question grouping** over the ~252 USA-tradition rubric atomic items, by dispatching **3 methodologically-distinct grouping methods × 3 runs each (9 subagents)** and computing per-pair agreement.

The output is the input to compendium 2.0 design:

- Item pairs that **9/9** runs agree are the same canonical question → high-confidence rows of compendium 2.0.
- Item pairs that **0/9** or **1/9** runs group together → high-confidence splits.
- Item pairs in the middle → human-review pile (the user reads, decides, lifts the consensus threshold to whatever they want).

This design separates two distinct sources of variance:

- **Method instability** (within-method variance across the 3 runs of a method) — tells us whether a method is reliable.
- **Method disagreement** (between-method variance) — tells us where genuine ambiguity lives in the corpus.

## Confidence

Load-bearing for compendium 2.0, therefore load-bearing for the per-state data layer that is this repo's deliverable. The methods are independently sensible; consensus across them gives stronger signal than any single method's output. Single-rubric anchoring or single-method anchoring is what we're explicitly avoiding by running this as a triangulation.

---

## Architecture

```
Input:  ~252 USA-tradition atomic items (pre-staged in step 1)
        ↓
9× parallel Task-tool subagent dispatches (general-purpose, local via MAX plan):
   M1 (cluster-anchored)  × 3 runs
   M2 (blind)             × 3 runs
   M3 (FOCAL-anchored)    × 3 runs
        ↓
9 grouping CSVs (uniform schema)
        ↓
tools/consensus_grouping.py — per-pair agreement count
        ↓
results/3way_consensus/consensus_summary.csv + report.md
```

**Subagent dispatch goes through Claude Code's Task tool, NOT the Anthropic API.** The user has a MAX plan; local subagents are free. (The orchestrator agent — the agent executing this plan — calls `Task(subagent_type="general-purpose", ...)` 9 times in parallel.)

**Tech stack:** Python 3.12, pandas, numpy. No new dependencies. Worktree-local venv (`unset VIRTUAL_ENV && uv sync && uv pip install` per the `feedback_pytest_in_worktree.md` memory).

---

## Scope (input universe: 9 USA-tradition rubrics, ~252 items after CPI filter)

| paper_id | n atomic | source file | notes |
|---|---:|---|---|
| `hired_guns_2007` | 47 | `cross_rubric_items_clustered.csv` (paper=`HiredGuns`) | |
| `focal_2024` | 50 | `cross_rubric_items_clustered.csv` (paper=`FOCAL`) | M3 anchor |
| `newmark_2017` | 19 | `cross_rubric_items_clustered.csv` (paper=`Newmark2017`) | |
| `newmark_2005` | 18 | `cross_rubric_items_clustered.csv` (paper=`Newmark2005`) | |
| `opheim_1991` | 22 | `cross_rubric_items_clustered.csv` (paper=`Opheim`) | |
| `opensecrets_2022` | 7 | `cross_rubric_items_clustered.csv` (paper=`OpenSecrets`) | |
| `sunlight_2015` | 5 | `cross_rubric_items_clustered.csv` (paper=`Sunlight`) | |
| `cpi_2015` | **1** (after filter) | `cross_rubric_items_clustered.csv` (paper=`CPI_2015`) | drop the 15 non-lobbying-domain rows; keep only `lobbying_disclosure.*` / similarly-tagged single in-scope row |
| `pri_2010` | 83 | `results/items_PRI_2010.tsv` (separate file) | included per 2026-05-06 partial PRI clearance — see RESEARCH_LOG and `feedback_pri_not_privileged.md` memory |

**Total in scope: ~252 items.** Exact count produced by the pre-stage script in step 1; treat 252 as approximate.

**Out of scope (European tradition — user direction 2026-05-06):** `AccessInfo`, `CouncilEurope`, `ALTER_EU`, `TI_2016`, `Carnstone`, `IBAC`, `McKayWozniak`, `SOMO`, `GDB`. ~325 items. The 2026-05-06 embedding analysis confirmed cross-tradition bridging is sparse and the conceptual divide is structural, not just lexical. Possible future pass as `cmp_*` reference; not in this plan.

**Expected output size:** ~150 canonical questions. **This is the user's gut-instinct estimate, not derived.** Treat as a soft anchor, not a target. ≥250 likely means methods are under-merging; ≤80 likely means over-merging or single-link chaining. The eyeball-check + consensus protocol decides whether clusters are real, not the count.

---

## Steps

### Step 1: Pre-stage the unified input CSV

Create `tools/build_usa_tradition_input.py` that emits `results/3way_consensus/usa_tradition_items.csv`. The output is a single CSV that all 9 subagents read.

```python
#!/usr/bin/env python3
"""Build the 9-rubric USA-tradition input for the 3-way consensus run.

Filters cross_rubric_items_clustered.csv to 8 USA-tradition rubrics, drops
CPI_2015 non-lobbying-domain rows, joins items_PRI_2010.tsv (separate file
since PRI was added later), writes a single CSV all subagents read.
"""
import pandas as pd
from pathlib import Path

ROOT = Path("docs/active/compendium-source-extracts/results")
USA_NON_PRI = ['HiredGuns', 'FOCAL', 'Newmark2017', 'Newmark2005',
               'Opheim', 'OpenSecrets', 'Sunlight', 'CPI_2015']

# Load 8-rubric corpus (already atomic, no composites)
df = pd.read_csv(ROOT / 'cross_rubric_items_clustered.csv')
df = df[df['paper'].isin(USA_NON_PRI)].copy()

# Drop CPI_2015 non-lobbying-domain rows. CPI_2015 is a multi-domain integrity
# scorecard; only the Lobbying Disclosure category is in scope. Inspect the 16
# rows by section/indicator_id and keep only the single in-scope row. (The
# implementer should print the 16 row labels and confirm before filtering.)
cpi_mask = df['paper'] == 'CPI_2015'
# TODO(implementer): set in_scope_ids based on actual indicator_id labels.
# Expect ~1 row to survive. If unsure, inspect:
#   df[df.paper=='CPI_2015'][['indicator_id','indicator_text','section']]
in_scope_cpi_ids: list[str] = []  # fill with the 1 lobbying-domain id
df = df[~cpi_mask | df['indicator_id'].isin(in_scope_cpi_ids)]

# Load PRI separately (different file, slightly different schema)
pri = pd.read_csv(ROOT / 'items_PRI_2010.tsv', sep='\t')
pri = pri.rename(columns={'paper_id': 'paper'})
# Align minimal columns
keep = ['paper', 'indicator_id', 'indicator_text', 'section_or_category']
pri = pri[[c for c in keep if c in pri.columns]]
pri['section'] = pri.get('section_or_category', '')
df_min = df[['paper', 'indicator_id', 'indicator_text', 'section']].copy()
pri_min = pri[['paper', 'indicator_id', 'indicator_text', 'section']].copy()
out = pd.concat([df_min, pri_min], ignore_index=True)

# Sanity check
print(out['paper'].value_counts())
print(f"Total: {len(out)} items")
assert out['indicator_id'].nunique() == len(out), "duplicate (paper,indicator_id)?"

out_path = ROOT / '3way_consensus' / 'usa_tradition_items.csv'
out_path.parent.mkdir(exist_ok=True)
out.to_csv(out_path, index=False)
print(f"Wrote {out_path}")
```

Verify the output: ~252 rows, 9 distinct papers, every `(paper, indicator_id)` pair unique.

### Step 2: Write the 3 method briefs

Save these as files under `docs/active/compendium-source-extracts/results/3way_consensus/briefs/`. Each subagent dispatch will inline one of these as its prompt. The briefs are method-specific; the input + output schema + constraints are identical across all three.

#### Common header (all three briefs)

```
You are grouping lobbying-disclosure rubric items into canonical questions for the
"LobbyView for the states" project's compendium 2.0.

Project context: this repo is building a per-state data layer where every state
answers the same fixed set of disclosure questions. Each canonical row in the
compendium = one such question, asked of all 50 states. Different rubrics ask
the same question with different framing — your job is to recognize that and
group items by the underlying concept, not the framing.

INPUT
-----
File: docs/active/compendium-source-extracts/results/3way_consensus/usa_tradition_items.csv
Columns: paper, indicator_id, indicator_text, section
Total rows: ~252 (varies slightly with CPI filter exact count)

OUTPUT
------
A CSV at: docs/active/compendium-source-extracts/results/3way_consensus/<METHOD>_<RUN>.csv
Columns: source_paper, source_id, source_text, group_id, group_label
- source_paper: copy of input `paper`
- source_id:    copy of input `indicator_id`
- source_text:  copy of input `indicator_text`
- group_id:     your unique group ID, format `g_001`, `g_002`, ... (zero-padded)
- group_label:  your canonical-question phrasing for that group (free text, ≤120 chars)

CONSTRAINTS
-----------
1. Every input row must appear exactly once in the output. Lossless transformation.
2. group_id values must be unique per group within this run.
3. group_label should be a neutral, declarative noun phrase describing the
   underlying disclosure question — not any single rubric's framing.
4. PRI 2010 IS in scope for this run (per the 2026-05-06 partial clearance).
   Do not exclude PRI items.
5. If two items are in different groups, you should be able to articulate WHY
   they aren't the same canonical question. If you can't, they probably should
   be the same group.
6. If a group has only one source item (singleton), that's fine — the item
   represents a unique question that no other rubric asked.

WRITE the output CSV directly via the Write tool, not via stdout.
```

#### M1 method block (cluster-anchored)

```
METHOD: cluster-anchored grouping

You have access to a starting set of 28 embedding-derived clusters from a
prior run (sim ≥ 0.68). Read them at:
  docs/active/compendium-source-extracts/results/embed_clusters_full__openai__text-embedding-3-large.txt

Procedure:
1. Read the cluster file. Each cluster groups 2+ items judged similar by
   text-embedding-3-large at sim ≥ 0.68.
2. For each cluster, validate by reading the actual indicator_text values:
   - If all items truly describe the same canonical question → keep as one group.
   - If the cluster mixes 2+ distinct questions (lexical-noise mismatch) → split.
   - If two clusters describe the same question → merge.
3. Walk the items NOT in any cluster (singletons in the embedding output).
   For each, decide: does it match an existing group, or start a new group?
4. PRI items are NOT in the embedding clusters (they were added separately).
   Place each PRI item: match to existing group, or singleton/new group.
5. Assign group_id and write a canonical group_label for each group.

Your output reflects: embedding's clusters as a starting prior + your judgment
on validation, splits, merges, and unclustered items.
```

#### M2 method block (blind)

```
METHOD: blind grouping (no priors)

Read the input CSV. Group all items by judgment alone — no cluster file, no
external rubric structure, no anchoring on any single paper.

Procedure:
1. Read all ~252 items end-to-end at least once, getting a feel for the
   recurring concepts.
2. Group items by underlying disclosure question. Each group = one canonical
   question.
3. Items that don't match any other rubric's items become singletons.
4. Assign group_id and canonical group_label.

Your output reflects: pure judgment over the corpus, with no method-specific
priors.
```

#### M3 method block (FOCAL-anchored)

```
METHOD: FOCAL-anchored grouping

The 50 indicators in FOCAL 2024 (Lacy-Nichols et al.) are a comprehensive
disclosure-transparency checklist designed for cross-jurisdiction comparison.
Use FOCAL as the backbone of the canonical question set.

Procedure:
1. Pull the 50 FOCAL items from the input CSV (paper == 'FOCAL'). Each FOCAL
   item is one initial group.
2. For each NON-FOCAL item (~202 items across 8 rubrics), assign it to its
   closest matching FOCAL group. The group_label is the FOCAL indicator_text
   (or a slightly cleaned-up canonical form of it).
3. If a non-FOCAL item does not match any FOCAL indicator (e.g. Opheim's
   enforcement battery — FOCAL has no enforcement items), create a NEW
   "extension" group with a clear group_label. These are the "things FOCAL
   didn't anticipate" — high-signal output for compendium 2.0 design.
4. Note: FOCAL has zero items in Prohibitions and minimal Personnel content
   (this is a known FOCAL design choice, not a flaw — FOCAL focuses on
   disclosure mechanisms, which is what this project cares about). Items in
   those categories will mostly fall into extension groups.
5. Assign group_id (FOCAL groups: `g_focal_001..050`; extension groups:
   `g_ext_001+`).

Your output reflects: FOCAL's 50-indicator structure as the spine, plus
extensions for what FOCAL doesn't cover.
```

### Step 3: Dispatch 9 subagents in parallel

Use Claude Code's Task tool with `subagent_type="general-purpose"`. Send all 9 calls in a SINGLE message so they run in parallel:

```
Task(subagent_type="general-purpose", description="M1 cluster-anchored run 1", prompt=<common_header + M1_method_block + "Output to: results/3way_consensus/m1_cluster_anchored_run1.csv">)
Task(subagent_type="general-purpose", description="M1 cluster-anchored run 2", prompt=<... run2.csv>)
Task(subagent_type="general-purpose", description="M1 cluster-anchored run 3", prompt=<... run3.csv>)
Task(subagent_type="general-purpose", description="M2 blind run 1", prompt=<common_header + M2_method_block + "Output to: results/3way_consensus/m2_blind_run1.csv">)
Task(subagent_type="general-purpose", description="M2 blind run 2", prompt=<... run2.csv>)
Task(subagent_type="general-purpose", description="M2 blind run 3", prompt=<... run3.csv>)
Task(subagent_type="general-purpose", description="M3 FOCAL-anchored run 1", prompt=<common_header + M3_method_block + "Output to: results/3way_consensus/m3_focal_anchored_run1.csv">)
Task(subagent_type="general-purpose", description="M3 FOCAL-anchored run 2", prompt=<... run2.csv>)
Task(subagent_type="general-purpose", description="M3 FOCAL-anchored run 3", prompt=<... run3.csv>)
```

Each subagent runs locally via the MAX plan. The orchestrator agent waits for all 9 to return.

### Step 4: Validate outputs

For each of the 9 output CSVs:

1. Row count matches input row count (lossless).
2. Every `(source_paper, source_id)` pair from input appears exactly once.
3. `group_id` values are unique per group within the run.
4. No empty `group_label` values.

If any output fails validation, re-dispatch that one subagent (don't accept malformed output).

### Step 5: Write the consensus tool

Create `tools/consensus_grouping.py`. Inputs: the 9 grouping CSVs. Output: `results/3way_consensus/consensus_summary.csv`.

For each pair `(item_i, item_j)` of source items (where `i < j`):

- Count how many of the 9 runs put `item_i` and `item_j` in the same group → `agreement_count` (0 to 9).
- Compute `pair_strength = agreement_count / 9`.

Output schema (one row per pair):

```
source_paper_i, source_id_i, source_text_i,
source_paper_j, source_id_j, source_text_j,
agreement_count, pair_strength,
m1_count, m2_count, m3_count,         # per-method agreement (0-3)
within_method_max_disagreement        # max(|m1_count - mean|, |m2|, |m3|) — flags method-specific instability
```

Number of pairs: ~252 × 251 / 2 ≈ 31,500 — fine for pandas.

**Derived views the tool also produces** (separate CSVs):

- `consensus_clusters_strict.csv` — clusters formed by transitively-closing pairs with `pair_strength ≥ 8/9`. These are the high-confidence canonical-question rows.
- `consensus_clusters_loose.csv` — same with threshold `pair_strength ≥ 6/9`. Wider net for the human-review pile.
- `consensus_human_review.csv` — pairs in the middle (3/9 ≤ pair_strength ≤ 5/9) — these are the actual disagreement signal.
- `method_instability_report.md` — per-method, what fraction of pairs the method disagrees with itself on across its 3 runs.

### Step 6: Surface results to user

Write `results/3way_consensus/report.md` with:

- Headline counts: total pairs, pairs at 9/9, pairs at 0/9, pairs in human-review band.
- Method-instability stats (within-method variance per method).
- Top 10 strict-consensus clusters (size + member items).
- Top 10 disagreement pairs (the items where methods most diverge — these are the most useful inspection targets).
- Coverage check: do the strict-consensus clusters cover the full input? Or are there isolated items?

Then surface to the user: cluster count, what the consensus pile looks like, where the methods disagreed.

---

## Output schema reference (uniform across all 9 runs)

```
source_paper, source_id, source_text, group_id, group_label
```

This format is "long" (one row per source item). The user said schema doesn't matter as long as we can map back to source items — long-format trivially supports that, and it's the most-mappable for pair-wise consensus.

---

## Constraints / non-negotiables

- **PRI 2010 is in scope** (per 2026-05-06 partial clearance). Do not silently re-exclude it.
- **Subagents launched LOCAL** via Task tool (MAX plan), not via the Anthropic API.
- **Every input item must appear exactly once in each output** (lossless).
- **`git add` specific files**, never `git add .` or `git add -A`.
- **Don't merge to main, don't open a PR** without explicit user request.
- **Don't write to other branches' STATUS.md rows** (per CLAUDE.md collaboration rules).

---

## Open decisions for the implementing agent

These are NOT user questions — the user has been clear that they want this to launch. The implementing agent makes the call and documents in the report.

1. **Consensus threshold for "strict" canonical clusters.** Default: `pair_strength ≥ 8/9`. Can be tuned in the report by producing multiple views.
2. **Canonical-text choice within a consensus cluster.** Default: prefer FOCAL phrasing if a FOCAL item is in the cluster (FOCAL is designed as a canonical-question checklist); else longest item text; else first by alphabetical paper. Document the rule in the report.
3. **Whether to dispatch all 9 in parallel or sequentially.** Parallel recommended (faster, no rate-limit on local MAX). Single message with 9 Task calls.
4. **Method-brief refinement.** If the first batch produces degenerate output (e.g. all items in 1 group, or 252 singletons), tighten the brief and re-dispatch only the affected method. Iterate up to 2 cycles before surfacing to user.

---

## Edge cases and known gotchas

- **CPI_2015 multi-domain noise.** 16 items, only 1 lobbying-domain. Filtered upfront in step 1. If the filter rule is unclear, inspect the rows and pick the single `lobbying_disclosure` row. The other 15 should NOT appear in the input CSV at all.
- **PRI was added separately** (`items_PRI_2010.tsv`, not in `cross_rubric_items_clustered.csv`). The pre-stage script in step 1 joins them. If the join produces duplicates or schema mismatch, fix the schema alignment before continuing.
- **FOCAL has 0 Prohibitions / minimal Personnel.** This is M3's known structural characteristic. Items in those categories will fall into extension groups. Do not interpret this as M3 method failure; it's the design.
- **Newmark2005 ↔ Newmark2017 redundancy.** Same author, near-identical wording. M1/M2/M3 will all likely cluster these tightly. If the strict-consensus output collapses Newmark2005 fully into Newmark2017, that's signal.
- **Embedding clusters are not authoritative.** M1 uses them as a starting prior, but the M1 brief explicitly tells the subagent to validate, split, and merge. If the embedding clusters look "obviously right" the M1 subagent should still rebuild from them.
- **Subagent direction-ambiguity** (per the 2026-05-01 statute-extraction lesson). If method briefs leave room for the subagent to interpret "group" differently across runs, within-method variance will be high. The briefs above are designed to minimize this — the orchestrator agent should treat any obvious ambiguity in the briefs as a bug and tighten before dispatch.

---

## Cost / time budget

- **Cost:** $0 in API spend (local subagents via MAX plan). Cap on opportunity cost only.
- **Wall-clock:** 9 parallel subagents × ~10–20 min each ≈ **15–30 min for dispatch**, gated by the slowest subagent.
- **Pre-stage + briefs:** ~30 min (one-time setup).
- **Validation:** ~5 min.
- **Consensus tool:** ~30 min (writing tools/consensus_grouping.py).
- **Surfacing:** ~15 min.
- **Total:** ~1.5–2 hours, mostly wall-clock for the dispatch wait.

---

## Provisional → final

This run produces a consensus snapshot, not the final compendium 2.0. The user reviews the strict-consensus clusters and the human-review pile, decides which clusters are real, then approves the canonical question list for compendium 2.0 schema design (which is a separate plan after this run).

If this run produces clean consensus on the easy cases and identifies a workable disagreement pile (≤30 ambiguous pairs), it's done. If method instability is high (e.g. M2 blind has very high within-method variance — runs disagree with themselves more than they disagree with M1/M3), it's a signal that the input corpus is harder than expected and additional methods or a structured back-and-forth pass may be needed. Surface either outcome to the user.

The next session is **user review of the consensus output** + drafting the compendium 2.0 schema plan based on what the consensus survives.

# Compendium assembly via regex/python — Implementation Plan

**Goal:** Produce a parallel candidate item set for compendium 2.0 (`comp_assembly_regex_v1.{tsv,md}`) by regex/string-based normalization + dedup, scoped to USA-tradition rubrics. This is one assembly *method*; the actual compendium 2.0 emerges from reconciling this output against the existing embedding-based candidate set, not from this output alone.

**Originating conversation:** [`docs/active/compendium-source-extracts/convos/20260506_comp_assembly_via_embeddings.md`](../convos/20260506_comp_assembly_via_embeddings.md)

**Context:** A 2026-05-06 session ran an OpenAI `text-embedding-3-large` pass over the 509 rubric atomic items and produced two embedding-based candidate sets (`comp_assembly_embed_v{1,2}.tsv`). The embedding approach has known weaknesses for the USA-tradition rubrics: it loses signal on short-label items (Newmark2005, Sunlight) and can mismatch on lexical-noise highest-similarity arguments (e.g. Opheim "lobbyist's total spending" argmaxed onto an HG frequency-of-reporting question). The regex approach is expected to be stronger on those exact edge cases — short labels lexically match each other, and explicit per-rubric framing-strip rules (already prototyped in `tools/normalize_state_items.py`) expose the underlying noun-phrase concept directly. Running both methods and reconciling is the user's intended path to compendium 2.0.

**Confidence:** Exploratory — testing whether regex/string methods produce a comparable or stronger USA-tradition candidate set than embeddings. The two methods are expected to disagree on some items; that disagreement is the most informative signal.

**Architecture:** Assemble candidates from `items_*.tsv` of USA-tradition rubrics → apply per-rubric framing-strip (extending the prototype in `tools/normalize_state_items.py`) → cluster by string similarity (token overlap, n-gram, edit distance — implementer's choice) → for each cluster produce one canonical row that links back to all source items. Output a TSV in the same schema as `comp_assembly_embed_v*` plus a methodology note.

**Branch:** `compendium-source-extracts` (active worktree at `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts/`)

**Tech Stack:** Python 3.12, `pandas`, `numpy`, regex (`re`). No embedding model needed for this run. Existing `tools/normalize_state_items.py` is the starting point for framing-strip rules.

---

## Scope

**In scope (USA-tradition rubrics):**

| paper_id | n atomic items | source TSV |
|---|---:|---|
| `hired_guns_2007` | 47 | `results/items_HiredGuns.tsv` |
| `focal_2024` | 50 | `results/items_FOCAL.tsv` |
| `newmark_2017` | 19 | `results/items_Newmark2017.tsv` |
| `newmark_2005` | 18 | `results/items_Newmark2005.tsv` |
| `opheim_1991` | 22 | `results/items_Opheim.tsv` |
| `opensecrets_2022` | 7 | `results/items_OpenSecrets.tsv` |
| `sunlight_2015` | 5 | `results/items_Sunlight.tsv` |
| `cpi_2015` | 16 | `results/items_CPI_2015.tsv` |
| `pri_2010` | 83 | `results/items_PRI_2010.tsv` |

Total: **287 atomic items** across 9 USA-tradition rubrics. (FOCAL is technically `cross` tradition since Lacy-Nichols 2024 is designed for cross-jurisdiction comparison; for compendium-2.0 US-state-disclosure scope it's grouped with the USA tradition. PRI is now permitted as a coverage extension per the 2026-05-06 user clearance — see the convo's PRI section.)

**NOT in scope (European tradition is notably different — user direction 2026-05-06):**

| paper_id | n | reason |
|---|---:|---|
| `accessinfo_2022`, `councileurope_2017`, `alter_eu_2014`, `ti_2016`, `carnstone_2020`, `ibac_2022`, `mckay_wozniak_2020`, `somo_2018`, `gdb_2022` | 325 | European/transnational normative frameworks. Most items are out of US-state-lobbying-disclosure scope (right-to-participate, EU MEP declarations, Dutch consultation reform, etc.). The 2026-05-06 embedding analysis confirmed cross-tradition bridging is sparse and the conceptual divide is structural, not just lexical. A small subset may later be flagged as `cmp_*` coverage-comparison reference; not in this plan. |

Total in scope: **287 items**. Total ignored: **325 items**.

## Composite-row filtering

Some `items_*.tsv` files include composite/sub-total rows that should be dropped before processing (see the existing `tools/assemble_comp_embed.py` for a pattern). Confirmed composites in scope:

- `items_Opheim.tsv`: drop `index.total`, `def.section_total`, `disclosure.section_total`, `enforce.section_total` (4 composites; 22 atomic remain)
- `items_Newmark2017.tsv`: drop `index.total`, `def.section_total`, `prohib.section_total`, `disclosure.section_total` (4 composites; 19 atomic remain)
- `items_HiredGuns.tsv`, `items_FOCAL.tsv`, `items_OpenSecrets.tsv`, `items_Sunlight.tsv`, `items_CPI_2015.tsv`, `items_Newmark2005.tsv`, `items_PRI_2010.tsv`: no composites — use directly.

Cross-check by comparing `items_*.tsv` row counts (incl. composites) against `cross_rubric_items_clustered.csv` row counts (atomic only) for the relevant `paper` value — discrepancies are composites.

## Recommended approach

The implementer is encouraged to pick the approach that best fits the data, but here's a recommended starting path:

**Approach: framing-strip → string-similarity dedup**

1. Extend `tools/normalize_state_items.py` to also handle `OpenSecrets`, `Sunlight`, `CPI_2015`, `PRI_2010` (only HG / Newmark2017 / Newmark2005 / Opheim / OpenSecrets are currently rule-cased there). The existing rules for HG and Newmark2017 are reasonable starting points.
2. Run normalization across all 287 USA-tradition items → `cross_rubric_items_usa_normalized.csv` (analogous to the existing `cross_rubric_items_state_normalized.csv` but covering more rubrics).
3. Compute pairwise string similarity within the normalized corpus. Reasonable choices:
   - Jaccard over token sets (after stop-word + stemming)
   - Character-level n-gram overlap
   - `rapidfuzz`/`difflib` ratio (only if user approves the dependency add — `rapidfuzz` is not currently in `pyproject.toml`)
   - All-of-the-above with the implementer picking thresholds per metric
4. Single-link cluster across rubrics at thresholds appropriate to each metric. Same single-link caveat applies as in the embedding run: chaining can produce a giant mega-cluster at low thresholds.
5. For each cluster ≥2 items, pick one canonical text (longest? most-rubric-spanning? composite of all? — implementer's call, document the choice). Produce a `compendium_role` tag analogous to the embedding run's `core_*` / `ext_*_*`.
6. Items in singletons (no cross-rubric matches) get `compendium_role = singleton_<paper_id>`.

**Alternative approaches** (weaker but worth considering):
- **Concept-keyword regex**: define a hand-crafted set of canonical concept patterns ("compensation threshold", "expenditure threshold", "gift disclosure", "registration form", "spending report"); regex-tag each item with concept matches; dedup at the concept level. Higher precision, lower recall, more manual labor.
- **Manual mapping table**: one engineer reads all 287 items and groups them by hand. Highest reliability, slowest. Probably the right choice if the regex approaches all underperform.

## Steps

1. Read the originating convo (`convos/20260506_comp_assembly_via_embeddings.md`) — particularly the **Provisional Findings** section on the structural-not-lexical European↔state divide and the **Open Questions** section on Newmark2005/Sunlight short-label artifacts. Both are directly relevant to expected regex performance.
2. Read `tools/normalize_state_items.py` end-to-end — that's the framing-strip prototype. The HG and Newmark2017 rules are the substantive part.
3. Read `tools/assemble_comp_embed.py` — that's the parallel-method assembler, useful for the output schema and the composite-filtering pattern.
4. Read the user's [`feedback_name_by_method_not_conclusion.md`](/Users/dan/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_name_by_method_not_conclusion.md) memory — name your outputs by method, not conclusion.
5. Decide on a string-similarity metric (or combination). Document the choice in the methodology note.
6. Extend `tools/normalize_state_items.py` to cover all 9 USA-tradition rubrics (or write a new `tools/normalize_usa_items.py` if the structural changes warrant — implementer's call).
7. Write a normalization-output sanity-check that prints per-rubric before/after diffs for human eyeballing. Run it. Inspect by eye that the framing-strip is producing sensible output. Iterate the rules until satisfied.
8. Write the dedup script: `tools/assemble_comp_regex.py`. Inputs: the per-rubric `items_*.tsv` files + the normalized text. Outputs: `results/<date>_comp_assembly_regex_v1.tsv` + `.md`.
9. Output schema: same as `comp_assembly_embed_v*` (13 cols), plus optionally a `cluster_id` column showing which cluster each item belongs to and a `canonical_for_cluster` boolean.
10. Run it. Spot-check the output by eye:
    - Pick 5 random clusters of size ≥3. Read the items. Are they actually the same concept?
    - Pick 5 random singletons. Are they genuinely unique items, or did the dedup miss a cross-rubric match?
    - For a few items the embedding method clustered together (e.g. HG `Q11` + Newmark2017 `disclosure.compensation_received_broken_down_by_employer`), check whether the regex method also clusters them.
11. Write the methodology note (`<date>_comp_assembly_regex_v1.md`) — same structure as `comp_assembly_embed_v1.md`. Include the **caveat block** at the top ("one method's output, not THE answer; parallel to the embedding-based candidate; the comprehensive set is whatever falls out of comparing/reconciling these").
12. Commit + push. Use `git add` for specific files, never `git add .` or `-A`.
13. Surface to the user: report the cluster count, the most-rubric-spanning clusters, the singletons, and any items where regex dedup disagrees with embedding dedup. The disagreement set is the most useful product of this run.

## Edge cases to think about

- **Rubric items that are explicitly multi-concept** (e.g. FOCAL `scope.1`: "The following types of lobbyists are included in the register: professional lobbyists/consultants, in-house lobbyists, third-party lobbyists, registered lobbyists, ..."). String dedup will treat this as one item but it's really an enumeration of sub-concepts. Decide: keep whole, split, or flag for manual review.
- **Short-label rubrics (Sunlight, CPI_2015, Newmark2005)**: their items are 2-3 words. Token-overlap dedup against longer items will be low-similarity even when concept-equivalent. The regex method should specifically handle this — for instance, by checking whether the short label is a substring or token-subset of any longer normalized item.
- **CPI_2015 multi-domain noise**: 15 of 16 CPI_2015 items are non-lobbying domains (Procurement, Pension management, etc.). These should NOT cluster with anything in the lobbying rubrics, and they should NOT silently inflate the singleton count. Either filter them out upfront with a hand-curated allowlist (only `Lobbying disclosure` is in scope) or tag them as `out_of_scope_cpi_2015` and exclude from the canonical set.
- **PRI items use distinctive question-style framing** ("Are X required to be Y?", "Is X required to disclose Y?"). The HG-style normalization rules in `normalize_state_items.py` will partially cover them, but PRI's specific patterns should be added.
- **PRI A-series rows are "who must register" decompositions** (lobbyists, volunteer lobbyists, lobbying firms, employers of lobbyists, etc.). These won't have direct 1-to-1 matches in HG/FOCAL/Newmark — they decompose what other rubrics treat as a single category. Decide: keep all PRI A-series as separate rows in the regex assembly, or merge them under a canonical "registration scope" parent. The convo's notes on PRI's decomposition style are relevant here.

## Testing plan (analysis-task variant — no TDD required)

This is an exploration/analysis task, not a TDD-style implementation. The "tests" are eyeball-checks of the output and consistency-checks against the embedding-based parallel.

**What to check after running:**

1. **Cluster sanity:** for 10 random clusters of size ≥2, read the items aloud. Do they describe the same concept? If not, flag for the implementer to revise the rules.
2. **Singleton sanity:** for 10 random singletons, check whether the embedding-based candidate (`comp_assembly_embed_v2.tsv`) also treats this item as singleton. If embedding clustered it with other items but regex didn't, that's a recall miss for the regex method — investigate whether a rule extension would catch it.
3. **Item count:** the output should have somewhere in the range of ~100-180 canonical rows (rough guess based on the embedding analysis showing ~25-45% within-rubric redundancy in the USA tradition). If the count is dramatically outside this range, something is probably wrong with the dedup thresholds.
4. **Coverage of items_* sources:** every item in the 9 source TSVs must appear in the output, either as a singleton or as a member of a cluster. Lossless transformation. A simple count check (sum of canonical-rows + sum of within-cluster-non-canonical-rows == 287) will catch dropped items.
5. **Cross-method disagreement:** for the same 287-item universe, compare the cluster structure produced by this regex method against the cluster structure of `comp_assembly_embed_v2.tsv`'s same items. Items the methods agree on are high-confidence dedup candidates. Items they disagree on are the most useful signal — that's where compendium-2.0 design needs human judgment.

**What constitutes a surprising result worth flagging to the user:**

- Cluster count in the >200 range (under-dedup) or <80 range (over-dedup chaining).
- A cluster spanning ≥6 rubrics (the embedding method's max was 5; if regex finds 6+ that's news).
- A PRI item clustering tightly with a non-PRI item in a way that wasn't expected (could indicate that Newmark/HG/FOCAL already cover something the PRI inclusion was meant to fill).
- A USA-tradition item that's in a singleton in BOTH methods. That's a coverage gap candidate that neither method's clustering exposes — worth highlighting for compendium-2.0 design.

NOTE: I will write *all* sanity-check verification code before relying on the output for any conclusions.

## Provisional → final

If the regex method produces clean clusters and good agreement with the embedding method on the easy cases, the two outputs can be reconciled into a v3 candidate set that's the union with disagreement flagged for human review. If the regex method produces noisy / unreliable clusters, the output is still useful as a sanity check on the embedding method's edge cases (Newmark2005/Sunlight short-label gaps, in particular).

The next session after this one is reconciliation — comparing both candidate sets and producing whichever combined artifact the user wants (called `comp_assembly_reconciled_v1.tsv` or similar; name reflects the method, again).

---

**Testing Details:** Sanity checks specified above operate on the output TSV — they verify dedup behavior on real data, not mocks. Cross-method comparison against `comp_assembly_embed_v2.tsv` is the key behavioral test (does this method recover the embedding method's high-confidence matches, and what does it disagree on?).

**Implementation Details:**

- Primary artifact: `tools/assemble_comp_regex.py` (analogous to `tools/assemble_comp_embed.py`)
- Secondary artifact: extended `tools/normalize_state_items.py` (or new `tools/normalize_usa_items.py`)
- Output: `results/<date>_comp_assembly_regex_v1.{tsv,md}` — schema matches `comp_assembly_embed_v*`
- Working venv: the worktree's local `.venv/` (NOT the main worktree's). Use `unset VIRTUAL_ENV && uv sync && uv pip install ...` per the `feedback_pytest_in_worktree.md` memory.
- Optional dependency: `rapidfuzz` for string similarity. Ask the user before adding to `pyproject.toml`.
- File naming discipline (per `feedback_name_by_method_not_conclusion.md`): name by method (`comp_assembly_regex`), not by conclusion (`comprehensive_set`). Adding new files? Use the `comp_assembly_regex` prefix consistently.
- Don't touch `STATUS.md` rows for other branches. Append a one-liner to "Recent Sessions" at session-end via the `finish-convo` skill.
- Don't merge to main. Don't open a PR unless the user explicitly asks.
- Don't unfreeze the PRI-out-of-bounds rules — only the partial clearance from 2026-05-06 applies (PRI as `ext_pri_2010_*` coverage extension; everything else still blocked).

**What could change:**

- If the user decides to also include some European-tradition items as `cmp_*` coverage-comparison reference, the in-scope universe expands. Treat that as a separate plan/session.
- If the user decides FOCAL doesn't belong in the USA-tradition group (e.g. wants a strict US-states-only filter), drop FOCAL and re-scope to 237 items.
- The embedding-based candidate set may be re-run with different threshold choices or a normalized corpus; if so, update the cross-method comparison against the latest version.
- The Newmark2005 ↔ Newmark2017 redundancy decision is open: in the embedding method, Newmark2005 was dropped as fully covered by Newmark2017 longer text. The regex method should be able to confirm this via short-label-substring matching. If confirmed, drop Newmark2005 from canonical rows in this run too.

**Questions** (to surface to the user at session start):

1. Is `rapidfuzz` an acceptable dependency to add for fuzzy string matching, or does the implementer need to roll the metric by hand with `re` + `difflib`?
2. For multi-concept items like FOCAL `scope.1` (enumeration of 5 lobbyist sub-types), keep as one row or split? The embedding method kept whole.
3. For canonical-text choice within a cluster (longest item / most-rubric-spanning item / composite of all source texts), which heuristic?
4. PRI A-series ("who must register" decomposition): keep all 11 rows or merge under a parent canonical? Affects ~10 rows in output count.
5. Is there budget appetite for an LLM-rewrite alternative (gpt-5-mini at ~$0.50 to rewrite each item as a neutral declarative noun phrase) if the regex method underperforms? The convo's earlier discussion mentioned this as a fallback option.

---

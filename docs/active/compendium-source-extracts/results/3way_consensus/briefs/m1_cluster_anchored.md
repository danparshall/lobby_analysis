METHOD: cluster-anchored grouping

You have access to a starting set of embedding-derived clusters from a prior
run, computed with OpenAI text-embedding-3-large at single-link similarity
≥ 0.68. Read them at:

  docs/active/compendium-source-extracts/results/embed_clusters_full__openai__text-embedding-3-large.txt

IMPORTANT: that cluster file was built over the FULL 509-item corpus
(USA-tradition + European-tradition rubrics). The 9 USA-tradition rubrics
listed in the common header are your scope. **Disregard any cluster
members where `paper` is not in the 9 USA-tradition rubrics.** If a
cluster mixes USA and Euro items, treat the Euro members as out-of-scope
and proceed with only the USA members.

Procedure:
1. Read the cluster file. Each cluster groups 2+ items judged similar by
   text-embedding-3-large at sim ≥ 0.68. Filter each cluster to its
   USA-tradition members.
2. For each cluster (post-filter), validate by reading the actual
   indicator_text values against the input CSV:
   - If all USA items truly describe the same canonical question → keep as
     one group.
   - If the cluster mixes 2+ distinct questions (lexical-noise mismatch)
     → split.
   - If two clusters describe the same question → merge.
3. Walk the items NOT in any cluster (singletons in the embedding output).
   For each, decide: does it match an existing group, or start a new group?
4. PRI 2010 items are NOT in the embedding clusters (they were added
   separately after the embedding run). Place each PRI item: match to an
   existing group, or create a singleton/new group.
5. Assign group_id (zero-padded `g_001`, `g_002`, ...) and write a canonical
   group_label for each group.

Your output reflects: embedding's clusters as a starting prior + your
judgment on validation, splits, merges, and unclustered items.

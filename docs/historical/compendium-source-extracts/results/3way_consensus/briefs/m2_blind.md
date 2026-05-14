METHOD: blind grouping (no priors)

Read the input CSV. Group all items by judgment alone — no cluster file, no
external rubric structure, no anchoring on any single paper. Do NOT read
the embed_clusters file. Do NOT inspect FOCAL items first as a backbone.

Procedure:
1. Read all 252 items end-to-end at least once, getting a feel for the
   recurring concepts.
2. Group items by underlying disclosure question. Each group = one
   canonical question. Two items belong in the same group if and only if
   they ask the same question, regardless of framing.
3. Items that don't match any other rubric's items become singletons.
4. Assign group_id (zero-padded `g_001`, `g_002`, ...) and a canonical
   group_label.

Your output reflects: pure judgment over the corpus, with no
method-specific priors.

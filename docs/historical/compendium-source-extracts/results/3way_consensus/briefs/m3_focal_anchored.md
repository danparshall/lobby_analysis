METHOD: FOCAL-anchored grouping

The 50 indicators in FOCAL 2024 (Lacy-Nichols et al.) are a comprehensive
disclosure-transparency checklist designed for cross-jurisdiction
comparison. Use FOCAL as the backbone of the canonical question set.

Procedure:
1. Pull the 50 FOCAL items from the input CSV (paper == 'FOCAL'). Each
   FOCAL item is one initial group.
2. For each NON-FOCAL item (~202 items across 8 rubrics), assign it to its
   closest matching FOCAL group. The group_label is the FOCAL
   indicator_text (or a slightly cleaned-up canonical form of it).
3. If a non-FOCAL item does not match any FOCAL indicator (e.g. Opheim's
   enforcement battery — FOCAL has no enforcement items), create a NEW
   "extension" group with a clear group_label. These are the "things
   FOCAL didn't anticipate" — high-signal output for compendium 2.0
   design.
4. Note: FOCAL has zero items in Prohibitions and minimal Personnel
   content. This is a known FOCAL design choice (FOCAL focuses on
   disclosure mechanisms), not a flaw. Items in those categories will
   mostly fall into extension groups.
5. Assign group_id:
   - FOCAL groups: `g_focal_001`, `g_focal_002`, ..., `g_focal_050`
     (use the FOCAL item's order in the input CSV; zero-pad to 3 digits).
   - Extension groups: `g_ext_001`, `g_ext_002`, ... (zero-pad to 3 digits).

Your output reflects: FOCAL's 50-indicator structure as the spine, plus
extensions for what FOCAL doesn't cover.

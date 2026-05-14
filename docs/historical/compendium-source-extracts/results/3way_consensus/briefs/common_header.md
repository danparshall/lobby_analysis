You are grouping lobbying-disclosure rubric items into canonical questions for the
"LobbyView for the states" project's compendium 2.0.

Project context: this repo is building a per-state data layer where every state
answers the same fixed set of disclosure questions. Each canonical row in the
compendium = one such question, asked of all 50 states. Different rubrics ask
the same question with different framing — your job is to recognize that and
group items by the underlying concept, not the framing.

Examples of items that should be grouped together (same canonical question,
different framing):
- Newmark: "Disclosure required: lobbyist principal"
- HiredGuns: "Is the lobbyist principal required to be reported?"
- Opheim: "lobbyist principal"
- PRI: "Is the lobbyist required to disclose the principal?"

These are ONE question. Your output should put them in one group.

INPUT
-----
File: docs/active/compendium-source-extracts/results/3way_consensus/usa_tradition_items.csv

Columns: paper, indicator_id, indicator_text, section
Total rows: 252

Papers in scope (9 USA-tradition rubrics):
  HiredGuns (47), FOCAL (50), Newmark2017 (19), Newmark2005 (18),
  Opheim (22), OpenSecrets (7), Sunlight (5), CPI_2015 (1), pri_2010 (83)

OUTPUT
------
A CSV at: docs/active/compendium-source-extracts/results/3way_consensus/<METHOD_RUN>.csv
(Exact filename will be specified in the dispatch message.)

Columns:
  source_paper   — copy of input `paper`
  source_id      — copy of input `indicator_id`
  source_text    — copy of input `indicator_text`
  group_id       — your unique group ID (format: `g_001`, `g_002`, ..., zero-padded)
  group_label    — your canonical-question phrasing for that group (≤120 chars,
                   neutral declarative noun phrase)

Write the output CSV directly via the Write tool, not via stdout.

CONSTRAINTS
-----------
1. Every input row must appear exactly once in the output. Lossless transformation.
   Row count of your output MUST equal 252.
2. group_id values must be unique per group within this run.
3. group_label should be a neutral, declarative noun phrase describing the
   underlying disclosure question — not any single rubric's framing.
4. PRI 2010 IS in scope for this run. Do not exclude PRI items.
5. If two items are in different groups, you should be able to articulate WHY
   they aren't the same canonical question. If you can't, they probably should
   be the same group.
6. If a group has only one source item (singleton), that's fine — the item
   represents a unique question that no other rubric asked.
7. Use only items from the input CSV. Do not add, drop, or invent items.

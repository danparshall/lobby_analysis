---
name: Update-Docs
description: Checkpoint research progress mid-session — create/update convo summary, save results with provenance, update RESEARCH_LOG and STATUS.md. Core operation that finish-convo builds on.
---

<required>
*CRITICAL* Add the following steps to your Todo list using TodoWrite:

1. Determine the current branch name and convo name (established at session start).

2. Create or update the conversation summary at `docs/active/<branch-name>/convos/<convo-name>.md`:

```markdown
# [Convo Name]

**Date:** YYYY-MM-DD
**Branch:** branch-name

## Summary
2-3 paragraphs of what was discussed and explored this session.

## Topics Explored
- Bullet points of what was investigated

## Provisional Findings
- What we learned or observed (these are provisional, not conclusions)

## Decisions Made
- Any concrete decisions about next steps or approach
- Link to plan docs if any were created

## Results
- Links to any results files saved this session (see step 3)

## Open Questions
- Things we didn't resolve
- Hypotheses that need testing
```

If updating an existing convo file (mid-session checkpoint), append new findings rather than rewriting — preserve the chronological record.

3. Save any results produced this session.

If the session produced tables, figures, analysis outputs, or data summaries:
- Save each to `docs/active/<branch-name>/results/`
- Name with date prefix: `YYYYMMDD_description.md` (for tables), `.png`/`.pdf` (for figures)
- Each results file should include a provenance header:

```markdown
<!-- Generated during: convos/YYYYMMDD_convo_name.md -->
```

- Add links to these results in the convo file's "Results" section
- For markdown tables: save as `.md` files in results/
- For figures/plots: save the image file AND a brief `.md` companion describing what it shows and how it was generated

If no results were produced, skip this step.

4. Append session entry to `docs/active/<branch-name>/RESEARCH_LOG.md`:

```markdown
## Session: YYYY-MM-DD — [convo-name]
### Topics Explored
- Brief bullet points (can reference the full convo file for detail)

### Provisional Findings
- Key takeaways from this session

### Results
- Links to any results files (e.g., `results/20260321_distribution_table.md`)

### Next Steps
- What to try next session
```

Place the new entry at the TOP of the log (below the header), so the most recent session is first.

If updating an existing RESEARCH_LOG entry (mid-session checkpoint), update in place rather than creating a duplicate.

5. Update STATUS.md with a one-line session summary.

- Add a line under a "Recent Sessions" section (or create it if it doesn't exist)
- Format: `- YYYY-MM-DD: [branch] explored X, found Y`
- Do NOT rewrite STATUS.md conclusions — just append the one-liner
</required>

# Common Mistakes

**Writing convo summaries that sound like settled conclusions**
- Problem: Future agents read "we determined X" and treat it as ground truth
- Fix: Use language like "we explored X and the initial evidence suggests Y"

**Forgetting to link results to conversations**
- Problem: A table or figure in results/ has no context — future agents don't know what question it was answering
- Fix: Every results file has a provenance header; every convo lists its results

**Overwriting STATUS.md**
- Problem: A one-session finding replaces months of accumulated context
- Fix: ONLY append a one-liner. Never rewrite existing STATUS.md content during update-docs.

**Creating a duplicate RESEARCH_LOG entry on second update-docs call**
- Problem: Mid-session checkpoint creates a second entry for the same session
- Fix: Check if an entry for this convo-name already exists; update it in place

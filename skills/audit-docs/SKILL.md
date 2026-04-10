---
name: Audit-Docs
description: Check docs/active/ structure for consistency — every convo indexed in RESEARCH_LOG, every plan linked to a convo, no orphaned files. Prompts the user for discrepancies rather than auto-fixing.
---

<required>
*CRITICAL* Add the following steps to your Todo list using TodoWrite:

1. Inventory all branch directories under docs/active/.
2. For each active branch, check convo/plan/results consistency.
3. Present discrepancies to the user and ask how to proceed.
4. Fix only what the user approves.
</required>

# The Audit

## Step 1: Inventory

For each directory in `docs/active/*/`:
- List all files in convos/, plans/, results/
- Read RESEARCH_LOG.md

## Step 2: Check consistency

For each active branch, check:

### Convos
- [ ] Every file in `convos/` is referenced in RESEARCH_LOG.md
- [ ] Every RESEARCH_LOG session entry points to a convo that exists
- [ ] Convo files have the expected structure (Date, Branch, Summary sections)

### Plans
- [ ] Every file in `plans/` has an "Originating conversation" field
- [ ] The referenced convo file actually exists
- [ ] Plans are referenced in RESEARCH_LOG.md or in the originating convo's "Decisions Made" section

### Results
- [ ] Every file in `results/` has a provenance header (`<!-- Generated during: ... -->`)
- [ ] The referenced convo file actually exists
- [ ] Results are linked from their originating convo's "Results" section

### RESEARCH_LOG
- [ ] Entries are in reverse-chronological order (newest first)
- [ ] No duplicate entries for the same session

## Step 3: Report and prompt

**CRITICAL: Do NOT auto-fix discrepancies.** The user may be running multiple sessions in parallel. A "missing" convo might still be open in another tab.

Present findings grouped by severity:

**Missing links (likely fixable):**
```
- plans/20260318_implement_pipeline.md has no originating conversation link
- results/20260315_distribution.md is not linked from any convo
```

**Possible orphans (check with user):**
```
- convos/20260315_pilot_analysis.md is not in RESEARCH_LOG.md
  (Could be an open session in another tab — want me to add it to the log?)
```

**Structural issues:**
```
- RESEARCH_LOG.md has entries out of order
- convo 20260312_exploration.md is missing the Summary section
```

Ask: "Want me to fix any of these? (Note: some may be from sessions still in progress.)"

## Step 4: Fix approved items only

For each item the user approves:
- Add missing RESEARCH_LOG entries
- Add missing originating conversation links to plans
- Add missing provenance headers to results
- Add missing results links to convo files
- Reorder RESEARCH_LOG entries if requested

Do NOT delete any files or remove any content.

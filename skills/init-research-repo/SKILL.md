---
name: Init-Research-Repo
description: Use when setting up a new repo (or an existing repo) for the research-first workflow — creates docs/active/ and docs/historical/ directories, adds Research Context to CLAUDE.md, seeds STATUS.md with the Archived Research Lines table
---

<required>
*CRITICAL* Add the following steps to your Todo list using TodoWrite:

1. Check what already exists (CLAUDE.md, STATUS.md, docs/)
2. Create directory structure
3. Add Research Context section to CLAUDE.md
4. Seed STATUS.md with research sections
5. Create initial RESEARCH_LOG.md if on a branch
6. Report what was created
</required>

# Init Research Repo

Sets up the directory structure and documentation scaffolding needed for the research-first workflow.

Announce at start: "I'm using the Init Research Repo skill to set up the research workflow."

## The Process

### Step 1: Check What Exists

Before creating anything, check what's already in place:

```bash
ls -la CLAUDE.md STATUS.md README.md 2>/dev/null
ls -d docs/ docs/active/ docs/historical/ 2>/dev/null
```

- If `docs/active/` already exists, this repo may already be set up — ask the user before overwriting
- If CLAUDE.md exists, we'll be appending to it, not replacing it

### Step 2: Create Directory Structure

```bash
mkdir -p docs/active docs/historical
```

If we're on a named branch (not main):

```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
  mkdir -p "docs/active/$BRANCH/convos" "docs/active/$BRANCH/plans" "docs/active/$BRANCH/results"
fi
```

### Step 3: Add Research Context to CLAUDE.md

If CLAUDE.md exists, check whether it already has a "Research Context" section. If not, append this block (or insert it before "Project Context" if that section exists):

```markdown
## Research Context

This is an active research project. All findings are provisional — evidence accumulates gradually.

**Document structure:**
- `docs/active/<branch-name>/` — active research lines, with `convos/`, `plans/`, `results/`, and `RESEARCH_LOG.md`
- `docs/historical/<topic>/` — archived research lines. **Do NOT read unless the user specifically asks.** The "Archived Research Lines" table in STATUS.md summarizes what's there.
- `docs/` root — general project docs

**Epistemic norms:**
- Do NOT treat any prior doc as settled truth
- Read `docs/active/<branch>/RESEARCH_LOG.md` to understand the trajectory of thinking on a research line
- When the user says "the data showed X, let's pivot," trust them — they have seen results you haven't
```

If CLAUDE.md doesn't exist, ask the user before creating one — they may have a specific structure in mind.

### Step 4: Seed STATUS.md

If STATUS.md exists, check whether it already has an "Archived Research Lines" section. If not, append:

```markdown
## Archived Research Lines

Lines moved to docs/historical/ — not currently active, but available for reference.

| Topic | Summary | Archived | Material |
|-------|---------|----------|----------|
| (none yet) | | | |

## Recent Sessions

(One-line session summaries, newest first)
```

If STATUS.md doesn't exist, ask the user whether to create one. A minimal seed:

```markdown
# STATUS — [Project Name]

Last updated: YYYY-MM-DD

## Current Focus

[To be filled in]

## Recent Sessions

(One-line session summaries, newest first)

## Archived Research Lines

Lines moved to docs/historical/ — not currently active, but available for reference.

| Topic | Summary | Archived | Material |
|-------|---------|----------|----------|
| (none yet) | | | |
```

### Step 5: Create Initial RESEARCH_LOG.md (if on a branch)

If we're on a named branch (not main/master), create `docs/active/<branch>/RESEARCH_LOG.md`:

```markdown
# Research Log: [branch-name]
Created: YYYY-MM-DD
Purpose: [ask the user for a one-sentence description]

---

(Sessions will be logged here, newest first)
```

### Step 6: Report

Tell the user what was created:

```
Research workflow initialized:
  - docs/active/           (active research lines)
  - docs/historical/       (archived research lines)
  - CLAUDE.md              (Research Context section added)
  - STATUS.md              (Archived Research Lines table + Recent Sessions section added)
  [- docs/active/<branch>/ (with RESEARCH_LOG.md, convos/, plans/, results/)]

Next steps:
  - Start a research session and the finish-convo skill will populate these
  - Use `git mv docs/active/<topic> docs/historical/<topic>` to archive completed research lines
```

## DOCS_INDEX.md Approach

If the repo has a DOCS_INDEX.md (or similar index file), convert it to a lightweight meta-index:

```markdown
## Active Research Lines
See docs/active/. Each branch directory has convos/, plans/, results/.
STATUS.md "Recent Sessions" tracks activity across branches.

## Historical
See docs/historical/. Summaries in STATUS.md "Archived Research Lines" table.

## Legacy Docs (docs/ root)
[existing entries for files not yet migrated]
```

The detailed per-branch indexing is handled by RESEARCH_LOG.md within each `docs/active/<branch>/` directory. Don't try to maintain a single global index across all branches — that creates merge conflicts and busywork.

## Notes

- This skill is idempotent — it checks before creating and won't overwrite existing content
- It's safe to run on an existing repo that's partially set up
- The skill creates structure only. Content comes from the research workflow (finish-convo, write-a-plan, etc.)
- **Push after setup** — `git push -u origin <branch>` to back up the scaffolding immediately

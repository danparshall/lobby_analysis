---
name: Use-Worktree
description: Use this whenever you need to create an isolated workspace — includes data/ symlink to prevent data loss on worktree cleanup
---

<required>
*CRITICAL* Add the following steps to your Todo list using TodoWrite:

1. Find the worktrees directory.

- Check existing directories using the Bash tool: `ls -d .worktrees 2>/dev/null`
- If not found, ask me for permission to create a .worktrees directory
- If given permission, create `.worktrees`.

2. Verify .gitignore before creating a worktree using the Bash tool:

```bash
# Check if directory pattern in .gitignore
grep -q "^\.worktrees/$" .gitignore || grep -q "^worktrees/$" .gitignore
```

- If not found, add the appropriate line to the .gitignore immediately.

3. Create the worktree

- Come up with a good branch name based on the request.
- Create the worktree with the Bash tool: `git worktree add ".worktrees/$BRANCH_NAME" -b "$BRANCH_NAME"
- cd into the newly created path with the Bash tool: `cd $path`

4. Symlink shared directories.

After creating the worktree and cd-ing into it, symlink `data/` and `.env.local` to the main worktree so that gitignored data is shared (not duplicated and lost on cleanup):

```bash
# Get the main worktree path (the repo root, NOT another worktree)
MAIN_WORKTREE=$(git worktree list | head -1 | awk '{print $1}')

# Symlink data/ if it exists in main
if [ -d "$MAIN_WORKTREE/data" ] && [ ! -e data ]; then
  ln -s "$MAIN_WORKTREE/data" data
fi

# Symlink .env.local if it exists in main
if [ -f "$MAIN_WORKTREE/.env.local" ] && [ ! -e .env.local ]; then
  ln -s "$MAIN_WORKTREE/.env.local" .env.local
fi
```

**Why:** `data/` is gitignored and contains checkpoints, raw responses, and intermediate results needed for reproducibility. Without symlinks, this data lives only in the worktree and gets **permanently deleted** on worktree cleanup. This has caused real data loss.

5. Initialize research docs (if this is a new research branch).

If this branch doesn't already have a `docs/active/<branch-name>/` directory:

```bash
BRANCH_NAME=$(git branch --show-current)
mkdir -p "docs/active/$BRANCH_NAME/convos" "docs/active/$BRANCH_NAME/plans" "docs/active/$BRANCH_NAME/results"
```

Create an initial `docs/active/$BRANCH_NAME/RESEARCH_LOG.md`:

```markdown
# Research Log: [branch-name]
Created: YYYY-MM-DD
Purpose: [one-sentence description from the user's request]
```

If this is an engineering branch (not research), skip this step.

6. Auto-detect and run project setup.

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

- If there is no obvious project setup, you _MUST_ ask me.

7. Run tests to ensure the worktree is clean.

```bash
# Examples - use project-appropriate command
npm test
cargo test
pytest
go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

8. Report Location

```
New working directory: <full-path>
Data symlink: data/ → <main-worktree>/data/
Tests passing (<N> tests, 0 failures)
All commands and tools will now refer to: <full-path>
```

9. Understand that you are now in a new working directory. Your Bash tool instructions from here on out should refer to the worktree directory, NOT your original directory. This is ABSOLUTELY CRITICAL.

</required>

# Maintaining Working Directory in Worktree

CRITICAL: Once you create and enter a worktree, you must stay within
it for the entire session.

Rules:

1. Never use cd .. from within a worktree - It will eventually take
   you outside the worktree boundary
2. Always use absolute paths for commands - Use npm run lint from
   within the worktree, not cd .. && npm run lint
3. If you need to run root-level commands, use the full worktree path:
   <bad-example>
   cd .. && npm run lint
   </bad-example>
   <good-example>
   npm run lint # (from worktree root)
   </good-example>

<good-example>
cd /home/$USER/code/project/.worktrees/branch-name && npm run lint
</good-example>

4. Verify your location frequently:

```bash
pwd  # Should show .worktrees/branch-name in path
git branch  # Should show * on your feature branch, not main
```

5. If you accidentally exit the worktree:

- Immediately recognize it (check if you're on main branch)
- Navigate back: cd /full/path/to/.worktrees/your-branch
- Verify: git branch should show your branch, not main

Red Flags:

- Running git status and seeing "On branch main" when you should be on a feature branch
- Running pwd and NOT seeing .worktrees/ in the path
- Any cd .. command while in a worktree

# Quick Reference

| Situation                   | Action                     |
| --------------------------- | -------------------------- |
| `.worktrees/` exists        | Use it (verify .gitignore) |
| `.worktrees` does not exist | Check CLAUDE.md → Ask user |
| Directory not in .gitignore | Add it immediately         |
| Tests fail during baseline  | Report failures + ask      |
| No package.json/Cargo.toml  | Skip dependency install    |
| No `data/` in main worktree | Skip data symlink          |

# Common Mistakes

**Skipping data/ symlink**

- **Problem:** Gitignored data (checkpoints, raw responses) lives only in the worktree and is permanently lost on cleanup
- **Fix:** Always symlink data/ to main worktree after creation

**Skipping .gitignore verification**

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always grep .gitignore before creating project-local worktree

**Assuming directory location**

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: existing > CLAUDE.md > ask

**Missing project installation**

- **Problem:** Tests and lint will fail, breaking the project
- **Fix:** Always install the project when creating a new worktree

**Proceeding with failing tests**

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

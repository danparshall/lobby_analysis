---
name: clean-worktrees
description: Use when you want to clean up accumulated git worktrees in a repo. Lists all worktrees with status, verifies data symlinks, ensures code and docs are committed, copies non-symlinked data files to main worktree, asks which to merge or keep, runs post-merge audits on new docs/papers, and removes merged worktrees.
---

<required>
CRITICAL: Add the following steps to your Todo list using TodoWrite:

1. Run inventory script to list all worktrees with status
2. Present inventory to user and confirm which worktrees to process
3. For each selected worktree, verify data symlinks and ensure everything is committed
4. Handle non-symlinked data files (copy to main, commit results under 50MB)
5. Ask user per-worktree: merge or keep
6. Merge approved worktrees, handle conflicts
7. Run post-merge audits on new docs/papers
8. Archive research docs if merging a research branch
9. Clean up merged worktree directories
</required>

# Cleaning Up Worktrees

Safely consolidates accumulated worktrees by committing work, preserving data, merging approved branches, and running post-merge audits.

Announce at start: "I'm using the Clean Worktrees skill to consolidate worktrees."

CRITICAL: Other Claude sessions may be actively working in worktrees. Never process a worktree without explicit user confirmation. A clean git status does NOT mean it's safe.

## The Process

### Step 1: Run Inventory

If the bundled script exists, run it for the overview:

```
python3 SKILLS_DIR/clean-worktrees/worktree_inventory.py REPO_ROOT
```

Otherwise, run `git worktree list` and for each worktree check:
- Branch name and last commit
- Uncommitted changes (`git status`)
- Open PRs on the branch (`gh pr list --head BRANCH`)
- Whether the branch is already merged into main

Present results and ask the user which worktrees to process. Never auto-select.

### Step 2: Verify Data Symlinks

For each selected worktree, check whether `data/` is a symlink to the main worktree:

```bash
MAIN_WORKTREE=$(git worktree list | head -1 | awk '{print $1}')

# Check if data/ is a symlink
if [ -L "data" ]; then
  echo "data/ is symlinked to: $(readlink data)"
  # Verify it points to main
  if [ "$(readlink data)" = "$MAIN_WORKTREE/data" ]; then
    echo "OK - points to main worktree"
  else
    echo "WARNING - points somewhere unexpected"
  fi
elif [ -d "data" ]; then
  echo "WARNING: data/ is a real directory, NOT a symlink"
  echo "Files here will be LOST when this worktree is removed"
  echo "Must copy contents to main worktree before cleanup"
fi
```

**If data/ is a real directory (not a symlink):** Copy its contents to the main worktree before proceeding. This prevents data loss.

```bash
# Copy non-symlinked data to main worktree
rsync -av --ignore-existing data/ "$MAIN_WORKTREE/data/"
```

### Step 3: Commit Outstanding Work

For each selected worktree:

- [ ] Check `git status` for uncommitted changes
- [ ] Check for untracked files — flag anything unexpected (forgotten source files, configs)
- [ ] Stage and commit any outstanding code and docs changes
- [ ] If there's an open PR, note it — the user may want to push before merging locally

### Step 4: Handle Non-Symlinked Data Files

Classify files in each worktree that aren't tracked in git:

- Final results under 50MB: stage and commit these (they should be preserved in git)
- Checkpoint files, large intermediates, temporary outputs: copy to main worktree (same relative path) but do not stage in git
- Ask the user if classification is ambiguous

Use file size and naming heuristics:
- Files with "checkpoint", "ckpt", "tmp", "temp" in the name are checkpoints
- Files in output/, results/, data/ directories are likely results
- Files over 50MB are always copy-only regardless of type

### Step 5: Merge Decision

For each worktree, ask the user: merge into main, or keep the branch?

Before merging, check:
- [ ] Is there an open PR? If yes, warn — consider merging via PR instead
- [ ] Is the branch already merged? If yes, skip merge, just clean up
- [ ] Are there merge conflicts? If yes, stop and present them — do not auto-resolve

To merge:
```
git checkout main && git merge BRANCH_NAME
```

Use `git branch -d` (not -D) after merge — this only works if the branch is fully merged, which is the safety check we want.

### Step 6: Archive Research Docs (if applicable)

If the merged branch has a `docs/active/branch-name/` directory, ask the user:
- **Archive:** `git mv docs/active/branch-name docs/historical/branch-name` and add an entry to the "Archived Research Lines" table in STATUS.md
- **Keep active:** Leave in `docs/active/` if the research line continues on another branch

### Step 7: Post-Merge Audits

After each merge, check what new files came in:

```
git diff --name-only HEAD~1 HEAD
```

- If any files in docs/ were added or changed: run maintaining-decision-docs skill on those files
- If PAPER_SUMMARIES.md was modified: run auditing-paper-summaries skill scoped to new entries

Only run audits on files that changed in the merge, not full audits.

### Step 8: Clean Up

For each merged worktree:

- [ ] Verify all non-symlinked data files were copied to main
- [ ] Verify data/ symlink status (if it's a real dir, contents MUST be copied first)
- [ ] Run `git worktree remove PATH` to remove the worktree directory
- [ ] Confirm the remote branch can be deleted (`git push origin --delete BRANCH` — ask first)

Report final summary: what was merged, what was kept, what data was preserved, what research lines were archived.

## File Classification Rules

| Type | Size | Action |
|------|------|--------|
| Source code, docs | any | commit in worktree before merge |
| Final results (csv, json, png, etc.) | under 50MB | commit in worktree before merge |
| Final results | over 50MB | copy to main, do not commit |
| Checkpoints, intermediates | any | copy to main, do not commit |
| Temp files, logs, caches | any | ask user, usually discard |

## Common Mistakes

- Processing a worktree that another session is actively using — always confirm with user
- Auto-resolving merge conflicts instead of presenting them
- Forgetting to check data/ symlink status — real directories get deleted with the worktree
- Forgetting to copy non-symlinked data files before removing the worktree directory
- Running full audits instead of scoping to new files from the merge
- Not archiving research docs when merging a research branch

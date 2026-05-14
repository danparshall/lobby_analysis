# Noridoc: clean-worktrees

Path: @/skills/clean-worktrees

### Overview
This skill helps inspect and clean accumulated git worktrees in the repository. Its helper script inventories worktrees, branch status, merge state, recent commits, and data-file risks.

### How it fits into the larger codebase

The project uses branch-specific worktrees for research lines, and @/CLAUDE.md treats branch hygiene as load-bearing. @/skills/clean-worktrees/worktree_inventory.py gives the skill a structured view of local worktrees before any cleanup decisions are made. It is especially relevant because this repo may contain generated data directories that should not be lost during worktree removal.

### Core Implementation

The helper shells out to git for worktree, status, merge, and last-commit information, then scans worktree paths for non-symlinked files under `data`. It reports dirty state and data risks so the agent can decide what needs committing, copying, merging, or preserving. The script avoids making cleanup changes itself.

### Things to Know

The helper treats data files as a special risk surface because worktree cleanup can otherwise remove locally generated artifacts. Its git calls are inspection-oriented and intended to precede explicit user-approved cleanup actions. The skill workflow, not the helper script alone, controls any destructive or branch-mutating steps.

Created and maintained by Nori.

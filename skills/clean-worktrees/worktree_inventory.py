#!/usr/bin/env python3
"""
Inventory all git worktrees in a repo with status information.

For each worktree reports:
- Branch name and last commit
- Uncommitted changes (staged, unstaged, untracked)
- Whether the branch is merged into main
- Untracked data files that may need handling
- Large files (>50MB)

Usage:
    python3 worktree_inventory.py [repo_root]
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: str, cwd: str = None) -> str:
    """Run a shell command and return stdout."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd
    )
    return result.stdout.strip()


def get_worktrees(repo_root: str) -> list:
    """Parse git worktree list --porcelain output."""
    raw = run("git worktree list --porcelain", cwd=repo_root)
    if not raw:
        return []

    worktrees = []
    current = {}
    for line in raw.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True
        elif line == "":
            pass
    if current:
        worktrees.append(current)

    return worktrees


def get_status(path: str) -> dict:
    """Get git status summary for a worktree."""
    status_raw = run("git status --porcelain", cwd=path)
    lines = [l for l in status_raw.split("\n") if l.strip()] if status_raw else []

    staged = [l for l in lines if l[0] != " " and l[0] != "?"]
    unstaged = [l for l in lines if len(l) > 1 and l[1] != " " and l[0] != "?"]
    untracked = [l[3:] for l in lines if l.startswith("??")]

    return {
        "staged": len(staged),
        "unstaged": len(unstaged),
        "untracked": untracked,
        "clean": len(lines) == 0,
    }


def is_merged(branch: str, repo_root: str) -> bool:
    """Check if branch is fully merged into main."""
    merged = run("git branch --merged main", cwd=repo_root)
    return branch in merged.split()


def get_last_commit(path: str) -> str:
    """Get last commit info."""
    return run('git log -1 --format="%h %s (%cr)"', cwd=path)


def find_data_files(path: str) -> list:
    """Find untracked files that look like data/results."""
    status_raw = run("git status --porcelain", cwd=path)
    if not status_raw:
        return []

    untracked = []
    for line in status_raw.split("\n"):
        if line.startswith("??"):
            filepath = line[3:].strip()
            full_path = os.path.join(path, filepath)
            if os.path.isfile(full_path):
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                ext = os.path.splitext(filepath)[1].lower()
                data_exts = {
                    ".csv", ".json", ".jsonl", ".parquet", ".pkl", ".pickle",
                    ".npy", ".npz", ".h5", ".hdf5", ".feather", ".arrow",
                    ".xlsx", ".xls", ".tsv", ".db", ".sqlite",
                    ".png", ".jpg", ".jpeg", ".svg", ".pdf",
                    ".pt", ".pth", ".ckpt", ".safetensors",
                    ".txt", ".log", ".md",
                }
                is_data = ext in data_exts
                is_checkpoint = any(
                    kw in filepath.lower()
                    for kw in ["checkpoint", "ckpt", "tmp", "temp", "cache"]
                )
                untracked.append({
                    "path": filepath,
                    "size_mb": round(size_mb, 1),
                    "ext": ext,
                    "is_data": is_data,
                    "is_checkpoint": is_checkpoint,
                    "over_50mb": size_mb > 50,
                })

    return [f for f in untracked if f["is_data"]]


def main():
    repo_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    repo_root = os.path.abspath(repo_root)

    worktrees = get_worktrees(repo_root)
    if not worktrees:
        print(f"No worktrees found in {repo_root}")
        sys.exit(0)

    # Identify main worktree
    main_wt = None
    feature_wts = []
    for wt in worktrees:
        branch = wt.get("branch", "")
        if branch in ("main", "master"):
            main_wt = wt
        else:
            feature_wts.append(wt)

    print("=" * 60)
    print("WORKTREE INVENTORY")
    print("=" * 60)
    print(f"\nRepo: {repo_root}")
    print(f"Main worktree: {main_wt['path'] if main_wt else 'NOT FOUND'}")
    print(f"Feature worktrees: {len(feature_wts)}")
    print()

    if not feature_wts:
        print("No feature worktrees to process.")
        sys.exit(0)

    for wt in feature_wts:
        path = wt["path"]
        branch = wt.get("branch", "(detached)")
        last_commit = get_last_commit(path)
        status = get_status(path)
        merged = is_merged(branch, repo_root) if branch != "(detached)" else False
        data_files = find_data_files(path)

        print(f"--- {branch} ---")
        print(f"  Path: {path}")
        print(f"  Last commit: {last_commit}")
        print(f"  Merged into main: {'YES' if merged else 'no'}")

        if status["clean"]:
            print("  Status: clean")
        else:
            parts = []
            if status["staged"]:
                parts.append(f"{status['staged']} staged")
            if status["unstaged"]:
                parts.append(f"{status['unstaged']} unstaged")
            if status["untracked"]:
                parts.append(f"{len(status['untracked'])} untracked")
            print(f"  Status: {', '.join(parts)}")

        if data_files:
            print(f"  Data files ({len(data_files)}):")
            for f in data_files:
                label = "CHECKPOINT" if f["is_checkpoint"] else "RESULT"
                size_note = " [>50MB, copy-only]" if f["over_50mb"] else ""
                print(f"    [{label}] {f['path']} ({f['size_mb']} MB){size_note}")

        # Check for open PRs (if gh is available)
        pr_check = run(f'gh pr list --head "{branch}" --json number,title,state 2>/dev/null', cwd=repo_root)
        if pr_check and pr_check != "[]":
            print(f"  Open PR: {pr_check}")

        print()

    # Summary
    already_merged = sum(1 for wt in feature_wts if is_merged(wt.get("branch", ""), repo_root))
    with_changes = sum(1 for wt in feature_wts if not get_status(wt["path"])["clean"])

    print("## Summary")
    print(f"  Total feature worktrees: {len(feature_wts)}")
    print(f"  Already merged into main: {already_merged}")
    print(f"  With uncommitted changes: {with_changes}")
    print(f"  Clean and unmerged: {len(feature_wts) - already_merged - with_changes}")


if __name__ == "__main__":
    main()

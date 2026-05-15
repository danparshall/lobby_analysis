#!/usr/bin/env python3
"""Apply compendium v2 row-ID renames + Candidate-8 doc typo across the repo.

Background: the row-naming audit on `compendium-naming-docs` (merged in
PR #10) accepted 15 row-ID renames and 1 documentation typo fix. This
script is the find-and-replace tool sister branches run after merging
main to bring their tree up to date.

Usage:

    # Show what would change without writing
    python tools/v2_update_names.py --dry-run

    # Apply changes to the working tree
    python tools/v2_update_names.py --apply

Defaults to dry-run for safety. The repo root is auto-detected via
`git rev-parse --show-toplevel`; override with `--root <path>`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from lobby_analysis.row_id_renamer import RENAMES, walk_and_apply


def _detect_repo_root() -> Path:
    """Return the git repo root for the current working directory."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit(
            "could not detect repo root via `git rev-parse --show-toplevel`. "
            "Pass --root explicitly."
        ) from exc
    return Path(out.stdout.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repo root to walk (default: git rev-parse --show-toplevel)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would change without writing (default)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="write changes to disk",
    )
    args = parser.parse_args(argv)

    root = args.root if args.root is not None else _detect_repo_root()
    dry_run = not args.apply  # dry-run is default

    print(f"root: {root}")
    print(f"mode: {'APPLY (writing)' if not dry_run else 'dry-run (no writes)'}")
    print(f"renames: {len(RENAMES)} entries")
    print()

    results = walk_and_apply(root, RENAMES, dry_run=dry_run)

    if not results:
        print("no files contain old names — tree is already up to date.")
        return 0

    total_subs = sum(results.values())
    print(f"{'would change' if dry_run else 'changed'}: "
          f"{len(results)} files, {total_subs} substitutions")
    print()
    for path in sorted(results):
        rel = path.relative_to(root) if path.is_absolute() else path
        print(f"  {results[path]:>4}  {rel}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

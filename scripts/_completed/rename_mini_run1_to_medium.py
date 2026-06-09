"""One-shot rename: data/oh_portal/extracted_openai/<rid>/mini_run_1_* → mini_medium_run_1_*.

Why this script exists
----------------------
The 2026-06-09 Day-2 partial Run 1 produced 55 filings under run_dir names of
the form `mini_run_1_<ts>_<uuid8>/`. Those were dispatched WITHOUT a
`reasoning_effort` argument — i.e., at OpenAI's API default, which is
"medium" for gpt-5-mini as of 2026-06. The next round adds two more arms
(`low`, `minimal`) and the dispatcher now writes effort-coupled labels:
`mini_medium_run_1_*`, `mini_low_run_1_*`, `mini_minimal_run_1_*`. The 55
existing dirs need to be relabeled so:

  1. Resume on Arm A (`--reasoning-effort=medium --pass=1`) correctly skips
     them (the dispatcher's `already_extracted` matches by run_label prefix).
  2. Downstream analysis can attribute outputs to settings without parsing
     extraction_run.json.

The script is idempotent: it does nothing on a second run because there are
no more `mini_run_1_*` dirs left to rename. It also refuses to overwrite an
existing `mini_medium_run_1_*` directory — that case shouldn't arise unless
medium has already been dispatched fresh, in which case the operator's
intent is ambiguous and we should not silently merge.

Reverse migration: if needed, run with `--reverse` to undo (rename back).

Provenance note: the underlying extractions were performed at API-default
medium reasoning effort. Calling them "medium" is correct *after* the
2026-06-08 OpenAI API state has been verified; if mini's default ever
shifts, this assumption needs revisiting. The extraction_run.json files
under these dirs do NOT carry an explicit `reasoning_effort` field (that
capture only lands in extractions performed after the extract_openai.py
change in the same commit series). Going forward, the field IS captured.

Run
---
    uv run python scripts/_completed/rename_mini_run1_to_medium.py
    uv run python scripts/_completed/rename_mini_run1_to_medium.py --reverse
    uv run python scripts/_completed/rename_mini_run1_to_medium.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from lobby_analysis.oh_portal.fetch import DATA_DIR  # noqa: E402
from lobby_analysis.oh_portal.pipeline_openai import (  # noqa: E402
    EXTRACTED_OPENAI_SUBDIR,
)

OLD_PREFIX = "mini_run_1_"
NEW_PREFIX = "mini_medium_run_1_"


def find_rename_targets(
    data_dir: Path, from_prefix: str, to_prefix: str
) -> list[tuple[Path, Path]]:
    """Walk extracted_openai/ and return (src, dst) pairs to rename.

    Skips dirs that already carry `to_prefix` (idempotency). Refuses to plan
    a rename when the target name already exists at the destination.
    """
    root = data_dir / EXTRACTED_OPENAI_SUBDIR
    if not root.is_dir():
        return []

    pairs: list[tuple[Path, Path]] = []
    for report_dir in sorted(root.iterdir()):
        if not report_dir.is_dir():
            continue
        for run_dir in sorted(report_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            if not run_dir.name.startswith(from_prefix):
                continue
            # The PREFIX must be a literal prefix and the rest of the name
            # must NOT itself collide with the to_prefix (defends against
            # double-rename if from_prefix is a substring of to_prefix or
            # vice versa).
            new_name = to_prefix + run_dir.name[len(from_prefix):]
            new_path = run_dir.parent / new_name
            if new_path.exists():
                raise RuntimeError(
                    f"Refusing to rename {run_dir} → {new_path}: "
                    f"target already exists. This usually means the rename "
                    f"was already done in part, or a fresh dispatch under "
                    f"the new label has produced overlapping output. "
                    f"Resolve by hand before retrying."
                )
            pairs.append((run_dir, new_path))
    return pairs


def execute_renames(pairs: list[tuple[Path, Path]], *, dry_run: bool) -> None:
    for src, dst in pairs:
        action = "WOULD RENAME" if dry_run else "RENAME"
        print(f"  {action} {src.name} → {dst.name}", file=sys.stderr)
        if not dry_run:
            src.rename(dst)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", default=str(DATA_DIR),
        help=f"Data directory (default {DATA_DIR}).",
    )
    parser.add_argument(
        "--reverse", action="store_true",
        help=(
            "Undo the rename: mini_medium_run_1_* → mini_run_1_*. "
            "Use only to roll back."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Plan and print renames but don't execute.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    from_prefix = NEW_PREFIX if args.reverse else OLD_PREFIX
    to_prefix = OLD_PREFIX if args.reverse else NEW_PREFIX

    pairs = find_rename_targets(data_dir, from_prefix, to_prefix)
    print(
        f"[rename] {len(pairs)} dirs to rename "
        f"({from_prefix!r} → {to_prefix!r}) under "
        f"{data_dir / EXTRACTED_OPENAI_SUBDIR}",
        file=sys.stderr,
    )
    if not pairs:
        print("[rename] nothing to do (idempotent).", file=sys.stderr)
        return 0
    execute_renames(pairs, dry_run=args.dry_run)
    print(
        f"[rename] {'planned' if args.dry_run else 'completed'} "
        f"{len(pairs)} renames.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

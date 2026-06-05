"""One-shot: drop the `prompt_text` column from the v2 compendium TSV.

Per plan docs/active/wi-tier1-direct-read/plans/20260604_wide_prompt_text_pass.md
Commit 1, step 11: prompts live in `compendium/source_quotes.yaml` after the
wide-pass design; the TSV's `prompt_text` column gets removed as part of
this commit.

Use `lineterminator='\n'` to preserve the file's Unix line endings (the csv
default '\r\n' would balloon the diff with CRLF noise).

After running once, this script moves to `scripts/_completed/`.
"""

from __future__ import annotations

import csv
from pathlib import Path


_WORKTREE = Path(__file__).resolve().parents[1]
_TSV_PATH = _WORKTREE / "compendium" / "disclosure_side_compendium_items_v2.tsv"

_COLUMN_TO_DROP = "prompt_text"


def main() -> None:
    if not _TSV_PATH.exists():
        raise FileNotFoundError(_TSV_PATH)

    with _TSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if _COLUMN_TO_DROP not in fieldnames:
        print(f"Column {_COLUMN_TO_DROP!r} already absent — nothing to do.")
        return

    fieldnames = [c for c in fieldnames if c != _COLUMN_TO_DROP]
    for row in rows:
        row.pop(_COLUMN_TO_DROP, None)

    with _TSV_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {_TSV_PATH}")
    print(f"  Dropped column: {_COLUMN_TO_DROP}")
    print(f"  Remaining columns: {fieldnames}")


if __name__ == "__main__":
    main()

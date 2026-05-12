#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# ///
"""Inventory v1 TSV anchors whose data-row appears empty.

A jurisdiction anchor that carries only its label token (and possibly one
or two vertical-text garbage tokens) likely has its data row dropped by
the v1 OCR — tesseract PSM 3 segments those bands out on certain scans.
See investigation in convos/20260511_opheim_phase0_table1_lift.md.

Usage: uv run scripts/diagnose_v1_token_gaps.py
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

TSV = Path("docs/active/cogel-extraction/results/20260505_v1_tokens.tsv")
# Threshold below which we treat an anchor as "empty data row". Pure-label
# anchors have 1-2 tokens (label only + maybe one rotated-header garbage);
# the smallest real data rows in the corpus (Georgia scan 169) have ~4.
EMPTY_THRESHOLD = 3


def main() -> None:
    counts: Counter[tuple[int, str]] = Counter()
    with TSV.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r["row"] in ("_header", "_footer"):
                continue
            counts[(int(r["scan_page"]), r["row"])] += 1

    empty = sorted(
        ((s, n, c) for (s, n), c in counts.items() if c < EMPTY_THRESHOLD),
        key=lambda t: (t[0], t[1]),
    )
    print(f"Anchors with < {EMPTY_THRESHOLD} tokens (label-only, no data row):")
    for s, n, c in empty:
        print(f"  scan {s:3d}  {n:25s}  tokens={c}")
    print(f"\nTotal: {len(empty)}")

    # Also report borderline rows (3-5 tokens) — these may have partial data
    borderline = sorted(
        ((s, n, c) for (s, n), c in counts.items()
         if EMPTY_THRESHOLD <= c < 6),
        key=lambda t: (t[0], t[1]),
    )
    print(f"\nBorderline anchors with 3-5 tokens (possibly partial data):")
    for s, n, c in borderline:
        print(f"  scan {s:3d}  {n:25s}  tokens={c}")
    print(f"\nTotal: {len(borderline)}")


if __name__ == "__main__":
    main()

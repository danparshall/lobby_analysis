"""Audit: how many of the 305 cached OH filings are Executive vs Legislative AERs?

Hypothesis: the extraction brief is titled for "Legislative agent AERs" but the
cache may contain a mix of Legislative and Executive AERs, which have
different section structures. If the cache is mostly/entirely Executive, the
"0 gifts" result has a structural explanation independent of prompt scope.

Method: scan each raw.html for the AER form title in the <title> tag and the
<h1>; count by type.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
RAW = ROOT / "data/oh_portal/raw"

TITLE_PATTERN = re.compile(r"<title>([^<]*)</title>", re.IGNORECASE)
H1_PATTERN = re.compile(r'<h1[^>]*>([^<]*)</h1>', re.IGNORECASE)


def main():
    filing_ids = sorted(p.name for p in RAW.iterdir() if p.is_dir())
    print(f"Total filings: {len(filing_ids)}")
    print()

    titles = Counter()
    h1s = Counter()
    sample_per_h1 = {}

    for fid in filing_ids:
        subdirs = list((RAW / fid).iterdir())
        if not subdirs:
            continue
        # newest by name (ISO sorted)
        latest = max(subdirs, key=lambda p: p.name)
        html = (latest / "raw.html").read_text(errors="replace")
        t = TITLE_PATTERN.search(html)
        h = H1_PATTERN.search(html)
        title_text = t.group(1).strip() if t else "(no title)"
        h1_text = h.group(1).strip() if h else "(no h1)"
        titles[title_text] += 1
        h1s[h1_text] += 1
        if h1_text not in sample_per_h1:
            sample_per_h1[h1_text] = fid

    print("=" * 70)
    print("By <title>")
    print("=" * 70)
    for t, n in titles.most_common():
        print(f"  {n:4d}  {t}")
    print()
    print("=" * 70)
    print("By <h1> (more specific form type)")
    print("=" * 70)
    for h, n in h1s.most_common():
        print(f"  {n:4d}  {h}  (sample filing_id: {sample_per_h1.get(h, '?')})")


if __name__ == "__main__":
    main()

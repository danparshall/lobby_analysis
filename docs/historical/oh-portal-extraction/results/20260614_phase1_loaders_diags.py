"""Diagnostic on duplicate filing_ids and the 18 unmatched bill_referenced positions."""
from collections import Counter
from pathlib import Path

from lobby_analysis.allocation.oh.classify import (
    classify_bill_label,
    classify_position_shape,
    extract_position_label,
)
from lobby_analysis.allocation.oh.load import load_filings, load_positions

WORKTREE = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
EXTRACT = WORKTREE / "data" / "oh_portal" / "extracted"

filings = load_filings(EXTRACT)
positions = load_positions(EXTRACT)

print("=" * 70, "\nDuplicate filing_ids\n", "=" * 70, sep="")
dup_ids = [fid for fid, n in Counter(filings["filing_id"]).items() if n > 1]
print(f"filing_ids with >1 extraction: {len(dup_ids)}")
for fid in dup_ids[:5]:
    rows = filings[filings["filing_id"] == fid]
    print(f"  {fid}: n_extractions={len(rows)}")
    for sp in rows["source_path"]:
        print(f"    {sp}")

print("\n" + "=" * 70, "\nUnmatched bill_referenced positions\n", "=" * 70, sep="")
unmatched_labels = Counter()
for pos in positions["position_obj"]:
    try:
        kind = classify_position_shape(pos)
    except ValueError:
        continue
    if kind != "bill_referenced":
        continue
    label = extract_position_label(pos)
    cls = classify_bill_label(label, kind)
    if cls == "unmatched":
        unmatched_labels[label] += 1
print(f"Total unmatched bill_referenced labels: {sum(unmatched_labels.values())}")
print("Distinct unmatched labels:")
for lbl, n in unmatched_labels.most_common():
    print(f"  {n}× {lbl!r}")

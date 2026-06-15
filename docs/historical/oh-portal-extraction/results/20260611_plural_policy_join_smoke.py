#!/usr/bin/env python3
"""Smoke test: does OH AER extraction bill_number join to Plural Policy OH_136_bills?

Run after Plural Policy OH 136th GA bulk-CSV lands at `data/bills/OH/136/`.
Collects distinct `positions[].bill_reference.bill_number` across all
`data/oh_portal/extracted/*/*/filing.json` (sonnet extractions; the `_openai`
variant is method-comparison only and excluded), normalizes labels, compares
against `OH_136_bills.csv` `identifier` column.

This is a structural sanity check — if extracted bill labels don't overlap with
the bills bundle, downstream chain composition is dead in the water. The
expected unmatched class is OH Administrative Code (OAC) rule citations
(e.g., '5160-32-02', 'JC 4731-9-01') that OH lobbyists track alongside bills
but that are not in Plural Policy's bill bundle by design — flag them
separately for the future OH chain composer to classify or drop.

Result from 2026-06-11 run on the 316 cached extractions:
  - 86.4% row-weighted join (887/1,027 references)
  - 74.6% distinct-label join (412/552 labels)
  - Unmatched class is exclusively OAC/JC admin-rule citations (not bills)
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXTRACT_DIR = REPO / "data" / "oh_portal" / "extracted"
BILLS_CSV = REPO / "data" / "bills" / "OH" / "136" / "OH_136_bills.csv"


def norm(s: str | None) -> str | None:
    """Normalize a bill identifier label for join.

    OH AER text and Plural Policy both use forms like 'HB 15', 'S.B. 2',
    'Sub. H. B. 96' etc. The bill_number field is already pulled out by the
    extraction, but may carry odd whitespace / case / dotting.
    """
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s.strip().upper())
    s = s.replace(".", "")  # H.B. -> HB
    return s or None


def load_plural_identifiers() -> set[str]:
    ids: set[str] = set()
    with BILLS_CSV.open() as f:
        for row in csv.DictReader(f):
            v = norm(row.get("identifier"))
            if v:
                ids.add(v)
    return ids


def scan_extractions() -> Counter:
    """Count normalized bill_number labels across all sonnet extractions."""
    c: Counter = Counter()
    files = list(EXTRACT_DIR.glob("*/*/filing.json"))
    print(f"scanning {len(files)} filing.json files under {EXTRACT_DIR}")
    for fp in files:
        try:
            d = json.loads(fp.read_text())
        except Exception as e:
            print(f"  WARN: {fp}: {e}")
            continue
        for pos in d.get("positions") or []:
            ref = pos.get("bill_reference") or {}
            label = norm(ref.get("bill_number") or ref.get("original_text"))
            if label:
                c[label] += 1
    return c


def main() -> None:
    plural = load_plural_identifiers()
    print(f"OH_136_bills.csv: {len(plural):,} distinct identifiers")
    print(f"  sample: {sorted(plural)[:6]}")

    extracted = scan_extractions()
    print(f"distinct bill labels in extractions: {len(extracted):,}")
    print(f"total bill-row references: {sum(extracted.values()):,}")
    if not extracted:
        print("\nNo bill references found in extractions - nothing to join.")
        return

    matched = {lbl for lbl in extracted if lbl in plural}
    unmatched = {lbl for lbl in extracted if lbl not in plural}
    print(f"\nMATCHED   labels: {len(matched):,} ({100*len(matched)/len(extracted):.1f}%)")
    print(f"UNMATCHED labels: {len(unmatched):,} ({100*len(unmatched)/len(extracted):.1f}%)")

    matched_rows = sum(extracted[l] for l in matched)
    total_rows = sum(extracted.values())
    print(f"row-weighted match: {matched_rows:,} / {total_rows:,} = {100*matched_rows/total_rows:.1f}%")

    print("\nTop 10 UNMATCHED labels (extraction emits, no Plural row):")
    for lbl, n in sorted([(l, extracted[l]) for l in unmatched], key=lambda x: -x[1])[:10]:
        print(f"  {n:4d}x {lbl}")

    print("\nTop 10 MATCHED labels (sanity check):")
    for lbl, n in sorted([(l, extracted[l]) for l in matched], key=lambda x: -x[1])[:10]:
        print(f"  {n:4d}x {lbl}")


if __name__ == "__main__":
    main()

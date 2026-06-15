"""OH chain composer — Phase 0 pre-flight audit.

Per docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md §5 Phase 0.

Verifies:
  (a) Plural Policy CSV schemas match the 2026-06-11 data-landed result doc.
  (b) Re-run the smoke test on the current extraction cache (may have grown).
  (c) OH allows multi-primary sponsorship empirically.
  (d) bill_actions.csv does NOT carry cosponsor names (WI lesson).

Run from anywhere; uses the worktree's data/ symlink.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WORKTREE = Path("/Users/dan/code/lobby_analysis/.worktrees/oh-chain-composer")
DATA = WORKTREE / "data"
BILLS_DIR = DATA / "bills" / "OH" / "136"
EXTRACT_DIR = DATA / "oh_portal" / "extracted"


def divider(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


# Expected from result doc 2026-06-11
EXPECTED_ROW_COUNTS = {
    "OH_136_bills.csv": 2325,
    "OH_136_bill_identifiers.csv": 2317,
    "OH_136_bill_abstracts.csv": 2336,
    "OH_136_bill_titles.csv": 4139,
    "OH_136_bill_actions.csv": 5549,
    "OH_136_bill_sources.csv": 6396,
    "OH_136_bill_sponsorships.csv": 11559,
    "OH_136_bill_documents.csv": 3803,
    "OH_136_bill_versions.csv": 4077,
    "OH_136_bill_document_links.csv": 3881,
    "OH_136_bill_version_links.csv": 8158,
    "OH_136_votes.csv": 921,
    "OH_136_vote_people.csv": 36023,
    "OH_136_vote_counts.csv": 1842,
    "OH_136_vote_sources.csv": 921,
    "OH_136_organizations.csv": 59,
}


def step_a_schemas() -> None:
    divider("(a) Plural Policy CSV schemas")
    csvs = sorted(BILLS_DIR.glob("*.csv"))
    print(f"Found {len(csvs)} CSVs at {BILLS_DIR}")
    for fp in csvs:
        # row count (subtract header)
        with fp.open() as f:
            n = sum(1 for _ in f) - 1
        with fp.open() as f:
            header = next(csv.reader(f))
        expected = EXPECTED_ROW_COUNTS.get(fp.name)
        drift = ""
        if expected is not None and n != expected:
            drift = f"  ⚠ drift vs 2026-06-11 (was {expected}, now {n}, Δ={n - expected:+d})"
        elif expected is not None:
            drift = "  ✓ matches 2026-06-11"
        print(f"\n{fp.name}: {n:,} rows{drift}")
        print(f"  cols ({len(header)}): {header}")


def step_b_smoke() -> dict:
    divider("(b) Smoke test re-run (vs 2026-06-11: 87/1027 = 86.4% row-weighted, 412/552 = 74.6% distinct)")

    def norm(s: str | None) -> str | None:
        if s is None:
            return None
        s = re.sub(r"\s+", " ", s.strip().upper())
        s = s.replace(".", "")
        return s or None

    plural: set[str] = set()
    with (BILLS_DIR / "OH_136_bills.csv").open() as f:
        for row in csv.DictReader(f):
            v = norm(row.get("identifier"))
            if v:
                plural.add(v)
    print(f"OH_136_bills.csv: {len(plural):,} distinct identifiers")

    extracted: Counter = Counter()
    files = sorted(EXTRACT_DIR.glob("*/*/filing.json"))
    print(f"Scanning {len(files):,} filing.json under {EXTRACT_DIR}")
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
                extracted[label] += 1

    matched = {lbl for lbl in extracted if lbl in plural}
    total_rows = sum(extracted.values())
    matched_rows = sum(extracted[l] for l in matched)
    distinct_labels = len(extracted)
    distinct_match = len(matched)
    print(f"\nFilings scanned: {len(files)}")
    print(f"Bill-row references: {total_rows:,}")
    print(f"Distinct labels: {distinct_labels:,}")
    print(f"DISTINCT-LABEL MATCH: {distinct_match} / {distinct_labels} = {100*distinct_match/distinct_labels:.1f}%")
    print(f"ROW-WEIGHTED MATCH:   {matched_rows} / {total_rows} = {100*matched_rows/total_rows:.1f}%")
    return {
        "filings_scanned": len(files),
        "bill_rows": total_rows,
        "distinct_labels": distinct_labels,
        "distinct_match_pct": round(100 * distinct_match / distinct_labels, 2) if distinct_labels else None,
        "row_weighted_match_pct": round(100 * matched_rows / total_rows, 2) if total_rows else None,
    }


def step_c_multi_primary() -> dict:
    divider("(c) Multi-primary sponsorship — empirical check on OH_136_bill_sponsorships.csv")
    fp = BILLS_DIR / "OH_136_bill_sponsorships.csv"
    # bill_id -> classification -> count
    by_bill: dict[str, Counter] = defaultdict(Counter)
    with fp.open() as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        print(f"sponsorships cols: {cols}")
        for row in reader:
            bid = row.get("bill_id") or row.get("bill") or ""
            cls = (row.get("classification") or "").strip()
            by_bill[bid][cls] += 1
    primary_counts = Counter(c.get("primary", 0) for c in by_bill.values())
    print(f"\nDistribution of 'primary' sponsor count per bill (across {len(by_bill):,} bills):")
    for k in sorted(primary_counts):
        print(f"  primary={k}: {primary_counts[k]:,} bills")
    multi_primary_bills = sum(n for k, n in primary_counts.items() if k > 1)
    print(f"\nBills with ≥2 primary sponsors: {multi_primary_bills:,}")
    cosponsor_counts = Counter(c.get("cosponsor", 0) for c in by_bill.values())
    sample = [(k, cosponsor_counts[k]) for k in sorted(cosponsor_counts)[:10]]
    print(f"\nDistribution of 'cosponsor' count per bill (first 10 buckets): {sample}")
    return {
        "bills_with_sponsorships": len(by_bill),
        "primary_count_distribution": dict(primary_counts),
        "multi_primary_bills": multi_primary_bills,
    }


def step_d_actions_cosponsor_check() -> dict:
    divider("(d) bill_actions.csv — does the description carry cosponsor names? (WI-lesson check)")
    fp = BILLS_DIR / "OH_136_bill_actions.csv"
    with fp.open() as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        print(f"bill_actions cols: {cols}")
        # Sample first 200 rows and scan for cosponsor keywords
        keyword_re = re.compile(r"(?i)\bcosponsor|co-sponsor\b")
        n = 0
        hits = []
        for row in reader:
            n += 1
            desc = row.get("description") or ""
            if keyword_re.search(desc):
                hits.append((row.get("bill_id", ""), desc[:120]))
            if n >= 5549:  # all rows
                break
        print(f"Scanned {n:,} rows")
        print(f"Cosponsor-keyword hits: {len(hits):,}")
        for bid, snippet in hits[:5]:
            print(f"  {bid}: {snippet!r}")
    return {"actions_rows": n, "cosponsor_keyword_hits": len(hits)}


def main() -> None:
    if not DATA.exists():
        print(f"ERROR: data/ not found at {DATA}")
        sys.exit(2)
    step_a_schemas()
    smoke = step_b_smoke()
    multi = step_c_multi_primary()
    actions = step_d_actions_cosponsor_check()

    divider("SUMMARY")
    print(json.dumps({"smoke": smoke, "multi_primary": multi, "actions": actions}, indent=2))


if __name__ == "__main__":
    main()

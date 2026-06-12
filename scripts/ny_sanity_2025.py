"""Phase 3 sanity-check over the materialized releases/ny 2025 TSVs.

Validates (a) headline aggregates, (b) dollar conservation at two levels, and
(c) top filers for portal spot-check. Reads only the (small) release TSVs +
recomputes the filing-comp total independently from the grain-collapsed values.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

REL = Path("releases/ny")


def read_tsv(name):
    with (REL / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def D(s):
    return Decimal(s) if s not in (None, "") else None


clients = read_tsv("NY_clients.tsv")
lobbyists = read_tsv("NY_lobbyists.tsv")
filings = read_tsv("NY_filings.tsv")
links = read_tsv("NY_filing_bill_links.tsv")

print("=== counts ===")
print(f"clients:           {len(clients):,}")
print(f"lobbyists:         {len(lobbyists):,}")
print(f"filings:           {len(filings):,}")
print(f"filing_bill_links: {len(links):,}")

# distinct bills
bill_ids = {r["bill_id"] for r in links}
bill_pv = {r["bill_print_version"] for r in links}
print(f"distinct bill_id (base, OS-join key):   {len(bill_ids):,}")
print(f"distinct bill_print_version (suffixed):  {len(bill_pv):,}")

# total compensation across distinct filings
total_comp = sum((D(r["total_compensation"]) or Decimal(0)) for r in filings)
n_comp_present = sum(1 for r in filings if r["total_compensation"] not in (None, ""))
print("\n=== compensation ===")
print(f"total_compensation (sum over {len(filings):,} filings): ${total_comp:,.2f}")
print(f"filings with comp present: {n_comp_present:,} / {len(filings):,}")
print(f"filings with $0 or absent comp: {len(filings)-n_comp_present:,}")

# ---- conservation check 1: SUM(comp_per_bill) == filing_compensation per filing ----
# Group links by (filing_id, lobbyist_id, client_id) — the firm is load-bearing:
# a shared client form_submission_id carries multiple firms' bill links, each
# with its own filing_compensation. Grouping on (filing_id, client_id) alone
# pools them and the conservation check fails spuriously.
by_filing = defaultdict(list)
for r in links:
    by_filing[(r["filing_id"], r["lobbyist_id"], r["client_id"])].append(r)

violations = []
checked = 0
for key, group in by_filing.items():
    fc = D(group[0]["filing_compensation"])
    if fc is None:
        continue
    s = sum((D(r["comp_per_bill"]) or Decimal(0)) for r in group)
    checked += 1
    if s != fc:
        violations.append((key, str(fc), str(s)))
print("\n=== conservation 1: SUM(comp_per_bill)==filing_compensation per filing ===")
print(f"filings checked (comp present, >=1 bill): {checked:,}")
print(f"violations: {len(violations)}")
for v in violations[:5]:
    print("  VIOLATION:", v)

# ---- conservation check 2: link-side filing_compensation total reconciles ----
# Sum filing_compensation once per (filing_id, client_id) group; should match the
# comp total restricted to filings that have >=1 bill link.
linked_comp = Decimal(0)
for key, group in by_filing.items():
    fc = D(group[0]["filing_compensation"])
    if fc is not None:
        linked_comp += fc
print("\n=== conservation 2: comp attributable to bill-linked filings ===")
print(f"sum filing_compensation over bill-linked filings: ${linked_comp:,.2f}")
print(f"(remainder is comp on filings with no real bill: ${total_comp-linked_comp:,.2f})")

# ---- top lobbyist firms by summed filing comp (for portal spot-check) ----
firm_comp = defaultdict(Decimal)
firm_name = {}
for r in filings:
    firm_comp[r["lobbyist_id"]] += (D(r["total_compensation"]) or Decimal(0))
for r in lobbyists:
    firm_name[r["id"]] = r["name"]
top_firms = sorted(firm_comp.items(), key=lambda kv: kv[1], reverse=True)[:10]
print("\n=== top 10 lobbyist firms by summed 2025 filing comp ===")
for fid, amt in top_firms:
    print(f"  ${amt:>14,.2f}  {firm_name.get(fid,'?')}  [{fid}]")

# ---- top clients by summed filing comp ----
client_comp = defaultdict(Decimal)
client_name = {r["id"]: r["name"] for r in clients}
for r in filings:
    client_comp[r["client_id"]] += (D(r["total_compensation"]) or Decimal(0))
top_clients = sorted(client_comp.items(), key=lambda kv: kv[1], reverse=True)[:10]
print("\n=== top 10 beneficial clients by summed 2025 filing comp ===")
for cid, amt in top_clients:
    print(f"  ${amt:>14,.2f}  {client_name.get(cid,'?')}  [{cid}]")

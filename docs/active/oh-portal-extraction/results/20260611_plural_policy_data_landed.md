# 2026-06-11 — Plural Policy OH 136th GA bulk-CSV landed; chain-side join smoke-tested clean

**Branch / surface:** main (doc-only update; OH branch `oh-portal-aprime-batch` already merged via PR #33).
**Trigger:** Dan dropped `data/PluralPolicy_OH_136_csv.zip` (15.7 MB) — the lawmaker↔bill leg blocker called out in `STATE_COVERAGE.md` OH section footnote 7 + STATUS row 64 pending item (b).

## What landed

```
data/bills/OH/
├── PluralPolicy_OH_136_csv.zip   (15.7 MB, preserved)
├── README                          (Plural Policy export metadata; State=OH Session=136 Generated 2026-06-07 23:19 UTC; CSV Format v2.1)
└── 136/
    ├── OH_136_bills.csv            2,325 bills
    ├── OH_136_bill_identifiers.csv 2,317 rows  (alt-id map)
    ├── OH_136_bill_abstracts.csv   2,336
    ├── OH_136_bill_titles.csv      4,139
    ├── OH_136_bill_actions.csv     5,549
    ├── OH_136_bill_sources.csv     6,396
    ├── OH_136_bill_sponsorships.csv 11,559   (person+org primaries+cosponsors)
    ├── OH_136_bill_documents.csv   3,803
    ├── OH_136_bill_versions.csv    4,077
    ├── OH_136_bill_document_links.csv 3,881
    ├── OH_136_bill_version_links.csv  8,158
    ├── OH_136_votes.csv              921
    ├── OH_136_vote_people.csv      36,023
    ├── OH_136_vote_counts.csv      1,842
    ├── OH_136_vote_sources.csv       921
    └── OH_136_organizations.csv       59
```

Layout mirrors `data/bills/WI/2025/`. The 136 directory name preserves Plural Policy's session-number convention (Ohio's 136th GA = 2025–2026 biennium).

## Join smoke-test

Script: `20260611_plural_policy_join_smoke.py` (sibling file in this directory).

Goal: confirm that the OH AER extraction outputs (`data/oh_portal/extracted/*/*/filing.json`, n=316) reference bills using a label format that joins to `OH_136_bills.csv.identifier`. If they don't, downstream chain composition is dead in the water.

Method: walk every `positions[].bill_reference.bill_number`, normalize (uppercase, strip spaces, drop dots), compare against the `identifier` column. Counts both distinct labels and row-weighted references.

| Metric | Value |
|---|---|
| Cached extractions scanned | 316 |
| Total `positions[].bill_reference` rows | 1,027 |
| Distinct bill labels in extractions | 552 |
| OH_136_bills.csv distinct identifiers | 2,317 |
| **Distinct-label match (extractions ∩ Plural)** | **412 / 552 = 74.6%** |
| **Row-weighted match** | **887 / 1,027 = 86.4%** |

Top matched labels (sanity-check signal):

```
 81× HB 96      ← FY 2026-27 state operating budget (most-lobbied, sane)
 12× SB 197
 12× HB 54
 12× HB 298
 11× HB 1
 10× SB 88
  8× HB 344
  8× SB 2
  7× HB 276
  7× HB 15
```

## What the 13.6% unmatched class is

**Not a data-quality problem.** The unmatched labels are exclusively **Ohio Administrative Code (OAC) rule citations**, not bills. Sample top-10 unmatched:

```
1× 5160-32-02
1× JC 4731-24-03
1× JC 4901:1-16-01 THROUGH 4901:1-16-06
1× 5123-4-03
1× 5123-1-03
1× JC 4759-4-01
1× JC 4731-9-01
1× JC 4761-7-04
1× JC 4731-35-01
1× JC 4731-6-30
```

These are:
- Bare 4-digit-dash-2-digit codes (e.g., `5160-32-02`) — OAC rule citations (Ohio Administrative Code), the regulatory rule layer underneath statute.
- `JC ...` prefix — Joint Committee on Agency Rule Review (JCARR) hearings on those administrative rules.

OH lobbyists track rule advocacy alongside bill advocacy on the AER form. Plural Policy's bill bundle (as expected) covers legislative bills only, not OAC/JCARR. **Implication for the future OH chain composer:** these need a separate "regulatory" classification (or to be dropped) — they will not join to `OH_136_bills.csv` and should not be mistaken for a join failure.

## What this unblocks / leaves open

**Unblocked:** STATE_COVERAGE.md OH footnote 7 first half — session bundle is now local at `data/bills/OH/136/`.

**Still pending:**
- **`oh.csv` legislator roster** — separate Plural Policy artifact (`openstates.org/data/legislators-csv/oh.csv`). Analog of `data/bills/WI/wi.csv`. Needed for `ocd-person/...` ID resolution on the sponsorship leg.
- **OH chain composer** — per Anna Karenina, this needs fresh design (OH has lobbyist↔lawmaker gift/meal edges natively per AER Section II.A/B, no compensation disclosure, and the OAC carve-out above). Planned for Day 4 of `leave-behind-prep` per STATUS row 65.
- **`releases/oh/chain/`** — downstream of the composer.
- **Full-corpus extraction** — pending Batches API + caching + transient retry build (~$800), tracked at issue #35; orthogonal to this session.

## Provenance

- Source zip mtime: 2026-06-08 15:48 (file contents dated 2026-06-07 23:19 UTC).
- A newer hash-named zip (`OH_136_csv_3jGHvyBQu2a2fMHlSV0S4A.zip`, file mtime 2026-06-11, contents dated 2026-06-10) is also present in `data/`; per Dan it is the same dataset under a different name (Plural Policy re-export naming, not a content delta).
- Smoke-test was run against the 06-07 zip contents (the dataset Dan named in the handoff).

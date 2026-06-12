# NY Phase 4 — chain composer + Open States join

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Built Phase 4: the end-to-end **company → lobbyist → bill → lawmaker → $** chain
(`allocation/ny/chain.py` + `cli.py`), joining the Phase-3 `releases/ny/` tables
to the Open States / Plural Policy NY 2025-2026 bill-sponsorship bundle. No IPF —
NY discloses the lobbyist→bill link directly, so the chain is a join plus two
deterministic transforms: the Decision-7 coalition beneficiary split and the
Decision-8 bill-id normalizer.

Work was split by data dependency. The OS-independent half (coalition split +
the shared `even_split` conservation primitive) was built first while Dan staged
the gated OS bundle, and committed separately (`af02ef5`). Once the bundle
landed, the OS-dependent half followed: the bill-id normalizer (calibrated to
OS's real identifier format), the OS bill loader, the composer, the CLI, and the
release output + README.

A real-data smoke test caught two bugs before commit — a glob that matched the
wrong file (zeroing the sponsor join) and a conservation-dedup key that omitted
`lobbyist_id`. Both root-caused and fixed (the second became a regression test
mirroring the Phase-3 firm-collapse bug at the chain layer). Final chain
conserves dollars to the cent against the Phase-3 release.

## Topics Explored

- OS NY identifier format (the Decision-8 gate): verified against the staged
  bundle before writing the normalizer.
- Coalition `beneficial_client` prevalence on real release data.
- Bill-id match rate, with vs without amendment-suffix stripping.
- Whether WI connects "parties lobbied" (Dan's question) and whether NY should.

## Provisional Findings

- **OS NY identifier = `<LETTER><SPACE><UNPADDED-DIGITS>`** (`A 1668`, `S 550`):
  single space, no zero-padding, no print suffix. The normalizer canonicalizes
  the lobbying id to this form (strip `-A/-B`, drop leading zeros, insert space).
- **Match rate: 99.5% of distinct bills / 99.8% of link rows** with
  suffix-stripping; only **81.3%** without — suffix-stripping is worth ~18 pts
  of chain closure. Validates Decision 5/8.
- **Conservation holds to $0:** summing `comp_per_cell` over distinct
  `(filing, lobbyist, beneficiary, bill)` cells = **$153,064,191.00** = the
  Phase-3 bill-linked release total exactly.
- **Coalition split:** 346 coalition clients (M up to 31); 12.8% of link rows
  reference a coalition client; multiplicative split `C/(M·N)` conserves C.
- Each NY bill has **exactly one primary sponsor**; 213 distinct sponsors across
  the chain = the full NY legislature (150 Assembly + 63 Senate). Cosponsors
  (~83k) deferred per plan.
- **WI does not connect "parties lobbied"** — its lawmaker edge is the bill
  primary sponsor (identical to NY); its only imputation (IPF) is *hours*
  allocation, not lawmakers. **NY actually discloses `parties_lobbied`** but it
  is free-text names/titles and was **not fetched** in the filtered 2025 `$select`
  pull (9 fields only). So a real disclosed lawmaker edge exists but needs a
  re-pull + name resolution — a v1.1 enhancement, not an imputation.

## Decisions Made

- **Coalition split is chain-layer only** (Dan): `NY_clients.tsv` keeps the raw
  semicolon string; no Phase-3 re-cut.
- **Bill-id normalizer defers to OS's format** (Decision 8 confirmed against real
  data): strip suffix + leading zeros, insert space.
- **Ship the 53 MB chain TSV committed** in `releases/ny/chain/` (Dan, overriding
  the gitignore-and-regenerate recommendation). Trips GitHub's >50 MB warning
  (not a block).
- **v1 ships the sponsor edge; `parties_lobbied` is the top v1.1 follow-up.**

## Results

- [`results/20260605_ny_phase4_chain_aggregates.md`](../results/20260605_ny_phase4_chain_aggregates.md)
  — match rate, conservation, chain aggregates, coalition prevalence.

## Open Questions

- Ingest `parties_lobbied` as a second, disclosed lawmaker edge? (needs re-pull +
  free-text → `ocd-person` resolution).
- Decode `&amp;` HTML entities in names (carried verbatim now).
- Cosponsors as a secondary sponsor edge; multi-year backfill (2019→).

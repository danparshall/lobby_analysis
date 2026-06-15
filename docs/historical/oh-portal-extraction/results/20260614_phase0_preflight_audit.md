# 2026-06-14 — OH chain composer Phase 0 pre-flight audit

**Branch:** `oh-chain-composer` (continuing from f59a7f9 — Phase 1 classifier shipped).
**Trigger:** Plan §5 Phase 0 pre-flight, per `plans/20260611_oh_chain_composer_design.md` step 5 of the implementer checklist.
**Script:** `20260614_phase0_preflight_audit.py` (sibling file in this directory).

## What this audit verifies

| Check | Plan reference | Result |
|---|---|---|
| (a) Plural Policy CSV schemas match the 2026-06-11 data-landed result doc | §5 Phase 0 step 1 | ✓ 16/16 CSVs row-count-stable; columns documented |
| (b) Smoke-test row-weighted match has not drifted | §5 Phase 0 step 2 | ✓ 86.4% (identical — cache has not grown since 06-11) |
| (c) OH allows multi-primary sponsorship empirically | §5 Phase 0 step 3 | ✓ 946 of 2,317 bills (40.8%) have ≥2 primaries |
| (d) `bill_actions.csv` does NOT carry cosponsor names (WI lesson) | §5 Phase 0 step 4 | ✓ 0 cosponsor-keyword hits across 5,525 action rows |
| (e) Download `oh.csv` legislator roster (Q3 → yes) | §7 Q3 + handoff Phase 0 | ✓ 132 legislators (99 House + 33 Senate) at `data/bills/OH/oh.csv` |

## (a) Plural Policy schemas — column inventory

All 16 CSVs row-count-stable vs the 2026-06-11 data-landed doc. Header columns (load-bearing for the loaders to type against):

| CSV | Rows | Columns |
|---|---:|---|
| `OH_136_bills.csv` | 2,325 | `id, identifier, title, classification, subject, session_identifier, jurisdiction, organization_classification` |
| `OH_136_bill_identifiers.csv` | 2,317 | `id, bill_id, identifier` |
| `OH_136_bill_abstracts.csv` | 2,336 | `id, bill_id, abstract, note` |
| `OH_136_bill_titles.csv` | 4,139 | `id, bill_id, title, note` |
| `OH_136_bill_actions.csv` | 5,549 | `id, bill_id, organization_id, description, date, classification, order` |
| `OH_136_bill_sources.csv` | 6,396 | `id, note, url, bill_id` |
| `OH_136_bill_sponsorships.csv` | 11,559 | `id, name, entity_type, organization_id, person_id, bill_id, primary, classification` |
| `OH_136_bill_documents.csv` | 3,803 | `id, bill_id, note, date, classification, extras` |
| `OH_136_bill_versions.csv` | 4,077 | `id, bill_id, note, date, classification, extras` |
| `OH_136_bill_document_links.csv` | 3,881 | `id, media_type, url, document_id` |
| `OH_136_bill_version_links.csv` | 8,158 | `id, media_type, url, version_id` |
| `OH_136_votes.csv` | 921 | `id, identifier, motion_text, motion_classification, start_date, result, organization_id, bill_id, bill_action_id, jurisdiction, session_identifier` |
| `OH_136_vote_people.csv` | 36,023 | `id, vote_event_id, option, voter_name, voter_id, note` |
| `OH_136_vote_counts.csv` | 1,842 | `id, vote_event_id, option, value` |
| `OH_136_vote_sources.csv` | 921 | `id, note, url, vote_event_id` |
| `OH_136_organizations.csv` | 59 | `id, name, parent_id, jurisdiction_id, classification, sources, links, other_names, created_at, updated_at, extras` |

**Note on the sponsorships schema:** there are TWO sponsor-shape columns — `primary` (boolean-ish, "is this a primary?") and `classification` (string, `"primary"` or `"cosponsor"`). The plan filter uses `classification`; this audit also uses `classification` and gets clean buckets. The `primary` boolean is presumably redundant with `classification == "primary"` but worth a paranoia-check in the loader unit tests.

**bill_actions structural notes:** row count via `csv.reader` is 5,525 (vs 5,549 file lines after header — 23-row delta is multi-line `description` fields with embedded newlines; csv.reader handles them correctly). Loaders must use `csv` (or pandas with `quoting='\\"'`) — naïve newline splitting will undercount.

## (b) Smoke-test re-run — identical to 06-11

| Metric | 2026-06-11 | 2026-06-14 | Δ |
|---|---:|---:|---|
| Cached extractions scanned | 316 | 316 | 0 |
| Total `positions[].bill_reference` rows | 1,027 | 1,027 | 0 |
| Distinct bill labels in extractions | 552 | 552 | 0 |
| Distinct-label match (extractions ∩ Plural) | 412 / 552 = 74.6% | 412 / 552 = 74.6% | 0.0pp |
| Row-weighted match | 887 / 1,027 = 86.4% | 887 / 1,027 = 86.4% | 0.0pp |

The cache has not grown — issue #35 (the $800 full-corpus extraction) has not run. The composer can be built and validated against this 316-filing slice; a Q1-locked **preview release** will be the materialization output (Phase 6).

## (c) Multi-primary sponsorship — CONFIRMED structural for OH

Distribution of `classification == "primary"` count per bill (across 2,317 bills with sponsorships):

| Primaries on bill | Bills | % |
|---:|---:|---:|
| 1 | 1,371 | 59.2% |
| 2 | 924 | 39.9% |
| 3 | 5 | 0.2% |
| 4 | 4 | 0.2% |
| 5 | 1 | 0.0% |
| 7 | 1 | 0.0% |
| 8 | 2 | 0.1% |
| 11 | 1 | 0.0% |
| 50 | 1 | 0.0% |
| 98 | 3 | 0.1% |
| 99 | 4 | 0.2% |
| **≥2 (total)** | **946** | **40.8%** |

**Two-primaries-or-one is the dominant shape**: 99.1% of bills have ≤2 primaries (1,371 + 924 = 2,295). The Plural Policy `bill_sponsorships.classification` filter is structurally clean — no need for additional disambiguation.

**The high-primary tail is exclusively ceremonial resolutions**, not substantive legislation. All 9 bills with ≥10 primaries are House Resolutions (`HR`) memorializing or honoring people:

```
primary= 99  HR 369    In memory of L. Helen Rankin.
primary= 99  HR 118    In memory of Ronald Edward Hood.
primary= 99  HR 263    Honoring Wendy Zhan on her retirement as the director of the Ohio Legislative Service Commission.
primary= 99  HR 38     In memory of Ross Allen Boggs, Jr.
primary= 98  HR 255    In memory of Mary Rose Oakar.
primary= 98  HR 234    In memory of Jack Cera.
primary= 98  HR 138    Honoring Don Jones for his exemplary service to the Ohio House of Representatives.
primary= 50  HR 241    In memory of Charles James Kirk.
primary= 11  HR 365    In memory of Master Sergeant Tyler Simmons.
```

99 = essentially the whole 99-seat House signing on as primary. Plural Policy is reflecting this faithfully; it's not a data anomaly.

**Implication for the chain composer:** if a lobbyist happens to file a position on `HR 369`, the cross-product emits 99 chain rows (one per primary sponsor). Truthful but voluminous. Two mitigations to consider for the README:
1. Document the high-primary tail as a known structural artifact (ceremonial resolutions); analysts should expect `SUM(amount_dollars)` rollups to be safe (no money in resolutions) but `COUNT(DISTINCT bill_label_raw)` to be the correct denominator for "how many bills did the lobbyist track."
2. Surface a `num_primary_sponsors` column on each chain row (already in the plan §4 schema sketch) so analysts can filter or de-dupe.

Multi-primary distribution by bill-identifier prefix (among the 946 multi-primary bills):

```
HB: 626   SB: 148   HR: 84   SR: 45   HCR: 30   HJR: 7   SCR: 3   SJR: 3
```

Substantive legislation dominates — multi-primary is a real OH practice on HBs and SBs, not just a resolution quirk. The composer's cross-product is exercising a real signal.

## (d) `bill_actions.description` cosponsor-name check — clean

Scanned 5,525 action rows for `\bcosponsor|co-sponsor\b` (case-insensitive): **0 hits**.

This means the WI lesson does NOT apply to OH. In WI, cosponsor identities lived in free-text `bill_actions.description` strings (forcing the cosponsor parser into the actions table). In OH, cosponsors live cleanly in `bill_sponsorships.csv` with `classification == "cosponsor"`. Phase 1's loader for `bill_sponsorships` is sufficient; no `bill_actions` parsing is needed for Q2's primary-only-now / cosponsor-v1.1 path.

## (e) `oh.csv` legislator roster — downloaded

URL probed: `https://data.openstates.org/people/current/oh.csv` → HTTP 200, 88,210 bytes, 132 rows + header.

Columns (load-bearing for the chain TSV's `sponsor_lawmaker_name` and the gifts TSV's `lawmaker_id` resolver):

```
id (ocd-person/...), name, current_party, current_district, current_chamber (lower/upper),
given_name, family_name, gender, email, biography, birth_date, death_date, image, links,
sources, capitol_address, capitol_voice, capitol_fax, district_address, district_voice,
district_fax, twitter, youtube, instagram, facebook, wikidata
```

132 legislators = 99 House + 33 Senate (OH's standard chamber sizes). Sample row:

```
ocd-person/0c6a7bcf-e990-41a0-b59c-923f05771880, Adam Bird, Republican, 63, lower, ...
```

Landed at `data/bills/OH/oh.csv` (i.e., `~/data/lobby_analysis/bills/OH/oh.csv` via the worktree's `data/` symlink). Closes the second half of `STATE_COVERAGE.md` OH footnote 7.

## What this unblocks

All Phase 0 checks green. Phase 1 (loaders) is unblocked. Phase 1 classifier (Steps A+B) already shipped at f59a7f9; Step C — `src/lobby_analysis/allocation/oh/load.py` — proceeds next under TDD with these verified column shapes as the structural-assertion truth.

## What stays open

- **Issue #35 (full-corpus extraction, ~$800)** — orthogonal to Phases 1–5. Q1-locked: a preview release against the 316-slice ships first; #35 dictates only whether/when a non-preview release follows.
- **Cosponsor parsing (Q2 v1.1 follow-up)** — `OH_136_bill_sponsorships.csv` carries the `classification == "cosponsor"` rows already. The v1.1 follow-up is purely a config flip in the loader filter, plus a chain-row multiplier review in the README.

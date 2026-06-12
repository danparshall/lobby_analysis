# OH chain composer — design plan (v0)

**Originating session:** [2026-06-11 main — Plural Policy 136th GA bundle landed](../results/20260611_plural_policy_data_landed.md)
**Workstream:** OH disclosure data (Track B / Prong 2). Continuation of `oh-portal-aprime-batch` (merged PR #33).
**Status:** plan only — no code yet. Ready for fresh-session implementer.
**Audience:** the next agent that picks this up (likely Day 4 of `leave-behind-prep` per STATUS row 65).

---

## 1. Why this plan exists

The OH workstream is at the same point WI was when `wi-allocation-matrix` started: extraction is validated, source-of-truth bill metadata is on disk, and the next deliverable is a **`releases/oh/chain/` Suhan-droppable TSV** mirroring `releases/wi/chain/WI_chain_2025.tsv` (115K rows, 15 columns, methodology README).

Per the **Anna Karenina principle**, OH's chain composer is **NOT a port** of WI's. The data shape is structurally different on three of the six edges. The point of this plan is to surface the design choices that differ before any code is written, so the implementer doesn't conflate the two.

---

## 2. What's already in place

| Asset | Location | Owner |
|---|---|---|
| OH AER extractions (316 cached, 0.7% of universe) | `data/oh_portal/extracted/*/*/filing.json` | merged via PR #33 |
| OH discovery TSV (45,605 AERs, full universe) | `data/oh_portal/discover/recent.tsv` (gitignored, regenerable) | merged via PR #33 |
| OH portal modules | `src/lobby_analysis/oh_portal/` (discover/fetch/extract/pipeline/batch/provenance/extraction_brief) | merged |
| Plural Policy 136th GA bills bundle | `data/bills/OH/136/` (16 CSVs; 2,325 bills, 11,559 sponsorship rows) | **landed 2026-06-11** |
| Plural Policy zip preserved | `data/bills/OH/PluralPolicy_OH_136_csv.zip` | landed 2026-06-11 |
| Smoke-test result | [`../results/20260611_plural_policy_data_landed.md`](../results/20260611_plural_policy_data_landed.md) | landed 2026-06-11 |
| Smoke-test script (reusable) | [`../results/20260611_plural_policy_join_smoke.py`](../results/20260611_plural_policy_join_smoke.py) | landed 2026-06-11 |

**Outstanding prerequisites (not blockers, but should be honest about them):**

1. **Full-corpus extraction (~$800, ~24 hr async via Batches API + caching + retry) is pending** at [issue #35](https://github.com/danparshall/lobby_analysis/issues/35). Composer will be designed against the 316-filing slice; whether to **run** against the slice or wait for the full corpus is Open Question #1 below.
2. **`oh.csv` legislator roster not yet downloaded.** Analog of `data/bills/WI/wi.csv`. Source: `openstates.org/data/legislators-csv/oh.csv`. Needed for human-readable lawmaker names on the chain. Plural Policy sponsorship rows already carry `person_id = ocd-person/...` so structural join works without it; `oh.csv` would supply the display-name layer.

---

## 3. Why OH is structurally different from WI and NY

The chain composer's shape follows the edge inventory of the underlying disclosure form. OH's edge inventory (from [`docs/STATE_COVERAGE.md`](../../../STATE_COVERAGE.md) OH section):

| Edge | OH AER status | WI shape | NY shape | OH shape |
|---|---|---|---|---|
| principal ↔ lobbyist $ | **✗ not disclosed** | IPF inference from row+col sums | JOIN on per-pair total_compensation | **skip — no signal** |
| principal ↔ lobbyist time | ✗ not disclosed | hours_comm + hours_other (filed %) | — | **skip — no signal** |
| principal ↔ lawmaker $ | back-projectable via lobbyist+gift | out of scope (campaign finance) | out of scope | back-projectable (Phase 2 candidate) |
| principal ↔ bill | via lobbyist's positions list | bill_efforts at principal grain | per-filing parties_lobbied (per-set) | **via lobbyist's positions (~)** |
| **lobbyist ↔ lawmaker $** | **✓ NATIVE (Section II.A gifts; II.B meals)** | — | contact-only, no $ | **OH's distinctive edge — make it first-class** |
| lobbyist ↔ bill | positions[] in extraction | bill_efforts × allocation | — | positions[] in extraction |
| lawmaker ↔ bill | Plural Policy sponsorships | Plural Policy sponsorships | Plural Policy sponsorships | Plural Policy sponsorships |

**Three structural deltas vs WI:**

1. **No IPF required.** WI used IPF because principal↔lobbyist time was disclosed at row sums (principal) AND column sums (lobbyist) but not per-pair. OH has neither row nor column sums for $ or time — there's nothing to fit. The composer is **pure edge enumeration**, more like NY's JOIN than WI's IPF.
2. **The gifts edge is NATIVE to OH.** WI has no analog of AER Section II.A (per-gift `recipient_name` + `amount`). This is OH's contribution to the cross-state corpus — the chain composer should expose this edge as **its own TSV** (`releases/oh/gifts/`) alongside the bill chain, not bury it as a sub-column.
3. **No stance disclosed.** Same as WI (and NY). Chain says "lobbied on," not "for or against." Document this in the README the same way WI's does.

**Two structural deltas vs NY:**

- **No per-pair $ marginal on principal↔lobbyist.** NY composes its chain in part by allocating `total_compensation` proportionally; OH has nothing to allocate.
- **OAC admin-rule citations** in the lobbyist↔"bill" edge (13.6% of extracted bill-row references, per smoke test). Plural Policy bundle does not contain OAC rules. Composer must classify and route these — they are not bills, they are regulatory activity.

---

## 4. Proposed output artifacts

Mirror the `releases/wi/chain/` convention but split OH's distinctive edge into a sibling artifact:

```
releases/oh/
├── README.md                       (state-level overview; pattern: releases/wi/README.md, releases/ny/README.md)
├── chain/
│   ├── OH_chain_2025_2026.tsv      (per-(period, principal, lobbyist, bill, sponsor) — bill-side chain)
│   └── README.md                   (methodology writeup, Suhan-droppable, mirroring releases/wi/chain/README.md)
└── gifts/
    ├── OH_gifts_2025_2026.tsv      (per-(period, lobbyist, lawmaker, gift) — OH's distinctive native edge)
    └── README.md                   (Section II.A/B methodology + AER quirks)
```

**Schema sketch for `OH_chain_2025_2026.tsv`** (decide at implementation; this is v0, not locked):

| Column | Type | Notes |
|---|---|---|
| `report_period` | str | OH AER reporting period (e.g. `2025-01-01..2025-04-30`, `2025-05-01..2025-08-31`); 3 periods/year on OH |
| `filing_id` | str | AER report ID — joins back to provenance |
| `principal_name` | str | from `LobbyingFiling.employer` |
| `principal_id` | str | `org-<slug>` from extraction (no canonical OH employer ID; resolution layer is a separate concern) |
| `lobbyist_name` | str | from `LobbyingFiling.filer_person` |
| `lobbyist_id` | str | `person-<slug>` from extraction |
| `bill_label_raw` | str | `positions[].bill_reference.original_text` (e.g. `HB 96`) |
| `bill_label_normalized` | str | normalized for join key (e.g. `HB 96`) |
| `bill_class` | str | `bill` / `oac_rule` / `jcarr` / `unmatched` — see OAC classification §6 |
| `bill_id` | str \| null | `ocd-bill/...` when `bill_class == 'bill'`; null otherwise |
| `bill_title` | str \| null | from `OH_136_bills.csv` |
| `position_description` | str | `positions[].description` — what the lobbyist said they did |
| `num_primary_sponsors` | int | OH allows multi-primary sponsorship (verify on `OH_136_bill_sponsorships.csv`) |
| `sponsor_lawmaker_id` | str | `ocd-person/...` |
| `sponsor_lawmaker_name` | str | from `oh.csv` if downloaded; else surname from `OH_136_bill_sponsorships.csv` |
| `sponsor_role` | str | `primary` / `cosponsor` (per-row; Plural Policy classification column) |
| `confidence` | str | `direct` (extracted + joined) / `oac_dropped` / `unmatched` / `null_extraction` |

**Schema sketch for `OH_gifts_2025_2026.tsv`** (OH's distinctive native edge):

| Column | Type | Notes |
|---|---|---|
| `report_period` | str | same as chain |
| `filing_id` | str | joins to provenance |
| `principal_name` | str | indirect — lobbyist's employer for the period |
| `lobbyist_name` | str | filer of the AER |
| `lawmaker_name_raw` | str | `gifts[].recipient_name` from extraction |
| `lawmaker_id` | str \| null | resolved via `oh.csv` matcher (if downloaded); else null |
| `event_type` | enum | `gift` (Section II.A) / `meal` (Section II.B) |
| `description` | str | what was given |
| `amount_dollars` | decimal | per-row $ |
| `date` | date | event date |

**Conservation rules to document in READMEs** (lessons learned from WI):

- **Do not aggregate `bill_label_raw` across `sponsor_role` rows naively.** A bill with 3 sponsors appears 3× per filing — a `SUM(amount)` over the table would triple-count any dollars. (Same shape as WI's `modeled_hours_per_sponsor` cautionary.)
- **`bill_class != 'bill'` rows do not join to Plural Policy.** Document this explicitly so an analyst doesn't go hunting for missing OAC rules in the bills bundle.

---

## 5. Phases (TDD)

Pre-execution: this plan should be re-read by the implementing agent. Open questions in §7 must be resolved with Dan before Phase 1.

| Phase | Scope | Cost | Tests |
|---|---|---|---|
| **Phase 0 — Pre-flight audit** | Load Plural Policy CSVs into pandas, inspect schemas, verify the smoke-test result against current cache (extractions can grow between this plan and execution). Confirm OH allows multi-primary sponsorship empirically. Confirm `bill_actions.csv` does NOT carry cosponsor names (WI lesson — cosponsors only in `bill_actions.description` free text). | $0 | RED: structural pandas assertions on CSV schemas; sanity counts. GREEN: pure-read code. |
| **Phase 1 — Loaders + classifier** | `src/lobby_analysis/allocation/oh/load.py` — load extractions + Plural Policy CSVs as typed pandas DataFrames. `src/lobby_analysis/allocation/oh/classify.py` — `bill_class` classifier (regex: `HB|SB|HR|SR|HJR|SJR|HCR|SCR` → `bill`; `JC ` prefix → `jcarr`; pure-numeric OAC pattern `\d+-\d+-\d+` → `oac_rule`; else `unmatched`). | $0 | TDD: classifier round-trips known examples from §3 above; loader DataFrames have expected columns + non-empty. |
| **Phase 2 — Chain composer** | `src/lobby_analysis/allocation/oh/chain.py` → `compose_bill_chain(extractions_dir, plural_dir) -> DataFrame`. Cross-product per filing: each position × each primary sponsor (+ cosponsors per §7 Q3). | $0 | TDD: hand-crafted test fixture w/ 1 filing × 2 positions × 1 bill × 2 sponsors → 4 rows; conservation invariant. |
| **Phase 3 — Gifts edge composer** | `src/lobby_analysis/allocation/oh/gifts.py` → `compose_gifts(extractions_dir, oh_csv_path \| None) -> DataFrame`. Independent of chain composer. | $0 | TDD: per-row attribution; `oh.csv` matcher tested with/without the file present. |
| **Phase 4 — CLI + materialize** | `src/lobby_analysis/allocation/oh/cli.py` → `python -m lobby_analysis.allocation.oh.cli materialize --extractions ... --bills ...`. Writes `releases/oh/chain/OH_chain_2025_2026.tsv` + `releases/oh/gifts/OH_gifts_2025_2026.tsv`. | $0 | TDD: CLI integration test with a 1-filing fixture; output TSV row count + column shape. |
| **Phase 5 — READMEs + release** | Author `releases/oh/README.md` + `releases/oh/chain/README.md` + `releases/oh/gifts/README.md` mirroring WI's Suhan-droppable pattern. | $0 | None (docs); manual review against `releases/wi/chain/README.md`. |
| **Phase 6 — Full-corpus run (separate decision)** | If §7 Q1 → "wait for full corpus": defer Phase 6 to post-#35. Else: run composer against current cache and ship a "preview" release. | depends on §7 Q1 | n/a |

Cumulative API spend through Phase 5: **$0** (all transformation on already-extracted data + already-downloaded Plural Policy data). The $800 is in #35, not here.

---

## 6. OAC / JCARR classification — design note

The 13.6% unmatched class is structural, not noise. Plural Policy bill bundles cover legislative bills only; OH lobbyists track three classes of advocacy on the AER:

| Pattern | Class | Example | Source data |
|---|---|---|---|
| `HB \d+`, `SB \d+`, `HR \d+`, `SR \d+`, `HJR \d+`, `SJR \d+`, `HCR \d+`, `SCR \d+` | `bill` | `HB 96` | `OH_136_bills.csv` |
| `JC \d+-\d+-\d+` | `jcarr` | `JC 4731-24-03` | not in Plural Policy — joint committee on administrative rule review |
| `\d+-\d+-\d+` (no `JC` prefix) | `oac_rule` | `5160-32-02` | not in Plural Policy — Ohio Administrative Code rule |
| else | `unmatched` | (TBD — should be empty if classifier is complete) | n/a |

The composer should emit these rows but mark them `bill_id = null`, `bill_class != 'bill'`. **Do not drop them silently** — a Suhan-facing audit will want to see "lobbyists tracked X OAC rules" as a finding, not a hidden gap.

---

## 7. Open questions (decide with Dan at execution-session start)

These are recommendations with rationale; the implementer should confirm before coding.

### Q1. Run against the 316-filing slice now, or wait for full-corpus extraction (#35)?

**Recommendation: build composer + ship a "preview" release against the 316-filing slice.**

Rationale:
- Composer code is the same in either case; running against the slice surfaces design bugs before the $800 full run.
- A preview release is honest about its scope (label clearly `OH_chain_2025_2026_preview.tsv`); analogous to WI's per-phase shipping.
- Day-4 timeline for `leave-behind-prep`: the slice run is hours; the full run is 24 hr async.

Downside: the 316-filing slice is not representative — 53% of those filings were nil, and the slice was sampled from agents-with-recent-activity; coverage of small-volume principals will be sparse.

### Q2. Cosponsors: include or primary-only?

**Recommendation: primary-only for v1 (matches WI's Phase 3 v1 scope).**

Rationale:
- WI's `wi-allocation-matrix` cosponsor parsing was explicitly deferred to a follow-up branch (4 refinement candidates flagged at merge).
- OH Plural Policy `bill_sponsorships.csv` carries a `classification` column (`primary` / `cosponsor`) — structurally clean to filter, easy to extend later.
- Primary-only halves the cross-product, keeps the TSV size manageable.

Cosponsor follow-up should be a separate branch — same parity rule as WI.

### Q3. Download `oh.csv` legislator roster as part of this plan, or defer?

**Recommendation: download as part of Phase 0.**

Rationale:
- Mechanical, $0 cost, $0 LLM spend; just a URL fetch.
- Provides display-name layer for the chain TSV's `sponsor_lawmaker_name` — without it, the column is just surname-fragment from Plural Policy's `bill_sponsorships.csv`.
- Closes the second half of `STATE_COVERAGE.md` OH footnote 7 in one stroke.

Provenance: `wget https://data.openstates.org/people/current/oh.csv -O data/bills/OH/oh.csv` (or whatever the current canonical Plural Policy people-data URL is — verify at execution time; `data.openstates.org` paths sometimes move).

### Q4. Bucket filter equivalent — what about expenditures?

**Recommendation: chain TSV covers `positions[]` only (bill-side advocacy). Gifts TSV covers Section II.A/B (gifts + meals). Expenditures (Section II.C/D — bulk expenditures, retirement system contributions) are NOT in v1.**

Rationale:
- Expenditures are aggregate-level (per-period totals), not per-bill or per-lawmaker. They don't compose a "chain" row.
- Treating them as a separate `releases/oh/expenditures/` artifact may make sense later, but not in v1.

### Q5. Branch hygiene — where does this work live?

**Recommendation: cut a fresh `oh-chain-composer` branch + worktree from current main at execution start. Don't add this work to `oh-portal-aprime-batch` (merged) or `oh-portal-extraction` (archived, awaiting promotion to historical).**

Rationale: clean branch hygiene; merges to main cleanly without dragging archived branch state.

---

## 8. Pre-execution checklist (read before starting)

The implementing agent should:

1. Read this plan end-to-end.
2. Read [`../results/20260611_plural_policy_data_landed.md`](../results/20260611_plural_policy_data_landed.md) — the data-drop session that produced this plan.
3. Read [`releases/wi/chain/README.md`](../../../../releases/wi/chain/README.md) and skim `src/lobby_analysis/allocation/wi/chain.py` — the precedent.
4. Read `docs/STATE_COVERAGE.md` OH section (the 6-row matrix in §3 above is a summary; the source-of-truth is the doc).
5. Re-run [`../results/20260611_plural_policy_join_smoke.py`](../results/20260611_plural_policy_join_smoke.py) on the current cache — verify the 86.4% number hasn't drifted (extractions may have grown).
6. Surface Q1, Q2, Q3, Q4, Q5 to Dan with rationale before Phase 1 RED. Per `skills/test-driven-development/SKILL.md` and Nori-flow protocol.
7. Cut `oh-chain-composer` branch + worktree per `skills/using-git-worktrees/SKILL.md`. Symlink `data/` into the worktree (mandatory per CLAUDE.md "Worktree data discipline" — `data/` holds irreplaceable cached extractions).

---

## 9. What this plan does NOT cover

To keep scope honest:

- **Full-corpus extraction (#35)** — orthogonal; this composer can run against any extraction set.
- **Stance inference** — OH AER does not collect stance per Section I (same as WI). Out of scope for this composer, out of scope for the project until a state's form discloses it.
- **`principal↔lawmaker $` back-projection through lobbyist gifts** — interesting Phase 2 candidate (treat gifts as principal-via-lobbyist contact spend), but design-deferred until v1 ships.
- **Cross-state composition** — Anna Karenina; this plan composes OH only.
- **Cosponsor parsing** — see Q2; deferred to follow-up branch matching WI's pattern.
- **Schema-versioning the chain TSV** — adopt the WI convention (v1.0 → v1.1 with `item_id` disambiguator) at the moment a breaking change is needed; don't pre-version.

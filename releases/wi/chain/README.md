# Wisconsin lobbying chain — 2025-2026 session (v1.1)

`WI_chain_2025.tsv` — a modeled per-`(semester, principal, lobbyist, bill, sponsor)` chain joining the published WI 2025-2026 disclosure data (the 6 TSVs one directory up) to bill sponsorship from the Wisconsin Legislature, with per-lobbyist effort hours inferred via IPF and per-sponsor effort hours normalized by primary-sponsor count.

**Audience:** colleagues who want the influence graph "company → lobbyist → bill → lawmaker" without having to assemble it from the 6 source TSVs themselves. This is a *derived* artifact — different shape than the source TSVs in `releases/wi/`. Read "What this is" and "What this isn't" before quantitative use.

---

## TL;DR

| | |
|---|---|
| **Rows** | 115,229 (46,446 H1 + 68,783 H2) |
| **Columns** | 15 (see Schema below) |
| **File size** | ~38 MB |
| **Coverage** | Wisconsin 2025-2026 legislative session — semesters H1 (Jan-Jun 2025) and H2 (Jul-Dec 2025), Legislative Bills/Resolutions bucket only |
| **Distinct principals** | 525 |
| **Distinct lobbyists** | 511 |
| **Distinct bills** | 984 |
| **Distinct sponsors** | 133 (132 legislators + 1 collective entity — Joint Legislative Council) |
| **Total modeled hours (per-sponsor-normalized)** | 48,789 |
| **Confidence label distribution** | 87.8% `ipf_fit` / 8.0% `exact` / 4.2% `zero_filed` |

---

## Provenance

| | |
|---|---|
| **Originating branch** | `wi-allocation-matrix` (merged from this PR; archived at [`docs/historical/wi-allocation-matrix/`](../../../docs/historical/wi-allocation-matrix/) post-merge) |
| **Source disclosure data** | The 6 TSVs in [`releases/wi/`](..) (one directory up) — merge commit [`5fcc6ac`](https://github.com/danparshall/lobby_analysis/commit/5fcc6ac) |
| **Source bill-sponsorship data** | [Plural Policy](https://open.pluralpolicy.com/) bulk CSV download — `WI_2025_bill_sponsorships.csv` + bill metadata + the WI legislator roster (`wi.csv` with `ocd-person/...` IDs). Plural Policy is the bulk-data face of OpenStates. |
| **Generating code** | [`src/lobby_analysis/allocation/wi/`](../../../src/lobby_analysis/allocation/wi/) — `load.py`, `graph.py`, `ipf.py`, `materialize.py`, `legislature.py`, `chain.py`, `cli.py` |
| **Methodology writeup (Suhan-facing)** | [`docs/historical/wi-allocation-matrix/results/20260602_wi_chain_synthesis.md`](../../../docs/historical/wi-allocation-matrix/results/20260602_wi_chain_synthesis.md) — standalone synthesis with TL;DR, 6-relation framing, chain construction in plain language, modeling assumptions consumers are trusting, findings, what the chain can and can't answer |
| **Per-phase technical writeups** | [`docs/historical/wi-allocation-matrix/results/`](../../../docs/historical/wi-allocation-matrix/results/) — Phases 0 (data audit), 1 (graph), 2 (IPF), 3 (chain), 3.1 (per-sponsor normalization), LeMahieu bill inspection, unknown-chamber audit |
| **Reproducer** | See "Reproducer" section below — requires fetching the Plural Policy bulk CSV in addition to the source `releases/wi/` data |

---

## Schema

15 columns, tab-separated, sorted deterministically by `(semester, principal_id, lobbyist_id, bill_id, sponsor_lawmaker_id)`.

| Column | Type | Example | Notes |
|---|---|---|---|
| `semester` | str | `2025-H1` / `2025-H2` | The same (principal, lobbyist, bill) tuple can appear in both semesters with different hours and percents |
| `principal_id` | int | `11091` | Joins to `releases/wi/WI_principals.tsv` |
| `principal_name` | str | `DoorDash, Inc.` | from same |
| `lobbyist_id` | int | `11077` | Joins to `releases/wi/WI_lobbyists.tsv` |
| `lobbyist_name` | str | `Clark Kaericher` | from same |
| `item_id` | int | `24507` | Joins to `releases/wi/WI_principal_bill_efforts.tsv` — disambiguates WI bill-id collisions (multiple distinct bills can share the same canonical `bill_id`; see Conservation rules below and caveat #4) |
| `bill_id` | str | `SB 256` | OpenStates short identifier; **not unique within a biennium** (see `item_id` and Conservation rules below) |
| `bill_title` | str | `Relating to: ...` | from Plural Policy bill metadata |
| `modeled_hours` | float | `9.872997` | `(hours_comm + hours_other) × (filed_percent / 100)` — replicated to every primary sponsor of this bill. **Do not aggregate this across sponsors** (see Conservation rules below). Use `modeled_hours_per_sponsor` for sponsor-level aggregation. |
| `num_sponsors_on_bill` | int | `15` | Count of primary sponsors on this bill in the Plural Policy data |
| `modeled_hours_per_sponsor` | float | `0.658200` | `modeled_hours / num_sponsors_on_bill` — the **honest metric for aggregating across sponsors**. Conservation invariant (enforced by test): `SUM(modeled_hours_per_sponsor)` over a `(semester, principal, lobbyist, item_id)` group equals `modeled_hours`. Uniform-share allocation is a **modeling assumption**, not a disclosed share. |
| `principal_filed_percent` | float | `0.21` | Float in [0, 1]; from the principal's filed bill-effort percentage |
| `sponsor_lawmaker_id` | str | `ocd-person/...` | OpenStates person ID for individual legislators; **name string** for collective entities (Joint Legislative Council) |
| `sponsor_lawmaker_name` | str | `LeMahieu` | Surname for legislators (with disambiguation prefix when shared — e.g. `B. Jacobson`, `L. Johnson`); full entity name for collective entities. **Join on `sponsor_lawmaker_id`, not surname** — surname is fragile when prefixes are present. |
| `attribution_confidence` | str | `ipf_fit` | One of: `exact` (uniquely pinned by constraints, no inference), `ipf_fit` (max-entropy fit from IPF), `zero_filed` (cell is on an authorization edge but a marginal is zero), `aggregation_flagged` (involves a lobbyist whose self-filed hours are implausibly high — descriptive only, not pejorative; see methodology writeup) |

To get the chamber for a sponsor, join `sponsor_lawmaker_id` → the Plural Policy WI legislator CSV (`wi.csv`) `.id` → `.current_chamber` (`lower` = Assembly, `upper` = Senate).

---

## Conservation rules / aggregator gotchas

**Read this before writing any aggregation query against the chain.** These are the two load-bearing rules that protect against silent over/undercounting.

### Rule 1 — A cell's identity is `(semester, principal_id, lobbyist_id, item_id)`, never `bill_id` alone

WI bill IDs are not unique across sessions or chambers: principal 11473 filed bill-effort against multiple distinct bills both labeled `Assembly Bill 1` (voter-ID vs education-assessment), and similarly for AB 6 and AB 10. The disambiguator is `item_id` — the unique source-row identifier the WI portal assigns. `bill_id` is its human-readable label, possibly ambiguous.

Aggregations that `GROUP BY bill_id` (without `item_id`) will silently merge effort filed on different bills into one bucket. Empirically the collision rate is low — Phase 3.1 found 3 out of 10,290 conservation groups affected in 2025-2026 (~0.03%) — but the merge is silent, so the rule is qualitative discipline: always include `item_id` in the cell key.

### Rule 2 — Do not sum `modeled_hours` across the sponsor rows of one cell

When a bill has N primary sponsors, the `modeled_hours` value for that cell is **replicated** across the N sponsor rows (the modeled hours attach to the bill, not subdivided per lawmaker). The honest per-sponsor metric is `modeled_hours_per_sponsor = modeled_hours / num_sponsors_on_bill`.

- **Aggregating by principal / lobbyist / bill (where the sponsor is NOT the group-by axis):** dedupe to the cell key first (`(semester, principal_id, lobbyist_id, item_id)`), then sum `modeled_hours`. Equivalent: don't dedupe, sum `modeled_hours_per_sponsor` — the two give the same answer by construction.
- **Aggregating by sponsor (where the sponsor IS the group-by axis):** sum `modeled_hours_per_sponsor` directly (do not dedupe).

`modeled_hours_per_sponsor` is computed under a **uniform-share modeling assumption** — "lead author and 9th co-author are equally lobbied." Probably false in practice, but the right neutral default until position-weighted attribution is designed. Carry that caveat into any sponsor-level claim.

These rules originate in the Phase 3 / 3.1 work on the `wi-allocation-matrix` branch — see [`docs/historical/wi-allocation-matrix/results/20260602_phase_3_1_per_sponsor_normalization.md`](../../../docs/historical/wi-allocation-matrix/results/20260602_phase_3_1_per_sponsor_normalization.md) for the worked-example that motivated each rule.

---

## What this is — a 30-second tour of the chain construction

This isn't a black-box output. Each of the three stages below is standard textbook math for its sub-problem; the synthesis writeup explains it in plain English. The TL;DR:

1. **Bipartite graph + IPF on (lobbyist, principal) hours.** WI lobbyists file aggregate hours per semester (no per-principal breakdown); WI principals file per-(principal, lobbyist) hours. Iterative Proportional Fitting fits the per-(lobbyist, principal) hours matrix from the two marginals subject to the authorization edge graph as the support pattern. Where the constraints uniquely pin a cell (a lobbyist with one principal or vice versa), we mark it `exact`; otherwise `ipf_fit`.
2. **Proportional bill attribution.** A lobbyist's hours are spread across their principal's bill mix in proportion to the principal's filed bill-effort percentages. This is a *modeling assumption*: "lobbyist Y attacks principal P's bill mix proportionally." It's the natural default in the absence of per-lobbyist-per-bill ground truth.
3. **Per-sponsor normalization.** A bill's modeled hours are split evenly across its primary sponsors via `modeled_hours_per_sponsor = modeled_hours / num_sponsors_on_bill`. This is a second modeling assumption: "lead author and 9th co-author are equally lobbied." Probably false in practice, but the right neutral default until a position-weighted scheme is designed.

---

## What this isn't (limitations bounding what claims it supports)

1. **Primary sponsors only.** Cosponsors are not in the chain. The Plural Policy bulk dump's structured sponsor list contains only `classification='primary'` rows; cosponsors live in `bill_actions.description` text and are not yet parsed. Aggregations like "lawmaker X's chain weight" exclude their cosponsorships.
2. **No campaign-finance leg.** The principal→lawmaker $-flow edge (and the lobbyist→lawmaker personal-donation edge) are not in this release. Adding them requires the Wisconsin Ethics Commission's CFIS database, which is separate from the lobbying disclosure portal. Scoping is on a follow-up branch.
3. **No position direction.** WI lobbying filings disclose *that* a principal lobbied on a bill, not *which side*. The chain detects coalition activity, not coalition composition. Listing Americans For Prosperity next to ATC Management on an electric-utility bill, for instance, reads as "industry coalition" by default — which may be the inverse of what's happening if AFP is lobbying against. Verify position direction from external evidence (testimony records, press releases) before quoting any coalition claim externally.
4. **Legislative Bills/Resolutions bucket only.** The chain emits rows only for the bucket with named bill IDs principals filed against (4,035 of 7,345 bill-effort rows in the source). Three other buckets are skipped:
   - Topics Not Yet Assigned A Bill Or Rule Number (2,327 rows, 31.7% of source)
   - Budget Bill Subjects (856 rows)
   - Administrative Rulemaking Proceedings (127 rows)
   Including these is a Phase 3+ refinement candidate.
5. **2025 semesters only.** Phase 2's allocation matrix covers 2025-H1 and 2025-H2; 2026-period effort rows are skipped (they exist in the source but were out of scope for v1).
6. **16 bills with zero structured sponsors** (procedural / Joint Legislative Council vehicles in the bulk CSV) produce no chain rows.
7. **The chain is hours-grain, not dollar-grain.** WI lobbyist filings are Time Reports — no per-bill compensation field exists in WI disclosure. There is no `comp_per_cell` analog here (unlike NY's chain). If you need dollars, work from `releases/wi/WI_principal_filings.tsv` directly — that has total expenditure per principal per semester, which is the only $-grain WI publishes.

---

## Headline finding

The chain's cleanest single-bill signal is **SB 28 (electric-transmission right-of-first-refusal legislation)**. Senate Majority Leader Devin LeMahieu introduced it as sole primary sponsor; 29 principals filed effort on it, heavily concentrated in the electric-utility industry (ATC Management — the incumbent transmission monopoly the bill benefits — at 331 hours, followed by WEC Energy at 134, WI Industrial Energy Group at 124, and the major investor-owned utilities). Americans For Prosperity also filed substantial effort (86 hours), but per "What this isn't" #3 above, the chain cannot infer their position. Full inspection: [`docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md`](../../../docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md).

Chamber distribution after per-sponsor normalization is roughly balanced (Assembly 26,543 hr / Senate 21,657 hr / Joint Legislative Council 590 hr — lower:upper ratio 1.23×); the pre-normalization metric had a 3.4× Assembly skew that was an artifact of Assembly bills carrying more primary co-authors than Senate bills.

---

## Sample analyses (with protective patterns called out)

Each snippet below demonstrates a correct aggregation pattern that respects the Conservation rules above. Comments name the gotcha each one avoids.

```python
import pandas as pd
chain = pd.read_csv("WI_chain_2025.tsv", sep="\t")
```

### 1. Top principals by chain weight on a specific bill

```python
# Each (semester, principal, lobbyist, item_id) cell is replicated across the
# bill's primary sponsors with `modeled_hours` repeated. Dedupe to the cell key
# BEFORE summing modeled_hours. Equivalent: sum modeled_hours_per_sponsor over
# all rows (no dedupe needed). Both give the same answer by construction.
sb28 = chain[chain["bill_id"] == "SB 28"]
cells = sb28.drop_duplicates(
    subset=["semester", "principal_id", "lobbyist_id", "item_id"]
)
top_on_sb28 = (
    cells.groupby("principal_name")["modeled_hours"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
```

### 2. Lawmakers most lobbied (across the whole chain)

```python
# When the sponsor IS the group-by key, use `modeled_hours_per_sponsor` directly
# (no dedupe — each row's contribution IS the per-sponsor uniform share).
# Reminder: the uniform-share split is a modeling assumption ("lead author and
# 9th co-author equally lobbied"), not a disclosed allocation.
top_lawmakers = (
    chain.groupby(["sponsor_lawmaker_id", "sponsor_lawmaker_name"])[
        "modeled_hours_per_sponsor"
    ]
    .sum()
    .sort_values(ascending=False)
    .head(20)
)
# Join `sponsor_lawmaker_id` to wi.csv (Plural Policy) for chamber/party.
```

### 3. Total modeled chain weight per principal across the full session

```python
# Same cell-identity discipline as Sample 1 — dedupe by cell, then sum
# modeled_hours. Each principal's total here equals their total filed
# (hours_comm + hours_other) × principal_filed_percent rolled across all bills.
cells = chain.drop_duplicates(
    subset=["semester", "principal_id", "lobbyist_id", "item_id"]
)
principal_totals = (
    cells.groupby("principal_name")["modeled_hours"]
    .sum()
    .sort_values(ascending=False)
)
```

### 4. Filter by attribution confidence for cautious analyses

```python
# `aggregation_flagged` marks cells involving a lobbyist whose self-filed
# hours are implausibly high (e.g., lobbyist 11072 / Deanna Pettack ≈ 32
# hours/day across a full semester — see releases/wi/README.md Caveat 1).
# Descriptive label, not pejorative. Useful pre-publication review filter.
flagged = chain[chain["attribution_confidence"] == "aggregation_flagged"]
flagged_principals = sorted(flagged["principal_name"].unique())

# Or, restrict to cells uniquely pinned by the IPF constraints (no inference):
exact_only = chain[chain["attribution_confidence"] == "exact"]
```

### 5. Single-semester view (e.g. compare H1 to H2)

```python
# The same (principal, lobbyist, item_id) tuple can appear in both semesters
# with independently-filed hours. Always include `semester` in cell-identity
# grouping when crossing semesters, or filter to one semester first.
h2 = chain[chain["semester"] == "2025-H2"]
h2_cells = h2.drop_duplicates(
    subset=["principal_id", "lobbyist_id", "item_id"]  # semester is fixed
)
h2_totals = h2_cells.groupby("principal_name")["modeled_hours"].sum()
```

---

## Reproducer

The chain depends on two source bundles: the 6 TSVs in `releases/wi/` (already in this repo) plus a Plural Policy bulk CSV download (external to this repo).

```bash
# 1. Fetch the Plural Policy WI 2025 bill bundle (~1 MB)
#    Currently at: https://open.pluralpolicy.com/data/session-csv/
#    You want the WI 2025 session CSV bundle (~15 normalized tables) plus the
#    WI legislator CSV from /data/legislator-csv/ (currently wi.csv).
#    Place the bundle at the path the CLI expects (see the allocation module).

# 2. Run the WI allocation pipeline (loads, fits IPF, composes chain, materializes TSV)
uv run python -m lobby_analysis.allocation.wi.cli materialize-chain \
    --state wi --vintage 2025 \
    --releases-dir releases/wi \
    --plural-dir <path-to-plural-bundle>
```

Wall time is ~1 min end-to-end (mostly the IPF fit on the 835-node giant connected component). Reproducibility is exact: the materialized output is sorted deterministically, so re-runs produce a byte-identical TSV when sources are unchanged.

---

## Open follow-ups

| Item | Where it goes |
|---|---|
| Phase 4 — WI CFIS (Ethics Commission campaign-finance) scoping | New branch off post-merge main |
| Cosponsor parsing from `bill_actions.description` | New branch off post-merge main (design decisions: schema shape, `num_sponsors_on_bill` interaction, regex test corpus) |
| Non-legislative-bill effort buckets (TNYB topics, budget, rulemaking) | Phase 3+ refinement candidate |
| 2026 semesters | Needs Phase 2 IPF refit |
| Position-weighted sponsor attribution (vs uniform-share) | Refinement, requires design |
| Per-cell IPF residual exposure as a numeric column | Refinement candidate |

---

## License & usage

Source data is public-record disclosure data from the Wisconsin Ethics Commission and the Wisconsin Legislature (via Plural Policy / OpenStates). This release is shared under the project's repo license. If you cite this chain, please include both the source `releases/wi/` commit and the wi-allocation-matrix merge commit, plus the Plural Policy / OpenStates attribution for the bill-sponsorship data.

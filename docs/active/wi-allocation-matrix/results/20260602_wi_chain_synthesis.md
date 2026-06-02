# WI 2025-2026 lobbying chain — synthesis

**Date:** 2026-06-02
**Branch:** `wi-allocation-matrix`
**Audience:** project lead (Suhan) and anyone reviewing what the WI chain currently does and doesn't show.
**Materialized output:** `data/allocations/WI/WI_chain_2025.tsv` (115,229 rows, 15 columns, ~38 MB)

This document is a standalone synthesis of the `wi-allocation-matrix` branch through Phase 3.1 (2026-05-30 → 2026-06-02). It pulls together what the five phase-specific writeups produce piecewise and is written to be read on its own — no prior branch context assumed. Phase docs referenced inline are linked from the [RESEARCH_LOG](../RESEARCH_LOG.md) if you want to step deeper into any one finding.

---

## TL;DR

We have, for Wisconsin 2025-2026 (semesters 2025-H1 and 2025-H2), a 115,229-row chain that maps **principal → lobbyist → bill → sponsoring lawmaker** with modeled per-sponsor effort hours and a per-row confidence label. 97.9% of the legislative effort rows in the underlying WI principal filings produce at least one chain row. The chain is the answer to Suhan's "company → lobbyist → lawmaker → bill" ask, except for the final **lawmaker → $-flow** link, which structurally requires the WI Ethics Commission's CFIS campaign-finance database (separate from lobbying disclosure, not yet integrated — Phase 4).

Two findings from this chain are worth a Suhan-level read right now:

1. **Senate Majority Leader Devin LeMahieu's #8 ranking is 98.8% driven by a single bill** — SB 28, electric-transmission right-of-first-refusal (ROFR) legislation where he is the sole primary sponsor. 29 principals filed effort on the bill, heavily concentrated in the electric-utility industry (ATC Management at 331 hrs, followed by WEC Energy, WI Industrial Energy Group, and the major investor-owned utilities). This is the chain's cleanest example of a single-bill industry-coalition signal — and it was completely invisible in the pre-Phase-3.1 metric (where it was spread across every Assembly co-author of every Assembly bill). Bill-level inspection: [`20260602_lemahieu_bill_inspection.md`](20260602_lemahieu_bill_inspection.md).
2. **The "Assembly is more lobbied than Senate" finding from the original chain was a metric artifact.** With per-sponsor normalization the lower:upper chamber ratio drops from 3.4× → 1.2× and 8 of the top 10 individually-lobbied sponsors are Senate. Lobbying effort is roughly balanced between chambers; the distribution *shapes* differ in interpretable ways.

The chain has known limitations that bound what claims it can support — most importantly, **primary sponsors only** (cosponsors are not yet parsed) and **no campaign-finance leg** (CFIS not yet integrated). The "What this can and can't answer" section below is the operative guide.

---

## The question — what Suhan asked for

The branch charter is to produce, for Wisconsin 2025-2026 from public disclosure data, the chain:

> Company W spends X via lobbyist Y on bill Z sponsored by lawmaker A who received $B from W.

That's a join across four entity types — {principal, lobbyist, lawmaker, bill} — which decomposes into **6 pairwise relations**. We classified each by where the data lives and how directly it's available:

| Relation | Source | Status in WI 2025-2026 |
|---|---|---|
| principal ↔ lobbyist | WI lobbying authorizations | **Direct** (sworn filing) |
| principal ↔ bill (with effort %) | WI principal expenditure report | **Direct** (sworn filing) |
| lobbyist ↔ hours (aggregate, by activity type) | WI lobbyist activity report | **Direct** (sworn filing) — but only aggregate, not per-bill |
| lobbyist ↔ bill | not filed | **Modeled** (Phase 2 IPF — see below) |
| lawmaker ↔ bill | WI Legislature bill records | **Direct external** (free, structured) |
| principal ↔ lawmaker ($-flow) | WI Ethics Commission (CFIS) | **External — not yet integrated** (Phase 4 scoping) |
| lobbyist ↔ lawmaker (direct contact) | not filed | **Structurally absent** in WI (no contact-log mandate) |

A central correction came on day one of the branch (kickoff convo, [`20260530`](../convos/20260530_wi_allocation_matrix_kickoff.md)): the `principal ↔ bill (with effort %)` link is **directly filed by the principal**, not modeled. WI principals file an expenditure report that allocates their lobbying spend across specific bills as percentages — this is sworn disclosure, not inference. This corrected an early framing that had treated principal→bill as an attribution problem.

The single relation that requires non-trivial modeling within WI lobbying data is **lobbyist ↔ bill**, because lobbyists file only aggregate hours per semester (with no bill breakdown), while principals file aggregate hours per lobbyist *and* bill effort percentages. This is a bipartite matrix-completion problem with known marginals on both axes — the standard textbook setup for Iterative Proportional Fitting (IPF).

---

## What we built

### The chain TSV

`data/allocations/WI/WI_chain_2025.tsv` is the deliverable. One row per `(semester, principal, lobbyist, bill, sponsor)` tuple. 115,229 rows across:

| Axis | Count |
|---|---:|
| Semesters | 2 (`2025-H1`, `2025-H2`) |
| Principals | 525 |
| Lobbyists | 511 |
| Bills | 984 |
| Sponsors | 133 (132 legislators + 1 collective entity) |
| Total modeled hours (per-sponsor-normalized) | 48,789 |
| Per-row confidence labels (chain TSV) | 87.8% `ipf_fit` / 8.0% `exact` / 4.2% `zero_filed` |

Columns (15):

```
semester, principal_id, principal_name, lobbyist_id, lobbyist_name,
item_id, bill_id, bill_title, modeled_hours, num_sponsors_on_bill,
modeled_hours_per_sponsor, principal_filed_percent,
sponsor_lawmaker_id, sponsor_lawmaker_name, attribution_confidence
```

Every row carries the source `item_id` from the principal filing, so consumers can trace any chain row back to the exact disclosure row that generated it. The chain is sorted deterministically so diffs across reruns are meaningful.

### Source inputs

The chain composes from two source bundles:

**WI lobbying disclosure** — `releases/wi/` on `main`, merged 2026-05-27 (`5fcc6ac`), 6 TSVs, $47.5M total spend across 944 principals for the 2025-2026 biennium. Schema documented in `releases/wi/README.md`. The three load-bearing inputs for the chain:

- `WI_principal_filings.tsv` — per-(principal, lobbyist, semester) hours filed *by the principal*, broken into "communicating" and "other" hours-types
- `WI_lobbyist_filings.tsv` — per-(lobbyist, semester) aggregate hours filed *by the lobbyist*, same two hours-types, no per-principal breakdown
- `WI_principal_bill_efforts.tsv` — per-(principal, bill, semester) effort percentages filed by the principal, applied to that semester's total principal-side hours

**WI Legislature bill sponsorship** — bulk CSV download from Plural Policy (https://open.pluralpolicy.com/data/session-csv/), which is the same database that backs OpenStates. Bills × primary sponsors with structured `ocd-person/...` identifiers on 99.8% of sponsorship rows.

---

## How the chain is built

The math sits in three stages. None of them is exotic; each is the standard textbook approach for its sub-problem. The point of laying them out here is so that "modeled hours" doesn't read as a black box.

### Stage 1 — Bipartite graph of who-could-have-worked-for-whom

For each semester, we build a bipartite graph: nodes are principals and lobbyists, edges are active authorizations (from `WI_principal_lobbyist_authorizations_unified.tsv`, filtered to the semester window — `authorized_on <= semester_end AND (withdrawn_on is null OR withdrawn_on >= semester_start)`). About 1,900 active edges per semester.

This graph decomposes into **connected components** — clusters where every principal can reach every lobbyist through the authorization roster, but the clusters are disjoint from each other. In the 2025 WI data, both semesters are dominated by one giant component (~835 nodes in H1, ~900 in H2) plus 70+ small ones and ~140 isolated singletons (a single lobbyist authorized by a single principal, or vice versa).

The decomposition matters because IPF works component-by-component: cells in different components are decoupled by construction.

### Stage 2 — IPF to fill in the (lobbyist, principal) hours matrix

Within each component, we want to fill in a matrix where rows are lobbyists, columns are principals, cells are hours. We know:

- **Row marginals** (one per lobbyist): the lobbyist's aggregate hours from their own filing.
- **Column marginals** (one per principal): the principal's hours-per-lobbyist sum from the principal's filing (this is per-lobbyist already, so for singleton-lobbyist principals the cell is *exactly pinned* — no fitting needed).
- **Support pattern**: the authorization edges. Cells not on an edge are forced to zero.

Where the constraints uniquely determine a cell (a lobbyist authorized by exactly one principal, or a principal with exactly one lobbyist), we mark the cell `exact` — no inference is happening, the constraints leave only one possible value. Where the constraints leave room (a lobbyist authorized by multiple principals, in a component with multiple other free cells), we run **Iterative Proportional Fitting (IPF / RAS)**, which finds the maximum-entropy distribution of hours consistent with the row sums, column sums, and support pattern. We mark those cells `ipf_fit`.

Two label cases are worth flagging:

- **`zero_filed`** — the cell is on an authorization edge (the lobbyist *could* have worked for the principal) but one of the marginals is zero, so the cell is zero by arithmetic. This is preserved deliberately so consumers can spot "authorized but didn't file any hours" cases.
- **`aggregation_flagged`** — a small number of cells (0.3% in H1) involve a lobbyist whose self-filed hours are implausibly high (e.g., Pettack at lobbyist 11072 reports 7,611 total hours for 2025-H1, ~32 hrs/day). The plan's original assumption was these would need exclusion from IPF. The actual data is more interesting: Pettack and her 6 SAA-family principals form their own small connected component, the marginals balance internally, and IPF fits the component honestly. We label the cells descriptively rather than excluding them, and let consumers decide how to treat them. **The label is descriptive, not pejorative** — we do not have evidence about whether the aggregation is illegal under WI §13.62; it's a portal artifact whose source we know.

The 4 label distribution on the materialized hours matrix (Phase 2 output): 6.4% `exact` / 90.8% `ipf_fit` / 2.5% `zero_filed` / 0.3% `aggregation_flagged`.

### Stage 3 — Join through bill efforts and per-sponsor normalization

From the (lobbyist, principal) hours matrix, we compute per-bill modeled hours by applying the principal's filed effort percentages: `modeled_hours(lobbyist, principal, bill) = hours(lobbyist, principal) × principal_filed_percent(principal, bill)`. This is the "lobbyist X attacks employer P's bill mix proportionally" assumption — the natural default in the absence of per-lobbyist-per-bill ground truth, and the modeling choice that consumers should know they're trusting.

Then we join to bill sponsors from the Plural Policy bulk CSV. The first version of this join (Phase 3 v1) replicated `modeled_hours` to every primary-sponsor row, which made `SUM(modeled_hours) GROUP BY sponsor` over-count by sponsor count — a serious problem because Assembly bills typically carry many primary co-authors (~10+) while Senate bills carry few (~3-4), so the metric *systematically* inflated Assembly sponsors. Phase 3.1 fixed this by adding **`modeled_hours_per_sponsor = modeled_hours / num_sponsors_on_bill`**, the uniform-share normalization. Both columns are in the TSV; `modeled_hours` is preserved unchanged for back-compat, but **`modeled_hours_per_sponsor` is the honest metric for aggregating across sponsors.**

The conservation invariant is enforced by test: `SUM(modeled_hours_per_sponsor)` over a `(semester, principal, lobbyist, item_id)` group equals `modeled_hours` exactly.

---

## Findings worth a project-lead read

### 1. LeMahieu's #8 ranking is a single-bill signal — SB 28 (electric transmission ROFR)

Bill-level inspection (full writeup: [`20260602_lemahieu_bill_inspection.md`](20260602_lemahieu_bill_inspection.md)) shows that LeMahieu's 1,081.2 hrs distribute across his 4 bills as:

| Bill | LeMahieu's role | Per-sponsor hrs | % of total |
|---|---|---:|---:|
| **SB 28** — incumbent transmission utility ROFR | sole primary (1 of 1) | **1,067.8** | **98.8%** |
| SB 258 — advanced practice registered nurses | 1 of 15 primary | 11.2 | 1.0% |
| SB 119 — Office of School Safety positions | 1 of 10 primary | 1.5 | 0.1% |
| SB 699 — alternative pupil transportation | 1 of 3 primary | 0.7 | 0.06% |

**The ranking is one bill, not four.** SB 28 is right-of-first-refusal legislation for incumbent electric transmission utilities — a high-profile state-by-state policy battle for the past ~5 years. LeMahieu introduced it alone (`num_sponsors_on_bill = 1`, so per-sponsor = full-bill effort). 29 distinct principals filed effort on it, heavily concentrated in the electric-utility industry:

| Top filer | Modeled hrs |
|---|---:|
| ATC Management Inc. (American Transmission Co — the incumbent monopoly the bill benefits) | 331.0 |
| WEC Energy Group | 134.4 |
| Wisconsin Industrial Energy Group | 124.3 |
| Americans For Prosperity | 86.6 |
| Dairyland Power Cooperative | 51.6 |
| Madison Gas & Electric Company | 51.1 |
| Northern States Power d/b/a Xcel Energy | 39.9 |
| Alliant Energy | 29.3 |
| Wisconsin Utilities Association | 28.7 |
| Municipal Electric Utilities of Wisconsin | 28.1 |

This is the chain's cleanest example of a single-bill industry-coalition signal — *and* the cleanest example of why position-direction matters. The WI lobbying data has no support/oppose field, so the chain says "AFP was active on SB 28" but cannot say which side. AFP has historically *opposed* ROFR legislation in other states on anti-competitive grounds. Any external presentation must explicitly disclose this — listing AFP next to ATC and the utilities reads as "industry coalition" by default, which may be the inverse of what's actually happening.

**Why LeMahieu specifically as sponsor?** The chain can't answer this. Plausible hypotheses — Senate Majority Leader role makes him strategically valuable for floor scheduling on a controversial industry bill, committee structure, personal policy interest — all require legislative-process knowledge the chain doesn't have.

**Suggested external phrasing** (also in the bill inspection writeup):

> The Phase 3.1 chain surfaces a sharp single-bill signal: 98.8% of Senate Majority Leader Devin LeMahieu's modeled-lobbying weight in 2025-2026 concentrates on **SB 28**, electric-transmission right-of-first-refusal legislation that he introduced as sole primary sponsor. 29 principals filed lobbying effort on the bill, heavily concentrated in the electric-utility industry — ATC Management (the incumbent transmission monopoly the bill benefits) at 331 hours, followed by WEC Energy, WI Industrial Energy Group, and the major investor-owned utilities. Americans For Prosperity also filed substantial effort (86 hours), but the WI lobbying data does not disclose position direction, so AFP's role on this bill (historically opposed to ROFR elsewhere on anti-competitive grounds) cannot be inferred from filings alone. The chain detects the *coalition's activity*; it does not adjudicate the *coalition's composition*.

**Method-level lesson worth carrying forward.** An earlier draft of this synthesis hypothesized a "leadership-vehicle pattern — Majority Leader's caucus-priority bills draw concentrated lobbying" before per-bill inspection. The data does not support that framing: 3 of LeMahieu's 4 bills are background-level noise, and the entire signal is one bill in one industry. **For any sponsor in the top-20 that gets external attention, the right next step is a per-bill breakdown before claiming a sponsor-level pattern.** Per-sponsor metrics can compress a single-bill signal into what looks like a broad agenda.

### 2. The "Assembly is more lobbied than Senate" finding was a metric artifact

Pre-Phase-3.1, the top 10 most-lobbied sponsors were **10 of 10 Assembly**. Lower:upper chamber hours were 3.44× imbalanced. With per-sponsor normalization (and using the ID-based chamber join — see numbers note below):

| Metric | OLD | NEW |
|---|---:|---:|
| Assembly total (modeled hrs) | 426,388 | 26,543 |
| Senate total (modeled hrs) | 123,790 | 21,657 |
| Lower:upper ratio | **3.44×** | **1.23×** |
| Top-10 sponsors that are Assembly | 10 | 2 |

> *Numbers note:* the Phase 3.1 writeup originally reported 25,892 / 21,610 / 1.20× by joining surname → roster `family_name`, which mis-bucketed three disambiguated-prefix legislators (B. Jacobson, L. Johnson, J. Jacobson — together 698 hrs) into an inflated "unknown" bucket. The ID-based join above is correct. See [`20260602_unknown_chamber_audit.md`](20260602_unknown_chamber_audit.md). Substantive finding is unchanged.

Lobbying effort is roughly balanced between the chambers. The original imbalance was the proportional-attribution artifact described in Stage 3 above (Assembly bills carry more co-authors → effort gets multiplied by more co-author count → Assembly sponsors look more lobbied).

**Two distinct profiles emerge after normalization:**

- **Concentrated Senate primaries** — moderate bill counts (65–123), high per-sponsor weight because Senate bills typically have few primary authors. Cabral-Guevara (108 bills, #1), James (104, #2), Tomczyk (118, #3), Nass (123, #4), Feyen (105, #5).
- **Broad Assembly co-authors** — huge bill counts (198–234), low per-sponsor weight because Assembly bills typically have many primary co-authors. Mursau (218, #10), O'Connor (234, #11), Dittrich (230, #14), Kreibich (230, #15).

This distribution-shape difference is a *structural fact about how the WI legislature processes bills*, not a metric artifact. Assembly bills picking up many primary co-authors is a procedural pattern in WI; the chain reflects it honestly under per-sponsor normalization.

### 3. The chain currently has a per-sponsor-honest grand total of 48,789 modeled hours

This is the total bill-allocated lobbyist effort across the 2025 biennium that the chain accounts for. The earlier figure of 561,625 hours was the pre-normalization inflated number — it's not wrong per se, but it's not what consumers usually want. **Quote 48,789 hr when summarizing "how much bill-targeted lobbying effort the WI 2025 chain accounts for."**

For scale: WI's reported total 2025 lobbying spend in `releases/wi/` is $47.5M across 944 principals. The 48,789 hr figure covers only the **legislative-bill** portion of effort — bill-effort rows tagged to specific bill IDs — and excludes other principal-filed effort categories (see "What's not in the chain" below).

### 4. WI bill-id collisions are real — `item_id` is the disambiguator

While verifying the conservation invariant on Phase 3.1, 3 of 10,290 `(semester, principal, lobbyist, bill_id)` groups failed because they contained multiple distinct `modeled_hours` values. Investigation showed:

```
principal 11473, 2025-H2:
  bill_id "AB 1":  item_id 24507 (voter ID)           AND  item_id 24521 (education assessment)
  bill_id "AB 6":  item_id 24534 (classroom 70%)      AND  item_id 24619 (nuclear energy)
  bill_id "AB 10": item_id 24554 (gun safe tax)       AND  item_id 24671 (worship gathering)
```

Multiple distinct bills (different `item_id`, different `item_description`, different `percent`) share the canonical `bill_id` on the WI portal. This is almost certainly biennium-internal renumbering (special-session bills or similar) that the portal's display strips. We added `item_id` to the chain TSV so consumers can disambiguate when it matters.

**This is also a finding for the `releases/wi/` documentation** — the canonical `bill_id` is not unique within a biennium, which is a portal-data-quality fact downstream users need to know. Worth a note in the next `releases/wi/README.md` revision. (All 3 cases in this snapshot are under principal 11473; the issue likely exists more broadly but doesn't surface unless a principal's bill roster happens to collide.)

---

## What this can and can't answer

### Can answer now

- **"How much lobbying effort was directed at bills primarily sponsored by lawmaker X in WI 2025?"** — sum `modeled_hours_per_sponsor` filtered to `sponsor_lawmaker_id = X`. Per the LeMahieu caveat, treat single-figure-bill-count results with care.
- **"Which principals lobbied bills primarily sponsored by lawmaker X?"** — group by `principal_id`.
- **"Which bills did principal P lobby on, and who sponsored them?"** — filter by `principal_id = P`, project bill and sponsor columns.
- **"For lobbyist L, what's the modeled mix of bills they worked on through their authorized principals?"** — filter by `lobbyist_id = L`, project bill, principal, and modeled hours.
- **"What's the chamber breakdown of lobbying effort?"** — group by `sponsor_lawmaker_name` joined to the chamber column in the Plural Policy legislator CSV.

### Can't answer yet (and why)

- **"Did principal P donate to lawmaker A?"** — needs CFIS leg (Phase 4 scoping).
- **"Did lobbyist L meet with lawmaker A?"** — structurally absent in WI; no contact-log disclosure mandate. CFIS provides a partial proxy via lobbyist personal donations.
- **"How much lobbying effort was directed at bills *cosponsored* (but not primarily sponsored) by lawmaker X?"** — primaries-only currently. The Plural Policy bulk dump does not contain cosponsors in any structured field; cosponsors live in `bill_actions.description` text and would require regex parsing. Refinement #2.
- **"How much effort did principals direct at issue areas without specific bill numbers?"** — currently skipped. WI principal filings have three additional effort buckets ("Topics Not Yet Assigned A Bill Or Rule Number" — 2,327 rows; "Budget Bill Subjects" — 856 rows; "Administrative Rulemaking Proceedings" — 127 rows) that the chain v1 does not include because they don't have a bill ID to join. Refinement #3.
- **"What's the chamber rollup *complete* (no unknown bucket)?"** — *resolved 2026-06-02.* The corrected (ID-based) unknown bucket is 590 hr (1.2% of 48,789), and it is entirely **Joint Legislative Council** (170 rows, 22 bills) — a collective entity for which no chamber assignment is meaningful by design. Coverage of the legislator roster is otherwise complete (zero individual-legislator IDs unresolved). Treat JLC as its own "collective entities" bucket if a fully-attributed chamber view is needed. Full audit: [`20260602_unknown_chamber_audit.md`](20260602_unknown_chamber_audit.md).

### What modeling assumptions consumers are trusting

Two assumptions are baked into `modeled_hours` and should be disclosed in any external presentation:

1. **Proportional attribution.** A lobbyist's hours are spread across their employer's bill mix in proportion to the employer's filed bill percentages. We have no per-lobbyist-per-bill ground truth in WI; this is the default, and the calibration is impossible against WI data alone (it might be possible against a state with contact-log disclosure as cross-validation; not in scope for this branch).
2. **Uniform-share sponsor attribution.** A bill's modeled lobbyist hours are split evenly across the bill's primary sponsors. This is the right neutral default, but it does assume that lead author and 9th co-author are equally lobbied — which is almost certainly false. A position-weighted scheme is on the refinement list and would be the upgrade if uniform-share turns out to be too crude.

---

## What's not in the chain

| Not in chain | Where it goes |
|---|---|
| Campaign-finance flows (principal → lawmaker $, lobbyist → lawmaker $) | Phase 4 CFIS — write-only scoping pending |
| Cosponsors (non-primary sponsors) | Phase 3+ refinement #2 — regex on `bill_actions.description` |
| Non-legislative-bill principal effort buckets (TNYB topics, budget, rulemaking) | Phase 3+ refinement #3 |
| 2026 semesters | Phase 2 allocation matrix covers 2025 only; 2026 chain emission needs a refit |
| 16 bills with zero structured sponsors (procedural / Joint Legislative Council vehicles) | Skipped — no rows emitted |
| Per-row residual exposure on `ipf_fit` cells | Phase 2+ refinement — currently the confidence label is categorical, not numeric |

---

## Open follow-ups and their dependency structure

We have three live options for next work, and they have non-trivial dependencies:

| Option | Cost | Depends on |
|---|---|---|
| **A.** Unknown-chamber audit | ~30 min diagnostic | nothing |
| **B.** Cosponsor parsing (refinement #2) | ~half day regex work | nothing |
| **C.** Phase 4 CFIS scoping (write-only) | hours of investigation + writeup | partially on **B**: the lawmaker join keys for CFIS depend on whether the chain includes cosponsors |

**A** is genuinely cheap and orthogonal — fold it into whatever else is happening, don't context-switch for it on its own.

**B → C** is the recommended ordering if there's no external timing pressure on CFIS. Cosponsor parsing materially changes the lawmaker side of the chain (Assembly bills typically have ~10 co-authors that aren't currently in the chain at all). Scoping CFIS join requirements before knowing whether cosponsors are in scope risks rework.

**C first** makes sense if there's a near-term Suhan-facing deliverable that needs the CFIS schema characterized, with the caveat "primaries-only is a known limitation of the chain it's joining against."

---

## Where the artifacts live

| Artifact | Path |
|---|---|
| Chain TSV (the deliverable) | `data/allocations/WI/WI_chain_2025.tsv` |
| Intermediate (lobbyist, principal) hours matrices | `data/allocations/WI/WI_lobbyist_principal_hours_h1_2025.tsv`, `..._h2_2025.tsv` |
| Source WI lobbying disclosures | `releases/wi/` (6 TSVs + README) |
| Code | `src/lobby_analysis/wi_allocation/` (loaders, graph, IPF, chain composer) |
| Per-phase technical writeups | `docs/active/wi-allocation-matrix/results/` |
| Per-session conversation summaries | `docs/active/wi-allocation-matrix/convos/` |
| Implementation plan | `docs/active/wi-allocation-matrix/plans/wi_allocation_matrix.md` |
| Branch trajectory and session index | `docs/active/wi-allocation-matrix/RESEARCH_LOG.md` |

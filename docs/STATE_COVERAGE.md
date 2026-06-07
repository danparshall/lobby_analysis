# State Coverage Matrix

For each priority state, this doc inventories what disclosure-data edges have been extracted into materialized artifacts, the data quality of each edge, and the source.

**Status:** Draft as of 2026-06-06. NY section is a skeleton; future NY-branch session will fill it in. CA/TX/CO/IL/WA/FL/NC are "Prong 1 statute SMR only" — no Prong 2 disclosure data extracted.

**See also:**
- `STATUS.md` — branch inventory + recent sessions
- `docs/RESEARCH_ARC.md` — three-prong arc + Prong 1 internals
- `releases/wi/chain/` — materialized WI chain TSV (only fully-shipped state artifact to date)

---

## Framework

The lobbying chain has **4 nodes** — principal, lobbyist, lawmaker, bill — connected by up to **6 edges**:

```
                lawmaker
               /        \
              /          \
        principal ──── lobbyist
              \          /
               \        /
                  bill
```

Each edge can carry up to **3 attributes**:
- **Money** — $ flowing along the edge (compensation, gifts, allocated spending)
- **Time** — hours or events allocated along the edge
- **Stance** — policy position on bills (support / oppose / monitor)

Per (edge, attribute), we mark **quality** and **source**.

**Quality conventions:**
- **✓ exact** — directly disclosed in source data, extracted to artifact
- **~ imputed** — derived via JOIN / IPF / allocation rule
- **✗ missing** — extractable in principle, not yet materialized
- **✗! structurally missing** — state doesn't collect / regime doesn't disclose
- **—** — not a meaningful (edge, attribute) combination
- **?** — needs validation

---

## WI — Wisconsin

**Status:** Mature. Full chain materialized at `releases/wi/chain/WI_chain_2025.tsv` (115,229 rows). Three archived branches: `wi-disclosure-explore`, `wi-allocation-matrix`, `wi-cfis-scoping`. Follow-up `wi-campaign-finance` queued pending FTM expanded access.

|                       | Money | Time | Stance |
|-----------------------|-------|------|--------|
| principal ↔ lobbyist  | ✗!¹   | ~²   | —      |
| principal ↔ lawmaker  | ✗³    | —    | —      |
| principal ↔ bill      | ~⁴    | ~²   | ✗!⁵    |
| lobbyist ↔ lawmaker   | ✗!⁶   | —    | —      |
| lobbyist ↔ bill       | ~⁴    | ~⁷   | ✗!⁵    |
| lawmaker ↔ bill       | —     | —    | ✓⁸     |

¹ WI §13.68(4) routes lobbyist compensation info to principal-side filings; not separately disclosed per (principal, lobbyist) pair (wi-tier1-direct-read finding)
² IPF over bipartite (principal, lobbyist) graph with semester marginals — `wi-allocation-matrix` Phase 2
³ Would come from WI Ethics Commission CFIS/Sunshine campaign-finance database — scoped on `wi-cfis-scoping`, materialization deferred to `wi-campaign-finance` (FTM expanded access pending Dan's 2026-06-03 email)
⁴ Proportionally allocated from per-principal total spending via chain composer — `wi-allocation-matrix` Phase 3
⁵ WI lobbying disclosure has no support/oppose field; chain detects activity, not composition (AFP-on-SB-28 finding documented in `docs/historical/wi-allocation-matrix/results/20260602_lemahieu_bill_inspection.md`)
⁶ WI principal-side filings don't itemize per-lawmaker gift recipients the way OH AERs do — the structurally-missing $-flow leg
⁷ Per-sponsor uniform-share normalization — chain TSV column `modeled_hours_per_sponsor`
⁸ Plural Policy WI bulk-CSV `bill_sponsorships.csv`, primary-only (cosponsors deferred; structurally absent from both JSON and CSV — only in `bill_actions.description` text)

---

## OH — Ohio

**Status:** Extraction pipeline validated at 300-filing slice. Discovery TSV (45,605 AERs for 2025-2026) materialized at $0. Full-corpus extraction (~$800 / ~24 hr via Batches API + caching) pending Batches integration. `releases/oh/` not yet materialized. Plural Policy OH bulk-CSV not yet downloaded.

|                       | Money | Time | Stance |
|-----------------------|-------|------|--------|
| principal ↔ lobbyist  | ✗!¹   | —    | —      |
| principal ↔ lawmaker  | ~²    | —    | —      |
| principal ↔ bill      | ~³    | —    | ✗!⁴    |
| lobbyist ↔ lawmaker   | ✓⁵    | ✓⁶   | —      |
| lobbyist ↔ bill       | ~³    | —    | ✗!⁴    |
| lawmaker ↔ bill       | —     | —    | ✗⁷     |

¹ OH AER form does NOT disclose compensation paid by employer to agent — verified 2026-06-06 against `src/lobby_analysis/oh_portal/extraction_brief.py` + raw HTML form 1472130. `LobbyingFiling.total_compensation` field exists on the schema (intended as PRI E1f_i/E2f_i federal concept) but is `null` on all OH extractions. Same structural shape as WI on this edge.
² Back-projectable through lobbyist (gift to lawmaker via principal's agent)
³ Itemized expenditures (Section II.A-D) allocate to lawmakers and aggregates; bill allocation would be by-period imputation
⁴ OH AER form does not collect stance per Section I (per `src/lobby_analysis/oh_portal/extraction_brief.py`)
⁵ AER Section II.A (Gifts) — `recipient_name` + `amount` per row
⁶ AER Section II.B (Itemized Meals & Beverages) treated as time-event proxy with $ amount; not literal hours
⁷ Plural Policy OH bulk-CSV not yet downloaded; `oh.csv` legislator roster pending. Same path as WI — `openstates.org/data/session-csv/` for the OH session bundle + `openstates.org/data/legislators-csv/` for `oh.csv`

---

## NY — New York

**Status:** `ny-disclosure-explore` branch active. **Chain shipped** (`releases/ny/chain/NY_chain_2025.tsv`, 83,786 rows, $153,064,191 conserved exactly; bill-match 99.9%; 213 distinct sponsors = full NY legislature). **`parties_lobbied` disclosed-lawmaker edge MVP shipped + nickname-matched** (`releases/ny/NY_filing_parties_lobbied.tsv`, 168,430 edges, **98.61%** of state-legislator-titled rows resolve to `ocd-person`, all 213 NY legislators covered). Chain integration of `parties_lobbied` deferred — per Phase-0 gating, the edge grain is a per-filing set, NOT a per-(lawmaker, bill) tuple. Plan sketch for chain completion lives on the `ny-disclosure-explore` branch at `docs/active/ny-disclosure-explore/plans/ny_chain_completion_sketch.md` (cross-branch link — will resolve on main once both branches merge).

|                       | Money | Time | Stance |
|-----------------------|-------|------|--------|
| principal ↔ lobbyist  | ✓¹    | ✗²   | —      |
| principal ↔ lawmaker  | ✗!³   | —    | —      |
| principal ↔ bill      | ~⁴    | ~⁵   | ✗!⁶    |
| lobbyist ↔ lawmaker   | ✓⁷ *(contact, not $)* | ~⁸ | ✗!⁶ |
| lobbyist ↔ bill       | ~⁴    | ~⁵   | ✗!⁶    |
| lawmaker ↔ bill       | —     | —    | ✓⁹     |

¹ Client semiannual `total_compensation` per (principal, lobbyist) filing — NY discloses money at the per-pair grain natively, so the chain composer uses no IPF (unlike WI). Conservation across the chain verified at $153,064,191 exactly.
² Time not a disclosed field on NY client semiannuals.
³ Out of lobbying-disclosure scope; would come from JCOPE / state campaign-finance — not in `ny-disclosure-explore` (same shape as WI's principal↔lawmaker).
⁴ Proportionally allocated from `total_compensation` via chain `comp_per_cell`; cell key includes `lobbyist_id`, replicated across sponsor rows — must not be summed naively (a smoke test caught −$68.6M phantom loss when the key omitted `lobbyist_id`).
⁵ Uniform per-sponsor share (`modeled_hours_per_sponsor`), same shape as WI.
⁶ NY structurally has no support/oppose/monitor field — neither on bills nor on lawmaker contact (same shape as WI/OH).
⁷ Disclosed via `parties_lobbied`. Today's nickname matcher (`io/ny/parties.py::NicknameIndex` + `nicknames` PyPI lib) closed resolution from 90.4% → 92.6% (accent-fold) → **98.61%** of state-legislator-titled rows (213/213 legislators = full Assembly + Senate). Of all `parties_lobbied` rows, ~42% are non-legislators (NYC municipal officials, executive offices, agencies, "entire-legislature" broadcasts), correctly `resolved=False`. **Grain caveat:** edge is per-filing set — recoverable as "lobbyist X contacted lawmaker Y in semester S," NOT "about bill Z" (cartesian, not a mapping per Phase-0 gating).
⁸ Treat `parties_lobbied` as a binary "contacted-in-semester" signal — ~ imputed time, not a frequency count.
⁹ Plural Policy NY bulk-CSV via OS; chain joins at 99.5% distinct / 99.8% link; 213 sponsors = full legislature. Primary-only — cosponsors deferred (same shape as WI).

**Remaining NY-side validation questions (for the next NY session, not blocking the leave-behind):**
- [ ] `lobbyist_bimonthly` filings — what additional edges/attributes do these carry? (fold-in pending)
- [ ] Multi-year backfill 2019→ — same schema, or year-to-year drift?
- [ ] `target_kind` taxonomy for the ~42% non-legislator `parties_lobbied` rows (post-MVP — currently all bucketed as `resolved=False`)
- [ ] `parties_lobbied` chain integration — see plan sketch above

---

## CA / TX (and CO, IL, WA, FL, NC) — Statute SMR only

**Status:** Prong 1 statute extraction completed at vintage 2015 via the cross-state CPI 2015 C11 validation round (`cross-state-cpi-2015-validation` branch). Typed-cell SMR populated for each (state, vintage). **No Prong 2 disclosure-data extraction has occurred** for any of these states.

Coverage matrix is uniformly empty:

|                       | Money | Time | Stance |
|-----------------------|-------|------|--------|
| (all edges)           | ✗     | ✗    | ✗      |

What we DO have for these states:
- Per-cell extraction of what the statute legally requires to be disclosed (181-row typed-cell SMR via the harness generalized cross-state in `cross-state-cpi-2015-validation`)
- Per-state CPI 2015 C11 projection accuracy: NY 4/6 · TX 4/6 · WI 3/6 · CA 3/6 · OH 1/6 indicators match published oracle (vintage 2015)
- σ_noise per state (Claude / GPT) at default-6-chunks dispatch shape: NY 90.5% / 88.1% · WI 84.5% / 88.1% · OH 92.9% / TBD · CA TBD · TX 73.8% / 60.7%
- CO, IL, WA, FL, NC deferred from the original 10-state plan; available for follow-up dispatch (~$15 to extend to N=10)

These states are **Prong 1 complete at vintage 2015**, not Prong 2 started. Each would need its own bespoke disclosure-data extraction pipeline (see Anna Karenina note below).

---

## Summary scorecard

| State | Discovery | Extraction | Chain composed | Released artifact | Tier |
|-------|-----------|------------|----------------|-------------------|------|
| WI    | ✓         | ✓          | ✓              | ✓ `releases/wi/chain/` | Mature |
| NY    | ✓         | partial    | ✗              | ✗                 | In progress |
| OH    | ✓ (45.6K) | ✓ (300/45.6K) | ✗           | ✗                 | In progress |
| CA, TX, CO, IL, WA, FL, NC | — | — | — | — | Prong 1 (statute) only |

---

## Anna Karenina note

Each state's disclosure pipeline is bespoke. The shared infrastructure (typed-cell schema, canonical `LobbyingFiling` model, projection functions, `releases/<state>/` format) lives **downstream** of extraction; the extraction work itself does not amortize across states.

WI required IPF + semester semantics because WI's lobbyist filings report aggregated effort across multiple (principal, lobbyist) edges with marginal constraints. OH's AER is per-(agent, employer, period) — chain composition reduces to JOINs, no matrix completion needed. NY's `parties_lobbied` is structurally richer than either: per-lobbyist disclosure of named lawmakers. Each state's idiosyncrasies live in per-state modules under `src/lobby_analysis/<state>/`; refactoring toward a state-agnostic chain composer is premature generalization and should be resisted.

Plan **~3 working days per state** at TDD discipline for chain composition (once the typed-cell schema is stable and the per-state discovery+extraction is shipped). There is no "do 50 states in 80 days" extrapolation from "3 states in 5 days."

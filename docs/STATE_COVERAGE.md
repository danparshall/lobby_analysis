# State Coverage Matrix

For each priority state, this doc inventories what disclosure-data edges have been extracted into materialized artifacts, the data quality of each edge, and the source.

**Status:** Updated 2026-06-09 (issue #48 corrections pass). WI mature (released on `main`). NY chain + `parties_lobbied` edges shipped on `ny-disclosure-explore` — merge to main gated on issue #37 (dollar double-count reconciliation) with TSV re-add per issue #46. OH extraction validated; chain not composed (#52). CA/TX are Prong 1 (vintage 2015) complete; CO/IL/WA/FL/NC Prong 1 dispatch is **pending** (#50, not completed). MI/NC carry disclosure-side recon findings (new section below).

**See also:**
- `STATUS.md` — branch inventory + recent sessions
- `docs/RESEARCH_ARC.md` — three-prong arc + Prong 1 internals
- `releases/wi/chain/` — materialized WI chain TSV (the only released artifact **on `main`** to date; the NY chain is shipped on `ny-disclosure-explore` with data TSVs deliberately untracked during dev — see NY section)

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

**Status:** `ny-disclosure-explore` branch active. **Chain shipped on branch** (`releases/ny/chain/NY_chain_2025.tsv`, 83,786 rows, $153,064,191 conserved exactly; bill-match 99.9%; 213 distinct sponsors = full NY legislature). **`parties_lobbied` disclosed-lawmaker edge MVP shipped + nickname-matched** (`releases/ny/NY_filing_parties_lobbied.tsv`, 168,430 edges, **98.61%** of state-legislator-titled rows resolve to `ocd-person`, all 213 NY legislators covered). **Tracking caveat:** both data TSVs are deliberately **untracked during dev** (`.gitignore` `releases/ny/**/*.tsv` — the 53MB chain TSV trips GitHub's >50MB warning and churns on regen); only the READMEs are in-tree. They are force-added at merge time per the checklist in issue **#46**. **Merge to main is gated on issue #37** (verify no dollar double-count across `client_semiannual` + `lobbyist_bimonthly`; document the reconciliation rule in `releases/ny/README.md`). Chain integration of `parties_lobbied` shipped 2026-06-08 as filing-grain metadata columns (`disclosed_lawmakers`, `sponsor_in_disclosed_set`, `disclosed_only_lawmaker_count`) — per Phase-0 gating, the edge grain is a per-filing set, NOT a per-(lawmaker, bill) tuple. Plan sketch for chain completion lives on the `ny-disclosure-explore` branch at `docs/active/ny-disclosure-explore/plans/ny_chain_completion_sketch.md` (cross-branch link — will resolve on main once both branches merge).

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

**Remaining NY-side validation questions:**
- [ ] **`lobbyist_bimonthly` dollar reconciliation — MERGE-BLOCKING, issue #37** (both datasets carry compensation for the retained-lobbyist universe at different grains; rule must be documented in `releases/ny/README.md` before merge). Broader bimonthly fold-in (itemized expenses as new edges) remains non-blocking follow-up.
- [ ] Multi-year backfill 2019→ — same schema, or year-to-year drift? (Hosting decision #47 gates this: backfilled TSVs will exceed GitHub's 100MB hard limit.)
- [ ] `target_kind` taxonomy for the ~42% non-legislator `parties_lobbied` rows (post-MVP — currently all bucketed as `resolved=False`)
- [x] `parties_lobbied` chain integration — shipped 2026-06-08 as filing-grain metadata columns (see status above)

---

## CA / TX (and CO, IL, WA, FL, NC) — Statute SMR only

**Status:** Prong 1 statute extraction at vintage 2015 is **complete for CA and TX** (dispatched alongside NY/WI/OH in Round 1 of the cross-state CPI 2015 C11 validation, `cross-state-cpi-2015-validation` branch). **CO/IL/WA/FL/NC have NOT been dispatched** — they were deferred from the original 10-state plan; Round 2 dispatch (~$15, requires Dan authorization) is issue **#50**. Typed-cell SMR is populated only for the five dispatched (state, vintage) pairs. **No Prong 2 disclosure-data extraction has occurred** for any of these states.

**Scope decision (2026-06-06):** this research line is **de jure only** — combined-axis rows are verboten. Reading statutes answers "what does the law say," not "what actually happens"; de facto is a separate research line. The 3 remaining combined-axis rows are queued for Pattern-C splits (issue #51).

Coverage matrix is uniformly empty:

|                       | Money | Time | Stance |
|-----------------------|-------|------|--------|
| (all edges)           | ✗     | ✗    | ✗      |

What we DO have for these states:
- Per-cell extraction of what the statute legally requires to be disclosed (181-row typed-cell SMR via the harness generalized cross-state in `cross-state-cpi-2015-validation`) — **dispatched five only** (NY/WI/OH/CA/TX)
- Per-state CPI 2015 C11 projection accuracy, **Round 1 pre-fix audit**: NY 4/6 · TX 4/6 · WI 3/6 · CA 3/6 · OH 1/6 indicators match published oracle (vintage 2015). **Post-Phase-1 helper-vocab fix (2026-06-06): aggregate 15/30 (50%) → 19/30 (63.3%)** — per-cell/per-state breakdown in `results/20260606_round_1_post_phase_1_audit.md` on `cross-state-cpi-2015-validation` (cross-branch link until merge).
- σ_noise per state (Claude / GPT) at default-6-chunks dispatch shape: NY 90.5% / 88.1% · WI 84.5% / 88.1% · OH 92.9% / TBD · CA TBD · TX 73.8% / 60.7%
- CO, IL, WA, FL, NC: nothing yet — available for Round 2 dispatch (~$15 to extend to N=10, issue #50)

CA/TX (with NY/WI/OH) are **Prong 1 complete at vintage 2015**, not Prong 2 started. CO/IL/WA/FL/NC are Prong 1 **pending**. Each would need its own bespoke disclosure-data extraction pipeline (see Anna Karenina note below).

---

## MI / NC — Disclosure-side recon only

Both states carry real **practical-availability findings** on stub branches (`mi-disclosure-explore`, `nc-disclosure-explore`); neither has extraction or chain work. Coverage matrices are uniformly ✗. These findings are exactly what the practical-availability axis of the N×50×2 matrix exists to capture — recorded here so they survive independent of branch fate. Both branches are stale vs main; rebase before resuming.

**NC** (characterization-only branch, per the 2026-05-24 gather-first pivot):
- **Registration graph already in hand as free bulk** — `NC_*.xlsx` files at `data/disclosures/NC/`. NC is *not* "impossible."
- **Activity/expenditure data is the blocked half**: offered only via JS-only per-record search (scripted search **prohibited by TOS**) or **paid** Data Subscription Services. The data is public by statute (Chapter 120C) — the paywall/TOS posture is itself the NC practical-availability datapoint.
- Open statute-honoring next move (not yet taken): public-records request to NC SoS for the bulk electronic activity file; record the subscription price/terms/refusal as the finding.
- Also in the Prong-1 Round-2 set (#50) — statute side not yet dispatched.

**MI** (recon, 2026-06-03; locked decisions: entity+expenditure MVP, no chain, 2025 vintage only):
- **No reliable public bulk download for 2025 MI lobby data.** Acquisition primitive = scrape/drive the **MiTN entellitrak** app (JS/AJAX, per-result export only; `robots.txt` 404; use ≥1.0s delay).
- Legacy NIC system holds 1982–2023 relationship bulk but the host is **decaying** (expired TLS, timeouts) and is the wrong vintage — historical cross-check only.
- Confirmed facets: **"Employed By"** (the WI authorization-graph analog) + **LR-4 itemized expenditure form** + semi-annual Financial Report Summary.
- Next: live-browser recon to capture the AJAX endpoint, then choose search-and-export vs WI-style enumerate-and-fetch.

---

## Summary scorecard

| State | Discovery | Extraction | Chain composed | Released artifact | Tier |
|-------|-----------|------------|----------------|-------------------|------|
| WI    | ✓         | ✓          | ✓              | ✓ `releases/wi/chain/` (on main) | Mature |
| NY    | ✓         | ✓          | ✓ (on branch)  | ✓ on `ny-disclosure-explore` — TSVs untracked-in-dev, re-add at merge (#46); merge gated on #37 | In progress |
| OH    | ✓ (45.6K) | ✓ (300/45.6K) | ✗ (#52)     | ✗                 | In progress |
| NC    | partial — registration graph in hand (free bulk); activity paywalled/TOS | ✗ | ✗ | ✗ | Recon (Prong 2) + Prong 1 pending (#50) |
| MI    | recon — MiTN scrape target identified | ✗ | ✗ | ✗ | Recon (Prong 2) only |
| CA, TX | —        | —          | —              | —                 | Prong 1 (statute, vintage 2015) complete |
| CO, IL, WA, FL | — | —         | —              | —                 | Prong 1 pending (#50) |

---

## Access-posture principle

Shared across state branches (originated 2026-06-03 during MI planning; parallel copies on `mi-` and `nc-disclosure-explore` — promoted here per #48 so it survives branch archival):

A website TOS is a contract of adhesion and **does not override a statutory public-records obligation**. An access barrier is a **practical-availability finding for the N×50×2 matrix, not a stop**. The statute-honoring lever is a **public-records request** that puts bulk provision back on the agency; a refusal or paywall on statutorily-public data is itself the finding. Distinction kept: the statute guarantees *access* (often per-record inspection / fee-based copies), not specifically *bulk machine-readable* provision — so request/demand is the instrument; scraping (legally defensible post-*hiQ*, but with practical + optics risk) stays in reserve.

---

## Anna Karenina note

Each state's disclosure pipeline is bespoke. The shared infrastructure (typed-cell schema, canonical `LobbyingFiling` model, projection functions, `releases/<state>/` format) lives **downstream** of extraction; the extraction work itself does not amortize across states.

WI required IPF + semester semantics because WI's lobbyist filings report aggregated effort across multiple (principal, lobbyist) edges with marginal constraints. OH's AER is per-(agent, employer, period) — chain composition reduces to JOINs, no matrix completion needed. NY's `parties_lobbied` is structurally richer than either: per-lobbyist disclosure of named lawmakers. Each state's idiosyncrasies live in per-state modules under `src/lobby_analysis/<state>/`; refactoring toward a state-agnostic chain composer is premature generalization and should be resisted.

Plan **~3 working days per state** at TDD discipline for chain composition (once the typed-cell schema is stable and the per-state discovery+extraction is shipped). There is no "do 50 states in 80 days" extrapolation from "3 states in 5 days."

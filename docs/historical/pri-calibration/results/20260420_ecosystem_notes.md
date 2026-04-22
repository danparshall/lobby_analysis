<!-- Generated during: convos/20260419_phase2b_phase3_scaffolding.md (continued 2026-04-20) -->

# Civic-tech ecosystem notes — OpenStates + Free Law Project

Captured 2026-04-20 while the Phase 3 baseline dispatch is queued up.
These are **observations, not decisions**. Neither organization is a drop-in
data source for state lobbying disclosure, but both maintain infrastructure
and/or datasets that are relevant to longer-horizon questions the project
will have to answer.

---

## OpenStates (openstates.org / Plural Policy)

Already covered in `docs/historical/research-prior-art/results/opencivicdata-analysis.md` — the original "depend, don't fork" decision stands. What's new (2026-04-20):

**Repos of note:**

- [`openstates/openstates-scrapers`](https://github.com/openstates/openstates-scrapers) — 50-state scrapers for bills/votes/legislators. Python, GPL-3.0, 896★, active (pushed 2 days ago). Layout: `scrapers/<state_abbr>/{bills,events,actions,…}.py`. **Does NOT cover lobbying disclosures.** This is the concrete "scraper-only fallback" material identified as a dependency-risk mitigation at project kickoff — if Plural's hosted API disappears, this is the self-hostable path.
- [`openstates/spatula`](https://github.com/openstates/spatula) — a standalone Python scraping framework (MIT-ish; confirm before adopting). Opinionated for government-data scraping. If we later want reproducible per-state lobbying scrapers (e.g., quarterly refresh, structured filings extraction), this is one candidate framework. Compatibility caveat: spatula is HTTP-first; state portals with JS/Cloudflare challenges (our experience with Justia + some state sites) may need Playwright integration, not clear whether spatula handles that natively.
- [`openstates/openstates-core`](https://github.com/openstates/openstates-core) — the Open Civic Data model + scraper backend. Defines schema for Person / Organization / Bill / Event. Relevant if we ever do entity-resolution to link lobbied principals to canonical Open States IDs.
- [`openstates/pyopenstates`](https://github.com/openstates/pyopenstates) — Python client for the Open States v3 API. What we'd import when we need bill-linkage in analytical code.

**Decision status:** no action. Noted for:
- Future "how do we scale lobbying-portal scraping from 5 calibration states to 50+" decision (Phase 5+).
- Future entity-resolution work (matching lobbying filings to canonical Open States bills/legislators).

## Free Law Project (free.law)

Surfaced 2026-04-20 via a screenshot of the free.law homepage. Nonprofit,
SF-based. **Their entire portfolio is judicial data** — courts, judges,
federal dockets, case opinions. They do **not** maintain any state
legislative or lobbying data.

**Active repos at `github.com/freelawproject` (53 non-archived, top by stars):**

| Repo | Stars | What it does |
|---|---|---|
| courtlistener | 897 | Federal + state court opinions, oral arguments, judge biographies, federal filings |
| x-ray | 797 | PDF bad-redaction detector |
| juriscraper | 564 | Scrapes American court websites for case metadata |
| eyecite | 224 | Legal-citation finder in text |
| reporters-db / courts-db | 125 / 102 | Court and court-reporter metadata |
| doctor | 103 | Microservice for PDF → text conversion at scale |
| recap-chrome | 75 | Browser extension that pushes purchased PACER docs into free archive |
| citation-regexes | 41 | Regexes for state/federal/international law citations |
| disclosure-extractor | 21 | Structured-data extraction from federal **judicial** financial disclosures |
| nomination-extractor | 9 | ML model for federal nomination disclosure forms |

**What this means for lobby_analysis:**

- **No direct data overlap.** They cover courts; we cover state legislative lobbying. Different vertical.
- **One genuinely interesting repo: `disclosure-extractor`.** It's scoped to federal judicial financial disclosures (wrong target), but the *problem shape* — parsing semi-structured government-disclosure PDF forms into queryable records — is exactly what we'd face if the project scales from "score the portal/statute" to "ingest individual lobbying filings." Worth skimming when we get to that layer.
- **`eyecite` might be useful** for detecting bill/statute references in lobbying filings (lobbyists cite bill numbers and statute sections in disclosure narratives). Low priority.
- **`juriscraper` is parallel to spatula** — same kind of scraping framework, but narrower (courts only). Not applicable to state lobbying portals.
- **`doctor`** (PDF → text microservice) is generic tooling we could depend on if lobbying-disclosure PDF volume grows large.

**Institutional signal, not infrastructure signal:** Free Law Project is the kind of well-funded civic-tech nonprofit that *might* host or mirror open lobbying-disclosure datasets in the future. Worth knowing they exist. Not a dependency or data source today.

**Decision status:** no action. Reconnaissance only.

---

## Reminder of our current stance

- **Statute text (2010 + 2026):** Justia. Stable URLs, historical coverage, audited.
- **Portal snapshots (2026):** LLM-subagent snapshotting (done, 50 states).
- **Per-state scrapers:** not built, not needed until we have a concrete reason (refresh cadence, structured filings extraction, scaling beyond 50 states).
- **Bill/legislator data:** depend on Open States API via `pyopenstates` when we need it. Scraper-only fallback via `openstates-scrapers` if their hosted API fails.
- **Judicial data:** not scoped into this project.

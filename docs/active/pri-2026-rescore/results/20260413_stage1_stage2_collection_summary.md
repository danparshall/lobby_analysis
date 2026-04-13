<!-- Generated during: convos/20260413_pri_phase4_data_collection_prep.md -->

# Stage 1 + Stage 2 Data Collection Summary — 2026-04-13

Portal URL discovery and raw portal snapshotting for all 50 US state lobbying disclosure systems, in support of the PRI 2026 accessibility re-score.

## Pipeline

Two subagent-driven stages:

1. **Stage 1 — URL discovery.** Per-state general-purpose subagent uses WebSearch + WebFetch to identify and verify the state's lobbying disclosure portal(s). Output: `data/portal_urls/<ABBR>.json` (one JSON per state with role-labeled URLs, HTTP verification, per-URL notes, observations).
2. **Stage 2 — Portal snapshotting.** Per-state subagent reads the Stage 1 JSON, fetches each URL with `curl` + realistic Chrome UA, saves raw bytes, computes sha256, then Sonnet-selects up to 15 additional linked pages (same seed hosts) for rubric coverage. Output: `data/portal_snapshots/<STATE>/2026-04-13/` with artifacts + `manifest.json`.

## Aggregate Totals

| Metric | Value |
|--------|-------|
| States with Stage 1 JSON | 50 / 50 |
| States with Stage 2 manifest | 50 / 50 |
| Total fetched artifacts | 981 |
| Total snapshot bytes | ~350 MB |
| Total honest skips (pre-flagged 403/DNS/auth) | 54 |
| Files flagged `suspicious_challenge_stub` | 17 |

## Per-State Collection

| State | Portal system | Seed URLs | Flagged seeds | Snapshots | Skipped | Stubs | MB |
|-------|---------------|----------:|--------------:|----------:|--------:|------:|---:|
| AK | APOC Online Reports + Insight (myAlaska) | 11 | 0 | 26 | 0 | 0 | 4.2 |
| AL | Alabama Ethics Commission / Alabama Interactive | 11 | 0 | 26 | 0 | 0 | 2.2 |
| AR | Arkansas Financial Disclosure Portal | 13 | 0 | 30 | 0 | 0 | 12.4 |
| AZ | Arizona SOS Lobbying Filing Portal | 12 | **12** | **0** | 12 | 0 | 0.0 |
| CA | CAL-ACCESS (CARS replacement in dev) | 10 | 3 | 24 | 1 | 0 | 1.4 |
| CO | Colorado SOS Online Lobbyist System | 10 | 0 | 25 | 0 | 0 | 3.7 |
| CT | OSE Lobbyist Filing System | 12 | 4 | 23 | 4 | 0 | 9.5 |
| DE | PIRS + LOBS | 12 | 3 | 24 | 3 | 1 | 3.9 |
| FL | Florida Lobbyist Registration / Compensation | 12 | 0 | 12 | 0 | 0 | 0.3 |
| GA | PeachFile (2026-present) / LERS (legacy) | 12 | 0 | 27 | 0 | 0 | 4.8 |
| HI | Hawaii Ethics Commission e-filing (Salesforce) | 10 | 2 | 25 | 0 | 0 | 1.9 |
| IA | Iowa Legislature Lobbyist System (Coolice) | 12 | 0 | 26 | 0 | 0 | 4.6 |
| ID | Sunshine (Angular SPA, Cloudflare) | 10 | 0 | 10 | 0 | 0 | 1.4 |
| IL | IL Lobbyist Registration & Expenditure Reporting | 13 | 7 | 13 | 0 | 0 | 1.5 |
| IN | Indiana Lobby Registration Commission E-File | 12 | 0 | 27 | 0 | 0 | 2.7 |
| KS | KS Lobbyist Center (SOS) + KPDC | 12 | 2 | 24 | 3 | 0 | 3.4 |
| KY | KLEC (legislative) + EBEC (executive) | 11 | 0 | 41 | 0 | 0 | 14.3 |
| LA | Louisiana Ethics Administration Program | 10 | 0 | 25 | 0 | 0 | 2.4 |
| MA | MA Lobbyist Registration & Reporting | 11 | 6 | 16 | 6 | 2 | 2.0 |
| MD | MSEC Lobbying Registrations | 9 | 0 | 15 | 0 | 0 | 2.7 |
| ME | Maine Lobbying Disclosure (SPA) | 13 | 0 | 19 | 0 | 0 | 8.6 |
| MI | Michigan Transparency Network (MiTN) | 10 | 8 | 23 | 2 | 0 | 9.0 |
| MN | MN Campaign Finance & Public Disclosure Board | 11 | 0 | 26 | 0 | 0 | 13.1 |
| MO | Missouri Ethics Commission LFS | 12 | 0 | 12 | 0 | 0 | 1.9 |
| MS | MSEL Lobbying Portal | 8 | 0 | 17 | 0 | 0 | 8.0 |
| MT | PLORS (Commissioner of Political Practices) | 9 | 0 | 23 | 0 | 0 | 5.6 |
| NC | NC SoS Lobbying Compliance / E-Filing | 12 | 1 | 19 | 1 | 0 | 5.3 |
| ND | FirstStop (SPA) | 12 | 0 | 12 | 0 | 7 | 0.6 |
| NE | Nebraska Legislature Lobbyist Reporting | 11 | 0 | 26 | 0 | 0 | 5.8 |
| NH | NH SOS Lobbyist Disclosure (paper-only, WAF) | 11 | 7 | 19 | 7 | 0 | 2.9 |
| NJ | ELEC Lobbying Disclosure | 12 | 0 | 27 | 0 | 0 | 2.4 |
| NM | CFIS (Campaign Finance Information System) | 13 | 0 | 13 | 0 | 0 | 7.3 |
| NV | Nevada Legislature Lobbyist Registration | 8 | 0 | 8 | 0 | 0 | 3.3 |
| NY | PSQ + Open NY Socrata + Lobbying App | 12 | 0 | 27 | 0 | 0 | 39.6 |
| OH | OLAC (Ohio Lobbying Activity Center) | 12 | 1 | 26 | 1 | 0 | 11.0 |
| OK | The Guardian (Civix) | 12 | 0 | 12 | 0 | 0 | 1.9 |
| OR | OGEC EFS + CMS | 12 | 0 | 27 | 0 | 0 | 2.0 |
| PA | PA Lobbying Services (DOS) | 12 | 0 | 26 | 1 | 0 | 63.6 |
| RI | RI Lobby Tracker | 9 | 0 | 9 | 0 | 0 | 2.3 |
| SC | SC Ethics Commission (ethicsfiling SPA + legacy) | 11 | 1 | 25 | 1 | 4 | 8.9 |
| SD | SOS Enterprise Lobbyist Services | 9 | 0 | 10 | 3 | 1 | 1.1 |
| TN | iLobby (Tennessee Ethics Commission) | 12 | 0 | 27 | 0 | 0 | 1.8 |
| TX | TEC Lobby Filing & Search System | 12 | 0 | 12 | 0 | 0 | 34.6 |
| UT | Utah Lobbyist Online Disclosure | 11 | 1 | 22* | 1 | 0 | 0.0* |
| VA | VA Ethics Council Lobbyist Registration | 11 | 0 | 15 | 0 | 1 | 12.1 |
| VT | Vermont Lobbying Information System | 9 | **8** | **1** | 8 | 0 | 0.1 |
| WA | Washington PDC (+ data.wa.gov Socrata) | 13 | 0 | 13 | 0 | 1 | 0.5 |
| WI | Eye on Lobbying | 11 | 0 | 26 | 0 | 0 | 7.9 |
| WV | WV Ethics Commission Lobbyist Portal | 12 | 0 | 27 | 0 | 0 | 1.6 |
| WY | Wyoming Lobbyist Center | 9 | 0 | 15 | 0 | 0 | 7.9 |

*UT uses a different manifest schema key than the other 49 states; 22 captures on disk, aggregator showed 0.

## Coverage Tiers

**Near-empty capture (needs playwright/manual):**
- **AZ** — 0/12 seeds fetched. Every azsos.gov/lobbying.az.gov URL WAF-403s under any UA. The only realistic path is a real browser or legal records request.
- **VT** — 1/9 seeds fetched. All *.vermont.gov is Incapsula-blocked; only the statutory text was recovered.

**Partial capture (WAF/SPA blocks a subset):**
- MA (6 skipped; Imperva serves 200-with-stub on HTML)
- NH (7 skipped; sos.nh.gov WAF)
- MI (2 skipped; 404s on stale URLs — not WAF)
- CT (4 skipped; oseapps.ct.gov ECONNRESETs)
- DE (3 skipped; egov.delaware.gov DNS fail)
- KS (3 skipped; SOS WAF bot filter)
- CA (1 skipped; auth wall + WAF)
- NC (1 skipped; SoS forbids scripted search)
- IL (5 curl HTTP/2 failures on ilsos.gov; 6 of 13 seeds salvaged)

**SPA-shell-only captures (curl got the bootstrap, not the data):**
- ID Sunshine (Angular)
- ND FirstStop (React; 7 stub flags)
- SC ethicsfiling (Angular; 4 stub flags)
- GA PeachFile (Angular)
- NM CFIS (post-2021 SPA)
- ME mainelobbying.com (JS SPA)
- MI MiTN entellitrak (JS-rendered)
- AR ethics-disclosures (SPA)
- IN ILRC public search (SPA)
- PA palobbyingservices (ASP.NET WebForms, `__doPostBack`-driven)

These will need a JS-capable fetcher (Playwright with stealth) to evaluate the actual filer UI for rubric scoring.

**Clean capture (rich static content + working bulk/PDF artifacts):**
- NY (39.6 MB — PSQ + Open NY Socrata ZIP + data dictionaries)
- TX (34.6 MB — TEC_LA_CSV.zip + PDF guide)
- PA (63.6 MB — annual report PDFs 2014-2024)
- MN, KY, VA, OH, AR, ME, SC (8-14 MB each)
- Most other states (1-8 MB clean HTML + PDFs)

## Key Findings (Provisional)

1. **WAF + no-API + no-bulk is a real pattern.** ~10 states combine bot protection with no programmatic data export and no bulk download. Their data is *technically* public but practically inaccessible at scale. The PRI 2026 rubric Q10/Q11/Q12 should score these configurations low — this is a rubric finding, not a pipeline defect.
2. **Zero fabricated URLs across 50 states.** Every subagent explicitly recorded WAF 403s, DNS failures, auth walls, and SPA shells rather than substituting unverified URLs. This provenance discipline held across 50 independent subagent invocations.
3. **Seed-file refinements surfaced during snapshotting** (for collaborator follow-up):
   - AL: `ethics-form.alabama.gov` hosts the real bulk-export endpoints (`WebDataLobbyistsPDF_2010.aspx`, `rptPrincipalsListing_Excel.aspx`) — add to AL.json.
   - HI: the two `hawaiiethics.my.site.com` URLs recorded as 403 via WebFetch actually return 200 SPA shells to curl+UA — update HI.json status.
   - MS: `www.sos.ms.gov` is Akamai-protected; the unprotected `lobbying.sos.ms.gov` equivalents should be added for every MS.json URL.
   - CA: `fppc.ca.gov` DNS-failed from the Stage 1 sandbox but the host is real — needs manual verification.
4. **Subagent tool-loading is probabilistic.** 2 of 50 Stage 1 dispatches (AK, AZ) initially reported no web tools under identical `subagent_type`. Retry with explicit "you have these tools" prompt succeeded in both cases. Factor in automatic retry for large batch dispatches.
5. **SPA coverage is the main structural gap.** Roughly 12 states' public search surfaces are JS-rendered and require a real browser. These are scoreable for many rubric items (statutes, FAQ, user guides, data dictionaries, bulk downloads) from the static captures we have; the portal-UX items will need Playwright supplementation.

## Next Steps

- Collaborator pass: manually verify WAF'd / DNS-failed / SPA-only URLs catalogued in `data/portal_urls/_flagged.md` and per-state manifest `skipped[]` entries. Update seed JSONs with corrected statuses.
- Playwright supplement for ~10 SPA + WAF'd states to capture actual portal UX for rubric-dependent items (AZ, VT, MA, NH, ID, ND, SC, GA, NM, ME).
- Phase 5: build Sonnet scoring function with the captured evidence, pilot on CA/CO/WY (same trio), iterate rubric if scoring disagreements surface.

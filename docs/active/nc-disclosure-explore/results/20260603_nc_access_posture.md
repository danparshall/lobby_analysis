# NC Access Posture — current best understanding + access-posture principle

**Date:** 2026-06-03
**Branch:** `nc-disclosure-explore`
**Context:** Written while planning the parallel Michigan pull (`mi-disclosure-explore`).
Dan asked to (a) reframe how we treat a scraping-prohibition TOS and (b) record our current
best understanding of NC access here. Consolidates the 2026-05-25 initial-look findings and
**re-verifies the load-bearing TOS claim against the live site (2026-06-03).**

## NC access posture (current best understanding)

NC lobbying disclosure is **public by statute** (NC General Statutes **Chapter 120C**; reports
are filed with the Secretary of State and are "open to public inspection"). But the *practical*
access surface is **tiered**, and only the registration side is freely scriptable:

| Data | Access tier | Scriptable? | Cost |
|---|---|---|---|
| **Registration graph** (lobbyist↔principal pairs, directories, liaison registries) | Free **bulk** Excel/text at `sosnc.gov/online_services/lobbying/download` | Yes (plain file download) | Free |
| **Activity / expenditure** (spend, compensation, bills lobbied, officials contacted, gifts, dates) | Free **per-record web search** (JS-only) **OR** paid bulk | **No** — scripted search prohibited (see TOS below) | Free per-record / **paid** for bulk |
| Aggregate | Annual "Lobbying Compliance Report" PDF (latest 2022–23) | n/a | Free |

**What we already have (free bulk registration side):** consolidated under
`data/disclosures/NC/` — `NC_2026.xlsx` (term export, 2,964 lobbyist↔principal pairs, Term=2025)
+ four directory files (`NC_directory_{lobbyists,principals,state_agency_liaisons,local_govt_liaisons}.xlsx`,
~6,366 rows combined, incl. emails + the covered-official/liaison side). See
[`20260525_nc_file_inventory.md`](20260525_nc_file_inventory.md).

**What's gated:** everything about lobbying *activity*. NC publishes **nothing** about
expenditure/compensation/bills/officials/gifts as free bulk data. That is the WI-style dataset
we cannot freely obtain for NC.

**The TOS (re-verified live 2026-06-03)** — NC SoS online-search policy:

> "The N.C. Secretary of State's online search tools are designed for interactive, real-time
> use by individuals and businesses. Automated or scripted searches may degrade system
> performance and are not permitted. For bulk access to public data, please use our Data
> Subscription Services."

So: scripted search of the activity data is explicitly prohibited, and bulk activity data is
pushed to a **paid** Data Subscription Service.

## Access-posture principle (TOS vs. statutory public-records obligation)

**This principle is shared across state branches; the parallel statement lives on
`mi-disclosure-explore` at `results/20260603_mi_portal_recon.md` → "Access posture & strategy."**

A state's online-search **Terms of Use is a click-through contract of adhesion and does not
override a statutory public-records obligation.** Where a disclosure statute requires records to
be public, the duty to make them *available* is on the state. For this project an access barrier
(scripted-search ban, JS-only per-record search, paywalled bulk) is **a practical-availability
finding to record on the N×50×2 matrix — not a stop.**

- **The lever that honors the statute is to put it back on the agency:** a public-records
  request (or direct ask) for the bulk electronic activity file in usable form. A refusal or a
  paywall on statutorily-public data is itself a documentable finding (and a strong one — it is
  exactly the legal-vs-practical gap the project exists to catalog).
- **Keep one distinction clean:** the statute typically guarantees *access* (often satisfiable
  by per-record inspection or fee-based copies), **not** specifically *bulk machine-readable
  provision*. NC's "open to public inspection" + "use Data Subscription Services for bulk" is an
  annoying-but-defensible reading of Chapter 120C. So the request/demand is the right
  instrument. Scraping publicly-accessible data is legally defensible post-*hiQ v. LinkedIn*
  (not a CFAA violation), and a **state actor's** TOS restricting access to its own
  statutorily-public records is on weak ground — but it carries practical risk (IP blocking
  regardless of legality) and an optics cost for a democracy-fellowship project. **Hold
  scraping in reserve; lead with the records request.**

## Implication for NC

NC is **not** "abandoned/impossible." Correct status: **registration graph obtained (free
bulk); activity data blocked on the free+scriptable tier and available only via paid
subscription or per-record manual search.** The open, statute-honoring move — not yet taken — is
a **public-records request to the NC SoS** for the bulk electronic activity/expenditure file
(citing Chapter 120C's public-inspection mandate), and to record the price/terms/refusal of the
Data Subscription Service as the NC practical-availability datapoint. That is "on them," and
their answer is the finding.

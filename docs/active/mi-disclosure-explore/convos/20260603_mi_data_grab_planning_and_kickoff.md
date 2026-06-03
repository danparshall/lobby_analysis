# MI data-grab — planning & branch kickoff

**Date:** 2026-06-03
**Branch:** `mi-disclosure-explore` (new, this session)
**Participants:** Dan, Claude
**Type:** Planning / reconnaissance (no code written)

## Goal of this session

Dan asked: "check the data we grabbed for WI … I'd like to do the same thing for MI.
Can you plan a large task to identify all the chunks that would basically get the same
data and statutes? … let's at least start an MI branch."

So: (1) reconstruct what the WI data-grab actually was, (2) recon Michigan's portal to
see whether the same approach ports, (3) produce a chunked acquisition plan, (4) start the
MI branch. Analysis is explicitly deferred ("we won't know how to do the analysis until we
have the data").

## What the WI data-grab actually was (reconstructed)

The published WI MVP (`releases/wi/`) is **six TSVs + a derived chain**, produced by a
two-tier scrape of `https://lobbying.wi.gov` (Wisconsin Ethics Commission), 2025-2026
session, snapshot 2026-05-25/26. Generating code lives at `src/lobby_analysis/io/wi/`.

- **Tier-1 (authorization graph):** discover all lobbyist IDs via an AJAX grid endpoint
  (`ShowLobbyistList?pageSize=1000`), fetch each lobbyist detail page, parse the
  "Principals Represented" back-links → lobbyist↔principal edges. Then a principal-side
  pass (IDs = directory `.xls` ∪ auth-graph) for validation/superset, unified with
  `discovered_via` provenance. Output: `WI_lobbyists.tsv` (773),
  `WI_principals.tsv` (944), `WI_lobbyist_principal_authorizations_unified.tsv` (2,254).
- **Tier-2 (detail):** re-parse the cached detail-page HTML for entity metadata,
  semester expenditure reports, quarterly activity reports, and — critically — the
  **"Percent Allocation of Lobbying Effort"** cross-tab that itemizes each principal's
  effort **by specific bill**. Output: `WI_principal_filings.tsv` (1,706),
  `WI_lobbyist_filings.tsv` (3,092), `WI_principal_bill_efforts.tsv` (7,345).
- **Statutes:** separate `statute-retrieval` harness pulled WI Chapter 13 §13.61–13.75
  (17 sections) from Justia into `data/statutes/wi/2025/` (manifest.json + section .txt,
  sha256 provenance). Also 2010 + 2015 vintages (9 sections each).
- **Derived chain (`releases/wi/chain/`):** principal → lobbyist → **bill** → sponsor,
  with per-lobbyist hours via IPF and per-sponsor normalization. 115,229 rows. **This is
  the "analysis" layer, and it is built entirely on `WI_principal_bill_efforts.tsv`.**

Architectural discipline carried over: full-HTML JSON checkpoints (never re-scrape;
parsers can change, snapshot is immutable), deterministic TSV sort, polite fetcher
(1.0 s delay), committed HTML fixtures for parser TDD.

## Michigan recon — the key finding (leads the session)

Michigan's portal is a **different system** and, more importantly, collects a
**different data model**. Two findings, one minor and one load-bearing:

1. **Portal mechanics differ but are tractable.** MI lobby disclosure now lives in
   **MiTN (Michigan Transparency Network)**, launched March 2024, running on the
   **entellitrak** COTS platform at `mi-boe.entellitrak.com/etk-mi-boe-prod/`
   (public lobby search: `page.request.do?page=page.miboeLobbyPublicSearch`). The legacy
   **E-Lobby** data was **migrated into MiTN**, so MiTN is a single source for current +
   historical. MiTN reportedly supports **per-filing export** ("a spreadsheet to export
   reported disclosures … a downloadable report of an entire filing"). There is also an
   older NIC/Tyler endpoint (`miboecfr.nicusa.com/cgi-bin/cfr/lobby_exp_anls.cgi`,
   "Itemized Lobby Expenditure Analysis") that may be a faster bulk source for historical
   itemized expenditures. Whether MiTN exposes a *bulk* (whole-dataset) export vs.
   per-filing-only export is the #1 recon question — it decides scrape vs. download.

2. **⚠️ The WI bill-effort / chain analysis has NO Michigan analog.** Michigan's Lobby
   Registration Act is **expenditure-centric, not bill-centric**. Lobbyists file a
   **semi-annual Financial Report Summary** (Jan 31 & Aug 31) reporting **total
   expenditures** plus **itemized** financial transactions / travel-lodging / food-
   beverage **benefitting public officials** over thresholds. They do **not** report
   which bills they lobbied on, nor positions, nor per-bill effort. WI's entire
   `bill_efforts → IPF → principal→lobbyist→bill→sponsor chain` was enabled by a
   **Wisconsin-specific** disclosure field. **That field does not exist in Michigan.**
   So "the same thing for MI" splits cleanly:
   - ✅ **Transferable:** the disclosure dataset — registrants (lobbyists/agents),
     the **"Employed By"** relationship graph (MI's structural analog of WI's
     authorization edges), and expenditure filings (summary + itemized-to-officials).
   - ❌ **Not transferable from disclosure data alone:** the bill-level allocation chain.
     Reproducing a WI-style chain for MI would require an *external* bill-position source,
     and even then MI filings give no lobbyist→bill linkage to anchor it.

This is a real finding, surfaced at full strength rather than softened: Michigan is one of
the weaker state lobby-disclosure regimes precisely on the dimension (subject/bill detail)
that made the WI chain possible. The MI MVP will be a strong **entity + expenditure**
dataset; it will not be a bill-attribution dataset.

## MI lobby data shape (from recon)

- **Filer roles:** Lobbyist and Lobbyist Agent; registrants can be individuals or orgs.
- **"Employed By" / employer graph:** added as a search facet — links agents to who
  employs them. This is the Tier-1 analog (who lobbies for whom).
- **Financial Report Summary:** semi-annual (Jan 31, Aug 31). Total expenditures.
- **Itemized Expenditure schedule:** single expenditures > $100 recorded separately
  (date, purpose, recipient name+address); categories = financial transactions w/
  officials, travel & lodging for officials, food & beverage for officials, over
  statutory thresholds (2026: $1,600 financial-transaction, $1,050 travel-lodging,
  $79/mo & $500 YTD food-beverage).
- **Search facets observed:** Lobbyist/Agent, Addresses, Filings, Expenditures,
  Expenditures Itemized, Fees, Notifications, Employees, Employed By.

## Decisions

- Branch: `mi-disclosure-explore` (parallel to archived `wi-disclosure-explore`).
  Worktree created at `.worktrees/mi-disclosure-explore`, `data/` symlinked.
- Scope of the plan: **data + statute acquisition only.** Analysis deferred per Dan.
- The plan explicitly carries the data-model caveat so the implementing agent does not
  try to build a bill-effort table or chain that the source data cannot support.

## Open questions for Dan / next session

1. **Bulk vs. per-filing export:** does MiTN expose a whole-dataset export, or only
   per-filing? (Gates the whole acquisition strategy — Phase 0 answers it.)
2. **Vintage depth:** how far back did E-Lobby → MiTN migration carry? WI did 2010/2015/2025
   statute vintages + a 2025 data snapshot; what vintages do we want for MI data?
3. **Is the entity+expenditure dataset valuable enough on its own** to be the MI MVP, given
   no chain is possible? (My read: yes — it's still a real LobbyView-for-MI contribution,
   and it's honest about the regime's limits. But Dan decides.)
4. Should we cross-check against The Accountability Project's MI lobbying dataset
   (publicaccountability.org, ~2023, stale) as a historical sanity check?

## Artifacts produced this session

- This convo.
- `docs/active/mi-disclosure-explore/RESEARCH_LOG.md`
- `docs/active/mi-disclosure-explore/plans/mi_data_acquisition.md` (chunked plan)

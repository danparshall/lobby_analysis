<!-- Generated during: convos/20260526_wi_principal_gap_investigation.md -->

# WI Principal-ID Gap Investigation — Results

**Date:** 2026-05-26
**Branch:** `wi-disclosure-explore`
**Originating handoff item:** "investigate the 40-principal gap between the auth graph (942) and the directory `.xls` (904)"
**Data inputs:**
- `~/data/lobby_analysis/disclosures/WI/WI_lobbyist_principal_authorizations.tsv` (2,251 rows, materialized by the prior session's scrape)
- `~/data/lobby_analysis/disclosures/WI/WI_directory_principals.xls` (printed 5/25/2026)
- `~/data/lobby_analysis/disclosures/WI/WI_directory_lobbyists.xls` (printed 5/25/2026)
- Live portal fetches from `https://lobbying.wi.gov/Who/PrincipalInformation/2025REG/Information/{id}` and `/Who/LobbyistInformation/2025REG/Information/{id}`, captured 2026-05-26
**Investigation artifacts (gitignored):** `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/` (40 principal HTMLs + 2 dir-only principal HTMLs + 1 lobbyist HTML + `gap_classification.csv`)

---

## TL;DR

The headline "40-principal gap" is **fully explained** and is not a scrape bug:

- **38 of 40 auth-only principals = ceased.** The directory `.xls` filters out principals with a `Cessation Date`. The auth graph correctly retains the historical authorizations they had before cessation. Behavior is expected and the graph is correct.
- **2 of 40 auth-only principals = privacy-redacted "low-spend pledge" entities** (IDs 11530, 13137). One explicitly carries the WI Ethics Commission footnote: *"This organization is one of fewer than 10 organizations registered with the Wisconsin Ethics Commission that is exempt from semi-annual reporting of its lobbying hours and expenditures. Instead of the semi-annual report the organization has submitted a written pledge not to spend more than $500 per year on lobbying."* Their principal-info detail fields (name, business interest, CEO, contact) are suppressed on the public portal, but their authorization graph is fully present. They are excluded from the directory `.xls`.

But the investigation surfaced **a separate, more important structural finding** while reconciling the 2 dir-only principals (i.e., principals in the directory `.xls` with 0 rows in our auth scrape):

- **The LobbyistList grid AJAX endpoint is not exhaustive.** At least one currently-active, currently-authorized, licensed Wisconsin lobbyist (Michael Schlaak, ID 12694) is silently omitted from both (a) the `POST /Who/Lobbyists/2025REG/ShowLobbyistList?pageSize=1000` discovery response (774 IDs) and (b) the published `WI_directory_lobbyists.xls` (776 rows). His detail page at `/Who/LobbyistInformation/2025REG/Information/12694` resolves cleanly (HTTP 200, real content), licensed 1/28/2025, authorized for WCTA (principal 12997) since 1/8/2026.
- **Implication:** our lobbyist-side discovery layer has a real, unbounded blind spot. We cannot determine the omission rate from this side. The only way to enumerate the set of "Schlaak-like" lobbyists is a principal-side scrape that discovers lobbyists via the back-link from principal pages — i.e., option (4) from the originating handoff. This investigation **directly motivates option (4)** as a completeness sweep, not just a redundant cross-check.

---

## Method

1. Reconcile the headline gap arithmetic by computing set differences both ways (auth-only and dir-only).
2. For each principal in `auth − dir`, fetch `/Who/PrincipalInformation/2025REG/Information/{id}`, classify by cessation status and page structure.
3. For each principal in `dir − auth`, fetch the same page, identify which lobbyist(s) they link to, and cross-check each linked lobbyist against our 774-ID discovery set, our 745-ID scrape result, and the 776-row lobbyist directory `.xls`.
4. Where a lobbyist appears on a principal page but not in our scrape, fetch the lobbyist's own detail page directly to determine whether it resolves and what its license/authorization dates are.

Polite-fetch convention from the prior session preserved: 1.0 s delay between calls, descriptive UA `lobby_analysis-research (contact: parshall.dan@gmail.com)`.

---

## Gap reconstruction

| Set | Count |
|---|---|
| Auth graph distinct principal IDs | **942** |
| Directory `.xls` distinct principal IDs | **904** |
| In auth, NOT in directory (the headline "40") | **40** |
| In directory, NOT in auth | **2** |
| Intersection | **902** |

`40 − 2 = 38 = 942 − 904` ✓. The naïve headline gap of 38 is the *net*; the actual reality is the asymmetric pair (40 auth-only, 2 dir-only).

---

## The 40 auth-only principals

All 40 fetched cleanly (HTTP 200, no soft-404, no hard error). Classification by cessation:

| Sub-class | Count | Examples |
|---|---|---|
| Ceased (filtered from directory `.xls`) | **38** | 10949 Apex Clean Energy (ceased 1/22/2025), 10973 Secure Elections Project (9/8/2025), 11017 Indivior Inc (9/4/2025), 11227 Heritage Action for America (1/27/2026), 11335 The College Entrance Examination Board (1/29/2026), 11494 DISH Network LLC (1/30/2026), 12832 Human Rights Campaign (2/10/2026), 13167 The Home Depot (2/5/2026) |
| Privacy-redacted "low-spend pledge" | **2** | 11530, 13137 (page title is generic "Lobbying in Wisconsin"; principal name and detail fields suppressed; Authorized Lobbyists section IS populated with real names + dates; 13137 has the explicit ≤$500/year exemption footnote) |

Full table: `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/gap_classification.csv`.

Cessation dates span 1/22/2025 → 4/30/2026, fairly evenly distributed across 15 months. The directory `.xls` filter is "exclude where `Cessation Date IS NOT NULL`", not "exclude where ceased before some recent date" — both old and recent cessations are filtered.

The 2 privacy-redacted cases show that the WI portal data model has a third class beyond "active" and "ceased": **active-but-suppressed**, used for the small set of pledge-exempt organizations. Their data is published structurally (authorizations visible, lobbyists named) but their principal-info fields are zeroed out for privacy. Our scrape captures their authorizations correctly because the auth graph lives in the lobbyist-side detail pages, where these principals are referenced normally.

---

## The 2 dir-only principals — surfacing the structural finding

These are principals listed in `WI_directory_principals.xls` with 0 rows in `WI_lobbyist_principal_authorizations.tsv`:

### 12900 — Voces de la Frontera Action, Inc.

- Principal page: HTTP 200, real content, no cessation date.
- Lists 1 authorized lobbyist: **Neumann-Ortiz, Christine (lobbyist ID 12717)**.
- Lobbyist 12717 status in our scrape: **in the 774-ID discovery grid**, but the fetch returned `status_code: 404` with `html: None`. This is the same soft-404 case the prior session captured and added the body-marker check for; the checkpoint sits at `~/data/lobby_analysis/disclosures/WI/_authorization_scrape_checkpoints/12717.json` with html=None.
- Cross-check: Neumann-Ortiz IS in `WI_directory_lobbyists.xls` (licensed 1/31/2025, organization `Voces de la Frontera Action, Inc.`, no surrendered date).
- **Diagnosis:** principal exists, lobbyist exists in both rosters, but the lobbyist's detail page can't be reached. Downstream effect: 0 authorizations captured, principal appears orphaned in our graph. This is a known failure mode (the soft-404 the prior session already addressed); the principal's apparent orphaning is the visible consequence.

### 12997 — WCTA (Wisconsin County Treasurers Association)

- Principal page: HTTP 200, real content, no cessation date.
- Lists 1 authorized lobbyist: **Schlaak, Michael (lobbyist ID 12694)**.
- Lobbyist 12694 status in our scrape: **NOT in the 774-ID discovery grid**. Checkpoint missing entirely.
- Cross-check: Schlaak's lobbyist detail page at `/Who/LobbyistInformation/2025REG/Information/12694` **resolves cleanly** (HTTP 200, 25 551 bytes, no soft-404 marker, title "Michael Schlaak - Lobbying in Wisconsin", license issued 1/28/2025, self-employed lobbyist, 1 principal = WCTA, authorized 1/8/2026).
- Cross-check against directory `.xls`: **Schlaak is NOT in `WI_directory_lobbyists.xls` either** (grep on "Schlaak" returns 0 matches across all 776 rows).
- **Diagnosis:** a real, currently-active, currently-authorized, licensed Wisconsin lobbyist is silently omitted from BOTH published roster sources, yet is fully visible by direct URL and reachable via the back-link from his principal's page.

---

## Why the Schlaak finding matters

- The prior session's discovery layer was built on the premise that `POST /Who/Lobbyists/2025REG/ShowLobbyistList?pageSize=1000` enumerates all lobbyists for the session. This investigation shows the premise is wrong: at least one real lobbyist with a real authorization is silently omitted.
- The directory `.xls` is similarly incomplete. We can't use one to backstop the other; both miss Schlaak.
- We have no way to bound the omission rate from this side. There may be 1 Schlaak-class lobbyist; there may be dozens. Their existence is invisible until you reach them from a principal page.
- The principal-side scrape (handoff option 4) is the only way to enumerate the omitted set: discover lobbyists via `<a href="/Who/LobbyistInformation/...">` back-links from all principal pages, then take the union of {grid-discovered, principal-discovered} as the actual lobbyist population.
- The completeness consequence is bigger than the cross-validation framing in the prior session's "Next Steps." It's not "cheap insurance" — it's how we discover the part of the auth graph that's currently invisible.

---

## What the directory `.xls` does and doesn't expose

The `WI_directory_principals.xls` directory is empirically equivalent to `principals WHERE cessation_date IS NULL AND NOT is_low_spend_pledge_exempt`. The directory's 904 rows are a curated subset of the underlying portal database, not a faithful publication of the registered-principal universe. The auth-graph view derived from lobbyist detail pages is broader and arguably more useful for influence-tracing.

The `WI_directory_lobbyists.xls` directory is similarly curated, but on a different axis we haven't yet characterized: it omits Schlaak even though Schlaak satisfies the obvious "licensed and not surrendered" filter (license issued 1/28/2025, surrendered date blank on his detail page, principal authorization current).

A principal-side scrape would let us derive empirical filter behaviors for both directory files by computing the set differences:
- `principals_directory − principals_active_per_portal` → reveals what the directory filter excludes
- `lobbyists_directory − lobbyists_referenced_from_principals` → same, on the lobbyist side

---

## Numerical pinpoints (for future reference)

- Gap: 942 − 904 = 38, decomposed as 40 auth-only − 2 dir-only.
- Of 40 auth-only: 38 cleanly ceased, 2 low-spend privacy-redacted. 0 soft-404 on principal-page side, 0 HTTP errors.
- Of 2 dir-only: 1 case downstream of an already-documented lobbyist soft-404 (Voces ← lob 12717), 1 case from a lobbyist absent from both rosters (WCTA ← lob 12694).
- Schlaak's dates: license issued 1/28/2025; authorized for WCTA 1/8/2026; directory printed 5/25/2026; our scrape ran 5/26/2026. He was in the system 16 months before our scrape, ruling out a registration race condition.
- Lobbyist directory `.xls` has 776 rows; grid AJAX returned 774; intersection cannot be computed by ID (the `.xls` has no `Lobbyist ID` column).

---

## Open questions

1. **Bound the omission rate.** How many lobbyists like Schlaak exist? Answerable only via a principal-side scrape (handoff option 4). Until done, our auth graph's "denominator" is unknown.
2. **Characterize the directory `.xls` filter on the lobbyist side.** What rule excludes Schlaak but not Neumann-Ortiz (both self-affiliated with their principals; both licensed in early 2025; both currently authorized)? Hypotheses: license-type (`Single` vs other; need to inspect Schlaak's License Type which isn't visible from the rendered text), special handling for self-employed lobbyists representing exactly one principal, or an opaque administrative state. Cannot resolve without more samples.
3. **Soft-404 prevalence.** The prior session captured 1 soft-404 (lob 12717). Are there others that the soft-404 detection (added test-first during the prior session) silently caught? The fetcher logs would tell us; not investigated this session.
4. **Cross-session stability.** Does Schlaak's omission persist on the next scrape? Worth re-checking before the principal-side scrape to verify it's not a one-day glitch.

---

## Files produced

- This document.
- New test fixtures (3 principal HTMLs, useful for future principal-page parser tests):
  - `tests/fixtures/wi/principal_10949.html` — Apex Clean Energy, ceased principal (canonical example)
  - `tests/fixtures/wi/principal_10973.html` — Secure Elections Project, ceased principal
  - `tests/fixtures/wi/principal_11017.html` — Indivior Inc, ceased principal
- Investigation HTMLs + classification CSV (gitignored, durable under `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/`).
- No source-code changes.

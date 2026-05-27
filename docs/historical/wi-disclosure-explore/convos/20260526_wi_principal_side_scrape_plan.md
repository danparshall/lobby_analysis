# wi_principal_side_scrape_plan

**Date:** 2026-05-26
**Branch:** `wi-disclosure-explore`

## Summary

Follow-up to this morning's gap investigation. Two short tasks: (1) re-fetch
lobbyist 12694 (Schlaak) to verify the bilateral omission (page resolves
cleanly + grid AJAX omits him) is persistent rather than a transient cache /
materialization glitch; (2) write the implementation plan for handoff option
(4), the principal-side completeness scrape — which the prior session
upgraded from "cheap insurance / cross-validation" to "the only mechanism to
bound lobbyist-side completeness."

The re-fetch confirmed both sides are byte-identical (sha256 match) to the
captures from ~5 hours earlier. That's good news for the structural-omission
hypothesis — Schlaak is still missing from the grid, his page still
resolves — but it's also weaker evidence than originally thought: byte-
identity at the 5-hour mark suggests edge-cached or daily-snapshot-served
content rather than a live database query, so we may be hitting the same
materialized snapshot both times. The dominant evidence for "structural, not
transient" remains the 16-month tenure pinpoint from the prior session
(license issued 2025-01-28, captured 2026-05-26).

Plan written for the principal-side scrape, sized against empirically-
captured principal page bytes (mean 47 KB across 42 gap-investigation
captures, not the original convo's ~560 KB spot-check estimate) and the
1.0 s polite-delay floor (~17 min wall for 944 pages, not 5 hr).

## Topics Explored

- Single-call re-fetch of `/Who/LobbyistInformation/2025REG/Information/12694` (Schlaak's lobbyist detail page) to verify omission persistence; comparison against the gap-investigation capture at `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/lobbyist_12694.html`.
- Bilateral re-check: also re-POSTed the grid AJAX (`/Who/Lobbyists/2025REG/ShowLobbyistList?pageSize=1000`) to confirm Schlaak is still absent from THAT side, not just present on his own detail page.
- Reconnaissance pass over the 42 captured principal HTMLs to characterize page-size distribution and lobbyist-back-link structure (the load-bearing parse target for the new plan).
- Reuse analysis on the existing scrape modules in `src/lobby_analysis/io/wi/` — fetcher is URL-specific to the lobbyist endpoint, so the plan needs to either refactor it generic or duplicate it for principals.
- Composition of the principal universe to scrape: union of `WI_directory_principals.xls` IDs (904) and the existing auth graph's principal IDs (942) = 944 distinct, with 902 in both.

## Provisional Findings

- **Re-fetch confirms bilateral omission is persistent.** Schlaak's detail page (HTTP 200, 25,551 bytes) is byte-identical (sha256 `bf616576fb1b2632`) to the prior capture; grid AJAX response (HTTP 200, 353,140 bytes) is byte-identical (sha256 `68b792835c41547f`) to the prior fixture; same 774 lobbyist IDs, Schlaak (12694) still absent, sanity checks (11042 present, 12717 present) pass. The structural-omission hypothesis holds.
- **Byte-identity at 5-hour separation is itself informative.** It suggests the portal is serving edge-cached or daily-snapshot content rather than live database query results. Implication: a "few hours later" re-check is weaker evidence of structural-vs-transient than I expected up front, because we may be hitting the same materialized snapshot. The 16-month tenure pinpoint from the prior session (license 1/28/2025, scrape 5/26/2026) remains the dominant evidence.
- **Principal page sizes are much smaller than originally estimated.** The kickoff convo's "~560 KB × 905 ≈ 500 MB" figure was a single bad spot-check. Real distribution from the 42 gap-investigation captures: 26 KB min, 40 KB median, 47 KB mean, 157 KB max. Caveat: the sample is biased toward ceased + low-volume principals; large active principals (WI Hospital Association, WI Auto Dealers each have 15 lobbyists per the prior session) may be 2-3× larger. Even tripled: 944 × 150 KB ≈ 140 MB. The "~500 MB" original framing was loose.
- **Wall time is bounded by politeness, not transfer.** At delay=1.0 s, 944 principal pages → ~17 min wall (parallel to the lobbyist scrape's 851 sec / ~14 min for 774 pages). The "~5 hr" framing carried in from RESEARCH_LOG was wrong — likely conflating a hypothetical conservative delay with the actual 1.0 s convention. The cost stays in the same envelope as the existing lobbyist scrape.
- **WCTA back-link parsing is confirmed.** Sanity-checked the `principal_12997.html` capture: a simple regex over `/Who/LobbyistInformation/2025REG/Information/(\d+)` href matches yields `[12694]` (Schlaak). The parse target is well-defined; the BeautifulSoup pass should be straightforward.
- **Existing fetcher is lobbyist-URL-specific** (`LOBBYIST_PAGE_URL_TEMPLATE` constant, `lobbyist_id` parameter naming). Three reuse options: refactor to a generic `fetch_entity_page` core with thin wrappers (DRY but touches tested code); duplicate as `principal_fetcher.py` (safer for the lobbyist code path, violates DRY); thin-wrap via `functools.partial` (compromise). Plan recommends option 1 with the alternatives documented.

## Decisions Made

- Decision: proceed to write the plan for handoff option (4) even though the re-fetch evidence is weaker than originally framed — the 16-month-tenure argument is strong enough on its own to motivate the spend.
- Decision: principal universe = union of directory `.xls` IDs (904) ∪ existing auth-graph principal IDs (942) = 944 distinct. This is the empirically-defensible coverage; enumerating principal IDs blindly (10000+ range) would be 10× the work to surface very few additional IDs.
- Decision: plan recommends refactoring `authorization_fetcher.py` to a generic `entity_fetcher` core (option 1) but flags option 2 (duplicate) as a valid alternative if Dan wants to keep the lobbyist code path frozen.
- Held over from prior session (unchanged): (1) `lobbying@wi.gov` reply, (3) State Agency Liaisons table pull. (4) — the principal-side scrape — now has a written plan.

## Results

- Re-fetch sha256 + content-sniff output captured in this convo's "Provisional Findings" (no separate results file — this is verification, not analysis).
- Plan written: [`../plans/wi_principal_side_scrape.md`](../plans/wi_principal_side_scrape.md).
- Reconnaissance script: `/tmp/principal_page_recon.py` (one-shot; not committed; numerical output captured in this convo's Findings).

## Open Questions

- **Are active principals with many lobbyists much larger than the sampled distribution?** The 42 captures sampled were biased toward ceased + low-volume; the largest was 157 KB. Could a 15-lobbyist active principal page reach 300-500 KB? Resolvable by sampling 2-3 known-active high-volume principal pages before kicking off the full scrape. Doesn't change the architectural plan.
- **What's the right unification rule for the output table?** The plan proposes three files: `WI_lobbyist_principal_authorizations_principal_side.tsv` (new), the existing `WI_lobbyist_principal_authorizations.tsv` (lobbyist-side, 2,251 rows), and a unified table tagging each row with `discovered_via ∈ {lobbyist, principal, both}`. Suhan / Dan may want a different consumer-facing shape — e.g., one table only with provenance columns, or a separate "Schlaak-class additions" diff file. Resolvable at plan-execution time.
- **Should `lobbying@wi.gov`'s reply (if it comes) take precedence?** A direct CSV from the Ethics Commission would supersede both scrapes. Plan currently says "if Dan has emailed and is waiting, give it a week before scraping." Dan to decide.
- **Are there principal-page soft-404s analogous to the lobbyist-side ones?** The gap-investigation pass got 42/42 clean fetches, but that's a small sample. The fetcher's soft-404 detection from the lobbyist side should port over to the principal-side parser; the plan calls for porting the body-marker check.

## Process notes

- The opening "re-fetch to confirm not a one-day glitch" framing in the user's prompt didn't quite match reality — the gap-investigation captures were ~5 hours old, not 1 day, when this session started. The re-fetch's "few hours later" check is structurally weaker than a "day later" check would have been. Flagged to the user up front before proceeding.
- The claude-exit verification ceremony passed cleanly at session start (sacrificial PID 31527 spawned alive, killed dead; target parent PID 31169 confirmed as `claude`). Nothing about it stood out; ceremony was uneventful.

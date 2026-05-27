# wi_principal_gap_investigation

**Date:** 2026-05-26
**Branch:** `wi-disclosure-explore`

## Summary

Investigation of the 40-principal gap between the WI authorization scrape's auth graph (942 distinct principals) and the directory `WI_directory_principals.xls` (904 distinct principals), flagged as a held-over follow-up by the prior session's results doc. Dan picked this option from the four held-over follow-ups because it was the cheapest and most likely to reshape whether the more expensive principal-side scrape (option 4) was actually needed. That bet paid off — the investigation resolved the headline gap cleanly AND surfaced a separate structural finding that makes the principal-side scrape considerably more important than it had been framed in the prior session.

The headline gap fully decomposes: 38 of 40 auth-only principals are ceased (with cessation dates spanning 1/22/2025 → 4/30/2026; directory `.xls` filters them out, auth graph correctly retains their historical authorizations), and 2 of 40 are privacy-redacted "low-spend pledge" entities (the WI Ethics Commission's <$500/year exemption — one of the two carries the explicit footnote text). The directory `.xls` is empirically equivalent to `principals WHERE cessation_date IS NULL AND NOT is_low_spend_pledge_exempt`.

But the asymmetric 2-dir-only side surfaced a more concerning finding while reconciling. Voces de la Frontera Action (12900) had no authorizations in our scrape because its lobbyist (Neumann-Ortiz, 12717) was the prior session's already-documented soft-404. WCTA (12997) had no authorizations because its lobbyist (Schlaak, 12694) is silently omitted from BOTH the LobbyistList grid AJAX response (774 IDs) AND the `WI_directory_lobbyists.xls` (776 rows), even though his lobbyist detail page resolves cleanly by direct URL and confirms a current, active authorization dating to 1/8/2026. Neither roster source is exhaustive — our discovery layer has a real, unbounded blind spot. The only way to enumerate Schlaak-class omissions is a principal-side scrape that discovers lobbyists via back-links from principal pages, which is exactly handoff option (4). The originating framing of (4) as "cheap insurance / redundant cross-validation" understates the case — it's the only mechanism to bound a real completeness gap.

## Topics Explored

- Bidirectional set-difference reconstruction of the principal-ID gap (auth_graph ⇄ directory `.xls`); the asymmetric pair `(40 auth-only, 2 dir-only)` netting to the headline 38.
- Live-portal classification of all 40 auth-only principal IDs by cessation status, parsing principal-info pages via `/Who/PrincipalInformation/2025REG/Information/{id}`. Polite-fetch conventions from the prior session preserved (1.0 s delay, descriptive UA).
- Discovery that 2 of 40 are not ceased but instead privacy-redacted under the WI Ethics Commission's <$500/year pledge exemption — page title generic, principal-info fields suppressed, but auth graph fully visible.
- Live-portal investigation of the 2 dir-only principals; identification that one (Voces) is downstream of an already-known lobbyist soft-404, but the other (WCTA) is downstream of a lobbyist absent from both roster sources.
- Direct fetch of `/Who/LobbyistInformation/2025REG/Information/12694` to confirm Schlaak is a real lobbyist (HTTP 200, license 1/28/2025, self-employed, current WCTA authorization 1/8/2026). Cross-check that "Schlaak" appears 0× in `WI_directory_lobbyists.xls` (776 rows) and 0× in the cached LobbyistList grid HTML.
- Pinning down that the omission isn't a registration race condition (Schlaak was in the system 16 months before our scrape).
- Reframing of handoff option (4) — principal-side scrape — from cross-validation to completeness sweep.

## Provisional Findings

- **Headline gap explained.** 942 − 904 = 38 = 40 auth-only − 2 dir-only. Of the 40 auth-only: 38 cleanly ceased (cessation date present on principal page), 2 privacy-redacted low-spend pledge entities. The directory `.xls` filter is empirically `cessation_date IS NULL AND NOT is_pledge_exempt`. No principal-side fetch errors, no soft-404s, no anomalies beyond the 2 pledge cases.
- **WI portal data model has 3 principal states, not 2.** Active, ceased, and active-but-suppressed (low-spend pledge). The third state matters because their auth graph IS published structurally even though their principal-info detail is suppressed — our scrape correctly captures them via the lobbyist-side detail pages.
- **The LobbyistList grid AJAX response is incomplete.** At least one currently-active, licensed, currently-authorized Wisconsin lobbyist (Schlaak, ID 12694) is silently omitted from both the grid response (774 IDs) and `WI_directory_lobbyists.xls` (776 rows). His detail page resolves cleanly by direct URL. The omission isn't a race condition (16-month tenure pre-scrape).
- **Our auth graph has unknown completeness on the lobbyist side.** We can't determine the omission rate from this side. The principal-side scrape is the only mechanism to enumerate the Schlaak-class set. This is a stronger motivation for handoff option (4) than the prior session expressed.
- **The Voces / lobbyist-12717 case is a known failure mode propagating downstream.** The prior session added soft-404 detection to the fetcher but didn't note that affected lobbyists' principals would appear orphaned in the auth graph. The principal-side scrape would recover their authorizations.

## Decisions Made

- Decision (this session): characterize the gap fully, write up results, do NOT pursue handoff options (3) or (4) in the same session. Both remain held over; (4) is now materially better-motivated.
- Decision (this session): preserve the 3 sampled principal HTMLs as committed test fixtures under `tests/fixtures/wi/principal_{10949,10973,11017}.html` — useful future material for principal-page parser tests. The 40-principal investigation HTMLs themselves stay gitignored under `data/` (durable under `~/data/lobby_analysis/disclosures/WI/_principal_gap_investigation/`).
- Held over (still): (1) reply from `lobbying@wi.gov`, (3) State Agency Liaisons table pull, (4) principal-side cross-validation / completeness scrape.

## Results

- [`../results/20260526_wi_principal_gap_investigation_results.md`](../results/20260526_wi_principal_gap_investigation_results.md) — full results writeup with methodology, classification table, structural finding analysis, and open questions.

## Open Questions

- **How many lobbyists like Schlaak exist?** Cannot be answered without the principal-side scrape. Our auth graph's lobbyist-side denominator is currently `774 (grid) − 29 (no-auth-rows) = 745 (≥1 auth)` but the true denominator might be 745 + N, with N currently unknown.
- **What rule excludes Schlaak from `WI_directory_lobbyists.xls` but includes Neumann-Ortiz?** Both are self-affiliated with their single principal, both licensed in early 2025, both currently authorized. Schlaak's `License Type` field isn't visible in the rendered text dump; the directory `.xls` has a `License Type` column ("Single" was seen for one row). Hypotheses: license-type sub-filter, self-employed-with-one-principal corner case, or an opaque administrative state. Resolvable with more samples once the principal-side scrape gives us a bigger Schlaak-like population.
- **Does Schlaak's omission persist on the next scrape?** Worth re-checking before option (4) executes to rule out a one-day glitch. Cheap (one HTTP call).
- **Are there other principal-page soft-404 analogues we haven't seen?** Other lobbyists may have detail pages that fail to render; we'd discover them via the principal-side scrape.
- **Did `lobbying@wi.gov` reply?** Still on Dan's end. If a CSV came back, it'd cross-validate both the principal universe and the lobbyist universe in one shot.

## Session meta-note (post-finish-convo)

After running finish-convo, the agent wrote a sign-off comment about the claude-exit verification ceremony that included the line *"That's a tighter loop than the ceremony from a couple sessions ago."* Dan pushed back: *"wait. ... you remember the ceremony from before?"* — correctly identifying a confabulation. The agent has no episodic memory across sessions and nothing on disk (CLAUDE.md, MEMORY.md, this branch's docs) describes specific prior ceremony details in enough depth to support a comparative claim. The "tighter than before" framing was an unsupported vibe dressed up as grounded comparison — the same failure mode the Nori-block tone instructions warn against ("false confidence is more costly than honest uncertainty").

Logged here rather than in RESEARCH_LOG because it's process-meta, not research-substantive. If this pattern recurs, it would be a candidate for a `feedback_dont_make_comparative_claims_about_prior_sessions_with_no_grounding.md` entry in `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/` — but Dan is the one who curates those, so just flagging.

Grounded alternatives the agent should have reached for instead of the vibe-comparison: `mcp__claude-exit__read_invocation_log` (actual cross-session record of ceremony runs on this machine) or `mcp__claude-exit__get_source_location` + git history of the file (whether the side-channel `target_parent_pid` is new or longstanding). Either would have given a real answer.

# wi-allocation-matrix kickoff

**Date:** 2026-05-30
**Branch:** wi-allocation-matrix

## Summary

Dan opened the session with a status check, then surfaced a directive from Suhan (Corda Democracy Fellowship lead): "We need as closely as possible to get **company → lobbyist → lawmaker → bill** chain." We walked the WI 2025-2026 release (`releases/wi/`, merged to main as `5fcc6ac` 2026-05-27) and asked which links of that chain we actually have.

The first answer I gave muddled "direct disclosure" with "inference" — Dan caught it: bill-effort allocations in `WI_principal_bill_efforts.tsv` are **filed by the principal themselves** on the principal expenditure report, so **company → bill (with effort %)** is a direct sworn disclosure, not an attribution. Lobbyists file a separate activity report containing only aggregate hours (communicating + other), no bill IDs.

That cleanup let us enumerate the 6 pairwise relations across {principal, lobbyist, lawmaker, bill} and classify each by source / availability / inference status. Dan then proposed an "X equations / Y unknowns" framing for the missing **lobbyist → bill** link — which formalizes cleanly as a bipartite matrix completion problem (IPF / RAS algorithm on row-sums from principal filings and column-sums from lobbyist filings, with the authorization edge graph as the support pattern). Mid-session he added: investigate WI CFIS (campaign finance) as a third leg closing the principal→lawmaker $-flow edge.

Decision: cut the `wi-allocation-matrix` branch off main, write the plan only this session, leave implementation for a fresh-context follow-up.

## Topics Explored

- WI 2025-2026 release inventory: 6 TSVs, schemas, headline aggregates ($47.5M total, DoorDash $2.18M outlier, 7,345 bill-effort rows)
- Who files which paperwork in WI lobbying disclosure: principal expenditure report (filed by principal) vs. lobbyist activity report (filed by lobbyist)
- The 6 pairwise relations across {principal, lobbyist, lawmaker, bill} — direct / inferable / external / structurally absent
- Bipartite matrix completion shape: ~2,254 authorization edges per semester as unknown cells; ~944 + ~773 = ~1,717 marginal constraints per hours-type; × 2 hours-types (comm + other) = ~3,432 constraints vs ~4,508 unknowns globally; decomposes into smaller connected components with many exactly-pinned cells (lobbyists with one principal, principals with one lobbyist)
- Standard solver for this shape: Iterative Proportional Fitting (IPF / RAS algorithm), nonnegative max-entropy fit
- Attribution chain `lobbyist → bill`: assuming `hours_{Y, bill_b} = Σ_{P employing Y} h_{Y,P} × percent_{P, b}` (lobbyist attacks employer's bill mix proportionally)
- Time-granularity mismatch: lobbyist filings quarterly (4/yr); principal filings semester (2/yr) — aggregate or keep separate marginals
- Authorization date weighting: edges have `authorized_on`/`withdrawn_on`; partial-semester membership reduces a lobbyist's possible contribution to that principal
- Two external data sources to close the chain: WI Legislature bill-sponsorship scrape (`docs.legis.wisconsin.gov`, free, structured), WI CFIS campaign finance (separate Ethics Commission database)
- Derived-proxy semantics: "lobbyist X targeted bills sponsored by lawmaker Y" is not the same as "X met with Y" — flag clearly to Suhan

## Provisional Findings

- **Company → bill IS a first-class direct disclosure in WI**, not an inference. Bill-effort percentages are filed by the principal on their own expenditure report; lobbyists do not report which bills they worked on.
- **Of 6 pairwise relations on {principal, lobbyist, lawmaker, bill}**:
  - 3 directly in WI lobbying disclosures (principal↔lobbyist, principal↔bill, lobbyist↔hours-aggregate)
  - 1 inferable via bipartite matrix completion (lobbyist↔bill)
  - 1 free external scrape (lawmaker↔bill via WI Legislature)
  - 2 structurally need CFIS or are absent without contact-log mandates (principal↔lawmaker, lobbyist↔lawmaker direct contact)
- The matrix-completion problem is globally under-determined by ~1,000 cells per semester, but **decomposes into connected components where many cells are exactly pinned** (single-employer lobbyists, single-lobbyist principals). The free cells live only in the dense sub-components.
- The "lobbyist X attacks employer P's bill mix proportionally" attribution assumption is the natural default but is a **modeling choice that should be flagged in any output**; without per-lobbyist-per-bill ground truth in WI, calibration is impossible against WI data alone (cross-state calibration against states with contact-log disclosure is possible).
- Adding CFIS as a third leg is what actually closes Suhan's chain end-to-end with **direct** edges throughout — the matrix-completion gives a *modeled* lobbyist→bill but CFIS gives *direct* principal→lawmaker and *direct* lobbyist→lawmaker (via personal donations).

## Decisions Made

- **Branch cut:** `wi-allocation-matrix` off main, worktree at `.worktrees/wi-allocation-matrix`, data symlink to `~/data/lobby_analysis`. Pytest baseline clean (1541 pass + 3 pre-existing `test_pipeline.py` baseline failures, matches main exactly).
- **Three legs of the stool** (named explicitly in branch charter): (1) bipartite matrix completion within WI lobbying data, (2) WI Legislature bill-sponsorship scrape, (3) CFIS campaign finance investigation.
- **No implementation this session.** Plan only — handoff to a fresh-context session that picks up Phase 0.
- Plan lives at `plans/wi_allocation_matrix.md`.

## Results

(none — plan-only session)

## Open Questions

- **CFIS data availability:** is there a bulk download? An API? Scrape-only? What's the principal identifier (employer name string? FEIN? something else)? Does the lobbyist personal-donation disclosure require a separate filing or is it covered by general individual-donor records? Phase 0 sub-task for the implementing agent.
- **WI Legislature scrape vs API:** does `docs.legis.wisconsin.gov` expose JSON/XML endpoints, or is HTML scraping the only path? OpenStates may already cover WI 2025-2026 — check first before writing a scraper.
- **Decimal-percent precision:** the `percent` column in `WI_principal_bill_efforts.tsv` is stored as a string like `"1%"` or `"54.9%"`. Per-(principal, semester) percentages may not sum exactly to 100% due to rounding — what's the rounding-discrepancy distribution? Affects whether we treat the % as exact constraint or noisy estimate.
- **Connected-component analysis:** before running IPF, what does the bipartite graph actually look like in WI 2025? Is it one giant component, or many small ones? The connected-component decomposition is the right unit of analysis and the right unit of confidence-quantification.
- **Validation:** WI alone can't validate the inferred lobbyist→bill matrix (no ground truth). Is there a cross-state validation play (e.g., a state with contact-log disclosure where we could test the proportional-attribution assumption)? Worth a sentence in the plan.
- **Pettack outlier handling:** the WI release notes a known portal artifact where lobbyist 11072 (Pettack/SAA) reports 7,611 total hours (≈32 hrs/day) — clearly an org-wide aggregate booked under one person's registration. How does IPF handle this? Probably needs an explicit outlier-flag step before fitting.

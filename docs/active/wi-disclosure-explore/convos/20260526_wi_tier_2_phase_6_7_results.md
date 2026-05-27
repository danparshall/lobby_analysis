# wi_tier_2_phase_6_7_results

**Date:** 2026-05-26
**Branch:** `wi-disclosure-explore`
**Plan:** [`plans/wi_tier_2_parser.md`](../plans/wi_tier_2_parser.md) (Phases 6 + 7)
**Prior session:** [`convos/20260526_wi_tier_2_phase_4_materialize.md`](20260526_wi_tier_2_phase_4_materialize.md) (Phases 4 + 5 shipped; this session picks up at Phase 6)
**Follow-up session:** [`convos/20260527_wi_parser_address_fix_and_pr.md`](20260527_wi_parser_address_fix_and_pr.md) — pre-merge code review surfaced an address-parser BLOCKER misdiagnosed in this session's results doc §8; fixed before PR.

## Summary

Pick-up session after the materializer + CLI shipped clean (Phases 0-5). Ran the Tier-2 materializer against the full 944 principal + 776 lobbyist checkpoint corpus to its proper output dir (`~/data/lobby_analysis/disclosures/WI/`), spot-checked the canonical principals against plan expectations, computed top-10 / bucket-distribution / lobbyist-hours-distribution aggregates, and wrote up findings as `results/20260526_wi_tier_2_parser_results.md`. Phase 7 doc-drift fix landed inline (WCTA 12997 = Wisconsin County Treasurers, not Cable Telecommunications) with a process note on verifying entity names from page body. The held-over `contact_details_json` address-quality eyeball from Phase 3 was folded into the results doc as §8 with concrete examples and a follow-up proposal.

End-to-end idempotency holds at the real-corpus level: 19.3 s wall vs the smoke run's 19.2 s, identical row counts (944 / 773 / 1706 / 3092 / 7345 / 0). Spot-checks against plan anchors passed cleanly: Lexia 11348 emits $65,225.58 YTD exactly as the plan expected. The two findings from the prior session (0 parse failures via the null-html branch, not ParseError path; WCTA 12997 emits 1 filing not 2) reproduced exactly and are documented in the results doc as Findings §1 and §2.

The analysis surfaced one **new** data-quality observation worth flagging for cross-state work: lobbyist 11072 (Deanna Pettack, School Administrators Alliance) reports 4,007 hrs H1 + 3,604 hrs H2 — ≈32 working hours per day across a 125-working-day semester, which is not physically possible for one individual. Likely interpretation: the SAA aggregates organization-wide lobbying-adjacent staff hours under their single registered lobbyist. Worth re-checking once a second state's Tier-2 lands.

## Topics Explored

- Running `tier_2_materialize_cli` with defaults against the on-disk corpus (945 principal + 773 lobbyist non-null checkpoints)
- Spot-checking three plan-anchor principals: Lexia 11348 ($65,225.58 YTD expected), Dairy 11590 (canonical fully-populated fixture), WCTA 12997 (low-spend-exempt)
- Computing top-10 principals by YTD spend across `WI_principal_filings.tsv`
- Computing bucket distribution across the 7,345 `WI_principal_bill_efforts.tsv` rows + distinct-principals-per-bucket
- Computing lobbyist-hours distribution across the 3,092 `WI_lobbyist_filings.tsv` rows (non-null vs > 0; communicating vs other; binned by hours-per-filing)
- Top-10 lobbyists by total hours (sum of communicating + other across all 4 periods)
- Verifying Neumann-Ortiz 12717 (lobbyist-side soft-404) is silently absent from both the lobbyists + lobbyist-filings TSVs and from the parse-failures TSV (null-html branch confirmed)
- Inspecting the 56 zero-filing principals (2 redacted + a long tail of new-registrants / empty-expenditure-section principals)
- Address-quality eyeball on `WI_lobbyists.tsv.contact_details_json` (held over from Phase 3)
- Checking the parser's declared `_BUCKET_HEADERS` constant vs which buckets actually appear in real data (6 declared, 4 used — Minor Efforts + Other Matters have 0 rows in 2025-2026)

## Provisional Findings

- **0 parse failures via null-html branch, not ParseError path.** Plan step 36 expected 1 row in `_tier_2_parse_failures.tsv` (the Neumann-Ortiz soft-404). The actual count is 0 — the fetcher's body-marker soft-404 detection stored that checkpoint as `html=null` during the prior auth-scrape session, and the materializer's null-html branch silently skips those checkpoints. **The handling is correct**, only the observation channel differs. Worth folding into the materializer as synthetic ParseFailure rows for downstream visibility.
- **WCTA 12997 emits 1 filing (H2 at $0/0/0), not 2.** Low-spend-exempt principals don't necessarily emit zero-row filings for every period; they file in whichever periods the portal records something for. 2025-H1 column is empty on the WCTA page, not populated-with-zero.
- **Lexia 11348: $65,225.58 YTD verified ($32,537.58 H1 + $32,688.00 H2)** — matches plan's exact expected value.
- **Dairy 11590: $88,568.50 YTD, 72 bill-effort rows** across 4 buckets (44 LBR + 15 Topics-Not-Yet + 9 Budget Bill + 4 Admin Rule).
- **Total principal-side spend across 944 principals: $47,458,304.69.** DoorDash leads at $2.18M (more than 2× #2).
- **Top-10 by spend:** DoorDash, WIIN, WMC, WHA, Wisconsin REALTORS, Farm Bureau, Americans For Prosperity, Wisconsin Property Taxpayers, Wisconsin Insurance Alliance, Wisconsin Counties Association.
- **888 of 944 principals have ≥ 1 filing** (94.1%); **812 have > $0 spend in any filing**.
- **Bucket distribution:** Legislative Bills 54.9% / Topics-Not-Yet 31.7% / Budget Bill 11.7% / Admin Rule 1.7%. The 2 declared buckets `Minor Efforts` + `Other Matters` have **0 rows** in 2025-2026. Worth re-checking next session.
- **Topics-Not-Yet has the most distinct principals (652)** but second-most rows — suggests it's a common low-volume bucket. Legislative Bills has 526 principals but 4,035 rows — long-tail of bill-by-bill itemization.
- **Lobbyist-filing hours: median 15 hrs communicating per non-zero filing, max 651; median 34.5 hrs other, max 3,356.5.** Only 1,128 / 3,092 (36.5%) of lobbyist-filing rows have any reported `hours_communicating` > 0. (The always-4-filings-per-page contract emits zero-rows for periods not reported.)
- **Pettack outlier (lobbyist 11072, SAA): 7,611 hrs total** across H1 + H2 — physically impossible for one individual. Probable interpretation: organization-wide hours aggregated under a single registered lobbyist. Portal data-entry pattern, not parser bug; cross-state validation pending.
- **`contact_details_json` address blob is structurally messy at source:** the `address` typed entry contains the full 4-line address block (firm name + street + city-state-zip + phone duplicated from the dedicated `phone` field); some rows have email mashed in instead of street. The parser preserves what the portal serves correctly; downstream geocoding/joins will want a `_parse_address_blob` helper that splits + tags lines. **Refactor warranted, but scope creep for this session.**

## Decisions Made

- **Phase 6 results doc shipped** at [`results/20260526_wi_tier_2_parser_results.md`](../results/20260526_wi_tier_2_parser_results.md). Covers all required deliverables: 0-parse-failures-via-null-html-branch finding, WCTA-12997-1-filing finding, spot-check verification (Lexia + Dairy + WCTA), top-10 by spend, bucket distribution, lobbyist-hours distribution, contact_details_json eyeball, and a process note on entity-name verification.
- **Phase 7 doc-drift fix landed inline** in [`results/20260526_wi_principal_side_scrape_results.md`](../results/20260526_wi_principal_side_scrape_results.md) line 65: "Wisconsin Cable Telecommunications Association" → "Wisconsin County Treasurers Association" + a 2026-05-26 correction-note block explaining the acronym ambiguity and the verify-from-page-body principle.
- **`contact_details_json` refactor deferred** to a follow-up: known limitation, not blocking, would require parser change + re-materialize + test/fixture updates. Documented as Finding §8 + Open Item.
- **Synthetic ParseFailure rows for null-html-skipped checkpoints deferred** to a follow-up: small materializer change to make soft-404 cases observable in the warnings TSV. Documented as Finding §1 + Open Item.
- **All Phase 0-7 work for `wi_tier_2_parser.md` is now complete.** The branch has shipped: Phase 0 fixtures, Phase 1 v1.2 schema bump, Phases 2-3 parsers, Phase 4 materializer, Phase 5 CLI, Phase 6 run + writeup, Phase 7 doc-drift fix. PR + merge of `wi-disclosure-explore` is a natural milestone — Dan's call.

## Results

- **Run output (gitignored):** 5 TSVs + `_tier_2_parse_failures.tsv` at `~/data/lobby_analysis/disclosures/WI/`. 944 / 773 / 1706 / 3092 / 7345 / 0 rows; 19.3 s wall. Idempotent against the smoke-run output (identical row counts).
- **Results doc:** [`results/20260526_wi_tier_2_parser_results.md`](../results/20260526_wi_tier_2_parser_results.md) — 8 findings, 5 open items.
- **Doc-drift fix:** in-place edit to [`results/20260526_wi_principal_side_scrape_results.md`](../results/20260526_wi_principal_side_scrape_results.md) (line 65 + correction-note block).
- **Analysis scripts (ephemeral):** `/tmp/wi_tier_2_analysis.py` + `/tmp/wi_missing_filings.py` — used for the aggregates + 56-principal investigation. Not checked in (one-off analysis; the results doc captures the numerical outputs).

## Open Questions / Follow-ups (carried to RESEARCH_LOG Next Steps)

- **Synthetic ParseFailure rows** for null-html-skipped checkpoints — make soft-404 cases observable in `_tier_2_parse_failures.tsv`.
- **`_parse_address_blob` helper** — split the 4-line address blob into typed sub-fields (firm | street | city-state-zip); preserve current single-blob behavior as fallback for unparseable cases.
- **Low-spend-exempt flag on `Organization`** — v1.3 candidate alongside the planned `LobbyingEffortAllocation` lift.
- **Cross-state validation** of the "organization-aggregates-hours-under-one-lobbyist" pattern (Pettack outlier). Open until a second state's Tier-2 lands.
- **Classify the 56 zero-filing principals** — distinguish new-registrant vs empty-expenditure-section vs other shapes.
- **6 vs 4 bucket count:** parser declares 6 (`Minor Efforts` + `Other Matters` included); only 4 appear in real 2025-2026 data. Re-check next session to confirm they're allowed in the WI portal schema but unused this session, or are dead code in the parser constant.
- **PR + merge of `wi-disclosure-explore`** — natural milestone. Dan's call. The branch has shipped:
  - Tier-1 auth-edge scrape (774 lobbyists / 944 principals / 2,251 authorization edges)
  - Principal-side scrape (944 principals fetched cleanly)
  - Auth-edge unification with `discovered_via` + `lobbyist_in_grid` provenance
  - Tier-2 parser (principal + lobbyist) with v1.2 schema bump
  - Tier-2 materializer + CLI
  - Run + spot-check + results writeup
  - All doc-drift fixes
- **Held over from prior sessions (orthogonal):** `lobbying@wi.gov` reply (Dan handling), SAL parser/ingest, cross-session principal_id stability.

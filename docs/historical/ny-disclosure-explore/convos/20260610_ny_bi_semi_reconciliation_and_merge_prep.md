# NY bi vs semi compensation reconciliation + #46 merge prep

**Date:** 2026-06-10
**Branch:** `ny-disclosure-explore`

## Summary

Goal for the session: finish the NY branch — empirically verify the compensation overlap between `client_semiannual` (chain spine) and `lobbyist_bimonthly` (currently only used for itemized expenses + person resolution) per GH #37, then if clean execute the GH #46 merge checklist and pause at the merge-confirmation gate.

The prior `fc6044a` commit (2026-06-07, claude.ai web) had resolved #37 documentarily — adding Caveat 11 to `releases/ny/README.md` stating "current build can't double-count by construction (only one dataset materialized); reconciliation deferred to first cross-dataset build." This session converted that into an empirical claim.

Two probe rounds. The first used only the local 38,404-row bimonthly JSON sample (1 bi-period per firm); the comparison was directional but couldn't test `SUM(3 bi periods) =? 1 semi` directly, so I surfaced to Dan with the 5-firm partial finding before locking the rule. Dan asked for the deeper probe; I added a targeted Socrata `$group` query for all 6 bimonthly periods of 5 firms (35 distinct filing tuples, 25s wall-time). With amendment-supersede applied to both sides via `max(form_submission_id)` per business key, the result was **11/11 cells matching to the cent**, including a load-bearing case where a semi amendment corrected $47,000 → $45,823 and the bi side independently reports $45,823 (the two filer-sides reconcile *by amendment*).

A second surfacing for #46: the chain TSV is now 238 MB (not the 53 MB cited in #46 — the 2026-06-08 disclosed-lawmakers columns 5×'d it), past GitHub's 100 MB hard per-file limit. Dan picked "force-add the 5 source TSVs only; chain stays gitignored as regenerable." Wrote one-sentence data-availability notes in both READMEs pointing at the existing chain reproducer.

## Topics Explored

- **Issue #37 — bi vs semi compensation overlap.** Two probe rounds; converged on an empirical SUM equality rule.
- **Amendment supersede on both sides.** STOP/Future of Life case showed the rule fails without it ($47,000 original → $45,823 amended on semi side; the bi side already had the amended $45,823 from its own filing). With supersede, both sides reconcile.
- **5-firm scope characterization.** Three retainer shapes tested: constant per-period (NYSEDC), variable per-period (CSEA), amendment-corrected total (STOP/Future of Life). All match.
- **Chain TSV size shock.** 53 MB → 238 MB between the prior session and now. Surfaced for Dan's decision; he picked force-add-sources-only.
- **README hygiene.** TL;DR file count was stale ("4 TSVs ~11 MB") — corrected to "5 TSVs ~42 MB" reflecting `NY_filing_parties_lobbied.tsv` joining the release on 2026-06-06.
- **2026-06-08 follow-up doc tracked.** The Phase 0 chain × parties_lobbied grain-check results doc that Dan ran locally was sitting untracked; committed as a separate hygiene commit so the 97.63% match-rate measurement survives on the branch.

## Provisional Findings (this session is the load-bearing source for these)

- **SUM(canonical bi periods of half-year H) = canonical semi(H) to the cent** for every `(principal_lobbyist, beneficial_client)` tested in 2025. The two datasets describe the same money on two cadences; naive concatenation = exact 2× double-count.
- **The rule depends on supersede on BOTH sides.** Raw concat without amendment-supersede on the bi side would also double-count *within* the bi dataset.
- **Cross-dataset business key is `(reporting_year, principal_lobbyist, beneficial_client, contractual_client_name)`.** `form_submission_id` is filer-side-specific (semi from client, bi from firm) — sequences are independent and not joinable across datasets.
- **`contractual_client_name` is the multi-client-retainer discriminator.** STOP retains two distinct clients (self + Future of Life Institute); without `contractual_client_name` in the key, their compensation would aggregate to one cell and the per-client reconciliation would fail.

## Decisions Made

- **#37 resolved** with empirically-strengthened Caveat 11 in `releases/ny/README.md` + new results doc `docs/active/ny-disclosure-explore/results/20260610_ny_bi_semi_reconciliation.md` + reproducer script `scripts/ny_probe_bi_semi_reconciliation.py`.
- **#46 chain-TSV strategy: force-add 5 source TSVs only; chain stays gitignored** (Dan's call). Both READMEs gain a one-sentence file-availability note.
- **Not merging this session.** Per the handoff, pausing at the merge-confirmation gate; Dan to merge explicitly.

## Results

- [`results/20260610_ny_bi_semi_reconciliation.md`](../results/20260610_ny_bi_semi_reconciliation.md) — the per-cell reconciliation table + method + supersede mechanics + scope caveats.
- [`results/20260610_ny_bi_full_pull.json`](../results/20260610_ny_bi_full_pull.json) — raw Socrata `$group` evidence (35 distinct bi filing tuples for the 5 firms).
- [`scripts/ny_probe_bi_semi_reconciliation.py`](../../../../scripts/ny_probe_bi_semi_reconciliation.py) — reproducer (Socrata query + local CSV scan + per-cell reconcile report).

## Open Questions

- **Full-sample sanity check on the SUM rule is owed once `lobbyist_bimonthly` is materialized.** 5 firms × 11 cells is enough for the binary "yes, they overlap; don't sum" verdict and to confirm three distinct retainer shapes; it isn't enough to claim every one of 2025's 1,333 firms × 4,373 clients reconciles to the cent. A run of the same script over the full bi pull (when one exists) is the natural next step.
- **Public-corporation universe untested.** This probe only touched the retained-lobbyist datasets. `public_corp_registration` + `public_corp_bimonthly` carry their own `compensation` field for in-house lobbyists; they don't overlap with the retained universe but have their own internal reconciliation question. Out of scope for #37.

## Next Steps

- Push the 3 new commits to `origin/ny-disclosure-explore`.
- Open the PR.
- Pause at merge-confirmation gate per Dan's handoff instruction.
- (Deferred to post-merge, per Dan-only convention) `git mv docs/active/ny-disclosure-explore docs/historical/ny-disclosure-explore` + STATUS row move from Active → Archived once the branch lands on `main`.

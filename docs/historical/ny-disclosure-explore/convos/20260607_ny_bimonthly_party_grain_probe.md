# NY `lobbyist_bimonthly` `party_name` grain probe

**Date:** 2026-06-07 (session began 2026-06-06 evening; substantive work + run landed morning of 2026-06-07)
**Branch:** `ny-disclosure-explore`

## Summary

Dan opened the session pointing at the chain-completion sketch
([`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md))
and asked what we had actually established about `parties_lobbied` and
`lobbyist_bimonthly`. After a state-of-the-branch briefing — `parties_lobbied`
heavily built out (98.61% legislator resolution, all 213 NY legislators covered,
artifact shipped); `lobbyist_bimonthly` known only from API probes, never pulled
— a sharp question from Dan ("parties lobbied is pretty valuable data; that
exists in bimonthly but not in semiannual?") forced an inspection of the
Phase-0 schema fixtures. Findings: **bimonthly does NOT have `parties_lobbied`
as a column**; it has a *singular* `party_name` column instead.

That singular-column shape suggested a possibly different grain — if `party_name`
is one-per-row at `(filing, focus)`, bimonthly could supply the per-bill
lawmaker tuples that the semiannual structurally cannot (Phase-0 settled
`parties_lobbied` is per-filing SET, cartesian-not-mapping). That would be a
material architecture change for the chain. Dan agreed to probe.

Built and ran `scripts/ny_probe_bimonthly_party_grain.py` (sister to the
existing `ny_probe_parties_lobbied_grain.py`). Two iterative design corrections
during the run (Dan correctly challenged a decorative `count(*)` smoke test that
was blocking real work on a slow Sunday-morning Socrata; subsequently had to
shrink the per-filing pull when the absolute-top-5 bimonthly submissions turned
out to carry 6–9 million rows each). Final run resolved the architectural
question and the name-format question in one pass.

## Topics Explored

- State briefing on what `parties_lobbied` and `lobbyist_bimonthly` have meant
  on this branch (the former: shipped artifact, 168k edges, 98.61% legislator
  resolution; the latter: known only from Phase-0 API probes, never pulled).
- Inspection of Phase-0 schema fixtures to verify column inventory for both
  datasets — corrected a prior overstatement in conversation that bimonthly
  carries a `parties_lobbied` column.
- Hypothesis: bimonthly's *singular* `party_name` might mean the contact
  reporting is per-row-per-`(filing, focus, party)` rather than
  per-filing-set — which would solve the cartesian-not-mapping result that
  blocks the chain from claiming `(lawmaker, bill)` tuples.
- Wrote and ran a probe to test (a) per-`(filing, focus)` distinct `party_name`
  count (the load-bearing test); (b) `party_name` name format vs the shipped
  `io/ny/parties` resolver; (c) delimiter-in-`party_name` check.
- Two probe-design corrections during the run: dropped a decorative `count(*)`
  smoke test that was blocking on slow Sunday-morning Socrata; switched from
  absolute-top-5 dense submissions (6–9M rows each, untenable to pull) to
  mid-size dense submissions (~7,500 rows each).

## Provisional Findings

- **Bimonthly is also cartesian (architecturally significant).** On 5 mid-size
  dense filings totaling 38,404 pulled rows / 133 distinct `(filing, focus)`
  pairs, **105 / 133 pairs (79%) carry ≥2 distinct `party_name` values**.
  Three pairs carry 164 distinct parties each. Bimonthly's effective grain is
  approximately `(filing × focus × party × expense_event)` fully crossed — the
  same structural problem as semiannual `parties_lobbied`, just denormalized
  differently. The yesterday-evening hypothesis that bimonthly might solve the
  per-bill resolution problem is dead.
- **Free upside: shipped resolver hits 100% on bimonthly's `party_name`.**
  Top-400 distinct `party_name` values cover 57,374,223 rows (99.1% of 2025
  bimonthly State Bill); of these 50,637,982 (88.2%) are legislator-titled, and
  the existing `io/ny/parties.resolve_party_lobbied` resolves **all** of them.
  Zero misses, zero resolver work owed if/when bimonthly is folded in.
- **`party_name` is genuinely singular.** Of the top-400 distinct values, only
  9 contain a `;` / `&` / ` and ` delimiter, and all 9 are committee or agency
  names ("Civil Service and Pensions (Senate Committee)", "Ways and Means
  (Assembly Committee)", etc.). Never multi-person lists.
- **Bimonthly submissions are enormous.** Top-5 worst-case 2025 bimonthly
  submissions carry 6.3M–9.1M rows each. Anonymous Socrata can't even
  `count(distinct ...)` over the full-year State-Bill subset (~58M rows) or
  one-period subset (~10M rows) within 600s. A full bimonthly pull would dwarf
  the 2.32 GB semiannual.
- **Bimonthly's value-prop is unchanged from Phase-0:** (1) individual-lobbyist
  names (semicolon-delimited rosters of actual humans in
  `individual_lobbyist_name` — semiannual only names firms), (2) itemized
  expenses (`expense_type`/`expense_paid_to`/`expense_purpose`, populated 100%
  on most sampled filings), (3) finer bimonthly time grain. None of these
  require per-bill grain to be useful.

## Decisions Made

- **Chain-completion sketch [`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md)
  stands as written.** Phase 4's deferral of `lobbyist_bimonthly` from the
  chain-completion scope was correct. The sketch's note that bimonthly "may
  carry additional attributes (e.g., contact-event grain finer than
  semiannual)" gets a one-line sharpening to reflect what we now know: the
  finer-grained rows are denormalized expense rows, not distinguishable
  contact events.
- **No bimonthly pull this session, no commit to one as next.** The decision
  on whether to fold bimonthly in (for individual-lobbyist names + itemized
  expenses) is unchanged from before this probe — same value-prop, same
  trade-off against a ~5× bigger pull + GH #37 cross-dataset double-count
  guardrail work.
- **No code changes shipped this session beyond the probe script.** Probe is
  pure analysis, no `releases/` or `src/` touches. The shipped
  `parties_lobbied` resolver was used as a library, not modified.

## Results

- [`results/20260607_ny_bimonthly_party_grain.md`](../results/20260607_ny_bimonthly_party_grain.md) — writeup of probe verdict + np distribution + name resolution rate
- [`results/20260607_ny_bimonthly_party_sample.json`](../results/20260607_ny_bimonthly_party_sample.json) — raw 38,404-row sample across 5 mid-size dense filings (provenance for the grain verdict)
- [`results/20260607_ny_bimonthly_party_top_distinct.json`](../results/20260607_ny_bimonthly_party_top_distinct.json) — top-400 distinct `party_name` values by 2025 State-Bill row weight (provenance for the 100% resolver match)

## Open Questions

- **Individual-lobbyist name resolution.** Bimonthly's `individual_lobbyist_name`
  is a semicolon-delimited list of person rosters (`'CAHN, ALBERT; Taper,
  Jason; WEINSTOCK, ANNE; Siffert, David'` — surname-first, mixed case,
  no titles). The shipped resolver only handles `party_name`-format strings
  ("Senator First M. Last") — it does not cover this format. Folding bimonthly
  for individual-lobbyist resolution would need a separate resolver design
  + collision-handling strategy. Not started.
- **Cross-dataset filing identity.** `form_submission_id` is the bimonthly's
  own report id and will NOT match semiannual ids. The semantic `FILING_KEY`
  (year + period + firm + client + contractual_client) is the only
  cross-dataset handle. Probe noted but did not test this join. GH #37
  (double-count risk) still owed.
- **The chain-completion plan's 4 open questions for Dan** ([`plans/ny_chain_completion_sketch.md`](../plans/ny_chain_completion_sketch.md))
  are unaffected by this probe and still owed.
- **Bimonthly resolution-rate caveat.** The 100% match on top-400 covers 99.1%
  of 2025 State-Bill rows — the residual ~0.9% (~520k rows) lives in less
  common `party_name` values and was not characterized. Could be former
  members, name variants, etc. Probably similar shape to the semiannual's
  pre-nickname-matcher residual, but unverified.

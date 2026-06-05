# Synthesis, audits, and merge decision

**Date:** 2026-06-02 (afternoon)
**Branch:** wi-allocation-matrix

## Summary

Started from the Phase 3.1 handoff (per-sponsor normalization + `item_id` shipped this morning). Dan asked for a discussion of the WI disclosure results before picking the next step from {unknown-chamber audit, cosponsor parsing, Phase 4 CFIS scoping}.

The discussion converged on producing a **Suhan-facing standalone synthesis** that integrates Phases 0 → 3.1 — not because the per-phase writeups were wrong, but because Phase 3.1 was the first endpoint where the chain produces interpretable findings (LeMahieu signal, two-profile chamber pattern) rather than infrastructure milestones. Drafted that synthesis as `results/20260602_wi_chain_synthesis.md`.

In drafting the synthesis I hypothesized a "leadership-vehicle pattern" to explain LeMahieu's #8 ranking on only 4 bills — plausible-sounding but unsupported. Dan called for tee-ing up the bill-level inspection. The data immediately disproved the hypothesis: LeMahieu's #8 ranking is **98.8% driven by one bill** (SB 28, electric-transmission ROFR, where he is sole primary sponsor and 29 principals — heavily concentrated in the electric-utility industry — filed effort totaling 1,067.8 hrs). Retracted the leadership-vehicle framing and replaced with the single-bill SB 28 finding, plus an explicit method-level lesson ("do per-bill inspection before claiming sponsor-level patterns externally"). Wrote `results/20260602_lemahieu_bill_inspection.md` and revised the synthesis.

Dan then chose to do the unknown-chamber audit (~30 min diagnostic) before discussing branch merge strategy. Audit surfaced another correction worth landing: the Phase 3.1 "1,288 hr unknown chamber bucket" was inflated by a fragile surname-based join. The corrected (`ocd-person/...` ID-based) figure is 590 hr / 1.2%, **all Joint Legislative Council** — a single collective entity. The missing 698 hr were three disambiguated-prefix legislators (B. Jacobson, L. Johnson, J. Jacobson) whose IDs resolve correctly but whose chain surnames carry initial prefixes the bare `family_name` doesn't match. Updated synthesis chamber-rollup numbers (Assembly 25,892 → 26,543; Senate 21,610 → 21,657; ratio 1.20× → 1.23×). Production code unaffected (only writes the name column, doesn't join on it).

Closed with a branch-merge discussion across the three wi-* branches (wi-disclosure-explore = done + merged; wi-tier1-direct-read = different workstream, owned by Dan's other agent; wi-allocation-matrix = ours, decision needed). Dan chose **option B (slice)**: merge current state now, with CFIS scoping going on a new branch off post-merge main; cosponsor parsing also on its own branch later. Chain TSV to be published in `releases/wi/chain/`. Used `finishing-a-research-branch` as the workflow skill (not finishing-a-development-branch — research branch lifecycle).

## Topics Explored

- Phase 3.1 results read-through (LeMahieu signal, two-profile chamber pattern, bill-id-collision finding)
- Suhan-facing synthesis structure (audience, what to lead with, what to caveat) — landed on standalone document rather than amendment to Phase 3.1 writeup
- LeMahieu bill-level breakdown: 4 bills, 98.8% concentration on SB 28, 29 principals with electric-utility coalition profile
- The Americans For Prosperity outlier on SB 28 (AFP historically opposes ROFR; chain can't infer position direction) — generalized to "the chain detects coalition *activity*, not coalition *composition*" as a project-wide finding
- Unknown-chamber audit: surname-based vs ID-based join surfaces 698 hr previously misclassified
- Joint Legislative Council vs Law Revision Committee — LRC has zero chain rows (no principals filed effort), invalidating part of the original hypothesis
- Three-branch merge strategy (wi-disclosure-explore, wi-tier1-direct-read, wi-allocation-matrix) — particularly the wi-tier1 interaction (snapshot date bump that fixes the 3 baseline failures on `test_pipeline.py`)
- Chain TSV publishing path: flat in releases/wi/ vs subdir; landed on `releases/wi/chain/` with its own README documenting the Plural Policy dependency

## Provisional Findings

- **LeMahieu's #8 sponsor ranking is one bill, not four** (SB 28, 98.8% of his total) — concrete signal worth surfacing externally with the bill-and-coalition framing rather than the sponsor-and-agenda framing
- **"Coalition activity vs coalition composition" is a project-wide finding**, not specific to SB 28 or LeMahieu — WI lobbying disclosure has no support/oppose field; the chain detects who was active on a bill, not which side they took. Probably belongs in compendium-side observations.
- **Per-sponsor metrics can compress single-bill signals into apparent broad patterns** — generalized method-level lesson logged in the synthesis. For any sponsor in a top-N list that gets external attention, the right next step is a per-bill breakdown.
- **Surname-based legislator joins are fragile** when disambiguation prefixes are present. Use `ocd-person/...` IDs.
- **Joint Legislative Council 590 hr is genuinely-unknown by-design** (collective entity, no chamber meaningful). Law Revision Committee has zero chain rows in 2025 — no principals filed effort on LRC items.
- **The "synthesis-first writing" failure mode is real:** an earlier draft of the synthesis included a plausible-sounding "leadership-vehicle pattern" hypothesis formed before looking at the per-bill data. Five minutes of inspection disproved it. Worth keeping the discipline of "inspect before claim" for any future Suhan-facing writeup.

## Decisions Made

- **Merge wi-allocation-matrix now** via `finishing-a-research-branch` workflow (option B / slice).
- **Phase 4 CFIS scoping → new branch off post-merge main.** Will use `nori-web-search-researcher` (or equivalent) to characterize the WI Ethics Commission access surface; deliverable is a scoping doc with explicit recommendation on whether to cut a `wi-campaign-finance` implementation branch.
- **Cosponsor parsing → new branch off post-merge main.** Three design decisions need to land in a plan before implementing: (a) schema shape (rows vs list-column), (b) `num_sponsors_on_bill` interaction with cosponsors, (c) regex test corpus characterization.
- **Chain TSV published at `releases/wi/chain/WI_chain_2025.tsv`** with its own README documenting the Plural Policy bulk-CSV dependency. Extends the `releases/` convention set by `5fcc6ac`. Committed in `6c595b5`.
- **3 baseline failures on `tests/test_pipeline.py`** (CA snapshot manifest missing at 2026-04-13) are inherited, not branch-caused, and are already fixed by `wi-tier1-direct-read`'s `a3bc1af`. Will be noted in PR body for reviewer context.

## Results

- [`results/20260602_wi_chain_synthesis.md`](../results/20260602_wi_chain_synthesis.md) — Suhan-facing standalone synthesis of Phases 0 → 3.1
- [`results/20260602_lemahieu_bill_inspection.md`](../results/20260602_lemahieu_bill_inspection.md) — bill-level inspection of LeMahieu's 4 bills; the SB 28 ROFR finding
- [`results/20260602_unknown_chamber_audit.md`](../results/20260602_unknown_chamber_audit.md) — corrected unknown bucket (590 hr JLC, not 1,288 hr unknown); corrected chamber rollup numbers
- Chain TSV publish: `releases/wi/chain/WI_chain_2025.tsv` + `releases/wi/chain/README.md` (committed `6c595b5`)

## Open Questions

- **CFIS access surface** — bulk download? API? scrape only? Principal-identifier shape? Lobbyist personal-donation disclosure path? All unknown until Phase 4 scoping runs on the new branch.
- **Position-direction gap on the compendium side** — does WI §13.62 / §13.685 require disclosure of position (support/oppose) on lobbied items? If yes, the chain's gap is a parser issue; if no, it's a permanent ceiling on what WI alone can support without external evidence. Worth a separate compendium-side investigation.
- **Cosponsor schema design** — three real options weighed but not chosen; belongs in the cosponsor-parsing branch plan, not here.
- **wi-tier1-direct-read merge timing** — Dan to coordinate. If wi-tier1 merges first, our PR inherits the snapshot-date fix and the baseline-failure footnote disappears.

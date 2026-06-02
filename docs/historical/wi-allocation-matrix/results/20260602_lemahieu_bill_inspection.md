# LeMahieu bill-level inspection

**Date:** 2026-06-02
**Branch:** `wi-allocation-matrix`
**Prerequisite to:** [`results/20260602_wi_chain_synthesis.md`](20260602_wi_chain_synthesis.md) (which has been revised based on these findings — see "Effect on the synthesis" below)
**Inspection script:** `/tmp/inspect_lemahieu.py` (one-off, not checked in)
**Data source:** `data/allocations/WI/WI_chain_2025.tsv` (150 rows where `sponsor_lawmaker_name == 'LeMahieu'`)

## TL;DR

LeMahieu's #8-ranked position in the post-per-sponsor-normalization top-20 sponsors is **98.8% driven by one bill**, not by a pattern across four bills. The bill is **SB 28**, electric-transmission right-of-first-refusal (ROFR) legislation where LeMahieu is the **sole primary sponsor** (`num_sponsors_on_bill = 1`, so per-sponsor = full effort) and where 29 distinct principals — heavily concentrated in the electric-utility industry — filed effort totaling 1,067.8 hrs.

My initial reading in the synthesis was "leadership-vehicle pattern — Majority Leader's caucus-priority bills draw concentrated lobbying across multiple bills he authors." The data does not support that. The actual pattern is **one bill, sole-sponsor, intense industry mobilization** — a much more specific signal.

## The 4 bills

| Bill | LeMahieu's role | Co-sponsors | Per-sponsor hrs (LM's share) | Un-normalized full-bill hrs | % of LM's total |
|---|---|---:|---:|---:|---:|
| **SB 28** | sole primary | 1 of 1 | **1,067.8** | 1,067.8 | **98.8%** |
| SB 258 | one of 15 primary | 1 of 15 | 11.2 | 167.7 | 1.0% |
| SB 119 | one of 10 primary | 1 of 10 | 1.5 | 15.3 | 0.1% |
| SB 699 | one of 3 primary | 1 of 3 | 0.7 | 2.2 | 0.06% |
| **Total** | | | **1,081.2** | 1,253.0 | 100% |

The cross-check matches the synthesis figures exactly (4 distinct bills, 1,081.2 hr sum), so the chain TSV is internally consistent. What's *different* is the within-LeMahieu distribution — concentration on SB 28 is far more extreme than I assumed.

## SB 28 — the bill carrying the signal

**Title:** "Relating to: an incumbent transmission facility owner's right to construct, own, and maintain certain transmission facilities and Public Service Commission procedures if the transmission facility is a regionally cost-shared transmission line."

**What this is:** Right-of-first-refusal (ROFR) legislation for incumbent electric transmission utilities. ROFR laws give the incumbent transmission owner (in eastern WI, predominantly American Transmission Co / ATC Management) the right to build new regionally cost-shared transmission lines without competitive bidding. ROFR has been a high-profile state-by-state policy battle for ~5 years, with the incumbent utilities pushing for it and competitive-bidding advocates (consumer groups, some free-market organizations) opposing.

**Sole primary sponsor.** `num_sponsors_on_bill = 1`. LeMahieu introduced this alone — no co-authors at all. This is what makes the per-sponsor hours (1,067.8) equal the full-bill hours (1,067.8).

**29 principals filed effort.** Top 10 by per-sponsor (= full-bill) modeled hours:

| Rank | Principal | Modeled hrs | # of LM's lobbyists they share with | Semesters |
|---:|---|---:|---:|---|
| 1 | **ATC Management Inc.** (American Transmission Co — the incumbent monopoly) | 331.0 | 11 | H1, H2 |
| 2 | WEC Energy Group, Inc. | 134.4 | 10 | H1 |
| 3 | Wisconsin Industrial Energy Group Inc | 124.3 | 4 | H1, H2 |
| 4 | **Americans For Prosperity** | 86.6 | 4 | H1, H2 |
| 5 | Dairyland Power Cooperative | 51.6 | 4 | H1 |
| 6 | Madison Gas & Electric Company | 51.1 | 3 | H1 |
| 7 | Northern States Power d/b/a Xcel Energy | 39.9 | 5 | H1 |
| 8 | Alliant Energy | 29.3 | 6 | H1 |
| 9 | Wisconsin Utilities Association Inc | 28.7 | 2 | H1, H2 |
| 10 | Municipal Electric Utilities of Wisconsin | 28.1 | 3 | H1 |

This is a near-complete who's-who of WI electric utility interests. ATC (the bill's immediate beneficiary) is the largest single filer at 331 hrs. The next 5 (WEC, WIEG, Dairyland, MGE, Xcel) are the major investor-owned and cooperative utilities. WUA and MEUW are the industry trade associations.

**The AFP outlier matters and needs a position-direction caveat.** Americans For Prosperity (Koch-affiliated free-market advocacy) filed 86.6 hrs on SB 28 — placing them #4 among 29 principals on a utility bill. AFP has historically *opposed* ROFR legislation in other states on anti-competitive / crony-capitalism grounds. **The WI lobbying data has no support/oppose field**, so the chain only tells us "AFP was active on this bill," not which side. Any external presentation should explicitly disclose this — listing AFP next to ATC and the utilities reads as "industry coalition" by default, which may be the opposite of what's happening.

## The other 3 bills

**SB 258** (advanced practice registered nurses, 15 co-sponsors) — modest medical/nursing-association lobbying (Wisconsin Medical Society, Wisconsin Nurses Association, Wisconsin Association of Nurse Anesthetists, etc.). LeMahieu's per-sponsor share is 11.2 hrs because the effort spreads across 15 co-authors.

**SB 119** (Office of School Safety positions, 10 co-sponsors) — 3 principals (Navigate 360, WI Council of Religious & Independent Schools, League of Women Voters of WI), 1.5 hrs to LeMahieu after the 10-way split.

**SB 699** (alternative methods of pupil transportation, 3 co-sponsors) — single principal (WI School Bus Association), 0.7 hrs to LeMahieu.

These are all background-level lobbying signals. None contributes meaningfully to LeMahieu's ranking.

## What this changes about the synthesis

**The original synthesis section on LeMahieu has been revised.** The previous "leadership-vehicle pattern" hypothesis was a plausible-sounding inference made before looking at the per-bill breakdown. It does not survive contact with the data: a leadership-vehicle pattern would predict the lobbying weight distributed across multiple bills LeMahieu personally authored, not 98.8% concentration on one industry-specific bill.

The corrected reading is more specific and more useful:

- **The chain can detect single-bill concentration with high specificity.** A one-bill signal of this magnitude (98.8% of a top-10 sponsor's modeled hours) is exactly the structural-power evidence the chain is supposed to surface, *but the unit is the bill, not the sponsor's general agenda*.
- **Why LeMahieu specifically?** Open question — needs domain context. Plausible hypotheses (none verified): (a) Senate Majority Leader role makes him strategically valuable as the sponsor of a controversial industry bill, because he controls floor scheduling; (b) the WI Energy & Utilities committee assignment / chair structure; (c) personal policy interest. None of these are testable from the chain alone — they require legislative-process knowledge.
- **The chain doesn't tell us position.** The 29 principals filed effort on SB 28; we don't know who supported and who opposed. The AFP-vs-ATC tension is the cleanest example of why this matters.
- **"Concentrated Senate primaries" pattern from the synthesis still holds** — for sponsors like Cabral-Guevara (108 bills), James (104), Tomczyk (118), the lobbying is distributed across many bills, not single-bill-driven. LeMahieu is a different shape — single-bill concentration — and should be described separately.

## Suggested phrasing for any external (Suhan / weekly update / future deliverable) use

> The Phase 3.1 chain surfaces a sharp single-bill signal: 98.8% of Senate Majority Leader Devin LeMahieu's modeled-lobbying weight in 2025-2026 concentrates on **SB 28**, electric-transmission right-of-first-refusal legislation that he introduced as sole primary sponsor. 29 principals filed lobbying effort on the bill, heavily concentrated in the electric-utility industry — ATC Management (the incumbent transmission monopoly the bill benefits) at 331 hours, followed by WEC Energy, WI Industrial Energy Group, and the major investor-owned utilities. Americans For Prosperity also filed substantial effort (86 hours), but the WI lobbying data does not disclose position direction, so AFP's role on this bill (historically opposed to ROFR elsewhere on anti-competitive grounds) cannot be inferred from filings alone. The chain detects the *coalition's activity*; it does not adjudicate the *coalition's composition*.

This phrasing leads with the bill, not the sponsor; flags the position-direction gap; and is defensible to ROFR-policy specialists who might read it.

## Open questions for follow-up

1. **What's the lobbyist breakdown for ATC's 331 hrs on SB 28?** 11 lobbyists is a lot for one bill — is each contributing ~30 hrs (broad coverage) or is one eating most of the budget (single-tactician)? This is a deeper IPF-residual question — interesting but not blocking.
2. **AFP position direction.** The chain can't answer this from WI filings. Cross-reference: AFP press releases / WI legislative testimony records / news coverage of SB 28. Probably ~30 min of web research.
3. **Cross-state ROFR pattern.** ROFR bills have moved through ~15 states in the last 5 years; many failed. WI's SB 28 fits a national industry-priority pattern. Worth a sentence of context in any external write-up.
4. **Position-direction gap is a project-wide finding.** The fact that the chain *cannot* distinguish "lobbying for" from "lobbying against" without a separate data source is a general limitation of WI's disclosure regime, not specific to SB 28. Worth surfacing this as a compendium-side observation (does WI §13.62 / §13.685 require disclosure of position? Cross-check before claiming.).
5. **Method-level lesson: do bill-level inspection before claiming a sponsor-level pattern.** Per-sponsor metrics can compress a single-bill signal into what looks like a broad pattern. For any sponsor in the top-20 that gets external attention, the right next step is a 5-minute per-bill breakdown like this one.

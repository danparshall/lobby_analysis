# State Disclosure Infrastructure Tiers

**Provenance:** `docs/active/research-prior-art/convos/20260410_scoping-kickoff.md`
**Last updated:** 2026-04-10
**Branch:** `research-prior-art`

## Purpose

Profile the US state lobbying disclosure landscape by data accessibility tier and identify the priority-state shortlist for the initial 5–8 states the pipeline will cover. This file also documents the "three keys" statutory analysis (which states require compensation + bills-lobbied + position-taken in the same filing) and flags a methodological concern with the F Minus 2024 report.

## The Four Tiers

Tiers are assigned based on data accessibility for a researcher trying to ingest itemized filings programmatically, not on statutory strictness. A state can have strong disclosure laws on paper and still be Tier 3 if the actual data is hard to get at.

### Tier 1 — Bulk-Accessible, Granular, Timely

States where itemized filings are available in bulk (API, CSV download, or similar), reasonably timely, and include enough detail to support bill-level position extraction.

| State | Portal / Mechanism | Notes |
|---|---|---|
| Colorado | Secretary of State lobbying portal | Requires position disclosure within 72 hours of action; this is unusual and makes CO the best real-time data source in the country |
| Washington | Public Disclosure Commission open data API | Approximately 11.5 million records accessible, but **only about 8% of filings include a parseable bill number** — a major caveat for bill-level analysis |
| California | CAL-ACCESS daily bulk download | The California Civic Data Coalition has built tooling around this for years; we can learn from their approach |
| Wisconsin | Government Accountability Board "Eye on Lobbying" | Publicly accessible since 2003, stable format |

### Tier 2 — Accessible but Constrained

States where data is accessible via an official portal but has one or more constraints: slower updates, less granular fields, harder-to-parse formats, or restricted bulk access.

New York (post-2023 ECRA reform), Texas, Florida (which has a dual-system architecture that complicates normalization), Illinois, Minnesota, Massachusetts, Iowa, Nebraska, New Jersey, Rhode Island.

### Tier 3 — Portal Only, Limited Bulk Access

States with searchable web portals but no usable bulk-download path. Scraping is possible but slow and fragile. Michigan, Virginia, Ohio, North Carolina, Georgia, Arizona, Indiana, Missouri, Tennessee, Louisiana, Kentucky.

### Tier 4 — Structural Gaps

States with minimal online infrastructure, paper-heavy processes, or both. North Dakota, South Dakota, Wyoming.

## The "Three Keys" Statutory Analysis

Three data elements, when present in the same filing, enable quantitative bill-level lobbying analysis:

1. **Compensation** — how much the lobbyist or firm is being paid (or spending)
2. **Bills lobbied** — which specific bills the lobbying activity addressed
3. **Position taken** — whether the lobbyist supported, opposed, or engaged on each bill

Only **8 states** statutorily require all three keys:

**CO, IA, MA, MT, NE, NJ, RI, WI**

Most other states require some combination of one or two, or allow free-text "general issue" descriptions that are much harder to parse into bill-level positions. The presence of the three keys doesn't guarantee the data is *accessible* — Montana requires all three but has the dual paper/electronic regime documented below — but their absence means even a perfect pipeline cannot reconstruct bill-level positions from state filings without LLM-based inference or cross-referencing other sources.

## Candidate Priority-State Shortlist (8)

**California, Colorado, New York, Washington, Texas, Wisconsin, Illinois, Florida.**

Selection rationale:
- **California, Colorado, Washington, Wisconsin** are Tier 1 with bulk access and (for CO and WI) the three-keys statutory floor.
- **New York and Illinois** are Tier 2 and are politically / economically significant enough that any serious state lobbying dataset that omits them is incomplete.
- **Texas and Florida** are Tier 2 and represent architectural diversity — TX has a particular filing structure and FL has a dual-system that stress-tests the normalization layer. They are also two of the largest state legislatures by lobbying expenditure.

The three left off the shortlist that were strong contenders:
- **Massachusetts** (Tier 2, three-keys state) — defensible to include; left off mainly to keep the initial scope at 8.
- **Minnesota** (Tier 2) — solid data quality, smaller scale.
- **New Jersey** (Tier 2, three-keys state, ELEC enforcement) — strong on every axis but the state is smaller than the cut line.

## Montana: A Detailed Counterexample

Montana is worth flagging as a case study in why statutory "three keys" requirements don't automatically translate to usable data.

- Montana requires compensation + bills lobbied + position taken statutorily.
- Since ~2019 Montana has run a **dual system**: the electronic Political Lobbying Online Reporting System (PLORS) and a parallel paper filing system. Approximately 80% of lobbyists file electronically, but the paper filings are not systematically transferred into PLORS — they are digitized as hardcopy images on a separate platform.
- The **December 2024 Montana Legislative Audit Division report "Public Access to Lobbying Information"** exposed that state staff do not transfer paper data into PLORS, perform only a "brief review" of filings, and do not treat "bills and subjects" as the focus of their review. Compliance monitoring is minimal.
- **HB 804 (2025)** mandates all-electronic filing effective **October 1, 2025**. This fixes the problem going forward but does not retroactively digitize the paper archive.

Implication for the pipeline: Montana is a good medium-term target (post-October-2025) but historical data coverage will be permanently incomplete on the paper-only side.

## Enforcement-Gap Survey

Every state has statutory penalties for late or inaccurate filings. Almost no state actually enforces them at a meaningful cadence. Selected examples:

- **California** — $10/day late fee plus FPPC penalties of up to $5,000 per violation. Enforcement is selective and typically driven by media attention.
- **Washington** — up to $10,000 per violation. The PDC has the enforcement authority but exercises it rarely relative to volume.
- **Massachusetts** — $50/day, no cap. Rare to see referrals.
- **New Jersey** — ELEC escalates $50 → $1,000 per violation. ELEC is one of the more active enforcers but is resource-constrained.
- **Pennsylvania** — tiered fines plus a 5-year lobbying ban for egregious cases. Ban has been used.
- **Ohio** — $250 plus referral to the Attorney General.

The pattern mirrors the federal regime. GAO-25-107523 (April 2025) shows that even at the federal level, where enforcement is centralized in the US Attorney's Office for DC, 3,566 referrals accumulated between 2015 and 2024 with approximately 63% still unresolved as of December 2024. State-level enforcement is structurally weaker.

**Qui-tam / whistleblower bounties do not exist for lobbying disclosure in any US state.** Qui tam is a creature of the False Claims Act, which addresses *fraud against government money*, and lobbying non-disclosure is an *informational harm* that does not fit the FCA frame. The informal argument that "bounties would flood ethics commissions with frivolous claims" is also plausible. The project's policy posture is that the pipeline **itself** is the enforcement multiplier — the Brandeis "sunlight" frame, not the qui-tam frame.

## F Minus 2024 — Methodological Caveat

The **F Minus 2024** state lobbying transparency report grades states on disclosure accessibility. The report's headline finding is that 27 states receive failing grades and Colorado alone receives an A. This may be true, but it is suspicious on its face for two reasons:

1. The distribution is far more bimodal than other state-transparency rankings (e.g., the Center for Public Integrity's 2015 State Integrity Investigation, or the R Street Institute rankings). That could reflect a genuine methodological improvement, or it could reflect a grading rubric with too-tight thresholds.
2. The report's methodology section does not enumerate the specific indicators being scored in a way that allows external replication.

**Recommendation:** Do not use F Minus 2024 as a primary input to state selection without an independent verification pass. Use it as a hypothesis generator ("these states are worth looking at more carefully") rather than as a scoring ground truth. FOCAL (Lacy-Nichols et al. 2024, 8 categories × 50 indicators) is a more transparent alternative rubric, though it has been applied primarily to country-level rather than US-state-level disclosure regimes.

<!-- Generated during: convos/20260521_hg_vintage_finding_and_deferral.md -->

# HG vintage correction — CPI "Hired Guns" is a 2003 survey, not 2007

**Date:** 2026-05-21
**Branch:** phase-c-projection-tdd
**Status:** Finding; awaiting cross-cutting rename + HG-implementation deferral.

## TL;DR

The CPI "Hired Guns" rubric has been labeled `CPI_2007_*` throughout this project (papers folder, compendium spec, plan doc, RESEARCH_LOG, v2 row provenance). **The underlying survey was actually conducted and published May 15, 2003.** No second survey was ever produced. The "2007" attribution propagated from CPI's modern WordPress page metadata (which appears to bear a "last-updated 2007" stamp from a December 2007 commentary article) into Lacy-Nichols 2024/2025, and from L-N into our spec doc.

This branch defers HG implementation rather than executing the rename + retrieval work now. Reason: Path A validation needs 2003-vintage statute data for 50 states, which we mostly don't have. Tracked as a GitHub `task` issue for resumption when 2003-vintage retrieval becomes a research line.

## Evidence chain

### 1. CPI's own archives roll-up (2008 wayback capture)

URL: <https://web.archive.org/web/20081110094417/http://projects.publicintegrity.org/hiredguns/default.aspx?act=archives>

CPI's "Hired Guns" archives page (captured Nov 2008) lists every article CPI published under the Hired Guns project banner. The full datelined list:

- **May 15, 2003** — *Special Report: Hired Guns* — Lobbyists spend loads of money to influence legislators ($715M / 39 states in 2002)
- **May 15, 2003** — *Sunset in Harrisburg* — Pennsylvania zero score
- **May 15, 2003** — *How the Feds Stack Up* — Federal lobby disclosure law substantially weaker than most states
- **May 19, 2004** — *Under Pressure* — commentary on 2003 ranking ($889M / 41 states in 2003)
- **Aug 10, 2005** — *State Lobbyists Near the $1 Billion Mark*
- **Aug 10, 2005** — *Lobbying Laws in the States* — 16-state roundup referencing 2003 ranking
- **Mar 1, 2006** — *States Outpace Congress* — subtitle: *"24 states have made disclosure strides since 2003"*
- **Oct 12, 2006** — *From Lobbyist to Legislator* + *No Longer on Staff* (ex-legislator/staffer-to-lobbyist features)
- Copyright: *© 2008, The Center for Public Integrity*

**No December 2007 ranking article appears.** Every entry treats the May 2003 ranking as the reference dataset.

### 2. 2010 wayback capture of the scorecard page still says "2003"

URL: <https://web.archive.org/web/20100706094146/http://projects.publicintegrity.org/hiredguns/nationwide.aspx?display=DRFEC>

The 2010-07-06 capture (7 years after the May 2003 survey) still carries:

- Page header: **"Lobby Disclosure Ranking 2003"**
- Dateline: *"WASHINGTON, May 15, 2003 — The Center for Public Integrity conducted a survey of lobby disclosure laws in all 50 states..."*
- Update note: *"The office of the Secretary of the Commonwealth of Virignia contacted us in March 2004 to provide additional information... the Center has revised the Virginia score, moving it into a tie for 16th place, up from 32nd place."*

By July 2010, CPI had been hosting this same ranking for 7 years without updating it.

### 3. Per-state per-question scorecard exists and is retrievable

Wayback CDX listing of `projects.publicintegrity.org/hiredguns/*` (2008 and 2010 captures) shows per-state URLs of the form:

```
nationwide.aspx?st=AL&display=DRStateNumbers
nationwide.aspx?st=AK&display=DRStateNumbers
... [all 50 states + Federal]
```

These pages contain the per-question score breakdown for each state — the Path A 1,900-cell ground truth (50 states × 38 in-scope items, after dropping enforcement + revolving-door per the disclosure-only Phase B qualifier). Not yet scraped or saved.

### 4. CPI tag vs. survey name distinction (per user)

CPI uses "Hired Guns" as a persistent **topic tag** on their site, not just as the name of the 2003 survey. The tag URL <https://publicintegrity.org/topics/politics/state-politics/influence/hired-guns/> still aggregates all articles CPI files under this topic, including post-2003 commentary. This is why the modern CPI methodology page bears a "2007" stamp — likely the date of the most recent article that linked back to the methodology (the December 2007 commentary piece), not the year of the methodology itself.

### 5. L-N 2024/2025 propagated the "2007" mistake

**Lacy-Nichols 2024** (FOCAL scoping review):
- Bibliography ref [33]: *"Center for Public Integrity. Hired Guns Methodology. **2007**. https://publicintegrity.org/politics/state-politics/influence/hired-guns/methodology-5/. Accessed January 22, 2024."*
- Body text: *"...particular Opheim's 1991 index and the Center for Public Integrity's **2007** Hired Guns methodology."*
- Table 2 row: *"Public Integrity[a] **2007** [...] Hired Guns / Partly / US states / 8"* — the "8" matches the 2003 methodology's 8 disclosure areas.

**Lacy-Nichols 2025** (Lobbying in the Shadows + supplement):
- Same citation pattern in both — both date HG as 2007, both cite the `methodology-5/` URL accessed Jan 22, 2024.

The L-N grad students cited CPI's modern page metadata without doing wayback archaeology. Three independent academic citations all repeated the same mistake.

### 6. Methodology content is identical between 2003 wayback and modern CPI page

The methodology PDF in `papers/CPI_2007__hired_guns_methodology.pdf` was a Firefox print from April 2026 of CPI's modern `methodology-5/` page. The methodology described there — 8 disclosure areas, 48 questions, 100-point scoring scheme, multiple-choice answer tiers — matches the methodology described on the 2003 wayback ranking page exactly. The survey *questions* are stable; what's at issue is the *vintage of the per-state scorecard*, which is 2003 and 2003 only.

## Implication for HG validation regime

Vintage = 2003 (statute data as of late-2002 / early-2003).

To validate `project_hg_2003_lobby_disclosure(cells, state) → score` against the CPI 2003 per-state scorecard, we need 2003-vintage statute snapshots feeding the v2 cells. Today's cells reflect today's statutes; any drift over 23 years would be measured as projection error.

### Justia historical coverage probe (small sample, user-supplied, 2026-05-21)

User checked Justia's earliest historical-code year for 13 states:

| Justia earliest year | States | Drift from HG 2003 |
|---|---|---|
| 2003 | FL, WA | 0 yr (vintage-exact) |
| 2005 | CA, OR, ID, MO, VT | 2 yr |
| 2006 | OH, AL, GA, VA | 3 yr |
| 2010 | TN | 7 yr |
| 2016 | CO | 13 yr |

Sample breakdown: 15% at 2003 (2/13), 38% at 2005 (5/13), 31% at 2006 (4/13), 15% at 2010+ (2/13).

**Generalization caveat:** 13 of 50 states. If the pattern holds, ~7-8 states would be vintage-exact at 2003 — enough for narrow strict-Path-A validation (76-300 strong cells, similar scale to Newmark 2017's 100 sub-aggregate cells). But CPI's own *"States Outpace Congress"* (Mar 2006, *"24 states have made disclosure strides since 2003"*) explicitly flags non-zero statute drift between 2003 and 2005-2006. We can't mix the 2005-2006-vintage Justia states into Path A without measuring 23 states' worth of reform as projection error.

### What would unblock HG (future research line)

50-state 2003-vintage statute retrieval. Likely combines:
- Justia 2003 codes where available (~2 states confirmed in sample, ~7-8 expected at scale)
- Wayback captures of state legislative portals at 2003-2004 (variable coverage; smaller states likely uncovered)
- State archives / law libraries for the remainder

Not a 30-minute task. A multi-day research line on its own, comparable in shape to `oh-statute-retrieval` but at 50-state breadth.

## Decision (2026-05-21)

1. **HG implementation deferred** for this branch. Joins Opheim 1991 (blocked on 1988-89 statute data) as out-of-scope for `phase-c-projection-tdd`. Mergeable rubric scope contracts from 8 → 6 (CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, FOCAL 2024).
2. **Rename work also deferred.** The cross-cutting `CPI_2007_*` → `CPI_2003_*` rename (papers folder, compendium spec, plan, RESEARCH_LOG, archived `compendium-source-extracts/` material) is real cleanup work but doesn't need to happen until HG implementation resumes. Touching archived material has higher coordination cost (multi-committer); better to do it as a single sweep when 2003-vintage retrieval has landed.
3. **Tracked as GH `task` issue** so the deferred-not-deleted state has a discoverable handle. When 2003-vintage retrieval becomes a research line, the task resurfaces with full context (this findings note, the existing `20260518_hg_2007_plan.md`, the wayback retrieval target URLs).
4. **FOCAL 2024 is the next implementation** on this branch. Plan-set already drafted; legal_core first per locked ordering.

## Open questions (to revisit on HG resumption, not now)

- Does CPI's `methodology-5/` slug imply versioning history (methodology-1 through methodology-4) we should examine? Or is it WordPress slug-collision auto-numbering? Cheap to check via wayback CDX if it ever matters.
- Are there 50-state 2003-vintage statute archives outside Justia + wayback? E.g., NCSL historical databases, state law-library digital collections, FollowTheMoney's archive.
- Does L-N's citation-quality bar have other gaps that affect FOCAL Suppl File 1's 1,372-cell weight matrix? The FOCAL summary already survived its pre-merge factual audit with one real correction + one clarity tightening; that was framework-coding accuracy. This vintage error is a different mode (bibliographic carelessness on a non-load-bearing source detail). Doesn't directly impeach Suppl File 1 but worth keeping in the back of our head when leaning hard on L-N for FOCAL ground truth.

## Sources / artifacts

- Wayback 2008 capture (50-state totals): <https://web.archive.org/web/20081128224546/http://projects.publicintegrity.org/hiredguns/nationwide.aspx>
- Wayback 2010 capture (still says 2003): <https://web.archive.org/web/20100706094146/http://projects.publicintegrity.org/hiredguns/nationwide.aspx?display=DRFEC>
- Wayback per-state URL pattern (Path A retrieval target): `nationwide.aspx?st=XX&display=DRStateNumbers`
- CPI archives roll-up (2008 capture, full datelined article list): <https://web.archive.org/web/20081110094417/http://projects.publicintegrity.org/hiredguns/default.aspx?act=archives>
- CPI modern methodology page (L-N's cited URL): <https://publicintegrity.org/politics/state-politics/influence/hired-guns/methodology-5/>
- CPI Hired Guns topic tag (persistent tag, not survey name): <https://publicintegrity.org/topics/politics/state-politics/influence/hired-guns/>
- Existing HG implementation plan (now deferred): [`../plans/20260518_hg_2007_plan.md`](../plans/20260518_hg_2007_plan.md)
- Project methodology text (Firefox print of modern CPI page): `papers/CPI_2007__hired_guns_methodology.{pdf,html,txt}` — content matches 2003 methodology; filename misdates the source.

# CSG Blue Book / Book of the States / COGEL Blue Book — Acquisition Findings

**Session:** 2026-05-03 (afternoon)
**Branch:** `compendium-source-extracts`
**Triggered by:** Plan Step 4 (Task #11) — acquire CSG/COGEL/State-Capital reference works to recover operational definitions for Opheim 1991 / Newmark 2005 / Newmark 2017 / Strickland 2014.
**Outcome:** Structural finding (the three "Blue Books" collapse into one publication series) + retrievability map. Cell-level content not retrieved this session.

---

## Headline finding: there are not three Blue Books, there are two

The plan named three reference works (CSG Blue Book, CSG *Book of the States*, COGEL Blue Books) plus the State Capital Handbook. After bibliographic verification (WorldCat, Stanford SearchWorks, HathiTrust, COGEL CDN), the structural picture is:

1. **CSG Blue Book = COGEL Blue Book.** They are the same publication series. Full title: *Campaign Finance, Ethics, Lobby Law & Judicial Conduct: COGEL Blue Book*, jointly published by the Council of State Governments and the Council on Governmental Ethics Laws since the early 1980s. WorldCat OCLC 80682979. The "1988-89 Special Edition" Opheim 1991 cited and the "COGEL Blue Books" Strickland 2014 cited at the early end of his 1988-2013 panel are the **same series at different vintages**.

2. **Book of the States** is genuinely separate — a different CSG annual covering all aspects of state government, with a lobbying-regulation chapter active through ~2005. Newmark 2005 and Strickland 2014 used it alongside the Blue Book.

3. **State Capital Handbook** is a third, commercial publication — the post-2004 BoS replacement Strickland used for 2004-2013.

So scope-wise: two acquisition targets in the open-access tier (Blue Book + BoS) and one in the commercial tier (State Capital Handbook).

---

## Per-target retrieval status

### Target 1 — COGEL Blue Book (= CSG Blue Book)

**Structure of the series.**

Phase 1 (~1982–early 1990s): single comprehensive volume covering campaign finance, ethics, lobby law, and judicial conduct in standardized comparative tables. **The 1988-89 Special Edition (used by Opheim) and the 1990 8th edition (verified on HathiTrust) are this format.**

Phase 2 (1996/1997–present): COGEL split the comprehensive Blue Book into thematic annual *Updates*: Ethics Update, Lobbying Update, Campaign Finance Update, Freedom of Information Update. The Lobbying Update since 1997 is by Kenneth A. Gross and is described in bibliographies as a "legislation and litigation" news series — different format from the Phase 1 comparative tables.

**This format change matters: the document Strickland 2014 used to extend Newmark backward (1988-2003) was Phase-1 format. The Phase-2 Lobbying Updates (post-1997) likely cannot fill the same role, even if retrieved, because they are not state-by-state comparative tables.**

**Retrieval status:**

| Edition | Public availability | Retrieved this session |
|---|---|---|
| 1988-89 Special Edition | Not located on web | No |
| 1990 8th Edition | **HathiTrust ID `mdp.39015077214750`, marked "Public Domain, Google-digitized"** | TOC only (web_fetch on `babel.hathitrust.org` returns 403; institutional auth presumably required despite public-domain status) |
| 1993 edition | WorldCat / Stanford SearchWorks listings | No |
| Subsequent Phase-1 editions | WorldCat listings only | No |
| 2024 Ethics Update (Phase 2) | `cdn.ymaws.com/www.cogel.org/.../cogel_blue_book_2024_ethics_.pdf` (626pp, public) | Fetched as reference (different format — self-reported ethics-agency narratives, not comparative tables) |
| 2024 Lobbying Update | URL pattern not found via search | No |

**Recovered structural information for the 1990 8th edition** (from HathiTrust catalog metadata, Tables of Contents, and search snippets):

The Lobby Laws section contains 5 tables:

1. **Table 28 — Lobbyists: Definition, Registration and Prohibited Activities.** Maps to Newmark 2005's 7 definition items + 4 prohibition items + Opheim's 7 definition items. Also implies registration data.
2. **Table 29 — Lobbyists: Reporting Requirements.** Maps to Newmark 2005's 7 disclosure items + Opheim's 8 disclosure items.
3. **Table 30 — Lobbying: Report Filing.** Filing-mechanism details (likely cadence, public access, where filed).
4. **Table 31 — Lobbying: Compliance of Selected Agencies.** Enforcement powers — **maps directly to Opheim's 7 enforcement items.** This table is therefore the source Newmark dropped when he reduced Opheim's 22-item index to his own 18-item index for 1990–2003.
5. **Table 32 — Education and Training: Lobbying Regulation.** **Used by neither Opheim nor Newmark nor Strickland.** Potentially a new dimension.

### Target 2 — *Book of the States* (1988-2005, lobbying chapters)

**Status:** Not located on web. Stanford / Google Books / HathiTrust catalog records exist; full-text public access not found. The 2005 vintage is explicitly de-prioritized per the user's note ("we probably don't lose much if we can't find Book of States from 2005, since Opheim and Newmark already have the items copied").

**What's recoverable from the 26 existing extracts:**
- Newmark 2005's 18 items (`items_Newmark2005.tsv`) are explicitly *operationally defined by* the 1988-2003 BoS volumes — those operational definitions are the BoS content, just stripped of state-by-state values.
- Opheim 1991's items (`items_Opheim.tsv`) include 1 item (out of 22) sourced from BoS 1988-89; the other 21 are CSG Blue Book.

**Implication:** if the BoS content is functionally already in `items_Newmark2005.tsv` + `items_Opheim.tsv` at the row-label level, the only thing the original BoS volumes would add is the **threshold magnitudes and cell-level coding rules** — same gap as the Blue Book. ILL or library acquisition only.

### Target 3 — State Capital Handbook

Full title: Christianson, Coyle, Poliakoff & Dyer (then Christianson et al., later SCG Legal / Thomson Reuters), *Lobbying, PACs, and Campaign Finance: 50 State Handbook.* Annual editions, West Publishing → Thomson Reuters since at least 2003.

**Status:** Strictly commercial. 2024 ed. ~$200; 2025 ed. is 1860pp, ~$200 used on eBay. No public-domain version. Not retrievable via web_fetch.

**Marketing copy describes the structure as:**
- Detailed coverage of prohibited lobbying practices, enforcement, and penalties
- Discussion of registration, recordkeeping, and reporting requirements + lists of state-specific forms
- Names, addresses, phone numbers of local commissioners and compliance officers

This is structurally compatible with Newmark's coding categories (definitions / prohibitions / disclosure) plus the contact-information layer that's relevant for portal acquisition.

---

## What this means for compendium 2.0

Three load-bearing observations:

### 1. Strickland inherited Newmark's drop of Opheim's enforcement items

From the Strickland extract (`items_Strickland.md`):
> "I employ a measure of lobby law stringency... Newmark's (2005) measure assumes values from 0 to 18 depending on the presence or absence of specific lobby laws. In this index, lobby laws come in three categories: definitions of lobbyists, prohibitions on their conduct, and reporting requirements... I utilize the three categories of lobby laws in Newmark's index as separate explanatory variables."

Strickland reapplies Newmark's 18 items unchanged. Newmark 2005 dropped Opheim's 7 enforcement items (oversight-agency powers: subpoena witnesses, subpoena records, conduct hearings, impose fines, impose penalties, file court actions, thoroughness of report review) when he restructured to definitions/prohibitions/disclosure. **Yet the COGEL Blue Book Table 31 — "Compliance of Selected Agencies" — IS the enforcement table.** So Newmark and Strickland both had access to enforcement data and chose not to use it. Compendium 2.0 should consciously decide whether to re-incorporate those items (they are already in `items_Opheim.tsv`, just frozen at 1991 vintage).

### 2. Table 32 (Education and Training) is unused by all three

None of Opheim, Newmark, or Strickland coded education/training items. The Blue Book has them. Other rubrics in the corpus also have items in this domain — `items_AccessInfo.tsv` has 7 such items, `items_CouncilEurope.tsv` has 6, `items_SOMO.tsv` has 3, `items_TI_2016.tsv` has 2. So the gap isn't that the topic is irrelevant; it's that the older state-rubric tradition didn't track it.

### 3. The Phase 1 → Phase 2 format change broke the comparative-tables tradition around 1997

Strickland used "biennial editions" of the COGEL Blue Book for 1988-2003. After 1996/1997, the comprehensive volume was replaced by thematic Updates that are structured very differently (legislation+litigation summaries, not state-comparative tables). The 2024 Ethics Update I retrieved confirms this. **This is why the State Capital Handbook became necessary as a Strickland source for 2004-2013** — the Blue Book lineage that Newmark and Opheim relied on no longer existed in the same format.

For compendium 2.0 design: do not assume there is a "current" comprehensive comparative-table source. There isn't. Either the project builds it (own statute reading; LLM-assisted from filings) or it commits to commercial sources (State Capital Handbook subscription).

---

## Realistic next-step paths for actually getting Blue Book / BoS content

In rough order of cost/effort:

1. **Email Adam Newmark** (Appalachian State, `newmarka@appstate.edu`). He authored the 2005 + 2017 measures and presumably has copies or can recommend a librarian path. Bundles cleanly with the Task #10 outreach to him for Vaughan & Newmark 2008. **Highest expected value per unit effort.**
2. **ILL request for HathiTrust 1990 8th edition.** Public-domain, Google-digitized, university-library-accessible. Local university or public-library partnership should be able to deliver a PDF. **Most direct path to actual cell-level content for the 8th edition.**
3. **WorldCat / OCLC search for 1988-89 Special Edition** with ILL request. Less standardized cataloging than the numbered editions; may take more searches.
4. **Purchase used copies on eBay / AbeBooks.** Listings exist for the 1990 edition (ISBN 0872929566). Cheapest acquisition path if budget allows. Same for the 1993 edition.
5. **Contact COGEL directly.** `director@cogel.org` — may have institutional copies of older editions or PDF scans.
6. **Defer State Capital Handbook indefinitely** unless the project budget supports the subscription (~$200/yr). Alternative paths: West Academic / Thomson Reuters have institutional access; some law-school libraries subscribe; LexisNexis/Westlaw may carry portions.

**Specifically de-prioritized this session per user instruction:** Book of the States 2005 vintage. The lobbying-regulation chapter content that Newmark coded is already in `items_Newmark2005.tsv` at the row-label level; the only gap is operational thresholds, which can be cross-referenced against newer FOCAL / IBAC / Opheim items where overlapping.

---

## Files referenced / produced this session

- `papers/text/Strickland_2014__lobbying_laws_interest_groups.txt` — re-read for methodology section (lines L415–422, L920–927)
- `docs/active/compendium-source-extracts/results/items_Strickland.md` — full extract notes
- `docs/active/compendium-source-extracts/results/items_Opheim.md`, `items_Newmark2005.md`, `items_Newmark2017.md` — re-read to verify what's already extracted vs what BlueBook/BoS would add
- This document

## Methodology notes

The headline structural finding (CSG Blue Book = COGEL Blue Book) is established by joint-publication metadata in WorldCat, Stanford SearchWorks, and the HathiTrust catalog record. The 1990 8th edition's Lobby Laws TOC is established from search-engine snippets of the HathiTrust catalog page; cell-level content was not retrieved due to the egress proxy returning 403 on `babel.hathitrust.org`. The 2024 Ethics Update was successfully fetched as a format-comparator. The Phase 1 → Phase 2 split is established from result #78 in the search log (Herrmann bibliography, 2006), which catalogs Gross's 2005 Lobbying Update as part of the post-1997 Update series. The State Capital Handbook's commercial-only status is established from Amazon, eBay, FCM Law publication listings, and Cornell Law Review citations (Vincent Johnson 2006, footnote text).

No PRI 2010 text was read this session. No v1 compendium files were touched.

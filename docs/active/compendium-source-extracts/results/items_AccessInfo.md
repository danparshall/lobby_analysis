# items_AccessInfo — Access Info Europe / Open Knowledge / Sunlight Foundation / Transparency International (2015)

Companion to `items_AccessInfo.tsv`. Captures the actual evaluation items extracted from the document, organising structure, and judgment calls.

## 1. Paper

**Citation.** Access Info Europe, Open Knowledge, Sunlight Foundation, and Transparency International. *International Standards for Lobbying Regulation: Towards greater transparency, integrity and participation.* 2015. Hashtag `#lobbyingtransparency`. Project URL: `lobbyingtransparency.net`. Funded with support from the European Commission's Prevention of and Fight Against Crime Programme (DG Home Affairs).

**Framing.** This is a **jointly authored international-NGO coalition framework** — not a scorecard or empirical study. The four co-authoring organisations (TI, Access Info Europe, Sunlight Foundation, Open Knowledge) explicitly position the work as the product of "two years of collaborative work with civil society" and pitch it at policy-makers, governments, and international organisations contemplating lobbying legislation, as well as civil society organisations campaigning at the national level (lines 37-46). The document positions itself as going *beyond* what existing regulations and prior soft-law standards (OECD, etc.) cover, addressing transparency, integrity, and participation as inter-related areas (lines 54-58).

**Important disambiguation.** This document is *distinct* from the 2015 Sunlight Foundation US-state lobbying-disclosure scorecard (`items_Sunlight.tsv`), even though Sunlight Foundation is one of four co-authors here. The state scorecard is an empirical 50-state ranking; this is an international normative-standards document.

## 2. Methodology

The document is brief on methodology. What it states (lines 37-46, 54-66):

- The standards are the result of "two years of collaborative work with civil society," led by TI, Access Info Europe, Sunlight Foundation, and Open Knowledge.
- They "build on best practice from existing lobby regulations" and "reference various existing international standards."
- Stated aim: be "internationally applicable" while respecting national differences.
- Coverage breadth claim: at least 20 countries had national lobbying regulation as of May 2015 (footnote 1: Australia, Austria, Brazil, Canada, Chile, France, Georgia, Germany, Hungary, Ireland, Israel, Lithuania, Macedonia, Montenegro, Peru, Poland, Slovenia, Taiwan, UK, US).
- The standards are framed as "under ongoing review" — explicitly a living document (line 79).

**What the document does *not* state.** No description of scoring methodology, weighting, or how each item is verified against any actual jurisdiction. There is no rubric — these are normative *standards* (what regulation *should* contain), not measurement criteria with tier definitions. As such, none of the items have a built-in scoring scale; the "scoring_rule" column in the TSV records the implied evaluation logic (presence/absence, threshold values where given, etc.), not anything codified by the document.

## 3. Organising structure

Verbatim section headers from the document, each followed by the count of items in that section:

| Section (verbatim) | Top-level standards | Granular sub-points | Total |
|---|---|---|---|
| GUIDING PRINCIPLES | 0 (3 unnumbered prose statements) | 0 | 3 |
| REGULATORY SCOPE (Definitions; Exceptions) | 6 | 0 | 6 |
| TRANSPARENCY (Lobbying Register; Public Access to Information) | 10 | 11 (under standard `transp.3`) | 21 |
| INTEGRITY (Public Officials; Lobbyists) | 6 | 7 (under standard `integ.1`) | 13 |
| PARTICIPATION & ACCESS (Public Participation; Expert/Advisory Groups; Lobbyist incentives) | 9 | 0 | 9 |
| OVERSIGHT, MANAGEMENT AND SANCTIONS | 4 | 7 (under standard `overs.1`) | 11 |
| REGULATORY FRAMEWORK DESIGN | 3 | 9 (under standard `rfd.2`) | 12 |
| **Totals** | **38** | **34** | **72 (+ 3 principles = 75)** |

**Vs FOCAL's claim of "7 categories, 72 items including 34 granular points":**

- **7 categories**: matches exactly. Confirmed by the table of contents (lines 18-32) and the seven major section headers in the body. The document's introduction also explicitly says "transparency, integrity and participation" are the three "critical and inter-related areas" (line 56-57), but those are the conceptual themes, not the categorical headings; the seven categories are the structural top level.
- **72 items**: matches exactly when one counts the 38 numbered top-level standards plus the 34 lettered sub-points, and **excludes** the 3 unnumbered guiding-principle statements (which read as preamble prose, not as scored items).
- **34 granular points**: matches exactly. 11 (transparency 3.a–k) + 7 (integrity 1.a–g) + 7 (oversight 1.a–g) + 9 (regulatory 2.a–i) = 34.

The document itself states "The 38 standards set out here..." (line 54), confirming 38 as the canonical count of top-level standards. FOCAL's 72 is therefore reconciled as 38 standards + 34 granular sub-points.

## 4. Indicator count and atomization decisions

**Top-level vs granular layers — both captured.** The document has a clear two-layer structure:

- **Layer 1 — Top-level standards:** 38 numbered items, indicator-IDs in `<category>.<n>` style (e.g., `scope.1`, `transp.3`, `integ.1`). Each is a self-contained normative claim.
- **Layer 2 — Granular sub-points:** 34 lettered items, indicator-IDs in `<category>.<parent>.<letter>` style (e.g., `transp.3.a`, `integ.1.b`). These appear *only* under four "umbrella" standards: `transp.3` (Information disclosed), `integ.1` (Codes of Conduct), `overs.1` (Management & Investigation), `rfd.2` (Broader regulatory framework). Sub-points are introduced with phrases like "shall include information on:" or "should include:" — they enumerate what the umbrella standard requires.

I captured both layers with separate rows so a downstream consumer can use either granularity. The umbrella row carries `indicator_type = standard (umbrella)` and a "Composite — see sub-points" scoring rule; the sub-points carry `indicator_type = granular sub-point`.

**Guiding principles — captured but flagged.** The 3 statements under GUIDING PRINCIPLES are not numbered in the document, do not read as enforceable standards, and are not part of FOCAL's 72-item count. I included them as `indicator_type = principle` with IDs `gp.1–gp.3` so they are recoverable, but they should be excluded from any per-paper item count meant to match the document's "38 standards" or FOCAL's "72."

**Indicator-type breakdown.** Of the 38 top-level standards: 4 definitions (`scope.1–4`), 2 exceptions (`scope.5–6`), 4 umbrella composites (`transp.3`, `integ.1`, `overs.1`, `rfd.2`), 1 cautionary (`part.9`), and 27 standard normative claims.

**Judgment calls.**

- **Section path in `section_or_category`.** The document has nested headings (e.g., TRANSPARENCY > Lobbying Register > Information disclosed). I preserved the full path so a downstream consumer can roll up at any level. The top-level category match is the leftmost component before the `>`.
- **Numbering restarts within each category.** The document numbers items 1, 2, 3 within each section, restarting at 1 in the next section. To produce globally unique indicator IDs, I prefixed each ID with a category short code (`scope`, `transp`, `integ`, `part`, `overs`, `rfd`).
- **`scope.6` (public officials/diplomats/political parties exception)** is permissive ("if deemed necessary, the regulation *may* exclude…") rather than mandatory. Recorded as `standard (exception)` with notes acknowledging the permissive nature.
- **`part.9` (Lobbyist incentives)** is a single short cautionary sentence, not a positive standard. Type recorded as `standard (cautionary)`.

## 5. Frameworks cited or reviewed

Names only, drawn from footnotes 2 and 3 (lines 88-99):

- **U4 Anti-Corruption Resource Centre** — 2014 lobbying training course; Nauro F. Campos, *In pursuit of policy influence* (U4 Brief 2009:1).
- **Transparency International** — *Lobbying in Europe – Hidden Influence, Privileged Access* (2015).
- **Sunlight Foundation** — *International Lobbying Disclosure Guidelines* (2014).
- **Access Info Europe** — *Lobbying Transparency via Right to Information Laws* (2013).
- **OECD** — *Lobbyists, Government and Public Trust*, Vol. 1 *Increasing Transparency through Legislation* (2009), Vol. 2 *Promoting Integrity through Self-regulation* (2012), Vol. 3 *Implementing the OECD Principles for Transparency and Integrity in Lobbying* (2014).

The document also references `opendefinition.org` as the open-data definition (in standard `transp.4`), but that is a normative reference rather than a framework cited.

## 6. Data sources

**N/A.** This is a normative standards document, not an empirical study. It does not collect or analyse any data; it issues recommendations to policymakers. The closest the document comes to data is the brief footnote-1 enumeration of 20 countries with national lobbying regulation as of May 2015, used only to justify the document's scope.

## 7. Notable quirks / open questions

- **Jurisdictional applicability is intentionally broad but unspecified.** The introduction states the standards are "internationally applicable… but with an awareness and respect for national differences" (lines 58-59), and the final section (REGULATORY FRAMEWORK DESIGN) explicitly defers detail to "the local context" (line 421). The document does not specify whether standards apply only to national-level regulation or also to sub-national; the definition of "Public Official" (`scope.2`) explicitly covers "national, sub-national, or supra-national levels," which suggests sub-national was contemplated, though the document does not address how a US-state-level scorecard would map onto these standards.
- **The 2022 update — NOT mentioned in this document.** The 2015 PDF makes no reference to a 2022 successor or update. FOCAL's reference 1 (described in the task as the 2022 update) is therefore an external development, not a self-reference. The 2015 document closes with a hashtag (`#lobbyingtransparency`) and URL (`lobbyingtransparency.net`) and explicitly states the standards are "under ongoing review" (line 79), which leaves room for the 2022 update without anticipating its content.
- **No scoring rubric.** Unlike the Sunlight 2015 state scorecard or the FOCAL evaluation framework, this document does not provide tier definitions or a rubric. The `scoring_rule` column captures the *implied* evaluation logic (presence/absence in legislation; threshold values where given, e.g., "≥2 years" for cooling-off periods or "minimum quarterly" for reporting frequency), but any consumer using these as scored indicators would need to construct a rubric externally.
- **Two thresholds are specified numerically and are worth flagging for cross-paper comparison:**
  - `transp.2`: activity reporting frequency "minimum quarterly, ideally close to real-time."
  - `integ.2`: post-employment cooling-off period "at least 2 years."
- **Composite umbrellas behave as set-membership tests.** The four umbrella standards (`transp.3`, `integ.1`, `overs.1`, `rfd.2`) are written so that the umbrella requirement is satisfied iff the regulation includes (or substantively addresses) each enumerated sub-point. A downstream evaluator could either (a) score the umbrella as a single binary item, (b) score each sub-point separately and aggregate, or (c) require all sub-points present for the umbrella to count — the document does not specify.
- **Co-author Sunlight Foundation also published a separate 2015 US-state scorecard** in the same year. The two documents serve different purposes: the international standards document defines what *should* be regulated; the Sunlight scorecard measures what US states *do* regulate. They are non-redundant and should be kept distinct in any framework dedup.

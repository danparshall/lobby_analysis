# Bednářová 2020 — Evaluation of the Czech Draft Lobbying Act

Companion narrative to `items_Bednarova.tsv`. Source text: `papers/text/Bednarova_2020__lobbying_regulation_quality.txt` (929 lines). PDF: `papers/Bednarova_2020__lobbying_regulation_quality.pdf`.

## 1. Paper

**Citation.** Bednářová, P. (2020). The Evaluation of the Government Draft Lobbying Act in the Czech Republic Beyond the Framework of RIA. *E&M Economics and Management*, 23(2), 33–47. https://doi.org/10.15240/tul/001/2020-2-003

**Framing.** A draft Lobbying Act was approved by the Czech government on 30 July 2019. The Final Report on Regulatory Impact Assessment (RIA) attached to the draft was largely qualitative; Bednářová sets out to "complement the assessment included in the Final Report on Regulatory Impact Assessment with a quantitative cost-benefit analysis" (lines 64–68). The vehicle for this complement is what she calls the **Ninefold theory**: a 3 × 3 grid that crosses CPI strictness/strength tiers (low / medium / high) with CII cost-burden tiers (low / medium / high). The paper applies the framework ex post to five comparison countries (Austria, Hungary, Poland, Slovakia, Slovenia) and ex ante to the Czech draft. The overall framing is normative: regulation is "good" when CPI > CII (benefits exceed costs), "acceptable" when CPI and CII land in the same tier, "unacceptable" when CPI < CII (lines 340–354).

> "The CPI Index together with the CII Index (the Ninefold theory) provides comprehensive and robust assessment of specific regulatory models, but also improves comparative assessment of lobbying regulations in different jurisdictions of selected countries." (lines 20–23)

## 2. Methodology

Bednářová merges two pre-existing instruments rather than designing a new one:

- **Hired Guns / CPI** (Center for Public Integrity, 2011) — 48 questions, 8 categories, max 100 points. Strictness/strength tiers: 1–29 low, 30–59 medium, 60–100 high (Chari, Murphy & Hogan 2011 "Threefold theory"). Lines 211–223, 238–243.
- **Cost Indicator Index (CII)** (Krsmanovic, 2014) — 47 questions, max raw 288 points, rescaled to 0–100 by dividing by 2.88. Burden tiers: 1–29 low, 30–69 medium, 70–100 high (lines 277–278, 300–318). Items 1–26 measure private-sector burden; items 27–47 measure public-sector burden (lines 281–282, 299).
- **Ninefold theory** — the 3×3 join of the two Threefold typologies (lines 326–339).

Bednářová does **not** introduce new questions. The CPI items in her Tab. 1 are reproduced from CPI (2011) — Table 1's caption explicitly says "for a complete CPI methodology see CPI, 2011" (line 471). The CII items in Tab. 2 are reproduced from Krsmanovic (2014) — Table 2's caption says "for complete methodology CII see Krsmanovic, 2014" (lines 593–594).

**Jurisdictions covered.** Six total: Czech Republic (current state + draft act), Austria, Hungary, Poland, Slovakia, Slovenia. The five-comparison-country set is announced in the abstract (line 27) and at lines 312–315. Confirmed against FOCAL's claim of "Czech Republic + Austria + Poland + Slovenia + Hungary + Slovakia."

**Year of data.** "The relevant information for the author's own calculations was received from their national legislation for 2018" (lines 729–731). The Czech draft was assessed from the 30 July 2019 government version (line 13). Comparison-country scores are "ex post evaluation of their current laws or rules of lobbying regulation" (lines 318–321).

> "To evaluate a regulatory system from the viewpoint of strength which it has, and the transparency rate which it generates, the specialized Hired Guns methodology (CPI Index) is used. Costs which are needed to achieve, maintain and control a lobbying regulatory system are quantified by means of a methodology by Krsmanovic (CII Index)." (lines 311–316)

## 3. Organizing structure

Bednářová uses **the same 8 categories on both the HG/CPI side and the CII side** — they are inherited unchanged from CPI's Hired Guns scheme:

1. Definition of a lobbyist
2. Individual registration
3. Individual spending disclosure
4. Employer spending disclosure
5. Electronic filling *(sic — "filing"; the typo "filling" is verbatim throughout the paper)*
6. Public access
7. Enforcement
8. Revolving door provision

> "the division of 48 questions in total into eight key areas: definition of lobbyists, individual registration, individual spending disclosure, employer spending disclosure, electronic filling, public access, enforcement and revolving door provision" (lines 215–219)

These 8 categories appear as section headers in **both** Tab. 1 (HG/CPI) and Tab. 2 (CII), confirming that Bednářová does not separate "HG-categories" from "CII-categories" — both indexes share the same categorical scaffolding. FOCAL's "8 categories" claim is verified.

**Caveat in the source typesetting.** In Tab. 2, item #38 ("In addition to legislative lobbyists, does the definition recognize executive branch lobbyists?") appears under the *Public access* section header rather than *Definition of a lobbyist*. The question is structurally a definition question (it mirrors HG.1), and the placement looks like a typesetting artifact (the category-header row before #38 is missing). Flagged in the TSV notes for cii.38; do not propagate the apparent miscategorization downstream without verifying against Krsmanovic (2014).

## 4. Indicator count and atomization decisions

**Verified counts.**

- HG/CPI: paper says **48** questions total (line 215). Tab. 1 shows **17** non-zero rows for the CZ draft (HG.1, 2, 3, 4, 5, 7, 9, 25, 28, 30, 31, 34, 38, 39, 40, 41, 44). FOCAL's "17 from Hired Guns" matches the visible-in-Tab.1 count, *not* the full HG inventory.
- CII: paper says **47** questions total (lines 277–278). Tab. 2 shows **19** non-zero rows for the CZ draft (CII.1, 2, 3, 4, 5, 6, 8, 24, 27, 29, 30, 33, 37, 38, 40, 41, 42, 44, 46). FOCAL's "19 from a CII" matches the visible-in-Tab.2 count.
- 17 + 19 = **36** items as displayed → matches FOCAL's claim of 36 items. FOCAL is counting *displayed-in-the-paper* items, not the full HG+CII inventory (which would be 48 + 47 = 95).

**Important distinction for cross-walking.** Bednářová did **not** drop any of CPI's 48 questions methodologically. Both tables explicitly state that zero-scored answers are omitted from display only (lines 467–471: "In Tab. 1, only the questions where answers with a non-zero score were detected are included. Questions where there were zero-score answers are not included"; lines 588–595: "Specific questions which are connected with a non-zero assessment of an answer are included in Tab. 2 (questions with a zero assessment of the answer are not included)"). The full 48-question HG inventory and 47-question CII inventory remain in force — the paper just reports the subset that produced points for the Czech draft.

**Implication for the compendium dedup.** The 36 visible items in Tab. 1 and Tab. 2 together represent the union of HG + CII questions where the Czech draft Lobbying Act has *any* substantive provision. Items HG.6, HG.8, HG.10–24 (other than 25), HG.26–27, HG.29, HG.32–33, HG.35–37, HG.42–43, HG.45–48 are silent on the Czech draft (not absent from the methodology). Same logic on the CII side for items 7, 9–23, 25–26, 28, 31–32, 34–36, 39, 43, 45, 47.

**Atomization decisions in TSV.**

- HG-side rows use Bednářová's published item numbers (`hg.1`, `hg.2`, …, `hg.44`) with gaps preserved. Same on the CII side (`cii.1`, …, `cii.46`). Gaps in numbering signal "Bednářová did not list this row because score was zero."
- Two composite rows (`score.cpi.total`, `score.cii.total`) capture the index totals and threefold classifications, separately from individual items.
- Each row's `notes` field flags whether it is HG-derived or CII-derived per the FOCAL request.
- Question wording matches Bednářová's tables verbatim, including small Czech-translation quirks ("Electronic filling", "Does oversight agency conducts mandatory reviews"). Where wording diverges between her HG and CII tables (e.g. "the state" vs "oversight agency"), the variants are preserved separately rather than harmonized.

**Modifications vs. CPI 2011 / Krsmanovic 2014?** None visible at the question-content level — Bednářová cites both source methodologies for full text and presents only items the Czech draft scored on. The TSV does not assume these are byte-identical to CPI 2007's Hired Guns or Krsmanovic 2014; downstream cross-walking should diff against those primary sources, not against this extract.

## 5. Frameworks cited or reviewed

- **Opheim's Index** (Opheim, 1991) — first US lobbying-strictness index.
- **Brinig et al. Index** (Brinig, Holcombe & Schwartzstein, 1993) — restrictiveness focus.
- **Newmark Index** (Newmark, 2005) — strictness-over-time.
- **CPI Hired Guns** (Center for Public Integrity, 2011) — Bednářová's chosen benefits instrument; built on Opheim + Brinig.
- **Threefold theory** (Chari, Murphy & Hogan, 2011) — CPI tiering.
- **Transparency International's 2015 Lobbying in Europe report** — 19 national reports; reference for the European context.
- **Mulcahy 2015 / TI 2015** — same Lobbying in Europe report (separate citation).
- **Krsmanovic CII** (Krsmanovic, 2014) — Bednářová's chosen costs instrument.
- **OECD 10 Principles for Transparency and Integrity in Lobbying** (OECD, 2013).
- **Council of Europe / Venice Commission report** (Council of Europe, 2013).
- **Open Governance Scorecard Standards** (Transparency International, 2013b).
- **Sunlight Foundation Open Data Policy Guidelines** (Sunlight Foundation, 2013).
- **Access Info Europe Standards: Lobbying Transparency via Right to Information Laws** (Access Info Europe, 2013).
- **Laboutková & Vymětal (2018)** "innovative catalogue of lobbying transparency" — four categories: lobbyists, targets of lobbying, sunshine principles, monitoring and sanctioning (lines 129–135). Distinct from the 8-category CPI/CII scheme actually applied in this paper.
- **EPRS (2016)** "Transparency of lobbying in Member States Comparative analysis" — primary source for comparison-country statute information.

## 6. Data sources

- **Czech Republic, current state.** Determined to be CPI = 0 / CII = 0 by inspection (no statutory regulation; "the costs and benefits of the zero option can be quantified only with difficulty and only by means of expert estimation" — lines 396–401).
- **Czech Republic, draft Lobbying Act.** Government Office of the Czech Republic, *Vládní návrh Zákona o lobbování*, retrieved 15 August 2019 from `https://apps.odok.cz/veklep-detail?pid=KORNB4B9CNQE`. Section references (e.g. §6(2), §12(2-d), §16(5–7)) are cited directly in Tab. 1 cells.
- **Comparison countries (Austria, Hungary, Poland, Slovakia, Slovenia).** "The relevant information for the author's own calculations was received from their national legislation for 2018" (lines 729–731). EPRS (2016) "Transparency of lobbying in Member States Comparative analysis" is cited repeatedly in the country prose (lines 745–748, 763–765, 776–777). For Slovakia, the cited authority is "The Government decree on the system of integrity management within public administration issued in 2013" (lines 750–751); for Slovenia, the **Integrity and Prevention of Corruption Act** (line 763); for Poland, **Act on Legislative and Regulatory Lobbying** of July 2005, in force March 2006, amended 2011 (lines 770–777); for Austria, **"Transparenzpaket"** (Transparency package) of June 2012, including **"LobbyG"**, in force January 2013 (lines 716–718, 736–739); for Hungary, **Act CXXXI of 2010 on Public Participation in Developing Legislation** (line 746).
- **Country-level scores reported.** Hungary CPI=0/CII=0; Slovakia 6/10; Poland 31/34; Slovenia 41/44; Austria 38/49; CZ current 0/0; CZ draft 34/35. (Fig. 2, lines 698–714.)

## 7. Notable quirks / open questions

- **"Hired Guns" misspelled twice in the paper** as "Hirend Gunds" (line 463). Verbatim quote retained where used.
- **"Electronic filling" not "filing"** — Czech-English typo; appears repeatedly. TSV uses Bednářová's actual section text.
- **Tab. 2 cii.38 placement.** Item 38 (executive branch lobbyists) appears under "Public access" heading in Tab. 2; almost certainly a typesetting artifact (no category-header row precedes it). Flagged in cii.38 notes; recommend confirming the canonical category against Krsmanovic (2014) before using.
- **HG.4 / Tab. 1 inconsistency.** Tab. 1 shows the CZ draft scoring 4 ("0 days") for "How many days can lobbying take place before registration is required?" (line 504). The narrative at lines 568–572 explicitly says "lobbyists will be obliged to fill in a registration form within ten days after they have commenced their activities at the latest." Ten days corresponds to a score of 2, not 4. Either Tab. 1 is wrong or §6(2) of the draft uses different language than the narrative suggests. Flagged.
- **HG.31 / Tab. 1 inconsistency.** Tab. 1 scores location/format = 2 (PDF on Web), but narrative at line 585 says "Downloadable files are a public access option in the draft act" (which would be 4). Possibly Bednářová is distinguishing what is *required* by statute vs. what is *available* as an option. Flagged.
- **Tier ladders for CII.3 and CII.6 contain duplicates.** Both list "Up to a month – 5 points; Up to 3 days – 5 points" (lines 611–613, 634–636). This appears to be a transcription quirk of Krsmanovic's original; Bednářová reproduces it as published.
- **CII total displayed is "100/2,88 / 35"** in Tab. 2 (line 680). This is the rescaling artifact: raw sum = 100 (out of 288), divided by 2.88 ≈ 34.72, rounded to 35. The TSV captures this in `score.cii.total`.
- **Newmark Index** is described in Section 1.1 as "the most frequently used tool for the evaluation of lobbying regulation at present" (lines 211–215), yet the paper does not apply it. Bednářová's reasoning: the CPI is the "most often used on a global scale for evaluating and comparing the lobbying regulation" (lines 241–243) — i.e., the CPI is preferred for cross-jurisdiction comparability.
- **Czech-language term variants.** Czech sources cited verbatim include "Vládní koncepce boje s korupcí na léta 2018 až 2022" (line 877), "Vládní návrh Zákona o lobbování" (line 880), "Lobbování v Evropské unii a v České republice" (line 886), and "Transparentní lobbing přesahuje účinnost jediného zákona" (line 891). For most CPI/CII content the question text is Bednářová's English translation; original Czech wording is not provided in the paper.
- **No revolving-door scoring for any country except partial Slovakia.** The Revolving door provision section never appears in either Tab. 1 or Tab. 2, consistent with the Czech draft being silent on revolving door (line 593: "The draft act in the Czech Republic does not address revolving door provisions either").
- **CPI vs CII numbering offset.** CPI/HG has 48 items; CII has 47. Inspection of the question lists shows CII drops one item somewhere in the 1–25 range (likely a definition item) — e.g. CII.24 "no spending → report of no activity" corresponds to HG.25. This complicates one-to-one cross-walking by question number alone.

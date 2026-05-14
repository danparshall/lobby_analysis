# McKay & Wozniak (2020) — extraction notes

`paper_id`: `mckay_wozniak_2020`

## 1. Paper

McKay, Amy Melissa, and Antal Wozniak. 2020. "Opaque: an empirical evaluation of lobbying transparency in the UK." *Interest Groups & Advocacy* 9(1): 102–118. doi:10.1057/s41309-019-00074-9. (Open Access — Liverpool repository green OA copy.)

> "The government of the UK is reputed to be among the world's most transparent governments. Yet in comparison with many other countries, its 5-year-old register of lobbyists provides little information about the lobbying activity directed at the British state. Further, its published lists of meetings with government ministers are vague, delayed, and scattered across numerous online locations. Our analysis of more than 72,000 reported ministerial meetings and nearly 1000 lobbying clients and consultants reveals major discrepancies between these two sources of information about lobbying in the UK." (Abstract, lines 19–26)

This is **not** a rubric-construction paper. The framing is empirical-evaluative: an audit of UK lobbying transparency that (a) re-applies the CPI Hired Guns index to the UK with two corrections, and (b) borrows Piotrowski & Liao's (2012) usability criteria — augmented by Holman & Luneburg's (2012) searchability — to evaluate UK ministerial meetings data. The headline contribution is the empirical comparison of two UK datasets (the consultant-lobbyist register and ministerial-meetings disclosures) showing that they barely overlap.

The paper title (the journal version actually reads "an empirical *evaluation*"; the assignment description used "investigation," but the on-page title is "an empirical evaluation of lobbying transparency in the UK"; lines 8 and 108) telegraphs the genre — evaluation against pre-existing criteria, not construction of new criteria.

## 2. Methodology

**Genre.** Mixed-methods empirical evaluation: descriptive statistics on two large compiled datasets, plus qualitative analysis of (i) the legislative consultation record and (ii) the disclosure infrastructure.

**Data sources.**
- **The lobby register**: UK Office of the Registrar of Consultant Lobbyists. Authors examine 918 clients and 116 consultant lobbying firms registered in 2015–2016 (line 533).
- **Ministerial meetings disclosures**: 1045 files from 23 UK Government departments (including the Offices of the Leaders of the House of Commons and House of Lords) covering Q1 2011 – Q4 2015. The compiled dataset has 72,756 recorded contacts between a ministerial-department senior official and an external organisation or individual. The authors note this is "the greatest number of meetings between government officials and outside interests that has ever been included in a single data set" (lines 442–447, 471).
- **Cabinet Office consultation submissions** (2012): 259 stakeholder responses to "Introducing a Statutory Register of Lobbyists." Authors rely on Crepaz (2017a)'s tally that 85% wanted stricter rules (lines 267–272).
- **House of Commons floor debate**: cited directly with Hansard-style speaker/date attributions (e.g., Tom Brake 22 Jan 2014, Michael Meacher 3 Sep 2013, Jon Trickett 9 Sep 2013, Graham Allen 9 Sep 2013).
- **Ministerial Code (2010)** as the legal basis for ministerial-meetings disclosure (lines 292–295).

**Data-cleaning method (transparent and reproducible).** A second dataset was created with semantic duplicates removed; acronyms checked via Google search; Fuzzy Lookup add-on for MS Excel used at threshold 0.90 to standardise organisation names; manual review caught e.g. Anglican Church → Church of England, GSIC Limited → Government of Singapore Investment Corporation, Harrow Council → Harrow London Borough Council (lines 473–490).

**Evaluation criteria (the "rubrics" the paper applies, not constructs).**
- **CPI Hired Guns index** (Center for Public Integrity 2003) — applied at the level of two specific items the authors revise from Keeling et al. (2017)'s UK scoring. They do *not* re-score the full 48-item Hired Guns instrument; they correct two items and report the resulting total.
- **Piotrowski & Liao (2012) usability criteria** — six dimensions: accuracy, accessibility, completeness, understandability, timeliness, free or low cost.
- **Holman & Luneburg (2012)** — adds searchability as a seventh criterion.
- The above are applied narratively (no per-item numerical scoring); each criterion gets one to two paragraphs of qualitative assessment.

## 3. Organizing structure

The paper presents three distinct organizing structures, none of them a numbered rubric of their own:

(a) **Five "aspects" thesis** (Introduction, lines 69–82). Five numbered claims that "together suggest that the Government purposely chose to keep lobbying in the UK in the dark" — covers regulatory weakness, register/meetings mismatch, collation burden, evidence from the legislative debate, and skewed access distribution.

(b) **Seven usability criteria** (Difficult-to-use data section, lines 332–434). Six borrowed from Piotrowski & Liao (2012) plus one from Holman & Luneburg (2012). Each gets a labelled paragraph; UK is then placed in Piotrowski & Liao's "overload" quadrant (line 432).

(c) **Four conclusion-level critiques** (Conclusions section, lines 695–720). The conclusion narrows the five-aspect thesis into four: register misses majority of lobbying; meetings data unusable; little overlap between datasets; skewed distribution of meetings. Aspect 4 (legislative-debate evidence) gets folded into the discussion section rather than into a discrete conclusion-level critique.

The paper also presents one full ranked **Top-25 table (Table 1)** of external groups that met most frequently with UK ministerial departments in 2011–2015 (Confederation of British Industry at #1 with 608 meetings; BAE Systems #2 with 384; etc.). This is descriptive evidence, not a rubric — captured as supporting empirical content, not as TSV items.

## 4. Indicator count and atomization decisions

**Total items in the TSV: 18.**

Composition:
- **5** thesis-level aspects (`thesis.aspect_1` – `thesis.aspect_5`) — the introduction's five-bullet roadmap. These are the closest analog the paper has to "criteria the authors are evaluating against."
- **7** usability criteria (`usability.accuracy`, `usability.accessibility`, `usability.completeness`, `usability.understandability`, `usability.timeliness`, `usability.free_or_low_cost`, `usability.searchability`) — adopted from Piotrowski & Liao (2012) + Holman & Luneburg (2012). Captured even though not original to this paper, because the paper *applies* this 7-criterion framework as its evaluative instrument and gives a UK assessment per criterion.
- **2** explicit CPI-rubric corrections (`cpi.correction.threshold_for_registration`, `cpi.correction.individual_lobbyists`). These are the only two specific items where the authors do per-item statute-coding work; together they reduce the UK from 33 to 26 and reclassify the regime from medium- to low-robust. Captured because they are the only places the paper does any numerical scoring of its own.
- **4** conclusion-level critiques (`conclusion.critique_1` – `conclusion.critique_4`). Captured even though they substantively re-state the thesis aspects, because they appear as a numbered list in the conclusion and an extracting downstream user might find either form useful.

Every TSV item is `indicator_type=open` *except* the two `cpi.correction.*` items, which are `categorical` (because they specify a CPI scoring rule the authors apply).

**What we deliberately did NOT atomize:**
- The Top-25 ministerial-meetings table is descriptive empirical evidence, not a criterion.
- The 91% "meetings without lobbyists" / 44% / 29% / 4% / 2% overlap statistics are findings, not items.
- The Cabinet Office consultation submission counts (80 trade associations / 34 civil-society orgs / 34 companies / 10 unions / 10 research orgs / 9 campaign groups / 78 individuals / 3 regulators / 1 MP) describe stakeholder composition; not criteria.
- We did not re-derive a full CPI Hired Guns scorecard for the UK from this paper — only the two items the authors explicitly correct are captured.

## 5. Frameworks cited or reviewed

Names only — relevant predecessor lobbying-rubric or transparency-criterion sources cited in the paper:

- **Center for Public Integrity (CPI) — Hired Guns index** (2003). The headline rubric the paper re-applies. Authors describe its eight components (line 124–130) and note it gives the U.S. 62/100 (line 140).
- **OECD principles on lobbying** (2014). Five elements: unambiguous definition; disclosure of funding sources; disclosure of lobbying targets; clear standards on revolving-door practice; appropriate monitoring and enforcement (lines 119–123).
- **Opheim (1991)** — cited as a US-state lobbying-regime rigour measure (line 129).
- **Newmark (2005)** — cited (a) for measuring state legislative lobbying regulation and (b) for a footnote on US-state regulation (lines 107, 129).
- **Holman & Luneburg (2012)** — provides the searchability criterion, also cited as a robustness measure correlating .65 with CPI per Chari et al. 2019 (lines 130–132, 336–338).
- **Chari, Hogan, Murphy & Crepaz (2019)** — *Regulating Lobbying: A Global Comparison*, 2nd ed. Cited heavily as the source of (a) the CPI medium/low-robust thresholds and (b) the cross-rubric correlation table (.80 / .62 / .65 with Opheim / Newmark / Holman-Luneburg respectively).
- **Keeling, Feeney & Hogan (2017)** — the prior CPI scoring of the UK (33 points) that this paper revises.
- **Piotrowski & Liao (2012)** — the source for six of the seven usability criteria, plus the four-quadrant transparency × usability typology that the authors place the UK in ("overload" quadrant).
- **Public Administration Select Committee (House of Commons) (2009)** — the report ("Lobbying: Access and Influence in Whitehall") setting out the more stringent regulatory recommendations the Government did not adopt (lines 241–247).
- **OECD (2009)** — earlier OECD recommendations to its 30 member nations.
- **Crepaz (2017a)** — PhD thesis tallying the 259 consultation responses.

The authors **explicitly endorse CPI as the highest content-validity option** among the alternatives (citing Chari et al. 2019), which is why their evaluation is "based primarily on those of the CPI" (lines 134–138).

## 6. Data sources

- **UK Office of the Registrar of Consultant Lobbyists** — the lobby register (consultant lobbyists only).
- **www.gov.uk "transparency data"** — the catch-all section under which each UK department posts its quarterly ministerial-meetings disclosures. Heterogeneous formats: 234 PDFs, 700 CSVs, 52 MS Excel worksheets, 23 MS Word documents, 6 Open Document spreadsheets, 24 Open Document texts, 6 RTFs (lines 322–325).
- **Hansard (UK Parliamentary record)** for floor debates on the Transparency of Lobbying Act 2014.
- **Ministerial Code** (the source of the 2010 disclosure obligation).
- **Cabinet Office consultation report (2012)** — text "A Summary of Responses to the Cabinet Office's Consultation Document 'Introducing a Statutory Register of Lobbyists.'"
- **Cabinet Office Impact Statement (2013)** — for the 85% in-house-lobbyist exclusion estimate.
- The defunct **whoslobbying.com** consolidator (Moving Flow Ltd; ceased Sep 2011) is named as historical context but not used as a data source (footnote 9, lines 355–358).
- No FOIA / FOI requests were used. No interviews were conducted. The work is done from public-record sources only.

## 7. Notable quirks / open questions

**UK-specific institutional features that complicate cross-walk to US-state schemes:**

- **Westminster system**. The 2014 Act's regulatory subject is *consultant* (third-party) lobbyists only. In-house lobbyists, campaigning organisations, trade associations and umbrella business groups (e.g., Confederation of British Industry, Federation of Small Businesses) are entirely outside the register — yet (per Table 1) these are the most active meeting-attenders. Cabinet Office's own 2013 Impact Statement estimated this "leave[s] 85% of lobbying unreported" (lines 230–231).
- **Quarterly lists of ministerial meetings as a parallel disclosure track**. UK transparency operates through *two* distinct, non-integrated disclosure regimes — the lobby register (since 2014) and the ministerial meetings logs (since 2010, under the Ministerial Code). The paper's central empirical contribution is showing that the two regimes produce nearly disjoint pictures of who is lobbying. Most US-state schemes have only one (the registration regime). Any cross-walk needs to decide whether US-state items mapping to "register" alone capture what UK observers consider "lobbying disclosure."
- **VAT-threshold quirk**. UK consultant lobby firms are exempt from registration if they have no VAT number, which under UK tax law requires annual revenue ≥ £85,000. McKay & Wozniak treat this as a *de facto* monetary threshold (lines 196–199) — it has no direct parallel in US-state schemes, which use direct dollar thresholds on lobbyist compensation or expenditure.
- **No revolving-door or gift-giving rules at all**. UK has neither cooling-off periods for ex-officials nor any restrictions on gifts to ministers (lines 188–190, 237). Items in any rubric covering these dimensions have to be coded as "not regulated" rather than "regulated weakly."
- **All-Party Parliamentary Groups (APPGs)** — *not addressed in this paper*. APPGs are a major UK lobbying access vector with their own (separate, weaker) disclosure regime via the Register of All-Party Parliamentary Groups maintained by the Parliamentary Commissioner for Standards. McKay & Wozniak's analysis is silent on APPGs. Open question for the compendium: whether to track APPG disclosure in a separate channel or fold into "register" items.
- **"Special Advisers" (SpAds) and senior civil servants**. These two groups are major lobbying targets but are not covered by either the consultant-lobbyist register *or* the ministerial-meetings disclosure. The exclusion is structural to both UK regimes (lines 232–235, 388–390). The Westminster political-civil service distinction has no clean US analog.
- **Fragmented disclosure infrastructure across departments**. No single web portal, no shared schema, no API; departments publish to gov.uk in idiosyncratic formats. McKay & Wozniak's Searchability assessment is essentially a rebuke of this fragmentation. Any compendium item like "single searchable database" would code UK at zero.
- **The article's own title contains a typographical mismatch**. The header of the article (line 8) reads "an empirical *evaluation* of lobbying transparency"; the running header (line 108) and journal metadata also use "evaluation." The task brief used "investigation"; the on-page title is "evaluation."
- **"Type I / Type II error" framing of Venn-diagram results**. The authors describe groups in the lobby register but not in ministerial meetings as "Type I error" and groups in meetings data not in the register as "Type II error" (lines 503–506). This is not a rubric item but a conceptual frame that downstream readers might want to flag — it carries the implicit normative claim that registration *should* track meetings, which is debatable (see "lobbyists may register clients as a matter of course" alternative explanation, lines 538–541).
- **Authors' alternative explanations for the 4% / 29% mismatch** (lines 538–550). Three non-rival hypotheses are offered: (1) lobbyists register clients routinely while meetings are sporadic; (2) registration confers professional benefit independent of activity; (3) lobbyists meet most often with SpAds and civil servants whose meetings are not disclosed. The authors do not adjudicate among these, which means the 4% figure is consistent with multiple worldviews about the register's failure mode.

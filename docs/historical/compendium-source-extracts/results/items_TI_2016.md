# TI 2016 — Open Data to Fight Corruption: Case Study, the EU and Lobbying

`paper_id = ti_2016`
Source text: `papers/text/TI_2016__open_data_eu_lobbying.txt` (529 lines).
PDF: `papers/TI_2016__open_data_eu_lobbying.pdf`.

## 1. Paper

**Citation.** Daniel Freund and Yannik Bendel (Transparency International EU), *Open Data to Fight Corruption — Case Study: The EU and Lobbying*, Transparency International, 2016. ISBN 978-3-943497-97-7. Information stated correct as of 21 December 2015. Reviewed by Savita Bailur (LSE), David McNair (ONE), Stefaan Verhulst (GovLab). (Lines 16–28.)

**Verified title note.** The user prompt described this paper as "Open Data and EU Lobbying: A Methodology to Evaluate Lobbying Disclosure." That is **not** its actual title. The cover and title page use "OPEN DATA TO FIGHT CORRUPTION — CASE STUDY: THE EU AND LOBBYING" (lines 1–4). The document is one of three TI case studies under the *Open Data to Fight Corruption* series.

**Framing.** The paper is **not** a stand-alone methodology paper. It is a **case study of the EU Integrity Watch project** (www.integritywatch.eu), which TI EU launched in October 2014 (line 163). It assesses the open-data quality of three lobbying-relevant EU datasets and uses that assessment to motivate the Integrity Watch tool, which scrapes and re-publishes the data in usable form.

The "open-data quality assessment" the FOCAL paper credits to TI 2016 is concentrated in two short tables (Table 1 "Data Availability" lines 238–298; Table 2 "Data Quality" lines 299–371) and the four-criterion lens stated at lines 67–71.

## 2. Methodology

**Construction of the framework.** Page 2 (lines 65–72) sets out four criteria the paper uses as the lens for "data … to fight corruption":

> "the data must be:
> - **accessible**: it must be free to use and reuse, published in a timely manner and easily found
> - **accurate**: it must be complete and reflective of reality
> - **intelligible**: it must be structured in a way that can be analysed (e.g. clear and consistent columns, values and formats)
> - **meaningful**: it must be useful for the user"

Footnote 4 (line 99) attributes these criteria explicitly to **Transparency International UK** ("Criteria developed by Transparency International UK"). The paper does **not** present them as new methodology — they are imported from a TI-UK rubric.

**Sample / scope.** The assessment covers **EU institutions only**, specifically:
- the European Commission (EC) and its senior officials;
- the European Parliament (EP) and its 751 MEPs;
- the EU Joint Transparency Register (jointly run by the EC and EP).

The paper notes that the Council of the European Union "and Parliament are noticeably absent and have contributed little to nothing to the common project" (lines 139–140), so the dataset assessment effectively excludes Council. The paper does **not** assess EU member states; the 19-country lobbying-policy comparison referenced in the introduction (lines 113–118) comes from a *separate* TI study cited at footnote 6 (*Lobbying in Europe: Hidden Influence, Privileged Access*, 2015).

**Three datasets assessed:**
1. MEPs' Declaration of Financial Interests (one PDF per MEP, 751 PDFs);
2. EU Joint Transparency Register (8,821 organisations registered as of writing — footnote 11);
3. Lobby meetings of EC senior officials (7,084 meetings declared as of 1 December 2015 — footnote 12).

**Rating method.** Table 2 rates each dataset on three dimensions (Level of Openness, Data Quality, Areas for Improvement) using a three-level rubric: **good / average / poor**. Footnote 14 (line 359) specifies the basis: "The assessment of data quality (good, average, poor) is based on individual chapters' determinations." This is a **subjective rating by TI national chapters**, not a numeric scoring scheme.

**Results of the rating** (Table 2):
| Dataset | Level of Openness | Data Quality |
| --- | --- | --- |
| MEP financial declarations | Poor | Average |
| EU Transparency Register | Good | Average |
| Lobby meetings (EC officials) | Poor | Average |

## 3. Organizing structure

The paper produces **no flat numbered checklist**. The closest things to enumerable items are:

| Category | Item count |
| --- | --- |
| Open-data criteria (the assessment lens, p. 2) | 4 |
| Table 1 "Data Availability" — fields disclosed in MEPs' declarations | 6 |
| Table 1 — fields disclosed in Transparency Register | 9 |
| Table 1 — fields disclosed in lobby-meeting records | 4 |
| Table 2 "Data Quality" — openness assessments (one per dataset) | 3 |
| Table 2 — data-quality assessments (one per dataset) | 3 |
| Table 2 — areas-for-improvement clusters (one per dataset) | 3 |
| Lessons-learned recommendations to the EU (p. 9) | 6 |
| **Total atomized indicators in the TSV** | **38** |

## 4. Indicator count and atomization decisions

I extracted **38 items** total. Atomization choices:

- **Open-data criteria (4 rows, `criterion.1`–`criterion.4`):** kept as one row per criterion, since the paper bullets them at the same level of granularity. They are the conceptual rubric of the paper, even though TI does not score against them numerically.
- **Table 1 fields (19 rows, `avail.{mep|tr|mtg}.N`):** atomized one row per bullet in the "Information" column of Table 1. Each row corresponds to a piece of information TI judged disclosed (or not) by the existing system.
- **Table 2 dimensions (9 rows, `qual.{mep|tr|mtg}.{openness|dataquality|improve}`):** rather than atomize every sub-bullet of every cell, I collapsed each dataset × dimension cell into a single row. The cell's text, rating, and sub-bullets are captured in `indicator_text` and `source_quote`. This preserves traceability without inflating the count: TI itself groups the sub-bullets, and they are not independent indicators in the paper's logic.
- **Lessons-learned recommendations (6 rows, `rec.eu.1`–`rec.eu.6`):** the paper presents these as a discrete bulleted list of forward-looking actions, distinct from the dataset assessments. Kept one row per bullet.
- **Excluded.** I did not extract: (a) the Integrity Watch impact statistics (4,250 complaints, €1.5M revenue decrease, 500+ articles, etc., lines 386–404); (b) the project-cost figures (€20,000 IT, €4,000 for Integrity Watch France); (c) the partner organisation lists in the Annex. None of these are evaluative criteria for lobbying disclosure.

The `paper_id` is `ti_2016` per the prompt. Indicator IDs are namespaced by section (`criterion.*`, `avail.*`, `qual.*`, `rec.*`) because TI does not number its own items.

## 5. Frameworks cited or reviewed

Names only, in order of appearance:
- **Open Knowledge Foundation, "Open Data Handbook"** — cited for the basic definition of open data (footnote 2, line 94). Used as a glossary, not as an evaluation framework.
- **G20 open-data principles** — referenced as motivating context (footnote 1, line 92), adopted at the November 2015 Turkish-presidency G20 meeting.
- **Open Data Charter** — named at line 57 as a multilateral attempt to "create a common foundation."
- **World Wide Web Foundation, "Open Data Barometer"** (January 2015) — cited for the "90% of 86 countries" statistic on missing budget/contracting data (footnote 3).
- **Transparency International UK** — cited as the source of the four-criterion rubric (accessible / accurate / intelligible / meaningful) used in this paper (footnote 4).
- **Transparency International, "Lobbying in Europe: Hidden Influence, Privileged Access"** (Berlin: TI, 2015) — cited for the 19-country / 65-indicator scoring of lobbying legislation (footnote 6, line 149). This is a sister TI study, *not* used as a methodology in this case study.
- **Transparency International, *Global Corruption Report: Education*** (Routledge, 2013) — cited for the Belgium/Greece/Italy/Spain/UK public-trust statistics (footnote 5).

The paper does **not** cite Sunlight Foundation Live Open Data Guidelines, Access Info Europe's *International Standards*, OECD Lobbying Principles, or any of the other lobbying-disclosure rubrics one might expect. It is consciously framed as an open-data case study, not a lobbying-policy benchmark.

## 6. Data sources

What TI examined to produce Tables 1–2:
- **MEPs' financial-interest declarations.** "Each of the 751 MEPs has his or her own declaration" (footnote 10, line 285), example URL `www.europarl.europa.eu/mepdif/4555_DFI_rev0_EN.pdf`. Format: scattered PDFs on individual MEP pages — TI flags this as a key openness failure.
- **EU Joint Transparency Register.** "There are currently 8,821 organisations registered; each organisation has its own declaration" (footnote 11, lines 287–288), example URL `http://ec.europa.eu/transparencyregister/public/consultation/displaylobbyist.do?id=501222919-71`. Hosted centrally and downloadable as XLS/HTML.
- **Lobby meetings of EC senior officials.** "As of 1 December 2015 there had been 7,084 meetings declared on 98 different web sites" (footnote 12, line 290). "Each has a dedicated website to register their meetings with lobbyists; there are a total of 98 dedicated websites" (footnote 13, line 293). The 98 sites = each Commissioner + each Cabinet + each Director-General running a separate disclosure page.

The "98 different websites" finding the FOCAL summary attributes to TI 2016 is **verified**, with two separate verbatim statements at lines 290 and 293.

The paper also references operational data sources used by Integrity Watch (not by the assessment itself): **ParlTrack** (data scraping platform, line 199), **LobbyFacts.eu** / Corporate Europe Observatory (shared back-end database, line 201), and the **EU Open Data Portal** launched December 2012 (line 129).

## 7. Notable quirks / open questions

**Quirk 1: This is a case study, not a methodology paper.** The "framework" the FOCAL paper credits is really a 4-bullet rubric imported from TI-UK plus a 3×3 good/average/poor table whose ratings are sourced to "individual chapters' determinations." Anyone treating TI 2016 as a *measurement methodology touchstone* should know that the paper itself does not claim to be one. The author bylines (Freund and Bendel, both TI EU) and the format (case study with project costs, partner lists, and impact statistics) make clear this is an advocacy/communications product describing the Integrity Watch project, with the data assessment subordinate to that narrative.

**Quirk 2: The 4 criteria are TI-UK's, not TI 2016's.** Footnote 4 is unambiguous. If the project's compendium is supposed to credit the originator, the criteria belong to TI-UK; TI 2016 is the *application* of the criteria to EU lobbying data. Whether to give them their own paper_id (e.g. `ti_uk_*`) is a downstream curation question — the original TI-UK source is not cited in the bibliography here.

**Quirk 3: The user's prompt asked about a 5-criteria Open Data checklist (Open Knowledge Foundation / Global Data Barometer). TI 2016 does not use that checklist.** The Open Knowledge Foundation is cited only for the basic glossary definition of open data (line 94, footnote 2). The Global Data Barometer is not cited at all. The widely-known "Open Definition" (open license, machine-readable, bulk download, free of charge, etc.) does not appear here. **TI 2016's framework is a 4-criterion rubric (accessible / accurate / intelligible / meaningful), not the 5-criterion Open Data Definition family.** Treating TI 2016 as the same framework as Global Data Barometer would be a category error.

**Quirk 4: Rating subjectivity.** Footnote 14 says good/average/poor ratings come from "individual chapters' determinations." The paper does not document which chapter rated which dataset, what evidence was reviewed, or what a "good" vs "average" threshold means. This limits the framework's reusability as a measurement tool: the rubric travels (the four criteria are reusable), but the *scoring procedure* is unreplicable.

**Quirk 5: Scope mismatch with FOCAL framing.** FOCAL describes TI 2016 as documenting "data openness for lobbyist meetings was poor, with only 'average' data quality (eg, information located across 98 different websites, not machine readable)." This is faithful to Table 2's lobby-meetings row. However, FOCAL's claim that this is a "methodological touchstone" overstates the paper's ambition — it is a four-criterion lens applied subjectively to three datasets in a case-study chapter, not a published methodology.

**Open question for downstream work.** Given (a) the 4 criteria are TI-UK's, and (b) the rating procedure is unspecified, should this paper be retained as a *framework_reference* in the compendium, or treated only as evidence that TI EU evaluated three specific datasets and rated them poor/poor/poor on openness (MEP, lobby meetings) and good (Transparency Register)? The TSV captures both readings, but a curator may want to demote the criterion rows to a separate TI-UK entry.

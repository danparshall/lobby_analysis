# GDB 2022 — Lobbying-Transparency Module Extract

`paper_id = global_data_barometer_2022`
Source: `papers/text/GlobalDataBarometer_2022__report.txt` (6026 lines).
PDF: `papers/GlobalDataBarometer_2022__report.pdf`.

## 1. Paper

**Citation.** Global Data Barometer (2022). *First Edition Report.* Data for Development Network (D4D.net), with funding from Canada's International Development Research Centre (IDRC). Builds on the Open Data Barometer (ODB) (Web Foundation / OD4D, 2013–2020). Public dataset and report at https://www.globaldatabarometer.org; research handbook at https://handbook.globaldatabarometer.org/2021/.

**Overall framing.** GDB measures "data for the public good" across **109 countries** (May 2019 – May 2021 evidence window) using **39 primary indicators** + **14 secondary indicators**, organized along 4 pillars (Governance 0.30, Capability 0.24, **Availability 0.42**, Use & Impact 0.04) and a set of thematic modules. Each primary indicator scored 0–100 against international "best practice"; report notes "Few countries score 100 out of 100 on any indicator" (line 308).

**Lobbying module specifically.** Lobbying lives inside the **Political Integrity** thematic module, alongside Public consultation, Political finance, RTI performance, and Asset declarations. The motivation:

> "Within democratic political systems, this involves transparency of political party finance, information on the interests of political decision makers, **information on lobbyists' interventions**, and information on public consultation processes in rule-making" (lines 2381–2384).

The Barometer flagged lobbying as a top-priority gap area:

> "The Barometer reveals, for the first time, the low availability of robust data on how private interests are seeking to influence public policy. With just 17.4 % of countries providing data online, and only 4 offering open data, this first edition of the Barometer offers a baseline to track progress if lobbying transparency gains, as we hope, greater profile in fora such as the Open Government Partnership in the coming years" (lines 2502–2506).

## 2. Methodology

**Construction.** Each "thematic" indicator pair (Governance + Availability) follows a common pattern (lines 662–675):

- **Existence** — does a framework / dataset exist, and what is its nature? (Used as a multiplier on the indicator score.)
- **Elements** — split between (a) **quality features** of the framework or dataset, drawn from "widely agreed international norms and clear use-cases", and (b) **(open) data features** drawn from a common cross-indicator checklist (structured, machine-readable, bulk, open license, etc.). Sub-questions weighted into element groups e1, e2, e3 summing to 100, with an optional negative-scoring group eb up to –20.
- **Extent** — does the framework/dataset cover the whole country and all citizens? (Used as a multiplier.)

**Scoring rule.** `final_score = element_score (0-100) × existence_multiplier × extent_multiplier`. Existence multipliers (governance) = 0 / 0.6 / 1; data-rule sub-multipliers run 0.6 / 0.85 / 0.95 / 1.0 (open-data requirement strongest). Availability multipliers = 0 / 0.5 / 1 (data missing / available not from gov / available from gov). Extent multipliers = 0.7 / 0.85 / 0.9 / 1. Element-level sub-questions answered Yes (1) / Partially (0.5) / No (0).

**Sample size.** 109 countries surveyed. For lobbying specifically, **19/109 (17.4%) had any lobby register information online; only 4 met the open-data definition**, with mean quality score 4.7 / 100 and mean openness score 5.19 / 100 (line 2427).

**Years covered:** evidence window May 1, 2019 → May 1, 2021. Field work May–late 2021.

**Top-line scale of effort:** 39 primary indicators, 607 primary variables, **107,389 data points**, 17,799 unique URLs reviewed, 581,040 words of justification.

## 3. Organizing structure

The lobbying-transparency module of GDB consists of **two paired primary indicators** (one Governance, one Availability), nested in the broader Political Integrity module:

| Indicator (appendix label) | Pillar | Module | Pillar weight | Module weight | Question text |
|---|---|---|---|---|---|
| **Lobbying register** | Governance | Political Integrity | 0.065 | 0.075 | "To what extent do relevant laws, regulations, policies, and guidance provide a basis for collecting and publishing data on lobbying activities?" (lines 5694–5698) |
| **Lobbying data** | Availability | Political Integrity | 0.0570 | 0.095 | "To what extent is lobby register information available as open data?" (lines 5850–5852) |

Each primary indicator decomposes into **Existence × Elements (e1+e2+e3, optional eb) × Extent**, with the element layer carrying the bulk of differentiating signal (the report uses a Data Protection Law worked example at lines 5300–5364: ~80 pts in e1, ~20 pts in e2, –20 pts available in eb).

Cross-cutting capability indicator that contextualizes lobbying alongside other political-integrity datasets:

| **Political integrity interoperability** | Capability | Political Integrity | 0.08 | 0.075 | "To what extent is political integrity data interoperable across different political integrity datasets, as well as other datasets associated with relevant information flows?" (lines 5759–5763) |

This interoperability indicator is what GDB uses to assess whether a country has "common identifiers that could tie together datasets" (line 2488) — relevant to lobbying because lobbyists' identifiers are what link lobby disclosures to political-finance disclosures, asset declarations, and company registers.

## 4. Indicator count and atomization decisions

**Headline count for the lobbying-transparency module: 2 primary indicators** (Lobbying register, Lobbying data), with a 3rd cross-cutting capability indicator (Political integrity interoperability) that partially carries lobbying-relevant signal.

**Atomization choice.** The TSV records the two paired primary indicators at the indicator level (i.e. the question-stem level), not at the sub-question level. Reasons:

1. The report itself appendix only lists indicators at this level. Sub-questions exist (the report describes the e1/e2/e3/eb structure) but their lobbying-specific texts are **not printed in the report** — they're in the research handbook at https://handbook.globaldatabarometer.org/2021/.
2. The worked example (Data Protection Law, lines 5298–5364) shows how sub-questions look (e.g. `G.GOVERNANCE.DPL.e1.CONSENT`). For lobbying, the analogous variable names and sub-question texts would need to be pulled from the GDB dataset/handbook.
3. The Capability cross-cut is included as a 3rd row but flagged in `notes` as borderline — extract only if "lobbying-transparency module" is read to include integrity-data interoperability.

**Implication for compendium use.** GDB's two indicators are **composite scores** rather than checklist items. They cover similar ground to country-level rubrics (existence of law, structured data, machine-readable, open license, etc.) but at one level of aggregation higher. To compare GDB items to per-disclosure-field items in (e.g.) FOCAL or PRI, you'd need the underlying handbook sub-questions.

## 5. Frameworks cited or reviewed

GDB explicitly inherits from / cites:

- **Open Data Barometer (ODB)** — direct predecessor, 4 editions 2013–2016, plus 2018 leaders edition and 2020 LATAM edition by ILDA. GDB describes itself as a "rebooting" of ODB (line 529).
- **Open Data Index** (Open Knowledge Foundation) — the crowd-sourced ancestor of ODB (line 518).
- **Sustainable Development Goals**, particularly **SDG 16** (Peace, Justice, Strong Institutions), targets 16.3 (rule of law), 16.6 (transparent/accountable institutions), 16.7 (responsive/inclusive decision-making), 16.10 (public access to information) — used as the reference frame for the Political Integrity module (lines 2395–2397).
- **The State of Open Data: Histories and Horizons** (book) — informed scoping (line 532).
- **Open Government Partnership (OGP)** — cited as the venue where lobbying-transparency progress should be tracked (line 2505).
- **The Data Spectrum** — open-vs-shared-vs-closed framework (line 413).
- For non-lobbying indicators GDB also leans on World Bank DGSS, UN E-Government Survey, Freedom House, ITU, ILO, WEF, WHO, RTI Rating — but none of these are lobbying-specific.

GDB does **not** cite a named lobbying-rubric predecessor in the lobbying-module narrative; the indicator design appears to have been done in-house by the Barometer team in consultation with thematic partners.

## 6. Data sources / collection method

> "From May 2021 until late 2021, field work took place in 109 countries, managed through a network of regional hubs. **An expert researcher for each country** completed an in-depth survey with responses going through regional and global reviews. Preliminary data was shared with thematic partners for additional validation with responses cross-checked, outliers reviewed, and final validation checks carried out by the Barometer team." (lines 589–597)

Network shape:
- **12 regional hubs** (e.g. Access Info Europe for Europe; ILDA for Latin America; Caribbean Open Institute; Open Data Kosovo; D4DAsia; etc.)
- **113 country researchers**
- **6 thematic partners** providing cross-country validation
- **Government surveys** (a shorter version of the expert survey) used in some countries during review (line 659)

Per indicator, researchers supplied:
- A written justification + sources
- URLs to specific laws / policies / dataset distributions
- File format, license, last-update date for each dataset cited (lines 680–684)

All justifications and supporting evidence are published as open data alongside the report.

## 7. Notable quirks / open questions

**(a) Paired Governance + Availability indicators.** GDB measures *what is required by law* and *what is actually online* as separate scores. Pairing reveals an "implementation gap": for the political-integrity datasets as a whole, "while 103 countries have rules requiring interest and asset declarations, and 53 include requirements around structured data collection and publication, just 50 have any information available online with just 4 providing open datasets" (lines 2510–2513). For lobbying, the implementation gap goes the other way (laws barely exist either): the report singles out "lobbying registers" as the **lowest-scoring sectoral governance indicator** (line 1238).

**(b) Open-data quality framework alongside the transparency-content framework.** This is the distinctive GDB move per the prompt. Each Availability indicator scores not only *whether* a dataset exists online, but *how openly*: a common checklist of open-definition criteria — "Online, Free, Machine Readable, Open License, Bulk data" plus "presence of accessible tools to explore available data" (lines 2053–2054) — runs across all 17 primary availability indicators, including Lobbying data. So a country with a lobby register published only as scanned PDFs would get partial credit on existence-online but lose nearly all element-score points. This is why the topline shows 19 countries with lobby info online but only 4 meeting the open-data definition.

**(c) Coverage extent multiplier.** A federal country whose lobby register only covers the national legislature (not states) is downgraded by the Extent multiplier to 0.7–0.85× of the element score. This is methodologically distinct from a binary "register exists yes/no" and is part of why GDB's lobbying scores cluster low.

**(d) Researcher supplementary-norms question.** When no framework exists, researchers were asked "In the absence of a strong legal framework, are there alternative norms or customs that play this role in the country?" (lines 5384–5385). For lobbying this is informative — many jurisdictions self-regulate — though the multiplier is still 0 in scoring.

**(e) FOCAL's stated relationship to GDB.** FOCAL (Lacy-Nichols 2024) cited GDB as methodological touchstone: "Building on the approach used in the Global Data Barometer, we focused on indicators measuring what information is disclosed in registers, and how information is disclosed." FOCAL's "what is disclosed" / "how it is disclosed" split mirrors GDB's element-quality / element-openness split. FOCAL's 50 conceptual indicators are approximately the **expanded sub-question layer** of what GDB compressed into 2 composite scores. FOCAL's "only 19 of 109 surveyed countries had a lobbyist register available online" is taken directly from GDB's `Lobbying data | 19 | 4 | 4.7 | 5.19` row (line 2427).

**(f) Sub-question text not in the report.** A real downside for compendium work: the report appendix gives indicator names and weights but not the lobbying-specific sub-question wording. To extract sub-question-level items comparable to FOCAL/Newmark/etc., you'd need to pull from the **handbook (https://handbook.globaldatabarometer.org/2021/)** or the **published GDB dataset** (filterable by `hlevel=4` and `data_type='response'`, per lines 5563–5567). This is an open follow-up if finer granularity is needed.

**(g) Country-level leaders.** Canada is flagged as both Regional and Global Leader on (A) Lobbying data (line 3935). Taiwan is Regional Leader on (G) Lobbying register (line 4750). USA is flagged as a leader on (A) Lobbying data with Use score 42.0 / Open Data Initiative 54.0 (line 4047) — surprising given the patchwork-state lobbying landscape, and worth interrogating.

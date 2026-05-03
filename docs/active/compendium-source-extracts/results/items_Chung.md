# Chung, Cullerton & Lacy-Nichols 2024 — Mapping the Lobbying Footprint of Harmful Industries

## 1. Paper

**Citation.** Chung H, Cullerton K, Lacy-Nichols J. Mapping the Lobbying Footprint of Harmful Industries: 23 Years of Data From OpenSecrets. *The Milbank Quarterly* 2024;102(1):212–232. doi: 10.1111/1468-0009.12686. Open access (CC-BY).

**Author affiliations.** Chung & Lacy-Nichols at the Centre for Health Policy, Melbourne School of Population and Global Health, University of Melbourne; Cullerton at the School of Public Health, University of Queensland.

**Framing.** This is an empirical mapping paper situated in the **commercial determinants of health (CDoHs)** literature. The authors argue that public-health advocates often refer to "the industry" or "corporations" as a homogenous proxy for harmful actors, which "stymies efforts to develop a science of commercial determinants" (lines 64–66). The study contrasts the lobbying activities of four industry sectors — **tobacco, alcohol, gambling, and ultraprocessed food (UPF)** — over 23 years (1998–2020), differentiating commercial companies from industry trade associations.

A second framing question runs alongside the empirical mapping: "what are the opportunities and limitations afforded by the OpenSecrets database?" (lines 164–165). This makes Chung 2024 partly a **practical assessment of OpenSecrets-as-monitoring-infrastructure** for CDoH researchers — including the authors' explicit interest in adapting the OpenSecrets approach to other jurisdictions ("we conclude by proposing ways that this database could be adapted and modified so that other jurisdictions can more easily monitor corporate political activity," lines 166–168).

## 2. Methodology

**Industries studied.** Four "harmful industry" sectors: tobacco, alcohol, gambling, ultraprocessed food (UPF). The paper argues these are sectors that have been the focus of much public-health research and advocacy, and notes (line 85) that other harmful sectors — guns, fossil fuels — are mentioned in the literature but not analyzed here.

**Time window.** 1998–2020 (23 years). Lobbying expenditure data drawn from OpenSecrets between May 15, 2022 and June 22, 2022 (110 individual CSV files manually downloaded; bulk-data access was requested but never granted).

**Data source.** OpenSecrets exclusively for the lobbying analysis, supplemented with **Euromonitor** market-share data (12 data sets covering 2013–2020 for alcohol, UPFs, and tobacco; gambling unavailable) and **World Bank** GDP deflators for inflation adjustment.

**Analytical strategy.** Two phases:

1. **Phase 1 — Sector-level mapping.** Annual lobbying expenses 1998–2020 collected for the four sectors (operationalized via five OpenSecrets industry categories: tobacco; casinos/gambling; beer, wine, and liquor; food and beverage; food processing and sales). All 1,047 clients reviewed and coded as commercial company vs. trade association; nine clients with multiple OpenSecrets classifications were assigned by largest spending. Inflation-adjusted to 2020 USD. Parent/subsidiary cross-walking done manually.

2. **Phase 2 — Lobbyist-level analysis.** For the **top 2 companies and top 2 trade associations per sector** (n = 16 clients), 333 lobbyist files were extracted (July 22–26, 2022). Phase 2 covers in-house vs. third-party employment, headcount, expenditure split, and revolving-door background.

**Visualization tool.** Power BI for relational data modeling and visualization.

## 3. Organizing structure

Chung 2024 does **not construct a disclosure-rubric or scoring system**. There are no items, points, or scales. What the paper does construct is:

- **An industry-classification scheme** that maps four "harmful industry" sectors of public-health concern onto five OpenSecrets industry categories.
- **A commercial-actor typology** (company vs. trade association) added on top of OpenSecrets' undifferentiated "client" label.
- **A lobbyist-employment typology** (in-house vs. third-party) — this one is already in OpenSecrets but the paper foregrounds the comparison.
- **A revolving-door classification** (former government employee / former member of Congress / no government background) — directly from OpenSecrets.
- **A set of computed metrics** layered onto these classifications: total spend, annual spend, active-client count, spending concentration, years active, market-share-to-lobbying coverage, in-house/third-party spend ratio, in-house/third-party headcount ratio, and revolving-door cross-tabs.

The TSV captures these as 14 rows because they are the project's analytical primitives: anyone replicating Chung's analysis on US state lobbying data would need to make the same decisions about each.

## 4. Indicator count and atomization decisions

**14 rows in `items_Chung.tsv`**, broken down as:

- 1 industry classification (sector) — kept as a single row because it is one variable, even though it draws on five OpenSecrets categories.
- 1 actor-type classification (company / trade association).
- 1 lobbyist-employment classification (in-house / third-party).
- 1 revolving-door classification (3-way categorical).
- 7 computed metrics (totals, annual, active-client count, concentration, years active, market-share match, parent linkage).
- 3 cross-tab metrics built on top of the classifications (in-house spend ratio, in-house headcount ratio, revolving-door-by-employment-type).

**Atomization decisions made:**

- **Industry-sector classification kept as one row, not five.** The five OpenSecrets categories (tobacco; casinos/gambling; beer/wine/liquor; food and beverage; food processing and sales) are the *implementation* of one analytical variable (sector). Treating them as five separate indicators would mistake the OpenSecrets taxonomy for Chung's contribution.
- **In-house/third-party split into two rows.** Because the paper explicitly distinguishes the **spend** ratio from the **headcount** ratio (and reports that they tell different stories), these are kept separate.
- **Total expenditure and annual expenditure split into two rows.** Same metric at two grains; the paper uses the annual series specifically to identify policy-event-correlated spikes (2009 sugar tax; 2013–2015 GMO labeling) which the cumulative figure would obscure.
- **Parent-company linkage included as a procedural row** even though it is not a metric. Without it, every other metric is wrong, so it is a load-bearing analytical primitive.
- **Market-share linkage kept as one row.** Although the paper reports both the coverage % (51–60% of top-market-share companies appear) and the spending share (64–90% of company lobbying), these are two reads of the same join.

## 5. Frameworks cited or reviewed

The paper situates itself against three CDoH-monitoring frameworks (lines 144–150):

- **Commercial Determinants of Health (CDoHs) Index** — Lee, Freudenberg, Zenone et al. 2022 (ref 31). The only one of the three to include lobbying as an indicator.
- **Corporate Permeation Index** — Madureira Lima & Galea 2019 (ref 33). Excluded lobbying due to insufficient cross-country comparable data.
- **Corporate Financial Influence Index** — Allen, Wigley & Holmer 2022 (ref 13/32). Also excluded lobbying for the same reason.

Other named instruments / databases:

- **OpenSecrets** (refs 36, 37) — the primary data source.
- **LobbyView** (ref 48; Kim 2018) — flagged as a complementary US database that links lobbying activity to specific bills.
- **International Standards for Lobbying Regulation** (ref 23) — the joint Access Info Europe / Open Knowledge / Sunlight Foundation / Transparency International product. Cited only for its definition of lobbying.
- **Comparative Agendas Project** (ref 50; Baumgartner, Bruenig & Grossman) — cited as an example of cross-country data harmonization.
- **OECD lobbying surveys** (refs 22, 24).
- **Global Data Barometer** (ref 19).
- **Euromonitor** market-share data (used for the cross-source linkage analysis).

## 6. Data sources

**Lobbying data: OpenSecrets exclusively.** The lobbying database is "compiled from reports filed with the Senate Office of Public Records (SOPR) in accordance with the Lobbying Disclosure Act" (lines 178–179). All federal-level. 110 CSV files manually downloaded.

**Supplementary sources:**

- **Euromonitor** for market-share data on the largest companies in alcohol (alcoholic drinks), UPFs (snacks, soft drinks, staple foods), and tobacco (8 product categories). 2013–2020 coverage. Gambling not available.
- **World Bank Databank** GDP deflators for inflation adjustment to 2020 USD.

**FOCAL author-cluster context.** Per the FOCAL ref #44, Chung is in the same author cluster as Lacy-Nichols 2023 + 2024. Confirmed in this paper's references:

- Ref 20: Lacy-Nichols, Quinn, Cullerton 2023 — *Aiding empirical research on the commercial determinants of health: a scoping review of datasets and methods about lobbying.* Health Res Policy Syst.
- Ref 21: Lacy-Nichols & Cullerton 2023 — *A proposal for systematic monitoring of the commercial determinants of health: a pilot study assessing the feasibility of monitoring lobbying and political donations in Australia.* Glob Health.
- Ref 51: Lacy-Nichols, Marten, Crosbie, Moodie 2022 — *The public health playbook.*

This study is explicitly part of the "broader program to explore approaches to monitor CDoHs" (lines 104–105) that Lacy-Nichols 2023 (ref 21) initiated for Australia. Cullerton appears as second author here and as co-author on the Australian pilot.

## 7. Notable quirks / open questions

**Federal-only scope.** The OpenSecrets data Chung uses is the LDA-derived federal lobbying database. Nothing in the paper covers state-level lobbying. A cross-walk to the project's "LobbyView for 50 states" framing would require **state-disclosure data integration** — which OpenSecrets itself does separately (the OpenSecrets State Lobbying Disclosure Scorecard, already extracted in the project's `items_OpenSecrets.tsv`, addresses state-level access; Chung does not touch it).

**Industry-category fit is loose.** The authors are explicit about this: "many companies in these categories have diverse portfolios (for instance, Coca-Cola has a large bottled-water segment) and that not all products are universally or equivalently harmful to health" (lines 198–201). UPF in particular is constructed by aggregating two OpenSecrets categories ("food and beverage" + "food processing and sales") that include non-UPF business. They flag the need for "more granular and nuanced classification schemes" (line 559).

**Bulk data inaccessible.** "Despite several requests, we were unable to access the bulk data and instead relied on manually downloading individual spreadsheets" (lines 202–204). For replication on state data, this points to the importance of bulk data availability as a methodological precondition.

**Parent-company resolution is hand-rolled and incomplete.** Chung admits to missing some links (e.g., Hay Island Holdings / Swisher International) and 1,047 clients were manually reviewed. Any state-level pipeline at the project's intended scale would need a more systematic entity-resolution approach.

**Pro-rata allocation for third-party lobbyists is a Chung methodological choice.** OpenSecrets reports total firm spend, not per-lobbyist spend; Chung divides firm spend by lobbyist count to avoid double counting. State data may not require (or may not permit) the same allocation.

**The revolving-door schema is "blunt."** Chung explicitly flags that the OpenSecrets revolving-door categories "are relatively blunt" and that "a more detailed schema (for instance, highlighting the particular congressional committee or pathway through politics) may offer more insights" (lines 522–526). The project's LLM pipeline could potentially do better here if structured filing data exposes prior-employment text.

**Indirect / "dark money" advocacy is out of scope.** "We did not capture in our analysis... political donations or grassroots lobbying... Many of these think tanks and associations are structured as nonprofits and are exempt from financial disclosure requirements" (lines 471–476). Chung's findings about industry-association lobbying (43% of alcohol; 32% of UPF) are likely lower bounds on indirect advocacy.

**Public-positions-vs-private-giving gap.** The paper raises but does not analyze the gap between companies' public statements and their lobbying via trade associations — citing Brulle & Downie 2022 on fossil-fuel trade associations holding "more controversial and oppositional issue position[s] on climate change issues" than their member companies do (lines 491–493).

**Federal-state cross-walk would be informative.** Chung implicitly assumes federal lobbying captures a substantial share of corporate political activity, but for some sectors (gambling, alcohol, UPF), state-level lobbying is plausibly where most influence-buying occurs. The project's state-level pipeline could test whether the four-sector concentration patterns Chung documents at the federal level replicate, attenuate, or invert at the state level.

---

## Notes on extraction

- All quotes verified line-by-line against `papers/text/Chung_2024__mapping_lobbying_footprint.txt` (761 lines).
- No external references consulted for this extract (no PRI 2010, no `compendium/disclosure_items.csv`, no `framework_dedup_map.csv`, no `docs/COMPENDIUM_AUDIT.md`, no `items_OpenSecrets.tsv`).
- Section 3 makes clear this paper does not construct a disclosure rubric. The TSV is populated with the analytical dimensions and computed metrics actually used; `notes` columns flag the empirical-application nature.

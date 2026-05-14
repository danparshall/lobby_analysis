# OpenSecrets 2022 — State Lobbying Disclosure: A Scorecard

## 1. Paper

**Citation.** Auble, Dan, and Brendan Glavin. "State Lobbying Disclosure: A Scorecard." OpenSecrets, June 28, 2022. Part of the *Layers of Lobbying* series, funded in part by Omidyar Network. Source: opensecrets.org (lines 1-5, 317-319).

**Framing.** OpenSecrets tracked over $1.8B in 2021 state-level lobbying spending, but argues this is a fraction of the true total because most state disclosure laws fail to require a full accounting. "OpenSecrets' database includes lobbyist and client registration data for all 50 states, but only 19 of the 50 states make meaningful data available on lobbying spending. The remaining states do not require sufficient disclosure of lobbying activity in a way that makes it possible to include them in a comparable manner to the 19 states that provide fuller disclosure" (lines 21-30). The scorecard "compares each state with a focus on four key areas of disclosure that affect the ability of the public to know key facts about lobbying in their states" (lines 35-37). The report explicitly frames itself as not comprehensive: "This report does not cover all areas of state lobbying disclosure. Disclosure of targeted legislation is something not addressed in this report that is ripe for further examination" (lines 305-308).

## 2. Methodology

- **Sample.** All 50 U.S. states are scored. (Distinct from the spending-tracking which only covers 19 states.) Map and "complete list" of per-state scores referenced in the article (lines 189-195) but full per-state data are not included in the text excerpt.
- **Year of data.** Reflects state disclosure regimes as of mid-2022; spending statistics cite 2021 totals.
- **Scoring scale.** Numeric, not letter-grade. "Each of the four key areas discussed above was graded on a five-point scale" (lines 196-197). Theoretical maximum total = 4 × 5 = **20**. The text references "top-scoring states (16 and up)" (line 221) and the "poorest scoring states, those that scored less than 10 total" (line 232), confirming the additive integer total across four 5-point categories.
- **Scoring rule per category.**
  - **Category 1 (Lobbyist/client disclosure):** baseline = 3 (identifies both lobbyist and client); 4 = separate registrations required; below baseline = 0-3 by circumstance. The score-5 anchor is not explicitly defined in the article text.
  - **Category 2 (Compensation):** 4 = baseline (full compensation disclosure linked to individual lobbyists, inferred from context); 5 = exceeds baseline; 0 = no compensation disclosure required; 1-3 for partial disclosure (ranges, or unlinked to individual lobbyists), "in relation to the level of compensation disclosed."
  - **Category 3 (Timely disclosure):** 4 = baseline (monthly when legislature in session, quarterly otherwise); 5 = exceeds baseline (monthly throughout the year); below baseline 0-3 per individual circumstances.
  - **Category 4 (Public availability):** 5-point composite summed from three sub-facets — user-friendly search (2 pts), downloadable data (2 pts), lobbyist/client lists (1 pt). Partial points allowed for "lists that are available, but not as easily accessed."
- **Aggregation.** Simple sum of the four category scores (0–20). The article does not define explicit grade tiers, but uses descriptive bands: "top-scoring states (16 and up)", and "poorest scoring states... less than 10 total" (lines 221, 232).
- **Inter-coder reliability.** Not reported.

## 3. Organizing structure

The scorecard organizes the rubric into 4 numbered key areas, with the fourth area itself decomposed into 3 named sub-facets. Indicator counts:

| # | Category (OpenSecrets' label) | Indicator count |
|---|-------------------------------|-----------------|
| 1 | Who is lobbying and who is paying for it? | 1 |
| 2 | How much are lobbyists getting paid? | 1 |
| 3 | Is there timely disclosure? | 1 |
| 4 | How easily can the public access disclosed information? (composite) | 1 composite + 3 sub-facets = 4 |
| **Total** | | **7** |

## 4. Indicator count and atomization decisions

**Total: 7 indicators** (4 top-level categories + 3 sub-facets of category 4 captured separately because they are individually point-weighted in the rubric).

Atomization judgment calls:

- **Category 4 split.** Public availability is enumerated as exactly three named sub-facets ("three key facets", lines 106-109): search, lists, downloads. Each carries a distinct point weight (2/2/1) explicitly stated in the article (lines 212-216). I represent both the composite (`public_availability_total`) and each sub-facet as separate indicator rows so downstream alignment with other rubrics can either match the composite or match the sub-facets. The composite row is annotated `composite_ordinal`.
- **Category 1 (lobbyist/client disclosure) kept single.** The article describes only two scoring anchors (baseline = 3 for "identifies both", 4 for "separate registrations") and references the rationale (clean data collection, single source of truth, lines 60-73). It does not split into "lobbyist identified" + "client identified" + "registrations separated" sub-indicators. Kept as a single ordinal.
- **Category 2 (compensation) kept single.** The article does discuss "ranges" vs "unlinked to individual lobbyists" as two distinct deficiency modes within partial disclosure (lines 78-81), but treats them collectively under one 0-5 ordinal. Not split.
- **Score-5 anchor for category 1.** The text describes baseline=3 and separate-registration=4 but does not say what would earn a 5 in this category. This is a gap in the rubric description; preserved verbatim in `notes`.
- **Not separately scored: targeted-legislation disclosure.** Explicitly excluded by OpenSecrets as a known gap: "Disclosure of targeted legislation is something not addressed in this report that is ripe for further examination" (lines 305-308). Not represented as an indicator because OpenSecrets does not score it.
- **Not separately scored: in-house vs contract lobbyists, gift bans, lobbyist-prior-employment disclosure, issue-area reporting.** These appear in the federal-comparison narrative (lines 161-184) but are not state-rubric indicators in OpenSecrets' scoring system.

## 5. Frameworks cited or reviewed

The article does **not** cite or review any prior state-disclosure rubric by name. Verified by full-text search of the source: no mention of Sunlight Foundation, Center for Public Integrity, Public Integrity Index, PRI, State Integrity, Newmark, or NCSL. The only OpenSecrets self-references are to companion reports in the *Layers of Lobbying* series (lines 6-11):

- "Layers of Lobbying: An examination of 2021 state and federal lobbying from K Street to Main Street"
- "Layers of Lobbying: Federal and state lobbying trends in spending, representation and messaging"

The federal comparison section references the **Lobbying Disclosure Act** (line 139) as a benchmark, not as a rubric.

OpenSecrets' own internal research is cited twice: a finding that government-relations workforce may be "at least double what is reported in official lobbying filings" (lines 179-181), and that "about half of former lobbyists who stop reporting lobbying each year remain in jobs related to government relations" (lines 182-184). These are evidence claims, not rubric inputs.

The Virginia Public Access Project is mentioned (lines 242-245) as a non-profit that fills disclosure gaps left by official Virginia outlets; not a rubric.

**Bottom line on FOCAL's claim.** FOCAL 2024 reportedly cites OpenSecrets 2022 as drawing on prior rubrics. From the OpenSecrets text alone, this is **not supported** — OpenSecrets 2022 does not name any predecessor rubric. The methodology appears to be original to OpenSecrets, derived from their own data-collection experience across 50 states.

## 6. Data sources

Per-state values come from OpenSecrets' own assessment, drawing on three implicit data sources (the article does not formally enumerate methodology, but the references throughout reveal these inputs):

- **State statutes / disclosure laws.** "Many states' disclosure laws do not require a full accounting" (lines 18-19); "OpenSecrets has analyzed lobbying disclosure rules state by state" (lines 33-35). Statute reading is the basis for categories 1, 2, and 3 (what is required to be disclosed and at what frequency).
- **State agency disclosure portals (firsthand inspection).** Direct reference to specific state sites is made for scoring category 4 — Washington state's site is praised for navigability and download links (lines 228-230); Oklahoma's guidance is quoted directly (lines 60-64); North Dakota, South Dakota, and Virginia are critiqued by site behavior (lines 234-245). The Virginia Public Access Project (a non-profit alternative) is mentioned as filling gaps (lines 242-245).
- **OpenSecrets' own database.** OpenSecrets maintains lobbyist/client registration data for all 50 states (line 21-22) and tracks spending in 19 (lines 22-23). The 19-state subset is the basis for the empirical $1.8B figure (line 13-14) and informs which states "are tracked in the OpenSecrets database" (line 224). The 19-state vs 50-state distinction is itself diagnostic of compensation-disclosure adequacy.

The article does not mention surveys of state agency staff. It does mention plans to "expand outreach efforts to data users and agency staff" (lines 309-311) as future work.

## 7. Notable quirks / open questions

- **The 19-state gap (yes, discussed).** OpenSecrets explicitly documents this. Of 50 states, only 19 "make meaningful data available on lobbying spending" (line 22). The other **31 states** are excluded from cross-state spending comparisons (not from the scorecard itself — all 50 are graded on rubric categories). The reason given: "The remaining states do not require sufficient disclosure of lobbying activity in a way that makes it possible to include them in a comparable manner to the 19 states that provide fuller disclosure" (lines 27-30). The deeper root cause, by OpenSecrets' diagnosis: missing or partial compensation disclosure. "Seventeen states do not require compensation paid to lobbyists be disclosed at all. Seven more states only require partial reporting with compensation either reported in ranges or not linked to individual lobbyists" (lines 78-81). 17 (none) + 7 (partial) = 24, but the spending-comparable 19 leaves room because partial-disclosure states may still be included if their partial data is structured enough.
- **Numerical tension on "states with full compensation disclosure".** The conclusion states "26 states require full compensation disclosure, seven have partial disclosure" (lines 266-267). 26 + 7 + 17 = 50; OK. But the spending-comparable subset is 19, not 26. The gap (26 - 19 = 7 states) is unexplained — perhaps these 7 states require compensation but the data is unusable for OpenSecrets' tracking pipeline for some other reason (data format, access barriers). Flagged as open question.
- **Score-5 descriptor missing for category 1.** The article gives baseline = 3 and separate-registration = 4, but does not state what earns a 5 in lobbyist/client disclosure. (For categories 2 and 3, score 5 = "exceeding baseline" is explicit.)
- **Category 4 sub-facet weights unequal.** Search and downloads each carry 2 points; lists carry 1 point. The article does not justify why lists are weighted half as much, beyond noting they are a "necessity" given current search-feature limitations.
- **No inter-coder reliability or audit methodology.** The scoring is presented as authoritative without describing whether multiple analysts coded each state, whether scores were verified with state agencies, or how disputes were resolved.
- **"Not comprehensive" disclaimer.** Targeted-legislation disclosure is named as the most prominent omission (lines 305-308). The 4-category rubric is therefore explicitly partial coverage of the disclosure-rules space, by OpenSecrets' own admission.
- **Subjectivity caveat for category 4.** OpenSecrets acknowledges public-availability scoring "are more subjective and can have gray areas" (lines 210-211). Categories 1-3 are presented as more rules-based.
- **Top-scoring shared profile.** All states scoring 16+ "require compensation to be reported and they make that information available to the public in an accessible way" (lines 221-224) — i.e., category 2 + category 4 jointly drive the top tier. Bottom-tier states (<10) almost universally score 0 on category 2 (lines 231-233). The score distribution implies category 2 is the dominant driver of total score.

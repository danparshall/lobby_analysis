# FOCAL — Lacy-Nichols et al. 2024

## 1. Paper

**Citation.** Lacy-Nichols J, Baradar H, Crosbie E, Cullerton K. Lobbying in the sunlight: a scoping review of frameworks to measure the accessibility of lobbying disclosures. *International Journal of Health Policy and Management* 2024;13:8497. doi:10.34172/ijhpm.8497.

**Framing.** The paper has a dual purpose: (a) a systematic scoping review of 15 prior frameworks for evaluating lobbying disclosure/transparency, and (b) a synthesis output — the **Framework fOr Comprehensive and Accessible Lobbying (FOCAL)**, an 8-category, 50-indicator framework constructed from the reviewed literature. FOCAL is positioned as a "template for policy-makers to develop or strengthen regulations to improve lobbying transparency" (abstract, line 25–27). The framework is **conceptual** in this iteration: "This first iteration of FOCAL is conceptual – the next logical step is to apply the framework to assess government lobbying disclosures in practice (this is the next phase of our research project)" (line 1177–1180).

This extract captures FOCAL's own 50-indicator synthesis, **not** the 15 reviewed predecessor frameworks (those are catalogued separately).

## 2. Methodology

FOCAL was synthesised by thematically coding the 15 frameworks identified through the scoping review:

> "Between June and August 2023, we used QSR NVivo to code the frameworks, coding a total of 248 items. We took an iterative approach to modifying our coding framework as new categories emerged. … When decisions were made about consolidating different disclosure requirements from the 15 frameworks, we preferenced the most rigorous indicators." (lines 382–395)

Key methodological choices:

- **Scope of coding:** indicators that could be assessed by viewing a register, plus two categories that can only be assessed by viewing legislation: (1) definitions of lobbyists/targets/activities, and (2) requirements about frequency of disclosures (lines 388–391).
- **Out-of-scope items excluded:** "enforcement/compliance, sanctions, ethics/integrity laws, cooling off period requirements, how the public accesses the policy process" (lines 372–375).
- **Synthesis principle:** when consolidating overlapping indicators across frameworks, the authors "preferenced the most rigorous indicators" (line 394–395).
- **Conceptual schema:** the authors built Figure 2, "The Dynamics of Lobbying," to distinguish actors and interests, which guided their framework structure (lines 376–381).

**Sample size and year not applicable** — FOCAL is a framework paper, not an applied scorecard. No jurisdictions are scored. The companion application study is referenced as forthcoming: "In a complementary study we are testing the feasibility of applying FOCAL to evaluate government lobbying disclosures" (line 834–836).

## 3. Organizing structure

FOCAL has **8 primary categories** containing **50 total indicators**:

| # | Category | Indicators | Category description (verbatim) |
|---|---|---|---|
| 1 | Scope | 4 | "The scope of what is included and excluded from the register" |
| 2 | Timeliness | 3 | "The frequency of lobbying disclosures" |
| 3 | Openness | 9 | "How easy it is to find and use information in the register" |
| 4 | Descriptors | 6 | "Descriptions and identifying elements of the individuals and organisations involved in lobbying" |
| 5 | Revolving door | 2 | "The movement between public and private sector employment" |
| 6 | Relationships | 4 | "The connections between the different actors involved in or benefiting from lobbying" |
| 7 | Financials | 11 | "The flow of money spent and earned through lobbying activities" |
| 8 | Contact log | 11 | "The activities of lobbyists" |
| | **Total** | **50** | |

**Authoritative quote on structure:**

> "Our FOCAL was synthesised from the above 15 frameworks. It comprises eight categories and 50 indicators (Table 3). … The first two categories (definitions and timeliness) can be assessed by viewing the reporting requirements for a register (eg, the legislation underpinning it), while the other categories can be assessed by viewing the register itself." (lines 827–834)

**Priority signal:** FOCAL is unweighted, but the paper recommends prioritising **scope and contact logs** for resource-constrained governments: "If governments have limited resources (such as many LMICs) to implement all aspects of FOCAL, we suggest they prioritise scope and contact logs" (lines 1153–1154).

## 4. Indicator count and atomization decisions

- **Total claimed:** 50 indicators in 8 categories (abstract line 22–23; results line 828).
- **Total verified:** 50 (4 + 3 + 9 + 6 + 2 + 4 + 11 + 11), counting each Table 3 row as one indicator. Confirmed by row count of `items_FOCAL.tsv`.
- **Categories named in abstract:** "scope, timeliness, openness, descriptors, revolving door, relationships, financials, and contact log" (line 22–23). Verified verbatim against Table 3 headings.

**Judgment calls:**

1. **No native numerical IDs.** Table 3 does not number indicators (no "1.1", "2.3" etc. as the brief anticipated). I assigned IDs of the form `<category>.<n>` (e.g., `scope.1`, `financials.11`) following Table 3 row order. This is an extraction convenience, not a FOCAL convention.
2. **Compound/checklist indicators kept as one row.** Several Table 3 rows enumerate multiple sub-criteria within a single indicator, e.g.:
   - `scope.1` lists 9 lobbyist types as one indicator.
   - `scope.3` lists 8 target types as one indicator.
   - `openness.3` bundles 5 sub-criteria (no registration / free / open license / non-proprietary / machine readable) as one indicator.
   - These were kept as single indicators because (a) Table 3 itself groups them on one row and (b) only that grouping makes the total "50" claim hold.
3. **"For consultant lobbyists & lobby firms" sub-header.** Table 3 includes a sub-header line above the first three Financials indicators (lines 1003–1004). It is not a separate indicator. It appears to scope `financials.1` (Total lobbying income — already labelled "for consultant lobbyists/lobby firms"), `financials.2` (Lobbying income per client), and `financials.3` (Income sources). The remaining 8 Financials items (`financials.4`–`financials.11`) are not visually under this sub-header and concern expenditure/contributions applicable to all lobbyists. I have flagged this scoping in the TSV `notes` column. The sub-header was not counted as a 51st indicator.
4. **Narrative inconsistency about category names.** The narrative section at line 831 refers to "the first two categories (definitions and timeliness)", but the abstract (line 22–23), Table 3 (line 947), and the in-narrative section heading at line 842 all use **"Scope"**, not "Definitions". This is a minor authorial slip; "Scope" is the canonical category name (see Quirks).
5. **`indicator_type` is my categorical inference**, not a FOCAL field. Values used: `boolean`, `checklist`, `field`, `amount`, `count`, `frequency`, `threshold`. FOCAL itself does not specify indicator types.
6. **`scoring_rule` is "Not specified" for all 50.** FOCAL does not assign weights, points, or thresholds. The paper is explicit: "While we have not added weights to our indicators, we propose that two categories are especially important…" (line 1147–1148). Scoring/weighting is flagged as future work via Delphi study (lines 1196–1200). For `scope.2`, the paper additionally flags subjectivity: "what is a 'low' financial or time threshold to qualify/exempt lobbyists from registration? This is a question we will consider in the next stage" (lines 1206–1208).

## 5. Frameworks cited or reviewed

FOCAL was synthesised from **15 frameworks** (6 peer-reviewed, 9 grey literature) covering 1991–2022. Per Table 2 (lines 455–769), they are:

| # | Author/Organisation | Year | Framework name |
|---|---|---|---|
| 1 | Opheim C. | 1991 | Index of state lobbying regulation law |
| 2 | Newmark A. | 2005 | Index to measuring state lobbying regulation |
| 3 | Center for Public Integrity | 2007 | Hired Guns |
| 4 | Pacific Research Institute | 2010 | State disclosure law criteria |
| 5 | Holman C; Luneburg W. | 2012 | Elements of lobbying regime |
| 6 | ALTER-EU | 2013 | Lobby disclosure requirements |
| 7 | Access Info Europe, Open Knowledge, Sunlight Foundation, Transparency International | 2015 | International Standards for Lobbying Regulation |
| 8 | Centre for Research on Multinational Corporations (SOMO / Vander Stichele) | 2016 | (Unnamed) |
| 9 | Council of Europe | 2017 | Guiding principles on devising policy at national level to regulate lobbying |
| 10 | Newmark A. | 2017 | 2015 Measure of lobbying regulation |
| 11 | Carnstone Partners Ltd; Meridian Institute (Hodgson & Witte) | 2020 | The Responsible Lobbying Framework |
| 12 | Roth A.S. | 2020 | Lobbying regulation robustness index |
| 13 | Bednárová P. | 2020 | CII/HG methodology |
| 14 | Independent Broad-based Anti-corruption Commission (IBAC) | 2022 | Recommendation 3 |
| 15 | Laboutková Š.; Vymětal P. | 2022 | Catalogue of transparent lobbying environments |

These are named here only because FOCAL is a synthesis output of these 15. Per the brief, **no items are re-extracted from them in this file** — predecessor extracts live separately.

## 6. Data sources

**N/A** — FOCAL is a framework paper, not an applied scorecard against a dataset. No state, country, or register is scored in this paper.

The paper does describe **applicability constraints**:

- **Conceptual iteration:** "This first iteration of FOCAL is conceptual" (line 1177).
- **Context dependence:** "this framework may not be applicable in the same way across all political systems, and that alterations may be necessary to account for the different systems and rules in place" (lines 184–186); "some of these may be context dependent, for instance the target of lobbying may vary depending on the form of government (eg, a Westminster vs Presidential system)" (lines 855–858).
- **US-centric financials:** "this particular category is especially US-centric, with many indicators originating from the Hired Guns framework, designed to evaluate US state lobbying regulations" (lines 1059–1062).
- **Scope of disclosure types:** FOCAL covers two disclosure mechanisms — **lobbyist registers** and **open agendas / ministerial diaries** — and excludes whistleblower protections, enforcement mechanisms, codes of conduct, etc. (lines 350–354, 372–375).

A companion application phase is forthcoming but not in this paper: "In a complementary study we are testing the feasibility of applying FOCAL to evaluate government lobbying disclosures" (line 834–836).

## 7. Notable quirks and open questions

1. **No native indicator numbering.** FOCAL's Table 3 uses category headings + bullet rows but does **not** assign indicator IDs like "1.1" or "2.3". The brief anticipated FOCAL would self-number; it doesn't. I imposed `<category>.<n>` IDs.
2. **Narrative slip on first category.** The narrative says "the first two categories (definitions and timeliness)" (line 831), but the actual category name is **Scope**, not Definitions. Likely an authorial residue from an earlier draft (the predecessor frameworks heavily use "Definition" as a category — e.g., Hired Guns, Newmark, Roth, Bednářová all have "Definition" categories). The Scope category does include lobbyist/target/activity definitions, but FOCAL's chosen label is Scope. Treat Scope as canonical.
3. **The "For consultant lobbyists & lobby firms" sub-header in Financials** is structural ambiguity within Table 3. Not a 51st indicator. Likely scopes the first 3 Financials items (income-side); the remaining 8 (expenditure/contributions) appear to apply to all lobbyists. The paper text doesn't explicitly resolve this. Captured in TSV `notes`.
4. **No weights, no thresholds, no scoring rules.** FOCAL is intentionally unweighted. This is an explicit limitation: "One limitation of FOCAL is that it is unweighted (ie, all indicators are equally important). … a useful area for future research is to assign values to the indicators" (lines 1194–1199). For state-by-state application via this project, downstream choices are needed: which indicators are relevant to US state-level data, what (if any) thresholds apply (e.g., what counts as "low" in `scope.2`, what "real time" means for `timeliness.1–2`).
5. **Compound indicators are common.** Several rows pack multiple sub-criteria (e.g., `scope.1` = 9 lobbyist types, `openness.3` = 5 open-data attributes). Downstream scoring/atomization must decide whether to score these as all-or-nothing, additive, or split into atomic sub-items. FOCAL's "50" count requires keeping them as one each.
6. **Two non-register-based categories.** Scope and Timeliness are flagged as assessable only by viewing legislation, not the register itself (lines 388–391, 831–834). For US state work, this means these 7 indicators (4 scope + 3 timeliness) require statute review, while the other 43 require register/website inspection.
7. **Priority recommendation (not weights).** Scope and Contact log are flagged as the highest-priority categories for resource-constrained jurisdictions (lines 1153–1167). This is a soft heuristic, not formal weighting.
8. **Financials category is acknowledged as US-centric.** This is relevant for this project's US-state-level application — it suggests FOCAL Financials items will map well to US state disclosures, but international comparison would be complicated.
9. **Health-policy framing.** The paper is published in IJHPM and frames the work in terms of commercial determinants of health (tobacco, alcohol, food). This is upstream motivation; the framework itself is health-agnostic and applies to any lobbying disclosure regime.

# Sunlight Foundation 2015 — State Lobbying Disclosure Scorecard

## 1. Paper

**Citation.** Hahn, Jonah. "How transparent is your state's lobbying disclosure?" Sunlight Foundation, 2015. URL: sunlightfoundation.com.

Companion data: per-state scorecard with letter grade and per-criterion scores in `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`.

**What Sunlight claims to be measuring.** In Sunlight's own framing, this is "a review of legislative requirements for and practical implementation of lobbyist disclosure, not an assessment of the quality of the data's openness" (line 29-31). The work updates a 2011 Sunlight examination by Schuman, Buck, and Dunn that "examined the various aspects of lobbying disclosure at the state level" by "reading legislation about who has to report, when a lobbyist must register, what needs to be included in the necessary forms and how much lobbyists must pay to register" (lines 9-19). The 2015 update specifically emphasizes "lobbyist disclosure requirements" (line 21) and finds that "many states fail to address the legislative flaws that create unfortunate loopholes, do not provide citizens with easily accessible information and navigable websites, and lack stringent transparency policies" (lines 23-26). Sunlight foregrounds two failure modes: (a) "minimum expenditure disclosure thresholds" and (b) lack of "an explicit connection between lobbyist activity and expenditures" (lines 85-87). It also flags lobbyist payroll/compensation disclosure as missing in roughly half the states. The author states explicitly: "Sunlight opposes any type of reporting limit: Any payment, gift or benefit to a politician — small or large — deserves to be publicly available for the sake of accountability" (lines 95-97).

## 2. Methodology

- **Sample.** 50 U.S. states (every state graded). Confirmed against companion CSV which has 50 state rows.
- **Year of data.** 2015 (data collection occurred 2015 per the article date; CSV row for Kansas notes "Kansas chooses not to hold any lobbying data before 2015 on its website" — line 241-242).
- **Data inputs (per Sunlight).** "We relied upon both the legal statutes and data provided on a state's website when determining the grade. We attempted to verify the information with the offices overseeing lobbying disclosure, but we gleaned the rest from the public website" (lines 130-133).
- **Indicators.** 5 criteria, each scored on its own ordinal rubric. The criteria and rubrics are explicit in the article (lines 137-192).
- **Aggregation to grade.** The article does not state the letter-grade cutoffs explicitly. By inspection of the companion CSV, the "Total" column is the simple arithmetic sum of the 5 indicator scores, and the letter grade tracks total ranges. Empirically (from the CSV):
  - A: total ≥ 4 (range 4–6 observed)
  - B: total 2–3
  - C: total 0–1
  - D: total -2 to -1
  - F: total ≤ -3
- **Theoretical score range.** Sum of indicator maxes = 2 + 2 + 0 + 2 + 0 = **6**. Sum of indicator mins = -1 + -1 + -1 + -2 + -1 = **-6**. Both endpoints observed in CSV (Massachusetts and South Carolina at 6; Florida at -6).
- **Inter-coder reliability.** Not reported.
- **Verification.** Sunlight states it "attempted to verify" findings with state offices but "gleaned the rest from the public website" (lines 132-133). One verification interaction is documented narratively (Ohio state employee, lines 67-70).

## 3. Organizing structure

The article organizes the rubric into 5 numbered evaluation criteria, each becoming one indicator:

| # | Criterion (Sunlight's label) | Indicator count |
|---|------------------------------|-----------------|
| 1 | Lobbyist Activity | 1 |
| 2 | Expenditure Transparency | 1 |
| 3 | Expenditure Reporting Thresholds | 1 |
| 4 | Document Accessibility (= "Form Accessibility" in rubric heading) | 1 |
| 5 | Lobbyist Compensation | 1 |
| **Total** | | **5** |

The article also has narrative sections ("Registering a problem", "An expenditure issue", "Miscellaneous observations") that discuss qualitative observations not used in scoring. These are not separate indicators.

## 4. Indicator count and atomization decisions

**Total: 5 indicators, all ordinal.**

**Atomization judgment calls:**

- **Single vs split: Lobbyist Activity.** The Tier 2 descriptor combines two facts ("bill/action discussed and position taken"). I kept this as one ordinal indicator with a 4-tier scale rather than splitting into "bill_disclosure" + "position_disclosure" boolean pair, because Sunlight scored it as a single column in the CSV and structures the rubric as a single ordinal scale.
- **Single vs split: Document Accessibility.** Tier 2 conflates "digital filing" with "digital forms publicly available" — these are conceptually two things. Kept as one indicator because Sunlight scores it on a single ordinal scale.
- **Threshold-as-ordinal.** "Expenditure Reporting Thresholds" is a 2-tier ordinal (effectively boolean: any threshold vs no threshold). Sunlight does *not* score the magnitude of the threshold, despite extensive narrative discussion of dollar amounts ($2, $5, $25, $50). I preserved Sunlight's actual rubric (2-tier) rather than imposing a more granular indicator that the paper does not actually use. Flagged as `notes` in TSV.
- **Indicator-narrative mismatches.** The narrative observation that 18 states require official-name disclosure only when accompanied by an expenditure (lines 102-105), and the discussion of conflicts-of-interest disclosures in Missouri, Alabama, and New Jersey (lines 208-222), are *not* captured in the rubric. They are commentary, not scoring criteria.

## 5. Frameworks cited or reviewed

- **Sunlight Foundation 2011 internal predecessor** — Schuman, Buck, and Dunn (cited line 9-11). The 2015 work is described as "an update of that database."
- **State Integrity** (cited as informational support, line 21).
- **National Institute on Money in State Politics** (cited as informational support, line 22).
- **Sunlight's "Open Data Policy Guidelines"** (cited line 33; said to be applied in a forthcoming companion analysis but not in this scorecard).

No academic framework citations.

## 6. Data sources

Per the "Grading the states on lobbying disclosure" section (lines 128-136):

1. **Legal statutes** of each state (primary).
2. **Data provided on a state's website** (i.e., the state lobbying disclosure portal).
3. **State offices overseeing lobbying disclosure** — used as verification when reachable.

The companion CSV records, for each state, the URL of (a) the state lobbying law and (b) the state disclosure portal — direct evidence that Sunlight read statutes and visited each state portal.

## 7. Notable quirks / open questions

- **Variable tier counts across rubrics, NOT uniform 4-tier.** The task spec stated "Sunlight uses 4-tier verbal-descriptor ordinal scales per indicator." This is incorrect for Sunlight 2015. The actual tier counts are: Lobbyist Activity 4-tier, Expenditure Transparency 4-tier, Expenditure Reporting Thresholds **2-tier**, Document Accessibility **5-tier**, Lobbyist Compensation **2-tier**. I captured tier descriptors verbatim per indicator at whatever count Sunlight actually uses.
- **"Document Accessibility" vs "Form Accessibility" naming inconsistency.** Criterion #4 is labeled "Document Accessibility" in the criteria list (line 150) and CSV header, but the rubric heading reads "Form Accessibility" (line 178). Same indicator, two labels.
- **Document Accessibility -1 vs -2 wording is ambiguous/likely typo.** Tier -1 reads "Public cannot access either the lobbyist registration form or the expenditure report online"; Tier -2 reads "Public cannot access both the lobbyist registration form or the expenditure report online" (lines 184-187). Logically Tier -2 should mean "cannot access either" (i.e., neither is accessible) and Tier -1 should mean "cannot access one of the two." Preserved verbatim; flagged as a likely source typo.
- **Threshold rubric ignores threshold magnitude.** Narrative discusses thresholds from $2 (low) to $50 (Connecticut, Ohio, Virginia) with a $25 average (lines 88-94). The rubric collapses all of these to a single -1 tier. A state with a $2 threshold scores identically to a state with a $50 threshold, despite the article's clear preference.
- **No grade-cutoff documentation in paper text.** Letter-grade cutoffs (A/B/C/D/F) are not specified in the article. Reverse-engineered from the CSV.
- **CSV-vs-paper completeness check (Step 2):**
  - **All 5 indicator columns in the CSV map 1:1 to indicators captured from paper text.** No CSV indicator is missing from the extraction.
  - **No paper-text indicator is missing from the CSV.**
  - **CSV adds non-indicator columns:** "Grade" (the letter grade), "Total" (sum), "State Lobbying Law" (URL), "State Disclosure Portal" (URL). These are output/reference columns, not scoring indicators — correctly excluded from the indicator extraction.
  - **CSV contains undocumented footnote markers** on score values: `*` (e.g., "1*"), `**`, `***`, `^`, `^^`. The paper text does not define these markers. They likely encode state-specific exceptions or qualifications that Sunlight surfaced for individual states, but with no key/legend in the article text, their meaning cannot be extracted. Flagged as a discrepancy.
- **Narrative content not in the rubric.** Several substantive observations in the article are *not* scored: (a) whether registration forms are public at all (six states withhold them entirely, lines 55-56), (b) login-wall barriers to public access (line 65-67), (c) whether lobbyists must name officials/bills only when there's an expenditure (lines 98-105), (d) gift-giving rules (Oklahoma, lines 196-208), (e) conflict-of-interest disclosure (Missouri, Alabama, New Jersey, lines 208-222), (f) machine-readable / bulk-downloadable data (line 242-244), (g) fees to access reports (Wyoming, line 237-238). These are scope-implicit limitations of the rubric, not indicators.

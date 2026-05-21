# CPI 2007 — "Hired Guns" Methodology — Indicator Extraction

## 1. Paper

**Citation.** Center for Public Integrity. *Hired Guns: Methodology.* 2007. Publisher URL: `https://publicintegrity.org/politics/state-politics/influence/hired-guns/methodology-5/`. On-disk source: `papers/text/CPI_2007__hired_guns_methodology.txt`.

**What CPI claims to be measuring (in CPI's own framing).** "'Hired Guns' is an analysis of lobby disclosure laws in all 50 states. The Center for Public Integrity created a ranking system that assigns a score to each state based on a survey containing a series of questions regarding state lobby disclosure" (line 6). "The questions addressed eight key areas of disclosure for state lobbyists and the organizations that put them to work: Deﬁnition of Lobbyist, Individual Registration, Individual Spending Disclosure, Employer Spending Disclosure, Electronic Filing, Public Access, Enforcement, Revolving Door Provision" (lines 10-14). The "answers with the highest values reward full disclosure, public access and accountability" (line 16).

## 2. Methodology

**Sample.** "all 50 states" (line 7).

**Year(s) of data.** Per Q35-Q37 the reference year for spending totals is **2002** ("States providing an overall, aggregate total of all lobby spending for 2002 received full points," lines 378, 384). Methodology document itself dated 2007 (publication year of the analysis cycle being captured here).

**Total point system and grade mapping.** "The maximum number of points a state could receive was 100" (line 17). "Because only one state scored an 80 or above, scores of 70 and higher are considered relatively satisfactory. Scores of 60 to 69 are considered marginal. Scores below 60 are considered failing" (lines 28-30). CPI does not specify A/B/C/D/F letter grades in the methodology text — it specifies relative bands (≥70 satisfactory; 60-69 marginal; <60 failing).

**Composite scoring rule.** Sum of points across all 48 questions. Per-category maxima sum to 100: Definition of Lobbyist 7 + Individual Registration 19 + Individual Spending Disclosure 29 + Employer Spending Disclosure 5 + Electronic Filing 3 + Public Access 20 + Enforcement 15 + Revolving Door Provision 2 = 100. Each question has a multiple-choice answer set with a numerical value attached; highest-disclosure answer = highest points.

**Conditional / cascade logic.** Itemization-detail questions Q16, Q17, Q18, Q19 are explicitly conditioned on Q15: "If spending is not required to be itemized, a state received no points" (lines 187-188, 194-195, 200-201, 211-212). For Q31 and Q32 the rule is highest-applies: "this question was answered by choosing the item with the highest point value that applies" (lines 320-321, 341-342).

**Inter-coder reliability.** Not reported in the methodology document.

## 3. Organizing structure

CPI's eight categories, exactly as labeled in the source, with question counts and point maxima as stated by CPI:

| Category | Questions | Point max |
|---|---|---|
| Deﬁnition of Lobbyist | Q1–Q2 (2 items) | 7 |
| Individual Registration | Q3–Q10 (8 items) | 19 |
| Individual Spending Disclosure | Q11–Q25 (15 items) | 29 |
| Employer Spending Disclosure | Q26–Q27 (2 items) | 5 |
| Electronic Filing | Q28–Q30 (3 items) | 3 |
| Public Access | Q31–Q38 (8 items) | 20 |
| Enforcement | Q39–Q47 (9 items) | 15 |
| Revolving Door Provision | Q48 (1 item) | 2 |
| **Total** | **48** | **100** |

**Confirmation vs. FOCAL's secondary count.** FOCAL's claim of 8 categories / 48 items is **exactly correct.** All eight category labels in FOCAL's description match CPI's source labels verbatim. Question count by category likewise matches: 2 + 8 + 15 + 2 + 3 + 8 + 9 + 1 = 48. Point maxima sum to CPI's stated 100.

## 4. Indicator count and atomization decisions

**Total rows in TSV: 48.**

**Atomization choices.**

- **One row per CPI question.** CPI numbers items Q1 through Q48; each is captured as a single row.
- **No subpart splitting.** No CPI question has labeled subparts (Q3a, Q3b, etc.). All 48 are atomic in the source.
- **Composite items kept as single rows even where the answer set is multidimensional.** Q24 (campaign contributions) is the most complex case: the answer set crosses (allowed-vs-prohibited) × (disclosed-vs-not) × (during-session-vs-not), producing 5 labeled levels with only 3 distinct point values (0/1/2). Kept as one row because CPI scores it as one question; the multidimensional structure is recorded in `scoring_rule` and called out in `notes`.
- **Conditional items kept as their own rows.** Q16-Q19 each depend on Q15's answer (no points if itemization not required). Captured individually with the conditional flagged in `notes`. Not collapsed into Q15.
- **Q23 (gifts) kept as a single ordinal item** despite mixing report-vs-prohibit-vs-limit semantics; CPI scores them on a single 0-1-2-3 ordinal scale.
- **Q31 and Q32 ("highest-applies" ladders).** Each captured as a single ordinal item; the `scoring_rule` records the 4-level ladder and `notes` records the highest-applies aggregation rule.

No row was created beyond what CPI itself enumerates. No row was merged from what CPI enumerates separately.

## 5. Frameworks cited or reviewed

The methodology document cites **no other rubric or framework by name.** It does not reference predecessor scoring systems (no PRI, no Common Cause, no NCSL framework reference, no academic citation). The methodology stands alone as CPI's own construction.

- **Rubric citations:** none.
- **Theoretical / methodological citations:** none in the methodology text.

## 6. Data sources

**Per-question data acquisition** (CPI's own description, line 19-23): "Center researchers developed 48 questions, and sought answers for them by studying statutes and interviewing ofﬁcials in charge of lobbying agencies in each state. Most questions required the researchers to ﬁnd the information in the state statute and then use public ofﬁcials for conﬁrmation."

**Primary source:** state lobbying statutes, read directly by CPI researchers.

**Confirmation/fallback source:** state oversight agency officials (interview).

**Items whose operational definition relies primarily on the fallback (interview) source:**

- **Q35, Q36, Q37** (state agency provides aggregate spending totals): scored on whether the agency provides totals "via the Web site or upon request" — fact-of-availability often requires asking the agency.
- **Q40** (mandatory reviews/audits): action-based, not statute-based — requires agency self-report on practice.
- **Q43** (last time penalty levied for late spending report): "According to a representative of the state oversight agency, when did the agency last levy a penalty…" (line 444). Self-report only.
- **Q46** (last time penalty levied for incomplete spending report): same self-report mechanism, line 474. Includes an "agency does not accept incomplete filings" bucket merged into the top tier.

These four (Q40, Q43, Q46, plus the public-access aggregate-total trio Q35-Q37) are the items where statute-only scoring is not sufficient and a state-agency interview is load-bearing.

## 7. Notable quirks / open questions

- **Q34 contains a typo in the CPI source.** "Are sample registration forms/spending reports available the Web?" (line 369) is missing the word "on." Captured verbatim in TSV.
- **Q24 has 5 labeled levels but only 3 distinct point values.** The "during session" vs. "allowed" distinction inside the "disclosed" branch does not change the point value (both are 1 point). The "during session" / "allowed" distinction inside the "not disclosed" branch likewise does not matter (both are 0 points). The labels carry information that the score does not — a quirk worth flagging if downstream consumers expect category labels and points to be biject.
- **Q38 has no 0-point option in the visible scale.** Scale starts at "Semi-annually or less often – 1 point" (line 399). Either CPI assumes every state updates at least semi-annually, or a state with no updates at all gets an unspecified 0. Source is silent on the floor case.
- **Q23 (gifts) "without a signiﬁcant amount of exceptions" rule.** "States prohibiting lobbyists from giving gifts to legislators, without a signiﬁcant amount of exceptions, received full points" (lines 245-247). What counts as "significant" is not operationalized — a coder judgment call.
- **Q48 only scores existence of cooling-off period, not length.** A 6-month and 5-year cooling-off period score identically. May matter for downstream comparison frameworks that score cooling-off duration.
- **Q21 and Q22 lean on state-specific definitions.** "States have different deﬁnitions about business associations, but they will either require or not require the lobbyist to disclose those relationships" (lines 230-232). CPI accepts whatever the state defines as "household member" or "business association"; these are scope-implicit items.
- **Categories of differing weight.** Individual Spending Disclosure (29 pts) and Public Access (20 pts) dominate the 100-point total; Revolving Door (2 pts) and Electronic Filing (3 pts) are nearly token. This means the composite is heavily disclosure-and-access-weighted; the "revolving door" and "e-filing" categories cannot meaningfully move a state's grade.
- **Conditional cascade on Q15.** A state that does not require itemization gets 0 on Q16-Q19 even if it has well-developed reporting in other dimensions. This creates a 4-point penalty cluster for non-itemizing states beyond the Q15 score itself.
- **No reliability or validation reporting.** Document does not describe inter-coder agreement, double-coding, or error-correction process.

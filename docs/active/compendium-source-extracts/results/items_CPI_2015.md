# CPI 2015 — State Integrity Investigation (Kusnetz overview article + landing page)

## 1. Paper

**Citation:** Kusnetz, Nicholas. "Only three states score higher than D+ in State Integrity Investigation; 11 flunk." Center for Public Integrity, November 9, 2015 (updated November 23, 2015, 11:00 a.m.). Joint project of the Center for Public Integrity and Global Integrity.

**Local sources used (no PDF or .txt extraction was present at the paths given in the prompt; only HTML archives were available, so they were converted to text in `/tmp/sii_article.txt` and `/tmp/sii_landing.txt` for analysis):**

- `papers/CPI_2015__sii_only_three_states.html` (1525 lines of HTML; 561-line text extraction)
- `papers/CPI_2015__sii_2015_landing.html` (1557 lines of HTML; 565-line text extraction)
- No `papers/CPI_2015__sii_only_three_states.txt` and no `papers/CPI_2015__sii_only_three_states.pdf` exist in this worktree, despite the prompt referencing them. Flagged.

**Framing of SII overall.** The State Integrity Investigation is a "data-driven assessment of state government" producing "transparency and accountability grades for all 50 states." It deliberately does **not** measure corruption itself: "Unlike many other examinations of the issue, the project does not attempt to measure corruption itself" — it measures "the systems that state governments use to prevent corruption and expose it when it does occur." The 2015 round is the second iteration; the first ran in 2011-2012.

**Framing of the lobbying-disclosure component.** Lobbying disclosure is one of 13 categories (the eleventh, by article order). The article does **not** enumerate the lobbying-disclosure questions. It instead uses lobbying-related anecdotes (Arkansas $50/Idaho gift loopholes, Tennessee Ethics Commission inaction against a lobbyist, Kansas budget director emailing lobbyists) to illustrate the broader integrity story. Substantive lobbying disclosure indicators are not visible in this article alone.

## 2. Methodology

What the article reveals:

- **Question count:** "The 2015 grades are based on **245 questions** that ask about key indicators of transparency and accountability."
- **Dual-prong scoring:** questions probe "not only at what the laws say, but also how well they're enforced or implemented" (i.e., de jure + de facto, the same in-law/in-practice split that ran through CPI Hired Guns 2007 and Global Integrity's broader methodology).
- **Indicator structure:** indicators are grouped into 13 categories (verbatim list in §3 below).
- **Coding labor:** "Experienced journalists in each state undertook exhaustive research and reporting to score each of the questions." Reporters credited per state on the 2015 reporters page (https://publicintegrity.org/2015/10/14/18317/state-integrity-2015-reporters).
- **Scoring rollup:** 1-100 numeric per question (implied by "perfect score" language and by "score" framing throughout); aggregated to **letter grades** (A through F) at both the category level and the state level. "The best grade in the nation, which went to Alaska, is just a C."
- **What the article does NOT specify:** the exact within-question scoring rubrics (point allocations between law/practice components), the question-to-category mapping, the category weighting in the overall grade, or how the 245 questions distribute across the 13 categories.

## 3. Organizing structure

**Verbatim list of the 13 categories** (single sentence in the article, ordered as written):

> "The 'indicators' are divided into 13 categories: **public access to information, political financing, electoral oversight, executive accountability, legislative accountability, judicial accountability, state budget processes, state civil service management, procurement, internal auditing, lobbying disclosure, state pension fund management and ethics enforcement agencies.**"

The lobbying-disclosure category is the 11th in article order. It is presumably the SII 2015 home for what CPI Hired Guns 2007 spread across registration, employer reporting, expenditure reporting, and related areas. The article gives no further structure within the lobbying-disclosure category — no sub-headings, no question count for that category, no scoring rubric.

A 14th cross-cutting layer was added in 2015: **open-data questions** were inserted into "each category." These are the strongest single driver of the overall score decline relative to 2012.

## 4. Indicator count and atomization decisions

**Critical caveat: the article does not enumerate the 245 questions.** It paraphrases exactly two:

1. **Q_LA1 (Legislative accountability example):** "whether lawmakers are required to file financial interest disclosures, and also whether they are complete and detailed" — used as an illustrative example, not verbatim wording. Bundles de jure ("are required to file") + de facto ("complete and detailed") into a single composite indicator.
2. **Q_AI1 (Public access to information example):** "whether citizens actually receive responses to their requests swiftly and at reasonable cost" — pure de facto / in-practice, surfaced because Missouri was the only state with a perfect score on it.

Plus the **open-data layer** (Q_OD): described as a set of category-specific questions added in each of the 13 categories. The article treats them collectively rather than individually, so we cannot enumerate them — there is at least one per category (so >=13 distinct open-data questions), but the exact count and wording are not in the article.

**Atomization decisions in `items_CPI_2015.tsv`:**

- 13 rows (`C01`–`C13`) for the verbatim category labels — the only fully visible level of the framework's structure.
- 2 rows (`Q_LA1`, `Q_AI1`) for the two paraphrased example questions, kept atomic with the de jure/de facto components folded in (matching how the article presents them).
- 1 row (`Q_OD`) for the open-data layer, treated as a placeholder for >=13 questions whose specific wording is not in our local sources.
- **Total: 16 rows. The remaining ~229 of the 245 questions are not extractable from the available sources.**

## 5. Frameworks cited or reviewed

Names only, surfaced in the article and landing page:

- **Global Integrity** — joint partner on the SII (and its global Africa/Asia/EU integrity-assessment work is the heritage methodology).
- **Center for Public Integrity (CPI)** — the publishing partner; also conducted the predecessor CPI Hired Guns 2007 lobbying-only study.
- **Sunlight Foundation** — Global Integrity "consulted with the Sunlight Foundation when writing the open data questions for this project" (per John Wonderlich, Sunlight policy director).
- **Common Cause** — quoted (Jenny Rose Flanagan, VP for state operations) for context, not as a methodology source.
- **Center for Governmental Studies** (defunct 2011) — quoted (Robert Stern, former president) for context.
- **Citizens Union** — cited for a count of NY ethical-misconduct departures.

No prior academic framework (e.g., Newmark, Opheim, PRI 2010) is cited or compared in the visible material.

## 6. Data sources

Per-state coding pattern (gleaned from the article):

- **In-state journalists** as principal coders, one per state, recruited and credited publicly. Landing page archive lists per-state authors of state-grade articles (e.g., Arizona — Evan Wyloge; Maine — Dave Sherwood; Mississippi — Anna Wolfe; Iowa — Lauren Mills; Maryland — Miranda Spivack; etc.) — these are the SII 2015 reporters.
- **Statute review** is implied by "looking not only at what the laws say."
- **Agency interviews** are implied by direct quotes from officials in the article (Kansas Governmental Ethics Commission director Carol Williams; Tennessee Bureau of Ethics director Drew Rawlins; Oklahoma Ethics Commission director Lee Slater; Massachusetts State Police spokesman; etc.).
- **Document review** (audit reports, news reports, ballot measures, ethics-commission complaint files) supports both the de jure and de facto scoring.
- This pattern matches Hired Guns 2007's "in-state lawyer or journalist + statute review" approach but expands the data source diet to include published audits and prosecutorial reports.

## 7. Notable quirks / open questions

**Notable quirks visible in the article:**

- **Open-data shock.** The 2015 round is not directly comparable to 2012 because open-data questions were added across all 13 categories. The article explicitly attributes most of the score decline vs. 2012 to this methodological change, not to actual deterioration. This means SII 2015 ≠ SII 2012 even though both produce 50-state letter grades.
- **No corruption proxy.** SII deliberately measures *systems*, not outcomes. State scandal counts (e.g., NY's 14 lawmakers ousted) are reported as context but do not enter the grade.
- **Letter grades from numeric questions.** The article does not specify the numeric-to-letter cutoffs nor how question scores aggregate to a category letter grade.
- **Composite question scoring.** The Q_LA1 example bundles "required to file" + "complete and detailed" into one question. This is a different atomization choice than Hired Guns 2007, which would split those into separate questions. Whether SII 2015 in general uses fewer-but-fatter composite questions vs. Hired Guns 2007's atomic boolean/ordinal questions is not resolvable from this article alone.
- **No dedicated lobbying-disclosure narrative.** Despite lobbying being one of 13 categories, the article never reports a top/bottom state for lobbying disclosure, never gives a category-wide pass-rate, and never lists any of the lobbying-disclosure questions. Lobbying appears only in anecdotes and is folded into legislative-accountability and ethics-enforcement narratives.

**Open questions / gaps requiring source retrieval before SII 2015 can be fully integrated into compendium-2.0:**

1. **The full 245-question methodology.** Not in our local archive. URL referenced in the article: `https://publicintegrity.org/accountability/state-integrity-investigation/state-integrity-2015` and the parent landing `https://publicintegrity.org/accountability/state-integrity-investigation/`. The methodology is reportedly published with question-level wording and per-state scores.
2. **The lobbying-disclosure subset specifically.** Without the methodology page, we cannot know how many of the 245 questions sit in the lobbying-disclosure category, what they ask, or how scoring is allocated within them.
3. **Per-state per-question scores.** CPI made a 50-state interactive available (`https://publicintegrity.org/2015/11/03/18822/how-does-your-state-rank-integrity`); whether the underlying question-level data is downloadable as a flat file (CSV) is unknown from the article alone.
4. **Question-category mapping.** Whether the 245 questions distribute evenly across 13 categories (~19 each) or unevenly is not stated.
5. **Open-data sub-questions.** At least one per category (so >=13 questions added in 2015), but the exact count, wording, and scoring rubric are not in our archive.
6. **Overlap with Hired Guns 2007.** The article does not state whether SII 2015's lobbying-disclosure questions are a literal carry-over of Hired Guns Q1-Q48, an expanded successor, or an independent re-design. The methodology page should resolve this.

**Recommendation for compendium-2.0:** The 13 verbatim category labels and the two paraphrased example questions are the only items that can be honestly extracted from the article + landing page. Treat SII 2015 as **partially captured** in the compendium until the full methodology page (or its archive.org snapshot) is retrieved. Until then, do not claim 245-item coverage from this paper.

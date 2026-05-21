# Kim 2018 — LobbyView: Firm-level Lobbying & Congressional Bills Database

## 1. Paper

**Citation.** Kim, In Song. 2018. *LobbyView: Firm-level Lobbying & Congressional Bills Database.* Working paper, MIT Department of Political Science, August 30, 2018. URL: http://web.mit.edu/insong/www/pdf/lobbyview.pdf. Financial support: NSF SES-1264090, SES-1725235.

**Framing — and an important caveat for this extraction.** This is a **federal LDA data-infrastructure paper**, not a state-level lobbying-disclosure rubric. There are **no scored evaluation items** here. LobbyView is "a comprehensive lobbying database that is based on the universe of lobbying reports filed under the Lobbying Disclosure Act of 1995" (lines 9-10) whose central contribution is bridging "two distinct observable political behaviors with regard to congressional bills: (1) sponsorship by politicians, and (2) reported lobbying by interest groups" (lines 11-12).

Per the task brief, the "items" extracted here are therefore **the data fields LobbyView exposes**, distinguishing fields that come directly from LDA filings (i.e., the raw input, replicable in principle from any analogous state-level disclosure regime) from **enrichments that LobbyView adds on top** (bill-linking, full-text indices, firm-name disambiguation, NAICS/Compustat merges, Herfindahl indices, the API). The relevance for `lobby_analysis` is the second set — those enrichments are what would need to exist on top of state disclosure data to deliver "LobbyView-equivalent infrastructure" at state level.

**Caveat from the paper itself.** The paper is explicitly a partial draft: "This document currently contains only some technical details of the database. We will soon update this paper to provide a full description of the methods used for constructing the database. Specifically, we will show 1) how we disambiguate interest group names using natural language processing (NLP) as well as collaborative filtering, 2) how the complex relational structure is stored using PostgreSQL and Elasticsearch, and 3) the scalability of our methods for bill number and bill title matching" (lines 23-29). Substantive descriptive/statistical analyses are forward-promised but absent. Companion papers cited for substance: Kim 2017 *APSR* and Kim & Kunisky 2018 (network).

## 2. Methodology

LobbyView ingests the **universe of LDA reports** (federal lobbying disclosures filed under the 1995 Act) and joins them to **congressional bills**. The core methodological contribution sketched in this draft is **bill identification within lobbying reports** — non-trivial because bill numbers are repeated across Congresses and are typically not annotated with their Congress number in lobbying reports.

The bill-identification pipeline has five steps (§2 of the paper):

1. **Bill Number Search.** Regular-expression scan of report text for canonical bill identifiers (e.g., `H.R. 2577`, `S. 1207`).
2. **Congress Identification.** For each bill number found, retrieve same-numbered bills from a candidate range of Congresses (default = three preceding Congresses including the report-year Congress); compute a bag-of-words representation `v_i` of each candidate bill (after tokenization + stopword filtering), and a bag-of-words representation `w` of the report text around the bill mention; choose the Congress by `argmax_i (v_i^T w) / (||v_i|| ||w||)` (lines 71-76). Fallback: if no same-numbered bill exists in the candidate range, default to the report-year Congress.
3. **Congress Propagation.** "If we successfully find a match for a Congress, it may be propagated to the other bills mentioned in the lobbying report, since, being scheduled on a quarterly basis, lobbying report will almost always only mention legislation from a single Congress. If different bills in a lobbying report disagree on the best-matching Congress, a majority vote may be taken, but this rarely occurs in practice" (lines 79-83).
4. **Bill Title Search.** Tokenize the report's specific-issue sections; text-match against a bill-titles table to catch bills referenced by name only (e.g., "Safe Data Act" without the H.R. number).
5. **Bill Range Expansion.** When a report writes a range (e.g., "H.R. 4182-4186"), expand to all integers in between, gated by same-prefix and gap ≤ 10.

**Worked example used in the paper.** A 2013 Google report mentions H.R. 2577 (the SAFE Data Act). Naive year→Congress mapping would assign H.R. 2577 to the 113th Congress; in fact it belongs to the 112th. The cosine-similarity step resolves this correctly (lines 49-52).

**Storage / indexing.** This draft documents the SQLite + Whoosh implementation in `/trade/code/database` (with SQLAlchemy + Elixir as the ORM layer, BeautifulSoup for parsing, NLTK for tokenization/stopwords). The forward-promised production system is **PostgreSQL + Elasticsearch** (lines 26-27). The paper does not describe the LDA-ingest pipeline itself in this draft.

**Firm-level disambiguation** is named as a load-bearing feature ("standardized firm- and industry-level identifiers", lines 12-13) but the *method* is forward-promised — "natural language processing (NLP) as well as collaborative filtering" (lines 24-26) — not described in this draft.

**Industry / firm financial enrichment.** A separate `lobby/code/hfcc` module joins firm-level lobbying records to **Compustat** financials and computes per-industry **Herfindahl–Hirschman indices**, with NAICS2 (or SIC) as the industry-grouping variable. Output: one CSV per year per classification system; the example invocation runs `1996–2011` (lines 320-322), giving an empirical lower bound on data coverage in the version described.

## 3. Organizing structure

LobbyView's data schema, as documented in this draft, is organized into three model directories under `/trade/code/database`:

| Module | Class / table | Role |
|--------|---------------|------|
| `bills/` | `Bill` | Congressional bill (PK = `{congress}_{billnumber}`, e.g., `110_HR7311`); has `introduced` (date), `summary` (CRS text); one-to-many to `BillTitle`; many-to-many to `Term` |
| `bills/` | `BillTitle` | Bill title strings (one bill → many titles) |
| `bills/` | `Term` | Subject-matter term (likely CRS terms); many-to-many with Bill |
| `lda/` | `LobbyingReport` | Quarterly LDA report (filterable by `year`, etc.); many-to-many to `LobbyingIssue`; contains `LobbyingSpecificIssue` text |
| `lda/` | `LobbyingIssue` | Standardized LDA issue codes (e.g., `'TRADE (DOMESTIC/FOREIGN)'`) |
| `lda/` | `LobbyingSpecificIssue` | Free-text narrative section of a lobbying report describing what was lobbied; full-text indexed |
| `firms/` | (firm models) | Standardized firm- and industry-level identifiers (disambiguation method forward-promised) |

**Inter-table relationships.** Examples shown in §5.2: `OneToMany('BillTitle')` from `Bill` to titles; reverse `ManyToOne('Bill')` from `BillTitle`; `ManyToMany('Term')` symmetric. The paper provides query examples — `LobbyingReport.query.filter_by(year=2011)` and the trade-issue filter that returns 52,418 reports.

**Two cross-cutting indices** (Whoosh):
- Bill CRS summary text — accessed via `bills/ix_utils.py:summary_search`
- Lobbying-report specific-issue text — accessed via `lda/ix_utils.py:issue_search` (and the helper `get_bill_specific_issues_by_titles` used during construction to bind report→bill via title text)

Both indices support phrase queries (`make_phrase=True`) — important to avoid bag-of-words false positives like "uruguay round" matching "uruguay" + "round" separately (lines 290-293).

**Industry / firm-level outputs (`hfcc/`)**: row-per-firm CSVs with NAICS2 industry, industry Herfindahl, firm-level lobbying summary, optional Compustat financial fields, and a derived `lobbied on at least one trade issue` flag.

## 4. Indicator count and atomization decisions

**Total: 18 data-field rows** in the TSV. These are not evaluation items; they are the data fields LobbyView exposes (or builds). The 18 cluster into four groups:

| Group | Rows | Origin |
|-------|------|--------|
| LDA-direct fields (raw federal disclosure inputs) | 4 | `lobbying_report`, `lobbying_specific_issue`, `lobbying_issue_code`, `report_filing_year` |
| Congressional-data fields (external — Congress.gov / CRS) | 5 | `bill`, `bill_introduced_date`, `bill_crs_summary`, `bill_title`, `bill_term` |
| LobbyView-added enrichments (the value-add) | 7 | `bill_lobbying_link`, `congress_disambiguation_score`, `firm`, `industry_naics`, `firm_financials` (Compustat merge), `industry_herfindahl`, `firm_trade_lobbying_indicator` |
| Infrastructure layers | 2 | `api_bulk_download`, `full_text_index` |

**Atomization judgment calls.**

- **Bill-detection pipeline kept as one row.** The five steps (regex bill numbers, cosine similarity, propagation, title matching, range expansion) jointly produce one logical edge — `bill_lobbying_link` — between a lobbying report (or specific-issue section) and one or more bills. The cosine-similarity step is split out as a separately-named row (`congress_disambiguation_score`) because it is a quantitatively scored intermediate, but the other four steps are folded into the link's `notes`.
- **`bill_term` kept distinct from `lobbying_issue_code`.** Both are categorical taxonomies, but they are different schemas: CRS subject terms classify *bills*; LDA issue codes classify *lobbying reports*. Kept separate.
- **Firm financial fields not enumerated individually.** The paper says only "firm-level compustat financial data" without listing which Compustat columns. Captured as one row (`firm_financials`) with the open question flagged.
- **Firm name disambiguation absent from this row set.** The paper says "we will show how we disambiguate interest group names" — this is forward-promised, not described. The `firm` row covers the existence of the standardized identifier; the *method* by which it is computed is not extractable from this draft.
- **Infrastructure rows included.** The full-text index and the bulk-download API are not "fields" per se but are load-bearing parts of what LobbyView delivers (and would need to be replicated at state level), so they are captured as `infrastructure` rows.
- **No scoring rules.** Every row's `scoring_rule` is `N/A` because none of these are scored indicators. The `indicator_type` column is repurposed to describe field type (`entity_table`, `categorical`, `free_text`, `numeric`, `datetime`, `boolean`, `derived_link`, `derived_score`, `infrastructure`).

## 5. Frameworks cited or reviewed

The paper cites **two companion works** (the "References" block at lines 31-36) and no other rubrics or frameworks:

- Kim, In Song. 2017. "Political Cleavages within Industry: Firm-level Lobbying for Trade Liberalization." *American Political Science Review* 111(1): 1–20.
- Kim, In Song, and Dmitriy Kunisky. 2018. "Mapping Political Communities: A Statistical Analysis of Lobbying Networks in Legislative Politics." Working paper, http://web.mit.edu/insong/www/pdf/network.pdf.

The only legal/regulatory reference is to the **Lobbying Disclosure Act of 1995** (line 10) — the data input, not a rubric. No state-level disclosure framework, no Public Integrity Index, no Sunlight Foundation work, no NCSL/NASS reference, no academic survey of disclosure rubrics is cited or reviewed.

## 6. Data sources

LobbyView combines four data sources (per this draft):

1. **LDA filings (federal).** "the universe of lobbying reports filed under the Lobbying Disclosure Act of 1995" (lines 9-10). Year coverage not explicitly stated in this draft; the Mattel example dates to 2002, the Google example to 2013, and the Herfindahl example invocation runs `1996–2011`, suggesting at least 1996-onward and likely through to the paper's 2018 date.
2. **Congressional bills (Congress.gov / CRS).** Bill records (`Bill` table) including introduction date, CRS summary text, titles, and CRS subject-matter terms. The data source is not explicitly named in this draft, but the use of CRS summaries (`b.summary` is the CRS summary, line 207) implies CRS as the source.
3. **Compustat (firm financials).** Joined onto firm records via the `hfcc.herfindadd` script. The merge key is the LobbyView firm identifier; presumably uses CIK or ticker/Compustat firm IDs internally.
4. **NAICS / SIC industry classifications.** Used for grouping firms in Herfindahl computation. NAICS2 default; SIC available.

No surveys, no manual coding of disclosures, no auxiliary administrative data are mentioned.

## 7. Notable quirks / open questions

### The federal-vs-state gap (load-bearing for `lobby_analysis`)

The brief asks: **what is the gap between LobbyView at federal level and what would need to exist at state level?** This is the central question, so it gets full treatment.

LobbyView leans hard on properties that are **federally true but not state-true**:

- **Universal mandatory federal disclosure regime.** The LDA gives a *single* federal statute defining what gets disclosed, in what format, by whom, when. There is no 50-state equivalent. Each state defines its own thresholds, formats, cadences, and exemptions; some require almost nothing. The state-level pipeline must therefore either (a) ingest 50 heterogeneous schemas and harmonize them into a common entity model — non-trivial because some states' raw fields literally have no analog in others — or (b) compute a least-common-denominator schema that excludes meaningful information from the better-disclosing states. Neither is what LobbyView did at federal level; it inherited a uniform schema for free.
- **Standard bill-identifier conventions.** LobbyView's regex `H.R. ####` / `S. ####` works because federal bill numbering is canonical. State bill numbering is fragmented (HB / SB / SF / HF / AB / SCR / HCR / etc.) and varies by chamber and state, and the practice of *referring* to bills in lobbying reports varies by state. The 5-step bill-detection pipeline would need to be re-derived per-state (or per-state-family) — and the cosine-similarity Congress disambiguation has no state analog because states do not have multi-year sessions in the same way Congress does (though they do have biennial sessions with carryover bills, and special sessions, which create their own ambiguities).
- **A complete public bill database with CRS summaries.** Federal bill text + CRS summaries + standardized subject terms are public, complete, and stable. State bill metadata varies dramatically in completeness and machine-accessibility; some states have well-structured legislative-information systems (LIS), others do not. The bill-side of the join is therefore much weaker at state level. (OpenStates is the closest aggregator, but coverage and metadata-richness vary by state.)
- **Quarterly cadence and "single-Congress" simplifying assumption.** Step 3 (Congress Propagation) leans on "lobbying report will almost always only mention legislation from a single Congress" because federal reports are quarterly. State disclosure cadences range from monthly (when in session) to annually; the equivalent simplifying assumption would be report-mentions-single-session, which holds for annual reports but partially fails for biennial-session states with carryover.
- **A stable firm-level identifier ecosystem.** LobbyView's firm-disambiguation feeds into NAICS/Compustat merges. This works at federal level because the lobbying entities are (overwhelmingly) large registered companies traceable to securities filings. At state level, lobbying clients include far more local non-profits, municipalities, professional associations, ad-hoc coalitions — entities outside the SEC-traceable universe, for which Compustat-style enrichment is unavailable.

**What a state-level "LobbyView-equivalent" would therefore need to add or solve:**

1. **A 50-state schema-harmonization layer.** Map each state's disclosure fields onto a common entity model (registrant, client, lobbyist, report, expenditure, issue, target). Document state-by-state coverage gaps explicitly (which states report compensation, which report bill-level activity, etc.). LobbyView did not need this.
2. **A per-state bill-identifier regex catalog and matching pipeline.** Generalize step 1 of the bill-detection pipeline to handle state bill formats. Replace the 3-Congress cosine-similarity disambiguation with state-session disambiguation appropriate to each state's session structure.
3. **A state legislative-information ingestion layer.** OpenStates as primary; state LIS as fallback. Bill metadata richness will be lower than CRS — no CRS-summary equivalent in most states, weaker subject-term taxonomy.
4. **A non-corporate firm enrichment story.** Compustat covers public corporations; state lobbying clients include far more entities outside that universe. A state pipeline would need an alternative enrichment path (501(c) tax filings? Secretary-of-State business registrations?) — or accept much sparser firm-level features.
5. **State-by-state coverage caveats baked into every output.** Because state regimes vary, every aggregate statistic needs a "which states are included" denominator. LobbyView did not need this — federal coverage is the universe.

### Other quirks within the paper itself

- **The paper is a partial draft.** Substantive descriptive analyses, the firm-disambiguation method, the production PostgreSQL/Elasticsearch architecture, and bill-matching scalability discussion are all forward-promised. What we have is the bill-detection pipeline (§2) and a code walkthrough (§§3–5).
- **Year coverage not explicitly stated.** Inferred to be at least 1996-onward from the Herfindahl example (`-s 1996 -e 2011`) and the Mattel 2002 example. Whether the database covers the full 1995-onward LDA universe in the version-of-record is not in the text.
- **No accuracy / precision metrics for the bill-detection pipeline.** The paper describes the algorithm but reports no precision/recall/F1 numbers on a labeled subset. This is forward-promised ("we will conduct several descriptive and statistical analyses to demonstrate the scope and quality of the lobbying database", lines 28-29).
- **The cosine-similarity step has a known failure mode.** "If no bill having the same number exists in the entire range of Congresses we consider, we simply guess that the bill comes from the Congress of the year the lobbying report was filed" (lines 77-78). This is a silent fallback whose error rate is not characterized.
- **Whoosh + SQLite is described as the current implementation.** The forward direction is PostgreSQL + Elasticsearch. So the technical-details section is at risk of being out-of-date relative to the production database researchers actually query.
- **"At least one trade issue" indicator is project-specific.** The Herfindahl/herfindadd module is built around trade-issue research. This reflects Kim's own substantive focus (trade liberalization, per Kim 2017 APSR) and is not a generic LobbyView feature — at state level, the analogous derived flags would be substantively different.
- **Open question: is firm name disambiguation production-quality?** The forward-promised "NLP + collaborative filtering" disambiguation is the load-bearing feature for any cross-firm or cross-time analysis. Not having a description of the method (or its evaluation) in the paper is a meaningful gap for anyone evaluating LobbyView reliability.

# ALTER-EU 2013 — Recommendations for Transparency Register Review: Lobby Disclosure Requirements

## 1. Paper

**Citation.** ALTER-EU (Alliance for Lobbying Transparency and Ethics Regulation). 2013. *ALTER-EU recommendations for Transparency Register review: Lobby disclosure requirements.* Companion submission to the June 2013 ALTER-EU report *Rescue the Register! How to make EU lobby transparency credible and reliable* (cited in footnote 1, lines 46–48 of the source text). Original URL: https://www.alter-eu.org/sites/default/files/documents/recommendations%20disclosure%20requirements.pdf

**Framing.** A short (≈97-line) policy-recommendations document submitted into the EU's 2013 review of the Joint Transparency Register operated by the European Parliament and European Commission. The document opens (lines 6–12):

> "ALTER-EU's June 2013 report 'Rescue the Register! How to make EU lobby transparency credible and reliable' contains detailed recommendations for the review of the Transparency Register, including on the question which data lobbyists should provide. The report shows clearly that the current register does not provide a comprehensive and reliable picture of who is lobbying, with what budgets, on which issues and on whose behalf. Part of the solution to this is upgraded disclosure requirements and stronger enforcement, including the following reforms:"

The document is a **prose recommendations submission**, not a scoring rubric or measurement framework. ALTER-EU is a coalition of (at the time) ~200 civil-society groups, trade unions, and academics advocating for stricter EU lobbying rules. The document targets **disclosure-requirement reform of the EU Transparency Register specifically**, in the context of the 2013 review.

## 2. Methodology

The document does not describe its methodology explicitly. From context:

- It is a **distillation/condensed companion** to a longer ALTER-EU report (*Rescue the Register!*, June 2013) — the recommendations here appear to be the disclosure-requirement subset extracted for submission to the register-review process.
- ALTER-EU's positions are coalition consensus from member organisations (e.g., Corporate Europe Observatory, Friends of the Earth Europe, LobbyControl); the document does not enumerate which members signed off, but framing as an "ALTER-EU" recommendation implies coalition agreement.
- The recommendations are grounded in **observed failure modes of the existing register** (e.g., "hugely diverging bandwidths", "incomplete client lists", "client names as abbreviations that are unrecognisable", "financial information... seriously outdated, referring to the situation several years ago"), suggesting the recommendation set was constructed from prior monitoring work by ALTER-EU members.
- No literature review, no formal coding scheme, no inter-rater reliability — this is **advocacy/policy submission**, not academic measurement.

## 3. Organizing structure

ALTER-EU groups its recommendations under **11 bolded category headings** in the source text. The categories are presented as a flat list (no super-categories, no numbering by ALTER-EU itself — the `<category>.<n>` indicator IDs in the TSV are assigned by the extractor). Recommendation count per category:

| # | Category (verbatim) | Recommendations extracted |
|---|---|---|
| 1 | Financial disclosure requirements | 1 |
| 2 | Transparency on funding sources | 3 |
| 3 | Names of lobbyists and revolving door listings | 2 |
| 4 | Issues lobbied on | 4 |
| 5 | Securing up-to-date information | 5 |
| 6 | Lobby firms' clients | 3 |
| 7 | Obliging registrants to disclose lobby consultancies and law firms assisting their lobbying | 1 |
| 8 | Tackling the problem of under-reporting the number of lobbyists | 3 |
| 9 | More comprehensive and effective data checking | 1 |
| 10 | Better public scrutiny | 1 |
| 11 | Pro-active transparency | 1 |
| **Total** | | **25** |

The categories are presented inline (each as a bolded header followed by a paragraph or two of prose), not in a table of contents.

## 4. Indicator count and atomization decisions

**Total recommendations extracted: 25**, from 11 categories.

ALTER-EU writes in flowing prose, not bulleted lists. Many category paragraphs bundle several distinct asks. Atomization rules used:

- **Distinct *what-must-be-disclosed* items split.** For example, *Transparency on funding sources* contains three separable obligations: (a) name all contributors, (b) specify amounts received from each, (c) exempt small individual donations. These are extracted as three rows because each could be implemented or omitted independently.
- **Mechanism vs. substance kept separate.** *Issues lobbied on* contains four atomic items: (a) require precise legislative-proposal information with official references, (b) ban blank/general descriptions, (c) introduce a user-friendly disclosure UI (drop-down dossier list), (d) require consultancies/law firms to provide per-client legislative lists. The first three would normally bundle, but ALTER-EU treats the form-design recommendation as a distinct sub-recommendation, and the consultancy-side requirement is an entirely different actor obligation, so all four are separated.
- **Update cadence atomized.** *Securing up-to-date information* yields five rows: secretariat active checking, recent-calendar-year reference period, twice-yearly fixed-date updates, twice-yearly rolling six-month consultancy client list, one-month new-client declaration. ALTER-EU lays each out as a distinct ask.
- **Enforcement bundled with substance only when inseparable.** *Lobby firms' clients* category produces three items: (a) regular checks + enforcement against incomplete and ambiguous-abbreviation client lists, (b) suspension and pass-withdrawal as the specific penalty, (c) rejection of the proposed confidentiality carve-out for law firms. Item (a) is itself a bundle (incomplete lists + ambiguous names), but ALTER-EU phrases them as a single failure-mode pair addressed by the same "regular checks and enforcement" remedy, so they remain one row with the dual scope flagged in `notes`.
- **Bullets that are pure rationale, not asks, omitted.** Lines 27–29 ("This is to enable public scrutiny of the revolving door, whereby public officials become private sector lobbyists, and vice versa, creating a high risk of conflicts of interest") are rationale for the lobbyist-names + revolving-door asks, not separate items.
- **`indicator_type` is `open` for all 25 rows.** ALTER-EU writes prose recommendations; there is no scoring rubric, scale, or yes/no checklist structure.
- **`scoring_rule` left empty for all rows** for the same reason.
- **Indicator IDs are extractor-assigned** using a `<short_category_slug>.<n>` convention (e.g., `funding_sources.2`). ALTER-EU does not number its own recommendations.

## 5. Frameworks cited or reviewed

The document cites only one prior ALTER-EU work by name:

- **ALTER-EU. 2013. *Rescue the Register! How to make EU lobby transparency credible and reliable.*** (Footnote 1, lines 46–48.) The recommendations document is explicitly a companion to this longer report.

The document does **not** cite outside frameworks (no PRI, no Transparency International, no OECD reference). It does reference, by name, the **EU Transparency Register's own 2012 annual report** (lines 61–63) — but only to push back against a confidentiality-carve-out proposal made there, not as an analytic frame.

## 6. Data sources

**N/A.** This is a recommendations / policy-advocacy document. It does not analyse a dataset; it specifies what data the EU Transparency Register *should* require registrants to provide. The only quantitative claim about the existing register is qualitative ("often seriously outdated, referring to the situation several years ago"; "incomplete client lists"; "client names as abbreviations that are unrecognisable") — sourced implicitly to ALTER-EU member monitoring rather than to a named dataset.

## 7. Notable quirks / open questions

**Target jurisdiction is the EU Transparency Register specifically.** The document is calibrated to one specific institutional setting: the 2011-established Joint Transparency Register of the European Parliament and Commission, which at the time of writing was voluntary (a recurring theme — see line 71, "the voluntary nature of the register"). Several recommendations are bound to EU-specific features:

| Recommendation | EU-specific element | Generalizable principle |
|---|---|---|
| `financial_disclosure.1` | €10,000 bandwidth | Narrower fixed-bandwidth bins for client-expenditure reporting |
| `lobbyist_names.1` | "Parliamentary access badges" | Full lobbyist roster, not just credentialed/badged subset |
| `lobbyist_names.2` | "(including at the national level)" — meaning national-EU-member-state offices | Revolving-door history disclosure |
| `firm_clients.2` | "Parliamentary passes withdrawn" | Suspension + credential revocation as enforcement |
| `firm_clients.3` | "category I [law firms and lobby consultancies]" — register's own taxonomy; pushes back on a proposal in the register's 2012 annual report | Equal-treatment principle: law firms doing lobbying held to same standard as other lobbyists |
| `consultancy_assistance.1` | Designed around "voluntary nature of the register" — many EU consultancies and law firms simply don't sign up | Reciprocal disclosure: clients name their lobby consultants, capturing activity by unregistered firms |
| `pro_active.1` | "European Commission" meetings | Government-side disclosure: executive-branch meeting/contact logs |

The remaining items (funding sources, issues-lobbied granularity, FTE calculation uniformity, change-history flagging system, systematic checking of new entries, ban on blank/general issue descriptions, drop-down legislative-dossier UI, semi-annual update cadence, one-month new-client declaration trigger) translate cleanly to a US-state lobbying-disclosure setting.

**Open questions for downstream use:**

- ALTER-EU does not specify the threshold below which individual donations should be exempt (`funding_sources.3`) — left to the implementing authority.
- "Most recent calendar year" (`up_to_date.2`) is positioned as a *starting point*; ALTER-EU implies stricter (more current) reporting may be desirable but doesn't specify.
- The FTE calculation methodology itself (`lobbyist_count.2`) is not provided — ALTER-EU only insists that *whatever* methodology is adopted, it be enforced uniformly across registrants. This is a meta-requirement (consistency) rather than a substantive one.
- The "flagging system" for change documentation (`public_scrutiny.1`) is not specified beyond enabling cross-organisation and over-time comparisons — implementation details (diff display, timestamps, archived snapshots) left open.
- The "voluntary nature" framing pre-dates the EU's later move toward a more mandatory regime; recommendations here implicitly assume the register's voluntary-but-incentivised structure.

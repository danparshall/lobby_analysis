# Carnstone 2020 — Responsible Lobbying: An Evaluation Framework

## 1. Paper

**Citation:** Hodgson, Simon and Witte, Daniel (2020). *Responsible Lobbying: An Evaluation Framework*. Carnstone Partners Ltd, with support from the Meridian Institute. Version 1.0, June 2020. Creative Commons Attribution 4.0 International License.

**URL:** https://www.responsible-lobbying.org/the-framework

**Source file:** `papers/text/Carnstone_2020__responsible_lobbying_framework.txt` (357 lines)

**Framing.** Carnstone is "an independent management consultancy, specialising in corporate responsibility and sustainability" (line 353). The Framework is presented as a *best-practice* / aspirational standard:

> "This best practice Framework has been developed by Carnstone for the Meridian Institute to help promote and support responsible lobbying practice." (lines 36–39)

The intended audience is **the originators of lobbying activity — companies and Civil Society Organisations (CSOs)** — *not* paid intermediaries and *not* governments:

> "Our Framework is intended for the originators of lobbying activity – in most cases companies or Civil Society Organisations (CSOs) – rather than focussing on intermediaries such as paid lobbyists." (lines 19–24)

> "It is intended to apply globally, allowing multi-national organisations to work to a common international standard." (lines 23–26)

The Framework explicitly rejects the lobbying-vs-advocacy normative split and applies the same standards to corporate and CSO actors equally:

> "all actors – whether corporate or CSO and whatever their cause – should be held to these same standards." (lines 67–68)

The motivation is voluntary self-regulation as an alternative to imposed restrictions:

> "We believe that responsible organisations will wish to sign up to robust standards to justify society's trust in the matter ... In the absence of effective voluntary self-regulation of this type, it is likely that strict limitations will increasingly be placed upon the practice." (lines 31–37)

## 2. Methodology

The Framework is a **synthesis of pre-existing standards** rather than original empirical research:

> "It is based on a large number of pre-existing standards and guides (see the references) but owes a particular debt to the work of Transparency International which has produced several very useful and authoritative documents on the topic." (lines 39–43)

The construction process is not described in detail — there is no stated advisory board, no consultation methodology, no scoring development. The document is structured as five normative principles, each illustrated with numbered "Which means:" recommendations and accompanied by per-recommendation source citations in the right margin (e.g., recommendation 1.1 cites "OECD Vol2, Harvard"; recommendation 2.1 cites "PRI Guide, ATNF BMS, OECD Principles, WHO, TI Standards, TI CPEI 2018, IM, Harvard"). The right-margin citations are the only methodological trace of how each item was derived.

The Framework defines lobbying using Transparency International's definition (lines 49–54) and explicitly adopts a process-based rather than cause-based view of legitimacy.

## 3. Organizing structure

**The framework is organized into 5 Principles, NOT 6 categories.** This contradicts the FOCAL claim of "6 categories" cited in the task brief — that 6-category schema (Definition / general disclosure requirements / financial disclosure requirements / timeliness, quality, and accessibility / integrity and ethics / enforcement and compliance) does **not** appear anywhere in the Carnstone document. The Carnstone categories are different both in name and number.

The five principles, with their headline statements:

1. **LEGITIMACY** — "Responsible lobbying will never be inconsistent with the public interest." (lines 105–108)
2. **TRANSPARENCY** — "Responsible lobbying organisations will be open, complete and truthful in their communications on the topic." (lines 154–158)
3. **CONSISTENCY** — "Responsible lobbying organisations will practice what they preach, remaining consistent with their professional codes, organizational values and other public positions." (lines 214–220)
4. **ACCOUNTABILITY** — "Responsible lobbying organisations and those who lobby for them will be accountable to stakeholders for their actions." (lines 245–250)
5. **OPPORTUNITY** — "Responsible lobbying organisations will coordinate and align activities with others when they identify issues that further the public interest and are of common concern." (lines 287–293)

**Per-category counts of numbered items (verified from source):**

| Principle | Top-level numbered items | Sub-bullet count (informational) |
|-----------|--------------------------|----------------------------------|
| 1. Legitimacy | 7 (1.1–1.7) | — |
| 2. Transparency | 5 (2.1–2.5) + 3 disclosure-quality cross-cutting rules (a/b/c) | 2.1 has 7 sub-bullets (a–g); 2.2 has 3 sub-bullets (a–c) |
| 3. Consistency | 2 (3.1–3.2) | 3.1 has 2 sub-bullets (a–b) |
| 4. Accountability | 5 (4.1–4.5) | 4.4 has 3 sub-bullets (a–c) |
| 5. Opportunity | 3 (5.1–5.3) | — |
| **Total numbered items** | **22 top-level + 3 disclosure-quality = 25** | |

## 4. Indicator count and atomization decisions

**Final extracted count: 25 indicators.**

**Atomization choices (and judgment calls):**

- **Top-level numbered items kept as the atomic unit.** Each numbered recommendation (1.1, 1.2, …, 5.3) is one indicator. This matches the Framework's own atomization — the document presents each numbered item as a standalone "Which means:" recommendation with its own source citations.
- **Sub-bullets within 2.1, 2.2, 3.1, 4.4 NOT split out.** Sub-bullets explain *what is contained within* a single recommendation rather than separate recommendations. For example, 2.1.a–g lists seven required disclosure fields *all of which* fall under the single recommendation "disclose the nature of all direct and intermediary lobbying." A user implementing the Framework either does 2.1 (with all sub-fields) or doesn't. This is a judgment call: an alternative atomization would split 2.1 into 7 disclosure-field indicators and 2.2 into 3 spend-category indicators (giving ~33 total). The chosen atomization respects the document's own numbering hierarchy.
- **The three Transparency disclosure-quality rules (lines 198–208, lettered a/b/c) ARE kept as separate indicators.** These cross-cutting rules — annual frequency, public/web-accessible location, dedicated report compilation — are not properties of a single numbered item; they apply to *all* Transparency disclosures. They are conceptually distinct quality requirements with distinct verification logic. Indicator IDs `carnstone_2_a`, `carnstone_2_b`, `carnstone_2_c`.

**Item type.** All indicators marked `open` (`indicator_type` column). The Framework offers no scoring rubric, no thresholds, no boolean checklist, no weighting. Each item is a normative recommendation — an organisation either adopts it (in some form) or does not, and there is no quantification within the document. `scoring_rule` left empty for every item.

**Discrepancy with the task brief's "23 items / 6 categories" expectation.** The brief (per FOCAL's claim) said 23 items across 6 categories. The actual document has **5 principles** (not 6) and, depending on atomization, **22 top-level items** (or **25** including the cross-cutting disclosure-quality rules, or up to **~33** if all sub-bullets are split). I cannot reproduce 23 with any clean atomization; the closest is 22 top-level items. The 6-category schema FOCAL described matches a different framework's structure entirely — likely Roth 2020, which the task brief warns is a separate framework with the same 6-category / 23-item layout. **It is plausible FOCAL conflated Carnstone with Roth 2020.**

## 5. Frameworks cited or reviewed

The "REFERENCES" section (lines 311–343) names the following standards/guides on which the Framework draws:

- **ATNF** — Access To Nutrition Foundation, Global Index 2018 (Category G – Engagement)
- **ATNF BMS** — ATNI Global Index 2018 Methodology (baby food / breast-milk substitutes code compliance)
- **Gates** — Bill & Melinda Gates Foundation, *U.S. Private Foundation Funds and Advocacy*
- **Harvard** — Harvard Kennedy School Corporate Responsibility Initiative & Business Fights Poverty, *Advocating together for the SDGs*
- **IM** — InfluenceMap's Methodology
- **OECD Principles** — OECD, *Principles for Transparency and Integrity in Lobbying*
- **OECD Vol2** — OECD, *Lobbyists, Governments and Public Trust, Volume 2: Promoting integrity through self-regulation*
- **PRI Guide** — UN Principles for Responsible Investment, *Converging on climate lobbying: aligning corporate practice with investor expectations*
- **TI CPEI 2018** — Transparency International UK, *Corporate Political Engagement Index 2018*
- **TI Glossary** — Transparency International, *Glossary, Conflicts of Interest*
- **TI Guide** — Transparency International Ireland, *A short Guide to Ethical Lobbying and Public Policy Engagement for Professionals, Executives and Activists*
- **TI Standards** — Transparency International, *38 International Standards for Lobbying Regulation*
- **WHO** — WHO Framework of engagement with non-State actors (private sector engagement procedures)
- **WHO Guidelines** — WHO Guidelines for Declaration of Interests (WHO Experts)

The Framework explicitly singles out Transparency International as its principal source (lines 41–43).

## 6. Data sources

**N/A.** Carnstone 2020 is a conceptual / advisory framework. It does not score states, score companies, score CSOs, or apply itself to any dataset within the document. There is no data collection, no sample, no jurisdiction list, no time period. The document is a normative reference for self-application by lobbying originators.

## 7. Notable quirks / open questions

- **Audience inversion vs. state-disclosure frameworks.** Most lobbying-disclosure frameworks (PRI, Roth, FOCAL, Newmark, etc.) evaluate *governments* on the disclosure regimes they impose on lobbyists. Carnstone evaluates *the lobbying organisations themselves* on their voluntary disclosure and conduct. This is a fundamentally different unit of analysis. Direct cross-walking to state-statute compendium items requires care: a Carnstone "disclose X" recommendation does not directly correspond to a state law requiring disclosure of X — it's a *should* aimed at the disclosing entity, not a *must* from a regulator.
- **Five principles, not six categories.** The task brief's FOCAL-derived claim of 6 categories does not hold up. Whoever built FOCAL appears to have assigned Carnstone a category structure that isn't in the document. (See discrepancy note in Section 4.)
- **Sub-bullet atomization is genuinely ambiguous.** A defensible alternative atomization would treat 2.1.a–g as seven separate disclosure indicators (since each is a distinct field — lobbyist identity, official identity, issues, outcomes, positions, frequency, beneficiaries) and 2.2.a–c as three separate spend categories. That would yield ~33 indicators. I chose to follow the document's numbering hierarchy and keep the seven 2.1 sub-bullets bundled in one indicator, with the sub-bullet content captured in `indicator_text`. This is a judgement call worth flagging for downstream cross-walk analysis.
- **The three "All disclosures should be" rules at end of Transparency** (frequency / accessibility / compilation, lines 198–208) are the only items in the framework that read as quality-of-disclosure standards independent of the disclosure subject matter. These map most cleanly to "timeliness, quality, and accessibility"–type categories in other frameworks.
- **No quantification anywhere.** No thresholds (e.g., what counts as "disproportionate resources" in 5.1?), no spend brackets, no time windows beyond "annually (ideally quarterly)" in 2.a. This will limit how Carnstone items can be scored if they enter a quantitative compendium.
- **Two cross-references inside the document.** Item 1.4 (political donations) and 1.5 (conflicts of interest) both say "see Principle 2," meaning their disclosure component is operationalised under Transparency. Item 4.1 cross-references Principle 5. Implementers should treat these as paired items.
- **Sectoral application notes (lines 76–94).** The document flags that key issues (1.1), key public policy frameworks (1.3), and conflict-of-interest arrangements (1.5) require sector-specific definition by the user — i.e., these three items are deliberately under-specified.
- **Footnote 2 (lines 144–148)** gives the Framework's working definition of conflict of interest, relevant to scoring 1.5.

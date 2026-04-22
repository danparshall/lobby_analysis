# Lobby Analysis — Landscape and Architecture

*A map of the frameworks, infrastructure, and data ecosystem we operate in, and where this project fits.*

**Audience:** Fellows onboarding to the project; future Claude instances picking up work; anyone trying to understand what we're building and why.

**Last updated:** 2026-04-22. This document is versioned with the repo; architectural claims are point-in-time and will drift as the project and the ecosystem evolve.

---

## 1. What this project is

`lobby_analysis` is **data infrastructure for state lobbying disclosure.** The project's primary deliverable is live, bulk-downloadable, cross-state lobbying disclosure data — structured according to an open schema, kept up-to-date on a cadence of weeks rather than years, covering all 50 states rather than a manageable subset.

The closest existing analogs are **LobbyView** (Bacik et al. 2025, MIT) at the federal level — ~1.6 million LDA reports with entity disambiguation, linked to Compustat, Orbis, BoardEx, VoteView — and **OpenSecrets** for federal lobbying spending plus a subset of state campaign-finance data (via FollowTheMoney). Neither covers state-level lobbying comprehensively. OpenSecrets' own 2022 state lobbying scorecard explicitly acknowledges that only 19 of the 50 states make "meaningful data available" in their operational model; the other 31 states are outside what OpenSecrets can feasibly ingest. **That 31-state gap is what this project targets.**

The companion deliverable is the **requirements-vs-availability matrix** — for each field in a field-level compendium, for each state, two answers: is the field *required* by state law, and is it *available* (both legally and practically)? This matrix is derived from the data + a separate legal-review pass. It is the artifact that turns our raw data into something policymakers, journalists, and researchers can use to identify and quantify state-level disclosure gaps.

The project is a **group effort of the Corda Democracy Fellowship**, led by Suhan Kacholia (Analogy Group), with approximately three fellows contributing. Dan Parshall authors most of this repository. The timeline is months, not years; the infrastructure bet is that LLM-assisted extraction (OCR, PDF parsing, text classification, statute interpretation) makes it cheap enough to maintain what organizations like the Council of State Governments stopped attempting around 2005.

## 2. What this project is not

Explicit non-deliverables, because the project lives adjacent to several efforts that look superficially similar:

- **Not a state ranking or scoring system.** We do not grade states on a single quality index. We publish data; downstream users apply whatever grading rubric serves their purpose.
- **Not a "Corda Rubric."** Several academic and NGO frameworks already exist (PRI 2010, FOCAL 2024/2026, CPI Hired Guns 2007, Newmark 2005/2017, Opheim 1991, Sunlight 2015, OpenSecrets 2022). These are internal scaffolding for our legal review; none is elevated to the status of "the project's rubric."
- **Not a compliance auditor.** We do not determine whether any individual filer violated disclosure law. We make it possible for others — journalists, ethics commissions, advocacy groups — to do that analysis.
- **Not an enforcement body.** Enforcement is out of scope. We surface compliance gaps; what happens next is up to civil society and institutional actors.
- **Not real-time.** State filing cadences are monthly to annual. We update on a weeks-to-months cadence matching what the underlying data supports. "Up-to-date" is the framing, not "real-time."

## 3. The four-axis framing

A field can be analyzed along four separable axes. The project delivers the first two directly; the third is enabled by the first two; the fourth is downstream entirely.

1. **Required.** Does the state's statute require this field to be disclosed? (Legal-review axis. Answered from statute text via LLM-assisted reading, validated against the PRI 2010 human-coded scores where overlap exists.)
2. **Available.** Is the disclosed data practically obtainable by the public? This axis has two sub-dimensions:
   - *Legally available* — is the filed data public under state law, or is it redacted, sealed, or access-restricted?
   - *Practically available* — is the public data usable given the portal's format? Structured bulk download, record-by-record search, HTML-only, PDF-only, or paper-on-request-only?
3. **Compliance.** Given what the state requires and what filers should therefore report, are they actually reporting it? (Derived by joining required fields from axis 1 against observed fields in filings. The GAO does this federally; our data makes the analysis possible for states.)
4. **Enforcement.** When non-compliance is detected, does anything happen? (Downstream of us entirely.)

A simple 2×2 typology on the first two axes gives the project's value proposition a crisp shape:

|                  | Available                   | Not Available                      |
|------------------|-----------------------------|------------------------------------|
| **Required**     | Working as intended          | **Accessibility gap — we fix this** |
| **Not Required** | Bonus (state exceeds its law) | Policy gap (statute reform needed)  |

The upper-right cell is where LLM-assisted extraction creates the most leverage: state law requires a disclosure, filers are submitting it, but the data is buried in scanned PDFs, behind WAF-blocked search pages, or only obtainable via written request. This is the PACER pattern — technically public, practically inaccessible. Converting these cells into "Required + Available" is the project's core contribution.

Note what the 2×2 does *not* locate. Quality of the underlying disclosure regime is a blend of all four axes plus enforcement, and different commentators weight the axes differently. Newmark (2017) found that four leading state-disclosure rubrics correlate at r=0.04 to r=0.52 with each other — they are measuring overlapping but distinct constructs. **The project does not choose a weighting.** We publish the underlying cells; users weight as their use case demands.

## 4. Layer 1: Data infrastructure

The open civic data ecosystem has converged around a small number of interoperating pieces. Understanding them is important because our data model aligns with them deliberately — the point is that our output is ingestable by the tools journalists and researchers already use.

### Popolo

The foundational spec. **Popolo** is a vendor-neutral, domain-general specification for representing civic and political entities in JSON: Person, Organization, Membership, Post, ContactDetail, Identifier, Area. It was developed jointly by Open North (Canada) and the Sunlight Foundation (US) in the early 2010s. Popolo doesn't know about lobbying specifically; it provides the reference-entity vocabulary that domain-specific extensions build on.

Our data model v1.0 is **Popolo-compatible at the reference-entity layer** — `Person`, `Organization`, `Identifier`, `ContactDetail` in `src/lobby_analysis/models/entities.py` follow Popolo's shape. This is a deliberate design choice. If a downstream consumer ingests our output using a Popolo-aware tool, they get sensible entity handling for free. Our domain-specific additions (`LobbyistRegistration`, `LobbyingFiling`, `StateMasterRecord`, etc.) extend Popolo rather than replacing it.

Popolo's governance has shifted since its original publication — the Sunlight Foundation shut down in September 2020, and Open North remains an active Canadian civic-tech organization. The spec itself is stable.

### Open Civic Data (OCD)

**Open Civic Data** is a project that extends Popolo for US-specific civic data. OCD lives at `opencivicdata/` on GitHub and publishes its specs as **OCDEPs** (Open Civic Data Extension Proposals). OCDEP 5 (the Popolo-based entity model) is the foundation; later OCDEPs extend to bills, votes, events, and elections. OCDEP-level specifications that are directly relevant here:

- **OCDEP 5** (adopted) — Persons and Organizations, Popolo-based.
- **OCDEP 6** (adopted) — Bills, votes, and legislative events.
- **"Campaign Finance Filings"** — a draft OCDEP that has circulated without formal adoption.
- **"Disclosures"** — an earlier withdrawn OCDEP that would have covered lobbying among other things.

The **absence of an adopted lobbying-disclosure OCDEP** is structurally important: there is no canonical open spec for state lobbying disclosure data. Our `LobbyingFiling`, `LobbyistRegistration`, `LobbyingPosition`, `LobbyingExpenditure`, `LobbyingEngagement`, and `Gift` models fill that gap. An open question (flagged for fellow discussion) is whether we engage actively with the OCD governance process to propose our models as the basis of an OCDEP, or remain passively compatible and let OCD pick up our models independently.

The reference library for OCD is **pupa** — a Python library for emitting OCD-compliant JSON. The primary consumer of OCD-emitted data is Open States.

### Open States (now "Plural Open Data")

**Open States** — rebranded **Plural Open Data** in 2023 under Plural (formerly Civic Eagle) — aggregates legislative data (bills, votes, legislators, committees) from all 50 states, DC, and Puerto Rico. It publishes data through an API and bulk downloads at pluralpolicy.com/open; the GitHub organization remains `openstates/`. The project's audience is members of the public, activist groups, journalists, and researchers with better data on what is happening in their state capital.

Open States is the natural distribution partner for our data at the legislative-references layer: when our `BillReference` resolves to an Open States canonical bill ID, our lobbying data becomes joinable with the Open States legislative record. A journalist investigating lobbying on a specific bill can click through from our data to Open States' bill page without entity-reconciliation friction.

### spatula

**spatula** is the page-oriented scraping framework Open States uses for their state-by-state scrapers. A spatula "page class" wraps an HTML page and exposes its content as parsed Python. It is the workhorse for turning state portal HTML into OCD-conformant structured data, with features like retry handling, caching, and pagination built in.

Context worth knowing: Open States has been experimenting with **Scrapy** as a potential spatula successor (the `openstates/scrapy-test` proof-of-concept repo) primarily to resolve dependency conflicts between spatula and other libraries. Spatula remains the current primary framework, but longer-term the scraping layer may migrate. For our project, the practical choice is between adopting spatula (distribution-channel alignment with Open States) and rolling our own extraction code. That decision is deferred; the data model is framework-agnostic regardless.

### Where we fit in Layer 1

Our pydantic data model (`src/lobby_analysis/models/`) is the bridge between the existing civic-tech ecosystem (Popolo + OCD + spatula + Open States) and the lobbying domain that ecosystem hasn't yet specified. Specifically:

- We use Popolo's reference-entity vocabulary.
- We follow OCD's pattern of publishing typed JSON with stable IDs.
- We keep our models parseable into Popolo/OCD-shaped records where possible.
- We add lobbying-specific models (`LobbyingFiling` and friends) to fill the OCDEP gap.

Version 1.0 of our data model was accepted 2026-04-21 and archived; a v1.1 update is in flight on the `data-model-v1.1` branch, adding availability-axis fields, framework-agnostic rubric traceability, and per-state pipeline-capability metadata. See `docs/historical/lobbying-data-model/results/lobbying_data_model_spec.md` and `docs/active/data-model-v1.1/plans/20260422_v1.1_gap_closures.md`.

## 5. Layer 2: The legal-review framework landscape

Independent of our data infrastructure, a body of work has attempted to measure the quality of state lobbying disclosure regimes. No single framework has established dominance; each measures something slightly different; they do not correlate well empirically. We use several of them as internal scaffolding for legal review, unioned into a **field-level compendium** that serves as our checklist.

Entries here are presented in rough chronological order, with relevance notes specific to this project. Full summaries of each are in `PAPER_SUMMARIES.md`.

### Opheim (1991)

The earliest systematic state-lobbying index. 22 binary items, 0–18 scale, three dimensions (statutory definitions / disclosure / oversight-enforcement). Applied to 47 states with OLS regression against political culture, legislative professionalism, and other predictors. Found moralistic states regulate most stringently, traditionalistic least. Foundational but superseded in granularity by later work.

### Newmark (2005)

Updated Opheim's approach into a time-series measure (6 time points, 1990–2003). 17 binary items; uses *The Book of the States* as the underlying data source. Validated against Opheim at r=0.84. Showed state regulation rose on average from 6.54 (1990–91) to 10.34 (2003). Item list is a proper subset of PRI 2010's.

### CPI "Hired Guns" (2007)

Center for Public Integrity's 48-question, 100-point, **weighted** state lobbying disclosure ranking. Notable because it is the only pre-FOCAL framework with explicit category weights (Individual Spending Disclosure 29%, Public Access 20%, Individual Registration 19%, Enforcement 15%). CPI replaced it with PRI 2010 three years later, so its evolution is informative — but it is also the only mainstream framework that **explicitly includes enforcement** as a scored category. PRI and FOCAL both exclude enforcement for feasibility reasons. Hired Guns is a reminder that the exclusion is deliberate, not natural.

### PRI / Clemens et al. (2010)

The Center for Public Integrity's *State Lobbying Disclosure Report* — 61-item disclosure-law rubric plus 22-item data-accessibility rubric, scored across all 50 states by human raters. **PRI's per-state scores are the only 50-state human-coded lobbying disclosure dataset that exists.** This gives them disproportionate weight as ground truth for calibrating our LLM-assisted statute-reading pipeline, even though PRI's rubric is structurally one frame among several (see the correlation discussion below). The `pri-calibration` branch is doing this calibration work now.

### Sunlight Foundation (2015)

A 5-category state lobbying disclosure scorecard (Jonah Hahn) using an unusual −2 to +2 point scale with letter grades. Key findings: 33 of 50 states don't require full itemized expenditure disclosure, 24 of 50 don't require lobbyist compensation disclosure, 6 states withhold the registration form from the public entirely. **The Sunlight Foundation shut down in September 2020**, and this scorecard was never updated. It is a named example of the sustainability problem our project claims to solve — a transparency-NGO-grade effort that produced a one-shot artifact and then decayed because there was no sustainable model for keeping it current.

### Newmark (2017)

Updated Newmark 2005 to 2015. Methodologically important beyond its item list: it is the single most careful cross-rubric comparison in the literature. Newmark found these correlations across contemporaneous state disclosure measures:

- **CPI Hired Guns ↔ PRI disclosure: r=0.04** (essentially zero)
- Newmark 2017 ↔ Sunlight Foundation: r=0.40
- Newmark 2017 ↔ CPI: r=0.52
- Newmark 2017 ↔ PRI accessibility: r=0.27
- Newmark 2017 ↔ PRI disclosure: ~zero

Newmark's interpretation: different measures, by design, measure different things. Factor analysis of his own 19-item index revealed 4–6 factors rather than 3 clean dimensions, suggesting states make bundled design choices rather than independent decisions per category. **This result is load-bearing for the project's positioning:** it is empirical proof that there is no single right rubric and that any scored ranking reflects the scorer's priorities as much as the underlying regime. Hence our compendium-first approach.

### FOCAL 2024 / Lacy-Nichols et al.

The **Framework for Comprehensive and Accessible Lobbying.** Lacy-Nichols, Baradar, Crosbie, and Cullerton (Melbourne / Nevada / Queensland) published a scoping review of 15 existing lobbying transparency frameworks in *International Journal of Health Policy and Management* (2024) and synthesized them into FOCAL: 50 indicators across 8 categories (Scope, Timeliness, Openness, Descriptors, Revolving Door, Relationships, Financials, Contact Log). The framework was developed for international Westminster-style governments but explicitly designed for cross-national application.

In 2026-04, we produced a US-state operationalization of FOCAL 2024 in `docs/active/focal-extraction/results/focal_2026_scoring_rubric.csv` — 54 rows (50 indicators − 1 compound + 5 decomposed), Westminster terms translated to US state equivalents, thresholds made explicit.

### Lacy-Nichols et al. (2025)

The FOCAL **application** paper, published in *Milbank Quarterly* July 2025. Applied the 50 FOCAL indicators with a weighted 0/1/2 scale (182-point total) to 28 national governments with online lobbyist registers. Headline results:

- **No country fulfilled all 50 indicators.** Top: Canada 49%, Chile 48%, **United States 45%**, Ireland 43%, France 43%.
- Category patterns: Scope scored highest across countries; **Revolving Door and Financials scored lowest**.
- Canada is the design exemplar (CSV downloads, unique IDs, data-linkage friendly); Chile/Ireland/Scotland have the best contact-log disclosures.
- **US scored at the federal LDA level**, not state-by-state. The authors explicitly call out US-state application as future work: *"researchers could apply the FOCAL to state governments in the United States, as many have more detailed disclosures than those required by the federal government"* (p. 875).

Two implications. First, our project is building what the FOCAL authors have publicly asked for. Second, FOCAL's published indicator weights are an input we should decide to adopt, modify, or discard consciously — not default to implicitly by staying with binary scoring. The question is flagged for the unified-rubric design.

### OpenSecrets (2022) — "State Lobbying Disclosure: A Scorecard"

The direct successor to Sunlight's 2015 scorecard, produced by OpenSecrets / Center for Responsive Politics (Dan Auble, Brendan Glavin) as part of their "Layers of Lobbying" series, funded in part by Omidyar Network. 4 categories × 5-point scale, 20-point max. The scorecard is what surfaced the 19-state operational ceiling: only 19 of the 50 states make meaningful data available in OpenSecrets' ingestion pipeline. **OpenSecrets does not publish the underlying state lobbying data in bulk** — we verified via their API and Bulk Data sections; federal lobbying is in bulk catalog, state campaign contributions come via FollowTheMoney, state lobbying data is not bulk-available.

### Federal LDA — field inventory

The Lobbying Disclosure Act of 1995, as amended by HLOGA (2007) and the JACK Act (2019), is the federal counterpart to state lobbying laws. It is not itself a scoring rubric but defines a set of disclosable fields across three forms (LD-1 registration, LD-2 quarterly activity, LD-203 semi-annual contributions) that belong in the compendium as a benchmark. The US scored 45% of FOCAL's 182 points in Lacy-Nichols 2025 — meaning LDA leaves meaningful room for improvement relative to the international best practice FOCAL represents, and state regimes that exceed LDA (as Lacy-Nichols notes "many have more detailed disclosures") are genuinely informative to document.

### Empirical takeaway

Newmark 2017's r=0.04 result is the single most important data point in this section. Rubrics that sound like they should measure the same thing (CPI's "disclosure" and PRI's "disclosure") measure different things. No single rubric is canonical. Our response — drop the idea of choosing one, union them into a field-level compendium, and let downstream users apply their preferred weights — follows directly from this empirical finding.

## 6. Federal context: GAO compliance audits

The **U.S. Government Accountability Office** is statutorily required to audit LDA compliance annually. **GAO-25-107523** (April 2025) is the 18th such report. Sampled ~100 quarterly LD-2 reports and ~80 semi-annual LD-203 reports; three questions: (1) extent of compliance, (2) filer-reported challenges, (3) enforcement activity by USAO-DC.

Relevant findings:

- 97% of new registrants filed required quarterly reports.
- 93% provided income/expense documentation.
- **21% of quarterly reports listed lobbyists who didn't fully disclose prior federal covered positions** — a persistent gap across annual audits.
- 5% of contribution reports missed reportable contributions (cross-checked against FEC database).
- 3,566 referrals to DOJ/USAO 2015–2024 for failure to file; ~63% unresolved as of December 2024.
- Zero criminal-conviction disclosure omissions in 258-person sample.

**Why this matters for our project:** GAO measures the compliance axis (#3 in our four-axis framing) for federal lobbying. GAO does not score the statute itself — LDA's coverage is taken as given. GAO's methodology (stratified random sample, filer survey plus interview plus documentation verification, cross-reference to FEC) is a template we could adapt for state-level compliance analysis once our extraction pipelines are operational.

The project will **not** directly conduct state-level compliance audits as a primary deliverable. But our data makes such analysis possible — a journalist, academic, or state ethics commission can now ask "what fraction of filings omit required gift-recipient disclosure?" and get an answer from our matrix + our data. That's the theory of change: infrastructure enables accountability.

One methodological note worth internalizing: a naive comparison like "federal lobbyists comply with LDA at X%, state lobbyists comply with state law at Y%" is almost always wrong. Federal LDA and any given state's law have different coverage; comparing miss rates means comparing different denominators. The defensible comparison is **"each jurisdiction's compliance with its own requirements"** — which our matrix supports without forcing the conflation.

## 7. Adjacent projects and positioning

The state lobbying data ecosystem has several existing players. Understanding who does what sharpens what this project adds.

### LobbyView (Bacik et al. 2025; earlier: Kim 2018)

MIT data-science team. LobbyView is a federal-only relational database: ~1.6 million LDA reports with entity disambiguation across clients, registrants, lobbyists, government entities, and legislators, linked to Compustat, Orbis, BoardEx, and VoteView. This is the **federal gold standard** we aspire to replicate at state level. LobbyView's methodology (regex + cosine-similarity pipelines for bill ID resolution, enriched with GPT-4 classifiers in newer work — Kim et al. 2025) is a useful design reference.

### OpenSecrets / Center for Responsive Politics

Federal lobbying + federal campaign finance, plus state campaign finance via FollowTheMoney. Their 2022 state lobbying scorecard is the public artifact; the underlying state lobbying data is not in their bulk catalog. Positioning relative to us is **complementary**: we target the 31 states they cannot feasibly cover, and our output could in principle feed a future OpenSecrets expansion.

### FollowTheMoney / National Institute on Money in State Politics

State campaign contributions, bulk-downloadable, mirrored by OpenSecrets under attribution. Different adjacent regime (campaign finance, not lobbying); not a direct competitor or collaborator, but a structural model for what open state-level political data can look like when someone invests in maintenance.

### Sunlight Foundation (shut down 2020)

Former heavyweight civic-tech organization. Their 2015 state lobbying scorecard is our named precedent for the sustainability failure mode. Worth studying what they built, how they framed it, and why it didn't survive — our sustainability plan is implicitly a response.

### Council of State Governments / *The Book of the States*

CSG has published *Book of the States* annually since 1935. The lobbying-regulation section was dropped around 2005 (Newmark 2017 cites this as the reason he shifted to primary-source statute review for his 2015 index). CSG continues publishing data on state government structure, courts, legislative bodies, and executive branches, but not lobbying. **This is the most informative gap-precedent for us**: a well-resourced, long-standing civic institution stopped maintaining the data collection because the work was too expensive relative to their other priorities. Our implicit bet is that LLM-assisted extraction shifts the cost curve enough to make sustained maintenance viable.

### F Minus

Activist organization that grades states with F-letter grades by design. The project scoped them in prior-art review (`docs/historical/research-prior-art/`) and decided to **treat F Minus as a hypothesis generator only**, pending methodology verification. Their advocacy framing is rhetorically useful, their measurement framing is not (yet) rigorous enough to use as a calibration source.

### MultiState (Compliance Insider)

Commercial lobbying compliance newsletter. Tracks state lobbying law changes for paying compliance professionals. Proprietary, subscription-gated, not usable as open infrastructure — but a signal that professional demand for cross-state lobbying law tracking is real enough to sustain a commercial operation. The gap we target is the same demand surface served openly.

### Project positioning in one sentence

**We are the maintained, open, all-50-states, field-level state lobbying data resource that the existing ecosystem has never collectively built** — complementing LobbyView at the federal level, extending what OpenSecrets 2022 scorecarded for 19 states to all 50, and filling the role CSG dropped in 2005.

## 8. Open questions

Genuine uncertainties, not decided as of 2026-04-22:

1. **OCDEP engagement strategy.** Is the "Campaign Finance Filings" draft OCDEP active, dormant, or effectively abandoned? If dormant, our pydantic models may be the most developed draft of what an open lobbying-disclosure OCDEP should look like — in which case active engagement with OCD governance could make our output the de facto open spec. If active, we should coordinate with whoever is leading it rather than duplicate. Flagged for Dan to raise with fellows and OCD maintainers.

2. **Sustainability past the fellowship.** Options: hand off to a civic-tech home (Plural / Open States, OpenSecrets, FollowTheMoney, Harvard's Ash Center, etc.), continue as an independent open-source project with community maintainership, or accept a 2026-snapshot-plus-code-for-revival model. Design for sustainability now; operationalize later.

3. **Weighting of the compendium.** Lacy-Nichols 2025 published FOCAL weights empirically derived from their 28-country study. CPI Hired Guns has its own category weights. PRI is unweighted. Whether our public matrix carries weights (and whose), or stays weight-neutral and lets downstream users weight, is an unresolved question.

4. **spatula vs. rolled-own extraction.** Adopting Open States' spatula framework aligns us with their distribution channel but inherits their dependency churn (the scrapy-test proof-of-concept suggests a scraper-framework transition may be coming). Rolling our own keeps us flexible but loses the free distribution channel.

5. **Federal LDA as a row in our matrix?** LDA is a peer disclosure regime. Including a "Federal" row alongside the 50 states — scored against the same compendium — would produce the cross-jurisdiction comparison the "federal baseline" narrative wants, without requiring the apples-to-apples contortion such comparisons usually need. Low-effort; flagged for later.

6. **F Minus collaboration or independence.** Their advocacy reach could amplify our data; their methodology concerns are real. Not urgent; not blocking.

## 9. Glossary

Quick reference for acronyms and domain terms used in this document:

- **BOS / Book of the States** — Council of State Governments' annual state government reference, 1935–present; lobbying section dropped ~2005.
- **CPI** — Center for Public Integrity (publisher of Hired Guns 2007 and PRI 2010).
- **FOCAL** — Framework for Comprehensive and Accessible Lobbying (Lacy-Nichols et al. 2024).
- **FOIA** — Freedom of Information Act (federal) and state analogs; governs public access to government records.
- **GAO** — U.S. Government Accountability Office (audits federal LDA compliance annually).
- **HLOGA** — Honest Leadership and Open Government Act of 2007; amended LDA.
- **JACK Act** — Justice Against Corruption on K Street Act 2018; amended LDA to add criminal-conviction disclosure for lobbyists.
- **LDA** — Lobbying Disclosure Act of 1995, as amended. Federal lobbying disclosure statute.
- **LD-1 / LD-2 / LD-203** — The three federal LDA filing forms: initial registration, quarterly activity, semi-annual contributions.
- **LobbyView** — MIT federal lobbying database (Bacik et al. 2025).
- **OCD / Open Civic Data** — Project that extends Popolo with US-specific civic data schemas.
- **OCDEP** — Open Civic Data Extension Proposal.
- **Open States / Plural Open Data** — All-50-states legislative data aggregator; formerly Open States, rebranded under Plural in 2023.
- **PACER** — Federal court records system; famously public-in-principle but paywalled in practice — the canonical "Required + Not Available" reference point.
- **Popolo** — Base spec for representing civic/political entities in JSON.
- **PRI** — Center for Public Integrity's 2010 State Lobbying Disclosure Report (rubric + 50-state scores).
- **pupa** — Python library for emitting OCD-compliant JSON (pronounced "pew-pa").
- **spatula** — Page-oriented Python scraping framework used by Open States.
- **StateMasterRecord (SMR)** — Our pydantic model capturing what each state's law requires, derived from legal review; joins against filings to enable compliance analysis.
- **USAO** — U.S. Attorney's Office (for the District of Columbia, which enforces LDA compliance federally).

---

## Changelog

- **2026-04-22** — Initial version. Drafted as output of the 2026-04-22 landscape brainstorm on `pri-calibration` branch; committed separately on `docs-landscape` branch for clean scoping.

## How this document should be used

- **Fellows onboarding:** read this document plus `README.md` plus `CLAUDE.md` first. Skip the Layer 1 section if already familiar with Popolo/OCD/Open States; skip Layer 2 if already familiar with the academic literature on state lobbying disclosure.
- **Future Claude instances:** this is project-level reference material. It is not branch-scoped. When revisiting, check the changelog to see if the landscape has shifted since last update.
- **External readers:** this is a snapshot of the project's architectural self-understanding. The actual deliverables live in `src/`, the actual data in `data/` (gitignored), the matrix exports at the project's eventual public URL (TBD).

# SOMO 2016 — A Structural Problem in the Shadows: source-extract notes

Companion to `items_SOMO.tsv`. Documents how SOMO's framework was atomized, what
is genuinely jurisdiction-portable vs. NL-specific, and the methodology behind
the assessment.

## 1. Paper

**Citation.** Vander Stichele, Myriam (SOMO). *A Structural Problem in the
Shadows: Lobbying by Banks in the Netherlands.* Stichting Onderzoek
Multinationale Ondernemingen (SOMO) / Centre for Research on Multinational
Corporations, Amsterdam, November 2016. ISBN 97-894-6207-1100. Funded by Open
Society Foundation. PDF: `papers/SOMO_2016__structural_problem.pdf`. Text:
`papers/text/SOMO_2016__structural_problem.txt` (3380 lines).

**Framing.** This is a **dual-purpose document**: it is simultaneously
(a) a Netherlands-specific case study assessing the Ministry of Finance and six
Dutch banks (ABN AMRO, ING, Rabobank, Triodos Bank, SNS Bank, ASN Bank) in the
context of post-2008 financial-sector reform, and (b) a normative framework for
what transparent and accountable lobbying *should* look like, articulated as
recommendations across three audiences (national government, Ministry of
Finance, banks). The framework is not given a brand name — FOCAL classified it
as "unnamed" and that is correct: SOMO labels its analytical lens with the
phrase "from a citizen's perspective" (chapter 1 title) but does not name the
framework itself.

The report builds on SOMO 2013 (*Taking Lobbying Public*) and Transparency
International–Nederland 2015 (*Lifting the Lid on Lobbying*). It frames its
mission as preventing "regulatory capture" of financial legislation — explicitly
treating capture as a major contributor to the 2007–2008 financial crisis.

## 2. Methodology

**Five high-level "aspects" applied throughout** (lines 269-288). Every chapter
assesses Ministry and banks against these:

1. Transparency (right to know)
2. Openness to citizen input (right to be heard)
3. Equality of access (integrity of democratic process)
4. Balance and public interest
5. Accountability

**Research methods** (lines 291-314):

- **Qualitative** — desk research and interviews with public-affairs staff and
  bank representatives at the six banks plus DBA/NVB (Dutch Banking
  Association). The Ministry of Finance declined an interview but answered
  written questions. Each bank reviewed findings; final responsibility remained
  with SOMO.
- **No fresh Wob (FOIA) requests** were filed for this report, but documents
  released through previous Wob requests were used.
- **Single embedded case study**: the EU's STS securitisation legislative
  proposal (September 2015 onwards) used to trace lobbying activity through a
  concrete legislative process.
- **Explicitly out of scope** (lines 322-333): parliamentary lobbying, lobbying
  of Dutch Central Bank/AFM/other ministries, revolving doors, payments to
  political parties, and informal personal/private encounters. This is a
  significant scoping decision — many items in larger frameworks (e.g. cooling-
  off periods) are simply *not addressed* by SOMO.

**Framework construction.** SOMO does not build the framework algorithmically.
Each chapter analyzes how the Ministry/banks fall short on one of the five
aspects, then Chapter 6 ("Recommendations") synthesizes those gaps into
prescriptive standards organized by audience (government / Ministry / banks).
The recommendations *are* the framework's enumerated items — there is no
separate scorecard or Table of Indicators.

## 3. Organizing structure

SOMO's recommendations are organized into **three audiences**, each with
**subsection headings** that I take to be the "categories." FOCAL's claim of 12
categories matches the count of subsection headings if you count carefully:

### Audience: government (6 categories)

1. **Legally binding regulations** — overarching call for binding national law,
   enumerating five specific instruments (transparency register, legislative
   footprint, civil-servant guidelines, ministerial diaries, weighing guidance).
   6 atomic items in TSV.
2. **Be transparent in order to protect the right to know** — legislative
   footprint, public legislative announcements, diary openness. 6 items.
3. **Protect the right to be heard** — improving consultations and citizen
   access. 7 items.
4. **Protect the integrity of the democratic legislative decision-making
   process** — mandatory transparency register + adapted code of conduct for
   civil servants. 10 items.
5. **Ensure that the public interest is weighed fairly** — stakeholder
   identification, impact assessment, balanced inputs, MvT explanations,
   trade-association capture check. 6 items.
6. **Exercise more accountability about lobbying activities** — synthesis
   item that ties prior categories to parliamentary/media accountability. 1
   item.

### Audience: Ministry of Finance (3 categories)

7. **A comprehensive transparency policy** — diary, EU-legislation page, BNC-
   fiche updates, EU-proposal consultations. 5 items.
8. **Better access for citizens, civil society organisations and diverse
   stakeholders** — consultation announcements, capacity. 4 items.
9. **Ensure all interests are weighed seriously** — krachtenveldanalyse, impact
   and risk analysis. 2 items.

### Audience: banks (3 categories)

10. **Public information improved/enhanced about lobbying activities and
    positions** — proposals, activities, definition, papers, memberships,
    budget. 13 items.
11. **Ensure integrity of the bank's interactions with, and lobbying of,
    legislative authorities** — code of conduct, CSR linkage, association
    codes, lobbyist disclosure. 4 items.
12. **Develop a comprehensive policy on interaction and lobbying on
    legislative proposals** — internal-policy bundle covering transparency,
    integrity, CSR, coordination, accountability, association engagement. 6
    items.

**Plus 5 "aspects" entries** at the report-framing level, recorded as principle-
type rows so the file documents the lens through which everything else is
assessed.

**Total per-category count:** 12 categories matches FOCAL's claim. The TSV
contains 71 prescriptive standards plus 5 framing principles = **76 items**.

## 4. Indicator count and atomization decisions

**Atomization rule.** Each terminal sub-bullet under a heading is treated as a
distinct item. Where SOMO uses a colon-introduced list (e.g. the Transparency
Register's seven required disclosure fields packed into one paragraph at lines
2980-2986), I kept it as a single compound row (`gov.integrity.register.3`)
rather than splitting, since SOMO presents it as one normative requirement.
Same treatment for the diary-archive metadata list (`gov.righttoknow.diary.2`)
and the lobbying-budget list (split into 4 rows, since SOMO presents those as
four enumerated bullet points under the budget heading at lines 3163-3174).

**Judgment calls:**

- The 5 "aspects" are recorded as `principle` rows (`aspect.1`–`aspect.5`)
  rather than as scoreable items, since SOMO uses them as evaluative lenses
  applied descriptively, not as binary checks. Without them the framework's
  organizing logic is lost.
- The "Legally binding regulations" preamble (`gov.binding.1`) is kept as its
  own item because it is the cap-stone — SOMO's strongest claim is that
  voluntary measures alone fail. The five enumerated specifics under it
  (`gov.binding.2`–`.6`) are each a distinct item; they reappear in expanded
  form later in the chapter, but I kept the short-form items because SOMO lists
  them as the binding-law content.
- The synthesis item `gov.accountability.1` is unusual: SOMO does not give it
  sub-bullets and treats accountability as a *consequence* of the prior items
  rather than a separate disclosure requirement. Recorded as `principle`-type.
- `bank.public.assoc.3` (internal-staff visibility of memberships) is a
  governance item, not external transparency. Flagged in `notes`.

## 5. Frameworks cited or reviewed (names only)

In-text comparators and benchmarks SOMO references (no PRI cross-references
were checked or added):

- **EU Transparency Register** (voluntary, run by EC + EP) — operative
  benchmark; SOMO recommends Dutch register meet or exceed it.
- **European Commission diary practices** — explicit benchmark for ministerial
  diary transparency.
- **Canadian lobbying regime / Office of the Commissioner of Lobbying of
  Canada** — held up as best-in-class for institutional enforcement.
- **Austria, France, US** — named as countries with binding lobbying
  legislation. The US is also cited as a *negative* comparator (industry uses
  consultation-flooding to delay legislation).
- **Transparency International — Nederland** (2015 *Lifting the Lid on
  Lobbying*) — methodological precursor.
- **Global Reporting Initiative (GRI) G4 Sustainability Reporting Guidelines**,
  specifically guideline G4-16 — voluntary disclosure benchmark for industry-
  association memberships in annual reports.
- **Initiatiefnota Lobby in daglicht** (Bouwmeester & Oosenbrug, MPs, December
  2015) — pending Dutch parliamentary proposal SOMO endorses.
- **Commissie De Wit** (parliamentary investigation into 2008 crisis, 2010) —
  origin of the "legislative footprint" concept in NL.
- **Aanwijzingen voor de Regelgeving** / **Memorie van Toelichting** /
  **Integraal Afwegingskader (IAK)** / **Gedragscode Integriteit Rijk (2015)**
  / **Gedragslijn Externe contacten (2016)** / **BNC-fiche** — Dutch
  domestic instruments the framework either cites or reforms.
- **SOMO 2013** (*Taking Lobbying Public*) — predecessor report that first
  assessed the same six banks.

## 6. Data sources

What SOMO drew on to evaluate the Ministry and banks:

- **Bank annual reports, websites, public statements** (with each bank's CSR /
  sustainability disclosures and "principles" pages).
- **Bank submissions to public consultations** (from the relevant consulting
  body's website — banks themselves rarely publish their own submissions,
  per SOMO's findings).
- **EU Transparency Register filings** for ABN AMRO, ING, Rabobank, Triodos
  Bank, DBA/NVB.
- **Interviews** with public-affairs staff at all six banks, plus DBA/NVB.
- **Written Q&A** with the Ministry of Finance (no interview granted).
- **Ministerial diary** (`agenda`), tweets (@J_Dijsselbloem, @Financien),
  speeches.
- **Memorie van Toelichting** documents (NL legislative explanatory notes)
  attached to financial laws.
- **BNC-fiche** documents for EU legislative proposals.
- **Documents released via prior Wob (FOIA-equivalent) requests** — SOMO
  flags Wob releases as the most informative source by far.
- **Parliamentary documents and Q&As** (Tweede Kamer / Eerste Kamer).
- **STS securitisation case study** — concrete legislative track followed
  through public meetings, Ministry-supplied meeting lists, EC consultation
  responses, and DSA (Dutch Securitization Association) lobbying activity.

## 7. Notable quirks / open questions

**Sectoral scope is narrow.** This is a *banking-sector* report. Every example,
every interviewee, and the entire case study (STS securitisation) sit within
financial-sector regulation. The framework asks what transparency around
banking-sector lobbying *should* look like. That said, the prescriptive
standards in Chapter 6 are nearly all written sector-agnostically — they speak
of "lobbyists," "industry associations," "civil servants," "stakeholders" —
with one exception: the bank-side recommendations sometimes specify "financial
industry associations." Readers can substitute any sector.

**Jurisdictional scope is more constraining.** Several items embed Dutch
instruments by name:

| Item id(s) | Dutch instrument | Generalizable equivalent |
|---|---|---|
| `gov.righttoknow.footprint.*`, `mof.access.consult.3`, `gov.weighing.5`, `mof.weighing.2` | Memorie van Toelichting (MvT) | Legislative explanatory note / fiscal note attached to a bill |
| `gov.righttoknow.footprint.4` | Aanwijzingen voor de Regelgeving | Drafting manual / legislative instructions |
| `gov.accountability.1`, `mof.transp.eu.1-3` | BNC-fiche | Domestic briefing on supranational legislative proposal — **no clean US-state analog** |
| `gov.integrity.coc.1` | Gedragscode Integriteit Rijk (2015) | Ethics code for civil servants |
| `mof.access.capacity.1` | Gedragslijn Externe contacten | External-contacts policy / lobby-disclosure protocol |
| `mof.weighing.1` | krachtenveldanalyse (IAK guidelines) | Stakeholder-power analysis as part of regulatory impact assessment |
| `bank.integrity.1` | Dutch bankers' oath | Industry self-regulatory oath / professional code |

The first 6 categories under "government" (binding regulations, right to know,
right to be heard, integrity, weighing, accountability) are all generalizable
to a US state-legislative context once the Dutch instruments are translated.
The most US-portable items are the Transparency Register design specs
(`gov.integrity.register.*`) — these are written almost identically to how a
US lobbying registry would be specified.

**EU-supranational items have no US-state analog.** `mof.transp.eu.*` and the
BNC-fiche items address how a national ministry should be transparent about its
co-decision role at EU level. The closest US-state analog would be a state
agency's transparency about its position on federal-level rulemakings — but
that is a much weaker structural relationship than EU co-decision.

**Bank-facing recommendations are self-regulatory standards, not government
disclosure rules.** All `bank.*` items describe what banks *should* disclose
voluntarily (or under voluntary codes of conduct). They do not specify
*regulatory* disclosure requirements imposed by the state. This makes them
useful for assessing the corporate-side complement of a state lobbying-
disclosure regime, but they would not be coded the same way as
government-imposed registry rules. The notable exception is
`bank.public.assoc.2` (submit memberships to a future Dutch transparency
register), which would be government-mandated.

**Voluntary-vs-binding emphasis.** SOMO's frame is that voluntary measures have
*failed*. The cap-stone item `gov.binding.1` ("legally binding regulations
should be introduced by national law") is rhetorically the most important item
in the framework — it is the synthesis judgment from the entire 56-page
assessment. For US-state assessment work, this maps onto the question of
whether a state's lobbying rules are statutory (binding) or merely guidance.

**Open questions:**

- Several items overlap (e.g. legislative-footprint requirements appear under
  `gov.binding.3`, `gov.righttoknow.footprint.1-4`, and
  `gov.righttoknow.announce.1`). SOMO presents these as a graduated
  specification — the cap-stone in binding regulations, then the implementation
  details under right-to-know. I kept them all rather than deduplicating.
- The "five aspects" framing (transparency / openness / equality / balance /
  accountability) maps loosely to PRI-style high-level categories but the
  language is Vander Stichele's own. No PRI cross-reference was performed.
- No explicit weighting or scoring scheme is provided — SOMO uses descriptive
  narrative ("not particularly helpful," "scant published information," "is
  not transparent") rather than a 0/1/2 rubric. Adapting these as binary
  presence/absence items is a downstream judgment call.

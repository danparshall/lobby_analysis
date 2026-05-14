# Mihut 2008 — comparative-narrative extract

## 1. Paper

**Citation.** Mihuţ, Liliana (2008). "Lobbying in the United States and the European Union: New Developments in Lobbying Regulation." *Romanian Journal of European Affairs* 8 (4): 5–17.

**Author.** Liliana Mihuţ, Professor of Political Science, Faculty of Law, 'Babeş-Bolyai' University, Cluj-Napoca, Romania.

**Framing.** Stated in the abstract: "The paper compares lobbying in the United States and in the European Union taking into account the specific environments in the two areas. It is focused on recent developments (2006 – 2008) in lobbying regulation in the US, at the federal level, and in the EU, at the level of the European institutions." (lines 9–12)

The paper is explicitly framed as a *comparison* organised around three concerns: (i) terminology / definitions; (ii) structural differences in the two political environments; (iii) regulatory developments 2006–2008. A concluding section addresses the relevance of this comparison for Romania.

## 2. Methodology

**Method.** Comparative narrative analysis of primary regulatory documents (US statutes; European Commission communications; European Parliament Rules of Procedure and resolutions) plus secondary scholarship. There is no quantitative coding instrument, no scoring rubric, no numbered checklist of disclosure items, no scoring weights, no application of an index to a sample of jurisdictions.

The strategy is to:

1. Define terms (using legal/official definitions in preference to scholarly ones).
2. Establish the contrasting environments (federalism vs. multi-level governance; pluralism vs. corporatism; party system; elections; PACs; interest-group systems).
3. Walk through US developments (Federal Regulation of Lobbying Act 1946 → LDA 1995 → 1998 Technical Amendments → HLOGA 2007).
4. Walk through EU developments (EP 1996–1997 Annex IX rules; Commission 1992/2002 communications; ETI Green Paper 2006 → Communication 2007 → Communication 2008 → Register opened June 2008; EP Resolution 8 May 2008).
5. Compare the two trajectories, using Pross 2007, Chari & Murphy 2006, Malone 2004, and Thomas 1993 as supporting framework references.
6. Draw concluding remarks about US/EU convergence and implications for Romania.

**No empirical dataset.** Mihut codes nothing. There are no tables, no figures, no scores, no inter-rater reliability — just text.

## 3. Organizing structure

The paper has four named sections:

1. **Terms and definitions: lobbying and lobbyist** — establishes that definitions are the substantive prerequisite for regulation; quotes OECD 2007 on the practical importance of defining who is "in" and "out"; contrasts the LDA's narrow technical definition with the ETI's broad activity-based definition; flags the EU's preferred term "interest representatives."
2. **EU and US — specific environments for lobbying activities** — lays out structural-environmental contrasts: federalism vs. multi-level governance / "deliberate ambiguity of this semi-confederation"; jurisdictional scope; budget size; party systems (two-party vs. multi-party "families"); electoral systems (plurality vs. PR); PACs; pluralism vs. corporatism dichotomy and Schmitter / Richardson / Greenwood / Michalowitz on the EU as "mixed."
3. **Lobbying in the US and the EU. Developments in lobbying regulations** — the substantive regulatory content. US: 1946 Act → LDA 1995 → 1998 amendments → HLOGA 2007 (Title I "Closing the Revolving Doors", Title II "Full Public Disclosure of Lobbying"; civil penalties $50K → $200K; first-ever criminal penalties up to 5 years). EU: EP Annex I + Annex IX; Commission's consistent rejection of accreditation 1992–2005; ETI from 2005; voluntary register + binding code of conduct from 2007/2008; the EP–Commission gap (mandatory vs. voluntary register; full vs. selected financial disclosure).
4. **Concluding remarks** — convergence claim + Romanian implications.

These four sections are the organizing structure. Within them, the comparative dimensions captured in the TSV are not numbered or labelled by Mihut — they emerge from the prose. There is no rubric numbering scheme to preserve.

## 4. Indicator count and atomization decisions

**Headline:** Mihut does not present a rubric. She presents a comparative narrative. The TSV therefore captures the *comparative dimensions she examines* as `indicator_type=open` rows, exactly as the prompt instructs for non-rubric papers.

**20 rows** in `items_Mihut.tsv`, organised as:

- **3 definitional dimensions** (`dim.definition_lobbying`, `dim.definition_lobbyist`, `dim.scope_branches_covered`) — what counts as lobbying and who counts as a lobbyist, and which branches of government are covered.
- **9 regulatory-content dimensions** (`dim.regulatory_approach`, `dim.registration_required`, `dim.disclosure_content`, `dim.disclosure_frequency`, `dim.gift_restrictions`, `dim.revolving_door`, `dim.code_of_conduct`, `dim.sanctions_civil`, `dim.sanctions_criminal`, `dim.sanctions_eu`) — the substantive regulatory line-items Mihut walks through. These are the closest analogue to disclosure-rubric items in any other paper, but Mihut treats them as comparative talking points, not as a scoring grid.
- **4 environmental dimensions** (`dim.pacs_campaign_finance`, `dim.interest_group_system`, `dim.access_points_governance`, `dim.professionalization`) — the structural contrasts Mihut uses to explain *why* the regulatory regimes differ.
- **3 typology references** (`typology.pross_2007`, `typology.chari_murphy_2006`, `typology.malone_2004`) — external framings Mihut cites without re-deriving. The Chari & Murphy three-tier classification (lowly / intermediately / highly regulated) is captured because it is the most rubric-like content in the paper, but it is **not Mihut's own**.

**Atomization choice.** I split `dim.sanctions_civil`, `dim.sanctions_criminal`, and `dim.sanctions_eu` rather than collapse to a single "sanctions" row, because Mihut treats them separately and the EU vs. US asymmetry is part of her argument. I split `dim.disclosure_content` from `dim.disclosure_frequency` for the same reason — HLOGA Title II changes both, and Mihut foregrounds each.

**What I did NOT atomize.** Many of Mihut's lines could be sub-divided further (e.g., revolving door could become "Senate cooling-off period" + "House cooling-off period"), but Mihut treats them as a single comparative point and the prompt asks for the dimensions she examines, not for a maximal decomposition.

**What I did NOT include.** The Romania concluding section is descriptive context about a third jurisdiction; it does not introduce comparative dimensions beyond those already captured.

## 5. Frameworks cited or reviewed

Names only:

- **Thomas, C.S. (1993)** — *First World Interest Groups: A Comparative Perspective* — used for cross-national characterizations of interest-group systems and for the claim that US lobbying regulation is "far more developed […] than in any other democracy" (Thomas 1993: 46).
- **Lijphart, A. (1999)** — *Patterns of Democracy* — invoked for the pluralism / corporatism dichotomy.
- **Schmitter, P.C. (1997)** — autobiographical reflections on corporatism — quoted on the EU emerging interest system being "more likely to be pluralist than corporatist."
- **Richardson, J. (2001)** — *European Union: Power and Policy-Making* — cited for "pluralism the defining characteristic of the EU interest group system."
- **Greenwood, J. (2003)** — *Interest Representation in the European Union* — cited for the position that neither corporatism nor pluralism alone fits the EU; for the 2/3 figure on EU business associations; and for differences in lobbying styles.
- **Michalowitz, I. (2002)** — "Beyond Corporatism and Pluralism" — quoted on "co-existence and complementarity of pluralism and neocorporatism."
- **Vogel, D. (1996)** — *Kindred Strangers* — cited on US business needing to invest in lobbying because no official channels.
- **Wallace, H. (2000)** and **Wallace, W. (2000)** — chapters in *Policy-Making in the European Union* — for "multi-level governance" and "deliberate ambiguity of this semi-confederation."
- **Watson, R. and Shackleton, M. (2006)** — chapter in *The European Union: How Does it Work?* — on EP lobbying environment, expertise dissemination, informal Commission–lobbyist relationship, and lobbying-style differences.
- **Schaber, Th. (1998)** — on the EP's quest for transparency and the structural reasons for the EP / Commission divergence.
- **Pross, A.P. (2007)** — OECD GOV/PGC/ETH(2007)4 "Lobbying: Models for Regulation" — quoted on the dual force of globalization and system-specific values.
- **Chari, R. and Murphy, G. (2006)** — IPA / Trinity College Dublin / DCU report — quoted for the three-tier (lowly / intermediately / highly regulated) classification.
- **Malone, M.M. (2004)** — IPA report — quoted on formal regulation being "more the exception than the rule."
- **OECD (2007)** — "Building a Framework for Enhancing Transparency and Accountability in Lobbying" — quoted on the importance of clear definitions.
- **Kallas, S. (2007)** — Commission VP speech "Lobbying: What Europe can learn from the US" — used for the brief comparison of HLOGA and ETI.
- **Mihuţ, L. (1994)** — author's own earlier work on Romanian pluralism.
- **Vass, A. (2008)** — for the observation about Romanian "active players."

## 6. Data sources

What Mihut actually examined (i.e., what she read, not statistical data):

- **US primary law:** Federal Regulation of Lobbying Act 1946; Lobbying Disclosure Act 1995; Lobbying Disclosure Technical Amendments Act 1998; Honest Leadership and Open Government Act 2007 (S.1, retrieved via Library of Congress THOMAS).
- **EU primary documents:**
  - European Parliament Rules of Procedure (Annex I "Transparency and members' financial interests"; Annex IX "Lobbying in Parliament"; Rule 9(4)).
  - Commission (1992) Communication "An open and structured dialogue between the Commission and special interest groups" (93/C63/02).
  - Commission (2002) Communication "General principles and minimum standards for consultation of interested parties" COM(2002) 704.
  - Commission (2006) Green Paper "European Transparency Initiative" COM(2006) 194.
  - Commission (2007) Communication on the Follow-up to the Green Paper COM(2007) 127.
  - Commission (2008) Communication on the ETI: framework for relations with interest representatives COM(2008) 323.
  - European Parliament (2003) Working Paper AFCO 104 EN "Lobbying in the European Union: Current Rules and Practices."
  - European Parliament (2008) Resolution of 8 May 2008 (2007/2115 (INI)).
- **Tertiary frameworks:** OECD 2007; Pross 2007; Chari & Murphy 2006; Malone 2004 (see §5).

**No empirical dataset.** Mihut does not code, score, or count. No statute compendium. No survey. No interview corpus.

## 7. Notable quirks / open questions

### Newmark 2017's framing — verified

The prompt flagged Newmark 2017's claim that Mihut concluded EU regulation is becoming more like US regulation. **Mihut does say this**, in the concluding remarks (lines 472–478):

> "We can conclude that the recent developments have strengthened some similarities between the American and the European ways of approaching lobbying regulation: transparency or open government, as well as honesty, integrity or accountability are the key words in the laws or other documents adopted either in the US or in the EU in the recent years. It essentially means that they have sprung from similar problems, and therefore have targeted similar goals, in a world where globalization has diffused lobbying practices."

But she immediately qualifies (lines 478–502):

> "However, as this paper has pointed out, the approaches remain different. The corporatist tradition in Europe, although declining, is still relevant in making the difference. […] On the contrary, the lack of official channels through which organizations can influence policy-making in the US explains why substantial resources are spent on lobbying and strict regulations for it are enforced."

So the headline finding is **partial convergence with persistent structural difference**. Earlier in the regulatory comparison (lines 449–466), citing Kallas 2007:

> "the documents reflect the traditional differences between the American and the European view on lobbying regulation: while the US has reinforced the mandatory approach, the Commission has maintained the self-regulation one (Kallas 2007). Nevertheless, further developments at the EU level have diminished the relevance of this difference. Particularly the position of the European Parliament gave more credit to the mandatory system, and, consequently, similarities with the American approach have chances to be strengthened through an increased inter-institutional cooperation on this matter."

Newmark 2017's gloss is therefore accurate but compressed — Mihut is not asserting a strong convergence claim, she is asserting that the *gap is narrowing*, mostly because the European Parliament (not the Commission) is moving toward the mandatory model.

### Empirical caution

Mihut's paper is dated 2008. The ETI Register opened in June 2008 and Mihut explicitly notes it is to be "experiment[ed]" for one year — so her assessment of the EU's voluntary approach is, by her own admission, ex ante. Anyone using this paper as a comparative anchor for present-day EU practice should be aware that the picture she sketched was provisional.

### Why this paper is in the corpus

It is **not a rubric paper**. The Chari & Murphy 2006 three-tier classification quoted within is the closest thing to a rubric, but it is borrowed and not applied. If the project's compendium uses this paper, its function is most likely:

- as background framing for the *why* of disclosure regulation (definitions matter; environments differ; convergence is partial),
- as a citation source pointing toward Chari & Murphy 2006 / Pross 2007 / Malone 2004 (the actual rubric / typology papers in the same lineage),
- as one of nine framework references showing the pre-2010 state of the comparative regulation literature.

It does not contribute scorable items.

### Open questions

- Whether to retain `typology.chari_murphy_2006` as an item in the Mihut row, or treat it as a pure cross-reference. I have included it because Mihut quotes the three-tier definition verbatim and applies it descriptively to half-the-US-states / federal-US / Canada / Germany / EP — which is the only quasi-scoring move in the paper. But the typology is not hers.
- Whether `dim.pacs_campaign_finance` should be in the rubric extract or treated as out-of-scope. PAC regulation is campaign-finance, not lobbying disclosure. I retained it because Mihut treats it as a comparative dimension of the lobbying environment, but downstream consumers may want to drop it.

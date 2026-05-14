# IBAC 2022 — Recommendation 3 (Lobbying) Item Extract

## 1. Paper

**Citation:** Independent Broad-based Anti-corruption Commission (IBAC). 2022. *Special Report on Corruption Risks Associated with Donations and Lobbying.* Melbourne, Victoria. https://www.ibac.vic.gov.au/publications-and-resources/article/corruption-risks-associated-with-donations-and-lobbying

**Framing.** This is a **state-level** integrity-commission report from Victoria, Australia — not a federal Australian report. IBAC is the Victorian standing anti-corruption body, established under the *Independent Broad-based Anti-corruption Commission Act 2011*. The report is a "special report" issued under IBAC's prevention-and-education mandate (the Act's s 162 reporting power), not the output of a single sworn investigation. It bundles four numbered recommendations (Rec 1–2 on donations, Rec 3 on lobbying substance, Rec 4 on the Victorian lobbying regulator and enforcement). **Only Recommendation 3** addresses lobbying-regulation substance; this extract captures only Rec 3 items. Donations-side items (Rec 1, Rec 2) and the regulator-design items (Rec 4) are out of scope per the task brief, with one boundary case noted in §7 below.

The report is forward-looking advocacy: IBAC is asking the Victorian Parliament and the Department of Premier and Cabinet to introduce new legislation. None of the items in Rec 3 reflect current Victorian law as of 2022 — they are the gap between status quo and IBAC's preferred end state. (This contrasts with frameworks scoring an existing register's quality.)

## 2. Methodology

IBAC describes its evidence base in Foreword §1 (lines 230–250) and the Recommendation 3 discussion section (Chapter 4):

- **Cross-jurisdictional consultation** with interstate integrity agencies — particularly the NSW Independent Commission Against Corruption (ICAC) and the Queensland Crime and Corruption Commission (CCC) / Queensland Integrity Commissioner (QIC).
- **Detailed policy analysis** drawing on prior reports (notably NSW ICAC Operation Eclipse 2021, Operation Aero 2022, Operation Spicer 2016; Queensland's Coaldrake Review 2022; Operation Belcarra 2019; the Yearbury Review 2021 of the QIC).
- **Cross-references to its own active investigations**, including the joint IBAC/Victorian Ombudsman *Operation Watts* report (June 2022) on misuse of electorate office and ministerial staff.
- **International comparison** with Scotland (*Lobbying (Scotland) Act 2016*), Republic of Ireland, and Canada (Canadian Lobbyists' Code of Conduct).
- **Review of Victorian instruments**: the *Public Administration Act 2004 (Vic)*, the Victorian Government Professional Lobbyist Code of Conduct (2013), the Ministerial Staff Code of Conduct (made public July 2022), the *Members of Parliament (Standards) Act*, and the *Public Records Act 1973 (Vic)*.

There were **no public hearings specifically tied to this special report** (it is an analytical/policy document, not the report of a sworn investigation). IBAC instead anchors its lobbying recommendations on the body of evidence developed by NSW ICAC's Operation Eclipse, which conducted public hearings on lobbying regulation 2018–2021.

> "In developing this suite of recommendations IBAC consulted with a wide range of stakeholders. In particular, IBAC: consulted with interstate agencies regarding the types of strategic issues that have been observed in Victoria, and measures that have been used elsewhere that could be considered for implementation in Victoria to mitigate those risks; conducted a detailed policy analysis of the issues under consideration, drawing on a range of publicly available research and lessons from other complaints and investigations that IBAC is currently undertaking, some of which are yet to be tabled as special reports" (papers/text/IBAC_2022__corruption_risks_donations_lobbying.txt:230-247).

## 3. Organizing structure

Recommendation 3 is structured as a single recommendation with **nine top-level lettered subsections (a) through (i)**. The discussion in Chapter 4 maps each lettered subsection to a numbered subsection of the report's analysis (e.g. (b) → §4.2.1.1, (c) → §4.2.1.2, (d)/(e)/(f) → §4.2.3.1, etc., per the right-hand "Discussion in this report" column on pp. 11–12).

- (a) generic transparency-and-accountability preamble (§4.1.3)
- (b) **definitions** — lobbying activity, lobbyist, government representative (§§4.2.1.1–4.2.1.3, 4.2.3.3)
- (c) **MP-initiated meeting** disclosure obligations (§4.2.1.2)
- (d) **lobbyist-side documentation** of contacts with a public, searchable register (§4.2.3.1)
- (e) **ministerial diary** (and ministerial staff diary) **monthly publication** (§§4.2.2.1, 4.2.3.1)
- (f) **lobbyist–minister / lobbyist–ministerial-staff** interaction transparency (§§4.2.3.1, 4.2.3.2)
- (g) **lobbyist–electorate-officer** interaction transparency (§4.2.3.3)
- (h) **success-fee prohibition**, broadened beyond procurement (§4.2.4.1)
- (i) **separation between campaign support and subsequent lobbying** (§4.2.4.2)

**FOCAL's claim of "8 categories" appears to be correct if the (a) preamble is excluded.** Subsections (b)–(i) = 8 categories, and they correspond exactly to FOCAL's list ("defines lobbying activities; MP-initiated meeting requirements; documenting contacts; ministerial diary publication; lobbyist–minister interactions; lobbyist–electorate-officer interactions; success-fee prohibition; cooling-off vis-à-vis campaign supporters"). This is **not** a FOCAL miscount, in contrast to the Newmark 2005 and Carnstone 2020 errors flagged in the brief. I have nonetheless retained (a) as `rec3.a` in the TSV so that `indicator_id` aligns with IBAC's own labeling rather than silently dropping it.

A further structural note: **post-employment cooling-off** (the classic "revolving door" concept) is **not** in Rec 3 — it is in Recommendation 4(c), which IBAC frames as enforcement/regulator-design rather than substantive lobbying conduct. The cooling-off in Rec 3(i) is a different concept: the period during which a lobbyist who supported an official's campaign cannot lobby that official. The brief's "cooling-off vis-à-vis campaign supporters" framing matches Rec 3(i) and excludes the post-employment cooling-off in Rec 4(c).

## 4. Indicator count and atomization decisions

**Total items: 24** (in the TSV) / **23** (excluding the (a) preamble) — matching FOCAL's claimed count of 23 once (a) is excluded.

Atomization choices:

- **Bullet-by-bullet under (b), (d), (e), (f), (g):** each Roman-numeral sub-item is a separate row. These read as parallel obligations (not enumerations of one obligation), e.g. (e)(i) date, (e)(ii) attendees, (e)(iii) interests, (e)(iv) issues — each is a distinct field that must be in the published diary extract.
- **(c)(i) decomposed into three rows** (`rec3.c.i.1`, `rec3.c.i.2`, `rec3.c.i.3`). This is the only place I expanded *below* Roman-numeral level. The three bulleted disclosures within (c)(i) are substantively distinct (private-interest yes/no flag, nature of interest, names of representers) and the third bullet has its own gating clause ("regardless of whether the MP has a private interest"), which makes it a separate trigger. Expanding here is what brings the total to 23 in (b)–(i).
- **(c)(ii)** kept as one row (recordkeeping/auditability) — it pairs with (c)(i) as a meta-obligation rather than a parallel disclosure field.
- **(h) and (i)** kept as single rows — IBAC writes them as single sentences with no sub-bullets.
- **(a) included as `rec3.a`** despite being a preamble — keeps `indicator_id` aligned with IBAC's own labeling. Marked clearly in the row notes as a generic principle rather than a substantive item.

Without the (c)(i) bullet expansion, the count drops to 21; without the (a) preamble, that becomes 21 substantive items in 8 categories — which is a defensible alternative reading. **I went with the 23+1 reading because it best preserves IBAC's own structure and matches FOCAL's prior count.**

`indicator_type` values used: `principle` (1×), `definitional` (3×), `disclosure` (10×), `recordkeeping` (3×), `governance` (2×), `training` (2×), `prohibition` (2×), totaling 23 substantive items + 1 preamble.

`scoring_rule` is "Not specified" for every row: IBAC's framework is a legislative reform recommendation, not a graded index. The closest IBAC comes to scoring is the implicit binary "is the law in force, yes/no" — but the document does not propose weights, partial credit, or comparative scoring across jurisdictions.

## 5. Frameworks cited or reviewed

IBAC names (no scoring frameworks; these are regulatory regimes and prior investigations):

- NSW ICAC, *Operation Eclipse* (2021) — investigation into the regulation of lobbying, access and influence in NSW
- NSW ICAC, *Operation Aero* (2022) — investigation into political donations facilitated by Chinese Friends of Labor in 2015
- NSW ICAC, *Operation Spicer* (2016) — investigation into NSW Liberal Party electoral funding for 2011 state election
- Queensland CCC, *Operation Belcarra* (2019)
- Coaldrake P. (2022) — *Review of Culture and Accountability in the Queensland Public Sector*
- Yearbury K. (2021) — *Strategic Review of the [Qld] Integrity Commissioner's Functions*
- IBAC and Victorian Ombudsman (2022), *Operation Watts*
- *Lobbying (Scotland) Act 2016*; Scottish Ministerial Code (2018 ed.)
- Republic of Ireland lobbying regime (referenced via NSW ICAC Op Eclipse rather than directly)
- Canadian Lobbyists' Code of Conduct (2015)
- *Lobbying of Government Officials Act 2011 (NSW)* and the NSW LOGO regulation
- *Integrity Act 2009 (Qld)*; Queensland Lobbyist Code of Conduct
- *Integrity (Lobbyists) Act 2016 (WA)*
- OECD (2020), *Government at a Glance: Latin America and the Caribbean 2020*, ch. 9.2
- Centre for Public Integrity (2022), *Integrity Inadequacies: Victoria*
- Ng Y-F (2020), "Regulating the influencers: The evolution of lobbying regulation in Australia," *Adelaide Law Review*

No scoring/index frameworks (e.g. CPI, GIR, FOCAL) are referenced. IBAC's anchor is comparative *legislation*, not comparative *scores*.

## 6. Data sources

- **Victorian primary materials**: Victorian Government Professional Lobbyist Code of Conduct (2013); Ministerial Staff Code of Conduct (2022); *Public Administration Act 2004 (Vic)*; *Members of Parliament (Standards) Act*; *Public Records Act 1973 (Vic)*; Code of Conduct for Parliamentary Electorate Officers; *Planning and Environment Act 1987 (Vic)*; Victorian Public Sector Commission lobbyist register.
- **Stakeholder consultation**: interstate integrity agencies (NSW ICAC, Qld CCC, Qld QIC), Department of Premier and Cabinet, agencies that would implement reforms.
- **Internal IBAC investigations**: complaints and investigations referenced obliquely ("some of which are yet to be tabled as special reports") plus the published *Operation Watts* report.
- **Comparative law review**: NSW, Queensland, Western Australia, Scotland, Ireland, Canada.

IBAC did **not** conduct fresh empirical work, did **not** survey lobbyists or government representatives, and did **not** hold public hearings for this report. The evidence base is documentary and consultative.

## 7. Notable quirks / open questions

**Cross-walkability to US state lobbying.**

Several Rec 3 items map cleanly onto US state lobbying frameworks; several are awkward; a few are parliamentary-system-specific in a way that requires conceptual translation.

**Generalizable to US states with minimal translation:**
- (b) definitions of "lobbying activity," "lobbyist," and the activity-based (rather than role-based) approach — same conceptual problem in US states.
- (d) lobbyist-side documentation and a public, searchable contact register — every US state lobby-disclosure regime has an analogue (with varying detail).
- (g) recordkeeping and training for legislator-staff interactions with lobbyists — maps onto US legislative staff and constituent-services staff.
- (h) success-fee prohibitions — most US states already have versions of this (often called contingent-fee bans).
- (i) prohibition on lobbying officials whose campaigns the lobbyist supported — has analogues in some US state ethics codes (e.g. revolving-door + donation matching restrictions), though weakly enforced.

**Awkward / parliamentary-system-specific:**
- (c) "MP-initiated meetings with a minister or their adviser" assumes the Westminster fusion of executive and legislature, where backbench MPs from the governing party can directly approach a minister's office. In US states the analogue might be "rank-and-file legislator approaching the governor's office" or "legislator approaching a cabinet secretary's office," but the dynamic is different: US state legislators are not part of the executive in the same way Australian MPs are, and the corruption-risk vector IBAC describes (donor-driven advocacy *via* an MP to a minister) plays out differently when the executive and legislature are constitutionally separated.
- (e) **"ministerial diary" / "ministerial staff diary"** has **no clean US state analogue.** US governors do not generally publish daily calendars in the way Scottish or Queensland ministers do. The closest US analogue would be open-records / FOIA-driven release of executive calendars, which is reactive (records-request based) rather than the **proactive monthly publication** IBAC recommends. Some US states release governor calendars on FOIA request with significant redaction; California and a handful of others have moved toward proactive release. **This is the single largest cross-walk gap.**
- (f) "Ministerial advisers" / ministerial staff have a US analogue (gubernatorial staff, agency political staff), but US ethics regimes generally do not require those staff to publish meeting logs, nor do they require chief-of-staff approval to take a lobbyist meeting.
- (g) "Electorate officer" — these are constituency-office staff for individual MPs, paid by the parliament. US analogue is the personal/district staff of a state legislator. US states vary widely on whether such staff are subject to lobby-disclosure or ethics rules.

**Other quirks:**
- The (a) preamble blurs the line between "transparency principle" and "discrete indicator." Different counts are defensible.
- IBAC explicitly defers the **regulator design** (sanctions, enforcement powers, resourcing, code-of-conduct instrument, post-employment cooling-off period scope) to **Recommendation 4**, asking the Department of Premier and Cabinet to study it further. This means Rec 3 is substantively about *what to disclose / prohibit*, and Rec 4 is about *how to enforce it*. Frameworks comparing IBAC to other lobby regimes need to decide whether to include Rec 4 items; this extract excludes them per the brief.
- IBAC does **not** propose financial or time thresholds for who counts as a lobbyist — it explicitly recommends an activity-based definition without monetary minima. This contrasts with US state regimes, most of which have dollar or hours thresholds.
- IBAC explicitly notes that no other Australian jurisdiction extends lobbying regulation to electorate officers (line 2632) — Rec 3(g) is novel within Australia.
- Local-government coverage: Rec 3(b)(i) explicitly covers "decision-making at the local government level." IBAC wants lobbying regulation at *both* state and local levels — comparable to US state lobby laws that cover state agencies but typically *exclude* municipal lobbying (which is regulated separately or not at all).

**Open question for the compendium:** does the project want to count IBAC items at the i-level (21 substantive items) or with (c)(i)'s three bullets expanded (23 substantive items)? I have chosen the 23-item expansion to match FOCAL's prior count, but the 21-item reading is equally defensible from the source text.

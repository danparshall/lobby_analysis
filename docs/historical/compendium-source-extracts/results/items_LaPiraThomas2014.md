# LaPira & Thomas 2014 — Revolving Door Lobbyists and Interest Representation

## 1. Paper

LaPira, Timothy M. and Herschel F. Thomas III. (2014). "Revolving door lobbyists and interest representation." *Interest Groups & Advocacy* 3: 4–29. doi: 10.1057/iga.2013.16. (Macmillan Publishers / Palgrave; advance online publication 21 January 2014.)

**Framing.** The paper poses one central empirical question: *do revolving door lobbyists represent different interests than conventional lobbyists?* It contrasts two normative views — lobbying-as-information-supply (expertise) versus lobbying-as-access-peddling — and asks which is empirically more consistent with how revolving-door lobbyists' clienteles are structured. Findings: revolving-door lobbyists tend to work as contract lobbyists, specialize disproportionately in appropriations/earmarks, and — for those who climbed the congressional staff ladder — represent more economically diverse clienteles than conventional lobbyists. Former bureaucrats, by contrast, retain *more* concentrated clienteles (consistent with sector-specific expertise). Former *members* of Congress show no significant effect, but the sample contains only 12 of them, so the null is uninformative.

> "Do revolving door lobbyists represent different interests than conventional lobbyists?" [papers/text/LaPira_Thomas_2014__revolving_door_lobbyists.txt:21–23]

> "the revolving door problem is not limited to a handful of headline-catching former legislators, is much bigger than the existing lobbying disclosure regime reveals and – most importantly – significantly distorts the representation of interests before government." [54–57]

## 2. Methodology

**Type.** *Empirical / measurement-construction*. This is **not** a rubric-of-disclosure-statutes paper, and it is **not** a purely theoretical paper. It is an original empirical study that (a) constructs a more accurate operational measure of revolving-door status than what LDA self-reports yield, (b) characterizes the revolving-door population by branch, hierarchy and partisanship, and (c) tests how those revolving-door attributes (plus occupation and specialization controls) predict an entropy-based measure of clientele diversity.

**Design.**

1. Drew a random 11% sample of registered federal lobbyists in 2008 (n = 1622, after deduplication n = 1614) from CRP's standardized lobbying database.
2. For each lobbyist, three trained RAs conducted comprehensive multi-source biographical searches (2011–2012 academic year) to identify previous Congressional, White House, executive-bureaucracy and judicial employment.
3. Linked the coded sample to ~51,475 quarterly LD-2 reports filed in 2008 for client- and activity-level variables.
4. Estimated two left-censored regressions (Tobit-style) of the lobbyist's clientele diversity (Shannon's H entropy across 13 CRP sectors) on revolving-door variables, occupation controls and advocacy-specialization controls.

> "we 1. drew a random sample of individual lobbyists registered in 2008; 2. conducted searches using multiple archival sources to record information about lobbyists' government experience and subsequent lobbying specializations; and, 3. linked the coded sample of lobbyists to measures of their clienteles and lobbying activities from LDA reports filed in 2008." [345–350]

**Key empirical findings (size of the loophole).**

> "Only 29.7 per cent of lobbyists report their covered official status, although 51.7 per cent of the sample was found to have held a position in government. Of the roughly half of lobbyists who were found to have worked in the government, two in three (67 per cent) chose not to report that information." [459–462]

> "we estimate that approximately 3948 (±2.3 per cent margin of error) registered lobbyists chose not to disclose their previous government employment in 2008." [463–465]

## 3. Organizing structure

The paper develops a **multi-component construct of revolving-door activity** built on top of (and explicitly distinguished from) the LDA's "covered official" statutory definition. The construct decomposes along three orthogonal dimensions:

1. **Verified-vs-self-reported revolving-door status.** A binary indicator (`rd.verified_government_employment`) coded 1 if any prior federal employment is verified in the multi-source biographical search, regardless of whether the lobbyist disclosed it on the LDA. This is the paper's core methodological contribution and the operational definition used in regressions.
2. **Branch / position type.** Five categories: former member of Congress; congressional staff; White House; federal bureaucracy; judiciary (the last excluded from analysis as mostly clerkships).
3. **Within-Congress hierarchy.** A 7-level scale ("congressional staff hierarchy") capturing whether a former staffer worked only in a member's personal office, only on a committee, on leadership, or some combination — the higher the level, the more "connections" the staffer brings.

Around this core, the paper adds **occupation controls** (contract vs. in-house; general-interest firm vs. boutique) and **advocacy-specialization controls** (legislative policy, appropriations/earmarks, regulatory/legal). The dependent variable is a **normalized Shannon's H entropy** over the 13 CRP economic-sector codes of the lobbyist's 2008 clients — the paper's proposed operationalization of the access-vs-expertise distinction.

> "the popular use of the 'access' concept implies not only that lobbyists know people in relevant government institutions, but also know those institutions' norms and routines... we seek to differentiate kinds of lobbyists – those oriented more toward policy expertise from those more inclined to trade on their access to the people in government who matter – by exploring the kinds of interests they represent." [250–257]

## 4. Indicator count and atomization decisions

**18 rows** in the TSV. Atomization choices:

- The **statutory LDA "covered official" definition** is captured as a separate row (`rd.covered_official_status_lda`) from the **authors' verified measure** (`rd.verified_government_employment`), because the paper's central methodological argument is that these diverge by ~22 percentage points and the authors' construct is the one used in regressions. Keeping them separate preserves the paper's critique of the LDA.
- **Number of government positions** (`rd.num_government_positions`) is a separate count from the binary verified-RD indicator because it enters the regression independently and the authors emphasize that LDA only requires reporting one prior position even though nearly half of revolving-door lobbyists held more.
- **Branch / position-type** atomized into five booleans (former member, staff, White House, bureaucracy, judiciary) plus the **staff hierarchy ordinal scale** as a sixth row. The hierarchy is a separate variable in the regressions, not redundant with the staff boolean.
- **Partisan affiliation of former employer** included as a single categorical row even though it is a face-validity check rather than a regression predictor — the authors construct and report it, so the construct includes it.
- **Occupation and specialization controls** (5 rows) are part of the paper's operationalization of "what predicts clientele diversity"; they are not the revolving-door construct itself but are tightly bound to it in the model. Including them keeps the captured construct faithful to the paper's analytical setup.
- **Outcome variables** (3 rows: number of clients, number of sectors, Shannon's H clientele diversity) included because clientele diversity *is itself* a constructed measure central to the paper. Number of clients and number of sectors are the inputs to the entropy calculation and are reported descriptively.
- Excluded from rows: judicial-branch employment is reported but excluded from analysis by the authors, so I included it for completeness but flagged the exclusion. Demographic, partisan-activity and campaign-activity variables are mentioned (line 401–402) as collected but never operationalized in the published analysis, so they are not captured.

## 5. Frameworks cited or reviewed

The paper is anchored in the interest-group / lobbying-influence literature, not in the disclosure-rubric literature. Names only:

- Bauer, Pool & Dexter 1963 (*American Business and Public Policy*)
- Milbrath 1963 (*The Washington Lobbyists*)
- Deakin 1966 (*The Lobbyists*)
- Zeigler & Baer 1969 (*Lobbying: Interactions and Influence in American State Legislatures*)
- Herring 1929 (*Group Representation before Congress*)
- Gormley 1979 — first explicit test of the "revolving door hypothesis" at the FCC
- Quirk 1981; Cohen 1986; McGuire 2000 — venue-specific RD tests
- Salisbury, Johnson, Heinz, Laumann & Nelson 1989 ("Who you know versus what you know")
- Hansen 1991 (Farm Lobby)
- Heinz, Laumann, Nelson & Salisbury 1993 (*The Hollow Core*) — ~800-lobbyist interview study
- Baumgartner, Berry, Hojnacki, Kimball & Leech 2009 (*Lobbying and Policy Change*) — uses LDA self-report of "covered official"
- Lazarus & McKay 2012 — universities + earmarks
- Blanes i Vidal, Mirko & Christian 2012 (*AER*) — name-matching to Hill payroll
- Bertrand, Bombardini & Trebbi 2011 — name-matching, issue switching
- Eggers & Hainmueller 2009; González-Bailon, Jennings & Lodge 2013 — UK private-sector employment of former officials
- Eggers 2010 — partisan revolving door
- Citizens for Responsibility and Ethics in Washington 2012; Public Citizen 2005; Revolving Door Working Group 2005 — watchdog-org reports
- Drutman & Cain forthcoming — congressional staff and regulatory change
- Lessig 2011 (*Republic, Lost*) — institutional-corruption framing
- Hall & Deardorff 2006 — lobbying as legislative subsidy
- Esterling 2004 — political economy of expertise
- Mansbridge 1992 — deliberative theory of interest representation
- Lowery & Marchetti 2012 — principals, agents, lobbying
- Boydstun, Bevan & Thomas (forthcoming); Jennings et al 2011; Halpin & Thomas 2012 — Shannon's H applications in political science
- Gray & Lowery 1996 — population ecology of interest representation; HHI usage
- Furlong 1997; Yackee 2006 — rulemaking / notice-and-comment lobbying
- Schattschneider 1960 [1975] — "heavenly chorus"
- Shannon 1948; Ben-Naim 2007 — information entropy

**Note:** No state-level disclosure-rubric papers are cited (no BoS, no Newmark, no Opheim). This is intentional: the paper's frame of reference is the federal LDA and the interest-group-influence literature, not state lobbying-regulation comparisons.

## 6. Data sources

All federal. Specifically:

- **CRP (Center for Responsive Politics) Lobbying Database** — primary source for the sampling frame, LD-2 quarterly reports, name disambiguation (>95% completion), and the 13-economic-sector client coding.
- **Senate Office of Public Records (SOPR) Lobbying Disclosure Database** — raw LD-1 and LD-2 reports.
- **CRP Revolving Door Database** — selected RD biographical info.
- **Congressional Quarterly First Street Database** — links registered lobbyists to Congressional Staff and Federal Staff directories from 1993 onward.
- **Lobbyists.info Directory** — proprietary; self-reported biographical data.
- **Lexis-Nexis Martindale-Hubbell Directory** — proprietary; attorney biographies.
- **LegiStorm Pro Directory** — proprietary; congressional staff salaries plus media-supplemented sources.
- **Firm / organization websites** — public.
- **LinkedIn** — membership-gated; self-reported biographies.

(Full description in Table A1, lines 1252–1296.)

**No state-level data sources at all.** The paper is entirely federal LDA-scoped.

## 7. Notable quirks / open questions

**(a) Federal-only. Cross-walk to state-level revolving-door measurement is non-trivial.** The paper's construct rests on three federal infrastructures that have no clean state-level analogue:

1. **Statutory baseline.** The LDA's 20-year-lookback "covered official" definition is a federal statute. State lobbying laws vary enormously in whether they require any prior-government-employment disclosure, what lookback window they use, and what positions count as "covered." A state-level revolving-door rubric would need to first inventory which states require *any* prior-government-employment disclosure on the lobbyist registration form, then characterize the lookback window and the position scope. (Outside this paper.)
2. **Branch / position taxonomy.** The five-category scheme (member of Congress, congressional staff, White House, federal bureaucracy, judiciary) maps awkwardly to state government. State legislators are part-time in many states; gubernatorial staff and agency political appointees are far smaller in number than their federal analogues; "leadership" structure differs by chamber size. The within-Congress staff hierarchy (member personal / committee / leadership) — which is the paper's most empirically diagnostic variable — would need rebuilding from scratch for each state legislature, and committee infrastructure varies by state.
3. **Biographical infrastructure.** The paper relies on LegiStorm, CQ First Street, CRP's lobbyist directories, and Lobbyists.info — all of which are essentially non-existent or radically thinner at the state level. Any state-level replication would either need to fund a comparable manual coding effort (the authors used three RAs for an academic year on a 1614-lobbyist sample) or to accept much more incomplete biographical reconstruction.

**(b) The transparency loophole is itself federal-statute-specific.** The paper's headline finding — that 67% of revolving-door lobbyists fail to self-report covered-official status because the LDA only requires it once — is a finding *about LDA's design*. The analogous question at the state level is "does this state require continuing disclosure of prior government employment, or only one-time?" That is a yes/no rubric item per state.

**(c) Sample is single year (2008).** Authors flag this. They cannot speak to time trends.

**(d) Subsequent-only revolving door.** The paper measures government-to-private (subsequent-private-sector). It does not measure private-to-government, nor lobbyists who go back and forth ("future-deferred-bribe" channel). State research could in principle do better here if state government employee records are accessible.

**(e) The measure of access is indirect.** Clientele diversity (Shannon's H over 13 economic sectors) is the paper's *inference* about access vs. expertise. It is not a direct observation of access. The paper is explicit about this — they treat clientele diversity as an "empirical manifestation of expertise or access" because direct self-reports of motivation would not be valid.

> "We thus infer lobbyists' primary mode of influence – access or expertise – based on the considerable variation in their respective clienteles." [811–814]

**(f) Former-member null is uninformative.** With only 12 former members in the sample, the standard error swamps the point estimate (0.111, SE 0.124). The authors caution against reading the null as evidence of "no effect."

**(g) Bureaucracy result reverses sign expectation.** Former bureaucrats have *more* concentrated clienteles, not more diverse — consistent with industry-specific regulatory expertise (the agency-capture story) rather than access-peddling. This is a substantive finding worth flagging for any state-level analogue: not all revolving-door types are alike, and a one-size-fits-all "RD = bad / diverse" mental model is wrong on this paper's evidence.

**(h) Reform recommendations are construct-relevant.** The paper recommends: (i) expand statutory definition of "lobbying activities"; (ii) require lobbyists to file a more complete employment-history record (continuing disclosure, not one-time); and (iii) shift some disclosure burden onto government officials themselves (members, WH staff, bureaucrats reporting contacts with former colleagues). These map directly to potential state-rubric items: continuing disclosure of prior employment, scope of the "lobbying activity" definition, and post-employment cooling-off rules.

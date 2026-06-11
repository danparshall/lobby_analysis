# State Lobbying Disclosure Regimes Differentiated by Target of Lobbying Activity

## Bottom Line for Data-Modeling Decision

**Approximately 8 states have unambiguous, statute-level multiple disclosure regimes that turn on the type of entity being lobbied** (Ohio, Florida, California, New York, New Jersey, Illinois, North Carolina, Massachusetts), with **roughly 4–6 additional states** in a "borderline" zone where disclosure differentiation exists but is debatable as to whether it rises to the level of a true regime split (Connecticut, Tennessee, Kentucky, Louisiana, Pennsylvania, plus various state-pension placement-agent policies that overlay general lobbying laws). That count is at the threshold where a **first-class "regime" axis on FieldRequirement is warranted** rather than a notes field — even if only ~8 states have clean statutory regime splits, the differentiation in those states is structural (different statutes, different administrators, different forms, different filing cadences) and cannot be cleanly modeled as scope-of-one-regime variation.

This memorandum walks through the verified regimes, then flags borderline cases, and closes with caveats about freshness.

---

## 1. States with Clear Multiple Disclosure Regimes

### Ohio — Three Separate Statutory Regimes
Ohio is the cleanest example in the country. Lobbying is partitioned by target into three distinct "engagements" — the same lobbyist representing the same employer must register **three separate times** (with three separate filing fees) if they engage all three branches:

| Regime | Statute | Administrator |
|---|---|---|
| Legislative agent | ORC §§ 101.70–101.79 (and OAC 101-9) | Joint Legislative Ethics Committee / Office of the Legislative Inspector General (OLIG) via the Ohio Lobbying Activity Center (OLAC) |
| Executive agency lobbyist | ORC §§ 121.60–121.69 (and OAC 101-11) | OLIG via OLAC |
| Retirement system lobbyist | ORC §§ 101.90–101.99 | OLIG via OLAC |

Disclosure-rule differences include: (a) **different registration cycles** — legislative engagements expire December 31 of every even-numbered year (biennial), while executive and retirement engagements expire January 31 each year (annual); (b) **separate Activity & Expenditure Reports** for each engagement type, filed tri-annually (May 31, September 30, January 31); (c) the retirement-system regime has unique "financial transaction" disclosure obligations that do not appear in the legislative or executive regimes; and (d) the retirement-system regime defines "expenditure" with respect to a different universe of recipients (board members, investment officials, employees with substantial discretion).

### Florida — Bifurcated Legislative and Executive Branch Regimes
Florida has the most explicit two-branch split among states:

| Regime | Statute | Administrator |
|---|---|---|
| Legislative branch lobbying | Fla. Stat. §§ 11.045–11.062 + Joint Rule One | Florida Legislature's Lobbyist Registration Office (within Office of Legislative Services) |
| Executive branch lobbying | Fla. Stat. § 112.3215 + Rule Chapter 34-12, FAC | Florida Commission on Ethics |

Disclosure-rule differences: (a) **different administering bodies** (the Legislature itself versus an independent ethics commission); (b) **different registration fees** ($50 first principal / $20 each additional for legislative; $25 per principal for executive); (c) **separate registration forms** in a single online portal but with different login credentials; (d) the executive-branch regime is funded through a dedicated Executive Branch Lobby Registration Trust Fund; (e) different administrative-rule frameworks govern the two regimes. Quarterly compensation reports are required of lobbying firms in both regimes but must be filed separately for each.

### California — General Lobbying + Placement-Agent Overlay
California's Political Reform Act (Cal. Gov. Code §§ 81000 et seq., particularly §§ 86100–86300) regulates lobbyists generally, administered by the **Fair Political Practices Commission (FPPC)** with filings handled by the Secretary of State. AB 1743 (2010) layered a separate placement-agent regime on top:

| Regime | Statute |
|---|---|
| General state lobbying | Gov. Code §§ 81000 et seq. (esp. §§ 82039, 86100 et seq.) |
| Placement agents (state public retirement systems) | Gov. Code §§ 7513.8, 7513.85–7513.95, 82002, 82025.3, 82039, 82047.3, 86100 et seq. |

A "placement agent" soliciting CalPERS, CalSTRS, or other state public retirement systems must register as a lobbyist (Forms 601/602/603/604), even though the agent does not communicate with the legislature or with traditional executive officials — registration is triggered by the targeted-entity status (state pension fund). The "administrative action" definition is expanded uniquely for placement agents to include retirement-system investment contracting decisions. Local public retirement systems trigger compliance with applicable local ordinances, layering a third regime in many California municipalities (Los Angeles, San Diego, San Francisco). Disclosure-rule differences: AB 1743 effectively imposes the entire PRA disclosure architecture (registration, periodic reports, gift disclosures, contribution limits) on persons whose activity would not otherwise count as "lobbying."

### New York — General Lobbying + Procurement Overlay + Placement-Agent Ban
New York has the most layered structure of any state:

| Regime | Statute | Administrator |
|---|---|---|
| General lobbying | Legislative Law §§ 1-a to 1-x (the "Lobbying Act") | Commission on Ethics and Lobbying in Government (COELIG, formerly JCOPE) |
| Procurement lobbying / restricted period | State Finance Law §§ 139-j, 139-k (Ch. 1 L. 2005, as amended Ch. 596 L. 2005); Legislative Law § 1-t | Advisory Council on Procurement Lobbying / Office of General Services (OGS); each procuring governmental entity also collects records of contact |
| Common Retirement Fund placement agents | Retirement & Social Security Law § 424-A; Ch. 203 L. 2018 codifying Comptroller's policy; 11 NYCRR Part 136-2 (DFS regulations) | NY State Comptroller (Office of the State Comptroller) |

Disclosure-rule differences: (a) **completely different forms and forms-collectors** — the COELIG bi-monthly lobbying reports are wholly separate from the §139-k "Record of Contact" forms maintained by each procuring agency, which are wholly separate from the Comptroller's Placement Agent Disclosure Letter; (b) the procurement regime applies to all procurements above a $15,000 annualized threshold and creates a "Restricted Period" with mandatory contact logs; (c) the Common Retirement Fund regime, since the 2018 codification, prohibits placement-agent use entirely (so the disclosure rules are now functionally limited to certifications of non-use rather than disclosure of fees) — but disclosure language and form letters remain in OSC policy. **Note**: post-2018 the placement-agent regime is largely a ban rather than a disclosure regime; pre-2018 it was a true disclosure regime, and the 2018 statute still requires investment-manager certifications, which are disclosure obligations.

### New Jersey — General Lobbying + Pay-to-Play Disclosure
New Jersey has at least two regimes administered by the same body but with fundamentally different filings:

| Regime | Statute | Administrator |
|---|---|---|
| General lobbying ("governmental affairs agents") | N.J.S.A. 52:13C-18 et seq. | Election Law Enforcement Commission (ELEC) |
| Pay-to-play disclosure (Form BE) | N.J.S.A. 19:44A-20.3 through 20.27 | ELEC (with parallel Local Public Contracts Law disclosures filed with contracting agencies) |
| Placement agents (NJ Division of Investment) | Treasury Department directive / SIC policies | NJ Treasury / State Investment Council |

Disclosure-rule differences: (a) Form BE captures a wholly different universe — it is filed annually (March 30 deadline) by **business entities** with NJ contracts of $50,000 or more reporting **political contributions**, not lobbying contacts; (b) reportable-contribution thresholds have changed — $300 pre-2023 Elections Transparency Act, $200 thereafter — and the change occurred mid-year, creating significant compliance friction; (c) the placement-agent regime layered onto NJ Division of Investment dealings is policy-based rather than statutory and does not cleanly map to ELEC lobbying disclosure. Form BE is best understood as a procurement-disclosure regime distinct from but adjacent to general lobbying.

### Illinois — General Lobbying + Procurement-Communications Reporting
Illinois operates two parallel disclosure systems:

| Regime | Statute | Administrator |
|---|---|---|
| General lobbying | Lobbyist Registration Act, 25 ILCS 170 | Illinois Secretary of State |
| Procurement-communications reporting | Illinois Procurement Code, 30 ILCS 500/50-38 (lobbyist disclosure) and 30 ILCS 500/50-39 (procurement communications) | Procurement Policy Board (with Executive Ethics Commission rules) |

Disclosure-rule differences: (a) the general regime requires **semi-monthly expenditure reports** filed with the Secretary of State (one of the most onerous reporting cadences in the country); (b) the procurement-communications regime requires reports of any substantive communication with a State employee on a procurement matter, filed promptly with the Procurement Policy Board (within 7 days) and posted on a separate searchable database; (c) §50-38 imposes parallel disclosure obligations on bidders/offerers (compensation paid to lobbyists, plus listing of any lobbyists among bid disclosures), separate from the lobbyist's own filings. The two regimes have entirely different fields (procurement communications include a detailed contact log with date, time, duration, location, telephone numbers, and substance, none of which appear in the standard lobbying expenditure report).

### North Carolina — Lobbyist + Liaison Regimes
North Carolina splits lobbying disclosure based on whether the registrant is private-sector or public-sector:

| Regime | Statute | Administrator |
|---|---|---|
| Lobbyist (private, including those representing local-government clients) | N.C. Gen. Stat. Ch. 120C, Articles 2 and 4 | NC Secretary of State (Lobbying Compliance Division) |
| State-agency liaison (state employees lobbying for their agency) | N.C. Gen. Stat. § 120C-500 | NC Secretary of State |
| Local-government employee "liaison equivalents" | N.C. Gen. Stat. § 120C-502 | NC Secretary of State |

Disclosure-rule differences: (a) liaison registrations use a different form ("State Agency Liaison Registration and Authorization Statement"), have **no registration fee** (versus the $500 lobbyist/principal fee imposed by S.L. 2023-134), and require dual signatures by the liaison and the State Agency Contact Person; (b) liaisons must register within one day of lobbying (rather than the "before lobbying" rule for lobbyists); (c) liaisons file quarterly reports regardless of activity, while lobbyist principals' reporting is keyed to expenditures; (d) the State Ethics Commission and the Secretary of State have **bifurcated jurisdiction** — Secretary handles registration and expenditure-reporting violations, Ethics Commission handles gift-ban and revolving-door issues. State agencies are also limited to two designated liaisons each (with statutory exceptions for the Department of Public Safety and the judicial branch's Chapter 7A entities).

### Massachusetts — Legislative Agent vs. Executive Agent
Massachusetts uses a single statute (M.G.L. c. 3, §§ 39–50) but defines two distinct agent types based on lobbying target:

| Regime | Definition |
|---|---|
| Legislative agent | Person who for compensation engages in legislative lobbying |
| Executive agent | Person who for compensation engages in executive lobbying (including communications with covered executive officials about policy or procurement) |

Disclosure-rule differences: (a) **separate registration trigger thresholds** — an individual must register if they agree to engage in legislative or executive lobbying for more than 25 hours during a six-month reporting period AND receive more than $2,500 in compensation during the same period — but these thresholds are computed **separately** for legislative and executive lobbying, not aggregated; (b) registration is on a single docket but the agent is identified as "legislative," "executive," or both; (c) the same lobbyist who hits only the executive trigger but not the legislative trigger registers only as an executive agent, with disclosure scope correspondingly limited. The administering body (Secretary of the Commonwealth's Lobbyist Division) is the same. Massachusetts is borderline between "single regime with target-segmented thresholds" and "two regimes" — the statute treats them as functionally separate categories with separate triggers, which is meaningful for a data model.

---

## 2. Borderline Cases (Disclosure Differentiation Exists but Whether it Rises to a "Regime Split" is Debatable)

### Connecticut
Connecticut distinguishes **client lobbyists** vs. **communicator lobbyists** (Conn. Gen. Stat. §§ 1-91, 1-95; Conn. Agencies Regs. § 1-92-41), with different reporting forms (client lobbyists file quarterly ETH-2D financial reports; communicator lobbyists file annual ETH-2A reports). The statute also distinguishes "legislative lobbying" from "administrative lobbying" (administrative lobbying covers executive/quasi-public agency action on rules, contracts, grants, awards, and purchasing). However, the same registration covers both legislative and administrative lobbying — the legislative/administrative distinction affects the substantive trigger and reporting fields but not the registration form itself. **This is a registrant-role split rather than a target-of-lobbying split, and probably should be modeled as scope variation rather than a separate regime.**

### Tennessee
A lobbyist who is a member of a commission established by and responsible to the General Assembly, or who is a member of a state regulatory commission, must file a separate "Sworn Disclosure of Consulting Services" form (T.C.A. §§ 2-10-125 and 2-10-126). General lobbying is governed by T.C.A. §§ 3-6-301 et seq. and administered by the Tennessee Ethics Commission. Tennessee's general lobbying registration covers both legislative and executive lobbying via a single form. **Borderline because the consulting-services overlay is a special disclosure but does not create a parallel registration regime.**

### Pennsylvania
The Lobbying Disclosure Act (65 Pa.C.S. Ch. 13A) administered by the Department of State covers both legislative and executive lobbying with a single registration. In February 2017 the Pennsylvania Treasurer issued a directive prohibiting investment managers from using third-party placement agents for funds managed on behalf of the Commonwealth Treasury Department. This is a substantive prohibition rather than a disclosure regime, but it is sometimes referenced alongside placement-agent disclosure regimes. **Not a regime split for present purposes.**

### Kentucky and Louisiana
Both states figured in the late-2000s pay-to-play scandals and have adopted some pension-fund placement-agent compliance measures, but the K&L Gates 2015 survey indicates these are pension-board policies and political-contribution restrictions rather than statutory lobbying-disclosure regime splits. Florida, Indiana, Massachusetts, and New Jersey are also identified by the K&L Gates survey as states whose general lobbying laws may capture placement-agent activity, but only New Jersey has a separate statutory disclosure regime (Form BE) layered on top.

### New Mexico
The New Mexico Educational Retirement Board and the State Investment Council each adopted **placement-agent disclosure policies** following the Aldus Equity scandal — but these are board policies attached to investment contracting, not separate statutory lobbying regimes. The general lobbying regime under the Lobbyist Regulation Act (NMSA §§ 2-11-1 to 2-11-9) is single-track and administered by the Secretary of State. **Not a regime split.**

### Other Pension-Board Placement-Agent Policies (Not Counted as Lobbying-Regime Splits)
The 2009–2011 "pay-to-play" wave produced placement-agent disclosure policies at numerous state pension funds (NYC's five retirement systems, CalSTRS, Maryland State Retirement and Pension System, Texas pension systems, Iowa PERS, Colorado PERA, Hawaii ERS, Connecticut Retirement Plans and Trust Funds, etc.). These are typically **internal investment-board policies** requiring disclosure of placement-agent fees in investment-manager contracts — they are not the same as state lobbying-law disclosure regimes. Treating them as separate regimes would explode the count without illuminating data structure.

---

## 3. Summary Count by Regime-Overlay Type

| Overlay Type | States with Clear Statutory Disclosure Regime |
|---|---|
| Legislative-vs-executive split (separate registrations or thresholds) | Florida, Massachusetts, Ohio (legislative + executive components) |
| Retirement / pension-system lobbying as separate regime | Ohio (statutory) |
| Procurement lobbying (restricted-period contact logs) | New York (§§139-j/k), Illinois (30 ILCS 500/50-39), Florida (procurement is folded into executive-branch regime) |
| Pay-to-play / business-entity political-contribution disclosure tied to procurement | New Jersey (Form BE) |
| Placement-agent registration as lobbyists (statutory) | California (AB 1743), Ohio (retirement-system regime captures placement agents) |
| Placement-agent disclosure required by statute (without lobbyist registration) | New York (CRF / RSSL §424-A and 2018 codification, now a ban with disclosure certifications) |
| State-agency liaison / local-government liaison separate registration | North Carolina |
| Borderline (different fields/cadence within a single regime, depending on target) | Connecticut, Tennessee |

**Hard count of states with multiple statutory disclosure regimes (broad definition): 8** (Ohio, Florida, California, New York, New Jersey, Illinois, North Carolina, Massachusetts).

**Adding borderline cases: ~10–12** depending on how strictly one defines "regime."

---

## 4. Discussion of Borderline Cases

The hardest classification call is **Massachusetts**, where the statute uses a single docket and unified administering body (Secretary of the Commonwealth) but treats the legislative-agent and executive-agent designations as **independent categories with their own thresholds**. A lobbyist who lobbies the legislature for 30 hours at $3,000 in compensation and the executive branch for 20 hours at $1,000 must register only as a legislative agent, because the executive trigger is computed independently and is not crossed. This is functionally a regime split for compliance purposes, even though the registration form is shared.

**Connecticut's** client/communicator dichotomy and **Tennessee's** consulting-services overlay illustrate a different kind of differentiation — splits along the registrant-role or registrant-status axis rather than the target-of-lobbying axis. Whether to treat these as "regimes" in the data model depends on whether the model's regime axis is meant to capture *what is being lobbied* (target) or *who is doing the lobbying and what additional categorization applies to them* (registrant taxonomy). The user's taxonomy in the prompt is target-focused, which would push Connecticut and Tennessee out of the count.

The **placement-agent universe** is the most diffuse. California's AB 1743 is a clear statutory regime split because placement-agent activity that would not otherwise be "lobbying" is forced into the lobbying registration system. Ohio's retirement-system regime achieves the same result through a separately codified chapter. New York's CRF rules, post-2018, are now mostly a ban-plus-certification rather than a disclosure regime. Other states' pension-board placement-agent policies are not statutory and do not create separate disclosure regimes — they create contract-clause obligations.

**Procurement lobbying** is genuinely a separate regime in New York (statutory, with its own contact-log architecture) and Illinois (statutory, with a separate database and reporting cadence). In Florida, procurement lobbying is folded into the executive-branch lobbying definition. In most other states, procurement-lobbying disclosure is either nonexistent (Maine and many others exempt procurement) or subsumed under general executive-branch lobbying.

---

## 5. Caveats on Freshness

- **Post-2024 changes flagged or possibly missed.** This memorandum reflects sources current through 2024–2025. New York's lobbying landscape has been in flux since JCOPE was replaced by COELIG in 2022, and a lower-court ruling in 2023 raised constitutional questions about the new commission's authority — that litigation may still be unresolved. Verify current administrator status before relying on any New York filing assumption.
- **New Jersey's Elections Transparency Act of 2023** (P.L. 2023, c. 30) altered Form BE reporting thresholds (reducing the reportable-contribution threshold from $300 to $200) and modified the universe of reportable recipients (excluding certain political party committees). This is a recent change and any model should treat NJ disclosure thresholds as version-dated.
- **North Carolina S.L. 2023-134** added the $500 registration fee for both lobbyists and lobbyist principals, effective October 3, 2023. This does not change the regime structure but materially affects the registration fields.
- **Tennessee Public Chapter 1087 (2022)** expanded the Disclosure of Consulting Services to include "campaign services" contracts effective August 15, 2022.
- **Ohio's regulatory architecture** has been updated as recently as October 2025 (the JLEC Lobbying Handbook reissued in October 2025) without changing the three-regime structure.
- **The placement-agent regulatory environment has stabilized but is not static.** Several pension boards revisit their policies periodically; what was a true disclosure regime in 2010 may have hardened into a ban-with-certification in 2024. New York's 2018 statutory codification is the clearest example.
- **California's FPPC regulations interpreting AB 1743** continue to evolve; the "one-third exemption" for portfolio managers, the competitive-bidding exemption, and the ride-along exemption are interpretive guidance that has been refined since 2010.
- I did not independently verify every one of the 50 states for completeness. The states identified here are the ones for which I found clear statutory or regulatory evidence of multiple regimes; smaller states (Alaska, Wyoming, the Dakotas, Vermont, Delaware, Rhode Island) generally have a single unified lobbying regime, but exhaustive 50-state verification was outside the time budget.

---

## 6. Recommendation for the Data Model

Eight states with structural statutory regime splits — and another two to four borderline — is enough that a notes field will produce inconsistent compendium entries. The differentiations are not all of the same kind: some are different statutes, some different administrators, some different cadences, some different forms with different fields. A first-class **regime axis on FieldRequirement** (with enumerated values like `legislative`, `executive`, `retirement_system`, `procurement_restricted_period`, `placement_agent`, `liaison_state_agency`, `liaison_local_government`, `pay_to_play_business_entity`) is the right design choice. Connecticut's client/communicator and Tennessee's consulting-services overlays can be handled as a separate axis (registrant_role) rather than crowding the regime axis.

A nullable regime field (defaulting to `general` for the ~40 states without a meaningful split) keeps the simple cases simple while allowing Ohio, Florida, New York, California, Illinois, New Jersey, North Carolina, and Massachusetts to be modeled accurately.
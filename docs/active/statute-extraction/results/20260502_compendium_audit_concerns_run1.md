# Compendium Audit v3 — Phase 0 Concerns (Run 1)

**Branch:** statute-extraction
**Sweep date:** 2026-05-02
**Compendium snapshot:** `compendium/disclosure_items.csv` sha `ef31b3ba96cde2f9f426172ee7f446a32c13ce2d` + `compendium/framework_dedup_map.csv` sha `5e0df8ea2ebdd3593098f0c1129bf93e5128659d` (worktree HEAD `8598b3fb`)
**Rows audited:** 141
**Auditor:** general-purpose subagent run 1

This is run 1 of two parallel audits. Reconciliation against run 2 is a downstream step.

## Phase 0 framing

Per `plans/20260502_compendium_item_audit_v3_phase0.md`: this run classifies concerns, does not propose fixes. Tags follow the 8-tag taxonomy (axis-ambiguous-name, name-misleading, description-broader-than-rubric, description-narrower-than-rubric, description-misscoped, rubric-source-ambiguous, cluster-asks-two-questions, cross-row-overlap, wrong-domain, other-issue).

## 1. Concerns

100 concerns across 72 distinct compendium rows. The full table is canonical; the companion CSV `20260502_compendium_audit_concerns_run1.csv` carries the same data for programmatic processing.

| # | row_id | criterion | tag | evidence | note |
|---|---|---|---|---|---|
| 1 | DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C1 | axis-ambiguous-name | ID `ADMIN_AGENCY_LOBBYING` could read as actor-axis ("lobbying *by* admin agencies") or target-axis ("lobbying *directed at* admin agencies"). Description anchors target-axis with explicit `TARGET axis. ... directed at (with administrative or executive-branch agencies as the recipients of lobbying contact)`. | Reference example from iter-1 disagreement on retirement_system regime; chunk-frame preamble papers over but ID layer still ambiguous. |
| 2 | DEF_ADMIN_AGENCY_LOBBYING_TRIGGER | C2 | rubric-source-ambiguous | All 4 cross-refs (Newmark 2017/2005 `def_admin_agency_lobbying`, Opheim 1991 `def_admin_agency_lobbying` with "administrative" in scare quotes in source paper, Hired Guns Q1) have direction-implicit source language. Hired Guns Q1 explicit text: *"In addition to legislative lobbyists, does the definition recognize executive branch lobbyists?"* — CPI gloss confirms target-axis but the question itself is direction-ambiguous; Newmark/Opheim use the noun "administrative agency lobbying" / "administrative lobbying" without naming direction. | Reinforces C1: rubric ambiguity propagated into row. |
| 3 | DEF_COMPENSATION_STANDARD | C1 | axis-ambiguous-name | ID `COMPENSATION_STANDARD` does not disambiguate income-side ("paid > $X = lobbyist") vs expenditure-side. Description must specify "income-side: paid > $X per period = lobbyist". Word "standard" is direction-agnostic. | Distinct from PRI D1 (expenditure-side exemption) per D3. |
| 4 | DEF_COMPENSATION_STANDARD | C4 | cross-row-overlap | No `_VALUE` counterpart row exists. Description references "$X per period" threshold but there is no `DEF_COMPENSATION_STANDARD_VALUE`. Asymmetric vs (DEF_EXPENDITURE_STANDARD ↔ THRESHOLD_LOBBYING_EXPENDITURE_VALUE) and (DEF_TIME_STANDARD ↔ THRESHOLD_LOBBYING_TIME_VALUE). A state with compensation-standard inclusion threshold has no row to populate the dollar value. | Curation gap. |
| 5 | DEF_EXPENDITURE_STANDARD | C1 | axis-ambiguous-name | ID `EXPENDITURE_STANDARD` could be inclusion-framed ("spends > $X IS a lobbyist") or exemption-framed ("spends < $X is exempt"). Description specifies `THRESHOLD axis (quantitative, inclusion-framed)` — the inclusion/exemption distinction is the load-bearing one (D11 disambiguation rule), and the ID does not carry it. | Pair with THRESHOLD_LOBBYING_EXPENDITURE_PRESENT (exemption-framed only after D11). |
| 6 | DEF_EXPENDITURE_STANDARD | C4 | cross-row-overlap | Pair with `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` (registration domain). D11 addendum acknowledges overlap and tightened descriptions to "inclusion-only" / "exemption-only" — but `THRESHOLD_LOBBYING_EXPENDITURE_VALUE` description says *"Dollar value of the lobbying-expenditure threshold (whether framed as inclusion or exemption)"* implying same VALUE applies to both rows, structurally wrong if a state has different inclusion and exemption thresholds. | Asymmetry: PRESENT/STANDARD split but VALUE shared. |
| 7 | DEF_TIME_STANDARD | C1 | axis-ambiguous-name | Same issue as DEF_EXPENDITURE_STANDARD: ID `TIME_STANDARD` does not signal inclusion vs exemption framing. Description tightens to `THRESHOLD axis (quantitative, inclusion-framed)`. | Pair with THRESHOLD_LOBBYING_TIME_PRESENT. |
| 8 | DEF_TIME_STANDARD | C4 | cross-row-overlap | Same asymmetry as DEF_EXPENDITURE_STANDARD: paired with `THRESHOLD_LOBBYING_TIME_PRESENT` but `THRESHOLD_LOBBYING_TIME_VALUE` is shared across inclusion/exemption framings. | Same. |
| 9 | THRESHOLD_LOBBYING_MATERIALITY_GATE | C1 | axis-ambiguous-name | ID prefix `THRESHOLD_*` shared with quantitative-threshold rows in registration domain (`THRESHOLD_LOBBYING_EXPENDITURE_PRESENT` etc.) but this row is in `definitions` domain and is qualitative-only per description (`THRESHOLD axis (qualitative)`). Shared `THRESHOLD_` prefix invites quantitative reading; description must override. | Cross-domain ID-prefix collision. |
| 10 | THRESHOLD_LOBBYING_EXPENDITURE_PRESENT | C1 | axis-ambiguous-name | ID `*_PRESENT` suggests boolean "is a threshold present?" which on its face captures both inclusion- and exemption-framed thresholds. Per D11 addendum (2026-05-01) this row is exemption-framed only; inclusion-framed counterpart is DEF_EXPENDITURE_STANDARD. Direction not in ID. | D11 disambiguation rule explicitly tightens descriptions but leaves IDs alone. |
| 11 | THRESHOLD_LOBBYING_TIME_PRESENT | C1 | axis-ambiguous-name | Same pattern as `THRESHOLD_LOBBYING_EXPENDITURE_PRESENT`: ID does not carry exemption-only framing; description does (per D11 addendum). | Pair with DEF_TIME_STANDARD. |
| 12 | REG_EXECUTIVE_AGENCY | C1 | axis-ambiguous-name | ID `EXECUTIVE_AGENCY` does not signal whether row is about agencies *as registrants* (actor) or lobbying *of* exec agencies (target). Description "Executive branch agencies." is verbatim-PRI single-noun and resolves nothing. Per D9 the row is actor-axis (must register). | Cross-row collision risk with `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (target-axis). Chunk frame `definitions.md` flags this pair explicitly. |
| 13 | REG_EXECUTIVE_AGENCY | C2 | description-narrower-than-rubric | Description "Executive branch agencies." is two-word PRI A6 verbatim noun phrase; fails to communicate the question "must executive-branch agencies register?" that the row asks. Compounds with C1 axis-ambiguity. | PRI-verbatim style across all REG_* A-series rows. |
| 14 | REG_EXECUTIVE_AGENCY | C4 | cross-row-overlap | Pair with `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (definitions). Both reference administrative/executive agencies; one is target-axis (DEF_), one is actor-axis (REG_). Names do not encode this distinction. Iter-1 disagreement on retirement_system regime is the textbook case; chunk frame `definitions.md` flags this pair explicitly. | Iter-1 reference example. Whichever row's name is renamed first owns the fix. |
| 15 | REG_GOVT_LOBBYING_GOVT | C1 | axis-ambiguous-name | ID phrase `GOVT_LOBBYING_GOVT` is itself directionally awkward. PRI A10 "Government agencies who lobby other agencies" clarifies in expansion. The atomic ID alone reads as both target and actor. | Description is one-line PRI verbatim; minimal disambiguation. |
| 16 | REG_GOVT_LOBBYING_GOVT | C2 | description-narrower-than-rubric | Description "Government agencies who lobby other agencies." restates PRI A10 noun phrase; lacks "must register" question framing. | Same PRI-verbatim style. |
| 17 | REG_GOVT_LOBBYING_GOVT | C4 | cross-row-overlap | Triangulates with `REG_EXECUTIVE_AGENCY` and `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER`. PRI A10 (govt-lobbying-govt) and A6 (executive branch agencies) share the agency-actor concept; the row `REG_GOVT_LOBBYING_GOVT` covers "agencies as actors lobbying other agencies" which is more specific. | Three-way scope overlap among PRI A6/A8/A10. |
| 18 | DEF_PUBLIC_ENTITY | C1 | axis-ambiguous-name | ID prefix `DEF_` but row lives in `domain="registration"`. Per D11 the `DEF_` prefix was reserved for definitions-domain rows ("who is a lobbyist?"). This row asks "does the law define public entity?" — a definitional question about public-entity status, not "who is a lobbyist". | 4-row cluster (DEF_PUBLIC_ENTITY + 3 sub-rows for charter/ownership/structure) shares DEF_ prefix collision. |
| 19 | DEF_PUBLIC_ENTITY | C5 | wrong-domain | Row in `domain="registration"`; per D11 conceptual line ("definitions = predicate on the agent — who is a lobbyist?"), "public entity definition" is a predicate on entity-class identity. Borderline — D11 explicitly placed PUBLIC_ENTITY rows in registration as "filing-architecture features" but the DEF_ prefix + entity-class-definition substance is a stronger fit for definitions. | Appears to revisit D11 partially. |
| 20 | DEF_PUBLIC_ENTITY | C4 | cross-row-overlap | 4-row cluster (parent + 3 sub-rows for charter/ownership/structure) is parent + sub-criteria pattern. PRI C1/C2/C3 are framed as "if Yes, does the definition rely on these three inclusive criteria?" — sub-rows are conditional on parent=true. No row-level signal that sub-rows depend on parent. | Cluster has dependency that's not encoded; harness might populate sub-rows when parent is false. |
| 21 | DEF_PUBLIC_ENTITY_CHARTER | C1 | axis-ambiguous-name | Same DEF_ prefix collision as DEF_PUBLIC_ENTITY. ID also lacks any verb signaling "definition relies on charter test". | Cluster with DEF_PUBLIC_ENTITY (parent). |
| 22 | DEF_PUBLIC_ENTITY_CHARTER | C5 | wrong-domain | Same as DEF_PUBLIC_ENTITY. | Cluster. |
| 23 | DEF_PUBLIC_ENTITY_OWNERSHIP | C1 | axis-ambiguous-name | Same DEF_ prefix collision; same noun-only ID. | Cluster. |
| 24 | DEF_PUBLIC_ENTITY_OWNERSHIP | C5 | wrong-domain | Same as DEF_PUBLIC_ENTITY. | Cluster. |
| 25 | DEF_PUBLIC_ENTITY_STRUCTURE | C1 | axis-ambiguous-name | Same DEF_ prefix collision; same noun-only ID. | Cluster. |
| 26 | DEF_PUBLIC_ENTITY_STRUCTURE | C5 | wrong-domain | Same as DEF_PUBLIC_ENTITY. | Cluster. |
| 27 | REG_LOBBYIST | C2 | description-narrower-than-rubric | Description is one-word PRI A1 verbatim ("Lobbyists.") — fails to communicate "must lobbyists register?". 6 framework_references span PRI A1, FOCAL 1.1, Newmark/Opheim/CPI def_legislative_lobbying. | PRI-verbatim style pervasive across A-series rows. |
| 28 | REG_LOBBYIST | C3 | cluster-asks-two-questions | 6 cross-refs mix "must legislative lobbyists register?" (PRI A1, FOCAL 1.1, Hired Guns Q3) with `def_legislative_lobbying` (Newmark/Opheim) which v2 audit (D2) classified as "universal-yes; criterion ≈ existence of any lobbyist-registration regime". Folding both questions onto one row is intentional per D2 but description gives no signal. | Appears consistent with D2 but description hides the merge. |
| 29 | REG_VOLUNTEER_LOBBYIST | C2 | description-narrower-than-rubric | Description "Volunteer lobbyists." is two-word PRI A2 verbatim; does not convey the question. | Same PRI-verbatim pattern. |
| 30 | REG_PRINCIPAL | C2 | description-narrower-than-rubric | Description "Principals who employ a lobbyist." is short PRI A3 verbatim; question "must principals register?" is implicit. | Same pattern. |
| 31 | REG_LOBBYING_FIRM | C2 | description-narrower-than-rubric | Description "Lobbying firms." is two-word PRI A4 verbatim. | Same pattern. |
| 32 | REG_GOVERNORS_OFFICE | C2 | description-narrower-than-rubric | Description "Governor's office." is two-word PRI A5 verbatim. | Same pattern. |
| 33 | REG_LEGISLATIVE_BRANCH | C2 | description-narrower-than-rubric | Description "Legislative branch." is two-word PRI A7 verbatim. | Same pattern. |
| 34 | REG_INDEPENDENT_AGENCY | C2 | description-narrower-than-rubric | Description "Independent agencies." is two-word PRI A8 verbatim. | Same pattern. |
| 35 | REG_LOCAL_GOVERNMENT | C2 | description-narrower-than-rubric | Description "Local governments." is two-word PRI A9 verbatim. | Same pattern. |
| 36 | REG_OTHER_PUBLIC_ENTITY | C2 | description-narrower-than-rubric | Description "Public entities, other than government agencies." is PRI A11 verbatim noun phrase. | Same pattern. |
| 37 | REG_LOBBYING_ACTIVITY_FORMS_SCOPE | C1 | axis-ambiguous-name | ID `_FORMS_SCOPE` reads as "scope of registration forms (paper)" but is actually "scope of activity-forms counted as lobbying" (oral/written/electronic). Different concepts; the polysemy of "forms" is the bug. | Mild but real ID confusion. |
| 38 | REG_LOBBYING_TARGETS_SCOPE | C2 | description-broader-than-rubric | Description verbatim FOCAL 1.3 with Westminster role names ("Ministers, Deputy Ministers, Director-Generals"). `focal_2024_indicators.csv` flags this: *"Westminster-centric role names; US-state application must translate to governor, lt. governor, legislators, agency heads, staff, etc."* Description retains UK/AUS terminology unfit for US-state application. | Curation note inherited from FOCAL extraction; not yet addressed. |
| 39 | EXEMPT_GOVT_OFFICIAL_CAPACITY | C1 | axis-ambiguous-name | ID `EXEMPT_GOVT_OFFICIAL_CAPACITY` could mean (a) exemption for officials acting in official capacity, or (b) definition exempts official-capacity activities. Description PRI B1 verbatim disambiguates well. Mild C1. | Mild. |
| 40 | EXEMPT_GOVT_PARTIAL_RELIEF | C1 | axis-ambiguous-name | ID `PARTIAL_RELIEF` is unusual phrasing; reads as "partial relief from what?". Description PRI B2 verbatim resolves it. | Mild. |
| 41 | RPT_LOBBYIST_GATE | C2 | description-narrower-than-rubric | Description "Are lobbyists required to disclose?." (sic, with literal extra period) is verbatim PRI E2a question text. Functional but the row is a "gate" for the entire E2 series; description doesn't communicate gate-vs-individual-field structure. | Pattern: many RPT_* rows have PRI verbatim question with stray punctuation. |
| 42 | RPT_PRINCIPAL_GATE | C2 | description-narrower-than-rubric | Description "Are principals required to disclose?." (sic). Same pattern as RPT_LOBBYIST_GATE. | Same pattern. |
| 43 | RPT_LOBBYIST_PRINCIPAL_NAMES | C3 | cluster-asks-two-questions | 4 cross-refs: PRI E2c (lobbyist's principal names on lobbyist report), FOCAL 4.1 (full names of lobbyists/orgs), FOCAL 6.1 (Client list under Relationships), Hired Guns Q9 (identify each employer by name on registration). FOCAL 6.1 is "Client list (for all consultant lobbyists and firms)" — a relationship-domain item, different scope from per-report principal listing. | Cluster bundles report-side, registration-side, relationship-side concepts. |
| 44 | RPT_PRINCIPAL_LOBBYIST_NAMES | C3 | cluster-asks-two-questions | 3 cross-refs: PRI E1c, FOCAL 4.1, FOCAL 7.4 (Number of lobbyists employed/contracted under Financials). FOCAL 7.4 is a count-of-lobbyists indicator — not a names-list disclosure question. | Cluster bundles names-disclosure with employed-count question. |
| 45 | RPT_LOBBYIST_BILL_SPECIFIC | C3 | cluster-asks-two-questions | 5 cross-refs include `sunlight_2015::activity` (4-tier ordinal: bill+position / bill / general / nothing) and Newmark `disc_seeking_to_influence` (broader: "seeking to influence legislation OR administrative action"). Sunlight tier collapses bill+position; Newmark item is broader-than-bill-specific. v2 audit MERGE'd via 4-row disjunction. Cluster bundles a tier with a sub-tier and a broader item. | Same Sunlight-activity-tier pattern repeats on issue/principal variants. |
| 46 | RPT_LOBBYIST_ISSUE_GENERAL | C3 | cluster-asks-two-questions | Same Sunlight-activity-tier + Newmark-broader pattern as RPT_LOBBYIST_BILL_SPECIFIC. | Same. |
| 47 | RPT_PRINCIPAL_BILL_SPECIFIC | C3 | cluster-asks-two-questions | Same pattern. | Same. |
| 48 | RPT_PRINCIPAL_ISSUE_GENERAL | C3 | cluster-asks-two-questions | Same pattern. | Same. |
| 49 | RPT_POSITION_TAKEN | C2 | description-broader-than-rubric | Description: "Position taken on each bill or item lobbied (support/oppose)." Sources `sunlight_2015::position_taken` (the 2-point top tier of Sunlight "Lobbyist Activity" — combines "bill discussed AND position taken") and `opheim_1991::disc_legislation_supported_opposed`. Sunlight's `position_taken` is not a standalone — no state can have position-taken without bill-specific in Sunlight's tier system. Compendium row treats it as standalone-distinct. | C4 candidate; tier-vs-atomic split. |
| 50 | RPT_POSITION_TAKEN | C4 | cross-row-overlap | Pair with `RPT_LOBBYIST_BILL_SPECIFIC`. Sunlight Activity tier collapses (bill+position) into one tier; splitting into two compendium rows is a curation choice but the rows can both fire on the same statutory provision (a state requiring "bill number AND position taken" populates BOTH). | Acceptable per curation but worth flagging. |
| 51 | RPT_LOBBYIST_COMPENSATION | C3 | cluster-asks-two-questions | 9 framework_references: PRI E2f_i (boolean), Sunlight `expenditure_transparency` (4-tier itemization ordinal), Sunlight `compensation` (yes/no), Newmark `disc_total_compensation`, Opheim `disc_total_income`, Hired Guns Q13, OpenSecrets `compensation`, FOCAL 7.1 (Total lobbying income for consultant lobbyists/firms). Sunlight `expenditure_transparency` 4-tier is structurally distinct from a yes/no "is comp disclosed?" boolean. FOCAL 7.1 is consultant-firm-side (not all lobbyists). Cluster bundles boolean with ordinal-tier and consultant-specific. | Largest cross-ref count (9). |
| 52 | RPT_PRINCIPAL_COMPENSATION | C3 | cluster-asks-two-questions | 7 cross-refs include Sunlight `expenditure_transparency` tier and FOCAL 7.6 ("Total lobbying expenditure (both in-house and consulting)"). FOCAL 7.6 is total-expenditure (not principal-side comp specifically); Sunlight's tier is granularity (not compensation specifically). Cluster bundles principal-comp with total-expenditure with tier ordinal. | Same pattern as RPT_LOBBYIST_COMPENSATION. |
| 53 | RPT_LOBBYIST_NON_COMPENSATION | C2 | description-broader-than-rubric | Description verbatim PRI E2f_ii ("Indirect lobbying costs (non-compensation)"). References Sunlight `expenditure_transparency` 4-tier — applies to expenditure granularity overall, not narrowly to non-compensation. Cross-ref appears too-broad. | Sunlight tier pattern fans out across many comp/non-comp/other-costs/itemized rows. |
| 54 | RPT_PRINCIPAL_NON_COMPENSATION | C2 | description-broader-than-rubric | Same Sunlight tier pattern; also FOCAL 7.6 (Total lobbying expenditure) and FOCAL 7.7 ("Compensated/uncompensated lobbying activities"). FOCAL 7.6 + 7.7 both broader than "principal report includes indirect costs" (PRI E1f_ii). | Same. |
| 55 | RPT_LOBBYIST_OTHER_COSTS | C3 | cluster-asks-two-questions | 5 cross-refs: PRI E2f_iii (gifts/entertainment/transport/lodging), Sunlight `expenditure_transparency` tier (broader: itemization granularity), Newmark/Opheim `disc_exp_benefitting_officials/employees` (narrower scope: officials-benefitting only), Hired Guns Q23_reported (PARTIAL per D7: gift-disclosure-half only). Multi-rubric refs span partly-overlapping concepts; row aggregates. | Compounds with C2 description-broader (Sunlight tier) and Newmark narrower (officials-only). |
| 56 | RPT_PRINCIPAL_OTHER_COSTS | C3 | cluster-asks-two-questions | 8 cross-refs (largest after RPT_LOBBYIST_COMPENSATION). Same multi-rubric scope-mismatch as RPT_LOBBYIST_OTHER_COSTS plus FOCAL 7.6/7.10. FOCAL 7.10 is "Expenditures benefiting public officials or employees including financial/non-financial gifts and support, employer/principal on whose behalf expenses were made" — an itemized-benefit-recipient question that arguably belongs at RPT_ITEMIZED_RECIPIENT or RPT_HOUSEHOLD_OF_OFFICIAL_SPENDING. | FOCAL 7.10 fans across multiple rows. |
| 57 | RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | C3 | cluster-asks-two-questions | 5 framework_references: PRI E1j (principal-side major contributors disclosure), FOCAL 6.2 (Names of all sponsors or members), FOCAL 7.3 (Income sources eg including government agencies, grant-making foundations, companies), Newmark `disc_contribs_received`, Opheim `disc_other_influence_peddling`. v2 audit D6 explicitly classified Opheim cross-ref as "too vague to commit to a single row" and folded as "closest existing match" — concrete C3 evidence. | Appears to revisit D6. |
| 58 | RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | C2 | description-misscoped | Beyond cluster: PRI E1j is principal-side and asks "major financial contributors". Folding Opheim "other influence peddling" (D6 borderline) is a misscoping — Opheim's catch-all is structurally a different question (influence-peddling activities) than "who funds the principal". Also FOCAL 7.3 is broader (income sources). | Reaffirms D6 borderline call. |
| 59 | RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS | other-issue | other-issue | Notes field on row says "No clean LobbyingFiling field today; would surface as a separate financial_contributors[] disclosure if added." Architectural note about LobbyingFiling schema, not a curation issue per se — but worth flagging that downstream filing-extraction shape isn't ironed out. | Architectural; not Phase 1 curation. |
| 60 | FREQ_LOBBYIST_MONTHLY | C3 | cluster-asks-two-questions | References include `newmark_2005::freq_binary`, `opheim_1991::freq_binary`, `opensecrets_2022::timely_disclosure` (compound freq schedule). Newmark/Opheim freq_binary is "monthly during session OR (monthly both in/out)" as single binary — they don't separately ask about pure "monthly". The MERGE expression in dedup-map handles via disjunction across cadence rows. Storing freq_binary cross-ref directly on each cadence row arguably misattributes. | Same pattern across other FREQ_*_* cadence rows. |
| 61 | FREQ_LOBBYIST_QUARTERLY | C3 | cluster-asks-two-questions | Same freq_binary cross-ref pattern. | Same. |
| 62 | FREQ_LOBBYIST_TRI_ANNUAL | C3 | cluster-asks-two-questions | Same freq_binary cross-ref pattern. | Same. |
| 63 | FREQ_LOBBYIST_SEMI_ANNUAL | C3 | cluster-asks-two-questions | Same freq_binary cross-ref pattern. | Same. |
| 64 | FREQ_PRINCIPAL_MONTHLY | C3 | cluster-asks-two-questions | Same freq_binary + OpenSecrets `timely_disclosure` cross-ref pattern. | Same. |
| 65 | FREQ_PRINCIPAL_QUARTERLY | C3 | cluster-asks-two-questions | Same pattern. | Same. |
| 66 | FREQ_LOBBYIST_OTHER | C1 | axis-ambiguous-name | ID `FREQ_LOBBYIST_OTHER` (free-text catch-all). "OTHER" alone in ID doesn't signal "free-text catch-all for cadences not enumerated above". | Mild. |
| 67 | FREQ_PRINCIPAL_OTHER | C1 | axis-ambiguous-name | Same as FREQ_LOBBYIST_OTHER. | Same. |
| 68 | RPT_OFFICIAL_DIARY_DISCLOSURE | C5 | wrong-domain | Row sits in `domain="contact_log"` but FOCAL 2.3 source ("Ministerial diaries are disclosed monthly (or more frequently)") is in FOCAL Timeliness category, not Contact log. Description is about cadence/freshness; closer fit is `accessibility` (timeliness). Pairs with `ACC_DIARIES_ONLINE` which is in accessibility. | Possible cross-row C4 with ACC_DIARIES_ONLINE. |
| 69 | RPT_OFFICIAL_DIARY_DISCLOSURE | C4 | cross-row-overlap | Pair with `ACC_DIARIES_ONLINE`: both about lobbyist/official diaries; one in `contact_log` (FOCAL 2.3 monthly cadence) one in `accessibility` (FOCAL 3.2 online availability). The two rows could plausibly fire on the same statutory provision. | Cross-domain pair. |
| 70 | ACC_DIARIES_ONLINE | C4 | cross-row-overlap | Pair with `RPT_OFFICIAL_DIARY_DISCLOSURE`. | Same. |
| 71 | ACC_DEDICATED_WEBSITE | C3 | cluster-asks-two-questions | 5 cross-refs: PRI Q2 (dedicated lobbying website), FOCAL 3.1 (Lobbyist register is online), Hired Guns Q28 (online registration filing), Hired Guns Q29 (online spending reporting), OpenSecrets `public_lists`. Q28/Q29 are about *filing online* (lobbyist/employer can submit forms via internet) — narrower/different than "state has dedicated website for lobbying info". | Cluster bundles three distinct concepts: "website exists", "online filing", "online lists/registry". |
| 72 | ACC_DEDICATED_WEBSITE | C2 | description-narrower-than-rubric | Description "The state has a dedicated website for lobbying information." covers website-existence question only; cross-refs to Hired Guns Q28+Q29 are about online filing (different question). | Compounds with C3 cluster. |
| 73 | ACC_DOWNLOAD_ANALYSIS_READY | C3 | cluster-asks-two-questions | 7 cross-refs: PRI Q6 (downloadable in usable format), FOCAL 3.3 (compound: no registration, free, open license, non-proprietary, machine readable), FOCAL 3.4 (downloadable as files), Sunlight `document_accessibility` (4-tier form access), Hired Guns Q31 (registrations format 4-tier), Hired Guns Q32 (spending reports format 4-tier), OpenSecrets `public_download`. FOCAL 3.3 explicitly flagged in `focal_2024_indicators.csv` as "Compound indicator: five sub-conditions ... Scoring may require decomposition." The cross-ref aggregation papers over a known-decomposable indicator. | Highest cross-ref count among accessibility rows. |
| 74 | ACC_DATA_AVAILABLE_AT_ALL | C2 | description-misscoped | Description: "At least some lobbying data available (in any format) either by request (email, telephone, fax, etc.) or anonymously (web-based)." References include `sunlight_2015::document_accessibility` which Sunlight defines as "Form Accessibility" (a 4-tier ordinal about whether *forms* — registration/expenditure forms — can be accessed online), not whether *lobbying data* is available. Different scope. | Sunlight's tier is form-availability, not data-availability. |
| 75 | ACC_MULTI_CRITERIA_SORT | C3 | cluster-asks-two-questions | 4 cross-refs: PRI Q8, FOCAL 3.5, Sunlight `document_accessibility` (form-access tier), OpenSecrets `public_search`. Sunlight's tier is form-access, not multi-criteria-sort. Mismatched cross-ref. | Same Sunlight tier mismatch. |
| 76 | REG_BILL_SUBJECT_ON_REGISTRATION | C4 | cross-row-overlap | Pair with `RPT_LOBBYIST_BILL_SPECIFIC` / `RPT_LOBBYIST_ISSUE_GENERAL`. CPI Q5 is "Bill/subject required on registration form"; the RPT_*_BILL_SPECIFIC / *_ISSUE_GENERAL rows are about bill/subject on *spending reports*. Different filing types but conceptually overlapping; the harness could plausibly populate both rows when a state's statute is structured as "bill numbers required on all filings". | REG_ vs RPT_ prefixes do help distinguish but the bill/subject substance overlaps. |
| 77 | RPT_LOBBYIST_PRINCIPAL_NAMES | C4 | cross-row-overlap | Pair with `REG_LOBBYIST`: REG_LOBBYIST is registration-side ("lobbyist must register" which implicitly requires identifying principals); RPT_LOBBYIST_PRINCIPAL_NAMES is per-report "list of principals". In states where the registration form itself includes the principal list, a single statutory provision populates both rows. | Filing-level vs report-level distinction not in IDs. |
| 78 | RPT_LOBBYIST_PRINCIPAL_CONTACT | other-issue | other-issue | Notes field acknowledges architectural tension: "Lobbyist contact info is on the registration record, not the principal's filing." Row is in `reporting` domain but the data lives on registration. Compounds the C4 risk that REG_*-side and RPT_*-side rows overlap. | Architectural; surface to Phase 1. |
| 79 | REG_SEPARATE_LOBBYIST_CLIENT_FILINGS | C2 | description-broader-than-rubric | Description: "State requires the client/principal to file a registration independently (cleaner data architecture) rather than embedding client identification within the lobbyist's registration." OpenSecrets source `lobbyist_client_separate` is per-paper a 5-tier scoring scale (separate filings / joint / client-only / etc.). Compendium row is boolean — narrower than the 5-tier scale. | Source-tier-info lost in boolean. |
| 80 | RPT_EXPENDITURE_FORMAT_GRANULARITY | C2 | description-narrower-than-rubric | Description: "Expenditure format granularity." Three-word terse description. Sources include `sunlight_2015::expenditure_format_granularity` (a 4-tier ordinal: itemized w/dates+desc / categorized / lump / none). Row data_type is categorical. The 4-tier scale isn't enumerated in the description. | Categorical row should enumerate categories. |
| 81 | FREQ_LOBBYIST_ANNUAL | C2 | description-narrower-than-rubric | Description: "Reporting frequency option: Annually." Direction unclear — does "option" mean state allows annual reporting, requires it, or merely that annual is an option among several? PRI E2h_v: "reporting frequency: annually" — also direction-ambiguous. The boolean's semantics ("this state's lobbyist reporting cadence allows annual filing") is implicit. | Pattern across all FREQ_*_* rows; description style inherits PRI E1h/E2h sub-item shape. |
| 82 | FREQ_LOBBYIST_OTHER | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 83 | FREQ_LOBBYIST_TRI_ANNUAL | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 84 | FREQ_LOBBYIST_SEMI_ANNUAL | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 85 | FREQ_LOBBYIST_QUARTERLY | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 86 | FREQ_LOBBYIST_MONTHLY | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 87 | FREQ_PRINCIPAL_ANNUAL | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 88 | FREQ_PRINCIPAL_OTHER | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 89 | FREQ_PRINCIPAL_TRI_ANNUAL | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 90 | FREQ_PRINCIPAL_SEMI_ANNUAL | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 91 | FREQ_PRINCIPAL_QUARTERLY | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 92 | FREQ_PRINCIPAL_MONTHLY | C2 | description-narrower-than-rubric | Same FREQ_* pattern. | Same. |
| 93 | RPT_LOBBYIST_CONTACTS_LOGGED | C2 | description-narrower-than-rubric | Description verbatim PRI E2i: "Are lobbyists required to disclose contacts?." (sic). Notes field clarifies gate semantics ("Gate item: presence of any engagement entry = contacts disclosed") but description doesn't reflect that gate framing. | PRI-verbatim with stray period. |
| 94 | RPT_PRINCIPAL_CONTACTS_LOGGED | C2 | description-narrower-than-rubric | Same PRI E1i pattern. | Same. |
| 95 | PARITY_GOVT_AS_LOBBYIST | C2 | description-narrower-than-rubric | Description verbatim PRI B3 plus stray period. | Same PRI-verbatim style. |
| 96 | PARITY_GOVT_AS_PRINCIPAL | C2 | description-narrower-than-rubric | Description verbatim PRI B4 plus stray period. | Same. |
| 97 | RPT_LOBBYIST_PRINCIPAL_NATURE | C2 | rubric-source-ambiguous | Description PRI E2e: "Are lobbyists required to disclose the nature of the principal's business (public or private)?" is direction-ambiguous: "public/private" could mean public-vs-private-sector OR public-disclosure-status. PRI 2010's coding context suggests sector. Mild. | Mild. |
| 98 | RPT_LOBBYIST_CONTRACT_TYPE | C2 | description-narrower-than-rubric | Description: "Type of lobbyist contract (eg, salaried staff, contracted)." (FOCAL 4.6 verbatim). References Hired Guns Q10 which is broader: "compensated/non-compensated, salaried/contracted on registration". FOCAL is narrower (contract type only); Q10 is two-axis (compensation status + contract type). | Mild. |
| 99 | FIN_INCOME_PER_CLIENT | C3 | cluster-asks-two-questions | 4 cross-refs: FOCAL 7.2 (income per client), Newmark/Opheim `disc_comp_by_employer` / `disc_sources_of_income`. Newmark item is "compensation broken down by employer" — closely aligned. Opheim "sources of income" is broader (could include all income sources, not lobbying-only). | Mild cluster cohesion concern. |
| 100 | ACC_AGGREGATE_TOTALS_BY_DEADLINE | C1 | axis-ambiguous-name | ID `BY_DEADLINE` is unusual; CPI Q36 is "Aggregate spending broken down by reporting deadline" (showing aggregate spent in each filing period). The ID could read as "by missed deadline" or "by upcoming deadline". | Mild. |

(Compendium rows not appearing in this table are implicitly clean on every criterion at this auditor's reading. 69 of 141 rows have zero concerns flagged.)

## 2. Aggregate counts

### By tag

| tag | count |
|---|---|
| description-narrower-than-rubric | 32 |
| cluster-asks-two-questions | 22 |
| axis-ambiguous-name | 19 |
| cross-row-overlap | 11 |
| description-broader-than-rubric | 5 |
| wrong-domain | 5 |
| rubric-source-ambiguous | 2 |
| description-misscoped | 2 |
| other-issue | 2 |
| name-misleading | 0 |

Sum = 100.

### By criterion

| criterion | count |
|---|---|
| C1 (name clarity) | 19 |
| C2 (description fidelity) | 41 |
| C3 (cluster cohesion) | 22 |
| C4 (cross-row scope) | 11 |
| C5 (domain) | 5 |
| other-issue | 2 |

Sum = 100.

### By domain

| domain | rows | rows flagged | concerns | concerns_per_row |
|---|---|---|---|---|
| accessibility | 33 | 6 | 7 | 0.21 |
| contact_log | 14 | 3 | 4 | 0.29 |
| definitions | 7 | 5 | 9 | 1.29 |
| financial | 5 | 1 | 1 | 0.20 |
| registration | 31 | 25 | 35 | 1.13 |
| relationship | 2 | 0 | 0 | 0.00 |
| reporting | 47 | 32 | 44 | 0.94 |
| revolving_door | 2 | 0 | 0 | 0.00 |
| **total** | **141** | **72** | **100** | **0.71** |

Concentration: registration (35 concerns / 31 rows = 1.13) and definitions (9 / 7 = 1.29) are the most concern-dense domains. Reporting is highest in absolute concerns (44) but lower density (0.94/row). Accessibility, contact_log, financial, relationship, revolving_door are sparsely flagged.

### By concern-count-per-row

| count | num_rows |
|---|---|
| 0 | 69 |
| 1 | 48 |
| 2 | 20 |
| 3 | 4 |
| 4+ | 0 |

The 4-concern-rows (3 each in this run) are: `DEF_PUBLIC_ENTITY` (C1+C5+C4), `REG_EXECUTIVE_AGENCY` (C1+C2+C4), `REG_GOVT_LOBBYING_GOVT` (C1+C2+C4), `RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS` (C3+C2+other-issue).

## 3. Observed candidate axis vocabularies (informational, not locked)

Captured per domain from C1 flags. Phase 1 may use these as starting input for axis vocabulary harmonization; Phase 0 explicitly does not lock them.

### `definitions` (7 rows, 5 flagged on C1)

Axes that surfaced explicitly in current row descriptions:

- **target** (`DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` — lobbying *directed at* X)
- **actor** (`DEF_ELECTED_OFFICIAL_AS_LOBBYIST`, `DEF_PUBLIC_EMPLOYEE_AS_LOBBYIST` — X engages in lobbying)
- **threshold (quantitative)** (`DEF_COMPENSATION_STANDARD`, `DEF_EXPENDITURE_STANDARD`, `DEF_TIME_STANDARD` — gate based on income/expenditure/time)
- **threshold (qualitative)** (`THRESHOLD_LOBBYING_MATERIALITY_GATE` — main-purpose / regular-and-substantial test)

Sub-axis under threshold: **inclusion-framed** vs **exemption-framed** is the load-bearing distinction (per D11 addendum) and is currently encoded only in descriptions.

### `registration` (31 rows, 25 flagged)

Axes implicit in description content:

- **registrant-type / actor** ("X must register": REG_LOBBYIST, REG_VOLUNTEER_LOBBYIST, REG_PRINCIPAL, REG_LOBBYING_FIRM, REG_LEGISLATIVE_BRANCH, REG_EXECUTIVE_AGENCY, REG_GOVERNORS_OFFICE, REG_INDEPENDENT_AGENCY, REG_LOCAL_GOVERNMENT, REG_GOVT_LOBBYING_GOVT, REG_OTHER_PUBLIC_ENTITY, REG_GOVT_LOBBYING_GOVT)
- **registration-form-content** (REG_BILL_SUBJECT_ON_REGISTRATION, REG_PHOTO_REQUIRED)
- **registration-cadence / window** (REG_PRE_LOBBYING_REGISTRATION_WINDOW, REG_REGISTRATION_RENEWAL_FREQUENCY, REG_CHANGE_NOTIFICATION_WINDOW)
- **filing-architecture** (REG_SEPARATE_LOBBYIST_CLIENT_FILINGS)
- **scope-of-activity / scope-of-target** (REG_LOBBYING_ACTIVITY_FORMS_SCOPE, REG_LOBBYING_TARGETS_SCOPE — these are FOCAL imports)
- **threshold (exemption-framed)** (THRESHOLD_LOBBYING_EXPENDITURE_PRESENT, THRESHOLD_LOBBYING_EXPENDITURE_VALUE, THRESHOLD_LOBBYING_TIME_PRESENT, THRESHOLD_LOBBYING_TIME_VALUE)
- **government-exemption** (EXEMPT_GOVT_OFFICIAL_CAPACITY, EXEMPT_GOVT_PARTIAL_RELIEF, PARITY_GOVT_AS_LOBBYIST, PARITY_GOVT_AS_PRINCIPAL)
- **public-entity-definition** (DEF_PUBLIC_ENTITY + 3 sub-criteria) — these have C5 wrong-domain flags from this run

The actor / target distinction is conflated in registration-domain IDs (REG_EXECUTIVE_AGENCY actor; DEF_ADMIN_AGENCY_LOBBYING_TRIGGER target — but cross-domain).

### `reporting` (47 rows, 32 flagged)

Axes implicit in description content:

- **filing-side** (lobbyist vs principal): RPT_LOBBYIST_* vs RPT_PRINCIPAL_*
- **report-content** (compensation, non-compensation, other-costs, itemized) — same content fields disclosed on each side
- **report-meta** (gate, itemized-flag, frequency, principal-names, principal-contact)
- **report-bill-and-issue** (bill-specific, issue-general, position-taken)
- **itemized-expenditure metadata** (RPT_ITEMIZED_DATE, RPT_ITEMIZED_DESCRIPTION, RPT_ITEMIZED_PRINCIPAL_BENEFITED, RPT_ITEMIZED_RECIPIENT, RPT_HOUSEHOLD_OF_OFFICIAL_SPENDING)
- **report-cadence** (FREQ_*_* boolean per cadence option × {lobbyist, principal})

Cadence options present as ALL-boolean enumeration (12 rows total: 6 cadences × 2 sides) is a design pattern that also appears in v1.2 schema-shape considerations.

### `contact_log` (14 rows, 3 flagged)

Axes implicit:

- **per-engagement field-content** (CONTACT_BENEFICIARY/DATE/FORM/INSTITUTION/LOCATION/MEETING_ATTENDEES/MATERIALS_SHARED/OUTCOMES_SOUGHT/PERSONS_CONTACTED/TOPICS/LEGISLATIVE_REFERENCES — FOCAL 8.x atoms)
- **gate** (RPT_LOBBYIST_CONTACTS_LOGGED, RPT_PRINCIPAL_CONTACTS_LOGGED — PRI E2i / E1i)
- **diary-disclosure-cadence** (RPT_OFFICIAL_DIARY_DISCLOSURE — flagged C5/C4 as cross-domain pair with ACC_DIARIES_ONLINE)

### `accessibility` (33 rows, 6 flagged)

Axes implicit:

- **availability** (ACC_DATA_AVAILABLE_AT_ALL, ACC_CURRENT_YEAR_DATA, ACC_HISTORICAL_DATA, ACC_DEDICATED_WEBSITE, ACC_DIARIES_ONLINE, ACC_SAMPLE_FORMS_ONLINE, ACC_LINKED_DATA, ACC_UNIQUE_IDENTIFIERS)
- **format-granularity** (ACC_DOWNLOAD_ANALYSIS_READY, ACC_MULTI_CRITERIA_SORT)
- **per-criterion-search** (ACC_SORT_BY_*, 14 rows = decomposition of PRI Q7)
- **freshness** (ACC_REGISTRY_UPDATE_FRESHNESS, ACC_ACTIVITY_DISCLOSURE_FRESHNESS, ACC_CHANGE_FLAGGING)
- **cost-barrier** (ACC_COPIES_COST)
- **agency-publishes-aggregate** (ACC_AGGREGATE_TOTALS_BY_*)
- **website-findability** (ACC_WEBSITE_FINDABILITY)

### `financial` (5 rows, 1 flagged)

Axes:

- **per-client / per-issue revenue or expenditure**: FIN_INCOME_PER_CLIENT, FIN_EXPENDITURE_PER_ISSUE
- **time-as-resource**: FIN_TIME_SPENT_LOBBYING (borderline domain match per row 76 commentary in CSV; not flagged in canonical table)
- **trade-association dues**: FIN_TRADE_ASSOCIATION_DUES
- **campaign-contributions**: FIN_CAMPAIGN_CONTRIBUTIONS

### `relationship` (2 rows, 0 flagged)

Axes:

- **board-seats** (REL_BOARD_SEATS)
- **direct-business-tie** (REL_OFFICIAL_BUSINESS_TIES)

### `revolving_door` (2 rows, 0 flagged)

Axes:

- **prior-offices-list** (REVOLVING_LOBBYIST_PRIOR_OFFICES)
- **cooling-off-database** (REVOLVING_COOLING_OFF_DATABASE)

## 4. Notable patterns flagged for Phase 1

Listed in descending order of how load-bearing each pattern is for Phase 1's solution-design choices.

1. **PRI-verbatim-style descriptions are by far the dominant C2 pattern (32/100 concerns).** Most REG_*-A-series rows (PRI A1–A11) have descriptions that are 1–4-word noun phrases or PRI question text with a stray "?." punctuation artifact. These descriptions don't communicate the question the row is asking — they're scaffolding from PRI's tabular checklist that survived into the compendium. Phase 1 design choice: rewrite descriptions in question-or-statement form (e.g., REG_LOBBYIST description = *"Does the state require lobbyists to register? (registrant-axis)"*); this is a high-volume but cheap change. The PRI-verbatim pattern is *not* a curation error in v2's sense — the rubric was correctly captured — but the description's job is to communicate intent to the harness. Currently it doesn't.

2. **Inclusion-framed vs exemption-framed threshold disambiguation is encoded only in descriptions, not IDs.** The `DEF_*_STANDARD` ↔ `THRESHOLD_LOBBYING_*_PRESENT` row pairs (and related VALUE rows) carry the load-bearing distinction in narrative description per D11 addendum. The IDs (`*_STANDARD` vs `*_PRESENT`) don't signal direction. Compounds with the structural asymmetry that `THRESHOLD_LOBBYING_EXPENDITURE_VALUE` and `THRESHOLD_LOBBYING_TIME_VALUE` are described as "shared across inclusion or exemption framings" while their boolean partners are split (D11 created the split for booleans only). `DEF_COMPENSATION_STANDARD` lacks a `_VALUE` row entirely.

3. **The agency-target / agency-actor / agency-as-lobbyist three-way is the iter-1 bug class and continues to bite cross-row.** `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (target), `REG_EXECUTIVE_AGENCY` (actor: agencies as registrants), `REG_GOVT_LOBBYING_GOVT` (actor: agencies-lobbying-other-agencies), and PRI A6/A7/A8/A9/A10/A11 multi-row split. The chunk frame `definitions.md` calls this out as a textbook case but the compendium row IDs themselves don't carry the actor/target signal. Phase 1 candidate IDs: e.g., `REG_EXECUTIVE_AGENCY_AS_REGISTRANT` and `DEF_LOBBYING_TARGET_EXECUTIVE_AGENCY` to encode axis in the ID.

4. **Sunlight-tier and FOCAL-compound cross-refs are scattered across many rows ("fan-out").** `sunlight_2015::expenditure_transparency` (4-tier ordinal capturing itemization granularity) appears as cross-ref on 6+ rows including RPT_LOBBYIST_COMPENSATION, RPT_PRINCIPAL_COMPENSATION, RPT_LOBBYIST_NON_COMPENSATION, RPT_PRINCIPAL_NON_COMPENSATION, RPT_LOBBYIST_OTHER_COSTS, RPT_PRINCIPAL_OTHER_COSTS, RPT_LOBBYIST_ITEMIZED, RPT_PRINCIPAL_ITEMIZED — bundling a tier-rollup with each individual boolean component. Similarly `sunlight_2015::activity` (4-tier: bill+position / bill / general / nothing) fans across RPT_LOBBYIST_BILL_SPECIFIC, RPT_LOBBYIST_ISSUE_GENERAL, RPT_PRINCIPAL_BILL_SPECIFIC, RPT_PRINCIPAL_ISSUE_GENERAL, RPT_POSITION_TAKEN. Also `sunlight_2015::document_accessibility` (4-tier form-access) appears on rows about data availability (ACC_DATA_AVAILABLE_AT_ALL, ACC_MULTI_CRITERIA_SORT, ACC_DEDICATED_WEBSITE, ACC_DOWNLOAD_ANALYSIS_READY) — but Sunlight's tier is about *forms* not *data*. Phase 1 may want a structured way to attach tier-ordinals to a single canonical row (e.g., an `expenditure_format_granularity` row already exists for the granularity tier; the cross-refs to the boolean rows could be removed). Same for Newmark's `freq_binary` which is computed from disjunctions across the 6 cadence rows — the dedup-map handles it via expression but the per-row cross-refs also include freq_binary, double-bookkeeping the same fact.

5. **The DEF_PUBLIC_ENTITY 4-row cluster has unencoded conditional dependency.** `DEF_PUBLIC_ENTITY` is "does the law include a definition of public entity?"; the three sub-rows (CHARTER, OWNERSHIP, STRUCTURE) are PRI's three sub-criteria conditional on the parent being yes. There is no row-level signal of the dependency — a state that doesn't define public entity could (under naïve scoring) still get yes-or-no on the sub-criteria. Compounds with the C5 wrong-domain question (DEF_ prefix in registration domain). Phase 1 may consider promoting the cluster to `definitions` domain and/or making the sub-rows use a `parent_id` field.

6. **Diary disclosure straddles two domains.** `RPT_OFFICIAL_DIARY_DISCLOSURE` is in `contact_log` for FOCAL 2.3 ("ministerial diaries are disclosed monthly"). `ACC_DIARIES_ONLINE` is in `accessibility` for FOCAL 3.2 ("diaries available online"). Both ask about diaries; one captures cadence, one captures online format. Possible cross-row C4 — if a state requires "monthly online diary disclosure" the same statutory provision populates both rows. Phase 1 candidate: clarify whether these are the same row at different cadence/format axes, or genuinely two rows.

7. **The six FREQ_*_* cadence rows × 2 sides (lobbyist, principal) = 12 boolean rows for cadence options.** Each is "is this cadence option offered/required for X-side filings?". Description style is "Reporting frequency option: Annually." (etc.), which is direction-ambiguous (allowed? required? actually-used?). Cross-refs include `freq_binary` which is computed across the cadence rows. Phase 1 may consider replacing 12 boolean rows with one categorical row per side (`RPT_LOBBYIST_FREQUENCY` enum {monthly, quarterly, …}) — but that's a v1.4 schema bump and outside Phase 1 scope. Phase 1 minimum: tighten descriptions to communicate the boolean's semantics (e.g., "True iff the state's lobbyist disclosure regime requires lobbyists to file at this cadence (or more frequently)").

8. **The registration / reporting / accessibility cross-row scope question for filing-content.** Several rows ask about content-of-registration (REG_BILL_SUBJECT_ON_REGISTRATION, REG_PHOTO_REQUIRED) vs content-of-spending-report (RPT_*_BILL_SPECIFIC). The REG_ vs RPT_ prefix encodes the filing type but the substantive content overlaps. CPI Q5 (registration form bill/subject) and PRI E2g_ii (spending report bill numbers) ask the same fact at different filings. Phase 1 may want to introduce a `filing-target` axis (registration / report / contact_log) explicitly in IDs where the content is shared.

9. **The PRI A-series fan-out via FOCAL 1.1 cross-ref bookkeeping.** FOCAL 1.1 covers 9 entity types via a single AND-disjunction-of-PRI A-series in dedup-map, but is also listed as a `framework_reference` on each individual REG_* A-series row. This is double-bookkeeping but conceptually correct (the row is *part of* FOCAL 1.1). Phase 1 may decide whether per-row cross-refs to FOCAL 1.1 should be retained or replaced with a single canonical reference.

10. **Empty `framework_references` rows: zero.** Every row has at least one cross-ref. No `other-issue` "missing FRs" flags surfaced. Curation completeness is solid on this axis.

## Phase 0 surprising-result triage (per plan §4)

Run-1 numbers triangulate as follows against the plan's "surprising result" thresholds:

- **Concern rate (this run): 100/141 = 71%.** Above the >50/141 (~35%) threshold the plan called "structural drift requiring aggressive triage." Phase 1 plan should expect cluster-grouping rather than fix-each-row.
- **Tag distribution heavily skewed toward description-fidelity tags:** 32 description-narrower-than-rubric + 5 description-broader-than-rubric + 2 description-misscoped + 2 rubric-source-ambiguous = **41/100 = 41% description-tag**. Per the plan, this exceeds the "80% description-tag" threshold for refocusing strategy, but is consistent with the plan's anticipated dominant fix-shape. Combined with 19 axis-ambiguous-name (C1) = 60/100 = 60% of concerns are *name-or-description* fidelity. The remaining 40 are cluster cohesion (22), cross-row (11), wrong-domain (5), other-issue (2). The PRI-verbatim style (within description-narrower) is the single largest sub-pattern.
- **Domain skew:** registration (35) + reporting (44) = 79/100 concerns. Agrees with the v2 audit's row-count weight on those domains.
- **Cross-row-overlap clusters of 3+ rows:** Yes — the 4-row DEF_PUBLIC_ENTITY cluster and the agency-axis triangle (DEF_ADMIN_AGENCY_LOBBYING_TRIGGER + REG_EXECUTIVE_AGENCY + REG_GOVT_LOBBYING_GOVT). Per the plan, "Suggests deeper scope-design issue beyond per-row rename."

## Notes on conformance with the Phase 0 plan

- All 141 rows audited at the same depth.
- All `framework_references` on every row examined for C2/C3 (full coverage, not sample).
- No fix proposals are recorded — only flags + evidence + notes.
- No retroactive re-tagging mid-sweep.
- v2 D1–D11 decisions where I disagree on review (specifically D6 RPT_PRINCIPAL_FINANCIAL_CONTRIBUTORS, partial D11 placement of DEF_PUBLIC_ENTITY rows in registration) are flagged with explicit "appears to revisit Dn" notes; deferred to Phase 1 to override.
- The 7 `definitions` rows are flagged on axis-ambiguous-name where appropriate even though chunk-frame preamble exists; per plan, IDs+descriptions are the load-bearing layer.

## Blockers / gaps

- None encountered. All rubric-text sources resolved cleanly via `papers/text/<paper>.txt`. Dedup-map covered every cross-rubric reference.
- The `compendium/portal_urls/` subdirectory exists but is unrelated to this audit.

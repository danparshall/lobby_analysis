# Predecessor Lobbying-Regulation Papers — Download Manifest

Captured: 2026-05-03
Branch: `compendium-source-extracts`
Source list: parent agent's predecessor-paper checklist (Step 1 verify, Step 2 NGO/grey-lit URLs, Step 3 DOI-based academic papers, Step 4 books)

Conventions
- `retrieved` = PDF saved to `papers/<stem>.pdf` and text extraction at `papers/text/<stem>.txt`
- `already-on-disk` = file existed at session start; verified content matches
- `paywalled` = publisher returned 403 / 204 / login-required even after best-effort retries (no sci-hub used per policy)
- `not-found` = URL returned 404 / DNS-fail; no working alternative located
- `book-only` = source is a print book; not retrievable by URL
- `html-archive` = HTML page captured (page is not a PDF; saved as `.html` or as text under `papers/text/`)

## Step 1 — Already-on-disk (verified)

| Citation | Status | File | Notes |
|---|---|---|---|
| LaPira & Thomas 2020, "The Lobbying Disclosure Act at 25" (Interest Groups & Advocacy 9:257-271) | already-on-disk | `papers/LaPira_Thomas_2020__lobbying_disclosure_act_at_25.pdf` | Verified — Springer OA, doi 10.1057/s41309-020-00101-0 |
| GAO 2025, "2024 Lobbying Disclosure: Observations on Compliance with Requirements" (GAO-25-107523) | already-on-disk | `papers/GAO_2025__lda_compliance_audit.pdf` | Verified — April 2025 GAO report |
| Lacy-Nichols et al. 2025, "Lobbying in the Shadows: A Comparative Analysis of Government Lobbyist Registers" (Milbank Quarterly 103(3):857-882) | already-on-disk | `papers/Lacy_Nichols_2025__lobbying_in_the_shadows.pdf` | **Distinct from FOCAL ref #21.** This is the 2025 Milbank cross-country FOCAL application. The 2023 BMC paper ("Aiding empirical research on the commercial determinants of health") was missing and has now been retrieved separately (see Step 3). The FOCAL scoping review itself (Lacy-Nichols 2024, IJHPM) was also already on disk as `Lacy_Nichols_2024__focal_scoping_review.pdf`. |

## Step 2 — Direct-URL NGO / grey-literature

| Citation | Status | URL tried | File | Notes |
|---|---|---|---|---|
| ALTER-EU 2013, *Recommendations on Disclosure Requirements* | retrieved | https://www.alter-eu.org/sites/default/files/documents/recommendations%20disclosure%20requirements.pdf | `papers/ALTER_EU_2013__transparency_register_review.pdf` | 87 KB, application/pdf |
| Access Info / OK / Sunlight / TI 2015, *International Standards for Lobbying Regulation* | retrieved | https://lobbyingtransparency.net/lobbyingtransparency.pdf | `papers/AccessInfo_2015__intl_lobbying_standards.pdf` | 624 KB |
| SOMO 2016, *A Structural Problem in the Shadows: Lobbying by Banks in the Netherlands* | retrieved | https://www.somo.nl/wp-content/uploads/2016/11/A-structural-problem-1.pdf | `papers/SOMO_2016__structural_problem.pdf` | Original lobbywatch.nl URL was 404; corrected via web search to somo.nl host. 1.5 MB |
| Council of Europe 2017, *Legal Regulation of Lobbying Activities in the Context of Public Decision-Making* | retrieved | https://rm.coe.int/legal-regulation-of-lobbying-activities/168073ed69 | `papers/CouncilEurope_2017__lobbying_legal_regulation.pdf` | 481 KB |
| Transparency International 2016, *Open Data and EU Lobbying* | retrieved | https://images.transparencycdn.org/images/2016_OpenData_EULobbying_EN.pdf | `papers/TI_2016__open_data_eu_lobbying.pdf` | 2.6 MB; redirects to files.transparencycdn.org |
| IBAC 2022, *Special Report on Corruption Risks Associated with Donations and Lobbying* (Victoria) | retrieved | https://www.ibac.vic.gov.au/media/160/download | `papers/IBAC_2022__corruption_risks_donations_lobbying.pdf` | 323 KB. **First fetch** of `/media/161/download` returned the summary (92 KB); probed all media/ IDs on the publication page and replaced with the full report from `/media/160/download`. |
| Global Data Barometer 2022 | retrieved | https://globaldatabarometer.org/wp-content/uploads/2022/05/GDB-Report-English.pdf | `papers/GlobalDataBarometer_2022__report.pdf` | 37 MB — large file with all GDB indicators incl. lobbying transparency module |
| Carnstone / Meridian 2020, *The Responsible Lobbying Framework* | retrieved | https://static1.squarespace.com/static/5e85df904eec2417de2b4800/t/5ef1e5fd5d6e1015f5b171ef/1592911361771/The-Responsible-Lobbying-Framework_v-June2020.pdf | `papers/Carnstone_2020__responsible_lobbying_framework.pdf` | 713 KB. Retrieved via Squarespace 302 redirect from `/s/...` link on responsible-lobbying.org. |
| Roth 2020, "Creating a Valid and Accessible Robustness Index" (Google Sites + lobbymeter.eu) | html-archive | https://sites.google.com/view/regulating-lobbying/home/work-of-colleagues/creating-a-valid-and-accessible-robustness-index | `papers/text/Roth_2020__lobbymeter_robustness_index.txt` (summary) | Google Sites page, not a PDF. Captured a summary as text. The page references a downloadable list of 23 index items, but the PDF link is not directly accessible. Roth's underlying thesis appears at https://d-nb.info/136695582X/34 (not retrieved this session — flag for follow-up). |
| Strickland 2014, "Disentangling the Effects of Lobbying Laws on Interest Group Registrations 1988-2013" (SSRN abstract 2467944) | paywalled | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2467944 ; https://www.researchgate.net/publication/272302971/.../fulltext-download | — | SSRN abstract page returns 403 to all programmatic fetches. ResearchGate full-text download endpoint also 403. SSRN's `Delivery.cfm?...` direct URL also 403. Marked paywalled. The published version of Strickland's index work appears in Newmark/Strickland 2017 IGA (not on the request list — that 2017 article *is* however the one captured already as `Newmark_2017__lobbying_regulation_revisited.pdf` … note this is sole-author Newmark, so Strickland's working paper remains an independent unretrieved item). |
| CPI 2015 SII article "Only three states score higher than D+" | retrieved (HTML archive) | https://publicintegrity.org/politics/state-politics/state-integrity-investigation/only-three-states-score-higher-than-d-in-state-integrity-investigation-11-flunk/ | `papers/CPI_2015__sii_only_three_states.html` | Captured as HTML (260 KB). The original `publicintegrity.org/2015/11/09/18693/...` URL 404s; the article moved under the `/politics/state-politics/...` path. |
| CPI 2015 SII landing page | retrieved (HTML archive) | https://publicintegrity.org/topics/politics/state-politics/state-integrity-investigation/state-integrity-2015/ | `papers/CPI_2015__sii_2015_landing.html` | 249 KB. The original `accountability/state-integrity-investigation/state-integrity-2015` URL 302-redirects through `publicintegrity1.wpcomstaging.com`, then 301-redirects back to the canonical path. |

## Step 3 — DOI-based academic downloads

| Citation | Status | URL tried | File | Notes |
|---|---|---|---|---|
| Holman & Luneburg 2012, "Lobbying and transparency" (Interest Groups & Advocacy 1(1):75-104, doi 10.1057/iga.2012.4) | retrieved | https://link.springer.com/content/pdf/10.1057/iga.2012.4.pdf | `papers/Holman_Luneburg_2012__lobbying_transparency.pdf` | 278 KB, application/pdf — Springer OA |
| Brinig, Holcombe & Schwartzstein 1993, "The Regulation of Lobbyists" (Public Choice 77:377-384, doi 10.1007/BF01047876) | paywalled | https://link.springer.com/content/pdf/10.1007/BF01047876.pdf (also tried with cookie session: HTTP 204) | — | Springer redirects PDF URL to HTML cookie-required page; with cookies the PDF endpoint returns 204 No Content. Older Public Choice articles are not OA. Working paper or preprint not located. |
| Lowery & Gray 1997, "How Some Rules Just Don't Matter" (Public Choice 91:139-147, doi 10.1023/A:1017909514423) | paywalled | https://link.springer.com/content/pdf/10.1023/A:1017909514423.pdf ; https://instruct.uwo.ca/politics/392e-570/LoweryGray.pdf | — | Springer same as Brinig. UWO course page that web search surfaced returned an HTML 404 (not a PDF). |
| Hunter, Wilson & Brunk 1991, "Social Complexity and Interest Group Lobbying in the American States" (J. Politics 53:488-503, doi 10.2307/2131770) | paywalled | https://www.journals.uchicago.edu/doi/pdf/10.2307/2131770 | — | UChicago Press blocks programmatic access (403). No public preprint located. |
| Gray & Lowery 1998, "State Lobbying Regulations and Their Enforcement" (State and Local Government Review 30(2):78-91, doi 10.1177/0160323X9803000201) | paywalled | https://journals.sagepub.com/doi/pdf/10.1177/0160323X9803000201 | — | SAGE 403 to all programmatic fetches. No preprint located. |
| Ozymy 2010, "Assessing the Impact of Legislative Lobbying Regulations on Interest Group Influence in U.S. State Legislatures" (SPPQ 10(4):397-420, doi 10.1177/153244001001000406) | paywalled | https://journals.sagepub.com/doi/pdf/10.1177/153244001001000406 ; https://www.cambridge.org/core/services/aop-cambridge-core/content/view/C8E1BA7DF7A8E00432E9955025B8AD8F/.../...pdf | — | SAGE 403. Cambridge AOP "view" URL pattern returns the abstract HTML, not the PDF — confirmed via WebFetch that the article is paywalled at Cambridge. |
| Ozymy 2013, "Keepin' on the Sunny Side" (American Politics Research 41:3-23, doi 10.1177/1532673X11432470) | paywalled | https://journals.sagepub.com/doi/pdf/10.1177/1532673X11432470 | — | SAGE 403. No preprint located. |
| Flavin 2015, "Lobbying Regulations and Political Equality in the American States" (American Politics Research 43:304-326, doi 10.1177/1532673X14545210) | retrieved | https://blogs.baylor.edu/patrick_j_flavin/files/2010/09/Flavin_Lobbying_Regulations_Political_Equality_1.28.14-1p7e1zg.pdf | `papers/Flavin_2015__lobbying_regulations_political_equality.pdf` | 369 KB. Author-hosted preprint (dated Jan 2014, matches accepted manuscript). SAGE final version itself paywalled. |
| Vaughan & Newmark 2008, "The Irony of Ethics Research: When the Sun Don't Shine on Enforcement" (Public Voices 10:87-95) | not-found | https://publicvoices.newark.rutgers.edu/index.php/pv/article/download/100/82 (DNS fail); journal site appears offline | — | Public Voices is published by Rutgers SPAA; the journal's domain returned ECONNREFUSED. Newmark's CV confirms the citation but provides no PDF link. Article does not have a DOI. |
| Newmark & Vaughan 2014, "When Sex Doesn't Sell: Political Scandals, Culture, and Media Coverage in the States" (Public Integrity 16:121-144) | paywalled | https://www.tandfonline.com/doi/pdf/10.2753/PIN1099-9922160202 | — | T&F/Routledge 403. **Note:** the parent task list described this as "Lobbying regulation" but Newmark's 2024 CV confirms the actual title is "When Sex Doesn't Sell" about political scandals (only tangentially about lobbying enforcement). Likely lower compendium relevance than other items on this list. |
| LaPira & Thomas 2014, "Revolving door lobbyists and interest representation" (Interest Groups & Advocacy 3:4-29, doi 10.1057/iga.2013.16) | paywalled | https://link.springer.com/content/pdf/10.1057/iga.2013.16.pdf (cookie session: HTTP 204) | — | Springer Palgrave; not OA in 2014. No preprint located on author pages. |
| Witko 2005, "Measuring the Stringency of State Campaign Finance Regulation" (SPPQ 5:295-310, doi 10.1177/153244000500500306) | paywalled | https://journals.sagepub.com/doi/pdf/10.1177/153244000500500306 ; https://www.cambridge.org/core/.../.../...pdf | — | Both SAGE and Cambridge 403/abstract-only. Penn State faculty page lists the publication but does not host a PDF. |
| Witko 2007, "Explaining Increases in the Stringency of State Campaign Finance Regulation, 1993-2002" (SPPQ 7:369-393, doi 10.1177/153244000700700402) | paywalled | https://journals.sagepub.com/doi/pdf/10.1177/153244000700700402 ; Cambridge AOP variant | — | Same as Witko 2005. |
| Mihut 2008, "Lobbying in the United States and the European Union: New Developments" (Romanian Journal of European Affairs 8(4):5-17) | paywalled | https://rjea.ier.gov.ro/wp-content/uploads/articole/RJEA_2008_vol8_no2_art1.pdf (HTTP 503) ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1299580 (SSRN 403) | — | RJEA archive returned 503 Service Unavailable; SSRN abstract 1299580 returned 403. Note volume/issue: web search confirms the article is in vol 8, no. 4 (Dec 2008), so the "no2" guess was wrong even if the host had been up. |
| Hogan, Murphy & Chari 2008, "Next Door They Have Regulation, But Not Here..." (Canadian Political Science Review 2(3):125-151) | retrieved | https://ojs.unbc.ca/index.php/cpsr/article/download/43/116/371 | `papers/Hogan_Murphy_Chari_2008__regulating_lobbying_globally.pdf` | 558 KB. CPSR is OA via OJS at UNBC. |
| Bednářová 2020 (E+M Ekonomie a Management 23(2):42-58, doi 10.15240/tul/001/2020-2-003) | retrieved | https://doi.org/10.15240/tul/001/2020-2-003 (302 → dspace.tul.cz) | `papers/Bednarova_2020__lobbying_regulation_quality.pdf` | 1.1 MB. CC-licensed via Liberec University DSpace. |
| Laboutková & Vymětal 2022/23, "Public-Sector Trustworthiness Through Transparent Lobbying Regulations" (Policy Studies 44(3):336-355, doi 10.1080/01442872.2022.2053092) | paywalled | https://www.tandfonline.com/doi/pdf/10.1080/01442872.2022.2053092 | — | T&F 403. No preprint located. |
| McKay & Wozniak 2020, "Opaque: An Empirical Investigation of Lobbying Transparency in the UK" (Interest Groups & Advocacy 9:102-118, doi 10.1057/s41309-019-00074-9) | retrieved | https://livrepository.liverpool.ac.uk/3072829/1/McKay%20&%20Wozniak%202020%20-%20Opaque%20-%20An%20Empirical%20Investigation%20of%20Lobbying%20Transparency%20in%20the%20UK.pdf | `papers/McKay_Wozniak_2020__lobbying_transparency_uk.pdf` | 746 KB. Liverpool repo green OA. |
| Lacy-Nichols, Quinn & Cullerton 2023, "Aiding Empirical Research on the Commercial Determinants of Health: A Scoping Review of Datasets and Methods about Lobbying" (Health Research Policy and Systems 21:56, doi 10.1186/s12961-023-01011-8) | retrieved | https://health-policy-systems.biomedcentral.com/counter/pdf/10.1186/s12961-023-01011-8.pdf | `papers/Lacy-Nichols_2023__aiding_empirical_research_cdoh.pdf` | 1.15 MB. BMC OA. **This is the FOCAL ref #21 paper that was missing despite the 2024 FOCAL scoping review and 2025 cross-country FOCAL application both being on disk.** |
| Chung et al. 2024 (Milbank Quarterly, doi 10.1111/1468-0009.12686) | paywalled | https://onlinelibrary.wiley.com/doi/pdf/10.1111/1468-0009.12686 | — | Wiley 403 to programmatic access. |

## Step 4 — Books (not retrievable)

| Citation | Status | Notes |
|---|---|---|
| Rosenson, Beth A. 2005, *The Shadowlands of Conduct: Ethics and State Politics* (Georgetown University Press) | book-only | Print monograph; full text not legally available online. |
| Chari, Hogan, Murphy & Crepaz 2020, *Regulating Lobbying: A Global Comparison*, 2nd ed. (Manchester University Press) | book-only | Print monograph. The 2008 CPSR article (Hogan/Murphy/Chari, retrieved above) summarizes the same authors' index methodology that became the spine of this book. |
| Holman 2008, "Lobbying and Lobbying Regulation in the United States" (chapter in Conor McGrath ed., *Interest Groups and Lobbying in the United States and Comparative Perspectives*, Edwin Mellen Press) | book-only | Print book chapter. Holman & Luneburg 2012 (retrieved above) covers very similar ground from the same lead author. |

## Author-page hunt round 1 (2026-05-03, post-manifest)

User retrieved 5 additional papers from author pages / institutional repos and dropped them in `papers/` on the main worktree. Moved + renamed to standard convention + text-extracted into worktree:

| Citation | New file | Notes |
|---|---|---|
| Strickland 2014, "Disentangling the Effects of Lobbying Laws on Interest Group Registrations 1988-2013" | `papers/Strickland_2014__lobbying_laws_interest_groups.pdf` (1167 lines text) | Was paywalled; user grabbed from author page |
| Mihut 2008, "Lobbying in the United States and the European Union" | `papers/Mihut_2008__lobbying_us_eu.pdf` (609 lines text) | Was paywalled / RJEA archive 503; user grabbed RJEA Vol 8 No 4 PDF directly |
| Chung et al. 2024, "Mapping the Lobbying Footprint of Harmful Industries" | `papers/Chung_2024__mapping_lobbying_footprint.pdf` (761 lines text) | Was paywalled at Wiley; user found OA version |
| LaPira & Thomas 2014, "Revolving door lobbyists and interest representation" | `papers/LaPira_Thomas_2014__revolving_door_lobbyists.pdf` (1301 lines text) | Was paywalled at Springer; user grabbed PDF directly |
| **CPI 2015 SII article (Kusnetz)** | `papers/CPI_2015__sii_only_three_states.pdf` (491 lines text) | User-supplied PDF version of the Kusnetz "Only three states score higher than D+" article; replaces (alongside) the HTML archive captured in Step 2 |

## Summary counts (updated 2026-05-03)

| Status | Count |
|---|---|
| retrieved (download wave + author-hunt round 1) | 19 PDFs + 2 HTML archives + 1 text-only summary (Roth) |
| already-on-disk (verified) | 3 |
| paywalled (post-2000 — pending email round) | 5 (Witko 2005, Witko 2007, Ozymy 2010, Ozymy 2013, Laboutková & Vymětal 2022/23) |
| not-found (post-2000) | 1 (Vaughan & Newmark 2008 — Public Voices site offline) |
| paywalled (pre-2000 — out of email-round scope) | 4 (Brinig 1993, Hunter 1991, Lowery & Gray 1997, Gray & Lowery 1998) |
| thin-version only | 1 (Roth 2020 — d-nb.info thesis not yet retrieved) |
| book-only | 3 |

Total candidates worked: 34

## Tricky retrievals / things to flag for the user

1. **Lacy-Nichols 2025 vs 2023.** The on-disk `Lacy_Nichols_2025__lobbying_in_the_shadows.pdf` is **not** FOCAL ref #21. It is the 2025 Milbank cross-country FOCAL application. The 2023 BMC paper "Aiding empirical research on the commercial determinants of health" (HRPS 21:56) was missing and is now retrieved as `Lacy-Nichols_2023__aiding_empirical_research_cdoh.pdf`. The 2024 IJHPM FOCAL scoping review was already on disk separately as `Lacy_Nichols_2024__focal_scoping_review.pdf`.
2. **IBAC 2022.** The PDF link in the task description (`/publications-and-resources/article/...`) is the article landing page. The summary PDF lives at `/media/161/download` and the **full report** at `/media/160/download`. First fetch returned the summary; replaced with the full report after probing all media-ID downloads on the page.
3. **Newmark & Vaughan 2014 title mismatch.** The parent task list framed this as "Lobbying Regulation in the American States" but Newmark's 2024 CV confirms the published Public Integrity 16:121-144 paper is actually "When Sex Doesn't Sell: Political Scandals, Culture, and Media Coverage in the States." This is a scandals/media paper, only tangentially about lobbying. May warrant deprioritization in compendium use.
4. **Carnstone 2020.** The framework PDF is hosted via a Squarespace 302 redirect; the redirect URL was identified via WebFetch and used directly.
5. **CPI 2015.** Both target URLs in the task list are stale — the 2015/11/09/18693 article URL 404s and the SII landing URL goes through wpcomstaging.com before resolving back to publicintegrity.org. Captured both as HTML archives.
6. **Roth 2020.** The Google Sites page does not host a directly fetchable PDF; the index items are referenced but not embedded. A separate Roth thesis may exist at d-nb.info/136695582X/34 — not retrieved this session, flagged for follow-up if the compendium needs the full Roth methodology.
7. **Strickland 2014.** Both SSRN and ResearchGate gate the full text behind 403 to all programmatic fetches. Marked paywalled per the no-sci-hub policy.
8. **Springer "204 No Content" pattern.** For older Springer journals (Public Choice 1993/1997, IGA 2014), the `content/pdf/` URL with proper article-page cookies returns HTTP 204 — Springer's anti-scrape behaviour. These are gated for non-subscribers.
9. **SAGE consistently 403s** for `/doi/pdf/...` programmatic access across SPPQ, APR, SLGR. The Cambridge mirror of older SPPQ articles also serves only abstract HTML to programmatic clients.

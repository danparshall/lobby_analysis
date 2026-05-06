# Research Log: compendium-source-extracts

Created: 2026-05-02
Purpose: Rebuild the project's compendium of disclosure-law indicators by extracting items independently from each non-PRI source-framework paper, with PRI 2010 fully excluded. The compendium-as-shipped (141 rows) is structurally PRI-shaped: row count, atomization decisions, and verbatim descriptions all derive from PRI's question hierarchy because PRI was the seed rubric and later rubrics were tucked in as `framework_references` on PRI-shaped rows. The 2026-05-02 v3 audit on `statute-extraction` (186 concerns / 24.2% inter-auditor agreement) made this concrete and the user pivoted from "audit + patch" to "rebuild from sources."

> **⛔ AGENT-CRITICAL: PRI 2010 is out of bounds for this branch.** Do not read `papers/text/PRI_2010__state_lobbying_disclosure.txt`, do not open `compendium/disclosure_items.csv` or `framework_dedup_map.csv`, do not "calibrate against PRI" anywhere. PRI may appear as a name in predecessor-citation lists in extracts; that is the only context. The user has explicitly registered strong frustration about repeated agent-side defaulting to PRI as the structural foundation. See the top-of-file `⛔ AGENT-CRITICAL` block in `STATUS.md` for the full posture. This rule is non-negotiable until compendium-2.0 lands and the user explicitly clears it.

Carry-forward signals (informational, not gates):
- The Phase 0 audit deliverable on `statute-extraction` (`docs/active/statute-extraction/results/20260502_compendium_audit_*`) is **historical evidence the rebuild was needed, not a fix-list**. Do not read it for guidance; it is PRI-shape-aware in ways that bias the rebuild.
- The harness work on `statute-extraction` (iter-2 onward) is paused until compendium-2.0 lands. Iter-2's tightened `definitions` row descriptions would need redoing post-2.0.
- The `papers/text/` corpus contains both the 7 originally-scoped framework papers and (as of 2026-05-02) ~16 additional candidate framework/review papers that were added to the worktree by a parallel process. Their inclusion in the rebuild scope is an open question for user resolution; see the locked plan's Open Question 1.

---

## Sessions

(Newest first.)

### 2026-05-03 (pm cont'd) — Acquisition mapping (Blue Book / BoS / COGEL) + cross-rubric descriptive stats

**Convo:** [`convos/20260503_pm_acquisition_and_descriptives.md`](convos/20260503_pm_acquisition_and_descriptives.md)
**Spawning artifact:** Plan Step 4 of [`plans/20260504_compendium_2_0_synthesis.md`](plans/20260504_compendium_2_0_synthesis.md), invoked early after a direct user request to (a) map acquisition options for the three reference works and (b) produce a cross-rubric descriptive pass to test the user's hypothesis about near-duplicate paraphrasing across rubrics.

#### Topics Explored

- **Acquisition mapping for Plan Step 4 / Task #11.** Bibliographic verification via WorldCat, Stanford SearchWorks, HathiTrust, COGEL CDN. The "CSG Blue Book" cited by Opheim 1991 and the "COGEL Blue Books" cited by Strickland 2014 are the same publication series — *Campaign Finance, Ethics, Lobby Law & Judicial Conduct: COGEL Blue Book*, jointly published by Council of State Governments and Council on Governmental Ethics Laws (OCLC 80682979). Series structure: Phase 1 single comprehensive volume (~1982–early 1990s; 1990 8th edition `mdp.39015077214750` is public-domain, Google-digitized on HathiTrust); Phase 2 split (~1996/1997–) into thematic annual Updates (Ethics, Lobbying, Campaign Finance, FOI). The 2024 Ethics Update (626pp, retrieved from `cdn.ymaws.com/www.cogel.org/.../cogel_blue_book_2024_ethics_.pdf`) confirms Phase-2 format is self-reported ethics-agency narratives, not the comparative-tables structure Strickland used.
- **1990 8th edition Lobby Laws TOC recovered from HathiTrust catalog snippets**: Tables 28 (Lobbyists: Definition, Registration and Prohibited Activities), 29 (Lobbyists: Reporting Requirements), 30 (Lobbying: Report Filing), 31 (Lobbying: Compliance of Selected Agencies = enforcement powers), 32 (Education and Training: Lobbying Regulation). Cell-level content not retrieved from this environment (HathiTrust babel returns 403 even on PD content).
- **Strickland 2014 methodology re-read**. He applies Newmark 2005's 18 items unchanged + extends 1988-2003 via biennial COGEL Blue Books + CSG *Book of the States*, 2004-2013 via State Capital Law Firm Group's *50 State Handbook*. Does not read statutes. Decomposition into Definitions/Prohibitions/Reporting sub-scales is a regression-specification choice, not an item-level change. Strickland's empirical finding (registration counts respond to prohibitions but not consistently to reporting; opposite-signed effects across the three sub-scales) is documented as a compendium-design caveat against single-index aggregation.
- **State Capital Handbook**: structurally compatible with Newmark categories per marketing copy (definitions / prohibitions / disclosure + contact info); commercial only (~$200, Thomson Reuters / SCG Legal); 2025 edition is 1860pp.
- **Cross-rubric descriptive stats**. Atomic-item filter applied to 26 TSVs → 661 atomic items (509 in 17 rubrics + 152 in 9 non-rubric extracts). Topic taxonomy of 47 topics across 14 meta-domains, regex-tagged. TF-IDF (1-2 grams, sublinear, English stops, min_df=1, max_df=0.5) + cosine + greedy single-link union-find clustering at thresholds 0.20-0.50. Sentence-embedding fallback (`all-MiniLM-L6-v2`) attempted but blocked by egress proxy at HuggingFace (only github / pypi / npmjs / ubuntu / etc. allowed).

#### Provisional Findings

- **CSG Blue Book = COGEL Blue Book** (joint-series finding). Reduces the three-publication acquisition target to two — the same series at different vintages, plus *Book of the States*, plus the (commercial) State Capital Handbook.
- **The 1990 Blue Book has 5 lobby-specific tables. Two are unused by the older state-rubric tradition.** Table 31 (Compliance of Selected Agencies) is exactly Opheim's 7 enforcement items; Newmark dropped them in 2005 and Strickland inherited the drop. Table 32 (Education and Training) is unused by all three.
- **Cross-rubric paraphrase variants are real but cluster within author-family or geographic tradition.** TF-IDF at sim≥0.30 surfaces 20 cross-rubric clusters; 13 of 20 are Newmark2005↔Newmark2017 (same author, near-identical wording — expected); only 1 cluster spans ≥3 rubrics. Across the broader 17-rubric corpus, **items are expressed in idiosyncratic vocabulary even when measuring the same thing**. The European-tradition rubrics (AccessInfo / CouncilEurope / ALTER_EU / FOCAL) and the state-tradition rubrics (Opheim / Newmark2005 / Newmark2017) use largely non-overlapping vocabulary, and TF-IDF mostly fails to bridge them.
- **The topic-frequency histogram has no natural elbow.** Topics-by-rubric-count distribution (1=8, 2=4, 3=7, 4=10, 5=4, 6=3, 7=4, 8=4, 9=2, 10=1, 11=1) is closer to a power-law than stepped. **Method A (frequency threshold) in the synthesis plan is on weaker ground than the plan acknowledged**; the user's prior intuition that frequency-based filtering over-indexes on uninformative items is supported.
- **Long-tail diagnostic candidates surfaced**: `enforce_subpoena` (Opheim only, 4 items), `enforce_review_quality` (Opheim only, 1 item), `disc_leg_footprint` (SOMO only, 5 items — corporate-actor "lobby paragraaf" lens), `e_filing` (HiredGuns only, 3 items), `disc_funding_pubmoney` (AccessInfo only, 2 items), `disc_exp_threshold` (Sunlight only, 1 item). These are exactly the kinds of items that distinguish state regimes informationally — they didn't make the high-frequency cut precisely because they're hard to ask consistently.
- **Universal topics (≥10 rubrics): only `disc_gifts` (11 rubrics, 18 items) and `reg_org_subsidiary` (10 rubrics, 36 items).** Second tier (8-9 rubrics) is the predictable battery: timeliness, definition of lobbying activity, revolving-door disclosure, business associations, penalties, searchable access.
- **FOCAL has zero items in Prohibitions and minimal Personnel content.** Method B (FOCAL-anchored expansion) inherits these blind spots — anchoring on FOCAL would systematically underweight contingent-fee bans, gift bans, campaign-contribution bans, revolving-door cooling-off rules. Compendium 2.0 should be **assembled, not filtered** — frequency does not produce a natural core, and lexical clustering recovers within-author repetition rather than cross-tradition convergence.

#### Decisions

| topic | decision |
|---|---|
| Blue Book acquisition path | Adam Newmark email is highest expected value per unit effort; ILL for HathiTrust 1990 8th ed. is the most direct path to actual cell-level content; used-copy purchase via eBay/AbeBooks is the cheapest acquisition; defer State Capital Handbook indefinitely unless project subscription budget supports it (~$200/yr) |
| Book of the States acquisition | De-prioritized per user (item labels already in `items_Newmark2005.tsv` / `items_Opheim.tsv`); re-evaluate only if Blue Book path delivers and operational thresholds become the binding gap |
| Method A (frequency threshold) | Documented as on weaker ground than the synthesis plan acknowledged; histogram has no natural elbow; should not be applied alone |
| Method C (discriminative-strength) | Strengthened by long-tail finding; the 1-rubric topics list is exactly the kind of items the user previously identified as diagnostically strong |
| Method B (FOCAL-anchored) | Carries explicit blind spots: zero Prohibitions items, minimal Personnel; would need a structural-anchor parallel run from another rubric to mitigate |
| Sentence-embedding fallback | Blocked by egress proxy; flagged as "what would unblock better analysis" in the descriptive doc; recommended for next session via either a model already in the repo or a pre-downloaded HF cache |
| Compendium 2.0 design plan | Still deferred per the synthesis plan; nothing in this session changes that, but the descriptive evidence sharpens the input |

#### Mistakes recorded

1. **Same user message arrived twice.** Likely an artifact of conversation compaction between session resume points; treated the second instance as a continuation rather than a re-initialization. No content harm but worth noting for future-session awareness.
2. **Initial topic taxonomy over-fired on `bills_subjects`** because the regex matched bare "issues?". Caught on first inspection; tightened to require actual bill/legislation references; rerun produced clean coverage. Documented in the descriptive doc's methodology section.
3. **HathiTrust public-domain content not retrievable from this environment.** `babel.hathitrust.org` returns 403 even on `mdp.39015077214750` (1990 8th ed., public-domain Google-digitized). Egress proxy / no-institutional-auth combination. Worked around by recovering structure from search-engine snippets but no cell-level content recovered.
4. **`cdn.ymaws.com` blocked from bash but accessible via web_fetch.** Not a mistake per se but a useful note for future sessions: the Anthropic egress proxy is more permissive than the bash-tool proxy. URL-pattern probing for older COGEL editions did not find files (CDN URLs likely have unique tokens, not just predictable filename patterns).

#### Results

- `docs/active/compendium-source-extracts/results/20260503_blue_book_bos_cogel_acquisition.md` — acquisition findings doc (~131 lines)
- `docs/active/compendium-source-extracts/results/20260503_cross_rubric_descriptive.md` — descriptive stats doc (~220 lines)
- `docs/active/compendium-source-extracts/results/cross_rubric_topic_x_rubric.csv` — 47 topics × 17 rubrics + n_rubrics
- `docs/active/compendium-source-extracts/results/cross_rubric_domain_x_rubric.csv` — 14 meta-domains × 17 rubrics + n_rubrics + total_items
- `docs/active/compendium-source-extracts/results/cross_rubric_items_clustered.csv` — 509 rubric atomic items × topic tags

#### Next Steps

- User reviews the two results docs and decides which acquisition paths to pursue.
- Email-author skill (Task #10) — bundle Adam Newmark email with Blue Book / BoS ask + Vaughan & Newmark 2008 retrieval ask.
- If sentence embeddings become available (proxy whitelist or pre-cached model in repo), re-run the cross-rubric clustering pass; current TF-IDF result understates semantic equivalence across European↔state-tradition rubrics.
- Compendium 2.0 design plan — still deferred per the synthesis plan, but inputs are sharper now.

---

#### Post-session continuation (2026-05-06)

The 2026-05-03 work landed (commit `a857965c`). Resumed 2026-05-06 with two minor follow-ups documented in the convo summary's Post-session continuation block:
1. HathiTrust path (catalog record `https://catalog.hathitrust.org/Record/002470321`; 1990 8th edition `https://babel.hathitrust.org/cgi/pt?id=mdp.39015077214750`, ID `mdp.39015077214750`) documented for the user's personal-machine retrieval.
2. **Sentence-embedding script committed at `tools/embed_cross_rubric.py`** (commit `4eed8f5f`). Local-machine companion to the 2026-05-03 TF-IDF analysis — sandboxed env couldn't reach `huggingface.co`. Runs `all-MiniLM-L6-v2` over the 509-item rubric-atomic-items CSV, produces similarity matrix + threshold summary + cluster dump. Designed to run from the user's desktop (`pip install sentence-transformers pandas numpy && python tools/embed_cross_rubric.py`). Predictions to falsify in the script docstring.

The cross-rubric clustering re-run is unblocked; user is handing it off to a desktop agent.

---

### 2026-05-03 — Per-paper extraction execution

**Convo:** [`convos/20260503_per_paper_extraction_execution.md`](convos/20260503_per_paper_extraction_execution.md)
**Spawning artifact:** the locked plan at [`plans/20260502_per_paper_source_extraction.md`](plans/20260502_per_paper_source_extraction.md)

#### Topics Explored

- Plan modifications at session start: no template-first; predecessor citation-collection + download wave before extraction; README headline → "LobbyView for 50 states".
- Citation-collectors against FOCAL 2024 (26 entries) and Newmark 2017 (25 entries) → deduplicated download-target list ~37 candidates.
- Predecessor-paper download wave: 17 retrieved (14 PDFs + 2 HTML + 1 text), 3 verified-on-disk, 13 paywalled, 1 not-found, 3 books.
- User author-page hunt round 1: 5 additional papers retrieved (Strickland 2014, Mihut 2008, Chung 2024, LaPira & Thomas 2014, CPI 2015 SII Kusnetz article).
- Test set of 3 extractions (Opheim 1991, CPI Hired Guns 2007, Sunlight 2015) → format validated across three rubric shapes.
- Wave 1+2+3a+3b: 23 more papers extracted in parallel batches of ~6.
- 26 papers extracted total. All TSV+MD pairs at `results/items_<Paper>.{tsv,md}`.

#### Provisional Findings

- **BoS-tradition runs deeper than expected.** 5 of 26 papers are pure secondary-source-coding rather than own statute reading: Opheim 1991 (21/22 BoS-defined), Newmark 2005 (18/18 = 100% BoS-defined), Newmark 2017 (hybrid: BoS structure / paper-coded values), Strickland 2014 (extends Newmark with COGEL Blue Books + State Capital Law Firm Group handbook), Flavin 2015 (uses Newmark unchanged). Operational definitions live in CSG / COGEL / State Capital reference works, not the papers themselves.
- **Many "predecessors" are not rubrics.** Only ~13 of 26 are independent measurement instruments. Rest split into empirical applications (Strickland, Flavin, Chung, Mihut), survey studies (Hogan/Murphy/Chari 2008), subset-displays of multiple rubrics (Bednařová), construct-defining work (LaPira & Thomas 2014), federal-data infrastructure (Kim 2018), methodological scoping reviews (Lacy-Nichols 2023), empirical evaluations (McKay & Wozniak 2020).
- **FOCAL Table 2 is not authoritative on category structure.** Right (10): Opheim, Newmark 2017, Hired Guns, FOCAL self, ALTER-EU, AccessInfo, IBAC, GDB-within-scope, CoE (within tolerance), SOMO. Wrong (3): Newmark 2005 (3 vs 4 categories), Carnstone 2020 (FOCAL conflated with Roth — wrong category labels + wrong count), TI 2016 ("methodological touchstone" overstates a 4-bullet TI-UK lens). Not-a-rubric (3): Bednařová, Hogan/Murphy/Chari, Kim 2018.
- **FOCAL 2024 is unweighted.** 50-indicator checklist; all `scoring_rule = "Not specified"`. Authors flag weighting as future Delphi work. Gives compendium-2.0 the field universe but not the grading rubric.
- **Federal-vs-state cross-walk gap is consistent across federal-data papers** (Kim 2018, Chung 2024, LaPira & Thomas 2014). Federal-only infrastructure (single LDA statute, canonical bill IDs, CRS bill database, LegiStorm, CQ First Street, CRP, SOPR, Compustat) is what makes federal lobbying analysis tractable. State equivalents don't exist. README's "LobbyView for 50 states" framing names exactly this gap. LaPira & Thomas: LDA self-reporting captures only 29.7% of the 51.7% verified revolving-door rate.
- **CDoH parallel measurement universe.** Lacy-Nichols 2023 cites 7 frameworks from public-health discipline with **zero overlap** with FOCAL 2024's 15 reviewed: Mialon 2015, Savell 2014 (CPA), Ulucanlar 2016 (Policy Dystopia), Madureira Lima 2019 (CPI), Allen 2022 (CFII), Lee 2022 (CDoH Index), OECD 2021. Different lens (corporate-actor side vs regulatory-disclosure side).

#### Decisions

| topic | decision |
|---|---|
| Plan modifications | No template-first; predecessor citation + download before extraction; README headline → "LobbyView for 50 states" |
| Extraction scope | 26 papers extracted = 7 originals + 14 retrieved predecessors + 5 author-hunt-round-1. Federal trio (LaPira 2020, GAO 2025) deferred. Roth 2020 deferred (text-only summary). Newmark & Vaughan 2014 dropped (not lobbying). Lacy-Nichols 2025 skipped (FOCAL application) |
| New acquisition list | Task #11 expanded: CSG Blue Book + BoS volumes + COGEL Blue Books + State Capital handbook; CII methodology source; GDB Research Handbook; TI-UK open-data rubric; Piotrowski & Liao 2012; Keeling et al. 2017; Chari/Murphy/Hogan 2007 PQ; CDoH 7-framework corpus; new candidates from extraction lit reviews (Pross 2007, Chari & Murphy 2006, Malone 2004, Hamm/Weber/Anderson 1994, Brasher/Lowery/Gray 1999, Lowery & Gray 1993/1994/1996 vintages, LaPira 2016, Rosenthal 2001) |
| Email-authors list | Task #10 maintained: post-2000 still-missing papers (Witko 2005/2007, Ozymy 2010/2013, Laboutková & Vymětal 2022/23, Vaughan & Newmark 2008, Roth 2020 thesis, plus Chari/Murphy/Hogan 2007 PQ ask) |
| Compendium-2.0 design | Still deferred. Not part of this session. User reviews the 26 extracts personally before design begins |

#### Mistakes recorded

1. **Working-directory confusion** — assistant's bash cwd was the main worktree rather than `compendium-source-extracts/` for several commands mid-session. Caused 5 PDFs to land in main's `papers/` instead of the worktree's. Recovered by copying across, but should have used absolute paths from the start.
2. **Spec error on Sunlight 2015** — prompt told the agent "Sunlight uses 4-tier ordinal scales per indicator." Wrong; only 2/5 are 4-tier, 1 is 5-tier, 2 are 2-tier. Agent caught the error and captured actual structure verbatim.
3. **CPI Hired Guns path inaccuracy** in agent prompt — recovered fine.
4. **`papers/extracts/` stray artifacts from prior session** — never cleaned up; still untracked, not committed.

#### Results

- 3 predecessor / manifest docs at `results/predecessors_FOCAL_2024.md`, `results/predecessors_Newmark_2017.md`, `results/predecessor_download_manifest.md`.
- 26 per-paper extracts at `results/items_*.{tsv,md}`.

#### Next Steps

- User reviews the 26 TSV+MD pairs.
- Compendium-2.0 design plan (separate plan, after review).
- Task #10: email-authors flow for missing post-2000 papers.
- Task #11: CSG Blue Book + Book of States + COGEL Blue Books + State Capital handbook acquisition (likely via Adam Newmark contact + library/HathiTrust hunt).
- Optional: CDoH-corpus expansion (7 frameworks); federal-extension extracts (LaPira 2020 / GAO 2025).

#### Plan produced (post-checkpoint)

[`plans/20260504_compendium_2_0_synthesis.md`](plans/20260504_compendium_2_0_synthesis.md) — for next session. Four goals: acquire missing papers (Tasks #10 + #11); extract newly-acquired rubric items; cross-rubric descriptive stats (intersection / union / items-by-rubric-count histogram / per-cluster coverage); brainstorm principled-subset selection methods (4 candidate approaches articulated) + item-family clustering (4 candidate dimensions). Six open questions for user resolution at session start. Compendium 2.0 + schema v2.0 stay deferred to follow-up plans.

#### Post-checkpoint findings

- **README rewrite** — dropped the "5–8 priority states" / "all 50 states" headline contradiction; new "What we deliver" section names the data-layer-not-rubric framing; new "Project state" section makes explicit that v1 is *not* the foundation for v2.0. Commits `6cef788`, `9682efd`.
- **v1.1 schema audit** — confirmed structurally PRI-shaped despite the row-level `FrameworkReference` abstraction. PRI-shaped: `RegistrationRequirement.role` 11-role Literal (= PRI A1-A11), `ReportingFrequency` 7-cadence Literal (= PRI E1h/E2h), named scalar SMR fields `de_minimis_financial_threshold` + `de_minimis_time_threshold`, `FrameworkId` Literal lists PRI first. Carry-forward: `FrameworkReference`, `CompendiumItem`, `MatrixCell`, `FieldRequirement` row-level, availability axes. Schema v2.0 must rebuild these Literals + drop named `de_minimis_*` fields alongside compendium-2.0 atomization. Same vocabulary-vs-structure pattern the compendium audit caught.
- **Rubric inventory settled at 14 + 12 + 4-pending** — 14 rubrics fully extracted, 12 non-rubric extracts (empirical applications / surveys / scoping reviews / federal-data infrastructure / construct-defining work / comparative narratives), 4 known-of-but-not-fully-retrieved (TI-UK 4-criterion, CII methodology, Roth 2020 thesis, Chari et al. books). 26 papers total.
- **Strategic framing clarified by user**: data layer is the deliverable, not a rubric or scorecard; researchers, activists, and journalists bring their own weights and rankings; common items derived from cross-rubric synthesis with informativeness as the actual selection criterion (frequency-of-use is just a starting filter); compatible with Popolo for entities + complementary OCD-style schema for filings since Popolo doesn't cover filings.

---

### 2026-05-02 (pm) — Branch creation + per-paper extraction plan

**Convo:** [`convos/20260502_pm_compendium_rebuild_pivot.md`](convos/20260502_pm_compendium_rebuild_pivot.md)
**Plan produced:** [`plans/20260502_per_paper_source_extraction.md`](plans/20260502_per_paper_source_extraction.md)
**Spawning artifact:** the v3 audit on `statute-extraction` (`docs/active/statute-extraction/results/20260502_compendium_audit_concerns.md`) — but the audit is **not a fix-list**; it is evidence-of-need.

#### Topics Explored

- Walk-through of the v3 Phase 0 audit's tag-disagreements (NON_COMPENSATION broader-vs-narrower, DEF_PUBLIC_ENTITY axis-ambiguous-vs-misleading, DEF_ADMIN_AGENCY rubric-ambiguous-vs-broader). Recognition that surface tag-disagreements were symptoms of two assumption-breaks in the audit's C1/C2 taxonomy: rows aren't all axis-typed, and `framework_references` clusters aren't all homogeneous.
- Recognition of structural PRI privilege in the compendium: 4-row DEF_PUBLIC_ENTITY family (PRI Q-C parent + 3 sub-criteria), 12-row FREQ_* (PRI E1h/E2h enumeration), 11-row REG_*-A-series (PRI A1–A11), 8-row RPT_*_NON_COMPENSATION/OTHER_COSTS/etc. (PRI E1f i/ii/iii/iv split × 2 sides), and a literal `?.` formatting artifact on ~24 rows (mechanical evidence of script-translated PRI text). Vocabulary fix in D9 was insufficient; structural rebuild required.
- Pivot decision: rebuild from non-PRI source papers, in each paper's own structure, with no carry-over from the existing compendium or any prior PRI-derived CSVs.
- Per-paper artifact spec: TSV (machine-readable) + MD (human-readable methodology summary). Output path `docs/active/compendium-source-extracts/results/items_<Paper>.{tsv,md}`. Rubric-native vocabulary; no domain assignment, no axis-tagging, no cross-paper mapping.
- Sequencing: template-first (one paper foreground, user format review) → parallel-dispatch remaining papers → per-paper user review → stop. Compendium-2.0 design is a separate plan written after all reviews are in. Predecessor-framework chase is a separate plan written after extracts ship.

#### Provisional Findings

- The compendium 1.x is unsalvageable as a foundation for compendium-2.0 design. Patches to row names, descriptions, or domain assignments leave the structural PRI-shape intact.
- D9's vocabulary de-PRI-ing was necessary but not sufficient — the row *atomization* itself is PRI's, and that requires source-paper rebuild.
- The ~16 additional papers (international/EU lobbying-regulation frameworks + review pieces) discovered untracked on the worktree at session-end materially expand the candidate source-paper universe beyond the 7 originally scoped. User triage needed before extraction dispatches.

#### Decisions

| topic | decision |
|---|---|
| Compendium 1.x posture | Frozen; soft-deprecated by compendium-2.0 work on this branch |
| PRI 2010 status | Fully excluded. Not "de-privileged"; ignored. No PRI text in any extract; PRI only appears as a citation name in predecessor lists |
| Source extraction posture | Re-extract every paper from scratch. Ignore prior CSVs (`focal_2024_indicators.csv`, Sunlight data CSV, pri-rubric CSVs). Compendium itself is off-limits as a seed |
| Format | TSV + MD per paper. `items_<Paper>.tsv` + `items_<Paper>.md` |
| Output location | `docs/active/compendium-source-extracts/results/` |
| Sequencing | Template-first, then parallel; user reviews each |
| Compendium-2.0 design | Separate plan, written after all per-paper reviews are in |
| Predecessor-framework chase | Enumerate-only in per-paper MDs; chase decision deferred |
| `statute-extraction` iter-2 of harness | Paused until 2.0 |
| Phase 0 audit doc on `statute-extraction` | Retained as historical evidence; supersession marker added on plan; canonical concerns doc + reconciliation note unchanged |
| STATUS.md PRI bar | Added top-of-file on this branch's STATUS.md; cherry-picked to `statute-extraction`'s STATUS.md |
| Auto-memory | `feedback_pri_not_privileged.md` updated to extend the rule from vocabulary to structure |

#### Mistakes recorded

For honesty + future-session protection:

1. **Missed structural PRI privilege repeatedly.** When user asked about the D11 concern, assistant framed it as PRI-neutral on the basis that row IDs were rubric-neutral. Failed to recognize that the row *atomization* itself was PRI's. Memory `feedback_pri_not_privileged.md` had the vocabulary lesson but assistant didn't generalize. The auto-memory has been updated to make the structural lesson explicit.
2. **Dispatched template extraction agent at wrong path/format** before the user clarified `results/items_<Paper>.tsv`. Agent wrote to `papers/extracts/Opheim_1991.{csv,md}` (wrong dir, wrong extension). Files have been deleted as part of session-end cleanup.
3. **Tried to redirect the in-flight agent** via `SendMessage`, but the tool was not in the assistant's surface; ToolSearch returned no match. User stopped execution.
4. **Conversation context too saturated** by end-of-session for clean execution. User explicitly: "you aren't capable of doing the work with your context as-is. Your job is to write the plan."

#### Next Steps

- User reviews the locked plan at `plans/20260502_per_paper_source_extraction.md` and resolves its 7 open questions, especially Open Question 1 (the universe of source papers — now potentially much larger than 7 given the ~16 untracked additions).
- After plan acceptance, fresh-context implementing agent executes per the plan: dispatches one template paper, surfaces for user format review, then dispatches the remaining papers in parallel.
- After all per-paper reviews are in, a follow-up plan is written for compendium-2.0 design (not part of this plan).



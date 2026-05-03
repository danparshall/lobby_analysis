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

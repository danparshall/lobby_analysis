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

### 2026-05-11 — Phase B continued: Sunlight 2015 projection mapping (3rd rubric)

**Convo:** [`convos/20260511_sunlight_phase_b_mapping.md`](convos/20260511_sunlight_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (third rubric, after CPI 2015 C11 and PRI 2010).
**Plan handoff for remaining 7:** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 4 in-scope Sunlight items mapped (item 4 excluded per 2026-05-07 audit decision): item 1 (Lobbyist Activity 4-tier) → 6 rows with α split; item 2 (Expenditure Transparency 4-tier) → 3 rows (2 reused from CPI mapping); item 3 (Expenditure Reporting Thresholds 2-tier) → 1 typed cell shared with HG Q15 at finer granularity; item 5 (Lobbyist Compensation 2-tier) → 3 rows (2 reused from CPI mapping). **13 distinct compendium rows touched; 11 of 13 have cross-rubric readers.**
- α (form-type split for content cells) executed for item 1: 3 disclosure-detail levels × 2 form types (reg form / spending report) = 6 rows. HG Q5 vs Q20 is the canonical motivating case.
- β (Opheim AND-projection) confirmed by user. Opheim's `disclosure.legislation_supported_or_opposed` is one binary in source TSV; projection reads `bill_id AND position` from compendium. Source not re-atomized.
- Three threshold concepts named distinctly for the first time: lobbyist-status (CPI #197), filing-de-minimis (PRI D1), itemization-de-minimis (Sunlight #3 / HG Q15). Must stay separate in compendium 2.0.
- Cross-rubric grep workflow surfaced as a fix for an error pattern in this session — proposing rows as if Sunlight-unique before checking other rubrics. Mandatory grep BEFORE drafting from this point forward.
- Non-Sunlight side artifact: bash-loop permissions investigation. User-flagged recurring failure mode (agents reaching for `for`-loops that trigger permission prompts) → project-level memory file + dotfiles note documenting four existing loop-backdoor rules (`xargs *`, `find *`, `awk *`, `sed *`) and proposing addition of `Bash(for *)` / `Bash(while *)` to DENY rules.

#### Provisional Findings

- **Sunlight's compendium contribution is cross-rubric redundancy, not novel structure.** 11/13 rows it touches are already read by other rubrics (HG, Newmark 17/05, CPI, PRI, FOCAL, Opheim). Per the projection-success criterion's "validated by many rubrics" pattern, these are the rows most likely to survive compendium-2.0 dedup.
- **"Collect once, map to many" annotation discipline is well-supported empirically.** Cross-rubric grep over the 8 rubric TSVs + historical PRI surfaced extensive overlap that single-rubric mapping would have missed. The `[cross-rubric: <other readers>]` annotation seeds the dedup pass.
- **Sunlight cannot reproduce its published `Total` or `Grade`** because item 4 is excluded. Per-item validation against the 4 in-scope per-criterion columns of the per-state CSV is the recommended Phase C scope.
- **Three threshold concepts must stay distinct.** Naming them surfaced a latent conflation risk; documented in Sunlight mapping doc's "CRITICAL distinction" block for design-team awareness.
- **Per-state distribution skew observed across 50 states:** item 1 mode tier 0 (50%, general subjects only); item 3 mode tier −1 (66%, threshold exists); item 5 split 46/54 (compensation disclosed / not).

#### Decisions

| topic | decision |
|---|---|
| Third Phase B target | Sunlight 2015, completed (4-of-5 in scope) |
| α form-type split | LOCKED for content-cell rows across remaining 7 mappings |
| β Opheim conflation | Reading (1) confirmed: AND projection at compendium layer, source TSV unchanged |
| "Collect once, map many" | LOCKED as annotation discipline (`[cross-rubric: …]` next to every row entry) |
| Three threshold concepts | Stay distinct in compendium 2.0; documented in Sunlight mapping doc |
| Sunlight Phase C validation | RECOMMENDED per-item only (cannot reproduce Total/Grade); user final lock-in pending |
| Cross-rubric grep workflow | MANDATORY before drafting any compendium row entry |
| Next-session handoff | Written at `plans/_handoffs/20260511_phase_b_continued_remaining_7.md` |

#### Mistakes recorded

1. Used a `for f in ...; do wc -l "$f"; done` bash loop for a simple multi-file inventory, triggering a permission prompt. The CLAUDE.md permission table explicitly lists `ls path/*` and explicit-args calls as pre-approved chain prefixes; `for` is not. User pushed back: "this comes up at least once a session, and it's really annoying." Wrote a project-level memory file (`~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_use_preapproved_bash_patterns.md`) leading with three rules-of-thumb at the moment-of-temptation: (1) explicit list or glob in one call; (2) parallel Bash calls; (3) Python script via `uv run python`. Also wrote a dotfiles note (`~/code/dotfiles/notes_bash_loop_permissions.md`) documenting four existing loop-backdoor rules.
2. Drafted Sunlight item 1 as if it introduced novel "bill discussed + position" rows without cross-checking. User pushback ("are you telling me Sunlight is the ONLY rubric that has an item capturing that? REALLY?") surfaced 11 cross-rubric items across HG Q5/Q20, Newmark 2017/2005, Opheim, FOCAL contact_log.10/11, PRI E1g_i/ii / E2g_ii, plus Sunlight #1 — the row family is one of the most-redundantly-validated in the entire corpus. Workflow fix: cross-rubric grep before drafting, not after.

#### Results

- [`results/projections/sunlight_2015_projection_mapping.md`](results/projections/sunlight_2015_projection_mapping.md) — Sunlight 2015 projection mapping doc (13 rows × 4 items, all annotated with cross-rubric overlap).
- [`../../../tools/sunlight_distributions.py`](../../../tools/sunlight_distributions.py) — 30-line Python script for per-state distribution table in the mapping doc (footnote-stripped tier counts across 50 states for all 5 indicators).
- Non-repo: `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_use_preapproved_bash_patterns.md` (project memory); `~/code/dotfiles/notes_bash_loop_permissions.md` (dotfiles note).

#### Next Steps

1. **OpenSecrets 2022 projection mapping** (4 cats, smallest of the remaining; per locked Phase C order). Watchpoints in `plans/_handoffs/20260511_phase_b_continued_remaining_7.md`: Cat 2 reuses Sunlight #5 compensation rows; Cat 4 maps to CPI #205-206 / HG Q28-34 / FOCAL openness.* portal-availability stack.
2. **Confirm Sunlight Phase C validation strategy** (per-item only is recommended).
3. Continue Phase B for remaining 6 rubrics: Newmark 2017, Newmark 2005, Opheim, HiredGuns, FOCAL, LobbyView (last; schema-coverage shape).
4. Dotfiles note's recommendation (add `Bash(for *)` / `Bash(while *)` to DENY rules) — decide whether to incorporate into `update_claude_permissions.py`.

---

### 2026-05-07 (late eve) — Phase B continued: PRI 2010 projection mapping

**Convo:** [`convos/20260507_pri_2010_phase_b_mapping.md`](convos/20260507_pri_2010_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (second rubric — PRI 2010, after CPI 2015 C11).
**Spawning artifact:** the predecessor convo `convos/20260507_phase_b_projection_mappings.md` (CPI mapping that locked the conventions PRI inherits).

#### Topics Explored

- All 83 PRI 2010 atomic items mapped per the locked Phase B template: 22 accessibility (Q1-Q6 binaries + Q7a-o 15-criteria search-filter battery + Q8 ordinal_0_to_15) + 61 disclosure-law (A1-A11 actor-side registrant taxonomy + B1-B4 government-exemption + C0-C3 public-entity-def + D0/D1/D2 materiality with typed cells + E1a-E1j 19 principal-side + E2a-E2i 18 lobbyist-side).
- Conceptual distinction recorded: PRI A is **actor-side** ("who must register as a lobbyist"); CPI #196 is **target-side** ("definition recognizes communications with X as lobbying"). Two distinct row families (`actor_*` vs `def_target_*`).
- E1/E2 parallelism preserved: PRI's principal-side and lobbyist-side atomization yields 2 compendium rows per pair (`principal_*` + `lobbyist_*`), per granularity-bias — regimes can regulate the two actors asymmetrically. Consensus method correctly identified all parallel pairs as paired loose clusters (loose-c_028 through c_039 are mostly E1*/E2* mirrors).
- Typed-cell pattern at PRI granularity: D1_present + D1_value collapse into ONE row carrying typed `Optional[Decimal]`; D2 same with `Optional[float]`. Two PRI atomic items, one compendium cell, two projections (presence-flag vs raw-value).
- E1h/E2h cadence representation: PRI's 6-binary atomization conflicts with CPI #202's enum cell. Resolution adopted: PRI's binary representation is canonical; CPI's enum becomes a derived projection. Flagged as Open Issue 4 (retroactive change to CPI mapping; design-team review).
- Q8's 0-15 ordinal partition treated as Open Issue analogous to CPI's 25/75 partial-credit (per user direction a2). Cell carries raw ordinal; partition decision deferred to Phase C.
- Aggregation rule structure verified empirically: accessibility max=22, disclosure-law max=37; spot-check Alabama/Alaska percentages match published values to ≤0.2%.

#### Provisional Findings

- The per-item template scales to PRI's atomic resolution (83 items) without modification. Compound items, parallel pairs, typed-with-presence-flag, free-text companions all fit cleanly.
- PRI adds **~52 NEW compendium rows** on top of CPI's 21, matching the handoff's prediction (30-50 new). Total compendium rows touched after CPI + PRI: ~85 distinct rows.
- Compendium row design is converging across rubrics. PRI adds rows but doesn't *contradict* CPI's design — every CPI row PRI touches reads the same observable. Validates the projection-driven row-design approach.
- PRI's published per-state ground truth is **sub-aggregate-level only** (5 disclosure-law sub-aggregates + 8 accessibility sub-components × 50 states = 650 ground-truth values). Per-atomic-item validation impossible against PRI's published data alone — Phase C tolerance for PRI must be at sub-aggregate granularity, with per-item validation via CPI's 700-cell ground truth where rows overlap.
- Within-E1/E2 rollup ambiguity confirmed: PRI paper does NOT specify how E1f_i-iv (4 binaries) → E1f sub-aggregate slot. Phase C empirical fit against per-state E_info_disclosed values is the resolution path; historical pri-calibration's "9 methodology differences" doc is the input.

#### Decisions

| topic | decision |
|---|---|
| Second Phase B target | PRI 2010, completed (single-pass per user direction a1) |
| PRI A vs CPI #196 | Distinct: A is actor-side, #196 target-side. Two row families. |
| E1/E2 parallel pairs | Two compendium rows per pair (principal_* + lobbyist_*); regimes may regulate asymmetrically |
| D1/D2 representation | One typed `Optional[Decimal]` (D1) / `Optional[float]` (D2) cell per threshold; D_present is `IS NOT NULL` projection |
| C1-C3 in compendium | Captured as compendium rows even though PRI projection doesn't read them |
| E1h/E2h cadence | 6 binary rows per actor (canonical); CPI's enum becomes derived projection (retroactive flag) |
| E1h_vi/E2h_vi "Other" | 2-row pair: binary indicator + free-text specification companion |
| Q8 partition | Open Issue (analogous to CPI 25/75); deferred to Phase C |
| B1/B2 scoring direction | Provisional +1 for True; Phase C empirical fit confirms or flips |

#### Mistakes recorded

None — single-pass execution; no rework cycles. Conventions from CPI session were tight enough that all 83 items resolved deterministically.

---

### 2026-05-07 (eve) — Phase B kickoff: CPI 2015 C11 projection mapping

**Convo:** [`convos/20260507_phase_b_projection_mappings.md`](convos/20260507_phase_b_projection_mappings.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (first rubric only).
**Spawning artifact:** the Phase B handoff at `plans/_handoffs/20260507_phase_b_handoff.md` written at end of (pm) session.

#### Topics Explored

- First Phase B per-rubric projection-mapping doc shipped: CPI 2015 C11 (smallest concrete first target per locked Phase C order). All 14 items mapped per the plan's per-item template.
- Three iteration cycles with user surfaced reusable conventions: (1) granularity-bias (split rows on every distinguishing case for max downstream flexibility) → 5 separate `def_target_*` rows from IND_196 alone; (2) typed-cell-on-`MatrixCell.value` pattern wins over named-scalar-with-citation for v2.0 schema migration; (3) evidence-companion field already exists in v1.1 (`FieldRequirement.evidence_source` + `legal_citation`) — Open Issue 5 retracted as misdiagnosis.
- Mid-session re-extraction of CPI scoring rules from `papers/CPI_2015__sii_criteria.xlsx`. Previous TSV truncated at ~300 chars; full text now in `items_CPI_2015_lobbying.tsv`. **Bonus:** xlsx contains per-state per-indicator scores for all 50 states × 14 indicators — extracted to `results/cpi_2015_c11_per_state_scores.csv` (700 cells of ground truth, not just category aggregate).
- Discovery: **8 de-facto items use 5-tier scoring (0/25/50/75/100), not the 3-tier as published criteria text suggests.** CPI graders awarded 25 and 75 as scorer-judgment partial credit between the 100/50/0 anchors documented in the rubric. Boundary semantics for 25/75 not in published criteria — Phase C question.

#### Provisional Findings

- 14 CPI items map to **21 distinct compendium rows** when granularity-bias is applied (5 per-target-type def rows from IND_196, compound-item decompositions for #201/#205, etc.).
- v1.1 schema already partially supports compendium 2.0: `RegistrationRequirement.role` Literal enumerates exactly the granular target-type roles needed; `CompendiumItem.data_type` declares typed cells. Gap is `MatrixCell.value` (typed value carrier missing) and the PRI-shape vestigial `StateMasterRecord.de_minimis_*` named scalars (should be retired in v2.0).
- All 6 de-jure CPI items are 2-tier or 3-tier; all 8 de-facto items are 5-tier — direct empirical validation of the v1.1 two-axis design (legal_availability / practical_availability) and of the typed-cell decision.
- The Phase B per-item template handles compound items (1 rubric-item → N compendium-rows) cleanly without modification — IND_201 reads 3 rows, IND_205 reads 3 rows, no exception needed.
- Per-state per-indicator data has 6 / 700 (~0.9%) cell-level glitches: 4 mixed-case typos ("Yes"/"No") + 2 numeric values where YES/MODERATE/NO expected (IND_199, IND_203 — 1 each). Phase C consumption layer should normalize.
- Cluster IDs from 3-way consensus are useful provenance hints, NOT authoritative row identifiers (user reminder mid-session: "earlier embedding groups aren't sacred, just guidelines. The real test will be this compendium-rubric mapping").

#### Decisions

| topic | decision |
|---|---|
| First Phase B target | CPI 2015 C11, completed |
| Granularity convention | Split on every distinguishing case (binary cells per case, Boolean projection composition); locked into doc-conventions block |
| Typed-cell pattern | `MatrixCell.value: Any` constrained by `CompendiumItem.data_type`; v2.0 schema bump retires named-scalar `de_minimis_*` fields |
| De-facto cell type | 5-tier typed int {0,25,50,75,100}, not 3-tier enum (correction from realized xlsx data) |
| Enforcement-adjacent items #207/208/209 | Kept in scope — measure whether enforcement exists at all, not enforcement strictness |
| Source-quote re-extraction | Done from xlsx; updated TSV with full text, no more 300-char truncation |
| Per-state per-indicator scores | Extracted to CSV (700 cells, 6 cells with data-quality glitches noted) |
| Cluster ID notation | `strict-c_NNN` / `loose-c_NNN` to disambiguate the two consensus files using independent numbering |

#### Mistakes recorded

1. 3-tier vs 5-tier mis-spec on first draft. Initial doc had 3-tier enum cell types based on published criteria text; realized data uses 5 tiers. Caught only when re-extracting per-state scores. Corrected doc-wide before commit.
2. Misdiagnosed an evidence-companion schema concern as a v1.1 gap; user noted the field exists in v1.1 already. Retracted; replaced Open Issue 5 with the actual hard concern (evidence circularity in 2015 round-trip).
3. Compound-item framing as exception in first draft. User confirmed compound is normal. Softened.
4. Cluster-ID conflation across strict/loose files. Doc now disambiguates explicitly.

#### Results

- [`results/projections/cpi_2015_c11_projection_mapping.md`](results/projections/cpi_2015_c11_projection_mapping.md) — 251-line Phase B mapping (14 items, 21 compendium rows, 6 open issues)
- [`results/cpi_2015_c11_per_state_scores.csv`](results/cpi_2015_c11_per_state_scores.csv) — 700 ground-truth cells
- [`results/items_CPI_2015_lobbying.tsv`](results/items_CPI_2015_lobbying.tsv) — updated with full scoring-rule text

#### Next Steps

1. **PRI 2010 Phase B mapping.** 83 items × 50 states. Stress-test the template at scale; will likely add 30-50 new compendium rows that CPI's higher-abstraction atomization didn't surface (PRI E1f_i-iv itemization, E1h/E2h cadence options, A1-A11 registrant taxonomy at finer granularity).
2. **Phase C scaffolding decision when ready** — `tests/fixtures/projection_inputs/cpi_2015_<state>.json` hand-population from the per-state-scores CSV is one-liner for de-jure half (clean ground truth, no circularity). De-facto half held per Open Issue 5 (evidence circularity).

---

### 2026-05-07 (pm) — Phase A atomic-item audits + Lacy-Nichols 2025 supplementary extraction

**Convo:** [`convos/20260507_atomic_item_audits_and_focal_supplement.md`](convos/20260507_atomic_item_audits_and_focal_supplement.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) — Phase A only.
**Spawning artifact:** the morning's plan. Phase A was the first concrete step; Phase B + C remain.

#### Topics Explored

- 4 parallel `general-purpose` subagents executed Phase A1-A4 (OpenSecrets / LobbyView / Sunlight / Lacy-Nichols 2025 supplementary).
- A1 OpenSecrets — first audit verdict "drop"; user pushback forced recheck specifically asking whether tier definitions or worked examples exist anywhere in the article. Recheck found 5 named worked-example states + statistical anchors in the Rankings narrative. Verdict overturned to KEEP (75% score-mass projectable).
- A2 LobbyView — agent walked Kim 2018 + Kim 2025 + LobbyView Python package GitHub source; 46 schema fields written. Three ambiguities flagged.
- A3 Sunlight — agent confirmed the 5 items are simultaneously headline categories AND atomic scoring units. Per-item judgment surfaced item 4's near-typo + dimensional conflation; user applied "drop what we can't cleanly map" rule, locking 4-of-5 scope.
- A4 Lacy-Nichols — three-pass execution. (1) First pass: Figure 3 max-observed weight inference, US row sanity check passed at 81/182 = 45%. (2) Second pass attempted Wiley web-fetch — blocked on every route (403 / timeout / archive.org refused / PMC embargoed). (3) User manually downloaded Suppl File 1 + 2 as docx; pandoc-converted to text; second extraction agent populated all 50 indicators with verbatim weights, closed all 8 weight-UNKNOWNs, caught 2 weight-decomposition conflicts, populated 50-row prior-framework mapping CSV, reconciled 1,372-cell per-country matrix.
- Internal supplement-vs-Figure-3 discrepancy: Suppl Table 5's "TOTAL out of 100pts" row doesn't match Figure 3 percentages. Computing Table 5 raw × Table 4 weights reproduces Figure 3 exactly for all 28 countries → Figure 3 is authoritative; Table 5 TOTAL row is wrong. Documented in audit.
- Phase B handoff written capturing what's locked since the plan was authored.

#### Provisional Findings

- **Contributing-rubric set locked:** HiredGuns 2007 (47), FOCAL 2024 (50), Newmark 2017 (19), Newmark 2005 (18), Opheim 1991 (22), PRI 2010 (83), CPI 2015 C11 (14), OpenSecrets 2022 (4 cats partial — 75% mass), Sunlight 2015 (4 of 5), LobbyView (46 schema fields). 9 score-projection rubrics + 1 schema-coverage rubric.
- **OpenSecrets's article narrative is structurally informative beyond the methodology block.** When a methodology says "depending on circumstances", the article's per-state rankings often pin the ordinal via worked examples. First audit missed this; recheck found it. Lesson generalizes to any shallow rubric.
- **Sunlight's 5-criterion structure is intentionally shallow** by design — not "headline categories with atomic items waiting to be found". The compendium-mapping question is per-item: can the rubric tier be a deterministic function of compendium cells? Yes for 4 of 5; no for item 4 (compound + near-typo).
- **L-N 2025 Suppl File 1 is dramatically richer than the plan anticipated** — contains all three target tables (verbatim per-indicator scoring rules with P/N criteria, cross-rubric weight mapping, 28×50 per-country score matrix). Phase A4's "may need to fall back to Option C" was overkill.
- **First A4 pass's Figure-3-inferred weights were 40/42 correct** vs verbatim Suppl Table 4. Two conflicts (`financials.3`, `financials.8`, both 1→2) were weight-decomposition errors; the published Figure 3 weighted-cell values were already correct.
- **Finland's published total drops 70 → 46 weighted** after Suppl Table 5 reconciliation (13 cells previously read as 0 in Figure 3 are actually "/" / unassessable per verbatim source). Figure-3-visual-reading error, not a rubric meta-finding.
- **Wiley web-fetch is solidly blocked.** For future Wiley supplementaries, plan for manual user download.
- **Pandoc handles Wiley supplementary docx cleanly** — preserved enough table structure that a downstream agent extracted verbatim cell content without round-trips.

#### Decisions

| topic | decision |
|---|---|
| OpenSecrets 2022 | KEEP — partial (75% mass projectable). Cat 1 binary, Cats 2/3 few-shot anchored, Cat 4 decomposed. |
| LobbyView | KEEP — schema-coverage rubric (different shape from score-projection rubrics). 46 fields. |
| Sunlight 2015 | KEEP items 1, 2, 3, 5; DROP item 4 from projection layer. Source-extract TSV unchanged. |
| FOCAL 2024 | KEEP — fully populated from verbatim L-N 2025 Suppl File 1 weights. US row anchor 81/182 = 45%. |
| Phase C order | CPI 2015 C11 first (smallest), PRI 2010 second (largest, hardest aggregation), other rubrics in plan order. |
| Phase C scaffolding | `tests/fixtures/projection_inputs/<rubric>_<state>_<vintage>.json` + `src/lobby_analysis/projections/<rubric>.py`. |
| Phase B handoff | Written at `plans/_handoffs/20260507_phase_b_handoff.md`. Supplements plan with what's locked since Phase A. |

#### Mistakes recorded

1. Pre-flight misidentification of `Lacy-Nichols-Supple-File-1-IJHPM.pdf`. The "IJHPM" token in the filename was a giveaway it was the 2024 paper's supplementary, not the 2025 Milbank paper's. Cost: one wasted agent dispatch + one Wiley web-fetch attempt destined to fail. Mitigation: read the first page of any "already-on-disk" supplementary file before asserting it's the right one.
2. Used `cd+git` compound early in session despite CLAUDE.md explicitly calling out the heuristic that blocks it. User pushback led to memory entry `feedback_use_preapproved_bash_patterns.md`. Switched to `git -C <path>` for the rest of the session.
3. First A1 OpenSecrets audit was incomplete — only walked the methodology block, not the Rankings narrative. User pushback forced a recheck that overturned the drop verdict. Useful precedent: methodology blocks can be misleading on shallow rubrics; the article narrative often pins the ordinal via worked examples.

#### Results

- `results/items_LobbyView.tsv` (46 schema fields) + `.md`
- `results/items_FOCAL.tsv` (updated: 50/50 verbatim weights from Suppl File 1) + `.md`
- `results/focal_2025_lacy_nichols_per_country_scores.csv` (1,372 cells, verbatim Suppl Table 5)
- `results/focal_2025_lacy_nichols_prior_framework_mapping.csv` (50 rows, verbatim Suppl Table 4)
- `results/opensecrets_worked_examples_2022.csv` (18 rows of state-level anchors)
- `results/20260507_opensecrets_atomic_audit.md` (original drop audit, kept as appendix)
- `results/20260507_opensecrets_recheck.md` (supersedes drop verdict)
- `results/20260507_sunlight_atomic_audit.md` (audit + user 4-of-5 decision)
- `results/20260507_focal_a4_audit.md` (covers all three passes + Table-5-vs-Figure-3 discrepancy)
- `papers/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_{001,002}.docx` (Wiley supplementaries)
- `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_{001,002}.txt` (pandoc extracts)
- `plans/_handoffs/20260507_phase_b_handoff.md` (Phase B handoff for next implementing agent)

#### Next Steps

1. **Phase B** — per-rubric projection mapping docs. Read `plans/_handoffs/20260507_phase_b_handoff.md` first, then the plan. Start with CPI 2015 C11. Union of `compendium_rows` across mappings → `results/projections/disclosure_side_compendium_items_v1.tsv`.
2. **Phase C** — projection function implementations under TDD. Order: CPI first, PRI second, then plan order.
3. Open option: OpenSecrets state-map widget JS pull would close Cat 1 projectability. Currently sufficient for Phase B mapping; revisit only if Phase C validation shows the binary doesn't reach published Cat-1 scores.

---

### 2026-05-07 — 3-way consensus execution + CPI 2015 C11 atomic-item addition + projection-success criterion

**Convo:** [`convos/20260507_3way_consensus_execution_and_cpi_addition.md`](convos/20260507_3way_consensus_execution_and_cpi_addition.md)
**Plan executed:** [`plans/20260506_comp_assembly_3way_consensus.md`](plans/20260506_comp_assembly_3way_consensus.md)
**Spawning artifact:** locked plan from 2026-05-06 evening, written for the implementing agent to execute the 9-subagent dispatch.

#### Topics Explored

- Pre-flight check on plan ambiguities (CPI in-scope filter, M1 cluster-file scope, stability-metric formula); user confirmed M1 USA-only filter and asked for both stability metrics distinct.
- 9-subagent parallel dispatch via Claude Code Task tool (M1×3 / M2×3 / M3×3); ~9 min wall clock total.
- Validation pass + consensus tool execution.
- CPI 2015 atomic-item discovery: realized C11 placeholder was an artifact of CPI's atomic items not being in our local archive. Located `PublicI/state-integrity-data` GitHub repo via web search; pulled `2015/criteria.xlsx` ` Lobbying Disclosure` sheet. 14 atomic indicators (#196-#209), 5 sub-categories, explicit de jure / de facto labels.
- Compare/contrast against the 9-rubric consensus output: per-item fold-in mapping for all 14 CPI items.
- **Projection-success criterion landed (user direction):** compendium 2.0 is judged by whether each source rubric is fully reconstructible from compendium cells via per-rubric projection logic. Goal: minimum compendium that lets all 9 rubrics project correctly.
- **Criterion sharpened (same-session, user direction):** four explicit architectural commitments. (1) ONE compendium — single canonical row set. (2) ONE extraction pipeline — single methodology applied uniformly across rows / states / years; the compendium row schema must be uniform enough that one prompt approach works for every row. (3) Multi-year reliability — pipeline must work across vintages (OH 2010, 2015, 2024, 2025), not just one. (4) **Source rubrics are SANITY CHECKS on extraction accuracy, not the goal.** PRI 2010, CPI 2015, FOCAL 2024, etc. are independent ground-truth yardsticks; the deliverable is the populated data layer, and rubrics validate it. Multi-rubric × multi-year coverage gives redundant per-row ground truth: e.g., "expenditures benefitting officials" is read by 4 rubrics, so that one row's extraction has 4 independent checks; different vintages validate different extraction years.

#### Provisional Findings

- **24 strict consensus clusters / 63 items** (25%); **39 loose / 106 items** (42%); **146 items (58%) appear in NO loose cluster**; 40 items never co-grouped by any of the 9 runs. 468 pairs in human-review band.
- Per-method group counts and within-method spread: M1 cluster-anchored 153/189/201 (spread 48; 19.1% instability); M2 blind 159/180/195 (spread 36; 14.4% — most stable); M3 FOCAL-anchored 92/110/120 (spread 28; 45.6% within-method instability driven by big groups).
- M1 was supposed to be the most stable thanks to its shared embedding-cluster prior; it wasn't. Different runs gave the prior very different weight. M2 blind was the most stable.
- Per-paper consensus coverage is asymmetric: Newmark2005/2017 + Opheim heavily in strict (predicted by plan — same author / near-identical wording); PRI 3/83 in strict (atomic items too fine-grained to find consensus).
- Top disagreement pairs are FOCAL ↔ PRI semantic mismatches — filer-direction-and-granularity tradeoffs that compendium 2.0 design has to make a call on.
- **CPI 2015 C11 has 14 atomic items** (6 de jure + 8 de facto). Far smaller and higher-abstraction than HG 2007's 47 items — confirms CPI 2015 = HG 2007 successor at higher abstraction.
- **CPI 2015's de jure / de facto pairing is its distinctive contribution** — no other rubric makes this distinction explicit at item level. The 8 de facto items map onto the v1.1 schema's `practical_availability` axis rather than creating new compendium rows. **Direct empirical validation that the two-axis schema design is the right architecture.**
- **CPI 2015 is fully projectable** from a populated compendium 2.0, with two caveats: compendium must capture cell values not just row presence (for IND_197 threshold-zero, IND_199 annual cadence), and must include the principal-side spending-report row (IND_203, currently a PRI singleton in consensus).
- 50 states × 14 CPI items × 2015 vintage = a usable ground-truth dataset for cross-validating any practical_availability pipeline downstream.

#### Decisions

| topic | decision |
|---|---|
| **Compendium 2.0 success criterion** | **Four architectural commitments: (1) ONE compendium (single canonical row set), (2) ONE extraction pipeline (single methodology applied uniformly across rows / states / years), (3) multi-year reliability (vintages: e.g., OH 2010 + 2015 + 2024 + 2025), (4) source rubrics as SANITY CHECKS on extraction accuracy — published rubric scores are independent ground-truth yardsticks, not goals. Multi-rubric × multi-year coverage gives redundant per-row ground truth. Falsifiable test: populate compendium → apply each rubric's projection → compare to published rubric score in that vintage → match within tolerance. All rubrics must pass for vintages they cover, on a sample of states. Goal: minimum compendium size where all rubrics still project correctly across all vintages.** |
| 3-way consensus run | Done. 9 subagents dispatched, all valid, consensus tool run, report written. |
| CPI 2015 atomic items | Extracted 14 C11 items from `PublicI/state-integrity-data` GitHub repo. xlsx + scores.csv saved to `papers/`. Items added to `results/items_CPI_2015_lobbying.tsv`. |
| CPI 2015 fold-in vs re-dispatch | Manual fold-in (cheaper). 9-subagent re-dispatch with CPI items added is not warranted. |
| Per-rubric projection logic | Becomes the natural follow-on. CPI 2015 C11 (14 items × 50 states, with published per-state ground truth) is the smallest concrete first target. |

#### Mistakes recorded

1. Initial CPI filter framing missed the bigger picture — filtered to C11 placeholder per the plan, then mid-session realized atomic items live elsewhere. Plan was right within scope; scope was incomplete. Recovery: extracted from GitHub.
2. Subagents left scratch files in worktree (3 of 9: `build_groups.py`, `.tmpwork/`, `.scratch/`). Cleaned up post-hoc. Future briefs should explicitly forbid out-of-output writes.
3. M3 within-method instability headline (45.6%) is misleading without group-size context. Big groups amplify pair-level variance. Report.md decomposes this but the headline number can be misread.

#### Results

**Code:**
- `tools/build_usa_tradition_input.py` — pre-stages 252-item input CSV
- `tools/consensus_grouping.py` — per-pair agreement + strict/loose/human-review views + both stability metrics

**Run artifacts** (`results/3way_consensus/`):
- `usa_tradition_items.csv` (252 items input)
- `m{1,2,3}_*_run{1,2,3}.csv` (9 grouping outputs)
- `consensus_summary.csv` (1,034 pairs)
- `consensus_clusters_strict.csv` (24 clusters / 63 items at ≥8/9)
- `consensus_clusters_loose.csv` (39 clusters / 106 items at ≥6/9)
- `consensus_human_review.csv` (468 pairs at 3-5/9)
- `method_instability_report.md`
- `report.md` (headline + analysis)
- `briefs/` (the four brief files used for dispatch)

**CPI 2015 addition:**
- `papers/CPI_2015__sii_criteria.xlsx` — full 13-sheet codebook (7.6 MB; 245 indicators total across 13 categories)
- `papers/CPI_2015__sii_scores.csv` — per-state scores
- `results/items_CPI_2015_lobbying.tsv` — 14 atomic C11 items in standard schema

**Compare/contrast doc:**
- `results/20260507_cpi_2015_c11_vs_consensus.md` — per-item fold-in, projection-success criterion as load-bearing principle, recommendations, open work

**Late-session additions** (post-checkpoint, same day; see convo's "Post-checkpoint continuation" section for narrative):
- Lacy-Nichols 2025 verified — `papers/Lacy_Nichols_2025__lobbying_in_the_shadows.pdf` applies FOCAL to 28 countries; US federal LDA scored 81/182 = 45%; per-indicator per-country scores in Figure 3 + Suppl. File 1 Table 5 ≈ 1,400 cells of ground truth. **FOCAL flips from Option C to standard validation rubric.**
- Jurisdiction scope expanded: `{50 US states} ∪ {Federal_US (LDA)}`. Federal LDA extraction added; validation = FOCAL score + LobbyView schema coverage + raw LDA fields, all on the same federal data. LobbyView confirmed federal-only (no state aggregations exist).
- Plan written: `plans/20260507_atomic_items_and_projections.md` (commit `cdea880` + update `e51bc48`). Three phases — Phase A atomic-item audits (incl. new A4 for L-N 2025 Suppl. File 1 retrieval), Phase B disclosure-first projection mappings, Phase C projection function implementations + integration tests against published prior data.

#### Next Steps

1. Per-rubric projection logic for each of the 9 source rubrics. CPI 2015 C11 (14 items × 50 states) is the smallest concrete target — start there as proof-of-concept.
2. Round-trip validation harness — once a projection exists, run it on populated compendium cells for some states and compare to published rubric scores.
3. Cell-value schema decisions for compendium 2.0 (which rows carry binary cells, which carry typed values).
4. Compendium 2.0 design plan, written with the projection-success criterion as the formal acceptance test.
5. Optional: re-run the 9-subagent dispatch with CPI 2015's 14 items added. Tightens consensus marginally but doesn't change architecture.

---

### 2026-05-06 (late) — 3-method × 3-run consensus design (supersedes regex assembly plan)

**Convo:** [`convos/20260506_3way_consensus_design.md`](convos/20260506_3way_consensus_design.md)
**Plan produced:** [`plans/20260506_comp_assembly_3way_consensus.md`](plans/20260506_comp_assembly_3way_consensus.md)
**Plan superseded:** [`plans/20260506_comp_assembly_via_regex.md`](plans/20260506_comp_assembly_via_regex.md) (SUPERSEDED banner added)
**Spawning artifact:** the regex-assembly handoff plan from earlier the same day; user opened a critical review and pivoted twice during the conversation.

#### Topics Explored

- Critical review of the regex assembly plan; framing-strip mechanics traced through `tools/normalize_state_items.py` (the existing prototype already does HG `"Is X required?"` → `"X"` and Newmark `"Disclosure required: X"` → `"X (disclosure)"` — token-overlap dedup would catch these, but PRI rules don't exist yet and Newmark suffix interaction is non-trivial).
- LobbyView-for-states framing made explicit: the compendium IS the per-state question set; recognition that two rubrics ask the same question with different framing is what enables the per-state matrix to be coherent.
- Method-independence as the basis for triangulation: 2 methods that are too similar produce correlated outputs and triangulation buys nothing.
- M3 candidate selection: top-down taxonomy → paraphrase-then-group → FOCAL-anchored. User chose FOCAL after correcting the assistant's mischaracterization of FOCAL's "zero Prohibitions, minimal Personnel" as a blind spot — those aren't disclosure-mechanism items, so anchoring on FOCAL biases toward what the project actually cares about.
- Local subagent dispatch via Claude Code Task tool (MAX plan); cost concern drops, parallel dispatch is fine.

#### Provisional Findings

- The regex plan's cross-method-comparison framing was implicitly treating embedding as ground truth. User's reframing made clear that disagreement is symmetric and the more useful product of multiple methods is identifying ambiguity, not validating one method against another.
- Manual (LLM-judgment-based) grouping is plausibly stronger than the regex pipeline for this corpus, because the hard parts of regex (PRI rules, Newmark suffix, CPI filter) are all judgment calls dressed as engineering. Long-format output preserves provenance automatically.
- 3-method × 3-run separates two distinct sources of variance: method instability (within-method, across 3 runs) and method disagreement (between-method). 9 runs of one method only measure the former.
- FOCAL anchoring is well-aligned with project scope (disclosure-mechanism focus, what populates StateMasterRecord cells).
- The `~150 items` expected output is gut anchor only, not derived. Plan flags this explicitly.

#### Decisions

| topic | decision |
|---|---|
| Method set | M1 cluster-anchored / M2 blind / M3 FOCAL-anchored. |
| Replication | 3 runs per method = 9 dispatches. |
| Dispatch mechanism | Claude Code Task tool, `subagent_type="general-purpose"`, parallel — NOT Anthropic API. |
| Output schema | Long-format `source_paper, source_id, source_text, group_id, group_label`. Uniform across all 9 runs. |
| Consensus tool | `tools/consensus_grouping.py` per-pair agreement count → strict (≥8/9) / loose (≥6/9) / human-review (3–5/9) views. |
| CPI_2015 | Filter upfront in pre-stage; 15/16 rows are non-lobbying-domain noise. |
| PRI | IN scope per 2026-05-06 partial clearance; loaded from `items_PRI_2010.tsv` separately, joined with the 8-rubric corpus from `cross_rubric_items_clustered.csv`. |
| Regex plan | Superseded; banner added; preserved for traceability. |

#### Mistakes recorded

1. Assistant over-engineered the regex plan critique with methodological perfectionism that the user's "we don't need rigorous justification" framing made misplaced.
2. Assistant confabulated derivation math for the ~150 expected-size estimate; user clarified it was gut instinct only.
3. Assistant initially mischaracterized FOCAL's category coverage gaps as a blind spot; corrected by user — those gaps are out of project scope.

#### Results

- Plan doc: [`plans/20260506_comp_assembly_3way_consensus.md`](plans/20260506_comp_assembly_3way_consensus.md)
- Convo: [`convos/20260506_3way_consensus_design.md`](convos/20260506_3way_consensus_design.md)
- Regex plan (superseded): [`plans/20260506_comp_assembly_via_regex.md`](plans/20260506_comp_assembly_via_regex.md) — banner added at top.

No code or data artifacts produced this session — this was a planning conversation; the plan is the deliverable.

#### Next Steps

- Next agent (possibly user from the road) executes the 3-way consensus plan: pre-stage input CSV, write briefs, dispatch 9 Task subagents in parallel, validate outputs, run `tools/consensus_grouping.py`, surface results in `report.md`.
- After results return: user reviews strict-consensus clusters + human-review pile; canonical question list approved; compendium 2.0 schema design plan written as a follow-up.

---

### 2026-05-06 — Compendium assembly via embeddings (te3-large) + first candidate item set

**Convo:** [`convos/20260506_comp_assembly_via_embeddings.md`](convos/20260506_comp_assembly_via_embeddings.md)
**Plan produced:** [`plans/20260506_comp_assembly_via_regex.md`](plans/20260506_comp_assembly_via_regex.md) (handoff for the parallel regex assembly)
**Spawning artifact:** the 2026-05-06 post-session continuation block in `convos/20260503_pm_acquisition_and_descriptives.md` had committed `tools/embed_cross_rubric.py` for desktop execution; this session ran it.

#### Topics Explored

- OpenAI `text-embedding-3-large` embedding run over the 509-item rubric atomic-items corpus. Vectors + index + similarity matrix preserved.
- Threshold tuning for single-link clustering (sweet spot at sim ≥ 0.68: 28 clusters / 106 items / 10 spanning ≥3 rubrics / 3 spanning ≥5 rubrics).
- Tradition-tagged cluster analysis (state / euro / cross). Counted clusters per tradition combination; identified the rare cross-tradition bridges.
- Coverage analysis: HiredGuns + FOCAL + Newmark2017 vs the rest of the state-tradition corpus.
- Normalization side-experiment: per-rubric regex framing-strip (HG interrogative, Newmark2017 "Disclosure required:", etc.) re-embedded over the 134 state-tradition items; modest tightening of within-tradition clusters; not load-bearing for the candidate set.
- Built first compendium-2.0 candidate item set via embedding-based coverage analysis. v1 = 126 items (HG + FOCAL + Newmark2017 + 10 Opheim coverage extensions). v2 = 209 items (v1 + all 83 PRI atomic items, added per explicit user clearance).
- Renamed deliverables from `comprehensive_set` → `comp_assembly_embed_v{n}` after user pushback that the original name pre-claimed an answer the artifact didn't have. Saved naming lesson to memory.

#### Provisional Findings

- Within-tradition consolidation works well at sim ≥ 0.68 (state side: HG+Newmark2017+Opheim+Sunlight on qualification thresholds, 8×4 cluster; multiple Newmark2005↔Newmark2017↔Opheim 3-rubric consolidations on definition triggers. Euro side: 5-rubric "what to register" cluster, 5-rubric "open-data accessibility" cluster, 4-rubric "code of conduct" cluster).
- Cross-tradition (state↔euro) bridging is sparse even at frontier embedding quality. Only 1 cross-tradition cluster forms at sim ≥ 0.68 ("timely disclosure / reporting frequency," 5 rubrics). Many additional state↔euro pairs cluster at sim 0.60-0.66 but get blocked by single-link chaining considerations.
- The European↔state vocabulary divide appears structural, not just lexical. Each rubric organizes items around a different conceptual frame (declarative-disclosure-inventory vs spending-report-itemization-audit vs normative-completeness vs meeting-record-schema vs public-official-duty). Stripping framing helps within-tradition but not cross-tradition.
- HG + FOCAL + Newmark2017 cover the state-tradition well: 79% at sim ≥ 0.70, 84% at sim ≥ 0.65, 89% at sim ≥ 0.55 across 184 state+cross atomic items. Real coverage gap is Opheim's enforcement battery (6 items, COGEL Blue Book Table 31 — Newmark dropped these in 2005 and Strickland inherited the drop) plus Opheim's income-disclosure pair (2 items, distinct from compensation).
- Newmark2005 and Sunlight residual gaps appear to be short-label artifacts rather than missing concepts.
- CPI_2015 SII is mostly out of scope for compendium-2.0 (multi-domain integrity scorecard; only 1 of 16 items is lobbying-specific).
- European-tradition rubrics are largely out of US-state-lobbying-disclosure scope (right-to-participate frameworks, Dutch consultation reform, EU MEP declarations, EU operational specifics). A small subset (e.g. IBAC MP-meeting-disclosure) might be worth flagging as `cmp_*` reference items in a future pass.

#### Decisions

| topic | decision |
|---|---|
| Embedding provider | OpenAI te3-large for production; sentence-transformers MiniLM kept as offline fallback. |
| Embedding artifacts | Save raw vectors + index + similarity matrix; preserve all so downstream re-clustering / UMAP / centroid work doesn't require API re-calls. |
| `comp_assembly_embed_v1` | HG + FOCAL + Newmark2017 + 10 Opheim items = 126. |
| `comp_assembly_embed_v2` | v1 + all 83 PRI = 209. PRI sourced from historical pri-2026-rescore transcriptions, NOT re-extracted from paper text. |
| PRI clearance | Partial clearance recorded 2026-05-06: PRI may be ADDED as `ext_pri_2010_*` coverage extension. Still blocked: structural anchoring, "match PRI" calibration, PRI-shaped row-frame seeding. STATUS.md ⛔ block remains for everything else. |
| File naming | `comp_assembly_<method>_v{n}.{tsv,md}` — names by method, not conclusion. Slot reserved for parallel `comp_assembly_via_regex` next. |
| Old (141-row PRI-shaped) compendium | Not a target / baseline / benchmark. Memory entry added. |

#### Mistakes recorded

1. Volunteered comparison against the old compendium when user asked a sizing question. Memory `feedback_dont_volunteer_comparisons.md` added.
2. Named files `comprehensive_set.tsv` / `_v2.tsv` (claims-to-be-the-answer naming). Memory `feedback_name_by_method_not_conclusion.md` added; files renamed.
3. Initial coverage analysis used wrong framing (within-set dedup instead of "% of each parent rubric covered by the set"). User redirected; recovered same turn.
4. Worktree-venv mismatch initially loaded main worktree's venv. Fixed via `unset VIRTUAL_ENV && uv sync && uv pip install` against worktree-local venv.

#### Results

Embedding artifacts (raw, full corpus):
- `results/embed_vectors__openai__text-embedding-3-large.npy` — 509×3072 float32
- `results/embed_index__openai__text-embedding-3-large.csv`
- `results/embed_similarity_matrix__openai__text-embedding-3-large.npy`
- `results/embed_clusters_full__openai__text-embedding-3-large.txt`
- `results/embed_clusters_at_thresholds__openai__text-embedding-3-large.csv`

Embedding artifacts (state-only normalized side-experiment):
- `results/cross_rubric_items_state_normalized.csv`
- `results/state_normalized/embed_*__openai__text-embedding-3-large.{npy,csv,txt}`

PRI items in standard schema:
- `results/items_PRI_2010.tsv` — 83 atomic items

Candidate item sets:
- `results/20260506_comp_assembly_embed_v1.tsv` + `.md` — 126 items
- `results/20260506_comp_assembly_embed_v2.tsv` + `.md` — 209 items

Tools:
- `tools/embed_cross_rubric.py` (extended with OpenAI provider + raw-vector preservation)
- `tools/normalize_state_items.py`
- `tools/assemble_comp_embed.py`

#### Next Steps

- Next agent runs `comp_assembly_via_regex` per the handoff plan: parallel candidate set produced via regex/python framing-normalization + dedup, scoped to USA-tradition rubrics only (Europe out of scope per user). Output: `comp_assembly_regex_v1.{tsv,md}`.
- After both candidate sets exist, reconcile: items present in both / present in only embed / present in only regex. The reconciled set is the actual compendium 2.0 input candidate, not either method's output alone.
- Open follow-ups parked in the convo's Open Questions section: borderline Opheim items, European-tradition coverage-comparison flagging, PRI-in-embedding-space dedup analysis.

---



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



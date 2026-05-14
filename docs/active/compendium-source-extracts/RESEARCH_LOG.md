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

### 2026-05-13 (paper-audit pre-merge) — `auditing-paper-summaries` (LAST pre-merge gate; branch is merge-ready)

**Convo:** [`convos/20260513_paper_summaries_audit_premerge.md`](convos/20260513_paper_summaries_audit_premerge.md)
**Handoff executed:** [`plans/_handoffs/20260514_paper_summaries_audit_premerge.md`](plans/_handoffs/20260514_paper_summaries_audit_premerge.md) (drafted 2026-05-13 late-late-late-late-late eve; executed same UTC day, hence convo dated 2026-05-13)
**Predecessor session:** [`### 2026-05-13 (late-late-late-late eve) — Compendium 2.0 row-freeze brainstorm`](#2026-05-13-late-late-late-late-eve--compendium-20-row-freeze-brainstorm-freeze-landed) below

#### Topics Explored

- **Inventory reality check.** Handoff said "17 PAPER_INDEX entries, 18 PDFs, 16+ branch-added papers." Actual inventory: **17 PAPER_INDEX entries, 37 PDFs in `papers/`, 39 .txt files in `papers/text/`**. Discrepancy explained: the handoff numbers (drafted during the row-freeze session) reflected an earlier branch state; ~20 papers were added during the branch's 3-week life (mostly during the cross-rubric Phase A/B work that pulled in international/comparative-regulation literature).
- **Format-audit script behavior.** `skills/auditing-paper-summaries/audit_paper_summaries.py` over-counts entries because `PAPER_SUMMARIES.md` uses a mixed convention: Bacik 2025 + Kim 2025 use `## Paper` H2s with nested `### Key findings` / `### Method` / `### Notes for our project` subsections, while the other 15 papers use `### Paper` H3s under `## Category` H2s. The script's `### Paper Title` pattern treats subsection H3s as paper entries. Documented in `PAPER_INDEX.md` Audit Notes; manual count is correct.
- **Roth 2020 orphan investigated.** `papers/text/Roth_2020__lobbymeter_robustness_index.txt` has no matching PDF in `papers/`. Read confirmed the .txt is a **WebFetch summary capture from 2026-05-03** of a Google Sites page (lobbymeter.eu project, Aminata Sarah Roth) — the source is web-only, not PDF; the .txt functions as both source-of-record and "extracted text." Decision: keep the .txt, add Roth 2020 to PAPER_INDEX with "(web-source-only; no local PDF)" annotation under the new International / Comparative category.
- **Lacy-Nichols supplementary file naming mismatch resolved.** `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` has no `.txt` of the same name, but `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_{001,002}.txt` exist with no corresponding `.pdf`. Confirmed: these are the extracted text of the suppl PDF, split into two parts and renamed at extraction time. Per user direction, **the canonical mapping is documented in `PAPER_INDEX.md` Audit Notes** (durable) **not in the convo** (session-scoped) — rationale: convos are for retracing logic, PAPER_INDEX is the load-bearing reference.
- **20-paper survey via subagent.** Dispatched a single `general-purpose` subagent with explicit per-paper depth cap (~500 lines of extracted text) to produce: title, authors/publisher, date, ≤35-word index summary, suggested category, 2-3-sentence summaries-stub, and confidence rating. Subagent returned MEDIUM-HIGH-confidence stubs for all 20 papers with honest LOW/MEDIUM flags where extraction was sparse (Global Data Barometer 2022, SOMO 2016).
- **Category structure update.** PAPER_INDEX previously had 4 categories: Entity Resolution & Record Linkage / Lobbying Data Infrastructure / Compliance & Disclosure Quality / State Lobbying Regulation Measurement. Added 2 new categories to absorb the international/comparative additions: **International / Comparative Lobbying Regulation** (14 entries — anchors the Opheim → CPI → comparative-international lineage cited in Lacy-Nichols 2024/2025) and **Lobbying & Political Outcomes (empirical)** (2 entries — Flavin 2015 and Strickland 2014/2018; distinct from rubric-creating measurement papers because they *use* the measures). Existing categories grew: Lobbying Data Infrastructure +LaPira & Thomas 2014; Compliance & Disclosure Quality +Lacy-Nichols 2023 + Chung 2024; State Lobbying Regulation Measurement +CPI 2015 SII (the source of the C11 atomic items extracted on this branch's 2026-05-07 session).
- **Factual spot-checks DEFERRED with explicit followup.** Handoff Stop condition #4 ("at least 3 summaries factually accurate against the source PDF") was deferred per user direction: the 17 pre-existing summaries are stable pre-branch and doing 3 deep factual checks at the merge gate adds low signal for the audit work, but the load-bearing downstream consumers (Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010) **will be hand-coded in Phase C projection logic** on a successor branch — factually wrong summaries would propagate into projection code. Per user "we need a task or note to be sure we don't forget at the end of this session" the followup is recorded in two durable places: (a) PAPER_INDEX.md Audit Notes section (visible whenever paper lookup happens), and (b) the upcoming Phase C kickoff handoff (when that branch is cut post-merge).
- **Strickland filename year discrepancy surfaced.** Filename is `Strickland_2014__lobbying_laws_interest_groups.pdf` but the SAGE DOI (10.1177/1532673X18788049) and "788049" article ID indicate 2018 publication; filename is from a working-paper version. Decision: leave filename as-is (don't rename a checked-in PDF mid-merge), note the actual publication date in the PAPER_INDEX / PAPER_SUMMARIES entries.

#### Provisional Findings

- **Branch is merge-ready** after this audit landed. All structural invariants now hold: every PDF in `papers/` has either a corresponding `.txt` (or is part of a documented supplementary-file mapping); every paper has at least a stub entry in PAPER_INDEX + PAPER_SUMMARIES.
- **20 papers were stub-indexed, not fully audited.** The "[stub-indexed]" annotation on each new entry signals to future readers that the depth here is single-pass — full-read pass is a future-audit candidate. The most project-relevant of the 20 (LaPira & Thomas 2014 for biographical-record linkage methodology; McKay & Wozniak 2020 for cross-source disclosure validation; Strickland 2014/2018 for registration-rate endogeneity; AccessInfo 2015 for normative disclosure-field schema) deserve deeper reads when their relevance becomes load-bearing.
- **Two new PAPER_INDEX categories are now stable.** International / Comparative Lobbying Regulation will likely grow further as additional Lacy-Nichols-adjacent or OECD-adjacent papers are added; Lobbying & Political Outcomes (empirical) has only 2 entries and could fold into Category 4 (State Lobbying Regulation Measurement) if it doesn't grow, but the *uses-the-measure* vs. *creates-the-measure* distinction is real.
- **The format-audit script is overly strict for this repo's PAPER_SUMMARIES convention.** Script expects every entry to have `arXiv` / `Authors` / `Date` / `Summary` / `Key findings` / `Relevance` fields. Repo uses a looser convention with narrative Summary + Key findings + Relevance subsections. Either the script needs adjustment for this repo's convention or PAPER_SUMMARIES needs reformatting; documented as a known issue in PAPER_INDEX Audit Notes, not blocking merge.

#### Decisions

| topic | decision |
|---|---|
| Treatment of 20 branch-added papers | **Stub-index all 20** in PAPER_INDEX + PAPER_SUMMARIES with "[stub-indexed]" annotation and "not factually audited" stubs. Full-read deferred. |
| Roth 2020 orphan .txt | **Keep as web-source-only** with explicit PAPER_INDEX annotation; no PDF to obtain. |
| Lacy-Nichols suppl naming mapping | **Document in PAPER_INDEX.md Audit Notes** (durable), not in convo summary alone. Mapping: `papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf` → `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_{001,002}.txt`. Do not rename either file. |
| Factual spot-checks (handoff Stop #4) | **Defer to Phase C successor branch** with explicit followup note in PAPER_INDEX.md Audit Notes. Priority targets when revisited: Newmark 2017, Lacy-Nichols 2024 / FOCAL, PRI 2010. |
| Strickland filename year (2014 vs 2018 actual) | **Leave filename**, document actual publication date in entries. SAGE DOI 10.1177/1532673X18788049 cited. |
| New PAPER_INDEX categories | **Add 2:** International / Comparative Lobbying Regulation (14 entries); Lobbying & Political Outcomes (empirical) (2 entries). |
| `auditing-paper-summaries` script discrepancy | **Document as known issue** (mixed heading convention in PAPER_SUMMARIES); not blocking merge. Reconciliation deferred. |
| Merge-readiness | **Branch is merge-ready** post this commit. All handoff Stop/done conditions satisfied or explicitly deferred-with-followup. |

#### Mistakes recorded

- Initial TaskUpdate calls used `id` instead of `taskId` (different harness's tool naming); failed silently for tasks 1+3 leaving them stale. Fixed when loading TaskUpdate schema via ToolSearch. Not a research mistake; surface-level harness-specific quirk.
- The handoff filename `20260514_paper_summaries_audit_premerge.md` is dated 2026-05-14 but the work was executed on 2026-05-13 (handoff was drafted late-late-late-late-late eve 2026-05-13 anticipating next-day execution). Convo filename uses 2026-05-13 (actual execution date) — slight asymmetry, called out in convo's frontmatter.

#### Results

- [`PAPER_INDEX.md`](../../../../PAPER_INDEX.md) — restructured with 2 new categories + 20 stub entries + Audit Notes section (Lacy-Nichols suppl mapping + Roth 2020 web-source-only + deferred factual audits + format-script known issue). Total: 37 PAPER_INDEX entries matching 37 PDFs + 1 web-only (Roth) — 38 papers indexed.
- [`PAPER_SUMMARIES.md`](../../../../PAPER_SUMMARIES.md) — 20 new stub entries appended under new H2 categories + 3 additional H2 continuations for in-category additions. All new entries marked `*[stub-indexed]*` and `**Stub-indexed; not factually audited.**` for honest depth-marking.
- This RESEARCH_LOG entry + the convo summary at `convos/20260513_paper_summaries_audit_premerge.md`.

#### Next Steps

1. **Commit + push this audit landing.** Single clean commit with PAPER_INDEX + PAPER_SUMMARIES + STATUS + RESEARCH_LOG + convo. Branch is then merge-ready.
2. **Merge `compendium-source-extracts` → `main`.** v2 row set (181 rows) becomes the contract for 3 successor branches. Per branch hygiene, do this in a fresh session.
3. **Archive `docs/active/compendium-source-extracts/` → `docs/historical/compendium-source-extracts/`** post-merge; add archive row to STATUS.md per the lifecycle in CLAUDE.md.
4. **Cut 3 successor branches in parallel** (per Option B locked 2026-05-13):
   - **OH statute retrieval** (Track A): adds OH 2007 + OH 2015 to existing OH 2010 + OH 2025 bundles; HG 2007 ground-truth retrieval sub-task.
   - **Extraction harness brainstorm** (Track B): brainstorm-then-plan; inherits prompt-architecture from archived `statute-extraction` iter-2; references v2 row set.
   - **Phase C projection TDD**: locked rubric order CPI 2015 C11 → PRI 2010 → Sunlight 2015 → Newmark 2017 → Newmark 2005 → Opheim 1991 → HG 2007 → FOCAL 2024 (8 rubrics; LobbyView is schema-coverage, not score-projection). **The Phase C kickoff handoff should reference PAPER_INDEX.md Audit Notes** for the deferred factual-accuracy audit on Newmark 2017 + FOCAL + PRI 2010.

---

### 2026-05-13 (late-late-late-late eve) — Compendium 2.0 row-freeze brainstorm (FREEZE LANDED)

**Convo:** [`convos/20260513_row_freeze_brainstorm.md`](convos/20260513_row_freeze_brainstorm.md)
**Plan executed:** [`plans/_handoffs/20260513_row_freeze_brainstorm.md`](plans/_handoffs/20260513_row_freeze_brainstorm.md) (full Phases 1–5).
**Decision log produced:** [`results/projections/20260513_row_freeze_decisions.md`](results/projections/20260513_row_freeze_decisions.md) (30 decisions D1-D30 + Sections 1-7 + appendix).
**Output TSV:** [`results/projections/disclosure_side_compendium_items_v2.tsv`](results/projections/disclosure_side_compendium_items_v2.tsv) (181 rows).
**Generation script:** [`tools/freeze_canonicalize_rows.py`](../../../../tools/freeze_canonicalize_rows.py) (idempotent).

#### Topics Explored

- **Naming canonicalization (load-bearing).** Greped 9 mapping docs for cross-rubric naming drift on canonical observables. Surfaced: (a) compensation cluster naming drift (PRI E2f_i `lobbyist_report_includes_direct_compensation` + CPI #201 `lobbyist_spending_report_includes_compensation` are the same observable as `lobbyist_spending_report_includes_total_compensation`; doc narratives all cross-cite, mechanical union missed), (b) PRI E1/E2 prefix inconsistency (`lobbyist_report_includes_*` violates α form-split convention; should be `lobbyist_spending_report_includes_*`), (c) `materiality_threshold_*` (PRI D1) conflicts with Sunlight's three-threshold-concept framework (rename to `lobbyist_filing_de_minimis_threshold_*`), (d) `compensation_broken_down_by_client` vs `_by_employer` (Newmark Open Issue 2; rename to `_by_payer`), (e) `def_target_legislative_or_executive_staff` vs `def_target_legislative_staff` (granularity-bias supports split into `legislative_staff` + `executive_staff`), (f) `lobbyist_disclosure_*` prefix vs `lobbyist_reg_form_*` for descriptors-side rows.
- **LobbyView freeze-candidates.** LV-1 IN as firm row (real distinguishing observable; LDA explicit; Kim 2025 GNN feature). LV-2 OUT (operational metadata). LV-3 OUT (user override of LobbyView mapping recommendation; YAGNI defers single-rubric typed-enum complexity). LV-4 OUT (operational; matches LobbyView mapping recommendation). All 4 candidate rows resolved.
- **OpenSecrets-distinctive candidates.** OS-1 (`separate_registrations_for_lobbyists_and_clients`) IN under path-b (project-internal need; no current rubric reads but real distinguishing observable). OS-2 (compensation exact-vs-ranges) and OS-3 (per-individual-vs-aggregate) stay reversibly tabled.
- **Atomization meta-rule.** User locked: keep current per-rubric atomization. PRI cadence binaries stay 12; PRI Q7a-o stays 15 binaries; FOCAL set-typed scope.1/.4 stays set-typed; FOCAL contact_log/descriptors stay atomized; HG Q31/Q32 stays 4 binaries. Source-rubric structure preserved; projection identical regardless.
- **Single-rubric walk by family.** Per Decision Rule 1 + atomization meta-rule, all 132 single-rubric rows in v2 are KEEP (D25-D30 batch-resolve by family: actor_*, PRI E1/E2 contents, PRI exemptions/govt_agencies/public_entity_def/law_*, HG-distinctive practical-axis, FOCAL-distinctive, CPI-distinctive). No single-rubric drops.
- **Per-doc Open Issues triage.** ~36 real freeze decisions per the handoff. ~12 resolved at freeze (D9-D24); ~7 deferred to Phase C as projection-logic questions (D24); ~70 of the 89 enumerated were status notes / promotions / watchpoints already covered.
- **Cell-type semantic conflicts (3).** D9: `lobbying_data_downloadable_in_analytical_format` becomes single binary. D10: `lobbyist_registration_required` stays two-axis. D11: `registration_deadline_days_after_first_lobbying` stays two-axis.

#### Provisional Findings

- **Compendium 2.0 row set: 181 rows** (180 firm + 1 path-b unvalidated). Down from v1's 186 rows (182 firm + 4 freeze-candidates) — net change: **-5 rows**. The decline reflects merges (D1+D2 + D6 collapse half) outweighing additions (LV-1 + OS-1 + D6 split half).
- **Single most-validated row: `lobbyist_spending_report_includes_total_compensation` at 8 rubrics** (cpi_2015 + pri_2010 + sunlight_2015 + newmark_2017 + newmark_2005 + opheim_1991 + hg_2007 + focal_2024). The mechanical TSV undercounted at 6-rubric; canonicalization revealed PRI E2f_i + CPI #201 + the existing 6-rubric set all read the same observable. This is the single load-bearing canonical row — every projection function will validate against it.
- **Final tier distribution:** 8-rubric × 1, 6-rubric × 4, 5-rubric × 3, 4-rubric × 6, 3-rubric × 10, 2-rubric × 24, 1-rubric × 132, 0-rubric × 1. Single-rubric mass is 73% — same as before freeze (135/182 = 74%); freeze didn't deflate single-rubric tier because all those rows passed Decision Rule 1's "real observable" test.
- **The freeze is a CONTRACT.** Three successor branches (OH retrieval, harness brainstorm, Phase C projection TDD) reference v2 as their row-set contract. Once `compendium-source-extracts` merges to main, row-set changes require a new branch.
- **The decision log is the durable artifact.** `20260513_row_freeze_decisions.md` captures the 30 decisions + rationale + the post-freeze inventory + appendix on what's NOT addressed (v2.0 schema bump, practical-axis cell population deferred to Track B, paper-index audit, embedding-purge already done, provenance-header retrofit). Anti-loop artifact for future agents.
- **Future freeze edits via the script + decision log.** `tools/freeze_canonicalize_rows.py` is idempotent — re-running reproduces v2 exactly. Future row-set adjustments encode in the script's data structures + this decision log, then re-run, rather than editing v2.tsv by hand.

#### Decisions

| topic | decision |
|---|---|
| Naming canonicalization | 30 decisions D1-D30 in the decision log. 4 row merges (D1+D2 + D6 collapse half) + 30 row renames (D3+D4+D5+D8) + 1 row split (D6 split half). |
| LV freeze-candidate dispositions | LV-1 IN; LV-2/3/4 OUT. |
| OS freeze-candidate dispositions | OS-1 IN under path-b; OS-2/3 stay tabled. |
| Atomization meta-rule | Keep current per-rubric atomization (D20). |
| Single-rubric walk | All 132 single-rubric rows KEEP per Decision Rule 1 (D25-D30). |
| HG-1 (`def_target_executive_agency` carve-out split) | DEFER (D21). Single cell stays. |
| HG-2 (Q2 'make/spend' projection) | `min(compensation_threshold, expenditure_threshold)` where both non-null (D22). No new compendium row. |
| Opheim catch-all un-projectable | OUT-of-scope; document in Opheim mapping (D23). |
| ~7 remaining Open Issues (Sunlight item-4, Newmark 2005 vintage-stability, Opheim cadence-monthly, HG Q12/Q23/Q24/itemized-detail, FOCAL partly-tier) | DEFERRED to Phase C as projection-logic questions (D24). |
| 3 semantic cell_type conflicts | Resolved D9-D11. |
| v2 row count | 181 (180 firm + 1 path-b unvalidated). |
| Successor sequencing (carry-forward from prior session) | Option B confirmed: merge after this freeze; cut 3 successor branches in parallel. |

#### Mistakes recorded

- Initially over-confident about LV-3 (recommended IN with typed enum); user overrode to OUT. Lesson: single-rubric LobbyView additions need stronger affirmative case than "could be typed enum"; YAGNI properly defers.
- Initial Section 6 row-tier-count math wrong (described 131 expected vs 132 actual as a discrepancy); re-derived correctly. Lesson: when applying multi-row merges, walk effect on each tier separately rather than netting end-to-end.

#### Results

- [`results/projections/disclosure_side_compendium_items_v2.tsv`](results/projections/disclosure_side_compendium_items_v2.tsv) — post-freeze canonical TSV (181 rows; tier distribution above).
- [`results/projections/20260513_row_freeze_decisions.md`](results/projections/20260513_row_freeze_decisions.md) — decision log (30 decisions D1-D30; Sections 1-7 + appendix).
- [`tools/freeze_canonicalize_rows.py`](../../../../tools/freeze_canonicalize_rows.py) — idempotent regeneration script (~250 lines).

#### Next Steps

1. **`auditing-paper-summaries` pass** — verify the 16+ branch-added papers are in PAPER_INDEX + PAPER_SUMMARIES (only remaining pre-merge audit per prior session's deferred items). **Forward-planning handoff:** [`plans/_handoffs/20260514_paper_summaries_audit_premerge.md`](plans/_handoffs/20260514_paper_summaries_audit_premerge.md) — self-contained brief for the next-session agent.
2. **Merge `compendium-source-extracts` → main.** v2 row set becomes the contract.
3. **Cut 3 successor branches in parallel** (per Option B locked 2026-05-13): OH statute retrieval (Track A), extraction harness brainstorm (Track B), Phase C projection TDD (locked order: CPI → PRI → Sunlight → Newmark 2017 → Newmark 2005 → Opheim → HG → FOCAL).

---

### 2026-05-13 (late-late-late eve) — Union step + pre-merge audit (Phase B closure plumbing)

**Convo:** [`convos/20260513_union_step_and_premerge_audit.md`](convos/20260513_union_step_and_premerge_audit.md)
**Plan executed:** [`plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md`](plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md) §§1-2 (union + audits); §3 (draft 3 successor plans) deferred per ordering pushback.
**Handoff this session was executing:** [`plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md`](plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md).

#### Topics Explored

- **Sequencing pushback at session start.** Handoff scoped union + audits + draft 3 successor plans in one session. Surfaced internal tension: row-freeze brainstorm (next-next session per Option B) regenerates the union TSV → v2 → invalidates plan-doc row-set references → re-pass required. User scoped to union + audits only; defer plans + row-freeze to later.
- **Union script (`tools/union_projection_rows.py`).** Parses `## Summary of compendium rows touched` section per doc; handles 3 table shape variants (5-col without Status, 6-col with Status, PRI's 2-subtable axis-implied form, LobbyView's coverage-summary form). Composite row entries (Opheim 2-cell monthly OR, Newmark 2005 8-cell more-frequent-than-annual OR) expanded into reads-of-constituent-PRI-rows rather than phantom row_ids. LobbyView's 4 candidate NEW rows hardcoded with `status=freeze-candidate`. Cell-type whitespace/backtick variants normalized.
- **TSV produced.** `results/projections/disclosure_side_compendium_items_v1.tsv` — 186 rows (182 firm + 4 freeze-candidates). Columns: `compendium_row_id, cell_type, axis, rubrics_reading, n_rubrics, first_introduced_by, status, notes`.
- **Headline gap finding.** Handoff's running estimate was ~111 disclosure-side rows; TSV shows **182 firm rows**. Gap (~73 rows) is NOT a dedup miss — dedup correctly collapsed 271 table-rows → 184 → 182 (one composite-row fix). The gap is that **mapping doc narratives systematically undercount their own NEW-row contributions vs what their tables actually carry**: PRI doc claims 47 distinct disclosure-law rows (table has 61; doc has internal arithmetic error 11+4+4+3+19+18=59); HG doc claims 22 NEW (table has 29; "8 practical Q31/Q32 only" undercount, omits Q28-Q30 + Q33-Q38); Newmark 2017 doc claims 14 (table has 15).
- **Cross-rubric naming drift surfaced.** Same observable appears under 3 distinct row_ids across docs: CPI's `lobbyist_spending_report_includes_compensation`, PRI's `lobbyist_report_includes_direct_compensation` (E2f_i), and later docs' `lobbyist_spending_report_includes_total_compensation`. Doc narratives claim "7-rubric-confirmed" based on human-author canonical understanding; TSV's mechanical match counts 6 rubrics. The TSV's cross-rubric counts are lower bounds; canonicalization is row-freeze-brainstorm work.
- **Single-rubric distribution:** 135 of 182 firm rows (74%) are single-rubric. Heavily driven by PRI (81 first-introduced rows, mostly fine-grained PRI-distinctive observables — A-family actors, B-family exemptions, Q7a-o search-filters, E-family principal/lobbyist parallels), FOCAL (34 first-introduced, mostly per-meeting contact_log + descriptors), and HG (29 first-introduced, mostly practical-availability access-tier cells).
- **Top cross-rubric rows (n_rubrics ≥ 5):** 5 rows at 6-rubric (gifts/entertainment lobbyist+principal pair; def_target_executive_agency; compensation_threshold; total_compensation), 3 at 5-rubric (compensation_broken_down_by_client; categorizes_expenses; def_target_legislative_branch). These are the load-bearing observables — the rows freeze KEEPs automatically.
- **Audit-docs findings.** All 17 convos referenced and all plans/handoffs linked. **Structural bug fixed**: `convos/20260503_pm_acquisition_and_descriptives.md` session entry body existed in RESEARCH_LOG but its `### 2026-05-03 (pm) — ...` heading was missing. Restored. RESEARCH_LOG now has 17 session entries matching 17 convos, all reverse-chronological. ~35 results .md files lack explicit `<!-- Generated during: X -->` provenance per skill literal; most have implicit provenance (`**Plan:**` / `**Source artifact:**` / methodology sections). Deferred — not blocking merge.
- **Branch-hygiene findings.** ~9MB of embedding `.npy` binaries in branch history (`embed_vectors__openai__text-embedding-3-large.npy` 6.25MB + 1.6MB; `embed_similarity_matrix__openai__text-embedding-3-large.npy` 1MB + 72KB). Regeneratable from `tools/embed_cross_rubric.py`. **User decision: purge via `git filter-repo` after this checkpoint** (rationale: the embedding-based assembly approach was an early exploration superseded by the "one compendium to spawn them all" framing — the .npy outputs are not load-bearing). PAPER_INDEX 17 entries vs 18 PDFs flagged for a future `auditing-paper-summaries` session.

#### Provisional Findings

- **Compendium 2.0 disclosure-side inventory at Phase B close: 182 firm rows + 4 LobbyView freeze-candidates = 186 total.** Authoritative TSV count, supersedes the ~111 running estimate. Going into row-freeze with **more rows to consider than expected**.
- **Single-rubric mass is heavy (74%).** Row-freeze should consider whether the high-atomization PRI rows (Q7a-o search filters; A-family per-actor-type registration; E-family per-cadence-option × principal/lobbyist; B-family exemption side) are auto-keep or get rolled up.
- **Cross-rubric naming canonicalization is its own subtask.** ~3+ observables have multiple row_ids across docs (total_compensation observable is the load-bearing example). Pre-row-freeze, a `disclosure_side_compendium_items_v1_canonical.tsv` pass would consolidate these — could be ~½ session of judgment calls.
- **The RESEARCH_LOG audit caught a real bug** (missing session header for 2026-05-03 pm). Audit-docs skill is doing its job at pre-merge.

#### Decisions

| topic | decision |
|---|---|
| Session scope | Union step + audits only this session; defer row-freeze and 3 successor plan drafts. |
| Sequencing question (plans-before-vs-after row-freeze) | Surfaced as concern; implicitly resolved as plans-AFTER-row-freeze. |
| Union TSV column set | Stayed close to handoff suggestion; added `n_rubrics` + `first_introduced_by` from script's hardcoded rubric order (CPI→PRI→Sunlight→Newmark 2017→Newmark 2005→Opheim→HG→FOCAL). |
| Composite row entries (Opheim, Newmark 2005 cadence aggregates) | Hardcoded expansion in script; no new row_ids created; constituent PRI rows credited with the reading rubric. |
| LobbyView freeze-candidates LV-1..LV-4 | Hardcoded in script with `status=freeze-candidate`. LV-5 omitted per LobbyView mapping doc's "recommended OUT" disposition. |
| OpenSecrets-distinctive 3 candidates | NOT in TSV (not in any mapping doc); separate row-freeze brainstorm input. |
| Missing 2026-05-03 (pm) session header in RESEARCH_LOG | Fixed: `### 2026-05-03 (pm) — Blue Book / COGEL acquisition + cross-rubric descriptive stats`. |
| Provenance-header retrofit (~35 results .md files) | Deferred (low-priority busywork; existing implicit provenance adequate). |
| Embedding `.npy` bloat (~9MB) | **User decision: purge via `git filter-repo` after this checkpoint.** Embeddings approach was an early exploration superseded by the current framing. |
| Cross-rubric naming canonicalization | Deferred to row-freeze brainstorm (or a small pre-row-freeze canonicalization subtask). |
| PAPER_INDEX 17 vs 18 + 16+ branch-added papers | Deferred to a future `auditing-paper-summaries` session before merge. |

#### Mistakes recorded

None significant. One script bug (returned-list vs append-vs-extend) caught on first run and fixed.

#### Results

- [`results/projections/disclosure_side_compendium_items_v1.tsv`](results/projections/disclosure_side_compendium_items_v1.tsv) — union of 8 score-projection mapping doc Summary tables + 4 LobbyView freeze-candidates. 186 rows total.
- [`tools/union_projection_rows.py`](../../../../tools/union_projection_rows.py) — the union script (~360 lines incl. composite-row expansion + cell-type normalization).

#### Next Steps

1. **Purge embedding `.npy` files** from branch history via `git filter-repo` (user-decided this session). Verify cleanly, then force-push.
2. **Row-freeze brainstorm** (next or later session). Inputs: this TSV + cross-rubric naming-canonicalization questions + the 4 LV candidates + 3 OS-distinctive candidates + each mapping doc's Open Issues section. Scope is heavier than the handoff anticipated (74% single-rubric mass to walk).
3. **`auditing-paper-summaries`** pass to confirm the 16+ branch-added papers are in PAPER_INDEX + PAPER_SUMMARIES (separate before-merge audit).
4. **Draft 3 successor plan docs** AFTER row-freeze (OH retrieval, harness brainstorm, Phase C projection TDD) — using the post-freeze canonical row set.

---

### 2026-05-13 (late-late eve) — Phase B CLOSED: LobbyView 2018/2025 (9th + final mapping) + FOCAL-1 resolved

**Convo:** [`convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md`](convos/20260513_lobbyview_phase_b_final_and_focal1_resolution.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (final rubric).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- **FOCAL-1 resolved by user decision 2026-05-13:** pull `revolving_door.1` IN scope; keep `revolving_door.2` OUT. Pushback recommended (4 grounds: observable shape ≠ FOCAL category label, closes load-bearing US LDA tolerance, trivial compendium cost, symmetric with rows already in scope). User concurred. FOCAL mapping doc updated in 7 in-place edits + Correction 4 added. NEW row introduced: `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal). US LDA tolerance closes from +6pt to 0pt on raw points (≤1pp residual percentage delta from denominator shift only).
- **LobbyView 2018/2025 schema-coverage mapping shipped — 9th + FINAL Phase B mapping.** Different shape from the 8 score-projection mappings: for each of LobbyView's 46 schema fields, classified into one of 5 coverage statuses (COVERED / COVERED-PARTIAL / NOT_COVERED candidate NEW row / OPERATIONAL_METADATA / EXTERNAL_ENRICHMENT). Output: `results/projections/lobbyview_schema_coverage.md` (307 lines).
- **Federal_US LDA disclosure-observable coverage: 14/18 = 78%.** Denominator excludes 25 external enrichments (Congress.gov / CRS / Bioguide / GovTrack / Compustat / Kim 2025 GNN features) and 5 operational-metadata fields. 4 NOT_COVERED items are candidate NEW rows for compendium 2.0 freeze (LV-1 through LV-4); LV-5 (bill_client_link) recommended OUT as operational.
- **Three watchpoints walked:**
  - W1 (`contributions_from_others` final promotion check): NO match in LobbyView. Row is now **single-rubric across the entire 9-rubric contributing set**. Freeze recommendation: KEEP per Newmark-distinctive-observable rationale.
  - W2 (`def_target_*` 4-cell extension): CONFIRMED via LDA §17 + 2 USC §1602(4) "covered legislative branch official" definition. All 4 cells `TRUE` for federal jurisdiction.
  - W3 (FOCAL-1 row validation): CONFIRMED via LDA §18 `covered_official_position`. The just-added `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` row is now **2-rubric-confirmed (FOCAL + LobbyView)** within the same session.

#### Provisional Findings

- **Phase B is COMPLETE.** All 9 mappings shipped: CPI 2015 C11 (21 rows), PRI 2010 (69 rows), Sunlight 2015 (13 rows), Newmark 2017 (14 rows; 6 new), Newmark 2005 (14 rows; 100% reuse), Opheim 1991 (14 rows; 100% reuse), HiredGuns 2007 (38 rows; 22 new), FOCAL 2024 (58 rows post-FOCAL-1; 36 new), LobbyView (schema-coverage). OpenSecrets 2022 structured-tabled with 3 OS-distinctive rows tabled (drop reversible).
- **Compendium 2.0 row inventory standing at ~111 rows post-FOCAL-1.** Post-Phase-B-close: 110 pre-FOCAL-1 + 1 from FOCAL-1 + 0 from LobbyView (LobbyView's candidate NEW rows are freeze-decision-deferred). If LV-1 through LV-4 pulled in at freeze, count grows to ~115.
- **FOCAL-1 resolution was validated by an independent rubric within hours of being made.** LDA §18 `covered_official_position` (LobbyView's most-distinctive lobbying-research-load-bearing federal field; used by Kim 2025's "lobbyist-legislator previously worked together" GNN edges) maps directly onto the FOCAL-1-introduced row. The strict plan reading would have left this row out — that would have been a worse outcome.
- **Row reuse rate distribution is strongly bimodal across the 8 score-projection mappings:** 100%-reuse (Newmark 2005, Opheim 1991; within-tradition battery rubrics confirming row design), 50-80% (CPI broke ground, Sunlight α-split innovator, Newmark 2017 within-tradition + 6 new), <50% (PRI largest; HG 42% finest practical-availability atomization; FOCAL 37.9% per-meeting contact_log + descriptors atomization).
- **`contributions_from_others` row stays single-rubric across the entire 9-rubric contributing set.** All 8 score-projection cross-checks + LobbyView coverage check confirm NO PARALLEL elsewhere. Freeze recommendation: KEEP.

#### Decisions

| topic | decision |
|---|---|
| FOCAL-1 (revolving_door.1 scope) | **RESOLVED — pull in.** NEW row `lobbyist_reg_form_includes_lobbyist_prior_public_offices_held` (binary; legal). revolving_door.2 stays deferred. |
| FOCAL mapping doc updates | 7 in-place edits + Correction 4 added; row count 57 → 58, NEW 35 → 36, reuse rate 38.5% → 37.9%. |
| US LDA Phase C tolerance after FOCAL-1 | Closed (+6pt → 0pt on raw points). |
| LobbyView mapping shape | Schema-coverage check (5-status classification of 46 fields), NOT score-projection. |
| LobbyView Federal_US coverage | 78% (14/18) disclosure observables. 4 candidate NEW rows (LV-1..LV-4); LV-5 recommended OUT. |
| W1: `contributions_from_others` in LobbyView | NO PARALLEL. Row single-rubric across full 9-rubric set. KEEP per Newmark-distinctive rationale. |
| W2: `def_target_*` 4-cell extension validation | CONFIRMED via LDA §17 + 2 USC §1602(4). |
| W3: FOCAL-1 row validation | CONFIRMED. Row is now 2-rubric-confirmed (FOCAL + LobbyView). |
| Phase B status | **COMPLETE** — all 9 mappings shipped. |
| Next | Union step into `disclosure_side_compendium_items_v1.tsv` + compendium 2.0 row-freeze brainstorm (separate plan). |

#### Mistakes recorded

None significant. FOCAL-1 resolution included an honest pushback on the strict plan reading; user concurred. LobbyView mapping followed established workflow conventions cleanly.

#### Results

- [`results/projections/focal_2024_projection_mapping.md`](results/projections/focal_2024_projection_mapping.md) — updated for FOCAL-1 resolution (commit `1ecaf86`).
- [`results/projections/lobbyview_schema_coverage.md`](results/projections/lobbyview_schema_coverage.md) — NEW schema-coverage mapping doc (commit `e5ba35b`); 307 lines; 46 fields × 5 coverage statuses; 3 watchpoints walked; 6 open issues flagged for freeze.

#### Next Steps

1. **Union step (next session)** — collect compendium-row references from all 9 mapping docs, dedupe, save as `results/projections/disclosure_side_compendium_items_v1.tsv`. Expected row count: ~111. Plus pre-merge audits (`audit-docs`, paper-index sanity, `git log --stat` blob check) + draft 3 plan docs for the parallel successor tracks.
2. **Row-freeze brainstorm (next-next session; Option B decided 2026-05-13).** Small standalone session BEFORE merging this branch to main. Resolves freeze decisions on the ~5-10 freeze-candidate rows (LV-1..LV-4, 3 OS-distinctive, FOCAL Open Issues 2-11, HG Open Issues 1-7, Newmark Open Issue 1). Then merge `compendium-source-extracts` → main + cut 3 successor branches in parallel.
3. **Three parallel successor tracks after merge** (post-union-independent):
   - OH statute retrieval pipeline (Track A; adds OH 2007 + OH 2015 to existing OH 2010 + OH 2025 bundles; HG 2007 ground-truth retrieval sub-task)
   - Extraction harness brainstorm (Track B; brainstorm-then-plan; inherits prompt-architecture from archived `statute-extraction` iter-2)
   - Phase C projection TDD — **8 rubrics** not 9 (LobbyView is schema-coverage, not score-projection). Locked order CPI → PRI → Sunlight → Newmark 2017 → Newmark 2005 → Opheim → HG → FOCAL.

**Forward-planning handoff:** [`plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md`](plans/_handoffs/20260513_phase_b_close_and_post_b_plan.md) — self-contained brief for the next-session agent. Captures Phase B closure, Option B decision, next-session scope, per-track plan-scaffolding notes, 9 standing watchpoints. Supersedes the now-stale 2026-05-11 handoff (which covered the now-completed Phase B work).

---

### 2026-05-13 (late eve) — Phase B continued: FOCAL 2024 projection mapping (8th rubric)

**Convo:** [`convos/20260513_focal_phase_b_mapping.md`](convos/20260513_focal_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (FOCAL 2024 — 8th rubric, immediately after HG shipped earlier this evening; LobbyView is the final remaining mapping).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 48 in-scope FOCAL atomic items mapped per the locked Phase B per-item template: 4 scope + 3 timeliness (2025 merges .1+.2) + 9 openness + 6 descriptors + 4 relationships (+ 1 2025-only Lobbyist-list documented) + 11 financials + 11 contact_log. 2 `revolving_door.*` items DEFERRED per strict plan reading (revolving_door.1 flagged as Open Issue FOCAL-1 for compendium 2.0 freeze reconsideration; revolving_door.2 is enforcement-adjacent).
- Cross-rubric grep BEFORE drafting per the locked 2026-05-11 workflow. Three parallel greps: FOCAL refs across 7 existing mapping docs; contact_log + descriptors + relationships concepts in PRI/HG; financials concepts across all mapping docs. Surfaced ~22 reusable rows out of 48 in-scope items + 35 NEW rows.
- α form-type split applied to descriptors (5 NEW reg-form-side cells; PRI E2b's spending-report-side cell is the existing α-pair).
- β AND-projection applied to contact_log.10 (`bill_id AND position` β pair from Sunlight #1, reused by Opheim + FOCAL).
- `def_target_*` family EXTENDED to 4 cells (NEW `def_target_legislative_or_executive_staff`) per FOCAL scope.3 partly-tier discrimination.
- Watchpoint walked: **`contributions_from_others` parallel in FOCAL `financials.*` battery** — the 2026-05-11 handoff's strongest remaining promotion candidate for Newmark 2017's row. **NO PARALLEL** across all 11 FOCAL financials items. Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row stays single-rubric across 8 of 9 contributing rubrics. LobbyView is last check.
- Per-meeting contact_log atomization: 9 NEW rows (beneficiary-org, official-name, institution/dept, attendees, date, communication-form, location, materials-shared, topics-discussed). PRI's coarse `_includes_contacts_made` (E1i/E2i) is the only existing parent row. FOCAL-distinctive at this granularity.
- 2024 → 2025 application differences encoded in projection logic: timeliness.1+.2 merged (read same compendium cell); 2025-only Lobbyist-list indicator added (NEW `principal_report_lists_lobbyists_employed` row, parallel to HG Q9 on principal side). Source TSV stays 2024.
- 2 FOCAL-distinctive set-typed cells proposed: `lobbyist_definition_included_actor_types` (9 organizational types, scope.1) + `lobbying_definition_included_activity_types` (8 activity types, scope.4). Atomization to 9+8=17 binary cells flagged as Open Issue FOCAL-2 for compendium 2.0 freeze.
- Scope-qualifier deviation documented in mapping doc: `revolving_door.1` (lobbyist's prior public offices disclosed on reg form) is statutorily disclosure-shaped but deferred per strict plan reading. Known Phase C tolerance: US federal LDA projects to 75/175 = 43% max vs published 81/182 = 45% — 6-point known under-scoring fully attributable to revolving_door.1 deferral.

#### Provisional Findings

- **Row reuse rate by item: 22/57 = 38.5%.** Lowest reuse rate of any Phase B mapping so far. Below HG's ≥70% prediction because FOCAL's per-meeting contact_log atomization (9 NEW rows) and per-lobbyist descriptors atomization (5 NEW rows) introduce row families that no other contributing rubric reads. Reuse breakdown by battery: scope 37.5%, timeliness 50%, openness 50%, descriptors 16.7%, relationships 60%, financials 54.5%, contact_log 25%.
- **35 NEW compendium rows introduced** — surpasses HG's 22 new rows, becoming the largest new-row contribution of any single Phase B mapping. Concentration: 9 contact_log + 5 descriptors + 5 openness + 5 financials + 1 staff target + 1 actor-types set + 1 activity-types set + 1 timeliness ministerial diary + 1 openness ministerial diary + 1 2025-only Lobbyist list + 5 misc.
- **`lobbyist_spending_report_includes_total_compensation` stays at 7-rubric-confirmed** (FOCAL is the 7th reader; most-validated row in compendium). Other promotions: bill_or_action_identifier α-pair to 5-rubric-confirmed; position_on_bill to 3-rubric-confirmed (Sunlight + Opheim + FOCAL via β AND); employment_type (HG Q10) to 2-rubric-confirmed; business_associations_with_officials (HG Q22) to 2-rubric-confirmed; campaign_contributions (HG Q24) to 2-rubric-confirmed.
- **The `contributions_from_others` row is now single-rubric across 8 of 9 contributing rubrics** (Newmark 2017 only). LobbyView is the last remaining promotion check; LDA's LD-203 captures OUTGOING contributions, not third-party-INCOMING-for-lobbying. Likely 1-rubric-confirmed at end of Phase B. **Compendium 2.0 freeze recommendation: KEEP** per Newmark-distinctive-observable rationale (MA principal reports list earmarked dues; some states explicitly require disclosure; observable is real but unusual).
- **FOCAL is the first contributing rubric where projection's max for US federal LDA is structurally < published score** (a 6-point known under-scoring from revolving_door.1 deferral). Other contributing rubrics either had no federal data (Newmark/Opheim — state-only) or aligned naturally with extraction scope.
- **9 NEW contact_log rows + 5 NEW descriptors rows complete the disclosure-side row backbone** for compendium 2.0 freeze. After FOCAL, LobbyView's schema-coverage check will validate the contact_log + descriptors atomization choices (LobbyView fields populate FOCAL contact_log.1/3/9/11 cells; rest will be uniformly NULL for federal jurisdiction).

#### Decisions

| topic | decision |
|---|---|
| Eighth Phase B target | FOCAL 2024, completed (48 atomic items in scope; 2 `revolving_door.*` deferred) |
| Row reuse | 22 of 57 distinct rows = 38.5% (lowest single-mapping rate) |
| New rows introduced | 35 distinct new rows (most of any single Phase B mapping) |
| Scope-qualifier — revolving_door deferral | DEFERRED per strict plan reading; revolving_door.1 flagged Open Issue FOCAL-1 |
| Phase C tolerance — known under-scoring | +6 pts on US federal LDA (revolving_door.1 deferral); other tolerances minor |
| Watchpoint — `contributions_from_others` in FOCAL financials.* | NO PARALLEL; row stays single-rubric across 8 of 9 contributing rubrics |
| α form-type split for descriptors | APPLIED (5 NEW reg-form-side cells) |
| `def_target_*` family extension | EXTENDED with `def_target_legislative_or_executive_staff` (4th cell) |
| 2024 → 2025 application differences | Encoded in projection logic; 2025-only Lobbyist-list row added |
| Per-meeting contact_log atomization | 9 NEW rows; FOCAL-distinctive |
| Set-typed cells (scope.1 + scope.4) | Set-typed retained; atomization to 17 binary cells flagged Open Issue FOCAL-2 |
| Phase C utility of FOCAL | Federal LDA per-indicator + 28-country ground truth; US states have NO FOCAL ground truth (state-level cross-rubric validation only) |
| Next target | LobbyView (final Phase B mapping — schema-coverage, different shape) |

#### Mistakes recorded

None significant. Workflow ran cleanly. One reasonable counter-argument flagged: 35 NEW rows may be over-atomizing contact_log + descriptors batteries — but granularity-bias rule supports atomization; LobbyView's schema-coverage will validate by checking which FOCAL-distinctive cells the federal LDA schema populates.

#### Results

- [`results/projections/focal_2024_projection_mapping.md`](results/projections/focal_2024_projection_mapping.md) — FOCAL 2024 projection mapping doc (957 lines; 48 atomic items × 57 distinct compendium row families; 22 reused / 35 new; 38.5% reuse — lowest single-mapping rate; includes 11 Open Issues for compendium 2.0 freeze + 3 Corrections to predecessor mappings + Promotions section + 2025-only Lobbyist-list documentation).

#### Next Steps

1. **LobbyView 2018/2025 schema-coverage check** — final Phase B mapping. Different shape (schema-coverage, not score-projection). 46 schema fields per Kim 2018 + Kim 2025. Target: ~100% federal LDA jurisdiction coverage against the now-rich 110+ compendium row set.
2. **`contributions_from_others` final promotion check** against LobbyView's federal LDA schema. If absent (likely), the row is single-rubric across the entire contributing set; Compendium 2.0 freeze: KEEP per Newmark-distinctive rationale.
3. **After Phase B closes** (FOCAL done; LobbyView next): union of 8 score-projection mapping docs + 1 schema-coverage doc → `results/projections/disclosure_side_compendium_items_v1.tsv`. Compendium 2.0 row-freeze brainstorm (separate plan).
4. **Phase C: code projections under TDD.** Order locked: CPI 2015 C11 first; PRI 2010 second; remaining 7 in mapping order; FOCAL last (after federal-LDA jurisdiction extraction is in place).
5. **Resolve Open Issue FOCAL-1** (revolving_door.1 scope decision) at user review.

---

### 2026-05-13 (eve) — Phase B continued: HiredGuns 2007 projection mapping (7th rubric)

**Convo:** [`convos/20260513_hiredguns_phase_b_mapping.md`](convos/20260513_hiredguns_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (HG 2007 — 7th rubric, the largest of the three rubrics remaining after Opheim shipped earlier on 2026-05-13).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 38 in-scope HG atomic items mapped per the locked Phase B per-item template (2 def + 8 ind-reg + 15 ind-spending + 2 emp-spending + 3 e-filing + 8 pub-access; 9 enforcement + 1 cooling-off OOS).
- Cross-rubric grep BEFORE drafting per locked 2026-05-11 workflow: 4 parallel greps across the 9 contributing-rubric TSVs + historical PRI 2010 disclosure-law CSV, plus targeted greps of CPI and PRI projection mapping docs. Surfaced 16 reusable rows out of 38 items + 22 NEW rows.
- α form-type split applied to Q5 vs Q20 (the canonical motivating case for the split locked 2026-05-11). HG reads both sides distinctly at 3-tier categorical projection on the pre-existing 6 Sunlight α rows.
- 5-tier ordinal magnitude reads on typed cells: HG Q2 (compensation threshold) and HG Q15 (itemization de-minimis threshold) are the FINEST readers of these typed cells in the contributing-rubric set; CPI #197 / Sunlight #3 read at coarser granularity on the same cells.
- Conditional-cascade pattern (Q15 gates Q16-Q19): 4 NEW itemized-detail cells (employer / recipient / date / description); cascade lives in the projection logic, not in the cells.
- Practical-availability granularity battery (Q28-Q38, 11 items) introduces the FINEST atomization of portal observables in the contributing-rubric set. Q31/Q32 access-tier ordinals decompose into 4 binary cells each (photocopies / pdf / searchable / downloadable, lobbyist-directory side and spending-report side). Sunlight item-4's underlying observables (kept in compendium 2.0 even though Sunlight item-4 itself was excluded from projection) get their FIRST projection-friendly reader here.
- Composite quirks: Q23 mixes disclosure (1 pt) + limits (2 pt) + prohibition (3 pt); Q24 has 5 labels / 3 distinct point values (allowed/disclosed/session crosstab). Disclosure-only projection caps at 1 pt of 3 for Q23, 1 pt of 2 for Q24. Maximum systematic under-scoring from disclosure-only scope = 3 pts per state on the 100-point scale.
- Watchpoint walks: (1) `contributions_from_others` parallel in HG — NO PARALLEL (Q24 is OUTGOING campaign contributions disclosure, not third-party-contributions INCOMING — the Newmark 2017 observable; row remains single-rubric across 7 of 9 contributing rubrics now); (2) `def_actor_class_*` 4th-reader check — HG is NOT a 4th reader (HG Q1/Q2/Q3/Q4 read target/threshold/gateway/deadline, not actor-class definitional inclusion; row family stays 3-rubric-confirmed).
- Discovered: the locked plan and 2026-05-11 handoff both reference HG as a 47-item rubric with "Q1-Q38 + Q49-Q56 in scope." Both numbers are incorrect — `items_HiredGuns.tsv` has 48 items (Q1-Q48), no Q49+. Disclosure-side in scope = Q1-Q38 = 38 items, not 47. Documented as Correction 1 in mapping doc.
- 7 row-design questions (HG-1 through HG-7) + 3 systemic issues (Q23/Q24 partial-scope tolerance; practical-availability cell Phase C strategy; convergence-of-atomization observation) flagged as Open Issues for compendium 2.0 freeze planning.

#### Provisional Findings

- **Row reuse rate by item: 16/38 = 42%.** Lowest reuse rate of any Phase B mapping so far. Expected: HG is the largest remaining rubric AND atomizes practical-availability finer than any contributing rubric. The reuse pattern is **HG-introduces-the-fine-cells; other rubrics read at coarser granularities** — the inverse of the Newmark/Opheim 100%-reuse pattern.
- **22 NEW compendium rows introduced** — the most of any single mapping. 14 new legal-axis rows + 8 new practical-axis rows (Q31/Q32 access-tier underlying cells) + supplementary practical cells (Q28-Q38). HG is the LAST significant batch of new disclosure-side observables; FOCAL (next) is expected to be ≥70% reuse.
- **`lobbyist_spending_report_includes_total_compensation` is now the most-validated row in the compendium: 7-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q13 + CPI #201 + PRI E2f_i). Other promotions to 5+ rubric-confirmed: `lobbyist_spending_report_categorizes_expenses_by_type` (6), `lobbyist_spending_report_includes_itemized_expenses` (6), `compensation_threshold_for_lobbyist_registration` at multiple granularities (5), gifts/entertainment/transport/lodging bundle (5+).
- **Q12 (filings per 2-year cycle) requires a NEW metadata cell** to make the projection deterministic from cadence binaries alone — `state_legislative_session_calendar` (structured) OR `lobbyist_spending_reports_implied_per_2yr_cycle: int` (direct derived). Latter is YAGNI-cleaner; defer to compendium 2.0 freeze.
- **Q23/Q24 disclosure-only projection caps at partial scope** — Q23 reaches 1 of 3 pts; Q24 reaches 1 of 2 pts. Maximum systematic under-scoring vs published HG totals = 3 pts of 100. Documented as Phase C validation tolerance issue, not a Phase B blocker.
- **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` is now single-rubric across 7 of 9 contributing rubrics.** Remaining promotion checks: FOCAL `financials.*` battery and LobbyView. If both fail, the row is single-rubric across the entire contributing set — that becomes a compendium 2.0 freeze question (real Newmark-distinctive observable, or over-atomization?).

#### Decisions

| topic | decision |
|---|---|
| Seventh Phase B target | HiredGuns 2007, completed (38 atomic items in scope; 10 OOS = 9 enforce.* + 1 cooling-off) |
| Row reuse | 16 of 38 = 42% (lowest Phase B mapping so far) |
| New rows introduced | 22 distinct new rows (14 legal-axis + 8 practical-axis Q31/Q32 family) |
| α form-type split on Q5/Q20 | APPLIED — canonical motivating case |
| 5-tier reads on Q2 / Q15 typed cells | APPLIED — finest granularity in contributing set |
| Q16-Q19 itemized-detail cascade | 4 NEW cells; conditional-on-Q15 logic in projection |
| Q31/Q32 cell decomposition | 4 binary cells per side × 2 form types = 8 NEW practical cells; granularity bias over single typed-enum |
| Watchpoint — `contributions_from_others` | NO PARALLEL in HG; single-rubric across 7 of 9 |
| Watchpoint — `def_actor_class_*` 4th reader | NOT a 4th reader; stays 3-rubric-confirmed |
| HG item-count correction | Plan/handoff said 47; TSV has 48 (Q1-Q48); 38 in scope (not 47) |
| Q23/Q24 partial-scope projection | DOCUMENTED as Phase C tolerance issue (3 pts max under-scoring per state) |
| Q12 session-calendar question | Flagged Open Issue HG-5 for compendium 2.0 freeze |
| Phase C utility of HG | Per-state per-question scorecard retrieval is the unlock (1,900 cells potential); statute-extraction populates ~22 legal cells, portal observation populates ~13 practical cells (Phase D dependency) |
| Next target | FOCAL 2024 (50 indicators; weighted aggregation; 1,372-cell L-N 2025 ground truth) |

#### Mistakes recorded

None significant. Cross-rubric grep workflow ran cleanly with 4 parallel greps; no rework cycles. One minor friction: HG's TSV has 48 items but plan/handoff said 47 — caught early during reading, documented as a correction; not a workflow mistake (source-of-truth discrepancy was in predecessor docs).

#### Results

- [`results/projections/hiredguns_2007_projection_mapping.md`](results/projections/hiredguns_2007_projection_mapping.md) — HG 2007 projection mapping doc (38 atomic items × ~38 distinct compendium row families; 16 reused / 22 new; longest mapping doc in the contributing set after PRI; includes "Corrections to predecessor mappings" section flagging the 48-not-47 item-count correction + non-`def_actor_class_*`-reader confirmation + Phase B mapping count update 6 → 7).

#### Next Steps

1. **FOCAL 2024 projection mapping** — 8th of 9 score-projection rubrics (LobbyView 9th, different shape). 50 indicators with weighted aggregation. Per L-N 2025 supplementary file: max 182 pts; US federal LDA scored 81/182 = 45% (project's primary validation anchor for federal jurisdiction). FOCAL `financials.*` battery is the strongest remaining check for the `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row.
2. After Phase B completes (FOCAL + LobbyView): union of all 9 score-projection mapping docs + 1 schema-coverage doc → `results/projections/disclosure_side_compendium_items_v1.tsv`; compendium 2.0 row-freeze brainstorm (separate plan).
3. Phase C: code projections under TDD per locked plan §Phase C. Order locked: CPI 2015 C11 first; PRI 2010 second; remaining 7 in mapping order.
4. **7 row-design Open Issues from HG (HG-1 through HG-7)** + 3 systemic issues all flagged for compendium 2.0 freeze planning; non-blocking for remaining 2 Phase B mappings.

---

### 2026-05-13 (pm late) — Phase B continued: Opheim 1991 projection mapping (6th rubric)

**Convo:** [`convos/20260513_opheim_phase_b_mapping.md`](convos/20260513_opheim_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (Opheim 1991 — 6th rubric, the explicit predecessor to Newmark 2005 which shipped earlier this afternoon).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 15 in-scope Opheim atomic items mapped: 7 def + 1 freq + 6 information-category (+ 1 catch-all un-projectable, treated as `unable_to_evaluate`). All 7 `enforce.*` items excluded per disclosure-only Phase B qualifier.
- Four watchpoints from the handoff walked: (1) β AND-projection on `disclosure.legislation_supported_or_opposed` — APPLIED, reads `bill_id AND position` from compendium (both pre-existing from Sunlight's α form-type split); this is the second concrete application of β after the 2026-05-11 Sunlight locking; (2) `def_actor_class_*` row family 3-rubric-confirmed — RESOLVED, Open Issue 1 pulled forward to compendium 2.0 freeze per handoff guidance; (3) `disclosure.frequency` finer-cut cadence projection — CONFIRMED, reads only PRI monthly cells (2 of the 8-cell family) vs Newmark 2005's >annual cut; (4) `contributions_from_others` parallel — NO PARALLEL in Opheim's 7-item info-category battery.
- The catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` item handling. Per `items_Opheim.md` §7 "the single most under-defined item in the index" — operationally undefined in the paper. First contributing-rubric item with `unable_to_evaluate` projection. Excluded from projected partial (not zeroed; not coerced to a closest-adjacent row). Phase C harness needs to support this outcome.
- Cross-rubric grep across all 10 contributing-rubric files BEFORE drafting per the locked 2026-05-11 workflow. Confirmed bill_id and position rows already in compendium from Sunlight α split; confirmed no `contributions_from_others` parallel; confirmed the cadence row family is the right target for the frequency projection.
- Structural delta from Newmark 2005 enumerated: Opheim has 7 enforcement items (all OOS) vs Newmark 2005's 4 prohibitions (also OOS); Opheim has the catch-all that Newmark 2005 drops; Opheim splits `legislation_supported_or_opposed` (β AND-projection on bill_id + position) where Newmark 2005 reads only the coarser subject-matter row.
- Three row-family promotions identified for compendium 2.0 freeze: (a) `def_actor_class_*` 3-rubric-confirmed → Open Issue 1 resolved-in-principle; (b) three lobbyist-status threshold cells 3-rubric-confirmed; (c) gifts/entertainment/transport/lodging bundle 4-rubric-confirmed at combined granularity.

#### Provisional Findings

- **Row reuse rate: 14/14 distinct row families = 100%.** Zero new compendium rows introduced. Same headline as Newmark 2005, consistent with Opheim being the explicit predecessor. Breakdown: 4 from CPI mapping, 4 from Sunlight mapping (including the bill_id/position pair from α split), 2 from PRI gifts-pair, 2 cells from the PRI cadence family (monthly only), 3 from Newmark 2017 mapping.
- **One item un-projectable.** Opheim's catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` has no operational definition in the paper. First contributing-rubric item with `unable_to_evaluate` projection. Phase C harness must support this outcome.
- **β AND-projection now established convention.** Second concrete application after the 2026-05-11 Sunlight session. Pattern: when source bundles N conceptually-distinct observables into one item, encode the bundling in projection logic (AND/OR/derived expression) rather than re-atomizing the source. Source TSV stays unedited.
- **Three row-family promotions for compendium 2.0 freeze.** `def_actor_class_*` 3-rubric-confirmed (Open Issue 1 resolved-in-principle); three lobbyist-status threshold cells 3-rubric-confirmed; gifts bundle 4-rubric-confirmed at combined granularity. **`lobbyist_spending_report_includes_total_compensation` is now the most-validated row** in the compendium going into HG: 6+ readers (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q13 + CPI #201 + PRI E2f_i).
- **`lobbyist_or_principal_report_includes_contributions_received_for_lobbying` stays single-rubric** after Opheim. Single-rubric across 6 of 9 contributing rubrics now (CPI, PRI, Sunlight, Newmark 2005, Newmark 2017, Opheim). Remaining promotion checks: HG, FOCAL, LobbyView. If all three fail, the row is single-rubric across the entire contributing set — compendium 2.0 freeze question, not a Phase B blocker.
- **Opheim's Phase C utility is temporal-depth validation.** 1988-89 vintage extends contributing-rubric coverage to ~28 years (1988-89 through 2015). Direct tolerance validation against Opheim's published totals reduces to a weak inequality (max projected partial = 14/22; 7 enforce + 1 catch-all OOS). Actual quality signal is cross-vintage stability check on BoS-derived rows that several rubrics read across multiple vintages.

#### Decisions

| topic | decision |
|---|---|
| Sixth Phase B target | Opheim 1991, completed (15 atomic items in scope; 7 OOS enforce.*; 14 of 15 projectable) |
| Row reuse | 14 of 14 row families = 100% (zero new rows) |
| Watchpoint 1 (β AND-projection on `legislation_supported_or_opposed`) | APPLIED — 2nd confirmed use of β |
| Watchpoint 2 (`def_actor_class_*` 3rd reader) | CONFIRMED — Open Issue 1 resolved-in-principle |
| Watchpoint 3 (`disclosure.frequency` finer cadence cut) | CONFIRMED — reads only PRI monthly cells; tri-annual → 0 |
| Watchpoint 4 (`contributions_from_others` parallel) | NO PARALLEL — Newmark 2017 row stays single-rubric in current set |
| Catch-all `disclosure.other_influence_peddling_or_conflict_of_interest` | UN-PROJECTABLE; `unable_to_evaluate`; excluded from partial |
| Three row-family promotions for compendium 2.0 freeze | `def_actor_class_*` + three threshold cells + gifts bundle |
| Phase C utility of Opheim | Temporal-depth validation; weak inequality only; cross-vintage stability check the actual quality signal |
| Next target | HiredGuns 2007 (47 items, disclosure-side only; largest single remaining mapping) |

#### Mistakes recorded

None significant. Followed locked conventions throughout (cross-rubric grep before drafting; α form-type split via existing Sunlight rows; β AND-projection on bundled item; `unable_to_evaluate` for un-projectable catch-all).

#### Results

- [`results/projections/opheim_1991_projection_mapping.md`](results/projections/opheim_1991_projection_mapping.md) — Opheim 1991 projection mapping doc (15 atomic items × 14 distinct compendium row families; 100% reuse; 1 item un-projectable; includes "Corrections to predecessor mappings" section flagging Open Issue 1 resolution + handoff remaining-rubric count decrement 4 → 3).

#### Next Steps

1. **HiredGuns 2007 projection mapping** — last 3 disclosure-focused rubrics: HG → FOCAL → LobbyView (schema-coverage, different shape, last). HG is the largest single remaining mapping (47 items in scope per the handoff).
2. After Phase B completes: union of mapping docs → `results/projections/disclosure_side_compendium_items_v1.tsv`; compendium 2.0 row-freeze brainstorm.
3. Open Issue 1 (`def_actor_class_*`) is now resolved-in-principle for compendium 2.0 freeze. Three additional row-family promotions noted above also feed into freeze planning.
4. Phase B is 67% complete (6 of 9 mappings done, OS tabled). A parallel compendium-2.0 row-freeze brainstorm could reasonably start scoping in parallel to HG/FOCAL/LobbyView.

---

### 2026-05-13 (pm) — Phase B continued: Newmark 2005 projection mapping (5th rubric)

**Convo:** [`convos/20260513_newmark_2005_phase_b_mapping.md`](convos/20260513_newmark_2005_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (Newmark 2005 — 5th rubric, predecessor to Newmark 2017 which shipped earlier today).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 14 in-scope Newmark 2005 atomic items mapped: 7 def + 1 freq + 6 disclosure. 4 `prohib.*` + 1 `penalty_stringency_2003` excluded per disclosure-only Phase B qualifier.
- Three watchpoints from the handoff walked: (1) PRI A-family overlap check on `def_actor_class_*` — resolved as NO OVERLAP (institutional-actor vs individual-actor-class are distinct observables); (2) three-threshold-cell verification against 2005 paper text — CONFIRMED, lines 120–121 enumerate compensation + expenditure + time as three separate definitional components; (3) `penalty_stringency_2003` exclusion — DOCUMENTED in the mapping doc's scope-qualifier table.
- 6-vs-7 disclosure-item delta between Newmark 2005 and Newmark 2017 surfaced. 2005 doesn't have `disc.contributions_from_others`; 2005 does have a standalone `freq_reporting_more_than_annual` item that 2017 omits (projects from existing PRI E1h/E2h cadence row family via 8-cell OR-projection, no new rows).
- Cross-rubric grep across PRI 2010 items + historical PRI 2010 disclosure-law CSV for actor-class overlap. PRI A1–A11 are structural/institutional-actor (legislative branch as institution lobbying, governor's office as institution lobbying, etc.); Newmark's `def_actor_class_*` is individual-actor (does a state senator personally lobbying fall under the lobbyist definition). Distinct row families; both already in the compendium plan.
- Per-state per-indicator data inventory for Newmark 2005. Paper Table 1 publishes per-state main-index totals across 6 panels (1990–91 through 2003); sub-aggregate breakdowns NOT published — weaker than Newmark 2017's Table 2 sub-aggregate publication.
- Mid-session user reframe: PRI institutional-actor tracking is itself valuable for the SMR regardless of overlap with `def_actor_class_*`. Confirmed already operationalized via the PRI projection mapping's 11 `actor_*` rows.

#### Provisional Findings

- **Row reuse rate: 14/14 = 100%.** Zero new compendium rows introduced; exceeds the handoff's ≥90% expectation. Breakdown: 4 from CPI mapping, 4 from Sunlight mapping, 2 from PRI gifts-pair, 1 PRI cadence family (8 cells under it), 4 from Newmark 2017 mapping.
- **Newmark 2017 mapping's `disc.contributions_from_others` parallel speculation falsified.** Newmark 2005 has only 6 disclosure items. `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` stays Newmark-2017-distinctive. Pending: HG, FOCAL, LobbyView (OS tabled).
- **Newmark 2005 Phase C utility is structurally weaker than Newmark 2017's.** Paper publishes per-state totals only. With disclosure-only scope, direct validation reduces to a weak inequality (`projected_partial ≤ paper_total`). Actual quality signal is **temporal-coverage validation** across 6 panels — only multi-vintage ground truth in the current set.
- **The `def_actor_class_*` row family is now 3-rubric-load-bearing if Opheim confirms** (Newmark 2017 + Newmark 2005 + Opheim 1991, the next mapping). Open Issue 1 from the Newmark 2017 mapping should be pulled forward to compendium 2.0 freeze rather than indefinitely deferred.

#### Decisions

| topic | decision |
|---|---|
| Fifth Phase B target | Newmark 2005, completed (14 atomic items in scope; 5 OOS) |
| Row reuse | 14 of 14 = 100% (zero new rows) |
| Watchpoint 1 (PRI A-family) | NO OVERLAP; both row families valid and distinct |
| Watchpoint 2 (three thresholds) | CONFIRMED in 2005 paper lines 120–121 |
| Watchpoint 3 (penalty_stringency_2003) | EXCLUDED |
| `freq_reporting_more_than_annual` projection | OR over 8 PRI cadence cells |
| Newmark 2017 speculation on 2005 contributions parallel | FALSIFIED |
| Open Issue 1 status | Increasingly load-bearing — pull forward to compendium 2.0 freeze planning |
| PRI A-family value (user note) | CONFIRMED — institutional-actor tracking belongs in the compendium; already done via PRI mapping |
| Next target | Opheim 1991 (last 4 disclosure-focused rubrics: Opheim → HG → FOCAL → LobbyView) |

#### Mistakes recorded

- Initially named the convo file with the `_projection_mapping` suffix in the mapping doc's link reference before the docs checkpoint surfaced the established `_phase_b_mapping` convention from prior sessions. Caught at update-docs time and corrected.

#### Results

- [`results/projections/newmark_2005_projection_mapping.md`](results/projections/newmark_2005_projection_mapping.md) — Newmark 2005 projection mapping doc (14 atomic items × 14 distinct compendium row families; 100% reuse; corrections to predecessor mappings noted).

#### Next Steps

1. **Opheim 1991 projection mapping** — last 4 disclosure-focused rubrics: Opheim → HG 2007 → FOCAL 2024 → LobbyView (schema-coverage, different shape, tackled last). Opheim is structurally adjacent to Newmark 2005 (Newmark explicitly invokes Opheim as the basis) so significant overlap expected.
2. After Phase B completes: union of mapping docs → `results/projections/disclosure_side_compendium_items_v1.tsv`; compendium 2.0 row-freeze brainstorm.
3. Open Issue 1 (`def_actor_class_*` row family) resolution should be pulled forward to compendium 2.0 freeze planning.

---

### 2026-05-13 — Phase B continued: Newmark 2017 projection mapping (4th rubric)

**Convo:** [`convos/20260513_newmark_2017_phase_b_mapping.md`](convos/20260513_newmark_2017_phase_b_mapping.md)
**Plan executed:** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (Newmark 2017 — 4th rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015; OpenSecrets 2022 was tabled earlier on 2026-05-13).
**Handoff (most recent, with this rubric's watchpoints):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- All 14 in-scope Newmark 2017 atomic items mapped per the locked Phase B per-item template (7 def + 7 disclosure; 5 `prohib.*` items explicitly excluded per the disclosure-only Phase B qualifier).
- Cross-rubric grep run BEFORE drafting per the locked 2026-05-11 workflow: 8 parallel greps across the 10 contributing-rubric files + historical PRI 2010 disclosure-law CSV + 3 existing projection mapping docs. Surfaced 8 reusable rows (5 from CPI, 2 from PRI, 1 from Sunlight at row-level; 4 additional pre-existing rows touched at compound granularity).
- Three threshold-concept discipline applied: Newmark's three def.*_standard items (compensation/expenditure/time) → three separate typed cells with `IS NOT NULL` projection (not a single binary row each).
- `disclosure.expenditures_benefiting_officials` row-design question (handoff watchpoint) resolved: keep existing PRI bundle (gifts ∪ entertainment ∪ transport ∪ lodging × lobbyist/principal), projected as OR over actor sides. HG Q23 gifts-specific granularity flagged for compendium 2.0 freeze, not split now.
- New `def_actor_class_*` row family proposed (Newmark/Opheim treat "elected officials as lobbyists" / "public employees as lobbyists" as definitional inclusion criteria; distinct from CPI's `def_target_*` family and PRI's `actor_*` family).
- Honest Phase C validation scope documented: Newmark 2017 publishes only sub-aggregate per-state data (Table 2). Direct Newmark validation is 50 states × 2 sub-aggregates = 100 ground-truth cells. Per-item validation requires cross-rubric overlap with PRI 2010 + CPI 2015 C11.

#### Provisional Findings

- **Reuse rate 8 of 14 = 57%.** Cumulative across 4 mappings, compendium-row growth is slowing as predicted — Newmark 2017's role is cross-rubric redundancy on the BoS-derived definitional-and-disclosure backbone, not novel observables (same role Sunlight plays).
- **Single Newmark-distinctive observable:** `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`. No other rubric in the current contributing set reads it directly; Newmark 2005's parallel item (next-up mapping) likely picks it up.
- **The `def_actor_class_*` row family is a genuinely new third family** alongside `def_target_*` (CPI) and `actor_*` (PRI). Conceptually distinct but fragile — could be folded into one of the other two at compendium 2.0 freeze if PRI A-family overlap is established.
- **Two no-variation items in Newmark 2017** (`def.legislative_lobbying`, `disclosure.expenditures_benefiting_officials`) — extracted normally; Phase C accounts for constant +2 contribution to the sub-aggregate ground truth.

#### Decisions

| topic | decision |
|---|---|
| Fourth Phase B target | Newmark 2017, completed (14 atomic items in scope) |
| Row reuse | 8 of 14 = 57% |
| New row family `def_actor_class_*` | PROPOSED for elected-officials and public-employees as lobbyists; Open Issue 1 at compendium 2.0 freeze |
| `expenditure_threshold_for_lobbyist_registration` typed cell | PROPOSED (parallel to CPI #197's compensation cell) |
| `time_threshold_for_lobbyist_registration` typed cell | PROPOSED with structured value type (magnitude + unit enum; accommodates federal LDA's 20%-of-work-time) |
| `lobbyist_spending_report_includes_total_expenditures` (binary) | PROPOSED as separate from `_required` per granularity bias |
| `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` (binary) | PROPOSED. Newmark-distinctive |
| `disclosure.expenditures_benefiting_officials` row design | RESOLVED: keep existing PRI bundle; HG Q23 gifts split deferred |
| Pushback on handoff watchpoint #4 | Three def.*_standard items read THREE typed cells, not one. Handoff wording was shorthand for "follow the CPI #197 typed-cell pattern" |
| Phase C validation scope for Newmark | Sub-aggregate-only against Newmark's published data (100 cells); per-item via cross-rubric overlap |
| Next target | Newmark 2005 (predecessor; 18 items; expect heavy overlap) |

#### Mistakes recorded

None significant. Cross-rubric grep workflow (locked 2026-05-11) ran cleanly on first attempt; no rework cycles. One minor friction: PRI mapping doc exceeded the 25k-token Read limit; switched to grep-based interrogation of existing rows — predictable consequence of PRI being the largest mapping, independent of process discipline.

#### Results

- [`results/projections/newmark_2017_projection_mapping.md`](results/projections/newmark_2017_projection_mapping.md) — Newmark 2017 projection mapping doc (14 atomic items × 14 distinct compendium rows; 6 new, 8 reused; all rows annotated with `[cross-rubric: …]`).

#### Next Steps

1. **Newmark 2005 projection mapping** (18 items; predecessor; very heavy overlap expected with Newmark 2017's row set).
2. Continue Phase B for remaining 4 rubrics: Opheim 1991, HiredGuns 2007, FOCAL 2024, LobbyView (schema-coverage, tackled last).
3. After Phase B completes: union of all 9 score-projection mapping docs' `compendium_rows` → `results/projections/disclosure_side_compendium_items_v1.tsv`; compendium 2.0 row-freeze brainstorm (separate plan; resolves the 4 Open Issues from this session + open issues from prior mappings).
4. Open Issue 4 (handoff threshold pushback — three typed cells vs one) needs design-team disposition at the next session start.

---

### 2026-05-12 → 2026-05-13 — Phase B continued: OpenSecrets 2022 attempt → tabled

**Convo:** [`convos/20260512_opensecrets_phase_b_tabled.md`](convos/20260512_opensecrets_phase_b_tabled.md)
**Plan executed (partially):** [`plans/20260507_atomic_items_and_projections.md`](plans/20260507_atomic_items_and_projections.md) Phase B (was 4th rubric per locked order; ended tabled).
**Handoff that pointed here (now updated):** [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md)

#### Topics Explored

- Cross-rubric grep across 9 rubric TSVs + historical PRI 2010 disclosure-law CSV for OpenSecrets's 4-category concepts. Heavy overlap with existing compendium rows confirmed for Cats 2 (compensation) and 4 (portal); Cat 3 cadence covered by Opheim's in-session/out-of-session split.
- Per-category projection logic drafted to completion before user check-in surfaced the structural problem.
- User-driven critical re-read of OpenSecrets's published rubric: only 2-3 anchors per category (Cat 1: 3, 4; Cat 2: 0, 4, 5-undefined; Cat 3: 4, 5; Cat 4: sub-facet weights only). No per-tier definitions for scores 0–3; no inter-coder reliability; no per-state per-category numerical data in accessible form (behind JS-rendered state-map widget).
- Re-anchoring against branch success criterion (STATUS.md ⭐ block): projection-vs-published-data validation requires reproducibility from cells. OpenSecrets fails. The original 2026-05-07 Phase A1 DROP verdict was structurally correct; the recheck's "few-shot calibratable" criterion was softer than the branch's bar.

#### Provisional Findings

- **OpenSecrets 2022 cannot serve as a Phase C projection-validation target under the branch's stated success criterion.** Empirically confirmed by mapping attempt: Cat 1 projects to {3, 4} only from cells; Cats 2/3 partial-credit (scores 1-3) requires calibration-by-distribution rather than deterministic projection.
- **The original Phase A1 DROP verdict was structurally correct.** The recheck overturn applied a weaker criterion than what the branch actually requires.
- **3 OS-distinctive row candidates were surfaced:** `separate_registrations_for_lobbyists_and_clients` (Cat 1 bonus), `lobbyist_compensation_disclosed_as_exact_amount_vs_ranges` (Cat 2 partial-credit), `lobbyist_compensation_disclosed_per_individual_lobbyist_vs_aggregate` (Cat 2 partial-credit). Real statutory observables; tabled alongside the rubric pending organic pickup or project-internal justification.
- **Cadence in-session/out-of-session split is NOT OS-distinctive** — Opheim 1991 reads the same split. Opheim's mapping will introduce the row family. CPI Open Issue 4 (cadence representation) remains open.
- **Cat 4 portal sub-facets fold into existing CPI/FOCAL/HG rows.** No new compendium rows needed for those; OS's contribution was only finer-granularity ordinal on the same cells.

#### Decisions

| topic | decision |
|---|---|
| OpenSecrets 2022 status | **TABLED 2026-05-13** (not permanently dropped). Reason: no published per-tier scoring definition; few-shot calibration doesn't meet projection-vs-published-data bar |
| 3 OS-distinctive row candidates | Tabled. Two reinstatement paths: organic pickup by another rubric / project-internal need at compendium 2.0 freeze |
| Phase B remaining order | Renumbered 7 → 6 rubrics. Next = **Newmark 2017** |
| Reinstatement triggers | Documented in `results/_tabled/opensecrets_2022_tabled.md` (per-tier sub-anchor publication / state-map widget JS pull / third-party reverse-engineering / project's framing change) |

#### Mistakes recorded

1. Executed handoff without re-checking branch purpose at session start. Should have read the recheck doc with a critical eye and compared its "few-shot calibratable" criterion against STATUS.md's success criterion before drafting. The recheck explicitly applied a weaker criterion ("operationally too strict" about the original audit's framing) — that mismatch should have been a session-opening flag.
2. Attempted `rm` on the projection-mapping doc instead of `git mv`-with-SUPERSEDED-banner. User pushed back ("are you deleting datafiles?"); the `rm` had been cancelled by parallel-tool rollback so the file was still on disk. Properly moved to `results/_tabled/opensecrets_2022_projection_mapping_superseded.md` with a banner. **Generalize:** prefer move-with-banner over delete for analytical artifacts, even un-committed — lesson is independent of the lucky outcome.
3. "Agent overcorrection in response to prior user pushback" is a real failure mode in research workflows. The recheck doc was an example — keeping OS in on a weaker criterion than the branch's actual bar. Flag this pattern when reading prior session artifacts.

#### Results

- [`results/_tabled/opensecrets_2022_tabled.md`](results/_tabled/opensecrets_2022_tabled.md) — new tabling doc with reasoning, reinstatement triggers, and 3 OS-distinctive row candidates (each with per-row pickup possibilities documented).
- Reversal addendum appended to [`results/20260507_opensecrets_recheck.md`](results/20260507_opensecrets_recheck.md).
- Handoff [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](plans/_handoffs/20260511_phase_b_continued_remaining_7.md) updated: 7 → 6 rubrics; OpenSecrets watchpoint replaced with tabling pointer; Newmark 2017 reordered to next.

#### Next Steps

1. **Newmark 2017 projection mapping** (19 items; mostly binary disclosure.* rows with strong existing-row reuse from CPI/Sunlight; key new row is `disclosure.expenditures_benefitting_officials` for the FOCAL/Newmark cross-rubric stack).
2. Optional: reconstruct the projection-mapping doc as a research artifact (the analytical work is captured in the tabled doc's row-candidates section but per-category projection reasoning is summarized rather than preserved verbatim). Punt-able.
3. Optional: state-map widget JS pull as a reinstatement attempt for OpenSecrets. Punt-able; not on critical path.
4. Compendium 2.0 row freeze (separate post-Phase-B plan) must make an active decision on the 3 OS-distinctive row candidates and on CPI Open Issue 4 (cadence representation).

---

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

### 2026-05-03 (pm) — Blue Book / COGEL acquisition + cross-rubric descriptive stats

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



# 2026-05-13 — Phase B continued: HiredGuns 2007 projection mapping (7th rubric)

**Plan executed:** [`../plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (HG 2007 — 7th rubric to ship, after CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, Opheim 1991; OpenSecrets 2022 was tabled 2026-05-13).
**Handoff that pointed here:** [`../plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../plans/_handoffs/20260511_phase_b_continued_remaining_7.md). HG was the largest-remaining-mapping per the handoff's renumbered Phase B order.
**Result doc:** [`../results/projections/hiredguns_2007_projection_mapping.md`](../results/projections/hiredguns_2007_projection_mapping.md).

## Session shape

Single-task session continuing the locked Phase B order. User opening message specified HG as next-up, with handoff context flagged as "largest remaining mapping at 47 disclosure-side items so the cross-rubric grep step is especially load-bearing." HG was per-spec the canonical case for the locked 2026-05-11 cross-rubric grep workflow.

## Topics Explored

- All 38 in-scope HG atomic items mapped per the locked Phase B per-item template (2 def + 8 ind-reg + 15 ind-spending + 2 emp-spending + 3 e-filing + 8 pub-access; 9 enforcement + 1 cooling-off OOS).
- **Cross-rubric grep BEFORE drafting** per locked 2026-05-11 workflow: ran 4 parallel greps across the 9 contributing-rubric TSVs + historical PRI 2010 disclosure-law CSV, plus targeted greps of the existing CPI and PRI projection mapping docs for row reuse identification. Surfaced 16 reusable rows out of 38 items + 22 NEW rows.
- α form-type split (locked Sunlight 2026-05-11): Q5/Q20 is the canonical motivating case — already in Sunlight mapping; HG reads both sides distinctly at 3-tier categorical projection.
- 5-tier ordinal magnitude reads on typed cells: HG Q2 (compensation threshold), HG Q15 (itemization de-minimis threshold) are the finest readers of these typed cells in the contributing-rubric set; CPI #197 / Sunlight #3 read at coarser granularity on the same cells.
- Conditional-cascade pattern: Q15 gates Q16-Q19 ("If spending is not required to be itemized, a state received no points"). 4 NEW itemized-detail cells (employer / recipient / date / description); cascade lives in the projection logic, not in the cells.
- Practical-availability granularity battery: HG Q28-Q38 (11 items) introduces the FINEST atomization of portal observables in the contributing-rubric set. Q31/Q32 access-tier ordinals decompose into 4 binary cells each (photocopies / pdf / searchable / downloadable, lobbyist-directory side and spending-report side); Sunlight item-4's underlying observables (which were kept in compendium 2.0 even though Sunlight item-4 itself was excluded from projection) get their FIRST projection-friendly reader here.
- Composite quirks: Q24 has 5 labels / 3 distinct point values; Q23 mixes disclosure (1 pt) + limits (2 pt) + prohibition (3 pt) — disclosure-only projection caps at 1 pt of 3 for Q23, 1 pt of 2 for Q24. Maximum systematic under-scoring from disclosure-only scope = 3 pts per state on the 100-point scale.
- Watchpoint 4 (handoff): `contributions_from_others` parallel in HG — WALKED. HG has no item parallel to Newmark 2017's `lobbyist_or_principal_report_includes_contributions_received_for_lobbying`. HG Q24 is the OUTGOING mirror (lobbyist → official campaign contributions), not the third-party-contributions-INCOMING observable Newmark 2017 reads. Row remains single-rubric across 7 of 9 contributing rubrics; FOCAL `financials.*` battery and LobbyView are the last promotion checks.
- Watchpoint on `def_actor_class_*` (handoff): "HG mapping need not re-examine the row family's existence; just check if any HG question reads it (likely Q3 / Q4 area on individual lobbyist definition — could be a 4th reader but immaterial to row design)" — WALKED. HG is NOT a 4th reader. HG Q3 is a registration-gateway question; HG Q4 is the registration deadline; neither reads actor-class definitional inclusion. Row family stays 3-rubric-confirmed (Newmark 2017 + Newmark 2005 + Opheim).
- Discovered: the locked plan and 2026-05-11 handoff both reference HG as a 47-item rubric with "Q1-Q38 + Q49-Q56 in scope." **Both numbers are incorrect** — `items_HiredGuns.tsv` has 48 items (Q1-Q48), with no Q49+. Disclosure-side in scope = Q1-Q38 = 38 items (not 47, not 46). The "Q49-Q56" sub-list is likely a paste-error from another rubric. Documented in Corrections section of mapping doc.
- Row-design questions for compendium 2.0 freeze documented as 7 Open Issues (HG-1 through HG-7) + 3 systemic issues (#8 partial-scope projection tolerance; #9 practical-availability cell Phase C strategy; #10 the contributing-rubric set has converged at HG's atomization granularity).

## Provisional Findings

- **Reuse rate by item: 16/38 = 42%.** Lowest reuse rate of any Phase B mapping so far. Expected: HG is the largest remaining rubric AND atomizes practical-availability finer than any contributing rubric except FOCAL. The reuse pattern is **HG-introduces-the-fine-cells; other rubrics read at coarser granularities.**
- **22 NEW compendium rows introduced** — the most of any single mapping. 14 new legal-axis rows (Q7 amendment deadline; Q8 photograph; Q9 reg-form employer list; Q10 employment type; Q16-Q19 itemized-detail × 4; Q21 household members; Q22 business associations; Q24 outgoing campaign contributions disclosure; Q25 null/no-activity report; plus the Q12 session-calendar metadata cell). 8 new practical-axis underlying-cell families from Q31/Q32 (photocopies/pdf/searchable/downloadable × 2 form types) + 5 other practical cells (Q28/Q29/Q30/Q33/Q34/Q35/Q36/Q37/Q38).
- **`lobbyist_spending_report_includes_total_compensation` is now the most-validated row in the compendium: 7-rubric-confirmed** (Sunlight + Newmark 2017 + Newmark 2005 + Opheim + HG Q13 + CPI #201 + PRI E2f_i). Other promotions to 5+ rubric-confirmed: `lobbyist_spending_report_categorizes_expenses_by_type` (6), `lobbyist_spending_report_includes_itemized_expenses` (6), `compensation_threshold_for_lobbyist_registration` at multiple granularities (5), gifts/entertainment/transport/lodging bundle (5+).
- **Q12 (filings per 2-year cycle) requires a NEW metadata cell** to make the projection deterministic from cadence binaries alone. Either `state_legislative_session_calendar` (structured value: `{session_length_months, sessions_per_two_years, in_session_cadence, out_of_session_cadence}`) OR `lobbyist_spending_reports_implied_per_2yr_cycle: int` (direct derived-by-extraction cell). Latter is YAGNI-cleaner; defer to compendium 2.0 freeze.
- **Q23/Q24 disclosure-only projection caps at partial scope** — Q23 reaches 1 of 3 pts; Q24 reaches 1 of 2 pts. Maximum systematic under-scoring vs published HG totals = 3 pts of 100. Documented as Phase C validation tolerance issue, not a Phase B blocker.
- **`def_target_executive_agency` may need a split for the HG legislative-action-only carve-out** (Open Issue HG-1). HG awards 0 if a state recognizes executive-branch lobbying only when it directly relates to legislative action; CPI #196's row design does not preserve this distinction. Not load-bearing for current Phase C but flagged.
- **The contributing-rubric set has converged at HG's atomization granularity for spending-disclosure observables.** FOCAL mapping (next) is expected to be ≥70% reuse rate; LobbyView schema-coverage check is the last mapping (different shape — coverage_check vs score-projection).

## Decisions

| topic | decision |
|---|---|
| Seventh Phase B target | HiredGuns 2007, completed (38 atomic items in scope; 10 OOS = 9 enforce.* + 1 cooling-off) |
| Row reuse rate | 16 of 38 = 42% (lowest Phase B mapping so far — predictable for the largest remaining rubric) |
| New rows introduced | 22 distinct new rows (14 legal-axis + 8 practical-axis families); most of any single mapping |
| Watchpoint — Q5/Q20 α split | APPLIED; pre-existing Sunlight rows reused exactly |
| Watchpoint — Q15 5-tier on typed itemization-de-minimis cell | APPLIED; finer than Sunlight #3's 2-tier read |
| Watchpoint — Q2 5-tier on typed compensation-threshold cell | APPLIED; finer than CPI #197's 3-tier read |
| Watchpoint — Q23/Q24 partial-scope projection | DOCUMENTED as Phase C tolerance issue (3 pts max under-scoring per state) |
| Watchpoint — `contributions_from_others` parallel in HG | NO PARALLEL — Newmark 2017 row stays single-rubric across 7 of 9 contributing rubrics; FOCAL + LobbyView are the last checks |
| Watchpoint — `def_actor_class_*` 4th reader check | NOT a 4th reader — HG Q1/Q2/Q3/Q4 read target/threshold/gateway/deadline, not actor-class definitional inclusion |
| HG item-count correction | Plan + handoff said 47 items / Q1-Q38 + Q49-Q56 — both incorrect; HG has 48 items (Q1-Q48), 38 in scope per disclosure-only qualifier |
| Q31/Q32 cell decomposition | 4 binary cells per access tier × 2 form types = 8 NEW practical cells; granularity bias preferred over single typed-enum cell |
| Q12 session-calendar question | Flagged as Open Issue HG-5; defer between metadata-cell approach vs derived-int-cell approach to compendium 2.0 freeze |
| Q16-Q19 itemized-detail conditional cascade | 4 NEW binary cells; conditional-on-Q15 logic in projection, not cell |
| Phase C validation tolerance | Document 3-pt-per-state max under-scoring from disclosure-only Q23+Q24 partial scope; document practical-availability cells (Q28-Q38) as Phase D extraction targets |
| Next target | FOCAL 2024 (50 indicators; weighted aggregation; 1,372-cell per-country ground truth from L-N 2025) |

## Mistakes recorded

None significant. The cross-rubric grep workflow (locked 2026-05-11) ran cleanly with 4 parallel greps surfacing all the reusable rows; no rework cycles or row-design corrections after the grep.

One minor friction: HG's TSV has 48 items but the plan/handoff said 47. Caught the inconsistency early during reading; documented as Correction 1 in the mapping doc. Not a workflow mistake — the source-of-truth discrepancy was in the predecessor docs.

## Results

- [`../results/projections/hiredguns_2007_projection_mapping.md`](../results/projections/hiredguns_2007_projection_mapping.md) — HG 2007 projection mapping doc (38 atomic items in scope × ~38 distinct compendium row families touched; 16 reused / 22 new; longest mapping doc in the contributing set after PRI; includes "Corrections to predecessor mappings" section flagging the 48-not-47 item-count correction + non-`def_actor_class_*`-reader confirmation + Phase B mapping count update 6 → 7).

## Next Steps

1. **FOCAL 2024 projection mapping** — 8th of 9 score-projection rubrics (LobbyView 9th, different shape). 50 indicators with weighted aggregation. Per L-N 2025 supplementary file: max 182 pts; US federal LDA scored 81/182 = 45% (project's primary validation anchor for federal jurisdiction). FOCAL `financials.*` battery is the strongest remaining check for the `lobbyist_or_principal_report_includes_contributions_received_for_lobbying` row (if FOCAL also fails, the row is single-rubric across the entire score-projection contributing set — compendium 2.0 freeze question).
2. After Phase B completes (FOCAL + LobbyView): union of all 9 score-projection mapping docs + 1 schema-coverage doc → `results/projections/disclosure_side_compendium_items_v1.tsv`; compendium 2.0 row-freeze brainstorm (separate plan).
3. Phase C: code projections under TDD per locked plan §Phase C. Order locked: CPI 2015 C11 first (smallest concrete target); PRI 2010 second (stress-tests architecture); remaining 7 in mapping order.
4. **Open Issue carry-forward from HG:** 7 row-design issues (HG-1 through HG-7) and 3 systemic issues (Q23/Q24 partial-scope tolerance; practical-axis cell Phase C strategy; convergence-of-atomization observation). All flagged for compendium 2.0 freeze planning, not blocking the remaining 2 Phase B mappings.

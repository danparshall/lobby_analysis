# CPI 2015 SII C11 (Lobbying Disclosure) vs. the 9-rubric consensus

**Source artifact:** [`papers/CPI_2015__sii_criteria.xlsx`](../../../../papers/CPI_2015__sii_criteria.xlsx) (sheet ` Lobbying Disclosure`), via `PublicI/state-integrity-data` GitHub repo. Companion per-state scores at `papers/CPI_2015__sii_scores.csv`.
**Atomic items extracted:** 14, in [`results/items_CPI_2015_lobbying.tsv`](items_CPI_2015_lobbying.tsv).
**Compared against:** the 24 strict + 21 loose-only consensus clusters from the 2026-05-07 3-way × 3-run run (see [`3way_consensus/report.md`](3way_consensus/report.md)).

---

## ⭐ Success criterion for compendium 2.0 (this is the load-bearing principle)

> **Given a populated compendium for a state, we must be able to use the compendium data to populate every source rubric's per-state score.**

The compendium 2.0 is judged by whether each source rubric is **fully reconstructible** from compendium cells. This is a falsifiable round-trip test:

1. Populate compendium cells for some sample of states (1, 5, eventually 50).
2. Apply each source rubric's projection logic to the cells.
3. Compare the projected per-rubric per-state score to the published rubric's actual score.
4. Match (within rubric-specific tolerance) ⇒ that rubric is covered.
5. **All 9 source rubrics must pass this test.**

This criterion gives compendium 2.0 a clear floor and ceiling:

- **Floor (additive):** every source rubric must be projectable. If any rubric needs a row the compendium doesn't have, that row gets added. New rubrics that pass through this branch later expand the floor as needed.
- **Ceiling (subtractive):** **goal — minimize compendium size while keeping the floor intact.** A row that no rubric's projection logic ever reads is deletable. The minimum compendium is the smallest set of canonical rows where all 9 rubrics still project correctly.

The 24 strict consensus clusters from the 3-way run are **not the compendium 2.0 by themselves** — consensus is a discovery aid, not a sufficiency test. The sufficiency test is projection-round-trip.

**Architectural framing (consistent with the 2026-04-29 reframe):** the compendium is the universe of canonical questions; PRI/Sunlight/FOCAL/CPI/Newmark/Opheim/HiredGuns/OpenSecrets are *projections* from a populated compendium, each with its own scoring layer that takes compendium cells as input. The compendium itself does not score; it provides the cells.

CPI 2015 C11 is the test case for this section. The rest of this doc walks through whether/how CPI 2015's 14 items are projectable from our existing consensus output.

---

## TL;DR

CPI 2015 C11 has two halves with very different relationships to our existing 9-rubric corpus:

1. **The 6 de jure items** (≈ HG 2007 / Newmark / Opheim territory at higher abstraction) **fold cleanly into existing consensus clusters or near-existing ones.** No genuinely new canonical questions.
2. **The 8 de facto items** are CPI's distinctive contribution. **They map onto the `practical_availability` axis of our v1.1 schema, not onto new compendium rows.** They validate the two-axis schema design empirically.

**Net contribution of CPI 2015 C11 to compendium 2.0:** ~0 new canonical-question rows, but a strong validation that practical-availability deserves first-class axis treatment with its own evidence types ("audits actually happen", "penalties actually imposed", "citizens can actually access").

**Projection-test verdict:** CPI 2015 C11 is fully projectable from a populated compendium 2.0, with two caveats:
1. Compendium must capture **cell values, not just row presence** (threshold dollar amounts for IND_197, cadence enumerations for IND_199).
2. Compendium must include the **principal-side spending-report row** (currently a PRI singleton in consensus).

CPI 2015's 14 items are **far smaller and higher-abstraction than HG 2007's 47** — confirming the per-paper-extract framing that CPI 2015 is HG 2007's successor at higher abstraction (consolidating dozens of granular HG questions into a 5-sub-category audit framework with explicit de jure/de facto pairs).

## Structure

CPI 2015 C11 organizes its 14 items into 5 sub-categories:

| sub-cat | de jure | de facto | total | scope |
|---|---:|---:|---:|---|
| 11.1 Definition of a lobbyist | 2 | 0 | 2 | who counts as a lobbyist statutorily |
| 11.2 Registration processes effective | 0 | 4 | 4 | empirical compliance with registration & reporting |
| 11.3 Detailed registration requirements | 3 | 0 | 3 | de jure registration & reporting requirements |
| 11.4 Citizens can access information | 0 | 2 | 2 | empirical accessibility |
| 11.5 Effective monitoring | 1 | 2 | 3 | audit & enforcement (de jure + de facto) |
| **total** | **6** | **8** | **14** | |

(Originally classified 5 de jure / 9 de facto in initial extraction — I count 6 de jure / 8 de facto on close read; #207 is "in law", so 11.5 has 1 de jure + 2 de facto. The TSV has the canonical type-tags.)

The de jure / de facto split is **the structural feature that distinguishes CPI 2015 from every other rubric in our corpus.** None of the other 9 rubrics make this distinction explicit at item level — they ask only about statutory provisions. CPI 2015 layers an empirical-compliance check on top.

## Per-item fold-in against existing consensus clusters

Notation:
- **strict c_NNN** = strict consensus cluster (≥ 8/9) from the 3-way run
- **loose c_NNN** = loose-only cluster (≥ 6/9, not all in strict)
- **NEW** = no clean match to any existing strict or loose cluster
- **practical_availability** = de facto item that maps to a v1.1-schema practical-availability assertion on an existing canonical question

| ID | Item (paraphrase) | Type | Fold-in |
|---|---|---|---|
| IND_196 | Definition recognizes executive-branch lobbyists alongside legislative | de jure | **EXACT match → loose c_006** (HG Q1 + Newmark2005/2017 admin-agency-def + Opheim) |
| IND_197 | Anyone paid is a lobbyist | de jure | Adjacent to strict c_009/c_010/c_011 (compensation/expenditure/time standards). Could fold; could be NEW canonical "$0 floor" question |
| IND_198 | All paid lobbyists actually register | de facto | **practical_availability** of registration-required (no strict cluster covers de jure registration mandate) |
| IND_199 | Required to file annual registration form | de jure | Mostly NEW. Adjacent to but distinct from FOCAL timeliness.* and HG Q12 (cadence of reports, not registration). The *existence* of a registration mandate is implicit in many existing items but never explicitly asked at item level |
| IND_200 | Lobbyists file registration forms within days | de facto | **practical_availability** of registration-timeliness (no strict de jure cluster) |
| IND_201 | Detailed spending reports incl. compensation | de jure | **Partial fold → loose c_001** (total compensation w/ HG Q13 + Sunlight + Newmark + Opheim). Compound item; includes both "spending report required" and "compensation in spending report" |
| IND_202 | Spending reports filed at reasonable frequency | de facto | **practical_availability of strict c_004** (frequency of reporting) |
| IND_203 | Employers/principals must file spending reports | de jure | NEW or partial-merge with PRI E1a-family (principal-side disclosure mandate). PRI's principal-side items are mostly singletons in our consensus output |
| IND_204 | Employers list lobbyist compensation in their reports | de facto | **practical_availability of strict c_024** (Newmark "compensation by employer") and/or strict c_018 (HG Q13 + Sunlight lobbyist comp) |
| IND_205 | Citizens can access docs (online, low cost) | de facto | **practical_availability of loose c_009** (lobbyist register online) and strict c_014 / loose c_002 (downloadable + open) |
| IND_206 | Open data format | de facto | **practical_availability of loose c_002** (FOCAL openness.3 + .4 + OpenSecrets downloads + PRI Q6) |
| IND_207 | In law, audits required | de jure | **Folds into loose c_023** (HG Q40 + Opheim enforce.thoroughness_of_reviews — currently 2-rubric loose pair; CPI #207 would promote it toward strict territory in a re-run) |
| IND_208 | Audits actually conducted | de facto | **practical_availability of loose c_023** (the auditing pair) |
| IND_209 | Penalties imposed when violated | de facto | **practical_availability of HG Q41/Q42** (de jure penalties; HG enforcement battery items currently singletons in consensus) |

## Coverage summary

- **3 de jure items fold cleanly into existing strict clusters (or loose pairs that would tighten with CPI added):** IND_196 → c_006; IND_201 → c_001 loose (partial); IND_207 → c_023 loose.
- **2 de jure items are partial-overlaps that need a placement call:** IND_197 (compensation/expenditure threshold or new "any compensation" row), IND_203 (principal-side spending reports).
- **1 de jure item is a candidate new row:** IND_199 (annual registration form, which has no clean parallel — it's implicit but never asked as an explicit yes/no anywhere else).
- **8 de facto items map to the v1.1 schema's practical_availability axis** on existing or near-existing canonical questions. None create new compendium rows.

## What CPI 2015 has that the other 9 rubrics don't

**The de facto / in-practice axis as a first-class measurement.** CPI 2015 spent journalist effort per-state to score whether the law is followed (audits #208, penalties imposed #209, registration compliance #198, citizen access works #205, open data actually delivered #206, etc.).

This is a fundamentally different research instrument than statute-reading. It requires per-state empirical investigation. PRI 2010 has accessibility items that are partly de facto (Q1-Q6 about whether the website actually works), but PRI does not pair them explicitly with their de jure counterparts — CPI does, by design.

**Implication for compendium 2.0:** the de facto / de jure pairing in CPI 2015 is **direct empirical validation of the v1.1 schema's two-axis design** (`legal_availability` × `practical_availability`). CPI 2015 is the only rubric in the corpus that explicitly measures both axes; that the architecture pre-dating this run already accommodates them is a positive signal.

## What CPI 2015 doesn't have that the other 9 rubrics do

A long list — these are the specific questions other rubrics ask that CPI 2015 abstracts away:

- **Gifts to public officials** — Newmark/Opheim core item, FOCAL financials.10 (strict c_001), PRI E1f_iii / E2f_iii. CPI's "expenditures benefitting officials" is implicit in #201 ("detailed spending reports") but not asked explicitly.
- **Revolving door / cooling-off period** — strict c_019 (HG Q48 + Newmark2017). CPI 2015 has no item covering this.
- **Prohibitions** — strict c_020/c_021/c_022 (Newmark2005/2017 campaign contribution and solicitation prohibitions). CPI's C11 has none; CPI handles prohibitions in other categories (likely C2 Political financing, C5 Legislative accountability).
- **Itemization granularity** — loose c_028 to c_031 (PRI E1f_i-iv principal/lobbyist twin pairs on direct/indirect/other costs and itemized format). CPI #201 says "detailed spending reports" without specifying itemization structure.
- **Per-meeting contact log** — FOCAL contact_log.* (mostly singletons in consensus). CPI doesn't ask about per-meeting fields.
- **Reporting cadence detail** — loose c_033-c_038 (PRI E1h/E2h cadence options: monthly, quarterly, tri-annually, semi-annually, annually, other). CPI #199 asks "annual" only; #202 asks "reasonable frequency" without enumerating options.
- **Search/filter granularity** — PRI Q7a-Q7o (15 search-by-field facets, all consensus singletons). CPI doesn't decompose.
- **Registrant taxonomy** — PRI A1-A11 (11 registrant categories: legislators, executive branch, governor's office, state agencies, etc.). CPI #197's "anyone paid" doesn't enumerate.
- **Bill numbers / specific legislation lobbied** — loose c_012 (FOCAL contact_log.11 + PRI E1g_ii / E2g_ii). CPI doesn't ask.
- **Frequency of website updates** — FOCAL timeliness.1 / HG Q38. CPI doesn't ask.

CPI 2015's deliberate abstraction is appropriate for its purpose (a 13-category whole-of-government integrity scorecard graded by working journalists) but means it's not a substitute for finer-grained instruments — it's complementary.

## Recommendations for compendium 2.0

These all serve the projection-success criterion stated above.

1. **Adopt the projection-round-trip test as the formal acceptance criterion.** Compendium 2.0 is "done enough" when all 9 source rubrics' published per-state scores can be reproduced (within rubric-specific tolerance) by applying each rubric's projection logic to populated compendium cells.
2. **Pursue the minimum-compendium goal explicitly.** A row that no rubric's projection logic ever reads is deletable. After the rubric-projection logic for all 9 is implemented, run a coverage analysis: for each canonical row, list which rubrics use it. Rows used by 0 rubrics are deletion candidates (modulo non-projection reasons to keep them — e.g., the practical-availability matrix downstream consumers will use).
3. **Commit to capturing cell values, not just row presence.** IND_197 (any-compensation threshold) and IND_199 (annual registration cadence) are projectable only if the compendium captures the value (threshold dollars; cadence as enumerated value), not a binary "is there a standard yes/no."
4. **Keep the principal-side spending-report row** even though it's a consensus singleton from PRI E1a-family. CPI #203 needs it for projection.
5. **Treat CPI 2015's 8 de facto items as evidence anchors for the practical_availability axis** in the v1.1 schema. Each maps to a `practical_availability` assertion that depends on per-state empirical research, not statute reading.
6. **Reuse CPI's 2015 per-state scores** (`papers/CPI_2015__sii_scores.csv`) as **cross-validation ground truth** for any pipeline we build that estimates practical-availability from portal scraping + LLM extraction. 50 states × 14 items, scored. With the caveat that 2015 conditions don't perfectly reflect 2026 — but that's a noise concern, not a sign-error one.
7. **Surface IND_199 (annual registration form) and IND_203 (principal-side spending reports) as candidate new compendium-2.0 rows.** These don't have clean strict-cluster homes and are real questions that other rubrics imply but don't ask.
8. **Do NOT do a 9-subagent re-dispatch just for the CPI 14 items.** Manual fold-in is much cheaper, and the existing consensus structure is rich enough to place them.

## Open work that follows from this success criterion

- **Per-rubric projection logic.** For each of the 9 source rubrics, define `f_rubric(compendium_cells_for_state) → rubric_score_for_state`. This is the projection layer; it's what consumes the compendium. Can be implemented per-rubric incrementally; CPI 2015 C11 is a small target (14 items × 50 states) and a good first concrete test.
- **Round-trip validation harness.** Once projections exist, run them on N states' populated compendium cells and compare to published rubric scores. Discrepancies feed back into compendium row-set decisions: missing row ⇒ add; unused row ⇒ candidate for removal.
- **Cell-value schema.** Decide which compendium rows carry binary cells and which carry typed values (dollars, days, enumerated cadences, etc.). The projection-test makes this concrete: if any rubric reads a value, the compendium has to carry it.

## Files

- `papers/CPI_2015__sii_criteria.xlsx` — full xlsx (13 sheets, 7.6 MB; lobbying-disclosure sheet is 14 of the 245 indicators)
- `papers/CPI_2015__sii_scores.csv` — per-state scores
- `results/items_CPI_2015_lobbying.tsv` — 14 atomic items in our standard schema
- `results/3way_consensus/` — the underlying consensus pass these items are being compared against

# Plan-sharpening + naming-convention memorialization

**Date:** 2026-05-14
**Branch:** compendium-naming-docs

## Summary

Sub-session 3 on `compendium-naming-docs`. Pre-implementation review of sub-2's plan ([`20260514_rename_review_and_plan.md`](20260514_rename_review_and_plan.md)) surfaced three places where the plan was weaker than it could be:

1. **C7's content-rename nature.** The rename `lobbying_definition_included_activity_types` → `def_lobbying_activity_types` (and the parallel `lobbyist_definition_*` row) drops the `_included_` infix that carried semantic precision — these rows enumerate the *included* activity/actor types in the statutory definition. The new family-uniform `def_*` shape is ambiguous about inclusivity. The plan treated C7 as a mechanical family-prefix swap alongside C1-C6, which is technically fine but understates the semantic shift.
2. **C3's `_<unit>` suffix decision was punted to execution time.** The convo's open questions said "Probably acceptable — it mirrors `lobbyist_filing_de_minimis_threshold_*` precedent." But execution agents are scoped to mechanical rename; design-shape calls don't belong there.
3. **C2's LV-1 categorical exception was a per-row judgment that needed promotion to a rule.** The decision to put `lobbyist_filing_distinguishes_in_house_vs_contract_filer` in `lobbyist_filing_*` (while its 5 cluster-siblings go to `lobbyist_spending_report_*`) was justified on "semantic faithfulness over cluster-uniformity." If that rule isn't memorialized, the next LobbyView-style schema-coverage row added will get mis-classified.

Sub-3 brought these to Dan as three sharpenings. Dan's calls: (1) leave C7 framing alone (the plan's §1 + §3 byte-identity tests already enforce the cell_type/provenance preservation, and the `def_*` family's flat shape is acceptable), (2) pick the C3 shape now and document the logic, (3) yes, memorialize the LV-1 distinction. Sub-3 then made the calls and executed 4 doc edits across the plan and NAMING_CONVENTIONS.md.

## Topics Explored

- Sub-2 convo + plan re-read with three sharpening candidates in mind
- C3 unit-suffix question — four candidate shapes considered:
  - **A. `_threshold_<measure>_<unit>`** (plan's current proposal) — chosen
  - B. `_<measure>_threshold_<unit>` — keeps measure-first ordering, breaks §9 suffix-table convention
  - C. `_threshold_<measure>` (drop the unit) — would also require renaming the de-minimis precedent, out of scope
  - D. `_threshold_<measure>` (same as C, family-uniform reading) — same issue
- Re-read of NAMING_CONVENTIONS.md §5 (α form-type split), §7 (three-threshold framework), §9 (cell-type conventions), §11 (prefix-choice decision tree) to find the right home for the LV-1 categorical-exception rule and the threshold-suffix rule
- Re-read of plan §5 (edge cases) to find E2's deferred-decision wording

## Provisional Findings

- The C3 suffix question turns out to be a *resolution of existing drift*, not a *creation of new drift*. NAMING_CONVENTIONS.md §9 already encoded `_threshold_*_dollars` / `_threshold_time_percent` as the canonical suffix shape (with `compensation_threshold_for_lobbyist_registration` listed there as an example of a row that *should* match but doesn't). The current names violate §9; the rename brings them into compliance. The earlier convo framing this as "novel for the `lobbyist_registration_*` family" understated the §9 precedent and overstated the drift.
- The unit token redundancy with `cell_type` (`_dollars` repeats info already in `cell_type: Optional[Decimal]`) is intentional — readers should be able to know the unit from the row_id alone.
- The "single-measure family uses `_threshold_<unit>`, multi-measure family uses `_threshold_<measure>_<unit>`" rule generalizes cleanly. The filing-de-minimis family is currently single-measure (`_dollars`) with a `_time_percent` sibling that *also* uses `_threshold_<unit>` because each row captures one measure of the same concept (`de_minimis`). C3's lobbyist-status threshold has three distinct measure concepts (compensation, expenditure, time) all triggering the same status threshold, so each row needs an explicit measure word.
- The LV-1 exception is fundamentally a distinction between **schema-coverage rows** ("does the system distinguish X at the data-system level") and **report-content rows** ("does the report include field X"). This distinction is already implicit in the v2 TSV's row inventory but wasn't surfaced as a naming rule until sub-3.

## Decisions Made

- **C7 framing: no changes.** Plan's §1 Candidate 7 stays as-is; §3 byte-identity tests cover cell_type/provenance preservation. The `_included_` infix drop is acceptable because the rest of the `def_*` family uses the same flat shape and the family convention is "rows enumerate what the statute includes."
- **C3 shape: `_threshold_<measure>_<unit>` is canonical.** Rule: "include the measure word when the family contains multiple measures, omit when there's only one; always include the unit suffix when `cell_type` is a typed numeric (intentional redundancy)." Documented in NAMING_CONVENTIONS.md §7. Plan §5 E2 updated to reference the resolved rule.
- **LV-1 categorical exception: codified as a rule.** Documented in NAMING_CONVENTIONS.md §5 (categorical-exception paragraph) and §11 (schema-coverage decision branch under "What kind of observable is it?"). Any future LobbyView-style schema-coverage row goes in `lobbyist_filing_*`, not `lobbyist_spending_report_*`.
- **Doc-only commit, no code, no tests.** No behavior changes; the v2 TSV is unchanged; the rename target set is unchanged.
- **Convo file: this file.** Sub-3 was a 6-edit follow-up to sub-2's plan rather than a standalone investigation, but per the finish-convo pattern we keep one convo file per session for uniformity. The RESEARCH_LOG sub-3 entry links here.

Links:
- [`plans/20260515_rename_execution_plan.md`](../plans/20260515_rename_execution_plan.md) — §5 E2 updated this session
- [`../../../compendium/NAMING_CONVENTIONS.md`](../../../../compendium/NAMING_CONVENTIONS.md) — §5, §7, §11 updated this session

## Results

No results files produced — the 4 doc edits ARE the deliverable.

## Open Questions

- **§7 single-measure rule edge case.** The §7 wording says "the measure word is omitted because the threshold concept itself has one name (`de_minimis`)." But `lobbyist_filing_de_minimis_threshold_dollars` has *two* sibling rows now (`_dollars`, `_time_percent`) — so is "single-measure" the right characterization, or are these two measures of the same concept (and so the measure word would be required if we wanted strict consistency)? The rule as written treats them as two unit-variants of one concept, which matches the empirical row inventory. Flag for the execution agent to revisit if it turns out the de-minimis family is actually multi-measure in disguise.
- **C7 `_included_` infix drop precedent.** Sub-3's decision was "don't dwell on it in the plan" — but future agents adding to the `def_*` family will hit the same question (do we say "_included_activity_types" or "_activity_types"?). The family-wide convention is implicitly "rows enumerate what the statute includes," but this isn't stated in §4 (the def/actor triangle). Possible follow-up: add a sentence to §4 making the inclusive-set convention explicit. Out of scope for sub-3; flag for a future audit/sharpening pass.
- **§11 schema-coverage bullet positioning.** I placed it right after the "spending report" bullet so the LV-1 distinction is encountered immediately after the case it most resembles. An alternative would be a §11 #1.5 sub-section explicitly about schema-coverage vs report-content. The bullet placement is sufficient for now; the §5 narrative carries the categorical rule.

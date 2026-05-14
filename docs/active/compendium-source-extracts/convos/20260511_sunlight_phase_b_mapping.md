# Sunlight 2015 — Phase B projection mapping (third rubric)

**Date:** 2026-05-11
**Branch:** compendium-source-extracts
**Plan executed:** [`../plans/20260507_atomic_items_and_projections.md`](../plans/20260507_atomic_items_and_projections.md) Phase B (third rubric, after CPI 2015 C11 and PRI 2010).
**Predecessor conventions:** [`../results/projections/cpi_2015_c11_projection_mapping.md`](../results/projections/cpi_2015_c11_projection_mapping.md), [`../results/projections/pri_2010_projection_mapping.md`](../results/projections/pri_2010_projection_mapping.md).

## Summary

Third Phase B per-rubric projection-mapping doc shipped: Sunlight Foundation 2015, the smallest contributing rubric (5 items, item 4 excluded → 4 in scope). The mapping produced 13 distinct compendium rows touched, 11 of which are read by at least one other rubric — confirming the 2026-05-07 audit's framing that Sunlight's contribution is cross-rubric redundancy on heavily-shared rows, not novel observables.

The session also produced two non-Sunlight artifacts triggered by an early permission-prompt mistake. (1) A user-flagged recurring failure mode — agents reaching for bash `for`-loops when explicit-list or Python alternatives would not have triggered a permission prompt — was documented in a new project-level memory file at `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_use_preapproved_bash_patterns.md`. (2) The same investigation surfaced that several existing ALLOW_RULES (`xargs *`, `find *`, `awk *`, `sed *`) already have the same loop-backdoor property as `for` would; a dotfiles note at `~/code/dotfiles/notes_bash_loop_permissions.md` documents the four current backdoors with concrete exploit paths and proposes a least-invasive permissions fix (add `Bash(for *)` / `Bash(while *)` to DENY so the failure mode hard-fails rather than soft-prompts).

Third locked architectural decision since the CPI session: **"Collect once, map to many."** Every compendium row is one statutory observable; multiple rubric projections read it. Where multiple rubrics ask the same conceptual question at varying granularities, the compendium stores the finer-grained observable and coarser rubrics' projections roll up via OR/AND/derived flags. This was implicit in the CPI/PRI mappings but became explicit when a user pushback caught me proposing Sunlight-only rows that 7 other rubrics also read. The "collect once" annotation discipline — `[cross-rubric: …]` next to every row entry — was added to the Sunlight doc and is locked for the remaining 7 rubrics.

## Topics Explored

- **Sunlight item 1 (Lobbyist Activity, 4-tier).** Decomposed into 3 nested binary observables (general subject matter / bill or action identifier / position on bill), then split per α into reg-form vs spending-report variants for 6 compendium rows total. Cross-rubric grep across HiredGuns, Newmark 2017/2005, Opheim, FOCAL, OpenSecrets, CPI, and PRI 2010 (the historical disclosure-law rubric, surveyed for cross-rubric continuity only) confirmed 11 cross-rubric readers across the 6 rows.
- **α — split registration-form vs spending-report.** User-confirmed for any content-cell row where the two forms are statutorily distinct observables. Cost is 3 extra binary cells per content concept (6 cells where 3 would suffice for a form-agnostic rubric like Sunlight); benefit is preserving the HG Q5 vs Q20 distinction (where a state can require bill_id on the spending report but not the reg form).
- **β — Opheim conflation.** Opheim's `disclosure.legislation_supported_or_opposed` single binary conflates bill-identifier AND position. Three possible "split" readings examined: (1) split projection only (Opheim TSV unchanged; projection reads compendium cells AND'd), (2) make position structurally conditional on subject (Optional[bool] modeling), (3) re-atomize Opheim's source TSV into 2 rows. User-confirmed Reading (1). Faithful to source paper; granularity bias lives at the compendium layer, not the source-extract layer.
- **Sunlight item 2 (Expenditure Transparency, 4-tier).** Decomposes into 3 binary observables (report_required, categorizes_by_type, includes_itemized_expenses) — clean nesting where each tier adds a requirement. The "includes_itemized_expenses" row pre-exists from CPI #201 mapping; "report_required" is implicit gateway across many rubrics.
- **Sunlight item 3 (Expenditure Reporting Thresholds, 2-tier).** Mapped to a typed `Optional[Decimal]` cell shared with HiredGuns Q15 (which reads same cell at 5-tier ordinal granularity). **Critical distinction surfaced and named:** three distinct threshold concepts must stay separate in compendium 2.0:
  - **Lobbyist-status threshold** (CPI #197, HG Q2, Newmark/Opheim def.*_standard, FOCAL scope.2) — at what level do you become a lobbyist
  - **Filing-de-minimis threshold** (PRI D1) — once a lobbyist, at what level do you start filing
  - **Itemization-de-minimis threshold** (Sunlight #3, HG Q15) — once filing, what within the filing must be itemized
  - These are commonly conflated in casual usage; the compendium must keep them distinct or PRI D1 vs Sunlight #3 cross-rubric validation will be wrong.
- **Sunlight item 5 (Lobbyist Compensation, 2-tier).** Form-agnostic; reads OR across 3 compensation-disclosure rows (total compensation on spending report, compensation broken down by client on spending report, compensation on registration form). Strong cross-rubric coverage: Newmark 2017/2005, HG Q13/Q27 (lobbyist + principal sides), PRI E2f_i, CPI #201, OpenSecrets cat 2 (which reads finer granularity).
- **Bash-loop permissions investigation.** Triggered by my own `for f in ...; do wc -l "$f"; done` early in the session, which prompted a permission request. User's frustration ("this comes up at least once a session, and it's really annoying") led to: (a) checking why for-loops trigger prompts (they don't match any pre-approved chain prefix); (b) considering whether expanding ALLOW_RULES is the right fix (no — loop bodies are dynamic and would create a backdoor); (c) finding existing `xargs / find / awk / sed` rules already have this backdoor property; (d) drafting two artifacts.

## Provisional Findings

- **13 compendium rows touched by 4 Sunlight items in scope; 11 of 13 have cross-rubric readers.** Distribution of overlap: reg-form variants (3 rows) read by HG Q5; spending-report variants (3 rows) read by HG Q20 + Newmark 2017/2005 + PRI E2g + Opheim + FOCAL contact_log.10/11; spending-report-gateway / categorization / itemization (3 rows) read by HG Q11/Q14/Q15 + CPI #201 + PRI E1f_iv + FOCAL financials.6; itemization-threshold (1 row) read by HG Q15; compensation rows (3) read by Newmark + HG Q13/Q27 + CPI #201 + PRI E2f_i + OpenSecrets cat 2. **Sunlight's role in compendium 2.0 is validation redundancy, not novel structure.**
- **The "collect once, map many" principle is well-supported empirically.** Per-rubric mapping done in isolation would have proposed at least 13 new compendium rows just for Sunlight; cross-rubric grep showed 11 of them were already touched by CPI/PRI mappings or pending rubric mappings. The dedup pass after all Phase B docs exist will collapse these substantially.
- **Three threshold concepts named distinctly for the first time.** Previously implicit in CPI #197 (lobbyist-status) and PRI D1 (filing-de-minimis) treatment; Sunlight #3 forced naming the third (itemization-de-minimis). Compendium 2.0's row freeze must preserve all three.
- **Sunlight cannot reproduce its published `Total` or `Grade`** with item 4 excluded. Per-item validation against the 4 in-scope per-criterion columns of the per-state CSV is the recommended Phase C scope; reproduce the 4 individual scores, not the aggregate.
- **Per-state distribution skew observed.** Item 1 mode is tier 0 ("general subjects only"; 50% of states); item 3 mode is tier −1 (66% of states have some itemization threshold); item 5 is approximately split (54% don't require compensation disclosure). These distributions tell us where the discriminating cells are for state-to-state variation.
- **Memory-file approach reduces but doesn't eliminate** agent-side bash-loop mistakes. The project memory file should load in future lobby_analysis sessions; the dotfiles note proposes the cheapest permission-list addition (`Bash(for *)` / `Bash(while *)` to DENY) that would surface the failure mode louder for agent-side training.

## Decisions Made

- **Phase B mapping #3 (Sunlight 2015) shipped.** All 4 in-scope items mapped per the locked template; result doc at `results/projections/sunlight_2015_projection_mapping.md`.
- **α (form-type split) confirmed** for content-cell rows. Locked across remaining 7 Phase B mappings.
- **β (Opheim AND projection) confirmed** Reading (1). Opheim's source TSV stays as one binary; projection lives in the projection layer.
- **"Collect once, map many" annotation discipline locked.** Every candidate row entry in remaining Phase B mappings includes a `[cross-rubric: …]` annotation listing other readers, seeding the compendium-2.0 dedup pass.
- **Three threshold concepts must stay distinct.** Locked for compendium-2.0 row freeze; documented in Sunlight mapping doc's "CRITICAL distinction" block.
- **Sunlight Phase C validation strategy: per-item only (recommended; user confirmation still pending).** Cannot reproduce Total or Grade because item 4 excluded; honest scope is the 4 individual per-criterion column comparisons.
- **Workflow fix: cross-rubric grep BEFORE drafting any row, not after.** Triggered by my error pattern in this session (proposing Sunlight-only rows that 7 other rubrics already read). Encoded in the new next-session plan handoff.
- **Next-session plan handoff written** at `plans/_handoffs/20260511_phase_b_continued_remaining_7.md` covering the 7 remaining rubrics + locked decisions + workflow fix.

## Results

- [`results/projections/sunlight_2015_projection_mapping.md`](../results/projections/sunlight_2015_projection_mapping.md) — Sunlight 2015 projection mapping doc (13 compendium rows × 4 items, with cross-rubric overlap annotations).
- [`../../../tools/sunlight_distributions.py`](../../../../tools/sunlight_distributions.py) — quick 30-line distribution script over Sunlight per-state CSV (used to fill the per-state-distributions table in the mapping doc).
- [`plans/_handoffs/20260511_phase_b_continued_remaining_7.md`](../plans/_handoffs/20260511_phase_b_continued_remaining_7.md) — next-session plan handoff for the remaining 7 Phase B mappings.
- **Non-repo artifacts** (out of lobby_analysis git tree):
  - `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_use_preapproved_bash_patterns.md` — project memory file for future sessions
  - `~/code/dotfiles/notes_bash_loop_permissions.md` — dotfiles working memo on bash-loop permissions and the four existing loop-backdoor rules

## Open Questions

- **Phase C validation strategy for Sunlight — final user confirmation.** Recommended per-item only; awaiting user lock-in. Two alternatives documented in the mapping doc (Total-minus-item-4 hack; drop Sunlight from Phase C entirely).
- **Threshold-concept naming for the v2.0 schema row freeze.** The three threshold rows surfaced this session (`compensation_threshold_for_lobbyist_registration`, `lobbyist_filing_de_minimis_threshold_dollars` per PRI mapping, `expenditure_itemization_de_minimis_threshold_dollars`) need cross-checking against the existing CPI/PRI mappings during dedup. Compendium 2.0 row IDs should be locked to prevent later conflation.
- **OpenSecrets state-map widget JS pull** — flagged in the 2026-05-07 (pm) handoff as a Phase-B-doesn't-need-but-Phase-C-might issue. Still open; not unblocked by this session.
- **Whether the next-session plan handoff itself needs more material.** The current handoff covers the 7 remaining rubrics at a per-rubric scope-and-watchpoints level. The implementing agent (likely fresh-context) will still need to read the locked plan + 2026-05-07 handoff + this session's convo. Three handoffs feels like a lot; worth re-streamlining if it becomes a friction point.

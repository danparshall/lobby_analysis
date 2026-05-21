# Per-Paper Source-Framework Extraction (Compendium 2.0 Foundation)

**Goal:** Produce a per-paper, rubric-native extraction of indicator items from each source-framework paper in `papers/text/`, **excluding PRI 2010 entirely**. Each paper gets one TSV (machine-readable indicator list) + one MD (human-readable methodology summary). After all extracts ship, the user personally reviews each one. Only after all reviews are in does data-object-2.0 design begin (a separate plan written then, not now).

**Originating conversation:** [`docs/active/compendium-source-extracts/convos/20260502_pm_compendium_rebuild_pivot.md`](../convos/20260502_pm_compendium_rebuild_pivot.md) — read this first; it documents *why* this plan exists, including the failure modes that drove the pivot. Implementing agent should not need to read the parent conversation transcript.

**Branch:** `compendium-source-extracts` (already created off `origin/main`; worktree at `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts/`).

**Confidence:** Procedural. Extraction itself is straightforward; the artifact format will likely need a tweak after the user reviews the template paper. Built-in template-first sequencing absorbs that.

**Architecture:** Pure analysis task. Per-paper agents read paper text only and write two artifacts each. No code changes. No schema changes. No new modules.

**Tech Stack:** None. The `papers/text/<paper>.txt` files are pre-extracted; `grep`/`Read` work directly. Optional: `csv`/`tsv` Python parsing for TSV-format validation if the implementing agent wants a sanity check, but not required.

**Execution model:** Implementing agent (could be a new Claude Code session, a general-purpose subagent, or the user) follows the Nori workflow per `CLAUDE.md`. Pre-flight reads STATUS.md, README.md, this branch's RESEARCH_LOG.md (to be created — see *Implementation Details*), this plan, and the spawning convo. The implementing agent dispatches one template extraction agent, surfaces output for user review, then dispatches the remaining 6 paper extractors in parallel.

---

## Why this plan exists

The compendium-as-shipped (`compendium/disclosure_items.csv`, 141 rows) is structurally PRI-shaped. The Phase 0 audit on the `statute-extraction` branch produced 186 concerns across 109 of 141 rows (`docs/active/statute-extraction/results/20260502_compendium_audit_concerns.md`); two-run inter-auditor agreement was 24.2%. Walking through the concerns showed that the surface tag-disagreements were symptoms of two deeper issues:

1. **C1/C2 taxonomy assumed every row is axis-typed and every `framework_references` cluster is homogeneous.** Both assumptions break: e.g., the `DEF_PUBLIC_ENTITY` family isn't axis-typed (it's a definition-existence + criteria cluster), and the `RPT_*_NON_COMPENSATION` rows have heterogeneous refs (PRI sub-component vs FOCAL total vs Sunlight tier).

2. **The compendium's row count, atomization, and descriptions are PRI-derived.** Concrete evidence:
   - `DEF_PUBLIC_ENTITY` is 4 rows because PRI Q-C had parent + 3 sub-criteria. No other rubric demands this split.
   - 12 `FREQ_*` rows = PRI E1h/E2h enumeration. Newmark uses one categorical (`freq_binary`).
   - 11 `REG_*-A-series` = PRI A1–A11. FOCAL 1.1 covers the same conceptually via one AND-disjunction.
   - 8 `RPT_*_NON_COMPENSATION`/`OTHER_COSTS`/`ITEMIZED`/`COMPENSATION` rows = PRI E1f i/ii/iii/iv split × 2 sides.
   - ~24 rows have a `?.` formatting artifact: literal evidence of "ran a script over PRI rubric text + appended `.`."

D9 fixed *vocabulary* PRI-privilege (rubric-neutral threshold-row IDs). D9 did not fix *structural* PRI-privilege. Patches to descriptions / domain assignments / row renames leave the PRI-shaped atomization intact. Phase 0's "fix list" path is the wrong shape of work. Rebuilding from sources is the right shape.

This plan is the first step of the rebuild: extract per-paper indicator lists in each paper's *own* structure, with **no PRI**, then user-review, then design 2.0.

---

## In scope for this plan

1. Extract indicator items from **7 source-framework papers** (or 8 — see Open Question 1):
   - `Opheim_1991__state_lobby_regulation`
   - `Newmark_2005__state_lobbying_regulation_measure`
   - `CPI_2007__hired_guns_methodology` (PDF + HTML supplement)
   - `Sunlight_2015__state_lobbying_disclosure_scorecard`
   - `Newmark_2017__lobbying_regulation_revisited`
   - `OpenSecrets_2022__state_lobbying_disclosure_scorecard`
   - `Lacy_Nichols_2024__focal_scoping_review` (FOCAL — paper + supplementary file `Lacy-Nichols-Supple-File-1-IJHPM.pdf`)

2. For each paper: produce `docs/active/compendium-source-extracts/results/items_<Paper>.tsv` + `items_<Paper>.md`. Filename convention: drop the paper's date suffix and use a short stable stem (e.g., `items_Opheim.tsv`, `items_FOCAL.tsv`, `items_Newmark2005.tsv`, `items_Newmark2017.tsv`, `items_HiredGuns.tsv`, `items_Sunlight.tsv`, `items_OpenSecrets.tsv`). Open Question 6 asks the user to confirm this naming.

3. Template-first sequencing: one paper extracted in foreground, user reviews format, then remaining 6 dispatched in parallel.

4. Per-paper MD summary enumerates predecessor frameworks the paper cites/reviews — names only, no chase. The union of cited predecessors becomes input to a separate follow-up audit.

5. Per-paper MD summary documents Book of States (or other) fallback dependence: when the paper's own definition of an item is thin and the operational definition lives in CSG's *Book of States* or another companion source, flag it. User-review decides whether to chase those companion-source definitions.

## Explicitly NOT in scope

- **Any reference to PRI 2010** in any extract. Implementing agent and per-paper agents do not read `papers/text/PRI_2010__state_lobbying_disclosure.txt`, do not open `compendium/disclosure_items.csv`, do not open `compendium/framework_dedup_map.csv`, do not open `docs/COMPENDIUM_AUDIT.md`. Predecessor lists in MDs may name PRI as a citation; that is the only place PRI appears.
- **Cross-paper mapping or comparison.** Don't annotate "this is similar to X paper's Y."
- **Domain assignment** (definitions / registration / reporting / contact_log / etc. — those are compendium 1.x's domains and do not apply here).
- **Axis-tagging** (target / actor / threshold / cadence / scope / etc.).
- **Merging or splitting items across papers.** If Opheim has 7 definition criteria and Newmark also has 7 with different boundaries, both go in their respective TSVs at full count; reconciliation is downstream.
- **Compendium 2.0 design** itself.
- **Chasing predecessor frameworks** (FOCAL's 15 reviewed; Newmark's predecessors; etc.). Per-paper MDs *enumerate* the citations; whether to chase any of them is a separate follow-up plan, written after all 7 extracts ship and the user has reviewed the cited universe.
- **Reading prior derived artifacts** as seeds: `focal_2024_indicators.csv`, `Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`, any pri-rubric CSVs from `pri-2026-rescore`, the compendium itself, the v2 audit doc. These exist; the agents should ignore them. Sunlight's data CSV may be consulted *after* extraction as a completeness sanity-check, not as a seed (Open Question 4 lets the user adjust this).

---

## Per-paper artifact spec

Each paper produces two files at `docs/active/compendium-source-extracts/results/`:

### TSV: `items_<Paper>.tsv`

Tab-separated (not CSV). One row per indicator/measure/rubric item the paper itself defines. Columns (header row):

| column | content |
|---|---|
| `paper_id` | Short stable ID. Use these: `opheim_1991`, `newmark_2005`, `hired_guns_2007`, `sunlight_2015`, `newmark_2017`, `opensecrets_2022`, `focal_2024` |
| `indicator_id` | Paper-native identifier verbatim if the paper numbers/labels its items (e.g., FOCAL's `1.1`, `2.3`; CPI Hired Guns Q-numbers; Sunlight's tier labels). If the paper doesn't number, generate a stable short ID following the paper's section structure (e.g., `def.compensation_standard`, `enforce.subpoena_witnesses`) |
| `indicator_text` | Verbatim short text from the paper (the item's name or one-line description) |
| `section_or_category` | Paper's own grouping label for this item (e.g., Opheim's "Statutory definition of a lobbyist", FOCAL's "Resourcing", CPI's section letters) |
| `indicator_type` | One of: `boolean` / `numeric` / `categorical` / `ordinal` / `open` / `unclear`. Inferred from how the paper scored the item. Use `unclear` (with `notes`) if the paper doesn't specify |
| `scoring_rule` | Verbatim quote of how the paper scored or weighted this item, if specified. Empty if the paper doesn't say |
| `source_quote` | Verbatim quote from the paper text (≤200 chars), with `papers/text/<paper>.txt:line_N` reference. This is non-optional; every row has a source_quote so the user-review can spot-check fidelity |
| `notes` | Anything ambiguous, scope-implicit, or worth flagging for review. Especially: composite indicators, items whose operational definitions live in a fallback source like Book of States, items the paper labels but doesn't define |

Tab-separated to avoid quoting hell on multi-clause indicator text. If a cell contains a tab character, escape as `\t` literal; if a cell contains a newline, replace with `; ` (record this transformation in the MD if used). UTF-8.

### MD: `items_<Paper>.md`

Markdown summary, sections (in order):

1. **Paper.** Full citation. 1-paragraph "what this paper claims to be measuring" in the paper's own framing (verbatim phrases preferred).
2. **Methodology.** How indicators chosen / scored / aggregated. Sample size (number of states reviewed if applicable). Year of data captured. Composite / sub-aggregate scoring rule, if one exists. Inter-coder reliability if reported. Anything else that affects how to interpret the indicator list.
3. **Organizing structure.** The paper's own section/category hierarchy that organizes the indicators. This captures *how the paper thinks the rubric decomposes* — important input for later cross-paper comparison. List sections + counts (e.g., "Definition: 7 items; Disclosure: 8 items; Enforcement: 7 items").
4. **Indicator count and atomization decisions.** Total count + brief notes where the paper atomized differently than common sense (e.g., "treats compensation/expenditure/time standards as 3 separate items in one sentence; followed paper's structure"). Flag any cases where the agent had to make a judgment call on row-count.
5. **Frameworks cited or reviewed.** Names only — no chase. Just "this paper cites or reviewed: X (year), Y (year), Z (year), ..." so we can later collect the universe of predecessors. Distinguish *rubric* citations (other lobbying-regulation rubrics) from *theoretical/methodological* citations if the distinction is clear in the paper.
6. **Data sources.** If the paper got per-state values from a fallback source (CSG's *Book of States*, NCSL, statute-text scrape, etc.), name it explicitly. **Critical:** if the paper's own definition of an item is thin and the operational definition lives in the fallback, flag this — Phase 2's reviewer (the user) needs to know which items are paper-defined vs paper-pointed-to-elsewhere.
7. **Notable quirks / open questions.** Anything that complicates a clean indicator list (e.g., the paper aggregates an ordinal composite that doesn't decompose cleanly; an indicator's scope is implicit and you had to infer it; an indicator appears in a table but not the prose).

---

## Sequencing

### Step 1: Pre-flight (implementing agent)

Read in order:
- `CLAUDE.md` (worktree root).
- `STATUS.md` and `README.md` at repo root.
- `docs/active/compendium-source-extracts/RESEARCH_LOG.md` (to be created — see *Implementation Details*).
- The spawning convo: `docs/active/compendium-source-extracts/convos/20260502_pm_compendium_rebuild_pivot.md`.
- This plan.
- The auto-memory feedback files relevant here: `~/.claude/projects/-Users-dan-code-lobby-analysis/memory/feedback_pri_not_privileged.md`. (The lesson is structural, not just lexical — this conversation extended the rule.)

Do NOT read: `papers/text/PRI_2010__state_lobbying_disclosure.txt`, `compendium/disclosure_items.csv`, `compendium/framework_dedup_map.csv`, `docs/COMPENDIUM_AUDIT.md`, the Phase 0 audit results docs on `statute-extraction`. These are excluded by design.

### Step 2: Cleanup

Check for stale wrong-path artifacts from the parent session's aborted Opheim dispatch:
- `papers/extracts/Opheim_1991.csv`
- `papers/extracts/Opheim_1991.md`

If found: do not commit. Either delete or leave untracked; they were written at the wrong path and in the wrong format and are pre-format-decision. Re-extract Opheim from scratch in Step 4 regardless.

### Step 3: Confirm Open Questions

User answers Open Questions below at plan-review. Implementing agent picks up the answered plan and proceeds.

### Step 4: Template extraction (one paper, foreground)

Dispatch one extraction agent against the template paper (recommendation: **Opheim 1991** — oldest, smallest, ~22 indicators, foundational; user can override at plan review). The agent prompt is the per-paper extraction prompt template at the end of this plan. Run foreground (block on completion) so the user can review the output before parallel-dispatching.

### Step 5: User format review

Surface the template's TSV + MD to the user. Wait for sign-off. If format adjustments are needed (column add/remove, MD section restructure, naming convention change), update this plan + the per-paper prompt template, then re-run the template if material.

### Step 6: Parallel dispatch (remaining 6 papers)

Single message, 6 `Agent` tool uses in parallel. Each agent gets the per-paper extraction prompt template, customized with its paper's path and `paper_id`. All run in background; surface each completion to the user as it lands.

### Step 7: User per-paper review

User reviews each paper's TSV + MD as they complete. Implementing agent does not advance to Step 8 until all 7 reviews are in.

### Step 8: Stop

Do **not** begin compendium-2.0 design. Do **not** begin predecessor-framework chase. Both are separate follow-up plans, written after this plan's deliverables ship and the user has had time to digest.

Implementing agent's last action: write a short session-end note to `RESEARCH_LOG.md` describing what was produced + flagging any items the user pushed back on during reviews; commit + push the branch.

---

## Per-paper extraction prompt template

When the implementing agent dispatches a per-paper extractor, use this prompt body (substituting `<PAPER>`, `<PAPER_PATH>`, `<PAPER_ID>`, `<OUTPUT_STEM>`):

> You are extracting the rubric/indicator items from **<PAPER>** for the `lobby_analysis` research project. Your output will feed a rebuild of the project's compendium of disclosure-law indicators.
>
> **Working directory:** `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts/`
>
> **Source paper:** `papers/<PAPER_PATH>.pdf` (PDF) and `papers/text/<PAPER_PATH>.txt` (pre-extracted text — prefer this for grep/Read).
>
> **ABSOLUTE RULE:** Do NOT read, reference, or compare against PRI 2010 in any way. Do NOT open `papers/text/PRI_2010__state_lobbying_disclosure.txt`, `compendium/disclosure_items.csv`, `compendium/framework_dedup_map.csv`, or `docs/COMPENDIUM_AUDIT.md`. The compendium-as-shipped is structurally biased toward PRI and we are explicitly rebuilding from sources without that contamination. If you find yourself wanting to cross-reference any of those files — stop. The whole point is fresh extraction.
>
> **Also do not seed from prior derived artifacts:** ignore `compendium/focal_2024_indicators.csv` (if present), `papers/Sunlight_2015__state_lobbying_disclosure_scorecard_data.csv`, and any pri-rubric CSVs from prior sessions. Read only `papers/text/<PAPER_PATH>.txt` (and the PDF if needed for tables/figures).
>
> **Your task:** Read the paper from scratch. Extract every indicator/measure/rubric item the paper itself defines. Preserve the paper's own structure and vocabulary verbatim. Do not map to any other rubric, do not use any project-internal taxonomy (no domain assignment, no axis-tagging), do not look at the existing compendium.
>
> **Output artifacts (two files):**
>
> 1. `docs/active/compendium-source-extracts/results/items_<OUTPUT_STEM>.tsv` — tab-separated, one row per indicator the paper defines. Columns: `paper_id`, `indicator_id`, `indicator_text`, `section_or_category`, `indicator_type`, `scoring_rule`, `source_quote`, `notes`. Header row required. UTF-8. `paper_id` = `<PAPER_ID>` constant. Every row has a non-empty `source_quote` with `papers/text/<PAPER_PATH>.txt:line_N` reference.
>
> 2. `docs/active/compendium-source-extracts/results/items_<OUTPUT_STEM>.md` — markdown summary with these sections (in order): **Paper** (citation + 1-paragraph framing), **Methodology** (how indicators chosen/scored, sample size, year, composite rule), **Organizing structure** (paper's section hierarchy + per-section count), **Indicator count and atomization decisions** (total + flag any judgment calls on row-count), **Frameworks cited or reviewed** (names only, no chase), **Data sources** (Book of States or other fallback if used; flag thin-paper-definition-vs-fallback-defines items), **Notable quirks / open questions**.
>
> Verbatim quotes are gold. Don't paraphrase. Don't tidy up the paper's structure. If the paper has 7 thin labels in a single sentence, you have 7 rows. If the paper has a composite that decomposes into 5 sub-components, you have 6 rows (composite + 5 sub-components) with the aggregation rule recorded in the composite's `notes`.
>
> **When done:** return a short summary (under 200 words): total indicator count; section/category breakdown; any genuinely ambiguous extraction calls you made; predecessor frameworks the paper cites (names); whether the paper relied on Book of States or another fallback for state-level data.
>
> Two files written to disk; nothing committed (parent session handles git).

---

## Edge cases and risks

- **Paper text gaps.** If `papers/text/<paper>.txt` has OCR/extraction holes that leave an indicator un-quotable, flag in `notes` with a `papers/<paper>.pdf` page reference for human follow-up. Don't skip the indicator.
- **Implicit-scope indicators.** Some papers (Opheim, Newmark) use thin labels ("expenditure standard", "compensation standard", "time standard") whose operational meaning sits in companion data tables / Book of States. Flag in `notes`; user-review decides whether BoS lookup happens now or later. Per the parent conversation's direction: BoS lookups are fine; just don't conflate "thin-paper-defines" with "fallback-defines."
- **Composite indicators.** Some papers score an indicator as a sum or aggregation of sub-components. Record both the composite and the sub-components as separate TSV rows; record the aggregation rule in the composite row's `notes`.
- **Ordinal indicators with verbal descriptors.** Sunlight uses 4-tier verbal descriptors per indicator (e.g., "no report / lump / broad categories / itemized w/ dates+desc"). Capture all four levels in `scoring_rule`, not just the binary present-or-not.
- **PRI references in the paper.** Many of these papers cite PRI in their lit reviews. The agent records "PRI" in the predecessor-frameworks list **without reading PRI text**. Don't ingest PRI's items.
- **Paper-level rubric variants.** PRI had two rubrics (disclosure + accessibility) from one paper. Among the 7 papers in this plan, similar splits may exist (e.g., FOCAL's 50 indicators are organized into 8 categories with "Resourcing", "Activities", etc.; might be one rubric or several). Treat as one paper → one extract unless the paper itself unambiguously presents two distinct rubrics; in that case use suffixes like `items_FOCAL_resourcing.tsv` and `items_FOCAL_activities.tsv`. Default to one extract per paper.
- **In-flight Opheim agent.** The parent session dispatched an Opheim extraction at the wrong path before format was locked. Output may exist at `papers/extracts/Opheim_1991.csv` + `papers/extracts/Opheim_1991.md`. Implementing agent ignores it and re-extracts Opheim per the locked spec; the wrong-path files can be deleted or left untracked but **not committed**.
- **Worktree state.** Worktree was created clean off `origin/main` (HEAD `7328d71`). The `data/` directory has its usual cross-machine-symlink state per the user's `feedback_data_symlink_intentional` memory; do not auto-fix.

---

## Branch / lifecycle relationship to other branches

- **`statute-extraction` is unaffected operationally** by this plan but is downstream-dependent: its harness iterates against the compendium-as-shipped, which is being rebuilt here. Once compendium-2.0 lands, the harness work will need a port-forward.
  - The Phase 0 audit deliverable on that branch (`docs/active/statute-extraction/results/20260502_compendium_audit_concerns.md` + reconciliation note) is **retained as historical evidence** that the rebuild was warranted. The Phase 0 plan should be marked superseded with a footer pointing here, but neither it nor the canonical concerns doc should be deleted.
  - **Iter-2 of the harness should pause** until compendium-2.0 lands (see Open Question 5). Iter-2's tightened descriptions on the 7 `definitions` rows would need re-doing post-2.0.
- **Other fellows' branches** (`oh-portal-extraction`) are unaffected operationally. They consume the compendium downstream as a contract; once 2.0 ships and their projection layer adapts, they continue.
- **`main`** is unaffected; this plan ships entirely on the `compendium-source-extracts` branch.

---

## Resolved decisions (locked at plan-acceptance, pending user sign-off)

1. **PRI 2010 is fully excluded** from this branch's work. Not "de-privileged"; ignored. No agent reads PRI text. PRI may be named in predecessor citation lists; nothing more.
2. **Re-extract every paper from scratch.** Ignore prior CSVs (`focal_2024_indicators.csv`, `Sunlight_*data.csv`, any pri-rubric CSVs). The cost of re-extraction is small; the benefit is eliminating compendium-shape carry-over.
3. **TSV not CSV.** Filename pattern `items_<Stem>.tsv` + companion `.md`. Stems: `Opheim`, `Newmark2005`, `HiredGuns`, `Sunlight`, `Newmark2017`, `OpenSecrets`, `FOCAL` (Open Question 6 lets the user override).
4. **Output location:** `docs/active/compendium-source-extracts/results/`. Not `papers/extracts/` (the in-flight Opheim agent's wrong destination). Not `results/` at repo root.
5. **Template-first sequencing.** One paper (recommendation: Opheim 1991) extracted in foreground; user reviews format; remaining 6 dispatched in parallel.
6. **No compendium-2.0 design** until all 7 reviews are in. Separate plan.
7. **Predecessor-framework chase deferred** to a follow-up audit after the 7 extracts ship.

## Open questions (need user input at plan review)

1. **Is there an 8th paper I'm missing?** I count 7 state-rubric papers in `papers/text/` after excluding PRI. The pivot message said "the other 8 frameworks." Possible 8th candidates: GAO 2025 LDA audit (federal), LaPira 2020 LDA at 25 (federal). Both excluded above as federal not state. Confirm 7, or specify the 8th.
2. **Template-paper choice.** Recommendation: **Opheim 1991** (oldest, ~22 indicators, foundational, all-or-mostly Book-of-States-fallback so it stress-tests the BoS-flag handling). Alternatives: **Sunlight 2015** (paper + state-scores CSV → format can be sanity-checked against the CSV's columns after extraction). User picks.
3. **Branch from main confirmation.** Worktree was created off `origin/main` and the new branch `compendium-source-extracts` already tracks origin/main. Confirm this is correct, or is there a different base branch?
4. **Sunlight data CSV usage.** Sunlight's indicator list is plausibly inferrable from its data CSV's columns. The plan keeps the agent blind during extraction. After extraction, should the agent be allowed to consult the CSV as a *completeness sanity-check* (not as a seed)? Recommendation: yes, as a final check, with any discrepancies flagged in the MD's "Notable quirks" section.
5. **Iter-2 of the statute-extraction harness.** Pause until compendium-2.0 lands? Recommendation: pause. Alternative: let it run knowing it's against a soon-to-be-deprecated compendium. Iter-2's chunk-frame preamble + tightened descriptions on the 7 `definitions` rows would need redoing post-2.0 either way; pausing avoids the redo cost.
6. **Filename stems.** Recommendation above: `items_Opheim`, `items_Newmark2005`, `items_HiredGuns`, `items_Sunlight`, `items_Newmark2017`, `items_OpenSecrets`, `items_FOCAL`. User-suggested in pivot message: `items_FOCAL`, `items_Opheim`. Confirm or override.
7. **Should the canonical Phase 0 audit doc be moved or marked superseded** now, or left where it is until compendium-2.0 ships and the audit is officially obsolete? Recommendation: leave in place; mark superseded after 2.0 ships.

---

## Implementation details

- **Worktree:** `/Users/dan/code/lobby_analysis/.worktrees/compendium-source-extracts/`. Branch tracks `origin/main`.
- **Directory scaffolding (already created):** `docs/active/compendium-source-extracts/{convos,plans,results,plans/_handoffs}/`.
- **Files to create on plan acceptance:**
  - `docs/active/compendium-source-extracts/RESEARCH_LOG.md` — minimal seed (purpose statement + this session's entry pointing at the convo + plan).
  - `STATUS.md` row in the *Active Research Lines* table for `compendium-source-extracts`.
- **Agent dispatch model:** general-purpose subagent type. Template-paper agent runs foreground; the parallel-dispatch wave is 6 agents in a single Agent-tool-uses message in background.
- **Commits:** the implementing agent commits per-paper as each ships (small commits, easy to revert). Final commit summarizes the session; `git push -u origin compendium-source-extracts` for backup.
- **No new code modules.** No `tests/` additions. No `src/` additions. No model changes.

## Testing plan (analysis-task exception per write-a-plan skill)

This is a **pure analysis task**. No TDD. Per-artifact validation:

**What to run:** the 8-step sequencing above.

**What outputs to check (per paper):**
- `items_<Stem>.tsv` exists at the planned path.
- TSV header row contains exactly the 8 specified columns in order.
- Row count > 0.
- Every row has a non-empty `source_quote` with `papers/text/<paper>.txt:line_N` reference.
- `paper_id` value is consistent across all rows in that file.
- `items_<Stem>.md` exists at the planned path.
- MD contains all 7 specified sections in order (Paper / Methodology / Organizing structure / Indicator count / Frameworks cited / Data sources / Notable quirks).
- "Frameworks cited" list is non-empty (or explicitly says "the paper cites no predecessor lobbying-disclosure rubric" if true — Opheim is likely an example).

**What constitutes a surprising result:**
- **Total indicator count across 7 papers < 100.** Suggests under-extraction; spot-check.
- **Total indicator count across 7 papers > 400.** Suggests over-decomposition or scope-creep into non-rubric content; spot-check.
- **A paper's MD lists zero predecessor citations.** Possible for Opheim (oldest); flag for any other paper.
- **A paper's MD reports the paper's definitions are entirely fallback-dependent (Book of States or similar).** Important user-review signal: that paper's items are really BoS items, not the paper's items.
- **Inter-paper item-count distribution heavily skewed.** Compendium-2.0 design will need to handle that; no action at this plan's stage.

---

## What could change

- **Format adjustment after template review.** Most likely: column add/remove, MD section restructure. If material, re-run template.
- **Open Question 1 resolution adds an 8th paper.** Sequencing absorbs it (7 + 1 in the parallel wave instead of 6).
- **A paper turns out to have multiple distinct rubrics.** Use suffixes (`items_FOCAL_resourcing.tsv`, etc.).
- **A paper's items are entirely fallback-dependent** (Book of States). User-review will decide whether to chase BoS in this branch or in a follow-up.
- **The user reviews a paper's extract and finds missed indicators** (e.g., from tables/figures not present in `.txt`). Re-run that paper.
- **After all 7 reviews, the user wants to chase a predecessor framework** before designing 2.0. Predecessor-framework-chase plan written then.

---

## Follow-up stages (informational, not gating)

This plan does **not** include data-object-2.0 design or predecessor-framework chasing. Both get their own plans, written after this plan's deliverables ship.

### Follow-up A — Data Object 2.0 Design (separate plan, written after all 7 reviews are in)

- Cross-paper comparison: identify items that ask the same statutory question across papers; identify items that decompose differently; identify items unique to one paper.
- Decide the 2.0 schema's atomization: per topic, what's the right row-count, informed by what the *statute* says, not by any single rubric's split.
- Decide framework_references handling: how do the per-paper TSVs project onto 2.0 rows? (Likely a many-to-many mapping table, but the design is open.)
- User-review gate.

### Follow-up B — Predecessor-Framework Chase (separate plan, written after Follow-up A or alongside)

- Compile the union of cited predecessors across all 7 per-paper MDs.
- For each predecessor: classify as (a) already in our 7-paper set, (b) accessible (PDF available or findable), (c) not retrievable.
- User decides which to add as additional source extracts.
- For added papers: dispatch additional per-paper extractors using the locked format from this plan.

---

**Testing Details:** N/A — pure analysis task. Output validation criteria documented under "What outputs to check" above.

**Implementation Details:** No code changes. Artifact additions: this plan + the convo summary + per-paper TSVs + per-paper MDs + minimal RESEARCH_LOG.md + STATUS.md row update. Implementing agent commits per-paper; final commit + push at session end.

**What could change:** Documented in detail under "What could change" above. Headline: format may shift after template review; an 8th paper may appear.

**Questions:** Seven open at plan-review (above).

---

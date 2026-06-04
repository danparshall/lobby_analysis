# Wide prompt_text pass — YAML-sidecar design

**Date:** 2026-06-04
**Branch:** wi-tier1-direct-read
**Predecessor convo:** [`20260603_prompt_text_fix_iterations_1_and_2.md`](20260603_prompt_text_fix_iterations_1_and_2.md)
**Resulting plan:** [`../plans/20260604_wide_prompt_text_pass.md`](../plans/20260604_wide_prompt_text_pass.md)
**v2.2 ledger entries touched:** Entry 3 (wide pass — currently open), Entry 4 (source-quote provenance — to be closed by this plan's YAML structure)

## Summary

Picked up the 2026-06-03 handoff. Dan chose option (a) from the three open next steps: the **wide 181-row `prompt_text` pass** (vs. (b) MI dispatch unblocked, or (c) Pattern C row-axis split). The narrow 17-row fix had landed and validated (65/66 inter-model agreement, 98.5%) at the cost of $4.7504 cumulative WI Tier-1 API spend.

The session was pure design work — no code written, no API spend. Across ~5 design rounds, Dan repeatedly pulled the proposed shape back toward simpler-and-flatter when I kept trying to encode structural relationships (clarifier slots, derivation rules, rename mappings). The settled design is meaningfully simpler than what I initially proposed: a sidecar YAML file with two flat fields per row (`source_quotes` for reference; `prompt` for what the model sees), a renderer that hides row IDs from the model entirely, and a multi-commit sequence that ships the architectural changes (renderer rewrite, YAML scaffolding) separately from the 181-row data population.

The session also surfaced a meta-pattern worth flagging: my proposals consistently ran a notch more elaborate than necessary; Dan's pushback each round was simplification. Tracking that as session signal — when Dan corrects this way, the correction tends to be load-bearing, not stylistic.

## Topics Explored

- **Column-schema fork: one column, two columns, or three?** Walked through the trade-offs of embedding citation in `prompt_text` (current narrow-pass shape) vs. splitting into `source_quote_verbatim + prompt_text` vs. three columns adding `source_citation`. Initially proposed two-column TSV; Dan reframed as JSON-in-TSV; I pushed back on JSON-in-TSV ergonomics and proposed sidecar YAML.
- **Multi-rubric storage shape.** The narrow pass stored one rubric's quote per row (from `first_introduced_by`). For rows read by N rubrics (one is 8/8), keeping only one rubric's voice undersells the compendium's atomization principle. Sidecar YAML's nested-dict shape accommodates all rubrics naturally.
- **Citation in the model prompt.** Narrow pass put rubric citation (e.g., "(CPI 2015 IND_201; cpi_2015_c11_projection_mapping.md.)") inside the model-facing `prompt_text`. Dropping it: yes, decisively. Citations are mild anchoring signals; provenance lives in YAML keys without going to the model.
- **Schema-coverage and tabled-rubric outliers.** Counted: 1 row from LobbyView schema coverage, 1 row from tabled OpenSecrets. Both have available source material (LobbyView = schema field definition; OpenSecrets-tabled = verbatim quote in the tabled doc). No special `synthetic:` policy needed; handle inline.
- **Row-rename cleanup — should renames happen as a separate commit?** I initially proposed: walk the wide pass, flag misleading renames, ship a substantive rename-cleanup commit. Dan pulled back: hoi polloi shouldn't archaeologize, but the rename problem mostly *evaporates* once the model isn't seeing row IDs — the row name was the Pattern A bug surface, not the structural issue. Rename-cleanup demoted to optional/stylistic.
- **Opaque-handle renderer.** Dan's framing: "the row name shouldn't be something they need to worry about, or probably even see." Implication: `render_legal_roster` should send per-chunk opaque handles (`row_001`, `row_002`, …) + the prompt only. Result parser maps handles → row_ids at receipt. Forcing-function for prompt quality: prompts can't lean on row-name semantic content.
- **Source-of-truth for prompts.** Dan's call: runtime reads YAML directly. TSV's `prompt_text` column gets dropped. TSV remains the compendium-row contract (row IDs, axes, cell types, `rubrics_reading`, `first_introduced_by`, `n_rubrics`, `status`, `notes`); YAML is the prompt SSOT. Two different change cycles — TSV bumps compendium version, YAML doesn't.
- **`prompt:` as flat string, not structurally decomposed.** I kept proposing the prompt as "quote + clarifier" composition; Dan pulled to "the prompt is just a prompt — happens to start as the verbatim quote, but we're evolving our own prompts." No `clarifier:` slot in YAML. No concat logic. The Ralph-loop forward-look made this concrete: the loop edits one mutable string per row.

## Provisional Findings

- **Rubric distribution across the 181 v2 compendium rows** (from `awk` over `first_introduced_by` column):
  - `pri_2010_projection_mapping.md` — 81 rows (45%)
  - `focal_2024_projection_mapping.md` — 35 rows (19%)
  - `hiredguns_2007_projection_mapping.md` — 29 rows (16%)
  - `cpi_2015_c11_projection_mapping.md` — 18 rows (10%)
  - `sunlight_2015_projection_mapping.md` — 10 rows (6%)
  - `newmark_2017_projection_mapping.md` — 6 rows (3%)
  - `lobbyview_schema_coverage.md` — 1 row (LobbyView outlier)
  - `_tabled/opensecrets_2022_tabled.md` — 1 row (OpenSecrets-tabled outlier)
- **LobbyView outlier row:** `lobbyist_filing_distinguishes_in_house_vs_contract_filer`. Schema field, not a rubric question; needs a synthesized prompt, keyed in YAML as `lobbyview_2018_schema_field`.
- **OpenSecrets-tabled outlier row:** `separate_registrations_for_lobbyists_and_clients`. The tabled doc preserves a verbatim quote ("the baseline score was three and states that require separate registrations for the lobbyists and clients were assigned a four"); usable as-is, keyed as `opensecrets_2022_tabled`.
- **Pattern A's empirical surprise — partial pre-confirmation that the opaque-handle renderer is good design.** The narrow pass collapsed 14/14 Pattern A rows even with row_id still visible to the model. This says the verbatim quote + clarifier text was strong enough to dominate the row_id signal — i.e., a well-crafted prompt obviates the row_id even when the row_id is shown. Removing row_id from what the model sees is a cleaner contract but may not change measurable behavior much. WI re-dispatch will give us a clean comparison point on the same data.
- **Pattern noticed in session:** I proposed structurally elaborate solutions four times (clarifier slot in YAML, "quote + clarifier" derivation rule, rename mapping file, substantive rename-cleanup commit) and Dan pulled back to the flat-and-simple form each time. The corrections were load-bearing — each simplification eliminated a real future-friction point. Worth flagging for future design walks: when the right move feels under-structured, that's likely correct.

## Decisions Made

- **Wide pass goes ahead as option (a) from the handoff.** Skip the MI-dispatch and Pattern-C-split options for this session.
- **Sidecar YAML at `compendium/source_quotes.yaml`** as the prompt SSOT. Two fields per row: `source_quotes` (dict keyed by rubric+section ref, immutable reference material) + `prompt` (flat string, what the model sees, mutable).
- **No citations in the model-facing `prompt`.** Provenance lives in YAML keys.
- **No `clarifier:` slot, no decomposition.** `prompt:` is whatever string we want to send. Initially populated as the most relevant verbatim quote (a sensible starting point), then evolved freely.
- **Opaque-handle renderer.** `render_legal_roster` rewrites to send per-chunk handles (`row_001`, `row_002`, …) + prompt only; result parser maps handles → row_ids on receipt. Row IDs stay internal.
- **TSV `prompt_text` column dropped.** Runtime reads YAML directly. `CompendiumCellSpec` gets `prompt: str | None` populated from YAML at registry build time, not from TSV.
- **Outlier rows handled inline.** LobbyView row gets a synthesized prompt; OpenSecrets-tabled row gets the tabled-doc verbatim. No special schema flag.
- **Rename-cleanup commit demoted to optional/stylistic.** The Pattern A bug surface was "model sees row_id"; opaque handles fix that. Renames-for-human-readability remain available as low-priority follow-up but don't block the wide pass.
- **Re-dispatch sequencing after wide pass lands:** option (c) — re-dispatch WI as a cheap sanity check (~$2.50, ~20 min), then move to MI. Validates that 164-row scale doesn't surface new failure modes on a state we already know well.
- **Four-commit sequence for the wide pass.** (1) Renderer rewrite + YAML scaffolding. (2) YAML population. (3) WI re-dispatch + audit. (4) Optional stylistic-rename commit (deferred). See the plan doc.
- **Plan written:** [`../plans/20260604_wide_prompt_text_pass.md`](../plans/20260604_wide_prompt_text_pass.md).

## Results

No results files produced this session — pure design work. Numbers cited inline (rubric distribution, outlier row identities) came from direct queries over `compendium/disclosure_side_compendium_items_v2.tsv` and `docs/historical/compendium-source-extracts/results/_tabled/opensecrets_2022_tabled.md`; reproducible from those sources without an intermediate results file.

## Open Questions

- **Empirical question for WI re-dispatch (after wide-pass YAML lands):** does the opaque-handle renderer change anything measurable? Pattern A collapsed even with row_id visible, so removing it may not move the agreement metric. The interesting case is if some currently-passing row *fails* under the new renderer because we accidentally relied on row_id semantic leakage. Watch for new disagreements that weren't in the 18 original.
- **Ralph-loop readiness.** Once `prompt:` is the only string the model sees and the YAML is editable, a Ralph loop can iterate per row. Open: does the loop need a measurement harness scaffold (variant → dispatch → measure agreement → keep best)? Out of scope for this session, but the YAML-sidecar design is the prerequisite.
- **Compendium versioning question.** Wide-pass YAML populates `prompt:` for all 181 rows but doesn't add/remove/rename any. Is this still v2.1, or is it v2.2-prep? The v2.2 ledger has 4 entries; closing Entry 3 + Entry 4 in the YAML doesn't move the v2.1 → v2.2 line by itself. Provisional: stay on v2.1 unless the rename-cleanup commit happens (which would bump). Worth confirming during the implementation pass.
- **Multi-rubric prompt policy (future).** For the row read by 8 rubrics: is "show the model only `first_introduced_by`'s quote" optimal? Or would showing all 8 verbatim framings produce better extraction at higher token cost? Ralph-loop experiment territory; not blocking the wide pass.

---

## Carry-over status from 2026-06-03 handoff

- **Cumulative WI Tier-1 API spend:** $4.7504 (unchanged this session — no dispatches).
- **Wide pass:** scoped + planned; implementation deferred to next session per the plan doc.
- **MI dispatch:** still unblocked; deferred until after wide pass + WI re-dispatch.
- **Pattern C row-axis split (v2.2 Entry 2):** still open; no progress this session.
- **v2.2 ledger:** Entry 4's resolution path is now concrete (YAML structure subsumes it). Entry 3's wide-pass status updates after the plan executes.

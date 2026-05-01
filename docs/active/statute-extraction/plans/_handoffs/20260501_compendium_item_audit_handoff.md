# Handoff: Compendium item audit (axis-explicitness + curation fidelity)

**Status:** brief — the receiving agent should produce the actual plan in `docs/active/statute-extraction/plans/`.

## Why this is needed

Iter-1 of the statute-extraction harness (run on OH 2025 `definitions` chunk, 2026-05-01) surfaced a curation gap that had been invisible during the v2 audit (PR #5). The compendium row `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is target-axis (lobbying *directed at* admin agencies — does the lobbyist definition cover that?). Its description is target-axis-explicit ("contact with administrative... agencies as a registration trigger"), but its **name** alone is direction-ambiguous: a careful human reading the name reasonably mapped it to the actor axis (FDA staff lobbying Congress on behalf of FDA) — a separate question that the compendium correctly captures elsewhere via the PRI A-series in the `registration` domain (`REG_GOVT_LOBBYING_GOVT`, `REG_EXECUTIVE_AGENCY`, etc.).

In iter-1 the harness happened to read the description correctly (3-of-3 runs went target-axis), but the agent's brief did not show framework_references — meaning the agent had no axis-anchoring evidence beyond a single preposition in the description. That's a brittle signal. Worse, this gap was only caught because of inter-run disagreement on one regime; on a row where the model picks consistently, axis misreading would be wrong-but-unanimous and the harness has no way to detect it.

This audit's job is to catch axis ambiguity (and other curation gaps) **at curation time**, not via inter-run disagreement at extraction time. Iter-2 of the harness has been (or will be) shipped with a per-chunk preamble for `definitions` that names the three axes (target / actor / threshold) and points each row to one — that's a band-aid on the prompt side. The compendium-side fix needs to be authoritative.

## Scope

The audit covers all 141 compendium rows. For each row, evaluate:

1. **Name clarity** — does the row ID communicate the row's intent unambiguously, in particular w.r.t. axis (target / actor / threshold / process / cadence / etc.)? `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` is the exemplar of a name that doesn't.
2. **Description fidelity** — does the description express what the *source* rubric items were asking? This requires reading the source rubric items, and where the meaning isn't clear from the rubric CSV alone, pulling the source paper text (`papers/text/`) for context. Iter-1 only pulled descriptions; rubric meaning was never independently verified.
3. **Framework reference cohesion** — do all `framework_references` clustered under one row actually ask the same question? The v2 audit (per `docs/COMPENDIUM_AUDIT.md` Decision Log D1–D11) grouped by topic similarity; some clusters may contain axis-divergent items that should be split.
4. **Cross-row scope clarity** — are adjacent rows' axes explicit and non-overlapping? E.g., `DEF_ADMIN_AGENCY_LOBBYING_TRIGGER` (target) vs. `REG_EXECUTIVE_AGENCY` (actor) are intentionally separate but their names don't make that obvious. Audit should flag pairs/clusters where readers are likely to confuse the rows.
5. **Domain assignment** — is each row in the right `CompendiumDomain` (`definitions` / `registration` / `reporting` / `contact_log` / `financial` / `relationship` / `revolving_door` / `accessibility` / `enforcement` / `other`)? Iter-1 already revealed one: target-axis vs actor-axis questions about the same statutory machinery (admin-agency lobbying) sit in different domains intentionally — an auditor should confirm those splits hold across the full row set.

## Source materials

- `compendium/disclosure_items.csv` — 141 rows; truth source.
- `compendium/framework_dedup_map.csv` — per-rubric-item audit trail (which source items rolled into which compendium row).
- `papers/` (PDFs) and `papers/text/` (extracted text) — source rubrics: PRI 2010, FOCAL 2024/2026, Newmark 2005/2017, Opheim 1991, CPI Hired Guns 2007, Sunlight 2015, OpenSecrets 2022.
- `docs/COMPENDIUM_AUDIT.md` — v2 audit decision log (D1–D11), excluded-items table, coverage matrix.
- `docs/active/statute-extraction/results/iter-1_analysis.md` — iter-1 findings that surfaced this gap.
- `src/scoring/chunk_frames/definitions.md` — the iter-2 preamble (encodes the axis vocabulary; auditor should confirm or revise).
- `src/lobby_analysis/models/compendium.py` — the schema (currently lacks an explicit axis field; the audit may recommend adding one).

## Likely deliverables (the receiving agent decides specifics)

1. **An audit checklist per row.** Probably a CSV column or markdown matrix: row ID × axis assignment × name-clarity verdict × description-fidelity verdict × cross-row-conflicts × proposed action.
2. **A categorized punch list** of issues found: rename / tighten description / split into N rows / merge rows / move domain / add framework reference / drop framework reference.
3. **A schema recommendation.** Should `CompendiumItem` gain an explicit `axis` field (`target` / `actor` / `threshold_quantitative` / `threshold_qualitative` / `process` / `cadence` / `granularity` / `n/a`) for v1.4? If yes, this becomes a small schema bump with a migration; if no, the chunk-frame preambles carry the disambiguation alone.
4. **A sequencing proposal.** Compendium changes are load-bearing for tests, fixtures, and prior-run interpretability. The plan should chunk the audit into reviewable increments (probably one `domain` at a time, smallest first) with user review at each step.

## Constraints and conventions to respect

- **Row IDs are stable contracts.** Renames are possible but require migration of references across `tests/`, `data/extractions/` (run dirs reference IDs in raw_output.json), `compendium/framework_dedup_map.csv`, and any fixtures. The audit should propose renames in batches, not piecemeal.
- **Multi-rubric union must be preserved.** When splitting a row into two axes-distinct rows, the framework_references must redistribute (no item gets dropped); when merging, the dedup-map must be re-derived.
- **Don't add new rows from rubrics not already in the dedup map.** This audit is curation cleanup, not coverage expansion. Coverage expansion is a separate decision (it would be a v3 compendium audit, not the same scope).
- **Decision Log discipline.** Following the `docs/COMPENDIUM_AUDIT.md` D1–D11 pattern, every non-trivial choice (rename, split, merge, schema field add) should land as a numbered Decision in the audit's report doc.

## Out of scope

- Rewriting the source rubric papers themselves.
- Changing the harness scaffolding (prompt, brief renderer, orchestrator). Iter-2's chunk-frame preamble is a parallel concern; the audit may recommend additional preambles, but the audit itself is about compendium data, not harness code.
- Re-running iter-1 dispatch.
- Extension to states other than the priority 5–8.

## What "done" looks like

A plan doc (`docs/active/statute-extraction/plans/<DATE>_compendium_item_audit_v3.md`) that:

1. Defines the per-row audit checklist (criteria, evidence-gathering procedure, output format).
2. Proposes the schema change (or formally recommends not changing the schema), with rationale grounded in the v2 audit's prior decisions.
3. Sequences the audit into small reviewable chunks with user gates between them.
4. Identifies the first 5–10 highest-confidence issues from a quick spot-check (so the user can see the audit's value before approving the full sweep).

The receiving agent should treat the v2 audit (`docs/COMPENDIUM_AUDIT.md`) as the procedural template — the Decision Log style, the per-rubric walks, the excluded-items discipline. v3 is the same shape applied to a different question (axis explicitness + curation fidelity, vs. v2's coverage union).

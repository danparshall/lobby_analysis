# Retrieval Agent v2 Generalization — Brainstorm Convo

**Date:** 2026-05-14
**Branch:** extraction-harness-brainstorm
**Agenda followed:** [`../plans/20260514_retrieval_plan_sketch.md`](../plans/20260514_retrieval_plan_sketch.md)
**Predecessor in this session:** [`20260514_chunks_brainstorm.md`](20260514_chunks_brainstorm.md) — chunks decided per-cell-spec resolution + 15-chunk manifest. Retrieval may consume that.

## Session frame

This is the **third brainstorm-then-plan cycle on this branch** (cells → chunks → retrieval), per the user's session strategy: brainstorm + plan all 4 downstream components first with user-in-loop, then launch implementations as API sub-branches in parallel, merge back.

Retrieval is the "cleanest parallel work" per the kickoff handoff — it's a rewrite of v1's `src/scoring/retrieval_agent_prompt.md`, not a new build. Most of the substantive guidance survives; only the rubric-coupling sites (PRI A5-A11 / C0-C3 references and `rubric_items_affected` output schema) need v2 anchors.

## Phase 1 — Carry-forward reading

### v1 retrieval prompt (`src/scoring/retrieval_agent_prompt.md`)

Re-read end-to-end. **Rubric-coupling sites:**

1. **Rule 2 substantive anchor:** "...the definition of 'person' directly controls rubric items A5–A11 (whether government entities must register) and C0–C3 (public entity definition)." → v2 anchor needs to point at `actor_*_registration_required` chunk (11 cells) + `public_entity_def_*` + `law_defines_public_entity` (= 4 cells in `lobbying_definitions` chunk).
2. **Output JSON schema:** `rubric_items_affected: ["A5", "A6", "A7", ...]` → v2 replaces with `cell_ids_affected: [["actor_executive_agency_registration_required", "legal"], ...]` (or `chunk_ids_affected: ["actor_registration_required"]`).
3. **Rule 4 implicit reference:** "If the lobbying chapter says 'as required by [other section],' that other section contains information the scorer needs for E-series items." E-series in PRI is reporting/spending items → in v2, this maps to the `lobbyist_spending_report`, `principal_spending_report`, `lobbying_contact_log`, `other_lobbyist_filings` chunks. Either name the chunks or describe generically.

**Rubric-agnostic surfaces** (carry forward verbatim or with minor tightening):
- The two-hop limit + URL-construction-from-pattern logic.
- URL confidence levels (high/medium/low) + reasoning fields.
- `unresolvable_references` schema.
- The substantive category list (definitions / penalties / exemptions / cross-cited disclosure requirements) — these are universal cross-ref categories.
- The OH 2010 §311.005 example as a concrete grounding for the "general definitions act" pattern.

**Empirical anchor.** Iter-1 dispatched this v1 prompt against OH 2025 and successfully retrieved §311.005 ("person" definition) as a hop-1 cross-ref. The v2 rewrite shouldn't regress that behavior — the v2 cells driving the "person" retrieval are equivalent to PRI's A5-A11/C0-C3, just labeled differently.

### v2 cell inventory for retrieval-relevant cells

Of the 186 cells, the legal-axis cells (~131) are the ones that genuinely need statute cross-ref retrieval. Practical-axis cells (50 + the 5 combined-axis practicals = 55 cells) are about portal usability and don't need statute text — they're scored against portal screenshots, not statute text.

By chunk, legal vs practical mix:

| Chunk | Legal | Practical | Mixed (combined) |
|-------|-------|-----------|------------------|
| `lobbying_definitions` | 15 | 0 | 0 |
| `actor_registration_required` | 11 | 0 | 0 |
| `registration_thresholds` | 6 | 0 | 0 |
| `registration_mechanics_and_exemptions` | 6 | 0 | 2 (combined) |
| `lobbyist_registration_form_contents` | 13 | 0 | 0 |
| `lobbyist_spending_report` | 29 | 4 | 1 (combined) |
| `principal_spending_report` | 23 | 0 | 0 |
| `lobbying_contact_log` | 9 | 0 | 0 |
| `other_lobbyist_filings` | 12 | 0 | 0 |
| `enforcement_and_audits` | 0 | 0 | 2 (combined) |
| `search_portal_capabilities` | 0 | 16 | 0 |
| `data_quality_and_access` | 0 | 10 | 0 |
| `disclosure_documents_online` | 0 | 5 | 0 |
| `lobbyist_directory_and_website` | 0 | 9 | 0 |
| `oversight_and_government_subjects` | 2 | 6 | 0 |

**Implication:** 5 chunks (`search_portal_capabilities`, `data_quality_and_access`, `disclosure_documents_online`, `lobbyist_directory_and_website`, and arguably `oversight_and_government_subjects` if its 2 govt_agencies rows are minor) don't need statute retrieval at all. Per-chunk retrieval lets us short-circuit those.

## Phase 2 — Architectural decisions

(Filled in as the brainstorm resolves each Q.)

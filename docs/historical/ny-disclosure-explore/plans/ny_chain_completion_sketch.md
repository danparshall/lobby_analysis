# Plan sketch: complete the NY chain by integrating `parties_lobbied`

**Status:** Sketch, not implementation-ready. A future agent on this branch will refine + execute under TDD.

**Originating context:** Sketched 2026-06-06 on the `leave-behind-prep` branch as part of the fellowship-wrap take-stock work. See that branch's `docs/active/leave-behind-prep/RESEARCH_LOG.md` (2026-06-06 entry) and `docs/STATE_COVERAGE.md` NY section for the framing context. Triggered by Dan's request: "sketch a plan to complete the chain for NY; I'll have a future agent implement."

**Cost:** $0 (no LLM calls — all deterministic joins).

---

## Where things stand

Two shipped NY artifacts, both regenerable from the verified 2.32 GB 2025 client_semiannual pull:

1. **The chain:** `releases/ny/chain/NY_chain_2025.tsv` — 83,786 rows, `$153,064,191` conserved exactly. Built by `allocation/ny/chain.py`, joining `releases/ny/NY_clients.tsv` to the OS Plural Policy NY 2025-2026 bill-sponsorship bundle. **The "lawmaker" leg is INFERRED via bill primary sponsor — NOT disclosed contact.** Bill-match 99.9%, 213 distinct sponsors = full NY legislature.
2. **The disclosed-lawmaker edge:** `releases/ny/NY_filing_parties_lobbied.tsv` — 168,430 edges, 98.61% of state-legislator-titled rows resolve to `ocd-person` (after the 2026-06-06 nickname matcher), all 213 NY legislators covered. **This is the disclosed contact** — what NY actually requires the filer to report. Grain is per-filing SET; cannot recover per-(lawmaker, bill) tuples (Phase-0 gating finding: cartesian, not mapping).

These two artifacts are NOT yet joined. The chain has no awareness of which sponsor-inferred lawmakers are also disclosed-contacted, and `parties_lobbied` has no awareness of the chain's bill / money structure.

---

## What "complete the chain" means in this plan

**The minimum complete deliverable** = chain rows enriched with disclosed-contact metadata, so a consumer of `NY_chain_2025.tsv` can answer: "for this (filing, lobbyist) pair, which of the inferred sponsor-lawmakers are corroborated by disclosed contact in `parties_lobbied`, AND which lawmakers were disclosed-contacted but are NOT in the sponsor-inferred set?"

Crucially: **add, do not replace.** The inferred-via-sponsor lawmaker column stays. Disclosed-contact metadata layers on top. This preserves the chain's bill-grain conservation and lets downstream consumers choose which signal they want (or use both for validation).

**Explicitly NOT in scope** for this plan:
- DO NOT attempt to recover per-(lawmaker, bill) edges from `parties_lobbied`. Phase-0 gating already established this is cartesian-not-mapping. Future schema work might cover it; this plan doesn't.
- DO NOT introduce new chain rows for disclosed-but-not-sponsor lawmakers (e.g., leadership contacted but not sponsoring). Those exist in `NY_filing_parties_lobbied.tsv` as standalone rows already; keep them there. Adding NULL-bill rows to the chain breaks bill-keyed conservation.
- DO NOT replace the inferred-sponsor lawmaker column with disclosed-only. Consumers need both.
- DO NOT touch cosponsors, `lobbyist_bimonthly` fold-in, `target_kind` taxonomy for non-legislators, or multi-year backfill. Each is its own follow-on (see Phase 4 below).
- DO NOT cross-import from WI or OH code. Each state's chain is bespoke (Anna Karenina). The 2026-06-06 audit confirmed NY has zero cross-state imports today — preserve that.

---

## Phases

### Phase 0 — Grain join sanity check (gating, ~30 min)

**Goal:** confirm `(filing_id, lobbyist_id)` is a valid composite join key between the chain and `parties_lobbied.tsv`, and that the join geometry is what we expect.

**Steps:**
1. Load both TSVs. For each chain row, compute how many `parties_lobbied` rows share its `(filing_id, lobbyist_id)` — distribution of fan-out.
2. Compute: of the chain's 83,786 rows, what fraction have at least one resolved (`ocd-person`-tagged) disclosed lawmaker in the same `(filing_id, lobbyist_id)`?
3. Spot-check 5 filings end-to-end manually.

**Gating expectation:** `parties_lobbied` was 99.9%-populated on 2025 client_semiannuals, so the LEFT JOIN coverage should be ≥99%. **If <90% — STOP and root-cause before Phase 1.** That would indicate a grain mismatch (e.g., `parties_lobbied` is per-(filing, focus_identifying_number) and we need a different composite key).

**Output:** results doc `results/YYYYMMDD_ny_chain_pl_grain_check.md` with the fan-out distribution + join-coverage number.

---

### Phase 1 — Add disclosed-lawmaker column to chain (TDD, ~2-3 hrs)

**Goal:** chain rows gain a `disclosed_lawmakers` column (semicolon-joined `ocd-person` IDs from `parties_lobbied`, deduped per `(filing_id, lobbyist_id)`).

**TDD discipline:**
- RED: write tests against a small fixture (3-5 known filings, parties_lobbied IDs known by hand). Test that:
  - `disclosed_lawmakers` column appears in chain output
  - For a filing with N resolved disclosed lawmakers, every chain row for that (filing, lobbyist) has the same N IDs, semicolon-joined, sorted deterministically
  - For a filing with zero disclosed legislators (only unresolved entities), `disclosed_lawmakers` is empty string
  - Conservation `comp_per_cell` unchanged after adding the column (it's metadata — should be additive only)
- GREEN: extend `allocation/ny/chain.py` with a LEFT JOIN on `parties_lobbied`, grouped to `(filing_id, lobbyist_id)`, joined back to chain rows.
- REFACTOR: pull the disclosed-lawmakers loader into a sibling function (e.g., `_load_disclosed_contacts`) so the chain composer stays readable.

**Acceptance:**
- All existing NY chain tests still pass (regression — no row count change, no money change)
- New `disclosed_lawmakers` tests pass
- `$153,064,191` conservation verified post-regeneration

---

### Phase 2 — Add reconciliation columns (TDD, ~1-2 hrs)

**Goal:** per chain row, surface whether the inferred-via-sponsor lawmaker is corroborated by disclosed contact.

**Two new columns:**
- `sponsor_in_disclosed_set` (Boolean): is the chain row's `sponsor_person_id` (inferred from OS) present in the `(filing, lobbyist)`'s `disclosed_lawmakers` set?
- `disclosed_only_lawmaker_count` (Int): how many disclosed lawmakers for this `(filing, lobbyist)` are NOT in any chain row's `sponsor_person_id`? (This is the "leadership contacted but didn't sponsor" count — Heastie / Stewart-Cousins / Krueger / Gianaris signal.)

**TDD discipline:**
- RED: extend the Phase-1 fixtures with hand-known reconciliation expectations.
- GREEN: implement the per-row Boolean + per-(filing, lobbyist) leadership count.
- Test the leadership case explicitly — fixture with Heastie/Stewart-Cousins disclosed but no bills they sponsor in the filing → `sponsor_in_disclosed_set=False` on all chain rows for that filing, `disclosed_only_lawmaker_count` ≥ 2.

**Acceptance:**
- Reconciliation metrics computable from the new columns
- Regenerated `NY_chain_2025.tsv` reports a single aggregate metric in the regeneration log: "X% of chain rows have `sponsor_in_disclosed_set=True`" — this is the chain's disclosure-corroboration rate.

---

### Phase 3 — Regenerate + document (no TDD, ~30 min)

**Goal:** ship the enriched chain and update README.

**Steps:**
1. Regenerate `releases/ny/chain/NY_chain_2025.tsv` with the four new columns: `disclosed_lawmakers`, `sponsor_in_disclosed_set`, plus carry the per-(filing, lobbyist) `disclosed_only_lawmaker_count`.
2. Verify conservation: `$153,064,191` exactly.
3. Update `releases/ny/chain/README.md`:
   - Add column documentation (esp. the grain caveat: `disclosed_lawmakers` is a set per (filing, lobbyist), NOT per bill)
   - Add the disclosure-corroboration rate from Phase 2
   - Note that disclosed-only-no-sponsor lawmakers live separately in `releases/ny/NY_filing_parties_lobbied.tsv` (cross-link both ways)
4. Update `docs/STATE_COVERAGE.md` NY section to reflect the chain's new enriched state.

**Note on file size:** the chain is already 53 MB and trips GitHub's >50 MB warning per Dan's explicit call (release TSVs are gitignored on `ny-disclosure-explore` per commit `10adc78`). Phase 3 doesn't change that policy — at merge time, re-add with `git add -f` per the existing convention.

---

### Phase 4 — Deferred follow-ons (NOT in this plan, listed for visibility)

These are real next steps but each is its own scoped work, not part of "complete the chain":

- **`target_kind` taxonomy** for the ~42% non-legislator `parties_lobbied` rows (NYC municipal officials, executive offices, agencies, "entire-legislature" broadcasts). Currently all `resolved=False`. Adding a typed taxonomy makes those edges first-class.
- **Cosponsors integration.** OS bulk-CSV has cosponsors only in `bill_actions.description` text (not structured). Same shape as WI's deferral. Would extend the chain's `lawmaker ↔ bill` edge density.
- **`lobbyist_bimonthly` fold-in.** NY has a second filing type not yet pulled (~60M rows for 2025, ~5× the semiannual). Value-prop: individual-lobbyist names (semicolon-list in `individual_lobbyist_name`; semiannual only names firms), itemized expenses (`expense_type`/`expense_paid_to`/`expense_purpose`), finer bimonthly time grain. **Does NOT supply per-bill lawmaker tuples** — the 2026-06-07 grain probe ([`../results/20260607_ny_bimonthly_party_grain.md`](../results/20260607_ny_bimonthly_party_grain.md)) confirmed bimonthly's singular `party_name` is also cartesian at `(filing, focus)`, effective grain `(filing × focus × party × expense_event)`. Shipped `io/ny/parties` resolver hits 100% on bimonthly's `party_name` — zero resolver work owed. Cross-dataset double-count guardrail (GH #37) still owed before any comp merge.
- **Multi-year backfill (2019→).** Same NY pipeline, older vintages. Requires schema-drift handling per vintage.
- **Acquisition-library hardening** plan already exists separately on this branch: [`ny_acquire_paginate_verify.md`](ny_acquire_paginate_verify.md) — owed to a separate TDD agent.

---

## Open questions for Dan before implementation

1. **Phase 1 column name** — `disclosed_lawmakers` or `parties_lobbied_resolved` or something else? Went with `disclosed_lawmakers` because it names what the column semantically IS (the disclosed counterpart to the inferred-via-sponsor lawmaker column), not the source field's name. Open to override.
2. **Deterministic sort order** for the semicolon-joined IDs — ascending alphabetical on `ocd-person` ID? Or some semantic order (e.g., chamber then last name)? Default suggestion: alphabetical on `ocd-person` ID for determinism + diff-friendliness. Cheap to change later.
3. **Whether Phase 3 should also write a parallel "disclosed-only contacts" summary** alongside the chain — i.e., for each (filing, lobbyist), the list of disclosed lawmakers with no sponsor match. This is derivable from `parties_lobbied.tsv` ∖ chain projection, so arguably redundant — leaving out of scope by default.
4. **Whether to backfill metric onto `docs/STATE_COVERAGE.md` lobbyist↔lawmaker cell footnote** — the corroboration rate would be a useful third number alongside "98.61% resolved" and "213/213 legislators covered." Cheap to add in Phase 3.

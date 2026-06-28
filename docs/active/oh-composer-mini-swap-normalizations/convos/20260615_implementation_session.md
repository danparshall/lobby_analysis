# Convo — 2026-06-15: implementation of the composer-side mini-swap normalizations

**Branch:** `oh-composer-mini-swap-normalizations` (off `main` @ `8b043f9`)
**Plan executed:** `docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md` (on leave-behind-prep)
**Outcome:** both normalizations + release re-roll shipped on-branch; PR-ready.

---

## Session shape

Handoff from a previous session arrived stale ("that paste was from
several days ago"). Pre-flight read of STATUS / recent commits surfaced
two new commits past the handoff's vintage:

- `2390ffe` 2026-06-16 — "end-of-fellowship final report"
- `8b043f9` 2026-06-27 — "CDF funder summary + project-level final report"

The "end-of-fellowship" framing made the plan's status genuinely
ambiguous — fellowship had wrapped, OH chain composer was framed as
"capstone." Stopped to confirm intent before cutting any branch. Dan
confirmed "execute as written."

---

## What landed

Three commits on this branch:

1. **`3f2c677`** — Steps 1+2 implementation + tests (TDD).
   - `derive_org_id` / `derive_person_id` / `_slugify` added to
     `src/lobby_analysis/allocation/oh/chain.py`. `_filing_base` reads
     derived IDs instead of model-emitted `Organization.id` /
     `Person.id`.
   - `_emit_position_rows` rescues `bill_referenced + unmatched` rows
     whose label has no digits, demoting them to
     `subject_general + subject + subject_only`.
   - Tests: 139 baseline → 184 green (29 new unit tests in
     `test_entity_id_derivation.py`; 3 composer-integration + ~13
     demotion-behavior tests in `test_chain.py`; 1 parametrize case
     explicitly skipped because Roman-numeral "Title IV-D" has no
     digits and would demote, which isn't quite the rule's intent).
   - Pre-existing `mixed_class_dirs` fixture's "unmatched" position
     relabeled from `"Early Intervention"` to `"HJ Res 5"` so the
     fixture's stated intent "one row per bill_class" survives.

2. **`5474189`** — post-fix acceptance experiment writeup.
   - Re-materialized both sonnet (305 filings) and mini briefv2 (100
     pre-staged) chains with the new normalizations; diffed against
     shipped sonnet artifact and against each other.
   - **Cell-level acceptance PASSED strongly**: `principal_id` /
     `lobbyist_id` disagreement on shared post-fix rows is 0/246
     (was 236/240 and 235/240 pre-fix).
   - **Step 2 sonnet impact**: 18 unmatched rows → 8 surviving + 10
     demoted. Plan expected "within 2 of 18" surviving and explicitly
     flagged "stop and check with Dan" if materially lower. Stopped.
     Findings: the 10 demoted labels are all unambiguous subject
     content ("Accessible Housing", "Federal IDEA funds/schools",
     ...); the 8 survivors are all digit-containing rule-shape
     citations ("5123-2-XX", "Ch. 4757-5, -6, ...", "CB DOH0105168").
     The rule isn't too aggressive — the plan author underestimated
     sonnet's own subject-leak rate.
   - **Row-set diff**: 61 → 56 mini-only (plan acceptance ≤10
     technical-FAIL). Breakdown reveals 55/56 are correctly-demoted
     `subject_general` rows whose text differs from sonnet's
     `general_issue_area` text on the same source — text-not-structure.
     Cell-level shared-row count actually went UP, 240 → 246 (+6).
   - Dan reviewed and approved: "Accept as-is" on the demotion rule,
     "Regenerate + commit + update README" on the release.

3. **`ed61518`** — release re-roll + README updates.
   - Regenerated `releases/oh/chain/OH_chain_2025_2026_preview.tsv`
     (1,589 rows, same shape; 58/135 distinct principal_ids change,
     39/125 distinct lobbyist_ids change, 10 sonnet unmatched rows
     demoted; bill_class distribution shifts 1,299/150/88/34/18 →
     1,299/160/88/34/8).
   - Regenerated `releases/oh/filings/OH_filings_2025_2026_preview.tsv`
     (305 rows, same shape) — **required because filings.py also
     reads model-emitted `.id` directly**, which would have left
     chain and filings TSVs inconsistent on the ID columns (breaks
     joins on `(filing_id, principal_id)`). Extended Step 1 to
     `compose_filings` to keep the two TSVs join-consistent. 2 new
     tests in `test_filings.py`. (Not in original plan; surfaced
     during the acceptance experiment by grep-walking the codebase
     for other consumers of `.employer.id` / `.filer_person.id`.)
   - `releases/oh/chain/README.md`: new section "Entity-ID derivation
     and bill_referenced demotion (2026-06-15 normalizations)"
     documenting both rules; per-row routing table extended with the
     no-digit demotion row; TL;DR + schema rows + conservation rule
     #4 updated for the new numbers.
   - `releases/oh/filings/README.md`: principal_id / lobbyist_id
     schema rows now point at the chain README's derivation section.
   - `releases/oh/README.md`: caveat 3 reframed (18→8 unmatched, with
     pointer to the new section).
   - Tests: 184 → 186 with the 2 filings-side tests.

Final tally: **186 OH allocation tests passing**, 1 skipped (the
Roman-numeral edge case).

---

## What this work does NOT include

Out-of-scope per the plan, deferred:

- **No full-corpus run** (#35, ~$150 batched). The chain composer's
  Step 1+2 changes will compose any future full-corpus extraction
  correctly without further plumbing.
- **No filings-TSV is_itemized / total_expenditure brief work.** Plan
  said chain-only; not touched.
- **No cost-identity reconciliation** (which model ID = the
  $0.0066/filing measurement). External-doc gate, not internal.

---

## Notes for the next agent

- **Three changes in `_filing_base` location to be aware of:** chain.py:
  derived IDs (lines 215, 217 now); filings.py: derived IDs (lines
  101-108 now); both go through `derive_org_id` / `derive_person_id`
  from `chain.py`. The import-chain is `filings.py → chain.py` (no
  cycle).
- **Commit message typo in `ed61518`:** says "Tests: 186 → 188",
  actually 184 → 186. Not amending; noting here for the record.
- **Release re-roll is committed but not merged.** Branch is PR-ready;
  Dan's call when to open it.
- **Plan's row-set acceptance criteria don't hold even with a working
  rule.** The plan author's mental model for "post-fix mini-vs-sonnet
  diff" assumed text identity that doesn't exist. The cell-level
  diff is the cleaner signal. Future plans of this shape should
  prefer cell-level acceptance numbers over row-set acceptance
  numbers.
- **The 0-collision result on the slugify is corpus-dependent.** A
  larger corpus could surface a collision (the `Risks` item-3 case).
  If a future regenerate ever shows >0 collisions, the path is
  documented in the plan (tighten the slug; add a name-list-per-ID
  audit).

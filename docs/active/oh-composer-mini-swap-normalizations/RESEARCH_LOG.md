# RESEARCH_LOG — oh-composer-mini-swap-normalizations

Newest entries first.

This branch executes the composer-side mini-swap normalizations plan
authored 2026-06-15 on `leave-behind-prep`. Scope: two composer-side
normalizations that close ~95% of the residual chain-row diff between
mini-sourced and sonnet-sourced OH chains, with no new API spend and no
re-extraction.

**Originating plan:** [`leave-behind-prep` → `plans/20260615_composer_side_mini_swap_normalizations.md`](https://github.com/danparshall/lobby_analysis/blob/leave-behind-prep/docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md)
**Originating findings:** [`leave-behind-prep` → `results/20260615_mini_swap_chain_level_evidence.md`](https://github.com/danparshall/lobby_analysis/blob/leave-behind-prep/docs/active/leave-behind-prep/results/20260615_mini_swap_chain_level_evidence.md)
**Originating convo:** [`leave-behind-prep` → `convos/20260615_mini_swap_chain_level_experiment.md`](https://github.com/danparshall/lobby_analysis/blob/leave-behind-prep/docs/active/leave-behind-prep/convos/20260615_mini_swap_chain_level_experiment.md)

The plan, findings, and convo live on the `leave-behind-prep` branch
rather than being copied here, to keep that branch as the canonical home
for the experiment that produced them. This branch carries only the
implementation work + a session-summary convo per the researcher
workflow.

---

## 2026-06-15 — Phase 1 + Phase 2 implementation landed (TDD)

**Branch:** cut off `main` @ `8b043f9` (post-fellowship-final-reports).
**Tests:** 139 OH allocation tests on main as baseline → 184 passed,
1 skipped after both phases (Phase 1 added 29 unit tests + 3 composer-
integration tests; Phase 2 added ~13 demotion-rule tests, 1
parametrize case explicitly skipped because Roman numerals would
otherwise demote unintentionally; one existing fixture position
updated).

### Phase 1 — deterministic entity-ID derivation (plan §"Step 1")

`derive_org_id` / `derive_person_id` / `_slugify` added to
`src/lobby_analysis/allocation/oh/chain.py`. `_filing_base` now derives
`principal_id` and `lobbyist_id` from the corresponding name rather
than reading the model-emitted `Organization.id` / `Person.id`. The
LobbyingFiling schema is untouched — derivation is composer-time, not
parse-time, per the plan's "Composer is the right seam, not the
schema" risk note.

Slug algorithm: NFKD-normalize → ASCII-fold → lowercase → replace any
run of non-alphanumerics with a single hyphen → strip leading/trailing
hyphens. Empty input → `None` (no `org-`/`person-` prefix attached to
nothing).

### Phase 2 — no-digit demotion of unmatched bill_referenced rows (plan §"Step 2")

`_emit_position_rows` in `chain.py` rescues `bill_referenced +
unmatched` positions whose label contains no digits, demoting them to
`subject_general + subject + subject_only`. The demotion happens
between `classify_bill_label` and the downstream non-bill emission
branch so that `_position_description_for` and `norm_label`
computation see the (possibly updated) kind. Digit-containing
unmatched rows (e.g., `'HJ Res 5'`) are preserved as unmatched to
keep the genuinely-malformed-bill audit signal.

Existing `mixed_class_dirs` fixture in `tests/allocation/oh/test_chain.py`
updated: the "unmatched" position's bill_reference changed from
`"Early Intervention"` to `"HJ Res 5"` so the fixture's stated intent
(one row per bill_class) is preserved after the demotion rule lands.

### Acceptance criteria status (final)

Plan §"Acceptance criteria (whole plan)":

1. ✅ Step-1 + Step-2 tests pass (TDD ground state).
2. ✅ Existing OH allocation tests still green (139 → 186 with new tests).
3. ✅ Re-run the 2026-06-15 experiment end-to-end — see
   [`results/20260615_post_fix_acceptance.md`](results/20260615_post_fix_acceptance.md).
   Cell-level acceptance (principal_id / lobbyist_id 0/246) **PASSES strongly**.
   Two of the plan's row-set acceptance numbers came in different
   from estimate; Dan reviewed and accepted as-is (rule is correct;
   plan author's mental model for those two numbers was wrong, not
   the rule).
4. ✅ Regenerated `releases/oh/chain/OH_chain_2025_2026_preview.tsv` +
   `releases/oh/filings/OH_filings_2025_2026_preview.tsv` (commit
   `ed61518`). The filings TSV regen was an in-scope extension
   surfaced during the acceptance experiment — `filings.py` also
   read model-emitted `.id`s, so leaving it untouched would have
   broken `(filing_id, principal_id)` joins between the two TSVs.
   Step 1 mirrored into `compose_filings` + 2 new tests.
5. ✅ Updated `releases/oh/chain/README.md` (new section "Entity-ID
   derivation and bill_referenced demotion"), plus
   `releases/oh/filings/README.md` and `releases/oh/README.md` for
   consistency.
6. ✅ Convo doc at [`convos/20260615_implementation_session.md`](convos/20260615_implementation_session.md).

**Branch status:** PR-ready; not yet merged. Dan's call when to open it.

**Commits on branch:**

- `3f2c677` — Steps 1+2 implementation + tests
- `5474189` — post-fix acceptance experiment writeup
- `ed61518` — release re-roll + filings.py mirror + README updates

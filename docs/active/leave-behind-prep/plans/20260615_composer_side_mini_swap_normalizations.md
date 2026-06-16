# Plan — composer-side normalizations for the mini-swap

**Originating findings:**
[`results/20260615_mini_swap_chain_level_evidence.md`](../results/20260615_mini_swap_chain_level_evidence.md)
**Predecessor findings:**
[`results/20260613_mini_swap_quality_gate_findings.md`](../results/20260613_mini_swap_quality_gate_findings.md)
**Originating convo:**
[`../convos/20260615_mini_swap_chain_level_experiment.md`](../convos/20260615_mini_swap_chain_level_experiment.md)
**Branch this plan was authored on:** `leave-behind-prep`
**Branch the implementation should run on:** see "Operational notes" below.

---

## Why this plan exists

The 2026-06-15 chain-level experiment showed that **briefv2 mini is
operationally equivalent to sonnet on LUPA AERs at the chain-row
level** — same position count, same bill resolution, zero
disagreement on sponsor edges. The remaining diff against sonnet is
two composer-side conventions, both deterministically closable
without a brief change or any new API spend.

**Implementing both normalizations should close ~95% of the residual
chain-row diff between mini and sonnet, with no new API spend and no
re-extraction.**

This plan is the actionable continuation of the findings doc. The
findings doc supersedes Q1 of the 2026-06-13 provisional findings (the
description-hoist that was Q1 turned out to be already in place; the
*actual* slot mismatch is the opposite direction, addressed in Step 2
below).

---

## Goal

Land two composer-side normalizations in
`src/lobby_analysis/allocation/oh/` such that:

1. **Entity IDs are derived deterministically from names**, not taken
   from the model-emitted `Organization.id` / `Person.id` schema
   fields. Closes the 97.9% / 98.3% `lobbyist_id` / `principal_id`
   disagreement on shared chain rows.

2. **Unmatched bill_referenced rows whose label contains no digits get
   demoted to `subject_general`.** Closes 59 of mini's 61 row-set diff
   ("mini-only" bucket) while preserving the audit signal for sonnet's
   18 genuinely-malformed-bill rows.

Both fixes are model-asymmetric in their measured impact (mini benefits
much more than sonnet), but **must be applied uniformly to both
models** — they are general composer policy, not a "fix mini to look
like sonnet" hack. The release artifact's `principal_id` /
`lobbyist_id` and bill-class distributions will change for both
sonnet-sourced and mini-sourced chains.

**Design consequence to surface:** the shipped sonnet chain artifact
(`releases/oh/chain/OH_chain_2025_2026_preview.tsv`, PR #59) would have
different `principal_id` / `lobbyist_id` columns after Step 1 lands.
The `_preview` suffix gives us license to change the convention, but
this is worth flagging to Dan before merging.

---

## Operational notes — branch state

**Code location:** the OH chain composer lives at
`src/lobby_analysis/allocation/oh/{chain,classify,load,filings,gifts,cli}.py`
on `main` (shipped 2026-06-15 via PR #59, `ac009f5`).

**Plan-authored-on branch (`leave-behind-prep`) does NOT have this code** —
it is ~90 commits behind main as of 2026-06-15. The implementing agent
should NOT attempt to land these changes on `leave-behind-prep`.

**Recommended implementation branch:** cut a new branch off `main`,
e.g. `oh-composer-mini-swap-normalizations` (or whatever name fits the
prevailing convention; the per-workstream branch pattern is the norm).
Reference this plan doc from the new branch's `RESEARCH_LOG.md`.

**Tests already in place** to inherit / extend:
- `tests/allocation/oh/test_classify.py` — Step B (`classify_bill_label`)
  unit tests. The demotion rule in Step 2 below extends this surface.
- `tests/allocation/oh/test_chain.py` — composer-level tests with
  fixture filings. Step 1's entity-ID derivation needs new tests here.
- `tests/allocation/oh/test_load.py` — loader tests.

**Per CLAUDE.md**, this branch is implementation work, so the
implementing agent should follow TDD: write the failing test first,
then the minimal code to pass.

---

## Step 1 — Entity-ID derivation from name

### Current behavior

`src/lobby_analysis/allocation/oh/chain.py:147-150` reads
`principal_id` and `lobbyist_id` directly from the
`LobbyingFiling.employer.id` and `LobbyingFiling.filer_person.id`
schema fields — i.e., the value emitted by the LLM during extraction.
Sonnet uses a (mostly) stable kebab-case convention; mini does not.

### Desired behavior

Both fields are derived deterministically from the corresponding
**name** field, with a stable slug algorithm. Model-emitted
`id` fields are ignored at composer time (still stored in
`filing_obj` for audit purposes — do NOT mutate the LobbyingFiling).

### Algorithm

```python
import re
import unicodedata

def derive_org_id(name: str | None) -> str | None:
    """Derive a deterministic chain-time organization ID from a name."""
    if name is None or not name.strip():
        return None
    return f"org-{_slugify(name)}"

def derive_person_id(name: str | None) -> str | None:
    """Derive a deterministic chain-time person ID from a name."""
    if name is None or not name.strip():
        return None
    return f"person-{_slugify(name)}"

def _slugify(s: str) -> str:
    # ASCII-fold (strip accents), lowercase, non-alphanumerics → hyphens,
    # collapse runs of hyphens, strip leading/trailing hyphens.
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lower = ascii_only.lower()
    hyphenated = re.sub(r"[^a-z0-9]+", "-", lower)
    return hyphenated.strip("-")
```

### Where to land it

Add the two derivation functions + slugify helper at the top of
`src/lobby_analysis/allocation/oh/chain.py` (above
`_filing_base`). In `_filing_base`, replace lines 148 and 150 with:

```python
principal_id = derive_org_id(principal_name)
lobbyist_id = derive_person_id(lobbyist_name)
```

(Note: `principal_name` and `lobbyist_name` are already computed on
the lines above.) The model-emitted `.id` reads disappear.

### Tests required (TDD-first)

In `tests/allocation/oh/test_chain.py` (or a new
`test_entity_id_derivation.py` next to it):

1. **Basic kebab-case derivation** — `"Cleveland Browns"` → `"org-cleveland-browns"`.
2. **Punctuation handling** — `"Coinbase, Inc."` → `"org-coinbase-inc"`.
3. **Accented characters** — `"Café Société"` → `"org-cafe-societe"`.
4. **Empty / whitespace input** — `None` → `None`; `""` → `None`; `"  "` → `None`.
5. **Composer integration** — fixture `LobbyingFiling` with
   `employer.name="AAA Club Alliance Inc"` and `employer.id="garbage-id"`;
   chain row has `principal_id == "org-aaa-club-alliance-inc"`.
6. **Person derivation** — `"Jane Doe"` → `"person-jane-doe"`.

### Acceptance check (re-run the experiment)

After Step 1 lands, restage briefv2 mini outputs and re-run the
composer; the diff against the new sonnet-sourced chain (also
regenerated) should show:

- `lobbyist_id` disagreements: 0 of 240 (was 235/240).
- `principal_id` disagreements: 0 of 240 (was 236/240).
- All other cell-level columns unchanged.

The regenerated `releases/oh/chain/OH_chain_2025_2026_preview.tsv`
will have all new `principal_id` / `lobbyist_id` columns vs the
existing shipped file. This is expected.

---

## Step 2 — Bill_referenced-unmatched demotion

### Current behavior

`src/lobby_analysis/allocation/oh/classify.py:classify_bill_label`
returns `unmatched` for any `bill_referenced` row whose label doesn't
match the HB/SB/JC/OAC patterns. The composer keeps these rows in the
chain as `position_kind=bill_referenced + bill_class=unmatched` with
`bill_id=None`. The design intent (per classify.py docstring) is to
surface malformed bill references in audit rather than silently drop
them.

This was a sonnet-tuned design: sonnet's unmatched rate is 1.2%
(18/1,468 over the 305-filing chain). Mini's unmatched rate is 14.2%
(59/416 over the 100-filing chain) — an order of magnitude higher,
because mini puts policy/regulatory subjects into the `bill_reference`
slot instead of `general_issue_area`.

### Desired behavior

When a position is `bill_referenced` but classifies as `unmatched`,
inspect the `bill_reference.original_text`. If it contains **no
digits**, demote the row to `subject_general` with the text as the
subject content. If it contains digits, keep it as
`bill_referenced + unmatched` (preserves the malformed-bill audit
signal).

**Rationale for the digit check:** every real OH bill, OAC rule, or
JCARR citation contains digits (`HB 96`, `5160-46-01`, `JC 4731-24-03`).
A label with no digits is structurally incapable of being a
bill/rule/jcarr citation, so demoting is safe. Subjects like "Issue 3"
or "Chapter 4" that happen to contain digits would remain in the
unmatched bucket — false-positive rate worth measuring in the
acceptance check but expected to be low.

### Where to land it

The cleanest seam is at the position-emission boundary in
`src/lobby_analysis/allocation/oh/chain.py:_emit_position_rows`,
*after* `classify_position_shape` and `classify_bill_label` have run.
If both return `bill_referenced` + `unmatched` and the label has no
digits, re-route the position through the `subject_general` branch.

Pseudocode:

```python
def _emit_position_rows(base, position, bills_by_norm, spons_by_bill_id):
    kind = classify_position_shape(position)
    label = extract_position_label(position)
    bill_class = classify_bill_label(label, kind)

    # Composer-side rescue: demote no-digit unmatched bills to subjects.
    if (
        kind == POSITION_KIND_BILL_REFERENCED
        and bill_class == BILL_CLASS_UNMATCHED
        and not re.search(r"\d", label)
    ):
        kind = POSITION_KIND_SUBJECT_GENERAL
        bill_class = BILL_CLASS_SUBJECT

    # ... existing emission logic uses the (possibly demoted) kind + bill_class
```

The classify.py module is pure (no I/O); the demotion belongs in
chain.py rather than classify.py to keep classify.py's signature pure
(it shouldn't need to peek at digit content as a side-channel).
Alternatively: add a small `demote_unmatched_if_no_digits(kind,
bill_class, label) -> (kind, bill_class)` helper in classify.py and
call it from chain.py — both are defensible; pick what the existing
code style suggests.

### Tests required (TDD-first)

In `tests/allocation/oh/` (extend `test_classify.py` if you add the
helper there, or add to `test_chain.py` for the integration path):

1. **No-digit demotion**: `bill_reference.original_text =
   "Competency Restoration"`, `position_kind=bill_referenced`,
   `bill_class=unmatched` → demoted to
   `subject_general + subject`.
2. **Digit preserved**: `bill_reference.original_text = "HJ Res 5"`
   that doesn't match `_BILL_PATTERN` (no HB/SB prefix) but contains
   a digit → stays as `bill_referenced + unmatched` (malformed-bill
   audit signal preserved).
3. **Real bill not affected**: `bill_reference.original_text =
   "HB 96"` → `bill_referenced + bill` (existing behavior, no
   change).
4. **Real OAC rule not affected**: `bill_reference.original_text =
   "5160-46-01"` → `bill_referenced + oac_rule` (existing behavior).
5. **subject_general not affected**: `general_issue_area = "Budget"`,
   no bill_reference → `subject_general + subject` (existing
   behavior, demotion rule shouldn't fire).
6. **Whitespace-only stays unmatched**: `bill_reference.original_text
   = "   "` → existing classify_bill_label returns unmatched; new
   demotion check sees no digits but also no content; defer to whatever
   downstream behavior was (probably stays as unmatched; verify and
   document).

### Acceptance check (re-run the experiment)

After Step 2 lands, restage briefv2 mini outputs and re-run the
composer; the diff against the regenerated sonnet chain should show:

- Mini-only rows in the row-set diff: drops from 61 to ~7 (the 4
  bill_referenced + bill / oac_rule + 5 subject_general rows survive;
  2 subject_hoisted survive).
- Mini chain `bill_class=unmatched` count: drops from 59 toward ~few
  (any rows where the bill_reference text genuinely contains digits
  that aren't real bills — measure this; if it's >5 the rule may
  need tightening).
- Sonnet chain `bill_class=unmatched` count (over 305 filings):
  drops from 18 to whatever fraction of those 18 don't contain
  digits. Measure this — if it drops significantly, the rule is too
  aggressive and we'd be losing the malformed-bill audit signal in
  sonnet's case. **If this number is materially lower than 18, stop
  and check with Dan before proceeding.**

---

## Acceptance criteria (whole plan)

1. **Step-1 tests + Step-2 tests pass** (TDD ground state).
2. **Existing OH allocation tests still green** (139/139 from the
   pre-merge state; the additions shouldn't regress anything).
3. **Re-run the 2026-06-15 experiment end-to-end:**
   a. Restage briefv2 mini outputs (`scripts/stage_briefv2_mini.py` —
      move the script from `/tmp/stage_briefv2_mini.py` if useful, or
      re-derive).
   b. Run composer on staged dir, write to a tmpdir.
   c. Run the diff scripts (move from `/tmp/diff_*` to `scripts/`
      if useful).
   d. **Acceptance numbers** (compared to the 2026-06-15 pre-fix
      baselines documented in the findings doc):
      - `principal_id` / `lobbyist_id` cell disagreement: 0 / 240
        (was 236 / 235).
      - Mini-only row-set diff: ≤ 10 rows (was 61).
      - Sonnet-only row-set diff: ≤ 50 rows (was 48; should be stable
        — the subject_general rows aren't touched by either fix).
      - Sonnet's overall `bill_class=unmatched` count (305 filings):
        within 2 of 18 (= digit-containing residue; if much lower,
        the demotion rule is too aggressive — see Step 2 acceptance
        check).
4. **Regenerate `releases/oh/chain/OH_chain_2025_2026_preview.tsv`**
   from the sonnet baseline using the patched composer. The columns
   `principal_id` / `lobbyist_id` will differ from the existing
   shipped file. Audit the diff manually before commit; surface to
   Dan for sign-off (it's a release-data change).
5. **Update the chain README** (`releases/oh/chain/README.md`) to
   document the entity-ID derivation convention (`org-{slug}` /
   `person-{slug}`) and the demotion rule. Cite this plan and the
   findings doc.
6. **Write a convo doc + RESEARCH_LOG entry** on the implementing
   branch summarizing the implementation + the post-fix numbers from
   step 3d.

---

## Out of scope (do NOT do in this plan)

- **Brief revision (briefv4).** The chain-level evidence shows
  briefv2 is sufficient; brief work would be needed for the filings
  TSV's `is_itemized` / `total_expenditure` conventions, not the
  chain TSV.
- **Full-corpus run (#35 Batches API).** Separate ticket; ~$150
  batched / ~$300 sync; orthogonal to this plan.
- **Q4 39-rid is_itemized-by-template follow-up.** Useful for a
  Suhan-facing filings doc; not required for chain ship-readiness.
- **Cost-identity reconciliation** (which model id = the $0.0066
  measurement). Required before any external dollar figure; not
  required for the composer changes here.
- **OAC granularity decision (Q5 from 2026-06-13 doc).** Whether the
  composer wants rule-level OR rolled-up granularity for the
  OAC/JCARR edge is Dan's call; not in scope here. Both mini and
  sonnet rows in that bucket pass through the composer unchanged.
- **Amendment-path / `is_current` corpus sweep.** Documented stub in
  the findings doc; live slice has zero amendments so unobservable.

---

## Risks / known gotchas

1. **Regenerating the shipped chain artifact will change
   `principal_id` / `lobbyist_id` columns** for *every* row. Any
   downstream consumer that uses those IDs as a join key will break.
   The `_preview` suffix gives license; surface to Dan before merge.
2. **The digit-check escape hatch in Step 2 is heuristic.** Subjects
   like "Issue 3" or "Title IV-D" contain digits and would stay as
   `bill_referenced + unmatched`. Acceptable false-positive rate
   pending the acceptance-check measurement. If meaningful, tighten
   to "must look like HB/SB-shape pattern."
3. **`derive_org_id` collision risk:** two organizations whose names
   slugify to the same value (e.g., "AAA, Inc." and "AAA Inc.") would
   collapse to one ID. The model-emitted IDs had the same risk in
   principle. Worth a one-off check during acceptance — count
   distinct names per derived ID and flag any > 1.
4. **Composer is the right seam, not the schema.** Do NOT change
   `LobbyingFiling.employer.id` to derive at parse time — the schema
   should faithfully reflect what the model emitted. Derivation
   happens at the chain-composition boundary, not extraction.
5. **`_PREVIEW_SUFFIX` is hard-coded** in `cli.py`; if Step-3 of the
   acceptance check writes to a tmpdir, the file name is still
   `OH_chain_2025_2026_preview.tsv`. Don't be surprised.
6. **No `oh.csv` legislator roster in the acceptance experiment**
   means gifts edges resolve without lawmaker IDs. The chain TSV
   doesn't depend on this (gifts is a separate TSV, and gifts rows
   were 0 in the prior runs anyway). Confirm gifts remains 0 after
   Step 2's demotion rule (it shouldn't be affected, but check —
   `BILL_CLASS_UNMATCHED` is bill-side, not gift-side).

---

## After completion

- This plan closes when steps 1-3 of the acceptance criteria pass
  and the regenerated chain artifact lands on main via PR. Steps 4-6
  are post-merge hygiene.
- The findings doc's "decision recommendation" is updated to
  reflect the locked state (no longer provisional).
- Reference back from the plan doc's RESEARCH_LOG entry to this
  plan + the findings doc + the 2026-06-13 predecessor.
- Filings TSV / is_itemized / full-corpus questions remain open;
  they belong on separate workstreams, not this plan.

---

## Suggested rough sequence for the implementing agent

1. Cut branch off main; seed `docs/active/<branch>/` skeleton
   (`RESEARCH_LOG.md`, `convos/`, `plans/`, `results/`); reference
   this plan from the new RESEARCH_LOG.
2. TDD Step 1 (entity-ID derivation): write 6 failing tests, implement
   the derivation helpers + the `_filing_base` swap, watch all green.
3. TDD Step 2 (demotion rule): write 6 failing tests, implement the
   demotion in `_emit_position_rows`, watch green. Verify 139 OH
   allocation tests still pass.
4. Restage briefv2 mini outputs; re-run composer; run the diff
   scripts; record the post-fix numbers.
5. Regenerate the sonnet chain artifact; diff against the shipped
   file; surface the column-level changes to Dan.
6. Update `releases/oh/chain/README.md` with the new conventions.
7. Convo doc + RESEARCH_LOG entry; commit; PR.

**Estimated wall:** half a day, $0 spend.

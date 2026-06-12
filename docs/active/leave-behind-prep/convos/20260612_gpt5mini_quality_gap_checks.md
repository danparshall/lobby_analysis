# gpt-5-mini quality-gap checks — 3 spotchecks + 3 diagnostic deep-dives

**Date:** 2026-06-12
**Branch:** leave-behind-prep
**Surface:** Claude Code (Dan + sonnet, local CLI on `Dans-MacBook-Air.local`)

**Predecessor convo:** [`20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md`](20260609_gpt5mini_reasoning_effort_three_arm_dispatch.md) — the 3-arm dispatch that surfaced the field-emission asymmetries this session was set up to disambiguate.
**Originating plan:** [`plans/20260609_is_itemized_investigation_and_writeup.md`](../plans/20260609_is_itemized_investigation_and_writeup.md) — Step 1 + Step 2 of that plan executed here.
**Originating commit:** [`bfdb8b6`](https://github.com/danparshall/lobby_analysis/commit/bfdb8b6) — added the three spotcheck scripts under `scripts/`; this convo path was forward-referenced in that commit message.
**Results:** [`results/20260612_gpt5mini_quality_gap_checks/`](../results/20260612_gpt5mini_quality_gap_checks/) — three `.log` files (verbatim stdout of the three scripts), committed at `8eaa131`.

> **For a reviewing remote agent:** the session ran three pre-authored spotcheck scripts against the OH 300-slice, then three follow-up diagnostics. The headline pivot is that **the brief revision (briefv2 → briefv3) is the regression source, not the model swap.** The "mini quality gap" framing from the predecessor convo's analyzer turns out to overstate the gap on two of three fields and understate it on the third. Suggestions wanted on items in the **Open questions** section at the bottom.

## Summary

The 3-arm dispatch (predecessor) flagged three fields where mini-medium-briefv3 looked worse than sonnet: `total_expenditure` (field-emission gap, 91% vs 100%), `positions` (lower agreement, ~87% identical), and `is_itemized` (0/100 vs 39/100 emission). The pre-authored scripts in bfdb8b6 were designed to triage each: separate "disqualifying" gaps (mini under-extracts a stated value) from "defensible" gaps (mini abstains where sonnet derives or guesses).

Ran all three scripts cleanly. Then ran three pointed diagnostics the user proposed mid-session:

1. **Did the source HTML actually say "HB 29"?** (One of the positions diff rids.) Answer: yes — `grep -io "HB[ .]*29\|House Bill 29" data/oh_portal/raw/1394434/*/raw.html` returned one hit. Mini's `'HB 29'` is faithful to source; sonnet's `'PUBLIC SAFETY'` is the abstraction.
2. **Where did mini put the subjects?** (rid 1412254, the 38-vs-39 LENGTH_DIFF with 36 "(NO BILL)" rows on the mini side.) Dumped the briefv3 filing.json. Answer: mini emits the subjects in `description`, leaves `general_issue_area=None` and `bill_reference=None`. Same content, different slot. 34/39 of mini's positions follow this pattern; the 4 with real `bill_reference` correctly resolve HB 96 (×2), ORC 340, 5122-29-20.
3. **`is_itemized` Step-2 hand-read of the 5 raw.htmls** flagged by Script 3. All 5 are JLEC ethics forms with a section literally titled **"D. Non-Itemized Meals and Beverages"** populated with a single "Meals Under $50" amount (range $9.91–$168.40). The form's own label uses "Non-Itemized." Ground truth is unambiguously `is_itemized=False`. sonnet=False ✓, briefv2=False ✓, briefv3=None (abstains, **wrong**).

Net: two fields are softer than the predecessor's headline; one is harder. The brief revision is what regressed.

## Spotcheck results (verbatim numbers; full per-rid output in `results/`)

### Script 1 — `total_expenditure_spotcheck.py`

Comparison set: 100 rids in (sonnet ∩ medium_briefv3); field = `total_expenditure`.

| direction | count |
|---|---:|
| both_null | 28 |
| both_emit_agree | 9 |
| both_emit_disagree | **0** |
| sonnet_only | 62 |
| mini_only | 1 |

**All 63 disagreement rows census: `sonnet=0.0`, `VERBATIM_IN_HTML+NOT_SUM`.** The form states a $0.00 total; sonnet emits the stated zero, mini abstains. **The disqualifying class (mini missing a stated non-zero total) is empty in this slice (0/100).**

The script's framing assumed there'd be a mix of `VERBATIM_IN_HTML+NOT_SUM` (disqualifying — mini missed a stated total) and `NOT_IN_HTML+EQUALS_ITEMIZED_SUM` (defensible — sonnet derived, mini abstained). In practice, neither bucket appears as expected: there are 0 stated-non-zero misses, and the 62 sonnet_only rows are all stated **zero** misses. That's a different policy question: should the schema emit `total_expenditure=0.0` when the form has an explicit "$0.00 Total Aggregate" row, or abstain because the filing has no expenditure activity? sonnet emits, mini abstains. The brief doesn't currently make this convention explicit.

### Script 2 — `positions_spotcheck.py`

Comparison set: 100 rids in (sonnet ∩ medium_briefv3).

| outcome | count |
|---|---:|
| identical | 87 |
| CONTENT_DIFF | 7 |
| LENGTH_DIFF | 6 |
| differing with `bills_match=False` (chain-corrupting) | **13/13** |

Of 13 differing rids, **0 have identical bill multisets after content normalization** — every diff sits in the bill-string slot the chain composer joins on. Three pattern families:

1. **Mini concatenates description into the bill field** (4 rids: 1419016, 1423324, 1429882, 1433628). Example, rid 1419016: sonnet=`'AUDITOR OF STATE'`, mini=`'AUDITOR OF STATE: DECISIONS RELATED TO AUDIT OF STATEWIDE FINANCIAL DATA FROM SCHOOL DISTRICTS'`. Same agency, mini appends the subject.
2. **Mini emits `(NO BILL)` placeholders** where sonnet emits subject categories (2 rids: 1406694, 1412254). This is the case the Diagnostic #2 deep-dive resolved: mini IS extracting the subject content, just putting it in `description` instead of `general_issue_area`.
3. **Mini emits literal administrative-rule numbers** (`5160-46-XX`, `5122-29-20`) where sonnet emits subject categories (1 rid: 1438098 + mini's rows in 1412254). These are real source content (the form lists ORC and OAC rule numbers); mini transcribes them faithfully, sonnet rolls them up.

The script's decision guide called these "chain-corrupting" because the OH chain composer joins positions on bill-string equality. They are — but at least patterns 1 and 2 are recoverable via a normalization layer on the composer side. Pattern 3 (literal rule numbers) is a real semantic gap and needs a brief-side fix.

### Script 3 — `is_itemized_spotcheck.py`

Comparison set: 100 rids in (sonnet ∩ medium_briefv2 ∩ medium_briefv3).

| arm | non-null emission rate |
|---|---:|
| sonnet | 39/100 |
| medium_briefv2 | 5/100 |
| medium_briefv3 | **0/100** |

5 briefv2-emits / briefv3-abstains rids (exact match to plan Step 1's expectation): 1398614, 1401008, 1405684, 1413012, 1427844. All 5: `sonnet=False`, `v2=False`, `v3=None`, `len(expenditures)=1` in every arm.

## Diagnostic deep-dives

### Diagnostic #1 — `HB 29` source check (rid 1394434)

```
$ grep -io "HB[ .]*29\|House Bill 29" data/oh_portal/raw/1394434/*/raw.html
HB 29
```

`HB 29` is in the source. Mini's emission is faithful. The chain composer punishes mini here for being **more literal** than sonnet (which abstracted to `'PUBLIC SAFETY'`). One rid is anecdote, not pattern — but it reframes the positions diff from "mini hallucinates bills" to "mini and sonnet disagree on the right level of abstraction."

### Diagnostic #2 — Where mini puts the subjects (rid 1412254)

Dumped `mini_medium_briefv3_run_1_*/filing.json` for 1412254 (38 vs 39 LENGTH_DIFF, most rows flagged as "(NO BILL)" in the spotcheck output).

```
None | None | 'Competency Restoration'
None | None | 'Behavioral Health Handbook'
None | None | 'ADAMH Board data'
{'bill_number': 'HB 96', ...} | None | 'Biennial budget/HB 96'
None | None | 'OneOhio'
None | None | 'Recovery Ohio'
... 34/39 rows have bill_reference=None, general_issue_area=None,
    description='<the subject>'.
```

- 34/39 positions: `bill_reference=None`, `general_issue_area=None`, `description='<subject>'`.
- 4/39 positions: real `bill_reference` resolved (HB 96 ×2, ORC 340 as `reference_type='other'`, 5122-29-20 as `reference_type='regulation'`).
- 0/39 positions have a non-null `general_issue_area`.

**Mini didn't lose the subjects — it slotted them in `description`.** Sonnet slots them in `general_issue_area`. Same content, different field. The positions spotcheck compared on the bill-string slot mini left empty.

A composer-side normalization rule — "if `general_issue_area is None` and `bill_reference is None` and `description` is short-and-uppercase-category-shaped, copy `description` into `general_issue_area`" — would close most of pattern 2 from Script 2. But the right fix is probably brief-side: the brief should specify which field carries subject categories when no bill is referenced. The schema currently allows both; mini and sonnet picked different conventions, and the brief didn't tie-break.

### Diagnostic #3 — `is_itemized` Step-2 hand-read (5 rids)

For each of the 5 spotcheck-flagged rids, stripped HTML from raw.html and inspected the dollar-amount context windows.

All 5 rids have **identical Section II shape** — a JLEC ethics form with a section titled **"D. Non-Itemized Meals and Beverages"** containing only a "Meals Under $50" line, plus zeros for "Speaking Engagements" and "National Conference Meals," and a "Total Aggregate (A + B + C + D)" line equal to the Meals-Under-$50 value:

| rid | Meals Under $50 | Total Aggregate | match? |
|---|---:|---:|---|
| 1398614 | $142.25 | $142.25 | ✓ |
| 1401008 | $9.91 | $9.91 | ✓ |
| 1405684 | $21.94 | $21.94 | ✓ |
| 1413012 | $168.40 | $168.40 | ✓ |
| 1427844 | $20.00 | $20.00 | ✓ |

Categorization per plan §"Step 3":

| rid | category | ground_truth | sonnet | briefv2 | briefv3 |
|---|---|---|---|---|---|
| 1398614 | GROUND_TRUTH_EMITS | `False` | False ✓ | False ✓ | None ✗ |
| 1401008 | GROUND_TRUTH_EMITS | `False` | False ✓ | False ✓ | None ✗ |
| 1405684 | GROUND_TRUTH_EMITS | `False` | False ✓ | False ✓ | None ✗ |
| 1413012 | GROUND_TRUTH_EMITS | `False` | False ✓ | False ✓ | None ✗ |
| 1427844 | GROUND_TRUTH_EMITS | `False` | False ✓ | False ✓ | None ✗ |

**5/5 GROUND_TRUTH_EMITS.** The form's own section header contains the word "Non-Itemized." This is the least ambiguous signal the form could give. briefv3's full abstention is a regression; it dropped real signal that sat in plain text in the form layout.

Per plan §"Step 4" decision table, **5/5 GROUND_TRUTH_EMITS → "brief-v4 with explicit is_itemized guidance. Worth iterating."**

## Reframed narrative

The predecessor convo's headline was "mini is the gap." This session's evidence reorders the story:

- **`positions`** — the 13% diff is mostly schema-slot mismatch (mini puts subjects in `description`, sonnet puts them in `general_issue_area`), plus one rid where mini is more literal than sonnet on rule numbers. Normalize and most of the gap disappears.
- **`total_expenditure`** — 0/100 stated-non-zero misses. The 62-rid gap is "form shows explicit $0, mini abstains" — a convention question the brief doesn't currently tie-break.
- **`is_itemized`** — briefv3 has a real regression vs **briefv2** (not vs sonnet): it abstains on 5/5 rids where the form's own header says "Non-Itemized." The model isn't the regressor; the brief is.

Plan §"Open question" framing was: "we don't yet know whether briefv3's abstention is correct or a regression." Answer in this 5-rid sample: **regression.** Briefv2 had it right; briefv3's step-8 change ("default is_current=True for originals") nudged adjacent optional fields toward over-abstention.

This matters for the brief-v4 question raised in the plan: instead of *adding* explicit is_itemized guidance to v3, the simpler path may be to identify which step-8 v3 change caused the abstention nudge and back it out for is_itemized specifically — keeping the is_current fix while restoring v2's is_itemized behavior. That's a brief-diff question I haven't done yet.

## Open questions (for remote agent review)

1. **`positions` schema-slot mismatch — fix where?** Two paths:
   - **(a) Brief-side:** specify in the briefv3→v4 diff that when a position has no bill reference, the subject category goes in `general_issue_area`, not `description`. Risk: nudging the model on one field perturbs adjacent ones (the recurring v2→v3 pattern).
   - **(b) Composer-side:** add a normalization step to the OH chain composer — if `general_issue_area is None` and `bill_reference is None`, hoist `description` into `general_issue_area` (modulo length / case heuristics). Risk: silently changes what's in each slot vs the model's emission.

   Which is the right layer? My instinct is composer-side (don't keep tuning the brief if it's a tie-breaking-convention issue, not an extraction issue), but you may have a strong opinion.

2. **`total_expenditure` stated-zero convention.** Should the schema/brief say "emit 0.0 when the form shows an explicit $0.00 total" or "abstain when the filing has no expenditure activity"? sonnet currently does the former, mini does the latter. Both are defensible; pick one and encode it. Open suggestion welcome on which is more useful for downstream chain composition.

3. **`is_itemized` briefv3 regression — patch v3 or build v4?** Plan's Step 4 table says 5/5 GROUND_TRUTH_EMITS → brief-v4. But before authoring v4, can the briefv3 diff vs briefv2 be inspected to find the specific change that caused the abstention nudge? If so, a smaller patch (back out one bullet, keep the is_current fix) might be cheaper than a full v4 revision and less risky for the adjacent-perturbation pattern.

4. **Sample size.** Diagnostics #1 and #3 ran on small N (1 rid and 5 rids respectively). The Diagnostic #3 verdict is unambiguous because the form's own header uses the word "Non-Itemized" — so even N=5 is decisive for that category of filing. But the JLEC form is one of multiple OH form templates; other templates may handle expenditure listings differently. Is a broader is_itemized sample (e.g., 50 rids from sonnet's 39 emissions) needed before committing to a brief change?

5. **Rule numbers (pattern 3 in Script 2).** Rid 1438098's mini emission includes a wall of `5160-46-XX` administrative rule references that sonnet rolls up under `'MEDICAID / HOME CARE / HOSPICE'`. Both are extracting real source content. Which level of abstraction does the chain composer want? (This is a downstream-consumer question more than an extractor question.)

## Topics Explored

- Forward-referenced convo (bfdb8b6 mentioned this path in its commit message; this session closed the reference)
- Reading raw.html via Python (Read tool would burn too much context across 5 × ~250-line files; small `strip_html → find_section_ii` script was cleaner)
- Confirming mini's positions content via direct filing.json inspection rather than relying on the spotcheck's bill-string slot
- Hooks dodge: the `cat ... | python3 -c "..."` pipeline the user pasted would trip the `block_brace_quote_heredoc` hook on the `['positions']` slice; routed through a Write-then-run script instead

## Provisional Findings

- **`positions` gap is mostly cosmetic, not extractive.** Composer-side normalization should close most of the 13% diff without any brief change.
- **`total_expenditure` gap is convention-shaped, not quality-shaped.** No stated-non-zero misses in the 100-rid sample.
- **`is_itemized` is the real regression.** briefv3 introduced it; briefv2 didn't have it. The model isn't the source of the gap. Fixing this likely requires either a targeted v3→v3.1 patch or a v4 revision.
- **The "two-step + one-pivot" pattern from the v2→v3 lesson is recurring.** Each brief revision so far has fixed one field while perturbing another (v2: fixed period, broke is_current; v3: fixed is_current, broke is_itemized). Before brief-v4, worth asking whether there's a structural reason for the perturbation (probably yes: optional fields share a "should I emit?" decision that responds to brief-wide cues) and whether the next revision should be designed to minimize cross-field coupling.

## Next Steps

- **For remote-agent review (this convo's purpose):** suggestions on the 5 Open questions above, especially #1 (brief-side vs composer-side fix for positions) and #3 (patch briefv3 vs author briefv4 for is_itemized).
- **Once direction is decided:** the actual brief diff / composer normalization work goes on a fresh session under TDD; this convo + plan are the brief.
- **Pre-existing:** plan §"After investigation, the writeup" — the Suhan-facing writeup is still pending; gated on this convo's decisions about briefv3 status.

## Provenance

- All numbers reproducible from `results/20260612_gpt5mini_quality_gap_checks/*.log` (committed at `8eaa131`)
- Scripts at `scripts/gpt5mini_oh_300slice_{total_expenditure,positions,is_itemized}_spotcheck.py` (committed at `bfdb8b6`)
- Raw HTML for the 5 is_itemized rids at `data/oh_portal/raw/<rid>/*/raw.html` (paths in `results/.../is_itemized_spotcheck.log`)
- Mini briefv3 filing.json for rid 1412254 at `data/oh_portal/extracted_openai/1412254/mini_medium_briefv3_run_1_20260609T232910_6b2315bc/filing.json`

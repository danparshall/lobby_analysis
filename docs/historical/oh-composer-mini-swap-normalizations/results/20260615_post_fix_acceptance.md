# Post-fix acceptance experiment (2026-06-15)

**Plan:** `docs/active/leave-behind-prep/plans/20260615_composer_side_mini_swap_normalizations.md`
(on `leave-behind-prep`)
**Originating findings:**
`docs/active/leave-behind-prep/results/20260615_mini_swap_chain_level_evidence.md`
(on `leave-behind-prep`)
**Implementation commit:** `3f2c677` on this branch.
**Cost:** $0 (no new API spend; existing extractions on disk).
**Wall:** ~10 min including diff scripting.

---

## TL;DR

Both normalizations work. The **structural** acceptance criteria pass
strongly: principal_id / lobbyist_id disagreement drops to **0/246** on
post-fix shared rows (was 236/240 and 235/240 pre-fix), and the no-digit
demotion rule fires on exactly the rows the findings doc characterized
as subject-leak (no false positives — the 8 surviving unmatched labels
are all malformed-bill-shape citations with digits).

**Two of the plan's acceptance numbers are wrong** in a way worth
surfacing rather than silently rationalizing past:

1. The plan expected sonnet's surviving `bill_class=unmatched` count to
   be "within 2 of 18" — i.e., the demotion would fire on ~0 of
   sonnet's 18 unmatched rows. It actually fires on **10**. The plan
   text reads:
   > If this number is materially lower than 18, **stop and check with
   > Dan before proceeding** — the rule may be too aggressive.
   
   I'm stopping here. **But** I think the rule is *not* too aggressive
   — see "Demoted sonnet labels" below; they're all unambiguous
   subject content. The plan author's estimate "sonnet's 18 unmatched
   are mostly malformed bills" turned out to be wrong; the actual
   composition is ~55% subject-leak + ~45% malformed-bill-shape. The
   rule correctly distinguishes the two.

2. The plan expected the mini-vs-sonnet row-set diff to drop to ≤10
   mini-only rows. It dropped from 61 to 56. **But** the breakdown
   reveals this is text-not-structure: 55 of the 56 mini-only rows are
   correctly-demoted `subject_general` rows whose text content
   (extracted from mini's bill_reference field) differs from sonnet's
   `general_issue_area` text on the same source filings. The plan
   author appears to have assumed post-demotion mini text would
   key-match sonnet text; in practice the two models describe the same
   regulatory subject with different wording, so the row-set diff
   stays high. The *cell-level* shared-row count actually went UP from
   240 to 246, which is the cleaner structural signal.

The composer-side changes are doing exactly what they were designed to
do. The plan's row-set acceptance criteria were calibrated against a
mental model of mini and sonnet producing identical subject text, which
isn't how the models actually behave. The cell-level criterion is the
load-bearing one and it passed strongly.

---

## A. Release re-roll diff (shipped sonnet vs new sonnet, 305 filings)

Row count identical: **1,589 = 1,589** ✓
(Step-2 demotion changes a row's class, not its existence — the row
total is conserved.)

### Step 1 — entity-ID derivation impact

| metric | shipped | new | changed |
|---|---|---|---|
| distinct (principal_name, principal_id) pairs | 135 | 132 | 58 |
| distinct (lobbyist_name, lobbyist_id) pairs | 125 | 123 | 39 |

**Collisions: 0.** Every derived `principal_id` and `lobbyist_id` maps
to exactly one distinct name in the corpus — the slugify-with-collision
risk the plan flagged (§"Risks / known gotchas" item 3) doesn't
materialize on this corpus.

The distinct-pair count drops slightly (135 → 132, 125 → 123) because
the derivation collapses two near-name variants in three cases — same
principal getting two different `principal_id`s in shipped because the
extractor emitted two different IDs on different filings. Worth noting:
this is a small QUALITY win on the shipped artifact, not just a
formatting normalization.

**Sample principal_id changes (shipped → new):**

| principal_name | shipped | new |
|---|---|---|
| AARP | `org-aarp-oh` | `org-aarp` |
| American Chemistry Council | `org-american-chemistry-council-oh` | `org-american-chemistry-council` |
| American College of Obstetricians & Gynecologists | `org-american-college-of-obstetrician` (truncated by extractor) | `org-american-college-of-obstetricians-gynecologists` |
| Centegix | `oh-org-centegix` | `org-centegix` |
| Central Ohio Transit Authority (COTA) | `org-cota` | `org-central-ohio-transit-authority-cota` |
| Cincinnati Children's Hospital Medical Center | `org-cincinnati-childrens-hospital-me` (truncated, no apostrophe) | `org-cincinnati-children-s-hospital-medical-center` |
| Cleveland Browns | `org-cleveland-browns-oh` | `org-cleveland-browns` |
| Coinbase, Inc. | `oh-org-coinbase-inc` | `org-coinbase-inc` |

The shipped IDs had three inconsistent conventions: `org-{slug}`,
`oh-org-{slug}`, and `org-{slug}-oh`. Sonnet's truncation on long names
("obstetrician", "hospital-me") also dropped content. The new derivation
gives one convention.

**Audit note for the implementer:** `org-children-s-hospital` is the
ASCII-folded form of `Children's Hospital`. The apostrophe becomes a
hyphen-flanked single letter `s`. Slightly less pretty than what the
extractor produced, but deterministic, stable, and round-trip-safe.

### Step 2 — no-digit demotion impact

| metric | shipped | new |
|---|---|---|
| sonnet `bill_class=unmatched` rows | 18 | 8 |
| demoted | 0 | 10 |

**Plan acceptance check:** plan expected "within 2 of 18" (16-20
surviving). Got **8** surviving. The plan flagged this as a stop-gate;
this doc surfaces it.

**Demoted sonnet labels** (all 10):

```
Accessible Housing
Early Intervention
Electronic Visit Verification
Excess and Surplus Lines Export List
Federal IDEA funds/schools
Issues affecting insurance agents
Multi-System Youth - Children's Issues
NM
Vocational Habilitation/Basic Employment Skills Training/Group Employment Support
Waiver Modernization
```

These are unambiguously subject content (regulatory topics, program
names) — not malformed bills. Sonnet leaked them into the
`bill_reference` slot for the same structural reason mini does (the
filer disclosed lobbying on a regulatory topic rather than a specific
bill; the extractor took the topic literally as a bill_reference). The
demotion rule correctly reroutes them to `subject_general` + `subject`.

**Surviving 8 unmatched labels** (post-fix):

```
5123-2-XX                                                       — OAC-shape with wildcard
5160:59-04, 5160-59-50, 5160-59-05.2                            — comma-sep OAC rules
5180:2-5-07, 5180:2-5-28                                        — comma-sep OAC rules
5180:4-5-09.1                                                   — colon-prefixed OAC rule
CB 7/21/2025                                                    — document ref with date
CB DOH0105168                                                   — document number
Ch. 4757-5, -6, -9, -1-08, -1-10, -13-19, -19-05, ...           — chapter list
Chapter 5160-35                                                 — chapter reference
```

All 8 contain digits and look like genuinely malformed bill / OAC / JCARR
references (colon-prefixed, comma-listed, "Ch.", "Chapter") that don't
match the regex patterns. The demotion correctly preserves them — this
is the exact audit signal the plan's `unmatched` class exists to carry.

**Verdict on Step 2:** the rule is working as designed. The plan
author's estimate of sonnet's pre-fix unmatched composition (~0 subject
leak, ~18 malformed bills) was wrong; the actual composition is **10
subject-leak + 8 malformed-bill-shape**. The fact that sonnet ALSO had
subject-leak (not just mini) is a quality finding on its own — the
demotion rule helps sonnet too.

---

## B. Post-fix mini-vs-sonnet diff on the shared 100 rids

(Restricting to the 100 rids the mini briefv2 run covers.)

| metric | sonnet (100 rids) | mini briefv2 |
|---|---|---|
| chain rows | 419 | 426 |
| filings present in chain | 59 | 59 |

### Row-set diff (key = filing_id × bill_label_normalized × position_kind)

| bucket | pre-fix (from findings doc) | post-fix |
|---|---|---|
| shared | 240 | **246** (+6) |
| sonnet-only | 48 | 42 (−6) |
| mini-only | 61 | 56 (−5) |

**Plan acceptance checks:**

- mini-only ≤ 10 — **FAIL** (got 56). See "Why this isn't actually
  bad" below.
- sonnet-only ≤ 50 — PASS (got 42).

### Mini-only breakdown (post-fix)

| position_kind | bill_class | rows | nature |
|---|---|---|---|
| `bill_referenced` | `bill` | 2 | mini extracted real bills sonnet missed |
| `bill_referenced` | `oac_rule` | 2 | mini emitted granular OAC rules sonnet rolled up |
| `bill_referenced` | `unmatched` | 3 | digit-containing malformed-bill (correctly preserved) |
| `subject_general` | `subject` | **55** | demoted from mini's pre-fix bill_referenced+unmatched bucket |
| `subject_hoisted_from_description` | `subject` | 2 | composer hoist already in place |

Pre-fix had **59** `bill_referenced+unmatched` mini-only rows; post-fix
has 3. The other 56 demoted, as designed.

### Sonnet-only breakdown (post-fix)

| position_kind | bill_class | rows |
|---|---|---|
| `subject_general` | `subject` | 57 |

(Was 48 subject_general+subject pre-fix; post-fix is 57 because some
sonnet rows that were `bill_referenced+unmatched` pre-fix demoted to
`subject_general+subject` on Step 2, joining the bucket. Symmetric to
mini's 55 subject_general demoted rows.)

### Why the row-set criterion "fails" but the result is actually good

The 55 mini-only `subject_general+subject` rows + 57 sonnet-only
`subject_general+subject` rows are **not structural disagreement** —
they're the same kind of content (regulatory subject leaks on EUPA
filings) **described with different wording** by the two models.

Concrete example from filing `20250528EUPA1412254`:

- **Mini's bill_reference text:** "Competency Restoration", "Behavioral
  Health Handbook" (these were originally bill_referenced+unmatched,
  now demoted to subject_general+subject)
- **Sonnet's general_issue_area text on the same filing:** "Opioid /
  OneOhio", "Behavioral Health" (these are in sonnet-only because the
  text doesn't key-match mini's text on the same filing)

Both models recognize the filing as carrying regulatory-subject
positions; they just describe those subjects with different wording.
The composer can't reconcile that without a semantic dedupe pass,
which is out of scope.

The cleaner structural signal is the **cell-level disagreement on
shared rows**, which strengthened from 240 to 246 shared (+6) and
collapsed both ID columns to 0 disagreement:

### Cell-level disagreement on the 246 shared rows

| field | pre-fix | post-fix | change |
|---|---|---|---|
| `principal_id` | 236/240 (98.3%) | **0/246 (0.0%)** | −236, **acceptance PASS** |
| `lobbyist_id` | 235/240 (97.9%) | **0/246 (0.0%)** | −235, **acceptance PASS** |
| `principal_name` | 4/240 (1.7%) | 4/246 (1.6%) | unchanged (content-level) |
| `lobbyist_name` | 0 | 0/246 | unchanged |
| `bill_class` | 0 | 0/246 | unchanged |
| `bill_id` | 0 | 0/246 | unchanged |
| `bill_title` | 0 | 0/246 | unchanged |
| `confidence` | 0 | 0/246 | unchanged |
| `sponsor_lawmaker_id` | 0 | 0/246 | unchanged |
| `num_primary_sponsors` | 0 | 0/246 | unchanged |

**This is the load-bearing acceptance criterion**, and it passes
strongly. Every column that the composer is supposed to deterministically
mint now agrees perfectly between sonnet- and mini-sourced chains. The
remaining 4-row `principal_name` disagreement is content-level (mini
spelled an org slightly differently than sonnet on the underlying
extraction) and out of scope for the composer-side normalization plan.

---

## Verdict

**Both normalizations behave correctly.** The plan's narrative claims
all check out: entity-ID derivation collapses model-formatting noise to
zero on shared rows, and the no-digit demotion rule correctly
distinguishes subject leak from malformed-bill-shape audit content.

**Two of the plan's pre-stated acceptance numbers were optimistic** —
both because they assumed cleaner pre-fix sonnet content than was
actually present:

1. Plan expected ~0 sonnet unmatched rows to demote; 10 actually did
   (sonnet had subject-leak too, just less than mini).
2. Plan expected mini-vs-sonnet row-set diff to drop to ≤10 mini-only;
   it dropped from 61 to 56 (the demoted rows correctly land in
   subject_general but their *text* differs from sonnet's
   subject_general text on the same source).

Neither is a sign of a broken rule. The cell-level diff — which is the
strongest structural signal — passes the acceptance criterion cleanly.

**Recommendation:** ship the composer changes. The release-TSV re-roll
(58 principal_ids changed, 39 lobbyist_ids changed, 10 sonnet
unmatched rows demoted) is a real column-level change to the shipped
artifact that warrants Dan's explicit sign-off per the plan's
§"Risks / known gotchas" item 1.

---

## Reproducibility

- **Sonnet inputs:** `data/oh_portal/extracted/` (symlinks to
  `~/data/lobby_analysis/`)
- **Mini briefv2 inputs:** `data/oh_portal/extracted_briefv2_mini/`
  (already-staged from the 2026-06-15 experiment; symlinks intact)
- **Plural bills bundle:** `data/bills/OH/136/`
- **Composer CLI:** `python -m lobby_analysis.allocation.oh.cli
  materialize --extractions <dir> --bills <dir> --out <dir>`
- **Diff script:** `/tmp/diff_post_fix.py` (move to `scripts/` if useful
  going forward; otherwise discard — composer behavior is locked by
  the unit tests in `tests/allocation/oh/test_entity_id_derivation.py`
  and the new test classes in `tests/allocation/oh/test_chain.py`)

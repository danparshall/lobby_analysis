<!-- Generated during: convos/20260604_sonnet_validation_employer_warnings_schema.md -->

# Sonnet vs opus validation — OH AER 1427844 (Aichele / ARC Gaming)

All runs against the **same cached HTML** the opus baseline `bd540187` used
(`data/oh_portal/raw/1427844/2026-06-03T19-31-18+00-00/raw.html`), so the only
variable is the model / brief. Run via a one-off that skips fetch and reuses the
shipped `extract_oh_legislative_filing`. Extraction artifacts under (gitignored)
`data/oh_portal/extracted/1427844/`.

Model note: `claude-sonnet-4-7` does not exist (404). Sonnet is on `4-6`; opus on `4-7`.

## Before the fix (old brief, no `employer` slot)

Sonnet, 3 runs, **consistent**:

| field | sonnet (3/3) | opus baseline `bd540187` |
|---|---|---|
| employer | — (no field existed) | — |
| `filer_organization` | **"ARC Gaming & Technologies"** (employer mis-filed here) | `null` (employer silently dropped) |
| `filer_person` | Nathan Aichele | Nathan Aichele |
| `is_itemized` | `false` (correct) | `null` (MISSING) |
| bills / expenditure / totals | all correct | all correct |

Root cause: brief rule 6 said "populate ... employer name" but the schema had no
employer slot → contradictory spec → opus drops, sonnet jams into `filer_organization`.
Both silent. **Prompt problem, not model-quality problem.**

## After the fix (new brief + `employer` + `extraction_warnings`)

| field | opus-4-7 | sonnet-4-6 |
|---|---|---|
| `employer` | ✅ "ARC Gaming &. Technologies" (verbatim, typo kept) | ✅ "ARC Gaming & Technologies" (typo normalized) |
| `filer_organization` | ✅ `null` (not misfiled) | ✅ `null` (**fixed** — was misfiled) |
| `filer_person` | Nathan Aichele | Nathan Aichele |
| `is_itemized` | `null` | `false` |
| `extraction_warnings` | 2 notes (II.D loss + period inference) | 3 notes (II.D loss + period + empty A/B/C) |
| bills / expenditure / totals | all correct | all correct |

**Both models converge** on the employer fix and both flag the Section II.D schema gap
through the new warnings channel (silent data-loss → visible signal).

## Decision

Switch `MODEL_ID` to `claude-sonnet-4-6` for bulk: correct post-fix, ~40% cheaper than
opus-4-7, fixes `is_itemized`. Residual: sonnet normalizes name typos (opus preserves
verbatim) — close with a brief rule iff verbatim fidelity matters downstream.

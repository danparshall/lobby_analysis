# SUPERSEDED — pre-v2.1 enforcement_and_audits dispatch results

These 6 JSONs are the pre-v2.1-Pattern-C-split dispatch results for the
`enforcement_and_audits` chunk on WI 2025, archived 2026-06-05 to clear the
resume-checkpoint state so the v2.1 BinaryCell additive-pattern dispatch
could re-run against the corrected schema.

**What they contain:** wide-pass results from the wi-tier1-direct-read Commit-3
era — `_imposed_in_practice` legal-axis cell + `_audit_required_in_law` legal-
axis cell, both reading combined-axis prompts under the v2 schema.

**Why archived (not deleted):** these JSONs are analytical work — the iter-5
silent-unit-mismatch sweep referenced them, and the wide-pass audit
(`docs/active/wi-tier1-direct-read/results/20260604_wi_wide_pass_audit.md`)
recorded findings on top of them. Keeping them with a SUPERSEDED banner per
the project memory entry "Prefer mv over rm for research artifacts" preserves
the lineage.

**Why superseded:** v2.1 Pattern C row split (this branch, 2026-06-05):
- `_imposed_in_practice` lost its legal-axis cell (category error); the de-jure
  pair lives on the new `_defined_in_law` BinaryCell row.
- `_audit_required_in_law` lost its practical-axis cell; that lives on the new
  `_audit_required_in_practice` row.
- The `enforcement_and_audits` chunk grew from 2 rows / 4 cells (2 legal + 2
  practical) to 4 rows / 4 cells (2 legal + 2 practical), all single-axis.
- Re-dispatch needed on the new chunk roster — these checkpoint files would
  have caused the dispatcher to skip the BinaryCell test entirely.

**Successor results:** the v2.1 dispatch's 6 JSONs land at the parent
directory under the same chunk_id immediately after this archive move.

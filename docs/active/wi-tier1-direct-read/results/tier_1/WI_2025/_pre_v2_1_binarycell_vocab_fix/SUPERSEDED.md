# SUPERSEDED — pre-prompt-fix BinaryCell dispatch results (negative-result evidence)

These 6 JSONs are the first v2.1 Pattern C dispatch on WI 2025
enforcement_and_audits — preserved as **negative-result evidence** for the
BinaryCell cell-type-aligned-vocabulary finding (2026-06-05).

**What they contain:** dispatch results with the initial v2.1 YAML prompt
for `lobbying_violation_penalties_defined_in_law` that instructed models to
answer with `'yes'` or `'no'`. Both Claude (3/3 runs) and GPT (3/3 runs)
correctly emitted `'yes'` based on WI §13.69 (penalties + forfeitures), but
the dispatcher's `_instantiate_cell` for `BinaryCell` (in
`scripts/tier_0_direct_read_smoke.py` ~L476-482) only accepts `'true'` or
`'false'` strings — so all 6 emissions failed instantiation with
`ValueError("BinaryCell: cannot coerce 'yes' to bool")`. The other legal
cell in the chunk (`_audit_required_in_law`, EnumCell) instantiated each
run with value-unstable across the 3 runs (the IND_207 CPI-errata candidate
already documented in iter-5 sweep).

**Cost burned:** $0.171 (all 6 dispatches recorded; 50% stable per model
because the EnumCell side instantiated 3/3 even as it value-flipped).

**Why archived (not deleted):** this IS the BinaryCell additive-pattern
discovery — concrete evidence that "yes"/"no" vocabulary in a BinaryCell
prompt produces 0/6 convergence due to a cell-type-vocabulary mismatch with
the dispatcher's coercion table. The iter-5 playbook's "cell-type
instantiation failure" branch lands literally here. Preserved as the
negative result that motivated the prompt rewrite.

**Successor results:** the v2.1+prompt-fix dispatch lands at the parent
directory immediately after this archive move, with prompts instructing
`true`/`false` (cell-type-aligned vocabulary).

**Finding documented in:** the convo summary doc for this session.

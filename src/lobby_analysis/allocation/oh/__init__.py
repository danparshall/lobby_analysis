"""OH chain composer (Phase 3 v0 — release-grade composition).

Stitches the OH AER extraction outputs (`LobbyingFiling` JSON, one per AER)
against the Plural Policy 136th GA bill bundle, emitting the
``releases/oh/chain/`` Suhan-droppable artifact.

Plan: ``docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md``
(last updated 2026-06-14 to incorporate the 2026-06-13 mini-swap findings).

Per Anna Karenina, this is NOT a port of the WI composer. OH has no
principal↔lobbyist marginal (no IPF needed), but it has native
lobbyist↔lawmaker gift/meal edges and a non-bill regulatory-rule layer
(OAC / JCARR) that the chain must classify rather than drop.

Module layout:

- ``classify`` — pure-logic Phase-1 classifiers (this file's first sibling).
- ``load`` — TODO (Phase 1 Step C): typed DataFrame loaders for extractions
  and Plural Policy CSVs.
- ``chain`` — TODO (Phase 2): bill-side cross-product composer.
- ``gifts`` — TODO (Phase 3): Section II.A/B per-event composer.
- ``filings`` — TODO (Phase 3.5, conditional on §7 Q6): filing-grain composer
  hosting the stated-zero + is_current normalizations.
- ``cli`` — TODO (Phase 4): CLI materializer to ``releases/oh/``.
"""

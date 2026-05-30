"""WI 2025-2026 allocation-matrix inference.

Three layers, each in its own module:

- ``load``  — read the merged ``releases/wi/`` TSVs into per-semester
              loader outputs (principal totals, lobbyist totals, active
              edges, per-bill effort percents)
- ``graph`` — assemble the bipartite (lobbyist, principal) graph,
              decompose into connected components, classify exactly-
              pinned vs free, flag Pettack-class outliers
- ``ipf``   — Phase 2: max-entropy IPF fit on free components

Semester format throughout: ``"2025-H1"``, ``"2025-H2"``, ``"2026-H1"``,
``"2026-H2"``.
"""

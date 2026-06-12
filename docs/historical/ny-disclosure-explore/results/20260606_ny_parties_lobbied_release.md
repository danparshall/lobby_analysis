<!-- Generated during: convos/20260606_ny_parties_lobbied_mvp.md -->

# NY `parties_lobbied` disclosed-lawmaker edge — MVP release aggregates

**Date:** 2026-06-06 (Dan AFK / YOLO). **Provenance:** `releases/ny/NY_filing_parties_lobbied.tsv`
(gitignored under `releases/ny/**/*.tsv`; regenerate with the command below).

**Pipeline:**
```
scripts/ny_pull_2025.py                       # paginated+verified re-pull (adds parties_lobbied)
  -> data/raw/ny/2025/client_semiannual.csv   # 11,200,080 rows, VERIFIED == live count(*)
python -m lobby_analysis.io.ny.parties_cli \
    --input data/raw/ny/2025/client_semiannual.csv \
    --os-dir data/bills/NY/2025 \
    --output-dir releases/ny
```

Inputs: the re-pulled `client_semiannual` (2025) + the Open States NY 2025-2026
`NY_*_bill_sponsorships.csv` roster (219 person-sponsors). Plan:
[`plans/ny_parties_lobbied_mvp.md`](../plans/ny_parties_lobbied_mvp.md); gating
Phase 0: [`results/20260606_ny_parties_lobbied_grain.md`](20260606_ny_parties_lobbied_grain.md).

---

## Headline

| metric | value |
|---|---|
| edge rows (one per filing × distinct party) | **170,328** |
| distinct firm-filings covered | 8,602 |
| **resolved edges (matched to an `ocd-person`)** | **90,612 (53.2% of all edges)** |
| distinct resolved legislators | **195** (of ~213; ≤ roster, sane) |
| legislator-titled edges | 100,250 (58.9% of all edges) |
| **— of those, resolved** | **90,612 (90.4%)** ← the Phase-0-comparable rate |
| non-legislator-titled edges (preserved, `resolved=False`) | 70,078 (41.1%) |

**Read the two rates correctly.** The **90.4%** is the rate that matters for the
MVP goal ("resolve named *state legislators*"): of the 100,250 edges that name a
state legislator (Senator / Assembly member title), 90.4% resolved to a specific
`ocd-person`. The **53.2%** is resolved-over-*all*-edges, dragged down because
**41% of disclosed parties are not state legislators at all** — they are NYC
municipal officials (Council members, the Mayor's office), state executive offices
/ agencies (Division of the Budget, DOH, NYSED), chamber program/counsel staff,
and "entire-legislature" broadcasts. Those are correctly **not** resolved to the
state legislative roster; they are kept verbatim with `resolved=False`.

**This validates the Phase-0 first+last decision:** exact full-name match would
have resolved ~63% of legislator edges; first+last lifts that to **90.4%**.

### Why 90.4% (edge grain) vs Phase 0's 93.7% (row-weighted)

Phase 0 measured the rate *row-weighted* (each disclosure value weighted by how
many of the ~11.2M denormalized rows it spans); this release measures it at the
**edge grain** (each distinct filing × party counted once). Leadership and
high-activity legislators dominate the row-weighting but collapse to one edge per
filing here, so the long tail of harder-to-match legislators (below) carries more
weight at edge grain — hence the few-point drop. Both are "right"; they answer
different questions.

## The residual unresolved legislators (9,638 rows / 212 distinct values)

These are named state legislators we did **not** resolve — all kept
`resolved=False`, raw preserved, nothing dropped. Three causes, all deferred per
MVP scope:

1. **Accent folding** — `Senator Jose M. Serrano` (OS roster: `José`),
   `Assembly member Emérita Torres`. The first+last key is not yet unicode-accent-
   normalized; folding both sides would recover these. *Cheap, high-value post-MVP fix.*
2. **Nicknames** — `Senator Elizabeth Krueger` (roster: `Liz Krueger`). Needs a
   nickname/alias map or a fuller official people source — genuinely fuzzy.
3. **Non-sponsoring members** — `Jennifer Lunsford`, `Luis R. Sepulveda`,
   `Chris Eachus`, `Matt Slater`, … legislators absent from the *sponsorship*
   roster entirely (they sponsored nothing in 2025-2026). Needs a complete OS
   people roster, not just sponsors.

## Caveats for downstream / policymakers

- **Disclosed ≠ inferred.** This edge is the genuinely *disclosed* "who was
  lobbied" field. It is distinct from — and complements — the chain's lawmaker
  edge (the bill *primary sponsor*, inferred via Open States). It surfaces
  leadership, committee chairs, executive offices, and municipal officials a
  sponsor join never could.
- **`resolved=True` ⟺ a specific named state legislator.** Only legislator-titled
  values that matched the roster are resolved. We never coerce an office, a
  broadcast, or a municipal official into a state-legislator id.
- **Resolution is non-uniform — do NOT read `resolved=False` density as "less
  lobbied."** It is biased against (a) non-state-legislator parties (by design)
  and (b) accent/nickname/non-sponsoring state legislators (a known gap). A naive
  "times each legislator was lobbied" count will undercount exactly the harder-to-
  match members.
- **Per-firm replication.** NY reports `parties_lobbied` at the client-submission
  level; the set replicates onto every co-retained firm's filing. We attach the
  client's full party set to each firm-filing — we do not claim firm X
  specifically contacted party Y, only that the client's filing retaining X
  disclosed Y.
- **Unweighted edge** — carries no dollars; there is no conservation invariant.
  The metric is the resolution rate.

## Post-MVP follow-ups (surfaced, not done)

- Accent-fold the first+last key (recovers Serrano, Torres, … — low effort).
- Fuller OS people roster (vote_people was tested and rejected — wrong name
  format; need the canonical OS people CSV) for non-sponsoring members + nicknames.
- `target_kind ∈ {legislator, executive, agency, committee_staff, chamber_broadcast,
  municipal}` taxonomy for the 41% non-legislator edges (note **municipal** —
  NYC Council/Mayor — is a real, sizable category the recon under-weighted).
- Chain integration (surface the disclosed edge alongside the inferred sponsor edge).

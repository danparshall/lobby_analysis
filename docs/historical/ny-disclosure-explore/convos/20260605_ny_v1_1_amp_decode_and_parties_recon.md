# NY v1.1 — `&amp;` decode fix + `parties_lobbied` reconnaissance

**Date:** 2026-06-05 (UTC) · **Branch:** `ny-disclosure-explore` · **Session:** agent, Dan AFK (YOLO/best-judgement)

## Context

Picked up the Phase-4-DONE handoff (chain shipped at `7d765ab`). The handoff's
v1.1 menu: `parties_lobbied` edge (top), `&amp;` decode, cosponsors, multi-year
backfill. Dan went AFK with "use your best judgement."

**Judgement call on scope.** Deferred the `parties_lobbied` *resolution* build:
it needs an 11.2M-row re-pull + a free-text→`ocd-person` name-resolution design,
and it produces the most policy-sensitive output (the only *disclosed* lawmaker
edge — "don't overclaim to policymakers"). That's a design decision to make with
Dan in the loop, not to invent unsupervised. Instead did the two safe,
high-value pieces: the `&amp;` decode (turned out to be a real correctness bug)
and `parties_lobbied` **reconnaissance** to de-risk the eventual resolution work.
Did **not** touch cosponsors (modeling decision) or multi-year backfill (large).

## What shipped

### 1. `&amp;` HTML-entity decode — a chain correctness bug, not cosmetics

**Discovery:** the chain's coalition splitter (`split_beneficiaries`) splits
`beneficial_client` on `;`, and the HTML-encoded ampersand `&amp;` *ends in a
`;`*. So undecoded `AT&amp;T` fractured into phantom beneficiaries `AT&amp` + `T`
— 3,748 of 87,534 chain rows (4.3%) affected. This fabricated beneficiaries,
inflated coalition member counts `M`, and misallocated `comp_per_cell` within
cells.

**Root cause + fix (TDD):** the parser never HTML-decoded. Fixed at the earliest
point — `io/ny/parse.py::_clean_name` now `html.unescape`s **before** the
trailing-`;` strip (order is load-bearing); `parse_individual_lobbyists`
unescapes before its `;` split too. The chain's `split_beneficiaries` needed no
change — it reads the now-decoded `NY_clients.tsv`. 5 new tests (RED→GREEN); NY
suite 89 → **94 green**, ruff clean.

**Regenerated** releases (`materialize_cli` over the raw 11.2M-row CSV, 58s) +
chain (`cli chain`). Validated:

| metric | pre | post |
|---|---|---|
| chain rows | 87,534 | 83,786 (−3,748 = exactly the phantom rows) |
| distinct beneficiaries | 1,892 | 1,812 |
| coalition filings (M>1) | 476 | **276** (old inflated ~42% by mis-split standalones) |
| **conservation total** | $153,064,191.00 | **$153,064,191.00 ($0 delta)** |
| bill-match | 99.9%, 30 unmatched | 99.9%, 30 unmatched (unchanged) |

0 residual `&amp;` in any `releases/ny/*.tsv`. Full writeup:
`results/20260605_ny_amp_decode_recompute.md`.

### 2. `parties_lobbied` reconnaissance (no resolver built)

Probed the live field (`scripts/ny_probe_parties_lobbied.py`). **Populated on
99.9% of 2025 rows.** Representative value-kind split (row-weighted `GROUP BY`,
top-400 distinct = 91% of rows):

- **83.0% named legislators** (`Senator X` / `Assembly member X`, often `, staff
  member`) — the resolvable core; target id space already exists (chain resolves
  all 213 NY legislators).
- **8.7% executive offices/agencies** (Governor, NYSED, ESD, CUNY) — no `ocd-person`.
- **5.0% committee/program-counsel staff**; **3.4% uncategorized**, incl. a real
  category — "communication sent to **entire** NYS Legislature/Assembly/Senate"
  broadcasts (~240k rows).

Confirms it's a real disclosed **ingest** (re-pull + normalization), richer than
sponsor-inference (names leadership/staff/executive actually lobbied), not an
imputation. **Recommendation surfaced (not decided):** model it as a separate
edge with a `target_kind ∈ {legislator, executive, agency, committee_staff,
chamber_broadcast}` discriminator; resolve `ocd-person` only for `legislator`;
let Dan set the routing policy for the ~17% non-individuals. Full findings +
design implications: `results/20260605_ny_parties_lobbied_recon.md`.

## Files

- **Changed:** `src/lobby_analysis/io/ny/parse.py` (decode), `tests/test_ny_entities.py`
  (+5 tests), `releases/ny/{NY_clients,NY_filings,NY_filing_bill_links}.tsv` +
  `releases/ny/chain/NY_chain_2025.tsv` (regenerated, 53 MB), `releases/ny/README.md`
  + `releases/ny/chain/README.md` (decode caveat + recomputed aggregates + v1.1
  list), `results/20260605_ny_phase4_chain_aggregates.md` (superseding note).
- **New:** `scripts/ny_probe_parties_lobbied.py`, `scripts/ny_chain_metrics.py`,
  `scripts/ny_chain_aggregates.py`, two `results/` docs, the two probe JSONs.

## Next session (for Dan)

- **`parties_lobbied` resolution** (the deferred top item): re-pull 2025 with the
  field in `$select`; resolve named-legislator rows to `ocd-person`; flag the
  ~17% non-individuals (`resolved=False`, raw preserved). **Plan written:**
  [`plans/ny_parties_lobbied_mvp.md`](../plans/ny_parties_lobbied_mvp.md) — Phase 0
  grain/name-format probe (gating), re-pull, TDD extract+resolve, ship
  `NY_filing_parties_lobbied.tsv`; chain integration + `target_kind` taxonomy are
  post-MVP.
- Cosponsors edge (OS bundle already staged; carries the same
  comp-replication-across-edges discipline as sponsors).
- Multi-year backfill (2019→).

## Addendum (2026-06-06) — release-artifact git-tracking decision

Follow-on discussion after I flagged that the `&amp;` fix meant re-committing the
53 MB chain TSV (a published, version-controlled artifact). Dan proposed purging
the chain TSV from branch history (`git filter-repo`) and re-adding it only at
merge.

**Investigated, then abandoned the history rewrite — two evidence-based reasons:**

1. **The reclaim is ~3.3 MB, not ~100 MB.** The chain TSV is 53 MB on disk but
   only **3.47 MB packed** (TSV deltifies/compresses extremely well across its
   two near-identical versions). A throwaway-clone purge measured pack
   95.43 → 92.10 MiB. My original "~100 MB smaller" estimate reasoned about file
   size instead of packed size and was wrong.
2. **`filter-repo` on the full reachable history was unsafe.** Run in an isolated
   throwaway clone (nothing pushed), it **dropped 118 commits** (598 → 480) and
   **destroyed the merge-base with `main`** by collapsing degenerate merges
   across shared ancestry (merge commits 64 → 45, plus the side-branch commits
   that became unreachable). The HEAD *tree* was clean (only the chain TSV
   removed) but the commit *DAG* was mangled — force-pushing it would have made
   the eventual merge-to-`main` a tangle. The verify gate (tree-diff +
   commit-count parity check) caught it before any force-push. A safe scoped form
   (`--refs <merge-base>..HEAD`) exists but still needs a force-push for a
   ~3.3 MB gain.

**Decision (Dan):** don't rewrite history; **untrack the regenerable release data
TSVs going forward** instead. Committed (`10adc78`, normal push, no force):
`git rm --cached` on all 5 NY release data TSVs (chain + clients + lobbyists +
filings + links) and a `.gitignore` pattern `releases/ny/**/*.tsv`. Working
copies stay on disk; the hand-written READMEs stay tracked; the already-committed
chain blob rides along in history at ~3.3 MB packed (negligible). The 5 TSVs are
deterministically regenerable (`materialize_cli` + `cli chain`, ~60 s).

**Two carry-forward notes:** (1) at merge, the release TSVs are gitignored —
re-add the final set with `git add -f releases/ny/...`. (2) a branch checkout now
has the `releases/ny/` READMEs but not the data they describe until regenerated;
acceptable since scripts + raw inputs are preserved.

**Process note (honesty):** I initially argued *purge-now* over the simpler
`rm --cached`; the evidence (packed size + the DAG damage the verify gate
surfaced) reversed that. Recorded here so the reasoning isn't lost.

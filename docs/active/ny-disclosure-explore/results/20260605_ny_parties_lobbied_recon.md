<!-- Generated during: convos/20260605_ny_v1_1_amp_decode_and_parties_recon.md -->

# NY v1.1 — `parties_lobbied` reconnaissance (the disclosed-lawmaker edge)

**Scope: reconnaissance only.** No re-pull of the full dataset, no name
resolver, no chain change. The goal is to characterize the free-text shape of
`client_semiannual.parties_lobbied` so the eventual `ocd-person` resolution
approach can be designed against real data — and so Dan can decide the routing
policy for the ~17% that are not individual legislators. The resolution method
is genuinely a design decision (and the most policy-sensitive output, since this
is the only *disclosed* lawmaker edge), so it is deliberately left for a session
with Dan in the loop.

## Why this matters

The current chain's lawmaker edge is the bill **primary sponsor**, *inferred*
via Open States — **not** a disclosed lobbying contact. `parties_lobbied` is the
genuinely disclosed "who was actually lobbied" field. It is richer than
sponsor-inference: it names leadership, committee staff, executive offices, and
agencies that a bill-sponsor join can never surface. This confirms the handoff's
framing — a real v1.1 **ingest** (re-pull + free-text normalization), not an
imputation. (WI does not impute this either; WI's lawmaker edge is also the bill
sponsor, and its IPF imputes *hours*, not lawmakers.)

## Coverage

- 2025 `client_semiannual` rows: **11,200,080**; rows with `parties_lobbied`
  populated: **11,191,171 = 99.9%** (row-grain; the dataset is denormalized
  ~1,300×, so this is row-level, not filing-level — but the field is essentially
  always present).
- The 2025 pull (`scripts/ny_pull_2025.py`) fetched only 9 fields and did **not**
  include `parties_lobbied`. A re-pull extending the `$select` is required.

## Value-kind distribution (representative)

Row-weighted over the **top 400 distinct values** (which cover ~91% of all
populated rows), via a `GROUP BY parties_lobbied` over the whole 2025 year
(`scripts/ny_probe_parties_lobbied.py`; raw in
`results/20260605_ny_parties_lobbied_top_distinct.json`):

| kind (coarse heuristic) | row weight | resolvable to `ocd-person`? |
|---|---|---|
| named legislator (`Senator X`, `Assembly member X`) | **83.0%** | yes — the core |
| executive office / agency (Governor, NYSED, ESD, CUNY, Division of the Budget) | 8.7% | no — not in the legislature |
| committee / caucus / program-&-counsel staff | 5.0% | partial — body, not a person |
| uncategorized (incl. "entire NYS Legislature" broadcasts) | 3.4% | no |

(The naive heuristic is non-exclusive for compound cells and will misfile some;
treat the split as ±a few points, not exact.)

### Top distinct values by row frequency (the head)

```
143,564  'NYS Senate Majority Program and Counsel Staff'
130,998  'NYS Assembly Majority Program and Counsel Staff'
130,983  'Executive Chamber/Office of the Governor'
 97,757  'A communication sent to entire NYS Legislature'
 87,370  'Department of Education (NYSED)'
 75,286  'Senator Andrea Stewart-Cousins'
 73,865  'A communication sent to entire NYS Assembly'
 69,720  'A communication sent to entire NYS Senate'
 65,803  'Governor Kathy Hochul (effective 8/24/21)'
 62,574  'Assembly member Carl E. Heastie'        # Speaker
 60,627  'Assembly member Harry B. Bronson'
 60,316  'Senator Shelley B. Mayer'
 ...     # then a long tail of named Senators / Assembly members
```

## Resolution-design implications (for the next session)

The free text decomposes into a **title prefix + name + noise suffix**, plus a
set of non-individual categories that need routing, not resolution:

1. **Title prefixes** to strip before name-matching: `Senator`, `Assembly
   member`, `Governor`, `Lieutenant Governor`, `Comptroller`, `Attorney
   General`, …
2. **Suffix / parenthetical noise** to strip: `, staff member` (very common — a
   named legislator's office, still resolves to that legislator); `(effective
   8/24/21)`; agency acronyms `(NYSED)` / `(ESD)` / `(CUNY)`.
3. **Named legislators (~83%)** → match `First [Middle] Last` against the OS
   `ocd-person` roster. The chain already resolves 213 distinct sponsors = the
   full NY legislature, so the target id space exists and is small. Note the
   disclosed contact is frequently **leadership** (Heastie, Stewart-Cousins,
   Gianaris) and **committee chairs**, who are rarely a given bill's sponsor —
   i.e. this edge will not duplicate the sponsor edge, it complements it.
4. **Non-individuals (~17%)** need an explicit routing decision (Dan's call):
   - executive offices / agencies (Governor's office, NYSED, ESD, CUNY, DOB) —
     not legislators; could be a separate `parties_lobbied_target` typed as
     `executive` / `agency`, or dropped from the lawmaker edge.
   - **"communication sent to entire NYS Legislature / Assembly / Senate"**
     (~240k rows) — a *broadcast*, resolvable to a chamber but not a person.
   - program / counsel staff for a chamber's majority/minority — a body, not a
     person.

   **Recommendation to surface, not decide:** model `parties_lobbied` as a
   separate edge table with a `target_kind ∈ {legislator, executive, agency,
   committee_staff, chamber_broadcast}` discriminator, resolving `ocd-person`
   only for `legislator`. This keeps the disclosed edge faithful (we don't
   overclaim a person where the filer disclosed an office or a broadcast) while
   still capturing the ~83% that *do* name an individual. **Don't overclaim to
   policymakers**: "disclosed contact" ≠ "lobbied this specific legislator" for
   the broadcast/office rows.

## Artifacts

- `scripts/ny_probe_parties_lobbied.py` — the probe (counts + 5k row sample +
  whole-year `GROUP BY` top-400).
- `results/20260605_ny_parties_lobbied_top_distinct.json` — top-400 distinct
  values with row counts (the representative distribution; **committed**).
- `results/20260605_ny_parties_lobbied_sample.json` — 5,000-row raw sample
  (clustered front-of-year; shape reference). **Gitignored** (raw API response,
  per branch hygiene); regenerate with the probe script.

## Not done (next session, with Dan)

Re-pull `client_semiannual` 2025 with `parties_lobbied` in the `$select`; design
the normalizer + `target_kind` router; resolve `legislator` rows to `ocd-person`;
decide the routing policy for the ~17% non-individual rows; then wire it as a
second, disclosed lawmaker edge alongside the inferred sponsor edge.

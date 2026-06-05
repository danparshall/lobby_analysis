# NY Phase 3 — real 2025 pull, firm-collapse bug, releases/ny

**Date:** 2026-06-05
**Branch:** ny-disclosure-explore

## Summary

Picked up the prior handoff (Phase 3 blocked on `data.ny.gov` egress). The block
was the **Web agent's** proxy, not this CLI machine — `curl` returned 200, so
Phase 3 was unblocked here. Ran the real 2025 pull, materialized the four
`releases/ny/` TSVs, validated, and wrote the release README from real
aggregates. The session's main event was a **major dollar-loss bug** that the
mandated large-filer spot-check surfaced, which we root-caused and fixed with TDD.

Two things diverged from the literal handoff, both surfaced and (the first) confirmed
with Dan. (1) The as-built `download_bulk_csv` can't serve the pull: `qym9-xzj6`
is all years (66.9M rows) with display-name headers the column-map can't consume.
Dan chose "extend the acquire module (TDD)", so we added `download_resource_csv`
(SODA `/resource/<id>.csv`, supports `$select`/`$where`, field-name headers) and
filed GH #39 on the `download_bulk_csv` gap. (2) The spot-check (Brown & Weinraub)
came up $2.8M short of an independent raw recompute — not a rounding nit but the
tip of a systematic 32% undercount.

## Topics Explored

- Egress reachability from this machine (open) vs the Web agent's block.
- Acquisition strategy: whole-view bulk (~55 GB, display headers, infeasible) vs
  filtered/projected SODA `/resource/.csv` (~1.9 GB, field-name headers). Probed
  throughput; rejected keyset pagination (`form_submission_id` is non-unique
  ~1,300× so any paging must slice by id *range*, never split a filing) in favor
  of a single streamed request + row-count verification.
- Memory feasibility of the in-memory `pd.read_csv` of 11.2M × 9 cols on 16 GB
  (fit fine, ~55 s).
- Root-cause of the spot-check mismatch → `form_submission_id` semantics.
- Focus-type + bill parse-rate coverage (Phase-3 probe the plan asked for).

## Provisional Findings

- **`form_submission_id` is the *client's* semi-annual report id, NOT a per-firm
  filing key.** One submission is shared across every firm a client retains —
  **2,249 / 8,613 (26%)** of 2025 submissions list >1 firm (Accenture's report
  735314 lists 6 firms, each with its own compensation). This breaks `grain.py`'s
  stated "submission primary key" assumption.
- **Two code defects flowed from that** (both fixed, TDD): `materialize_ny` keyed
  the filings dict + even-split on `(submission, client)` omitting the firm →
  co-retained firms collided via `setdefault`, dropping all but one firm's comp
  (**$108.9M / 32% loss**); and `grain.collapse_to_filing_grain` computed
  `n_bills_in_filing` by `form_submission_id` alone → every co-retained firm got
  the *union* of all firms' bills (wrong even-split denominator). Filing identity
  is now `(year, period, submission, firm, client)` = `FILING_KEY`.
- **Post-fix validation (two independent code paths, both exact):** Brown &
  Weinraub reconciles to the raw API at $24,217,924 (0 dropped); total comp
  matches a full from-raw recompute at **$345,762,462 (delta $0)**; even-split
  conservation holds with 0 violations across 4,328 bill-linked filings.
- **Release shape:** 4,373 clients · 1,333 firms · 10,870 firm-filings · 47,204
  bill links · 6,352 distinct bills (→ 5,449 base after suffix strip). 44% of
  comp ($153.1M) is on bill-linked filings.
- **Coverage:** State Bill = 87.7% of rows; **85.4%** of State-Bill rows parse to
  a canonical `bill_id`. Non-parsers are prose or non-canonical refs (e.g.
  "(S8417/A8888)") — a Phase-4 extraction opportunity.
- Lesser data-quality notes: coalition `beneficial_client` cells (semicolon list
  → one monster entity); unescaped `&amp;`; bill-number zero-padding inconsistent
  at source (`A00804` vs `A804`) → Phase-4 normalization needed; `bill_id` ==
  `bill_print_version` (both suffixed) by design.

## Decisions Made

- Acquisition: extend the acquire module with `download_resource_csv` (TDD), per
  Dan's pick. Single streamed filtered request + row-count verification; no
  paging. GH #39 filed on the `download_bulk_csv` gap.
- Filing identity = `(year, period, submission, firm, client)` everywhere. Joins
  of these tables MUST include `lobbyist_id`.
- Wrote `releases/ny/README.md` from real aggregates (deferred until after the
  real run, as the plan required).
- Did NOT split coalition `beneficial_client` lists or canonicalize bill padding
  this session — surfaced both to Dan, who decided them as Phase-4 work (below).

### Phase 4 decisions landed this session (Dan)

- **Decision 7 — split `beneficial_client` + even credit allocation.** Split the
  semicolon-delimited beneficiary lists into one client per beneficiary, allocate
  credit evenly (uniform, like the per-bill split — no disclosed per-beneficiary
  weight). Composes multiplicatively with the per-bill even-split:
  `comp_per_cell = C / (M_beneficiaries · N_bills)`, conserving `C`. Scoped as a
  Phase-4 chain/allocation transform; the Phase-3 release entity tables keep the
  raw disclosed string for source fidelity. **Open sub-question raised to Dan:**
  whether `NY_clients.tsv` itself should also split (that would re-cut Phase 3).
- **Decision 8 — bill-number padding → defer to Open States.** Source padding is
  inconsistent (`A00804` vs `A804`); canonicalize NY ids to OS's `identifier`
  format rather than inventing our own scheme. Acquire the OS NY bulk CSV *first*,
  read its real identifiers, then write the normalizer to match.
- Both recorded in the plan (Decisions 7 & 8 + reordered Phase-4 tasks) at
  `a53cc84`.

## Results

- [`results/20260605_ny_phase3_aggregates.md`](../results/20260605_ny_phase3_aggregates.md)

## Open Questions / Next Steps

- **Phase 4** — chain composer (`allocation/ny/chain.py`, no IPF) + Open States
  join. Now carries Decisions 7 & 8: split beneficiaries + even-allocate; defer
  bill-padding to OS (acquire OS CSV first). Measure OS match rate with vs.
  without the `-A/-B` suffix.
- **Whether `NY_clients.tsv` should also split coalition beneficiaries** (would
  re-cut Phase 3) — raised to Dan, awaiting steer.
- Whether to fold `lobbyist_bimonthly` (itemized expenses + individual people)
  into the build, and multi-year materialization (currently 2025-only).
- `LobbyingFiling.total_compensation` `Decimal`-typing pass; `&amp;` HTML-entity
  decoding (open follow-ups).

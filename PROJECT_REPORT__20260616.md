# `lobby_analysis` — Project Report

*Corda Democracy Fellowship, April–June 2026*

> A long-form companion to the [Corda funder summary](docs/CDF_FINAL_REPORT__20260616.md). The summary is ~250 words for external readers wanting the gist; this document is the project-level account — what we set out to do, what we built, what we learned, and what's queued up for whoever picks the work up next. It draws heavily on [`docs/RESEARCH_ARC.md`](docs/RESEARCH_ARC.md) (the architecture-of-record) and the [weekly updates](docs/weekly_updates/) (the running narrative).

---

## What this project is

`lobby_analysis` is open-source infrastructure to make **U.S. state lobbying disclosure data usable as an up-to-date input for democracy measurement** — filling the state-side gap that LobbyView (MIT, federal-LDA only) and OpenSecrets (federal-only / 31-state summary scorecard) leave open.

Policy capture — when private interests systematically shape government decisions at the expense of the public — is one of the clearest indicators of democratic backsliding. At the U.S. state level, lobbying disclosure data is the most direct signal of who is trying to influence policy and how much they're spending to do it. That data is hard to use today: state portals bury it in inconsistent formats, PDFs, and clunky search interfaces. The best existing aggregators cover only a subset of states and only summary totals — without the enrichment (which bills were lobbied on, what positions were taken, which officials received gifts) that makes the data actionable.

Project lead: **Suhan Kacholia** (Co-Founder, Analogy Group). Fellows: **Dan Parshall, Amina Rakhimbergenova, Gowrav Mannem**.

---

## Why no single rubric is the foundation

The research literature on state lobbying regulation has built scorecards for decades — PRI 2010, CPI Hired Guns 2007, Sunlight 2015, OpenSecrets 2022 — and academic measures (Opheim 1991, Newmark 2005/2017) alongside them. Each has its own atomization, weighting, and category structure.

The load-bearing finding: **Newmark 2017 found that two of the most-cited disclosure measures (PRI's and CPI's) correlate at r = 0.04** — they purport to measure the same thing and are essentially unrelated. This is not a measurement disagreement to arbitrate. It is evidence that *no single rubric should be privileged* as the project's foundation. (Verified at Newmark 2017 p.421–422 in a pre-merge factual audit of the compendium.)

So the project's deliverable is **not a "Corda Rubric"**, not a ranking, not a 50-state composite score. The deliverable is a **rubric-agnostic data layer** — structured, queryable, reproducible — that researchers can re-aggregate into PRI-style scorecards, FOCAL-style transparency assessments, or any other framing they prefer.

---

## The three pillars

The project is organized around three pillars, each with a different relationship to the data:

| Pillar | What it does | Role |
|---|---|---|
| **1. Statute → reference layer** | Read each state's lobbying statutes; emit a structured record of what the law *legally requires* to be disclosed | Scaffolding |
| **2. Portal → disclosure data** | Read each state's lobbying portal; extract structured filings + compose the principal → lobbyist → bill → lawmaker influence chain | **Product** |
| **3. Display** | Serve the unified data via public API and web interface | **Product** |

Pillar 1 is upstream scaffolding for Pillars 2 and 3. It earns its keep two ways: (a) it provides a common vocabulary — the typed-cell schema — that anchors what every state's release format inherits, and (b) the gap between what the statute *requires* (Pillar 1) and what the portal *actually exposes* (Pillar 2) is itself a research artifact worth publishing.

Full architecture: [`docs/RESEARCH_ARC.md`](docs/RESEARCH_ARC.md).

---

## What we built

### Pillar 1 — the rubric-agnostic reference layer

**Compendium 2.0** — 181 typed-cell rows specifying every observable about a state's lobbying-disclosure regime, drawn from nine published frameworks treated on even footing (PRI 2010, CPI 2015, CPI Hired Guns 2007, Sunlight 2015, Newmark 2005/2017, Opheim 1991, FOCAL 2024, OpenSecrets 2022, plus LobbyView 2018/2025 schema-coverage). Frozen 2026-05-13, merged to `main` 2026-05-14. Each row carries a typed cell (binary / integer / decimal / enum / etc.) so values from different states can be compared structurally.

**Statute-reading extraction harness.** Given a state's statute bundle (plain text) and the compendium row contract, the harness emits one structured record per (state, vintage) — what the statute legally requires across all 181 cells. Uses Anthropic Claude + OpenAI GPT-5.2 in parallel with three runs per cell for noise measurement; per-cell statute citations are produced and verified. Per-state cost ≈ $3, with run-to-run stability between 60–90% depending on state and model.

**Cross-state validation against a published rubric.** Five states (NY / WI / CA / TX / OH) × vintage 2015 × default-6-chunks × 2 models × 3 runs = 180 dispatches at $14.43, scored against the CPI 2015 published oracle. **Match rate 19/30 per-state-per-indicator after a free helper-vocab fix** (15/30 pre-fix). Per-state post-fix: NY 6/6 · WI 4/6 · CA 3/6 · TX 3/6 · OH 2/6. The +4 lift came from updating deterministic translation helpers, not from re-dispatching extraction — demonstrating that the schema reads statutes correctly, and most prior-art "disagreement" is vocabulary mismatch in the projection layer.

A queued **Round 2** ([#50](https://github.com/danparshall/lobby_analysis/issues/50)) would extend this to CO/IL/WA/FL/NC at ~$15 to confirm trends at N=10.

### Pillar 2 — three state releases, three structurally different shapes

The flagship Pillar 2 finding is what we call the **Anna Karenina principle**: every state's disclosure regime imposes its own data shape; per-state extraction pipelines are bespoke; what amortizes across states is the *output format*, not the *pipeline*. We shipped three state releases during the fellowship, and the three shapes are genuinely different:

**Wisconsin** ([`releases/wi/`](releases/wi/)) — shipped 2026-05-27. **115,229-row chain** at `releases/wi/chain/WI_chain_2025.tsv`. WI lobbyists report only aggregate hours, not per-pair compensation — so the lobbyist↔bill leg has to be *inferred* via iterative proportional fitting (IPF) over a bipartite (principal × lobbyist) graph with semester marginals. Architecturally: 5 IO modules + 4 allocation phases + per-CC matrix completion.

**New York** ([`releases/ny/`](releases/ny/)) — shipped 2026-06-08, merged 2026-06-12. **83,786-row chain** at `releases/ny/chain/`. NY discloses lobbyist↔bill compensation natively at the per-pair grain, so the chain is a pure JOIN — no inference needed. **$153,064,191 in bill-linked compensation reconciles exactly to the source semiannual filings.** A separate `parties_lobbied` edge layer (NY's disclosed-contact field) covers all 213 NY legislators; 98.6% of state-legislator-titled rows resolve to canonical Open States IDs.

**Ohio** ([`releases/oh/`](releases/oh/)) — shipped 2026-06-14, merged 2026-06-15. **1,589-row chain preview** at `releases/oh/chain/` + 305-row filings TSV. OH's shape is a third form: per-`(filing, position, sponsor)` cross-product, with position-shape normalization (subject-only positions preserved, not silently dropped) and OAC-routing (administrative-rule citations like JCARR classed separately from bills). OH's AER form has a **native lobbyist↔lawmaker gift/meal edge** that neither WI nor NY discloses — though our preview slice had zero itemized gifts (an empirical finding, confirmed by spot-check across all 305 cached filings: 93.8% report "No expenditures").

OH is a **preview release**; the full-corpus run (~45,605 AERs, ~$800 / ~24 hr via Anthropic Batches API + caching) is queued at [#35](https://github.com/danparshall/lobby_analysis/issues/35).

Each release ships with its own README documenting schema, conservation rules ("don't sum across multi-primary cross-product rows"), provenance, and reproducer commands. None require Postgres or external services to inspect — they're TSVs you can open in any tool.

### Pillar 3 — backend prototype

**Amina Rakhimbergenova** built a working backend prototype across May–June. Architecture:
- **v0** (2026-05-28): FastAPI + CLI + SQLite. Ingested Dan's WI release the same day — 4,798 filings, DoorDash YTD $2,183,623.40 matching the release headline exactly.
- **Postgres swap** (2026-06-05): docker-compose + psycopg3, byte-identical invariants vs SQLite.
- **Frontend + `/stats` endpoint** (2026-06-11): React/Vite **State Lobbying Disclosure Explorer** — stats bar, filer-name search, role filter, filings table/detail. `GET /stats` aggregates top spenders via a JSONB cast. 24/24 backend tests green; live-verified against real WI data.

This is "goal #3 — the simple interface" complete. It demonstrates that downstream consumers can stand the infrastructure up end-to-end with one `docker compose up`. The production-tier design lives in [`docs/active/ARCHITECTURE.md`](docs/active/ARCHITECTURE.md) (GraphQL + MCP topology, authored by Gowrav Mannem) as the design target the v0 prototype eventually grows into.

---

## What we learned (and now treat as load-bearing)

Three principles landed in June 2026 that reshaped how we think about the work — captured in [`docs/RESEARCH_ARC.md`](docs/RESEARCH_ARC.md):

**SMR-as-canonical.** The statute-reading record is the canonical, statute-literal data. Translation to any particular rubric's vocabulary (CPI's three-tier `{0, 50, 100}`, PRI's `YES/NO/100/50/0`) lives in a deterministic projection layer, not in the extraction prompts. Matching prior-art scores is a *check*, not the optimization target — and some residual mismatch is *defensible disagreement* with prior-art scoring (we documented two CPI 2015 errata candidates). This principle is the structural mitigation for Goodhart's-law pressure: "make the oracle happy" pressure lands on testable Python helpers, not on the prompts.

**Anna Karenina.** Per-state pipelines are bespoke. The shared infrastructure (typed-cell schema, canonical filing schema, projection helpers, `releases/<state>/` format) lives *downstream* of extraction. There is no "one chain composer fits 50 states." Budget **~3 working days per state** for chain composition at TDD discipline. No "50 states in 80 days" extrapolation from "3 states in 5 days."

**De-jure-only validation.** Reading statutes answers "what does the law say," not "what actually happens." The cross-state validation line is statute-only by design. *Practical* availability (whether portals actually expose the data the statute requires) is Pillar 2's axis, observed from portals — not inferred from statutes.

---

## What didn't ship

Honest accounting of work that was scoped but did not land in-window:

- **Compendium v2.2.** The May framing assumed v2.2 was a gating schema redesign. The June evidence (Phase B + Phase A vocab-fix loops) mooted most of that framing — what v2.2 was supposed to redesign turned out to be projection-translation engineering on top of v2.1. A real v2.2 design ledger does exist (the `regime` axis gap, ~50-state survey in [`docs/STATE_REGIME_SPLITTING.md`](docs/STATE_REGIME_SPLITTING.md)) but it is no longer the load-bearing next step.
- **OH full-corpus extraction** ([#35](https://github.com/danparshall/lobby_analysis/issues/35)) — the 316-filing slice is a preview, not a release.
- **Cross-state CPI Round 2** ([#50](https://github.com/danparshall/lobby_analysis/issues/50)) — CO/IL/WA/FL/NC at vintage 2015, ~$15.
- **WI campaign-finance leg.** FollowTheMoney scoping shipped 2026-06-03; full ingest blocked on expanded-access review ([#43](https://github.com/danparshall/lobby_analysis/issues/43), [#44](https://github.com/danparshall/lobby_analysis/issues/44)). **Caveat:** FTM is in sunset/integration mode pending the OpenSecrets merger — data current through 2024 cycle, site unmaintained.
- **NY multi-year backfill** (currently 2025 only) + `lobbyist_bimonthly` fold-in.
- **FOCAL Plans 3+4** ([#53](https://github.com/danparshall/lobby_analysis/issues/53)) — openness+timeliness items + top-level projector.
- **MI + NC disclosure pipelines.** Branches exist (`mi-disclosure-explore`, `nc-disclosure-explore`) but are stub-status. NC is a clean **legal-vs-practical** datapoint: public by statute (Chapter 120C), gated in practice behind JS-only per-record search or paid subscription.
- **Production-tier front-end.** The v0 backend prototype is the working artifact; the GraphQL + MCP topology in [`docs/active/ARCHITECTURE.md`](docs/active/ARCHITECTURE.md) remains a design target, not an implementation.

---

## How it's teed up

For whoever picks this up — us, a future cohort, or any other team — the public releases, the archived research lines, and the open task queue are all reproducible from `main`:

- **Three released chains on `main`** ([`releases/wi/`](releases/wi/), [`releases/ny/`](releases/ny/), [`releases/oh/`](releases/oh/)). Each has a self-contained `README.md` with schema, conservation rules, provenance, and reproducer commands.
- **22 archived research lines under [`docs/historical/`](docs/historical/)**, each with its branch's `RESEARCH_LOG.md`, `convos/`, `plans/`, and `results/` intact. Convo summaries are the institutional memory — "why was this decided" is recoverable per-decision.
- **~20 open task-labeled GitHub issues** capture the explicit pickup queue, from high-leverage (#35 OH full-corpus, #50 CPI Round 2, #43 FTM ingest) to surgical (#57 test-infra Postgres-fixture scoping, #58 OH extraction-brief form-type split).
- **The backend prototype is dockerized.** One `docker compose up` plus an ingest call brings up the WI release as a queryable Postgres-backed API with the React explorer.
- **The Plural Policy bulk-CSV pattern is reusable cross-state** (WI, NY, OH all use it for the lawmaker↔bill leg; [#42](https://github.com/danparshall/lobby_analysis/issues/42) tracks extracting it into a shared library).
- **Statute-line extraction is on a measured baseline.** σ_noise per state is recorded; helper-side fixes re-project stored data for free; the dispatch architecture is stable enough that adding the next five states to the validation is a one-line CLI change.

---

## Acknowledgments

Thanks to **Suhan Kacholia** for the framing pressure that turned "build a rubric" into "build the substrate for any rubric" — the r=0.04 finding would have been a footnote without that reframing. Thanks to **Amina Rakhimbergenova** for the backend prototype that turns the releases from TSVs-on-GitHub into something a journalist could query, and for picking the OH portal work up cleanly in May. Thanks to **Gowrav Mannem** for the architecture-of-record that the production tier will eventually build against. And thanks to the **Corda Democracy Fellowship** for hosting the cross-disciplinary collaboration this needed.

---

## Pointers

**Project framing:**
- [`README.md`](README.md) — what the project does and why, positioning vs LobbyView / OpenSecrets / Sunlight / FOCAL
- [`docs/LANDSCAPE.md`](docs/LANDSCAPE.md) — fellow-facing landscape report

**Architecture and findings:**
- [`docs/RESEARCH_ARC.md`](docs/RESEARCH_ARC.md) — three-pillar arc + Pillar 1 internals + Ralph-loop validation
- [`compendium/README.md`](compendium/README.md) — the Compendium 2.0 contract (181 rows, 9 source frameworks)
- [`compendium/disclosure_side_compendium_items_v2.tsv`](compendium/disclosure_side_compendium_items_v2.tsv) — the contract itself

**Tee-up for future contributors:**
- [`STATUS.md`](STATUS.md) — current branch state; "where everything is"
- [`docs/STATE_COVERAGE.md`](docs/STATE_COVERAGE.md) — per-state edge × attribute coverage matrix
- [Open task issues](https://github.com/danparshall/lobby_analysis/issues?q=is%3Aopen+label%3Atask) — the scoped pickup queue
- [`docs/historical/`](docs/historical/) — archived research lines with full provenance
- [`docs/CDF_FINAL_REPORT__20260616.md`](docs/CDF_FINAL_REPORT__20260616.md) — the funder-facing summary version of this report

**Weekly progress reports:**
- [`docs/weekly_updates/`](docs/weekly_updates/) — full series, April through June 2026
- [`docs/weekly_updates/2026-06-16.md`](docs/weekly_updates/2026-06-16.md) — end-of-fellowship narrative

**The three released chains (deep dives):**
- [`releases/wi/README.md`](releases/wi/README.md) — Wisconsin (IPF-based, 115K rows)
- [`releases/ny/README.md`](releases/ny/README.md) — New York (JOIN-based, 84K rows, $153M conserved)
- [`releases/oh/README.md`](releases/oh/README.md) — Ohio (preview, 1.6K rows; full corpus at #35)

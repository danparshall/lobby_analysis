# Architecture Decisions

State lobbying data infrastructure — architectural choices and the reasoning behind them.

This document captures the *why* behind the architecture, not the *what*. The goal is that a new contributor can read this and understand not just the shape of the system but the tradeoffs that produced it, so they can make consistent decisions when the document runs out.

---

## Framing

Three framings shape every decision below. When a choice below seems surprising, it usually traces back to one of these.

**This is a data quality pipeline, not a data movement pipeline.** The hard problem isn't moving bytes from state portals into storage — it's knowing which records are trustworthy, which are stale, which are wrong, and which changed since last time. The architecture is optimized around confidence tracking, replay, and observability, not throughput.

**Idempotency and replay are non-negotiable.** State portals go down. LLM extractions have bugs you find in month three. Enrichment sources update. The pipeline must be safely re-runnable end-to-end and at any intermediate stage. This constraint drives many storage and stage-separation decisions.

**Per-state heterogeneity is the dominant complexity.** Each state has its own data formats, quirks, and update patterns. A monolithic pipeline will be fragile; a fully bespoke pipeline per state duplicates work. The right shape is a thin common framework with state-specific modules implementing a shared interface.

---

## System overview

Six pipeline stages feed a common store, which is served by a query layer exposing two surfaces.

```
Discovery → Fetch → Parse → Normalize → Enrich → Publish
                                                    ↓
                                              Query layer
                                              ↙         ↘
                                       GraphQL API    MCP server
```

Each stage is independently replayable, has well-defined input/output, and writes to durable storage before the next stage runs. Don't combine stages to save a network hop — the separation is what makes debugging and replay tractable.

---

## Storage

### Postgres as the source of truth

One managed Postgres instance holds normalized filings, entities, bills, relationships, enrichment annotations, and pipeline state. At the fellowship's scale (hundreds of thousands of filings, millions of alias rows, embeddings on bills), a single well-tuned Postgres instance handles every access pattern we need.

Specific extensions relied on:

- `pg_trgm` for fuzzy entity name matching (trigram similarity on aliases)
- `pgvector` for semantic bill similarity and filing search
- Standard full-text search for keyword queries

**Managed hosting via Neon.** Managed because fellow time is more valuable than the savings from self-hosting. Neon specifically because database branching is genuinely useful for this project — a fellow can branch, try a destructive schema migration, and throw the branch away. Serverless pricing (scales to zero) matches the intermittent traffic pattern of a fellowship-budget project. Migrating to self-hosted Postgres later is straightforward if the project graduates and cost becomes a concern.

**We don't use a separate graph database.** The access patterns are relationship-heavy, which initially suggests Neo4j or similar. We don't have enough entities to justify the operational overhead, and recursive CTEs in Postgres handle 2–3 hop traversals fine at this scale. Revisit if we ever need 5+ hop queries at interactive latency.

**We don't use a separate vector database.** Pgvector handles millions of embeddings on modest hardware and — critically — lets us combine semantic search with structured filters in a single SQL query ("bills similar to X AND in state Y AND from 2023+"). A dedicated vector store would force us to orchestrate two queries and merge results in application code. Revisit only if performance limits force it.

**We don't use a separate search engine.** Postgres full-text search is adequate for the queries the API serves. Elasticsearch is powerful but adds an operational surface that isn't earning its keep at this scale.

### S3-compatible object storage for raw artifacts

Original PDFs, HTML snapshots, and cached fetcher responses live in object storage, keyed deterministically:

```
{state}/{filing_id}/{fetched_at_iso}/raw.{ext}
```

**Never overwrite — every fetch is a new object.** Versioning is free storage and priceless debugging. If a filing changes on the state portal, we have both versions. If we discover three months in that our Texas parser was wrong, we can re-parse every historical version without re-fetching.

**Cloudflare R2 over AWS S3.** R2 is S3-compatible, noticeably cheaper for storage, and charges zero egress fees. For an open-source project that will have external researchers downloading raw artifacts, zero egress meaningfully lowers the cost of being useful.

### What we preserve everywhere

Two rules applied at every layer where extracted data exists:

- **Raw text is preserved alongside every normalized value.** Texas gives us "$150,000 – $199,999" as a checkbox range. We store the range *and* the original string. A caller can decide whether to use the exact value (null for TX), the min/max, or the raw text.
- **Confidence scores and source URLs travel with every enriched field.** These aren't metadata hidden in a separate table — they're part of the API contract, because journalists using this data need to know which claims are rock-solid and which are inferred.

---

## API layer

### FastAPI over Django

The API is a read-heavy, stateful-database-backed service. Django is heavy for this workload — we don't need admin UI, auth, ORM migrations, or templates in the public API. FastAPI is lighter, has better async support (important for the MCP server making concurrent enrichment lookups), and its type-hinting story means fewer bugs in a codebase three people are touching simultaneously.

Stack:

- **FastAPI** — API framework
- **Strawberry** — GraphQL layer
- **SQLAlchemy** (async) — database layer
- **Pydantic** — validation and structured output contracts (used heavily for LLM output validation)

A separate small Django admin app pointed at the same database can serve the low-confidence extraction review queue. That's admin UI, not public API — separating them keeps the public service light.

### GraphQL for the programmatic API

The data model is a graph: entities connected to filings connected to bills connected to legislators connected back to entities via gifts. REST either explodes into many narrow endpoints (`/companies/{id}`, `/companies/{id}/filings`, `/companies/{id}/bills`, etc.) or picks one traversal direction and makes others awkward. GraphQL lets callers ask for exactly the slice they need across entity boundaries in a single query.

Schema principles:

- **Entity as interface, concrete types per entity category.** `Company`, `TradeAssociation`, `Lobbyist`, and `GovernmentOfficial` all implement `Entity` but expose type-specific fields. Lets search return `[Entity!]!` while still surfacing `Company.ticker` or `TradeAssociation.members` via fragments.
- **Confidence and provenance are first-class, not metadata.** Every field that's extracted, inferred, or enriched exposes its confidence score and source reference.
- **Ranges modeled explicitly.** `MoneyAmount` carries `exact`, `min`, `max`, `rawText`, and `isRange`. Never collapse ranges to midpoints silently.
- **Relay Connection pattern for pagination.** Boring industry standard; every GraphQL client supports it. Don't invent custom pagination.
- **Both primitive and composite queries exist.** `entity`, `filing`, `bill` are primitives for sophisticated callers. `lobbyingByTopic`, `influenceMap`, `giftsFromLobbyistsOnBill` are composite queries that handle common cases well without forcing callers to figure out how to compose primitives correctly.

Guardrails from day one:

- **DataLoader pattern for resolvers** — prevents N+1 database queries.
- **Mandatory pagination on all list fields.**
- **Query depth limit** (7 levels).
- **Query complexity limit** — depth alone doesn't catch a 3-level query requesting 10,000 items with 100 fields each. Compute cost per query, limit on that.
- **Field-level authorization from day one** — internal fields like reviewer notes and raw LLM outputs are marked with `@auth(requires: ADMIN)` directives. Retrofitting this is painful because callers end up depending on fields they shouldn't have access to.

### MCP server with opposite design principles

The MCP server exposes the same data to LLMs, and the right design principles are *opposite* to the GraphQL API:

- **Tools are task-shaped, not data-shaped.** Tools answer questions users actually ask, not expose database operations. LLMs compose primitive tools poorly — they forget state, hallucinate IDs, plan suboptimal multi-step queries.
- **Tools return rich, self-contained results.** A filing comes back with its entities, its bills, and its provenance inline — not as references that require follow-up calls.
- **Few and broad, not many and narrow.** Every additional tool eats context budget and adds a decision point where Claude can pick wrong. Five to seven well-designed tools beat twenty narrow ones.
- **Inputs tolerate natural language.** Tools accept "Chevron" not a UUID, "climate disclosure" not a subject code. Fuzzy resolution is the tool layer's job, not the caller's.
- **Provenance is inline in the response body.** Claude can't "check a separate field" the way a UI can — sources and confidence scores need to appear in the response where the LLM will reason over them.

Planned tool surface:

1. `search_entities` — resolve natural language names to canonical entities
2. `get_influence_map` — full picture for one entity (direct + indirect lobbying, cross-state patterns, relationships)
3. `find_lobbying_on_topic` — policy-first query, handles both specific bills and semantic topics
4. `trace_connection` — shortest-path relationship queries between two entities
5. `get_timeline` — temporal aggregations with breakdowns
6. `get_legislator_activity` — gifts received, bills sponsored, lobbyist meetings, cross-references
7. `search_filings` — escape hatch for queries not fitting the other six

Every response follows the same shape: `summary` (a paraphrasable one-paragraph summary), `data` (structured results), `provenance` (coverage caveats), `sources` (citation-ready references).

### Deployment shape

**Fly.io** for the API and MCP server. Runs Docker containers, sensible pricing, puts the service in the same region as the database (matters for latency), fast cold starts, good Docker ergonomics.

**The MCP server is the same FastAPI service, separate entry point.** Not a separate deployment. Shared code, shared database connection pool, shared observability. Split only if there's a concrete reason.

**Not Vercel, not Lambda, not Kubernetes.** Vercel and similar serverless/edge platforms are built for stateless frontends; they're a bad fit for a database-heavy Python API (cold starts, connection pool exhaustion, execution time limits). Lambda has real operational overhead (IaC, connection pooling, layer management) that doesn't pay off at this scale. Kubernetes is always the wrong answer for a three-person fellowship project.

---

## Scraper infrastructure

### Separated from the API

Scrapers run on different infrastructure than the API. Scrapers have unpredictable memory usage (PDF parsing spikes), unpredictable CPU (LLM calls block), long-running operations, and different failure modes (IP bans, rate limits, portal downtime). Mixing them with the API means API latency degrades whenever scraping is active.

**Fly Machines** (ephemeral VMs spun up per job) for scraper workers. Workers pull from a Postgres work queue, do their thing, write results, exit. Horizontal scaling is just running more instances.

### Orchestration via Postgres, not Airflow

For a pipeline of six sequential stages with per-state parallelism, Postgres-backed work queues are sufficient and debuggable. Airflow, Prefect, Dagster are good tools for complex DAGs with many interdependent jobs — we don't have that.

Tables:

- `pipeline_runs` — tracks each run of each stage per state, with status, timings, record counts, error summaries. This is the operational dashboard.
- `work_queue` per stage — workers claim atomically via `UPDATE ... SET status='claimed' RETURNING ...`
- A simple scheduler (cron, or GitHub Actions scheduled workflows) enqueues discovery runs and triggers downstream stages.

Every worker wraps its run in error-handling that guarantees a `pipeline_runs` record on exit even on uncaught exceptions. A worker that crashes without recording its failure is one we discover is silently broken three weeks later.

### Rate limiting and politeness

State portals vary widely in tolerance. Some are fine with 10 req/s; some IP-ban at 1 req/s sustained. Per-state rate limits live in the common framework, configurable per state module. A token bucket (shared across workers via Redis or Postgres advisory locks) is better than naive sleeps because it lets us spend rate budget on the most important work.

Politeness is ethical and operational both — we're building something that needs to exist long-term; don't burn goodwill with state IT teams in month one. Identifiable User-Agent pointing to a contact page, respect robots.txt even when legally unnecessary, aggressive backoff on 5xx responses.

### IP diversity escalation path

Start polite. Escalate only when a specific state blocks us, and escalate only for that state:

1. **Aggressive rate limiting + identifiable User-Agent** — sufficient for most states.
2. **Residential proxies** (Bright Data, Smartproxy) for states that block cloud IPs aggressively. Budget $50–200/month.
3. **Multi-region deployment** for egress IP diversity.

### Headless browsers only when necessary

Playwright is the standard if we need JavaScript-rendered pages, but it's heavy (memory, startup time, brittleness). For each state, first check for hidden JSON APIs (network tab inspection), structured downloads, or bulk exports. Often the "portal" is a thin UI over a queryable backend. Exhaust those before reaching for Playwright.

---

## LLM infrastructure

### Single client wrapper, not scattered calls

Every LLM call goes through one client wrapper handling: retries with backoff, structured output validation (Pydantic schemas), cost tracking, prompt versioning, and caching. Not ten different call sites each reinventing the pattern.

Hash-based caching of `(input, prompt_version, model)` tuples means re-running the pipeline doesn't re-call LLMs for unchanged inputs. This falls out naturally from the stage-based architecture: parsed records are stored durably, so Stage 3 re-running against the same raw PDF produces a cache hit.

### Where LLMs run in the pipeline

The rule from the project plan: LLMs should not be in the hot path for every record. They're used to:

- **Build extractors** (generate parsing code for new PDF formats, map a state's fields to the schema) — this is offline work.
- **Parse in Stage 3** as fallback when rule-based parsers can't handle a record. Confidence-routed: deterministic parser tried first, LLM only for records where confidence is below threshold.
- **Resolve entities in Stage 4** as the last stage after deterministic + fuzzy + SEC EDGAR lookup. Always given a shortlist ("is this one of these five?") rather than asked to resolve from scratch.
- **Enrich in Stage 5** for specific tasks (SEC 10-K narrative parsing, bill-to-lobbying inference) with explicit budget caps and caching.

### Provider strategy

**Anthropic API for parsing, entity disambiguation, and narrative extraction.** Vision capabilities handle scanned and image-heavy PDFs; structured output support pairs well with the Pydantic validation layer.

**OpenAI `text-embedding-3-small` for embeddings.** Cheap and good enough for bill similarity. Semantic precision here is forgiving.

### Non-negotiable practices

- **Prompt versioning with a regression test suite.** Every prompt has a version. 20–50 hand-labeled filings per hard state form the eval set. Every model change or prompt edit runs against the eval set before shipping; CI blocks PRs that regress precision or recall.
- **Cost tracking per call, per prompt version, per state.** Stored in a table, visible on dashboards. LLM costs will be the surprise budget item; we need visibility from day one.
- **Budget caps per worker per day. Fail closed, not open.** A runaway worker burning $500 overnight is a real failure mode.
- **Structured output validation, always.** Never parse whatever JSON the LLM emits. Define a Pydantic schema, validate every extraction, send failures to a retry path with a more explicit prompt. Track success rate per prompt version over time — silent degradation after a model update is the failure mode to watch for.

---

## Entity resolution

Entity resolution is architecturally central because every cross-state query depends on it. Getting it wrong poisons the API's most valuable queries in subtle ways.

### Three tables, not one

- **`canonical_entities`** — the source of truth for "what is a unique thing in the world." Entity type, canonical name, metadata (ticker, EIN, SEC CIK), confidence.
- **`entity_aliases`** — every raw name ever seen, pointed at a canonical entity. Resolution method (exact / fuzzy / LLM / human / SEC EDGAR), confidence, source state, first/last seen.
- **`entity_relationships`** — the graph: parent_of, subsidiary_of, funds, member_of, employs, represented_by, officer_of, board_member_of. Each relationship has an evidence source and confidence.

Aliasing and relationships are fundamentally different operations with different correctness criteria. Merging two aliases that shouldn't be merged corrupts the data (Chevron's filings now include Chevrolet's). Adding a wrong relationship is a fixable annotation error. Different review workflows, different confidence thresholds, different audit trails.

### Resolution pipeline: cheapest first

1. **Deterministic matching** — normalize (lowercase, strip punctuation, split corporate suffix), hash, exact-match against known aliases. Handles 60–70% of cases at zero cost.
2. **Fuzzy matching** — trigram similarity via `pg_trgm` against known aliases. Auto-link above 0.85 if suffix-stripped names match; queue for review between 0.7–0.85.
3. **External identifier lookup** — SEC EDGAR full-text search for companies (yields CIK), IRS EIN lookups for tax-exempt orgs. Highest-leverage enrichment we do — ground-truth identity for public companies and large nonprofits.
4. **LLM judgment** — for names surviving 1–3, batch and send with a candidate shortlist. Auto-apply above confidence 0.9; otherwise queue for review.

### Reversible merges and the review queue

Merges are soft (set `merged_into` on the loser, don't delete). All queries transparently follow merge chains. Unmerging is clearing `merged_into`. Build this from day one; retrofitting is painful.

The human review queue (merges below auto-apply threshold) needs a simple UI — a Django admin page or Retool dashboard over the review tables is sufficient. Reviewers are the fellows during development and possibly journalists/researchers later.

### The failure mode to guard against

The worst outcome isn't low recall (missing links). It's high-confidence wrong merges, which poison cross-state queries in subtle ways that are hard to detect downstream. Defenses:

- Require multiple independent signals for auto-merge at the highest confidence tier
- Flag merges that combine entities with conflicting metadata (different CIKs, EINs, states of incorporation)
- Periodic audits sampling high-confidence merges for spot-checks

---

## Observability

"Checking logs" is not observability. The following surfaces exist from week one.

### Per-state health dashboard

For each state: filings discovered/fetched/parsed/normalized in the last 24h and 7d, parse confidence distribution, enrichment coverage, last successful run of each stage, error rate. A single page per state that answers "is this state healthy?" at a glance.

### Confidence drift tracking

Parse confidence should be roughly stationary over time. If Texas drops from 0.91 to 0.78 over a month, something changed — state updated their template, LLM model drifted, prompt got worse. Alert on significant shifts.

### Coverage reports

Sample-based comparison against state portals' own counts: what percentage of filings that exist in the state's records do we have in our database? This is the single most important correctness metric.

### Cost tracking

LLM costs per state per enricher per day, with anomaly alerts.

### Dead letter queue visibility

Every stage has a DLQ for failed records. The DLQ needs visible state — what's stuck, why, and for how long. Records sitting in a DLQ unreviewed for a week are a sign the pipeline is effectively broken even if it looks healthy.

### Tooling

- **Logs:** Logtail (Better Stack) or Axiom. Managed aggregator, not files on disk.
- **Error tracking:** Sentry. Every uncaught exception goes here.
- **Metrics and dashboards:** Grafana Cloud (free tier).
- **Pipeline-specific dashboards:** Retool or Metabase over the `pipeline_runs` table. Generic APM is bad at showing "when did the Texas discovery job last succeed."

---

## CI/CD

**GitHub Actions.** Code lives there, it's free for public repos (which this is, as open-source infrastructure), sufficient for the workflow.

- Tests on every PR
- `ruff` and `mypy` on every PR
- Deploy to staging on merge to main
- Deploy to production via manual trigger or tag
- **Regression test suite on any PR touching parsing or prompts** — the hand-labeled extraction eval runs against the changed prompt/parser; CI blocks on regressions

The last point is the one most projects skip and regret. It's what prevents silent extraction quality decay.

---

## Secrets and config

- **Secrets:** environment variables via the hosting platform's secrets UI. No `.env` files in the repo. Don't build a custom secrets system.
- **Shared configuration** (per-state rate limits, parser thresholds, prompt templates): versioned config files in the repo. Reviewable, rollbackable, testable.

---

## What we explicitly don't build

Patterns that sound reasonable and that we're not reaching for, with reasons:

- **MongoDB or document stores** — we have relational data with complex joins.
- **Elasticsearch** — Postgres full-text + pgvector cover the access patterns without the operational burden.
- **Kafka, RabbitMQ, SQS** — Postgres work queues are sufficient at this scale and debuggable with SQL.
- **Redis** — no specific caching need that isn't solved by Postgres materialized views.
- **Custom authentication** — if the API needs auth later, use a managed service (Clerk, Auth0, or the hosting platform's built-in). Don't build auth.
- **A web frontend** — not needed for v1. The API, MCP server, and docs are the product. Journalists and researchers are the users, and they want programmatic access or LLM-mediated access, not another dashboard.
- **Separate OLTP and analytics databases** — premature at this scale. A read replica is the first scale-out move if API traffic warrants it.
- **Subscriptions / real-time GraphQL** — useful for the monitoring stretch goal; skipped for v1.

---

## Cost sketch

Order-of-magnitude steady-state monthly costs:

| Component                          | Monthly (USD)    |
| ---------------------------------- | ---------------- |
| Postgres (Neon)                    | $20–50           |
| Object storage (R2)                | $5–20            |
| API hosting (Fly.io)               | $25–75           |
| Scraper workers (Fly Machines)     | $20–50           |
| LLM API calls                      | $50–500          |
| Observability (free tiers)         | $0               |
| Proxies (if needed)                | $0–100           |
| **Total**                          | **~$150–800**    |

LLM cost is the widest-variance line and where prompt discipline, caching, and confidence-routed extraction pay off most. Initial historical backfill (2023–2025) will spike costs for a few weeks, then drop to steady-state as we process only new filings.

Before committing to vendors, check open-source credit programs (Anthropic startup credits, GitHub sponsorships of open-source infra, cloud provider open-source programs). A credit grant covers most of a fellowship's infrastructure costs.

---

## Decision log

When these choices need revisiting:

| Decision                         | Revisit when                                                    |
| -------------------------------- | --------------------------------------------------------------- |
| Managed Postgres (Neon)          | Cost becomes a line-item concern post-fellowship                |
| Pgvector instead of vector DB    | Vector query performance degrades below acceptable latency      |
| Postgres work queues vs. Airflow | The pipeline grows cross-stage dependencies beyond linear order |
| Single Fly.io region             | External researchers report latency issues                      |
| No Redis                         | A specific cache pattern can't be served by materialized views  |
| No headless browsers             | A priority state has no structured API and JS-gated portal      |
| LLM in hot path of Stage 3       | Per-filing LLM cost > $X or latency budget blown                |

Each of these is a reasonable default for the current scale; each has a specific signal that would justify changing it.

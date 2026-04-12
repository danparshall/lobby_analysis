# Open Civic Data Schema Analysis

**Provenance:** `docs/active/research-prior-art/convos/20260410_scoping-kickoff.md`
**Last updated:** 2026-04-10
**Branch:** `research-prior-art`
**Source repo:** github.com/opencivicdata/docs.opencivicdata.org (cloned locally during the session for direct reading of OCDEP proposals)

## Purpose

Decide whether the lobbying pipeline should adopt, extend, or parallel the Open Civic Data schema. This file documents the analysis of the four OCD Enhancement Proposals (OCDEPs) that are most relevant, the decision to depend on Open States without forking it, and the schema direction for a future lobbying OCDEP.

## The OCD Ecosystem in One Paragraph

Open Civic Data is a family of schemas and tools maintained (historically by Sunlight Foundation, now effectively by Plural Policy via Open States) to represent civic information — people, organizations, bills, votes, events — in a standardized way across jurisdictions. The schemas are refined via OCDEPs (Enhancement Proposals), which are numbered, RFC-style documents in the `opencivicdata/docs.opencivicdata.org` repository. OCDEPs have statuses: Draft, Accepted, Withdrawn, Deprecated. Open States (bills, legislators, votes for all 50 states) is the largest production consumer of the schema.

## OCDEP 5 — People / Organizations / Posts / Memberships (Accepted)

**Author:** James Turk, 2014. **Status:** Accepted.

Adopts **Popolo** (http://www.popoloproject.com/) for the entity model:
- **Person** — an individual
- **Organization** — a company, interest group, government body, etc.
- **Post** — a role that can be held within an organization (e.g., "Senator for Delaware")
- **Membership** — a time-bounded assignment of a Person to an Organization (optionally via a Post)

The proposal **explicitly omits fragile name segmentation fields** (first/middle/last as separate columns) in favor of a single display name. This is a good choice because name segmentation is a source of bugs that never end.

**Constraint for our use case:** OCDEP 5 does not allow Organization-Organization memberships. An organization cannot be a "member" of another organization in the Popolo model; only people can be members of organizations. For lobbying data this matters because we need to represent corporate hierarchies (a subsidiary lobbying on behalf of a parent, or a trade association lobbying on behalf of its member companies). The workaround is to represent the relationship as a separate `OrganizationRelationship` entity or similar, not as a Membership.

**Decision:** **Adopt OCDEP 5 for people and organizations** in the lobbying pipeline. The fit is good, the constraint is manageable, and interoperability with Open States is a direct benefit.

## OCDEP 6 — Bills (Accepted)

**Author:** James Turk, 2014. **Status:** Accepted.

Defines the schema for legislative bills, including bill identifiers, actions, sponsors, versions, and related documents. Contains an **honest admission** that primary-vs-cosponsor terminology varies jurisdiction-by-jurisdiction — which is a good sign for a schema designer (acknowledging the irreducible variation rather than pretending it can be normalized away).

**Gap for our use case:** OCDEP 6 has no concept of **extraction provenance** or **confidence scores** for fields that were derived rather than directly entered. This matters for us because our pipeline will extract bill IDs from free-text lobbying descriptions using LLM + regex, and downstream consumers need to know (a) which field came from structured data vs. extraction, and (b) how confident the extraction was.

**Decision:** **Depend on Open States for bill data** (via its API). Do not re-scrape or re-model bills. When the lobbying pipeline references a bill, it references it by Open States' canonical identifier. For extraction provenance, introduce a separate provenance layer in our own schema (see `schema-design-questions.md`) rather than trying to modify OCDEP 6.

## Withdrawn Disclosures Proposal — Cautionary Tale

**Author:** Bob Lannon (Sunlight Foundation). **Status:** Withdrawn.

This is the OCDEP that is most directly relevant to our project, and it was **withdrawn**, which is itself informative. The proposal tried to represent lobbying disclosures using existing OCD primitives — specifically, by overloading the `Event` entity and using `related_entities` with free-text `note` fields to distinguish roles (client, registrant, lobbyist, target agency).

Why this failed:
1. **No itemized financial data.** Events have a single `amount` or similar; lobbying filings have multiple itemized expenditure categories that need independent representation.
2. **Free-text bill linkage.** The proposal stored lobbied bills as free-text references rather than typed links to Bill entities, giving up the connection to OCDEP 6.
3. **Event has wrong semantics.** An Event in OCD is meant to have a specific date/time and location (a committee hearing, a rally). Lobbying filings are reporting-period aggregates over a quarter or a year, with no point-in-time location. Overloading the Event required placeholder values and role confusion.
4. **Participants flattened into an untyped list.** The `related_entities` structure does not distinguish the *role* of each participant (client vs. registrant vs. lobbyist vs. target) in a typed way — it relies on free-text notes, which means downstream queries have to parse English strings to understand the data.
5. **No amendment handling.** Lobbying filings are routinely amended, and the Event model does not handle supersession lineage at all.

**Decision:** **Do not follow this pattern.** The lobbying pipeline needs first-class entities (LobbyingFiling, LobbyingPosition, LobbyingExpenditure, Gift, LobbyingEngagement), not an overloaded Event. This is not a criticism of the original proposal author — they were trying to minimize the schema change, which is a reasonable design instinct — but the downstream consequences of the retrofit are severe enough that the proposal was withdrawn.

## Draft Campaign Finance Filings Proposal — Pattern to Adopt

**Author:** Abraham Epton. **Status:** Draft.

This proposal models campaign finance filings (which share structural DNA with lobbying disclosures: periodic, amended, itemized transactions, filed by a regulated entity to a regulator). It uses a three-level structure:

- **Filing** — the top-level document. One row per filed report.
- **Sections** — logical subsections within a filing. One row per section.
- **Transactions** — itemized rows within a section. One row per reportable transaction.

Amendment handling uses a `filing_actions` sub-entity with `is_current` and `supersedes_prior_versions` booleans. Each amendment is its own Filing row with an explicit link to the one it supersedes, so the amendment lineage is queryable rather than embedded.

The proposal includes an explicit **philosophy** section that is worth adopting wholesale: *minimize transformation, store source faithfully, push transformations into a separate layer.* This is the right design discipline for our project too, because state lobbying filings vary so much in format that any aggressive normalization at ingest time is going to mangle some state's semantics.

It also includes a candid **"Questions to answer"** section where the author lists unresolved design questions rather than pretending they are resolved. This is a format we should steal for our own schema proposal — see `schema-design-questions.md` in this directory.

**Decision:** **Adopt Epton's Filing → Sections → Transactions structure and the `filing_actions` amendment pattern** for the lobbying schema. Also adopt the "store source faithfully, transform in a separate layer" philosophy.

## Open States Dependency Analysis

Open States is the largest production consumer of the OCD schema. It covers bills, legislators, votes, committees, and hearings for all 50 states. It was originally a Sunlight Foundation project and is now maintained by Plural Policy (commercial), which operates a free public API alongside its commercial offerings.

### The fork-vs-depend decision

**Option A: Fork Open States and add lobbying coverage.** Gives full control over the schema and lets us add lobbying as a first-class concept in the same repo. Costs: ongoing maintenance burden for 50 state bill scrapers, divergence from upstream over time, duplicated work on things unrelated to lobbying, political awkwardness with an active open-source project.

**Option B: Depend on Open States as an external service.** The lobbying pipeline is a separate project that uses Open States as a bill/legislator lookup service, referencing entities by their canonical OS identifiers. Costs: we are dependent on Plural Policy's continued operation of the free API (mitigation: pin version, keep a scraper-only fallback option documented), and we cannot extend the OS schema without going through OCDEP review.

**Decision: Option B.** The scope multiplier for Option A is roughly 2–3× the initial 8-state work and 5×+ at full 50-state scale, and almost all of that added work is on bill/legislator scraping which Open States already does well. Reinventing that work is strictly negative-value.

### Mitigations for Open States dependency risk

1. **Pin the Open States API version** in the pipeline's dependency configuration. Don't auto-track breaking changes.
2. **Document a scraper-only fallback path** — the pipeline should be able to function (with degraded bill linkage) if the hosted Open States API becomes unusable.
3. **Cache Open States responses locally** for any entity the pipeline has processed, so a temporary API outage doesn't break historical data access.
4. **Track OS project health** — if Plural Policy de-prioritizes the free API, we need to know early.

## Schema Direction Summary

1. **Adopt Popolo via OCDEP 5** for Person / Organization / Post / Membership.
2. **Depend on OCDEP 6 (Bills) via Open States** rather than re-modeling bills.
3. **Do not follow the withdrawn Disclosures proposal** — first-class entities, not overloaded Events.
4. **Adopt Epton's draft Campaign Finance Filings pattern** — Filing → Sections → Transactions with `filing_actions` amendment handling and the "store source faithfully, transform in a separate layer" philosophy.
5. **Introduce new first-class entities for lobbying:** LobbyingFiling, LobbyingPosition, LobbyingExpenditure, Gift, LobbyingEngagement.
6. **Add two things OCD currently lacks:**
   - Field-level extraction provenance with confidence scores (for any field populated by LLM or regex rather than structured source data).
   - A compliance-tracking layer (Violation, Referral, Penalty) that links back to Filings and Filers.

The detailed open design questions on each of these are in `schema-design-questions.md`.

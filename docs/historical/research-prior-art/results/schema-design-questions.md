# Schema Design Questions — Lobbying Pipeline

**Provenance:** `docs/active/research-prior-art/convos/20260410_scoping-kickoff.md`
**Last updated:** 2026-04-10
**Branch:** `research-prior-art`
**Format note:** Following Abraham Epton's OCDEP draft for Campaign Finance Filings, which includes an explicit "Questions to answer" section listing unresolved design decisions rather than pretending they are resolved. This is the right level of honesty for a scoping document.

## Purpose

Enumerate the design questions that need answers before a formal lobbying-schema proposal can be written. These are the questions that, if handwaved, will cause pain later. Each question has a tentative direction where one has emerged during scoping, but the direction is explicitly provisional.

## Entity Types

### Q1. What are the first-class lobbying entities?

**Tentative list:**
- **LobbyingFiling** — the top-level filed document. One row per filed (periodic) report.
- **LobbyingFilingSection** — a logical subsection within a filing (e.g., expenditures, gifts, positions). One row per section per filing.
- **LobbyingPosition** — an interest group's position (Support / Oppose / Engage / Mention) on a specific bill during a specific reporting period, derived from text extraction.
- **LobbyingExpenditure** — an itemized expenditure item (who was paid, how much, for what purpose).
- **Gift** — gifts reported to officials (where required by state law). Separate from expenditures because the data model and disclosure requirements differ.
- **LobbyingEngagement** — a specific act of lobbying (meeting, phone call, written communication) where disclosed. Most states do not require contact-level logging; this entity is relevant only for the subset that do.

**Open:** Whether to add **LobbyistRegistration** as a separate entity from LobbyingFiling. A registration is a one-time (or occasional) filing distinct from the periodic activity reports, and it creates the legal predicate for activity reports. Leaning yes.

### Q2. Should the compliance layer be first-class entities or a derived view?

- Option A: First-class entities — **Violation**, **Referral**, **Penalty** — linked back to Filings and Filers.
- Option B: A derived view computed from Filing data and external enforcement records.

Leaning Option A because enforcement actions are the **policy payload** the project is ultimately trying to surface. If compliance signal is hidden behind a query-time computation, downstream consumers (journalists, researchers, policymakers) will not find it. First-class entities make it discoverable by default.

**Open:** How to handle the asymmetry between states where enforcement records are publicly available (CA FPPC, WA PDC) and states where they are not. The schema has to accommodate "this filing is known to be late but we have no Referral record for it" without making Referral mandatory.

### Q3. How are corporate hierarchies represented?

OCDEP 5 / Popolo does not allow Organization-Organization memberships. We need a way to represent (a) subsidiary-of-parent relationships, (b) trade-association-member-companies relationships, and (c) subcontracted-lobbyist relationships.

**Tentative direction:** A separate **OrganizationRelationship** entity, typed with relationship categories (`subsidiary_of`, `member_of`, `subcontracts_to`, etc.), time-bounded with start/end dates, and linked to a provenance source.

**Open:** Whether to invest in detecting hierarchies automatically (via external sources like OpenCorporates and SEC filings) or only store relationships that are directly disclosed in lobbying filings. Leaning toward "direct disclosures only in v1, automatic detection in a later enrichment layer."

## Amendment Handling

### Q4. How is filing lineage represented?

Adopt Epton's `filing_actions` pattern:
- Each amendment is its own **LobbyingFiling** row with a full copy of the data as filed.
- A `filing_actions` sub-entity records the relationship: `supersedes` / `amends` / `withdraws` etc. with `is_current` and `supersedes_prior_versions` booleans.
- Queries that want "the current state of the record" filter on `is_current = true`. Queries that want the audit trail traverse `filing_actions`.

### Q5. What about states that don't track amendment lineage?

Several states just overwrite filings or accumulate new versions without explicit links. In those cases, the pipeline cannot reconstruct lineage from the source data.

**Tentative direction:** Support a **"provenance-only, no lineage"** fallback mode. When the source state provides a timestamp but no explicit "this amends filing X" link, the pipeline records the timestamp and marks the `filing_actions` link as `inferred_by_timestamp_ordering` with a corresponding confidence field. Downstream consumers can decide whether to trust the inference.

**Open:** Whether to attempt to infer amendment lineage by matching filing content (filer + reporting period + overlapping transactions). Leaning no for v1 because the error modes are subtle — a filer who files twice for the same period with non-overlapping transactions might be (a) correcting an omission or (b) filing for two separate clients in the same period, and those are indistinguishable without external context.

## Provenance

### Q6. What level of granularity does provenance need?

Options, from coarsest to finest:
- **Filing-level** — record the scraping source and timestamp per filing.
- **Section-level** — record provenance per LobbyingFilingSection.
- **Field-level** — record provenance per individual field within a section.

**Tentative direction:** **Field-level** provenance for any field populated by LLM extraction, regex extraction, or inference from related data. Structured fields copied directly from a machine-readable source can use coarser provenance.

### Q7. What does a provenance record contain?

- `source` — URL / identifier / timestamp of the raw data source
- `extraction_method` — `direct_copy` / `regex` / `llm` / `inferred` / `human_corrected`
- `confidence` — a score in [0, 1] for non-direct extractions (meaningless for direct copies)
- `extracted_at` — timestamp of when the extraction was run
- `model_version` — for LLM extractions, the model and prompt version so re-runs are reproducible

**Open:** Whether provenance should include the **text span** from the source document that was used as the basis for extraction (for auditability). Leaning yes for LLM extractions, no for direct copies, because storing the full source text for every field is expensive and recoverable from the `source` field.

### Q8. How do we represent confidence on fields that didn't need extraction?

A field directly copied from a state's CSV export has no meaningful confidence score — it's either correct (the state reported it) or incorrect (the state reported it incorrectly), and our pipeline has no information about which. Proposal: use `null` confidence for direct-copy fields, and interpret `null` at query time as "confidence is whatever the source's native confidence is — don't assume we vetted it." This is explicit about the pipeline's epistemic limits.

## Cross-State Entity Resolution

### Q9. How do we match a lobbying client across state filings?

The pipeline will see "Pfizer Inc." in California, "Pfizer, Inc." in New York, "Pfizer Government Relations LLC" in Texas, and "Pfizer" in Wisconsin. These are the same entity for most policy-relevant purposes, and it is probably four different entities for others (a subsidiary matters when analyzing who actually paid for the lobbying).

**Tentative direction:** Build an entity-resolution layer that produces a canonical **CrossStateOrgIdentifier** separate from the state-specific filing records. Each state-specific record has a `canonical_org_id` field linking to the cross-state identifier, with a confidence score for the link. Consumers can query at either level: "all lobbying by Pfizer entities" (follow the canonical identifier) or "Pfizer's exact legal name as filed in Texas" (read the state-specific record).

**Open:** Which entity-resolution method to use. Candidates are (a) fastLink (classical Fellegi-Sunter, R package), (b) fuzzylink (Ornstein 2025, LLM embeddings + zero-shot prompts, R package), (c) Libgober-Jerzak (2024, organization-specific, uses OpenCorporates collaborative records), (d) Splink (Python/DuckDB, Fellegi-Sunter family). **This is the biggest open methodological question in the project.** The candidates should be benchmarked on a labeled subset of state lobbying client names before committing to one.

### Q10. Do we link to external entity IDs?

Candidates for external IDs to include: **Open States' person/org identifiers**, **OpenCorporates identifiers** for corporate clients, **SEC EDGAR CIK** for publicly traded clients, **LobbyView identifiers** for entities that also appear in federal LDA data.

Leaning yes on all four. The identifiers are small, the linkage value is large, and consumers with specialized needs (a political scientist linking state to federal, an investigative journalist pulling SEC filings) get dramatic leverage from them.

**Open:** Whether to store these links in the core schema or in a separate enrichment layer. Leaning separate enrichment layer because the linkage quality will improve over time and should be re-computable.

## Bill Linkage

### Q11. How are bills referenced?

Bills are referenced by **Open States canonical identifier**, not by re-scraped text. If a lobbying filing mentions "H.B. 1249", the pipeline resolves that to the specific Open States bill record for that session / chamber and stores the canonical ID plus the original text span for provenance.

### Q12. What about bills that don't exist in Open States?

Two cases:
- **Historical bills** — Open States coverage is uneven before ~2011 for some states. If the pipeline encounters a pre-coverage bill reference, it records the text reference with a `unresolved_bill_reference` flag and no canonical ID.
- **Regulatory or executive actions** — some state lobbying filings reference agency rulemakings, executive orders, or federal legislation, none of which are "bills" in the Open States sense. Represent these as a distinct **LegislativeOrRegulatoryReference** entity with a `type` field, not as a forced Bill link.

### Q13. How do we handle bill ranges and bulk references?

LobbyView's regex approach expands "H.R. 4182–4186" into five separate bill references. We should do the same, but with an explicit flag `inferred_from_range_expansion` on each expanded reference so downstream consumers can see which references came from direct mention vs. range expansion.

## Open Questions With No Current Direction

These are questions I don't yet have a useful tentative answer for. Flagging them so they don't get forgotten.

- **Privacy and redaction.** Some state filings include home addresses of individual lobbyists. Should the pipeline redact these by default, or store them verbatim and leave redaction to consumers?
- **Unicode and legal-name characters.** Corporate legal names contain ™, ®, Inc., LLC, nested quotation marks, em dashes, etc. How much normalization happens at ingest time vs. query time?
- **Non-English filings.** Are any state lobbying filings submitted in Spanish or other languages? (Probably not at scale, but worth checking before assuming English-only.)
- **Retroactive schema migration.** When the schema evolves, how do we update already-ingested data from prior versions without re-running the entire pipeline? This is a painful general problem and the schema design can either help or hurt.

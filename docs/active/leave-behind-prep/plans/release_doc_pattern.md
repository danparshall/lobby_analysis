# Plan: Per-state Suhan-droppable release-doc pattern

**Created:** 2026-06-09
**Author:** Claude (session 20260609 with Dan, web/claude.ai)
**Originating convo:** [`docs/active/leave-behind-prep/convos/20260609_wi_vs_ny_chain_parity.md`](../convos/20260609_wi_vs_ny_chain_parity.md)
**Estimated execution time:** ~2:20
**Status:** Drafted, awaiting fresh-agent execution

---

## TL;DR

Extend the four existing READMEs in `releases/wi/` and `releases/ny/` (plus a small touch to `docs/STATE_COVERAGE.md`) so that each state's release directory is **self-contained and Suhan-droppable**: someone can upload the contents of `releases/<state>/` into a fresh claude.ai Project — without any other repo files — and a cold-context agent can answer analytical questions about the data without making silent aggregation mistakes.

No new docs are created. No data files change. This is purely doc enrichment.

---

## Why this matters

Suhan's expected workflow after the Fellowship ends (~2026-06-11):

1. He wants to use a state's lobbying data for an analysis.
2. He creates a fresh claude.ai Project.
3. He uploads the contents of `releases/<state>/` into that Project's knowledge.
4. He asks the resulting agent to do analysis.
5. The agent must (a) understand what the data is, (b) understand the modeling assumptions, (c) avoid the load-bearing aggregation traps that would cause silent over/undercounting.

Today's docs don't fully support that workflow. Specifically:

- `releases/wi/README.md` (on `main`) and `releases/ny/README.md` (on `ny-disclosure-explore`) cover provenance + files + caveats but **lack the 4-node × 6-edge × 3-attribute framework** that explains what edges/attributes a state's data covers. That framework lives in `docs/STATE_COVERAGE.md`, which won't be in an isolated Project.
- The chain READMEs have asymmetric quality (per the 2026-06-09 parity check): WI's has consumer-front-door polish (TL;DR, audience, 30-sec tour) but weak load-bearing aggregation warnings; NY's has rigorous conservation rules but no consumer framing.
- Neither has **sample analyses** that show correct aggregation patterns to anchor a cold-context agent against the gotchas.

---

## Architectural decision (do not relitigate)

Three docs per state, all already exist, all to be enriched (not replaced):

```
releases/<state>/README.md             ← Per-state primer ("basics")
releases/<state>/chain/README.md       ← Chain consumer doc ("nitty-gritty")
docs/STATE_COVERAGE.md                 ← Cross-state matrix (mostly unchanged)
```

**Duplication is accepted.** The 4×6×3 framework is reproduced in each `releases/<state>/README.md` (≈15 lines × N states) so each release dir is self-contained. The cost (N+1 places to update if framework evolves) is acceptable at N=3; revisit at N≥10.

**Out of scope for this plan:**
- Adding new attribute axes (only Money / Time / Stance for now)
- Restructuring `STATE_COVERAGE.md` beyond adding "See also" pointers
- Touching data TSVs
- Cosponsor edges, multi-year backfills, `lobbyist_bimonthly` integration, FTM NY validation
- Anything that requires re-running the chain composers

---

## Reading list (do this BEFORE writing anything)

In order:

1. This file.
2. [`docs/active/leave-behind-prep/convos/20260609_wi_vs_ny_chain_parity.md`](../convos/20260609_wi_vs_ny_chain_parity.md) — the originating discussion, has the specific back-port lists for each chain README.
3. [`docs/STATE_COVERAGE.md`](../../../STATE_COVERAGE.md) — source material for the framework + per-state matrices. The bulk of new content will be adapted from here.
4. `releases/wi/README.md` (on `main`) — current state.
5. `releases/wi/chain/README.md` (on `main`) — current state.
6. `releases/ny/README.md` (on `ny-disclosure-explore`) — current state.
7. `releases/ny/chain/README.md` (on `ny-disclosure-explore`) — current state.

**Branch note:** NY work is on `ny-disclosure-explore` (not merged to main as of 2026-06-09). WI work is on `main`. The fresh agent must switch branches via the Contents API `?ref=` parameter (or local git) when touching NY files.

---

## Deliverables

1. Extended `releases/wi/README.md` on `main`
2. Extended `releases/wi/chain/README.md` on `main`
3. Extended `releases/ny/README.md` on `ny-disclosure-explore`
4. Extended `releases/ny/chain/README.md` on `ny-disclosure-explore`
5. Minor touch to `docs/STATE_COVERAGE.md` on `main` — add per-state release-README links to its "See also" header
6. RESEARCH_LOG entry on `leave-behind-prep` documenting what shipped

---

## Step-by-step execution

### Step 1 — Extend `releases/wi/README.md` (~25 min, on `main`)

Read the existing file first to get the current section order. The existing sections are roughly: intro paragraph → Provenance → Files → Headline aggregates → Caveats → License & usage.

**Insert these new sections (placement guidance below):**

#### A. TL;DR (place right after the intro paragraph, before Provenance)

A compact 5-7 row table or paragraph: state, vintage, rows in chain, distinct entities, file count, total $ or hours, key acronyms (FTM, OS/PP, IPF, MMS).

Goal: a one-glance "what is this" anchor.

#### B. Framework (place after TL;DR, before Provenance)

Adapt verbatim from `docs/STATE_COVERAGE.md` "## Framework" section. Include:

- The ASCII 4-node diagram (principal/lobbyist/lawmaker/bill)
- The "up to 6 edges" framing
- The 3 attributes: Money / Time / Stance (with one-sentence definitions)
- The 6 quality-convention symbols: ✓ exact / ~ imputed / ✗ missing / ✗! structurally missing / — not meaningful / ? needs validation

This section is roughly 15 lines. It is the load-bearing piece that makes the rest of the doc legible to a cold agent.

#### C. What this release covers for WI (place after Framework, before Files)

Adapt from `docs/STATE_COVERAGE.md` "## WI — Wisconsin" section. Include:

- The status paragraph (Mature, chain shipped, etc.)
- The 6×3 edge × attribute matrix
- **All 8 footnotes**, but rewrite cross-state references (e.g. "Same structural shape as WI on this edge" in OH would be incoherent here — but the WI section has no such cross-references, so this is mostly a direct copy)

The footnotes are the load-bearing gotchas. They must not be summarized; they must be reproduced verbatim where they explain the state's specific foibles.

#### D. How to use this release with a Claude agent (place after Caveats, before License)

New section, ~10-15 lines. Concrete drop+go instructions:

- Files to upload to a Project: `README.md` (this file), `chain/README.md`, `chain/WI_chain_2025.tsv`. Optionally the other 6 TSVs in the dir if doing analysis below the chain layer.
- The chain README has the schema + conservation rules — point to it explicitly.
- Note the two most likely silent-mistake traps: **(a) don't sum `modeled_hours` across sponsor rows; use `modeled_hours_per_sponsor` instead; (b) the chain is hours-grain, not dollar-grain — see chain README §"What this isn't" for the explanation.**

#### E. See also (place at the very end, after License)

Bullets pointing to:
- `chain/README.md` for chain artifact deep-dive
- `docs/STATE_COVERAGE.md` (link via GitHub blob URL since it won't be in an isolated Project) — frame as "cross-state context, optional"

#### Acceptance for Step 1:
- The doc stands alone — a cold agent can read it and understand what edges/attributes WI covers and which are inferred vs disclosed, without reading anything else
- All 8 STATE_COVERAGE WI footnotes are preserved verbatim
- The 6×3 matrix renders correctly in GitHub markdown
- Existing content (Provenance, Files, Aggregates, Caveats, License) is preserved unchanged

### Step 2 — Extend `releases/wi/chain/README.md` (~40 min, on `main`)

Read the existing file first. Existing structure: TL;DR → Provenance → Schema → 30-second tour → What this isn't → Headline finding → Reproducer → Open follow-ups → License.

**Add these sections / strengthen these existing pieces:**

#### A. Elevate conservation rules

Currently the don't-sum-`modeled_hours`-across-sponsors warning is buried inline in the schema row. Pull it out into a **new section called "Conservation rules / aggregator gotchas"**, placed right after Schema and before "30-second tour".

Pattern this section after `releases/ny/chain/README.md`'s "How dollars are attributed (conservation)" section (read it first). Use the same "load-bearing rules for anyone aggregating this file" framing.

The two WI conservation rules to elevate:

1. **A cell's identity is `(filing_id, lobbyist_id, principal_id, bill_id, item_id)` — never `bill_id` alone.** WI bill IDs collide across sessions/chambers; `item_id` is the disambiguator. Aggregating on `bill_id` without `item_id` silently merges distinct bills.
2. **Do not sum `modeled_hours` across the sponsor rows of one cell.** When a bill has multiple primary sponsors, `modeled_hours` is replicated across those sponsor rows (the modeled hours attach to the bill, not subdivided per lawmaker). Use `modeled_hours_per_sponsor` if you need a per-sponsor metric — that column is `modeled_hours / num_sponsors_on_bill`, a uniform-allocation modeling assumption, not a disclosed share.

The second rule needs the explicit "uniform-allocation is a modeling assumption, not a disclosed share" framing — this is the NY-style semantic warning back-ported. A cold agent must understand that `modeled_hours_per_sponsor=2.5` means "we modeled it as 2.5, assuming uniform split across sponsors" not "the lobbyist actually spent 2.5 hours on this lawmaker about this bill."

#### B. Measured-impact disclosure for bill-id disambiguation

If not already present at this level of specificity, add a 2-3 sentence note in the conservation-rules section quantifying the `item_id` disambiguation impact. Source: any historical results doc in `docs/historical/wi-allocation-matrix/` that measured the collision rate — search the results dir for the relevant number, or note "X% of `bill_id` values collide across sessions/chambers; `item_id` resolves these uniquely."

If no historical measurement exists, omit the quantification — do not invent numbers. State the disambiguation rule qualitatively.

#### C. Sample analyses section (place before Reproducer)

New section: **3-5 worked analyses showing correct aggregation patterns.** Each should demonstrate avoiding one of the gotchas. Phrased as pandas snippets with comments explaining what they do.

Suggested analyses:

1. **Top principals by chain weight on a given bill** — demonstrates de-duplication on cell key before summing modeled_hours.
2. **Lawmakers most lobbied by a given coalition** — demonstrates the per-sponsor split + the modeling-assumption caveat.
3. **Industry-level rollup** — if there's a sector tag (check the schema); otherwise skip and substitute another query.
4. **Confidence-label filtering** — show how to filter to only `ipf_fit` rows for high-confidence work, or to include all rows with appropriate uncertainty caveats.
5. **Joining to bill metadata** — show how to pull bill title / OS bill identifier for downstream display.

Each snippet should include a 1-line comment explaining what gotcha it avoids. The agent doesn't need to actually run the queries — they need to be plausibly correct based on the schema.

#### Acceptance for Step 2:
- Conservation rules section exists, is elevated out of schema, names both rules explicitly with "uniform-allocation is a modeling assumption" framing
- Sample analyses section has 3-5 snippets, each with a comment explaining the protective pattern
- Existing TL;DR / 30-second tour / Reproducer sections are preserved
- A cold agent reading just this file can do basic analyses without falling into the sponsor-replication or `bill_id`-collision traps

### Step 3 — Extend `releases/ny/README.md` (~25 min, on `ny-disclosure-explore`)

**Switch branches.** Either checkout `ny-disclosure-explore` locally, or pass `?ref=ny-disclosure-explore` on every Contents API read/write.

Read the existing file first. Then apply the same five additions from Step 1 (A through E), substituting NY content:

- **B. Framework:** same as Step 1 (copied from STATE_COVERAGE.md)
- **C. What this release covers for NY:** adapt from `docs/STATE_COVERAGE.md` "## NY — New York" section. Includes the status paragraph (chain shipped, `parties_lobbied` MVP shipped, 98.61% nickname-match), the 6×3 matrix, all 9 footnotes verbatim
- **D. How to use:** adjust the gotchas to NY's load-bearing ones: (a) cell key includes `lobbyist_id` (smoke test caught −$68.6M phantom loss when omitted); (b) `comp_per_cell` replicated across sponsor rows — do not sum; (c) `disclosed_lawmakers` is filing-grain not bill-grain — don't read `sponsor_in_disclosed_set=True` as bill-specific evidence

Note: NY's existing `releases/ny/README.md` has a "Disclosed lawmaker contacts" subsection that doesn't appear in WI's. Preserve it.

### Step 4 — Extend `releases/ny/chain/README.md` (~45 min, on `ny-disclosure-explore`)

Read the existing file first. Existing structure: Aggregates → Schema → How dollars are attributed (conservation) → Disclosed vs inferred → Honest limitations → Bill-id normalization → Regenerating → Follow-ups.

**Add these consumer-facing sections (the WI-style polish back-ported):**

#### A. TL;DR table (place right at the top, before "Aggregates")

5-7 row table: rows in chain (83,786), distinct entities (firms / beneficiaries / bills / sponsors), total compensation ($153,064,191), conservation check (exact, $0 delta), `os_matched` rate (99.9%), date covered (2025).

#### B. Audience line (place immediately under the TL;DR table)

One sentence like "for colleagues who want the influence graph 'company → lobbyist → bill → lawmaker' for NY 2025 without assembling it from the 6 source TSVs themselves." Adapt the WI chain README's audience line for tone.

#### C. 30-second tour of construction (place after Schema, before How dollars are attributed)

NY's construction is structurally simpler than WI's — it's a join, not an IPF. Plain-English walk-through:

1. **Lobbying disclosure → chain rows.** NY filers (lobbyists, on behalf of clients) report compensation + bill list semi-annually. We join those filings to Open States bill metadata to get the sponsor for each bill.
2. **Coalition split.** When a filing lists multiple beneficiaries (a coalition), we split the compensation evenly across them (a uniform-allocation modeling assumption).
3. **Per-bill, per-sponsor split.** Compensation is also split evenly across the bills lobbied, then replicated across sponsor rows for each bill. Cells sum to the filing's disclosed compensation exactly (integer-cent even-split, no rounding loss).

This is 3 plain-English paragraphs. The point: the chain is mostly a clean join with two deterministic splits — much less modeling than WI's chain, but the splits are still modeling assumptions (not disclosed shares) and consumers should know that.

#### D. Headline finding / worked example (place after the 30-second tour)

Use one specific bill or coalition from the dataset — something compact that demonstrates the chain in action. Suggestion: pick a high-compensation bill (top 5 by total `comp_per_cell` summed correctly) and walk through what the chain reveals. Don't over-editorialize; the goal is to show what the data looks like in use.

If picking a specific bill requires querying the TSV and the agent doesn't want to do that load: skip this section. It's nice-to-have, not load-bearing.

#### E. Copy-pasteable Reproducer (replace the existing "Regenerating" section)

Currently NY has a regeneration command in a code block. Make it a fully copy-pasteable block with environment setup notes, the command, and the expected output line ("✓ Chain written to releases/ny/chain/NY_chain_2025.tsv (83,786 rows, $153,064,191 conserved)"). Match the WI chain README's "Reproducer" style.

#### F. Sample analyses section (place before "Follow-ups")

Same shape as Step 2.C — 3-5 worked queries with protective patterns. NY-specific suggestions:

1. Top principals on a bill — demonstrates the don't-sum-on-`filing_id`-alone rule + the sponsor-row de-duplication
2. Top sponsors by chain weight — demonstrates the `comp_per_cell`-replicated-across-sponsors trap
3. Disclosed lawmakers analysis — demonstrates that `sponsor_in_disclosed_set=True` is not bill-specific evidence; use `disclosed_only_lawmaker_count` for the off-sponsor signal
4. Coalition decomposition — pick a multi-beneficiary filing and show how comp splits
5. Bill-id normalization use case — show how to join external bill-text data via `os_bill_identifier`

#### Acceptance for Step 4:
- TL;DR table at top
- Audience line is present and adapted (not verbatim from WI)
- 30-second tour explains the JOIN + 2 splits structure clearly
- Sample analyses section has 3-5 snippets, each with a protective-pattern comment
- Existing rigor (Conservation rules, Disclosed vs inferred, Honest limitations, Bill-id normalization) is preserved
- A cold agent reading just this file can do basic analyses without falling into the firm-collapse, sponsor-replication, or base-rate-fallacy traps

### Step 5 — Touch `docs/STATE_COVERAGE.md` (~5 min, on `main`)

Add two bullets to the "See also" header at the top of the file:

- `releases/wi/README.md` — per-state Suhan-droppable primer
- `releases/ny/README.md` (on `ny-disclosure-explore` branch) — per-state Suhan-droppable primer

No other changes to STATE_COVERAGE.md. Do not duplicate the framework into per-state sections beyond what's there now (those changes go into the release READMEs).

### Step 6 — Document what shipped (~10 min, on `leave-behind-prep`)

Append to `docs/active/leave-behind-prep/RESEARCH_LOG.md` (at the top, below the existing 2026-06-09 entry from the parity-check session) a new entry like:

```
## 2026-06-09 — Release-doc pattern shipped for WI + NY

[summary: 5 files updated across 2 branches, list each commit, link the
release READMEs as the now-Suhan-droppable artifacts]
```

If the work spans into 2026-06-10, date the entry for the day execution completed, not the day the plan was authored.

---

## Acceptance criteria (whole plan)

A reviewer should be able to:

1. **Drop `releases/wi/` into a fresh Project and have a cold Claude agent answer the question "what's the top principal by chain weight on AB 50?"** — and the agent should produce a correct pandas snippet that de-duplicates on the cell key first. (Test this with a small query if data is loadable; otherwise, eyeball the sample analyses for protective patterns.)
2. **Drop `releases/ny/` into a fresh Project and have a cold Claude agent answer "did Doordash lobby Senator X about S 1234?"** — and the agent should correctly cite the `comp_per_cell` chain row AND correctly caveat that `disclosed_lawmakers` is filing-grain (not per-bill).
3. **Read just `releases/<state>/README.md` (no other docs) and explain what edges/attributes that state covers and which are inferred vs disclosed.** — the framework + matrix + footnotes carry this load.

If any of those tests fails on a cold-context read, the doc isn't yet self-contained and needs another pass.

---

## Risks / known gotchas for the executing agent

1. **Branch switching for NY.** Files under `releases/ny/` live on `ny-disclosure-explore`, not main. Reading/writing without the correct `?ref=` will silently fail or write to main. Always specify the branch on NY operations.
2. **The cross-state references in STATE_COVERAGE footnotes.** Phrases like "same shape as WI" are useful in the cross-state context but become weird in a per-state release README. Light editing of footnote prose is fine; preserving the substantive content is essential.
3. **Sample analyses must avoid showing the gotcha as correct.** Each snippet's purpose is to demonstrate the protective pattern. A snippet that sums `comp_per_cell` across sponsor rows would actively teach the cold agent the wrong pattern. Triple-check that each snippet de-duplicates / aggregates correctly.
4. **Don't invent numbers.** Quantifications (collision rates, match rates, dollar totals) must come from existing docs or actual computations. If a number isn't readily available, omit the quantification rather than estimate.
5. **The existing chain README structure is load-bearing.** Don't restructure aggressively; insert new sections at the suggested placement points. Preserve existing content unless explicitly extending it.
6. **Style consistency.** The WI chain README has a distinct voice ("colleagues who want X without having to assemble it"). The NY back-port should match that register. The release READMEs (Steps 1 & 3) should also match this voice across states.

---

## After completion

Once Steps 1-6 are done:

1. **Surface to Dan.** Summarize what shipped, with paths and commit SHAs, in the chat session that picks up this plan.
2. **Suggest tasks closed.** If any pre-existing GH issues are closed by this work, mark them via PR / comment. Probably none from the current open task set (#42, #43, #44, plus any others) — this is doc work, not issue-resolution.
3. **Flag for Day 4-5 if OH ships.** When OH chain composer ships and creates `releases/oh/`, the same release-doc pattern from this plan applies. A follow-up plan (or extension of this one) should propagate the pattern to OH.

---

## Pointers

- **Originating convo:** `docs/active/leave-behind-prep/convos/20260609_wi_vs_ny_chain_parity.md`
- **Source material for framework + matrices:** `docs/STATE_COVERAGE.md`
- **Existing release READMEs:** `releases/wi/README.md` (main), `releases/ny/README.md` (ny-disclosure-explore)
- **Existing chain READMEs:** `releases/wi/chain/README.md` (main), `releases/ny/chain/README.md` (ny-disclosure-explore)
- **Style reference for chain README polish:** `releases/wi/chain/README.md` (TL;DR, audience, 30-sec tour pattern to back-port to NY)
- **Style reference for chain README rigor:** `releases/ny/chain/README.md` (Conservation rules, Disclosed vs inferred pattern to back-port to WI — applied to `modeled_hours`)
- **WI synthesis writeup (companion artifact, optional reading):** `docs/historical/wi-allocation-matrix/results/20260602_wi_chain_synthesis.md`

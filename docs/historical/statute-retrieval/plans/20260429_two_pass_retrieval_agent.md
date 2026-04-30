# Two-Pass Statute Retrieval Agent — Implementation Plan

**Goal:** Build the statute-reading harness that produces correct, auditable disclosure-requirement extractions for the StateMasterRecord. The two-pass design (retrieval agent → scoring agent) is the means, not the end. Replace manual per-state URL curation with an LLM-driven retrieval agent that autonomously follows cross-references, and run a scoring agent over the expanded bundle as a calibration instrument.

**Originating conversation:** `docs/active/statute-retrieval/convos/20260429_retrieval_pipeline_design.md`

**Context:** The pri-calibration branch's baseline showed 0% exact-match agreement against PRI 2010 on disclosure-law scoring. Root cause (H1): statute bundles contained only the core lobbying chapter, but rubric items ask about definitions and provisions in cross-referenced chapters (e.g., TX Ch. 305 uses "person" without defining it — the definition lives in §311.005(2), a different title). Hand-curating support chapters per state doesn't scale to 50 states annually. The fix: make the retrieval agent itself capable of following cross-references.

**Confidence:** Medium-high on architecture. The two-pass design and enriched manifest are well-motivated by the H1 diagnosis. The LLM's ability to reliably parse cross-references across diverse state citation styles is the main uncertainty — OH is the test case.

**Architecture:** Pass 1 (retrieval agent) starts from core lobbying chapter URLs, reads statute text, identifies cross-referenced sections relevant to disclosure-rubric items, retrieves support chapters (2-hop limit), and writes an enriched manifest. Pass 2 (scoring agent) consumes the expanded bundle using the existing calibration harness (`build_statute_subagent_brief` → scorer subagent → `calibrate`). The scoring agent's job is to project the harness's statute-reading onto a published rubric (PRI 2010, eventually Sunlight 2015 / CPI / etc.) so that human-rater agreement can serve as a calibration signal — it is **not** the harness's output. The output we care about is the underlying disclosure-requirement extraction; per-rubric scores are the diagnostic.

**Branch:** `statute-retrieval`

**Tech Stack:** Python 3.12, pydantic, Playwright (Justia fetching), Claude Code subagents (retrieval agent prompt)

---

## Testing Plan

This is a hybrid implementation/research task. The retrieval agent itself is an LLM subagent (not unit-testable in the traditional sense), but the infrastructure around it — enriched manifest format, statute loader changes, and the end-to-end calibration comparison — is testable.

**Unit tests (TDD):**
- `StatuteArtifact` model accepts new fields (`role` expanded to `core_chapter | support_chapter`, plus `retrieved_because`, `hop`, `referenced_from`)
- `statute_loader.load_statute_bundle` correctly loads enriched manifests and validates new fields
- `retrieve_statute_bundle` writes enriched manifest entries with the new fields for core chapters (hop=0)

**Integration test:**
- `test_retrieve_bundles_all_calibration_subset` still passes with the enriched manifest format (backward compat for the flat retrieval path)

**End-to-end validation (the "TDD equivalent"):**
- Run the full two-pass pipeline on OH
- Compare scored output against PRI 2010 OH ground-truth via `calibrate` subcommand
- Measure improvement over baseline (which was 0% exact match with narrow bundles)
- Inspect OH manifest: does the retrieval agent find the known cross-references between §101.70 and §101.99? Between Ch. 101 and Ch. 121?

NOTE: I will write *all* unit/integration tests before I add any implementation behavior.

---

## Phase 1: Enrich the manifest and model layer

### Step 1.1 — Expand `StatuteArtifact` model

**File:** `src/scoring/models.py`

Add optional fields to `StatuteArtifact`:

- `role`: change from `Literal["statute"]` to `Literal["core_chapter", "support_chapter"]`
- `retrieved_because`: `str = ""` — agent's reasoning for why this artifact was retrieved
- `hop`: `int = 0` — 0 for core chapters (from `LOBBYING_STATUTE_URLS`), 1-2 for cross-referenced support chapters
- `referenced_from`: `str = ""` — filename of the artifact that contained the cross-reference

Default values ensure backward compatibility with existing manifests that only have `role: "statute"`.

### Step 1.2 — Update `statute_loader.py` to handle both old and new manifests

**File:** `src/scoring/statute_loader.py`

The loader reads `manifest.json` and constructs `StatuteArtifact` objects. Update it to:
- Map old `role: "statute"` to `role: "core_chapter"` for backward compatibility
- Pass through new fields (`retrieved_because`, `hop`, `referenced_from`) when present
- Default missing fields gracefully (existing manifests won't have them)

### Step 1.3 — Update `retrieve_statute_bundle` to write enriched manifests for core chapters

**File:** `src/scoring/statute_retrieval.py`

When writing the manifest for the initial (human-curated URL) retrieval, set:
- `role: "core_chapter"`
- `hop: 0`
- `retrieved_because: "curated core lobbying chapter"`
- `referenced_from: ""`

This is a non-breaking change — the existing `retrieve-statutes` orchestrator subcommand produces enriched manifests going forward.

### Step 1.4 — Write tests for all of the above

**File:** `tests/test_models.py` (add cases), `tests/test_statute_loader.py` (add cases), `tests/test_statute_retrieval_bundle.py` (update)

- Test `StatuteArtifact` accepts `core_chapter` and `support_chapter` roles
- Test `StatuteArtifact` accepts and round-trips `retrieved_because`, `hop`, `referenced_from`
- Test `load_statute_bundle` handles old-format manifests (maps `"statute"` → `"core_chapter"`)
- Test `load_statute_bundle` handles new-format manifests with all enriched fields
- Test `retrieve_statute_bundle` writes `role: "core_chapter"` and `hop: 0` in new manifests

---

## Phase 2: Retrieval agent prompt and orchestrator subcommand

### Step 2.1 — Write the retrieval agent prompt

**New file:** `src/scoring/prompts/retrieval_agent.md` (locked prompt, like the scorer prompt)

The prompt instructs the retrieval agent to:

1. **Read all core chapter files** in the statute bundle (provided as an artifact index, same pattern as the scorer brief)
2. **Identify cross-references** — look for citations to other sections, chapters, or titles that define terms, set penalties, or establish exemptions relevant to the PRI rubric items (rubric items provided inline as context)
3. **For each cross-reference found**, output a structured JSON entry:
   ```json
   {
     "section_reference": "§311.005(2)",
     "referenced_from": "title1-chapter101-101_70.txt",
     "relevance": "Defines 'person' — needed for rubric items A5-A11 (who must register)",
     "justia_url": "https://law.justia.com/codes/ohio/2010/title1/chapter311/311_005.html"
   }
   ```
4. **Construct Justia URLs** for referenced sections using the state's known URL pattern (provided in the prompt as examples from the core chapter URLs)
5. **Apply 2-hop limit:** after retrieving hop-1 support chapters, scan them for additional cross-references (hop-2). Stop after hop 2 — do not chase further.
6. **Output:** write a JSON file listing all cross-references found, organized by hop level

Key prompt design decisions:
- Provide the rubric items so the agent knows what's relevant (don't chase every cross-reference, only ones that affect scoring)
- Provide example URLs from the core chapters so the agent can infer the URL pattern for the same state/vintage
- Explicitly state the 2-hop limit
- Ask for structured output (JSON) so the orchestrator can parse it programmatically

### Step 2.2 — Write `build_retrieval_subagent_brief` in `bundle.py`

**File:** `src/scoring/bundle.py`

New function, parallel to `build_statute_subagent_brief`, that:
- Takes the existing statute bundle (core chapters only)
- Takes the PRI disclosure-law rubric items (as context for relevance filtering)
- Takes the retrieval agent locked prompt path
- Produces a brief the retrieval agent can follow

### Step 2.3 — Write `cmd_expand_bundle` orchestrator subcommand

**File:** `src/scoring/orchestrator.py`

New subcommand `expand-bundle` that:
1. Loads the existing statute bundle from `data/statutes/<STATE>/<YEAR>/`
2. Builds and writes a retrieval agent brief to `data/statutes/<STATE>/<YEAR>/retrieval_brief.md`
3. (Manual step: user dispatches retrieval agent subagent with this brief)
4. Reads the agent's output JSON (cross-references found)
5. Fetches each referenced URL via `PlaywrightClient`
6. Appends the new artifacts to the existing manifest with enriched fields (`role: support_chapter`, `hop`, `retrieved_because`, `referenced_from`)
7. Re-writes `manifest.json` with the expanded bundle

Alternative: steps 4-7 could be a separate `ingest-crossrefs` subcommand that takes the agent's output JSON as input. This separates the LLM-dependent step from the deterministic fetch-and-update step.

CLI: `scoring-orchestrator expand-bundle --state OH --vintage 2010`

### Step 2.4 — Tests for the retrieval brief builder

**File:** `tests/test_bundle.py` (or new `tests/test_retrieval_brief.py`)

- Test `build_retrieval_subagent_brief` includes rubric items, artifact index, URL pattern examples, and 2-hop instruction
- Test the brief is well-formed markdown that a subagent can parse

---

## Phase 3: Run on OH and calibrate

### Step 3.1 — Re-retrieve OH core chapters with enriched manifests

Run `scoring-orchestrator retrieve-statutes --state OH --vintage 2010` to re-generate the manifest with `role: core_chapter` and `hop: 0` fields.

### Step 3.2 — Run retrieval agent on OH

Dispatch the retrieval agent subagent with the OH brief. Inspect its output:
- Which cross-references did it find?
- Do the Justia URLs it constructed look correct?
- Did it identify the §101.70 ↔ §101.99 cross-reference? The Ch. 101 ↔ Ch. 121 relationship?

### Step 3.3 — Ingest cross-references and expand the OH bundle

Run the orchestrator to fetch the support chapters and update the manifest.

### Step 3.4 — Run scoring agent on the expanded OH bundle

Use the existing `calibrate-prepare-run` → subagent dispatch → `calibrate-finalize-run` flow.

### Step 3.5 — Compare to PRI 2010 OH ground truth

Run `scoring-orchestrator calibrate --state-subset OH --rubric pri_disclosure_law --vintage 2010`.

Evaluate:
- Exact-match agreement on sub-aggregates (A, B, C, D, E)
- Per-item disagreements — are they retrieval failures (missing cross-refs) or scoring failures (agent misinterpretation)?
- If agreement is poor, diagnose: is the manifest missing a cross-reference the agent should have found? Or did the agent find the right statutes but misinterpret them?

### Step 3.6 — Iterate

Based on the diagnosis:
- If retrieval gaps: refine the retrieval agent prompt (add examples, adjust relevance filtering)
- If scoring gaps: that's a pass-2 problem — refine the scorer prompt (separate concern)
- If PRI disagreement: check whether the agent or PRI is correct (flag for manual review)

---

## Edge cases

1. **Cross-reference URL doesn't exist on Justia.** The agent constructs a URL for a referenced section, but Justia doesn't have that page for the 2010 vintage. The fetch step should handle 404s gracefully — log the failure in the manifest as a `failed_retrieval` entry with the URL and HTTP status, don't crash.

2. **Agent hallucinates a cross-reference.** It claims §999.99 is referenced when it isn't. The `referenced_from` field is the audit trail — we can verify by searching the source file for the cited section number. Build a validation step: for each cross-reference the agent reports, grep the `referenced_from` file for the section number.

3. **Circular cross-references.** §101.70 references §101.99 which references §101.70. The hop counter prevents infinite loops, but the manifest should deduplicate — don't re-fetch a URL that's already in the bundle.

4. **State-specific citation styles.** Ohio uses "section NNN.NN of the Revised Code." Texas uses "Section NNN.NNN, Government Code." California uses "Section NNNNN." The retrieval agent prompt should include examples from the state's own statutes (extracted from the core chapters) rather than a universal regex.

5. **Ambiguous cross-references.** "As defined by law" or "pursuant to applicable regulations" with no specific section number. The agent should flag these as `unresolvable_reference` in its output rather than guessing.

6. **Large support chapters.** Some cross-referenced chapters may be very long (e.g., an entire definitions title). The retrieval agent should fetch the specific section, not the whole chapter, when the reference is section-specific.

---

**Testing Details:** Unit tests cover the enriched manifest format (model layer, loader, writer). Integration tests verify backward compatibility with old manifests. End-to-end validation uses PRI 2010 OH scores as the ground truth — improvement over the 0% baseline is the success metric.

**Implementation Details:**
- Phase 1 is pure infrastructure (model + loader changes) — no LLM involvement, fully TDD
- Phase 2 introduces the retrieval agent prompt and orchestrator plumbing — the prompt is the critical artifact
- Phase 3 is the experimental run on OH — results feed back into prompt refinement
- The `expand-bundle` subcommand separates the LLM step (agent writes cross-ref JSON) from the deterministic step (fetch URLs, update manifest) for reproducibility
- Enriched manifests are backward-compatible — old manifests load fine with default values
- The scorer brief (`build_statute_subagent_brief`) needs no changes — it already reads whatever artifacts are in the bundle
- Hop-2 support chapters use the same `StatuteArtifact` model and manifest format as hop-1

**What could change:**
- If the retrieval agent can't reliably construct Justia URLs from cross-references, we may need a hybrid approach (agent identifies references → code constructs URLs using known Justia patterns per state)
- If 2 hops isn't enough for some states (deeply nested cross-references), we'd increase the limit — but start conservative
- The rubric items provided to the retrieval agent are currently PRI disclosure-law only; if we later score accessibility or FOCAL, the retrieval agent needs those rubric items too (or we do separate retrieval passes per rubric)
- If OH works well but TX still fails (due to TX's more unusual cross-reference patterns), the prompt may need state-specific examples

**Resolved questions:**
1. Retrieval agent gets PRI disclosure-law rubric items only. Accessibility is scored separately against portal data, not statutes.
2. Two subcommands: `expand-bundle` (generates retrieval agent brief) and `ingest-crossrefs` (fetches URLs from agent output, updates manifest). Clean separation of LLM-dependent and deterministic steps.
3. The scorer brief will indicate core vs. support chapter roles in the artifact index — trivial to include and helps the scorer weight evidence.
4. Backward compat with old `role: "statute"` manifests: included via defaults but will drop if it makes anything awkward.

---

# OH (A') Brainstorm — Smallest-viable single-filing round-trip

**Date:** 2026-05-07
**Branch:** oh-portal-extraction

## Summary

First substantive working session on `oh-portal-extraction` after merging 39 commits of upstream Track A and compendium work into the branch. The session ran the `brainstorming` skill end-to-end on the question "what does done-for-OH look like for the next ~2 weeks of Track B?" Three scope tiers were considered (single-filing demo, single-regime MVP pipeline, full-regime production-shape) and we converged on a phased path: (A') a smallest-viable one-filing round-trip first, (B') single-regime MVP across all current filers next, then graduate. The "(A') first" choice was anchored on the constraint Amina articulated explicitly — *keep in sync with everything teammates do* — which argues for surfacing schema-fit problems via a real round-trip before scaling any infrastructure.

Within (A'), three architectural approaches were compared by validation strategy: model-anchored (validate `LobbyingFiling` itself), SMR-anchored (validate against Track A's `field_requirements` for the chosen regime), and form-as-schema (extract the form's fields and assess gap to model). Approach 1 (model-anchored) won on the smallest-viable framing — building SMR validation for one filing is over-engineering, and the SMR is still a moving target while `statute-extraction` iterates beyond the `definitions` chunk. Approach 2's validation pattern was held back as the bridge to (B'). Approach 3 falls out naturally — schema gaps surface as a side-effect of the hand-validation step.

For the OH regime choice within (A'), Dan's regime survey (`statute-extraction` branch) was the grounding artifact. OH has three unambiguous statutory regimes (legislative ORC §§101.70–101.79, executive-agency ORC §§121.60–121.69, retirement-system ORC §§101.90–101.99), all administered by OLIG via OLAC. Legislative was chosen for (A') because it's the largest filer population, has the most stable upstream contract (Dan's iter-1 `definitions` chunk converged here; SMR diff says the statute is structurally unchanged 2010 → 2025), and it's the canonical mental model — "lobbyist talks to legislators about bills" — for the schema test.

Finally, four design sections were validated incrementally with the user: (1) round-trip architecture, (2) source acquisition + sample selection, (3) extraction + validation, (4) failure handling + testing scope + definition of done. Each was confirmed before moving on.

## Topics Explored

- Scope of "done for OH" over the next ~2 weeks (three-tier framing, A'/B'/C')
- Validation strategy for (A') — model-anchored vs SMR-anchored vs form-as-schema
- Multi-regime structure of OH lobbying disclosure law (Dan's regime survey)
- Coupling with Track A's WIP SMR — when to integrate, when to defer
- Source format trade-offs (OLAC PDF vs HTML detail page) for one filing
- Provenance shape for a single-LLM-call extraction (one `Provenance` instance shared across populated fields)
- Tool-use / structured-output as the Pydantic-schema enforcement mechanism
- Test scope at (A') scale (rejection of mocked-LLM tests as testing-anti-pattern)
- Definition of done for (A') and graduation gate to (B')

## Provisional Findings

- OH legislative agent regime is the right starting wedge: largest filer population, statute structurally unchanged 2010 → 2025 per the OH SMR diff, Track A's iter-1 already converged for this regime's `definitions` chunk. Provisional — could shift if OLAC's legislative search interface turns out to be much harder to scrape than the executive-agency one.
- Track A and Track B should integrate at the *output schema level* (both emit Pydantic-validated artifacts that the other's tools can read) rather than at the SMR-validation level for (A'). The SMR is still a moving target while Dan iterates beyond the `definitions` chunk; tightly coupling Track B's first deliverable to a moving spec would invert the work order.
- The "keep in sync with teammates" constraint is best operationalized as five concrete commitments (no unilateral schema bumps, output = `LobbyingFiling.model_dump_json()`, regime-enum reuse, STATUS.md row discipline, plans-before-code) rather than as a tight runtime coupling between tracks.
- Hand-spot-check is the right validation methodology at (A') scale. Mocked-LLM unit tests of extraction quality are a testing-anti-pattern — they don't tell us anything we couldn't get from one real call against the real PDF.

## Decisions Made

- (A') = single-filing round-trip on OH legislative agent activity report; validation by hand spot-check; output is `LobbyingFiling.model_dump_json()`; provenance is a single shared `Provenance` instance attached to the filing.
- (B') deferred until (A') ships and team consensus on any v1.4 schema gaps that surface.
- Implementation plan to be drafted next: `plans/20260507_oh_a_prime_implementation.md`.
- Sample selection criteria: OH legislative-agent Activity & Expenditure Report from 2024 or 2025; mid-sized; at least one bill/issue and one expenditure line; recorded by report ID + URL.
- Tech stack pinned: `requests` for fetch (no Playwright until (B') hits a JS-rendered page), `claude-opus-4-7` direct PDF intake via Anthropic SDK tool-use enforcing the `LobbyingFiling` Pydantic schema, hand-spot-check validation in a results doc.
- Failure handling at (A'): fail loud, no retries. One PDF→HTML fallback for parse-unfriendly PDFs; one sample swap for unrecoverable fetches; otherwise abort.

## Results

No analysis outputs produced this session — output is the plan + this convo summary. Next-session results will land at `docs/active/oh-portal-extraction/results/<date>_oh_a_prime_validation.md`.

## Open Questions

- Does OLAC require auth or CAPTCHA to access individual activity-report PDFs? Dan's 2026-04-13 snapshot succeeded with curl + Chrome UA but didn't enumerate per-report PDF endpoints — first attempt of (A') will surface this.
- Are activity report URLs stable/predictable on OLAC, or dynamically generated from search params? Affects how we record the "stable identifier" for the sample.
- Is the `LobbyingFiling` Pydantic model amenable to Anthropic SDK tool-use schema generation, or do its discriminated unions / nested optionals need flattening for the SDK? First implementation step will tell us.
- What's the team's preferred handling of v1.4 schema gaps surfaced by (A')? Convo doc + Dan/Gowrav review, or a more formal RFC pattern? Worth raising at the next weekly sync.

<!-- Generated during: convos/20260507_oh_a_prime_brainstorm.md -->

# (A') Sample Selection — OH Legislative Agent Activity & Expenditure Report

**Date:** 2026-05-07
**Branch:** oh-portal-extraction
**Phase:** 0.4 of `plans/20260507_oh_a_prime_implementation.md`

## Selected Sample

| Field | Value |
|---|---|
| **Agent** | Nathan Aichele |
| **Employer / Principal** | ARC Gaming & Technologies |
| **Regime** | `legislative` (per `origin/statute-extraction` convention) |
| **Form type** | Legislative Agent Activity & Expenditure Report (AER) |
| **Reporting period** | May–Aug 2025 (deadline Sep 30, 2025) |
| **Date filed** | 2025-09-03 |
| **OLAC report ID** | `1427844` |
| **OLAC confirmation number** | `20250903LUPA1427844` |
| **View URL** | https://www2.jlec-olig.state.oh.us/olac/AERs/1427844/View |
| **Authentication** | None — public access, no login or CAPTCHA |
| **Source format** | HTML only (no PDF download endpoint observed) |

## Why This Sample

Picked from a small candidate pool surfaced via OLAC's **Agent Forms Filed Search** by querying for Nathan Aichele's filings. Aichele was chosen as the candidate after Mike Abrams's (Ohio Hospital Association) 2025 AERs all turned out to be near-empty (1 bill, 0 expenditures across all three reporting windows).

The Aichele / ARC Gaming filing has:

- **Four bills listed** in Section I — `HB 96`, `HB 298`, `HB 344`, `SB 197`. Mix of HB and SB identifiers exercises both chamber prefixes.
- **A real $20.00 expenditure** in Section II.D (Non-Itemized Meals and Beverages, "Meals Under $50") — exercises the `LobbyingExpenditure` sub-entity.
- **Multi-section expenditure structure** with three empty sub-tables (A: Gifts, B: Itemized Meals, C: Functions) and one populated aggregate sub-section (D: Non-Itemized Meals split into 3 sub-rows). Tests how the extractor handles section structure with mixed empty/populated rows.
- **Concrete industry context** (gaming, multiple gambling-related bills) — the schema-fit story has real specifics rather than generic association advocacy.

## Plan-Criteria Deviations

The original plan asked for "5–20 bills/issues × 5–20 expenditure lines." This sample has 4 bills × 1 expenditure aggregate. **Accepting the deviation deliberately** because:

- A scan of Mike Abrams's 2025 filings (multiple AERs across three reporting windows for Ohio Hospital Association) shows all of them at "1 bill / 0 expenditures." Looking through Aichele's filings, the May–Aug 2025 AER above is the most-populated.
- This points at a **domain finding** worth recording (see next section): the modal OH legislative-agent A&E report has near-zero activity relative to plan expectations. Hunting for an outlier-large filing to satisfy the original criteria would cut against the smallest-viable framing.
- The strict criteria served their purpose — they forced sample-pool inspection that surfaced this real distribution finding, even if the chosen sample doesn't itself meet them.

## Domain Findings (Provisional)

### Modal A&E report has very low activity

From Mike Abrams's three 2025 AERs (Ohio Hospital Association engagement) and an informal survey of Aichele's filings, the typical OH legislative-agent A&E report at single-(agent, employer, regime, window) granularity reports:

- One bill OR a small handful (1–8) of related bills,
- Zero expenditures OR a single small aggregate line (typically Section D non-itemized meals under $50),
- Empty itemized sections (A, B, C) almost always.

This contradicts an implicit assumption in the plan that mid-sized filings would routinely have 5–20 bills × 5–20 expenditure lines. Provisional — the survey was small and biased toward agents we recognized. **(B') should profile the actual distribution** before picking sampling strategy.

### Bulk CSV downloads exist at year-aggregate level

OLAC's "Active Agents By Year" page exports two CSVs:

- `ActiveAgentDetails_<year>.csv` — one row per (agent, employer, engagement type) tuple. **For 2025: 12,170 rows.**
- `ActiveAgentSummary_<year>.csv` — one row per agent with per-regime yes/no flags. **For 2025: 1,566 unique agents.**

Both saved at `data/oh_portal/bulk_csvs/2025/` (gitignored).

These are **engagement registry metadata, not filing content** — they don't include AER bodies. But they give us our (B') universe size:

```
~12k engagements × 3 reporting windows/year ≈ 36k AER instances/year as upper bound
```

Actual AER count will be lower because not every engagement results in three filings (terminations, partial-year registrations, "no activity" no-filing variants if any exist). (B') discovery work should start by querying OLAC's Agent Forms Filed Search for `form_type=Legislative Agent AER, year=2025` to count the actual universe.

### URL pattern is stable

The OLAC view URL is `/olac/AERs/{report_id}/View` with `{report_id}` being an opaque sequential integer. Confirmation number embeds the report ID at the tail: `20250903LUPA1427844` ↔ report ID 1427844. Both fields are stable provenance values for (B') re-fetch.

## Source Format Decision: HTML, not PDF

The plan originally assumed PDF intake. **AER 1427844 has no PDF download endpoint** — only an HTML view at `/olac/AERs/{report_id}/View`. Plan revised accordingly: fetch HTML, extract structured text via BeautifulSoup, pass text to `claude-opus-4-7` as a regular message rather than as a `document` block. Architecture unchanged; one-line swap in `fetch.py` and `extract.py`.

## Schema-Gap Signal Spotted Pre-Extraction

OH's Section II (Expenditure Statement) has four sub-sections (A: Gifts itemized; B: Itemized Meals; C: Dinner/Functions where all members invited; D: Non-Itemized aggregate). Section D is itself split into three sub-rows: "Meals Under $50," "Speaking Engagements," "National Conference Meals."

The current `LobbyingExpenditure` model has:

```python
category: Literal["compensation", "reimbursement", "entertainment", "travel",
                  "lodging", "gift", "campaign_contribution", "membership_sponsorship", "other"]
amount: float | None
recipient_name: str | None
recipient_role: str | None
```

This **cannot cleanly represent OH's Section D structure.** Either:
- Collapse Section D's three sub-rows into one `LobbyingExpenditure(category="entertainment", amount=20.00)` and lose the sub-categorization, OR
- Add a v1.4 field (sub-category? aggregate-vs-itemized boolean?) to capture it.

The (A') extraction will use the collapse approach. The schema-gap is flagged for the next weekly sync as a v1.4 conversation. **Not a unilateral schema bump** — per the plan's "keep in sync with teammates" constraint.

## Out-of-Scope but Useful Context Found

- **Aichele has multiple engagements.** Beyond ARC Gaming, he files for Board of Lucas County Commissioners (Sep–Dec 2025 AER, 8 bills, 0 expenditures), Holistic Alternative Recovery Trust / HART (Sep–Dec 2025 AER, 1 bill, $3.50 in Section D), LKQ Corporation (Jan–Apr 2025 AER, 3 bills, $21.94 in Section D), and others. This tells us (B') will need to handle multiple `LobbyingFiling` rows per agent — one per (agent, employer, regime, period) tuple — and the 12,170-engagement universe stat above implicitly already reflects that.
- **Aichele also has an Initial filing.** `View Legislative Initial / Confirmation 20250505LINA479498 / Date Filed 2025-05-05`. This is OH's Engagement Registration form (separate form type, filed once per engagement). For (B') we'll need to handle Initial separately from AER — likely a different `LobbyingFiling.filing_action` value or a different model entirely. Out of scope for (A').

### Pre-Vetted (B') Candidate Seeds

In addition to the (A') sample (1427844), the same sample-selection session vetted two more Aichele filings of the same shape (Section D only). These are ready to use as (B') smoke-test inputs without re-doing the discovery work:

| Report ID | Confirmation | Employer | Period | Bills | Sec D Total |
|---|---|---|---|---|---|
| **1427844** ((A') sample) | 20250903LUPA1427844 | ARC Gaming & Technologies | May–Aug 2025 | 4 | $20.00 |
| 1459616 | 20260106LUPA1459616 | Holistic Alternative Recovery Trust (HART) | Sep–Dec 2025 | 1 | $3.50 |
| 1405684 | 20250522LUPA1405684 | LKQ Corporation | Jan–Apr 2025 | 3 | $21.94 |

URLs follow `/olac/AERs/{report_id}/View`.

### Strengthened Domain Finding: Section D Dominates Real Filings

All three above populate **only Section II.D (non-itemized aggregate)**; Sections A (Gifts), B (Itemized Meals), C (Functions for all members) are empty in every case. Combined with Mike Abrams's three 2025 AERs (all "no expenditures"), the provisional pattern is:

- The modal OH legislative-agent expenditure disclosure is **non-itemized meals under $50** (Section D).
- Itemized reporting (A/B/C) is **rare in practice**, presumably because per-event thresholds are seldom triggered.
- This sharpens the v1.4 schema-gap conversation: `LobbyingExpenditure`'s inability to represent Section D's three sub-row structure (Meals Under $50 / Speaking Engagements / National Conference Meals) isn't an edge case — it's the **common shape** for actually-populated expenditures. Worth raising at the next weekly sync as a higher-priority gap than the rate-limited itemized cases.

## Status

- Phase 0.4 complete.
- Plan to be updated in same commit: PDF→HTML intake; flag the deviation-from-criteria as already-accepted.
- Next: Phase 1 (failing tests for `extraction_brief.build_oh_legislative_brief()` and `provenance.build_provenance()`).

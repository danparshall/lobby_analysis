# OH lobbying chain — 2025-2026 (preview)

`OH_chain_2025_2026_preview.tsv` — a per-`(filing, position, sponsor)` chain joining the OH AER extractions (`positions[].bill_reference`) to Plural Policy's 136th GA bill sponsorships, with **§4a position-shape normalization** so subject-only positions are preserved rather than silently dropped.

**Audience:** colleagues who want OH's influence graph "principal → lobbyist → bill → sponsor" without writing the join themselves. **Preview scope** — see the parent [`releases/oh/README.md`](../README.md) for the 316-filing slice caveat and the issue #35 path to full-corpus.

---

## TL;DR

| | |
|---|---|
| **Rows** | 1,589 |
| **Columns** | 18 (see Schema) |
| **File size** | ~600 KB |
| **Distinct canonical filings contributing rows** | 140 (of 305 canonical filings; 54% of filings are position-empty in this slice) |
| **bill_class distribution** | 1,299 `bill` / 160 `subject` / 88 `jcarr` / 34 `oac_rule` / 8 `unmatched` |
| **Cross-product math** | 855 unique bill-position joins × avg 1.52 primary sponsors → 1,299 bill chain rows |
| **Most-lobbied bill** | HB 96 (FY 2026-27 budget — 73 chain rows) |

---

## Schema

18 columns, tab-separated.

| Column | Type | Example | Notes |
|---|---|---|---|
| `report_period` | str | `2025-01-01..2025-04-30` | OH AER reporting period; 3 windows/year |
| `filing_id` | str | `20250314EUPA1394434` | OH AER report ID — joins back to source provenance |
| `principal_name` | str | `Ohio Poverty Law Center` | From `LobbyingFiling.employer.name` |
| `principal_id` | str | `org-ohio-poverty-law-center` | **Derived deterministically from `principal_name`** at composer time (`org-{slug}`, where the slug is NFKD-folded to ASCII, lowercased, with runs of non-alphanumerics collapsed to single hyphens). The model-emitted `LobbyingFiling.employer.id` is intentionally NOT read — see "Entity-ID derivation" below. |
| `lobbyist_name` | str | `Susan M Jagers` | From `LobbyingFiling.filer_person.name` |
| `lobbyist_id` | str | `person-susan-m-jagers` | **Derived deterministically from `lobbyist_name`** (same slug algorithm, `person-{slug}`). |
| `position_kind` | enum | `bill_referenced` / `subject_general` / `subject_hoisted_from_description` | §4a Step A: which of the three `LobbyingPosition` fields carries the subject |
| `bill_label_raw` | str | `HB 96` | The display label — `bill_reference.original_text` for bill-referenced positions; the subject text otherwise |
| `bill_label_normalized` | str | `HB 96` | Normalized form (uppercase + dot-stripped + ws-collapsed) used as the join key for `bill_class == "bill"` rows |
| `bill_class` | enum | `bill` / `subject` / `jcarr` / `oac_rule` / `unmatched` | §6 OAC table + §4a subject row (Step B classification) |
| `bill_id` | str \| null | `ocd-bill/ocd-jurisdiction/country:us/state:oh/government/sessions/136/bills/...` | Plural Policy bill ID when `bill_class == "bill"`; null otherwise |
| `bill_title` | str \| null | `Make state operating appropriations for FY 2026-27` | From `OH_136_bills.csv.title`; null for non-bill rows |
| `position_description` | str \| null | `support the appropriations` | From `LobbyingPosition.description`; null for `subject_hoisted_from_description` rows (description was hoisted into `bill_label_raw`, see §4a) |
| `num_primary_sponsors` | int | `2` | Count of primary sponsors on the bill (0 for non-bill rows) |
| `sponsor_lawmaker_id` | str \| null | `ocd-person/aaa-bird-id` | From `OH_136_bill_sponsorships.person_id` (one row per primary); null for non-bill rows |
| `sponsor_lawmaker_name` | str \| null | `Rep. Adam Bird` | From `OH_136_bill_sponsorships.name`; null for non-bill rows |
| `sponsor_role` | str \| null | `primary` | Always `primary` in v1; null for non-bill rows. v1.1 cosponsor follow-up will add `cosponsor` rows. |
| `confidence` | enum | `direct` | One of: `direct` (bill class, joined to Plural), `oac_dropped` (jcarr/oac_rule), `subject_only` (subject_general / subject_hoisted), `unmatched` (classifier flagged or join failed), `null_extraction` (empty position sentinel) |

---

## Per-row routing — what each class means

Per the §4a "Conservation implication" and §6 OAC routing tables:

| Source position | bill_class | Sponsor fields | confidence | Row count contribution |
|---|---|---|---|---|
| `bill_reference` set, label matches Plural | `bill` | populated (cross-product over primaries) | `direct` | N (one per primary) |
| `bill_reference` set, label matches Plural, bill has 0 primaries (defensive) | `bill` | null | `direct` (with `num_primary_sponsors=0`) | 1 |
| `bill_reference` set, label looks like bill (HB/SB/HR/SR/...) but doesn't join Plural | `unmatched` | null | `unmatched` | 1 |
| `bill_reference` set, label = `JC \d...` | `jcarr` | null | `oac_dropped` | 1 |
| `bill_reference` set, label = `\d+-\d+-\d+` | `oac_rule` | null | `oac_dropped` | 1 |
| `bill_reference` set, label is neither bill nor admin-rule shape, **contains a digit** (e.g., `'Ch. 4757-5'`, `'CB DOH0105168'`) | `unmatched` | null | `unmatched` | 1 |
| `bill_reference` set, label is neither bill nor admin-rule shape, **contains NO digit** (e.g., `'Early Intervention'`, `'Accessible Housing'`) | `subject` (demoted) | null | `subject_only` (with `position_kind = subject_general`) | 1 |
| `bill_reference` null, `general_issue_area` set | `subject` | null | `subject_only` | 1 |
| `bill_reference` null, `general_issue_area` null, `description` set | `subject` | null | `subject_only` (with `position_kind = subject_hoisted_from_description`) | 1 |
| All three fields null (defect) | `null` (sentinel) | null | `null_extraction` | 1 |

---

## Conservation rules (read before quantitative use)

1. **Multi-primary cross-product.** A single position on a multi-primary bill emits N rows. OH allows multi-primary sponsorship on 40.8% of bills (one ceremonial House Resolution has 99 primaries). **`SUM(num_primary_sponsors)` is not a sponsor count** — it overcounts by the multiplier. Aggregate by `(filing_id, position_index)` or by `bill_label_normalized` per filing to deduplicate.

   - Example: a lobbyist files a position on `HB 96` (1 primary) and `HB 1` (2 primaries) → emits 1 + 2 = 3 chain rows. The lobbyist tracked 2 bills, not 3.

2. **`bill_class != 'bill'` rows do not join to Plural.** Subject / JCARR / OAC / unmatched rows have null `bill_id`. **Do not** `INNER JOIN OH_chain ... ON bill_id = ...` — that silently drops 290 rows (18% of the chain). Use `LEFT JOIN` or filter `WHERE bill_class = 'bill'` explicitly.

3. **Subject-only rows are real lobbying activity**, not nulls. They represent advocacy on a topic (e.g., "Public Safety", "Aging") that the lobbyist did not pin to a specific bill — common for executive-agency advocacy and ongoing-issue coalitions. **Do not filter them out** without a deliberate reason.

4. **The 8 unmatched rows are an extraction-quality canary.** Inspect with `WHERE confidence = 'unmatched'` to see the patterns. As of the 2026-06-15 composer-side normalization re-roll, the `unmatched` count dropped from 18 → 8: 10 no-digit subject-leak rows were demoted to `subject_general + subject` (see "Per-row routing" + "Entity-ID derivation and bill_referenced demotion" below). The 8 survivors are all digit-containing, mostly OAC variants the regex doesn't cover (e.g., `5180:4-5-09.1` with a colon, `Ch. 4757-5, -6, ...`) plus a handful of document references (`CB DOH0105168`).

5. **Stance not disclosed.** OH AER carries no support/oppose/monitor signal at the position level. Same as WI. The chain says "the lobbyist tracked this bill," not "for or against." (The `position_description` column sometimes hints at stance — `"support the appropriations"`, `"strike section 1"` — but is not structured.)

6. **`extract_position_label` uses `original_text` not `bill_number`** (open follow-up). If a position's `bill_reference.original_text` carries extra text (e.g., `"HB 96 BUDGET BILL"`), the join may fail and the row downgrades to `unmatched`. In the current 316-filing slice no such labels appear, so the practical impact is zero. The full-corpus run after #35 may surface a few; tracked at Phase 2 findings doc.

---

## Entity-ID derivation and bill_referenced demotion (2026-06-15 normalizations)

Two composer-side normalizations were landed 2026-06-15 to close the
release artifact's residual disagreement between sonnet- and mini-
sourced chains (chain-level mini-swap experiment, leave-behind-prep).
Both apply uniformly to every chain row regardless of extractor — they
are general composer policy, not a "fix mini to look like sonnet" hack.

### Entity-ID derivation (`principal_id` / `lobbyist_id`)

Both ID columns are **derived deterministically from the corresponding
name** at composer time:

- `principal_id = "org-" + slug(principal_name)`
- `lobbyist_id  = "person-" + slug(lobbyist_name)`

where `slug` is: NFKD-normalize → ASCII-fold (drop accents) →
lowercase → replace any run of non-alphanumerics with a single hyphen →
strip leading/trailing hyphens. Empty / whitespace-only input yields
`null` (the `org-`/`person-` prefix is not attached to nothing).

The model-emitted `LobbyingFiling.employer.id` / `filer_person.id`
fields are intentionally NOT read. Pre-normalization, those fields
carried three inconsistent conventions in the sonnet baseline alone
(`org-{slug}`, `oh-org-{slug}`, `org-{slug}-oh`), plus an occasional
truncation on long names; mini's extractions used yet other formats.
Composer-side derivation collapses that to one stable convention.

**Consequence for downstream consumers:**

- The `principal_id` / `lobbyist_id` columns in this preview release
  differ from any prior cut of the artifact for ~43% of distinct
  principals and ~31% of distinct lobbyists (the changes are
  format-only; the underlying names are identical).
- Joining this chain TSV to `releases/oh/filings/` on `principal_id` or
  `lobbyist_id` is safe — the filings composer applies the same
  derivation, so the two TSVs are consistent.
- Collisions (two distinct names slugifying to the same ID) are
  measured and currently 0/132 organizations and 0/123 people on this
  corpus.

### bill_referenced demotion when label has no digits

When a position's `bill_reference` is set and its label classifies as
`unmatched` (no HB/SB/JC/OAC pattern match) AND the label contains no
digits, the composer **demotes** the row from
`bill_referenced + unmatched` to `subject_general + subject`.

**Rationale:** every real OH bill, OAC rule, or JCARR citation
contains at least one digit. A label with no digits is structurally
incapable of being a bill / rule / JCARR reference and is almost
always subject content that the filer placed in the wrong schema
slot. Demoting it routes it to the correct conceptual bucket
(subject_general) where downstream consumers will sum it correctly.

Digit-containing unmatched labels (e.g., `'5180:4-5-09.1'`,
`'Ch. 4757-5, -6, -9, ...'`, `'CB DOH0105168'`) are preserved as
`unmatched` so the genuinely-malformed-bill audit signal survives.

**Impact on this release:** 10 of sonnet's 18 pre-normalization
unmatched rows demoted (all unambiguous subject content like
"Accessible Housing", "Early Intervention", "Federal IDEA
funds/schools"); 8 surviving unmatched rows are all clean
malformed-bill-shape audit content.

### Reference

Plan + post-fix acceptance experiment live on the
`oh-composer-mini-swap-normalizations` branch under
`docs/active/oh-composer-mini-swap-normalizations/`. The originating
chain-level experiment lives on `leave-behind-prep` under
`docs/active/leave-behind-prep/{convos,results,plans}/20260615_*`.

---

## Provenance

| | |
|---|---|
| **Source disclosure data** | OH AER extractions at `data/oh_portal/extracted/*/*/filing.json` (316 cached; gitignored — generated via `oh_portal/` per PR #33) |
| **Source bill metadata** | `data/bills/OH/136/OH_136_bills.csv` + `OH_136_bill_sponsorships.csv` (Plural Policy 136th GA export, 2026-06-07) |
| **Generating code** | [`src/lobby_analysis/allocation/oh/chain.py`](../../../src/lobby_analysis/allocation/oh/chain.py) (composer); [`classify.py`](../../../src/lobby_analysis/allocation/oh/classify.py) (Steps A+B); [`load.py`](../../../src/lobby_analysis/allocation/oh/load.py) (typed loaders + dedup helper) |
| **CLI** | `uv run python -m lobby_analysis.allocation.oh.cli materialize --extractions ... --bills ... --out releases/oh` |
| **Tests** | `tests/allocation/oh/` — 186 tests (139 baseline + 47 added 2026-06-15 for the entity-ID derivation + bill_referenced demotion normalizations), no DB / network / real-data required |
| **Methodology** | Plan at [`docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`](../../../docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md) §4 (schema), §4a (position-shape normalization, added 2026-06-14), §6 (OAC routing); per-phase findings under `results/` |

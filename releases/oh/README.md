# Ohio lobbying disclosure — 2025-2026 session (PREVIEW release)

A snapshot of structured lobbying-disclosure data extracted from the [Ohio Joint Legislative Ethics Committee's lobbying portal](https://www2.jlec-olig.state.oh.us/olac/) for the **2025-2026 legislative biennium (136th General Assembly)**, joined to Plural Policy's bulk bill bundle.

> **PREVIEW SCOPE.** This release is built from a **316-filing slice** of the OH AER cache (≈0.7% of the 45,605 AERs in `data/oh_portal/discover/recent.tsv`). The slice was drawn from agents-with-recent-activity per `results/20260605_slice_validation_300.md`; **53% of those 316 filings are nil** (the most-volume principals had no activity in the slice window). The full-corpus run (~$800, ~24 hr async, tracked at issue [#35](https://github.com/danparshall/lobby_analysis/issues/35)) replaces this preview when it lands. Filenames end in `_preview` until then.

**Audience:** colleagues kicking the tires on the OH track + analysts wanting to see chain shape before the full corpus ships. **Provisional research data, not a published product.**

---

## TL;DR

| | |
|---|---|
| **State** | Ohio |
| **Vintage** | 136th General Assembly (2025-2026) |
| **Files** | 3 TSVs (~820 KB total) |
| **Source: lobbying disclosure** | OH AER extractions, 316-filing slice; full corpus at issue #35 |
| **Source: bill metadata** | [Plural Policy](https://open.pluralpolicy.com/) 136th GA bulk export (2,325 bills, 11,559 sponsorship rows) |
| **Source: lawmaker roster** | [Open States `oh.csv`](https://data.openstates.org/people/current/oh.csv) (99 House + 33 Senate) |
| **Distinct canonical filings** | 305 |
| **Distinct principals** | 284 (filed via `employer.name` on the AER) |
| **Distinct lobbyists** | 231 (filed via `filer_person.name`) |
| **Position-grain chain rows** | 1,589 — see [`chain/`](chain/) |
| **Gift-event rows (II.A + II.B)** | 0 — see [`gifts/`](gifts/) for what that means |
| **Filing-grain rows** | 305 — see [`filings/`](filings/) |
| **Key acronyms** | **AER** = Activity & Expenditure Report (OH's periodic lobbying disclosure). **OLAC** = OH Legislative Activity & Conduct portal. **JCARR** = Joint Committee on Agency Rule Review (administrative-rule oversight). **OAC** = Ohio Administrative Code. **OS/PP** = Open States / Plural Policy. |

---

## What's in this release

Three sibling TSVs, each at a different grain. Read the per-artifact README before quantitative use:

| File | Grain | Description |
|---|---|---|
| [`chain/OH_chain_2025_2026_preview.tsv`](chain/) | per `(filing, position, sponsor)` | 18-column principal → lobbyist → bill → sponsor chain. Subject-only positions emit single rows with null sponsor fields (§4a). |
| [`gifts/OH_gifts_2025_2026_preview.tsv`](gifts/) | per `(filing, gift event)` | OH's distinctive native edge — Section II.A gifts + II.B meals. **Empty in this preview** (see caveat below). |
| [`filings/OH_filings_2025_2026_preview.tsv`](filings/) | per filing | Per-AER summary including the stated-zero (`total_expenditure → 0.0`) and `is_current` normalizations. |

---

## Why OH is structurally different from WI and NY

(Repeated from `docs/STATE_COVERAGE.md` for analysts opening this release first.)

| Edge | WI shape | NY shape | OH shape |
|---|---|---|---|
| principal ↔ lobbyist $ | IPF inference from row+col sums | JOIN on per-pair `total_compensation` | **not disclosed** (skip) |
| principal ↔ lobbyist time | hours_comm + hours_other (filed %) | — | **not disclosed** (skip) |
| principal ↔ bill | `bill_efforts` at principal grain | per-filing `parties_lobbied` | **via lobbyist's positions[]** |
| **lobbyist ↔ lawmaker $** | — | contact-only, no $ | **✓ NATIVE (AER II.A/B)** — see [`gifts/`](gifts/) |
| lobbyist ↔ bill | `bill_efforts × allocation` | — | `positions[]` |
| lawmaker ↔ bill | Plural Policy | Plural Policy | Plural Policy |

**Three deltas from WI.** (1) No IPF needed: OH has no marginals to fit (no per-pair compensation or hours disclosure). The chain is **pure edge enumeration**, more like NY's JOIN than WI's IPF. (2) The gifts edge is native to OH. (3) Same as WI: no stance disclosed — chain says "lobbied on," not "for or against."

**Two deltas from NY.** (1) No per-pair compensation. (2) **OAC admin-rule citations** (13.6% of extracted bill-row references) — OH lobbyists track regulatory advocacy alongside legislative bills on the AER. Plural Policy bundles cover bills only, so OAC + JCARR rows in the chain are flagged with `bill_class ∈ {oac_rule, jcarr}` and null `bill_id`.

---

## Caveats (read before quantitative use)

1. **316-filing slice is non-representative.** Most-volume principals may not appear; 53% of the slice is nil. **The full-corpus run (issue #35) is the deliverable**, not this preview. Do not compute rankings or coverage statistics that depend on completeness.

2. **0 gift-event rows — empirical base-rate finding, not a defect.** OH AER Sections II.A (gifts) and II.B (meals) returned zero itemized events across all 305 cached filings. A 2026-06-15 spot-check (`docs/active/oh-portal-extraction/results/20260615_gifts_spotcheck_findings.md`) confirmed: 93.8% of filings have empty Section II ("No expenditures"); of the 6.2% with content, **zero** have itemized II.A or II.B rows. All disclosed activity is the non-itemized sub-$50 meal aggregate, correctly extracted to `category="entertainment"` and visible in `filings/` via `total_expenditure`. The extraction-prompt-scope hypothesis is ruled out. The `gifts/` README documents the empty state with full diagnostic detail.

3. **8 chain rows are extraction defects** (`bill_class == "unmatched"`). All are digit-containing malformed-bill-shape labels: OAC variants the regex doesn't cover (colons, "Chapter" prefix, comma-listed rules), or malformed document identifiers like `CB DOH0105168`. **Surfaced, not hidden.** Filter `WHERE confidence = 'unmatched'` to inspect them as a quality canary. (As of the 2026-06-15 composer-side normalizations: 10 no-digit unmatched rows that were actually subject content placed in `bill_reference` — e.g., `Early Intervention`, `Accessible Housing` — now route to `subject_general + subject + subject_only` instead of polluting the unmatched bucket. See `chain/README.md` §"Entity-ID derivation and bill_referenced demotion" for the rule.)

4. **Multi-primary cross-product.** OH allows multiple primary sponsors on a bill (40.8% of bills, with 99 primaries on a few ceremonial House Resolutions). Each bill chain row × N primaries = N rows. The schema's `num_primary_sponsors` column tells you the multiplier; **don't naively `SUM(amount)` across sponsor rows** — that would multi-count. Aggregate by `(filing_id, position_id)` first.

5. **Position-shape normalization (§4a).** A position can carry its subject in any of three fields: `bill_reference` (canonical), `general_issue_area` (subject-only canonical), or `description` (mini-model quirk). The composer routes all three through Step A; subject-only positions get one chain row with null sponsor fields and `confidence='subject_only'`. **Subject-only positions are real lobbying activity**, not nulls — they're just not joinable to bills by design.

6. **OH AER carries no compensation disclosure** (principal↔lobbyist $). OH discloses bill-level activity + gifts/meals, not the $ relationship between principal and lobbyist. **Structural gap**, not a missing column.

---

## Provenance

| | |
|---|---|
| **Originating branch** | `oh-chain-composer` (this PR; cut from `bfe9f8f` 2026-06-14) |
| **Predecessor** | `oh-portal-aprime-batch` (PR #33, merged) — extraction pipeline |
| **Generating code** | [`src/lobby_analysis/allocation/oh/`](../../src/lobby_analysis/allocation/oh/) — `classify.py`, `load.py`, `chain.py`, `gifts.py`, `filings.py`, `cli.py` |
| **Plan** | [`docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md`](../../docs/active/oh-portal-extraction/plans/20260611_oh_chain_composer_design.md) (updated 2026-06-14) |
| **Phase findings** | [`docs/active/oh-portal-extraction/results/`](../../docs/active/oh-portal-extraction/results/) — `20260614_phase0_preflight_audit.md`, `20260614_phase1_loaders_findings.md`, `20260614_phase2_chain_findings.md` |
| **Reproducer** | See "Reproducer" below |

---

## Reproducer

```bash
# 1. Get the OH AER extractions (PR #33 already merged).
git checkout main
# data/oh_portal/extracted/ is gitignored; either re-run the extraction
# pipeline or pull from machine-local cache (~/data/lobby_analysis/).

# 2. Plural Policy bundle (already in repo via Dan's data drop 2026-06-11).
# data/bills/OH/136/*.csv (16 CSVs; 2,325 bills, 11,559 sponsorships)

# 3. Open States legislator roster.
wget https://data.openstates.org/people/current/oh.csv \
  -O data/bills/OH/oh.csv

# 4. Run the composer CLI.
uv run --active python -m lobby_analysis.allocation.oh.cli materialize \
  --extractions data/oh_portal/extracted \
  --bills       data/bills/OH/136 \
  --oh-csv      data/bills/OH/oh.csv \
  --out         releases/oh
```

Tests: `uv run python -m pytest tests/allocation/oh/` (139 tests, pure-logic, no DB / network / real data required).

# FOCAL Phase A4 — Supplementary File Audit (2026-05-07)

## TL;DR

The supplementary PDF on disk (`papers/Lacy-Nichols-Supple-File-1-IJHPM.pdf`) is the
2024 IJHPM paper's **Supplementary File 1: Database and Grey Literature Search
Strategies**, NOT the 2025 paper's supplementary file. The 2025 *Milbank Quarterly*
paper's Supplementary File 1 (containing Tables 1–5, including the per-indicator
scoring rules in Table 3, the cross-rubric mapping in Table 4, and the per-country
unweighted matrix in Table 5) is **referenced but not on disk**.

Phase A4 was completed using the data that IS available — primarily Figure 3 of
the 2025 main paper, which contains the full weighted 28-country × 50-indicator
scoring matrix. The US row sums to **81/182 = 44.5% ≈ 45%**, matching the
published total exactly.

## What was on the supplementary PDF

`Lacy-Nichols-Supple-File-1-IJHPM.pdf` (4 pages) contains:

- Page 1: Article title block + footnote ("Supplementary file 1. Database and Grey
  Literature Search Strategies"). Journal = **International Journal of Health
  Policy and Management (IJHPM)** — the 2024 framework definition paper.
- Page 2: Concept synonym groups (Framework / Lobbying / Transparency) + database
  search strategies for Scopus, Web of Science, ProQuest, JSTOR, Business Source
  Complete (dated 8/03/2023).
- Pages 3–4: Grey-literature searches (Google Advanced + 24 targeted website
  searches dated late March / early April 2023).

This supplementary file does NOT contain Tables 3, 4, or 5 referenced in the
2025 paper. There is no per-indicator scoring rule, no cross-rubric weighting
mapping, and no per-country score matrix in this PDF.

## What the 2025 paper says about its supplementary

From `papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows.txt`:

- Line 183: "28 countries with online lobbyist registers (Supplementary File 1
  Table 1)" — country list.
- Line 185: "the policy, legislation, act, code, or other legal instrument that
  underpinned the register (Supplementary File 1 Table 2)" — sources of law.
- Lines 195–196: "creating a set of notes to assign a value of yes, no, or
  partly for each of the indicators, weighted two, one, and zero, respectively
  (Supplementary File 1 Table 3)" — per-indicator scoring rules.
- Line 199: "we reviewed the three frameworks with weighted indicators and
  mapped them against our 50 indicators (see Supplementary File 1 Table 4 for
  details)" — cross-rubric mapping.
- Line 304: "Figure 3; see also Supplementary File 1 Table 5, which shows the
  unweighted benchmarking" — Figure 3 = weighted; Suppl Table 5 = unweighted
  version of same matrix.
- Line 2930ff: "Supplementary Material … Additional supporting information may
  be found in the online version of this article at
  http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1468-0009"

The 2025 paper is in Milbank Quarterly (not IJHPM); its supplementary file is
hosted at the Wiley URL, not on disk in this repo.

## What I extracted instead

### 1. items_FOCAL.tsv — `scoring_rule` populated from 2025 main text

The scoring scheme is documented in the **main paper** (line 195–196, verbatim):

> "creating a set of notes to assign a value of yes, no, or partly for each of
> the indicators, weighted two, one, and zero, respectively"

This applies uniformly across all 50 indicators as the BASE rule. Per-indicator
**weights** are not given verbatim in the main text but can be **inferred from
Figure 3's max-observed cell value per row** (the legend says cells are colour-
coded 0, 1, 2, 3, 4, 6, with no 5 — implying weights ∈ {1, 2, 3} where weight 1
gives 0/1/2, weight 2 gives 0/2/4, weight 3 gives 0/3/6).

I have populated `scoring_rule` with the verbatim main-text rule and annotated
each indicator with its inferred weight in `notes`. The literal Suppl Table 3
text is **not** quoted in `source_quote` — instead `source_quote` cites the main
paper's methodology section.

### 2. focal_2025_lacy_nichols_per_country_scores.csv — Figure 3 (WEIGHTED)

Figure 3 from the 2025 paper main text contains the weighted scoring matrix for
28 countries × 50 indicators. The text extraction in
`papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows.txt` (lines 347–1968)
preserves both indicator labels and the column-major numerical grid. I have
parsed this into a tidy long-format CSV with columns:

- `country` (28 countries, in Figure 3's display order: Canada → Netherlands)
- `indicator_id` (joins to items_FOCAL.tsv `indicator_id`)
- `weighted_score` (cell value from Figure 3; integers 0,1,2,3,4,6 or `NA` if
  en-dash "–" indicating "could not be assessed")

**Caveats:**

- Figure 3 has **50 rows** but FOCAL 2024 has 50 indicators with two adjustments
  in the 2025 application:
  1. **timeliness.1 + timeliness.2 merged** into one combined indicator
     ("Changes ... and activities ... are updated close to real time"). The 2025
     paper says explicitly (line 202–204): "we combined two of the timeliness
     indicators (around updating changes in general versus activities), as the
     answers were the same across all registers." Net: 50 → 49 in 2025 register
     scoring.
  2. **A new "Lobbyist list" indicator was added** to the Relationships category
     (line 213: "We created an additional indicator for listing the lobbyists
     employed by a company or lobby firm, as we found this was inconsistently
     disclosed"). Net: 49 → 50.

  So the 2025 application uses 50 indicators that map to FOCAL 2024's 50 with
  one merge (-1) and one addition (+1). The CSV uses the 2025 application
  indicator IDs to preserve verbatim Figure 3 fidelity. A
  `focal_2024_indicator_id_map` column shows the join back to FOCAL 2024.

- Suppl Table 5 (the **unweighted** version) is not on disk. The CSV uses
  Figure 3 (weighted) values — these can be back-derived to unweighted via
  weighted/weight = 0/1/2 (no/partly/yes), but the CSV ships the weighted
  values verbatim as published. A `raw_score` column gives the inferred yes/
  no/partly base value (0/1/2).

### 3. focal_2025_lacy_nichols_prior_framework_mapping.csv — NOT extracted

Suppl Table 4 is not on disk. Three prior weighted frameworks are named in the
**2024** paper (refs 31, 33, 34):

- **Bednářová 2020** ("The evaluation of the government draft lobbying act in
  the Czech Republic")
- **Hired Guns 2007** (Center for Public Integrity)
- **Roth 2020** ("Creating a Valid and Accessible Robustness Index")

A stub CSV is created at
`focal_2025_lacy_nichols_prior_framework_mapping.csv` containing only the
framework names + a placeholder row per FOCAL 2025 indicator with NULL mapping.
The actual cross-rubric mapping requires retrieving the 2025 paper's Suppl
Table 4 (Wiley online, not on disk).

## Sanity check: US row total

Computed from the per-country CSV (US column, all 50 indicators):

```
Scope:         4 + 0 + 0 + 2  =  6
Timeliness:    0 + 0          =  0
Openness:      4 + 0 + 6 + 3 + 6 + 2 + 2 + 2 + 2  =  27
Descriptors:   4 + 2 + 0 + 0 + 2 + 0  =  8
Revolving door: 6 + 0  =  6
Relationships:  6 + 2 + 0 + 0 + 0  =  8
Financials:    4 + 4 + 0 + 0 + 0 + 4 + 0 + 0 + 0 + 0 + 4  =  16
Contact log:   2 + 0 + 2 + 0 + 0 + 0 + 0 + 0 + 3 + 0 + 3  =  10
TOTAL:         81
```

**81 / 182 = 44.5% ≈ 45%** — matches Figure 3's published US Score column
exactly. Extraction is verified.

## What's missing / what to do next

To fully complete Phase A4 per the original plan:

1. **Retrieve the 2025 paper's Supplementary File 1** from Wiley
   (https://onlinelibrary.wiley.com/doi/10.1111/1468-0009.70033). This contains
   verbatim Tables 3, 4, 5.
2. Populate `items_FOCAL.tsv` `scoring_rule` and `source_quote` with verbatim
   Suppl Table 3 text (currently the rule is from main-text methodology).
3. Build `focal_2025_lacy_nichols_prior_framework_mapping.csv` from Suppl Table 4.
4. Replace the weighted Figure 3 CSV with the unweighted Suppl Table 5 CSV (or
   add a parallel CSV) — the unweighted version makes the per-indicator scoring
   logic transparent.

For now, the project's primary need (the **US calibration anchor**) is met:
the US row from Figure 3 is captured, sums to the published 81/182 = 45%, and
is structurally joinable to other rubrics' per-indicator scores via
`indicator_id`.

---

## Followup attempt 2026-05-07 (pm) — Wiley retrieval BLOCKED

Attempted to retrieve `Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_file_1.pdf`
from Wiley Online Library to close the 8 weight=UNKNOWN indicators
(`descriptors.6`, `revolving_door.2`, `relationships.4`, `financials.5`,
`financials.7`, `financials.9`, `financials.10`, `contact_log.8`) and populate
the cross-rubric mapping (Suppl Table 4) and unweighted matrix (Suppl Table 5).

**Outcome: download failed.** All retrieval routes were blocked:

- `WebFetch https://onlinelibrary.wiley.com/doi/10.1111/1468-0009.70033` → **403 Forbidden**
- `WebFetch` on `/doi/full/`, `/doi/abs/`, `/doi/pdf/`, `/doi/epdf/` variants → all **403**
- `WebFetch` on guessed `action/downloadSupplement?doi=...&file=milq70033-sup-0001-*.pdf`
  candidate URLs → all **403**
- `WebFetch` on Milbank Memorial Fund article landing
  (`https://www.milbank.org/quarterly/articles/lobbying-in-the-shadows-...`) →
  **timeout (60 s)** on multiple attempts.
- `WebFetch` on web.archive.org → tool refuses ("unable to fetch from web.archive.org").
- PMC version of the paper is **PMC12438441, not available until 2026-09-01**
  (per PubMed metadata).
- `curl` is on the ASK permission list and was **denied** for direct retrieval
  in this session.

**No fabrication.** Per task instructions ("If Wiley download fails …
document in audit note + stop. Do NOT fabricate"), I have not edited
`items_FOCAL.tsv` (the 8 UNKNOWN-weight rows remain UNKNOWN), have not
overwritten the stub `focal_2025_lacy_nichols_prior_framework_mapping.csv`,
and have not modified `focal_2025_lacy_nichols_per_country_scores.csv`.

**Recommended next step (manual):** download Suppl File 1 in a browser from
`https://onlinelibrary.wiley.com/doi/10.1111/1468-0009.70033` (Supporting
Information section near the bottom of the page) and place it at
`papers/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_file_1.pdf`. Then
re-run this followup against the on-disk file. Alternatively, grant the
agent `curl` permission for `onlinelibrary.wiley.com` and `milbank.org` for a
single retrieval attempt.

**Closed: 0 of 8 UNKNOWN-weight indicators.**
**Populated: 0 cross-rubric mapping rows (stub unchanged).**

---

## Followup completed 2026-05-07 (pm) — Suppl File 1 extracted from docx

The 2025 paper's Supplementary File 1 was retrieved separately and extracted to
`papers/text/Lacy_Nichols_2025__lobbying_in_the_shadows__suppl_001.txt` (738 lines).
The file contains all three load-bearing tables:

- **Suppl Table 3** ("FOCAL indicators and notes", lines 158-343) — verbatim P/N criteria per indicator.
- **Suppl Table 4** ("Details of weighted indicators", lines 346-513) — cross-rubric weight mapping with columns Bednarova(CII) | CPI | Roth | Total | Our weights. Header rationale (lines 348-355): "Scores 10 and higher were weighted 3, scores 1 and higher were weighted 2. We also identified four indicators that we believe are crucial to transparency and also warrant a weight of 3 based on our experience".
- **Suppl Table 5** ("Benchmarking completeness of indicators", lines 515-724) — 28-country × 50-indicator UNWEIGHTED raw scores (0/1/2 or "/" for unassessable), plus a published "TOTAL (out of 100pts)" row.

### What was updated

**1. items_FOCAL.tsv** — `scoring_rule` column for all 50 rows replaced with:
`Verbatim "Our weights" from Suppl File 1 Table 4: <W>. Base scoring rule (main text line 195-196): yes=2, partly=1, no=0; cell value = base × weight. Verbatim P/N criteria (Suppl Table 3): <pn>.`

- **8/8 UNKNOWN-weight indicators closed** with verbatim values:
  - `descriptors.6` (type of lobbyist contract) → weight 1
  - `revolving_door.2` (cooling-off period database) → weight 1
  - `relationships.4` (direct business associations with public officials) → weight 2
  - `financials.5` (amount of time on lobbying) → weight 2
  - `financials.7` (compensated/uncompensated) → weight 2
  - `financials.9` (expenditure on membership/sponsorship) → weight 1
  - `financials.10` (expenditures benefitting officials) → weight 2
  - `contact_log.8` (materials shared in meetings) → weight 1
- **40/42 Figure-3-inferred weights match verbatim Table 4** exactly.
- **2 conflicts found and resolved (verbatim wins):**
  - `financials.3` (Income sources): Figure-3-inferred 1 → verbatim **2**.
  - `financials.8` (Expenditure per issue): Figure-3-inferred 1 → verbatim **2**.
  - In both cases the published Figure 3 *weighted* cell values were correct (Canada/Germany financials.3 = weighted 2 = raw 1 × weight 2; France financials.8 = weighted 2 = raw 1 × weight 2). Only the decomposition was wrong in the existing CSV. Substantive raw_score values updated 2 → 1 for those three cells; weighted_score unchanged.

**2. focal_2025_lacy_nichols_prior_framework_mapping.csv** — replaced stub with full verbatim Suppl Table 4. **50 rows** with columns `indicator_id, indicator_text, bednarova_cii, cpi_normalised, cpi_original, roth_normalised, roth_original, total_unweighted, our_weight, source_quote`. Original (non-normalised) CPI/Roth weights are captured in `*_original`; the normalised values (against Bednárová) are in `*_normalised`.

  Weight distribution across the 50 indicators: 20 × weight-1, 19 × weight-2, 11 × weight-3. Total max = 2 × (1×20 + 2×19 + 3×11) = 2 × 91 = **182 points** (matches published).

**3. focal_2025_lacy_nichols_per_country_scores.csv** — 1,400 rows updated.
   - **1,327 cells matched** Suppl Table 5 verbatim raw values exactly.
   - **45 cells differed** — patterns:
     - 27 cells: existing-CSV blank/0 → Suppl-Table-5 "/" (unassessable). Mostly Ministerial-diary rows (`timeliness.3`, `openness.2`) where countries with no diary have empty cells.
     - 2 cells: Georgia `financials.1` and `financials.2` — existing blank → Suppl 0 (Suppl renders these as literal blank cells but the column total of 2 implies they are counted as 0). Captured as 0 with audit note.
     - 13 cells: Finland descriptors / revolving-door / relationships.1 / contact_log.* — existing concrete 0s and 2s → Suppl "/" (the existing extractor recorded Figure-3 visual reads as concrete; Suppl Table 5 is authoritative). Finland's weighted total updated from 70 → **46** as a result.
     - 3 cells (raw-value substantive): Canada/`financials.3` (2 → 1), Germany/`financials.3` (2 → 1), France/`financials.8` (2 → 1). Weighted values unchanged because weight changed 1 → 2.
   - All 28 per-country weighted totals now reproduce Figure 3 percentages exactly (US 81/182 = 44.5% ≈ 45%; Canada 89/182 = 48.9% ≈ 49%; Netherlands 16/182 = 8.8% ≈ 9%; …).

**4. items_FOCAL.md** — methodology note updated to reflect verbatim sourcing, distribution table, conflict report, and Finland-NA correction.

### Discrepancy WITHIN the supplement (flagged, not fixed)

Suppl Table 5 includes a "TOTAL (out of 100pts)" row at the top: 47, 46, 42, 39, 38, 34, 27, 27, 26, 25, 24, 24, 24, 23, 22, 23, 23, 21, 21, 21, 19, 18, 16, 15, 14, 10, 9, 7. These differ from the main-paper Figure 3 percentages (49, 48, 45, 43, 43, 40, 38, 31, 31, 30, 29, 27, 27, 27, 27, 27, 26, 23, 23, 23, 20, 20, 18, 16, 16, 12, 11, 9 — using Figure 3's column ordering, which differs slightly from Suppl Table 5's). Computing weighted totals from Suppl Table 5 raw values × Suppl Table 4 weights reproduces **Figure 3 percentages exactly**, not the Suppl Table 5 TOTAL row. Concluding that Suppl Table 5's TOTAL row is itself in error (likely a stale draft); main-paper Figure 3 is authoritative.

### Sanity check: US row total

US row from verbatim Suppl Table 5 (raw values × verbatim Table 4 weights):
- Scope: 2×2 + 0×3 + 0×3 + 2×1 = 6
- Timeliness: 0×3 + 0×1 = 0
- Openness: 2×2 + 0×1 + 2×3 + 1×3 + 2×3 + 2×1 + 2×1 + 2×1 + 2×1 = 27
- Descriptors: 2×2 + 2×1 + 0×1 + 0×1 + 2×1 + 0×1 = 8
- Revolving door: 2×3 + 0×1 = 6
- Relationships: 2×3 + 1×2 + 0×1 + 0×1 + 0×2 = 8
- Financials: 2×2 + 2×2 + 0×2 + 0×1 + 0×2 + 2×2 + 0×2 + 0×2 + 0×1 + 0×2 + 2×2 = 16
- Contact log: 1×2 + 0×2 + 1×2 + 0×1 + 0×2 + 0×2 + 0×1 + 0×1 + 1×3 + 0×3 + 1×3 = 10
- **TOTAL = 81 / 182 = 44.5% ≈ 45%** ✓ (matches Figure 3)

**Closed: 8 of 8 UNKNOWN-weight indicators.**
**Populated: 50 cross-rubric mapping rows (Suppl Table 4 verbatim).**
**Per-country CSV: 45 cell corrections applied (mostly NA-handling for Finland and unassessable diaries); all 28 country totals reproduce Figure 3 exactly.**

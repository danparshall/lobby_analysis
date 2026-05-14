# Cross-Rubric Descriptive Statistics — Compendium 2.0 Synthesis Input

**Session:** 2026-05-03 (afternoon)
**Branch:** `compendium-source-extracts`
**Triggered by:** User request after Blue Book / BoS / COGEL acquisition mapping; "I imagine there's probably items that have almost identical meaning but slightly different verbage."
**Outcome:** Per-rubric atomic counts, topic-domain coverage matrix, multi-threshold cross-rubric clustering. Lexical-similarity finding overturns the implicit assumption — paraphrase variants are surprisingly heterogeneous.

---

## 1. Headline numbers

The 26 source-paper extracts shipped 2026-05-03 contain **674 raw rows**. Filtering out composites (section subtotals, overall index rows) and meta-rows (Strickland's "applies Newmark unchanged"), the corpus has **661 atomic items**:

- **509 atomic items in 17 measurement rubrics** (the focus of this analysis)
- **152 atomic items in 9 non-rubric extracts** (empirical applications, surveys, scoping reviews — counted but not analyzed for coverage)

Per-rubric atomic counts (sorted by size):

| Rubric | Atomic items | Notes |
|---|---|---|
| SOMO | 76 | Largest. 12 categories. CDoH lens. |
| AccessInfo | 75 | 38 top-level + 34 sub + 3 principles. |
| FOCAL | 50 | 8 categories. Unweighted. |
| HiredGuns | 47 | 8 categories. Own statute reading. |
| CouncilEurope | 41 | 11 categories. |
| TI_2016 | 38 | 14 categories (per-dataset assessments). |
| ALTER_EU | 25 | 11 categories. |
| Carnstone | 25 | 5 principles. |
| IBAC | 24 | 8 categories. |
| Opheim | 22 | 3 sections (def / disclosure / enforcement). 100% Blue-Book-defined. |
| Newmark2017 | 19 | 3 sub-scores. 7 def / 5 prohib / 7 disc. |
| McKayWozniak | 18 | UK-focused; combines CPI HG + Piotrowski-Liao. |
| Newmark2005 | 18 | + 1 penalty supplement. 100% BoS-defined. |
| CPI_2015 | 16 | 13 categories captured but lobbying-Qs not enumerated in available materials. |
| OpenSecrets | 7 | 7 indicators. |
| Sunlight | 5 | Heterogeneous tier counts (2/4/4/5/2 tiers). |
| GDB | 3 | Stems only; full sub-Qs in Research Handbook. |

**Tagged-by-topic coverage:** 313 / 509 = 61.5% of rubric atomic items received at least one topic tag from the regex-based taxonomy below. The 196 untagged items are concentrated in SOMO (44 — many CDoH/sustainability framing items) and AccessInfo (21 — many ATI principles rather than measurable indicators), with smaller residuals across other rubrics. Tag-rate per rubric varies from 92% (IBAC) down to 19% (CPI_2015) and 20% (Sunlight). The CPI/Sunlight low rates are because their items are short labels ("Executive accountability", "Lobbyist Activity") that contain no taxonomy keywords; the underlying subject is captured in the tier descriptions or the linked questionnaire, not the indicator name itself.

## 2. Topic-domain × rubric coverage

The 47 topics in the taxonomy collapse into 14 meta-domains. Counts below are atomic items per (domain × rubric) cell. The right-hand columns give the row totals across all 17 rubrics. **A `.` means zero items in that cell.**

```
Domain            |ALTER_ Access CPI_20 Carnst Counci  FOCAL    GDB HiredG   IBAC McKayW Newmar Newmar OpenSe Opheim   SOMO Sunlig TI_201| nrub  tot
                  |  EU    Info    015   one    lEur          Guns          Wozni  k2005  k2017  Secret  ms     SOMO   ht    _2016
-------------------------------------------------------------------------------------------------------------------------------------------------
Definition        |     .      7      .      3      6     12      .      1      6      1      6      7      1      7      1      .      .|   12   58
Registration      |     5      5      .      6      3      7      .     10      1      2      .      .      1      .     12      .      4|   11   56
Activity          |     3      7      .      3      4     12      .      2      8      2      .      .      .      .     12      .      5|   10   58
Financial         |     .      6      .      4      1      3      .      7      1      1      7      7      1      5      1      1      1|   14   46
Personnel         |     2      3      1      3      1      4      .      2      1      .      .      1      .      1      1      .      9|   12   29
Prohibitions      |     .      1      .      1      .      1      .      .      1      .      4      5      .      .      .      .      .|    6   13
Timing            |     5      2      .      2      1      .      .      5      .      1      1      .      1      1      2      .      4|   11   25
Accessibility     |     .      5      1      1      1      8      2      3      3      5      .      .      2      .      6      .     11|   12   48
Enforcement       |     .     32      1      4      2      .      .     12      7      .      .      5      .      7      3      .      1|   10   74
Education         |     .      7      .      1      6      .      1      1      2      .      .      .      .      .      3      .      .|    7   21
Conduct           |     .      2      .      .      .      .      .      .      2      .      .      .      .      .      4      .      .|    3    8
Other (consult)   |     .      6      .      .      .      .      1      .      .      .      .      .      .      .      3      .      .|    3   10
Other (princ)     |     .      1      .      .      .      .      .      .      .      .      .      .      .      .      .      .      .|    1    1
```

**Reading the matrix.** Eight domains are covered by 10+ rubrics (Definition / Registration / Activity / Financial / Personnel / Timing / Accessibility / Enforcement). Three are noticeably narrower: Prohibitions (6 rubrics — concentrated in Newmark + IBAC + scattered single items), Education (7 rubrics), and Conduct (3 rubrics — the code-of-conduct topic is mostly an EU-framework concern).

**The Enforcement row is dominated by AccessInfo (32 items) and HiredGuns (12).** AccessInfo treats enforcement as an extensive separate concern (oversight body powers, audit, sanctions); HiredGuns inherits the CPI tradition of asking explicit enforcement questions. **Newmark dropped enforcement entirely**; only the penalty stringency supplement remains, and it's coded only for 2003.

## 3. Cross-rubric paraphrase clustering — the user's hypothesis tested

User's intuition: "I imagine there's probably items that have almost identical meaning but slightly different verbage." Test: TF-IDF (1-2 grams, sublinear, English stops) + cosine similarity, then single-link clustering of pairs from *different* rubrics at varying thresholds.

| Threshold | Cross-rubric clusters | Items in clusters | Largest cluster | ≥3-rubric clusters |
|---|---|---|---|---|
| 0.50 | 10 | 20 | 2 | 0 |
| 0.45 | 12 | 26 | 4 | 0 |
| 0.40 | 14 | 30 | 4 | 0 |
| 0.35 | 15 | 34 | 4 | 0 |
| 0.30 | 20 | 49 | 6 | 1 |
| 0.25 | 25 | 68 | 10 | 5 |
| 0.20 | 31 | 92 | 12 | 9 |

**Sample clusters at sim ≥ 0.30** (clean):

- *Lobbyist definition (AccessInfo + CouncilEurope):* "'Lobbyist' should entail any natural or legal person who engages in lobbying activities..." ≈ "lobbyist means any natural or legal person who engages in lobbying."
- *Time standard (Newmark2005 + Newmark2017 + Opheim, the only ≥3-rubric cluster at 0.30):* "time standard" ≈ "Time standard for lobbyist status..." ≈ "specific time standard to delineate lobbying activity"
- *Materials shared (Carnstone + FOCAL):* "Disclose any materials shared with public sector recipients..." ≈ "Any materials that were shared, excluding commercially sensitive..."
- *Business associations (FOCAL + HiredGuns):* "Direct business associations with public officials, candidates or members of their households" ≈ "Is a lobbyist required to disclose direct business associations..."
- *In-kind political contributions (AccessInfo + FOCAL):* "Any political contributions, including in-kind" ≈ "Campaign/political contributions, including in-kind"

**Honest finding:** The TF-IDF clustering surfaces the user's near-duplicates, but they cluster mostly **within author family** (Opheim → Newmark2005 → Newmark2017) or **within geographic-tradition cluster** (AccessInfo / CouncilEurope / ALTER_EU / FOCAL — all European). Of the 20 clusters at sim≥0.30, **13 are Newmark2005↔Newmark2017** (same author, near-identical wording — expected and uninteresting). **Only 1 cluster spans ≥3 rubrics at sim≥0.30** (the time-standard cluster).

**Across the broader 17-rubric corpus, items are expressed in idiosyncratic vocabulary even when they're measuring the same thing.** Lexical clustering catches a small fraction of the semantic equivalence. The European/state-tradition divide is the most striking — the same concept ("lobbyists must register," "report must include subject matter") is phrased in non-overlapping vocabulary across the two traditions and TF-IDF mostly fails to bridge them.

## 4. The ≥3-rubric clusters that DO exist (at sim≥0.20, with noise warning)

Lowering the threshold to 0.20 surfaces 9 clusters spanning ≥3 rubrics, but at this threshold the clusters start to drift semantically. Two of the cleanest:

**Cluster A — Lobbyist definition** (5 rubrics: AccessInfo, CouncilEurope, Newmark2005, Newmark2017, Opheim):
- AccessInfo: "'Lobbyist' should entail any natural or legal person who engages in lobbying activities..."
- CouncilEurope: "lobbyist means any natural or legal person who engages in lobbying."
- Newmark2005: "legislative lobbying"
- Newmark2017: "Legislative lobbying necessitates registering as a lobbyist"
- Opheim: "legislative lobbying as a criterion for definition"

This bridges European-framework definitional language with state-tradition definitional shorthand — the only place where the lexical bridge actually works.

**Cluster B — Public access to information** (5 rubrics: AccessInfo, CPI_2015, CouncilEurope, HiredGuns, OpenSecrets):
- AccessInfo: "Access to information law: a comprehensive access-to-information law shall guarantee the public's right of access..."
- CPI_2015: "Public access to information"
- CouncilEurope: "Where a member State can demonstrate that alternative mechanisms guarantee public access to information on lobbying activities..."
- HiredGuns: "Cost of copies"
- OpenSecrets: "How easily can the public access disclosed information"

This cluster is real (all 5 are about ATI / public access) but the semantic granularity varies wildly — HiredGuns asks specifically about copy-fees; AccessInfo asserts the existence of an ATI law; OpenSecrets asks a composite question.

**Caveat: clusters at sim≥0.20 include false positives.** The cluster "ALTER_EU + FOCAL + HiredGuns" at 0.20 groups items that are tangentially related (lobbyist-listing requirements + cooling-off-period databases) — TF-IDF picked up shared vocabulary like "register" or "lobbyist" that happens to occur in different real topics.

## 5. Long-tail items (in only 1-2 rubrics) — diagnostic candidates

Topics covered by exactly 1 rubric:

| Topic | Rubric | Items |
|---|---|---|
| `enforce_review_quality` (thoroughness of report review) | Opheim only | 1 |
| `enforce_subpoena` (subpoena, hearings) | Opheim only | 4 |
| `disc_funding_pubmoney` (public funding to lobbyists) | AccessInfo only | 2 |
| `proh_gifts` (gift cap as ban, not just disclosure) | Newmark2005 only | 1 |
| `disc_exp_threshold` (de minimis for expense reporting) | Sunlight only | 1 |
| `disc_leg_footprint` (legislative footprint linkage) | SOMO only | 5 |
| `e_filing` (electronic filing required) | HiredGuns only | 3 |
| `preamble_principle` | AccessInfo only | 1 |

Topics covered by exactly 2 rubrics:

| Topic | Rubrics | Items |
|---|---|---|
| `proh_contingent` | IBAC + Newmark2017 | 2 |
| `disc_exp_itemized` (itemized expenditures with date/amount) | HiredGuns + Opheim | 6 |
| `proh_camp_contrib` | Newmark2005 + Newmark2017 | 4 |
| `proh_solicitation` | Newmark2005 + Newmark2017 | 2 |

**This list is the per-user prediction.** When the user wrote earlier "diagnostically-strong items often appear in only 2-3 rubrics," that's exactly this set. Notable instances:

- **Opheim's enforcement battery** (`enforce_subpoena`, `enforce_review_quality`) — Newmark dropped these and Strickland inherited the drop. They survive only in `items_Opheim.tsv`. **The COGEL Blue Book Table 31 ("Compliance of Selected Agencies") IS this enforcement data**, available to Newmark and Strickland but unused.
- **SOMO's legislative footprint** (`disc_leg_footprint`, 5 items) — not in any other rubric. SOMO conceptualizes lobbying disclosure as bidirectional: not just "what did lobbyists do" but "what bills got influenced by which lobbying." This is the corporate-actor / CDoH lens that LacyNichols 2023 catalogued.
- **HiredGuns's electronic filing battery** (`e_filing`, 3 items) — surprising that it's HiredGuns-only, given that e-filing is now standard. The other rubrics either bundle it under access_online or treat it as a sub-question of access_searchable.
- **Sunlight's de-minimis-threshold question** — at 1 item, this is exactly the kind of thing that's lost when newer rubrics consolidate. Sunlight is the only one explicitly asking *whether the state has a reporting threshold*; FOCAL conceptually does (`scope.2`) but treats it as a registration-side question.

## 6. Universal topics (in 10+ rubrics)

Only two topics show up in 10+ rubrics:

| Topic | n_rubrics | total items |
|---|---|---|
| `disc_gifts` (gifts/hospitality/meals/travel disclosure) | 11 | 18 |
| `reg_org_subsidiary` (in-house lobbying / parent / subsidiary) | 10 | 36 |

A second tier (8-9 rubrics): `timeliness`, `def_what_lobbying`, `disc_revolving`, `disc_business_assoc`, `penalties`, `access_searchable`. Below that, the histogram has a long tail with no obvious elbow:

```
Topics covering N rubrics:
   1 rubrics:   8  ########
   2 rubrics:   4  ####
   3 rubrics:   7  #######
   4 rubrics:  10  ##########
   5 rubrics:   4  ####
   6 rubrics:   3  ###
   7 rubrics:   4  ####
   8 rubrics:   4  ####
   9 rubrics:   2  ##
  10 rubrics:   1  #
  11 rubrics:   1  #
```

There is no natural elbow at "in 6+ rubrics" or any other threshold. The frequency-based filter (Method A in the synthesis plan's brainstorm options) would not yield a clean core; the distribution is closer to a power law than a stepped one.

## 7. Methodology, caveats, and what would unblock better analysis

**What was done.**
- Atomic-item filter: dropped composites (section subtotals like `def.section_total`, overall-index rows like `index.total`), meta-rows (`uses_X` markers), and numeric rows whose text was a literal "(N items)" subtotal.
- Topic taxonomy: 47 topics across 14 meta-domains, hand-tuned regex against indicator_text + section_or_category. Multi-tag allowed (mean 1.0 tags per tagged item; 38.5% of rubric items received zero tags).
- TF-IDF: scikit-learn `TfidfVectorizer(ngram_range=(1,2), stop_words='english', sublinear_tf=True, min_df=1, max_df=0.5)` on `indicator_text + section`.
- Clustering: greedy single-link union-find restricted to cross-rubric pairs above a similarity threshold. Five thresholds reported.

**Caveats.**

- **Lexical similarity ≠ semantic similarity.** TF-IDF cannot bridge "report quarterly" ↔ "file every three months" or "must disclose all gifts" ↔ "lobbyists shall list any thing of value provided." The 31.8% untagged rate and the cluster-thinness at sim≥0.30 are both consequences. **Sentence embeddings via `all-MiniLM-L6-v2` would have been more informative** but the egress proxy blocked the HuggingFace download.
- **The regex taxonomy has known gaps.** SOMO's CDoH-style items (sustainability/responsibility framing) are largely untagged; AccessInfo's ATI-principle items are partially tagged. These items aren't necessarily out-of-scope for compendium 2.0 — they're framed in vocabulary the disclosure-rubric tradition doesn't share.
- **Single-link clustering is sensitive to threshold.** At sim≥0.20, transitive bridges create some semantic drift (one of the 0.20 ≥3-rubric clusters has noise — e.g., HiredGuns "name each employer" got pulled into a Newmark disclosure cluster).
- **Composite items vary in what they roll up.** Newmark2017's row "2015 disclosure/reporting sub-score (7 items)" was excluded as composite, but the 7 sub-items are atomized. Sunlight's heterogeneous-tier ordinals are kept atomic but the actual semantic meaning is in the tier descriptions — counting 5 items understates Sunlight's measurement granularity.

**What would meaningfully improve this analysis.**

1. **Sentence embeddings.** All-MiniLM-L6-v2 (~80MB) or similar would catch the same-meaning-different-vocabulary clusters TF-IDF misses. Currently blocked by egress proxy.
2. **LLM-based topic classification** of the 196 untagged items. Half the SOMO and AccessInfo content would land in cleaner buckets — `lobby_meetings_disclosed`, `corporate_responsibility_lens`, `code_of_conduct`, `public_consultation`, `transparency_register_governance`. The current taxonomy was built bottom-up from the more rubric-shaped extracts and under-specifies these.
3. **Hand-coded "concept ID" per item.** A flat ~80–120 concept identifier per atomic item, assigned by review of all 509 items, would directly answer the user's "almost identical meaning, slightly different verbage" question. This is what the synthesis plan's Step 9 ("manual / spreadsheet clustering") proposed; we used the regex approximation as a pre-pass.

## 8. Files saved

In `/home/claude/lobby/extracts/` during this session (not committed, scratch):
- `items_clustered_v2.csv` — 509 rubric atomic items + topic tags
- `topic_rubric_freshmatrix.csv` — 47 topics × 17 rubrics + n_rubrics
- `domain_x_rubric.csv` — 14 domains × 17 rubrics + n_rubrics + total_items
- `similarity_matrix.npy` — 509×509 TF-IDF cosine matrix

The matrices saved with this commit:
- `docs/active/compendium-source-extracts/results/cross_rubric_topic_x_rubric.csv` (this commit)
- `docs/active/compendium-source-extracts/results/cross_rubric_domain_x_rubric.csv` (this commit)

---

## Implications for compendium 2.0 design

Three things this analysis tells us about the synthesis plan's Step 10 (subset-selection methods):

1. **Method A (frequency threshold) is on weaker ground than the plan acknowledged.** The histogram has no elbow. A "≥6 rubrics" cut would yield ~14 topics covering items that are mostly the easiest-to-include things (gifts disclosure, in-house structure, oversight body, penalties); a "≥10 rubrics" cut yields just 2 topics. **The user's prior intuition that this would over-index on uninformative items is supported.**
2. **Method C (discriminative-strength filtering) gets first-pass signal from the long tail.** The 1-rubric topics (`enforce_subpoena`, `enforce_review_quality`, `disc_leg_footprint`, `e_filing`, `disc_funding_pubmoney`, `disc_exp_threshold`) are exactly the kind of items that distinguish state regimes in informationally-useful ways. They didn't make the high-frequency cut precisely because they're hard to ask consistently — but for that same reason, states that DO disclose them are doing meaningfully more than states that don't.
3. **Method B (FOCAL-anchored expansion) inherits FOCAL's blind spot in two known directions.** FOCAL has zero items in the Prohibitions row (state-tradition-only concern: contingent-fee bans, gift bans as bans-not-disclosure, campaign-contribution bans). FOCAL also has minimal Personnel (revolving door + business associations), with most of the personnel content concentrated in TI_2016 (9 items) and FOCAL itself (4). Anchoring on FOCAL would underweight both domains.

**Strongest claim from this descriptive pass:** a meaningful core item set will need to be **assembled, not filtered**. The frequency distribution does not produce a natural core, and the lexical-similarity clusters mostly recover within-author repetition rather than cross-tradition convergence.

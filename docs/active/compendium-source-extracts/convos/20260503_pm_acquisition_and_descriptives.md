# 2026-05-03 (pm cont'd) — Blue Book / BoS / COGEL acquisition mapping + cross-rubric descriptive stats

**Branch:** `compendium-source-extracts`
**Status:** Closed (acquisition findings + descriptive stats docs shipped; commit pending)
**Originating plan:** Plan Step 4 of [`plans/20260504_compendium_2_0_synthesis.md`](../plans/20260504_compendium_2_0_synthesis.md), invoked early after a direct user request
**Originating convo:** [`convos/20260503_per_paper_extraction_execution.md`](20260503_per_paper_extraction_execution.md) (immediate predecessor in the same calendar day)

## Summary

Same-day continuation. The user picked up after the morning's plan was written and asked Claude to (a) attempt acquisition of all three reference works named in Plan Step 4 (CSG Blue Book, CSG *Book of the States*, COGEL Blue Book), with explicit de-prioritization of post-2005 BoS and explicit interest in COGEL Blue Book content for comparison against Strickland 2014's extension methodology, and (b) produce cross-rubric descriptive statistics across the 26 source-paper extracts shipped earlier in the day, motivated by a hypothesis that "items have almost identical meaning but slightly different verbage" across rubrics.

Headline outcome: the three "Blue Books" collapse to two publications (CSG Blue Book = COGEL Blue Book, joint-published series); cell-level content remains unrecoverable from this environment but the structural picture is now well-mapped; and the user's paraphrase-variant hypothesis is partially confirmed but scopes much narrower than implicit, with cross-rubric near-duplicates clustering primarily within author-family or geographic tradition rather than across the full 17-rubric corpus.

## Topics Explored

- **Bibliographic verification of the three reference works.** WorldCat, Stanford SearchWorks, HathiTrust catalog, COGEL CDN. Established that the CSG and COGEL Blue Books are the same series. Established the Phase-1 → Phase-2 format split around 1996/1997 (comprehensive volume → thematic annual Updates).
- **Recovery of the 1990 8th edition Lobby Laws Tables of Contents** from HathiTrust catalog snippets — Tables 28-32 named explicitly.
- **2024 Ethics Update fetched as format-comparator** — confirmed Phase-2 format is self-reported ethics-agency narratives, not state-comparative tables.
- **Strickland 2014 methodology re-read** from `items_Strickland.md`. Strickland uses Newmark 2005's 18 items unchanged, extends 1988-2003 via biennial COGEL/BoS, 2004-2013 via State Capital Handbook, never reads statutes. Decomposition into Definitions/Prohibitions/Reporting sub-scales is a regression-specification choice, not an item-level change.
- **Atomic-item filtering** of 26 TSVs → 661 items (509 rubric / 152 non-rubric).
- **Topic taxonomy** of 47 topics across 14 meta-domains, regex-tagged. Mean tags per item = 1.0; 38.5% of rubric items received zero tags (concentrated in SOMO + AccessInfo where items are framed in CDoH or general-ATI vocabulary).
- **TF-IDF clustering** at 5 thresholds (0.20-0.50). Most clusters at sim≥0.30 are within author-family (Newmark2005↔Newmark2017, plus a few Opheim cross-bridges) or within European geographic cluster.
- **Sentence-embedding fallback attempted but blocked** by egress proxy at HuggingFace.
- **Long-tail diagnostic candidates identified** from the 1-rubric and 2-rubric topics (Opheim's enforcement battery, SOMO's legislative footprint, HiredGuns's e-filing battery, Sunlight's de-minimis-threshold question).

## Provisional Findings

(Detailed in the result docs; summary here.)

- CSG Blue Book = COGEL Blue Book = same publication series. Reduces three-target acquisition to two (Blue Book series + Book of the States) plus the commercial State Capital Handbook.
- The 1990 8th edition Lobby Laws section has 5 tables (28-32). Two are unused by the older state-rubric tradition: Table 31 (enforcement compliance) was Opheim's source for his 7 enforcement items, dropped by Newmark and inherited-as-dropped by Strickland; Table 32 (Education and Training) is unused by all three.
- The Phase-2 Lobbying Update (Gross, 1997–) is a legislation+litigation news series — different format from what Strickland used. The State Capital Handbook became necessary for Strickland's 2004-2013 extension precisely because the Phase-1 Blue Book lineage no longer existed in the same comparative-tables format.
- TF-IDF cross-rubric clustering at sim≥0.30: 20 clusters covering 49 items. 13 of 20 are Newmark2005↔Newmark2017 (same author). Only 1 cluster spans ≥3 rubrics. Across the 17-rubric corpus, paraphrase variants are mostly within-tradition; the European-rubric ↔ state-tradition-rubric vocabulary divide is sharp and not bridged by lexical similarity.
- Topic-frequency histogram has no natural elbow. Method A (frequency threshold) over-indexes on the most generic topics; the user's prior intuition is supported.
- Method B (FOCAL-anchored) carries explicit blind spots: zero Prohibitions items, minimal Personnel content. Anchoring on FOCAL would systematically underweight contingent-fee bans, gift bans, campaign-contribution bans, revolving-door cooling-off rules.
- Method C (discriminative-strength) gets first-pass signal from the long tail. The 1-rubric topics list (`enforce_subpoena`, `enforce_review_quality`, `disc_leg_footprint`, `e_filing`, `disc_funding_pubmoney`, `disc_exp_threshold`) is exactly the set of items the user previously identified as diagnostically strong.
- **Strongest claim from this descriptive pass**: a meaningful core item set will need to be assembled, not filtered. Frequency does not produce a natural core; lexical clustering recovers within-author repetition rather than cross-tradition convergence.

## Decisions

| topic | decision |
|---|---|
| Acquisition path priority | Adam Newmark email is highest expected value per unit effort. ILL on HathiTrust 1990 8th edition is the most direct cell-level path. Used-copy purchase eBay/AbeBooks is the cheapest. Defer State Capital Handbook unless project has the subscription budget |
| Book of the States | De-prioritized per user; revisit only if Blue Book path delivers and operational thresholds are the binding gap |
| Method A | Documented as on weaker ground than the synthesis plan acknowledged; histogram has no natural elbow; not to be applied alone |
| Method C | Strengthened by the long-tail finding |
| Method B | Carries explicit blind spots (Prohibitions, Personnel); needs a structural-anchor parallel run from another rubric to mitigate |
| Sentence-embedding fallback | Blocked by egress proxy; flagged as "what would unblock better analysis" in the descriptive doc; recommended for next session via either a model already in the repo or a pre-downloaded HF cache |
| Compendium 2.0 design plan | Still deferred per the synthesis plan; inputs are sharper but the design itself is not in scope this session |

## Mistakes recorded

For honesty + future-session context:

1. **Same user message arrived twice.** Likely an artifact of conversation compaction at the resume point. Treated the second instance as a continuation rather than a re-initialization. No content harm but worth noting for future sessions where compaction-replay artifacts may surface.
2. **Initial topic taxonomy over-fired** because the regex matched bare `issues?` for `bills_subjects`, and several other topics had similarly loose patterns. Caught on first inspection (290 items in `bills_subjects` was a clear over-tag); tightened the taxonomy and rerun produced clean coverage. Documented in the descriptive doc's methodology section. The pattern of "build-tag-audit-tighten" is reusable — future sessions doing similar regex-based topic classification should plan for at least one inspection pass.
3. **HathiTrust public-domain content not retrievable from this environment.** `babel.hathitrust.org` returns 403 even on `mdp.39015077214750` (1990 8th ed., public-domain Google-digitized). Combination of egress proxy + no institutional auth. Recovered structural information from search-engine snippets but no cell-level content. Future sessions wanting Blue Book content will need ILL or an institutional-credentialed environment.
4. **`cdn.ymaws.com` is accessible via `web_fetch` but blocked from bash.** Worth recording for future-session efficiency: the Anthropic egress proxy used by `web_fetch` is more permissive than the bash-tool egress proxy. URL-pattern probing for older COGEL editions did not find files (CDN URLs likely have unique tokens, not predictable filename patterns), so brute-force probing isn't a viable acquisition strategy.

## Goal of this session

Execute Plan Step 4 (Blue Book / BoS / COGEL acquisition mapping) early, plus the descriptive-stats pass, and surface findings for user review.

Outcome: Acquisition options mapped (with realistic effort/yield estimates per path); cross-rubric descriptive stats shipped; the synthesis plan's brainstormed Methods A/B/C/D have sharper input data, particularly that Method A is on weaker ground than the plan acknowledged.

## Next steps

- User reviews the two result docs.
- User picks acquisition path(s) to pursue. Adam Newmark email recommended as highest-yield; ILL or used-copy purchase as alternatives.
- If sentence embeddings become available (proxy whitelist, pre-cached model in repo, or a model from the repo's tooling layer), re-run the cross-rubric clustering pass — current TF-IDF result understates semantic equivalence across European-tradition ↔ state-tradition rubrics.
- Compendium 2.0 design plan remains deferred per the synthesis plan. The descriptive evidence sharpens the input but doesn't change the deferral.

## Results

- [`results/20260503_blue_book_bos_cogel_acquisition.md`](../results/20260503_blue_book_bos_cogel_acquisition.md)
- [`results/20260503_cross_rubric_descriptive.md`](../results/20260503_cross_rubric_descriptive.md)
- [`results/cross_rubric_topic_x_rubric.csv`](../results/cross_rubric_topic_x_rubric.csv) — 47 topics × 17 rubrics + n_rubrics
- [`results/cross_rubric_domain_x_rubric.csv`](../results/cross_rubric_domain_x_rubric.csv) — 14 domains × 17 rubrics + n_rubrics + total_items
- [`results/cross_rubric_items_clustered.csv`](../results/cross_rubric_items_clustered.csv) — 509 rubric atomic items × topic tags

## Plan produced

None. This session executed an early portion of the existing [`plans/20260504_compendium_2_0_synthesis.md`](../plans/20260504_compendium_2_0_synthesis.md) and surfaced findings that sharpen its Method A/B/C/D brainstorm without producing a new plan.

---

## Post-session continuation (2026-05-06)

The 2026-05-03 work landed (commit `a857965c`). Session resumed 2026-05-06 with two minor follow-ups that didn't justify their own convo:

1. **HathiTrust path documented inline.** Catalog record at `https://catalog.hathitrust.org/Record/002470321`; 1990 8th edition direct link `https://babel.hathitrust.org/cgi/pt?id=mdp.39015077214750` (HathiTrust ID `mdp.39015077214750`); page-structure shortcuts (Section 7 / scan #121 for Lobby Laws Tables 28-32). Browser access is gated by HathiTrust-member institutional auth; user has the path documented for personal-machine retrieval.

2. **Sentence-embedding script committed at `tools/embed_cross_rubric.py`** (commit `4eed8f5f`). Purpose: enable the cross-rubric clustering re-run with semantic embeddings that the 2026-05-03 sandboxed env couldn't do (egress proxy excludes `huggingface.co`). Default model `all-MiniLM-L6-v2` (~80MB, 384-dim, fast on CPU). Reads `docs/active/compendium-source-extracts/results/cross_rubric_items_clustered.csv` (the 509-item rubric atomic-items file from 2026-05-03), writes three artifacts: `embed_similarity_matrix.npy` (NxN cosine-sim), `embed_clusters_at_thresholds.csv` (summary stats), `embed_clusters_full.txt` (cluster contents). Designed to run from a local machine; `pip install sentence-transformers pandas numpy` then `python tools/embed_cross_rubric.py`.

   **Threshold guidance** (sentence-embedding cosine-sim is not directly comparable to TF-IDF cosine-sim): 0.30 ~ noise; 0.50 ~ probably-same-concept (default starting threshold); 0.70 ~ near-paraphrase; 0.85 ~ essentially-identical-wording. The script defaults to `0.50,0.60,0.70,0.80`.

   **Predictions to falsify** (script docstring also lists these for the next agent):
   - Does the European<->state-tradition vocabulary divide bridge under semantic embeddings? TF-IDF caught only 1 cross-tradition cluster spanning >=3 rubrics ("lobbyist definition," and only because the literal word "lobbyist" appeared in all five). Embeddings should produce more.
   - Does the "expenditures benefiting public officials" concept consolidate? Currently scattered across Opheim / FOCAL / Newmark / HiredGuns / Sunlight in non-overlapping vocabulary; TF-IDF caught Newmark<->Opheim<->FOCAL but missed HiredGuns and Sunlight.
   - Does the meeting-log family form? SOMO `disc_leg_footprint`, IBAC ministerial-diary, AccessInfo "duty to keep a true and detailed record of meetings", CouncilEurope "Recorded contacts", FOCAL contact-log category, TI_2016 "Lobby meeting record" — same concept, near-zero lexical overlap.

   **If MiniLM does NOT bridge these, that itself is a finding** — would mean the vocabulary divide reflects genuinely different conceptual decompositions, not just different words for the same thing. Either way, worth recording into a follow-up results doc next session.

## Handoff to next agent (desktop)

**Branch:** `compendium-source-extracts`. HEAD as of this writing: `4eed8f5f`. 6 commits ahead of `main`. Multi-committer rules apply (pull-before-push; never force-push; never merge to main without explicit user ask).

**Pre-flight reading order for the next agent:**
1. `CLAUDE.md` (worktree root)
2. `STATUS.md` (note the top-of-file PRI-out-of-bounds block — non-negotiable)
3. `README.md`
4. `docs/active/compendium-source-extracts/RESEARCH_LOG.md`
5. `docs/active/compendium-source-extracts/convos/20260503_per_paper_extraction_execution.md`
6. This convo (`20260503_pm_acquisition_and_descriptives.md`) — particularly the **Post-session continuation** block above for the local-execution context
7. `docs/active/compendium-source-extracts/plans/20260504_compendium_2_0_synthesis.md`
8. `docs/active/compendium-source-extracts/results/20260503_blue_book_bos_cogel_acquisition.md`
9. `docs/active/compendium-source-extracts/results/20260503_cross_rubric_descriptive.md`
10. `tools/embed_cross_rubric.py` (the script's docstring summarizes the predictions)

**What's runnable locally without further setup:**
- `python tools/embed_cross_rubric.py` — produces three local outputs (similarity matrix, threshold summary, cluster dump). Should run in 30-60 seconds on CPU after the one-time MiniLM download.

**What the user has decided NOT to do this round:**
- Acquire State Capital Handbook (commercial-only, ~$200/yr; deferred indefinitely unless project subscription budget materializes).
- Acquire Book of the States 2005 (item labels already in `items_Newmark2005.tsv`/`items_Opheim.tsv`; revisit only if Blue Book path delivers and operational thresholds become the binding gap).

**What the user has flagged as runnable from their personal machine:**
- HathiTrust 1990 8th edition reader (catalog record above) — they have the path documented; institutional auth dependent.
- The embedding script (committed today).

**Open questions for the next agent to confirm at session start:**
1. Did the local sentence-embedding run produce useful cross-tradition bridges? (Predictions in the script docstring.) If yes, integrate into a follow-up results doc; if no, that null result is itself worth a short addendum to `20260503_cross_rubric_descriptive.md`.
2. Has the user retrieved any Blue Book content from HathiTrust personally? If yes, the next step is extracting Tables 28-32 cell content into TSV form following the 2026-05-03 extraction template (`paper_id`, `indicator_id`, `indicator_text`, `section_or_category`, `indicator_type`, `scoring_rule`, `source_quote`, `notes`) under `docs/active/compendium-source-extracts/results/items_CSG_BlueBook_1990.{tsv,md}`.
3. Has the Adam Newmark email gone out? (Task #10 / Task #11 of `plans/20260504_compendium_2_0_synthesis.md`.) If yes, check responses; if no, the user may want the next agent to draft a single combined ask covering Vaughan & Newmark 2008 retrieval + Blue Book/BoS questions.

**What is OUT of scope until compendium 2.0 lands:**
- Reading PRI 2010 in any form (the ⛔ block in STATUS.md).
- Reopening compendium 1.x or schema v1.1 for "fixes" (frozen pending v2.0).
- Iter-2 or further work on the `statute-extraction` harness (paused).

**Hot-take takeaway for the next agent in two sentences:** Frequency-based filtering will not produce a clean compendium 2.0 core (the histogram has no elbow), and lexical clustering only catches within-author paraphrasing, not cross-tradition convergence — so the immediate question the embedding pass tries to answer is whether SEMANTIC clustering can do the bridging that TF-IDF could not. If it can, the path forward is hybrid Method D (anchor + frequency + discriminative-strength). If it cannot, the project will need to confront that the European-tradition and state-tradition rubrics are measuring genuinely different things, not just expressing the same things differently.

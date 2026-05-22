# Research Log: phase-c-projection-tdd

Created: 2026-05-14
Purpose: Phase C successor branch (per Option B locked 2026-05-13). TDD-implements per-rubric projection functions `f_rubric(compendium_cells_for_state_year) → rubric_score` in the **locked rubric order**:

1. **CPI 2015 C11** (smallest concrete target; 21 rows in v2 mapping; 14 atomic items from `PublicI/state-integrity-data/2015/criteria.xlsx`)
2. **PRI 2010** (69 rows in v2 mapping; ~52 NEW vs v1.2; sub-aggregate rollup rule already paper-derived in archived `pri-calibration`)
3. **Sunlight 2015** (13 rows in v2 mapping; 11 cross-rubric; three locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation)
4. **Newmark 2017** (14 rows; 8 reused, 6 new; load-bearing r=0.04 CPI↔PRI-disclosure correlation factually-audited 2026-05-13)
5. **Newmark 2005** (14 rows; **100% reuse** of Newmark 2017 mappings; 2005 mapping falsified the 2017 mapping's `contributions_from_others` parallel speculation)
6. **Opheim 1991** (14 row families / 15 in-scope items; **100% reuse**; β AND-projection 2nd concrete use; 1 catch-all un-projectable)
7. **HG 2007** (38 rows; 16 reused, 22 new; 42% reuse; ground-truth retrieval is a `oh-statute-retrieval` sub-task — depend on its output)
8. **FOCAL 2024** (58 rows post-FOCAL-1 / 22 reused, 36 new; 37.9% reuse — lowest single-mapping rate; **L-N 2025 Suppl File 1 weights** — 1,372-cell ground truth; US LDA 81/182 = 45%)

**LobbyView 2018/2025 is NOT in scope for Phase C** — it's a schema-coverage check (Federal_US LDA disclosure-observable coverage 14/18 = 78%), not a score-projection. Already documented as Phase B mapping #9; no projection function to implement.

> **Predecessor:** Cut off `main` at `8bfc225` post-archive of `compendium-source-extracts` (merged 2026-05-14 as `cac1469`; archived to `docs/historical/compendium-source-extracts/`).
>
> **Row-freeze contract:** [`compendium/disclosure_side_compendium_items_v2.tsv`](../../../compendium/disclosure_side_compendium_items_v2.tsv) — 181 rows. Promoted from `docs/historical/...` to repo-level `compendium/` on 2026-05-14 by the `compendium-v2-promote` branch (live contract for the two parallel-running successors; v1 artifacts retained at `compendium/_deprecated/v1/`). Load via `from lobby_analysis.compendium_loader import load_v2_compendium` (returns raw `list[dict[str, str]]`). Decision log at [`20260513_row_freeze_decisions.md`](../../historical/compendium-source-extracts/results/projections/20260513_row_freeze_decisions.md). (Path is live on main after `compendium-v2-promote` merges; until then read via the worktree-local view.)
>
> **Compendium 2.0 success criterion:** see the ⭐ section in [`../../../STATUS.md`](../../../STATUS.md). This branch is direct work on criterion #4 (per-rubric projections as sanity checks on extraction accuracy).
>
> **Per-rubric projection mapping docs (Phase B output):** [`docs/historical/compendium-source-extracts/results/projections/`](../../historical/compendium-source-extracts/results/projections/) — one `<rubric>_projection_mapping.md` per rubric documents the column-by-column projection logic. Each TDD session can use the matching projection-mapping doc as its spec.
>
> **Factual-audit verdict (2026-05-13, pre-merge):** Newmark 2017's r=0.04 CPI↔PRI-disclosure correlation (load-bearing for unification rationale) verified exactly at paper p.421-422. PRI 2010's dense numerical claims (sub-component max counts A:11 + B:4 + C:1 + D:1 + E:20 = 37; B1/B2 reverse-scoring per footnotes 85/86; E rubric "higher of E1/E2 + F/G double-count + separate J") all confirmed exactly. FOCAL had 1 correction landed (contact-log 13/15 restored) + 1 clarity tightening (openness 11/15 vs open-data sub-theme 9/15). **Phase C agents can trust the projection-arithmetic values in these summaries.** One outstanding sourcing nit on Newmark 2017's parenthetical "0.71" comparator: it's sourced from Newmark 2005 (separate paper), not the 2017 PDF — extract from `papers/text/Newmark_2005__lobbying_regulation_in_the_states.txt` if needed.

## Out of scope for this branch

- Multi-vintage OH statute retrieval — that lives on `oh-statute-retrieval` (Track A; Phase C HG 2007 projection depends on Track A's ground-truth retrieval sub-task).
- Designing the extraction harness — that lives on `extraction-harness-brainstorm` (Track B). Phase C projections operate on hypothetically-correct `compendium_cells`; the extraction pipeline that populates those cells is Track B's concern.
- LobbyView score-projection — LobbyView is schema-coverage only.

## Data symlink note

The `data/` symlink convention from `skills/use-worktree/SKILL.md` was **skipped at branch creation** because (a) `data/` is now fully gitignored post-2026-05-14 rename (`data/compendium/` → repo-root `compendium/`) so the prior conflict is resolved but (b) on this machine no gitignored data under `data/` actually exists yet to share. Projection functions are pure code over compendium-keyed cells + tracked rubric ground-truth CSVs — likely no gitignored data needed at all for this branch.

---

## Sessions

(Newest first.)

### 2026-05-22 — FOCAL 2024 legal-core TDD continued: financials + scope batteries + ground-truth loader shipped (15 of 26 + loader; legal-core sub-plan complete)

Convo: [`convos/20260522_focal_2024_legal_core_continued.md`](convos/20260522_focal_2024_legal_core_continued.md)
Plan: [`plans/20260518_focal_2024_legal_core_plan.md`](plans/20260518_focal_2024_legal_core_plan.md)

Closed out the FOCAL legal-core sub-plan. Shipped financials (11 items including the AND-3-tier `financials.6` helper and the imported-from-newmark_2017 `financials.10` rescale), scope (4 items via named helpers `_project_focal_scope_1` through `_project_focal_scope_4`), and the per-country ground-truth loader stub against `focal_2025_lacy_nichols_per_country_scores.csv`. Two commits, 112 new tests (74 per-item + 38 ground-truth), full projections suite 718 → 830 + 3 xfailed (Plan-4-deferred per-country aggregates). Ruff clean throughout.

**Topics explored**

- Financials.6 AND-3-tier helper shipped with **UNABLE-on-unknown** semantics rather than the plan's `bool()`-coerce-None pseudocode. Matches `relationships.1`'s principled OR convention from the prior session; silent-coerce would hide extraction holes.
- Financials.10 imports `project_gifts_actor_agnostic_or` from `newmark_2017` and rescales 0/1 → 0/2 for FOCAL's per-item granularity. Coupling-test regression-guards drift in newmark's helper.
- Scope.4's spec-doc P/N labels ("limited to influencing legislative changes" / "{face_to_face} only") don't atomize onto the 8-enum `Set[enum]` cell content. Projected parallel to scope.1's set-membership shape (full → 2, non-empty proper subset → 1, empty → 0); documented as known divergence. US LDA scope.4 = 2 sanity-checks the convention against the published anchor.
- Scope.3 staff-AND vs major-branch precedence: known-FALSE major branch → 0 regardless of staff; all-major-branches TRUE + both staff TRUE → 2 (OQ2 strict); all-major TRUE + any staff FALSE → 1. UNABLE only when an axis is ambiguous between 2 and 1 or between {2,1} and 0.
- Loader CSV missing-value flavors: 40 `"NA"` cells (L-N "not_assessable", concentrated on non-US scope/openness) + 15 empty cells (parliamentary `timeliness.2` in non-parliamentary jurisdictions) both collapse to `None` in the loader output. Downstream aggregation excludes from numerator AND denominator identically.
- Indicator-ID convention: loader returns bare IDs (`"financials.1"`); callers add `focal_2024.` prefix for dispatcher comparison. Keeps the loader as a pure CSV reader.

**Provisional findings**

- **US Federal LDA legal-core raw sum = 23** across the 27 legal-core indicators. Verified verbatim against L-N 2025 Suppl Table 5 via 27 parametrized per-indicator tests.
- **OQ1 cutoffs ($1000 / 5%) hold against US LDA validation.** LDA has $3000 comp + 20% time → both above cutoffs → significant=True → scope.2 = 0, matching published.
- **No new spec-doc-vs-v2 renames discovered.** All row IDs for the 15 newly-implemented items were present in v2 TSV at session start.
- **Module's compound-helper surface now consolidated** via `_COMPOUND_DISPATCH` dict (7 entries: `relationships.1`, `financials.6`, `financials.10`, `scope.1`-`scope.4`). Companion plans extend by adding entries; cleaner than the prior inline-if dispatch.

**Decisions made**

- `_project_binary_and_3tier` ships with UNABLE-on-unknown (diverges from plan pseudocode, matches project convention).
- `_COMPOUND_DISPATCH` dict replaces inline if-chain in `project_focal_2024_item`.
- Scope.4 set-membership semantics diverge from spec doc P/N labels (documented).
- Loader returns `int | None` and bare indicator IDs (no module prefix).
- `FOCAL_2024_LEGAL_CORE_INDICATORS` exported as a public frozenset for companion-plan + Plan-4 introspection.

**Next steps**

- **Plan 2 (FOCAL contact_log):** 11 items. Read [`plans/20260518_focal_2024_contact_log_plan.md`](plans/20260518_focal_2024_contact_log_plan.md) at next session start.
- **Plan 3 (FOCAL openness + timeliness):** 12 items; practical-axis read pattern. Loader already loads these rows but `FOCAL_2024_LEGAL_CORE_INDICATORS` excludes them.
- **Plan 4 (FOCAL aggregation):** top-level projector + US LDA federal-validation harness + cross-rubric harness for US states. Closing plan for FOCAL.

Convo for the next session: `20260523_focal_2024_contact_log.md` (or similar — per-sub-plan granularity preserved per the legal-core plan's "Closing the loop").

---

### 2026-05-21 — FOCAL 2024 legal-core TDD: descriptors + revolving_door + relationships shipped (12 of 26 items)

Convo: [`convos/20260521_focal_2024_legal_core_tdd.md`](convos/20260521_focal_2024_legal_core_tdd.md)
Plan: [`plans/20260518_focal_2024_legal_core_plan.md`](plans/20260518_focal_2024_legal_core_plan.md)

Continued from earlier-same-day HG-deferral session. Started FOCAL 2024 implementation per the `legal_core` plan. Shipped descriptors (6 items, single-row binary + typed-IS-NOT-NULL), revolving_door (1 item), and relationships (4 binary + 1 vintage-gated `relationships.0`). Two commits, 42 per-item tests, full projections suite 676 → 718 (+42; ruff clean throughout).

**Topics explored**

- Phase-0 cross-check against the live v2 TSV: 35 legal-core row IDs verified present (no spec-doc-vs-v2 drift).
- L-N 2025 CSV inspection for the Federal US LDA validation anchor: weighted sum 81, max 182, raw sum 42; matches the plan's 81/180 = 45% target after revolving_door.2 exclusion.
- Cross-national vs US-state framing: surfaced explicitly mid-session that FOCAL was published as a cross-national framework (28 jurisdictions national-level); the CSV's "United States" row is the **federal LDA**, not any US state. No per-state FOCAL ground truth exists in the world. State-level validation will run via cross-rubric agreement (Plan 4).
- Newmark 2017 module re-read to confirm the dispatcher pattern + helper signatures. FOCAL's 2-tier (0/2) binary reads, vintage gating, and OR-helper are extensions to that shape.
- Permission-rule investigation: `uv run pytest` is the MEMORY-noted footgun (loads main's editable install in worktrees); workaround `.venv/bin/python -m pytest` triggers prompts because `Bash(python *)` is prefix-matched and doesn't cover the path-prefixed invocation. Dan added `Bash(.venv/bin/python *)` to the permission list.

**Provisional findings**

- **17th rename baked in (relationships.0)**: the plan's working name `relationships.lobbyist_list_2025` doesn't match L-N's published ID. The CSV uses `relationships.0` with `focal_2024_indicator_id_map = "(new in 2025)"`. Module docstring lists this as rename #17 alongside the 16 from the plan.
- **Vintage gate semantics**: scope-mismatch raises KeyError, not UNABLE. UNABLE is reserved for data-missing; treating "this item isn't in vintage scope" as data-missing would silently mask aggregator iteration bugs.
- **OR-helper is module-internal and generic** (`_project_binary_or_2tier(cells, row_ids)`); will be reused for financials.10 via the import-from-newmark path the plan recommends.

**Decisions carried forward**

- All 5 OQ defaults from the legal-core plan (scope.2 cutoffs $1000/5%, scope.3 staff AND-strict, descriptors/relationships.4 partly-tier YAGNI, per-battery subtotals informational only) are in force for subsequent sessions.
- Sentinel + 2-tier binary return + `_MIN_VINTAGE`-gated KeyError pattern are settled; later batteries inherit.

**Next steps**

- Continue FOCAL legal-core: financials battery (11 items, biggest remaining), scope battery (4 items, all named helpers including the typed Set[enum] reads for scope.1/scope.4), ground-truth loader stub. After legal-core lands, Plan 2 (contact_log, 11 items) is next.
- Convo for the continuation session: `20260522_focal_2024_legal_core_continued.md` (per-sub-plan granularity; overarching `focal_2024_tdd.md` lands at Plan 4 completion per the plan's "Closing the loop").

---

### 2026-05-21 — HG vintage finding + deferral; FOCAL is next

Convo: [`convos/20260521_hg_vintage_finding_and_deferral.md`](convos/20260521_hg_vintage_finding_and_deferral.md)
Results: [`results/20260521_hg_vintage_correction.md`](results/20260521_hg_vintage_correction.md)

User picked HG 2007 as next implementation. Per the plan's retrieval-gate, started a Path A scorecard retrieval attempt. The attempt surfaced that **the CPI "Hired Guns" rubric is a May 2003 survey, not a 2007 one** — no second survey was ever conducted. Wayback evidence (2008 + 2010 captures both titled "Lobby Disclosure Ranking 2003"), CPI's own archives roll-up (no Dec 2007 ranking article), and user's domain knowledge (CPI uses "Hired Guns" as a persistent topic tag, not a survey name) all converged. L-N 2024/2025's "2007" attribution is a grad-student misread of CPI's modern page metadata, propagated through three independent academic citations.

**Topics explored**

- Pre-flight status reconstructed: 5 of 8 rubrics shipped, HG + FOCAL outstanding, Opheim blocked.
- HG retrieval-gate Path A attempt — wayback CDX scan of `projects.publicintegrity.org/hiredguns/*` showed ~200 captures spanning 2008-2010, all under "Lobby Disclosure Ranking 2003" framing.
- Per-state per-question scorecard pages exist on wayback (50 states × `nationwide.aspx?st=XX&display=DRStateNumbers`, 2010-07-06 captures) — Path A 1,900-cell ground truth is retrievable in principle.
- Cross-source vintage triangulation: wayback page titles, CPI archives roll-up dates, methodology PDF metadata (Firefox print, uninformative), L-N 2024/2025 bibliography refs.
- Justia historical-coverage probe — Cloudflare TLS-fingerprint blocked curl + WebFetch from both residential Comcast egress and Anthropic egress. User probed manually from a browser; 13-state sample: 2 at 2003 (FL, WA), 9 at 2005-2006, 2 at 2010+.

**Provisional findings**

- **HG vintage = 2003** (statute data late-2002 / early-2003; CPI publication May 15, 2003). The "Q35-Q37 at 2002" detail from `items_HiredGuns.md §6` becomes coherent — prior-year agency self-report in an early-2003 survey, not mixed-vintage drift.
- **L-N 2024/2025 carries a bibliographic citation error** on HG vintage. Three independent papers cite the methodology as 2007 via the modern `methodology-5/` URL accessed Jan 22, 2024. CPI's tag-vs-survey distinction (clarified by user) is the root cause: methodology page bears a "last updated 2007" stamp (date of Dec 2007 commentary article), grad students copied it as the methodology date. Doesn't impeach L-N's FOCAL framework coding (already factual-audit-clean); does flag that L-N's citation-quality bar has gaps on non-load-bearing details.
- **Path A retrieval target is real and retrievable** but vintage-bound. Validation requires 2003-vintage statute snapshots feeding v2 cells. Today's cells reflect 2026 statutes; 23 years of statute drift would be measured as projection error.
- **Justia 2003 coverage is partial and state-specific.** If 13-state sample generalizes, ~7-8 of 50 states would be vintage-exact at 2003. Most are 2005-2006. CPI's own *States Outpace Congress* (Mar 2006) explicitly documents 24 states making disclosure changes between 2003 and 2006 — can't mix 2005-2006 Justia data into a 2003 validation set.

**Decisions made**

- **Defer HG implementation** on this branch. Joins Opheim 1991 as blocked-on-vintage. Mergeable rubric scope contracts 8 → 6: CPI 2015 C11, PRI 2010, Sunlight 2015, Newmark 2017, Newmark 2005, FOCAL 2024.
- **Defer the cross-cutting `CPI_2007_*` → `CPI_2003_*` rename.** Worth doing as a single sweep when HG implementation resumes alongside 2003-vintage retrieval; not worth touching archived `compendium-source-extracts/` material twice.
- **FOCAL 2024 is next implementation** on this branch. Plan-set already drafted: `legal_core` → `contact_log` → `openness_timeliness` → `aggregation`, all converging on single `focal_2024.py`. Start with `20260518_focal_2024_legal_core_plan.md`.
- **HG implementation captured as GH `task` issue** so the deferred-not-deleted state has a discoverable handle. Resurfaces when 2003-vintage retrieval becomes a research line.

**Next steps**

- Next session: read `plans/20260518_focal_2024_legal_core_plan.md`; TDD-implement FOCAL legal_core sub-module against `_ATOMIC_SPEC` declarative table; validate against L-N 2025 Suppl File 1's 1,372-cell weight matrix where legal-core-relevant cells are present. Honest counterfactual on FOCAL's partly-tier YAGNI collapse (binary 0/2 instead of partly-tier) — document over-scoring in module docstring.
- Future research line (not this branch): 50-state 2003-vintage statute retrieval. Combines Justia 2003 codes (~7-8 states), wayback state portal captures (variable), state law-library archives (uncertain). Unblocks HG + naming-correction sweep + potentially benefits Opheim if 1988-89 coverage extends.

---

### 2026-05-18 — Newmark 2017 + Newmark 2005 modules shipped

Convo: [`convos/20260518_newmark_modules_shipped.md`](convos/20260518_newmark_modules_shipped.md)

Following the same-day scope correction, shipped the deterministic Python for Newmark 2017 and Newmark 2005 in one session. Both modules use the `sunlight_2015.py` shape (frozen Pydantic score model + per-item helpers + dispatcher + top-level projector); zero LLM imports across both.

- `src/lobby_analysis/projections/newmark_2017.py` — 305 lines. 14 in-scope items (7 def + 7 disclosure); 5 `prohib.*` items excluded. Exposes `def_section_total` + `disclosure_section_total` (each 0–7) — these are publishable Table-2 sub-aggregates. No `index_total` (`prohib.*` excluded).
- `src/lobby_analysis/projections/newmark_2005.py` — 282 lines. 14 in-scope items (7 def + 1 freq + 6 disclosure); 4 `prohib_*` + 1 `penalty_stringency_2003` excluded. Imports `project_gifts_actor_agnostic_or` from `newmark_2017`. Introduces NEW `project_cadence_more_than_annual_or` helper (8-cell OR over sub-annual cadence cells; `_annual` / `_other` deliberately NOT read). Exposes only `per_item_scores` + `panel` label — NO sub-aggregate fields. Rationale: Newmark 2005 publishes only per-state totals (Table 1), not sub-aggregates; exposing them would smuggle an API claiming reproducibility against unpublished data.

**Regression-guarded:**
- No `index_total` API in either module (both rubrics' headlines require excluded items).
- No `prohib.*` / `prohib_*` / `penalty_stringency_2003` helpers (dispatcher raises `KeyError`).
- No-variation cells (Newmark 2017 `def.legislative_lobbying`, gifts OR) project per the cell value, not coerced.
- Falsified-2017-speculation in Newmark 2005: NO `contributions_from_others` item; the cell-with-True doesn't affect 2005's output.

**Tests:** 82 new (45 Newmark 2017 + 37 Newmark 2005), all passing. Full projections suite: 676 pass. Ruff clean.

**Renames applied** (from spec doc working-names → v2 row IDs): 7 inherited from Newmark 2017's row-freeze (3 typed-dollar long-form; 2 gifts `_report_` → `_spending_report_`; 1 `_by_client` → `_by_payer`; 1 contributions-received `_report_` → `_spending_report_`) + 8 cadence renames in Newmark 2005 (`*_report_cadence_*` → `*_spending_report_cadence_*`).

**Ground-truth deferred:** Newmark Tables 1 (2005) and 2 (2017) have not been extracted to CSV; per-state validation harness deferred until that extraction lands. Per-item helper tests + aggregation fixtures cover the projection logic in the meantime.

**Process notes:**
- `uv run pytest` in the worktree initially loaded the main repo's editable install (pre-existing footgun per MEMORY entry). Fixed by running through the worktree's venv directly (`<worktree>/.venv/bin/python -m pytest`). Also had to install `pytest` + `ruff` into the worktree's venv (they weren't synced).
- 3 pre-existing `tests/test_pipeline.py` failures verified unrelated (missing `data/portal_snapshots/CA/2026-04-13` — cross-machine data-sync lag; data only has `2026-05-01` locally). Not fixed per "data symlink is intentional" guidance.

**Next:** HG 2007 (Session B; 38 items, declarative `_ATOMIC_SPEC`), then FOCAL 2024 (Session C; 50 indicators weighted, L-N 2025 Suppl File 1 = 1,372-cell ground truth). After all 4 land + tests pass, branch is mergeable.

---

### 2026-05-18 — Scope correction: this branch ships deterministic Python, nothing more

Convo: [`convos/20260518_scope_correction.md`](convos/20260518_scope_correction.md)

The branch's scope is reset to its irreducible core: **ship deterministic Python that maps populated SMR cells → rubric scores**. No LLM in the loop, no headless launcher, no canary, no Sub-N multi-session orchestration. The 3 shipped modules (CPI 2015 C11, PRI 2010, Sunlight 2015) confirmed the shape — 0 LLM imports across all three; pure `csv` / `re` / `pathlib` / `typing` / `pydantic`.

**Trigger:** Sub-4 (this session) was set up to "build a headless `claude -p` launcher + run a Sunlight canary." User pushed back as the 4th-conversation-in-a-row evidence of plan inflation. Filesystem + git-history scan confirmed: no `newmark*.py` / `opheim*.py` / `hg*.py` / `focal*.py` projection module has ever existed on any branch, ever. Only CPI, PRI, Sunlight have shipped code.

**Retired:**

- `plans/20260514_headless_api_key_handoff.md` — the headless `claude -p` launcher idea (don't build it).
- The "Sub-0 / Sub-1 / Sub-2 / Sub-3 / Sub-4" multi-sub-session orchestration framing.
- The 7 Sub-0 conventions wrapped as ceremony — STOP clauses, "Phase 0 cross-check" rituals, per-helper RED/GREEN documentation requirements. CPI/PRI/Sunlight shipped without any of that overhead; match their shape.
- The 5 Sub-1/2/3 plans (~2,190 lines) as process scripture. **Content kept** as cell-mapping reference (which v2 rows feed which item; rename tables; ground-truth CSV paths); **process framing ignored**.

**Remaining work — for all 4 outstanding rubrics:** ship deterministic Python that turns a populated SMR into a rubric score.

- Newmark 2017
- Newmark 2005 (~100% reuse of 2017 mappings; near-twin with weak-inequality aggregation + imports from `newmark_2017`)
- HG 2007 (38 items, declarative `_ATOMIC_SPEC`)
- FOCAL 2024 (50 indicators × weighted aggregation; L-N 2025 Suppl File 1 ground truth)

Opheim 1991 stays blocked on 1988-89 statute data; not this branch's concern until Track A expands vintage scope.

**How:** open `sunlight_2015.py` as the template; open the matching Phase B mapping doc in `docs/historical/compendium-source-extracts/results/projections/` as the spec; write the module + tests; commit; move on. After all 4 ship + tests pass, branch is mergeable.

**Vocabulary fix going forward:** reserve "shipped" for code + tests merged; use "drafted" or "landed" for plan documents. The current ambiguous usage in convos (Sub-3's "Sub-2 Newmark plans shipped + pushed") compressed in cross-machine status memory to "Newmark shipped" and was the proximate cause of the scope-correction session.

---

### 2026-05-18 — Sub-3 Stream 3 plans: FOCAL 2024 plan-set (4 plans) + HG 2007 plan

Convo: [`convos/20260518_focal_hg_plans_drafting.md`](convos/20260518_focal_hg_plans_drafting.md)
Plans:
- [`plans/20260518_hg_2007_plan.md`](plans/20260518_hg_2007_plan.md) — ~500 lines
- [`plans/20260518_focal_2024_legal_core_plan.md`](plans/20260518_focal_2024_legal_core_plan.md) — ~470 lines
- [`plans/20260518_focal_2024_contact_log_plan.md`](plans/20260518_focal_2024_contact_log_plan.md) — ~320 lines
- [`plans/20260518_focal_2024_openness_timeliness_plan.md`](plans/20260518_focal_2024_openness_timeliness_plan.md) — ~390 lines
- [`plans/20260518_focal_2024_aggregation_plan.md`](plans/20260518_focal_2024_aggregation_plan.md) — ~510 lines

**Topics explored**

- Pre-flight: reconstructed Phase C state from `cacb65b` HEAD (Sub-2 Newmark plans shipped + pushed); read Sub-0's playbook gap audit + Sub-1's drafting conventions convo + Sub-2's drafting convo + the rubric implementation playbook + the FOCAL (938 lines) and HG (815 lines) spec docs end-to-end.
- **Phase 0 cross-check executed.** Ran `load_v2_compendium()` against 59 expected FOCAL rows + 49 expected HG rows + 6 PRI cadence binaries (Q12 input). Surfaced **23 spec-doc-vs-v2 renames** total (9 for HG, 17 for FOCAL); all resolved cleanly via TSV verification. Most renames inherit from Sub-1 + Sub-2 families; FOCAL adds a few of its own (set-typed cell prefix normalization, staff-cell v2 split).
- **HG plan drafted** with retrieval-gate dual-path validation — Path A (Strong, 1,900-cell ground truth if CPI's 2007 scorecard retrievable) vs Path B (Weak-inequality `our_partial ≤ published_total - 17` if not). 38 in-scope items via declarative `_ATOMIC_SPEC` + 9 named helpers. Q12 cadence-derived projection; Q15+Q16-Q19 conditional cascade; Q23/Q24 partial-scope projection. **Retrieval is NOT a Track A task** — correction to the spec doc's misattribution; HG plan calls for a separate pre-launch retrieval attempt.
- **FOCAL plan-set drafted** as 4 sub-plans per Sub-0's recommendation (legal core / contact log / openness+timeliness / aggregation), all converging on a SINGLE `focal_2024.py` module via additions to a shared `_ATOMIC_SPEC` dispatcher dict. Sub-4 launcher must enforce intra-FOCAL ordering.
- **scope.3 v2 staff-split structural delta** — v2 split FOCAL's single `def_target_legislative_or_executive_staff` into 2 cells (`_legislative_staff` + `_executive_staff`). Plan handles via strict-AND projection.
- **FOCAL partly-tier YAGNI collapse** — ~19 of FOCAL's ~20 partly-tier sub-criteria are not extractable from v2 binary cells. Collapse to binary (TRUE → 2; FALSE → 0); document systematic over-scoring on Federal US LDA per battery; tolerance budget ~±15 raw points on the 81 target.
- **scope.2 calibration cutoffs** — Sub-0 had flagged this as a Phase C decision. Plan ships defaults `LOW_DOLLAR_CUTOFF = $1000`, `LOW_TIME_CUTOFF = 5%`. Federal US LDA's $3000 + 20% threshold is "significant" under these cutoffs (matches published scope.2 = 0).
- **2024-vs-2025 vintage handling** — L-N 2025 merged timeliness.1 + timeliness.2 + added "Lobbyist list" indicator. Spec encoded via `min_vintage` / `max_vintage` per `_ATOMIC_SPEC` entry; dispatcher filters by `current_vintage`.

**Provisional findings**

- **FOCAL's partly-tier sub-criteria are mostly not operationally extractable from v2 binary cells.** Only 1 of ~20 (openness.6 "only business IDs") reads cleanly from v2 typed cells. Systematic over-scoring documented in module docstrings; tolerance budgeted per battery in the aggregation plan.
- **scope.3 v2 staff split** is a meaningful structural change from the spec doc. Plan handles via strict-AND; Federal US LDA validation will surface whether strict reading aligns with L-N 2025's coding.
- **HG retrieval gate creates a real branching workflow** for Sub-5+ implementation. Path A (per-state per-item scorecard from CPI archives) gives 1,900-cell ground truth; Path B (composite totals only) gives 50 weak-inequality checks. Launch infrastructure (Sub-4) must run the retrieval attempt first.
- **Cross-rubric overlap promotion at FOCAL landing** — `lobbyist_spending_report_includes_total_compensation` reaches 8-module-confirmed at the projection layer (was 7 after HG; Opheim blocked). Phase 4 cross-rubric agreement audit becomes substantially more powerful.
- **No shared helpers between FOCAL and HG.** Unlike Stream 2 (Newmark 2017's `project_gifts_actor_agnostic_or` shared with Newmark 2005), Stream 3 has no intra-stream helper sharing. FOCAL optionally imports `project_gifts_actor_agnostic_or` from `newmark_2017` for financials.10 if available.

**Decisions carried forward**

- **Sub-3's 5 plans are committed-ready as-is.** Self-contained per write-a-plan; carry the 7 Sub-0 conventions; STOP clauses for spec-doc-vs-v2 drift; Phase-0 cross-checks specified inline; rename mapping tables baked in.
- **4-plan FOCAL split** at battery/concern boundary; all converging on `focal_2024.py`. Sub-4 launcher must enforce intra-FOCAL ordering.
- **HG dual-path validation regime** — Path A (Strong) if scorecard retrievable; Path B (Weak-inequality) if not. Launcher attempts retrieval first; passes `HG_GROUND_TRUTH_PATH=A|B` to implementing agent's environment.
- **FOCAL partly-tier YAGNI collapse** with documented over-scoring tolerance.
- **scope.3 strict-AND read for v2 staff split.**
- **scope.2 calibration defaults** `$1000 / 5%`; per-fixture override for sensitivity analysis.
- **2024-vs-2025 vintage handling** via single dispatcher with `min_vintage` / `max_vintage` per spec entry.
- **19 Open Questions surfaced** across the 5 plans for the implementing agent (or pre-launch decision) to confirm before launch. All flagged in the plans' Open Questions sections.

**Next steps**

Stream 3's plans are ready for Sub-5+ headless implementation once Sub-4's launch infrastructure exists. Recommended sequencing per the locked rubric order: (1) HG 2007 implementation — independent; can launch in parallel with FOCAL. Pre-launch task: scorecard retrieval attempt. (2) FOCAL 2024 implementation — 4 sub-sessions in strict order (legal core → contact log → openness+timeliness → aggregation).

**Sub-4 (launch infra + Sunlight canary)** is the next session. The launch infrastructure handles: path-selection step for HG (retrieval attempt + env var); intra-FOCAL ordering enforcement (4-step sequence); Stream-2 ordering enforcement (Newmark 2017 before 2005); API-key handoff per `plans/20260514_headless_api_key_handoff.md`; Sunlight canary — re-run rubric #3 implementation headless to validate the launcher.

After Stream 3 ships, Phase C is **7 of 8 score-projection rubrics complete** (Opheim blocked on 1988-89 statute data). Phase 4 cross-rubric agreement audit becomes the natural next research line.

---

### 2026-05-18 — Sub-2 Stream 2 plans: Newmark 2017 + Newmark 2005

Convo: [`convos/20260518_newmark_plans_drafting.md`](convos/20260518_newmark_plans_drafting.md)
Plans:
- [`plans/20260518_newmark_2017_plan.md`](plans/20260518_newmark_2017_plan.md) — 435 lines
- [`plans/20260518_newmark_2005_plan.md`](plans/20260518_newmark_2005_plan.md) — 551 lines

**Topics explored**

- Pre-flight: re-confirmed `compendium-naming-docs` + `compendium-row-id-renames` have shipped (15 renames live; `compendium/NAMING_CONVENTIONS.md` exists); confirmed Sunlight 2015 (rubric #3) shipped + CPI 2015 drift fix landed; confirmed Opheim 1991 (rubric #6) flagged blocked on 1988-89 statute data (commit `e62910b`). Sub-2 (deferred during Sub-1 pending GH #9) is unblocked.
- Pulled `phase-c-projection-tdd` worktree forward from `1450eb4` (Sub-1) to `e62910b` (current head) — 30 commits across the v2 row-ID renames, Sunlight 2015 implementation, CPI drift fix, and Opheim blocking caveat.
- **Phase-0 cross-check executed.** Ran `load_v2_compendium()` against the 15 expected Newmark 2017 rows + 8 additional Newmark 2005 cadence rows. Surfaced 7 spec-doc-vs-v2 renames for Newmark 2017 (3 long-form threshold renames `_threshold_for_lobbyist_registration` → `lobbyist_registration_threshold_*` family; 2 gifts `_report_` → `_spending_report_`; 1 `_by_client` → `_by_payer` inherited from Sunlight; 1 contributions-received `_report_` → `_spending_report_`) + 8 cadence renames for Newmark 2005 (`_report_cadence_` → `_spending_report_cadence_` family). All resolved cleanly. Both plans bake the rename tables inline.
- **Newmark 2017 plan drafted** — declarative `_ATOMIC_SPEC` table dispatcher mirroring `pri_2010.py`; 14 in-scope items (5 prohib OUT); Medium validation regime (per-state sub-aggregate); 50-state validation against Phase 0-extracted Table 2 (def.section_total + disclosure.section_total cells, 100 validation-usable cells); rubric-agnostic `project_gifts_actor_agnostic_or` helper for Newmark 2005 + Opheim re-use; honest counterfactual handling of the 2 no-variation items.
- **Newmark 2005 plan drafted** — declarative `_ATOMIC_SPEC` table dispatcher mirroring `newmark_2017.py`; 14 in-scope items (4 prohib + 1 penalty OUT); Weak-inequality validation regime only (Newmark 2005 publishes per-state totals only — no sub-aggregates); imports `project_gifts_actor_agnostic_or` from `newmark_2017`; introduces NEW rubric-agnostic `project_cadence_more_than_annual_or` helper (8-cell OR over sub-annual cadence); 2003-panel-first validation strategy with `xfail` markers for the other 5 panels pending Track A retrieval scope expansion; falsified-2017-speculation regression-guard (Newmark 2005 has 6 disclosure items, NOT 7); explicit no-sub-aggregate-validation discipline (Newmark 2005 doesn't publish sub-aggregates, so module exposes them only as `_informational` fields).
- **Cross-rubric reuse opportunity surfaced** for Opheim 1991 — when Opheim is unblocked, its `project_opheim_disclosure_gifts` can refactor to import the rubric-agnostic helper from `newmark_2017`, and its `project_opheim_disclosure_frequency` is naturally a monthly-only variant of `project_cadence_more_than_annual_or`. Plan flags this as a follow-up; does NOT modify Opheim's drafted plan.

**Provisional findings**

- **Stream 2 ordering is helper-sharing, not row-introduction.** All 6 Newmark-2017-NEW rows are already in v2 (the row-freeze locked them in `compendium-v2-promote`). The dependency between Newmark 2017 and Newmark 2005 is at the helper-import level (`project_gifts_actor_agnostic_or` + threshold IS-NOT-NULL pattern). Sub-4 headless launch script must enforce intra-stream ordering.
- **Newmark 2005 has structurally weaker validation than Newmark 2017** — by a meaningful margin. Newmark 2017 contributes 100 sub-aggregate cells of full-tolerance ground truth from a single 2015 vintage; Newmark 2005 contributes 300 weak-inequality cells across 6 panels, but the inequality has `[0, 4]` headroom from the OOS prohibitions and no per-item / sub-aggregate decomposition. Newmark 2005's role is **temporal-coverage validation**, not direct validation utility — the plan frames this honestly via the validation-regime declaration.
- **Falsified-2017-speculation is a regression-guard hazard.** The Newmark 2017 mapping doc speculated a 2005 parallel for `disclosure.contributions_from_others`; Newmark 2005 mapping doc Correction 1 falsified it. The Newmark 2005 plan bakes in an explicit regression-guard test asserting the `contributions_received_for_lobbying` row is NOT referenced in the module — a future copy-paste error from `newmark_2017.py` would re-introduce the falsified item silently.
- **Rubric-agnostic helper naming pays off here.** `project_gifts_actor_agnostic_or` (rather than `project_newmark_gifts_or` or `project_opheim_gifts_or`) lets Newmark 2005 + (eventually) Opheim import without redefinition. Same pattern for the new `project_cadence_more_than_annual_or` — Opheim's monthly-only variant becomes a natural neighbor.
- **No-sub-aggregate-validation discipline is a new convention.** Newmark 2005's plan introduces an explicit "module must not expose sub-aggregates as validation outputs, but MAY expose them as `_informational` fields with module-docstring caveat." This is finer than the playbook's binary "validation regime tier" — it's a per-rubric output-API decision separate from input-axis decisions. Worth folding into the playbook if HG / FOCAL surface similar shapes.

**Decisions carried forward**

- **Sub-2 plans are committed-ready as-is.** Self-contained per write-a-plan; carry the 7 Sub-0 conventions; STOP clauses for spec-doc-vs-v2 drift; Phase-0 cross-checks specified inline; rename mapping tables baked in.
- **Helper-sharing pattern**: `project_gifts_actor_agnostic_or` lives in `newmark_2017.py` (Newmark 2005 imports it). `project_cadence_more_than_annual_or` lives in `newmark_2005.py` (Opheim's eventual monthly-only variant will live alongside). Refactor to a shared `lobby_analysis.projections._shared` module only when HG / FOCAL need a third helper.
- **Newmark 2005's panel strategy**: 2003 panel-first validation at Phase C launch; `xfail` markers for the 5 earlier panels pending Track A scope expansion. Track A scope expansion is a separate conversation on `oh-statute-retrieval` branch — NOT in Phase C scope.
- **No-sub-aggregate-validation convention**: when a rubric publishes per-state totals only (no sub-aggregates), the projection module may expose sub-aggregates as `_informational` fields for debugging / Phase 4 audit, but tests do NOT assert equality against any published sub-aggregate value. Convention documented inline in Newmark 2005 plan; consider hoisting to the playbook if HG / FOCAL share the shape.
- **7 Open Questions surfaced** across both plans for the implementing agent to confirm before launch. All flagged in the plans' Questions sections.

**Next steps**

Stream 2's plans are ready for Sub-5+ headless implementation once Sub-4's launch infrastructure exists. Recommended sequencing per the locked rubric order: (1) Newmark 2017 implementation (must land first — Stream 2 ordering); (2) Newmark 2005 implementation (imports helpers from Newmark 2017). After Stream 2 ships, Phase 4 cross-rubric agreement audit prototype becomes substantially more powerful — the `lobbyist_spending_report_includes_total_compensation` 8-rubric mega-row gains 2 more readers (CPI + PRI + Sunlight + Newmark 2017 + Newmark 2005 = 5 module-level readers).

Sub-3 (FOCAL plan-set + HG plan with retrieval gate) is the next plan-drafting session; Sub-4 (launch infra + Sunlight canary) follows. Opheim remains blocked on 1988-89 statute data — when unblocked, its plan benefits from refactoring to import `project_gifts_actor_agnostic_or` from `newmark_2017` and from co-locating its monthly-only cadence helper alongside `project_cadence_more_than_annual_or` in `newmark_2005`.

---

### 2026-05-18 — CPI 2015 drift fix + v2 row-reference audit (closes GH #17)

Convo: [`convos/20260518_cpi_drift_fix_and_v2_row_audit.md`](convos/20260518_cpi_drift_fix_and_v2_row_audit.md)
Predecessor: same-day Sunlight 2015 session ([`convos/20260518_sunlight_2015_projection_tdd.md`](convos/20260518_sunlight_2015_projection_tdd.md)) — surfaced the IND_201 drift and filed it as GH #17.
GH issue: [danparshall/lobby_analysis#17](https://github.com/danparshall/lobby_analysis/issues/17)

**Topics explored**

- Verified GH #17's claims against the live v2 TSV — 6 reference sites for IND_201's bad name; `lobbyist_spending_report_includes_total_compensation` confirmed at line 138 (8-rubric mega-row).
- Wrote a first-pass shape-based audit. It immediately flagged a second drift instance at IND_200 (`registration_timeliness_after_first_lobbying_activity` — merged into two-axis `lobbyist_registration_deadline_days_after_first_lobbying` by D11 of the row-freeze) plus 4 false-positive enum-value matches (`cadence in (...)` / `rule == "..."` comparisons).
- Per user direction, fixed IND_200 here too and rewrote the audit with syntactic AST detection.
- My first IND_200 rename used the wrong v2 name (took it from the historical mapping doc, which uses the unprefixed `registration_deadline_days_after_first_lobbying`); the rewritten audit caught it. Actual v2 row is `lobbyist_registration_deadline_days_after_first_lobbying` (line 178 v2 TSV).
- Syntactic AST audit detects 4 reference patterns + sentinel-prefix exclusion: `_legal/_practical(cells, X)` second arg; `cells[X]` subscript; tuple-register `("ID", X, _LEGAL|_PRACTICAL)`; module-level `_FOO_ROW`/`_FOO_ROWS` constants; `__`-prefixed names excluded as deliberate test-only sentinels (sole instance: `__ind_205_partial_credit_passthrough`).

**Provisional findings**

- **Audit is load-bearing.** Paid for itself before commit — caught a second drift instance the issue didn't name, then caught my own wrong-rename. Both surfaced from end-state detection, not prior knowledge.
- **Syntactic detection is the right model.** Shape-based has irreducible false positives because v2 row names and v2 enum values share lexical shape. Syntactic detection by AST position cleanly separates them and is robust to new accessors that follow the `(cells, row_id, ...)` convention.
- **The v2 TSV is the source of truth for current row names.** The historical mapping docs predate the freeze and use earlier candidate names; treat them as background, not as the contract. Burnt-finger lesson from the IND_200 wrong-rename.

**Results**

No standalone results files this session.

**Decisions carried forward**

- Audit scope is `src/lobby_analysis/projections/*.py` only. Test-side fixture-drift audit punted to follow-up if more surface (would need stricter detection, e.g., only `cells[...]` subscripts in test files).
- 3 pre-existing `test_pipeline.py` failures (FileNotFoundError on `data/portal_snapshots/CA/2026-04-13/manifest.json`) NOT fixed — out of scope; require `data/` symlink plumbing for this worktree (intentionally absent at branch creation per RESEARCH_LOG line 33–35). Surfaced to user.

**Next steps**

Phase 4 cross-rubric agreement audit on the `_total_compensation` 8-rubric mega-row is now unblocked. Per the predecessor convo's recommendation: either (a) Newmark 2017 (rubric #4) plan-drafting or (b) Opheim 1991 (rubric #6) implementation — both ready, both advance the locked rubric order; or (c) prototype the cross-rubric agreement audit on the now-3-module overlap (CPI + PRI + Sunlight).

---

### 2026-05-18 — Sunlight 2015 projection: rubric #3 shipped

Convo: [`convos/20260518_sunlight_2015_projection_tdd.md`](convos/20260518_sunlight_2015_projection_tdd.md)
Results: [`results/20260518_sunlight_2015_projection.md`](results/20260518_sunlight_2015_projection.md)
Plan: [`plans/20260514_sunlight_2015_plan.md`](plans/20260514_sunlight_2015_plan.md)
Spec doc: [`../../historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md`](../../historical/compendium-source-extracts/results/projections/sunlight_2015_projection_mapping.md)

**Topics explored**

- Phase 0 pre-flight: v2 cross-check (13/13 expected rows present after the `_by_client` → `_by_payer` rename); ground-truth CSV smoke (50 rows × 10 cols; 36 marker-carrying cells inventory); data-year paper re-read (line 242 "Kansas chooses not to hold any lobbying data before 2015" lifts confidence MEDIUM-LOW → MEDIUM).
- 4 in-scope items TDD'd item-by-item with RED-GREEN-COMMIT cadence (item 1 split into 3 sub-stages: unable_to_evaluate → truth-table → oddity flags).
- Function-per-item dispatcher (matches CPI 2015 C11 style; PRI 2010's declarative table wouldn't compress Sunlight's bespoke compound logic).
- Reverse-projection cells builder as a test-only fixture, enabling 50-state × 4-item parameterized round-trip (200 cells).
- Item 4 (`document_accessibility`) regression-guarded as excluded (no helper, in `EXCLUDED_ITEMS`).
- No-aggregation regression guards: module exports no `_total`/`_grade`/`rank_*` function; `Sunlight2015Score` has no total/grade/rank field.
- Footnote-marker stripping in ground-truth loader + sibling provenance dict (36 markers: 28 `*`, 2 `**`, 5 `***`, 1 `^^`).
- **Pre-existing CPI 2015 drift surfaced during Phase 0** — `project_ind_201` reads `lobbyist_spending_report_includes_compensation` which doesn't exist in v2 (merged into `_total_compensation` by D1/D2 of row-freeze). CPI tests pass only because fixtures use the same wrong name. Filed as task #12; **NOT fixed this session.**

**Provisional findings**

- **Helper signature `tuple[int | Literal["unable_to_evaluate"], str | None]` is clean.** Score is either tier or sentinel; oddity flag is None or a description string. Threaded into the score model with `per_item_scores: dict[str, int | str]` and `oddity_flags: dict[str, list[str]]`.
- **Item 1 vs item 2 semantics: a real asymmetry surfaced.** Item 1's spec table is monotonic (no wildcards); item 2's uses an explicit `(T, *, T) → 2` wildcard. I implemented item 1 with **cascading-downward** (lowest failing predicate sets tier) and item 2 with the wildcard. Both are defensible; future rubrics with nested predicates should pick deliberately.
- **Item 3 None-vs-missing asymmetry.** For the typed-cell case, `legal_availability=None` projects to tier 0 per the spec rule "threshold IS NULL → 0". The `unable_to_evaluate` sentinel is reserved for "row not a key in cells." Items 1, 2, 5 use a different convention: legal_availability=None on a binary cell → unable_to_evaluate.
- **The 200-cell round-trip is a weak validation.** It exercises reverse-projection-to-projection consistency, not statute-extraction-to-projection consistency. Real validation comes when `extraction-harness-brainstorm` ships and projections run on actual extracted cells.
- **Sunlight cross-rubric reuse is high.** 11 of 13 v2 rows feed ≥1 other rubric. Phase 4 cross-rubric agreement audit (deferred until ≥3 modules exist; we now have CPI + PRI + Sunlight) is now well-defined — though the CPI drift means the audit can't yet land cleanly on the `_total_compensation` row.

**Results**

- [`results/20260518_sunlight_2015_projection.md`](results/20260518_sunlight_2015_projection.md) — what landed, validation outcome, Phase 0 outcomes, row-promotion delta, naming-drift corrections, items skipped per YAGNI, decisions log.

**Decisions carried forward**

- Helper return shape unified (tuple).
- Item 1 cascading-downward semantics — revisitable in Phase 4.
- No aggregation API — firm.
- CPI #201 drift fix sequencing: **task #12 first** (small, surgical, unblocks Phase 4 prototyping by fixing the `_total_compensation` audit row), then either Newmark 2017 (rubric #4) or Opheim 1991 (rubric #6 — Opheim's β-AND test now resolves since `project_sunlight_item1` exists).
- Data-year confidence lift documented in `results/20260514_rubric_data_years.md`; Sub-1 follow-up checklist updated.

**Next steps**

Recommended sequencing: (d) fix CPI drift (task #12) → (a) Newmark 2017 plan-drafting OR (b) Opheim 1991 implementation. (a) and (b) are equally good after (d); either advances the locked rubric order. Phase 4 cross-rubric audit prototype becomes viable post-(d).

---

### 2026-05-14 — Sub-1 Stream 1 plans: Sunlight 2015 + Opheim 1991

Convo: [`convos/20260514_sub_1_sunlight_opheim_plans.md`](convos/20260514_sub_1_sunlight_opheim_plans.md)
Plans:
- [`plans/20260514_sunlight_2015_plan.md`](plans/20260514_sunlight_2015_plan.md) — 399 lines
- [`plans/20260514_opheim_1991_plan.md`](plans/20260514_opheim_1991_plan.md) — 491 lines
GH issue: [danparshall/lobby_analysis#9](https://github.com/danparshall/lobby_analysis/issues/9)

**Topics explored**

- Pre-flight: Sub-0's three artifacts + the headless-API-key handoff doc + both rubrics' projection mapping docs (Sunlight 217 lines, Opheim 424 lines).
- API-key billing confirmed via `/status` on Dans-MacBook-Pro (work-project budget per the multi-sub-session design).
- **Phase-0 cross-check executed.** Ran `load_v2_compendium()` against the 13 expected Sunlight rows + 17 expected Opheim rows. Surfaced 5 spec-doc-vs-v2 renames (1 in Sunlight: `_by_client` → `_by_payer`; 4 in Opheim: `*_report_*` → `*_spending_report_*` for cadence + gifts pairs — same family PRI 2010 caught). All under the 10% STOP threshold; both plans bake the rename tables inline.
- **Sunlight 2015 plan drafted** — function-per-item dispatcher; 4 in-scope items (item 4 EXCLUDED per 2026-05-07 audit); Strong validation regime (200-cell ground truth in `papers/Sunlight_2015__...csv`); no-`Total`/no-`Grade` regression-guard tests; data-year Phase-0 confidence-lift task (MEDIUM-LOW → goal MEDIUM/HIGH).
- **Opheim 1991 plan drafted** — declarative `_ATOMIC_SPEC` table mirroring PRI 2010 + 3 named helpers (cadence-OR, gifts-OR, β AND); 14 effective in-scope items + 1 un-projectable catch-all (max 14/22); Weak-inequality validation regime only; 47-state sample (MT/SD/VA missing) enforced via `ValueError`; β AND-projection cross-rubric continuity test imports `project_sunlight_item1`; Phase-0 task extracts Table 1 from paper text (no CSV exists).
- **Token-prefix conventions audit (user-prompted).** Searched `compendium/README.md`, `20260513_row_freeze_decisions.md`, the row-freeze brainstorm convo, the rubric playbook, per-rubric mapping docs. Found D3 (and D1, D2, D6) document the specific renames; broader prefix-family taxonomy is NOT canonically documented. Captured as GH #9.
- **Branching analysis for the docs overhaul.** Verified `git diff --stat origin/main -- compendium/` is empty on this branch (Phase C is read-only on `compendium/`). Concluded: GH #9 can land cleanly off main; both compendium-consumer branches (`phase-c-projection-tdd`, `extraction-harness-brainstorm`) pull main forward afterward.

**Provisional findings**

- **Spec-doc-vs-v2 drift is a recurring Phase B → Phase C handoff failure mode.** PRI 2010 hit it; Sunlight + Opheim hit it again (same `*_report_*` family); Stream 2/3/4 likely will too. Systemic fix is GH #9; per-plan workaround (rename mapping table inline) is sufficient but adds friction.
- **Stream 1 plans are self-contained but internally coupled.** Sunlight must land before Opheim's implementation runs (Opheim's cross-rubric continuity test imports `project_sunlight_item1`). Sub-4's headless launch script needs to encode this ordering.
- **`unable_to_evaluate` convention now exercised concretely.** Sunlight uses it for missing input cells; Opheim uses it for missing cells AND the operationally-undefined catch-all. Per Sub-0 gap audit Pattern 3, this is the canonical disclosure-only-Phase-B treatment.
- **β AND-projection second-exemplification landed.** First was Sunlight item 1's row introductions (locked 2026-05-11); second is Opheim's `disclosure.legislation_supported_or_opposed`. Pattern is now empirically demonstrated, not just hypothesized.
- **`phase-c-projection-tdd` is read-only on `compendium/`.** Structurally true (Phase C consumes the v2 contract; doesn't modify it) and empirically verified. Off-main → merge-back → merge-forward works cleanly for GH #9.

**Decisions carried forward**

- **GH #9 is the prerequisite for clean Stream 2/3/4 plan-drafting.** Recommendation: defer Sub-2 (Newmark 2017 → Newmark 2005) until #9 merges. Newmark 2017 introduces 6 new rows whose naming would benefit from the taxonomy doc landing first.
- **Sub-1 plans are committed-ready as-is.** Self-contained per write-a-plan; carry the 7 Sub-0 conventions; STOP clauses for spec-doc-vs-v2 drift; Phase-0 cross-checks specified inline; rename mapping tables baked in.
- **5 Open Questions surfaced** for the implementing agent to confirm before launch (oddity-flag return shape; Opheim Table 1 CSV destination; MT/SD/VA refusal vs sentinel; Sub-4 launch-ordering enforcement; `_is_not_null` helper survival). All flagged in the plans' Questions sections.

**Next steps**

Sub-2 (Newmark 2017 + Newmark 2005) — recommend defer until GH #9 merges. Sub-1's deliverables are ready for Sub-5+ headless implementation once Sub-4's launch infrastructure exists. If a parallel `compendium-naming-docs` branch is cut to land GH #9, `phase-c-projection-tdd` will pull main forward after that branch merges (expected-clean merge).

---

### 2026-05-14 — Rubric plans drafting (meta-session, sub-0 of 5): playbook gap audit + data-year audit

Convo: [`convos/20260514_rubric_plans_drafting.md`](convos/20260514_rubric_plans_drafting.md)
Results:
- [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) — playbook vs reality for the 6 remaining rubrics
- [`results/20260514_rubric_data_years.md`](results/20260514_rubric_data_years.md) — publication-year vs data-year per rubric (12 distinct vintages across the 8 rubrics)

**Topics explored**

- **Meta-question:** can the 6 remaining rubrics (Sunlight, Newmark 2017/2005, Opheim, HG 2007, FOCAL 2024) be parallelized for headless API-key-billed implementation? Motivation: user wants to bill API key (work-project budget) instead of Claude Code subscription. Original framing was "pure parallelism via API."
- **Reframe chain:** Pure parallelism fights inter-rubric dependencies. Counter: 3 streams (Sunlight→Opheim; Newmark 2017→2005; FOCAL), HG held on `oh-statute-retrieval` Track A. Counter to counter: 2 retrieval blockers for HG, not 1 (CPI scorecard + Track A). Settled: 5 sub-sessions structure with plans drafted in this branch's worktree, headless launches via `claude -p` with API-key auth in later sub-sessions.
- **Playbook gap audit (sub-0 main work).** Read intro + scope + aggregation + validation + Open Issues of all 5 remaining spec docs (Newmark 2017, Newmark 2005, Opheim 1991, HG 2007, FOCAL 2024); also re-read Sunlight 2015 in full as sanity-check on whether playbook is faithful.
- **Data-year audit (user interjection mid-session).** Grepped `papers/text/` for each rubric to identify publication-year vs data-year — critical because extraction needs to fetch correct statute vintage from Justia. Found 12 distinct statute vintages spanning 1988-89 → 2025.

**Provisional findings — 5 cross-cutting meta-patterns the playbook missed**

1. **"Disclosure-only Phase B" scope qualifier applies to every remaining rubric** (5 prohib in Newmark 2017; 5 prohib+penalty in Newmark 2005; 8 enforce+catch-all in Opheim; 10 enforce+cooling-off in HG; 1 revolving_door.2 in FOCAL post-FOCAL-1). None can reproduce their published index total.
2. **Validation regime tiers split 3 ways** — Strong (CPI/HG/FOCAL: per-state per-item); Medium (PRI/Newmark 2017: per-state sub-aggregate); **Weak-inequality only (Newmark 2005, Opheim 1991)**: `our_partial ≤ paper_total` is the only check.
3. **`unable_to_evaluate` convention applies across the board** (not just Opheim's catch-all): OOS items, un-projectable items, and Phase D portal-cells when only statute data is available. Critically: **not zeroed** (so weak-inequality holds).
4. **"Same-row-different-binary-cut" is a recurring per-item helper pattern** (PRI cadence family read by Newmark 2005 at 8-cell-OR and Opheim at 2-cell-OR).
5. **Row-promotion meta-pattern (`X-rubric-confirmed`)** is the seed of Phase 4 cross-rubric audit. `lobbyist_spending_report_includes_total_compensation` is now 7-rubric-confirmed.

**Provisional findings — biggest per-rubric surprises**

- **FOCAL 2024 has NO per-state US ground truth** — only federal LDA + 27 other countries. Cross-rubric is the *only* check for state FOCAL projections.
- **Newmark 2005 is NOT a near-clone of Newmark 2017** — different aggregation (4 sections vs 3), different validation regime (weak-inequality vs sub-aggregate), 6 panels vs 1.
- **HG 2007 has TWO retrieval blockers, not one**: (a) CPI's 2007 per-state scorecard (NOT Track A), (b) Track A `oh-statute-retrieval` for OH-specific sub-task.
- **HG's 22 NEW rows include 13 practical-availability cells** requiring portal observation, not statute extraction. Phase D targets.
- **FOCAL is substantially heavier than playbook suggests** — 11 Open Issues, scorer-judgment cutoff for scope.2, 2024→2025 numbering asymmetry, set-typed cells, weighted aggregation.

**Provisional findings — data-year audit (user-interjected)**

- 12 distinct statute vintages across the 8 rubrics, 1988-89 → 2025.
- **HG 2007 has per-item vintage split**: Q35-Q37 at 2002, rest at 2006-2007.
- **FOCAL state projections are vintage-flexible**: align to L-N 2025's 2019-2023 collection window.
- 4 rubrics have MEDIUM-or-lower data-year confidence (Sunlight, CPI 2015, PRI 2010, Newmark 2017); papers should be re-read during plan drafting to firm up.
- `oh-statute-retrieval` (Track A) currently fetches 4 vintages (2007/2010/2015/2025); full Phase C validation needs 12. Track A scope expansion is a separate conversation.

**Decisions carried forward**

- **Structure B**: 5 sub-sessions (sub-0 gap audit now complete; sub-1 Stream 1 plans → sub-2 Stream 2 plans → sub-3 FOCAL plan-set + HG plan → sub-4 launch infra + Sunlight canary).
- **FOCAL plan shape**: split into 3-4 sub-plans per scope (legal-side core, contact_log battery, openness battery, aggregation + US LDA validation).
- **HG plan launch gated** on Phase 0 scorecard retrieval; plan drafted with both paths (per-state if retrievable, weak-inequality if not).
- **Strict reading of disclosure-only Phase B scope** — keep current OOS items OUT; FOCAL-1 precedent does not retroactively apply.
- **7 convention proposals** from the gap audit to bake into all 6 plans (see [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) for the full list).

**Results**

- [`results/20260514_playbook_gap_audit.md`](results/20260514_playbook_gap_audit.md) — gap audit (5 cross-cutting meta-patterns + per-rubric gaps + implementation implications + convention proposals + decisions).
- [`results/20260514_rubric_data_years.md`](results/20260514_rubric_data_years.md) — publication-year vs data-year lookup table for all 8 rubrics, with confidence levels and paper-line citations.

**Next steps**

Sub-session 1 (next; separate Claude Code session with API-key auth): Stream 1 plans — Sunlight 2015 + Opheim 1991 in a single sub-session. Sunlight first (function-per-item; item 4 exclusion; per-item validation regime); Opheim second (declarative table; weak-inequality regime; un-projectable catch-all; β AND-projection reuse from Sunlight). Both plans self-contained per write-a-plan skill, with STOP clauses for spec-doc-vs-v2 drift. Each plan opens with a "Scope qualifier" + "Validation regime" + "Data year" section per the conventions established by sub-0.

After Sub-1: Sub-2 (Newmark 2017 → 2005), Sub-3 (FOCAL plan-set + HG plan with retrieval gate), Sub-4 (prompt template + headless launch script + Sunlight canary). HG launch waits on scorecard retrieval task (#6).

---

### 2026-05-14 — PRI 2010 projection: rubric #2 + PRI-MVP retirement

Convo: [`convos/20260514_pri_2010_tdd.md`](convos/20260514_pri_2010_tdd.md)
Results: [`results/20260514_pri_2010_projection.md`](results/20260514_pri_2010_projection.md)
Spec doc: [`../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md`](../../historical/compendium-source-extracts/results/projections/pri_2010_projection_mapping.md)
Rollup spec: [`../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md`](../../historical/pri-calibration/results/20260419_pri_rollup_rule_spec.md)

**Topics explored**

- Per-atomic-item projection logic for 76 PRI 2010 rubric items (54 disclosure-law + 22 accessibility). 75 are pure binary cell -> 0/1 passthroughs; Q8 is a typed 0..15 passthrough.
- Reuse of the paper-derived rollup helpers at `src/scoring/calibration.py` (handoff's "port if survived, rebuild from spec doc if not" resolved to **port** — the rollup is intact and unit-tested by 114 rule-level tests).
- Spec-doc / v2-TSV naming drift. Spec's `principal_report_*` and `lobbyist_report_*` resolve to v2's `principal_spending_report_*` and `lobbyist_spending_report_*`. E1f_i and E2f_i resolve to multi-rubric shared rows.
- End-to-end validation strategy given PRI publishes only sub-aggregate ground truth. User picked rule-based: existing calibration rollup tests + fixture per-item tests + accessibility 50-state round-trip + disclosure-law wiring tests.
- Architectural decision: declarative spec table for per-item layer (vs CPI's function-per-item pattern). Resolves CPI's deferred Open Question on cross-rubric template.
- Phase 3 PRI-MVP retirement (same session): move `smr_projection.py` and `test_smr_projection.py` to `_deprecated/` subdirs with SUPERSEDED banners; remove `cmd_build_smr` from `orchestrator.py`.

**Provisional findings**

- **Two projection axes, separate functions.** PRI 2010 publishes disclosure-law (max 37) and accessibility (max 22) as independent scores. Top-level API: `project_pri_2010_disclosure_law` + `project_pri_2010_accessibility`, each returning a typed score model carrying atomic_scores + sub-aggregates + total + percent.
- **Accessibility 50-state round-trip passes within tolerance.** Max residual ~0.05 across all 50 states (1-dp rounding artifact of PRI's published total_2010 column). Q8_normalized's 1-dp publication is the dominant error source (recovering Q8_raw introduces at most 0.033 per state); well inside ±1 spec.
- **No letter grade for PRI 2010.** Same as CPI 2015. The handoff's "confirm rubric-by-rubric" question for letter grades resolved negatively for rubric #2 as well.
- **`lobbyist_spending_report_includes_total_compensation` reaches 8 rubrics.** Once two projection modules read it, cross-rubric agreement audit on that row becomes well-defined — this is the kind of redundant validation Compendium 2.0's success criterion #4 was built for.
- **PRI-MVP cleanly retires.** 10 deprecated tests still pass when targeted directly (`uv run pytest tests/_deprecated/test_smr_projection.py`); excluded from default pytest collection.

**Results**

- Module: `src/lobby_analysis/projections/pri_2010.py` (388 LOC; declarative `_ATOMIC_SPEC` table + two Pydantic score models + 2 top-level projections + competition rank + ground-truth loaders).
- Tests: `tests/projections/test_pri_2010_per_item.py` (247 tests), `test_pri_2010_ground_truth.py` (6 tests), `test_pri_2010_aggregation.py` (13 tests) — 266 new tests, all passing.
- Phase 3 retirement: `src/scoring/smr_projection.py` -> `src/scoring/_deprecated/smr_projection.py`, `tests/test_smr_projection.py` -> `tests/_deprecated/test_smr_projection.py`, `cmd_build_smr` + helpers removed from `orchestrator.py`, `norecursedirs = ["_deprecated"]` added to pyproject.
- Full test suite: 640 passing + 5 skipped + 3 pre-existing failures (same `tests/test_pipeline.py::test_ca_snapshot_*` failures CPI 2015 flagged; missing gitignored data file).

**Decisions carried forward**

- **Declarative `_ATOMIC_SPEC` table** is the right pattern for rubrics with many near-identical per-item helpers. CPI's function-per-item pattern still fits rubrics with bespoke compound reads.
- **Cross-check spec-doc row names against v2 TSV early** — Phase B projection mappings written pre-`compendium-v2-promote` may have similar `*_spending_report_*` rename drift.
- **Per-rubric module + sibling tests pattern** carries forward unchanged from CPI: `src/lobby_analysis/projections/<rubric>.py` + `tests/projections/test_<rubric>_*.py`.
- **End-to-end validation tolerance is per rubric.** PRI accessibility supports 50-state round-trip; PRI disclosure-law is rule-level only (per-atomic-item ground truth never published). Future rubrics need a per-rubric validation strategy decision.

**Next steps**

Either:
- (a) Rubric #3: Sunlight 2015 (13 rows; 11 cross-rubric). Locked conventions: α form-type split, β Opheim AND-projection, "collect once, map many" annotation.
- (b) Phase 4 cross-rubric agreement audit prototype, using CPI + PRI's two-module overlap.
- (c) Backport CPI 2015 to declarative table format (probably premature — CPI's compound reads don't compress cleanly into a 2-tuple spec).

Recommendation: (a). Cross-rubric audit (b) is more useful with 3 modules.

**Rubric-implementation playbook landed same session:** [`plans/20260514_rubric_implementation_playbook.md`](plans/20260514_rubric_implementation_playbook.md) generalizes the CPI + PRI patterns into a reusable kickoff brief for the remaining 6 rubrics (Sunlight, Newmark 2017/2005, Opheim, HG, FOCAL). Future rubric sessions should read the playbook instead of the original kickoff plan sketch — the playbook covers pre-flight (spec doc + v2-row-name cross-check + ground-truth location + rollup-helper survival check), architectural decision (declarative table vs function-per-item), validation regime selection, standard module structure, common rubric patterns (binary / tier / compound / typed / reverse-scoring / AND-projection / form-type-split / collect-once-map-many / catch-all), per-rubric notes for the 6 remaining rubrics, Phase 3 retirement protocol, and Phase 4 cross-rubric audit shape.

---

### 2026-05-14 — CPI 2015 C11 projection: first TDD session

Convo: [`convos/20260514_cpi_2015_c11_tdd.md`](convos/20260514_cpi_2015_c11_tdd.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md) (Phase 0 + Phase 1)
Results: [`results/20260514_cpi_2015_c11_aggregation_fit.md`](results/20260514_cpi_2015_c11_aggregation_fit.md)

**Topics explored**

- Per-item projection logic for the 14 CPI 2015 C11 indicators (6 de jure
  Boolean / threshold / enum reads + 8 de facto 5-tier passthroughs +
  1 compound passthrough on IND_205).
- Empirical fit of the aggregation rule against the published 50-state
  per-state aggregate. Four candidates evaluated; only one fits within
  tolerance.
- Data-quality normalization for 8 known glitch cells in the 700-cell
  ground-truth CSV (6 mixed-case Colorado cells + 2 numeric-where-
  categorical cells in Texas / Massachusetts).
- Rank tie-break convention used by CPI's published per-category rank.

**Provisional findings**

- **Aggregation rule:** unweighted mean of the 5 sub-category means
  (sub-cats 11.1-11.5 extracted from `papers/CPI_2015__sii_criteria.xlsx`,
  item counts 2/4/3/2/3). Max abs residual across 50 states is 0.05,
  i.e. a one-decimal rounding artifact of the published score. The
  other 3 candidates (simple mean, de-jure/de-facto halves, sequential
  sub-cats) miss the +/-1 tolerance on 18-38 of 50 states.
- **Normalization for invalid de jure cells:** the 2 numeric-string
  cells (Texas IND_199 "100", Massachusetts IND_203 "100") are
  consistent with CPI's aggregator treating them as NO (0), not YES
  (100). Setting them to NO produces exact fit; setting them to YES
  over-estimates by ~6.7 per state. Codified as a 0-default fallback
  for any de jure cell not in the YES/MODERATE/NO set after
  case-insensitive match.
- **Rank tie-break:** CPI uses competition ranking (1224 style; ties
  share a rank, next rank skips). Sequential ranking with alphabetical
  tie-break (a-priori guess) was off-by-1 to off-by-2 on 11 states.
- **No per-category letter grades.** CPI 2015 publishes letter grades
  at the overall-state level only. The kickoff plan implied
  per-category grades; that was incorrect for C11. Letter-grade
  projection dropped from this rubric's deliverable; rubrics #2-#8
  likely the same — confirm rubric-by-rubric.

**Results**

- Module: `src/lobby_analysis/projections/cpi_2015_c11.py` (per-item
  helpers IND_196-IND_209, ground-truth loader, sub-cat aggregator,
  rank, top-level `project_cpi_2015_c11`, `CPI2015C11Score` Pydantic
  model).
- Tests: `tests/projections/test_cpi_2015_c11_per_item.py`,
  `test_cpi_2015_c11_ground_truth.py`,
  `test_cpi_2015_c11_aggregation.py` (78 tests, all passing; full
  suite 384 pass + 3 pre-existing failures from
  `tests/test_pipeline.py` unrelated to this branch).
- Fit script: `scripts/fit_cpi_2015_c11_aggregation.py` (reproduces
  the empirical-fit decision; evaluates 4 candidate aggregators).
- Fit result: `results/20260514_cpi_2015_c11_aggregation_fit.md`.

**Decisions carried forward**

- Per-rubric module layout: `src/lobby_analysis/projections/<rubric>.py`
  + `tests/projections/test_<rubric>_*.py`.
- Cell input shape: `cells[row_id][axis] = value` nested dict,
  harness-independent.
- Per-item helper return type: plain `int` in {0, 25, 50, 75, 100}.
- Score type: frozen Pydantic model with `state` + `per_item_scores`
  dict + `category_score` float (no per-category letter grade — not
  published).
- Aggregation-fit pattern: try 3-4 closed-form candidates (simple mean,
  de-jure/de-facto halves, sub-cat means from published methodology
  doc when available, etc.), pick the one with the smallest max
  residual against published per-state aggregate.

**Next steps**

Either (a) start rubric #2 (PRI 2010, 69 rows; sub-aggregate rollup
rule already paper-derived in archived `pri-calibration` — port if
recoverable, rebuild from spec doc if not) or (b) refactor CPI
projection toward a declarative table format before more rubrics land.
Recommendation: (a). Refactor only if PRI 2010 makes duplication
painful.

**Pre-existing test failures flagged.** 3 tests in
`tests/test_pipeline.py` (test_ca_snapshot_*, test_brief_contains_*,
test_stamp_rows_*) fail on this branch *and* on main because
`data/portal_snapshots/CA/2026-04-13/manifest.json` doesn't exist
(`data/` is gitignored, no symlink set up for this branch). Not caused
by this session; flagged for the next person who looks at the test
suite — likely needs a `pytest.skipif` on missing data path or a
documented data-symlink step.

---

### 2026-05-14 — Kickoff orientation + plan sketch (NOT the first TDD session)

Convo: [`convos/20260514_kickoff_orientation.md`](convos/20260514_kickoff_orientation.md)
Plan: [`plans/20260514_kickoff_plan_sketch.md`](plans/20260514_kickoff_plan_sketch.md)

**Originating context.** This branch was assigned plan-sketch work as a side-effect of the 2026-05-14 coordination session on `compendium-v2-promote` (see [`../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md`](../../compendium-v2-promote/convos/20260514_compendium_v2_promote.md), available post-merge). User wanted a "solidly sketched" plan in `plans/` so the kickoff agent isn't reading skeleton stubs cold.

**Locked decisions carried forward.** v2 row contract now lives at `compendium/disclosure_side_compendium_items_v2.tsv` (181 rows). `extraction-harness-brainstorm` owns v2 Pydantic models; this branch operates on raw `dict[str, Any]` keyed by `compendium_row_id` until those models exist. The ⛔ PRI-out-of-bounds banner is gone — PRI is rubric #2 in this branch's locked order.

**Sketch contents.** Concrete TDD agenda starting with CPI 2015 C11 (most-ready first rubric):
- Phase 0: env setup + projections module skeleton (`src/lobby_analysis/projections/`)
- Phase 1: per-item TDD cycles for 14 CPI items (6 de jure 2/3-tier + 8 de facto 5-tier per spec doc); aggregation rule fitted empirically against 50-state ground truth (700 cells per-item + 50 cells category-aggregate); letter grade + rank as derivations
- Phase 2: carry pattern through remaining 7 rubrics in locked order, with per-rubric notes (PRI 2010 rollup recoverable from `pri-calibration` archive; Newmark 2005 = 100% reuse of 2017; Opheim 100% reuse + weak-inequality tolerance; HG 2007 blocked on `oh-statute-retrieval`; FOCAL 2024 lowest reuse at 37.9%)
- Phase 3: PRI-MVP retirement after rubric #2 (move `cmd_build_smr` + `smr_projection` to `_deprecated/`)
- Phase 4: cross-rubric agreement audit after all 8 rubrics ship

**Recommended first session deliverable:** CPI 2015 C11 projection function (per-item + aggregation) passing against the 700-cell per-state-per-item + 50-cell category-aggregate ground truth.

**Open questions flagged for the first TDD session.** scipy/numpy availability for aggregation-rule fitting (current `pyproject.toml` has neither); PRI rollup helper recoverability from `pri-calibration` archive; letter grade boundaries (published vs back-fit); OH SMR equivalence tolerance for PRI-MVP retirement validation.

**Not implementation work.** No code, no tests written; only docs (the convo + plan sketch + this RESEARCH_LOG update + the Row-freeze contract path migration).


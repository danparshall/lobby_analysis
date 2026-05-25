# v2 Pydantic Cell Models — Implementation Plan

**Goal:** Build the typed Pydantic v2 cell model layer (`src/lobby_analysis/models_v2/`) — `CompendiumCell` ABC, per-cell-type subclasses, the `CompendiumCellSpec` registry mapped from the 186-cell roster, and the `StateVintageExtraction` container — under TDD. Pure-data; no LLM calls; unblocks both this branch's downstream LLM-calling harness work and Phase C's projection function work.

**Originating conversation:** [`../convos/20260514_extraction_harness_brainstorm.md`](../convos/20260514_extraction_harness_brainstorm.md) (Phase 2 architectural decisions; locks the (row_id, axis) cell-ID space and the separate-module layout via AskUserQuestion).

**Antecedent agenda:** [`20260514_kickoff_plan_sketch.md`](20260514_kickoff_plan_sketch.md) (this is the implementation plan that sketch teed up; sketch's recommended first component was "v2 Pydantic cell models," reaffirmed by the brainstorm).

**Context:** Compendium 2.0 landed 2026-05-14 (`compendium-v2-promote` merged as `0a6804f`) with a 181-row × 8-column TSV at `compendium/disclosure_side_compendium_items_v2.tsv`. The v2 row contract has 29 distinct `cell_type` values (150 binary + 31 typed), spanning 126 legal + 50 practical + 5 legal+practical axes. This branch owns the v2 Pydantic model rewrite (model shape = extraction output shape). Phase C consumes the resulting cell types as a downstream contract; their projection functions read `dict[tuple[str, str], CompendiumCell]` keyed by (row_id, axis) per the Q0 decision in the brainstorm convo.

**Confidence:** Medium-high on the model layer. The cell-class taxonomy is grounded in the v2 TSV's `cell_type` distribution; the `(row_id, axis)` keying is locked by user via AskUserQuestion; the separate `models_v2/` module location is locked by user; the wrapper-fields approach to conditionality + provenance is grounded in iter-1 precedent. Lower confidence on the specialized cell shapes (`UpdateCadenceCell`, `TimeThresholdCell`, etc., for ~6 one-off rows) — those are settled in TDD against each specific row's `notes` column.

**Architecture:**

Module structure (all paths relative to `src/lobby_analysis/models_v2/`):
- `cells.py` — `CompendiumCell` ABC + per-type subclasses (`BinaryCell`, `DecimalCell`, etc.). Each subclass carries a `value` field of its type-specific shape plus the common wrapper fields (`cell_id`, `conditional`, `condition_text`, `confidence`, `provenance`).
- `cell_spec.py` — `CompendiumCellSpec(row_id, axis, expected_cell_class)` data class + `build_cell_spec_registry()` function that loads the v2 TSV and produces the canonical 186-cell roster mapping each (row_id, axis) tuple to its expected `CompendiumCell` subclass.
- `extraction.py` — `StateVintageExtraction(state, vintage, run_id, cells)` container + `ExtractionRun(run_id, model_version, prompt_sha, started_at)` provenance wrapper.
- `provenance.py` — `EvidenceSpan(section_reference, artifact_path, quoted_span, url)` citation pointer.
- `enum_domains.py` — Per-row enum domain registries for `EnumCell` / `EnumSetCell` rows. Populated incrementally; rows whose enum domain isn't yet specified produce a `EnumCell` that accepts any string (validation against the registry happens once the domain is filled in).
- `__init__.py` — public exports.

Module is parallel to v1.1 at `src/lobby_analysis/models/` (per user-confirmed Q4 decision). v1.1 stays UNTOUCHED so `cmd_build_smr`, `smr_projection`, `tests/test_compendium_loader.py`, `tests/test_smr_projection.py` keep working.

**Branch:** `extraction-harness-brainstorm` (worktree `.worktrees/extraction-harness-brainstorm/`).

**Tech Stack:** Python 3.12, Pydantic 2.x (`pydantic>=2.8` already in `pyproject.toml`), pytest, ruff. Anthropic SDK is **not** added by this plan — pure-data only.

---

## Testing Plan

This is the testing-shaped section — written first, before implementation, per TDD.

I will add unit tests in `tests/test_models_v2_cells.py` that:

- Construct each `CompendiumCell` subclass with valid type-conforming values and assert the constructed instance has the expected `value` attribute. (Tests `BinaryCell(value=True)`, `BinaryCell(value=False)`, `DecimalCell(value=Decimal("200"))`, `DecimalCell(value=None)` for `Optional`, `GradedIntCell(value=0)`, `GradedIntCell(value=25)`, `GradedIntCell(value=100)`, etc.)
- Construct each subclass with **invalid** values and assert Pydantic raises `ValidationError`. Concrete invalid cases: `BinaryCell(value="yes")` (wrong type); `DecimalCell(value=-Decimal("1"))` (negative threshold — out of range per the row's semantic); `GradedIntCell(value=30)` (not on the 25-step grid); `GradedIntCell(value=125)` (out of 0-100 bounds); `BoundedIntCell(value=16)` (out of 0-15 bounds for `lobbying_search_simultaneous_multicriteria_capability`).
- Construct each subclass with the **wrapper fields** set and verify they propagate: `BinaryCell(value=True, conditional=True, condition_text="if expenditures exceed $200/quarter", confidence="high")` and assert all four read back. Then construct with conditional defaults and verify `conditional=False`, `condition_text=None`, `confidence=None`, `provenance=None`.

I will add unit tests in `tests/test_models_v2_cell_spec.py` that:

- Call `build_cell_spec_registry()` against the real `compendium/disclosure_side_compendium_items_v2.tsv` and assert the returned mapping has exactly **186 entries** (181 row_ids + the 5 legal+practical doublings).
- Assert every legal-only TSV row maps to exactly `(row_id, "legal")` in the registry.
- Assert every practical-only TSV row maps to exactly `(row_id, "practical")` in the registry.
- Assert each of the 5 legal+practical TSV rows maps to BOTH `(row_id, "legal")` AND `(row_id, "practical")` with the cell classes specified by the row's `cell_type` column (e.g., `lobbyist_registration_required` → `BinaryCell` at "legal" + `GradedIntCell` at "practical").
- Assert no orphan `cell_type` values — every distinct `cell_type` in the TSV has a known `CompendiumCell` subclass.
- Assert the 8-rubric most-validated row `lobbyist_spending_report_includes_total_compensation` maps to `BinaryCell` at axis `"legal"` (sanity check on the cross-rubric anchor row).

I will add unit tests in `tests/test_models_v2_extraction.py` that:

- Construct a `StateVintageExtraction(state="OH", vintage=2025, run_id="test_run_001", cells={})` and assert it validates with an empty `cells` dict.
- Populate `cells` with a `(row_id, axis)` → `CompendiumCell` instance and verify it round-trips.
- Construct a `StateVintageExtraction` with a cell whose key doesn't match its own `cell_id` and assert a validation error (key/cell_id consistency check).
- Construct an `ExtractionRun` with sha hash + timestamp + model_version and verify serialization round-trips via `model_dump_json()` / `model_validate_json()`.

I will add a unit test in `tests/test_models_v2_provenance.py` that constructs an `EvidenceSpan` with all fields set and one with only the required field, and asserts both validate.

I will **NOT** write tests that:
- Simply assert a dataclass has certain attribute names (those test that Pydantic typing works, not that our behavior is correct).
- Mock `load_v2_compendium()` — the cell-spec registry tests must run against the **real** TSV so a TSV change is caught as a test failure.
- Test pydantic's own validation logic (e.g., "test that `int` field rejects strings" — that's testing the framework, not us). Tests target our row-semantic rules: GradedIntCell's 25-step grid, BoundedIntCell's 0-15 range, the cell_id↔key consistency rule, the 186-entry registry size.

**Iteration unit:** Each cell subclass + its targeted tests is one TDD cycle. Bulk-add via a parametrized test where the test parameters are the v2 TSV rows themselves — given the registry, parametrize "for each (row_id, axis, expected_class), construct an instance with a valid value and assert it validates." That covers all 186 cells in one parametrized sweep.

NOTE: I will write *all* tests before I add any implementation behavior.

---

## Steps

### Phase 0 — Scaffolding (15-30 min)

1. Read this plan, the originating brainstorm convo, and the plan sketch's antecedent agenda once more.
2. `git -C .worktrees/extraction-harness-brainstorm status` to confirm clean tree (worktree was merged with main mid-brainstorm; v2 TSV should be at `compendium/disclosure_side_compendium_items_v2.tsv`; `load_v2_compendium()` should be importable).
3. Run `uv run pytest -x` to confirm baseline test suite is green before any new code lands. Capture the pass/skip count.
4. Create the `src/lobby_analysis/models_v2/` directory with empty `__init__.py`. Commit "scaffolding: empty models_v2 module" so future blame is informative.

### Phase 1 — `EvidenceSpan` provenance struct (smallest, foundational)

1. Write the failing test `tests/test_models_v2_provenance.py` (one test exercising the model's field shape + optional/required semantics).
2. Run it. Confirm it fails (ModuleNotFoundError for `lobby_analysis.models_v2.provenance`).
3. Implement `src/lobby_analysis/models_v2/provenance.py` with `EvidenceSpan` as a Pydantic `BaseModel`. Fields: `section_reference: str` (required), `artifact_path: str | None = None`, `quoted_span: str | None = None` (with a max-length validator at 200 chars), `url: str | None = None`.
4. Run the test; confirm it passes.
5. Commit "models_v2: EvidenceSpan provenance struct".

### Phase 2 — `CompendiumCell` ABC + first cell subclass `BinaryCell`

1. Write failing tests in `tests/test_models_v2_cells.py` covering:
   - `BinaryCell(value=True)` and `BinaryCell(value=False)` construct with `conditional=False`, `condition_text=None`, `confidence=None`, `provenance=None`.
   - `BinaryCell(value="yes")` raises `ValidationError`.
   - `BinaryCell(value=True, conditional=True, condition_text="if expenditures ≥ $200/quarter", confidence="high", provenance=EvidenceSpan(section_reference="§101.70(B)(1)"))` constructs and all fields read back.
   - `BinaryCell` instances have `cell_id: tuple[str, str]` set to the (row_id, axis) tuple they were constructed with; constructing without `cell_id` raises `ValidationError`.
2. Run tests; confirm they fail (no `BinaryCell`).
3. Implement `src/lobby_analysis/models_v2/cells.py`:
   - `CompendiumCell` Pydantic abstract base with common fields: `cell_id: tuple[str, str]`, `conditional: bool = False`, `condition_text: str | None = None`, `confidence: Literal["high", "medium", "low"] | None = None`, `provenance: EvidenceSpan | None = None`. Use `model_config = ConfigDict(frozen=True)` so cells are immutable once constructed (matches iter-1's temp-0 stamped-output discipline).
   - `BinaryCell(CompendiumCell)`: adds `value: bool`.
4. Run tests; confirm they pass.
5. Commit "models_v2: CompendiumCell ABC + BinaryCell".

### Phase 3 — Numeric cell subclasses (`DecimalCell`, `IntCell`, `FloatCell`, `GradedIntCell`, `BoundedIntCell`)

1. Write failing tests in `tests/test_models_v2_cells.py` covering each subclass with valid + invalid values:
   - `DecimalCell`: `value=Decimal("200")`, `value=Decimal("0")`, `value=None` (Optional); reject `value="200"` (string), `value=-Decimal("1")` (negative threshold).
   - `IntCell`: `value=10`, `value=None`; reject `value=10.5`, `value="ten"`.
   - `FloatCell`: `value=0.25`, `value=None`; reject `value="0.25"`.
   - `GradedIntCell`: `value=0`, `value=25`, `value=50`, `value=75`, `value=100`; reject `value=30` (off grid), `value=125` (out of range), `value=-25`.
   - `BoundedIntCell`: `value=0`, `value=8`, `value=15`; reject `value=16`, `value=-1`.
2. Run tests; confirm failures.
3. Implement each subclass in `cells.py` with a `value` field of the right type + Pydantic `field_validator` decorators for the grid/range rules.
4. Run tests; confirm they pass.
5. Commit "models_v2: numeric cell subclasses".

### Phase 4 — Enum cell subclasses + `FreeTextCell` + specialized cells

1. For each, write failing tests then implement. Specialized cells map 1:1 to specific v2 TSV rows; refer to the row's `notes` column for the intended struct shape:
   - `EnumCell(value: str)` — parameterized via Pydantic generic or a per-row `enum_domain: frozenset[str]` field that validators check against. Domain registry lives in `enum_domains.py` (start empty; populate per row as needed).
   - `EnumSetCell(value: frozenset[str])` — set of values from a registered enum domain.
   - `FreeTextCell(value: str)` — 2 rows (`lobbyist_spending_report_cadence_other_specification`, `principal_spending_report_cadence_other_specification`). Bound to `max_length=500` to prevent unbounded extraction.
   - `UpdateCadenceCell` — 1 row (`lobbyist_directory_update_cadence`). Per v2 TSV `notes` lookup at implementation time; likely an enum {"daily", "weekly", "monthly", "quarterly", "annually", "ad_hoc"}.
   - `TimeThresholdCell` — 1 row (`lobbyist_registration_threshold_time_percent`). Likely `value: int | None` + `unit: Literal["hours", "days", "percent_of_time"]`.
   - `TimeSpentCell` — 1 row. Per `notes`.
   - `SectorClassificationCell` — 1 row (`lobbyist_reg_form_includes_lobbyist_sector`). Per `notes`; likely `value: frozenset[str]` over a NAICS-or-similar enum.
   - `CountWithFTECell` — 1 row (`lobbyist_or_principal_spending_report_includes_lobbyist_count_total_and_FTE`). Per `notes`; likely `count: int | None`, `fte: float | None`.
   - `EnumSetWithAmountsCell` — 1 row (`consultant_lobbyist_report_includes_income_by_source_type`). Per `notes`; likely `value: frozenset[str]` + `amounts: dict[str, Decimal]`.
2. Commit each specialized cell as its own micro-commit so the history reads as "one cell per commit."

### Phase 5 — `CompendiumCellSpec` registry + the 186-cell roster

1. Write failing tests in `tests/test_models_v2_cell_spec.py`:
   - `build_cell_spec_registry()` returns a `dict[tuple[str, str], type[CompendiumCell]]` with exactly **186 entries** (assert via `len(registry) == 186`).
   - For each `axis="legal"` TSV row, assert `(row_id, "legal")` is in the registry and maps to the right subclass per the row's `cell_type` column.
   - For each `axis="practical"` TSV row, assert `(row_id, "practical")` is in the registry and the right subclass.
   - For each `axis="legal+practical"` TSV row, assert BOTH `(row_id, "legal")` AND `(row_id, "practical")` are in the registry and map to the right subclasses for each side.
   - Assert `lobbyist_spending_report_includes_total_compensation` → `BinaryCell` at axis `"legal"` (anchor).
   - Assert no `cell_type` from the TSV is orphaned (every distinct value has a parsing rule).
2. Run tests; confirm failures (ModuleNotFoundError or registry mismatch).
3. Implement `src/lobby_analysis/models_v2/cell_spec.py`:
   - `@dataclass(frozen=True) class CompendiumCellSpec: row_id: str; axis: Literal["legal", "practical"]; expected_cell_class: type[CompendiumCell]`.
   - `_CELL_TYPE_PARSER` private dict: `{"binary": BinaryCell, "typed Optional[Decimal]": DecimalCell, ...}`. For the 5 combined-axis rows, parse the `cell_type` string with a small split function (split on `" + "`, parse each half's `"(legal)"` / `"(practical)"` suffix).
   - `build_cell_spec_registry(tsv_path=DEFAULT_COMPENDIUM_V2_TSV) -> dict[tuple[str, str], CompendiumCellSpec]`. Internally calls `load_v2_compendium()`, walks each row, parses `cell_type` + `axis`, emits 1 or 2 entries per row.
4. Run tests; confirm they pass.
5. Commit "models_v2: CompendiumCellSpec + 186-cell registry".

### Phase 6 — `StateVintageExtraction` container + `ExtractionRun`

1. Write failing tests in `tests/test_models_v2_extraction.py`:
   - `StateVintageExtraction(state="OH", vintage=2025, run_id="r1", cells={})` validates.
   - Populate `cells[("lobbyist_spending_report_includes_total_compensation", "legal")] = BinaryCell(cell_id=(..., "legal"), value=True)`; assert read-back.
   - Construct with a cell whose `cell_id` mismatches its dict key; assert `ValidationError`.
   - `ExtractionRun(run_id="r1", model_version="claude-opus-4-7", prompt_sha="abc123", started_at=datetime.now(timezone.utc))` validates and round-trips via `model_dump_json()` / `model_validate_json()`.
2. Run tests; confirm failures.
3. Implement `src/lobby_analysis/models_v2/extraction.py`:
   - `class StateVintageExtraction(BaseModel)`: `state: str` (USPS 2-letter), `vintage: int` (4-digit year), `run_id: str`, `cells: dict[tuple[str, str], CompendiumCell]`. Add a `model_validator(mode="after")` that walks `cells` and asserts each cell's `cell_id` matches its dict key.
   - `class ExtractionRun(BaseModel)`: `run_id: str`, `model_version: str`, `prompt_sha: str`, `started_at: datetime`, `completed_at: datetime | None = None`.
4. Run tests; confirm they pass.
5. Commit "models_v2: StateVintageExtraction container + ExtractionRun provenance".

### Phase 7 — `__init__.py` exports + `load_v2_compendium_typed()` wrapper

1. Write failing tests in `tests/test_models_v2_init.py` and `tests/test_compendium_loader_v2_typed.py`:
   - `from lobby_analysis.models_v2 import CompendiumCell, BinaryCell, ..., StateVintageExtraction, CompendiumCellSpec, build_cell_spec_registry` succeeds.
   - `load_v2_compendium_typed()` (added to `src/lobby_analysis/compendium_loader.py`) returns a `list[CompendiumCellSpec]` of length 186.
2. Run; confirm failures.
3. Implement `__init__.py` with explicit re-exports; add `load_v2_compendium_typed()` to `compendium_loader.py` as a thin wrapper around `build_cell_spec_registry()` that returns its `.values()` as a list.
4. Run tests; confirm they pass.
5. Commit "models_v2: __init__ exports + load_v2_compendium_typed".

### Phase 8 — Suite-wide green check + lint

1. Run `uv run pytest` and confirm full suite is green (baseline from Phase 0 + all new tests).
2. Run `uv run ruff check src/lobby_analysis/models_v2/ tests/test_models_v2_*.py tests/test_compendium_loader_v2_typed.py` and fix any lint findings.
3. Run `uv run ruff format src/lobby_analysis/models_v2/ tests/test_models_v2_*.py tests/test_compendium_loader_v2_typed.py`.
4. Commit "models_v2: lint + format pass" if anything changed; otherwise skip.

### Phase 9 — RESEARCH_LOG + STATUS.md updates + finish-convo

1. Update `docs/active/extraction-harness-brainstorm/RESEARCH_LOG.md` with the implementation-session entry pointing at the convo + plan + commit SHAs.
2. Update `STATUS.md` row for `extraction-harness-brainstorm` (only this row — don't touch others per multi-committer guidance).
3. Run finish-convo to push.

---

## Out of scope for this plan

These are explicitly NOT in this plan; downstream plans pick them up:
- The chunk-grouping function (Q1's mechanic — chunking the 186-cell roster into prompt-sized groups). Builds on `CompendiumCellSpec` registry; needs the registry to exist first.
- The brief-writer module for the LLM-calling harness. Builds on cells + chunks.
- The cross-reference retrieval agent's v2 generalization. Builds on the existing `src/scoring/retrieval_agent_prompt.md`.
- The scorer prompt's rewrite (rubric-agnostic, v2-compendium-shaped). Builds on cells + chunks + retrieval bundle.
- Anthropic SDK wiring. Defer until there's a concrete reason to break the subagent-dispatch pattern.

---

## Edge cases the implementing agent must handle

- **Decimal vs float for threshold-dollar rows.** Use `Decimal`, not `float`. Currency precision matters. The v2 TSV's `cell_type` column says `typed Optional[Decimal]` explicitly for these rows.
- **`None` vs missing.** A cell with `value=None` (e.g., `DecimalCell(value=None)`) is semantically "extraction ran and found no threshold mentioned" — different from "extraction hasn't been attempted." The latter is represented by the absence of a `(row_id, axis)` key from `StateVintageExtraction.cells`. Both states must be expressible; tests should cover both.
- **The `path_b_unvalidated` row.** v2 TSV has 1 row with `status="path_b_unvalidated"` (OS-1, an OpenSecrets row added during the row-freeze). It still appears in the 181-row count. The cell spec registry should include it; downstream extraction code may want to gate on `status` (skip path-b rows) but that's not this plan's call.
- **The 5 legal+practical rows.** Test the split-parsing of `cell_type` strings explicitly: `"binary (legal) + typed int 0-100 step 25 (practical)"` must yield two `CompendiumCellSpec` entries, one with `BinaryCell` at `axis="legal"` and one with `GradedIntCell` at `axis="practical"`. Don't hard-code these 5 rows — write a general parser; otherwise a future combined-axis row addition silently corrupts the registry.
- **`law_includes_materiality_test` is a top-level binary row.** Different from the per-cell `conditional` flag. Tests should construct a cell for this row AND a separate cell with `conditional=True` to confirm they're orthogonal.
- **Pydantic frozen + dict serialization.** `frozen=True` cells must still serialize via `model_dump()`. Make sure `cell_id: tuple[str, str]` serializes as a list in JSON and round-trips correctly.
- **Enum cells with unfilled enum domains.** A row whose enum domain hasn't been specified in `enum_domains.py` yet: `EnumCell` should validate any non-empty string, with a comment noting the domain is pending. Don't fail extraction for these — just don't enforce membership yet.
- **`GradedIntCell` semantic.** The value is on the 0-25-50-75-100 grid representing FOCAL-style 0% / 25% / 50% / 75% / 100% gradings of practical-side observables. Validator: `value % 25 == 0 and 0 <= value <= 100`. Don't represent this as a float fraction or a Literal — keep it as an int with a range validator so downstream arithmetic is exact.

---

## Risks + mitigations

- **Risk: I parse a `cell_type` string incorrectly and silently produce wrong subclasses for some rows.** *Mitigation:* the registry-size test (`assert len(registry) == 186`) catches dropped rows; the per-cell-type orphan test catches missing parsers; the anchor-row test catches the most-validated row.
- **Risk: The 6 specialized cell shapes (`UpdateCadenceCell`, `TimeThresholdCell`, etc.) get rushed and the wrong struct shape locks Phase C against the wrong type.** *Mitigation:* for each specialized cell, before implementing, **read the v2 TSV `notes` column for that specific row** to confirm intended shape. If `notes` is empty, surface the ambiguity to the user before TDD'ing the cell.
- **Risk: Pydantic `frozen=True` interacts poorly with subclass field addition.** *Mitigation:* model_config is set on the ABC and inherited; subclasses just add fields. Test round-trip serialization to confirm.

---

## How TDD discipline is enforced

- Every test file added before the corresponding module file.
- Every commit is either "test: X (fails)" then "implement: X (passes)" — read git log on completion to verify the pattern. If a commit lands implementation without a preceding red-test commit, that's a TDD violation and should be flagged.
- The `uv run pytest -x` failure between Phase 0 and Phase 1 is recorded in the convo summary so future agents see the discipline was followed.

---

**Testing Details.** Tests target the row-semantic rules (GradedIntCell 0-100 step 25, BoundedIntCell 0-15, registry has exactly 186 entries, every `cell_type` has a parser, cell_id matches its dict key) — NOT Pydantic's own validation framework. Tests run against the **real** `compendium/disclosure_side_compendium_items_v2.tsv`, not a fixture, so a TSV change propagates as a test failure. No mocks of `load_v2_compendium()`.

**Implementation Details.**

- All new code in `src/lobby_analysis/models_v2/`; v1.1 at `src/lobby_analysis/models/` is UNTOUCHED.
- All new tests in `tests/test_models_v2_*.py` so the new tests are visually grouped.
- Pydantic 2.x; use `BaseModel`, `ConfigDict(frozen=True)`, `field_validator`, `model_validator(mode="after")` patterns.
- `CompendiumCell` is an abstract base with the common fields; subclasses inherit and add `value`. Don't use ABC's `abc.ABCMeta` — Pydantic's own pattern (instantiation only at concrete subclasses by convention) suffices.
- `Literal` types for `axis: Literal["legal", "practical"]` and `confidence: Literal["high", "medium", "low"]`.
- `frozen=True` model_config so cells are immutable; lines up with iter-1's stamped-output discipline.
- Don't add `Anthropic` SDK dependency.
- Worktree path is `.worktrees/extraction-harness-brainstorm/`; absolute paths in commands use that prefix.

**What could change.**

- **Specialized cell shapes** (the 6 one-off rows) are the highest-uncertainty piece; the v2 TSV's `notes` column is the source of truth and may force different struct shapes than this plan sketches.
- **`EvidenceSpan` field shape** — `section_reference` might end up as a structured `(title, chapter, section)` tuple instead of a string, once the LLM-calling harness's actual emissions are seen. Plan starts with `str`; revisit when retrieval bundle structure is known.
- **`law_includes_materiality_test` row's semantic** could shift if the brainstorm convo's read of it is wrong. If so, fix the test, not the model.
- **Phase C's adoption pace.** If Phase C wants typed models immediately, accelerate `load_v2_compendium_typed()` (Phase 7 here) to land earlier. If they're happy with raw `load_v2_compendium()` for weeks, this branch's downstream LLM work (chunk-grouping → brief writer → harness) consumes the typed models in parallel.
- **Frozen vs mutable cells.** If iter-2-style "update confidence after second-pass review" turns out to be a real workflow, drop `frozen=True`. For now, frozen is the safer default (iter-1's stamped-output discipline).

**Questions.**

- **Is the `(state, vintage, run_id)` tuple unique enough for `StateVintageExtraction`?** Or should `ExtractionRun` be embedded inside `StateVintageExtraction` rather than parallel? Sketch has them parallel (one `ExtractionRun` ID per `StateVintageExtraction`); could be embedded as `StateVintageExtraction.run: ExtractionRun`. Decide during TDD.
- **Should `enum_domains.py` registries be loaded at import time or lazily?** Sketch leans import-time (Python module load reads them) but lazy loading allows tests to inject test-only enum domains. Decide during TDD.
- **Does Phase C want `cell_id` as `tuple[str, str]` or `tuple[str, Literal["legal", "practical"]]`?** The latter is stricter but adds Literal overhead everywhere. Plan uses the former; revisit if Phase C feedback says otherwise.
- **The `compendium/README.md` projection-input phrasing (`{row_id: typed_value}`) is now inaccurate** given the (row_id, axis) decision. Should this plan update the README in a follow-up commit, or leave it to the brainstorm-convo's coordination items section? Brainstorm convo flagged it; not blocking this plan.

---

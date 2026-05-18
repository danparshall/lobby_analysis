"""Audit: row names referenced in projection modules must exist in v2 TSV.

The row-ID renamer (``tools/v2_update_names.py``) handles OLD→NEW renames
but cannot detect references to **merged-away** rows. This audit catches
that class of silent drift across all projection modules in
``src/lobby_analysis/projections/``.

Surfaced 2026-05-18 (GH #17): CPI 2015 ``project_ind_201`` read
``lobbyist_spending_report_includes_compensation`` (merged into
``lobbyist_spending_report_includes_total_compensation`` by D1/D2 of the
2026-05-13 row-freeze); ``project_ind_200`` read
``registration_timeliness_after_first_lobbying_activity`` (merged into
two-axis ``registration_deadline_days_after_first_lobbying`` by D11).
Both bugs were invisible because test fixtures used the same wrong names.

Detection is **syntactic**, not shape-based: row-name string literals are
identified by the AST positions they occupy, not by snake_case shape.
This rejects lookalike enum values (e.g., ``"more_frequent_than_annual"``
used in a ``cadence in (...)`` comparison) that would be false positives
under shape detection.

Scope is ``src/lobby_analysis/projections/*.py``. Test-side fixture drift
is a separate problem class — when a test fixture references a row absent
from v2 but the projection correctly references it, projection behavior
diverges between live runs and tests. The current PR fixed the two
fixture-drift instances surfaced; a dedicated test-side audit can be
added later if more surface.
"""

from __future__ import annotations

import ast
from pathlib import Path

from lobby_analysis.compendium_loader import load_v2_compendium

PROJECTIONS_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "lobby_analysis"
    / "projections"
)


# Accessor helpers defined in each projection module that take
# ``(cells, row_id, ...)``. Second positional arg is a row name.
_CELL_ACCESSORS: frozenset[str] = frozenset({"_legal", "_practical"})

# Module-level constants whose Name appears as the third element of a
# tuple-register; presence identifies the tuple as a row-name register.
_ROW_AXIS_CONSTS: frozenset[str] = frozenset({"_LEGAL", "_PRACTICAL"})


class _RowNameCollector(ast.NodeVisitor):
    """Collect row-name string literals from a projection module's AST.

    Detects four reference patterns:

    1. Call site: ``_legal(cells, "row")`` / ``_practical(cells, "row")``
       — second positional arg as ``Constant[str]`` or as a ``Name``
       resolving to a module-level ``Final[str]`` row constant.
    2. Subscript: ``cells["row"]`` / ``cells[ROW_CONST]``.
    3. Tuple-register: ``("ITEM_ID", "row", _LEGAL | _PRACTICAL)`` — any
       3-tuple whose third element is a ``Name`` from ``_ROW_AXIS_CONSTS``;
       second element is the row name.
    4. Module-level constants: ``_FOO_ROW: Final[str] = "row"`` and
       ``_FOO_ROWS: Final[tuple[str, ...]] = ("a", "b", ...)`` are
       harvested directly. This catches indirect references via
       ``for row_id in _FOO_ROWS: _legal(cells, row_id)``.
    """

    def __init__(self) -> None:
        self.found: set[str] = set()
        self._module_final_strs: dict[str, str] = {}

    def collect(self, module_ast: ast.Module) -> set[str]:
        """Run both passes and return the set of referenced row names."""
        self._harvest_module_consts(module_ast)
        self.visit(module_ast)
        return self.found

    # ---------- Pass 1: module-level row-name constants ----------

    def _harvest_module_consts(self, module_ast: ast.Module) -> None:
        for stmt in module_ast.body:
            target_name, rhs = self._unpack_assignment(stmt)
            if target_name is None or rhs is None:
                continue
            if not self._is_row_constant_name(target_name):
                continue
            if isinstance(rhs, ast.Constant) and isinstance(rhs.value, str):
                self._module_final_strs[target_name] = rhs.value
                self.found.add(rhs.value)
            elif isinstance(rhs, (ast.Tuple, ast.List)):
                for elt in rhs.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        self.found.add(elt.value)

    @staticmethod
    def _unpack_assignment(stmt: ast.stmt) -> tuple[str | None, ast.expr | None]:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            return stmt.target.id, stmt.value
        if (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
        ):
            return stmt.targets[0].id, stmt.value
        return None, None

    @staticmethod
    def _is_row_constant_name(name: str) -> bool:
        """Module-level constant naming convention for row-name holders."""
        return name.endswith("_ROW") or name.endswith("_ROWS")

    # ---------- Pass 2: syntactic call-site detection ----------

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in _CELL_ACCESSORS
            and len(node.args) >= 2
        ):
            self._absorb_row_expr(node.args[1])
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == "cells":
            self._absorb_row_expr(node.slice)
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        # Tuple-register: ("ITEM_ID", "row_name", _LEGAL | _PRACTICAL)
        if (
            len(node.elts) == 3
            and isinstance(node.elts[0], ast.Constant)
            and isinstance(node.elts[0].value, str)
            and isinstance(node.elts[2], ast.Name)
            and node.elts[2].id in _ROW_AXIS_CONSTS
        ):
            self._absorb_row_expr(node.elts[1])
        self.generic_visit(node)

    def _absorb_row_expr(self, expr: ast.expr) -> None:
        """Add a row-name reference if ``expr`` is a string literal or a
        Name resolving to a harvested module-level ``Final[str]`` constant."""
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            self.found.add(expr.value)
        elif isinstance(expr, ast.Name) and expr.id in self._module_final_strs:
            self.found.add(self._module_final_strs[expr.id])


def _referenced_row_names(source: str) -> set[str]:
    return _RowNameCollector().collect(ast.parse(source))


def _is_synthetic_sentinel(row_name: str) -> bool:
    """Names starting with ``__`` are deliberate test-only sentinels, not v2 rows.

    Example: ``__ind_205_partial_credit_passthrough`` is a key the round-trip
    test injects to carry scorer-judgment partial credit through the projection;
    it is intentionally absent from v2. Real v2 row names never start with
    ``__`` (no v2 row name starts with an underscore at all).
    """
    return row_name.startswith("__")


def test_every_row_reference_in_projections_exists_in_v2_tsv():
    """Every row name referenced by a projection module must exist in v2 TSV.

    Catches references to rows merged away during the row-freeze. The
    renamer cannot detect these (it handles OLD→NEW renames but not
    MERGED→DROPPED).
    """
    valid_rows = {row["compendium_row_id"] for row in load_v2_compendium()}

    offenders: dict[str, list[str]] = {}
    for py_path in sorted(PROJECTIONS_DIR.glob("*.py")):
        if py_path.name == "__init__.py":
            continue
        refs = _referenced_row_names(py_path.read_text())
        bad = sorted(
            s for s in refs if s not in valid_rows and not _is_synthetic_sentinel(s)
        )
        if bad:
            offenders[py_path.name] = bad

    assert not offenders, (
        "projection modules reference row names absent from v2 TSV:\n"
        + "\n".join(
            f"  {fname}: {names}" for fname, names in sorted(offenders.items())
        )
    )

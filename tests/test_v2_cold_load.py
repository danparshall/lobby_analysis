"""Cold-load regression test for the v2 import graph.

Background: commit ``0979779`` (the EvidenceSpan migration on 2026-05-18)
shipped tight in line-count but introduced a structural import cycle that
the rest of the test suite couldn't catch — tests import lazily inside
their test functions, so the offending modules were always loaded after
the cycle had been broken by an earlier import. A fresh interpreter,
which is how scripts and orchestrators load these modules in real use,
hit the cycle on the first import.

This test invokes a fresh Python interpreter via ``subprocess`` so the
cold-load order matches what scripts actually do. If anyone re-introduces
a cycle into the import graph by moving a foundational type back inside a
package that pulls in the rest of the dependency tree, this test fails
where lazy-imported tests would not.
"""

from __future__ import annotations

import subprocess
import sys


def test_chunks_v2_loads_cold() -> None:
    """Cold-load entry point: ``chunks_v2.build_chunks`` must import cleanly.

    Regression: the EvidenceSpan migration in commit ``0979779`` made
    ``models_v2.cells`` import from ``retrieval_v2.models``, which (via
    ``retrieval_v2/__init__.py`` → ``brief_writer`` → ``chunks_v2``) closed
    a cycle. The fix relocates ``EvidenceSpan`` to ``models_v2.citations``
    so the foundational type no longer drags in the retrieval-agent module.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from lobby_analysis.chunks_v2 import build_chunks; build_chunks()",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"cold load failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_models_v2_cells_loads_cold() -> None:
    """Cold-loading ``models_v2.cells`` directly must not pull in ``retrieval_v2``.

    The structural fix is "``models_v2.cells`` imports ``EvidenceSpan`` from
    ``models_v2.citations``, not from ``retrieval_v2.models``." This test
    locks that in by asserting ``retrieval_v2`` is not in ``sys.modules``
    after loading ``models_v2.cells`` from a fresh interpreter.
    """
    code = (
        "import sys\n"
        "import lobby_analysis.models_v2.cells  # noqa: F401\n"
        "assert 'lobby_analysis.retrieval_v2' not in sys.modules, "
        "    sorted(m for m in sys.modules if m.startswith('lobby_analysis'))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"models_v2.cells inadvertently imports retrieval_v2:\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_retrieval_v2_evidence_span_back_compat() -> None:
    """``EvidenceSpan`` must remain importable from its historical locations.

    Existing call sites use::

        from lobby_analysis.retrieval_v2 import EvidenceSpan
        from lobby_analysis.retrieval_v2.models import EvidenceSpan

    Both paths must still resolve to the same class as the new canonical
    home in ``models_v2.citations``.
    """
    code = (
        "from lobby_analysis.retrieval_v2 import EvidenceSpan as A\n"
        "from lobby_analysis.retrieval_v2.models import EvidenceSpan as B\n"
        "from lobby_analysis.models_v2 import EvidenceSpan as C\n"
        "from lobby_analysis.models_v2.citations import EvidenceSpan as D\n"
        "assert A is B is C is D, 'EvidenceSpan identity mismatch'\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"EvidenceSpan back-compat re-exports broken:\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

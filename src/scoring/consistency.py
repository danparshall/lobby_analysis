"""Inter-run consistency analysis for temp-0 self-consistency checks.

Given N scored CSVs for the same (state, rubric) across N runs, compute per-item
agreement and per-rubric disagreement rate. Used by the orchestrator's
`analyze-consistency` subcommand for Phase 3 pilot + optional Phase 4 sampling.

A rubric with disagreement_rate > 0.10 is flagged for rubric-sharpening.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ItemAgreement:
    item_id: str
    unanimous: bool
    unable_disagreement: bool  # runs disagree on unable_to_evaluate
    score_values: list[str]  # normalized string repr per run
    unable_values: list[str]  # "true" / "false" per run


@dataclass
class ConsistencyReport:
    state: str
    rubric: str
    run_ids: list[str]
    n_items: int
    n_unanimous: int
    n_any_disagree: int
    n_unable_disagreement: int
    per_item: list[ItemAgreement]

    @property
    def disagreement_rate(self) -> float:
        if self.n_items == 0:
            return 0.0
        return self.n_any_disagree / self.n_items

    @property
    def flagged(self) -> bool:
        return self.disagreement_rate > 0.10

    def flagged_items(self) -> list[str]:
        return [a.item_id for a in self.per_item if not a.unanimous]


def csv_path(repo_root: Path, state: str, snapshot_date: str, run_id: str, rubric: str) -> Path:
    return repo_root / "data" / "scores" / state / snapshot_date / run_id / f"{rubric}.csv"


def _norm(row: dict) -> tuple[str, str]:
    unable = (row.get("unable_to_evaluate") or "").strip().lower()
    unable_flag = "true" if unable == "true" else "false"
    score = (row.get("score") or "").strip()
    return unable_flag, score


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def compute_consistency(
    repo_root: Path,
    state: str,
    rubric: str,
    run_ids: list[str],
    snapshot_date: str,
) -> ConsistencyReport:
    rows_by_run: dict[str, list[dict]] = {}
    for rid in run_ids:
        rows = _load_rows(csv_path(repo_root, state, snapshot_date, rid, rubric))
        if rows:
            rows_by_run[rid] = rows
    available = list(rows_by_run.keys())
    if len(available) < 2:
        return ConsistencyReport(
            state=state,
            rubric=rubric,
            run_ids=available,
            n_items=0,
            n_unanimous=0,
            n_any_disagree=0,
            n_unable_disagreement=0,
            per_item=[],
        )
    item_ids = [r["item_id"] for r in rows_by_run[available[0]]]
    for rid in available[1:]:
        other = [r["item_id"] for r in rows_by_run[rid]]
        if other != item_ids:
            raise ValueError(
                f"item_id order mismatch: {available[0]} vs {rid} (state={state}, rubric={rubric})"
            )
    by_item = {rid: {r["item_id"]: r for r in rows_by_run[rid]} for rid in available}
    per_item: list[ItemAgreement] = []
    n_unanimous = 0
    n_any_disagree = 0
    n_unable_disagreement = 0
    for iid in item_ids:
        keys = [_norm(by_item[rid][iid]) for rid in available]
        unable_vals = [k[0] for k in keys]
        score_vals = [k[1] for k in keys]
        unable_disagree = len(set(unable_vals)) > 1
        score_disagree = len(set(score_vals)) > 1 and not unable_disagree
        unanimous = not unable_disagree and len(set(score_vals)) == 1
        per_item.append(
            ItemAgreement(
                item_id=iid,
                unanimous=unanimous,
                unable_disagreement=unable_disagree,
                score_values=score_vals,
                unable_values=unable_vals,
            )
        )
        if unanimous:
            n_unanimous += 1
        else:
            n_any_disagree += 1
            if unable_disagree:
                n_unable_disagreement += 1
    return ConsistencyReport(
        state=state,
        rubric=rubric,
        run_ids=available,
        n_items=len(item_ids),
        n_unanimous=n_unanimous,
        n_any_disagree=n_any_disagree,
        n_unable_disagreement=n_unable_disagreement,
        per_item=per_item,
    )


def render_markdown(reports: list[ConsistencyReport]) -> str:
    lines = [
        "# Inter-run consistency report",
        "",
        "Per-rubric item-level disagreement across temp-0 runs.",
        "Rubric flagged if disagreement_rate > 10%.",
        "",
        "| state | rubric | runs | items | unanimous | disagree | unable-disagree | rate | flag |",
        "|-------|--------|-----:|------:|----------:|---------:|----------------:|-----:|------|",
    ]
    for rep in reports:
        if len(rep.run_ids) < 2:
            lines.append(
                f"| {rep.state} | {rep.rubric} | {len(rep.run_ids)} | — | — | — | — | — | insufficient data |"
            )
            continue
        lines.append(
            f"| {rep.state} | {rep.rubric} | {len(rep.run_ids)} | {rep.n_items} "
            f"| {rep.n_unanimous} | {rep.n_any_disagree} | {rep.n_unable_disagreement} "
            f"| {rep.disagreement_rate:.2%} | {'FLAGGED' if rep.flagged else 'ok'} |"
        )
    lines += ["", "## Flagged items (by state, rubric)", ""]
    any_flagged = False
    for rep in reports:
        if rep.flagged and rep.flagged_items():
            any_flagged = True
            lines.append(f"### {rep.state} / {rep.rubric} — {len(rep.flagged_items())} items")
            lines.append("")
            for a in rep.per_item:
                if a.unanimous:
                    continue
                details = []
                if a.unable_disagreement:
                    details.append(f"unable: {a.unable_values}")
                details.append(f"scores: {a.score_values}")
                lines.append(f"- `{a.item_id}` — " + "; ".join(details))
            lines.append("")
    if not any_flagged:
        lines.append("_None._")
    return "\n".join(lines) + "\n"

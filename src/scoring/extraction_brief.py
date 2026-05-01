"""v2 extraction-brief builder.

Inlines the state's statute bundle as a single string the subagent reads
end-to-end (no Read tool, no files-read sidecar). The brief has two parts:

- A stable bundle prefix (the inlined statute text + its manifest sha) that
  is identical across all chunks for a given (state, vintage), so prompt
  caching can amortize it across the four chunk dispatches.
- A variable suffix (chunk-specific row briefs + the v2 scorer prompt body)
  that is the only part written to disk per run.

`build_extraction_brief()` returns both. `reconstruct_brief()` rebuilds the
full brief from a saved suffix + the bundle dir, so the per-run artifact
stays small while the prompt itself is fully reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path

from lobby_analysis.compendium_loader import load_compendium
from lobby_analysis.models.compendium import CompendiumItem
from scoring.provenance import compute_bundle_manifest_sha as _compute_bundle_manifest_sha


# Re-exported for back-compat with callers that imported from extraction_brief.
compute_bundle_manifest_sha = _compute_bundle_manifest_sha


_CHUNK_DOMAIN_FILTERS: dict[str, frozenset[str]] = {
    "definitions": frozenset({"definitions"}),
    "registration": frozenset({"registration"}),
    "reporting": frozenset({"reporting"}),
    "contact_log": frozenset({"contact_log"}),
    "other": frozenset({"definitions", "financial", "revolving_door", "relationship"}),
}

VALID_CHUNKS: tuple[str, ...] = tuple(_CHUNK_DOMAIN_FILTERS)


def build_extraction_brief(
    *,
    state: str,
    vintage_year: int,
    chunk: str,
    bundle_dir: Path,
    compendium_csv: Path,
    scorer_prompt_path: Path,
    repo_root: Path,
) -> tuple[str, str]:
    """Render the full subagent brief and the variable suffix.

    Returns:
        (full_brief, suffix) — full_brief is what's sent to the subagent;
        suffix is what's saved to disk per run (bundle reconstructible by
        manifest sha).
    """
    if chunk not in _CHUNK_DOMAIN_FILTERS:
        raise ValueError(
            f"unknown chunk {chunk!r}; valid choices: {VALID_CHUNKS}"
        )

    domains = _CHUNK_DOMAIN_FILTERS[chunk]
    chunk_rows = [r for r in load_compendium(compendium_csv) if r.domain in domains]
    chunk_rows.sort(key=lambda r: r.id)

    artifacts = _load_sorted_artifacts(bundle_dir)
    bundle_manifest_sha = compute_bundle_manifest_sha(bundle_dir)

    bundle_prefix = _render_bundle_prefix(
        state=state,
        vintage_year=vintage_year,
        bundle_manifest_sha=bundle_manifest_sha,
        artifacts=artifacts,
        bundle_dir=bundle_dir,
    )
    suffix = _render_suffix(
        chunk=chunk,
        rows=chunk_rows,
        scorer_prompt_path=scorer_prompt_path,
        repo_root=repo_root,
    )

    return bundle_prefix + suffix, suffix


def reconstruct_brief(
    *,
    suffix_path: Path,
    bundle_dir: Path,
    bundle_manifest_sha: str,
    scorer_prompt_path: Path,
    repo_root: Path,
) -> str:
    """Rebuild the full brief from a saved suffix + the bundle on disk.

    Verifies the bundle's current manifest sha matches the recorded
    `bundle_manifest_sha`; raises ValueError if the bundle has drifted.
    """
    actual_sha = compute_bundle_manifest_sha(bundle_dir)
    if actual_sha != bundle_manifest_sha:
        raise ValueError(
            f"bundle manifest sha mismatch for {bundle_dir}: "
            f"expected {bundle_manifest_sha}, got {actual_sha}"
        )

    manifest = _read_manifest(bundle_dir)
    artifacts = _load_sorted_artifacts(bundle_dir)
    bundle_prefix = _render_bundle_prefix(
        state=manifest["state_abbr"],
        vintage_year=manifest["vintage_year"],
        bundle_manifest_sha=bundle_manifest_sha,
        artifacts=artifacts,
        bundle_dir=bundle_dir,
    )
    return bundle_prefix + suffix_path.read_text()


def _read_manifest(bundle_dir: Path) -> dict:
    return json.loads((bundle_dir / "manifest.json").read_text())


def _load_sorted_artifacts(bundle_dir: Path) -> list[dict]:
    manifest = _read_manifest(bundle_dir)
    return sorted(manifest["artifacts"], key=lambda a: a["local_path"])


def _render_bundle_prefix(
    *,
    state: str,
    vintage_year: int,
    bundle_manifest_sha: str,
    artifacts: list[dict],
    bundle_dir: Path,
) -> str:
    parts: list[str] = [
        "= STATE STATUTE BUNDLE =\n",
        f"State: {state}\n",
        f"Vintage year: {vintage_year}\n",
        f"Bundle manifest sha256: {bundle_manifest_sha}\n",
        f"Section count: {len(artifacts)}\n",
        "\n== Sections (inlined; no Read-tool fetch needed) ==\n\n",
    ]
    for art in artifacts:
        section_body = (bundle_dir / art["local_path"]).read_text()
        parts.append(f"-- {art['local_path']} --\n")
        parts.append(f"URL: {art['url']}\n")
        parts.append(f"Role: {art['role']}\n")
        parts.append(f"sha256: {art['sha256']}\n")
        parts.append("\n")
        parts.append(section_body)
        if not section_body.endswith("\n"):
            parts.append("\n")
        parts.append("\n")
    return "".join(parts)


def _render_suffix(
    *,
    chunk: str,
    rows: list[CompendiumItem],
    scorer_prompt_path: Path,
    repo_root: Path,
) -> str:
    try:
        prompt_rel = scorer_prompt_path.relative_to(repo_root)
    except ValueError:
        prompt_rel = scorer_prompt_path
    prompt_body = scorer_prompt_path.read_text()
    row_briefs = "\n".join(_format_row_brief(r) for r in rows)

    return (
        f"\n= COMPENDIUM CHUNK: {chunk} =\n"
        f"Rows in this chunk: {len(rows)}\n"
        f"Locked scorer prompt: {prompt_rel}\n"
        "\n== Compendium rows to extract ==\n\n"
        f"{row_briefs}\n"
        "\n== Locked scorer prompt v2 (verbatim) ==\n\n"
        f"{prompt_body}\n"
        "\n== Output reminder ==\n\n"
        "Emit a single JSON array of FieldRequirement v1.3 records — one or "
        "more records per compendium_row_id, per Rule 7's regime/registrant_role "
        "emission rule. Every record carries `condition_text`, `regime`, and "
        "`registrant_role` (use null when uniform). Status values: `required` / "
        "`not_required` / `not_addressed` / `required_conditional`. No preamble, "
        "no prose outside the JSON array.\n"
    )


def _format_row_brief(r: CompendiumItem) -> str:
    return (
        f"--- {r.id} ---\n"
        f"name: {r.name}\n"
        f"domain: {r.domain}\n"
        f"data_type: {r.data_type}\n"
        f"description: {r.description}\n"
        f"notes: {r.notes}\n"
    )

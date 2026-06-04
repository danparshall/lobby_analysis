"""Wide-pass population of `compendium/source_quotes.yaml` for the 164
v2-compendium rows not yet covered by the narrow pass (Commit 1 of plan
``docs/active/wi-tier1-direct-read/plans/20260604_wide_prompt_text_pass.md``).

For each unpopulated v2 row:

1. Look up the row's ``first_introduced_by`` projection doc.
2. Resolve the v2 row_id to its pre-freeze (v1) row_id via the rename rules
   from ``docs/historical/compendium-source-extracts/results/projections/
   20260513_row_freeze_decisions.md`` (D1-D8). The projection docs were
   written against v1 row_ids; the v2 TSV was canonicalized after the freeze.
3. Find the atomic-indicator block in the projection doc that mentions the
   resolved row_id in a ``**Compendium rows:**`` listing.
4. Extract the verbatim ``"…"`` from the block's ``**Source quote:**`` line
   and the citation parenthetical that follows.
5. Emit a YAML entry: ``source_quotes`` keyed by a heading-derived rubric
   reference; ``prompt`` is initially the verbatim quote alone (no
   decoration; the Ralph loop evolves it).

Two outlier rows are hand-encoded inline per plan step 19:

- ``lobbyist_filing_distinguishes_in_house_vs_contract_filer`` — LobbyView
  schema-coverage source (no quotable question; synthesize prompt).
- ``separate_registrations_for_lobbyists_and_clients`` — OpenSecrets-tabled
  doc line 48 (path-b unvalidated row).

Rows where the extractor cannot find a clean ``Source quote`` field are
written to a "surfaces" report rather than being silently fabricated. Per
plan step 20: surface to Dan; do not invent.

The script is idempotent: existing populated rows are preserved verbatim;
only missing rows are added. Re-runs after manual edits to YAML are safe.

After GREEN tests pass, this script moves to ``scripts/_completed/`` per the
pattern from ``scripts/_completed/migrate_prompts_to_yaml.py``.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


_WORKTREE = Path(__file__).resolve().parents[1]
_COMPENDIUM_TSV = _WORKTREE / "compendium" / "disclosure_side_compendium_items_v2.tsv"
_YAML_PATH = _WORKTREE / "compendium" / "source_quotes.yaml"
_PROJECTIONS_DIR = (
    _WORKTREE
    / "docs"
    / "historical"
    / "compendium-source-extracts"
    / "results"
    / "projections"
)


# ---------------------------------------------------------------------------
# Rename map: v2 row_id → list of candidate v1 row_ids to look up in the
# projection doc. The lookup tries each candidate in order; first match wins.
# Per ``20260513_row_freeze_decisions.md`` decisions D1-D8.
# ---------------------------------------------------------------------------


# Explicit v2 → v1 renames. Each maps to the row_id(s) used in the
# projection doc (which was written pre-freeze). Discovered during the
# wide-pass dry-run; each is a clean rename (not a lacking-Source-quote
# case).
#
# Source of each rename:
#   D1: v2 `lobbyist_spending_report_includes_total_compensation` → v1
#       `lobbyist_report_includes_direct_compensation` (PRI E2f_i — the
#       row's first_introduced_by per TSV).
#   D2: v2 `principal_spending_report_includes_compensation_paid_to_lobbyists`
#       → v1 `principal_report_includes_direct_compensation` (PRI E1f_i).
#   D4: v2 `lobbyist_filing_de_minimis_threshold_dollars` → v1
#       `materiality_threshold_financial_value` (PRI D1_present / D1_value).
#       (The D4 rule's mechanical replace `de_minimis_threshold_` →
#       `materiality_threshold_` missed the `_financial_value` suffix.)
#   Lobbyist-status threshold family (CPI #197 / Newmark def.time_standard):
#       v2 puts the cell name first
#       (`lobbyist_registration_threshold_X_units`) while CPI/Newmark v1
#       names put the threshold-substance first
#       (`X_threshold_for_lobbyist_registration`).
#   Itemization threshold: Sunlight uses `expenditure_itemization_*` v1;
#       v2 renames to `lobbyist_filing_itemization_*`.
#   FOCAL scope rename: v2 short `def_X` ↔ v1 long
#       `Y_definition_included_X_types`.
#   FOCAL openness.2: v1 plural `diaries`; v2 singular `diary`.
#   FOCAL relationships.2: v1 `principal_or_lobbyist_*`; v2 word-order
#       swap to `lobbyist_or_principal_*`.
_EXPLICIT_RENAMES: dict[str, list[str]] = {
    # D1 — compensation cluster merge.
    "lobbyist_spending_report_includes_total_compensation": [
        "lobbyist_report_includes_direct_compensation",  # PRI E2f_i
    ],
    # D2 — principal-side compensation merge.
    "principal_spending_report_includes_compensation_paid_to_lobbyists": [
        "principal_report_includes_direct_compensation",  # PRI E1f_i
    ],
    # D4 partial — financial_value suffix not picked up by mechanical rule.
    "lobbyist_filing_de_minimis_threshold_dollars": [
        "materiality_threshold_financial_value",  # PRI D1_present / D1_value
    ],
    # CPI #197 / Newmark def.time_standard — threshold family.
    "lobbyist_registration_threshold_compensation_dollars": [
        "compensation_threshold_for_lobbyist_registration",
    ],
    "lobbyist_registration_threshold_time_percent": [
        "time_threshold_for_lobbyist_registration",
    ],
    # Sunlight itemization threshold (Sunlight #3).
    "lobbyist_filing_itemization_de_minimis_threshold_dollars": [
        "expenditure_itemization_de_minimis_threshold_dollars",
    ],
    # FOCAL scope.4 / scope.1.
    "def_lobbying_activity_types": [
        "lobbying_definition_included_activity_types",
    ],
    "def_lobbyist_actor_types": [
        "lobbyist_definition_included_actor_types",
    ],
    # FOCAL openness.2 — plural diaries.
    "ministerial_diary_available_online": [
        "ministerial_diaries_available_online",
    ],
    # FOCAL relationships.2 — word-order swap.
    "lobbyist_or_principal_reg_form_includes_member_or_sponsor_names": [
        "principal_or_lobbyist_reg_form_includes_member_or_sponsor_names",
    ],
}


def _candidate_v1_ids(v2_row_id: str) -> list[str]:
    """Return ordered list of candidate row_ids to search the projection doc for.

    Strategy: always include the v2 row_id first (covers the post-freeze case
    where the projection doc happens to use the canonical name). Then apply
    the D1-D8 rename rules to produce v1 candidates.
    """
    candidates = [v2_row_id]

    # Explicit renames (D1/D2 merges + CPI/Newmark/Sunlight/FOCAL renames).
    if v2_row_id in _EXPLICIT_RENAMES:
        candidates.extend(_EXPLICIT_RENAMES[v2_row_id])

    # D3 — PRI E1/E2 prefix rename: lobbyist_spending_report_* → lobbyist_report_*
    # and same for principal_spending_report_* → principal_report_*.
    # Cadence-row variants too. We try the demoted prefix when the v2 row uses
    # the spending_report form.
    if "_spending_report_" in v2_row_id:
        candidates.append(v2_row_id.replace("_spending_report_", "_report_"))

    # D4 — filing-de-minimis threshold rename
    if v2_row_id.startswith("lobbyist_filing_de_minimis_threshold_"):
        candidates.append(
            v2_row_id.replace(
                "lobbyist_filing_de_minimis_threshold_",
                "materiality_threshold_",
            )
        )

    # D5 — compensation-broken-down rename
    if v2_row_id == "lobbyist_spending_report_includes_compensation_broken_down_by_payer":
        candidates.append(
            "lobbyist_spending_report_includes_compensation_broken_down_by_client"
        )
        # Combined with D3 — also try the pre-D3 form
        candidates.append(
            "lobbyist_report_includes_compensation_broken_down_by_client"
        )
        candidates.append(
            "lobbyist_report_includes_compensation_broken_down_by_payer"
        )

    # D6 — def_target staff split. Both new v2 rows look up the same v1 combined name.
    if v2_row_id in ("def_target_legislative_staff", "def_target_executive_staff"):
        candidates.append("def_target_legislative_or_executive_staff")

    # D8 — lobbyist_disclosure_includes_* → lobbyist_reg_form_includes_*
    if v2_row_id.startswith("lobbyist_reg_form_includes_"):
        candidates.append(
            v2_row_id.replace("lobbyist_reg_form_includes_", "lobbyist_disclosure_includes_")
        )

    return candidates


# ---------------------------------------------------------------------------
# Projection-doc parsing
# ---------------------------------------------------------------------------


_HEADER_RE = re.compile(r"^(#+)\s+(.*)$")
_COMPENDIUM_ROWS_RE = re.compile(r"\*\*Compendium rows[^:]*:\*\*")
_SOURCE_QUOTE_RE = re.compile(r"\*\*Source quote:\*\*")
_BACKTICKED_RE = re.compile(r"`([^`]+)`")
_OTHER_FIELD_RE = re.compile(r"^\s*-\s+\*\*(?!Compendium rows)([^:*]+?):\*\*")


@dataclass(frozen=True)
class BlockExtraction:
    """What we extracted from one atomic-indicator block in a projection doc."""

    heading: str
    row_ids: list[str]  # backticked tokens from all **Compendium rows*:** sub-lists
    source_quote: str | None  # the verbatim text between the FIRST `"…"` pair
    citation_paren: str | None  # the first `(…)` after the source quote


def parse_projection_doc(path: Path) -> list[BlockExtraction]:
    """Parse a projection-mapping doc into indicator blocks.

    A block is delimited by ANY heading line (``^#+ ``). For each block we
    collect:
    - heading text (most-recent header line)
    - all backticked tokens that appear inside ``**Compendium rows*:**`` sub-
      lists. The "sub-list" runs from a ``**Compendium rows*:**`` line until
      the next ``- **<other field>:**`` top-level bullet OR the end of the
      block.
    - the verbatim quote from the (first) ``**Source quote:**`` line.
    - the citation paren immediately following the quote.

    Heading levels are NOT respected: each header line closes the previous
    block. This is correct for our docs — PRI's ``####`` section headers
    (e.g., ``#### A. Who is required to register``) have no inline content,
    only nested ``#####`` items below. So splitting on every header gives the
    right granularity for ``#####`` atomic-item blocks AND for the ``####``
    blocks of other docs.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    blocks: list[BlockExtraction] = []

    current_heading: str | None = None
    current_lines: list[str] = []

    def _emit() -> None:
        if current_heading is None:
            return
        ext = _extract_from_block(current_heading, current_lines)
        # Only keep blocks that actually carry compendium-row + source quote
        # information; skip Section headers like "## Doc conventions".
        if ext.row_ids or ext.source_quote:
            blocks.append(ext)

    for line in lines:
        m = _HEADER_RE.match(line)
        if m is not None:
            _emit()
            current_heading = m.group(2).strip()
            current_lines = []
            continue
        current_lines.append(line)

    _emit()
    return blocks


def _extract_from_block(heading: str, block_lines: list[str]) -> BlockExtraction:
    """Extract row_ids, source quote, and citation from one block."""
    # State machine: walk lines, identify "Compendium rows sub-list" regions.
    # A sub-list starts on a line matching `_COMPENDIUM_ROWS_RE` and runs until
    # the next top-level bullet whose `**<field>:**` is NOT a Compendium-rows
    # variant. Continuation bullets (indented sub-bullets) are part of the
    # sub-list.
    row_ids: list[str] = []
    in_compendium_rows = False
    for line in block_lines:
        if _COMPENDIUM_ROWS_RE.search(line):
            in_compendium_rows = True
            # Also scan THIS line for backticked tokens (inline-format case).
            row_ids.extend(_BACKTICKED_RE.findall(line))
            continue
        if in_compendium_rows:
            # Check whether this line starts a different top-level bullet.
            if _OTHER_FIELD_RE.match(line):
                in_compendium_rows = False
                # Fall through to source-quote / citation handling below.
            else:
                row_ids.extend(_BACKTICKED_RE.findall(line))
                continue

    # Source quote: find the FIRST `**Source quote:**` line.
    source_quote: str | None = None
    citation_paren: str | None = None
    for line in block_lines:
        if _SOURCE_QUOTE_RE.search(line):
            quote, paren = _split_quote_and_citation(line)
            source_quote = quote
            citation_paren = paren
            break

    # De-duplicate row_ids while preserving order.
    seen: set[str] = set()
    unique_rows: list[str] = []
    for r in row_ids:
        if r not in seen:
            seen.add(r)
            unique_rows.append(r)

    return BlockExtraction(
        heading=heading,
        row_ids=unique_rows,
        source_quote=source_quote,
        citation_paren=citation_paren,
    )


_FIRST_QUOTE_RE = re.compile(r'"([^"]+)"')
_FIRST_PAREN_RE = re.compile(r"\(([^)]+)\)")


def _split_quote_and_citation(line: str) -> tuple[str | None, str | None]:
    """From a ``**Source quote:**`` line, return (quote, citation_paren).

    The line shape is ``- **Source quote:** "verbatim quote" (citation).``
    Sometimes the citation is more complex (FOCAL: ``"q" (FOCAL Table 3); P/N
    from Suppl Table 3: "x" (Suppl File 1 line N).``) — we take the FIRST
    quote and the FIRST parenthetical that follows it.
    """
    qm = _FIRST_QUOTE_RE.search(line)
    if qm is None:
        return None, None
    quote = qm.group(1)
    after = line[qm.end():]
    pm = _FIRST_PAREN_RE.search(after)
    citation = pm.group(1) if pm else None
    return quote, citation


# ---------------------------------------------------------------------------
# YAML key derivation
# ---------------------------------------------------------------------------


# Rubric prefix per projection doc filename.
_DOC_TO_RUBRIC: dict[str, str] = {
    "pri_2010_projection_mapping.md": "pri_2010",
    "cpi_2015_c11_projection_mapping.md": "cpi_2015",
    "focal_2024_projection_mapping.md": "focal_2024",
    "hiredguns_2007_projection_mapping.md": "hiredguns_2007",
    "newmark_2017_projection_mapping.md": "newmark_2017",
    "sunlight_2015_projection_mapping.md": "sunlight_2015",
    "lobbyview_schema_coverage.md": "lobbyview_2018",
    "_tabled/opensecrets_2022_tabled.md": "opensecrets_2022_tabled",
}


_HEADING_LEADING_SECTION_RE = re.compile(r"^([A-Za-z0-9._#§§\-]+?)[:\s—-]")
_HEADING_PUNCT_RE = re.compile(r"[^\w§#.]")


def _heading_slug(heading: str) -> str:
    """Derive a YAML-key-friendly slug from a heading line.

    Examples:
    - ``Q1: At least some lobbying data ...`` → ``Q1``
    - ``IND_196: Definition recognizes ...`` → ``IND_196``
    - ``focal_2024.scope.1 — Lobbyist definition ...`` → ``scope.1``
      (rubric prefix already known; strip it)
    - ``hg_2007.Q1 — Executive-branch ...`` → ``Q1``
    - ``newmark_2017.def.legislative_lobbying — ...`` → ``def_legislative_lobbying``
    - ``sunlight_2015.lobbyist_activity (4-tier, ...)`` → ``lobbyist_activity``
    - ``E2f_i: Required component of disclosure ...`` → ``E2f_i``
    - ``D1_present: Financial threshold exists ...`` → ``D1_present``
    """
    # Extract the leading identifier (before first ": " or " — " or end).
    # Walk char by char until we hit a sentinel that ends the identifier.
    sentinels = (":", " —", " -", " (", "  ")
    cut = len(heading)
    for sent in sentinels:
        idx = heading.find(sent)
        if 0 < idx < cut:
            cut = idx
    leading = heading[:cut].strip()

    # Strip rubric prefix if present (focal_2024.X, hg_2007.X, newmark_2017.X,
    # sunlight_2015.X).
    for prefix in (
        "focal_2024.",
        "hg_2007.",
        "newmark_2017.",
        "newmark_2005.",
        "opheim.",
        "sunlight_2015.",
    ):
        if leading.startswith(prefix):
            leading = leading[len(prefix):]
            break

    # Replace dots with underscores in the slug (e.g. scope.1 → scope_1) to
    # match the established narrow-pass key convention. § / # / _ preserved.
    leading = leading.replace(".", "_")

    return leading


def _build_yaml_key(rubric_prefix: str, heading: str) -> str:
    """Build a ``source_quotes`` YAML key from rubric + heading."""
    slug = _heading_slug(heading)
    if not slug:
        # Defensive fallback — shouldn't happen for valid headings.
        return rubric_prefix
    return f"{rubric_prefix}_{slug}"


# ---------------------------------------------------------------------------
# Outlier rows — plan step 19
# ---------------------------------------------------------------------------


_LOBBYVIEW_OUTLIER_ID = "lobbyist_filing_distinguishes_in_house_vs_contract_filer"
_OPENSECRETS_OUTLIER_ID = "separate_registrations_for_lobbyists_and_clients"


_OUTLIER_ENTRIES: dict[str, dict] = {
    _LOBBYVIEW_OUTLIER_ID: {
        "source_quotes": {
            "lobbyview_2018_schema_field_is_client_self_filer": (
                "LobbyView (Kim 2018) schema includes the field "
                "`is_client_self_filer`, capturing whether the registrant is "
                "the principal filing on their own behalf (in-house) vs. a "
                "contract lobbyist filing for a client. Promoted to compendium "
                "v2 per row-freeze decision D12 (LV-1 IN); no quotable question "
                "exists in the source paper — provenance is the schema-field "
                "origin."
            )
        },
        "prompt": (
            "Does the state's lobbyist registration filing distinguish "
            "in-house lobbyists (filing on their own behalf as the principal) "
            "from contract lobbyists (filing on behalf of a client / "
            "principal)?"
        ),
    },
    _OPENSECRETS_OUTLIER_ID: {
        "source_quotes": {
            "opensecrets_2022_tabled_candidate_1": (
                "the baseline score was three and states that require "
                "separate registrations for the lobbyists and clients were "
                "assigned a four"
            )
        },
        "prompt": (
            "Does the state require both the lobbyist AND the client / "
            "principal to file SEPARATE registration forms (each as an "
            "independent registrant), as opposed to a single combined form "
            "covering both parties?"
        ),
    },
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _read_tsv() -> list[dict[str, str]]:
    """Read the v2 compendium TSV as a list of dicts."""
    import csv

    with _COMPENDIUM_TSV.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader)


def _build_doc_indices() -> dict[str, list[BlockExtraction]]:
    """Parse every projection doc once; return ``{filename: blocks}``."""
    indices: dict[str, list[BlockExtraction]] = {}
    for doc_name in _DOC_TO_RUBRIC:
        # _tabled and lobbyview don't follow the projection-doc parsing model.
        if doc_name.startswith("_tabled/") or doc_name == "lobbyview_schema_coverage.md":
            continue
        path = _PROJECTIONS_DIR / doc_name
        indices[doc_name] = parse_projection_doc(path)
    return indices


def _resolve_block_for_row(
    v2_row_id: str, doc_blocks: list[BlockExtraction]
) -> BlockExtraction | None:
    """Find the block in a doc whose ``**Compendium rows:**`` contains a
    candidate spelling of the v2 row_id.

    Tries v2 row_id first, then renamed candidates from D1-D8.
    """
    candidates = _candidate_v1_ids(v2_row_id)
    for candidate in candidates:
        for block in doc_blocks:
            if candidate in block.row_ids and block.source_quote:
                return block
    return None


def _load_existing_yaml() -> dict[str, dict]:
    """Load existing YAML payload (preserving 17 narrow-pass rows verbatim)."""
    if not _YAML_PATH.exists():
        return {}
    with _YAML_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _str_representer(dumper: yaml.SafeDumper, data: str):
    """Multi-line strings as literal block scalar (``|``); single-line as
    double-quoted. Same convention as the narrow-pass migration script."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.SafeDumper.add_representer(str, _str_representer)


_YAML_HEADER = (
    "# compendium/source_quotes.yaml\n"
    "#\n"
    "# Source-quotes sidecar — prompt SSOT for the tier-1 dispatch.\n"
    "#\n"
    "# Per-row schema:\n"
    "#   <compendium_row_id>:\n"
    "#     source_quotes:                            # non-empty dict\n"
    "#       <rubric>_<vintage>_<section_ref>: \"<verbatim quote>\"\n"
    "#     prompt: \"<what the model sees>\"        # non-empty string\n"
    "#\n"
    "# `source_quotes` is immutable reference material; provenance lives\n"
    "# in the keys. `prompt` is mutable — the Ralph loop edits it.\n"
    "# Citations DO NOT appear inside the `prompt` value; they live in\n"
    "# the `source_quotes` keys only. See\n"
    "# `convos/20260604_wide_pass_yaml_sidecar_design.md` for the design.\n"
    "#\n"
    "# Commit 1 (wide-pass plan): 17 narrow-pass rows migrated from the\n"
    "# now-dropped `prompt_text` TSV column.\n"
    "# Commit 2 (this file): 164 remaining rows populated via the projection-\n"
    "# doc walk by `scripts/_completed/populate_source_quotes_wide_pass.py`.\n"
    "\n"
)


def main(verbose: bool = True, write: bool = True) -> int:
    """Walk unpopulated rows; merge into YAML; surface unknowns.

    Args:
        verbose: print progress + unresolved row report.
        write: if False, do not write YAML — just print what would happen
            (useful for surfacing unresolved rows before committing).

    Returns 0 on success, 1 if any rows could not be resolved.
    """
    existing = _load_existing_yaml()
    rows = _read_tsv()
    doc_indices = _build_doc_indices()

    new_entries: dict[str, dict] = {}
    failed: list[tuple[str, str, str, list[str]]] = (
        []
    )  # (row_id, doc, reason, candidate_v1_ids)

    for row in rows:
        row_id = row["compendium_row_id"]
        if row_id in existing:
            continue  # narrow-pass row already in YAML

        doc_name = row["first_introduced_by"]
        rubric_prefix = _DOC_TO_RUBRIC.get(doc_name)
        if rubric_prefix is None:
            failed.append((row_id, doc_name, "unknown doc filename", []))
            continue

        # Outlier rows — hand-encoded
        if row_id in _OUTLIER_ENTRIES:
            new_entries[row_id] = _OUTLIER_ENTRIES[row_id]
            continue

        if doc_name not in doc_indices:
            failed.append((row_id, doc_name, "doc not in index (outlier path)", []))
            continue

        block = _resolve_block_for_row(row_id, doc_indices[doc_name])
        if block is None:
            failed.append(
                (
                    row_id,
                    doc_name,
                    "no block found / no clean Source quote",
                    _candidate_v1_ids(row_id),
                )
            )
            continue

        key = _build_yaml_key(rubric_prefix, block.heading)
        new_entries[row_id] = {
            "source_quotes": {key: block.source_quote},
            "prompt": block.source_quote,
        }

    if verbose:
        print(f"Loaded {len(existing)} existing YAML rows.")
        print(f"Walked {len(rows)} TSV rows.")
        print(f"Resolved {len(new_entries)} new entries.")
        print(f"Unresolved: {len(failed)}")
        if failed:
            print("\nUnresolved rows (surface to Dan):")
            for row_id, doc, reason, cands in failed:
                print(f"  {row_id}")
                print(f"    doc: {doc}")
                print(f"    reason: {reason}")
                if cands:
                    print(f"    tried v1 ids: {cands}")

    if not write:
        if verbose:
            print("\n[dry-run] Not writing YAML.")
        return 0 if not failed else 1

    # Merge: existing rows preserved as-is; new entries appended.
    merged = dict(existing)
    merged.update(new_entries)
    # Sort by row_id for stable diff.
    sorted_merged = {k: merged[k] for k in sorted(merged)}

    rendered = yaml.safe_dump(
        sorted_merged,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,
        sort_keys=False,
    )
    _YAML_PATH.write_text(_YAML_HEADER + rendered, encoding="utf-8")
    if verbose:
        print(f"\nWrote {_YAML_PATH}")
        print(f"  total rows: {len(sorted_merged)}")

    return 0 if not failed else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry-run" in args
    sys.exit(main(verbose=True, write=not dry))

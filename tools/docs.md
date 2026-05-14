# Noridoc: tools

Path: @/tools

### Overview
This folder contains research-line utility scripts for assembling, normalizing, clustering, and freezing cross-rubric compendium source material. The scripts are executable companions to the compendium-source-extracts research artifacts rather than importable library modules.

### How it fits into the larger codebase

The tools read intermediate results from the compendium research line and write derived TSV, CSV, Markdown, and embedding artifacts used to reason about the compendium row set. They sit upstream of @/scripts/build_compendium.py: @/tools helps produce and audit candidate source material, while the build script turns finalized curation judgments into the committed @/compendium CSVs. Several tools consume paper-derived item tables and projection docs stored under @/docs, making the research provenance visible beside the generated outputs.

### Core Implementation

The scripts are file-oriented command-line programs. Table parsers such as @/tools/union_projection_rows.py extract rows from Markdown projection docs, normalization scripts such as @/tools/normalize_state_items.py and @/tools/freeze_canonicalize_rows.py canonicalize candidate rows, and embedding/consensus scripts such as @/tools/embed_cross_rubric.py, @/tools/assemble_comp_embed.py, and @/tools/consensus_grouping.py analyze cross-rubric similarity. The scripts use Pandas, NumPy, optional embedding providers, and explicit path constants rooted at the repository.

### Things to Know

These tools preserve research workflow state rather than providing a stable public API. Their path constants and output filenames encode the research-line artifacts they were written for, so they should be read together with the matching docs/results files when interpreting their behavior. Some scripts require optional local or API-backed embedding dependencies that are not part of the core package runtime.

Created and maintained by Nori.

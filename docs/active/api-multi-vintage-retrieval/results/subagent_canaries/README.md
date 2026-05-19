# Subagent canary bundles — reproducibility-ready

Created 2026-05-18 when the Anthropic workspace API cap blocked the direct-SDK orchestrator path. Each per-(state, vintage) subdirectory captures a full reproducibility bundle so that:

1. The work the LLM-as-subagent did (URL discovery) is preserved.
2. A future direct-API run (e.g., once the workspace cap clears on 2026-06-01) can replay the **same** prompt over the **same** TSV inputs without re-fetching Justia, enabling subagent-vs-direct-API agreement measurement.

## Bundle format

`<state>_<vintage>/` contains:

| File | Contents |
|---|---|
| `pass1_state_index.html` | Raw HTML of `https://law.justia.com/codes/<slug>/<vintage>/` |
| `pass1_state_index.tsv` | Cleaned link TSV (output of `_build_justia_link_tsv`) — the actual input to pass-1 LLM reasoning |
| `pass1_chosen.json` | Subagent's pass-1 output: which titles were picked |
| `pass2_<title-slug>.html` / `.tsv` | One pair per chosen title from pass-1 |
| `pass2_<title-slug>_chosen.json` | Subagent's pass-2 output for that title: which chapters were picked |
| `pass3_<chapter-slug>.html` / `.tsv` | One pair per chosen chapter from pass-2, when pass-3 fired |
| `pass3_<chapter-slug>_chosen.json` | Subagent's pass-3 output for that chapter: which sections were picked |
| `result.json` | Final aggregated output: proposed URLs, regime structure notes, tree depth, errors, prompt-file git rev |

## Provenance

Prompt files used by the subagent (version-controlled in the repo):
- `src/scoring/api_seed_discovery_pass1_prompt.md`
- `src/scoring/api_seed_discovery_pass2_prompt.md` (also reused as pass-3 template)

Each `result.json` records the `prompt_git_rev` at the time the subagent ran.

## Lossy bundles (no TSV/HTML capture)

These were dispatched before this capture format was added. URL outputs only:
- 2010: WY (pilot), MA, IL, PA, MI, GA, NC, VA, AZ
- 2015: WY, FL, NY

For these, re-running on direct API requires re-fetching Justia first.

# Noridoc: auditing-paper-summaries

Path: @/skills/auditing-paper-summaries

### Overview
This skill audits whether papers are represented consistently across source PDFs, extracted text, the paper index, and paper summaries. Its helper script checks the repository's research-paper bookkeeping rather than scoring or modeling lobbying data.

### How it fits into the larger codebase

The skill supports the literature side of the research workflow described in @/CLAUDE.md. @/skills/auditing-paper-summaries/audit_paper_summaries.py reads repo-level paper artifacts such as @/PAPER_SUMMARIES.md and files under @/papers to identify missing or inconsistent entries. It is complementary to the main code packages because the scoring and modeling work depends on stable prior-art provenance.

### Core Implementation

The helper parses summary entries, derives expected PDF and extracted-text paths, and reports whether each entry has matching local artifacts. It uses filesystem checks and markdown parsing conventions rather than package imports from @/src. Its output is meant for agent review and follow-up decisions in the skill workflow.

### Things to Know

The script is an audit aid, not an automatic fixer. It can flag structure or completeness gaps, but the surrounding skill decides how to handle discrepancies with the user. The paper filenames and markdown conventions are therefore part of the helper's operating assumptions.

Created and maintained by Nori.

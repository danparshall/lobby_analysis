# Noridoc: maintaining-decision-docs

Path: @/skills/maintaining-decision-docs

### Overview
This skill audits and maintains decision-document indexes and summaries under the repo's docs tree. Its helper script checks decision docs for coverage in index files, ADR-style structure, related links, and broken cross-references.

### How it fits into the larger codebase

The project keeps durable research and architecture context under @/docs, and decision docs need to remain discoverable as branches move from active to historical. @/skills/maintaining-decision-docs/audit_decision_docs.py supports that documentation layer without interacting with @/src/scoring or @/src/lobby_analysis. The skill is designed to run alongside Noridoc updates when code changes also affect decision documentation.

### Core Implementation

The helper locates a docs directory, lists markdown decision documents, parses index and summary entries, checks basic ADR compliance, extracts related links, and reports links that do not resolve to known docs. It returns structured audit information through terminal output for the agent to interpret. The script uses conservative filesystem and regex parsing because it is checking documentation shape, not rendering markdown.

### Things to Know

The audit reports gaps and inconsistencies but does not decide the documentation policy by itself. It assumes the repo has conventional docs index and summary files when those checks are relevant. Broken-link and ADR-shape findings should be reviewed in context because research docs can be provisional.

Created and maintained by Nori.
